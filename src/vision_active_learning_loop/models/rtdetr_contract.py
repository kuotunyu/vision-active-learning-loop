"""Pinned raw-output contract for Transformers RT-DETR."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
from torch import nn

RDD_LABELS = ("D00", "D10", "D20", "D40")


class ContractUnavailable(RuntimeError):
    """Raised when a normative raw tensor cannot be observed label-free."""


@dataclass(frozen=True)
class RawDetectorOutput:
    logits: torch.Tensor
    final_boxes: torch.Tensor
    penultimate_boxes: torch.Tensor
    intermediate_boxes: torch.Tensor


@dataclass(frozen=True)
class SourceContractObservation:
    invariants: Mapping[str, bool]


@dataclass(frozen=True)
class RawContractObservation:
    config_num_queries: int
    config_num_labels: int
    decoder_layers: int
    shapes: Mapping[str, list[int]]
    invariants: Mapping[str, bool]
    status: str
    errors: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionDeviceObservation:
    environment: Mapping[str, object]
    invariants: Mapping[str, bool]


def _normalized_gpu_uuid(value: str | None) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.removeprefix("GPU-").lower()
    if (
        re.fullmatch(
            r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            normalized,
        )
        is None
    ):
        return None
    return normalized


def reset_four_class_head(model: Any, seed: int = 17) -> None:
    """Replace every class-dependent module in one seeded RNG stream."""
    decoder = getattr(getattr(model, "model", None), "decoder", None)
    class_embed = getattr(decoder, "class_embed", None)
    try:
        old_heads = list(class_embed)
    except TypeError as error:
        raise ContractUnavailable("decoder class heads are unavailable") from error
    if not old_heads or any(not isinstance(head, nn.Linear) for head in old_heads):
        raise ContractUnavailable("decoder class heads are unavailable")
    denoising = getattr(model.model, "denoising_class_embed", None)
    if not isinstance(denoising, nn.Embedding):
        raise ContractUnavailable("denoising class embedding is unavailable")
    encoder = getattr(model.model, "enc_score_head", None)
    if not isinstance(encoder, nn.Linear):
        raise ContractUnavailable("encoder score head is unavailable")
    cuda_devices = sorted(
        {
            tensor.device.index
            for tensor in [
                *(head.weight for head in old_heads),
                denoising.weight,
                encoder.weight,
            ]
            if tensor.device.type == "cuda" and tensor.device.index is not None
        }
    )
    with torch.random.fork_rng(devices=cuda_devices):
        torch.manual_seed(seed)
        if cuda_devices:
            torch.cuda.manual_seed_all(seed)
        prior_probability = (
            getattr(model.config, "initializer_bias_prior_prob", None) or 1 / 5
        )
        new_heads = nn.ModuleList()
        for old_head in old_heads:
            head = nn.Linear(
                old_head.in_features,
                len(RDD_LABELS),
                bias=old_head.bias is not None,
                device=old_head.weight.device,
                dtype=old_head.weight.dtype,
            )
            nn.init.xavier_uniform_(head.weight)
            if head.bias is not None:
                nn.init.constant_(
                    head.bias,
                    -math.log((1 - prior_probability) / prior_probability),
                )
            new_heads.append(head)

        replacement_embedding = nn.Embedding(
            len(RDD_LABELS) + 1,
            denoising.embedding_dim,
            padding_idx=len(RDD_LABELS),
            device=denoising.weight.device,
            dtype=denoising.weight.dtype,
        )
        nn.init.xavier_uniform_(replacement_embedding.weight)
        with torch.no_grad():
            replacement_embedding.weight[replacement_embedding.padding_idx].zero_()

        replacement_encoder = nn.Linear(
            encoder.in_features,
            len(RDD_LABELS),
            bias=encoder.bias is not None,
            device=encoder.weight.device,
            dtype=encoder.weight.dtype,
        )
        nn.init.xavier_uniform_(replacement_encoder.weight)
        if replacement_encoder.bias is not None:
            nn.init.constant_(
                replacement_encoder.bias,
                -math.log((1 - prior_probability) / prior_probability),
            )

    model.model.decoder.class_embed = new_heads
    model.model.denoising_class_embed = replacement_embedding
    model.model.enc_score_head = replacement_encoder

    model.config.num_labels = len(RDD_LABELS)
    model.config.id2label = dict(enumerate(RDD_LABELS))
    model.config.label2id = {label: index for index, label in enumerate(RDD_LABELS)}


def _required_tensor(outputs: Any, name: str) -> torch.Tensor:
    value = getattr(outputs, name, None)
    if not isinstance(value, torch.Tensor):
        raise ContractUnavailable(f"{name} is unavailable")
    return value


def extract_raw_contract(outputs: Any) -> RawDetectorOutput:
    """Extract raw foreground logits and layer-aligned boxes without postprocessing."""
    logits = _required_tensor(outputs, "logits")
    final_boxes = _required_tensor(outputs, "pred_boxes")
    intermediate = _required_tensor(outputs, "intermediate_reference_points")
    expected_ranks = (
        ("logits", logits, 3),
        ("pred_boxes", final_boxes, 3),
        ("intermediate_reference_points", intermediate, 4),
    )
    for name, tensor, expected_rank in expected_ranks:
        if tensor.ndim != expected_rank:
            raise ContractUnavailable(f"{name} must have rank {expected_rank}")
    if intermediate.shape[1] < 2:
        raise ContractUnavailable(
            "intermediate_reference_points requires at least two decoder layers"
        )
    if final_boxes.shape[-1] != 4:
        raise ContractUnavailable("pred_boxes must have last dimension 4")
    if intermediate.shape[-1] != 4:
        raise ContractUnavailable(
            "intermediate_reference_points must have last dimension 4"
        )
    if not (
        logits.shape[:2] == final_boxes.shape[:2]
        and logits.shape[:2] == (intermediate.shape[0], intermediate.shape[2])
    ):
        raise ContractUnavailable("raw outputs must share batch and query dimensions")
    return RawDetectorOutput(
        logits=logits,
        final_boxes=final_boxes,
        penultimate_boxes=intermediate[:, -2, :, :],
        intermediate_boxes=intermediate,
    )


def foreground_scores(raw: RawDetectorOutput) -> torch.Tensor:
    """Return the four independent focal-loss foreground probabilities."""
    return torch.sigmoid(raw.logits)


def observe_execution_device(
    model: Any,
    pixel_values: torch.Tensor,
    pixel_mask: torch.Tensor,
    raw: RawDetectorOutput,
    *,
    expected_gpu_name: str,
    nvidia_smi_gpu_name: str | None = None,
    nvidia_smi_gpu_uuid: str | None = None,
) -> ExecutionDeviceObservation:
    """Bind the selected CUDA GPU to model, input, and raw-output devices."""
    cuda_available = bool(torch.cuda.is_available())
    device_count = int(torch.cuda.device_count()) if cuda_available else 0
    selected_index: int | None = None
    selected_name: str | None = None
    selected_uuid: str | None = None
    selected_device: str | None = None
    if cuda_available and device_count > 0:
        selected_index = int(torch.cuda.current_device())
        selected_name = str(torch.cuda.get_device_name(selected_index))
        raw_uuid = getattr(
            torch.cuda.get_device_properties(selected_index), "uuid", None
        )
        if isinstance(raw_uuid, bytes):
            selected_uuid = raw_uuid.decode("ascii")
        elif raw_uuid is not None:
            selected_uuid = str(raw_uuid)
        selected_device = str(torch.device("cuda", selected_index))

    parameter_devices = {
        str(tensor.device) for tensor in [*model.parameters(), *model.buffers()]
    }
    model_device = (
        next(iter(parameter_devices)) if len(parameter_devices) == 1 else None
    )
    tensor_devices = {
        "pixel_values_device": str(pixel_values.device),
        "pixel_mask_device": str(pixel_mask.device),
        "logits_device": str(raw.logits.device),
        "final_boxes_device": str(raw.final_boxes.device),
        "penultimate_boxes_device": str(raw.penultimate_boxes.device),
        "intermediate_boxes_device": str(raw.intermediate_boxes.device),
    }
    inputs_on_selected = selected_device is not None and all(
        tensor_devices[name] == selected_device
        for name in ("pixel_values_device", "pixel_mask_device")
    )
    outputs_on_selected = selected_device is not None and all(
        tensor_devices[name] == selected_device
        for name in (
            "logits_device",
            "final_boxes_device",
            "penultimate_boxes_device",
            "intermediate_boxes_device",
        )
    )
    invariants = {
        "torch_cuda_available": cuda_available and device_count > 0,
        "torch_selected_gpu_is_canonical": (
            selected_index is not None
            and selected_name == expected_gpu_name
            and selected_name == nvidia_smi_gpu_name
            and _normalized_gpu_uuid(selected_uuid)
            == _normalized_gpu_uuid(nvidia_smi_gpu_uuid)
            and isinstance(nvidia_smi_gpu_uuid, str)
            and nvidia_smi_gpu_uuid.startswith("GPU-")
        ),
        "model_on_selected_cuda_device": (
            selected_device is not None and model_device == selected_device
        ),
        "inputs_on_selected_cuda_device": inputs_on_selected,
        "outputs_on_selected_cuda_device": outputs_on_selected,
    }
    return ExecutionDeviceObservation(
        environment={
            "cuda_available": cuda_available,
            "device_count": device_count,
            "selected_index": selected_index,
            "selected_name": selected_name,
            "torch_selected_gpu_uuid": selected_uuid,
            "selected_device": selected_device,
            "nvidia_smi_gpu_name": nvidia_smi_gpu_name,
            "nvidia_smi_gpu_uuid": nvidia_smi_gpu_uuid,
            "model_device": model_device,
            **tensor_devices,
        },
        invariants=invariants,
    )


def evaluate_raw_contract(
    model: Any,
    raw: RawDetectorOutput,
    scores: torch.Tensor,
    source: SourceContractObservation,
) -> RawContractObservation:
    """Evaluate raw tensor invariants without thresholding, NMS, or postprocessing."""
    config = model.config
    decoder_layers = int(config.decoder_layers)
    config_num_queries = int(config.num_queries)
    config_num_labels = int(config.num_labels)
    shapes = {
        "logits": list(raw.logits.shape),
        "pred_boxes": list(raw.final_boxes.shape),
        "intermediate_reference_points": list(raw.intermediate_boxes.shape),
    }
    class_heads = list(model.model.decoder.class_embed)
    invariants = {
        "config_num_queries_300": config_num_queries == 300,
        "config_num_labels_4": config_num_labels == 4,
        "config_decoder_layers_3": decoder_layers == 3,
        "decoder_class_heads_four_channels": (
            len(class_heads) == decoder_layers
            and all(getattr(head, "out_features", None) == 4 for head in class_heads)
        ),
        "logits_shape": shapes["logits"] == [2, 300, 4],
        "pred_boxes_shape": shapes["pred_boxes"] == [2, 300, 4],
        "intermediate_reference_points_shape": shapes["intermediate_reference_points"]
        == [2, decoder_layers, 300, 4],
        "decoder_layers_at_least_two": decoder_layers >= 2,
        "native_fifth_logit_absent": raw.logits.ndim == 3 and raw.logits.shape[-1] == 4,
        "final_boxes_are_last_layer": torch.equal(
            raw.final_boxes, raw.intermediate_boxes[:, -1, :, :]
        ),
        "penultimate_boxes_are_previous_layer": torch.equal(
            raw.penultimate_boxes, raw.intermediate_boxes[:, -2, :, :]
        ),
        "foreground_scores_are_sigmoid": (
            scores.shape == raw.logits.shape
            and torch.equal(scores, torch.sigmoid(raw.logits))
        ),
    }
    invariants.update(
        {name: value is True for name, value in source.invariants.items()}
    )
    errors = tuple(name for name, passed in invariants.items() if not passed)
    return RawContractObservation(
        config_num_queries=config_num_queries,
        config_num_labels=config_num_labels,
        decoder_layers=decoder_layers,
        shapes=shapes,
        invariants=invariants,
        status="PASS" if not errors else "FAIL",
        errors=errors,
    )


def _class_method(
    tree: ast.Module, class_name: str, method_name: str
) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for member in node.body:
                if isinstance(member, ast.FunctionDef) and member.name == method_name:
                    return member
    return None


def _is_name(node: ast.AST, name: str) -> bool:
    return isinstance(node, ast.Name) and node.id == name


def _is_stack_axis_one(node: ast.AST) -> bool:
    if not isinstance(node, ast.Call):
        return False
    function = node.func
    if not (
        isinstance(function, ast.Attribute)
        and _is_name(function.value, "torch")
        and function.attr == "stack"
    ):
        return False
    if not node.args or not _is_name(node.args[0], "intermediate_reference_points"):
        return False
    return any(
        keyword.arg == "dim"
        and isinstance(keyword.value, ast.Constant)
        and keyword.value.value == 1
        for keyword in node.keywords
    )


def _assigns_stack_axis_one(method: ast.FunctionDef | None) -> bool:
    if method is None:
        return False
    return any(
        isinstance(node, ast.Assign)
        and any(
            _is_name(target, "intermediate_reference_points") for target in node.targets
        )
        and _is_stack_axis_one(node.value)
        for node in ast.walk(method)
    )


def _has_no_query_permutation(method: ast.FunctionDef | None) -> bool:
    if method is None:
        return False
    forbidden = {
        "argsort",
        "gather",
        "index_select",
        "permute",
        "sort",
        "take_along_dim",
        "transpose",
    }
    return not any(
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in forbidden
        for node in ast.walk(method)
    )


def _is_negative_one(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.UnaryOp)
        and isinstance(node.op, ast.USub)
        and isinstance(node.operand, ast.Constant)
        and node.operand.value == 1
    )


def _final_boxes_use_last_layer(method: ast.FunctionDef | None) -> bool:
    if method is None:
        return False
    outputs_coord_bound = False
    final_bound = False
    for node in ast.walk(method):
        if not isinstance(node, ast.Assign):
            continue
        targets = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if "outputs_coord" in targets:
            value = node.value
            outputs_coord_bound = (
                isinstance(value, ast.Attribute)
                and value.attr == "intermediate_reference_points"
            )
        if "pred_boxes" in targets and isinstance(node.value, ast.Subscript):
            value = node.value
            dimensions = value.slice.elts if isinstance(value.slice, ast.Tuple) else []
            final_bound = (
                _is_name(value.value, "outputs_coord")
                and len(dimensions) == 2
                and _is_negative_one(dimensions[1])
            )
    return outputs_coord_bound and final_bound


def inspect_rtdetr_source_contract(path: Path) -> SourceContractObservation:
    """Prove the pinned source stacks layers at axis 1 without query reordering."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    decoder_forward = _class_method(tree, "RTDetrDecoder", "forward")
    detector_forward = _class_method(tree, "RTDetrForObjectDetection", "forward")
    return SourceContractObservation(
        invariants={
            "source_stack_axis_one": _assigns_stack_axis_one(decoder_forward),
            "source_no_query_permutation": _has_no_query_permutation(decoder_forward),
            "source_final_boxes_last_layer": _final_boxes_use_last_layer(
                detector_forward
            ),
        }
    )
