# Wave 0 A7 CUDA Grid-Sample Backward Attribution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not dispatch subagents unless the owner explicitly requests them.

**Goal:** Attribute or rule out the pinned CUDA `grid_sampler_2d_backward_cuda` boundary as the first tensor-level cause of the closed A6 replay failure by running exactly two uninstrumented controls, five instrumented model replicas, and five isolated VJP replicas, without changing or passing Wave 0.

**Architecture:** Add a diagnostic-only package beside the frozen Wave 0 probes. A transparent adapter wraps only `model.model.decoder.layers[0..2].encoder_attn.attn`, temporarily intercepts the pinned `torch.nn.functional.grid_sample` calls, calls the saved original function with unchanged operands and arguments, returns the original result, and records six tensor roles for the nine stable `(decoder_layer, feature_level)` operation IDs. A separate tensor-evidence module owns canonical little-endian bytes, finite/norm evidence, pairwise descriptive comparisons, component tensor bundles, and the restricted VJP snapshot. One closed receipt type represents valid control, instrumented, isolated-VJP, and aggregate records; the central receipt validator independently recomputes component and terminal semantics. A dedicated PowerShell runner executes within the one Task 7-created campaign and fresh image, launches each replica in a fresh Docker process, never invokes feasibility or the Wave 0 aggregate gate, and closes at an A7 diagnostic terminal.

**Tech Stack:** Python 3.12.11; uv 0.8.15; pytest 9.0.2; JSON Schema 2020-12; Black 22.6.0; Ruff 0.16.4; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; SciPy 1.18.0; pycocotools 2.0.10; CUDA 12.6; Docker Desktop Linux engine; RTX 4090 24 GB; PowerShell 7.

## Global Constraints

- The owner's 2026-08-25 delegation reply is the written approval of the A7 authoritative specification. The approved specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `5f699e4ad29cd57751d68352fdc684004a71f67a`, especially Section 5.2.9.
- Entry branch is `codex/wave0-model-contract`. Implementation may begin only when HEAD is the docs-only commit containing this plan, its first parent is `5f699e4ad29cd57751d68352fdc684004a71f67a`, and its only changed path is `docs/superpowers/plans/2026-08-26-val-wave0-a7-grid-sample-attribution.md`.
- Exact implementation allowlist is closed to these ten tracked files:
  1. `src/vision_active_learning_loop/diagnostics/__init__.py`
  2. `src/vision_active_learning_loop/diagnostics/tensor_evidence.py`
  3. `src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py`
  4. `src/vision_active_learning_loop/artifacts/receipts.py`
  5. `schemas/grid-sample-attribution-receipt.schema.json`
  6. `scripts/run_wave0_a7.ps1`
  7. `tests/diagnostics/__init__.py`
  8. `tests/diagnostics/test_tensor_evidence.py`
  9. `tests/diagnostics/test_grid_sample_attribution.py`
  10. `tests/artifacts/test_receipts.py`
- Needing an eleventh tracked file is a hard stop for a new written spec/plan review. In particular, do not modify `training_feasibility.py`, `model_contract.py`, `wave0.py`, `run_wave0_clean.ps1`, `run_wave0_clean.sh`, a Dockerfile, `pyproject.toml`, `uv.lock`, model/config pins, the approved spec, this plan, or historical evidence during implementation.
- Reuse the frozen A6 runtime helpers without changing their behavior: `configure_determinism()`, `run_math_only_labeled_forward_backward()`, `run_allowlisted_backward()`, `_expected_grid_sample_warning_count()`, `_observe_live_environment()`, and `_prepare_labeled_batch()`. No A7 path constructs an optimizer, scheduler, checkpoint, feasibility receipt, numerical-replay result, or Wave 0 gate receipt.
- The model is the exact A6 RT-DETR-R18 model at revision `cc5b50f32f0100caaa3bd275343e2fb17762c73d`, reset with seed 17 to four RDD classes and run with 300 queries, three decoder layers, three feature levels, BF16 labeled forward, Math-only SDPA, `disable_custom_kernels == true`, and exactly nine registered `grid_sampler_2d_backward_cuda` warnings.
- The fresh parent model-assets receipt must also retain and verify DINOv2-small revision `ed25f3a31f01632728cabb09d1542f84ab7b0056`; A7 never loads or runs that encoder, but it does not weaken the frozen two-model asset contract.
- The adapter may replace only `model.model.decoder.layers[index].encoder_attn.attn` for `index in range(3)`. It must hold the original parameter-free module, save the original `torch.nn.functional.grid_sample` callable, restore the callable in `finally`, verify restoration by object identity, and reject nested/reentrant use.
- For every intercepted call, require `mode == "bilinear"`, `padding_mode == "zeros"`, `align_corners is False`, positional operand identity, and feature indexes exactly `0,1,2`. The adapter calls the saved original callable once, returns that exact result tensor, performs no arithmetic on the returned path, and registers a hook that returns `None` after recording the unmodified incoming gradient.
- Stable operation IDs are exactly `decoder-0/feature-0` through `decoder-2/feature-2`. The canonical operation order is decoder-major for inventories; causal traversal uses the observed backward callback order, which must be a permutation of all nine IDs and exact across the five instrumented replicas.
- Tensor evidence supports only `torch.bfloat16`, `torch.float16`, `torch.float32`, and `torch.float64`. It rejects unsupported dtype, sparse, quantized, meta, empty, non-finite, non-contiguous-after-normalization, shape/element mismatch, native big-endian, missing, extra, duplicate, symlinked, junctioned, non-regular, wrong-hash, or malformed evidence.
- Canonical tensor bytes are detached, moved to CPU, made contiguous, and serialized in C order on a little-endian host. Evidence includes role, stable operation ID, shape, dtype token, element count, finite count, non-finite count, SHA-256, and CPU-float64 L2 norm. Grid-sample tensors use one of the nine decoder/feature IDs; trainable-parameter gradients use `model-parameter`. Comparison evidence contains exact-digest equality, difference L2, relative L2, and cosine; it is descriptive and defines no tolerance.
- Every component publishes one atomic no-clobber `tensor-bundle.vala7` file containing every raw tensor named in that component receipt, so the aggregate process can recompute descriptive comparisons from bytes rather than from receipt claims. In addition, only `instrumented-0` publishes `vjp-snapshot.vala7`, containing exactly the value, sampling-grid, and incoming-result-gradient tensors for all nine operation IDs. Both file kinds use magic `VALA7T1\n`, an unsigned little-endian 64-bit canonical-JSON header length, a closed header with byte order, sorted tensor names, offsets, sizes, shapes, dtype tokens, and SHA-256 values, followed by concatenated canonical tensor bytes.
- Exactly two fresh-process control replicas are named `control-0` and `control-1`. Exactly five fresh-process instrumented replicas are named `instrumented-0` through `instrumented-4`. Exactly five fresh-process isolated replicas are named `isolated-vjp-0` through `isolated-vjp-4`. No alias, missing ID, extra ID, duplicate ID, or in-process loop can satisfy the aggregate.
- Every model replica records exact identity, loss hex, warning evidence, deterministic-attention evidence, runtime, peak allocated/reserved VRAM, and a complete ordered trainable-parameter gradient inventory before clipping. Missing gradients fail closed. Parameter-gradient equality between controls and instrumented replicas is descriptive, not an instrumentation-validity gate.
- Every CUDA replica retains the A6 peak-allocated VRAM ceiling of 22 GiB. Exceeding it is an A7 inconclusive hard stop, never permission to reduce tensors, omit evidence, change precision, or retry.
- The runner derives source commit from the approved clean worktree and verifies it against the fresh image OCI label. It passes the value as both `VAL_SOURCE_COMMIT` and the CLI `--source-commit`; production requires exact equality. Runtime image ID and base digest are taken from the validated parent environment receipt and must equal runner-provided environment values. Component receipts also bind a canonical source inventory SHA-256 over both new diagnostic modules.
- Every instrumented replica records six roles per operation: `forward_value`, `forward_grid`, `forward_result`, `incoming_result_gradient`, `outgoing_value_gradient`, and `outgoing_grid_gradient`. The first four determine eligibility; outgoing gradients determine the model candidate. Instrumented replicas also record adapter source SHA-256 and hook/restoration invariants.
- Every isolated replica loads and verifies the one `instrumented-0` snapshot and its parent receipt, recreates the nine original pinned `grid_sample` calls, and invokes one `torch.autograd.backward()` over the nine results with the nine saved incoming gradients inside the existing warning-bounded helper. It performs no model forward, model load, dataset operation, optimizer, scheduler, checkpoint, or receipt-parent substitution.
- Instrumentation validity requires exact source/image/model/fixture/seed/backend/loss/warning identities across two controls and five instrumented replicas; exact forward value, grid, and result digests across five instrumented replicas; exact callback order; restored original callable; and complete finite evidence. Parameter-gradient digest inequality is not itself invalid.
- Any unexpected CUDA synchronization error, new warning, changed loss, forward mismatch, missing callback, unstable callback order, callable-restoration failure, or static identity mismatch makes the campaign inconclusive and stops it; none may be ignored or retried.
- Causal classification traverses callback order. A model candidate requires exact value, grid, result, and incoming result gradient across five instrumented replicas, differing outgoing value or grid gradient, and all earlier callbacks exact on all six roles. Kernel attribution additionally requires five isolated replicas with exact snapshot parents, exact operands/incoming/result, exactly nine registered warnings, and at least two different outgoing digests for the same candidate role.
- `NOT_ATTRIBUTED` requires all diagnostics valid, every outgoing value/grid gradient exact for all nine isolated VJPs, every instrumented operation exact on all six roles, and at least two different complete parameter-gradient inventory digests among the five instrumented replicas. A completely exact model diagnostic is `INCONCLUSIVE`, not not-attributed.
- Closed terminals are exactly:
  - `WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`
  - `WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`
  - `WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN`
