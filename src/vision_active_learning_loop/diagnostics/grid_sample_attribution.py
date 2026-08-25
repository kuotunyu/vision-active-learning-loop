"""Bounded diagnostics for the pinned RT-DETR CUDA grid-sample seam."""

from __future__ import annotations

import argparse
import copy
import json
import os
import subprocess
import sys
import time
from collections.abc import Callable, Mapping, Sequence
from contextlib import nullcontext
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

import torch
from torch.nn import functional

from ..artifacts.digests import canonical_json_sha256, sha256_file
from ..artifacts.receipts import atomic_write_receipt, validate_receipt_for_run
from ..cli_manifest import command
from .tensor_evidence import (
    TensorEvidence,
    TensorEvidenceError,
    atomic_write_snapshot,
    canonical_tensor_bytes,
    compare_tensors,
    decode_snapshot,
    observe_tensor,
)

OPERATION_IDS = tuple(
    f"decoder-{decoder}/feature-{feature}"
    for decoder in range(3)
    for feature in range(3)
)
_OPERATION_ROLES = (
    "forward_value",
    "forward_grid",
    "forward_result",
    "incoming_result_gradient",
    "outgoing_value_gradient",
    "outgoing_grid_gradient",
)
_VJP_ROLES = (
    "forward_value",
    "forward_grid",
    "incoming_result_gradient",
)
_ORIGINAL_GRID_SAMPLE = functional.grid_sample


class AttributionError(ValueError):
    """Raised when the A7 observation seam is incomplete or changes execution."""


@dataclass
class OperationCapture:
    """All tensor roles captured for one stable grid-sample operation."""

    operation_id: str
    callback_order: int | None
    tensors: dict[str, torch.Tensor]


@dataclass(frozen=True)
class ModelReplicaInputs:
    """Paths and immutable identities for one model-level replica."""

    environment: Path
    model_assets: Path
    model_contract: Path
    component_root: Path
    component_id: str
    run_id: str
    source_commit: str
    image_id: str
    base_image_digest: str
    argv: tuple[str, ...]
    vjp_snapshot_output: Path | None


@dataclass(frozen=True)
class IsolatedReplicaInputs:
    """Paths and immutable identities for one isolated VJP replica."""

    environment: Path
    model_assets: Path
    model_contract: Path
    parent_instrumented_receipt: Path
    vjp_snapshot: Path
    component_root: Path
    component_id: str
    run_id: str
    source_commit: str
    image_id: str
    base_image_digest: str
    argv: tuple[str, ...]


class ModelRecorder:
    """Retain live autograd tensors while storing only immutable evidence copies."""

    def __init__(
        self, *, expected_operation_ids: Sequence[str] = OPERATION_IDS
    ) -> None:
        expected = tuple(expected_operation_ids)
        if not expected or len(expected) != len(set(expected)):
            raise AttributionError(
                "expected operation IDs must be unique and non-empty"
            )
        if any(operation_id not in OPERATION_IDS for operation_id in expected):
            raise AttributionError("unexpected operation ID inventory")
        self._expected = expected
        self._captures: dict[str, OperationCapture] = {}
        self._live: dict[str, tuple[torch.Tensor, torch.Tensor, torch.Tensor]] = {}
        self._callback_ids: list[str] = []
        self._finalized = False

    def observe_forward(
        self,
        operation_id: str,
        value: torch.Tensor,
        grid: torch.Tensor,
        result: torch.Tensor,
    ) -> None:
        """Record an original-call result without changing the live result path."""
        if self._finalized:
            raise AttributionError("recorder is already finalized")
        if operation_id not in self._expected:
            raise AttributionError(f"unexpected operation ID: {operation_id}")
        if operation_id in self._captures:
            raise AttributionError(f"duplicate operation capture: {operation_id}")
        tensors = {
            "forward_value": _evidence_copy(value, operation_id, "forward_value"),
            "forward_grid": _evidence_copy(grid, operation_id, "forward_grid"),
            "forward_result": _evidence_copy(result, operation_id, "forward_result"),
        }
        self._captures[operation_id] = OperationCapture(operation_id, None, tensors)
        self._live[operation_id] = (value, grid, result)

    def incoming_gradient_hook(
        self, operation_id: str
    ) -> Callable[[torch.Tensor], torch.Tensor | None]:
        """Return a hook that observes, but never replaces, an incoming gradient."""
        if operation_id not in self._expected:
            raise AttributionError(f"unexpected operation ID: {operation_id}")

        def observe(incoming: torch.Tensor) -> None:
            capture = self._captures.get(operation_id)
            if capture is None:
                raise AttributionError("incoming gradient preceded forward capture")
            if operation_id in self._callback_ids:
                raise AttributionError(f"duplicate callback for {operation_id}")
            try:
                copied = _evidence_copy(
                    incoming, operation_id, "incoming_result_gradient"
                )
            except AttributionError as error:
                raise AttributionError(
                    "non-finite or invalid incoming gradient"
                ) from error
            capture.callback_order = len(self._callback_ids)
            capture.tensors["incoming_result_gradient"] = copied
            self._callback_ids.append(operation_id)

        return observe

    def finalize(self) -> tuple[OperationCapture, ...]:
        """Read retained outgoing gradients after backward and close the recorder."""
        if self._finalized:
            raise AttributionError("recorder is already finalized")
        if tuple(self._captures) != self._expected:
            raise AttributionError(
                "forward operation inventory is missing or reordered"
            )
        if set(self._callback_ids) != set(self._expected) or len(
            self._callback_ids
        ) != len(self._expected):
            raise AttributionError("backward callback inventory is incomplete")
        for operation_id in self._expected:
            capture = self._captures[operation_id]
            value, grid, result = self._live[operation_id]
            if value.grad is None or grid.grad is None or result.grad is None:
                raise AttributionError(f"missing retained gradient for {operation_id}")
            incoming = capture.tensors.get("incoming_result_gradient")
            if incoming is None:
                raise AttributionError(f"missing incoming gradient for {operation_id}")
            if canonical_tensor_bytes(result.grad) != canonical_tensor_bytes(incoming):
                raise AttributionError(
                    "result .grad differs from observed incoming gradient"
                )
            capture.tensors["outgoing_value_gradient"] = _evidence_copy(
                value.grad, operation_id, "outgoing_value_gradient"
            )
            capture.tensors["outgoing_grid_gradient"] = _evidence_copy(
                grid.grad, operation_id, "outgoing_grid_gradient"
            )
            if tuple(capture.tensors) != _OPERATION_ROLES:
                raise AttributionError("operation tensor role inventory is not exact")
        self._finalized = True
        self._live.clear()
        return tuple(self._captures[operation_id] for operation_id in self._expected)


class GridSampleAttributionAdapter(torch.nn.Module):
    """Temporarily intercept exactly three original grid-sample calls."""

    def __init__(
        self, wrapped: torch.nn.Module, decoder_layer: int, recorder: ModelRecorder
    ) -> None:
        super().__init__()
        if not isinstance(wrapped, torch.nn.Module):
            raise AttributionError("wrapped attention must be a torch module")
        if decoder_layer not in range(3):
            raise AttributionError("decoder layer must be 0, 1, or 2")
        if not isinstance(recorder, ModelRecorder):
            raise AttributionError("recorder must be a ModelRecorder")
        self.wrapped = wrapped
        self.decoder_layer = decoder_layer
        self.recorder = recorder
        self._active = False

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
        """Delegate unchanged while observing the exact original callable results."""
        if self._active:
            raise AttributionError("grid-sample adapter reentry is forbidden")
        if functional.grid_sample is not _ORIGINAL_GRID_SAMPLE:
            raise AttributionError("grid-sample callable entry drift")
        original_grid_sample = functional.grid_sample
        call_count = 0

        def intercepted_grid_sample(
            value,
            grid,
            mode="bilinear",
            padding_mode="zeros",
            align_corners=None,
        ):
            nonlocal call_count
            if call_count >= 3:
                raise AttributionError("extra grid_sample call in decoder adapter")
            if (
                mode != "bilinear"
                or padding_mode != "zeros"
                or align_corners is not False
            ):
                raise AttributionError(
                    "grid_sample arguments differ from pinned contract"
                )
            operation_id = f"decoder-{self.decoder_layer}/feature-{call_count}"
            result = original_grid_sample(
                value,
                grid,
                mode=mode,
                padding_mode=padding_mode,
                align_corners=align_corners,
            )
            self.recorder.observe_forward(operation_id, value, grid, result)
            try:
                value.retain_grad()
                grid.retain_grad()
                result.retain_grad()
                result.register_hook(self.recorder.incoming_gradient_hook(operation_id))
            except RuntimeError as error:
                raise AttributionError(
                    "grid_sample operands and result must require gradients"
                ) from error
            call_count += 1
            return result

        self._active = True
        functional.grid_sample = intercepted_grid_sample
        try:
            output = self.wrapped(
                value,
                value_spatial_shapes,
                value_spatial_shapes_list,
                level_start_index,
                sampling_locations,
                attention_weights,
                im2col_step,
            )
        finally:
            restoration_drift = functional.grid_sample is not intercepted_grid_sample
            functional.grid_sample = original_grid_sample
            self._active = False
            if restoration_drift:
                raise AttributionError("grid-sample callable restoration drift")
        if call_count != 3:
            raise AttributionError(
                "decoder adapter requires exactly three grid_sample calls"
            )
        return output


