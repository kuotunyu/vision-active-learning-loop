import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

import vision_active_learning_loop.environment as environment
from vision_active_learning_loop.artifacts import receipts
from vision_active_learning_loop.artifacts.receipts import (
    ReceiptValidationError,
    validate_receipt,
)
from vision_active_learning_loop.environment import EnvironmentContract


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BASE_IMAGE_DIGEST = (
    "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
)
UV_VERSION = "0.8.15"


@pytest.fixture
def contract() -> EnvironmentContract:
    return EnvironmentContract(
        python="3.12.11",
        uv=UV_VERSION,
        scipy="1.18.0",
        torch="2.12.0+cu126",
        torchvision="0.27.0+cu126",
        transformers="5.15.0",
        cuda_runtime="12.6",
    )


@pytest.fixture
def canonical_observation() -> dict[str, object]:
    return {
        "schema_version": 1,
        "python": "3.12.11",
        "uv": UV_VERSION,
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


def _write_contract(path: Path) -> None:
    path.write_text(
        f"""
schema_version: 1
python: 3.12.11
uv: {UV_VERSION}
scipy: 1.18.0
torch: 2.12.0+cu126
torchvision: 0.27.0+cu126
transformers: 5.15.0
pycocotools: 2.0.10
cuda_runtime: '12.6'
canonical_os: Linux
requires_wsl: true
gpu_name: NVIDIA GeForce RTX 4090
container_image:
  requested: nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04
  digest: {BASE_IMAGE_DIGEST}
runtime:
  tf32: false
  deterministic_algorithms: true
  bf16_supported: true
""".lstrip(),
        encoding="utf-8",
    )


def test_contract_rejects_native_windows_as_canonical(
    contract: EnvironmentContract,
) -> None:
    errors = contract.validate(
        {"os": "Windows", "wsl": False, "gpu_name": "NVIDIA GeForce RTX 4090"}
    )
    assert "canonical execution requires WSL2/OCI" in errors


def test_contract_accepts_exact_core_versions(
    contract: EnvironmentContract, canonical_observation: dict[str, object]
) -> None:
    assert contract.validate(canonical_observation) == []


def test_contract_rejects_core_version_drift(
    contract: EnvironmentContract, canonical_observation: dict[str, object]
) -> None:
    drifted = canonical_observation | {"torch": "2.12.1+cu126"}

    assert contract.validate(drifted) == [
        "torch must be exactly 2.12.0+cu126 (observed 2.12.1+cu126)"
    ]


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        ("tf32", True, "tf32 must be exactly False (observed True)"),
        ("tf32", None, "tf32 must be exactly False (observed None)"),
        (
            "deterministic_algorithms",
            False,
            "deterministic_algorithms must be exactly True (observed False)",
        ),
        (
            "deterministic_algorithms",
            None,
            "deterministic_algorithms must be exactly True (observed None)",
        ),
        (
            "bf16_supported",
            False,
            "bf16_supported must be exactly True (observed False)",
        ),
        (
            "bf16_supported",
            None,
            "bf16_supported must be exactly True (observed None)",
        ),
    ],
)
def test_contract_rejects_unsafe_or_unknown_runtime_state(
    contract: EnvironmentContract,
    canonical_observation: dict[str, object],
    field: str,
    value: object,
    expected_error: str,
) -> None:
    errors = contract.validate(canonical_observation | {field: value})

    assert expected_error in errors


@pytest.mark.parametrize("digest", [None, "sha256:unapproved"])
def test_contract_requires_observed_approved_base_image_digest(
    contract: EnvironmentContract,
    canonical_observation: dict[str, object],
    digest: str | None,
) -> None:
    errors = contract.validate(
        canonical_observation | {"container_image_digest": digest}
    )

    assert (
        f"container_image_digest must be exactly {BASE_IMAGE_DIGEST} "
        f"(observed {digest})"
    ) in errors


