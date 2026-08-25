from __future__ import annotations

import copy
import json
import warnings
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

import vision_active_learning_loop.probes.training_feasibility as feasibility_probe
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    _receipt_content_sha256,
    _stored_receipt_sha256,
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.probes.training_feasibility import (
    FeasibilityError,
    StepObservation,
    _prepare_labeled_batch,
    configure_determinism,
    evaluate_step_observation,
    resolve_cli_paths,
    validate_live_environment_evidence,
)

from ..artifacts.test_receipts import build_valid_model_contract_receipt

HASH = "a" * 64
GRID_WARNING = (
    "grid_sampler_2d_backward_cuda does not have a deterministic implementation."
)


def _emit_grid_sample_warnings(count: int) -> None:
    for _ in range(count):
        warnings.warn(
            "grid_sampler_2d_backward_cuda does not have a deterministic "
            "implementation, but deterministic algorithms were requested",
            UserWarning,
            stacklevel=2,
        )


def _emit_warning_messages(
    messages: tuple[str, ...], category: type[Warning] = UserWarning
) -> None:
    for message in messages:
        warnings.warn(message, category, stacklevel=2)


class _TinyGroupedModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.detector = torch.nn.Linear(2, 1)
        self.model = torch.nn.Module()
        self.model.backbone = torch.nn.Linear(2, 1)


def _parent_environment() -> dict[str, object]:
    return {
        "schema_version": 1,
        "python": "3.12.11",
        "uv": "0.8.15",
        "scipy": "1.18.0",
        "torch": "2.12.0+cu126",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "pycocotools": "2.0.10",
        "cuda_runtime": "12.6",
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "gpu_uuid": "GPU-11111111-1111-1111-1111-111111111111",
        "driver": "591.86",
        "os": "Linux",
        "wsl": True,
        "container_image_digest": "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356",
        "runtime_image_digest": "sha256:7ba1dd9364de4bdfc60ee14c42f3441d736e46fcd41128992c3cd49c67059ae2",
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
        "data_root_unset": True,
        "status": "PASS",
        "errors": [],
        "torch_execution": {
            "cuda_available": True,
            "device_count": 1,
            "selected_index": 0,
            "selected_name": "NVIDIA GeForce RTX 4090",
            "torch_selected_gpu_uuid": "11111111-1111-1111-1111-111111111111",
            "selected_device": "cuda:0",
            "nvidia_smi_gpu_name": "NVIDIA GeForce RTX 4090",
            "nvidia_smi_gpu_uuid": "GPU-11111111-1111-1111-1111-111111111111",
            "model_device": "cuda:0",
            "pixel_values_device": "cuda:0",
            "pixel_mask_device": "cuda:0",
            "logits_device": "cuda:0",
            "final_boxes_device": "cuda:0",
            "penultimate_boxes_device": "cuda:0",
            "intermediate_boxes_device": "cuda:0",
        },
    }


