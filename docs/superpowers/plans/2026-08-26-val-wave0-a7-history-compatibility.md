# Wave 0 A7 Protected-Git Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Execute inline in the registered worktree; do not dispatch subagents unless the owner explicitly requests them.

**Goal:** Make the reviewed A7 launcher candidate accept exactly the owner-approved authoritative-spec lineage transition while preserving the immutable root history, closing container/audit evidence gaps, and publishing separate no-clobber evidence for launcher validation failures that occur after Task 8.

**Architecture:** The Task 7 launcher publishes an augmented baseline with three closed protected-Git structures: the unchanged root array, the complete reviewed-current array, and one exact spec transition bound to the direct spec/plan commit pair. The Task 8 runner independently validates the same lineage before its existing artifact/image rehash. The launcher also classifies project containers from immutable inspect records, turns the build and CPU micro-check receipts into full identity-binding audits, and routes every post-Task-8 validation failure to new `52/53` records without invoking the existing pre-Task-8 closure path.

**Tech Stack:** Windows 11; PowerShell 7; Python 3.12.11; uv 0.8.15; pytest 9.0.2; Black 22.6.0; Ruff 0.16.4; Git; Docker Desktop Linux engine; NVIDIA CUDA 12.6 base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`; RTX 4090 24 GB visibility is read-only during candidate verification.

## Global Constraints

- The authoritative specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `adfb54bb9c53238eddafa714e202925d5b9aae7e`, especially Section 5.2.11.
- The checked-out specification identity at that commit is exactly 156,800 bytes, SHA-256 `3d0f3b3701cdd310298c31e8a2351b2504d10efb0b8bf489c487fd43484ade7c`, and Git object `4c5ecb32b12a7bc89c4c85a05e61a6f858942607`.
- This plan is `docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md`. Its commit must be the direct child of `adfb54bb9c53238eddafa714e202925d5b9aae7e` and must change only this new document.
- Implementation entry branch is exactly `codex/wave0-model-contract`. Entry HEAD must be the separately owner-approved commit containing this plan. Both the linked worktree and canonical `main` worktree must be clean and staging must be empty.
- The implementation tracked-file allowlist is closed to exactly:
  1. `scripts/start_wave0_a7.ps1`
  2. `scripts/run_wave0_a7.ps1`
  3. `tests/gates/test_wave0_a7_launcher.py`
- A fourth tracked file is a hard stop. Do not modify the approved specification, this plan, the production micro-check, its tests, any model/diagnostic module, receipt schema or validator, Dockerfile, configuration, dependency declaration, `uv.lock`, fixture used by formal research, or historical evidence.
- Existing implementation commits `246053d1c1328bbdf169dc767d7ca87756621cde` and `e15b9ad6646b55ff57ad3801da42295a1366b93c` remain append-only ancestors. Do not amend, reset, rebase, squash, force, or rewrite them.
- The original Task 1 baseline SHA-256 remains `4715e35d4ed693d74577cc40781f51a65bf7f34089b97d6610fb43f4d675cadd`. Its complete sorted 68-record `protected_git` array remains unchanged in every augmented baseline.
- Current immutable history remains 64,011 artifact files, 14 registered `vision-active-learning-loop:wave0-*` image identities, 68 root protected-Git paths, all failed A7 campaigns/images, and seven fixed A6 evidence hashes. Every record is reverified; no prior object is moved, deleted, overwritten, or reinterpreted.
- The only approved protected-Git transition path is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`, with reason exactly `owner-approved-design-amendment`. There is no wildcard, second transition, renamed path, or promoted root record.
- No implementation test may use the real artifact root, build an image, acquire the real GPU lease, invoke the real Task 8 campaign, load a model, access RDD or `VAL_DATA_ROOT`, make a network request, or start Wave 1. Temporary Git repositories and controlled executable adapters are allowed inside pytest temporary directories.
- Runtime publication continues to use `FileMode.CreateNew`, safe regular non-link paths, parse-back verification, exact inventory checks, and SHA-256 bindings. No caller creates a compatibility shortcut around no-clobber behavior.
- A build, CPU micro-check, and Task 8 runner remain one-shot for one run ID. No implementation or candidate-review step creates a real run ID, image, campaign root, or lease.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`. Remote, push, merge, tag, Release, publication, RDD, and Wave 1 remain forbidden.

---

## File Map

| File | Responsibility |
|---|---|
| `scripts/start_wave0_a7.ps1` | Build the exact augmented protected-Git transition, classify inspected project containers, publish full build/micro-check binding audits, and route post-Task-8 validation failures to no-clobber `52/53` evidence |
| `scripts/run_wave0_a7.ps1` | Independently validate the immutable root array, exact spec/plan lineage, complete current array, and all 68 checked-out identities before the existing Task 8 history and GPU sequence |
| `tests/gates/test_wave0_a7_launcher.py` | Own all new RED/GREEN behavior tests, including temporary 68-file Git lineage fixtures, Task 8 function probes, digest-launched containers, full audit bindings, and post-Task-8 failure closures |

The existing `Test-HistoricalBaseline` artifact/image helper remains testable in isolation. A new `Test-A7ProtectedGitLineage` function owns the strict Git transition and is called unconditionally by the production Task 8 path immediately before `Test-HistoricalBaseline`. This preserves existing CPU test ownership without providing a production bypass.

---

### Task 1: Revalidate the Plan Entry and Immutable Pre-Implementation State

**Files:**
- Read: Git metadata, approved spec/plan lineage, original and augmented historical baselines, registered image identities, fixed A6 evidence
- Modify: none

**Interfaces:**
- Consumes: the owner-approved commit containing this plan
- Produces: one recorded entry SHA and a read-only preservation report used by Tasks 2–5

- [ ] **Step 1: Resolve the registered worktree and exact plan lineage**

Run from the registered worktree:

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md'
$SpecPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
$SpecCommit = 'adfb54bb9c53238eddafa714e202925d5b9aae7e'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$PlanFiles = @(git diff-tree --no-commit-id --name-only -r $PlanCommit)
git worktree list --porcelain
git branch --show-current
git rev-parse HEAD
git rev-parse "$PlanCommit^"
git status --porcelain=v1
git -C '<repo>' status --porcelain=v1
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'wrong branch' }
if ((git rev-parse HEAD).Trim() -cne $PlanCommit) { throw 'HEAD is not the reviewed plan commit' }
if ((git rev-parse "$PlanCommit^").Trim() -cne $SpecCommit) { throw 'plan is not the direct spec child' }
if ($PlanFiles.Count -ne 1 -or $PlanFiles[0] -cne $PlanPath) { throw 'plan commit scope is not closed' }
```

