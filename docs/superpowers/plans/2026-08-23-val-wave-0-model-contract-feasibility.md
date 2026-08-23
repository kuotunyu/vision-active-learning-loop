# Wave 0 Model Contract Feasibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove, using synthetic inputs only, that the pinned Windows/WSL2/CUDA/model stack satisfies every executable RT-DETR and deterministic-training invariant before any RDD access.

**Architecture:** Canonical execution uses a digest-pinned OCI image inside WSL2 with the Windows RTX driver exposed through NVIDIA Container Toolkit. A `val probe model-contract` CLI generates schema-validated receipts from two synthetic images; a separate feasibility smoke performs one training step and checkpoint round-trip. A single fail-closed wave gate accepts receipts from two clean environments or blocks Wave 1.

**Tech Stack:** Python 3.12.11; uv 0.8.15 lock workflow; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; safetensors; pytest; JSON Schema; CUDA 12.6; RTX 4090 24 GB; WSL2 Ubuntu 24.04; OCI.

## Global Constraints

- Do not download, extract, scan, or process any RDD archive in this wave.
- Use only `PekingU/rtdetr_r18vd` revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d` and `facebook/dinov2-small` revision `ed25f3a31f01632728cabb09d1542f84ab7b0056`.
- RT-DETR and DINOv2 safetensors SHA-256 values must match the approved spec exactly.
- The probe batch is two original synthetic RGB images sized 320×640 and 640×320 before preprocessing.
- Canonical evidence requires RTX 4090, TF32 disabled, deterministic algorithms enabled, and BF16 feasibility.
- Any normative invariant failure produces `FAIL`, prevents Wave 1, and requires owner/design review. Do not substitute a model, package, query contract, or preprocessing rule.
- Network access is allowlisted to official Python/package, NVIDIA container, and pinned Hugging Face model endpoints.
- Every runtime output resolves below the environment-provided logical root `VAL_ARTIFACT_ROOT`: receipts under `wave0/receipts/`, model cache under `wave0/model_cache/`, temporary checkpoints under `wave0/checkpoints/`, and clean attempts under `wave0/clean-runs/`. Tracked configuration must not contain a machine-specific absolute path.
- `VAL_DATA_ROOT` must remain unset and must not be created, searched, or mounted in Wave 0.

---

### Task 1: Lock the canonical environment and compatibility decision

**Objective:** Create the minimum package/runtime skeleton and a machine-readable compatibility matrix that selects WSL2/OCI for canonical work and limits native Windows to CPU compatibility checks.

**Files:**
- Create: `.python-version`
- Create: `pyproject.toml`
- Create: `uv.lock`
- Create: `docker/wave0.Dockerfile`
- Create: `configs/environment/wave0.yaml`
- Create: `src/vision_active_learning_loop/__init__.py`
- Create: `src/vision_active_learning_loop/cli.py`
- Create: `src/vision_active_learning_loop/cli_manifest.py`
- Create: `src/vision_active_learning_loop/environment.py`
- Create: `tests/cli/test_cli.py`
- Create: `tests/environment/test_compatibility.py`
- Create: `docs/environment-boundary.md`

**Interfaces:**
- Produces: `EnvironmentContract.from_yaml(path: Path) -> EnvironmentContract`
- Produces: `EnvironmentContract.validate(observed: Mapping[str, object]) -> list[str]`
- Produces console entry point: `[project.scripts] val = "vision_active_learning_loop.cli:main"`
- Produces: `@command("group action")` metadata consumed by the AST-built lazy CLI manifest; command modules are imported only when selected.
- Produces CLI: `python -m vision_active_learning_loop.environment check --config configs/environment/wave0.yaml --output <receipt.json>`
- Receipt keys: `schema_version`, `python`, `torch`, `torchvision`, `transformers`, `cuda_runtime`, `gpu_name`, `gpu_uuid`, `driver`, `os`, `wsl`, `container_image_digest`, `tf32`, `deterministic_algorithms`, `status`, `errors`.

- [ ] **Step 1: Write the failing compatibility tests**

```python
def test_contract_rejects_native_windows_as_canonical(contract):
    errors = contract.validate({"os": "Windows", "wsl": False, "gpu_name": "NVIDIA GeForce RTX 4090"})
    assert "canonical execution requires WSL2/OCI" in errors

