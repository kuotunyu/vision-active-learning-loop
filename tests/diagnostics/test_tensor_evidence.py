"""Tests for canonical A7 tensor observations and snapshot storage."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from itertools import pairwise
from pathlib import Path

import pytest
import torch

from vision_active_learning_loop.artifacts.no_clobber import NoClobberError
from vision_active_learning_loop.diagnostics.tensor_evidence import (
    SNAPSHOT_MAGIC,
    TensorEvidenceError,
    atomic_write_snapshot,
    canonical_tensor_bytes,
    compare_tensors,
    decode_snapshot,
    encode_snapshot,
    observe_tensor,
)

_OPERATION_IDS = tuple(f"decoder.layers.{index}.encoder_attn" for index in range(9))
_ROLES = ("forward_value", "forward_grid", "incoming_result_gradient")
_NAMES = tuple(
    f"{operation_id}.{role}" for operation_id in _OPERATION_IDS for role in _ROLES
)


def _snapshot_tensors() -> dict[str, torch.Tensor]:
    return {
        name: torch.tensor([float(index), float(index + 1)], dtype=torch.float32)
        for index, name in enumerate(reversed(_NAMES))
    }


def _split_snapshot(encoded: bytes) -> tuple[dict[str, object], bytes]:
    assert encoded.startswith(SNAPSHOT_MAGIC)
    header_size = struct.unpack_from("<Q", encoded, len(SNAPSHOT_MAGIC))[0]
    header_start = len(SNAPSHOT_MAGIC) + 8
    header_end = header_start + header_size
    return json.loads(encoded[header_start:header_end]), encoded[header_end:]


def _rebuild_snapshot(header: dict[str, object], payload: bytes) -> bytes:
    encoded_header = json.dumps(
        header,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return (
        SNAPSHOT_MAGIC
        + struct.pack("<Q", len(encoded_header))
        + encoded_header
        + payload
    )


@pytest.mark.parametrize(
    ("dtype", "expected_name", "expected_bytes"),
    [
        (torch.bfloat16, "bfloat16", struct.pack("<HHH", 0x3F80, 0xC000, 0x3F00)),
        (torch.float16, "float16", struct.pack("<eee", 1.0, -2.0, 0.5)),
        (torch.float32, "float32", struct.pack("<fff", 1.0, -2.0, 0.5)),
        (torch.float64, "float64", struct.pack("<ddd", 1.0, -2.0, 0.5)),
    ],
)
def test_canonical_tensor_bytes_are_little_endian_contiguous_and_dtype_bound(
    monkeypatch: pytest.MonkeyPatch,
    dtype: torch.dtype,
    expected_name: str,
    expected_bytes: bytes,
) -> None:
    tensor = torch.tensor([[1.0, 99.0], [-2.0, 99.0], [0.5, 99.0]], dtype=dtype)[:, 0]

    dtype_name, shape, payload = canonical_tensor_bytes(tensor)

    assert (dtype_name, shape, payload) == (expected_name, (3,), expected_bytes)
    monkeypatch.setattr(sys, "byteorder", "big")
    with pytest.raises(TensorEvidenceError, match="little-endian"):
        canonical_tensor_bytes(tensor)


def test_observe_tensor_records_exact_counts_digest_and_float64_norm() -> None:
    tensor = torch.tensor([3.0, 4.0], dtype=torch.float16)

    evidence = observe_tensor("result", "forward_value", tensor, operation_id="op-0")

    assert evidence.name == "result"
    assert evidence.role == "forward_value"
    assert evidence.operation_id == "op-0"
    assert evidence.shape == (2,)
    assert evidence.dtype == "float16"
    assert evidence.element_count == 2
    assert evidence.finite_count == 2
    assert evidence.non_finite_count == 0
    assert evidence.sha256 == hashlib.sha256(struct.pack("<ee", 3.0, 4.0)).hexdigest()
    assert evidence.l2_norm == 5.0


def test_canonical_tensor_bytes_reject_sparse_quantized_meta_empty_unsupported_and_nonfinite() -> None:
    cases = [
        torch.tensor([1.0]).to_sparse(),
        torch.quantize_per_tensor(
            torch.tensor([1.0]), scale=0.1, zero_point=0, dtype=torch.qint8
        ),
        torch.empty(1, device="meta"),
        torch.empty(0, dtype=torch.float32),
        torch.tensor([1], dtype=torch.int32),
        torch.tensor([float("nan")], dtype=torch.float32),
        torch.tensor([float("inf")], dtype=torch.float32),
    ]

    for tensor in cases:
        with pytest.raises(TensorEvidenceError):
            canonical_tensor_bytes(tensor)


def test_observe_tensor_does_not_alias_or_modify_the_input() -> None:
    tensor = torch.tensor([1.0, 2.0], dtype=torch.float32, requires_grad=True)
    before = tensor.detach().clone()

    evidence = observe_tensor("x", "forward_grid", tensor, operation_id="op")
    tensor.detach()[0] = 9.0

    assert torch.equal(before, torch.tensor([1.0, 2.0]))
    assert evidence.sha256 == hashlib.sha256(struct.pack("<ff", 1.0, 2.0)).hexdigest()


@pytest.mark.parametrize(
    ("left", "right", "difference", "relative", "cosine", "exact"),
    [
        ([1.0, 2.0], [1.0, 2.0], 0.0, 0.0, 1.0, True),
        ([3.0, 4.0], [0.0, 4.0], 3.0, 0.6, 0.8, False),
        ([0.0, 0.0], [0.0, 0.0], 0.0, 0.0, 1.0, True),
        ([0.0, 0.0], [1.0, 0.0], 1.0, 1.0, 0.0, False),
    ],
)
def test_compare_tensors_registers_exact_formulas(
    left: list[float],
    right: list[float],
    difference: float,
    relative: float,
    cosine: float,
    exact: bool,
) -> None:
    comparison = compare_tensors(
        "primary",
        "clean-a",
        "captured",
        torch.tensor(left, dtype=torch.float32),
        torch.tensor(right, dtype=torch.float32),
    )

    assert comparison.left_replica == "primary"
    assert comparison.right_replica == "clean-a"
    assert comparison.name == "captured"
    assert comparison.exact_digest_equal is exact
    assert comparison.difference_l2 == pytest.approx(difference)
    assert comparison.relative_l2 == pytest.approx(relative)
    assert comparison.cosine == pytest.approx(cosine)


@pytest.mark.parametrize(
    ("left", "right"),
    [
        (torch.ones(1), torch.ones(2)),
        (torch.ones(1, dtype=torch.float16), torch.ones(1, dtype=torch.float32)),
        (torch.tensor([float("nan")]), torch.ones(1)),
    ],
)
def test_compare_tensors_rejects_incompatible_or_nonfinite_inputs(
    left: torch.Tensor, right: torch.Tensor
) -> None:
    with pytest.raises(TensorEvidenceError):
        compare_tensors("a", "b", "x", left, right)


def test_compare_tensors_clamps_roundoff_to_the_closed_cosine_range() -> None:
    left = torch.tensor([0.42502921342344874, -2.347860196470522], dtype=torch.float64)
    right = torch.tensor([0.42502921342344896, -2.347860196470522], dtype=torch.float64)

    comparison = compare_tensors("a", "b", "x", left, right)

    assert comparison.exact_digest_equal is False
    assert -1.0 <= comparison.cosine <= 1.0


def test_snapshot_encoding_is_deterministic_sorted_and_self_describing() -> None:
    tensors = _snapshot_tensors()

    encoded = encode_snapshot(tensors)
    encoded_reordered = encode_snapshot(dict(reversed(tuple(tensors.items()))))
    header, payload = _split_snapshot(encoded)

    assert encoded == encoded_reordered
    assert header["byte_order"] == "little"
    assert header["version"] == 1
    entries = header["tensors"]
    assert isinstance(entries, list)
    assert [entry["name"] for entry in entries] == sorted(_NAMES)
    assert entries[0]["offset"] == 0
    for previous, current in pairwise(entries):
        assert current["offset"] == previous["offset"] + previous["size"]
    assert entries[-1]["offset"] + entries[-1]["size"] == len(payload)
    for entry in entries:
        chunk = payload[entry["offset"] : entry["offset"] + entry["size"]]
        assert hashlib.sha256(chunk).hexdigest() == entry["sha256"]
        assert entry["element_count"] == 2
        assert entry["dtype"] == "float32"
        assert entry["shape"] == [2]


def test_snapshot_round_trip_requires_exact_27_name_inventory(tmp_path: Path) -> None:
    tensors = _snapshot_tensors()
    path = tmp_path / "snapshot.bin"
    path.write_bytes(encode_snapshot(tensors))

    decoded = decode_snapshot(path, expected_names=_NAMES)

    assert list(decoded) == sorted(_NAMES)
    for name in _NAMES:
        assert torch.equal(decoded[name], tensors[name])
        assert decoded[name].data_ptr() != tensors[name].data_ptr()


@pytest.mark.parametrize("mutation", ["missing", "extra", "renamed", "duplicate"])
def test_snapshot_decode_rejects_name_inventory_drift(
    tmp_path: Path, mutation: str
) -> None:
    header, payload = _split_snapshot(encode_snapshot(_snapshot_tensors()))
    entries = header["tensors"]
    assert isinstance(entries, list)
    if mutation == "missing":
        entries.pop()
    elif mutation == "extra":
        entries.append({**entries[-1], "name": "unexpected"})
    elif mutation == "renamed":
        entries[-1]["name"] = "renamed"
    else:
        entries[-1]["name"] = entries[0]["name"]
    path = tmp_path / f"{mutation}.bin"
    path.write_bytes(_rebuild_snapshot(header, payload))

    with pytest.raises(TensorEvidenceError):
        decode_snapshot(path, expected_names=_NAMES)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("dtype", "float128"),
        ("shape", [3]),
        ("element_count", 3),
        ("offset", 1),
        ("size", 999),
        ("sha256", "0" * 64),
    ],
)
def test_snapshot_decode_rejects_corrupt_tensor_header(
    tmp_path: Path, field: str, value: object
) -> None:
    header, payload = _split_snapshot(encode_snapshot(_snapshot_tensors()))
    header["tensors"][0][field] = value
    path = tmp_path / f"wrong-{field}.bin"
    path.write_bytes(_rebuild_snapshot(header, payload))

    with pytest.raises(TensorEvidenceError):
        decode_snapshot(path, expected_names=_NAMES)


@pytest.mark.parametrize(
    "mutation", ["endian", "truncated", "trailing", "utf8", "json"]
)
def test_snapshot_decode_rejects_container_corruption(
    tmp_path: Path, mutation: str
) -> None:
    encoded = encode_snapshot(_snapshot_tensors())
    if mutation == "endian":
        header, payload = _split_snapshot(encoded)
        header["byte_order"] = "big"
        encoded = _rebuild_snapshot(header, payload)
    elif mutation == "truncated":
        encoded = encoded[:-1]
    elif mutation == "trailing":
        encoded += b"x"
    elif mutation == "utf8":
        encoded = SNAPSHOT_MAGIC + struct.pack("<Q", 1) + b"\xff"
    else:
        encoded = SNAPSHOT_MAGIC + struct.pack("<Q", 1) + b"{"
    path = tmp_path / f"{mutation}.bin"
    path.write_bytes(encoded)

    with pytest.raises(TensorEvidenceError):
        decode_snapshot(path, expected_names=_NAMES)


def test_snapshot_decode_rejects_nonregular_and_symlink_paths(tmp_path: Path) -> None:
    with pytest.raises(TensorEvidenceError, match="regular"):
        decode_snapshot(tmp_path, expected_names=_NAMES)

    target = tmp_path / "target.bin"
    target.write_bytes(encode_snapshot(_snapshot_tensors()))
    link = tmp_path / "link.bin"
    try:
        link.symlink_to(target)
    except OSError as error:
        pytest.skip(f"file symlink unavailable: {error}")
    with pytest.raises(TensorEvidenceError, match="link|junction"):
        decode_snapshot(link, expected_names=_NAMES)


@pytest.mark.skipif(os.name != "nt", reason="Windows junction case")
def test_snapshot_decode_rejects_junction_parent(tmp_path: Path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    target = real / "snapshot.bin"
    target.write_bytes(encode_snapshot(_snapshot_tensors()))
    junction = tmp_path / "junction"
    completed = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(junction), str(real)],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode:
        pytest.skip(f"junction unavailable: {completed.stderr}")
    with pytest.raises(TensorEvidenceError, match="link|junction|parent"):
        decode_snapshot(junction / "snapshot.bin", expected_names=_NAMES)


def test_atomic_snapshot_publication_is_no_clobber_and_requires_parent(
    tmp_path: Path,
) -> None:
    tensors = _snapshot_tensors()
    output = tmp_path / "snapshot.bin"
    expected = hashlib.sha256(encode_snapshot(tensors)).hexdigest()

    assert atomic_write_snapshot(output, tensors) == expected
    assert output.is_file()
    with pytest.raises(NoClobberError):
        atomic_write_snapshot(output, tensors)
    with pytest.raises(OSError, match="parent|directory|unavailable"):
        atomic_write_snapshot(tmp_path / "missing" / "snapshot.bin", tensors)


def test_atomic_snapshot_publication_race_has_exactly_one_winner(
    tmp_path: Path,
) -> None:
    output = tmp_path / "snapshot.bin"
    tensors = _snapshot_tensors()

    def publish() -> str:
        try:
            return atomic_write_snapshot(output, tensors)
        except NoClobberError:
            return "exists"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: publish(), range(2)))

    assert sum(result != "exists" for result in results) == 1
    assert sum(result == "exists" for result in results) == 1
    assert decode_snapshot(output, expected_names=_NAMES)
