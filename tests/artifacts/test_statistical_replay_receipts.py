from __future__ import annotations

import copy
import math
from concurrent.futures import ThreadPoolExecutor
from itertools import combinations
from pathlib import Path
from threading import Barrier

import pytest

from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.no_clobber import NoClobberError
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.artifacts.statistical_replay_receipts import (
    StatisticalReplayReceiptError,
    validate_calibration_consistency,
    validate_validation_consistency,
)

from .test_no_clobber import _make_directory_link

SCHEMA_ROOT = Path(__file__).resolve().parents[2] / "schemas"
CALIBRATION_SCHEMA = SCHEMA_ROOT / "statistical-replay-calibration-receipt.schema.json"
VALIDATION_SCHEMA = SCHEMA_ROOT / "statistical-replay-validation-receipt.schema.json"

METRIC_KEYS = (
    "gradient_norm.relative_difference",
    "model_update.backbone.cosine_defect",
    "model_update.backbone.relative_l2",
    "model_update.detector.cosine_defect",
    "model_update.detector.relative_l2",
    "optimizer_state.backbone.exp_avg.cosine_defect",
    "optimizer_state.backbone.exp_avg.relative_l2",
    "optimizer_state.backbone.exp_avg_sq.cosine_defect",
    "optimizer_state.backbone.exp_avg_sq.relative_l2",
    "optimizer_state.detector.exp_avg.cosine_defect",
    "optimizer_state.detector.exp_avg.relative_l2",
    "optimizer_state.detector.exp_avg_sq.cosine_defect",
    "optimizer_state.detector.exp_avg_sq.relative_l2",
)
CALIBRATION_INVARIANTS = (
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
)
VALIDATION_INVARIANTS = (
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
)
CALIBRATION_IDS = tuple(f"calibration-{index:02d}" for index in range(12))
VALIDATION_IDS = tuple(f"validation-{index:02d}" for index in range(12))
SOURCE_COMMIT = "1" * 40
SPECIFICATION_COMMIT = "b59b0d4407b98b460f6166ea7288ba6021dc7a78"
PLAN_COMMIT = "2" * 40
BASE_IMAGE = "sha256:" + "3" * 64


def _record(name: str, character: str = "a") -> dict[str, object]:
    return {
        "path": f"D:/a11/{name}",
        "size": 100 + len(name),
        "sha256": character * 64,
    }


def _static_identity() -> dict[str, object]:
    return {
        "source_commit": SOURCE_COMMIT,
        "specification_commit": SPECIFICATION_COMMIT,
        "plan_commit": PLAN_COMMIT,
        "base_image_digest": BASE_IMAGE,
        "detector_revision": "4" * 40,
        "detector_sha256": "5" * 64,
        "processor_revision": "6" * 40,
        "processor_sha256": "7" * 64,
        "dinov2_revision": "8" * 40,
        "dinov2_sha256": "9" * 64,
        "config_sha256": "a" * 64,
        "fixture_sha256": "b" * 64,
        "packages": {
            "python": "3.12.11",
            "uv": "0.8.15",
            "scipy": "1.18.0",
            "torch": "2.12.0+cu126",
            "torchvision": "0.27.0+cu126",
            "transformers": "5.15.0",
            "pycocotools": "2.0.10",
        },
        "gpu": {
            "name": "NVIDIA GeForce RTX 4090",
            "uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
            "driver": "591.86",
            "cuda_runtime": "12.6",
        },
        "model_cache_inventory_sha256": "c" * 64,
    }


def _replicas(phase: str) -> list[dict[str, object]]:
    ids = CALIBRATION_IDS if phase == "calibration" else VALIDATION_IDS
    prefix = "cal" if phase == "calibration" else "val"
    offset = 100 if phase == "calibration" else 200
    replicas = []
    for index, replica_id in enumerate(ids):
        feasibility = _record(f"{prefix}/{replica_id}/feasibility.json", "d")
        checkpoint = _record(f"{prefix}/{replica_id}/checkpoint.valckpt", "e")
        feasibility["sha256"] = f"{offset + index:064x}"
        checkpoint["sha256"] = f"{offset + 50 + index:064x}"
        replicas.append(
            {
                "replica_id": replica_id,
                "feasibility": feasibility,
                "checkpoint": checkpoint,
            }
        )
    return replicas


