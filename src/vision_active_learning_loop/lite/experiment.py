"""Whole-experiment schedule for v0.2-lite: one shared start, three arms, one
evaluation pass, and the aggregate outputs of protocol Sections 4 and 6.

The fitter, scorer, and evaluator are injectable so the schedule itself can be
verified without a model; the defaults are the real pinned-detector paths.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import torch

from ..artifacts.no_clobber import NoClobberError, create_directory_no_clobber
from ..cli_manifest import command
from ..models.rtdetr_contract import RDD_LABELS, extract_raw_contract
from ..probes.model_contract import build_contract_processor
from ..probes.training_feasibility import FeasibilityError
from ..training.checkpoint_io import (
    CheckpointVerificationError,
    load_checkpoint_verified,
)
from .acquisition import entropy_image_scores, margin_image_scores
from .dataset import DatasetError, build_image_index, load_sample
from .evaluate import EvaluationError, normalized_aubc
from .loop import (
    FitArtifacts,
    FitIdentity,
    FitRuntime,
    LoopError,
    cuda_backward_runner,
    evaluate_checkpoint,
    fit_once,
    load_pinned_detector,
    plan_baseline,
)
from .manifest import write_json_no_clobber
from .rounds import (
    RoundsError,
    ledger_entries,
    next_acquisition,
    round_plan,
    scoring_rows,
)
from .train import (
    BATCH_SIZE,
    REGISTERED_ARMS,
    REGISTERED_BUDGET_FRACTIONS,
    SHARED_START_ROLE,
    TRAINING_STEPS,
    WARMUP_STEPS,
)

RECEIPT_TYPE = "lite-experiment"
SCHEMA_VERSION = 1
METRIC_COLUMNS = ("mAP50_95", "AP50") + tuple(
    f"{prefix}_{label}" for label in RDD_LABELS for prefix in ("AP50_95", "recall")
)
_SCORERS = {"entropy": entropy_image_scores, "margin": margin_image_scores}


class ExperimentError(ValueError):
    """Raised when the experiment configuration or publication is not usable."""


@dataclass(frozen=True)
class ExperimentConfig:
    experiment_id: str
    seed: int
    arms: tuple[str, ...]
    snapshot: Path
    device: torch.device
    output_root: Path
    steps: int = TRAINING_STEPS
    batch_size: int = BATCH_SIZE
    warmup_steps: int = WARMUP_STEPS


@dataclass(frozen=True)
class ExperimentSummary:
    experiment_id: str
    root: Path
    receipt_path: Path
    fit_count: int
    naubc: Mapping[str, float]


@dataclass(frozen=True)
class _FitRecord:
    arm: str
    budget_fraction: float
    budget: int
    artifacts: FitArtifacts


def score_pool(
    *,
    arm: str,
    snapshot: Path,
    checkpoint_path: Path,
    checkpoint_sha256: str,
    public_rows: Sequence[Mapping[str, Any]],
    image_index: Mapping[str, Path],
    device: torch.device,
    batch_size: int = BATCH_SIZE,
) -> dict[str, float]:
    """Score label-free pool rows with one verified checkpoint for one arm."""
    scorer = _SCORERS.get(arm)
    if scorer is None:
        raise ExperimentError(f"arm {arm!r} does not score")
    try:
        state = load_checkpoint_verified(Path(checkpoint_path), checkpoint_sha256)
    except CheckpointVerificationError as error:
        raise ExperimentError(f"checkpoint is not usable: {error}") from error
    model = load_pinned_detector(snapshot)
    model.load_state_dict(state.model_state, strict=True)
    model.to(device)
    model.eval()
    processor = build_contract_processor()

    scores: dict[str, float] = {}
    rows = list(public_rows)
    for start in range(0, len(rows), batch_size):
        chunk = rows[start : start + batch_size]
        samples = [load_sample(image_index, row) for row in chunk]
        batch = processor(
            images=[sample.image for sample in samples], return_tensors="pt"
        )
        with torch.inference_mode():
            outputs = model(
                pixel_values=batch["pixel_values"].to(device),
                pixel_mask=batch["pixel_mask"].to(device),
            )
        values = scorer(extract_raw_contract(outputs)).tolist()
        for sample, value in zip(samples, values, strict=True):
            scores[sample.item_id] = float(value)
    return scores


def _validate_config(config: ExperimentConfig) -> None:
    if not config.arms:
        raise ExperimentError("at least one arm is required")
    if len(set(config.arms)) != len(config.arms):
        raise ExperimentError("arms must be unique")
    for arm in config.arms:
        if arm not in REGISTERED_ARMS:
            raise ExperimentError(f"arm {arm!r} is not registered")


def _runtime(config: ExperimentConfig) -> FitRuntime:
    is_cuda = config.device.type == "cuda"
    return FitRuntime(
        snapshot=Path(config.snapshot),
        device=config.device,
        steps=config.steps,
        batch_size=config.batch_size,
        warmup_steps=config.warmup_steps,
        autocast_dtype=torch.bfloat16 if is_cuda else None,
        backward_runner=cuda_backward_runner() if is_cuda else None,
    )


def _fit_dir(root: Path, arm: str, fraction: float) -> Path:
    return root / "fits" / f"{arm}-{fraction:.2f}"


_CURVE_COLOURS = {"random": "#6b7280", "entropy": "#d97706", "margin": "#2563eb"}


def _write_curve(
    path: Path, curves: Mapping[str, Sequence[tuple[float, float]]]
) -> None:
    """Write a dependency-free SVG budget curve; the 2% point is shared."""
    width, height, left, top = 640, 400, 64, 24
    plot_w, plot_h = width - left - 24, height - top - 56
    fractions = list(REGISTERED_BUDGET_FRACTIONS)
    x_min, x_max = fractions[0], fractions[-1]
    values = [value for points in curves.values() for _, value in points]
    y_max = max(0.05, max(values) * 1.15) if values else 1.0

    def sx(fraction: float) -> float:
        return left + (fraction - x_min) / (x_max - x_min) * plot_w

    def sy(value: float) -> float:
        return top + plot_h - (value / y_max) * plot_h

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="sans-serif" font-size="12">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for tick in range(6):
        value = y_max * tick / 5
        y = sy(value)
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{left + plot_w}" y2="{y:.1f}" '
            f'stroke="#e5e7eb"/>'
        )
        parts.append(
            f'<text x="{left - 6}" y="{y + 4:.1f}" text-anchor="end">{value:.2f}</text>'
        )
    for fraction in fractions:
        x = sx(fraction)
        parts.append(
            f'<text x="{x:.1f}" y="{top + plot_h + 18}" text-anchor="middle">'
            f"{int(round(fraction * 100))}%</text>"
        )
    parts.append(
        f'<rect x="{left}" y="{top}" width="{plot_w}" height="{plot_h}" '
        f'fill="none" stroke="#9ca3af"/>'
    )
    for index, (arm, points) in enumerate(sorted(curves.items())):
        colour = _CURVE_COLOURS.get(arm, "#111827")
        polyline = " ".join(f"{sx(f):.1f},{sy(v):.1f}" for f, v in points)
        parts.append(
            f'<polyline points="{polyline}" fill="none" stroke="{colour}" '
            f'stroke-width="2"/>'
        )
        for fraction, value in points:
            parts.append(
                f'<circle cx="{sx(fraction):.1f}" cy="{sy(value):.1f}" r="3.5" '
                f'fill="{colour}"/>'
            )
        parts.append(
            f'<text x="{left + plot_w - 8}" y="{top + 16 + 16 * index}" '
            f'text-anchor="end" fill="{colour}">{arm}</text>'
        )
    parts.append(
        f'<text x="{left + plot_w / 2:.1f}" y="{height - 8}" text-anchor="middle">'
        "acquired image fraction (2% point is shared) vs source-test mAP50-95</text>"
    )
    parts.append("</svg>")
    with path.open("x", encoding="utf-8") as handle:
        handle.write("\n".join(parts) + "\n")


def run_experiment(
    config: ExperimentConfig,
    *,
    manifest: Mapping[str, Any],
    public_view: Mapping[str, Any],
    image_index: Mapping[str, Path],
    fitter: Callable[..., FitArtifacts] = fit_once,
    scorer: Callable[..., Mapping[str, float]] = score_pool,
    evaluator: Callable[..., Mapping[str, float]] = evaluate_checkpoint,
) -> ExperimentSummary:
    """Run the shared start, every arm's rounds, and the final evaluation pass."""
    _validate_config(config)
    try:
        plan = plan_baseline(
            manifest, public_view, seed=config.seed, experiment_id=config.experiment_id
        )
    except LoopError as error:
        raise ExperimentError(str(error)) from error

    output_root = Path(config.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    try:
        root = create_directory_no_clobber(output_root / config.experiment_id)
    except (NoClobberError, OSError) as error:
        raise ExperimentError(
            f"experiment root exists or is unusable: {error}"
        ) from error
    (root / "fits").mkdir()

    rows = {row["item_id"]: row for row in manifest["images"]}
    pool_ids = tuple(str(row["item_id"]) for row in public_view["images"])
    test_rows = [row for row in manifest["images"] if row["split"] == "test"]
    runtime = _runtime(config)

    def fit(arm: str, fraction: float, items: Sequence[str]) -> FitArtifacts:
        ordered = tuple(sorted(items))
        identity = FitIdentity(
            experiment_id=config.experiment_id,
            manifest_sha256=plan.manifest_sha256,
            arm=arm,
            seed=config.seed,
            budget_fraction=fraction,
            item_ids=ordered,
        )
        return fitter(
            identity,
            runtime,
            rows_by_item={item: rows[item] for item in ordered},
            image_index=image_index,
            output_dir=_fit_dir(root, arm, fraction),
        )

    fits: list[_FitRecord] = []
    shared = fit(
        SHARED_START_ROLE, REGISTERED_BUDGET_FRACTIONS[0], plan.start_item_ids
    )
    fits.append(
        _FitRecord(
            SHARED_START_ROLE, REGISTERED_BUDGET_FRACTIONS[0], plan.budget, shared
        )
    )

    for arm in config.arms:
        acquired: set[str] = set(plan.start_item_ids)
        previous = shared
        entries = []
        for round_index, (fraction, count, delta) in enumerate(
            round_plan(pool_size=plan.pool_size), start=1
        ):
            unacquired = tuple(item for item in pool_ids if item not in acquired)
            scores = None
            if arm != "random":
                scores = scorer(
                    arm=arm,
                    snapshot=runtime.snapshot,
                    checkpoint_path=previous.checkpoint_path,
                    checkpoint_sha256=previous.checkpoint_sha256,
                    public_rows=scoring_rows(rows, unacquired=unacquired),
                    image_index=image_index,
                    device=config.device,
                    batch_size=config.batch_size,
                )
            try:
                chosen = next_acquisition(
                    arm,
                    scores=scores,
                    acquired=acquired,
                    pool_ids=pool_ids,
                    seed=config.seed,
                    count=delta,
                )
            except RoundsError as error:
                raise ExperimentError(str(error)) from error
            entries.extend(
                ledger_entries(
                    round_index=round_index,
                    budget_fraction=fraction,
                    chosen=chosen,
                    scores=scores,
                )
            )
            acquired |= set(chosen)
            if len(acquired) != count:
                raise ExperimentError(f"{arm} budget mismatch at {fraction}")
            previous = fit(arm, fraction, tuple(acquired))
            fits.append(_FitRecord(arm, fraction, count, previous))
        write_json_no_clobber(
            root / f"ledger-{arm}.json",
            {
                "arm": arm,
                "seed": config.seed,
                "manifest_sha256": plan.manifest_sha256,
                "entries": [asdict(entry) for entry in entries],
            },
        )

    evaluated: list[dict[str, Any]] = []
    for record in fits:
        metrics = evaluator(
            snapshot=runtime.snapshot,
            checkpoint_path=record.artifacts.checkpoint_path,
            checkpoint_sha256=record.artifacts.checkpoint_sha256,
            test_rows=test_rows,
            image_index=image_index,
            device=config.device,
            batch_size=config.batch_size,
        )
        evaluated.append(
            {
                "arm": record.arm,
                "budget_fraction": record.budget_fraction,
                "budget": record.budget,
                "checkpoint_sha256": record.artifacts.checkpoint_sha256,
                "receipt_path": str(record.artifacts.receipt_path.relative_to(root)),
                "metrics": {key: float(metrics[key]) for key in METRIC_COLUMNS},
            }
        )

    shared_point = (
        REGISTERED_BUDGET_FRACTIONS[0],
        evaluated[0]["metrics"]["mAP50_95"],
    )
    curves: dict[str, list[tuple[float, float]]] = {}
    for entry in evaluated[1:]:
        curves.setdefault(entry["arm"], [shared_point]).append(
            (entry["budget_fraction"], entry["metrics"]["mAP50_95"])
        )
    naubc = {arm: normalized_aubc(points) for arm, points in curves.items()}
    deltas = (
        {arm: naubc[arm] - naubc["random"] for arm in naubc if arm != "random"}
        if "random" in naubc
        else {}
    )

    with (root / "metrics.csv").open("x", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            ["arm", "budget_fraction", "budget", "checkpoint_sha256", *METRIC_COLUMNS]
        )
        for entry in evaluated:
            writer.writerow(
                [
                    entry["arm"],
                    entry["budget_fraction"],
                    entry["budget"],
                    entry["checkpoint_sha256"],
                    *[entry["metrics"][key] for key in METRIC_COLUMNS],
                ]
            )
    _write_curve(root / "curve.svg", curves)

    receipt = {
        "receipt_type": RECEIPT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "normative": {
            "experiment_id": config.experiment_id,
            "manifest_sha256": plan.manifest_sha256,
            "seed": config.seed,
            "arms": list(config.arms),
            "pool_size": plan.pool_size,
            "test_image_count": len(test_rows),
            "budgets": {
                f"{fraction:.2f}": count
                for fraction, count, _ in round_plan(pool_size=plan.pool_size)
            }
            | {f"{REGISTERED_BUDGET_FRACTIONS[0]:.2f}": plan.budget},
            "runtime": {
                "device": config.device.type,
                "steps": config.steps,
                "batch_size": config.batch_size,
                "warmup_steps": config.warmup_steps,
                "snapshot": str(config.snapshot),
            },
            "fits": evaluated,
            "naubc": naubc,
            "naubc_delta_vs_random": deltas,
        },
    }
    receipt_path = root / "experiment-receipt.json"
    write_json_no_clobber(receipt_path, receipt)
    return ExperimentSummary(
        experiment_id=config.experiment_id,
        root=root,
        receipt_path=receipt_path,
        fit_count=len(fits),
        naubc=naubc,
    )


def _load_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise ExperimentError(f"{label} is unavailable: {error}") from error
    if not isinstance(document, Mapping):
        raise ExperimentError(f"{label} must be a JSON object")
    return document


@command("lite run")
def run_main(argv: Sequence[str] | None = None) -> int:
    """Run the full v0.2-lite experiment for one seed."""
    parser = argparse.ArgumentParser(prog="val lite run")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--public-view", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--device", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--arms", default=",".join(REGISTERED_ARMS))
    parser.add_argument("--steps", type=int, default=TRAINING_STEPS)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--warmup-steps", type=int, default=WARMUP_STEPS)
    arguments = parser.parse_args(list(argv) if argv is not None else None)

    try:
        manifest = _load_json(Path(arguments.manifest), "manifest")
        view = _load_json(Path(arguments.public_view), "public view")
        image_index = build_image_index(Path(arguments.images))
        config = ExperimentConfig(
            experiment_id=arguments.experiment_id,
            seed=arguments.seed,
            arms=tuple(part.strip() for part in arguments.arms.split(",") if part),
            snapshot=Path(arguments.snapshot),
            device=torch.device(arguments.device),
            output_root=Path(arguments.output_root),
            steps=arguments.steps,
            batch_size=arguments.batch_size,
            warmup_steps=arguments.warmup_steps,
        )
        _validate_config(config)
    except (ExperimentError, DatasetError, RuntimeError) as error:
        print(f"lite run input error: {error}", file=sys.stderr)
        return 3

    try:
        summary = run_experiment(
            config, manifest=manifest, public_view=view, image_index=image_index
        )
    except (
        ExperimentError,
        LoopError,
        RoundsError,
        EvaluationError,
        FeasibilityError,
        OSError,
    ) as error:
        print(f"lite run failed: {error}", file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "experiment_id": summary.experiment_id,
                "root": str(summary.root),
                "fit_count": summary.fit_count,
                "naubc": dict(summary.naubc),
            },
            sort_keys=True,
        )
    )
    return 0
