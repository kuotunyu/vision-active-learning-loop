"""Schema-validated, content-addressed receipt publication."""

from __future__ import annotations

import copy
import errno
import hashlib
import json
import math
import os
import re
from collections.abc import Mapping
from pathlib import Path

from .digests import canonical_json_sha256
from .no_clobber import open_unique_staging_file, publish_staged_file_no_clobber


class ReceiptValidationError(ValueError):
    """Raised when a receipt is not an approved, internally consistent record."""


_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"
_ALLOWED_SCHEMAS = {
    ("environment", 1): _SCHEMA_ROOT / "environment-receipt.schema.json",
    ("model-contract", 1): _SCHEMA_ROOT / "model-contract-receipt.schema.json",
    ("feasibility", 3): _SCHEMA_ROOT / "feasibility-receipt.schema.json",
    ("model-assets", 1): _SCHEMA_ROOT / "model-asset-receipt.schema.json",
    ("wave0-gate", 2): _SCHEMA_ROOT / "wave0-gate-receipt.schema.json",
}
_APPROVED_ENVIRONMENT_CONTRACT = {
    "schema_version": 1,
    "python": "3.12.11",
    "uv": "0.8.15",
    "scipy": "1.18.0",
    "torch": "2.12.0+cu126",
    "torchvision": "0.27.0+cu126",
    "transformers": "5.15.0",
    "pycocotools": "2.0.10",
    "cuda_runtime": "12.6",
    "canonical_os": "Linux",
    "requires_wsl": True,
    "gpu_name": "NVIDIA GeForce RTX 4090",
    "container_image_digest": (
        "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
    ),
    "tf32": False,
    "deterministic_algorithms": True,
    "bf16_supported": True,
}
_APPROVED_MODEL_CONTRACT_ASSET_HASHES = {
    "model_sha256": "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
    "config_file_sha256": "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2",
    "processor_file_sha256": "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a",
    "fixture_sha256": "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f",
    "loss_source_sha256": "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
    "synthetic_target_sha256": "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198",
    "probe_sha256": "42a1df763c5e22cdfdcfc16821ba4c371946a9e81004de2425c369e3e6d5964e",
}
_APPROVED_RTDETR_SOURCE_FILES = {
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
}
_A3_BACKWARD_OPERATION = "grid_sampler_2d_backward_cuda"
_A4_BACKWARD_SOURCE_HASH_RULE = "python-source-lf-normalized-sha256-v1"
_A4_BACKWARD_SOURCE_SHA256 = {
    "torch_init": "d9dfff4b75d46e4c75572200a3466b70231d05b0318e38ac1bd121789165fb49",
    "torch_nn_functional": "27493186ee22f811b553e31d9c804d4d46716d1be62d034d731537f66f27ef19",
    "transformers_modeling_rt_detr": (
        "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3"
    ),
}
_A6_DETERMINISTIC_ATTENTION = {
    "attn_implementation": "sdpa",
    "backend": "MATH",
    "scope": "labeled_forward_through_backward",
    "before": {
        "cudnn": True,
        "flash": True,
        "math": True,
        "memory_efficient": True,
    },
    "inside": {
        "cudnn": False,
        "flash": False,
        "math": True,
        "memory_efficient": False,
    },
    "after": {
        "cudnn": True,
        "flash": True,
        "math": True,
        "memory_efficient": True,
    },
    "restored": True,
    "source_hash_rule": "python-source-lf-normalized-sha256-v1",
    "source_sha256": {
        "torch_nn_attention": (
            "56e10b6f965cc050db782dd4dc472097c9b02ec5b5fe3ab2c8b04055c0b0bbe0"
        ),
        "transformers_sdpa_attention": (
            "d334e0b1d0c17ac97964348e49e6df681a4193241c8161f23292817ca39e2098"
        ),
    },
}
_APPROVED_MODEL_DOCUMENT_HASHES = {
    "rtdetr": {
        "config": "59cc37a4cc7abe1096b62ab401ef7252e00a0378c83ddc612a0f148e2a3374c0",
        "processor": "2ca7c13652ff0e272ee5153f8bebe5b1058a1706344d76d8376c099f3a3bd8c5",
    },
    "dinov2": {
        "config": "d971c7bfef11cd2ae681bdec253ad8ef811e3e9794d7d202f2dc8137ed312f7e",
        "processor": "0f6addc5987e9ab323986e0e3ad4ef3aeea735e6839c6df97dc9397e8df50669",
    },
}


def validate_receipt(receipt: Mapping[str, object], schema_path: Path) -> None:
    """Validate a stored receipt against its allowlisted receipt type and schema."""
    _validate_receipt(receipt, schema_path=schema_path, require_content_hash=True)


def validate_receipt_for_run(
    receipt: Mapping[str, object], schema_path: Path, run_id: str
) -> None:
    """Validate a receipt and require it to belong to the explicit current run."""
    if not isinstance(run_id, str) or not run_id.strip():
        raise ReceiptValidationError("expected run_id must be non-empty")
    validate_receipt(receipt, schema_path)
    metadata = receipt.get("metadata")
    if not isinstance(metadata, Mapping) or metadata.get("run_id") != run_id:
        raise ReceiptValidationError("receipt run_id does not match current run_id")


def normative_receipt_sha256(receipt: Mapping[str, object]) -> str:
    """Return the digest used to compare deterministic receipt observations."""
    _validate_receipt(receipt, schema_path=None, require_content_hash=False)
    normative = receipt["normative"]
    if not isinstance(normative, Mapping):  # Guarded above; retained for type safety.
        raise ReceiptValidationError("normative must be an object")
    return canonical_json_sha256(dict(normative))


def _stored_receipt_sha256(receipt: Mapping[str, object]) -> str:
    """Hash the exact canonical bytes used by atomic receipt publication."""
    return hashlib.sha256(_canonical_storage_bytes(receipt)).hexdigest()


def atomic_write_receipt(path: Path, receipt: Mapping[str, object]) -> str:
    """Validate and publish one immutable canonical receipt, returning its digest."""
    target = Path(path)
    staging = None
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

        encoded = _canonical_storage_bytes(document)
        expected_storage_sha256 = hashlib.sha256(encoded).hexdigest()
        staging = open_unique_staging_file(target)
        with staging.handle as output:
            output.write(encoded)
            output.flush()
            os.fsync(output.fileno())

        staged_bytes = staging.path.read_bytes()
        if hashlib.sha256(staged_bytes).hexdigest() != expected_storage_sha256:
            raise ReceiptValidationError("staged receipt bytes do not match input")
        try:
            staged_document = json.loads(staged_bytes)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ReceiptValidationError("staged receipt is not valid JSON") from error
        if not isinstance(staged_document, Mapping):
            raise ReceiptValidationError("staged receipt must be an object")
        _validate_receipt(
            staged_document,
            schema_path=expected_schema,
            require_content_hash=True,
        )
        _fsync_parent(target.parent)
        publish_staged_file_no_clobber(staging.path, target)
        return digest
    finally:
        if staging is not None:
            _unlink_staging_best_effort(staging.path)


