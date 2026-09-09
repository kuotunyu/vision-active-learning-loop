"""Fixed-step training loop and fit receipt for v0.2-lite.

Implements protocol Section 3: one thousand optimizer steps with a fifty-step
linear warm-up then cosine decay, batch size eight, gradient-norm clipping at
0.1, and a seed-deterministic sampler that reshuffles every epoch. The loop
takes its model, optimizer, scheduler, and batches from the caller so the same
code path serves the GPU run and the CPU tests.
"""

from __future__ import annotations

import math
import statistics
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

import torch

from .dataset import epoch_order

TRAINING_STEPS = 1000
WARMUP_STEPS = 50
BATCH_SIZE = 8
GRADIENT_CLIP = 0.1
LOSS_WINDOW_FRACTION = 0.1
DETECTOR_LEARNING_RATE = 1e-4
BACKBONE_LEARNING_RATE = 1e-5
WEIGHT_DECAY = 1e-4
REGISTERED_ARMS = ("random", "entropy", "margin")
SHARED_START_ROLE = "shared"
FIT_ROLES = REGISTERED_ARMS + (SHARED_START_ROLE,)
REGISTERED_BUDGET_FRACTIONS = (0.02, 0.05, 0.10, 0.20)
RECEIPT_TYPE = "lite-fit"
SCHEMA_VERSION = 1

_SHA256_LENGTH = 64


class TrainingError(ValueError):
    """Raised when a training input, step, or receipt field is not usable."""


@dataclass(frozen=True)
class FitResult:
    steps: int
    losses: tuple[float, ...]
    learning_rates: tuple[float, ...]
    gradient_norms: tuple[float, ...]
    gradient_clip: float
    first_window_median: float
    last_window_median: float
    loss_decreased: bool
    peak_allocated_bytes: int
    backward_evidence: Any = field(default=None)


def learning_rate_multiplier(
    step: int,
    *,
    total_steps: int = TRAINING_STEPS,
    warmup_steps: int = WARMUP_STEPS,
) -> float:
    """Return the linear warm-up then cosine decay factor for one step."""
    if not isinstance(step, int) or isinstance(step, bool):
        raise TrainingError("step must be an integer")
    if total_steps <= 0 or warmup_steps <= 0 or warmup_steps >= total_steps:
        raise TrainingError("schedule bounds are invalid")
    if step < 0 or step >= total_steps:
        raise TrainingError("step is outside the schedule")
    if step < warmup_steps:
        return (step + 1) / warmup_steps
    progress = (step - warmup_steps + 1) / (total_steps - warmup_steps)
    return 0.5 * (1.0 + math.cos(math.pi * progress))


def build_lite_scheduler(
    optimizer: torch.optim.Optimizer,
    *,
    total_steps: int = TRAINING_STEPS,
    warmup_steps: int = WARMUP_STEPS,
) -> torch.optim.lr_scheduler.LambdaLR:
    """Create the protocol schedule bound to one optimizer."""
    return torch.optim.lr_scheduler.LambdaLR(
        optimizer,
        lambda step: learning_rate_multiplier(
            min(step, total_steps - 1),
            total_steps=total_steps,
            warmup_steps=warmup_steps,
        ),
    )


def training_batches(
    item_ids: Sequence[str],
    *,
    seed: int,
    steps: int,
    batch_size: int = BATCH_SIZE,
) -> Iterable[tuple[int, tuple[str, ...]]]:
    """Yield exactly `steps` `(epoch, items)` full batches, reshuffling per epoch."""
    values = tuple(item_ids)
    if not isinstance(steps, int) or isinstance(steps, bool) or steps <= 0:
        raise TrainingError("steps must be a positive integer")
    if not isinstance(batch_size, int) or isinstance(batch_size, bool):
        raise TrainingError("batch size must be an integer")
    if batch_size <= 0 or batch_size > len(values):
        raise TrainingError("batch size exceeds the acquired pool")

    produced = 0
    epoch = 0
    while produced < steps:
        order = epoch_order(values, seed=seed, epoch=epoch)
        for start in range(0, len(order) - batch_size + 1, batch_size):
            if produced == steps:
                break
            yield epoch, order[start : start + batch_size]
            produced += 1
        epoch += 1


def _median_window(losses: Sequence[float], *, last: bool) -> float:
    size = max(1, int(len(losses) * LOSS_WINDOW_FRACTION))
    window = losses[-size:] if last else losses[:size]
    return float(statistics.median(window))


