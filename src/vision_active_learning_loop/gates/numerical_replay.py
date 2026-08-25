"""Exact and bounded same-host replay comparisons for Wave 0 A3."""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import torch

from ..training.checkpoint_io import CheckpointState

GRADIENT_REL_TOL = 1e-5
GRADIENT_ABS_TOL = 1e-7
VECTOR_REL_L2_LIMIT = 1e-3
VECTOR_COSINE_MINIMUM = 0.99999
_GROUP_NAMES = ("detector", "backbone")
_MOMENT_NAMES = ("exp_avg", "exp_avg_sq")


class ReplayComparisonError(ValueError):
    """Raised internally when replay evidence is incomplete or ambiguous."""


@dataclass(frozen=True)
class ReplayComparison:
    exact: Mapping[str, object]
    numerical: Mapping[str, object]
    errors: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.errors

    def as_dict(self) -> dict[str, object]:
        return {
            "exact": dict(self.exact),
            "numerical": dict(self.numerical),
            "errors": list(self.errors),
            "passed": self.passed,
        }


@dataclass(frozen=True)
class _ParsedState:
    inventory: tuple[Mapping[str, object], ...]
    parameter_names: Mapping[str, tuple[str, ...]]
    parameter_ids: Mapping[str, tuple[int, ...]]


def compare_replay(
    canonical_receipt: Mapping[str, object],
    canonical_state: CheckpointState,
    replay_receipt: Mapping[str, object],
    replay_state: CheckpointState,
) -> ReplayComparison:
    """Compare one replay to primary A without trusting child PASS booleans."""
    exact_errors: list[str] = []
    numerical_errors: list[str] = []
    canonical_exact_sha256 = "0" * 64
    replay_exact_sha256 = "0" * 64
    try:
        canonical_normative = _normative(canonical_receipt)
        replay_normative = _normative(replay_receipt)
        canonical_exact = _mapping(
            canonical_normative.get("exact_comparison"), "canonical exact comparison"
        )
        replay_exact = _mapping(
            replay_normative.get("exact_comparison"), "replay exact comparison"
        )
        canonical_exact_sha256 = _sha256(
            canonical_exact.get("sha256"), "canonical exact comparison sha256"
        )
        replay_exact_sha256 = _sha256(
            replay_exact.get("sha256"), "replay exact comparison sha256"
        )
        if not _values_equal(canonical_exact, replay_exact):
            exact_errors.append("exact comparison receipts differ")
        canonical_parsed = _parse_state(canonical_exact, canonical_state, "canonical")
        replay_parsed = _parse_state(replay_exact, replay_state, "replay")
        _compare_checkpoint_exact(
            canonical_state,
            replay_state,
            canonical_parsed,
            replay_parsed,
            exact_errors,
        )
    except ReplayComparisonError as error:
        exact_errors.append(str(error))
        canonical_normative = {}
        replay_normative = {}
        canonical_parsed = None
        replay_parsed = None

    exact_errors = sorted(set(exact_errors))
    exact = {
        "rule": "wave0-a3-exact-checkpoint-fields-v1",
        "canonical_exact_sha256": canonical_exact_sha256,
        "replay_exact_sha256": replay_exact_sha256,
        "passed": not exact_errors,
        "errors": exact_errors,
    }
    if exact_errors or canonical_parsed is None or replay_parsed is None:
        numerical_errors.append("numerical comparison requires exact replay structure")
        numerical = _empty_numerical(numerical_errors)
    else:
        try:
            numerical = _compare_numerical(
                canonical_normative,
                canonical_state,
                canonical_parsed,
                replay_normative,
                replay_state,
                replay_parsed,
                numerical_errors,
            )
        except ReplayComparisonError as error:
            numerical_errors.append(str(error))
            numerical = _empty_numerical(numerical_errors)
    errors = tuple(sorted({*exact_errors, *numerical_errors}))
    return ReplayComparison(exact=exact, numerical=numerical, errors=errors)


