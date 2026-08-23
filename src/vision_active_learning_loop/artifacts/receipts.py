"""Schema-validated, content-addressed receipt publication."""

from __future__ import annotations

import copy
import errno
import json
import math
import os
import re
from collections.abc import Mapping
from pathlib import Path

from .digests import canonical_json_sha256


class ReceiptValidationError(ValueError):
    """Raised when a receipt is not an approved, internally consistent record."""


_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"
_ALLOWED_SCHEMAS = {
    ("model-contract", 1): _SCHEMA_ROOT / "model-contract-receipt.schema.json",
    ("feasibility", 1): _SCHEMA_ROOT / "feasibility-receipt.schema.json",
    ("model-assets", 1): _SCHEMA_ROOT / "model-asset-receipt.schema.json",
}
_APPROVED_MODEL_CONTRACT_ASSET_HASHES = {
    "model_sha256": "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
    "config_file_sha256": "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2",
    "processor_file_sha256": "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a",
    "fixture_sha256": "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f",
    "probe_sha256": "640d7aceb71aa67db5d16709e1cc0db8de78735407ca47c0b1ed43dd0624cec4",
}
_APPROVED_RTDETR_SOURCE_FILES = {
    "models/rt_detr/configuration_rt_detr.py": {
        "size": 9028,
        "sha256": "22c1b65c1385d35534658cbf1e91afa7174737134cb6a14ffdaffcd7b7a161a6",
    },
    "models/rt_detr/configuration_rt_detr_resnet.py": {
        "size": 3538,
        "sha256": "52a9a3ca8dd648f04bcb5f61b30ab927ca3f15187748736f7714f48af1f1ae73",
    },
    "models/rt_detr/image_processing_rt_detr.py": {
        "size": 24476,
        "sha256": "47ae2f0ca25a2763f4f42b27e8a2760bcbb0c2ef07d0f1e97aa779f9219fc558",
    },
    "models/rt_detr/modeling_rt_detr.py": {
        "size": 86564,
        "sha256": "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3",
    },
    "models/rt_detr/modeling_rt_detr_resnet.py": {
        "size": 15986,
        "sha256": "fc13ccc6ba1e57862e4c129c9e74bb97f091012186c1104974b92d5ec7b4019c",
    },
}
def validate_receipt(receipt: Mapping[str, object], schema_path: Path) -> None:
    """Validate a stored receipt against its allowlisted receipt type and schema."""
    _validate_receipt(receipt, schema_path=schema_path, require_content_hash=True)


def normative_receipt_sha256(receipt: Mapping[str, object]) -> str:
    """Return the digest used to compare deterministic receipt observations."""
    _validate_receipt(receipt, schema_path=None, require_content_hash=False)
    normative = receipt["normative"]
    if not isinstance(normative, Mapping):  # Guarded above; retained for type safety.
        raise ReceiptValidationError("normative must be an object")
    return canonical_json_sha256(dict(normative))


def atomic_write_receipt(path: Path, receipt: Mapping[str, object]) -> str:
    """Validate and atomically publish one canonical receipt, returning its digest."""
    target = Path(path)
    partial = target.with_name(f"{target.name}.partial")
    try:
        document = copy.deepcopy(dict(receipt))
        expected_schema = _expected_schema_path(document)
        _validate_receipt(
            document, schema_path=expected_schema, require_content_hash=False
        )
        metadata = document["metadata"]
        if not isinstance(metadata, dict):
            raise ReceiptValidationError("metadata must be an object")
        actual = metadata.get("receipt_content_sha256")
        digest = _receipt_content_sha256(document)
        if actual is not None and actual != digest:
            raise ReceiptValidationError("receipt content hash mismatch")
        metadata["receipt_content_sha256"] = digest
        _validate_receipt(
            document, schema_path=expected_schema, require_content_hash=True
        )

        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = _canonical_storage_bytes(document)
        _unlink_if_present(partial)
        with partial.open("xb") as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        _fsync_parent(target.parent)
        os.replace(partial, target)
        return digest
    except Exception:
        _unlink_if_present(partial)
        raise


