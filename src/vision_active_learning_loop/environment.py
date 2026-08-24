"""Canonical environment contract and receipt command."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import yaml

from .artifacts.digests import canonical_json_sha256
from .artifacts.receipts import atomic_write_receipt
from .cli_manifest import command


APPROVED_BASE_IMAGE_DIGEST = (
    "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
)


class EnvironmentBoundaryError(ValueError):
    """Raised when receipt output crosses the approved artifact boundary."""


@dataclass(frozen=True)
class EnvironmentContract:
    python: str
    uv: str
    scipy: str
    torch: str
    torchvision: str
    transformers: str
    cuda_runtime: str
    pycocotools: str = "2.0.10"
    container_image_digest: str = APPROVED_BASE_IMAGE_DIGEST
    tf32: bool = False
    deterministic_algorithms: bool = True
    bf16_supported: bool = True
    canonical_os: str = "Linux"
    requires_wsl: bool = True
    gpu_name: str = "NVIDIA GeForce RTX 4090"

    @classmethod
    def from_yaml(cls, path: Path) -> EnvironmentContract:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, Mapping):
            raise ValueError("environment contract must be a YAML mapping")
        image = document.get("container_image")
        runtime = document.get("runtime")
        if not isinstance(image, Mapping) or not isinstance(runtime, Mapping):
            raise ValueError("environment contract requires image and runtime mappings")
        boolean_values = {
            "requires_wsl": document.get("requires_wsl"),
            "tf32": runtime.get("tf32"),
            "deterministic_algorithms": runtime.get("deterministic_algorithms"),
            "bf16_supported": runtime.get("bf16_supported"),
        }
        for name, value in boolean_values.items():
            if type(value) is not bool:
                raise ValueError(f"{name} must be a YAML boolean")
        return cls(
            python=str(document["python"]),
            uv=str(document["uv"]),
            scipy=str(document["scipy"]),
            torch=str(document["torch"]),
            torchvision=str(document["torchvision"]),
            transformers=str(document["transformers"]),
            cuda_runtime=str(document["cuda_runtime"]),
            pycocotools=str(document["pycocotools"]),
            container_image_digest=str(image["digest"]),
            tf32=boolean_values["tf32"],
            deterministic_algorithms=boolean_values["deterministic_algorithms"],
            bf16_supported=boolean_values["bf16_supported"],
            canonical_os=str(document["canonical_os"]),
            requires_wsl=boolean_values["requires_wsl"],
            gpu_name=str(document["gpu_name"]),
        )

    def as_dict(self) -> dict[str, object]:
        """Return the stable normative contract embedded in environment receipts."""
        return {
            "schema_version": 1,
            "python": self.python,
            "uv": self.uv,
            "scipy": self.scipy,
            "torch": self.torch,
            "torchvision": self.torchvision,
            "transformers": self.transformers,
            "pycocotools": self.pycocotools,
            "cuda_runtime": self.cuda_runtime,
            "canonical_os": self.canonical_os,
            "requires_wsl": self.requires_wsl,
            "gpu_name": self.gpu_name,
            "container_image_digest": self.container_image_digest,
            "tf32": self.tf32,
            "deterministic_algorithms": self.deterministic_algorithms,
            "bf16_supported": self.bf16_supported,
        }

    def validate(self, observed: Mapping[str, object]) -> list[str]:
        errors: list[str] = []
        if observed.get("os") != self.canonical_os or (
            self.requires_wsl and observed.get("wsl") is not True
        ):
            errors.append("canonical execution requires WSL2/OCI")
        expected = {
            "python": self.python,
            "uv": self.uv,
            "scipy": self.scipy,
            "torch": self.torch,
            "torchvision": self.torchvision,
            "transformers": self.transformers,
            "pycocotools": self.pycocotools,
            "cuda_runtime": self.cuda_runtime,
            "gpu_name": self.gpu_name,
            "container_image_digest": self.container_image_digest,
            "tf32": self.tf32,
            "deterministic_algorithms": self.deterministic_algorithms,
            "bf16_supported": self.bf16_supported,
        }
        for name, value in expected.items():
            actual = observed.get(name)
            if actual != value:
                errors.append(f"{name} must be exactly {value} (observed {actual})")
        return errors


def environment_invariants(
    contract: EnvironmentContract, observed: Mapping[str, object]
) -> dict[str, bool]:
    """Derive every environment gate boolean directly from observations."""
    gpu_uuid = observed.get("gpu_uuid")
    driver = observed.get("driver")
    runtime_image_digest = observed.get("runtime_image_digest")
    return {
        "approved_base_image": (
            observed.get("container_image_digest") == contract.container_image_digest
        ),
        "bf16_supported": observed.get("bf16_supported") is contract.bf16_supported,
        "canonical_gpu": (
            observed.get("gpu_name") == contract.gpu_name
            and _normalized_gpu_uuid(gpu_uuid) is not None
            and isinstance(driver, str)
            and bool(driver)
        ),
        "canonical_os_wsl": (
            observed.get("os") == contract.canonical_os
            and (not contract.requires_wsl or observed.get("wsl") is True)
        ),
        "data_root_unset": observed.get("data_root_unset") is True,
        "deterministic_algorithms": (
            observed.get("deterministic_algorithms")
            is contract.deterministic_algorithms
        ),
        "exact_cuda_runtime": observed.get("cuda_runtime") == contract.cuda_runtime,
        "exact_pycocotools": observed.get("pycocotools") == contract.pycocotools,
        "exact_python": observed.get("python") == contract.python,
        "exact_scipy": observed.get("scipy") == contract.scipy,
        "exact_torch": observed.get("torch") == contract.torch,
        "exact_torchvision": observed.get("torchvision") == contract.torchvision,
        "exact_transformers": (observed.get("transformers") == contract.transformers),
        "exact_uv": observed.get("uv") == contract.uv,
        "runtime_image_recorded": (
            isinstance(runtime_image_digest, str)
            and re.fullmatch(r"sha256:[0-9a-f]{64}", runtime_image_digest) is not None
        ),
        "tf32_disabled": observed.get("tf32") is contract.tf32,
    }


def _normalized_gpu_uuid(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    match = re.fullmatch(
        r"GPU-([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
        r"[0-9a-fA-F]{4}-[0-9a-fA-F]{12})",
        value,
    )
    return match.group(1).lower() if match is not None else None


def environment_errors(
    contract: EnvironmentContract, observed: Mapping[str, object]
) -> list[str]:
    """Derive the exact deterministic error inventory for an observation."""
    errors = contract.validate(observed)
    if observed.get("data_root_unset") is not True:
        errors.append("VAL_DATA_ROOT must remain unset for Wave 0")
    for name, passed in environment_invariants(contract, observed).items():
        if passed is not True and not any(name in error for error in errors):
            errors.append(name)
    return errors


def _installed_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


def _uv_version() -> str | None:
    try:
        result = subprocess.run(
            ["uv", "--version"], check=True, capture_output=True, text=True
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    fields = result.stdout.strip().split()
    if len(fields) < 2 or fields[0] != "uv":
        return None
    return fields[1]


def _wsl() -> bool:
    return "microsoft" in platform.release().lower() or "WSL_DISTRO_NAME" in os.environ


def _gpu() -> tuple[str | None, str | None, str | None]:
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,uuid,driver_version",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None, None, None
    lines = result.stdout.splitlines()
    if not lines:
        return None, None, None
    values = [part.strip() for part in lines[0].split(",")]
    if len(values) != 3 or not all(values):
        return None, None, None
    return values[0], values[1], values[2]


def _torch_runtime() -> tuple[str | None, bool | None, bool | None, bool | None]:
    try:
        import torch
    except ImportError:
        return None, None, None, None
    cuda_runtime = torch.version.cuda
    return (
        str(cuda_runtime) if cuda_runtime is not None else None,
        bool(torch.backends.cuda.matmul.allow_tf32),
        bool(torch.are_deterministic_algorithms_enabled()),
        bool(torch.cuda.is_bf16_supported()),
    )


def _configure_torch_runtime(contract: EnvironmentContract) -> None:
    try:
        import torch
    except ImportError:
        return
    torch.backends.cuda.matmul.allow_tf32 = contract.tf32
    torch.backends.cudnn.allow_tf32 = contract.tf32
    torch.use_deterministic_algorithms(contract.deterministic_algorithms)


def observe_environment() -> dict[str, object]:
    """Observe runtime state without accepting caller-provided expected values."""
    gpu_name, gpu_uuid, driver = _gpu()
    cuda_runtime, tf32, deterministic, bf16_supported = _torch_runtime()
    return {
        "schema_version": 1,
        "python": platform.python_version(),
        "uv": _uv_version(),
        "scipy": _installed_version("scipy"),
        "torch": _installed_version("torch"),
        "torchvision": _installed_version("torchvision"),
        "transformers": _installed_version("transformers"),
        "pycocotools": _installed_version("pycocotools"),
        "cuda_runtime": cuda_runtime,
        "gpu_name": gpu_name,
        "gpu_uuid": gpu_uuid,
        "driver": driver,
        "os": platform.system(),
        "wsl": _wsl(),
        "container_image_digest": os.environ.get("VAL_OBSERVED_BASE_IMAGE_DIGEST"),
        "runtime_image_digest": os.environ.get("VAL_RUNTIME_IMAGE_DIGEST"),
        "tf32": tf32,
        "deterministic_algorithms": deterministic,
        "bf16_supported": bf16_supported,
    }


def project_environment_input_errors(
    config_path: Path, pyproject_path: Path, dockerfile_path: Path
) -> list[str]:
    """Validate the tracked dependency inputs against the exact Wave 0 contract."""
    config = yaml.safe_load(Path(config_path).read_text(encoding="utf-8"))
    project = tomllib.loads(Path(pyproject_path).read_text(encoding="utf-8"))
    dockerfile = Path(dockerfile_path).read_text(encoding="utf-8")
    if not isinstance(config, Mapping):
        return ["environment config must be a YAML mapping"]
    errors: list[str] = []
    if str(config.get("scipy")) != "1.18.0":
        errors.append("environment config must declare scipy==1.18.0")
    project_table = project.get("project")
    dependencies = (
        project_table.get("dependencies", [])
        if isinstance(project_table, Mapping)
        else []
    )
    if not isinstance(dependencies, list) or "scipy==1.18.0" not in dependencies:
        errors.append("project dependencies must declare scipy==1.18.0")
    match = re.search(r"\buv==([^\s\\]+)", dockerfile)
    observed_uv = match.group(1) if match is not None else None
    if observed_uv != "0.8.15":
        errors.append(f"Dockerfile must install uv==0.8.15 (observed {observed_uv})")
    return errors


def _resolve_receipt_output(output: Path) -> Path:
    configured_root = os.environ.get("VAL_ARTIFACT_ROOT")
    if configured_root is None:
        raise EnvironmentBoundaryError("VAL_ARTIFACT_ROOT is required")
    root_input = Path(configured_root).expanduser()
    if not root_input.is_absolute():
        raise EnvironmentBoundaryError("VAL_ARTIFACT_ROOT must be absolute")
    try:
        root = root_input.resolve(strict=True)
    except (FileNotFoundError, OSError) as error:
        raise EnvironmentBoundaryError(
            "VAL_ARTIFACT_ROOT must resolve to an existing directory"
        ) from error
    if not root.is_dir():
        raise EnvironmentBoundaryError("VAL_ARTIFACT_ROOT must be a directory")
    wave_root = (root / "wave0").resolve(strict=False)
    if not wave_root.is_relative_to(root):
        raise EnvironmentBoundaryError(
            "VAL_ARTIFACT_ROOT/wave0 must resolve beneath VAL_ARTIFACT_ROOT"
        )
    candidate = output if output.is_absolute() else wave_root / output
    resolved = candidate.resolve(strict=False)
    if not resolved.is_relative_to(wave_root) or resolved == wave_root:
        raise EnvironmentBoundaryError(
            "receipt output must resolve beneath VAL_ARTIFACT_ROOT/wave0"
        )
    return resolved


@command("environment check")
def check(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="val environment check")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)

    if not arguments.run_id.strip():
        print("run_id must be non-empty", file=sys.stderr)
        return 2

    try:
        output = _resolve_receipt_output(arguments.output)
    except EnvironmentBoundaryError as error:
        print(error, file=sys.stderr)
        return 2
    if output.exists():
        print(
            "fresh output path is required for each environment attempt",
            file=sys.stderr,
        )
        return 2
    document = yaml.safe_load(arguments.config.read_text(encoding="utf-8"))
    if not isinstance(document, Mapping):
        raise ValueError("environment contract must be a YAML mapping")
    contract = EnvironmentContract.from_yaml(arguments.config)
    _configure_torch_runtime(contract)
    observed = observe_environment()
    observed["data_root_unset"] = "VAL_DATA_ROOT" not in os.environ
    errors = environment_errors(contract, observed)
    invariants = environment_invariants(contract, observed)
    contract_document = contract.as_dict()
    receipt = {
        "receipt_type": "environment",
        "schema_version": 1,
        "normative": {
            "contract": contract_document,
            "contract_sha256": canonical_json_sha256(contract_document),
            "observed": dict(observed),
            "invariants": dict(sorted(invariants.items())),
            "status": "FAIL" if errors else "PASS",
            "errors": errors,
        },
        "metadata": {
            "timestamp": datetime.now(UTC).isoformat(),
            "run_id": arguments.run_id,
        },
    }
    atomic_write_receipt(output, receipt)
    return 2 if errors else 0


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments.pop(0) != "check":
        print(
            "usage: python -m vision_active_learning_loop.environment check ...",
            file=sys.stderr,
        )
        return 2
    return check(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
