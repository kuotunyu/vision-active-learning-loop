# Wave 0 A11 Entry-Verifier Contradictory-Result Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a persistent, behaviorally tested scalar identity verifier can read and exactly match all 20 frozen v2-v5 file identities while preserving the consumed contradictory entry as a failed non-PASS fact.

**Architecture:** A minimal read-only Stage 0 admits only Git/worktree state and fresh absence. A RED-first scalar comparator contract then freezes explicit `Int64` and ordinal-string behavior before one canonical inventory, one static admission, and one formal read-only entry verification. Independent closure publishes an entry-verifier-only PASS and stops before child-exit recovery.

**Tech Stack:** PowerShell 7.6.4; Windows PowerShell 5.1 parser compatibility; .NET `StringComparer`, `Int64`, `JsonDocument`, `Utf8JsonWriter`, `ArrayBufferWriter<byte>`, `SHA256`, `System.IO.Path`, and `System.IO.Directory.GetParent`; Git; Markdown; ignored append-only evidence.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract`.
- Approved design commit is exactly `c558c0a9a1ce02c3162305b4b7bf6592a905432a`; this plan commit must be its one-file direct child.
- Design path is `docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery-design.md`, Git blob `5bfa3ded2c55acf48b3e193a9fbb53d126e945ad`.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- The consumed v6 entry remains a failed non-PASS observation. Never rerun, reinterpret, repair, replace, or declare PASS for it.
- The consumed v6 workspace `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/` remains absent.
- Never execute, modify, delete, rename, replace, copy over, or use any v5/v4/v3/v2 source as a child or command.
- The only fresh workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/`.
- Stage 0 performs no v2-v5 enumeration, byte measurement, or digest comparison and creates no file.
- Create every human-authored ignored file with `apply_patch`; never generate source, JSON, report, or audit content with a script or shell redirection.
- The execution inventory is exactly nine human-authored files and zero machine files.
- Run Stage 0 exactly once, comparator RED exactly once, comparator GREEN exactly once, static admission exactly once, formal entry exactly once, pre-report closure exactly once, and final closure exactly once.
- Once a process consumes a source, module, inventory, report, command identity, or path, it is immutable.
- Any unexpected Stage 0, RED, GREEN, static, formal, or closure result stops the plan; do not edit, replace, or retry it.
- Every filesystem ancestor walk stores a canonical path string and calls `[IO.Directory]::GetParent($Cursor)`. No filesystem item is queried for `.Parent`.
- Every path-bearing argument is a literal fully qualified Windows path. No receiver supports relative fallback, module-name search, PATH search, or alternate candidate.
- Canonical JSON reconstruction uses explicit `Utf8JsonWriter` calls with `UnsafeRelaxedJsonEscaping`; no source uses `ConvertTo-Json` or `JsonSerializer.Serialize`.
- No `machine/`, child evidence, sidecar, transcript, result, digest, temporary file, or runtime output may be created.
- Do not inspect or execute Docker, Docker Desktop processes, WSL, Hyper-V, builders, images, containers, caches, volumes, GPU, `nvidia-smi`, CUDA, CPU baseline, dependencies, model, A11 launcher, entry child, product task, Wave 1, or runtime.
- Do not create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`.
- Do not modify product code, another repository, a remote, or Git history.
- Do not push, merge, tag, release, amend, rebase, reset, stash, or delete evidence.
- The only final success terminal is `ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED`.
- Execution creates ignored evidence only; there is no tracked implementation commit after this plan commit.

## Normative Inputs

- Approved design: commit `c558c0a9a1ce02c3162305b4b7bf6592a905432a`, blob `5bfa3ded2c55acf48b3e193a9fbb53d126e945ad`.
- Consumed plan: commit `68cd174c64a17e4b8c42771caf046ecb23c3eb06`, blob `d36d0b09dbb4ff19fe17c18c139e4897dee41cfe`.
- Frozen PowerShell: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`, 301,368 bytes, SHA-256 `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`, valid Authenticode signature.
- Repository root: `<repo>\.worktrees\wave0-model-contract`.
- Canonical worktree: `<repo>`.
- Preserved contradictory target: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-evidence-module-red-v3.psm1`, 97 bytes, SHA-256 `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136`.
- Consumed rejection class: `inventory hash rejected`; no consumed success terminal was emitted and retroactive PASS is forbidden.

## File and Interface Map

Execution creates exactly these ignored human-authored files:

| Path | Responsibility |
|---|---|
| `task-1-stage0-audit-v7.ps1` | Immutable audit copy of the plan-pinned Stage 0 source and exact result; never executed. |
| `task-1-scalar-identity-tests-v7.ps1` | One RED and one GREEN behavioral contract. |
| `task-1-scalar-identity-red-v7.psm1` | Intentional equal-scalar rejection subject. |
| `task-1-scalar-identity-green-v7.psm1` | Side-effect-free production comparator. |
| `task-1-preserved-inventory-v7.json` | Canonical incident, executable, 20-file, and 10-absence record. |
| `task-1-entry-verifier-v7.ps1` | One-shot formal read-only inventory verifier. |
| `task-1-static-verifier-v7.ps1` | Parser, AST, type-flow, canonicalization, and forbidden-action gate. |
| `task-1-closure-verifier-v7.ps1` | Independent read-only pre-report and final closure. |
| `task-1-report.md` | Immutable final evidence index and first exact terminal. |

The production comparator exports exactly:

```powershell
function Compare-A11ScalarIdentity {
    param(
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualSha256,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedSha256
    )
}
```

The behavioral test accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Red', 'Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $ModulePath,
    [Parameter(Mandatory)] [string] $ExpectedModulePath,
    [Parameter(Mandatory)] [long] $ExpectedModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath
)
```

