"""Contracts for the `val lite manifest` command."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest
from PIL import Image

from vision_active_learning_loop.lite.manifest import (
    MIN_POOL_IMAGES,
    assign_split,
    manifest_main,
    manifest_sha256,
)

ARCHIVE_SHA = "c" * 64


def _png(index: int) -> bytes:
    # Two channels encode the index so thousands of images stay byte-distinct.
    image = Image.new("RGB", (8, 6), (index % 256, (index // 256) % 256, 3))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _annotation(class_ids: list[int]) -> bytes:
    labels = ("D00", "D10", "D20", "D40")
    body = "".join(
        f"<object><name>{labels[class_id]}</name><bndbox>"
        f"<xmin>{class_id}</xmin><ymin>1</ymin><xmax>{class_id + 2}</xmax>"
        f"<ymax>4</ymax></bndbox></object>"
        for class_id in class_ids
    )
    return (
        "<annotation><size><width>8</width><height>6</height></size>"
        f"{body}</annotation>"
    ).encode("utf-8")


def _dataset(root: Path, count: int) -> tuple[Path, Path]:
    images = root / "images"
    annotations = root / "annotations" / "xmls"
    images.mkdir(parents=True)
    annotations.mkdir(parents=True)
    for index in range(count):
        (images / f"img_{index:06d}.jpg").write_bytes(_png(index))
        (annotations / f"img_{index:06d}.xml").write_bytes(_annotation([0, 1, 2, 3]))
    return images, annotations


def _argv(images: Path, annotations: Path, out: Path, **extra: str) -> list[str]:
    argv = [
        "--images",
        str(images),
        "--annotations",
        str(annotations),
        "--archive-sha256",
        extra.get("sha", ARCHIVE_SHA),
        "--output",
        str(out / "manifest.json"),
        "--public-view",
        str(out / "public-pool.json"),
    ]
    return argv


def test_manifest_command_writes_manifest_and_public_view(tmp_path: Path) -> None:
    # 2,000 images leave roughly 1,600 in the pool, above the 1,500 floor, and
    # every test image carries one box per class, above the 20-box floor.
    images, annotations = _dataset(tmp_path / "data", 2000)
    out = tmp_path / "out"
    out.mkdir()

    exit_code = manifest_main(_argv(images, annotations, out))

    assert exit_code == 0
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    view = json.loads((out / "public-pool.json").read_text(encoding="utf-8"))
    assert manifest["image_count"] == 2000
    assert manifest["source_archive_sha256"] == ARCHIVE_SHA
    assert view["manifest_sha256"] == manifest_sha256(manifest)
    assert len(view["images"]) == sum(
        1 for row in manifest["images"] if row["split"] == "pool"
    )
    assert len(view["images"]) >= MIN_POOL_IMAGES
    assert all("boxes" not in row for row in view["images"])


def test_manifest_command_rows_carry_the_frozen_split(tmp_path: Path) -> None:
    images, annotations = _dataset(tmp_path / "data", 2000)
    out = tmp_path / "out"
    out.mkdir()

    manifest_main(_argv(images, annotations, out))

    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert all(
        row["split"] == assign_split(row["item_id"]) for row in manifest["images"]
    )


def test_manifest_command_fails_closed_on_coverage(tmp_path: Path, capsys) -> None:
    images, annotations = _dataset(tmp_path / "data", 40)
    out = tmp_path / "out"
    out.mkdir()

    exit_code = manifest_main(_argv(images, annotations, out))

    assert exit_code == 2
    assert not (out / "manifest.json").exists()
    assert not (out / "public-pool.json").exists()
    assert "pool split has" in capsys.readouterr().err


def test_manifest_command_never_overwrites_an_existing_output(tmp_path: Path) -> None:
    images, annotations = _dataset(tmp_path / "data", 2000)
    out = tmp_path / "out"
    out.mkdir()
    (out / "manifest.json").write_text("frozen", encoding="utf-8")

    exit_code = manifest_main(_argv(images, annotations, out))

    assert exit_code == 3
    assert (out / "manifest.json").read_text(encoding="utf-8") == "frozen"
    assert not (out / "public-pool.json").exists()


def test_manifest_command_publishes_nothing_when_only_the_view_exists(
    tmp_path: Path,
) -> None:
    # A pre-existing public view must stop the run before the manifest is
    # written; otherwise a half-published pair would be left on disk.
    images, annotations = _dataset(tmp_path / "data", 2000)
    out = tmp_path / "out"
    out.mkdir()
    (out / "public-pool.json").write_text("frozen", encoding="utf-8")

    exit_code = manifest_main(_argv(images, annotations, out))

    assert exit_code == 3
    assert not (out / "manifest.json").exists()
    assert (out / "public-pool.json").read_text(encoding="utf-8") == "frozen"


def test_manifest_command_rejects_a_malformed_archive_digest(tmp_path: Path) -> None:
    images, annotations = _dataset(tmp_path / "data", 3)
    out = tmp_path / "out"
    out.mkdir()

    assert manifest_main(_argv(images, annotations, out, sha="nope")) == 3
    assert not (out / "manifest.json").exists()


@pytest.mark.parametrize("missing", ["images", "annotations"])
def test_manifest_command_rejects_a_missing_directory(
    tmp_path: Path, missing: str
) -> None:
    images, annotations = _dataset(tmp_path / "data", 3)
    out = tmp_path / "out"
    out.mkdir()
    if missing == "images":
        images = tmp_path / "absent"
    else:
        annotations = tmp_path / "absent"

    assert manifest_main(_argv(images, annotations, out)) == 3
