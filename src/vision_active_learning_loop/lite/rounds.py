"""Per-arm acquisition rounds for the v0.2-lite loop.

Implements protocol Section 4: exact nested budgets, the random arm's frozen
order, the score-ranked selection of the uncertainty arms, ledger entries,
and the label-free rows a strategy is allowed to see.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from .acquisition import random_acquisition_order, select_by_score
from .diversity import DiversityError, Embeddings, hybrid_candidates, k_center_select
from .train import DIVERSITY_ARMS, REGISTERED_ARMS, REGISTERED_BUDGET_FRACTIONS

START_FRACTION = REGISTERED_BUDGET_FRACTIONS[0]
LATER_FRACTIONS = REGISTERED_BUDGET_FRACTIONS[1:]
PUBLIC_ROW_KEYS = ("item_id", "width", "height")


class RoundsError(ValueError):
    """Raised when a round's inputs or selection are not usable."""


@dataclass(frozen=True)
class LedgerEntry:
    round_index: int
    budget_fraction: float
    rank: int
    item_id: str
    score: float | None


def budget_count(fraction: float, pool_size: int) -> int:
    """Return B(p) = ceil(p * N) using exact rational arithmetic.

    Binary64 ceil gives the same answer for the registered fractions at every
    pool size checked up to 20,000; the rational form is a guarantee.
    """
    if float(fraction) not in REGISTERED_BUDGET_FRACTIONS:
        raise RoundsError("budget fraction is not registered")
    if not isinstance(pool_size, int) or isinstance(pool_size, bool):
        raise RoundsError("pool size must be an integer")
    if pool_size <= 0:
        raise RoundsError("pool size must be positive")
    return math.ceil(Fraction(str(float(fraction))) * pool_size)


def round_plan(*, pool_size: int) -> tuple[tuple[float, int, int], ...]:
    """Return (fraction, cumulative budget, new images) for each later round."""
    previous = budget_count(START_FRACTION, pool_size)
    plan: list[tuple[float, int, int]] = []
    for fraction in LATER_FRACTIONS:
        count = budget_count(fraction, pool_size)
        plan.append((fraction, count, count - previous))
        previous = count
    return tuple(plan)


@dataclass(frozen=True)
class DiversityRound:
    chosen: tuple[str, ...]
    distances: dict[str, float]
    shortlist: tuple[str, ...] | None


def diversity_round(
    arm: str,
    *,
    scores: Mapping[str, float] | None,
    acquired: Iterable[str],
    pool_ids: Sequence[str],
    count: int,
    embeddings: Embeddings | None,
) -> DiversityRound:
    """One core-set or hybrid round: candidates, centers and the greedy k-center pick."""
    if arm not in DIVERSITY_ARMS:
        raise RoundsError(f"arm {arm!r} is not a diversity arm")
    if embeddings is None:
        raise RoundsError(f"{arm} requires embeddings")
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise RoundsError("count must be a positive integer")
    taken = sorted(set(acquired))
    taken_set = set(taken)
    unacquired = tuple(item for item in pool_ids if item not in taken_set)
    if count > len(unacquired):
        raise RoundsError("count exceeds the unacquired pool")
    shortlist: tuple[str, ...] | None = None
    if arm == "coreset":
        if scores is not None:
            raise RoundsError("the coreset arm must not receive scores")
        candidates: tuple[str, ...] = unacquired
    else:
        if not isinstance(scores, Mapping):
            raise RoundsError("the hybrid arm requires a score per unacquired item")
        missing = [item for item in unacquired if item not in scores]
        if missing:
            raise RoundsError(f"score missing for {missing[0]}")
        shortlist = hybrid_candidates({item: scores[item] for item in unacquired}, count)
        candidates = shortlist
    try:
        picked = k_center_select(
            candidates, embeddings.rows(candidates), embeddings.rows(taken), count
        )
    except DiversityError as error:
        raise RoundsError(str(error)) from error
    return DiversityRound(
        chosen=tuple(item for item, _ in picked),
        distances={item: distance for item, distance in picked},
        shortlist=shortlist,
    )


def next_acquisition(
    arm: str,
    *,
    scores: Mapping[str, float] | None,
    acquired: Iterable[str],
    pool_ids: Sequence[str],
    seed: int,
    count: int,
    embeddings: Embeddings | None = None,
) -> tuple[str, ...]:
    """Choose the next `count` unacquired images for one arm."""
    if arm not in REGISTERED_ARMS:
        raise RoundsError(f"arm {arm!r} is not registered")
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise RoundsError("count must be a positive integer")
    taken = set(acquired)
    unacquired = tuple(item for item in pool_ids if item not in taken)
    if count > len(unacquired):
        raise RoundsError("count exceeds the unacquired pool")

    if arm in DIVERSITY_ARMS:
        return diversity_round(
            arm,
            scores=scores,
            acquired=taken,
            pool_ids=pool_ids,
            count=count,
            embeddings=embeddings,
        ).chosen

    if arm == "random":
        if scores is not None:
            raise RoundsError("the random arm must not receive scores")
        order = random_acquisition_order(seed, pool_ids)
        return tuple(item for item in order if item not in taken)[:count]

    if not isinstance(scores, Mapping):
        raise RoundsError("uncertainty arms require a score per unacquired item")
    missing = [item for item in unacquired if item not in scores]
    if missing:
        raise RoundsError(f"score missing for {missing[0]}")
    return select_by_score({item: scores[item] for item in unacquired}, count)


def ledger_entries(
    *,
    round_index: int,
    budget_fraction: float,
    chosen: Sequence[str],
    scores: Mapping[str, float] | None,
) -> tuple[LedgerEntry, ...]:
    """Record one round's ordered acquisitions with their selection scores."""
    return tuple(
        LedgerEntry(
            round_index=round_index,
            budget_fraction=float(budget_fraction),
            rank=rank,
            item_id=item,
            score=None if scores is None else float(scores[item]),
        )
        for rank, item in enumerate(chosen, start=1)
    )


def scoring_rows(
    rows_by_item: Mapping[str, Mapping[str, Any]], *, unacquired: Sequence[str]
) -> list[dict[str, Any]]:
    """Return the label-free pool rows a strategy may score, and nothing else."""
    public: list[dict[str, Any]] = []
    for item in unacquired:
        row = rows_by_item.get(item)
        if row is None:
            raise RoundsError(f"{item} is absent from the manifest rows")
        if row.get("split") != "pool":
            raise RoundsError(f"{item} is not a pool row; test rows are sealed")
        public.append({key: row[key] for key in PUBLIC_ROW_KEYS})
    return public
