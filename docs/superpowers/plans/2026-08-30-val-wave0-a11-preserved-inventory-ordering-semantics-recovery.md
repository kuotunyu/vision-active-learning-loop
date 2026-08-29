# Wave 0 A11 Preserved-Inventory Ordering-Semantics Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Use superpowers:test-driven-development for Tasks 2-5, superpowers:requesting-code-review in Task 6, and superpowers:verification-before-completion before the implementation commit and diagnostic terminal. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Introduce explicit versioned run-inventory canonicalization, re-prove all five immutable A11 attempts with their unchanged frozen digests, and complete the approved registry-backed dependency-transport recovery without modifying historical evidence or starting a formal runtime attempt.

**Architecture:** Each registry attempt carries one closed `run_inventory_algorithm` ID. Attempts 1-4 use deterministic legacy-compatible `StringComparer.OrdinalIgnoreCase` with collision rejection; attempt 5 uses `StringComparer.Ordinal`. Both versions share one closed `path,size,sha256` compact-JSON/UTF-8 serializer, and the generic verifier dispatches only from the registry field.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker Engine 29.6.1 / BuildKit; exact uv 0.8.15; Git.

## Global Constraints

- The approved ordering-semantics design is `docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery-design.md` at commit `68f51519d2cb480200ca4fef740651b0d15dd76f`.
- This plan commit must be the direct child of that design commit and add only this plan file.
- The digest-recovery design and plan remain immutable at `2db13d302da97a241daeaba3578cd9cec1c8073b` and `03115325f36da31b135b4593fb8df1689eac9a35`.
- The runtime-transport design, plan, and diagnostic-root erratum remain immutable at `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`, `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`, and `101bb79369399cc3947f1c667f0a11988f916638`.
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
- The superseded attempt-5 digest `b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448` and the rejected attempt-1 universal-v2 digest `72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c` may appear only in recovery documents and negative tests.

## Normative overlay

Everything in the digest-recovery plan at commit
`03115325f36da31b135b4593fb8df1689eac9a35` remains binding except these exact
replacements:

| Contract | Superseded value | Effective value |
| --- | --- | --- |
| Run inventory ordering | universal `StringComparer.Ordinal` | registry-selected closed v1/v2 algorithm |
| Attempts 1-4 algorithm | implicit/universal ordinal | `a11-run-inventory-json-ordinal-ignore-case-v1` |
| Attempt 5 algorithm | implicit universal ordinal | `a11-run-inventory-json-ordinal-v2` |
| Registry algorithm metadata | absent | required `run_inventory_algorithm` enum on every attempt |
| Canonical inventory API | `Get-A11CanonicalRunInventory -RunRoot <absolute>` | `Get-A11CanonicalRunInventory -RunRoot <absolute> -Algorithm <exact-id>` |
| Implementation parent | digest-recovery plan `03115325f36da31b135b4593fb8df1689eac9a35` | this ordering-semantics plan commit |
| Implementation grandparent | digest-recovery design `2db13d302da97a241daeaba3578cd9cec1c8073b` | ordering-semantics design `68f51519d2cb480200ca4fef740651b0d15dd76f` |

The common compact JSON, record property order, UTF-8, hash, path, link, and
artifact rules remain unchanged. Algorithm IDs are registry metadata and are
not inserted into the hashed record array.

## Frozen preservation envelope

| Ordinal | State | Algorithm | Calibration run | Owner | Files | Dirs | Inventory SHA-256 |
| ---: | --- | --- | --- | --- | ---: | ---: | --- |
| 1 | `launcher-stage-failure` | `a11-run-inventory-json-ordinal-ignore-case-v1` | `wave0-a11-calibration-20260828T045848083Z-b9917463` | `OWNER-A11-RUNTIME-20260828-01` | 48 | 18 | `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b` |
| 2 | `image-build-timeout` | `a11-run-inventory-json-ordinal-ignore-case-v1` | `wave0-a11-calibration-20260828T114911289Z-fe8b7000` | `steven001` | 5 | 5 | `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b` |
| 3 | `foundation-stream-contract-failure` | `a11-run-inventory-json-ordinal-ignore-case-v1` | `wave0-a11-calibration-20260828T172921151Z-a0f55fa1` | `steven002` | 60 | 18 | `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2` |
| 4 | `aggregate-cache-inventory-contract-failure` | `a11-run-inventory-json-ordinal-ignore-case-v1` | `wave0-a11-calibration-20260829T050706309Z-f5a0129e` | `steven003` | 137 | 30 | `f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717` |
| 5 | `dependency-transport-build-failure` | `a11-run-inventory-json-ordinal-v2` | `wave0-a11-calibration-20260829T123151657Z-bf516632` | `steven004` | 10 | 5 | `e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64` |

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

The exact image and release evidence remains:

```text
vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463
  sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5
  release 35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060
  released 146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322
vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1
  sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd
  release 72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93
  released a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f
vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e
  sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e
  release aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1
  released b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c
```

## Implementation file map and allowlist