def _runtime_identity(phase: str) -> dict[str, object]:
    replicas = _replicas(phase)
    ids = CALIBRATION_IDS if phase == "calibration" else VALIDATION_IDS
    marker = "f" if phase == "calibration" else "0"
    hour = "13" if phase == "calibration" else "15"
    run_id = f"wave0-a11-{phase}-20260827T130000000Z"
    return {
        "run_id": run_id,
        "image_tag": f"vision-active-learning-loop:wave0-a11-{phase}-test",
        "image_id": "sha256:" + marker * 64,
        "campaign_root": f"D:/a11/{phase}",
        "model_cache_root": f"D:/a11/{phase}/cache",
        "lease_id": f"wave0-a11-{phase}-lease-test",
        "lease_path": f"D:/a11/leases/{phase}.json",
        "container_ids": [
            f"{index + (1 if phase == 'calibration' else 101):064x}"
            for index in range(12)
        ],
        "replica_receipt_paths": [
            str(item["feasibility"]["path"]) for item in replicas
        ],
        "replica_receipt_sha256": [
            str(item["feasibility"]["sha256"]) for item in replicas
        ],
        "checkpoint_paths": [str(item["checkpoint"]["path"]) for item in replicas],
        "checkpoint_sha256": [str(item["checkpoint"]["sha256"]) for item in replicas],
        "timestamps": [
            f"2026-08-27T{hour}:{index:02d}:00+00:00" for index in range(12)
        ],
        "audit_paths": [
            f"D:/a11/{phase}/audit/{name}.json"
            for name in (
                "identity",
                "image-inspect",
                "cache-inventory",
                "gpu-preflight",
                "historical-preservation",
            )
        ],
        "replica_ids": list(ids),
    }


def _metadata(phase: str) -> dict[str, object]:
    runtime = _runtime_identity(phase)
    return {
        "run_id": runtime["run_id"],
        "source_commit": SOURCE_COMMIT,
        "specification_commit": SPECIFICATION_COMMIT,
        "plan_commit": PLAN_COMMIT,
        "image_tag": runtime["image_tag"],
        "image_id": runtime["image_id"],
        "base_image_digest": BASE_IMAGE,
        "owner_authorization_id": "OWNER-A11-TEST",
        "timestamp": "2026-08-27T14:00:00+00:00",
    }


def _identity(phase: str) -> dict[str, object]:
    return {"static": _static_identity(), "runtime": _runtime_identity(phase)}


def _exact(left_index: int, right_index: int) -> dict[str, object]:
    return {
        "rule": "wave0-a3-exact-checkpoint-fields-v1",
        "canonical_exact_sha256": f"{left_index + 1:064x}",
        "replay_exact_sha256": f"{right_index + 1:064x}",
        "passed": True,
        "errors": [],
    }


def _pairs(phase: str, value: float = 0.001) -> list[dict[str, object]]:
    ids = CALIBRATION_IDS if phase == "calibration" else VALIDATION_IDS
    return [
        {
            "left_replica_id": left,
            "right_replica_id": right,
            "exact": _exact(ids.index(left), ids.index(right)),
            "metrics": {key: value for key in METRIC_KEYS},
        }
        for left, right in combinations(ids, 2)
    ]


def _practical_ceilings() -> dict[str, object]:
    return {
        "threshold_multiplier": 1.5,
        "threshold_multiplier_hex": "0x1.8000000000000p+0",
        "gradient_relative_difference": 0.01,
        "gradient_relative_difference_hex": "0x1.47ae147ae147bp-7",
        "vector_relative_l2": 0.10,
        "vector_relative_l2_hex": "0x1.999999999999ap-4",
        "cosine_defect": 0.005,
        "cosine_defect_hex": "0x1.47ae147ae147bp-8",
    }


def _thresholds() -> dict[str, dict[str, object]]:
    return {
        key: {
            "maximum": 0.001,
            "maximum_hex": (0.001).hex(),
            "threshold": 0.0015,
            "threshold_hex": (0.0015).hex(),
        }
        for key in METRIC_KEYS
    }


