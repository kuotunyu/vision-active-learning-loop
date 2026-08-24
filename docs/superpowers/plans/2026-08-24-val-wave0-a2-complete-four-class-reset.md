# Wave 0 A2 Complete Four-Class Reset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the confirmed RT-DETR 80-vs-4 class-contract omission, close the checkpoint and receipt no-clobber findings, and replay the already-approved Wave 0 gates from a fresh evidence chain without changing the experiment design.

**Architecture:** Keep the pinned RT-DETR-R18 model and its 300-query pipeline unchanged. Extend the existing seeded reset so every class-dependent decoder, denoising, and encoder module is replaced in one fixed RNG stream. Expand the synthetic model-contract probe to observe both label-free and labeled loss paths, bind the pinned loss source and registered targets into the receipt, and fail on every reachable non-four-class tensor. Use one cross-platform hard-link publication primitive for atomic create-if-absent files and atomic directory creation for fresh checkpoint roots. Commit and review all source changes before building a fresh OCI image; then execute one primary A2 chain and two clean replays under one new run identity, aggregate them, and stop before Wave 1.

**Tech Stack:** Python 3.12.11; uv 0.8.15; SciPy 1.18.0; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; pycocotools 2.0.10; pytest; JSON Schema; Black 22.6.0 for touched-file checks; Ruff 0.16.4 for touched-file checks; CUDA 12.6; RTX 4090 24 GB; WSL2 Ubuntu 24.04; OCI.

## Scope lock and immutable baseline

- The implementation entry point is the owner-reviewed commit containing this plan on `codex/wave0-model-contract`. The executor must verify that exact owner-supplied SHA, branch, repository, clean worktree, clean canonical main, and approved Git identity before changing a file. A mismatch stops execution; checkout, reset, rebase, stash, cherry-pick, and repository switching are forbidden.
- A2 fixes only the confirmed `model.model.enc_score_head` omission that caused the 80-vs-4 labeled-loss failure and the two final reviewer findings: fresh checkpoint roots/destinations and atomic no-clobber receipt publication.
- The detector remains `PekingU/rtdetr_r18vd` revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d`; the processor, 300 queries, four RDD classes, seed 17, dependency versions, datasets, acquisition arms, budgets, and fit counts remain unchanged.
- No new model, head strategy, dataset, seed, acquisition arm, pilot fit, formal fit, or research claim is introduced. The established counts remain 9 pilot fits, 66 primary fits, and 6 label-noise auxiliary fits.
- No Wave 0 gate is reduced. The A2 finite labeled-forward check supplements the existing BF16 backward, finite-gradient, parameter-update, VRAM, checkpoint round-trip, deterministic replay, and aggregate gates.
- No RDD bytes, paths, annotations, archives, metadata dumps, mounts, or downloads are permitted. `VAL_DATA_ROOT` remains unset throughout Wave 0.
- Earlier commits, the prior OCI image, the registered eleven pre-existing receipt records, the Option A receipts, the 80-vs-4 failure record, logs, checkpoints, hash corrections, and audits remain immutable. A previous `FAIL` stays `FAIL`; a previous narrower `PASS` is not A2 evidence.
- Every A2 runtime output is placed below a newly and atomically created run root under `$VAL_ARTIFACT_ROOT/wave0/a2-runs/`. Nothing generated at runtime enters Git.
- Whole-tree Black/Ruff debt is outside this repair. Format and lint only the Python files listed as touched below; do not mass-format or refactor unrelated code.
- No remote is created or changed. Push, PR, merge, tag, Release, GitHub repository creation, and publication are forbidden.
- Even if A2 passes, Wave 1 remains forbidden until a separate owner authorization.

## A2 file map

| Area | Exact files | Action |
|---|---|---|
| Complete reset | `src/vision_active_learning_loop/models/rtdetr_contract.py`; `tests/probes/test_model_contract.py` | Modify |
| Synthetic targets and labeled contract | `fixtures/synthetic/wave0/fixture-manifest.json`; `scripts/generate_wave0_fixtures.py`; `src/vision_active_learning_loop/probes/model_contract.py`; `src/vision_active_learning_loop/probes/training_feasibility.py`; `tests/probes/test_model_contract.py`; `tests/probes/test_processor_contract.py`; `tests/probes/test_training_feasibility.py` | Modify |
| Pinned source and receipt contract | `configs/models/pinned-models.yaml`; `src/vision_active_learning_loop/models/assets.py`; `src/vision_active_learning_loop/artifacts/receipts.py`; `schemas/model-asset-receipt.schema.json`; `schemas/model-contract-receipt.schema.json`; `schemas/feasibility-receipt.schema.json`; `tests/models/test_assets.py`; `tests/artifacts/test_receipts.py` | Modify |
| Atomic no-clobber primitive | `src/vision_active_learning_loop/artifacts/no_clobber.py`; `tests/artifacts/test_no_clobber.py` | Create |
| Checkpoint freshness | `src/vision_active_learning_loop/training/checkpoint_io.py`; `src/vision_active_learning_loop/probes/training_feasibility.py`; `tests/training/test_checkpoint_io.py`; `tests/probes/test_training_feasibility.py` | Modify |
| Wave 0 aggregate replay | `src/vision_active_learning_loop/gates/__init__.py`; `src/vision_active_learning_loop/gates/wave0.py`; `schemas/wave0-gate-receipt.schema.json`; `tests/gates/test_wave0_gate.py`; `scripts/run_wave0_clean.ps1`; `scripts/run_wave0_clean.sh`; `docs/runbooks/wave0.md` | Create |

The original plan `docs/superpowers/plans/2026-08-23-val-wave-0-model-contract-feasibility.md` is the approved baseline and is not modified by this remediation.

---

### Task 1: Complete every class-dependent RT-DETR reset

**Objective:** Make `reset_four_class_head()` replace the decoder, denoising, and encoder classification modules in the exact approved RNG order while preserving every non-class structural property.

**Files:**
- Modify: `tests/probes/test_model_contract.py`
- Modify: `src/vision_active_learning_loop/models/rtdetr_contract.py`

**Interfaces:**
- Preserve: `reset_four_class_head(model: Any, seed: int = 17) -> None`
- Preserve: `RDD_LABELS = ("D00", "D10", "D20", "D40")`
- Failure type: `ContractUnavailable` when a required decoder head, `model.model.denoising_class_embed`, or `model.model.enc_score_head` is missing or has the wrong module kind.

The replacement order is normative and contains no reseed or intervening random module initialization:

1. `model.model.decoder.class_embed[index]`, ascending index;
2. `model.model.denoising_class_embed`;
3. `model.model.enc_score_head`.

- [ ] **Step 1: Expand the CPU fake model and write the failing encoder-reset test**

Add the test-only helper `_model_with_class_components(*, labels: int = 80, decoder_layers: int = 3, decoder_bias: bool = True, encoder_bias: bool = True, dtype: torch.dtype = torch.float32) -> SimpleNamespace`. It must construct three `nn.Linear(8, labels)` decoder heads, `nn.Embedding(labels + 1, 16, padding_idx=labels)`, and `nn.Linear(256, labels)` at the exact production module paths.

```python
def test_reset_replaces_encoder_score_head_with_four_classes() -> None:
    model = _model_with_class_components(labels=80)
    original = model.model.enc_score_head

    reset_four_class_head(model, seed=17)

    assert model.model.enc_score_head is not original
    assert model.model.enc_score_head.out_features == 4
