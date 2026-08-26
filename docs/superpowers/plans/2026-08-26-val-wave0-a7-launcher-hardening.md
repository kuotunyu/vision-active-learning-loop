# Wave 0 A7 Launch Orchestration Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execute inline in the registered worktree; do not dispatch subagents unless the owner explicitly requests them.

**Goal:** Replace ad hoc session-side A7 Task 7 commands with one checked-in, tested launcher and one production-only CPU micro-check so a separately authorized fresh A7 attempt can reach the existing Task 8 runner without weakening identity, history, lease, no-clobber, or no-retry gates.

**Architecture:** `scripts/start_wave0_a7.ps1` owns the complete Task 7 state machine: registered-worktree and environment checks, augmented history, fresh build identity, CPU micro-check, atomic GPU lease, exactly-once delegation to the frozen Task 8 runner, and failure closure. `scripts/run_wave0_a7_cpu_microcheck.py` runs inside the fresh production image without pytest, test imports, model forward, network, or CUDA and returns one closed JSON result. The existing `scripts/run_wave0_a7.ps1` remains byte-for-byte unchanged and is invoked only after every Task 7 binding is closed.

**Tech Stack:** Windows 11; PowerShell 7; Python 3.12.11; uv 0.8.15; pytest 9.0.2 for development only; Black 22.6.0; Ruff 0.16.4; Docker Desktop Linux engine; NVIDIA CUDA 12.6 base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`; PyTorch 2.12.0+cu126; RTX 4090 24 GB.

## Global Constraints

- The authoritative launcher-hardening specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `5d6ffe0567a4aeed0bcaceed7a33416b04f41925`, especially Section 5.2.10.
- Implementation entry branch is exactly `codex/wave0-model-contract`. Entry HEAD must be the owner-approved commit containing this plan, its first parent must be `5d6ffe0567a4aeed0bcaceed7a33416b04f41925`, and that plan commit must change only `docs/superpowers/plans/2026-08-26-val-wave0-a7-launcher-hardening.md`.
- The implementation tracked-file allowlist is closed to exactly four new files:
  1. `scripts/start_wave0_a7.ps1`
  2. `scripts/run_wave0_a7_cpu_microcheck.py`
  3. `tests/gates/test_wave0_a7_launcher.py`
  4. `tests/diagnostics/test_wave0_a7_cpu_microcheck.py`
- A necessary fifth tracked file or any modification to an existing tracked file is a hard stop for renewed written scope review. In particular, do not modify `scripts/run_wave0_a7.ps1`, a model or diagnostic module, a receipt validator or schema, a Dockerfile, configuration, fixture, dependency declaration, `uv.lock`, the approved specification, this plan, or historical evidence during implementation.
- Current immutable history contains 64,011 Wave 0 artifact files, 14 `vision-active-learning-loop:wave0-*` images, 68 original protected Git paths, three closed A7 launch campaigns, and the original Task 1 baseline SHA-256 `4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd`.
- The latest closed A7 campaign is `wave0-a7-20260826T021633738Z`; its failed image is `sha256:958713719023c74c6be255f3baa513a17a36022165a6714f183ca8ecfbcd250a`, and its closure SHA-256 is `e983a044b63ca4bbf36f8ccfe8ea6041f94a796a20b397a926740e74e764a728`. Preserve it and every earlier campaign/image byte-for-byte.
- Required build labels are exactly `org.opencontainers.image.revision`, `org.opencontainers.image.val.run_id`, `org.opencontainers.image.val.spec_commit`, `org.opencontainers.image.val.plan_commit`, and `org.opencontainers.image.base.digest`. They appear as five separate `--label`, `key=value` argv pairs in that order.
- No implementation test may build an OCI image, use the real GPU, acquire the real project lease, load a model, access RDD or any path named by `VAL_DATA_ROOT`, invoke Task 8 against real Docker, or make a remote request. A controlled subprocess may set `VAL_DATA_ROOT` to a nonexistent sentinel solely to prove fail-closed rejection. External Docker and Task 8 processes are represented by controlled temporary executables at their process boundary.
- The checked-in micro-check imports no `pytest` or `tests.*`, installs nothing, uses no network or model cache, performs no model forward, accepts no hidden dataset path, and finishes with `torch.cuda.is_initialized() == false`.
- The launcher performs no recovery action: no checkout, reset, rebase, worktree creation, Docker context change, prune, retag, evidence move/delete, retry loop, CPU fallback, threshold change, or Wave 1 action.
- After a campaign root is claimed, every failure closes through new diagnostic, preservation, campaign-result, pre-closure-manifest, and closure files using `FileMode.CreateNew`. Before claim, failure creates no campaign directory, image, or lease.
- A build, CPU micro-check, and Task 8 runner can each be invoked at most once for one run ID. Implementation approval does not authorize any of those real executions.
- Author and committer name is `kuotunyu`; email is `61350295+kuotunyu@users.noreply.github.com`. All commits are append-only; amend, rebase, reset, squash, force, push, merge, tag, Release, and publication remain forbidden.
- `VAL_DATA_ROOT` remains unset. RDD and Wave 1 remain forbidden.

---

## File Map

| File | Responsibility |
|---|---|
| `scripts/run_wave0_a7_cpu_microcheck.py` | Production-runtime lazy-manifest, source-hash, tensor-byte, snapshot, receipt, classifier, forbidden-import, and CUDA-uninitialized micro-check |
| `tests/diagnostics/test_wave0_a7_cpu_microcheck.py` | Independent CPU RED/GREEN coverage for the micro-check API and CLI without importing A7 test builders |
| `scripts/start_wave0_a7.ps1` | Task 7 identity, history, build, inspect, micro-check, lease, exactly-once Task 8 delegation, and complete failure closure |
| `tests/gates/test_wave0_a7_launcher.py` | Real PowerShell behavior tests with controlled filesystem roots and temporary external process adapters |

No existing tracked file changes.

---

### Task 1: Revalidate Entry Identity and Freeze the Pre-Implementation Baseline

**Files:**
- Read: Git metadata, approved spec/plan lineage, current 64,011 artifact records, 14 image identities, 68 protected Git records, and seven fixed A6 evidence files
- Modify in Git: none
- Write outside Git: one never-existing path formed as `Join-Path $env:TEMP ("val-a7-launcher-prechange-{0}.json" -f $PlanCommit)` using `FileMode.CreateNew`

**Interfaces:**
- Consumes: registered branch `codex/wave0-model-contract`, spec commit `5d6ffe0567a4aeed0bcaceed7a33416b04f41925`, and the owner-approved plan commit
- Produces: a complete pre-implementation baseline path/SHA-256 used by Tasks 6 and 7

- [ ] **Step 1: Resolve and validate the registered worktree**

Run:

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-launcher-hardening.md'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$SpecCommit = '5d6ffe0567a4aeed0bcaceed7a33416b04f41925'
git worktree list --porcelain
git branch --show-current
git rev-parse HEAD
git rev-parse "$PlanCommit^"
git diff-tree --no-commit-id --name-only -r $PlanCommit
git status --porcelain=v1
git -C '<repo>' status --porcelain=v1
```

