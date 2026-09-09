"""The protocol Section 8 gate between the shared baseline and the full run.

Reads the baseline's published metrics and fit receipt and answers one
question: may the full experiment start? It passes only when the baseline loss
decreased (median of the first 10% of steps above the median of the last 10%)
and, on CUDA, exactly the registered number of allowlisted
`grid_sampler_2d_backward_cuda` warnings were observed.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from ..cli_manifest import command
from .loop import ALLOWLISTED_BACKWARD_WARNINGS, RECEIPT_NAME
from .train import REGISTERED_BUDGET_FRACTIONS, SHARED_START_ROLE


class GateError(ValueError):
    """Raised when the baseline evidence needed by the gate is unavailable."""


def _load(path: Path, label: str) -> Mapping[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        raise GateError(f"{label} is unavailable: {error}") from error
    if not isinstance(document, Mapping):
        raise GateError(f"{label} must be a JSON object")
    return document


def evaluate_gate(experiment_dir: Path, *, device: str) -> tuple[bool, dict[str, Any]]:
    """Return the verdict and the observations it rests on."""
    root = Path(experiment_dir)
    suffix = f"{SHARED_START_ROLE}-{REGISTERED_BUDGET_FRACTIONS[0]:.2f}"
    metrics = _load(root / f"metrics-{suffix}.json", "baseline metrics")
    receipt = _load(root / "fits" / suffix / RECEIPT_NAME, "baseline fit receipt")
    try:
        loss_decreased = bool(metrics["loss"]["decreased"])
        map_value = float(metrics["metrics"]["mAP50_95"])
        environment = receipt["normative"].get("environment", {})
    except (KeyError, TypeError, ValueError) as error:
        raise GateError(f"baseline evidence is malformed: {error}") from error
    warnings = environment.get("allowlisted_backward_warnings")
    warnings_ok = (
        warnings == ALLOWLISTED_BACKWARD_WARNINGS if device == "cuda" else True
    )
    expected = ALLOWLISTED_BACKWARD_WARNINGS if device == "cuda" else None
    observations = {
        "loss_decreased": loss_decreased,
        "allowlisted_backward_warnings": warnings,
        "expected_warnings": expected,
        "mAP50_95": map_value,
    }
    return loss_decreased and warnings_ok, observations


@command("lite gate")
def gate_main(argv: Sequence[str] | None = None) -> int:
    """Print `PASS {...}` or `FAIL {...}`; exit 0, 2 (fail), or 3 (input error)."""
    parser = argparse.ArgumentParser(prog="val lite gate")
    parser.add_argument("--experiment-dir", required=True)
    parser.add_argument("--device", required=True)
    arguments = parser.parse_args(list(argv) if argv is not None else None)
    try:
        passed, observations = evaluate_gate(
            Path(arguments.experiment_dir), device=arguments.device
        )
    except GateError as error:
        print(f"lite gate input error: {error}", file=sys.stderr)
        return 3
    print(("PASS " if passed else "FAIL ") + json.dumps(observations, sort_keys=True))
    return 0 if passed else 2
