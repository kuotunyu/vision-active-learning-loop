import json
import shutil
from pathlib import Path

import pytest

from val_explainer.data import (
    ARMS,
    DEFAULT_RESULTS_ROOT,
    ExplainerDataError,
    format_delta,
    load_explainer_data,
)

SUMMARY = DEFAULT_RESULTS_ROOT / "summary-ep18-3seeds" / "summary.json"


def _summary() -> dict:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_results_root_points_at_the_repo():
    assert DEFAULT_RESULTS_ROOT.name == "results"
    assert DEFAULT_RESULTS_ROOT.parent.name == "docs"
    assert SUMMARY.is_file()


def test_pool_test_and_budgets_come_from_the_receipt():
    data = load_explainer_data()
    first = _summary()["per_seed"][0]["experiment_id"]
    receipt = json.loads((DEFAULT_RESULTS_ROOT / first / "experiment-receipt.json").read_text(encoding="utf-8"))["normative"]
    assert data.pool_size == receipt["pool_size"]
    assert data.test_size == receipt["test_image_count"]
    assert data.budgets == {k: int(v) for k, v in receipt["budgets"].items()}
    assert list(data.budgets) == ["0.02", "0.05", "0.10", "0.20"]
    assert data.start_count() == data.budgets["0.02"]


def test_deltas_match_the_summary_per_seed():
    data = load_explainer_data()
    summary = _summary()
    assert data.seeds == [int(s) for s in summary["seeds"]]
    for entry in summary["per_seed"]:
        seed = int(entry["seed"])
        for arm in ("entropy", "margin"):
            assert data.delta[arm][seed] == pytest.approx(entry["delta_vs_random"][arm])
    assert data.claim_rule == summary["claim_rule"]


def test_positive_seed_count_counts_strictly_positive_deltas():
    data = load_explainer_data()
    for arm in ("entropy", "margin"):
        expected = sum(1 for v in data.delta[arm].values() if v > 0)
        assert data.positive_seed_count(arm) == expected


def test_curves_have_four_ascending_points_per_arm_and_share_the_start():
    data = load_explainer_data()
    for seed in data.seeds:
        start = data.curves[seed]["random"][0]
        for arm in ARMS:
            points = data.curves[seed][arm]
            assert len(points) == 4
            fractions = [p[0] for p in points]
            assert fractions == sorted(fractions)
            assert fractions == [0.02, 0.05, 0.10, 0.20]
            assert points[0] == start


def test_curve_points_match_the_receipt_fits():
    data = load_explainer_data()
    for entry in _summary()["per_seed"]:
        seed = int(entry["seed"])
        receipt = json.loads((DEFAULT_RESULTS_ROOT / entry["experiment_id"] / "experiment-receipt.json").read_text(encoding="utf-8"))["normative"]
        for fit in receipt["fits"]:
            arm = fit["arm"]
            fraction = float(fit["budget_fraction"])
            expected = float(fit["metrics"]["mAP50_95"])
            arms = ARMS if arm == "shared" else (arm,)
            for a in arms:
                got = dict(data.curves[seed][a])[fraction]
                assert got == pytest.approx(expected)


def test_missing_results_root_raises(tmp_path: Path):
    with pytest.raises(ExplainerDataError):
        load_explainer_data(results_root=tmp_path)


