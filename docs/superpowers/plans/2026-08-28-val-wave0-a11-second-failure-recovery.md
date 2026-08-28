# Wave 0 A11 Second Failure-Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the A11 launcher close failures safely under production StrictMode, give both frozen Docker dependency installs a bounded 300-second HTTP timeout, and fail closed over the two immutable A11 attempts before any future write.

**Architecture:** Keep the existing two-phase launcher and its one-build/no-cache runtime boundary. Repair the closure accumulator with one typed `List[string]`, replace the single-attempt preflight value with an ordered two-record preservation envelope whose records retain distinct state schemas, and pass those preserved identities into the existing fresh-destination gate. Exercise only real production function text through the CPU-only Python/PowerShell AST harness; Docker and filesystem runtime boundaries are stubbed in tests, while final preservation checks are read-only.

**Tech Stack:** PowerShell 7.6.4 plus Windows PowerShell 5.1 parser; Python 3.12.11; pytest 9.0.2; Black and Ruff; Dockerfile syntax; Git linked worktree; read-only Docker/image inspection.

## Global Constraints

- The approved written specification is `docs/superpowers/specs/2026-08-28-val-wave0-a11-second-failure-recovery-design.md` at commit `cca4d97380d9b35977c034f3ad1bb46bacf2a9ab`; its source parent is `1445a90b799b6306d6c1f7abc94b4a201afe5dc6`.
- This plan commit must be the design commit's direct child and must contain only `docs/superpowers/plans/2026-08-28-val-wave0-a11-second-failure-recovery.md`.
- Code work begins only after the owner approves this committed plan. The implementation commit must be this plan commit's direct child and its diff must contain exactly `docker/wave0.Dockerfile`, `scripts/run_wave0_a11.ps1`, and `tests/gates/test_wave0_a11_launcher.py`.
- The implementation is CPU-only TDD. Do not invoke `scripts/run_wave0_a11.ps1`, `docker build`, `docker run`, model download, CUDA initialization, a real lease, a replica, calibration, validation, RDD, Wave 1, or any synthetic runtime authorization.
- `OWNER-A11-RUNTIME-20260828-01` and `steven001` are consumed. Do not reuse either value. A later runtime attempt needs a separate owner review and one fresh explicit authorization identifier.
- Preserve attempt 1 run `wave0-a11-calibration-20260828T045848083Z-b9917463` at 48 files and inventory SHA-256 `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b`; preserve its image ID `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`, historical record SHA-256 `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`, released lease SHA-256 `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`, and release record SHA-256 `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`.
- Preserve attempt 2 run `wave0-a11-calibration-20260828T114911289Z-fe8b7000` at five files and inventory SHA-256 `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b`; preserve preregistered validation ID `wave0-a11-validation-20260828T114911296Z-3107aff0`, authorization `steven001`, and the five exact file records from the approved design.
- Never close, backfill, repair, delete, rename, move, retag, reuse, or reinterpret either preserved attempt. Attempt 1 keeps 78/80/81/82 absent; attempt 2 keeps 78 through 82 absent and has no created image, lease/release, validation root, payload, replica, checkpoint, receipt, cache content, or container.
- Preserve exactly 64,306 historical non-A11 files at inventory SHA-256 `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`, exactly 21 historical images at inventory SHA-256 `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`, and all eight fixed A10 hashes already enforced by `Resolve-A11Worktree`.
- Keep the base-image digest, lockfile, dependencies, package index, five OCI labels, `--frozen`, launcher `--no-cache`, one build per phase, 12+12 cohorts, schemas, metrics, thresholds, ceilings, GPU identity, CUDA runtime, cache contract, lease protocol, terminal strings, no-clobber behavior, phase order, and Wave 1 prohibition unchanged.
- The Docker timeout is exactly two inline literal `UV_HTTP_TIMEOUT=300` assignments, one on each existing `uv sync` command. It is not a global `ENV`, an `ARG`, a retry, a cache, an index override, or a caller-controlled value.
- Keep staging empty through every RED/GREEN task. There are no intermediate commits. Commit once only after every CPU, style, parser, preservation, scope, and review gate passes.
- The single implementation commit must use author and committer `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- No amend, rebase, reset, stash, cherry-pick, cleanup of preserved evidence, push, merge, tag, release, publication, or modification of another repository is authorized.

## File Responsibility Map

| Path | Responsibility |
|---|---|
| `docker/wave0.Dockerfile` | Scope a fixed 300-second `uv` HTTP timeout to each of the two frozen dependency-install commands only |
| `scripts/run_wave0_a11.ps1` | Aggregate closure errors with a typed list; inventory two immutable attempts; reject drift, consumed authorization, and preserved identity reuse before initialization |
| `tests/gates/test_wave0_a11_launcher.py` | Run production PowerShell functions under StrictMode; provide exact two-attempt fixtures; test timeout source, mutation rejection, destination uniqueness, closure order, and no retry/write behavior without Docker or GPU |

## Closed Interface Map

`Get-A11PriorAttemptInventory -ArtifactRoot string` retains its name and returns this ordered envelope:

```text
run_names              string[2]
image_tags              string[1]
lease_names              string[2]
authorization_evidence   object[2]
attempts                 object[2]  # launcher-stage-failure, image-build-timeout
links_absent             bool
```

Attempt 1 has the exact closed keys `state`, `run_id`, `source_commit`, `registered_run_ids`, `registered_image_tags`, `registered_paths`, `owner_authorization_id`, `run_file_count`, `run_inventory_sha256`, `historical_preservation_sha256`, `released_lease_sha256`, `release_record_sha256`, `closure_paths_present`, `image_tag`, `image_id`, and `links_absent`.

Attempt 2 has the exact closed keys `state`, `run_id`, `source_commit`, `registered_run_ids`, `registered_image_tags`, `registered_paths`, `owner_authorization_id`, `run_file_count`, `run_inventory_sha256`, `file_records`, `directory_names`, `image_tags_present`, `lease_paths_present`, `validation_present`, `payload_file_paths_present`, `closure_paths_present`, `latest_write_utc`, and `links_absent`. `latest_write_utc` is contextual reporting only; the five path/size/SHA-256 records are the preservation identity.

`Resolve-A11Worktree` exposes the envelope as `prior_a11_attempts`. `Test-A11ReadOnlyPreflight` accepts only that plural field and its closed schemas. `Test-A11PhaseDestinationsAbsent -Identities object[2] -PriorAttempts object[2] -OwnerAuthorizationId string` rejects any new current/peer run ID, image tag, derived path, or authorization that intersects either preserved attempt before `Initialize-A11Phase` can write.

---

### Task 1: Freeze the plan lineage and two-attempt entry state

**Files:**
- Modify: none
- Inspect: linked/canonical Git state, historical artifacts/images, both A11 attempts, leases, containers, Docker engine, and CPU baseline

**Interfaces:**
- Consumes: approved design commit `cca4d97380d9b35977c034f3ad1bb46bacf2a9ab` and the owner-approved plan commit at `HEAD`
- Produces: an immutable read-only entry transcript and a clean three-file implementation gate

- [ ] **Step 1: Verify exact Git lineage and plan-only commit**

Run from the linked worktree:

```powershell
$PlanCommit = (git rev-parse HEAD).Trim()
$DesignCommit = 'cca4d97380d9b35977c034f3ad1bb46bacf2a9ab'
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'branch mismatch' }
if ((git rev-parse "$PlanCommit^").Trim() -cne $DesignCommit) { throw 'plan parent mismatch' }
$PlanPaths = @(git diff-tree --no-commit-id --name-only -r $PlanCommit)
if ($PlanPaths.Count -ne 1 -or $PlanPaths[0] -cne 'docs/superpowers/plans/2026-08-28-val-wave0-a11-second-failure-recovery.md') { throw 'plan commit scope mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree is dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }

$Listing = @(git worktree list --porcelain)
$CanonicalLine = $Listing | Where-Object { $_ -like 'worktree *' } | Select-Object -First 1
if ($null -eq $CanonicalLine) { throw 'canonical worktree missing' }
$Canonical = $CanonicalLine.Substring(9)
if (@(git -C $Canonical status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'canonical worktree is dirty' }
if ((git rev-parse --path-format=absolute --git-common-dir).Trim() -cne (git -C $Canonical rev-parse --path-format=absolute --git-common-dir).Trim()) { throw 'worktree common-dir mismatch' }
```

Any mismatch is a hard stop: preserve the observed state and report it without reset, stash, deletion, or repair.

- [ ] **Step 2: Recompute both A11 run inventories and exact filesystem state read-only**

```powershell
$ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
$Run1 = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
$Run2 = 'wave0-a11-calibration-20260828T114911289Z-fe8b7000'
$Validation2 = 'wave0-a11-validation-20260828T114911296Z-3107aff0'
$A11Root = Join-Path $ArtifactRoot 'a11-runs'

function Get-ClosedInventory([string]$Root) {
    $Links = @(Get-ChildItem -LiteralPath $Root -Recurse -Force | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint })
    if ($Links.Count -ne 0) { throw "linked evidence under $Root" }
    $Records = @(Get-ChildItem -LiteralPath $Root -File -Recurse -Force | Sort-Object FullName | ForEach-Object {
        [ordered]@{
            path = $_.FullName.Substring($Root.Length + 1).Replace('\','/')
            size = [long]$_.Length
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    })
    $Json = ConvertTo-Json -InputObject @($Records) -Depth 6 -Compress
    $Digest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($Json))).ToLowerInvariant()
    [pscustomobject]@{ records=$Records; count=$Records.Count; sha256=$Digest }
}

$One = Get-ClosedInventory (Join-Path $A11Root $Run1)
$Two = Get-ClosedInventory (Join-Path $A11Root $Run2)
if ($One.count -ne 48 -or $One.sha256 -cne 'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b') { throw 'attempt 1 drift' }
if ($Two.count -ne 5 -or $Two.sha256 -cne '8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b') { throw 'attempt 2 drift' }
$RunNames = @(Get-ChildItem -LiteralPath $A11Root -Directory -Force | Sort-Object Name -CaseSensitive | ForEach-Object Name)
if ((ConvertTo-Json $RunNames -Compress) -cne (ConvertTo-Json @($Run1,$Run2) -Compress)) { throw 'A11 run-root drift' }
if (Test-Path -LiteralPath (Join-Path $A11Root $Validation2)) { throw 'attempt 2 validation root exists' }

$ExpectedTwoFiles = [ordered]@{
    'audit/00-identity.json' = '2873|df1b6f37bfd9f7bce399f3a8b481bba564b5cacdd397ca82723100802b4bcec3'
    'audit/01-gpu-preflight.json' = '125|de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7'
    'audit/10-build.json' = '1234|d6fe3823a1d4f7980feecf0531d210158630287b2d6f9379353fbff0c7edae66'
    'audit/10-build.stderr.log' = '865210|50d3bf5bf6cfc3dcde1edca56c4bd84db0e7da77fd108dd47abdd1db6b9b881e'
    'audit/10-build.stdout.log' = '0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
}
foreach ($Record in $Two.records) {
    if (-not $ExpectedTwoFiles.Contains($Record.path)) { throw "unexpected attempt 2 file: $($Record.path)" }
    if ("$($Record.size)|$($Record.sha256)" -cne $ExpectedTwoFiles[$Record.path]) { throw "attempt 2 file drift: $($Record.path)" }
}
$TwoDirectories = @(Get-ChildItem -LiteralPath (Join-Path $A11Root $Run2) -Directory -Recurse -Force | Sort-Object FullName | ForEach-Object { $_.FullName.Substring((Join-Path $A11Root $Run2).Length + 1).Replace('\','/') })
$ExpectedDirectories = @('audit','wave0','wave0/checkpoints','wave0/model_cache','wave0/receipts')
if (Compare-Object $ExpectedDirectories $TwoDirectories -CaseSensitive) { throw 'attempt 2 directory drift' }
```

- [ ] **Step 3: Recompute historical, image, lease, container, and Docker preservation read-only**

Extract `Get-A11JsonSha256`, `Get-A11HistoricalArtifactInventory`, and `Get-A11HistoricalImageInventory` from the production AST and execute only those functions:

```powershell
$Script = (Resolve-Path 'scripts/run_wave0_a11.ps1').Path
$Tokens=$null; $Errors=$null
$Ast=[Management.Automation.Language.Parser]::ParseFile($Script,[ref]$Tokens,[ref]$Errors)
if ($Errors.Count -ne 0) { throw ($Errors.Message -join '; ') }
foreach ($Name in @('Get-A11JsonSha256','Get-A11HistoricalArtifactInventory','Get-A11HistoricalImageInventory')) {
    $Match=@($Ast.FindAll({ param($Node) $Node -is [Management.Automation.Language.FunctionDefinitionAst] -and $Node.Name -eq $Name },$true))
    if ($Match.Count -ne 1) { throw "AST mismatch: $Name" }
    Invoke-Expression $Match[0].Extent.Text
}
$Historical=Get-A11HistoricalArtifactInventory -ArtifactRoot 'D:\vision-active-learning-loop-artifacts\wave0'
$Images=Get-A11HistoricalImageInventory
if (@($Historical.records).Count -ne 64306 -or $Historical.sha256 -cne 'e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95') { throw 'historical artifact drift' }
if (@($Images.records).Count -ne 21 -or $Images.sha256 -cne '9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f') { throw 'historical image drift' }

$OldTag='vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
$A11Tags=@(docker image ls --filter 'reference=vision-active-learning-loop:wave0-a11-*' --format '{{.Repository}}:{{.Tag}}' | Sort-Object -Unique)
if ($LASTEXITCODE -ne 0 -or $A11Tags.Count -ne 1 -or $A11Tags[0] -cne $OldTag) { throw 'A11 image inventory drift' }
$OldImage=@(docker image inspect -- $OldTag | ConvertFrom-Json)
if ($LASTEXITCODE -ne 0 -or $OldImage.Count -ne 1 -or [string]$OldImage[0].Id -cne 'sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5') { throw 'attempt 1 image drift' }
$LeaseNames=@(Get-ChildItem -LiteralPath 'D:\vision-active-learning-loop-artifacts\wave0\leases' -File -Force | Where-Object Name -Like 'wave0-a11-*' | Sort-Object Name -CaseSensitive | ForEach-Object Name)
$ExpectedLeaseNames=@('wave0-a11-calibration-20260828T045848083Z-b9917463.release.json','wave0-a11-calibration-20260828T045848083Z-b9917463.released')
if (Compare-Object $ExpectedLeaseNames $LeaseNames -CaseSensitive) { throw 'A11 lease history drift' }
if (Test-Path Env:VAL_DATA_ROOT) { throw 'VAL_DATA_ROOT must remain unset' }
$ProjectContainers=@(docker ps --all --format '{{.ID}}' | ForEach-Object {
    $ContainerId=$_
    $ImageId=(docker inspect --format '{{.Image}}' -- $ContainerId).Trim()
    $RepoTagsJson=(docker image inspect --format '{{json .RepoTags}}' -- $ImageId).Trim()
    $RepoTags=if($RepoTagsJson -ceq 'null'){@()}else{@($RepoTagsJson | ConvertFrom-Json)}
    if (@($RepoTags | Where-Object { $_ -like 'vision-active-learning-loop:*' }).Count -gt 0) { "$ContainerId|$ImageId" }
})
if ($ProjectContainers.Count -ne 0) { throw 'project container exists in running or stopped state' }
$Docker=(docker info --format '{{.OSType}}|{{.ServerVersion}}').Trim()
if ($LASTEXITCODE -ne 0 -or $Docker -cnotmatch '^linux\|.+$') { throw 'Docker Linux engine unavailable' }
```

Also rehash the eight paths in `$FixedA10` inside `Resolve-A11Worktree`; require every current hash to equal the literal registered hash. Do not replace any value from observed data.

- [ ] **Step 4: Run the unchanged full CPU baseline without bytecode or pytest cache**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest -q -p no:cacheprovider
```

Expected: the pre-implementation baseline passes (`1107 passed, 15 skipped` at plan creation). If the count or outcome differs, preserve the output and stop before editing.

- [ ] **Step 5: Confirm the exact edit allowlist before RED**

```powershell
$Allowed=@('docker/wave0.Dockerfile','scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')
foreach ($Path in $Allowed) { if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "missing allowlisted path: $Path" } }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'candidate is dirty before RED' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty before RED' }
```

---

### Task 2: Make failure closure StrictMode-safe for every error cardinality

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py:68-100,1777-1849,1992-2079`
- Modify: `scripts/run_wave0_a11.ps1:1520-1588`

**Interfaces:**
- Consumes: `_invoke_functions`, real `Write-A11NewText`, `Get-A11FileRecord`, `Close-A11Phase`, and `Invoke-A11Campaign`
- Produces: a production-equivalent StrictMode AST harness and one `Collections.Generic.List[string]` accumulator used for initial, aggregate, preservation, and default errors

- [ ] **Step 1: Add production StrictMode to the AST harness**

Insert this line before `$ErrorActionPreference` in `_invoke_functions`:

```python
script = f"""
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
```

Run the existing single-failure closure test:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py::test_close_a11_phase_publishes_complete_bound_failure_chain
```

Expected RED: PowerShell reports that `Count` cannot be found on the one-string `$ErrorList`.

- [ ] **Step 2: Add RED zero/one/multiple cardinality coverage against the real closure**

Refactor the existing closure setup into `_run_close_a11_phase(tmp_path, *, terminal, failure, aggregate_errors)` and keep the real writer/file-record/closure functions. For the multiple case, write `wave0/receipts/statistical-replay-calibration.json` with `{"normative":{"errors":["first","second"]}}`; for zero and one, omit that receipt. Add this exact contract test:

```python
@pytest.mark.parametrize(
    ("terminal", "failure", "aggregate_errors", "expected"),
    [
        (
            "WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN",
            "",
            [],
            [],
        ),
        (
            "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN",
            "injected:build",
            [],
            ["injected:build"],
        ),
        (
            "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN",
            "",
            ["first", "second"],
            ["first", "second"],
        ),
    ],
)
def test_close_a11_phase_keeps_typed_error_cardinality_under_strictmode(
    tmp_path: Path,
    terminal: str,
    failure: str,
    aggregate_errors: list[str],
    expected: list[str],
) -> None:
    completed, audit = _run_close_a11_phase(
        tmp_path,
        terminal=terminal,
        failure=failure,
        aggregate_errors=aggregate_errors,
    )
    assert completed.returncode == 0, completed.stderr
    diagnostic = audit / "78-failure-diagnostic.json"
    if expected:
        assert json.loads(diagnostic.read_text(encoding="utf-8"))["errors"] == expected
    else:
        assert not diagnostic.exists()
        result = json.loads((audit / "80-campaign-result.json").read_text())
        assert result["failure"] == ""
```

Expected RED: the one-error row fails under StrictMode; the test also fixes the required serialization behavior for zero and multiple errors.

- [ ] **Step 3: Add a RED real campaign build-failure closure test**

Add `test_campaign_build_failure_publishes_one_complete_closure_and_stops`. Stub only preflight, identities, initialization, Docker build, and historical inventories. `Initialize-A11Phase` creates the temporary `audit`, `wave0/receipts`, `wave0/checkpoints`, and `wave0/model_cache` directories; `Invoke-A11Build` appends `build:calibration` then throws `injected:build`. Invoke real `Invoke-A11Campaign` and real `Close-A11Phase`, then require:

```python
assert output["count"] == 1
assert output["result"]["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
assert output["events"] == ["init:calibration", "build:calibration"]
assert sorted(path.name for path in calibration_audit.glob("*.json")) == [
    "78-failure-diagnostic.json",
    "79-historical-preservation-final.json",
    "80-campaign-result.json",
    "81-campaign-file-manifest.json",
    "82-campaign-closure.json",
]
assert not validation_root.exists()
```

The stubbed raw preflight must include `prior_a11_attempts = @{ attempts = @() }` until Task 5 supplies real preserved records. Expected RED: closure fails at scalar `.Count`, so 78–82 are not all published.

- [ ] **Step 4: Implement the minimal typed accumulator**

Replace the scalar/array construction and every later reassignment or `+=` with this typed interface:

```powershell
$ErrorList = [Collections.Generic.List[string]]::new()
if (-not [string]::IsNullOrWhiteSpace($Failure)) {
    [void]$ErrorList.Add($Failure)
}
```

Use the same list at each later branch:

```powershell
if (-not $Preserved) {
    $Terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
    [void]$ErrorList.Add('A11 final historical preservation rehash failed')
}

if (
    $Terminal -ceq 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' -and
    $ErrorList.Count -eq 0
) {
    $AggregatePath = [IO.Path]::Combine(
        $Identity.campaign_root, 'wave0', 'receipts',
        "statistical-replay-$($Identity.phase).json"
    )
    if (Test-Path -LiteralPath $AggregatePath -PathType Leaf) {
        $Aggregate = Get-Content -Raw -LiteralPath $AggregatePath | ConvertFrom-Json
        foreach ($AggregateError in @($Aggregate.normative.errors)) {
            [void]$ErrorList.Add([string]$AggregateError)
        }
    }
    if ($ErrorList.Count -eq 0) {
        [void]$ErrorList.Add('A11 normative phase failure')
    }
}
$Failure = $ErrorList -join '; '
```

Serialize `errors = @($ErrorList.ToArray())`. Do not change closure paths, order, schemas, terminal values, `Write-A11NewText`, manifest contents, or the catch branches in `Invoke-A11Campaign`.

- [ ] **Step 5: Run closure GREEN and no-repair regressions**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_close_a11_phase_keeps_typed_error_cardinality_under_strictmode `
  tests/gates/test_wave0_a11_launcher.py::test_close_a11_phase_publishes_complete_bound_failure_chain `
  tests/gates/test_wave0_a11_launcher.py::test_campaign_build_failure_publishes_one_complete_closure_and_stops `
  tests/gates/test_wave0_a11_launcher.py::test_campaign_surfaces_closure_write_failure_without_retry `
  tests/gates/test_wave0_a11_launcher.py::test_single_campaign_result_rejects_zero_or_multiple_values
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging changed during TDD' }
```

Expected: PASS. The sentinel closure-publication test must retain original bytes and expose one `closure_error`; no validation, retry, repair, or second build occurs.

---

### Task 3: Bound both frozen Docker dependency downloads to 300 seconds

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py:12-19,1427-1462,2279-2292`
- Modify: `docker/wave0.Dockerfile:31-35`

**Interfaces:**
- Consumes: Dockerfile source and real `New-A11BuildArguments`
- Produces: two command-local literal timeout assignments with the existing dependency graph and one-build/no-cache launcher contract unchanged

- [ ] **Step 1: Add a RED exact-source Dockerfile test**

Add `_DOCKERFILE = _ROOT / "docker" / "wave0.Dockerfile"` and:

```python
def test_wave0_dockerfile_has_exact_bounded_uv_timeouts() -> None:
    source = _DOCKERFILE.read_text(encoding="utf-8")
    timeout_lines = [
        line.strip() for line in source.splitlines() if "UV_HTTP_TIMEOUT" in line
    ]
    assert timeout_lines == [
        "RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev --no-install-project",
        "RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev",
    ]
    assert "ENV UV_HTTP_TIMEOUT" not in source
    assert "ARG UV_HTTP_TIMEOUT" not in source
    assert source.count("uv sync --frozen --no-dev") == 2
    lowered = source.lower()
    assert "--retry" not in lowered
    assert "--index-url" not in lowered
    assert "--extra-index-url" not in lowered
```

Extend `test_launcher_source_has_no_cleanup_retry_or_wave1_capability` with:

```python
assert source.count("'build', '--no-cache'") == 1
assert source.count("Invoke-A11Build $Identity") == 1
```

- [ ] **Step 2: Run the timeout and build-contract tests and verify RED**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_wave0_dockerfile_has_exact_bounded_uv_timeouts `
  tests/gates/test_wave0_a11_launcher.py::test_build_arguments_have_exact_independent_labels `
  tests/gates/test_wave0_a11_launcher.py::test_launcher_source_has_no_cleanup_retry_or_wave1_capability
```

Expected RED: the Dockerfile has zero `UV_HTTP_TIMEOUT` lines.

- [ ] **Step 3: Make the two literal Dockerfile replacements only**

```dockerfile
RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev --no-install-project
COPY src ./src
COPY configs ./configs
RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev
```

Do not change any other Dockerfile line or any build argument.

- [ ] **Step 4: Run GREEN and inspect the exact Dockerfile diff**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_wave0_dockerfile_has_exact_bounded_uv_timeouts `
  tests/gates/test_wave0_a11_launcher.py::test_build_arguments_have_exact_independent_labels `
  tests/gates/test_wave0_a11_launcher.py::test_launcher_source_has_no_cleanup_retry_or_wave1_capability
git diff --check -- docker/wave0.Dockerfile tests/gates/test_wave0_a11_launcher.py
git diff -- docker/wave0.Dockerfile
```

Expected: PASS and exactly two one-line replacements. Do not build the image.

---

### Task 4: Replace the one-attempt preflight with two distinct closed records

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py:21-61,314-426,900-1057`
- Modify: `scripts/run_wave0_a11.ps1:172-249,371-579,1694-1707`

**Interfaces:**
- Consumes: `Get-A11JsonSha256`, `Invoke-A11Native`, the exact artifact root, both identity documents, and read-only filesystem/image inventories
- Produces: the `prior_a11_attempts` envelope and two state-specific records defined in the Closed Interface Map

- [ ] **Step 1: Add exact constants and fixture records for attempt 2**

Add constants for the second run, its preregistered peer, consumed owner, and both registered tags:

```python
_FAILED_VALIDATION_ID = "wave0-a11-validation-20260828T045848091Z-084431a4"
_FAILED_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "2622e402e4f5-20260828T045848091Z-084431a4"
)
_TIMEOUT_RUN_ID = "wave0-a11-calibration-20260828T114911289Z-fe8b7000"
_TIMEOUT_VALIDATION_ID = "wave0-a11-validation-20260828T114911296Z-3107aff0"
_TIMEOUT_OWNER = "steven001"
_TIMEOUT_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "1445a90b799b-20260828T114911289Z-fe8b7000"
)
_TIMEOUT_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "1445a90b799b-20260828T114911296Z-3107aff0"
)
_TIMEOUT_RUN_SHA256 = "8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b"
_TIMEOUT_FILES = [
    {"path": "audit/00-identity.json", "size": 2873, "sha256": "df1b6f37bfd9f7bce399f3a8b481bba564b5cacdd397ca82723100802b4bcec3"},
    {"path": "audit/01-gpu-preflight.json", "size": 125, "sha256": "de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7"},
    {"path": "audit/10-build.json", "size": 1234, "sha256": "d6fe3823a1d4f7980feecf0531d210158630287b2d6f9379353fbff0c7edae66"},
    {"path": "audit/10-build.stderr.log", "size": 865210, "sha256": "50d3bf5bf6cfc3dcde1edca56c4bd84db0e7da77fd108dd47abdd1db6b9b881e"},
    {"path": "audit/10-build.stdout.log", "size": 0, "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
]
```

Replace `_prior_attempt()` with `_prior_attempts()` returning the closed envelope and the exact two state records. Attempt 1 registers its calibration and peer IDs/tags from `audit/00-identity.json`; attempt 2 registers `_TIMEOUT_RUN_ID`, `_TIMEOUT_VALIDATION_ID`, `_TIMEOUT_IMAGE_TAG`, and `_TIMEOUT_VALIDATION_TAG`. The envelope's `authorization_evidence` is exactly:

```python
[
    {
        "run_id": _FAILED_RUN_ID,
        "path": "audit/00-identity.json",
        "owner_authorization_id": _FAILED_OWNER,
    },
    {
        "run_id": _TIMEOUT_RUN_ID,
        "path": "audit/00-identity.json",
        "owner_authorization_id": _TIMEOUT_OWNER,
    },
]
```

Build each record's `registered_paths` with this deterministic helper so the current and preregistered peer destinations are both bound even when the peer root was never created:

```python
def _registered_paths(artifact_root: str, run_ids: list[str]) -> list[str]:
    root = Path(artifact_root)
    values: list[str] = []
    for run_id in run_ids:
        campaign = root / "a11-runs" / run_id
        values.extend(
            [
                str(campaign),
                str(campaign / "wave0" / "model_cache"),
                str(campaign / "audit" / "active-lease.json"),
                str(root / "leases" / f"{run_id}.released"),
                str(root / "leases" / f"{run_id}.release.json"),
                str(campaign / "audit"),
                str(campaign / "wave0" / "receipts"),
                str(campaign / "wave0" / "checkpoints"),
            ]
        )
    return [str(Path(value)) for value in values]
```

The preflight fixture uses artifact root `D:/vision-active-learning-loop-artifacts/wave0`, attempt 1 source `2622e402e4f536b94326ac34f9b20c90b513002b`, and attempt 2 source `1445a90b799b6306d6c1f7abc94b4a201afe5dc6`. Production normalizes every registered path with `[IO.Path]::GetFullPath` before exact ordinal-ignore-case filesystem comparison.
Set attempt 2 `directory_names` to `['audit', 'wave0', 'wave0/checkpoints', 'wave0/model_cache', 'wave0/receipts']`, all four absence arrays empty, `validation_present` false, and contextual `latest_write_utc` to `2026-08-28T12:17:12.8122776Z`.

Set `_preflight()["prior_a11_attempts"] = _prior_attempts()` and remove the singular key.

- [ ] **Step 2: Add RED closed-schema and mutation tests**

Rename the acceptance test to `test_read_only_preflight_accepts_exact_two_attempt_evidence`. Add exact schema assertions:

```python
def test_two_prior_attempts_keep_distinct_closed_state_schemas() -> None:
    attempts = _prior_attempts()["attempts"]
    assert [attempt["state"] for attempt in attempts] == [
        "launcher-stage-failure",
        "image-build-timeout",
    ]
    assert set(attempts[0]) == {
        "state", "run_id", "source_commit", "registered_run_ids",
        "registered_image_tags", "registered_paths",
        "owner_authorization_id", "run_file_count", "run_inventory_sha256",
        "historical_preservation_sha256", "released_lease_sha256",
        "release_record_sha256", "closure_paths_present", "image_tag",
        "image_id", "links_absent",
    }
    assert set(attempts[1]) == {
        "state", "run_id", "source_commit", "registered_run_ids",
        "registered_image_tags", "registered_paths",
        "owner_authorization_id", "run_file_count", "run_inventory_sha256",
        "file_records", "directory_names", "image_tags_present",
        "lease_paths_present", "validation_present",
        "payload_file_paths_present", "closure_paths_present",
        "latest_write_utc", "links_absent",
    }
```

Use `copy.deepcopy(_preflight())` and parameterize mutations over all of these exact paths:

```python
_PRIOR_MUTATIONS = [
    (("run_names",), []),
    (("image_tags",), []),
    (("lease_names",), []),
    (("authorization_evidence", 1, "owner_authorization_id"), _FAILED_OWNER),
    (("links_absent",), False),
    (("attempts", 0, "state"), "image-build-timeout"),
    (("attempts", 0, "source_commit"), "0" * 40),
    (("attempts", 0, "registered_paths"), []),
    (("attempts", 0, "run_file_count"), 47),
    (("attempts", 0, "run_inventory_sha256"), "0" * 64),
    (("attempts", 0, "historical_preservation_sha256"), "0" * 64),
    (("attempts", 0, "released_lease_sha256"), "0" * 64),
    (("attempts", 0, "release_record_sha256"), "0" * 64),
    (("attempts", 0, "closure_paths_present"), ["80-campaign-result.json"]),
    (("attempts", 0, "image_id"), "sha256:" + "0" * 64),
    (("attempts", 1, "state"), "launcher-stage-failure"),
    (("attempts", 1, "source_commit"), "0" * 40),
    (("attempts", 1, "registered_paths"), []),
    (("attempts", 1, "owner_authorization_id"), _FAILED_OWNER),
    (("attempts", 1, "run_file_count"), 4),
    (("attempts", 1, "run_inventory_sha256"), "0" * 64),
    (("attempts", 1, "file_records", 3, "size"), 865209),
    (("attempts", 1, "file_records", 3, "sha256"), "0" * 64),
    (("attempts", 1, "directory_names"), ["audit"]),
    (("attempts", 1, "image_tags_present"), [_TIMEOUT_IMAGE_TAG]),
    (("attempts", 1, "lease_paths_present"), ["active-lease.json"]),
    (("attempts", 1, "validation_present"), True),
    (("attempts", 1, "payload_file_paths_present"), ["wave0/receipts/x.json"]),
    (("attempts", 1, "closure_paths_present"), ["78-failure-diagnostic.json"]),
    (("attempts", 1, "links_absent"), False),
]
```

The mutation helper walks dictionaries/lists by the tuple path, sets the replacement, runs real `Test-A11ReadOnlyPreflight`, and requires nonzero exit with `prior A11` in stderr. Add separate rows that swap the two attempt records, add a third run, add a second A11 image, add a third lease history file, move `steven001` to attempt 1 authorization evidence, delete any one of the five attempt-2 file records, and substitute one state's record for the other.

- [ ] **Step 3: Run preflight tests and verify RED**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py -k 'two_attempt or prior_a11 or read_only_preflight'
```

Expected RED: production requires singular `prior_a11_attempt`, exactly one run, one attempt-1 image, and the old flat schema.

- [ ] **Step 4: Expand the temporary collector fixture to both partial states**

Update `_run_prior_attempt_inventory` so it creates:

```text
artifacts/a11-runs/<attempt-1>/audit/00-identity.json
artifacts/a11-runs/<attempt-1>/audit/79-historical-preservation-final.json
artifacts/a11-runs/<attempt-1>/payload.bin
artifacts/a11-runs/<attempt-2>/audit/00-identity.json
artifacts/a11-runs/<attempt-2>/audit/01-gpu-preflight.json
artifacts/a11-runs/<attempt-2>/audit/10-build.json
artifacts/a11-runs/<attempt-2>/audit/10-build.stderr.log
artifacts/a11-runs/<attempt-2>/audit/10-build.stdout.log
artifacts/a11-runs/<attempt-2>/wave0/checkpoints/
artifacts/a11-runs/<attempt-2>/wave0/model_cache/
artifacts/a11-runs/<attempt-2>/wave0/receipts/
artifacts/leases/<attempt-1>.release.json
artifacts/leases/<attempt-1>.released
```

Both identity documents use the exact `current` and `preregistered_peer` fields consumed by production: `run_id`, `image_tag`, `campaign_root`, `cache_root`, `lease_id`, `lease_lock_path`, `lease_path`, and `owner_authorization_id`. Stub `docker image ls` with attempt 1's tag only and `docker image inspect` with `_FAILED_IMAGE_ID`. Add defects for a link in either run, a link in leases, an extra empty A11 directory, attempt-2 payload content, an existing validation root, an existing attempt-2 release file, an unexpected A11 image, and Docker inspection failure.

The collector success test recomputes both temporary run digests in Python and requires the envelope/schema from the Closed Interface Map, exact sorted root inventories, empty attempt-2 forbidden arrays, and `latest_write_utc` parseable as UTC.

Update the AST extraction tuple to include `Test-A11PathEntryPresent` and the new `Get-A11RegisteredAttemptPaths`; add the latter to `test_launcher_has_exact_parameters_and_required_functions`. Add `test_launcher_preflight_inventories_all_container_states`, which reads the launcher source and requires exactly one `docker ps --all` inventory and no plain `docker ps --format` inventory. This test is RED before the `Resolve-A11Worktree` change.

- [ ] **Step 5: Implement the two-record collector**

Keep one root-level pass for `run_names`, `image_tags`, and `lease_names`. Require all inspected A11 roots and descendants to be non-links. Read each run's `audit/00-identity.json` and bind its current plus preregistered peer identities. Build file records with the existing ordered shape and `Get-A11JsonSha256`.

For attempt 1, return:

```powershell
[pscustomobject][ordered]@{
    state = 'launcher-stage-failure'
    run_id = $Run1Id
    source_commit = [string]$Identity1.current.source_commit
    registered_run_ids = @([string]$Identity1.current.run_id, [string]$Identity1.preregistered_peer.run_id)
    registered_image_tags = @([string]$Identity1.current.image_tag, [string]$Identity1.preregistered_peer.image_tag)
    registered_paths = @(Get-A11RegisteredAttemptPaths -ArtifactRoot $ArtifactRoot -Identities @($Identity1.current, $Identity1.preregistered_peer))
    owner_authorization_id = [string]$Identity1.current.owner_authorization_id
    run_file_count = $Records1.Count
    run_inventory_sha256 = Get-A11JsonSha256 -Value $Records1 -Depth 6
    historical_preservation_sha256 = (Get-FileHash -LiteralPath $FinalHistoryPath -Algorithm SHA256).Hash.ToLowerInvariant()
    released_lease_sha256 = (Get-FileHash -LiteralPath $ReleasedPath -Algorithm SHA256).Hash.ToLowerInvariant()
    release_record_sha256 = (Get-FileHash -LiteralPath $ReleaseRecordPath -Algorithm SHA256).Hash.ToLowerInvariant()
    closure_paths_present = @($Closure1Present)
    image_tag = $Attempt1ImageTag
    image_id = [string]$Images[0].Id
    links_absent = $true
}
```

For attempt 2, enumerate its five records, exact directory names, `wave0` payload files, closure files 78–82, validation root, current/peer release and lease destinations, and both registered image tags. Return:

```powershell
[pscustomobject][ordered]@{
    state = 'image-build-timeout'
    run_id = $Run2Id
    source_commit = [string]$Identity2.current.source_commit
    registered_run_ids = @([string]$Identity2.current.run_id, [string]$Identity2.preregistered_peer.run_id)
    registered_image_tags = @([string]$Identity2.current.image_tag, [string]$Identity2.preregistered_peer.image_tag)
    registered_paths = @(Get-A11RegisteredAttemptPaths -ArtifactRoot $ArtifactRoot -Identities @($Identity2.current, $Identity2.preregistered_peer))
    owner_authorization_id = [string]$Identity2.current.owner_authorization_id
    run_file_count = $Records2.Count
    run_inventory_sha256 = Get-A11JsonSha256 -Value $Records2 -Depth 6
    file_records = @($Records2)
    directory_names = @($Directories2)
    image_tags_present = @($ImageTags | Where-Object { $_ -cin @([string]$Identity2.current.image_tag, [string]$Identity2.preregistered_peer.image_tag) })
    lease_paths_present = @($Attempt2LeasePaths | Where-Object { Test-A11PathEntryPresent -Path $_ })
    validation_present = Test-A11PathEntryPresent -Path ([string]$Identity2.preregistered_peer.campaign_root)
    payload_file_paths_present = @($Payload2)
    closure_paths_present = @($Closure2Present)
    latest_write_utc = ($Latest2.LastWriteTimeUtc.ToString('o'))
    links_absent = $true
}
```

Add `Get-A11RegisteredAttemptPaths -ArtifactRoot string -Identities object[2]` immediately before the collector. For each identity, require its campaign root equals `ArtifactRoot/a11-runs/<run_id>`, its cache and active-lease paths equal the deterministic descendants, and emit the eight paths shown by the Python `_registered_paths` helper. Derive release paths from `ArtifactRoot/leases`; do not include the shared GPU lock in `registered_paths` because a future attempt intentionally uses that same lock destination after proving it absent.

Return the ordered envelope with the two records in attempt order and exactly two authorization-evidence entries. Identity parsing must require current and peer authorization IDs equal within each document; it must not search or rewrite document contents. Change the all-container inventory in `Resolve-A11Worktree` from `docker ps` to `docker ps --all`; the existing `project_containers` closed field then rejects both running and stopped project containers.

- [ ] **Step 6: Close and validate the plural preflight schema**

In `Resolve-A11Worktree`, emit `prior_a11_attempts = $PriorA11`. In both `Test-A11ReadOnlyPreflight` and `Invoke-A11Campaign`, replace the singular preflight key with the plural key. Enforce the exact envelope keys, record order, distinct record key sets, all literal counts/digests/IDs/tags/files/directories/absence arrays, and exactly one authorization-evidence location per attempt. Require `steven001` only in attempt 2's identity evidence. Parse `latest_write_utc` as UTC but do not compare it to a preservation hash or use it as identity.

Run GREEN:

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py -k 'preflight or prior_attempt or two_attempt or active_lease or gpu_inventory'
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging changed during TDD' }
```

Expected: PASS and no real artifact mutation.

---

### Task 5: Reject consumed authorization and every preserved identity before initialization

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py:429-488,900-958,1140-1392,1873-2276`
- Modify: `scripts/run_wave0_a11.ps1:476-579,670-735,1686-1714`

**Interfaces:**
- Consumes: `prior_a11_attempts.attempts`, two new in-memory phase identities, and the caller-supplied authorization
- Produces: `Test-A11PhaseDestinationsAbsent -Identities -PriorAttempts -OwnerAuthorizationId` and orchestration order `preflight -> identities -> preserved/fresh destination gate -> initialization`

- [ ] **Step 1: Add RED rejection for both consumed authorizations**

Replace the one-value test with:

```python
@pytest.mark.parametrize("owner", [_FAILED_OWNER, _TIMEOUT_OWNER])
def test_read_only_preflight_rejects_each_consumed_authorization(owner: str) -> None:
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",),
        _preflight_body(_preflight(), owner=owner),
    )
    assert completed.returncode != 0
    assert "prior owner authorization" in completed.stderr
```

Expected RED: `steven001` is not rejected.

- [ ] **Step 2: Extend destination fixtures and add RED preserved-identity cases**

Add `owner_authorization_id: _OWNER` to both dictionaries returned by `_phase_destination_identities`. Change `_run_phase_destination_gate` to pass `-PriorAttempts` from `_prior_attempts()["attempts"]` and `-OwnerAuthorizationId _OWNER`.

Add these mutation rows:

```python
@pytest.mark.parametrize(
    ("phase_index", "field", "preserved_value"),
    [
        (0, "run_id", _FAILED_RUN_ID),
        (1, "run_id", "wave0-a11-validation-20260828T045848091Z-084431a4"),
        (0, "run_id", _TIMEOUT_RUN_ID),
        (1, "run_id", _TIMEOUT_VALIDATION_ID),
        (0, "image_tag", _FAILED_IMAGE_TAG),
        (1, "image_tag", _TIMEOUT_VALIDATION_TAG),
    ],
)
def test_phase_destination_gate_rejects_any_preserved_runtime_identity(
    tmp_path: Path, phase_index: int, field: str, preserved_value: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    identities[phase_index][field] = preserved_value
    completed = _run_phase_destination_gate(identities)
    assert completed.returncode != 0
    assert "preserved" in completed.stderr
```

Add `test_phase_destination_gate_rejects_each_preserved_path_even_when_the_entry_is_absent`. Build `preserved = _prior_attempts()["attempts"][1]["registered_paths"][8:]` for attempt 2's preregistered validation identity and parameterize its eight entries:

```python
@pytest.mark.parametrize("path_index", range(8))
def test_phase_destination_gate_rejects_each_preserved_path_even_when_absent(
    tmp_path: Path, path_index: int
) -> None:
    identities = _phase_destination_identities(tmp_path)
    preserved = _prior_attempts()["attempts"][1]["registered_paths"][8:]
    target = Path(preserved[path_index])
    if path_index == 0:
        identities[1]["campaign_root"] = str(target)
    elif path_index == 1:
        identities[1]["cache_root"] = str(target)
    elif path_index == 2:
        identities[1]["lease_path"] = str(target)
    else:
        identities[1]["run_id"] = _TIMEOUT_VALIDATION_ID
    completed = _run_phase_destination_gate(identities)
    assert completed.returncode != 0
    assert "preserved" in completed.stderr
```

For rows 3–7 the registered run-ID rejection may fire before path comparison; the separate rows 0–2 prove absent path comparison itself. Instrument the PowerShell stubs with counters and require zero `Test-A11PathEntryPresent` and Docker calls.

Add `test_phase_destination_gate_rejects_consumed_or_mismatched_owner`: use each consumed owner and one identity whose `owner_authorization_id` differs from the supplied fresh owner; require failure before any `Test-A11PathEntryPresent` or Docker call.

- [ ] **Step 3: Implement prior-set comparison at the start of the destination gate**

Change the signature to:

```powershell
function Test-A11PhaseDestinationsAbsent {
    param(
        [Parameter(Mandatory = $true)][ValidateCount(2, 2)][object[]]$Identities,
        [Parameter(Mandatory = $true)][ValidateCount(2, 2)][object[]]$PriorAttempts,
        [Parameter(Mandatory = $true)][string]$OwnerAuthorizationId
    )
```

Before existing timestamp, path, and Docker checks, build case-sensitive sets and reject intersections:

```powershell
$PriorRunIds = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$PriorImageTags = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$PriorOwners = [Collections.Generic.HashSet[string]]::new([StringComparer]::Ordinal)
$PriorPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
foreach ($Attempt in $PriorAttempts) {
    foreach ($Value in @($Attempt.registered_run_ids)) { [void]$PriorRunIds.Add([string]$Value) }
    foreach ($Value in @($Attempt.registered_image_tags)) { [void]$PriorImageTags.Add([string]$Value) }
    foreach ($Value in @($Attempt.registered_paths)) { [void]$PriorPaths.Add([IO.Path]::GetFullPath([string]$Value)) }
    [void]$PriorOwners.Add([string]$Attempt.owner_authorization_id)
}
if ($PriorOwners.Contains($OwnerAuthorizationId)) {
    throw 'A11 prior owner authorization cannot be reused'
}
foreach ($Identity in $Identities) {
    if ([string]$Identity.owner_authorization_id -cne $OwnerAuthorizationId) {
        throw 'A11 phase owner authorization mismatch'
    }
    if ($PriorRunIds.Contains([string]$Identity.run_id)) {
        throw "A11 preserved run identity is reused: $($Identity.run_id)"
    }
    if ($PriorImageTags.Contains([string]$Identity.image_tag)) {
        throw "A11 preserved image identity is reused: $($Identity.image_tag)"
    }
    $LeaseRoot = [IO.Path]::GetDirectoryName([string]$Identity.lease_lock_path)
    $CandidatePaths = @(
        [string]$Identity.campaign_root,
        [string]$Identity.cache_root,
        [string]$Identity.lease_path,
        [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).released"),
        [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).release.json"),
        [IO.Path]::Combine([string]$Identity.campaign_root, 'audit'),
        [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'receipts'),
        [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'checkpoints')
    )
    foreach ($Path in $CandidatePaths) {
        if ($PriorPaths.Contains([IO.Path]::GetFullPath($Path))) {
            throw "A11 preserved runtime destination is reused: $Path"
        }
    }
}
```

Keep the existing calibration/validation cross-comparison, case-insensitive filesystem probe, shared lease-lock absence check, and exact Docker tag query after these preserved-set checks. The shared GPU lock is checked for absence but is not treated as a forbidden historical identity.

- [ ] **Step 4: Bind authorization rejection to the closed preflight evidence**

After parsing and schema-validating `prior_a11_attempts`, replace the old one-literal consumed-owner branch with:

```powershell
$PriorOwners = @($Evidence.prior_a11_attempts.attempts | ForEach-Object {
    [string]$_.owner_authorization_id
})
if ($OwnerAuthorizationId -cin $PriorOwners) {
    throw 'A11 prior owner authorization cannot be reused'
}
```

This is evidence-derived and still rejects both exact consumed values. Do not create a default authorization or read one from the environment.

- [ ] **Step 5: Wire the preserved records into orchestration before the first write**

Change the campaign call to:

```powershell
Test-A11PhaseDestinationsAbsent `
    -Identities @($Calibration, $Validation) `
    -PriorAttempts @($RawPreflight.prior_a11_attempts.attempts) `
    -OwnerAuthorizationId $AuthorizationId | Out-Null
```

Every campaign test stub for `Resolve-A11Worktree` must now return a `prior_a11_attempts.attempts` value, and every direct destination test must pass the new parameters. Preserve the existing event prefix:

```python
assert events[:6] == [
    "preflight",
    "identity:calibration",
    "identity:validation",
    "destinations",
    "init:calibration",
    "build:calibration",
]
```

Extend `test_campaign_destination_failure_precedes_initialization_and_writes_nothing` so the injected preserved-ID collision fails with no marker, no Docker call, no initialized directory, and one surfaced error.

- [ ] **Step 6: Run identity/destination/orchestration GREEN**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py -k 'authorization or destination or phase_identities or campaign_orders or campaign_destination or calibration_failure or stage_failure or closure_write or build_failure'
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
$Changed=@(git status --porcelain=v1 --untracked-files=all | ForEach-Object { $_.Substring(3).Replace('\','/') })
$Allowed=@('docker/wave0.Dockerfile','scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')
if (@($Changed | Where-Object { $_ -cnotin $Allowed }).Count -ne 0) { throw 'implementation scope expanded' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging changed during TDD' }
```

Expected: PASS, and all failures occur before initialization or close once after an initialized normal stage failure.

---

### Task 6: Verify, independently review, preserve, commit once, and stop before runtime

**Files:**
- Stage and commit only: `docker/wave0.Dockerfile`
- Stage and commit only: `scripts/run_wave0_a11.ps1`
- Stage and commit only: `tests/gates/test_wave0_a11_launcher.py`
- Historical and A11 runtime evidence: read-only

**Interfaces:**
- Consumes: Tasks 1–5, their RED/GREEN transcript, and the immutable entry hashes
- Produces: one reviewed implementation commit eligible only for a later owner runtime review

- [ ] **Step 1: Run the focused launcher and related CPU suites**

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider `
  tests/cli/test_cli.py `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/models/test_assets.py `
  tests/probes/test_model_contract.py `
  tests/probes/test_training_feasibility.py `
  tests/gates/test_wave0_a11_launcher.py
```

These cover the original A11 calibration/statistical, model, feasibility, orchestration, and receipt-validator boundaries. Expected: all pass without Docker, GPU, network, or model execution.

- [ ] **Step 2: Run the complete CPU, format, lint, lock, diff, and parser gates**

```powershell
uv run pytest -q -p no:cacheprovider
uvx --offline --python .venv\Scripts\python.exe black --check tests/gates/test_wave0_a11_launcher.py
uvx --offline --python .venv\Scripts\python.exe ruff check tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check

pwsh -NoProfile -NonInteractive -Command '$t=$null;$e=$null;[Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e)|Out-Null;if($e.Count-ne 0){throw ($e.Message-join "; ")}'
powershell -NoProfile -NonInteractive -Command '$t=$null;$e=$null;[Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e)|Out-Null;if($e.Count-ne 0){throw ($e.Message-join "; ")}'
```

Require all exit codes zero. Confirm no `__pycache__`, `.pyc`, or `.pytest_cache` was created; if a tool violates the configured no-cache boundary, stop and report the exact generated paths rather than broad cleanup.

- [ ] **Step 3: Verify exact uncommitted scope and conduct independent Critical/Important review**

```powershell
$Allowed=@('docker/wave0.Dockerfile','scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')
$Tracked=@(git diff --name-only)
$Untracked=@(git ls-files --others --exclude-standard)
$Candidate=@($Tracked + $Untracked | Sort-Object -Unique)
if ($Candidate.Count -ne 3 -or @($Candidate | Where-Object { $_ -cnotin $Allowed }).Count -ne 0) { throw 'candidate scope mismatch' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty before review' }
```

Use `requesting-code-review` with an independent reviewer. Review the approved design, this plan, and the three-file diff line by line. Require Critical=0 and Important=0, specifically checking:

- typed list behavior for zero/one/multiple errors under StrictMode and unchanged 78–82 order/schema/no-clobber;
- closure publication error is surfaced once with no retry, repair, validation, or cleanup;
- exactly two command-local literal timeouts and no dependency/index/cache/base/lock/build-label change;
- exact two run roots, one old image, two old lease-history files, five attempt-2 file records, and state-specific closed schemas;
- `steven001` occurs only in attempt 2 registered identity evidence and both consumed authorizations are rejected;
- new calibration and validation IDs/tags/paths/authorization are distinct from both attempts and each other before initialization;
- fixed historical counts/digests and eight A10 hashes remain exact;
- no changed model/statistical/cohort/metric/threshold/ceiling/schema/GPU/lease/phase/Wave 1 behavior.

For each Critical or Important finding, first add a focused failing test and observe RED, then make the minimum allowlisted correction and observe GREEN. Rerun Steps 1–3 after every correction. A required fourth file is a hard stop for owner review.

- [ ] **Step 4: Repeat the full read-only preservation gate against the candidate**

Extract the candidate's read-only inventory functions and assert the fixed values directly:

```powershell
$ArtifactRoot='D:\vision-active-learning-loop-artifacts\wave0'
$Script=(Resolve-Path 'scripts/run_wave0_a11.ps1').Path
$Tokens=$null;$Errors=$null
$Ast=[Management.Automation.Language.Parser]::ParseFile($Script,[ref]$Tokens,[ref]$Errors)
if($Errors.Count-ne 0){throw ($Errors.Message-join '; ')}
foreach($Name in @(
    'Get-A11JsonSha256','Get-A11HistoricalArtifactInventory',
    'Get-A11HistoricalImageInventory','Invoke-A11Native',
    'Test-A11PathEntryPresent','Get-A11RegisteredAttemptPaths',
    'Get-A11PriorAttemptInventory','Get-A11ActiveLeasePaths'
)){
    $Match=@($Ast.FindAll({param($Node)$Node-is [Management.Automation.Language.FunctionDefinitionAst]-and $Node.Name-eq $Name},$true))
    if($Match.Count-ne 1){throw "AST mismatch: $Name"}
    Invoke-Expression $Match[0].Extent.Text
}
$Historical=Get-A11HistoricalArtifactInventory -ArtifactRoot $ArtifactRoot
$Images=Get-A11HistoricalImageInventory
$Prior=Get-A11PriorAttemptInventory -ArtifactRoot $ArtifactRoot
if(@($Historical.records).Count-ne 64306-or $Historical.sha256-cne 'e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95'){throw 'historical artifact drift'}
if(@($Images.records).Count-ne 21-or $Images.sha256-cne '9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f'){throw 'historical image drift'}
if(@($Prior.attempts).Count-ne 2){throw 'prior attempt cardinality drift'}
if([int]$Prior.attempts[0].run_file_count-ne 48-or [string]$Prior.attempts[0].run_inventory_sha256-cne 'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b'){throw 'attempt 1 drift'}
if([int]$Prior.attempts[1].run_file_count-ne 5-or [string]$Prior.attempts[1].run_inventory_sha256-cne '8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b'){throw 'attempt 2 drift'}
if([string]$Prior.attempts[0].historical_preservation_sha256-cne '927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d'){throw 'attempt 1 historical record drift'}
if([string]$Prior.attempts[0].released_lease_sha256-cne '146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322'){throw 'attempt 1 released lease drift'}
if([string]$Prior.attempts[0].release_record_sha256-cne '35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060'){throw 'attempt 1 release record drift'}
if([string]$Prior.attempts[0].image_id-cne 'sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5'){throw 'attempt 1 image drift'}
if([string]$Prior.attempts[1].owner_authorization_id-cne 'steven001'){throw 'attempt 2 authorization drift'}
if(@($Prior.image_tags).Count-ne 1-or @($Prior.lease_names).Count-ne 2-or $Prior.links_absent-cne $true){throw 'A11 root inventory drift'}
if(@(Get-A11ActiveLeasePaths -LeaseRoot (Join-Path $ArtifactRoot 'leases')).Count-ne 0){throw 'active A11 lease exists'}

$FixedA10=[ordered]@{
 'a7-runs/wave0-a7-20260827T034653088Z/wave0/receipts/environment.json'='7fc82adaa6053a1d6a9617410b27fa5200882d7c99758567bef2c60c8a704e8f'
 'a7-runs/wave0-a7-20260827T034653088Z/wave0/receipts/model-assets.json'='c1e1620fdaff57e3fc4424a393d925b194301f866e3215089303ec3ad8500483'
 'a7-runs/wave0-a7-20260827T034653088Z/wave0/receipts/model-contract.json'='1258c45e5b8b672ca81cc8e2b5af9d955bb22eece3b1aabcf0485174c1a706c0'
 'a7-runs/wave0-a7-20260827T034653088Z/a7/aggregate/receipt.json'='f4a6f0f3fd2cc54f319e65141fa1b0a0367a6e14e2baa0df58268b051270251f'
 'a7-runs/wave0-a7-20260827T034653088Z/audit/40-campaign-result.json'='3f10fbfe8bf33c89fddb71c71e58457f738fa92d933ad05115fa1e66e3126239'
 'a7-runs/wave0-a7-20260827T034653088Z/audit/41-campaign-file-manifest.json'='55f78146f201d090807fcc62a836ec9db82604e3a878ca2323de85edda85f6e2'
 'a7-runs/wave0-a7-20260827T034653088Z/audit/30-historical-preservation.json'='93c9093efebfe7c78a9cf6ae6a10f264b52271aee434236a71d68801b9e0ad3f'
 'a7-runs/wave0-a7-20260827T034653088Z/audit/51-campaign-closure-manifest.json'='3f3c1e548d0454bc81c44e8130e710e7e8d0b47264f69afdb96560d7fbc92162'
}
foreach($Relative in $FixedA10.Keys){
    $Path=Join-Path $ArtifactRoot $Relative
    if(-not(Test-Path -LiteralPath $Path -PathType Leaf)-or (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()-cne $FixedA10[$Relative]){throw "A10 drift: $Relative"}
}

$ProjectContainers=@(docker ps --all --format '{{.ID}}' | ForEach-Object {
    $ContainerId=$_;$ImageId=(docker inspect --format '{{.Image}}' -- $ContainerId).Trim()
    $RepoTagsJson=(docker image inspect --format '{{json .RepoTags}}' -- $ImageId).Trim()
    $RepoTags=if($RepoTagsJson-ceq 'null'){@()}else{@($RepoTagsJson|ConvertFrom-Json)}
    if(@($RepoTags|Where-Object{$_-like 'vision-active-learning-loop:*'}).Count-gt 0){"$ContainerId|$ImageId"}
})
if($ProjectContainers.Count-ne 0){throw 'project container exists'}
if((docker info --format '{{.OSType}}|{{.ServerVersion}}').Trim()-cnotmatch '^linux\|.+$'){throw 'Docker Linux engine unavailable'}
if(Test-Path Env:VAL_DATA_ROOT){throw 'VAL_DATA_ROOT must remain unset'}
```

Additionally require the never-published paths and attempt-2 payload remain absent:

```powershell
$Run1='D:\vision-active-learning-loop-artifacts\wave0\a11-runs\wave0-a11-calibration-20260828T045848083Z-b9917463'
$Run2='D:\vision-active-learning-loop-artifacts\wave0\a11-runs\wave0-a11-calibration-20260828T114911289Z-fe8b7000'
$Forbidden1=@('78-failure-diagnostic.json','80-campaign-result.json','81-campaign-file-manifest.json','82-campaign-closure.json')
$Forbidden2=@('78-failure-diagnostic.json','79-historical-preservation-final.json','80-campaign-result.json','81-campaign-file-manifest.json','82-campaign-closure.json')
if (@($Forbidden1 | Where-Object { Test-Path -LiteralPath (Join-Path $Run1 "audit\$_") }).Count -ne 0) { throw 'attempt 1 was backfilled' }
if (@($Forbidden2 | Where-Object { Test-Path -LiteralPath (Join-Path $Run2 "audit\$_") }).Count -ne 0) { throw 'attempt 2 was backfilled' }
if (@(Get-ChildItem -LiteralPath (Join-Path $Run2 'wave0') -File -Recurse -Force).Count -ne 0) { throw 'attempt 2 payload appeared' }
if (Test-Path -LiteralPath 'D:\vision-active-learning-loop-artifacts\wave0\a11-runs\wave0-a11-validation-20260828T114911296Z-3107aff0') { throw 'attempt 2 validation appeared' }
if (Test-Path -LiteralPath 'D:\vision-active-learning-loop-artifacts\wave0\leases\GPU-7639cc81-2a55-164e-e5be-c5cd71752a63.json') { throw 'active A11 lease exists' }
```

Require both run digests, historical counts/digests, old image ID, exact image/lease/run inventories, Docker Linux health, no project container, unset `VAL_DATA_ROOT`, and all eight A10 hashes equal the Task 1 transcript. The canonical worktree must remain clean; the linked worktree may differ only at the three allowlisted paths.

- [ ] **Step 5: Create the one append-only implementation commit**

Only after all gates and the independent review pass:

```powershell
$PlanCommit=(git rev-parse HEAD).Trim()
if ((git rev-parse "$PlanCommit^").Trim() -cne 'cca4d97380d9b35977c034f3ad1bb46bacf2a9ab') { throw 'plan lineage changed' }
$env:GIT_AUTHOR_NAME='kuotunyu'
$env:GIT_AUTHOR_EMAIL='61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME='kuotunyu'
$env:GIT_COMMITTER_EMAIL='61350295+kuotunyu@users.noreply.github.com'
git add -- docker/wave0.Dockerfile scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
$Staged=@(git diff --cached --name-only)
$Allowed=@('docker/wave0.Dockerfile','scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')
if ($Staged.Count -ne 3 -or @($Staged | Where-Object { $_ -cnotin $Allowed }).Count -ne 0) { throw 'staged scope mismatch' }
git diff --cached --check
git commit -m 'fix: recover A11 second failure boundaries'
```

- [ ] **Step 6: Verify the committed candidate and stop before runtime**

Require the implementation parent to equal `$PlanCommit`, exact author/committer identity, exact three-file diff, and clean linked/canonical worktrees:

```powershell
$Implementation=(git rev-parse HEAD).Trim()
if ((git rev-parse "$Implementation^").Trim() -cne $PlanCommit) { throw 'implementation parent mismatch' }
if ((git show -s --format='%an <%ae>|%cn <%ce>' $Implementation).Trim() -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>|kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'commit identity mismatch' }
$Paths=@(git diff-tree --no-commit-id --name-only -r $Implementation)
if ($Paths.Count -ne 3 -or @($Paths | Where-Object { $_ -cnotin @('docker/wave0.Dockerfile','scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py') }).Count -ne 0) { throw 'implementation commit scope mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree is not clean' }
```

From the committed tree, rerun the two PowerShell parser commands, `uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py`, and the complete Step 4 preservation block in this task. Report design, plan, and implementation SHAs; RED/GREEN selectors; focused/full test counts; Black/Ruff/lock/diff/parser results; both attempt digests; historical/image/lease/container/Git evidence; and Critical=0/Important=0.

Do not invoke the launcher, build an image, create a run, or accept `steven001` again. Stop with status “implementation eligible for separate runtime review”; A11 is not passed and Wave 1 is not started.
