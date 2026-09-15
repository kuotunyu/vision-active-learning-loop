"""Disk verification of the v0.3 diversity runs (2026-09-11).

Same checks as the v0.2.1 script for the rule-B experiments
`lite-czech-ep18-div-s<seed>-*` (steps 200/252/504/1008, epochs 40/18/18/18,
nine warnings, MATH SDPA, model_sha256, checkpoint digests, manifest digest,
ledger shape) plus: the embeddings file hash matches both its receipt and the
experiment receipt; the coreset ledger is reproduced exactly by re-running
greedy k-center from the stored embeddings; the hybrid ledger is reproduced
from the stored shortlists; the random ledger equals the v0.2.1 frozen order.

Run from the repo root with the project venv:

    .venv\\Scripts\\python.exe docs\\status\\2026-09-11-v0.3-disk-verification.py [--seeds 17,29,43]

Writes `2026-09-11-v0.3-disk-verification.json` next to this file and exits
non-zero if any check fails. Reads the private evidence root only.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from vision_active_learning_loop.lite.diversity import (  # noqa: E402
    HYBRID_FACTOR,
    hybrid_candidates,
    k_center_select,
    load_embeddings,
)
from vision_active_learning_loop.lite.loop import shared_start_items  # noqa: E402

if not os.environ.get("VAL_EVIDENCE_ROOT"):
    sys.exit("set VAL_EVIDENCE_ROOT to the private evidence root; see scripts/local-paths.example.ps1")
EVIDENCE = Path(os.environ["VAL_EVIDENCE_ROOT"]) / "lite"
DATA = EVIDENCE / "data" / "czech"
V02_LITE_MODEL_SHA256 = "bb736d5335079f9234a73724092b86433614fdbe7281e6b718161641e589a809"
MANIFEST_SHA256 = "3d961040969e9008b1c534740f5c1c5b4f019c6394db7170acd99cddd8f9388d"
RULE_B_STEPS = {0.02: 200, 0.05: 252, 0.10: 504, 0.20: 1008}
RULE_B_EPOCHS = {0.02: 40, 0.05: 18, 0.10: 18, 0.20: 18}
ARMS = ("random", "coreset", "hybrid")
LEDGER_SHAPE = {0.05: 67, 0.1: 113, 0.2: 225}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_fit(fit_dir: Path, normative: dict, *, seed: int, steps: int, tag: str, failures: list[str]) -> str:
    env = normative.get("environment", {})
    digest = sha256(fit_dir / "checkpoint.pt")
    checks = {
        "steps": normative.get("steps") == steps,
        "warnings": env.get("allowlisted_backward_warnings") == 9,
        "sdpa": env.get("sdpa_backend") == "MATH",
        "model_sha256": normative.get("model_sha256") == V02_LITE_MODEL_SHA256,
        "checkpoint_sha256": digest == normative.get("checkpoint_sha256"),
        "manifest_sha256": normative.get("manifest_sha256") == MANIFEST_SHA256,
        "seed": normative.get("seed") == seed,
        "rule": (normative.get("training_rule") or {}).get("name") == "fixed-epochs",
    }
    for name, ok in checks.items():
        if not ok:
            failures.append(f"{tag}: {name}")
    return digest


def replay_selection(experiment: Path, embeddings, view_ids: tuple[str, ...], seed: int, failures: list[str]) -> dict:
    """Re-run coreset and hybrid selection from the stored embeddings and shortlists."""
    start = list(shared_start_items(view_ids, seed=seed))
    result = {}
    for arm in ("coreset", "hybrid"):
        entries = load(experiment / f"ledger-{arm}.json")["entries"]
        shortlists = load(experiment / "hybrid-shortlists.json")["rounds"] if arm == "hybrid" else None
        acquired = list(start)
        replayed = 0
        arm_failures: list[str] = []
        for round_index in (1, 2, 3):
            recorded = [e for e in entries if e["round_index"] == round_index]
            count = len(recorded)
            taken = set(acquired)
            unacquired = tuple(item for item in view_ids if item not in taken)
            if arm == "coreset":
                candidates: tuple[str, ...] = unacquired
            else:
                stored = shortlists[round_index - 1]["candidates"]
                scores = {c["item_id"]: c["score"] for c in stored}
                if len(stored) != min(HYBRID_FACTOR * count, len(unacquired)):
                    arm_failures.append(f"hybrid round {round_index}: shortlist size {len(stored)}")
                candidates = hybrid_candidates(scores, count)
                if tuple(c["item_id"] for c in stored) != candidates:
                    arm_failures.append(f"hybrid round {round_index}: shortlist order is not score-then-id")
            picked = k_center_select(candidates, embeddings.rows(candidates), embeddings.rows(sorted(acquired)), count)
            chosen = [item for item, _ in picked]
            if chosen != [e["item_id"] for e in recorded]:
                arm_failures.append(f"{arm} round {round_index}: replayed selection differs from the ledger")
            for (item, distance), entry in zip(picked, recorded):
                if abs(distance - float(entry["score"])) > 1e-5:
                    arm_failures.append(f"{arm} round {round_index}: distance for {item[:8]} differs")
            replayed += len(chosen)
            acquired.extend(chosen)
        failures.extend(arm_failures)
        result[arm] = {"replayed": replayed, "matches_ledger": not arm_failures}
    return result


def verify(seed: int) -> dict:
    failures: list[str] = []
    matches = sorted(glob.glob(str(EVIDENCE / f"lite-czech-ep18-div-s{seed}-*")))
    if len(matches) != 1:
        return {"seed": seed, "failures": [f"expected one experiment dir, found {len(matches)}"]}
    experiment = Path(matches[0])
    receipt = load(experiment / "experiment-receipt.json")["normative"]
    if receipt["arms"] != list(ARMS):
        failures.append(f"arms {receipt['arms']}")
    embeddings = load_embeddings(DATA / "embeddings-dinov2-small.npz")
    emb_receipt = load(DATA / "embeddings-receipt.json")["normative"]
    if not (embeddings.sha256 == emb_receipt["embeddings_sha256"] == receipt.get("embeddings_sha256")):
        failures.append("embeddings hash differs between file, its receipt and the experiment receipt")
    if emb_receipt["manifest_sha256"] != MANIFEST_SHA256 or emb_receipt["image_count"] != receipt["pool_size"]:
        failures.append("embeddings receipt is not bound to this manifest/pool")
    fits = []
    for entry in receipt["fits"]:
        path = experiment / entry["receipt_path"]
        fit = load(path)["normative"]
        fraction = round(float(fit["budget_fraction"]), 2)
        tag = f"{fit['arm']}-{fraction:.2f}"
        digest = check_fit(path.parent, fit, seed=seed, steps=RULE_B_STEPS[fraction], tag=tag, failures=failures)
        if digest != entry["checkpoint_sha256"]:
            failures.append(f"{tag}: experiment receipt checkpoint digest")
        if fit.get("epochs_started") != RULE_B_EPOCHS[fraction]:
            failures.append(f"{tag}: epochs_started {fit.get('epochs_started')}")
        fits.append({"fit": tag, "steps": fit["steps"], "images": fit["acquired_image_count"], "elapsed_seconds": fit.get("elapsed_seconds")})
    if len(receipt["fits"]) != 10:
        failures.append(f"experiment lists {len(receipt['fits'])} fits")
    for arm in ARMS:
        entries = load(experiment / f"ledger-{arm}.json")["entries"]
        per: dict[float, int] = {}
        for e in entries:
            per[e["budget_fraction"]] = per.get(e["budget_fraction"], 0) + 1
        ids = [e["item_id"] for e in entries]
        if not (len(entries) == 405 and len(set(ids)) == 405 and per == LEDGER_SHAPE):
            failures.append(f"ledger {arm}: shape {len(entries)} {per}")
    view_ids = tuple(str(row["item_id"]) for row in load(DATA / "public-pool.json")["images"])
    previous = sorted(glob.glob(str(EVIDENCE / f"lite-czech-ep18-s{seed}-2*")))
    if previous:
        old_random = [e["item_id"] for e in load(Path(previous[-1]) / "ledger-random.json")["entries"]]
        new_random = [e["item_id"] for e in load(experiment / "ledger-random.json")["entries"]]
        if old_random != new_random:
            failures.append("random ledger differs from the v0.2.1 frozen order")
    replay = replay_selection(experiment, embeddings, view_ids, seed, failures)
    for log_path in sorted(glob.glob(str(EVIDENCE / f"run-lite-ep18-div-seed{seed}-*.log"))):
        if "Traceback" in Path(log_path).read_text(encoding="utf-8", errors="replace"):
            failures.append(f"Traceback in {Path(log_path).name}")
    if (experiment / "failure.json").exists():
        failures.append("failure.json present")
    return {
        "seed": seed,
        "experiment_id": experiment.name,
        "embeddings_sha256": embeddings.sha256,
        "timing": receipt.get("timing"),
        "naubc": receipt["naubc"],
        "naubc_delta_vs_random": receipt["naubc_delta_vs_random"],
        "fits": fits,
        "selection_replay": replay,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="17,29,43")
    arguments = parser.parse_args()
    seeds = [int(s) for s in arguments.seeds.split(",") if s]
    results = {"evidence_root": "<evidence-root>/lite", "running_lock_present": (EVIDENCE / "RUNNING.lock").exists(), "runs": []}
    total = 0
    for seed in seeds:
        report = verify(seed)
        results["runs"].append(report)
        total += len(report["failures"])
        print(f"seed {seed}: {'PASS' if not report['failures'] else 'FAIL ' + '; '.join(report['failures'])}")
    results["total_failures"] = total
    out = Path(__file__).with_suffix(".json")
    out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.name}; total failures {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
