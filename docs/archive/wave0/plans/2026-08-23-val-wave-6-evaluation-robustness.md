# Wave 6 Evaluation and Robustness Implementation Plan

> **Historical 8-wave protocol.** Preserved for provenance; this is not the current task queue. The original Wave 0 gate did not pass. The separately approved lite research completed its v0.3 five-strategy first comparison on 2026-09-12; see the [current README](../../../../README.md) and [v0.3 results](../../../results/2026-09-12-v0.3-diversity.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** After verifying `formal_completion_seal`, run six pre-registered noise fits and one atomic source/shift evaluation batch, then generate grouped uncertainty and claim-gated label-efficiency evidence.

**Architecture:** Seal verification grants a one-experiment evaluator capability. Before result unsealing, a trainer-only path creates six noise checkpoints from frozen 20% manifests. One batch manifest then binds all primary/noise checkpoints and sealed datasets; evaluator writes to an unreadable staging store until atomic completion. Trusted analysis derives metrics, group bootstrap, curves, censoring outcomes, claims, tables, and charts from immutable batch results.

**Tech Stack:** Frozen runtime; pycocotools 2.0.10; NumPy/Pandas/Parquet; Matplotlib; RTX 4090; sealed evaluator OCI image; external write-only result store; pytest.

## Global Constraints

- Entry requires a valid Wave 5 completion seal and explicit owner approval to unseal evaluation.
- Source-test and China Drone are evaluated in one manifest-driven batch; China Drone is always `shift_only` and excluded from source nAUBC/claim rescue.
- Evaluator staging is write-only to running evaluator and unreadable to strategy/trainer/analyst until the full batch atomically completes.
- Technical retry requires byte-identical checkpoints, manifests, evaluator image/code/environment, and output schema; changed input requires a new batch/experiment review.
- Six noise fits are exactly random/hybrid at clean 20% for three seeds; they do not alter the 66 count.
- Bootstrap unit is `split_group_id`, stratified within source country; China Drone is separate; 2,000 replicates.
- Three seed curves remain primary; no small-n p-value or human time/money claim.

---

### Task 1: Verify the seal and construct the one-shot evaluation capability

**Objective:** Make evaluator startup impossible without the exact seal and define an immutable batch manifest that can later include the six registered auxiliary checkpoints.

**Files:**
- Create: `src/vision_active_learning_loop/evaluation/capability.py`
- Create: `src/vision_active_learning_loop/evaluation/batch_manifest.py`
- Create: `schemas/evaluation-batch.schema.json`
- Create: `tests/evaluation/test_capability.py`
- Create: `tests/evaluation/test_batch_manifest.py`

**Interfaces:**
- Produces: `EvaluationCapability.from_seal(seal, protocol, evaluator_image_digest) -> EvaluationCapability`
- Produces: `build_batch_manifest(capability, primary_inventory, auxiliary_inventory, source_manifest, shift_manifest) -> EvaluationBatchManifest`
- CLI: `val evaluation plan --seal <json> --auxiliary-inventory <json> --output <json>`

- [ ] **Step 1: Write failing seal/input tests**

```python
def test_capability_rejects_wrong_inventory_digest(seal, protocol):
    seal.inventory_digest = "0" * 64
    with pytest.raises(UnsealDenied):
        EvaluationCapability.from_seal(seal, protocol, "image-digest")

def test_batch_contains_source_and_shift_as_separate_roles(batch):
    assert batch.dataset_roles == ("source_test", "shift_only")
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/evaluation/test_capability.py tests/evaluation/test_batch_manifest.py -v`

Expected: missing evaluation modules.

- [ ] **Step 3: Implement capability verification**

Rehash seal and every parent, require 66 primary inventory rows, PASS embargo audit, exact protocol/model/environment, owner-unseal receipt, and evaluator image digest. The capability is scoped to one experiment/seal/batch and cannot mount strategy/trainer outputs beyond frozen checkpoint inputs.

- [ ] **Step 4: Implement batch schema without launching it**

Batch rows contain checkpoint digest, kind/seed/arm/budget, calibration receipt, source/shift manifest digests, evaluator code/image/environment, metric config, and expected output partitions. Sort by `(kind,seed,arm,budget,checkpoint_digest)`.

- [ ] **Step 5: Verify plan-time denial and schema**

Run: `uv run pytest tests/evaluation/test_capability.py tests/evaluation/test_batch_manifest.py -v`

Expected: all tests pass; no evaluator process starts during planning; missing owner unseal or auxiliary inventory keeps batch status `NOT_READY`.

**Artifact/evidence produced:** evaluation capability/schema and seal-adversarial tests.

**Stop condition:** Seal/parent/owner approval/evaluator image cannot be verified.

**Commit boundary:** `feat: gate sealed evaluation capability`

---

### Task 2: Generate exact noise manifests and complete six auxiliary fits

**Objective:** Apply deterministic 10% corruption to random/hybrid 20% training items and finish all six checkpoints before opening evaluation results.

**Files:**
- Create: `src/vision_active_learning_loop/robustness/label_noise.py`
- Create: `src/vision_active_learning_loop/robustness/noise_runner.py`
- Create: `schemas/corruption-manifest.schema.json`
- Create: `schemas/auxiliary-inventory.schema.json`
- Create: `tests/robustness/test_label_noise.py`
- Create: `tests/robustness/test_noise_runner.py`

**Interfaces:**
- Produces: `build_corruption_manifest(clean_manifest, seed, arm) -> CorruptionManifest`
- Produces: `apply_corruption(labels, manifest) -> CorruptedLabels`
- Produces: `NoiseRunner.run(manifests, gpu_lease) -> AuxiliaryInventory`

- [ ] **Step 1: Write failing rounding/no-op/order tests**

```python
@pytest.mark.parametrize(("M","expected"), [(0,(0,0,0,0)), (9,(0,0,0,0)), (10,(1,0,0,1)), (100,(10,4,3,3))])
def test_noise_rounding(M, expected):
    assert noise_counts(M) == expected

def test_k_zero_is_noop(clean_manifest):
    manifest = build_for_M(clean_manifest, M=9)
    assert manifest.status == "NO_OP" and manifest.affected_ids == []
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/robustness/test_label_noise.py tests/robustness/test_noise_runner.py -v`

Expected: missing robustness modules.

- [ ] **Step 3: Implement exact allocation and box hash rules**

Let `K=floor(.10M)`, `drop=floor(.40K)`, `class=floor(.30K)`, `jitter=K-drop-class`. Rank positive training images and target boxes by approved hashes; assign contiguous operation segments. Implement class-next-mod-4 and four-word deterministic jitter mapping. Calibration remains clean.

- [ ] **Step 4: Bind and run six fits under trainer embargo**

Run: `uv run val robustness noise-run --seal <seal.json> --experiment-root <root> --output "$VAL_ARTIFACT_ROOT/formal/<experiment_id>/auxiliary-inventory.json"`

Expected: six fits=`2 arms×3 seeds`, all initialized from pinned base with same 20% clean acquisition/calibration split, receipts bind clean manifest/dataset/seed/arm/operations, no evaluator result is readable.

- [ ] **Step 5: Verify exact manifests/checkpoints**

Run: `uv run pytest tests/robustness/test_label_noise.py tests/robustness/test_noise_runner.py -v`

Expected: allocation/operation/hash golden vectors pass; forced-one-image, calibration corruption, wrong arm/budget, or clean-manifest mismatch fails.

**Artifact/evidence produced:** six corruption manifests/checkpoints/training receipts and auxiliary inventory.

**Stop condition:** Count differs from six, allocation differs, calibration is corrupted, clean manifest mismatch, or test result influences execution.

**Commit boundary:** `feat: run registered label noise fits`

---

### Task 3: Run the atomic source and China Drone evaluation batch

**Objective:** Compute detection and calibrated confidence outputs for all batch checkpoints without exposing partial results.

**Files:**
- Create: `src/vision_active_learning_loop/evaluation/coco.py`
- Create: `src/vision_active_learning_loop/evaluation/runner.py`
- Create: `src/vision_active_learning_loop/evaluation/atomic_store.py`
- Create: `docker/evaluator.Dockerfile`
- Create: `schemas/evaluation-result.schema.json`
- Create: `tests/evaluation/test_coco.py`
- Create: `tests/evaluation/test_atomic_batch.py`
- Create: `tests/evaluation/test_retry.py`

**Interfaces:**
- Produces: `evaluate_checkpoint(checkpoint, dataset_role, metric_config, calibration_receipt) -> CheckpointEvaluation`
- Produces: `EvaluationBatchRunner.run(batch_manifest, capability, staging_root) -> BatchReceipt`
- Produces: `AtomicResultStore.publish(batch_receipt) -> str`

- [ ] **Step 1: Write failing COCO/atomic/retry tests**

```python
def test_coco_contract(metric_config):
    assert metric_config.iou_thresholds == tuple(np.arange(.50, .96, .05))
    assert metric_config.max_detections == 100

def test_partial_batch_is_unreadable(store, partial_batch):
    with pytest.raises(ResultEmbargoed):
        store.open(partial_batch.digest)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/evaluation/test_coco.py tests/evaluation/test_atomic_batch.py tests/evaluation/test_retry.py -v`

Expected: missing evaluator modules.

- [ ] **Step 3: Implement exact checkpoint metrics**

Compute mAP50–95, AP50, per-class AP/recall maxDets100, macro/min/D40 recall, supports, source countries, aggregate source, and separate shift. Apply already-fitted scalar temperature to identical top-100 candidate denominator; report raw/calibrated Brier/adaptive ECE/status/support. Do not fit temperature from evaluator labels.

- [ ] **Step 4: Implement write-only atomic batch and retry fingerprint**

Evaluator writes checkpoint partitions to a staging capability readable only by itself. On full validation, hash inventory and success receipt are atomically moved to results. Retry is permitted only when complete batch input/image/code/environment/schema fingerprint is identical; old partial tree is preserved for audit and not merged.

- [ ] **Step 5: Run the single batch**

Run: `uv run val evaluation plan --seal <seal.json> --auxiliary-inventory <aux.json> --output <batch.json> && uv run val evaluation run --batch <batch.json> --staging-root "$VAL_ARTIFACT_ROOT/evaluator_write_only/<seal_digest>"`

Expected: one complete batch receipt, source and shift partitions for every primary/auxiliary checkpoint, no readable partial output, atomic result publication only at batch completion.

- [ ] **Step 6: Verify atomic/retry behavior**

Run: `uv run pytest tests/evaluation/test_coco.py tests/evaluation/test_atomic_batch.py tests/evaluation/test_retry.py -v`

Expected: metric golden fixture passes; interrupted identical retry succeeds; any changed byte denies retry/new review required.

**Artifact/evidence produced:** immutable batch manifest/result inventory, machine result partitions, atomic batch/retry receipt.

**Stop condition:** Partial result leaks, temperature is test-fit, metric contract differs, source/shift mixes, or retry input changes.

**Commit boundary:** `feat: evaluate sealed experiment atomically`

---

### Task 4: Compute country-stratified split-group bootstrap sensitivity

**Objective:** Produce optional fixed-checkpoint evaluation-set sensitivity without image-IID or seed-uncertainty claims.

**Files:**
- Create: `src/vision_active_learning_loop/analysis/group_bootstrap.py`
- Create: `schemas/bootstrap-result.schema.json`
- Create: `tests/analysis/test_group_bootstrap.py`

**Interfaces:**
- Produces: `bootstrap_source_groups(predictions, groups, countries, checkpoint_hash, n=2000) -> BootstrapResult`
- Produces: `bootstrap_shift_groups(predictions, groups, checkpoint_hash, n=2000) -> BootstrapResult`

- [ ] **Step 1: Write failing cluster/strata/RNG tests**

```python
def test_resample_keeps_complete_groups(sample):
    assert every_selected_group_contains_all_images(sample)

def test_source_resampling_is_within_country(bootstrap_draw):
    assert bootstrap_draw.cross_country_group_moves == 0
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/analysis/test_group_bootstrap.py -v`

Expected: missing bootstrap module.

- [ ] **Step 3: Implement exact 2,000-replicate procedures**

Seed RNG with `SHA256("group-bootstrap-v1"||checkpoint_hash||dataset_role)`. For each source country, sample the observed number of group IDs with replacement and retain all group images; duplicate selected groups with replicate-local IDs. Bootstrap China Drone groups separately. Recompute registered metrics from fixed predictions.

- [ ] **Step 4: Verify clustered behavior and labels**

Run: `uv run pytest tests/analysis/test_group_bootstrap.py -v`

Expected: deterministic replicate digests; no image-level sampling; source countries preserved; shift separate; result metadata says `fixed_checkpoint_evaluation_set_sensitivity` and `not_seed_uncertainty`.

**Artifact/evidence produced:** group-bootstrap result tables/receipts and deterministic sample tests.

**Stop condition:** Image is sampled independently, groups split, countries mix, shift pools with source, or interval is labeled method uncertainty.

**Commit boundary:** `feat: add grouped evaluation sensitivity`

---

### Task 5: Compute budget curves, nAUBC, targets, and censoring truth table

**Objective:** Derive exact label-efficiency and compute-efficiency statistics from immutable evaluation/cost records.

**Files:**
- Create: `src/vision_active_learning_loop/analysis/budget_curves.py`
- Create: `src/vision_active_learning_loop/analysis/aubc.py`
- Create: `src/vision_active_learning_loop/analysis/censoring.py`
- Create: `tests/analysis/test_aubc.py`
- Create: `tests/analysis/test_censoring.py`

**Interfaces:**
- Produces: `normalized_aubc(points) -> float`
- Produces: `labels_to_target(curve, ceiling_map) -> TargetOutcome`
- Produces: `compare_target_cost(hybrid, random) -> Literal["PASS","SUPPORTIVE","FAIL","INSUFFICIENT"]`

- [ ] **Step 1: Write failing AUBC/target tests**

```python
def test_aubc_excludes_acquired_budget_ceiling(points):
    assert normalized_aubc(points) == trapezoid(points.at([.02,.05,.10,.20,.40])) / .38

def test_both_censored_is_insufficient():
    assert compare_target_cost(censored(), censored()) == "INSUFFICIENT"
```

- [ ] **Step 2: Add all censor truth-table cases as failing tests**

Run: `uv run pytest tests/analysis/test_aubc.py tests/analysis/test_censoring.py -v`

Expected: missing modules.

- [ ] **Step 3: Implement exact observed-budget and box-cost rules**

Target is 90% of each seed’s 100% acquired-budget-ceiling source mAP. Use first observed budget only, no interpolation. Implement observed/observed both-cost <=; hybrid observed/random censored lower bounds at random 40% for images and boxes; random observed/hybrid censored FAIL; both censored INSUFFICIENT.

- [ ] **Step 4: Build per-seed and paired tables**

Run: `uv run pytest tests/analysis/test_aubc.py tests/analysis/test_censoring.py -v && uv run val analyze budgets --results <batch-root> --cost-ledgers <root> --output <analysis-root>`

Expected: each seed/arm curve has image/fraction/box/GPU-hour axes; shared 2% labeled once; nAUBC/paired deltas/mean/median/sign consistency; shift excluded.

**Artifact/evidence produced:** budget curves, nAUBC and target/censor tables with golden tests.

**Stop condition:** Ceiling enters AUBC, interpolation creates success, censored outcome changes, box cost absent, or shift rescues source.

**Commit boundary:** `feat: compute label efficiency outcomes`

---

### Task 6: Generate machine-readable reports, charts, and claim decisions

**Objective:** Publish honest individual-seed, rare-class, calibration, selection, shift, noise, and compute evidence with a mechanical headline-claim gate.

**Files:**
- Create: `src/vision_active_learning_loop/analysis/claims.py`
- Create: `src/vision_active_learning_loop/reporting/tables.py`
- Create: `src/vision_active_learning_loop/reporting/charts.py`
- Create: `schemas/claim-decision.schema.json`
- Create: `tests/analysis/test_claims.py`
- Create: `tests/reporting/test_tables.py`
- Create: `tests/reporting/test_charts.py`

**Interfaces:**
- Produces: `decide_reduced_labeling_cost(evidence) -> ClaimDecision`
- Produces: `build_result_tables(evaluation, budgets, bootstrap, noise, compute) -> TableBundle`
- Produces: `render_static_charts(table_bundle, output_root) -> ChartManifest`

- [ ] **Step 1: Write failing claim-gate tests**

```python
def test_one_insufficient_seed_blocks_headline(valid_evidence):
    valid_evidence.seed_outcomes[1] = "INSUFFICIENT"
    assert decide_reduced_labeling_cost(valid_evidence).headline_allowed is False

def test_rare_class_decline_over_three_points_blocks(valid_evidence):
    valid_evidence.d40_delta_at_40 = [-.031, 0, 0]
    assert decide_reduced_labeling_cost(valid_evidence).headline_allowed is False
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/analysis/test_claims.py tests/reporting/test_tables.py tests/reporting/test_charts.py -v`

Expected: missing analysis/reporting modules.

- [ ] **Step 3: Implement all claim prerequisites**

Require hybrid nAUBC > random in all three seeds, per-seed target-cost PASS/SUPPORTIVE with no INSUFFICIENT, min/D40 recall within 3 points at 40%, no shift rescue, no censored exact-savings statement. Emit `positive`, `mixed`, `negative`, or `insufficient` plus failed clauses; never infer human time/money.

- [ ] **Step 4: Build tables and charts**

Include individual curves plus mean/median, paired deltas/ranges/signs, per-class/country/support, selection proportions/revealed distributions/discovery round, raw/calibrated Brier/adaptive ECE/status, shift-only, six noise deltas, timing/VRAM/GPU hours, bootstrap labeled as fixed-checkpoint sensitivity, and all failures/censoring.

- [ ] **Step 5: Verify static output contracts**

Run: `uv run pytest tests/analysis/test_claims.py tests/reporting/test_tables.py tests/reporting/test_charts.py -v`

Expected: golden result sets produce correct claim decisions; every chart caption identifies role/seed aggregation/budget/calibration/shared 2%/100% acquired-budget ceiling; no p-value/human savings language.

**Artifact/evidence produced:** claim receipt, aggregate machine tables, chart manifest/static charts.

**Stop condition:** Claim can bypass a gate, three individual seeds disappear, supports/status absent, or prohibited claim wording appears.

**Commit boundary:** `feat: generate claim gated result evidence`

---

### Task 7: Seal Wave 6 evaluation and robustness evidence

**Objective:** Validate the atomic batch, six auxiliary fits, analyses, reports, and no-feedback lineage before portfolio work.

**Files:**
- Create: `src/vision_active_learning_loop/gates/wave6.py`
- Create: `schemas/wave6-gate-receipt.schema.json`
- Create: `tests/gates/test_wave6_gate.py`
- Create: `docs/runbooks/wave6.md`

**Interfaces:**
- Produces: `evaluate_wave6(inputs: Wave6Inputs) -> Wave6GateReceipt`
- CLI: `val gate wave6 --seal <json> --batch <json> --auxiliary <json> --analysis-root <path> --output <json>`

- [ ] **Step 1: Write failing completeness/no-feedback tests**

```python
def test_wave6_requires_six_auxiliary_fits(inputs):
    inputs.auxiliary.fit_count = 5
    assert evaluate_wave6(inputs).status == "FAIL"

def test_evaluation_digest_never_parents_training(inputs):
    assert all(inputs.batch.digest not in fit.parent_digests for fit in inputs.all_training_receipts)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/gates/test_wave6_gate.py -v`

Expected: missing gate.

- [ ] **Step 3: Implement complete lineage validation**

Require valid seal/capability, 66 primary plus 6 auxiliary checkpoint evaluations, atomic batch, exact source/shift separation, calibration statuses, 2,000 group bootstraps if reported, all curves/claims/compute/noise tables, retry fingerprint, and no evaluator output digest in any training/acquisition/resume/config parent.

- [ ] **Step 4: Run gate and stop**

Run: `uv run pytest tests/evaluation tests/robustness tests/analysis tests/reporting tests/gates/test_wave6_gate.py -v && uv run val gate wave6 --seal <seal.json> --batch <batch.json> --auxiliary <aux.json> --analysis-root <root> --output <wave6.json>`

Expected: all tests pass and gate `PASS`; report the actual claim status even if negative/mixed/insufficient. Stop before portfolio release work.

**Artifact/evidence produced:** Wave 6 gate, evaluation/robustness lineage and owner review packet.

**Stop condition:** Any input/count/atomicity/separation/claim/no-feedback invariant fails.

**Commit boundary:** `feat: seal evaluation robustness evidence`
