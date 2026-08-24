"""Pinned raw-output contract for Transformers RT-DETR."""

from __future__ import annotations

import ast
import math
import re
from collections.abc import Mapping, Sequence
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
    intermediate_logits: torch.Tensor
    enc_outputs_class: torch.Tensor
    enc_topk_logits: torch.Tensor
    final_boxes: torch.Tensor
    penultimate_boxes: torch.Tensor
    intermediate_boxes: torch.Tensor


@dataclass(frozen=True)
class SourceContractObservation:
    invariants: Mapping[str, bool]


@dataclass(frozen=True)
class LabeledLossCapture:
    logits: torch.Tensor
    outputs_class: torch.Tensor
    enc_topk_logits: torch.Tensor
    denoising_meta_values: Mapping[str, Any] | None
    auxiliary_outputs: Sequence[Mapping[str, torch.Tensor]]


@dataclass(frozen=True)
class LabeledContractObservation:
    loss_shape: Sequence[int]
    logits_shape: Sequence[int]
    intermediate_logits_shape: Sequence[int]
    enc_outputs_class_shape: Sequence[int]
    enc_topk_logits_shape: Sequence[int]
    decoder_auxiliary_shapes: Sequence[Sequence[int]]
    encoder_auxiliary_shapes: Sequence[Sequence[int]]
    denoising_auxiliary_shapes: Sequence[Sequence[int]]
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
    intermediate_logits = _required_tensor(outputs, "intermediate_logits")
    enc_outputs_class = _required_tensor(outputs, "enc_outputs_class")
    enc_topk_logits = _required_tensor(outputs, "enc_topk_logits")
    final_boxes = _required_tensor(outputs, "pred_boxes")
    intermediate = _required_tensor(outputs, "intermediate_reference_points")
    expected_ranks = (
        ("logits", logits, 3),
        ("intermediate_logits", intermediate_logits, 4),
        ("enc_outputs_class", enc_outputs_class, 3),
        ("enc_topk_logits", enc_topk_logits, 3),
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
        and logits.shape[:2]
        == (intermediate_logits.shape[0], intermediate_logits.shape[2])
        and logits.shape[:2] == enc_topk_logits.shape[:2]
        and logits.shape[0] == enc_outputs_class.shape[0]
        and intermediate_logits.shape[1] == intermediate.shape[1]
    ):
        raise ContractUnavailable("raw outputs must share batch and query dimensions")
    return RawDetectorOutput(
        logits=logits,
        intermediate_logits=intermediate_logits,
        enc_outputs_class=enc_outputs_class,
        enc_topk_logits=enc_topk_logits,
        final_boxes=final_boxes,
        penultimate_boxes=intermediate[:, -2, :, :],
        intermediate_boxes=intermediate,
    )


def foreground_scores(raw: RawDetectorOutput) -> torch.Tensor:
    """Return the four independent focal-loss foreground probabilities."""
    return torch.sigmoid(raw.logits)


def run_labeled_contract_forward(
    model: Any,
    *,
    pixel_values: torch.Tensor,
    pixel_mask: torch.Tensor,
    labels: Sequence[Mapping[str, torch.Tensor]],
) -> tuple[Any, LabeledLossCapture]:
    """Capture the exact tensors consumed by the pinned official labeled loss."""
    original_loss = model.loss_function
    capture: LabeledLossCapture | None = None

    def capturing_loss(
        logits,
        loss_labels,
        device,
        pred_boxes,
        config,
        outputs_class=None,
        outputs_coord=None,
        enc_topk_logits=None,
        enc_topk_bboxes=None,
        denoising_meta_values=None,
        **kwargs,
    ):
        nonlocal capture
        result = original_loss(
            logits,
            loss_labels,
            device,
            pred_boxes,
            config,
            outputs_class,
            outputs_coord,
            enc_topk_logits=enc_topk_logits,
            enc_topk_bboxes=enc_topk_bboxes,
            denoising_meta_values=denoising_meta_values,
            **kwargs,
        )
        if not isinstance(outputs_class, torch.Tensor):
            raise ContractUnavailable("labeled outputs_class is unavailable")
        if not isinstance(enc_topk_logits, torch.Tensor):
            raise ContractUnavailable("labeled enc_topk_logits is unavailable")
        if not isinstance(result, tuple) or len(result) != 3:
            raise ContractUnavailable("official RT-DETR loss result is unavailable")
        auxiliary_outputs = result[2]
        if not isinstance(auxiliary_outputs, Sequence) or isinstance(
            auxiliary_outputs, (str, bytes)
        ):
            raise ContractUnavailable("official auxiliary outputs are unavailable")
        if any(not isinstance(item, Mapping) for item in auxiliary_outputs):
            raise ContractUnavailable("official auxiliary output is malformed")
        capture = LabeledLossCapture(
            logits=logits,
            outputs_class=outputs_class,
            enc_topk_logits=enc_topk_logits,
            denoising_meta_values=denoising_meta_values,
            auxiliary_outputs=tuple(auxiliary_outputs),
        )
        return result

    model.loss_function = capturing_loss
    try:
        outputs = model(
            pixel_values=pixel_values,
            pixel_mask=pixel_mask,
            labels=labels,
        )
    finally:
        model.loss_function = original_loss
    if capture is None:
        raise ContractUnavailable("official labeled loss was not called")
    return outputs, capture


