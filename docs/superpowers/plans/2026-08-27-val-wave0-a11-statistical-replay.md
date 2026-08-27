# Wave 0 A11 Statistical Replay Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the failed legacy Wave 0 numerical-bound gate with one independently calibrated and independently validated same-host statistical replay envelope, without changing the pinned model, dependency stack, synthetic step, historical evidence, or any Wave 1 research contract.

**Architecture:** A new Python gate module loads twelve existing schema-v3 feasibility receipts and their verified checkpoints, reuses the existing A3 exact-comparison result, computes thirteen closed CPU-float64 pair metrics, and produces either a calibration threshold receipt or a validation aggregate receipt. Two closed JSON schemas and a focused semantic-validator module keep those receipts exact and fail closed. One new PowerShell launcher owns the host-side two-phase lifecycle: it preregisters disjoint identities, builds separate fresh images and caches, serializes each twelve-process cohort behind separate RTX 4090 leases, releases calibration before validation, preserves every failure, and never starts Wave 1.

**Tech Stack:** Python 3.12.11; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; pytest 9.0.2; JSON Schema draft 2020-12; PowerShell 7 plus Windows PowerShell 5.1 parser checks; Docker Desktop Linux engine; RTX 4090 24 GB.

## Global Constraints

- The authoritative specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `b59b0d4407b98b460f6166ea7288ba6021dc7a78`, especially Section 5.2.15.
- At that commit the specification Git blob is exactly 205,867 bytes, has SHA-256 `772b9258f7926d9a23c62d1e803a581343be2324513ec09c38b5339f007f8838`, and Git object `3921de59fca0ba5b255b8c57aee2b1f16995b250`.
- This plan commit must be the direct child of the specification commit and must change only `docs/superpowers/plans/2026-08-27-val-wave0-a11-statistical-replay.md`.
- The current authorization covers this plan only. No implementation task, Docker build, GPU lease, calibration, validation, RDD access, or Wave 1 work may begin until the owner explicitly authorizes implementation against the reviewed plan commit.
- The branch is exactly `codex/wave0-model-contract`; the registered linked worktree and canonical `main` worktree must share one Git common directory and be clean at every implementation and runtime entry gate.
- Preserve the closed A10-bound A7 campaign `wave0-a7-20260827T034653088Z`, source `2cb3e38b4328eee2b3497571e05565c73f4691c9`, image `sha256:ea6bde836cad9fd96c3c8999fb00a7fe7aaecdc7b34d870e0ad9b6ce710f2afa`, all earlier A2–A10 objects, and every historical failure verdict byte-for-byte.
- The plan-stage filesystem inventory is 64,306 regular files below `D:\vision-active-learning-loop-artifacts\wave0`. The expected project-image inventory is 21 images from the closed lineage; Docker was offline during plan drafting, so Task 1 must inspect and prove that exact image set before any implementation edit rather than accepting the count by implication.
- Keep the exact detector, model and processor revisions, DINOv2 revision, 300 queries, four RDD classes, seed 17, synthetic fixture, three decoder layers, three feature levels, BF16 step, Math-only SDPA scope, nine-warning grid-sample exception, optimizer/scheduler recipe, 22 GiB peak-allocation ceiling, package versions, CUDA identity, checkpoint round-trip, and source-hash rules.
- Calibration has exactly twelve fresh-process replicas `calibration-00` through `calibration-11`; validation has exactly twelve different fresh-process replicas `validation-00` through `validation-11`. Each cohort has all `12 choose 2 = 66` lexicographically ordered unordered pairs.
- The thirteen metric keys are closed and lexicographically ordered: one gradient relative-difference key plus relative-L2 and cosine-defect keys for detector/backbone model updates and detector/backbone AdamW `exp_avg` and `exp_avg_sq` states.
- The threshold formula is exactly `T_m = 1.5 * M_m`, identifier `wave0-a11-pairwise-max-times-1.5-v1`, with no floor. The exact binary64 constants are `1.5 == 0x1.8000000000000p+0`, `0.01 == 0x1.47ae147ae147bp-7`, `0.10 == 0x1.999999999999ap-4`, and `0.005 == 0x1.47ae147ae147bp-8`.
- Calibration and validation use different run IDs, image tags/IDs, campaign roots, cache roots, leases, container IDs, paths, timestamps, receipts, and checkpoints. They use the same source/specification/plan/base identities, model and fixture identities, dependency versions, GPU UUID, driver/CUDA identity, and exact cache inventory.
- Calibration success publishes receipt type `statistical-replay-calibration`, schema version 1, status `RECORDED`, and terminal `WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`. Calibration failure leaves the success receipt absent and publishes only the no-clobber campaign result and bound diagnostic.
- Validation publishes receipt type `statistical-replay-validation`, schema version 1, status in the closed set `{"PASS", "FAIL"}`. Only complete all-pairs success may publish terminal `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`; every failure uses `WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`.
- The specification simultaneously registers a validation `FAIL` receipt and says every listed invariant is true. This plan resolves that representational contradiction without falsifying evidence: calibration `RECORDED` and validation `PASS` require every invariant true; a validation `FAIL` is publishable only after a structurally complete 66-pair evaluation and requires every structural/evidence invariant true while `all_pairs_within_thresholds` and/or `all_pairs_within_ceilings` is Boolean false. No other false invariant is accepted in an aggregate receipt; earlier structural, identity, preservation, or execution failures publish only the campaign result/diagnostic and no validation aggregate. Owner approval of this plan explicitly approves this interpretation; otherwise implementation must stop for a specification amendment.
- The only permitted claim language is `empirically_replayable_same_host` or `calibrated_statistical_replay`. Never describe the training step, CUDA backward, model, or project as deterministic, bitwise reproducible, or reproducible across GPUs, hosts, drivers, CUDA/PyTorch releases, or long trajectories.
- The implementation tracked-file allowlist is exactly the following nine paths. A tenth tracked implementation file is a hard stop:
  - `src/vision_active_learning_loop/gates/statistical_replay.py`
  - `src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py`
  - `src/vision_active_learning_loop/artifacts/receipts.py`
  - `schemas/statistical-replay-calibration-receipt.schema.json`
  - `schemas/statistical-replay-validation-receipt.schema.json`
  - `tests/gates/test_statistical_replay.py`
  - `tests/artifacts/test_statistical_replay_receipts.py`
  - `scripts/run_wave0_a11.ps1`
  - `tests/gates/test_wave0_a11_launcher.py`
