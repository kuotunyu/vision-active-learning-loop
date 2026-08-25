"""Canonical tensor observations and immutable A7 snapshot storage."""

from __future__ import annotations

import errno
import hashlib
import json
import math
import os
import struct
import sys
from collections.abc import Collection, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch

from ..artifacts.no_clobber import (
    open_unique_staging_file,
    publish_staged_file_no_clobber,
)

SNAPSHOT_MAGIC = b"VALA7T1\n"
_HEADER_PREFIX_SIZE = len(SNAPSHOT_MAGIC) + 8
_DTYPES = {
    torch.bfloat16: ("bfloat16", torch.uint16),
    torch.float16: ("float16", torch.float16),
    torch.float32: ("float32", torch.float32),
    torch.float64: ("float64", torch.float64),
}
_DTYPES_BY_NAME = {name: dtype for dtype, (name, _) in _DTYPES.items()}
_DTYPE_SIZES = {
    name: torch.empty((), dtype=dtype).element_size()
    for name, dtype in _DTYPES_BY_NAME.items()
}
_ENTRY_KEYS = {
    "dtype",
    "element_count",
    "name",
    "offset",
    "sha256",
    "shape",
    "size",
}


class TensorEvidenceError(ValueError):
    """Raised when tensor evidence is unsafe, unsupported, or inconsistent."""


@dataclass(frozen=True)
class TensorEvidence:
    """One immutable observation of a named tensor."""

    name: str
    role: str
    operation_id: str
    shape: tuple[int, ...]
    dtype: str
    element_count: int
    finite_count: int
    non_finite_count: int
    sha256: str
    l2_norm: float


@dataclass(frozen=True)
class TensorComparison:
    """Registered pairwise metrics for two replica tensors."""

    left_replica: str
    right_replica: str
    name: str
    exact_digest_equal: bool
    difference_l2: float
    relative_l2: float
    cosine: float


def canonical_tensor_bytes(
    tensor: torch.Tensor,
) -> tuple[str, tuple[int, ...], bytes]:
    """Return fail-closed little-endian bytes without changing tensor precision."""
    if sys.byteorder != "little":
        raise TensorEvidenceError("canonical tensor bytes require a little-endian host")
    if not isinstance(tensor, torch.Tensor):
        raise TensorEvidenceError("tensor evidence requires a torch.Tensor")
    if tensor.device.type == "meta":
        raise TensorEvidenceError("meta tensors are forbidden")
    if tensor.is_quantized:
        raise TensorEvidenceError("quantized tensors are forbidden")
    if tensor.layout != torch.strided:
        raise TensorEvidenceError("sparse or non-strided tensors are forbidden")
    dtype_definition = _DTYPES.get(tensor.dtype)
    if dtype_definition is None:
        raise TensorEvidenceError(f"unsupported tensor dtype: {tensor.dtype}")
    if tensor.numel() == 0:
        raise TensorEvidenceError("empty tensors are forbidden")

    detached = tensor.detach().to(device="cpu").contiguous()
    if not bool(torch.isfinite(detached).all().item()):
        raise TensorEvidenceError("non-finite tensors are forbidden")
    dtype_name, byte_view_dtype = dtype_definition
    byte_view = (
        detached.view(byte_view_dtype) if tensor.dtype == torch.bfloat16 else detached
    )
    payload = byte_view.numpy().tobytes(order="C")
    expected_size = detached.numel() * detached.element_size()
    if len(payload) != expected_size:
        raise TensorEvidenceError("canonical tensor byte count is inconsistent")
    return dtype_name, tuple(int(size) for size in detached.shape), payload