Expected: one registered worktree on `codex/wave0-model-contract`; `HEAD == $PlanCommit`; `$PlanCommit^ == $SpecCommit`; the plan commit changes only `$PlanPath`; both status commands are empty.

- [ ] **Step 2: Verify immutable evidence and environment remain untouched**

Run read-only checks for:

```text
artifact files = 64,011
Wave 0 images = 14
protected Git records = 68
latest A7 closure = e983a044b63ca4bbf36f8ccfe8ea6041f94a796a20b397a926740e74e764a728
Docker context = desktop-linux
Docker server OS = linux
active project containers = 0
active project leases = 0
VAL_DATA_ROOT = unset
```

Also recompute the seven fixed A6 hashes registered in Section 5.2.9. Any mismatch stops before creating a baseline.

- [ ] **Step 3: Publish the complete pre-implementation baseline**

Use PowerShell and .NET `FileMode.CreateNew` to write a compact JSON document assembled from these exact fields:

```powershell
$BaselineDocument = [ordered]@{
    schema_version = 1
    plan_commit = $PlanCommit
    parent_baseline_sha256 = '4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd'
    artifact_root = 'D:\vision-active-learning-loop-artifacts\wave0'
    artifact_files = $ArtifactRecords
    images = $ImageRecords
    protected_git = $ProtectedGitRecords
}
```

The three arrays contain complete sorted records with exact path/tag, size where applicable, and SHA-256/image ID. Parse the file back, require counts 64,011/14/68, and record its SHA-256 in the task report.

**Stop condition:** any Git, environment, count, hash, image, link, path, or baseline-publication mismatch.

---

### Task 2: Implement the Production-Only CPU Micro-Check with TDD

**Files:**
- Create: `tests/diagnostics/test_wave0_a7_cpu_microcheck.py`
- Create: `scripts/run_wave0_a7_cpu_microcheck.py`

**Interfaces:**
- Consumes: a read-only workspace root and a source-inventory JSON file produced by the launcher
- Produces: `run_microcheck(workspace_root: Path, source_inventory_path: Path) -> dict[str, object]` and `main(argv: Sequence[str] | None = None) -> int`
- CLI: `python /workspace/scripts/run_wave0_a7_cpu_microcheck.py --workspace-root /workspace --source-inventory /audit/21-a7-source-inventory.json`
- Stdout: exactly one compact UTF-8 JSON object followed by one newline; stderr empty on success

- [ ] **Step 1: Write the RED tests for lazy discovery and source inventory**

Create a test-local loader using `importlib.util.spec_from_file_location()` and tests with these exact names:

```python
def test_microcheck_discovers_a7_command_before_diagnostic_import(tmp_path): ...
def test_microcheck_rejects_changed_source_inventory(tmp_path): ...
def test_microcheck_does_not_import_pytest_tests_or_models(tmp_path): ...
```

The valid inventory is a literal JSON object with `schema_version == 1`, the reviewed source commit, and exact `{path, sha256}` records for:

```text
scripts/start_wave0_a7.ps1
scripts/run_wave0_a7_cpu_microcheck.py
scripts/run_wave0_a7.ps1
src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py
src/vision_active_learning_loop/diagnostics/tensor_evidence.py
src/vision_active_learning_loop/artifacts/receipts.py
schemas/grid-sample-attribution-receipt.schema.json
```

The test fixture creates a complete isolated temporary tree for those seven paths, including deterministic launcher content before the real launcher exists; its literal expected digests are independent of production inventory construction. Production diagnostic imports still resolve from the installed project, while every file hashed or opened through `workspace_root` comes from that temporary tree.

The source-mutation test changes one digest to 64 `0` characters and expects `MicrocheckError("source inventory mismatch")`. The forbidden-import test launches a subprocess with an import blocker for `pytest`, `tests`, and `vision_active_learning_loop.models`; success proves the production path does not require them.

- [ ] **Step 2: Run the lazy/source tests to verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -q `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py `
  -k 'discovers or source_inventory or does_not_import'
```

Expected: collection or test failure because `scripts/run_wave0_a7_cpu_microcheck.py` and its API do not exist. A syntax or fixture error is not acceptable RED evidence.

- [ ] **Step 3: Implement the minimal lazy/source boundary**

Define these exact public names:

```python
class MicrocheckError(ValueError):
    """Raised when the production-only A7 CPU contract is not closed."""


def run_microcheck(
    workspace_root: Path, source_inventory_path: Path
) -> dict[str, object]:
    ...


def main(argv: Sequence[str] | None = None) -> int:
    ...
```

`run_microcheck()` first rejects a set `VAL_DATA_ROOT`, requires safe regular non-link inputs, hashes the seven exact paths, and calls `build_manifest()` before importing any diagnostic module. It requires:

```text
diagnose grid-sample-attribution
-> vision_active_learning_loop.diagnostics.grid_sample_attribution:main
```

Only after that assertion may it import PyTorch, attribution, tensor-evidence, and receipt-validation production APIs.

- [ ] **Step 4: Run the lazy/source tests to verify GREEN**

Run the Step 2 command. Expected: all selected tests pass with no warning and no bytecode file in the worktree.

- [ ] **Step 5: Write RED tests for tensor and snapshot evidence**

Add:

```python
def test_microcheck_proves_four_canonical_dtypes(tmp_path): ...
def test_microcheck_round_trips_exact_27_tensor_snapshot(tmp_path): ...
def test_microcheck_rejects_corrupted_snapshot(tmp_path): ...
```

Hand-derived expected bytes are:

```python
{
    "bfloat16": struct.pack("<HH", 0x3F80, 0xC000),
    "float16": struct.pack("<ee", 1.0, -2.0),
    "float32": struct.pack("<ff", 1.0, -2.0),
    "float64": struct.pack("<dd", 1.0, -2.0),
}
```

Snapshot names are the sorted Cartesian product of the nine production `OPERATION_IDS` and `forward_value`, `forward_grid`, `incoming_result_gradient`. Flip the last payload byte and require `TensorEvidenceError`.

- [ ] **Step 6: Run the tensor/snapshot tests to verify RED**

Run:

```powershell
uv run --no-sync pytest -q `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py `
  -k 'canonical or snapshot'
