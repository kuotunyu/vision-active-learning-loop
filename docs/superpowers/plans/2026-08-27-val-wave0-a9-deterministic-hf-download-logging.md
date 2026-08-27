# Wave 0 A9 Deterministic Hugging Face Download Logging Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the exact empty-stderr cache-preflight gate while preventing pinned `huggingface_hub` 1.28.0 progress bars and anonymous server warnings from reaching that stage's stderr.

**Architecture:** Task 7 supplies two fixed, cache-preflight-only Docker environment variables before the read-only workspace and read-write fresh-cache mounts. Task 8 independently validates their exact positions and values from the hash-bound Task 7 audit. No Python verifier, schema, dependency, model, dataset, threshold, or stderr acceptance rule changes.

**Tech Stack:** PowerShell 7 and Windows PowerShell 5.1, Docker Desktop Linux engine, Python 3.12.11, pytest, pinned `huggingface_hub` 1.28.0, Git append-only commits, RTX 4090 only after every pre-lease gate passes.

## Global Constraints

- The authoritative specification is `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `ffd33555509237ced367898985eaf2433b89ed97`, especially Section 5.2.13.
- At that commit the specification is exactly 175,244 bytes, SHA-256 `ab04ef5ff42a7edd613d15b4fc180b037679b250d45de434496b2b7c254f2c22`, and Git object `01791fcc1267ad628c502a6c49e053ca8f287942`.
- This plan must be committed as the direct child of that specification commit and that commit must change only this new plan file.
- The implementation branch is exactly `codex/wave0-model-contract`; the registered linked worktree and canonical `main` worktree must both be clean and share the same Git common directory.
- The implementation tracked-file allowlist is closed to exactly `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, and `tests/gates/test_wave0_a7_launcher.py`. A fourth tracked implementation file is a hard stop.
- Preserve closed campaign `wave0-a7-20260827T010418013Z`, image `sha256:a5d385028e603272065c14c9759034d29a457b47ee8110a68176ffaad0613078`, its 48-file manifest, its fresh 30-file/169,176,408-byte cache, and every earlier artifact, image, receipt, lease, log, and audit byte-for-byte.
- The cache-preflight process gate remains exit code 0, stdout exactly `PASS` plus the platform newline, and stderr exactly zero bytes. Do not filter, normalize, whitelist, delete, or reinterpret stderr after execution.
- The only new runtime argv elements are exact ordered pairs `-e`, `HF_HUB_DISABLE_PROGRESS_BARS=1`, `-e`, `HF_HUB_VERBOSITY=error`, immediately after `-e`, `PYTHONPATH=/workspace/src` and before both mounts.
- Never pass `HF_TOKEN`, `HUGGING_FACE_HUB_TOKEN`, `HF_HOME`, `--env-file`, Docker secrets, token mounts, host-wide environment forwarding, or credentials into the container.
- Keep the cache preflight as the sole networked stage (`--network bridge`) and CPU-only (no `--gpus`). Keep Task 8 `--network none`, `--gpus all`, `HF_HUB_OFFLINE=1`, and `TRANSFORMERS_OFFLINE=1` with the fresh cache mounted read-only.
- Do not change the detector, processor, model revisions, payload or metadata hashes, four-file allowlist, lock inventory, labels, query count, seeds, datasets, acquisition arms, fit counts, dependencies, `uv.lock`, Docker base, thresholds, warning policy, or research claims.
- No RDD access, Wave 1, remote, push, merge, tag, Release, publication, historical cleanup, retry of any earlier campaign, or reuse of any prior run ID is authorized.

---

### Task 1: Reconfirm A9 entry identity and preservation baseline

**Files:**
- Modify: none
- Historical evidence: read-only

**Interfaces:**
- Consumes: specification commit `ffd33555509237ced367898985eaf2433b89ed97`, this plan's future direct-child commit, closed A8 campaign, registered worktree
- Produces: exact entry SHA, plan SHA, and a no-clobber pre-change preservation snapshot outside the repository

- [ ] **Step 1: Verify Git topology and exact document scopes**