def test_contract_accepts_exact_core_versions(contract, canonical_observation):
    assert contract.validate(canonical_observation) == []

def test_cli_manifest_is_lazy_and_rejects_duplicate_paths(tmp_path):
    manifest = build_manifest(tmp_path / "src")
    assert "vision_active_learning_loop.evaluation" not in sys.modules
    with pytest.raises(DuplicateCommandError):
        manifest.add("probe model-contract", "duplicate.module:main")
```

- [ ] **Step 2: Run the focused tests and verify the red state**

Run: `uv run pytest tests/environment/test_compatibility.py tests/cli/test_cli.py -v`

Expected: collection fails because `vision_active_learning_loop.environment` does not exist.

- [ ] **Step 3: Add the exact lock inputs and validator**

Set Python `==3.12.11`, torch `==2.12.0+cu126`, torchvision `==0.27.0+cu126`, Transformers `==5.15.0`, and pycocotools `==2.0.10`. Configure uv’s PyTorch index for CUDA 12.6 and generate `uv.lock`; `uv lock --check` must later reject drift. Use `nvidia/cuda:12.6.3-cudnn-runtime-ubuntu24.04` as the requested base tag, resolve it to a digest, and record the digest in the environment receipt. If the tag cannot be resolved or the compatibility matrix does not support the exact core versions, stop with `OWNER_DECISION_REQUIRED`; do not choose another base or core version.

Add the `val` entry point and AST-built lazy command manifest. A command module declares `@command("group action")`; manifest generation records module/callable without importing it, so trainer images do not import evaluator modules. Duplicate command paths or a missing callable fail the build.

Implement the validator with exact comparisons:

```python
@dataclass(frozen=True)
class EnvironmentContract:
    python: str
    torch: str
    torchvision: str
    transformers: str
    cuda_runtime: str
    canonical_os: str = "Linux"
    requires_wsl: bool = True
    gpu_name: str = "NVIDIA GeForce RTX 4090"
```

- [ ] **Step 4: Verify lock and compatibility behavior**

Run: `uv lock --check && uv run pytest tests/environment/test_compatibility.py tests/cli/test_cli.py -v`

Expected: lock check exits 0; compatibility and lazy-manifest tests pass, including duplicate-path rejection without importing evaluator modules.

- [ ] **Step 5: Produce environment-boundary evidence**

Run: `uv run python -m vision_active_learning_loop.environment check --config configs/environment/wave0.yaml --output "$VAL_ARTIFACT_ROOT/wave0/receipts/environment-receipt.json"`

Expected: on canonical WSL2/OCI, JSON status is `PASS`; on native Windows canonical mode, command exits 2 and status is `FAIL` without creating a success marker.

**Artifact/evidence produced:** `environment-receipt.json`, `uv.lock`, image digest, compatibility table, and native-Windows rejection test.

**Stop condition:** Any exact core wheel, CUDA, WSL2 GPU, or base-image digest cannot be validated.

**Commit boundary:** `chore: lock wave zero runtime`

---

### Task 2: Implement content hashing and receipt validation primitives

**Objective:** Make every Wave 0 observation content-addressed and schema-validated before model-specific work.

**Files:**
- Create: `src/vision_active_learning_loop/artifacts/digests.py`
- Create: `src/vision_active_learning_loop/artifacts/receipts.py`
- Create: `schemas/model-contract-receipt.schema.json`
- Create: `schemas/feasibility-receipt.schema.json`
- Create: `tests/artifacts/test_digests.py`
- Create: `tests/artifacts/test_receipts.py`

**Interfaces:**
- Produces: `sha256_file(path: Path) -> str`
- Produces: `canonical_json_sha256(value: Mapping[str, object]) -> str`
- Produces: `validate_receipt(receipt: Mapping[str, object], schema_path: Path) -> None`
- Produces: `atomic_write_receipt(path: Path, receipt: Mapping[str, object]) -> str`

- [ ] **Step 1: Write failing tests for canonical hashes and fail-closed receipts**

```python
def test_canonical_json_hash_ignores_mapping_insertion_order():
    assert canonical_json_sha256({"b": 2, "a": 1}) == canonical_json_sha256({"a": 1, "b": 2})