def install_adapters(
    model: torch.nn.Module, recorder: ModelRecorder
) -> tuple[GridSampleAttributionAdapter, ...]:
    """Install exactly three adapters at the pinned RT-DETR module paths."""
    try:
        layers = model.model.decoder.layers
    except AttributeError as error:
        raise AttributionError("pinned decoder module path is unavailable") from error
    if not isinstance(layers, (torch.nn.ModuleList, list, tuple)) or len(layers) != 3:
        raise AttributionError("pinned model must have exactly three decoder layers")
    adapters: list[GridSampleAttributionAdapter] = []
    for index, layer in enumerate(layers):
        try:
            wrapped = layer.encoder_attn.attn
        except AttributeError as error:
            raise AttributionError(
                "pinned attention module path is unavailable"
            ) from error
        if not isinstance(wrapped, torch.nn.Module):
            raise AttributionError("pinned attention module path is not a module")
        adapter = GridSampleAttributionAdapter(wrapped, index, recorder)
        layer.encoder_attn.attn = adapter
        adapters.append(adapter)
    return tuple(adapters)


def capture_parameter_gradients(
    model: torch.nn.Module,
    *,
    canonical_parameters: Sequence[tuple[str, torch.nn.Parameter]] | None = None,
) -> dict[str, object]:
    """Capture every trainable parameter gradient in registered model order."""
    if not isinstance(model, torch.nn.Module):
        raise AttributionError("parameter inventory requires a torch module")
    try:
        named = list(model.named_parameters(remove_duplicate=False))
    except TypeError:
        named = list(model.named_parameters())
    live_trainable = [
        (name, parameter) for name, parameter in named if parameter.requires_grad
    ]
    trainable = (
        list(canonical_parameters)
        if canonical_parameters is not None
        else live_trainable
    )
    if not trainable:
        raise AttributionError("model has no trainable parameters")
    identities = [id(parameter) for _, parameter in trainable]
    names = [name for name, _ in trainable]
    live_identities = [id(parameter) for _, parameter in live_trainable]
    if (
        any(
            not isinstance(name, str)
            or not name
            or not isinstance(parameter, torch.nn.Parameter)
            or not parameter.requires_grad
            for name, parameter in trainable
        )
        or len(identities) != len(set(identities))
        or len(names) != len(set(names))
        or len(live_identities) != len(set(live_identities))
        or set(identities) != set(live_identities)
    ):
        raise AttributionError("duplicate trainable parameter record")
    records: list[dict[str, object]] = []
    for name, parameter in trainable:
        if parameter.grad is None:
            raise AttributionError(f"missing parameter gradient: {name}")
        try:
            evidence = observe_tensor(
                name,
                "parameter_gradient",
                parameter.grad,
                operation_id="model",
            )
        except TensorEvidenceError as error:
            raise AttributionError(f"invalid parameter gradient: {name}") from error
        records.append(_tensor_evidence_document(evidence))
    inventory_sha256 = canonical_json_sha256({"parameters": records})
    return {
        "count": len(records),
        "inventory_sha256": inventory_sha256,
        "parameters": records,
    }


def run_isolated_vjp_tensors(
    tensors: Mapping[str, torch.Tensor],
) -> dict[str, object]:
    """Run the nine original grid-sample VJPs from one verified tensor inventory."""
    expected_names = {
        f"{operation_id}.{role}"
        for operation_id in OPERATION_IDS
        for role in _VJP_ROLES
    }
    if set(tensors) != expected_names or len(tensors) != len(expected_names):
        raise AttributionError("isolated VJP snapshot must contain exactly 27 tensors")

    devices = {tensor.device.type for tensor in tensors.values()}
    if len(devices) != 1 or not devices <= {"cpu", "cuda"}:
        raise AttributionError("isolated VJP tensors must share one CPU or CUDA device")
    cuda_forward = devices == {"cuda"}
    forward_context = (
        torch.autocast(device_type="cuda", dtype=torch.bfloat16)
        if cuda_forward
        else nullcontext()
    )
    live: list[tuple[str, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]] = []
    results: list[torch.Tensor] = []
    incoming_gradients: list[torch.Tensor] = []
    with forward_context:
        autocast_observed = bool(torch.is_autocast_enabled("cuda"))
        for operation_id in OPERATION_IDS:
            value = _validated_vjp_tensor(
                tensors[f"{operation_id}.forward_value"],
                operation_id,
                "forward_value",
            ).requires_grad_(True)
            grid = _validated_vjp_tensor(
                tensors[f"{operation_id}.forward_grid"], operation_id, "forward_grid"
            ).requires_grad_(True)
            incoming = _validated_vjp_tensor(
                tensors[f"{operation_id}.incoming_result_gradient"],
                operation_id,
                "incoming_result_gradient",
            )
            result = _ORIGINAL_GRID_SAMPLE(
                value,
                grid,
                mode="bilinear",
                padding_mode="zeros",
                align_corners=False,
            )
            if result.shape != incoming.shape or result.dtype != incoming.dtype:
                raise AttributionError(
                    "isolated VJP incoming gradient shape or dtype mismatch"
                )
            live.append((operation_id, value, grid, result, incoming))
            results.append(result)
            incoming_gradients.append(incoming)

    warning_evidence = _run_allowlisted_backward(
        lambda: torch.autograd.backward(tuple(results), tuple(incoming_gradients)),
        expected_count=9,
    )
    if not isinstance(warning_evidence, Mapping) or warning_evidence.get("count") != 9:
        raise AttributionError(
            "isolated VJP warning evidence must contain nine warnings"
        )

    captures: list[OperationCapture] = []
    for operation_id, value, grid, result, incoming in live:
        if value.grad is None or grid.grad is None:
            raise AttributionError("isolated VJP outgoing gradient is missing")
        captured = {
            "forward_value": _evidence_copy(value, operation_id, "forward_value"),
            "forward_grid": _evidence_copy(grid, operation_id, "forward_grid"),
            "forward_result": _evidence_copy(result, operation_id, "forward_result"),
            "incoming_result_gradient": _evidence_copy(
                incoming, operation_id, "incoming_result_gradient"
            ),
            "outgoing_value_gradient": _evidence_copy(
                value.grad, operation_id, "outgoing_value_gradient"
            ),
            "outgoing_grid_gradient": _evidence_copy(
                grid.grad, operation_id, "outgoing_grid_gradient"
            ),
        }
        captures.append(OperationCapture(operation_id, None, captured))
    return {
        "warning_evidence": dict(warning_evidence),
        "operations": tuple(captures),
        "autocast_observed": autocast_observed,
    }