def _normative(receipt: Mapping[str, object]) -> Mapping[str, object]:
    if not isinstance(receipt, Mapping):
        raise ReplayComparisonError("receipt must be an object")
    return _mapping(receipt.get("normative"), "receipt normative")


def _mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ReplayComparisonError(f"{name} must be an object")
    return value


def _sha256(value: object, name: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ReplayComparisonError(f"{name} is invalid")
    return value


def _parse_state(
    exact: Mapping[str, object], state: CheckpointState, label: str
) -> _ParsedState:
    if not isinstance(state, CheckpointState):
        raise ReplayComparisonError(f"{label} checkpoint type mismatch")
    inventory_value = exact.get("parameter_inventory")
    model_inventory_value = exact.get("model_state_inventory")
    if not isinstance(inventory_value, list) or not inventory_value:
        raise ReplayComparisonError(f"{label} parameter inventory is incomplete")
    if not isinstance(model_inventory_value, list) or not model_inventory_value:
        raise ReplayComparisonError(f"{label} model-state inventory is incomplete")
    inventory: list[Mapping[str, object]] = []
    names: list[str] = []
    groups: dict[str, list[str]] = {name: [] for name in _GROUP_NAMES}
    for value in inventory_value:
        entry = _mapping(value, f"{label} parameter inventory entry")
        if set(entry) != {"name", "group_name", "shape", "dtype"}:
            raise ReplayComparisonError(f"{label} parameter inventory fields mismatch")
        name = entry.get("name")
        group_name = entry.get("group_name")
        if not isinstance(name, str) or group_name not in _GROUP_NAMES:
            raise ReplayComparisonError(
                f"{label} parameter inventory identity mismatch"
            )
        if name in names:
            raise ReplayComparisonError(
                f"{label} parameter inventory contains duplicates"
            )
        names.append(name)
        groups[str(group_name)].append(name)
        inventory.append(entry)
    if any(not groups[name] for name in _GROUP_NAMES):
        raise ReplayComparisonError(f"{label} parameter groups are incomplete")

    model_state = _mapping(state.model_state, f"{label} model state")
    actual_model_inventory: list[dict[str, object]] = []
    trainable = set(names)
    for name, value in model_state.items():
        if not isinstance(name, str) or not isinstance(value, torch.Tensor):
            raise ReplayComparisonError(
                f"{label} model state must contain named tensors"
            )
        actual_model_inventory.append(
            {
                "name": name,
                "shape": list(value.shape),
                "dtype": str(value.dtype).removeprefix("torch."),
                "trainable": name in trainable,
            }
        )
    if actual_model_inventory != model_inventory_value:
        raise ReplayComparisonError(f"{label} model-state inventory mismatch")
    for entry in inventory:
        tensor = model_state.get(str(entry["name"]))
        if (
            not isinstance(tensor, torch.Tensor)
            or list(tensor.shape) != entry.get("shape")
            or str(tensor.dtype).removeprefix("torch.") != entry.get("dtype")
            or not (tensor.is_floating_point() or tensor.is_complex())
        ):
            raise ReplayComparisonError(f"{label} trainable tensor contract mismatch")

    optimizer = _mapping(state.optimizer_state, f"{label} optimizer state")
    if set(optimizer) != {"state", "param_groups"}:
        raise ReplayComparisonError(f"{label} optimizer state fields mismatch")
    optimizer_states = _mapping(optimizer.get("state"), f"{label} optimizer states")
    param_groups = optimizer.get("param_groups")
    if not isinstance(param_groups, list) or len(param_groups) != 2:
        raise ReplayComparisonError(f"{label} optimizer groups mismatch")
    parameter_ids: dict[str, tuple[int, ...]] = {}
    seen_ids: list[int] = []
    for index, expected_name in enumerate(_GROUP_NAMES):
        group = _mapping(param_groups[index], f"{label} optimizer group")
        if group.get("group_name") != expected_name:
            raise ReplayComparisonError(f"{label} optimizer group order mismatch")
        identifiers = group.get("params")
        if (
            not isinstance(identifiers, list)
            or len(identifiers) != len(groups[expected_name])
            or any(type(item) is not int for item in identifiers)
        ):
            raise ReplayComparisonError(f"{label} optimizer parameter mapping mismatch")
        parameter_ids[expected_name] = tuple(identifiers)
        seen_ids.extend(identifiers)
    if len(set(seen_ids)) != len(seen_ids) or set(optimizer_states) != set(seen_ids):
        raise ReplayComparisonError(f"{label} optimizer parameter IDs are ambiguous")
    model_state_map = dict(model_state)
    for group_name in _GROUP_NAMES:
        for name, identifier in zip(
            groups[group_name], parameter_ids[group_name], strict=True
        ):
            member = _mapping(
                optimizer_states.get(identifier), f"{label} optimizer parameter state"
            )
            if set(member) != {"step", "exp_avg", "exp_avg_sq"}:
                raise ReplayComparisonError(f"{label} AdamW state fields mismatch")
            step = member.get("step")
            if (
                not isinstance(step, torch.Tensor)
                or step.numel() != 1
                or not bool(torch.isfinite(step).all())
            ):
                raise ReplayComparisonError(f"{label} AdamW step is invalid")
            parameter = model_state_map[name]
            for moment_name in _MOMENT_NAMES:
                moment = member.get(moment_name)
                if (
                    not isinstance(moment, torch.Tensor)
                    or moment.shape != parameter.shape
                    or moment.dtype != parameter.dtype
                ):
                    raise ReplayComparisonError(
                        f"{label} AdamW {moment_name} tensor mismatch"
                    )
                if not bool(torch.isfinite(moment).all()):
                    raise ReplayComparisonError(
                        f"{label} AdamW {moment_name} tensor is non-finite"
                    )
    return _ParsedState(
        inventory=tuple(inventory),
        parameter_names={name: tuple(groups[name]) for name in _GROUP_NAMES},
        parameter_ids=parameter_ids,
    )


def _compare_checkpoint_exact(
    canonical: CheckpointState,
    replay: CheckpointState,
    canonical_parsed: _ParsedState,
    replay_parsed: _ParsedState,
    errors: list[str],
) -> None:
    if canonical_parsed.parameter_names != replay_parsed.parameter_names:
        errors.append("ordered trainable parameter mapping differs")
    for name, canonical_value, replay_value in (
        ("epoch", canonical.epoch, replay.epoch),
        ("step", canonical.step, replay.step),
        (
            "sampler_order_digest",
            canonical.sampler_order_digest,
            replay.sampler_order_digest,
        ),
        ("scheduler_state", canonical.scheduler_state, replay.scheduler_state),
        ("scaler_state", canonical.scaler_state, replay.scaler_state),
        ("rng_state", canonical.rng_state, replay.rng_state),
    ):
        if not _values_equal(canonical_value, replay_value):
            errors.append(f"{name} differs")

    canonical_model = _mapping(canonical.model_state, "canonical model state")
    replay_model = _mapping(replay.model_state, "replay model state")
    if list(canonical_model) != list(replay_model):
        errors.append("model state key order differs")
        return
    trainable = {
        name for names in canonical_parsed.parameter_names.values() for name in names
    }
    for name in canonical_model:
        first = canonical_model[name]
        second = replay_model[name]
        if not isinstance(first, torch.Tensor) or not isinstance(second, torch.Tensor):
            errors.append(f"model state {name} is not a tensor")
            continue
        if first.shape != second.shape or first.dtype != second.dtype:
            errors.append(f"model state {name} structure differs")
            continue
        if (name not in trainable or not first.is_floating_point()) and not torch.equal(
            first, second
        ):
            errors.append(f"exact model state {name} differs")

    canonical_optimizer = _mapping(canonical.optimizer_state, "canonical optimizer")
    replay_optimizer = _mapping(replay.optimizer_state, "replay optimizer")
    canonical_groups = canonical_optimizer.get("param_groups")
    replay_groups = replay_optimizer.get("param_groups")
    if not _values_equal(canonical_groups, replay_groups):
        errors.append("optimizer parameter groups differ")
    canonical_states = _mapping(canonical_optimizer.get("state"), "canonical states")
    replay_states = _mapping(replay_optimizer.get("state"), "replay states")
    if list(canonical_states) != list(replay_states):
        errors.append("optimizer state key order differs")
        return
    for identifier in canonical_states:
        first = _mapping(canonical_states[identifier], "canonical parameter state")
        second = _mapping(replay_states[identifier], "replay parameter state")
        if not _values_equal(first.get("step"), second.get("step")):
            errors.append(f"optimizer step differs for parameter {identifier}")
        for moment_name in _MOMENT_NAMES:
            first_moment = first.get(moment_name)
            second_moment = second.get(moment_name)
            if (
                not isinstance(first_moment, torch.Tensor)
                or not isinstance(second_moment, torch.Tensor)
                or first_moment.shape != second_moment.shape
                or first_moment.dtype != second_moment.dtype
            ):
                errors.append(
                    f"optimizer {moment_name} structure differs for parameter {identifier}"
                )


def _compare_numerical(
    canonical_normative: Mapping[str, object],
    canonical_state: CheckpointState,
    canonical_parsed: _ParsedState,
    replay_normative: Mapping[str, object],
    replay_state: CheckpointState,
    replay_parsed: _ParsedState,
    errors: list[str],
) -> dict[str, object]:
    canonical_step = _mapping(canonical_normative.get("step"), "canonical step")
    replay_step = _mapping(replay_normative.get("step"), "replay step")
    canonical_gradient = _finite_number(
        canonical_step.get("gradient_norm"), "canonical gradient norm"
    )
    replay_gradient = _finite_number(
        replay_step.get("gradient_norm"), "replay gradient norm"
    )
    gradient_passed = math.isclose(
        canonical_gradient,
        replay_gradient,
        rel_tol=GRADIENT_REL_TOL,
        abs_tol=GRADIENT_ABS_TOL,
    )
    gradient = {
        "canonical": canonical_gradient,
        "replay": replay_gradient,
        "rel_tol": GRADIENT_REL_TOL,
        "abs_tol": GRADIENT_ABS_TOL,
        "passed": gradient_passed,
    }
    if not gradient_passed:
        errors.append("gradient norm exceeds registered tolerance")

    canonical_updates = _mapping(
        canonical_normative.get("update_groups"), "canonical update groups"
    )
    replay_updates = _mapping(
        replay_normative.get("update_groups"), "replay update groups"
    )
    canonical_model = _mapping(canonical_state.model_state, "canonical model state")
    replay_model = _mapping(replay_state.model_state, "replay model state")
    model_metrics: dict[str, object] = {}
    for group_name in _GROUP_NAMES:
        canonical_norm = _update_norm(canonical_updates, group_name, "canonical")
        replay_norm = _update_norm(replay_updates, group_name, "replay")
        difference_squared = 0.0
        for name in canonical_parsed.parameter_names[group_name]:
            first = canonical_model[name]
            second = replay_model[name]
            assert isinstance(first, torch.Tensor)
            assert isinstance(second, torch.Tensor)
            difference = first.detach().cpu().to(
                torch.float64
            ) - second.detach().cpu().to(torch.float64)
            if not bool(torch.isfinite(difference).all()):
                raise ReplayComparisonError(f"{group_name} model update is non-finite")
            difference_squared += float(torch.sum(difference * difference))
        difference_norm = math.sqrt(difference_squared)
        metrics = _derived_vector_metrics(canonical_norm, replay_norm, difference_norm)
        model_metrics[group_name] = metrics
        if not metrics["passed"]:
            errors.append(f"{group_name} model update exceeds registered bounds")

    canonical_optimizer = _mapping(
        canonical_state.optimizer_state, "canonical optimizer"
    )
    replay_optimizer = _mapping(replay_state.optimizer_state, "replay optimizer")
    canonical_states = _mapping(canonical_optimizer.get("state"), "canonical states")
    replay_states = _mapping(replay_optimizer.get("state"), "replay states")
    optimizer_metrics: dict[str, object] = {}
    for group_name in _GROUP_NAMES:
        group_metrics: dict[str, object] = {}
        for moment_name in _MOMENT_NAMES:
            canonical_tensors: list[torch.Tensor] = []
            replay_tensors: list[torch.Tensor] = []
            for canonical_id, replay_id in zip(
                canonical_parsed.parameter_ids[group_name],
                replay_parsed.parameter_ids[group_name],
                strict=True,
            ):
                canonical_member = _mapping(
                    canonical_states[canonical_id], "canonical optimizer member"
                )
                replay_member = _mapping(
                    replay_states[replay_id], "replay optimizer member"
                )
                canonical_tensors.append(canonical_member[moment_name])
                replay_tensors.append(replay_member[moment_name])
            metrics = _direct_vector_metrics(canonical_tensors, replay_tensors)
            group_metrics[moment_name] = metrics
            if not metrics["passed"]:
                errors.append(
                    f"{group_name} AdamW {moment_name} exceeds registered bounds"
                )
        optimizer_metrics[group_name] = group_metrics

    unique_errors = sorted(set(errors))
    return {
        "rule": "wave0-a3-same-host-float64-bounds-v1",
        "thresholds": {
            "gradient_rel_tol": GRADIENT_REL_TOL,
            "gradient_abs_tol": GRADIENT_ABS_TOL,
            "vector_relative_l2_max": VECTOR_REL_L2_LIMIT,
            "vector_cosine_min": VECTOR_COSINE_MINIMUM,
        },
        "gradient_norm": gradient,
        "model_updates": model_metrics,
        "optimizer_states": optimizer_metrics,
        "passed": not unique_errors,
        "errors": unique_errors,
    }


def _update_norm(groups: Mapping[str, object], group_name: str, label: str) -> float:
    group = _mapping(groups.get(group_name), f"{label} {group_name} update group")
    if set(group) != {"l2_norm"}:
        raise ReplayComparisonError(
            f"{label} {group_name} update group fields mismatch"
        )
    value = _finite_number(group.get("l2_norm"), f"{label} {group_name} update norm")
    if value <= 0.0:
        raise ReplayComparisonError(
            f"{label} {group_name} update norm must be positive"
        )
    return value


def _derived_vector_metrics(
    canonical_norm: float, replay_norm: float, difference_norm: float
) -> dict[str, object]:
    if (
        any(
            not math.isfinite(value) or value < 0.0
            for value in (canonical_norm, replay_norm, difference_norm)
        )
        or canonical_norm == 0.0
        or replay_norm == 0.0
    ):
        raise ReplayComparisonError("model update vector norm is zero or non-finite")
    relative_l2 = difference_norm / max(canonical_norm, replay_norm)
    cosine_raw = (
        canonical_norm * canonical_norm
        + replay_norm * replay_norm
        - difference_norm * difference_norm
    ) / (2.0 * canonical_norm * replay_norm)
    if (
        not math.isfinite(cosine_raw)
        or cosine_raw < -1.000000000001
        or cosine_raw > 1.000000000001
    ):
        raise ReplayComparisonError("model update cosine cannot be derived")
    cosine = min(1.0, max(-1.0, cosine_raw))
    passed = relative_l2 <= VECTOR_REL_L2_LIMIT and cosine >= VECTOR_COSINE_MINIMUM
    return {
        "canonical_l2": canonical_norm,
        "replay_l2": replay_norm,
        "difference_l2": difference_norm,
        "relative_l2": relative_l2,
        "relative_l2_max": VECTOR_REL_L2_LIMIT,
        "cosine": cosine,
        "cosine_min": VECTOR_COSINE_MINIMUM,
        "passed": passed,
    }


def _direct_vector_metrics(
    canonical_tensors: Sequence[torch.Tensor], replay_tensors: Sequence[torch.Tensor]
) -> dict[str, object]:
    if not canonical_tensors or len(canonical_tensors) != len(replay_tensors):
        raise ReplayComparisonError("optimizer state tensor inventory mismatch")
    canonical_squared = 0.0
    replay_squared = 0.0
    difference_squared = 0.0
    dot = 0.0
    for first, second in zip(canonical_tensors, replay_tensors, strict=True):
        if (
            not isinstance(first, torch.Tensor)
            or not isinstance(second, torch.Tensor)
            or first.shape != second.shape
            or first.dtype != second.dtype
        ):
            raise ReplayComparisonError("optimizer state tensor structure mismatch")
        first64 = first.detach().cpu().to(torch.float64)
        second64 = second.detach().cpu().to(torch.float64)
        if not bool(torch.isfinite(first64).all()) or not bool(
            torch.isfinite(second64).all()
        ):
            raise ReplayComparisonError("optimizer state tensor is non-finite")
        canonical_squared += float(torch.sum(first64 * first64))
        replay_squared += float(torch.sum(second64 * second64))
        difference = first64 - second64
        difference_squared += float(torch.sum(difference * difference))
        dot += float(torch.sum(first64 * second64))
    canonical_norm = math.sqrt(canonical_squared)
    replay_norm = math.sqrt(replay_squared)
    difference_norm = math.sqrt(difference_squared)
    if canonical_norm == 0.0 or replay_norm == 0.0:
        raise ReplayComparisonError("optimizer state vector norm is zero")
    relative_l2 = difference_norm / max(canonical_norm, replay_norm)
    cosine = dot / (canonical_norm * replay_norm)
    if not math.isfinite(relative_l2) or not math.isfinite(cosine):
        raise ReplayComparisonError("optimizer state vector metric is non-finite")
    cosine = min(1.0, max(-1.0, cosine))
    passed = relative_l2 <= VECTOR_REL_L2_LIMIT and cosine >= VECTOR_COSINE_MINIMUM
    return {
        "canonical_l2": canonical_norm,
        "replay_l2": replay_norm,
        "difference_l2": difference_norm,
        "relative_l2": relative_l2,
        "relative_l2_max": VECTOR_REL_L2_LIMIT,
        "cosine": cosine,
        "cosine_min": VECTOR_COSINE_MINIMUM,
        "passed": passed,
    }


def _empty_numerical(errors: Sequence[str]) -> dict[str, object]:
    return {
        "rule": "wave0-a3-same-host-float64-bounds-v1",
        "thresholds": {
            "gradient_rel_tol": GRADIENT_REL_TOL,
            "gradient_abs_tol": GRADIENT_ABS_TOL,
            "vector_relative_l2_max": VECTOR_REL_L2_LIMIT,
            "vector_cosine_min": VECTOR_COSINE_MINIMUM,
        },
        "gradient_norm": {},
        "model_updates": {},
        "optimizer_states": {},
        "passed": False,
        "errors": sorted(set(errors)),
    }


def _finite_number(value: object, name: str) -> float:
    if type(value) not in (int, float) or not math.isfinite(float(value)):
        raise ReplayComparisonError(f"{name} must be finite")
    return float(value)


def _values_equal(first: object, second: object) -> bool:
    if isinstance(first, torch.Tensor) or isinstance(second, torch.Tensor):
        return (
            isinstance(first, torch.Tensor)
            and isinstance(second, torch.Tensor)
            and first.shape == second.shape
            and first.dtype == second.dtype
            and torch.equal(first.cpu(), second.cpu())
        )
    if isinstance(first, Mapping) or isinstance(second, Mapping):
        return (
            isinstance(first, Mapping)
            and isinstance(second, Mapping)
            and list(first) == list(second)
            and all(_values_equal(first[name], second[name]) for name in first)
        )
    if isinstance(first, (list, tuple)) or isinstance(second, (list, tuple)):
        return (
            type(first) is type(second)
            and len(first) == len(second)
            and all(
                _values_equal(left, right)
                for left, right in zip(first, second, strict=True)
            )
        )
    return type(first) is type(second) and first == second
