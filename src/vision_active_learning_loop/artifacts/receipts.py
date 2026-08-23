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
    value: object, schema: Mapping[str, object], location: str = "$"
) -> None:
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
                _validate_schema(member, member_schema, f"{location}.{name}")
            elif additional is False:
                raise ReceiptValidationError(f"{location}.{name} is not permitted")
            elif isinstance(additional, Mapping):
                _validate_schema(member, additional, f"{location}.{name}")
    elif schema_type == "array":
        if not isinstance(value, list):
            raise ReceiptValidationError(f"{location} must be an array")
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ReceiptValidationError(f"{location} has too few items")
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, member in enumerate(value):
                _validate_schema(member, items, f"{location}[{index}]")
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
