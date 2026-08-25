# Wave 0 A5 Warning Diagnostics Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Do not dispatch subagents unless the owner explicitly requests them.

**Goal:** Preserve the complete ordered warning inventory whenever the closed A3/A4 backward-warning contract rejects it, then execute exactly one fresh primary-only GPU diagnostic attempt without claiming a Wave 0 pass.

**Architecture:** Add one failure-only canonical JSON formatter inside the existing feasibility probe and test it through the helper and CLI stderr boundary. Keep the successful nine-warning evidence, receipt/schema, parser, operation/category/count allowlist, runner, and all training gates unchanged. After a single append-only implementation commit, build a fresh source-bound image and use a session-side no-clobber harness that stops after primary feasibility-A in every outcome.

**Tech Stack:** Python 3.12.11; uv 0.8.15; pytest 9.0.2; Black 22.6.0; Ruff 0.16.4; PyTorch 2.12.0+cu126; torchvision 0.27.0+cu126; Transformers 5.15.0; CUDA 12.6; Docker Desktop Linux engine; RTX 4090 24 GB; PowerShell 7.

## Global Constraints

- Authoritative specification: `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md` at commit `bca40031056b1e39f4a40cf00541f3be742b64e0`, especially Section 5.2.7.
- Entry branch is `codex/wave0-model-contract`. The implementation-entry HEAD must be the docs-only commit containing this plan; its first parent must be the approved spec commit above, and its only changed path must be this plan.
- Exact implementation allowlist: `src/vision_active_learning_loop/probes/training_feasibility.py` and `tests/probes/test_training_feasibility.py`. Needing a third tracked implementation file is a hard stop.
- Preserve exact warning acceptance: nine `UserWarning` instances, each parsed by the existing `_DETERMINISTIC_WARNING_PATTERN` to `grid_sampler_2d_backward_cuda`, with the existing per-warning parse-before-category order followed by count and operation checks.
- Preserve `python-source-lf-normalized-sha256-v1` and its exact three source digests, strict deterministic-mode restoration, BF16, finite loss/gradients, parameter update, 22 GiB peak-allocation limit, checkpoint round trip, exact/numerical replay fields, atomic no-clobber publication, and all parent/path gates.
- Preserve Python, uv, PyTorch, torchvision, Transformers, SciPy, pycocotools, CUDA, RT-DETR-R18/DINOv2 revisions, 300 queries, four RDD classes, seed 17, formal seeds/budgets, nine pilot fits, 66 primary fits, six label-noise fits, and every research claim.
- Do not modify schemas, receipt validation, `scripts/run_wave0_clean.ps1`, Dockerfiles, configs, `uv.lock`, dependencies, assets, specs, older plans, or historical evidence during implementation.
- Preserve the complete A4 campaign `wave0-a4-20260825T074134919Z`, source `502c0dc8e755a8ba49cf038c8a66ad8a5e6293fd`, image `sha256:be9a8a75065cbc8cc22834dab60bea11932893bb12b4df0092b42caffc734108`, and terminal `WAVE0_A4_NORMATIVE_FAIL / WAVE1_FORBIDDEN` without modification, deletion, reuse, retry, or reinterpretation.
- A5 permits one fresh diagnostic run ID, image, campaign root, primary attempt, checkpoint root, and GPU lease. It never runs feasibility-B, clean-a, clean-b, or aggregate Wave 0.
- A captured A5 diagnostic is failure evidence, not a feasibility receipt or Wave 0 pass. A malformed/missing diagnostic, unexpected feasibility-A pass, or any identity/test/Docker/GPU/evidence failure is inconclusive and cannot be retried under this plan.
- `VAL_DATA_ROOT` remains unset. Do not read, list, mount, download, or access RDD. Wave 1, remote operations, push, merge, tag, Release, and GitHub publication are forbidden.
- Author and committer must be `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`. Do not amend, rebase, reset, squash, or rewrite history.

---

## File Map

| File | Responsibility in A5 |
|---|---|
| `src/vision_active_learning_loop/probes/training_feasibility.py` | Construct the failure-only canonical JSON diagnostic and use it at the four existing post-callback warning rejection points |
| `tests/probes/test_training_feasibility.py` | Prove RED/GREEN diagnostic structure, exact raw inventory, validation order, strict restoration, unchanged success/callback/source behavior, and CLI stderr/no-receipt behavior |

No new module, receipt field, schema version, CLI option, runner parameter, Docker stage, runtime dependency, or research configuration is introduced.

---

### Task 1: Revalidate Entry Identity and Freeze the Historical Baseline

**Files:**
- Read: Git metadata, approved A5 spec, current probe/tests, and preserved Wave 0 evidence
- Modify: none
- Write outside Git: one never-used temporary A5 baseline manifest using atomic `CreateNew`

**Interfaces:**
- Consumes: the registered linked worktree and docs-only A5 plan commit
- Produces: exact entry identities and a pre-change artifact/image hash inventory for Tasks 3 and 5

- [ ] **Step 1: Verify the registered worktree and plan lineage**

Run from the linked worktree discovered through `git worktree list --porcelain`:

```powershell
$ErrorActionPreference = 'Stop'
$A5SpecHead = 'bca40031056b1e39f4a40cf00541f3be742b64e0'
$A5PlanPath = 'docs/superpowers/plans/2026-08-25-val-wave0-a5-warning-diagnostics.md'
$A5PlanHead = git rev-parse HEAD
git worktree list --porcelain
git rev-parse HEAD
git rev-parse HEAD^
git diff-tree --no-commit-id --name-only -r HEAD
git branch --show-current
git rev-parse --git-dir
git rev-parse --git-common-dir
git status --porcelain=v1
git -C '<repo>' status --porcelain=v1
git show -s --format=fuller HEAD
```

Require branch `codex/wave0-model-contract`, `HEAD^ == $A5SpecHead`, the plan commit changes only `$A5PlanPath`, exact author/committer identity, and empty status for the linked worktree and canonical main. Do not repair a mismatch.

- [ ] **Step 2: Reconfirm the A4 evidence trigger and hashes**

Read and hash these exact immutable files:

