"""Cross-seed summary of v0.2-lite experiments.

Implements the reporting rule of the approved design (Section 10.3): nAUBC per
seed and arm, paired arm-minus-random deltas per seed, their mean and median,
and all-seed sign consistency. v0.2.1 adds the training rule the receipts ran
under, the actual steps and seconds per setting, and the optional full-label
reference fits the 20% points are compared against. Every input is a published
receipt; nothing is recomputed from checkpoints. Three seeds give a range, not
a confidence interval, and the summary never calls it one.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ..artifacts.no_clobber import NoClobberError
from ..cli_manifest import command
from ..models.rtdetr_contract import RDD_LABELS
from .experiment import write_budget_curve
from .manifest import write_json_no_clobber
from .train import (
    FIXED_STEPS_RULE,
    REFERENCE_ROLE,
    REGISTERED_ARMS,
    REGISTERED_BUDGET_FRACTIONS,
    SHARED_START_ROLE,
)

RECEIPT_TYPE = "lite-experiment"
FINAL_FRACTION = REGISTERED_BUDGET_FRACTIONS[-1]


class SummaryError(ValueError):
    """Raised when the receipts cannot be summarized together."""


def _rule_name(normative: Mapping[str, Any]) -> str:
    """Name the rule a receipt ran under; receipts older than v0.2.1 are fixed-step."""
    runtime = normative.get("runtime", {})
    rule = runtime.get("training_rule") if isinstance(runtime, Mapping) else None
    if isinstance(rule, Mapping) and rule.get("name"):
        return str(rule["name"])
    return FIXED_STEPS_RULE.name


def _mean_or_none(values: Sequence[float | None]) -> float | None:
    present = [float(value) for value in values if value is not None]
    return float(statistics.mean(present)) if present else None


def _normative(receipt: Mapping[str, Any]) -> Mapping[str, Any]:
    if receipt.get("receipt_type") != RECEIPT_TYPE:
        raise SummaryError("every input must be a lite-experiment receipt")
    normative = receipt.get("normative")
    if not isinstance(normative, Mapping):
        raise SummaryError("receipt normative payload is missing")
    return normative


def _min_class_recall(metrics: Mapping[str, Any]) -> float:
    try:
        return min(float(metrics[f"recall_{label}"]) for label in RDD_LABELS)
    except (KeyError, TypeError, ValueError) as error:
        raise SummaryError(f"per-class recall is missing: {error}") from error


def _reference_rows(
    references: Sequence[Mapping[str, Any]], *, manifest: str, rule: str
) -> dict[int, dict[str, Any]]:
    """Index reference metrics documents by seed, checking they belong here."""
    rows: dict[int, dict[str, Any]] = {}
    for document in references:
        if document.get("arm") != REFERENCE_ROLE:
            raise SummaryError("every reference document must be a reference fit")
        if document.get("manifest_sha256") != manifest:
            raise SummaryError("reference fit does not bind the summarized manifest")
        name = document.get("training_rule", {}).get("name")
        if name != rule:
            raise SummaryError(f"reference fit ran under {name!r}, experiments under {rule!r}")
        seed = document.get("seed")
        if seed in rows:
            raise SummaryError(f"reference seed {seed} appears more than once")
        metrics = document["metrics"]
        rows[seed] = {
            "experiment_id": document.get("experiment_id"),
            "mAP50_95": float(metrics["mAP50_95"]),
            "min_class_recall": _min_class_recall(metrics),
            "images": int(document["budget"]),
            "steps": document.get("steps"),
            "elapsed_seconds": document.get("elapsed_seconds"),
        }
    return rows


def summarize_experiments(
    receipts: Sequence[Mapping[str, Any]],
    references: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Aggregate one or more single-seed experiment receipts."""
    if not receipts:
        raise SummaryError("at least one experiment receipt is required")
    per_seed: list[dict[str, Any]] = []
    manifests: set[str] = set()
    rules: set[str] = set()
    seen_seeds: set[int] = set()
    curves: dict[str, dict[str, list[float]]] = {}
    compute: dict[str, dict[str, dict[str, list[Any]]]] = {}
    final_map: dict[int, dict[str, float]] = {}

    for receipt in receipts:
        normative = _normative(receipt)
        seed = normative.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise SummaryError("receipt seed must be an integer")
        if seed in seen_seeds:
            raise SummaryError(f"seed {seed} appears more than once")
        seen_seeds.add(seed)
        manifests.add(str(normative.get("manifest_sha256")))
        rules.add(_rule_name(normative))
        naubc = normative.get("naubc")
        if not isinstance(naubc, Mapping) or "random" not in naubc:
            raise SummaryError("receipt naubc must include the random arm")
        arms = [arm for arm in REGISTERED_ARMS if arm in naubc]
        deltas = {arm: float(naubc[arm]) - float(naubc["random"]) for arm in arms}
        min_recall: dict[str, float] = {}
        final_map[seed] = {}
        for fit in normative.get("fits", ()):
            arm = fit["arm"]
            fraction = f"{float(fit['budget_fraction']):.2f}"
            value = float(fit["metrics"]["mAP50_95"])
            curves.setdefault(arm, {}).setdefault(fraction, []).append(value)
            cell = compute.setdefault(arm, {}).setdefault(
                fraction, {"images": [], "steps": [], "elapsed_seconds": []}
            )
            cell["images"].append(int(fit["budget"]))
            cell["steps"].append(fit.get("steps"))
            cell["elapsed_seconds"].append(fit.get("elapsed_seconds"))
            if float(fit["budget_fraction"]) == FINAL_FRACTION:
                min_recall[arm] = _min_class_recall(fit["metrics"])
                final_map[seed][arm] = value
        timing = normative.get("timing")
        per_seed.append(
            {
                "seed": seed,
                "experiment_id": normative.get("experiment_id"),
                "naubc": {arm: float(naubc[arm]) for arm in ["random", *arms]},
                "delta_vs_random": deltas,
                f"min_class_recall_at_{FINAL_FRACTION:.2f}": min_recall,
                "timing_seconds": dict(timing) if isinstance(timing, Mapping) else None,
            }
        )
    if len(manifests) != 1:
        raise SummaryError("every receipt must bind the same manifest")
    if len(rules) != 1:
        raise SummaryError("every receipt must run under the same training rule")
    rule = next(iter(rules))
    manifest = next(iter(manifests))

    reference = _reference_rows(references, manifest=manifest, rule=rule)
    for row in per_seed:
        ref = reference.get(row["seed"])
        row["reference_mAP50_95"] = ref["mAP50_95"] if ref else None
        row[f"fraction_of_reference_at_{FINAL_FRACTION:.2f}"] = (
            {
                arm: value / ref["mAP50_95"]
                for arm, value in final_map[row["seed"]].items()
            }
            if ref and ref["mAP50_95"] > 0.0
            else None
        )

    per_seed.sort(key=lambda row: row["seed"])
    arms_present = [
        arm for arm in REGISTERED_ARMS if arm != "random"
        if all(arm in row["delta_vs_random"] for row in per_seed)
    ]
    delta_summary: dict[str, Any] = {}
    for arm in arms_present:
        values = [row["delta_vs_random"][arm] for row in per_seed]
        delta_summary[arm] = {
            "values": values,
            "mean": float(statistics.mean(values)),
            "median": float(statistics.median(values)),
            "sign_consistent": all(value > 0 for value in values)
            or all(value < 0 for value in values),
            "positive_seeds": sum(1 for value in values if value > 0),
        }
    mean_curve = {
        arm: {
            fraction: float(statistics.mean(values))
            for fraction, values in sorted(fractions.items())
        }
        for arm, fractions in curves.items()
    }
    range_curve = {
        arm: {
            fraction: [float(min(values)), float(max(values))]
            for fraction, values in sorted(fractions.items())
        }
        for arm, fractions in curves.items()
    }
    compute_summary = {
        arm: {
            fraction: {
                "images": int(cell["images"][0]),
                "mean_steps": _mean_or_none(cell["steps"]),
                "mean_elapsed_seconds": _mean_or_none(cell["elapsed_seconds"]),
            }
            for fraction, cell in sorted(fractions.items())
        }
        for arm, fractions in compute.items()
    }
    return {
        "receipt_type": "lite-summary",
        "schema_version": 2,
        "manifest_sha256": manifest,
        "training_rule": rule,
        "seeds": [row["seed"] for row in per_seed],
        "arms": ["random", *arms_present],
        "per_seed": per_seed,
        "delta_vs_random": delta_summary,
        "mean_map50_95": mean_curve,
        "range_map50_95": range_curve,
        "compute": compute_summary,
        "reference": {
            "per_seed": {str(seed): row for seed, row in sorted(reference.items())},
            "mean_map50_95": _mean_or_none([row["mAP50_95"] for row in reference.values()]),
        },
        "claim_rule": (
            "an arm may be called consistently above random only when every "
            "seed's paired nAUBC delta is positive; single-seed deltas sit within "
            "the same-host replay spread; range_map50_95 is the min/max over "
            "seeds, not a confidence interval"
        ),
    }


