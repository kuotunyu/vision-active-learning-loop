"""Raw-query acquisition scores and deterministic ordering for v0.2-lite.

Implements the uncertainty contract of the approved design specification
Section 7.3 and the deterministic random order of Section 7.2. No score
threshold, NMS, or detection postprocessor participates in a score.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Mapping, Sequence

import torch

from ..models.rtdetr_contract import RawDetectorOutput

TOP_QUERY_COUNT = 20
STATE_COUNT = 5
CLASS_WEIGHT = 0.75
LOCALIZATION_WEIGHT = 0.25
PROBABILITY_FLOOR = 1e-12
RANDOM_PREFIX = "random"
SHARED_START_PREFIX = "initial"

_LOG_STATE_COUNT = math.log(STATE_COUNT)


class AcquisitionError(ValueError):
    """Raised when acquisition inputs or scores are not usable."""


def _float64(tensor: object, label: str, *, last_dim: int) -> torch.Tensor:
    if not isinstance(tensor, torch.Tensor):
        raise AcquisitionError(f"{label} must be a tensor")
    if tensor.ndim < 2 or tensor.shape[-1] != last_dim:
        raise AcquisitionError(f"{label} must have last dimension {last_dim}")
    value = tensor.detach().to(dtype=torch.float64)
    if not bool(torch.isfinite(value).all()):
        raise AcquisitionError(f"{label} must be finite")
    return value


def _foreground_and_distribution(
    logits: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    objectness = torch.sigmoid(logits).amax(dim=-1)
    conditional = torch.softmax(logits, dim=-1)
    background = (1.0 - objectness).unsqueeze(-1)
    foreground = objectness.unsqueeze(-1) * conditional
    return objectness, torch.cat([background, foreground], dim=-1)


def five_state_distribution(logits: torch.Tensor) -> torch.Tensor:
    """Return the project-defined background-plus-four-class distribution."""
    values = _float64(logits, "logits", last_dim=4)
    _, distribution = _foreground_and_distribution(values)
    return distribution


def _corners(boxes: torch.Tensor) -> tuple[torch.Tensor, ...]:
    centre_x, centre_y, width, height = boxes.unbind(dim=-1)
    left = (centre_x - width / 2.0).clamp(0.0, 1.0)
    top = (centre_y - height / 2.0).clamp(0.0, 1.0)
    right = (centre_x + width / 2.0).clamp(0.0, 1.0)
    bottom = (centre_y + height / 2.0).clamp(0.0, 1.0)
    return left, top, right, bottom


def localization_uncertainty(
    final_boxes: torch.Tensor, penultimate_boxes: torch.Tensor
) -> torch.Tensor:
    """Return 1 - IoU between the final and penultimate decoder boxes."""
    final = _float64(final_boxes, "final boxes", last_dim=4)
    penultimate = _float64(penultimate_boxes, "penultimate boxes", last_dim=4)
    if final.shape != penultimate.shape:
        raise AcquisitionError("final and penultimate boxes must share a shape")

    left_a, top_a, right_a, bottom_a = _corners(final)
    left_b, top_b, right_b, bottom_b = _corners(penultimate)
    area_a = (right_a - left_a) * (bottom_a - top_a)
    area_b = (right_b - left_b) * (bottom_b - top_b)
    overlap_width = (
        torch.minimum(right_a, right_b) - torch.maximum(left_a, left_b)
    ).clamp(min=0.0)
    overlap_height = (
        torch.minimum(bottom_a, bottom_b) - torch.maximum(top_a, top_b)
    ).clamp(min=0.0)
    intersection = overlap_width * overlap_height
    union = area_a + area_b - intersection
    degenerate = (area_a <= 0.0) | (area_b <= 0.0) | (union <= 0.0)
    intersection_over_union = torch.where(
        degenerate,
        torch.zeros_like(union),
        intersection / union.clamp(min=PROBABILITY_FLOOR),
    )
    return 1.0 - intersection_over_union


def _query_uncertainty(
    logits: torch.Tensor,
    final_boxes: torch.Tensor,
    penultimate_boxes: torch.Tensor,
    class_term: str,
) -> torch.Tensor:
    values = _float64(logits, "logits", last_dim=4)
    if values.shape[:-1] != _float64(final_boxes, "final boxes", last_dim=4).shape[:-1]:
        raise AcquisitionError("logits and boxes must share query dimensions")
    objectness, distribution = _foreground_and_distribution(values)
    if class_term == "entropy":
        floored = distribution.clamp(min=PROBABILITY_FLOOR)
        class_uncertainty = (
            -(distribution * floored.log()).sum(dim=-1) / _LOG_STATE_COUNT
        )
    else:
        top_two = distribution.topk(2, dim=-1).values
        class_uncertainty = 1.0 - (top_two[..., 0] - top_two[..., 1])
    localization = localization_uncertainty(final_boxes, penultimate_boxes)
    return (
        CLASS_WEIGHT * class_uncertainty
        + LOCALIZATION_WEIGHT * objectness * localization
    )


def entropy_query_uncertainty(
    logits: torch.Tensor,
    final_boxes: torch.Tensor,
    penultimate_boxes: torch.Tensor,
) -> torch.Tensor:
    """Return the per-query entropy uncertainty of Section 7.3."""
    return _query_uncertainty(logits, final_boxes, penultimate_boxes, "entropy")


def margin_query_uncertainty(
    logits: torch.Tensor,
    final_boxes: torch.Tensor,
    penultimate_boxes: torch.Tensor,
) -> torch.Tensor:
    """Return the per-query margin uncertainty of Section 7.3."""
    return _query_uncertainty(logits, final_boxes, penultimate_boxes, "margin")


def image_uncertainty(query_uncertainty: torch.Tensor) -> torch.Tensor:
    """Return the mean of the twenty largest query uncertainties per image."""
    if not isinstance(query_uncertainty, torch.Tensor) or query_uncertainty.ndim != 2:
        raise AcquisitionError("query uncertainty must be a batch-by-query tensor")
    if query_uncertainty.shape[1] < TOP_QUERY_COUNT:
        raise AcquisitionError(
            f"image uncertainty requires at least {TOP_QUERY_COUNT} queries"
        )
    values = query_uncertainty.detach().to(dtype=torch.float64)
    if not bool(torch.isfinite(values).all()):
        raise AcquisitionError("query uncertainty must be finite")
    return values.topk(TOP_QUERY_COUNT, dim=1).values.mean(dim=1)


def _image_scores(raw: RawDetectorOutput, class_term: str) -> torch.Tensor:
    if not isinstance(raw, RawDetectorOutput):
        raise AcquisitionError("raw detector output is required")
    return image_uncertainty(
        _query_uncertainty(
            raw.logits, raw.final_boxes, raw.penultimate_boxes, class_term
        )
    )


def entropy_image_scores(raw: RawDetectorOutput) -> torch.Tensor:
    """Return one entropy image score per batch element."""
    return _image_scores(raw, "entropy")


def margin_image_scores(raw: RawDetectorOutput) -> torch.Tensor:
    """Return one margin image score per batch element."""
    return _image_scores(raw, "margin")


def _validated_item_ids(item_ids: Sequence[str]) -> tuple[str, ...]:
    if isinstance(item_ids, str) or not isinstance(item_ids, Sequence):
        raise AcquisitionError("item ids must be a sequence")
    values = tuple(item_ids)
    if any(not isinstance(value, str) or not value for value in values):
        raise AcquisitionError("item ids must be non-empty strings")
    if len(set(values)) != len(values):
        raise AcquisitionError("item ids must be unique")
    return values


def _ordering_digest(prefix: str, seed: int, item_id: str) -> bytes:
    return hashlib.sha256(
        prefix.encode("utf-8") + str(seed).encode("utf-8") + item_id.encode("utf-8")
    ).digest()


def _deterministic_order(
    prefix: str, seed: int, item_ids: Sequence[str]
) -> tuple[str, ...]:
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise AcquisitionError("seed must be an integer")
    values = _validated_item_ids(item_ids)
    return tuple(
        sorted(values, key=lambda item: (_ordering_digest(prefix, seed, item), item))
    )


def random_acquisition_order(seed: int, item_ids: Sequence[str]) -> tuple[str, ...]:
    """Return the one complete random order of Section 7.2 for this seed."""
    return _deterministic_order(RANDOM_PREFIX, seed, item_ids)


def shared_start_order(seed: int, item_ids: Sequence[str]) -> tuple[str, ...]:
    """Return the shared 2% start order of Section 6.2 for this seed."""
    return _deterministic_order(SHARED_START_PREFIX, seed, item_ids)


def select_by_score(scores: Mapping[str, float], count: int) -> tuple[str, ...]:
    """Return the highest-scoring item ids, breaking exact ties by ascending id."""
    if not isinstance(scores, Mapping):
        raise AcquisitionError("scores must be a mapping")
    if not isinstance(count, int) or isinstance(count, bool) or count < 0:
        raise AcquisitionError("count must be a non-negative integer")
    if count > len(scores):
        raise AcquisitionError("count exceeds the candidate pool")
    _validated_item_ids(tuple(scores))
    values: dict[str, float] = {}
    for item_id, score in scores.items():
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise AcquisitionError(f"{item_id} score must be a number")
        if not math.isfinite(float(score)):
            raise AcquisitionError(f"{item_id} score must be finite")
        values[item_id] = float(score)
    ordered = sorted(values, key=lambda item: (-values[item], item))
    return tuple(ordered[:count])