```powershell
$A4Root = 'D:\vision-active-learning-loop-artifacts\wave0\a4-runs\wave0-a4-20260825T074134919Z'
$A4Expected = [ordered]@{
    'primary\audit\04-feasibility-a.log' = '9357e9976b09d5428861f5912d541af1f082afd96b47d960ca510ebe1576ad3f'
    'primary\audit\04-feasibility-a.json' = 'a3bab1d3dcb4184eedf2ca10dadbee6860e5135d7809fd3bb7a43b2ee90cac36'
    'audit\32-warning-contract-diagnostic.json' = '08070bb1d0f3dc26aae3a2bbd93f3ee28c39ed73c9c5e00ea52d3554a663b17f'
    'audit\40-campaign-failure.json' = '8b3c7ea82020947d43a3d7e4313fa3993f4b21d189a0ceca349b1b173588d791'
    'audit\41-failure-evidence-manifest.json' = 'eeae9c620251bfcfcfebc6246518f75b1efc8ef6302d0e60550be7454e642fd8'
    'audit\50-historical-preservation.json' = '19723276ed0d3dc8e818f78077a9fccb5566a1a67bbdc6cb05ff8bebae665ebf'
    'audit\51-campaign-closure-manifest.json' = '471bafcf0dcc5ec37b39585393ddaa147a567960e38f9ffc23e6df4cd14c3186'
}
foreach ($RelativePath in $A4Expected.Keys) {
    $Actual = (Get-FileHash -Algorithm SHA256 -LiteralPath (
        Join-Path $A4Root $RelativePath
    )).Hash.ToLowerInvariant()
    if ($Actual -ne $A4Expected[$RelativePath]) {
        throw "A4 evidence drift: $RelativePath"
    }
}
```

Require the stage log to end in `unparsable deterministic backward warning`, no feasibility receipt/checkpoint, and the closure terminal above.

- [ ] **Step 3: Create the immutable pre-change inventory**

Set a never-used temporary path keyed by `$A5PlanHead`. Inventory every existing file below `D:\vision-active-learning-loop-artifacts\wave0`, every current `vision-active-learning-loop:wave0-*` tag-to-image-ID pair, and these protected Git paths:

```text
schemas/
scripts/run_wave0_clean.ps1
docker/wave0.Dockerfile
configs/
uv.lock
docs/superpowers/specs/
docs/superpowers/plans/
```

Exclude only the plan file itself from protected Git comparison and do not exclude any historical artifact path. Use this exact session-side inventory and atomic writer:

```powershell
function Write-A5NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Encoding = [System.Text.UTF8Encoding]::new($false)
    $Stream = [System.IO.FileStream]::new(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $Writer = [System.IO.StreamWriter]::new($Stream, $Encoding)
        try { $Writer.Write($Text) } finally { $Writer.Dispose() }
    } finally {
        if ($Stream.CanWrite) { $Stream.Dispose() }
    }
}

$A5TemporaryRoot = Join-Path (
    [System.IO.Path]::GetTempPath()
) "vision-active-learning-loop-a5-$A5PlanHead"
if (Test-Path -LiteralPath $A5TemporaryRoot) {
    throw "A5 temporary baseline root already exists: $A5TemporaryRoot"
}
[System.IO.Directory]::CreateDirectory($A5TemporaryRoot) | Out-Null
$A5BaselinePath = Join-Path $A5TemporaryRoot 'baseline.json'
$WaveEvidenceRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
$ArtifactFiles = @(Get-ChildItem -LiteralPath $WaveEvidenceRoot -File -Force -Recurse |
    Sort-Object FullName |
    ForEach-Object {
        [ordered]@{
            path = $_.FullName
            size = [long]$_.Length
            attributes = $_.Attributes.ToString()
            sha256 = ((Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant())
        }
    })
$ImageTags = @(docker image ls --format '{{.Repository}}:{{.Tag}}' |
    Where-Object { $_ -like 'vision-active-learning-loop:wave0-*' } |
    Sort-Object -Unique)
$Images = @($ImageTags | ForEach-Object {
    [ordered]@{
        tag = $_
        image_id = (docker image inspect --format '{{.Id}}' $_).Trim()
    }
})
$ProtectedPaths = @(git ls-files -- `
    'schemas/**' `
    'scripts/run_wave0_clean.ps1' `
    'docker/wave0.Dockerfile' `
    'configs/**' `
    'uv.lock' `
    'docs/superpowers/specs/**' `
    'docs/superpowers/plans/**' |
    Where-Object { $_ -ne $A5PlanPath } |
    Sort-Object -Unique)
$ProtectedFiles = @($ProtectedPaths | ForEach-Object {
    [ordered]@{
        path = $_
        size = [long](Get-Item -LiteralPath $_).Length
        sha256 = ((Get-FileHash -Algorithm SHA256 -LiteralPath $_).Hash.ToLowerInvariant())
    }
})
$Baseline = [ordered]@{
    schema_version = 1
    plan_head = $A5PlanHead
    artifact_files = $ArtifactFiles
    images = $Images
    protected_files = $ProtectedFiles
}
Write-A5NewText -Path $A5BaselinePath -Text (
    ($Baseline | ConvertTo-Json -Depth 8 -Compress) + "`n"
)
```

Require every native command exit code 0 and record `$A5BaselinePath` in the execution notes. Do not overwrite an existing baseline. The later A5 campaign root does not yet exist and therefore needs no wildcard exclusion.

**Stop condition:** Any identity, lineage, hash, terminal, Git cleanliness, or author mismatch.

---

### Task 2: Add Failure-Only Warning Diagnostics With TDD

**Files:**
- Modify: `tests/probes/test_training_feasibility.py`
- Modify: `src/vision_active_learning_loop/probes/training_feasibility.py`

**Interfaces:**
- Consumes: `FeasibilityError`, `run_allowlisted_backward()`, `main()`, `json`, ordered `raw_warnings`, and ordered `warning_categories`
- Produces: `_WARNING_CONTRACT_DIAGNOSTIC_PREFIX: str` and `_warning_contract_error(reason: str, raw_warnings: tuple[str, ...], warning_categories: tuple[str, ...]) -> FeasibilityError`

- [ ] **Step 1: Add a test-only diagnostic decoder**

In `tests/probes/test_training_feasibility.py`, add:

```python
WARNING_DIAGNOSTIC_PREFIX = (
    "deterministic backward warning contract failure; diagnostic="
)


def _warning_diagnostic(error: BaseException) -> dict[str, object]:
    text = str(error)
    assert text.startswith(WARNING_DIAGNOSTIC_PREFIX)
    document = json.loads(text.removeprefix(WARNING_DIAGNOSTIC_PREFIX))
    assert set(document) == {"reason", "schema_version", "warnings"}
    assert document["schema_version"] == 1
    return document