The formal verifier accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [string] $InventoryPath,
    [Parameter(Mandatory)] [string] $ExpectedInventoryPath,
    [Parameter(Mandatory)] [long] $ExpectedInventoryByteCount,
    [Parameter(Mandatory)] [string] $ExpectedInventorySha256,
    [Parameter(Mandatory)] [string] $ComparatorModulePath,
    [Parameter(Mandatory)] [string] $ExpectedComparatorModulePath,
    [Parameter(Mandatory)] [long] $ExpectedComparatorModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedComparatorModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [string] $ExpectedPlanCommit,
    [Parameter(Mandatory)] [string] $ExpectedDesignCommit
)
```

The closure verifier accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('PreReport', 'Final')] [string] $Mode,
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [string] $InventoryPath,
    [Parameter(Mandatory)] [long] $ExpectedInventoryByteCount,
    [Parameter(Mandatory)] [string] $ExpectedInventorySha256,
    [Parameter(Mandatory)] [string] $ComparatorModulePath,
    [Parameter(Mandatory)] [long] $ExpectedComparatorModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedComparatorModuleSha256,
    [Parameter(Mandatory)] [string] $FormalTerminal,
    [string] $ReportPath = '',
    [long] $ExpectedReportByteCount = -1,
    [string] $ExpectedReportSha256 = ''
)
```

---

### Task 1: Admit Stage 0 and complete scalar comparator RED→GREEN

**Files:**
- Create after Stage 0: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-stage0-audit-v7.ps1`
- Create after Stage 0: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-scalar-identity-tests-v7.ps1`
- Create after Stage 0: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-scalar-identity-red-v7.psm1`
- Create after exact RED: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-scalar-identity-green-v7.psm1`

**Interfaces:**
- Consumes: exact docs lineage, clean linked/canonical worktrees, frozen PowerShell, and two absent fresh workspaces.
- Produces: one immutable Stage 0 fact and a frozen production comparator proven against the equal-scalar rejection mutation and seven invalid-shape/value categories.

- [ ] **Step 1: Run the plan-pinned minimal Stage 0 exactly once**

Use the frozen PowerShell executable with the exact following LF/UTF-8 source as its command body. The approved plan blob is the immutable source carrier. Do not create the workspace or inspect any v2-v5 path before this returns exact PASS.

