# Wave 5 Embargoed Formal Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce exactly 66 primary detector fits and all acquisition/training/calibration artifacts under a technical source-test/shift embargo, then issue the sole completion seal that can authorize evaluation.

**Architecture:** A frozen job DAG expands three seeds into shared 2%, five-arm 5/10/20/40%, and shared acquired-budget-ceiling fits. A host GPU lease serializes canonical jobs; each job publishes atomically and resumes only from identical manifests. A completeness service operating without evaluator mounts validates every hash and emits `formal_completion_seal`.

**Tech Stack:** Frozen Waves 0–4 OCI/runtime/protocol; RTX 4090 exclusive lease; external manifests/checkpoints; append-only job journal; pytest; no evaluator package in trainer image.

## Global Constraints

- Entry requires owner approval and a valid Wave 4 protocol-freeze receipt.
- Seeds are exactly 17, 29, 43. Arms and budgets are unchanged.
- Per seed: 1 shared 2% fit + 5 arms×4 later fits + 1 shared 100% acquired-budget ceiling =22; total=66.
- Every budget fit initializes from the same pinned pretrained base; previous model selects only.
- Formal trainer/strategy images cannot contain evaluator code or mount source-test/China Drone paths.
- No source-test/shift prediction, score, metric, thumbnail, or log may be produced before the completion seal.
- A protocol/hash/mount/selection/fit mismatch invalidates the experiment ID; it is never repaired in place.

---

### Task 1: Expand and verify the frozen 66-fit formal DAG

**Objective:** Generate the complete immutable formal job matrix with exact dependencies and no evaluator capability.

**Files:**
- Create: `src/vision_active_learning_loop/formal/matrix.py`
- Create: `configs/experiments/formal-v1.yaml`
- Create: `schemas/formal-job.schema.json`
- Create: `schemas/formal-matrix.schema.json`
- Create: `tests/formal/test_matrix.py`
- Create: `tests/formal/test_dependencies.py`

**Interfaces:**
- Produces: `build_formal_matrix(freeze_receipt) -> FormalMatrix`
- Produces: `FormalJob(job_id, seed, arm, budget, kind, parents, manifest_digest, required_capabilities)`
- CLI: `val formal plan --freeze <receipt> --output <matrix>`

- [ ] **Step 1: Write failing exact-accounting tests**

```python
def test_formal_matrix_counts(matrix):
    assert len(matrix.fit_jobs) == 66
    assert count_kind(matrix, "shared_2pct") == 3
    assert count_kind(matrix, "arm_later") == 60
    assert count_kind(matrix, "acquired_budget_ceiling") == 3

def test_formal_seeds_and_arms_are_exact(matrix):
    assert matrix.seeds == (17, 29, 43)
    assert set(matrix.arms) == {"random", "entropy", "margin", "core_set", "hybrid_uncertainty_diversity"}
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/formal/test_matrix.py tests/formal/test_dependencies.py -v`

Expected: missing formal matrix modules.

- [ ] **Step 3: Implement per-seed dependency expansion**

Shared 2% checkpoint feeds first selection for all arms; arm round `p` selection depends on that arm’s previous-round checkpoint/ledger; each later fit starts from pinned base and its cumulative acquired ledger. Ceiling fit depends only on all-pool acquired/calibration manifest for its seed and is shared across arms. Job IDs hash every frozen input.

- [ ] **Step 4: Reject evaluator capabilities in jobs**

Formal job schema allows public pool, acquired labels, relevant checkpoint/embedding, job output, and trusted oracle capability for reveal phase. It rejects evaluator roots/modules/result tokens and source/shift role IDs.

- [ ] **Step 5: Generate matrix and verify graph**

Run: `uv run val formal plan --freeze "$VAL_ARTIFACT_ROOT/pilot/protocol-freeze-receipt.json" --output "$VAL_ARTIFACT_ROOT/formal/<experiment_id>/formal-matrix.json" && uv run pytest tests/formal/test_matrix.py tests/formal/test_dependencies.py -v`

Expected: exactly 66 acyclic fit nodes, correct acquisition edges, no extra seed/arm/budget, no evaluator capability.

**Artifact/evidence produced:** frozen formal matrix/DAG and accounting tests.

**Stop condition:** Count/dependency/capability differs or freeze digest is invalid.

**Commit boundary:** `feat: define frozen formal job matrix`

---

### Task 2: Implement the exclusive RTX lease and formal job journal

**Objective:** Serialize canonical GPU work, detect stale owners safely, and persist crash-safe job state without overlapping fits.

**Files:**
- Create: `src/vision_active_learning_loop/execution/gpu_lease.py`
- Create: `src/vision_active_learning_loop/execution/job_journal.py`
- Create: `schemas/gpu-lease.schema.json`
- Create: `schemas/job-event.schema.json`
- Create: `tests/execution/test_gpu_lease.py`
- Create: `tests/execution/test_job_journal.py`

