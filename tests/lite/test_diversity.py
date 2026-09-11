"""Contracts for the v0.3 diversity arms: k-center, hybrid candidates, embeddings."""

from __future__ import annotations

import math

import pytest
import torch

from vision_active_learning_loop.lite.diversity import (
    HYBRID_FACTOR,
    DiversityError,
    cosine_distances,
    hybrid_candidates,
    k_center_reference,
    k_center_select,
)


def _unit(rows: list[list[float]]) -> torch.Tensor:
    tensor = torch.tensor(rows, dtype=torch.float32)
    return tensor / tensor.norm(dim=1, keepdim=True)


def test_cosine_distance_is_one_minus_dot_and_clamped() -> None:
    a = _unit([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0]])
    centers = _unit([[1.0, 0.0]])
    distances = cosine_distances(a, centers)
    assert distances.shape == (3, 1)
    assert distances[0, 0] == pytest.approx(0.0)
    assert distances[1, 0] == pytest.approx(1.0)
    assert distances[2, 0] == pytest.approx(2.0)


def test_cosine_distance_requires_unit_vectors() -> None:
    with pytest.raises(DiversityError, match="normal"):
        cosine_distances(torch.tensor([[2.0, 0.0]]), _unit([[1.0, 0.0]]))


def test_k_center_picks_the_farthest_from_the_nearest_center_each_step() -> None:
    ids = ("a", "b", "c", "d")
    candidates = _unit([[1.0, 0.0], [0.0, 1.0], [-1.0, 0.0], [0.7, 0.7]])
    centers = _unit([[1.0, 0.0]])
    chosen = k_center_select(ids, candidates, centers, 2)
    # c is opposite the center (distance 2); then b is 1.0 from both the center
    # and c, while d is ~0.29 from the center -> b
    assert [item for item, _ in chosen] == ["c", "b"]
    assert chosen[0][1] == pytest.approx(2.0)
    assert chosen[1][1] == pytest.approx(1.0)


def test_k_center_breaks_exact_ties_by_ascending_item_id() -> None:
    ids = ("zeta", "alpha", "mid")
    candidates = _unit([[0.0, 1.0], [0.0, 1.0], [0.0, 1.0]])
    centers = _unit([[1.0, 0.0]])
    chosen = k_center_select(ids, candidates, centers, 2)
    assert [item for item, _ in chosen] == ["alpha", "mid"]
    assert chosen[1][1] == pytest.approx(0.0)


def test_k_center_with_no_centers_starts_from_the_smallest_id() -> None:
    ids = ("b", "a")
    candidates = _unit([[1.0, 0.0], [0.0, 1.0]])
    chosen = k_center_select(ids, candidates, torch.zeros((0, 2)), 2)
    assert [item for item, _ in chosen] == ["a", "b"]
    assert chosen[0][1] == pytest.approx(2.0)


def test_k_center_rejects_more_than_the_candidates() -> None:
    with pytest.raises(DiversityError, match="count"):
        k_center_select(("a",), _unit([[1.0, 0.0]]), _unit([[0.0, 1.0]]), 2)


@pytest.mark.parametrize("seed", [0, 1, 2, 3])
def test_k_center_matches_the_reference_on_random_matrices(seed: int) -> None:
    generator = torch.Generator().manual_seed(seed)
    candidates = torch.randn((60, 8), generator=generator)
    candidates = candidates / candidates.norm(dim=1, keepdim=True)
    centers = torch.randn((5, 8), generator=generator)
    centers = centers / centers.norm(dim=1, keepdim=True)
    ids = tuple(f"item-{index:03d}" for index in range(60))
    fast = k_center_select(ids, candidates, centers, 12)
    slow = k_center_reference(ids, candidates, centers, 12)
    assert [item for item, _ in fast] == [item for item, _ in slow]
    for (_, a), (_, b) in zip(fast, slow):
        assert math.isclose(a, b, rel_tol=0, abs_tol=1e-5)


def test_hybrid_candidates_take_the_top_factor_times_count_by_score_then_id() -> None:
    scores = {"a": 0.9, "b": 0.9, "c": 0.5, "d": 0.1, "e": 0.7}
    assert hybrid_candidates(scores, count=1, factor=2) == ("a", "b")
    assert hybrid_candidates(scores, count=1, factor=3) == ("a", "b", "e")
    assert hybrid_candidates(scores, count=10) == ("a", "b", "e", "c", "d")
    assert HYBRID_FACTOR == 5