```powershell
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$ExpectedDesign = 'c558c0a9a1ce02c3162305b4b7bf6592a905432a'
$ExpectedDesignBlob = '5bfa3ded2c55acf48b3e193a9fbb53d126e945ad'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery.md'
$FreshWorkspace = Join-Path $RepositoryRoot '.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery'
$ConsumedV6Workspace = Join-Path $RepositoryRoot '.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery'
$FrozenPwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'

Push-Location -LiteralPath $RepositoryRoot
try {
    $ExpectedPlan = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $ExpectedPlan -notmatch '^[0-9a-f]{40}$') { throw 'plan commit identity rejected' }
    if ((git branch --show-current) -cne 'codex/wave0-model-contract') { throw 'branch rejected' }
    if ((git rev-list --parents -n 1 HEAD) -cne "$ExpectedPlan $ExpectedDesign") { throw 'plan parent rejected' }
    if (-not [string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))) { throw 'superproject rejected' }
    $GitDir = [IO.Path]::GetFullPath((git rev-parse --git-dir))
    $GitCommon = [IO.Path]::GetFullPath((git rev-parse --git-common-dir))
    if ([StringComparer]::OrdinalIgnoreCase.Equals($GitDir, $GitCommon)) { throw 'linked-worktree isolation missing' }
    $Changed = @(git diff-tree --no-commit-id --name-only -r HEAD)
    if ($Changed.Count -ne 1 -or $Changed[0] -cne $PlanPath) { throw 'plan path rejected' }
    $Identity = git show -s --format='%an|%ae|%cn|%ce|%s' HEAD
    if ($Identity -cne 'kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 entry verifier contradictory result recovery') { throw 'plan identity rejected' }
    if ((git rev-parse "HEAD:$DesignPath") -cne $ExpectedDesignBlob) { throw 'design blob rejected' }
    if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree dirty' }
    if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging not empty' }
    if (@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'canonical worktree dirty' }
    if (Test-Path -LiteralPath $FreshWorkspace) { throw 'fresh workspace already exists' }
    if (Test-Path -LiteralPath $ConsumedV6Workspace) { throw 'consumed v6 workspace exists' }
    if ((Get-Item -LiteralPath $FrozenPwsh -Force).Length -ne 301368) { throw 'PowerShell bytes rejected' }
    if ((Get-FileHash -LiteralPath $FrozenPwsh -Algorithm SHA256).Hash.ToLowerInvariant() -cne 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f') { throw 'PowerShell hash rejected' }
    if ((Get-AuthenticodeSignature -LiteralPath $FrozenPwsh).Status -cne 'Valid') { throw 'PowerShell signature rejected' }
    'ENTRYV7_STAGE0_PASS|workspace=absent|v6=absent|linked=clean|canonical=clean'
}
finally {
    Pop-Location
}
```

Require exactly 3,421 LF/UTF-8 bytes and SHA-256 `82adc690130d2930ca931bd374b086c5681ff047fa459bb04e7d1242c4543644`. Require exit 0, empty stderr, and sole stdout:

```text
ENTRYV7_STAGE0_PASS|workspace=absent|v6=absent|linked=clean|canonical=clean
```

Any difference stops before workspace creation. Never repeat Stage 0.

- [ ] **Step 2: Create the Stage 0 audit, behavioral test, and intentional RED with `apply_patch`**

Create the fresh directory only through the first `apply_patch`. The audit file contains the exact Stage 0 source above followed by comments containing its pre-frozen byte count, SHA-256, exact invocation identity, exact terminal, exit 0, and empty stderr. It is never executed.

The behavioral test uses the exact interface in the file map. It validates the module as absolute, canonical, contained, ordinary, non-linked, exact-byte, and exact-hash with a path-string ancestor walk. It imports only:

```powershell
Import-Module -Name $ValidatedModulePath -Force -ErrorAction Stop
```

It requires the sole export `Compare-A11ScalarIdentity`, verifies no file appears, and removes the module in `finally`. Its literal exact pair is `[long]97` and the v3 digest `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136`.

The intentional RED module exports the exact public interface and returns the exact seven-property ordered record, but always sets `identity_match` to Boolean false. It has only `Set-StrictMode`, the function definition, and final `Export-ModuleMember` at module scope.

- [ ] **Step 3: Parse and run comparator RED exactly once**