```

Run:

```powershell
uv run pytest tests/probes/test_model_contract.py::test_reset_replaces_encoder_score_head_with_four_classes -v
```

Expected RED: the assertion reports `out_features == 80`, reproducing the confirmed omission without loading a pretrained model or running a forward pass.

- [ ] **Step 2: Add sentinel, identity, structure-preservation, and exact-mapping tests**

Set every old decoder/encoder weight and bias and every denoising row to distinct constant sentinels. Record each old module object, device, dtype, `in_features` or `embedding_dim`, and bias presence. After reset assert:

```python
assert [head.out_features for head in model.model.decoder.class_embed] == [4, 4, 4]
assert model.model.denoising_class_embed.num_embeddings == 5
assert model.model.denoising_class_embed.padding_idx == 4
assert model.model.enc_score_head.out_features == 4
assert model.config.num_labels == 4
assert model.config.id2label == {0: "D00", 1: "D10", 2: "D20", 3: "D40"}
assert model.config.label2id == {"D00": 0, "D10": 1, "D20": 2, "D40": 3}
```

Assert all module identities changed; decoder and encoder `in_features`, denoising `embedding_dim`, bias presence, device, and dtype did not change; no replacement tensor equals or contains the old sentinel rows; and denoising row 4 is exactly zero.

Run:

```powershell
uv run pytest tests/probes/test_model_contract.py -v -k "reset and (sentinel or identity or preserves or mapping)"
```

Expected RED: encoder identity/sentinel checks fail because the current implementation retains the COCO encoder head.

- [ ] **Step 3: Add an independent RNG-order oracle and deterministic replay tests**

Create a test-only `_reference_replacements_in_approved_order(model: Any, seed: int) -> dict[str, torch.Tensor]`. It must use an independent `torch.random.fork_rng` scope and create/initialize the replacement modules in the approved decoder-index, denoising, encoder order. It may not call `reset_four_class_head()`.

Test two fake models whose old COCO tensors contain different values. Reset both with seed 17 and assert bit-identical decoder weights/biases, denoising weights, and encoder weights/biases. Compare all replacements with the independent oracle. Reset with seed 29 and assert at least one replacement tensor differs. Add missing/wrong-type tests for each required component.

Run:

```powershell
uv run pytest tests/probes/test_model_contract.py -v -k "rng_order or deterministic or unavailable"
```

Expected RED: the oracle has an encoder observation that the production reset does not produce; missing encoder and denoising modules are not yet rejected consistently.

- [ ] **Step 4: Implement the minimal complete reset**

Collect CUDA device indices from all old decoder heads, the denoising embedding, and the encoder score head before entering one `torch.random.fork_rng` scope. Seed that scope exactly once with the supplied seed. Recreate and initialize modules in the normative order.

For decoder and encoder linear modules:

- construct a new `nn.Linear` with the original `in_features`, original bias presence, original weight device, and original weight dtype;
- apply `nn.init.xavier_uniform_` to the weight;
- set the bias to `-log((1 - p) / p)`, where `p = model.config.initializer_bias_prior_prob or 1 / 5`;
- never index, copy, slice, or load a pretrained class-specific tensor.

For the denoising embedding:

- construct `nn.Embedding(5, original.embedding_dim, padding_idx=4)` on the original device/dtype;
- apply Xavier uniform initialization;
- zero row 4 after initialization;
- never copy an old embedding row.

Update `num_labels`, `id2label`, and `label2id` only after all three replacement groups complete.

- [ ] **Step 5: Run Task 1 GREEN verification**

```powershell
uv run pytest tests/probes/test_model_contract.py -v -k "reset or rng_order or deterministic or sentinel or identity or mapping or unavailable"
```

Expected GREEN: all selected tests pass on CPU; exact seed-17 replay includes the encoder replacement and no COCO class-specific tensor is reused.

- [ ] **Step 6: Format, lint, review, and commit Task 1**

```powershell
uv run --with black==22.6.0 black --check src/vision_active_learning_loop/models/rtdetr_contract.py tests/probes/test_model_contract.py
uv run --with ruff==0.16.4 ruff check src/vision_active_learning_loop/models/rtdetr_contract.py tests/probes/test_model_contract.py
git diff --check
git diff -- src/vision_active_learning_loop/models/rtdetr_contract.py tests/probes/test_model_contract.py
git add src/vision_active_learning_loop/models/rtdetr_contract.py tests/probes/test_model_contract.py
git commit -m "fix: complete RT-DETR four-class reset"
```

Expected: checks exit 0; the diff contains only the complete class reset and its tests; the commit author and committer are `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.

**Stop condition:** Any required module is unavailable, the seed-17 oracle differs, a device/dtype/dimension/bias changes, a COCO value is reused, or the exact RDD mappings differ. Do not load a model or enter Task 2 until CPU tests are green.

---

### Task 2: Complete the executable label-free and labeled model contract

**Objective:** Make the model-contract receipt prove every four-class tensor that can reach the pinned labeled loss, including decoder, denoising, and encoder auxiliaries, while binding the official loss source and exact synthetic targets.

**Files:**
- Modify: `configs/models/pinned-models.yaml`
- Modify: `fixtures/synthetic/wave0/fixture-manifest.json`
- Modify: `scripts/generate_wave0_fixtures.py`
- Modify: `src/vision_active_learning_loop/models/assets.py`
- Modify: `src/vision_active_learning_loop/models/rtdetr_contract.py`
- Modify: `src/vision_active_learning_loop/probes/model_contract.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Modify: `schemas/model-asset-receipt.schema.json`
- Modify: `schemas/model-contract-receipt.schema.json`
- Modify: `schemas/feasibility-receipt.schema.json`
- Modify: `tests/models/test_assets.py`
- Modify: `tests/artifacts/test_receipts.py`
- Modify: `tests/probes/test_model_contract.py`
- Modify: `tests/probes/test_processor_contract.py`
- Modify: `tests/probes/test_training_feasibility.py`

**Pinned normative hashes:**

- `modeling_rt_detr.py`: size 86,564; SHA-256 `fce24c79c8599e52f3648f549502879e9b396cc86f593c3a07baf10c002cead3`.
- `loss/loss_rt_detr.py`: size 22,057; SHA-256 `01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6`.
- RT-DETR source inventory including the loss file: canonical SHA-256 `8ef5c4fec87fa10ff7ab65f38ad894968f43d0a59ddb86bf8e4da1786c2fe239`.
- Existing synthetic input document remains SHA-256 `4e5eddbb21426c00932c34af331ae3e0ef3d30eb9010da7310b7319e91ec6d0f`.
- Registered synthetic target document is SHA-256 `abffd232b48a8306af8a35e6e2bce3ad0afa92f6380508f47e9c22b90e87d198`.

**Interfaces:**

```python
@dataclass(frozen=True)
class SyntheticContractFixture:
    manifest: Mapping[str, Any]
    images: Sequence[Image.Image]
    annotations: Sequence[Mapping[str, Any]]
    input_sha256: str
    target_sha256: str

@dataclass(frozen=True)
class LabeledLossCapture:
    logits: torch.Tensor
    outputs_class: torch.Tensor
    enc_topk_logits: torch.Tensor
    denoising_meta_values: Mapping[str, Any] | None
    auxiliary_outputs: Sequence[Mapping[str, torch.Tensor]]

@dataclass(frozen=True)
class LabeledContractObservation:
    loss_shape: Sequence[int]
    logits_shape: Sequence[int]
    intermediate_logits_shape: Sequence[int]
    enc_outputs_class_shape: Sequence[int]
    enc_topk_logits_shape: Sequence[int]
    decoder_auxiliary_shapes: Sequence[Sequence[int]]
    encoder_auxiliary_shapes: Sequence[Sequence[int]]
    denoising_auxiliary_shapes: Sequence[Sequence[int]]
    invariants: Mapping[str, bool]
