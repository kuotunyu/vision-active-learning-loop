"""Pure semantic validation for Wave 0 A11 aggregate receipts."""

from __future__ import annotations

import math
import re
from collections.abc import Mapping
from itertools import combinations

from ..gates.statistical_replay import (
    COSINE_DEFECT_CEILING,
    GRADIENT_CEILING,
    METRIC_KEYS,
    RELATIVE_L2_CEILING,
    THRESHOLD_FORMULA,
    THRESHOLD_MULTIPLIER,
    PairMetrics,
    StatisticalReplayError,
    derive_calibration_thresholds,
    expected_replica_ids,
    summarize_validation,
    threshold_inventory_sha256,
)


class StatisticalReplayReceiptError(ValueError):
    """Raised when an A11 receipt contradicts its embedded evidence."""


_CALIBRATION_NORMATIVE_KEYS = frozenset(
    {
        "phase",
        "identity",
        "replicas",
        "pairs",
        "metric_keys",
        "practical_ceilings",
        "derivation",
        "thresholds",
        "threshold_inventory_sha256",
        "invariants",
        "historical_preservation",
        "status",
        "errors",
        "terminal",
    }
)
_VALIDATION_NORMATIVE_KEYS = frozenset(
    {
        "phase",
        "identity",
        "replicas",
        "pairs",
        "metric_keys",
        "practical_ceilings",
        "calibration_binding",
        "cross_phase_identity",
        "summaries",
        "all_pairs_decision",
        "invariants",
        "historical_preservation",
        "status",
        "errors",
        "terminal",
    }
)
_METADATA_KEYS = frozenset(
    {
        "run_id",
        "source_commit",
        "specification_commit",
        "plan_commit",
        "image_tag",
        "image_id",
        "base_image_digest",
        "owner_authorization_id",
        "timestamp",
    }
)
_STATIC_IDENTITY_KEYS = frozenset(
    {
        "source_commit",
        "specification_commit",
        "plan_commit",
        "base_image_digest",
        "detector_revision",
        "detector_sha256",
        "processor_revision",
        "processor_sha256",
        "dinov2_revision",
        "dinov2_sha256",
        "config_sha256",
        "fixture_sha256",
        "packages",
        "gpu",
        "model_cache_inventory_sha256",
    }
)
_RUNTIME_IDENTITY_KEYS = frozenset(
    {
        "run_id",
        "image_tag",
        "image_id",
        "campaign_root",
        "model_cache_root",
        "lease_id",
        "lease_path",
        "container_ids",
        "replica_receipt_paths",
        "replica_receipt_sha256",
        "checkpoint_paths",
        "checkpoint_sha256",
        "timestamps",
        "audit_paths",
        "replica_ids",
    }
)
_CALIBRATION_INVARIANTS = frozenset(
    {
        "replica_count_exact",
        "replica_ids_exact",
        "replica_receipts_valid",
        "cohort_identity_exact",
        "pair_count_exact",
        "pair_order_exact",
        "metric_keys_exact",
        "exact_comparisons_pass",
        "finite_metrics",
        "thresholds_recomputed",
        "thresholds_within_ceilings",
        "publication_no_clobber",
        "historical_evidence_preserved",
    }
)
_VALIDATION_INVARIANTS = frozenset(
    {
        "replica_count_exact",
        "replica_ids_exact",
        "replica_receipts_valid",
        "cohort_identity_exact",
        "pair_count_exact",
        "pair_order_exact",
        "metric_keys_exact",
        "exact_comparisons_pass",
        "finite_metrics",
        "calibration_binding_exact",
        "cross_phase_static_identity_exact",
        "cross_phase_runtime_identity_distinct",
        "all_pairs_within_thresholds",
        "all_pairs_within_ceilings",
        "publication_no_clobber",
        "historical_evidence_preserved",
    }
)
_PRACTICAL_CEILINGS = {
    "threshold_multiplier": THRESHOLD_MULTIPLIER,
    "threshold_multiplier_hex": THRESHOLD_MULTIPLIER.hex(),
    "gradient_relative_difference": GRADIENT_CEILING,
    "gradient_relative_difference_hex": GRADIENT_CEILING.hex(),
    "vector_relative_l2": RELATIVE_L2_CEILING,
    "vector_relative_l2_hex": RELATIVE_L2_CEILING.hex(),
    "cosine_defect": COSINE_DEFECT_CEILING,
    "cosine_defect_hex": COSINE_DEFECT_CEILING.hex(),
}
_PACKAGES = {
    "python": "3.12.11",
    "uv": "0.8.15",
    "scipy": "1.18.0",
    "torch": "2.12.0+cu126",
    "torchvision": "0.27.0+cu126",
    "transformers": "5.15.0",
    "pycocotools": "2.0.10",
}
_CALIBRATION_TERMINAL = (
    "WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
)
_VALIDATION_PASS_TERMINAL = (
    "WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED"
)
_VALIDATION_FAIL_TERMINAL = "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
_HASH_PATTERN = re.compile(r"[0-9a-f]{64}")
_COMMIT_PATTERN = re.compile(r"[0-9a-f]{40}")
_IMAGE_PATTERN = re.compile(r"sha256:[0-9a-f]{64}")


