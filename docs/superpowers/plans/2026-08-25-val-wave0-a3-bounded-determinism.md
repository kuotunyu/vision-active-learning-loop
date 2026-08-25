# Wave 0 A3 Bounded CUDA Determinism Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the structurally impossible bitwise CUDA-backward requirement with the owner-authorized, fail-closed A3 bounded exception; prove exact replay of discrete state and fixed same-host numerical replay bounds; then execute one fresh Wave 0 campaign without changing the research model or entering Wave 1.

**Architecture:** Keep deterministic error mode everywhere except the dynamic extent of `loss.backward()`. That extent captures every warning, accepts exactly nine normalized `grid_sampler_2d_backward_cuda` warnings after verifying the pinned PyTorch and Transformers source hashes, and restores error mode in `finally`. Each feasibility receipt records an exact pre-update/discrete replay identity plus per-group update norms. A focused numerical replay module loads all six verified post-step checkpoints, compares the five non-canonical observations to primary A, requires exact structure and discrete state, and applies the preregistered float64 gradient/update/AdamW bounds. The aggregate gate publishes the structured exact and numerical comparisons in schema-version-2 evidence.

**Tech Stack:** Python 3.12.11; uv 0.8.15; SciPy 1.18.0; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; pycocotools 2.0.10; pytest; JSON Schema; Black 22.6.0; Ruff 0.16.4; CUDA 12.6; RTX 4090 24 GB; WSL2 Ubuntu 24.04; Docker Desktop Linux engine.

## Scope lock and immutable baseline

- The implementation starts from the clean `codex/wave0-model-contract` worktree whose HEAD contains both A3 spec commits: `cf6dbca376341c9dfb41177bc5c851ca6434680e` and `0721096ba4ecf9d44f7f0a2b27935f14cc8faf54`. Verify the registered worktree path, branch, HEAD, Git common directory, clean linked worktree, clean canonical main, and approved Git identity before modifying a file.
- Preserve RT-DETR-R18 revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d`, the processor, 300 queries, four RDD classes, full detector/backbone optimization, BF16, seed 17, dependency versions, datasets, acquisition arms, formal seeds, budgets, nine pilot fits, 66 primary fits, and six label-noise fits.
- Do not freeze transformer layers, move backward to CPU, change kernels, change model or package pins, alter thresholds after a GPU observation, or weaken loss, gradient, update, VRAM, checkpoint, parent-binding, no-clobber, or path-boundary checks.
- Preserve every older campaign, image, checkpoint, receipt, log, failure record, and audit byte-for-byte. In particular, `wave0-a2-20260825T025943120Z` remains `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN` with the three hashes recorded in specification Section 5.2.5.
- A3 runtime outputs use a fresh run ID, fresh OCI image, fresh campaign/attempt/checkpoint roots, and atomic no-clobber publication. Existing roots or destinations stop the run; they are never cleaned or reused.
- `VAL_DATA_ROOT` remains unset. No RDD file, annotation, path, archive, metadata dump, mount, or download is accessed. Wave 1 and all remote, push, PR, merge, tag, Release, and GitHub operations remain outside this plan.
- Whole-tree formatting debt is out of scope. Only touched Python files receive targeted Black and Ruff checks. No unrelated refactor or mass formatting is allowed.
- Schema version 1 feasibility and Wave 0 gate receipts remain valid historical evidence only. They cannot satisfy A3 and are never rewritten.

## A3 file map

| Area | Exact files | Action |
|---|---|---|
| Bounded backward and feasibility v2 | `src/vision_active_learning_loop/probes/training_feasibility.py`; `tests/probes/test_training_feasibility.py`; `schemas/feasibility-receipt.schema.json` | Modify |
| Receipt-version dispatch and semantic validation | `src/vision_active_learning_loop/artifacts/receipts.py`; `tests/artifacts/test_receipts.py` | Modify |
| Replay comparison | `src/vision_active_learning_loop/gates/numerical_replay.py`; `tests/gates/test_numerical_replay.py` | Create |
| Aggregate gate v2 | `src/vision_active_learning_loop/gates/wave0.py`; `tests/gates/test_wave0_gate.py`; `schemas/wave0-gate-receipt.schema.json` | Modify |

No other tracked file is expected. The central receipt validator is required because it owns the allowlisted `(receipt_type, schema_version)` dispatch and semantic consistency checks; editing only a JSON Schema would leave both A3 receipt types unpublishable. If implementation requires another tracked file, stop, explain the necessity, and amend this plan/spec before expanding scope.

---

### Task 1: Enforce the exact bounded-backward warning contract

**Objective:** Permit only the pinned RT-DETR deformable-attention CUDA backward warnings, only during backward, while preserving strict deterministic error mode before and after the call.

**Files:**
- Modify: `tests/probes/test_training_feasibility.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class BackwardWarningEvidence:
    operation_identifier: str
    expected_count: int
    observed_count: int
    raw_warnings: tuple[str, ...]
    warning_categories: tuple[str, ...]
    operation_identifiers: tuple[str, ...]
    source_sha256: Mapping[str, str]