```

Exact callable signatures:

- `load_synthetic_contract_fixture(path: Path) -> SyntheticContractFixture`
- `run_labeled_contract_forward(model: Any, *, pixel_values: torch.Tensor, pixel_mask: torch.Tensor, labels: Sequence[Mapping[str, torch.Tensor]]) -> tuple[Any, LabeledLossCapture]`
- `observe_labeled_contract(model: Any, outputs: Any, capture: LabeledLossCapture) -> LabeledContractObservation`

Extend `RawDetectorOutput` with `intermediate_logits`, `enc_outputs_class`, and `enc_topk_logits`. Extend `ModelContractReceipt` with `observed_class_modules`, `labeled_observed_shapes`, and the two new hashes `loss_source_sha256` and `synthetic_target_sha256`. Preserve the existing `run_model_contract_probe` function signature.

The asset CLI becomes:

```text
val assets verify --config configs/models/pinned-models.yaml --cache-root PATH --run-id RUN_ID --output PATH --download
```

`--run-id` is required and is stored in model-asset metadata. Model-contract input validation must use `validate_receipt_for_run()` for both environment and model-assets parents.

- [ ] **Step 1: Register the exact synthetic targets and write digest/geometry RED tests**

Add a `targets` array to the existing manifest. It contains exactly:

- fixture `wide-gradient`, image ID 1, category 0, box `[64.0, 32.0, 192.0, 96.0]`, area 18,432, `iscrowd=0`;
- fixture `tall-checker`, image ID 2, category 3, box `[32.0, 128.0, 96.0, 256.0]`, area 24,576, `iscrowd=0`.

The target hash preimage contains only `schema_version`, `fixture_set`, and `targets`. The input hash preimage contains only `schema_version`, `fixture_set`, and `images`; adding registered targets must not change the approved input digest.

Add tests that the loader rejects a target with category 4, a fixture/image mismatch, a box outside its source image, a wrong area, any extra image/target, and any digest drift. Update `_prepare_labeled_batch()` to consume only `SyntheticContractFixture.annotations`; remove its duplicate inline annotations.

Run:

```powershell
uv run pytest tests/probes/test_processor_contract.py tests/probes/test_training_feasibility.py -v -k "target or fixture or labeled_batch"
```

Expected RED: the manifest/loader does not yet expose targets or the approved target digest.

- [ ] **Step 2: Pin the official loss source and write source-inventory RED tests**

Add `loss/loss_rt_detr.py` with the exact size/hash above to `configs/models/pinned-models.yaml`, `_CANONICAL_SOURCE_FILES`, `_APPROVED_RTDETR_SOURCE_FILES`, both receipt schemas, and model-asset consistency checks. Change RT-DETR source filtering so the model-contract inventory contains the five existing `models/rt_detr/` files plus exactly `loss/loss_rt_detr.py`.

Tests must reject a missing, altered, extra, or rehashed loss source and assert the exact composite source hash `8ef5c4fec87fa10ff7ab65f38ad894968f43d0a59ddb86bf8e4da1786c2fe239`.

Run:

```powershell
uv run pytest tests/models/test_assets.py tests/artifacts/test_receipts.py tests/probes/test_model_contract.py -v -k "loss_source or source_inventory or source_sha256"
```

Expected RED: the current source allowlists and schemas omit `loss/loss_rt_detr.py`.

- [ ] **Step 3: Write label-free tensor RED tests**

Extend the fake output factory with `intermediate_logits`, `enc_outputs_class`, and `enc_topk_logits`. Test exact final class width 4 for:

- label-free `logits` `[2, 300, 4]`;
- every layer in `intermediate_logits`;
- `enc_outputs_class`;
- `enc_topk_logits` `[2, 300, 4]`.

Parameterize adversarial widths 80, 5, 3, and 1 at each reachable field. A non-four width must produce a false invariant and `FAIL`; missing tensors must raise `ContractUnavailable` and publish only a complete `FAIL` receipt.

Run:

```powershell
uv run pytest tests/probes/test_model_contract.py -v -k "intermediate_logits or enc_outputs_class or enc_topk_logits or non_four"
```

Expected RED: the current extractor neither observes nor rejects the encoder/intermediate classification tensors.

- [ ] **Step 4: Write labeled-loss capture and auxiliary RED tests**

`run_labeled_contract_forward()` temporarily wraps the model's settable `loss_function` property with the exact Transformers 5.15.0 call signature, records the tensors passed to the official function, invokes that original function once, and restores it in `finally`. It must not replace, approximate, or reimplement the loss.

The probe first completes the existing label-free call in `eval()` plus `torch.inference_mode()`. It then enters a separate forked RNG scope seeded once with the existing seed 17, switches the same reset model to `train()` so the approved denoising branch is reachable, and performs one labeled forward under `torch.no_grad()`. This second seed occurs only after the complete class reset; it cannot alter the normative replacement RNG stream. The model-contract probe does not backward or update parameters; those unchanged gates remain in feasibility.

`observe_labeled_contract()` uses `denoising_meta_values["dn_num_split"]` only to observe the exact tensor slices used by the pinned loss:

- final labeled `logits`;
- decoder auxiliaries from the non-denoising `outputs_class[:, :-1]` layers;
- the encoder auxiliary from `enc_topk_logits`;
- denoising auxiliaries from every layer of the split `dn_out_class`;
- the labeled output's `enc_outputs_class` and `enc_topk_logits`;
- scalar finite `outputs.loss`.

Add a pinned-loss AST/source-structure test that proves the official source splits `outputs_class` on dimension 2 with `dn_num_split`, constructs decoder auxiliaries, appends `enc_topk_logits`, and constructs denoising auxiliaries from `dn_out_class`. This observation helper is valid only when that source test and exact loss hash pass.

Use pure fake tensors to inject width 80 separately into decoder, encoder, and denoising paths. Assert `no_reachable_non_four_class_logits` is false for each attack. Add tests for a vector loss, NaN loss, Inf loss, missing denoising metadata, and a finite scalar loss.

Run:

```powershell
uv run pytest tests/probes/test_model_contract.py tests/artifacts/test_receipts.py -v -k "labeled or auxiliary or finite_scalar or reachable_non_four or loss_data_flow"
```

Expected RED: no labeled contract or denoising/encoder auxiliary inventory exists yet.

- [ ] **Step 5: Implement the complete observations and receipt vocabulary**

Keep the existing label-free `observed_shapes` keys and add `intermediate_logits`, `enc_outputs_class`, and `enc_topk_logits`. Add a required `labeled_observed_shapes` object with these exact keys:

```text
loss
logits
intermediate_logits
enc_outputs_class
enc_topk_logits
decoder_auxiliary_logits
encoder_auxiliary_logits
denoising_auxiliary_logits
```

The first five values are one shape array. The last three are non-empty arrays of shape arrays. Add `observed_class_modules` with:

- an ordered `decoder_class_heads` array containing path, replaced boolean, in/out features, bias presence, device, and dtype;
- one `denoising_class_embed` object containing path, replaced boolean, embedding dimension, row count, padding index, device, and dtype;
- one `encoder_score_head` object containing path, replaced boolean, in/out features, bias presence, device, and dtype;
- observed `num_labels`, `id2label`, and `label2id`.

Do not serialize Python memory addresses. `replaced` is the stable observation that pre/post module objects were not identical.

Add these required invariant names and recompute them from embedded evidence in `receipts.py` rather than trusting caller booleans:

```text
decoder_class_heads_four_channels
denoising_class_embed_five_rows_padding_four
encoder_score_head_four_channels
exact_rdd_label_mappings
class_reset_preserves_structure
four_class_reset_rng_order_seed_17
pretrained_coco_head_rows_not_reused
intermediate_logits_four_channels
enc_outputs_class_four_channels
enc_topk_logits_four_channels
decoder_auxiliary_logits_four_channels
encoder_auxiliary_logits_four_channels
denoising_auxiliary_logits_four_channels
no_reachable_non_four_class_logits
labeled_forward_finite_scalar_loss
synthetic_targets_only
label_free_model_call
labeled_model_call
```

Preserve all existing required invariants. A `PASS` still requires every old and new invariant to be literal `true`.

- [ ] **Step 6: Bind model assets and feasibility to the new run-scoped A2 parent**

Require a non-empty `run_id` in model-asset metadata and CLI input. Propagate `loss_source_sha256` and `synthetic_target_sha256` into the feasibility receipt's copied parent hash set and consistency checks. Feasibility must reject a historical model-contract receipt that lacks either A2 hash or any new required invariant, even when its old status was `PASS`.

Update all receipt fixtures and negative tests together. Schema tests must reject:

- absent loss hash, target hash, module observation, labeled shape, or invariant;
- a self-consistently rehashed 80-channel tensor;
- a finite-loss claim with a non-scalar or non-finite embedded observation;
- a source inventory without the pinned loss file;
- a model-assets parent with another run ID;
- a feasibility receipt bound to the narrower Option A model contract.

- [ ] **Step 7: Pin the completed probe implementation hash and run Task 2 GREEN verification**

After the Task 2 source is final, calculate `_probe_hash()` from the tracked implementation, write that exact lowercase value into the model-contract schema and `_APPROVED_MODEL_CONTRACT_ASSET_HASHES`, and assert equality in a test. Do not use a receipt-provided value as the expected pin.

```powershell
uv run pytest tests/models/test_assets.py tests/artifacts/test_receipts.py tests/probes/test_model_contract.py tests/probes/test_processor_contract.py tests/probes/test_training_feasibility.py -v
```

Expected GREEN: all selected CPU/source/schema tests pass; no model forward is required by this step; every adversarial non-four-class path produces `FAIL`.

- [ ] **Step 8: Format, lint, review, and commit Task 2**

```powershell
uv run --with black==22.6.0 black --check scripts/generate_wave0_fixtures.py src/vision_active_learning_loop/models/assets.py src/vision_active_learning_loop/models/rtdetr_contract.py src/vision_active_learning_loop/probes/model_contract.py src/vision_active_learning_loop/probes/training_feasibility.py src/vision_active_learning_loop/artifacts/receipts.py tests/models/test_assets.py tests/artifacts/test_receipts.py tests/probes/test_model_contract.py tests/probes/test_processor_contract.py tests/probes/test_training_feasibility.py
uv run --with ruff==0.16.4 ruff check scripts/generate_wave0_fixtures.py src/vision_active_learning_loop/models/assets.py src/vision_active_learning_loop/models/rtdetr_contract.py src/vision_active_learning_loop/probes/model_contract.py src/vision_active_learning_loop/probes/training_feasibility.py src/vision_active_learning_loop/artifacts/receipts.py tests/models/test_assets.py tests/artifacts/test_receipts.py tests/probes/test_model_contract.py tests/probes/test_processor_contract.py tests/probes/test_training_feasibility.py
git diff --check
git diff --stat
git add configs/models/pinned-models.yaml fixtures/synthetic/wave0/fixture-manifest.json scripts/generate_wave0_fixtures.py src/vision_active_learning_loop/models/assets.py src/vision_active_learning_loop/models/rtdetr_contract.py src/vision_active_learning_loop/probes/model_contract.py src/vision_active_learning_loop/probes/training_feasibility.py src/vision_active_learning_loop/artifacts/receipts.py schemas/model-asset-receipt.schema.json schemas/model-contract-receipt.schema.json schemas/feasibility-receipt.schema.json tests/models/test_assets.py tests/artifacts/test_receipts.py tests/probes/test_model_contract.py tests/probes/test_processor_contract.py tests/probes/test_training_feasibility.py
git commit -m "fix: expand Wave 0 A2 model contract"
```

Expected: only the listed A2 contract files are committed; no dependency version, model identifier, processor setting, query count, seed, or research protocol changes.

**Stop condition:** The official loss source cannot be pinned exactly, a reachable classification tensor cannot be observed/proved, labeled loss is non-scalar/non-finite, the target digest differs, any schema can accept contradictory A2 evidence, or historical evidence would need alteration.

---

### Task 3: Enforce fresh checkpoint roots and exact destinations

**Objective:** Claim each checkpoint root atomically before model/GPU work and publish the exact checkpoint destination without overwriting any file, directory, symlink, junction, or racing writer.

**Files:**
- Create: `src/vision_active_learning_loop/artifacts/no_clobber.py`
- Create: `tests/artifacts/test_no_clobber.py`
- Modify: `src/vision_active_learning_loop/training/checkpoint_io.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`
- Modify: `tests/training/test_checkpoint_io.py`
- Modify: `tests/probes/test_training_feasibility.py`

**Interfaces:**

`NoClobberError` subclasses `FileExistsError`; `NoClobberUnsupportedError` subclasses `OSError`. `StagingFile` is a mutable dataclass with `path: Path` and `handle: BinaryIO`.

Exact callable signatures:

- `create_directory_no_clobber(path: Path) -> Path`
- `open_unique_staging_file(destination: Path) -> StagingFile`
- `publish_staged_file_no_clobber(staging: Path, destination: Path) -> None`

Preserve:

`save_checkpoint_atomic(state: CheckpointState, target: Path) -> str`

`create_directory_no_clobber()` uses one `mkdir(parents=False, exist_ok=False)` call against an existing verified parent. `publish_staged_file_no_clobber()` requires a fully written regular staging file in the same verified non-link directory and creates the destination with `os.link(staging, destination, follow_symlinks=False)`. It never calls `os.replace`, never unlinks a destination, and maps unsupported safe semantics to `NoClobberUnsupportedError`.

- [ ] **Step 1: Write checkpoint-root RED tests**

Parameterize a pre-existing empty directory, non-empty directory, regular file, symlink, and Windows junction at the requested checkpoint-root path. Patch `_execute_probe` with a sentinel that fails the test if called. Invoke the feasibility CLI and assert exit 2, byte-identical pre-existing content, no output receipt, and zero probe/GPU calls.

Add a race test in which two workers call `create_directory_no_clobber()` for one root. Exactly one succeeds, one receives `NoClobberError`, and neither removes or merges the winner's root.

Run:

```powershell
uv run pytest tests/probes/test_training_feasibility.py tests/artifacts/test_no_clobber.py -v -k "checkpoint_root or directory_no_clobber"
```

Expected RED: the current CLI accepts a non-link existing checkpoint directory and `_execute_probe()` uses `exist_ok=True`.

- [ ] **Step 2: Write exact-destination and adversarial checkpoint RED tests**

Pre-create `step-000001.pt` as a file, directory, symlink, and junction; call `save_checkpoint_atomic()` and assert the target is unchanged. Add two-writer concurrency with distinct valid checkpoint states: exactly one destination is published, it verifies as one complete state, and the loser cannot replace it. Simulate `EPERM`, `EOPNOTSUPP`, `ENOTSUP`, and `EXDEV` from `os.link` and assert fail-closed behavior with destination absent.

Run:

```powershell
uv run pytest tests/training/test_checkpoint_io.py tests/artifacts/test_no_clobber.py -v -k "no_clobber or preexisting or race or unsupported"
```

Expected RED: `save_checkpoint_atomic()` currently replaces an existing target.

- [ ] **Step 3: Implement root claim before execution and no-clobber checkpoint publication**

In the feasibility CLI, after canonical path resolution and before reading the model-contract receipt or calling `_execute_probe()`, atomically create the checkpoint root. Preserve that claimed root on every later success or failure as evidence; never clean it or retry with the same path.

Remove `checkpoint_root.mkdir(parents=True, exist_ok=True)` from `_execute_probe()`. Require the newly claimed root to exist as a non-link directory. Save the checkpoint into a unique exclusive staging file, flush and fsync it, hash the complete staged bytes, fsync the parent, and make `os.link` the decisive destination-creation operation. Staging cleanup is best-effort and can never delete or alter the committed destination.

- [ ] **Step 4: Run Task 3 GREEN verification**

```powershell
uv run pytest tests/artifacts/test_no_clobber.py tests/training/test_checkpoint_io.py tests/probes/test_training_feasibility.py -v
```

Expected GREEN: all checkpoint success, corruption, resume, pre-existing-path, race, link/junction, and unsupported-filesystem tests pass; no CUDA model is executed.

- [ ] **Step 5: Format, lint, review, and commit Task 3**

```powershell
uv run --with black==22.6.0 black --check src/vision_active_learning_loop/artifacts/no_clobber.py src/vision_active_learning_loop/training/checkpoint_io.py src/vision_active_learning_loop/probes/training_feasibility.py tests/artifacts/test_no_clobber.py tests/training/test_checkpoint_io.py tests/probes/test_training_feasibility.py
uv run --with ruff==0.16.4 ruff check src/vision_active_learning_loop/artifacts/no_clobber.py src/vision_active_learning_loop/training/checkpoint_io.py src/vision_active_learning_loop/probes/training_feasibility.py tests/artifacts/test_no_clobber.py tests/training/test_checkpoint_io.py tests/probes/test_training_feasibility.py
git diff --check
git add src/vision_active_learning_loop/artifacts/no_clobber.py src/vision_active_learning_loop/training/checkpoint_io.py src/vision_active_learning_loop/probes/training_feasibility.py tests/artifacts/test_no_clobber.py tests/training/test_checkpoint_io.py tests/probes/test_training_feasibility.py
git commit -m "fix: enforce fresh Wave 0 checkpoints"
```

Expected: one scoped checkpoint/no-clobber commit with exact author/committer identity.

**Stop condition:** Any pre-existing root/destination is accepted, any target can be overwritten, an unsupported filesystem degrades to overwrite semantics, the root is created after GPU work begins, or a failure cleans prior evidence.

---

### Task 4: Publish receipts with atomic destination creation

**Objective:** Replace check-then-`os.replace` receipt publication with a same-directory, complete, fsynced staging artifact and an atomic no-clobber destination creation that behaves safely on Windows and Linux.

**Files:**
- Modify: `src/vision_active_learning_loop/artifacts/no_clobber.py`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Modify: `tests/artifacts/test_no_clobber.py`
- Modify: `tests/artifacts/test_receipts.py`

**Interface:** Preserve `atomic_write_receipt(path: Path, receipt: Mapping[str, object]) -> str`. It now raises `NoClobberError` for any existing destination and `NoClobberUnsupportedError` when the filesystem cannot guarantee atomic create-if-absent semantics.

- [ ] **Step 1: Write direct publication RED tests**

Add tests that a valid receipt cannot replace an existing valid receipt, invalid receipt, empty file, directory, symlink, or junction. Hash/byte-compare every pre-existing destination after the rejected call. Assert the publisher requires an existing non-link parent and leaves no final receipt when validation, write, fsync, or publication fails.

Run:

```powershell
uv run pytest tests/artifacts/test_receipts.py -v -k "existing or no_clobber or symlink or junction"
```

Expected RED: the current `os.replace(partial, target)` overwrites a regular destination.

- [ ] **Step 2: Write same-destination race and incomplete-staging RED tests**

Create two different valid receipts with distinct run IDs and synchronize two worker processes immediately before publication. Assert exactly one call succeeds, one raises `NoClobberError`, the final bytes are one complete schema-valid receipt, its content hash matches, and no `.partial` or `.staging` file is interpreted as current evidence.

Inject short write, file fsync failure, parent fsync failure, hard-link failure, and stage cleanup failure. Publication before the decisive link must leave no destination. Cleanup failure after successful link must not invalidate or remove the complete destination.

- [ ] **Step 3: Add explicit Windows and Linux contract tests**

In `tests/artifacts/test_no_clobber.py` add:

- an NTFS test guarded by `os.name == "nt"` that uses real `os.link`, verifies existing destination refusal, and covers a junction parent;
- a Linux test guarded by `sys.platform.startswith("linux")` that uses real `os.link`, verifies existing destination refusal, and covers a symlink parent;
- platform-independent injected-error tests for `EPERM`, `EOPNOTSUPP`, `ENOTSUP`, and `EXDEV`.

The Windows test runs during Task 5 local verification. The Linux test runs inside every Task 6 OCI attempt. A platform-specific skip is acceptable only for the opposite platform; the active platform's test must pass.

- [ ] **Step 4: Implement complete staging and decisive no-clobber publication**

`atomic_write_receipt()` must:

1. deep-copy, validate, content-hash, and serialize the receipt before opening a stage;
2. require an existing verified non-link parent;
3. create a UUID-named same-directory staging file with exclusive creation;
4. write the canonical UTF-8 bytes plus final newline, flush, and fsync;
5. re-read, hash, and schema-validate the staged document;
6. fsync the parent before publication;
7. call `publish_staged_file_no_clobber()` so `os.link` atomically creates the absent destination;
8. never perform a fallible mutation of the destination after successful publication;
9. best-effort remove only its own unique stage.

An early `path.exists()` check may remain only as a fast rejection; it is not the safety mechanism. `os.replace` is forbidden in receipt and checkpoint publication.

- [ ] **Step 5: Run Task 4 GREEN verification on Windows**

```powershell
uv run pytest tests/artifacts/test_no_clobber.py tests/artifacts/test_receipts.py tests/models/test_assets.py tests/probes/test_model_contract.py tests/probes/test_training_feasibility.py -v
```

Expected GREEN: the Windows real-filesystem test passes, the Linux real-filesystem test alone is skipped, all race/failure tests pass, and no existing receipt can be changed.

- [ ] **Step 6: Format, lint, review, and commit Task 4**

```powershell
uv run --with black==22.6.0 black --check src/vision_active_learning_loop/artifacts/no_clobber.py src/vision_active_learning_loop/artifacts/receipts.py tests/artifacts/test_no_clobber.py tests/artifacts/test_receipts.py
uv run --with ruff==0.16.4 ruff check src/vision_active_learning_loop/artifacts/no_clobber.py src/vision_active_learning_loop/artifacts/receipts.py tests/artifacts/test_no_clobber.py tests/artifacts/test_receipts.py
git diff --check
git add src/vision_active_learning_loop/artifacts/no_clobber.py src/vision_active_learning_loop/artifacts/receipts.py tests/artifacts/test_no_clobber.py tests/artifacts/test_receipts.py
git commit -m "fix: publish Wave 0 artifacts without clobber"
```

Expected: one scoped publication commit; old receipt files outside Git remain untouched.

**Stop condition:** Publication depends on check-then-replace, a race can overwrite the winner, a partial/stage can become current evidence, active-platform semantics are untested, or unsupported semantics do not fail closed.

---

### Task 5: Prepare the existing Wave 0 replay gate and complete local review

**Objective:** Finish the already-approved baseline aggregate gate, verify the complete A2 implementation locally without GPU/Docker execution, preserve all historical hashes, and establish a clean source-review checkpoint before runtime work.

**Files:**
- Create: `src/vision_active_learning_loop/gates/__init__.py`
- Create: `src/vision_active_learning_loop/gates/wave0.py`
- Create: `schemas/wave0-gate-receipt.schema.json`
- Create: `tests/gates/test_wave0_gate.py`
- Create: `scripts/run_wave0_clean.ps1`
- Create: `scripts/run_wave0_clean.sh`
- Create: `docs/runbooks/wave0.md`
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Modify: `tests/artifacts/test_receipts.py`

These files are the unfinished Task 6 files from the approved baseline plan. They add no new research behavior; they only orchestrate and aggregate the unchanged Wave 0 checks for the fresh A2 replay.

**Interfaces:**

```python
@dataclass(frozen=True)
class ReplayReceiptPaths:
    environment: Path
    model_assets: Path
    model_contract: Path
    feasibility_a: Path
    feasibility_b: Path

