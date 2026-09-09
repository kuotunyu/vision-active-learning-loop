"""Dataset manifest, frozen split, and public pool view for v0.2-lite.

Implements Sections 2.2 and 2.3 of the v0.2-lite protocol: PASCAL VOC parsing
into the four RDD classes, content-addressed item identity, exact-duplicate
collapse, the frozen hash split, the coverage audit, and the label-free view
handed to acquisition and training.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree

from PIL import Image, UnidentifiedImageError

from ..artifacts.digests import canonical_json_sha256
from ..artifacts.no_clobber import (
    NoClobberError,
    open_unique_staging_file,
    publish_staged_file_no_clobber,
)
from ..cli_manifest import command
from ..models.rtdetr_contract import RDD_LABELS

SCHEMA_VERSION = 1
RDD_CLASS_IDS = {label: index for index, label in enumerate(RDD_LABELS)}
SPLIT_SALT = "val-loop-split-v1"
SPLIT_MODULUS = 10000
TEST_UPPER_BOUND = 2000
MIN_TEST_BOXES_PER_CLASS = 20
MIN_POOL_IMAGES = 1500
ANNOTATION_SUFFIX = ".xml"

_SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
_INTEGER_PATTERN = re.compile(r"^-?\d+$")


class ManifestError(ValueError):
    """Raised when dataset inputs or manifest content are not usable."""


@dataclass(frozen=True)
class Box:
    class_id: int
    x_min: int
    y_min: int
    x_max: int
    y_max: int

    def as_row(self) -> list[int]:
        return [self.class_id, self.x_min, self.y_min, self.x_max, self.y_max]


@dataclass(frozen=True)
class Annotation:
    width: int
    height: int
    boxes: tuple[Box, ...]
    discarded_boxes: int


@dataclass(frozen=True)
class ScannedImage:
    item_id: str
    relative_path: str
    width: int
    height: int
    boxes: tuple[Box, ...]
    discarded_boxes: int


@dataclass(frozen=True)
class DatasetScan:
    images: tuple[ScannedImage, ...]
    alias_count: int


def _integer(element: ElementTree.Element | None, label: str) -> int:
    if element is None or element.text is None:
        raise ManifestError(f"{label} is missing")
    text = element.text.strip()
    if not _INTEGER_PATTERN.match(text):
        raise ManifestError(f"{label} must be an integer")
    return int(text)


def parse_voc_annotation(data: bytes) -> Annotation:
    """Parse one VOC annotation into RDD boxes and a discarded-label count."""
    try:
        root = ElementTree.fromstring(data)
    except ElementTree.ParseError as error:
        raise ManifestError("annotation is not well-formed XML") from error

    size = root.find("size")
    if size is None:
        raise ManifestError("annotation size is missing")
    width = _integer(size.find("width"), "annotation width")
    height = _integer(size.find("height"), "annotation height")
    if width <= 0 or height <= 0:
        raise ManifestError("annotation size must be positive")

    boxes: list[Box] = []
    discarded = 0
    for entry in root.findall("object"):
        name = entry.find("name")
        label = (name.text or "").strip() if name is not None else ""
        if label not in RDD_CLASS_IDS:
            discarded += 1
            continue
        bndbox = entry.find("bndbox")
        if bndbox is None:
            raise ManifestError(f"{label} object has no bndbox")
        x_min = _integer(bndbox.find("xmin"), "xmin")
        y_min = _integer(bndbox.find("ymin"), "ymin")
        x_max = _integer(bndbox.find("xmax"), "xmax")
        y_max = _integer(bndbox.find("ymax"), "ymax")
        if x_min >= x_max or y_min >= y_max:
            raise ManifestError(f"{label} box is degenerate")
        if x_min < 0 or y_min < 0 or x_max > width or y_max > height:
            raise ManifestError(f"{label} box leaves the declared image size")
        boxes.append(
            Box(
                class_id=RDD_CLASS_IDS[label],
                x_min=x_min,
                y_min=y_min,
                x_max=x_max,
                y_max=y_max,
            )
        )
    return Annotation(
        width=width, height=height, boxes=tuple(boxes), discarded_boxes=discarded
    )


def item_id_for_bytes(data: bytes) -> str:
    """Return the canonical content identity of one image file."""
    if not isinstance(data, bytes) or not data:
        raise ManifestError("image bytes are required")
    return hashlib.sha256(data).hexdigest()


def assign_split(split_group_id: str) -> str:
    """Return the frozen partition of one split group."""
    if not isinstance(split_group_id, str) or not split_group_id:
        raise ManifestError("split group id must be a non-empty string")
    digest = hashlib.sha256(
        SPLIT_SALT.encode("utf-8") + split_group_id.encode("utf-8")
    ).digest()
    remainder = int.from_bytes(digest[:8], "big") % SPLIT_MODULUS
    return "test" if remainder < TEST_UPPER_BOUND else "pool"


def _image_size(data: bytes, relative_path: str) -> tuple[int, int]:
    try:
        with Image.open(io.BytesIO(data)) as image:
            return int(image.width), int(image.height)
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise ManifestError(f"{relative_path} is not a readable image") from error


def scan_dataset(image_dir: Path, annotation_dir: Path) -> DatasetScan:
    """Pair every image with its annotation and collapse exact duplicates."""
    image_dir = Path(image_dir)
    annotation_dir = Path(annotation_dir)
    image_paths = sorted(path for path in image_dir.iterdir() if path.is_file())
    annotation_stems = {
        path.stem
        for path in annotation_dir.iterdir()
        if path.is_file() and path.suffix == ANNOTATION_SUFFIX
    }
    image_stems = {path.stem for path in image_paths}
    if not image_paths:
        raise ManifestError("image directory is empty")
    if len(image_stems) != len(image_paths):
        raise ManifestError("image stems must be unique")
    missing_annotations = sorted(image_stems - annotation_stems)
    if missing_annotations:
        raise ManifestError(f"annotation missing for {missing_annotations[0]}")
    orphan_annotations = sorted(annotation_stems - image_stems)
    if orphan_annotations:
        raise ManifestError(f"image missing for {orphan_annotations[0]}")

    scanned: list[ScannedImage] = []
    for path in image_paths:
        relative_path = path.name
        data = path.read_bytes()
        width, height = _image_size(data, relative_path)
        annotation = parse_voc_annotation(
            (annotation_dir / f"{path.stem}{ANNOTATION_SUFFIX}").read_bytes()
        )
        if (annotation.width, annotation.height) != (width, height):
            raise ManifestError(
                f"{relative_path} size disagrees with its annotation"
            )
        scanned.append(
            ScannedImage(
                item_id=item_id_for_bytes(data),
                relative_path=relative_path,
                width=width,
                height=height,
                boxes=annotation.boxes,
                discarded_boxes=annotation.discarded_boxes,
            )
        )

    retained: dict[str, ScannedImage] = {}
    alias_count = 0
    for image in sorted(scanned, key=lambda entry: entry.relative_path):
        existing = retained.get(image.item_id)
        if existing is None:
            retained[image.item_id] = image
            continue
        if (existing.width, existing.height, existing.boxes) != (
            image.width,
            image.height,
            image.boxes,
        ):
            raise ManifestError(
                f"{image.relative_path} duplicates {existing.relative_path} "
                "with a different annotation"
            )
        alias_count += 1
    images = tuple(
        sorted(retained.values(), key=lambda entry: entry.relative_path)
    )
    return DatasetScan(images=images, alias_count=alias_count)


def build_manifest(scan: DatasetScan, *, source_archive_sha256: str) -> dict:
    """Build the frozen manifest, assigning every retained image to a split."""
    if not isinstance(scan, DatasetScan):
        raise ManifestError("a dataset scan is required")
    if not isinstance(source_archive_sha256, str) or not _SHA256_PATTERN.match(
        source_archive_sha256
    ):
        raise ManifestError("source archive digest must be a lowercase SHA-256")
    item_ids = [image.item_id for image in scan.images]
    if len(set(item_ids)) != len(item_ids):
        raise ManifestError("manifest item ids must be unique")

    class_box_counts = {label: 0 for label in RDD_LABELS}
    box_count = 0
    discarded_box_count = 0
    negative_image_count = 0
    rows: list[dict[str, object]] = []
    for image in sorted(scan.images, key=lambda entry: entry.item_id):
        for box in image.boxes:
            class_box_counts[RDD_LABELS[box.class_id]] += 1
        box_count += len(image.boxes)
        discarded_box_count += image.discarded_boxes
        if not image.boxes:
            negative_image_count += 1
        rows.append(
            {
                "item_id": image.item_id,
                "width": image.width,
                "height": image.height,
                "split": assign_split(image.item_id),
                "boxes": [box.as_row() for box in image.boxes],
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": source_archive_sha256,
        "image_count": len(rows),
        "box_count": box_count,
        "class_box_counts": class_box_counts,
        "alias_count": scan.alias_count,
        "discarded_box_count": discarded_box_count,
        "negative_image_count": negative_image_count,
        "images": rows,
    }


def manifest_sha256(manifest: Mapping[str, object]) -> str:
    """Return the canonical content digest that binds every later artifact."""
    if not isinstance(manifest, Mapping):
        raise ManifestError("manifest must be a mapping")
    return canonical_json_sha256(manifest)


def _rows(manifest: Mapping[str, object]) -> Sequence[Mapping[str, object]]:
    rows = manifest.get("images")
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise ManifestError("manifest images must be a sequence")
    return rows


def audit_coverage(manifest: Mapping[str, object]) -> tuple[str, ...]:
    """Return the coverage failures that block the experiment, if any."""
    rows = _rows(manifest)
    pool_images = sum(1 for row in rows if row.get("split") == "pool")
    test_class_boxes = {label: 0 for label in RDD_LABELS}
    for row in rows:
        if row.get("split") != "test":
            continue
        for box in row.get("boxes", ()):
            test_class_boxes[RDD_LABELS[int(box[0])]] += 1

    errors: list[str] = []
    if pool_images < MIN_POOL_IMAGES:
        errors.append(
            f"pool split has {pool_images} images, below {MIN_POOL_IMAGES}"
        )
    for label in RDD_LABELS:
        observed = test_class_boxes[label]
        if observed < MIN_TEST_BOXES_PER_CLASS:
            errors.append(
                f"test split class {label} has {observed} boxes, "
                f"below {MIN_TEST_BOXES_PER_CLASS}"
            )
    return tuple(errors)


def public_pool_view(manifest: Mapping[str, object]) -> dict:
    """Return the label-free pool view given to acquisition and training."""
    rows = _rows(manifest)
    return {
        "schema_version": SCHEMA_VERSION,
        "manifest_sha256": manifest_sha256(manifest),
        "images": [
            {
                "item_id": row["item_id"],
                "width": row["width"],
                "height": row["height"],
            }
            for row in rows
            if row.get("split") == "pool"
        ],
    }


def write_json_no_clobber(path: Path, document: Mapping[str, object]) -> None:
    """Publish one canonical JSON document without overwriting anything."""
    encoded = (
        json.dumps(
            document,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")
    staging = open_unique_staging_file(path)
    try:
        with staging.handle as handle:
            handle.write(encoded)
            handle.flush()
        publish_staged_file_no_clobber(staging.path, path)
    finally:
        staging.path.unlink(missing_ok=True)


def _existing_directory(value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_dir():
        raise ManifestError(f"{label} directory is unavailable: {value}")
    return path


@command("lite manifest")
def manifest_main(argv: Sequence[str] | None = None) -> int:
    """Build, audit, and publish the frozen manifest plus its public view."""
    parser = argparse.ArgumentParser(prog="val lite manifest")
    parser.add_argument("--images", required=True)
    parser.add_argument("--annotations", required=True)
    parser.add_argument("--archive-sha256", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--public-view", required=True)
    arguments = parser.parse_args(list(argv) if argv is not None else None)

    output = Path(arguments.output)
    view_path = Path(arguments.public_view)
    try:
        images = _existing_directory(arguments.images, "images")
        annotations = _existing_directory(arguments.annotations, "annotations")
        for destination in (output, view_path):
            if destination.exists():
                raise ManifestError(
                    f"destination already exists: {destination.name}"
                )
        manifest = build_manifest(
            scan_dataset(images, annotations),
            source_archive_sha256=arguments.archive_sha256,
        )
    except ManifestError as error:
        print(f"lite manifest input error: {error}", file=sys.stderr)
        return 3

    summary = {
        key: manifest[key]
        for key in (
            "image_count",
            "box_count",
            "class_box_counts",
            "alias_count",
            "discarded_box_count",
            "negative_image_count",
        )
    }
    errors = audit_coverage(manifest)
    if errors:
        print(f"lite manifest summary: {json.dumps(summary)}", file=sys.stderr)
        for error in errors:
            print(f"lite manifest coverage: {error}", file=sys.stderr)
        return 2

    try:
        write_json_no_clobber(output, manifest)
        write_json_no_clobber(view_path, public_pool_view(manifest))
    except (NoClobberError, OSError) as error:
        print(f"lite manifest publication error: {error}", file=sys.stderr)
        return 3
    print(
        json.dumps(
            {**summary, "manifest_sha256": manifest_sha256(manifest)}, sort_keys=True
        )
    )
    return 0