- No A7 component or aggregate status contains the standalone token `PASS`. Valid component receipts use `RECORDED`; aggregate status is `ATTRIBUTED`, `NOT_ATTRIBUTED`, or `INCONCLUSIVE` and must agree exactly with its terminal and errors.
- `RECORDED`, `ATTRIBUTED`, and `NOT_ATTRIBUTED` require a non-empty closed invariant map with every value `true` and `errors == []`. `INCONCLUSIVE` requires at least one false invariant or a non-empty canonical error list; a fully observable but exactly reproduced model run uses the explicit `model_divergence_not_reproduced` error.
- Every A7 destination is absent before use. All receipt, component-bundle, and VJP-snapshot publication uses the existing atomic file no-clobber primitives. Task 7 atomically claims the campaign/audit root; the runner requires that bound root and lease to exist while every Wave 0 parent, component, aggregate, bundle, and snapshot destination remains absent. Trusted orchestration creates parents, publishers never create them, and audit logs/records/campaign results use `FileMode.CreateNew`.
- The A6 campaign `wave0-a6-20260825T125943018Z`, source `efe5cee58931e8e8bb85292b4c48701ec2e32c9b`, image `sha256:04bce082c4040fded9cda6b9dfde2a76dc5686299fe991358951bd023fe39be8`, and all A2-A6 objects remain immutable. A7 rehashes the complete pre-change inventory before and after execution and cannot retry, complete, or reinterpret A6.
- `VAL_DATA_ROOT` remains unset. Do not read, list, mount, download, or access RDD. Wave 1, the Wave 0 aggregate gate, remote operations, push, merge, tag, Release, and GitHub publication are forbidden.
- Whole-tree formatting debt remains out of scope. Only touched Python files receive targeted Black/Ruff. Author and committer are `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`; commits are append-only without amend, rebase, reset, squash, force, or history rewriting.

---

## File Map

| File | Responsibility in A7 |
|---|---|
| `src/vision_active_learning_loop/diagnostics/__init__.py` | Mark the diagnostic-only package without importing CUDA/model code at package import time |
| `src/vision_active_learning_loop/diagnostics/tensor_evidence.py` | Canonical tensor bytes/evidence, pairwise descriptive comparisons, snapshot encoding/decoding, and atomic no-clobber snapshot publication |
| `src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py` | Stable operation IDs, transparent adapter, model/control/instrumented/isolated executions, aggregate classification, path validation, receipt construction, and lazy CLI command |
| `src/vision_active_learning_loop/artifacts/receipts.py` | Register schema v1 and independently enforce A7 component identities, inventories, hashes, counts, comparison consistency, and aggregate terminal logic |
| `schemas/grid-sample-attribution-receipt.schema.json` | Closed `oneOf` schema for control, instrumented, isolated-VJP, and aggregate receipts |
| `scripts/run_wave0_a7.ps1` | Fail-closed fresh campaign orchestration, fresh-process Docker stages, exact count/order, audit publication, lease boundary, and closure |
| `tests/diagnostics/__init__.py` | Test package marker only |
| `tests/diagnostics/test_tensor_evidence.py` | CPU RED/GREEN proof for bytes, records, comparisons, snapshots, corruption, links, and no-clobber behavior |
| `tests/diagnostics/test_grid_sample_attribution.py` | CPU fake-model proof for adapter transparency/order/hooks, replica logic, classification, CLI boundaries, and runner structure |
| `tests/artifacts/test_receipts.py` | Independent schema/semantic validation against forged A7 receipt claims |

No configuration, dependency, model pin, Dockerfile, A6 probe, A6 schema, Wave 0 gate, dataset path, or research artifact changes.

---

### Task 1: Revalidate Entry Identity and Freeze the Historical Baseline

**Files:**
- Read: Git metadata, approved A7 spec/plan lineage, current implementation surface, and all historical artifact/image identities
- Modify: none
- Write outside Git: one never-used pre-change baseline manifest using atomic `CreateNew`

**Interfaces:**
- Consumes: the registered linked worktree and docs-only A7 plan commit
- Produces: exact Git, artifact, image, and protected-path inventories reused by Tasks 6 and 8

- [ ] **Step 1: Locate and validate the registered worktree and plan lineage**

Run from the worktree selected from `git worktree list --porcelain`, never a hand-written path:

```powershell
$ErrorActionPreference = 'Stop'
$ExpectedBranch = 'codex/wave0-model-contract'
$ExpectedSpecHead = '5f699e4ad29cd57751d68352fdc684004a71f67a'
$PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-grid-sample-attribution.md'
$Records = @(git worktree list --porcelain)
$Candidates = @()
$Current = @{}
foreach ($Line in $Records + '') {
    if ($Line -eq '') {
        if ($Current.branch -eq 'refs/heads/' + $ExpectedBranch) { $Candidates += $Current }
        $Current = @{}
    } elseif ($Line -match '^(worktree|HEAD|branch) (.+)$') {
        $Current[$Matches[1]] = $Matches[2]
    }
}
if ($Candidates.Count -ne 1) { throw 'A7 registered worktree is not unique' }
$Worktree = (Resolve-Path -LiteralPath $Candidates[0].worktree).Path
Set-Location -LiteralPath $Worktree
$PlanHead = (git rev-parse HEAD).Trim()
$PlanParent = (git rev-parse HEAD^).Trim()
$Branch = (git branch --show-current).Trim()
$GitDir = (git rev-parse --path-format=absolute --git-dir).Trim()
$CommonDir = (git rev-parse --path-format=absolute --git-common-dir).Trim()
$Files = @(git diff-tree --no-commit-id --name-only -r HEAD)
$LinkedStatus = @(git status --porcelain=v1)
$CanonicalRoot = (Resolve-Path -LiteralPath (Join-Path $CommonDir '..')).Path
$CanonicalStatus = @(git -C $CanonicalRoot status --porcelain=v1)
$Author = (git show -s --format='%an <%ae>' HEAD).Trim()
$Committer = (git show -s --format='%cn <%ce>' HEAD).Trim()
if ($Branch -ne $ExpectedBranch) { throw 'A7 branch mismatch' }
if ($PlanParent -ne $ExpectedSpecHead) { throw 'A7 plan parent mismatch' }
if ($GitDir -eq $CommonDir) { throw 'A7 is not in the linked worktree' }
if ($Files.Count -ne 1 -or $Files[0] -ne $PlanPath) { throw 'A7 plan commit is not docs-only' }
if ($LinkedStatus.Count -ne 0 -or $CanonicalStatus.Count -ne 0) { throw 'Git state is not clean' }
$ExpectedIdentity = 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>'
if ($Author -ne $ExpectedIdentity -or $Committer -ne $ExpectedIdentity) { throw 'A7 plan identity mismatch' }
git show -s --format=fuller HEAD
```

Do not checkout, repair, reset, or move a mismatch.

- [ ] **Step 2: Rehash the fixed A6 trigger evidence**

```powershell
$A6Root = 'D:\vision-active-learning-loop-artifacts\wave0\a6-runs\wave0-a6-20260825T125943018Z'
$A6Expected = [ordered]@{
    'audit\09-microcheck-result.json' = '59ca6f4697d85327ac098761d290e40e338a9a0894574c2ac7fbbb99981c5d42'
    'gate\wave0-gate-receipt.json' = 'aa4912a792d054dce2e3a46c48e40dd5390f9b8ff66feb574bf20970ae244624'
    'audit\22-aggregate-failure-diagnostic.json' = '26d67369ddc73b1d2e9476e3fbe4f6ac7a6564b336580a256943ef2d14302a22'
    'audit\40-campaign-result.json' = '441144efc226bf87ca0a11869a87ae0f64c8e0d829b030626ac1cfba59755bbd'
    'audit\41-campaign-file-manifest.json' = '50b5f17a3244290ccbd41118b07034dc47976d2c046c2cf88e6c6cb413c74642'
    'audit\30-historical-preservation.json' = '61248362331be335501b7dc5439500cea179f02b192fdad4afa24930f1eb4d75'
    'audit\51-campaign-closure-manifest.json' = 'bf869deca033a82c9b0510baff9d2ee55227cc79e62648fcbae3bc316810e1c8'
}
foreach ($Relative in $A6Expected.Keys) {
    $Path = Join-Path $A6Root $Relative
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant()
    if ($Actual -ne $A6Expected[$Relative]) { throw "A6 evidence drift: $Relative" }
}
```

Inspect the campaign result and require source/image/run identities plus permanent terminal `WAVE0_A6_NORMATIVE_FAIL / WAVE1_FORBIDDEN`.

- [ ] **Step 3: Write a complete no-clobber baseline inventory**

Inventory every existing file below `D:\vision-active-learning-loop-artifacts\wave0`, every `vision-active-learning-loop:wave0-*` tag and exact image ID, and every tracked Git file outside the ten-file implementation allowlist. Include the spec and plan. Write compact canonical JSON plus newline using `FileMode.CreateNew` to a never-used `$env:TEMP\val-a7-baseline-$PlanHead.json`.

The implementation session must retain the path and SHA-256 of this baseline. Any missing, changed, or unexpected historical entry at Tasks 6 or 8 is a hard stop.

**Stop condition:** identity mismatch, dirty state, A6 hash drift, an active project GPU lease/container, or inability to atomically create the exact baseline.

---

### Task 2: Implement Canonical Tensor Evidence and Snapshot I/O With TDD

**Files:**
- Create: `src/vision_active_learning_loop/diagnostics/__init__.py`
- Create: `src/vision_active_learning_loop/diagnostics/tensor_evidence.py`
- Create: `tests/diagnostics/__init__.py`
- Create: `tests/diagnostics/test_tensor_evidence.py`

**Interfaces:**

```python
@dataclass(frozen=True)
class TensorEvidence:
    name: str
    role: str
    operation_id: str
    shape: tuple[int, ...]
    dtype: str
    element_count: int
    finite_count: int
    non_finite_count: int
    sha256: str
    l2_norm: float

@dataclass(frozen=True)
class TensorComparison:
    left_replica: str
    right_replica: str
    name: str
    exact_digest_equal: bool
    difference_l2: float
    relative_l2: float
    cosine: float

def canonical_tensor_bytes(tensor: torch.Tensor) -> tuple[str, tuple[int, ...], bytes]: ...
def observe_tensor(name: str, role: str, tensor: torch.Tensor, *, operation_id: str) -> TensorEvidence: ...
def compare_tensors(left_replica: str, right_replica: str, name: str, left: torch.Tensor, right: torch.Tensor) -> TensorComparison: ...
def encode_snapshot(tensors: Mapping[str, torch.Tensor]) -> bytes: ...
def decode_snapshot(path: Path, *, expected_names: Collection[str]) -> dict[str, torch.Tensor]: ...
def atomic_write_snapshot(path: Path, tensors: Mapping[str, torch.Tensor]) -> str: ...
```

- [ ] **Step 1: Create package markers and RED byte/evidence tests**

Add only module docstrings to both `__init__.py` files. In `test_tensor_evidence.py`, add RED cases for:

```text
test_canonical_tensor_bytes_are_little_endian_contiguous_and_dtype_bound
test_observe_tensor_records_exact_counts_digest_and_float64_norm
test_canonical_tensor_bytes_reject_sparse_quantized_meta_empty_unsupported_and_nonfinite
test_observe_tensor_does_not_alias_or_modify_the_input
```

Use literal known vectors for all four allowed dtypes and compare their bytes to `struct.pack` or explicit uint16 words for BF16. Patch `sys.byteorder` to `"big"` and require fail-closed rejection before hashing.

- [ ] **Step 2: Add RED pairwise-comparison tests**

Test exact, finite drift, both-zero, and one-zero cases. Register these formulas:

```python
difference_l2 = torch.linalg.vector_norm(left64 - right64).item()
denominator = max(torch.linalg.vector_norm(left64).item(), torch.linalg.vector_norm(right64).item())
relative_l2 = 0.0 if denominator == 0.0 else difference_l2 / denominator
cosine = 1.0 if both_zero else 0.0 if exactly_one_zero else torch.dot(left64, right64).item() / (left_norm * right_norm)
```

Require equal shape and dtype, finite outputs, and exact digest equality computed from canonical bytes rather than a tolerance.

- [ ] **Step 3: Add RED snapshot round-trip and corruption tests**

Create an exact 27-name inventory for nine operation IDs times `forward_value`, `forward_grid`, and `incoming_result_gradient`. Add tests for deterministic encode, exact decode, magic/header length, sorted names, byte order, offsets, sizes, per-tensor hash, total length, and fresh regular-file path.

