"""One end-to-end v0.2-lite fit: pinned detector, data, loop, checkpoint, receipt.

`fit_once` is the unit the experiment loop repeats. It validates the fit's
identity before touching a model, loads the pinned RT-DETR snapshot with the
four-class reset, streams augmented batches through the pinned processor,
runs the fixed-step loop, and publishes a checkpoint and receipt without
overwriting anything.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterator, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from ..artifacts.no_clobber import NoClobberError, create_directory_no_clobber
from ..models.rtdetr_contract import reset_four_class_head
from ..probes.model_contract import build_contract_processor
from ..probes.training_feasibility import (
    FeasibilityError,
    build_optimizer,
    configure_determinism,
    trainable_parameter_sha256,
)
from ..training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    capture_rng_state,
    save_checkpoint_atomic,
)
from .dataset import augment_sample, collate, load_sample, sampler_digest
from .manifest import write_json_no_clobber
from .train import (
    BATCH_SIZE,
    REGISTERED_ARMS,
    REGISTERED_BUDGET_FRACTIONS,
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
    if identity.arm not in REGISTERED_ARMS:
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
        result = run_fit(
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            batches=batches(),
            backward_runner=runtime.backward_runner,
            autocast_dtype=runtime.autocast_dtype,
        )
    except TrainingError as error:
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
