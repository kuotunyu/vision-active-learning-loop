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
import re
import sys
import time
import warnings
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import torch
import transformers
from torch.nn.attention import SDPBackend, sdpa_kernel
from transformers import RTDetrForObjectDetection
from transformers.integrations import sdpa_attention as transformers_sdpa_attention

from ..artifacts.digests import canonical_json_sha256, sha256_file
from ..artifacts.no_clobber import create_directory_no_clobber
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
_ALLOWLISTED_BACKWARD_OPERATION = "grid_sampler_2d_backward_cuda"
_ALLOWLISTED_BACKWARD_SOURCE_HASH_RULE = "python-source-lf-normalized-sha256-v1"
_ALLOWLISTED_BACKWARD_SOURCE_SHA256 = {
    "torch_init": "d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49",
    "torch_nn_functional": "27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19",
    "transformers_modeling_rt_detr": (
        "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3"
    ),
}
_DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE = "python-source-lf-normalized-sha256-v1"
_DETERMINISTIC_ATTENTION_SOURCE_SHA256 = {
    "torch_nn_attention": (
        "56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0"
    ),
    "transformers_sdpa_attention": (
        "d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098"
    ),
}
_DETERMINISTIC_ATTENTION_BEFORE = {
    "cudnn": True,
    "flash": True,
    "math": True,
    "memory_efficient": True,
}
_DETERMINISTIC_ATTENTION_INSIDE = {
    "cudnn": False,
    "flash": False,
    "math": True,
    "memory_efficient": False,
}
_DETERMINISTIC_WARNING_PATTERN = re.compile(
    r"^([A-Za-z0-9_]+) does not have a deterministic implementation(?:[,.]|$)"
)
_WARNING_CONTRACT_DIAGNOSTIC_PREFIX = (
    "deterministic backward warning contract failure; diagnostic="
)
_WARNING_CONTRACT_DIAGNOSTIC_REASONS = frozenset(
    {
        "unparsable_message",
        "unexpected_category",
        "count_mismatch",
        "unexpected_operation",
    }
)
_FIXTURE_MANIFEST = (
    _project_root() / "fixtures" / "synthetic" / "wave0" / "fixture-manifest.json"
)
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
class DeterministicAttentionEvidence:
    attn_implementation: str
    backend: str
    scope: str
    before: Mapping[str, bool]
    inside: Mapping[str, bool]
    after: Mapping[str, bool]
    restored: bool
    source_hash_rule: str
    source_sha256: Mapping[str, str]


@dataclass(frozen=True)
class BackwardWarningEvidence:
    operation_identifier: str
    expected_count: int
    observed_count: int
    raw_warnings: tuple[str, ...]
    warning_categories: tuple[str, ...]
    operation_identifiers: tuple[str, ...]
    source_hash_rule: str
    source_sha256: Mapping[str, str]
    strict_mode_restored: bool


@dataclass(frozen=True)
class ParameterBaseline:
    inventory: tuple[Mapping[str, object], ...]
    values: tuple[torch.Tensor, ...]


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
    allowlisted_backward: BackwardWarningEvidence
    deterministic_attention: DeterministicAttentionEvidence
    device: str
    live_model_state_digest_after: str
    trainable_parameter_count: int
    parameter_digest_before: str
    parameter_digest_after: str
    parameter_inventory: tuple[Mapping[str, object], ...]
    update_groups: Mapping[str, float]
    optimizer_groups: tuple[Mapping[str, object], ...]
    scheduler_state_before_sha256: str
    sampler_order_digest: str
    input_digests: Mapping[str, str]
    semantic_input_digests: Mapping[str, str]
    checkpoint_epoch: int
    checkpoint_step: int
    model_state_inventory: tuple[Mapping[str, object], ...]
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


def _allowlisted_backward_source_paths() -> Mapping[str, Path]:
    transformers_source = inspect.getsourcefile(RTDetrForObjectDetection)
    if transformers_source is None:
        raise FeasibilityError("pinned Transformers RT-DETR source is unavailable")
    torch_init = getattr(torch, "__file__", None)
    torch_functional = getattr(torch.nn.functional, "__file__", None)
    if not isinstance(torch_init, str) or not isinstance(torch_functional, str):
        raise FeasibilityError("pinned PyTorch source is unavailable")
    return {
        "torch_init": Path(torch_init),
        "torch_nn_functional": Path(torch_functional),
        "transformers_modeling_rt_detr": Path(transformers_source),
    }