- Create `configs/a11/preserved-attempts.json`: five immutable declarative records with one exact `run_inventory_algorithm` each.
- Create `schemas/a11-preserved-attempts.schema.json`: closed draft-2020-12 registry schema including the two-value algorithm enum.
- Create `scripts/run_uv_sync_with_retries.py`: bounded dependency-build-only transport wrapper.
- Modify `scripts/run_wave0_a11.ps1`: version-aware canonical inventory, registry loader/verifier, registry digest guard, and unchanged single-build campaign path.
- Modify `docker/wave0.Dockerfile`: named dependency stage, exact wrapper calls, and two locked BuildKit uv cache mounts.
- Modify `tests/gates/test_wave0_a11_launcher.py`: ordering-version, canonical-vector, registry, verifier, Dockerfile, and launcher TDD.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD.

No other tracked path may change. Do not edit any existing design or plan,
`pyproject.toml`, `uv.lock`, `configs/environment/wave0-lock.json`, receipt
schema, `src/`, statistical code, or model code.

---

### Task 1: Re-prove versioned ordering, preservation, and baseline

**Files:**
- Modify: none
- Read: Git topology, both recovery designs/plans, all five run roots, image/lease/historical inventories, Docker/GPU state, and complete CPU tests

**Interfaces:**
- Consumes: ordering design commit `68f51519d2cb480200ca4fef740651b0d15dd76f` and the attempt-5 JSON vector at digest-design commit `2db13d302da97a241daeaba3578cd9cec1c8073b`
- Produces: one read-only entry report containing exact lineage, v1/v2 ordering proofs, five run digests, attempt-5 byte proof, external envelope, and baseline test counts

- [ ] **Step 1: Prove plan lineage, identities, branch, and worktree isolation**

Run from the linked worktree:

```powershell
$ErrorActionPreference = 'Stop'
$OrderingDesign = '68f51519d2cb480200ca4fef740651b0d15dd76f'
$DigestPlan = '03115325f36da31b135b4593fb8df1689eac9a35'
$DigestDesign = '2db13d302da97a241daeaba3578cd9cec1c8073b'
$Erratum = '101bb79369399cc3947f1c667f0a11988f916638'
$RuntimePlan = 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350'
$RuntimeDesign = 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery.md'
$OrderingDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery-design.md'
$DigestPlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery.md'
$DigestDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery-design.md'
$Plan = (git rev-parse HEAD).Trim()
if ((git rev-parse "$Plan^").Trim() -cne $OrderingDesign) { throw 'ordering plan parent mismatch' }
if ((git rev-parse "$OrderingDesign^").Trim() -cne $DigestPlan) { throw 'ordering design parent mismatch' }
if ((git rev-parse "$DigestPlan^").Trim() -cne $DigestDesign) { throw 'digest plan parent mismatch' }
if ((git rev-parse "$DigestDesign^").Trim() -cne $Erratum) { throw 'digest design parent mismatch' }
if ((git rev-parse "$Erratum^").Trim() -cne $RuntimePlan) { throw 'erratum parent mismatch' }
if ((git rev-parse "$RuntimePlan^").Trim() -cne $RuntimeDesign) { throw 'runtime plan parent mismatch' }
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'branch mismatch' }
$ExpectedIdentity = 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>|kuotunyu <61350295+kuotunyu@users.noreply.github.com>'
foreach ($Pair in @(
    @($OrderingDesign, $OrderingDesignPath),
    @($Plan, $PlanPath),
    @($DigestPlan, $DigestPlanPath),
    @($DigestDesign, $DigestDesignPath)
)) {
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

- [ ] **Step 2: Load and independently prove the committed attempt-5 vector**

Read the single `json` fence from the committed digest-recovery design, not
from the artifact:

```powershell
$DigestDesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery-design.md'
$Text = [IO.File]::ReadAllText((Join-Path (Get-Location) $DigestDesignPath))
$Blocks = [regex]::Matches($Text, '(?s)```json\r?\n(.*?)\r?\n```')
if ($Blocks.Count -ne 1) { throw 'attempt-5 vector cardinality mismatch' }
$ExpectedAttempt5Records = @($Blocks[0].Groups[1].Value | ConvertFrom-Json)
if ($ExpectedAttempt5Records.Count -ne 10) { throw 'attempt-5 record count mismatch' }
foreach ($Record in $ExpectedAttempt5Records) {
    if ((@($Record.PSObject.Properties.Name) -join ',') -cne 'path,size,sha256') {
        throw 'attempt-5 property order mismatch'
    }
}
$ProductionJson = ConvertTo-Json -InputObject @($ExpectedAttempt5Records) -Depth 8 -Compress
$ManualRows = @($ExpectedAttempt5Records | ForEach-Object {
    '{"path":"' + $_.path + '","size":' +
    ([long]$_.size).ToString([Globalization.CultureInfo]::InvariantCulture) +
    ',"sha256":"' + $_.sha256 + '"}'
})
$IndependentJson = '[' + [string]::Join(',', $ManualRows) + ']'
if ($ProductionJson -cne $IndependentJson) { throw 'attempt-5 encoders disagree' }
$Bytes = [Text.UTF8Encoding]::new($false).GetBytes($ProductionJson)
$Digest = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($Bytes)).ToLowerInvariant()
if ($Bytes.Count -ne 1283 -or
    $Digest -cne 'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64') {
    throw 'attempt-5 committed vector mismatch'
}
```

- [ ] **Step 3: Hash each run once and prove versioned canonicalization**

Use these exact helpers. Sorting an in-memory record copy must not reread a file:

```powershell
$V1 = 'a11-run-inventory-json-ordinal-ignore-case-v1'
$V2 = 'a11-run-inventory-json-ordinal-v2'

