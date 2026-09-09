"""Contracts for one end-to-end v0.2-lite fit."""

from __future__ import annotations

import io
import json
import os
from pathlib import Path

import pytest
import torch
from PIL import Image

from vision_active_learning_loop.lite.dataset import build_image_index
from vision_active_learning_loop.lite.loop import (
    FitIdentity,
    FitRuntime,
    LoopError,
    fit_once,
    load_pinned_detector,
)
from vision_active_learning_loop.lite.manifest import item_id_for_bytes
from vision_active_learning_loop.training.checkpoint_io import (
    load_checkpoint_verified,
)

SNAPSHOT = os.environ.get("VAL_LITE_SNAPSHOT")
requires_snapshot = pytest.mark.skipif(
    not SNAPSHOT, reason="set VAL_LITE_SNAPSHOT to the pinned RT-DETR snapshot"
)


def _png(index: int, width: int = 64, height: int = 48) -> bytes:
    image = Image.new("RGB", (width, height), (index % 256, 40 + index, 200))
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def _rows_and_index(root: Path, count: int) -> tuple[dict[str, dict], dict]:
    images = root / "images"
    images.mkdir(parents=True)
    rows: dict[str, dict] = {}
    for index in range(count):
        payload = _png(index)
        (images / f"img_{index:03d}.png").write_bytes(payload)
        item_id = item_id_for_bytes(payload)
        rows[item_id] = {
            "item_id": item_id,
            "width": 64,
            "height": 48,
            "split": "pool",
            "boxes": [[index % 4, 4 + index, 6, 30 + index, 40]],
        }
    return rows, build_image_index(images)


def _identity(item_ids: tuple[str, ...], **overrides) -> FitIdentity:
    values = {
        "experiment_id": "lite-test",
        "manifest_sha256": "a" * 64,
        "arm": "random",
        "seed": 17,
        "budget_fraction": 0.02,
        "item_ids": item_ids,
    }
    values.update(overrides)
    return FitIdentity(**values)


def test_fit_identity_rejects_an_unregistered_arm_before_loading_a_model(
    tmp_path: Path,
) -> None:
    rows, index = _rows_and_index(tmp_path, 2)
    runtime = FitRuntime(snapshot=tmp_path / "absent", device=torch.device("cpu"))

    with pytest.raises(LoopError, match="arm"):
        fit_once(
            _identity(tuple(rows), arm="core_set"),
            runtime,
            rows_by_item=rows,
            image_index=index,
            output_dir=tmp_path / "out",
        )


def test_fit_identity_rejects_items_missing_from_the_manifest(tmp_path: Path) -> None:
    rows, index = _rows_and_index(tmp_path, 2)
    runtime = FitRuntime(snapshot=tmp_path / "absent", device=torch.device("cpu"))

    with pytest.raises(LoopError, match="manifest"):
        fit_once(
            _identity(tuple(rows) + ("f" * 64,)),
            runtime,
            rows_by_item=rows,
            image_index=index,
            output_dir=tmp_path / "out",
        )


def test_fit_runtime_rejects_a_warmup_not_shorter_than_the_steps(
    tmp_path: Path,
) -> None:
    rows, index = _rows_and_index(tmp_path, 2)
    runtime = FitRuntime(
        snapshot=tmp_path / "absent", device=torch.device("cpu"), steps=2
    )

    with pytest.raises(LoopError, match="warm-up"):
        fit_once(
            _identity(tuple(rows)),
            runtime,
            rows_by_item=rows,
            image_index=index,
            output_dir=tmp_path / "out",
        )


def test_load_pinned_detector_rejects_an_absent_snapshot(tmp_path: Path) -> None:
    with pytest.raises(LoopError, match="snapshot"):
        load_pinned_detector(tmp_path / "absent")


@requires_snapshot
def test_fit_once_trains_the_pinned_detector_on_cpu_and_publishes_evidence(
    tmp_path: Path,
) -> None:
    rows, index = _rows_and_index(tmp_path, 4)
    identity = _identity(tuple(sorted(rows)))
    runtime = FitRuntime(
        snapshot=Path(SNAPSHOT),
        device=torch.device("cpu"),
        steps=2,
        batch_size=2,
        warmup_steps=1,
    )
    output = tmp_path / "fit"

    artifacts = fit_once(
        identity, runtime, rows_by_item=rows, image_index=index, output_dir=output
    )

    assert artifacts.result.steps == 2
    assert all(torch.isfinite(torch.tensor(artifacts.result.losses)))
    receipt = json.loads(artifacts.receipt_path.read_text(encoding="utf-8"))
    normative = receipt["normative"]
    assert normative["arm"] == "random"
    assert normative["acquired_image_count"] == 4
    assert normative["checkpoint_sha256"] == artifacts.checkpoint_sha256
    assert normative["environment"]["device"] == "cpu"
    assert normative["environment"]["steps"] == 2
    assert len(normative["model_sha256"]) == 64
    state = load_checkpoint_verified(
        artifacts.checkpoint_path, artifacts.checkpoint_sha256
    )
    assert state.step == 2
    assert state.input_digests["manifest_sha256"] == "a" * 64