def observe_tensor(
    name: str,
    role: str,
    tensor: torch.Tensor,
    *,
    operation_id: str,
) -> TensorEvidence:
    """Observe one tensor with exact-byte identity and a float64 norm."""
    _require_nonempty_string(name, "name")
    _require_nonempty_string(role, "role")
    _require_nonempty_string(operation_id, "operation_id")
    dtype_name, shape, payload = canonical_tensor_bytes(tensor)
    detached64 = tensor.detach().to(device="cpu", dtype=torch.float64).contiguous()
    norm = float(torch.linalg.vector_norm(detached64).item())
    if not math.isfinite(norm):
        raise TensorEvidenceError("tensor norm must be finite")
    element_count = tensor.numel()
    return TensorEvidence(
        name=name,
        role=role,
        operation_id=operation_id,
        shape=shape,
        dtype=dtype_name,
        element_count=element_count,
        finite_count=element_count,
        non_finite_count=0,
        sha256=hashlib.sha256(payload).hexdigest(),
        l2_norm=norm,
    )


def compare_tensors(
    left_replica: str,
    right_replica: str,
    name: str,
    left: torch.Tensor,
    right: torch.Tensor,
) -> TensorComparison:
    """Compare equal-shape, equal-dtype tensors using registered formulas."""
    _require_nonempty_string(left_replica, "left_replica")
    _require_nonempty_string(right_replica, "right_replica")
    _require_nonempty_string(name, "name")
    left_dtype, left_shape, left_bytes = canonical_tensor_bytes(left)
    right_dtype, right_shape, right_bytes = canonical_tensor_bytes(right)
    if left_dtype != right_dtype or left_shape != right_shape:
        raise TensorEvidenceError("tensor comparisons require equal dtype and shape")

    left64 = left.detach().to(device="cpu", dtype=torch.float64).contiguous().view(-1)
    right64 = right.detach().to(device="cpu", dtype=torch.float64).contiguous().view(-1)
    left_norm = float(torch.linalg.vector_norm(left64).item())
    right_norm = float(torch.linalg.vector_norm(right64).item())
    difference_l2 = float(torch.linalg.vector_norm(left64 - right64).item())
    denominator = max(left_norm, right_norm)
    relative_l2 = 0.0 if denominator == 0.0 else difference_l2 / denominator
    if left_norm == 0.0 and right_norm == 0.0:
        cosine = 1.0
    elif left_norm == 0.0 or right_norm == 0.0:
        cosine = 0.0
    else:
        cosine = float(torch.dot(left64, right64).item()) / (left_norm * right_norm)
    metrics = (difference_l2, relative_l2, cosine)
    if not all(math.isfinite(value) for value in metrics):
        raise TensorEvidenceError("tensor comparison metrics must be finite")
    return TensorComparison(
        left_replica=left_replica,
        right_replica=right_replica,
        name=name,
        exact_digest_equal=(
            hashlib.sha256(left_bytes).digest() == hashlib.sha256(right_bytes).digest()
        ),
        difference_l2=difference_l2,
        relative_l2=relative_l2,
        cosine=cosine,
    )


