# Wave 4 Pilot and Protocol Freeze Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run exactly nine pilot fits on the isolated pilot partition, measure conservative component costs, and freeze a formal protocol only when every registered gate passes.

**Architecture:** A pilot matrix generator creates one shared 2% fit and four-arm 5%/10% fits for seed 17. The same orchestration/training paths intended for formal work emit timing and replay receipts; a cost projector enumerates every future fit and arm/round rather than scaling one pilot average. The protocol freezer produces a single immutable capability required by Wave 5.

**Tech Stack:** Waves 0–3 locked environment/library; RTX 4090; external artifact store; pytest; JSON/Parquet timing tables; deterministic job manifests.

## Global Constraints

- Entry requires PASS receipts for Waves 0–3 and explicit owner approval for nine RTX pilot fits.
- Pilot role is the frozen 8% engineering partition only; source-test, formal pool, and China Drone are unmounted.
- Pilot seed is 17; arms are random, entropy, core-set, and hybrid; budgets are 2%, 5%, and 10%.
- Fit count is exactly `1 + 4×2 = 9`; pilot outputs never enter formal curves.
- Any NaN/Inf/OOM/deterministic fallback, non-decreasing loss gate, score std <`1e-6`, exact-sequence mismatch, group/firewall error, resume mismatch, budget error, VRAM >22 GiB, projected arm/round >15 min, or projected 66-fit total >240 h blocks freeze.
- All cost bounds include 15% safety factor and use worst relevant observation, not the median round.

---

### Task 1: Generate the isolated nine-job pilot matrix

**Objective:** Encode pilot jobs and mount capabilities so no formal/test/shift artifact can enter.

**Files:**
- Create: `src/vision_active_learning_loop/pilot/matrix.py`
- Create: `configs/experiments/pilot-v1.yaml`
- Create: `schemas/pilot-job.schema.json`
- Create: `tests/pilot/test_matrix.py`
- Create: `tests/pilot/test_boundary.py`

**Interfaces:**
- Produces: `build_pilot_matrix(dataset_manifest, protocol) -> tuple[PilotJob, ...]`
- Produces: `PilotJob(job_id, seed, arm, from_budget, to_budget, fit_budget, mounts, parent_jobs)`
- CLI: `val pilot plan --config configs/experiments/pilot-v1.yaml --output <manifest>`

- [ ] **Step 1: Write failing count/dependency/boundary tests**

```python
def test_pilot_matrix_has_exactly_nine_fits(matrix):
    assert len(matrix.fit_jobs) == 9
    assert count(matrix, arm="shared", budget="0.02") == 1
    assert count_later(matrix) == 8

def test_pilot_mounts_exclude_formal_and_tests(matrix):
    assert forbidden_roles(matrix.mounts) == set()
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/pilot/test_matrix.py tests/pilot/test_boundary.py -v`

Expected: missing pilot modules.

- [ ] **Step 3: Implement exact DAG and manifests**

Shared 2% acquisition/fit precedes all arms. For each arm, 2→5 selection precedes its 5% fresh-base fit, then 5→10 selection precedes its 10% fresh-base fit. Job IDs hash protocol, pilot manifest, seed/arm/budget, model/environment, and parents. No formal/test/shift locator is serializable in `PilotJob`.

- [ ] **Step 4: Generate and inspect matrix**

Run: `uv run val pilot plan --config configs/experiments/pilot-v1.yaml --output "$VAL_ARTIFACT_ROOT/pilot/pilot-job-matrix.json"`

Expected: nine fits, eight later selection jobs, exact dependency edges, pilot-only mounts, seed 17, no margin arm.

**Artifact/evidence produced:** pilot config/matrix and role-boundary tests.

**Stop condition:** Count/dependency differs, non-pilot role enters, or a job lacks complete parent hashes.

**Commit boundary:** `feat: define isolated pilot matrix`

---

### Task 2: Execute, interrupt, resume, and replay all pilot jobs

**Objective:** Exercise real training/acquisition paths and prove finite convergence, deterministic resume, exact ledgers, and canonical selection sequences.

**Files:**
- Create: `src/vision_active_learning_loop/pilot/runner.py`
- Create: `src/vision_active_learning_loop/pilot/gates.py`
- Create: `schemas/pilot-fit-receipt.schema.json`
- Create: `tests/pilot/test_runner.py`
- Create: `tests/pilot/test_gates.py`

**Interfaces:**
- Produces: `PilotRunner.run(matrix, gpu_lease) -> PilotRunReceipt`
- Produces: `evaluate_fit_gate(training_receipt) -> GateResult`
- Produces: `evaluate_selection_gate(round_receipt) -> GateResult`

- [ ] **Step 1: Write failing convergence/resume/budget tests**

```python
def test_loss_gate_uses_first_and_last_ten_percent(receipt):
    assert evaluate_fit_gate(receipt).loss_decreased is True

def test_pilot_resume_matches_uninterrupted(interrupted, uninterrupted):
    assert interrupted.final_artifact_hash == uninterrupted.final_artifact_hash
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/pilot/test_runner.py tests/pilot/test_gates.py -v`