Parametrize rejection of missing/extra/renamed/duplicate names; wrong dtype/shape/count/offset/size/hash/endian; truncated/trailing bytes; invalid UTF-8/JSON; non-regular file; symlink; junction when available; existing destination; missing parent; and a publication race where exactly one writer succeeds.

- [ ] **Step 4: Run RED and record only intended missing-symbol failures**

```powershell
uv run pytest -q tests/diagnostics/test_tensor_evidence.py
```

Require failures because the new module/API does not exist. Collection, environment, and existing-suite failures are hard stops.

- [ ] **Step 5: Implement canonical bytes and evidence minimally**

Use a closed dtype table:

```python
_DTYPES = {
    torch.bfloat16: ("bfloat16", torch.uint16),
    torch.float16: ("float16", torch.float16),
    torch.float32: ("float32", torch.float32),
    torch.float64: ("float64", torch.float64),
}
```

Detach, transfer to CPU, make contiguous, check `sys.byteorder == "little"`, check element count and finiteness, view BF16 as uint16 only for byte extraction, and calculate the norm from `tensor.double()` on CPU. Never cast before hashing.

- [ ] **Step 6: Implement the closed snapshot container and atomic publication**

Build header offsets relative to the payload, encode the header with `json.dumps(..., sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)`, prefix the fixed magic and `struct.pack("<Q", len(header))`, and append bytes in sorted name order. Decode with explicit bounds before tensor construction, copy from the immutable buffer, and re-observe every tensor to match the header.

Publish through `open_unique_staging_file()` and `publish_staged_file_no_clobber()`, fsync the staging file, reread and verify its SHA-256 and decode result, then publish. Remove only the unique staging file in `finally`; never create the parent or unlink the destination.

- [ ] **Step 7: Run GREEN and commit the isolated foundation**

```powershell
uv run pytest -q tests/diagnostics/test_tensor_evidence.py
uv run black --check src/vision_active_learning_loop/diagnostics/__init__.py src/vision_active_learning_loop/diagnostics/tensor_evidence.py tests/diagnostics/__init__.py tests/diagnostics/test_tensor_evidence.py
uv run ruff check src/vision_active_learning_loop/diagnostics/__init__.py src/vision_active_learning_loop/diagnostics/tensor_evidence.py tests/diagnostics/__init__.py tests/diagnostics/test_tensor_evidence.py
git diff --check
```

Commit only the four Task 2 files:

```powershell
git add -- src/vision_active_learning_loop/diagnostics/__init__.py src/vision_active_learning_loop/diagnostics/tensor_evidence.py tests/diagnostics/__init__.py tests/diagnostics/test_tensor_evidence.py
git commit -m "feat: add A7 tensor evidence primitives"
```

---

### Task 3: Implement the Transparent Adapter and Replica Engines With TDD

**Files:**
- Create: `src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py`
- Create: `tests/diagnostics/test_grid_sample_attribution.py`

**Interfaces:**

```python
OPERATION_IDS = tuple(
    f"decoder-{decoder}/feature-{feature}"
    for decoder in range(3)
    for feature in range(3)
)

@dataclass
class OperationCapture:
    operation_id: str
    callback_order: int | None
    tensors: dict[str, torch.Tensor]

class AttributionError(ValueError): ...

@dataclass(frozen=True)
class ModelReplicaInputs:
    environment: Path
    model_assets: Path
    model_contract: Path
    component_root: Path
    component_id: str
    run_id: str
    source_commit: str
    image_id: str
    base_image_digest: str
    argv: tuple[str, ...]
    vjp_snapshot_output: Path | None

@dataclass(frozen=True)
class IsolatedReplicaInputs:
    environment: Path
    model_assets: Path
    model_contract: Path
    parent_instrumented_receipt: Path
    vjp_snapshot: Path
    component_root: Path
    component_id: str
    run_id: str
    source_commit: str
    image_id: str
    base_image_digest: str
    argv: tuple[str, ...]

class ModelRecorder:
    def observe_forward(self, operation_id: str, value: torch.Tensor, grid: torch.Tensor, result: torch.Tensor) -> None: ...
    def incoming_gradient_hook(self, operation_id: str) -> Callable[[torch.Tensor], torch.Tensor | None]: ...
    def finalize(self) -> tuple[OperationCapture, ...]: ...

class GridSampleAttributionAdapter(torch.nn.Module):
    def __init__(self, wrapped: torch.nn.Module, decoder_layer: int, recorder: ModelRecorder) -> None: ...
    def forward(self, value, value_spatial_shapes, value_spatial_shapes_list, level_start_index, sampling_locations, attention_weights, im2col_step): ...

def install_adapters(model: torch.nn.Module, recorder: ModelRecorder) -> tuple[GridSampleAttributionAdapter, ...]: ...
def run_model_replica(inputs: ModelReplicaInputs, *, instrumented: bool) -> dict[str, object]: ...
def run_isolated_vjp_replica(inputs: IsolatedReplicaInputs) -> dict[str, object]: ...
def classify_aggregate(
    controls: Sequence[Mapping[str, object]],
    instrumented: Sequence[Mapping[str, object]],
    isolated: Sequence[Mapping[str, object]],
) -> dict[str, object]: ...
```

- [ ] **Step 1: Add RED operation-ID and adapter-structure tests**

Build a tiny parameter-free fake of the pinned `MultiScaleDeformableAttention.forward` loop. Require exactly three decoder adapters, three feature calls each, decoder-major inventory IDs, original module retention, and rejection of wrong decoder count, feature count, module path, arguments, reentry, duplicate call, extra call, or callable-restoration drift.

Add an AST/source test requiring production adapter code to call the saved original grid-sample callable exactly once and forbidding `.detach()`/`.clone()`/casts/arithmetic on the returned value before it is returned. Evidence copies are made only inside the recorder after the original result exists.

- [ ] **Step 2: Add RED transparency and hook tests**

For identical CPU fake operands, compare unwrapped and wrapped outputs exactly. Backpropagate a non-symmetric scalar and require exact model input gradients, one callback per operation, a nine-ID callback permutation, `None` hook returns, all six tensor roles, and no leaked monkeypatch after normal or exceptional exit.

Test that forward value/grid/result evidence is captured before backward and incoming/outgoing gradients only after backward. Missing `.grad`, non-finite gradient, duplicate callback, or a result hook that returns a replacement must raise `AttributionError` and publish no receipt, component bundle, or VJP snapshot.

- [ ] **Step 3: Add RED complete parameter-gradient inventory tests**

Use a small named model with detector and backbone parameters. Require named-parameter order, no duplicates, every `requires_grad` parameter present, exact name/shape/dtype/evidence, and a canonical inventory SHA-256. Reject absent grad, extra record, non-finite grad, reordered name, or count mismatch.

- [ ] **Step 4: Add RED isolated-VJP tests**

With nine CPU snapshot fixtures, patch only `run_allowlisted_backward` to execute its callback and return the existing valid warning evidence. Require nine calls to the saved original `grid_sample`, unchanged exact arguments, one multi-output `torch.autograd.backward`, no model constructor/forward import path, and six roles per operation.

Add fail-closed cases for a non-`instrumented-0` parent, VJP-snapshot/parent receipt hash mismatch, wrong 27-name VJP-snapshot inventory, differing source/image/run/GPU identities, warning count other than nine, additional warning, non-finite output gradient, or component-bundle/VJP-snapshot link or junction.

- [ ] **Step 5: Run RED**

```powershell
uv run pytest -q tests/diagnostics/test_grid_sample_attribution.py -k "adapter or operation or gradient or isolated"
```

- [ ] **Step 6: Implement the adapter without changing the original result path**

