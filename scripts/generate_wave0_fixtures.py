"""Build the two deterministic, label-free Wave 0 RGB fixtures."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from PIL import Image

_APPROVED_INPUT_SHA256 = (
    "4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f"
)
_APPROVED_TARGET_SHA256 = (
    "abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198"
)


def _canonical_json_sha256(value: Mapping[str, Any]) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and bool(is_junction()))


def load_manifest(path: Path) -> Mapping[str, Any]:
    """Load the tracked synthetic-fixture description."""
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(document, Mapping):
        raise TypeError("fixture manifest must be an object")
    if document.get("schema_version") != 1:
        raise ValueError("fixture manifest schema_version must be 1")
    if document.get("fixture_set") != "wave0-rtdetr-contract":
        raise ValueError("unexpected fixture set")
    images = document.get("images")
    if not isinstance(images, list) or len(images) != 2:
        raise ValueError("fixture manifest requires exactly two images")
    targets = document.get("targets")
    if not isinstance(targets, list) or len(targets) != 2:
        raise ValueError("fixture manifest requires exactly two targets")
    input_document = {
        "schema_version": document["schema_version"],
        "fixture_set": document["fixture_set"],
        "images": images,
    }
    target_document = {
        "schema_version": document["schema_version"],
        "fixture_set": document["fixture_set"],
        "targets": targets,
    }
    if _canonical_json_sha256(input_document) != _APPROVED_INPUT_SHA256:
        raise ValueError("fixture input digest differs")
    if _canonical_json_sha256(target_document) != _APPROVED_TARGET_SHA256:
        raise ValueError("fixture target digest differs")
    for item in images:
        if not isinstance(item, Mapping):
            raise TypeError("fixture image must be an object")
        filename = item.get("filename")
        if (
            not isinstance(filename, str)
            or Path(filename).is_absolute()
            or Path(filename).name != filename
        ):
            raise ValueError("fixture filename must be a plain relative name")
    return document


def _rgb_bytes(width: int, height: int, pattern: str) -> bytes:
    if pattern == "wide-gradient":
        return bytes(
            channel
            for y in range(height)
            for x in range(width)
            for channel in (x % 256, y % 256, (x + y) % 256)
        )
    if pattern == "tall-checker":
        return bytes(
            channel
            for y in range(height)
            for x in range(width)
            for channel in (
                255 - (x % 256),
                (2 * y) % 256,
                255 if ((x // 32) + (y // 32)) % 2 else 0,
            )
        )
    raise ValueError(f"unsupported fixture pattern: {pattern}")


def build_fixture_images(manifest: Mapping[str, Any]) -> list[Image.Image]:
    """Create fixture images in manifest order without reading any dataset."""
    images: list[Image.Image] = []
    for item in manifest["images"]:
        width = int(item["width"])
        height = int(item["height"])
        image = Image.frombytes(
            "RGB",
            (width, height),
            _rgb_bytes(width, height, str(item["pattern"])),
        )
        digest = hashlib.sha256(image.tobytes()).hexdigest()
        if digest != item.get("pixel_sha256"):
            raise ValueError(f"fixture pixel digest mismatch: {item.get('id')}")
        images.append(image)
    return images


def _external_wave_root() -> Path:
    configured = os.environ.get("VAL_ARTIFACT_ROOT")
    if not configured:
        raise ValueError("VAL_ARTIFACT_ROOT is required")
    if "VAL_DATA_ROOT" in os.environ:
        raise ValueError("VAL_DATA_ROOT must remain unset for Wave 0")
    root_input = Path(configured).expanduser()
    if (
        not root_input.is_absolute()
        or not root_input.is_dir()
        or _is_link_or_junction(root_input)
    ):
        raise ValueError(
            "VAL_ARTIFACT_ROOT must be an existing absolute non-link directory"
        )
    root = root_input.resolve(strict=True)
    wave_input = root / "wave0"
    if _is_link_or_junction(wave_input):
        raise ValueError("VAL_ARTIFACT_ROOT/wave0 link is forbidden")
    wave_root = wave_input.resolve(strict=False)
    if not wave_root.is_relative_to(root):
        raise ValueError("VAL_ARTIFACT_ROOT/wave0 escapes VAL_ARTIFACT_ROOT")
    return wave_root


def _prepare_destination(wave_root: Path, output_root: Path) -> Path:
    candidate = Path(output_root)
    if not candidate.is_absolute():
        raise ValueError("fixture output must be absolute")
    try:
        relative = candidate.relative_to(wave_root)
    except ValueError as error:
        raise ValueError(
            "fixture output must be below VAL_ARTIFACT_ROOT/wave0"
        ) from error
    if not relative.parts:
        raise ValueError("fixture output must be below VAL_ARTIFACT_ROOT/wave0")
    current = wave_root
    for part in relative.parts:
        current = current / part
        if _is_link_or_junction(current):
            raise ValueError("fixture output parent link is forbidden")
        if current.exists():
            resolved = current.resolve(strict=True)
            if not resolved.is_relative_to(wave_root):
                raise ValueError("fixture output parent escapes wave0")
    candidate.mkdir(parents=True, exist_ok=True)
    destination = candidate.resolve(strict=True)
    if not destination.is_relative_to(wave_root):
        raise ValueError("fixture output escapes VAL_ARTIFACT_ROOT/wave0")
    return destination


def materialize_fixtures(manifest: Mapping[str, Any], output_root: Path) -> list[Path]:
    """Write exact PPM fixtures only below ``VAL_ARTIFACT_ROOT/wave0``."""
    wave_root = _external_wave_root()
    destination = _prepare_destination(wave_root, output_root)

    paths: list[Path] = []
    for item, image in zip(manifest["images"], build_fixture_images(manifest)):
        filename = str(item["filename"])
        if Path(filename).is_absolute() or Path(filename).name != filename:
            raise ValueError("fixture filename must be a plain relative name")
        target_input = destination / filename
        if _is_link_or_junction(target_input):
            raise ValueError("fixture target link is forbidden")
        target = target_input.resolve(strict=False)
        if not target.is_relative_to(destination):
            raise ValueError("fixture filename escapes its output directory")
        expected = b"P6\n%d %d\n255\n" % image.size + image.tobytes()
        if target.exists():
            if target.read_bytes() != expected:
                raise ValueError(f"existing fixture differs: {target.name}")
        else:
            partial = target.with_name(f"{target.name}.partial")
            if partial.exists() or _is_link_or_junction(partial):
                raise ValueError(
                    f"preexisting fixture partial is forbidden: {partial.name}"
                )
            with partial.open("xb") as handle:
                handle.write(expected)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(partial, target)
        paths.append(target)
    return paths


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="generate_wave0_fixtures")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output-root", type=Path)
    arguments = parser.parse_args(argv)
    output_root = arguments.output_root
    if output_root is None:
        output_root = _external_wave_root() / "fixtures" / "synthetic" / "wave0"
    try:
        generated = materialize_fixtures(load_manifest(arguments.manifest), output_root)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 2
    for path in generated:
        print(path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