def run_allowlisted_backward(
    backward: Callable[[], None], *, expected_count: int
) -> BackwardWarningEvidence: ...
```

The normative constants are:

```text
operation_identifier = grid_sampler_2d_backward_cuda
expected_count = config.decoder_layers * config.num_feature_levels = 3 * 3 = 9
Transformers modeling_rt_detr.py = fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3
PyTorch torch/__init__.py = b508de5a66ebc368fc8fa2161b1e0e88ae0034d9d9540e7c020460237a5464a9
PyTorch torch/nn/functional.py = e409a97896241e0dfb8c23fbf1f09967ecf5e65ec9626aec0d97d9cc5d727d50
```

- [ ] **Step 1: Write RED unit tests for the warning boundary**

Use CPU callbacks that emit realistic `UserWarning` messages so the contract can be tested without a model or GPU. Tests must prove:

1. strict deterministic error mode is required on entry;
2. the callback observes deterministic algorithms enabled in warning mode;
3. exactly nine parseable `grid_sampler_2d_backward_cuda` warnings pass;
4. zero, eight, ten, a different operation, mixed operations, an unparsable warning, or an unexpected category fails;
5. every warning is a `UserWarning`, and raw message order and category names are preserved;
6. strict error mode is restored after success and after a callback exception; and
7. any pinned source hash mismatch fails before invoking the callback.

Run:

```powershell
uv run pytest tests/probes/test_training_feasibility.py -v -k "allowlisted_backward or warning_boundary or source_hash"
```

Expected RED: the helper/evidence type does not exist and the current implementation rejects every deterministic warning globally.

- [ ] **Step 2: Implement the smallest fail-closed boundary**

Locate the installed source files from imported objects, resolve them to regular non-link files, and hash them before changing deterministic mode. Enter `warnings.catch_warnings(record=True)` with `warnings.simplefilter("always")`, keep deterministic algorithms enabled with warning behavior only while calling the supplied backward callback, and restore `warn_only=False` plus debug mode `error` in `finally`. Normalize only messages whose leading operation identifier matches the pinned PyTorch deterministic warning form. Do not accept substring-only matches or wildcard operation names.

In `run_one_step_smoke()`, derive the expected count from the loaded model config, require the pinned values `decoder_layers == 3` and `num_feature_levels == 3`, and replace only the direct `loss.backward()` call with the helper. Forward, clipping, optimizer/scheduler steps, checkpointing, and all other work remain in strict mode. Remove the old broad `deterministic_fallback_detected` heuristic.

- [ ] **Step 3: Run the bounded-backward GREEN tests**

```powershell
uv run pytest tests/probes/test_training_feasibility.py -v -k "determin or allowlisted or fallback or source_hash"
```

Expected GREEN: the exact exception passes; every other warning path fails; strict restoration is observable.

**Stop condition:** Any extra/unparsable warning, source-hash drift, wrong config-derived count, failure to restore strict mode, or need to widen the exception ends implementation before a GPU run.

---

### Task 2: Publish complete feasibility-v2 replay evidence

**Objective:** Replace the old bitwise comparison preimage with an exact A3 identity and record sufficient per-group data for independent numerical replay checks.

**Files:**
- Modify: `tests/probes/test_training_feasibility.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`
- Modify: `schemas/feasibility-receipt.schema.json`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Modify: `tests/artifacts/test_receipts.py`

**Receipt contract:** `schema_version == 2`; retain all applicable A2 evidence; require `allowlisted_backward`, ordered `parameter_inventory`, `update_groups`, and `exact_comparison`; prohibit the old `deterministic_fallback_absent` interpretation.

- [ ] **Step 1: Write RED tests for parameter/update evidence**

Build tiny CPU modules with detector and `model.backbone` parameters. Tests must prove:

- `build_optimizer()` emits exactly two named groups, `detector` then `backbone`, at the existing learning rates and weight decay;
- the inventory contains each trainable parameter exactly once in `model.named_parameters()` order with `name`, `group_name`, shape, and dtype;
- per-group update L2 norms are accumulated in canonical name order on CPU float64;
- a missing, duplicate, reordered, non-finite, wrong-shape, or zero group update fails;
- timing/allocator fields are excluded from `exact_comparison`, while pre-update digest, inventory, loss hex, synthetic input/target/item/sampler digests, scheduler-before digest, post-step RNG digest, warning evidence, recipe/group semantics, and model/checkpoint structure identity are included; and
- changing any included field changes the exact comparison hash.

- [ ] **Step 2: Capture the pre/post update evidence**

Before forward, snapshot every trainable parameter to CPU without altering model/device state, build the ordered inventory, and digest the pre-update scheduler state. After `optimizer.step()`, calculate detector/backbone update norms from `post - pre` in float64. Keep the existing full post-step checkpoint and within-run content/digest round-trip checks unchanged.

Extend `StepObservation` with structured warning evidence, parameter inventory, update-group norms, and exact-comparison inputs. Keep post-update model/optimizer digests as per-run content identities, but do not put them into the cross-run exact hash.

- [ ] **Step 3: Migrate the feasibility schema and validation tests to v2**

Register `("feasibility", 2)` and, in preparation for Task 4, `("wave0-gate", 2)` as the only current schema versions for those receipt types. Version 1 remains rejected by current A3 code rather than being remapped to the v2 schema. Dispatch semantic validation by the receipt's explicit version so the new field inventory is checked directly and the historical validator cannot silently reinterpret it.

The schema must enumerate every allowed property with `additionalProperties: false`. Define reusable strict objects for:

- one warning occurrence and the aggregate allowlisted-backward evidence;
- one ordered parameter inventory row;
- exactly the `detector` and `backbone` update groups with finite positive L2 norms;
- the exact-comparison preimage and its canonical SHA-256.

Require `allowlisted_grid_sample_backward == true`, exact count 9, the exact operation identifier and source hashes, deterministic algorithms enabled, strict mode restored, and every retained feasibility invariant. Version-1 or hybrid v1/v2 documents must fail validation.

Add adversarial tests for missing/extra/renamed warning fields, changed source hashes, wrong counts, unordered/duplicate inventory, missing groups, NaN/Inf serialized attempts, contradicted invariant booleans, and a rehashed but semantically inconsistent comparison.

- [ ] **Step 4: Run Task 2 GREEN verification**

```powershell
uv run pytest tests/probes/test_training_feasibility.py -v
uv run pytest tests/artifacts/test_receipts.py -v -k "feasibility or schema"
```

Expected GREEN: CPU tests validate a complete v2 receipt without invoking CUDA or loading a model.

**Stop condition:** If the receipt cannot independently identify the exception and update groups, if the old bitwise post-update digest remains normative across runs, or if schema version 1 can satisfy A3, stop before Task 3.

---

### Task 3: Implement the checkpoint numerical replay comparator

**Objective:** Compare five non-canonical post-step observations against primary A using exact structural/discrete checks and the fixed A3 numerical thresholds.

**Files:**
- Create: `tests/gates/test_numerical_replay.py`
- Create: `src/vision_active_learning_loop/gates/numerical_replay.py`

**Interfaces:**

```python
GRADIENT_REL_TOL = 1e-5
GRADIENT_ABS_TOL = 1e-7
VECTOR_REL_L2_LIMIT = 1e-3
VECTOR_COSINE_MINIMUM = 0.99999

