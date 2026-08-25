from __future__ import annotations

import copy
import math
from collections.abc import Mapping

import torch

from vision_active_learning_loop.gates.numerical_replay import compare_replay
from vision_active_learning_loop.training.checkpoint_io import CheckpointState

HASH = "a" * 64


def _inventory() -> list[dict[str, object]]:
    return [
        {
            "name": "detector.weight",
            "group_name": "detector",
            "shape": [2],
            "dtype": "float32",
        },
        {
            "name": "model.backbone.weight",
            "group_name": "backbone",
            "shape": [2],
            "dtype": "float32",
        },
    ]


def _model_inventory() -> list[dict[str, object]]:
    return [
        {
            "name": "detector.weight",
            "shape": [2],
            "dtype": "float32",
            "trainable": True,
        },
        {
            "name": "model.backbone.weight",
            "shape": [2],
            "dtype": "float32",
            "trainable": True,
        },
        {
            "name": "running_mean",
            "shape": [1],
            "dtype": "float32",
            "trainable": False,
        },
        {
            "name": "running_count",
            "shape": [],
            "dtype": "int64",
            "trainable": False,
        },
    ]


def _receipt(
    *,
    detector_norm: float = 1.0,
    backbone_norm: float = 2.0,
    gradient_norm: float = 0.75,
) -> dict[str, object]:
    exact = {
        "rule": "wave0-a3-exact-replay-sha256-v1",
        "parameter_digest_before": "0" * 64,
        "parameter_inventory": _inventory(),
        "ordered_loss_hex": [(3.25).hex()],
        "optimizer_groups": [
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
        ],
        "scheduler_state_before_sha256": "1" * 64,
        "sampler_order_digest": "2" * 64,
        "semantic_input_digests": {
            "fixture_sha256": "3" * 64,
            "synthetic_target_sha256": "4" * 64,
        },
        "checkpoint_epoch": 0,
        "checkpoint_step": 1,
        "model_state_inventory": _model_inventory(),
        "state_digests": {
            "scheduler": "4" * 64,
            "scaler": "5" * 64,
            "rng": "6" * 64,
            "sampler": "2" * 64,
        },
        "allowlisted_backward": {
            "operation_identifier": "grid_sampler_2d_backward_cuda"
        },
        "sha256": HASH,
    }
    return {
        "normative": {
            "exact_comparison": exact,
            "step": {"gradient_norm": gradient_norm},
            "update_groups": {
                "detector": {"l2_norm": detector_norm},
                "backbone": {"l2_norm": backbone_norm},
            },
        }
    }


def _optimizer_state(
    detector: torch.Tensor, backbone: torch.Tensor
) -> dict[str, object]:
    return {
        "state": {
            0: {
                "step": torch.tensor(1.0),
                "exp_avg": detector.clone(),
                "exp_avg_sq": detector.square().mul(0.01),
            },
            1: {
                "step": torch.tensor(1.0),
                "exp_avg": backbone.clone(),
                "exp_avg_sq": backbone.square().mul(0.01),
            },
        },
        "param_groups": [
            {
                "group_name": "detector",
                "lr": 1e-4,
                "weight_decay": 1e-4,
                "params": [0],
            },
            {
                "group_name": "backbone",
                "lr": 1e-5,
                "weight_decay": 1e-4,
                "params": [1],
            },
        ],
    }


def _state(
    *,
    detector: tuple[float, float] = (1.0, 0.0),
    backbone: tuple[float, float] = (0.0, 2.0),
    moment_scale: float = 1.0,
) -> CheckpointState:
    detector_tensor = torch.tensor(detector, dtype=torch.float32)
    backbone_tensor = torch.tensor(backbone, dtype=torch.float32)
    return CheckpointState(
        model_state={
            "detector.weight": detector_tensor,
            "model.backbone.weight": backbone_tensor,
            "running_mean": torch.tensor([0.5], dtype=torch.float32),
            "running_count": torch.tensor(1, dtype=torch.int64),
        },
        optimizer_state=_optimizer_state(
            detector_tensor.mul(moment_scale), backbone_tensor.mul(moment_scale)
        ),
        scheduler_state={"last_epoch": 1, "_step_count": 2},
        scaler_state=None,
        epoch=0,
        step=1,
        sampler_order_digest="2" * 64,
        rng_state={"seed": 17, "stream": torch.tensor([1, 2], dtype=torch.uint8)},
        input_digests={"model_contract_receipt": "3" * 64},
    )