Before execution, parse the audit, test, and RED module under PowerShell 7.6.4 and Windows PowerShell 5.1. Statically require one import from `$ValidatedModulePath`, one exported function, no predecessor path, write, redirection, dynamic evaluation, shell string, process start, Docker/GPU/A11/product/Git/network/runtime command, or `machine/` path.

Run the test in `Red` mode with literal paths and the measured RED-module byte count/hash. It calls the exact equal-scalar pair, requires all six input/individual fields exact but `identity_match=false`, and emits only:

```text
SCALAR_IDENTITY_TEST_RED_PASS|fault=equal_scalar_rejected
```

Any other exit, output, exception, type, property, or side effect is `ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO`; preserve and stop. Never edit or rerun the RED subject or invocation.

- [ ] **Step 4: Implement the minimal GREEN comparator after exact RED**

Create the GREEN module with `apply_patch`. Its complete comparison core is:

```powershell
function Compare-A11ScalarIdentity {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedByteCount,
        [Parameter(Mandatory)] [AllowNull()] [object] $ActualSha256,
        [Parameter(Mandatory)] [AllowNull()] [object] $ExpectedSha256
    )

    if ($null -eq $ActualByteCount -or $null -eq $ExpectedByteCount -or $null -eq $ActualSha256 -or $null -eq $ExpectedSha256) { throw 'null identity value rejected' }
    if ($ActualByteCount -is [array] -or $ExpectedByteCount -is [array] -or $ActualSha256 -is [array] -or $ExpectedSha256 -is [array]) { throw 'array identity value rejected' }
    if (($ActualByteCount -is [System.Collections.IEnumerable] -and $ActualByteCount -isnot [string]) -or
        ($ExpectedByteCount -is [System.Collections.IEnumerable] -and $ExpectedByteCount -isnot [string]) -or
        ($ActualSha256 -is [System.Collections.IEnumerable] -and $ActualSha256 -isnot [string]) -or
        ($ExpectedSha256 -is [System.Collections.IEnumerable] -and $ExpectedSha256 -isnot [string])) { throw 'enumerable identity value rejected' }
    if ($ActualByteCount.GetType() -ne [long] -or $ExpectedByteCount.GetType() -ne [long]) { throw 'byte count type rejected' }
    if ([long]$ActualByteCount -lt 0 -or [long]$ExpectedByteCount -lt 0) { throw 'negative byte count rejected' }
    if ($ActualSha256.GetType() -ne [string] -or $ExpectedSha256.GetType() -ne [string]) { throw 'digest type rejected' }
    if (-not [regex]::IsMatch([string]$ActualSha256, '\A[0-9a-f]{64}\z', [Text.RegularExpressions.RegexOptions]::CultureInvariant)) { throw 'actual digest format rejected' }
    if (-not [regex]::IsMatch([string]$ExpectedSha256, '\A[0-9a-f]{64}\z', [Text.RegularExpressions.RegexOptions]::CultureInvariant)) { throw 'expected digest format rejected' }

    $ByteCountMatch = ([long]$ActualByteCount -eq [long]$ExpectedByteCount)
    $Sha256Match = [StringComparer]::Ordinal.Equals([string]$ActualSha256, [string]$ExpectedSha256)
    [pscustomobject][ordered]@{
        actual_byte_count = [long]$ActualByteCount
        expected_byte_count = [long]$ExpectedByteCount
        byte_count_match = [bool]$ByteCountMatch
        actual_sha256 = [string]$ActualSha256
        expected_sha256 = [string]$ExpectedSha256
        sha256_match = [bool]$Sha256Match
        identity_match = [bool]($ByteCountMatch -and $Sha256Match)
    }
}
```

The complete file begins with `Set-StrictMode -Version Latest` and ends with:

```powershell
Export-ModuleMember -Function Compare-A11ScalarIdentity
```

No other module-scope statement is allowed.

- [ ] **Step 5: Run the same behavioral test against GREEN exactly once**

Parse the frozen test and GREEN module under both parsers. Run `Green` with exact path/bytes/hash. The test performs these literal cases without deriving expected results from the module:

1. exact `[long]97` and exact digest returns the seven exact properties with all three Boolean matches true;
2. `ActualSha256 = [object[]]@($ExactHash)` throws;
3. `ActualByteCount = [object[]]@([long]97)` throws;
4. the final hash nibble changed from `6` to `7` returns only digest/identity false;
5. actual byte count `[long]98` returns only byte-count/identity false;
6. uppercase, 63-character, 65-character, whitespace, null, and `[int]7` digest values each throw;
7. negative `[long]-1`, `[int]97`, and string `'97'` byte counts each throw; and
8. the exact result property order and Boolean runtime types are closed and exact.

Require exit 0, empty stderr, no filesystem change, and sole stdout:

```text
SCALAR_IDENTITY_TEST_GREEN_PASS|cases=8|comparison=ordinal|collections=rejected
```

Any difference is `ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO`; freeze the test and GREEN module without retry.

---

### Task 2: Author canonical inventory and pass static admission

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-preserved-inventory-v7.json`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-entry-verifier-v7.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-static-verifier-v7.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-closure-verifier-v7.ps1`

**Interfaces:**
- Consumes: frozen Stage 0, comparator RED/GREEN, plan/design/executable identities, and no formal inventory observation.
- Produces: one canonical 20-file/10-absence inventory and statically admitted read-only formal/closure sources.

- [ ] **Step 1: Measure fresh source identities and author the canonical inventory manually**

Print one immutable table for the plan commit, Stage 0 audit, behavioral test, RED module, GREEN module, frozen PowerShell, repository root, and fresh workspace. Use the literal values in `apply_patch`; do not generate JSON.

The root is one compact UTF-8 JSON line plus LF with exact property order:

```text
schema_version,inventory_id,source_plan_commit,failed_attempt,frozen_powershell,workspaces,absent_paths
```

Use `schema_version=1`, `inventory_id=entryv7-preserved-inventory-001`, and the literal plan commit measured from HEAD. `failed_attempt` has exact order:

```text
plan_commit,plan_blob,reported_path,rejection_class,later_byte_count,later_sha256,success_terminal_emitted,retroactive_pass_allowed
```

Its values are consumed plan `68cd174c64a17e4b8c42771caf046ecb23c3eb06`, blob `d36d0b09dbb4ff19fe17c18c139e4897dee41cfe`, the absolute v3 module path, rejection class `inventory hash rejected`, `[long]97`, exact v3 hash, and Boolean false for both final fields.

`frozen_powershell` order is `path,byte_count,sha256,signature_status` with the normative executable identity and string `Valid`.

`workspaces` contains v5, v4, v3, v2 in that order. Each object order is `generation,path,file_count,files`; each file order is `path,byte_count,sha256`. Use exactly these 20 literal records:

| Gen | File | Bytes | SHA-256 |
|---|---|---:|---|
| v5 | `task-1-ancestor-chain-red-v5.ps1` | 1436 | `dfa8f9b572ff31439b8198acd014d53c0efbc408ab50cbce156423293e92b9ac` |
| v5 | `task-1-ancestor-chain-tests-v5.ps1` | 8798 | `07dc9df03102dd64c6d79326c25281fcd143246618777a0c55abfb917623ca09` |
| v5 | `task-1-bootstrap-command-static-v5.ps1` | 20783 | `8ae484662c7f5165b721ad70e3213f1aad43f4b5d238af5282e6ecda1df051f9` |
| v5 | `task-1-bootstrap-red-brief-v5.md` | 5003 | `5d5a95ef800a34f5cfb9a65833367191bde725f6741bb2d79fce0c626644da27` |
| v5 | `task-1-entry-gate-v5.ps1` | 6250 | `2d1b8f10842d6abdc8bea772d258f593b733b2fa7a8af21522c569199fb7dee1` |
| v5 | `task-1-evidence-module-red-v5.psm1` | 97 | `efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071` |
| v5 | `task-1-evidence-tests-v5.ps1` | 12339 | `21b59e3e4264706d095c5135a9c1a71fc7ada45dfb2731c02badf0134818c92b` |
| v5 | `task-1-red-command-v5.json` | 1437 | `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3` |
| v4 | `task-1-bootstrap-command-static-v4.ps1` | 12532 | `e17d575e0ff8287ea7424c28c08b14bd7625e5603651b07f0283e4a5ced72a68` |
| v4 | `task-1-entry-gate-v4.ps1` | 5562 | `8e35c0ab663116587448ecb6840bf6c6ecc876c367fe25f4fa86a3e2616b764d` |
| v4 | `task-1-evidence-module-red-v4.psm1` | 97 | `dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb` |
| v4 | `task-1-evidence-tests-v4.ps1` | 8824 | `aca02e4a213baa1703eec9c0a82a638240de46ecfb77cd0b944c3ab778f7a863` |
| v4 | `task-1-red-command-v4.json` | 1461 | `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6` |
| v3 | `task-1-bootstrap-path-static-v3.ps1` | 7521 | `636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9` |
| v3 | `task-1-entry-gate-v3.ps1` | 5151 | `fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19` |
| v3 | `task-1-evidence-module-red-v3.psm1` | 97 | `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136` |
| v3 | `task-1-evidence-tests-v3.ps1` | 9012 | `db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c` |
| v2 | `task-1-entry-gate.ps1` | 3541 | `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b` |
| v2 | `task-1-evidence-module-red.psm1` | 103 | `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc` |
| v2 | `task-1-evidence-tests.ps1` | 4420 | `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65` |