Expected: the exact registered linked worktree is selected; branch and parent match; both status commands and the staging area are empty; the plan commit changes only `$PlanPath`.

- [ ] **Step 2: Recompute the approved specification identity**

```powershell
$SpecItem = Get-Item -LiteralPath $SpecPath
$SpecSha256 = (Get-FileHash -LiteralPath $SpecPath -Algorithm SHA256).Hash.ToLowerInvariant()
$SpecObject = (git rev-parse "$SpecCommit`:$SpecPath").Trim()
if ($SpecItem.Length -ne 156800) { throw 'spec size mismatch' }
if ($SpecSha256 -cne '3d0f3b3701cdd310298c31e8a2351b2504d10efb0b8bf489c487fd43484ade7c') { throw 'spec hash mismatch' }
if ($SpecObject -cne '4c5ecb32b12a7bc89c4c85a05e61a6f858942607') { throw 'spec Git object mismatch' }
```

Expected: all three identities match exactly.

- [ ] **Step 3: Repeat the read-only history and environment review**

Rehash all 64,011 artifact records; inspect all 14 registered image tag-to-ID records; verify the unchanged 68-record root protected-Git array and seven fixed A6 hashes; require no active project lease/container and an unset `VAL_DATA_ROOT`. Docker commands in this step are limited to `context show`, `version`, `info`, `image ls`, `image inspect`, `ps --no-trunc`, and the approved no-network `nvidia-smi` visibility collector. Any mismatch stops before a tracked edit.

**Stop condition:** wrong Git identity, dirty state, missing baseline, history drift, image drift, fixed-evidence drift, active project state, or set `VAL_DATA_ROOT`.

---

### Task 2: Add the Exact Protected-Git Lineage Contract with TDD

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Modify: `scripts/start_wave0_a7.ps1`
- Modify: `scripts/run_wave0_a7.ps1`

**Interfaces:**
- `New-A7AugmentedBaseline` additionally consumes `GitExecutable`, `ExpectedSpecCommit`, and `ExpectedPlanCommit`
- Produces root `protected_git`, reviewed `current_protected_git`, and one `approved_protected_git_transitions` object
- Adds `Test-A7ProtectedGitLineage(RootBaselinePath, RootBaselineSha256, AugmentedBaselinePath, AugmentedBaselineSha256, ProjectRoot, SourceCommit, SpecCommit, PlanCommit) -> ordered map`

- [ ] **Step 1: Add a deterministic 68-path temporary Git fixture**

Add `_protected_git_lineage_fixture(tmp_path)` to the existing launcher test file. It must:

```python
transition_path = "docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md"
plan_path = "docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md"
unchanged_paths = [f"protected/record-{index:02d}.txt" for index in range(67)]
assert len(unchanged_paths) == 67
```

Create one temporary Git repository with author/committer fixture identity. Commit the 67 unchanged files plus the old spec content as the root state; record the 68 sorted `{path,size,sha256}` root entries. Replace only the spec content and create the docs-only spec commit. Add only `plan_path` and create its direct-child plan commit. Add one implementation-marker commit so the fixture source commit is an append-only descendant. Return the Git executable, repository root, all three commits, spec Git object, root/augmented paths, and expected current records. Use `subprocess.run([...], check=True)` argument vectors only.

- [ ] **Step 2: Write RED tests for the exact launcher transition**

Add these tests:

```python
def test_history_accepts_only_owner_approved_spec_transition(tmp_path: Path) -> None:
    fixture = _protected_git_lineage_fixture(tmp_path)
    completed = _invoke_augmented_history(fixture)
    assert completed.returncode == 0, completed.stderr
    document = json.loads(Path(fixture["output"]).read_text(encoding="utf-8"))
    assert document["protected_git"] == fixture["root_records"]
    assert document["current_protected_git"] == fixture["current_records"]
    assert document["approved_protected_git_transitions"] == [fixture["transition"]]


