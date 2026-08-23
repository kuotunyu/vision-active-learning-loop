"""Fail-closed verification for the two Wave 0 model snapshots."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from ..artifacts.digests import sha256_file
from ..artifacts.receipts import atomic_write_receipt
from ..cli_manifest import command


RTDETR_REVISION = "cc5b50f32f0100caaa3bd275343e2fb17762c73d"
DINOV2_REVISION = "ed25f3a31f01632728cabb09d1542f84ab7b0056"
APPROVED_MODELS = {
    "PekingU/rtdetr_r18vd": RTDETR_REVISION,
    "facebook/dinov2-small": DINOV2_REVISION,
}
_DOWNLOAD_ALLOWLIST = (
    "README.md",
    "config.json",
    "model.safetensors",
    "preprocessor_config.json",
)
_APPROVED_LICENSE = "apache-2.0"


class ModelAssetError(ValueError):
    """Base class for rejected model asset evidence."""


class AssetMismatch(ModelAssetError):
    """Raised when a required file is absent or differs from its pin."""


class RevisionMismatch(ModelAssetError):
    """Raised when a snapshot does not prove the approved revision."""


class LicenseMismatch(ModelAssetError):
    """Raised when model-card evidence is not exactly Apache-2.0."""


class SourceMismatch(ModelAssetError):
    """Raised when installed Transformers source differs from its pin."""


class ArtifactBoundaryError(ModelAssetError):
    """Raised when model cache or receipt paths escape the external root."""


@dataclass(frozen=True)
class FileSpec:
    size: int
    sha256: str


@dataclass(frozen=True)
class FileObservation:
    size: int
    sha256: str


@dataclass(frozen=True)
class PinnedAssetSpec:
    name: str
    repo_id: str
    revision: str
    license: str
    license_evidence: str
    files: Mapping[str, FileSpec]
    transformers_version: str
    source_files: Mapping[str, FileSpec]


@dataclass(frozen=True)
class ModelAssetReceipt:
    name: str
    repo_id: str
    revision: str
    license: str
    license_evidence: FileObservation
    files: Mapping[str, FileObservation]
    config: Mapping[str, object]
    processor: Mapping[str, object]

    def as_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "repo_id": self.repo_id,
            "revision": self.revision,
            "license": self.license,
            "license_evidence": {
                "path": "README.md",
                "size": self.license_evidence.size,
                "sha256": self.license_evidence.sha256,
            },
            "files": {
                name: {"size": item.size, "sha256": item.sha256}
                for name, item in sorted(self.files.items())
            },
            "config": dict(self.config),
            "processor": dict(self.processor),
        }


_CANONICAL_MODEL_FILES: dict[str, dict[str, FileSpec]] = {
    "rtdetr": {
        "model.safetensors": FileSpec(
            80_904_152,
            "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
        ),
        "config.json": FileSpec(
            5_307,
            "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2",
        ),
        "preprocessor_config.json": FileSpec(
            841,
            "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a",
        ),
        "README.md": FileSpec(
            9_102,
            "0d6d6065595011f4897e724f11d2b86494764eba68e3514cc6c70f0a851e539e",
        ),
    },
    "dinov2": {
        "model.safetensors": FileSpec(
            88_249_960,
            "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1",
        ),
        "config.json": FileSpec(
            547,
            "1809f83e3bdb1609a501a610ad4a742f4fd8ae44d72ca4aa0df52d1f2ac8628d",
        ),
        "preprocessor_config.json": FileSpec(
            436,
            "14e780d86fa1861f8751f868d7f45425b5feb55c38ca26f152ca5097ab30f828",
        ),
        "README.md": FileSpec(
            3_033,
            "4c20dca454a8e5c670e8de5c7e6040f512aeca5438516f7623eedc4e3b00599c",
        ),
    },
}

_CANONICAL_SOURCE_FILES = {
    "models/bit/image_processing_bit.py": FileSpec(
        1_260,
        "62ad10de9929cb0a5722d9a9c93d90e6a38f7e4c05b50811d8492fb1ed40f2eb",
    ),
    "models/dinov2/configuration_dinov2.py": FileSpec(
        3_385,
        "5d90862b483744e951756f18b9b93bc1a04634c8744ddf74e8f3fb0b6ebe97f5",
    ),
    "models/dinov2/modeling_dinov2.py": FileSpec(
        25_000,
        "9c7e028bdadef16e4fe6c59833ac916fe0a7987d1ac968a6f19aca40359ea9f8",
    ),
    "models/rt_detr/configuration_rt_detr.py": FileSpec(
        9_028,
        "22c1b65c1385d35534658cbf1e91afa7174737134cb6a14ffdaffcd7b7a161a6",
    ),
    "models/rt_detr/configuration_rt_detr_resnet.py": FileSpec(
        3_538,
        "52a9a3ca8dd648f04bcb5f61b30ab927ca3f15187748736f7714f48af1f1ae73",
    ),
    "models/rt_detr/image_processing_rt_detr.py": FileSpec(
        24_476,
        "47ae2f0ca25a2763f4f42b27e8a2760bcbb0c2ef07d0f1e97aa779f9219fc558",
    ),
    "models/rt_detr/modeling_rt_detr.py": FileSpec(
        86_564,
        "fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3",
    ),
    "models/rt_detr/modeling_rt_detr_resnet.py": FileSpec(
        15_986,
        "fc13ccc6ba1e57862e4c129c9e74bb97f091012186c1104974b92d5ec7b4019c",
    ),
}


def _mapping(value: object, description: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssetMismatch(f"{description} must be a mapping")
    return value


def _file_specs(value: object, description: str) -> dict[str, FileSpec]:
    document = _mapping(value, description)
    result: dict[str, FileSpec] = {}
    for name, item in document.items():
        if not isinstance(name, str):
            raise AssetMismatch(f"{description} file names must be strings")
        details = _mapping(item, f"{description}.{name}")
        size = details.get("size")
        digest = details.get("sha256")
        if type(size) is not int or not isinstance(digest, str):
            raise AssetMismatch(f"{description}.{name} requires size and sha256")
        result[name] = FileSpec(size, digest)
    return result


def load_pinned_asset_specs(path: Path) -> dict[str, PinnedAssetSpec]:
    """Load the tracked contract only when it matches the compiled allowlist."""
    document = _mapping(
        yaml.safe_load(Path(path).read_text(encoding="utf-8")), "model config"
    )
    if document.get("schema_version") != 1:
        raise AssetMismatch("model config schema_version must be 1")
    if document.get("artifact_root_env") != "VAL_ARTIFACT_ROOT":
        raise AssetMismatch("model config must use VAL_ARTIFACT_ROOT")
    if document.get("cache_path") != "wave0/model_cache":
        raise AssetMismatch("model config cache_path must be wave0/model_cache")
    if document.get("offline_verification_default") is not True:
        raise AssetMismatch("offline verification must be the default")

    transformers = _mapping(document.get("transformers"), "transformers")
    version = transformers.get("version")
    if version != "5.15.0":
        raise SourceMismatch("Transformers version pin must be exactly 5.15.0")
    source_files = _file_specs(transformers.get("source_files"), "source_files")
    if source_files != _CANONICAL_SOURCE_FILES:
        raise SourceMismatch(
            "Transformers source pins differ from the approved contract"
        )

    models = _mapping(document.get("models"), "models")
    if set(models) != {"rtdetr", "dinov2"}:
        raise AssetMismatch("config must contain exactly rtdetr and dinov2")
    expected_identity = {
        "rtdetr": ("PekingU/rtdetr_r18vd", RTDETR_REVISION),
        "dinov2": ("facebook/dinov2-small", DINOV2_REVISION),
    }
    specs: dict[str, PinnedAssetSpec] = {}
    for name, identity in expected_identity.items():
        model = _mapping(models[name], f"models.{name}")
        repo_id, revision = identity
        if (model.get("repo_id"), model.get("revision")) != identity:
            raise RevisionMismatch(
                f"{name} must be exactly {repo_id}@{revision}"
            )
        if model.get("license") != _APPROVED_LICENSE:
            raise LicenseMismatch(f"{name} must declare Apache-2.0")
        if model.get("license_evidence") != "README.md":
            raise LicenseMismatch(f"{name} license evidence must be README.md")
        files = _file_specs(model.get("files"), f"models.{name}.files")
        if files != _CANONICAL_MODEL_FILES[name]:
            raise AssetMismatch(f"{name} file pins differ from the approved contract")
        specs[name] = PinnedAssetSpec(
            name=name,
            repo_id=repo_id,
            revision=revision,
            license=_APPROVED_LICENSE,
            license_evidence="README.md",
            files=files,
            transformers_version=str(version),
            source_files=source_files,
        )
    return specs


def _verify_snapshot_identity(spec: PinnedAssetSpec, root: Path) -> None:
    if root.name != spec.revision:
        raise RevisionMismatch(
            f"{spec.repo_id} snapshot revision must be {spec.revision}; "
            f"observed {root.name}"
        )
    expected_repo_names = {
        spec.repo_id.replace("/", "--"),
        f"models--{spec.repo_id.replace('/', '--')}",
    }
    if not any(parent.name in expected_repo_names for parent in root.parents):
        raise RevisionMismatch(f"snapshot path does not prove repository {spec.repo_id}")


def _model_card_license(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise LicenseMismatch("Apache-2.0 model-card evidence is missing") from error
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise LicenseMismatch("Apache-2.0 model-card front matter is missing")
    try:
        end = next(
            index
            for index, line in enumerate(lines[1:], 1)
            if line.strip() == "---"
        )
    except StopIteration as error:
        raise LicenseMismatch("Apache-2.0 model-card front matter is incomplete") from error
    front_matter = yaml.safe_load("\n".join(lines[1:end]))
    if not isinstance(front_matter, Mapping):
        raise LicenseMismatch("Apache-2.0 model-card front matter is invalid")
    value = front_matter.get("license")
    return str(value).strip().lower()


def _observe_file(path: Path, expected: FileSpec) -> FileObservation:
    try:
        size = path.stat().st_size
    except OSError as error:
        raise AssetMismatch(f"required asset is missing: {path.name}") from error
    if size != expected.size:
        raise AssetMismatch(
            f"{path.name} size mismatch: expected {expected.size}, observed {size}"
        )
    digest = sha256_file(path)
    if digest != expected.sha256:
        raise AssetMismatch(
            f"{path.name} SHA-256 mismatch: expected {expected.sha256}, observed {digest}"
        )
    return FileObservation(size=size, sha256=digest)


def _load_json_object(path: Path, description: str) -> Mapping[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AssetMismatch(f"{description} is not valid JSON") from error
    if not isinstance(value, Mapping):
        raise AssetMismatch(f"{description} must be a JSON object")
    return value


def verify_snapshot(
    spec: PinnedAssetSpec, snapshot_root: Path
) -> ModelAssetReceipt:
    """Verify one already-downloaded snapshot without network or model loading."""
    root = Path(snapshot_root)
    _verify_snapshot_identity(spec, root)
    license_path = root / spec.license_evidence
    observed_license = _model_card_license(license_path)
    if observed_license != _APPROVED_LICENSE:
        raise LicenseMismatch(
            f"{spec.repo_id} requires Apache-2.0 model-card evidence; "
            f"observed {observed_license!r}"
        )

    files = {
        name: _observe_file(root / name, expected)
        for name, expected in spec.files.items()
    }
    payload_names = {
        item.relative_to(root).as_posix()
        for item in root.rglob("*")
        if item.is_file() and ".cache" not in item.relative_to(root).parts
    }
    if payload_names != set(spec.files):
        raise AssetMismatch(
            "snapshot payload inventory differs from the four-file allowlist"
        )

    return ModelAssetReceipt(
        name=spec.name,
        repo_id=spec.repo_id,
        revision=spec.revision,
        license=observed_license,
        license_evidence=files[spec.license_evidence],
        files=files,
        config=_load_json_object(root / "config.json", "config.json"),
        processor=_load_json_object(
            root / "preprocessor_config.json", "preprocessor_config.json"
        ),
    )


def verify_transformers_source(spec: PinnedAssetSpec) -> dict[str, FileObservation]:
    """Hash the installed official Transformers config/model/processor sources."""
    observed_version = importlib.metadata.version("transformers")
    if observed_version != spec.transformers_version:
        raise SourceMismatch(
            f"Transformers must be {spec.transformers_version}; observed {observed_version}"
        )
    import transformers

    package_root = Path(transformers.__file__).resolve().parent
    return {
        name: _observe_file(package_root / Path(name), expected)
        for name, expected in spec.source_files.items()
    }


def _external_roots(cache_root: Path, output: Path) -> tuple[Path, Path]:
    configured = os.environ.get("VAL_ARTIFACT_ROOT")
    if not configured:
        raise ArtifactBoundaryError("VAL_ARTIFACT_ROOT is required")
    root_input = Path(configured).expanduser()
    if not root_input.is_absolute():
        raise ArtifactBoundaryError("VAL_ARTIFACT_ROOT must be absolute")
    try:
        root = root_input.resolve(strict=True)
    except OSError as error:
        raise ArtifactBoundaryError(
            "VAL_ARTIFACT_ROOT must resolve to an existing directory"
        ) from error
    wave_root = (root / "wave0").resolve(strict=False)
    expected_cache = (wave_root / "model_cache").resolve(strict=False)
    actual_cache = Path(cache_root).resolve(strict=False)
    actual_output = Path(output).resolve(strict=False)
    receipts_root = (wave_root / "receipts").resolve(strict=False)
    if actual_cache != expected_cache:
        raise ArtifactBoundaryError(
            "cache root must be VAL_ARTIFACT_ROOT/wave0/model_cache"
        )
    if (
        not actual_output.is_relative_to(receipts_root)
        or actual_output == receipts_root
    ):
        raise ArtifactBoundaryError(
            "receipt must be below VAL_ARTIFACT_ROOT/wave0/receipts"
        )
    return actual_cache, actual_output


def _direct_snapshot_root(cache_root: Path, spec: PinnedAssetSpec) -> Path:
    return (
        cache_root
        / "snapshots"
        / spec.repo_id.replace("/", "--")
        / spec.revision
    )


def _find_snapshot_root(cache_root: Path, spec: PinnedAssetSpec) -> Path:
    candidates = (
        _direct_snapshot_root(cache_root, spec),
        cache_root
        / f"models--{spec.repo_id.replace('/', '--')}"
        / "snapshots"
        / spec.revision,
    )
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    repo_roots = (
        _direct_snapshot_root(cache_root, spec).parent,
        candidates[1].parent,
    )
    for repo_root in repo_roots:
        if repo_root.is_dir():
            revisions = sorted(item for item in repo_root.iterdir() if item.is_dir())
            if revisions:
                return revisions[0]
    raise AssetMismatch(f"snapshot is missing for {spec.repo_id}@{spec.revision}")


def download_snapshot(spec: PinnedAssetSpec, cache_root: Path) -> Path:
    """Download only the four literal approved payload files at the exact commit."""
    if os.environ.get("HF_HUB_OFFLINE", "").strip().lower() in {"1", "true", "yes"}:
        raise ModelAssetError("cannot download while HF_HUB_OFFLINE is enabled")
    from huggingface_hub import snapshot_download

    target = _direct_snapshot_root(cache_root, spec)
    resolved = snapshot_download(
        repo_id=spec.repo_id,
        revision=spec.revision,
        local_dir=target,
        allow_patterns=list(_DOWNLOAD_ALLOWLIST),
    )
    return Path(resolved)


def _source_dict(
    version: str, observations: Mapping[str, FileObservation]
) -> dict[str, object]:
    return {
        "version": version,
        "files": {
            name: {"size": item.size, "sha256": item.sha256}
            for name, item in sorted(observations.items())
        },
    }


def _receipt_document(
    *,
    models: Mapping[str, ModelAssetReceipt],
    source: Mapping[str, object] | None,
    errors: Sequence[str],
) -> dict[str, object]:
    passed = not errors
    return {
        "receipt_type": "model-assets",
        "schema_version": 1,
        "normative": {
            "models": {
                name: receipt.as_dict() for name, receipt in sorted(models.items())
            },
            "transformers": dict(source or {"version": "5.15.0", "files": {}}),
            "invariants": {
                "all_assets_verified": passed,
                "exact_revisions": passed,
                "exact_file_inventory": passed,
                "apache_2_0_licenses": passed,
                "exact_transformers_source": passed,
                "data_root_unset": "VAL_DATA_ROOT" not in os.environ,
            },
            "status": "PASS" if passed else "FAIL",
            "errors": list(errors),
        },
        "metadata": {"timestamp": datetime.now(UTC).isoformat()},
    }


@command("assets verify")
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="val assets verify")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--download", action="store_true")
    arguments = parser.parse_args(argv)

    try:
        cache_root, output = _external_roots(arguments.cache_root, arguments.output)
    except ModelAssetError as error:
        print(error, file=sys.stderr)
        return 2

    models: dict[str, ModelAssetReceipt] = {}
    source: dict[str, object] | None = None
    errors: list[str] = []
    try:
        if "VAL_DATA_ROOT" in os.environ:
            raise ArtifactBoundaryError("Wave 0 model verification forbids a data root")
        specs = load_pinned_asset_specs(arguments.config)
        selected = ["rtdetr", "dinov2"]
        source_observations = verify_transformers_source(specs["rtdetr"])
        source = _source_dict(
            specs["rtdetr"].transformers_version, source_observations
        )
        for name in selected:
            spec = specs[name]
            snapshot = (
                download_snapshot(spec, cache_root)
                if arguments.download
                else _find_snapshot_root(cache_root, spec)
            )
            models[name] = verify_snapshot(spec, snapshot)
    except (ModelAssetError, OSError, ValueError) as error:
        errors.append(str(error))

    receipt = _receipt_document(models=models, source=source, errors=errors)
    atomic_write_receipt(output, receipt)
    print(receipt["normative"]["status"])
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
