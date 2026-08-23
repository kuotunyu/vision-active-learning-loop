"""Canonical environment contract and receipt command."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

import yaml

from .cli_manifest import command


@dataclass(frozen=True)
class EnvironmentContract:
    python: str
    torch: str
    torchvision: str
    transformers: str
    cuda_runtime: str
    canonical_os: str = "Linux"
    requires_wsl: bool = True
    gpu_name: str = "NVIDIA GeForce RTX 4090"

    @classmethod
    def from_yaml(cls, path: Path) -> EnvironmentContract:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(document, Mapping):
            raise ValueError("environment contract must be a YAML mapping")
        values = {field.name: document[field.name] for field in fields(cls)}
        return cls(**{key: str(value) if key != "requires_wsl" else bool(value) for key, value in values.items()})

    def validate(self, observed: Mapping[str, object]) -> list[str]:
        errors: list[str] = []
        if observed.get("os") != self.canonical_os or (
            self.requires_wsl and observed.get("wsl") is not True
        ):
            errors.append("canonical execution requires WSL2/OCI")
        expected = {
            "python": self.python,
            "torch": self.torch,
            "torchvision": self.torchvision,
            "transformers": self.transformers,
            "cuda_runtime": self.cuda_runtime,
            "gpu_name": self.gpu_name,
        }
        for name, value in expected.items():
            actual = observed.get(name)
            if actual != value:
                errors.append(f"{name} must be exactly {value} (observed {actual})")
        return errors


def _installed_version(distribution: str) -> str | None:
    try:
        return importlib.metadata.version(distribution)
    except importlib.metadata.PackageNotFoundError:
        return None


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
    first_gpu = result.stdout.splitlines()[0]
    name, uuid, driver = (part.strip() for part in first_gpu.split(",", maxsplit=2))
    return name, uuid, driver


def _torch_settings() -> tuple[bool | None, bool | None]:
    try:
        import torch
    except ImportError:
        return None, None
    return (
        bool(torch.backends.cuda.matmul.allow_tf32),
        bool(torch.are_deterministic_algorithms_enabled()),
    )


def observe_environment(config: Mapping[str, Any]) -> dict[str, object]:
    torch_version = _installed_version("torch")
    gpu_name, gpu_uuid, driver = _gpu()
    tf32, deterministic = _torch_settings()
    configured_image = config.get("container_image", {})
    image_digest = (
        os.environ.get("VAL_CONTAINER_IMAGE_DIGEST")
        or configured_image.get("digest")
        if isinstance(configured_image, Mapping)
        else None
    )
    cuda_runtime = None
    if torch_version and "+cu" in torch_version:
        cuda_digits = torch_version.rsplit("+cu", maxsplit=1)[1]
        cuda_runtime = f"{cuda_digits[:-1]}.{cuda_digits[-1]}"
    return {
        "schema_version": config.get("schema_version", 1),
        "python": platform.python_version(),
        "torch": torch_version,
        "torchvision": _installed_version("torchvision"),
        "transformers": _installed_version("transformers"),
        "cuda_runtime": cuda_runtime,
        "gpu_name": gpu_name,
        "gpu_uuid": gpu_uuid,
        "driver": driver,
        "os": platform.system(),
        "wsl": _wsl(),
        "container_image_digest": image_digest,
        "tf32": tf32,
        "deterministic_algorithms": deterministic,
    }


@command("environment check")
def check(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="val environment check")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args(argv)

    document = yaml.safe_load(arguments.config.read_text(encoding="utf-8"))
    if not isinstance(document, Mapping):
        raise ValueError("environment contract must be a YAML mapping")
    contract = EnvironmentContract.from_yaml(arguments.config)
    receipt = observe_environment(document)
    errors = contract.validate(receipt)
    receipt["status"] = "FAIL" if errors else "PASS"
    receipt["errors"] = errors
    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 2 if errors else 0


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if not arguments or arguments.pop(0) != "check":
        print("usage: python -m vision_active_learning_loop.environment check ...", file=sys.stderr)
        return 2
    return check(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
