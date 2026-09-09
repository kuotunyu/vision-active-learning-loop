"""Contracts for the shared 2% baseline driver (`val lite baseline`)."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path

import pytest
from PIL import Image

from vision_active_learning_loop.lite.loop import (
    LoopError,
    baseline_main,
    budget_count,
    plan_baseline,
    shared_start_items,
)
from vision_active_learning_loop.lite.manifest import (
    SCHEMA_VERSION,
    item_id_for_bytes,
    manifest_sha256,
    public_pool_view,
)

SNAPSHOT = os.environ.get("VAL_LITE_SNAPSHOT")
requires_snapshot = pytest.mark.skipif(
    not SNAPSHOT, reason="set VAL_LITE_SNAPSHOT to the pinned RT-DETR snapshot"
)


def _manifest(rows: list[dict]) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": "9" * 64,
        "image_count": len(rows),
        "box_count": sum(len(row["boxes"]) for row in rows),
        "class_box_counts": {"D00": 0, "D10": 0, "D20": 0, "D40": 0},
        "alias_count": 0,
        "discarded_box_count": 0,
        "negative_image_count": 0,
        "images": sorted(rows, key=lambda row: row["item_id"]),
    }


def _synthetic_rows(pool: int, test: int) -> list[dict]:
    rows = []
    for index in range(pool):
        rows.append(
            {
                "item_id": f"pool-{index:04d}",
                "width": 64,
                "height": 48,
                "split": "pool",
                "boxes": [[index % 4, 1, 1, 20, 20]],
            }
        )
    for index in range(test):
        rows.append(
            {
                "item_id": f"test-{index:04d}",
                "width": 64,
                "height": 48,
                "split": "test",
                "boxes": [[index % 4, 1, 1, 20, 20]],
            }
        )
    return rows


def test_plan_baseline_takes_the_shared_start_of_the_pool() -> None:
    manifest = _manifest(_synthetic_rows(pool=250, test=8))
    view = public_pool_view(manifest)

    plan = plan_baseline(manifest, view, seed=17, experiment_id="exp")

    pool_ids = tuple(row["item_id"] for row in view["images"])
    assert plan.pool_size == 250
    assert plan.budget == budget_count(0.02, 250) == 5
    assert plan.start_item_ids == shared_start_items(pool_ids, seed=17)
    assert set(plan.start_item_ids) <= set(pool_ids)
    assert plan.manifest_sha256 == manifest_sha256(manifest)
    assert plan.experiment_id == "exp"


def test_plan_baseline_rejects_a_view_from_a_different_manifest() -> None:
    manifest = _manifest(_synthetic_rows(pool=250, test=8))
    view = public_pool_view(_manifest(_synthetic_rows(pool=251, test=8)))

    with pytest.raises(LoopError, match="public view"):
        plan_baseline(manifest, view, seed=17, experiment_id="exp")


def test_plan_baseline_rejects_a_view_that_leaks_test_rows() -> None:
    manifest = _manifest(_synthetic_rows(pool=250, test=8))
    view = public_pool_view(manifest)
    view["images"].append({"item_id": "test-0000", "width": 64, "height": 48})

    with pytest.raises(LoopError, match="public view"):
        plan_baseline(manifest, view, seed=17, experiment_id="exp")


def test_baseline_main_rejects_a_missing_manifest(tmp_path: Path) -> None:
    exit_code = baseline_main(
        [
            "--manifest",
            str(tmp_path / "absent.json"),
            "--public-view",
            str(tmp_path / "absent-view.json"),
            "--images",
            str(tmp_path),
            "--snapshot",
            str(tmp_path),
            "--experiment-id",
            "exp",
            "--seed",
            "17",
            "--device",
            "cpu",
            "--output-root",
            str(tmp_path / "out"),
        ]
    )

    assert exit_code == 3


def test_baseline_main_records_a_fit_failure_on_disk(tmp_path: Path) -> None:
    manifest_path, view_path, images = _real_dataset(tmp_path / "data")
    empty_snapshot = tmp_path / "empty-snapshot"
    empty_snapshot.mkdir()
    output_root = tmp_path / "artifacts"

    exit_code = baseline_main(
        [
            "--manifest",
            str(manifest_path),
            "--public-view",
            str(view_path),
            "--images",
            str(images),
            "--snapshot",
            str(empty_snapshot),
            "--experiment-id",
            "lite-fail",
            "--seed",
            "17",
            "--device",
            "cpu",
            "--output-root",
            str(output_root),
            "--steps",
            "2",
            "--batch-size",
            "1",
            "--warmup-steps",
            "1",
        ]
    )

    assert exit_code == 2
    failure = json.loads(
        (output_root / "lite-fail" / "failure.json").read_text(encoding="utf-8")
    )
    assert failure["stage"] == "baseline"
    assert "snapshot" in failure["error"]


def _png(index: int) -> bytes:
    image = Image.new("RGB", (64, 48), (index % 256, 90, 30))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _real_dataset(root: Path) -> tuple[Path, Path, Path]:
    images = root / "images"
    images.mkdir(parents=True)
    rows = []
    for index in range(12):
        payload = _png(index)
        (images / f"img_{index:03d}.png").write_bytes(payload)
        rows.append(
            {
                "item_id": item_id_for_bytes(payload),
                "width": 64,
                "height": 48,
                "split": "pool" if index < 8 else "test",
                "boxes": [[index % 4, 2, 2, 30, 30]],
            }
        )
    manifest = _manifest(rows)
    manifest_path = root / "manifest.json"
    view_path = root / "public-pool.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    view_path.write_text(json.dumps(public_pool_view(manifest)), encoding="utf-8")
    return manifest_path, view_path, images


@requires_snapshot
def test_baseline_main_fits_and_scores_the_shared_start_on_cpu(tmp_path: Path) -> None:
    manifest_path, view_path, images = _real_dataset(tmp_path / "data")
    output_root = tmp_path / "artifacts"

    exit_code = baseline_main(
        [
            "--manifest",
            str(manifest_path),
            "--public-view",
            str(view_path),
            "--images",
            str(images),
            "--snapshot",
            SNAPSHOT,
            "--experiment-id",
            "lite-test",
            "--seed",
            "17",
            "--device",
            "cpu",
            "--output-root",
            str(output_root),
            "--steps",
            "2",
            "--batch-size",
            "1",
            "--warmup-steps",
            "1",
        ]
    )

    assert exit_code == 0
    fit_dir = output_root / "lite-test" / "fits" / "shared-0.02"
    assert (fit_dir / "checkpoint.pt").exists()
    receipt = json.loads((fit_dir / "fit-receipt.json").read_text(encoding="utf-8"))
    assert receipt["normative"]["acquired_image_count"] == 1  # B(0.02, 8) = 1
    metrics = json.loads(
        (output_root / "lite-test" / "metrics-shared-0.02.json").read_text(
            encoding="utf-8"
        )
    )
    assert metrics["checkpoint_sha256"] == receipt["normative"]["checkpoint_sha256"]
    assert 0.0 <= metrics["metrics"]["mAP50_95"] <= 1.0
    assert metrics["test_image_count"] == 4