```powershell
$SpecPath = 'docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a9-deterministic-hf-download-logging.md'
$SpecCommit = 'ffd33555509237ced367898985eaf2433b89ed97'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$PlanParent = (git rev-parse "$PlanCommit^").Trim()
$SpecFiles = @(git diff-tree --no-commit-id --name-only -r $SpecCommit)
$PlanFiles = @(git diff-tree --no-commit-id --name-only -r $PlanCommit)
if ($PlanParent -cne $SpecCommit) { throw 'A9 plan parent mismatch' }
if ($SpecFiles.Count -ne 1 -or $SpecFiles[0] -cne $SpecPath) { throw 'A9 spec scope mismatch' }
if ($PlanFiles.Count -ne 1 -or $PlanFiles[0] -cne $PlanPath) { throw 'A9 plan scope mismatch' }
git worktree list --porcelain
git status --short
```

Expected: the A9 plan is the specification commit's direct child, each docs commit changed exactly its named file, the linked worktree is on `codex/wave0-model-contract`, and both worktrees are clean.

- [ ] **Step 2: Rehash the closed A8 failure evidence and historical baseline**

Verify these exact hashes before any test edit:

```text
cache receipt       bcd3db50afbcd103e970315ba7d6af468d94e031a2da6322dd36d043a7e8095c
cache stderr        62aed2c689a19d9782caaf514aece8c9094850978d9dff16c6320bfdf67d75a8
failure diagnostic  e3ea21be4671df79267b903f33c78347d5e81c3eb2c8b2f5807eb6a710beeb3b
campaign result     71e3e75cb2756ae274f60b8d7c8ece4d34939fbfd1a48da8fd99f09c7e21e2dd
file manifest       ac090dfd146f86a3f6c2128254a5db860370c9334206554a74d5ea9696173fdc
closure manifest    a804a90c1c8ca508c485ffef9f1b2696eeb90fa34ed103aa50b65e6bd25a24fd
```

Parse `audit/41-campaign-file-manifest.json`, rehash all 48 entries, and require zero missing, size-drifted, or hash-drifted files. Rehash the augmented baseline `83c1833afb2973f08e9b4fbe7a2609ad45a8499deadf01d367e99517364f6ed7` and require 64,090 artifact files, 18 images, 68 root Git records, 68 current Git records, and one approved protected-Git transition.

- [ ] **Step 3: Publish a no-clobber temporary pre-change record**

Use a new timestamped file below `[IO.Path]::GetTempPath()` containing the entry source/specification/plan identities, the complete historical artifact/image arrays, protected Git arrays, the six A8 fixed evidence hashes above, `VAL_DATA_ROOT` presence only, active lease paths, running project-container identities, and Docker image identities. Create with `FileMode.CreateNew`, parse back, and record its SHA-256. Do not write under the repository or artifact root.

---

### Task 2: Add RED coverage for the exact A9 environment and plan identity

**Files:**
- Modify: `tests/gates/test_wave0_a7_launcher.py`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: current A8 launcher/runner behavior and existing real-PowerShell adapters
- Produces: RED tests that fail because the two environment pairs and A9 plan paths are absent

- [ ] **Step 1: Point the protected-plan fixture at the committed A9 plan**

Replace the value of `_COMPATIBILITY_PLAN_PATH` with:

```python
_COMPATIBILITY_PLAN_PATH = (
    "docs/superpowers/plans/2026-08-27-val-wave0-a9-deterministic-hf-download-logging.md"
)
```

Rename `test_production_launcher_binds_the_a8_plan_identity` to `test_launcher_and_runner_bind_the_a9_plan_identity` and assert the exact A9 path occurs in both `_LAUNCHER` and `_RUNNER`; assert the A8 and A7 history-plan paths do not occur in either production identity location.

- [ ] **Step 2: Extend the real cache-preflight test with exact argv assertions**

In `test_model_cache_preflight_is_networked_cpu_only_and_audited`, add:

```python
assert argv[13:17] == [
    "-e",
    "HF_HUB_DISABLE_PROGRESS_BARS=1",
    "-e",
    "HF_HUB_VERBOSITY=error",
]
joined = "\n".join(argv)
for forbidden in (
    "HF_TOKEN",
    "HUGGING_FACE_HUB_TOKEN",
    "HF_HOME",
    "--env-file",
    "--secret",
):
    assert forbidden not in joined
```

Also require `document["docker_argv"] == ["docker", *argv]` and retain the existing no-GPU, network bridge, exact command suffix, empty-stderr, no-clobber, receipt, and hash assertions.

- [ ] **Step 3: Update the closed Task 7 fixture to the desired 33-element audit**

Insert the same two pairs into `model_cache_argv` after `PYTHONPATH=/workspace/src`. Do not change any receipt or model identity fixture.

- [ ] **Step 4: Run RED tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q `
  tests/gates/test_wave0_a7_launcher.py::test_launcher_and_runner_bind_the_a9_plan_identity `
  tests/gates/test_wave0_a7_launcher.py::test_model_cache_preflight_is_networked_cpu_only_and_audited `
  tests/gates/test_wave0_a7_launcher.py::test_task8_accepts_closed_task7_binding_audits
```

Expected: failures identify the old plan path, missing logging environment pairs, and Task 8's obsolete 29-element audit contract. A syntax, fixture, or unrelated failure is not acceptable RED evidence.

---

### Task 3: Make Task 7 construct the deterministic cache-preflight command

**Files:**
- Modify: `scripts/start_wave0_a7.ps1`
- Test: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: `Invoke-A7ModelCachePreflight` and exact A9 plan path
- Produces: a cache-preflight audit whose Docker argv contains the two fixed environment pairs and whose stderr gate remains exact-empty

- [ ] **Step 1: Change both Task 7 plan identity constants to A9**

Set both the protected transition `$PlanPath` and production `$PlanRelativePath` to:

```powershell
'docs/superpowers/plans/2026-08-27-val-wave0-a9-deterministic-hf-download-logging.md'
```

Do not change spec path, Git topology checks, root/current protected inventories, transition count, or source identity logic.

- [ ] **Step 2: Add only the two logging controls to cache preflight**

The exact portion of `$DockerArguments` becomes:

```powershell
'--workdir', '/workspace', '--entrypoint', 'val',
'-e', 'VAL_ARTIFACT_ROOT=/artifacts',
'-e', 'PYTHONPATH=/workspace/src',
'-e', 'HF_HUB_DISABLE_PROGRESS_BARS=1',
'-e', 'HF_HUB_VERBOSITY=error',
'-v', "${Worktree}:/workspace:ro",
'-v', "${PreflightRoot}:/artifacts:rw",
```

Do not add a token, env file, secret, GPU flag, extra network, stderr filtering, retry, or download change.

- [ ] **Step 3: Run the Task 7 RED tests to GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q `
  tests/gates/test_wave0_a7_launcher.py::test_model_cache_preflight_is_networked_cpu_only_and_audited `
  tests/gates/test_wave0_a7_launcher.py::test_launcher_and_runner_bind_the_a9_plan_identity
```

Expected: the cache-preflight test passes; the combined plan-identity test may remain RED only for the runner until Task 4. `test_task8_accepts_closed_task7_binding_audits` must remain RED until Task 4.

---

### Task 4: Make Task 8 validate the exact 33-element audit and A9 plan

**Files:**
- Modify: `scripts/run_wave0_a7.ps1`
- Modify: `tests/gates/test_wave0_a7_launcher.py`

**Interfaces:**
- Consumes: the hash-bound Task 7 `23-a7-model-cache-preflight.json`
- Produces: exact A9 plan lineage and fail-closed validation of the new logging environment

- [ ] **Step 1: Update the Task 8 plan path**

Set `$PlanPath` in `Test-A7ProtectedGitLineage` to the exact A9 plan path used by Task 7.

- [ ] **Step 2: Add mutation coverage before changing the validator**

Create `test_task8_rejects_mutated_hf_logging_environment`, parameterized over `missing`, `extra`, `reordered`, `wrong_progress_value`, `wrong_verbosity_value`, and `token_added`. For each case mutate only `fixture["model_cache_audit_document"]["docker_argv"]`, rewrite the audit, let `_task7_audit_binding_body` bind the recomputed audit hash, invoke real `Test-Task7AuditBinding`, and assert nonzero return code containing `Task 7 model-cache Docker argv binding mismatch`.

Use these mutations:

```python
if mutation == "missing":
    del argv[13:15]
