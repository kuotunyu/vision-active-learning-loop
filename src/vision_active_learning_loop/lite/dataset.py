"""Sample loading, deterministic augmentation, and canvas geometry for v0.2-lite.

Preprocessing is delegated to the pinned Wave 0 processor contract, so boxes
are normalized against the padded 640x640 canvas rather than the original
image. Augmentation is derived per sample from a digest of the seed, epoch,
and item id, so it does not depend on batching or iteration order.
"""

from __future__ import annotations

import hashlib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image, ImageEnhance, UnidentifiedImageError

from ..artifacts.digests import canonical_json_sha256
from .manifest import Box, ManifestError, item_id_for_bytes

CANVAS_SIZE = 640
JITTER_STRENGTH = 0.1
AUGMENT_PREFIX = b"augment"
SAMPLER_PREFIX = b"sampler"
_UNIFORM_SCALE = float(2**64)


class DatasetError(ValueError):
    """Raised when sample inputs or canvas geometry are not usable."""


@dataclass(frozen=True)
class Sample:
    item_id: str
    image: Image.Image
    boxes: tuple[Box, ...]


@dataclass(frozen=True)
class AugmentationDecision:
    flip: bool
    brightness: float
    contrast: float
    saturation: float


def _uniforms(prefix: bytes, seed: int, epoch: int, item_id: str) -> tuple[float, ...]:
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise DatasetError("seed must be an integer")
    if not isinstance(epoch, int) or isinstance(epoch, bool) or epoch < 0:
        raise DatasetError("epoch must be a non-negative integer")
    if not isinstance(item_id, str) or not item_id:
        raise DatasetError("item id must be a non-empty string")
    digest = hashlib.sha256(
        prefix
        + str(seed).encode("utf-8")
        + str(epoch).encode("utf-8")
        + item_id.encode("utf-8")
    ).digest()
    return tuple(
        int.from_bytes(digest[8 * index : 8 * index + 8], "big") / _UNIFORM_SCALE
        for index in range(4)
    )


def build_image_index(image_dir: Path) -> dict[str, Path]:
    """Map every image's content identity to its lexicographically first path."""
    directory = Path(image_dir)
    index: dict[str, Path] = {}
    for path in sorted(path for path in directory.iterdir() if path.is_file()):
        item_id = item_id_for_bytes(path.read_bytes())
        index.setdefault(item_id, path)
    if not index:
        raise DatasetError("image directory is empty")
    return index


def load_sample(index: Mapping[str, Path], row: Mapping[str, Any]) -> Sample:
    """Load one manifest row into an RGB image and its pixel boxes."""
    item_id = row.get("item_id")
    path = index.get(item_id) if isinstance(item_id, str) else None
    if path is None:
        raise DatasetError(f"{item_id} is absent from the image index")
    try:
        with Image.open(path) as opened:
            image = opened.convert("RGB")
    except (UnidentifiedImageError, OSError, ValueError) as error:
        raise DatasetError(f"{item_id} is not a readable image") from error
    if image.size != (row.get("width"), row.get("height")):
        raise DatasetError(f"{item_id} size disagrees with the manifest")
    try:
        boxes = tuple(
            Box(
                class_id=int(entry[0]),
                x_min=int(entry[1]),
                y_min=int(entry[2]),
                x_max=int(entry[3]),
                y_max=int(entry[4]),
            )
            for entry in row.get("boxes", ())
        )
    except (TypeError, ValueError, IndexError) as error:
        raise DatasetError(f"{item_id} has a malformed box row") from error
    return Sample(item_id=item_id, image=image, boxes=boxes)


def flip_sample(sample: Sample) -> Sample:
    """Mirror the image and its boxes about the vertical centre line."""
    if not isinstance(sample, Sample):
        raise DatasetError("a sample is required")
    width = sample.image.width
    return Sample(
        item_id=sample.item_id,
        image=sample.image.transpose(Image.Transpose.FLIP_LEFT_RIGHT),
        boxes=tuple(
            Box(
                class_id=box.class_id,
                x_min=width - box.x_max,
                y_min=box.y_min,
                x_max=width - box.x_min,
                y_max=box.y_max,
            )
            for box in sample.boxes
        ),
    )


def augmentation_decision(seed: int, epoch: int, item_id: str) -> AugmentationDecision:
    """Derive this sample's flip and jitter factors from a frozen digest."""
    uniforms = _uniforms(AUGMENT_PREFIX, seed, epoch, item_id)
    lower = 1.0 - JITTER_STRENGTH
    span = 2.0 * JITTER_STRENGTH
    return AugmentationDecision(
        flip=uniforms[0] < 0.5,
        brightness=lower + span * uniforms[1],
        contrast=lower + span * uniforms[2],
        saturation=lower + span * uniforms[3],
    )


