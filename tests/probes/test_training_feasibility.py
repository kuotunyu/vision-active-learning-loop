from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import torch

import vision_active_learning_loop.probes.training_feasibility as feasibility_probe
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.probes.training_feasibility import (
    FeasibilityError,
    StepObservation,
    _prepare_labeled_batch,
    configure_determinism,
    deterministic_comparison,
    evaluate_step_observation,
    resolve_cli_paths,
)


HASH = "a" * 64


def _observation(**changes: object) -> StepObservation:
    values: dict[str, object] = {
        "ordered_losses": (3.25,),
        "finite_loss": True,
        "finite_gradients": True,
        "parameter_changed": True,
        "gradient_norm": 0.75,
        "peak_allocated_bytes": 8 * 1024**3,
        "peak_reserved_bytes": 9 * 1024**3,
        "wall_seconds": 1.25,
        "gpu_seconds": 1.0,
        "cuda_matmul_allow_tf32": False,
        "cudnn_allow_tf32": False,
        "cudnn_benchmark": False,
        "deterministic_algorithms": True,
        "deterministic_debug_mode": 2,
        "cublas_workspace_config": ":4096:8",
        "bf16_supported": True,
        "bf16_autocast_enabled": True,
        "deterministic_fallback_detected": False,
        "device": "cuda:0",
        "model_digest_before": "0" * 64,
        "model_digest_after": "1" * 64,
        "state_digests": {
            "model": "1" * 64,
            "optimizer": "2" * 64,
            "scheduler": "3" * 64,
            "scaler": "4" * 64,
            "rng": "5" * 64,
            "sampler": "6" * 64,
        },
        "checkpoint_state": None,
    }
    values.update(changes)
    return StepObservation(**values)


def _receipt() -> dict[str, object]:
    observation = _observation()
    comparison = deterministic_comparison(observation)
    return {
        "receipt_type": "feasibility",
        "schema_version": 1,
        "normative": {
            "model_sha256": HASH,
            "config_sha256": HASH,
            "source_sha256": HASH,
            "processor_sha256": HASH,
            "fixture_sha256": HASH,
            "probe_sha256": HASH,
            "environment_sha256": HASH,
            "model_contract_receipt_sha256": HASH,
            "checkpoint_sha256": HASH,
            "checkpoint_state_sha256": HASH,
            "observed_shapes": {
                "pixel_values": [2, 3, 640, 640],
                "pixel_mask": [2, 640, 640],
            },
            "invariants": {
                "adamw_update": True,
                "batch_size_two": True,
                "bf16_autocast": True,
                "bf16_supported": True,
                "checkpoint_content_verified": True,
                "checkpoint_round_trip": True,
                "cublas_workspace_configured": True,
                "cudnn_benchmark_disabled": True,
                "deterministic_algorithms": True,
                "deterministic_fallback_absent": True,
                "finite_gradients": True,
                "finite_loss": True,
                "gradient_clip_0_1": True,
                "parameter_changed": True,
                "peak_allocated_vram_within_22_gib": True,
                "resume_state_verified": True,
                "seed_17": True,
                "synthetic_labels_only": True,
                "tf32_disabled": True,
            },
            "ordered_losses": list(observation.ordered_losses),
            "state_digests": dict(observation.state_digests),
            "comparison": comparison,
            "step": {
                "loss_hex": float(3.25).hex(),
                "gradient_norm": 0.75,
                "finite_loss": True,
                "finite_gradients": True,
                "parameter_digest_before": "0" * 64,
                "parameter_digest_after": "1" * 64,
            },
            "checkpoint": {
                "file_sha256": HASH,
                "verified_file_sha256": HASH,
                "state_sha256_before_save": HASH,
                "state_sha256_after_load": HASH,
                "state_digests_before_save": dict(observation.state_digests),
                "state_digests_after_load": dict(observation.state_digests),
                "state_digests_after_restore": dict(observation.state_digests),
                "input_digests_verified": True,
            },
            "synthetic_labels": {
                "item_ids": ["wide-gradient", "tall-checker"],
                "class_labels": [[0], [3]],
                "boxes_per_image": [1, 1],
                "source": "tracked-synthetic-fixture-geometry-v1",
            },
            "runtime": {
                "seed": 17,
                "device": "cuda:0",
                "precision": "bfloat16",
                "tf32": False,
                "cuda_matmul_allow_tf32": False,
                "cudnn_allow_tf32": False,
                "cudnn_benchmark": False,
                "deterministic_algorithms": True,
                "deterministic_debug_mode": 2,
                "cublas_workspace_config": ":4096:8",
                "bf16_supported": True,
                "bf16_autocast_enabled": True,
                "deterministic_fallback_detected": False,
            },
            "recipe": {
                "seed": 17,
                "batch_size": 2,
                "optimizer": "AdamW",
                "detector_learning_rate": 1e-4,
                "backbone_learning_rate": 1e-5,
                "weight_decay": 1e-4,
                "gradient_clip_norm": 0.1,
                "fixture_set": "wave0-rtdetr-contract",
            },
            "timing": {
                "wall_seconds": 1.25,
                "gpu_seconds": 1.0,
                "checkpoint_write_seconds": 0.2,
                "checkpoint_load_seconds": 0.1,
            },
            "vram": {
                "peak_allocated_bytes": 8 * 1024**3,
                "peak_reserved_bytes": 9 * 1024**3,
                "allocated_limit_bytes": 22 * 1024**3,
            },
            "resume_verified": True,
            "status": "PASS",
            "errors": [],
        },
        "metadata": {"timestamp": "2026-08-23T00:00:00Z", "run_id": "a"},
    }


