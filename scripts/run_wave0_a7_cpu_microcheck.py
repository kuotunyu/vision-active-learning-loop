"""Production-only CPU contract checks for Wave 0 A7 launch orchestration."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import struct
import sys
import tempfile
from collections.abc import Mapping, Sequence
from itertools import combinations
from pathlib import Path

SOURCE_PATHS = (
    "scripts/start_wave0_a7.ps1",
    "scripts/run_wave0_a7_cpu_microcheck.py",
    "scripts/run_wave0_a7.ps1",
    "src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py",
    "src/vision_active_learning_loop/diagnostics/tensor_evidence.py",
    "src/vision_active_learning_loop/artifacts/receipts.py",
    "schemas/grid-sample-attribution-receipt.schema.json",
)
_MANIFEST_PATH = "diagnose grid-sample-attribution"
_MANIFEST_TARGET = (
    "vision_active_learning_loop.diagnostics.grid_sample_attribution:main"
)


class MicrocheckError(ValueError):
    """Raised when the production-only A7 CPU contract is not closed."""


def run_microcheck(
    workspace_root: Path, source_inventory_path: Path
) -> dict[str, object]:
    """Verify reviewed sources and lazy A7 command discovery on CPU only."""
    if os.environ.get("VAL_DATA_ROOT"):
        raise MicrocheckError("VAL_DATA_ROOT must be unset")
    workspace = Path(workspace_root).resolve(strict=True)
    if not workspace.is_dir() or _is_link_or_junction(Path(workspace_root)):
        raise MicrocheckError("workspace root must be a safe directory")
    inventory_path = Path(source_inventory_path)
    _require_safe_regular_file(inventory_path)
    inventory = _load_inventory(inventory_path)
    _verify_source_inventory(workspace, inventory)

    from vision_active_learning_loop.cli_manifest import build_manifest

    manifest = build_manifest(workspace / "src")
    try:
        target = manifest[_MANIFEST_PATH]
    except KeyError as error:
        raise MicrocheckError("A7 command is missing from lazy manifest") from error
    if target != _MANIFEST_TARGET:
        raise MicrocheckError("A7 command target is invalid")

    import torch

    from vision_active_learning_loop.artifacts import receipts as receipt_validation
    from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
    from vision_active_learning_loop.diagnostics import grid_sample_attribution
    from vision_active_learning_loop.diagnostics.tensor_evidence import (
        TensorEvidenceError,
        canonical_tensor_bytes,
        decode_snapshot,
        encode_snapshot,
    )

    if grid_sample_attribution.main is None:
        raise MicrocheckError("A7 diagnostic entry point is unavailable")
    canonical_dtypes = _verify_canonical_dtypes(torch, canonical_tensor_bytes)
    snapshot = _verify_snapshot_contract(
        torch,
        grid_sample_attribution.OPERATION_IDS,
        encode_snapshot,
        decode_snapshot,
        TensorEvidenceError,
    )
    receipt_kinds, classifier_statuses = _verify_receipt_and_classifier_contracts(
        workspace,
        inventory,
        grid_sample_attribution,
        canonical_json_sha256,
        receipt_validation,
    )
    cuda_initialized = bool(torch.cuda.is_initialized())
    if cuda_initialized:
        raise MicrocheckError("CPU micro-check initialized CUDA")
    return {
        "schema_version": 1,
        "status": "RECORDED",
        "source_commit": inventory["source_commit"],
        "source_inventory_sha256": _sha256_file(inventory_path),
        "source_files": list(inventory["files"]),
        "manifest_target": target,
        "canonical_dtypes": canonical_dtypes,
        **snapshot,
        "receipt_kinds": receipt_kinds,
        "classifier_statuses": classifier_statuses,
        "cuda_initialized": cuda_initialized,
    }


def _verify_canonical_dtypes(torch, canonical_tensor_bytes) -> list[str]:
    expected = (
        (torch.bfloat16, "bfloat16", struct.pack("<HH", 0x3F80, 0xC000)),
        (torch.float16, "float16", struct.pack("<ee", 1.0, -2.0)),
        (torch.float32, "float32", struct.pack("<ff", 1.0, -2.0)),
        (torch.float64, "float64", struct.pack("<dd", 1.0, -2.0)),
    )
    observed: list[str] = []
    for dtype, expected_name, expected_payload in expected:
        name, shape, payload = canonical_tensor_bytes(
            torch.tensor([1.0, -2.0], dtype=dtype)
        )
        if name != expected_name or shape != (2,) or payload != expected_payload:
            raise MicrocheckError("canonical tensor byte contract mismatch")
        observed.append(name)
    return observed


def _verify_snapshot_contract(
    torch,
    operation_ids,
    encode_snapshot,
    decode_snapshot,
    tensor_error,
) -> dict[str, object]:
    roles = (
        "forward_value",
        "forward_grid",
        "incoming_result_gradient",
    )
    tensors = {
        f"{operation_id}.{role}": torch.tensor(
            [float(operation_index + 1), float(role_index + 1)],
            dtype=torch.float32,
        )
        for operation_index, operation_id in enumerate(operation_ids)
        for role_index, role in enumerate(roles)
    }
    names = sorted(tensors)
    if len(names) != 27:
        raise MicrocheckError("snapshot tensor inventory mismatch")
    encoded = encode_snapshot(tensors)
    corruption_rejected = False
    with tempfile.TemporaryDirectory(prefix="val-a7-cpu-microcheck-") as temporary:
        temporary_root = Path(temporary)
        snapshot_path = temporary_root / "snapshot.vala7"
        with snapshot_path.open("xb") as output:
            output.write(encoded)
        decoded = decode_snapshot(snapshot_path, expected_names=names)
        if list(decoded) != names or any(
            not torch.equal(decoded[name], tensors[name]) for name in names
        ):
            raise MicrocheckError("snapshot round-trip mismatch")

        corrupted_path = temporary_root / "snapshot-corrupted.vala7"
        corrupted = bytearray(encoded)
        corrupted[-1] ^= 0x01
        with corrupted_path.open("xb") as output:
            output.write(corrupted)
        try:
            decode_snapshot(corrupted_path, expected_names=names)
        except tensor_error:
            corruption_rejected = True
    if not corruption_rejected:
        raise MicrocheckError("corrupted snapshot was accepted")
    return {
        "snapshot_tensor_count": len(names),
        "snapshot_names": names,
        "snapshot_corruption_rejected": True,
    }


def _verify_receipt_and_classifier_contracts(
    workspace: Path,
    inventory: Mapping[str, object],
    attribution,
    canonical_json_sha256,
    receipt_validation,
) -> tuple[list[str], list[str]]:
    source_commit = str(inventory["source_commit"])
    source_digests = {
        str(record["path"]): str(record["sha256"])
        for record in inventory["files"]
        if isinstance(record, Mapping)
    }
    schema_relative = "schemas/grid-sample-attribution-receipt.schema.json"
    schema_path = (
        Path(receipt_validation.__file__).resolve().parents[3] / schema_relative
    )
    if _sha256_file(schema_path) != source_digests[schema_relative]:
        raise MicrocheckError("receipt validator schema source mismatch")
    attributed = _literal_branch_components(
        "ATTRIBUTED", source_commit, source_digests, attribution, canonical_json_sha256
    )
    receipt_documents = [
        _literal_component_receipt(
            "control",
            0,
            source_commit,
            source_digests,
            attribution.OPERATION_IDS,
            canonical_json_sha256,
        ),
        _literal_component_receipt(
            "instrumented",
            0,
            source_commit,
            source_digests,
            attribution.OPERATION_IDS,
            canonical_json_sha256,
        ),
        _literal_component_receipt(
            "isolated-vjp",
            0,
            source_commit,
            source_digests,
            attribution.OPERATION_IDS,
            canonical_json_sha256,
        ),
        _literal_aggregate_receipt(
            attributed,
            source_commit,
            source_digests,
            attribution,
            canonical_json_sha256,
        ),
    ]
    kinds = ["control", "instrumented", "isolated-vjp", "aggregate"]
    for receipt in receipt_documents:
        receipt_validation.validate_receipt(receipt, schema_path)

    expected = {
        "ATTRIBUTED": {
            "status": "ATTRIBUTED",
            "candidate_operation": attribution.OPERATION_IDS[0],
            "candidate_role": "outgoing_value_gradient",
            "reason_codes": [],
            "terminal": (
                "WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / " "WAVE1_FORBIDDEN"
            ),
        },
        "INCONCLUSIVE": {
            "status": "INCONCLUSIVE",
            "candidate_operation": None,
            "candidate_role": None,
            "reason_codes": ["model_divergence_not_reproduced"],
            "terminal": (
                "WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / "
                "WAVE1_FORBIDDEN"
            ),
        },
        "NOT_ATTRIBUTED": {
            "status": "NOT_ATTRIBUTED",
            "candidate_operation": None,
            "candidate_role": None,
            "reason_codes": [],
            "terminal": (
                "WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / "
                "WAVE1_FORBIDDEN"
            ),
        },
    }
    statuses: list[str] = []
    for status in ("ATTRIBUTED", "INCONCLUSIVE", "NOT_ATTRIBUTED"):
        components = (
            attributed
            if status == "ATTRIBUTED"
            else _literal_branch_components(
                status,
                source_commit,
                source_digests,
                attribution,
                canonical_json_sha256,
            )
        )
        observed = attribution.classify_aggregate(
            components["controls"],
            components["instrumented"],
            components["isolated"],
        )
        if observed != expected[status]:
            raise MicrocheckError(f"classifier branch mismatch: {status}")
        statuses.append(status)
    return kinds, statuses


def _literal_branch_components(
    status: str,
    source_commit: str,
    source_digests: Mapping[str, str],
    attribution,
    canonical_json_sha256,
) -> dict[str, list[dict[str, object]]]:
    candidate = attribution.OPERATION_IDS[0]
    controls = [
        _literal_component_receipt(
            "control",
            index,
            source_commit,
            source_digests,
            attribution.OPERATION_IDS,
            canonical_json_sha256,
        )["normative"]
        for index in range(2)
    ]
    instrumented = [
        _literal_component_receipt(
            "instrumented",
            index,
            source_commit,
            source_digests,
            attribution.OPERATION_IDS,
            canonical_json_sha256,
            divergent_operation=(
                candidate if status == "ATTRIBUTED" and index == 1 else None
            ),
            parameter_variant=(
                "drift" if status == "NOT_ATTRIBUTED" and index == 1 else "same"
            ),
        )["normative"]
        for index in range(5)
    ]
    isolated = [
        _literal_component_receipt(
            "isolated-vjp",
            index,
            source_commit,
            source_digests,
            attribution.OPERATION_IDS,
            canonical_json_sha256,
            divergent_operation=(
                candidate if status == "ATTRIBUTED" and index == 1 else None
            ),
        )["normative"]
        for index in range(5)
    ]
    return {
        "controls": controls,
        "instrumented": instrumented,
        "isolated": isolated,
    }


def _literal_component_receipt(
    kind: str,
    index: int,
    source_commit: str,
    source_digests: Mapping[str, str],
    operation_ids,
    canonical_json_sha256,
    *,
    divergent_operation: str | None = None,
    divergent_role: str = "outgoing_value_gradient",
    parameter_variant: str = "same",
) -> dict[str, object]:
    component_id = f"{kind}-{index}"
    identity = _literal_identity(
        kind,
        component_id,
        source_commit,
        source_digests,
        canonical_json_sha256,
    )
    normative: dict[str, object] = {
        "identity": identity,
        "parent_receipts": {
            "environment": _literal_artifact("wave0/receipts/environment.json"),
            "model_assets": _literal_artifact("wave0/receipts/model-assets.json"),
            "model_contract": _literal_artifact("wave0/receipts/model-contract.json"),
        },
        "execution": _literal_execution(kind),
        "invariants": _literal_invariants(),
        "status": "RECORDED",
        "errors": [],
    }
    names: list[str]
    if kind == "control":
        parameters = _literal_parameters(canonical_json_sha256, parameter_variant)
        normative["parameter_gradients"] = parameters
        names = [str(record["name"]) for record in parameters["parameters"]]
    elif kind == "instrumented":
        parameters = _literal_parameters(canonical_json_sha256, parameter_variant)
        operations = _literal_operations(
            operation_ids,
            divergent_operation=divergent_operation,
            divergent_role=divergent_role,
        )
        normative["parameter_gradients"] = parameters
        normative["operations"] = operations
        names = [str(record["name"]) for record in parameters["parameters"]]
        names.extend(
            str(record["name"])
            for operation in operations
            for record in operation["tensors"]
        )
        if index == 0:
            snapshot_names = sorted(
                f"{operation_id}.{role}"
                for operation_id in operation_ids
                for role in (
                    "forward_value",
                    "forward_grid",
                    "incoming_result_gradient",
                )
            )
            normative["vjp_snapshot"] = _literal_artifact(
                "a7/components/instrumented-0/vjp-snapshot.vala7",
                names=snapshot_names,
                canonical_json_sha256=canonical_json_sha256,
            )
    elif kind == "isolated-vjp":
        operations = _literal_operations(
            operation_ids,
            divergent_operation=divergent_operation,
            divergent_role=divergent_role,
        )
        normative["operations"] = operations
        normative["parent_receipts"]["instrumented"] = _literal_artifact(
            "a7/components/instrumented-0/receipt.json"
        )
        snapshot_names = sorted(
            f"{operation_id}.{role}"
            for operation_id in operation_ids
            for role in (
                "forward_value",
                "forward_grid",
                "incoming_result_gradient",
            )
        )
        normative["vjp_snapshot"] = _literal_artifact(
            "a7/components/instrumented-0/vjp-snapshot.vala7",
            names=snapshot_names,
            canonical_json_sha256=canonical_json_sha256,
        )
        names = [
            str(record["name"])
            for operation in operations
            for record in operation["tensors"]
        ]
    else:
        raise MicrocheckError(f"unknown literal component kind: {kind}")
    normative["tensor_bundle"] = _literal_artifact(
        f"a7/components/{component_id}/tensor-bundle.vala7",
        names=sorted(names),
        canonical_json_sha256=canonical_json_sha256,
    )
    return _seal_literal_receipt(
        {
            "receipt_type": "grid-sample-attribution",
            "schema_version": 1,
            "normative": normative,
            "metadata": {
                "timestamp": "2026-08-26T00:00:02+00:00",
                "run_id": "wave0-a7-microcheck",
            },
        },
        canonical_json_sha256,
    )


def _literal_aggregate_receipt(
    components: Mapping[str, list[dict[str, object]]],
    source_commit: str,
    source_digests: Mapping[str, str],
    attribution,
    canonical_json_sha256,
) -> dict[str, object]:
    controls = components["controls"]
    instrumented = components["instrumented"]
    isolated = components["isolated"]
    classification = attribution.classify_aggregate(controls, instrumented, isolated)
    parent_components = []
    for normative in (*controls, *instrumented, *isolated):
        component_id = str(normative["identity"]["component_id"])
        parent_components.append(
            {
                "component_id": component_id,
                "receipt": _literal_artifact(
                    f"a7/components/{component_id}/receipt.json"
                ),
                "tensor_bundle": copy.deepcopy(normative["tensor_bundle"]),
            }
        )
    normative = {
        "identity": _literal_identity(
            "aggregate",
            "aggregate",
            source_commit,
            source_digests,
            canonical_json_sha256,
        ),
        "parent_receipts": {
            "environment": _literal_artifact("wave0/receipts/environment.json"),
            "model_assets": _literal_artifact("wave0/receipts/model-assets.json"),
            "model_contract": _literal_artifact("wave0/receipts/model-contract.json"),
        },
        "execution": _literal_execution("aggregate"),
        "components": {
            "controls": controls,
            "instrumented": instrumented,
            "isolated": isolated,
        },
        "parent_components": parent_components,
        "comparisons": _literal_comparison_inventory(controls, instrumented, isolated),
        "classification": classification,
        "invariants": _literal_invariants(),
        "status": classification["status"],
        "terminal": classification["terminal"],
        "errors": list(classification["reason_codes"]),
    }
    return _seal_literal_receipt(
        {
            "receipt_type": "grid-sample-attribution",
            "schema_version": 1,
            "normative": normative,
            "metadata": {
                "timestamp": "2026-08-26T00:00:03+00:00",
                "run_id": "wave0-a7-microcheck",
            },
        },
        canonical_json_sha256,
    )


def _literal_identity(
    kind: str,
    component_id: str,
    source_commit: str,
    source_digests: Mapping[str, str],
    canonical_json_sha256,
) -> dict[str, object]:
    adapter_path = (
        "src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py"
    )
    tensor_path = "src/vision_active_learning_loop/diagnostics/tensor_evidence.py"
    adapter_sha256 = source_digests[adapter_path]
    tensor_sha256 = source_digests[tensor_path]
    source_sha256 = canonical_json_sha256(
        {
            "files": [
                {"path": adapter_path, "sha256": adapter_sha256},
                {"path": tensor_path, "sha256": tensor_sha256},
            ]
        }
    )
    return {
        "source_commit": source_commit,
        "image_id": f"sha256:{'2' * 64}",
        "base_image_digest": f"sha256:{'2' * 64}",
        "run_id": "wave0-a7-microcheck",
        "component_kind": kind,
        "component_id": component_id,
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "gpu_uuid": "GPU-12345678-1234-1234-1234-123456789abc",
        "model_sha256": "1" * 64,
        "config_sha256": "1" * 64,
        "processor_sha256": "1" * 64,
        "fixture_sha256": "1" * 64,
        "model_loss_source_sha256": (
            "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
        ),
        "adapter_source_sha256": adapter_sha256,
        "tensor_evidence_source_sha256": tensor_sha256,
        "source_sha256": source_sha256,
        "seed": 17,
        "precision": "BF16",
        "num_queries": 300,
        "decoder_layers": 3,
        "feature_levels": 3,
        "disable_custom_kernels": True,
    }


def _literal_execution(subcommand: str) -> dict[str, object]:
    return {
        "argv": ["val", "diagnose", "grid-sample-attribution", subcommand],
        "exit_code": 0,
        "started_at": "2026-08-26T00:00:00+00:00",
        "ended_at": "2026-08-26T00:00:01+00:00",
        "runtime_seconds": 1.0,
        "peak_vram_bytes": 1024,
        "peak_reserved_vram_bytes": 2048,
        "loss_hex": "0x1.0000000000000p+0",
        "warning_evidence": {
            "count": 9,
            "operations": ["grid_sampler_2d_backward_cuda"] * 9,
        },
        "backend": {
            "math_only": True,
            "strict_restored": True,
            "autocast_bf16": True,
        },
    }


def _literal_invariants() -> dict[str, bool]:
    return {
        "identity_verified": True,
        "parents_verified": True,
        "tensor_inventory_verified": True,
        "warnings_verified": True,
        "backend_restored": True,
        "publication_verified": True,
    }


def _literal_tensor(
    operation_id: str, role: str, *, variant: str = "same"
) -> dict[str, object]:
    name = f"{operation_id}.{role}"
    return {
        "name": name,
        "role": role,
        "operation_id": operation_id,
        "shape": [1, 2],
        "dtype": "float32",
        "element_count": 2,
        "finite_count": 2,
        "non_finite_count": 0,
        "sha256": hashlib.sha256(f"{name}:{variant}".encode()).hexdigest(),
        "l2_norm": 1.0,
    }


def _literal_operations(
    operation_ids,
    *,
    divergent_operation: str | None = None,
    divergent_role: str = "outgoing_value_gradient",
) -> list[dict[str, object]]:
    roles = (
        "forward_value",
        "forward_grid",
        "forward_result",
        "incoming_result_gradient",
        "outgoing_value_gradient",
        "outgoing_grid_gradient",
    )
    callback_order = tuple(reversed(operation_ids))
    return [
        {
            "operation_id": operation_id,
            "callback_order": callback_order.index(operation_id),
            "tensors": [
                _literal_tensor(
                    operation_id,
                    role,
                    variant=(
                        "drift"
                        if operation_id == divergent_operation
                        and role == divergent_role
                        else "same"
                    ),
                )
                for role in roles
            ],
        }
        for operation_id in operation_ids
    ]


def _literal_parameters(canonical_json_sha256, variant: str) -> dict[str, object]:
    parameters = [
        {
            **_literal_tensor("model", "parameter_gradient", variant=variant),
            "name": name,
        }
        for name in ("detector.weight", "backbone.weight")
    ]
    return {
        "count": 2,
        "inventory_sha256": canonical_json_sha256({"parameters": parameters}),
        "parameters": parameters,
    }


def _literal_artifact(
    path: str,
    *,
    names: list[str] | None = None,
    canonical_json_sha256=None,
) -> dict[str, object]:
    artifact: dict[str, object] = {
        "path": path,
        "size": 123,
        "sha256": "1" * 64,
    }
    if names is not None:
        if canonical_json_sha256 is None:
            raise MicrocheckError("literal inventory digest function is required")
        artifact.update(
            {
                "inventory_sha256": canonical_json_sha256({"names": names}),
                "names": names,
                "public_export_candidate": False,
            }
        )
    return artifact


def _records_by_name(
    component: Mapping[str, object], *, parameters: bool
) -> dict[str, Mapping[str, object]]:
    records = (
        component["parameter_gradients"]["parameters"]
        if parameters
        else [
            tensor
            for operation in component["operations"]
            for tensor in operation["tensors"]
        ]
    )
    return {str(record["name"]): record for record in records}


def _literal_comparison_pair(
    left: Mapping[str, object],
    right: Mapping[str, object],
    *,
    parameters: bool,
) -> dict[str, object]:
    left_id = str(left["identity"]["component_id"])
    right_id = str(right["identity"]["component_id"])
    left_records = _records_by_name(left, parameters=parameters)
    right_records = _records_by_name(right, parameters=parameters)
    if set(left_records) != set(right_records):
        raise MicrocheckError("literal comparison inventory mismatch")
    tensors = []
    for name in sorted(left_records):
        exact = left_records[name]["sha256"] == right_records[name]["sha256"]
        tensors.append(
            {
                "left_replica": left_id,
                "right_replica": right_id,
                "name": name,
                "exact_digest_equal": exact,
                "difference_l2": 0.0 if exact else 1.0,
                "relative_l2": 0.0 if exact else 1.0,
                "cosine": 1.0 if exact else 0.0,
            }
        )
    left_inventory = left.get("parameter_gradients", {}).get("inventory_sha256")
    right_inventory = right.get("parameter_gradients", {}).get("inventory_sha256")
    return {
        "left_replica": left_id,
        "right_replica": right_id,
        "inventory_digest_equal": (
            left_inventory == right_inventory if parameters else True
        ),
        "tensors": tensors,
    }


def _literal_comparison_inventory(
    controls: list[dict[str, object]],
    instrumented: list[dict[str, object]],
    isolated: list[dict[str, object]],
) -> dict[str, object]:
    model_components = [*controls, *instrumented]
    return {
        "callback_order": [
            operation_id
            for _, operation_id in sorted(
                (operation["callback_order"], operation["operation_id"])
                for operation in instrumented[0]["operations"]
            )
        ],
        "parameter_pairs": [
            _literal_comparison_pair(left, right, parameters=True)
            for left, right in combinations(model_components, 2)
        ],
        "instrumented_pairs": [
            _literal_comparison_pair(left, right, parameters=False)
            for left, right in combinations(instrumented, 2)
        ],
        "isolated_pairs": [
            _literal_comparison_pair(left, right, parameters=False)
            for left, right in combinations(isolated, 2)
        ],
    }


def _seal_literal_receipt(
    receipt: dict[str, object], canonical_json_sha256
) -> dict[str, object]:
    preimage = copy.deepcopy(receipt)
    preimage["metadata"].pop("receipt_content_sha256", None)
    receipt["metadata"]["receipt_content_sha256"] = canonical_json_sha256(preimage)
    return receipt


def _load_inventory(path: Path) -> dict[str, object]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        raise MicrocheckError("source inventory mismatch") from error
    if not isinstance(document, dict) or set(document) != {
        "schema_version",
        "source_commit",
        "files",
    }:
        raise MicrocheckError("source inventory mismatch")
    source_commit = document["source_commit"]
    if (
        document["schema_version"] != 1
        or not isinstance(source_commit, str)
        or len(source_commit) != 40
        or any(character not in "0123456789abcdef" for character in source_commit)
    ):
        raise MicrocheckError("source inventory mismatch")
    files = document["files"]
    if not isinstance(files, list) or len(files) != len(SOURCE_PATHS):
        raise MicrocheckError("source inventory mismatch")
    return document


def _verify_source_inventory(workspace: Path, inventory: Mapping[str, object]) -> None:
    raw_files = inventory["files"]
    if not isinstance(raw_files, list):
        raise MicrocheckError("source inventory mismatch")
    observed_paths: list[str] = []
    for item in raw_files:
        if not isinstance(item, dict) or set(item) != {"path", "sha256"}:
            raise MicrocheckError("source inventory mismatch")
        relative = item["path"]
        expected_digest = item["sha256"]
        if (
            not isinstance(relative, str)
            or not isinstance(expected_digest, str)
            or len(expected_digest) != 64
            or any(character not in "0123456789abcdef" for character in expected_digest)
        ):
            raise MicrocheckError("source inventory mismatch")
        relative_path = Path(relative)
        if relative_path.is_absolute() or ".." in relative_path.parts:
            raise MicrocheckError("source inventory mismatch")
        target = workspace / relative_path
        _require_safe_regular_file(target, boundary=workspace)
        if _sha256_file(target) != expected_digest:
            raise MicrocheckError("source inventory mismatch")
        observed_paths.append(relative)
    if tuple(observed_paths) != SOURCE_PATHS:
        raise MicrocheckError("source inventory mismatch")


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        with Path(path).open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        raise MicrocheckError("source inventory mismatch") from error
    return digest.hexdigest()


def _require_safe_regular_file(path: Path, *, boundary: Path | None = None) -> None:
    target = Path(path)
    if not target.is_file():
        raise MicrocheckError("source inventory mismatch")
    candidates = [target]
    if boundary is None:
        candidates.extend(target.parents)
    else:
        current = target.parent
        while True:
            candidates.append(current)
            if current == boundary:
                break
            if boundary not in current.parents:
                raise MicrocheckError("source inventory mismatch")
            current = current.parent
    if any(_is_link_or_junction(candidate) for candidate in candidates):
        raise MicrocheckError("source inventory mismatch")


def _is_link_or_junction(path: Path) -> bool:
    candidate = Path(path)
    is_junction = getattr(candidate, "is_junction", None)
    return candidate.is_symlink() or (callable(is_junction) and bool(is_junction()))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the A7 CPU micro-check and emit one compact JSON line."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", type=Path, required=True)
    parser.add_argument("--source-inventory", type=Path, required=True)
    try:
        arguments = parser.parse_args(list(argv) if argv is not None else None)
        result = run_microcheck(arguments.workspace_root, arguments.source_inventory)
        encoded = json.dumps(
            result,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (AssertionError, MicrocheckError, OSError, ValueError) as error:
        print(
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "ERROR",
                    "error_type": type(error).__name__,
                    "message": str(error),
                },
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ),
            file=sys.stderr,
        )
        return 1
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