`absent_paths` is exactly these 10 fully qualified strings in order: v5/v4/v3/v2 `machine` directories; the four `preformal-003-recorder-red-verify.stdout.bin`, `.stderr.bin`, `.result.json`, `.result.sha256` paths under the restart-aware recovery `machine` directory; the consumed v6 workspace; and the fresh entryv7 `machine` directory.

Immediately require strict UTF-8 without BOM, exactly one LF, closed property orders, recursive duplicate rejection, and freeze the literal inventory byte count/SHA-256 before any formal/static/closure source exists.

- [ ] **Step 2: Author the complete formal entry verifier**

Use the exact formal interface in the file map. Implement private functions for strict ordinary path validation, strict JSON reading, explicit canonical reconstruction, and Git closure. Every path validation uses canonical string ancestry and rejects null/whitespace, wildcard, provider, URI, UNC, device, ADS, relative, escaping, wrong-kind, linked, wrong-byte, and wrong-hash values.

The formal source validates root/nested property order and types before using a value. For each expected file, its comparison loop is exactly shaped as:

```powershell
$ExpectedByteCount = [long]$FileElement.GetProperty('byte_count').GetInt64()
$ExpectedSha256 = [string]$FileElement.GetProperty('sha256').GetString()
$ActualByteCount = [long](Get-Item -LiteralPath $ValidatedFilePath -Force).Length
$ActualSha256 = [string](Get-FileHash -LiteralPath $ValidatedFilePath -Algorithm SHA256).Hash.ToLowerInvariant()
$Record = Compare-A11ScalarIdentity -ActualByteCount $ActualByteCount -ExpectedByteCount $ExpectedByteCount -ActualSha256 $ActualSha256 -ExpectedSha256 $ExpectedSha256
if ($Record.identity_match.GetType() -ne [bool] -or -not [bool]$Record.identity_match) { throw 'preserved identity rejected' }
[void]$IdentityRecords.Add($Record)
```

It calls the comparator exactly 20 times, retains 20 records in memory, checks each workspace file count independently, verifies all 10 absences, validates frozen PowerShell bytes/hash/signature, requires exact plan/design lineage and linked/canonical cleanliness, and writes nothing. Sole PASS:

```text
ENTRY_VERIFIER_FORMAL_PASS|workspaces=4|files=20|comparison=ordinal|contradiction=preserved|v6=absent
```

- [ ] **Step 3: Author the independent closure verifier**

Use the exact closure interface in the file map. It must not import the production comparator or invoke the formal verifier. Reconstruct inventory canonically, validate its identity, and independently repeat scalar `Int64` and `StringComparer.Ordinal` comparison for all 20 records.

In `PreReport`, require empty report arguments and absent report, exact formal terminal, nine-minus-report human files, all 10 absences, exact Git state, and emit only:

```text
ENTRY_VERIFIER_CLOSURE_PASS|workspaces=4|files=20|formal=exact|writes=0
```