def test_truncated_receipt_raises(tmp_path: Path):
    shutil.copytree(DEFAULT_RESULTS_ROOT / "summary-ep18-3seeds", tmp_path / "summary-ep18-3seeds")
    for entry in _summary()["per_seed"]:
        src = DEFAULT_RESULTS_ROOT / entry["experiment_id"]
        dst = tmp_path / entry["experiment_id"]
        dst.mkdir()
        receipt = json.loads((src / "experiment-receipt.json").read_text(encoding="utf-8"))
        receipt["normative"]["fits"] = receipt["normative"]["fits"][:9]
        (dst / "experiment-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ExplainerDataError, match="fits"):
        load_explainer_data(results_root=tmp_path)


def test_format_delta_keeps_the_sign_and_four_decimals():
    assert format_delta(0.0019409691678418661) == "+0.0019"
    assert format_delta(-0.00051) == "-0.0005"


# ------------------------------------------------------------------ long version (both rules)

from val_explainer.data import BUDGET_KEYS, Reference, RulePair, load_rule_pair, range_text  # noqa: E402


def test_rule_pair_loads_both_rules():
    pair = load_rule_pair()
    assert isinstance(pair, RulePair)
    assert pair.rule_a.rule_name == "fixed-steps"
    assert pair.rule_b.rule_name == "fixed-epochs"
    assert pair.rule_a.seeds == pair.rule_b.seeds
    assert pair.rule_a.batch_size == 8 and pair.rule_b.batch_size == 8


def test_rule_b_steps_and_epochs_come_from_receipts():
    b = load_rule_pair().rule_b
    assert b.steps == {"0.02": 200, "0.05": 252, "0.10": 504, "0.20": 1008}
    assert b.epochs == {"0.02": 40, "0.05": 18, "0.10": 18, "0.20": 18}


def test_rule_a_steps_from_runtime_and_epochs_computed_with_full_batches():
    a = load_rule_pair().rule_a
    assert a.steps == {k: 1000 for k in BUDGET_KEYS}
    # ceil(1000 / (images // 8)) with images 46/113/226/451 -> 200/72/36/18
    assert a.epochs == {"0.02": 200, "0.05": 72, "0.10": 36, "0.20": 18}


def test_mean_curve_has_four_points_per_arm_and_matches_summary():
    b = load_rule_pair().rule_b
    summary = _summary()
    for arm in ARMS:
        points = b.mean_curve[arm]
        assert [p[0] for p in points] == [0.02, 0.05, 0.10, 0.20]
        assert points[0][1] == pytest.approx(summary["mean_map50_95"]["shared"]["0.02"])
        assert points[3][1] == pytest.approx(summary["mean_map50_95"][arm]["0.20"])


def test_reference_per_seed_matches_summary_and_receipt():
    pair = load_rule_pair()
    for data, summary_dir in ((pair.rule_a, "summary-3seeds-with-reference"), (pair.rule_b, "summary-ep18-3seeds")):
        summary = json.loads((DEFAULT_RESULTS_ROOT / summary_dir / "summary.json").read_text(encoding="utf-8"))
        for seed in data.seeds:
            ref = data.reference[seed]
            entry = summary["reference"]["per_seed"][str(seed)]
            assert isinstance(ref, Reference)
            assert ref.map50_95 == pytest.approx(entry["mAP50_95"])
            assert ref.steps == entry["steps"] and ref.images == entry["images"]
            receipt = json.loads((DEFAULT_RESULTS_ROOT / entry["experiment_id"] / "fit-receipt.json").read_text(encoding="utf-8"))["normative"]
            assert ref.epochs == receipt["epochs_started"]
        assert data.reference_mean == pytest.approx(summary["reference"]["mean_map50_95"])
    assert pair.rule_b.reference[17].epochs == 18
    assert pair.rule_a.reference[17].epochs == 4


def test_ratio_and_min_recall_at_20_match_summary():
    b = load_rule_pair().rule_b
    summary = _summary()
    for entry in summary["per_seed"]:
        seed = int(entry["seed"])
        for arm in ARMS:
            assert b.ratio_20[seed][arm] == pytest.approx(entry["fraction_of_reference_at_0.20"][arm])
            assert b.min_recall_20[seed][arm] == pytest.approx(entry["min_class_recall_at_0.20"][arm])
    assert b.arm_values_20("ratio_20", "random") == [b.ratio_20[s]["random"] for s in b.seeds]


def test_range_text_formats_min_and_max():
    assert range_text([0.302, 0.445, 0.363], 2) == "0.30–0.45"
    assert range_text([0.0656, 0.0670, 0.0666], 4) == "0.0656–0.0670"
    assert range_text([0.3], 3) == "0.300–0.300"


def test_missing_reference_block_raises(tmp_path: Path):
    shutil.copytree(DEFAULT_RESULTS_ROOT / "summary-ep18-3seeds", tmp_path / "summary-ep18-3seeds")
    for entry in _summary()["per_seed"]:
        shutil.copytree(DEFAULT_RESULTS_ROOT / entry["experiment_id"], tmp_path / entry["experiment_id"])
    summary_path = tmp_path / "summary-ep18-3seeds" / "summary.json"
    document = json.loads(summary_path.read_text(encoding="utf-8"))
    del document["reference"]
    summary_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ExplainerDataError, match="reference"):
        load_explainer_data(results_root=tmp_path)