def _canonical_python_source_sha256(path: Path) -> str:
    raw = path.read_bytes()
    canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(canonical).hexdigest()


def _deterministic_attention_source_locations() -> Mapping[str, tuple[Path, Path]]:
    torch_source = inspect.getsourcefile(torch.nn.attention)
    transformers_source = inspect.getsourcefile(transformers_sdpa_attention)
    torch_package = getattr(torch, "__file__", None)
    transformers_package = getattr(transformers, "__file__", None)
    if not isinstance(torch_source, str) or not isinstance(torch_package, str):
        raise FeasibilityError("pinned PyTorch attention source is unavailable")
    if not isinstance(transformers_source, str) or not isinstance(
        transformers_package, str
    ):
        raise FeasibilityError("pinned Transformers SDPA source is unavailable")
    return {
        "torch_nn_attention": (Path(torch_source), Path(torch_package).parent),
        "transformers_sdpa_attention": (
            Path(transformers_source),
            Path(transformers_package).parent,
        ),
    }


def _verify_deterministic_attention_sources() -> dict[str, str]:
    observed: dict[str, str] = {}
    locations = _deterministic_attention_source_locations()
    if set(locations) != set(_DETERMINISTIC_ATTENTION_SOURCE_SHA256):
        raise FeasibilityError("deterministic-attention source inventory mismatch")
    for name in sorted(locations):
        path, boundary = locations[name]
        try:
            path.relative_to(boundary)
        except ValueError as error:
            raise FeasibilityError(
                f"deterministic-attention source path mismatch: {name}"
            ) from error
        if not path.is_file():
            raise FeasibilityError(
                f"deterministic-attention source is not a regular file: {name}"
            )
        if _path_has_link(path, boundary):
            raise FeasibilityError(
                f"deterministic-attention source has a link or junction: {name}"
            )
        raw = path.read_bytes()
        try:
            raw.decode("utf-8")
        except UnicodeDecodeError as error:
            raise FeasibilityError(
                f"deterministic-attention source is not UTF-8: {name}"
            ) from error
        canonical = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        digest = hashlib.sha256(canonical).hexdigest()
        if digest != _DETERMINISTIC_ATTENTION_SOURCE_SHA256[name]:
            raise FeasibilityError(
                f"deterministic-attention source hash mismatch: {name}"
            )
        observed[name] = digest
    return observed


def _sdpa_backend_state() -> dict[str, bool]:
    return {
        "cudnn": bool(torch.backends.cuda.cudnn_sdp_enabled()),
        "flash": bool(torch.backends.cuda.flash_sdp_enabled()),
        "math": bool(torch.backends.cuda.math_sdp_enabled()),
        "memory_efficient": bool(torch.backends.cuda.mem_efficient_sdp_enabled()),
    }


def _verify_allowlisted_backward_sources() -> dict[str, str]:
    observed: dict[str, str] = {}
    paths = _allowlisted_backward_source_paths()
    if set(paths) != set(_ALLOWLISTED_BACKWARD_SOURCE_SHA256):
        raise FeasibilityError("bounded-backward source inventory mismatch")
    for name in sorted(paths):
        path = paths[name]
        if not path.is_file() or _is_link_or_junction(path):
            raise FeasibilityError(
                f"bounded-backward source is not a regular file: {name}"
            )
        digest = _canonical_python_source_sha256(path)
        if digest != _ALLOWLISTED_BACKWARD_SOURCE_SHA256[name]:
            raise FeasibilityError(f"bounded-backward source hash mismatch: {name}")
        observed[name] = digest
    return observed