Expected: missing pilot runner/gates.

- [ ] **Step 3: Implement GPU-leased execution and interruption injection**

Use the common trainer/round runner, atomic artifacts, one GPU lease, and no evaluator. For one representative later fit and one k-center selection, inject termination at a deterministic safe point, resume/replay, and compare final hashes to clean runs. Record loss-step series, score distribution, ledgers, memory, timing, and environment.

- [ ] **Step 4: Run the nine jobs**

Run: `uv run val pilot run --matrix "$VAL_ARTIFACT_ROOT/pilot/pilot-job-matrix.json" --output-root "$VAL_ARTIFACT_ROOT/pilot/run-v1"`

Expected: nine complete fit receipts; finite loss decreases under the registered median-window rule; uncertainty score std >=`1e-6` on >=100 remaining items; exact reference/canonical IDs; nested exact budgets; peak allocated VRAM <=22 GiB.

- [ ] **Step 5: Verify replay and no evaluator access**

Run: `uv run pytest tests/pilot/test_runner.py tests/pilot/test_gates.py -v && uv run val pilot audit --run-root "$VAL_ARTIFACT_ROOT/pilot/run-v1" --output <pilot-audit.json>`

Expected: all gate booleans true, interruption parity true, no source/shift path/import/output.

**Artifact/evidence produced:** 9 fit receipts, selection/ledger artifacts, replay/interruption evidence, pilot audit.

**Stop condition:** Any registered pilot gate fails; do not rerun selectively to cherry-pick.

**Commit boundary:** `feat: execute and audit pilot jobs`

---

### Task 3: Instrument component-level canonical timing

**Objective:** Measure training steady-state/fixed costs and each acquisition component with dimensions needed for conservative formal projection.

**Files:**
- Create: `src/vision_active_learning_loop/compute/timers.py`
- Create: `src/vision_active_learning_loop/compute/observations.py`
- Create: `src/vision_active_learning_loop/compute/kernel_grid.py`
- Create: `schemas/timing-observation.schema.json`
- Create: `tests/compute/test_timers.py`
- Create: `tests/compute/test_kernel_grid.py`

**Interfaces:**
- Produces: `measure_training_steps(job) -> TrainingTimingObservation`
- Produces: `measure_detector_scoring(shape) -> ScoringObservation`
- Produces: `benchmark_kcenter_grid(grid: Sequence[KernelShape]) -> KernelGridReceipt`
- Produces: `KernelShape(N: int, centers: int, batch: int, dimension: int = 384)`

- [ ] **Step 1: Write failing dimension/component tests**

```python
def test_training_observation_separates_fixed_and_step_cost(obs):
    assert obs.model_load_seconds >= 0 and obs.checkpoint_write_seconds >= 0
    assert len(obs.steady_state_step_seconds) > 0

def test_grid_contains_projected_40_percent_shape(grid, projection_inputs):
    assert grid.brackets(projection_inputs.round_40_shape)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/compute/test_timers.py tests/compute/test_kernel_grid.py -v`

Expected: missing compute modules.

- [ ] **Step 3: Implement synchronized timers and observations**

Use CUDA events plus wall clock with synchronization. Record model load, warmup-discarded steps, steady-state steps, checkpoint write, acquired-dev inference, detector raw-output bytes/materialization throughput, score/sort, random ordering, embedding, core initialization/updates, hybrid shortlist/initialization/updates, peak VRAM/RAM, and exact workload dimensions.

- [ ] **Step 4: Benchmark formal-shape brackets**

Run: `uv run val compute benchmark --dataset-manifest <json> --pilot-root <root> --output "$VAL_ARTIFACT_ROOT/pilot/timing"`

Expected: grid brackets every projected `N,c,b,d`, including worst 40% rounds; each observation is canonical RTX/environment-bound; no test data read.

- [ ] **Step 5: Verify timer integrity**

Run: `uv run pytest tests/compute/test_timers.py tests/compute/test_kernel_grid.py -v`

Expected: injected unsynchronized, missing-dimension, median-only, or noncanonical observation fails validation.

**Artifact/evidence produced:** raw timings, dimensioned kernel grid, memory/resource observations.

**Stop condition:** Any formal shape is unbracketed, observation lacks a component/dimension, or canonical timing cannot be isolated.

**Commit boundary:** `feat: measure canonical pilot components`

---

### Task 4: Project every formal fit and arm/round conservatively

**Objective:** Apply exact step/tile formulas and worst conservative bounds to all 66 fits and 20 acquisitions plus the separate project total.

**Files:**
- Create: `src/vision_active_learning_loop/compute/projection.py`
- Create: `schemas/compute-projection.schema.json`
- Create: `tests/compute/test_projection.py`
- Create: `tests/compute/test_fit_accounting.py`

**Interfaces:**
- Produces: `project_66_fits(formal_matrix, timing) -> FitProjectionTable`
- Produces: `project_20_acquisitions(formal_matrix, timing, kernel_grid) -> AcquisitionProjectionTable`
- Produces: `project_total(pilot, primary, noise, embeddings, evaluation, reporting) -> ProjectTotal`

