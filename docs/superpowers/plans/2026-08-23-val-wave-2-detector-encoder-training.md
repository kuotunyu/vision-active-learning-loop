# Wave 2 Detector, Encoder, and Training Foundation Implementation Plan

> **Historical 8-wave protocol.** Preserved for provenance; this is not the current task queue. The original Wave 0 gate did not pass. The separately approved lite research completed its v0.3 five-strategy first comparison on 2026-09-12; see the [current README](../../../README.md) and [v0.3 results](../../results/2026-09-12-v0.3-diversity.md).

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the fixed RT-DETR/DINOv2 training foundation, calibration primitives, and resumable checkpoint contracts without reading source-test or China Drone data.

**Architecture:** Model wrappers expose typed raw outputs and frozen embeddings whose hashes are bound to the Wave 1 manifest. Training manifests separate acquired training and calibration images by immutable hash, and the trainer always starts from the same pinned pretrained base. Checkpoints atomically capture optimizer/scheduler/RNG/sampler state; calibration uses acquired labels only.

**Tech Stack:** Wave 0 locked PyTorch/Transformers runtime; RT-DETR-R18; DINOv2-small; BF16; AdamW; cosine schedule; pycocotools only in later evaluator; pytest and synthetic/tiny fixtures.

## Global Constraints

- Entry requires a valid Wave 1 gate receipt and owner approval.
- No source-test or China Drone evaluator module/path may be imported, mounted, or read.
- Input is 640×640 aspect-preserving resize plus bottom/right zero pad; training adds only horizontal flip p=0.5 and color jitter <=0.1.
- Train 30 epochs, batch 8, BF16, AdamW detector LR `1e-4`, backbone LR `1e-5`, weight decay `1e-4`, one-epoch warmup, cosine-to-zero, gradient clip 0.1, no early stopping.
- Formal/pilot fits use the final epoch and always initialize from the same pinned pretrained base; prior active-learning checkpoints only select.
- Calibration images count against acquired image/box budgets and never update detector weights.
- DINOv2 is frozen; embedding is 384-D post-LayerNorm CLS, float32 L2-normalized.

---

### Task 1: Implement the fixed RT-DETR wrapper and preprocessing contract

**Objective:** Provide one typed detector interface whose preprocessing and raw inference outputs exactly match the Wave 0 receipt.

**Files:**
- Create: `src/vision_active_learning_loop/models/types.py`
- Create: `src/vision_active_learning_loop/models/rtdetr.py`
- Create: `src/vision_active_learning_loop/models/preprocessing.py`
- Create: `configs/models/rtdetr-r18-rdd4.yaml`
- Create: `tests/models/test_rtdetr_wrapper.py`
- Create: `tests/models/test_preprocessing.py`

**Interfaces:**
- Produces: `RtdetrR18.from_receipt(asset_receipt, contract_receipt, seed: int) -> RtdetrR18`
- Produces: `RtdetrR18.raw_infer(batch: PixelBatch) -> RawDetectorOutput`
- Produces: `RtdetrR18.training_loss(batch: DetectionBatch) -> LossBundle`
- Produces: `preprocess_detection(image, boxes | None, training: bool, seed_key: str) -> PixelSample`

- [ ] **Step 1: Write failing wrapper/transform tests**

```python
def test_raw_wrapper_preserves_contract(wrapper, synthetic_batch):
    out = wrapper.raw_infer(synthetic_batch)
    assert out.logits.shape == (2, 300, 4)
    assert out.intermediate_boxes.shape[2:] == (300, 4)

def test_eval_transform_is_resize_pad_only(sample):
    a = preprocess_detection(sample.image, sample.boxes, training=False, seed_key="a")
    b = preprocess_detection(sample.image, sample.boxes, training=False, seed_key="b")
    assert torch.equal(a.pixel_values, b.pixel_values)
```

- [ ] **Step 2: Confirm tests fail before wrapper exists**

Run: `uv run pytest tests/models/test_rtdetr_wrapper.py tests/models/test_preprocessing.py -v`

Expected: missing wrapper/preprocessing modules.

- [ ] **Step 3: Implement receipt-bound loading and transforms**

