"""One end-to-end v0.2-lite fit: pinned detector, data, loop, checkpoint, receipt.

`fit_once` is the unit the experiment loop repeats. It validates the fit's
identity before touching a model, loads the pinned RT-DETR snapshot with the
four-class reset, streams augmented batches through the pinned processor,
runs the fixed-step loop, and publishes a checkpoint and receipt without
overwriting anything.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch.nn.attention import SDPBackend, sdpa_kernel

from ..artifacts.no_clobber import NoClobberError, create_directory_no_clobber
from ..models.rtdetr_contract import extract_raw_contract, reset_four_class_head
from ..probes.model_contract import build_contract_processor
from ..probes.training_feasibility import (
    FeasibilityError,
    build_optimizer,
    configure_determinism,
    run_allowlisted_backward,
    trainable_parameter_sha256,
)
from ..training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    capture_rng_state,
    load_checkpoint_verified,
    save_checkpoint_atomic,
)
from .acquisition import shared_start_order
from ..cli_manifest import command
from .dataset import (
    DatasetError,
    augment_sample,
    build_image_index,
    collate,
    load_sample,
    sampler_digest,
)
from .evaluate import EvaluationError, detections_from_outputs, evaluate_detections
from .manifest import manifest_sha256, write_json_no_clobber
from .rounds import RoundsError
from .rounds import budget_count as _exact_budget_count
from .train import (
    BATCH_SIZE,
    FIT_ROLES,
    REGISTERED_BUDGET_FRACTIONS,
    SHARED_START_ROLE,
    TRAINING_STEPS,
    WARMUP_STEPS,
    FitResult,
    TrainingError,
    build_lite_scheduler,
    fit_receipt,
    run_fit,
    training_batches,
)

CHECKPOINT_NAME = "checkpoint.pt"
RECEIPT_NAME = "fit-receipt.json"
RESET_SEED = 17
ALLOWLISTED_BACKWARD_WARNINGS = 9

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")


class LoopError(ValueError):
    """Raised when a fit's identity, inputs, or publication are not usable."""


@dataclass(frozen=True)
class FitIdentity:
    experiment_id: str
    manifest_sha256: str
    arm: str
    seed: int
    budget_fraction: float
    item_ids: tuple[str, ...]


@dataclass(frozen=True)
class FitRuntime:
    snapshot: Path
    device: torch.device
    steps: int = TRAINING_STEPS
    batch_size: int = BATCH_SIZE
    warmup_steps: int = WARMUP_STEPS
    autocast_dtype: torch.dtype | None = None
    backward_runner: Callable[[Callable[[], None]], Any] | None = None
    deterministic_attention: bool = True


@dataclass(frozen=True)
class FitArtifacts:
    result: FitResult
    receipt: Mapping[str, Any]
    receipt_path: Path
    checkpoint_path: Path
    checkpoint_sha256: str
    model_sha256: str


def _validate_identity(identity: FitIdentity) -> None:
    if not isinstance(identity, FitIdentity):
        raise LoopError("a fit identity is required")
    if not identity.experiment_id:
        raise LoopError("experiment id is required")
    if not _SHA256_PATTERN.match(identity.manifest_sha256):
        raise LoopError("manifest digest must be a lowercase SHA-256")
    if identity.arm not in FIT_ROLES:
        raise LoopError(f"arm {identity.arm!r} is not registered")
    if float(identity.budget_fraction) not in REGISTERED_BUDGET_FRACTIONS:
        raise LoopError("budget fraction is not registered")
    if not isinstance(identity.seed, int) or isinstance(identity.seed, bool):
        raise LoopError("seed must be an integer")
    items = identity.item_ids
    if not items or len(set(items)) != len(items):
        raise LoopError("acquired item ids must be unique and non-empty")