Inside each adapter call, set a guarded recorder context, replace `torch.nn.functional.grid_sample` only for the duration of `self.wrapped(...)`, and restore it in `finally`. The interception closure must:

```python
result = original_grid_sample(
    value,
    grid,
    mode=mode,
    padding_mode=padding_mode,
    align_corners=align_corners,
)
recorder.observe_forward(operation_id, value, grid, result)
value.retain_grad()
grid.retain_grad()
result.retain_grad()
result.register_hook(recorder.incoming_gradient_hook(operation_id))
return result
```

After bounded backward, `recorder.finalize()` reads retained `.grad` tensors and creates immutable CPU evidence copies. It must not clip, update, or zero gradients.

- [ ] **Step 7: Implement the shared A6-bound model setup and control/instrumented engines**

Validate the fresh A7 parent environment, model-assets, and model-contract receipts for the same run ID. Re-verify the pinned snapshot/source, configure seed 17 before CUDA initialization, require one RTX 4090 and BF16, load locally with safetensors, call `reset_four_class_head(model, seed=17)`, move to CUDA, and use `_prepare_labeled_batch()`.

The labeled callback is exactly:

```python
model.train()
model.zero_grad(set_to_none=True)
with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
    autocast_observed = bool(torch.is_autocast_enabled("cuda"))
    outputs = model(**model_batch)
    loss = outputs.loss
return loss, autocast_observed
```

Call `run_math_only_labeled_forward_backward(..., expected_warning_count=9)`, then record evidence before any clip/update. Controls install no adapter. Instrumented replicas install exactly three adapters and finalize exactly nine operations. Both delete the model/batch in `finally` and synchronize only for evidence/timing/VRAM capture.

Before publishing a valid component receipt, write `tensor-bundle.vala7` atomically from the full ordered parameter-gradient tensors plus all operation tensors for instrumented replicas. `instrumented-0` separately writes the restricted 27-tensor `vjp-snapshot.vala7`; other model replicas reject a non-null VJP-snapshot destination. A bundle or snapshot publication failure publishes no receipt and leaves the immutable partial evidence for audit.

- [ ] **Step 8: Implement isolated VJP execution**

Load the exact snapshot onto the selected CUDA device, mark value and grid tensors `requires_grad_(True)`, compute nine original `torch.nn.functional.grid_sample` outputs, and call:

```python
warning_evidence = run_allowlisted_backward(
    lambda: torch.autograd.backward(tuple(results), tuple(incoming_gradients)),
    expected_count=9,
)
```

Record exact forward results and outgoing value/grid gradients. Verify strict mode and backend restoration. Do not import or call `RTDetrForObjectDetection` in this code path.

Publish each isolated replica's full six-role operation tensors as its component `tensor-bundle.vala7` before its receipt. The isolated bundle contains no parameter tensor and cannot substitute for the one restricted VJP snapshot.

- [ ] **Step 9: Run GREEN for engines**

```powershell
uv run pytest -q tests/diagnostics/test_tensor_evidence.py tests/diagnostics/test_grid_sample_attribution.py -k "not receipt and not runner and not cli"
uv run black --check src/vision_active_learning_loop/diagnostics tests/diagnostics
uv run ruff check src/vision_active_learning_loop/diagnostics tests/diagnostics
git diff --check
```

Do not commit yet; receipt/classification integration in Task 4 must close the public surface first.

---

### Task 4: Close A7 Receipt, Semantic Validation, and Classification With TDD

**Files:**
- Modify: `src/vision_active_learning_loop/artifacts/receipts.py`
- Create: `schemas/grid-sample-attribution-receipt.schema.json`
- Modify: `src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py`
- Modify: `tests/diagnostics/test_grid_sample_attribution.py`
- Modify: `tests/artifacts/test_receipts.py`

**Interfaces:**
- Receipt key: `("grid-sample-attribution", 1)`
- Component kinds: `control`, `instrumented`, `isolated-vjp`, `aggregate`
- Valid nonterminal status: `RECORDED`
- Aggregate statuses: `ATTRIBUTED`, `NOT_ATTRIBUTED`, `INCONCLUSIVE`

- [ ] **Step 1: Add valid closed fixtures for all four receipt branches**

Create builders in `test_grid_sample_attribution.py` using small literal tensors/evidence. Import those builders into `test_receipts.py`. Every fixture includes:

```text
receipt_type, schema_version, normative, metadata
identity: source_commit, image_id, base_image_digest, run_id, component_kind,
          component_id, gpu_name, gpu_uuid, model/config/processor/fixture/source hashes,
          seed, precision, query/layer/feature counts, disable_custom_kernels
parent_receipts: environment, model-assets, model-contract, plus instrumented parent for VJP
execution: exact argv, exit_code=0, timestamps, runtime, peak VRAM, warning/backend evidence
invariants, status, errors
```

Every component receipt requires a `tensor_bundle` object binding relative path, size, file SHA-256, inventory SHA-256, exact names, and `public_export_candidate == false`. Instrumented receipts require nine closed operations. Only the nested `instrumented-0` schema branch permits and requires `vjp_snapshot`; the `instrumented-1..4` branches omit and forbid that field. The VJP-snapshot object binds the same file identity fields and exactly 27 names. Isolated receipts require that exact VJP snapshot and parent hash. Aggregate receipts require exactly 2+5+5 parent receipt-and-bundle path/size/hash records and all comparison/classification evidence.

- [ ] **Step 2: Add schema RED mutations**

For each branch, reject missing/extra/wrong field, unsupported component/status/terminal, malformed SHA/image/GPU ID, nonzero exit code, wrong ID set/count, duplicate operation, wrong callback order shape, tensor role omission/extra, non-finite JSON number, comparison omission, snapshot on wrong replica, missing snapshot on `instrumented-0`, and the token `PASS` anywhere in status/terminal.

The schema uses `oneOf` on `normative.identity.component_kind`; every object has `additionalProperties: false`; every operation list has exactly nine items; parent lists have exact lengths; and terminal/status pairs use `if/then` or branch constants rather than free strings.

Because the local validator currently implements `minItems` but not `maxItems` or `oneOf`, add RED unit cases and then the minimal generic support for exactly those two JSON Schema keywords in `_validate_schema()`: `maxItems` rejects oversized arrays, and `oneOf` succeeds only when exactly one mapping candidate validates. Do not add remote references, coercion, defaults, or any other schema feature. Re-run all existing receipt tests to prove the hardening does not reinterpret historical valid receipts.

- [ ] **Step 3: Add independent semantic-validator RED mutations**

Schema-valid forgeries must be rejected for:

```text
metadata.run_id != normative.identity.run_id
component ID/kind mismatch or non-canonical set
parent receipt content/hash/run/image/GPU mismatch
exact-digest comparison claims that disagree with source tensor records, or exact comparisons with nonzero difference/relative L2 or cosine other than one
parameter inventory digest/order/count mismatch
operation ID/order/role mismatch
callback order not a common nine-ID permutation
instrumentation identity/loss/warning/forward mismatch
component-bundle or VJP-snapshot inventory/hash/parent mismatch
isolated operand/result/warning mismatch
claimed first candidate with an earlier non-exact callback
claimed attribution without matching isolated outgoing divergence
claimed NOT_ATTRIBUTED with any operation divergence or one parameter digest
claimed INCONCLUSIVE with attributed/not-attributed evidence
status/errors/invariants/terminal disagreement
```

The independent validator must recompute canonical inventory hashes and aggregate classification from receipt content; it must not trust `classification.candidate_operation`, `status`, or `terminal` fields.

