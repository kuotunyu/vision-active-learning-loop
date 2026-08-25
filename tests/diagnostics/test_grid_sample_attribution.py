"""Tests for the bounded A7 grid-sample attribution seam."""

from __future__ import annotations

import ast
import copy
import hashlib
import inspect
import json
import shutil
import subprocess
import textwrap
from itertools import combinations
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
from torch.nn import functional

from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.diagnostics import (
    grid_sample_attribution as attribution,
)
from vision_active_learning_loop.diagnostics.grid_sample_attribution import (
    OPERATION_IDS,
    AttributionError,
    GridSampleAttributionAdapter,
    ModelRecorder,
    capture_parameter_gradients,
    classify_aggregate,
    install_adapters,
    run_isolated_vjp_tensors,
)
from vision_active_learning_loop.diagnostics.tensor_evidence import (
    atomic_write_snapshot,
)


class FakeAttention(torch.nn.Module):
    """A tiny parameter-free fake of the pinned three-feature loop."""

    def __init__(
        self,
        *,
        feature_count: int = 3,
        mode: str = "bilinear",
        fail_after: int | None = None,
    ) -> None:
        super().__init__()
        self.feature_count = feature_count
        self.mode = mode
        self.fail_after = fail_after

    def forward(
        self,
        value,
        value_spatial_shapes,
        value_spatial_shapes_list,
        level_start_index,
        sampling_locations,
        attention_weights,
        im2col_step,
    ):
        del value_spatial_shapes, level_start_index, attention_weights, im2col_step
        results = []
        for feature in range(self.feature_count):
            result = functional.grid_sample(
                value[feature],
                sampling_locations[feature],
                mode=self.mode,
                padding_mode="zeros",
                align_corners=False,
            )
            results.append(result)
            if self.fail_after == feature:
                raise RuntimeError("fake attention failure")
        assert len(value_spatial_shapes_list) >= self.feature_count
        return torch.stack(results)


class FakeLayer(torch.nn.Module):
    def __init__(self, attention: torch.nn.Module | None = None) -> None:
        super().__init__()
        self.encoder_attn = SimpleNamespace(attn=attention or FakeAttention())


class FakeModel(torch.nn.Module):
    def __init__(self, *, layers: int = 3, attention_factory=FakeAttention) -> None:
        super().__init__()
        decoder_layers = torch.nn.ModuleList(
            [FakeLayer(attention_factory()) for _ in range(layers)]
        )
        self.model = SimpleNamespace(decoder=SimpleNamespace(layers=decoder_layers))


def _operands() -> tuple[list[torch.Tensor], list[torch.Tensor]]:
    values = [
        torch.tensor(
            [[[[1.0, 2.0], [3.0, 5.0]]]],
            dtype=torch.float64,
            requires_grad=True,
        )
        for _ in range(3)
    ]
    grids = [
        torch.tensor(
            [[[[-0.75, -0.25], [0.5, 0.25]]]],
            dtype=torch.float64,
            requires_grad=True,
        )
        for _ in range(3)
    ]
    return values, grids


def _call(attention: torch.nn.Module, values, grids) -> torch.Tensor:
    wrapped = getattr(attention, "wrapped", attention)
    feature_count = getattr(wrapped, "feature_count", 3)
    while len(values) < feature_count:
        values.append(values[-1].detach().clone().requires_grad_(True))
        grids.append(grids[-1].detach().clone().requires_grad_(True))
    return attention(
        values,
        torch.tensor([[2, 2]] * feature_count),
        [(2, 2)] * feature_count,
        torch.arange(feature_count) * 4,
        grids,
        torch.ones(1),
        64,
    )


def test_operation_inventory_and_adapter_structure_are_exact() -> None:
    assert OPERATION_IDS == tuple(
        f"decoder-{decoder}/feature-{feature}"
        for decoder in range(3)
        for feature in range(3)
    )
    model = FakeModel()
    originals = tuple(layer.encoder_attn.attn for layer in model.model.decoder.layers)

    adapters = install_adapters(model, ModelRecorder())

    assert len(adapters) == 3
    assert tuple(adapter.wrapped for adapter in adapters) == originals
    assert (
        tuple(layer.encoder_attn.attn for layer in model.model.decoder.layers)
        == adapters
    )


@pytest.mark.parametrize(
    ("model", "message"),
    [
        (FakeModel(layers=2), "three decoder"),
        (SimpleNamespace(), "module path"),
    ],
)
def test_install_adapters_rejects_wrong_decoder_count_or_module_path(
    model: object, message: str
) -> None:
    with pytest.raises(AttributionError, match=message):
        install_adapters(model, ModelRecorder())


@pytest.mark.parametrize(
    ("factory", "message"),
    [
        (lambda: FakeAttention(feature_count=2), "three grid_sample"),
        (lambda: FakeAttention(feature_count=4), "extra grid_sample"),
        (lambda: FakeAttention(mode="nearest"), "arguments"),
    ],
)
def test_adapter_rejects_wrong_feature_count_or_arguments(
    factory, message: str
) -> None:
    model = FakeModel(attention_factory=factory)
    adapter = install_adapters(model, ModelRecorder())[0]
    values, grids = _operands()

    with pytest.raises(AttributionError, match=message):
        _call(adapter, values, grids)


