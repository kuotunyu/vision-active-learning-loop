"""Contracts for the whole v0.2-lite experiment schedule."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest
import torch

from vision_active_learning_loop.lite.experiment import (
    ExperimentConfig,
    ExperimentError,
    run_experiment,
)
from vision_active_learning_loop.lite.loop import FitArtifacts
from vision_active_learning_loop.lite.manifest import (
    SCHEMA_VERSION,
    manifest_sha256,
    public_pool_view,
)
from vision_active_learning_loop.lite.rounds import budget_count
from vision_active_learning_loop.lite.train import FitResult

POOL_SIZE = 250
TEST_SIZE = 8


def _rows() -> list[dict]:
    rows = []
    for index in range(POOL_SIZE):
        rows.append(
            {
                "item_id": f"pool-{index:04d}",
                "width": 64,
                "height": 48,
                "split": "pool",
                "boxes": [[index % 4, 1, 1, 20, 20]],
            }
        )
    for index in range(TEST_SIZE):
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


def _manifest() -> dict:
    rows = _rows()
    return {
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": "9" * 64,
        "image_count": len(rows),
        "box_count": len(rows),
        "class_box_counts": {"D00": 0, "D10": 0, "D20": 0, "D40": 0},
        "alias_count": 0,
        "discarded_box_count": 0,
        "negative_image_count": 0,
        "images": sorted(rows, key=lambda row: row["item_id"]),
    }


class _Recorder:
    """Real-shaped stand-ins that record every call the schedule makes."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.fits: list[dict] = []
        self.score_calls: list[dict] = []
        self.evaluations: list[dict] = []

    def fitter(self, identity, runtime, *, rows_by_item, image_index, output_dir):
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True)
        digest = f"{len(self.fits):064x}"
        (output_dir / "checkpoint.pt").write_bytes(b"ckpt")
        self.fits.append(
            {
                "arm": identity.arm,
                "fraction": identity.budget_fraction,
                "items": tuple(identity.item_ids),
                "rows": {item: dict(row) for item, row in rows_by_item.items()},
                "output": output_dir,
            }
        )
        result = FitResult(
            steps=2,
            losses=(2.0, 1.0),
            learning_rates=(0.1, 0.1),
            gradient_norms=(1.0, 1.0),
            gradient_clip=0.1,
            first_window_median=2.0,
            last_window_median=1.0,
            loss_decreased=True,
            peak_allocated_bytes=0,
        )
        receipt = {"receipt_type": "lite-fit", "normative": {"loss": {"final": 1.0}}}
        (output_dir / "fit-receipt.json").write_text(json.dumps(receipt))
        return FitArtifacts(
            result=result,
            receipt=receipt,
            receipt_path=output_dir / "fit-receipt.json",
            checkpoint_path=output_dir / "checkpoint.pt",
            checkpoint_sha256=digest,
            model_sha256="d" * 64,
        )

    def scorer(self, *, arm, checkpoint_path, checkpoint_sha256, public_rows, **_):
        self.score_calls.append(
            {
                "arm": arm,
                "checkpoint": checkpoint_sha256,
                "rows": [dict(row) for row in public_rows],
            }
        )
        # Deterministic, arm-dependent scores so the two arms diverge.
        offset = 0.0 if arm == "entropy" else 0.5
        return {
            row["item_id"]: (int(row["item_id"][-4:]) % 97) / 97.0 + offset
            for row in public_rows
        }

    def evaluator(self, *, checkpoint_path, checkpoint_sha256, test_rows, **_):
        self.evaluations.append(
            {
                "checkpoint": checkpoint_sha256,
                "test_items": [row["item_id"] for row in test_rows],
            }
        )
        value = 0.1 + 0.05 * len(self.evaluations)
        metrics = {"mAP50_95": value, "AP50": value}
        for label in ("D00", "D10", "D20", "D40"):
            metrics[f"AP50_95_{label}"] = value
            metrics[f"recall_{label}"] = value
        return metrics


def _config(tmp_path: Path, **overrides) -> ExperimentConfig:
    values = {
        "experiment_id": "lite-test",
        "seed": 17,
        "arms": ("random", "entropy", "margin"),
        "snapshot": tmp_path / "snapshot",
        "device": torch.device("cpu"),
        "output_root": tmp_path / "artifacts",
        "steps": 2,
        "batch_size": 1,
        "warmup_steps": 1,
    }
    values.update(overrides)
    return ExperimentConfig(**values)