- [ ] **Step 4: Run receipt/schema RED**

```powershell
uv run pytest -q tests/artifacts/test_receipts.py tests/diagnostics/test_grid_sample_attribution.py -k "receipt or schema or semantic or classify"
```

- [ ] **Step 5: Register the new receipt and implement closed schema**

Add only:

```python
(_A7_RECEIPT_TYPE, 1): _SCHEMA_ROOT / "grid-sample-attribution-receipt.schema.json"
```

to `_ALLOWED_SCHEMAS`, include the type in the non-empty run-ID set, and dispatch it to `_validate_grid_sample_attribution_consistency(normative, metadata)`. Keep every valid existing receipt behavior unchanged; the only cross-schema hardening is rejection of arrays that already exceed an existing `maxItems` declaration.

Implement the two previously RED schema keywords before registering the A7 schema. Error messages are `"<location> has too many items"` for `maxItems` and `"<location> must match exactly one schema"` for `oneOf`; candidate validation must not mutate input or suppress non-schema exceptions.

- [ ] **Step 6: Implement one pure classifier used by producer and independently mirrored by validator**

Production `classify_aggregate()` returns a canonical classification document. The validator recomputes the decision using its own parsing and comparisons in `receipts.py`; it may share only general canonical JSON hashing, not call the production classifier.

Decision order is exact:

```text
1. Any identity/count/parent/evidence/instrumentation invariant false -> INCONCLUSIVE.
2. Traverse the common callback order; require all earlier operations exact on all six roles.
3. First operation with exact forward value/grid/result/incoming and differing outgoing role is candidate.
4. If candidate has matching isolated-VJP outgoing divergence for that role -> ATTRIBUTED.
5. If a candidate exists but isolated proof is absent/exact/mismatched -> INCONCLUSIVE.
6. If no candidate, all instrumented six-role and isolated outgoing evidence is exact, and at least two instrumented parameter inventory digests differ -> NOT_ATTRIBUTED.
7. Otherwise -> INCONCLUSIVE.
```

Do not introduce a numerical tolerance or use A3 replay thresholds.

- [ ] **Step 7: Implement descriptive comparison inventories**

Aggregate creation loads and validates exact stored component receipts and their bound tensor bundles by run ID and file SHA-256, two bundles at a time, then releases them before loading the next pair. It emits:

- every pairwise trainable-parameter tensor comparison for the two controls plus five instrumented replicas;
- every pairwise six-role operation comparison for five instrumented replicas;
- every pairwise five-role operation comparison (`forward_value`, `forward_grid`, `forward_result`, `incoming_result_gradient`, and each outgoing role) for five isolated replicas;
- exact inventory-digest equality matrices and the common callback order.

Comparisons are evidence only; classification uses byte-digest equality except for finiteness/shape identity.

- [ ] **Step 8: Run GREEN for receipt/classification**

```powershell
uv run pytest -q tests/diagnostics/test_tensor_evidence.py tests/diagnostics/test_grid_sample_attribution.py tests/artifacts/test_receipts.py
uv run black --check src/vision_active_learning_loop/diagnostics src/vision_active_learning_loop/artifacts/receipts.py tests/diagnostics tests/artifacts/test_receipts.py
uv run ruff check src/vision_active_learning_loop/diagnostics src/vision_active_learning_loop/artifacts/receipts.py tests/diagnostics tests/artifacts/test_receipts.py
git diff --check
```

---

### Task 5: Add the Lazy CLI and Fresh-Process A7 Runner With TDD

**Files:**
- Modify: `src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py`
- Create: `scripts/run_wave0_a7.ps1`
- Modify: `tests/diagnostics/test_grid_sample_attribution.py`

**Interfaces:**
- Lazy command: `val diagnose grid-sample-attribution`
- Subcommands: `control`, `instrumented`, `isolated-vjp`, `aggregate`
- Runner parameters: `RunId`, `ImageTag`, `ImageDigest`, `HostCampaignRoot`, `LeasePath`

Exact CLI options are:

```text
control:
  --environment --model-assets --model-contract --component-root
  --component-id --source-commit --run-id --output
instrumented:
  --environment --model-assets --model-contract --component-root
  --component-id --source-commit --run-id --output
  [--vjp-snapshot-output, required only for instrumented-0 and forbidden otherwise]
isolated-vjp:
  --environment --model-assets --model-contract --parent-instrumented-receipt
  --vjp-snapshot --component-root --component-id --source-commit --run-id --output
aggregate:
  --environment --model-assets --model-contract --components-root
  --source-commit --run-id --output
```

`tensor-bundle.vala7` is derived from the validated component root and is never a caller-selectable filename.

- [ ] **Step 1: Add RED CLI discovery and path-boundary tests**

Require `build_manifest()` to discover `diagnose grid-sample-attribution` without importing the module. Test each subcommand with monkeypatched engines and real receipt publication. Exact paths are:

```text
VAL_ARTIFACT_ROOT/wave0/receipts/environment.json
VAL_ARTIFACT_ROOT/wave0/receipts/model-assets.json
VAL_ARTIFACT_ROOT/wave0/receipts/model-contract.json
VAL_ARTIFACT_ROOT/a7/components/<component-id>/tensor-bundle.vala7
VAL_ARTIFACT_ROOT/a7/components/<component-id>/receipt.json
VAL_ARTIFACT_ROOT/a7/components/instrumented-0/vjp-snapshot.vala7
VAL_ARTIFACT_ROOT/a7/aggregate/receipt.json
```

Reject missing parents, wrong names, wrong component directory, links/junctions, existing output/bundle/snapshot, blank run ID, invalid ID-kind pair, parent run mismatch, `VAL_DATA_ROOT` set, and aggregate with missing/extra component roots. CLI errors return 2 on stderr without traceback and publish nothing.

- [ ] **Step 2: Add RED PowerShell parser and structural tests**

Parse `run_wave0_a7.ps1` with the PowerShell AST. Require:

```text
desktop Linux assumptions but no context switch
VAL_DATA_ROOT rejection
existing source/image-bound campaign root plus absent Wave 0 parent, component, bundle, snapshot, and aggregate destinations
exact source/image/base-image/lease bindings
environment -> assets -> model-contract preamble
control-0, control-1 in separate docker run calls
instrumented-0..4 in separate docker run calls
isolated-vjp-0..4 in separate docker run calls
aggregate exactly once after all twelve receipts
--network none for every model/VJP/aggregate stage
--gpus all for every diagnostic stage
read-only worktree mount and read-write fresh campaign mount
no feasibility command, checkpoint path, gate wave0, RDD, Wave 1, force, delete, retry loop, or reused run ID
```

Extract and execute `Write-NewText` and `Invoke-NativeCommandCapture` as existing runner tests do. Require a legal zero-byte audit log, correct stderr/exit capture, `FileMode.CreateNew`, and no `$Host` built-in-variable assignment.

- [ ] **Step 3: Implement CLI subcommands and exact metadata**

Decorate one `main()` with `@command("diagnose grid-sample-attribution")`. Use argparse subparsers with exact required options, including `--source-commit`, and require it to equal `VAL_SOURCE_COMMIT`. Reconstruct receipt argv as `['val', 'diagnose', 'grid-sample-attribution', *argv]`, set receipt exit code to 0 only after successful engine completion and bundle/snapshot verification, atomically publish once, print `RECORDED` for components or the aggregate terminal, and return 0. Any exception returns 2 and no receipt.

- [ ] **Step 4: Implement the dedicated runner**

Copy only the already-tested native capture/no-clobber text writer patterns; do not call the existing Wave 0 runner. The runner must:

