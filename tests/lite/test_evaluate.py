"""Contracts for v0.2-lite detection conversion, COCO metrics, and nAUBC."""

from __future__ import annotations

import pytest
import torch

from vision_active_learning_loop.lite.evaluate import (
    MAX_DETECTIONS,
    Detection,
    EvaluationError,
    detections_from_outputs,
    evaluate_detections,
    normalized_aubc,
)
from vision_active_learning_loop.models.rtdetr_contract import RawDetectorOutput

WIDTH, HEIGHT = 320, 640


def _raw(logits: torch.Tensor, boxes: torch.Tensor) -> RawDetectorOutput:
    batch, queries, _ = logits.shape
    return RawDetectorOutput(
        logits=logits,
        intermediate_logits=torch.zeros((batch, 2, queries, 4)),
        enc_outputs_class=torch.zeros((batch, queries, 4)),
        enc_topk_logits=torch.zeros((batch, queries, 4)),
        final_boxes=boxes,
        penultimate_boxes=boxes,
        intermediate_boxes=torch.stack([boxes, boxes], dim=1),
    )


def _outputs(queries: int = 300, batch: int = 1):
    logits = torch.full((batch, queries, 4), -8.0)
    boxes = torch.full((batch, queries, 4), 0.25)
    return logits, boxes


def test_detections_take_the_highest_sigmoid_class_per_query() -> None:
    logits, boxes = _outputs()
    logits[0, 0] = torch.tensor([-8.0, 2.0, -8.0, -8.0])
    # cx, cy, w, h on the padded canvas: recovers (32, 128, 128, 384) at scale 1.
    boxes[0, 0] = torch.tensor([0.125, 0.4, 0.15, 0.4])

    detections = detections_from_outputs(
        _raw(logits, boxes), item_ids=["item-a"], sizes=[(WIDTH, HEIGHT)]
    )

    best = detections[0]
    assert best.item_id == "item-a"
    assert best.class_id == 1
    assert best.score == pytest.approx(float(torch.sigmoid(torch.tensor(2.0))))
    assert best.box == pytest.approx((32.0, 128.0, 128.0, 384.0), abs=1e-3)


def test_detections_are_capped_at_one_hundred_per_image() -> None:
    logits, boxes = _outputs()
    logits[0, :, 0] = torch.linspace(-5.0, 5.0, 300)

    detections = detections_from_outputs(
        _raw(logits, boxes), item_ids=["item-a"], sizes=[(WIDTH, HEIGHT)]
    )

    assert len(detections) == MAX_DETECTIONS == 100
    assert detections[0].score > detections[-1].score


def test_detections_are_kept_without_any_confidence_threshold() -> None:
    logits, boxes = _outputs()  # every query has max sigmoid 0.00034

    detections = detections_from_outputs(
        _raw(logits, boxes), item_ids=["item-a"], sizes=[(WIDTH, HEIGHT)]
    )

    assert len(detections) == MAX_DETECTIONS
    assert all(0.0 < detection.score < 0.001 for detection in detections)


def test_detections_cover_every_image_in_the_batch() -> None:
    logits, boxes = _outputs(batch=2)

    detections = detections_from_outputs(
        _raw(logits, boxes),
        item_ids=["item-a", "item-b"],
        sizes=[(WIDTH, HEIGHT), (WIDTH, HEIGHT)],
    )

    assert {detection.item_id for detection in detections} == {"item-a", "item-b"}
    assert len(detections) == 2 * MAX_DETECTIONS


def test_detections_reject_a_mismatched_item_count() -> None:
    logits, boxes = _outputs(batch=2)

    with pytest.raises(EvaluationError):
        detections_from_outputs(
            _raw(logits, boxes), item_ids=["item-a"], sizes=[(WIDTH, HEIGHT)]
        )


def _rows() -> list[dict]:
    rows = []
    for class_id in range(4):
        for index in range(3):
            offset = 10 * index
            rows.append(
                {
                    "item_id": f"test-{class_id}-{index}",
                    "width": WIDTH,
                    "height": HEIGHT,
                    "split": "test",
                    "boxes": [[class_id, 20 + offset, 30, 120 + offset, 230]],
                }
            )
    return rows


def _perfect_detections() -> list[Detection]:
    return [
        Detection(
            item_id=row["item_id"],
            class_id=row["boxes"][0][0],
            score=1.0,
            box=(
                float(row["boxes"][0][1]),
                float(row["boxes"][0][2]),
                float(row["boxes"][0][3]),
                float(row["boxes"][0][4]),
            ),
        )
        for row in _rows()
    ]


def test_exact_detections_score_a_perfect_average_precision() -> None:
    metrics = evaluate_detections(_rows(), _perfect_detections())

    assert metrics["mAP50_95"] == pytest.approx(1.0, abs=1e-6)
    assert metrics["AP50"] == pytest.approx(1.0, abs=1e-6)
    for label in ("D00", "D10", "D20", "D40"):
        assert metrics[f"AP50_95_{label}"] == pytest.approx(1.0, abs=1e-6)
        assert metrics[f"recall_{label}"] == pytest.approx(1.0, abs=1e-6)


def test_no_detections_score_zero_rather_than_a_sentinel() -> None:
    metrics = evaluate_detections(_rows(), [])

    assert metrics["mAP50_95"] == 0.0
    assert metrics["AP50"] == 0.0
    assert metrics["recall_D40"] == 0.0


def test_displaced_detections_lose_average_precision() -> None:
    displaced = [
        Detection(
            item_id=detection.item_id,
            class_id=detection.class_id,
            score=detection.score,
            box=(
                detection.box[0] + 90.0,
                detection.box[1],
                detection.box[2] + 90.0,
                detection.box[3],
            ),
        )
        for detection in _perfect_detections()
    ]

    metrics = evaluate_detections(_rows(), displaced)

    assert metrics["mAP50_95"] < 0.5


def test_evaluation_rejects_a_test_class_with_no_ground_truth() -> None:
    rows = [row for row in _rows() if row["boxes"][0][0] != 3]
    detections = [
        detection for detection in _perfect_detections() if detection.class_id != 3
    ]

    with pytest.raises(EvaluationError, match="no ground truth"):
        evaluate_detections(rows, detections)


def test_evaluation_rejects_a_detection_for_an_unknown_image() -> None:
    stray = [
        Detection(item_id="absent", class_id=0, score=1.0, box=(1.0, 2.0, 3.0, 4.0))
    ]

    with pytest.raises(EvaluationError):
        evaluate_detections(_rows(), stray)


def test_normalized_aubc_matches_the_hand_computed_trapezoid() -> None:
    points = ((0.02, 0.1), (0.05, 0.2), (0.10, 0.3), (0.20, 0.5))

    # 0.5*(0.1+0.2)*0.03 + 0.5*(0.2+0.3)*0.05 + 0.5*(0.3+0.5)*0.10 = 0.057
    assert normalized_aubc(points) == pytest.approx(0.057 / 0.18, rel=1e-12)


def test_normalized_aubc_of_a_constant_curve_is_that_constant() -> None:
    points = ((0.02, 0.4), (0.05, 0.4), (0.10, 0.4), (0.20, 0.4))

    assert normalized_aubc(points) == pytest.approx(0.4, rel=1e-12)


def test_normalized_aubc_requires_the_registered_budget_fractions() -> None:
    with pytest.raises(EvaluationError):
        normalized_aubc(((0.02, 0.1), (0.05, 0.2), (0.10, 0.3)))

    with pytest.raises(EvaluationError):
        normalized_aubc(((0.02, 0.1), (0.05, 0.2), (0.20, 0.3), (0.10, 0.5)))