def run_model_replica(
    inputs: ModelReplicaInputs, *, instrumented: bool
) -> dict[str, object]:
    """Execute one no-update model replica and publish its immutable tensor files."""
    expected_kind = "instrumented" if instrumented else "control"
    expected_ids = (
        {f"instrumented-{index}" for index in range(5)}
        if instrumented
        else {f"control-{index}" for index in range(2)}
    )
    if inputs.component_id not in expected_ids:
        raise AttributionError("model replica component ID/kind mismatch")
    if instrumented and inputs.component_id == "instrumented-0":
        if inputs.vjp_snapshot_output is None:
            raise AttributionError("instrumented-0 requires a VJP snapshot destination")
    elif inputs.vjp_snapshot_output is not None:
        raise AttributionError("VJP snapshot destination is forbidden on this replica")
    root = _artifact_root()
    _validate_component_root(inputs.component_root, root, inputs.component_id)
    parents = _load_parent_receipts(inputs, root)

    from transformers import RTDetrForObjectDetection

    from ..models.assets import (
        _find_snapshot_root,
        load_pinned_asset_specs,
        verify_snapshot,
        verify_transformers_source,
    )
    from ..models.rtdetr_contract import reset_four_class_head
    from ..probes.training_feasibility import (
        _prepare_labeled_batch,
        configure_determinism,
        run_math_only_labeled_forward_backward,
    )

    config_path = _project_root() / "configs" / "models" / "pinned-models.yaml"
    spec = load_pinned_asset_specs(config_path)["rtdetr"]
    snapshot = _find_snapshot_root(root / "wave0" / "model_cache", spec)
    verified = verify_snapshot(spec, snapshot)
    verify_transformers_source(spec)
    model_contract = parents["model_contract"]
    contract_normative = _mapping(model_contract.get("normative"), "model contract")
    if verified.files["model.safetensors"].sha256 != contract_normative.get(
        "model_sha256"
    ):
        raise AttributionError("live model asset differs from model-contract receipt")

    determinism = configure_determinism(17)
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise AttributionError("A7 requires exactly one visible CUDA device")
    if not determinism.bf16_supported:
        raise AttributionError("A7 requires BF16 support")
    device = torch.device("cuda", 0)
    if torch.cuda.get_device_name(device) != "NVIDIA GeForce RTX 4090":
        raise AttributionError("A7 requires NVIDIA GeForce RTX 4090")
    _require_live_gpu_identity(parents)

    model = None
    batch = None
    model_batch = None
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats(device)
    try:
        model = RTDetrForObjectDetection.from_pretrained(
            snapshot,
            local_files_only=True,
            use_safetensors=True,
        )
        reset_four_class_head(model, seed=17)
        model.to(device)
        batch, _, _ = _prepare_labeled_batch(device, sha256_file(inputs.model_contract))
        model_batch = {
            name: value for name, value in batch.items() if not name.startswith("_val_")
        }
        canonical_parameters = tuple(
            (name, parameter)
            for name, parameter in model.named_parameters(remove_duplicate=False)
            if parameter.requires_grad
        )
        recorder = ModelRecorder()
        if instrumented:
            install_adapters(model, recorder)

        def labeled_forward() -> tuple[torch.Tensor, bool]:
            model.train()
            model.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                autocast_observed = bool(torch.is_autocast_enabled("cuda"))
                outputs = model(**model_batch)
                loss = outputs.loss
            return loss, autocast_observed

        (
            loss,
            autocast_observed,
            warning_evidence,
            attention_evidence,
        ) = run_math_only_labeled_forward_backward(
            model,
            labeled_forward,
            expected_warning_count=9,
        )
        parameters = capture_parameter_gradients(
            model, canonical_parameters=canonical_parameters
        )
        raw_tensors = {
            name: parameter.grad
            for name, parameter in canonical_parameters
            if parameter.grad is not None
        }
        operations: tuple[OperationCapture, ...] = ()
        if instrumented:
            operations = recorder.finalize()
            raw_tensors.update(
                {
                    f"{capture.operation_id}.{role}": tensor
                    for capture in operations
                    for role, tensor in capture.tensors.items()
                }
            )
        torch.cuda.synchronize(device)
        peak_vram_bytes = int(torch.cuda.max_memory_allocated(device))
        peak_reserved_vram_bytes = int(torch.cuda.max_memory_reserved(device))
        _require_vram_limit(peak_vram_bytes)
        bundle_path = inputs.component_root / "tensor-bundle.vala7"
        bundle_sha256 = atomic_write_snapshot(bundle_path, raw_tensors)
        bundle = _snapshot_artifact(root, bundle_path, raw_tensors, bundle_sha256)
        vjp_snapshot = None
        if inputs.vjp_snapshot_output is not None:
            snapshot_tensors = {
                f"{capture.operation_id}.{role}": capture.tensors[role]
                for capture in operations
                for role in _VJP_ROLES
            }
            snapshot_sha256 = atomic_write_snapshot(
                inputs.vjp_snapshot_output, snapshot_tensors
            )
            vjp_snapshot = _snapshot_artifact(
                root,
                inputs.vjp_snapshot_output,
                snapshot_tensors,
                snapshot_sha256,
            )
        ended_at = datetime.now(UTC)
        execution = _execution_document(
            inputs.argv,
            started_at,
            ended_at,
            time.perf_counter() - started,
            peak_vram_bytes,
            peak_reserved_vram_bytes,
            float(loss.detach().to(device="cpu", dtype=torch.float64).item()).hex(),
            warning_evidence,
            autocast_observed,
            bool(attention_evidence.restored),
        )
        normative: dict[str, object] = {
            "identity": _identity_document(
                parents, inputs, expected_kind, contract_normative
            ),
            "parent_receipts": _parent_artifacts(root, inputs),
            "execution": execution,
            "tensor_bundle": bundle,
            "parameter_gradients": parameters,
            "invariants": _valid_invariants(),
            "status": "RECORDED",
            "errors": [],
        }
        if instrumented:
            normative["operations"] = _operation_documents(operations)
        if vjp_snapshot is not None:
            normative["vjp_snapshot"] = vjp_snapshot
        return _receipt_document(normative, inputs.run_id)
    finally:
        if model_batch is not None:
            del model_batch
        if batch is not None:
            del batch
        if model is not None:
            del model
        if torch.cuda.is_available():
            torch.cuda.synchronize(device)


def run_isolated_vjp_replica(inputs: IsolatedReplicaInputs) -> dict[str, object]:
    """Execute one original-call-only VJP replica from instrumented-0 evidence."""
    expected_ids = {f"isolated-vjp-{index}" for index in range(5)}
    if inputs.component_id not in expected_ids:
        raise AttributionError("isolated replica component ID mismatch")
    root = _artifact_root()
    _validate_component_root(inputs.component_root, root, inputs.component_id)
    parents = _load_parent_receipts(inputs, root)
    from ..artifacts.receipts import validate_receipt_for_run

    parent_document = _read_mapping(inputs.parent_instrumented_receipt)
    validate_receipt_for_run(
        parent_document,
        _project_root() / "schemas" / "grid-sample-attribution-receipt.schema.json",
        inputs.run_id,
    )
    parent_normative = _mapping(parent_document.get("normative"), "instrumented parent")
    parent_identity = _mapping(
        parent_normative.get("identity"), "instrumented identity"
    )
    if parent_identity.get("component_id") != "instrumented-0":
        raise AttributionError("isolated VJP parent must be instrumented-0")
    if (
        parent_identity.get("source_commit") != inputs.source_commit
        or parent_identity.get("image_id") != inputs.image_id
        or parent_identity.get("base_image_digest") != inputs.base_image_digest
    ):
        raise AttributionError("isolated VJP parent identity mismatch")
    expected_names = tuple(
        sorted(
            f"{operation_id}.{role}"
            for operation_id in OPERATION_IDS
            for role in _VJP_ROLES
        )
    )
    parent_snapshot = _mapping(
        parent_normative.get("vjp_snapshot"), "parent VJP snapshot"
    )
    if (
        parent_snapshot.get("sha256") != sha256_file(inputs.vjp_snapshot)
        or parent_snapshot.get("size") != inputs.vjp_snapshot.stat().st_size
        or parent_snapshot.get("names") != list(expected_names)
    ):
        raise AttributionError("VJP snapshot/parent receipt hash mismatch")
    decoded = decode_snapshot(inputs.vjp_snapshot, expected_names=expected_names)
    from torch.nn.attention import SDPBackend, sdpa_kernel

    from ..probes.training_feasibility import (
        _DETERMINISTIC_ATTENTION_BEFORE,
        _DETERMINISTIC_ATTENTION_INSIDE,
        _sdpa_backend_state,
        configure_determinism,
    )

    determinism = configure_determinism(17)
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise AttributionError("isolated A7 VJP requires exactly one CUDA device")
    if not determinism.bf16_supported:
        raise AttributionError("isolated A7 VJP requires BF16 support")
    device = torch.device("cuda", 0)
    if torch.cuda.get_device_name(device) != "NVIDIA GeForce RTX 4090":
        raise AttributionError("isolated A7 VJP requires RTX 4090")
    _require_live_gpu_identity(parents)
    cuda_tensors = {name: tensor.to(device) for name, tensor in decoded.items()}
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    torch.cuda.reset_peak_memory_stats(device)
    before = _sdpa_backend_state()
    if before != _DETERMINISTIC_ATTENTION_BEFORE:
        raise AttributionError("isolated VJP attention entry backend mismatch")
    body_error: BaseException | None = None
    result: dict[str, object] | None = None
    try:
        with sdpa_kernel(SDPBackend.MATH):
            if _sdpa_backend_state() != _DETERMINISTIC_ATTENTION_INSIDE:
                raise AttributionError("isolated VJP Math-only backend mismatch")
            result = run_isolated_vjp_tensors(cuda_tensors)
    except BaseException as error:  # noqa: BLE001 - verify restoration on every exit.
        body_error = error
    strict_restored = (
        torch.are_deterministic_algorithms_enabled()
        and not torch.is_deterministic_algorithms_warn_only_enabled()
        and torch.get_deterministic_debug_mode() == 2
    )
    if _sdpa_backend_state() != before or not strict_restored:
        restoration = AttributionError("isolated VJP runtime restoration mismatch")
        if body_error is not None:
            raise restoration from body_error
        raise restoration
    if body_error is not None:
        raise body_error.with_traceback(body_error.__traceback__)
    assert result is not None
    if result.get("autocast_observed") is not True:
        raise AttributionError("isolated VJP BF16 autocast was not observed")
    operations = result["operations"]
    raw_tensors = {
        f"{capture.operation_id}.{role}": tensor
        for capture in operations
        for role, tensor in capture.tensors.items()
    }
    torch.cuda.synchronize(device)
    peak_vram_bytes = int(torch.cuda.max_memory_allocated(device))
    peak_reserved_vram_bytes = int(torch.cuda.max_memory_reserved(device))
    _require_vram_limit(peak_vram_bytes)
    bundle_path = inputs.component_root / "tensor-bundle.vala7"
    bundle_sha256 = atomic_write_snapshot(bundle_path, raw_tensors)
    contract_normative = _mapping(
        parents["model_contract"].get("normative"), "model contract"
    )
    parent_execution = _mapping(parent_normative.get("execution"), "parent execution")
    ended_at = datetime.now(UTC)
    warning_evidence = result["warning_evidence"]
    execution = {
        "argv": list(inputs.argv),
        "exit_code": 0,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "runtime_seconds": time.perf_counter() - started,
        "peak_vram_bytes": peak_vram_bytes,
        "peak_reserved_vram_bytes": peak_reserved_vram_bytes,
        "loss_hex": parent_execution["loss_hex"],
        "warning_evidence": dict(warning_evidence),
        "backend": {
            "math_only": True,
            "strict_restored": strict_restored,
            "autocast_bf16": result["autocast_observed"],
        },
    }
    parent_orders = {
        operation["operation_id"]: operation["callback_order"]
        for operation in parent_normative["operations"]
    }
    for capture in operations:
        capture.callback_order = parent_orders[capture.operation_id]
    normative = {
        "identity": _identity_document(
            parents, inputs, "isolated-vjp", contract_normative
        ),
        "parent_receipts": {
            **_parent_artifacts(root, inputs),
            "instrumented": _file_artifact(root, inputs.parent_instrumented_receipt),
        },
        "execution": execution,
        "tensor_bundle": _snapshot_artifact(
            root, bundle_path, raw_tensors, bundle_sha256
        ),
        "vjp_snapshot": dict(parent_snapshot),
        "operations": _operation_documents(operations),
        "invariants": _valid_invariants(),
        "status": "RECORDED",
        "errors": [],
    }
    return _receipt_document(normative, inputs.run_id)