def _metric(result: Mapping[str, object], *path: str) -> object:
    value: object = result
    for name in path:
        assert isinstance(value, Mapping)
        value = value[name]
    return value


def test_equal_checkpoint_replay_passes_every_exact_and_numerical_gate() -> None:
    result = compare_replay(_receipt(), _state(), _receipt(), _state())

    assert result.errors == ()
    assert result.exact["passed"] is True
    assert result.exact["canonical_exact_sha256"] == HASH
    assert result.exact["replay_exact_sha256"] == HASH
    assert result.numerical["passed"] is True
    assert _metric(result.numerical, "gradient_norm", "passed") is True
    assert _metric(result.numerical, "model_updates", "detector", "relative_l2") == 0.0
    assert _metric(result.numerical, "model_updates", "backbone", "cosine") == 1.0
    assert math.isfinite(
        float(
            _metric(
                result.numerical,
                "optimizer_states",
                "detector",
                "exp_avg_sq",
                "cosine",
            )
        )
    )


def test_gradient_norm_uses_both_registered_isclose_tolerances() -> None:
    tolerance = max(0.75 * 1e-5, 1e-7)
    accepted = compare_replay(
        _receipt(),
        _state(),
        _receipt(gradient_norm=0.75 + tolerance * 0.99),
        _state(),
    )
    rejected = compare_replay(
        _receipt(),
        _state(),
        _receipt(gradient_norm=0.75 + tolerance * 1.01),
        _state(),
    )

    assert _metric(accepted.numerical, "gradient_norm", "passed") is True
    assert not accepted.errors
    assert _metric(rejected.numerical, "gradient_norm", "passed") is False
    assert "gradient norm exceeds registered tolerance" in rejected.errors


def test_model_update_vectors_use_recorded_norms_and_checkpoint_difference() -> None:
    within_detector = (1.0, 0.0005)
    outside_detector = (1.0, 0.002)
    within_norm = math.hypot(*within_detector)
    outside_norm = math.hypot(*outside_detector)

    within = compare_replay(
        _receipt(),
        _state(),
        _receipt(detector_norm=within_norm),
        _state(detector=within_detector),
    )
    outside = compare_replay(
        _receipt(),
        _state(),
        _receipt(detector_norm=outside_norm),
        _state(detector=outside_detector),
    )

    assert _metric(within.numerical, "model_updates", "detector", "passed") is True
    assert (
        float(_metric(within.numerical, "model_updates", "detector", "relative_l2"))
        < 1e-3
    )
    assert _metric(outside.numerical, "model_updates", "detector", "passed") is False
    assert "detector model update exceeds registered bounds" in outside.errors


def test_adamw_moments_are_compared_by_group_and_state_name() -> None:
    within = _state(moment_scale=1.0005)
    outside = _state(moment_scale=1.01)

    accepted = compare_replay(_receipt(), _state(), _receipt(), within)
    rejected = compare_replay(_receipt(), _state(), _receipt(), outside)

    assert (
        _metric(
            accepted.numerical,
            "optimizer_states",
            "detector",
            "exp_avg",
            "passed",
        )
        is True
    )
    assert (
        _metric(
            rejected.numerical,
            "optimizer_states",
            "backbone",
            "exp_avg_sq",
            "passed",
        )
        is False
    )
    assert "backbone AdamW exp_avg_sq exceeds registered bounds" in rejected.errors


def test_rotated_adamw_moment_fails_the_cosine_gate() -> None:
    replay = _state()
    optimizer = replay.optimizer_state
    assert isinstance(optimizer, dict)
    states = optimizer["state"]
    assert isinstance(states, dict)
    member = states[0]
    assert isinstance(member, dict)
    member["exp_avg"] = torch.tensor([0.0, 1.0], dtype=torch.float32)

    result = compare_replay(_receipt(), _state(), _receipt(), replay)

    assert (
        _metric(
            result.numerical,
            "optimizer_states",
            "detector",
            "exp_avg",
            "cosine",
        )
        == 0.0
    )
    assert "detector AdamW exp_avg exceeds registered bounds" in result.errors