def _threshold_digest(thresholds: dict[str, dict[str, object]]) -> str:
    return canonical_json_sha256(
        {
            "formula": "wave0-a11-pairwise-max-times-1.5-v1",
            "metric_keys": list(METRIC_KEYS),
            "thresholds": thresholds,
        }
    )


def build_calibration_receipt() -> dict[str, object]:
    thresholds = _thresholds()
    return {
        "receipt_type": "statistical-replay-calibration",
        "schema_version": 1,
        "normative": {
            "phase": "calibration",
            "identity": _identity("calibration"),
            "replicas": _replicas("calibration"),
            "pairs": _pairs("calibration"),
            "metric_keys": list(METRIC_KEYS),
            "practical_ceilings": _practical_ceilings(),
            "derivation": {
                "formula": "wave0-a11-pairwise-max-times-1.5-v1",
                "pair_count": 66,
                "metric_count": 13,
            },
            "thresholds": thresholds,
            "threshold_inventory_sha256": _threshold_digest(thresholds),
            "invariants": {key: True for key in CALIBRATION_INVARIANTS},
            "historical_preservation": _record("cal/history.json", "1"),
            "status": "RECORDED",
            "errors": [],
            "terminal": (
                "WAVE0_A11_CALIBRATION_RECORDED / " "WAVE0_NOT_PASSED / WAVE1_FORBIDDEN"
            ),
        },
        "metadata": _metadata("calibration"),
    }


def build_validation_receipt(*, failed: bool = False) -> dict[str, object]:
    thresholds = _thresholds()
    pairs = _pairs("validation")
    summaries = {
        key: {"minimum": 0.001, "median": 0.001, "maximum": 0.001}
        for key in METRIC_KEYS
    }
    errors: list[str] = []
    within_thresholds = True
    if failed:
        pairs[0]["metrics"]["gradient_norm.relative_difference"] = 0.002
        summaries["gradient_norm.relative_difference"]["maximum"] = 0.002
        errors = [
            (
                "validation-00/validation-01 "
                "gradient_norm.relative_difference exceeds calibration threshold"
            )
        ]
        within_thresholds = False
    status = "FAIL" if failed else "PASS"
    return {
        "receipt_type": "statistical-replay-validation",
        "schema_version": 1,
        "normative": {
            "phase": "validation",
            "identity": _identity("validation"),
            "replicas": _replicas("validation"),
            "pairs": pairs,
            "metric_keys": list(METRIC_KEYS),
            "practical_ceilings": _practical_ceilings(),
            "calibration_binding": {
                **_record("cal/receipt.json", "2"),
                "run_id": _runtime_identity("calibration")["run_id"],
                "threshold_inventory_sha256": _threshold_digest(thresholds),
                "thresholds": thresholds,
            },
            "cross_phase_identity": {
                "equal": _static_identity(),
                "distinct": {
                    "calibration": _runtime_identity("calibration"),
                    "validation": _runtime_identity("validation"),
                },
            },
            "summaries": summaries,
            "all_pairs_decision": {
                "within_thresholds": within_thresholds,
                "within_ceilings": True,
                "passed": not failed,
            },
            "invariants": {
                key: not (failed and key == "all_pairs_within_thresholds")
                for key in VALIDATION_INVARIANTS
            },
            "historical_preservation": _record("val/history.json", "3"),
            "status": status,
            "errors": errors,
            "terminal": (
                "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
                if failed
                else "WAVE0_A11_PASS / WAVE1_NOT_STARTED / "
                "OWNER_WAVE1_REVIEW_REQUIRED"
            ),
        },
        "metadata": _metadata("validation"),
    }


@pytest.mark.parametrize(
    ("builder", "validator"),
    [
        (build_calibration_receipt, validate_calibration_consistency),
        (build_validation_receipt, validate_validation_consistency),
    ],
)
def test_complete_receipts_pass_pure_semantic_validation(
    builder: object, validator: object
) -> None:
    assert callable(builder)
    assert callable(validator)
    receipt = builder()
    validator(receipt["normative"], receipt["metadata"])