@dataclass(frozen=True)
class ReplayComparison:
    exact: Mapping[str, object]
    numerical: Mapping[str, object]
    errors: tuple[str, ...]

def compare_replay(
    canonical_receipt: Mapping[str, object],
    canonical_state: CheckpointState,
    replay_receipt: Mapping[str, object],
    replay_state: CheckpointState,
) -> ReplayComparison: ...
```

- [ ] **Step 1: Write RED hand-calculated comparator tests**

Use tiny in-memory `CheckpointState` objects and v2 receipt fragments. Cover:

- an exact/numerically equal replay;
- gradient norm at both accepted boundaries and just outside them;
- detector/backbone update vectors that pass and fail relative-L2 and cosine independently;
- AdamW `exp_avg` and `exp_avg_sq` comparisons for both groups;
- exact key order, name-to-state mapping, shapes, dtypes, integer/bool tensors, non-training buffers, scheduler, scaler, RNG, sampler, epoch, step, and input digests;
- zero, NaN, Inf, missing/extra/reordered state, missing optimizer moments, duplicate parameter IDs, unknown group names, and inconsistent recorded update norms.

Calculate expected scalar examples in tests instead of copying production helper output.

```powershell
uv run pytest tests/gates/test_numerical_replay.py -v
```

Expected RED: the module is absent.

- [ ] **Step 2: Implement canonical float64 accumulation**

Walk the receipt inventory in its recorded name order. Reconstruct each optimizer parameter-ID-to-name mapping from the named `detector` and `backbone` checkpoint groups, rejecting any ambiguity. Compare non-floating/discrete tensors exactly. For each floating trainable group, obtain `||delta||` from the independently recorded per-run update norm and obtain `||delta_replay - delta_primary||` from the two exact post-step checkpoint tensors because the pre-update parameter digest is exact. Derive cosine from the two norms and the difference norm, clamping only roundoff within the mathematical `[-1, 1]` interval; do not hide an invalid vector.

For `exp_avg` and `exp_avg_sq`, concatenate checkpoint tensors in group/name order and directly compute both norms, the pairwise difference, relative L2, and cosine. All reductions occur on CPU float64. Return every measured value, threshold, boolean, and error in deterministic key order.

- [ ] **Step 3: Run Task 3 GREEN verification**

```powershell
uv run pytest tests/gates/test_numerical_replay.py -v
uv run --with black==22.6.0 black --check src/vision_active_learning_loop/gates/numerical_replay.py tests/gates/test_numerical_replay.py
uv run --with ruff==0.16.4 ruff check src/vision_active_learning_loop/gates/numerical_replay.py tests/gates/test_numerical_replay.py
```

Expected GREEN: all pass/fail boundaries are covered without CUDA.

**Stop condition:** Any comparison depends on unordered dictionary iteration, CUDA reductions, a receipt-provided PASS flag, threshold tuning, or silently skipped state.

---

### Task 4: Integrate A3 comparison into the Wave 0 aggregate gate

**Objective:** Make the aggregate gate load and verify all six checkpoints, compare primary B and both A/B observations from clean-a/clean-b to primary A, and publish schema-valid structured v2 evidence.

**Files:**
- Modify: `tests/gates/test_wave0_gate.py`
- Modify: `src/vision_active_learning_loop/gates/wave0.py`
- Modify: `schemas/wave0-gate-receipt.schema.json`

- [ ] **Step 1: Upgrade test attempt fixtures and write RED integration tests**

`ReplayReceiptPaths` gains `checkpoint_a` and `checkpoint_b` at the existing canonical attempt paths:

```text
wave0/checkpoints/feasibility-a/step-000001.pt
wave0/checkpoints/feasibility-b/step-000001.pt
```

Test helpers publish real tiny checkpoints with `save_checkpoint_atomic()`, bind each feasibility receipt to its own file and state hashes, and keep every output path unique. Add tests proving:

- a complete v2 primary/clean-a/clean-b chain passes with exactly five comparisons;
- a missing, corrupt, pre-existing-substitution, wrong-hash, or wrong-input checkpoint fails before numerical comparison;
- version-1 feasibility evidence is rejected as historical;
- exact receipt, structure, discrete state, warning, or pre-update divergence fails the exact invariant;
- each gradient, update-vector, and optimizer-state threshold fails independently;
- primary A is always the canonical observation and no pair is omitted; and
- paths, run IDs, source/image identities, parent bindings, no-data-root, four-class/labeled-loss, BF16, finite-gradient, update, VRAM, and within-run checkpoint gates remain mandatory.

- [ ] **Step 2: Load verified checkpoints and evaluate five comparisons**

Extend `_load_attempt()` so `load_checkpoint_verified()` receives the receipt-declared checkpoint SHA-256 and input digests. Store verified states alongside documents and stored hashes. Build these stable comparison keys:

```text
primary_b
clean_a_a
clean_a_b
clean_b_a
clean_b_b
```

For each key call `compare_replay(primary.feasibility_a, primary.checkpoint_a, ...)`. Do not compare parent receipt storage hashes, checkpoint file hashes, paths, timestamps, durations, or container attempt IDs across independent attempts.

- [ ] **Step 3: Publish the Wave 0 gate v2 contract**

Replace the old `deterministic_comparisons` payload with required `exact_comparisons` and `numerical_replay_comparisons`. Require separate invariants:

```text
allowlisted_backward_verified
feasibility_ab_exact_fields_match
clean_replays_exact_fields_match
numerical_replays_within_bounds
```

Retain every unrelated A2 invariant. The terminal interpretation becomes exactly:

```text
PASS: WAVE0_A3_PASS / WAVE1_NOT_STARTED
FAIL: WAVE0_A3_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