def test_adapter_rejects_reentry_duplicate_forward_and_restoration_drift(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    recorder = ModelRecorder()
    adapter = GridSampleAttributionAdapter(FakeAttention(), 0, recorder)
    values, grids = _operands()
    adapter._active = True
    with pytest.raises(AttributionError, match="reentry"):
        _call(adapter, values, grids)
    adapter._active = False
    _call(adapter, values, grids)
    with pytest.raises(AttributionError, match="duplicate"):
        _call(adapter, values, grids)

    drifting = GridSampleAttributionAdapter(FakeAttention(), 1, ModelRecorder())
    saved = functional.grid_sample

    def replace_callable(*args, **kwargs):
        functional.grid_sample = lambda *inner_args, **inner_kwargs: None
        return saved(*args, **kwargs)

    monkeypatch.setattr(FakeAttention, "forward", replace_callable)
    with pytest.raises((AttributionError, TypeError), match="restoration|argument"):
        _call(drifting, values, grids)
    assert functional.grid_sample is saved


def test_adapter_is_transparent_and_records_backward_callback_permutation() -> None:
    plain_values, plain_grids = _operands()
    wrapped_values, wrapped_grids = _operands()
    plain = FakeAttention()
    recorder = ModelRecorder(expected_operation_ids=OPERATION_IDS[:3])
    adapter = GridSampleAttributionAdapter(FakeAttention(), 0, recorder)

    plain_output = _call(plain, plain_values, plain_grids)
    wrapped_output = _call(adapter, wrapped_values, wrapped_grids)
    assert torch.equal(plain_output, wrapped_output)
    weights = torch.arange(1, wrapped_output.numel() + 1, dtype=torch.float64).reshape(
        wrapped_output.shape
    )
    (plain_output * weights).sum().backward()
    (wrapped_output * weights).sum().backward()

    assert functional.grid_sample is torch.nn.functional.grid_sample
    for plain_value, wrapped_value in zip(plain_values, wrapped_values, strict=True):
        assert torch.equal(plain_value.grad, wrapped_value.grad)
    for plain_grid, wrapped_grid in zip(plain_grids, wrapped_grids, strict=True):
        assert torch.equal(plain_grid.grad, wrapped_grid.grad)
    captures = recorder.finalize()
    assert {capture.operation_id for capture in captures} == set(OPERATION_IDS[:3])
    assert sorted(capture.callback_order for capture in captures) == [0, 1, 2]
    assert all(
        set(capture.tensors)
        == {
            "forward_value",
            "forward_grid",
            "forward_result",
            "incoming_result_gradient",
            "outgoing_value_gradient",
            "outgoing_grid_gradient",
        }
        for capture in captures
    )


def test_adapter_restores_callable_after_wrapped_exception() -> None:
    adapter = GridSampleAttributionAdapter(
        FakeAttention(fail_after=0),
        0,
        ModelRecorder(expected_operation_ids=OPERATION_IDS[:3]),
    )
    saved = functional.grid_sample
    values, grids = _operands()

    with pytest.raises(RuntimeError, match="fake attention failure"):
        _call(adapter, values, grids)

    assert functional.grid_sample is saved


def test_recorder_rejects_finalize_before_backward_duplicate_and_nonfinite_gradient() -> None:
    values, grids = _operands()
    recorder = ModelRecorder(expected_operation_ids=OPERATION_IDS[:3])
    adapter = GridSampleAttributionAdapter(FakeAttention(), 0, recorder)
    output = _call(adapter, values, grids)
    with pytest.raises(AttributionError, match="gradient|callback"):
        recorder.finalize()
    hook = recorder.incoming_gradient_hook(OPERATION_IDS[0])
    assert hook(torch.ones_like(output[0])) is None
    with pytest.raises(AttributionError, match="duplicate"):
        hook(torch.ones_like(output[0]))
    bad = ModelRecorder(expected_operation_ids=(OPERATION_IDS[0],))
    bad.observe_forward(OPERATION_IDS[0], values[0], grids[0], output[0])
    with pytest.raises(AttributionError, match="non-finite"):
        bad.incoming_gradient_hook(OPERATION_IDS[0])(
            torch.full_like(output[0], float("nan"))
        )


def test_adapter_source_calls_saved_original_once_and_returns_unmodified_result() -> None:
    source = textwrap.dedent(inspect.getsource(GridSampleAttributionAdapter.forward))
    tree = ast.parse(source)
    calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "original_grid_sample"
    ]
    assert len(calls) == 1
    result_assignment = source.index("result = original_grid_sample")
    result_return = source.index("return result", result_assignment)
    result_path = source[result_assignment:result_return]
    assert all(
        forbidden not in result_path
        for forbidden in (
            "result.detach",
            "result.clone",
            "result.to(",
            "result +",
            "result *",
        )
    )


class NamedGradientModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.detector = torch.nn.Linear(2, 2, bias=False, dtype=torch.float64)
        self.backbone = torch.nn.Linear(2, 1, bias=False, dtype=torch.float64)


def test_parameter_gradient_inventory_is_complete_ordered_and_canonical() -> None:
    model = NamedGradientModel()
    model.backbone(
        model.detector(torch.tensor([[1.0, 2.0]], dtype=torch.float64))
    ).sum().backward()

    inventory = capture_parameter_gradients(model)

    assert [record["name"] for record in inventory["parameters"]] == [
        "detector.weight",
        "backbone.weight",
    ]
    assert inventory["count"] == 2
    assert len(inventory["inventory_sha256"]) == 64
    assert all(isinstance(record["shape"], list) for record in inventory["parameters"])
    assert all(
        record["role"] == "parameter_gradient" for record in inventory["parameters"]
    )


def test_parameter_gradient_inventory_preserves_pre_adapter_names() -> None:
    model = NamedGradientModel()
    canonical_parameters = tuple(model.named_parameters(remove_duplicate=False))

    class Wrapper(torch.nn.Module):
        def __init__(self, wrapped: torch.nn.Module) -> None:
            super().__init__()
            self.wrapped = wrapped

        def forward(self, value: torch.Tensor) -> torch.Tensor:
            return self.wrapped(value)

    model.detector = Wrapper(model.detector)
    model.backbone(
        model.detector(torch.tensor([[1.0, 2.0]], dtype=torch.float64))
    ).sum().backward()

    inventory = capture_parameter_gradients(
        model, canonical_parameters=canonical_parameters
    )

    assert [record["name"] for record in inventory["parameters"]] == [
        "detector.weight",
        "backbone.weight",
    ]


@pytest.mark.parametrize("case", ["missing", "nonfinite", "duplicate"])
def test_parameter_gradient_inventory_rejects_incomplete_or_invalid_gradients(
    case: str,
) -> None:
    model = NamedGradientModel()
    if case != "missing":
        model.backbone(
            model.detector(torch.ones(1, 2, dtype=torch.float64))
        ).sum().backward()
    if case == "nonfinite":
        model.detector.weight.grad[0, 0] = float("inf")
    if case == "duplicate":
        model.alias = model.detector
    with pytest.raises(AttributionError):
        capture_parameter_gradients(model)


def test_live_gpu_uuid_and_vram_ceiling_are_fail_closed() -> None:
    attribution._validate_live_gpu_uuid(_GPU_UUID, f"{_GPU_UUID}\n")
    attribution._require_vram_limit(22 * 1024**3)
    with pytest.raises(AttributionError, match="UUID"):
        attribution._validate_live_gpu_uuid(_GPU_UUID, f"{_GPU_UUID}\n{_GPU_UUID}\n")
    with pytest.raises(AttributionError, match="UUID"):
        attribution._validate_live_gpu_uuid(
            _GPU_UUID, "GPU-ffffffff-ffff-ffff-ffff-ffffffffffff\n"
        )
    with pytest.raises(AttributionError, match="22 GiB"):
        attribution._require_vram_limit(22 * 1024**3 + 1)


def _isolated_snapshot() -> dict[str, torch.Tensor]:
    tensors: dict[str, torch.Tensor] = {}
    for operation_id in OPERATION_IDS:
        value = torch.tensor([[[[1.0, 2.0], [3.0, 4.0]]]], dtype=torch.float64)
        grid = torch.tensor([[[[-0.5, -0.5], [0.5, 0.5]]]], dtype=torch.float64)
        incoming = torch.tensor([[[[1.0, 2.0]]]], dtype=torch.float64)
        tensors[f"{operation_id}.forward_value"] = value
        tensors[f"{operation_id}.forward_grid"] = grid
        tensors[f"{operation_id}.incoming_result_gradient"] = incoming
    return tensors