In `Final`, require an ordinary contained report at the exact path/bytes/hash, exactly nine human files, the report's closed evidence sections and literal terminals, unchanged source/inventory identities, all 10 absences, and emit only:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

The closure writes nothing in either mode.

- [ ] **Step 4: Author the static verifier and non-consumingly precheck all sources**

The static verifier accepts `WorkspacePath` plus explicit actual/expected path, byte-count, and SHA-256 quartets for the behavioral test, RED module, GREEN module, inventory, formal verifier, and closure verifier. No parameter is optional.

It parses every PowerShell source under PowerShell 7.6.4 and Windows PowerShell 5.1; verifies exact public parameters/exports/property orders; permits numeric byte equality only; requires exactly one production `StringComparer.Ordinal.Equals`; rejects digest identity through `-eq`, `-ceq`, `Compare-Object`, interpolation, containment, pipeline aggregation, or collection truthiness; proves runtime type checks precede comparison; validates explicit `Utf8JsonWriter` reconstruction; and requires zero writes/retries/process starts.

It AST-rejects filesystem-object `.Parent`, dot-source, dynamic evaluation, `Start-Process`, shell strings, redirection, transcript/sidecar/result/digest/temp/machine paths, protected-variable assignment, predecessor execution, Docker/GPU/A11/product/Git-mutation/network/runtime commands, and the consumed v6 source as an invocation target.

Before consuming the static source, parse it under both parsers and run an isolated in-memory canonical-writer microcheck against exact inventory bytes. Then run the static verifier exactly once with all literal identities. Require exit 0, empty stderr, and sole stdout:

```text
ENTRY_VERIFIER_STATIC_PASS|exports=1|types=scalar|comparison=ordinal|writes=0|retries=0
```

Any difference is `ENTRY_VERIFIER_STATIC_REJECTED / NO_GO`; freeze everything and stop without formal entry.

---

### Task 3: Execute one formal entry and pre-report closure

**Files:**
- Read only: the eight pre-report entryv7 files, 20 preserved files, 10 absent paths, Git state, and frozen PowerShell.
- Create: none.

**Interfaces:**
- Consumes: exact comparator GREEN and static PASS with every formal input frozen.
- Produces: one formal entry PASS and one independent pre-report closure PASS, or the first preserved NO_GO.

- [ ] **Step 1: Freeze the formal command identity without executing it**

Print literal actual/expected identities for inventory and GREEN comparator plus plan/design commits and fresh workspace. Construct the formal argv with the exact interface and fully qualified literal paths. Require formal/static/closure sources, inventory, comparator, test, RED, and audit unchanged; report and every prohibited path absent; linked/canonical clean.

- [ ] **Step 2: Run formal entry exactly once**

Invoke frozen PowerShell with `task-1-entry-verifier-v7.ps1` and the frozen literal argv. Require exit 0, empty stderr, no file change, and sole stdout:

```text
ENTRY_VERIFIER_FORMAL_PASS|workspaces=4|files=20|comparison=ordinal|contradiction=preserved|v6=absent
```

Any exit, exception, output, identity, count, type, path, signature, absence, Git, or side-effect difference is `ENTRY_VERIFIER_RECOVERY_UNPROVABLE / NO_GO`. Preserve and stop; never rerun formal entry or change any consumed input.

- [ ] **Step 3: Run pre-report closure exactly once**

Invoke the frozen closure in `PreReport` with exact inventory/comparator identities, the literal exact formal terminal, empty report path/hash fields, and fresh workspace. Require exit 0, empty stderr, no file change, and sole stdout:

```text
ENTRY_VERIFIER_CLOSURE_PASS|workspaces=4|files=20|formal=exact|writes=0
```

Any difference is `ENTRY_VERIFIER_RECOVERY_UNPROVABLE / NO_GO`; preserve and stop without report creation.

---

