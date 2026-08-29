# Wave 0 A11 Preserved-Inventory Digest Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for Tasks 2-5, superpowers:requesting-code-review in Task 6, and superpowers:verification-before-completion before the implementation commit and diagnostic terminal. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct the unreproducible fifth-attempt inventory digest from an append-only specification, re-prove the complete A11 entry envelope, and then finish the already approved registry-backed dependency-transport recovery without modifying historical evidence or starting a formal runtime attempt.

**Architecture:** This plan is a narrow normative overlay on the approved runtime-transport plan at `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`. It replaces only the fifth-attempt aggregate digest, the Task 1 proof that consumes it, and the Git lineage made obsolete by the recovery design; all other runtime-transport requirements remain binding. A closed canonical run-inventory function uses ordinal POSIX paths and an ordered compact JSON record array, while an independent encoder binds the fifth attempt to the approved 1,283-byte test vector before any implementation path changes.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker Engine 29.6.1 / BuildKit; exact uv 0.8.15; Git.

## Global Constraints

- The approved digest-recovery design is `docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery-design.md` at commit `2db13d302da97a241daeaba3578cd9cec1c8073b`.
- This plan commit must be the direct child of that design commit and add only this plan file.
- The prior runtime-transport design, plan, and diagnostic-root erratum remain immutable at `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`, `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`, and `101bb79369399cc3947f1c667f0a11988f916638`.
- The implementation must be one append-only commit, the direct child of this plan commit, changing exactly the seven implementation paths listed below. Tasks 2-5 do not create intermediate commits.
- Author and committer must both be exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, clean evidence, push, merge, tag, release, or modify another repository.
- The artifact root `D:\vision-active-learning-loop-artifacts\wave0` is read-only. A mismatch is a stop condition, never a repair instruction.
- Do not invoke `scripts/run_wave0_a11.ps1`, generate or guess an `OwnerAuthorizationId`, acquire a GPU lease, initialize a model, create a calibration or validation identity, access RDD, or start Wave 1.
- Consumed owners `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`, and `steven004` remain immutable evidence. Test-only owner values must contain `TEST`.
- The only Docker invocation permitted to execute a stage is the single dependency-only diagnostic in Task 7. Tasks 5-6 may call `docker buildx build --check`, which validates the Dockerfile without executing or exporting a stage.
- Keep Python `3.12.11`, uv `0.8.15`, CUDA `12.6`, base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`, every dependency version, and `uv.lock` byte-identical at SHA-256 `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`.
- Keep model, receipt, statistical, threshold, replica, split, acquisition, data-firewall, lease, validation, and Wave 1 contracts unchanged.
- CPU tests must set `PYTHONDONTWRITEBYTECODE=1` and pass `-p no:cacheprovider`; they may not use network, Docker, GPU, model loading, CUDA, or the external artifact root.
- The dependency diagnostic writes only beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`, outside the repository and artifact baseline. It has no owner ID, run ID, image export, project container, model process, or statistical meaning.
- The superseded digest `b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448` may appear only in recovery documents and negative tests. Production registry data must use `e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64`.

## Normative overlay

Everything in the runtime-transport plan at commit
`e31fc0c10fe34b480f7b2ee3d12a2e55530c6350` remains binding except these exact
replacements:

| Contract | Superseded value | Effective value |
| --- | --- | --- |
| Attempt-5 run inventory SHA-256 | `b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448` | `e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64` |
| Implementation parent | diagnostic-root erratum `101bb79369399cc3947f1c667f0a11988f916638` | this digest-recovery plan commit |
| Implementation grandparent | runtime-transport plan `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350` | digest-recovery design `2db13d302da97a241daeaba3578cd9cec1c8073b` |
| Diagnostic evidence parent | artifact-root child | `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics` |

The exact attempt-5 files, directory names, counts, identities, latest-write
timestamp, and absence rules are unchanged. The corrected digest is derived
from those unchanged records; it is not a newly discovered evidence state.

## Frozen preservation envelope

| Ordinal | State | Calibration run | Owner | Source | Files | Dirs | Inventory SHA-256 |
| ---: | --- | --- | --- | --- | ---: | ---: | --- |
| 1 | `launcher-stage-failure` | `wave0-a11-calibration-20260828T045848083Z-b9917463` | `OWNER-A11-RUNTIME-20260828-01` | `2622e402e4f536b94326ac34f9b20c90b513002b` | 48 | 18 | `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b` |
| 2 | `image-build-timeout` | `wave0-a11-calibration-20260828T114911289Z-fe8b7000` | `steven001` | `1445a90b799b6306d6c1f7abc94b4a201afe5dc6` | 5 | 5 | `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b` |
| 3 | `foundation-stream-contract-failure` | `wave0-a11-calibration-20260828T172921151Z-a0f55fa1` | `steven002` | `ff5cfac5820415662e608886f1a10d7892f3ee00` | 60 | 18 | `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2` |
| 4 | `aggregate-cache-inventory-contract-failure` | `wave0-a11-calibration-20260829T050706309Z-f5a0129e` | `steven003` | `77f8eecb3b8c0f471a4e980269187ac02a3b9ebc` | 137 | 30 | `f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717` |
| 5 | `dependency-transport-build-failure` | `wave0-a11-calibration-20260829T123151657Z-bf516632` | `steven004` | `ed6f157c7cbd545895b9d047f6e094968a1f9d94` | 10 | 5 | `e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64` |

All attempts bind specification `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
and original A11 plan `7dbd3a7576ea76beccfc64f748c4e495259ea89b`.
The fifth peer run remains
`wave0-a11-validation-20260829T123151664Z-7af53ca8`, and its latest write remains
`2026-08-29T13:39:47.0148945Z`.

The external envelope remains exactly:

```text
five calibration run roots
zero validation run roots
three A11 image tags
six A11 lease-history files
zero active GPU lease files
zero vision-active-learning-loop containers in any state
zero numeric CUDA compute processes
64,306 historical files / e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
21 historical images / 9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
```

The three exact A11 images are:

```text
vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463
  sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5
vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1
  sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd
vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e
  sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e
```

The release-record/released-lease SHA-256 pairs for ordinals 1, 3, and 4 are:

```text
ordinal 1  35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060 / 146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322
ordinal 3  72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93 / a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f
ordinal 4  aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1 / b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c
```

## Implementation file map and allowlist

- Create `configs/a11/preserved-attempts.json`: five immutable declarative attempt records; ordinal 5 carries the corrected digest.
- Create `schemas/a11-preserved-attempts.schema.json`: closed draft-2020-12 registry schema.
- Create `scripts/run_uv_sync_with_retries.py`: bounded dependency-build-only transport wrapper.
- Modify `scripts/run_wave0_a11.ps1`: canonical inventory encoder, registry loader/verifier, registry digest guard, and unchanged single-build campaign path.
- Modify `docker/wave0.Dockerfile`: named dependency stage, exact wrapper calls, and two locked BuildKit uv cache mounts.
- Modify `tests/gates/test_wave0_a11_launcher.py`: canonical-vector, registry, verifier, Dockerfile, and launcher TDD.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD.

No other tracked path may change. In particular, do not edit any existing design
or plan, `pyproject.toml`, `uv.lock`, `configs/environment/wave0-lock.json`,
receipt schema, `src/`, statistical code, or model code.

---

### Task 1: Re-prove corrected lineage, canonical vector, preservation, and baseline

**Files:**
- Modify: none
- Read: Git topology, the committed recovery design, all five run roots, image/lease/historical inventories, Docker/GPU state, and the complete test suite

**Interfaces:**
- Consumes: recovery design commit `2db13d302da97a241daeaba3578cd9cec1c8073b` and its single embedded JSON record vector
- Produces: one read-only entry report whose frozen fields are compared again in Tasks 6 and 7

- [ ] **Step 1: Prove the plan lineage, identities, and worktree isolation**

Run from the linked worktree:

```powershell
$ErrorActionPreference = 'Stop'
$Design = '2db13d302da97a241daeaba3578cd9cec1c8073b'
$Erratum = '101bb79369399cc3947f1c667f0a11988f916638'
$RuntimePlan = 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350'
$RuntimeDesign = 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery.md'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery-design.md'
$Plan = (git rev-parse HEAD).Trim()
if ((git rev-parse "$Plan^").Trim() -cne $Design) { throw 'recovery plan parent mismatch' }
if ((git rev-parse "$Design^").Trim() -cne $Erratum) { throw 'recovery design parent mismatch' }
if ((git rev-parse "$Erratum^").Trim() -cne $RuntimePlan) { throw 'erratum parent mismatch' }
if ((git rev-parse "$RuntimePlan^").Trim() -cne $RuntimeDesign) { throw 'runtime plan parent mismatch' }
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'branch mismatch' }
$ExpectedIdentity = 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>|kuotunyu <61350295+kuotunyu@users.noreply.github.com>'
foreach ($Pair in @(@($Design, $DesignPath), @($Plan, $PlanPath))) {
    $Paths = @(git diff-tree --no-commit-id --name-only -r $Pair[0])
    if ($Paths.Count -ne 1 -or $Paths[0] -cne $Pair[1]) { throw 'recovery document scope mismatch' }
    if ((git show -s --format='%an <%ae>|%cn <%ce>' $Pair[0]).Trim() -cne $ExpectedIdentity) {
        throw 'recovery document identity mismatch'
    }
}
$Canonical = '<repo>'
if (@(git status --porcelain=v1).Count -ne 0) { throw 'linked worktree dirty' }
if (@(git -C $Canonical status --porcelain=v1).Count -ne 0) { throw 'canonical worktree dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }
$LinkedGit = [IO.Path]::GetFullPath((git rev-parse --git-dir).Trim(), (Get-Location).Path)
$LinkedCommon = [IO.Path]::GetFullPath((git rev-parse --git-common-dir).Trim(), (Get-Location).Path)
$CanonicalGit = [IO.Path]::GetFullPath((git -C $Canonical rev-parse --git-dir).Trim(), $Canonical)
$CanonicalCommon = [IO.Path]::GetFullPath((git -C $Canonical rev-parse --git-common-dir).Trim(), $Canonical)
if ($LinkedGit -ceq $CanonicalGit -or $LinkedCommon -cne $CanonicalCommon) {
    throw 'linked worktree isolation mismatch'
}
if ((Get-FileHash -LiteralPath 'uv.lock' -Algorithm SHA256).Hash.ToLowerInvariant() -cne
    '530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93') {
    throw 'uv.lock changed'
}
```

- [ ] **Step 2: Prove the committed canonical test vector independently**

Read the single `json` fence from the committed recovery design, not from the
external artifact. Validate exact property order and compute two independent
encodings:

```powershell
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery-design.md'
$Text = [IO.File]::ReadAllText((Join-Path (Get-Location) $DesignPath))
$Blocks = [regex]::Matches($Text, '(?s)```json\r?\n(.*?)\r?\n```')
if ($Blocks.Count -ne 1) { throw 'recovery design vector cardinality mismatch' }
$ExpectedRecords = @($Blocks[0].Groups[1].Value | ConvertFrom-Json)
if ($ExpectedRecords.Count -ne 10) { throw 'attempt-5 vector count mismatch' }
foreach ($Record in $ExpectedRecords) {
    if ((@($Record.PSObject.Properties.Name) -join ',') -cne 'path,size,sha256') {
        throw 'attempt-5 vector property order mismatch'
    }
}
$ProductionJson = ConvertTo-Json -InputObject @($ExpectedRecords) -Depth 8 -Compress
$ManualRows = @($ExpectedRecords | ForEach-Object {
    '{"path":"' + $_.path + '","size":' +
    ([long]$_.size).ToString([Globalization.CultureInfo]::InvariantCulture) +
    ',"sha256":"' + $_.sha256 + '"}'
})
$IndependentJson = '[' + [string]::Join(',', $ManualRows) + ']'
if ($ProductionJson -cne $IndependentJson) { throw 'canonical encoders disagree' }
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($ProductionJson)
$Digest = [Convert]::ToHexString(
    [Security.Cryptography.SHA256]::HashData($Bytes)
).ToLowerInvariant()
if ($Bytes.Count -ne 1283 -or
    $Digest -cne 'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64') {
    throw 'canonical test vector mismatch'
}
```

- [ ] **Step 3: Rehash all five runs with the canonical production convention**

Use an ordinal path dictionary so neither filesystem enumeration order nor
current culture controls the aggregate:

```powershell
function Get-RecoveryRunInventory {
    param([Parameter(Mandatory=$true)][string]$Path)
    $Root = [IO.Path]::GetFullPath($Path)
    $RootItem = Get-Item -LiteralPath $Root -Force -ErrorAction Stop
    if (-not $RootItem.PSIsContainer -or
        ($RootItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw "invalid run root: $Root"
    }
    $Items = @(Get-ChildItem -LiteralPath $Root -Recurse -Force)
    if (@($Items | Where-Object {
        $_.Attributes -band [IO.FileAttributes]::ReparsePoint
    }).Count -ne 0) { throw "run contains a link: $Root" }
    $ByPath = [Collections.Generic.Dictionary[string,object]]::new(
        [StringComparer]::Ordinal
    )
    foreach ($File in @($Items | Where-Object { -not $_.PSIsContainer })) {
        $Relative = $File.FullName.Substring($Root.Length + 1).Replace('\', '/')
        $Record = [pscustomobject][ordered]@{
            path = $Relative
            size = [long]$File.Length
            sha256 = (Get-FileHash -LiteralPath $File.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
        if (-not $ByPath.TryAdd($Relative, $Record)) { throw 'duplicate ordinal run path' }
    }
    [string[]]$Paths = @($ByPath.Keys)
    [Array]::Sort($Paths, [StringComparer]::Ordinal)
    $Records = @($Paths | ForEach-Object { $ByPath[$_] })
    $Json = ConvertTo-Json -InputObject @($Records) -Depth 8 -Compress
    $Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Json)
    [string[]]$DirectoryNames = @($Items | Where-Object { $_.PSIsContainer } | ForEach-Object {
        $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
    })
    [Array]::Sort($DirectoryNames, [StringComparer]::Ordinal)
    $LatestFiles = @($Items | Where-Object { -not $_.PSIsContainer } |
        Sort-Object LastWriteTimeUtc | Select-Object -Last 1)
    if ($LatestFiles.Count -ne 1) { throw "run has no regular file: $Root" }
    return [pscustomobject][ordered]@{
        records = $Records
        directory_names = $DirectoryNames
        file_count = $Records.Count
        directory_count = $DirectoryNames.Count
        canonical_byte_count = $Bytes.Count
        sha256 = [Convert]::ToHexString(
            [Security.Cryptography.SHA256]::HashData($Bytes)
        ).ToLowerInvariant()
        latest_write_utc = $LatestFiles[0].LastWriteTimeUtc.ToString('o')
        links_absent = $true
    }
}

$ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
$Expected = [ordered]@{
    'wave0-a11-calibration-20260828T045848083Z-b9917463' = @(48,18,'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b','2026-08-28T06:06:15.8277603Z')
    'wave0-a11-calibration-20260828T114911289Z-fe8b7000' = @(5,5,'8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b','2026-08-28T12:17:12.8122776Z')
    'wave0-a11-calibration-20260828T172921151Z-a0f55fa1' = @(60,18,'628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2','2026-08-28T18:10:34.6753199Z')
    'wave0-a11-calibration-20260829T050706309Z-f5a0129e' = @(137,30,'f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717','2026-08-29T06:13:25.1659510Z')
    'wave0-a11-calibration-20260829T123151657Z-bf516632' = @(10,5,'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64','2026-08-29T13:39:47.0148945Z')
}
$RunRoot = Join-Path $ArtifactRoot 'a11-runs'
$ObservedNames = @(Get-ChildItem -LiteralPath $RunRoot -Directory -Force |
    Sort-Object Name -CaseSensitive | ForEach-Object Name)
if (($ObservedNames | ConvertTo-Json -Compress) -cne
    (@($Expected.Keys) | ConvertTo-Json -Compress)) { throw 'A11 run envelope mismatch' }
foreach ($Name in $Expected.Keys) {
    $Observed = Get-RecoveryRunInventory -Path (Join-Path $RunRoot $Name)
    $Value = $Expected[$Name]
    if ($Observed.file_count -ne $Value[0] -or
        $Observed.directory_count -ne $Value[1] -or
        $Observed.sha256 -cne $Value[2] -or
        $Observed.latest_write_utc -cne $Value[3] -or
        -not $Observed.links_absent) { throw "preserved run mismatch: $Name" }
}
$Attempt5 = Get-RecoveryRunInventory -Path (
    Join-Path $RunRoot 'wave0-a11-calibration-20260829T123151657Z-bf516632'
)
if (($Attempt5.records | ConvertTo-Json -Depth 8 -Compress) -cne
    ($ExpectedRecords | ConvertTo-Json -Depth 8 -Compress)) {
    throw 'attempt-5 exact records mismatch'
}
$ExpectedDirectories = @('audit','wave0','wave0/checkpoints','wave0/model_cache','wave0/receipts')
if (($Attempt5.directory_names | ConvertTo-Json -Compress) -cne
    ($ExpectedDirectories | ConvertTo-Json -Compress)) {
    throw 'attempt-5 exact directory mismatch'
}
```

The function above must be run to completion. Do not add a timeout, sample the
files, reuse an earlier report, or treat progress silence as failure.

- [ ] **Step 4: Re-prove images, leases, historical baselines, Docker, GPU, and diagnostic absence**

Use the exact `Get-A11HistoricalArtifactInventory` and
`Get-A11HistoricalImageInventory` algorithms from committed
`scripts/run_wave0_a11.ps1`; they are read-only and exclude only `a11-runs/*`,
`leases/wave0-a11-*`, and the frozen active-lease name from the historical file
inventory. Require the exact counts and hashes in the frozen envelope above.

Independently require:

```powershell
if ((docker info --format '{{.OSType}}|{{.ServerVersion}}').Trim() -cnotmatch '^linux\|[^|]+$') {
    throw 'Docker Linux engine unavailable'
}
$LeaseRoot = 'D:\vision-active-learning-loop-artifacts\wave0\leases'
$Active = @(Get-ChildItem -LiteralPath $LeaseRoot -File -Force |
    Where-Object { $_.Name -cmatch '^GPU-[A-Za-z0-9-]+\.json$' })
if ($Active.Count -ne 0) { throw 'active lease exists' }
$Compute = @(& nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits |
    Where-Object { $_ -match '^\s*[0-9]+\s*$' })
if ($LASTEXITCODE -ne 0 -or $Compute.Count -ne 0) { throw 'CUDA process gate failed' }
```

Enumerate every container with `docker ps --all --format
'{{.ID}}|{{.Image}}'`; inspect each container's immutable image ID and that
image's `RepoTags`. Require zero containers whose inspected image has a tag
matching `vision-active-learning-loop:*`. Do not trust the display image alone.

Require the A11 run-directory names, three image tag/ID pairs, and six exact
lease-history hashes shown above. Require no validation run root. Require no
`00-identity.json` beneath
`D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`.
The diagnostic parent may be absent; do not create it.

- [ ] **Step 5: Run the complete baseline from the unchanged committed tree**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider
```

Require exit 0 and capture exact passed/skipped counts. Afterwards require both
worktrees clean, staging empty, and no `__pycache__`, `.pyc`, `.pytest_cache`,
runtime artifact, or diagnostic directory inside the repository. Any Task 1
failure is `NO_GO`; stop without editing an implementation path.

---

### Task 2: Add RED canonical-vector, registry, and generic-verifier tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: existing `_invoke_functions(...)` AST adapter and embedded synthetic artifact fixtures
- Produces: test contracts for `Get-A11CanonicalRunInventory`, `Read-A11PreservedAttemptRegistry`, `Assert-A11PreservedAttemptRegistryUnchanged`, and generic `Get-A11PriorAttemptInventory`

- [ ] **Step 1: Add exact recovery and attempt-5 fixtures**

Add these constants beside the existing attempt fixtures:

```python
_REGISTRY = _ROOT / "configs" / "a11" / "preserved-attempts.json"
_REGISTRY_SCHEMA = _ROOT / "schemas" / "a11-preserved-attempts.schema.json"
_TRANSPORT_RUN_ID = "wave0-a11-calibration-20260829T123151657Z-bf516632"
_TRANSPORT_VALIDATION_ID = "wave0-a11-validation-20260829T123151664Z-7af53ca8"
_TRANSPORT_OWNER = "steven004"
_TRANSPORT_SOURCE = "ed6f157c7cbd545895b9d047f6e094968a1f9d94"
_TRANSPORT_RUN_SHA256 = (
    "e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64"
)
_SUPERSEDED_TRANSPORT_RUN_SHA256 = (
    "b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448"
)
_TRANSPORT_CANONICAL_BYTE_COUNT = 1283
_TRANSPORT_LATEST_WRITE = "2026-08-29T13:39:47.0148945Z"
_TRANSPORT_DIRECTORIES = [
    "audit", "wave0", "wave0/checkpoints", "wave0/model_cache", "wave0/receipts"
]
_TRANSPORT_KEY_FILES = [
    ("audit/00-identity.json", 2873, "9fb7f3572e8341af986f24473c2ee66933d17d736b632b95e0c3a64c91e9d67d"),
    ("audit/01-gpu-preflight.json", 125, "de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7"),
    ("audit/10-build.json", 1234, "3ef76de20f776e977f172d2ba9c3277185db693bd3a7fc9949bfe42b39af6f68"),
    ("audit/10-build.stderr.log", 865248, "e53b9598c39343785aea27be4381f1755accb5f91553630af64d1b71712e82c5"),
    ("audit/10-build.stdout.log", 0, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"),
    ("audit/78-failure-diagnostic.json", 766, "cc0e391fdb743dac2c2c80362d690703da08b9ae38c5a8294031ace8bef9c311"),
    ("audit/79-historical-preservation-final.json", 301, "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d"),
    ("audit/80-campaign-result.json", 751, "346b4aa69f8e6c440262f463e4cbb756f39dd1dde0df51124f533093ffe8b651"),
    ("audit/81-campaign-file-manifest.json", 1885, "8be8ee5adadb296d269c5dda0c1827d8ef9ee56d024872aa3ee6e0cb74bbedd6"),
    ("audit/82-campaign-closure.json", 659, "a3ba8ef72165dde8443ac85ffcaaf27b307afd15af10c8a0d347ca7f30cfcaa1"),
]
```

Extend the pure `_prior_attempts()` fixture to five chronological attempts and
five consumed owners. Tests must not read the real artifact root.

- [ ] **Step 2: Write canonical-vector RED tests**

Use synthetic files with bytes reconstructed to match a small independent
fixture and use the exact ten-record vector as a pure serializer fixture. Add
tests with these assertions:

```python
assert observed["canonical_byte_count"] == _TRANSPORT_CANONICAL_BYTE_COUNT
assert observed["sha256"] == _TRANSPORT_RUN_SHA256
assert observed["sha256"] != _SUPERSEDED_TRANSPORT_RUN_SHA256
assert [record["path"] for record in observed["records"]] == sorted(
    (record["path"] for record in observed["records"]), key=lambda value: tuple(map(ord, value))
)
```

Parameterize one mutation at a time for path, size, file SHA, record order,
field order, JSON whitespace, BOM, final newline, rooted path, `.`/`..`, and a
reparse point. Require the closed serializer or expected comparison to reject
each mutation. Switch current culture between `en-US` and `tr-TR` in the
PowerShell adapter and require byte-identical output.

- [ ] **Step 3: Write registry-loader and generic-verifier RED tests**

Require the future registry to have schema version 1, ordinals `[1,2,3,4,5]`,
the five exact owners, and ordinal-5 digest `_TRANSPORT_RUN_SHA256`. Validate it
through PowerShell `Test-Json -SchemaFile`.

Require `Read-A11PreservedAttemptRegistry` to return the registry file SHA and
parsed attempts together and reject missing/link inputs, malformed JSON,
unknown fields, explicit `null`, unknown state, unordered/duplicate ordinals,
and duplicate owner/current/peer/image/destination identities. Require
`Get-A11PriorAttemptInventory` to compare exact records, directories, counts,
latest-write, absence flags, images, releases, and complete external sets for
all five records.

Parameterize rejection of an extra or missing run, image, lease, owner,
destination, key file, directory, replica directory, checkpoint, closure,
success receipt, validation root, release record, and link. Prove all five
consumed owners fail reuse while `OWNER-A11-TEST-FRESH` passes the pure gate.

- [ ] **Step 4: Write registry-digest stability and identity-binding RED tests**

Load a copied registry, change one byte after load, and require
`Assert-A11PreservedAttemptRegistryUnchanged` to fail before a stubbed
`Initialize-A11Phase` writes. Require both preregistered identities and their
synthetic `audit/00-identity.json` to carry the same lowercase 64-hex
`preserved_attempt_registry_sha256`.

- [ ] **Step 5: Run focused RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'canonical_run_inventory or preserved_attempt_registry or prior_attempt or preflight or destination or identity_binding'
```

Require collection success and failures caused only by absent registry/schema/
functions or existing four-attempt hard-coding. Syntax errors, external
artifact access, Docker calls, or GPU calls are invalid RED results.

---

### Task 3: Implement the canonical inventory, registry, and generic verifier

**Files:**
- Create: `configs/a11/preserved-attempts.json`
- Create: `schemas/a11-preserved-attempts.schema.json`
- Modify: `scripts/run_wave0_a11.ps1`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: `Get-A11CanonicalRunInventory -RunRoot <absolute>` and `Read-A11PreservedAttemptRegistry -ArtifactRoot <absolute> [-RegistryPath <absolute>] [-SchemaPath <absolute>]`
- Produces: closed canonical inventory objects; `{schema_version,registry_path,registry_sha256,attempts}`; generic prior-attempt evidence; and `Assert-A11PreservedAttemptRegistryUnchanged -Registry <object> -> $true | throw`

- [ ] **Step 1: Create the exact closed schema and five-record registry**

Create the draft-2020-12 schema from Task 3 Step 1 of the immutable runtime-
transport plan at commit `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`.
That exact block is normative: `additionalProperties:false` at every object,
the five-state enum, required common fields, and state-dependent `image` and
`release` presence. Do not add a recovery-only schema property.

Create the registry as two-space UTF-8 JSON with LF and one final newline. Migrate
ordinals 1-4 from the exact committed fixtures named in that plan, never from
the live artifact root. Create ordinal 5 from the exact record vector in the
approved recovery design, with:

```json
{
  "ordinal": 5,
  "state": "dependency-transport-build-failure",
  "run_id": "wave0-a11-calibration-20260829T123151657Z-bf516632",
  "peer_run_id": "wave0-a11-validation-20260829T123151664Z-7af53ca8",
  "source_commit": "ed6f157c7cbd545895b9d047f6e094968a1f9d94",
  "specification_commit": "b59b0d4407b98b460f6166ea7288ba6021dc7a78",
  "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
  "owner_authorization_id": "steven004",
  "run_file_count": 10,
  "run_directory_count": 5,
  "run_inventory_sha256": "e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64",
  "latest_write_utc": "2026-08-29T13:39:47.0148945Z",
  "success_receipt_present": false,
  "validation_present": false,
  "links_absent": true
}
```

The object above shows every corrected scalar but is not a reduced schema: add
the exact `registered_run_ids`, two registered image tags, sixteen registered
destinations, five directory names, ten `key_file_records`, five closure names,
and empty replica/checkpoint lists frozen in the recovery design and original
runtime-transport plan. Attempt 5 has no `image` or `release` property.

- [ ] **Step 2: Implement the closed canonical run inventory**

Add `Get-A11CanonicalRunInventory` before `Get-A11PriorAttemptInventory`.
Implement exactly the algorithm in Task 1 Step 3, with parameter
`[string]$RunRoot`, ordinal dictionary/sort, ordered `path,size,sha256` records,
compact JSON, strict UTF-8 without BOM/newline, byte count, lowercase digest,
directory names, latest write, and link rejection. Return only:

```powershell
[pscustomobject][ordered]@{
    records = @($Records)
    directory_names = @($DirectoryNames)
    file_count = $Records.Count
    directory_count = $DirectoryNames.Count
    canonical_byte_count = $Bytes.Count
    sha256 = $Digest
    latest_write_utc = $LatestWrite
    links_absent = $true
}
```

Do not accept caller-supplied expected values, state, owner, or ordinal. The
function observes one root and returns evidence; the generic comparer owns all
expectations.

- [ ] **Step 3: Implement the registry loader and byte-stability guard**

`Read-A11PreservedAttemptRegistry` must reject linked/missing inputs, a UTF-8
BOM, invalid UTF-8, schema failure, alternate property sets, duplicate
identities, path escapes, rooted/backslash paths, unordered ordinals, and
unknown state. Use `ConvertFrom-Json -DateKind String` and retain the SHA-256 of
the exact registry bytes. Return only:

```powershell
[pscustomobject][ordered]@{
    schema_version = 1
    registry_path = [IO.Path]::GetFullPath($RegistryPath)
    registry_sha256 = $RegistryDigest
    attempts = @($Document.attempts)
}
```

`Assert-A11PreservedAttemptRegistryUnchanged` rehashes `registry_path`, compares
it case-sensitively to `registry_sha256`, and returns `$true` or throws.

- [ ] **Step 4: Replace attempt-specific PowerShell branches with one generic comparer**

`Get-A11PriorAttemptInventory` must accept an optional loaded registry, call
`Get-A11CanonicalRunInventory` once per declared run, and compare every field
with an error containing the ordinal and field name. It must validate current
and peer identity content, expected absences/presences, optional image/release
objects, and the complete actual-versus-registered run/image/lease/owner/
destination sets. Use `StringComparer.Ordinal` for relative POSIX records and
`StringComparer.OrdinalIgnoreCase` only for Windows containment and absolute
destination collision checks.

Remove executable attempt-specific run IDs, owners, image IDs, file hashes,
fixed `ValidateCount(4,4)`, and cardinality branches. Keep those values only in
the registry and tests.

- [ ] **Step 5: Bind the registry digest through the existing preflight/write boundary**

Return `registry_path` and `registry_sha256` in `prior_a11_attempts`. Add mandatory
`[string]$PreservedAttemptRegistrySha256` to `New-A11PhaseIdentity`, validate
lowercase 64-hex, and store `preserved_attempt_registry_sha256` on both phase
identities. Immediately after `Confirm-A11ProtectedGit` and before each
`Initialize-A11Phase`, run:

```powershell
Assert-A11PreservedAttemptRegistryUnchanged `
    -Registry $RawPreflight.prior_a11_attempts | Out-Null
```

Make `Test-A11PhaseDestinationsAbsent` accept mandatory `ArtifactRoot`, resolve
every registry-relative destination beneath it, reject alternate roots and
case-insensitive aliases, and retain the current no-clobber ordering.

- [ ] **Step 6: Run registry GREEN and full launcher tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'canonical_run_inventory or preserved_attempt_registry or prior_attempt or preflight or destination or identity_binding'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Require both exit 0 without real Docker, GPU, network, model, or artifact access.

---

### Task 4: Add RED bounded uv transport-wrapper tests

**Files:**
- Create: `tests/scripts/test_run_uv_sync_with_retries.py`
- Test: `tests/scripts/test_run_uv_sync_with_retries.py`

**Interfaces:**
- Consumes: `run_uv_sync(argv, *, runner, sleeper, environ, stdout, stderr) -> int` and `main(argv: Sequence[str] | None = None) -> int`
- Produces: exact retry cardinality, classification, byte-stream, environment, and CLI contracts used by Task 5

- [ ] **Step 1: Create isolated injected fixtures**

Import the future script by file path; do not edit `pyproject.toml`. Use
`subprocess.CompletedProcess[bytes]`, `io.BytesIO`, a fake runner that records
the exact command/environment, and a fake sleeper that records delays.

- [ ] **Step 2: Specify success, retry, and exhaustion**

Parameterize exactly these case-sensitive stderr signatures:

```python
RETRYABLE = [
    b"error decoding response body",
    b"request or response body error",
    b"error reading a body from connection",
    b"stream error received:",
    b"Failed to download distribution due to network timeout",
    b"connection reset by peer",
]
```

Require first-attempt success to use one process/no sleep. Require transport
failure then success to use two processes and `[5.0]`; two transport failures
then success to use three and `[5.0,10.0]`; three failures return the third exit
code. Emit `A11_UV_SYNC_ATTEMPT n/3` once before every child.

- [ ] **Step 3: Specify fail-closed and CLI cases**

Require one process/no sleep for lock drift, resolution conflict, hash mismatch,
invalid wheel/ZIP, disk full, permission, Python build, project install,
capitalized/non-exact signature, stdout-only signature, and unclassified exit.
Map `-9` to `137` without retry. Preserve invalid UTF-8 bytes while classifying
a separate stderr decode with `errors='replace'`.

Require `main` to reject missing `--`, empty post-separator argv, non-`uv`
executable, any command other than the two frozen tuples, or pseudo retry
options. Prove `shell=False`, `check=False`, exact argv forwarding, and
`UV_HTTP_TIMEOUT=300` overriding inheritance.

- [ ] **Step 4: Run focused RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
```

Require collection success and failures only because the production script or
its interfaces do not yet exist.

---

### Task 5: Implement the wrapper and Docker dependency stage

**Files:**
- Create: `scripts/run_uv_sync_with_retries.py`
- Modify: `docker/wave0.Dockerfile`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/scripts/test_run_uv_sync_with_retries.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: Task 4 wrapper contracts and the unchanged launcher `New-A11BuildArguments`
- Produces: Docker target `a11-dependencies` and unchanged final `ENTRYPOINT ["val"]`

- [ ] **Step 1: Implement the minimal wrapper**

Use these immutable constants:

```python
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (5.0, 10.0)
ALLOWED_COMMANDS = {
    ("uv", "sync", "--frozen", "--no-dev", "--no-install-project"),
    ("uv", "sync", "--frozen", "--no-dev"),
}
RETRYABLE_STDERR = (
    "error decoding response body",
    "request or response body error",
    "error reading a body from connection",
    "stream error received:",
    "Failed to download distribution due to network timeout",
    "connection reset by peer",
)
```

Copy the environment, set `UV_HTTP_TIMEOUT=300`, call the runner with
`stdout=PIPE`, `stderr=PIPE`, `shell=False`, `check=False`, re-emit complete raw
byte streams, classify only decoded stderr, flush after each process, map a
negative return code to `128 + abs(returncode)`, and reject invalid CLI with
exit 2 before running a child.

- [ ] **Step 2: Run wrapper GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
```

- [ ] **Step 3: Add RED Dockerfile structure assertions**

Require one syntax directive, one named `a11-dependencies` stage, exact
`uv==0.8.15`, one `UV_LINK_MODE=copy`, two identical locked cache mounts with
ID `val-wave0-uv-0.8.15-cu126-v1`, two wrapper calls with the frozen command
vectors, one final stage, and one `ENTRYPOINT ["val"]`. Require one launcher
build, one `--no-cache`, one `--progress plain`, and no Docker-level retry loop.

- [ ] **Step 4: Refactor the Dockerfile minimally**

Preserve the current labels, Python arguments/build, uv install, PATH, WORKDIR,
source/config copies, and entrypoint. Change the dependency structure to:

```dockerfile
# syntax=docker/dockerfile:1
FROM nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356 AS a11-dependencies
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
COPY scripts/run_uv_sync_with_retries.py ./scripts/run_uv_sync_with_retries.py
RUN --mount=type=cache,id=val-wave0-uv-0.8.15-cu126-v1,target=/root/.cache/uv,sharing=locked \
    /opt/python/bin/python3.12 scripts/run_uv_sync_with_retries.py -- \
    uv sync --frozen --no-dev --no-install-project

FROM a11-dependencies AS final
COPY src ./src
COPY configs ./configs
RUN --mount=type=cache,id=val-wave0-uv-0.8.15-cu126-v1,target=/root/.cache/uv,sharing=locked \
    /opt/python/bin/python3.12 scripts/run_uv_sync_with_retries.py -- \
    uv sync --frozen --no-dev
ENTRYPOINT ["val"]
```

Do not add package upgrades, cache export, wheel exceptions, shell retries,
cache cleanup, or another final target.

- [ ] **Step 5: Run Dockerfile and launcher GREEN without executing a stage**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'dockerfile or build_arguments or campaign_orders or no_cleanup_retry'
docker buildx build --check --file docker/wave0.Dockerfile .
```

Require exit 0 and no image, container, A11 run, lease, or artifact change.

---

### Task 6: Verify, review, and create the single implementation commit

**Files:**
- Modify: none beyond the exact seven-path implementation allowlist
- Verify: all project tests, canonical/schema/style/lock/parser/Docker/Git gates, and the immutable external envelope

**Interfaces:**
- Consumes: complete uncommitted Tasks 2-5 implementation
- Produces: one reviewed implementation commit whose parent is this recovery plan commit

- [ ] **Step 1: Run focused, affected, and full CPU suites**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/scripts/test_run_uv_sync_with_retries.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py `
  tests/scripts/test_run_uv_sync_with_retries.py
uv run pytest -q -p no:cacheprovider
```

Require all three exit 0 and capture exact passed/skipped counts.

- [ ] **Step 2: Run canonical, schema, style, lock, parser, Dockerfile, and whitespace gates**

Re-run the committed ten-record independent encoder proof from Task 1 Step 2.
Then run:

```powershell
$Raw = Get-Content -Raw -LiteralPath 'configs/a11/preserved-attempts.json'
if (-not ($Raw | Test-Json -SchemaFile 'schemas/a11-preserved-attempts.schema.json')) {
    throw 'registry schema invalid'
}
$Registry = $Raw | ConvertFrom-Json -DateKind String
if ([string]$Registry.attempts[4].run_inventory_sha256 -cne
    'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64') {
    throw 'registry corrected digest mismatch'
}
uvx --offline black --check scripts/run_uv_sync_with_retries.py `
  tests/gates/test_wave0_a11_launcher.py tests/scripts/test_run_uv_sync_with_retries.py
uvx --offline ruff check scripts/run_uv_sync_with_retries.py `
  tests/gates/test_wave0_a11_launcher.py tests/scripts/test_run_uv_sync_with_retries.py
uv lock --check
pwsh -NoProfile -NonInteractive -Command `
  '$null=$t=$e=$null; [Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e) | Out-Null; if($e.Count){throw ($e.Message -join "; ")}'
powershell.exe -NoProfile -NonInteractive -Command `
  '$null=$t=$e=$null; [Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e) | Out-Null; if($e.Count){throw ($e.Message -join "; ")}'
docker buildx build --check --file docker/wave0.Dockerfile .
git diff --check
```

Require the fixed `uv.lock` hash from Global Constraints and no Docker stage
execution.

- [ ] **Step 3: Enforce exact scope and forbidden capabilities**

```powershell
$Expected = @(
  'configs/a11/preserved-attempts.json',
  'docker/wave0.Dockerfile',
  'schemas/a11-preserved-attempts.schema.json',
  'scripts/run_uv_sync_with_retries.py',
  'scripts/run_wave0_a11.ps1',
  'tests/gates/test_wave0_a11_launcher.py',
  'tests/scripts/test_run_uv_sync_with_retries.py'
) | Sort-Object
$Observed = @(git status --porcelain=v1 | ForEach-Object { $_.Substring(3) }) | Sort-Object
if (($Observed | ConvertTo-Json -Compress) -cne ($Expected | ConvertTo-Json -Compress)) {
    throw 'implementation allowlist mismatch'
}
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging must be empty before review' }
rg -n 'steven005|OWNER-A11-RUNTIME-20260830|Wave 1|wave1' `
  configs/a11 scripts/run_uv_sync_with_retries.py docker/wave0.Dockerfile
if ($LASTEXITCODE -eq 0) { throw 'future owner or Wave 1 capability found' }
if ($LASTEXITCODE -ne 1) { throw 'forbidden scan failed' }
```

Require no generated cache, bytecode, runtime artifact, or diagnostic directory
inside the repository.

- [ ] **Step 4: Re-run the complete external preservation gate**

Repeat Task 1 Steps 2-4 from the uncommitted candidate and compare the report to
the Task 1 entry report field-for-field. Require all five runs, the 1,283-byte
vector, three images, six lease files, zero active objects, 64,306 historical
files, and 21 historical images unchanged.

- [ ] **Step 5: Perform cold requirements and code review**

Use `superpowers:requesting-code-review`. Review the complete diff against the
recovery design, this plan, and the immutable runtime-transport design/plan.
Require `Critical=0` and `Important=0` for canonical byte correctness,
registry/schema closure, generic comparison, path containment/link rejection,
digest stability, exact retry behavior, Docker stage/cache shape, fixed runtime
versions, and forbidden runtime/GPU/owner/Wave 1 capabilities.

Resolve every finding with a new failing test followed by the smallest code
change, then rerun every affected gate and repeat review.

- [ ] **Step 6: Stage exactly seven paths and commit once**

```powershell
git add -- configs/a11/preserved-attempts.json `
  schemas/a11-preserved-attempts.schema.json `
  scripts/run_uv_sync_with_retries.py scripts/run_wave0_a11.ps1 `
  docker/wave0.Dockerfile tests/gates/test_wave0_a11_launcher.py `
  tests/scripts/test_run_uv_sync_with_retries.py
$Staged = @(git diff --cached --name-only | Sort-Object)
if (($Staged | ConvertTo-Json -Compress) -cne ($Expected | ConvertTo-Json -Compress)) {
    throw 'staged scope mismatch'
}
git diff --cached --check
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git commit -m 'fix: harden A11 dependency transport boundary'
```

- [ ] **Step 7: Verify the committed candidate**

Require the implementation parent to equal this plan commit, exact seven changed
paths, exact identity, clean linked/canonical worktrees, empty staging, fixed
`uv.lock`, and unchanged preservation report. Re-run wrapper tests, full
launcher tests, both parser gates, schema/canonical validation, Dockerfile
`--check`, and `git show --check HEAD`.

The only permitted claim is that the source candidate passed repository and
preservation review and is eligible for the one dependency-only diagnostic.
Do not claim formal A11 runtime success.

---

### Task 7: Execute and preserve exactly one dependency-only diagnostic

**Files:**
- Modify in repository: none
- Create outside repository/artifact root: one append-only directory beneath `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`
- Docker effect: BuildKit cache data only; no image export

**Interfaces:**
- Consumes: clean implementation commit and Docker target `a11-dependencies`
- Produces: `A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED` or `A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN`

- [ ] **Step 1: Prove one-shot diagnostic eligibility**

Repeat Task 6 Step 7 and the complete Task 1 preservation gate. Additionally:

```powershell
$Source = (git rev-parse HEAD).Trim()
$RecoveryPlan = (git rev-parse 'HEAD^').Trim()
$RecoveryDesign = (git rev-parse 'HEAD^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^').Trim()
if ($RecoveryDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5') {
    throw 'diagnostic lineage mismatch'
}
```

Require healthy Linux Docker, zero project containers, zero active leases, zero
numeric CUDA compute processes, and no diagnostic identity whose
`source_commit` equals `$Source`. Snapshot `docker image ls --no-trunc --digests`
and every preservation digest before creating evidence.

- [ ] **Step 2: Create one fresh append-only diagnostic identity**

Use parent:

```text
D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics
```

Create a child exactly once with name:

```text
a11-dependencies-<first 12 source hex>-<yyyyMMddTHHmmssfffZ>-<8 lowercase GUID hex>
```

Reject parent/child reparse points. Create exactly these evidence files with
create-new semantics, UTF-8 without BOM, and one final LF for JSON:

```text
00-identity.json
10-build.stdout.log
10-build.stderr.log
11-result.json
12-file-manifest.json
13-closure.json
```

The closed identity contains:

```text
schema_version = 1
diagnostic_type = a11-dependency-transport
diagnostic_id
source_commit
digest_recovery_plan_commit = $RecoveryPlan
digest_recovery_design_commit = 2db13d302da97a241daeaba3578cd9cec1c8073b
diagnostic_root_erratum_commit = 101bb79369399cc3947f1c667f0a11988f916638
runtime_transport_plan_commit = e31fc0c10fe34b480f7b2ee3d12a2e55530c6350
runtime_transport_design_commit = db047dcb8ad602fc4ac316a743ab4ddec3168cd5
specification_commit = b59b0d4407b98b460f6166ea7288ba6021dc7a78
original_plan_commit = 7dbd3a7576ea76beccfc64f748c4e495259ea89b
branch = codex/wave0-model-contract
docker_ostype
docker_server_version
docker_buildx_version
started_utc
argv = [docker, buildx, build, --no-cache, --progress=plain, --target, a11-dependencies, --output=type=cacheonly, --file, docker/wave0.Dockerfile, .]
formal_runtime_authorized = false
owner_authorization_id_present = false
gpu_requested = false
```

- [ ] **Step 3: Invoke the exact diagnostic once**

```powershell
& docker buildx build `
  --no-cache `
  --progress=plain `
  --target a11-dependencies `
  --output=type=cacheonly `
  --file docker/wave0.Dockerfile `
  . `
  1> (Join-Path $DiagnosticPath '10-build.stdout.log') `
  2> (Join-Path $DiagnosticPath '10-build.stderr.log')
$DiagnosticExitCode = $LASTEXITCODE
```

Do not wrap, retry, relaunch, automate, or repeat this command. If completion
cannot be proven after it starts, preserve a diagnostic `NO_GO`.

- [ ] **Step 4: Publish result, manifest, and closure**

`11-result.json` records exact argv, exit code, timestamps, stdout/stderr file
records, all case-sensitive `A11_UV_SYNC_ATTEMPT [123]/3` markers in log order,
and one terminal. Exit 0 maps to diagnostic PASS; nonzero maps to diagnostic
NO_GO. Never reinterpret a nonzero result.

`12-file-manifest.json` covers identity, both logs, and result with ordinal
relative paths, sizes, and SHA-256. `13-closure.json` binds result, manifest,
terminal, `formal_runtime_invoked=false`, and `wave1_started=false`.

- [ ] **Step 5: Re-prove preservation and stop**

Repeat the complete Task 1 preservation gate and require clean implementation
worktrees. Compare pre/post Docker image inventories byte-for-byte; `cacheonly`
must create no exported tagged or dangling image. Require no new A11 run,
validation root, lease, project container, receipt, checkpoint, owner identity,
model process, or Wave 1 object.

Report exactly one terminal:

```text
A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED
```

or:

```text
A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN
```

Stop in either case. A later formal runtime attempt requires a separate explicit
owner authorization bound to the exact implementation source, original
specification, original A11 plan, and branch.
