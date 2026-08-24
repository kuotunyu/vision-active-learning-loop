"""Dataset-independent RT-DETR executable-contract observations."""

from __future__ import annotations

import argparse
import copy
import hashlib
import inspect
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import torch
from PIL import Image
from transformers import RTDetrForObjectDetection, RTDetrImageProcessor

from ..artifacts.digests import canonical_json_sha256, sha256_file
from ..artifacts.receipts import (
    atomic_write_receipt,
    validate_receipt_for_run,
)
from ..cli_manifest import command
from ..environment import (
    EnvironmentContract,
    _configure_torch_runtime,
    environment_invariants,
    observe_environment,
)
from ..models.assets import (
    PinnedAssetSpec,
    load_pinned_asset_specs,
    verify_snapshot,
    verify_transformers_source,
)
from ..models.rtdetr_contract import (
    ContractUnavailable,
    evaluate_raw_contract,
    extract_raw_contract,
    foreground_scores,
    inspect_rtdetr_loss_source_contract,
    inspect_rtdetr_source_contract,
    observe_execution_device,
    observe_labeled_contract,
    reset_four_class_head,
    run_labeled_contract_forward,
)


class ModelContractInputError(ValueError):
    """Raised when probe inputs do not prove the approved offline boundary."""


@dataclass(frozen=True)
class SyntheticContractFixture:
    manifest: Mapping[str, Any]
    images: Sequence[Image.Image]
    annotations: Sequence[Mapping[str, Any]]
    input_sha256: str
    target_sha256: str


_APPROVED_SYNTHETIC_INPUT_SHA256 = (
    "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f"
)
_APPROVED_SYNTHETIC_TARGET_SHA256 = (
    "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198"
)


REQUIRED_MODEL_CONTRACT_INVARIANTS = (
    "aspect_preserving_size",
    "asset_receipt_pass",
    "bilinear_resize",
    "bottom_right_padding_is_zero",
    "canonical_environment",
    "config_decoder_layers_3",
    "config_num_labels_4",
    "config_num_queries_300",
    "class_reset_preserves_structure",
    "decoder_class_heads_four_channels",
    "decoder_auxiliary_logits_four_channels",
    "decoder_layers_at_least_two",
    "denoising_auxiliary_logits_four_channels",
    "denoising_class_embed_five_rows_padding_four",
    "enc_outputs_class_four_channels",
    "enc_topk_logits_four_channels",
    "encoder_auxiliary_logits_four_channels",
    "encoder_score_head_four_channels",
    "expected_valid_mask_rectangles",
    "exact_rdd_label_mappings",
    "exact_scipy",
    "final_boxes_are_last_layer",
    "foreground_scores_are_sigmoid",
    "four_class_head_reset_seed_17",
    "four_class_reset_rng_order_seed_17",
    "inputs_on_selected_cuda_device",
    "intermediate_reference_points_shape",
    "intermediate_logits_four_channels",
    "label_free_model_call",
    "labeled_forward_finite_scalar_loss",
    "labeled_model_call",
    "labels_absent",
    "live_snapshot_matches_asset_receipt",
    "live_transformers_source_matches_asset_receipt",
    "logits_shape",
    "model_eval_mode",
    "model_on_selected_cuda_device",
    "native_fifth_logit_absent",
    "no_reachable_non_four_class_logits",
    "normalization_disabled",
    "outputs_on_selected_cuda_device",
    "padding_enabled",
    "penultimate_boxes_are_previous_layer",
    "pixel_mask_shape",
    "pixel_values_shape",
    "pred_boxes_shape",
    "pretrained_coco_head_rows_not_reused",
    "rescale_one_over_255",
    "rescale_without_normalization_observed",
    "source_final_boxes_last_layer",
    "source_no_query_permutation",
    "source_stack_axis_one",
    "synthetic_targets_only",
    "torch_cuda_available",
    "torch_inference_mode",
    "torch_selected_gpu_is_canonical",
)
REQUIRED_MODEL_CONTRACT_SHAPES = (
    "enc_outputs_class",
    "enc_topk_logits",
    "intermediate_logits",
    "intermediate_reference_points",
    "logits",
    "pixel_mask",
    "pixel_values",
    "pred_boxes",
)
REQUIRED_LABELED_MODEL_CONTRACT_SHAPES = (
    "loss",
    "logits",
    "intermediate_logits",
    "enc_outputs_class",
    "enc_topk_logits",
    "decoder_auxiliary_logits",
    "encoder_auxiliary_logits",
    "denoising_auxiliary_logits",
)


