"""Read the committed evidence the explainer animates. Nothing here is hand-typed."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# docs/media/manim/val_explainer/data.py -> parents[3] is docs/
DEFAULT_RESULTS_ROOT = Path(__file__).resolve().parents[3] / "results"
DEFAULT_SUMMARY_DIR = "summary-ep18-3seeds"
RULE_A_SUMMARY_DIR = "summary-3seeds-with-reference"
ARMS = ("random", "entropy", "margin")
SHARED_ARM = "shared"
BUDGET_KEYS = ("0.02", "0.05", "0.10", "0.20")
FITS_PER_EXPERIMENT = 10
POINTS_PER_ARM = 4


class ExplainerDataError(ValueError):
    """Raised when the committed evidence is missing or malformed."""


@dataclass(frozen=True)
class Reference:
    map50_95: float
    steps: int
    images: int
    epochs: int


@dataclass(frozen=True)
class ExplainerData:
    pool_size: int
    test_size: int
    budgets: dict[str, int]
    seeds: list[int]
    delta: dict[str, dict[int, float]]
    curves: dict[int, dict[str, list[tuple[float, float]]]]
    claim_rule: str
    rule_name: str = ""
    batch_size: int = 0
    steps: dict[str, int] = field(default_factory=dict)
    epochs: dict[str, int] = field(default_factory=dict)
    mean_curve: dict[str, list[tuple[float, float]]] = field(default_factory=dict)
    reference: dict[int, Reference] = field(default_factory=dict)
    reference_mean: float = 0.0
    ratio_20: dict[int, dict[str, float]] = field(default_factory=dict)
    min_recall_20: dict[int, dict[str, float]] = field(default_factory=dict)

    def positive_seed_count(self, arm: str) -> int:
        return sum(1 for value in self.delta[arm].values() if value > 0)

    def start_count(self) -> int:
        return self.budgets["0.02"]

    def arm_values_20(self, table: str, arm: str) -> list[float]:
        rows: dict[int, dict[str, float]] = getattr(self, table)
        return [rows[seed][arm] for seed in self.seeds]


@dataclass(frozen=True)
class RulePair:
    rule_a: ExplainerData
    rule_b: ExplainerData


def format_delta(value: float) -> str:
    return f"{value:+.4f}"


def range_text(values: list[float], decimals: int) -> str:
    return f"{min(values):.{decimals}f}–{max(values):.{decimals}f}"


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


def _budget_key(fraction: float) -> str:
    return f"{fraction:.2f}"


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


def _steps_and_epochs(
    fits: list[dict[str, Any]], runtime: dict[str, Any], budgets: dict[str, int], path: Path
) -> tuple[dict[str, int], dict[str, int]]:
    """Per-budget steps and epochs. New receipts carry both per fit; old ones give steps in runtime and epochs are computed."""
    batch = int(_require(runtime, "batch_size", path))
    steps: dict[str, int] = {}
    epochs: dict[str, int] = {}
    for fit in fits:
        key = _budget_key(float(fit["budget_fraction"]))
        if "steps" in fit and "epochs_started" in fit:
            value_steps, value_epochs = int(fit["steps"]), int(fit["epochs_started"])
        else:
            value_steps = int(_require(runtime, "steps", path))
            value_epochs = math.ceil(value_steps / (budgets[key] // batch))
        if key in steps and (steps[key], epochs[key]) != (value_steps, value_epochs):
            raise ExplainerDataError(f"{path}: fits at budget {key} disagree on steps/epochs")
        steps[key], epochs[key] = value_steps, value_epochs
    if set(steps) != set(BUDGET_KEYS):
        raise ExplainerDataError(f"{path}: budgets covered {sorted(steps)}, expected {BUDGET_KEYS}")
    return steps, epochs


def _mean_curve(summary: dict[str, Any], path: Path) -> dict[str, list[tuple[float, float]]]:
    table = _require(summary, "mean_map50_95", path)
    if "shared" not in table or "0.02" not in table["shared"]:
        raise ExplainerDataError(f"{path}: mean_map50_95 lacks the shared 2% point")
    start = (0.02, float(table["shared"]["0.02"]))
    curves: dict[str, list[tuple[float, float]]] = {}
    for arm in ARMS:
        if arm not in table:
            raise ExplainerDataError(f"{path}: mean_map50_95 lacks arm {arm!r}")
        curves[arm] = [start] + [(float(key), float(table[arm][key])) for key in ("0.05", "0.10", "0.20")]
    return curves


def _references(
    root: Path, summary: dict[str, Any], seeds: list[int], path: Path
) -> tuple[dict[int, Reference], float]:
    block = _require(summary, "reference", path)
    per_seed = _require(block, "per_seed", path)
    references: dict[int, Reference] = {}
    for seed in seeds:
        entry = per_seed.get(str(seed))
        if entry is None:
            raise ExplainerDataError(f"{path}: reference block lacks seed {seed}")
        receipt_path = root / str(_require(entry, "experiment_id", path)) / "fit-receipt.json"
        receipt = _require(_load_json(receipt_path), "normative", receipt_path)
        references[seed] = Reference(
            map50_95=float(_require(entry, "mAP50_95", path)),
            steps=int(_require(entry, "steps", path)),
            images=int(_require(entry, "images", path)),
            epochs=int(_require(receipt, "epochs_started", receipt_path)),
        )
    return references, float(_require(block, "mean_map50_95", path))


def load_explainer_data(
    results_root: Path = DEFAULT_RESULTS_ROOT,
    summary_dir: str = DEFAULT_SUMMARY_DIR,
) -> ExplainerData:
    root = Path(results_root)
    summary_path = root / summary_dir / "summary.json"
    summary = _load_json(summary_path)
    seeds = [int(seed) for seed in _require(summary, "seeds", summary_path)]
    claim_rule = str(_require(summary, "claim_rule", summary_path))
    rule_name = str(_require(summary, "training_rule", summary_path))
    per_seed = _require(summary, "per_seed", summary_path)

    delta: dict[str, dict[int, float]] = {"entropy": {}, "margin": {}}
    curves: dict[int, dict[str, list[tuple[float, float]]]] = {}
    ratio_20: dict[int, dict[str, float]] = {}
    min_recall_20: dict[int, dict[str, float]] = {}
    header: tuple[int, int, dict[str, int]] | None = None
    steps_epochs: tuple[dict[str, int], dict[str, int]] | None = None
    batch_size = 0

    for entry in per_seed:
        seed = int(_require(entry, "seed", summary_path))
        experiment_id = str(_require(entry, "experiment_id", summary_path))
        deltas = _require(entry, "delta_vs_random", summary_path)
        for arm in delta:
            if arm not in deltas:
                raise ExplainerDataError(f"{summary_path}: seed {seed} lacks delta for {arm!r}")
            delta[arm][seed] = float(deltas[arm])
        ratios = _require(entry, "fraction_of_reference_at_0.20", summary_path)
        recalls = _require(entry, "min_class_recall_at_0.20", summary_path)
        ratio_20[seed] = {arm: float(ratios[arm]) for arm in ARMS}
        min_recall_20[seed] = {arm: float(recalls[arm]) for arm in ARMS}

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
        runtime = _require(normative, "runtime", receipt_path)
        batch_size = int(_require(runtime, "batch_size", receipt_path))
        current = _steps_and_epochs(fits, runtime, budgets, receipt_path)
        if steps_epochs is None:
            steps_epochs = current
        elif steps_epochs != current:
            raise ExplainerDataError(f"{receipt_path}: steps/epochs differ from the first seed")

    if header is None or steps_epochs is None or sorted(curves) != sorted(seeds):
        raise ExplainerDataError(f"{summary_path}: per_seed entries do not cover seeds {seeds}")
    pool_size, test_size, budgets = header
    steps, epochs = steps_epochs
    references, reference_mean = _references(root, summary, seeds, summary_path)
    return ExplainerData(
        pool_size=pool_size,
        test_size=test_size,
        budgets=budgets,
        seeds=seeds,
        delta=delta,
        curves=curves,
        claim_rule=claim_rule,
        rule_name=rule_name,
        batch_size=batch_size,
        steps=steps,
        epochs=epochs,
        mean_curve=_mean_curve(summary, summary_path),
        reference=references,
        reference_mean=reference_mean,
        ratio_20=ratio_20,
        min_recall_20=min_recall_20,
    )


def load_rule_pair(results_root: Path = DEFAULT_RESULTS_ROOT) -> RulePair:
    rule_a = load_explainer_data(results_root, RULE_A_SUMMARY_DIR)
    rule_b = load_explainer_data(results_root, DEFAULT_SUMMARY_DIR)
    if rule_a.rule_name != "fixed-steps" or rule_b.rule_name != "fixed-epochs":
        raise ExplainerDataError(f"unexpected rules: {rule_a.rule_name!r}, {rule_b.rule_name!r}")
    if rule_a.seeds != rule_b.seeds:
        raise ExplainerDataError("the two rules do not share the same seeds")
    return RulePair(rule_a=rule_a, rule_b=rule_b)
