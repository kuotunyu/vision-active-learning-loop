"""Hand-computed contracts for the v0.2-lite acquisition scores and ordering."""

from __future__ import annotations

import math

import pytest
import torch

from vision_active_learning_loop.lite.acquisition import (
    AcquisitionError,
    TOP_QUERY_COUNT,
    entropy_image_scores,
    entropy_query_uncertainty,
    five_state_distribution,
    image_uncertainty,
    localization_uncertainty,
    margin_image_scores,
    margin_query_uncertainty,
    random_acquisition_order,
    select_by_score,
    shared_start_order,
)
from vision_active_learning_loop.models.rtdetr_contract import RawDetectorOutput

# For z = [0, 0, 0, 0]: o = 1/2, pi = 1/4, so P = [1/2, 1/8, 1/8, 1/8, 1/8] and
# H = -(1/2 ln 1/2 + 4 * 1/8 ln 1/8) = (1/2)ln2 + (3/2)ln2 = ln 4.
UNIFORM_ENTROPY = math.log(4.0) / math.log(5.0)
# Sorted P is [1/2, 1/8, ...], so margin = 1/2 - 1/8 = 3/8 and m = 5/8.
UNIFORM_MARGIN = 1.0 - 0.375

BOX = (0.5, 0.5, 0.4, 0.4)
SHIFTED_BOX = (0.6, 0.5, 0.4, 0.4)  # xyxy overlap gives IoU 0.12 / 0.20 = 0.6
FAR_BOX = (0.8, 0.8, 0.1, 0.1)
NEAR_BOX = (0.2, 0.2, 0.1, 0.1)
DEGENERATE_BOX = (0.5, 0.5, 0.0, 0.4)


def _queries(logit_rows: list[list[float]]) -> torch.Tensor:
    return torch.tensor([logit_rows], dtype=torch.float64)


def _boxes(rows: list[tuple[float, float, float, float]]) -> torch.Tensor:
    return torch.tensor([list(row) for row in rows], dtype=torch.float64).unsqueeze(0)


def _single(logits: list[float], final: tuple, penultimate: tuple) -> tuple:
    return _queries([logits]), _boxes([final]), _boxes([penultimate])


def test_five_state_distribution_matches_hand_computed_uniform_case() -> None:
    distribution = five_state_distribution(_queries([[0.0, 0.0, 0.0, 0.0]]))

    assert distribution.shape == (1, 1, 5)
    assert distribution[0, 0].tolist() == pytest.approx(
        [0.5, 0.125, 0.125, 0.125, 0.125], rel=1e-12
    )


def test_five_state_distribution_sums_to_one() -> None:
    distribution = five_state_distribution(_queries([[3.0, -1.0, 0.5, -4.0]]))

    assert float(distribution.sum()) == pytest.approx(1.0, rel=1e-12)


def test_entropy_query_uncertainty_matches_hand_computed_uniform_case() -> None:
    logits, final, penultimate = _single([0.0, 0.0, 0.0, 0.0], BOX, BOX)

    observed = entropy_query_uncertainty(logits, final, penultimate)

    assert float(observed[0, 0]) == pytest.approx(0.75 * UNIFORM_ENTROPY, rel=1e-12)


def test_margin_query_uncertainty_matches_hand_computed_uniform_case() -> None:
    logits, final, penultimate = _single([0.0, 0.0, 0.0, 0.0], BOX, BOX)

    observed = margin_query_uncertainty(logits, final, penultimate)

    assert float(observed[0, 0]) == pytest.approx(0.75 * UNIFORM_MARGIN, rel=1e-12)


def test_identical_boxes_contribute_no_localization_uncertainty() -> None:
    assert float(localization_uncertainty(_boxes([BOX]), _boxes([BOX]))[0, 0]) == 0.0


def test_partially_overlapping_boxes_have_hand_computed_iou() -> None:
    observed = localization_uncertainty(_boxes([BOX]), _boxes([SHIFTED_BOX]))

    assert float(observed[0, 0]) == pytest.approx(1.0 - 0.6, rel=1e-12)