def classify_aggregate(
    controls: Sequence[Mapping[str, object]],
    instrumented: Sequence[Mapping[str, object]],
    isolated: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    """Classify exact-digest evidence without introducing a numerical tolerance."""
    try:
        _validate_component_set(controls, "control", 2)
        _validate_component_set(instrumented, "instrumented", 5)
        _validate_component_set(isolated, "isolated-vjp", 5)
        all_components = (*controls, *instrumented, *isolated)
        if not all(_all_invariants_true(component) for component in all_components):
            return _inconclusive("component_invariant_false")
        if not _static_identities_match(all_components):
            return _inconclusive("static_identity_mismatch")
        if not _model_execution_matches((*controls, *instrumented)):
            return _inconclusive("instrumentation_execution_mismatch")
        for component in (*controls, *instrumented):
            if not _parameter_inventory_valid(component):
                return _inconclusive("parameter_inventory_invalid")

        instrumented_operations = [
            _operation_records(component) for component in instrumented
        ]
        callback_order = _common_callback_order(instrumented_operations)
        if callback_order is None:
            return _inconclusive("callback_order_mismatch")
        isolated_operations = [_operation_records(component) for component in isolated]
        if any(set(records) != set(OPERATION_IDS) for records in isolated_operations):
            return _inconclusive("isolated_operation_inventory_mismatch")

        candidates: list[tuple[str, str]] = []
        for operation_id in callback_order:
            for role in (
                "forward_value",
                "forward_grid",
                "forward_result",
                "incoming_result_gradient",
            ):
                if not _role_exact(instrumented_operations, operation_id, role):
                    return _inconclusive("instrumented_forward_or_incoming_mismatch")
            candidates.extend(
                (operation_id, role)
                for role in (
                    "outgoing_value_gradient",
                    "outgoing_grid_gradient",
                )
                if not _role_exact(instrumented_operations, operation_id, role)
            )
            if candidates:
                break

        for candidate_operation, candidate_role in candidates:
            for role in (
                "forward_value",
                "forward_grid",
                "forward_result",
                "incoming_result_gradient",
            ):
                if not _role_exact(isolated_operations, candidate_operation, role):
                    return _inconclusive("isolated_operand_or_result_mismatch")
                if not _role_matches_reference(
                    isolated_operations,
                    instrumented_operations[0],
                    candidate_operation,
                    role,
                ):
                    return _inconclusive("isolated_snapshot_parent_mismatch")
            if not _role_exact(
                isolated_operations, candidate_operation, candidate_role
            ):
                return {
                    "status": "ATTRIBUTED",
                    "candidate_operation": candidate_operation,
                    "candidate_role": candidate_role,
                    "reason_codes": [],
                    "terminal": (
                        "WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / "
                        "WAVE1_FORBIDDEN"
                    ),
                }
        if candidates:
            return _inconclusive("isolated_outgoing_divergence_absent")

        for operation_id in OPERATION_IDS:
            for role in _OPERATION_ROLES:
                if not _role_exact(isolated_operations, operation_id, role):
                    return _inconclusive("isolated_divergence_without_model_candidate")
                if role in {
                    "forward_value",
                    "forward_grid",
                    "forward_result",
                    "incoming_result_gradient",
                } and not _role_matches_reference(
                    isolated_operations,
                    instrumented_operations[0],
                    operation_id,
                    role,
                ):
                    return _inconclusive("isolated_snapshot_parent_mismatch")
        parameter_digests = {
            component["parameter_gradients"]["inventory_sha256"]
            for component in instrumented
        }
        if len(parameter_digests) < 2:
            return _inconclusive("model_divergence_not_reproduced")
        return {
            "status": "NOT_ATTRIBUTED",
            "candidate_operation": None,
            "candidate_role": None,
            "reason_codes": [],
            "terminal": (
                "WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / "
                "WAVE1_FORBIDDEN"
            ),
        }
    except (KeyError, TypeError, ValueError, TensorEvidenceError) as error:
        return _inconclusive(f"malformed_evidence:{type(error).__name__}")


def _inconclusive(reason: str) -> dict[str, object]:
    return {
        "status": "INCONCLUSIVE",
        "candidate_operation": None,
        "candidate_role": None,
        "reason_codes": [reason],
        "terminal": (
            "WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / " "WAVE1_FORBIDDEN"
        ),
    }


def _validate_component_set(
    components: Sequence[Mapping[str, object]], kind: str, count: int
) -> None:
    if len(components) != count:
        raise AttributionError(f"{kind} component count mismatch")
    expected_ids = (
        {f"{kind}-{index}" for index in range(count)}
        if kind != "isolated-vjp"
        else {f"isolated-vjp-{index}" for index in range(count)}
    )
    actual_ids = set()
    for component in components:
        identity = component["identity"]
        if identity["component_kind"] != kind:
            raise AttributionError("component kind mismatch")
        actual_ids.add(identity["component_id"])
    if actual_ids != expected_ids:
        raise AttributionError(f"{kind} component ID set mismatch")


def _all_invariants_true(component: Mapping[str, object]) -> bool:
    invariants = component.get("invariants")
    return (
        isinstance(invariants, Mapping)
        and bool(invariants)
        and all(value is True for value in invariants.values())
    )


def _static_identities_match(components: Sequence[Mapping[str, object]]) -> bool:
    excluded = {"component_kind", "component_id"}
    identities = []
    parents = []
    for component in components:
        identity = component.get("identity")
        parent_receipts = component.get("parent_receipts")
        if not isinstance(identity, Mapping) or not isinstance(
            parent_receipts, Mapping
        ):
            return False
        identities.append(
            {key: value for key, value in identity.items() if key not in excluded}
        )
        parents.append(
            {
                key: parent_receipts.get(key)
                for key in ("environment", "model_assets", "model_contract")
            }
        )
    return all(item == identities[0] for item in identities[1:]) and all(
        item == parents[0] for item in parents[1:]
    )


def _model_execution_matches(components: Sequence[Mapping[str, object]]) -> bool:
    observations = []
    for component in components:
        execution = component.get("execution")
        if not isinstance(execution, Mapping):
            return False
        observations.append(
            {
                key: execution.get(key)
                for key in ("loss_hex", "warning_evidence", "backend")
            }
        )
    return all(item == observations[0] for item in observations[1:])


def _parameter_inventory_valid(component: Mapping[str, object]) -> bool:
    inventory = component.get("parameter_gradients")
    if not isinstance(inventory, Mapping):
        return False
    parameters = inventory.get("parameters")
    if not isinstance(parameters, list) or inventory.get("count") != len(parameters):
        return False
    names = [
        parameter.get("name")
        for parameter in parameters
        if isinstance(parameter, Mapping)
    ]
    if len(names) != len(parameters) or len(names) != len(set(names)):
        return False
    return inventory.get("inventory_sha256") == canonical_json_sha256(
        {"parameters": parameters}
    )


def _operation_records(
    component: Mapping[str, object],
) -> dict[str, Mapping[str, object]]:
    operations = component.get("operations")
    if not isinstance(operations, list) or len(operations) != 9:
        raise AttributionError("operation count mismatch")
    records: dict[str, Mapping[str, object]] = {}
    for operation in operations:
        if not isinstance(operation, Mapping):
            raise AttributionError("operation must be an object")
        operation_id = operation.get("operation_id")
        tensors = operation.get("tensors")
        if operation_id not in OPERATION_IDS or operation_id in records:
            raise AttributionError("operation ID inventory mismatch")
        if not isinstance(tensors, list) or len(tensors) != 6:
            raise AttributionError("operation tensor count mismatch")
        role_map: dict[str, Mapping[str, object]] = {}
        for tensor in tensors:
            if not isinstance(tensor, Mapping):
                raise AttributionError("tensor evidence must be an object")
            role = tensor.get("role")
            if role not in _OPERATION_ROLES or role in role_map:
                raise AttributionError("operation tensor role mismatch")
            if tensor.get("operation_id") != operation_id:
                raise AttributionError("tensor operation ID mismatch")
            role_map[role] = tensor
        if set(role_map) != set(_OPERATION_ROLES):
            raise AttributionError("operation role inventory mismatch")
        records[operation_id] = {
            "callback_order": operation.get("callback_order"),
            "roles": role_map,
        }
    if set(records) != set(OPERATION_IDS):
        raise AttributionError("operation inventory mismatch")
    return records


def _common_callback_order(
    replicas: Sequence[Mapping[str, Mapping[str, object]]],
) -> tuple[str, ...] | None:
    orders: list[tuple[str, ...]] = []
    for records in replicas:
        indexed = []
        for operation_id, record in records.items():
            order = record.get("callback_order")
            if type(order) is not int or order not in range(9):
                return None
            indexed.append((order, operation_id))
        indexed.sort()
        if [order for order, _ in indexed] != list(range(9)):
            return None
        orders.append(tuple(operation_id for _, operation_id in indexed))
    if not orders or any(order != orders[0] for order in orders[1:]):
        return None
    return orders[0]


def _role_exact(
    replicas: Sequence[Mapping[str, Mapping[str, object]]],
    operation_id: str,
    role: str,
) -> bool:
    digests = {replica[operation_id]["roles"][role]["sha256"] for replica in replicas}
    return len(digests) == 1


def _role_matches_reference(
    replicas: Sequence[Mapping[str, Mapping[str, object]]],
    reference: Mapping[str, Mapping[str, object]],
    operation_id: str,
    role: str,
) -> bool:
    expected = reference[operation_id]["roles"][role]["sha256"]
    return all(
        replica[operation_id]["roles"][role]["sha256"] == expected
        for replica in replicas
    )


def _artifact_root() -> Path:
    configured = os.environ.get("VAL_ARTIFACT_ROOT")
    if not configured:
        raise AttributionError("VAL_ARTIFACT_ROOT is required")
    root = Path(configured)
    if not root.is_absolute() or not root.is_dir() or _is_link_or_junction(root):
        raise AttributionError(
            "VAL_ARTIFACT_ROOT must be an existing non-link directory"
        )
    if "VAL_DATA_ROOT" in os.environ:
        raise AttributionError("A7 forbids VAL_DATA_ROOT")
    return root.resolve(strict=True)


def _require_live_gpu_identity(
    parents: Mapping[str, Mapping[str, object]],
) -> None:
    environment = _mapping(parents["environment"].get("normative"), "environment")
    observed = _mapping(environment.get("observed"), "environment observed")
    expected_uuid = observed.get("gpu_uuid")
    if not isinstance(expected_uuid, str):
        raise AttributionError("parent GPU UUID is unavailable")
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=uuid",
            "--format=csv,noheader,nounits",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AttributionError("live GPU UUID observation failed")
    _validate_live_gpu_uuid(expected_uuid, completed.stdout)


def _validate_live_gpu_uuid(expected_uuid: str, output: str) -> None:
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    if len(lines) != 1 or lines[0] != expected_uuid:
        raise AttributionError("live GPU UUID does not match the parent receipt")


def _require_vram_limit(peak_vram_bytes: int) -> None:
    if type(peak_vram_bytes) is not int or not 0 <= peak_vram_bytes <= 22 * 1024**3:
        raise AttributionError("A7 peak allocation exceeds the 22 GiB ceiling")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _validate_component_root(path: Path, root: Path, component_id: str) -> None:
    expected = root / "a7" / "components" / component_id
    try:
        resolved = Path(path).resolve(strict=True)
    except OSError as error:
        raise AttributionError("component root must already exist") from error
    if (
        resolved != expected
        or not resolved.is_dir()
        or _is_link_or_junction(Path(path))
    ):
        raise AttributionError("component root path mismatch or link")


def _load_parent_receipts(
    inputs: ModelReplicaInputs | IsolatedReplicaInputs, root: Path
) -> dict[str, Mapping[str, object]]:
    from ..artifacts.receipts import validate_receipt_for_run

    paths = {
        "environment": inputs.environment,
        "model_assets": inputs.model_assets,
        "model_contract": inputs.model_contract,
    }
    expected = {
        "environment": root / "wave0" / "receipts" / "environment.json",
        "model_assets": root / "wave0" / "receipts" / "model-assets.json",
        "model_contract": root / "wave0" / "receipts" / "model-contract.json",
    }
    schemas = {
        "environment": "environment-receipt.schema.json",
        "model_assets": "model-asset-receipt.schema.json",
        "model_contract": "model-contract-receipt.schema.json",
    }
    documents: dict[str, Mapping[str, object]] = {}
    for name, path in paths.items():
        actual = Path(path)
        if actual.resolve(strict=True) != expected[name] or _is_link_or_junction(
            actual
        ):
            raise AttributionError(f"A7 {name} parent path mismatch")
        document = _read_mapping(actual)
        validate_receipt_for_run(
            document,
            _project_root() / "schemas" / schemas[name],
            inputs.run_id,
        )
        normative = _mapping(document.get("normative"), f"{name} normative")
        if normative.get("status") != "PASS":
            raise AttributionError(f"A7 {name} parent must be PASS")
        documents[name] = document
    return documents


def _identity_document(
    parents: Mapping[str, Mapping[str, object]],
    inputs: ModelReplicaInputs | IsolatedReplicaInputs,
    component_kind: str,
    contract: Mapping[str, object],
) -> dict[str, object]:
    environment = _mapping(parents["environment"].get("normative"), "environment")
    observed = _mapping(environment.get("observed"), "environment observed")
    gpu_uuid = observed.get("gpu_uuid")
    if not isinstance(gpu_uuid, str) or not gpu_uuid.startswith("GPU-"):
        raise AttributionError("A7 GPU UUID is unavailable")
    if observed.get("gpu_name") != "NVIDIA GeForce RTX 4090":
        raise AttributionError("A7 parent GPU identity mismatch")
    if observed.get("runtime_image_digest") != inputs.image_id:
        raise AttributionError("A7 runtime image identity mismatch")
    if observed.get("container_image_digest") != inputs.base_image_digest:
        raise AttributionError("A7 base image identity mismatch")
    adapter_path = Path(__file__).resolve(strict=True)
    tensor_evidence_path = adapter_path.with_name("tensor_evidence.py").resolve(
        strict=True
    )
    adapter_source_sha256 = sha256_file(adapter_path)
    tensor_evidence_source_sha256 = sha256_file(tensor_evidence_path)
    source_sha256 = canonical_json_sha256(
        {
            "files": [
                {
                    "path": (
                        "src/vision_active_learning_loop/diagnostics/"
                        "grid_sample_attribution.py"
                    ),
                    "sha256": adapter_source_sha256,
                },
                {
                    "path": (
                        "src/vision_active_learning_loop/diagnostics/"
                        "tensor_evidence.py"
                    ),
                    "sha256": tensor_evidence_source_sha256,
                },
            ]
        }
    )
    required_hashes = {
        "model_sha256": contract.get("model_sha256"),
        "config_sha256": contract.get("config_file_sha256"),
        "processor_sha256": contract.get("processor_file_sha256"),
        "fixture_sha256": contract.get("fixture_sha256"),
        "model_loss_source_sha256": contract.get("loss_source_sha256"),
        "adapter_source_sha256": adapter_source_sha256,
        "tensor_evidence_source_sha256": tensor_evidence_source_sha256,
        "source_sha256": source_sha256,
    }
    if any(
        not isinstance(value, str) or len(value) != 64
        for value in required_hashes.values()
    ):
        raise AttributionError("A7 model-contract hash inventory is incomplete")
    return {
        "source_commit": inputs.source_commit,
        "image_id": inputs.image_id,
        "base_image_digest": inputs.base_image_digest,
        "run_id": inputs.run_id,
        "component_kind": component_kind,
        "component_id": inputs.component_id,
        "gpu_name": observed["gpu_name"],
        "gpu_uuid": gpu_uuid,
        **required_hashes,
        "seed": 17,
        "precision": "BF16",
        "num_queries": 300,
        "decoder_layers": 3,
        "feature_levels": 3,
        "disable_custom_kernels": True,
    }


def _parent_artifacts(
    root: Path, inputs: ModelReplicaInputs | IsolatedReplicaInputs
) -> dict[str, object]:
    return {
        "environment": _file_artifact(root, inputs.environment),
        "model_assets": _file_artifact(root, inputs.model_assets),
        "model_contract": _file_artifact(root, inputs.model_contract),
    }


def _file_artifact(root: Path, path: Path) -> dict[str, object]:
    target = Path(path)
    if not target.is_file() or _is_link_or_junction(target):
        raise AttributionError("A7 artifact must be a regular non-link file")
    try:
        relative = target.resolve(strict=True).relative_to(root).as_posix()
    except ValueError as error:
        raise AttributionError("A7 artifact escapes VAL_ARTIFACT_ROOT") from error
    return {
        "path": relative,
        "size": target.stat().st_size,
        "sha256": sha256_file(target),
    }


def _snapshot_artifact(
    root: Path,
    path: Path,
    tensors: Mapping[str, torch.Tensor],
    digest: str,
) -> dict[str, object]:
    artifact = _file_artifact(root, path)
    if artifact["sha256"] != digest:
        raise AttributionError("published tensor snapshot digest mismatch")
    names = sorted(tensors)
    return {
        **artifact,
        "inventory_sha256": canonical_json_sha256({"names": names}),
        "names": names,
        "public_export_candidate": False,
    }


def _operation_documents(
    operations: Sequence[OperationCapture],
) -> list[dict[str, object]]:
    documents = []
    for capture in operations:
        if capture.callback_order is None:
            raise AttributionError("operation callback order is unavailable")
        tensors = [
            _tensor_evidence_document(
                observe_tensor(
                    f"{capture.operation_id}.{role}",
                    role,
                    capture.tensors[role],
                    operation_id=capture.operation_id,
                )
            )
            for role in _OPERATION_ROLES
        ]
        documents.append(
            {
                "operation_id": capture.operation_id,
                "callback_order": capture.callback_order,
                "tensors": tensors,
            }
        )
    return documents


def _execution_document(
    argv: tuple[str, ...],
    started_at: datetime,
    ended_at: datetime,
    runtime_seconds: float,
    peak_vram_bytes: int,
    peak_reserved_vram_bytes: int,
    loss_hex: str,
    warning_evidence: object,
    autocast_observed: bool,
    backend_restored: bool,
) -> dict[str, object]:
    observed_count = getattr(warning_evidence, "observed_count", None)
    operations = getattr(warning_evidence, "operation_identifiers", None)
    if (
        observed_count != 9
        or tuple(operations or ()) != ("grid_sampler_2d_backward_cuda",) * 9
    ):
        raise AttributionError(
            "A7 warning evidence differs from exact nine-call contract"
        )
    return {
        "argv": list(argv),
        "exit_code": 0,
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "runtime_seconds": runtime_seconds,
        "peak_vram_bytes": int(peak_vram_bytes),
        "peak_reserved_vram_bytes": int(peak_reserved_vram_bytes),
        "loss_hex": loss_hex,
        "warning_evidence": {"count": 9, "operations": list(operations)},
        "backend": {
            "math_only": True,
            "strict_restored": backend_restored,
            "autocast_bf16": autocast_observed,
        },
    }


def _valid_invariants() -> dict[str, bool]:
    return {
        "identity_verified": True,
        "parents_verified": True,
        "tensor_inventory_verified": True,
        "warnings_verified": True,
        "backend_restored": True,
        "publication_verified": True,
    }


def _receipt_document(
    normative: Mapping[str, object], run_id: str
) -> dict[str, object]:
    return {
        "receipt_type": "grid-sample-attribution",
        "schema_version": 1,
        "normative": dict(normative),
        "metadata": {"timestamp": datetime.now(UTC).isoformat(), "run_id": run_id},
    }


def _read_mapping(path: Path) -> Mapping[str, object]:
    try:
        document = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise AttributionError(
            f"A7 receipt cannot be read: {Path(path).name}"
        ) from error
    return _mapping(document, "A7 receipt")


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise AttributionError(f"{name} must be an object")
    return value


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and bool(is_junction()))


