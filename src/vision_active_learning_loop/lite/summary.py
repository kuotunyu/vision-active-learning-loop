"""Cross-seed summary of v0.2-lite experiments.

Implements the reporting rule of the approved design (Section 10.3): nAUBC per
seed and arm, paired arm-minus-random deltas per seed, their mean and median,
and all-seed sign consistency. Every input is a published experiment receipt;
nothing is recomputed from checkpoints.
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
from .train import REGISTERED_ARMS, REGISTERED_BUDGET_FRACTIONS, SHARED_START_ROLE

RECEIPT_TYPE = "lite-experiment"
FINAL_FRACTION = REGISTERED_BUDGET_FRACTIONS[-1]


class SummaryError(ValueError):
    """Raised when the receipts cannot be summarized together."""


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


def summarize_experiments(receipts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Aggregate one or more single-seed experiment receipts."""
    if not receipts:
        raise SummaryError("at least one experiment receipt is required")
    per_seed: list[dict[str, Any]] = []
    manifests: set[str] = set()
    seen_seeds: set[int] = set()
    curves: dict[str, dict[str, list[float]]] = {}

    for receipt in receipts:
        normative = _normative(receipt)
        seed = normative.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise SummaryError("receipt seed must be an integer")
        if seed in seen_seeds:
            raise SummaryError(f"seed {seed} appears more than once")
        seen_seeds.add(seed)
        manifests.add(str(normative.get("manifest_sha256")))
        naubc = normative.get("naubc")
        if not isinstance(naubc, Mapping) or "random" not in naubc:
            raise SummaryError("receipt naubc must include the random arm")
        arms = [arm for arm in REGISTERED_ARMS if arm in naubc]
        deltas = {arm: float(naubc[arm]) - float(naubc["random"]) for arm in arms}
        min_recall: dict[str, float] = {}
        for fit in normative.get("fits", ()):
            arm = fit["arm"]
            fraction = f"{float(fit['budget_fraction']):.2f}"
            value = float(fit["metrics"]["mAP50_95"])
            curves.setdefault(arm, {}).setdefault(fraction, []).append(value)
            if float(fit["budget_fraction"]) == FINAL_FRACTION:
                min_recall[arm] = _min_class_recall(fit["metrics"])
        per_seed.append(
            {
                "seed": seed,
                "experiment_id": normative.get("experiment_id"),
                "naubc": {arm: float(naubc[arm]) for arm in ["random", *arms]},
                "delta_vs_random": deltas,
                f"min_class_recall_at_{FINAL_FRACTION:.2f}": min_recall,
            }
        )
    if len(manifests) != 1:
        raise SummaryError("every receipt must bind the same manifest")

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
    return {
        "receipt_type": "lite-summary",
        "schema_version": 1,
        "manifest_sha256": next(iter(manifests)),
        "seeds": [row["seed"] for row in per_seed],
        "arms": ["random", *arms_present],
        "per_seed": per_seed,
        "delta_vs_random": delta_summary,
        "mean_map50_95": mean_curve,
        "claim_rule": (
            "an arm may be called consistently above random only when every "
            "seed's paired nAUBC delta is positive; single-seed deltas sit within "
            "the same-host replay spread"
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
        rows.append(record)
    return rows


@command("lite summarize")
def summary_main(argv: Sequence[str] | None = None) -> int:
    """Summarize several single-seed experiments into summary.json and summary.csv."""
    parser = argparse.ArgumentParser(prog="val lite summarize")
    parser.add_argument("--experiment", action="append", required=True)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args(list(argv) if argv is not None else None)

    receipts = []
    try:
        for root in arguments.experiment:
            path = Path(root) / "experiment-receipt.json"
            try:
                receipts.append(json.loads(path.read_text(encoding="utf-8")))
            except (OSError, ValueError) as error:
                raise SummaryError(f"{path} is unavailable: {error}") from error
        summary = summarize_experiments(receipts)
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
