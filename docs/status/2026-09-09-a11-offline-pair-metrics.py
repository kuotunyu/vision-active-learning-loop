"""Read-only CPU diagnostic: recompute the 13 A11 pair metrics over the twelve
existing steven006 calibration replicas (receipts + verified checkpoints).

Writes nothing into the evidence tree. Output JSON goes to the scratchpad.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(
    r"<evidence-root>\wave0"
    r"\a11-runs\wave0-a11-calibration-20260831T051426556Z-b3e22466"
)
OUT = Path(sys.argv[1])

from vision_active_learning_loop.gates.statistical_replay import (  # noqa: E402
    COSINE_DEFECT_CEILING,
    GRADIENT_CEILING,
    METRIC_KEYS,
    THRESHOLD_MULTIPLIER,
    ReplicaEvidence,
    StatisticalReplayError,
    compare_statistical_pair,
    derive_calibration_thresholds,
    expected_replica_ids,
    ordered_replica_pairs,
)
from vision_active_learning_loop.gates import statistical_replay as sr  # noqa: E402
from vision_active_learning_loop.training.checkpoint_io import (  # noqa: E402
    load_checkpoint_verified,
)

VECTOR_CEILING = getattr(sr, "VECTOR_RELATIVE_L2_CEILING", None) or getattr(
    sr, "RELATIVE_L2_CEILING", 0.10
)


def ceiling_for(key: str) -> float:
    if key.endswith("relative_difference"):
        return GRADIENT_CEILING
    if key.endswith("cosine_defect"):
        return COSINE_DEFECT_CEILING
    return VECTOR_CEILING


def main() -> int:
    started = time.time()
    replicas = []
    for replica_id in expected_replica_ids("calibration"):
        receipt_path = ROOT / "wave0" / "receipts" / f"{replica_id}.json"
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        normative = receipt["normative"]
        checkpoint_path = ROOT / "wave0" / "checkpoints" / replica_id / "step-000001.pt"
        state = load_checkpoint_verified(checkpoint_path, normative["checkpoint_sha256"])
        replicas.append(ReplicaEvidence(replica_id, receipt, state))
        print(f"loaded {replica_id} ({time.time() - started:.1f}s)", flush=True)

    pairs = []
    errors = []
    for left_e, right_e in ordered_replica_pairs(replicas, "calibration"):
        try:
            pairs.append(compare_statistical_pair(left_e, right_e))
        except StatisticalReplayError as error:
            errors.append(f"{left_e.replica_id}/{right_e.replica_id}: {error}")
    print(f"pairs={len(pairs)} errors={len(errors)} ({time.time() - started:.1f}s)", flush=True)

    per_key = {}
    for key in METRIC_KEYS:
        values = sorted(p.metrics[key] for p in pairs)
        maximum = max(values) if values else math.nan
        per_key[key] = {
            "min": values[0] if values else None,
            "median": (values[32] + values[33]) / 2 if len(values) == 66 else None,
            "max": maximum,
            "threshold_1p5x_max": THRESHOLD_MULTIPLIER * maximum,
            "ceiling": ceiling_for(key),
            "within_ceiling": (THRESHOLD_MULTIPLIER * maximum) <= ceiling_for(key),
        }

    threshold_error = None
    try:
        derive_calibration_thresholds(pairs)
    except StatisticalReplayError as error:
        threshold_error = str(error)

    result = {
        "diagnostic": "offline-cpu-recompute-of-a11-pair-metrics",
        "source_root": str(ROOT),
        "note": (
            "Read-only recomputation over the frozen steven006 calibration replicas. "
            "Not an A11 receipt; not a Wave 0 pass; makes no claim beyond same-host replay spread."
        ),
        "replica_count": len(replicas),
        "pair_count": len(pairs),
        "pair_errors": errors,
        "derive_calibration_thresholds_error": threshold_error,
        "metrics": per_key,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    for key, row in per_key.items():
        flag = "OK " if row["within_ceiling"] else "OVER"
        print(
            f"{flag} {key:48s} max={row['max']:.3e} 1.5x={row['threshold_1p5x_max']:.3e} ceiling={row['ceiling']:.3g}"
        )
    print("derive_calibration_thresholds:", threshold_error or "OK (all 13 thresholds within ceilings)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