```

- [ ] **Step 2: Convert the inventory-drift test into the RED contract**

Change the existing parameter table's final field from prose fragments to exact reason codes:

```python
"count_mismatch"
"unexpected_operation"
"unparsable_message"
"unexpected_category"
```

Capture `pytest.raises(FeasibilityError)` without a regex, decode it with `_warning_diagnostic()`, and assert:

```python
assert diagnostic["reason"] == expected_reason
assert diagnostic["warnings"] == [
    {"category": category.__name__, "index": index, "message": message}
    for index, message in enumerate(messages)
]
```

Keep the three strict deterministic-mode restoration assertions after every failure.

- [ ] **Step 3: Add RED coverage for complete JSON escaping and order**

Add a nine-warning unexpected-operation case whose final raw message contains quotes, a backslash, a newline, and non-ASCII text:

```python
def test_warning_diagnostic_preserves_complete_special_character_inventory() -> None:
    configure_determinism(seed=17)
    special = (
        'other_backward_cuda does not have a deterministic implementation, '
        'details="quoted"\\path\n雪'
    )
    messages = (GRID_WARNING,) * 8 + (special,)

    with pytest.raises(FeasibilityError) as caught:
        feasibility_probe.run_allowlisted_backward(
            lambda: _emit_warning_messages(messages), expected_count=9
        )

    diagnostic = _warning_diagnostic(caught.value)
    assert diagnostic == {
        "reason": "unexpected_operation",
        "schema_version": 1,
        "warnings": [
            {"category": "UserWarning", "index": index, "message": message}
            for index, message in enumerate(messages)
        ],
    }
    expected_json = json.dumps(
        diagnostic, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    assert str(caught.value) == WARNING_DIAGNOSTIC_PREFIX + expected_json
```

- [ ] **Step 4: Add the RED CLI stderr/no-receipt boundary**

Monkeypatch `resolve_cli_paths()` to return temporary model/checkpoint/output paths and `_execute_probe()` to invoke one unparsable warning through `run_allowlisted_backward()`. Assert exit code 2, exactly one canonical diagnostic in stderr, no traceback, and `output.exists() is False`. The checkpoint root may be created by the existing CLI before `_execute_probe()` and must remain a fresh empty diagnostic root.

- [ ] **Step 5: Run RED and confirm the intended failures**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'allowlisted_backward_rejects_every_inventory_drift or warning_diagnostic or cli_reports_warning_diagnostic'
```

Require failure because the current four generic errors contain no prefix/JSON inventory. A collection error, source-hash failure, strict-mode failure, or unrelated fixture failure is a hard stop.

- [ ] **Step 6: Implement the minimal canonical formatter**

In `src/vision_active_learning_loop/probes/training_feasibility.py`, add near the warning constants:

```python
_WARNING_CONTRACT_DIAGNOSTIC_PREFIX = (
    "deterministic backward warning contract failure; diagnostic="
)
_WARNING_CONTRACT_DIAGNOSTIC_REASONS = frozenset(
    {
        "unparsable_message",
        "unexpected_category",
        "count_mismatch",
        "unexpected_operation",
    }
)
```

Add the formatter immediately before `run_allowlisted_backward()`:

```python
def _warning_contract_error(
    reason: str,
    raw_warnings: tuple[str, ...],
    warning_categories: tuple[str, ...],
) -> FeasibilityError:
    if reason not in _WARNING_CONTRACT_DIAGNOSTIC_REASONS:
        raise ValueError("unknown warning diagnostic reason")
    warning_inventory = [
        {"category": category, "index": index, "message": message}
        for index, (message, category) in enumerate(
            zip(raw_warnings, warning_categories, strict=True)
        )
    ]
    diagnostic = {
        "reason": reason,
        "schema_version": 1,
        "warnings": warning_inventory,
    }
    encoded = json.dumps(
        diagnostic, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    )
    return FeasibilityError(_WARNING_CONTRACT_DIAGNOSTIC_PREFIX + encoded)
```

- [ ] **Step 7: Replace only the four post-callback generic errors**

Keep the current loop and validation order. Replace the four raises with:

```python
raise _warning_contract_error(
    "unparsable_message", raw_warnings, warning_categories
)
raise _warning_contract_error(
    "unexpected_category", raw_warnings, warning_categories
)
raise _warning_contract_error("count_mismatch", raw_warnings, warning_categories)
raise _warning_contract_error(
    "unexpected_operation", raw_warnings, warning_categories
)
```

Do not change `_DETERMINISTIC_WARNING_PATTERN`, `_ALLOWLISTED_BACKWARD_OPERATION`, `expected_count`, warning capture, strict-mode `finally`, success evidence, source verification, callback exceptions, receipt construction, or CLI exception handling.

- [ ] **Step 8: Run GREEN and retained-boundary tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests/probes/test_training_feasibility.py -v `
  -k 'allowlisted_backward or warning_diagnostic or cli_reports_warning_diagnostic or source_hash'
uv run pytest tests/probes/test_training_feasibility.py -q
```

Require zero failures. Confirm the exact nine-warning path still returns the same `BackwardWarningEvidence`; invalid entry, callback exception, source inventory/hash/link failures retain their old non-diagnostic errors; and no diagnostic failure publishes a receipt.

**Stop condition:** Any need for a third tracked file, parser/allowlist/count/category change, receipt/schema change, altered callback error, or success-path evidence change.

---

### Task 3: Verify, Review, and Commit the A5 Candidate

**Files:**
- Verify: exactly the two implementation files
- Modify: no file outside the two-file allowlist

**Interfaces:**
- Consumes: Task 2 GREEN worktree and Task 1 baseline inventory
- Produces: one clean append-only A5 source candidate commit

- [ ] **Step 1: Run the complete CPU and quality gates**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest tests -q
uv run --with black==22.6.0 black --check `
  src/vision_active_learning_loop/probes/training_feasibility.py `
  tests/probes/test_training_feasibility.py
uv run --with ruff==0.16.4 ruff check `
  src/vision_active_learning_loop/probes/training_feasibility.py `
  tests/probes/test_training_feasibility.py
uv lock --check
git diff --check
```

Require zero failures. Capability skips must remain explained and cannot cover A5 behavior.

- [ ] **Step 2: Perform the required fresh second-pass review**

Review the complete diff against Section 5.2.7 and record Critical, Important, and Minor findings. Critical and Important must both be zero. Inspect exactly:

```text
prefix and four reason codes
compact ensure_ascii/sort_keys/separators serialization
complete ordered message/category inventory with zero-based indexes
per-item parse-before-category, then count, then operation order
strict mode restored before validation errors or callback errors escape
source/entry/callback failures remain non-diagnostic
exact nine-warning success evidence unchanged
CLI emits stderr without traceback or receipt publication
no receipt/schema/runner/config/dependency/research change
```

Any correction reruns the focused tests and every Step 1 gate.

- [ ] **Step 3: Verify scope and historical preservation**

Require `git diff --name-only` to equal exactly:

```text
src/vision_active_learning_loop/probes/training_feasibility.py
tests/probes/test_training_feasibility.py
```

Compare every Task 1 historical artifact/image/protected-file record. For protected Git paths, allow only the current plan commit plus the two implementation paths; require every other blob unchanged. Require `uv.lock`, schema, receipt validator, runner, Dockerfile, configs, spec, older plans, and every prior campaign/image/evidence object unchanged.

- [ ] **Step 4: Create one append-only implementation commit**

```powershell
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git add -- `
  src/vision_active_learning_loop/probes/training_feasibility.py `
  tests/probes/test_training_feasibility.py
git diff --cached --check
git commit -m 'fix: preserve Wave 0 warning diagnostics'
```

- [ ] **Step 5: Verify the committed candidate freshly**

Repeat the focused tests, run `git diff HEAD^ HEAD --check`, inspect exact author/committer and the two-file commit inventory, and require both linked worktree and canonical main clean. The resulting full SHA is the sole A5 candidate.

**Stop condition:** Any failed gate, unresolved Critical/Important finding, evidence drift, extra tracked file, dirty worktree, or identity mismatch.

---

### Task 4: Build and Preflight One Fresh A5 Diagnostic Campaign

**Files:**
- Execute unchanged: `docker/wave0.Dockerfile` and the current `val` CLI
- Write externally: one new no-clobber A5 campaign/audit root and later one GPU lease
- Modify in Git: none

**Interfaces:**
- Consumes: the clean A5 candidate SHA
- Produces: one fresh source-bound OCI image and a CPU-only proof of the A5 diagnostic contract

- [ ] **Step 1: Revalidate the execution boundary**

Require exact candidate/branch/worktree/common-dir/clean identities; `VAL_DATA_ROOT` unset; Docker context `desktop-linux`; `docker version` with Linux Server; `docker info` success; `docker-desktop` WSL Running; exact historical Option A image ID `sha256:558a468b2bcb1a96a9198fb35a1590e57c376e5a7e6ac5032b3cdff44bbaacc9`; exact A4 image ID above; no active project GPU lease; and unchanged Task 1 evidence hashes. Do not restart Docker, change context, or repair Git under this plan.

- [ ] **Step 2: Create fresh identities and build once**

Generate the identities, roots, and image with this no-clobber sequence:

```powershell
function Write-A5NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Encoding = [System.Text.UTF8Encoding]::new($false)
    $Stream = [System.IO.FileStream]::new(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $Writer = [System.IO.StreamWriter]::new($Stream, $Encoding)
        try { $Writer.Write($Text) } finally { $Writer.Dispose() }
    } finally {
        if ($Stream.CanWrite) { $Stream.Dispose() }
    }
}