1. require an already-claimed exact lease path bound to the run ID/GPU UUID;
2. require the supplied campaign root to be the already-claimed Task 7 root, verify its build/micro-check identity, and inspect/match the image tag/digest;
3. require every Wave 0 parent, component, bundle, snapshot, and aggregate destination to be absent, then create their fixed parents once;
4. run fresh environment, model-assets, and model-contract parents under the new run ID;
5. run the 12 replicas in the exact order `control-0`, `control-1`, `instrumented-0..4`, `isolated-vjp-0..4`;
6. verify each expected receipt/snapshot exists and hashes it before continuing;
7. invoke aggregate once;
8. write no-clobber stage logs/JSON, campaign result, full file manifest, historical-preservation record, and closure manifest;
9. preserve partial evidence and emit the inconclusive terminal on the first failure without retry;
10. release only the exact validated lease in `finally` through a no-clobber release record and rename to `<RunId>.released`.

The runner never prints or writes an A7 `PASS` token.

- [ ] **Step 5: Run focused GREEN including PowerShell tests**

```powershell
uv run pytest -q tests/diagnostics/test_tensor_evidence.py tests/diagnostics/test_grid_sample_attribution.py tests/artifacts/test_receipts.py
uv run black --check src/vision_active_learning_loop/diagnostics src/vision_active_learning_loop/artifacts/receipts.py tests/diagnostics tests/artifacts/test_receipts.py
uv run ruff check src/vision_active_learning_loop/diagnostics src/vision_active_learning_loop/artifacts/receipts.py tests/diagnostics tests/artifacts/test_receipts.py
uv lock --check
git diff --check
```

**Stop condition:** any path/CLI/runner test failure, an eleventh file, a production change outside the allowlist, or a runner path that can invoke feasibility/Wave 0/Wave 1.

---

### Task 6: Verify, Independently Review, and Commit the A7 Candidate

**Files:**
- Modify: only the exact ten-file allowlist
- Read: all source/tests/schemas/spec/plans and Task 1 baseline

- [ ] **Step 1: Run focused and complete CPU gates**

```powershell
uv run pytest -q tests/diagnostics/test_tensor_evidence.py tests/diagnostics/test_grid_sample_attribution.py tests/artifacts/test_receipts.py
uv run pytest -q
uv run black --check src/vision_active_learning_loop/diagnostics/__init__.py src/vision_active_learning_loop/diagnostics/tensor_evidence.py src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py src/vision_active_learning_loop/artifacts/receipts.py tests/diagnostics/__init__.py tests/diagnostics/test_tensor_evidence.py tests/diagnostics/test_grid_sample_attribution.py tests/artifacts/test_receipts.py
uv run ruff check src/vision_active_learning_loop/diagnostics/__init__.py src/vision_active_learning_loop/diagnostics/tensor_evidence.py src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py src/vision_active_learning_loop/artifacts/receipts.py tests/diagnostics/__init__.py tests/diagnostics/test_tensor_evidence.py tests/diagnostics/test_grid_sample_attribution.py tests/artifacts/test_receipts.py
uv lock --check
git diff --check
```

CPU mocks prove adapter/evidence/classification contracts only. They cannot be reported as CUDA attribution.

- [ ] **Step 2: Perform a fresh independent review**

Review the ten-file diff against Section 5.2.9 and this plan. Record findings by severity and require:

```text
Critical = 0
Important = 0
```

The review must explicitly inspect original-call transparency, hook return values, monkeypatch restoration, exact 2+5+5 counts, first-divergence traversal, snapshot integrity, no-clobber races, receipt semantic independence, CLI path boundaries, runner fresh-process guarantees, absence of optimizer/checkpoint/gate calls, and terminal wording.

- [ ] **Step 3: Verify allowlist and historical preservation**

```powershell
$Allowed = @(
 'schemas/grid-sample-attribution-receipt.schema.json',
 'scripts/run_wave0_a7.ps1',
 'src/vision_active_learning_loop/artifacts/receipts.py',
 'src/vision_active_learning_loop/diagnostics/__init__.py',
 'src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py',
 'src/vision_active_learning_loop/diagnostics/tensor_evidence.py',
 'tests/artifacts/test_receipts.py',
 'tests/diagnostics/__init__.py',
 'tests/diagnostics/test_grid_sample_attribution.py',
 'tests/diagnostics/test_tensor_evidence.py'
)
$Changed = @(git status --porcelain=v1 | ForEach-Object { $_.Substring(3).Replace('\','/') } | Sort-Object -Unique)
if (@(Compare-Object $Allowed $Changed).Count -ne 0) { throw 'A7 implementation allowlist mismatch' }
```

Recompute the complete Task 1 artifact/image/protected-Git baseline and seven fixed A6 hashes. Before A7 execution, require exact set equality, zero drift, and no untracked cache files.

- [ ] **Step 4: Create one append-only implementation commit**

```powershell
git config user.name kuotunyu
git config user.email 61350295+kuotunyu@users.noreply.github.com
git add -- schemas/grid-sample-attribution-receipt.schema.json scripts/run_wave0_a7.ps1 src/vision_active_learning_loop/artifacts/receipts.py src/vision_active_learning_loop/diagnostics/__init__.py src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py src/vision_active_learning_loop/diagnostics/tensor_evidence.py tests/artifacts/test_receipts.py tests/diagnostics/__init__.py tests/diagnostics/test_grid_sample_attribution.py tests/diagnostics/test_tensor_evidence.py
git diff --cached --name-only
git commit -m "feat: attribute A7 grid-sample backward"
```

Verify author/committer, parent, exact ten-file commit diff, clean linked worktree, and clean canonical main.

- [ ] **Step 5: Verify the committed candidate freshly and stop**

Repeat focused tests, complete CPU suite, targeted Black/Ruff, `uv lock --check`, `git diff --check`, history hashes, and Git cleanliness from the committed SHA. Report RED/GREEN evidence, counts, review result, exact diff, and candidate SHA.

Do not build an image, generate an A7 run ID, or acquire a GPU lease until the owner separately approves this exact implementation candidate for Tasks 7-8.

**Stop condition:** any test/quality/review/history/identity failure, Critical/Important finding, extra tracked file, or dirty worktree.

---

### Task 7: Build and CPU-Preflight One Fresh A7 Diagnostic Campaign

**Files:**
- Modify in Git: none
- Write outside Git: one new campaign root, image audit, CPU micro-check audit, and one GPU lease only after preflight

- [ ] **Step 1: Revalidate candidate and environment without redoing Tasks 1-6**

Require exact approved candidate SHA, branch, author/committer, ten-file commit diff, both Git states clean, Docker context `desktop-linux`, Linux Server health, Docker GPU collector showing exactly one RTX 4090, `VAL_DATA_ROOT` unset, no numeric compute process, no active project lease/container, complete Task 1 history match, and exact historical Option A image identity. Do not change Docker settings or repair Git.

- [ ] **Step 2: Create one new identity and build exactly once**

```powershell
$SourceSha = (git rev-parse HEAD).Trim()
$RunId = 'wave0-a7-' + [DateTime]::UtcNow.ToString('yyyyMMddTHHmmssfffZ')
$ImageTag = "vision-active-learning-loop:wave0-a7-$($SourceSha.Substring(0,12))-$RunId"
$CampaignRoot = "D:\vision-active-learning-loop-artifacts\wave0\a7-runs\$RunId"
if (Test-Path -LiteralPath $CampaignRoot) { throw 'fresh A7 campaign root required' }
$CampaignParent = Split-Path -Parent $CampaignRoot
if (-not (Test-Path -LiteralPath $CampaignParent -PathType Container)) { throw 'A7 campaign parent missing' }
New-Item -ItemType Directory -Path $CampaignRoot -ErrorAction Stop | Out-Null
$AuditRoot = New-Item -ItemType Directory -Path (Join-Path $CampaignRoot 'audit') -ErrorAction Stop
```