def _validated_vjp_tensor(
    tensor: torch.Tensor, operation_id: str, role: str
) -> torch.Tensor:
    try:
        canonical_tensor_bytes(tensor)
    except TensorEvidenceError as error:
        raise AttributionError(f"invalid isolated {role}: {operation_id}") from error
    return tensor.detach().clone()


def _evidence_copy(tensor: torch.Tensor, operation_id: str, role: str) -> torch.Tensor:
    try:
        canonical_tensor_bytes(tensor)
    except TensorEvidenceError as error:
        raise AttributionError(f"invalid {role} tensor for {operation_id}") from error
    return tensor.detach().to(device="cpu").clone()


def _run_allowlisted_backward(
    callback: Callable[[], None], *, expected_count: int
) -> Mapping[str, object]:
    from ..probes.training_feasibility import run_allowlisted_backward

    evidence = run_allowlisted_backward(callback, expected_count=expected_count)
    return {
        "count": evidence.observed_count,
        "operations": list(evidence.operation_identifiers),
    }


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise AttributionError(message)


@command("diagnose grid-sample-attribution")
def main(argv: Sequence[str] | None = None) -> int:
    """Run one fail-closed A7 component or aggregate publication."""
    arguments_list = list(argv or ())
    parser = _ArgumentParser(prog="val diagnose grid-sample-attribution")
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    for name in ("control", "instrumented"):
        child = subparsers.add_parser(name)
        _add_parent_arguments(child)
        child.add_argument("--component-root", type=Path, required=True)
        child.add_argument("--component-id", required=True)
        child.add_argument("--source-commit", required=True)
        child.add_argument("--run-id", required=True)
        child.add_argument("--output", type=Path, required=True)
        if name == "instrumented":
            child.add_argument("--vjp-snapshot-output", type=Path)
    isolated_parser = subparsers.add_parser("isolated-vjp")
    _add_parent_arguments(isolated_parser)
    isolated_parser.add_argument(
        "--parent-instrumented-receipt", type=Path, required=True
    )
    isolated_parser.add_argument("--vjp-snapshot", type=Path, required=True)
    isolated_parser.add_argument("--component-root", type=Path, required=True)
    isolated_parser.add_argument("--component-id", required=True)
    isolated_parser.add_argument("--source-commit", required=True)
    isolated_parser.add_argument("--run-id", required=True)
    isolated_parser.add_argument("--output", type=Path, required=True)
    aggregate_parser = subparsers.add_parser("aggregate")
    _add_parent_arguments(aggregate_parser)
    aggregate_parser.add_argument("--components-root", type=Path, required=True)
    aggregate_parser.add_argument("--source-commit", required=True)
    aggregate_parser.add_argument("--run-id", required=True)
    aggregate_parser.add_argument("--output", type=Path, required=True)
    try:
        parsed = parser.parse_args(arguments_list)
        root = _artifact_root()
        _validate_cli_identity(parsed.source_commit, parsed.run_id)
        _validate_cli_parent_paths(parsed, root)
        full_argv = (
            "val",
            "diagnose",
            "grid-sample-attribution",
            *arguments_list,
        )
        if parsed.subcommand in {"control", "instrumented"}:
            receipt = _run_model_cli(parsed, root, full_argv)
        elif parsed.subcommand == "isolated-vjp":
            receipt = _run_isolated_cli(parsed, root, full_argv)
        else:
            receipt = _run_aggregate_cli(parsed, root, full_argv)
        atomic_write_receipt(parsed.output, receipt)
    except (
        AttributionError,
        OSError,
        RuntimeError,
        TensorEvidenceError,
        ValueError,
    ) as error:
        print(error, file=sys.stderr)
        return 2
    normative = _mapping(receipt.get("normative"), "A7 normative")
    if parsed.subcommand == "aggregate":
        print(normative["terminal"])
    else:
        print(normative["status"])
    return 0