def _validate_receipt(
    receipt: Mapping[str, object], *, schema_path: Path | None, require_content_hash: bool
) -> None:
    if not isinstance(receipt, Mapping):
        raise ReceiptValidationError("receipt must be an object")
    _reject_non_finite(receipt)
    expected_schema = _expected_schema_path(receipt)
    if (
        schema_path is not None
        and Path(schema_path).resolve() != expected_schema.resolve()
    ):
        raise ReceiptValidationError("schema path is not allowlisted for receipt type")
    schema = _load_schema(expected_schema)
    _validate_schema(receipt, schema)

    normative = receipt.get("normative")
    if not isinstance(normative, Mapping):
        raise ReceiptValidationError("normative must be an object")
    if receipt.get("receipt_type") == "model-contract":
        _validate_model_contract_consistency(normative)
    invariants = normative.get("invariants")
    if not isinstance(invariants, Mapping):
        raise ReceiptValidationError("invariants must be an object")
    status = normative.get("status")
    errors = normative.get("errors")
    if status == "PASS":
        if errors != []:
            raise ReceiptValidationError("PASS receipt requires empty errors")
        if not invariants or any(value is not True for value in invariants.values()):
            raise ReceiptValidationError("PASS receipt requires every invariant true")

    if require_content_hash:
        metadata = receipt.get("metadata")
        if not isinstance(metadata, Mapping):
            raise ReceiptValidationError("metadata must be an object")
        actual = metadata.get("receipt_content_sha256")
        if not isinstance(actual, str):
            raise ReceiptValidationError("receipt content hash is required")
        if actual != _receipt_content_sha256(receipt):
            raise ReceiptValidationError("receipt content hash mismatch")


def _validate_model_contract_consistency(normative: Mapping[str, object]) -> None:
    """Reject embedded model-contract evidence that contradicts its digests/proofs."""
    digest_documents = {
        "config_sha256": "config",
        "processor_sha256": "processor",
        "source_sha256": "source_files",
        "environment_sha256": "environment",
    }
    for digest_name, document_name in digest_documents.items():
        document = normative.get(document_name)
        if not isinstance(document, Mapping):
            raise ReceiptValidationError(f"{document_name} must be an object")
        expected = canonical_json_sha256(dict(document))
        if normative.get(digest_name) != expected:
            raise ReceiptValidationError(
                f"{digest_name} does not match embedded {document_name}"
            )
    for digest_name, expected in _APPROVED_MODEL_CONTRACT_ASSET_HASHES.items():
        if normative.get(digest_name) != expected:
            raise ReceiptValidationError(
                f"{digest_name} does not match the compiled approved pin"
            )
    if normative.get("source_files") != _APPROVED_RTDETR_SOURCE_FILES:
        raise ReceiptValidationError(
            "source_files do not match the compiled approved source observations"
        )

    config = normative.get("config")
    shapes = normative.get("observed_shapes")
    processor = normative.get("processor")
    environment = normative.get("environment")
    invariants = normative.get("invariants")
    if not all(
        isinstance(value, Mapping)
        for value in (config, shapes, processor, environment, invariants)
    ):
        raise ReceiptValidationError("model-contract evidence must be objects")
    assert isinstance(config, Mapping)
    assert isinstance(shapes, Mapping)
    assert isinstance(processor, Mapping)
    assert isinstance(environment, Mapping)
    assert isinstance(invariants, Mapping)

    decoder_layers = config.get("decoder_layers")
    canonical_environment = {
        "schema_version": 1,
        "python": "3.12.11",
        "torch": "2.12.0+cu126",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "pycocotools": "2.0.10",
        "cuda_runtime": "12.6",
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "os": "Linux",
        "wsl": True,
        "container_image_digest": (
            "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
        ),
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
        "status": "PASS",
        "errors": [],
    }
    logits_shape = shapes.get("logits")
    expected_evidence: dict[str, bool] = {
        "config_decoder_layers_3": decoder_layers == 3,
        "config_num_queries_300": config.get("num_queries") == 300,
        "config_num_labels_4": config.get("num_labels") == 4,
        "decoder_layers_at_least_two": (
            type(decoder_layers) is int and decoder_layers >= 2
        ),
        "logits_shape": shapes.get("logits") == [2, 300, 4],
        "pred_boxes_shape": shapes.get("pred_boxes") == [2, 300, 4],
        "intermediate_reference_points_shape": shapes.get(
            "intermediate_reference_points"
        )
        == [2, decoder_layers, 300, 4],
        "native_fifth_logit_absent": (
            isinstance(logits_shape, list)
            and len(logits_shape) == 3
            and logits_shape[-1] == 4
        ),
        "pixel_values_shape": shapes.get("pixel_values") == [2, 3, 640, 640],
        "pixel_mask_shape": shapes.get("pixel_mask") == [2, 640, 640],
        "aspect_preserving_size": processor.get("size")
        == {"max_height": 640, "max_width": 640},
        "bilinear_resize": processor.get("resample") == 2,
        "padding_enabled": (
            processor.get("do_pad") is True
            and processor.get("pad_size") == {"height": 640, "width": 640}
        ),
        "rescale_one_over_255": (
            processor.get("do_rescale") is True
            and processor.get("rescale_factor") == 1 / 255
        ),
        "normalization_disabled": processor.get("do_normalize") is False,
        "canonical_environment": (
            all(
                environment.get(name) == expected
                for name, expected in canonical_environment.items()
            )
            and isinstance(environment.get("gpu_uuid"), str)
            and str(environment["gpu_uuid"]).startswith("GPU-")
            and isinstance(environment.get("driver"), str)
            and bool(environment.get("driver"))
            and _is_prefixed_sha256(environment.get("runtime_image_digest"))
        ),
    }
    torch_execution = environment.get("torch_execution")
    if isinstance(torch_execution, Mapping):
        selected_device = torch_execution.get("selected_device")
        selected_index = torch_execution.get("selected_index")
        device_count = torch_execution.get("device_count")
        selected_name = torch_execution.get("selected_name")
        torch_uuid = torch_execution.get("torch_selected_gpu_uuid")
        nvidia_name = torch_execution.get("nvidia_smi_gpu_name")
        nvidia_uuid = torch_execution.get("nvidia_smi_gpu_uuid")
        identity_matches = (
            type(selected_index) is int
            and type(device_count) is int
            and 0 <= selected_index < device_count
            and selected_device == f"cuda:{selected_index}"
            and selected_name == environment.get("gpu_name")
            and selected_name == nvidia_name
            and _normalized_gpu_uuid(torch_uuid)
            == _normalized_gpu_uuid(environment.get("gpu_uuid"))
            == _normalized_gpu_uuid(nvidia_uuid)
            and _normalized_gpu_uuid(torch_uuid) is not None
        )
        expected_evidence.update(
            {
                "torch_cuda_available": (
                    torch_execution.get("cuda_available") is True
                    and type(torch_execution.get("device_count")) is int
                    and torch_execution["device_count"] > 0
                ),
                "torch_selected_gpu_is_canonical": identity_matches,
                "model_on_selected_cuda_device": (
                    selected_device is not None
                    and torch_execution.get("model_device") == selected_device
                ),
                "inputs_on_selected_cuda_device": (
                    selected_device is not None
                    and torch_execution.get("pixel_values_device") == selected_device
                    and torch_execution.get("pixel_mask_device") == selected_device
                ),
                "outputs_on_selected_cuda_device": (
                    selected_device is not None
                    and all(
                        torch_execution.get(name) == selected_device
                        for name in (
                            "logits_device",
                            "final_boxes_device",
                            "penultimate_boxes_device",
                            "intermediate_boxes_device",
                        )
                    )
                ),
            }
        )

    for invariant_name, evidence_passed in expected_evidence.items():
        if invariants.get(invariant_name) is True and evidence_passed is not True:
            raise ReceiptValidationError(
                f"{invariant_name} contradicts embedded model-contract evidence"
            )