def test_history_records_all_67_unchanged_protected_git_paths(tmp_path: Path) -> None:
    fixture = _protected_git_lineage_fixture(tmp_path)
    completed = _invoke_augmented_history(fixture)
    assert completed.returncode == 0, completed.stderr
    document = json.loads(Path(fixture["output"]).read_text(encoding="utf-8"))
    root = {record["path"]: record for record in document["protected_git"]}
    current = {record["path"]: record for record in document["current_protected_git"]}
    unchanged = [path for path in root if path != fixture["transition_path"]]
    assert len(unchanged) == 67
    assert all(root[path] == current[path] for path in unchanged)
```

Parameterize a rejection test over: missing transition, second transition, wrong path, wrong reason, root size/hash mutation, current size/hash mutation, wrong spec commit, wrong spec object, wrong plan commit, non-parent plan, dirty spec, staged spec, missing unchanged path, changed unchanged path, extra current path, duplicate root/current path, symlinked transition, and existing augmented destination.

- [ ] **Step 3: Run the launcher lineage tests to verify RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'protected_git or approved_spec_transition or plan_lineage'
```

Expected: the new assertions fail because `current_protected_git`, `approved_protected_git_transitions`, and the exact lineage validation do not exist. Fixture, syntax, Git setup, or permission failures are not acceptable RED evidence.

- [ ] **Step 4: Implement the launcher-side closed transition**

Extend `New-A7AugmentedBaseline` with these mandatory parameters:

```powershell
[Parameter(Mandatory = $true)][string]$GitExecutable,
[Parameter(Mandatory = $true)][string]$ExpectedSpecCommit,
[Parameter(Mandatory = $true)][string]$ExpectedPlanCommit
```

Use these exact constants:

```powershell
$TransitionPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md'
$TransitionReason = 'owner-approved-design-amendment'
```

Validate before publication:

```text
root protected_git count = 68
current protected_git count = 68
approved transition count = 1
HEAD = SourceCommit
ExpectedPlanCommit^ = ExpectedSpecCommit
last commit touching TransitionPath = ExpectedSpecCommit
last commit touching PlanPath = ExpectedPlanCommit
SpecCommit diff-tree = TransitionPath only
PlanCommit diff-tree = PlanPath only
index and worktree = clean
git -C $ProtectedRootPath hash-object --path=$TransitionPath -- $FullPath = SpecCommit:$TransitionPath
```

Preserve the root array as parsed and compare its compact JSON to the published `protected_git` compact JSON after parse-back. Build the other two structures with only these fields and this order:

```powershell
$Transition = [pscustomobject][ordered]@{
    path = $TransitionPath
    root_size = [long]$RootRecord.size
    root_sha256 = [string]$RootRecord.sha256
    current_size = [long]$CurrentRecord.size
    current_sha256 = [string]$CurrentRecord.sha256
    spec_commit = $ExpectedSpecCommit
    spec_git_object = $SpecGitObject
    plan_commit = $ExpectedPlanCommit
    reason = $TransitionReason
}
```

