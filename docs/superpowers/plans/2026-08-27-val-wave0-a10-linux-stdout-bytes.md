# Wave 0 A10 Linux Stdout Bytes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the successful model-cache preflight token byte-exact as Linux `PASS\n` in both Task 7 and Task 8 without changing any other process, receipt, cache, or diagnostic contract.

**Architecture:** Task 7 compares only the cache-preflight child process's decoded stdout to PowerShell ``"PASS`n"`` while retaining exact exit-code-zero and empty-stderr gates. Task 8 reads the hash-bound stdout file as bytes and independently requires `50 41 53 53 0a`. The generic native runner and every other stage remain unchanged.

**Tech Stack:** PowerShell 7 and Windows PowerShell 5.1, Python 3.12.11 test adapters, pytest, Docker Desktop Linux engine, Git append-only commits, RTX 4090 only after all pre-lease gates pass.

## Global Constraints

- The authoritative specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `c7eb8ae5aaccdfc4bbf681e8f07a994bee5e30c0`, especially Section 5.2.14.
- At that commit the specification Git blob is exactly 183,503 bytes, SHA-256 `cfc805ff07843357e8ddcd7529d5693838a4d9b010591a68c2ee2772ab3052de`, and Git object `3d8f888da914b46facca0f0548b95cb625977313`.
- This plan must be committed as the direct child of that specification commit and that commit must change only this new plan file.
- The branch is exactly `codex/wave0-model-contract`; the registered linked worktree and canonical `main` worktree must share one Git common directory and be clean before implementation and runtime execution.
- Preserve closed A9 campaign `wave0-a7-20260827T021745408Z`, image `sha256:b0f3f64275d99fd9965759db51d09fc9804bb3ae55d7a370a53a7ed65109bdc3`, its 48-entry manifest and 50-file closure, its 31 cache-preflight files, and every earlier artifact, image, receipt, log, lease record, and audit byte-for-byte.
- The A9 evidence hashes fixed by Section 5.2.14 are immutable. The pre-A9 historical baseline remains 64,140 artifacts and 19 images; after adding the closed A9 campaign and image, the A10 entry inventory is 64,190 artifact files and 20 project images.
- The canonical successful cache-preflight stdout is exactly the five UTF-8 bytes `50 41 53 53 0a`. Do not trim, split, normalize, rewrite, accept CRLF, or accept a missing newline.
- Exit code must remain zero, stderr must remain zero bytes, and the model-assets receipt must remain schema-valid PASS with no normative errors. A10 does not reinterpret A9 as a pass.
- Keep the A9 cache-preflight Docker argv exactly 33 elements, including `HF_HUB_DISABLE_PROGRESS_BARS=1` and `HF_HUB_VERBOSITY=error` at their fixed positions. Do not pass a token, environment file, secret, host-wide environment, or extra logging control.
- Keep cache preflight as the only networked stage (`--network bridge`) and CPU-only. Keep Task 8 `--network none`, `--gpus all`, `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, and the run-scoped model cache mounted read-only.
- The implementation tracked-file allowlist is closed to `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, and `tests/gates/test_wave0_a7_launcher.py`. A fourth tracked implementation file is a hard stop.
- Do not change any Python production module, schema, Dockerfile, configuration, dependency, `uv.lock`, model revision, payload/metadata/lock hash, labels, query count, seed, dataset, acquisition arm, fit count, threshold, warning rule, numerical bound, or research claim.
- No RDD access, Wave 1, remote operation, push, merge, tag, Release, publication, historical cleanup, reuse of a prior run ID, or overwrite of an existing destination is authorized.

---

### Task 1: Freeze A10 entry identity and preservation baseline

**Files:**
- Modify: none
- Historical evidence: read-only
- Temporary output: one no-clobber JSON below `[IO.Path]::GetTempPath()`

**Interfaces:**
- Consumes: A10 specification commit, this plan's future direct-child commit, registered worktree, closed A9 campaign and image
- Produces: exact pre-change identities and a complete external preservation snapshot

- [ ] **Step 1: Verify docs lineage and Git topology**

Run:

```powershell
$SpecPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a10-linux-stdout-bytes.md'
$SpecCommit = 'c7eb8ae5aaccdfc4bbf681e8f07a994bee5e30c0'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
if ((git rev-parse "$PlanCommit^").Trim() -cne $SpecCommit) {
    throw 'A10 plan parent mismatch'
}
if (@(git diff-tree --no-commit-id --name-only -r $SpecCommit).Count -ne 1) {
    throw 'A10 specification scope mismatch'
}
if (@(git diff-tree --no-commit-id --name-only -r $PlanCommit).Count -ne 1) {
    throw 'A10 plan scope mismatch'
}
git worktree list --porcelain
git status --short
git diff --cached --name-only
```