- Do not modify `numerical_replay.py`, the existing A3 limits, any A7 script, Dockerfile, model/config pin, dependency file, `uv.lock`, existing schema, existing test, specification, plan, historical evidence, dataset rule, seed, budget, arm, fit count, metric, or research claim.
- No wildcard acceptance, retry, partial-cohort rescue, averaging rescue, threshold override, validation-to-calibration feedback, existing destination reuse, CPU fallback, Colab substitution, custom CUDA kernel, RDD access, Wave 1, remote operation, push, merge, tag, Release, or publication is authorized.

## File Responsibility Map

| Path | Responsibility |
|---|---|
| `gates/statistical_replay.py` | Closed replica IDs and metric keys; receipt/checkpoint loading; exact-pair gating; float64 metrics; calibration threshold derivation; validation summaries and CLI commands |
| `artifacts/statistical_replay_receipts.py` | Pure semantic consistency checks for the two A11 receipt types; no filesystem publication |
| `artifacts/receipts.py` | Register the two schemas and dispatch their semantic validators through the existing atomic receipt pipeline |
| two new schema files | Closed structural contracts with `additionalProperties: false` at every object boundary |
| two Python test files | Hand-computed math, mutation/adversarial schema tests, CLI/no-clobber behavior, and legacy-bound isolation |
| `scripts/run_wave0_a11.ps1` | Host preflight, fresh image/cache/lease lifecycle, 12+12 fresh Docker processes, phase closure, history preservation, and exact stop terminals |
| `tests/gates/test_wave0_a11_launcher.py` | Adapter-driven process/order/path/identity/lease/failure tests without Docker or GPU |

---

### Task 1: Freeze the A11 entry identity and preservation baseline

**Files:**
- Modify: none
- Historical evidence: read-only
- Temporary output: one timestamped `FileMode.CreateNew` JSON below `[IO.Path]::GetTempPath()`

**Interfaces:**
- Consumes: approved A11 specification, this future plan commit, registered Git worktree, all closed A2–A10 artifacts and images
- Produces: exact pre-implementation Git/artifact/image baseline used by every later task

- [ ] **Step 1: Verify direct-child docs lineage and Git topology**

Run:

```powershell
$SpecCommit = 'b59b0d4407b98b460f6166ea7288ba6021dc7a78'
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a11-statistical-replay.md'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
if ((git rev-parse "$PlanCommit^").Trim() -cne $SpecCommit) {
    throw 'A11 plan parent mismatch'
}
if (@(git diff-tree --no-commit-id --name-only -r $SpecCommit).Count -ne 1) {
    throw 'A11 specification commit scope mismatch'
}
if (@(git diff-tree --no-commit-id --name-only -r $PlanCommit).Count -ne 1) {
    throw 'A11 plan commit scope mismatch'
}
git worktree list --porcelain
git status --short
git diff --cached --name-only
```

Require branch `codex/wave0-model-contract`, HEAD equal to the plan commit, clean linked and canonical worktrees, empty staging, and identical Git common directories. Do not repair a mismatch.

- [ ] **Step 2: Rehash the fixed A10 boundary**

Require the immutable A10 identities:

```text
environment receipt       7fc82adaa6053a1d6a9617410b27fa5200882d7c99758567bef2c60c8a704e8f
model-assets receipt      c1e1620fdaff57e3fc4424a393d925b194301f866e3215089303ec3ad8500483
model-contract receipt    1258c45e5b8b672ca81cc8e2b5af9d955bb22eece3b1aabcf0485174c1a706c0
A7 aggregate receipt      f4a6f0f3fd2cc54f319e65141fa1b0a0367a6e14e2baa0df58268b051270251f
campaign result           3f10fbfe8bf33c89fddb71c71e58457f738fa92d933ad05115fa1e66e3126239
pre-closure manifest      55f78146f201d090807fcc62a836ec9db82604e3a878ca2323de85edda85f6e2
historical preservation  93c9093efebfe7c78a9cf6ae6a10f264b52271aee434236a71d68801b9e0ad3f
closure manifest          3f3c1e548d0454bc81c44e8130e710e7e8d0b47264f69afdb96560d7fbc92162
```

Parse the A7 aggregate and require `ATTRIBUTED`, all aggregate invariants true, exact source/specification/plan/image bindings, the registered `decoder-2/feature-2` outgoing-value-gradient attribution, no A11 threshold fields, and the permanent Wave-1-forbidden terminal.