For every non-transition path, require exact root/current path, size, and SHA-256 equality. Reject any missing, extra, duplicate, linked, dirty, wrong-object, wrong-parent, or unrecorded entry before `Write-A7NewText` claims the augmented destination.

- [ ] **Step 5: Run the launcher lineage tests to verify GREEN**

Run the Step 3 command. Expected: every selected test passes.

- [ ] **Step 6: Write RED tests for independent Task 8 lineage enforcement**

Extract `Test-A7ProtectedGitLineage` from the runner AST and invoke it against the same temporary repository and baseline pair. Add:

```python
def test_task8_accepts_the_exact_approved_protected_git_transition(tmp_path: Path) -> None:
    fixture = _protected_git_lineage_fixture(tmp_path)
    completed = _invoke_task8_lineage_probe(fixture)
    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["status"] == "PRESERVED"


def test_task8_runner_calls_lineage_gate_before_history_gate() -> None:
    calls = _top_level_function_calls(_RUNNER)
    assert calls.index("Test-A7ProtectedGitLineage") < calls.index("Test-HistoricalBaseline")
```

Reuse the mutation list from Step 2 and require nonzero exit for every forbidden transition. The probe must execute the new runner function, not call the launcher verifier.

- [ ] **Step 7: Run the Task 8 lineage tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'task8 and (lineage or protected_git)'
```

Expected: failure because the runner function and mandatory call do not exist.

- [ ] **Step 8: Implement the independent Task 8 lineage gate**

Add `Test-A7ProtectedGitLineage` to `scripts/run_wave0_a7.ps1`. It independently reads and hashes both baseline files, requires the root `protected_git` array to match the augmented root array exactly, requires exact closed property sets for all three structures, verifies the one transition and direct spec/plan Git lineage, and rehashes all 68 current paths against `current_protected_git`. Use Git argument vectors; never rewrite a baseline or substitute a computed owner value.

In the production runner, call:

```powershell
$ProtectedGit = Test-A7ProtectedGitLineage `
    -RootBaselinePath $RootBaselinePath `
    -RootBaselineSha256 $RootBaselineSha256 `
    -AugmentedBaselinePath ([string]$Lease.historical_baseline_path) `
    -AugmentedBaselineSha256 ([string]$Lease.historical_baseline_sha256) `
    -ProjectRoot $ProjectRoot `
    -SourceCommit $SourceCommit `
    -SpecCommit ([string]$Lease.spec_commit) `
    -PlanCommit ([string]$Lease.plan_commit)
$Historical = Test-HistoricalBaseline `
    -RootBaselinePath $RootBaselinePath `
    -RootBaselineSha256 $RootBaselineSha256 `
    -AugmentedBaselinePath ([string]$Lease.historical_baseline_path) `
    -AugmentedBaselineSha256 ([string]$Lease.historical_baseline_sha256)
```

Remove only the current-checkout rehash loop from `Test-HistoricalBaseline`; retain its root-versus-augmented protected-array equality, artifact subset/exact-set checks, image checks, and return shape. The production path has no branch that skips `$ProtectedGit`.

- [ ] **Step 9: Run Task 8 and all history tests to verify GREEN**

```powershell
uv run --no-sync pytest -q `
  tests/gates/test_wave0_a7_launcher.py `
  tests/diagnostics/test_grid_sample_attribution.py `
  -k 'history or lineage or protected_git'
```

Expected: new strict lineage tests and existing artifact-history tests all pass.

- [ ] **Step 10: Commit the lineage slice**

```powershell
git add -- `
  scripts/start_wave0_a7.ps1 `
  scripts/run_wave0_a7.ps1 `
  tests/gates/test_wave0_a7_launcher.py
git -c user.name=kuotunyu `
    -c user.email=61350295+kuotunyu@users.noreply.github.com `
    commit -m 'fix: bind approved A7 Git lineage'