def test_isolated_vjp_uses_nine_original_calls_and_one_multi_output_backward(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[object, ...]] = []
    backward_calls: list[tuple[object, ...]] = []
    saved_grid_sample = functional.grid_sample
    saved_backward = torch.autograd.backward

    def observed_grid_sample(value, grid, **kwargs):
        calls.append((value, grid, kwargs))
        return saved_grid_sample(value, grid, **kwargs)

    def observed_backward(tensors, grad_tensors):
        backward_calls.append((tensors, grad_tensors))
        return saved_backward(tensors, grad_tensors)

    def allowlisted(callback, *, expected_count):
        assert expected_count == 9
        callback()
        return {"count": 9, "operations": ["grid_sampler_2d_backward_cuda"] * 9}

    monkeypatch.setattr(attribution, "_ORIGINAL_GRID_SAMPLE", observed_grid_sample)
    monkeypatch.setattr(torch.autograd, "backward", observed_backward)
    monkeypatch.setattr(attribution, "_run_allowlisted_backward", allowlisted)

    result = run_isolated_vjp_tensors(_isolated_snapshot())

    assert len(calls) == 9
    assert len(backward_calls) == 1
    assert all(
        call[2] == {"mode": "bilinear", "padding_mode": "zeros", "align_corners": False}
        for call in calls
    )
    assert result["autocast_observed"] is False
    assert result["warning_evidence"]["count"] == 9
    assert len(result["operations"]) == 9
    assert all(len(operation.tensors) == 6 for operation in result["operations"])


def test_isolated_engine_wires_strict_math_only_runtime_and_forward_autocast() -> None:
    replica_source = inspect.getsource(attribution.run_isolated_vjp_replica)
    vjp_source = inspect.getsource(attribution.run_isolated_vjp_tensors)

    assert "configure_determinism(17)" in replica_source
    assert "sdpa_kernel(SDPBackend.MATH)" in replica_source
    assert "torch.are_deterministic_algorithms_enabled()" in replica_source
    assert "torch.is_deterministic_algorithms_warn_only_enabled()" in replica_source
    assert "with forward_context:" in vjp_source
    assert vjp_source.index("with forward_context:") < vjp_source.index(
        "result = _ORIGINAL_GRID_SAMPLE"
    )
    assert vjp_source.index("_run_allowlisted_backward") > vjp_source.index(
        "result = _ORIGINAL_GRID_SAMPLE"
    )


def test_model_engine_filters_audit_only_batch_fields_before_forward() -> None:
    source = inspect.getsource(attribution.run_model_replica)

    assert 'if not name.startswith("_val_")' in source
    assert "model(**model_batch)" in source
    assert "model(**batch)" not in source


def test_replica_engines_capture_allocated_and_reserved_vram() -> None:
    model_source = inspect.getsource(attribution.run_model_replica)
    isolated_source = inspect.getsource(attribution.run_isolated_vjp_replica)

    for source in (model_source, isolated_source):
        assert "torch.cuda.max_memory_allocated" in source
        assert "torch.cuda.max_memory_reserved" in source
        assert "peak_reserved_vram_bytes" in source


