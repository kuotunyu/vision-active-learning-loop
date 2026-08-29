"""Same-host statistical replay calculations for the Wave 0 A11 gate."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import stat
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any

import torch

from ..artifacts.digests import canonical_json_sha256, sha256_file
from ..artifacts.no_clobber import NoClobberError, NoClobberUnsupportedError
from ..artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt,
    validate_receipt_for_run,
)
from ..cli_manifest import command
from ..models.assets import DINOV2_REVISION, RTDETR_REVISION
from ..training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    load_checkpoint_verified,
)
from .numerical_replay import compare_replay

THRESHOLD_MULTIPLIER = 1.5
GRADIENT_CEILING = 0.01
RELATIVE_L2_CEILING = 0.10
COSINE_DEFECT_CEILING = 0.005
THRESHOLD_FORMULA = "wave0-a11-pairwise-max-times-1.5-v1"

METRIC_KEYS = (
    "gradient_norm.relative_difference",
    "model_update.backbone.cosine_defect",
    "model_update.backbone.relative_l2",
    "model_update.detector.cosine_defect",
    "model_update.detector.relative_l2",
    "optimizer_state.backbone.exp_avg.cosine_defect",
    "optimizer_state.backbone.exp_avg.relative_l2",
    "optimizer_state.backbone.exp_avg_sq.cosine_defect",
    "optimizer_state.backbone.exp_avg_sq.relative_l2",
    "optimizer_state.detector.exp_avg.cosine_defect",
    "optimizer_state.detector.exp_avg.relative_l2",
    "optimizer_state.detector.exp_avg_sq.cosine_defect",
    "optimizer_state.detector.exp_avg_sq.relative_l2",
)

_GROUP_NAMES = ("detector", "backbone")
_MOMENT_NAMES = ("exp_avg", "exp_avg_sq")
_PHASES = ("calibration", "validation")
_COSINE_ENDPOINT_SLACK = 1e-12
_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"
_FEASIBILITY_SCHEMA = _SCHEMA_ROOT / "feasibility-receipt.schema.json"
_CALIBRATION_SCHEMA = (
    _SCHEMA_ROOT / "statistical-replay-calibration-receipt.schema.json"
)
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
_IMAGE_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")
_BASE_IMAGE_DIGEST = (
    "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
)
_DINOV2_SHA256 = "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1"
_HISTORICAL_FILE_INVENTORY_SHA256 = (
    "e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95"
)
_HISTORICAL_IMAGE_INVENTORY_SHA256 = (
    "9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f"
)
_CALIBRATION_TERMINAL = (
    "WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
)
_VALIDATION_PASS_TERMINAL = (
    "WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED"
)
_VALIDATION_FAIL_TERMINAL = "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
_CALIBRATION_INVARIANTS = (
    "replica_count_exact",
    "replica_ids_exact",
    "replica_receipts_valid",
    "cohort_identity_exact",
    "pair_count_exact",
    "pair_order_exact",
    "metric_keys_exact",
    "exact_comparisons_pass",
    "finite_metrics",
    "thresholds_recomputed",
    "thresholds_within_ceilings",
    "publication_no_clobber",
    "historical_evidence_preserved",
)
_VALIDATION_INVARIANTS = (
    "replica_count_exact",
    "replica_ids_exact",
    "replica_receipts_valid",
    "cohort_identity_exact",
    "pair_count_exact",
    "pair_order_exact",
    "metric_keys_exact",
    "exact_comparisons_pass",
    "finite_metrics",
    "calibration_binding_exact",
    "cross_phase_static_identity_exact",
    "cross_phase_runtime_identity_distinct",
    "all_pairs_within_thresholds",
    "all_pairs_within_ceilings",
    "publication_no_clobber",
    "historical_evidence_preserved",
)


class StatisticalReplayError(ValueError):
    """Raised when A11 replay evidence or mathematics is invalid."""


@dataclass(frozen=True)
class ReplicaEvidence:
    replica_id: str
    receipt: Mapping[str, object]
    checkpoint: CheckpointState


@dataclass(frozen=True)
class PairMetrics:
    left_replica_id: str
    right_replica_id: str
    exact: Mapping[str, object]
    metrics: Mapping[str, float]


def expected_replica_ids(phase: str) -> tuple[str, ...]:
    """Return the closed, zero-padded twelve-replica inventory for one phase."""
    if phase not in _PHASES:
        raise StatisticalReplayError("replica phase is invalid")
    return tuple(f"{phase}-{index:02d}" for index in range(12))


def ordered_replica_pairs(
    replicas: Sequence[ReplicaEvidence], phase: str
) -> tuple[tuple[ReplicaEvidence, ReplicaEvidence], ...]:
    """Validate one cohort and return all 66 lexicographic unordered pairs."""
    expected = expected_replica_ids(phase)
    if (
        not isinstance(replicas, Sequence)
        or any(not isinstance(replica, ReplicaEvidence) for replica in replicas)
        or tuple(replica.replica_id for replica in replicas) != expected
    ):
        raise StatisticalReplayError("replica inventory mismatch")
    return tuple(combinations(replicas, 2))


def gradient_relative_difference(left: object, right: object) -> float:
    """Return the registered positive-gradient relative difference."""
    left_value = _positive_finite_number(left, "left gradient norm")
    right_value = _positive_finite_number(right, "right gradient norm")
    result = abs(left_value - right_value) / max(left_value, right_value)
    if not math.isfinite(result):
        raise StatisticalReplayError("gradient relative difference is non-finite")
    return result


def vector_metrics(left: torch.Tensor, right: torch.Tensor) -> dict[str, float]:
    """Return CPU-float64 relative-L2 and cosine-defect metrics for two tensors."""
    return _direct_vector_metrics((left,), (right,))


def derived_vector_metrics(
    left_norm: object, right_norm: object, difference_norm: object
) -> dict[str, float]:
    """Derive vector metrics from two positive norms and their difference norm."""
    first = _positive_finite_number(left_norm, "left vector norm")
    second = _positive_finite_number(right_norm, "right vector norm")
    difference = _nonnegative_finite_number(difference_norm, "vector difference norm")
    relative_l2 = difference / max(first, second)
    cosine = (first * first + second * second - difference * difference) / (
        2.0 * first * second
    )
    cosine = _normalize_cosine(cosine)
    if not math.isfinite(relative_l2):
        raise StatisticalReplayError("vector relative L2 is non-finite")
    return {"relative_l2": relative_l2, "cosine_defect": 1.0 - cosine}


def compare_statistical_pair(
    left: ReplicaEvidence, right: ReplicaEvidence
) -> PairMetrics:
    """Require A3 exact compatibility, then compute the thirteen A11 observations."""
    if not isinstance(left, ReplicaEvidence) or not isinstance(right, ReplicaEvidence):
        raise StatisticalReplayError("replica evidence type mismatch")
    if (
        not isinstance(left.replica_id, str)
        or not isinstance(right.replica_id, str)
        or left.replica_id >= right.replica_id
    ):
        raise StatisticalReplayError("pair replica order mismatch")

    comparison = compare_replay(
        left.receipt,
        left.checkpoint,
        right.receipt,
        right.checkpoint,
    )
    exact = comparison.exact
    if exact.get("passed") is not True:
        raise StatisticalReplayError("A11 pair requires an exact-compatible replay")

    left_normative = _mapping(left.receipt.get("normative"), "left normative")
    right_normative = _mapping(right.receipt.get("normative"), "right normative")
    left_step = _mapping(left_normative.get("step"), "left step")
    right_step = _mapping(right_normative.get("step"), "right step")
    raw_metrics: dict[str, float] = {
        "gradient_norm.relative_difference": gradient_relative_difference(
            left_step.get("gradient_norm"), right_step.get("gradient_norm")
        )
    }

    left_exact = _mapping(
        left_normative.get("exact_comparison"), "left exact comparison"
    )
    parameter_groups = _parameter_groups(left_exact)
    left_updates = _mapping(left_normative.get("update_groups"), "left update groups")
    right_updates = _mapping(
        right_normative.get("update_groups"), "right update groups"
    )
    left_model = _mapping(left.checkpoint.model_state, "left model state")
    right_model = _mapping(right.checkpoint.model_state, "right model state")
    for group_name in _GROUP_NAMES:
        difference_norm = _tensor_difference_norm(
            tuple(left_model[name] for name in parameter_groups[group_name]),
            tuple(right_model[name] for name in parameter_groups[group_name]),
        )
        left_group = _mapping(
            left_updates.get(group_name), f"left {group_name} update group"
        )
        right_group = _mapping(
            right_updates.get(group_name), f"right {group_name} update group"
        )
        metrics = derived_vector_metrics(
            left_group.get("l2_norm"),
            right_group.get("l2_norm"),
            difference_norm,
        )
        for metric_name, value in metrics.items():
            raw_metrics[f"model_update.{group_name}.{metric_name}"] = value

    left_optimizer = _mapping(left.checkpoint.optimizer_state, "left optimizer state")
    right_optimizer = _mapping(
        right.checkpoint.optimizer_state, "right optimizer state"
    )
    left_states = _mapping(left_optimizer.get("state"), "left optimizer states")
    right_states = _mapping(right_optimizer.get("state"), "right optimizer states")
    left_ids = _parameter_ids(left_optimizer)
    right_ids = _parameter_ids(right_optimizer)
    for group_name in _GROUP_NAMES:
        for moment_name in _MOMENT_NAMES:
            left_tensors: list[torch.Tensor] = []
            right_tensors: list[torch.Tensor] = []
            for left_id, right_id in zip(
                left_ids[group_name], right_ids[group_name], strict=True
            ):
                left_member = _mapping(
                    left_states.get(left_id), "left optimizer member"
                )
                right_member = _mapping(
                    right_states.get(right_id), "right optimizer member"
                )
                left_tensors.append(left_member.get(moment_name))
                right_tensors.append(right_member.get(moment_name))
            metrics = _direct_vector_metrics(left_tensors, right_tensors)
            for metric_name, value in metrics.items():
                raw_metrics[
                    f"optimizer_state.{group_name}.{moment_name}.{metric_name}"
                ] = value

    if set(raw_metrics) != set(METRIC_KEYS):
        raise StatisticalReplayError("computed metric inventory mismatch")
    metrics = {key: raw_metrics[key] for key in METRIC_KEYS}
    return PairMetrics(left.replica_id, right.replica_id, dict(exact), metrics)


def derive_calibration_thresholds(
    pairs: Sequence[PairMetrics],
) -> Mapping[str, Mapping[str, object]]:
    """Derive the frozen 1.5-times-maximum thresholds from all calibration pairs."""
    values = _validated_pair_values(pairs, "calibration")
    thresholds: dict[str, Mapping[str, object]] = {}
    for key in METRIC_KEYS:
        maximum = max(values[key])
        threshold = THRESHOLD_MULTIPLIER * maximum
        if not math.isfinite(threshold):
            raise StatisticalReplayError(f"{key} threshold is non-finite")
        if threshold > _ceiling_for(key):
            raise StatisticalReplayError(f"{key} threshold exceeds practical ceiling")
        thresholds[key] = {
            "maximum": maximum,
            "maximum_hex": maximum.hex(),
            "threshold": threshold,
            "threshold_hex": threshold.hex(),
        }
    return thresholds


def threshold_inventory_sha256(thresholds: Mapping[str, object]) -> str:
    """Return the canonical digest of the closed threshold inventory."""
    _validate_thresholds(thresholds)
    return canonical_json_sha256(
        {
            "formula": THRESHOLD_FORMULA,
            "metric_keys": list(METRIC_KEYS),
            "thresholds": dict(thresholds),
        }
    )


def summarize_validation(
    pairs: Sequence[PairMetrics], thresholds: Mapping[str, object]
) -> Mapping[str, object]:
    """Summarize all validation values and apply frozen thresholds plus ceilings."""
    values = _validated_pair_values(pairs, "validation")
    threshold_values = _validate_thresholds(thresholds)
    summaries: dict[str, Mapping[str, float]] = {}
    threshold_errors: list[str] = []
    ceiling_errors: list[str] = []
    for key in METRIC_KEYS:
        ordered_values = sorted(values[key])
        summaries[key] = {
            "minimum": ordered_values[0],
            "median": (ordered_values[32] + ordered_values[33]) / 2.0,
            "maximum": ordered_values[-1],
        }
        for pair, value in zip(pairs, values[key], strict=True):
            pair_name = f"{pair.left_replica_id}/{pair.right_replica_id} {key}"
            if value > threshold_values[key]:
                threshold_errors.append(f"{pair_name} exceeds calibration threshold")
            if value > _ceiling_for(key):
                ceiling_errors.append(f"{pair_name} exceeds practical ceiling")
    errors = sorted({*threshold_errors, *ceiling_errors})
    return {
        "summaries": summaries,
        "all_pairs_within_thresholds": not threshold_errors,
        "all_pairs_within_ceilings": not ceiling_errors,
        "errors": errors,
    }


def _mapping(value: object, label: str) -> Mapping[Any, Any]:
    if not isinstance(value, Mapping):
        raise StatisticalReplayError(f"{label} must be an object")
    return value


def _positive_finite_number(value: object, label: str) -> float:
    result = _nonnegative_finite_number(value, label)
    if result == 0.0:
        raise StatisticalReplayError(f"{label} must be a positive gradient or vector")
    return result


def _nonnegative_finite_number(value: object, label: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(float(value)):
        raise StatisticalReplayError(f"{label} must be finite")
    result = float(value)
    if result < 0.0:
        raise StatisticalReplayError(f"{label} must be nonnegative")
    return result


def _normalize_cosine(value: float) -> float:
    if not math.isfinite(value):
        raise StatisticalReplayError("vector cosine is non-finite")
    if abs(value + 1.0) <= _COSINE_ENDPOINT_SLACK:
        return -1.0
    if abs(value - 1.0) <= _COSINE_ENDPOINT_SLACK:
        return 1.0
    if value < -1.0:
        raise StatisticalReplayError("vector cosine is outside its domain")
    if value > 1.0:
        raise StatisticalReplayError("vector cosine is outside its domain")
    return value


def _validate_tensor_pair(
    left: object, right: object, label: str
) -> tuple[torch.Tensor, torch.Tensor]:
    if not isinstance(left, torch.Tensor) or not isinstance(right, torch.Tensor):
        raise StatisticalReplayError(f"{label} must contain tensors")
    if left.shape != right.shape:
        raise StatisticalReplayError(f"{label} shape mismatch")
    if left.dtype != right.dtype:
        raise StatisticalReplayError(f"{label} dtype mismatch")
    if not left.is_floating_point() or left.numel() == 0:
        raise StatisticalReplayError(f"{label} dtype must be floating point")
    left64 = left.detach().cpu().to(torch.float64)
    right64 = right.detach().cpu().to(torch.float64)
    if not bool(torch.isfinite(left64).all()) or not bool(
        torch.isfinite(right64).all()
    ):
        raise StatisticalReplayError(f"{label} tensors must be finite")
    return left64, right64


def _direct_vector_metrics(
    left_tensors: Sequence[torch.Tensor], right_tensors: Sequence[torch.Tensor]
) -> dict[str, float]:
    if not left_tensors or len(left_tensors) != len(right_tensors):
        raise StatisticalReplayError("vector tensor inventory mismatch")
    left_squared = 0.0
    right_squared = 0.0
    difference_squared = 0.0
    dot = 0.0
    for left, right in zip(left_tensors, right_tensors, strict=True):
        left64, right64 = _validate_tensor_pair(left, right, "vector")
        left_squared += float(torch.sum(left64 * left64))
        right_squared += float(torch.sum(right64 * right64))
        difference = left64 - right64
        difference_squared += float(torch.sum(difference * difference))
        dot += float(torch.sum(left64 * right64))
    left_norm = math.sqrt(left_squared)
    right_norm = math.sqrt(right_squared)
    if left_norm == 0.0 or right_norm == 0.0:
        raise StatisticalReplayError("vector norm is zero")
    relative_l2 = math.sqrt(difference_squared) / max(left_norm, right_norm)
    cosine = _normalize_cosine(dot / (left_norm * right_norm))
    if not math.isfinite(relative_l2):
        raise StatisticalReplayError("vector relative L2 is non-finite")
    return {"relative_l2": relative_l2, "cosine_defect": 1.0 - cosine}


def _tensor_difference_norm(
    left_tensors: Sequence[object], right_tensors: Sequence[object]
) -> float:
    if not left_tensors or len(left_tensors) != len(right_tensors):
        raise StatisticalReplayError("model update tensor inventory mismatch")
    difference_squared = 0.0
    for left, right in zip(left_tensors, right_tensors, strict=True):
        left64, right64 = _validate_tensor_pair(left, right, "model update")
        difference = left64 - right64
        difference_squared += float(torch.sum(difference * difference))
    result = math.sqrt(difference_squared)
    if not math.isfinite(result):
        raise StatisticalReplayError("model update difference is non-finite")
    return result


def _parameter_groups(exact: Mapping[str, object]) -> Mapping[str, tuple[str, ...]]:
    inventory = exact.get("parameter_inventory")
    if not isinstance(inventory, list):
        raise StatisticalReplayError("exact parameter inventory is invalid")
    groups: dict[str, list[str]] = {name: [] for name in _GROUP_NAMES}
    for value in inventory:
        entry = _mapping(value, "parameter inventory entry")
        name = entry.get("name")
        group_name = entry.get("group_name")
        if not isinstance(name, str) or group_name not in _GROUP_NAMES:
            raise StatisticalReplayError("exact parameter inventory is invalid")
        groups[str(group_name)].append(name)
    if any(not groups[name] for name in _GROUP_NAMES):
        raise StatisticalReplayError("exact parameter groups are incomplete")
    return {name: tuple(groups[name]) for name in _GROUP_NAMES}


def _parameter_ids(optimizer: Mapping[str, object]) -> Mapping[str, tuple[int, ...]]:
    groups = optimizer.get("param_groups")
    if not isinstance(groups, list) or len(groups) != 2:
        raise StatisticalReplayError("optimizer parameter groups are invalid")
    result: dict[str, tuple[int, ...]] = {}
    for index, group_name in enumerate(_GROUP_NAMES):
        group = _mapping(groups[index], "optimizer parameter group")
        identifiers = group.get("params")
        if (
            group.get("group_name") != group_name
            or not isinstance(identifiers, list)
            or any(type(item) is not int for item in identifiers)
        ):
            raise StatisticalReplayError("optimizer parameter order mismatch")
        result[group_name] = tuple(identifiers)
    return result


def _validated_pair_values(
    pairs: Sequence[PairMetrics], phase: str
) -> Mapping[str, list[float]]:
    expected_pairs = tuple(combinations(expected_replica_ids(phase), 2))
    if not isinstance(pairs, Sequence) or len(pairs) != len(expected_pairs):
        raise StatisticalReplayError("pair count mismatch")
    values = {key: [] for key in METRIC_KEYS}
    for pair, expected in zip(pairs, expected_pairs, strict=True):
        if (
            not isinstance(pair, PairMetrics)
            or (pair.left_replica_id, pair.right_replica_id) != expected
        ):
            raise StatisticalReplayError("pair order mismatch")
        if not isinstance(pair.exact, Mapping) or pair.exact.get("passed") is not True:
            raise StatisticalReplayError("pair exact comparison failed")
        if not isinstance(pair.metrics, Mapping) or tuple(pair.metrics) != METRIC_KEYS:
            raise StatisticalReplayError("metric inventory mismatch")
        for key in METRIC_KEYS:
            value = _nonnegative_finite_number(pair.metrics[key], f"{key} metric")
            values[key].append(value)
    return values


def _validate_thresholds(thresholds: Mapping[str, object]) -> Mapping[str, float]:
    if not isinstance(thresholds, Mapping) or tuple(thresholds) != METRIC_KEYS:
        raise StatisticalReplayError("threshold metric inventory mismatch")
    result: dict[str, float] = {}
    expected_fields = {"maximum", "maximum_hex", "threshold", "threshold_hex"}
    for key in METRIC_KEYS:
        entry = _mapping(thresholds[key], f"{key} threshold")
        if set(entry) != expected_fields:
            raise StatisticalReplayError(f"{key} threshold fields mismatch")
        maximum = _nonnegative_finite_number(entry.get("maximum"), f"{key} maximum")
        threshold = _nonnegative_finite_number(
            entry.get("threshold"), f"{key} threshold"
        )
        if entry.get("maximum_hex") != maximum.hex():
            raise StatisticalReplayError(f"{key} maximum hexadecimal mismatch")
        if entry.get("threshold_hex") != threshold.hex():
            raise StatisticalReplayError(f"{key} threshold hexadecimal mismatch")
        if threshold != THRESHOLD_MULTIPLIER * maximum:
            raise StatisticalReplayError(f"{key} threshold derivation mismatch")
        result[key] = threshold
    return result


def _ceiling_for(key: str) -> float:
    if key == "gradient_norm.relative_difference":
        return GRADIENT_CEILING
    if key.endswith(".relative_l2"):
        return RELATIVE_L2_CEILING
    if key.endswith(".cosine_defect"):
        return COSINE_DEFECT_CEILING
    raise StatisticalReplayError(f"unknown metric key: {key}")


@dataclass(frozen=True)
class _PhaseEvidence:
    phase: str
    manifest: Mapping[str, object]
    replicas: tuple[ReplicaEvidence, ...]
    replica_records: tuple[Mapping[str, object], ...]
    static_identity: Mapping[str, object]
    runtime_identity: Mapping[str, object]


def _require_exact_keys(
    value: object, expected: set[str], label: str
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or set(value) != expected:
        raise StatisticalReplayError(f"{label} fields mismatch")
    return value


def _require_nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\r" in value or "\n" in value:
        raise StatisticalReplayError(f"{label} is invalid")
    return value


def _require_pattern(value: object, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise StatisticalReplayError(f"{label} is invalid")
    return value


def _load_json(path: Path, label: str) -> Mapping[str, object]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StatisticalReplayError(f"unable to load {label}") from error
    if not isinstance(value, Mapping):
        raise StatisticalReplayError(f"{label} must be an object")
    return value


def _same_path(left: Path, right: Path) -> bool:
    return os.path.normcase(str(left)) == os.path.normcase(str(right))


def _is_link_or_junction(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction = getattr(path, "is_junction", None)
    return bool(callable(junction) and junction())


def _validated_root(path: Path) -> Path:
    root = Path(path)
    try:
        absolute = root.absolute()
        resolved = root.resolve(strict=True)
        mode = root.lstat().st_mode
    except OSError as error:
        raise StatisticalReplayError("phase root is unavailable") from error
    if (
        not stat.S_ISDIR(mode)
        or _is_link_or_junction(root)
        or not _same_path(absolute, resolved)
    ):
        raise StatisticalReplayError("phase root must be a non-link directory")
    return resolved


def _confined_regular_file(value: object, root: Path, label: str) -> Path:
    raw = _require_nonempty(value, f"{label} path")
    path = Path(raw)
    if not path.is_absolute():
        raise StatisticalReplayError(f"{label} path must be absolute")
    try:
        absolute = path.absolute()
        resolved = path.resolve(strict=True)
        mode = path.lstat().st_mode
        absolute.relative_to(root)
        resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise StatisticalReplayError(f"{label} path escapes phase root") from error
    if (
        not stat.S_ISREG(mode)
        or _is_link_or_junction(path)
        or not _same_path(absolute, resolved)
    ):
        raise StatisticalReplayError(f"{label} must be a regular non-link file")
    return resolved


def _external_regular_file(path: Path, label: str) -> Path:
    candidate = Path(path)
    try:
        absolute = candidate.absolute()
        resolved = candidate.resolve(strict=True)
        mode = candidate.lstat().st_mode
    except OSError as error:
        raise StatisticalReplayError(f"{label} is unavailable") from error
    if (
        not stat.S_ISREG(mode)
        or _is_link_or_junction(candidate)
        or not _same_path(absolute, resolved)
    ):
        raise StatisticalReplayError(f"{label} must be a regular non-link file")
    return resolved


def _validate_output_destination(path: Path, root: Path) -> None:
    candidate = Path(path)
    if not candidate.is_absolute():
        raise StatisticalReplayError("aggregate output path must be absolute")
    try:
        parent_absolute = candidate.parent.absolute()
        parent_resolved = candidate.parent.resolve(strict=True)
        candidate.absolute().relative_to(root)
        parent_resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise StatisticalReplayError(
            "aggregate output path escapes phase root"
        ) from error
    if (
        not parent_resolved.is_dir()
        or _is_link_or_junction(candidate.parent)
        or not _same_path(parent_absolute, parent_resolved)
    ):
        raise StatisticalReplayError(
            "aggregate output parent must be a non-link directory"
        )


def _validated_file_record(
    value: object, root: Path, label: str
) -> tuple[Mapping[str, object], Path]:
    record = _require_exact_keys(value, {"path", "size", "sha256"}, label)
    size = record.get("size")
    digest = record.get("sha256")
    if type(size) is not int or size < 0:
        raise StatisticalReplayError(f"{label} size is invalid")
    _require_pattern(digest, _HASH_PATTERN, f"{label} hash")
    path = _confined_regular_file(record.get("path"), root, label)
    if path.stat().st_size != size:
        raise StatisticalReplayError(f"{label} size mismatch")
    if sha256_file(path) != digest:
        raise StatisticalReplayError(f"{label} hash mismatch")
    return record, path


def _model_cache_inventory_sha256(root: Path) -> str:
    entries: list[dict[str, object]] = []
    try:
        paths = list(root.rglob("*"))
    except OSError as error:
        raise StatisticalReplayError("model cache inventory is unavailable") from error
    inventory_files: list[tuple[str, Path]] = []
    for path in paths:
        if _is_link_or_junction(path):
            raise StatisticalReplayError("model cache contains a link or junction")
        if path.is_dir():
            continue
        if not path.is_file():
            raise StatisticalReplayError("model cache contains a non-regular file")
        relative = path.relative_to(root).as_posix()
        inventory_files.append((relative, path))
    for relative, path in sorted(inventory_files, key=lambda item: item[0]):
        if relative.endswith(".metadata") and "/.cache/huggingface/download/" in (
            f"/{relative}"
        ):
            # The third line is a download-time observation; commit and ETag are
            # the stable cache identity already verified by the assets receipt.
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
                timestamp = float(lines[2])
            except (OSError, UnicodeDecodeError, ValueError, IndexError) as error:
                raise StatisticalReplayError(
                    "model cache metadata is invalid"
                ) from error
            if len(lines) != 3 or not math.isfinite(timestamp) or timestamp <= 0.0:
                raise StatisticalReplayError("model cache metadata is invalid")
            normalized = f"{lines[0]}\n{lines[1]}\n".encode()
            size = len(normalized)
            digest = hashlib.sha256(normalized).hexdigest()
        else:
            size = path.stat().st_size
            digest = sha256_file(path)
        entries.append({"path": relative, "size": size, "sha256": digest})
    if not entries:
        raise StatisticalReplayError("model cache is empty")
    return canonical_json_sha256({"files": entries})


def _validate_invocation_audit(
    record: object,
    root: Path,
    *,
    run_id: str,
    receipt_path: Path,
    checkpoint_path: Path,
) -> Path:
    _, audit_path = _validated_file_record(record, root, "invocation audit")
    audit = _require_exact_keys(
        _load_json(audit_path, "invocation audit"),
        {"schema_version", "argv", "exit_code", "stdout", "stderr"},
        "invocation audit",
    )
    if audit.get("schema_version") != 1 or audit.get("exit_code") != 0:
        raise StatisticalReplayError("invocation audit did not record success")
    argv = audit.get("argv")
    if (
        not isinstance(argv, list)
        or not argv
        or any(not isinstance(item, str) or not item for item in argv)
    ):
        raise StatisticalReplayError("invocation argv is invalid")
    expected_argv = [
        "val",
        "probe",
        "training-feasibility",
        "--model-contract",
        (receipt_path.parent / "model-contract.json").as_posix(),
        "--checkpoint-root",
        checkpoint_path.parent.as_posix(),
        "--run-id",
        run_id,
        "--output",
        receipt_path.as_posix(),
    ]
    if argv != expected_argv:
        raise StatisticalReplayError("invocation argv binding mismatch")
    stream_paths: dict[str, Path] = {}
    for stream in ("stdout", "stderr"):
        _, stream_paths[stream] = _validated_file_record(
            audit.get(stream), root, f"invocation {stream}"
        )
    try:
        stdout = stream_paths["stdout"].read_bytes()
        stderr = stream_paths["stderr"].read_bytes()
    except OSError as error:
        raise StatisticalReplayError("invocation streams are unavailable") from error
    if stdout != b"PASS\n" or stderr != b"":
        raise StatisticalReplayError("invocation process stream contract mismatch")
    return audit_path


def _validate_historical_preservation(path: Path) -> None:
    evidence = _require_exact_keys(
        _load_json(path, "historical preservation"),
        {
            "schema_version",
            "historical_file_count",
            "historical_image_count",
            "historical_file_inventory_sha256",
            "historical_image_inventory_sha256",
            "preserved",
        },
        "historical preservation",
    )
    expected = {
        "schema_version": 1,
        "historical_file_count": 64306,
        "historical_image_count": 21,
        "historical_file_inventory_sha256": _HISTORICAL_FILE_INVENTORY_SHA256,
        "historical_image_inventory_sha256": _HISTORICAL_IMAGE_INVENTORY_SHA256,
        "preserved": True,
    }
    if evidence != expected:
        raise StatisticalReplayError("historical preservation evidence mismatch")


def _validate_lease_evidence(
    path: Path,
    *,
    manifest: Mapping[str, object],
    root: Path,
    cache_root: Path,
    inventory_sha256: str,
    gpu: Mapping[str, object],
    audits: Mapping[str, object],
) -> None:
    evidence = _require_exact_keys(
        _load_json(path, "lease evidence"),
        {
            "schema_version",
            "phase",
            "lease_id",
            "run_id",
            "source_commit",
            "image_tag",
            "image_id",
            "campaign_root",
            "cache_root",
            "cache_inventory_sha256",
            "audit_bindings",
            "gpu_uuid",
            "acquired_at",
        },
        "lease evidence",
    )
    lease = _mapping(manifest.get("lease"), "lease")
    expected = {
        "schema_version": 1,
        "phase": manifest["phase"],
        "lease_id": lease["lease_id"],
        "run_id": manifest["run_id"],
        "source_commit": manifest["source_commit"],
        "image_tag": manifest["image_tag"],
        "image_id": manifest["image_id"],
        "campaign_root": root.as_posix(),
        "cache_root": cache_root.as_posix(),
        "cache_inventory_sha256": inventory_sha256,
        "audit_bindings": dict(audits),
        "gpu_uuid": gpu["uuid"],
    }
    for name, value in expected.items():
        if evidence.get(name) != value:
            raise StatisticalReplayError(f"lease {name} binding mismatch")
    _require_nonempty(evidence.get("acquired_at"), "lease acquired timestamp")


def _receipt_normative(document: Mapping[str, object]) -> Mapping[str, object]:
    return _mapping(document.get("normative"), "receipt normative")


def _receipt_metadata(document: Mapping[str, object]) -> Mapping[str, object]:
    return _mapping(document.get("metadata"), "receipt metadata")


def _static_identity_from_receipt(
    manifest: Mapping[str, object], receipt: Mapping[str, object]
) -> Mapping[str, object]:
    normative = _receipt_normative(receipt)
    model_contract = _mapping(
        normative.get("parent_model_contract"), "parent model contract"
    )
    model_normative = _receipt_normative(model_contract)
    model = _mapping(model_normative.get("model"), "model identity")
    environment = _mapping(model_normative.get("environment"), "model environment")
    static = {
        "source_commit": manifest["source_commit"],
        "specification_commit": manifest["specification_commit"],
        "plan_commit": manifest["plan_commit"],
        "base_image_digest": manifest["base_image_digest"],
        "detector_revision": model.get("revision"),
        "detector_sha256": normative.get("model_sha256"),
        "processor_revision": model.get("revision"),
        "processor_sha256": normative.get("processor_sha256"),
        "dinov2_revision": DINOV2_REVISION,
        "dinov2_sha256": _DINOV2_SHA256,
        "config_sha256": normative.get("config_sha256"),
        "fixture_sha256": normative.get("fixture_sha256"),
        "packages": {
            name: environment.get(name)
            for name in (
                "python",
                "uv",
                "scipy",
                "torch",
                "torchvision",
                "transformers",
                "pycocotools",
            )
        },
        "gpu": dict(_mapping(manifest.get("gpu"), "GPU identity")),
        "model_cache_inventory_sha256": _mapping(
            manifest.get("model_cache"), "model cache"
        ).get("inventory_sha256"),
    }
    if model.get("revision") != RTDETR_REVISION:
        raise StatisticalReplayError("detector revision mismatch")
    return static


def _load_phase_manifest(
    manifest_path: Path, phase_root: Path, expected_phase: str
) -> _PhaseEvidence:
    root = _validated_root(phase_root)
    manifest_file = _confined_regular_file(
        Path(manifest_path).absolute().as_posix(), root, "phase manifest"
    )
    manifest = _require_exact_keys(
        _load_json(manifest_file, "phase manifest"),
        {
            "schema_version",
            "phase",
            "run_id",
            "campaign_root",
            "source_commit",
            "specification_commit",
            "plan_commit",
            "image_tag",
            "image_id",
            "base_image_digest",
            "owner_authorization_id",
            "model_cache",
            "gpu",
            "lease",
            "historical_preservation",
            "audits",
            "replicas",
        },
        "phase manifest",
    )
    if manifest.get("schema_version") != 1 or manifest.get("phase") != expected_phase:
        raise StatisticalReplayError("phase manifest identity mismatch")
    if not _same_path(Path(str(manifest.get("campaign_root"))).resolve(), root):
        raise StatisticalReplayError("campaign root binding mismatch")
    run_id = _require_nonempty(manifest.get("run_id"), "run ID")
    if not run_id.startswith(f"wave0-a11-{expected_phase}-"):
        raise StatisticalReplayError("run ID phase mismatch")
    for name in ("source_commit", "specification_commit", "plan_commit"):
        _require_pattern(manifest.get(name), _COMMIT_PATTERN, name)
    image_tag = _require_nonempty(manifest.get("image_tag"), "image tag")
    if not image_tag.startswith(
        f"vision-active-learning-loop:wave0-a11-{expected_phase}-"
    ):
        raise StatisticalReplayError("image tag phase mismatch")
    _require_pattern(manifest.get("image_id"), _IMAGE_PATTERN, "image ID")
    if manifest.get("base_image_digest") != _BASE_IMAGE_DIGEST:
        raise StatisticalReplayError("base image digest mismatch")
    _require_nonempty(manifest.get("owner_authorization_id"), "owner authorization ID")

    gpu = _require_exact_keys(
        manifest.get("gpu"), {"name", "uuid", "driver", "cuda_runtime"}, "GPU"
    )
    if (
        gpu.get("name") != "NVIDIA GeForce RTX 4090"
        or gpu.get("cuda_runtime") != "12.6"
    ):
        raise StatisticalReplayError("GPU contract mismatch")
    for name in ("uuid", "driver"):
        _require_nonempty(gpu.get(name), f"GPU {name}")
    model_cache = _require_exact_keys(
        manifest.get("model_cache"), {"path", "inventory_sha256"}, "model cache"
    )
    cache_path_raw = _require_nonempty(model_cache.get("path"), "model cache path")
    cache_path = Path(cache_path_raw)
    try:
        cache_resolved = cache_path.resolve(strict=True)
        cache_resolved.relative_to(root)
    except (OSError, ValueError) as error:
        raise StatisticalReplayError("model cache escapes phase root") from error
    if (
        not cache_resolved.is_dir()
        or _is_link_or_junction(cache_path)
        or not _same_path(cache_path.absolute(), cache_resolved)
    ):
        raise StatisticalReplayError("model cache must be a non-link directory")
    inventory_digest = _require_pattern(
        model_cache.get("inventory_sha256"), _HASH_PATTERN, "model cache inventory"
    )
    if _model_cache_inventory_sha256(cache_resolved) != inventory_digest:
        raise StatisticalReplayError("model cache inventory mismatch")

    lease = _require_exact_keys(
        manifest.get("lease"),
        {"lease_id", "path", "size", "sha256"},
        "lease",
    )
    _require_nonempty(lease.get("lease_id"), "lease ID")
    _, lease_path = _validated_file_record(
        {name: lease[name] for name in ("path", "size", "sha256")},
        root,
        "lease",
    )
    _, history_path = _validated_file_record(
        manifest.get("historical_preservation"), root, "historical preservation"
    )
    _validate_historical_preservation(history_path)
    audits = _require_exact_keys(
        manifest.get("audits"),
        {"identity", "image_inspect", "cache_inventory", "gpu_preflight"},
        "audits",
    )
    audit_paths: list[str] = []
    for name in ("identity", "image_inspect", "cache_inventory", "gpu_preflight"):
        _, path = _validated_file_record(audits.get(name), root, f"{name} audit")
        audit_paths.append(path.as_posix())
    _validate_lease_evidence(
        lease_path,
        manifest=manifest,
        root=root,
        cache_root=cache_resolved,
        inventory_sha256=inventory_digest,
        gpu=gpu,
        audits=audits,
    )

    replica_documents = manifest.get("replicas")
    expected_ids = expected_replica_ids(expected_phase)
    if not isinstance(replica_documents, list) or len(replica_documents) != 12:
        raise StatisticalReplayError("replica count mismatch")
    replicas: list[ReplicaEvidence] = []
    records: list[Mapping[str, object]] = []
    container_ids: list[str] = []
    receipt_paths: list[str] = []
    receipt_hashes: list[str] = []
    checkpoint_paths: list[str] = []
    checkpoint_hashes: list[str] = []
    timestamps: list[str] = []
    static_identity: Mapping[str, object] | None = None
    for replica_value, replica_id in zip(replica_documents, expected_ids, strict=True):
        replica = _require_exact_keys(
            replica_value,
            {
                "replica_id",
                "container_id",
                "timestamp",
                "invocation_audit",
                "feasibility",
                "checkpoint",
            },
            "replica",
        )
        if replica.get("replica_id") != replica_id:
            raise StatisticalReplayError("replica ID order mismatch")
        container_id = _require_pattern(
            replica.get("container_id"), _HASH_PATTERN, "container ID"
        )
        timestamp = _require_nonempty(replica.get("timestamp"), "replica timestamp")
        feasibility_record, receipt_path = _validated_file_record(
            replica.get("feasibility"), root, "feasibility receipt"
        )
        checkpoint_record, checkpoint_path = _validated_file_record(
            replica.get("checkpoint"), root, "checkpoint"
        )
        _validate_invocation_audit(
            replica.get("invocation_audit"),
            root,
            run_id=run_id,
            receipt_path=receipt_path,
            checkpoint_path=checkpoint_path,
        )
        receipt = _load_json(receipt_path, "feasibility receipt")
        validate_receipt_for_run(receipt, _FEASIBILITY_SCHEMA, run_id)
        if _receipt_metadata(receipt).get("timestamp") != timestamp:
            raise StatisticalReplayError("replica receipt timestamp mismatch")
        normative = _receipt_normative(receipt)
        if normative.get("status") != "PASS" or normative.get("errors") != []:
            raise StatisticalReplayError("replica feasibility receipt is not PASS")
        environment = _mapping(normative.get("environment"), "replica environment")
        observed = _mapping(environment.get("observed"), "observed environment")
        expected_environment = {
            "runtime_image_digest": manifest["image_id"],
            "container_image_digest": manifest["base_image_digest"],
            "gpu_name": gpu["name"],
            "gpu_uuid": gpu["uuid"],
            "driver": gpu["driver"],
            "cuda_runtime": gpu["cuda_runtime"],
        }
        if any(
            observed.get(name) != value for name, value in expected_environment.items()
        ):
            raise StatisticalReplayError("replica environment identity mismatch")
        checkpoint_digest = normative.get("checkpoint_sha256")
        parent_digest = normative.get("model_contract_receipt_sha256")
        if checkpoint_digest != checkpoint_record.get("sha256") or not isinstance(
            parent_digest, str
        ):
            raise StatisticalReplayError("checkpoint receipt binding mismatch")
        checkpoint = load_checkpoint_verified(
            checkpoint_path,
            str(checkpoint_digest),
            expected_input_digests={"model_contract_receipt": parent_digest},
        )
        current_static = _static_identity_from_receipt(manifest, receipt)
        if static_identity is None:
            static_identity = current_static
        elif current_static != static_identity:
            raise StatisticalReplayError("replica cohort identity mismatch")
        replicas.append(ReplicaEvidence(replica_id, receipt, checkpoint))
        records.append(replica)
        container_ids.append(container_id)
        receipt_paths.append(receipt_path.as_posix())
        receipt_hashes.append(str(feasibility_record["sha256"]))
        checkpoint_paths.append(checkpoint_path.as_posix())
        checkpoint_hashes.append(str(checkpoint_record["sha256"]))
        timestamps.append(timestamp)
    if len(set(container_ids)) != 12:
        raise StatisticalReplayError("container IDs are not unique")
    assert static_identity is not None
    runtime_identity = {
        "run_id": run_id,
        "image_tag": manifest["image_tag"],
        "image_id": manifest["image_id"],
        "campaign_root": root.as_posix(),
        "model_cache_root": cache_resolved.as_posix(),
        "lease_id": lease["lease_id"],
        "lease_path": lease_path.as_posix(),
        "container_ids": container_ids,
        "replica_receipt_paths": receipt_paths,
        "replica_receipt_sha256": receipt_hashes,
        "checkpoint_paths": checkpoint_paths,
        "checkpoint_sha256": checkpoint_hashes,
        "timestamps": timestamps,
        "audit_paths": [*audit_paths, history_path.as_posix()],
        "replica_ids": list(expected_ids),
    }
    return _PhaseEvidence(
        phase=expected_phase,
        manifest=manifest,
        replicas=tuple(replicas),
        replica_records=tuple(records),
        static_identity=static_identity,
        runtime_identity=runtime_identity,
    )


def _pair_documents(evidence: _PhaseEvidence) -> tuple[PairMetrics, ...]:
    ordered = ordered_replica_pairs(evidence.replicas, evidence.phase)
    return tuple(compare_statistical_pair(left, right) for left, right in ordered)


def _pair_as_dict(pair: PairMetrics) -> dict[str, object]:
    return {
        "left_replica_id": pair.left_replica_id,
        "right_replica_id": pair.right_replica_id,
        "exact": dict(pair.exact),
        "metrics": {key: pair.metrics[key] for key in METRIC_KEYS},
    }


def _aggregate_replica_records(evidence: _PhaseEvidence) -> list[dict[str, object]]:
    result = []
    for replica in evidence.replica_records:
        result.append(
            {
                "replica_id": replica["replica_id"],
                "feasibility": dict(
                    _mapping(replica.get("feasibility"), "feasibility record")
                ),
                "checkpoint": dict(
                    _mapping(replica.get("checkpoint"), "checkpoint record")
                ),
            }
        )
    return result


def _metadata_from_manifest(evidence: _PhaseEvidence) -> dict[str, object]:
    manifest = evidence.manifest
    timestamps = evidence.runtime_identity["timestamps"]
    assert isinstance(timestamps, list)
    return {
        "run_id": manifest["run_id"],
        "source_commit": manifest["source_commit"],
        "specification_commit": manifest["specification_commit"],
        "plan_commit": manifest["plan_commit"],
        "image_tag": manifest["image_tag"],
        "image_id": manifest["image_id"],
        "base_image_digest": manifest["base_image_digest"],
        "owner_authorization_id": manifest["owner_authorization_id"],
        "timestamp": timestamps[-1],
    }


def _practical_ceilings() -> dict[str, object]:
    return {
        "threshold_multiplier": THRESHOLD_MULTIPLIER,
        "threshold_multiplier_hex": THRESHOLD_MULTIPLIER.hex(),
        "gradient_relative_difference": GRADIENT_CEILING,
        "gradient_relative_difference_hex": GRADIENT_CEILING.hex(),
        "vector_relative_l2": RELATIVE_L2_CEILING,
        "vector_relative_l2_hex": RELATIVE_L2_CEILING.hex(),
        "cosine_defect": COSINE_DEFECT_CEILING,
        "cosine_defect_hex": COSINE_DEFECT_CEILING.hex(),
    }


def _calibration_receipt(evidence: _PhaseEvidence) -> dict[str, object]:
    pairs = _pair_documents(evidence)
    thresholds = derive_calibration_thresholds(pairs)
    return {
        "receipt_type": "statistical-replay-calibration",
        "schema_version": 1,
        "normative": {
            "phase": "calibration",
            "identity": {
                "static": dict(evidence.static_identity),
                "runtime": dict(evidence.runtime_identity),
            },
            "replicas": _aggregate_replica_records(evidence),
            "pairs": [_pair_as_dict(pair) for pair in pairs],
            "metric_keys": list(METRIC_KEYS),
            "practical_ceilings": _practical_ceilings(),
            "derivation": {
                "formula": THRESHOLD_FORMULA,
                "pair_count": len(pairs),
                "metric_count": len(METRIC_KEYS),
            },
            "thresholds": dict(thresholds),
            "threshold_inventory_sha256": threshold_inventory_sha256(thresholds),
            "invariants": {name: True for name in _CALIBRATION_INVARIANTS},
            "historical_preservation": dict(
                _mapping(
                    evidence.manifest.get("historical_preservation"),
                    "historical preservation",
                )
            ),
            "status": "RECORDED",
            "errors": [],
            "terminal": _CALIBRATION_TERMINAL,
        },
        "metadata": _metadata_from_manifest(evidence),
    }


def _load_calibration_receipt(path: Path) -> tuple[Mapping[str, object], Path]:
    receipt_path = _external_regular_file(path, "calibration receipt")
    document = _load_json(receipt_path, "calibration receipt")
    validate_receipt(document, _CALIBRATION_SCHEMA)
    normative = _receipt_normative(document)
    if (
        normative.get("status") != "RECORDED"
        or normative.get("errors") != []
        or normative.get("terminal") != _CALIBRATION_TERMINAL
    ):
        raise StatisticalReplayError("calibration receipt is not complete")
    return document, receipt_path


def _validation_receipt(
    evidence: _PhaseEvidence,
    calibration: Mapping[str, object],
    calibration_path: Path,
) -> dict[str, object]:
    calibration_normative = _receipt_normative(calibration)
    calibration_metadata = _receipt_metadata(calibration)
    if calibration_metadata.get("owner_authorization_id") != evidence.manifest.get(
        "owner_authorization_id"
    ):
        raise StatisticalReplayError("cross-phase owner authorization mismatch")
    calibration_identity = _mapping(
        calibration_normative.get("identity"), "calibration identity"
    )
    calibration_static = _mapping(
        calibration_identity.get("static"), "calibration static identity"
    )
    calibration_runtime = _mapping(
        calibration_identity.get("runtime"), "calibration runtime identity"
    )
    if calibration_static != evidence.static_identity:
        raise StatisticalReplayError("cross-phase static identity mismatch")
    thresholds = _mapping(
        calibration_normative.get("thresholds"), "calibration thresholds"
    )
    pairs = _pair_documents(evidence)
    summary = summarize_validation(pairs, thresholds)
    within_thresholds = summary["all_pairs_within_thresholds"]
    within_ceilings = summary["all_pairs_within_ceilings"]
    passed = within_thresholds is True and within_ceilings is True
    status = "PASS" if passed else "FAIL"
    terminal = _VALIDATION_PASS_TERMINAL if passed else _VALIDATION_FAIL_TERMINAL
    invariants = {name: True for name in _VALIDATION_INVARIANTS}
    invariants["all_pairs_within_thresholds"] = within_thresholds
    invariants["all_pairs_within_ceilings"] = within_ceilings
    return {
        "receipt_type": "statistical-replay-validation",
        "schema_version": 1,
        "normative": {
            "phase": "validation",
            "identity": {
                "static": dict(evidence.static_identity),
                "runtime": dict(evidence.runtime_identity),
            },
            "replicas": _aggregate_replica_records(evidence),
            "pairs": [_pair_as_dict(pair) for pair in pairs],
            "metric_keys": list(METRIC_KEYS),
            "practical_ceilings": _practical_ceilings(),
            "calibration_binding": {
                "path": calibration_path.as_posix(),
                "size": calibration_path.stat().st_size,
                "sha256": sha256_file(calibration_path),
                "run_id": calibration_metadata["run_id"],
                "threshold_inventory_sha256": calibration_normative[
                    "threshold_inventory_sha256"
                ],
                "thresholds": dict(thresholds),
            },
            "cross_phase_identity": {
                "equal": dict(evidence.static_identity),
                "distinct": {
                    "calibration": dict(calibration_runtime),
                    "validation": dict(evidence.runtime_identity),
                },
            },
            "summaries": summary["summaries"],
            "all_pairs_decision": {
                "within_thresholds": within_thresholds,
                "within_ceilings": within_ceilings,
                "passed": passed,
            },
            "invariants": invariants,
            "historical_preservation": dict(
                _mapping(
                    evidence.manifest.get("historical_preservation"),
                    "historical preservation",
                )
            ),
            "status": status,
            "errors": summary["errors"],
            "terminal": terminal,
        },
        "metadata": _metadata_from_manifest(evidence),
    }


def _parser(prog: str, *, validation: bool) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument("--phase-manifest", type=Path, required=True)
    parser.add_argument("--phase-root", type=Path, required=True)
    if validation:
        parser.add_argument("--calibration-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    return parser


def _print_input_error(error: BaseException) -> int:
    print(error, file=sys.stderr)
    return 2


def _publish_aggregate(output: Path, receipt: Mapping[str, object]) -> int | None:
    try:
        atomic_write_receipt(output, receipt)
    except (
        NoClobberError,
        NoClobberUnsupportedError,
        OSError,
        ReceiptValidationError,
        ValueError,
    ) as error:
        print(error, file=sys.stderr)
        return 3
    return None


@command("gate statistical-replay calibrate")
def calibration_main(argv: Sequence[str] | None = None) -> int:
    """Validate a fresh calibration cohort and publish its frozen thresholds."""
    arguments = _parser(
        "val gate statistical-replay calibrate", validation=False
    ).parse_args(argv)
    if arguments.output.exists():
        print("calibration output already exists", file=sys.stderr)
        return 3
    try:
        evidence = _load_phase_manifest(
            arguments.phase_manifest, arguments.phase_root, "calibration"
        )
        _validate_output_destination(
            arguments.output, Path(arguments.phase_root).resolve(strict=True)
        )
        receipt = _calibration_receipt(evidence)
    except (
        CheckpointVerificationError,
        ReceiptValidationError,
        StatisticalReplayError,
        OSError,
        ValueError,
    ) as error:
        return _print_input_error(error)
    publication_error = _publish_aggregate(arguments.output, receipt)
    if publication_error is not None:
        return publication_error
    print(_CALIBRATION_TERMINAL)
    return 0


@command("gate statistical-replay validate")
def validation_main(argv: Sequence[str] | None = None) -> int:
    """Validate a fresh holdout cohort against one immutable calibration."""
    arguments = _parser(
        "val gate statistical-replay validate", validation=True
    ).parse_args(argv)
    if arguments.output.exists():
        print("validation output already exists", file=sys.stderr)
        return 3
    try:
        calibration, calibration_path = _load_calibration_receipt(
            arguments.calibration_receipt
        )
        evidence = _load_phase_manifest(
            arguments.phase_manifest, arguments.phase_root, "validation"
        )
        _validate_output_destination(
            arguments.output, Path(arguments.phase_root).resolve(strict=True)
        )
        receipt = _validation_receipt(evidence, calibration, calibration_path)
    except (
        CheckpointVerificationError,
        ReceiptValidationError,
        StatisticalReplayError,
        OSError,
        ValueError,
    ) as error:
        return _print_input_error(error)
    publication_error = _publish_aggregate(arguments.output, receipt)
    if publication_error is not None:
        return publication_error
    normative = _receipt_normative(receipt)
    print(normative["terminal"])
    return 0 if normative["status"] == "PASS" else 2