```

Verify the commit changes exactly the three allowlisted files and the worktree is clean.

---

### Task 3: Close Container Ownership and Task 7 Audit Bindings with TDD

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Modify: `scripts/start_wave0_a7.ps1`
- Modify: `scripts/run_wave0_a7.ps1`

**Interfaces:**
- Adds `Select-A7ProjectContainers(ContainerRecordsJson, RegisteredImageIdsJson) -> object[]`
- `20-image-build-result.json` becomes the closed build binding audit
- Adds raw payload `22-a7-cpu-micro-check-payload.json`
- `22-a7-cpu-micro-check.json` becomes the closed CPU micro-check binding audit
- `Test-Task7AuditBinding` independently validates both audit documents against the lease

- [ ] **Step 1: Write RED tests for immutable container ownership**

Add literal inspect records with the exact shape:

```python
record = {
    "id": "a" * 64,
    "name": "unrelated",
    "configured_image": "nvidia/cuda@sha256:" + "b" * 64,
    "image_id": "sha256:" + "c" * 64,
}
```

Parameterize matches for exact names beginning `val-a7-` and `val-wave0-`, a configured `vision-active-learning-loop:wave0-*` tag, and an immutable image ID equal to one registered Wave 0 image ID even when `configured_image` is a digest. Add nonmatches for substring-only names, non-Wave-0 tags, and unrelated IDs. Reject malformed/duplicate container IDs, missing inspect fields, non-SHA image IDs, and duplicate registered image IDs.

- [ ] **Step 2: Run container tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'project_container or digest_launched'
```

Expected: failure because the selector and immutable-ID matching do not exist.

- [ ] **Step 3: Implement closed container collection and selection**

`Invoke-A7Production` must obtain running IDs with:

```text
docker ps --no-trunc --quiet
```

For each exact ID, obtain one inspect object with:

```text
docker container inspect --format {{json .}} -- $ContainerId
```

Normalize only these closed fields: `id`, name without the single Docker-leading slash, `Config.Image` as `configured_image`, and `.Image` as `image_id`. `Select-A7ProjectContainers` returns a record when any approved name/reference/immutable-ID condition matches. Collect historical Wave 0 image tag/ID records before classifying containers so digest-launched containers are detectable. Feed only the selected closed records to `Test-A7DockerGpuPreflight`; one selected record blocks lease acquisition.

- [ ] **Step 4: Run container tests to verify GREEN**

Run the Step 2 command. Expected: all selected tests pass.

- [ ] **Step 5: Write RED tests for complete build and micro-check binding audits**

After a controlled successful launch, assert that `20-image-build-result.json` contains only:

```python
BUILD_AUDIT_FIELDS = {
    "schema_version", "owner_authorization_id", "run_id", "source_commit",
    "spec_commit", "plan_commit", "branch", "image_tag", "image_id",
    "base_image_digest", "argv", "augmented_baseline_path",
    "augmented_baseline_sha256", "argv_audit_path", "argv_audit_sha256",
    "stdout_path", "stdout_sha256", "stderr_path", "stderr_sha256",
    "exit_code", "started_at", "completed_at",
}
```

Assert that `22-a7-cpu-micro-check-payload.json` is byte-for-byte the one compact JSON line returned by the controlled micro-check and that `22-a7-cpu-micro-check.json` contains only:

```python
MICROCHECK_AUDIT_FIELDS = {
    "schema_version", "owner_authorization_id", "run_id", "source_commit",
    "spec_commit", "plan_commit", "branch", "image_tag", "image_id",
    "base_image_digest", "augmented_baseline_path", "augmented_baseline_sha256",
    "source_inventory_path", "source_inventory_sha256", "payload_path",
    "payload_sha256", "payload", "docker_argv", "stdout_path", "stdout_sha256",
    "stderr_path", "stderr_sha256", "exit_code", "started_at", "completed_at",
}
```

For each audit, parameterize missing, extra, wrong identity, wrong path, changed log/payload hash, changed argv, nonzero exit, malformed timestamp, and existing-destination cases. Assert no lease file is created on any mutation.

- [ ] **Step 6: Run audit-binding tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'build_audit or microcheck_audit or audit_binding'
```

Expected: failures because the current build audit omits required identities and the current micro-check audit is only the raw payload.

- [ ] **Step 7: Implement the two closed audits and raw payload separation**

Capture `started_at` immediately before each external invocation and `completed_at` immediately after it returns. Publish paths relative to or contained by the campaign audit root, require safe regular non-link files, and recompute every hash before audit publication. Publish the payload with `Write-A7NewText` before the binding audit. Parse back both audits, require exact property sets and equality to runtime inputs, then pass only the binding-audit SHA-256 values to `New-A7Lease`.

Enhance Task 8 `Test-Task7AuditBinding` to parse the two binding audits and independently require their exact property sets and equality to the lease's owner/run/source/spec/plan/image/base/baseline identities. It also rehashes the argv audit, logs, source inventory, and raw payload. A hash-only receipt check is insufficient.

- [ ] **Step 8: Run audit-binding tests to verify GREEN**

Run the Step 6 command. Expected: all selected tests pass.

- [ ] **Step 9: Commit the container/audit slice**

```powershell
git add -- `
  scripts/start_wave0_a7.ps1 `
  scripts/run_wave0_a7.ps1 `
  tests/gates/test_wave0_a7_launcher.py
git -c user.name=kuotunyu `
    -c user.email=61350295+kuotunyu@users.noreply.github.com `
    commit -m 'fix: close A7 launch audit bindings'
```

