"""Deterministic BF16 training and checkpoint feasibility probe."""

from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import math
import os
import random
import sys
import time
import warnings
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import RTDetrForObjectDetection

from ..artifacts.digests import canonical_json_sha256, sha256_file
from ..artifacts.receipts import atomic_write_receipt, validate_receipt_for_run
from ..cli_manifest import command
from ..environment import (
    EnvironmentContract,
    environment_invariants,
    observe_environment,
)
from ..models.assets import (
    load_pinned_asset_specs,
    verify_snapshot,
    verify_transformers_source,
)
from ..models.rtdetr_contract import reset_four_class_head
from ..training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    capture_rng_state,
    checkpoint_state_digests,
    checkpoint_state_sha256,
    load_checkpoint_verified,
    restore_checkpoint_state,
    save_checkpoint_atomic,
    structured_state_sha256,
)
from .model_contract import (
    _artifact_root,
    _is_link_or_junction,
    _mapping,
    _project_root,
    _required_child_directory,
    _snapshot_root,
    build_contract_processor,
    load_synthetic_contract_fixture,
)


class FeasibilityError(ValueError):
    """Raised when a normative feasibility condition cannot be proved."""


SEED = 17
VRAM_LIMIT_BYTES = 22 * 1024**3
_CUBLAS_WORKSPACE_CONFIG = ":4096:8"
_PARAMETER_DIGEST_RULE = "ordered-trainable-named-parameters-sha256-v1"
_FIXTURE_MANIFEST = (
    _project_root() / "fixtures" / "synthetic" / "wave0" / "fixture-manifest.json"
)
_STATE_DIGEST_KEYS = ("model", "optimizer", "scheduler", "scaler", "rng", "sampler")
_ENVIRONMENT_COMPARISON_FIELDS = (
    "schema_version",
    "python",
    "uv",
    "scipy",
    "torch",
    "torchvision",
    "transformers",
    "pycocotools",
    "cuda_runtime",
    "gpu_name",
    "gpu_uuid",
    "driver",
    "os",
    "wsl",
    "container_image_digest",
    "runtime_image_digest",
    "tf32",
    "deterministic_algorithms",
    "bf16_supported",
    "data_root_unset",
)


@dataclass(frozen=True)
class DeterminismState:
    seed: int
    cuda_matmul_allow_tf32: bool
    cudnn_allow_tf32: bool
    cudnn_benchmark: bool
    deterministic_algorithms: bool
    deterministic_debug_mode: int
    cublas_workspace_config: str
    bf16_supported: bool


@dataclass(frozen=True)
class StepObservation:
    ordered_losses: tuple[float, ...]
    finite_loss: bool
    finite_gradients: bool
    parameter_changed: bool
    gradient_norm: float
    peak_allocated_bytes: int
    peak_reserved_bytes: int
    wall_seconds: float
    gpu_seconds: float
    cuda_matmul_allow_tf32: bool
    cudnn_allow_tf32: bool
    cudnn_benchmark: bool
    deterministic_algorithms: bool
    deterministic_debug_mode: int
    cublas_workspace_config: str
    bf16_supported: bool
    bf16_autocast_enabled: bool
    deterministic_fallback_detected: bool
    device: str
    live_model_state_digest_after: str
    trainable_parameter_count: int
    parameter_digest_before: str
    parameter_digest_after: str
    state_digests: Mapping[str, str]
    checkpoint_state: CheckpointState | None