Require the linked branch to be `codex/wave0-model-contract`, its HEAD to be the plan commit, both worktrees clean, the staging area empty, and the Git common directories equal.

- [ ] **Step 2: Verify the A9 failure boundary exactly**

Require these immutable identities:

```text
stdout                 c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431
stderr                 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
model-assets receipt   af709bb6317d73607bb28dacc51ac3af945e7138952a8e664f03e5a45044d7f3
failure diagnostic     45ab59a8adb0897819912a6cdacd05c6d442dfee572aec320be16175fd56a1c9
campaign result        7e0147bebc17bda440941ac1888143d16fe49250d5c4d9f913fb0f5aa3f26c34
file manifest          676bff30ce5b6a93dbbf3dd2f80e812f1c8dcd92e4587cfcf3ede558568d6d9c
closure manifest       690dc7974eb7b4c7fa87f8fc3fe2935c253f4c88e58bf61bb83f3f781ed68337
```

Read the stdout as bytes and require `50-41-53-53-0A`; require the stderr length to be zero; parse the receipt and require PASS with zero errors; parse the result and require `model_cache_preflight`, `FAILED`, no lease, Task 8 count zero, and the exact Wave-1-forbidden terminal. Rehash all 48 manifest entries plus the manifest and closure themselves.

- [ ] **Step 3: Publish a no-clobber pre-change record outside the repository**

Enumerate and hash all 64,190 current artifact files and inspect all 20 project image tags/IDs. Include protected Git records, both worktree states, specification/plan identities, A9 fixed evidence, `VAL_DATA_ROOT` presence only, active lease paths, and running project containers. Write the timestamped JSON with `[IO.FileMode]::CreateNew`, parse it back, and record its SHA-256. Do not write under the repository or artifact root.

---

### Task 2: Add RED coverage for raw LF and fail-closed byte validation

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: real `Invoke-A7Native`, `Invoke-A7ModelCachePreflight`, and `Test-Task7AuditBinding`
- Produces: two independent RED signals for Task 7 host-derived newline rejection and Task 8 logical-line overacceptance

- [ ] **Step 1: Make the real cache-preflight adapter emit raw Linux bytes**

Change `_write_model_cache_preflight_adapter` to accept `stdout_bytes: bytes = b"PASS\n"`. Keep its current source as a plain triple-quoted string with a unique `__STDOUT_BYTES__` marker, replace that marker with `repr(stdout_bytes)`, and make its final output:

```python
sys.stdout.buffer.write(b"PASS\n")
```

Do not use `print`, `text=True`, `os.linesep`, or an expectation derived from the PowerShell code. Retain the real receipt creation and argv recording. Add an assertion that the published stdout log equals literal `b"PASS\n"`.

- [ ] **Step 2: Add Task 7 noncanonical-byte rejection tests**

Define one literal tuple used only by tests:

```python
_NONCANONICAL_MODEL_CACHE_STDOUT = (
    b"PASS",
    b"PASS\r\n",
    b"PASS\n\n",
    b" PASS\n",
    b"PASS \n",
    b"\xef\xbb\xbfPASS\n",
    b"pass\n",
    b"PASS\nextra",
    b"",
)
```

Extract the existing real-function setup into `_invoke_model_cache_preflight(tmp_path: Path, stdout_bytes: bytes) -> tuple[subprocess.CompletedProcess[str], dict[str, Path]]`; it must still create a new campaign/audit/worktree/baseline/adapter/state, call the real three PowerShell functions, and return the completed process plus paths for `campaign`, `audit`, `state`, and `baseline`. Keep the existing success test's detailed argv/audit/receipt/no-clobber assertions. Add `test_model_cache_preflight_rejects_noncanonical_stdout`, parameterized over the literal tuple, and require nonzero return plus `A7 model-cache preflight process contract failed`.

- [ ] **Step 3: Make the closed Task 7 fixture canonical**

Replace the text-mode stdout write in `_closed_audit_fixture` with:

```python
model_cache_stdout.write_bytes(b"PASS\n")
```

Recompute its existing audit hash normally. Do not alter any receipt, stderr, Docker argv, cache, or lease fixture.

- [ ] **Step 4: Add Task 8 noncanonical-byte rejection tests**

Add `test_task8_rejects_noncanonical_model_cache_stdout`, parameterized over `_NONCANONICAL_MODEL_CACHE_STDOUT`. For each case, write only `fixture["model_cache_stdout"]`, update `model_cache_audit_document["stdout_sha256"]` to the new literal file hash, rewrite `model_cache_audit`, let `_task7_audit_binding_body` bind the recomputed audit hash, invoke real `Test-Task7AuditBinding`, and require a nonzero return containing `Task 7 model-cache stdout byte contract mismatch`.