def _environment_evidence() -> dict[str, object]:
    parent = _parent_environment()
    observed = {
        name: parent[name]
        for name in (
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
    }
    observed["data_root_unset"] = True
    return {
        "observed": observed,
        "selected_cuda": {
            "cuda_available": True,
            "device_count": 1,
            "selected_index": 0,
            "selected_name": "NVIDIA GeForce RTX 4090",
            "selected_uuid": "11111111-1111-1111-1111-111111111111",
            "selected_device": "cuda:0",
        },
        "parent_environment_sha256": canonical_json_sha256(parent),
    }


def _warning_evidence() -> feasibility_probe.BackwardWarningEvidence:
    operation = "grid_sampler_2d_backward_cuda"
    message = f"{operation} does not have a deterministic implementation."
    return feasibility_probe.BackwardWarningEvidence(
        operation_identifier=operation,
        expected_count=9,
        observed_count=9,
        raw_warnings=(message,) * 9,
        warning_categories=("UserWarning",) * 9,
        operation_identifiers=(operation,) * 9,
        source_sha256={
            "torch_init": (
                "b508de5a66ebc368fc8fa2161b1e0e88ae0034d9d9540e7c020460237a5464a9"
            ),
            "torch_nn_functional": (
                "e409a97896241e0dfb8c23fbf1f09967ecf5e65ec9626aec0d97d9cc5d727d50"
            ),
            "transformers_modeling_rt_detr": (
                "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3"
            ),
        },
        strict_mode_restored=True,
    )


def _observation(**changes: object) -> StepObservation:
    values: dict[str, object] = {
        "ordered_losses": (3.25,),
        "finite_loss": True,
        "finite_gradients": True,
        "parameter_changed": True,
        "gradient_norm": 0.75,
        "peak_allocated_bytes": 8 * 1024**3,
        "peak_reserved_bytes": 9 * 1024**3,
        "wall_seconds": 1.25,
        "gpu_seconds": 1.0,
        "cuda_matmul_allow_tf32": False,
        "cudnn_allow_tf32": False,
        "cudnn_benchmark": False,
        "deterministic_algorithms": True,
        "deterministic_debug_mode": 2,
        "cublas_workspace_config": ":4096:8",
        "bf16_supported": True,
        "bf16_autocast_enabled": True,
        "allowlisted_backward": _warning_evidence(),
        "device": "cuda:0",
        "live_model_state_digest_after": "7" * 64,
        "trainable_parameter_count": 2,
        "parameter_digest_before": "0" * 64,
        "parameter_digest_after": "1" * 64,
        "parameter_inventory": (
            {
                "name": "detector.weight",
                "group_name": "detector",
                "shape": [4, 8],
                "dtype": "float32",
            },
            {
                "name": "model.backbone.weight",
                "group_name": "backbone",
                "shape": [8, 8],
                "dtype": "float32",
            },
        ),
        "update_groups": {"detector": 0.125, "backbone": 0.0625},
        "optimizer_groups": (
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
        ),
        "scheduler_state_before_sha256": "8" * 64,
        "sampler_order_digest": "6" * 64,
        "input_digests": {"model_contract_receipt": "9" * 64},
        "semantic_input_digests": {
            "fixture_sha256": (
                "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f"
            ),
            "synthetic_target_sha256": (
                "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198"
            ),
        },
        "checkpoint_epoch": 0,
        "checkpoint_step": 1,
        "model_state_inventory": (
            {
                "name": "detector.weight",
                "shape": [4, 8],
                "dtype": "float32",
                "trainable": True,
            },
            {
                "name": "running_count",
                "shape": [],
                "dtype": "int64",
                "trainable": False,
            },
        ),
        "state_digests": {
            "model": "7" * 64,
            "optimizer": "2" * 64,
            "scheduler": "3" * 64,
            "scaler": "4" * 64,
            "rng": "5" * 64,
            "sampler": "6" * 64,
        },
        "checkpoint_state": None,
    }
    values.update(changes)
    return StepObservation(**values)


def _receipt() -> dict[str, object]:
    observation = _observation()
    comparison = feasibility_probe.exact_comparison(observation)
    environment = _environment_evidence()
    parent = build_valid_model_contract_receipt()
    parent["metadata"]["receipt_content_sha256"] = _receipt_content_sha256(parent)
    parent_normative = parent["normative"]
    return {
        "receipt_type": "feasibility",
        "schema_version": 2,
        "normative": {
            "model_sha256": parent_normative["model_sha256"],
            "config_sha256": parent_normative["config_sha256"],
            "source_sha256": parent_normative["source_sha256"],
            "processor_sha256": parent_normative["processor_sha256"],
            "fixture_sha256": parent_normative["fixture_sha256"],
            "loss_source_sha256": parent_normative["loss_source_sha256"],
            "synthetic_target_sha256": parent_normative["synthetic_target_sha256"],
            "probe_sha256": feasibility_probe._probe_hash(),
            "environment_sha256": canonical_json_sha256(environment),
            "parent_environment_sha256": environment["parent_environment_sha256"],
            "environment": environment,
            "model_contract_receipt_sha256": _stored_receipt_sha256(parent),
            "parent_model_contract": parent,
            "checkpoint_sha256": HASH,
            "checkpoint_state_sha256": HASH,
            "observed_shapes": {
                "pixel_values": [2, 3, 640, 640],
                "pixel_mask": [2, 640, 640],
            },
            "invariants": {
                "adamw_update": True,
                "batch_size_two": True,
                "bf16_autocast": True,
                "bf16_supported": True,
                "checkpoint_content_verified": True,
                "checkpoint_round_trip": True,
                "cublas_workspace_configured": True,
                "cudnn_benchmark_disabled": True,
                "canonical_environment": True,
                "deterministic_algorithms": True,
                "allowlisted_backward_verified": True,
                "strict_deterministic_error_mode_restored": True,
                "exact_scipy": True,
                "finite_gradients": True,
                "finite_loss": True,
                "gradient_clip_0_1": True,
                "parameter_changed": True,
                "peak_allocated_vram_within_22_gib": True,
                "resume_state_verified": True,
                "seed_17": True,
                "synthetic_labels_only": True,
                "tf32_disabled": True,
            },
            "ordered_losses": list(observation.ordered_losses),
            "state_digests": dict(observation.state_digests),
            "allowlisted_backward": feasibility_probe._allowlisted_backward_document(
                observation.allowlisted_backward
            ),
            "parameter_inventory": [
                dict(item) for item in observation.parameter_inventory
            ],
            "update_groups": {
                name: {"l2_norm": observation.update_groups[name]}
                for name in ("detector", "backbone")
            },
            "exact_comparison": comparison,
            "step": {
                "loss_hex": (3.25).hex(),
                "gradient_norm": 0.75,
                "finite_loss": True,
                "finite_gradients": True,
                "parameter_digest_rule": "ordered-trainable-named-parameters-sha256-v1",
                "trainable_parameter_count": 2,
                "parameter_digest_before": "0" * 64,
                "parameter_digest_after": "1" * 64,
            },
            "checkpoint": {
                "file_sha256": HASH,
                "verified_file_sha256": HASH,
                "live_model_state_sha256_after_step": observation.live_model_state_digest_after,
                "state_sha256_before_save": HASH,
                "state_sha256_after_load": HASH,
                "state_digests_before_save": dict(observation.state_digests),
                "state_digests_after_load": dict(observation.state_digests),
                "state_digests_after_restore": dict(observation.state_digests),
                "input_digests_verified": True,
            },
            "synthetic_labels": {
                "item_ids": ["wide-gradient", "tall-checker"],
                "class_labels": [[0], [3]],
                "boxes_per_image": [1, 1],
                "source": "tracked-synthetic-fixture-geometry-v1",
            },
            "runtime": {
                "seed": 17,
                "device": "cuda:0",
                "precision": "bfloat16",
                "tf32": False,
                "cuda_matmul_allow_tf32": False,
                "cudnn_allow_tf32": False,
                "cudnn_benchmark": False,
                "deterministic_algorithms": True,
                "deterministic_debug_mode": 2,
                "cublas_workspace_config": ":4096:8",
                "bf16_supported": True,
                "bf16_autocast_enabled": True,
                "allowlisted_grid_sample_backward": True,
                "strict_deterministic_error_mode_restored": True,
            },
            "recipe": {
                "seed": 17,
                "batch_size": 2,
                "optimizer": "AdamW",
                "detector_learning_rate": 1e-4,
                "backbone_learning_rate": 1e-5,
                "weight_decay": 1e-4,
                "gradient_clip_norm": 0.1,
                "fixture_set": "wave0-rtdetr-contract",
            },
            "timing": {
                "wall_seconds": 1.25,
                "gpu_seconds": 1.0,
                "checkpoint_write_seconds": 0.2,
                "checkpoint_load_seconds": 0.1,
            },
            "vram": {
                "peak_allocated_bytes": 8 * 1024**3,
                "peak_reserved_bytes": 9 * 1024**3,
                "allocated_limit_bytes": 22 * 1024**3,
            },
            "resume_verified": True,
            "status": "PASS",
            "errors": [],
        },
        "metadata": {"timestamp": "2026-08-23T00:00:00Z", "run_id": "run-a"},
    }


def test_tf32_is_disabled_and_runtime_controls_are_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch seeded determinism leaving TF32, benchmarking, or fallback warnings enabled."""
    monkeypatch.delenv("CUBLAS_WORKSPACE_CONFIG", raising=False)

    state = configure_determinism(seed=17)

    assert state.cuda_matmul_allow_tf32 is False
    assert state.cudnn_allow_tf32 is False
    assert state.cudnn_benchmark is False
    assert state.deterministic_algorithms is True
    assert state.deterministic_debug_mode == 2
    assert state.cublas_workspace_config == ":4096:8"


def test_allowlisted_backward_accepts_exact_inventory_and_restores_error_mode() -> None:
    configure_determinism(seed=17)

    evidence = feasibility_probe.run_allowlisted_backward(
        lambda: _emit_grid_sample_warnings(9), expected_count=9
    )

    assert evidence.operation_identifier == "grid_sampler_2d_backward_cuda"
    assert evidence.expected_count == 9
    assert evidence.observed_count == 9
    assert evidence.operation_identifiers == ("grid_sampler_2d_backward_cuda",) * 9
    assert evidence.warning_categories == ("UserWarning",) * 9
    assert len(evidence.raw_warnings) == 9
    assert evidence.strict_mode_restored is True
    assert evidence.source_sha256 == {
        "torch_init": (
            "b508de5a66ebc368fc8fa2161b1e0e88ae0034d9d9540e7c020460237a5464a9"
        ),
        "torch_nn_functional": (
            "e409a97896241e0dfb8c23fbf1f09967ecf5e65ec9626aec0d97d9cc5d727d50"
        ),
        "transformers_modeling_rt_detr": (
            "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3"
        ),
    }
    assert torch.are_deterministic_algorithms_enabled() is True
    assert torch.is_deterministic_algorithms_warn_only_enabled() is False
    assert torch.get_deterministic_debug_mode() == 2


@pytest.mark.parametrize(
    ("messages", "category", "expected"),
    [
        ((), UserWarning, "count mismatch"),
        (
            (GRID_WARNING,) * 8,
            UserWarning,
            "count mismatch",
        ),
        (
            (GRID_WARNING,) * 10,
            UserWarning,
            "count mismatch",
        ),
        (
            ("other_backward_cuda does not have a deterministic implementation.",) * 9,
            UserWarning,
            "unexpected deterministic backward operation",
        ),
        (
            (GRID_WARNING,) * 8
            + ("other_backward_cuda does not have a deterministic implementation.",),
            UserWarning,
            "unexpected deterministic backward operation",
        ),
        (
            ("deterministic warning without an operation identifier",),
            UserWarning,
            "unparsable",
        ),
        (
            (GRID_WARNING,) * 9,
            RuntimeWarning,
            "unexpected deterministic warning category",
        ),
    ],
    ids=[
        "zero",
        "eight",
        "ten",
        "different-operation",
        "mixed-operations",
        "unparsable",
        "wrong-category",
    ],
)
def test_allowlisted_backward_rejects_every_inventory_drift(
    messages: tuple[str, ...], category: type[Warning], expected: str
) -> None:
    configure_determinism(seed=17)

    with pytest.raises(FeasibilityError, match=expected):
        feasibility_probe.run_allowlisted_backward(
            lambda: _emit_warning_messages(messages, category), expected_count=9
        )

    assert torch.are_deterministic_algorithms_enabled() is True
    assert torch.is_deterministic_algorithms_warn_only_enabled() is False
    assert torch.get_deterministic_debug_mode() == 2


def test_allowlisted_backward_requires_strict_error_mode_on_entry() -> None:
    configure_determinism(seed=17)
    torch.use_deterministic_algorithms(True, warn_only=True)
    try:
        with pytest.raises(FeasibilityError, match="strict deterministic error mode"):
            feasibility_probe.run_allowlisted_backward(
                lambda: _emit_grid_sample_warnings(9), expected_count=9
            )
    finally:
        torch.use_deterministic_algorithms(True, warn_only=False)
        torch.set_deterministic_debug_mode("error")


def test_allowlisted_backward_restores_error_mode_when_backward_raises() -> None:
    configure_determinism(seed=17)

    def fail() -> None:
        raise RuntimeError("backward failed")

    with pytest.raises(RuntimeError, match="backward failed"):
        feasibility_probe.run_allowlisted_backward(fail, expected_count=9)

    assert torch.are_deterministic_algorithms_enabled() is True
    assert torch.is_deterministic_algorithms_warn_only_enabled() is False
    assert torch.get_deterministic_debug_mode() == 2


def test_allowlisted_backward_rejects_source_hash_drift_before_callback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_determinism(seed=17)
    called = False

    def callback() -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(feasibility_probe, "sha256_file", lambda path: "0" * 64)

    with pytest.raises(FeasibilityError, match="source hash mismatch"):
        feasibility_probe.run_allowlisted_backward(callback, expected_count=9)

    assert called is False


def test_grid_sample_warning_count_is_derived_from_pinned_model_config() -> None:
    model = SimpleNamespace(
        config=SimpleNamespace(decoder_layers=3, num_feature_levels=3)
    )

    assert feasibility_probe._expected_grid_sample_warning_count(model) == 9


@pytest.mark.parametrize(
    ("decoder_layers", "feature_levels"),
    [(2, 3), (3, 4), (True, 3), (3, None)],
)
def test_grid_sample_warning_count_rejects_config_drift(
    decoder_layers: object, feature_levels: object
) -> None:
    model = SimpleNamespace(
        config=SimpleNamespace(
            decoder_layers=decoder_layers, num_feature_levels=feature_levels
        )
    )

    with pytest.raises(FeasibilityError, match="pinned RT-DETR deformable-attention"):
        feasibility_probe._expected_grid_sample_warning_count(model)


def test_optimizer_and_parameter_inventory_have_exact_named_groups() -> None:
    model = _TinyGroupedModel()

    optimizer = feasibility_probe.build_optimizer(model)
    baseline = feasibility_probe._capture_parameter_baseline(model)

    assert [group["group_name"] for group in optimizer.param_groups] == [
        "detector",
        "backbone",
    ]
    assert [group["lr"] for group in optimizer.param_groups] == [1e-4, 1e-5]
    assert [group["weight_decay"] for group in optimizer.param_groups] == [
        1e-4,
        1e-4,
    ]
    assert baseline.inventory == (
        {
            "name": "detector.weight",
            "group_name": "detector",
            "shape": [1, 2],
            "dtype": "float32",
        },
        {
            "name": "detector.bias",
            "group_name": "detector",
            "shape": [1],
            "dtype": "float32",
        },
        {
            "name": "model.backbone.weight",
            "group_name": "backbone",
            "shape": [1, 2],
            "dtype": "float32",
        },
        {
            "name": "model.backbone.bias",
            "group_name": "backbone",
            "shape": [1],
            "dtype": "float32",
        },
    )


def test_parameter_update_norms_use_ordered_cpu_float64_groups() -> None:
    model = _TinyGroupedModel()
    with torch.no_grad():
        for parameter in model.parameters():
            parameter.zero_()
    baseline = feasibility_probe._capture_parameter_baseline(model)
    with torch.no_grad():
        model.detector.weight.add_(torch.tensor([[3.0, 4.0]]))
        model.detector.bias.add_(12.0)
        model.model.backbone.weight.add_(torch.tensor([[5.0, 12.0]]))
        model.model.backbone.bias.add_(84.0)

    update_groups = feasibility_probe._measure_parameter_update_groups(model, baseline)

    assert update_groups == {"detector": 13.0, "backbone": 85.0}


def test_initialized_cuda_requires_preconfigured_cublas_workspace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch setting the deterministic workspace too late for an existing CUDA model."""
    monkeypatch.delenv("CUBLAS_WORKSPACE_CONFIG", raising=False)
    monkeypatch.setattr(torch.cuda, "is_initialized", lambda: True)

    with pytest.raises(FeasibilityError, match="before CUDA initialization"):
        configure_determinism(seed=17)


def test_deterministic_comparison_is_exact_and_excludes_timing() -> None:
    """Catch observational post-update jitter entering the exact A3 identity."""
    first = _observation()
    second = _observation(
        wall_seconds=99.0,
        gpu_seconds=98.0,
        gradient_norm=0.7500001,
        parameter_digest_after="a" * 64,
        live_model_state_digest_after="b" * 64,
        update_groups={"detector": 0.1251, "backbone": 0.0626},
        state_digests={
            "model": "a" * 64,
            "optimizer": "b" * 64,
            "scheduler": "3" * 64,
            "scaler": "4" * 64,
            "rng": "5" * 64,
            "sampler": "6" * 64,
        },
    )
    changed = _observation(ordered_losses=(3.2500000000000004,))

    assert feasibility_probe.exact_comparison(
        first
    ) == feasibility_probe.exact_comparison(second)
    assert feasibility_probe.exact_comparison(
        first
    ) != feasibility_probe.exact_comparison(changed)
    assert feasibility_probe.exact_comparison(first)["ordered_loss_hex"] == [
        (3.25).hex()
    ]
    assert set(feasibility_probe.exact_comparison(first)["state_digests"]) == {
        "scheduler",
        "scaler",
        "rng",
        "sampler",
    }


def test_buffer_only_state_change_cannot_prove_parameter_update() -> None:
    """Catch BatchNorm running buffers being mistaken for an AdamW parameter update."""
    model = torch.nn.BatchNorm1d(2)
    model.train()
    parameter_digest_before = feasibility_probe.trainable_parameter_sha256(model)
    full_state_digest_before = feasibility_probe.structured_state_sha256(
        model.state_dict()
    )

    with torch.no_grad():
        model(torch.tensor([[1.0, 2.0], [3.0, 6.0]]))

    parameter_digest_after = feasibility_probe.trainable_parameter_sha256(model)
    full_state_digest_after = feasibility_probe.structured_state_sha256(
        model.state_dict()
    )
    assert full_state_digest_before != full_state_digest_after
    assert parameter_digest_before == parameter_digest_after

    with pytest.raises(FeasibilityError, match="parameter update"):
        evaluate_step_observation(
            _observation(
                parameter_changed=full_state_digest_before != full_state_digest_after,
                parameter_digest_before=parameter_digest_before,
                parameter_digest_after=parameter_digest_after,
            )
        )


def test_omitted_cpu_checkpoint_model_state_is_rejected(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch a checkpoint capture silently omitting live post-step model state."""
    model = torch.nn.Linear(2, 1)
    original_copy = feasibility_probe._state_to_cpu

    def omit_bias(value: object) -> object:
        copied = original_copy(value)
        if isinstance(copied, dict) and set(copied) == {"weight", "bias"}:
            copied.pop("bias")
        return copied

    monkeypatch.setattr(feasibility_probe, "_state_to_cpu", omit_bias)

    with pytest.raises(FeasibilityError, match="CPU checkpoint model state mismatch"):
        feasibility_probe._capture_checkpoint_model_state(model)


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"ordered_losses": (float("nan"),), "finite_loss": False}, "non-finite loss"),
        ({"finite_gradients": False}, "non-finite gradients"),
        (
            {"allowlisted_backward": replace(_warning_evidence(), observed_count=8)},
            "allowlisted backward",
        ),
        ({"cuda_matmul_allow_tf32": True}, "TF32"),
        ({"bf16_supported": False}, "BF16"),
        ({"parameter_changed": False}, "parameter update"),
        ({"peak_allocated_bytes": 22 * 1024**3 + 1}, "22 GiB"),
    ],
)
def test_normative_runtime_failures_are_never_masked(
    changes: dict[str, object], expected: str
) -> None:
    """Catch a stop condition being converted into a passing or fallback observation."""
    with pytest.raises(FeasibilityError, match=expected):
        evaluate_step_observation(_observation(**changes))


def test_feasibility_receipt_is_schema_valid_and_content_addressed(
    tmp_path: Path,
) -> None:
    """Catch publishing incomplete or non-canonical feasibility evidence."""
    output = tmp_path / "feasibility.json"

    atomic_write_receipt(output, _receipt())
    stored = json.loads(output.read_text(encoding="utf-8"))

    validate_receipt(
        stored,
        Path(__file__).resolve().parents[2]
        / "schemas"
        / "feasibility-receipt.schema.json",
    )
    assert (
        stored["normative"]["loss_source_sha256"]
        == stored["normative"]["parent_model_contract"]["normative"][
            "loss_source_sha256"
        ]
    )
    assert (
        stored["normative"]["synthetic_target_sha256"]
        == stored["normative"]["parent_model_contract"]["normative"][
            "synthetic_target_sha256"
        ]
    )
    exact = stored["normative"]["exact_comparison"]
    assert exact["sha256"] == canonical_json_sha256(
        {name: value for name, value in exact.items() if name not in {"rule", "sha256"}}
    )


def test_historical_feasibility_schema_version_cannot_satisfy_a3(
    tmp_path: Path,
) -> None:
    receipt = _receipt()
    receipt["schema_version"] = 1

    with pytest.raises(ReceiptValidationError, match="unknown receipt type or schema"):
        atomic_write_receipt(tmp_path / "historical.json", receipt)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda n: n["allowlisted_backward"].pop("source_sha256"), "source_sha256"),
        (
            lambda n: n["allowlisted_backward"].update({"expected_count": 8}),
            "expected_count",
        ),
        (
            lambda n: n["allowlisted_backward"]["raw_warnings"].pop(),
            "raw_warnings",
        ),
        (
            lambda n: n["allowlisted_backward"]["warning_categories"].__setitem__(
                0, "RuntimeWarning"
            ),
            "warning_categories",
        ),
        (
            lambda n: n["allowlisted_backward"]["operation_identifiers"].__setitem__(
                0, "other_backward_cuda"
            ),
            "operation_identifiers",
        ),
        (
            lambda n: n["allowlisted_backward"]["source_sha256"].update(
                {"torch_init": "0" * 64}
            ),
            "torch_init",
        ),
        (
            lambda n: n["allowlisted_backward"].update({"strict_mode_restored": False}),
            "strict_mode_restored",
        ),
        (
            lambda n: n["allowlisted_backward"].update({"unexpected": True}),
            "unexpected",
        ),
        (
            lambda n: n["parameter_inventory"].append(
                copy.deepcopy(n["parameter_inventory"][0])
            ),
            "parameter inventory count",
        ),
        (lambda n: n["update_groups"].pop("backbone"), "backbone"),
        (
            lambda n: n["update_groups"]["detector"].update({"l2_norm": 0.0}),
            "detector update norm",
        ),
    ],
)
def test_a3_feasibility_evidence_drift_fails_closed(
    tmp_path: Path, mutation: object, expected: str
) -> None:
    receipt = _receipt()
    normative = receipt["normative"]
    assert isinstance(normative, dict)
    assert callable(mutation)
    mutation(normative)

    with pytest.raises(ReceiptValidationError, match=expected):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda n: n["exact_comparison"].update({"sha256": "0" * 64}),
            "exact comparison",
        ),
        (
            lambda n: n["runtime"].update({"tf32": True}),
            "runtime.tf32",
        ),
        (
            lambda n: n["vram"].update({"peak_allocated_bytes": 22 * 1024**3 + 1}),
            "peak_allocated_vram_within_22_gib",
        ),
        (
            lambda n: n["recipe"].update({"gradient_clip_norm": 1.0}),
            "gradient_clip_norm",
        ),
        (
            lambda n: n["step"].update(
                {"parameter_digest_after": n["step"]["parameter_digest_before"]}
            ),
            "parameter_changed",
        ),
        (
            lambda n: n["step"].update({"trainable_parameter_count": 0}),
            "parameter inventory count",
        ),
        (
            lambda n: n["step"].update(
                {"parameter_digest_rule": "full-model-state-sha256"}
            ),
            "parameter_digest_rule",
        ),
        (
            lambda n: n["step"].update({"finite_gradients": False}),
            "finite_gradients",
        ),
        (
            lambda n: n["synthetic_labels"].update({"class_labels": [[0], [2]]}),
            "synthetic_labels_only",
        ),
        (
            lambda n: n["runtime"].update({"precision": "float32"}),
            "precision",
        ),
        (
            lambda n: n["checkpoint"].update({"verified_file_sha256": "b" * 64}),
            "checkpoint_content_verified",
        ),
        (
            lambda n: n["checkpoint"]["state_digests_after_load"].update(
                {"optimizer": "b" * 64}
            ),
            "checkpoint_round_trip",
        ),
        (
            lambda n: n["checkpoint"].update(
                {"live_model_state_sha256_after_step": "b" * 64}
            ),
            "checkpoint_round_trip",
        ),
        (
            lambda n: n["checkpoint"]["state_digests_after_restore"].update(
                {"rng": "b" * 64}
            ),
            "resume_state_verified",
        ),
    ],
)
def test_rehashed_pass_receipt_cannot_contradict_embedded_evidence(
    tmp_path: Path, mutation: object, expected: str
) -> None:
    """Catch a self-consistent outer hash masking false feasibility evidence."""
    receipt = _receipt()
    normative = receipt["normative"]
    assert isinstance(normative, dict)
    assert callable(mutation)
    mutation(normative)

    with pytest.raises(ReceiptValidationError, match=expected):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


def test_cli_manifest_discovers_training_feasibility_probe() -> None:
    """Catch omitting the required lazy CLI command."""
    source_root = Path(__file__).resolve().parents[2] / "src"

    manifest = build_manifest(source_root)

    assert manifest["probe training-feasibility"] == (
        "vision_active_learning_loop.probes.training_feasibility:main"
    )


def test_labeled_batch_uses_only_registered_synthetic_fixture_geometry() -> None:
    """Catch the feasibility smoke using unlabeled, external, or reordered samples."""
    batch, shapes, evidence = _prepare_labeled_batch(torch.device("cpu"), HASH)

    assert shapes == {
        "pixel_values": [2, 3, 640, 640],
        "pixel_mask": [2, 640, 640],
    }
    assert evidence == {
        "item_ids": ["wide-gradient", "tall-checker"],
        "class_labels": [[0], [3]],
        "boxes_per_image": [1, 1],
        "source": "tracked-synthetic-fixture-geometry-v1",
    }
    assert [label["class_labels"].tolist() for label in batch["labels"]] == [
        [0],
        [3],
    ]


def test_labeled_batch_consumes_only_loader_annotations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch reintroducing duplicated inline labels outside the tracked fixture."""
    original = feasibility_probe.load_synthetic_contract_fixture(
        feasibility_probe._FIXTURE_MANIFEST
    )
    annotations = copy.deepcopy(original.annotations)
    annotations[0]["annotations"][0]["category_id"] = 2
    fixture = SimpleNamespace(
        manifest=original.manifest,
        images=original.images,
        annotations=annotations,
        input_sha256=HASH,
        target_sha256=HASH,
    )
    monkeypatch.setattr(
        feasibility_probe,
        "load_synthetic_contract_fixture",
        lambda path: fixture,
        raising=False,
    )

    batch, _, evidence = _prepare_labeled_batch(torch.device("cpu"), HASH)

    assert evidence["class_labels"] == [[2], [3]]
    assert [label["class_labels"].tolist() for label in batch["labels"]] == [
        [2],
        [3],
    ]


def test_cli_paths_reject_data_root_and_noncanonical_locations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch checkpoint/receipt outputs escaping the external Wave 0 boundary."""
    wave = tmp_path / "wave0"
    receipts = wave / "receipts"
    checkpoints = wave / "checkpoints"
    receipts.mkdir(parents=True)
    checkpoints.mkdir()
    model_contract = receipts / "model-contract-run-a.json"
    model_contract.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))

    resolved = resolve_cli_paths(
        model_contract,
        checkpoints / "feasibility-a",
        receipts / "feasibility-a.json",
    )
    assert resolved == (
        model_contract.resolve(),
        (checkpoints / "feasibility-a").resolve(),
        (receipts / "feasibility-a.json").resolve(),
    )

    monkeypatch.setenv("VAL_DATA_ROOT", str(tmp_path / "forbidden"))
    with pytest.raises(FeasibilityError, match="VAL_DATA_ROOT"):
        resolve_cli_paths(
            model_contract,
            checkpoints / "feasibility-a",
            receipts / "feasibility-a.json",
        )


def test_cli_reports_missing_training_backend_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Catch a missing exact-stack backend escaping as an uncontrolled traceback."""
    paths = (tmp_path / "model.json", tmp_path / "checkpoints", tmp_path / "out.json")
    monkeypatch.setattr(feasibility_probe, "resolve_cli_paths", lambda *args: paths)
    monkeypatch.setattr(
        feasibility_probe,
        "_execute_probe",
        lambda *args: (_ for _ in ()).throw(ImportError("SciPy is required")),
    )

    exit_code = feasibility_probe.main(
        [
            "--model-contract",
            str(paths[0]),
            "--checkpoint-root",
            str(paths[1]),
            "--run-id",
            "run-a",
            "--output",
            str(paths[2]),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err.strip() == "SciPy is required"
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    ("location", "field", "value", "expected"),
    [
        ("observed", "python", "3.12.12", "python"),
        ("observed", "uv", "0.11.18", "uv"),
        ("observed", "scipy", "1.17.1", "scipy"),
        ("selected", "selected_index", 1, "cuda:0"),
        ("selected", "selected_uuid", "22222222-2222-2222-2222-222222222222", "UUID"),
    ],
)
def test_live_environment_evidence_rejects_runtime_or_device_drift(
    location: str, field: str, value: object, expected: str
) -> None:
    parent = _parent_environment()
    evidence = _environment_evidence()
    if location == "observed":
        evidence["observed"][field] = value
    else:
        evidence["selected_cuda"][field] = value

    with pytest.raises(FeasibilityError, match=expected):
        validate_live_environment_evidence(parent, evidence)


def test_feasibility_receipt_rejects_rehashed_environment_drift(
    tmp_path: Path,
) -> None:
    receipt = _receipt()
    normative = receipt["normative"]
    normative["environment"]["observed"]["torch"] = "2.12.1+cu126"
    normative["environment_sha256"] = canonical_json_sha256(normative["environment"])

    with pytest.raises(ReceiptValidationError, match="live torch"):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


def test_feasibility_receipt_rejects_consistently_rehashed_parent_bindings(
    tmp_path: Path,
) -> None:
    receipt = _receipt()
    normative = receipt["normative"]
    for name in (
        "model_sha256",
        "config_sha256",
        "source_sha256",
        "processor_sha256",
        "fixture_sha256",
        "loss_source_sha256",
        "synthetic_target_sha256",
        "model_contract_receipt_sha256",
        "parent_environment_sha256",
    ):
        normative[name] = "0" * 64
    normative["environment"]["parent_environment_sha256"] = "0" * 64
    normative["environment_sha256"] = canonical_json_sha256(normative["environment"])

    with pytest.raises(
        ReceiptValidationError, match="parent model-contract|loss_source_sha256"
    ):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


@pytest.mark.parametrize(
    ("field", "invariant"),
    [
        ("loss_source_sha256", None),
        ("synthetic_target_sha256", None),
        (None, "encoder_score_head_four_channels"),
    ],
)
def test_feasibility_rejects_narrower_option_a_parent(
    tmp_path: Path, field: str | None, invariant: str | None
) -> None:
    """Catch historical label-free PASS evidence being promoted to A2."""
    receipt = _receipt()
    normative = receipt["normative"]
    parent = normative["parent_model_contract"]
    parent_normative = parent["normative"]
    if field is not None:
        del parent_normative[field]
    else:
        del parent_normative["invariants"][invariant]
    parent["metadata"]["receipt_content_sha256"] = _receipt_content_sha256(parent)
    normative["model_contract_receipt_sha256"] = _stored_receipt_sha256(parent)

    with pytest.raises(ReceiptValidationError, match="missing required|invariant"):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


def test_feasibility_receipt_rejects_invented_fail_cause(tmp_path: Path) -> None:
    receipt = _receipt()
    normative = receipt["normative"]
    normative["invariants"]["canonical_environment"] = False
    normative["status"] = "FAIL"
    normative["errors"] = ["canonical_environment"]

    with pytest.raises(ReceiptValidationError, match="canonical_environment"):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


def test_feasibility_receipt_rejects_rehashed_failed_parent(
    tmp_path: Path,
) -> None:
    receipt = _receipt()
    normative = receipt["normative"]
    parent = normative["parent_model_contract"]
    parent["normative"]["status"] = "FAIL"
    parent["normative"]["errors"] = ["invented parent failure"]
    parent["metadata"]["receipt_content_sha256"] = _receipt_content_sha256(parent)
    normative["model_contract_receipt_sha256"] = _stored_receipt_sha256(parent)

    with pytest.raises(ReceiptValidationError, match="parent model-contract.*PASS"):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


def test_cli_requires_fresh_output_path_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output = tmp_path / "feasibility.json"
    output.write_text("older receipt", encoding="utf-8")
    paths = (tmp_path / "model.json", tmp_path / "checkpoints", output)
    called = False

    def unexpected_execute(*args: object) -> dict[str, object]:
        nonlocal called
        called = True
        return _receipt()

    monkeypatch.setattr(feasibility_probe, "resolve_cli_paths", lambda *args: paths)
    monkeypatch.setattr(feasibility_probe, "_execute_probe", unexpected_execute)

    exit_code = feasibility_probe.main(
        [
            "--model-contract",
            str(paths[0]),
            "--checkpoint-root",
            str(paths[1]),
            "--run-id",
            "run-a",
            "--output",
            str(paths[2]),
        ]
    )

    assert exit_code == 2
    assert called is False
    assert output.read_text(encoding="utf-8") == "older receipt"
    assert "fresh output" in capsys.readouterr().err


def test_schema_rejects_missing_resume_or_rng_digest(tmp_path: Path) -> None:
    """Catch incomplete checkpoint proof being published as PASS."""
    for field in ("resume_verified", "state_digests"):
        receipt = _receipt()
        normative = receipt["normative"]
        assert isinstance(normative, dict)
        if field == "state_digests":
            state_digests = normative[field]
            assert isinstance(state_digests, dict)
            del state_digests["rng"]
        else:
            del normative[field]

        with pytest.raises(ReceiptValidationError):
            atomic_write_receipt(tmp_path / f"{field}.json", receipt)