def _auxiliary_logits(
    auxiliary_outputs: Sequence[Mapping[str, torch.Tensor]],
) -> list[torch.Tensor]:
    logits: list[torch.Tensor] = []
    for item in auxiliary_outputs:
        value = item.get("logits")
        if not isinstance(value, torch.Tensor) or value.ndim != 3:
            raise ContractUnavailable("auxiliary logits are unavailable")
        logits.append(value)
    return logits


def observe_labeled_contract(
    model: Any, outputs: Any, capture: LabeledLossCapture
) -> LabeledContractObservation:
    """Observe every classification tensor reachable by the pinned labeled loss."""
    _ = model
    loss = _required_tensor(outputs, "loss")
    logits = _required_tensor(outputs, "logits")
    intermediate_logits = _required_tensor(outputs, "intermediate_logits")
    enc_outputs_class = _required_tensor(outputs, "enc_outputs_class")
    enc_topk_logits = _required_tensor(outputs, "enc_topk_logits")
    metadata = capture.denoising_meta_values
    if not isinstance(metadata, Mapping):
        raise ContractUnavailable("denoising metadata is unavailable")
    split = metadata.get("dn_num_split")
    if (
        not isinstance(split, Sequence)
        or isinstance(split, (str, bytes))
        or len(split) != 2
        or any(type(value) is not int or value <= 0 for value in split)
        or sum(split) != capture.outputs_class.shape[2]
    ):
        raise ContractUnavailable("dn_num_split is unavailable or malformed")
    if capture.outputs_class.ndim != 4:
        raise ContractUnavailable("labeled outputs_class must have rank 4")
    denoising_class, _ = torch.split(capture.outputs_class, list(split), dim=2)
    auxiliary_logits = _auxiliary_logits(capture.auxiliary_outputs)
    decoder_layers = capture.outputs_class.shape[1] - 1
    if decoder_layers <= 0 or len(auxiliary_logits) != decoder_layers + 1:
        raise ContractUnavailable("decoder and encoder auxiliaries are incomplete")
    decoder_auxiliary = auxiliary_logits[:decoder_layers]
    encoder_auxiliary = auxiliary_logits[decoder_layers:]
    denoising_auxiliary = [
        denoising_class[:, index] for index in range(denoising_class.shape[1])
    ]

    decoder_four = all(tensor.shape[-1] == 4 for tensor in decoder_auxiliary)
    encoder_four = (
        all(tensor.shape[-1] == 4 for tensor in encoder_auxiliary)
        and capture.enc_topk_logits.shape[-1] == 4
    )
    denoising_four = all(tensor.shape[-1] == 4 for tensor in denoising_auxiliary)
    direct_four = all(
        tensor.shape[-1] == 4
        for tensor in (
            logits,
            intermediate_logits,
            enc_outputs_class,
            enc_topk_logits,
            capture.logits,
            capture.outputs_class,
            capture.enc_topk_logits,
        )
    )
    finite_scalar = loss.ndim == 0 and bool(torch.isfinite(loss).item())
    invariants = {
        "labeled_logits_four_channels": direct_four,
        "decoder_auxiliary_logits_four_channels": decoder_four,
        "encoder_auxiliary_logits_four_channels": encoder_four,
        "denoising_auxiliary_logits_four_channels": denoising_four,
        "no_reachable_non_four_class_logits": (
            direct_four and decoder_four and encoder_four and denoising_four
        ),
        "labeled_forward_finite_scalar_loss": finite_scalar,
    }
    return LabeledContractObservation(
        loss_shape=list(loss.shape),
        logits_shape=list(logits.shape),
        intermediate_logits_shape=list(intermediate_logits.shape),
        enc_outputs_class_shape=list(enc_outputs_class.shape),
        enc_topk_logits_shape=list(enc_topk_logits.shape),
        decoder_auxiliary_shapes=[list(tensor.shape) for tensor in decoder_auxiliary],
        encoder_auxiliary_shapes=[list(tensor.shape) for tensor in encoder_auxiliary],
        denoising_auxiliary_shapes=[
            list(tensor.shape) for tensor in denoising_auxiliary
        ],
        invariants=invariants,
    )


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
        "intermediate_logits": list(raw.intermediate_logits.shape),
        "enc_outputs_class": list(raw.enc_outputs_class.shape),
        "enc_topk_logits": list(raw.enc_topk_logits.shape),
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
        "intermediate_logits_four_channels": shapes["intermediate_logits"]
        == [2, decoder_layers, 300, 4],
        "enc_outputs_class_four_channels": (
            raw.enc_outputs_class.ndim == 3
            and raw.enc_outputs_class.shape[0] == 2
            and raw.enc_outputs_class.shape[-1] == 4
        ),
        "enc_topk_logits_four_channels": shapes["enc_topk_logits"] == [2, 300, 4],
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


