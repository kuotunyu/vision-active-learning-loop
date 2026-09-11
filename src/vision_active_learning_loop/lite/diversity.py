"""v0.3 diversity arms: DINOv2-small embeddings, greedy k-center, hybrid shortlist.

Definitions follow the v0.3 protocol Section 1 (cosine distance clamped to
[0, 2], acquired images as initial centers, farthest-from-nearest-center
greedy selection, ties by ascending item_id). Everything runs in float32 on
CPU; the pool is small enough that no chunking is needed.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

import torch

HYBRID_FACTOR = 5
UNIT_TOLERANCE = 1e-3


class DiversityError(ValueError):
    """Raised when embeddings or a selection request are not usable."""


def _check_unit(vectors: torch.Tensor, label: str) -> torch.Tensor:
    if vectors.ndim != 2:
        raise DiversityError(f"{label} must be a 2-D tensor")
    vectors = vectors.to(dtype=torch.float32)
    if vectors.shape[0] and not torch.allclose(
        vectors.norm(dim=1), torch.ones(vectors.shape[0]), atol=UNIT_TOLERANCE, rtol=0
    ):
        raise DiversityError(f"{label} must be L2-normalized")
    return vectors


def cosine_distances(candidates: torch.Tensor, centers: torch.Tensor) -> torch.Tensor:
    """[C, K] cosine distances 1 - <u, v>, clamped to [0, 2]."""
    candidates = _check_unit(candidates, "candidates")
    centers = _check_unit(centers, "centers")
    return torch.clamp(1.0 - candidates @ centers.T, 0.0, 2.0)


def _validate_request(
    candidate_ids: Sequence[str], candidate_vectors: torch.Tensor, count: int
) -> None:
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise DiversityError("count must be a positive integer")
    if len(candidate_ids) != candidate_vectors.shape[0]:
        raise DiversityError("candidate ids and vectors disagree in length")
    if len(set(candidate_ids)) != len(candidate_ids):
        raise DiversityError("candidate ids must be unique")
    if count > len(candidate_ids):
        raise DiversityError("count exceeds the candidate pool")


def k_center_select(
    candidate_ids: Sequence[str],
    candidate_vectors: torch.Tensor,
    center_vectors: torch.Tensor,
    count: int,
) -> tuple[tuple[str, float], ...]:
    """Greedy k-center: repeatedly take the candidate farthest from its nearest center."""
    candidate_vectors = _check_unit(candidate_vectors, "candidates")
    center_vectors = _check_unit(center_vectors, "centers")
    _validate_request(candidate_ids, candidate_vectors, count)
    ids = list(candidate_ids)
    if center_vectors.shape[0]:
        nearest = cosine_distances(candidate_vectors, center_vectors).min(dim=1).values
    else:
        nearest = torch.full((len(ids),), 2.0, dtype=torch.float32)
    remaining = list(range(len(ids)))
    chosen: list[tuple[str, float]] = []
    for _ in range(count):
        best = min(remaining, key=lambda index: (-float(nearest[index]), ids[index]))
        chosen.append((ids[best], float(nearest[best])))
        remaining.remove(best)
        if remaining:
            to_new = cosine_distances(
                candidate_vectors[remaining], candidate_vectors[best : best + 1]
            )[:, 0]
            nearest[remaining] = torch.minimum(nearest[remaining], to_new)
    return tuple(chosen)


def k_center_reference(
    candidate_ids: Sequence[str],
    candidate_vectors: torch.Tensor,
    center_vectors: torch.Tensor,
    count: int,
) -> tuple[tuple[str, float], ...]:
    """The plain reference: recompute every candidate's nearest-center distance each step."""
    candidate_vectors = _check_unit(candidate_vectors, "candidates")
    center_vectors = _check_unit(center_vectors, "centers")
    _validate_request(candidate_ids, candidate_vectors, count)
    ids = list(candidate_ids)
    centers = [center_vectors[i] for i in range(center_vectors.shape[0])]
    remaining = list(range(len(ids)))
    chosen: list[tuple[str, float]] = []
    for _ in range(count):
        scored = []
        for index in remaining:
            if centers:
                distance = min(
                    float(
                        torch.clamp(
                            1.0 - torch.dot(candidate_vectors[index], center), 0.0, 2.0
                        )
                    )
                    for center in centers
                )
            else:
                distance = 2.0
            scored.append((-distance, ids[index], index, distance))
        scored.sort()
        _, item, index, distance = scored[0]
        chosen.append((item, distance))
        remaining.remove(index)
        centers.append(candidate_vectors[index])
    return tuple(chosen)


def hybrid_candidates(
    scores: Mapping[str, float], count: int, factor: int = HYBRID_FACTOR
) -> tuple[str, ...]:
    """Top min(factor * count, all) item ids by uncertainty score, ties by ascending id."""
    if not isinstance(count, int) or isinstance(count, bool) or count <= 0:
        raise DiversityError("count must be a positive integer")
    ordered = sorted(scores, key=lambda item: (-float(scores[item]), item))
    return tuple(ordered[: min(factor * count, len(ordered))])