def _normalized_gpu_uuid(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.removeprefix("GPU-").lower()
    if re.fullmatch(
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        normalized,
    ) is None:
        return None
    return normalized


def _is_prefixed_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def _expected_schema_path(receipt: Mapping[str, object]) -> Path:
    receipt_type = receipt.get("receipt_type")
    schema_version = receipt.get("schema_version")
    if not isinstance(receipt_type, str) or type(schema_version) is not int:
        raise ReceiptValidationError("unknown receipt type or schema version")
    key = (receipt_type, schema_version)
    if key not in _ALLOWED_SCHEMAS:
        raise ReceiptValidationError("unknown receipt type or schema version")
    return _ALLOWED_SCHEMAS[key]


def _load_schema(path: Path) -> Mapping[str, object]:
    try:
        schema = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReceiptValidationError(
            f"unable to load receipt schema: {path.name}"
        ) from error
    if not isinstance(schema, Mapping):
        raise ReceiptValidationError("receipt schema must be an object")
    return schema


def _validate_schema(
    value: object,
    schema: Mapping[str, object],
    location: str = "$",
    root_schema: Mapping[str, object] | None = None,
) -> None:
    if root_schema is None:
        root_schema = schema
    reference = schema.get("$ref")
    if isinstance(reference, str):
        resolved = _resolve_local_schema_reference(reference, root_schema)
        _validate_schema(value, resolved, location, root_schema)
        return
    condition = schema.get("if")
    if isinstance(condition, Mapping):
        try:
            _validate_schema(value, condition, location, root_schema)
        except ReceiptValidationError:
            selected = schema.get("else")
        else:
            selected = schema.get("then")
        if isinstance(selected, Mapping):
            _validate_schema(value, selected, location, root_schema)
    if "const" in schema and not _schema_values_equal(value, schema["const"]):
        raise ReceiptValidationError(f"{location} must equal {schema['const']!r}")
    enum = schema.get("enum")
    if isinstance(enum, list) and not any(
        _schema_values_equal(value, candidate) for candidate in enum
    ):
        raise ReceiptValidationError(f"{location} has an unsupported value")
    schema_type = schema.get("type")
    if schema_type == "object":
        if not isinstance(value, Mapping):
            raise ReceiptValidationError(f"{location} must be an object")
        required = schema.get("required", [])
        if isinstance(required, list):
            for name in required:
                if name not in value:
                    raise ReceiptValidationError(
                        f"{location} is missing required field {name}"
                    )
        minimum = schema.get("minProperties")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ReceiptValidationError(f"{location} has too few properties")
        properties = schema.get("properties", {})
        if not isinstance(properties, Mapping):
            raise ReceiptValidationError("schema properties must be an object")
        additional = schema.get("additionalProperties", True)
        for name, member in value.items():
            member_schema = properties.get(name)
            if isinstance(member_schema, Mapping):
                _validate_schema(
                    member, member_schema, f"{location}.{name}", root_schema
                )
            elif additional is False:
                raise ReceiptValidationError(f"{location}.{name} is not permitted")
            elif isinstance(additional, Mapping):
                _validate_schema(
                    member, additional, f"{location}.{name}", root_schema
                )
    elif schema_type == "array":
        if not isinstance(value, list):
            raise ReceiptValidationError(f"{location} must be an array")
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ReceiptValidationError(f"{location} has too few items")
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, member in enumerate(value):
                _validate_schema(
                    member, items, f"{location}[{index}]", root_schema
                )
    elif schema_type == "string":
        if not isinstance(value, str):
            raise ReceiptValidationError(f"{location} must be a string")
        pattern = schema.get("pattern")
        if isinstance(pattern, str) and re.fullmatch(pattern, value) is None:
            raise ReceiptValidationError(f"{location} has an invalid format")
    elif schema_type == "integer":
        if type(value) is not int:
            raise ReceiptValidationError(f"{location} must be an integer")
    elif schema_type == "number":
        if type(value) not in (int, float):
            raise ReceiptValidationError(f"{location} must be a number")
    elif schema_type == "boolean" and type(value) is not bool:
        raise ReceiptValidationError(f"{location} must be a boolean")


def _resolve_local_schema_reference(
    reference: str, root_schema: Mapping[str, object]
) -> Mapping[str, object]:
    if not reference.startswith("#/"):
        raise ReceiptValidationError("only local schema references are supported")
    current: object = root_schema
    for encoded_part in reference[2:].split("/"):
        part = encoded_part.replace("~1", "/").replace("~0", "~")
        if not isinstance(current, Mapping) or part not in current:
            raise ReceiptValidationError(f"unresolved schema reference: {reference}")
        current = current[part]
    if not isinstance(current, Mapping):
        raise ReceiptValidationError(f"schema reference is not an object: {reference}")
    return current


def _reject_non_finite(value: object, location: str = "$") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ReceiptValidationError(f"non-finite value at {location}")
    if isinstance(value, Mapping):
        for name, member in value.items():
            _reject_non_finite(member, f"{location}.{name}")
    elif isinstance(value, list):
        for index, member in enumerate(value):
            _reject_non_finite(member, f"{location}[{index}]")


def _schema_values_equal(value: object, expected: object) -> bool:
    """Compare schema constants without Python's bool-is-int coercion."""
    return type(value) is type(expected) and value == expected


def _receipt_content_sha256(receipt: Mapping[str, object]) -> str:
    preimage = copy.deepcopy(dict(receipt))
    metadata = preimage.get("metadata")
    if not isinstance(metadata, dict):
        raise ReceiptValidationError("metadata must be an object")
    metadata.pop("receipt_content_sha256", None)
    return canonical_json_sha256(preimage)


def _canonical_storage_bytes(receipt: Mapping[str, object]) -> bytes:
    return (
        json.dumps(
            receipt,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _unlink_if_present(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _fsync_parent(directory: Path) -> None:
    """Durably flush the directory entry where the platform permits it."""
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError as error:
        if _windows_directory_open_is_unsupported(error):
            return
        raise
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _windows_directory_open_is_unsupported(error: OSError) -> bool:
    """Recognize the Windows directory-open limitation before fsync can run."""
    return (
        os.name == "nt"
        and type(error) is PermissionError
        and error.errno == errno.EACCES
    )