def test_pass_receipt_requires_every_invariant(tmp_path, valid_receipt):
    del valid_receipt["invariants"]["logits_shape"]
    with pytest.raises(ReceiptValidationError):
        atomic_write_receipt(tmp_path / "receipt.json", valid_receipt)
```

- [ ] **Step 2: Verify tests fail before primitives exist**

Run: `uv run pytest tests/artifacts/test_digests.py tests/artifacts/test_receipts.py -v`

Expected: import/collection failure for the missing artifacts modules.

- [ ] **Step 3: Implement deterministic JSON and atomic publication**

Canonical JSON uses UTF-8, sorted keys, separators `(',', ':')`, `allow_nan=False`, and a final newline only in the stored file. Write to `<name>.partial`, fsync file and parent directory, validate schema, compute SHA-256, then atomically rename. A `PASS` receipt requires all invariant values to be literal `true`; an `errors` list must be empty.

- [ ] **Step 4: Verify hash vectors and corrupted receipt rejection**

Run: `uv run pytest tests/artifacts/test_digests.py tests/artifacts/test_receipts.py -v`

Expected: all tests pass; truncated, NaN-containing, or missing-invariant receipts are rejected and no final receipt remains.

- [ ] **Step 5: Commit receipt schemas and golden examples**

Run: `uv run python -m json.tool schemas/model-contract-receipt.schema.json > NUL`

Expected: JSON parser exits 0; schema requires model/config/source/processor/fixture/probe/environment hashes, observed shapes, invariant map, status, and errors.

**Artifact/evidence produced:** receipt schemas, canonical hash golden vectors, and atomic-write tests.

**Stop condition:** Receipt status can be `PASS` with a missing/false invariant or non-finite value.

**Commit boundary:** `feat: add content addressed receipts`

---

### Task 3: Verify pinned model assets, source, and licenses

**Objective:** Fetch only the two approved model snapshots, prove their hashes/revisions/licenses, and reject the historical noncommercial DINOv2 revision.

**Files:**
- Create: `configs/models/pinned-models.yaml`
- Create: `src/vision_active_learning_loop/models/assets.py`
- Create: `tests/models/test_assets.py`
- Create: `docs/model-licenses.md`
- Create: `schemas/model-asset-receipt.schema.json`

**Interfaces:**
- Produces: `PinnedAssetSpec`
- Produces: `verify_snapshot(spec: PinnedAssetSpec, snapshot_root: Path) -> ModelAssetReceipt`
- CLI: `val assets verify --config configs/models/pinned-models.yaml --cache-root <VAL_ARTIFACT_ROOT>/wave0/model_cache --output <receipt.json>`

- [ ] **Step 1: Write failing exact-hash and license tests**

```python
def test_rtdetr_weight_hash_is_exact(receipt):
    assert receipt.files["model.safetensors"].sha256 == "fe87a5a30f5daf298d10794c7682a63b6107986f97d6a770ba948d89e4340093"

def test_dinov2_weight_hash_and_size_are_exact(dino_receipt):
    weight = dino_receipt.files["model.safetensors"]
    assert weight.sha256 == "ae1e99fcefd534ed978cdeb8326f08030c96e28b7a81ffcbc98a857c84d14be1"
    assert weight.size == 88_249_960

def test_dino_rejects_noncommercial_card(spec, snapshot_with_nc_card):
    with pytest.raises(LicenseMismatch):
        verify_snapshot(spec, snapshot_with_nc_card)
