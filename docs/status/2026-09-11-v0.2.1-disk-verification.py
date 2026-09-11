"""Disk verification of the v0.2.1 GPU runs (2026-09-11).

Checks every rule-B experiment (three seeds, 10 fits each, plus the shared 2%
baseline run) and all six full-label reference fits against the pre-registered
protocol: steps per rule, epochs started, the nine allowlisted backward
warnings, Math-only SDPA, loss decrease, `model_sha256` equal to the v0.2-lite
receipts, checkpoint bytes matching every receipt that names them, manifest
digest, ledger shape and nesting, the frozen random order, and the absence of
tracebacks, lock files and `failure.json`.

Run from the worktree root with the project venv:

    .venv\\Scripts\\python.exe docs\\status\\2026-09-11-v0.2.1-disk-verification.py

Writes `2026-09-11-v0.2.1-disk-verification.json` next to this file and exits
non-zero if any check fails. Reads the private evidence root only; writes
nothing there.
"""

from __future__ import annotations

import csv
import glob
import hashlib
import json
import os
import sys
from pathlib import Path

EVIDENCE = Path(r"<evidence-root>/lite")
V02_LITE_MODEL_SHA256 = "bb736d5335079f9234a73724092b86433614fdbe7281e6b718161641e589a809"
MANIFEST_SHA256 = "3d961040969e9008b1c534740f5c1c5b4f019c6394db7170acd99cddd8f9388d"
RULE_B_STEPS = {0.02: 200, 0.05: 252, 0.10: 504, 0.20: 1008}
RULE_B_EPOCHS = {0.02: 40, 0.05: 18, 0.10: 18, 0.20: 18}
REFERENCE_STEPS = {"fixed-epochs": 5058, "fixed-steps": 1000}
SEEDS = (17, 29, 43)
LEDGER_SHAPE = {0.05: 67, 0.1: 113, 0.2: 225}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def only_dir(pattern: str, failures: list[str]) -> Path | None:
    matches = sorted(glob.glob(str(EVIDENCE / pattern)))
    if len(matches) != 1:
        failures.append(f"expected exactly one directory for {pattern}, found {len(matches)}")
        return None
    return Path(matches[0])


def check_fit(fit_dir: Path, normative: dict, *, seed: int, rule: str, steps: int, tag: str, failures: list[str]) -> str:
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
        "rule": (normative.get("training_rule") or {}).get("name") == rule,
    }
    for name, ok in checks.items():
        if not ok:
            failures.append(f"{tag}: {name}")
    return digest


