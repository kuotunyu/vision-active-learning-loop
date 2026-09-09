"""Detection conversion, COCO metrics, and budget-curve integration for v0.2-lite.

Implements protocol Section 6: every raw query contributes a detection scored
by its largest foreground sigmoid, the highest hundred per image are kept with
no threshold and no NMS, and pycocotools scores them against the frozen test
split at IoU 0.50:0.05:0.95.
"""

from __future__ import annotations

import contextlib
import io
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
import torch
from pycocotools.coco import COCO
from pycocotools.cocoeval import COCOeval

from ..models.rtdetr_contract import RDD_LABELS, RawDetectorOutput
from .dataset import canvas_box_to_original

MAX_DETECTIONS = 100
CATEGORY_ID_OFFSET = 1
BUDGET_FRACTIONS = (0.02, 0.05, 0.10, 0.20)


class EvaluationError(ValueError):
    """Raised when detections, ground truth, or curve points are not usable."""


@dataclass(frozen=True)
class Detection:
    item_id: str
    class_id: int
    score: float
    box: tuple[float, float, float, float]


def detections_from_outputs(
    raw: RawDetectorOutput,
    *,
    item_ids: Sequence[str],
    sizes: Sequence[tuple[int, int]],
) -> tuple[Detection, ...]:
    """Convert one raw batch into at most a hundred detections per image."""
    if not isinstance(raw, RawDetectorOutput):
        raise EvaluationError("raw detector output is required")
    scores = torch.sigmoid(raw.logits.detach().to(dtype=torch.float64))
    batch = scores.shape[0]
    if len(item_ids) != batch or len(sizes) != batch:
        raise EvaluationError("item ids and sizes must match the batch")

    best_scores, best_classes = scores.max(dim=-1)
    detections: list[Detection] = []
    for index in range(batch):
        width, height = sizes[index]
        keep = min(MAX_DETECTIONS, best_scores.shape[1])
        order = torch.topk(best_scores[index], keep, sorted=True).indices
        for query in order.tolist():
            detections.append(
                Detection(
                    item_id=item_ids[index],
                    class_id=int(best_classes[index, query]),
                    score=float(best_scores[index, query]),
                    box=canvas_box_to_original(
                        raw.final_boxes[index, query].detach().tolist(), width, height
                    ),
                )
            )
    return tuple(detections)


def _image_ids(rows: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    item_ids = sorted(str(row["item_id"]) for row in rows)
    if len(set(item_ids)) != len(item_ids):
        raise EvaluationError("evaluation item ids must be unique")
    return {item_id: index + 1 for index, item_id in enumerate(item_ids)}


def coco_ground_truth(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build the COCO ground-truth document for the frozen test split."""
    if not rows:
        raise EvaluationError("evaluation requires at least one image")
    image_ids = _image_ids(rows)
    images: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []
    present: set[int] = set()
    annotation_id = 1
    for row in rows:
        image_id = image_ids[str(row["item_id"])]
        images.append(
            {
                "id": image_id,
                "width": int(row["width"]),
                "height": int(row["height"]),
                "file_name": f"{row['item_id']}.jpg",
            }
        )
        for box in row.get("boxes", ()):
            class_id = int(box[0])
            width = float(box[3] - box[1])
            height = float(box[4] - box[2])
            annotations.append(
                {
                    "id": annotation_id,
                    "image_id": image_id,
                    "category_id": class_id + CATEGORY_ID_OFFSET,
                    "bbox": [float(box[1]), float(box[2]), width, height],
                    "area": width * height,
                    "iscrowd": 0,
                }
            )
            present.add(class_id)
            annotation_id += 1
    missing = [
        label for index, label in enumerate(RDD_LABELS) if index not in present
    ]
    if missing:
        raise EvaluationError(f"test split has no ground truth for {missing[0]}")
    return {
        # pycocotools 2.0.10 copies these two keys when loading results.
        "info": {"description": "vision-active-learning-loop v0.2-lite test split"},
        "licenses": [],
        "images": images,
        "annotations": annotations,
        "categories": [
            {"id": index + CATEGORY_ID_OFFSET, "name": label}
            for index, label in enumerate(RDD_LABELS)
        ],
    }


def _detection_records(
    detections: Sequence[Detection], image_ids: Mapping[str, int]
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for detection in detections:
        image_id = image_ids.get(detection.item_id)
        if image_id is None:
            raise EvaluationError(f"{detection.item_id} is not an evaluation image")
        left, top, right, bottom = detection.box
        records.append(
            {
                "image_id": image_id,
                "category_id": detection.class_id + CATEGORY_ID_OFFSET,
                "bbox": [left, top, right - left, bottom - top],
                "score": float(detection.score),
            }
        )
    return records


def _clean(value: float) -> float:
    number = float(value)
    return 0.0 if number < 0.0 or not np.isfinite(number) else number


def _summarize(evaluation: COCOeval) -> tuple[float, float, float]:
    with contextlib.redirect_stdout(io.StringIO()):
        evaluation.evaluate()
        evaluation.accumulate()
        evaluation.summarize()
    stats = evaluation.stats
    return _clean(stats[0]), _clean(stats[1]), _clean(stats[8])


def evaluate_detections(
    rows: Sequence[Mapping[str, Any]], detections: Sequence[Detection]
) -> dict[str, float]:
    """Score detections against the frozen test split with pycocotools."""
    ground_truth = coco_ground_truth(rows)
    image_ids = _image_ids(rows)
    records = _detection_records(detections, image_ids)

    with contextlib.redirect_stdout(io.StringIO()):
        coco = COCO()
        coco.dataset = ground_truth
        coco.createIndex()
        results = coco.loadRes(records) if records else None

    if results is None:
        metrics = {"mAP50_95": 0.0, "AP50": 0.0}
        for label in RDD_LABELS:
            metrics[f"AP50_95_{label}"] = 0.0
            metrics[f"recall_{label}"] = 0.0
        return metrics

    evaluation = COCOeval(coco, results, iouType="bbox")
    evaluation.params.maxDets = [1, 10, MAX_DETECTIONS]
    mean_average_precision, average_precision_50, _ = _summarize(evaluation)

    metrics = {"mAP50_95": mean_average_precision, "AP50": average_precision_50}
    for index, label in enumerate(RDD_LABELS):
        per_class = COCOeval(coco, results, iouType="bbox")
        per_class.params.maxDets = [1, 10, MAX_DETECTIONS]
        per_class.params.catIds = [index + CATEGORY_ID_OFFSET]
        class_map, _, class_recall = _summarize(per_class)
        metrics[f"AP50_95_{label}"] = class_map
        metrics[f"recall_{label}"] = class_recall
    return metrics


def normalized_aubc(points: Sequence[tuple[float, float]]) -> float:
    """Integrate the budget curve over the registered fractions and normalize."""
    fractions = tuple(round(float(point[0]), 10) for point in points)
    if fractions != BUDGET_FRACTIONS:
        raise EvaluationError("budget fractions must be the registered ordered set")
    values = [float(point[1]) for point in points]
    area = 0.0
    for index in range(len(values) - 1):
        width = fractions[index + 1] - fractions[index]
        area += 0.5 * (values[index] + values[index + 1]) * width
    return area / (fractions[-1] - fractions[0])