def _validate_runtime(runtime: FitRuntime) -> None:
    if not isinstance(runtime, FitRuntime):
        raise LoopError("a fit runtime is required")
    if runtime.steps <= 0 or runtime.batch_size <= 0:
        raise LoopError("steps and batch size must be positive")
    if runtime.warmup_steps <= 0 or runtime.warmup_steps >= runtime.steps:
        raise LoopError("warm-up steps must be positive and shorter than the fit")


def _validate_inputs(
    identity: FitIdentity,
    rows_by_item: Mapping[str, Mapping[str, Any]],
    image_index: Mapping[str, Path],
) -> None:
    for item_id in identity.item_ids:
        if item_id not in rows_by_item:
            raise LoopError(f"{item_id} is absent from the manifest rows")
        if item_id not in image_index:
            raise LoopError(f"{item_id} is absent from the image index")


def deterministic_attention_context():
    """Restrict SDPA to the Math backend, as Wave 0 A6 did for the labeled step.

    Fused Flash and Memory-Efficient attention backwards emit their own
    nondeterminism warnings on CUDA; only the Math backend keeps the backward
    warning inventory at the nine registered grid-sample warnings.
    """
    return sdpa_kernel(SDPBackend.MATH)


def load_pinned_detector(snapshot: Path) -> torch.nn.Module:
    """Load the pinned RT-DETR snapshot offline and apply the four-class reset."""
    root = Path(snapshot)
    if not root.is_dir():
        raise LoopError(f"model snapshot is unavailable: {root}")
    from transformers import RTDetrForObjectDetection

    try:
        model = RTDetrForObjectDetection.from_pretrained(
            root, local_files_only=True, use_safetensors=True
        )
    except Exception as error:
        raise LoopError(f"model snapshot could not be loaded: {error}") from error
    reset_four_class_head(model, seed=RESET_SEED)
    return model


def _to_device(value: Any, device: torch.device) -> Any:
    if isinstance(value, torch.Tensor):
        return value.to(device)
    if isinstance(value, Mapping):
        return {key: _to_device(item, device) for key, item in value.items()}
    if isinstance(value, list):
        return [_to_device(item, device) for item in value]
    return value