def inspect_rtdetr_loss_source_contract(path: Path) -> SourceContractObservation:
    """Prove how the pinned RT-DETR loss constructs every auxiliary branch."""
    tree = ast.parse(Path(path).read_text(encoding="utf-8"), filename=str(path))
    loss_function = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.FunctionDef)
            and node.name == "RTDetrForObjectDetectionLoss"
        ),
        None,
    )
    if loss_function is None:
        return SourceContractObservation(
            invariants={
                "loss_splits_outputs_class_dim_2": False,
                "loss_builds_decoder_auxiliaries": False,
                "loss_appends_enc_topk_logits": False,
                "loss_builds_denoising_auxiliaries": False,
            }
        )
    calls = [node for node in ast.walk(loss_function) if isinstance(node, ast.Call)]
    split_observed = any(
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "split"
        and call.args
        and _is_name(call.args[0], "outputs_class")
        and "dn_num_split" in ast.unparse(call)
        and any(
            keyword.arg == "dim"
            and isinstance(keyword.value, ast.Constant)
            and keyword.value.value == 2
            for keyword in call.keywords
        )
        for call in calls
    )
    decoder_auxiliary_observed = any(
        (
            (_is_name(call.func, "_set_aux_loss"))
            or (
                isinstance(call.func, ast.Attribute)
                and call.func.attr == "_set_aux_loss"
            )
        )
        and "outputs_class[:, :-1]" in ast.unparse(call)
        for call in calls
    )
    encoder_auxiliary_observed = any(
        isinstance(call.func, ast.Attribute)
        and call.func.attr == "extend"
        and "enc_topk_logits" in ast.unparse(call)
        for call in calls
    )
    denoising_auxiliary_observed = any(
        (
            (_is_name(call.func, "_set_aux_loss"))
            or (
                isinstance(call.func, ast.Attribute)
                and call.func.attr == "_set_aux_loss"
            )
        )
        and "dn_out_class" in ast.unparse(call)
        for call in calls
    )
    return SourceContractObservation(
        invariants={
            "loss_splits_outputs_class_dim_2": split_observed,
            "loss_builds_decoder_auxiliaries": decoder_auxiliary_observed,
            "loss_appends_enc_topk_logits": encoder_auxiliary_observed,
            "loss_builds_denoising_auxiliaries": denoising_auxiliary_observed,
        }
    )