def _warning_contract_error(
    reason: str,
    raw_warnings: tuple[str, ...],
    warning_categories: tuple[str, ...],
) -> FeasibilityError:
    if reason not in _WARNING_CONTRACT_DIAGNOSTIC_REASONS:
        raise ValueError("unknown warning diagnostic reason")
    warning_inventory = [
        {"category": category, "index": index, "message": message}
        for index, (message, category) in enumerate(
            zip(raw_warnings, warning_categories, strict=True)
        )
    ]
    diagnostic = {
        "reason": reason,
        "schema_version": 1,
        "warnings": warning_inventory,
    }
    encoded = json.dumps(
        diagnostic, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    return FeasibilityError(_WARNING_CONTRACT_DIAGNOSTIC_PREFIX + encoded)


def run_allowlisted_backward(
    backward: Callable[[], None], *, expected_count: int
) -> BackwardWarningEvidence:
    """Run only backward in deterministic warn mode and verify its exact warnings."""
    if not callable(backward):
        raise FeasibilityError("backward must be callable")
    if type(expected_count) is not int or expected_count <= 0:
        raise FeasibilityError("expected backward warning count must be positive")
    if (
        not torch.are_deterministic_algorithms_enabled()
        or torch.is_deterministic_algorithms_warn_only_enabled()
        or torch.get_deterministic_debug_mode() != 2
    ):
        raise FeasibilityError("strict deterministic error mode is required")
    source_sha256 = _verify_allowlisted_backward_sources()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            torch.use_deterministic_algorithms(True, warn_only=True)
            torch.set_deterministic_debug_mode("warn")
            backward()
        finally:
            torch.use_deterministic_algorithms(True, warn_only=False)
            torch.set_deterministic_debug_mode("error")
    raw_warnings = tuple(str(item.message) for item in caught)
    warning_categories = tuple(item.category.__name__ for item in caught)
    identifiers: list[str] = []
    for message, category in zip(raw_warnings, warning_categories, strict=True):
        match = _DETERMINISTIC_WARNING_PATTERN.match(message)
        if match is None:
            raise _warning_contract_error(
                "unparsable_message", raw_warnings, warning_categories
            )
        if category != "UserWarning":
            raise _warning_contract_error(
                "unexpected_category", raw_warnings, warning_categories
            )
        identifiers.append(match.group(1))
    operation_identifiers = tuple(identifiers)
    if len(operation_identifiers) != expected_count:
        raise _warning_contract_error(
            "count_mismatch", raw_warnings, warning_categories
        )
    if any(
        identifier != _ALLOWLISTED_BACKWARD_OPERATION
        for identifier in operation_identifiers
    ):
        raise _warning_contract_error(
            "unexpected_operation", raw_warnings, warning_categories
        )
    return BackwardWarningEvidence(
        operation_identifier=_ALLOWLISTED_BACKWARD_OPERATION,
        expected_count=expected_count,
        observed_count=len(operation_identifiers),
        raw_warnings=raw_warnings,
        warning_categories=warning_categories,
        operation_identifiers=operation_identifiers,
        source_hash_rule=_ALLOWLISTED_BACKWARD_SOURCE_HASH_RULE,
        source_sha256=source_sha256,
        strict_mode_restored=(
            torch.are_deterministic_algorithms_enabled()
            and not torch.is_deterministic_algorithms_warn_only_enabled()
            and torch.get_deterministic_debug_mode() == 2
        ),
    )


def run_math_only_labeled_forward_backward(
    model: object,
    labeled_forward: Callable[[], tuple[torch.Tensor, bool]],
    *,
    expected_warning_count: int,
) -> tuple[
    torch.Tensor,
    bool,
    BackwardWarningEvidence,
    DeterministicAttentionEvidence,
]:
    """Run the labeled forward/backward boundary with only public SDPA Math."""
    if not callable(labeled_forward):
        raise FeasibilityError("labeled forward must be callable")
    if type(expected_warning_count) is not int or expected_warning_count <= 0:
        raise FeasibilityError("expected backward warning count must be positive")
    source_sha256 = _verify_deterministic_attention_sources()
    config = getattr(model, "config", None)
    if getattr(config, "_attn_implementation", None) != "sdpa":
        raise FeasibilityError("deterministic attention requires sdpa")
    if (
        not torch.are_deterministic_algorithms_enabled()
        or torch.is_deterministic_algorithms_warn_only_enabled()
        or torch.get_deterministic_debug_mode() != 2
    ):
        raise FeasibilityError("strict deterministic error mode is required")
    before = _sdpa_backend_state()
    if before != _DETERMINISTIC_ATTENTION_BEFORE:
        raise FeasibilityError("deterministic attention entry backend mismatch")

    body_error: BaseException | None = None
    result: tuple[
        torch.Tensor,
        bool,
        BackwardWarningEvidence,
        dict[str, bool],
    ] | None = None
    try:
        with sdpa_kernel(SDPBackend.MATH):
            inside = _sdpa_backend_state()
            if inside != _DETERMINISTIC_ATTENTION_INSIDE:
                raise FeasibilityError(
                    "deterministic attention inside backend mismatch"
                )
            loss, autocast_observed = labeled_forward()
            if not isinstance(loss, torch.Tensor) or loss.numel() != 1:
                raise FeasibilityError("model did not return a scalar training loss")
            if not bool(torch.isfinite(loss.detach()).all()):
                raise FeasibilityError("non-finite loss")
            warning_evidence = run_allowlisted_backward(
                loss.backward, expected_count=expected_warning_count
            )
            result = (loss, autocast_observed, warning_evidence, inside)
    except BaseException as error:  # noqa: BLE001 - restoration covers every exit.
        body_error = error

    after = _sdpa_backend_state()
    strict_restored = (
        torch.are_deterministic_algorithms_enabled()
        and not torch.is_deterministic_algorithms_warn_only_enabled()
        and torch.get_deterministic_debug_mode() == 2
    )
    if after != before or not strict_restored:
        restoration = FeasibilityError(
            "deterministic attention backend restoration mismatch"
        )
        if body_error is not None:
            raise restoration from body_error
        raise restoration
    if body_error is not None:
        raise body_error.with_traceback(body_error.__traceback__)
    assert result is not None
    loss, autocast_observed, warning_evidence, inside = result
    evidence = DeterministicAttentionEvidence(
        attn_implementation="sdpa",
        backend="MATH",
        scope="labeled_forward_through_backward",
        before=before,
        inside=inside,
        after=after,
        restored=True,
        source_hash_rule=_DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE,
        source_sha256=source_sha256,
    )
    return loss, autocast_observed, warning_evidence, evidence


def _expected_grid_sample_warning_count(model: object) -> int:
    config = getattr(model, "config", None)
    decoder_layers = getattr(config, "decoder_layers", None)
    feature_levels = getattr(config, "num_feature_levels", None)
    if (
        type(decoder_layers) is not int
        or type(feature_levels) is not int
        or decoder_layers != 3
        or feature_levels != 3
    ):
        raise FeasibilityError(
            "pinned RT-DETR deformable-attention configuration mismatch"
        )
    return decoder_layers * feature_levels


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
            {"params": detector, "lr": 1e-4, "group_name": "detector"},
            {"params": backbone, "lr": 1e-5, "group_name": "backbone"},
        ],
        lr=1e-4,
        weight_decay=1e-4,
    )