$A5CandidateSha = (git rev-parse HEAD).Trim()
$A5RunId = 'wave0-a5-' + [DateTimeOffset]::UtcNow.ToString(
    'yyyyMMddTHHmmssfffZ'
)
$A5RunsRoot = 'D:\vision-active-learning-loop-artifacts\wave0\a5-runs'
if (-not (Test-Path -LiteralPath $A5RunsRoot -PathType Container)) {
    $null = New-Item -ItemType Directory -Path $A5RunsRoot -ErrorAction Stop
}
$A5CampaignRoot = Join-Path $A5RunsRoot $A5RunId
if (Test-Path -LiteralPath $A5CampaignRoot) {
    throw "A5 campaign root already exists: $A5CampaignRoot"
}
$null = New-Item -ItemType Directory -Path $A5CampaignRoot -ErrorAction Stop
$A5AuditRoot = New-Item -ItemType Directory -Path (
    Join-Path $A5CampaignRoot 'audit'
) -ErrorAction Stop
$A5ImageTag = (
    'vision-active-learning-loop:wave0-a5-' +
    $A5CandidateSha.Substring(0, 12) + '-' + $A5RunId.ToLowerInvariant()
)
& docker image inspect $A5ImageTag *> $null
if ($LASTEXITCODE -eq 0) {
    throw "A5 image tag already exists: $A5ImageTag"
}
$A5BaseDigest = `
    'sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356'
$A5BuildArgs = @(
    'build', '--no-cache',
    '--file', 'docker/wave0.Dockerfile',
    '--label', "org.opencontainers.image.revision=$A5CandidateSha",
    '--label', "org.opencontainers.image.ref.name=$A5RunId",
    '--label', "org.opencontainers.image.base.digest=$A5BaseDigest",
    '--tag', $A5ImageTag,
    '.'
)
$A5BuildStarted = [DateTimeOffset]::UtcNow
$A5BuildItems = @(& docker @A5BuildArgs 2>&1)
$A5BuildExit = [int]$LASTEXITCODE
$A5BuildFinished = [DateTimeOffset]::UtcNow
$A5BuildText = if ($A5BuildItems.Count -eq 0) {
    ''
} else {
    (($A5BuildItems | ForEach-Object { $_.ToString() }) -join `
        [Environment]::NewLine) + [Environment]::NewLine
}
Write-A5NewText -Path (Join-Path $A5AuditRoot.FullName '20-image-build.log') `
    -Text $A5BuildText
$A5BuildResult = [ordered]@{
    schema_version = 1
    run_id = $A5RunId
    source_sha = $A5CandidateSha
    image_tag = $A5ImageTag
    argv = @('docker') + $A5BuildArgs
    exit_code = $A5BuildExit
    started_at = $A5BuildStarted.ToString('o')
    finished_at = $A5BuildFinished.ToString('o')
}
Write-A5NewText -Path (
    Join-Path $A5AuditRoot.FullName '20-image-build-result.json'
) -Text (($A5BuildResult | ConvertTo-Json -Depth 6 -Compress) + "`n")
if ($A5BuildExit -ne 0) {
    throw "A5 image build failed: $A5BuildExit"
}
$A5InspectItems = @(& docker image inspect $A5ImageTag 2>&1)
$A5InspectExit = [int]$LASTEXITCODE
$A5InspectText = ($A5InspectItems | ForEach-Object { $_.ToString() }) -join `
    [Environment]::NewLine
Write-A5NewText -Path (
    Join-Path $A5AuditRoot.FullName '21-image-inspect.json'
) -Text ($A5InspectText + [Environment]::NewLine)
if ($A5InspectExit -ne 0) {
    throw "A5 image inspect failed: $A5InspectExit"
}
$A5Inspect = $A5InspectText | ConvertFrom-Json
$A5ImageId = [string]$A5Inspect[0].Id
if ($A5Inspect[0].Config.Labels.'org.opencontainers.image.revision' -ne
        $A5CandidateSha -or
    $A5Inspect[0].Config.Labels.'org.opencontainers.image.ref.name' -ne
        $A5RunId -or
    $A5Inspect[0].Config.Labels.'org.opencontainers.image.base.digest' -ne
        $A5BaseDigest) {
    throw 'A5 OCI label identity mismatch'
}
```