@pytest.mark.parametrize("case", ["missing", "extra", "nonfinite"])
def test_isolated_vjp_rejects_wrong_snapshot_inventory_or_gradient(
    monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    snapshot = _isolated_snapshot()
    if case == "missing":
        snapshot.pop(next(iter(snapshot)))
    elif case == "extra":
        snapshot["extra"] = torch.ones(1)
    else:
        key = next(
            name for name in snapshot if name.endswith("incoming_result_gradient")
        )
        snapshot[key][0] = float("nan")
    monkeypatch.setattr(
        attribution,
        "_run_allowlisted_backward",
        lambda callback, *, expected_count: callback(),
    )
    with pytest.raises(AttributionError):
        run_isolated_vjp_tensors(snapshot)


_SHA = "1" * 64
_IMAGE = f"sha256:{'2' * 64}"
_GPU_UUID = "GPU-12345678-1234-1234-1234-123456789abc"
_SCHEMA = (
    Path(__file__).resolve().parents[2]
    / "schemas"
    / "grid-sample-attribution-receipt.schema.json"
)


def _tensor_record(
    operation_id: str, role: str, *, variant: str = "same"
) -> dict[str, object]:
    name = f"{operation_id}.{role}"
    digest = hashlib.sha256(f"{name}:{variant}".encode()).hexdigest()
    return {
        "name": name,
        "role": role,
        "operation_id": operation_id,
        "shape": [1, 2],
        "dtype": "float32",
        "element_count": 2,
        "finite_count": 2,
        "non_finite_count": 0,
        "sha256": digest,
        "l2_norm": 1.0,
    }


def _operations(
    *,
    divergent_operation: str | None = None,
    divergent_role: str = "outgoing_value_gradient",
) -> list[dict[str, object]]:
    callback_order = tuple(reversed(OPERATION_IDS))
    return [
        {
            "operation_id": operation_id,
            "callback_order": callback_order.index(operation_id),
            "tensors": [
                _tensor_record(
                    operation_id,
                    role,
                    variant=(
                        "drift"
                        if operation_id == divergent_operation
                        and role == divergent_role
                        else "same"
                    ),
                )
                for role in (
                    "forward_value",
                    "forward_grid",
                    "forward_result",
                    "incoming_result_gradient",
                    "outgoing_value_gradient",
                    "outgoing_grid_gradient",
                )
            ],
        }
        for operation_id in OPERATION_IDS
    ]


def _parameters(*, variant: str = "same") -> dict[str, object]:
    records = [
        {
            **_tensor_record("model", "parameter_gradient", variant=variant),
            "name": name,
        }
        for name in ("detector.weight", "backbone.weight")
    ]
    return {
        "count": 2,
        "inventory_sha256": canonical_json_sha256({"parameters": records}),
        "parameters": records,
    }


def _artifact(path: str, *, names: list[str] | None = None) -> dict[str, object]:
    document: dict[str, object] = {"path": path, "size": 123, "sha256": _SHA}
    if names is not None:
        document.update(
            {
                "inventory_sha256": canonical_json_sha256({"names": names}),
                "names": names,
                "public_export_candidate": False,
            }
        )
    return document


def _seal_receipt(receipt: dict[str, object]) -> dict[str, object]:
    preimage = copy.deepcopy(receipt)
    preimage["metadata"].pop("receipt_content_sha256", None)
    receipt["metadata"]["receipt_content_sha256"] = canonical_json_sha256(preimage)
    return receipt


def _identity(kind: str, component_id: str) -> dict[str, object]:
    adapter_path = Path(attribution.__file__).resolve()
    tensor_path = adapter_path.with_name("tensor_evidence.py")
    adapter_sha256 = hashlib.sha256(adapter_path.read_bytes()).hexdigest()
    tensor_sha256 = hashlib.sha256(tensor_path.read_bytes()).hexdigest()
    source_sha256 = canonical_json_sha256(
        {
            "files": [
                {
                    "path": (
                        "src/vision_active_learning_loop/diagnostics/"
                        "grid_sample_attribution.py"
                    ),
                    "sha256": adapter_sha256,
                },
                {
                    "path": (
                        "src/vision_active_learning_loop/diagnostics/"
                        "tensor_evidence.py"
                    ),
                    "sha256": tensor_sha256,
                },
            ]
        }
    )
    return {
        "source_commit": "a" * 40,
        "image_id": _IMAGE,
        "base_image_digest": _IMAGE,
        "run_id": "wave0-a7-test",
        "component_kind": kind,
        "component_id": component_id,
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "gpu_uuid": _GPU_UUID,
        "model_sha256": _SHA,
        "config_sha256": _SHA,
        "processor_sha256": _SHA,
        "fixture_sha256": _SHA,
        "model_loss_source_sha256": (
            "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
        ),
        "adapter_source_sha256": adapter_sha256,
        "tensor_evidence_source_sha256": tensor_sha256,
        "source_sha256": source_sha256,
        "seed": 17,
        "precision": "BF16",
        "num_queries": 300,
        "decoder_layers": 3,
        "feature_levels": 3,
        "disable_custom_kernels": True,
    }


def _execution(subcommand: str) -> dict[str, object]:
    return {
        "argv": ["val", "diagnose", "grid-sample-attribution", subcommand],
        "exit_code": 0,
        "started_at": "2026-08-26T00:00:00+00:00",
        "ended_at": "2026-08-26T00:00:01+00:00",
        "runtime_seconds": 1.0,
        "peak_vram_bytes": 1024,
        "peak_reserved_vram_bytes": 2048,
        "loss_hex": "0x1.0000000000000p+0",
        "warning_evidence": {
            "count": 9,
            "operations": ["grid_sampler_2d_backward_cuda"] * 9,
        },
        "backend": {
            "math_only": True,
            "strict_restored": True,
            "autocast_bf16": True,
        },
    }


def _invariants() -> dict[str, bool]:
    return {
        "identity_verified": True,
        "parents_verified": True,
        "tensor_inventory_verified": True,
        "warnings_verified": True,
        "backend_restored": True,
        "publication_verified": True,
    }


def build_component_receipt(
    kind: str,
    index: int = 0,
    *,
    divergent_operation: str | None = None,
    divergent_role: str = "outgoing_value_gradient",
    parameter_variant: str = "same",
) -> dict[str, object]:
    component_id = (
        f"{kind}-{index}" if kind != "instrumented" else f"instrumented-{index}"
    )
    if kind == "isolated-vjp":
        component_id = f"isolated-vjp-{index}"
    names: list[str]
    normative: dict[str, object] = {
        "identity": _identity(kind, component_id),
        "parent_receipts": {
            "environment": _artifact("wave0/receipts/environment.json"),
            "model_assets": _artifact("wave0/receipts/model-assets.json"),
            "model_contract": _artifact("wave0/receipts/model-contract.json"),
        },
        "execution": _execution(kind),
        "invariants": _invariants(),
        "status": "RECORDED",
        "errors": [],
    }
    if kind == "control":
        parameters = _parameters(variant=parameter_variant)
        names = [record["name"] for record in parameters["parameters"]]
        normative["parameter_gradients"] = parameters
    elif kind == "instrumented":
        parameters = _parameters(variant=parameter_variant)
        operations = _operations(
            divergent_operation=divergent_operation,
            divergent_role=divergent_role,
        )
        names = [record["name"] for record in parameters["parameters"]]
        names.extend(
            record["name"]
            for operation in operations
            for record in operation["tensors"]
        )
        normative["parameter_gradients"] = parameters
        normative["operations"] = operations
        if index == 0:
            snapshot_names = sorted(
                f"{operation_id}.{role}"
                for operation_id in OPERATION_IDS
                for role in (
                    "forward_value",
                    "forward_grid",
                    "incoming_result_gradient",
                )
            )
            normative["vjp_snapshot"] = _artifact(
                "a7/components/instrumented-0/vjp-snapshot.vala7",
                names=snapshot_names,
            )
    else:
        operations = _operations(
            divergent_operation=divergent_operation,
            divergent_role=divergent_role,
        )
        names = [
            record["name"]
            for operation in operations
            for record in operation["tensors"]
        ]
        normative["operations"] = operations
        normative["parent_receipts"]["instrumented"] = _artifact(
            "a7/components/instrumented-0/receipt.json"
        )
        normative["vjp_snapshot"] = _artifact(
            "a7/components/instrumented-0/vjp-snapshot.vala7",
            names=sorted(
                f"{operation_id}.{role}"
                for operation_id in OPERATION_IDS
                for role in (
                    "forward_value",
                    "forward_grid",
                    "incoming_result_gradient",
                )
            ),
        )
    normative["tensor_bundle"] = _artifact(
        f"a7/components/{component_id}/tensor-bundle.vala7", names=sorted(names)
    )
    return _seal_receipt(
        {
            "receipt_type": "grid-sample-attribution",
            "schema_version": 1,
            "normative": normative,
            "metadata": {
                "timestamp": "2026-08-26T00:00:02+00:00",
                "run_id": "wave0-a7-test",
            },
        }
    )


def build_aggregate_receipt(*, attributed: bool = True) -> dict[str, object]:
    candidate = OPERATION_IDS[0]
    controls = [
        build_component_receipt("control", index)["normative"] for index in range(2)
    ]
    instrumented = [
        build_component_receipt(
            "instrumented",
            index,
            divergent_operation=candidate if attributed and index == 1 else None,
        )["normative"]
        for index in range(5)
    ]
    isolated = [
        build_component_receipt(
            "isolated-vjp",
            index,
            divergent_operation=candidate if attributed and index == 1 else None,
        )["normative"]
        for index in range(5)
    ]
    status = "ATTRIBUTED" if attributed else "INCONCLUSIVE"
    terminal = (
        "WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
        if attributed
        else "WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
    )
    parent_components = []
    for normative in (*controls, *instrumented, *isolated):
        component_id = normative["identity"]["component_id"]
        parent_components.append(
            {
                "component_id": component_id,
                "receipt": _artifact(f"a7/components/{component_id}/receipt.json"),
                "tensor_bundle": copy.deepcopy(normative["tensor_bundle"]),
            }
        )
    reason_codes = [] if attributed else ["model_divergence_not_reproduced"]
    classification = {
        "status": status,
        "candidate_operation": candidate if attributed else None,
        "candidate_role": "outgoing_value_gradient" if attributed else None,
        "reason_codes": reason_codes,
        "terminal": terminal,
    }
    comparisons = _comparison_inventory(controls, instrumented, isolated)
    return _seal_receipt(
        {
            "receipt_type": "grid-sample-attribution",
            "schema_version": 1,
            "normative": {
                "identity": _identity("aggregate", "aggregate"),
                "parent_receipts": {
                    "environment": _artifact("wave0/receipts/environment.json"),
                    "model_assets": _artifact("wave0/receipts/model-assets.json"),
                    "model_contract": _artifact("wave0/receipts/model-contract.json"),
                },
                "execution": _execution("aggregate"),
                "components": {
                    "controls": controls,
                    "instrumented": instrumented,
                    "isolated": isolated,
                },
                "parent_components": parent_components,
                "comparisons": comparisons,
                "classification": classification,
                "invariants": _invariants(),
                "status": status,
                "terminal": terminal,
                "errors": list(reason_codes),
            },
            "metadata": {
                "timestamp": "2026-08-26T00:00:03+00:00",
                "run_id": "wave0-a7-test",
            },
        }
    )


def _records_by_name(
    component: dict[str, object], *, parameters: bool
) -> dict[str, dict[str, object]]:
    records = (
        component["parameter_gradients"]["parameters"]
        if parameters
        else [
            tensor
            for operation in component["operations"]
            for tensor in operation["tensors"]
        ]
    )
    return {record["name"]: record for record in records}


def _comparison_pair(
    left: dict[str, object], right: dict[str, object], *, parameters: bool
) -> dict[str, object]:
    left_id = left["identity"]["component_id"]
    right_id = right["identity"]["component_id"]
    left_records = _records_by_name(left, parameters=parameters)
    right_records = _records_by_name(right, parameters=parameters)
    assert set(left_records) == set(right_records)
    records = []
    for name in sorted(left_records):
        exact = left_records[name]["sha256"] == right_records[name]["sha256"]
        records.append(
            {
                "left_replica": left_id,
                "right_replica": right_id,
                "name": name,
                "exact_digest_equal": exact,
                "difference_l2": 0.0 if exact else 1.0,
                "relative_l2": 0.0 if exact else 1.0,
                "cosine": 1.0 if exact else 0.0,
            }
        )
    left_inventory = left.get("parameter_gradients", {}).get("inventory_sha256")
    right_inventory = right.get("parameter_gradients", {}).get("inventory_sha256")
    return {
        "left_replica": left_id,
        "right_replica": right_id,
        "inventory_digest_equal": (
            left_inventory == right_inventory if parameters else True
        ),
        "tensors": records,
    }


def _comparison_inventory(
    controls: list[dict[str, object]],
    instrumented: list[dict[str, object]],
    isolated: list[dict[str, object]],
) -> dict[str, object]:
    model_components = [*controls, *instrumented]
    return {
        "callback_order": [
            operation_id
            for _, operation_id in sorted(
                (operation["callback_order"], operation["operation_id"])
                for operation in instrumented[0]["operations"]
            )
        ],
        "parameter_pairs": [
            _comparison_pair(left, right, parameters=True)
            for left, right in combinations(model_components, 2)
        ],
        "instrumented_pairs": [
            _comparison_pair(left, right, parameters=False)
            for left, right in combinations(instrumented, 2)
        ],
        "isolated_pairs": [
            _comparison_pair(left, right, parameters=False)
            for left, right in combinations(isolated, 2)
        ],
    }


@pytest.mark.parametrize(
    "receipt",
    [
        build_component_receipt("control", 0),
        build_component_receipt("instrumented", 0),
        build_component_receipt("isolated-vjp", 0),
        build_aggregate_receipt(),
    ],
)
def test_grid_sample_attribution_receipt_schema_accepts_all_closed_branches(
    receipt: dict[str, object],
) -> None:
    validate_receipt(receipt, _SCHEMA)


@pytest.mark.parametrize(
    "mutation",
    [
        "extra",
        "wrong_status",
        "nonzero_exit",
        "missing_operation",
        "snapshot_wrong_replica",
        "pass_token",
    ],
)
def test_grid_sample_attribution_schema_rejects_closed_branch_mutations(
    mutation: str,
) -> None:
    receipt = build_component_receipt("instrumented", 1)
    normative = receipt["normative"]
    if mutation == "extra":
        normative["unexpected"] = True
    elif mutation == "wrong_status":
        normative["status"] = "ATTRIBUTED"
    elif mutation == "nonzero_exit":
        normative["execution"]["exit_code"] = 1
    elif mutation == "missing_operation":
        normative["operations"].pop()
    elif mutation == "snapshot_wrong_replica":
        normative["vjp_snapshot"] = _artifact("wrong", names=[])
    else:
        normative["status"] = "PASS"
    with pytest.raises(ReceiptValidationError):
        validate_receipt(receipt, _SCHEMA)


def test_classify_aggregate_attributes_first_eligible_callback_divergence() -> None:
    receipt = build_aggregate_receipt(attributed=True)
    components = receipt["normative"]["components"]

    classification = classify_aggregate(
        components["controls"], components["instrumented"], components["isolated"]
    )

    assert classification == receipt["normative"]["classification"]


def test_classify_aggregate_uses_the_isolated_confirmed_divergent_role() -> None:
    candidate = OPERATION_IDS[0]
    controls = [
        build_component_receipt("control", index)["normative"] for index in range(2)
    ]
    instrumented = [
        build_component_receipt(
            "instrumented",
            index,
            divergent_operation=candidate if index == 1 else None,
        )["normative"]
        for index in range(5)
    ]
    grid_drift = _tensor_record(candidate, "outgoing_grid_gradient", variant="drift")
    for tensor in instrumented[1]["operations"][0]["tensors"]:
        if tensor["role"] == "outgoing_grid_gradient":
            tensor.update(grid_drift)
    isolated = [
        build_component_receipt(
            "isolated-vjp",
            index,
            divergent_operation=candidate if index == 1 else None,
            divergent_role="outgoing_grid_gradient",
        )["normative"]
        for index in range(5)
    ]

    classification = classify_aggregate(controls, instrumented, isolated)

    assert classification["status"] == "ATTRIBUTED"
    assert classification["candidate_operation"] == candidate
    assert classification["candidate_role"] == "outgoing_grid_gradient"


def test_inconclusive_aggregate_receipt_binds_reason_codes_to_errors() -> None:
    receipt = build_aggregate_receipt(attributed=False)

    validate_receipt(receipt, _SCHEMA)

    normative = receipt["normative"]
    assert normative["status"] == "INCONCLUSIVE"
    assert normative["errors"] == normative["classification"]["reason_codes"]
    assert normative["errors"]


def test_classify_aggregate_not_attributed_requires_parameter_divergence() -> None:
    controls = [
        build_component_receipt("control", index)["normative"] for index in range(2)
    ]
    instrumented = [
        build_component_receipt(
            "instrumented", index, parameter_variant="drift" if index == 1 else "same"
        )["normative"]
        for index in range(5)
    ]
    isolated = [
        build_component_receipt("isolated-vjp", index)["normative"]
        for index in range(5)
    ]

    classification = classify_aggregate(controls, instrumented, isolated)

    assert classification["status"] == "NOT_ATTRIBUTED"
    assert classification["candidate_operation"] is None


@pytest.mark.parametrize("mutation", ["identity", "forward", "earlier", "isolated"])
def test_classify_aggregate_fails_closed_on_instrumentation_or_proof_drift(
    mutation: str,
) -> None:
    receipt = build_aggregate_receipt(attributed=True)
    components = receipt["normative"]["components"]
    if mutation == "identity":
        components["instrumented"][1]["identity"]["source_commit"] = "b" * 40
    elif mutation == "forward":
        components["instrumented"][1]["operations"][0]["tensors"][0]["sha256"] = (
            "f" * 64
        )
    elif mutation == "earlier":
        components["instrumented"][1]["operations"][-2]["tensors"][-1]["sha256"] = (
            "e" * 64
        )
    else:
        components["isolated"][1]["operations"][0]["tensors"][-2][
            "sha256"
        ] = components["isolated"][0]["operations"][0]["tensors"][-2]["sha256"]

    classification = classify_aggregate(
        components["controls"], components["instrumented"], components["isolated"]
    )

    assert classification["status"] == "INCONCLUSIVE"


def test_identity_document_binds_both_diagnostic_source_files() -> None:
    adapter_path = Path(attribution.__file__).resolve()
    tensor_path = adapter_path.with_name("tensor_evidence.py")
    adapter_sha256 = hashlib.sha256(adapter_path.read_bytes()).hexdigest()
    tensor_sha256 = hashlib.sha256(tensor_path.read_bytes()).hexdigest()
    source_inventory_sha256 = canonical_json_sha256(
        {
            "files": [
                {
                    "path": "src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py",
                    "sha256": adapter_sha256,
                },
                {
                    "path": "src/vision_active_learning_loop/diagnostics/tensor_evidence.py",
                    "sha256": tensor_sha256,
                },
            ]
        }
    )
    parents = {
        "environment": {
            "normative": {
                "observed": {
                    "gpu_uuid": _GPU_UUID,
                    "gpu_name": "NVIDIA GeForce RTX 4090",
                    "runtime_image_digest": _IMAGE,
                    "container_image_digest": _IMAGE,
                }
            }
        }
    }
    inputs = SimpleNamespace(
        source_commit="a" * 40,
        image_id=_IMAGE,
        base_image_digest=_IMAGE,
        run_id="wave0-a7-test",
        component_id="control-0",
    )
    contract = {
        "model_sha256": _SHA,
        "config_file_sha256": _SHA,
        "processor_file_sha256": _SHA,
        "fixture_sha256": _SHA,
        "loss_source_sha256": "f" * 64,
    }

    identity = attribution._identity_document(parents, inputs, "control", contract)

    assert identity["model_loss_source_sha256"] == "f" * 64
    assert identity["adapter_source_sha256"] == adapter_sha256
    assert identity["tensor_evidence_source_sha256"] == tensor_sha256
    assert identity["source_sha256"] == source_inventory_sha256


def _cli_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    root = tmp_path / "artifacts"
    receipts_root = root / "wave0" / "receipts"
    receipts_root.mkdir(parents=True)
    for name in ("environment.json", "model-assets.json", "model-contract.json"):
        (receipts_root / name).write_text("{}", encoding="utf-8")
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(root))
    monkeypatch.setenv("VAL_SOURCE_COMMIT", "a" * 40)
    monkeypatch.setenv("VAL_IMAGE_ID", _IMAGE)
    monkeypatch.setenv("VAL_BASE_IMAGE_DIGEST", _IMAGE)
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    return root