- [ ] **Step 5: Advance the test plan fixture to A10**

Set `_COMPATIBILITY_PLAN_PATH` to `docs/superpowers/plans/2026-08-27-val-wave0-a10-linux-stdout-bytes.md`. Rename the static lineage regression to A10 and require the exact A10 plan path in both scripts while rejecting the A9, A8, and A7 history-plan paths.

- [ ] **Step 6: Run RED tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q `
  tests/gates/test_wave0_a7_launcher.py::test_model_cache_preflight_is_networked_cpu_only_and_audited `
  tests/gates/test_wave0_a7_launcher.py::test_model_cache_preflight_rejects_noncanonical_stdout `
  tests/gates/test_wave0_a7_launcher.py::test_task8_rejects_noncanonical_model_cache_stdout `
  tests/gates/test_wave0_a7_launcher.py::test_launcher_and_runner_bind_the_a10_plan_identity
```

Expected RED causes are exact: Task 7 rejects raw LF because it expects Windows CRLF; Task 8 accepts at least raw `PASS` or CRLF because it reads logical lines; both scripts still name A9. Syntax, fixture, receipt, path, or unrelated failures are invalid RED evidence.

---

### Task 3: Make Task 7 require the Linux stdout token

**Files:**
- Modify: `scripts/start_wave0_a7.ps1`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: `Invoke-A7Native` result string and raw stdout file
- Produces: a closed Task 7 cache audit only for exit zero, exact `PASS\n`, empty stderr, and a valid receipt

- [ ] **Step 1: Change only the cache-preflight stdout comparison**

In `Invoke-A7ModelCachePreflight`, replace:

```powershell
[string]$Result.stdout -cne "PASS$([Environment]::NewLine)"
```

with:

```powershell
[string]$Result.stdout -cne "PASS`n"
```

Retain the adjacent exit-code and empty-stderr predicates exactly. Do not change `Invoke-A7Native`, `Write-A7NewText`, receipt validation, audit publication, or any other stage.

- [ ] **Step 2: Advance both Task 7 plan paths to A10**

Set `$PlanPath` in `New-A7AugmentedBaseline` and `$PlanRelativePath` in `Invoke-A7Production` to:

```text
docs/superpowers/plans/2026-08-27-val-wave0-a10-linux-stdout-bytes.md
```

- [ ] **Step 3: Run the Task 7 tests to GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q `
  tests/gates/test_wave0_a7_launcher.py::test_model_cache_preflight_is_networked_cpu_only_and_audited `
  tests/gates/test_wave0_a7_launcher.py::test_model_cache_preflight_rejects_noncanonical_stdout `
  tests/gates/test_wave0_a7_launcher.py::test_launcher_and_runner_bind_the_a10_plan_identity
```

The first two tests must pass. The combined plan test may remain RED only because the Task 8 script still names A9.

---

### Task 4: Make Task 8 validate the exact stdout bytes

**Files:**
- Modify: `scripts/run_wave0_a7.ps1`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: the hash-bound `23-a7-model-cache-preflight.stdout.log`
- Produces: independent exact byte validation before receipt acceptance or GPU work

- [ ] **Step 1: Replace logical-line acceptance with fixed byte checks**

In `Test-Task7AuditBinding`, replace `$ModelCacheStdoutLines` and its line-count/value predicates with:

```powershell
$ModelCacheStdoutBytes = [IO.File]::ReadAllBytes($Paths.model_cache_stdout)
if ($ModelCacheStdoutBytes.Count -ne 5 -or
    $ModelCacheStdoutBytes[0] -ne 0x50 -or
    $ModelCacheStdoutBytes[1] -ne 0x41 -or
    $ModelCacheStdoutBytes[2] -ne 0x53 -or
    $ModelCacheStdoutBytes[3] -ne 0x53 -or
    $ModelCacheStdoutBytes[4] -ne 0x0A) {
    throw 'Task 7 model-cache stdout byte contract mismatch'
}
```

Keep zero-byte stderr, receipt type/version/run/status/errors/models, audit hashes, and path validation unchanged in the following receipt-binding block.

- [ ] **Step 2: Advance Task 8 protected lineage to A10**

Set `$PlanPath` in `Test-A7ProtectedGitLineage` to the exact A10 plan path.

- [ ] **Step 3: Run Task 8 GREEN and mutation coverage**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q `
  tests/gates/test_wave0_a7_launcher.py::test_task8_accepts_closed_task7_binding_audits `
  tests/gates/test_wave0_a7_launcher.py::test_task8_rejects_noncanonical_model_cache_stdout `
  tests/gates/test_wave0_a7_launcher.py::test_launcher_and_runner_bind_the_a10_plan_identity
