"""Contracts for v0.2-lite sample loading, augmentation, and canvas geometry."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from vision_active_learning_loop.lite.dataset import (
    CANVAS_SIZE,
    JITTER_STRENGTH,
    DatasetError,
    Sample,
    augmentation_decision,
    augment_sample,
    build_image_index,
    canvas_box_to_original,
    coco_annotation_payload,
    collate,
    epoch_order,
    flip_sample,
    load_sample,
    sampler_digest,
)
from vision_active_learning_loop.lite.manifest import Box
from vision_active_learning_loop.probes.model_contract import build_contract_processor

ITEM_IDS = ("item-a", "item-b", "item-c", "item-d", "item-e")


def _png(width: int, height: int, marker: int) -> bytes:
    image = Image.new("RGB", (width, height), (marker % 256, 90, 160))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _write_images(root: Path, payloads: dict[str, bytes]) -> Path:
    directory = root / "images"
    directory.mkdir(parents=True)
    for name, data in payloads.items():
        (directory / name).write_bytes(data)
    return directory


def _row(item_id: str, width: int, height: int, boxes: list[list[int]]) -> dict:
    return {
        "item_id": item_id,
        "width": width,
        "height": height,
        "split": "pool",
        "boxes": boxes,
    }


def _sample(width: int = 320, height: int = 640) -> Sample:
    return Sample(
        item_id="item-a",
        image=Image.new("RGB", (width, height), (10, 20, 30)),
        boxes=(Box(class_id=0, x_min=32, y_min=128, x_max=128, y_max=384),),
    )


def test_build_image_index_maps_content_identity_to_paths(tmp_path: Path) -> None:
    from vision_active_learning_loop.lite.manifest import item_id_for_bytes

    first, second = _png(40, 30, 1), _png(40, 30, 2)
    directory = _write_images(tmp_path, {"a.png": first, "b.png": second})

    index = build_image_index(directory)

    assert index[item_id_for_bytes(first)] == directory / "a.png"
    assert index[item_id_for_bytes(second)] == directory / "b.png"


def test_build_image_index_keeps_the_lexicographically_smallest_duplicate(
    tmp_path: Path,
) -> None:
    from vision_active_learning_loop.lite.manifest import item_id_for_bytes

    payload = _png(40, 30, 1)
    directory = _write_images(tmp_path, {"z.png": payload, "a.png": payload})

    index = build_image_index(directory)

    assert index[item_id_for_bytes(payload)] == directory / "a.png"


def test_load_sample_returns_the_image_and_pixel_boxes(tmp_path: Path) -> None:
    from vision_active_learning_loop.lite.manifest import item_id_for_bytes

    payload = _png(40, 30, 1)
    directory = _write_images(tmp_path, {"a.png": payload})
    index = build_image_index(directory)
    row = _row(item_id_for_bytes(payload), 40, 30, [[2, 1, 2, 30, 20]])

    sample = load_sample(index, row)

    assert sample.item_id == row["item_id"]
    assert sample.image.size == (40, 30)
    assert sample.image.mode == "RGB"
    assert sample.boxes == (Box(class_id=2, x_min=1, y_min=2, x_max=30, y_max=20),)


def test_load_sample_rejects_an_item_missing_from_the_index(tmp_path: Path) -> None:
    directory = _write_images(tmp_path, {"a.png": _png(40, 30, 1)})

    with pytest.raises(DatasetError):
        load_sample(build_image_index(directory), _row("f" * 64, 40, 30, []))


def test_load_sample_rejects_a_size_that_disagrees_with_the_manifest(
    tmp_path: Path,
) -> None:
    from vision_active_learning_loop.lite.manifest import item_id_for_bytes

    payload = _png(40, 30, 1)
    directory = _write_images(tmp_path, {"a.png": payload})
    row = _row(item_id_for_bytes(payload), 41, 30, [])

    with pytest.raises(DatasetError):
        load_sample(build_image_index(directory), row)


def test_flip_sample_mirrors_boxes_about_the_image_width() -> None:
    flipped = flip_sample(_sample())

    assert flipped.boxes == (
        Box(class_id=0, x_min=320 - 128, y_min=128, x_max=320 - 32, y_max=384),
    )


def test_flipping_twice_restores_the_original_boxes() -> None:
    sample = _sample()

    assert flip_sample(flip_sample(sample)).boxes == sample.boxes


def test_augmentation_decision_matches_the_frozen_digest_stream() -> None:
    decision = augmentation_decision(17, 0, "item-a")

    assert decision.flip is False
    assert decision.brightness == pytest.approx(1.0689970611, rel=1e-9)
    assert decision.contrast == pytest.approx(1.0032999410, rel=1e-9)
    assert decision.saturation == pytest.approx(0.9834666032, rel=1e-9)


def test_augmentation_decision_flips_a_different_item() -> None:
    assert augmentation_decision(17, 0, "item-c").flip is True


def test_augmentation_decision_depends_on_the_epoch() -> None:
    assert augmentation_decision(17, 0, "item-a").flip is False
    assert augmentation_decision(17, 2, "item-a").flip is True


def test_augmentation_jitter_stays_inside_the_registered_strength() -> None:
    for index in range(200):
        decision = augmentation_decision(17, 0, f"probe-{index}")
        for factor in (decision.brightness, decision.contrast, decision.saturation):
            assert 1.0 - JITTER_STRENGTH <= factor <= 1.0 + JITTER_STRENGTH


def test_augment_sample_applies_the_decided_flip() -> None:
    sample = _sample()

    unflipped = augment_sample(sample, seed=17, epoch=0)
    flipped = augment_sample(
        Sample(item_id="item-c", image=sample.image, boxes=sample.boxes),
        seed=17,
        epoch=0,
    )

    assert unflipped.boxes == sample.boxes
    assert flipped.boxes == flip_sample(sample).boxes
    assert flipped.image.size == sample.image.size


def test_coco_annotation_payload_uses_xywh_and_category_ids() -> None:
    payload = coco_annotation_payload([_sample()])

    assert len(payload) == 1
    annotation = payload[0]["annotations"][0]
    assert annotation["bbox"] == [32.0, 128.0, 96.0, 256.0]
    assert annotation["category_id"] == 0
    assert annotation["area"] == pytest.approx(96.0 * 256.0)
    assert annotation["iscrowd"] == 0


def test_coco_annotation_payload_keeps_a_negative_sample() -> None:
    negative = Sample(
        item_id="item-b",
        image=Image.new("RGB", (40, 30), (1, 2, 3)),
        boxes=(),
    )

    payload = coco_annotation_payload([negative])

    assert payload[0]["annotations"] == []


def test_collate_produces_the_pinned_canvas_batch() -> None:
    batch = collate(build_contract_processor(), [_sample(), _sample(640, 320)])

    assert tuple(batch["pixel_values"].shape) == (2, 3, CANVAS_SIZE, CANVAS_SIZE)
    assert tuple(batch["pixel_mask"].shape) == (2, CANVAS_SIZE, CANVAS_SIZE)
    assert len(batch["labels"]) == 2
    assert batch["labels"][0]["class_labels"].tolist() == [0]


def test_canvas_boxes_round_trip_through_the_pinned_processor() -> None:
    for width, height, box in (
        (320, 640, Box(class_id=0, x_min=32, y_min=128, x_max=128, y_max=384)),
        (100, 50, Box(class_id=1, x_min=10, y_min=5, x_max=30, y_max=15)),
    ):
        sample = Sample(
            item_id="item-a",
            image=Image.new("RGB", (width, height), (5, 5, 5)),
            boxes=(box,),
        )

        batch = collate(build_contract_processor(), [sample])
        normalized = batch["labels"][0]["boxes"][0].tolist()

        assert canvas_box_to_original(normalized, width, height) == pytest.approx(
            (box.x_min, box.y_min, box.x_max, box.y_max), abs=1e-3
        )


def test_canvas_box_is_clipped_to_the_original_image() -> None:
    recovered = canvas_box_to_original([0.5, 0.5, 2.0, 2.0], 320, 640)

    assert recovered == pytest.approx((0.0, 0.0, 320.0, 640.0), abs=1e-6)


def test_canvas_box_rejects_a_non_positive_original_size() -> None:
    with pytest.raises(DatasetError):
        canvas_box_to_original([0.5, 0.5, 0.1, 0.1], 0, 640)


def test_epoch_order_matches_the_frozen_sampler_digest() -> None:
    assert epoch_order(ITEM_IDS, seed=17, epoch=0) == (
        "item-c",
        "item-b",
        "item-e",
        "item-a",
        "item-d",
    )


def test_epoch_order_changes_with_the_epoch_and_the_seed() -> None:
    assert epoch_order(ITEM_IDS, seed=17, epoch=1) == (
        "item-b",
        "item-e",
        "item-c",
        "item-a",
        "item-d",
    )
    assert epoch_order(ITEM_IDS, seed=29, epoch=0) == (
        "item-c",
        "item-a",
        "item-e",
        "item-b",
        "item-d",
    )


def test_epoch_order_is_a_permutation_of_its_input() -> None:
    assert sorted(epoch_order(ITEM_IDS, seed=17, epoch=3)) == sorted(ITEM_IDS)


def test_epoch_order_rejects_duplicate_item_ids() -> None:
    with pytest.raises(DatasetError):
        epoch_order(("item-a", "item-a"), seed=17, epoch=0)


def test_sampler_digest_depends_on_the_consumed_order() -> None:
    first = sampler_digest([("item-a", "item-b"), ("item-c",)])
    second = sampler_digest([("item-b", "item-a"), ("item-c",)])

    assert len(first) == 64
    assert first != second
    assert first == sampler_digest([("item-a", "item-b"), ("item-c",)])