elif mutation == "extra":
    argv[17:17] = ["-e", "HF_HUB_DISABLE_PROGRESS_BARS=1"]
elif mutation == "reordered":
    argv[13:17] = argv[15:17] + argv[13:15]
elif mutation == "wrong_progress_value":
    argv[14] = "HF_HUB_DISABLE_PROGRESS_BARS=0"
elif mutation == "wrong_verbosity_value":
    argv[16] = "HF_HUB_VERBOSITY=warning"
elif mutation == "token_added":
    argv[17:17] = ["-e", "HF_TOKEN=forbidden"]
```

The existing Task 8 validator may already reject these malformed 33-element fixtures because it still accepts only the old 29-element contract. The normative RED signal remains the valid 33-element fixture from Task 2, which must still fail at this point; these mutation cases prevent the GREEN implementation from accepting a merely length-correct or prefix-only command.

- [ ] **Step 3: Replace the model-cache argv index contract**

Require count 33 and these exact positions:

```powershell
$ModelCacheArgv[9]  -ceq '-e'
$ModelCacheArgv[10] -ceq 'VAL_ARTIFACT_ROOT=/artifacts'
$ModelCacheArgv[11] -ceq '-e'
$ModelCacheArgv[12] -ceq 'PYTHONPATH=/workspace/src'
$ModelCacheArgv[13] -ceq '-e'
$ModelCacheArgv[14] -ceq 'HF_HUB_DISABLE_PROGRESS_BARS=1'
$ModelCacheArgv[15] -ceq '-e'
$ModelCacheArgv[16] -ceq 'HF_HUB_VERBOSITY=error'
$ModelCacheArgv[17] -ceq '-v'
$ModelCacheArgv[19] -ceq '-v'
$ModelCacheArgv[21] -ceq [string]$Lease.image_id
```

Validate the workspace mount at index 18, cache-preflight mount at index 20, and the unchanged `assets verify ... --download` suffix at indices 22 through 32. Retain exact zero-byte stderr validation.

- [ ] **Step 4: Run Task 8 tests to GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q `
  tests/gates/test_wave0_a7_launcher.py::test_task8_accepts_closed_task7_binding_audits `
  tests/gates/test_wave0_a7_launcher.py::test_task8_rejects_mutated_hf_logging_environment `
  tests/gates/test_wave0_a7_launcher.py::test_launcher_and_runner_bind_the_a9_plan_identity
```

Expected: all pass; no mutation is accepted.

---

### Task 5: Complete verification, preservation, review, and source commit

**Files:**
- Stage only: `scripts/start_wave0_a7.ps1`, `scripts/run_wave0_a7.ps1`, `tests/gates/test_wave0_a7_launcher.py`
- Historical evidence: read-only

**Interfaces:**
- Consumes: the three-file GREEN candidate and Task 1 pre-change record
- Produces: one reviewed clean source commit eligible for a single A9 attempt

- [ ] **Step 1: Run focused and full deterministic gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/gates/test_wave0_a7_launcher.py -q
uv run pytest -q
uv run black --check tests/gates/test_wave0_a7_launcher.py
uvx --offline ruff check tests/gates/test_wave0_a7_launcher.py
uv lock --check
git diff --check
```

Parse `scripts/start_wave0_a7.ps1` and `scripts/run_wave0_a7.ps1` with both `pwsh` and `powershell`; each parser error array must be empty.

- [ ] **Step 2: Verify exact scope and perform independent review**

```powershell
$Allowed = @(
  'scripts/start_wave0_a7.ps1',
  'scripts/run_wave0_a7.ps1',
  'tests/gates/test_wave0_a7_launcher.py'
)
$Changed = @(git diff --name-only)
if (@(Compare-Object ($Allowed | Sort-Object) ($Changed | Sort-Object)).Count -ne 0) {
  throw 'A9 tracked-file scope drift'
}
git diff --stat
git diff --check
git diff -- $Allowed
```