def _run(tmp_path: Path, **overrides):
    manifest = _manifest()
    recorder = _Recorder(tmp_path)
    summary = run_experiment(
        _config(tmp_path, **overrides),
        manifest=manifest,
        public_view=public_pool_view(manifest),
        image_index={row["item_id"]: tmp_path / "img" for row in manifest["images"]},
        fitter=recorder.fitter,
        scorer=recorder.scorer,
        evaluator=recorder.evaluator,
    )
    return manifest, recorder, summary


def test_schedule_runs_one_shared_fit_and_three_fits_per_arm(tmp_path: Path) -> None:
    _manifest_, recorder, summary = _run(tmp_path)

    assert len(recorder.fits) == 10
    assert recorder.fits[0]["arm"] == "shared"
    assert [fit["arm"] for fit in recorder.fits[1:]] == [
        "random",
        "random",
        "random",
        "entropy",
        "entropy",
        "entropy",
        "margin",
        "margin",
        "margin",
    ]
    assert summary.fit_count == 10


def test_every_arm_nests_its_budgets_on_the_shared_start(tmp_path: Path) -> None:
    _manifest_, recorder, _summary = _run(tmp_path)

    shared = set(recorder.fits[0]["items"])
    assert len(shared) == budget_count(0.02, POOL_SIZE)
    for arm in ("random", "entropy", "margin"):
        arm_fits = [fit for fit in recorder.fits if fit["arm"] == arm]
        previous = shared
        for fit, fraction in zip(arm_fits, (0.05, 0.10, 0.20)):
            current = set(fit["items"])
            assert fit["fraction"] == fraction
            assert len(current) == budget_count(fraction, POOL_SIZE)
            assert previous <= current
            previous = current


def test_random_arm_never_scores_and_uncertainty_arms_score_each_round(
    tmp_path: Path,
) -> None:
    _manifest_, recorder, _summary = _run(tmp_path)

    assert [call["arm"] for call in recorder.score_calls] == ["entropy"] * 3 + [
        "margin"
    ] * 3


def test_scoring_sees_only_label_free_unacquired_pool_rows(tmp_path: Path) -> None:
    _manifest_, recorder, _summary = _run(tmp_path)

    entropy_fits = [fit for fit in recorder.fits if fit["arm"] == "entropy"]
    shared_items = set(recorder.fits[0]["items"])
    first_call = recorder.score_calls[0]
    assert all(
        set(row) == {"item_id", "width", "height"} for row in first_call["rows"]
    )
    assert {row["item_id"] for row in first_call["rows"]} == (
        {f"pool-{index:04d}" for index in range(POOL_SIZE)} - shared_items
    )
    assert all(not row["item_id"].startswith("test-") for row in first_call["rows"])
    assert first_call["checkpoint"] == "0" * 64  # scored with the shared checkpoint
    assert entropy_fits[0]["items"] != recorder.fits[1]["items"]  # differs from random


def test_fits_receive_labels_only_for_acquired_items(tmp_path: Path) -> None:
    _manifest_, recorder, _summary = _run(tmp_path)

    for fit in recorder.fits:
        assert set(fit["rows"]) == set(fit["items"])
        assert all("boxes" in row for row in fit["rows"].values())
        assert all(not item.startswith("test-") for item in fit["items"])


def test_every_checkpoint_is_evaluated_once_on_the_frozen_test_split(
    tmp_path: Path,
) -> None:
    _manifest_, recorder, _summary = _run(tmp_path)

    assert len(recorder.evaluations) == 10
    assert len({call["checkpoint"] for call in recorder.evaluations}) == 10
    assert all(
        call["test_items"] == [f"test-{index:04d}" for index in range(TEST_SIZE)]
        for call in recorder.evaluations
    )