**Interfaces:**
- Produces: `GpuLease.acquire(gpu_uuid, job_id, ttl_seconds) -> LeaseHandle`
- Produces: `LeaseHandle.heartbeat()`, `LeaseHandle.release()`
- Produces: `JobJournal.compare_and_append(job_id, expected_state, event) -> JobState`

- [ ] **Step 1: Write failing contention/stale/replay tests**

```python
def test_second_job_cannot_acquire_live_gpu_lease(lease_store):
    first = lease_store.acquire(GPU_UUID, "job-a", 60)
    with pytest.raises(GpuBusy):
        lease_store.acquire(GPU_UUID, "job-b", 60)

def test_stale_lease_requires_absent_process_and_audit(lease_store, stale):
    assert lease_store.reclaim(stale).audit_event.reason == "owner_absent_and_expired"
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/execution/test_gpu_lease.py tests/execution/test_job_journal.py -v`

Expected: missing execution modules.

- [ ] **Step 3: Implement atomic lease/journal semantics**

Lease records GPU UUID, host/container/process ID, experiment/job, acquisition/heartbeat/expiry. Use OS-atomic create and compare-and-swap updates. Reclaim only after expiry plus absent host process/container. Journal transitions `planned→ready→running→checkpointed→validated→published` or `failed/invalidated`; events are append-only and hash-chained.

- [ ] **Step 4: Test crash and double-publish protection**

Run: `uv run pytest tests/execution/test_gpu_lease.py tests/execution/test_job_journal.py -v`

Expected: concurrent ownership, early reclaim, state skip, duplicate publish, and altered event chain fail; valid crash recovery writes an audit event.

**Artifact/evidence produced:** GPU lease/journal schemas and concurrency/recovery tests.

**Stop condition:** Two canonical jobs can overlap, stale reclaim lacks proof, or event history can be rewritten.

**Commit boundary:** `feat: add canonical gpu job lease`

---

### Task 3: Run formal acquisition and training under technical embargo

**Objective:** Execute every ready DAG node with exact receipts while making evaluator access technically impossible.

**Files:**
- Create: `src/vision_active_learning_loop/formal/runner.py`
- Create: `src/vision_active_learning_loop/formal/embargo.py`
- Create: `docker/formal-runner.Dockerfile`
- Create: `tests/formal/test_runner.py`
- Create: `tests/formal/test_embargo.py`
- Create: `docs/runbooks/formal-execution.md`

**Interfaces:**
- Produces: `FormalRunner.run_ready(matrix, gpu_lease) -> Sequence[JobReceipt]`
- Produces: `EmbargoPolicy.validate_image(image_manifest, mounts, imports) -> None`
- CLI: `val formal run --matrix <json> --experiment-root <external-path>`

- [ ] **Step 1: Write failing embargo/fresh-base/resume tests**

```python
def test_formal_image_has_no_evaluator_package_or_mount(policy, image):
    assert policy.scan(image).forbidden_entries == []

def test_later_fit_uses_pinned_base(runner, later_job):
    receipt = runner.prepare(later_job)
    assert receipt.initial_checkpoint_digest == later_job.pretrained_base_digest
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/formal/test_runner.py tests/formal/test_embargo.py -v`

Expected: missing runner/embargo modules.

- [ ] **Step 3: Build trainer-only image and embargo checks**

Use a separate image target that excludes `evaluation/`, source/shift schemas, pycocotools evaluator entrypoints, and result readers. Mount policy denies sealed evaluator roots and network. Before every job, scan image/import graph/mounts/environment/config/log destinations.

- [ ] **Step 4: Execute the frozen DAG**

Run: `uv run val formal run --matrix "$VAL_ARTIFACT_ROOT/formal/<experiment_id>/formal-matrix.json" --experiment-root "$VAL_ARTIFACT_ROOT/formal/<experiment_id>"`

Expected: jobs run when parents ready, acquire one RTX lease, select/reveal/train/calibrate through approved paths, publish atomic receipts, and stop/resume from identical checkpoints. No evaluator output exists.

- [ ] **Step 5: Audit every completed job continuously**

Run: `uv run val formal audit --experiment-root "$VAL_ARTIFACT_ROOT/formal/<experiment_id>" --mode embargoed --output <audit.json>`

Expected: completed count rises toward 66; each receipt matches freeze/job/ledger/config/environment; source/shift file/process/log scan remains empty. Any violation invalidates the experiment ID immediately.

**Artifact/evidence produced:** 66 candidate checkpoint/training/calibration/acquisition receipts, formal journal, embargo scans.

**Stop condition:** Evaluator capability/output appears, recipe/input/selection mismatch, non-finite/deterministic failure, or artifact cannot validate. Do not continue the same experiment ID after contamination.

**Commit boundary:** `feat: run formal jobs under embargo`

---

### Task 4: Verify exact artifact completeness and resume/idempotence

**Objective:** Prove that all 66 jobs and every dependent ledger/manifest/hash are present, unique, nested, valid, and immutable before sealing.