- [ ] **Step 1: Write failing exact-count and slowest-round tests**

```python
def test_fit_projection_enumerates_66_jobs(table):
    assert len(table.rows) == 66
    assert counts(table) == {"shared_2pct": 3, "arm_later": 60, "acquired_ceiling": 3}

def test_gate_uses_each_round_not_median(table):
    table.rows[-1].conservative_seconds = 901
    assert table.all_rounds_under_15_minutes is False
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/compute/test_projection.py tests/compute/test_fit_accounting.py -v`

Expected: missing projection module.

- [ ] **Step 3: Implement exact training/scoring formulas**

Training uses `30*ceil(n_train/8)*1.15*p95(step)` plus 1.15 times maximum load/checkpoint and bounded final acquired-dev batches. Detector scoring uses exact remaining batches, raw bytes, lower-fifth-percentile throughput, score/sort. Core/hybrid use exact initialization/update tile counts over the slowest bracketing kernel throughput plus 15%.

- [ ] **Step 4: Produce primary and project-total tables**

Run: `uv run val compute project --formal-matrix <matrix.json> --timing-root <timing> --output "$VAL_ARTIFACT_ROOT/pilot/projections"`

Expected: 20 acquisition rows each <=900 seconds; 66 fit rows sum <=240 GPU-hours. Separate totals list 9 pilot, 66 primary, 6 noise, DINO embedding, scoring/k-center, embargoed evaluation, reporting.

- [ ] **Step 5: Run projection tests**

Run: `uv run pytest tests/compute/test_projection.py tests/compute/test_fit_accounting.py -v`

Expected: count/formula/gate golden cases pass; linear reduced-pool-only and median-round implementations are rejected.

**Artifact/evidence produced:** machine-readable fit/acquisition/project projections with raw parents and pass/fail fields.

**Stop condition:** Any acquisition >15 min, 66 fits >240 GPU-hours, count differs, or a component is hidden in an aggregate.

**Commit boundary:** `feat: project formal compute bounds`

---

### Task 5: Freeze the protocol and issue the Wave 4 gate receipt

**Objective:** Content-address every normative input and prevent Wave 5 from starting with an incomplete or mutable pilot/projection result.

**Files:**
- Create: `src/vision_active_learning_loop/protocol/freeze.py`
- Create: `src/vision_active_learning_loop/gates/wave4.py`
- Create: `schemas/protocol-freeze-receipt.schema.json`
- Create: `schemas/wave4-gate-receipt.schema.json`
- Create: `tests/protocol/test_freeze.py`
- Create: `tests/gates/test_wave4_gate.py`
- Create: `docs/runbooks/wave4.md`

**Interfaces:**
- Produces: `freeze_protocol(spec_digest, wave_receipts, pilot_audit, projections) -> ProtocolFreezeReceipt`
- Produces: `evaluate_wave4(freeze_receipt) -> Wave4GateReceipt`
- CLI: `val protocol freeze --spec <file> --pilot <receipt> --projections <root> --output <receipt>`

- [ ] **Step 1: Write failing completeness/mutation tests**

```python
def test_freeze_requires_all_eleven_pilot_gates(inputs):
    inputs.pilot_gates.pop("peak_vram")
    with pytest.raises(FreezeDenied):
        freeze_protocol(**inputs)

def test_frozen_protocol_rejects_normative_mutation(freeze, mutated_config):
    assert evaluate_wave4(freeze.with_config(mutated_config)).status == "FAIL"
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/protocol/test_freeze.py tests/gates/test_wave4_gate.py -v`

Expected: missing freeze/gate modules.

- [ ] **Step 3: Implement freeze inventory**

Bind spec/protocol, dataset/exclusion/split, model/processor/environment, training recipe, seeds/budgets/arms, equations/tie/quantization, calibration, metric/claim, pilot, timing/projection, schemas, code commit, and dirty-state. Freeze receipt is created only from clean Git and all PASS parents.

- [ ] **Step 4: Issue and verify freeze**

Run: `uv run val protocol freeze --spec docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md --pilot <pilot-audit.json> --projections <projection-root> --output "$VAL_ARTIFACT_ROOT/pilot/protocol-freeze-receipt.json" && uv run pytest tests/protocol/test_freeze.py tests/gates/test_wave4_gate.py -v`

Expected: immutable PASS receipt and Wave 4 gate; any one-byte normative change fails capability validation.

- [ ] **Step 5: Stop for owner formal-run decision**

Report nine fits, every gate, worst projected arm/round, 66-fit hours, project total, freeze digest, failures, and requested Wave 5 GPU authority. Do not create a formal job.

**Artifact/evidence produced:** protocol freeze and Wave 4 receipts, owner review packet.

**Stop condition:** Any pilot/projection/input/clean-tree condition fails or owner has not approved formal execution.

**Commit boundary:** `feat: freeze pilot validated protocol`