function Get-RecoveryComparer {
    param([Parameter(Mandatory=$true)][string]$Algorithm)
    switch -CaseSensitive ($Algorithm) {
        'a11-run-inventory-json-ordinal-ignore-case-v1' { return [StringComparer]::OrdinalIgnoreCase }
        'a11-run-inventory-json-ordinal-v2' { return [StringComparer]::Ordinal }
        default { throw "unknown run inventory algorithm: $Algorithm" }
    }
}

function Sort-RecoveryNames {
    param(
        [Parameter(Mandatory=$true)][string[]]$Names,
        [Parameter(Mandatory=$true)][string]$Algorithm
    )
    $Comparer = Get-RecoveryComparer -Algorithm $Algorithm
    $Seen = [Collections.Generic.HashSet[string]]::new($Comparer)
    foreach ($Name in $Names) {
        if ([string]::IsNullOrWhiteSpace($Name) -or -not $Seen.Add($Name)) {
            throw "run inventory path collision under $Algorithm"
        }
    }
    $Sorted = [string[]]@($Names)
    [Array]::Sort($Sorted, $Comparer)
    return @($Sorted)
}

function Get-RecoveryCanonicalPayload {
    param(
        [Parameter(Mandatory=$true)][object[]]$Records,
        [Parameter(Mandatory=$true)][string]$Algorithm
    )
    $ByPath = [Collections.Generic.Dictionary[string,object]]::new([StringComparer]::Ordinal)
    foreach ($Record in $Records) {
        if ((@($Record.PSObject.Properties.Name) -join ',') -cne 'path,size,sha256' -or
            [string]$Record.path -notmatch '^[^/\\]+(?:/[^/\\]+)*$' -or
            @([string]$Record.path -split '/' | Where-Object { $_ -in @('.', '..') }).Count -ne 0 -or
            [long]$Record.size -lt 0 -or
            [string]$Record.sha256 -cnotmatch '^[0-9a-f]{64}$' -or
            -not $ByPath.TryAdd([string]$Record.path, $Record)) {
            throw 'invalid closed run inventory record'
        }
    }
    $Paths = Sort-RecoveryNames -Names @($ByPath.Keys) -Algorithm $Algorithm
    $OrderedRecords = @($Paths | ForEach-Object { $ByPath[$_] })
    $Json = ConvertTo-Json -InputObject @($OrderedRecords) -Depth 8 -Compress
    $Bytes = [Text.UTF8Encoding]::new($false).GetBytes($Json)
    return [pscustomobject][ordered]@{
        records = $OrderedRecords
        json = $Json
        canonical_byte_count = $Bytes.Count
        sha256 = [Convert]::ToHexString(
            [Security.Cryptography.SHA256]::HashData($Bytes)
        ).ToLowerInvariant()
    }
}

function Get-RecoveryRunInventory {
    param(
        [Parameter(Mandatory=$true)][string]$Path,
        [Parameter(Mandatory=$true)][string]$Algorithm
    )
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
    $RawRecords = @($Items | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
        [pscustomobject][ordered]@{
            path = $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
            size = [long]$_.Length
            sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
        }
    })
    $Payload = Get-RecoveryCanonicalPayload -Records $RawRecords -Algorithm $Algorithm
    $RawDirectories = [string[]]@($Items | Where-Object { $_.PSIsContainer } | ForEach-Object {
        $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
    })
    $DirectoryNames = Sort-RecoveryNames -Names $RawDirectories -Algorithm $Algorithm
    $Latest = @($Items | Where-Object { -not $_.PSIsContainer } |
        Sort-Object LastWriteTimeUtc | Select-Object -Last 1)
    if ($Latest.Count -ne 1) { throw "run has no regular file: $Root" }
    return [pscustomobject][ordered]@{
        records = @($Payload.records)
        directory_names = @($DirectoryNames)
        file_count = $Payload.records.Count
        directory_count = $DirectoryNames.Count
        canonical_byte_count = $Payload.canonical_byte_count
        sha256 = $Payload.sha256
        latest_write_utc = $Latest[0].LastWriteTimeUtc.ToString('o')
        links_absent = $true
    }
}

$ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
$RunRoot = Join-Path $ArtifactRoot 'a11-runs'
$Expected = [ordered]@{
    'wave0-a11-calibration-20260828T045848083Z-b9917463' = @($V1,48,18,'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b','2026-08-28T06:06:15.8277603Z')
    'wave0-a11-calibration-20260828T114911289Z-fe8b7000' = @($V1,5,5,'8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b','2026-08-28T12:17:12.8122776Z')
    'wave0-a11-calibration-20260828T172921151Z-a0f55fa1' = @($V1,60,18,'628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2','2026-08-28T18:10:34.6753199Z')
    'wave0-a11-calibration-20260829T050706309Z-f5a0129e' = @($V1,137,30,'f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717','2026-08-29T06:13:25.1659510Z')
    'wave0-a11-calibration-20260829T123151657Z-bf516632' = @($V2,10,5,'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64','2026-08-29T13:39:47.0148945Z')
}
$ObservedNames = @(Get-ChildItem -LiteralPath $RunRoot -Directory -Force |
    Sort-Object Name -CaseSensitive | ForEach-Object Name)