def encode_snapshot(tensors: Mapping[str, torch.Tensor]) -> bytes:
    """Encode a deterministic, closed tensor snapshot."""
    if not isinstance(tensors, Mapping) or not tensors:
        raise TensorEvidenceError("snapshot tensors must be a non-empty mapping")
    entries: list[dict[str, object]] = []
    chunks: list[bytes] = []
    offset = 0
    for name in sorted(tensors):
        _require_nonempty_string(name, "snapshot tensor name")
        dtype_name, shape, payload = canonical_tensor_bytes(tensors[name])
        entries.append(
            {
                "dtype": dtype_name,
                "element_count": tensors[name].numel(),
                "name": name,
                "offset": offset,
                "sha256": hashlib.sha256(payload).hexdigest(),
                "shape": list(shape),
                "size": len(payload),
            }
        )
        chunks.append(payload)
        offset += len(payload)
    header = {
        "byte_order": "little",
        "tensors": entries,
        "version": 1,
    }
    try:
        encoded_header = json.dumps(
            header,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as error:
        raise TensorEvidenceError("snapshot header cannot be encoded") from error
    return (
        SNAPSHOT_MAGIC
        + struct.pack("<Q", len(encoded_header))
        + encoded_header
        + b"".join(chunks)
    )


def decode_snapshot(
    path: Path,
    *,
    expected_names: Collection[str],
) -> dict[str, torch.Tensor]:
    """Decode and fully verify one regular, non-link snapshot file."""
    target = Path(path)
    _require_safe_regular_file(target)
    expected = _validated_expected_names(expected_names)
    try:
        encoded = target.read_bytes()
    except OSError as error:
        raise TensorEvidenceError("snapshot file cannot be read") from error
    if len(encoded) < _HEADER_PREFIX_SIZE or not encoded.startswith(SNAPSHOT_MAGIC):
        raise TensorEvidenceError("snapshot magic or header prefix is invalid")
    header_size = struct.unpack_from("<Q", encoded, len(SNAPSHOT_MAGIC))[0]
    header_end = _HEADER_PREFIX_SIZE + header_size
    if header_size == 0 or header_end > len(encoded):
        raise TensorEvidenceError("snapshot header length is invalid")
    try:
        header = json.loads(
            encoded[_HEADER_PREFIX_SIZE:header_end].decode("utf-8"),
            object_pairs_hook=_reject_duplicate_json_keys,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, TensorEvidenceError) as error:
        raise TensorEvidenceError("snapshot header is invalid UTF-8 JSON") from error
    if not isinstance(header, dict) or set(header) != {
        "byte_order",
        "tensors",
        "version",
    }:
        raise TensorEvidenceError("snapshot header fields are not exact")
    if header["version"] != 1 or header["byte_order"] != "little":
        raise TensorEvidenceError("snapshot version or byte order is invalid")
    raw_entries = header["tensors"]
    if not isinstance(raw_entries, list) or not raw_entries:
        raise TensorEvidenceError("snapshot tensor inventory must be non-empty")
    payload = encoded[header_end:]
    entries = _validated_entries(raw_entries, payload)
    names = [entry["name"] for entry in entries]
    if names != sorted(names) or set(names) != expected or len(names) != len(expected):
        raise TensorEvidenceError("snapshot tensor names do not match exact inventory")

    decoded: dict[str, torch.Tensor] = {}
    for entry in entries:
        name = entry["name"]
        offset = entry["offset"]
        size = entry["size"]
        chunk = payload[offset : offset + size]
        tensor = _tensor_from_bytes(entry["dtype"], entry["shape"], chunk)
        observation = observe_tensor(name, "snapshot", tensor, operation_id="snapshot")
        if (
            observation.dtype != entry["dtype"]
            or observation.shape != tuple(entry["shape"])
            or observation.element_count != entry["element_count"]
            or observation.sha256 != entry["sha256"]
        ):
            raise TensorEvidenceError("decoded tensor does not match its header")
        decoded[name] = tensor
    return decoded


def atomic_write_snapshot(path: Path, tensors: Mapping[str, torch.Tensor]) -> str:
    """Atomically publish one immutable snapshot and return its storage digest."""
    target = Path(path)
    encoded = encode_snapshot(tensors)
    expected_digest = hashlib.sha256(encoded).hexdigest()
    expected_names = tuple(tensors)
    staging = None
    try:
        staging = open_unique_staging_file(target)
        with staging.handle as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())
        staged_bytes = staging.path.read_bytes()
        if hashlib.sha256(staged_bytes).hexdigest() != expected_digest:
            raise TensorEvidenceError("staged snapshot bytes do not match input")
        decode_snapshot(staging.path, expected_names=expected_names)
        _fsync_parent(target.parent)
        publish_staged_file_no_clobber(staging.path, target)
        return expected_digest
    finally:
        if staging is not None:
            try:
                staging.path.unlink()
            except OSError:
                pass