The labels must be exactly:

```text
org.opencontainers.image.revision=<full A5 candidate SHA>
org.opencontainers.image.ref.name=<new A5 run ID>
org.opencontainers.image.base.digest=sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356
```

Atomically preserve the build log/result and exact `docker image inspect` identity. Any build or identity failure closes the new campaign inconclusive without a rebuild.

- [ ] **Step 3: Run the CPU-only diagnostic micro-check before the GPU lease**

Run the fresh image without GPU, network, host mount, or model forward. Use the following micro-check source and command:

```powershell
$A5MicrocheckCode = @'
import json
import warnings

import torch

from vision_active_learning_loop.probes.training_feasibility import (
    FeasibilityError,
    configure_determinism,
    run_allowlisted_backward,
)

prefix = "deterministic backward warning contract failure; diagnostic="
message = "diagnostic warning without an operation identifier"
configure_determinism(seed=17)
try:
    run_allowlisted_backward(
        lambda: warnings.warn(message, UserWarning, stacklevel=2),
        expected_count=9,
    )
except FeasibilityError as error:
    text = str(error)
else:
    raise AssertionError("diagnostic failure was not raised")
if not text.startswith(prefix):
    raise AssertionError(text)
diagnostic = json.loads(text.removeprefix(prefix))
expected = {
    "reason": "unparsable_message",
    "schema_version": 1,
    "warnings": [
        {"category": "UserWarning", "index": 0, "message": message}
    ],
}
if diagnostic != expected:
    raise AssertionError(diagnostic)
if not torch.are_deterministic_algorithms_enabled():
    raise AssertionError("deterministic algorithms disabled")
if torch.is_deterministic_algorithms_warn_only_enabled():
    raise AssertionError("warning mode not restored")
if torch.get_deterministic_debug_mode() != 2:
    raise AssertionError("error mode not restored")
print(json.dumps(diagnostic, ensure_ascii=True, sort_keys=True, separators=(",", ":")))
'@
$A5MicrocheckStarted = [DateTimeOffset]::UtcNow
$A5MicrocheckItems = @(& docker run --rm --network none `
    --entrypoint /opt/val/.venv/bin/python `
    $A5ImageTag -c $A5MicrocheckCode 2>&1)
$A5MicrocheckExit = $LASTEXITCODE
$A5MicrocheckFinished = [DateTimeOffset]::UtcNow
$A5MicrocheckText = if ($A5MicrocheckItems.Count -eq 0) {
    ''
} else {
    (($A5MicrocheckItems | ForEach-Object { $_.ToString() }) -join `
        [Environment]::NewLine) + [Environment]::NewLine
}
Write-A5NewText -Path (Join-Path $A5AuditRoot '22-diagnostic-microcheck.log') `
    -Text $A5MicrocheckText
$A5MicrocheckRecord = [ordered]@{
    schema_version = 1
    run_id = $A5RunId
    source_sha = $A5CandidateSha
    image_tag = $A5ImageTag
    image_id = $A5ImageId
    network = 'none'
    gpu_requested = $false
    model_forward_performed = $false
    exit_code = [int]$A5MicrocheckExit
    started_at = $A5MicrocheckStarted.ToString('o')
    finished_at = $A5MicrocheckFinished.ToString('o')
    log_sha256 = if (Test-Path -LiteralPath (
        Join-Path $A5AuditRoot '22-diagnostic-microcheck.log'
    )) {
        ((Get-FileHash -Algorithm SHA256 -LiteralPath (
            Join-Path $A5AuditRoot '22-diagnostic-microcheck.log'
        )).Hash.ToLowerInvariant())
    } else {
        $null
    }
}
Write-A5NewText -Path (
    Join-Path $A5AuditRoot '22-diagnostic-microcheck.json'
) -Text (($A5MicrocheckRecord | ConvertTo-Json -Depth 6 -Compress) + "`n")
if ($A5MicrocheckExit -ne 0) {
    throw "A5 diagnostic micro-check failed: $A5MicrocheckExit"
}
```

The decoded output must equal:

```python
diagnostic == {
    "reason": "unparsable_message",
    "schema_version": 1,
    "warnings": [
        {
            "category": "UserWarning",
            "index": 0,
            "message": "diagnostic warning without an operation identifier",
        }
    ],
}
```

Also assert strict deterministic error mode is restored. Preserve command, stdout/stderr, exit code, source/image/run identities, and hashes with atomic no-clobber audit files. Failure stops before lease acquisition.

**Stop condition:** Any Docker/source/image/micro-check/history/identity failure or pre-existing destination.

---

### Task 5: Execute Primary Through Feasibility-A Once and Close

**Files:**
- Execute unchanged: current `val environment check`, `val assets verify`, `val probe model-contract`, and `val probe training-feasibility`
- Do not execute: `scripts/run_wave0_clean.ps1`, feasibility-B, clean attempts, or aggregate gate
- Write externally: the fresh primary attempt, stage audit logs/records, diagnostic closure, preservation manifest, and released lease
- Modify in Git: none

**Interfaces:**
- Consumes: Task 4 campaign/image and an exclusive RTX 4090 lease
- Produces: exactly one immutable `DIAGNOSTIC_CAPTURED` or `DIAGNOSTIC_INCONCLUSIVE` A5 campaign

- [ ] **Step 1: Acquire the exclusive RTX 4090 lease**

Use the approved collector with the CUDA image entrypoint overridden:

```powershell
docker run --rm --gpus all --network none --entrypoint nvidia-smi `
  nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356 `
  --query-gpu=uuid,name,memory.total,memory.used,memory.free `
  --format=csv,noheader,nounits
```