if (($ObservedNames | ConvertTo-Json -Compress) -cne
    (@($Expected.Keys) | ConvertTo-Json -Compress)) { throw 'A11 run envelope mismatch' }
$ObservedRuns = [ordered]@{}
foreach ($Name in $Expected.Keys) {
    $Value = $Expected[$Name]
    $Observed = Get-RecoveryRunInventory -Path (Join-Path $RunRoot $Name) -Algorithm $Value[0]
    if ($Observed.file_count -ne $Value[1] -or
        $Observed.directory_count -ne $Value[2] -or
        $Observed.sha256 -cne $Value[3] -or
        $Observed.latest_write_utc -cne $Value[4] -or
        -not $Observed.links_absent) { throw "preserved run mismatch: $Name" }
    $ObservedRuns[$Name] = $Observed
}
```

- [ ] **Step 4: Prove legacy/v1 equality and v2 negative/positive vectors**

Continue with the in-memory results from Step 3:

```powershell
foreach ($Name in @($Expected.Keys | Select-Object -First 4)) {
    $Root = Join-Path $RunRoot $Name
    $LegacyFiles = @(Get-ChildItem -LiteralPath $Root -File -Recurse -Force |
        Sort-Object FullName | ForEach-Object {
            $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
        })
    $V1Files = @($ObservedRuns[$Name].records | ForEach-Object path)
    if (($LegacyFiles | ConvertTo-Json -Compress) -cne
        ($V1Files | ConvertTo-Json -Compress)) { throw "legacy/v1 file order mismatch: $Name" }
    $LegacyDirectories = @(Get-ChildItem -LiteralPath $Root -Directory -Recurse -Force |
        Sort-Object FullName | ForEach-Object {
            $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
        })
    if (($LegacyDirectories | ConvertTo-Json -Compress) -cne
        ($ObservedRuns[$Name].directory_names | ConvertTo-Json -Compress)) {
        throw "legacy/v1 directory order mismatch: $Name"
    }
}
$Attempt1Name = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
$Attempt1V2 = Get-RecoveryCanonicalPayload `
    -Records @($ObservedRuns[$Attempt1Name].records) -Algorithm $V2
if ($Attempt1V2.sha256 -cne
    '72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c') {
    throw 'attempt-1 v2 negative vector mismatch'
}
$Attempt5Name = 'wave0-a11-calibration-20260829T123151657Z-bf516632'
$Attempt5 = $ObservedRuns[$Attempt5Name]
if (($Attempt5.records | ConvertTo-Json -Depth 8 -Compress) -cne
    ($ExpectedAttempt5Records | ConvertTo-Json -Depth 8 -Compress)) {
    throw 'attempt-5 exact records mismatch'
}
$ExpectedDirectories = @('audit','wave0','wave0/checkpoints','wave0/model_cache','wave0/receipts')
if (($Attempt5.directory_names | ConvertTo-Json -Compress) -cne
    ($ExpectedDirectories | ConvertTo-Json -Compress)) {
    throw 'attempt-5 exact directories mismatch'
}
if ($Attempt5.canonical_byte_count -ne 1283 -or
    $Attempt5.sha256 -cne 'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64') {
    throw 'attempt-5 v2 vector mismatch'
}
```

Run Steps 3-4 to completion without timeout, sampling, cached hashes, or
replacement constants. A mismatch is `NO_GO`.

- [ ] **Step 5: Re-prove images, leases, historical baselines, Docker, GPU, and diagnostic absence**

Use the exact committed `Get-A11HistoricalArtifactInventory` and
`Get-A11HistoricalImageInventory` algorithms. Require the frozen historical
counts/hashes, the exact five run names, three image tag/ID pairs, six
lease-history hashes, no validation run, and no diagnostic `00-identity.json`.
The diagnostic parent may be absent; do not create it.

Run these independent state gates:

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
$DiagnosticParent = 'D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics'
if (Test-Path -LiteralPath $DiagnosticParent) {
    if (@(Get-ChildItem -LiteralPath $DiagnosticParent -Filter '00-identity.json' -File -Recurse -Force).Count -ne 0) {
        throw 'dependency diagnostic identity already exists'
    }
}
```

Enumerate all containers with `docker ps --all --format '{{.ID}}|{{.Image}}'`;
inspect immutable image IDs and `RepoTags`; require zero containers associated
with any `vision-active-learning-loop:*` image.

- [ ] **Step 6: Run the complete CPU baseline and preserve the entry report**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider
```

Require exit 0 and record exact passed/skipped counts. Afterwards require both
worktrees clean, staging empty, and no `__pycache__`, `.pyc`, `.pytest_cache`,
runtime artifact, or diagnostic directory inside the repository. Any Task 1
failure stops without editing an implementation path.

---

### Task 2: Add RED algorithm-version, registry, and verifier tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: existing `_invoke_functions(...)` PowerShell AST adapter and fixture-only synthetic artifacts
- Produces: RED contracts for `Sort-A11CanonicalRelativePaths`, `Get-A11CanonicalRunInventory`, `Read-A11PreservedAttemptRegistry`, `Assert-A11PreservedAttemptRegistryUnchanged`, and generic `Get-A11PriorAttemptInventory`

- [ ] **Step 1: Add exact algorithm and attempt-5 fixtures**

Add beside the existing attempt constants:

```python
_RUN_INVENTORY_V1 = "a11-run-inventory-json-ordinal-ignore-case-v1"
_RUN_INVENTORY_V2 = "a11-run-inventory-json-ordinal-v2"
_ATTEMPT1_UNIVERSAL_V2_SHA256 = (
    "72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c"
)
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
```

Copy the ten exact transport `(path, size, sha256)` tuples from the committed
digest-recovery vector. Extend `_prior_attempts()` to five chronological
attempts; records 1-4 carry v1 and record 5 carries v2. Tests never read the
external artifact root.

- [ ] **Step 2: Write ordering-version RED tests**

Use in-memory paths and synthetic temp trees to require:

```python
assert sort_paths(["snapshots/facebook--dinov2-small/x", "snapshots/PekingU--rtdetr_r18vd/x"], _RUN_INVENTORY_V1) == [
    "snapshots/facebook--dinov2-small/x",
    "snapshots/PekingU--rtdetr_r18vd/x",
]
assert sort_paths(["snapshots/facebook--dinov2-small/x", "snapshots/PekingU--rtdetr_r18vd/x"], _RUN_INVENTORY_V2) == [
    "snapshots/PekingU--rtdetr_r18vd/x",
    "snapshots/facebook--dinov2-small/x",
]
```

Require v1 to reject `A/file.bin` plus `a/file.bin`, and both versions to
reject exact duplicates, rooted/backslash paths, `.`/`..`, missing/null/
unknown/differently-cased IDs. Switch PowerShell current culture among `zh-TW`,
`en-US`, and `tr-TR`; require byte-identical results per algorithm.

- [ ] **Step 3: Write canonical-vector and negative-digest RED tests**

Call `Get-A11CanonicalRunInventory` with an explicit algorithm. Require the
exact attempt-5 serializer vector to satisfy:

```python
assert observed["algorithm"] == _RUN_INVENTORY_V2
assert observed["canonical_byte_count"] == _TRANSPORT_CANONICAL_BYTE_COUNT
assert observed["sha256"] == _TRANSPORT_RUN_SHA256
assert observed["sha256"] != _SUPERSEDED_TRANSPORT_RUN_SHA256
```

Use an attempt-1-style mixed-case synthetic fixture to prove v1 and v2 produce
different ordered arrays and digests. Bind the v2 result as a negative value,
never an accepted alternative. Parameterize path, size, SHA, field order,
record order, whitespace, BOM, newline, and link mutations.

- [ ] **Step 4: Write registry/schema and generic-verifier RED tests**

Require schema version 1, ordinals `[1,2,3,4,5]`, exact algorithm assignments,
five owners, and exact frozen digests. Validate through `Test-Json -SchemaFile`.

Reject an algorithm field that is missing, null, unknown, differently cased,
or changed on any attempt. For attempt 2 or 5, require a changed algorithm ID
to fail through registry byte binding even when the fixture happens to sort
identically under v1 and v2.

Require the loader and generic verifier to reject missing/link inputs,
malformed JSON, unknown fields/states, unordered/duplicate ordinals, duplicate
owner/run/image/destination identities, extra/missing external run/image/lease,
record/directory/count/latest-write drift, unexpected replica/checkpoint/
closure/success/validation state, and path escape. All five consumed owners
fail reuse; `OWNER-A11-TEST-FRESH` passes the pure read-only gate.

- [ ] **Step 5: Write registry-byte stability and identity-binding RED tests**

Load a copied registry, mutate one byte, and require
`Assert-A11PreservedAttemptRegistryUnchanged` to fail before a stubbed
`Initialize-A11Phase`. Require both synthetic identities to store the same
lowercase 64-hex `preserved_attempt_registry_sha256`.