def _publish_mock_bundle(
    root: Path, receipt: dict[str, object]
) -> dict[str, torch.Tensor]:
    normative = receipt["normative"]
    bundle = normative["tensor_bundle"]
    names = bundle["names"]
    records: dict[str, dict[str, object]] = {}
    parameters = normative.get("parameter_gradients")
    if isinstance(parameters, dict):
        records.update(
            {str(record["name"]): record for record in parameters["parameters"]}
        )
    for operation in normative.get("operations", []):
        records.update({str(record["name"]): record for record in operation["tensors"]})
    tensors: dict[str, torch.Tensor] = {}
    for name in names:
        record = records[name]
        drift_digest = hashlib.sha256(
            f"{record['operation_id']}.{record['role']}:drift".encode()
        ).hexdigest()
        offset = 0.25 if record["sha256"] == drift_digest else 0.0
        base = float(int(hashlib.sha256(name.encode()).hexdigest()[:8], 16) % 1000)
        tensor = torch.tensor([[base + offset, base + 1.0]], dtype=torch.float32)
        observed = attribution._tensor_evidence_document(
            attribution.observe_tensor(
                name,
                str(record["role"]),
                tensor,
                operation_id=str(record["operation_id"]),
            )
        )
        record.clear()
        record.update(observed)
        tensors[name] = tensor
    if isinstance(parameters, dict):
        parameters["inventory_sha256"] = canonical_json_sha256(
            {"parameters": parameters["parameters"]}
        )
    path = root / Path(bundle["path"])
    digest = atomic_write_snapshot(path, tensors)
    bundle["size"] = path.stat().st_size
    bundle["sha256"] = digest
    receipt["metadata"].pop("receipt_content_sha256", None)
    return tensors