@dataclass(frozen=True)
class Wave0Inputs:
    run_id: str
    primary: ReplayReceiptPaths
    clean_a: ReplayReceiptPaths
    clean_b: ReplayReceiptPaths

@dataclass(frozen=True)
class Wave0GateReceipt:
    run_id: str
    parent_receipts: Mapping[str, Mapping[str, str]]
    deterministic_comparisons: Mapping[str, str]
    invariants: Mapping[str, bool]
    errors: Sequence[str]
```

Exact callable signatures:

- `Wave0GateReceipt.as_dict(self) -> dict[str, object]`
- `evaluate_wave0(inputs: Wave0Inputs) -> Wave0GateReceipt`

CLI:

```text
val gate wave0 --run-id RUN_ID --primary-root PATH --clean-a-root PATH --clean-b-root PATH --output PATH
```

Script interfaces:

```text
powershell -File scripts/run_wave0_clean.ps1 -RunId RUN_ID -AttemptId primary -ImageTag IMAGE_TAG -ImageDigest IMAGE_DIGEST -HostArtifactRoot PATH
bash scripts/run_wave0_clean.sh --run-id RUN_ID --attempt-id clean-a --image-tag IMAGE_TAG --image-digest IMAGE_DIGEST --host-artifact-root PATH
```

`AttemptId` is exactly one of `primary`, `clean-a`, or `clean-b`. Each script atomically creates one absent attempt root, creates an empty uv cache and empty model cache, runs environment, model assets, model contract, feasibility A, and feasibility B serially, records every command/exit/hash, and never retries or removes an attempt root.

- [ ] **Step 1: Write aggregate-gate RED tests**

Create schema-valid parent fixtures for one primary and two clean attempts. Parameterize every parent receipt and every old/new invariant as the single failed input. Add tests for:

- missing or different run IDs;
- wrong environment/model-contract/feasibility parent content hashes;
- missing loss-source or synthetic-target hashes;
- A/B deterministic comparison divergence;
- clean-a/clean-b normative divergence;
- `VAL_DATA_ROOT` present in any attempt;
- an existing output destination;
- a narrower historical model-contract receipt;
- an attempted Wave 1 capability or command.

Run:

```powershell
uv run pytest tests/gates/test_wave0_gate.py -v
```

Expected RED: the gate package and schema do not exist.

- [ ] **Step 2: Implement the fail-closed aggregate and schema**

`evaluate_wave0()` must validate every parent schema/content hash, require the same non-empty A2 run ID in all environment/model-asset/model-contract/feasibility metadata, verify the exact environment→model-contract→feasibility bindings in each chain, and compare only registered normative deterministic fields. Timestamps, container IDs, attempt paths, receipt content hashes, and runtime durations remain observational and may differ.

Required gate invariants are:

```text
primary_complete_pass
clean_a_complete_pass
clean_b_complete_pass
all_run_ids_match
all_parent_bindings_match
loss_source_hash_matches
synthetic_target_hash_matches
all_classification_tensors_four_channels
labeled_losses_finite_scalar
bf16_backward_passed
finite_gradients_passed
parameter_update_passed
vram_limit_passed
checkpoint_round_trips_passed
feasibility_ab_deterministic
clean_replays_deterministic
data_root_unset
fresh_evidence_chain
historical_evidence_not_used
```

A `PASS` gate receipt creates no Wave 1 capability and starts no Wave 1 process. The only success interpretation is `WAVE0_A2_PASS / WAVE1_NOT_STARTED`.

- [ ] **Step 3: Implement and test equivalent PowerShell/Bash orchestration**

Both scripts must:

- reject set `VAL_DATA_ROOT`;
- reject an existing attempt root by atomic directory creation;
- reject an existing receipt/checkpoint root/destination;
- mount the worktree read-only and only the new attempt artifact root read-write;
- use official-network access only for the pinned asset download phase, then `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and `--network none` for model contract and feasibility;
- pass the same run ID and new OCI image identity into every receipt;
- run feasibility A and B with distinct fresh checkpoint roots/destinations;
- capture command argv, exit code, image/container inspect, receipt hash, checkpoint hash, disk bytes, runtime, and `VAL_DATA_ROOT` absence;
- preserve the entire attempt on the first nonzero exit and stop without launching the next phase.