- [ ] **Step 3: Freeze the complete artifact and Docker image sets**

Start with read-only Docker health checks. Require `desktop-linux`, a Linux Server, successful `docker info`, and no running project container. Enumerate every regular non-link file below `D:\vision-active-learning-loop-artifacts\wave0`; require 64,306 exact paths and record path, size, SHA-256. Inspect all `vision-active-learning-loop:*` images by exact tag, ID, labels, created time, and parent/base identity; require the expected 21-image set. Require no active GPU lease and unset `VAL_DATA_ROOT`.

Write the baseline outside the repository/artifact root using:

```powershell
$Path = Join-Path ([IO.Path]::GetTempPath()) (
    'val-a11-entry-' + [Guid]::NewGuid().ToString('N') + '.json'
)
$Stream = [IO.File]::Open($Path, [IO.FileMode]::CreateNew,
    [IO.FileAccess]::Write, [IO.FileShare]::None)
```

The JSON binds specification/plan commits, protected Git, artifact/image arrays, the eight fixed A10 hashes, active/released leases, project containers, Docker/GPU health, and only the presence Boolean for `VAL_DATA_ROOT`. Parse it back and record its SHA-256. Any mismatch stops before an implementation edit.

---

### Task 2: Implement exact A11 pair metrics and threshold mathematics

**Files:**
- Create: `src/vision_active_learning_loop/gates/statistical_replay.py`
- Create: `tests/gates/test_statistical_replay.py`

**Interfaces:**
- Consumes: `compare_replay(canonical_receipt, canonical_state, replay_receipt, replay_state)` from `gates.numerical_replay`, schema-v3 feasibility mappings, and verified `CheckpointState` objects
- Produces:
  - `ReplicaEvidence(replica_id: str, receipt: Mapping[str, object], checkpoint: CheckpointState)`
  - `PairMetrics(left_replica_id: str, right_replica_id: str, exact: Mapping[str, object], metrics: Mapping[str, float])`
  - `compare_statistical_pair(left: ReplicaEvidence, right: ReplicaEvidence) -> PairMetrics`
  - `derive_calibration_thresholds(pairs: Sequence[PairMetrics]) -> Mapping[str, Mapping[str, object]]`
  - `summarize_validation(pairs: Sequence[PairMetrics], thresholds: Mapping[str, object]) -> Mapping[str, object]`

- [ ] **Step 1: Write RED tests for the closed inventories**

Define the exact metric keys in the test, not by importing the production constant:

```python
EXPECTED_METRIC_KEYS = (
    "gradient_norm.relative_difference",
    "model_update.backbone.cosine_defect",
    "model_update.backbone.relative_l2",
    "model_update.detector.cosine_defect",
    "model_update.detector.relative_l2",
    "optimizer_state.backbone.exp_avg.cosine_defect",
    "optimizer_state.backbone.exp_avg.relative_l2",
    "optimizer_state.backbone.exp_avg_sq.cosine_defect",
    "optimizer_state.backbone.exp_avg_sq.relative_l2",
    "optimizer_state.detector.exp_avg.cosine_defect",
    "optimizer_state.detector.exp_avg.relative_l2",
    "optimizer_state.detector.exp_avg_sq.cosine_defect",
    "optimizer_state.detector.exp_avg_sq.relative_l2",
)
```

Require `calibration-00..11` and `validation-00..11` to produce exactly 66 lexicographic pairs. Missing, extra, duplicate, non-zero-padded, cross-cohort, or reordered IDs must raise `StatisticalReplayError`.

- [ ] **Step 2: Write RED tests for hand-computed float64 metrics**

Construct tiny CPU float64 checkpoint fixtures with exact discrete state and known vectors. Prove:

```python
assert gradient_relative_difference(2.0, 1.0) == 0.5
assert vector_metrics(torch.tensor([1.0, 0.0]), torch.tensor([0.0, 1.0])) == {
    "relative_l2": math.sqrt(2.0),
    "cosine_defect": 1.0,
}
```

Also test identical vectors, one-ULP endpoint normalization inside `1e-12`, an endpoint outside `1e-12`, zero norm, NaN/Inf, dtype/shape/order mismatch, missing optimizer moment, and Boolean-as-number rejection.

- [ ] **Step 3: Write RED tests that isolate A11 from legacy numerical acceptance**

Build an exact-compatible pair whose A3 `vector_relative_l2_max == 1e-3` comparison fails but whose values remain valid A11 observations. Require `compare_statistical_pair` to retain the existing A3 exact comparison and compute A11 metrics without treating the legacy numerical failure as an A11 failure. An A3 exact-field failure must still stop before any A11 metric is returned.

- [ ] **Step 4: Write RED threshold and validation tests**

For all 66 pairs, require per-key maxima, `float.hex()` serialization, `1.5 * M_m`, no floor, threshold-inventory digest, and practical ceiling checks. Include exact-zero calibration, threshold rounding, one ceiling breach, one validation value exactly equal to threshold, and one one-ULP-above-threshold failure. Verify the validation median is the binary64 average of the 33rd and 34th values after ascending numeric sort.

- [ ] **Step 5: Run the focused tests to prove RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_statistical_replay.py
```

Expected: collection fails because `vision_active_learning_loop.gates.statistical_replay` does not exist. Fixture, import-environment, or existing-test failures are invalid RED evidence.

- [ ] **Step 6: Implement the minimal pure-Python calculation surface**

Start the module with the exact constants and immutable records:

```python
THRESHOLD_MULTIPLIER = 1.5
GRADIENT_CEILING = 0.01
RELATIVE_L2_CEILING = 0.10
COSINE_DEFECT_CEILING = 0.005
THRESHOLD_FORMULA = "wave0-a11-pairwise-max-times-1.5-v1"