def _parameter_group_name(name: str) -> str:
    return "backbone" if name.startswith("model.backbone") else "detector"


def _capture_parameter_baseline(model: torch.nn.Module) -> ParameterBaseline:
    inventory: list[Mapping[str, object]] = []
    values: list[torch.Tensor] = []
    groups: set[str] = set()
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        group_name = _parameter_group_name(name)
        groups.add(group_name)
        inventory.append(
            {
                "name": name,
                "group_name": group_name,
                "shape": list(parameter.shape),
                "dtype": str(parameter.dtype).removeprefix("torch."),
            }
        )
        values.append(parameter.detach().cpu().clone())
    if not inventory or groups != {"detector", "backbone"}:
        raise FeasibilityError("detector/backbone parameter inventory is incomplete")
    return ParameterBaseline(inventory=tuple(inventory), values=tuple(values))


def _measure_parameter_update_groups(
    model: torch.nn.Module, baseline: ParameterBaseline
) -> dict[str, float]:
    current = tuple(
        (name, parameter)
        for name, parameter in model.named_parameters()
        if parameter.requires_grad
    )
    if len(current) != len(baseline.inventory) or len(current) != len(baseline.values):
        raise FeasibilityError("trainable parameter inventory changed during update")
    squared = {"detector": 0.0, "backbone": 0.0}
    for (name, parameter), entry, before in zip(
        current, baseline.inventory, baseline.values, strict=True
    ):
        expected = {
            "name": name,
            "group_name": _parameter_group_name(name),
            "shape": list(parameter.shape),
            "dtype": str(parameter.dtype).removeprefix("torch."),
        }
        if dict(entry) != expected or list(before.shape) != list(parameter.shape):
            raise FeasibilityError(
                "trainable parameter inventory changed during update"
            )
        difference = parameter.detach().cpu().to(torch.float64) - before.to(
            torch.float64
        )
        if not bool(torch.isfinite(difference).all()):
            raise FeasibilityError("non-finite parameter update")
        squared[expected["group_name"]] += float(torch.sum(difference * difference))
    norms = {name: math.sqrt(value) for name, value in squared.items()}
    if any(not math.isfinite(value) or value <= 0.0 for value in norms.values()):
        raise FeasibilityError("zero or non-finite parameter update group")
    return norms