def test_experiment_publishes_ledgers_metrics_and_receipt(tmp_path: Path) -> None:
    manifest, recorder, summary = _run(tmp_path)
    root = tmp_path / "artifacts" / "lite-test"

    for arm in ("random", "entropy", "margin"):
        ledger = json.loads((root / f"ledger-{arm}.json").read_text(encoding="utf-8"))
        assert [entry["round_index"] for entry in ledger["entries"]][:1] == [1]
        assert len(ledger["entries"]) == budget_count(0.20, POOL_SIZE) - budget_count(
            0.02, POOL_SIZE
        )
        if arm == "random":
            assert all(entry["score"] is None for entry in ledger["entries"])
        else:
            assert all(entry["score"] is not None for entry in ledger["entries"])

    with (root / "metrics.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert len(rows) == 10
    assert {row["arm"] for row in rows} == {"shared", "random", "entropy", "margin"}
    assert {"budget_fraction", "budget", "mAP50_95", "checkpoint_sha256"} <= set(
        rows[0]
    )

    receipt = json.loads(
        (root / "experiment-receipt.json").read_text(encoding="utf-8")
    )
    normative = receipt["normative"]
    assert normative["manifest_sha256"] == manifest_sha256(manifest)
    assert normative["seed"] == 17
    assert normative["arms"] == ["random", "entropy", "margin"]
    assert len(normative["fits"]) == 10
    assert set(normative["naubc"]) == {"random", "entropy", "margin"}
    assert set(normative["naubc_delta_vs_random"]) == {"entropy", "margin"}
    assert summary.receipt_path == root / "experiment-receipt.json"


def test_naubc_uses_the_shared_point_and_the_arm_points(tmp_path: Path) -> None:
    _manifest_, recorder, _summary = _run(tmp_path)
    root = tmp_path / "artifacts" / "lite-test"
    receipt = json.loads(
        (root / "experiment-receipt.json").read_text(encoding="utf-8")
    )

    # The evaluator returns 0.15, 0.20, ... in evaluation order (shared first,
    # then random x3, entropy x3, margin x3); random's curve is 0.15, 0.20,
    # 0.25, 0.30 over fractions 0.02, 0.05, 0.10, 0.20.
    expected_random = (
        0.5 * (0.15 + 0.20) * 0.03
        + 0.5 * (0.20 + 0.25) * 0.05
        + 0.5 * (0.25 + 0.30) * 0.10
    ) / 0.18
    assert receipt["normative"]["naubc"]["random"] == pytest.approx(expected_random)


def test_experiment_refuses_an_existing_experiment_root(tmp_path: Path) -> None:
    (tmp_path / "artifacts" / "lite-test").mkdir(parents=True)

    with pytest.raises(ExperimentError, match="exists"):
        _run(tmp_path)


def test_experiment_rejects_an_unregistered_arm(tmp_path: Path) -> None:
    with pytest.raises(ExperimentError, match="arm"):
        _run(tmp_path, arms=("random", "core_set"))


SNAPSHOT = __import__("os").environ.get("VAL_LITE_SNAPSHOT")


@pytest.mark.skipif(
    not SNAPSHOT, reason="set VAL_LITE_SNAPSHOT to the pinned RT-DETR snapshot"
)
def test_run_experiment_end_to_end_with_the_pinned_detector_on_cpu(
    tmp_path: Path,
) -> None:
    import io

    from PIL import Image

    from vision_active_learning_loop.lite.manifest import item_id_for_bytes

    # Pool of 50 gives budgets 1, 3, 5, 10 so every round acquires something.
    images = tmp_path / "images"
    images.mkdir()
    rows = []
    for index in range(58):
        image = Image.new("RGB", (64, 48), (index % 256, 60, 120))
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        payload = buffer.getvalue()
        (images / f"img_{index:03d}.png").write_bytes(payload)
        rows.append(
            {
                "item_id": item_id_for_bytes(payload),
                "width": 64,
                "height": 48,
                "split": "pool" if index < 50 else "test",
                "boxes": [[index % 4, 2, 2, 30, 30]],
            }
        )
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "source_archive_sha256": "9" * 64,
        "image_count": len(rows),
        "box_count": len(rows),
        "class_box_counts": {"D00": 0, "D10": 0, "D20": 0, "D40": 0},
        "alias_count": 0,
        "discarded_box_count": 0,
        "negative_image_count": 0,
        "images": sorted(rows, key=lambda row: row["item_id"]),
    }
    from vision_active_learning_loop.lite.dataset import build_image_index

    summary = run_experiment(
        ExperimentConfig(
            experiment_id="lite-e2e",
            seed=17,
            arms=("random", "entropy", "margin"),
            snapshot=Path(SNAPSHOT),
            device=torch.device("cpu"),
            output_root=tmp_path / "artifacts",
            steps=2,
            batch_size=1,
            warmup_steps=1,
        ),
        manifest=manifest,
        public_view=public_pool_view(manifest),
        image_index=build_image_index(images),
    )

    assert summary.fit_count == 10
    assert set(summary.naubc) == {"random", "entropy", "margin"}
    receipt = json.loads(summary.receipt_path.read_text(encoding="utf-8"))
    assert len(receipt["normative"]["fits"]) == 10
    assert (summary.root / "curve.svg").exists()
    assert (summary.root / "metrics.csv").exists()
    for arm in ("entropy", "margin"):
        ledger = json.loads(
            (summary.root / f"ledger-{arm}.json").read_text(encoding="utf-8")
        )
        assert all(entry["score"] is not None for entry in ledger["entries"])