Reject asset/contract/environment/dataset digest mismatches. Reset all decoder class heads to four outputs with the fit seed. Expose independent raw logits plus final/penultimate/intermediate cxcywh boxes. Transform boxes through resize, augmentation, and padding; reject invalid boxes before batching and record exclusions in the training receipt.

- [ ] **Step 4: Test exact augmentation allowlist**

Run: `uv run pytest tests/models/test_preprocessing.py -v -k "resize or pad or flip or color or forbidden"`

Expected: tests pass; mosaic, mixup, crop, copy-paste, and unregistered transform config are rejected.

- [ ] **Step 5: Verify against Wave 0 synthetic receipt**

Run: `uv run val model verify-wrapper --contract "$VAL_ARTIFACT_ROOT/wave0/receipts/model-contract-receipt.json" --config configs/models/rtdetr-r18-rdd4.yaml --output "$VAL_ARTIFACT_ROOT/training_receipts/wrapper.json"`

Expected: `PASS`, exact raw shapes/preprocessor digest/head reset, no labels used during raw inference.

**Artifact/evidence produced:** detector config/wrapper, transform tests, wrapper receipt.

**Stop condition:** Any output/processor/head invariant differs from Wave 0 or an unapproved augmentation can enter.

**Commit boundary:** `feat: add fixed rtdetr training wrapper`

---

### Task 2: Build the frozen DINOv2 embedding pipeline

**Objective:** Produce one content-addressed 384-D embedding matrix for each accepted manifest, reusable by core-set/hybrid without recomputation.

**Files:**
- Create: `src/vision_active_learning_loop/models/dinov2.py`
- Create: `src/vision_active_learning_loop/embeddings/store.py`
- Create: `schemas/embedding-manifest.schema.json`
- Create: `tests/models/test_dinov2.py`
- Create: `tests/embeddings/test_store.py`

**Interfaces:**
- Produces: `DinoV2Small.from_asset_receipt(receipt) -> DinoV2Small`
- Produces: `DinoV2Small.embed(images: Sequence[ImageRecord]) -> Float32Array[N,384]`
- Produces: `EmbeddingStore.create(dataset_digest, processor_digest, model_digest, rows) -> EmbeddingManifest`
- Produces: `EmbeddingStore.open_verified(manifest) -> EmbeddingMatrix`

- [ ] **Step 1: Write failing embedding invariants**

```python
def test_embeddings_are_float32_l2_unit(embeddings):
    assert embeddings.dtype == np.float32
    np.testing.assert_allclose(np.linalg.norm(embeddings, axis=1), 1.0, atol=1e-6)
    assert embeddings.shape[1] == 384

def test_store_rejects_manifest_digest_mismatch(store, manifest):
    manifest.dataset_digest = "f" * 64
    with pytest.raises(ArtifactMismatch):
        store.open_verified(manifest)
```

- [ ] **Step 2: Run tests in red state**

Run: `uv run pytest tests/models/test_dinov2.py tests/embeddings/test_store.py -v`

Expected: missing modules.

- [ ] **Step 3: Implement frozen CLS extraction and store**

Load only the pinned asset, set `eval()`, disable gradients, use checkpoint processor at 224 pixels, take final post-LayerNorm CLS, cast to float32, normalize, and order rows by item ID. Store matrix externally with item-ID row index, dtype/shape/row checksums, model/processor/dataset/probe hashes, GPU/time/VRAM receipt.

- [ ] **Step 4: Verify one-time and permutation behavior**

Run: `uv run pytest tests/models/test_dinov2.py tests/embeddings/test_store.py -v`

Expected: exact item-ID ordering independent of input order; second identical request reuses verified artifact; mismatched manifest/model refuses reuse.

- [ ] **Step 5: Generate retained-manifest embeddings**

Run: `uv run val embeddings build --dataset-manifest "$VAL_ARTIFACT_ROOT/manifests/dataset-manifest.json" --output-root "$VAL_ARTIFACT_ROOT/embeddings"`

Expected: one verified external matrix and manifest; no pixels/embeddings enter Git; source-test/shift embeddings are absent from strategy-facing stores.