@dataclass(frozen=True)
class ReplicaEvidence:
    replica_id: str
    receipt: Mapping[str, object]
    checkpoint: CheckpointState

@dataclass(frozen=True)
class PairMetrics:
    left_replica_id: str
    right_replica_id: str
    exact: Mapping[str, object]
    metrics: Mapping[str, float]
```

Call existing `compare_replay` once per pair and consume only its `exact` mapping;
do not use `ReplayComparison.passed`, `ReplayComparison.errors`, or its legacy
`numerical` mapping, and do not copy or modify the A3 constants. For each
detector/backbone model-update role, exact common-preimage compatibility makes the
post-update checkpoint difference equal to the update-vector difference; combine
that difference norm with the two receipt-recorded positive update norms and the
binary64 law of cosines. Traverse optimizer states in the exact registered
parameter order. Convert tensors to detached CPU float64 before sums, differences,
dot products, and norms. Reject invalid mathematical domains rather than clamping,
except the registered `1e-12` endpoint normalization.

- [ ] **Step 7: Run GREEN and retain the isolated math unit uncommitted**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py
git diff --check -- `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_statistical_replay.py
```

Require all legacy A3 tests unchanged and green. Keep staging empty and retain the
two files as uncommitted candidate changes; Section 5.2.15 prohibits every
implementation commit until the complete Task 6 gate and review have passed.

---

### Task 3: Add closed A11 receipt schemas and semantic validation

**Files:**
- Create: `schemas/statistical-replay-calibration-receipt.schema.json`
- Create: `schemas/statistical-replay-validation-receipt.schema.json`
- Create: `src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Create: `tests/artifacts/test_statistical_replay_receipts.py`

**Interfaces:**
- Consumes: calibration/validation receipt mappings produced by Task 4
- Produces:
  - `validate_calibration_consistency(normative: Mapping[str, object], metadata: Mapping[str, object]) -> None`
  - `validate_validation_consistency(normative: Mapping[str, object], metadata: Mapping[str, object]) -> None`
  - `atomic_write_receipt(path, receipt)` support for `("statistical-replay-calibration", 1)` and `("statistical-replay-validation", 1)`

- [ ] **Step 1: Write RED schema-shape tests**

Build one complete valid calibration receipt and one complete valid validation receipt. Their root is exactly:

```json
{
  "receipt_type": "statistical-replay-calibration",
  "schema_version": 1,
  "normative": {},
  "metadata": {}
}
```

The calibration normative object requires exactly `phase`, `identity`, `replicas`, `pairs`, `metric_keys`, `practical_ceilings`, `derivation`, `thresholds`, `threshold_inventory_sha256`, `invariants`, `historical_preservation`, `status`, `errors`, and `terminal`. Validation replaces `derivation` and `thresholds` with `calibration_binding`, `cross_phase_identity`, `summaries`, and `all_pairs_decision`. Every object uses `additionalProperties: false`.

- [ ] **Step 2: Write RED metadata, replica, pair, and invariant mutations**

Require closed metadata keys `run_id`, `source_commit`, `specification_commit`, `plan_commit`, `image_tag`, `image_id`, `base_image_digest`, `owner_authorization_id`, `timestamp`, and optional publication-added `receipt_content_sha256`. Replica entries contain exact `replica_id` plus `path`, `size`, and `sha256` records for one schema-v3 feasibility receipt and one checkpoint. Pair entries contain exact left/right IDs, the existing exact-comparison mapping, and all thirteen finite metrics.

Mutate each required field through missing, extra, wrong type, Boolean-as-integer, non-finite, wrong hash, reordered IDs, wrong pair count, alias metric, duplicated pair, extra invariant, truthy non-Boolean invariant, status/error contradiction, and wrong terminal. Every mutation must fail semantic validation even if its shape still passes JSON Schema.

Define the invariant keys independently in tests as these exact ordered tuples:

```python
CALIBRATION_INVARIANTS = (
    "replica_count_exact",
    "replica_ids_exact",
    "replica_receipts_valid",
    "cohort_identity_exact",
    "pair_count_exact",
    "pair_order_exact",
    "metric_keys_exact",
    "exact_comparisons_pass",
    "finite_metrics",
    "thresholds_recomputed",
    "thresholds_within_ceilings",
    "publication_no_clobber",
    "historical_evidence_preserved",
)

VALIDATION_INVARIANTS = (
    "replica_count_exact",
    "replica_ids_exact",
    "replica_receipts_valid",
    "cohort_identity_exact",
    "pair_count_exact",
    "pair_order_exact",
    "metric_keys_exact",
    "exact_comparisons_pass",
    "finite_metrics",
    "calibration_binding_exact",
    "cross_phase_static_identity_exact",
    "cross_phase_runtime_identity_distinct",
    "all_pairs_within_thresholds",
    "all_pairs_within_ceilings",
    "publication_no_clobber",
    "historical_evidence_preserved",
)
```

For calibration `RECORDED` and validation `PASS`, every value must be the Boolean
`True` and `errors` must be empty. For a complete validation `FAIL`, only
`all_pairs_within_thresholds` and/or `all_pairs_within_ceilings` may be Boolean
`False`; `errors` must be the exact sorted list of failed pair/metric decisions and
the terminal must be the normative-failure terminal. Any other false invariant is
an upstream failure and must not produce an aggregate receipt.