The gate schema uses `schema_version == 2`, enumerates all five comparison keys, requires the registered thresholds as constants, forbids extra properties, and rejects version-1/hybrid documents. Receipt status and invariant booleans must be recomputed from evidence, never trusted from child status alone.

- [ ] **Step 4: Run Task 4 GREEN verification**

```powershell
uv run pytest tests/gates/test_numerical_replay.py tests/gates/test_wave0_gate.py -v
uv run pytest tests/training/test_checkpoint_io.py tests/probes/test_training_feasibility.py tests/gates/test_wave0_gate.py -v
```

Expected GREEN: the complete CPU fixture chain passes and every corrupted comparison fails closed.

**Stop condition:** Any checkpoint is deserialized before its file hash is verified, any of six observations is missing, any of five comparisons is omitted, version-1 evidence passes, or a floating tolerance is applied to a field registered as exact.

---

### Task 5: Full verification, independent review, and append-only implementation commit

**Objective:** Prove the complete source/schema change is internally consistent and does not alter historical evidence before building an image.

- [ ] **Step 1: Run all focused and full CPU gates**

```powershell
uv run pytest tests/probes/test_training_feasibility.py tests/gates/test_numerical_replay.py tests/gates/test_wave0_gate.py tests/training/test_checkpoint_io.py -v
uv run pytest
uv lock --check
```

