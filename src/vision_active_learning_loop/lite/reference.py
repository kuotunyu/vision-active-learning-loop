"""The full-label reference baseline of v0.2.1 Section 2.

One fit on every pool image with every pool label, under a named training
rule, scored once on the frozen test split. It is the ceiling the budget
curves are compared against; it never touches the test split for training or
for any choice.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ..cli_manifest import command
from .loop import BaselinePlan, LoopError, scored_fit_main
from .train import REFERENCE_FRACTION, REFERENCE_ROLE


def reference_items(
    plan: BaselinePlan, public_view: Mapping[str, Any]
) -> tuple[str, ...]:
    """Return every pool item in the frozen public view, sorted."""
    ids = tuple(sorted(str(row["item_id"]) for row in public_view.get("images", ())))
    if not ids or len(ids) != plan.pool_size:
        raise LoopError("the public view does not hold the whole pool")
    return ids


@command("lite reference")
def reference_main(argv: Sequence[str] | None = None) -> int:
    """Fit the whole labelled pool under one training rule and score it."""
    return scored_fit_main(
        argv,
        prog="val lite reference",
        stage="reference",
        role=REFERENCE_ROLE,
        fraction=REFERENCE_FRACTION,
        plan_items=reference_items,
    )


__all__ = ["reference_items", "reference_main"]