@pytest.mark.parametrize(
    ("builder", "schema"),
    [
        (build_calibration_receipt, CALIBRATION_SCHEMA),
        (build_validation_receipt, VALIDATION_SCHEMA),
    ],
)
def test_complete_receipts_publish_and_validate_through_allowlisted_pipeline(
    tmp_path: Path, builder: object, schema: Path
) -> None:
    assert callable(builder)
    output = tmp_path / "receipt.json"
    atomic_write_receipt(output, builder())
    stored = __import__("json").loads(output.read_bytes())

    validate_receipt(stored, schema)
    assert stored["metadata"]["receipt_content_sha256"]


@pytest.mark.parametrize(
    "field",
    [
        "run_id",
        "source_commit",
        "specification_commit",
        "plan_commit",
        "image_tag",
        "image_id",
        "base_image_digest",
        "owner_authorization_id",
        "timestamp",
    ],
)
def test_metadata_is_closed_and_complete(tmp_path: Path, field: str) -> None:
    missing = build_calibration_receipt()
    missing["metadata"].pop(field)
    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / f"missing-{field}.json", missing)

    extra = build_calibration_receipt()
    extra["metadata"]["unexpected"] = field
    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / f"extra-{field}.json", extra)


def test_nested_objects_reject_additional_properties(tmp_path: Path) -> None:
    receipt = build_calibration_receipt()
    receipt["normative"]["identity"]["static"]["extra"] = True

    with pytest.raises(ReceiptValidationError, match="permitted|mismatch"):
        atomic_write_receipt(tmp_path / "extra.json", receipt)


@pytest.mark.parametrize(
    "mutation",
    [
        "reordered_replicas",
        "duplicate_pair",
        "alias_metric",
        "boolean_metric",
        "nonfinite_metric",
        "wrong_hash",
        "extra_invariant",
        "truthy_invariant",
        "wrong_terminal",
    ],
)
def test_calibration_mutations_fail_closed(tmp_path: Path, mutation: str) -> None:
    receipt = build_calibration_receipt()
    normative = receipt["normative"]
    if mutation == "reordered_replicas":
        normative["replicas"][0], normative["replicas"][1] = (
            normative["replicas"][1],
            normative["replicas"][0],
        )
    elif mutation == "duplicate_pair":
        normative["pairs"][1] = copy.deepcopy(normative["pairs"][0])
    elif mutation == "alias_metric":
        metrics = normative["pairs"][0]["metrics"]
        metrics["gradient_relative_difference"] = metrics.pop(
            "gradient_norm.relative_difference"
        )
    elif mutation == "boolean_metric":
        normative["pairs"][0]["metrics"][METRIC_KEYS[0]] = True
    elif mutation == "nonfinite_metric":
        normative["pairs"][0]["metrics"][METRIC_KEYS[0]] = float("nan")
    elif mutation == "wrong_hash":
        normative["threshold_inventory_sha256"] = "0" * 64
    elif mutation == "extra_invariant":
        normative["invariants"]["extra"] = True
    elif mutation == "truthy_invariant":
        normative["invariants"][CALIBRATION_INVARIANTS[0]] = 1
    else:
        normative["terminal"] = "WAVE0_A11_PASS"

    with pytest.raises((ReceiptValidationError, StatisticalReplayReceiptError)):
        atomic_write_receipt(tmp_path / f"{mutation}.json", receipt)


@pytest.mark.parametrize(
    "field",
    ["maximum", "maximum_hex", "threshold", "threshold_hex"],
)
def test_calibration_recomputes_every_threshold_field(
    tmp_path: Path, field: str
) -> None:
    receipt = build_calibration_receipt()
    entry = receipt["normative"]["thresholds"][METRIC_KEYS[0]]
    entry[field] = 0.0 if not field.endswith("hex") else "0x0.0p+0"

    with pytest.raises(ReceiptValidationError, match="threshold|maximum|hex"):
        atomic_write_receipt(tmp_path / f"threshold-{field}.json", receipt)


