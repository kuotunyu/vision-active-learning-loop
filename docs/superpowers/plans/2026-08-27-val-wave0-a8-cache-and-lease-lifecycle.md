# Wave 0 A8 Cache and Lease Lifecycle Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the checked-in A7 Task 7/8 boundary download and verify one fresh run-scoped Hugging Face cache before the GPU lease, consume that cache offline in Task 8, and preserve exact historical-set verification while accounting only for the current lease lifecycle.

**Architecture:** Task 7 adds one CPU-only, source/image-bound model-cache preflight between its existing CPU micro-check and GPU lease. Its PASS receipt and closed audit are hash-bound into the lease; Task 8 independently validates those bindings, mounts only the run-scoped cache read-only, and excludes exactly the current active/released/release-record paths from historical exact-set comparison. The fixed GPU-UUID active lease remains the atomic cross-run mutex, and every old cache, campaign, image, receipt, and release record remains immutable.

**Tech Stack:** Windows 11; PowerShell 7; Python 3.12.11; uv 0.8.15; pytest 9.0.2; Black 22.6.0; Ruff 0.16.4; Git; Docker Desktop Linux engine; NVIDIA CUDA 12.6 base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`; PyTorch 2.12.0+cu126; Transformers 5.15.0; Hugging Face Hub 1.28.0; RTX 4090 24 GB.

## Global Constraints

- The authoritative A8 specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `becb35b45d7a3f7f8a5a450705ad7ccdd2ad4aaa`, especially Section 5.2.12.
- At that commit the specification is exactly 167,798 bytes, SHA-256 `010ddf28a382492a675284a1f3b0d1e2cf5c049b0486687ef3ec6741a8f70c5b`, and Git object `66d4d5ac63889b7724edb250a01d7db796304514`.
- This plan is `docs/superpowers/plans/2026-08-27-val-wave0-a8-cache-and-lease-lifecycle.md`. Its commit must be the direct child of the specification commit and must change only this new plan document.
- Implementation entry branch is exactly `codex/wave0-model-contract`. Both the registered linked worktree and canonical `main` worktree must be clean, staging must be empty, and implementation starts only from the committed plan.
- The implementation tracked-file allowlist is closed to exactly:
  1. `scripts/start_wave0_a7.ps1`
  2. `scripts/run_wave0_a7.ps1`
  3. `tests/gates/test_wave0_a7_launcher.py`
- A fourth tracked implementation file is a hard stop. Do not modify the specification, this plan, any Python production module, schema, Dockerfile, configuration, dependency declaration, `uv.lock`, model pin, test fixture used by formal research, or historical evidence.
- The old shared cache at `D:\vision-active-learning-loop-artifacts\wave0\model_cache` remains immutable and invalid under the exact lock-metadata contract. Do not backfill, copy from, mount, delete, rename, or reinterpret it.
- The fresh preflight root is exactly `<campaign>\cache-preflight`; its model cache is `<campaign>\cache-preflight\wave0\model_cache`, and its receipt is `<campaign>\cache-preflight\wave0\receipts\model-assets.json`. Every destination must be absent before trusted Task 7 orchestration creates its parent.
- The only post-build network-enabled container is the cache preflight. It uses `--network bridge`, no `--gpus`, no `VAL_DATA_ROOT`, and the exact command suffix `val assets verify --config /workspace/configs/models/pinned-models.yaml --cache-root /artifacts/wave0/model_cache --output /artifacts/wave0/receipts/model-assets.json --run-id $RunId --download`.
- That command reuses the sole tracked frozen model configuration, `configs/models/pinned-models.yaml`; it does not create or select a second config contract.
- The preflight must return exit code 0, stdout exactly `PASS` plus the platform newline captured by `Invoke-A7Native`, empty stderr, and a schema-valid PASS receipt whose exact content is SHA-256-bound into its audit and the lease. No other pre-lease step initializes CUDA or claims model execution.
- Task 8 uses `--network none`, `--gpus all`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and mounts the exact run-scoped cache at `/artifacts/wave0/model_cache:ro`. Its ordinary model-assets stage reruns without `--download` and publishes the current campaign receipt.
- Each snapshot remains pinned exactly: RT-DETR-R18 `PekingU/rtdetr_r18vd@cc5b50f32f0100caaa3bd275343e2fb17762c73d` and DINOv2-small `facebook/dinov2-small@ed25f3a31f01632728cabb09d1542f84ab7b0056`. Each has exactly four payloads and four matching zero-byte `.lock` files already enforced by the production verifier.
- Lease paths are exact and distinct: active `leases\<GPU-UUID>.json`, released `leases\<RUN_ID>.released`, and release record `leases\<RUN_ID>.release.json`. The active path remains the single atomic `FileMode.CreateNew` mutex for the GPU UUID.
- Task 8 historical verification excludes only its current campaign subtree and the exact three lease lifecycle paths obtained from the validated lease. At the pre-release check the active path exists and the two release destinations do not. Every other baseline/current artifact and historical image must match exactly.
- After Task 8, Task 7 independently requires the active lease to be absent; both release files to be regular non-link files; the released-lease SHA-256 to equal `original_lease_sha256`; and release-record `run_id`, `source_commit`, and `image_digest` to match the current execution.
- Preserve every earlier A2-A7 campaign, image, receipt, log, cache, checkpoint, lease, release record, and audit byte-for-byte. A new candidate may create no runtime object until all implementation gates pass.
- No implementation test may use the real artifact root, make a network request, build an image, acquire the real lease, use the real GPU, load a model, touch RDD, or invoke the real Task 8 campaign. Tests use temporary directories and controlled executable adapters.
- `VAL_DATA_ROOT` remains unset. RDD, A6 retry, the Wave 0 aggregate gate, Wave 1, remote operations, push, merge, tag, Release, and publication remain forbidden.
- Whole-tree formatting debt is out of scope. Format and lint only `tests/gates/test_wave0_a7_launcher.py`; both PowerShell scripts must parse. Author and committer are `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`. Commits are append-only without amend, reset, rebase, squash, force, or history rewriting.
- The implementation ends in one candidate commit after all gates and Critical=0/Important=0 review. The standing unattended delegation then permits exactly one fresh A8-bound A7 attempt. Any normative failure preserves its new objects and stops without retry or candidate modification.

---

## File Map

| File | Responsibility in A8 |
|---|---|
| `scripts/start_wave0_a7.ps1` | Create and audit the fresh model cache before lease acquisition, bind it into the lease, enforce state/order/network/no-GPU rules, and validate released-lease evidence after Task 8 |
| `scripts/run_wave0_a7.ps1` | Validate cache-preflight audit/receipt/lease identity, mount the run-scoped cache offline, and perform exact historical-set comparison with only current lease lifecycle exclusions |
| `tests/gates/test_wave0_a7_launcher.py` | Real PowerShell RED/GREEN coverage for cache preflight, lease bindings, offline mount, exact exclusions, release integrity, closure, and exactly-once behavior |

No source verifier or receipt schema changes are needed: `assets.py` and `schemas/model-asset-receipt.schema.json` already enforce the exact payload, `.metadata`, and zero-byte `.lock` inventory.

---

### Task 1: Revalidate the Committed Plan Entry and Freeze Pre-Implementation Evidence

**Files:**
- Read: Git metadata, A8 specification/plan lineage, historical baseline, artifact/image inventory, and the latest closed A7 evidence
- Modify: none

**Interfaces:**
- Consumes: specification commit `becb35b45d7a3f7f8a5a450705ad7ccdd2ad4aaa` and this plan's direct-child commit
- Produces: exact entry SHA and a no-clobber temporary pre-change preservation record for the final review

- [ ] **Step 1: Verify branch, lineage, scopes, and clean worktrees**

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a8-cache-and-lease-lifecycle.md'
$SpecPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
$SpecCommit = 'becb35b45d7a3f7f8a5a450705ad7ccdd2ad4aaa'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$PlanFiles = @(git diff-tree --no-commit-id --name-only -r $PlanCommit)
git worktree list --porcelain
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'wrong branch' }
if ((git rev-parse HEAD).Trim() -cne $PlanCommit) { throw 'HEAD is not the plan commit' }
if ((git rev-parse "$PlanCommit^").Trim() -cne $SpecCommit) { throw 'plan is not direct spec child' }
if ($PlanFiles.Count -ne 1 -or $PlanFiles[0] -cne $PlanPath) { throw 'plan commit scope mismatch' }
if ((git status --porcelain=v1).Count -ne 0) { throw 'linked worktree is not clean' }
if ((git -C '<repo>' status --porcelain=v1).Count -ne 0) { throw 'canonical main is not clean' }
if ((Get-Item $SpecPath).Length -ne 167798) { throw 'spec size mismatch' }
if ((Get-FileHash $SpecPath -Algorithm SHA256).Hash.ToLowerInvariant() -cne '010ddf28a382492a675284a1f3b0d1e2cf5c049b0486687ef3ec6741a8f70c5b') { throw 'spec hash mismatch' }
if ((git rev-parse "$SpecCommit`:$SpecPath").Trim() -cne '66d4d5ac63889b7724edb250a01d7db796304514') { throw 'spec object mismatch' }
```

Expected: every assertion succeeds and staging is empty.

- [ ] **Step 2: Record a complete pre-change historical identity outside Git**

Use a never-existing file under `[IO.Path]::GetTempPath()` named `val-a8-prechange-$PlanCommit.json`. Enumerate all regular non-link files beneath `D:\vision-active-learning-loop-artifacts\wave0`, recording sorted relative path, byte size, and SHA-256; record every `vision-active-learning-loop:wave0-*` tag and exact inspected image ID; record all 68 root protected-Git identities and the A8-approved current spec transition. Publish with `FileMode.CreateNew`, then record its SHA-256 in the execution notes.

Expected: all historical paths hash successfully, no link/junction is traversed, the latest closed campaign `wave0-a7-20260826T224622928Z` and its two release files are present, and no active `GPU-*.json` lease exists.

---

### Task 2: Add RED Tests for the Fresh Model-Cache Preflight

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Production files: unchanged in this task

**Interfaces:**
- Consumes: existing AST helpers `_invoke_functions()` and controlled native-process adapters
- Produces: tests for `Invoke-A7ModelCachePreflight(...)` and its closed audit contract

- [ ] **Step 1: Add the success fixture and exact argv test**

Add a temporary fake Docker executable that writes a valid model-assets PASS receipt containing both pinned model identities and their exact payload/metadata maps, prints `PASS`, and records received argv. The test invokes the new production function with a temporary campaign and asserts this exact semantic vector:

```python
assert argv[:8] == ["run", "--rm", "--network", "bridge", "--workdir", "/workspace", "--entrypoint", "val"]
assert "--gpus" not in argv
assert "VAL_DATA_ROOT" not in "\n".join(argv)
assert "HF_HUB_OFFLINE" not in "\n".join(argv)
assert "TRANSFORMERS_OFFLINE" not in "\n".join(argv)
assert argv[-11:] == [
    "assets", "verify", "--config", "/workspace/configs/models/pinned-models.yaml",
    "--cache-root", "/artifacts/wave0/model_cache",
    "--output", "/artifacts/wave0/receipts/model-assets.json",
    "--run-id", _RUN_ID, "--download",
]
```

Assert the cache root, receipt, stdout, stderr, and `23-a7-model-cache-preflight.json` are regular files/directories under the campaign; stdout is exactly `PASS` with one newline, stderr is zero bytes, and the audit contains only the specified closed properties.

- [ ] **Step 2: Add fail-closed cache-preflight cases**

Parameterize mutations for nonzero exit, unexpected stdout, nonempty stderr, FAIL/malformed/missing receipt, wrong run ID, wrong receipt type/version, changed model revision, missing/extra/renamed/nonzero/unpaired lock identity, linked cache ancestor, pre-existing cache root, pre-existing receipt, pre-existing log, `--gpus`, missing `--network bridge`, a second network-enabled command, and any `VAL_DATA_ROOT` argument.

```python
@pytest.mark.parametrize(
    "mutation",
    [
        "exit_2", "stdout_extra", "stderr_nonempty", "receipt_fail",
        "receipt_malformed", "receipt_missing", "wrong_run", "wrong_revision",
        "missing_lock", "extra_lock", "nonzero_lock", "linked_cache",
        "preexisting_root", "preexisting_receipt", "gpu_flag", "wrong_network",
    ],
)
def test_model_cache_preflight_fails_closed(tmp_path: Path, mutation: str) -> None:
    completed = _invoke_model_cache_preflight_fixture(tmp_path, mutation=mutation)
    assert completed.returncode != 0
