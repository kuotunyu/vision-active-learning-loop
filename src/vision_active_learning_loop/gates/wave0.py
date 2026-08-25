"""Aggregate immutable Wave 0 A3 evidence without starting Wave 1."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from ..artifacts.no_clobber import NoClobberError, NoClobberUnsupportedError
from ..artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt,
)
from ..cli_manifest import command
from ..training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    load_checkpoint_verified,
)
from .numerical_replay import compare_replay

_SCHEMA_ROOT = Path(__file__).resolve().parents[3] / "schemas"
_RECEIPT_FILENAMES = {
    "environment": "environment.json",
    "model_assets": "model-assets.json",
    "model_contract": "model-contract.json",
    "feasibility_a": "feasibility-a.json",
    "feasibility_b": "feasibility-b.json",
}
_SCHEMA_FILENAMES = {
    "environment": "environment-receipt.schema.json",
    "model_assets": "model-asset-receipt.schema.json",
    "model_contract": "model-contract-receipt.schema.json",
    "feasibility_a": "feasibility-receipt.schema.json",
    "feasibility_b": "feasibility-receipt.schema.json",
}
_LOSS_SOURCE_SHA256 = "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6"
_SYNTHETIC_TARGET_SHA256 = (
    "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198"
)
WAVE0_GATE_INVARIANTS = (
    "primary_complete_pass",
    "clean_a_complete_pass",
    "clean_b_complete_pass",
    "all_run_ids_match",
    "all_parent_bindings_match",
    "loss_source_hash_matches",
    "synthetic_target_hash_matches",
    "all_classification_tensors_four_channels",
    "labeled_losses_finite_scalar",
    "bf16_backward_passed",
    "finite_gradients_passed",
    "parameter_update_passed",
    "vram_limit_passed",
    "checkpoint_round_trips_passed",
    "allowlisted_backward_verified",
    "feasibility_ab_exact_fields_match",
    "clean_replays_exact_fields_match",
    "numerical_replays_within_bounds",
    "data_root_unset",
    "fresh_evidence_chain",
    "historical_evidence_not_used",
)
_A2_CLASS_INVARIANTS = (
    "decoder_class_heads_four_channels",
    "decoder_auxiliary_logits_four_channels",
    "denoising_auxiliary_logits_four_channels",
    "encoder_auxiliary_logits_four_channels",
    "encoder_score_head_four_channels",
    "enc_outputs_class_four_channels",
    "enc_topk_logits_four_channels",
    "intermediate_logits_four_channels",
    "no_reachable_non_four_class_logits",
)


@dataclass(frozen=True)
class ReplayReceiptPaths:
    environment: Path
    model_assets: Path
    model_contract: Path
    feasibility_a: Path
    feasibility_b: Path
    checkpoint_a: Path
    checkpoint_b: Path


@dataclass(frozen=True)
class Wave0Inputs:
    run_id: str
    primary: ReplayReceiptPaths
    clean_a: ReplayReceiptPaths
    clean_b: ReplayReceiptPaths


@dataclass(frozen=True)
class Wave0GateReceipt:
    run_id: str
    parent_receipts: Mapping[str, Mapping[str, str]]
    exact_comparisons: Mapping[str, Mapping[str, object]]
    numerical_replay_comparisons: Mapping[str, Mapping[str, object]]
    invariants: Mapping[str, bool]
    errors: Sequence[str]

    def as_dict(self) -> dict[str, object]:
        passed = not self.errors and all(self.invariants.values())
        interpretation = (
            "WAVE0_A3_PASS / WAVE1_NOT_STARTED"
            if passed
            else "WAVE0_A3_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
        )
        return {
            "receipt_type": "wave0-gate",
            "schema_version": 2,
            "normative": {
                "parent_receipts": {
                    name: dict(values)
                    for name, values in sorted(self.parent_receipts.items())
                },
                "exact_comparisons": {
                    name: dict(value)
                    for name, value in sorted(self.exact_comparisons.items())
                },
                "numerical_replay_comparisons": {
                    name: dict(value)
                    for name, value in sorted(self.numerical_replay_comparisons.items())
                },
                "invariants": dict(sorted(self.invariants.items())),
                "status": "PASS" if passed else "FAIL",
                "errors": list(self.errors),
                "interpretation": interpretation,
            },
            "metadata": {"run_id": self.run_id},
        }


@dataclass(frozen=True)
class _AttemptEvidence:
    documents: Mapping[str, Mapping[str, object]]
    stored_hashes: Mapping[str, str]
    checkpoints: Mapping[str, CheckpointState]


def _paths_from_root(root: Path) -> ReplayReceiptPaths:
    receipts = Path(root) / "wave0" / "receipts"
    checkpoints = Path(root) / "wave0" / "checkpoints"
    return ReplayReceiptPaths(
        **{name: receipts / filename for name, filename in _RECEIPT_FILENAMES.items()},
        checkpoint_a=checkpoints / "feasibility-a" / "step-000001.pt",
        checkpoint_b=checkpoints / "feasibility-b" / "step-000001.pt",
    )


def _load_attempt(
    name: str, paths: ReplayReceiptPaths, errors: list[str]
) -> _AttemptEvidence | None:
    documents: dict[str, Mapping[str, object]] = {}
    stored_hashes: dict[str, str] = {}
    checkpoints: dict[str, CheckpointState] = {}
    for stage in _RECEIPT_FILENAMES:
        path = getattr(paths, stage)
        try:
            raw = path.read_bytes()
            document = json.loads(raw)
            if not isinstance(document, Mapping):
                raise ReceiptValidationError("receipt must be an object")
            validate_receipt(document, _SCHEMA_ROOT / _SCHEMA_FILENAMES[stage])
        except (
            OSError,
            UnicodeDecodeError,
            json.JSONDecodeError,
            ReceiptValidationError,
        ) as error:
            errors.append(f"{name}.{stage}: {error}")
            return None
        documents[stage] = document
        stored_hashes[stage] = hashlib.sha256(raw).hexdigest()
    for suffix in ("a", "b"):
        stage = f"feasibility_{suffix}"
        checkpoint_name = f"checkpoint_{suffix}"
        normative = _normative(documents[stage])
        digest = normative.get("checkpoint_sha256")
        parent_digest = normative.get("model_contract_receipt_sha256")
        try:
            if not isinstance(digest, str) or not isinstance(parent_digest, str):
                raise CheckpointVerificationError(
                    "checkpoint receipt binding is incomplete"
                )
            checkpoint = load_checkpoint_verified(
                getattr(paths, checkpoint_name),
                digest,
                expected_input_digests={"model_contract_receipt": parent_digest},
            )
        except (OSError, CheckpointVerificationError, ValueError) as error:
            errors.append(f"{name}.{checkpoint_name}: {error}")
            return None
        checkpoints[suffix] = checkpoint
        stored_hashes[checkpoint_name] = digest
    return _AttemptEvidence(
        documents=documents,
        stored_hashes=stored_hashes,
        checkpoints=checkpoints,
    )


def _normative(document: Mapping[str, object]) -> Mapping[str, object]:
    value = document.get("normative")
    return value if isinstance(value, Mapping) else {}


def _metadata(document: Mapping[str, object]) -> Mapping[str, object]:
    value = document.get("metadata")
    return value if isinstance(value, Mapping) else {}


def _is_pass(document: Mapping[str, object]) -> bool:
    return _normative(document).get("status") == "PASS"


def _attempt_is_complete_pass(attempt: _AttemptEvidence | None) -> bool:
    return attempt is not None and all(
        _is_pass(document) for document in attempt.documents.values()
    )


def _all_run_ids_match(
    attempts: Mapping[str, _AttemptEvidence | None], run_id: str
) -> bool:
    if not run_id.strip() or any(attempt is None for attempt in attempts.values()):
        return False
    return all(
        _metadata(document).get("run_id") == run_id
        for attempt in attempts.values()
        if attempt is not None
        for document in attempt.documents.values()
    )


def _parent_bindings_match(attempt: _AttemptEvidence | None) -> bool:
    if attempt is None:
        return False
    environment = attempt.documents["environment"]
    model_contract = attempt.documents["model_contract"]
    model_normative = _normative(model_contract)
    environment_content_hash = _metadata(environment).get("receipt_content_sha256")
    if (
        model_normative.get("environment_receipt_sha256")
        != attempt.stored_hashes["environment"]
        or model_normative.get("environment_receipt_content_sha256")
        != environment_content_hash
        or model_normative.get("parent_environment_receipt") != environment
    ):
        return False
    for stage in ("feasibility_a", "feasibility_b"):
        feasibility_normative = _normative(attempt.documents[stage])
        if (
            feasibility_normative.get("model_contract_receipt_sha256")
            != attempt.stored_hashes["model_contract"]
            or feasibility_normative.get("parent_model_contract") != model_contract
        ):
            return False
    return True


def _all_normative_values(
    attempts: Mapping[str, _AttemptEvidence | None], stages: Sequence[str], field: str
) -> list[object]:
    return [
        _normative(attempt.documents[stage]).get(field)
        for attempt in attempts.values()
        if attempt is not None
        for stage in stages
    ]


def _all_classification_tensors_are_four_channels(
    attempts: Mapping[str, _AttemptEvidence | None]
) -> bool:
    if any(attempt is None for attempt in attempts.values()):
        return False
    shape_fields = (
        "logits",
        "intermediate_logits",
        "enc_outputs_class",
        "enc_topk_logits",
    )
    for attempt in attempts.values():
        assert attempt is not None
        normative = _normative(attempt.documents["model_contract"])
        invariants = normative.get("invariants")
        if not isinstance(invariants, Mapping) or not all(
            invariants.get(name) is True for name in _A2_CLASS_INVARIANTS
        ):
            return False
        for evidence_name in ("observed_shapes", "labeled_observed_shapes"):
            shapes = normative.get(evidence_name)
            if not isinstance(shapes, Mapping):
                return False
            for field in shape_fields:
                shape = shapes.get(field)
                if not isinstance(shape, list) or not shape or shape[-1] != 4:
                    return False
    return True


def _labeled_losses_are_finite_scalar(
    attempts: Mapping[str, _AttemptEvidence | None]
) -> bool:
    if any(attempt is None for attempt in attempts.values()):
        return False
    for attempt in attempts.values():
        assert attempt is not None
        model = _normative(attempt.documents["model_contract"])
        labeled_shapes = model.get("labeled_observed_shapes")
        try:
            loss = float.fromhex(str(model.get("labeled_loss_hex")))
        except ValueError:
            return False
        if (
            not isinstance(labeled_shapes, Mapping)
            or labeled_shapes.get("loss") != []
            or not math.isfinite(loss)
        ):
            return False
        for stage in ("feasibility_a", "feasibility_b"):
            invariants = _normative(attempt.documents[stage]).get("invariants")
            if (
                not isinstance(invariants, Mapping)
                or invariants.get("finite_loss") is not True
            ):
                return False
    return True


def _feasibility_invariant(
    attempts: Mapping[str, _AttemptEvidence | None], *names: str
) -> bool:
    if any(attempt is None for attempt in attempts.values()):
        return False
    return all(
        isinstance(invariants, Mapping)
        and all(invariants.get(name) is True for name in names)
        for attempt in attempts.values()
        if attempt is not None
        for stage in ("feasibility_a", "feasibility_b")
        for invariants in (_normative(attempt.documents[stage]).get("invariants"),)
    )


def _data_root_is_unset(attempts: Mapping[str, _AttemptEvidence | None]) -> bool:
    if any(attempt is None for attempt in attempts.values()):
        return False
    for attempt in attempts.values():
        assert attempt is not None
        environment = _normative(attempt.documents["environment"])
        observed = environment.get("observed")
        assets_invariants = _normative(attempt.documents["model_assets"]).get(
            "invariants"
        )
        model_environment = _normative(attempt.documents["model_contract"]).get(
            "environment"
        )
        if (
            not isinstance(observed, Mapping)
            or observed.get("data_root_unset") is not True
            or not isinstance(assets_invariants, Mapping)
            or assets_invariants.get("data_root_unset") is not True
            or not isinstance(model_environment, Mapping)
            or model_environment.get("data_root_unset") is not True
        ):
            return False
    return True


def _semantic_environment_identities_match(
    attempts: Mapping[str, _AttemptEvidence | None]
) -> bool:
    if any(attempt is None for attempt in attempts.values()):
        return False
    observations: list[Mapping[str, object]] = []
    for attempt in attempts.values():
        assert attempt is not None
        observed = _normative(attempt.documents["environment"]).get("observed")
        if not isinstance(observed, Mapping):
            return False
        observations.append(observed)
    return bool(observations) and all(
        dict(observed) == dict(observations[0]) for observed in observations[1:]
    )


def _a3_comparisons(
    attempts: Mapping[str, _AttemptEvidence | None], errors: list[str]
) -> tuple[dict[str, Mapping[str, object]], dict[str, Mapping[str, object]]]:
    if any(attempt is None for attempt in attempts.values()):
        return {}, {}
    primary = attempts["primary"]
    assert primary is not None
    canonical_receipt = primary.documents["feasibility_a"]
    canonical_state = primary.checkpoints["a"]
    targets = {
        "primary_b": ("primary", "b"),
        "clean_a_a": ("clean_a", "a"),
        "clean_a_b": ("clean_a", "b"),
        "clean_b_a": ("clean_b", "a"),
        "clean_b_b": ("clean_b", "b"),
    }
    exact: dict[str, Mapping[str, object]] = {}
    numerical: dict[str, Mapping[str, object]] = {}
    for comparison_name, (attempt_name, suffix) in targets.items():
        attempt = attempts[attempt_name]
        assert attempt is not None
        result = compare_replay(
            canonical_receipt,
            canonical_state,
            attempt.documents[f"feasibility_{suffix}"],
            attempt.checkpoints[suffix],
        )
        exact[comparison_name] = dict(result.exact)
        numerical[comparison_name] = dict(result.numerical)
        errors.extend(f"{comparison_name}: {message}" for message in result.errors)
    return exact, numerical


def _historical_evidence_absent(
    attempts: Mapping[str, _AttemptEvidence | None]
) -> bool:
    if any(attempt is None for attempt in attempts.values()):
        return False
    for attempt in attempts.values():
        assert attempt is not None
        normative = _normative(attempt.documents["model_contract"])
        invariants = normative.get("invariants")
        if (
            any(
                attempt.documents[stage].get("schema_version") != 3
                for stage in ("feasibility_a", "feasibility_b")
            )
            or normative.get("loss_source_sha256") != _LOSS_SOURCE_SHA256
            or normative.get("synthetic_target_sha256") != _SYNTHETIC_TARGET_SHA256
            or not isinstance(normative.get("observed_class_modules"), Mapping)
            or not isinstance(normative.get("labeled_observed_shapes"), Mapping)
            or not isinstance(invariants, Mapping)
            or not all(invariants.get(name) is True for name in _A2_CLASS_INVARIANTS)
        ):
            return False
    return True


def evaluate_wave0(inputs: Wave0Inputs) -> Wave0GateReceipt:
    """Validate three complete A3 chains and return their aggregate gate receipt."""
    input_errors: list[str] = []
    paths = {
        "primary": inputs.primary,
        "clean_a": inputs.clean_a,
        "clean_b": inputs.clean_b,
    }
    attempts = {
        name: _load_attempt(name, value, input_errors) for name, value in paths.items()
    }
    exact_comparisons, numerical_comparisons = _a3_comparisons(attempts, input_errors)
    all_paths = [
        getattr(receipt_paths, stage).absolute()
        for receipt_paths in paths.values()
        for stage in _RECEIPT_FILENAMES
    ] + [
        getattr(receipt_paths, stage).absolute()
        for receipt_paths in paths.values()
        for stage in ("checkpoint_a", "checkpoint_b")
    ]
    all_bindings = all(_parent_bindings_match(value) for value in attempts.values())
    run_ids_match = _all_run_ids_match(attempts, inputs.run_id)
    semantic_environments_match = _semantic_environment_identities_match(attempts)
    loss_hashes = _all_normative_values(
        attempts,
        ("model_contract", "feasibility_a", "feasibility_b"),
        "loss_source_sha256",
    )
    target_hashes = _all_normative_values(
        attempts,
        ("model_contract", "feasibility_a", "feasibility_b"),
        "synthetic_target_sha256",
    )
    historical_evidence_not_used = _historical_evidence_absent(attempts)
    exact_passes = {
        name: value.get("passed") is True for name, value in exact_comparisons.items()
    }
    numerical_passes = {
        name: value.get("passed") is True
        for name, value in numerical_comparisons.items()
    }
    invariants = {
        "primary_complete_pass": _attempt_is_complete_pass(attempts["primary"]),
        "clean_a_complete_pass": _attempt_is_complete_pass(attempts["clean_a"]),
        "clean_b_complete_pass": _attempt_is_complete_pass(attempts["clean_b"]),
        "all_run_ids_match": run_ids_match,
        "all_parent_bindings_match": all_bindings,
        "loss_source_hash_matches": len(loss_hashes) == 9
        and all(value == _LOSS_SOURCE_SHA256 for value in loss_hashes),
        "synthetic_target_hash_matches": len(target_hashes) == 9
        and all(value == _SYNTHETIC_TARGET_SHA256 for value in target_hashes),
        "all_classification_tensors_four_channels": _all_classification_tensors_are_four_channels(
            attempts
        ),
        "labeled_losses_finite_scalar": _labeled_losses_are_finite_scalar(attempts),
        "bf16_backward_passed": _feasibility_invariant(
            attempts, "bf16_autocast", "bf16_supported"
        ),
        "finite_gradients_passed": _feasibility_invariant(attempts, "finite_gradients"),
        "parameter_update_passed": _feasibility_invariant(
            attempts, "adamw_update", "parameter_changed"
        ),
        "vram_limit_passed": _feasibility_invariant(
            attempts, "peak_allocated_vram_within_22_gib"
        ),
        "checkpoint_round_trips_passed": _feasibility_invariant(
            attempts,
            "checkpoint_content_verified",
            "checkpoint_round_trip",
            "resume_state_verified",
        ),
        "allowlisted_backward_verified": _feasibility_invariant(
            attempts,
            "allowlisted_backward_verified",
            "strict_deterministic_error_mode_restored",
        ),
        "feasibility_ab_exact_fields_match": len(exact_passes) == 5
        and all(exact_passes.values()),
        "clean_replays_exact_fields_match": len(exact_passes) == 5
        and all(
            exact_passes.get(name) is True
            for name in ("clean_a_a", "clean_a_b", "clean_b_a", "clean_b_b")
        ),
        "numerical_replays_within_bounds": len(numerical_passes) == 5
        and all(numerical_passes.values()),
        "data_root_unset": _data_root_is_unset(attempts),
        "fresh_evidence_chain": len(set(all_paths)) == len(all_paths)
        and run_ids_match
        and all_bindings
        and semantic_environments_match,
        "historical_evidence_not_used": historical_evidence_not_used,
    }
    errors = sorted(
        set(input_errors + [name for name, passed in invariants.items() if not passed])
    )
    parent_receipts = {
        name: dict(attempt.stored_hashes)
        for name, attempt in attempts.items()
        if attempt is not None
    }
    return Wave0GateReceipt(
        run_id=inputs.run_id,
        parent_receipts=parent_receipts,
        exact_comparisons=exact_comparisons,
        numerical_replay_comparisons=numerical_comparisons,
        invariants=invariants,
        errors=errors,
    )


@command("gate wave0")
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="val gate wave0")
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--primary-root", type=Path, required=True)
    parser.add_argument("--clean-a-root", type=Path, required=True)
    parser.add_argument("--clean-b-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)
    inputs = Wave0Inputs(
        run_id=arguments.run_id,
        primary=_paths_from_root(arguments.primary_root),
        clean_a=_paths_from_root(arguments.clean_a_root),
        clean_b=_paths_from_root(arguments.clean_b_root),
    )
    receipt = evaluate_wave0(inputs)
    try:
        atomic_write_receipt(arguments.output, receipt.as_dict())
    except (
        NoClobberError,
        NoClobberUnsupportedError,
        OSError,
        ReceiptValidationError,
        ValueError,
    ) as error:
        print(error, file=sys.stderr)
        return 3
    document = receipt.as_dict()
    normative = document["normative"]
    assert isinstance(normative, Mapping)
    print(normative["interpretation"])
    return 0 if normative["status"] == "PASS" else 2