```

- [ ] **Step 2: Run tests and confirm missing implementation**

Run: `uv run pytest tests/models/test_assets.py -v`

Expected: collection fails because `models.assets` is absent.

- [ ] **Step 3: Implement allowlisted snapshot verification**

Allow only the two repository/revision pairs. Fetch with revision pinning and no pattern wider than config/model/processor/source/license files. Hash every file, parse model-card license, archive the Apache-2.0 notice, and make network-free verification the default after download.

- [ ] **Step 4: Run offline verification**

Run: `HF_HUB_OFFLINE=1 uv run val assets verify --config configs/models/pinned-models.yaml --cache-root "$VAL_ARTIFACT_ROOT/wave0/model_cache" --output "$VAL_ARTIFACT_ROOT/wave0/receipts/model-assets.json"`

Expected: status `PASS`, exact revisions/weight hashes, both approved license checks true, and no RDD path referenced.

- [ ] **Step 5: Test tamper and revision failures**

Run: `uv run pytest tests/models/test_assets.py -v -k "tamper or revision or license"`

Expected: all negative tests pass by observing verifier exit 2 and a `FAIL` receipt.

**Artifact/evidence produced:** pinned model config, asset receipt, file inventory, source hashes, and archived license notices outside Git when upstream text requires it.

**Stop condition:** Any model revision, safetensors/config/source hash, or Apache-2.0 evidence fails.

**Commit boundary:** `feat: verify pinned model assets`

---

### Task 4: Build the synthetic RT-DETR executable-contract probe

**Objective:** Observe every normative inference/preprocessing invariant on the pinned runtime without labels or RDD data.

**Files:**
- Create: `src/vision_active_learning_loop/probes/model_contract.py`
- Create: `src/vision_active_learning_loop/models/rtdetr_contract.py`
- Create: `scripts/generate_wave0_fixtures.py`
- Create: `fixtures/synthetic/wave0/fixture-manifest.json`
- Create: `tests/probes/test_model_contract.py`
- Create: `tests/probes/test_processor_contract.py`

**Interfaces:**
- Produces: `reset_four_class_head(model, seed: int = 17) -> None`
- Produces: `extract_raw_contract(outputs) -> RawDetectorOutput`
- Produces: `run_model_contract_probe(spec, asset_receipt, fixture_manifest) -> ModelContractReceipt`
- CLI: `val probe model-contract --assets <receipt> --fixtures <manifest> --output <receipt>`

- [ ] **Step 1: Generate and test two deterministic fixtures**

```python
def test_fixture_dimensions(fixtures):
    assert [image.size for image in fixtures] == [(640, 320), (320, 640)]
    assert fixtures[0].tobytes() != fixtures[1].tobytes()
```

Run: `uv run pytest tests/probes/test_processor_contract.py::test_fixture_dimensions -v`

Expected: fails because fixture generator/manifest does not exist.

- [ ] **Step 2: Write failing tensor-contract tests**

```python
def test_observed_rtdetr_contract(receipt):
    assert receipt.config_num_queries == 300
    assert receipt.config_num_labels == 4
    assert receipt.shapes["logits"] == [2, 300, 4]
    assert receipt.shapes["pred_boxes"] == [2, 300, 4]
    assert receipt.shapes["intermediate_reference_points"] == [2, receipt.decoder_layers, 300, 4]
    assert receipt.invariants["native_fifth_logit_absent"] is True
```

- [ ] **Step 3: Implement processor and raw-output extraction**

Use bilinear `size={"max_height":640,"max_width":640}`, `do_pad=True`, `pad_size={"height":640,"width":640}`, bottom/right zero padding, `do_rescale=True`, factor `1/255`, `do_normalize=False`, and no labels. Assert pixel tensors `[2,3,640,640]`, masks `[2,640,640]`, and expected valid-mask rectangles.

`RawDetectorOutput` has exact fields:

```python
@dataclass(frozen=True)
class RawDetectorOutput:
    logits: torch.Tensor                 # [B,300,4]
    final_boxes: torch.Tensor            # [B,300,4]
    penultimate_boxes: torch.Tensor      # [B,300,4]
    intermediate_boxes: torch.Tensor     # [B,L,300,4]
