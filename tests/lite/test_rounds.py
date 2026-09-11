"""Contracts for the per-arm acquisition rounds of the v0.2-lite loop."""

from __future__ import annotations

import pytest

from vision_active_learning_loop.lite.acquisition import random_acquisition_order
from vision_active_learning_loop.lite.rounds import (
    LedgerEntry,
    RoundsError,
    ledger_entries,
    next_acquisition,
    round_plan,
    scoring_rows,
)

POOL = tuple(f"item-{index:03d}" for index in range(100))


def test_round_plan_lists_the_three_later_budgets_with_exact_deltas() -> None:
    plan = round_plan(pool_size=2255)

    # B = 46, 113, 226, 451 for the Czech pool.
    assert [(fraction, count, delta) for fraction, count, delta in plan] == [
        (0.05, 113, 67),
        (0.10, 226, 113),
        (0.20, 451, 225),
    ]


def test_budget_count_matches_the_exact_rational_ceiling() -> None:
    from vision_active_learning_loop.lite.rounds import budget_count

    # Exact integers must come back exactly; see the note in test_loop.py.
    assert budget_count(0.10, 100) == 10
    assert budget_count(0.20, 5) == 1
    assert budget_count(0.02, 2255) == 46


def test_round_plan_deltas_sum_to_the_final_budget_minus_the_start() -> None:
    plan = round_plan(pool_size=100)

    assert sum(delta for _fraction, _count, delta in plan) == 20 - 2


def test_random_round_takes_the_next_prefix_of_the_frozen_order() -> None:
    order = random_acquisition_order(17, POOL)
    acquired = set(order[:5])

    chosen = next_acquisition(
        "random", scores=None, acquired=acquired, pool_ids=POOL, seed=17, count=3
    )

    assert chosen == order[5:8]


def test_random_round_skips_items_acquired_out_of_order() -> None:
    order = random_acquisition_order(17, POOL)
    acquired = {order[0], order[2], order[4]}

    chosen = next_acquisition(
        "random", scores=None, acquired=acquired, pool_ids=POOL, seed=17, count=2
    )

    assert chosen == (order[1], order[3])


def test_uncertainty_round_takes_the_highest_unacquired_scores() -> None:
    scores = {item: index / 100.0 for index, item in enumerate(POOL)}
    acquired = {POOL[99], POOL[98]}

    chosen = next_acquisition(
        "entropy", scores=scores, acquired=acquired, pool_ids=POOL, seed=17, count=2
    )

    assert chosen == (POOL[97], POOL[96])


def test_uncertainty_round_breaks_ties_by_ascending_item_id() -> None:
    scores = {item: 0.5 for item in POOL}

    chosen = next_acquisition(
        "margin", scores=scores, acquired=set(), pool_ids=POOL, seed=17, count=3
    )

    assert chosen == POOL[:3]


def test_uncertainty_round_requires_a_score_for_every_unacquired_item() -> None:
    scores = {item: 0.5 for item in POOL[:50]}

    with pytest.raises(RoundsError, match="score"):
        next_acquisition(
            "entropy", scores=scores, acquired=set(), pool_ids=POOL, seed=17, count=3
        )


def test_random_round_rejects_scores_it_must_not_use() -> None:
    with pytest.raises(RoundsError):
        next_acquisition(
            "random",
            scores={item: 0.5 for item in POOL},
            acquired=set(),
            pool_ids=POOL,
            seed=17,
            count=3,
        )


def test_next_acquisition_rejects_an_unregistered_arm_or_oversized_count() -> None:
    with pytest.raises(RoundsError):
        next_acquisition(
            "core_set", scores=None, acquired=set(), pool_ids=POOL, seed=17, count=1
        )
    with pytest.raises(RoundsError):
        next_acquisition(
            "random",
            scores=None,
            acquired=set(POOL[:99]),
            pool_ids=POOL,
            seed=17,
            count=2,
        )


def test_ledger_entries_record_round_rank_item_and_score() -> None:
    entries = ledger_entries(
        round_index=1,
        budget_fraction=0.05,
        chosen=("item-b", "item-a"),
        scores={"item-a": 0.2, "item-b": 0.9},
    )

    assert entries == (
        LedgerEntry(
            round_index=1, budget_fraction=0.05, rank=1, item_id="item-b", score=0.9
        ),
        LedgerEntry(
            round_index=1, budget_fraction=0.05, rank=2, item_id="item-a", score=0.2
        ),
    )


def test_ledger_entries_carry_no_score_for_the_random_arm() -> None:
    entries = ledger_entries(
        round_index=1, budget_fraction=0.05, chosen=("item-a",), scores=None
    )

    assert entries[0].score is None