- [ ] **Step 3: Write RED recomputation and cross-phase tests**

Calibration validation recomputes all 66 pair orders, all maxima, both number/hex
representations, every threshold, every ceiling comparison, and
`threshold_inventory_sha256`. The digest is
`canonical_json_sha256({"formula": THRESHOLD_FORMULA, "metric_keys":
list(METRIC_KEYS), "thresholds": thresholds})`, where each lexicographically
inserted threshold entry contains exactly `maximum`, `maximum_hex`, `threshold`,
and `threshold_hex`. Validation recomputes its raw values and min/median/max
summaries and verifies the calibration receipt content hash and run ID.

The closed cross-phase equal map covers source/specification/plan/base identities,
model and processor revisions and hashes, config and fixture hashes, package
versions, driver/CUDA identity, GPU name/UUID, and model-cache inventory digest.
The closed distinct map covers run ID, image ID/tag, campaign root, cache root,
lease ID/path, container IDs, replica receipt/checkpoint paths and hashes,
timestamps, and audit paths. Reject an omitted or extra identity, a different equal
identity such as GPU UUID, or a reused distinct identity such as a run, image,
cache, lease, container, receipt, checkpoint, timestamp, or path.

- [ ] **Step 4: Prove RED**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/artifacts/test_statistical_replay_receipts.py
```

Expected: failure because both schema files and validator module are absent.

- [ ] **Step 5: Add the schemas and pure semantic validators**

Keep the validator module independent of `receipts.py` to avoid a circular import. Use an exact-key helper rather than truthiness:

```python
class StatisticalReplayReceiptError(ValueError):
    """Raised when an A11 receipt contradicts its embedded evidence."""

def _require_exact_keys(
    value: object, expected: frozenset[str], label: str
) -> Mapping[str, object]:
    if not isinstance(value, Mapping) or frozenset(value) != expected:
        raise StatisticalReplayReceiptError(f"{label} fields mismatch")
    return value
```

The semantic functions use exact set/list equality and recomputation; they never trust `status`, an invariant Boolean, a stored maximum, a threshold, a summary, or `all_pairs_decision` by itself.

- [ ] **Step 6: Register both receipt types in the existing pipeline**

Add exactly these entries to `_ALLOWED_SCHEMAS`:

```python
("statistical-replay-calibration", 1):
    _SCHEMA_ROOT / "statistical-replay-calibration-receipt.schema.json",
("statistical-replay-validation", 1):
    _SCHEMA_ROOT / "statistical-replay-validation-receipt.schema.json",
```

Require non-empty run IDs for both. Dispatch to the new semantic functions and translate `StatisticalReplayReceiptError` into `ReceiptValidationError` without changing validation of any existing receipt type.

- [ ] **Step 7: Run GREEN and atomic publication tests without committing**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py
git diff --check
```

Include explicit tests that existing output, missing parent, link/junction boundary, staging failure, and publication race remain no-clobber.
Keep staging empty; these five additional paths remain part of the same uncommitted
candidate as Task 2.

---

### Task 4: Add calibration and validation CLI gates

**Files:**
- Modify: `src/vision_active_learning_loop/gates/statistical_replay.py`
- Modify: `tests/gates/test_statistical_replay.py`

**Interfaces:**
- Consumes: one closed phase manifest, twelve feasibility receipts, twelve checkpoints, and for validation one verified calibration receipt
- Produces:
  - `@command("gate statistical-replay calibrate") calibration_main(argv: Sequence[str] | None = None) -> int`
  - `@command("gate statistical-replay validate") validation_main(argv: Sequence[str] | None = None) -> int`

- [ ] **Step 1: Write RED phase-manifest tests**

Build the closed test manifest with exactly twelve fixture-backed file records. The
test helper must write each valid schema-v3 receipt and checkpoint first, then
derive the record from the bytes that the loader will consume:

```python
def file_record(path: Path) -> dict[str, object]:
    return {
        "path": path.as_posix(),
        "size": path.stat().st_size,
        "sha256": sha256_file(path),
    }

run_id = "wave0-a11-calibration-20260827T130000000Z"
cache_root = phase_root / "cache"
cache_root.mkdir()
cache_inventory_sha256 = write_model_cache_fixture(cache_root)
lease_path = write_audit_fixture(root=phase_root, name="lease")
history_path = write_audit_fixture(root=phase_root, name="history")
audits = {}
for audit_name in (
    "identity",
    "image_inspect",
    "cache_inventory",
    "gpu_preflight",
):
    audits[audit_name] = file_record(
        write_audit_fixture(root=phase_root, name=audit_name)
    )
replicas = []
for index in range(12):
    replica_id = f"calibration-{index:02d}"
    replica_timestamp = f"2026-08-27T13:00:{index:02d}+00:00"
    receipt_path, checkpoint_path, invocation_audit_path = write_replica_fixture(
        root=phase_root,
        replica_id=replica_id,
        run_id=run_id,
        timestamp=replica_timestamp,
    )
    replicas.append(
        {
            "replica_id": replica_id,
            "container_id": f"{index + 1:064x}",
            "timestamp": replica_timestamp,
            "invocation_audit": file_record(invocation_audit_path),
            "feasibility": file_record(receipt_path),
            "checkpoint": file_record(checkpoint_path),
        }
    )

manifest = {
    "schema_version": 1,
    "phase": "calibration",
    "run_id": run_id,
    "campaign_root": phase_root.as_posix(),
    "source_commit": "1" * 40,
    "specification_commit": "b59b0d4407b98b460f6166ea7288ba6021dc7a78",
    "plan_commit": "2" * 40,
    "image_tag": "vision-active-learning-loop:wave0-a11-calibration-test",
    "image_id": "sha256:" + "3" * 64,
    "base_image_digest": "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356",
    "owner_authorization_id": "OWNER-A11-TEST",
    "model_cache": {
        "path": cache_root.as_posix(),
        "inventory_sha256": cache_inventory_sha256,
    },
    "gpu": {
        "name": "NVIDIA GeForce RTX 4090",
        "uuid": "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63",
        "driver": "test-driver",
        "cuda_runtime": "12.6",
    },
    "lease": {
        "lease_id": "wave0-a11-calibration-lease-test",
        **file_record(lease_path),
    },
    "historical_preservation": file_record(history_path),
    "audits": audits,
    "replicas": replicas,
}
```