Require exactly one CSV row for the RTX 4090 and no numeric compute process. Atomically create `D:\vision-active-learning-loop-artifacts\wave0\leases\<RUN_ID>` and its acquisition record. If busy or unavailable, preserve the campaign and stop without CPU fallback.

- [ ] **Step 2: Create a primary-only no-clobber stage harness in the PowerShell session**

Do not write the harness into the repository. It must:

```text
use FileMode.CreateNew for every audit log/record
allow an empty captured log
merge native stdout/stderr without losing ErrorRecord text
record argv, exit code, timestamps, network, source/image/run identity,
receipt hash when present, checkpoint inventory, and attempt disk bytes
mount the linked worktree read-only and the fresh primary root read-write
set VAL_ARTIFACT_ROOT=/artifacts, PYTHONPATH=/workspace/src,
UV_CACHE_DIR=/artifacts/wave0/uv_cache, CUBLAS_WORKSPACE_CONFIG=:4096:8
set HF_HUB_OFFLINE=1 and TRANSFORMERS_OFFLINE=1 for network-none stages
never read or set VAL_DATA_ROOT
```

Define the session harness exactly as follows; `Write-A5NewText` is repeated here so this task is executable independently:

```powershell
function Write-A5NewText {
    param(
        [Parameter(Mandatory = $true)][string]$Path,
        [Parameter(Mandatory = $true)][AllowEmptyString()][string]$Text
    )
    $Encoding = [System.Text.UTF8Encoding]::new($false)
    $Stream = [System.IO.FileStream]::new(
        $Path,
        [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write,
        [System.IO.FileShare]::None
    )
    try {
        $Writer = [System.IO.StreamWriter]::new($Stream, $Encoding)
        try { $Writer.Write($Text) } finally { $Writer.Dispose() }
    } finally {
        if ($Stream.CanWrite) { $Stream.Dispose() }
    }
}

function Invoke-A5NativeCapture {
    param(
        [Parameter(Mandatory = $true)][string]$FilePath,
        [Parameter(Mandatory = $true)][string[]]$ArgumentList
    )
    $Application = Get-Command -Name $FilePath -CommandType Application `
        -ErrorAction Stop | Select-Object -First 1
    $PreviousPreference = $ErrorActionPreference
    try {
        $ErrorActionPreference = 'Continue'
        $Items = @(& $Application.Source @ArgumentList 2>&1)
        $ExitCode = [int]$LASTEXITCODE
    } finally {
        $ErrorActionPreference = $PreviousPreference
    }
    $Lines = @($Items | ForEach-Object {
        if ($_ -is [System.Management.Automation.ErrorRecord]) {
            $_.Exception.Message
        } else {
            $_.ToString()
        }
    })
    $Text = if ($Lines.Count -eq 0) {
        ''
    } else {
        ($Lines -join [Environment]::NewLine) + [Environment]::NewLine
    }
    [pscustomobject]@{ exit_code = $ExitCode; text = $Text }
}