def _to_cpu_state(value: Any) -> Any:
    if isinstance(value, torch.Tensor):
        return value.detach().to("cpu").clone()
    if isinstance(value, Mapping):
        return {key: _to_cpu_state(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return type(value)(_to_cpu_state(item) for item in value)
    return value


def _environment(runtime: FitRuntime, evidence: Any) -> dict[str, Any]:
    document: dict[str, Any] = {
        "device": runtime.device.type,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
        "steps": runtime.steps,
        "warmup_steps": runtime.warmup_steps,
        "batch_size": runtime.batch_size,
        "autocast_dtype": (
            str(runtime.autocast_dtype).replace("torch.", "")
            if runtime.autocast_dtype is not None
            else None
        ),
        "deterministic_algorithms": bool(
            torch.are_deterministic_algorithms_enabled()
        ),
        "sdpa_backend": "MATH" if runtime.deterministic_attention else "default",
    }
    if runtime.device.type == "cuda":
        document["gpu_name"] = torch.cuda.get_device_name(runtime.device)
    observed = getattr(evidence, "observed_count", None)
    if observed is not None:
        document["allowlisted_backward_warnings"] = int(observed)
    return document


def fit_once(
    identity: FitIdentity,
    runtime: FitRuntime,
    *,
    rows_by_item: Mapping[str, Mapping[str, Any]],
    image_index: Mapping[str, Path],
    output_dir: Path,
) -> FitArtifacts:
    """Train one fit from the pinned base and publish its checkpoint and receipt."""
    _validate_identity(identity)
    _validate_runtime(runtime)
    _validate_inputs(identity, rows_by_item, image_index)
    try:
        output = create_directory_no_clobber(Path(output_dir))
    except (NoClobberError, OSError) as error:
        raise LoopError(f"fit output directory is not usable: {error}") from error

    try:
        configure_determinism(identity.seed)
    except FeasibilityError as error:
        raise LoopError(str(error)) from error
    model = load_pinned_detector(runtime.snapshot)
    if runtime.deterministic_attention:
        implementation = getattr(
            getattr(model, "config", None), "_attn_implementation", None
        )
        if implementation != "sdpa":
            raise LoopError("deterministic attention requires the sdpa implementation")
    model_sha256 = trainable_parameter_sha256(model)
    model.to(runtime.device)
    processor = build_contract_processor()
    optimizer = build_optimizer(model)
    scheduler = build_lite_scheduler(
        optimizer, total_steps=runtime.steps, warmup_steps=runtime.warmup_steps
    )

    consumed: list[tuple[str, ...]] = []
    last_epoch = 0

    def batches() -> Iterator[Mapping[str, Any]]:
        nonlocal last_epoch
        for epoch, items in training_batches(
            identity.item_ids,
            seed=identity.seed,
            steps=runtime.steps,
            batch_size=runtime.batch_size,
        ):
            consumed.append(items)
            last_epoch = epoch
            samples = [
                augment_sample(
                    load_sample(image_index, rows_by_item[item]),
                    seed=identity.seed,
                    epoch=epoch,
                )
                for item in items
            ]
            batch = collate(processor, samples)
            yield {
                "pixel_values": batch["pixel_values"].to(runtime.device),
                "pixel_mask": batch["pixel_mask"].to(runtime.device),
                "labels": _to_device(batch["labels"], runtime.device),
            }

    try:
        if runtime.deterministic_attention:
            with deterministic_attention_context():
                result = run_fit(
                    model=model,
                    optimizer=optimizer,
                    scheduler=scheduler,
                    batches=batches(),
                    backward_runner=runtime.backward_runner,
                    autocast_dtype=runtime.autocast_dtype,
                )
        else:
            result = run_fit(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                batches=batches(),
                backward_runner=runtime.backward_runner,
                autocast_dtype=runtime.autocast_dtype,
            )
    except (TrainingError, FeasibilityError) as error:
        raise LoopError(str(error)) from error

    order_digest = sampler_digest(consumed)
    state = CheckpointState(
        model_state=_to_cpu_state(model.state_dict()),
        optimizer_state=_to_cpu_state(optimizer.state_dict()),
        scheduler_state=_to_cpu_state(scheduler.state_dict()),
        scaler_state=None,
        epoch=last_epoch,
        step=result.steps,
        sampler_order_digest=order_digest,
        rng_state=capture_rng_state(),
        input_digests={
            "manifest_sha256": identity.manifest_sha256,
            "model_sha256": model_sha256,
        },
    )
    checkpoint_path = output / CHECKPOINT_NAME
    try:
        checkpoint_sha256 = save_checkpoint_atomic(state, checkpoint_path)
    except (CheckpointVerificationError, NoClobberError, OSError) as error:
        raise LoopError(f"checkpoint could not be published: {error}") from error

    receipt = fit_receipt(
        result,
        experiment_id=identity.experiment_id,
        manifest_sha256=identity.manifest_sha256,
        arm=identity.arm,
        seed=identity.seed,
        budget_fraction=identity.budget_fraction,
        acquired_item_ids=identity.item_ids,
        sampler_digest=order_digest,
        model_sha256=model_sha256,
        checkpoint_sha256=checkpoint_sha256,
        environment=_environment(runtime, result.backward_evidence),
    )
    receipt_path = output / RECEIPT_NAME
    try:
        write_json_no_clobber(receipt_path, receipt)
    except (NoClobberError, OSError) as error:
        raise LoopError(f"receipt could not be published: {error}") from error
    return FitArtifacts(
        result=result,
        receipt=receipt,
        receipt_path=receipt_path,
        checkpoint_path=checkpoint_path,
        checkpoint_sha256=checkpoint_sha256,
        model_sha256=model_sha256,
    )


def budget_count(fraction: float, pool_size: int) -> int:
    """Return B(p) = ceil(p * N) exactly; see `rounds.budget_count`."""
    try:
        return _exact_budget_count(fraction, pool_size)
    except RoundsError as error:
        raise LoopError(str(error)) from error


def shared_start_items(pool_item_ids: Sequence[str], *, seed: int) -> tuple[str, ...]:
    """Return the shared 2% start every arm trains from for this seed."""
    order = shared_start_order(seed, pool_item_ids)
    return order[: budget_count(REGISTERED_BUDGET_FRACTIONS[0], len(order))]


def evaluate_checkpoint(
    *,
    snapshot: Path,
    checkpoint_path: Path,
    checkpoint_sha256: str,
    test_rows: Sequence[Mapping[str, Any]],
    image_index: Mapping[str, Path],
    device: torch.device,
    batch_size: int = BATCH_SIZE,
) -> dict[str, float]:
    """Score one verified checkpoint on the frozen test split."""
    try:
        state = load_checkpoint_verified(Path(checkpoint_path), checkpoint_sha256)
    except CheckpointVerificationError as error:
        raise LoopError(f"checkpoint is not usable: {error}") from error
    if batch_size <= 0:
        raise LoopError("batch size must be positive")
    rows = list(test_rows)
    if not rows:
        raise LoopError("evaluation requires test rows")

    model = load_pinned_detector(snapshot)
    try:
        model.load_state_dict(state.model_state, strict=True)
    except RuntimeError as error:
        raise LoopError(f"checkpoint does not fit the pinned model: {error}") from error
    model.to(device)
    model.eval()
    processor = build_contract_processor()

    detections = []
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
        detections.extend(
            detections_from_outputs(
                extract_raw_contract(outputs),
                item_ids=[sample.item_id for sample in samples],
                sizes=[sample.image.size for sample in samples],
            )
        )
    return evaluate_detections(rows, detections)


@dataclass(frozen=True)
class BaselinePlan:
    experiment_id: str
    manifest_sha256: str
    seed: int
    pool_size: int
    budget: int
    start_item_ids: tuple[str, ...]


def plan_baseline(
    manifest: Mapping[str, Any],
    public_view: Mapping[str, Any],
    *,
    seed: int,
    experiment_id: str,
) -> BaselinePlan:
    """Bind the shared 2% start to one manifest and its label-free pool view."""
    digest = manifest_sha256(manifest)
    if public_view.get("manifest_sha256") != digest:
        raise LoopError("public view does not bind this manifest")
    pool_rows = {
        row["item_id"]
        for row in manifest.get("images", ())
        if row.get("split") == "pool"
    }
    view_ids = tuple(str(row["item_id"]) for row in public_view.get("images", ()))
    if len(set(view_ids)) != len(view_ids) or set(view_ids) != pool_rows:
        raise LoopError("public view rows do not match the manifest pool")
    start = shared_start_items(view_ids, seed=seed)
    return BaselinePlan(
        experiment_id=experiment_id,
        manifest_sha256=digest,
        seed=seed,
        pool_size=len(view_ids),
        budget=len(start),
        start_item_ids=start,
    )


def cuda_backward_runner(
    expected_count: int = ALLOWLISTED_BACKWARD_WARNINGS,
) -> Callable[[Callable[[], None]], Any]:
    """Wrap backward in the A3 allowlist so only the known CUDA warnings pass."""

    def runner(backward: Callable[[], None]) -> Any:
        return run_allowlisted_backward(backward, expected_count=expected_count)

    return runner


def _load_json(path: Path, label: str) -> Mapping[str, Any]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise LoopError(f"{label} is unavailable: {error}") from error
    if not isinstance(document, Mapping):
        raise LoopError(f"{label} must be a JSON object")
    return document


@command("lite baseline")
def baseline_main(argv: Sequence[str] | None = None) -> int:
    """Fit the shared 2% start from the pinned base and score it on the test split."""
    parser = argparse.ArgumentParser(prog="val lite baseline")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--public-view", required=True)
    parser.add_argument("--images", required=True)
    parser.add_argument("--snapshot", required=True)
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--device", required=True)
    parser.add_argument("--output-root", required=True)
    parser.add_argument("--steps", type=int, default=TRAINING_STEPS)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--warmup-steps", type=int, default=WARMUP_STEPS)
    arguments = parser.parse_args(list(argv) if argv is not None else None)

    try:
        manifest = _load_json(Path(arguments.manifest), "manifest")
        view = _load_json(Path(arguments.public_view), "public view")
        plan = plan_baseline(
            manifest, view, seed=arguments.seed, experiment_id=arguments.experiment_id
        )
        image_index = build_image_index(Path(arguments.images))
        device = torch.device(arguments.device)
    except (LoopError, DatasetError, RuntimeError) as error:
        print(f"lite baseline input error: {error}", file=sys.stderr)
        return 3

    rows = {row["item_id"]: row for row in manifest["images"]}
    acquired_rows = {item: rows[item] for item in plan.start_item_ids}
    test_rows = [row for row in manifest["images"] if row["split"] == "test"]
    experiment_root = Path(arguments.output_root) / plan.experiment_id
    fit_dir = experiment_root / "fits" / f"{SHARED_START_ROLE}-0.02"
    metrics_path = experiment_root / f"metrics-{SHARED_START_ROLE}-0.02.json"
    (experiment_root / "fits").mkdir(parents=True, exist_ok=True)

    identity = FitIdentity(
        experiment_id=plan.experiment_id,
        manifest_sha256=plan.manifest_sha256,
        arm=SHARED_START_ROLE,
        seed=plan.seed,
        budget_fraction=REGISTERED_BUDGET_FRACTIONS[0],
        item_ids=plan.start_item_ids,
    )
    runtime = FitRuntime(
        snapshot=Path(arguments.snapshot),
        device=device,
        steps=arguments.steps,
        batch_size=arguments.batch_size,
        warmup_steps=arguments.warmup_steps,
        autocast_dtype=torch.bfloat16 if device.type == "cuda" else None,
        backward_runner=cuda_backward_runner() if device.type == "cuda" else None,
    )
    try:
        artifacts = fit_once(
            identity,
            runtime,
            rows_by_item=acquired_rows,
            image_index=image_index,
            output_dir=fit_dir,
        )
        metrics = evaluate_checkpoint(
            snapshot=runtime.snapshot,
            checkpoint_path=artifacts.checkpoint_path,
            checkpoint_sha256=artifacts.checkpoint_sha256,
            test_rows=test_rows,
            image_index=image_index,
            device=device,
            batch_size=arguments.batch_size,
        )
        document = {
            "experiment_id": plan.experiment_id,
            "manifest_sha256": plan.manifest_sha256,
            "seed": plan.seed,
            "arm": SHARED_START_ROLE,
            "budget_fraction": REGISTERED_BUDGET_FRACTIONS[0],
            "budget": plan.budget,
            "pool_size": plan.pool_size,
            "checkpoint_sha256": artifacts.checkpoint_sha256,
            "test_image_count": len(test_rows),
            "loss": artifacts.receipt["normative"]["loss"],
            "metrics": metrics,
        }
        write_json_no_clobber(metrics_path, document)
    except (LoopError, EvaluationError, FeasibilityError, OSError) as error:
        print(f"lite baseline failed: {error}", file=sys.stderr)
        try:
            write_json_no_clobber(
                experiment_root / "failure.json",
                {
                    "experiment_id": plan.experiment_id,
                    "stage": "baseline",
                    "type": type(error).__name__,
                    "error": str(error),
                },
            )
        except (NoClobberError, OSError) as publication_error:
            print(f"failure record not written: {publication_error}", file=sys.stderr)
        return 2
    print(json.dumps(document, sort_keys=True))
    return 0