Expected: zero failures; only already-registered capability skips are allowed.

- [ ] **Step 2: Format/lint only touched Python files and validate diffs**

```powershell
uv run --with black==22.6.0 black --check src/vision_active_learning_loop/probes/training_feasibility.py src/vision_active_learning_loop/gates/numerical_replay.py src/vision_active_learning_loop/gates/wave0.py tests/probes/test_training_feasibility.py tests/gates/test_numerical_replay.py tests/gates/test_wave0_gate.py
uv run --with ruff==0.16.4 ruff check src/vision_active_learning_loop/probes/training_feasibility.py src/vision_active_learning_loop/gates/numerical_replay.py src/vision_active_learning_loop/gates/wave0.py tests/probes/test_training_feasibility.py tests/gates/test_numerical_replay.py tests/gates/test_wave0_gate.py
git diff --check
```

- [ ] **Step 3: Perform an independent second-pass review**

Review the complete staged diff from a clean context against specification Section 5.2.5 and this plan. Record Critical, Important, and Minor findings. Critical and Important must both be zero before commit. Re-run affected tests after any correction. Explicitly review warning parsing, strict-mode restoration, source hashes, six-checkpoint coverage, exact-versus-numerical field separation, denominator/cosine math, NaN/zero handling, schema closure, no-clobber behavior, and version-1 rejection.