```

Verify `final_boxes` is exactly layer `-1`, penultimate is layer `-2`, source AST/source hash shows stacking on axis 1 without query-axis permutation, and foreground scores equal `torch.sigmoid(logits)`. Do not call thresholding, NMS, or the non-focal postprocessor.

- [ ] **Step 4: Run the probe on the canonical GPU**

Run: `uv run val probe model-contract --assets "$VAL_ARTIFACT_ROOT/wave0/receipts/model-assets.json" --fixtures fixtures/synthetic/wave0/fixture-manifest.json --output "$VAL_ARTIFACT_ROOT/wave0/receipts/model-contract-receipt.json"`

Expected: exit 0 and `PASS`; all normative boolean fields true; receipt includes model/config/weights/Transformers source/processor/fixture/probe/environment hashes and observed shapes.

- [ ] **Step 5: Prove fail-closed behavior**

Run: `uv run pytest tests/probes/test_model_contract.py tests/probes/test_processor_contract.py -v`

Expected: tests pass, including injected fifth-logit, 299-query, permuted-intermediate, wrong-mask, and softmax-path fixtures producing `FAIL` with no Wave 0 pass marker.

**Artifact/evidence produced:** two synthetic images/manifest, probe source hash, complete model-contract receipt, and adversarial contract tests.

**Stop condition:** Any observed value differs, any intermediate output is unavailable label-free, or query correspondence cannot be proved from pinned execution/source.

**Commit boundary:** `feat: add executable rtdetr contract probe`

---

### Task 5: Prove BF16, determinism, VRAM, and checkpoint round-trip feasibility

**Objective:** Run a dataset-independent one-step forward/backward/update and verify the approved training mechanics fit the RTX 4090 and resume exactly enough for canonical evidence.

**Files:**
- Create: `src/vision_active_learning_loop/probes/training_feasibility.py`
- Create: `src/vision_active_learning_loop/training/checkpoint_io.py`
- Create: `tests/probes/test_training_feasibility.py`
- Create: `tests/training/test_checkpoint_io.py`
- Modify: `schemas/feasibility-receipt.schema.json`

**Interfaces:**
- Produces: `configure_determinism(seed: int) -> DeterminismState`
- Produces: `run_one_step_smoke(model, batch, seed: int) -> StepObservation`
- Produces: `save_checkpoint_atomic(state: CheckpointState, target: Path) -> str`
- Produces: `load_checkpoint_verified(target: Path, expected_digest: str) -> CheckpointState`
- CLI: `val probe training-feasibility --model-contract <receipt> --checkpoint-root <external-path> --output <receipt>`

- [ ] **Step 1: Write failing determinism and checkpoint tests**

```python
def test_tf32_is_disabled(observation):
    assert observation.cuda_matmul_allow_tf32 is False
    assert observation.cudnn_allow_tf32 is False

def test_checkpoint_round_trip_preserves_states(round_trip):
    assert round_trip.model_digest_before == round_trip.model_digest_after
    assert round_trip.optimizer_digest_before == round_trip.optimizer_digest_after
    assert round_trip.rng_digest_before == round_trip.rng_digest_after