Verify exact three-file scope and a clean worktree.

---

### Task 4: Separate Post-Task-8 Validation Failure Evidence with TDD

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Modify: `scripts/start_wave0_a7.ps1`

**Interfaces:**
- Adds `Close-A7PostTask8ValidationFailure(...) -> pscustomobject`
- Produces `52-task7-post-task8-validation-failure.json` and `53-task7-post-task8-validation-closure.json`
- Never calls `Close-A7Campaign` after Task 8 has been invoked

- [ ] **Step 1: Extend the controlled Task 8 adapter with exact failure modes**

Add modes that invoke Task 8 exactly once and then produce: a valid terminal with nonzero exit, missing `30`, missing `40`, missing `41`, missing `51`, malformed result, malformed closure, terminal mismatch, closure-file hash drift, active lease left in place, missing released lease, missing release record, and pre-existing `52` or `53`. Each mode records `task8_count` before producing evidence. A valid nonzero exit with complete hash-valid evidence remains a normal closed Task 8 result and must not produce `52/53`.

- [ ] **Step 2: Write RED post-Task-8 closure tests**

Add:

```python
@pytest.mark.parametrize(
    "mode",
    [
        "task8_missing_30", "task8_missing_40",
        "task8_missing_41", "task8_missing_51", "task8_malformed_result",
        "task8_malformed_closure", "task8_terminal_mismatch",
        "task8_hash_drift", "task8_active_lease", "task8_missing_release",
        "task8_missing_release_record",
    ],
)
def test_post_task8_validation_failure_uses_only_52_53_evidence(
    tmp_path: Path, mode: str
) -> None:
    fixture = _launch_fixture(tmp_path, mode=mode)
    completed = _invoke_functions(_LAUNCH_FUNCTIONS, _launch_body(fixture))
    assert completed.returncode == 0, completed.stderr
    state = json.loads(Path(fixture["task8_state"]).read_text(encoding="utf-8"))
    assert state["task8_count"] == 1
    audit = Path(fixture["campaign"]) / "audit"
    assert (audit / "52-task7-post-task8-validation-failure.json").is_file()
    assert (audit / "53-task7-post-task8-validation-closure.json").is_file()
```

Snapshot every Task 8-owned file that exists before launcher-side validation and assert its size/SHA-256 is unchanged afterward. For active-lease mode, assert the active lease remains active and is recorded as such. For pre-existing `52`/`53`, assert nonzero failure, unchanged destination bytes, and no second Task 8 invocation.

Add a separate `test_task8_nonzero_with_complete_evidence_remains_a_valid_closed_result` assertion: invocation count is one, the exact nonzero exit is reported, the hash-valid Task 8 terminal is returned, and neither `52` nor `53` exists.

