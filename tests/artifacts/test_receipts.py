from __future__ import annotations

import copy
import errno
import json
import os
from pathlib import Path

import pytest

import vision_active_learning_loop.artifacts.receipts as receipts
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    normative_receipt_sha256,
    validate_receipt,
)


HASH = "a" * 64


@pytest.fixture
def valid_receipt() -> dict[str, object]:
    return {
        "receipt_type": "model-contract",
        "schema_version": 1,
        "normative": {
            "model_sha256": HASH,
            "config_sha256": HASH,
            "source_sha256": HASH,
            "processor_sha256": HASH,
            "fixture_sha256": HASH,
            "probe_sha256": HASH,
            "environment_sha256": HASH,
            "observed_shapes": {"logits": [2, 300, 4]},
            "invariants": {"logits_shape": True, "four_class_head": True},
            "status": "PASS",
            "errors": [],
        },
        "metadata": {"timestamp": "2026-08-23T00:00:00Z", "run_id": "run-a"},
    }


def test_invalid_update_preserves_existing_valid_receipt(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    output = tmp_path / "receipt.json"
    atomic_write_receipt(output, valid_receipt)
    original = output.read_bytes()
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    invariants = normative["invariants"]
    assert isinstance(invariants, dict)
    del invariants["logits_shape"]

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(output, valid_receipt)

    assert output.read_bytes() == original
    assert not (tmp_path / "receipt.json.partial").exists()


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (lambda receipt: receipt["normative"]["invariants"].update({"logits_shape": False}), "PASS"),  # type: ignore[index,union-attr]
        (lambda receipt: receipt["normative"].update({"errors": ["bad"]}), "PASS"),  # type: ignore[index,union-attr]
        (lambda receipt: receipt["normative"].update({"status": "UNKNOWN"}), "status"),  # type: ignore[index,union-attr]
    ],
)
def test_invalid_pass_receipts_are_not_published(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    mutation: object,
    expected: str,
) -> None:
    assert callable(mutation)
    mutation(valid_receipt)
    output = tmp_path / "receipt.json"

    with pytest.raises(ReceiptValidationError, match=expected):
        atomic_write_receipt(output, valid_receipt)

    assert not output.exists()
    assert not (tmp_path / "receipt.json.partial").exists()