def _csv_rows(summary: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for row in summary["per_seed"]:
        record: dict[str, Any] = {
            "seed": row["seed"],
            "experiment_id": row["experiment_id"],
        }
        for arm, value in row["naubc"].items():
            record[f"naubc_{arm}"] = value
        for arm, value in row["delta_vs_random"].items():
            record[f"delta_{arm}"] = value
        for arm, value in row[f"min_class_recall_at_{FINAL_FRACTION:.2f}"].items():
            record[f"min_recall_{arm}"] = value
        record["reference_map"] = row["reference_mAP50_95"]
        for arm, value in (row[f"fraction_of_reference_at_{FINAL_FRACTION:.2f}"] or {}).items():
            record[f"ratio_{arm}"] = value
        rows.append(record)
    return rows


def _read_json(path: Path) -> Mapping[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise SummaryError(f"{path} is unavailable: {error}") from error


@command("lite summarize")
def summary_main(argv: Sequence[str] | None = None) -> int:
    """Summarize several single-seed experiments into summary.json and summary.csv."""
    parser = argparse.ArgumentParser(prog="val lite summarize")
    parser.add_argument("--experiment", action="append", required=True)
    parser.add_argument(
        "--reference",
        action="append",
        default=[],
        help="metrics-reference-1.00.json of a full-label fit for one seed",
    )
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(list(argv) if argv is not None else None)

    try:
        receipts = [
            _read_json(Path(root) / "experiment-receipt.json")
            for root in arguments.experiment
        ]
        references = [_read_json(Path(path)) for path in arguments.reference]
        summary = summarize_experiments(receipts, references)
        output = Path(arguments.output)
        output.mkdir(parents=True, exist_ok=True)
        json_path = output / "summary.json"
        csv_path = output / "summary.csv"
        curve_path = output / "mean-curve.svg"
        if json_path.exists() or csv_path.exists() or curve_path.exists():
            raise SummaryError(f"summary already exists in {output}")
        write_json_no_clobber(json_path, summary)
        write_budget_curve(
            output / "mean-curve.svg",
            {
                arm: [
                    (float(fraction), value)
                    for fraction, value in sorted(points.items())
                ]
                for arm, points in summary["mean_map50_95"].items()
                if arm != SHARED_START_ROLE
            },
        )
        rows = _csv_rows(summary)
        columns = sorted(
            {key for row in rows for key in row}, key=lambda k: (k != "seed", k)
        )
        with csv_path.open("x", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)
    except (SummaryError, NoClobberError, OSError) as error:
        print(f"lite summarize error: {error}", file=sys.stderr)
        return 3
    print(
        json.dumps(
            {
                "seeds": summary["seeds"],
                "training_rule": summary["training_rule"],
                "reference_mean_map50_95": summary["reference"]["mean_map50_95"],
                "delta_vs_random": {
                    arm: {
                        "mean": stats["mean"],
                        "sign_consistent": stats["sign_consistent"],
                    }
                    for arm, stats in summary["delta_vs_random"].items()
                },
            },
            sort_keys=True,
        )
    )
    return 0


__all__ = [
    "SHARED_START_ROLE",
    "SummaryError",
    "summarize_experiments",
    "summary_main",
]
