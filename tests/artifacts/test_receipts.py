from __future__ import annotations

import copy
import errno
import json
import multiprocessing
import os
from pathlib import Path
from typing import BinaryIO, Self

import pytest

from vision_active_learning_loop.artifacts import receipts
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.no_clobber import (
    NoClobberError,
    StagingFile,
)
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    normative_receipt_sha256,
    validate_receipt,
)

from .test_no_clobber import _make_directory_link

HASH = "a" * 64
MODEL_CONTRACT_INVARIANTS = (
    "aspect_preserving_size",
    "asset_receipt_pass",
    "bilinear_resize",
    "bottom_right_padding_is_zero",
    "canonical_environment",
    "class_reset_preserves_structure",
    "config_decoder_layers_3",
    "config_num_labels_4",
    "config_num_queries_300",
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


def build_valid_environment_receipt(run_id: str = "run-a") -> dict[str, object]:
    contract = dict(receipts._APPROVED_ENVIRONMENT_CONTRACT)
    observed = {
        "schema_version": 1,
        "python": "3.12.11",
        "uv": "0.8.15",
        "scipy": "1.18.0",
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
        "container_image_digest": contract["container_image_digest"],
        "runtime_image_digest": "sha256:7ba1dd9364de4bdfc60ee14c42f3441d736e46fcd41128992c3cd49c67059ae2",
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
        "data_root_unset": True,
    }
    invariants = {
        "approved_base_image": True,
        "bf16_supported": True,
        "canonical_gpu": True,
        "canonical_os_wsl": True,
        "data_root_unset": True,
        "deterministic_algorithms": True,
        "exact_cuda_runtime": True,
        "exact_pycocotools": True,
        "exact_python": True,
        "exact_scipy": True,
        "exact_torch": True,
        "exact_torchvision": True,
        "exact_transformers": True,
        "exact_uv": True,
        "runtime_image_recorded": True,
        "tf32_disabled": True,
    }
    document = {
        "receipt_type": "environment",
        "schema_version": 1,
        "normative": {
            "contract": contract,
            "contract_sha256": canonical_json_sha256(contract),
            "observed": observed,
            "invariants": invariants,
            "status": "PASS",
            "errors": [],
        },
        "metadata": {"timestamp": "2026-08-23T00:00:00Z", "run_id": run_id},
    }
    document["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        document
    )
    return document


def _race_publish_receipt(
    output: Path, run_id: str, barrier: object, result_queue: object
) -> None:
    original_publish = receipts.publish_staged_file_no_clobber

    def synchronized_publish(staging: Path, destination: Path) -> None:
        barrier.wait()  # type: ignore[attr-defined]
        original_publish(staging, destination)

    receipts.publish_staged_file_no_clobber = synchronized_publish
    try:
        digest = atomic_write_receipt(output, build_valid_environment_receipt(run_id))
    except NoClobberError:
        result_queue.put("no-clobber")  # type: ignore[attr-defined]
    else:
        result_queue.put(f"published:{digest}")  # type: ignore[attr-defined]


def build_valid_model_contract_receipt() -> dict[str, object]:
    parent_environment = build_valid_environment_receipt()
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
            "loss_source_sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
            "synthetic_target_sha256": "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198",
            "probe_sha256": "42a1df763c5e22cdfdcfc16821ba4c371946a9e81004de2425c369e3e6d5964e",
            "environment_sha256": HASH,
            "environment_receipt_sha256": receipts._stored_receipt_sha256(
                parent_environment
            ),
            "environment_receipt_content_sha256": parent_environment["metadata"][
                "receipt_content_sha256"
            ],
            "parent_environment_receipt": parent_environment,
            "model": {
                "repository": "PekingU/rtdetr_r18vd",
                "revision": "cc5b50f32f0100caaa3bd275343e2fb17762c73d",
            },
            "transformers_version": "5.15.0",
            "source_files": {
                "loss/loss_rt_detr.py": {
                    "size": 22057,
                    "sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
                },
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
                "uv": "0.8.15",
                "scipy": "1.18.0",
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
                "data_root_unset": True,
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
                "intermediate_logits": [2, 3, 300, 4],
                "enc_outputs_class": [2, 8400, 4],
                "enc_topk_logits": [2, 300, 4],
                "pred_boxes": [2, 300, 4],
                "intermediate_reference_points": [2, 3, 300, 4],
                "pixel_values": [2, 3, 640, 640],
                "pixel_mask": [2, 640, 640],
            },
            "labeled_observed_shapes": {
                "loss": [],
                "logits": [2, 300, 4],
                "intermediate_logits": [2, 3, 300, 4],
                "enc_outputs_class": [2, 8400, 4],
                "enc_topk_logits": [2, 300, 4],
                "decoder_auxiliary_logits": [[2, 300, 4], [2, 300, 4]],
                "encoder_auxiliary_logits": [[2, 300, 4]],
                "denoising_auxiliary_logits": [
                    [2, 200, 4],
                    [2, 200, 4],
                    [2, 200, 4],
                ],
            },
            "observed_class_modules": {
                "decoder_class_heads": [
                    {
                        "path": f"model.model.decoder.class_embed[{index}]",
                        "replaced": True,
                        "in_features": 256,
                        "out_features": 4,
                        "bias": True,
                        "device": "cuda:0",
                        "dtype": "torch.float32",
                    }
                    for index in range(3)
                ],
                "denoising_class_embed": {
                    "path": "model.model.denoising_class_embed",
                    "replaced": True,
                    "embedding_dim": 256,
                    "num_embeddings": 5,
                    "padding_idx": 4,
                    "device": "cuda:0",
                    "dtype": "torch.float32",
                },
                "encoder_score_head": {
                    "path": "model.model.enc_score_head",
                    "replaced": True,
                    "in_features": 256,
                    "out_features": 4,
                    "bias": True,
                    "device": "cuda:0",
                    "dtype": "torch.float32",
                },
                "num_labels": 4,
                "id2label": {"0": "D00", "1": "D10", "2": "D20", "3": "D40"},
                "label2id": {"D00": 0, "D10": 1, "D20": 2, "D40": 3},
                "reset_seed": 17,
                "replacement_order": [
                    "model.model.decoder.class_embed[0]",
                    "model.model.decoder.class_embed[1]",
                    "model.model.decoder.class_embed[2]",
                    "model.model.denoising_class_embed",
                    "model.model.enc_score_head",
                ],
                "deterministic_replay": True,
                "structure_preserved": True,
                "pretrained_class_rows_reused": False,
            },
            "labeled_loss_hex": (3.25).hex(),
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


@pytest.fixture
def valid_receipt() -> dict[str, object]:
    return build_valid_model_contract_receipt()


def test_model_contract_schema_accepts_complete_a2_evidence(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch a schema that cannot represent the approved complete A2 proof."""
    atomic_write_receipt(tmp_path / "model-contract.json", valid_receipt)


@pytest.mark.parametrize(
    ("field", "nested"),
    [
        ("loss_source_sha256", None),
        ("synthetic_target_sha256", None),
        ("observed_class_modules", None),
        ("labeled_observed_shapes", None),
        ("invariants", "encoder_score_head_four_channels"),
    ],
)
def test_model_contract_schema_rejects_missing_a2_evidence(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    field: str,
    nested: str | None,
) -> None:
    """Catch accepting the narrower historical Option A receipt as A2."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    if nested is None:
        del normative[field]
    else:
        child = normative[field]
        assert isinstance(child, dict)
        del child[nested]

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "model-contract.json", valid_receipt)


def test_model_contract_rejects_self_consistent_eighty_channel_evidence(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch a fully re-described COCO-width contract retaining PASS booleans."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    for shapes_name in ("observed_shapes", "labeled_observed_shapes"):
        shapes = normative[shapes_name]
        assert isinstance(shapes, dict)
        for name in (
            "logits",
            "intermediate_logits",
            "enc_outputs_class",
            "enc_topk_logits",
        ):
            shapes[name][-1] = 80
    labeled = normative["labeled_observed_shapes"]
    assert isinstance(labeled, dict)
    for name in (
        "decoder_auxiliary_logits",
        "encoder_auxiliary_logits",
        "denoising_auxiliary_logits",
    ):
        for shape in labeled[name]:
            shape[-1] = 80
    modules = normative["observed_class_modules"]
    assert isinstance(modules, dict)
    for head in modules["decoder_class_heads"]:
        head["out_features"] = 80
    modules["encoder_score_head"]["out_features"] = 80

    with pytest.raises(ReceiptValidationError, match="four_channels|non_four"):
        atomic_write_receipt(tmp_path / "model-contract.json", valid_receipt)


@pytest.mark.parametrize(
    ("loss_shape", "loss_hex"),
    [([1], (3.25).hex()), ([], float("nan").hex()), ([], float("inf").hex())],
)
def test_model_contract_rejects_false_finite_scalar_loss_claim(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    loss_shape: list[int],
    loss_hex: str,
) -> None:
    """Catch a finite-scalar invariant detached from the observed labeled loss."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    normative["labeled_observed_shapes"]["loss"] = loss_shape
    normative["labeled_loss_hex"] = loss_hex

    with pytest.raises(ReceiptValidationError, match="finite_scalar"):
        atomic_write_receipt(tmp_path / "model-contract.json", valid_receipt)


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
    "existing_kind",
    [
        "valid-receipt",
        "invalid-receipt",
        "empty-file",
        "directory",
        "symlink",
        "junction",
    ],
)
def test_receipt_publication_never_replaces_any_existing_destination(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    existing_kind: str,
) -> None:
    """Catch any pre-existing path being overwritten, followed, or repurposed."""
    output = tmp_path / "receipt.json"
    prior = b"prior-evidence"
    if existing_kind == "valid-receipt":
        atomic_write_receipt(output, valid_receipt)
        original = output.read_bytes()
    elif existing_kind == "invalid-receipt":
        output.write_bytes(prior)
        original = prior
    elif existing_kind == "empty-file":
        output.write_bytes(b"")
        original = b""
    elif existing_kind == "directory":
        output.mkdir()
        (output / "prior.bin").write_bytes(prior)
        original = prior
    elif existing_kind == "symlink":
        source = tmp_path / "source.bin"
        source.write_bytes(prior)
        try:
            output.symlink_to(source)
        except OSError as error:
            pytest.skip(f"file symlink unavailable: {error}")
        original = prior
    else:
        source = tmp_path / "junction-source"
        _make_directory_link(output, source, junction=True)
        (source / "prior.bin").write_bytes(prior)
        original = prior

    with pytest.raises(NoClobberError):
        atomic_write_receipt(output, valid_receipt)

    if existing_kind in {"directory", "junction"}:
        assert (output / "prior.bin").read_bytes() == original
    else:
        assert output.read_bytes() == original


def test_receipt_publication_requires_existing_non_link_parent(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    missing_output = tmp_path / "missing" / "receipt.json"
    with pytest.raises(OSError, match="parent"):
        atomic_write_receipt(missing_output, valid_receipt)
    assert not missing_output.exists()

    real_parent = tmp_path / "real-parent"
    linked_parent = tmp_path / "linked-parent"
    _make_directory_link(linked_parent, real_parent, junction=True)
    linked_output = linked_parent / "receipt.json"
    with pytest.raises(OSError, match="parent|link|junction"):
        atomic_write_receipt(linked_output, valid_receipt)
    assert not linked_output.exists()


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
            "parent environment",
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
            "parent environment",
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


def test_model_contract_rejects_unapproved_probe_implementation(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch rehashing an arbitrary probe implementation into an otherwise valid PASS."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    normative["probe_sha256"] = "0" * 64

    with pytest.raises(
        ReceiptValidationError, match="probe_sha256.*approved pin|must equal"
    ):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_model_contract_rejects_rehashed_decoder_depth_mutation(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    """Catch a self-consistent depth-four config and output shape replacing the pin."""
    normative = valid_receipt["normative"]
    assert isinstance(normative, dict)
    config = normative["config"]
    shapes = normative["observed_shapes"]
    assert isinstance(config, dict)
    assert isinstance(shapes, dict)
    config["decoder_layers"] = 4
    shapes["intermediate_reference_points"] = [2, 4, 300, 4]
    normative["config_sha256"] = canonical_json_sha256(config)

    with pytest.raises(ReceiptValidationError, match="config_decoder_layers_3"):
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
    parent = normative["parent_environment_receipt"]
    parent["normative"]["observed"]["runtime_image_digest"] = f"sha256:{'b' * 64}"
    parent["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        parent
    )
    normative["environment_receipt_content_sha256"] = parent["metadata"][
        "receipt_content_sha256"
    ]
    normative["environment_receipt_sha256"] = receipts._stored_receipt_sha256(parent)

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
        "run_id": "run-a",
        "receipt_content_sha256": "0" * 64,
    }
    output = tmp_path / "receipt.json"

    with pytest.raises(ReceiptValidationError, match="content hash"):
        atomic_write_receipt(output, valid_receipt)

    assert not output.exists()


def test_receipt_publication_never_calls_replace(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "receipt.json"
    monkeypatch.setattr(
        receipts.os,
        "replace",
        lambda *args: (_ for _ in ()).throw(
            AssertionError("replace cannot provide no-clobber publication")
        ),
    )

    atomic_write_receipt(output, valid_receipt)

    assert output.exists()


def test_atomic_write_fsyncs_file_and_parent_before_decisive_link(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    events: list[str] = []
    parent_descriptor = 999
    original_link = receipts.os.link

    def record_open(directory: Path, flags: int) -> int:
        assert directory == tmp_path
        assert flags == os.O_RDONLY
        events.append("parent-open")
        return parent_descriptor

    def record_fsync(descriptor: int) -> None:
        events.append(
            "parent-fsync" if descriptor == parent_descriptor else "file-fsync"
        )

    def record_close(descriptor: int) -> None:
        assert descriptor == parent_descriptor
        events.append("parent-close")

    def record_link(source: Path, destination: Path, *, follow_symlinks: bool) -> None:
        events.append("link")
        original_link(source, destination, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(receipts.os, "open", record_open)
    monkeypatch.setattr(receipts.os, "fsync", record_fsync)
    monkeypatch.setattr(receipts.os, "close", record_close)
    monkeypatch.setattr(receipts.os, "link", record_link)

    atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)

    assert events == [
        "file-fsync",
        "parent-open",
        "parent-fsync",
        "parent-close",
        "link",
    ]


def test_atomic_write_has_no_required_fallible_operation_after_link(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "receipt.json"
    linked = False
    parent_descriptor = 999
    original_link = receipts.os.link
    original_unlink = Path.unlink

    def record_open(directory: Path, flags: int) -> int:
        return parent_descriptor

    def fail_if_after_link(descriptor: int) -> None:
        if linked:
            raise OSError("post-link operation must not run")

    def record_link(source: Path, destination: Path, *, follow_symlinks: bool) -> None:
        nonlocal linked
        original_link(source, destination, follow_symlinks=follow_symlinks)
        linked = True

    def fail_stage_cleanup(path: Path, *args: object, **kwargs: object) -> None:
        if linked and path.name.endswith(".staging"):
            raise OSError("injected best-effort cleanup failure")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(receipts.os, "open", record_open)
    monkeypatch.setattr(receipts.os, "fsync", fail_if_after_link)
    monkeypatch.setattr(receipts.os, "close", lambda descriptor: None)
    monkeypatch.setattr(receipts.os, "link", record_link)
    monkeypatch.setattr(Path, "unlink", fail_stage_cleanup)

    atomic_write_receipt(output, valid_receipt)

    assert linked is True
    assert output.exists()
    stored = json.loads(output.read_text(encoding="utf-8"))
    validate_receipt(stored, _schema_path("model-contract-receipt.schema.json"))


def test_receipt_publication_race_has_one_complete_winner(tmp_path: Path) -> None:
    output = tmp_path / "environment.json"
    context = multiprocessing.get_context("spawn")
    barrier = context.Barrier(2)
    result_queue = context.Queue()
    processes = [
        context.Process(
            target=_race_publish_receipt,
            args=(output, run_id, barrier, result_queue),
        )
        for run_id in ("run-a", "run-b")
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=20)
    alive = [process for process in processes if process.is_alive()]
    for process in alive:
        process.terminate()
        process.join()

    assert not alive
    assert all(process.exitcode == 0 for process in processes)
    results = [result_queue.get(timeout=5) for _ in processes]
    assert sum(result.startswith("published:") for result in results) == 1
    assert results.count("no-clobber") == 1
    stored = json.loads(output.read_text(encoding="utf-8"))
    validate_receipt(stored, _schema_path("environment-receipt.schema.json"))
    assert stored["metadata"]["run_id"] in {"run-a", "run-b"}
    assert not list(tmp_path.glob("*.partial"))
    assert not list(tmp_path.glob("*.staging"))


@pytest.mark.parametrize("failure", ["file-fsync", "parent-fsync", "hard-link"])
def test_receipt_publication_storage_failure_leaves_no_destination(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
    failure: str,
) -> None:
    output = tmp_path / "receipt.json"

    if failure == "file-fsync":
        monkeypatch.setattr(
            receipts.os,
            "fsync",
            lambda descriptor: (_ for _ in ()).throw(
                OSError(errno.EIO, "injected file fsync failure")
            ),
        )
    elif failure == "parent-fsync":
        monkeypatch.setattr(
            receipts,
            "_fsync_parent",
            lambda parent: (_ for _ in ()).throw(
                OSError(errno.EIO, "injected parent fsync failure")
            ),
        )
    else:
        monkeypatch.setattr(
            receipts,
            "publish_staged_file_no_clobber",
            lambda staging, destination: (_ for _ in ()).throw(
                OSError(errno.EIO, "injected hard-link failure")
            ),
        )

    with pytest.raises(OSError, match="injected"):
        atomic_write_receipt(output, valid_receipt)

    assert not output.exists()
    assert not list(tmp_path.glob("*.partial"))
    assert not list(tmp_path.glob("*.staging"))


def test_receipt_publication_detects_injected_short_write(
    tmp_path: Path,
    valid_receipt: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    output = tmp_path / "receipt.json"
    original_open = receipts.open_unique_staging_file

    class ShortWriter:
        def __init__(self, handle: BinaryIO) -> None:
            self.handle = handle

        def __enter__(self) -> Self:
            return self

        def __exit__(self, *args: object) -> None:
            self.handle.close()

        def write(self, content: bytes) -> int:
            self.handle.write(content[:-1])
            return len(content)

        def flush(self) -> None:
            self.handle.flush()

        def fileno(self) -> int:
            return self.handle.fileno()

    def open_short_writer(destination: Path) -> StagingFile:
        staging = original_open(destination)
        return StagingFile(staging.path, ShortWriter(staging.handle))  # type: ignore[arg-type]

    monkeypatch.setattr(receipts, "open_unique_staging_file", open_short_writer)

    with pytest.raises(ReceiptValidationError, match="staged receipt bytes"):
        atomic_write_receipt(output, valid_receipt)

    assert not output.exists()
    assert not list(tmp_path.glob("*.staging"))


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


def test_wave0_gate_receipt_requires_complete_parent_and_comparison_inventory(
    tmp_path: Path,
) -> None:
    from vision_active_learning_loop.gates.wave0 import (
        WAVE0_GATE_INVARIANTS,
        Wave0GateReceipt,
    )

    stages = (
        "environment",
        "model_assets",
        "model_contract",
        "feasibility_a",
        "feasibility_b",
    )
    attempts = ("primary", "clean_a", "clean_b")
    receipt = Wave0GateReceipt(
        run_id="run-a",
        parent_receipts={
            attempt: {stage: "a" * 64 for stage in stages} for attempt in attempts
        },
        deterministic_comparisons={
            f"{attempt}_{suffix}": "b" * 64
            for attempt in attempts
            for suffix in ("feasibility_a", "feasibility_b", "replay")
        },
        invariants={name: True for name in WAVE0_GATE_INVARIANTS},
        errors=[],
    )
    output = tmp_path / "wave0-gate.json"

    atomic_write_receipt(output, receipt.as_dict())

    stored = json.loads(output.read_text(encoding="utf-8"))
    validate_receipt(stored, _schema_path("wave0-gate-receipt.schema.json"))

    for field in ("parent_receipts", "deterministic_comparisons"):
        forged = receipt.as_dict()
        normative = forged["normative"]
        assert isinstance(normative, dict)
        value = normative[field]
        assert isinstance(value, dict)
        value.pop(next(iter(value)))
        with pytest.raises(ReceiptValidationError, match="requires every"):
            atomic_write_receipt(tmp_path / f"forged-{field}.json", forged)


def test_volatile_only_differences_do_not_change_normative_digest(
    valid_receipt: dict[str, object]
) -> None:
    other = copy.deepcopy(valid_receipt)
    other["metadata"] = {
        "timestamp": "2026-08-24T00:00:00Z",
        "run_id": "run-a",
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


def test_model_contract_rejects_rehashed_noncanonical_uv_environment(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    normative = valid_receipt["normative"]
    environment = normative["environment"]
    environment["uv"] = "0.11.18"
    normative["environment_sha256"] = canonical_json_sha256(environment)

    with pytest.raises(ReceiptValidationError, match="parent environment"):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def test_schema_forbids_receipt_declared_volatile_fields(
    tmp_path: Path, valid_receipt: dict[str, object]
) -> None:
    valid_receipt["metadata"]["volatile_fields"] = ["model_sha256"]

    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)


def _schema_path(name: str) -> Path:
    return Path(__file__).parents[2] / "schemas" / name