Add AST/text tests that PowerShell and Bash enumerate the same five receipt stages, never mention a Wave 1 command, never mount a data root, never use an overwrite flag, and never remove an evidence root.

- [ ] **Step 4: Run focused gate GREEN tests and commit replay support**

```powershell
uv run pytest tests/gates/test_wave0_gate.py tests/artifacts/test_receipts.py tests/cli/test_cli.py -v
uv run --with black==22.6.0 black --check src/vision_active_learning_loop/gates/__init__.py src/vision_active_learning_loop/gates/wave0.py src/vision_active_learning_loop/artifacts/receipts.py tests/gates/test_wave0_gate.py tests/artifacts/test_receipts.py
uv run --with ruff==0.16.4 ruff check src/vision_active_learning_loop/gates/__init__.py src/vision_active_learning_loop/gates/wave0.py src/vision_active_learning_loop/artifacts/receipts.py tests/gates/test_wave0_gate.py tests/artifacts/test_receipts.py
git diff --check
git add src/vision_active_learning_loop/gates/__init__.py src/vision_active_learning_loop/gates/wave0.py src/vision_active_learning_loop/artifacts/receipts.py schemas/wave0-gate-receipt.schema.json tests/gates/test_wave0_gate.py tests/artifacts/test_receipts.py scripts/run_wave0_clean.ps1 scripts/run_wave0_clean.sh docs/runbooks/wave0.md
git commit -m "feat: prepare Wave 0 A2 replay gate"
```