Review against Section 5.2.13. Critical and Important findings must both equal zero. Confirm exact two preflight variables, no secret propagation, no stderr relaxation, no Task 8 environment inheritance, correct 33-element binding, exact A9 plan path in both scripts, and no retry logic.

- [ ] **Step 3: Rehash immutable history**

Rehash every Task 1 baseline artifact/image and the six fixed A8 evidence files. Require exact sets and zero hash drift. Verify the old shared cache is unchanged, the failed A8 cache has 30 unchanged files, `VAL_DATA_ROOT` is unset, no project container exists, and no active GPU lease exists.

- [ ] **Step 4: Commit only the three reviewed files**

```powershell
git add -- scripts/start_wave0_a7.ps1 scripts/run_wave0_a7.ps1 tests/gates/test_wave0_a7_launcher.py
git -c user.name='kuotunyu' `
    -c user.email='61350295+kuotunyu@users.noreply.github.com' `
    commit -m 'fix: silence Hugging Face cache preflight logs'
git status --short
```

Expected: one append-only implementation commit by `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`, exact three-file scope, clean linked and canonical worktrees.

---

### Task 6: Execute one fresh A9-bound A7 attempt and stop

**Files:**
- Modify: none
- New runtime outputs: one fresh image, run ID, campaign, cache root, and lease lifecycle only

**Interfaces:**
- Consumes: clean reviewed source commit, spec `ffd33555509237ced367898985eaf2433b89ed97`, this plan commit, healthy Linux Docker/RTX 4090, zero active project lease
- Produces: one immutable diagnostic campaign terminating before Wave 1

- [ ] **Step 1: Run the final read-only preflight without repeating earlier implementation tasks**

Require exact branch/HEAD, clean linked/canonical worktrees, matching Git common directory, `desktop-linux`, Linux Docker Server, successful `docker info`, running `docker-desktop` WSL backend, exactly one visible RTX 4090, unset `VAL_DATA_ROOT`, no project container, no active lease, absent candidate image tag, unchanged historical hashes/images, and absent fresh destinations. A failed check creates no run ID or runtime object.

- [ ] **Step 2: Invoke the checked-in launcher exactly once**

```powershell
$SourceCommit = (git rev-parse HEAD).Trim()
$PlanPath = 'docs/superpowers/plans/2026-08-27-val-wave0-a9-deterministic-hf-download-logging.md'
$PlanCommit = (git log -1 --format='%H' -- $PlanPath).Trim()
$OwnerAuthorizationId = 'OWNER-STANDING-A9-20260827-UNATTENDED-01'
pwsh -NoProfile -NonInteractive -File scripts/start_wave0_a7.ps1 `
  -OwnerAuthorizationId $OwnerAuthorizationId `
  -ExpectedSourceCommit $SourceCommit `
  -ExpectedSpecCommit 'ffd33555509237ced367898985eaf2433b89ed97' `
  -ExpectedPlanCommit $PlanCommit `
  -ExpectedBranch 'codex/wave0-model-contract'
$Task7Exit = $LASTEXITCODE
```

`Invoke-A7Production` generates the only run ID immediately before claim. Do not supply a session-side run ID. Do not invoke the launcher a second time regardless of terminal.

- [ ] **Step 3: Preserve and report the terminal**

Hash and validate every new identity, image inspect, cache audit/receipt/log, environment/model-contract receipt, control/instrumented/VJP evidence, aggregate receipt, campaign result/manifest/closure, released lease, and release record that exists. Confirm historical preservation, Git cleanliness, no active lease, no running fresh-image container, RDD untouched, and Wave 1 not started.

The only diagnostic terminals remain:

```text
WAVE0_A7_DIAGNOSTIC_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_NOT_ATTRIBUTED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
WAVE0_A7_DIAGNOSTIC_INCONCLUSIVE / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
```

Any normative failure stops after preserving evidence. No A9/A7 result is a Wave 0 pass or authority to begin Wave 1.