def _publish_mock_vjp_snapshot(
    root: Path,
    receipt: dict[str, object],
    tensors: dict[str, torch.Tensor],
) -> dict[str, object]:
    snapshot = receipt["normative"]["vjp_snapshot"]
    selected = {name: tensors[name] for name in snapshot["names"]}
    path = root / Path(snapshot["path"])
    digest = atomic_write_snapshot(path, selected)
    snapshot["size"] = path.stat().st_size
    snapshot["sha256"] = digest
    receipt["metadata"].pop("receipt_content_sha256", None)
    return copy.deepcopy(snapshot)


def _stored_artifact(root: Path, path: Path) -> dict[str, object]:
    return {
        "path": path.relative_to(root).as_posix(),
        "size": path.stat().st_size,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


def test_engine_artifact_verification_rejects_bundle_tensor_evidence_mismatch(
    tmp_path: Path,
) -> None:
    root = tmp_path / "artifacts"
    component_root = root / "a7" / "components" / "control-0"
    component_root.mkdir(parents=True)
    receipt = build_component_receipt("control", 0)
    _publish_mock_bundle(root, receipt)
    receipt["normative"]["parameter_gradients"]["parameters"][0]["sha256"] = "b" * 64

    with pytest.raises(AttributionError, match="tensor evidence"):
        attribution._verify_engine_artifacts(root, component_root, receipt)


def test_lazy_manifest_discovers_grid_sample_attribution_command() -> None:
    source_root = Path(__file__).resolve().parents[2] / "src"
    manifest = build_manifest(source_root)

    assert manifest["diagnose grid-sample-attribution"] == (
        "vision_active_learning_loop.diagnostics.grid_sample_attribution:main"
    )


def test_control_cli_publishes_real_receipt_after_mock_engine_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    root = _cli_root(tmp_path, monkeypatch)
    component_root = root / "a7" / "components" / "control-0"
    component_root.mkdir(parents=True)
    output = component_root / "receipt.json"

    def fake_engine(inputs: object, *, instrumented: bool) -> dict[str, object]:
        assert instrumented is False
        receipt = build_component_receipt("control", 0)
        _publish_mock_bundle(root, receipt)
        return receipt

    monkeypatch.setattr(attribution, "run_model_replica", fake_engine)
    result = attribution.main(
        [
            "control",
            "--environment",
            str(root / "wave0" / "receipts" / "environment.json"),
            "--model-assets",
            str(root / "wave0" / "receipts" / "model-assets.json"),
            "--model-contract",
            str(root / "wave0" / "receipts" / "model-contract.json"),
            "--component-root",
            str(component_root),
            "--component-id",
            "control-0",
            "--source-commit",
            "a" * 40,
            "--run-id",
            "wave0-a7-test",
            "--output",
            str(output),
        ]
    )

    assert result == 0
    assert capsys.readouterr().out.strip() == "RECORDED"
    validate_receipt(json.loads(output.read_text(encoding="utf-8")), _SCHEMA)


def test_instrumented_cli_publishes_bundle_snapshot_and_receipt(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _cli_root(tmp_path, monkeypatch)
    component_root = root / "a7" / "components" / "instrumented-0"
    component_root.mkdir(parents=True)
    output = component_root / "receipt.json"
    snapshot = component_root / "vjp-snapshot.vala7"

    def fake_engine(inputs: object, *, instrumented: bool) -> dict[str, object]:
        assert instrumented is True
        receipt = build_component_receipt("instrumented", 0)
        tensors = _publish_mock_bundle(root, receipt)
        _publish_mock_vjp_snapshot(root, receipt, tensors)
        return receipt

    monkeypatch.setattr(attribution, "run_model_replica", fake_engine)
    result = attribution.main(
        [
            "instrumented",
            "--environment",
            str(root / "wave0" / "receipts" / "environment.json"),
            "--model-assets",
            str(root / "wave0" / "receipts" / "model-assets.json"),
            "--model-contract",
            str(root / "wave0" / "receipts" / "model-contract.json"),
            "--component-root",
            str(component_root),
            "--component-id",
            "instrumented-0",
            "--source-commit",
            "a" * 40,
            "--run-id",
            "wave0-a7-test",
            "--output",
            str(output),
            "--vjp-snapshot-output",
            str(snapshot),
        ]
    )

    assert result == 0
    assert output.is_file()
    assert snapshot.is_file()
    validate_receipt(json.loads(output.read_text(encoding="utf-8")), _SCHEMA)


def test_isolated_cli_publishes_bundle_from_fixed_parent_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _cli_root(tmp_path, monkeypatch)
    parent_root = root / "a7" / "components" / "instrumented-0"
    parent_root.mkdir(parents=True)
    parent_receipt = parent_root / "receipt.json"
    parent_receipt.write_text("{}", encoding="utf-8")
    component_root = root / "a7" / "components" / "isolated-vjp-0"
    component_root.mkdir(parents=True)
    output = component_root / "receipt.json"
    receipt = build_component_receipt("isolated-vjp", 0)
    tensors = _publish_mock_bundle(root, receipt)
    snapshot_artifact = _publish_mock_vjp_snapshot(root, receipt, tensors)
    (root / Path(receipt["normative"]["tensor_bundle"]["path"])).unlink()

    def fake_engine(inputs: object) -> dict[str, object]:
        _publish_mock_bundle(root, receipt)
        return receipt

    monkeypatch.setattr(attribution, "run_isolated_vjp_replica", fake_engine)
    result = attribution.main(
        [
            "isolated-vjp",
            "--environment",
            str(root / "wave0" / "receipts" / "environment.json"),
            "--model-assets",
            str(root / "wave0" / "receipts" / "model-assets.json"),
            "--model-contract",
            str(root / "wave0" / "receipts" / "model-contract.json"),
            "--parent-instrumented-receipt",
            str(parent_receipt),
            "--vjp-snapshot",
            str(root / snapshot_artifact["path"]),
            "--component-root",
            str(component_root),
            "--component-id",
            "isolated-vjp-0",
            "--source-commit",
            "a" * 40,
            "--run-id",
            "wave0-a7-test",
            "--output",
            str(output),
        ]
    )

    assert result == 0
    assert output.is_file()
    validate_receipt(json.loads(output.read_text(encoding="utf-8")), _SCHEMA)


def test_aggregate_cli_rereads_all_receipts_and_bound_bundles(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _cli_root(tmp_path, monkeypatch)
    components_root = root / "a7" / "components"
    aggregate_root = root / "a7" / "aggregate"
    components_root.mkdir(parents=True)
    aggregate_root.mkdir(parents=True)
    parent_artifacts = {
        name: _stored_artifact(
            root, root / "wave0" / "receipts" / f"{name.replace('_', '-')}.json"
        )
        for name in ("environment", "model_assets", "model_contract")
    }
    candidate = OPERATION_IDS[0]
    snapshot_artifact: dict[str, object] | None = None

    for kind, count in (("control", 2), ("instrumented", 5)):
        for index in range(count):
            component_id = f"{kind}-{index}"
            component_root = components_root / component_id
            component_root.mkdir()
            receipt = build_component_receipt(
                kind,
                index,
                divergent_operation=(
                    candidate if kind == "instrumented" and index == 1 else None
                ),
            )
            receipt["normative"]["parent_receipts"] = copy.deepcopy(parent_artifacts)
            tensors = _publish_mock_bundle(root, receipt)
            if component_id == "instrumented-0":
                snapshot_artifact = _publish_mock_vjp_snapshot(root, receipt, tensors)
            _seal_receipt(receipt)
            atomic_write_receipt(component_root / "receipt.json", receipt)

    assert snapshot_artifact is not None
    instrumented_parent = _stored_artifact(
        root, components_root / "instrumented-0" / "receipt.json"
    )
    for index in range(5):
        component_id = f"isolated-vjp-{index}"
        component_root = components_root / component_id
        component_root.mkdir()
        receipt = build_component_receipt(
            "isolated-vjp",
            index,
            divergent_operation=candidate if index == 1 else None,
        )
        receipt["normative"]["parent_receipts"] = {
            **copy.deepcopy(parent_artifacts),
            "instrumented": copy.deepcopy(instrumented_parent),
        }
        receipt["normative"]["vjp_snapshot"] = copy.deepcopy(snapshot_artifact)
        _publish_mock_bundle(root, receipt)
        _seal_receipt(receipt)
        atomic_write_receipt(component_root / "receipt.json", receipt)

    output = aggregate_root / "receipt.json"
    result = attribution.main(
        [
            "aggregate",
            "--environment",
            str(root / "wave0" / "receipts" / "environment.json"),
            "--model-assets",
            str(root / "wave0" / "receipts" / "model-assets.json"),
            "--model-contract",
            str(root / "wave0" / "receipts" / "model-contract.json"),
            "--components-root",
            str(components_root),
            "--source-commit",
            "a" * 40,
            "--run-id",
            "wave0-a7-test",
            "--output",
            str(output),
        ]
    )

    assert result == 0
    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["normative"]["status"] == "ATTRIBUTED"
    assert stored["normative"]["execution"]["runtime_seconds"] > 0.0
    assert (
        stored["normative"]["execution"]["started_at"]
        != stored["normative"]["execution"]["ended_at"]
    )
    validate_receipt(stored, _SCHEMA)


def test_aggregate_engine_copies_inconclusive_reason_codes_to_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = _cli_root(tmp_path, monkeypatch)
    components_root = root / "a7" / "components"
    aggregate_root = root / "a7" / "aggregate"
    components_root.mkdir(parents=True)
    aggregate_root.mkdir(parents=True)
    fixture = build_aggregate_receipt(attributed=False)["normative"]
    components = fixture["components"]
    expected_ids = [
        *(f"control-{index}" for index in range(2)),
        *(f"instrumented-{index}" for index in range(5)),
        *(f"isolated-vjp-{index}" for index in range(5)),
    ]
    documents = {
        component["identity"]["component_id"]: {"normative": component}
        for component in (
            *components["controls"],
            *components["instrumented"],
            *components["isolated"],
        )
    }
    monkeypatch.setattr(
        attribution, "_validate_component_directory_inventory", lambda *_: None
    )
    monkeypatch.setattr(
        attribution,
        "_read_mapping",
        lambda path: documents[Path(path).parent.name],
    )
    monkeypatch.setattr(attribution, "validate_receipt_for_run", lambda *_: None)
    monkeypatch.setattr(attribution, "_verify_engine_artifacts", lambda *_: None)
    monkeypatch.setattr(
        attribution,
        "_build_aggregate_comparisons",
        lambda *_: copy.deepcopy(fixture["comparisons"]),
    )
    monkeypatch.setattr(
        attribution,
        "_file_artifact",
        lambda _root, path: _artifact(Path(path).as_posix()),
    )
    parsed = SimpleNamespace(
        components_root=components_root,
        output=aggregate_root / "receipt.json",
        source_commit="a" * 40,
        run_id="wave0-a7-test",
        environment=root / "wave0" / "receipts" / "environment.json",
        model_assets=root / "wave0" / "receipts" / "model-assets.json",
        model_contract=root / "wave0" / "receipts" / "model-contract.json",
    )

    receipt = attribution._run_aggregate_cli(
        parsed,
        root,
        ("val", "diagnose", "grid-sample-attribution", "aggregate"),
    )

    assert set(documents) == set(expected_ids)
    normative = receipt["normative"]
    assert normative["status"] == "INCONCLUSIVE"
    assert normative["errors"] == normative["classification"]["reason_codes"]
    assert normative["errors"] == ["model_divergence_not_reproduced"]


@pytest.mark.parametrize("case", ["wrong_output", "data_root", "existing_bundle"])
def test_component_cli_fails_closed_before_engine_on_path_or_environment_drift(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, case: str
) -> None:
    root = _cli_root(tmp_path, monkeypatch)
    component_root = root / "a7" / "components" / "control-0"
    component_root.mkdir(parents=True)
    output = component_root / "receipt.json"
    if case == "wrong_output":
        output = component_root / "wrong.json"
    elif case == "data_root":
        monkeypatch.setenv("VAL_DATA_ROOT", str(tmp_path / "rdd"))
    else:
        (component_root / "tensor-bundle.vala7").write_bytes(b"existing")
    called = False

    def fake_engine(inputs: object, *, instrumented: bool) -> dict[str, object]:
        nonlocal called
        called = True
        return build_component_receipt("control", 0)

    monkeypatch.setattr(attribution, "run_model_replica", fake_engine)
    result = attribution.main(
        [
            "control",
            "--environment",
            str(root / "wave0" / "receipts" / "environment.json"),
            "--model-assets",
            str(root / "wave0" / "receipts" / "model-assets.json"),
            "--model-contract",
            str(root / "wave0" / "receipts" / "model-contract.json"),
            "--component-root",
            str(component_root),
            "--component-id",
            "control-0",
            "--source-commit",
            "a" * 40,
            "--run-id",
            "wave0-a7-test",
            "--output",
            str(output),
        ]
    )

    assert result == 2
    assert called is False
    assert not (component_root / "receipt.json").exists()


def test_aggregate_component_directory_inventory_rejects_any_extra_entry(
    tmp_path: Path,
) -> None:
    components_root = tmp_path / "components"
    components_root.mkdir()
    expected_ids = [
        *(f"control-{index}" for index in range(2)),
        *(f"instrumented-{index}" for index in range(5)),
        *(f"isolated-vjp-{index}" for index in range(5)),
    ]
    for component_id in expected_ids:
        (components_root / component_id).mkdir()

    attribution._validate_component_directory_inventory(components_root, expected_ids)
    (components_root / "unexpected.txt").write_text("drift", encoding="utf-8")

    with pytest.raises(AttributionError, match="inventory"):
        attribution._validate_component_directory_inventory(
            components_root, expected_ids
        )


def test_a7_powershell_runner_has_exact_component_order_and_forbidden_tokens() -> None:
    script = Path(__file__).resolve().parents[2] / "scripts" / "run_wave0_a7.ps1"
    text = script.read_text(encoding="utf-8")
    expected = [
        "control-0",
        "control-1",
        *(f"instrumented-{index}" for index in range(5)),
        *(f"isolated-vjp-{index}" for index in range(5)),
    ]
    positions = [text.index(component_id) for component_id in expected]

    assert positions == sorted(positions)
    assert "'--network', 'none'" in text
    assert "'--gpus', 'all'" in text
    assert "FileMode]::CreateNew" in text
    assert "30-historical-preservation.json" in text
    assert "51-campaign-closure-manifest.json" in text
    assert "[System.IO.File]::Move" in text
    assert "function Release-A7Lease" in text
    assert "function Test-Task7AuditBinding" in text
    assert "20-image-build-result.json" in text
    assert "22-a7-cpu-micro-check.json" in text
    assert "$Lease.campaign_root" in text
    assert "$Environment.normative.observed.gpu_uuid -ne $Lease.gpu_uuid" in text
    assert "expected_artifacts" in text
    stage = text[
        text.index("function Invoke-A7Stage") : text.index(
            "if (Test-Path Env:VAL_DATA_ROOT)"
        )
    ]
    assert "$ImageDigest" in stage
    assert "$ImageDigest\n    ) + $Command" in stage
    assert "$Host =" not in text
    for forbidden in (
        "gate wave0",
        "training-feasibility",
        "VAL_DATA_ROOT=/",
        "start wave1",
        "docker context use",
        "prune",
        "retry loop",
    ):
        assert forbidden.lower() not in text.lower()


def test_a7_powershell_runner_parses(tmp_path: Path) -> None:
    powershell = shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is unavailable")
    script = Path(__file__).resolve().parents[2] / "scripts" / "run_wave0_a7.ps1"
    command = (
        "$tokens=$null;$errors=$null;"
        f"[void][Management.Automation.Language.Parser]::ParseFile('{script}',[ref]$tokens,[ref]$errors);"
        "if($errors.Count){$errors|% Message;exit 1}"
    )
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr


def test_a7_powershell_runner_helpers_preserve_empty_output_and_exit_code(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    powershell = shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is unavailable")
    script = Path(__file__).resolve().parents[2] / "scripts" / "run_wave0_a7.ps1"
    output = tmp_path / "empty.log"
    monkeypatch.setenv("VAL_TEST_A7_SCRIPT", str(script))
    monkeypatch.setenv("VAL_TEST_A7_EMPTY_LOG", str(output))
    command = r"""
$ErrorActionPreference = 'Stop'
$Tokens = $null
$ParseErrors = $null
$Ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $env:VAL_TEST_A7_SCRIPT,
    [ref]$Tokens,
    [ref]$ParseErrors
)
if ($ParseErrors.Count -ne 0) { throw 'A7 script did not parse' }
foreach ($FunctionName in @('Write-NewText', 'Invoke-NativeCommandCapture')) {
    $Function = $Ast.Find({
        param($Node)
        $Node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
            $Node.Name -eq $FunctionName
    }, $true)
    if ($null -eq $Function) { throw "missing helper: $FunctionName" }
    Invoke-Expression $Function.Extent.Text
}
Write-NewText -Path $env:VAL_TEST_A7_EMPTY_LOG -Text ''
$Result = Invoke-NativeCommandCapture -FilePath 'cmd.exe' -ArgumentList @(
    '/d', '/c', 'echo diagnostic 1>&2 & exit /b 7'
)
[pscustomobject]@{
    text = $Result.Text
    exit_code = $Result.ExitCode
    preference = $ErrorActionPreference.ToString()
} | ConvertTo-Json -Compress
"""
    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert output.read_bytes() == b""
    payload = json.loads(completed.stdout)
    assert payload["text"].strip() == "diagnostic"
    assert payload["exit_code"] == 7
    assert payload["preference"] == "Stop"