```

- [ ] **Step 2: Confirm red tests**

Run: `uv run pytest tests/probes/test_training_feasibility.py tests/training/test_checkpoint_io.py -v`

Expected: missing-module collection failure.

- [ ] **Step 3: Implement the exact smoke**

Use seed 17, deterministic algorithms, cuDNN benchmark off, TF32 off, batch size 2 synthetic labeled images derived from the fixture geometry, BF16 autocast, AdamW learning rates `1e-4`/`1e-5`, weight decay `1e-4`, and gradient clip 0.1. Record finite loss, finite gradients, parameter change, allocated/reserved VRAM peak, wall/GPU time, and absence of deterministic fallback. Save model, optimizer, scheduler, scaler state if present, epoch/step, sampler order digest, and Python/NumPy/torch CPU/CUDA RNG states.

- [ ] **Step 4: Run twice from the same initial state**

Run: `uv run val probe training-feasibility --model-contract "$VAL_ARTIFACT_ROOT/wave0/receipts/model-contract-receipt.json" --checkpoint-root "$VAL_ARTIFACT_ROOT/wave0/checkpoints/feasibility-a" --output "$VAL_ARTIFACT_ROOT/wave0/receipts/feasibility-a.json" && uv run val probe training-feasibility --model-contract "$VAL_ARTIFACT_ROOT/wave0/receipts/model-contract-receipt.json" --checkpoint-root "$VAL_ARTIFACT_ROOT/wave0/checkpoints/feasibility-b" --output "$VAL_ARTIFACT_ROOT/wave0/receipts/feasibility-b.json"`

Expected: both `PASS`, peak allocated VRAM <=22 GiB, finite forward/backward/update, identical ordered state digests and loss within the receipt’s exact canonical comparison rule.

- [ ] **Step 5: Interrupt and resume the smoke**

Run: `uv run pytest tests/training/test_checkpoint_io.py -v -k "round_trip or corrupt or mismatch"`

Expected: valid state round-trips; truncation, input-digest mismatch, and RNG omission fail before resume.

**Artifact/evidence produced:** two feasibility receipts, VRAM/timing observations, checkpoint schema/hash, and deterministic resume proof.

**Stop condition:** OOM, non-finite value, deterministic-op error, TF32 enabled, BF16 unsupported, state mismatch, or peak allocated VRAM >22 GiB.

**Commit boundary:** `feat: verify deterministic training feasibility`

---

### Task 6: Reproduce Wave 0 cleanly and enforce the wave gate

**Objective:** Demonstrate clean-environment reproducibility, dataset-independent disk/runtime feasibility, and an irreversible block on Wave 1 when any prerequisite fails.

**Files:**
- Create: `src/vision_active_learning_loop/gates/wave0.py`
- Create: `schemas/wave0-gate-receipt.schema.json`
- Create: `tests/gates/test_wave0_gate.py`
- Create: `scripts/run_wave0_clean.ps1`
- Create: `scripts/run_wave0_clean.sh`
- Create: `docs/runbooks/wave0.md`

**Interfaces:**
- Produces: `evaluate_wave0(receipts: Wave0Inputs) -> Wave0GateReceipt`
- CLI: `val gate wave0 --environment <json> --assets <json> --model-contract <json> --feasibility-a <json> --feasibility-b <json> --output <json>`
- Exit codes: `0=PASS`, `2=normative FAIL`, `3=input/schema/hash error`.

- [ ] **Step 1: Write failing aggregate-gate tests**

```python
@pytest.mark.parametrize("failed_input", ["environment", "assets", "model_contract", "feasibility_a", "feasibility_b"])
def test_wave0_fails_if_any_parent_fails(valid_inputs, failed_input):
    valid_inputs[failed_input]["status"] = "FAIL"
    assert evaluate_wave0(valid_inputs).status == "FAIL"
```

- [ ] **Step 2: Verify the red state**

Run: `uv run pytest tests/gates/test_wave0_gate.py -v`

Expected: missing gate module.

- [ ] **Step 3: Implement clean-run scripts and aggregate validation**

Each script creates a new temporary uv cache, empty model cache target, and new container from the pinned digest; it runs Tasks 1–5 without RDD mounts, records download/cache/disk bytes and total runtime, then emits receipts below `$VAL_ARTIFACT_ROOT/wave0/clean-runs/<run-id>/<attempt-id>/`. The script never overwrites an existing attempt. The gate checks exact parent digests, two independent clean-run results, disk/runtime observations, that `VAL_DATA_ROOT` is absent, and all statuses `PASS`; its final receipt is `$VAL_ARTIFACT_ROOT/wave0/receipts/wave0-gate-receipt.json`.

- [ ] **Step 4: Execute the clean reproduction**

Run: `powershell -File scripts/run_wave0_clean.ps1 -RunId clean-a` followed by the same command with `clean-b`, then run the gate CLI.

Expected: two independent receipt trees and one `wave0-gate-receipt.json` with `status=PASS`; no RDD archive/path access appears in process/file audit logs.

- [ ] **Step 5: Verify Wave 1 cannot bypass the gate**

Run: `uv run pytest tests/gates/test_wave0_gate.py -v -k "fail or bypass or rdd"`

Expected: every corrupted/missing receipt and every attempted RDD access yields nonzero exit and no `wave0.pass` capability file.

- [ ] **Step 6: Stop for owner review**

Report the Wave 0 commit range, environment/model/probe/feasibility/gate receipt hashes, VRAM/runtime/disk observations, failures, and whether an owner/design decision is required. Do not invoke a Wave 1 command.

**Artifact/evidence produced:** two clean receipt trees, dataset-access audit, aggregate Wave 0 gate receipt, runbook, and owner review packet.

**Stop condition:** Any parent mismatch, clean-run divergence, undeclared network/data path, or normative `FAIL`. The only next action is owner/design review.

**Commit boundary:** `feat: enforce wave zero feasibility gate`