The top-level key set is exactly the keys shown above. `audits` has exactly
`identity`, `image_inspect`, `cache_inventory`, and `gpu_preflight`; each is a
path/size/SHA-256 record. Each replica has exactly `replica_id`, `container_id`,
`timestamp`, `invocation_audit`, `feasibility`, and `checkpoint`. The invocation
audit is a closed JSON record binding the exact argv, exit code, and stdout/stderr
path/size/SHA-256 records for that one fresh process. Require paths confined below
the mounted phase root, regular non-link files, exact file sizes/hashes, correct run
ID and timestamp on every receipt, exact schema-v3 PASS receipts, verified
checkpoint digests/input bindings, unique 64-hex container IDs, and exact replica
order. The validation manifest uses the same closed shape with phase-specific IDs
and paths.

- [ ] **Step 2: Write RED CLI success and failure tests**

Calibration success must publish one content-addressed receipt, print only its calibration terminal, and return zero. A metric/ceiling/input failure returns 2, writes an error to stderr, and leaves the success output nonexistent. Validation success publishes PASS/terminal and returns zero; a complete out-of-envelope validation publishes FAIL/terminal and returns 2. Malformed calibration binding or phase manifest returns 2 without a partial receipt. Existing output returns 3 and remains byte-identical.

- [ ] **Step 3: Prove RED**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_statistical_replay.py -k 'manifest or cli'
```

Expected: commands are absent from the lazy manifest.

- [ ] **Step 4: Implement closed loading and receipt construction**

Use these CLI signatures:

```text
val gate statistical-replay calibrate \
  --phase-manifest MANIFEST --phase-root ROOT --output OUTPUT

val gate statistical-replay validate \
  --phase-manifest MANIFEST --phase-root ROOT \
  --calibration-receipt RECEIPT --output OUTPUT