def test_observation_does_not_fall_back_to_expected_image_digest(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("VAL_OBSERVED_BASE_IMAGE_DIGEST", raising=False)
    monkeypatch.delenv("VAL_CONTAINER_IMAGE_DIGEST", raising=False)
    monkeypatch.setattr(environment, "_gpu", lambda: (None, None, None))
    monkeypatch.setattr(
        environment, "_torch_runtime", lambda: (None, False, True, None)
    )

    observed = environment.observe_environment()

    assert observed["container_image_digest"] is None


def test_observation_uses_torch_runtime_cuda_and_reports_pycocotools(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_torch = SimpleNamespace(
        version=SimpleNamespace(cuda="12.6"),
        backends=SimpleNamespace(
            cuda=SimpleNamespace(matmul=SimpleNamespace(allow_tf32=False))
        ),
        are_deterministic_algorithms_enabled=lambda: True,
        cuda=SimpleNamespace(is_bf16_supported=lambda: True),
    )
    versions = {
        "torch": "2.12.0+cu999",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "pycocotools": "2.0.10",
    }
    monkeypatch.setitem(sys.modules, "torch", fake_torch)
    monkeypatch.setattr(environment, "_gpu", lambda: (None, None, None))
    monkeypatch.setattr(environment, "_installed_version", versions.get)

    observed = environment.observe_environment()

    assert observed["cuda_runtime"] == "12.6"
    assert observed.get("pycocotools") == "2.0.10"


@pytest.mark.parametrize(
    ("field", "value", "expected_error"),
    [
        (
            "cuda_runtime",
            "12.7",
            "cuda_runtime must be exactly 12.6 (observed 12.7)",
        ),
        (
            "pycocotools",
            "2.0.9",
            "pycocotools must be exactly 2.0.10 (observed 2.0.9)",
        ),
    ],
)
def test_contract_rejects_runtime_dependency_drift(
    contract: EnvironmentContract,
    canonical_observation: dict[str, object],
    field: str,
    value: str,
    expected_error: str,
) -> None:
    assert expected_error in contract.validate(canonical_observation | {field: value})


def test_contract_loads_machine_readable_yaml(tmp_path: Path) -> None:
    config = tmp_path / "wave0.yaml"
    _write_contract(config)

    loaded = EnvironmentContract.from_yaml(config)
    assert loaded == EnvironmentContract(
        python="3.12.11",
        uv=UV_VERSION,
        scipy="1.18.0",
        torch="2.12.0+cu126",
        torchvision="0.27.0+cu126",
        transformers="5.15.0",
        cuda_runtime="12.6",
    )
    assert getattr(loaded, "pycocotools", None) == "2.0.10"
    assert getattr(loaded, "container_image_digest", None) == BASE_IMAGE_DIGEST
    assert getattr(loaded, "tf32", None) is False
    assert getattr(loaded, "deterministic_algorithms", None) is True
    assert getattr(loaded, "bf16_supported", None) is True


def test_receipt_status_fails_when_runtime_state_is_unsafe(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "receipts" / "environment-receipt.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        environment,
        "observe_environment",
        lambda: canonical_observation | {"deterministic_algorithms": False},
    )

    exit_code = environment.check(
        ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
    )
    receipt = json.loads(output.read_text(encoding="utf-8"))

    assert exit_code == 2
    assert receipt["normative"]["status"] == "FAIL"
    assert (
        "deterministic_algorithms must be exactly True (observed False)"
        in receipt["normative"]["errors"]
    )


def test_check_requires_artifact_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "wave0.yaml"
    output = tmp_path / "outside.json"
    _write_contract(config)
    monkeypatch.delenv("VAL_ARTIFACT_ROOT", raising=False)

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    assert not output.exists()


@pytest.mark.parametrize("escape_kind", ["traversal", "absolute"])
def test_check_rejects_output_escape(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    escape_kind: str,
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    if escape_kind == "traversal":
        output = artifact_root / "wave0" / ".." / "escaped.json"
    else:
        output = tmp_path / "absolute-escape.json"

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    assert not output.exists()


def test_check_rejects_symlink_output_escape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact_root = tmp_path / "artifacts"
    wave_root = artifact_root / "wave0"
    outside = tmp_path / "outside"
    wave_root.mkdir(parents=True)
    outside.mkdir()
    link = wave_root / "linked"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlinks unavailable: {error}")
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = link / "escaped.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    assert not (outside / "escaped.json").exists()


def test_check_rejects_symlink_wave_root_escape(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact_root = tmp_path / "artifacts"
    outside = tmp_path / "outside"
    artifact_root.mkdir()
    outside.mkdir()
    try:
        (artifact_root / "wave0").symlink_to(outside, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlinks unavailable: {error}")
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "escaped.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    assert not (outside / "escaped.json").exists()


def test_check_rejects_set_data_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "receipts" / "receipt.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.setenv("VAL_DATA_ROOT", "forbidden")
    monkeypatch.setattr(
        environment, "observe_environment", lambda: canonical_observation
    )

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    receipt = json.loads(output.read_text(encoding="utf-8"))
    assert (
        "VAL_DATA_ROOT must remain unset for Wave 0" in receipt["normative"]["errors"]
    )


@pytest.mark.parametrize("stdout", ["", "only-name,only-uuid"])
def test_gpu_observation_handles_empty_or_malformed_output(
    monkeypatch: pytest.MonkeyPatch, stdout: str
) -> None:
    completed = subprocess.CompletedProcess(
        args=["nvidia-smi"], returncode=0, stdout=stdout, stderr=""
    )
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: completed)
    try:
        observed = environment._gpu()
    except (IndexError, ValueError):
        observed = "raised"

    assert observed == (None, None, None)


def test_contract_loads_and_rejects_uv_drift(tmp_path: Path) -> None:
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    contract = EnvironmentContract.from_yaml(config)
    observed = {
        "python": "3.12.11",
        "uv": "0.11.18",
        "scipy": "1.18.0",
        "torch": "2.12.0+cu126",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "pycocotools": "2.0.10",
        "cuda_runtime": "12.6",
        "os": "Linux",
        "wsl": True,
        "gpu_name": "NVIDIA GeForce RTX 4090",
        "container_image_digest": BASE_IMAGE_DIGEST,
        "tf32": False,
        "deterministic_algorithms": True,
        "bf16_supported": True,
    }

    assert contract.uv == UV_VERSION
    assert contract.validate(observed) == [
        "uv must be exactly 0.8.15 (observed 0.11.18)"
    ]


def test_environment_check_publishes_content_addressed_pass_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "receipts" / "environment-receipt.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        environment,
        "observe_environment",
        lambda: canonical_observation
        | {
            "schema_version": 1,
            "uv": UV_VERSION,
            "gpu_uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
            "driver": "591.86",
            "runtime_image_digest": "sha256:" + "1" * 64,
        },
    )

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 0
    )
    stored = json.loads(output.read_text(encoding="utf-8"))
    validate_receipt(
        stored, PROJECT_ROOT / "schemas" / "environment-receipt.schema.json"
    )
    assert stored["receipt_type"] == "environment"
    assert stored["normative"]["status"] == "PASS"
    assert stored["normative"]["invariants"]["exact_uv"] is True
    assert stored["metadata"]["receipt_content_sha256"]


def test_environment_check_never_overwrites_historical_receipt(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    output = artifact_root / "wave0" / "receipts" / "environment-receipt.json"
    output.parent.mkdir(parents=True)
    output.write_text(
        json.dumps({"status": "PASS", "deterministic_algorithms": False}),
        encoding="utf-8",
    )
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        environment,
        "observe_environment",
        lambda: canonical_observation
        | {
            "schema_version": 1,
            "uv": "0.11.18",
            "gpu_uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
            "driver": "591.86",
            "runtime_image_digest": "sha256:" + "1" * 64,
        },
    )

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    assert json.loads(output.read_text(encoding="utf-8")) == {
        "status": "PASS",
        "deterministic_algorithms": False,
    }


def test_environment_receipt_rejects_rehashed_forged_uv_pass(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "receipts" / "environment-receipt.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        environment,
        "observe_environment",
        lambda: canonical_observation
        | {
            "schema_version": 1,
            "uv": UV_VERSION,
            "gpu_uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
            "driver": "591.86",
            "runtime_image_digest": "sha256:" + "1" * 64,
        },
    )
    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 0
    )
    forged = json.loads(output.read_text(encoding="utf-8"))
    forged["normative"]["observed"]["uv"] = "0.11.18"
    forged["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        forged
    )

    with pytest.raises(ReceiptValidationError, match="exact_uv"):
        validate_receipt(
            forged, PROJECT_ROOT / "schemas" / "environment-receipt.schema.json"
        )


def test_environment_check_rejects_malformed_gpu_uuid(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "receipts" / "environment-receipt.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        environment,
        "observe_environment",
        lambda: canonical_observation
        | {
            "schema_version": 1,
            "uv": UV_VERSION,
            "gpu_uuid": "GPU-111111111111111111111111111111111111",
            "driver": "591.86",
            "runtime_image_digest": "sha256:" + "1" * 64,
        },
    )

    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    stored = json.loads(output.read_text(encoding="utf-8"))
    assert stored["normative"]["invariants"]["canonical_gpu"] is False


def test_environment_receipt_rejects_invented_fail_cause(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    canonical_observation: dict[str, object],
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    config = tmp_path / "wave0.yaml"
    _write_contract(config)
    output = artifact_root / "wave0" / "receipts" / "environment-receipt.json"
    monkeypatch.setenv("VAL_ARTIFACT_ROOT", str(artifact_root))
    monkeypatch.delenv("VAL_DATA_ROOT", raising=False)
    monkeypatch.setattr(
        environment,
        "observe_environment",
        lambda: canonical_observation
        | {
            "schema_version": 1,
            "uv": "0.11.18",
            "gpu_uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
            "driver": "591.86",
            "runtime_image_digest": "sha256:" + "1" * 64,
        },
    )
    assert (
        environment.check(
            ["--config", str(config), "--run-id", "test-run", "--output", str(output)]
        )
        == 2
    )
    forged = json.loads(output.read_text(encoding="utf-8"))
    forged["normative"]["errors"] = ["invented failure"]
    forged["metadata"]["receipt_content_sha256"] = receipts._receipt_content_sha256(
        forged
    )

    with pytest.raises(ReceiptValidationError, match="errors"):
        validate_receipt(
            forged, PROJECT_ROOT / "schemas" / "environment-receipt.schema.json"
        )