def test_atomic_write_stores_canonical_json_newline_and_content_hash(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    output = tmp_path / "receipt.json"

    digest = atomic_write_receipt(output, valid_receipt)

    raw = output.read_bytes()
    stored = json.loads(raw)
    assert raw.endswith(b"\n")
    assert raw[:-1] == json.dumps(
        stored, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")
    assert stored["metadata"]["receipt_content_sha256"] == digest
    validate_receipt(stored, _schema_path("model-contract-receipt.schema.json"))


def test_receipt_hash_mismatch_is_rejected_without_final_receipt(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    valid_receipt["metadata"] = {"receipt_content_sha256": "0" * 64}
    output = tmp_path / "receipt.json"

    with pytest.raises(ReceiptValidationError, match="content hash"):
        atomic_write_receipt(output, valid_receipt)

    assert not output.exists()


def test_rename_failure_preserves_existing_valid_receipt(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "receipt.json"
    atomic_write_receipt(output, valid_receipt)
    original = output.read_bytes()

    def fail_rename(source: Path, destination: Path) -> None:
        raise OSError("injected rename failure")

    monkeypatch.setattr(receipts.os, "replace", fail_rename)
    with pytest.raises(OSError, match="injected rename failure"):
        atomic_write_receipt(output, valid_receipt)

    assert output.read_bytes() == original
    assert not (tmp_path / "receipt.json.partial").exists()


def test_atomic_write_fsyncs_file_and_parent_before_replace(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    parent_descriptor = 999
    original_replace = receipts.os.replace

    def record_open(directory: Path, flags: int) -> int:
        assert directory == tmp_path
        assert flags == os.O_RDONLY
        events.append("parent-open")
        return parent_descriptor

    def record_fsync(descriptor: int) -> None:
        events.append("parent-fsync" if descriptor == parent_descriptor else "file-fsync")

    def record_close(descriptor: int) -> None:
        assert descriptor == parent_descriptor
        events.append("parent-close")

    def record_replace(source: Path, destination: Path) -> None:
        events.append("replace")
        original_replace(source, destination)

    monkeypatch.setattr(receipts.os, "open", record_open)
    monkeypatch.setattr(receipts.os, "fsync", record_fsync)
    monkeypatch.setattr(receipts.os, "close", record_close)
    monkeypatch.setattr(receipts.os, "replace", record_replace)

    atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)

    assert events == [
        "file-fsync",
        "parent-open",
        "parent-fsync",
        "parent-close",
        "replace",
    ]


def test_atomic_write_has_no_fallible_operation_after_replace(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "receipt.json"
    replaced = False
    parent_descriptor = 999
    original_replace = receipts.os.replace

    def record_open(directory: Path, flags: int) -> int:
        return parent_descriptor

    def fail_if_after_replace(descriptor: int) -> None:
        if replaced:
            raise OSError("post-replace operation must not run")

    def record_replace(source: Path, destination: Path) -> None:
        nonlocal replaced
        original_replace(source, destination)
        replaced = True

    monkeypatch.setattr(receipts.os, "open", record_open)
    monkeypatch.setattr(receipts.os, "fsync", fail_if_after_replace)
    monkeypatch.setattr(receipts.os, "close", lambda descriptor: None)
    monkeypatch.setattr(receipts.os, "replace", record_replace)

    atomic_write_receipt(output, valid_receipt)

    assert replaced is True
    assert output.exists()


def test_parent_fsync_propagates_supported_platform_storage_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    descriptor = 999

    monkeypatch.setattr(receipts.os, "open", lambda directory, flags: descriptor)
    monkeypatch.setattr(
        receipts.os,
        "fsync",
        lambda received: (_ for _ in ()).throw(OSError(errno.EIO, "storage failure")),
    )
    monkeypatch.setattr(receipts.os, "close", lambda received: None)

    with pytest.raises(OSError, match="storage failure"):
        receipts._fsync_parent(tmp_path)


def test_windows_directory_handle_access_denied_is_tolerated(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    access_denied = PermissionError(errno.EACCES, "directory handles unsupported")
    access_denied.winerror = 5  # type: ignore[attr-defined]
    monkeypatch.setattr(
        receipts.os,
        "open",
        lambda directory, flags: (_ for _ in ()).throw(access_denied),
    )
    monkeypatch.setattr(receipts.os, "name", "nt")

    receipts._fsync_parent(tmp_path)


def test_validate_receipt_rejects_truncated_non_finite_and_unknown_receipts(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    output = tmp_path / "receipt.json"
    atomic_write_receipt(output, valid_receipt)
    stored = json.loads(output.read_text(encoding="utf-8"))
    schema = _schema_path("model-contract-receipt.schema.json")

    with pytest.raises(ReceiptValidationError):
        validate_receipt({"receipt_type": "model-contract"}, schema)

    non_finite = copy.deepcopy(stored)
    non_finite["normative"]["observed_shapes"]["loss"] = [float("inf")]
    with pytest.raises(ReceiptValidationError, match="non-finite"):
        validate_receipt(non_finite, schema)

    unknown = copy.deepcopy(stored)
    unknown["receipt_type"] = "unapproved"
    with pytest.raises(ReceiptValidationError, match="unknown"):
        validate_receipt(unknown, schema)

    with pytest.raises(ReceiptValidationError, match="allowlisted"):
        validate_receipt(stored, _schema_path("feasibility-receipt.schema.json"))


def test_boolean_schema_version_is_rejected(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    valid_receipt["schema_version"] = True

    with pytest.raises(ReceiptValidationError, match="unknown"):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_volatile_only_differences_do_not_change_normative_digest(
    valid_receipt: dict[str, object]
) -> None:
    other = copy.deepcopy(valid_receipt)
    other["metadata"] = {
        "timestamp": "2026-08-24T00:00:00Z",
        "run_id": "run-b",
        "temporary_directory": "/tmp/different",
        "container_instance_id": "container-b",
    }

    assert normative_receipt_sha256(valid_receipt) == normative_receipt_sha256(other)


def test_normative_divergence_changes_normative_digest(
    valid_receipt: dict[str, object]
) -> None:
    other = copy.deepcopy(valid_receipt)
    other["normative"]["observed_shapes"]["logits"] = [2, 299, 4]

    assert normative_receipt_sha256(valid_receipt) != normative_receipt_sha256(other)


def test_schema_forbids_receipt_declared_volatile_fields(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    valid_receipt["metadata"]["volatile_fields"] = ["model_sha256"]

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def _schema_path(name: str) -> Path:
    return Path(__file__).parents[2] / "schemas" / name