def validate_calibration_consistency(
    normative: Mapping[str, object], metadata: Mapping[str, object]
) -> None:
    """Recompute and validate one complete successful calibration receipt."""
    document = _require_exact_keys(
        normative, _CALIBRATION_NORMATIVE_KEYS, "calibration normative"
    )
    if document.get("phase") != "calibration":
        raise StatisticalReplayReceiptError("calibration phase mismatch")
    static, runtime = _validate_identity(
        document.get("identity"), metadata, "calibration"
    )
    del static
    _validate_replicas(document.get("replicas"), runtime, "calibration")
    pairs = _pair_metrics(document.get("pairs"), "calibration")
    _require_metric_keys(document.get("metric_keys"))
    if document.get("practical_ceilings") != _PRACTICAL_CEILINGS:
        raise StatisticalReplayReceiptError("practical ceilings mismatch")
    if document.get("derivation") != {
        "formula": THRESHOLD_FORMULA,
        "pair_count": 66,
        "metric_count": len(METRIC_KEYS),
    }:
        raise StatisticalReplayReceiptError("calibration derivation mismatch")

    try:
        expected_thresholds = derive_calibration_thresholds(pairs)
        expected_digest = threshold_inventory_sha256(expected_thresholds)
    except StatisticalReplayError as error:
        raise StatisticalReplayReceiptError(str(error)) from error
    if document.get("thresholds") != expected_thresholds:
        raise StatisticalReplayReceiptError("calibration thresholds mismatch")
    if document.get("threshold_inventory_sha256") != expected_digest:
        raise StatisticalReplayReceiptError("calibration threshold digest mismatch")

    _require_true_invariants(
        document.get("invariants"), _CALIBRATION_INVARIANTS, "calibration"
    )
    _validate_file_record(
        document.get("historical_preservation"), "historical preservation"
    )
    if document.get("status") != "RECORDED" or document.get("errors") != []:
        raise StatisticalReplayReceiptError("calibration status or errors mismatch")
    if document.get("terminal") != _CALIBRATION_TERMINAL:
        raise StatisticalReplayReceiptError("calibration terminal mismatch")


