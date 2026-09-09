"""Contracts for the v0.2-lite dataset manifest, split, and public view."""

from __future__ import annotations

import io
from pathlib import Path

import pytest
from PIL import Image

from vision_active_learning_loop.lite.manifest import (
    MIN_POOL_IMAGES,
    MIN_TEST_BOXES_PER_CLASS,
    RDD_CLASS_IDS,
    SCHEMA_VERSION,
    Box,
    ManifestError,
    assign_split,
    audit_coverage,
    build_manifest,
    item_id_for_bytes,
    manifest_sha256,
    parse_voc_annotation,
    public_pool_view,
    scan_dataset,
)

ARCHIVE_SHA = "a" * 64


def _annotation(
    objects: list[tuple[str, int, int, int, int]],
    *,
    width: int = 40,
    height: int = 30,
) -> bytes:
    body = "".join(
        f"<object><name>{name}</name><bndbox>"
        f"<xmin>{x_min}</xmin><ymin>{y_min}</ymin>"
        f"<xmax>{x_max}</xmax><ymax>{y_max}</ymax>"
        f"</bndbox></object>"
        for name, x_min, y_min, x_max, y_max in objects
    )
    return (
        "<annotation><size>"
        f"<width>{width}</width><height>{height}</height><depth>3</depth>"
        f"</size>{body}</annotation>"
    ).encode("utf-8")


def _image_bytes(marker: int, *, width: int = 40, height: int = 30) -> bytes:
    image = Image.new("RGB", (width, height), (marker % 256, 7, 11))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _dataset(root: Path, entries: dict[str, tuple[bytes, bytes]]) -> tuple[Path, Path]:
    images = root / "images"
    annotations = root / "annotations"
    images.mkdir(parents=True)
    annotations.mkdir(parents=True)
    for stem, (image, annotation) in entries.items():
        (images / f"{stem}.png").write_bytes(image)
        (annotations / f"{stem}.xml").write_bytes(annotation)
    return images, annotations


def test_parse_voc_annotation_maps_the_four_rdd_classes() -> None:
    data = _annotation(
        [
            ("D00", 1, 2, 3, 4),
            ("D10", 5, 6, 7, 8),
            ("D20", 1, 1, 2, 2),
            ("D40", 0, 0, 5, 5),
        ]
    )

    parsed = parse_voc_annotation(data)

    assert [box.class_id for box in parsed.boxes] == [0, 1, 2, 3]
    assert parsed.boxes[0] == Box(class_id=0, x_min=1, y_min=2, x_max=3, y_max=4)
    assert parsed.discarded_boxes == 0
    assert RDD_CLASS_IDS == {"D00": 0, "D10": 1, "D20": 2, "D40": 3}


def test_parse_voc_annotation_discards_and_counts_unknown_labels() -> None:
    parsed = parse_voc_annotation(
        _annotation([("D00", 1, 2, 3, 4), ("D43", 1, 1, 9, 9), ("D50", 2, 2, 8, 8)])
    )

    assert len(parsed.boxes) == 1
    assert parsed.discarded_boxes == 2


def test_parse_voc_annotation_keeps_an_image_with_only_unknown_labels() -> None:
    parsed = parse_voc_annotation(_annotation([("D44", 1, 1, 9, 9)]))

    assert parsed.boxes == ()
    assert parsed.discarded_boxes == 1
    assert (parsed.width, parsed.height) == (40, 30)


def test_parse_voc_annotation_rejects_a_degenerate_box() -> None:
    with pytest.raises(ManifestError):
        parse_voc_annotation(_annotation([("D00", 5, 2, 5, 9)]))


def test_parse_voc_annotation_rejects_a_box_outside_the_declared_size() -> None:
    with pytest.raises(ManifestError):
        parse_voc_annotation(_annotation([("D00", 1, 1, 41, 9)]))


def test_parse_voc_annotation_rejects_a_non_positive_size() -> None:
    with pytest.raises(ManifestError):
        parse_voc_annotation(_annotation([("D00", 0, 0, 1, 1)], width=0))


def test_parse_voc_annotation_rejects_non_integer_coordinates() -> None:
    with pytest.raises(ManifestError):
        parse_voc_annotation(
            b"<annotation><size><width>40</width><height>30</height></size>"
            b"<object><name>D00</name><bndbox><xmin>1.5</xmin><ymin>2</ymin>"
            b"<xmax>3</xmax><ymax>4</ymax></bndbox></object></annotation>"
        )


