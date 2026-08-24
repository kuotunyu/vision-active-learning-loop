import json
from pathlib import Path

import pytest

import vision_active_learning_loop.environment as environment
from vision_active_learning_loop.artifacts import receipts
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    validate_receipt,
)
from vision_active_learning_loop.environment import EnvironmentContract


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCHEMA = PROJECT_ROOT / "schemas" / "environment-receipt.schema.json"
BASE_IMAGE_DIGEST = (
    "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
)
RUN_ID = "option-a-red"


@pytest.fixture
def canonical_observation() -> dict[str, object]:
    return {
        "schema_version": 1,
        "python": "3.12.11",
        "uv": "0.8.15",
        "scipy": "1.18.0",
        "torch": "2.12.0+cu126",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "pycocotools": "2.0.10",
        "cuda_runtime": "12.6",
        "os": "Linux",
        "wsl": True,
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "gpu_uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
        "driver": "591.86",
        "container_image_digest": BASE_IMAGE_DIGEST,
        "runtime_image_digest": "sha256:" + "1" * 64,
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
    }


def _run_check(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    observation: dict[str, object],
) -> tuple[int, dict[str, object]]:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    output = artifact_root / "wave0" / "receipts" / "environment.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(environment, "observe_environment", lambda: observation)
    exit_code = environment.check(
        [
            "--config",
            str(PROJECT_ROOT / "configs" / "environment" / "wave0.yaml"),
            "--run-id",
            RUN_ID,
            "--output",
            str(output),
        ]
    )
    return exit_code, json.loads(output.read_text(encoding="utf-8"))


def test_project_contract_rejects_wrong_docker_uv() -> None:
    errors = environment.project_environment_input_errors(
        PROJECT_ROOT / "configs" / "environment" / "wave0.yaml",
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "docker" / "wave0.Dockerfile",
    )

    assert "Dockerfile must install uv==0.8.15 (observed 0.11.18)" not in errors
    assert errors == []


def test_current_attempt_rejects_runtime_uv_drift(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    exit_code, receipt = _run_check(
        tmp_path,
        monkeypatch,
        canonical_observation | {"uv": "0.11.18"},
    )

    assert exit_code == 2
    assert receipt["metadata"]["run_id"] == RUN_ID
    assert receipt["normative"]["invariants"]["exact_uv"] is False


def test_project_contract_requires_declared_scipy() -> None:
    errors = environment.project_environment_input_errors(
        PROJECT_ROOT / "configs" / "environment" / "wave0.yaml",
        PROJECT_ROOT / "pyproject.toml",
        PROJECT_ROOT / "docker" / "wave0.Dockerfile",
    )

    assert "environment config must declare scipy==1.18.0" not in errors
    assert "project dependencies must declare scipy==1.18.0" not in errors
    assert errors == []


def test_current_attempt_fails_when_scipy_is_unimportable(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    exit_code, receipt = _run_check(
        tmp_path,
        monkeypatch,
        canonical_observation | {"scipy": None},
    )

    assert exit_code == 2
    assert receipt["normative"]["invariants"]["exact_scipy"] is False
    assert (
        "scipy must be exactly 1.18.0 (observed None)" in receipt["normative"]["errors"]
    )


def test_contract_rejects_runtime_scipy_drift(
    canonical_observation: dict[str, object],
) -> None:
    contract = EnvironmentContract.from_yaml(
        PROJECT_ROOT / "configs" / "environment" / "wave0.yaml"
    )

    assert contract.validate(canonical_observation | {"scipy": "1.17.1"}) == [
        "scipy must be exactly 1.18.0 (observed 1.17.1)"
    ]


def test_forged_receipt_cannot_copy_expected_scipy_into_observed(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    exit_code, forged = _run_check(
        tmp_path,
        monkeypatch,
        canonical_observation | {"scipy": None},
    )
    assert exit_code == 2
    forged["normative"]["observed"]["scipy"] = "1.18.0"
    forged["normative"]["status"] = "PASS"
    forged["normative"]["errors"] = []
    forged["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        forged
    )

    with pytest.raises(ReceiptValidationError, match="exact_scipy"):
        validate_receipt(forged, SCHEMA)


def test_environment_receipt_requires_exact_scipy_invariant(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    exit_code, incomplete = _run_check(tmp_path, monkeypatch, canonical_observation)
    assert exit_code == 0
    incomplete["normative"]["invariants"].pop("exact_scipy")
    incomplete["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        incomplete
    )

    with pytest.raises(ReceiptValidationError, match="exact_scipy"):
        validate_receipt(incomplete, SCHEMA)


def test_historical_receipt_is_not_current_for_a_new_run(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    exit_code, historical = _run_check(tmp_path, monkeypatch, canonical_observation)
    assert exit_code == 0
    historical["metadata"].pop("run_id")
    historical["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        historical
    )

    with pytest.raises(ReceiptValidationError, match="run_id"):
        receipts.validate_receipt_for_run(historical, SCHEMA, RUN_ID)
