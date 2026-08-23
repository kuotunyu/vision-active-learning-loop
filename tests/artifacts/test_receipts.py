from __future__ import annotations

import copy
import errno
import json
import os
from pathlib import Path

import pytest

import vision_active_learning_loop.artifacts.receipts as receipts
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    normative_receipt_sha256,
    validate_receipt,
)


HASH = "a" * 64
MODEL_CONTRACT_INVARIANTS = (
    "aspect_preserving_size",
    "asset_receipt_pass",
    "bilinear_resize",
    "bottom_right_padding_is_zero",
    "canonical_environment",
    "config_num_labels_4",
    "config_num_queries_300",
    "decoder_class_heads_four_channels",
    "decoder_layers_at_least_two",
    "expected_valid_mask_rectangles",
    "final_boxes_are_last_layer",
    "foreground_scores_are_sigmoid",
    "four_class_head_reset_seed_17",
    "inputs_on_selected_cuda_device",
    "intermediate_reference_points_shape",
    "label_free_model_call",
    "labels_absent",
    "live_snapshot_matches_asset_receipt",
    "live_transformers_source_matches_asset_receipt",
    "logits_shape",
    "model_eval_mode",
    "model_on_selected_cuda_device",
    "native_fifth_logit_absent",
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
    "torch_cuda_available",
    "torch_inference_mode",
    "torch_selected_gpu_is_canonical",
)
@pytest.fixture
def valid_receipt() -> dict[str, object]:
    document: dict[str, object] = {
        "receipt_type": "model-contract",
        "schema_version": 1,
        "normative": {
            "model_sha256": "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
            "config_sha256": HASH,
            "config_file_sha256": "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2",
            "source_sha256": HASH,
            "processor_sha256": HASH,
            "processor_file_sha256": "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a",
            "fixture_sha256": "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f",
            "probe_sha256": HASH,
            "environment_sha256": HASH,
            "model": {
                "repository": "PekingU/rtdetr_r18vd",
                "revision": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
            },
            "transformers_version": "5.15.0",
            "source_files": {
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
            },
            "config": {
                "num_queries": 300,
                "num_labels": 4,
                "decoder_layers": 3,
                "id2label": {"0": "D00", "1": "D10", "2": "D20", "3": "D40"},
                "label2id": {"D00": 0, "D10": 1, "D20": 2, "D40": 3},
            },
            "processor": {
                "size": {"max_height": 640, "max_width": 640},
                "resample": 2,
                "do_pad": True,
                "pad_size": {"height": 640, "width": 640},
                "do_rescale": True,
                "rescale_factor": 1 / 255,
                "do_normalize": False,
            },
            "environment": {
                "schema_version": 1,
                "python": "3.12.11",
                "torch": "2.12.0+cu126",
                "torchvision": "0.27.0+cu126",
                "transformers": "5.15.0",
                "pycocotools": "2.0.10",
                "cuda_runtime": "12.6",
                "gpu_name": "NVIDIA GeForce RTX 4090",
                "gpu_uuid": "GPU-11111111-1111-1111-1111-111111111111",
                "driver": "591.86",
                "os": "Linux",
                "wsl": True,
                "container_image_digest": "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356",
                "runtime_image_digest": "sha256:7ba1dd9364de4bdfc60ee14c42f3441d736e46fcd41128992c3cd49c67059ae2",
                "tf32": False,
                "deterministic_algorithms": True,
                "bf16_supported": True,
                "status": "PASS",
                "errors": [],
                "torch_execution": {
                    "cuda_available": True,
                    "device_count": 1,
                    "selected_index": 0,
                    "selected_name": "NVIDIA GeForce RTX 4090",
                    "torch_selected_gpu_uuid": "11111111-1111-1111-1111-111111111111",
                    "selected_device": "cuda:0",
                    "nvidia_smi_gpu_name": "NVIDIA GeForce RTX 4090",
                    "nvidia_smi_gpu_uuid": "GPU-11111111-1111-1111-1111-111111111111",
                    "model_device": "cuda:0",
                    "pixel_values_device": "cuda:0",
                    "pixel_mask_device": "cuda:0",
                    "logits_device": "cuda:0",
                    "final_boxes_device": "cuda:0",
                    "penultimate_boxes_device": "cuda:0",
                    "intermediate_boxes_device": "cuda:0",
                },
            },
            "observed_shapes": {
                "logits": [2, 300, 4],
                "pred_boxes": [2, 300, 4],
                "intermediate_reference_points": [2, 3, 300, 4],
                "pixel_values": [2, 3, 640, 640],
                "pixel_mask": [2, 640, 640],
            },
            "invariants": {name: True for name in MODEL_CONTRACT_INVARIANTS},
            "status": "PASS",
            "errors": [],
        },
        "metadata": {"timestamp": "2026-08-23T00:00:00Z", "run_id": "run-a"},
    }
    normative = document["normative"]
    assert isinstance(normative, dict)
    for digest_name, evidence_name in (
        ("config_sha256", "config"),
        ("processor_sha256", "processor"),
        ("source_sha256", "source_files"),
        ("environment_sha256", "environment"),
    ):
        normative[digest_name] = canonical_json_sha256(normative[evidence_name])
    return document


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