def test_disjoint_boxes_have_maximum_localization_uncertainty() -> None:
    observed = localization_uncertainty(_boxes([NEAR_BOX]), _boxes([FAR_BOX]))

    assert float(observed[0, 0]) == 1.0


def test_degenerate_box_scores_zero_iou() -> None:
    observed = localization_uncertainty(_boxes([DEGENERATE_BOX]), _boxes([BOX]))

    assert float(observed[0, 0]) == 1.0


def test_box_disagreement_adds_the_hand_computed_localization_term() -> None:
    aligned = entropy_query_uncertainty(*_single([0.0] * 4, BOX, BOX))
    shifted = entropy_query_uncertainty(*_single([0.0] * 4, BOX, SHIFTED_BOX))

    # 0.25 * o_q * l_q = 0.25 * 0.5 * 0.4
    assert float(shifted[0, 0] - aligned[0, 0]) == pytest.approx(0.05, rel=1e-12)


def test_confident_foreground_has_low_class_uncertainty() -> None:
    logits, final, penultimate = _single([10.0, -10.0, -10.0, -10.0], BOX, BOX)

    assert float(entropy_query_uncertainty(logits, final, penultimate)[0, 0]) < 0.01
    assert float(margin_query_uncertainty(logits, final, penultimate)[0, 0]) < 0.01


def test_ambiguous_background_versus_foreground_raises_entropy() -> None:
    confident = entropy_query_uncertainty(
        *_single([10.0, -10.0, -10.0, -10.0], BOX, BOX)
    )
    ambiguous = entropy_query_uncertainty(
        *_single([0.0, -10.0, -10.0, -10.0], BOX, BOX)
    )

    assert float(ambiguous[0, 0]) > 0.3
    assert float(ambiguous[0, 0]) > 100.0 * float(confident[0, 0])


def test_ambiguous_foreground_classes_maximize_margin_uncertainty() -> None:
    confident = margin_query_uncertainty(
        *_single([10.0, -10.0, -10.0, -10.0], BOX, BOX)
    )
    ambiguous = margin_query_uncertainty(*_single([5.0, 5.0, -10.0, -10.0], BOX, BOX))

    assert float(ambiguous[0, 0]) > 0.7
    assert float(ambiguous[0, 0]) > float(confident[0, 0])


def test_image_uncertainty_averages_only_the_twenty_largest_queries() -> None:
    values = (torch.arange(300, dtype=torch.float64) / 1000.0).unsqueeze(0)

    observed = image_uncertainty(values)

    # Largest 20 values are 0.280 .. 0.299, whose mean is 0.2895.
    assert float(observed[0]) == pytest.approx(0.2895, rel=1e-12)
    assert TOP_QUERY_COUNT == 20


def test_image_uncertainty_rejects_fewer_queries_than_the_fixed_cardinality() -> None:
    with pytest.raises(AcquisitionError):
        image_uncertainty(torch.zeros((1, TOP_QUERY_COUNT - 1), dtype=torch.float64))


def _raw(logits: torch.Tensor, final: torch.Tensor, penultimate: torch.Tensor):
    batch, queries, _ = logits.shape
    unused_logits = torch.zeros((batch, 2, queries, 4), dtype=logits.dtype)
    unused_boxes = torch.stack([penultimate, final], dim=1)
    return RawDetectorOutput(
        logits=logits,
        intermediate_logits=unused_logits,
        enc_outputs_class=torch.zeros((batch, queries, 4), dtype=logits.dtype),
        enc_topk_logits=torch.zeros((batch, queries, 4), dtype=logits.dtype),
        final_boxes=final,
        penultimate_boxes=penultimate,
        intermediate_boxes=unused_boxes,
    )


def _uniform_batch(logit_row: list[float], queries: int = 300):
    logits = torch.tensor([[logit_row] * queries], dtype=torch.float64)
    boxes = torch.tensor([[list(BOX)] * queries], dtype=torch.float64)
    return _raw(logits, boxes, boxes)


def test_entropy_image_score_of_uniform_queries_equals_the_query_value() -> None:
    observed = entropy_image_scores(_uniform_batch([0.0, 0.0, 0.0, 0.0]))

    assert observed.shape == (1,)
    assert float(observed[0]) == pytest.approx(0.75 * UNIFORM_ENTROPY, rel=1e-12)