```

Expected: assertions fail because the result does not yet report four dtype checks, 27 decoded names, and corruption rejection.

- [ ] **Step 7: Implement tensor/snapshot checks**

Use only production `canonical_tensor_bytes()`, `encode_snapshot()`, and `decode_snapshot()`. Temporary snapshot files live under `tempfile.TemporaryDirectory()` and are removed before return. The result fields are exact:

```json
{
  "canonical_dtypes": ["bfloat16", "float16", "float32", "float64"],
  "snapshot_tensor_count": 27,
  "snapshot_corruption_rejected": true
}
```

- [ ] **Step 8: Run the tensor/snapshot tests to verify GREEN**

Run the Step 6 command. Expected: all selected tests pass.

- [ ] **Step 9: Write RED tests for four receipt kinds and three classifications**

Add tests named:

```python
def test_microcheck_validates_four_closed_receipt_kinds(tmp_path): ...
def test_microcheck_exercises_three_literal_classifier_branches(tmp_path): ...
def test_microcheck_finishes_without_cuda_initialization(tmp_path): ...
def test_microcheck_cli_emits_one_json_line(tmp_path): ...
```

Independent literal builders in the micro-check may use loops over fixed production operation IDs, but they must not import or copy a function from `tests/diagnostics/test_grid_sample_attribution.py`. Required result values are:

```json
{
  "receipt_kinds": ["control", "instrumented", "isolated-vjp", "aggregate"],
  "classifier_statuses": ["ATTRIBUTED", "INCONCLUSIVE", "NOT_ATTRIBUTED"],
  "cuda_initialized": false,
  "status": "RECORDED"
}
```

- [ ] **Step 10: Run receipt/classifier/CLI tests to verify RED**

Run:

```powershell
uv run --no-sync pytest -q tests/diagnostics/test_wave0_a7_cpu_microcheck.py
```

Expected: the new receipt/classifier/CLI assertions fail while the earlier tests remain green.

- [ ] **Step 11: Implement the closed micro-check result**

Create deterministic private builders `_literal_component()` and `_literal_branches()` from literal identities, fixed digest strings, fixed finite records, and production `OPERATION_IDS`. Validate one full receipt for each kind against `/workspace/schemas/grid-sample-attribution-receipt.schema.json`; call production `classify_aggregate()` for all three branches and compare complete canonical classification documents, not only statuses. Return only JSON-serializable scalar/list/map values with `allow_nan=False`. `main()` prints exactly one compact line and returns zero; it prints one compact error document to stderr and returns nonzero on `MicrocheckError`, `TensorEvidenceError`, receipt-validation error, malformed JSON, or assertion failure.

- [ ] **Step 12: Run the complete micro-check test file to verify GREEN**

Run:

```powershell
uv run --no-sync pytest -q tests/diagnostics/test_wave0_a7_cpu_microcheck.py
uv run --no-sync black --check `
  scripts/run_wave0_a7_cpu_microcheck.py `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py
uvx --offline ruff check `
  scripts/run_wave0_a7_cpu_microcheck.py `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py
```

Expected: zero failures and zero formatting/lint findings.

- [ ] **Step 13: Commit the micro-check slice**

```powershell
git add -- `
  scripts/run_wave0_a7_cpu_microcheck.py `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py
git -c user.name=kuotunyu `
    -c user.email=61350295+kuotunyu@users.noreply.github.com `
    commit -m "feat: add A7 production microcheck"
```

Verify the commit contains exactly those two files and the worktree is clean.

---

### Task 3: Implement Typed Docker Build and Image Identity Gates with TDD

**Files:**
- Create: `tests/gates/test_wave0_a7_launcher.py`
- Create: `scripts/start_wave0_a7.ps1`

**Interfaces:**
- Produces PowerShell functions `Write-A7NewText`, `Invoke-A7Native`, `New-A7BuildArguments`, `Assert-A7BuildArguments`, and `Assert-A7ImageInspect`
- `New-A7BuildArguments` consumes source/run/spec/plan/base/tag values and returns `[string[]]`
- External process boundary consumes executable path plus `[string[]]` without a shell-command string

- [ ] **Step 1: Write RED behavior tests for five independent labels**

The Python test extracts PowerShell functions from the launcher AST, invokes them in `powershell -NoProfile -NonInteractive`, converts the returned array to JSON, and asserts this exact suffix structure:

```python
expected_pairs = [
    ["--label", f"org.opencontainers.image.revision={source}"],
    ["--label", f"org.opencontainers.image.val.run_id={run_id}"],
    ["--label", f"org.opencontainers.image.val.spec_commit={spec}"],
    ["--label", f"org.opencontainers.image.val.plan_commit={plan}"],
    ["--label", f"org.opencontainers.image.base.digest={base}"],
]
```

Add rejection cases for one concatenated value, duplicate key, blank value, malformed source/spec/plan SHA, wrong base digest, sixth label, and a label value containing whitespace followed by `org.opencontainers.image.`.

- [ ] **Step 2: Run label tests to verify RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k label
```

Expected: failure because the launcher/functions do not exist.

- [ ] **Step 3: Implement typed build arguments and validation**

`New-A7BuildArguments` creates `System.Collections.Generic.List[string]`, calls `.Add('--label')` and `.Add("key=$Value")` separately five times, and returns `.ToArray()`. Its fixed build prefix is:

```text
build --no-cache --progress plain --file docker/wave0.Dockerfile
```

Its fixed suffix is:

```powershell
'--tag', $ImageTag, '.'
```

`Assert-A7BuildArguments` requires exactly five label flags, exact order/keys/values, no joined assignment, and one final context `.`. It runs before Docker build and the same argv is stored in the build audit afterward.

- [ ] **Step 4: Run label tests to verify GREEN**

Run the Step 2 command. Expected: all label tests pass.

- [ ] **Step 5: Write RED tests for native capture and image inspect**

Add:

```python
def test_launcher_preserves_zero_byte_stdout_and_exit_code(tmp_path): ...
def test_launcher_passes_argv_without_shell_reparsing(tmp_path): ...
def test_launcher_accepts_exact_single_image_inspect(tmp_path): ...
def test_launcher_rejects_missing_concatenated_or_wrong_image_labels(tmp_path): ...
```

