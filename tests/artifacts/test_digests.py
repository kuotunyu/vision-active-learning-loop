from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from vision_active_learning_loop.artifacts.digests import (
    canonical_json_sha256,
    sha256_file,
)


def test_canonical_json_hash_ignores_mapping_insertion_order() -> None:
    assert canonical_json_sha256({"b": 2, "a": 1}) == canonical_json_sha256(
        {"a": 1, "b": 2}
    )


def test_canonical_json_hash_matches_utf8_compact_sorted_golden_vector() -> None:
    assert canonical_json_sha256({"b": 2, "a": 1}) == (
        "43258cff783fe7036d8a43033f830adfc60ec037382473548ac742b888292777"
    )


def test_canonical_json_hash_rejects_non_finite_values() -> None:
    with pytest.raises(ValueError):
        canonical_json_sha256({"value": float("nan")})


def test_sha256_file_hashes_exact_file_bytes(tmp_path: Path) -> None:
    payload = tmp_path / "payload.bin"
    payload.write_bytes(b"receipt\x00bytes\n")

    assert sha256_file(payload) == hashlib.sha256(b"receipt\x00bytes\n").hexdigest()