def test_margin_image_score_of_uniform_queries_equals_the_query_value() -> None:
    observed = margin_image_scores(_uniform_batch([0.0, 0.0, 0.0, 0.0]))

    assert float(observed[0]) == pytest.approx(0.75 * UNIFORM_MARGIN, rel=1e-12)


def test_image_with_no_thresholded_detections_still_scores() -> None:
    # Every query has max sigmoid 0.0067, below any usable detection threshold.
    observed = entropy_image_scores(_uniform_batch([-5.0, -5.0, -5.0, -5.0]))

    assert float(observed[0]) == pytest.approx(0.0230475, rel=1e-5)


def test_image_score_is_invariant_under_query_permutation() -> None:
    generator = torch.Generator().manual_seed(17)
    logits = torch.randn((1, 300, 4), generator=generator, dtype=torch.float64) * 3.0
    final = torch.rand((1, 300, 4), generator=generator, dtype=torch.float64)
    penultimate = torch.rand((1, 300, 4), generator=generator, dtype=torch.float64)
    order = torch.randperm(300, generator=generator)

    original = _raw(logits, final, penultimate)
    permuted = _raw(logits[:, order], final[:, order], penultimate[:, order])

    assert float(entropy_image_scores(permuted)[0]) == pytest.approx(
        float(entropy_image_scores(original)[0]), rel=1e-12
    )
    assert float(margin_image_scores(permuted)[0]) == pytest.approx(
        float(margin_image_scores(original)[0]), rel=1e-12
    )


ITEM_IDS = ("item-a", "item-b", "item-c", "item-d", "item-e")


def test_random_acquisition_order_matches_the_frozen_digest_ordering() -> None:
    assert random_acquisition_order(17, ITEM_IDS) == (
        "item-c",
        "item-a",
        "item-b",
        "item-e",
        "item-d",
    )


def test_random_acquisition_order_depends_on_the_seed() -> None:
    assert random_acquisition_order(29, ITEM_IDS) == (
        "item-c",
        "item-d",
        "item-e",
        "item-a",
        "item-b",
    )


def test_random_acquisition_order_ignores_input_order() -> None:
    assert random_acquisition_order(17, tuple(reversed(ITEM_IDS))) == (
        random_acquisition_order(17, ITEM_IDS)
    )


def test_shared_start_order_uses_a_different_prefix_than_random() -> None:
    assert shared_start_order(17, ITEM_IDS) == (
        "item-d",
        "item-a",
        "item-c",
        "item-e",
        "item-b",
    )


def test_orders_reject_duplicate_item_ids() -> None:
    with pytest.raises(AcquisitionError):
        random_acquisition_order(17, ("item-a", "item-a"))


def test_select_by_score_takes_the_highest_scores_first() -> None:
    scores = {"item-a": 0.1, "item-b": 0.9, "item-c": 0.5}

    assert select_by_score(scores, 2) == ("item-b", "item-c")


def test_select_by_score_breaks_exact_ties_by_ascending_item_id() -> None:
    scores = {"item-c": 0.5, "item-a": 0.5, "item-b": 0.5}

    assert select_by_score(scores, 2) == ("item-a", "item-b")


def test_select_by_score_rejects_a_count_above_the_candidate_pool() -> None:
    with pytest.raises(AcquisitionError):
        select_by_score({"item-a": 0.1}, 2)


def test_select_by_score_rejects_a_non_finite_score() -> None:
    with pytest.raises(AcquisitionError):
        select_by_score({"item-a": float("nan"), "item-b": 0.1}, 1)


def test_float32_model_outputs_score_as_float64() -> None:
    # The detector emits float32; scoring must upcast rather than reject or
    # accumulate in float32.
    batch = _uniform_batch([0.0, 0.0, 0.0, 0.0])
    float32 = _raw(
        batch.logits.to(torch.float32),
        batch.final_boxes.to(torch.float32),
        batch.penultimate_boxes.to(torch.float32),
    )

    observed = entropy_image_scores(float32)

    assert observed.dtype == torch.float64
    assert float(observed[0]) == pytest.approx(0.75 * UNIFORM_ENTROPY, rel=1e-12)