- [ ] **Step 4: Verify immutable evidence and file scope**

Hash every pre-existing campaign/evidence file from the preserved baseline inventory and compare it with the pre-change values. Verify `git diff --name-only` contains only the ten A3 files in this plan and that `uv.lock`, pinned-model config, Dockerfiles, specs, older plans, scripts, historical evidence, and all model/data identities are unchanged.

- [ ] **Step 5: Create one append-only implementation commit**

Stage only the ten A3 implementation files. Use exact author and committer identity `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` and do not amend, rebase, squash, or rewrite history.

```powershell
git commit -m "fix: bound Wave 0 CUDA replay"
```

After commit, repeat focused tests, `git diff --check`, author/committer verification, and clean-worktree checks. The resulting SHA is the sole A3 source candidate.

**Stop condition:** Any failure, unexpected file, unresolved Critical/Important review finding, evidence hash drift, dirty canonical main, or identity mismatch stops before Docker build.

---

### Task 6: Execute one fresh Wave 0 A3 campaign

**Objective:** Produce one complete, source/image/run-bound A3 evidence chain on the canonical RTX 4090 and stop before Wave 1.

- [ ] **Step 1: Revalidate the execution boundary**

Without redoing Tasks 1–5, verify the registered worktree/branch/candidate SHA and clean states; Docker context `desktop-linux`; Linux Server health; RTX 4090 visibility; exact historical Option A image identity; `VAL_DATA_ROOT` unset; no active project GPU lease; and unchanged historical evidence hashes. A failed preflight makes no project mutation.

- [ ] **Step 2: Create fresh identities with no-clobber roots**

Generate one never-used UTC run ID, create a fresh source-SHA-bound OCI image, inspect its immutable image ID/digest/labels, and atomically acquire the project GPU lease. Confirm the campaign root, all attempt roots, every receipt destination, and every checkpoint root do not exist before their trusted creator creates them.

- [ ] **Step 3: Execute primary, clean-a, and clean-b once**

Run the approved Wave 0 runner in order. Each attempt publishes environment, model-assets, model-contract, feasibility-A, and feasibility-B evidence plus both checkpoints. Confirm exactly nine allowlisted warnings in every feasibility receipt; finite scalar labeled loss; BF16 backward; finite gradients; parameter update; peak allocated VRAM at most 22 GiB; and exact within-run checkpoint round trips.

Do not retry a failed stage under the same source or run ID. Preserve the failure record and stop.

- [ ] **Step 4: Run the aggregate A3 gate**

Load the six verified checkpoints, produce all five exact/numerical comparisons, and atomically publish the Wave 0 gate receipt. Validate the stored receipt against `schemas/wave0-gate-receipt.schema.json`, recompute its content hash, and require every invariant true with terminal interpretation:

```text
WAVE0_A3_PASS / WAVE1_NOT_STARTED
```

- [ ] **Step 5: Close and report**

Release the GPU lease in all outcomes. Re-hash all older campaigns/evidence, verify the linked worktree and canonical main remain clean at the candidate SHA, and report source/image/run identities, GPU environment, six feasibility receipt/checkpoint hashes, warning counts, loss/gradient/VRAM/update metrics, five exact and numerical comparisons, aggregate receipt hash/verdict, historical preservation, and Git status.

**Success endpoint:** `WAVE0_A3_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`

**Failure endpoint:** `WAVE0_A3_NORMATIVE_FAIL / WAVE1_FORBIDDEN`

Wave 1 does not begin under this plan even after success.

## Plan self-review record

- [x] No unresolved marker, optional gate, or unregistered threshold remains.
- [x] Exact module paths, schema versions, source hashes, warning identifier/count/category, comparison pairs, thresholds, commands, file scope, and terminal interpretations are explicit.
- [x] The plan distinguishes exact discrete replay from bounded post-backward floating replay without calling the latter deterministic or bitwise identical.
- [x] Error-mode restoration, warning parsing, source verification, checkpoint verification-before-load, NaN/zero handling, atomic no-clobber, and historical evidence preservation fail closed.
- [x] No model, dependency, dataset, seed, budget, acquisition arm, fit count, research claim, RDD access, Wave 1 work, or external Git operation is introduced.
