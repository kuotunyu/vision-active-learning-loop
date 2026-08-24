"""Fail-closed verification for the two Wave 0 model snapshots."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
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
    etag: str = ""
    blob_id: str = ""


@dataclass(frozen=True)
class FileObservation:
    size: int
    sha256: str


@dataclass(frozen=True)
class HuggingFaceFileMetadata:
    metadata_path: str
    commit_hash: str
    etag: str
    blob_id: str
    timestamp: float
    size: int
    sha256: str


@dataclass(frozen=True)
class HuggingFaceMetadataReceipt:
    commit_hash: str
    files: Mapping[str, HuggingFaceFileMetadata]
    inventory: Mapping[str, FileObservation]


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
    huggingface_metadata: HuggingFaceMetadataReceipt
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
            "huggingface_metadata": {
                "commit_hash": self.huggingface_metadata.commit_hash,
                "files": {
                    name: {
                        "metadata_path": item.metadata_path,
                        "commit_hash": item.commit_hash,
                        "etag": item.etag,
                        "blob_id": item.blob_id,
                        "timestamp": item.timestamp,
                        "size": item.size,
                        "sha256": item.sha256,
                    }
                    for name, item in sorted(self.huggingface_metadata.files.items())
                },
                "inventory": {
                    name: {"size": item.size, "sha256": item.sha256}
                    for name, item in sorted(
                        self.huggingface_metadata.inventory.items()
                    )
                },
            },
            "config": dict(self.config),
            "processor": dict(self.processor),
        }


_CANONICAL_MODEL_FILES: dict[str, dict[str, FileSpec]] = {
    "rtdetr": {
        "model.safetensors": FileSpec(
            80_904_152,
            "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
            "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093",
            "99878207a862ab963eafb175cd79c4364fa1db62",
        ),
        "config.json": FileSpec(
            5_307,
            "0be0da088d7c323ebc32e7b564ffb7c072fd0c6197e0aba67a38d3eaf304e0e2",
            "2bc5c87afa01965b4d6dd65053a0b087c013aee2",
            "2bc5c87afa01965b4d6dd65053a0b087c013aee2",
        ),
        "preprocessor_config.json": FileSpec(
            841,
            "ffb4b9461a1dad746be8f0f9c8330ed7743a1ba5fba4f75c232cd281b3d4c64a",
            "0eaa5c051317a3725f47218ae30b6e654f0ece36",
            "0eaa5c051317a3725f47218ae30b6e654f0ece36",
        ),
        "README.md": FileSpec(
            9_102,
            "0d6d6065595011f4897e724f11d2b86494764eba68e3514cc6c70f0a851e539e",
            "8911a08498e4b2a1118faa1d63b091c5b237b24d",
            "8911a08498e4b2a1118faa1d63b091c5b237b24d",
        ),
    },
    "dinov2": {
        "model.safetensors": FileSpec(
            88_249_960,
            "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1",
            "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1",
            "e13b8fec08e8dd9ac531165e7c8c0ec7d467952a",
        ),
        "config.json": FileSpec(
            547,
            "1809f83e3bdb1609a501a610ad4a742f4fd8ae44d72ca4aa0df52d1f2ac8628d",
            "5664b325e6258d3960fad8c4c1cff958f3cc2272",
            "5664b325e6258d3960fad8c4c1cff958f3cc2272",
        ),
        "preprocessor_config.json": FileSpec(
            436,
            "14e780d86fa1861f8751f868d7f45425b5feb55c38ca26f152ca5097ab30f828",
            "ff5b47c2edcd1d3556d63c01a65d93b58b9efce1",
            "ff5b47c2edcd1d3556d63c01a65d93b58b9efce1",
        ),
        "README.md": FileSpec(
            3_033,
            "4c20dca454a8e5c670e8de5c7e6040f512aeca5438516f7623eedc4e3b00599c",
            "6b3380957df44ed203ec1d5102e1245accbbbba9",
            "6b3380957df44ed203ec1d5102e1245accbbbba9",
        ),
    },
}

_CANONICAL_SOURCE_FILES = {
    "loss/loss_rt_detr.py": FileSpec(
        22_057,
        "01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6",
    ),
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
        etag = details.get("etag", "")
        blob_id = details.get("blob_id", "")
        if (
            type(size) is not int
            or not isinstance(digest, str)
            or not isinstance(etag, str)
            or not isinstance(blob_id, str)
        ):
            raise AssetMismatch(f"{description}.{name} requires size and sha256")
        result[name] = FileSpec(size, digest, etag, blob_id)
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
            raise RevisionMismatch(f"{name} must be exactly {repo_id}@{revision}")
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


def _validate_approved_spec(spec: PinnedAssetSpec) -> None:
    expected_identity = {
        "rtdetr": ("PekingU/rtdetr_r18vd", RTDETR_REVISION),
        "dinov2": ("facebook/dinov2-small", DINOV2_REVISION),
    }
    identity = expected_identity.get(spec.name)
    if identity is None or (spec.repo_id, spec.revision) != identity:
        raise RevisionMismatch("asset spec differs from the approved contract")
    if spec.license != _APPROVED_LICENSE or spec.license_evidence != "README.md":
        raise LicenseMismatch("asset spec license differs from the approved contract")
    if dict(spec.files) != _CANONICAL_MODEL_FILES[spec.name]:
        raise AssetMismatch("asset spec file pins differ from the approved contract")
    if spec.transformers_version != "5.15.0":
        raise SourceMismatch("asset spec Transformers version is not approved")
    if dict(spec.source_files) != _CANONICAL_SOURCE_FILES:
        raise SourceMismatch("asset spec source pins differ from the approved contract")


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and bool(is_junction()))


def _safe_directory(path: Path, boundary: Path) -> Path:
    if _is_link_or_junction(path):
        raise ArtifactBoundaryError(
            f"directory symlink or junction is forbidden: {path.name}"
        )
    try:
        resolved_boundary = boundary.resolve(strict=True)
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise ArtifactBoundaryError(
            f"required directory is missing: {path.name}"
        ) from error
    if not resolved.is_relative_to(resolved_boundary):
        raise ArtifactBoundaryError(f"directory escapes verified root: {path.name}")
    if not resolved.is_dir():
        raise ArtifactBoundaryError(
            f"required directory is not a directory: {path.name}"
        )
    return resolved


def _safe_regular_file(path: Path, boundary: Path) -> Path:
    if _is_link_or_junction(path):
        raise ArtifactBoundaryError(
            f"file symlink or junction is forbidden: {path.name}"
        )
    try:
        resolved_boundary = boundary.resolve(strict=True)
        resolved = path.resolve(strict=True)
    except OSError as error:
        raise FileNotFoundError(path) from error
    if not resolved.is_relative_to(resolved_boundary):
        raise ArtifactBoundaryError(f"file escapes verified root: {path.name}")
    if not resolved.is_file():
        raise ArtifactBoundaryError(f"required file is not regular: {path.name}")
    return resolved


def _metadata_paths(spec: PinnedAssetSpec) -> set[str]:
    paths = {
        ".cache/huggingface/.gitignore",
        ".cache/huggingface/CACHEDIR.TAG",
        f".cache/huggingface/trees/{spec.revision}.json",
    }
    paths.update(f".cache/huggingface/download/{name}.metadata" for name in spec.files)
    paths.update(f".cache/huggingface/download/{name}.lock" for name in spec.files)
    return paths


def _unversioned_observation(path: Path) -> FileObservation:
    return FileObservation(size=path.stat().st_size, sha256=sha256_file(path))


def _verify_huggingface_metadata(
    spec: PinnedAssetSpec, root: Path
) -> HuggingFaceMetadataReceipt:
    metadata_root = root / ".cache" / "huggingface"
    try:
        _safe_directory(root / ".cache", root)
        _safe_directory(metadata_root, root)
        _safe_directory(metadata_root / "download", root)
        _safe_directory(metadata_root / "trees", root)
    except ArtifactBoundaryError as error:
        if "missing" in str(error):
            raise RevisionMismatch(
                "required Hugging Face metadata inventory is missing"
            ) from error
        raise

    expected_paths = _metadata_paths(spec)
    actual_paths: set[str] = set()
    actual_directories: set[str] = set()
    for entry in metadata_root.rglob("*"):
        relative = entry.relative_to(root).as_posix()
        if _is_link_or_junction(entry):
            raise ArtifactBoundaryError(
                f"Hugging Face metadata symlink or junction is forbidden: {relative}"
            )
        if entry.is_dir():
            _safe_directory(entry, root)
            actual_directories.add(relative)
        elif entry.is_file():
            _safe_regular_file(entry, root)
            actual_paths.add(relative)
        else:
            raise ArtifactBoundaryError(
                f"Hugging Face metadata entry is not regular: {relative}"
            )
    expected_directories = {
        ".cache/huggingface/download",
        ".cache/huggingface/trees",
    }
    if actual_directories != expected_directories or actual_paths != expected_paths:
        raise RevisionMismatch(
            "Hugging Face metadata inventory differs from the exact expected set"
        )

    inventory = {
        relative: _unversioned_observation(
            _safe_regular_file(root / Path(relative), root)
        )
        for relative in sorted(expected_paths)
    }
    tree_path = root / ".cache" / "huggingface" / "trees" / f"{spec.revision}.json"
    try:
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RevisionMismatch(
            "Hugging Face revision tree metadata is invalid"
        ) from error
    if not isinstance(tree, Mapping) or tree.get("format_version") != 1:
        raise RevisionMismatch("Hugging Face revision tree metadata is invalid")
    tree_files = tree.get("files")
    if not isinstance(tree_files, Mapping):
        raise RevisionMismatch("Hugging Face revision tree has no file inventory")

    file_metadata: dict[str, HuggingFaceFileMetadata] = {}
    for name, expected in spec.files.items():
        lock_relative = f".cache/huggingface/download/{name}.lock"
        if inventory[lock_relative].size != 0:
            raise RevisionMismatch(f"{name} Hugging Face lock must be zero bytes")
        metadata_relative = f".cache/huggingface/download/{name}.metadata"
        metadata_path = root / Path(metadata_relative)
        try:
            lines = metadata_path.read_text(encoding="utf-8").splitlines()
            timestamp = float(lines[2])
        except (OSError, ValueError, IndexError) as error:
            raise RevisionMismatch(
                f"invalid Hugging Face metadata for {name}"
            ) from error
        if len(lines) != 3 or not math.isfinite(timestamp) or timestamp <= 0:
            raise RevisionMismatch(f"invalid Hugging Face metadata for {name}")
        commit_hash, etag = lines[0], lines[1]
        if commit_hash != spec.revision:
            raise RevisionMismatch(
                f"{name} metadata commit must be {spec.revision}; observed {commit_hash}"
            )
        if etag != expected.etag:
            raise RevisionMismatch(
                f"{name} metadata etag must be {expected.etag}; observed {etag}"
            )
        tree_entry = tree_files.get(name)
        if not isinstance(tree_entry, Mapping):
            raise RevisionMismatch(f"revision tree is missing {name}")
        if tree_entry.get("size") != expected.size:
            raise RevisionMismatch(f"revision tree size differs for {name}")
        if tree_entry.get("blob_id") != expected.blob_id:
            raise RevisionMismatch(f"revision tree blob identity differs for {name}")
        if name == "model.safetensors" and (
            tree_entry.get("lfs_sha256") != expected.sha256
            or tree_entry.get("lfs_size") != expected.size
        ):
            raise RevisionMismatch(
                "revision tree LFS identity differs for model.safetensors"
            )
        observation = inventory[metadata_relative]
        file_metadata[name] = HuggingFaceFileMetadata(
            metadata_path=metadata_relative,
            commit_hash=commit_hash,
            etag=etag,
            blob_id=expected.blob_id,
            timestamp=timestamp,
            size=observation.size,
            sha256=observation.sha256,
        )
    return HuggingFaceMetadataReceipt(
        commit_hash=spec.revision,
        files=file_metadata,
        inventory=inventory,
    )


def _verify_payload_entries(spec: PinnedAssetSpec, root: Path) -> dict[str, Path]:
    expected_names = set(spec.files)
    entries = {entry.name: entry for entry in root.iterdir()}
    if set(entries) != expected_names | {".cache"}:
        raise AssetMismatch(
            "snapshot payload inventory differs from the four-file allowlist"
        )
    return {name: _safe_regular_file(entries[name], root) for name in expected_names}


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
    repo_parent = next(
        (parent for parent in root.parents if parent.name in expected_repo_names),
        None,
    )
    if repo_parent is None:
        raise RevisionMismatch(
            f"snapshot path does not prove repository {spec.repo_id}"
        )
    current = root
    while True:
        if _is_link_or_junction(current):
            raise ArtifactBoundaryError(
                f"snapshot directory symlink or junction is forbidden: {current.name}"
            )
        if current == repo_parent:
            break
        current = current.parent


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
            index for index, line in enumerate(lines[1:], 1) if line.strip() == "---"
        )
    except StopIteration as error:
        raise LicenseMismatch(
            "Apache-2.0 model-card front matter is incomplete"
        ) from error
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


def verify_snapshot(spec: PinnedAssetSpec, snapshot_root: Path) -> ModelAssetReceipt:
    """Verify one already-downloaded snapshot without network or model loading."""
    _validate_approved_spec(spec)
    root = Path(snapshot_root)
    _safe_directory(root, root)
    _verify_snapshot_identity(spec, root)
    huggingface_metadata = _verify_huggingface_metadata(spec, root)
    payload_paths = _verify_payload_entries(spec, root)
    license_path = payload_paths[spec.license_evidence]
    observed_license = _model_card_license(license_path)
    if observed_license != _APPROVED_LICENSE:
        raise LicenseMismatch(
            f"{spec.repo_id} requires Apache-2.0 model-card evidence; "
            f"observed {observed_license!r}"
        )

    files = {
        name: _observe_file(payload_paths[name], expected)
        for name, expected in spec.files.items()
    }

    return ModelAssetReceipt(
        name=spec.name,
        repo_id=spec.repo_id,
        revision=spec.revision,
        license=observed_license,
        license_evidence=files[spec.license_evidence],
        files=files,
        huggingface_metadata=huggingface_metadata,
        config=_load_json_object(payload_paths["config.json"], "config.json"),
        processor=_load_json_object(
            payload_paths["preprocessor_config.json"], "preprocessor_config.json"
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
    if not root.is_dir():
        raise ArtifactBoundaryError("VAL_ARTIFACT_ROOT must be a directory")
    wave_root = (root / "wave0").resolve(strict=False)
    if not wave_root.is_relative_to(root):
        raise ArtifactBoundaryError("wave0 resolves outside the artifact root")
    expected_cache = (wave_root / "model_cache").resolve(strict=False)
    actual_cache = Path(cache_root).resolve(strict=False)
    actual_output = Path(output).resolve(strict=False)
    receipts_root = (wave_root / "receipts").resolve(strict=False)
    if not expected_cache.is_relative_to(root):
        raise ArtifactBoundaryError("model_cache resolves outside the artifact root")
    if not receipts_root.is_relative_to(root):
        raise ArtifactBoundaryError("receipts resolves outside the artifact root")
    if actual_cache != expected_cache:
        raise ArtifactBoundaryError(
            "cache root must be VAL_ARTIFACT_ROOT/wave0/model_cache"
        )
    if not actual_output.is_relative_to(root):
        raise ArtifactBoundaryError("receipt resolves outside the artifact root")
    if (
        not actual_output.is_relative_to(receipts_root)
        or actual_output == receipts_root
    ):
        raise ArtifactBoundaryError(
            "receipt must be below VAL_ARTIFACT_ROOT/wave0/receipts"
        )
    return actual_cache, actual_output


def _direct_snapshot_root(cache_root: Path, spec: PinnedAssetSpec) -> Path:
    return cache_root / "snapshots" / spec.repo_id.replace("/", "--") / spec.revision


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


def _snapshot_within_cache(snapshot: Path, cache_root: Path) -> Path:
    if _is_link_or_junction(cache_root):
        raise ArtifactBoundaryError("model_cache symlink or junction is forbidden")
    try:
        resolved_cache = cache_root.resolve(strict=True)
        resolved_snapshot = snapshot.resolve(strict=True)
    except OSError as error:
        raise ArtifactBoundaryError("model snapshot path is missing") from error
    if not resolved_snapshot.is_relative_to(resolved_cache):
        raise ArtifactBoundaryError("model snapshot resolves outside model_cache")
    return snapshot


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
    run_id: str,
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
                "exact_huggingface_metadata": passed,
                "apache_2_0_licenses": passed,
                "exact_transformers_source": passed,
                "data_root_unset": "VAL_DATA_ROOT" not in os.environ,
            },
            "status": "PASS" if passed else "FAIL",
            "errors": list(errors),
        },
        "metadata": {"timestamp": datetime.now(UTC).isoformat(), "run_id": run_id},
    }


@command("assets verify")
def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="val assets verify")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--download", action="store_true")
    arguments = parser.parse_args(argv)

    if not arguments.run_id.strip():
        print("run_id must be non-empty", file=sys.stderr)
        return 2

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
        source = _source_dict(specs["rtdetr"].transformers_version, source_observations)
        for name in selected:
            spec = specs[name]
            snapshot = (
                download_snapshot(spec, cache_root)
                if arguments.download
                else _find_snapshot_root(cache_root, spec)
            )
            snapshot = _snapshot_within_cache(snapshot, cache_root)
            models[name] = verify_snapshot(spec, snapshot)
    except (ModelAssetError, OSError, ValueError) as error:
        errors.append(str(error))

    receipt = _receipt_document(
        models=models,
        source=source,
        errors=errors,
        run_id=arguments.run_id,
    )
    atomic_write_receipt(output, receipt)
    print(receipt["normative"]["status"])
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