def augment_sample(sample: Sample, *, seed: int, epoch: int) -> Sample:
    """Apply the decided flip and colour jitter to one training sample."""
    decision = augmentation_decision(seed, epoch, sample.item_id)
    augmented = flip_sample(sample) if decision.flip else sample
    image = augmented.image
    image = ImageEnhance.Brightness(image).enhance(decision.brightness)
    image = ImageEnhance.Contrast(image).enhance(decision.contrast)
    image = ImageEnhance.Color(image).enhance(decision.saturation)
    return Sample(item_id=augmented.item_id, image=image, boxes=augmented.boxes)


def coco_annotation_payload(samples: Sequence[Sample]) -> list[dict[str, Any]]:
    """Build the COCO-format annotations consumed by the pinned processor."""
    payload: list[dict[str, Any]] = []
    annotation_id = 1
    for image_id, sample in enumerate(samples, start=1):
        annotations: list[dict[str, Any]] = []
        for box in sample.boxes:
            width = float(box.x_max - box.x_min)
            height = float(box.y_max - box.y_min)
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": box.class_id,
                    "bbox": [float(box.x_min), float(box.y_min), width, height],
                    "area": width * height,
                    "iscrowd": 0,
                }
            )
            annotation_id += 1
        payload.append({"image_id": image_id, "annotations": annotations})
    return payload


def collate(processor: Any, samples: Sequence[Sample]) -> Mapping[str, Any]:
    """Preprocess one batch through the pinned aspect-preserving processor."""
    if not samples:
        raise DatasetError("a batch requires at least one sample")
    return processor(
        images=[sample.image for sample in samples],
        annotations=coco_annotation_payload(samples),
        return_tensors="pt",
    )


def canvas_scale(original_width: int, original_height: int) -> float:
    """Return the aspect-preserving factor mapping the image onto the canvas."""
    if original_width <= 0 or original_height <= 0:
        raise DatasetError("original image size must be positive")
    return CANVAS_SIZE / float(max(original_width, original_height))


def canvas_box_to_original(
    box: Sequence[float], original_width: int, original_height: int
) -> tuple[float, float, float, float]:
    """Convert one canvas-normalized cxcywh box back to original-pixel xyxy."""
    scale = canvas_scale(original_width, original_height)
    if len(box) != 4:
        raise DatasetError("a canvas box requires four values")
    centre_x, centre_y, width, height = (float(value) * CANVAS_SIZE for value in box)
    left = (centre_x - width / 2.0) / scale
    top = (centre_y - height / 2.0) / scale
    right = (centre_x + width / 2.0) / scale
    bottom = (centre_y + height / 2.0) / scale
    return (
        min(max(left, 0.0), float(original_width)),
        min(max(top, 0.0), float(original_height)),
        min(max(right, 0.0), float(original_width)),
        min(max(bottom, 0.0), float(original_height)),
    )


def epoch_order(
    item_ids: Sequence[str], *, seed: int, epoch: int
) -> tuple[str, ...]:
    """Return this epoch's seed-deterministic shuffle of the training items."""
    values = tuple(item_ids)
    if not values:
        raise DatasetError("an epoch requires at least one item")
    if len(set(values)) != len(values):
        raise DatasetError("item ids must be unique")
    return tuple(
        sorted(
            values,
            key=lambda item: (
                hashlib.sha256(
                    SAMPLER_PREFIX
                    + str(seed).encode("utf-8")
                    + str(epoch).encode("utf-8")
                    + item.encode("utf-8")
                ).digest(),
                item,
            ),
        )
    )


def sampler_digest(consumed: Sequence[Sequence[str]]) -> str:
    """Hash the exact ordered item ids consumed by every training step."""
    return canonical_json_sha256(
        {"sampler_version": 1, "steps": [list(step) for step in consumed]}
    )


__all__ = [
    "AugmentationDecision",
    "CANVAS_SIZE",
    "DatasetError",
    "JITTER_STRENGTH",
    "ManifestError",
    "Sample",
    "augment_sample",
    "augmentation_decision",
    "build_image_index",
    "canvas_box_to_original",
    "canvas_scale",
    "coco_annotation_payload",
    "collate",
    "epoch_order",
    "flip_sample",
    "load_sample",
    "sampler_digest",
]