def test_scoring_rows_strip_every_label_before_the_strategy_sees_them() -> None:
    rows = {
        "item-a": {
            "item_id": "item-a",
            "width": 4,
            "height": 4,
            "split": "pool",
            "boxes": [[0, 0, 0, 1, 1]],
        },
        "item-b": {
            "item_id": "item-b",
            "width": 4,
            "height": 4,
            "split": "pool",
            "boxes": [],
        },
    }

    public = scoring_rows(rows, unacquired=("item-a", "item-b"))

    assert [row["item_id"] for row in public] == ["item-a", "item-b"]
    assert all(set(row) == {"item_id", "width", "height"} for row in public)


def test_scoring_rows_refuse_a_test_row() -> None:
    rows = {
        "item-t": {
            "item_id": "item-t",
            "width": 4,
            "height": 4,
            "split": "test",
            "boxes": [],
        },
    }

    with pytest.raises(RoundsError, match="test"):
        scoring_rows(rows, unacquired=("item-t",))


# ------------------------------------------------------------------ v0.3 diversity arms

import torch  # noqa: E402

from vision_active_learning_loop.lite.diversity import Embeddings, k_center_select  # noqa: E402
from vision_active_learning_loop.lite.rounds import DiversityRound, diversity_round  # noqa: E402
from vision_active_learning_loop.lite.train import DIVERSITY_ARMS, REGISTERED_ARMS  # noqa: E402


def _embeddings(ids: tuple[str, ...]) -> Embeddings:
    generator = torch.Generator().manual_seed(7)
    vectors = torch.randn((len(ids), 6), generator=generator)
    vectors = vectors / vectors.norm(dim=1, keepdim=True)
    ordered = sorted(range(len(ids)), key=lambda index: ids[index])
    return Embeddings(
        item_ids=tuple(ids[i] for i in ordered), vectors=vectors[ordered], sha256="e" * 64
    )


def test_registered_arms_include_the_diversity_arms() -> None:
    assert REGISTERED_ARMS == ("random", "entropy", "margin", "coreset", "hybrid")
    assert DIVERSITY_ARMS == ("coreset", "hybrid")


def test_coreset_round_uses_acquired_items_as_centers_and_records_distances() -> None:
    embeddings = _embeddings(POOL)
    acquired = set(POOL[:5])
    result = diversity_round(
        "coreset", scores=None, acquired=acquired, pool_ids=POOL, count=3, embeddings=embeddings
    )
    assert isinstance(result, DiversityRound)
    assert len(result.chosen) == 3 and not set(result.chosen) & acquired
    assert set(result.distances) == set(result.chosen)
    assert result.shortlist is None
    unacquired = tuple(item for item in POOL if item not in acquired)
    direct = k_center_select(
        unacquired, embeddings.rows(unacquired), embeddings.rows(sorted(acquired)), 3
    )
    assert result.chosen == tuple(item for item, _ in direct)


def test_hybrid_round_shortlists_by_score_then_runs_k_center() -> None:
    embeddings = _embeddings(POOL)
    scores = {item: (index * 37) % 101 / 101.0 for index, item in enumerate(POOL)}
    result = diversity_round(
        "hybrid", scores=scores, acquired=set(POOL[:2]), pool_ids=POOL, count=2, embeddings=embeddings
    )
    assert result.shortlist is not None and len(result.shortlist) == 10  # 5 x 2
    assert set(result.chosen) <= set(result.shortlist)
    top = sorted((item for item in POOL[2:]), key=lambda item: (-scores[item], item))[:10]
    assert result.shortlist == tuple(top)


def test_next_acquisition_routes_the_diversity_arms() -> None:
    embeddings = _embeddings(POOL)
    chosen = next_acquisition(
        "coreset", scores=None, acquired=set(), pool_ids=POOL, seed=17, count=2, embeddings=embeddings
    )
    assert len(chosen) == 2
    with pytest.raises(RoundsError, match="embeddings"):
        next_acquisition("coreset", scores=None, acquired=set(), pool_ids=POOL, seed=17, count=2)
    with pytest.raises(RoundsError, match="scores"):
        next_acquisition(
            "coreset", scores={item: 0.1 for item in POOL}, acquired=set(), pool_ids=POOL,
            seed=17, count=2, embeddings=embeddings,
        )
    with pytest.raises(RoundsError, match="score"):
        next_acquisition(
            "hybrid", scores=None, acquired=set(), pool_ids=POOL, seed=17, count=2, embeddings=embeddings
        )