def test_exact_receipt_identity_drift_stops_numerical_comparison() -> None:
    replay_receipt = _receipt()
    normative = replay_receipt["normative"]
    assert isinstance(normative, dict)
    exact = normative["exact_comparison"]
    assert isinstance(exact, dict)
    exact["sha256"] = "b" * 64

    result = compare_replay(_receipt(), _state(), replay_receipt, _state())

    assert result.exact["passed"] is False
    assert result.numerical["passed"] is False
    assert "exact comparison receipts differ" in result.errors


def test_nontraining_float_and_integer_state_must_be_exact() -> None:
    replay = _state()
    model_state = replay.model_state
    assert isinstance(model_state, dict)
    model_state["running_mean"] = torch.tensor([0.5001], dtype=torch.float32)
    model_state["running_count"] = torch.tensor(2, dtype=torch.int64)

    result = compare_replay(_receipt(), _state(), _receipt(), replay)

    assert "exact model state running_mean differs" in result.errors
    assert "exact model state running_count differs" in result.errors


def test_discrete_checkpoint_state_must_be_exact() -> None:
    replay = _state()
    object.__setattr__(replay, "sampler_order_digest", "9" * 64)
    object.__setattr__(replay, "scheduler_state", {"last_epoch": 2, "_step_count": 2})

    result = compare_replay(_receipt(), _state(), _receipt(), replay)

    assert "sampler_order_digest differs" in result.errors
    assert "scheduler_state differs" in result.errors


def test_missing_nonfinite_or_zero_optimizer_state_fails_closed() -> None:
    missing = _state()
    nonfinite = _state()
    zero = _state()
    for state, mutation in (
        (missing, "missing"),
        (nonfinite, "nonfinite"),
        (zero, "zero"),
    ):
        optimizer = state.optimizer_state
        assert isinstance(optimizer, dict)
        states = optimizer["state"]
        assert isinstance(states, dict)
        member = states[0]
        assert isinstance(member, dict)
        if mutation == "missing":
            member.pop("exp_avg_sq")
        elif mutation == "nonfinite":
            member["exp_avg"] = torch.tensor([float("nan"), 0.0])
        else:
            member["exp_avg"] = torch.zeros(2)

    missing_result = compare_replay(_receipt(), _state(), _receipt(), missing)
    nonfinite_result = compare_replay(_receipt(), _state(), _receipt(), nonfinite)
    zero_result = compare_replay(_receipt(), _state(), _receipt(), zero)

    assert any("AdamW state fields mismatch" in item for item in missing_result.errors)
    assert any("non-finite" in item for item in nonfinite_result.errors)
    assert any("vector norm is zero" in item for item in zero_result.errors)


def test_reordered_mistyped_or_ambiguous_checkpoint_structure_fails_closed() -> None:
    reordered = copy.deepcopy(_state())
    wrong_dtype = copy.deepcopy(_state())
    duplicate_id = copy.deepcopy(_state())
    object.__setattr__(
        reordered,
        "model_state",
        dict(reversed(list(reordered.model_state.items()))),
    )
    wrong_dtype_state = wrong_dtype.model_state
    assert isinstance(wrong_dtype_state, dict)
    wrong_dtype_state["detector.weight"] = wrong_dtype_state["detector.weight"].double()
    optimizer = duplicate_id.optimizer_state
    assert isinstance(optimizer, dict)
    groups = optimizer["param_groups"]
    assert isinstance(groups, list)
    groups[1]["params"] = [0]

    reordered_result = compare_replay(_receipt(), _state(), _receipt(), reordered)
    wrong_dtype_result = compare_replay(_receipt(), _state(), _receipt(), wrong_dtype)
    duplicate_result = compare_replay(_receipt(), _state(), _receipt(), duplicate_id)

    assert any(
        "model-state inventory mismatch" in item for item in reordered_result.errors
    )
    assert any(
        "model-state inventory mismatch" in item for item in wrong_dtype_result.errors
    )
    assert any(
        "parameter IDs are ambiguous" in item for item in duplicate_result.errors
    )


def test_nonfinite_gradient_and_zero_recorded_update_norm_fail_closed() -> None:
    nonfinite = compare_replay(
        _receipt(),
        _state(),
        _receipt(gradient_norm=float("nan")),
        _state(),
    )
    zero = compare_replay(_receipt(), _state(), _receipt(detector_norm=0.0), _state())

    assert any("gradient norm must be finite" in item for item in nonfinite.errors)
    assert any("update norm must be positive" in item for item in zero.errors)