### Task 4: Publish immutable report and final terminal

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/task-1-report.md`
- Read: nine human-authored files, 20 preserved files, 10 absent paths, Git state, and frozen PowerShell.

**Interfaces:**
- Consumes: exact Stage 0, comparator RED/GREEN, static, formal, and pre-report closure PASS evidence.
- Produces: one immutable evidence index and final entry-verifier-only success or first preserved NO_GO.

- [ ] **Step 1: Author the final report once with `apply_patch`**

Index exact design/plan commits/blobs; worktree topology; authority; the consumed failure path/class and later matching 97-byte/hash observation; explicit statement that no retroactive PASS occurred; Stage 0 source/identity/result; comparator test/RED/GREEN identities and terminals; inventory bytes/hash/property orders; static/formal/closure source identities and terminals; all 20 actual/expected byte/hash records; all 10 absence records; nine-file final inventory; and prohibited-action non-occurrence.

Every actual identity is written as a literal measured value. The report contains the exact final terminal once, in a fenced evidence section, but its presence is not PASS until final closure emits it. Never edit the report after creation.

- [ ] **Step 2: Run final closure exactly once**

Freeze the report byte count/SHA-256 and invoke closure in `Final` with exact inventory/comparator/report identities and literal formal terminal. Require exit 0, empty stderr, no file change, and sole stdout:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Any contradiction, omission, output difference, or state change is `ENTRY_VERIFIER_RECOVERY_UNPROVABLE / NO_GO`; never repair or rerun the report/closure.

- [ ] **Step 3: Prove repository and authority closure**

Require HEAD remains this plan commit; tracked/staged/untracked scope is clean; ignored additions are exactly the nine files in the fresh workspace; no `machine/` or other ignored path exists; canonical worktree is clean; v2-v5 and all absence facts remain exact; consumed v6 workspace remains absent; and no external evidence, identity, commit, Docker/GPU/A11/product/model/runtime action occurred.

Stop. A later separately approved design/plan may consume the final PASS. Do not resume the consumed v6 plan or begin child-exit recovery.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserve consumed contradiction without retroactive PASS | Global Constraints; Task 2 Step 1; Task 4 Steps 1-3 |
| Minimal Stage 0 without predecessor comparison | Task 1 Step 1 |
| Plan-pinned Stage 0 source and audit | Task 1 Steps 1-2 |
| Equal-scalar RED before production comparator | Task 1 Steps 2-4 |
| Explicit `Int64` and ordinal-string GREEN behavior | Task 1 Steps 4-5 |
| Eight literal comparator behavior categories | Task 1 Step 5 |
| Human-authored canonical incident/inventory record | Task 2 Step 1 |
| Exact 20 file and 10 absence records | Task 2 Step 1 |
| Parser/AST/type/canonical static admission | Task 2 Step 4 |
| One read-only formal entry | Task 3 Steps 1-2 |
| Independent pre-report and final closure | Task 2 Step 3; Task 3 Step 3; Task 4 Step 2 |
| Exactly nine human files and zero machine files | File Map; Task 4 Steps 1-3 |
| PASS stops before child-exit recovery | Global Constraints; Task 4 Steps 2-3 |
| No Docker/GPU/runtime/OwnerAuthorizationId | Global Constraints; Task 2 Step 4; Task 4 Step 3 |

## Plan Completion Gate

Before committing this plan, require:

1. this plan is one file in a direct-child commit of `c558c0a9a1ce02c3162305b4b7bf6592a905432a`;
2. author, committer, subject, and only changed path are exact;
3. every design requirement maps to a concrete coverage row;
4. nine files, interfaces, property orders, 20 identities, 10 absences, terminals, and namespaces are consistent;
5. no unresolved marker, conflict marker, vague error case, or unspecified behavior remains;
6. every PowerShell code block parses under PowerShell 7.6.4 and Windows PowerShell 5.1 where applicable;
7. the exact Stage 0 block is 3,421 LF/UTF-8 bytes with SHA-256 `82adc690130d2930ca931bd374b086c5681ff047fa459bb04e7d1242c4543644`;
8. linked/canonical worktrees are clean, plan path and both fresh workspaces were absent at authoring entry, and the preserved target remains exactly 97 bytes with frozen SHA-256;
9. the design blob is exact and the final success remains child-exit-not-authorized; and
10. plan authoring executed no Stage 0, failed entry, predecessor source, comparator, static, formal, closure, Docker, GPU, A11, product, model, or runtime command.