```

- [ ] **Step 3: Run the RED slice**

```powershell
uv run pytest tests/gates/test_wave0_a7_launcher.py -k 'model_cache_preflight' -vv
```

Expected: failures identify missing `Invoke-A7ModelCachePreflight`; no production file has changed.

---

### Task 3: Implement Task 7 Cache Preflight and Lease Binding

**Files:**
- Modify: `scripts/start_wave0_a7.ps1`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: `Write-A7NewText`, `Invoke-A7Native`, validated Task 7 identities, fresh image ID, and existing production model-assets verifier
- Produces: `Invoke-A7ModelCachePreflight(...)` returning immutable cache/audit/receipt paths and hashes; extended `New-A7Lease(...)` fields

- [ ] **Step 1: Implement the closed preflight function**

Add one function whose result object has exactly these properties:

```powershell
[pscustomobject][ordered]@{
    cache_root = $CacheRoot
    audit_path = $AuditPath
    audit_sha256 = (& $GetSha256 $AuditPath)
    receipt_path = $ReceiptPath
    receipt_sha256 = (& $GetSha256 $ReceiptPath)
}
```

The function must create the absent `cache-preflight`, `wave0`, `model_cache`, and `receipts` directories with `New-Item -ErrorAction Stop`; reject reparse points on every ancestor within the campaign; call only the fresh image; capture stdout/stderr no-clobber; require exit 0, `PASS` plus one line ending, empty stderr, and a parsed model-assets PASS receipt for `$RunId`; then publish `audit\23-a7-model-cache-preflight.json` with this closed property set:

```text
schema_version, owner_authorization_id, run_id, source_commit, spec_commit,
plan_commit, branch, image_tag, image_id, base_image_digest,
augmented_baseline_path, augmented_baseline_sha256, docker_argv, network,
gpu_enabled, cache_root, receipt_path, receipt_sha256, receipt_models,
stdout_path, stdout_sha256, stderr_path, stderr_sha256, exit_code,
started_at, completed_at
```

`network` is exactly `bridge`; `gpu_enabled` is exactly `false`; `receipt_models` is the complete receipt `normative.models` object, not a summary.

- [ ] **Step 2: Insert the state transition before lease acquisition**

Immediately after `22-a7-cpu-micro-check.json` is finalized, set `$Stage = 'model_cache_preflight'`, invoke the function once, recompute the audit and receipt hashes while revalidating the cache through that receipt, and only then set `$Stage = 'gpu_lease'`. No code path may acquire the lease first or invoke the preflight twice.

- [ ] **Step 3: Extend the lease as a closed identity**

Add exact `New-A7Lease` parameters and JSON fields:

```powershell
[Parameter(Mandatory = $true)][string]$ModelCacheRoot,
[Parameter(Mandatory = $true)][string]$ModelCachePreflightAuditPath,
[Parameter(Mandatory = $true)][string]$ModelCachePreflightAuditSha256,
[Parameter(Mandatory = $true)][string]$ModelCacheReceiptPath,
[Parameter(Mandatory = $true)][string]$ModelCacheReceiptSha256
```

Validate all paths as regular non-link descendants of the claimed campaign, require the audit at `audit\23-a7-model-cache-preflight.json`, require cache/receipt at their exact contract paths, recompute both file hashes before atomic lease publication, and bind the five fields in the lease. Extend the lease parse-back property-set and identity checks without weakening any existing field.

- [ ] **Step 4: Run the cache-preflight GREEN slice**

```powershell
uv run pytest tests/gates/test_wave0_a7_launcher.py -k 'model_cache_preflight or lease' -vv
```

Expected: all selected tests pass; tests prove preflight precedes lease and no GPU/network leakage occurs.

---

### Task 4: Add RED Tests for Task 8 Cache Consumption and Exact Lease Exclusions

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Production files: unchanged in this task

**Interfaces:**
- Consumes: `_invoke_runner_functions()`, a closed fake lease/audit/receipt fixture, and a temporary artifact baseline
- Produces: failing tests for Task 8's new cache and historical-set contracts

- [ ] **Step 1: Add runner binding and mount tests**

Build a fake Task 7 audit/lease whose five cache fields hash correctly. Assert `Test-Task7AuditBinding` rejects each missing/extra field, altered audit hash, altered receipt hash, wrong path, linked path, wrong run/source/image, non-PASS receipt, changed pinned revision, and receipt inventory drift. Add a structural runner test requiring the Task 8 Docker argv to contain exactly:

```python
assert "--network|none" in joined
assert "HF_HUB_OFFLINE=1" in joined
assert "TRANSFORMERS_OFFLINE=1" in joined
assert f"{run_scoped_cache}:/artifacts/wave0/model_cache:ro" in joined
assert r"D:\vision-active-learning-loop-artifacts\wave0\model_cache" not in joined
assert "--download" not in model_assets_stage
```

- [ ] **Step 2: Reproduce the active-lease exact-set drift**

Create a baseline for two historical files, a current campaign subtree, and exact active/released/release-record paths. With only the active path present, call the current `Test-HistoricalBaseline` and assert RED failure `historical artifact set drift`. Then define the target behavior:

```python
assert result["status"] == "PRESERVED"
assert result["approved_lease_exclusions"] == [active_rel, released_rel, release_record_rel]
assert result["observed_lease_exclusions"] == [active_rel]
assert result["exact_set_match"] is True
```

- [ ] **Step 3: Add exclusion/release attack cases**

Reject wildcard or prefix exclusions, a fourth exclusion, a path outside the fixed lease root, duplicate paths, wrong literal names, symlink/junction paths, missing active lease, pre-existing released/release-record destinations, unapproved extra artifact, missing baseline artifact, and historical size/hash drift. Add launcher post-Task-8 tests that reject linked release files, release hash mismatch, wrong run/source/image, active lease still present, and missing release evidence.

- [ ] **Step 4: Run the RED slice**

```powershell
uv run pytest tests/gates/test_wave0_a7_launcher.py -k 'run_scoped_cache or lease_exclusion or release_integrity' -vv
```

Expected: new behavior tests fail against the unchanged Task 8 runner while all pre-A8 tests remain green.

---

### Task 5: Implement Task 8 Binding, Offline Cache Mount, and Historical Preservation

**Files:**
- Modify: `scripts/run_wave0_a7.ps1`
- Modify: `scripts/start_wave0_a7.ps1`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: the five new lease fields, `Get-A7LeaseReleasePaths`, current campaign root, and immutable augmented baseline
- Produces: verified run-scoped `$ModelCacheRoot`, exact lease exclusions, expanded preservation evidence, and independently validated release evidence

- [ ] **Step 1: Extend `Test-Task7AuditBinding`**

Require the lease's five cache fields and parse `23-a7-model-cache-preflight.json`. Enforce its closed property set, exact identities, timestamps, `network == 'bridge'`, `gpu_enabled == $false`, exact Docker argv, zero exit, stdout/stderr hashes, receipt hash, PASS status, exact run ID, and exact RT-DETR/DINOv2 revisions. Return the verified cache root; callers must not derive it from the historical artifact root.

- [ ] **Step 2: Replace the historical cache mount**

Remove `$HistoricalModelCache = Join-Path $HistoricalWaveRoot 'model_cache'`. Set `$ModelCacheRoot` only from the validated lease/audit result and change `Invoke-A7Stage` to mount:

```powershell
'-v', "${ModelCacheRoot}:/artifacts/wave0/model_cache:ro"
```

Retain `--gpus all`, `--network none`, both offline variables, and the unchanged Task 8 `assets verify` command without `--download`.

- [ ] **Step 3: Add exact current-lease exclusions to `Test-HistoricalBaseline`**

Extend the function signature with three mandatory absolute paths. Canonicalize them, require distinct direct children of the fixed `leases` root and literal current GPU/run names, require active present and release destinations absent, and build one ordinal-ignore-case set. During traversal, skip only files whose full path equals a member of that set; do not skip directories or prefixes. Return:

```powershell
approved_lease_exclusions = @($ApprovedRelativePaths | Sort-Object -CaseSensitive)
observed_lease_exclusions = @($ObservedRelativePaths | Sort-Object -CaseSensitive)
baseline_artifact_count = $ExpectedArtifactPaths.Count
observed_historical_count = $CurrentHistoricalPaths.Count
exact_set_match = $true
```

Require `observed_lease_exclusions` to contain exactly the active relative path at the pre-release check. Existing artifact and image identity loops remain unchanged.

- [ ] **Step 4: Harden Task 7 post-release validation**

After Task 8 returns, assert active absence and regular non-link released/release-record files. Parse the release record as a closed object with exactly `schema_version`, `run_id`, `source_commit`, `image_digest`, `released_at`, and `original_lease_sha256`; require current identities, valid timestamp/hash syntax, and exact hash equality to the released lease. Feed any failure through the existing no-clobber `52/53` post-Task-8 closure path without reinvoking Task 8.

- [ ] **Step 5: Run all launcher tests**

```powershell
uv run pytest tests/gates/test_wave0_a7_launcher.py -vv
```

Expected: zero failures with only existing capability skips; no real Docker, GPU, network, or artifact root is used.

---

### Task 6: Complete Orchestration, Failure-Closure, and Regression Coverage

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Modify only if a test exposes a contract defect: the two approved PowerShell scripts

**Interfaces:**
- Consumes: completed Task 7 preflight/lease and Task 8 preservation interfaces
- Produces: end-to-end controlled proof of the A8 state machine and all stop boundaries

- [ ] **Step 1: Add exact state/order and exactly-once tests**

The controlled launcher adapter records build, CPU micro-check, cache preflight, lease publication, and Task 8 invocation. Assert this exact order and count:

```python
assert events == [
    "image_build",
    "cpu_microcheck",
    "model_cache_preflight",
    "gpu_lease",
    "task8",
]
assert events.count("model_cache_preflight") == 1
assert events.count("gpu_lease") == 1
assert events.count("task8") == 1
```

For failures at every cache-preflight boundary, assert no lease and no Task 8 invocation. For failures after Task 8, assert Task 8 count remains one and `52/53` close without overwriting Task 8 evidence.

- [ ] **Step 2: Add no-clobber and preservation regression tests**

Run each publication fixture twice against the same destination and require the second call to fail. Assert old release files remain part of the baseline, only current lifecycle paths are excluded, the historical shared cache is never changed, and no wildcard `.lock` or lease path appears in either script.

- [ ] **Step 3: Run focused and neighboring regression suites**

```powershell
uv run pytest tests/gates/test_wave0_a7_launcher.py tests/models/test_assets.py tests/diagnostics tests/artifacts/test_receipts.py -q
```

Expected: zero failures with only documented capability skips.

---

### Task 7: Full Candidate Verification, Independent Review, and Append-Only Commit

**Files:**
- Verify/stage only: `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, `tests/gates/test_wave0_a7_launcher.py`
- Historical evidence: read-only