def _validate_receipt(
    receipt: Mapping[str, object],
    *,
    schema_path: Path | None,
    require_content_hash: bool,
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
    metadata = receipt.get("metadata")
    if not isinstance(normative, Mapping):
        raise ReceiptValidationError("normative must be an object")
    if not isinstance(metadata, Mapping):
        raise ReceiptValidationError("metadata must be an object")
    receipt_type = receipt.get("receipt_type")
    if receipt_type in {
        "environment",
        "model-assets",
        "model-contract",
        "feasibility",
        "wave0-gate",
    }:
        run_id = metadata.get("run_id")
        if not isinstance(run_id, str) or not run_id.strip():
            raise ReceiptValidationError("run_id must be non-empty")
    if receipt_type == "environment":
        _validate_environment_consistency(normative)
    elif receipt_type == "model-contract":
        _validate_model_contract_consistency(normative, metadata)
    elif receipt_type == "feasibility":
        _validate_feasibility_consistency(
            normative, metadata, schema_version=receipt.get("schema_version")
        )
    elif receipt_type == "model-assets":
        _validate_model_assets_consistency(normative)
    elif receipt_type == "wave0-gate":
        _validate_wave0_gate_consistency(normative)
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


def _validate_environment_consistency(normative: Mapping[str, object]) -> None:
    """Reject environment receipts whose claims disagree with exact observations."""
    contract_document = normative.get("contract")
    observed = normative.get("observed")
    invariants = normative.get("invariants")
    if not all(
        isinstance(value, Mapping)
        for value in (contract_document, observed, invariants)
    ):
        raise ReceiptValidationError("environment evidence must be objects")
    assert isinstance(contract_document, Mapping)
    assert isinstance(observed, Mapping)
    assert isinstance(invariants, Mapping)
    if dict(contract_document) != _APPROVED_ENVIRONMENT_CONTRACT:
        raise ReceiptValidationError(
            "environment contract does not match the compiled approved contract"
        )
    if normative.get("contract_sha256") != canonical_json_sha256(
        dict(contract_document)
    ):
        raise ReceiptValidationError("environment contract digest mismatch")

    from ..environment import (
        EnvironmentContract,
        environment_errors,
        environment_invariants,
    )

    contract = EnvironmentContract(
        python=str(contract_document["python"]),
        uv=str(contract_document["uv"]),
        scipy=str(contract_document["scipy"]),
        torch=str(contract_document["torch"]),
        torchvision=str(contract_document["torchvision"]),
        transformers=str(contract_document["transformers"]),
        cuda_runtime=str(contract_document["cuda_runtime"]),
        pycocotools=str(contract_document["pycocotools"]),
        container_image_digest=str(contract_document["container_image_digest"]),
        tf32=bool(contract_document["tf32"]),
        deterministic_algorithms=bool(contract_document["deterministic_algorithms"]),
        bf16_supported=bool(contract_document["bf16_supported"]),
        canonical_os=str(contract_document["canonical_os"]),
        requires_wsl=bool(contract_document["requires_wsl"]),
        gpu_name=str(contract_document["gpu_name"]),
    )
    expected_invariants = environment_invariants(contract, observed)
    for name, expected in expected_invariants.items():
        if invariants.get(name) is not expected:
            raise ReceiptValidationError(
                f"{name} contradicts embedded environment evidence"
            )
    if set(invariants) != set(expected_invariants):
        raise ReceiptValidationError("environment invariant inventory mismatch")
    expected_status = "PASS" if all(expected_invariants.values()) else "FAIL"
    if normative.get("status") != expected_status:
        raise ReceiptValidationError(
            "environment status contradicts embedded observations"
        )
    if normative.get("errors") != environment_errors(contract, observed):
        raise ReceiptValidationError(
            "environment errors contradict embedded observations"
        )


def _validate_model_assets_consistency(normative: Mapping[str, object]) -> None:
    """Bind model-asset status to the completeness of exact embedded evidence."""
    if normative.get("status") == "PASS":
        _validate_model_assets_pass_evidence(normative)
        return
    try:
        _validate_model_assets_pass_evidence(normative)
    except ReceiptValidationError:
        return
    raise ReceiptValidationError(
        "model-assets FAIL contradicts complete verified evidence"
    )


def _validate_wave0_gate_consistency(normative: Mapping[str, object]) -> None:
    """Bind the aggregate verdict to the exact approved invariant inventory."""
    from ..gates.wave0 import WAVE0_GATE_INVARIANTS

    invariants = normative.get("invariants")
    errors = normative.get("errors")
    status = normative.get("status")
    interpretation = normative.get("interpretation")
    if not isinstance(invariants, Mapping) or set(invariants) != set(
        WAVE0_GATE_INVARIANTS
    ):
        raise ReceiptValidationError("wave0 gate invariant inventory mismatch")
    expected_status = (
        "PASS"
        if all(invariants.get(name) is True for name in WAVE0_GATE_INVARIANTS)
        and errors == []
        else "FAIL"
    )
    if status != expected_status:
        raise ReceiptValidationError("wave0 gate status contradicts its evidence")
    expected_interpretation = (
        "WAVE0_A3_PASS / WAVE1_NOT_STARTED"
        if expected_status == "PASS"
        else "WAVE0_A3_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    )
    if interpretation != expected_interpretation:
        raise ReceiptValidationError(
            "wave0 gate interpretation contradicts its evidence"
        )
    if expected_status == "PASS":
        parent_receipts = normative.get("parent_receipts")
        exact_comparisons = normative.get("exact_comparisons")
        numerical_comparisons = normative.get("numerical_replay_comparisons")
        expected_attempts = {"primary", "clean_a", "clean_b"}
        expected_stages = {
            "environment",
            "model_assets",
            "model_contract",
            "feasibility_a",
            "feasibility_b",
            "checkpoint_a",
            "checkpoint_b",
        }
        expected_comparisons = {
            "primary_b",
            "clean_a_a",
            "clean_a_b",
            "clean_b_a",
            "clean_b_b",
        }
        if (
            not isinstance(parent_receipts, Mapping)
            or set(parent_receipts) != expected_attempts
            or any(
                not isinstance(values, Mapping) or set(values) != expected_stages
                for values in parent_receipts.values()
            )
        ):
            raise ReceiptValidationError(
                "PASS wave0 gate requires every registered parent receipt"
            )
        if (
            not isinstance(exact_comparisons, Mapping)
            or set(exact_comparisons) != expected_comparisons
        ):
            raise ReceiptValidationError(
                "PASS wave0 gate requires every exact comparison"
            )
        if (
            not isinstance(numerical_comparisons, Mapping)
            or set(numerical_comparisons) != expected_comparisons
        ):
            raise ReceiptValidationError(
                "PASS wave0 gate requires every numerical replay comparison"
            )
        if any(
            not isinstance(value, Mapping)
            or value.get("passed") is not True
            or value.get("errors") != []
            for value in exact_comparisons.values()
        ):
            raise ReceiptValidationError(
                "PASS wave0 gate has a failed exact comparison"
            )
        expected_thresholds = {
            "gradient_rel_tol": 1e-5,
            "gradient_abs_tol": 1e-7,
            "vector_relative_l2_max": 1e-3,
            "vector_cosine_min": 0.99999,
        }
        if any(
            not isinstance(value, Mapping)
            or value.get("passed") is not True
            or value.get("errors") != []
            or value.get("thresholds") != expected_thresholds
            or not _complete_numerical_replay_evidence(value)
            for value in numerical_comparisons.values()
        ):
            raise ReceiptValidationError(
                "PASS wave0 gate has incomplete numerical replay evidence"
            )


def _complete_numerical_replay_evidence(value: Mapping[str, object]) -> bool:
    gradient = value.get("gradient_norm")
    model_updates = value.get("model_updates")
    optimizer_states = value.get("optimizer_states")
    if not isinstance(gradient, Mapping) or set(gradient) != {
        "canonical",
        "replay",
        "rel_tol",
        "abs_tol",
        "passed",
    }:
        return False
    if gradient.get("passed") is not True:
        return False
    if not isinstance(model_updates, Mapping) or set(model_updates) != {
        "detector",
        "backbone",
    }:
        return False
    if not isinstance(optimizer_states, Mapping) or set(optimizer_states) != {
        "detector",
        "backbone",
    }:
        return False
    expected_metric_fields = {
        "canonical_l2",
        "replay_l2",
        "difference_l2",
        "relative_l2",
        "relative_l2_max",
        "cosine",
        "cosine_min",
        "passed",
    }
    for group_name in ("detector", "backbone"):
        model_metric = model_updates.get(group_name)
        optimizer_group = optimizer_states.get(group_name)
        if (
            not isinstance(model_metric, Mapping)
            or set(model_metric) != expected_metric_fields
            or model_metric.get("passed") is not True
            or not isinstance(optimizer_group, Mapping)
            or set(optimizer_group) != {"exp_avg", "exp_avg_sq"}
        ):
            return False
        for moment_name in ("exp_avg", "exp_avg_sq"):
            moment_metric = optimizer_group.get(moment_name)
            if (
                not isinstance(moment_metric, Mapping)
                or set(moment_metric) != expected_metric_fields
                or moment_metric.get("passed") is not True
            ):
                return False
    return True


def _validate_model_assets_pass_evidence(normative: Mapping[str, object]) -> None:
    """Bind complete model-assets evidence to compiled payload/source/HF identities."""

    # Local import avoids a module cycle: the asset verifier publishes through
    # this receipt module, while its loader independently checks tracked pins
    # against compiled constants before returning them.
    from ..models.assets import load_pinned_asset_specs

    specs = load_pinned_asset_specs(
        _SCHEMA_ROOT.parent / "configs" / "models" / "pinned-models.yaml"
    )
    models = normative.get("models")
    transformers = normative.get("transformers")
    if not isinstance(models, Mapping) or not isinstance(transformers, Mapping):
        raise ReceiptValidationError("model-assets evidence must be objects")

    source_files = transformers.get("files")
    expected_source_files = {
        name: {"size": item.size, "sha256": item.sha256}
        for name, item in sorted(specs["rtdetr"].source_files.items())
    }
    if transformers.get("version") != "5.15.0" or source_files != expected_source_files:
        raise ReceiptValidationError(
            "Transformers source files do not match the compiled approved pins"
        )

    for name, spec in sorted(specs.items()):
        model = models.get(name)
        if not isinstance(model, Mapping):
            raise ReceiptValidationError(f"{name} model evidence must be an object")
        expected_files = {
            filename: {"size": item.size, "sha256": item.sha256}
            for filename, item in sorted(spec.files.items())
        }
        if model.get("files") != expected_files:
            raise ReceiptValidationError(
                f"{name} files do not match the compiled approved pins"
            )
        expected_license = {
            "path": "README.md",
            **expected_files["README.md"],
        }
        if model.get("license_evidence") != expected_license:
            raise ReceiptValidationError(
                f"{name} license evidence does not match README.md"
            )
        expected_document_hashes = _APPROVED_MODEL_DOCUMENT_HASHES[name]
        for document_name in ("config", "processor"):
            document = model.get(document_name)
            if (
                not isinstance(document, Mapping)
                or canonical_json_sha256(dict(document))
                != expected_document_hashes[document_name]
            ):
                raise ReceiptValidationError(
                    f"{name} {document_name} differs from the approved payload"
                )

        huggingface = model.get("huggingface_metadata")
        if not isinstance(huggingface, Mapping):
            raise ReceiptValidationError(
                f"{name} Hugging Face metadata must be an object"
            )
        metadata_files = huggingface.get("files")
        inventory = huggingface.get("inventory")
        if (
            huggingface.get("commit_hash") != spec.revision
            or not isinstance(metadata_files, Mapping)
            or not isinstance(inventory, Mapping)
        ):
            raise ReceiptValidationError(
                f"{name} Hugging Face metadata does not match its revision"
            )
        for filename, expected in sorted(spec.files.items()):
            observation = metadata_files.get(filename)
            if not isinstance(observation, Mapping):
                raise ReceiptValidationError(
                    f"{name} {filename} metadata evidence must be an object"
                )
            metadata_path = f".cache/huggingface/download/{filename}.metadata"
            identity = (
                observation.get("metadata_path") == metadata_path
                and observation.get("commit_hash") == spec.revision
                and observation.get("etag") == expected.etag
                and observation.get("blob_id") == expected.blob_id
            )
            if not identity:
                raise ReceiptValidationError(
                    f"{name} {filename} metadata identity differs from its pin"
                )
            inventory_observation = inventory.get(metadata_path)
            expected_inventory = {
                "size": observation.get("size"),
                "sha256": observation.get("sha256"),
            }
            if inventory_observation != expected_inventory:
                raise ReceiptValidationError(
                    f"{name} {filename} metadata inventory is inconsistent"
                )


def _validate_model_contract_consistency(
    normative: Mapping[str, object], metadata: Mapping[str, object]
) -> None:
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

    parent_environment_receipt = normative.get("parent_environment_receipt")
    if not isinstance(parent_environment_receipt, Mapping):
        raise ReceiptValidationError("parent environment receipt must be an object")
    _validate_receipt(
        parent_environment_receipt,
        schema_path=_ALLOWED_SCHEMAS[("environment", 1)],
        require_content_hash=True,
    )
    parent_metadata = parent_environment_receipt.get("metadata")
    parent_normative = parent_environment_receipt.get("normative")
    if not isinstance(parent_metadata, Mapping) or not isinstance(
        parent_normative, Mapping
    ):
        raise ReceiptValidationError("parent environment receipt is incomplete")
    if parent_metadata.get("run_id") != metadata.get("run_id"):
        raise ReceiptValidationError("parent environment run_id mismatch")
    if parent_normative.get("status") != "PASS":
        raise ReceiptValidationError("parent environment receipt must be PASS")
    if normative.get("environment_receipt_sha256") != _stored_receipt_sha256(
        parent_environment_receipt
    ):
        raise ReceiptValidationError("parent environment receipt digest mismatch")
    if normative.get("environment_receipt_content_sha256") != parent_metadata.get(
        "receipt_content_sha256"
    ):
        raise ReceiptValidationError("parent environment content hash mismatch")

    config = normative.get("config")
    shapes = normative.get("observed_shapes")
    labeled_shapes = normative.get("labeled_observed_shapes")
    class_modules = normative.get("observed_class_modules")
    processor = normative.get("processor")
    environment = normative.get("environment")
    invariants = normative.get("invariants")
    if not all(
        isinstance(value, Mapping)
        for value in (
            config,
            shapes,
            labeled_shapes,
            class_modules,
            processor,
            environment,
            invariants,
        )
    ):
        raise ReceiptValidationError("model-contract evidence must be objects")
    assert isinstance(config, Mapping)
    assert isinstance(shapes, Mapping)
    assert isinstance(labeled_shapes, Mapping)
    assert isinstance(class_modules, Mapping)
    assert isinstance(processor, Mapping)
    assert isinstance(environment, Mapping)
    assert isinstance(invariants, Mapping)

    decoder_layers = config.get("decoder_layers")
    canonical_environment = {
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
        "os": "Linux",
        "wsl": True,
        "container_image_digest": (
            "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
        ),
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
        "data_root_unset": True,
        "status": "PASS",
        "errors": [],
    }
    logits_shape = shapes.get("logits")
    decoder_heads = class_modules.get("decoder_class_heads")
    denoising = class_modules.get("denoising_class_embed")
    encoder = class_modules.get("encoder_score_head")
    if (
        not isinstance(decoder_heads, list)
        or not isinstance(denoising, Mapping)
        or not isinstance(encoder, Mapping)
    ):
        raise ReceiptValidationError("class-module evidence is incomplete")
    expected_paths = [
        f"model.model.decoder.class_embed[{index}]"
        for index in range(decoder_layers if type(decoder_layers) is int else 0)
    ]

    def shape_ends_in_four(value: object, *, rank: int | None = None) -> bool:
        return (
            isinstance(value, list)
            and (rank is None or len(value) == rank)
            and bool(value)
            and value[-1] == 4
        )

    def every_shape_ends_in_four(value: object) -> bool:
        return (
            isinstance(value, list)
            and bool(value)
            and all(shape_ends_in_four(shape) for shape in value)
        )

    try:
        labeled_loss = float.fromhex(str(normative.get("labeled_loss_hex")))
    except ValueError:
        labeled_loss = math.nan
    labeled_loss_finite_scalar = labeled_shapes.get("loss") == [] and math.isfinite(
        labeled_loss
    )
    decoder_heads_four = (
        len(decoder_heads) == decoder_layers
        and [head.get("path") for head in decoder_heads] == expected_paths
        and all(
            isinstance(head, Mapping)
            and head.get("replaced") is True
            and head.get("out_features") == 4
            and type(head.get("in_features")) is int
            and head["in_features"] > 0
            and isinstance(head.get("bias"), bool)
            and isinstance(head.get("device"), str)
            and bool(head["device"])
            and isinstance(head.get("dtype"), str)
            and bool(head["dtype"])
            for head in decoder_heads
        )
    )
    denoising_four = (
        denoising.get("path") == "model.model.denoising_class_embed"
        and denoising.get("replaced") is True
        and denoising.get("num_embeddings") == 5
        and denoising.get("padding_idx") == 4
        and type(denoising.get("embedding_dim")) is int
        and denoising["embedding_dim"] > 0
        and isinstance(denoising.get("device"), str)
        and bool(denoising["device"])
        and isinstance(denoising.get("dtype"), str)
        and bool(denoising["dtype"])
    )
    encoder_four = (
        encoder.get("path") == "model.model.enc_score_head"
        and encoder.get("replaced") is True
        and encoder.get("out_features") == 4
        and type(encoder.get("in_features")) is int
        and encoder["in_features"] > 0
        and isinstance(encoder.get("bias"), bool)
        and isinstance(encoder.get("device"), str)
        and bool(encoder["device"])
        and isinstance(encoder.get("dtype"), str)
        and bool(encoder["dtype"])
    )
    exact_mappings = (
        class_modules.get("num_labels") == 4
        and class_modules.get("id2label")
        == {"0": "D00", "1": "D10", "2": "D20", "3": "D40"}
        and class_modules.get("label2id") == {"D00": 0, "D10": 1, "D20": 2, "D40": 3}
    )
    reset_order_proven = (
        class_modules.get("reset_seed") == 17
        and class_modules.get("replacement_order")
        == [
            *expected_paths,
            "model.model.denoising_class_embed",
            "model.model.enc_score_head",
        ]
        and class_modules.get("deterministic_replay") is True
    )
    label_free_class_shapes = (
        shape_ends_in_four(shapes.get("logits"), rank=3)
        and shape_ends_in_four(shapes.get("intermediate_logits"), rank=4)
        and shape_ends_in_four(shapes.get("enc_outputs_class"), rank=3)
        and shape_ends_in_four(shapes.get("enc_topk_logits"), rank=3)
    )
    labeled_class_shapes = (
        shape_ends_in_four(labeled_shapes.get("logits"), rank=3)
        and shape_ends_in_four(labeled_shapes.get("intermediate_logits"), rank=4)
        and shape_ends_in_four(labeled_shapes.get("enc_outputs_class"), rank=3)
        and shape_ends_in_four(labeled_shapes.get("enc_topk_logits"), rank=3)
        and every_shape_ends_in_four(labeled_shapes.get("decoder_auxiliary_logits"))
        and every_shape_ends_in_four(labeled_shapes.get("encoder_auxiliary_logits"))
        and every_shape_ends_in_four(labeled_shapes.get("denoising_auxiliary_logits"))
    )
    expected_evidence: dict[str, bool] = {
        "config_decoder_layers_3": decoder_layers == 3,
        "config_num_queries_300": config.get("num_queries") == 300,
        "config_num_labels_4": config.get("num_labels") == 4,
        "class_reset_preserves_structure": class_modules.get("structure_preserved")
        is True,
        "decoder_layers_at_least_two": (
            type(decoder_layers) is int and decoder_layers >= 2
        ),
        "decoder_class_heads_four_channels": decoder_heads_four,
        "denoising_class_embed_five_rows_padding_four": denoising_four,
        "encoder_score_head_four_channels": encoder_four,
        "exact_rdd_label_mappings": exact_mappings,
        "four_class_head_reset_seed_17": reset_order_proven,
        "four_class_reset_rng_order_seed_17": reset_order_proven,
        "pretrained_coco_head_rows_not_reused": class_modules.get(
            "pretrained_class_rows_reused"
        )
        is False,
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
        "intermediate_logits_four_channels": (
            shape_ends_in_four(shapes.get("intermediate_logits"), rank=4)
            and shape_ends_in_four(labeled_shapes.get("intermediate_logits"), rank=4)
        ),
        "enc_outputs_class_four_channels": (
            shape_ends_in_four(shapes.get("enc_outputs_class"), rank=3)
            and shape_ends_in_four(labeled_shapes.get("enc_outputs_class"), rank=3)
        ),
        "enc_topk_logits_four_channels": (
            shape_ends_in_four(shapes.get("enc_topk_logits"), rank=3)
            and shape_ends_in_four(labeled_shapes.get("enc_topk_logits"), rank=3)
        ),
        "decoder_auxiliary_logits_four_channels": every_shape_ends_in_four(
            labeled_shapes.get("decoder_auxiliary_logits")
        ),
        "encoder_auxiliary_logits_four_channels": every_shape_ends_in_four(
            labeled_shapes.get("encoder_auxiliary_logits")
        ),
        "denoising_auxiliary_logits_four_channels": every_shape_ends_in_four(
            labeled_shapes.get("denoising_auxiliary_logits")
        ),
        "no_reachable_non_four_class_logits": (
            label_free_class_shapes and labeled_class_shapes
        ),
        "labeled_forward_finite_scalar_loss": labeled_loss_finite_scalar,
        "label_free_model_call": label_free_class_shapes,
        "labeled_model_call": labeled_class_shapes and labeled_loss_finite_scalar,
        "synthetic_targets_only": normative.get("synthetic_target_sha256")
        == _APPROVED_MODEL_CONTRACT_ASSET_HASHES["synthetic_target_sha256"],
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
        "exact_scipy": environment.get("scipy") == "1.18.0",
    }
    torch_execution = environment.get("torch_execution")
    parent_observed = parent_normative.get("observed")
    if not isinstance(parent_observed, Mapping):
        raise ReceiptValidationError("parent environment observation is missing")
    for field in _APPROVED_ENVIRONMENT_CONTRACT:
        if field in {"canonical_os", "requires_wsl"}:
            continue
        if environment.get(field) != parent_observed.get(field):
            raise ReceiptValidationError(
                f"live {field} differs from parent environment receipt"
            )
    for field in (
        "gpu_uuid",
        "driver",
        "os",
        "wsl",
        "runtime_image_digest",
        "data_root_unset",
    ):
        if environment.get(field) != parent_observed.get(field):
            raise ReceiptValidationError(
                f"live {field} differs from parent environment receipt"
            )
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

    exact_a2_invariants = {
        "class_reset_preserves_structure",
        "decoder_class_heads_four_channels",
        "decoder_auxiliary_logits_four_channels",
        "denoising_auxiliary_logits_four_channels",
        "denoising_class_embed_five_rows_padding_four",
        "enc_outputs_class_four_channels",
        "enc_topk_logits_four_channels",
        "encoder_auxiliary_logits_four_channels",
        "encoder_score_head_four_channels",
        "exact_rdd_label_mappings",
        "four_class_head_reset_seed_17",
        "four_class_reset_rng_order_seed_17",
        "intermediate_logits_four_channels",
        "label_free_model_call",
        "labeled_forward_finite_scalar_loss",
        "labeled_model_call",
        "no_reachable_non_four_class_logits",
        "pretrained_coco_head_rows_not_reused",
        "synthetic_targets_only",
    }
    for invariant_name, evidence_passed in expected_evidence.items():
        if (
            invariant_name in exact_a2_invariants
            and invariants.get(invariant_name) is not evidence_passed
        ):
            raise ReceiptValidationError(
                f"{invariant_name} contradicts embedded model-contract evidence"
            )
        if invariants.get(invariant_name) is True and evidence_passed is not True:
            raise ReceiptValidationError(
                f"{invariant_name} contradicts embedded model-contract evidence"
            )


def _validate_feasibility_consistency(
    normative: Mapping[str, object],
    metadata: Mapping[str, object],
    *,
    schema_version: object,
) -> None:
    """Reject feasibility claims that contradict their embedded observations."""
    if schema_version != 3:
        raise ReceiptValidationError("A6 requires feasibility schema version 3")
    runtime = normative.get("runtime")
    recipe = normative.get("recipe")
    shapes = normative.get("observed_shapes")
    vram = normative.get("vram")
    timing = normative.get("timing")
    step = normative.get("step")
    checkpoint = normative.get("checkpoint")
    synthetic_labels = normative.get("synthetic_labels")
    environment = normative.get("environment")
    parent_model_contract = normative.get("parent_model_contract")
    invariants = normative.get("invariants")
    state_digests = normative.get("state_digests")
    comparison = normative.get("exact_comparison")
    allowlisted_backward = normative.get("allowlisted_backward")
    deterministic_attention = normative.get("deterministic_attention")
    parameter_inventory = normative.get("parameter_inventory")
    update_groups = normative.get("update_groups")
    if not all(
        isinstance(value, Mapping)
        for value in (
            runtime,
            recipe,
            shapes,
            vram,
            timing,
            step,
            checkpoint,
            synthetic_labels,
            environment,
            parent_model_contract,
            invariants,
            state_digests,
            comparison,
            allowlisted_backward,
            deterministic_attention,
            update_groups,
        )
    ) or not isinstance(parameter_inventory, list):
        raise ReceiptValidationError("feasibility evidence must be objects")
    assert isinstance(runtime, Mapping)
    assert isinstance(recipe, Mapping)
    assert isinstance(shapes, Mapping)
    assert isinstance(vram, Mapping)
    assert isinstance(timing, Mapping)
    assert isinstance(step, Mapping)
    assert isinstance(checkpoint, Mapping)
    assert isinstance(synthetic_labels, Mapping)
    assert isinstance(environment, Mapping)
    assert isinstance(parent_model_contract, Mapping)
    assert isinstance(invariants, Mapping)
    assert isinstance(state_digests, Mapping)
    assert isinstance(comparison, Mapping)
    assert isinstance(allowlisted_backward, Mapping)
    assert isinstance(deterministic_attention, Mapping)
    assert isinstance(parameter_inventory, list)
    assert isinstance(update_groups, Mapping)

    _validate_receipt(
        parent_model_contract,
        schema_path=_ALLOWED_SCHEMAS[("model-contract", 1)],
        require_content_hash=True,
    )
    parent_normative = parent_model_contract.get("normative")
    parent_metadata = parent_model_contract.get("metadata")
    if not isinstance(parent_normative, Mapping):
        raise ReceiptValidationError("parent model-contract normative is missing")
    if not isinstance(parent_metadata, Mapping) or parent_metadata.get(
        "run_id"
    ) != metadata.get("run_id"):
        raise ReceiptValidationError("parent model-contract run_id mismatch")
    parent_invariants = parent_normative.get("invariants")
    if (
        parent_normative.get("status") != "PASS"
        or parent_normative.get("errors") != []
        or not isinstance(parent_invariants, Mapping)
        or not parent_invariants
        or any(value is not True for value in parent_invariants.values())
    ):
        raise ReceiptValidationError("parent model-contract must be a complete PASS")
    if normative.get("model_contract_receipt_sha256") != _stored_receipt_sha256(
        parent_model_contract
    ):
        raise ReceiptValidationError("parent model-contract receipt digest mismatch")
    for name in (
        "model_sha256",
        "config_sha256",
        "source_sha256",
        "processor_sha256",
        "fixture_sha256",
        "loss_source_sha256",
        "synthetic_target_sha256",
    ):
        if normative.get(name) != parent_normative.get(name):
            raise ReceiptValidationError(
                f"{name} differs from the parent model-contract receipt"
            )
    parent_environment = parent_normative.get("environment")
    if not isinstance(parent_environment, Mapping):
        raise ReceiptValidationError("parent model-contract environment is missing")
    expected_parent_environment_sha256 = canonical_json_sha256(dict(parent_environment))

    observed_environment = environment.get("observed")
    selected_cuda = environment.get("selected_cuda")
    if not isinstance(observed_environment, Mapping) or not isinstance(
        selected_cuda, Mapping
    ):
        raise ReceiptValidationError("feasibility environment evidence is incomplete")
    if normative.get("environment_sha256") != canonical_json_sha256(dict(environment)):
        raise ReceiptValidationError("feasibility environment digest mismatch")
    if (
        normative.get("parent_environment_sha256") != expected_parent_environment_sha256
        or environment.get("parent_environment_sha256")
        != expected_parent_environment_sha256
    ):
        raise ReceiptValidationError(
            "parent model-contract environment digest mismatch"
        )
    for field in (
        "schema_version",
        "python",
        "uv",
        "scipy",
        "torch",
        "torchvision",
        "transformers",
        "pycocotools",
        "cuda_runtime",
        "gpu_name",
        "gpu_uuid",
        "driver",
        "os",
        "wsl",
        "container_image_digest",
        "runtime_image_digest",
        "tf32",
        "deterministic_algorithms",
        "bf16_supported",
        "data_root_unset",
    ):
        if observed_environment.get(field) != parent_environment.get(field):
            raise ReceiptValidationError(
                f"live {field} differs from the parent model-contract environment"
            )
    if normative.get("probe_sha256") != _training_probe_sha256():
        raise ReceiptValidationError(
            "training probe differs from the receipt source hash"
        )

    from ..environment import EnvironmentContract, environment_invariants

    contract = EnvironmentContract(
        python=str(_APPROVED_ENVIRONMENT_CONTRACT["python"]),
        uv=str(_APPROVED_ENVIRONMENT_CONTRACT["uv"]),
        scipy=str(_APPROVED_ENVIRONMENT_CONTRACT["scipy"]),
        torch=str(_APPROVED_ENVIRONMENT_CONTRACT["torch"]),
        torchvision=str(_APPROVED_ENVIRONMENT_CONTRACT["torchvision"]),
        transformers=str(_APPROVED_ENVIRONMENT_CONTRACT["transformers"]),
        cuda_runtime=str(_APPROVED_ENVIRONMENT_CONTRACT["cuda_runtime"]),
        pycocotools=str(_APPROVED_ENVIRONMENT_CONTRACT["pycocotools"]),
        container_image_digest=str(
            _APPROVED_ENVIRONMENT_CONTRACT["container_image_digest"]
        ),
        tf32=bool(_APPROVED_ENVIRONMENT_CONTRACT["tf32"]),
        deterministic_algorithms=bool(
            _APPROVED_ENVIRONMENT_CONTRACT["deterministic_algorithms"]
        ),
        bf16_supported=bool(_APPROVED_ENVIRONMENT_CONTRACT["bf16_supported"]),
        canonical_os=str(_APPROVED_ENVIRONMENT_CONTRACT["canonical_os"]),
        requires_wsl=bool(_APPROVED_ENVIRONMENT_CONTRACT["requires_wsl"]),
        gpu_name=str(_APPROVED_ENVIRONMENT_CONTRACT["gpu_name"]),
    )
    live_environment_invariants = environment_invariants(contract, observed_environment)
    selected_uuid = _normalized_gpu_uuid(selected_cuda.get("selected_uuid"))
    observed_uuid = _normalized_gpu_uuid(observed_environment.get("gpu_uuid"))
    canonical_environment = (
        all(live_environment_invariants.values())
        and selected_cuda.get("cuda_available") is True
        and type(selected_cuda.get("device_count")) is int
        and selected_cuda.get("device_count", 0) >= 1
        and selected_cuda.get("selected_index") == 0
        and selected_cuda.get("selected_device") == "cuda:0"
        and selected_cuda.get("selected_name")
        == _APPROVED_ENVIRONMENT_CONTRACT["gpu_name"]
        and selected_uuid is not None
        and selected_uuid == observed_uuid
    )

    ordered_losses = normative.get("ordered_losses")
    if not isinstance(ordered_losses, list):
        raise ReceiptValidationError("ordered_losses must be an array")
    expected_loss_hex = [
        value.hex() for value in ordered_losses if isinstance(value, float)
    ]
    if len(expected_loss_hex) != len(ordered_losses):
        expected_loss_hex = [float(value).hex() for value in ordered_losses]
    if (
        allowlisted_backward.get("operation_identifier") != _A3_BACKWARD_OPERATION
        or allowlisted_backward.get("expected_count") != 9
        or allowlisted_backward.get("observed_count") != 9
        or allowlisted_backward.get("strict_mode_restored") is not True
        or allowlisted_backward.get("source_hash_rule") != _A4_BACKWARD_SOURCE_HASH_RULE
        or allowlisted_backward.get("source_sha256") != _A4_BACKWARD_SOURCE_SHA256
    ):
        raise ReceiptValidationError("allowlisted backward identity mismatch")
    if dict(deterministic_attention) != _A6_DETERMINISTIC_ATTENTION:
        raise ReceiptValidationError("deterministic attention identity mismatch")
    raw_warnings = allowlisted_backward.get("raw_warnings")
    warning_categories = allowlisted_backward.get("warning_categories")
    operation_identifiers = allowlisted_backward.get("operation_identifiers")
    if (
        not isinstance(raw_warnings, list)
        or len(raw_warnings) != 9
        or any(
            not isinstance(message, str)
            or not message.startswith(
                f"{_A3_BACKWARD_OPERATION} does not have a deterministic implementation"
            )
            for message in raw_warnings
        )
        or warning_categories != ["UserWarning"] * 9
        or operation_identifiers != [_A3_BACKWARD_OPERATION] * 9
    ):
        raise ReceiptValidationError("allowlisted backward warning inventory mismatch")

    if not parameter_inventory or len(parameter_inventory) != step.get(
        "trainable_parameter_count"
    ):
        raise ReceiptValidationError("parameter inventory count mismatch")
    parameter_names: list[str] = []
    observed_groups: set[str] = set()
    for entry in parameter_inventory:
        if not isinstance(entry, Mapping):
            raise ReceiptValidationError("parameter inventory entry must be an object")
        name = entry.get("name")
        group_name = entry.get("group_name")
        shape = entry.get("shape")
        dtype = entry.get("dtype")
        if (
            not isinstance(name, str)
            or not name
            or group_name not in {"detector", "backbone"}
            or not isinstance(shape, list)
            or any(type(item) is not int or item < 0 for item in shape)
            or not isinstance(dtype, str)
            or not dtype
        ):
            raise ReceiptValidationError("parameter inventory entry is invalid")
        parameter_names.append(name)
        observed_groups.add(str(group_name))
    if len(set(parameter_names)) != len(parameter_names) or observed_groups != {
        "detector",
        "backbone",
    }:
        raise ReceiptValidationError("parameter inventory is duplicate or incomplete")

    if set(update_groups) != {"detector", "backbone"}:
        raise ReceiptValidationError("update group inventory mismatch")
    for group_name, value in update_groups.items():
        if (
            not isinstance(value, Mapping)
            or set(value) != {"l2_norm"}
            or type(value.get("l2_norm")) not in (int, float)
            or not math.isfinite(float(value["l2_norm"]))
            or float(value["l2_norm"]) <= 0.0
        ):
            raise ReceiptValidationError(f"{group_name} update norm is invalid")

    exact_state_digests = {
        name: state_digests.get(name)
        for name in ("scheduler", "scaler", "rng", "sampler")
    }
    expected_optimizer_groups = [
        {
            "group_name": "detector",
            "learning_rate": 1e-4,
            "weight_decay": 1e-4,
        },
        {
            "group_name": "backbone",
            "learning_rate": 1e-5,
            "weight_decay": 1e-4,
        },
    ]
    model_state_inventory = comparison.get("model_state_inventory")
    if not isinstance(model_state_inventory, list) or not model_state_inventory:
        raise ReceiptValidationError("model state inventory is incomplete")
    model_state_names = [
        entry.get("name") if isinstance(entry, Mapping) else None
        for entry in model_state_inventory
    ]
    if any(not isinstance(name, str) or not name for name in model_state_names) or len(
        set(model_state_names)
    ) != len(model_state_names):
        raise ReceiptValidationError("model state inventory is invalid")
    if not all(
        isinstance(entry, Mapping)
        and set(entry) == {"name", "shape", "dtype", "trainable"}
        and isinstance(entry.get("shape"), list)
        and all(type(item) is int and item >= 0 for item in entry["shape"])
        and isinstance(entry.get("dtype"), str)
        and bool(entry.get("dtype"))
        and type(entry.get("trainable")) is bool
        for entry in model_state_inventory
    ):
        raise ReceiptValidationError("model state inventory entry is invalid")
    if comparison.get("rule") != "wave0-a3-exact-replay-sha256-v1":
        raise ReceiptValidationError("exact comparison rule mismatch")
    if comparison.get("parameter_digest_before") != step.get("parameter_digest_before"):
        raise ReceiptValidationError("exact comparison parameter digest mismatch")
    if comparison.get("parameter_inventory") != parameter_inventory:
        raise ReceiptValidationError("exact comparison parameter inventory mismatch")
    if comparison.get("ordered_loss_hex") != expected_loss_hex:
        raise ReceiptValidationError("exact comparison ordered losses mismatch")
    if comparison.get("optimizer_groups") != expected_optimizer_groups:
        raise ReceiptValidationError("exact comparison optimizer groups mismatch")
    if comparison.get("sampler_order_digest") != state_digests.get("sampler"):
        raise ReceiptValidationError("exact comparison sampler digest mismatch")
    if comparison.get("state_digests") != exact_state_digests:
        raise ReceiptValidationError("exact comparison state digests mismatch")
    if comparison.get("allowlisted_backward") != allowlisted_backward:
        raise ReceiptValidationError("exact comparison warning evidence mismatch")
    if comparison.get("deterministic_attention") != deterministic_attention:
        raise ReceiptValidationError(
            "exact comparison deterministic attention mismatch"
        )
    if (
        comparison.get("checkpoint_epoch") != 0
        or comparison.get("checkpoint_step") != 1
    ):
        raise ReceiptValidationError("exact comparison progress mismatch")
    if not isinstance(comparison.get("scheduler_state_before_sha256"), str):
        raise ReceiptValidationError("scheduler-before digest is missing")
    input_digests = comparison.get("semantic_input_digests")
    if not isinstance(input_digests, Mapping) or dict(input_digests) != {
        "fixture_sha256": normative.get("fixture_sha256"),
        "synthetic_target_sha256": normative.get("synthetic_target_sha256"),
    }:
        raise ReceiptValidationError("exact comparison semantic input digests mismatch")
    comparison_preimage = {
        name: value
        for name, value in comparison.items()
        if name not in {"rule", "sha256"}
    }
    if comparison.get("sha256") != canonical_json_sha256(comparison_preimage):
        raise ReceiptValidationError("exact comparison digest mismatch")

    peak_allocated = vram.get("peak_allocated_bytes")
    peak_reserved = vram.get("peak_reserved_bytes")
    limit = vram.get("allocated_limit_bytes")
    if any(
        type(value) is not int or value < 0
        for value in (peak_allocated, peak_reserved, limit)
    ):
        raise ReceiptValidationError("VRAM observations must be non-negative integers")
    assert isinstance(peak_allocated, int)
    assert isinstance(peak_reserved, int)
    assert isinstance(limit, int)
    if (
        invariants.get("peak_allocated_vram_within_22_gib") is True
        and peak_allocated > limit
    ):
        raise ReceiptValidationError(
            "peak_allocated_vram_within_22_gib contradicts embedded feasibility evidence"
        )
    if peak_reserved < peak_allocated:
        raise ReceiptValidationError("reserved VRAM must cover allocated VRAM")
    for name, value in timing.items():
        if type(value) not in (int, float) or value < 0:
            raise ReceiptValidationError(f"timing {name} must be non-negative")

    parameter_update_observed = (
        step.get("parameter_digest_rule")
        == "ordered-trainable-named-parameters-sha256-v1"
        and type(step.get("trainable_parameter_count")) is int
        and step.get("trainable_parameter_count", 0) > 0
        and step.get("parameter_digest_before") != step.get("parameter_digest_after")
    )
    attention_before = deterministic_attention.get("before")
    attention_inside = deterministic_attention.get("inside")
    attention_after = deterministic_attention.get("after")
    attention_sources = deterministic_attention.get("source_sha256")
    expected_evidence = {
        "parameter_changed": parameter_update_observed,
        "adamw_update": parameter_update_observed
        and recipe.get("optimizer") == "AdamW"
        and all(
            isinstance(update_groups.get(name), Mapping)
            and float(update_groups[name].get("l2_norm", 0.0)) > 0.0
            for name in ("detector", "backbone")
        ),
        "allowlisted_backward_verified": runtime.get("allowlisted_grid_sample_backward")
        is True
        and allowlisted_backward.get("source_hash_rule")
        == _A4_BACKWARD_SOURCE_HASH_RULE
        and dict(allowlisted_backward.get("source_sha256", {}))
        == _A4_BACKWARD_SOURCE_SHA256
        and allowlisted_backward.get("observed_count") == 9,
        "batch_size_two": shapes.get("pixel_values") == [2, 3, 640, 640]
        and shapes.get("pixel_mask") == [2, 640, 640],
        "bf16_autocast": runtime.get("bf16_autocast_enabled") is True,
        "bf16_supported": runtime.get("bf16_supported") is True,
        "checkpoint_content_verified": checkpoint.get("file_sha256")
        == normative.get("checkpoint_sha256")
        and checkpoint.get("verified_file_sha256") == normative.get("checkpoint_sha256")
        and checkpoint.get("input_digests_verified") is True,
        "checkpoint_round_trip": checkpoint.get("state_sha256_before_save")
        == normative.get("checkpoint_state_sha256")
        and checkpoint.get("state_sha256_after_load")
        == normative.get("checkpoint_state_sha256")
        and checkpoint.get("live_model_state_sha256_after_step")
        == state_digests.get("model")
        and checkpoint.get("state_digests_before_save") == state_digests
        and checkpoint.get("state_digests_after_load") == state_digests,
        "cublas_workspace_configured": runtime.get("cublas_workspace_config")
        == ":4096:8",
        "cudnn_benchmark_disabled": runtime.get("cudnn_benchmark") is False,
        "canonical_environment": canonical_environment
        and runtime.get("device") == selected_cuda.get("selected_device"),
        "deterministic_algorithms": runtime.get("deterministic_algorithms") is True
        and runtime.get("deterministic_debug_mode") == 2,
        "deterministic_attention_math_only": (
            deterministic_attention.get("attn_implementation") == "sdpa"
            and deterministic_attention.get("backend") == "MATH"
            and isinstance(attention_inside, Mapping)
            and dict(attention_inside) == _A6_DETERMINISTIC_ATTENTION["inside"]
        ),
        "deterministic_attention_scope_verified": (
            deterministic_attention.get("scope") == "labeled_forward_through_backward"
        ),
        "deterministic_attention_source_verified": (
            deterministic_attention.get("source_hash_rule")
            == "python-source-lf-normalized-sha256-v1"
            and isinstance(attention_sources, Mapping)
            and dict(attention_sources) == _A6_DETERMINISTIC_ATTENTION["source_sha256"]
        ),
        "deterministic_attention_backend_restored": (
            isinstance(attention_before, Mapping)
            and dict(attention_before) == _A6_DETERMINISTIC_ATTENTION["before"]
            and isinstance(attention_after, Mapping)
            and dict(attention_after) == dict(attention_before)
            and deterministic_attention.get("restored") is True
        ),
        "exact_scipy": observed_environment.get("scipy") == "1.18.0",
        "finite_gradients": step.get("finite_gradients") is True,
        "finite_loss": step.get("finite_loss") is True
        and bool(ordered_losses)
        and all(
            type(value) in (int, float) and math.isfinite(value)
            for value in ordered_losses
        )
        and step.get("loss_hex") == float(ordered_losses[0]).hex(),
        "gradient_clip_0_1": recipe.get("gradient_clip_norm") == 0.1,
        "peak_allocated_vram_within_22_gib": peak_allocated <= limit
        and limit == 22 * 1024**3,
        "resume_state_verified": normative.get("resume_verified") is True
        and checkpoint.get("state_digests_after_restore") == state_digests,
        "seed_17": runtime.get("seed") == 17 and recipe.get("seed") == 17,
        "strict_deterministic_error_mode_restored": runtime.get(
            "strict_deterministic_error_mode_restored"
        )
        is True
        and allowlisted_backward.get("strict_mode_restored") is True,
        "synthetic_labels_only": recipe.get("fixture_set") == "wave0-rtdetr-contract"
        and dict(synthetic_labels)
        == {
            "item_ids": ["wide-gradient", "tall-checker"],
            "class_labels": [[0], [3]],
            "boxes_per_image": [1, 1],
            "source": "tracked-synthetic-fixture-geometry-v1",
        },
        "tf32_disabled": runtime.get("tf32") is False
        and runtime.get("cuda_matmul_allow_tf32") is False
        and runtime.get("cudnn_allow_tf32") is False,
    }
    exact_recipe = {
        "seed": 17,
        "batch_size": 2,
        "optimizer": "AdamW",
        "detector_learning_rate": 1e-4,
        "backbone_learning_rate": 1e-5,
        "weight_decay": 1e-4,
        "gradient_clip_norm": 0.1,
        "fixture_set": "wave0-rtdetr-contract",
    }
    if dict(recipe) != exact_recipe:
        if recipe.get("gradient_clip_norm") != 0.1:
            raise ReceiptValidationError(
                "gradient_clip_0_1 contradicts embedded feasibility evidence"
            )
        raise ReceiptValidationError("training recipe differs from the approved smoke")
    if set(invariants) != set(expected_evidence):
        raise ReceiptValidationError("feasibility invariant inventory mismatch")
    for name, expected in expected_evidence.items():
        if invariants.get(name) is not expected:
            raise ReceiptValidationError(
                f"{name} contradicts embedded feasibility evidence"
            )
    expected_errors = sorted(
        name for name, passed in expected_evidence.items() if passed is not True
    )
    expected_status = "PASS" if not expected_errors else "FAIL"
    if normative.get("status") != expected_status:
        raise ReceiptValidationError("feasibility status contradicts embedded evidence")
    if normative.get("errors") != expected_errors:
        raise ReceiptValidationError("feasibility errors contradict embedded evidence")


def _normalized_gpu_uuid(value: object) -> str | None:
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


def _training_probe_sha256() -> str:
    project_root = _SCHEMA_ROOT.parent
    source_files = (
        project_root
        / "src"
        / "vision_active_learning_loop"
        / "probes"
        / "training_feasibility.py",
        project_root
        / "src"
        / "vision_active_learning_loop"
        / "training"
        / "checkpoint_io.py",
    )
    observations = {
        path.relative_to(project_root)
        .as_posix(): hashlib.sha256(path.read_text(encoding="utf-8").encode("utf-8"))
        .hexdigest()
        for path in source_files
    }
    return canonical_json_sha256(observations)


def _is_prefixed_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None
    )


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
                _validate_schema(member, additional, f"{location}.{name}", root_schema)
    elif schema_type == "array":
        if not isinstance(value, list):
            raise ReceiptValidationError(f"{location} must be an array")
        minimum = schema.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            raise ReceiptValidationError(f"{location} has too few items")
        items = schema.get("items")
        if isinstance(items, Mapping):
            for index, member in enumerate(value):
                _validate_schema(member, items, f"{location}[{index}]", root_schema)
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


def _unlink_staging_best_effort(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
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