def validate_validation_consistency(
    normative: Mapping[str, object], metadata: Mapping[str, object]
) -> None:
    """Recompute and validate one complete validation verdict receipt."""
    document = _require_exact_keys(
        normative, _VALIDATION_NORMATIVE_KEYS, "validation normative"
    )
    if document.get("phase") != "validation":
        raise StatisticalReplayReceiptError("validation phase mismatch")
    static, runtime = _validate_identity(
        document.get("identity"), metadata, "validation"
    )
    _validate_replicas(document.get("replicas"), runtime, "validation")
    pairs = _pair_metrics(document.get("pairs"), "validation")
    _require_metric_keys(document.get("metric_keys"))
    if document.get("practical_ceilings") != _PRACTICAL_CEILINGS:
        raise StatisticalReplayReceiptError("practical ceilings mismatch")

    binding = _validate_calibration_binding(document.get("calibration_binding"))
    _validate_cross_phase_identity(
        document.get("cross_phase_identity"), static, runtime, binding
    )
    thresholds = _require_exact_keys(
        binding.get("thresholds"), frozenset(METRIC_KEYS), "calibration thresholds"
    )
    try:
        if binding.get("threshold_inventory_sha256") != threshold_inventory_sha256(
            thresholds
        ):
            raise StatisticalReplayReceiptError("calibration threshold digest mismatch")
        recomputed = summarize_validation(pairs, thresholds)
    except StatisticalReplayError as error:
        raise StatisticalReplayReceiptError(str(error)) from error

    if document.get("summaries") != recomputed["summaries"]:
        raise StatisticalReplayReceiptError("validation summaries mismatch")
    within_thresholds = recomputed["all_pairs_within_thresholds"]
    within_ceilings = recomputed["all_pairs_within_ceilings"]
    passed = within_thresholds is True and within_ceilings is True
    expected_decision = {
        "within_thresholds": within_thresholds,
        "within_ceilings": within_ceilings,
        "passed": passed,
    }
    if document.get("all_pairs_decision") != expected_decision:
        raise StatisticalReplayReceiptError("validation decision mismatch")

    invariants = _require_exact_keys(
        document.get("invariants"), _VALIDATION_INVARIANTS, "validation invariants"
    )
    for name in _VALIDATION_INVARIANTS - {
        "all_pairs_within_thresholds",
        "all_pairs_within_ceilings",
    }:
        if invariants.get(name) is not True:
            raise StatisticalReplayReceiptError(
                f"validation invariant {name} is not true"
            )
    if invariants.get("all_pairs_within_thresholds") is not within_thresholds:
        raise StatisticalReplayReceiptError(
            "validation threshold invariant contradicts pair evidence"
        )
    if invariants.get("all_pairs_within_ceilings") is not within_ceilings:
        raise StatisticalReplayReceiptError(
            "validation ceiling invariant contradicts pair evidence"
        )
    if document.get("errors") != recomputed["errors"]:
        raise StatisticalReplayReceiptError("validation errors mismatch decision")
    expected_status = "PASS" if passed else "FAIL"
    if document.get("status") != expected_status:
        raise StatisticalReplayReceiptError("validation status mismatch decision")
    expected_terminal = (
        _VALIDATION_PASS_TERMINAL if passed else _VALIDATION_FAIL_TERMINAL
    )
    if document.get("terminal") != expected_terminal:
        raise StatisticalReplayReceiptError("validation terminal mismatch")
    _validate_file_record(
        document.get("historical_preservation"), "historical preservation"
    )


