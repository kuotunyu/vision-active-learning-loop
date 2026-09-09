"""Contracts for the cross-seed summary of v0.2-lite experiments."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from vision_active_learning_loop.lite.summary import (
    SummaryError,
    summarize_experiments,
    summary_main,
)

MANIFEST = "3" * 64


def _receipt(seed: int, naubc: dict[str, float], *, manifest: str = MANIFEST) -> dict:
    fits = []
    arms = (("shared", 0.002), ("random", 0.01), ("entropy", 0.02), ("margin", 0.03))
    for arm, base in arms:
        fractions = (0.02,) if arm == "shared" else (0.05, 0.10, 0.20)
        for fraction in fractions:
            fits.append(
                {
                    "arm": arm,
                    "budget_fraction": fraction,
                    "budget": int(fraction * 2255),
                    "checkpoint_sha256": f"{seed:02d}{arm[:2]}".ljust(64, "0"),
                    "metrics": {
                        "mAP50_95": base + fraction,
                        "AP50": 2 * (base + fraction),
                        "recall_D00": 0.5,
                        "recall_D10": 0.4,
                        "recall_D20": 0.1 * seed / 17,
                        "recall_D40": 0.3,
                    },
                }
            )
    return {
        "receipt_type": "lite-experiment",
        "schema_version": 1,
        "normative": {
            "experiment_id": f"lite-czech-s{seed}-test",
            "manifest_sha256": manifest,
            "seed": seed,
            "arms": ["random", "entropy", "margin"],
            "pool_size": 2255,
            "test_image_count": 574,
            "fits": fits,
            "naubc": naubc,
            "naubc_delta_vs_random": {
                arm: naubc[arm] - naubc["random"] for arm in ("entropy", "margin")
            },
        },
    }


def test_summary_tabulates_every_seed_and_paired_deltas() -> None:
    receipts = [
        _receipt(17, {"random": 0.0147, "entropy": 0.0185, "margin": 0.0202}),
        _receipt(29, {"random": 0.0160, "entropy": 0.0150, "margin": 0.0210}),
    ]

    summary = summarize_experiments(receipts)

    assert summary["seeds"] == [17, 29]
    assert summary["manifest_sha256"] == MANIFEST
    per_seed = {row["seed"]: row for row in summary["per_seed"]}
    assert per_seed[17]["naubc"]["margin"] == pytest.approx(0.0202)
    assert per_seed[29]["delta_vs_random"]["entropy"] == pytest.approx(-0.0010)
    assert summary["delta_vs_random"]["margin"]["values"] == pytest.approx(
        [0.0055, 0.0050]
    )
    assert summary["delta_vs_random"]["margin"]["mean"] == pytest.approx(0.00525)
    assert summary["delta_vs_random"]["margin"]["median"] == pytest.approx(0.00525)
    assert summary["delta_vs_random"]["margin"]["sign_consistent"] is True
    assert summary["delta_vs_random"]["entropy"]["sign_consistent"] is False


def test_summary_reports_mean_map_per_arm_and_budget() -> None:
    receipts = [
        _receipt(17, {"random": 0.01, "entropy": 0.02, "margin": 0.03}),
        _receipt(29, {"random": 0.01, "entropy": 0.02, "margin": 0.03}),
    ]

    summary = summarize_experiments(receipts)

    curve = summary["mean_map50_95"]
    assert curve["shared"]["0.02"] == pytest.approx(0.002 + 0.02)
    assert curve["margin"]["0.20"] == pytest.approx(0.03 + 0.20)
    assert curve["random"]["0.05"] == pytest.approx(0.01 + 0.05)


def test_summary_records_min_class_recall_at_the_final_budget() -> None:
    receipts = [_receipt(17, {"random": 0.01, "entropy": 0.02, "margin": 0.03})]

    summary = summarize_experiments(receipts)

    row = summary["per_seed"][0]
    assert row["min_class_recall_at_0.20"]["margin"] == pytest.approx(0.1)


def test_summary_rejects_duplicate_seeds_or_mixed_manifests() -> None:
    same = {"random": 0.01, "entropy": 0.02, "margin": 0.03}
    with pytest.raises(SummaryError, match="seed"):
        summarize_experiments([_receipt(17, same), _receipt(17, same)])
    with pytest.raises(SummaryError, match="manifest"):
        summarize_experiments(
            [_receipt(17, same), _receipt(29, same, manifest="4" * 64)]
        )


def test_summary_rejects_a_receipt_without_the_random_arm() -> None:
    receipt = _receipt(17, {"entropy": 0.02, "margin": 0.03, "random": 0.01})
    del receipt["normative"]["naubc"]["random"]

    with pytest.raises(SummaryError, match="random"):
        summarize_experiments([receipt])


def test_summary_command_writes_json_and_csv_without_overwriting(
    tmp_path: Path,
) -> None:
    roots = []
    for seed, naubc in (
        (17, {"random": 0.0147, "entropy": 0.0185, "margin": 0.0202}),
        (29, {"random": 0.0160, "entropy": 0.0150, "margin": 0.0210}),
    ):
        root = tmp_path / f"lite-czech-s{seed}-test"
        root.mkdir()
        (root / "experiment-receipt.json").write_text(
            json.dumps(_receipt(seed, naubc)), encoding="utf-8"
        )
        roots.append(str(root))
    out = tmp_path / "summary"

    exit_code = summary_main(
        ["--experiment", roots[0], "--experiment", roots[1], "--output", str(out)]
    )

    assert exit_code == 0
    summary = json.loads((out / "summary.json").read_text(encoding="utf-8"))
    assert summary["seeds"] == [17, 29]
    with (out / "summary.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert {row["seed"] for row in rows} == {"17", "29"}
    assert {"naubc_random", "naubc_entropy", "naubc_margin", "delta_margin"} <= set(
        rows[0]
    )

    assert summary_main(["--experiment", roots[0], "--output", str(out)]) == 3


def test_summary_command_reports_a_missing_receipt(tmp_path: Path) -> None:
    exit_code = summary_main(
        ["--experiment", str(tmp_path / "absent"), "--output", str(tmp_path / "out")]
    )

    assert exit_code == 3