$A5Worktree = (git rev-parse --show-toplevel).Trim()
$A5AttemptRoot = Join-Path $A5CampaignRoot 'primary'
if (Test-Path -LiteralPath $A5AttemptRoot) {
    throw "A5 primary root already exists: $A5AttemptRoot"
}
$A5AttemptDirectory = New-Item -ItemType Directory -Path $A5AttemptRoot `
    -ErrorAction Stop
$A5AttemptRoot = $A5AttemptDirectory.FullName
$A5WaveRoot = New-Item -ItemType Directory -Path (
    Join-Path $A5AttemptRoot 'wave0'
) -ErrorAction Stop
$A5ReceiptsRoot = New-Item -ItemType Directory -Path (
    Join-Path $A5WaveRoot.FullName 'receipts'
) -ErrorAction Stop
$A5CheckpointsRoot = New-Item -ItemType Directory -Path (
    Join-Path $A5WaveRoot.FullName 'checkpoints'
) -ErrorAction Stop
$null = New-Item -ItemType Directory -Path (
    Join-Path $A5WaveRoot.FullName 'model_cache'
) -ErrorAction Stop
$null = New-Item -ItemType Directory -Path (
    Join-Path $A5WaveRoot.FullName 'uv_cache'
) -ErrorAction Stop
$A5AttemptAuditRoot = New-Item -ItemType Directory -Path (
    Join-Path $A5AttemptRoot 'audit'
) -ErrorAction Stop

function Invoke-A5Stage {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][ValidateSet('none', 'bridge')]
        [string]$Network,
        [Parameter(Mandatory = $true)][string[]]$Command,
        [Parameter(Mandatory = $true)][string]$Receipt,
        [switch]$RequirePassReceipt
    )
    $LogPath = Join-Path $A5AttemptAuditRoot.FullName "$Name.log"
    $RecordPath = Join-Path $A5AttemptAuditRoot.FullName "$Name.json"
    $ReceiptPath = Join-Path $A5ReceiptsRoot.FullName $Receipt
    if ((Test-Path -LiteralPath $LogPath) -or
        (Test-Path -LiteralPath $RecordPath)) {
        throw "A5 audit destination already exists for $Name"
    }
    $DockerArgs = @(
        'run', '--rm', '--gpus', 'all', '--network', $Network,
        '--workdir', '/workspace', '--entrypoint', 'val',
        '-e', 'VAL_ARTIFACT_ROOT=/artifacts',
        '-e', "VAL_OBSERVED_BASE_IMAGE_DIGEST=$A5BaseDigest",
        '-e', "VAL_RUNTIME_IMAGE_DIGEST=$A5ImageId",
        '-e', 'PYTHONPATH=/workspace/src',
        '-e', 'UV_CACHE_DIR=/artifacts/wave0/uv_cache',
        '-e', 'CUBLAS_WORKSPACE_CONFIG=:4096:8',
        '-v', "${A5Worktree}:/workspace:ro",
        '-v', "${A5AttemptRoot}:/artifacts:rw"
    )
    if ($Network -eq 'none') {
        $DockerArgs += @(
            '-e', 'HF_HUB_OFFLINE=1',
            '-e', 'TRANSFORMERS_OFFLINE=1'
        )
    }
    $DockerArgs += @($A5ImageTag)
    $DockerArgs += $Command
    $Started = [DateTimeOffset]::UtcNow
    $Native = Invoke-A5NativeCapture -FilePath 'docker' `
        -ArgumentList $DockerArgs
    $Finished = [DateTimeOffset]::UtcNow
    Write-A5NewText -Path $LogPath -Text $Native.text
    $ReceiptHash = if (Test-Path -LiteralPath $ReceiptPath -PathType Leaf) {
        ((Get-FileHash -Algorithm SHA256 -LiteralPath $ReceiptPath).Hash.ToLowerInvariant())
    } else {
        $null
    }
    $CheckpointFiles = @(Get-ChildItem -LiteralPath `
        $A5CheckpointsRoot.FullName -File -Recurse)
    $CheckpointInventory = @($CheckpointFiles | Sort-Object FullName |
        ForEach-Object {
            [ordered]@{
                path = $_.FullName.Substring($A5AttemptRoot.Length + 1).Replace('\', '/')
                size = [long]$_.Length
                sha256 = ((Get-FileHash -Algorithm SHA256 `
                    -LiteralPath $_.FullName).Hash.ToLowerInvariant())
            }
        })
    $AttemptBytes = [long]((Get-ChildItem -LiteralPath $A5AttemptRoot `
        -File -Recurse | Measure-Object -Property Length -Sum).Sum)
    $Record = [ordered]@{
        schema_version = 1
        run_id = $A5RunId
        attempt_id = 'primary'
        stage = $Name
        argv = @('docker') + $DockerArgs
        exit_code = [int]$Native.exit_code
        started_at = $Started.ToString('o')
        finished_at = $Finished.ToString('o')
        runtime_seconds = ($Finished - $Started).TotalSeconds
        source_sha = $A5CandidateSha
        image_tag = $A5ImageTag
        image_digest = $A5ImageId
        network = $Network
        val_data_root_unset = -not (Test-Path Env:VAL_DATA_ROOT)
        receipt = $Receipt
        receipt_sha256 = $ReceiptHash
        checkpoint_files = $CheckpointInventory
        attempt_disk_bytes = $AttemptBytes
    }
    Write-A5NewText -Path $RecordPath -Text (
        ($Record | ConvertTo-Json -Depth 10 -Compress) + "`n"
    )
    if ($RequirePassReceipt) {
        if ($Native.exit_code -ne 0) {
            throw "A5 stage $Name failed with exit code $($Native.exit_code)"
        }
        if (-not (Test-Path -LiteralPath $ReceiptPath -PathType Leaf)) {
            throw "A5 stage $Name did not publish $Receipt"
        }
    }
    [pscustomobject]@{
        exit_code = [int]$Native.exit_code
        log_path = $LogPath
        record_path = $RecordPath
        receipt_path = $ReceiptPath
    }
}
```

Before invoking the harness, set `$A5RunId`, `$A5CampaignRoot`, `$A5CandidateSha`, `$A5ImageTag`, `$A5ImageId`, and `$A5BaseDigest` from the verified Task 4 records. Create exactly these fresh primary directories: `wave0/receipts`, `wave0/checkpoints`, `wave0/model_cache`, `wave0/uv_cache`, and `audit`. Require the `feasibility-a` checkpoint root and output receipt absent before stage 4.

- [ ] **Step 3: Execute only the four authorized stages**

Invoke the fresh image with exactly these four calls:

```powershell
$null = Invoke-A5Stage -Name '01-environment' -Network 'none' `
    -Receipt 'environment.json' -RequirePassReceipt -Command @(
        'environment', 'check',
        '--config', '/workspace/configs/environment/wave0.yaml',
        '--run-id', $A5RunId,
        '--output', '/artifacts/wave0/receipts/environment.json'
    )
$null = Invoke-A5Stage -Name '02-model-assets' -Network 'bridge' `
    -Receipt 'model-assets.json' -RequirePassReceipt -Command @(
        'assets', 'verify',
        '--config', '/workspace/configs/models/pinned-models.yaml',
        '--cache-root', '/artifacts/wave0/model_cache',
        '--output', '/artifacts/wave0/receipts/model-assets.json',
        '--run-id', $A5RunId,
        '--download'
    )
$null = Invoke-A5Stage -Name '03-model-contract' -Network 'none' `
    -Receipt 'model-contract.json' -RequirePassReceipt -Command @(
        'probe', 'model-contract',
        '--assets', '/artifacts/wave0/receipts/model-assets.json',
        '--environment', '/artifacts/wave0/receipts/environment.json',
        '--fixtures', '/workspace/fixtures/synthetic/wave0/fixture-manifest.json',
        '--run-id', $A5RunId,
        '--output', '/artifacts/wave0/receipts/model-contract.json'
    )
$A5FeasibilityCheckpoint = Join-Path `
    $A5CheckpointsRoot.FullName 'feasibility-a'
$A5FeasibilityReceipt = Join-Path `
    $A5ReceiptsRoot.FullName 'feasibility-a.json'
if ((Test-Path -LiteralPath $A5FeasibilityCheckpoint) -or
    (Test-Path -LiteralPath $A5FeasibilityReceipt)) {
    throw 'A5 feasibility destination is not fresh'
}
$A5Stage4 = Invoke-A5Stage -Name '04-feasibility-a' -Network 'none' `
    -Receipt 'feasibility-a.json' -Command @(
        'probe', 'training-feasibility',
        '--model-contract', '/artifacts/wave0/receipts/model-contract.json',
        '--checkpoint-root', '/artifacts/wave0/checkpoints/feasibility-a',
        '--run-id', $A5RunId,
        '--output', '/artifacts/wave0/receipts/feasibility-a.json'
    )
```

For reviewer readability, those calls resolve to these CLI commands:

```text
01-environment, network none:
val environment check --config /workspace/configs/environment/wave0.yaml
  --run-id <RUN_ID> --output /artifacts/wave0/receipts/environment.json

02-model-assets, network bridge:
val assets verify --config /workspace/configs/models/pinned-models.yaml
  --cache-root /artifacts/wave0/model_cache
  --output /artifacts/wave0/receipts/model-assets.json
  --run-id <RUN_ID> --download

03-model-contract, network none:
val probe model-contract --assets /artifacts/wave0/receipts/model-assets.json
  --environment /artifacts/wave0/receipts/environment.json
  --fixtures /workspace/fixtures/synthetic/wave0/fixture-manifest.json
  --run-id <RUN_ID> --output /artifacts/wave0/receipts/model-contract.json

04-feasibility-a, network none:
val probe training-feasibility
  --model-contract /artifacts/wave0/receipts/model-contract.json
  --checkpoint-root /artifacts/wave0/checkpoints/feasibility-a
  --run-id <RUN_ID> --output /artifacts/wave0/receipts/feasibility-a.json