```

Require all literal noncanonical byte variants to fail with the stdout-byte-contract error while canonical LF passes.

---

### Task 5: Verify, review, and commit the A10 source candidate

**Files:**
- Stage only: `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, `tests/gates/test_wave0_a7_launcher.py`
- Historical evidence: read-only

**Interfaces:**
- Consumes: the final three-file candidate and Task 1 preservation snapshot
- Produces: one clean reviewed append-only source commit

- [ ] **Step 1: Run complete deterministic gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/gates/test_wave0_a7_launcher.py -q
uv run pytest -q
uv run black --check tests/gates/test_wave0_a7_launcher.py
uvx --offline ruff check tests/gates/test_wave0_a7_launcher.py
uv lock --check
git diff --check
```

Parse both PowerShell scripts with the PowerShell parser under `pwsh` and `powershell`; both error arrays must be empty.

- [ ] **Step 2: Verify scope and review the exact diff**

Require `git diff --name-only` to equal exactly the three implementation files. Review Section 5.2.14 line by line and require Critical=0 and Important=0. Specifically confirm canonical bytes in both stages, no generic output normalization, exact A10 plan identity in three locations, no stderr/exit/receipt relaxation, no new environment variable, no network/GPU change, no retry, and no historical mutation.

- [ ] **Step 3: Rehash all immutable history**

Rehash every artifact and inspect every image recorded in Task 1. Require exactly 64,190 pre-candidate artifact files, 20 historical images, the seven fixed A9 hashes, unchanged A9 image ID, no active lease, no project container, and unset `VAL_DATA_ROOT`. Compare exact path, size, hash, and image sets; do not exclude or repair drift.

- [ ] **Step 4: Commit only the reviewed implementation**

```powershell
git add -- scripts/start_wave0_a7.ps1 scripts/run_wave0_a7.ps1 tests/gates/test_wave0_a7_launcher.py
git -c user.name='kuotunyu' `
    -c user.email='61350295+kuotunyu@users.noreply.github.com' `
    commit -m 'fix: require Linux cache preflight stdout bytes'
git status --short
```

Verify the author and committer are `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`, the parent is this plan commit, the commit changes exactly the three files, and both worktrees are clean.

---

### Task 6: Execute one fresh A10-bound attempt and stop at the Wave 1 boundary

**Files:**
- Modify: none
- New runtime outputs: one fresh run ID, image, campaign, cache root, and lease lifecycle only

**Interfaces:**
- Consumes: clean reviewed A10 source, specification, plan, healthy Docker Linux engine and RTX 4090
- Produces: one immutable A7 diagnostic campaign and terminal evidence

- [ ] **Step 1: Run final read-only preflight**

Require exact branch/HEAD, clean linked and canonical worktrees, matching Git common directory, Docker context `desktop-linux`, Linux Client and Server, successful `docker info`, running `docker-desktop` WSL backend, exactly one visible RTX 4090, unset `VAL_DATA_ROOT`, no project container, no active lease, absent candidate tag, unchanged 64,190 historical artifacts and 20 images, and absent fresh destinations. A failed preflight creates no run ID or runtime object.

- [ ] **Step 2: Invoke the checked-in launcher exactly once**

```powershell
$SourceCommit = (git rev-parse HEAD).Trim()
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a10-linux-stdout-bytes.md'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
pwsh -NoProfile -NonInteractive -File scripts/start_wave0_a7.ps1 `
  -OwnerAuthorizationId 'OWNER-STANDING-A10-20260827-UNATTENDED-01' `
  -ExpectedSourceCommit $SourceCommit `
  -ExpectedSpecCommit 'c7eb8ae5aaccdfc4bbf681e8f07a994bee5e30c0' `
  -ExpectedPlanCommit $PlanCommit `
  -ExpectedBranch 'codex/wave0-model-contract'
```

The launcher generates the only run ID. Do not invoke it a second time, even if the terminal is pre-GPU.

- [ ] **Step 3: Validate and report the closed campaign**

Hash and parse every new object that exists: identity, build audit/result/logs, image inspect/source inventory, CPU micro-check, cache audit/receipt/logs, lease, Task 8 control/instrumented/isolated-VJP/aggregate receipts, checkpoint evidence, campaign result/manifest/closure, released lease, and release record. Require historical preservation, clean Git, zero active lease, no running candidate container, RDD untouched, and Wave 1 not started.

Any normative failure preserves the campaign and stops without a fix or retry. Even a complete A7 attribution terminal remains `WAVE0_NOT_PASSED`; no result authorizes Wave 1.
