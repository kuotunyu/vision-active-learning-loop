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


def _receipt(
    seed: int,
    naubc: dict[str, float],
    *,
    manifest: str = MANIFEST,
    rule: dict | None = None,
    with_compute: bool = False,
) -> dict:
    fits = []
    arms = (("shared", 0.002), ("random", 0.01), ("entropy", 0.02), ("margin", 0.03))
    for arm, base in arms:
        fractions = (0.02,) if arm == "shared" else (0.05, 0.10, 0.20)
        for fraction in fractions:
            fit = {
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
            if with_compute:
                fit["steps"] = int(1000 * fraction)
                fit["elapsed_seconds"] = 100.0 * fraction + seed
            fits.append(fit)
    normative = {
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
    }
    if rule is not None:
        normative["runtime"] = {"training_rule": rule}
    if with_compute:
        normative["timing"] = {
            "fit_seconds": 600.0,
            "scoring_seconds": 300.0,
            "evaluation_seconds": 200.0,
        }
    return {"receipt_type": "lite-experiment", "schema_version": 1, "normative": normative}


EPOCH_RULE = {"name": "fixed-epochs", "steps": None, "epochs": 18, "min_steps": 200}


def _reference(seed: int, value: float, *, rule: str = "fixed-epochs") -> dict:
    return {
        "experiment_id": f"lite-czech-ref-{rule}-s{seed}-test",
        "manifest_sha256": MANIFEST,
        "seed": seed,
        "arm": "reference",
        "budget_fraction": 1.0,
        "budget": 2255,
        "pool_size": 2255,
        "training_rule": {"name": rule, "steps": 5058},
        "steps": 5058,
        "elapsed_seconds": 1000.0,
        "metrics": {
            "mAP50_95": value,
            "AP50": 2 * value,
            "recall_D00": 0.6,
            "recall_D10": 0.5,
            "recall_D20": 0.2,
            "recall_D40": 0.4,
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


def test_summary_labels_legacy_receipts_as_fixed_steps_and_reports_ranges() -> None:
    receipts = [
        _receipt(17, {"random": 0.01, "entropy": 0.02, "margin": 0.03}),
        _receipt(29, {"random": 0.01, "entropy": 0.02, "margin": 0.03}),
    ]

    summary = summarize_experiments(receipts)

    assert summary["training_rule"] == "fixed-steps"
    assert summary["range_map50_95"]["margin"]["0.20"] == pytest.approx([0.23, 0.23])
    assert summary["compute"]["margin"]["0.20"] == {
        "images": 451,
        "mean_steps": None,
        "mean_elapsed_seconds": None,
    }
    assert summary["per_seed"][0]["timing_seconds"] is None
    assert summary["reference"] == {"per_seed": {}, "mean_map50_95": None}
    assert summary["per_seed"][0]["reference_mAP50_95"] is None
    assert "confidence" not in summary["claim_rule"].split("not a ")[0]


def test_summary_reports_the_rule_compute_and_timing_of_v021_receipts() -> None:
    receipts = [
        _receipt(17, {"random": 0.01, "entropy": 0.02, "margin": 0.03}, rule=EPOCH_RULE, with_compute=True),
        _receipt(29, {"random": 0.01, "entropy": 0.02, "margin": 0.03}, rule=EPOCH_RULE, with_compute=True),
    ]

    summary = summarize_experiments(receipts)

    assert summary["training_rule"] == "fixed-epochs"
    cell = summary["compute"]["entropy"]["0.10"]
    assert cell["images"] == 225
    assert cell["mean_steps"] == 100
    assert cell["mean_elapsed_seconds"] == pytest.approx(10.0 + 23.0)
    assert summary["per_seed"][1]["timing_seconds"]["scoring_seconds"] == 300.0


def test_summary_rejects_receipts_from_different_training_rules() -> None:
    same = {"random": 0.01, "entropy": 0.02, "margin": 0.03}

    with pytest.raises(SummaryError, match="training rule"):
        summarize_experiments([_receipt(17, same), _receipt(29, same, rule=EPOCH_RULE)])


def test_summary_relates_the_final_budget_to_a_matching_reference() -> None:
    same = {"random": 0.01, "entropy": 0.02, "margin": 0.03}
    receipts = [_receipt(17, same, rule=EPOCH_RULE), _receipt(29, same, rule=EPOCH_RULE)]

    summary = summarize_experiments(receipts, [_reference(17, 0.5), _reference(29, 0.4)])

    assert summary["reference"]["mean_map50_95"] == pytest.approx(0.45)
    assert summary["reference"]["per_seed"]["17"]["steps"] == 5058
    assert summary["reference"]["per_seed"]["17"]["min_class_recall"] == pytest.approx(0.2)
    row = {r["seed"]: r for r in summary["per_seed"]}
    assert row[17]["reference_mAP50_95"] == 0.5
    assert row[17]["fraction_of_reference_at_0.20"]["margin"] == pytest.approx(0.23 / 0.5)
    assert row[29]["fraction_of_reference_at_0.20"]["random"] == pytest.approx(0.21 / 0.4)


def test_summary_reference_without_a_seed_leaves_that_seed_unrelated() -> None:
    same = {"random": 0.01, "entropy": 0.02, "margin": 0.03}
    receipts = [_receipt(17, same, rule=EPOCH_RULE), _receipt(29, same, rule=EPOCH_RULE)]

    summary = summarize_experiments(receipts, [_reference(17, 0.5)])

    row = {r["seed"]: r for r in summary["per_seed"]}
    assert row[29]["reference_mAP50_95"] is None
    assert row[29]["fraction_of_reference_at_0.20"] is None


def test_summary_rejects_a_reference_from_another_rule_or_manifest_or_role() -> None:
    same = {"random": 0.01, "entropy": 0.02, "margin": 0.03}
    receipts = [_receipt(17, same, rule=EPOCH_RULE)]

    with pytest.raises(SummaryError, match="ran under"):
        summarize_experiments(receipts, [_reference(17, 0.5, rule="fixed-steps")])
    foreign = _reference(17, 0.5)
    foreign["manifest_sha256"] = "4" * 64
    with pytest.raises(SummaryError, match="manifest"):
        summarize_experiments(receipts, [foreign])
    shared = _reference(17, 0.5)
    shared["arm"] = "shared"
    with pytest.raises(SummaryError, match="reference fit"):
        summarize_experiments(receipts, [shared])
    with pytest.raises(SummaryError, match="more than once"):
        summarize_experiments(receipts, [_reference(17, 0.5), _reference(17, 0.6)])


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


def test_summary_command_accepts_reference_documents(tmp_path: Path, capsys) -> None:
    root = tmp_path / "lite-czech-ep18-s17-test"
    root.mkdir()
    (root / "experiment-receipt.json").write_text(
        json.dumps(
            _receipt(17, {"random": 0.01, "entropy": 0.02, "margin": 0.03}, rule=EPOCH_RULE)
        ),
        encoding="utf-8",
    )
    reference = tmp_path / "metrics-reference-1.00.json"
    reference.write_text(json.dumps(_reference(17, 0.5)), encoding="utf-8")
    out = tmp_path / "summary"

    exit_code = summary_main(
        ["--experiment", str(root), "--reference", str(reference), "--output", str(out)]
    )

    assert exit_code == 0
    printed = json.loads(capsys.readouterr().out)
    assert printed["training_rule"] == "fixed-epochs"
    assert printed["reference_mean_map50_95"] == 0.5
    with (out / "summary.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["reference_map"] == "0.5"
    assert float(rows[0]["ratio_margin"]) == pytest.approx(0.23 / 0.5)


def test_summary_command_reports_a_missing_receipt(tmp_path: Path) -> None:
    exit_code = summary_main(
        ["--experiment", str(tmp_path / "absent"), "--output", str(tmp_path / "out")]
    )

    assert exit_code == 3


def test_summary_command_writes_a_mean_budget_curve(tmp_path: Path) -> None:
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
    curve = (out / "mean-curve.svg").read_text(encoding="utf-8")
    assert curve.startswith("<svg")
    for arm in ("random", "entropy", "margin"):
        assert f">{arm}<" in curve