- [ ] **Step 6: Run focused RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'inventory_algorithm or canonical_run_inventory or preserved_attempt_registry or prior_attempt or preflight or destination or identity_binding'
```

Require collection success and failures caused only by absent algorithm-aware
functions, registry/schema files, or existing four-attempt branches. Syntax
errors and external Docker/GPU/artifact access are invalid RED.

---

### Task 3: Implement versioned inventory, registry, and generic verifier

**Files:**
- Create: `configs/a11/preserved-attempts.json`
- Create: `schemas/a11-preserved-attempts.schema.json`
- Modify: `scripts/run_wave0_a11.ps1`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: `Sort-A11CanonicalRelativePaths -Paths <string[]> -Algorithm <exact-id>` and `Get-A11CanonicalRunInventory -RunRoot <absolute> -Algorithm <exact-id>`
- Produces: `{algorithm,records,directory_names,file_count,directory_count,canonical_byte_count,sha256,latest_write_utc,links_absent}`; `{schema_version,registry_path,registry_sha256,attempts}`; generic prior-attempt evidence; `Assert-A11PreservedAttemptRegistryUnchanged -Registry <object> -> $true | throw`

- [ ] **Step 1: Create the exact closed schema and registry**

Create the draft-2020-12 schema from the immutable runtime-transport plan,
retaining `additionalProperties:false`, five-state enum, common required
fields, and state-dependent image/release rules. Add
`run_inventory_algorithm` to the common `required` array and add this exact
closed property:

```json
"run_inventory_algorithm": {
  "enum": [
    "a11-run-inventory-json-ordinal-ignore-case-v1",
    "a11-run-inventory-json-ordinal-v2"
  ]
}
```

Create two-space UTF-8 JSON with LF and one final newline. Migrate ordinals
1-4 from committed fixtures, never live artifacts, and set v1. Create ordinal
5 from the committed exact vector and set v2:

```json
{
  "ordinal": 5,
  "state": "dependency-transport-build-failure",
  "run_inventory_algorithm": "a11-run-inventory-json-ordinal-v2",
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

The excerpt is not a reduced object: include its exact two run IDs, two image
tags, sixteen destinations, five directories, ten key records, five closure
names, empty replica/checkpoint arrays, and all common fields required by the
schema. Attempt 5 has no image or release object.

- [ ] **Step 2: Implement closed algorithm dispatch and sorting**

Add these exact constants and pure sorter before the inventory function:

```powershell
$script:A11RunInventoryV1 = 'a11-run-inventory-json-ordinal-ignore-case-v1'
$script:A11RunInventoryV2 = 'a11-run-inventory-json-ordinal-v2'

function Sort-A11CanonicalRelativePaths {
    param(
        [Parameter(Mandatory=$true)][string[]]$Paths,
        [Parameter(Mandatory=$true)][string]$Algorithm
    )
    $Comparer = switch -CaseSensitive ($Algorithm) {
        'a11-run-inventory-json-ordinal-ignore-case-v1' { [StringComparer]::OrdinalIgnoreCase; break }
        'a11-run-inventory-json-ordinal-v2' { [StringComparer]::Ordinal; break }
        default { throw 'A11 run inventory algorithm is unsupported' }
    }
    $Seen = [Collections.Generic.HashSet[string]]::new($Comparer)
    foreach ($Path in $Paths) {
        if ([string]::IsNullOrWhiteSpace($Path) -or -not $Seen.Add($Path)) {
            throw 'A11 canonical relative path collision'
        }
    }
    $Sorted = [string[]]@($Paths)
    [Array]::Sort($Sorted, $Comparer)
    return @($Sorted)
}
```

Validate normalized relative POSIX paths before calling the sorter. Do not use
`Sort-Object`, current culture, expected digests, attempt state, or ordinal to
select the comparer.

- [ ] **Step 3: Implement the algorithm-explicit canonical inventory**

Add `Get-A11CanonicalRunInventory` with mandatory `[string]$RunRoot` and
`[string]$Algorithm`. Materialize unordered closed records once, reject links
and path escapes, use the pure sorter for file and directory paths, serialize
ordered `path,size,sha256` records as compact JSON, encode strict UTF-8 without
BOM/newline, and return only:

```powershell
[pscustomobject][ordered]@{
    algorithm = $Algorithm
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

The function accepts no expected digest, state, owner, or ordinal.

- [ ] **Step 4: Implement the loader and registry byte-stability guard**

`Read-A11PreservedAttemptRegistry` rejects missing/link inputs, BOM, invalid
UTF-8, schema failure, alternate property sets, duplicate identities, path
escape, unordered ordinals, unknown states, and invalid algorithm IDs. Use
`ConvertFrom-Json -DateKind String`, retain the exact registry byte hash, and
return only:

```powershell
[pscustomobject][ordered]@{
    schema_version = 1
    registry_path = [IO.Path]::GetFullPath($RegistryPath)
    registry_sha256 = $RegistryDigest
    attempts = @($Document.attempts)
}
```

`Assert-A11PreservedAttemptRegistryUnchanged` rehashes `registry_path`, compares
case-sensitively with `registry_sha256`, and returns `$true` or throws.

- [ ] **Step 5: Replace state-specific inventory branches with the generic verifier**

`Get-A11PriorAttemptInventory` accepts an optional loaded registry and calls:

```powershell
$Observed = Get-A11CanonicalRunInventory `
    -RunRoot $RunRoot `
    -Algorithm ([string]$Attempt.run_inventory_algorithm)
```

Compare every closed field with an error naming ordinal and field. Validate
current/peer identities, exact records/directories/counts/latest write,
absences/presences, optional image/release objects, and complete actual versus
registered run/image/lease/owner/destination sets.

Remove executable attempt-specific IDs, owners, image IDs, file hashes,
`ValidateCount(4,4)`, and cardinality branches. Keep evidence only in registry
and tests. Use `OrdinalIgnoreCase` only where the approved v1 algorithm or
Windows absolute containment/collision contract explicitly requires it.

- [ ] **Step 6: Bind registry bytes through the first-write boundary**

Return `registry_path` and `registry_sha256` in `prior_a11_attempts`. Add
mandatory `[string]$PreservedAttemptRegistrySha256` to
`New-A11PhaseIdentity`, validate lowercase 64-hex, and store
`preserved_attempt_registry_sha256` on both identities. After
`Confirm-A11ProtectedGit` and before each `Initialize-A11Phase`, run:

```powershell
Assert-A11PreservedAttemptRegistryUnchanged `
    -Registry $RawPreflight.prior_a11_attempts | Out-Null
```

Make `Test-A11PhaseDestinationsAbsent` accept mandatory `ArtifactRoot`, resolve
registry-relative destinations beneath it, reject aliases and alternate roots,
and retain existing no-clobber ordering.

- [ ] **Step 7: Run ordering/registry GREEN and the full launcher suite**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'inventory_algorithm or canonical_run_inventory or preserved_attempt_registry or prior_attempt or preflight or destination or identity_binding'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Require both exit 0 with no real Docker, GPU, network, model, or artifact use.

---

### Task 4: Add RED bounded uv transport-wrapper tests

**Files:**
- Create: `tests/scripts/test_run_uv_sync_with_retries.py`
- Test: `tests/scripts/test_run_uv_sync_with_retries.py`

**Interfaces:**
- Consumes: `run_uv_sync(argv, *, runner, sleeper, environ, stdout, stderr) -> int` and `main(argv: Sequence[str] | None = None) -> int`
- Produces: exact retry cardinality, classification, byte-stream, environment, and CLI contracts used by Task 5

- [ ] **Step 1: Create isolated injected fixtures**

Import the future script by file path without editing `pyproject.toml`. Use
`subprocess.CompletedProcess[bytes]`, `io.BytesIO`, a fake runner recording
command/environment, and a fake sleeper recording delays.

- [ ] **Step 2: Specify success, retry, and exhaustion**

Parameterize exactly:

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

First-attempt success uses one process/no sleep. Failure then success uses two
processes and `[5.0]`; two failures then success uses three and `[5.0, 10.0]`;
three failures return the third exit code. Emit
`A11_UV_SYNC_ATTEMPT n/3` before each child.

- [ ] **Step 3: Specify fail-closed and CLI cases**

Require one process/no sleep for lock drift, resolution conflict, hash mismatch,
invalid wheel/ZIP, disk full, permission, Python build, project install,
capitalized/non-exact signature, stdout-only signature, and unclassified exit.
Map `-9` to `137` without retry. Preserve invalid UTF-8 bytes while classifying
a separate stderr decode with `errors='replace'`.

Require `main` to reject missing `--`, empty post-separator argv, non-`uv`
executable, commands outside the two frozen tuples, or pseudo retry options.
Prove `shell=False`, `check=False`, exact argv, and `UV_HTTP_TIMEOUT=300`.

- [ ] **Step 4: Run focused RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
```

Require failures only because the production wrapper is absent.

---

### Task 5: Implement the wrapper and Docker dependency stage

**Files:**
- Create: `scripts/run_uv_sync_with_retries.py`
- Modify: `docker/wave0.Dockerfile`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/scripts/test_run_uv_sync_with_retries.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: Task 4 wrapper contracts and unchanged launcher `New-A11BuildArguments`
- Produces: Docker target `a11-dependencies` and unchanged final `ENTRYPOINT ["val"]`

- [ ] **Step 1: Implement the minimal wrapper**

Use exact constants:

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

Copy environment, set `UV_HTTP_TIMEOUT=300`, call runner with `stdout=PIPE`,
`stderr=PIPE`, `shell=False`, `check=False`, re-emit raw streams, classify only
decoded stderr, flush after each process, map negative return codes to
`128 + abs(returncode)`, and reject invalid CLI with exit 2 before a child.

- [ ] **Step 2: Run wrapper GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
```

- [ ] **Step 3: Add RED Dockerfile and launcher assertions**

Require one syntax directive, one `a11-dependencies` stage, exact uv 0.8.15,
one `UV_LINK_MODE=copy`, two identical locked cache mounts with ID
`val-wave0-uv-0.8.15-cu126-v1`, two wrapper calls with frozen argv, one final
stage, and one `ENTRYPOINT ["val"]`. Require one launcher build,
one `--no-cache`, one `--progress plain`, and no Docker retry loop.

- [ ] **Step 4: Refactor the Dockerfile minimally**

Preserve labels, Python build, uv installation, PATH, WORKDIR, copies, and
entrypoint. Use:

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

Do not add upgrades, cache export, wheel exceptions, shell retries, cache
cleanup, or another final target.

- [ ] **Step 5: Run GREEN without executing a Docker stage**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'dockerfile or build_arguments or campaign_orders or no_cleanup_retry'
docker buildx build --check --file docker/wave0.Dockerfile .
```

Require exit 0 and no image, container, run, lease, or artifact change.

---

### Task 6: Verify, review, and create the single implementation commit

**Files:**
- Modify: none beyond the exact seven-path implementation allowlist
- Verify: project tests, versioned canonicalization, schema/style/lock/parser/Docker/Git gates, and immutable external envelope

**Interfaces:**
- Consumes: complete uncommitted Tasks 2-5 implementation
- Produces: one reviewed implementation commit whose parent is this plan commit

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

Require all exit 0 and record exact passed/skipped counts.

- [ ] **Step 2: Run algorithm, schema, style, lock, parser, Dockerfile, and whitespace gates**

Re-run Task 1 Steps 2-4. Then run:

```powershell
$Raw = Get-Content -Raw -LiteralPath 'configs/a11/preserved-attempts.json'
if (-not ($Raw | Test-Json -SchemaFile 'schemas/a11-preserved-attempts.schema.json')) {
    throw 'registry schema invalid'
}
$Registry = $Raw | ConvertFrom-Json -DateKind String
$Algorithms = @($Registry.attempts | ForEach-Object { [string]$_.run_inventory_algorithm })
$ExpectedAlgorithms = @(
  'a11-run-inventory-json-ordinal-ignore-case-v1',
  'a11-run-inventory-json-ordinal-ignore-case-v1',
  'a11-run-inventory-json-ordinal-ignore-case-v1',
  'a11-run-inventory-json-ordinal-ignore-case-v1',
  'a11-run-inventory-json-ordinal-v2'
)
if (($Algorithms | ConvertTo-Json -Compress) -cne
    ($ExpectedAlgorithms | ConvertTo-Json -Compress)) { throw 'registry algorithm mapping mismatch' }
if ([string]$Registry.attempts[4].run_inventory_sha256 -cne
    'e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64') {
    throw 'registry attempt-5 digest mismatch'
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

Require fixed `uv.lock` hash and no Docker stage execution.

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

Require no generated cache, bytecode, runtime artifact, or diagnostic path
inside the repository.

- [ ] **Step 4: Re-run complete external preservation**

Repeat Task 1 Steps 2-5 from the uncommitted candidate and compare with the
entry report field-for-field. Require all versioned run digests, attempt-1 v2
negative vector, attempt-5 1,283-byte vector, three images, six lease files,
zero active objects, 64,306 historical files, and 21 historical images.

- [ ] **Step 5: Perform cold requirements and code review**

Use `superpowers:requesting-code-review`. Review against the ordering design,
this plan, digest recovery, and runtime transport contracts. Require
`Critical=0` and `Important=0` for algorithm dispatch, collision rejection,
canonical bytes, registry/schema closure, path/link containment, byte
stability, retry behavior, Docker cache/stage shape, fixed versions, and
forbidden runtime/GPU/owner/Wave 1 capabilities.

Resolve findings with a new failing test and smallest code change, rerun every
affected gate, and repeat review.

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
git commit -m 'fix: harden A11 recovery boundaries'
```

- [ ] **Step 7: Verify the committed candidate**

Require implementation parent equals this plan, exact seven paths, exact
identity, clean linked/canonical worktrees, empty staging, fixed `uv.lock`, and
unchanged preservation report. Re-run wrapper tests, full launcher tests, both
parser gates, schema/algorithm validation, Dockerfile `--check`, and
`git show --check HEAD`.

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

Repeat Task 6 Step 7 and complete Task 1 preservation. Additionally:

```powershell
$Source = (git rev-parse HEAD).Trim()
$OrderingPlan = (git rev-parse 'HEAD^').Trim()
$OrderingDesign = (git rev-parse 'HEAD^^').Trim()
$DigestPlan = (git rev-parse 'HEAD^^^').Trim()
$DigestDesign = (git rev-parse 'HEAD^^^^').Trim()
$Erratum = (git rev-parse 'HEAD^^^^^').Trim()
$RuntimePlan = (git rev-parse 'HEAD^^^^^^').Trim()
$RuntimeDesign = (git rev-parse 'HEAD^^^^^^^').Trim()
if ($OrderingDesign -cne '68f51519d2cb480200ca4fef740651b0d15dd76f' -or
    $DigestPlan -cne '03115325f36da31b135b4593fb8df1689eac9a35' -or
    $DigestDesign -cne '2db13d302da97a241daeaba3578cd9cec1c8073b' -or
    $Erratum -cne '101bb79369399cc3947f1c667f0a11988f916638' -or
    $RuntimePlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    $RuntimeDesign -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5') {
    throw 'diagnostic lineage mismatch'
}
```

Require healthy Linux Docker, zero project containers, zero active leases,
zero numeric CUDA compute processes, and no diagnostic identity with this
`source_commit`. Snapshot `docker image ls --no-trunc --digests` and every
preservation digest before evidence creation.

- [ ] **Step 2: Create one fresh append-only diagnostic identity**

Create a child under the diagnostic parent exactly once with name:

```text
a11-dependencies-<first 12 source hex>-<yyyyMMddTHHmmssfffZ>-<8 lowercase GUID hex>
```

Reject parent/child reparse points. Create exactly these files with create-new
semantics, UTF-8 without BOM, and one final LF for JSON:

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
ordering_recovery_plan_commit = $OrderingPlan
ordering_recovery_design_commit = 68f51519d2cb480200ca4fef740651b0d15dd76f
digest_recovery_plan_commit = 03115325f36da31b135b4593fb8df1689eac9a35
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

Do not wrap, retry, relaunch, automate, or repeat. If completion cannot be
proven after start, preserve diagnostic `NO_GO`.

- [ ] **Step 4: Publish result, manifest, and closure**

`11-result.json` records exact argv, exit code, timestamps, stdout/stderr
records, all case-sensitive `A11_UV_SYNC_ATTEMPT [123]/3` markers in log order,
and one terminal. Exit 0 is diagnostic PASS; nonzero is diagnostic NO_GO.

`12-file-manifest.json` covers identity, logs, and result with ordinal relative
paths, sizes, and SHA-256. `13-closure.json` binds result, manifest, terminal,
`formal_runtime_invoked=false`, and `wave1_started=false`.

- [ ] **Step 5: Re-prove preservation and stop**

Repeat complete Task 1 preservation and require clean implementation
worktrees. Compare pre/post Docker images byte-for-byte; `cacheonly` creates no
exported tagged or dangling image. Require no new A11 run, validation root,
lease, project container, receipt, checkpoint, owner identity, model process,
or Wave 1 object.

Report exactly one terminal:

```text
A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED
```

or:

```text
A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN
```

Stop in either case. A later formal runtime attempt requires separate explicit
owner authorization bound to the exact implementation source, original
specification, original A11 plan, and branch.