Build once with `--no-cache` from `docker/wave0.Dockerfile`, with OCI labels for source SHA, run ID, spec commit, plan commit, and base digest. Record exact argv/stdout/stderr/exit, inspect JSON, image ID, repo digest when available, and labels through no-clobber audit files. Any build failure preserves the root and stops; no rebuild.

- [ ] **Step 3: Run a CPU-only no-model/no-CUDA micro-check**

Run the fresh image with `--network none` and no `--gpus` option, no model cache, and no model forward. Verify:

```text
source SHA and exact new source-file hashes
CLI manifest discovery without importing diagnostic/model modules
schema registration and one valid tiny receipt per branch
canonical tensor bytes for four dtypes
snapshot encode/decode/corruption rejection
all three classifier branches on synthetic literal evidence
runner PowerShell parse and forbidden-token scan
VAL_DATA_ROOT unset
```

Publish the micro-check audit with `FileMode.CreateNew`. This proves packaging and CPU contract only, not CUDA attribution.

- [ ] **Step 4: Acquire the exclusive RTX 4090 lease**

Only after the micro-check passes, atomically claim the project lease for `$RunId`, bind GPU UUID, process/container inventory, source SHA, image ID, timestamps, and owner authorization, then recheck no competing numeric process. A busy or unsafe GPU stops without CPU fallback.

**Stop condition:** any candidate, Docker, image, micro-check, history, GPU, or lease mismatch. Preserve the fresh campaign/image/audit and do not retry.

---

### Task 8: Execute Exactly One A7 Campaign, Classify, Preserve, and Stop

**Files:**
- Modify in Git: none
- Execute: `scripts/run_wave0_a7.ps1` once
- Write outside Git: only the fresh A7 campaign and lease-release evidence

- [ ] **Step 1: Invoke the approved runner exactly once**

```powershell
& .\scripts\run_wave0_a7.ps1 `
    -RunId $RunId `
    -ImageTag $ImageTag `
    -ImageDigest $ImageId `
    -HostCampaignRoot $CampaignRoot `
    -LeasePath $LeasePath
$A7Exit = $LASTEXITCODE
```

Do not wrap this in a retry loop. The runner performs the fresh parent stages, two controls, five instrumented replicas, five isolated replicas, and aggregate once in the registered order.

- [ ] **Step 2: Verify component identities and evidence before trusting aggregate**

Require exact 2+5+5 component IDs, separate Docker process audit records, one common run/source/image/base/GPU/fixture/model identity, complete parent hashes, exactly nine warnings per replica, exact scalar loss across seven model replicas, complete gradient inventories, exactly nine instrumented operations, one common callback order, one verified tensor bundle per component, one additional 27-tensor VJP snapshot only at `instrumented-0`, and five isolated parents bound to that exact snapshot/receipt.

Require no optimizer/scheduler/checkpoint/feasibility/gate files or argv values anywhere in the A7 root.

- [ ] **Step 3: Independently verify aggregate classification**

Run the receipt validator against the stored aggregate and recompute all component file hashes from disk. Require the stored status/terminal to match one and only one closed classifier branch. Report candidate operation/role only for `ATTRIBUTED`; report differing instrumented parameter-inventory digests only for `NOT_ATTRIBUTED`; otherwise report the exact inconclusive errors.

- [ ] **Step 4: Rehash history, close campaign, release lease, and stop**

Require every Task 1 baseline entry and all seven A6 fixed hashes unchanged, the candidate Git worktrees clean at the approved SHA, `VAL_DATA_ROOT` unset, no RDD/Wave 1 artifact, and no active project container. When checking additions, exclude only the exact new `$CampaignRoot` and exact new `$ImageTag`; any other new historical-root file or Wave 0 image is drift. Validate the no-clobber campaign result, full file manifest, historical-preservation record, closure manifest, and lease release record.

Every outcome stops immediately at one of:

```text
WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
```

Do not fix, rebuild, rerun, change thresholds, select a new model/kernel, run Wave 0 aggregate, access RDD, or begin Wave 1. Every A7 result returns to owner design review.

---

## Plan Self-Review Record

- [x] Every Section 5.2.9 statement maps to an exact file, type, test, validator, runner gate, execution step, or terminal.
- [x] The ten-file tracked allowlist is exact; an eleventh tracked file is a hard stop.
- [x] A7 is isolated from A6 feasibility, checkpoint, numerical-replay, gate, Dockerfile, dependency, model/config, and research surfaces.
- [x] RED tests precede implementation for tensor bytes/snapshots, adapter/hooks, replica engines, schema/semantic validation/classification, CLI, and runner.
- [x] Stable operation IDs, six instrumented roles, three snapshot roles, 2+5+5 replica IDs, callback traversal, and snapshot parent are consistent across all tasks.
- [x] The adapter calls the saved original pinned function once with exact arguments, returns the original result, restores the callable in `finally`, and permits only a `None` hook return.
- [x] Canonical bytes, dtype tokens, little-endian rule, counts, hashes, norms, comparisons, component bundles, the restricted VJP snapshot, corruption rejection, and no-clobber publication are closed and type-consistent.
- [x] Controls and instrumented replicas use the exact A6 model/batch/BF16/Math-only/warning boundary and stop before clip/update/checkpoint.
- [x] Isolated replicas execute only nine original grid-sample VJPs from one verified snapshot; no model/dataset/optimizer/checkpoint path is reachable.
- [x] Instrumentation validity does not incorrectly require parameter-gradient equality.
- [x] First divergence uses callback order and exact earlier events; isolated VJP must reproduce the same outgoing role before attribution.
- [x] NOT_ATTRIBUTED requires exact model-operation and isolated-operation outputs plus reproduced differing full parameter gradients; a fully exact run remains inconclusive.
- [x] No numerical tolerance or A3 threshold is introduced; magnitudes are descriptive only.
- [x] Component and aggregate receipts never use `PASS`; all three terminals include `WAVE0_NOT_PASSED` and `WAVE1_FORBIDDEN`.
- [x] Schema and central semantic validator independently reject forged hashes, parents, counts, inventories, comparisons, decisions, and terminal claims.
- [x] Every component is a fresh Docker process, every destination is fresh/no-clobber, and at most one approved A7 campaign is executable with no retry.
- [x] A6 and all earlier evidence/images/campaigns remain immutable and are fully rehashed before and after A7.
- [x] CPU tests/micro-checks do not claim CUDA attribution; the RTX 4090 diagnostic begins only after image approval and exclusive lease.
- [x] Model, revisions, processor, queries, classes, BF16, dependencies, seed, formal seeds/budgets, fit counts, VRAM ceiling, thresholds, and research claims remain unchanged.
- [x] RDD, Wave 0 aggregate, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.
- [x] Placeholder, contradiction, ambiguity, scope-drift, exact-path, type-consistency, evidence-preservation, and terminal scans have no unresolved finding.

## Execution Selection

The owner delegated execution-method selection. After this plan commit receives written owner implementation-plan review, use **Inline Execution** in the existing registered linked worktree with `superpowers:executing-plans`. Do not dispatch subagents. Implementation Tasks 1-6 then stop for separate owner candidate approval; Tasks 7-8 begin only for that exact approved candidate and stop at the A7 owner design checkpoint.