def test_item_id_is_the_sha256_of_the_image_bytes() -> None:
    import hashlib

    data = _image_bytes(1)

    assert item_id_for_bytes(data) == hashlib.sha256(data).hexdigest()


def test_assign_split_matches_the_frozen_hash_intervals() -> None:
    assert assign_split("img-004") == "test"  # r = 691
    assert assign_split("img-000") == "pool"  # r = 9645


def test_assign_split_treats_1999_as_test_and_2000_as_pool() -> None:
    assert assign_split("probe-26778") == "test"  # r = 1999
    assert assign_split("probe-23723") == "pool"  # r = 2000


def test_assign_split_rejects_an_empty_group_id() -> None:
    with pytest.raises(ManifestError):
        assign_split("")


def test_scan_dataset_pairs_images_with_annotations_by_stem(tmp_path: Path) -> None:
    images, annotations = _dataset(
        tmp_path,
        {
            "a": (_image_bytes(1), _annotation([("D00", 1, 2, 3, 4)])),
            "b": (_image_bytes(2), _annotation([("D40", 0, 0, 5, 5)])),
        },
    )

    scan = scan_dataset(images, annotations)

    assert [image.relative_path for image in scan.images] == ["a.png", "b.png"]
    assert scan.images[0].item_id == item_id_for_bytes(_image_bytes(1))
    assert scan.alias_count == 0


def test_scan_dataset_rejects_an_image_without_an_annotation(tmp_path: Path) -> None:
    images, annotations = _dataset(
        tmp_path, {"a": (_image_bytes(1), _annotation([("D00", 1, 2, 3, 4)]))}
    )
    (images / "orphan.png").write_bytes(_image_bytes(2))

    with pytest.raises(ManifestError):
        scan_dataset(images, annotations)


def test_scan_dataset_rejects_an_annotation_without_an_image(tmp_path: Path) -> None:
    images, annotations = _dataset(
        tmp_path, {"a": (_image_bytes(1), _annotation([("D00", 1, 2, 3, 4)]))}
    )
    (annotations / "orphan.xml").write_bytes(_annotation([("D00", 1, 2, 3, 4)]))

    with pytest.raises(ManifestError):
        scan_dataset(images, annotations)


def test_scan_dataset_rejects_a_size_that_disagrees_with_the_image(
    tmp_path: Path,
) -> None:
    images, annotations = _dataset(
        tmp_path,
        {"a": (_image_bytes(1), _annotation([("D00", 1, 2, 3, 4)], width=41))},
    )

    with pytest.raises(ManifestError):
        scan_dataset(images, annotations)


def test_scan_dataset_collapses_byte_identical_duplicates(tmp_path: Path) -> None:
    payload = _image_bytes(1)
    annotation = _annotation([("D00", 1, 2, 3, 4)])
    images, annotations = _dataset(
        tmp_path,
        {"z-copy": (payload, annotation), "a-original": (payload, annotation)},
    )

    scan = scan_dataset(images, annotations)

    assert len(scan.images) == 1
    assert scan.images[0].relative_path == "a-original.png"
    assert scan.alias_count == 1


def test_scan_dataset_rejects_duplicates_whose_annotations_disagree(
    tmp_path: Path,
) -> None:
    payload = _image_bytes(1)
    images, annotations = _dataset(
        tmp_path,
        {
            "a": (payload, _annotation([("D00", 1, 2, 3, 4)])),
            "b": (payload, _annotation([("D10", 1, 2, 3, 4)])),
        },
    )

    with pytest.raises(ManifestError):
        scan_dataset(images, annotations)


def _scan(tmp_path: Path):
    return scan_dataset(
        *_dataset(
            tmp_path,
            {
                "a": (
                    _image_bytes(1),
                    _annotation([("D00", 1, 2, 3, 4), ("D43", 1, 1, 9, 9)]),
                ),
                "b": (_image_bytes(2), _annotation([("D40", 0, 0, 5, 5)])),
                "c": (_image_bytes(3), _annotation([])),
            },
        )
    )


