from pathlib import Path

import pytest

from vision_active_learning_loop.environment import EnvironmentContract


@pytest.fixture
def contract() -> EnvironmentContract:
    return EnvironmentContract(
        python="3.12.11",
        torch="2.12.0+cu126",
        torchvision="0.27.0+cu126",
        transformers="5.15.0",
        cuda_runtime="12.6",
    )


@pytest.fixture
def canonical_observation() -> dict[str, object]:
    return {
        "python": "3.12.11",
        "torch": "2.12.0+cu126",
        "torchvision": "0.27.0+cu126",
        "transformers": "5.15.0",
        "cuda_runtime": "12.6",
        "os": "Linux",
        "wsl": True,
        "gpu_name": "NVIDIA GeForce RTX 4090",
    }


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


def test_contract_loads_machine_readable_yaml(tmp_path: Path) -> None:
    config = tmp_path / "wave0.yaml"
    config.write_text(
        """
python: 3.12.11
torch: 2.12.0+cu126
torchvision: 0.27.0+cu126
transformers: 5.15.0
cuda_runtime: '12.6'
canonical_os: Linux
requires_wsl: true
gpu_name: NVIDIA GeForce RTX 4090
""".lstrip(),
        encoding="utf-8",
    )

    assert EnvironmentContract.from_yaml(config) == EnvironmentContract(
        python="3.12.11",
        torch="2.12.0+cu126",
        torchvision="0.27.0+cu126",
        transformers="5.15.0",
        cuda_runtime="12.6",
    )