def test_validation_pass_and_complete_numeric_fail_are_both_publishable(
    tmp_path: Path,
) -> None:
    pass_output = tmp_path / "pass.json"
    fail_output = tmp_path / "fail.json"

    atomic_write_receipt(pass_output, build_validation_receipt())
    atomic_write_receipt(fail_output, build_validation_receipt(failed=True))

    assert pass_output.exists()
    assert fail_output.exists()


@pytest.mark.parametrize(
    "mutation",
    [
        "summary",
        "calibration_digest",
        "static_mismatch",
        "runtime_reuse",
        "forbidden_false_invariant",
        "errors",
        "decision",
    ],
)
def test_validation_recomputes_evidence_and_cross_phase_identity(
    tmp_path: Path, mutation: str
) -> None:
    receipt = build_validation_receipt()
    normative = receipt["normative"]
    if mutation == "summary":
        normative["summaries"][METRIC_KEYS[0]]["median"] = 0.0
    elif mutation == "calibration_digest":
        normative["calibration_binding"]["threshold_inventory_sha256"] = "0" * 64
    elif mutation == "static_mismatch":
        normative["cross_phase_identity"]["equal"]["fixture_sha256"] = "0" * 64
    elif mutation == "runtime_reuse":
        calibration = normative["cross_phase_identity"]["distinct"]["calibration"]
        validation = normative["cross_phase_identity"]["distinct"]["validation"]
        validation["run_id"] = calibration["run_id"]
    elif mutation == "forbidden_false_invariant":
        normative["status"] = "FAIL"
        normative["terminal"] = "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
        normative["invariants"]["replica_count_exact"] = False
    elif mutation == "errors":
        normative["errors"] = ["invented"]
    else:
        normative["all_pairs_decision"]["passed"] = False

    with pytest.raises((ReceiptValidationError, StatisticalReplayReceiptError)):
        atomic_write_receipt(tmp_path / f"{mutation}.json", receipt)


def test_validation_fail_errors_are_exact_sorted_pair_metric_decisions(
    tmp_path: Path,
) -> None:
    receipt = build_validation_receipt(failed=True)
    receipt["normative"]["errors"] = ["invented"]

    with pytest.raises(ReceiptValidationError, match="error|decision"):
        atomic_write_receipt(tmp_path / "wrong-errors.json", receipt)


def test_existing_output_missing_parent_and_junction_remain_no_clobber(
    tmp_path: Path,
) -> None:
    output = tmp_path / "receipt.json"
    atomic_write_receipt(output, build_calibration_receipt())
    original = output.read_bytes()
    with pytest.raises(NoClobberError):
        atomic_write_receipt(output, build_calibration_receipt())
    assert output.read_bytes() == original

    missing = tmp_path / "missing" / "receipt.json"
    with pytest.raises(OSError, match="parent"):
        atomic_write_receipt(missing, build_calibration_receipt())
    assert not missing.exists()

    real_parent = tmp_path / "real-parent"
    linked_parent = tmp_path / "linked-parent"
    _make_directory_link(linked_parent, real_parent, junction=True)
    with pytest.raises(OSError, match="parent|link|junction"):
        atomic_write_receipt(
            linked_parent / "receipt.json", build_calibration_receipt()
        )


def test_a11_publication_race_has_one_complete_winner(tmp_path: Path) -> None:
    output = tmp_path / "receipt.json"
    barrier = Barrier(2)

    def publish() -> str:
        barrier.wait()
        try:
            return atomic_write_receipt(output, build_calibration_receipt())
        except NoClobberError:
            return "no-clobber"

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: publish(), range(2)))

    assert results.count("no-clobber") == 1
    assert len([value for value in results if value != "no-clobber"]) == 1
    stored = __import__("json").loads(output.read_bytes())
    validate_receipt(stored, CALIBRATION_SCHEMA)


def test_nonfinite_validation_summary_is_rejected_even_when_boolean_claims_pass(
    tmp_path: Path,
) -> None:
    receipt = build_validation_receipt()
    receipt["normative"]["summaries"][METRIC_KEYS[0]]["maximum"] = math.inf

    with pytest.raises(ReceiptValidationError, match="non-finite"):
        atomic_write_receipt(tmp_path / "nonfinite.json", receipt)
