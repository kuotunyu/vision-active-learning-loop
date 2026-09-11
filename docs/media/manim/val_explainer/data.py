"""Read the committed evidence the explainer animates. Nothing here is hand-typed."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# docs/media/manim/val_explainer/data.py -> parents[3] is docs/
DEFAULT_RESULTS_ROOT = Path(__file__).resolve().parents[3] / "results"
DEFAULT_SUMMARY_DIR = "summary-ep18-3seeds"
ARMS = ("random", "entropy", "margin")
SHARED_ARM = "shared"
FITS_PER_EXPERIMENT = 10
POINTS_PER_ARM = 4


class ExplainerDataError(ValueError):
    """Raised when the committed evidence is missing or malformed."""


@dataclass(frozen=True)
class ExplainerData:
    pool_size: int
    test_size: int
    budgets: dict[str, int]
    seeds: list[int]
    delta: dict[str, dict[int, float]]
    curves: dict[int, dict[str, list[tuple[float, float]]]]
    claim_rule: str

    def positive_seed_count(self, arm: str) -> int:
        return sum(1 for value in self.delta[arm].values() if value > 0)

    def start_count(self) -> int:
        return self.budgets["0.02"]


def format_delta(value: float) -> str:
    return f"{value:+.4f}"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ExplainerDataError(f"missing evidence file: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ExplainerDataError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(document, dict):
        raise ExplainerDataError(f"{path} must hold a JSON object")
    return document


def _require(document: dict[str, Any], key: str, path: Path) -> Any:
    if key not in document:
        raise ExplainerDataError(f"{path} lacks key {key!r}")
    return document[key]


def _receipt_points(fits: list[dict[str, Any]], path: Path) -> dict[str, list[tuple[float, float]]]:
    shared = [fit for fit in fits if fit.get("arm") == SHARED_ARM]
    if len(shared) != 1:
        raise ExplainerDataError(f"{path} must list exactly one shared fit, found {len(shared)}")
    start = (float(shared[0]["budget_fraction"]), float(shared[0]["metrics"]["mAP50_95"]))
    curves: dict[str, list[tuple[float, float]]] = {}
    for arm in ARMS:
        rest = sorted(
            (float(fit["budget_fraction"]), float(fit["metrics"]["mAP50_95"]))
            for fit in fits
            if fit.get("arm") == arm
        )
        points = [start, *rest]
        if len(points) != POINTS_PER_ARM:
            raise ExplainerDataError(f"{path}: arm {arm!r} has {len(points)} points, expected {POINTS_PER_ARM}")
        curves[arm] = points
    return curves


def load_explainer_data(
    results_root: Path = DEFAULT_RESULTS_ROOT,
    summary_dir: str = DEFAULT_SUMMARY_DIR,
) -> ExplainerData:
    root = Path(results_root)
    summary_path = root / summary_dir / "summary.json"
    summary = _load_json(summary_path)
    seeds = [int(seed) for seed in _require(summary, "seeds", summary_path)]
    claim_rule = str(_require(summary, "claim_rule", summary_path))
    per_seed = _require(summary, "per_seed", summary_path)

    delta: dict[str, dict[int, float]] = {"entropy": {}, "margin": {}}
    curves: dict[int, dict[str, list[tuple[float, float]]]] = {}
    header: tuple[int, int, dict[str, int]] | None = None

    for entry in per_seed:
        seed = int(_require(entry, "seed", summary_path))
        experiment_id = str(_require(entry, "experiment_id", summary_path))
        deltas = _require(entry, "delta_vs_random", summary_path)
        for arm in delta:
            if arm not in deltas:
                raise ExplainerDataError(f"{summary_path}: seed {seed} lacks delta for {arm!r}")
            delta[arm][seed] = float(deltas[arm])

        receipt_path = root / experiment_id / "experiment-receipt.json"
        normative = _require(_load_json(receipt_path), "normative", receipt_path)
        pool_size = int(_require(normative, "pool_size", receipt_path))
        test_size = int(_require(normative, "test_image_count", receipt_path))
        budgets = {str(k): int(v) for k, v in _require(normative, "budgets", receipt_path).items()}
        if header is None:
            header = (pool_size, test_size, budgets)
        elif header != (pool_size, test_size, budgets):
            raise ExplainerDataError(f"{receipt_path}: pool/test/budgets differ from the first seed")
        fits = _require(normative, "fits", receipt_path)
        if len(fits) != FITS_PER_EXPERIMENT:
            raise ExplainerDataError(f"{receipt_path} lists {len(fits)} fits, expected {FITS_PER_EXPERIMENT}")
        curves[seed] = _receipt_points(fits, receipt_path)

    if header is None or sorted(curves) != sorted(seeds):
        raise ExplainerDataError(f"{summary_path}: per_seed entries do not cover seeds {seeds}")
    pool_size, test_size, budgets = header
    return ExplainerData(
        pool_size=pool_size,
        test_size=test_size,
        budgets=budgets,
        seeds=seeds,
        delta=delta,
        curves=curves,
        claim_rule=claim_rule,
    )
