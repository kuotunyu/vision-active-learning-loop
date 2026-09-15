"""Read-only sanity audit of the v0.2-lite data and evidence (2026-09-10).

Recomputes, on CPU and from disk, the facts the next round rests on:
split assignment from item ids, annotation conversion against the raw VOC
XML, the shared model initialisation across every fit, the fixed-step
recipe every receipt claims, ledger nesting, and the acquisition scores.
Nothing is written except the JSON report next to this script.

Run from the worktree:

    .venv\\Scripts\\python.exe docs\\verification\\2026-09-10-lite-sanity-audit.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from vision_active_learning_loop.lite.manifest import (  # noqa: E402
    assign_split,
    manifest_sha256,
    parse_voc_annotation,
)
from vision_active_learning_loop.lite.rounds import budget_count  # noqa: E402

if not os.environ.get("VAL_EVIDENCE_ROOT"):
    sys.exit("set VAL_EVIDENCE_ROOT to the private evidence root; see scripts/local-paths.example.ps1")
ARTIFACTS = Path(os.environ["VAL_EVIDENCE_ROOT"]) / "lite"
if not os.environ.get("VAL_DATA_ROOT"):
    sys.exit("set VAL_DATA_ROOT to the RDD2022 data root; see scripts/local-paths.example.ps1")
DATA = Path(os.environ["VAL_DATA_ROOT"]) / "rdd2022" / "czech"
EXPERIMENTS = (
    "lite-czech-s17-20260909T1002Z",
    "lite-czech-s29-20260909T1145Z",
    "lite-czech-s43-20260909T1640Z",
    "lite-czech-s43-20260909T1755Z",
)
SAMPLE_XML = 200


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_manifest() -> dict:
    manifest = _load(ARTIFACTS / "data" / "czech" / "manifest.json")
    rows = manifest["images"]
    split_mismatch = sum(1 for row in rows if assign_split(row["item_id"]) != row["split"])
    splits = Counter(row["split"] for row in rows)
    class_counts = Counter(box[0] for row in rows for box in row["boxes"])
    test_class_counts = Counter(
        box[0] for row in rows if row["split"] == "test" for box in row["boxes"]
    )
    pool = splits["pool"]
    return {
        "manifest_sha256": manifest_sha256(manifest),
        "image_count": len(rows),
        "split_recomputed_mismatches": split_mismatch,
        "splits": dict(splits),
        "class_box_counts": {str(k): v for k, v in sorted(class_counts.items())},
        "test_class_box_counts": {str(k): v for k, v in sorted(test_class_counts.items())},
        "negative_images": sum(1 for row in rows if not row["boxes"]),
        "budgets": {f"{p:.2f}": budget_count(p, pool) for p in (0.02, 0.05, 0.10, 0.20)},
        "reference_pool_size": pool,
    }, manifest


def audit_annotations(manifest: dict) -> dict:
    """Re-parse a fixed random sample of raw XML files and compare to the manifest."""
    by_id = {row["item_id"]: row for row in manifest["images"]}
    xml_dir = DATA / "annotations" / "xmls"
    image_dir = DATA / "images"
    names = sorted(path.stem for path in xml_dir.glob("*.xml"))
    chosen = random.Random(20260910).sample(names, SAMPLE_XML)
    mismatches = []
    size_mismatches = 0
    for stem in chosen:
        image_bytes = (image_dir / f"{stem}.jpg").read_bytes()
        item_id = hashlib.sha256(image_bytes).hexdigest()
        annotation = parse_voc_annotation((xml_dir / f"{stem}.xml").read_bytes())
        row = by_id.get(item_id)
        if row is None:
            mismatches.append({"file": stem, "reason": "item_id absent"})
            continue
        expected = sorted(
            [box.class_id, box.x_min, box.y_min, box.x_max, box.y_max]
            for box in annotation.boxes
        )
        if sorted(row["boxes"]) != expected:
            mismatches.append({"file": stem, "reason": "boxes differ"})
        if (row["width"], row["height"]) != (annotation.width, annotation.height):
            size_mismatches += 1
    return {
        "xml_files": len(names),
        "sampled": SAMPLE_XML,
        "box_mismatches": mismatches,
        "size_mismatches": size_mismatches,
    }


def audit_experiment(experiment_id: str) -> dict:
    root = ARTIFACTS / experiment_id
    receipt = _load(root / "experiment-receipt.json")["normative"]
    pool = receipt["pool_size"]
    fits = []
    for entry in receipt["fits"]:
        fit = _load(root / entry["receipt_path"])["normative"]
        checkpoint = root / Path(entry["receipt_path"]).parent / "checkpoint.pt"
        digest = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        fits.append(
            {
                "arm": fit["arm"],
                "fraction": fit["budget_fraction"],
                "images": fit["acquired_image_count"],
                "steps": fit["steps"],
                "epochs_approx": round(fit["steps"] * fit["recipe"]["batch_size"] / fit["acquired_image_count"], 1),
                "warnings": fit["environment"].get("allowlisted_backward_warnings"),
                "sdpa": fit["environment"].get("sdpa_backend"),
                "model_sha256": fit["model_sha256"],
                "checkpoint_matches": digest == fit["checkpoint_sha256"] == entry["checkpoint_sha256"],
                "loss_decreased": fit["loss"]["decreased"],
                "last_window_median": round(fit["loss"]["last_window_median"], 3),
                "mAP50_95": entry["metrics"]["mAP50_95"],
            }
        )
    ledgers = {}
    for arm in ("random", "entropy", "margin"):
        entries = _load(root / f"ledger-{arm}.json")["entries"]
        per_round = Counter(entry["round_index"] for entry in entries)
        ids = [entry["item_id"] for entry in entries]
        scores = [entry["score"] for entry in entries]
        ledgers[arm] = {
            "per_round": dict(sorted(per_round.items())),
            "unique_ids": len(set(ids)) == len(ids),
            "expected_per_round": [
                budget_count(p, pool) - budget_count(q, pool)
                for q, p in ((0.02, 0.05), (0.05, 0.10), (0.10, 0.20))
            ],
            "scored": all(s is not None for s in scores) if arm != "random" else all(s is None for s in scores),
        }
    with (root / "metrics.csv").open(encoding="utf-8", newline="") as handle:
        csv_rows = list(csv.DictReader(handle))
    return {
        "seed": receipt["seed"],
        "manifest_sha256": receipt["manifest_sha256"],
        "fit_count": len(fits),
        "distinct_model_sha256": len({fit["model_sha256"] for fit in fits}),
        "all_checkpoints_match": all(fit["checkpoint_matches"] for fit in fits),
        "all_steps": sorted({fit["steps"] for fit in fits}),
        "all_warnings": sorted({fit["warnings"] for fit in fits}),
        "all_sdpa": sorted({fit["sdpa"] for fit in fits}),
        "all_loss_decreased": all(fit["loss_decreased"] for fit in fits),
        "metrics_csv_rows": len(csv_rows),
        "naubc": receipt["naubc"],
        "naubc_delta_vs_random": receipt["naubc_delta_vs_random"],
        "fits": fits,
        "ledgers": ledgers,
    }


def main() -> int:
    manifest_report, manifest = audit_manifest()
    report = {
        "generated": "2026-09-10",
        "manifest": manifest_report,
        "annotations": audit_annotations(manifest),
        "experiments": {name: audit_experiment(name) for name in EXPERIMENTS},
    }
    models = {
        fit["model_sha256"]
        for experiment in report["experiments"].values()
        for fit in experiment["fits"]
    }
    report["shared_initialisation_across_all_fits"] = len(models) == 1
    output = Path(__file__).with_suffix(".json")
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "experiments"}, indent=2))
    for name, experiment in report["experiments"].items():
        print(name, json.dumps({k: v for k, v in experiment.items() if k not in ("fits", "ledgers")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