@pytest.mark.parametrize(
    ("mutation", "rehash", "expected"),
    [
        (
            lambda normative: normative.update({"config_sha256": "0" * 64}),
            None,
            "config_sha256",
        ),
        (
            lambda normative: normative.update({"processor_sha256": "0" * 64}),
            None,
            "processor_sha256",
        ),
        (
            lambda normative: normative.update({"source_sha256": "0" * 64}),
            None,
            "source_sha256",
        ),
        (
            lambda normative: normative.update({"environment_sha256": "0" * 64}),
            None,
            "environment_sha256",
        ),
        (
            lambda normative: normative["config"].update({"num_queries": 299}),
            "config",
            "config_num_queries_300",
        ),
        (
            lambda normative: normative["observed_shapes"].update(
                {"logits": [2, 299, 4]}
            ),
            None,
            "logits_shape",
        ),
        (
            lambda normative: normative["environment"]["torch_execution"].update(
                {"model_device": "cpu"}
            ),
            "environment",
            "model_on_selected_cuda_device",
        ),
        (
            lambda normative: (
                normative["environment"].update({"gpu_name": "Not canonical"}),
                normative["environment"]["torch_execution"].update(
                    {
                        "selected_name": "Not canonical",
                        "nvidia_smi_gpu_name": "Not canonical",
                    }
                ),
            ),
            "environment",
            "canonical_environment",
        ),
        (
            lambda normative: normative["environment"]["torch_execution"].update(
                {
                    "selected_index": 9,
                    "selected_device": "cuda:9",
                    "model_device": "cuda:9",
                    "pixel_values_device": "cuda:9",
                    "pixel_mask_device": "cuda:9",
                    "logits_device": "cuda:9",
                    "final_boxes_device": "cuda:9",
                    "penultimate_boxes_device": "cuda:9",
                    "intermediate_boxes_device": "cuda:9",
                }
            ),
            "environment",
            "torch_selected_gpu_is_canonical",
        ),
        (
            lambda normative: (
                normative["environment"].update({"gpu_uuid": "GPU-"}),
                normative["environment"]["torch_execution"].update(
                    {
                        "torch_selected_gpu_uuid": "GPU-",
                        "nvidia_smi_gpu_uuid": "GPU-",
                    }
                ),
            ),
            "environment",
            "torch_selected_gpu_is_canonical",
        ),
    ],
)
def test_model_contract_rejects_digest_or_evidence_contradiction(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    mutation: object,
    rehash: str | None,
    expected: str,
) -> None:
    """Catch content-addressed PASS receipts whose embedded proof is false."""
    assert callable(mutation)
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    mutation(normative)
    if rehash is not None:
        normative[f"{rehash}_sha256"] = canonical_json_sha256(normative[rehash])

    with pytest.raises(ReceiptValidationError, match=expected):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


@pytest.mark.parametrize(
    "field",
    ["model_sha256", "config_file_sha256", "processor_file_sha256"],
)
def test_model_contract_rejects_unapproved_asset_pin(
    tmp_path: Path, valid_receipt: dict[str, object], field: str
) -> None:
    """Catch a self-consistent receipt for unapproved model asset bytes."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    normative[field] = "b" * 64

    with pytest.raises(ReceiptValidationError, match="approved pin|must equal"):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_model_contract_rejects_unapproved_source_observation(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch recomputing the aggregate around non-pinned Transformers source."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    source_files = normative["source_files"]
    assert isinstance(source_files, dict)
    source = source_files["models/rt_detr/modeling_rt_detr.py"]
    assert isinstance(source, dict)
    source["sha256"] = "b" * 64
    normative["source_sha256"] = canonical_json_sha256(source_files)

    with pytest.raises(ReceiptValidationError, match="approved source|must equal"):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_runtime_image_digest_is_recorded_not_pinned(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch rejecting a legitimate rebuild from the same approved base image."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    environment = normative["environment"]
    assert isinstance(environment, dict)
    environment["runtime_image_digest"] = f"sha256:{'b' * 64}"
    normative["environment_sha256"] = canonical_json_sha256(environment)

    atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_model_contract_schema_requires_timestamp(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch publishing a receipt without the required execution timestamp."""
    metadata = valid_receipt["metadata"]
    assert isinstance(metadata, dict)
    del metadata["timestamp"]

    with pytest.raises(ReceiptValidationError, match="timestamp"):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_model_contract_schema_requires_every_rtdetr_source(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch a recomputed aggregate hiding omitted pinned source evidence."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    source_files = normative["source_files"]
    assert isinstance(source_files, dict)
    del source_files["models/rt_detr/configuration_rt_detr.py"]
    normative["source_sha256"] = canonical_json_sha256(source_files)

    with pytest.raises(
        ReceiptValidationError,
        match="source_sha256|configuration_rt_detr.py",
    ):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


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
    valid_receipt["metadata"] = {
        "timestamp": "2026-08-23T00:00:00Z",
        "receipt_content_sha256": "0" * 64,
    }
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
    other["normative"]["invariants"]["logits_shape"] = False
    other["normative"]["status"] = "FAIL"
    other["normative"]["errors"] = ["logits_shape"]

    assert normative_receipt_sha256(valid_receipt) != normative_receipt_sha256(other)


def test_schema_forbids_receipt_declared_volatile_fields(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    valid_receipt["metadata"]["volatile_fields"] = ["model_sha256"]

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def _schema_path(name: str) -> Path:
    return Path(__file__).parents[2] / "schemas" / name