def test_tf32_is_disabled_and_runtime_controls_are_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch seeded determinism leaving TF32, benchmarking, or fallback warnings enabled."""
    monkeypatch.delenv("CUBLAS_WORKSPACE_CONFIG", raising=False)

    state = configure_determinism(seed=17)

    assert state.cuda_matmul_allow_tf32 is False
    assert state.cudnn_allow_tf32 is False
    assert state.cudnn_benchmark is False
    assert state.deterministic_algorithms is True
    assert state.deterministic_debug_mode == 2
    assert state.cublas_workspace_config == ":4096:8"


def test_initialized_cuda_requires_preconfigured_cublas_workspace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch setting the deterministic workspace too late for an existing CUDA model."""
    monkeypatch.delenv("CUBLAS_WORKSPACE_CONFIG", raising=False)
    monkeypatch.setattr(torch.cuda, "is_initialized", lambda: True)

    with pytest.raises(FeasibilityError, match="before CUDA initialization"):
        configure_determinism(seed=17)


def test_deterministic_comparison_is_exact_and_excludes_timing() -> None:
    """Catch timing jitter entering, or float rounding weakening, the comparison rule."""
    first = _observation()
    second = _observation(wall_seconds=99.0, gpu_seconds=98.0)
    changed = _observation(ordered_losses=(3.2500000000000004,))

    assert deterministic_comparison(first) == deterministic_comparison(second)
    assert deterministic_comparison(first) != deterministic_comparison(changed)
    assert deterministic_comparison(first)["ordered_loss_hex"] == [float(3.25).hex()]


@pytest.mark.parametrize(
    ("changes", "expected"),
    [
        ({"ordered_losses": (float("nan"),), "finite_loss": False}, "non-finite loss"),
        ({"finite_gradients": False}, "non-finite gradients"),
        ({"deterministic_fallback_detected": True}, "deterministic fallback"),
        ({"cuda_matmul_allow_tf32": True}, "TF32"),
        ({"bf16_supported": False}, "BF16"),
        ({"parameter_changed": False}, "parameter update"),
        ({"peak_allocated_bytes": 22 * 1024**3 + 1}, "22 GiB"),
    ],
)
def test_normative_runtime_failures_are_never_masked(
    changes: dict[str, object], expected: str
) -> None:
    """Catch a stop condition being converted into a passing or fallback observation."""
    with pytest.raises(FeasibilityError, match=expected):
        evaluate_step_observation(_observation(**changes))


def test_feasibility_receipt_is_schema_valid_and_content_addressed(
    tmp_path: Path,
) -> None:
    """Catch publishing incomplete or non-canonical feasibility evidence."""
    output = tmp_path / "feasibility.json"

    atomic_write_receipt(output, _receipt())
    stored = json.loads(output.read_text(encoding="utf-8"))

    validate_receipt(
        stored,
        Path(__file__).resolve().parents[2]
        / "schemas"
        / "feasibility-receipt.schema.json",
    )
    assert stored["normative"]["comparison"]["sha256"] == canonical_json_sha256(
        {
            "ordered_loss_hex": [float(3.25).hex()],
            "state_digests": stored["normative"]["state_digests"],
        }
    )


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        (
            lambda n: n["comparison"].update({"sha256": "0" * 64}),
            "comparison",
        ),
        (
            lambda n: n["runtime"].update({"tf32": True}),
            "tf32_disabled",
        ),
        (
            lambda n: n["vram"].update(
                {"peak_allocated_bytes": 22 * 1024**3 + 1}
            ),
            "peak_allocated_vram_within_22_gib",
        ),
        (
            lambda n: n["recipe"].update({"gradient_clip_norm": 1.0}),
            "gradient_clip_0_1",
        ),
        (
            lambda n: n["step"].update(
                {"parameter_digest_after": n["step"]["parameter_digest_before"]}
            ),
            "parameter_changed",
        ),
        (
            lambda n: n["step"].update({"finite_gradients": False}),
            "finite_gradients",
        ),
        (
            lambda n: n["synthetic_labels"].update({"class_labels": [[0], [2]]}),
            "synthetic_labels_only",
        ),
        (
            lambda n: n["runtime"].update({"precision": "float32"}),
            "precision",
        ),
        (
            lambda n: n["checkpoint"].update({"verified_file_sha256": "b" * 64}),
            "checkpoint_content_verified",
        ),
        (
            lambda n: n["checkpoint"]["state_digests_after_load"].update(
                {"optimizer": "b" * 64}
            ),
            "checkpoint_round_trip",
        ),
        (
            lambda n: n["checkpoint"]["state_digests_after_restore"].update(
                {"rng": "b" * 64}
            ),
            "resume_state_verified",
        ),
    ],
)
def test_rehashed_pass_receipt_cannot_contradict_embedded_evidence(
    tmp_path: Path, mutation: object, expected: str
) -> None:
    """Catch a self-consistent outer hash masking false feasibility evidence."""
    receipt = _receipt()
    normative = receipt["normative"]
    assert isinstance(normative, dict)
    assert callable(mutation)
    mutation(normative)

    with pytest.raises(ReceiptValidationError, match=expected):
        atomic_write_receipt(tmp_path / "feasibility.json", receipt)