def _add_parent_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--model-assets", type=Path, required=True)
    parser.add_argument("--model-contract", type=Path, required=True)


def _validate_cli_identity(source_commit: str, run_id: str) -> None:
    if not run_id.strip():
        raise AttributionError("run_id must be non-empty")
    expected_source = os.environ.get("VAL_SOURCE_COMMIT")
    if source_commit != expected_source or len(source_commit) != 40:
        raise AttributionError("source commit differs from VAL_SOURCE_COMMIT")
    for name in ("VAL_IMAGE_ID", "VAL_BASE_IMAGE_DIGEST"):
        value = os.environ.get(name)
        if not isinstance(value, str) or not value.startswith("sha256:"):
            raise AttributionError(f"{name} is required")


def _validate_cli_parent_paths(parsed: argparse.Namespace, root: Path) -> None:
    expected = {
        "environment": root / "wave0" / "receipts" / "environment.json",
        "model_assets": root / "wave0" / "receipts" / "model-assets.json",
        "model_contract": root / "wave0" / "receipts" / "model-contract.json",
    }
    for name, path in expected.items():
        supplied = Path(getattr(parsed, name))
        if (
            not supplied.is_file()
            or _is_link_or_junction(supplied)
            or supplied.resolve(strict=True) != path
        ):
            raise AttributionError(f"{name} must use the fixed A7 parent path")