- [ ] **Step 3: Run post-Task-8 tests to verify RED**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'post_task8 or task8_nonzero or missing_release'
```

Expected: current code enters `Close-A7Campaign`, collides with Task 8-owned destinations, or lacks `52/53`; the new assertions fail.

- [ ] **Step 4: Implement the no-clobber `52/53` records**

Before publishing either record, require both destinations absent and the audit root safe. Enumerate the complete pre-publication campaign file inventory as sorted records `{path,size,sha256}`. Build a sorted `required_files` array for exactly `30`, `40`, `41`, and `51`, recording `exists`, and size/SHA-256 only for a safe regular existing file. Build a closed lease-state object for active, released, and release-record paths without moving or reinterpreting any file.

The failure record contains only:

```powershell
$FailureRecord = [ordered]@{
    schema_version = 1
    owner_authorization_id = $OwnerAuthorizationId
    run_id = $RunId
    source_commit = $ExpectedSourceCommit
    spec_commit = $ExpectedSpecCommit
    plan_commit = $ExpectedPlanCommit
    image_tag = $ImageTag
    image_id = $ImageId
    campaign_root = $CampaignRoot
    task8_exit_code = [int]$Task8Result.exit_code
    observed_terminal = $ObservedTerminal
    validation_error = $ValidationError
    required_files = @($RequiredFiles)
    lease_state = $LeaseState
    pre_publication_files = @($PrePublicationFiles)
    recorded_at = [DateTimeOffset]::UtcNow.ToString('o')
}
```

After atomically writing and hashing `52`, publish `53` with the same immutable identity, Task 8 exit, observed terminal, validation error, lease state, and pre-publication inventory plus:

```powershell
status = 'POST_TASK8_VALIDATION_FAILED'
failure_record = [ordered]@{
    path = 'audit/52-task7-post-task8-validation-failure.json'
    size = [long]$FailureFile.Length
    sha256 = $FailureSha256
}
```

Parse and rehash both records. The returned launcher result reports `task8_invocation_count = 1`, the exact Task 8 exit, `validation_status = 'FAILED'`, and does not claim a new diagnostic terminal when the Task 8 terminal is unavailable or invalid.

- [ ] **Step 5: Route the state machine by invocation state**

Initialize `$Task8Invoked = $false`; set it to `$true` immediately before the one `Invoke-A7Native` call for Task 8. Wrap only post-return evidence validation in its own `try/catch`. That catch calls `Close-A7PostTask8ValidationFailure` once. The outer catch may call `Close-A7Campaign` only while `$Task8Invoked -eq $false`. No catch, finally block, or helper calls Task 8 or moves a lease.

- [ ] **Step 6: Run post-Task-8 and exactly-once tests to verify GREEN**

```powershell
uv run --no-sync pytest -q tests/gates/test_wave0_a7_launcher.py -k 'post_task8 or task8 or exactly_once or closure'
```

Expected: all selected tests pass; every mode invokes Task 8 once; Task 8-owned files remain unchanged; `52/53` are no-clobber; lease state is factual.

- [ ] **Step 7: Commit the post-Task-8 slice**

```powershell
git add -- scripts/start_wave0_a7.ps1 tests/gates/test_wave0_a7_launcher.py
git -c user.name=kuotunyu `
    -c user.email=61350295+kuotunyu@users.noreply.github.com `
    commit -m 'fix: preserve A7 post-Task-8 evidence'
```

Verify the commit changes exactly those two allowlisted files and the worktree is clean.

---

### Task 5: Run the Mandatory Candidate Gates and Independent Review

**Files:**
- Modify: none unless a Critical/Important finding requires a new RED/GREEN fix inside the exact three-file allowlist
- Read: approved Sections 5.2.10–5.2.11, this plan, all three implementation files, Git/Docker/history evidence

**Interfaces:**
- Consumes: all append-only implementation commits from Tasks 2–4
- Produces: one clean candidate SHA with Critical=0 and Important=0

- [ ] **Step 1: Run the focused behavior suite**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -q `
  tests/gates/test_wave0_a7_launcher.py `
  tests/diagnostics/test_grid_sample_attribution.py `
  tests/diagnostics/test_wave0_a7_cpu_microcheck.py `
  tests/diagnostics/test_tensor_evidence.py `
  tests/artifacts/test_receipts.py