**Interfaces:**
- Consumes: the green three-file candidate and Task 1 pre-change preservation record
- Produces: one clean reviewed candidate commit and a complete local verification record

- [ ] **Step 1: Run all deterministic gates**

```powershell
uv run pytest tests/gates/test_wave0_a7_launcher.py -q
uv run pytest -q
uv run black --check tests/gates/test_wave0_a7_launcher.py
uv run ruff check tests/gates/test_wave0_a7_launcher.py
uv lock --check
git diff --check
$Tokens=$null; $Errors=$null
[void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path 'scripts/start_wave0_a7.ps1'),[ref]$Tokens,[ref]$Errors)
if ($Errors.Count -ne 0) { throw ($Errors.Message -join '; ') }
$Tokens=$null; $Errors=$null
[void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path 'scripts/run_wave0_a7.ps1'),[ref]$Tokens,[ref]$Errors)
if ($Errors.Count -ne 0) { throw ($Errors.Message -join '; ') }
```

Expected: zero test, formatter, lint, lock, diff, or parser failures.

- [ ] **Step 2: Rehash protected state and perform independent review**

Recompute every Task 1 artifact/image/Git identity and compare exact sets. Verify the eight fixed hashes cited in A8 Section 5.2.12, verify the old shared cache still has zero of the eight required locks, verify `VAL_DATA_ROOT` is unset, and confirm no project container or active GPU lease exists. Review `git diff --stat`, `git diff --check`, and the complete three-file diff against Section 5.2.12. Record findings by severity; Critical and Important must both equal zero. Fix only within the three-file allowlist and repeat all gates if either count is nonzero.