def _run_model_cli(
    parsed: argparse.Namespace, root: Path, argv: tuple[str, ...]
) -> dict[str, object]:
    instrumented = parsed.subcommand == "instrumented"
    expected_ids = (
        {f"instrumented-{index}" for index in range(5)}
        if instrumented
        else {f"control-{index}" for index in range(2)}
    )
    if parsed.component_id not in expected_ids:
        raise AttributionError("component ID/subcommand mismatch")
    _validate_cli_component_destinations(
        root,
        parsed.component_root,
        parsed.component_id,
        parsed.output,
        getattr(parsed, "vjp_snapshot_output", None),
    )
    inputs = ModelReplicaInputs(
        environment=parsed.environment,
        model_assets=parsed.model_assets,
        model_contract=parsed.model_contract,
        component_root=parsed.component_root,
        component_id=parsed.component_id,
        run_id=parsed.run_id,
        source_commit=parsed.source_commit,
        image_id=os.environ["VAL_IMAGE_ID"],
        base_image_digest=os.environ["VAL_BASE_IMAGE_DIGEST"],
        argv=argv,
        vjp_snapshot_output=getattr(parsed, "vjp_snapshot_output", None),
    )
    receipt = run_model_replica(inputs, instrumented=instrumented)
    _verify_engine_artifacts(root, parsed.component_root, receipt)
    return receipt


def _run_isolated_cli(
    parsed: argparse.Namespace, root: Path, argv: tuple[str, ...]
) -> dict[str, object]:
    if parsed.component_id not in {f"isolated-vjp-{index}" for index in range(5)}:
        raise AttributionError("isolated component ID mismatch")
    _validate_cli_component_destinations(
        root, parsed.component_root, parsed.component_id, parsed.output, None
    )
    parent = root / "a7" / "components" / "instrumented-0" / "receipt.json"
    snapshot = root / "a7" / "components" / "instrumented-0" / "vjp-snapshot.vala7"
    if (
        parsed.parent_instrumented_receipt.resolve(strict=True) != parent
        or parsed.vjp_snapshot.resolve(strict=True) != snapshot
        or _is_link_or_junction(parsed.parent_instrumented_receipt)
        or _is_link_or_junction(parsed.vjp_snapshot)
    ):
        raise AttributionError("isolated parent receipt or VJP snapshot path mismatch")
    inputs = IsolatedReplicaInputs(
        environment=parsed.environment,
        model_assets=parsed.model_assets,
        model_contract=parsed.model_contract,
        parent_instrumented_receipt=parsed.parent_instrumented_receipt,
        vjp_snapshot=parsed.vjp_snapshot,
        component_root=parsed.component_root,
        component_id=parsed.component_id,
        run_id=parsed.run_id,
        source_commit=parsed.source_commit,
        image_id=os.environ["VAL_IMAGE_ID"],
        base_image_digest=os.environ["VAL_BASE_IMAGE_DIGEST"],
        argv=argv,
    )
    receipt = run_isolated_vjp_replica(inputs)
    _verify_engine_artifacts(root, parsed.component_root, receipt)
    return receipt


def _validate_cli_component_destinations(
    root: Path,
    component_root: Path,
    component_id: str,
    output: Path,
    vjp_snapshot: Path | None,
) -> None:
    expected_root = root / "a7" / "components" / component_id
    if (
        not component_root.is_dir()
        or _is_link_or_junction(component_root)
        or component_root.resolve(strict=True) != expected_root
    ):
        raise AttributionError("component root must be the fixed existing directory")
    if (
        output.resolve(strict=False) != expected_root / "receipt.json"
        or output.exists()
    ):
        raise AttributionError("component receipt destination must be fresh and fixed")
    bundle = expected_root / "tensor-bundle.vala7"
    if bundle.exists():
        raise AttributionError("tensor bundle destination already exists")
    expected_vjp = (
        expected_root / "vjp-snapshot.vala7"
        if component_id == "instrumented-0"
        else None
    )
    if expected_vjp is None:
        if vjp_snapshot is not None:
            raise AttributionError("VJP snapshot is forbidden for this component")
    elif vjp_snapshot is None or vjp_snapshot.resolve(strict=False) != expected_vjp:
        raise AttributionError("instrumented-0 requires the fixed VJP snapshot path")
    elif vjp_snapshot.exists():
        raise AttributionError("VJP snapshot destination already exists")


def _verify_engine_artifacts(
    root: Path, component_root: Path, receipt: Mapping[str, object]
) -> None:
    normative = _mapping(receipt.get("normative"), "A7 normative")
    for field, expected_path in (
        ("tensor_bundle", component_root / "tensor-bundle.vala7"),
        (
            "vjp_snapshot",
            root / "a7" / "components" / "instrumented-0" / "vjp-snapshot.vala7",
        ),
    ):
        artifact = normative.get(field)
        if artifact is None:
            continue
        document = _mapping(artifact, field)
        path = root / str(document.get("path"))
        if path != expected_path or not path.is_file() or _is_link_or_junction(path):
            raise AttributionError(f"{field} path is not the fixed regular file")
        if document.get("size") != path.stat().st_size or document.get(
            "sha256"
        ) != sha256_file(path):
            raise AttributionError(f"{field} file identity mismatch")
        names = document.get("names")
        if not isinstance(names, list):
            raise AttributionError(f"{field} tensor names are unavailable")
        decoded = decode_snapshot(path, expected_names=names)
        expected_records = _receipt_tensor_records(
            normative, snapshot=field == "vjp_snapshot"
        )
        if set(decoded) != set(expected_records):
            raise AttributionError(f"{field} tensor evidence inventory mismatch")
        for name, tensor in decoded.items():
            record = expected_records[name]
            observed = _tensor_evidence_document(
                observe_tensor(
                    name,
                    str(record["role"]),
                    tensor,
                    operation_id=str(record["operation_id"]),
                )
            )
            if observed != dict(record):
                raise AttributionError(f"{field} tensor evidence mismatch: {name}")


def _receipt_tensor_records(
    normative: Mapping[str, object], *, snapshot: bool
) -> dict[str, Mapping[str, object]]:
    records: dict[str, Mapping[str, object]] = {}
    if not snapshot:
        parameter_document = normative.get("parameter_gradients")
        if isinstance(parameter_document, Mapping):
            parameters = parameter_document.get("parameters")
            if not isinstance(parameters, list):
                raise AttributionError("parameter tensor evidence is unavailable")
            for parameter in parameters:
                record = _mapping(parameter, "parameter tensor evidence")
                name = str(record.get("name"))
                if name in records:
                    raise AttributionError("duplicate receipt tensor evidence")
                records[name] = record
    operations = normative.get("operations")
    if isinstance(operations, list):
        allowed_roles = set(_VJP_ROLES) if snapshot else set(_OPERATION_ROLES)
        for operation in operations:
            operation_document = _mapping(operation, "operation tensor evidence")
            tensors = operation_document.get("tensors")
            if not isinstance(tensors, list):
                raise AttributionError("operation tensor evidence is unavailable")
            for tensor in tensors:
                record = _mapping(tensor, "operation tensor evidence")
                if record.get("role") in allowed_roles:
                    name = str(record.get("name"))
                    if name in records:
                        raise AttributionError("duplicate receipt tensor evidence")
                    records[name] = record
    if not records:
        raise AttributionError("receipt tensor evidence inventory is invalid")
    return records