```

Validate each feasibility receipt through the existing allowlisted schema and
current run ID, then derive the checkpoint input binding from its verified
`normative.model_contract_receipt_sha256`:

```python
expected_input_digests = {
    "model_contract_receipt": feasibility_normative[
        "model_contract_receipt_sha256"
    ]
}
checkpoint = load_checkpoint_verified(
    checkpoint_path,
    checkpoint_sha256,
    expected_input_digests=expected_input_digests,
)
```

Do not accept an input-digest assertion from the phase manifest itself. Build
metadata exclusively from the verified phase manifest. Publish through
`atomic_write_receipt`; never create the output parent and never write a failure
receipt at the calibration success destination.

- [ ] **Step 5: Run command discovery and gate tests without committing**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/cli/test_cli.py `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_statistical_replay_receipts.py
git diff --check
```

Require the AST-built manifest to discover both commands without importing GPU/model modules during discovery.
Keep staging empty and retain the cumulative candidate uncommitted.

---

### Task 5: Add the fail-closed two-phase A11 launcher

**Files:**
- Create: `scripts/run_wave0_a11.ps1`
- Create: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: exact owner authorization, reviewed source/specification/plan commits, Docker Desktop Linux engine, external Wave 0 root, and one RTX 4090
- Produces: separate calibration/validation run IDs, images, roots, cache inventories, leases/releases, 12+12 replica records, aggregate receipts, failure diagnostics, preservation records, and closures

- [ ] **Step 1: Write RED identity and preflight tests**

The script parameters are exactly:

```powershell
param(
    [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedBranch,
    [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
)
```

Adapter tests must reject a wrong worktree/branch/HEAD/common-dir, dirty linked or canonical tree, set `VAL_DATA_ROOT`, non-Linux Docker, missing Server, non-4090/multiple GPU rows, existing phase root/tag/cache/checkpoint/receipt/lease destination, active project container, active lease, historical drift, and blank/malformed identity. A failed read-only preflight must create no run ID, root, image, cache, or lease.

- [ ] **Step 2: Write RED process-order and fresh-identity tests**

Using fake `docker`, `git`, GPU, and hashing adapters, require the exact order:

```text
read-only preflight
→ preregister both run IDs/tags/root names in calibration identity audit
→ calibration build/inspect
→ calibration networked CPU-only cache preflight
→ calibration GPU lease
→ calibration environment/assets/model-contract
→ calibration-00..11 as twelve separate docker run --rm processes
→ calibration gate and receipt validation
→ calibration lease release and closure
→ validation build/inspect
→ validation networked CPU-only cache preflight
→ validation GPU lease
→ validation environment/assets/model-contract
→ validation-00..11 as twelve separate docker run --rm processes
→ validation gate and receipt validation
→ validation lease release, history rehash, result, manifest, closure
```

Validation must not build, create its root, acquire a lease, or run if calibration does not close with the exact RECORDED terminal.

- [ ] **Step 3: Write RED Docker/mount/replica tests**

Every model execution uses `--rm --gpus all --network none`, the phase cache read-only, the phase root read-write, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and the exact image ID rather than a mutable tag. Each replica invokes `val probe training-feasibility` once with its phase run ID, unique absent checkpoint root, unique absent receipt, and the common phase model-contract receipt. No container or CUDA context may serve two replicas.

Among `docker run` stages, only the cache preflight may use a network; it must be
CPU-only and retain the A10 exact `PASS\n`/empty-stderr contract. The pinned
Dockerfile build may use its normal build-time network to reproduce the locked
environment, but no model execution container may have network access. Calibration
and validation use separately built images and separately downloaded exact caches
whose inventories match but roots differ.

- [ ] **Step 4: Write RED lease, cross-phase, and failure-closure tests**

Require one atomic fixed-GPU active lease at a time, phase-specific lease IDs, exact audit/cache/image bindings, and no reclaim. Calibration release files must exist and rehash before validation lease creation. Reject same run ID, image ID/tag, root, cache, lease, container, receipt, checkpoint, timestamp, or audit identity across phases; reject different static/source/model/GPU identities.

Inject failure at every stage. Require `FileMode.CreateNew` diagnostics/results/manifests/closures, success destination preservation, best-effort lease release with explicit unreleased state if release fails, no second invocation, no cleanup, and exact `WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN` terminal.

- [ ] **Step 5: Prove RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Expected: failure because `scripts/run_wave0_a11.ps1` is absent.

- [ ] **Step 6: Implement the launcher with testable functions**

Use explicit functions rather than one monolithic body: `Resolve-A11Worktree`, `Test-A11ReadOnlyPreflight`, `New-A11PhaseIdentity`, `New-A11BuildArguments`, `Invoke-A11CachePreflight`, `New-A11Lease`, `Invoke-A11Replica`, `Invoke-A11Gate`, `Release-A11Lease`, `Close-A11Phase`, `Test-A11CrossPhaseIdentity`, and `Invoke-A11Campaign`.

The primitive used for every text audit must be a true no-clobber write:

```powershell
function Write-A11NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Encoding = [Text.UTF8Encoding]::new($false)
    $Stream = [IO.FileStream]::new(
        $Path, [IO.FileMode]::CreateNew,
        [IO.FileAccess]::Write, [IO.FileShare]::None
    )
    try {
        $Bytes = $Encoding.GetBytes($Text)
        $Stream.Write($Bytes, 0, $Bytes.Length)
        $Stream.Flush($true)
    } finally {
        $Stream.Dispose()
    }
}
```

All writes use `FileMode.CreateNew` or the repository's atomic no-clobber receipt publisher. Do not use `Test-Path` followed by replace/move as a publication primitive. Keep stdout/stderr/audit files even when empty. Hash every subprocess argv, exit, stdout, stderr, and produced file before consuming it.

- [ ] **Step 7: Run GREEN and retain the launcher uncommitted**

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
```

No Docker or GPU is used by these adapter tests. Keep staging empty and retain all
nine implementation paths as one uncommitted candidate for Task 6.

---

### Task 6: Verify, review, and freeze the A11 implementation candidate

**Files:**
- Stage and commit only the nine-file implementation allowlist after every gate and review passes
- Historical evidence: read-only

**Interfaces:**
- Consumes: Tasks 1–5 and the entry preservation baseline
- Produces: one clean reviewed final candidate SHA eligible for a separately authorized runtime attempt

- [ ] **Step 1: Run focused and complete CPU gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider
uvx --offline black --check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uvx --offline ruff check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
```

Parse `scripts/run_wave0_a11.ps1` under both `pwsh` and `powershell`; both parser error arrays must be empty.

- [ ] **Step 2: Verify exact uncommitted scope and conduct independent review**

Require the union of tracked working-tree changes and untracked candidate paths to
contain exactly the nine allowed paths, with staging still empty. Review Section
5.2.15 line-by-line and require Critical=0 and Important=0. Specifically verify
all 13 keys, both 66-pair inventories, exact/discrete gating before numerical
metrics, binary64 math, no floor, independent ceilings, receipt recomputation, no
success receipt on calibration failure, distinct/equal cross-phase identities,
phase-ordered lease release, no retry, no A3 mutation, and no Wave 1 capability.

- [ ] **Step 3: Rehash historical artifacts and images**

Recompute every Task 1 path/size/SHA-256 and inspect every image tag/ID/label. Require the unchanged 64,306-file and 21-image entry sets, all eight fixed A10 hashes, clean protected Git outside the candidate, no active lease, no running project container, no A11 campaign root, and unset `VAL_DATA_ROOT`. Do not exclude or repair drift.

- [ ] **Step 4: Address review findings in the uncommitted candidate and rerun all gates**

Critical or Important findings must be fixed only within the nine-file allowlist,
with focused RED/GREEN evidence and no commit yet. Repeat Steps 1–3 until
Critical=0 and Important=0. A required tenth tracked file stops for owner review.

- [ ] **Step 5: Create the single reviewed implementation commit and stop**

Stage exactly the nine allowed paths, verify the staged diff contains no other path,
and create one append-only commit without amend, rebase, squash, or history rewrite:

```powershell
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git add -- `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  schemas/statistical-replay-calibration-receipt.schema.json `
  schemas/statistical-replay-validation-receipt.schema.json `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  scripts/run_wave0_a11.ps1 `
  tests/gates/test_wave0_a11_launcher.py
git diff --cached --check
git commit -m 'feat: add A11 statistical replay gate'
```

Verify the commit is the direct child of this plan commit, its author and committer
are exactly `kuotunyu 61350295+kuotunyu@users.noreply.github.com`, its sole diff is
the nine-file allowlist, both worktrees are clean, and no runtime object exists.
Report the final source SHA, exact diff, test/lint/parser results, preservation
record/hash, and review verdict. Runtime still requires explicit owner authorization
tied to that exact source SHA and this plan commit.

---

### Task 7: Execute the calibration cohort once under a fresh lease

**Files:**
- Modify: none
- Runtime outputs: one fresh calibration run ID, image, campaign root, cache, lease/release, twelve replicas, threshold receipt, audits, preservation record, result, manifest, and closure

**Interfaces:**
- Consumes: clean owner-authorized final candidate and healthy local Docker/RTX 4090
- Produces: immutable calibration threshold receipt or immutable A11 failure terminal

- [ ] **Step 1: Perform the final no-write preflight**

Require exact branch/HEAD/spec/plan/owner authorization, clean worktrees, healthy `desktop-linux`, one RTX 4090 with the registered UUID, no numeric CUDA compute process, no project container, no active lease, unset `VAL_DATA_ROOT`, exact 64,306 historical files and 21 historical images, and every planned calibration/validation destination absent. A failed preflight creates no run ID.

- [ ] **Step 2: Invoke the checked-in launcher exactly once**

The execution session must set `$OwnerAuthorizationId` to the exact value in the later written runtime authorization; it must never infer or synthesize that value. Resolve the other identities from the reviewed clean checkout:

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a11-statistical-replay.md'
$ExpectedSourceCommit = (git rev-parse HEAD).Trim()
$ExpectedPlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
if ([string]::IsNullOrWhiteSpace($OwnerAuthorizationId)) {
    throw 'A11 runtime owner authorization is required'
}
pwsh -NoProfile -NonInteractive -File scripts/run_wave0_a11.ps1 `
  -ExpectedSourceCommit $ExpectedSourceCommit `
  -ExpectedSpecCommit 'b59b0d4407b98b460f6166ea7288ba6021dc7a78' `
  -ExpectedPlanCommit $ExpectedPlanCommit `
  -ExpectedBranch 'codex/wave0-model-contract' `
  -OwnerAuthorizationId $OwnerAuthorizationId
```

The launcher generates both never-used phase identities but creates and executes only calibration until its exact receipt is verified and its lease is released. Never invoke the launcher a second time.

- [ ] **Step 3: Validate the calibration closure**

Require exactly twelve schema-v3 PASS feasibility receipts/checkpoints, 66 exact-compatible pairs, thirteen complete metric inventories, finite metrics, recomputed maxima/thresholds, thresholds at or below practical ceilings, exact decimal/hex constants, atomic calibration receipt, unchanged history, released lease, and terminal `WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`.

Any calibration, Docker, GPU, lease, receipt, checkpoint, threshold, preservation, or closure failure preserves all new objects, prohibits validation, and stops without retry or candidate modification.

---

### Task 8: Execute independent validation and stop at the Wave 1 owner boundary

**Files:**
- Modify: none
- Runtime outputs: one fresh validation image, campaign root, cache, lease/release, twelve replicas, validation aggregate, audits, preservation record, result, manifest, and closure

**Interfaces:**
- Consumes: the same single launcher invocation and the verified immutable calibration receipt
- Produces: one immutable A11 PASS or normative-failure terminal

- [ ] **Step 1: Verify the phase boundary before validation model initialization**

Require calibration receipt path/size/SHA-256/run identity, calibration result/manifest/closure hashes, calibration lease release evidence, no active lease/container, unchanged source/specification/plan/base/model/GPU semantic identities, and all required validation runtime identities distinct. Rehash the pre-A11 baseline plus the complete calibration additions. A mismatch stops before validation root creation or model initialization.

- [ ] **Step 2: Run twelve validation processes and the frozen-threshold gate**

Build the separately labeled validation image, create and verify a separately downloaded exact cache, acquire the new lease, run `validation-00..11` as twelve fresh Docker processes, and invoke the validation CLI with the calibration threshold receipt mounted read-only. Do not override, recompute, widen, floor, or update thresholds.

- [ ] **Step 3: Close and classify the immutable result**

Require 66 exact-compatible validation pairs, all thirteen raw metrics finite, exact min/median/max summaries, every value at or below both frozen threshold and independent ceiling, exact calibration binding, complete history preservation, released lease, and clean Git.

If every gate passes, the sole terminal is:

```text
WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED
```

Otherwise preserve all evidence and stop at:

```text
WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

Report source/specification/plan/image/run identities, all receipt/checkpoint/result/manifest/closure/release hashes, GPU/driver/CUDA/VRAM/timing observations, calibration thresholds, validation summaries, historical-preservation result, Docker/container/lease state, Git status, and explicit Wave 1 prohibition. Do not access RDD or begin Wave 1 even after PASS.