**Files:**
- Create: `src/vision_active_learning_loop/formal/completeness.py`
- Create: `schemas/formal-completeness.schema.json`
- Create: `tests/formal/test_completeness.py`
- Create: `tests/formal/test_artifact_inventory.py`

**Interfaces:**
- Produces: `build_formal_inventory(matrix, experiment_root) -> FormalInventory`
- Produces: `validate_formal_inventory(inventory, freeze_receipt) -> CompletenessReceipt`

- [ ] **Step 1: Write failing missing/duplicate/nesting tests**

```python
def test_missing_one_checkpoint_fails(inventory):
    inventory.checkpoints.pop()
    assert validate_formal_inventory(inventory).status == "FAIL"

def test_arm_ledgers_are_nested(inventory):
    assert all(previous_ids(r) <= current_ids(r) for r in inventory.arm_rounds)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/formal/test_completeness.py tests/formal/test_artifact_inventory.py -v`

Expected: missing completeness modules.

- [ ] **Step 3: Implement exhaustive inventory checks**

Require 66 unique checkpoint/training manifests/receipts, three shared 2%, 60 arm-later, three ceilings, every acquisition/queue/cost/calibration event, exact budgets/nesting, base initialization, ordered-item/RNG/resume hashes, schema/protocol/environment/model/dataset/freeze parents, and clean atomic files. Rehash bytes rather than trusting filenames.

- [ ] **Step 4: Build and validate inventory**

Run: `uv run val formal inventory --matrix <formal-matrix.json> --experiment-root <root> --output <formal-inventory.json> && uv run pytest tests/formal/test_completeness.py tests/formal/test_artifact_inventory.py -v`

Expected: exactly 66 validated fit rows and all dependent artifacts; injected deletion/substitution/duplicate/mutation/nonnested set fails.

**Artifact/evidence produced:** complete content-hash inventory and completeness receipt.

**Stop condition:** Any expected artifact is absent, extra, mutable, mismatched, or incomplete.

**Commit boundary:** `feat: verify formal artifact completeness`

---

### Task 5: Issue `formal_completion_seal` without evaluating

**Objective:** Create the only evaluator-unseal capability after proving all 66 artifacts, resume/idempotence, calibration receipts, and zero metric exposure.

**Files:**
- Create: `src/vision_active_learning_loop/formal/seal.py`
- Create: `src/vision_active_learning_loop/gates/wave5.py`
- Create: `schemas/formal-completion-seal.schema.json`
- Create: `schemas/wave5-gate-receipt.schema.json`
- Create: `tests/formal/test_seal.py`
- Create: `tests/gates/test_wave5_gate.py`

**Interfaces:**
- Produces: `issue_completion_seal(freeze, inventory, embargo_audit) -> FormalCompletionSeal`
- Produces: `verify_completion_seal(seal, expected_protocol) -> VerifiedSeal`
- CLI: `val formal seal --freeze <json> --inventory <json> --embargo-audit <json> --output <json>`

- [ ] **Step 1: Write failing seal prerequisite tests**

```python
def test_seal_requires_66_complete_artifacts(inputs):
    inputs.inventory.fit_count = 65
    with pytest.raises(SealDenied):
        issue_completion_seal(**inputs)

def test_any_test_output_contaminates_experiment(inputs):
    inputs.embargo_audit.test_output_paths = ["metrics.json"]
    with pytest.raises(ExperimentContaminated):
        issue_completion_seal(**inputs)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/formal/test_seal.py tests/gates/test_wave5_gate.py -v`

Expected: missing seal/gate modules.

- [ ] **Step 3: Implement seal creation and capability token**

Bind experiment/protocol/freeze/model/environment/dataset/inventory/66 checkpoint/ledger/calibration/resume/idempotence/embargo hashes and code commit. Verify no test/shift output or evaluator start event. Store seal in external `completion_seals/<experiment_id>`; capability token is seal digest plus schema verification, not a mutable flag.

- [ ] **Step 4: Issue seal and verify Wave 5**

Run: `uv run val formal seal --freeze <freeze.json> --inventory <inventory.json> --embargo-audit <audit.json> --output "$VAL_ARTIFACT_ROOT/completion_seals/<experiment_id>/formal_completion_seal.json" && uv run pytest tests/formal/test_seal.py tests/gates/test_wave5_gate.py -v`

Expected: valid seal and Wave 5 PASS with zero evaluation metrics. Corrupted parent, 65/67 count, output leak, dirty code, or retry mismatch fails.

- [ ] **Step 5: Stop for owner evaluator-unseal review**

Report exact 66 accounting, checkpoint/ledger/inventory/seal digests, actual GPU hours, resumes/failures, embargo audit, and requested Wave 6 unseal authority. Do not launch evaluator.

**Artifact/evidence produced:** formal completion seal, Wave 5 gate and owner review packet.

**Stop condition:** Any prerequisite fails or owner has not explicitly approved evaluator unseal.

**Commit boundary:** `feat: seal completed formal experiment`
