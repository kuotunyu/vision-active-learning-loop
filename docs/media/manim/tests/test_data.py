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