@dataclass(frozen=True)
class ModelContractReceipt:
    model_repository: str
    model_revision: str
    transformers_version: str
    hashes: Mapping[str, str]
    source_files: Mapping[str, Mapping[str, object]]
    config_num_queries: int
    config_num_labels: int
    decoder_layers: int
    processor: Mapping[str, object]
    shapes: Mapping[str, list[int]]
    labeled_shapes: Mapping[str, object]
    observed_class_modules: Mapping[str, object]
    labeled_loss_hex: str
    loss_source_sha256: str
    synthetic_target_sha256: str
    invariants: Mapping[str, bool]
    environment: Mapping[str, object]
    parent_environment_receipt: Mapping[str, object]
    environment_receipt_sha256: str
    environment_receipt_content_sha256: str
    errors: tuple[str, ...]
    timestamp: str
    run_id: str

    @property
    def status(self) -> str:
        complete_invariants = {
            name: self.invariants.get(name, False)
            for name in REQUIRED_MODEL_CONTRACT_INVARIANTS
        }
        return (
            "PASS"
            if not self.errors
            and all(value is True for value in complete_invariants.values())
            else "FAIL"
        )

    def as_dict(self) -> dict[str, object]:
        complete_invariants = {
            name: self.invariants.get(name, False)
            for name in REQUIRED_MODEL_CONTRACT_INVARIANTS
        }
        false_invariants = [
            name for name, passed in complete_invariants.items() if passed is not True
        ]
        errors = list(dict.fromkeys([*self.errors, *false_invariants]))
        config = _config_document(
            self.config_num_queries,
            self.config_num_labels,
            self.decoder_layers,
        )
        normative = {
            **dict(self.hashes),
            "model": {
                "repository": self.model_repository,
                "revision": self.model_revision,
            },
            "transformers_version": self.transformers_version,
            "source_files": {
                name: dict(observation)
                for name, observation in sorted(self.source_files.items())
            },
            "config": config,
            "processor": dict(self.processor),
            "environment": dict(self.environment),
            "parent_environment_receipt": dict(self.parent_environment_receipt),
            "environment_receipt_sha256": self.environment_receipt_sha256,
            "environment_receipt_content_sha256": (
                self.environment_receipt_content_sha256
            ),
            "loss_source_sha256": self.loss_source_sha256,
            "synthetic_target_sha256": self.synthetic_target_sha256,
            "observed_shapes": {
                name: list(self.shapes.get(name, []))
                for name in REQUIRED_MODEL_CONTRACT_SHAPES
            },
            "labeled_observed_shapes": {
                name: copy.deepcopy(self.labeled_shapes.get(name, []))
                for name in REQUIRED_LABELED_MODEL_CONTRACT_SHAPES
            },
            "observed_class_modules": copy.deepcopy(dict(self.observed_class_modules)),
            "labeled_loss_hex": self.labeled_loss_hex,
            "invariants": dict(sorted(complete_invariants.items())),
            "status": self.status,
            "errors": errors,
        }
        return {
            "receipt_type": "model-contract",
            "schema_version": 1,
            "normative": normative,
            "metadata": {"timestamp": self.timestamp, "run_id": self.run_id},
        }


@dataclass(frozen=True)
class ProcessorContractObservation:
    shapes: Mapping[str, list[int]]
    invariants: Mapping[str, bool]


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _processor_document() -> dict[str, object]:
    return {
        "size": {"max_height": 640, "max_width": 640},
        "resample": int(Image.Resampling.BILINEAR),
        "do_pad": True,
        "pad_size": {"height": 640, "width": 640},
        "do_rescale": True,
        "rescale_factor": 1 / 255,
        "do_normalize": False,
    }


def _config_document(
    num_queries: int, num_labels: int, decoder_layers: int
) -> dict[str, object]:
    return {
        "num_queries": num_queries,
        "num_labels": num_labels,
        "decoder_layers": decoder_layers,
        "id2label": {
            str(index): label
            for index, label in enumerate(("D00", "D10", "D20", "D40"))
        },
        "label2id": {
            label: index for index, label in enumerate(("D00", "D10", "D20", "D40"))
        },
    }


def build_contract_processor() -> RTDetrImageProcessor:
    """Create the exact aspect-preserving, bottom/right-padding processor."""
    return RTDetrImageProcessor(do_resize=True, **_processor_document())


def prepare_contract_batch(
    processor: RTDetrImageProcessor, images: Sequence[Image.Image]
) -> Mapping[str, Any]:
    """Preprocess the label-free synthetic batch into PyTorch tensors."""
    return processor(images=list(images), return_tensors="pt")


def _size_value(size: object, name: str) -> object:
    if isinstance(size, Mapping):
        return size.get(name)
    return getattr(size, name, None)


def observe_processor_contract(
    processor: RTDetrImageProcessor, batch: Mapping[str, Any]
) -> ProcessorContractObservation:
    """Observe every normative processor and valid-mask invariant."""
    pixel_values = batch.get("pixel_values")
    pixel_mask = batch.get("pixel_mask")
    shapes = {
        "pixel_values": list(pixel_values.shape)
        if isinstance(pixel_values, torch.Tensor)
        else [],
        "pixel_mask": list(pixel_mask.shape)
        if isinstance(pixel_mask, torch.Tensor)
        else [],
    }

    expected_masks = torch.zeros((2, 640, 640), dtype=torch.int64)
    expected_masks[0, :320, :640] = 1
    expected_masks[1, :640, :320] = 1
    mask_matches = (
        isinstance(pixel_mask, torch.Tensor)
        and pixel_mask.dtype == torch.int64
        and torch.equal(pixel_mask.cpu(), expected_masks)
    )
    padding_is_zero = (
        isinstance(pixel_values, torch.Tensor)
        and tuple(pixel_values.shape) == (2, 3, 640, 640)
        and torch.count_nonzero(pixel_values[0, :, 320:, :]).item() == 0
        and torch.count_nonzero(pixel_values[1, :, :, 320:]).item() == 0
    )
    rescaled_only = (
        isinstance(pixel_values, torch.Tensor)
        and bool(torch.isfinite(pixel_values).all())
        and float(pixel_values.min()) >= 0.0
        and float(pixel_values.max()) <= 1.0
    )
    invariants = {
        "aspect_preserving_size": (
            _size_value(processor.size, "max_height") == 640
            and _size_value(processor.size, "max_width") == 640
        ),
        "bilinear_resize": int(processor.resample) == int(Image.Resampling.BILINEAR),
        "padding_enabled": (
            processor.do_pad is True
            and _size_value(processor.pad_size, "height") == 640
            and _size_value(processor.pad_size, "width") == 640
        ),
        "rescale_one_over_255": (
            processor.do_rescale is True and float(processor.rescale_factor) == 1 / 255
        ),
        "normalization_disabled": processor.do_normalize is False,
        "pixel_values_shape": shapes["pixel_values"] == [2, 3, 640, 640],
        "pixel_mask_shape": shapes["pixel_mask"] == [2, 640, 640],
        "expected_valid_mask_rectangles": bool(mask_matches),
        "bottom_right_padding_is_zero": bool(padding_is_zero),
        "rescale_without_normalization_observed": bool(rescaled_only),
        "labels_absent": "labels" not in batch,
    }
    return ProcessorContractObservation(shapes=shapes, invariants=invariants)