Use a temporary external executable that writes received argv as JSON, emits controlled stdout/stderr, and exits with a controlled code. The exact valid inspect fixture contains one image with the reviewed ID and all five required labels as separate JSON properties. Never call real Docker in these tests.

- [ ] **Step 6: Run native/inspect tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'native or inspect or stdout'
```

Expected: failure because capture and inspect behavior is absent.

- [ ] **Step 7: Implement native capture, no-clobber logs, and inspect validation**

`Invoke-A7Native` uses `System.Diagnostics.ProcessStartInfo.ArgumentList`, `UseShellExecute = $false`, independent async stdout/stderr reads, and the real integer exit code. `Write-A7NewText` accepts `[AllowEmptyString()]`, encodes UTF-8 without BOM, opens `FileMode.CreateNew`, writes exactly the supplied text, and flushes to disk. `Assert-A7ImageInspect` requires one image, exact ID/tag binding, and exact values for all five required keys; unrelated base-image metadata may remain.

- [ ] **Step 8: Run native/inspect tests to verify GREEN**

Run the Step 6 command. Expected: all selected tests pass.

---

### Task 4: Implement Git, History, Docker/GPU Preflight, and Atomic Lease Gates with TDD

**Files:**
- Modify: `scripts/start_wave0_a7.ps1`
- Modify: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Produces `Resolve-A7Worktree`, `New-A7AugmentedBaseline`, `Test-A7DockerGpuPreflight`, and `New-A7Lease`
- Augmented baseline fields: `schema_version`, `source_commit`, `parent_baseline_sha256`, `artifact_root`, `artifact_files`, `images`, `protected_git`
- Lease fields: `schema_version`, `owner_authorization_id`, `run_id`, `source_commit`, `spec_commit`, `plan_commit`, `image_tag`, `image_id`, `base_image_digest`, `gpu_uuid`, `campaign_root`, `historical_baseline_path`, `historical_baseline_sha256`, `build_audit_sha256`, `microcheck_audit_sha256`, `host_processes`, `containers`, `claimed_at`

- [ ] **Step 1: Write RED tests for registered-worktree and clean-state enforcement**

Controlled Git fixtures prove exact branch/HEAD/common-dir resolution and rejection of wrong branch, wrong HEAD, multiple matching worktrees, linked dirt, canonical-main dirt, staged content, and unregistered paths. The launcher receives mandatory parameters:

```powershell
param(
    [Parameter(Mandatory = $true)][string]$ExpectedSourceCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedPlanCommit,
    [Parameter(Mandatory = $true)][string]$ExpectedBranch,
    [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
)
```

- [ ] **Step 2: Run Git identity tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'worktree or git_identity'
```

Expected: the assertions fail because the resolver/preflight is absent.

- [ ] **Step 3: Implement registered-worktree resolution and reject-only identity checks**

Parse `git worktree list --porcelain`; select exactly one worktree whose branch and HEAD equal mandatory expected values; confirm `git-common-dir`; require empty linked/canonical/staging status. Do not invoke any mutating Git command.

- [ ] **Step 4: Run Git identity tests to verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

- [ ] **Step 5: Write RED tests for augmented historical baseline**

Temporary roots cover:

```text
valid original subset plus two preserved failed campaigns
missing root artifact
changed root size/hash
duplicate/extra unrecorded path
changed protected Git record
changed historical image ID
symlink/reparse baseline path
existing augmented destination
stable sorted output and parse-back counts
```

Expected root-baseline SHA is the fixed Task 1 hash. Test expectations use hand-written literal file contents and SHA-256, not the production baseline builder.

- [ ] **Step 6: Run history tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k history
```

Expected: failure because `New-A7AugmentedBaseline` is absent.

- [ ] **Step 7: Implement full history verification and no-clobber augmented publication**

Rehash every current file; inspect every current image through the external process boundary; require the fixed original baseline as an unchanged subset; reject duplicate paths/tags; publish a complete sorted JSON file outside the artifact root through `Write-A7NewText`; parse it back and recompute its SHA-256 before campaign claim.

- [ ] **Step 8: Run history tests to verify GREEN**

Run the Step 6 command. Expected: all selected tests pass.

- [ ] **Step 9: Write RED tests for Docker/GPU ordering and atomic lease contention**

Tests provide literal collector outputs for one RTX 4090 and WDDM `[N/A]` GUI rows. Reject wrong context, missing Linux server, zero/two GPUs, wrong name/UUID, a numeric CUDA compute row, active project container, active lease, set `VAL_DATA_ROOT`, missing build audit, missing micro-check audit, changed audit hashes, existing lease destination, and symlinked lease root. Assert no lease file exists before a valid micro-check result.

- [ ] **Step 10: Run Docker/GPU/lease tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'docker or gpu or lease'
```

Expected: failure because preflight and lease functions are absent.

- [ ] **Step 11: Implement Docker/GPU preflight and atomic lease creation**

Require `desktop-linux`, Linux server/info, `docker-desktop` running, exactly one collector CSV row for UUID `GPU-*` and name `NVIDIA GeForce RTX 4090`, no numeric compute process, no active project container/lease, and unset `VAL_DATA_ROOT`. Only after recomputing build/micro-check audit hashes may `New-A7Lease` publish the exact lease through `FileMode.CreateNew` and parse/hash it back.

- [ ] **Step 12: Run Docker/GPU/lease tests to verify GREEN**

Run the Step 10 command. Expected: all selected tests pass.

---

### Task 5: Implement the One-Shot Task 7 State Machine and Complete Failure Closure with TDD

**Files:**
- Modify: `scripts/start_wave0_a7.ps1`
- Modify: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Produces `Close-A7Campaign` and `Invoke-A7Launch`
- State order: `UNCLAIMED`, `CAMPAIGN_CLAIMED`, `IMAGE_VERIFIED`, `CPU_VERIFIED`, `GPU_LEASED`, `TASK8_INVOKED_ONCE`, `CLOSED`
- Delegates exactly once to the reviewed absolute `scripts/run_wave0_a7.ps1` path

- [ ] **Step 1: Write RED tests for pre-claim and post-claim state transitions**

Parameterize failure injection at campaign claim, build exit, build argv audit, image inspect, source inventory, CPU micro-check exit/blank/malformed payload, audit hash, GPU preflight, lease claim, Task 8 exit, preservation, manifest, and lease release. Assert:

```text
pre-claim failure -> no campaign/image/lease
post-claim failure -> diagnostic + 30 + 40 + 41 + 51
no destination overwritten
no state skipped or repeated
micro-check count <= 1
Task 8 count <= 1
```

- [ ] **Step 2: Run transition tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'transition or closure'
```

Expected: failure because the state machine and closure do not exist.

- [ ] **Step 3: Implement fail-closed campaign claim and closure**

After all unclaimed checks and augmented-baseline publication, generate one UTC run ID and require absent campaign root and image tag. Create campaign/audit directories once. `Close-A7Campaign` writes one stage-specific diagnostic, revalidates the augmented baseline while excluding only the exact current campaign/image, writes result, captures the pre-manifest inventory, writes closure, and validates every closure hash. If no lease exists, it records `lease_acquired=false`; if a lease exists, it requires the frozen Task 8 runner to release it or records closure failure without inventing a release.

- [ ] **Step 4: Run transition tests to verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

- [ ] **Step 5: Write RED integration tests for the CPU micro-check Docker invocation**

Assert the exact Docker arguments include:

```powershell
'run', '--rm', '--network', 'none', '--workdir', '/workspace', '--entrypoint', 'python',
'-v', ("{0}:/workspace:ro" -f $RegisteredWorktree),
'-v', ("{0}:/audit:ro" -f $CampaignAuditRoot),
$ImageId,
'/workspace/scripts/run_wave0_a7_cpu_microcheck.py',
'--workspace-root', '/workspace',
'--source-inventory', '/audit/21-a7-source-inventory.json'
```

Assert absence of `--gpus`, model-cache mounts, `VAL_DATA_ROOT`, `PYTHONPATH=/workspace/src`, pytest, tests paths, network access, model commands, and stdin payloads. A fake micro-check returns one literal valid JSON line; blank, multiple lines, malformed JSON, CUDA initialized, wrong source, or wrong result inventory fails before lease.

- [ ] **Step 6: Run micro-check invocation tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k microcheck
```

Expected: failure because `Invoke-A7Launch` does not yet run or validate the payload.

- [ ] **Step 7: Implement image build, source inventory, CPU micro-check, and audit binding**

Build exactly once with the validated argv. Store zero-byte logs legally. Inspect exact identity. Publish `21-a7-source-inventory.json`. Run the checked-in micro-check once with the exact arguments above. Require one JSON line whose closed result matches the inventory and reports `cuda_initialized=false`; publish `22-a7-cpu-micro-check.json` through `FileMode.CreateNew`; recompute hashes before lease.

- [ ] **Step 8: Run micro-check invocation tests to verify GREEN**

Run the Step 6 command. Expected: all selected tests pass.

- [ ] **Step 9: Write RED tests for exactly-once Task 8 delegation**

The temporary Task 8 adapter records argv and invocation count. Require exact arguments:

```powershell
'-RunId', $RunId,
'-ImageTag', $ImageTag,
'-ImageDigest', $ImageId,
'-HostCampaignRoot', $CampaignRoot,
'-LeasePath', $LeasePath
```

Assert invocation count one on valid preconditions and zero for every earlier failure. Nonzero Task 8 exit closes without a second call. Assert no forbidden `gate wave0`, feasibility, RDD, Wave 1, retry, context change, prune, retag, or remote token appears in any launched argv.

- [ ] **Step 10: Run Task 8 delegation tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'task8 or exactly_once'
```

Expected: failure because delegation is absent.

- [ ] **Step 11: Implement exactly-once delegation and final terminal propagation**

After atomic lease creation, call the existing runner absolute path once using PowerShell's call operator and a typed argument array. Capture its exact exit and terminal. Do not wrap it in a loop or recover it. Require the existing runner's campaign result, closure, and lease-release records; independently recompute their hashes. Return one of the three Section 5.2.9 terminals exactly as stored.

- [ ] **Step 12: Run Task 8 and complete launcher tests to verify GREEN**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py
$Tokens = $null
$Errors = $null
[void][Management.Automation.Language.Parser]::ParseFile(
    (Resolve-Path 'scripts/start_wave0_a7.ps1'),
    [ref]$Tokens,
    [ref]$Errors
)
if ($Errors.Count -ne 0) { $Errors | ForEach-Object Message; exit 1 }
```

Expected: zero test failures and zero PowerShell parse errors.

- [ ] **Step 13: Commit the launcher slice**

```powershell
git add -- scripts/start_wave0_a7.ps1 tests/gates/test_wave0_a7_launcher.py
git -c user.name=kuotunyu `
    -c user.email=61350295+kuotunyu@users.noreply.github.com `
    commit -m "feat: harden A7 launch orchestration"
```

Verify the commit contains exactly those two files and the worktree is clean.

---

### Task 6: Run Mandatory Verification, Review the Four-File Candidate, and Freeze It

**Files:**
- Modify: none unless a Critical/Important finding requires a TDD fix within the same four-file allowlist
- Read: all four implementation files, approved Section 5.2.10, this plan, historical baseline, Git/Docker state

**Interfaces:**
- Consumes: the two append-only implementation commits from Tasks 2 and 5
- Produces: one reviewed candidate SHA with Critical=0, Important=0 and complete verification evidence

- [ ] **Step 1: Run focused launcher and diagnostic tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -q `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py `
  tests/gates/test_wave0_a7_launcher.py `
  tests/diagnostics/test_grid_sample_attribution.py `
  tests/diagnostics/test_tensor_evidence.py `
  tests/artifacts/test_receipts.py
```

Expected: zero failures; only existing capability skips are allowed.

- [ ] **Step 2: Run the complete CPU suite**

```powershell
uv run --no-sync pytest -q
```

Expected: zero failures. Record exact passed/skipped counts rather than predicting them.

- [ ] **Step 3: Run formatting, lint, lock, diff, and PowerShell gates**

```powershell
uv run --no-sync black --check `
  scripts/run_wave0_a7_cpu_microcheck.py `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py `
  tests/gates/test_wave0_a7_launcher.py
uvx --offline ruff check `
  scripts/run_wave0_a7_cpu_microcheck.py `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py `
  tests/gates/test_wave0_a7_launcher.py
uv lock --check
git diff --check
```

Parse both PowerShell scripts with `System.Management.Automation.Language.Parser`. Expected: every command exits zero.

- [ ] **Step 4: Verify exact implementation scope and history**

Require the cumulative diff from the owner-approved plan commit to contain exactly the four allowlisted files. Rehash the Task 1 pre-implementation baseline and require all 64,011 historical files, 14 historical images, 68 protected Git paths, original Task 1 baseline, seven A6 fixed hashes, and three A7 launch campaigns/images unchanged. Require no active project container/lease and unset `VAL_DATA_ROOT`.

- [ ] **Step 5: Perform the mandatory inline code review**

Review against Section 5.2.10 and this plan. Explicitly inspect:

```text
argument-vector element boundaries
PowerShell reserved-variable names
empty stdout/stderr behavior
CreateNew/no-clobber publication
pre-claim versus post-claim state
all failure closure paths
source/spec/plan/image/baseline/lease bindings
test/dev import prohibition
CUDA-uninitialized assertion
micro-check-before-lease ordering
Task 8 invocation count
history exclusion limited to current campaign/image
forbidden RDD/Wave 1/remote/retry operations
```

Critical and Important findings must be fixed with a new RED/GREEN cycle and all gates rerun. Minor findings may be recorded only when they do not affect a normative contract.

- [ ] **Step 6: Verify commit lineage, author, and clean state**

Require both implementation commits to be append-only children of the owner-approved plan commit, author/committer exact, only four new tracked files cumulatively, linked worktree clean, canonical main clean, and staging empty.

**Stop condition:** any failed test/gate, Critical/Important finding, fifth tracked file, history drift, dirty Git state, or external-state mutation.

---

### Task 7: Reverify the Committed Candidate and Stop for Owner Review

**Files:**
- Modify: none
- Execute: read-only Git, tests, format/lint/lock/diff, history, Docker health, and GPU visibility checks

**Interfaces:**
- Consumes: the clean reviewed candidate SHA from Task 6
- Produces: exact candidate report for separate owner authorization

- [ ] **Step 1: Repeat all Task 6 gates from the committed SHA**

Run focused tests, complete CPU suite, Black, Ruff, both PowerShell parses, `uv lock --check`, `git diff --check`, history/image hashes, Git identity, Docker Linux health, and read-only RTX 4090 visibility. Do not create a run ID, campaign, image, micro-check audit, or lease.

- [ ] **Step 2: Report exact candidate identity and stop**

Report:

```text
spec commit
plan commit
micro-check implementation commit
launcher implementation commit
final candidate SHA
exact four-file cumulative diff
focused/full test counts
format/lint/lock/parse results
Critical/Important review counts
historical preservation result
Git/Docker/GPU read-only state
Wave 1 forbidden state
```

Terminal:

```text
A7_LAUNCHER_IMPLEMENTATION_COMMITTED / OWNER_CANDIDATE_REVIEW_REQUIRED
```

Do not proceed to Task 8 without a new owner prompt naming the exact candidate SHA and authorizing one fresh campaign.

---

### Task 8: Execute One Fresh A7 Campaign Only After Separate Candidate Authorization

**Files:**
- Modify in Git: none
- Write outside Git: launcher-generated augmented baseline, one fresh campaign/image, one lease and its release evidence

**Interfaces:**
- Consumes: exact owner-approved source/spec/plan commits and authorization ID
- Produces: one closed A7 diagnostic campaign or one closed pre-GPU launcher failure; never a retry

- [ ] **Step 1: Revalidate owner authorization and derive exact immutable inputs**

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-launcher-hardening.md'
$ExpectedSourceCommit = (git rev-parse HEAD).Trim()
$ExpectedSpecCommit = '5d6ffe0567a4aeed0bcaceed7a33416b04f41925'
$ExpectedPlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$ExpectedBranch = 'codex/wave0-model-contract'
```

The separate owner prompt must state the same source/spec/plan commits and a unique non-empty authorization ID. A computed value that differs from the prompt stops rather than updating the prompt value.

- [ ] **Step 2: Invoke the launcher exactly once**

```powershell
& .\scripts\start_wave0_a7.ps1 `
  -ExpectedSourceCommit $ExpectedSourceCommit `
  -ExpectedSpecCommit $ExpectedSpecCommit `
  -ExpectedPlanCommit $ExpectedPlanCommit `
  -ExpectedBranch $ExpectedBranch `
  -OwnerAuthorizationId $OwnerAuthorizationId
$A7LauncherExit = $LASTEXITCODE
```

`$OwnerAuthorizationId` is copied exactly from the separate owner execution prompt. Do not invoke the launcher when that value is absent, inferred, reused, or changed.

- [ ] **Step 3: Independently verify the closed result and stop**

Recompute image labels, build/micro-check/lease/Task 8 audit hashes, component/aggregate identities when present, historical preservation, closure manifest, Git cleanliness, active containers, lease release, unset `VAL_DATA_ROOT`, and absence of RDD/Wave 1 artifacts. Preserve every outcome.

Allowed terminals remain exactly:

```text
WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
```

No outcome authorizes a second invocation, mitigation, threshold change, RDD access, or Wave 1.

---

## Plan Self-Review Record

- [x] Section 5.2.10 architecture maps to exactly one launcher, one production micro-check, and their two test files.
- [x] The four-file implementation allowlist is exact; a fifth tracked file or existing-file modification stops for renewed written review.
- [x] Every required label has one exact key, order, value source, typed argv rule, RED test, GREEN implementation step, and inspect gate.
- [x] Lazy manifest, seven source paths, four dtypes, 27-tensor snapshot/corruption, four receipt kinds, three classifier branches, forbidden imports, and CUDA-uninitialized evidence map to Task 2.
- [x] Git/worktree identity, complete augmented history, Docker Linux/RTX preflight, micro-check-before-lease ordering, and atomic lease contention map to Tasks 3–5.
- [x] Every post-claim failure maps to complete no-clobber closure; pre-claim failures create no campaign/image/lease.
- [x] Task 8 is delegated exactly once to the unchanged existing runner and is separately owner-gated after the committed candidate review.
- [x] Focused/full tests, Black, Ruff, PowerShell parse, lock, diff, historical hashes, Critical=0/Important=0 review, author/committer, and clean Git gates are explicit.
- [x] No implementation step builds a real image, starts GPU work, accesses RDD/Wave 1, or performs a remote operation before separate candidate authorization.
- [x] No unresolved marker, omitted error branch, ambiguous file path, inconsistent function name, or incomplete implementation instruction remains.

**Plan terminal:** `A7_LAUNCHER_PLAN_COMMITTED / OWNER_IMPLEMENTATION_PLAN_REVIEW_REQUIRED`
