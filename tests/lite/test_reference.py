"""Contracts for the full-label reference baseline (`val lite reference`)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from tests.lite.test_baseline import _real_dataset
from vision_active_learning_loop.lite.loop import LoopError, plan_baseline
from vision_active_learning_loop.lite.manifest import public_pool_view
from vision_active_learning_loop.lite.reference import reference_items, reference_main

SNAPSHOT = os.environ.get("VAL_LITE_SNAPSHOT")
requires_snapshot = pytest.mark.skipif(
    not SNAPSHOT, reason="set VAL_LITE_SNAPSHOT to the pinned RT-DETR snapshot"
)


def _arguments(manifest: Path, view: Path, images: Path, snapshot: Path, out: Path):
    return [
        "--manifest",
        str(manifest),
        "--public-view",
        str(view),
        "--images",
        str(images),
        "--snapshot",
        str(snapshot),
        "--experiment-id",
        "lite-ref",
        "--seed",
        "17",
        "--device",
        "cpu",
        "--output-root",
        str(out),
        "--steps",
        "2",
        "--batch-size",
        "1",
        "--warmup-steps",
        "1",
    ]


def test_reference_items_are_every_pool_row_and_never_test_rows(tmp_path: Path) -> None:
    manifest_path, view_path, _images = _real_dataset(tmp_path / "data")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    view = json.loads(view_path.read_text(encoding="utf-8"))
    plan = plan_baseline(manifest, view, seed=17, experiment_id="ref")

    items = reference_items(plan, view)

    pool = {row["item_id"] for row in manifest["images"] if row["split"] == "pool"}
    assert set(items) == pool and len(items) == 8
    assert list(items) == sorted(items)
    other = plan_baseline(manifest, view, seed=29, experiment_id="ref")
    assert reference_items(other, public_pool_view(manifest)) == items


def test_reference_items_reject_a_view_that_is_not_the_whole_pool(tmp_path: Path) -> None:
    manifest_path, view_path, _images = _real_dataset(tmp_path / "data")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    view = json.loads(view_path.read_text(encoding="utf-8"))
    plan = plan_baseline(manifest, view, seed=17, experiment_id="ref")

    with pytest.raises(LoopError, match="whole pool"):
        reference_items(plan, {"images": view["images"][:-1]})


def test_reference_main_rejects_a_missing_manifest(tmp_path: Path) -> None:
    exit_code = reference_main(
        _arguments(tmp_path / "absent.json", tmp_path / "v.json", tmp_path, tmp_path, tmp_path)
    )

    assert exit_code == 3


def test_reference_main_records_a_fit_failure_on_disk(tmp_path: Path) -> None:
    manifest_path, view_path, images = _real_dataset(tmp_path / "data")
    empty_snapshot = tmp_path / "empty-snapshot"
    empty_snapshot.mkdir()
    out = tmp_path / "artifacts"

    exit_code = reference_main(
        _arguments(manifest_path, view_path, images, empty_snapshot, out)
    )

    assert exit_code == 2
    failure = json.loads((out / "lite-ref" / "failure.json").read_text(encoding="utf-8"))
    assert failure["stage"] == "reference"
    assert "snapshot" in failure["error"]


@requires_snapshot
def test_reference_main_fits_the_whole_pool_on_cpu(tmp_path: Path) -> None:
    manifest_path, view_path, images = _real_dataset(tmp_path / "data")
    out = tmp_path / "artifacts"

    exit_code = reference_main(
        _arguments(manifest_path, view_path, images, Path(SNAPSHOT), out)
    )

    assert exit_code == 0
    fit_dir = out / "lite-ref" / "fits" / "reference-1.00"
    receipt = json.loads((fit_dir / "fit-receipt.json").read_text(encoding="utf-8"))
    assert receipt["normative"]["arm"] == "reference"
    assert receipt["normative"]["budget_fraction"] == 1.0
    assert receipt["normative"]["acquired_image_count"] == 8
    metrics = json.loads(
        (out / "lite-ref" / "metrics-reference-1.00.json").read_text(encoding="utf-8")
    )
    assert metrics["budget"] == 8 and metrics["pool_size"] == 8
    assert metrics["training_rule"]["name"] == "fixed-steps"
    assert metrics["steps"] == 2
    assert metrics["elapsed_seconds"] > 0.0
    assert 0.0 <= metrics["metrics"]["mAP50_95"] <= 1.0