```

Expected: zero failures; record exact passed/skipped counts from fresh output.

- [ ] **Step 2: Run the complete CPU suite**

```powershell
uv run --no-sync pytest -q
```

Expected: zero failures; only capability skips are allowed. Do not predict counts.

- [ ] **Step 3: Run formatting, lint, lock, diff, and parser gates**

```powershell
uv run --no-sync black --check tests/gates/test_wave0_a7_launcher.py
uvx --offline ruff check tests/gates/test_wave0_a7_launcher.py
uv lock --check
git diff --check
$ParseFailures = [System.Collections.Generic.List[string]]::new()
foreach ($Path in @('scripts/start_wave0_a7.ps1', 'scripts/run_wave0_a7.ps1')) {
    $Tokens = $null
    $Errors = $null
    [void][Management.Automation.Language.Parser]::ParseFile(
        (Resolve-Path $Path), [ref]$Tokens, [ref]$Errors
    )
    foreach ($ErrorRecord in @($Errors)) { [void]$ParseFailures.Add("${Path}: $($ErrorRecord.Message)") }
}
if ($ParseFailures.Count -ne 0) { $ParseFailures; throw 'PowerShell parse gate failed' }
```

Expected: every command exits zero and both scripts have zero parser errors.

- [ ] **Step 4: Verify exact cumulative implementation scope and lineage**

```powershell
$PlanPath = 'docs/superpowers/plans/2026-08-26-val-wave0-a7-history-compatibility.md'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$Changed = @(git diff --name-only "$PlanCommit..HEAD")
$Allowed = @(
    'scripts/run_wave0_a7.ps1',
    'scripts/start_wave0_a7.ps1',
    'tests/gates/test_wave0_a7_launcher.py'
) | Sort-Object -CaseSensitive
if ((($Changed | Sort-Object -CaseSensitive) -join "`n") -cne ($Allowed -join "`n")) {
    throw 'implementation scope mismatch'
}
git log --format='%H %P %an <%ae> | %cn <%ce>' "$PlanCommit..HEAD"
git status --porcelain=v1
```

Require append-only ancestry, exact author/committer, exactly the three allowlisted cumulative paths, empty staging, and clean linked/canonical worktrees.

- [ ] **Step 5: Reverify all immutable external evidence read-only**

From the complete baseline, rehash all 64,011 artifacts, inspect all 14 registered image IDs, compare all 68 immutable root protected-Git records, validate the exact approved spec transition/current 68-record array, and recompute seven fixed A6 hashes. Require no active project container/lease, unset `VAL_DATA_ROOT`, Docker context `desktop-linux`, Linux Server health, and read-only visibility of exactly one RTX 4090. Do not build, run the project image, create a campaign, or claim a lease.

- [ ] **Step 6: Perform the independent local review**

Review every cumulative diff line against Sections 5.2.10–5.2.11 and this plan. Explicitly inspect:

```text
root protected_git serialization remains unchanged
exact 68/68/1 protected-Git structure counts
all 67 unchanged paths remain exact
spec/plan direct-parent lineage and Git object verification
no production route skips Task 8 lineage enforcement
container names, configured references, and immutable image IDs
no-trunc container enumeration
complete build and micro-check audit field sets
raw payload separated and hash-bound
lease hashes only binding audits
pre-Task-8 versus post-Task-8 failure routing
Task 8 invocation count exactly one
30/40/41/51 ownership remains Task 8-only after invocation
52/53 atomic no-clobber behavior
active/released lease state is never fabricated
no RDD, Wave 1, retry, Docker mutation, or remote operation
```

Critical and Important findings must be fixed with a new RED test, observed RED failure, minimal allowlisted fix, GREEN rerun, complete gate rerun, and append-only commit. A required fourth file or external-state mutation stops immediately.

- [ ] **Step 7: Freeze and report the reviewed candidate**

Report exact spec commit/size/SHA/object, plan commit, each implementation commit, final candidate SHA, three-file cumulative diff, focused/full test counts, Black/Ruff/lock/diff/parser outcomes, review counts, history/image/fixed-evidence hashes, Docker/GPU read-only state, and both Git statuses.

Terminal:

```text
A7_HISTORY_COMPATIBILITY_IMPLEMENTATION_COMMITTED / OWNER_CANDIDATE_REVIEW_REQUIRED
```

Do not invoke the launcher or Task 8 without a later owner prompt naming the exact reviewed candidate, authorizing a fresh owner-authorization ID, new run ID, fresh image, fresh campaign root, and fresh lease destination.

---

## Plan Self-Review Record

- [x] The plan commit is constrained to be the direct child of specification commit `adfb54bb9c53238eddafa714e202925d5b9aae7e` and records the exact checked-out spec size, SHA-256, and Git object.
- [x] The future implementation allowlist is exactly the three files authorized by Section 5.2.11; a fourth file is a hard stop.
- [x] The immutable root 68-record array, complete current 68-record array, exact one-transition array, all 67 unchanged paths, and the sole spec transition have independent launcher and Task 8 RED/GREEN coverage.
- [x] Existing isolated artifact-history tests remain valid while the production Task 8 flow unconditionally runs the new strict lineage gate first.
- [x] Container ownership covers `val-a7-`, `val-wave0-`, Wave 0 tags, and immutable registered image IDs, including digest-launched containers.
- [x] Build and CPU micro-check audits have exact closed fields, raw payload separation, log/argv/payload hashes, parse-back checks, and lease bindings.
- [x] Every post-Task-8 validation failure writes only atomic `52/53` evidence, preserves Task 8-owned `30/40/41/51`, records factual lease state, and never retries Task 8.
- [x] Focused/full tests, Black, Ruff, PowerShell parse, `uv lock --check`, `git diff --check`, complete history/image/fixed-evidence verification, Critical=0/Important=0 review, author/committer, and clean Git gates are explicit.
- [x] No step authorizes a real build, GPU campaign, lease, RDD, Wave 1, remote, push, merge, tag, Release, or publication.
- [x] No unresolved placeholder, implicit wildcard, ambiguous path, unowned receipt, inconsistent function signature, or omitted normative failure branch remains.

**Plan terminal:** `A7_HISTORY_COMPATIBILITY_PLAN_COMMITTED / OWNER_IMPLEMENTATION_PLAN_REVIEW_REQUIRED`