```

Stages 1–3 require exit 0, schema-valid PASS receipts, and exact parent/source/image/run bindings. After stage 4 returns—exit 0 or nonzero—the harness must stop. It must not have a stage-5 command or call the full runner.

- [ ] **Step 4: Validate and classify the stage-4 outcome**

Search and validate the complete stage-4 log with this fail-closed classifier:

```powershell
$A5DiagnosticPrefix = `
    'deterministic backward warning contract failure; diagnostic='
$A5AllowedReasons = @(
    'unparsable_message',
    'unexpected_category',
    'count_mismatch',
    'unexpected_operation'
)
$A5ClassificationError = $null
$A5DecodedDiagnostic = $null
try {
    if ($A5Stage4.exit_code -ne 2) {
        throw "unexpected feasibility-A exit code: $($A5Stage4.exit_code)"
    }
    $A5DiagnosticLines = @(Get-Content -LiteralPath $A5Stage4.log_path |
        Where-Object { $_.StartsWith($A5DiagnosticPrefix) })
    if ($A5DiagnosticLines.Count -ne 1) {
        throw "diagnostic line count: $($A5DiagnosticLines.Count)"
    }
    $A5DiagnosticJson = $A5DiagnosticLines[0].Substring(
        $A5DiagnosticPrefix.Length
    )
    $A5DecodedDiagnostic = ConvertFrom-Json -InputObject $A5DiagnosticJson `
        -AsHashtable
    if ((@($A5DecodedDiagnostic.Keys | Sort-Object) -join ',') -ne `
        'reason,schema_version,warnings') {
        throw 'diagnostic top-level inventory mismatch'
    }
    if ($A5DecodedDiagnostic.schema_version -ne 1) {
        throw 'diagnostic schema version mismatch'
    }
    if ($A5DecodedDiagnostic.reason -notin $A5AllowedReasons) {
        throw 'diagnostic reason mismatch'
    }
    $A5Warnings = @($A5DecodedDiagnostic.warnings)
    for ($Index = 0; $Index -lt $A5Warnings.Count; $Index++) {
        $Warning = $A5Warnings[$Index]
        if ((@($Warning.Keys | Sort-Object) -join ',') -ne `
            'category,index,message') {
            throw "warning inventory mismatch at index $Index"
        }
        if ($Warning.index -ne $Index -or
            $Warning.category -isnot [string] -or
            $Warning.message -isnot [string]) {
            throw "warning value mismatch at index $Index"
        }
    }
    if (Test-Path -LiteralPath $A5Stage4.receipt_path) {
        throw 'diagnostic failure published a feasibility receipt'
    }
    if (@(Get-ChildItem -LiteralPath $A5CheckpointsRoot.FullName `
        -File -Recurse).Count -ne 0) {
        throw 'diagnostic failure published a checkpoint file'
    }
    $A5Terminal = `
        'WAVE0_A5_DIAGNOSTIC_CAPTURED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN'
} catch {
    $A5ClassificationError = $_.Exception.Message
    $A5Terminal = 'WAVE0_A5_DIAGNOSTIC_INCONCLUSIVE / WAVE1_FORBIDDEN'
}
```

For a captured diagnostic this classifier requires:

```text
stage exit code == 2
exactly one prefix occurrence
JSON parses with exact top-level keys reason/schema_version/warnings
schema_version == 1
reason is one of the four registered values
warnings is an ordered array with exact category/index/message keys
indexes equal 0..N-1 without gaps
no feasibility receipt exists
no checkpoint file exists
strict-mode failure did not replace the diagnostic
```

Record the complete decoded warning inventory without normalizing it. Close as:

```text
WAVE0_A5_DIAGNOSTIC_CAPTURED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN
```

Every other outcome—including feasibility-A exit 0, a pre-diagnostic failure, malformed/missing/multiple diagnostics, receipt/checkpoint publication on diagnostic failure, or an identity/evidence mismatch—closes as:

```text
WAVE0_A5_DIAGNOSTIC_INCONCLUSIVE / WAVE1_FORBIDDEN
```

- [ ] **Step 5: Preserve, rehash, release, and stop**

Write no-clobber campaign result, file manifest, historical-preservation record, and closure manifest. Rehash every Task 1 historical artifact and old image identity; exclude the new campaign only by its exact path and the new image only by its exact tag. Release the lease with a no-clobber release record and move only the validated exact lease directory to `<RUN_ID>.released`. Require active project lease count zero, both Git worktrees clean at the candidate SHA, `VAL_DATA_ROOT` unset, no RDD access, and no Wave 1 artifact.

Do not alter code, rerun, rebuild, start another campaign, change the parser/allowlist, execute full Task 6, or enter Wave 1. The raw diagnostic requires a separate owner-reviewed amendment.

**Stop condition:** The first failed identity, stage, diagnostic, preservation, lease, or no-clobber check. Preserve what exists and do not retry.

---

## Plan Self-Review Record

- [x] Section 5.2.7 maps to an exact task, file, command, or terminal condition.
- [x] The two-file implementation allowlist is closed; a third tracked file is a hard stop.
- [x] RED tests precede production changes and fail specifically because current errors omit the canonical inventory.
- [x] Prefix, schema version, four reason codes, JSON settings, array order, keys, indexes, messages, and categories are exact.
- [x] Existing per-warning parse-before-category, then count, then operation order is preserved.
- [x] Source/entry/callback failures remain non-diagnostic, strict mode is restored, and the exact success evidence is unchanged.
- [x] Receipt/schema/validator/runner/Dockerfile/config/dependency/research surfaces are not modified.
- [x] Complete CPU, formatting, lint, lock, diff, history, identity, and Critical/Important review gates precede the sole implementation commit.
- [x] The fresh image receives a CPU-only diagnostic micro-check before GPU lease acquisition.
- [x] Session-side execution contains only four stages and stops after feasibility-A in every outcome.
- [x] A5 diagnostic capture is explicitly not a Wave 0 pass, feasibility receipt, retry, or parser amendment.
- [x] Every prior campaign/image/evidence object remains immutable; every A5 destination is fresh and no-clobber.
- [x] RDD, feasibility-B, clean replay, aggregate Wave 0, Wave 1, remote, push, merge, tag, Release, and publication remain forbidden.
- [x] No unresolved placeholder, optional gate, ambiguous signature, unspecified error boundary, or scope expansion remains.

## Execution Selection

The owner delegated execution-method selection. Use **Inline Execution** in the existing registered worktree with `superpowers:executing-plans`. Do not use subagents unless the owner explicitly requests them. Begin only after this plan commit receives owner execution authorization; then pause only at a hard stop or the A5 diagnostic owner checkpoint.