**Artifact/evidence produced:** embedding matrix/manifest, row checksums, reuse and leak-boundary tests.

**Stop condition:** Encoder trainability, wrong dimension/dtype/norm, duplicate/missing item ID, or strategy store contains test/shift rows.

**Commit boundary:** `feat: build frozen dinov2 embeddings`

---

### Task 3: Create seed, acquired-label, training, and calibration manifests

**Objective:** Turn an acquired-label ledger into immutable train/calibration sets and deterministic data orders without consulting hidden labels.

**Files:**
- Create: `src/vision_active_learning_loop/training/manifests.py`
- Create: `src/vision_active_learning_loop/training/seeds.py`
- Create: `src/vision_active_learning_loop/training/sampler.py`
- Create: `schemas/training-manifest.schema.json`
- Create: `schemas/acquired-label-ledger.schema.json`
- Create: `tests/training/test_manifests.py`
- Create: `tests/training/test_sampler.py`

**Interfaces:**
- Produces: `build_training_manifest(dataset_digest, acquired_ledger, seed, budget) -> TrainingManifest`
- Produces: `seed_everything(seed: int) -> RngDigestBundle`
- Produces: `ordered_epoch_items(manifest, epoch: int) -> tuple[str, ...]`

- [ ] **Step 1: Write failing calibration/budget tests**

```python
def test_calibration_items_count_in_budget_but_not_training(manifest):
    assert len(manifest.acquired_ids) == len(manifest.train_ids) + len(manifest.calibration_ids)
    assert set(manifest.train_ids).isdisjoint(manifest.calibration_ids)

def test_calibration_assignment_is_item_hash_only(item_id):
    assert calibration_remainder(item_id) == calibration_remainder(item_id)
```

- [ ] **Step 2: Verify red state**

Run: `uv run pytest tests/training/test_manifests.py tests/training/test_sampler.py -v`

Expected: missing manifest/sampler modules.

- [ ] **Step 3: Implement immutable manifest construction**

Validate all acquired IDs exist in formal/pilot role, all revealed annotations have oracle digests, and budget count uses images. Assign remainder zero to calibration and others to training. Record revealed boxes only after acquisition. Seed streams are namespaced for head initialization, augmentation, sampler, worker, and noise.

- [ ] **Step 4: Implement deterministic sampler order**

Use an explicit torch generator per epoch and record ordered item digest. Reject seed outside `{17,29,43}` in formal mode; pilot permits only 17. Do not infer source country or class balance.

- [ ] **Step 5: Verify manifests and orders**

Run: `uv run pytest tests/training/test_manifests.py tests/training/test_sampler.py -v`

Expected: nested acquired sets produce correct disjoint train/cal partitions, exact budget counts, stable orders, and hidden-label-free construction.

**Artifact/evidence produced:** schemas, manifest builder, RNG/order digests, calibration budget tests.

**Stop condition:** Calibration labels enter weights, hidden counts affect a manifest, acquired/train/cal sets do not reconcile, or formal seed differs.

**Commit boundary:** `feat: define deterministic training manifests`

---

### Task 4: Implement the fixed trainer and atomic resume contract

**Objective:** Train from the pinned base with the approved recipe and resume only from a byte/schema/input-compatible checkpoint.

**Files:**
- Create: `src/vision_active_learning_loop/training/optimizer.py`
- Create: `src/vision_active_learning_loop/training/schedule.py`
- Create: `src/vision_active_learning_loop/training/trainer.py`
- Modify: `src/vision_active_learning_loop/training/checkpoint_io.py`
- Create: `schemas/checkpoint-manifest.schema.json`
- Create: `schemas/training-receipt.schema.json`
- Create: `tests/training/test_optimizer.py`
- Create: `tests/training/test_trainer.py`
- Create: `tests/training/test_resume.py`

**Interfaces:**
- Produces: `build_optimizer(model) -> AdamW`
- Produces: `build_schedule(optimizer, steps_per_epoch, epochs=30) -> LRScheduler`
- Produces: `Trainer.run(manifest: TrainingManifest, resume: Path | None) -> TrainingReceipt`