Expected: focused tests and touched-file checks pass; one scoped baseline-replay commit is created; no runtime evidence or host path is tracked.

- [ ] **Step 5: Verify the registered eleven receipts and Option A failure evidence before any runtime action**

Read `$VAL_ARTIFACT_ROOT/wave0/builds/task5-option-a-20260824T134408p0800-boundary-replay/08-pre-existing-receipt-preservation.json`. Require `receipt_count == 11`, `all_unchanged == true`, and independently re-hash every listed receipt path; every current length/hash must equal the recorded values.

Independently require:

- Option A failure record stored SHA-256 `ef6f55609f6a6db0281206c8e434c39fa3407399bc7c7f0db4312c5293677507`;
- its embedded content SHA-256 `0896d4edcfd281749dfd04215cb09ae518e74d39645ec61b08c5792607778122`;
- Option A evidence-manifest SHA-256 `be98fcb8dcab91384f192bb42fd1fdad91a970d55be6e155be5ee2d97a7252df`;
- archived pre-hardening receipt SHA-256 `a9261e378d137b93ecbf8d9c1b2f9ca3ff32f10673b7ee6bae0294aeb351143e`;
- prior Option A image ID `sha256:558a468b2bcb1a96a9198fb35a1590e57c376e5a7e6ac5032b3cdff44bbaacc9` remains inspectable and is not retagged or deleted.