def _optimizer_group_evidence(
    optimizer: torch.optim.Optimizer,
) -> tuple[Mapping[str, object], ...]:
    evidence: list[Mapping[str, object]] = []
    for group in optimizer.param_groups:
        name = group.get("group_name")
        learning_rate = group.get("lr")
        weight_decay = group.get("weight_decay")
        if (
            name not in {"detector", "backbone"}
            or type(learning_rate) not in (int, float)
            or type(weight_decay) not in (int, float)
        ):
            raise FeasibilityError("optimizer parameter-group evidence is incomplete")
        evidence.append(
            {
                "group_name": str(name),
                "learning_rate": float(learning_rate),
                "weight_decay": float(weight_decay),
            }
        )
    expected = (
        {
            "group_name": "detector",
            "learning_rate": 1e-4,
            "weight_decay": 1e-4,
        },
        {
            "group_name": "backbone",
            "learning_rate": 1e-5,
            "weight_decay": 1e-4,
        },
    )
    if tuple(evidence) != expected:
        raise FeasibilityError("optimizer parameter-group evidence mismatch")
    return tuple(evidence)


def _model_state_inventory(
    model: torch.nn.Module,
) -> tuple[Mapping[str, object], ...]:
    trainable_names = {
        name for name, parameter in model.named_parameters() if parameter.requires_grad
    }
    inventory: list[Mapping[str, object]] = []
    for name, value in model.state_dict().items():
        if not isinstance(value, torch.Tensor):
            raise FeasibilityError("model state inventory contains a non-tensor")
        inventory.append(
            {
                "name": name,
                "shape": list(value.shape),
                "dtype": str(value.dtype).removeprefix("torch."),
                "trainable": name in trainable_names,
            }
        )
    if not inventory or not trainable_names:
        raise FeasibilityError("model state inventory is incomplete")
    return tuple(inventory)


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
    semantic_input_digests = batch.get("_val_semantic_input_digests")
    if (
        not isinstance(item_ids, (list, tuple))
        or len(item_ids) != 2
        or any(not isinstance(item, str) for item in item_ids)
    ):
        raise FeasibilityError("synthetic batch requires exactly two ordered item IDs")
    if not isinstance(input_digests, Mapping):
        raise FeasibilityError("training input digests are required")
    if not isinstance(semantic_input_digests, Mapping) or set(
        semantic_input_digests
    ) != {"fixture_sha256", "synthetic_target_sha256"}:
        raise FeasibilityError("semantic training input digests are required")
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
    optimizer_groups = _optimizer_group_evidence(optimizer)
    scheduler_state_before_sha256 = structured_state_sha256(scheduler.state_dict())
    sampler_digest = hashlib.sha256(
        json.dumps(list(item_ids), separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    model.train()
    optimizer.zero_grad(set_to_none=True)
    parameter_baseline = _capture_parameter_baseline(model)
    parameter_digest_before = trainable_parameter_sha256(model)

    torch.cuda.reset_peak_memory_stats(device)
    torch.cuda.synchronize(device)
    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)
    wall_start = time.perf_counter()
    start_event.record()

    def labeled_forward() -> tuple[torch.Tensor, bool]:
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            autocast_observed = bool(torch.is_autocast_enabled("cuda"))
            outputs = model(**model_batch)
            loss = getattr(outputs, "loss", None)
        return loss, autocast_observed

    (
        loss,
        autocast_observed,
        backward_evidence,
        deterministic_attention,
    ) = run_math_only_labeled_forward_backward(
        model,
        labeled_forward,
        expected_warning_count=_expected_grid_sample_warning_count(model),
    )
    finite_loss = True
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
    wall_seconds = time.perf_counter() - wall_start
    gpu_seconds = float(start_event.elapsed_time(end_event)) / 1000.0
    loss_value = float(loss.detach().float().cpu())
    parameter_digest_after = trainable_parameter_sha256(model)
    update_groups = _measure_parameter_update_groups(model, parameter_baseline)
    model_state_inventory = _model_state_inventory(model)
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
        semantic_input_digests={
            str(name): str(value) for name, value in semantic_input_digests.items()
        },
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
        allowlisted_backward=backward_evidence,
        deterministic_attention=deterministic_attention,
        device=str(device),
        live_model_state_digest_after=live_model_state_digest_after,
        trainable_parameter_count=len(parameters),
        parameter_digest_before=parameter_digest_before,
        parameter_digest_after=parameter_digest_after,
        parameter_inventory=parameter_baseline.inventory,
        update_groups=update_groups,
        optimizer_groups=optimizer_groups,
        scheduler_state_before_sha256=scheduler_state_before_sha256,
        sampler_order_digest=sampler_digest,
        input_digests={str(name): str(value) for name, value in input_digests.items()},
        semantic_input_digests={
            str(name): str(value) for name, value in semantic_input_digests.items()
        },
        checkpoint_epoch=0,
        checkpoint_step=1,
        model_state_inventory=model_state_inventory,
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
            not _allowlisted_backward_is_valid(observation.allowlisted_backward),
            "allowlisted backward evidence mismatch",
        ),
        (
            not _deterministic_attention_is_valid(observation.deterministic_attention),
            "deterministic attention evidence mismatch",
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


def _allowlisted_backward_is_valid(evidence: BackwardWarningEvidence) -> bool:
    return (
        evidence.operation_identifier == _ALLOWLISTED_BACKWARD_OPERATION
        and evidence.expected_count == 9
        and evidence.observed_count == 9
        and len(evidence.raw_warnings) == 9
        and evidence.warning_categories == ("UserWarning",) * 9
        and evidence.operation_identifiers == (_ALLOWLISTED_BACKWARD_OPERATION,) * 9
        and evidence.source_hash_rule == _ALLOWLISTED_BACKWARD_SOURCE_HASH_RULE
        and dict(evidence.source_sha256) == _ALLOWLISTED_BACKWARD_SOURCE_SHA256
        and evidence.strict_mode_restored is True
    )


def _deterministic_attention_is_valid(
    evidence: DeterministicAttentionEvidence,
) -> bool:
    return (
        evidence.attn_implementation == "sdpa"
        and evidence.backend == "MATH"
        and evidence.scope == "labeled_forward_through_backward"
        and dict(evidence.before) == _DETERMINISTIC_ATTENTION_BEFORE
        and dict(evidence.inside) == _DETERMINISTIC_ATTENTION_INSIDE
        and dict(evidence.after) == _DETERMINISTIC_ATTENTION_BEFORE
        and evidence.restored is True
        and evidence.source_hash_rule == _DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE
        and dict(evidence.source_sha256) == _DETERMINISTIC_ATTENTION_SOURCE_SHA256
    )


def _allowlisted_backward_document(
    evidence: BackwardWarningEvidence,
) -> dict[str, object]:
    return {
        "operation_identifier": evidence.operation_identifier,
        "expected_count": evidence.expected_count,
        "observed_count": evidence.observed_count,
        "raw_warnings": list(evidence.raw_warnings),
        "warning_categories": list(evidence.warning_categories),
        "operation_identifiers": list(evidence.operation_identifiers),
        "source_hash_rule": evidence.source_hash_rule,
        "source_sha256": dict(sorted(evidence.source_sha256.items())),
        "strict_mode_restored": evidence.strict_mode_restored,
    }


def _deterministic_attention_document(
    evidence: DeterministicAttentionEvidence,
) -> dict[str, object]:
    return {
        "attn_implementation": evidence.attn_implementation,
        "backend": evidence.backend,
        "scope": evidence.scope,
        "before": dict(evidence.before),
        "inside": dict(evidence.inside),
        "after": dict(evidence.after),
        "restored": evidence.restored,
        "source_hash_rule": evidence.source_hash_rule,
        "source_sha256": dict(sorted(evidence.source_sha256.items())),
    }


def exact_comparison(observation: StepObservation) -> dict[str, object]:
    """Build the A3 exact replay identity, excluding post-backward float values."""
    state_digests = {
        name: str(observation.state_digests[name])
        for name in ("scheduler", "scaler", "rng", "sampler")
    }
    preimage = {
        "parameter_digest_before": observation.parameter_digest_before,
        "parameter_inventory": [dict(item) for item in observation.parameter_inventory],
        "ordered_loss_hex": [value.hex() for value in observation.ordered_losses],
        "optimizer_groups": [dict(item) for item in observation.optimizer_groups],
        "scheduler_state_before_sha256": observation.scheduler_state_before_sha256,
        "sampler_order_digest": observation.sampler_order_digest,
        "semantic_input_digests": dict(
            sorted(observation.semantic_input_digests.items())
        ),
        "checkpoint_epoch": observation.checkpoint_epoch,
        "checkpoint_step": observation.checkpoint_step,
        "model_state_inventory": [
            dict(item) for item in observation.model_state_inventory
        ],
        "state_digests": state_digests,
        "allowlisted_backward": _allowlisted_backward_document(
            observation.allowlisted_backward
        ),
        "deterministic_attention": _deterministic_attention_document(
            observation.deterministic_attention
        ),
    }
    return {
        "rule": "wave0-a3-exact-replay-sha256-v1",
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
        "allowlisted_grid_sample_backward": _allowlisted_backward_is_valid(
            observation.allowlisted_backward
        ),
        "strict_deterministic_error_mode_restored": (
            observation.allowlisted_backward.strict_mode_restored
        ),
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
        "deterministic_attention_math_only": (
            observation.deterministic_attention.attn_implementation == "sdpa"
            and observation.deterministic_attention.backend == "MATH"
            and dict(observation.deterministic_attention.inside)
            == _DETERMINISTIC_ATTENTION_INSIDE
        ),
        "deterministic_attention_scope_verified": (
            observation.deterministic_attention.scope
            == "labeled_forward_through_backward"
        ),
        "deterministic_attention_source_verified": (
            observation.deterministic_attention.source_hash_rule
            == _DETERMINISTIC_ATTENTION_SOURCE_HASH_RULE
            and dict(observation.deterministic_attention.source_sha256)
            == _DETERMINISTIC_ATTENTION_SOURCE_SHA256
        ),
        "deterministic_attention_backend_restored": (
            dict(observation.deterministic_attention.before)
            == _DETERMINISTIC_ATTENTION_BEFORE
            and dict(observation.deterministic_attention.after)
            == dict(observation.deterministic_attention.before)
            and observation.deterministic_attention.restored is True
        ),
        "allowlisted_backward_verified": _allowlisted_backward_is_valid(
            observation.allowlisted_backward
        ),
        "strict_deterministic_error_mode_restored": (
            observation.allowlisted_backward.strict_mode_restored
        ),
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
        "allowlisted_backward": _allowlisted_backward_document(
            observation.allowlisted_backward
        ),
        "deterministic_attention": _deterministic_attention_document(
            observation.deterministic_attention
        ),
        "parameter_inventory": [dict(item) for item in observation.parameter_inventory],
        "update_groups": {
            name: {"l2_norm": float(observation.update_groups[name])}
            for name in ("detector", "backbone")
        },
        "exact_comparison": exact_comparison(observation),
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
        "schema_version": 3,
        "normative": normative,
        "metadata": {"timestamp": datetime.now(UTC).isoformat(), "run_id": run_id},
    }


def _execute_probe(
    model_contract_path: Path,
    checkpoint_root: Path,
    output_path: Path,
    run_id: str,
) -> dict[str, object]:
    if _is_link_or_junction(checkpoint_root) or not checkpoint_root.is_dir():
        raise FeasibilityError(
            "checkpoint root must be the newly claimed non-link directory"
        )
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
    batch = dict(batch)
    batch["_val_semantic_input_digests"] = {
        "fixture_sha256": str(normative["fixture_sha256"]),
        "synthetic_target_sha256": str(normative["synthetic_target_sha256"]),
    }
    try:
        observation = run_one_step_smoke(model, batch, seed=SEED)
        evaluate_step_observation(observation)
        state = observation.checkpoint_state
        if state is None:
            raise FeasibilityError("checkpoint state was not captured")
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
        create_directory_no_clobber(checkpoint_root)
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