def test_cli_manifest_discovers_training_feasibility_probe() -> None:
    """Catch omitting the required lazy CLI command."""
    source_root = Path(__file__).resolve().parents[2] / "src"

    manifest = build_manifest(source_root)

    assert manifest["probe training-feasibility"] == (
        "vision_active_learning_loop.probes.training_feasibility:main"
    )


def test_labeled_batch_uses_only_registered_synthetic_fixture_geometry() -> None:
    """Catch the feasibility smoke using unlabeled, external, or reordered samples."""
    batch, shapes, evidence = _prepare_labeled_batch(torch.device("cpu"), HASH)

    assert shapes == {
        "pixel_values": [2, 3, 640, 640],
        "pixel_mask": [2, 640, 640],
    }
    assert evidence == {
        "item_ids": ["wide-gradient", "tall-checker"],
        "class_labels": [[0], [3]],
        "boxes_per_image": [1, 1],
        "source": "tracked-synthetic-fixture-geometry-v1",
    }
    assert [label["class_labels"].tolist() for label in batch["labels"]] == [
        [0],
        [3],
    ]


def test_cli_paths_reject_data_root_and_noncanonical_locations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch checkpoint/receipt outputs escaping the external Wave 0 boundary."""
    wave = tmp_path / "wave0"
    receipts = wave / "receipts"
    checkpoints = wave / "checkpoints"
    receipts.mkdir(parents=True)
    checkpoints.mkdir()
    model_contract = receipts / "model-contract-receipt.json"
    model_contract.write_text("{}", encoding="utf-8")
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(tmp_path))

    resolved = resolve_cli_paths(
        model_contract,
        checkpoints / "feasibility-a",
        receipts / "feasibility-a.json",
    )
    assert resolved == (
        model_contract.resolve(),
        (checkpoints / "feasibility-a").resolve(),
        (receipts / "feasibility-a.json").resolve(),
    )

    monkeypatch.setenv("VAL_DATA_ROOT", str(tmp_path / "forbidden"))
    with pytest.raises(FeasibilityError, match="VAL_DATA_ROOT"):
        resolve_cli_paths(
            model_contract,
            checkpoints / "feasibility-a",
            receipts / "feasibility-a.json",
        )


def test_cli_reports_missing_training_backend_without_traceback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Catch a missing exact-stack backend escaping as an uncontrolled traceback."""
    paths = (tmp_path / "model.json", tmp_path / "checkpoints", tmp_path / "out.json")
    monkeypatch.setattr(feasibility_probe, "resolve_cli_paths", lambda *args: paths)
    monkeypatch.setattr(
        feasibility_probe,
        "_execute_probe",
        lambda *args: (_ for _ in ()).throw(ImportError("SciPy is required")),
    )

    exit_code = feasibility_probe.main(
        [
            "--model-contract",
            str(paths[0]),
            "--checkpoint-root",
            str(paths[1]),
            "--output",
            str(paths[2]),
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 2
    assert captured.err.strip() == "SciPy is required"
    assert "Traceback" not in captured.err


def test_schema_rejects_missing_resume_or_rng_digest(tmp_path: Path) -> None:
    """Catch incomplete checkpoint proof being published as PASS."""
    for field in ("resume_verified", "state_digests"):
        receipt = _receipt()
        normative = receipt["normative"]
        assert isinstance(normative, dict)
        if field == "state_digests":
            state_digests = normative[field]
            assert isinstance(state_digests, dict)
            del state_digests["rng"]
        else:
            del normative[field]

        with pytest.raises(ReceiptValidationError):
            atomic_write_receipt(tmp_path / f"{field}.json", receipt)