def _normalized_gpu_uuid(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.removeprefix("GPU-").lower()
    groups = normalized.split("-")
    if [len(group) for group in groups] != [8, 4, 4, 4, 12]:
        return None
    if any(
        any(character not in "0123456789abcdef" for character in group)
        for group in groups
    ):
        return None
    return normalized


def validate_live_environment_evidence(
    parent_environment: Mapping[str, object],
    evidence: Mapping[str, object],
) -> dict[str, object]:
    """Fail closed unless Task 5 is running in Task 4's canonical environment."""
    observed = evidence.get("observed")
    selected = evidence.get("selected_cuda")
    if not isinstance(observed, Mapping) or not isinstance(selected, Mapping):
        raise FeasibilityError("live environment evidence must be complete objects")
    if (
        parent_environment.get("status") != "PASS"
        or parent_environment.get("errors") != []
    ):
        raise FeasibilityError("parent model-contract environment must be PASS")

    contract = EnvironmentContract.from_yaml(
        _project_root() / "configs" / "environment" / "wave0.yaml"
    )
    parent_errors = contract.validate(parent_environment)
    if parent_errors:
        raise FeasibilityError(
            "parent model-contract environment is non-canonical: "
            + "; ".join(parent_errors)
        )
    expected_parent_sha256 = canonical_json_sha256(dict(parent_environment))
    if evidence.get("parent_environment_sha256") != expected_parent_sha256:
        raise FeasibilityError("parent environment digest mismatch")

    live_errors = contract.validate(observed)
    live_invariants = environment_invariants(contract, observed)
    failed_invariants = [
        name for name, passed in live_invariants.items() if passed is not True
    ]
    if live_errors or failed_invariants:
        raise FeasibilityError(
            "live environment is non-canonical: "
            + "; ".join([*live_errors, *failed_invariants])
        )
    for field in _ENVIRONMENT_COMPARISON_FIELDS:
        if observed.get(field) != parent_environment.get(field):
            raise FeasibilityError(
                f"live {field} differs from the parent model-contract environment"
            )

    if (
        selected.get("cuda_available") is not True
        or type(selected.get("device_count")) is not int
        or selected.get("device_count", 0) < 1
        or selected.get("selected_index") != 0
        or selected.get("selected_device") != "cuda:0"
    ):
        raise FeasibilityError("canonical training feasibility must select cuda:0")
    if selected.get("selected_name") != contract.gpu_name:
        raise FeasibilityError("selected CUDA device must be NVIDIA GeForce RTX 4090")
    selected_uuid = _normalized_gpu_uuid(selected.get("selected_uuid"))
    observed_uuid = _normalized_gpu_uuid(observed.get("gpu_uuid"))
    parent_uuid = _normalized_gpu_uuid(parent_environment.get("gpu_uuid"))
    if (
        selected_uuid is None
        or selected_uuid != observed_uuid
        or selected_uuid != parent_uuid
    ):
        raise FeasibilityError("selected CUDA UUID differs from environment evidence")
    return {
        "observed": dict(observed),
        "selected_cuda": dict(selected),
        "parent_environment_sha256": expected_parent_sha256,
    }


def _observe_live_environment(
    parent_environment: Mapping[str, object],
) -> dict[str, object]:
    observed = observe_environment()
    observed["data_root_unset"] = "VAL_DATA_ROOT" not in os.environ
    selected_index = torch.cuda.current_device()
    raw_uuid = getattr(torch.cuda.get_device_properties(selected_index), "uuid", None)
    if isinstance(raw_uuid, bytes):
        selected_uuid = raw_uuid.decode("ascii")
    elif raw_uuid is None:
        selected_uuid = None
    else:
        selected_uuid = str(raw_uuid)
    evidence = {
        "observed": observed,
        "selected_cuda": {
            "cuda_available": torch.cuda.is_available(),
            "device_count": torch.cuda.device_count(),
            "selected_index": selected_index,
            "selected_name": torch.cuda.get_device_name(selected_index),
            "selected_uuid": selected_uuid,
            "selected_device": f"cuda:{selected_index}",
        },
        "parent_environment_sha256": canonical_json_sha256(dict(parent_environment)),
    }
    return validate_live_environment_evidence(parent_environment, evidence)


def configure_determinism(seed: int) -> DeterminismState:
    """Configure the exact fail-closed seeded CUDA determinism controls."""
    if type(seed) is not int or seed < 0:
        raise FeasibilityError("seed must be a non-negative integer")
    current_workspace = os.environ.get("CUBLAS_WORKSPACE_CONFIG")
    cuda_initialized = torch.cuda.is_initialized()
    if cuda_initialized and current_workspace != _CUBLAS_WORKSPACE_CONFIG:
        raise FeasibilityError(
            "CUBLAS_WORKSPACE_CONFIG must be set before CUDA initialization"
        )
    if not cuda_initialized:
        os.environ["CUBLAS_WORKSPACE_CONFIG"] = _CUBLAS_WORKSPACE_CONFIG
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cudnn.benchmark = False
    torch.use_deterministic_algorithms(True, warn_only=False)
    torch.set_deterministic_debug_mode("error")
    return DeterminismState(
        seed=seed,
        cuda_matmul_allow_tf32=bool(torch.backends.cuda.matmul.allow_tf32),
        cudnn_allow_tf32=bool(torch.backends.cudnn.allow_tf32),
        cudnn_benchmark=bool(torch.backends.cudnn.benchmark),
        deterministic_algorithms=bool(torch.are_deterministic_algorithms_enabled()),
        deterministic_debug_mode=int(torch.get_deterministic_debug_mode()),
        cublas_workspace_config=os.environ.get("CUBLAS_WORKSPACE_CONFIG", ""),
        bf16_supported=bool(
            torch.cuda.is_available() and torch.cuda.is_bf16_supported()
        ),
    )


def build_optimizer(model: torch.nn.Module) -> torch.optim.AdamW:
    """Build the approved detector/backbone AdamW parameter groups."""
    backbone: list[torch.nn.Parameter] = []
    detector: list[torch.nn.Parameter] = []
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        (backbone if name.startswith("model.backbone") else detector).append(parameter)
    if not backbone or not detector:
        raise FeasibilityError(
            "RT-DETR backbone/detector parameter groups are required"
        )
    return torch.optim.AdamW(
        [
            {"params": detector, "lr": 1e-4},
            {"params": backbone, "lr": 1e-5},
        ],
        lr=1e-4,
        weight_decay=1e-4,
    )


def build_scheduler(
    optimizer: torch.optim.Optimizer,
) -> torch.optim.lr_scheduler.LambdaLR:
    """Create a serializable scheduler state for the one-step feasibility seam."""
    return torch.optim.lr_scheduler.LambdaLR(optimizer, _constant_lr)


def trainable_parameter_sha256(model: torch.nn.Module) -> str:
    """Hash ordered trainable parameter names and values, excluding model buffers."""
    named_parameters = tuple(
        (name, parameter.detach())
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    )
    if not named_parameters:
        raise FeasibilityError("model has no trainable parameters")
    return structured_state_sha256(named_parameters)


def _verify_cpu_checkpoint_model_state(
    live_model_digest: str, checkpoint_model_digest: str
) -> None:
    if checkpoint_model_digest != live_model_digest:
        raise FeasibilityError("CPU checkpoint model state mismatch")


def _capture_checkpoint_model_state(
    model: torch.nn.Module,
) -> tuple[Mapping[str, Any], str]:
    live_model_digest = structured_state_sha256(model.state_dict())
    checkpoint_model_state = _state_to_cpu(model.state_dict())
    if not isinstance(checkpoint_model_state, Mapping):
        raise FeasibilityError("CPU checkpoint model state mismatch")
    _verify_cpu_checkpoint_model_state(
        live_model_digest, structured_state_sha256(checkpoint_model_state)
    )
    return checkpoint_model_state, live_model_digest


def run_one_step_smoke(
    model: torch.nn.Module, batch: Mapping[str, Any], seed: int
) -> StepObservation:
    """Run exactly one BF16 forward/backward/clipped AdamW update on CUDA."""
    determinism = configure_determinism(seed)
    parameters = [
        parameter for parameter in model.parameters() if parameter.requires_grad
    ]
    if not parameters:
        raise FeasibilityError("model has no trainable parameters")
    devices = {parameter.device for parameter in parameters}
    if len(devices) != 1:
        raise FeasibilityError("model parameters span multiple devices")
    device = next(iter(devices))
    if device.type != "cuda":
        raise FeasibilityError(
            "canonical training feasibility requires CUDA; no CPU fallback"
        )
    if not determinism.bf16_supported:
        raise FeasibilityError("BF16 is unsupported on the selected CUDA device")

    item_ids = batch.get("_val_item_ids")
    input_digests = batch.get("_val_input_digests")
    if (
        not isinstance(item_ids, (list, tuple))
        or len(item_ids) != 2
        or any(not isinstance(item, str) for item in item_ids)
    ):
        raise FeasibilityError("synthetic batch requires exactly two ordered item IDs")
    if not isinstance(input_digests, Mapping):
        raise FeasibilityError("training input digests are required")
    model_batch = {
        name: value for name, value in batch.items() if not name.startswith("_val_")
    }
    pixel_values = model_batch.get("pixel_values")
    pixel_mask = model_batch.get("pixel_mask")
    labels = model_batch.get("labels")
    if not isinstance(pixel_values, torch.Tensor) or list(pixel_values.shape) != [
        2,
        3,
        640,
        640,
    ]:
        raise FeasibilityError("synthetic pixel_values shape mismatch")
    if not isinstance(pixel_mask, torch.Tensor) or list(pixel_mask.shape) != [
        2,
        640,
        640,
    ]:
        raise FeasibilityError("synthetic pixel_mask shape mismatch")
    if not isinstance(labels, list) or len(labels) != 2:
        raise FeasibilityError("synthetic labels are required for both images")

    optimizer = build_optimizer(model)
    scheduler = build_scheduler(optimizer)
    sampler_digest = hashlib.sha256(
        json.dumps(list(item_ids), separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    model.train()
    optimizer.zero_grad(set_to_none=True)
    parameter_digest_before = trainable_parameter_sha256(model)

    torch.cuda.reset_peak_memory_stats(device)
    torch.cuda.synchronize(device)
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    wall_start = time.perf_counter()
    fallback_detected = False
    autocast_observed = False
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        start_event.record()
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            autocast_observed = bool(torch.is_autocast_enabled("cuda"))
            outputs = model(**model_batch)
            loss = getattr(outputs, "loss", None)
        if not isinstance(loss, torch.Tensor) or loss.numel() != 1:
            raise FeasibilityError("model did not return a scalar training loss")
        finite_loss = bool(torch.isfinite(loss.detach()).all())
        if not finite_loss:
            raise FeasibilityError("non-finite loss")
        loss.backward()
        gradients = [
            parameter.grad for parameter in parameters if parameter.grad is not None
        ]
        finite_gradients = bool(gradients) and all(
            bool(torch.isfinite(gradient).all()) for gradient in gradients
        )
        if not finite_gradients:
            raise FeasibilityError("non-finite gradients")
        gradient_norm_tensor = torch.nn.utils.clip_grad_norm_(parameters, max_norm=0.1)
        gradient_norm = float(gradient_norm_tensor.detach().float().cpu())
        if not math.isfinite(gradient_norm):
            raise FeasibilityError("non-finite gradient norm")
        optimizer.step()
        scheduler.step()
        end_event.record()
        torch.cuda.synchronize(device)
        fallback_detected = any(
            "determin" in str(item.message).lower() for item in caught
        )
    wall_seconds = time.perf_counter() - wall_start
    gpu_seconds = float(start_event.elapsed_time(end_event)) / 1000.0
    loss_value = float(loss.detach().float().cpu())
    parameter_digest_after = trainable_parameter_sha256(model)
    (
        checkpoint_model_state,
        live_model_state_digest_after,
    ) = _capture_checkpoint_model_state(model)
    state = CheckpointState(
        model_state=checkpoint_model_state,
        optimizer_state=_state_to_cpu(optimizer.state_dict()),
        scheduler_state=_state_to_cpu(scheduler.state_dict()),
        scaler_state=None,
        epoch=0,
        step=1,
        sampler_order_digest=sampler_digest,
        rng_state=capture_rng_state(),
        input_digests={str(name): str(value) for name, value in input_digests.items()},
    )
    digests = checkpoint_state_digests(state)
    observation = StepObservation(
        ordered_losses=(loss_value,),
        finite_loss=finite_loss,
        finite_gradients=finite_gradients,
        parameter_changed=parameter_digest_before != parameter_digest_after,
        gradient_norm=gradient_norm,
        peak_allocated_bytes=int(torch.cuda.max_memory_allocated(device)),
        peak_reserved_bytes=int(torch.cuda.max_memory_reserved(device)),
        wall_seconds=wall_seconds,
        gpu_seconds=gpu_seconds,
        cuda_matmul_allow_tf32=bool(torch.backends.cuda.matmul.allow_tf32),
        cudnn_allow_tf32=bool(torch.backends.cudnn.allow_tf32),
        cudnn_benchmark=bool(torch.backends.cudnn.benchmark),
        deterministic_algorithms=bool(torch.are_deterministic_algorithms_enabled()),
        deterministic_debug_mode=int(torch.get_deterministic_debug_mode()),
        cublas_workspace_config=os.environ.get("CUBLAS_WORKSPACE_CONFIG", ""),
        bf16_supported=bool(torch.cuda.is_bf16_supported()),
        bf16_autocast_enabled=autocast_observed,
        deterministic_fallback_detected=fallback_detected,
        device=str(device),
        live_model_state_digest_after=live_model_state_digest_after,
        trainable_parameter_count=len(parameters),
        parameter_digest_before=parameter_digest_before,
        parameter_digest_after=parameter_digest_after,
        state_digests=digests,
        checkpoint_state=state,
    )
    evaluate_step_observation(observation)
    return observation


def evaluate_step_observation(observation: StepObservation) -> StepObservation:
    """Apply every normative stop condition without fallback or masking."""
    failures = (
        (
            not observation.finite_loss
            or not all(math.isfinite(item) for item in observation.ordered_losses),
            "non-finite loss",
        ),
        (not observation.finite_gradients, "non-finite gradients"),
        (
            observation.deterministic_fallback_detected,
            "deterministic fallback detected",
        ),
        (
            observation.cuda_matmul_allow_tf32 or observation.cudnn_allow_tf32,
            "TF32 is enabled",
        ),
        (observation.cudnn_benchmark, "cuDNN benchmark is enabled"),
        (
            not observation.deterministic_algorithms,
            "deterministic algorithms are disabled",
        ),
        (
            observation.deterministic_debug_mode != 2,
            "deterministic error mode is disabled",
        ),
        (
            observation.cublas_workspace_config != _CUBLAS_WORKSPACE_CONFIG,
            "deterministic CUBLAS workspace is not configured",
        ),
        (not observation.bf16_supported, "BF16 is unsupported"),
        (not observation.bf16_autocast_enabled, "BF16 autocast was not observed"),
        (
            not _parameter_update_observed(observation),
            "parameter update was not observed",
        ),
        (
            observation.peak_allocated_bytes > VRAM_LIMIT_BYTES,
            "peak allocated VRAM exceeds 22 GiB",
        ),
    )
    for failed, message in failures:
        if failed:
            raise FeasibilityError(message)
    return observation


def _parameter_update_observed(observation: StepObservation) -> bool:
    return (
        observation.parameter_changed is True
        and observation.trainable_parameter_count > 0
        and observation.parameter_digest_before != observation.parameter_digest_after
    )


def deterministic_comparison(observation: StepObservation) -> dict[str, object]:
    """Build the exact cross-run comparison, excluding timing and allocator jitter."""
    ordered_loss_hex = [value.hex() for value in observation.ordered_losses]
    state_digests = {
        name: str(observation.state_digests[name]) for name in _STATE_DIGEST_KEYS
    }
    preimage = {
        "ordered_loss_hex": ordered_loss_hex,
        "state_digests": state_digests,
    }
    return {
        "rule": "float-hex-and-state-digests-sha256-v1",
        **preimage,
        "sha256": canonical_json_sha256(preimage),
    }


def resolve_cli_paths(
    model_contract: Path, checkpoint_root: Path, output: Path
) -> tuple[Path, Path, Path]:
    """Resolve only the approved external Task 5 input/output locations."""
    try:
        root = _artifact_root()
    except ValueError as error:
        raise FeasibilityError(str(error)) from error
    wave_root = _required_child_directory(root, "wave0")
    receipts_root = _required_child_directory(wave_root, "receipts")
    checkpoints_root = _required_child_directory(wave_root, "checkpoints")
    actual_model_contract = Path(model_contract).resolve(strict=True)
    actual_checkpoint_root = Path(checkpoint_root).resolve(strict=False)
    actual_output = Path(output).resolve(strict=False)
    if actual_model_contract.parent != receipts_root or _path_has_link(
        Path(model_contract), receipts_root
    ):
        raise FeasibilityError(
            "model-contract must be a non-link receipt directly below "
            "VAL_ARTIFACT_ROOT/wave0/receipts"
        )
    if actual_checkpoint_root.parent != checkpoints_root or _path_has_link(
        Path(checkpoint_root), checkpoints_root
    ):
        raise FeasibilityError(
            "checkpoint-root must be directly below VAL_ARTIFACT_ROOT/wave0/checkpoints"
        )
    if actual_output.parent != receipts_root or _path_has_link(
        Path(output), receipts_root
    ):
        raise FeasibilityError(
            "output must be directly below VAL_ARTIFACT_ROOT/wave0/receipts"
        )
    return actual_model_contract, actual_checkpoint_root, actual_output


def _prepare_labeled_batch(
    device: torch.device, model_contract_digest: str
) -> tuple[Mapping[str, Any], Mapping[str, list[int]], Mapping[str, object]]:
    fixture = load_synthetic_contract_fixture(_FIXTURE_MANIFEST)
    entries = fixture.manifest["images"]
    assert isinstance(entries, list)
    processor = build_contract_processor()
    encoded = processor(
        images=fixture.images,
        annotations=fixture.annotations,
        return_tensors="pt",
    )
    batch = {
        name: _move_to_device(value, device) for name, value in dict(encoded).items()
    }
    batch["_val_item_ids"] = [str(item["id"]) for item in entries]
    batch["_val_input_digests"] = {"model_contract_receipt": model_contract_digest}
    shapes = {
        "pixel_values": list(encoded["pixel_values"].shape),
        "pixel_mask": list(encoded["pixel_mask"].shape),
    }
    encoded_labels = encoded["labels"]
    label_evidence = {
        "item_ids": [str(item["id"]) for item in entries],
        "class_labels": [label["class_labels"].tolist() for label in encoded_labels],
        "boxes_per_image": [int(label["boxes"].shape[0]) for label in encoded_labels],
        "source": "tracked-synthetic-fixture-geometry-v1",
    }
    return batch, shapes, label_evidence


def _build_receipt(
    *,
    model_contract: Mapping[str, Any],
    model_contract_digest: str,
    checkpoint_digest: str,
    checkpoint_evidence: Mapping[str, object],
    observation: StepObservation,
    shapes: Mapping[str, list[int]],
    synthetic_labels: Mapping[str, object],
    checkpoint_write_seconds: float,
    checkpoint_load_seconds: float,
    resume_verified: bool,
    run_id: str,
    live_environment: Mapping[str, object],
) -> dict[str, object]:
    normative_contract = _mapping(model_contract.get("normative"), "model contract")
    state = observation.checkpoint_state
    if state is None:
        raise FeasibilityError("checkpoint state was not captured")
    runtime = {
        "seed": SEED,
        "device": observation.device,
        "precision": "bfloat16",
        "tf32": observation.cuda_matmul_allow_tf32 or observation.cudnn_allow_tf32,
        "cuda_matmul_allow_tf32": observation.cuda_matmul_allow_tf32,
        "cudnn_allow_tf32": observation.cudnn_allow_tf32,
        "cudnn_benchmark": observation.cudnn_benchmark,
        "deterministic_algorithms": observation.deterministic_algorithms,
        "deterministic_debug_mode": observation.deterministic_debug_mode,
        "cublas_workspace_config": observation.cublas_workspace_config,
        "bf16_supported": observation.bf16_supported,
        "bf16_autocast_enabled": observation.bf16_autocast_enabled,
        "deterministic_fallback_detected": observation.deterministic_fallback_detected,
    }
    recipe = {
        "seed": SEED,
        "batch_size": 2,
        "optimizer": "AdamW",
        "detector_learning_rate": 1e-4,
        "backbone_learning_rate": 1e-5,
        "weight_decay": 1e-4,
        "gradient_clip_norm": 0.1,
        "fixture_set": "wave0-rtdetr-contract",
    }
    expected_state_sha256 = checkpoint_state_sha256(state)
    checkpoint_content_verified = (
        checkpoint_evidence.get("file_sha256") == checkpoint_digest
        and checkpoint_evidence.get("verified_file_sha256") == checkpoint_digest
        and checkpoint_evidence.get("input_digests_verified") is True
    )
    checkpoint_round_trip = (
        checkpoint_evidence.get("state_sha256_before_save") == expected_state_sha256
        and checkpoint_evidence.get("state_sha256_after_load") == expected_state_sha256
        and checkpoint_evidence.get("live_model_state_sha256_after_step")
        == observation.live_model_state_digest_after
        and checkpoint_evidence.get("live_model_state_sha256_after_step")
        == observation.state_digests.get("model")
        and checkpoint_evidence.get("state_digests_before_save")
        == observation.state_digests
        and checkpoint_evidence.get("state_digests_after_load")
        == observation.state_digests
    )
    resume_state_verified = (
        resume_verified
        and checkpoint_evidence.get("state_digests_after_restore")
        == observation.state_digests
    )
    invariants = {
        "adamw_update": _parameter_update_observed(observation),
        "batch_size_two": shapes.get("pixel_values", [0])[0] == 2,
        "bf16_autocast": observation.bf16_autocast_enabled,
        "bf16_supported": observation.bf16_supported,
        "checkpoint_content_verified": checkpoint_content_verified,
        "checkpoint_round_trip": checkpoint_round_trip,
        "cublas_workspace_configured": observation.cublas_workspace_config
        == _CUBLAS_WORKSPACE_CONFIG,
        "cudnn_benchmark_disabled": not observation.cudnn_benchmark,
        "canonical_environment": True,
        "deterministic_algorithms": observation.deterministic_algorithms,
        "deterministic_fallback_absent": not observation.deterministic_fallback_detected,
        "exact_scipy": live_environment["observed"].get("scipy") == "1.18.0",
        "finite_gradients": observation.finite_gradients,
        "finite_loss": observation.finite_loss,
        "gradient_clip_0_1": recipe["gradient_clip_norm"] == 0.1,
        "parameter_changed": _parameter_update_observed(observation),
        "peak_allocated_vram_within_22_gib": observation.peak_allocated_bytes
        <= VRAM_LIMIT_BYTES,
        "resume_state_verified": resume_state_verified,
        "seed_17": SEED == 17,
        "synthetic_labels_only": True,
        "tf32_disabled": runtime["tf32"] is False,
    }
    errors = sorted(name for name, passed in invariants.items() if passed is not True)
    copied_hashes = {
        name: str(normative_contract[name])
        for name in (
            "model_sha256",
            "config_sha256",
            "source_sha256",
            "processor_sha256",
            "fixture_sha256",
            "loss_source_sha256",
            "synthetic_target_sha256",
        )
    }
    normative = {
        **copied_hashes,
        "environment_sha256": canonical_json_sha256(dict(live_environment)),
        "parent_environment_sha256": str(live_environment["parent_environment_sha256"]),
        "environment": dict(live_environment),
        "probe_sha256": _probe_hash(),
        "model_contract_receipt_sha256": model_contract_digest,
        "parent_model_contract": copy.deepcopy(dict(model_contract)),
        "checkpoint_sha256": checkpoint_digest,
        "checkpoint_state_sha256": expected_state_sha256,
        "observed_shapes": {name: list(value) for name, value in shapes.items()},
        "invariants": dict(sorted(invariants.items())),
        "ordered_losses": list(observation.ordered_losses),
        "state_digests": dict(observation.state_digests),
        "comparison": deterministic_comparison(observation),
        "step": {
            "loss_hex": observation.ordered_losses[0].hex(),
            "gradient_norm": observation.gradient_norm,
            "finite_loss": observation.finite_loss,
            "finite_gradients": observation.finite_gradients,
            "parameter_digest_rule": _PARAMETER_DIGEST_RULE,
            "trainable_parameter_count": observation.trainable_parameter_count,
            "parameter_digest_before": observation.parameter_digest_before,
            "parameter_digest_after": observation.parameter_digest_after,
        },
        "checkpoint": dict(checkpoint_evidence),
        "synthetic_labels": dict(synthetic_labels),
        "runtime": runtime,
        "recipe": recipe,
        "timing": {
            "wall_seconds": observation.wall_seconds,
            "gpu_seconds": observation.gpu_seconds,
            "checkpoint_write_seconds": checkpoint_write_seconds,
            "checkpoint_load_seconds": checkpoint_load_seconds,
        },
        "vram": {
            "peak_allocated_bytes": observation.peak_allocated_bytes,
            "peak_reserved_bytes": observation.peak_reserved_bytes,
            "allocated_limit_bytes": VRAM_LIMIT_BYTES,
        },
        "resume_verified": resume_verified,
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }
    return {
        "receipt_type": "feasibility",
        "schema_version": 1,
        "normative": normative,
        "metadata": {"timestamp": datetime.now(UTC).isoformat(), "run_id": run_id},
    }


def _execute_probe(
    model_contract_path: Path,
    checkpoint_root: Path,
    output_path: Path,
    run_id: str,
) -> dict[str, object]:
    model_contract = _mapping(
        json.loads(model_contract_path.read_text(encoding="utf-8")), "model contract"
    )
    validate_receipt_for_run(
        model_contract,
        _project_root() / "schemas" / "model-contract-receipt.schema.json",
        run_id,
    )
    normative = _mapping(model_contract.get("normative"), "model contract normative")
    if normative.get("status") != "PASS":
        raise FeasibilityError("model-contract receipt must be PASS")
    parent_environment = _mapping(
        normative.get("environment"), "model-contract environment"
    )
    model_contract_digest = sha256_file(model_contract_path)
    spec = load_pinned_asset_specs(
        _project_root() / "configs" / "models" / "pinned-models.yaml"
    )["rtdetr"]
    root = _artifact_root()
    snapshot = _snapshot_root(root, spec)
    verified_asset = verify_snapshot(spec, snapshot)
    verify_transformers_source(spec)
    if verified_asset.files["model.safetensors"].sha256 != normative.get(
        "model_sha256"
    ):
        raise FeasibilityError("live RT-DETR asset differs from model-contract receipt")

    determinism = configure_determinism(SEED)
    if not torch.cuda.is_available():
        raise FeasibilityError("canonical training feasibility requires CUDA")
    if not determinism.bf16_supported:
        raise FeasibilityError("BF16 is unsupported on the selected CUDA device")
    device = torch.device("cuda", torch.cuda.current_device())
    if torch.cuda.get_device_name(device) != "NVIDIA GeForce RTX 4090":
        raise FeasibilityError("canonical training feasibility requires RTX 4090")
    live_environment = _observe_live_environment(parent_environment)

    model = RTDetrForObjectDetection.from_pretrained(
        snapshot,
        local_files_only=True,
        use_safetensors=True,
    )
    reset_four_class_head(model, seed=SEED)
    model.to(device)
    batch, shapes, synthetic_labels = _prepare_labeled_batch(
        device, model_contract_digest
    )
    try:
        observation = run_one_step_smoke(model, batch, seed=SEED)
        evaluate_step_observation(observation)
        state = observation.checkpoint_state
        if state is None:
            raise FeasibilityError("checkpoint state was not captured")
        checkpoint_root.mkdir(parents=True, exist_ok=True)
        checkpoint_target = checkpoint_root / "step-000001.pt"
        state_sha256_before_save = checkpoint_state_sha256(state)
        state_digests_before_save = checkpoint_state_digests(state)
        checkpoint_write_start = time.perf_counter()
        checkpoint_digest = save_checkpoint_atomic(state, checkpoint_target)
        checkpoint_write_seconds = time.perf_counter() - checkpoint_write_start
        checkpoint_load_start = time.perf_counter()
        loaded = load_checkpoint_verified(
            checkpoint_target,
            checkpoint_digest,
            expected_input_digests=state.input_digests,
        )
        checkpoint_load_seconds = time.perf_counter() - checkpoint_load_start
        state_sha256_after_load = checkpoint_state_sha256(loaded)
        state_digests_after_load = checkpoint_state_digests(loaded)
        if state_digests_after_load != observation.state_digests:
            raise FeasibilityError("checkpoint round-trip state mismatch")

        with torch.no_grad():
            next(model.parameters()).zero_()
        resume_optimizer = build_optimizer(model)
        resume_scheduler = build_scheduler(resume_optimizer)
        restored = restore_checkpoint_state(
            loaded,
            model=model,
            optimizer=resume_optimizer,
            scheduler=resume_scheduler,
            scaler=None,
            expected_input_digests=state.input_digests,
        )
        resume_verified = restored == observation.state_digests
        if not resume_verified:
            raise FeasibilityError("restored state mismatch")
        checkpoint_evidence = {
            "file_sha256": checkpoint_digest,
            "verified_file_sha256": sha256_file(checkpoint_target),
            "live_model_state_sha256_after_step": observation.live_model_state_digest_after,
            "state_sha256_before_save": state_sha256_before_save,
            "state_sha256_after_load": state_sha256_after_load,
            "state_digests_before_save": state_digests_before_save,
            "state_digests_after_load": state_digests_after_load,
            "state_digests_after_restore": restored,
            "input_digests_verified": loaded.input_digests == state.input_digests,
        }
        return _build_receipt(
            model_contract=model_contract,
            model_contract_digest=model_contract_digest,
            checkpoint_digest=checkpoint_digest,
            checkpoint_evidence=checkpoint_evidence,
            observation=observation,
            shapes=shapes,
            synthetic_labels=synthetic_labels,
            checkpoint_write_seconds=checkpoint_write_seconds,
            checkpoint_load_seconds=checkpoint_load_seconds,
            resume_verified=resume_verified,
            run_id=run_id,
            live_environment=live_environment,
        )
    finally:
        del batch
        del model


@command("probe training-feasibility")
def main(argv: Sequence[str] | None = None) -> int:
    """Run the canonical offline deterministic BF16 feasibility smoke."""
    parser = argparse.ArgumentParser(prog="val probe training-feasibility")
    parser.add_argument("--model-contract", type=Path, required=True)
    parser.add_argument("--checkpoint-root", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        if not arguments.run_id.strip():
            raise FeasibilityError("run_id must be non-empty")
        model_contract, checkpoint_root, output = resolve_cli_paths(
            arguments.model_contract,
            arguments.checkpoint_root,
            arguments.output,
        )
        if output.exists():
            raise FeasibilityError(
                "fresh output path is required for each feasibility attempt"
            )
        receipt = _execute_probe(
            model_contract, checkpoint_root, output, arguments.run_id
        )
        atomic_write_receipt(output, receipt)
    except (
        CheckpointVerificationError,
        FeasibilityError,
        ImportError,
        OSError,
        RuntimeError,
        ValueError,
    ) as error:
        if (
            isinstance(error, torch.OutOfMemoryError)
            or "out of memory" in str(error).lower()
        ):
            print(f"OOM: {error}", file=sys.stderr)
        else:
            print(error, file=sys.stderr)
        return 2
    print(receipt["normative"]["status"])
    return 0 if receipt["normative"]["status"] == "PASS" else 2


def _constant_lr(_: int) -> float:
    return 1.0


def _state_to_cpu(value: object) -> Any:
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().clone()
    if isinstance(value, Mapping):
        return {key: _state_to_cpu(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_state_to_cpu(item) for item in value)
    if isinstance(value, list):
        return [_state_to_cpu(item) for item in value]
    return copy.deepcopy(value)


def _move_to_device(value: object, device: torch.device) -> Any:
    if isinstance(value, torch.Tensor):
        return value.to(device)
    if isinstance(value, Mapping):
        return {name: _move_to_device(item, device) for name, item in value.items()}
    if isinstance(value, list):
        return [_move_to_device(item, device) for item in value]
    if isinstance(value, tuple):
        return tuple(_move_to_device(item, device) for item in value)
    return value


def _canonical_source_sha256(path: Path) -> str:
    normalized = Path(path).read_text(encoding="utf-8")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _probe_hash() -> str:
    source_files = (
        Path(__file__).resolve(),
        Path(inspect.getfile(save_checkpoint_atomic)).resolve(),
    )
    observations = {
        str(path.relative_to(_project_root())).replace("\\", "/"): (
            _canonical_source_sha256(path)
        )
        for path in source_files
    }
    return canonical_json_sha256(observations)


def _path_has_link(path: Path, boundary: Path) -> bool:
    candidate = Path(path)
    while True:
        if candidate.exists() and _is_link_or_junction(candidate):
            return True
        if candidate.resolve(strict=False) == boundary:
            return False
        if candidate.parent == candidate:
            return True
        candidate = candidate.parent
