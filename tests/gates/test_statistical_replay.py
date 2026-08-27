from __future__ import annotations

import copy
import hashlib
import json
import math
from collections.abc import Mapping
from itertools import combinations
from pathlib import Path

import pytest
import torch

from vision_active_learning_loop.artifacts import receipts
from vision_active_learning_loop.artifacts.digests import (
    canonical_json_sha256,
    sha256_file,
)
from vision_active_learning_loop.artifacts.receipts import (
    _receipt_content_sha256,
    _stored_receipt_sha256,
    atomic_write_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.gates import statistical_replay
from vision_active_learning_loop.gates.numerical_replay import compare_replay
from vision_active_learning_loop.gates.statistical_replay import (
    PairMetrics,
    ReplicaEvidence,
    StatisticalReplayError,
    compare_statistical_pair,
    derive_calibration_thresholds,
    derived_vector_metrics,
    expected_replica_ids,
    gradient_relative_difference,
    ordered_replica_pairs,
    summarize_validation,
    threshold_inventory_sha256,
    vector_metrics,
)
from vision_active_learning_loop.training.checkpoint_io import (
    CheckpointState,
    checkpoint_state_digests,
    checkpoint_state_sha256,
    save_checkpoint_atomic,
)

from ..artifacts.test_receipts import build_valid_model_contract_receipt
from ..probes.test_training_feasibility import _receipt as valid_feasibility_receipt
from .test_wave0_gate import _bind_checkpoint_evidence, _checkpoint_fixture

EXPECTED_METRIC_KEYS = (
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
EXPECTED_CALIBRATION_IDS = tuple(f"calibration-{index:02d}" for index in range(12))
EXPECTED_VALIDATION_IDS = tuple(f"validation-{index:02d}" for index in range(12))
HASH = "a" * 64


def _inventory() -> list[dict[str, object]]:
    return [
        {
            "name": "detector.weight",
            "group_name": "detector",
            "shape": [2],
            "dtype": "float64",
        },
        {
            "name": "model.backbone.weight",
            "group_name": "backbone",
            "shape": [2],
            "dtype": "float64",
        },
    ]


def _model_inventory() -> list[dict[str, object]]:
    return [
        {
            "name": "detector.weight",
            "shape": [2],
            "dtype": "float64",
            "trainable": True,
        },
        {
            "name": "model.backbone.weight",
            "shape": [2],
            "dtype": "float64",
            "trainable": True,
        },
        {
            "name": "running_mean",
            "shape": [1],
            "dtype": "float64",
            "trainable": False,
        },
        {
            "name": "running_count",
            "shape": [],
            "dtype": "int64",
            "trainable": False,
        },
    ]


def _receipt(
    *,
    detector_norm: float = 1.0,
    backbone_norm: float = 2.0,
    gradient_norm: float = 0.75,
) -> dict[str, object]:
    return {
        "normative": {
            "exact_comparison": {
                "rule": "wave0-a3-exact-replay-sha256-v1",
                "parameter_digest_before": "0" * 64,
                "parameter_inventory": _inventory(),
                "ordered_loss_hex": [(3.25).hex()],
                "optimizer_groups": [
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
                ],
                "scheduler_state_before_sha256": "1" * 64,
                "sampler_order_digest": "2" * 64,
                "semantic_input_digests": {
                    "fixture_sha256": "3" * 64,
                    "synthetic_target_sha256": "4" * 64,
                },
                "checkpoint_epoch": 0,
                "checkpoint_step": 1,
                "model_state_inventory": _model_inventory(),
                "state_digests": {
                    "scheduler": "4" * 64,
                    "scaler": "5" * 64,
                    "rng": "6" * 64,
                    "sampler": "2" * 64,
                },
                "allowlisted_backward": {
                    "operation_identifier": "grid_sampler_2d_backward_cuda"
                },
                "sha256": HASH,
            },
            "step": {"gradient_norm": gradient_norm},
            "update_groups": {
                "detector": {"l2_norm": detector_norm},
                "backbone": {"l2_norm": backbone_norm},
            },
        }
    }


def _optimizer_state(
    detector: torch.Tensor, backbone: torch.Tensor
) -> dict[str, object]:
    return {
        "state": {
            0: {
                "step": torch.tensor(1.0, dtype=torch.float64),
                "exp_avg": detector.clone(),
                "exp_avg_sq": detector.square().mul(0.01),
            },
            1: {
                "step": torch.tensor(1.0, dtype=torch.float64),
                "exp_avg": backbone.clone(),
                "exp_avg_sq": backbone.square().mul(0.01),
            },
        },
        "param_groups": [
            {
                "group_name": "detector",
                "lr": 1e-4,
                "weight_decay": 1e-4,
                "params": [0],
            },
            {
                "group_name": "backbone",
                "lr": 1e-5,
                "weight_decay": 1e-4,
                "params": [1],
            },
        ],
    }


def _state(
    *,
    detector: tuple[float, float] = (1.0, 0.0),
    backbone: tuple[float, float] = (0.0, 2.0),
    moment_scale: float = 1.0,
) -> CheckpointState:
    detector_tensor = torch.tensor(detector, dtype=torch.float64)
    backbone_tensor = torch.tensor(backbone, dtype=torch.float64)
    return CheckpointState(
        model_state={
            "detector.weight": detector_tensor,
            "model.backbone.weight": backbone_tensor,
            "running_mean": torch.tensor([0.5], dtype=torch.float64),
            "running_count": torch.tensor(1, dtype=torch.int64),
        },
        optimizer_state=_optimizer_state(
            detector_tensor.mul(moment_scale), backbone_tensor.mul(moment_scale)
        ),
        scheduler_state={"last_epoch": 1, "_step_count": 2},
        scaler_state=None,
        epoch=0,
        step=1,
        sampler_order_digest="2" * 64,
        rng_state={"seed": 17, "stream": torch.tensor([1, 2], dtype=torch.uint8)},
        input_digests={"model_contract_receipt": "3" * 64},
    )


def _replica(replica_id: str) -> ReplicaEvidence:
    return ReplicaEvidence(replica_id, _receipt(), _state())


def _pair_metrics(
    *,
    phase: str = "calibration",
    metric_values: Mapping[str, float] | None = None,
) -> list[PairMetrics]:
    ids = (
        EXPECTED_CALIBRATION_IDS if phase == "calibration" else EXPECTED_VALIDATION_IDS
    )
    values = {key: 0.0 for key in EXPECTED_METRIC_KEYS}
    if metric_values is not None:
        values.update(metric_values)
    return [
        PairMetrics(left, right, {"passed": True, "errors": []}, dict(values))
        for left, right in combinations(ids, 2)
    ]


def _thresholds(value: float) -> dict[str, dict[str, object]]:
    return {
        key: {
            "maximum": value / 1.5,
            "maximum_hex": (value / 1.5).hex(),
            "threshold": value,
            "threshold_hex": value.hex(),
        }
        for key in EXPECTED_METRIC_KEYS
    }


def test_closed_replica_inventories_produce_all_66_lexicographic_pairs() -> None:
    assert expected_replica_ids("calibration") == EXPECTED_CALIBRATION_IDS
    assert expected_replica_ids("validation") == EXPECTED_VALIDATION_IDS

    calibration = ordered_replica_pairs(
        [_replica(replica_id) for replica_id in EXPECTED_CALIBRATION_IDS],
        "calibration",
    )
    validation = ordered_replica_pairs(
        [_replica(replica_id) for replica_id in EXPECTED_VALIDATION_IDS],
        "validation",
    )

    assert len(calibration) == 66
    assert len(validation) == 66
    assert [(left.replica_id, right.replica_id) for left, right in calibration] == list(
        combinations(EXPECTED_CALIBRATION_IDS, 2)
    )
    assert [(left.replica_id, right.replica_id) for left, right in validation] == list(
        combinations(EXPECTED_VALIDATION_IDS, 2)
    )


@pytest.mark.parametrize(
    "replica_ids,phase",
    [
        (EXPECTED_CALIBRATION_IDS[:-1], "calibration"),
        ((*EXPECTED_CALIBRATION_IDS, "calibration-12"), "calibration"),
        ((*EXPECTED_CALIBRATION_IDS[:-1], "calibration-00"), "calibration"),
        ((*EXPECTED_CALIBRATION_IDS[:-1], "calibration-1"), "calibration"),
        (EXPECTED_VALIDATION_IDS, "calibration"),
        (
            (
                EXPECTED_CALIBRATION_IDS[1],
                EXPECTED_CALIBRATION_IDS[0],
                *EXPECTED_CALIBRATION_IDS[2:],
            ),
            "calibration",
        ),
    ],
)
def test_invalid_replica_inventories_fail_closed(
    replica_ids: tuple[str, ...], phase: str
) -> None:
    with pytest.raises(StatisticalReplayError, match="replica inventory"):
        ordered_replica_pairs(
            [_replica(replica_id) for replica_id in replica_ids], phase
        )


def test_hand_computed_float64_metrics_are_exact() -> None:
    assert gradient_relative_difference(2.0, 1.0) == 0.5
    assert vector_metrics(
        torch.tensor([1.0, 0.0], dtype=torch.float64),
        torch.tensor([0.0, 1.0], dtype=torch.float64),
    ) == {"relative_l2": math.sqrt(2.0), "cosine_defect": 1.0}
    assert vector_metrics(
        torch.tensor([1.0, -2.0], dtype=torch.float64),
        torch.tensor([1.0, -2.0], dtype=torch.float64),
    ) == {"relative_l2": 0.0, "cosine_defect": 0.0}


def test_derived_cosine_normalizes_only_the_registered_endpoint_slack() -> None:
    inside_difference = math.nextafter(2.0, math.inf)
    outside_difference = math.sqrt(4.0 + 8.0e-12)

    assert derived_vector_metrics(1.0, 1.0, inside_difference)["cosine_defect"] == 2.0
    with pytest.raises(StatisticalReplayError, match="cosine"):
        derived_vector_metrics(1.0, 1.0, outside_difference)


@pytest.mark.parametrize(
    "left,right,error",
    [
        (
            torch.zeros(2, dtype=torch.float64),
            torch.ones(2, dtype=torch.float64),
            "zero",
        ),
        (
            torch.tensor([float("nan"), 1.0], dtype=torch.float64),
            torch.ones(2, dtype=torch.float64),
            "finite",
        ),
        (
            torch.tensor([float("inf"), 1.0], dtype=torch.float64),
            torch.ones(2, dtype=torch.float64),
            "finite",
        ),
        (
            torch.ones(2, dtype=torch.float32),
            torch.ones(2, dtype=torch.float64),
            "dtype",
        ),
        (
            torch.ones(2, dtype=torch.float64),
            torch.ones(3, dtype=torch.float64),
            "shape",
        ),
    ],
)
def test_vector_metrics_reject_invalid_domains(
    left: torch.Tensor, right: torch.Tensor, error: str
) -> None:
    with pytest.raises(StatisticalReplayError, match=error):
        vector_metrics(left, right)


@pytest.mark.parametrize(
    "left,right",
    [
        (True, 1.0),
        (1.0, False),
        (float("nan"), 1.0),
        (1.0, float("inf")),
        (0.0, 0.0),
    ],
)
def test_gradient_metric_rejects_booleans_nonfinite_and_zero(
    left: object, right: object
) -> None:
    with pytest.raises(StatisticalReplayError, match="gradient"):
        gradient_relative_difference(left, right)


def test_a11_retains_exact_gate_but_ignores_legacy_numerical_failure() -> None:
    detector = (1.0, 0.002)
    right_receipt = _receipt(detector_norm=math.hypot(*detector))
    legacy = compare_replay(
        _receipt(), _state(), right_receipt, _state(detector=detector)
    )

    assert legacy.exact["passed"] is True
    assert legacy.numerical["passed"] is False
    result = compare_statistical_pair(
        ReplicaEvidence("calibration-00", _receipt(), _state()),
        ReplicaEvidence("calibration-01", right_receipt, _state(detector=detector)),
    )

    assert result.exact == legacy.exact
    assert result.metrics["model_update.detector.relative_l2"] > 1e-3
    assert tuple(result.metrics) == EXPECTED_METRIC_KEYS


def test_exact_field_failure_stops_before_a11_metrics() -> None:
    changed = _receipt()
    normative = changed["normative"]
    assert isinstance(normative, dict)
    exact = normative["exact_comparison"]
    assert isinstance(exact, dict)
    exact["sha256"] = "b" * 64

    with pytest.raises(StatisticalReplayError, match="exact"):
        compare_statistical_pair(
            ReplicaEvidence("calibration-00", _receipt(), _state()),
            ReplicaEvidence("calibration-01", changed, _state()),
        )


@pytest.mark.parametrize("mutation", ["order", "dtype", "missing_moment"])
def test_checkpoint_structure_drift_stops_before_a11_metrics(mutation: str) -> None:
    changed = copy.deepcopy(_state())
    if mutation == "order":
        object.__setattr__(
            changed, "model_state", dict(reversed(changed.model_state.items()))
        )
    elif mutation == "dtype":
        model_state = changed.model_state
        assert isinstance(model_state, dict)
        model_state["detector.weight"] = model_state["detector.weight"].float()
    else:
        optimizer = changed.optimizer_state
        assert isinstance(optimizer, dict)
        states = optimizer["state"]
        assert isinstance(states, dict)
        member = states[0]
        assert isinstance(member, dict)
        member.pop("exp_avg_sq")

    with pytest.raises(StatisticalReplayError, match="exact"):
        compare_statistical_pair(
            ReplicaEvidence("calibration-00", _receipt(), _state()),
            ReplicaEvidence("calibration-01", _receipt(), changed),
        )


def test_calibration_derives_binary64_maxima_thresholds_and_digest() -> None:
    pairs = _pair_metrics()
    for index, pair in enumerate(pairs):
        metrics = dict(pair.metrics)
        metrics["gradient_norm.relative_difference"] = index * 0.0001
        pairs[index] = PairMetrics(
            pair.left_replica_id,
            pair.right_replica_id,
            pair.exact,
            metrics,
        )

    thresholds = derive_calibration_thresholds(pairs)
    maximum = 65 * 0.0001
    expected_threshold = 1.5 * maximum

    assert tuple(thresholds) == EXPECTED_METRIC_KEYS
    assert thresholds["gradient_norm.relative_difference"] == {
        "maximum": maximum,
        "maximum_hex": maximum.hex(),
        "threshold": expected_threshold,
        "threshold_hex": expected_threshold.hex(),
    }
    expected_digest = canonical_json_sha256(
        {
            "formula": "wave0-a11-pairwise-max-times-1.5-v1",
            "metric_keys": list(EXPECTED_METRIC_KEYS),
            "thresholds": thresholds,
        }
    )
    assert threshold_inventory_sha256(thresholds) == expected_digest


def test_zero_calibration_has_no_floor_and_rounding_uses_binary64() -> None:
    zero = derive_calibration_thresholds(_pair_metrics())
    assert all(entry["threshold"] == 0.0 for entry in zero.values())
    assert all(entry["threshold_hex"] == "0x0.0p+0" for entry in zero.values())

    maximum = math.nextafter(0.001, math.inf)
    rounded = derive_calibration_thresholds(
        _pair_metrics(metric_values={"gradient_norm.relative_difference": maximum})
    )["gradient_norm.relative_difference"]
    assert rounded["maximum"] == maximum
    assert rounded["maximum_hex"] == maximum.hex()
    assert rounded["threshold"] == 1.5 * maximum
    assert rounded["threshold_hex"] == (1.5 * maximum).hex()


def test_calibration_threshold_above_practical_ceiling_fails_closed() -> None:
    with pytest.raises(StatisticalReplayError, match="ceiling"):
        derive_calibration_thresholds(
            _pair_metrics(metric_values={"gradient_norm.relative_difference": 0.01})
        )


def test_calibration_rejects_wrong_pair_order_or_metric_inventory() -> None:
    reversed_pairs = list(reversed(_pair_metrics()))
    missing_metric = _pair_metrics()
    first = missing_metric[0]
    metrics = dict(first.metrics)
    metrics.pop(EXPECTED_METRIC_KEYS[-1])
    missing_metric[0] = PairMetrics(
        first.left_replica_id,
        first.right_replica_id,
        first.exact,
        metrics,
    )

    with pytest.raises(StatisticalReplayError, match="pair order"):
        derive_calibration_thresholds(reversed_pairs)
    with pytest.raises(StatisticalReplayError, match="metric inventory"):
        derive_calibration_thresholds(missing_metric)


def test_validation_accepts_threshold_equality_and_rejects_one_ulp_above() -> None:
    threshold = 0.0015
    thresholds = _thresholds(threshold)
    equal_pairs = _pair_metrics(
        phase="validation",
        metric_values={"gradient_norm.relative_difference": threshold},
    )
    above_pairs = list(equal_pairs)
    first = above_pairs[0]
    metrics = dict(first.metrics)
    metrics["gradient_norm.relative_difference"] = math.nextafter(threshold, math.inf)
    above_pairs[0] = PairMetrics(
        first.left_replica_id,
        first.right_replica_id,
        first.exact,
        metrics,
    )

    equal = summarize_validation(equal_pairs, thresholds)
    above = summarize_validation(above_pairs, thresholds)

    assert equal["all_pairs_within_thresholds"] is True
    assert equal["all_pairs_within_ceilings"] is True
    assert equal["errors"] == []
    assert above["all_pairs_within_thresholds"] is False
    assert above["all_pairs_within_ceilings"] is True
    assert above["errors"] == [
        (
            "validation-00/validation-01 "
            "gradient_norm.relative_difference exceeds calibration threshold"
        )
    ]


def test_validation_rejects_threshold_not_derived_from_stored_maximum() -> None:
    thresholds = _thresholds(0.0015)
    entry = thresholds["gradient_norm.relative_difference"]
    assert isinstance(entry, dict)
    entry["maximum"] = 0.0
    entry["maximum_hex"] = (0.0).hex()

    with pytest.raises(StatisticalReplayError, match="derivation"):
        summarize_validation(_pair_metrics(phase="validation"), thresholds)


def test_validation_median_is_the_binary64_average_of_middle_values() -> None:
    pairs = _pair_metrics(phase="validation")
    for index, pair in enumerate(pairs):
        metrics = dict(pair.metrics)
        metrics["gradient_norm.relative_difference"] = index * 1e-6
        pairs[index] = PairMetrics(
            pair.left_replica_id,
            pair.right_replica_id,
            pair.exact,
            metrics,
        )

    result = summarize_validation(pairs, _thresholds(0.01))
    summaries = result["summaries"]
    assert isinstance(summaries, Mapping)
    gradient = summaries["gradient_norm.relative_difference"]
    assert isinstance(gradient, Mapping)
    assert gradient == {
        "minimum": 0.0,
        "median": float.fromhex("0x1.10a137f38c543p-15"),
        "maximum": 65e-6,
    }


def test_independent_ceiling_can_fail_when_calibration_threshold_is_wider() -> None:
    thresholds = _thresholds(0.02)
    result = summarize_validation(
        _pair_metrics(
            phase="validation",
            metric_values={"gradient_norm.relative_difference": 0.011},
        ),
        thresholds,
    )

    assert result["all_pairs_within_thresholds"] is True
    assert result["all_pairs_within_ceilings"] is False
    assert result["errors"][0].endswith("exceeds practical ceiling")


@pytest.fixture(autouse=True)
def _bind_a11_model_document_hashes(monkeypatch: pytest.MonkeyPatch) -> None:
    empty_hash = canonical_json_sha256({})
    monkeypatch.setattr(
        receipts,
        "_APPROVED_MODEL_DOCUMENT_HASHES",
        {
            name: {"config": empty_hash, "processor": empty_hash}
            for name in ("rtdetr", "dinov2")
        },
    )


def _file_record(path: Path) -> dict[str, object]:
    return {
        "path": path.as_posix(),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def _write_audit_fixture(root: Path, name: str, content: object | None = None) -> Path:
    path = root / "audits" / f"{name}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    document = {"name": name} if content is None else content
    path.write_text(
        json.dumps(document, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="",
    )
    return path


def _model_cache_inventory(cache_root: Path) -> str:
    entries = []
    for path in sorted(item for item in cache_root.rglob("*") if item.is_file()):
        relative = path.relative_to(cache_root).as_posix()
        if relative.endswith(".metadata") and "/.cache/huggingface/download/" in (
            f"/{relative}"
        ):
            lines = path.read_text(encoding="utf-8").splitlines()
            content = f"{lines[0]}\n{lines[1]}\n".encode()
            size = len(content)
            digest = hashlib.sha256(content).hexdigest()
        else:
            size = path.stat().st_size
            digest = sha256_file(path)
        entries.append(
            {
                "path": relative,
                "size": size,
                "sha256": digest,
            }
        )
    return canonical_json_sha256({"files": entries})


def test_model_cache_inventory_normalizes_only_download_metadata_timestamp(
    tmp_path: Path,
) -> None:
    metadata = (
        tmp_path
        / "snapshot"
        / ".cache"
        / "huggingface"
        / "download"
        / "config.json.metadata"
    )
    metadata.parent.mkdir(parents=True)
    metadata.write_text("a" * 40 + "\n" + "b" * 64 + "\n123.5\n", encoding="utf-8")
    first = statistical_replay._model_cache_inventory_sha256(tmp_path)
    metadata.write_text("a" * 40 + "\n" + "b" * 64 + "\n999.25\n", encoding="utf-8")

    assert statistical_replay._model_cache_inventory_sha256(tmp_path) == first


def _retarget_model_contract(
    document: dict[str, object],
    *,
    run_id: str,
    image_id: str,
    gpu_uuid: str,
    driver: str,
) -> dict[str, object]:
    metadata = document["metadata"]
    normative = document["normative"]
    assert isinstance(metadata, dict)
    assert isinstance(normative, dict)
    environment_receipt = normative["parent_environment_receipt"]
    assert isinstance(environment_receipt, dict)
    environment_metadata = environment_receipt["metadata"]
    environment_normative = environment_receipt["normative"]
    assert isinstance(environment_metadata, dict)
    assert isinstance(environment_normative, dict)
    observed = environment_normative["observed"]
    assert isinstance(observed, dict)
    observed.update(
        {
            "gpu_uuid": gpu_uuid,
            "driver": driver,
            "runtime_image_digest": image_id,
        }
    )
    environment_metadata["run_id"] = run_id
    environment_metadata["receipt_content_sha256"] = _receipt_content_sha256(
        environment_receipt
    )

    environment = normative["environment"]
    assert isinstance(environment, dict)
    environment.update(
        {
            "gpu_uuid": gpu_uuid,
            "driver": driver,
            "runtime_image_digest": image_id,
        }
    )
    torch_execution = environment["torch_execution"]
    assert isinstance(torch_execution, dict)
    torch_execution["torch_selected_gpu_uuid"] = gpu_uuid.removeprefix("GPU-")
    torch_execution["nvidia_smi_gpu_uuid"] = gpu_uuid
    normative["environment_sha256"] = canonical_json_sha256(environment)
    normative["environment_receipt_sha256"] = _stored_receipt_sha256(
        environment_receipt
    )
    normative["environment_receipt_content_sha256"] = environment_metadata[
        "receipt_content_sha256"
    ]
    metadata["run_id"] = run_id
    metadata["receipt_content_sha256"] = _receipt_content_sha256(document)
    return document


def _write_replica_fixture(
    *,
    root: Path,
    replica_id: str,
    run_id: str,
    timestamp: str,
    image_id: str,
    gpu_uuid: str,
    driver: str,
    state_offset: float,
) -> tuple[Path, Path, Path]:
    model_contract = _retarget_model_contract(
        build_valid_model_contract_receipt(),
        run_id=run_id,
        image_id=image_id,
        gpu_uuid=gpu_uuid,
        driver=driver,
    )
    model_contract_digest = _stored_receipt_sha256(model_contract)
    state, evidence = _checkpoint_fixture(model_contract_digest)
    detector = state.model_state["detector.weight"]
    assert isinstance(detector, torch.Tensor)
    detector.view(-1)[0].add_(state_offset)
    evidence["state_digests"] = checkpoint_state_digests(state)
    evidence["checkpoint_state_sha256"] = checkpoint_state_sha256(state)

    checkpoint_path = root / "checkpoints" / replica_id / "step-000001.pt"
    checkpoint_path.parent.mkdir(parents=True)
    checkpoint_digest = save_checkpoint_atomic(state, checkpoint_path)
    feasibility = valid_feasibility_receipt()
    feasibility_metadata = feasibility["metadata"]
    feasibility_normative = feasibility["normative"]
    assert isinstance(feasibility_metadata, dict)
    assert isinstance(feasibility_normative, dict)
    feasibility_metadata.update({"run_id": run_id, "timestamp": timestamp})
    environment = feasibility_normative["environment"]
    assert isinstance(environment, dict)
    observed = environment["observed"]
    selected = environment["selected_cuda"]
    assert isinstance(observed, dict)
    assert isinstance(selected, dict)
    observed.update(
        {
            "gpu_uuid": gpu_uuid,
            "driver": driver,
            "runtime_image_digest": image_id,
        }
    )
    selected["selected_uuid"] = gpu_uuid.removeprefix("GPU-")
    parent_environment = model_contract["normative"]["environment"]
    environment["parent_environment_sha256"] = canonical_json_sha256(parent_environment)
    feasibility_normative["environment_sha256"] = canonical_json_sha256(environment)
    feasibility_normative["parent_environment_sha256"] = environment[
        "parent_environment_sha256"
    ]
    _bind_checkpoint_evidence(
        feasibility,
        model_contract=model_contract,
        model_contract_digest=model_contract_digest,
        checkpoint_digest=checkpoint_digest,
        evidence=evidence,
    )
    receipt_path = root / "receipts" / f"{replica_id}.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_receipt(receipt_path, feasibility)

    stdout_path = root / "logs" / f"{replica_id}.stdout.log"
    stderr_path = root / "logs" / f"{replica_id}.stderr.log"
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stdout_path.write_bytes(b"PASS\n")
    stderr_path.write_bytes(b"")
    invocation = {
        "schema_version": 1,
        "argv": [
            "val",
            "probe",
            "training-feasibility",
            "--model-contract",
            (root / "receipts" / "model-contract.json").as_posix(),
            "--checkpoint-root",
            checkpoint_path.parent.as_posix(),
            "--run-id",
            run_id,
            "--output",
            receipt_path.as_posix(),
        ],
        "exit_code": 0,
        "stdout": _file_record(stdout_path),
        "stderr": _file_record(stderr_path),
    }
    invocation_path = _write_audit_fixture(root, f"{replica_id}-invocation", invocation)
    return receipt_path, checkpoint_path, invocation_path


def _write_phase_manifest(
    parent: Path,
    phase: str,
    *,
    state_step: float = 1e-8,
) -> tuple[Path, Path, dict[str, object]]:
    phase_root = parent / phase
    phase_root.mkdir()
    run_id = f"wave0-a11-{phase}-20260827T130000000Z"
    image_marker = "3" if phase == "calibration" else "4"
    image_id = "sha256:" + image_marker * 64
    gpu_uuid = "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63"
    driver = "test-driver"
    cache_root = phase_root / "cache"
    cache_root.mkdir()
    (cache_root / "model-cache.bin").write_bytes(b"pinned-model-cache")
    cache_inventory_sha256 = _model_cache_inventory(cache_root)
    history_path = _write_audit_fixture(
        phase_root,
        "history",
        {
            "schema_version": 1,
            "historical_file_count": 64306,
            "historical_image_count": 21,
            "historical_file_inventory_sha256": (
                "e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95"
            ),
            "historical_image_inventory_sha256": (
                "9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f"
            ),
            "preserved": True,
        },
    )
    audits = {
        name: _file_record(_write_audit_fixture(phase_root, name))
        for name in ("identity", "image_inspect", "cache_inventory", "gpu_preflight")
    }
    lease_path = _write_audit_fixture(
        phase_root,
        "lease",
        {
            "schema_version": 1,
            "phase": phase,
            "lease_id": f"wave0-a11-{phase}-lease-test",
            "run_id": run_id,
            "source_commit": "1" * 40,
            "image_tag": f"vision-active-learning-loop:wave0-a11-{phase}-test",
            "image_id": image_id,
            "campaign_root": phase_root.as_posix(),
            "cache_root": cache_root.as_posix(),
            "cache_inventory_sha256": cache_inventory_sha256,
            "audit_bindings": audits,
            "gpu_uuid": gpu_uuid,
            "acquired_at": "2026-08-27T12:59:59+00:00",
        },
    )
    ids = expected_replica_ids(phase)
    replicas = []
    phase_offset = 0.0 if phase == "calibration" else 100.0 * state_step
    hour = "13" if phase == "calibration" else "15"
    for index, replica_id in enumerate(ids):
        timestamp = f"2026-08-27T{hour}:00:{index:02d}+00:00"
        receipt_path, checkpoint_path, invocation_path = _write_replica_fixture(
            root=phase_root,
            replica_id=replica_id,
            run_id=run_id,
            timestamp=timestamp,
            image_id=image_id,
            gpu_uuid=gpu_uuid,
            driver=driver,
            state_offset=phase_offset + index * state_step,
        )
        replicas.append(
            {
                "replica_id": replica_id,
                "container_id": f"{index + (1 if phase == 'calibration' else 101):064x}",
                "timestamp": timestamp,
                "invocation_audit": _file_record(invocation_path),
                "feasibility": _file_record(receipt_path),
                "checkpoint": _file_record(checkpoint_path),
            }
        )
    manifest: dict[str, object] = {
        "schema_version": 1,
        "phase": phase,
        "run_id": run_id,
        "campaign_root": phase_root.as_posix(),
        "source_commit": "1" * 40,
        "specification_commit": "b59b0d4407b98b460f6166ea7288ba6021dc7a78",
        "plan_commit": "2" * 40,
        "image_tag": f"vision-active-learning-loop:wave0-a11-{phase}-test",
        "image_id": image_id,
        "base_image_digest": (
            "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
        ),
        "owner_authorization_id": "OWNER-A11-TEST",
        "model_cache": {
            "path": cache_root.as_posix(),
            "inventory_sha256": cache_inventory_sha256,
        },
        "gpu": {
            "name": "NVIDIA GeForce RTX 4090",
            "uuid": gpu_uuid,
            "driver": driver,
            "cuda_runtime": "12.6",
        },
        "lease": {
            "lease_id": f"wave0-a11-{phase}-lease-test",
            **_file_record(lease_path),
        },
        "historical_preservation": _file_record(history_path),
        "audits": audits,
        "replicas": replicas,
    }
    manifest_path = phase_root / "phase-manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="",
    )
    return manifest_path, phase_root, manifest


def _gate_arguments(manifest_path: Path, phase_root: Path, output: Path) -> list[str]:
    return [
        "--phase-manifest",
        str(manifest_path),
        "--phase-root",
        str(phase_root),
        "--output",
        str(output),
    ]


def test_statistical_replay_cli_commands_are_lazy_manifest_discoverable() -> None:
    manifest = build_manifest(Path(__file__).parents[2] / "src")

    assert manifest["gate statistical-replay calibrate"].endswith(
        "gates.statistical_replay:calibration_main"
    )
    assert manifest["gate statistical-replay validate"].endswith(
        "gates.statistical_replay:validation_main"
    )


def test_calibration_cli_loads_closed_manifest_and_publishes_thresholds(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest_path, phase_root, _ = _write_phase_manifest(tmp_path, "calibration")
    output = phase_root / "statistical-replay-calibration.json"

    result = statistical_replay.calibration_main(
        _gate_arguments(manifest_path, phase_root, output)
    )

    streams = capsys.readouterr()
    assert result == 0
    assert streams.out == (
        "WAVE0_A11_CALIBRATION_RECORDED / " "WAVE0_NOT_PASSED / WAVE1_FORBIDDEN\n"
    )
    assert streams.err == ""
    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["normative"]["threshold_inventory_sha256"]


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_top_level",
        "reordered_replicas",
        "bad_file_hash",
        "bad_audit",
        "bad_invocation_argv",
        "bad_invocation_stdout",
        "bad_history",
        "bad_lease",
    ],
)
def test_calibration_cli_rejects_malformed_phase_manifest_without_output(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    mutation: str,
) -> None:
    manifest_path, phase_root, manifest = _write_phase_manifest(tmp_path, "calibration")
    if mutation == "missing_top_level":
        manifest.pop("owner_authorization_id")
    elif mutation == "reordered_replicas":
        replicas = manifest["replicas"]
        assert isinstance(replicas, list)
        replicas[0], replicas[1] = replicas[1], replicas[0]
    elif mutation == "bad_file_hash":
        replicas = manifest["replicas"]
        assert isinstance(replicas, list)
        replicas[0]["checkpoint"]["sha256"] = "0" * 64
    elif mutation in {
        "bad_audit",
        "bad_invocation_argv",
        "bad_invocation_stdout",
    }:
        replicas = manifest["replicas"]
        assert isinstance(replicas, list)
        audit_path = Path(replicas[0]["invocation_audit"]["path"])
        if mutation == "bad_audit":
            replacement: object = {}
        elif mutation == "bad_invocation_argv":
            replacement = json.loads(audit_path.read_text(encoding="utf-8"))
            replacement["argv"][
                replacement["argv"].index("--output") + 1
            ] = "D:/fabricated/host/path.json"
        else:
            replacement = json.loads(audit_path.read_text(encoding="utf-8"))
            stdout_path = Path(replacement["stdout"]["path"])
            stdout_path.write_bytes(b"unexpected\n")
            replacement["stdout"] = _file_record(stdout_path)
        audit_path.write_text(
            json.dumps(replacement, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="",
        )
        replicas[0]["invocation_audit"] = _file_record(audit_path)
    elif mutation == "bad_history":
        history = manifest["historical_preservation"]
        assert isinstance(history, dict)
        history_path = Path(history["path"])
        content = json.loads(history_path.read_text(encoding="utf-8"))
        content["historical_file_inventory_sha256"] = "0" * 64
        history_path.write_text(
            json.dumps(content, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="",
        )
        manifest["historical_preservation"] = _file_record(history_path)
    else:
        lease = manifest["lease"]
        assert isinstance(lease, dict)
        lease_path = Path(lease["path"])
        content = json.loads(lease_path.read_text(encoding="utf-8"))
        content["image_id"] = "sha256:" + "9" * 64
        lease_path.write_text(
            json.dumps(content, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
            newline="",
        )
        manifest["lease"] = {
            "lease_id": lease["lease_id"],
            **_file_record(lease_path),
        }
    manifest_path.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="",
    )
    output = phase_root / "statistical-replay-calibration.json"

    result = statistical_replay.calibration_main(
        _gate_arguments(manifest_path, phase_root, output)
    )

    streams = capsys.readouterr()
    assert result == 2
    assert streams.out == ""
    assert streams.err
    assert not output.exists()


def test_validation_cli_binds_calibration_and_publishes_pass(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    calibration_manifest, calibration_root, _ = _write_phase_manifest(
        tmp_path, "calibration"
    )
    calibration_output = calibration_root / "statistical-replay-calibration.json"
    assert (
        statistical_replay.calibration_main(
            _gate_arguments(calibration_manifest, calibration_root, calibration_output)
        )
        == 0
    )
    capsys.readouterr()
    validation_manifest, validation_root, _ = _write_phase_manifest(
        tmp_path, "validation"
    )
    validation_output = validation_root / "statistical-replay-validation.json"
    arguments = _gate_arguments(validation_manifest, validation_root, validation_output)
    arguments[4:4] = ["--calibration-receipt", str(calibration_output)]

    result = statistical_replay.validation_main(arguments)

    streams = capsys.readouterr()
    assert result == 0
    assert streams.out == (
        "WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED\n"
    )
    assert streams.err == ""
    stored = json.loads(validation_output.read_text(encoding="utf-8"))
    assert stored["normative"]["status"] == "PASS"


def test_validation_cli_requires_same_owner_authorization_as_calibration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    calibration_manifest, calibration_root, _ = _write_phase_manifest(
        tmp_path, "calibration"
    )
    calibration_output = calibration_root / "statistical-replay-calibration.json"
    assert (
        statistical_replay.calibration_main(
            _gate_arguments(calibration_manifest, calibration_root, calibration_output)
        )
        == 0
    )
    capsys.readouterr()
    validation_manifest, validation_root, manifest = _write_phase_manifest(
        tmp_path, "validation"
    )
    manifest["owner_authorization_id"] = "OWNER-DIFFERENT"
    validation_manifest.write_text(
        json.dumps(manifest, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
        newline="",
    )
    validation_output = validation_root / "statistical-replay-validation.json"
    arguments = _gate_arguments(validation_manifest, validation_root, validation_output)
    arguments[4:4] = ["--calibration-receipt", str(calibration_output)]

    result = statistical_replay.validation_main(arguments)

    streams = capsys.readouterr()
    assert result == 2
    assert streams.out == ""
    assert streams.err
    assert not validation_output.exists()


def test_validation_cli_publishes_complete_numeric_fail(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    calibration_manifest, calibration_root, _ = _write_phase_manifest(
        tmp_path, "calibration", state_step=1e-8
    )
    calibration_output = calibration_root / "statistical-replay-calibration.json"
    assert (
        statistical_replay.calibration_main(
            _gate_arguments(calibration_manifest, calibration_root, calibration_output)
        )
        == 0
    )
    capsys.readouterr()
    validation_manifest, validation_root, _ = _write_phase_manifest(
        tmp_path, "validation", state_step=2e-7
    )
    validation_output = validation_root / "statistical-replay-validation.json"
    arguments = _gate_arguments(validation_manifest, validation_root, validation_output)
    arguments[4:4] = ["--calibration-receipt", str(calibration_output)]

    result = statistical_replay.validation_main(arguments)

    streams = capsys.readouterr()
    assert result == 2
    assert streams.out == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN\n"
    assert streams.err == ""
    stored = json.loads(validation_output.read_text(encoding="utf-8"))
    assert stored["normative"]["status"] == "FAIL"
    assert stored["normative"]["errors"] == sorted(stored["normative"]["errors"])


def test_calibration_cli_existing_output_is_return_3_and_byte_preserved(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest_path, phase_root, _ = _write_phase_manifest(tmp_path, "calibration")
    output = phase_root / "statistical-replay-calibration.json"
    output.write_bytes(b"historical")

    result = statistical_replay.calibration_main(
        _gate_arguments(manifest_path, phase_root, output)
    )

    streams = capsys.readouterr()
    assert result == 3
    assert streams.out == ""
    assert streams.err
    assert output.read_bytes() == b"historical"


def test_calibration_cli_rejects_output_outside_phase_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    manifest_path, phase_root, _ = _write_phase_manifest(tmp_path, "calibration")
    output = tmp_path / "outside-calibration.json"

    result = statistical_replay.calibration_main(
        _gate_arguments(manifest_path, phase_root, output)
    )

    streams = capsys.readouterr()
    assert result == 2
    assert streams.out == ""
    assert streams.err
    assert not output.exists()