def verify(seed: int, rule: str) -> dict:
    failures: list[str] = []
    report: dict = {"seed": seed, "rule": rule}
    if rule == "fixed-epochs":
        baseline = only_dir(f"lite-czech-ep18-s{seed}-baseline-*", failures)
        if baseline is not None:
            metrics = load(baseline / "metrics-shared-0.02.json")
            fit = load(baseline / "fits" / "shared-0.02" / "fit-receipt.json")["normative"]
            check_fit(baseline / "fits" / "shared-0.02", fit, seed=seed, rule=rule, steps=200, tag="baseline", failures=failures)
            if not metrics["loss"]["decreased"]:
                failures.append("baseline: loss not decreased")
            report["baseline"] = {
                "experiment_id": baseline.name,
                "steps": fit["steps"],
                "epochs_started": fit.get("epochs_started"),
                "elapsed_seconds": fit.get("elapsed_seconds"),
                "mAP50_95": metrics["metrics"]["mAP50_95"],
            }
    reference = only_dir(f"lite-czech-ref-{rule}-s{seed}-*", failures)
    if reference is not None:
        metrics = load(reference / "metrics-reference-1.00.json")
        fit = load(reference / "fits" / "reference-1.00" / "fit-receipt.json")["normative"]
        digest = check_fit(reference / "fits" / "reference-1.00", fit, seed=seed, rule=rule, steps=REFERENCE_STEPS[rule], tag="reference", failures=failures)
        if metrics.get("budget") != 2255 or fit.get("acquired_image_count") != 2255:
            failures.append("reference: budget is not the whole pool")
        if metrics.get("checkpoint_sha256") != digest:
            failures.append("reference: metrics checkpoint digest")
        if not metrics["loss"]["decreased"]:
            failures.append("reference: loss not decreased")
        report["reference"] = {
            "experiment_id": reference.name,
            "steps": fit["steps"],
            "epochs_started": fit.get("epochs_started"),
            "elapsed_seconds": fit.get("elapsed_seconds"),
            "mAP50_95": metrics["metrics"]["mAP50_95"],
            "min_class_recall": min(v for k, v in metrics["metrics"].items() if k.startswith("recall_")),
        }
    if rule == "fixed-epochs":
        experiment = only_dir(f"lite-czech-ep18-s{seed}-2*", failures)
        if experiment is not None:
            receipt = load(experiment / "experiment-receipt.json")["normative"]
            if not (receipt["seed"] == seed and receipt["pool_size"] == 2255 and receipt["test_image_count"] == 574 and receipt["manifest_sha256"] == MANIFEST_SHA256):
                failures.append("experiment receipt header")
            if len(receipt["fits"]) != 10:
                failures.append(f"experiment lists {len(receipt['fits'])} fits")
            fits = []
            for entry in receipt["fits"]:
                path = experiment / entry["receipt_path"]
                fit = load(path)["normative"]
                fraction = round(float(fit["budget_fraction"]), 2)
                tag = f"{fit['arm']}-{fraction:.2f}"
                digest = check_fit(path.parent, fit, seed=seed, rule=rule, steps=RULE_B_STEPS[fraction], tag=tag, failures=failures)
                if digest != entry["checkpoint_sha256"]:
                    failures.append(f"{tag}: experiment receipt checkpoint digest")
                if fit.get("epochs_started") != RULE_B_EPOCHS[fraction]:
                    failures.append(f"{tag}: epochs_started {fit.get('epochs_started')}")
                fits.append({"fit": tag, "steps": fit["steps"], "images": fit["acquired_image_count"], "epochs_started": fit.get("epochs_started"), "elapsed_seconds": fit.get("elapsed_seconds")})
            for arm in ("random", "entropy", "margin"):
                entries = load(experiment / f"ledger-{arm}.json")["entries"]
                ids = [e["item_id"] for e in entries]
                per_round: dict[float, int] = {}
                for e in entries:
                    per_round[e["budget_fraction"]] = per_round.get(e["budget_fraction"], 0) + 1
                if not (len(entries) == 405 and len(set(ids)) == 405 and per_round == LEDGER_SHAPE):
                    failures.append(f"ledger {arm}: shape {len(entries)} {per_round}")
            previous = sorted(glob.glob(str(EVIDENCE / f"lite-czech-s{seed}-2*")))
            if previous:
                old_random = [e["item_id"] for e in load(Path(previous[-1]) / "ledger-random.json")["entries"]]
                new_random = [e["item_id"] for e in load(experiment / "ledger-random.json")["entries"]]
                report["random_ledger_identical_to_v02_lite"] = old_random == new_random
                if old_random != new_random:
                    failures.append("random ledger differs from the v0.2-lite frozen order")
            rows = list(csv.DictReader((experiment / "metrics.csv").open(encoding="utf-8")))
            if len(rows) != 10:
                failures.append("metrics.csv rows")
            for name in ("curve.svg", "ledger-random.json", "ledger-entropy.json", "ledger-margin.json"):
                if not (experiment / name).exists():
                    failures.append(f"missing {name}")
            if (experiment / "failure.json").exists():
                failures.append("failure.json present")
            report["experiment"] = {
                "experiment_id": experiment.name,
                "timing": receipt.get("timing"),
                "naubc": receipt["naubc"],
                "naubc_delta_vs_random": receipt["naubc_delta_vs_random"],
                "fits": fits,
            }
    prefix = "run-lite-ep18-" if rule == "fixed-epochs" else "run-lite-"
    logs = sorted(glob.glob(str(EVIDENCE / f"{prefix}seed{seed}-20260911T*.log")))
    report["logs"] = [os.path.basename(p) for p in logs]
    for log in logs:
        if "Traceback" in Path(log).read_text(encoding="utf-8", errors="replace"):
            failures.append(f"Traceback in {os.path.basename(log)}")
    report["failures"] = failures
    return report


def main() -> int:
    results = {"evidence_root": str(EVIDENCE), "running_lock_present": (EVIDENCE / "RUNNING.lock").exists(), "runs": []}
    total = 0
    for rule in ("fixed-epochs", "fixed-steps"):
        for seed in SEEDS:
            report = verify(seed, rule)
            results["runs"].append(report)
            total += len(report["failures"])
            print(f"{rule} seed {seed}: {'PASS' if not report['failures'] else 'FAIL ' + '; '.join(report['failures'])}")
    if results["running_lock_present"]:
        total += 1
        print("RUNNING.lock is present")
    results["total_failures"] = total
    out = Path(__file__).with_suffix(".json")
    out.write_text(json.dumps(results, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {out.name}; total failures {total}")
    return 0 if total == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