def _validated_entries(
    raw_entries: list[object], payload: bytes
) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    expected_offset = 0
    seen: set[str] = set()
    for raw_entry in raw_entries:
        if not isinstance(raw_entry, dict) or set(raw_entry) != _ENTRY_KEYS:
            raise TensorEvidenceError("snapshot tensor header fields are not exact")
        entry = dict(raw_entry)
        name = entry["name"]
        _require_nonempty_string(name, "snapshot tensor name")
        if name in seen:
            raise TensorEvidenceError("duplicate snapshot tensor name")
        seen.add(name)
        dtype_name = entry["dtype"]
        if dtype_name not in _DTYPES_BY_NAME:
            raise TensorEvidenceError("snapshot tensor dtype is unsupported")
        shape = entry["shape"]
        if (
            not isinstance(shape, list)
            or not shape
            or any(type(size) is not int or size < 0 for size in shape)
        ):
            raise TensorEvidenceError("snapshot tensor shape is invalid")
        element_count = entry["element_count"]
        if type(element_count) is not int or element_count <= 0:
            raise TensorEvidenceError("snapshot tensor element count is invalid")
        if math.prod(shape) != element_count:
            raise TensorEvidenceError("snapshot tensor shape and count differ")
        offset = entry["offset"]
        size = entry["size"]
        if type(offset) is not int or offset != expected_offset:
            raise TensorEvidenceError("snapshot tensor offsets are not contiguous")
        if type(size) is not int or size != element_count * _DTYPE_SIZES[dtype_name]:
            raise TensorEvidenceError("snapshot tensor byte size is invalid")
        end = offset + size
        if end > len(payload):
            raise TensorEvidenceError("snapshot tensor exceeds payload bounds")
        digest = entry["sha256"]
        if (
            not isinstance(digest, str)
            or len(digest) != 64
            or any(character not in "0123456789abcdef" for character in digest)
            or hashlib.sha256(payload[offset:end]).hexdigest() != digest
        ):
            raise TensorEvidenceError("snapshot tensor digest is invalid")
        expected_offset = end
        entries.append(entry)
    if expected_offset != len(payload):
        raise TensorEvidenceError(
            "snapshot contains truncated or trailing payload bytes"
        )
    return entries


def _tensor_from_bytes(
    dtype_name: str, shape: list[int], payload: bytes
) -> torch.Tensor:
    storage = bytearray(payload)
    if dtype_name == "bfloat16":
        tensor = (
            torch.frombuffer(storage, dtype=torch.uint16).clone().view(torch.bfloat16)
        )
    else:
        tensor = torch.frombuffer(storage, dtype=_DTYPES_BY_NAME[dtype_name]).clone()
    return tensor.reshape(tuple(shape))


def _validated_expected_names(expected_names: Collection[str]) -> set[str]:
    if isinstance(expected_names, (str, bytes)):
        raise TensorEvidenceError("expected tensor names must be a collection of names")
    names = list(expected_names)
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise TensorEvidenceError("expected tensor names must be non-empty strings")
    if len(names) != len(set(names)):
        raise TensorEvidenceError("expected tensor names must be unique")
    return set(names)


def _reject_duplicate_json_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    document: dict[str, object] = {}
    for key, value in pairs:
        if key in document:
            raise TensorEvidenceError(f"duplicate JSON field: {key}")
        document[key] = value
    return document


def _require_safe_regular_file(path: Path) -> None:
    if not path.is_file():
        raise TensorEvidenceError("snapshot path must be a regular file")
    for candidate in (path, *path.parents):
        if _is_link_or_junction(candidate):
            raise TensorEvidenceError("snapshot path link or junction is forbidden")


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and bool(is_junction()))


def _require_nonempty_string(value: object, field: str) -> None:
    if not isinstance(value, str) or not value:
        raise TensorEvidenceError(f"{field} must be a non-empty string")


def _fsync_parent(directory: Path) -> None:
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except OSError as error:
        if (
            os.name == "nt"
            and type(error) is PermissionError
            and error.errno == errno.EACCES
        ):
            return
        raise
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