- [ ] **Step 3: Create the single implementation commit**

```powershell
$Allowed = @(
  'scripts/start_wave0_a7.ps1',
  'scripts/run_wave0_a7.ps1',
  'tests/gates/test_wave0_a7_launcher.py'
)
$Changed = @(git status --porcelain=v1 | ForEach-Object { $_.Substring(3).Replace('\','/') } | Sort-Object -Unique)
if (($Changed -join '|') -cne (($Allowed | Sort-Object) -join '|')) { throw 'candidate scope mismatch' }
git add -- $Allowed
git -c user.name=kuotunyu -c user.email=61350295+kuotunyu@users.noreply.github.com commit -m 'fix: bind A7 cache and lease lifecycle'
```

Expected: author and committer are exact, the commit is an append-only child of the plan commit, only the three allowed files changed, and the worktree is clean.

- [ ] **Step 4: Repeat focused/full gates after commit**

Run Step 1 again from the committed SHA and repeat the historical identity comparison. A post-commit discrepancy is a hard stop before Docker build or run ID creation.

---

### Task 8: Execute the Single Authorized Fresh A8-Bound A7 Attempt

**Files:**
- Repository: read-only after the candidate commit
- Create outside Git: one fresh OCI image, campaign root, cache-preflight root, and GPU lease/release evidence