Expected: every value is unchanged. Any mismatch stops with `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN`; do not repair or regenerate historical evidence.

- [ ] **Step 6: Run targeted and full local verification**

```powershell
uv --version
uv lock --check
uv run pytest tests/probes/test_model_contract.py tests/probes/test_processor_contract.py tests/models/test_assets.py tests/artifacts/test_no_clobber.py tests/artifacts/test_receipts.py tests/training/test_checkpoint_io.py tests/probes/test_training_feasibility.py tests/gates/test_wave0_gate.py -v
uv run pytest -v
```

Expected:

- uv reports `0.8.15` and lock check exits 0 without changing `uv.lock`;
- all collected tests pass;
- only the Linux real-filesystem no-clobber test and already-registered unavailable-platform tests may skip on Windows;
- no CUDA model forward, Docker build, or container run occurs.

- [ ] **Step 7: Run touched-file format/lint, schema, source/hash, and public-boundary checks**

Run Black and Ruff only over the Python files in the A2 file map. Then run:

```powershell
Get-ChildItem schemas -Filter *.json | ForEach-Object { .venv\Scripts\python.exe -m json.tool $_.FullName > $null; if ($LASTEXITCODE -ne 0) { throw "invalid schema: $($_.Name)" } }
$LossSource = '.venv\Lib\site-packages\transformers\loss\loss_rt_detr.py'
$LossHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $LossSource).Hash.ToLowerInvariant()
if ($LossHash -ne '01c6fe0bdc5965ccf71e7eabfc98a3d05101300bc69dc1773ae3f58ebd7d02e6') { throw "pinned loss source hash mismatch" }
git diff --check
git status --short
git ls-files | ForEach-Object { $item = Get-Item -LiteralPath $_; if ($item.Length -gt 5242880) { $item.FullName } }
git ls-files | Select-String -Pattern '\.(pt|pth|ckpt|safetensors|onnx|zip|7z|tar|npy|npz|parquet)$'
$SecretPattern = ('gh' + 'p_[A-Za-z0-9]+|github_' + 'pat_[A-Za-z0-9_]+|h' + 'f_[A-Za-z0-9]{20,}|A' + 'KIA[0-9A-Z]{16}|BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY')
git grep -n -I -E $SecretPattern
$PrivatePathPattern = ('[A-Za-z]:' + '\\' + 'Users' + '\\' + '|/m' + 'nt/[a-z]/|/ho' + 'me/[^/]+/|/Us' + 'ers/[^/]+')
git grep -n -I -E $PrivatePathPattern
git remote -v
```

Expected:

- every schema parses;
- `git diff --check` exits 0;
- tracked files over 5 MiB: zero;
- model/data/checkpoint suffix matches: zero;
- credential/private-key matches: zero;
- private host-path matches: zero;
- remotes: zero;
- worktree is clean after the five scoped implementation commits.

- [ ] **Step 8: Establish the clean review checkpoint**

```powershell
git log --format="%H %an <%ae> %cn <%ce> %s" --reverse b178233537fc1e1168ec028b54970065a045904b..HEAD
git status --short
git -C ..\.. status --short
git rev-parse HEAD
```

Expected: exactly the scoped implementation/replay commits from Tasks 1–5, all with the approved author/committer; implementation worktree and canonical main are clean. Record this SHA as the source-review checkpoint and stop for code review if any finding remains. Do not amend or rewrite a commit.

**Stop condition:** A local test, targeted formatter/linter, schema/hash scan, history hash, author identity, source boundary, or cleanliness check fails. No GPU or Docker work may begin from a dirty or unreviewed checkpoint.

---

### Task 6: Execute a fresh Wave 0 A2 primary chain, clean replays, and aggregate gate

**Objective:** Build a new immutable OCI image from the clean reviewed source, run the full unchanged Wave 0 contract in one primary attempt and two clean attempts under a fresh run ID, aggregate the evidence, and stop before Wave 1.

**Repository files changed:** None. All commands in this task create only external run-scoped artifacts, OCI image/container records, and receipts. Any source/test issue discovered here is a normative failure; do not patch or rebuild within the same run ID.

**Evidence layout:**

```text
$VAL_ARTIFACT_ROOT/wave0/a2-runs/RUN_ID/
  primary/wave0/receipts/
  primary/wave0/checkpoints/
  primary/wave0/model_cache/
  clean-a/wave0/receipts/
  clean-a/wave0/checkpoints/
  clean-a/wave0/model_cache/
  clean-b/wave0/receipts/
  clean-b/wave0/checkpoints/
  clean-b/wave0/model_cache/
  gate/wave0-gate-receipt.json
  audit/
```

`RUN_ID` in this layout means the concrete value generated once by the command below; it is not edited by hand and is identical in every A2 receipt.

- [ ] **Step 1: Generate one fresh identity and atomically claim the campaign root**

```powershell
if (Test-Path Env:VAL_DATA_ROOT) { throw "VAL_DATA_ROOT must remain unset" }
$A2RunId = "wave0-a2-" + [DateTimeOffset]::UtcNow.ToString("yyyyMMddTHHmmssfffZ")
$A2CampaignRoot = Join-Path $env:VAL_ARTIFACT_ROOT "wave0/a2-runs/$A2RunId"
New-Item -ItemType Directory -Path $A2CampaignRoot -ErrorAction Stop | Out-Null
$A2SourceSha = (git rev-parse HEAD).Trim()
$A2ImageTag = "vision-active-learning-loop:wave0-a2-$($A2SourceSha.Substring(0,12))-$A2RunId"
```

Expected: `VAL_DATA_ROOT` is absent; the run ID is new; the single atomic directory creation succeeds; no path from any earlier run is reused. If the root already exists, stop and generate no replacement ID during this execution attempt.

- [ ] **Step 2: Acquire the project GPU lease and run the preflight**

Atomically create `$VAL_ARTIFACT_ROOT/wave0/leases/$A2RunId`, record `nvidia-smi`, Docker GPU visibility, process inventory, free VRAM, and selected RTX 4090 identity. Do not terminate or alter another process. If another formal workload is active or the approved lease cannot be acquired, preserve the preflight and stop without building/running the probe.

```powershell
nvidia-smi
docker run --rm --gpus all --network none nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356 nvidia-smi
```

Expected: one visible `NVIDIA GeForce RTX 4090`, adequate free VRAM, no conflicting compute workload, and the exclusive project lease held.

- [ ] **Step 3: Build and record a new OCI image identity without touching the old image**