def _mapping(value: object, description: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ModelContractInputError(f"{description} must be an object")
    return value


def load_synthetic_contract_fixture(path: Path) -> SyntheticContractFixture:
    """Load and validate the only approved Wave 0 inputs and targets."""
    try:
        manifest = _mapping(
            json.loads(Path(path).read_text(encoding="utf-8")), "fixture manifest"
        )
    except (OSError, json.JSONDecodeError) as error:
        raise ModelContractInputError("unable to load fixture manifest") from error
    if manifest.get("schema_version") != 1 or manifest.get("fixture_set") != (
        "wave0-rtdetr-contract"
    ):
        raise ModelContractInputError("unexpected fixture manifest identity")
    entries = manifest.get("images")
    if not isinstance(entries, list) or len(entries) != 2:
        raise ModelContractInputError("fixture manifest requires exactly two images")
    targets = manifest.get("targets")
    if not isinstance(targets, list) or len(targets) != 2:
        raise ModelContractInputError("fixture manifest requires exactly two targets")
    expected = (
        ("wide-gradient", "wide-gradient.ppm", 640, 320),
        ("tall-checker", "tall-checker.ppm", 320, 640),
    )
    images: list[Image.Image] = []
    for item, identity in zip(entries, expected):
        entry = _mapping(item, "fixture image")
        observed_identity = (
            entry.get("id"),
            entry.get("filename"),
            entry.get("width"),
            entry.get("height"),
        )
        if observed_identity != identity or entry.get("pattern") != identity[0]:
            raise ModelContractInputError("fixture identity or geometry differs")
        width, height = identity[2], identity[3]
        if identity[0] == "wide-gradient":
            pixels = bytes(
                channel
                for y in range(height)
                for x in range(width)
                for channel in (x % 256, y % 256, (x + y) % 256)
            )
        else:
            pixels = bytes(
                channel
                for y in range(height)
                for x in range(width)
                for channel in (
                    255 - (x % 256),
                    (2 * y) % 256,
                    255 if ((x // 32) + (y // 32)) % 2 else 0,
                )
            )
        if hashlib.sha256(pixels).hexdigest() != entry.get("pixel_sha256"):
            raise ModelContractInputError("fixture pixel digest differs")
        images.append(Image.frombytes("RGB", (width, height), pixels))

    expected_targets = (("wide-gradient", 1), ("tall-checker", 2))
    for item, (fixture_id, image_id), (_, _, width, height) in zip(
        targets, expected_targets, expected
    ):
        target = _mapping(item, "fixture target")
        if set(target) != {"fixture_id", "image_id", "annotations"}:
            raise ModelContractInputError("fixture target fields differ")
        if (target.get("fixture_id"), target.get("image_id")) != (
            fixture_id,
            image_id,
        ):
            raise ModelContractInputError("fixture target identity differs")
        annotations = target.get("annotations")
        if not isinstance(annotations, list) or len(annotations) != 1:
            raise ModelContractInputError("fixture requires exactly one annotation")
        annotation = _mapping(annotations[0], "fixture annotation")
        if set(annotation) != {
            "id",
            "image_id",
            "category_id",
            "bbox",
            "area",
            "iscrowd",
        }:
            raise ModelContractInputError("fixture annotation fields differ")
        if annotation.get("id") != image_id or annotation.get("image_id") != image_id:
            raise ModelContractInputError("fixture annotation image identity differs")
        category_id = annotation.get("category_id")
        if (
            not isinstance(category_id, int)
            or isinstance(category_id, bool)
            or not 0 <= category_id < 4
        ):
            raise ModelContractInputError("fixture category must be in [0, 3]")
        bbox = annotation.get("bbox")
        if (
            not isinstance(bbox, list)
            or len(bbox) != 4
            or any(
                not isinstance(value, (int, float)) or isinstance(value, bool)
                for value in bbox
            )
        ):
            raise ModelContractInputError("fixture bbox must contain four numbers")
        x, y, box_width, box_height = (float(value) for value in bbox)
        if (
            x < 0
            or y < 0
            or box_width <= 0
            or box_height <= 0
            or x + box_width > width
            or y + box_height > height
        ):
            raise ModelContractInputError("fixture bbox is outside its source image")
        area = annotation.get("area")
        if not isinstance(area, (int, float)) or isinstance(area, bool):
            raise ModelContractInputError("fixture area must be numeric")
        if float(area) != box_width * box_height:
            raise ModelContractInputError("fixture area differs from bbox geometry")
        if annotation.get("iscrowd") != 0:
            raise ModelContractInputError("fixture iscrowd must be zero")

    input_document = {
        "schema_version": manifest["schema_version"],
        "fixture_set": manifest["fixture_set"],
        "images": entries,
    }
    target_document = {
        "schema_version": manifest["schema_version"],
        "fixture_set": manifest["fixture_set"],
        "targets": targets,
    }
    input_sha256 = canonical_json_sha256(input_document)
    target_sha256 = canonical_json_sha256(target_document)
    if input_sha256 != _APPROVED_SYNTHETIC_INPUT_SHA256:
        raise ModelContractInputError("synthetic input digest differs")
    if target_sha256 != _APPROVED_SYNTHETIC_TARGET_SHA256:
        raise ModelContractInputError("synthetic target digest differs")
    return SyntheticContractFixture(
        manifest=copy.deepcopy(dict(manifest)),
        images=images,
        annotations=copy.deepcopy(targets),
        input_sha256=input_sha256,
        target_sha256=target_sha256,
    )


def _load_fixture_images(path: Path) -> tuple[Mapping[str, Any], list[Image.Image]]:
    fixture = load_synthetic_contract_fixture(path)
    return fixture.manifest, list(fixture.images)


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and bool(is_junction()))


def _artifact_root() -> Path:
    configured = os.environ.get("VAL_ARTIFACT_ROOT")
    if not configured:
        raise ModelContractInputError("VAL_ARTIFACT_ROOT is required")
    root_input = Path(configured).expanduser()
    if not root_input.is_absolute() or _is_link_or_junction(root_input):
        raise ModelContractInputError(
            "VAL_ARTIFACT_ROOT must be an existing absolute non-link directory"
        )
    try:
        root = root_input.resolve(strict=True)
    except OSError as error:
        raise ModelContractInputError("VAL_ARTIFACT_ROOT is unavailable") from error
    if not root.is_dir():
        raise ModelContractInputError("VAL_ARTIFACT_ROOT must be a directory")
    if "VAL_DATA_ROOT" in os.environ:
        raise ModelContractInputError("VAL_DATA_ROOT must remain unset for Wave 0")
    return root


def _required_child_directory(parent: Path, name: str) -> Path:
    candidate = parent / name
    if _is_link_or_junction(candidate):
        raise ModelContractInputError(f"{name} directory link is forbidden")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as error:
        raise ModelContractInputError(f"{name} directory is unavailable") from error
    if not resolved.is_dir() or not resolved.is_relative_to(parent):
        raise ModelContractInputError(f"{name} directory escapes its parent")
    return resolved


def _snapshot_root(root: Path, spec: PinnedAssetSpec) -> Path:
    wave_root = _required_child_directory(root, "wave0")
    cache_root = _required_child_directory(wave_root, "model_cache")
    candidates = (
        cache_root / "snapshots" / spec.repo_id.replace("/", "--") / spec.revision,
        cache_root
        / f"models--{spec.repo_id.replace('/', '--')}"
        / "snapshots"
        / spec.revision,
    )
    for candidate in candidates:
        if candidate.is_dir():
            if _is_link_or_junction(candidate):
                raise ModelContractInputError("model snapshot link is forbidden")
            resolved = candidate.resolve(strict=True)
            if not resolved.is_relative_to(cache_root):
                raise ModelContractInputError("model snapshot escapes model_cache")
            for parent in candidate.parents:
                if parent == cache_root:
                    break
                if _is_link_or_junction(parent):
                    raise ModelContractInputError(
                        "model snapshot parent link is forbidden"
                    )
            return resolved
    raise ModelContractInputError("exact RT-DETR snapshot is unavailable")


def _source_document(
    observations: Mapping[str, Any],
) -> dict[str, dict[str, object]]:
    return {
        name: {"size": item.size, "sha256": item.sha256}
        for name, item in sorted(observations.items())
    }


def _runtime_environment() -> tuple[dict[str, object], list[str]]:
    config_path = _project_root() / "configs" / "environment" / "wave0.yaml"
    contract = EnvironmentContract.from_yaml(config_path)
    _configure_torch_runtime(contract)
    observed = observe_environment()
    observed["data_root_unset"] = "VAL_DATA_ROOT" not in os.environ
    errors = contract.validate(observed)
    if observed["data_root_unset"] is not True:
        errors.append("VAL_DATA_ROOT must remain unset for Wave 0")
    environment = {
        **observed,
        "status": "FAIL" if errors else "PASS",
        "errors": list(errors),
    }
    return environment, errors


def _environment_binding_errors(
    parent_environment: Mapping[str, object], live_environment: Mapping[str, object]
) -> list[str]:
    """Compare independently observed live fields with a validated parent."""
    return [
        f"live {field} differs from parent environment receipt"
        for field, expected in parent_environment.items()
        if live_environment.get(field) != expected
    ]


def _unobserved_torch_execution() -> dict[str, object]:
    return {
        "cuda_available": False,
        "device_count": 0,
        "selected_index": None,
        "selected_name": None,
        "torch_selected_gpu_uuid": None,
        "selected_device": None,
        "nvidia_smi_gpu_name": None,
        "nvidia_smi_gpu_uuid": None,
        "model_device": None,
        "pixel_values_device": None,
        "pixel_mask_device": None,
        "logits_device": None,
        "final_boxes_device": None,
        "penultimate_boxes_device": None,
        "intermediate_boxes_device": None,
    }


def _canonical_source_sha256(path: Path) -> str:
    """Hash UTF-8 source after universal-newline checkout normalization."""
    normalized = Path(path).read_text(encoding="utf-8")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _probe_hash() -> str:
    source_files = (
        Path(__file__).resolve(),
        Path(inspect.getfile(reset_four_class_head)).resolve(),
        _project_root() / "scripts" / "generate_wave0_fixtures.py",
    )
    observations = {
        str(path.relative_to(_project_root())).replace("\\", "/"): (
            _canonical_source_sha256(path)
        )
        for path in source_files
    }
    return canonical_json_sha256(observations)


def _fixture_manifest_hash(path: Path) -> str:
    return load_synthetic_contract_fixture(path).input_sha256


def _unobserved_labeled_shapes() -> dict[str, object]:
    return {
        "loss": [],
        "logits": [],
        "intermediate_logits": [],
        "enc_outputs_class": [],
        "enc_topk_logits": [],
        "decoder_auxiliary_logits": [[]],
        "encoder_auxiliary_logits": [[]],
        "denoising_auxiliary_logits": [[]],
    }


def _unobserved_class_modules(decoder_layers: int) -> dict[str, object]:
    linear_placeholder = {
        "replaced": False,
        "in_features": 0,
        "out_features": 0,
        "bias": False,
        "device": "",
        "dtype": "",
    }
    return {
        "decoder_class_heads": [
            {
                "path": f"model.model.decoder.class_embed[{index}]",
                **linear_placeholder,
            }
            for index in range(max(decoder_layers, 0))
        ],
        "denoising_class_embed": {
            "path": "model.model.denoising_class_embed",
            "replaced": False,
            "embedding_dim": 0,
            "num_embeddings": 0,
            "padding_idx": -1,
            "device": "",
            "dtype": "",
        },
        "encoder_score_head": {
            "path": "model.model.enc_score_head",
            **linear_placeholder,
        },
        "num_labels": 0,
        "id2label": {},
        "label2id": {},
        "reset_seed": 17,
        "replacement_order": [],
        "deterministic_replay": False,
        "structure_preserved": False,
        "pretrained_class_rows_reused": True,
    }


def _linear_module_observation(
    path: str, module: torch.nn.Linear, *, replaced: bool
) -> dict[str, object]:
    return {
        "path": path,
        "replaced": replaced,
        "in_features": module.in_features,
        "out_features": module.out_features,
        "bias": module.bias is not None,
        "device": str(module.weight.device),
        "dtype": str(module.weight.dtype),
    }


def _embedding_module_observation(
    module: torch.nn.Embedding, *, replaced: bool
) -> dict[str, object]:
    return {
        "path": "model.model.denoising_class_embed",
        "replaced": replaced,
        "embedding_dim": module.embedding_dim,
        "num_embeddings": module.num_embeddings,
        "padding_idx": module.padding_idx,
        "device": str(module.weight.device),
        "dtype": str(module.weight.dtype),
    }


def _module_state(module: torch.nn.Module) -> dict[str, torch.Tensor]:
    return {
        name: tensor.detach().clone() for name, tensor in module.state_dict().items()
    }


def _state_equal(
    left: Mapping[str, torch.Tensor], right: Mapping[str, torch.Tensor]
) -> bool:
    return set(left) == set(right) and all(
        torch.equal(left[name], right[name]) for name in left
    )


def _rows(module: torch.nn.Module) -> list[torch.Tensor]:
    weight = getattr(module, "weight", None)
    if not isinstance(weight, torch.Tensor) or weight.ndim != 2:
        return []
    return [row.detach().clone() for row in weight]


def _class_reset_observation(model: Any) -> tuple[dict[str, object], dict[str, bool]]:
    detector = getattr(model, "model", None)
    decoder = getattr(detector, "decoder", None)
    try:
        old_heads = list(getattr(decoder, "class_embed", None))
    except TypeError as error:
        raise ContractUnavailable("class-dependent modules are unavailable") from error
    old_denoising = getattr(detector, "denoising_class_embed", None)
    old_encoder = getattr(detector, "enc_score_head", None)
    if (
        not old_heads
        or any(not isinstance(head, torch.nn.Linear) for head in old_heads)
        or not isinstance(old_denoising, torch.nn.Embedding)
        or not isinstance(old_encoder, torch.nn.Linear)
    ):
        raise ContractUnavailable("class-dependent modules are unavailable")
    original_rows = [
        row
        for module in (*old_heads, old_denoising, old_encoder)
        for row in _rows(module)
    ]

    reset_four_class_head(model, seed=17)
    first_modules = [
        *model.model.decoder.class_embed,
        model.model.denoising_class_embed,
        model.model.enc_score_head,
    ]
    first_states = [_module_state(module) for module in first_modules]
    reset_four_class_head(model, seed=17)
    heads = list(model.model.decoder.class_embed)
    denoising = model.model.denoising_class_embed
    encoder = model.model.enc_score_head
    active_modules = [*heads, denoising, encoder]
    deterministic_replay = all(
        _state_equal(expected, _module_state(module))
        for expected, module in zip(first_states, active_modules)
    )
    structure_preserved = (
        len(heads) == len(old_heads)
        and all(
            head.in_features == old.in_features
            and (head.bias is None) == (old.bias is None)
            and head.weight.device == old.weight.device
            and head.weight.dtype == old.weight.dtype
            for head, old in zip(heads, old_heads)
        )
        and denoising.embedding_dim == old_denoising.embedding_dim
        and denoising.weight.device == old_denoising.weight.device
        and denoising.weight.dtype == old_denoising.weight.dtype
        and encoder.in_features == old_encoder.in_features
        and (encoder.bias is None) == (old_encoder.bias is None)
        and encoder.weight.device == old_encoder.weight.device
        and encoder.weight.dtype == old_encoder.weight.dtype
    )
    replacement_rows = [
        row
        for module in active_modules
        for row in _rows(module)
        if not (
            module is denoising
            and denoising.padding_idx is not None
            and torch.equal(row, denoising.weight[denoising.padding_idx])
        )
    ]
    pretrained_rows_reused = any(
        replacement.shape == original.shape and torch.equal(replacement, original)
        for replacement in replacement_rows
        for original in original_rows
    )
    replacement_order = [
        *(f"model.model.decoder.class_embed[{index}]" for index in range(len(heads))),
        "model.model.denoising_class_embed",
        "model.model.enc_score_head",
    ]
    observations = {
        "decoder_class_heads": [
            _linear_module_observation(
                f"model.model.decoder.class_embed[{index}]",
                head,
                replaced=head is not old_heads[index],
            )
            for index, head in enumerate(heads)
        ],
        "denoising_class_embed": _embedding_module_observation(
            denoising, replaced=denoising is not old_denoising
        ),
        "encoder_score_head": _linear_module_observation(
            "model.model.enc_score_head",
            encoder,
            replaced=encoder is not old_encoder,
        ),
        "num_labels": model.config.num_labels,
        "id2label": {
            str(index): label for index, label in model.config.id2label.items()
        },
        "label2id": dict(model.config.label2id),
        "reset_seed": 17,
        "replacement_order": replacement_order,
        "deterministic_replay": deterministic_replay,
        "structure_preserved": structure_preserved,
        "pretrained_class_rows_reused": pretrained_rows_reused,
    }
    invariants = {
        "decoder_class_heads_four_channels": all(
            head.out_features == 4 for head in heads
        ),
        "denoising_class_embed_five_rows_padding_four": (
            denoising.num_embeddings == 5 and denoising.padding_idx == 4
        ),
        "encoder_score_head_four_channels": encoder.out_features == 4,
        "exact_rdd_label_mappings": (
            model.config.num_labels == 4
            and model.config.id2label == {0: "D00", 1: "D10", 2: "D20", 3: "D40"}
            and model.config.label2id == {"D00": 0, "D10": 1, "D20": 2, "D40": 3}
        ),
        "class_reset_preserves_structure": structure_preserved,
        "four_class_head_reset_seed_17": deterministic_replay,
        "four_class_reset_rng_order_seed_17": deterministic_replay,
        "pretrained_coco_head_rows_not_reused": not pretrained_rows_reused,
    }
    return observations, invariants


def _receipt_hashes(
    asset_model: Mapping[str, Any],
    source_files: Mapping[str, Mapping[str, object]],
    fixture_manifest: Path,
    environment: Mapping[str, object],
    config: Mapping[str, object],
    processor: Mapping[str, object],
) -> dict[str, str]:
    files = _mapping(asset_model.get("files"), "RT-DETR asset files")
    relevant_source = {
        name: dict(item)
        for name, item in source_files.items()
        if name.startswith("models/rt_detr/") or name == "loss/loss_rt_detr.py"
    }
    fixture = load_synthetic_contract_fixture(fixture_manifest)
    loss_source = _mapping(
        source_files.get("loss/loss_rt_detr.py"), "RT-DETR loss source"
    )
    return {
        "model_sha256": str(
            _mapping(files["model.safetensors"], "model file")["sha256"]
        ),
        "config_sha256": canonical_json_sha256(dict(config)),
        "config_file_sha256": str(
            _mapping(files["config.json"], "config file")["sha256"]
        ),
        "source_sha256": canonical_json_sha256(relevant_source),
        "processor_sha256": canonical_json_sha256(dict(processor)),
        "processor_file_sha256": str(
            _mapping(files["preprocessor_config.json"], "processor file")["sha256"]
        ),
        "fixture_sha256": fixture.input_sha256,
        "loss_source_sha256": str(loss_source["sha256"]),
        "synthetic_target_sha256": fixture.target_sha256,
        "probe_sha256": _probe_hash(),
        "environment_sha256": canonical_json_sha256(dict(environment)),
    }


def _model_receipt(
    *,
    spec: PinnedAssetSpec,
    asset_model: Mapping[str, Any],
    source_files: Mapping[str, Mapping[str, object]],
    fixture_manifest: Path,
    environment: Mapping[str, object],
    parent_environment_receipt: Mapping[str, object],
    environment_receipt_sha256: str,
    run_id: str,
    config_num_queries: int,
    config_num_labels: int,
    decoder_layers: int,
    shapes: Mapping[str, list[int]],
    labeled_shapes: Mapping[str, object],
    observed_class_modules: Mapping[str, object],
    labeled_loss_hex: str,
    invariants: Mapping[str, bool],
    errors: Sequence[str],
) -> ModelContractReceipt:
    relevant_source = {
        name: dict(item)
        for name, item in source_files.items()
        if name.startswith("models/rt_detr/") or name == "loss/loss_rt_detr.py"
    }
    config = _config_document(
        config_num_queries,
        config_num_labels,
        decoder_layers,
    )
    processor = _processor_document()
    receipt_hashes = _receipt_hashes(
        asset_model,
        source_files,
        fixture_manifest,
        environment,
        config,
        processor,
    )
    return ModelContractReceipt(
        model_repository=spec.repo_id,
        model_revision=spec.revision,
        transformers_version=spec.transformers_version,
        hashes=receipt_hashes,
        source_files=relevant_source,
        config_num_queries=config_num_queries,
        config_num_labels=config_num_labels,
        decoder_layers=decoder_layers,
        processor=processor,
        shapes=shapes,
        labeled_shapes=labeled_shapes,
        observed_class_modules=observed_class_modules,
        labeled_loss_hex=labeled_loss_hex,
        loss_source_sha256=receipt_hashes["loss_source_sha256"],
        synthetic_target_sha256=receipt_hashes["synthetic_target_sha256"],
        invariants=invariants,
        environment=environment,
        parent_environment_receipt=parent_environment_receipt,
        environment_receipt_sha256=environment_receipt_sha256,
        environment_receipt_content_sha256=str(
            _mapping(
                parent_environment_receipt.get("metadata"),
                "parent environment metadata",
            )["receipt_content_sha256"]
        ),
        errors=tuple(errors),
        timestamp=datetime.now(UTC).isoformat(),
        run_id=run_id,
    )


def run_model_contract_probe(
    spec: PinnedAssetSpec | None,
    asset_receipt: Mapping[str, object],
    fixture_manifest: Path,
    parent_environment_receipt: Mapping[str, object],
    environment_receipt_sha256: str,
    run_id: str,
) -> ModelContractReceipt:
    """Execute the exact pinned RT-DETR label-free contract on canonical CUDA."""
    normative = _mapping(asset_receipt.get("normative"), "asset receipt normative")
    if normative.get("status") != "PASS":
        raise ModelContractInputError("asset receipt must have PASS status")
    if spec is None:
        raise ModelContractInputError("the approved RT-DETR spec is required")
    validate_receipt_for_run(
        parent_environment_receipt,
        _project_root() / "schemas" / "environment-receipt.schema.json",
        run_id,
    )
    parent_environment_normative = _mapping(
        parent_environment_receipt.get("normative"),
        "parent environment normative",
    )
    if parent_environment_normative.get("status") != "PASS":
        raise ModelContractInputError("parent environment receipt must be PASS")
    parent_environment = _mapping(
        parent_environment_normative.get("observed"),
        "parent environment observation",
    )
    validate_receipt_for_run(
        asset_receipt,
        _project_root() / "schemas" / "model-asset-receipt.schema.json",
        run_id,
    )
    models = _mapping(normative.get("models"), "asset receipt models")
    asset_model = _mapping(models.get("rtdetr"), "RT-DETR asset receipt")
    if (asset_model.get("repo_id"), asset_model.get("revision")) != (
        spec.repo_id,
        spec.revision,
    ):
        raise ModelContractInputError("asset receipt RT-DETR identity differs")

    root = _artifact_root()
    snapshot = _snapshot_root(root, spec)
    verified_model = verify_snapshot(spec, snapshot).as_dict()
    if verified_model != dict(asset_model):
        raise ModelContractInputError(
            "live RT-DETR snapshot differs from asset receipt"
        )
    source_observations = verify_transformers_source(spec)
    source_files = _source_document(source_observations)
    asset_transformers = _mapping(
        normative.get("transformers"), "asset receipt transformers"
    )
    if (
        asset_transformers.get("version") != spec.transformers_version
        or asset_transformers.get("files") != source_files
    ):
        raise ModelContractInputError(
            "live Transformers source differs from asset receipt"
        )

    fixture = load_synthetic_contract_fixture(fixture_manifest)
    images = list(fixture.images)
    processor = build_contract_processor()
    batch = prepare_contract_batch(processor, images)
    processor_observation = observe_processor_contract(processor, batch)
    environment, environment_errors = _runtime_environment()
    environment_errors.extend(
        _environment_binding_errors(parent_environment, environment)
    )
    environment = {
        **environment,
        "torch_execution": _unobserved_torch_execution(),
    }
    base_config = _mapping(asset_model.get("config"), "RT-DETR config")
    base_shapes = dict(processor_observation.shapes)
    base_labeled_shapes = _unobserved_labeled_shapes()
    base_class_modules = _unobserved_class_modules(
        int(base_config.get("decoder_layers", 0))
    )
    base_invariants = {
        "logits_shape": False,
        "asset_receipt_pass": True,
        "live_snapshot_matches_asset_receipt": True,
        "live_transformers_source_matches_asset_receipt": True,
        "canonical_environment": not environment_errors,
        "exact_scipy": environment_invariants(
            EnvironmentContract.from_yaml(
                _project_root() / "configs" / "environment" / "wave0.yaml"
            ),
            environment,
        )["exact_scipy"],
        **processor_observation.invariants,
        "synthetic_targets_only": fixture.target_sha256
        == _APPROVED_SYNTHETIC_TARGET_SHA256,
    }
    if environment_errors:
        return _model_receipt(
            spec=spec,
            asset_model=asset_model,
            source_files=source_files,
            fixture_manifest=fixture_manifest,
            environment=environment,
            parent_environment_receipt=parent_environment_receipt,
            environment_receipt_sha256=environment_receipt_sha256,
            run_id=run_id,
            config_num_queries=int(base_config.get("num_queries", 0)),
            config_num_labels=4,
            decoder_layers=int(base_config.get("decoder_layers", 0)),
            shapes=base_shapes,
            labeled_shapes=base_labeled_shapes,
            observed_class_modules=base_class_modules,
            labeled_loss_hex="",
            invariants=base_invariants,
            errors=environment_errors,
        )

    source_path = Path(inspect.getfile(RTDetrForObjectDetection))
    source_contract = inspect_rtdetr_source_contract(source_path)
    loss_source_path = source_path.parents[2] / "loss" / "loss_rt_detr.py"
    loss_source_contract = inspect_rtdetr_loss_source_contract(loss_source_path)
    model: RTDetrForObjectDetection | None = None
    try:
        if not all(loss_source_contract.invariants.values()):
            raise ContractUnavailable("pinned labeled-loss data flow is unproven")
        model = RTDetrForObjectDetection.from_pretrained(
            snapshot,
            local_files_only=True,
            use_safetensors=True,
        )
        observed_class_modules, reset_invariants = _class_reset_observation(model)
        model.eval()
        selected_device = torch.device("cuda", torch.cuda.current_device())
        model.to(selected_device)
        pixel_values = batch["pixel_values"].to(selected_device)
        pixel_mask = batch["pixel_mask"].to(selected_device)
        with torch.inference_mode():
            inference_mode_observed = torch.is_inference_mode_enabled()
            outputs = model(pixel_values=pixel_values, pixel_mask=pixel_mask)
        label_free_eval_mode = not model.training
        raw = extract_raw_contract(outputs)
        raw_observation = evaluate_raw_contract(
            model, raw, foreground_scores(raw), source_contract
        )
        expected_gpu_name = EnvironmentContract.from_yaml(
            _project_root() / "configs" / "environment" / "wave0.yaml"
        ).gpu_name
        device_observation = observe_execution_device(
            model,
            pixel_values,
            pixel_mask,
            raw,
            expected_gpu_name=expected_gpu_name,
            nvidia_smi_gpu_name=(
                str(environment["gpu_name"])
                if isinstance(environment.get("gpu_name"), str)
                else None
            ),
            nvidia_smi_gpu_uuid=(
                str(environment["gpu_uuid"])
                if isinstance(environment.get("gpu_uuid"), str)
                else None
            ),
        )
        environment = {
            **environment,
            "torch_execution": dict(device_observation.environment),
        }
        labeled_batch = processor(
            images=images,
            annotations=fixture.annotations,
            return_tensors="pt",
        )
        labeled_pixel_values = labeled_batch["pixel_values"].to(selected_device)
        labeled_pixel_mask = labeled_batch["pixel_mask"].to(selected_device)
        labels = [
            {
                name: value.to(selected_device)
                if isinstance(value, torch.Tensor)
                else value
                for name, value in label.items()
            }
            for label in labeled_batch["labels"]
        ]
        with torch.random.fork_rng(devices=[selected_device.index]):
            torch.manual_seed(17)
            torch.cuda.manual_seed_all(17)
            model.train()
            with torch.no_grad():
                labeled_outputs, labeled_capture = run_labeled_contract_forward(
                    model,
                    pixel_values=labeled_pixel_values,
                    pixel_mask=labeled_pixel_mask,
                    labels=labels,
                )
        labeled_observation = observe_labeled_contract(
            model, labeled_outputs, labeled_capture
        )
        labeled_shapes = {
            "loss": list(labeled_observation.loss_shape),
            "logits": list(labeled_observation.logits_shape),
            "intermediate_logits": list(labeled_observation.intermediate_logits_shape),
            "enc_outputs_class": list(labeled_observation.enc_outputs_class_shape),
            "enc_topk_logits": list(labeled_observation.enc_topk_logits_shape),
            "decoder_auxiliary_logits": [
                list(shape) for shape in labeled_observation.decoder_auxiliary_shapes
            ],
            "encoder_auxiliary_logits": [
                list(shape) for shape in labeled_observation.encoder_auxiliary_shapes
            ],
            "denoising_auxiliary_logits": [
                list(shape) for shape in labeled_observation.denoising_auxiliary_shapes
            ],
        }
        invariants = {
            **base_invariants,
            **processor_observation.invariants,
            **raw_observation.invariants,
            **device_observation.invariants,
            **reset_invariants,
            **labeled_observation.invariants,
            "canonical_environment": True,
            "model_eval_mode": label_free_eval_mode,
            "torch_inference_mode": inference_mode_observed,
            "label_free_model_call": "labels" not in batch,
            "labeled_model_call": len(labels) == len(images),
            "synthetic_targets_only": fixture.target_sha256
            == _APPROVED_SYNTHETIC_TARGET_SHA256,
        }
        shapes = {**base_shapes, **raw_observation.shapes}
        errors = [name for name, passed in invariants.items() if passed is not True]
        return _model_receipt(
            spec=spec,
            asset_model=asset_model,
            source_files=source_files,
            fixture_manifest=fixture_manifest,
            environment=environment,
            parent_environment_receipt=parent_environment_receipt,
            environment_receipt_sha256=environment_receipt_sha256,
            run_id=run_id,
            config_num_queries=raw_observation.config_num_queries,
            config_num_labels=raw_observation.config_num_labels,
            decoder_layers=raw_observation.decoder_layers,
            shapes=shapes,
            labeled_shapes=labeled_shapes,
            observed_class_modules=observed_class_modules,
            labeled_loss_hex=float(labeled_outputs.loss.item()).hex(),
            invariants=invariants,
            errors=errors,
        )
    except (ContractUnavailable, RuntimeError, ValueError) as error:
        invariants = {**base_invariants, **source_contract.invariants}
        return _model_receipt(
            spec=spec,
            asset_model=asset_model,
            source_files=source_files,
            fixture_manifest=fixture_manifest,
            environment=environment,
            parent_environment_receipt=parent_environment_receipt,
            environment_receipt_sha256=environment_receipt_sha256,
            run_id=run_id,
            config_num_queries=int(base_config.get("num_queries", 0)),
            config_num_labels=int(
                getattr(getattr(model, "config", None), "num_labels", 4)
            ),
            decoder_layers=int(base_config.get("decoder_layers", 0)),
            shapes=base_shapes,
            labeled_shapes=base_labeled_shapes,
            observed_class_modules=base_class_modules,
            labeled_loss_hex="",
            invariants=invariants,
            errors=[str(error)],
        )
    finally:
        if model is not None:
            del model


def _resolve_cli_paths(
    assets: Path, environment: Path, fixtures: Path, output: Path
) -> tuple[Path, Path, Path, Path]:
    root = _artifact_root()
    wave_root = _required_child_directory(root, "wave0")
    receipts_root = _required_child_directory(wave_root, "receipts")
    expected_assets = receipts_root / "model-assets.json"
    actual_assets = Path(assets).resolve(strict=True)
    if actual_assets != expected_assets or _is_link_or_junction(Path(assets)):
        raise ModelContractInputError(
            "assets must be VAL_ARTIFACT_ROOT/wave0/receipts/model-assets.json"
        )
    actual_environment = Path(environment).resolve(strict=True)
    if actual_environment.parent != receipts_root or _is_link_or_junction(
        Path(environment)
    ):
        raise ModelContractInputError(
            "environment must be a non-link receipt directly below "
            "VAL_ARTIFACT_ROOT/wave0/receipts"
        )
    expected_fixtures = (
        _project_root() / "fixtures" / "synthetic" / "wave0" / "fixture-manifest.json"
    ).resolve(strict=True)
    actual_fixtures = Path(fixtures).resolve(strict=True)
    if actual_fixtures != expected_fixtures or _is_link_or_junction(Path(fixtures)):
        raise ModelContractInputError("fixtures must be the tracked Wave 0 manifest")
    actual_output = Path(output).resolve(strict=False)
    if actual_output.parent != receipts_root or _is_link_or_junction(Path(output)):
        raise ModelContractInputError(
            "output must be directly below VAL_ARTIFACT_ROOT/wave0/receipts"
        )
    return actual_assets, actual_environment, actual_fixtures, actual_output


@command("probe model-contract")
def main(argv: Sequence[str] | None = None) -> int:
    """Run the canonical, offline, label-free RT-DETR contract probe."""
    parser = argparse.ArgumentParser(prog="val probe model-contract")
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--environment", type=Path, required=True)
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    try:
        if not arguments.run_id.strip():
            raise ModelContractInputError("run_id must be non-empty")
        assets_path, environment_path, fixtures_path, output_path = _resolve_cli_paths(
            arguments.assets,
            arguments.environment,
            arguments.fixtures,
            arguments.output,
        )
        if output_path.exists():
            raise ModelContractInputError(
                "fresh output path is required for each model-contract attempt"
            )
        asset_receipt = _mapping(
            json.loads(assets_path.read_text(encoding="utf-8")), "asset receipt"
        )
        environment_receipt = _mapping(
            json.loads(environment_path.read_text(encoding="utf-8")),
            "environment receipt",
        )
        spec = load_pinned_asset_specs(
            _project_root() / "configs" / "models" / "pinned-models.yaml"
        )["rtdetr"]
        receipt = run_model_contract_probe(
            spec,
            asset_receipt,
            fixtures_path,
            environment_receipt,
            sha256_file(environment_path),
            arguments.run_id,
        )
        atomic_write_receipt(output_path, receipt.as_dict())
    except (ModelContractInputError, OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 2
    print(receipt.status)
    return 0 if receipt.status == "PASS" else 2