def run_fit(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler.LRScheduler,
    batches: Iterable[Mapping[str, Any]],
    gradient_clip: float = GRADIENT_CLIP,
    backward_runner: Callable[[Callable[[], None]], Any] | None = None,
    autocast_dtype: torch.dtype | None = None,
) -> FitResult:
    """Run one fit over the given batches and record its step observations."""
    if not isinstance(model, torch.nn.Module):
        raise TrainingError("a torch model is required")
    if gradient_clip <= 0.0:
        raise TrainingError("gradient clip must be positive")

    device = next((parameter.device for parameter in model.parameters()), None)
    if device is not None and device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)
    parameters = [
        parameter for parameter in model.parameters() if parameter.requires_grad
    ]
    losses: list[float] = []
    learning_rates: list[float] = []
    gradient_norms: list[float] = []
    evidence: Any = None

    model.train()
    for batch in batches:
        optimizer.zero_grad(set_to_none=True)
        if autocast_dtype is None:
            outputs = model(**batch)
        else:
            with torch.autocast(device_type=device.type, dtype=autocast_dtype):
                outputs = model(**batch)
        loss = getattr(outputs, "loss", None)
        if not isinstance(loss, torch.Tensor) or loss.ndim != 0:
            raise TrainingError("model must return a scalar loss")
        loss_value = float(loss.detach())
        if not math.isfinite(loss_value):
            raise TrainingError("training loss is not finite")

        if backward_runner is None:
            loss.backward()
        else:
            evidence = backward_runner(loss.backward)
        norm = torch.nn.utils.clip_grad_norm_(parameters, gradient_clip)
        norm_value = float(norm)
        if not math.isfinite(norm_value):
            raise TrainingError("gradient norm is not finite")

        learning_rates.append(float(optimizer.param_groups[0]["lr"]))
        optimizer.step()
        scheduler.step()
        losses.append(loss_value)
        gradient_norms.append(norm_value)

    if not losses:
        raise TrainingError("a fit requires at least one step")

    first_window = _median_window(losses, last=False)
    last_window = _median_window(losses, last=True)
    peak_allocated = (
        int(torch.cuda.max_memory_allocated(device))
        if device is not None and device.type == "cuda"
        else 0
    )
    return FitResult(
        steps=len(losses),
        losses=tuple(losses),
        learning_rates=tuple(learning_rates),
        gradient_norms=tuple(gradient_norms),
        gradient_clip=float(gradient_clip),
        first_window_median=first_window,
        last_window_median=last_window,
        loss_decreased=last_window < first_window,
        peak_allocated_bytes=peak_allocated,
        backward_evidence=evidence,
    )


def _digest(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _SHA256_LENGTH
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise TrainingError(f"{label} must be a lowercase SHA-256")
    return value


def fit_receipt(
    result: FitResult,
    *,
    experiment_id: str,
    manifest_sha256: str,
    arm: str,
    seed: int,
    budget_fraction: float,
    acquired_item_ids: Sequence[str],
    sampler_digest: str,
    model_sha256: str,
    checkpoint_sha256: str,
    environment: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Bind one fit's observations to the identities that make it auditable."""
    if not isinstance(result, FitResult):
        raise TrainingError("a fit result is required")
    if arm not in FIT_ROLES:
        raise TrainingError("arm is not registered")
    if float(budget_fraction) not in REGISTERED_BUDGET_FRACTIONS:
        raise TrainingError("budget fraction is not registered")
    if not isinstance(experiment_id, str) or not experiment_id:
        raise TrainingError("experiment id is required")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise TrainingError("seed must be an integer")
    acquired = tuple(acquired_item_ids)
    if not acquired or len(set(acquired)) != len(acquired):
        raise TrainingError("acquired item ids must be unique and non-empty")

    return {
        "receipt_type": RECEIPT_TYPE,
        "schema_version": SCHEMA_VERSION,
        "normative": {
            "experiment_id": experiment_id,
            "manifest_sha256": _digest(manifest_sha256, "manifest digest"),
            "arm": arm,
            "seed": seed,
            "budget_fraction": float(budget_fraction),
            "acquired_image_count": len(acquired),
            "sampler_digest": _digest(sampler_digest, "sampler digest"),
            "model_sha256": _digest(model_sha256, "model digest"),
            "checkpoint_sha256": _digest(checkpoint_sha256, "checkpoint digest"),
            "steps": result.steps,
            "recipe": {
                "batch_size": BATCH_SIZE,
                "gradient_clip": result.gradient_clip,
                "detector_learning_rate": DETECTOR_LEARNING_RATE,
                "backbone_learning_rate": BACKBONE_LEARNING_RATE,
                "weight_decay": WEIGHT_DECAY,
                "warmup_steps": WARMUP_STEPS,
                "total_steps": TRAINING_STEPS,
            },
            "loss": {
                "final": result.losses[-1],
                "first_window_median": result.first_window_median,
                "last_window_median": result.last_window_median,
                "decreased": result.loss_decreased,
            },
            "peak_allocated_bytes": result.peak_allocated_bytes,
            **(
                {"environment": dict(environment)}
                if environment is not None
                else {}
            ),
        },
    }