**Interfaces:**
- Consumes: clean reviewed candidate SHA, committed A8 spec/plan identities, Docker Linux/RTX 4090 health, no active lease, and standing unattended authorization
- Produces: one immutable A7 diagnostic campaign ending before Wave 1

- [ ] **Step 1: Run the read-only preflight without repeating Tasks 1-5**

Require clean linked/canonical worktrees, exact candidate HEAD, `desktop-linux`, Linux Docker Server, successful `docker info`, one visible RTX 4090, unset `VAL_DATA_ROOT`, no project container, no active `GPU-*.json` lease, unchanged historical hashes/images, and absent fresh destinations. A failed check creates no runtime object.

- [ ] **Step 2: Let the checked-in launcher generate one run identity and invoke it once**

```powershell
$SourceCommit = (git rev-parse HEAD).Trim()
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a8-cache-and-lease-lifecycle.md'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$OwnerAuthorizationId = 'OWNER-STANDING-A8-20260827-UNATTENDED-01'
pwsh -NoProfile -NonInteractive -File scripts/start_wave0_a7.ps1 `
  -OwnerAuthorizationId $OwnerAuthorizationId `
  -ExpectedSourceCommit $SourceCommit `
  -ExpectedSpecCommit 'becb35b45d7a3f7f8a5a450705ad7ccdd2ad4aaa' `
  -ExpectedPlanCommit $PlanCommit `
  -ExpectedBranch 'codex/wave0-model-contract'