def test_build_manifest_summarizes_boxes_classes_and_negatives(tmp_path: Path) -> None:
    manifest = build_manifest(_scan(tmp_path), source_archive_sha256=ARCHIVE_SHA)

    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["source_archive_sha256"] == ARCHIVE_SHA
    assert manifest["image_count"] == 3
    assert manifest["box_count"] == 2
    assert manifest["class_box_counts"] == {"D00": 1, "D10": 0, "D20": 0, "D40": 1}
    assert manifest["discarded_box_count"] == 1
    assert manifest["negative_image_count"] == 1
    assert manifest["alias_count"] == 0


def test_manifest_rows_expose_no_filename_and_are_sorted(tmp_path: Path) -> None:
    manifest = build_manifest(_scan(tmp_path), source_archive_sha256=ARCHIVE_SHA)

    item_ids = [row["item_id"] for row in manifest["images"]]
    assert item_ids == sorted(item_ids)
    for row in manifest["images"]:
        assert set(row) == {"item_id", "width", "height", "split", "boxes"}


def test_manifest_split_uses_the_item_id_as_the_group(tmp_path: Path) -> None:
    manifest = build_manifest(_scan(tmp_path), source_archive_sha256=ARCHIVE_SHA)

    for row in manifest["images"]:
        assert row["split"] == assign_split(row["item_id"])


def test_build_manifest_rejects_a_malformed_archive_digest(tmp_path: Path) -> None:
    with pytest.raises(ManifestError):
        build_manifest(_scan(tmp_path), source_archive_sha256="not-a-digest")


def test_manifest_sha256_ignores_key_insertion_order(tmp_path: Path) -> None:
    manifest = build_manifest(_scan(tmp_path), source_archive_sha256=ARCHIVE_SHA)
    reordered = dict(reversed(list(manifest.items())))

    assert manifest_sha256(reordered) == manifest_sha256(manifest)


def _synthetic_manifest(
    *, pool_images: int, test_boxes_per_class: int
) -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for index in range(pool_images):
        rows.append(
            {
                "item_id": f"pool-{index:06d}",
                "width": 40,
                "height": 30,
                "split": "pool",
                "boxes": [[0, 1, 2, 3, 4]],
            }
        )
    for class_id in range(4):
        for index in range(test_boxes_per_class):
            rows.append(
                {
                    "item_id": f"test-{class_id}-{index:06d}",
                    "width": 40,
                    "height": 30,
                    "split": "test",
                    "boxes": [[class_id, 1, 2, 3, 4]],
                }
            )
    return {
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": ARCHIVE_SHA,
        "image_count": len(rows),
        "box_count": len(rows),
        "class_box_counts": {"D00": 0, "D10": 0, "D20": 0, "D40": 0},
        "alias_count": 0,
        "discarded_box_count": 0,
        "negative_image_count": 0,
        "images": sorted(rows, key=lambda row: row["item_id"]),
    }


def test_audit_coverage_passes_a_manifest_meeting_both_floors() -> None:
    manifest = _synthetic_manifest(
        pool_images=MIN_POOL_IMAGES, test_boxes_per_class=MIN_TEST_BOXES_PER_CLASS
    )

    assert audit_coverage(manifest) == ()


def test_audit_coverage_reports_a_test_class_below_the_box_floor() -> None:
    manifest = _synthetic_manifest(
        pool_images=MIN_POOL_IMAGES, test_boxes_per_class=MIN_TEST_BOXES_PER_CLASS - 1
    )

    errors = audit_coverage(manifest)

    assert len(errors) == 4
    assert all("test" in error for error in errors)


def test_audit_coverage_reports_a_pool_below_the_image_floor() -> None:
    manifest = _synthetic_manifest(
        pool_images=MIN_POOL_IMAGES - 1, test_boxes_per_class=MIN_TEST_BOXES_PER_CLASS
    )

    errors = audit_coverage(manifest)

    assert len(errors) == 1
    assert "pool" in errors[0]


def test_public_pool_view_drops_test_rows_and_pool_labels() -> None:
    manifest = _synthetic_manifest(pool_images=3, test_boxes_per_class=1)

    view = public_pool_view(manifest)

    assert len(view["images"]) == 3
    assert all(row["item_id"].startswith("pool-") for row in view["images"])
    for row in view["images"]:
        assert set(row) == {"item_id", "width", "height"}


def test_public_pool_view_binds_the_source_manifest_digest() -> None:
    manifest = _synthetic_manifest(pool_images=3, test_boxes_per_class=1)

    view = public_pool_view(manifest)

    assert view["manifest_sha256"] == manifest_sha256(manifest)
    assert view["schema_version"] == SCHEMA_VERSION