- [ ] **Step 1: Write failing recipe and fresh-base tests**

```python
def test_optimizer_groups_are_exact(optimizer):
    assert {(g["name"], g["lr"]) for g in optimizer.param_groups} == {("detector", 1e-4), ("backbone", 1e-5)}
    assert all(g["weight_decay"] == 1e-4 for g in optimizer.param_groups)

def test_later_budget_loads_pretrained_base_not_previous_checkpoint(trainer, manifest):
    assert trainer.initial_model_digest(manifest) == manifest.pretrained_base_digest
```

- [ ] **Step 2: Confirm tests fail**

Run: `uv run pytest tests/training/test_optimizer.py tests/training/test_trainer.py tests/training/test_resume.py -v`

Expected: missing optimizer/trainer modules.

- [ ] **Step 3: Implement exact 30-epoch trainer**

Use batch 8, `drop_last=False`, BF16, deterministic algorithms, clip norm 0.1, one warmup epoch, cosine-to-zero, final-epoch checkpoint, no early stopping. Log finite loss/components, LR, step/epoch, timing, memory, ordered-item digest, input hashes, and training-only/calibration counts. Do not import evaluator packages.

- [ ] **Step 4: Implement atomic checkpoint/resume**

Checkpoint includes model/optimizer/scheduler/AMP state, epoch/step, manifest/config/base/environment/protocol hashes, sampler position/order, RNG states, and content digest. Resume rejects any mismatch and proves interrupted vs uninterrupted final receipt equality on the canonical tiny fixture.

- [ ] **Step 5: Verify trainer and resume**

Run: `uv run pytest tests/training/test_optimizer.py tests/training/test_trainer.py tests/training/test_resume.py -v`

Expected: all tests pass; injected previous-budget warm start, missing RNG, altered item order, NaN, evaluator import, and mismatched manifest fail.

**Artifact/evidence produced:** fixed trainer, checkpoint/training schemas, recipe and resume proof.

**Stop condition:** Recipe drift, non-finite/deterministic failure, prior-budget warm start, checkpoint mismatch acceptance, or test/shift dependency.

**Commit boundary:** `feat: add fixed resumable detector trainer`

---

### Task 5: Implement acquired-only temperature, Brier, and adaptive ECE

**Objective:** Fit/report calibration exactly from acquired calibration labels while leaving acquisition logits untouched.

**Files:**
- Create: `src/vision_active_learning_loop/calibration/candidates.py`
- Create: `src/vision_active_learning_loop/calibration/temperature.py`
- Create: `src/vision_active_learning_loop/calibration/metrics.py`
- Create: `schemas/calibration-receipt.schema.json`
- Create: `tests/calibration/test_candidates.py`
- Create: `tests/calibration/test_temperature.py`
- Create: `tests/calibration/test_metrics.py`

**Interfaces:**
- Produces: `build_calibration_candidates(raw_outputs, acquired_labels) -> CandidateTable`
- Produces: `fit_scalar_temperature(table: CandidateTable) -> TemperatureFit`
- Produces: `binary_brier(confidence, correctness) -> float`
- Produces: `adaptive_ece(table, max_bins: int = 15) -> AdaptiveEceResult`

- [ ] **Step 1: Write failing denominator and eligibility tests**

```python
def test_candidate_denominator_is_top_100_pre_nms(raw_image):
    table = build_calibration_candidates(raw_image, acquired_labels(raw_image.item_id))
    assert len(table) == 100

def test_insufficient_support_returns_null_temperature(small_table):
    result = fit_scalar_temperature(small_table)
    assert result.status == "INSUFFICIENT" and result.temperature is None
```

- [ ] **Step 2: Write failing hand-calculated metric tests**

```python
def test_brier_hand_value():
    assert binary_brier([0.0, 0.5, 1.0], [0, 1, 1]) == pytest.approx(1 / 12)
```

Run: `uv run pytest tests/calibration -v`

Expected: missing calibration modules.

- [ ] **Step 3: Implement matching, gates, temperature, and metrics**