$Task7Exit = $LASTEXITCODE
```

`Invoke-A7Production` generates the sole run ID immediately before `Invoke-A7Launch`; no session-side run ID is accepted. The authorization ID is the audit label for the owner's standing unattended A8 delegation; it is not a claim that the owner supplied a separately numbered token. Do not change it after any runtime object is created.

- [ ] **Step 3: Stop, preserve, and report**

Regardless of attributed, not-attributed, or inconclusive terminal, do not retry. Hash the image inspect, cache preflight audit/receipt, environment/model-assets/model-contract receipts, every A7 component receipt/bundle, aggregate receipt, preservation/campaign/closure records, released lease, and release record that exists. Confirm Git remains clean, active lease absent, history unchanged, RDD untouched, and Wave 1 not started.

The only valid stopping terminals remain:

```text
WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
```

No A8/A7 outcome is a Wave 0 pass or authority to begin Wave 1.

---

## Plan Self-Review

- [x] Every A8 Section 5.2.12 requirement maps to Tasks 2-8: fresh official cache, pre-lease/no-GPU/network boundary, receipt/audit/lease identity, Task 8 offline mount, exact current-lease exclusions, release validation, failure closure, and one-shot execution.
- [x] The three-file implementation allowlist is identical in the spec, plan, staging check, and commit command.
- [x] Function/property names are consistent: `Invoke-A7ModelCachePreflight`, `model_cache_root`, `model_cache_preflight_audit_path`, `model_cache_preflight_audit_sha256`, `model_cache_receipt_path`, and `model_cache_receipt_sha256`.
- [x] The plan contains no deferred implementation marker, wildcard exception, threshold change, source/schema/config edit, historical mutation, A6 retry, RDD access, Wave 0 pass claim, or Wave 1 action.
- [x] Tests explicitly separate mocked CPU orchestration evidence from real Docker/GPU diagnostic evidence.