```powershell
docker image inspect $A2ImageTag 2>$null
if ($LASTEXITCODE -eq 0) { throw "fresh image tag already exists" }
docker build --no-cache --pull=false --label "org.opencontainers.image.revision=$A2SourceSha" --label "org.opencontainers.image.ref.name=$A2RunId" -f docker/wave0.Dockerfile -t $A2ImageTag .
$A2ImageDigest = (docker image inspect --format '{{.Id}}' $A2ImageTag).Trim()
if ($A2ImageDigest -eq 'sha256:558a468b2bcb1a96a9198fb35a1590e57c376e5a7e6ac5032b3cdff44bbaacc9') { throw "A2 image identity reused Option A" }
docker image inspect vision-active-learning-loop:wave0-option-a-97d5789 > $null
```

Expected: build uses the unchanged pinned base digest, produces a new image ID bound to the clean review SHA, and the old Option A image remains inspectable and unchanged. Record the new tag, ID, base digest, source SHA, and full inspect hash below the new campaign audit root.

- [ ] **Step 4: Execute the primary A2 chain serially**

```powershell
powershell -File scripts/run_wave0_clean.ps1 -RunId $A2RunId -AttemptId primary -ImageTag $A2ImageTag -ImageDigest $A2ImageDigest -HostArtifactRoot $A2CampaignRoot
```

Expected sequence and gates:

1. fresh environment receipt PASS with exact Python/uv/SciPy/torch/torchvision/Transformers/pycocotools/CUDA/base/runtime image/RTX identity;
2. fresh run-scoped model-assets receipt PASS with pinned model/revision/license/source hashes;
3. complete A2 model-contract PASS for label-free and labeled paths, finite scalar loss, target digest, loss-source hash, and no reachable non-four-class tensor;
4. feasibility A PASS with BF16 forward/backward, finite loss/gradients, parameter update, TF32 disabled, deterministic algorithms, peak allocated VRAM at most 22 GiB, and verified fresh checkpoint round-trip;
5. feasibility B PASS under a distinct fresh checkpoint root with the same normative deterministic comparison.

At the first nonzero exit, preserve the attempt root, logs, receipts/stages, container/image identity, checkpoint-root state, and error; release the GPU lease; emit `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN`; do not launch clean-a.

- [ ] **Step 5: Execute clean-a and clean-b from empty caches and new containers**

```powershell
powershell -File scripts/run_wave0_clean.ps1 -RunId $A2RunId -AttemptId clean-a -ImageTag $A2ImageTag -ImageDigest $A2ImageDigest -HostArtifactRoot $A2CampaignRoot
powershell -File scripts/run_wave0_clean.ps1 -RunId $A2RunId -AttemptId clean-b -ImageTag $A2ImageTag -ImageDigest $A2ImageDigest -HostArtifactRoot $A2CampaignRoot
```

Expected: both atomically claim previously absent roots, use distinct empty uv/model caches and new containers, independently rerun environment/assets/complete A2 contract/feasibility A/B, pass the Linux no-clobber filesystem test, and preserve exact parent/run bindings. No RDD/data mount or `VAL_DATA_ROOT` appears. Clean-b starts only after clean-a passes.

If either clean attempt fails, preserve it and stop with `WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN`. Do not retry the failed attempt or reuse `$A2RunId`.

- [ ] **Step 6: Publish the aggregate gate receipt with no-clobber semantics**

Atomically create the new gate directory, then run the gate inside the A2 image with network disabled, worktree read-only, and only the A2 campaign root read-write:

```powershell
$A2GateDirectory = Join-Path $A2CampaignRoot "gate"
New-Item -ItemType Directory -Path $A2GateDirectory -ErrorAction Stop | Out-Null
docker run --rm --network none --entrypoint val -e "VAL_ARTIFACT_ROOT=/artifacts" -e "A2_RUN_ID=$A2RunId" -v "$($PWD.Path):/workspace:ro" -v "$($env:VAL_ARTIFACT_ROOT):/artifacts:rw" $A2ImageTag gate wave0 --run-id $A2RunId --primary-root "/artifacts/wave0/a2-runs/$A2RunId/primary" --clean-a-root "/artifacts/wave0/a2-runs/$A2RunId/clean-a" --clean-b-root "/artifacts/wave0/a2-runs/$A2RunId/clean-b" --output "/artifacts/wave0/a2-runs/$A2RunId/gate/wave0-gate-receipt.json"
```

Expected: receipt publication succeeds only once; every parent status/hash/run binding and every unchanged gate is true; deterministic comparisons match across primary A/B and clean-a/clean-b; gate status is `PASS`. No capability file or Wave 1 command is created.

- [ ] **Step 7: Verify final evidence preservation, repository state, and terminal verdict**

Re-run the eleven-receipt and Option A evidence hash checks from Task 5. Hash every new A2 receipt/checkpoint/audit record and verify the gate receipt with `validate_receipt_for_run()`. Inspect Git without modifying it:

```powershell
git status --short
git -C ..\.. status --short
git remote -v
docker ps --filter "name=val-" --format '{{.ID}} {{.Names}} {{.Status}}'
```

Expected:

- implementation worktree clean;
- canonical main clean;
- no remote;
- no A2 task container left running;
- GPU lease released with a recorded release receipt;
- all historical hashes unchanged;
- A2 image retained under its unique tag/identity;
- no RDD, `VAL_DATA_ROOT`, Wave 1, push, merge, tag, Release, or publication action.

If the aggregate receipt is `PASS`, the only legal endpoint is:

```text
WAVE0_A2_PASS / WAVE1_NOT_STARTED
```

For any normative, provenance, deterministic, storage, or preservation failure, the only legal endpoint is:

```text
WAVE0_A2_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

**Stop condition:** Any failure immediately freezes the fresh evidence chain. Do not patch source, change model/package/hardware, weaken a gate, clean an evidence path, rerun with the same run ID, or enter Wave 1.

## Plan author self-review

- A2 spec coverage: PASS. Complete reset, both execution paths, loss/source/target evidence, no-clobber findings, unchanged downstream gates, and fresh replay are mapped to Tasks 1–6.
- Exact module paths: PASS. Decoder, denoising, and encoder paths are named and tested directly.
- RNG order: PASS. One seed-17 stream and decoder-index → denoising → encoder order have an independent test oracle.
- Labeled-loss data flow: PASS. Capture observes the arguments used by official Transformers 5.15.0 and is bound to the pinned loss AST/hash.
- Receipt schema/type consistency: PASS. New hashes, module observations, labeled shapes, run identity, feasibility propagation, negative tests, and compiled evidence checks are paired.
- Checkpoint/receipt atomicity: PASS. Root claim uses atomic directory creation; file publication uses same-directory exclusive staging plus atomic hard-link destination creation; overwrite and unsupported semantics fail closed.
- Windows/Linux semantics: PASS. Active-platform real-filesystem tests plus injected unsupported-error tests are mandatory; opposite-platform tests run in Task 6 OCI.
- Evidence preservation: PASS. The eleven registered receipts, archived receipt, Option A failure record/content hash/evidence manifest, and prior OCI image are explicitly reverified before and after runtime work.
- Fresh-run identity: PASS. One generated A2 run ID, new campaign/attempt/checkpoint/receipt paths, new image identity, and exact parent bindings are required.
- Wave 1 prohibition: PASS. A PASS receipt creates no capability and the plan stops at `WAVE0_A2_PASS / WAVE1_NOT_STARTED`.
- Research scope: PASS. Models, revisions, processor, queries, dependencies, datasets, seeds, arms, budgets, gates, and 9/66/6 fit counts are unchanged.
- Ambiguity and scope drift scan: PASS. Every task has exact files, interfaces, RED/GREEN commands, expected results, commit boundaries, evidence, and stop conditions; no broad formatting, cleanup, remote, or publication action is authorized.