Take 100 largest query-class sigmoid candidates per image before threshold/NMS; tie by item/query/class. Greedily match class-and-IoU>=0.5 one-to-one. Enforce 200 images, 100 GT boxes, 20 per class, 50 correct, and 50 incorrect. Fit scalar `T` in `[0.05,10]` via deterministic float64 bounded optimization. Implement exact Brier and adaptive equal-count/tie-run bin formula from the spec.

- [ ] **Step 4: Prove acquisition remains raw**

Run: `uv run pytest tests/calibration -v -k "raw or acquisition or eligibility or ties or brier"`

Expected: tests pass; acquisition accessor rejects a calibrated-logit input; no test/shift labels are accepted by fit APIs.

- [ ] **Step 5: Validate receipt schema**

Run: `uv run pytest tests/calibration -v`

Expected: raw/calibrated status, temperature, Brier, adaptive ECE, bin/denominator/support counts serialize deterministically; LaECE is absent.

**Artifact/evidence produced:** calibration library/schema, hand-calculated tests, acquired-only enforcement.

**Stop condition:** Test/shift labels enter fitting, acquired support gate can be bypassed, calibration changes acquisition, or LaECE becomes required.

**Commit boundary:** `feat: add acquired only calibration metrics`

---

### Task 6: Integrate synthetic/tiny training evidence and the Wave 2 gate

**Objective:** Validate detector, embeddings, manifests, trainer, resume, calibration, and zero-detection behavior together without opening the formal evaluator.

**Files:**
- Create: `fixtures/synthetic/training/manifest.json`
- Create: `src/vision_active_learning_loop/gates/wave2.py`
- Create: `schemas/wave2-gate-receipt.schema.json`
- Create: `tests/integration/test_tiny_training.py`
- Create: `tests/integration/test_no_evaluator_access.py`
- Create: `tests/gates/test_wave2_gate.py`
- Create: `docs/runbooks/wave2.md`

**Interfaces:**
- Produces: `evaluate_wave2(inputs: Wave2Inputs) -> Wave2GateReceipt`
- CLI: `val gate wave2 --wave1 <receipt> --wrapper <receipt> --embeddings <manifest> --training <receipt> --calibration <receipt> --output <receipt>`

- [ ] **Step 1: Write failing end-to-end and embargo tests**

```python
def test_tiny_fit_resumes_to_same_final_digest(tiny_run):
    assert tiny_run.uninterrupted.final_digest == tiny_run.resumed.final_digest

def test_training_process_has_no_evaluator_mount_or_import(training_process):
    assert training_process.evaluator_paths == []
    assert training_process.imports_matching("evaluation.sealed") == []
```

- [ ] **Step 2: Run integration tests in red state**

Run: `uv run pytest tests/integration tests/gates/test_wave2_gate.py -v`

Expected: missing fixture/gate.

- [ ] **Step 3: Create original tiny detection fixture and integrated smoke**

Use synthetic road-like images/boxes for D00/D10/D20/D40, including an empty image and an output with zero thresholded detections. Run a short test-only schedule through the real transforms/trainer interfaces; mark it `fixture_only`, never as a pilot/formal fit.

- [ ] **Step 4: Evaluate all Wave 2 receipts**

Run: `uv run pytest tests/models tests/embeddings tests/training tests/calibration tests/integration -v && uv run val gate wave2 --wave1 <wave1.json> --wrapper <wrapper.json> --embeddings <embedding.json> --training <tiny-training.json> --calibration <calibration.json> --output <wave2.json>`

Expected: tests pass and Wave 2 gate `PASS`; no source-test/shift mount/import/output; exact receipt lineage.

- [ ] **Step 5: Stop for owner review**

Report commits, wrapper/embedding/training/calibration/gate hashes, tiny-fixture limitations, VRAM/runtime, and all failed attempts. Do not run Wave 3.

**Artifact/evidence produced:** integrated synthetic receipt tree, zero-detection test, embargo import audit, Wave 2 gate and review packet.

**Stop condition:** Any component receipt fails, tiny resume diverges, formal evaluator is reachable, or fixture output is mislabeled as experimental evidence.

**Commit boundary:** `feat: seal wave two training foundation`