def _require_exact_keys(
    value: object, expected: frozenset[str], label: str
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or frozenset(value) != expected:
        raise StatisticalReplayReceiptError(f"{label} fields mismatch")
    return value


def _validate_metadata(value: object, phase: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise StatisticalReplayReceiptError("metadata fields mismatch")
    keys = frozenset(value)
    if keys not in (_METADATA_KEYS, _METADATA_KEYS | {"receipt_content_sha256"}):
        raise StatisticalReplayReceiptError("metadata fields mismatch")
    for name in (
        "run_id",
        "image_tag",
        "owner_authorization_id",
        "timestamp",
    ):
        _require_nonempty_string(value.get(name), f"metadata {name}")
    if not str(value["run_id"]).startswith(f"wave0-a11-{phase}-"):
        raise StatisticalReplayReceiptError("metadata run ID phase mismatch")
    if not str(value["image_tag"]).startswith(
        f"vision-active-learning-loop:wave0-a11-{phase}-"
    ):
        raise StatisticalReplayReceiptError("metadata image tag phase mismatch")
    for name in ("source_commit", "specification_commit", "plan_commit"):
        _require_pattern(value.get(name), _COMMIT_PATTERN, f"metadata {name}")
    for name in ("image_id", "base_image_digest"):
        _require_pattern(value.get(name), _IMAGE_PATTERN, f"metadata {name}")
    if "receipt_content_sha256" in value:
        _require_pattern(
            value.get("receipt_content_sha256"),
            _HASH_PATTERN,
            "metadata receipt content hash",
        )
    return value


def _validate_identity(
    value: object, metadata: object, phase: str
) -> tuple[Mapping[str, object], Mapping[str, object]]:
    identity = _require_exact_keys(value, frozenset({"static", "runtime"}), "identity")
    metadata_document = _validate_metadata(metadata, phase)
    static = _validate_static_identity(identity.get("static"))
    runtime = _validate_runtime_identity(identity.get("runtime"), phase)
    for name in (
        "source_commit",
        "specification_commit",
        "plan_commit",
        "base_image_digest",
    ):
        if static.get(name) != metadata_document.get(name):
            raise StatisticalReplayReceiptError(f"metadata {name} binding mismatch")
    for name in ("run_id", "image_tag", "image_id"):
        if runtime.get(name) != metadata_document.get(name):
            raise StatisticalReplayReceiptError(f"metadata {name} binding mismatch")
    return static, runtime


def _validate_static_identity(value: object) -> Mapping[str, object]:
    static = _require_exact_keys(value, _STATIC_IDENTITY_KEYS, "static identity")
    for name in (
        "source_commit",
        "specification_commit",
        "plan_commit",
        "detector_revision",
        "processor_revision",
        "dinov2_revision",
    ):
        _require_pattern(static.get(name), _COMMIT_PATTERN, f"static {name}")
    for name in (
        "detector_sha256",
        "processor_sha256",
        "dinov2_sha256",
        "config_sha256",
        "fixture_sha256",
        "model_cache_inventory_sha256",
    ):
        _require_pattern(static.get(name), _HASH_PATTERN, f"static {name}")
    _require_pattern(
        static.get("base_image_digest"), _IMAGE_PATTERN, "static base image digest"
    )
    if static.get("packages") != _PACKAGES:
        raise StatisticalReplayReceiptError("static package identity mismatch")
    gpu = _require_exact_keys(
        static.get("gpu"),
        frozenset({"name", "uuid", "driver", "cuda_runtime"}),
        "GPU identity",
    )
    if (
        gpu.get("name") != "NVIDIA GeForce RTX 4090"
        or gpu.get("cuda_runtime") != "12.6"
    ):
        raise StatisticalReplayReceiptError("GPU contract mismatch")
    for name in ("uuid", "driver"):
        _require_nonempty_string(gpu.get(name), f"GPU {name}")
    return static


def _validate_runtime_identity(value: object, phase: str) -> Mapping[str, object]:
    runtime = _require_exact_keys(value, _RUNTIME_IDENTITY_KEYS, "runtime identity")
    expected_ids = list(expected_replica_ids(phase))
    for name in (
        "run_id",
        "image_tag",
        "campaign_root",
        "model_cache_root",
        "lease_id",
        "lease_path",
    ):
        _require_nonempty_string(runtime.get(name), f"runtime {name}")
    if not str(runtime["run_id"]).startswith(f"wave0-a11-{phase}-"):
        raise StatisticalReplayReceiptError("runtime run ID phase mismatch")
    if not str(runtime["image_tag"]).startswith(
        f"vision-active-learning-loop:wave0-a11-{phase}-"
    ):
        raise StatisticalReplayReceiptError("runtime image tag phase mismatch")
    _require_pattern(runtime.get("image_id"), _IMAGE_PATTERN, "runtime image ID")
    list_rules = {
        "container_ids": (12, _HASH_PATTERN),
        "replica_receipt_paths": (12, None),
        "replica_receipt_sha256": (12, _HASH_PATTERN),
        "checkpoint_paths": (12, None),
        "checkpoint_sha256": (12, _HASH_PATTERN),
        "timestamps": (12, None),
        "audit_paths": (5, None),
    }
    for name, (length, pattern) in list_rules.items():
        items = runtime.get(name)
        if not isinstance(items, list) or len(items) != length:
            raise StatisticalReplayReceiptError(f"runtime {name} inventory mismatch")
        for item in items:
            if pattern is None:
                _require_nonempty_string(item, f"runtime {name} item")
            else:
                _require_pattern(item, pattern, f"runtime {name} item")
        if len(set(items)) != len(items):
            raise StatisticalReplayReceiptError(f"runtime {name} contains duplicates")
    if runtime.get("replica_ids") != expected_ids:
        raise StatisticalReplayReceiptError("runtime replica IDs mismatch")
    return runtime


def _validate_replicas(
    value: object, runtime: Mapping[str, object], phase: str
) -> None:
    expected_ids = expected_replica_ids(phase)
    if not isinstance(value, list) or len(value) != len(expected_ids):
        raise StatisticalReplayReceiptError("replica count mismatch")
    feasibility_paths: list[object] = []
    feasibility_hashes: list[object] = []
    checkpoint_paths: list[object] = []
    checkpoint_hashes: list[object] = []
    for replica, replica_id in zip(value, expected_ids, strict=True):
        entry = _require_exact_keys(
            replica,
            frozenset({"replica_id", "feasibility", "checkpoint"}),
            "replica",
        )
        if entry.get("replica_id") != replica_id:
            raise StatisticalReplayReceiptError("replica ID order mismatch")
        feasibility = _validate_file_record(
            entry.get("feasibility"), "replica feasibility"
        )
        checkpoint = _validate_file_record(entry.get("checkpoint"), "checkpoint")
        feasibility_paths.append(feasibility["path"])
        feasibility_hashes.append(feasibility["sha256"])
        checkpoint_paths.append(checkpoint["path"])
        checkpoint_hashes.append(checkpoint["sha256"])
    expected_runtime = {
        "replica_receipt_paths": feasibility_paths,
        "replica_receipt_sha256": feasibility_hashes,
        "checkpoint_paths": checkpoint_paths,
        "checkpoint_sha256": checkpoint_hashes,
    }
    for name, expected in expected_runtime.items():
        if runtime.get(name) != expected:
            raise StatisticalReplayReceiptError(f"replica {name} binding mismatch")


def _pair_metrics(value: object, phase: str) -> tuple[PairMetrics, ...]:
    expected_pairs = tuple(combinations(expected_replica_ids(phase), 2))
    if not isinstance(value, list) or len(value) != len(expected_pairs):
        raise StatisticalReplayReceiptError("pair count mismatch")
    result: list[PairMetrics] = []
    for pair, (left_id, right_id) in zip(value, expected_pairs, strict=True):
        entry = _require_exact_keys(
            pair,
            frozenset({"left_replica_id", "right_replica_id", "exact", "metrics"}),
            "pair",
        )
        if (entry.get("left_replica_id"), entry.get("right_replica_id")) != (
            left_id,
            right_id,
        ):
            raise StatisticalReplayReceiptError("pair order mismatch")
        exact = _require_exact_keys(
            entry.get("exact"),
            frozenset(
                {
                    "rule",
                    "canonical_exact_sha256",
                    "replay_exact_sha256",
                    "passed",
                    "errors",
                }
            ),
            "exact comparison",
        )
        if (
            exact.get("rule") != "wave0-a3-exact-checkpoint-fields-v1"
            or exact.get("passed") is not True
            or exact.get("errors") != []
        ):
            raise StatisticalReplayReceiptError("exact comparison failed")
        for name in ("canonical_exact_sha256", "replay_exact_sha256"):
            _require_pattern(exact.get(name), _HASH_PATTERN, f"exact {name}")
        metrics = _require_exact_keys(
            entry.get("metrics"), frozenset(METRIC_KEYS), "pair metrics"
        )
        if tuple(metrics) != METRIC_KEYS:
            raise StatisticalReplayReceiptError("pair metric order mismatch")
        normalized: dict[str, float] = {}
        for key in METRIC_KEYS:
            metric = metrics[key]
            if (
                type(metric) not in (int, float)
                or not math.isfinite(float(metric))
                or float(metric) < 0.0
            ):
                raise StatisticalReplayReceiptError(f"{key} metric is invalid")
            normalized[key] = float(metric)
        result.append(PairMetrics(left_id, right_id, dict(exact), normalized))
    return tuple(result)


def _require_metric_keys(value: object) -> None:
    if value != list(METRIC_KEYS):
        raise StatisticalReplayReceiptError("metric key inventory mismatch")


def _validate_calibration_binding(value: object) -> Mapping[str, object]:
    binding = _require_exact_keys(
        value,
        frozenset(
            {
                "path",
                "size",
                "sha256",
                "run_id",
                "threshold_inventory_sha256",
                "thresholds",
            }
        ),
        "calibration binding",
    )
    _validate_file_record(
        {name: binding[name] for name in ("path", "size", "sha256")},
        "calibration receipt",
    )
    _require_nonempty_string(binding.get("run_id"), "calibration run ID")
    if not str(binding["run_id"]).startswith("wave0-a11-calibration-"):
        raise StatisticalReplayReceiptError("calibration run ID phase mismatch")
    _require_pattern(
        binding.get("threshold_inventory_sha256"),
        _HASH_PATTERN,
        "calibration threshold digest",
    )
    return binding


def _validate_cross_phase_identity(
    value: object,
    current_static: Mapping[str, object],
    current_runtime: Mapping[str, object],
    binding: Mapping[str, object],
) -> None:
    cross_phase = _require_exact_keys(
        value, frozenset({"equal", "distinct"}), "cross-phase identity"
    )
    equal = _validate_static_identity(cross_phase.get("equal"))
    if equal != current_static:
        raise StatisticalReplayReceiptError("cross-phase static identity mismatch")
    distinct = _require_exact_keys(
        cross_phase.get("distinct"),
        frozenset({"calibration", "validation"}),
        "cross-phase distinct identity",
    )
    calibration = _validate_runtime_identity(distinct.get("calibration"), "calibration")
    validation = _validate_runtime_identity(distinct.get("validation"), "validation")
    if validation != current_runtime:
        raise StatisticalReplayReceiptError("validation runtime identity mismatch")
    if binding.get("run_id") != calibration.get("run_id"):
        raise StatisticalReplayReceiptError("calibration receipt run ID mismatch")
    list_names = {
        "container_ids",
        "replica_receipt_paths",
        "replica_receipt_sha256",
        "checkpoint_paths",
        "checkpoint_sha256",
        "timestamps",
        "audit_paths",
        "replica_ids",
    }
    for name in _RUNTIME_IDENTITY_KEYS - list_names:
        if calibration.get(name) == validation.get(name):
            raise StatisticalReplayReceiptError(
                f"cross-phase runtime identity reused: {name}"
            )
    for name in list_names:
        left = calibration.get(name)
        right = validation.get(name)
        if not isinstance(left, list) or not isinstance(right, list):
            raise StatisticalReplayReceiptError(
                f"cross-phase runtime identity invalid: {name}"
            )
        if set(left) & set(right):
            raise StatisticalReplayReceiptError(
                f"cross-phase runtime identity reused: {name}"
            )


def _require_true_invariants(
    value: object, expected: frozenset[str], phase: str
) -> None:
    invariants = _require_exact_keys(value, expected, f"{phase} invariants")
    if any(invariants.get(name) is not True for name in expected):
        raise StatisticalReplayReceiptError(f"{phase} invariant is not true")


def _validate_file_record(value: object, label: str) -> Mapping[str, object]:
    record = _require_exact_keys(value, frozenset({"path", "size", "sha256"}), label)
    _require_nonempty_string(record.get("path"), f"{label} path")
    size = record.get("size")
    if type(size) is not int or size < 0:
        raise StatisticalReplayReceiptError(f"{label} size is invalid")
    _require_pattern(record.get("sha256"), _HASH_PATTERN, f"{label} hash")
    return record


def _require_nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or "\n" in value or "\r" in value:
        raise StatisticalReplayReceiptError(f"{label} is invalid")
    return value


def _require_pattern(value: object, pattern: re.Pattern[str], label: str) -> str:
    if not isinstance(value, str) or pattern.fullmatch(value) is None:
        raise StatisticalReplayReceiptError(f"{label} is invalid")
    return value