def _tensor_evidence_document(evidence: TensorEvidence) -> dict[str, object]:
    document = asdict(evidence)
    shape = document.get("shape")
    if not isinstance(shape, tuple):
        raise AttributionError("tensor evidence shape is not canonical")
    document["shape"] = list(shape)
    return document


def _run_aggregate_cli(
    parsed: argparse.Namespace, root: Path, argv: tuple[str, ...]
) -> dict[str, object]:
    started_at = datetime.now(UTC)
    started = time.perf_counter()
    components_root = root / "a7" / "components"
    aggregate_root = root / "a7" / "aggregate"
    if (
        parsed.components_root.resolve(strict=True) != components_root
        or _is_link_or_junction(parsed.components_root)
        or parsed.output.resolve(strict=False) != aggregate_root / "receipt.json"
        or not aggregate_root.is_dir()
        or _is_link_or_junction(aggregate_root)
        or parsed.output.exists()
    ):
        raise AttributionError("aggregate root or output path mismatch")
    expected_ids = [
        *(f"control-{index}" for index in range(2)),
        *(f"instrumented-{index}" for index in range(5)),
        *(f"isolated-vjp-{index}" for index in range(5)),
    ]
    _validate_component_directory_inventory(components_root, expected_ids)
    documents = []
    for component_id in expected_ids:
        path = components_root / component_id / "receipt.json"
        document = _read_mapping(path)
        validate_receipt_for_run(
            document,
            _project_root() / "schemas" / "grid-sample-attribution-receipt.schema.json",
            parsed.run_id,
        )
        _verify_engine_artifacts(root, components_root / component_id, document)
        documents.append(document)
    normatives = [
        _mapping(document.get("normative"), "component") for document in documents
    ]
    controls = normatives[:2]
    instrumented = normatives[2:7]
    isolated = normatives[7:]
    classification = classify_aggregate(controls, instrumented, isolated)
    comparisons = _build_aggregate_comparisons(root, controls, instrumented, isolated)
    first_identity = copy.deepcopy(_mapping(controls[0].get("identity"), "identity"))
    first_identity["component_kind"] = "aggregate"
    first_identity["component_id"] = "aggregate"
    if (
        first_identity.get("source_commit") != parsed.source_commit
        or first_identity.get("image_id") != os.environ["VAL_IMAGE_ID"]
        or first_identity.get("base_image_digest")
        != os.environ["VAL_BASE_IMAGE_DIGEST"]
    ):
        raise AttributionError("aggregate source/image identity mismatch")
    first_execution = _mapping(controls[0].get("execution"), "execution")
    ended_at = datetime.now(UTC)
    execution = {
        **copy.deepcopy(first_execution),
        "argv": list(argv),
        "started_at": started_at.isoformat(),
        "ended_at": ended_at.isoformat(),
        "runtime_seconds": time.perf_counter() - started,
        "peak_vram_bytes": max(
            int(_mapping(component.get("execution"), "execution")["peak_vram_bytes"])
            for component in normatives
        ),
        "peak_reserved_vram_bytes": max(
            int(
                _mapping(component.get("execution"), "execution")[
                    "peak_reserved_vram_bytes"
                ]
            )
            for component in normatives
        ),
    }
    parent_components = []
    for component_id, document, normative in zip(
        expected_ids, documents, normatives, strict=True
    ):
        receipt_path = components_root / component_id / "receipt.json"
        parent_components.append(
            {
                "component_id": component_id,
                "receipt": _file_artifact(root, receipt_path),
                "tensor_bundle": copy.deepcopy(normative["tensor_bundle"]),
            }
        )
    normative = {
        "identity": first_identity,
        "parent_receipts": {
            "environment": _file_artifact(root, parsed.environment),
            "model_assets": _file_artifact(root, parsed.model_assets),
            "model_contract": _file_artifact(root, parsed.model_contract),
        },
        "execution": execution,
        "components": {
            "controls": [copy.deepcopy(item) for item in controls],
            "instrumented": [copy.deepcopy(item) for item in instrumented],
            "isolated": [copy.deepcopy(item) for item in isolated],
        },
        "parent_components": parent_components,
        "comparisons": comparisons,
        "classification": classification,
        "invariants": _valid_invariants(),
        "status": classification["status"],
        "terminal": classification["terminal"],
        "errors": (
            list(classification["reason_codes"])
            if classification["status"] == "INCONCLUSIVE"
            else []
        ),
    }
    return _receipt_document(normative, parsed.run_id)


def _validate_component_directory_inventory(
    components_root: Path, expected_ids: Sequence[str]
) -> None:
    entries = list(Path(components_root).iterdir())
    if (
        len(entries) != len(expected_ids)
        or any(not entry.is_dir() or _is_link_or_junction(entry) for entry in entries)
        or sorted(entry.name for entry in entries) != sorted(expected_ids)
    ):
        raise AttributionError("aggregate component root inventory mismatch")


def _build_aggregate_comparisons(
    root: Path,
    controls: Sequence[Mapping[str, object]],
    instrumented: Sequence[Mapping[str, object]],
    isolated: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    model_components = [*controls, *instrumented]
    callback_order = tuple(
        operation_id
        for _, operation_id in sorted(
            (
                int(operation["callback_order"]),
                str(operation["operation_id"]),
            )
            for operation in instrumented[0]["operations"]
        )
    )
    return {
        "callback_order": list(callback_order),
        "parameter_pairs": [
            _compare_component_pair(root, left, right, parameters=True)
            for left, right in _pairwise(model_components)
        ],
        "instrumented_pairs": [
            _compare_component_pair(root, left, right, parameters=False)
            for left, right in _pairwise(instrumented)
        ],
        "isolated_pairs": [
            _compare_component_pair(root, left, right, parameters=False)
            for left, right in _pairwise(isolated)
        ],
    }


def _pairwise(
    components: Sequence[Mapping[str, object]],
) -> list[tuple[Mapping[str, object], Mapping[str, object]]]:
    return [
        (components[left], components[right])
        for left in range(len(components))
        for right in range(left + 1, len(components))
    ]


def _compare_component_pair(
    root: Path,
    left: Mapping[str, object],
    right: Mapping[str, object],
    *,
    parameters: bool,
) -> dict[str, object]:
    left_identity = _mapping(left.get("identity"), "left identity")
    right_identity = _mapping(right.get("identity"), "right identity")
    left_id = str(left_identity["component_id"])
    right_id = str(right_identity["component_id"])
    left_bundle = _load_bound_bundle(root, left)
    right_bundle = _load_bound_bundle(root, right)
    if parameters:
        left_parameters = _mapping(left.get("parameter_gradients"), "left parameters")
        right_parameters = _mapping(
            right.get("parameter_gradients"), "right parameters"
        )
        names = sorted(str(record["name"]) for record in left_parameters["parameters"])
        right_names = sorted(
            str(record["name"]) for record in right_parameters["parameters"]
        )
        inventory_equal = (
            left_parameters["inventory_sha256"] == right_parameters["inventory_sha256"]
        )
    else:
        names = sorted(
            str(tensor["name"])
            for operation in left["operations"]
            for tensor in operation["tensors"]
        )
        right_names = sorted(
            str(tensor["name"])
            for operation in right["operations"]
            for tensor in operation["tensors"]
        )
        inventory_equal = True
    if names != right_names or any(
        name not in left_bundle or name not in right_bundle for name in names
    ):
        raise AttributionError("aggregate pair tensor inventory mismatch")
    comparisons = []
    for name in names:
        comparison = asdict(
            compare_tensors(
                left_id,
                right_id,
                name,
                left_bundle[name],
                right_bundle[name],
            )
        )
        if comparison["exact_digest_equal"]:
            comparison["difference_l2"] = 0.0
            comparison["relative_l2"] = 0.0
            comparison["cosine"] = 1.0
        comparisons.append(comparison)
    del left_bundle
    del right_bundle
    return {
        "left_replica": left_id,
        "right_replica": right_id,
        "inventory_digest_equal": inventory_equal,
        "tensors": comparisons,
    }


def _load_bound_bundle(
    root: Path, component: Mapping[str, object]
) -> dict[str, torch.Tensor]:
    artifact = _mapping(component.get("tensor_bundle"), "tensor bundle")
    path = root / str(artifact["path"])
    if (
        not path.is_file()
        or _is_link_or_junction(path)
        or path.stat().st_size != artifact.get("size")
        or sha256_file(path) != artifact.get("sha256")
    ):
        raise AttributionError("aggregate tensor bundle file identity mismatch")
    names = artifact.get("names")
    if not isinstance(names, list):
        raise AttributionError("aggregate tensor bundle names missing")
    return decode_snapshot(path, expected_names=names)
