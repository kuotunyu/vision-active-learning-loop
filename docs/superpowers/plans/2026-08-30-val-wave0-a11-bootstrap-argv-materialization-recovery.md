# Wave 0 A11 Bootstrap Argv-Materialization Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace dynamic bootstrap serialization with one identity-frozen canonical command brief, obtain one intended fresh recorder RED, and complete the non-recursive synthetic evidence-host proof under fresh `hostv4-*` identities.

**Architecture:** Layer 0 is a human-authored strict JSON command brief whose exact executable, working directory, and argv are admitted before process creation. A read-only verifier reconstructs the brief with explicit `Utf8JsonWriter` calls and proves absolute validated import flow without calling a dynamic serializer. After one exact RED, a side-effect-free three-export module and minimal leaf host capture eight unique synthetic children into 32 create-new files and close them independently.

**Tech Stack:** PowerShell 7.6.4; Windows PowerShell 5.1 parser compatibility; .NET `System.IO.Path`, `StringComparer`, `JsonDocument`, `Utf8JsonWriter`, `ArrayBufferWriter<byte>`, `ProcessStartInfo.ArgumentList`, `FileStream`, `Task`, `Stopwatch`, and SHA-256; Git; Markdown; ignored append-only evidence.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract`.
- Approved design commit is exactly `b01372fcb147ac1d38ae2ad4ae45cf9f890e8152`; this plan commit must be its one-file direct child.
- Design path is `docs/superpowers/specs/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery-design.md`, Git blob `36ee24379b81e6c6cb0622ae5c7cb4f6475d0630`.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Preserved plan commits `c579527e91abf5d9bde23a26aedcbc73f362dc5d` and `890466f71c6730e07774c4568c7b50f70db8ebe2`, their workspaces, sources, terminals, and absent machine paths are immutable.
- The immediate predecessor terminal remains `BOOTSTRAP_PATH_STATIC_REJECTED / NO_GO`; never execute its static verifier, RED test, or RED module.
- The older predecessor terminal remains `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`; never execute its RED test or module.
- Earlier `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, `CUDA_OBSERVATION_UNPROVABLE / NO_GO`, artifacts, images, inventories, digests, reports, leases, owner identities, and attempts remain immutable.
- The only new execution workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/`, and it must be absent at entry.
- Create every human-authored ignored file with `apply_patch`; never generate source, command-brief JSON, manifest JSON, or report content with a script or shell redirection.
- The evidence host may create only the exact 32 predetermined `machine/hostv4-*` files.
- Once a process consumes a source, brief, fixture, manifest, command ID, or destination, it is immutable.
- Any defect before formal static start requires a new append-only identity. Any unexpected formal static, RED, host, or closure result closes this plan; do not fix, replace, or retry it.
- Every path-bearing process argument is a literal fully qualified Windows path. No receiver supports a relative fallback, module-name search, PATH search, or alternate candidate.
- Bootstrap executable sources contain no `JsonSerializer.Serialize` or `ConvertTo-Json`; canonical brief reconstruction uses only explicit `Utf8JsonWriter` methods with `UnsafeRelaxedJsonEscaping`.
- Do not inspect or execute Docker CLI, Docker Desktop processes, Docker/WSL pipes, builders, images, containers, caches, volumes, GPU, `nvidia-smi`, CUDA, CPU baseline, dependencies, model, A11 launcher, entry child, formal runtime, Wave 1, or product Tasks 2-8.
- Do not create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`.
- Do not modify product code, the seven-file A11 implementation allowlist, external evidence, another repository, a remote, or Git history.
- Do not push, merge, tag, release, amend, rebase, reset, stash, or delete preserved evidence.
- The only success terminal is `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.
- Execution creates ignored evidence only; there is no tracked implementation commit after this plan commit.

## Normative Inputs

- Approved design: commit `b01372fcb147ac1d38ae2ad4ae45cf9f890e8152`, blob `36ee24379b81e6c6cb0622ae5c7cb4f6475d0630`.
- Immediate failed plan: commit `c579527e91abf5d9bde23a26aedcbc73f362dc5d`.
- Immediate failed workspace: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/`.
- Immediate failed files:
  - `task-1-bootstrap-path-static-v3.ps1`, 7,521 bytes, SHA-256 `636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9`;
  - `task-1-entry-gate-v3.ps1`, 5,151 bytes, SHA-256 `fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19`;
  - `task-1-evidence-module-red-v3.psm1`, 97 bytes, SHA-256 `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136`;
  - `task-1-evidence-tests-v3.ps1`, 9,012 bytes, SHA-256 `db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c`.
- Older failed workspace: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/`.
- Older failed files:
  - `task-1-entry-gate.ps1`, 3,541 bytes, SHA-256 `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b`;
  - `task-1-evidence-module-red.psm1`, 103 bytes, SHA-256 `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc`;
  - `task-1-evidence-tests.ps1`, 4,420 bytes, SHA-256 `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65`.
- Frozen PowerShell executable: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`, 301,368 bytes, SHA-256 `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`, valid Authenticode signature.
- Repository root: `<repo>\.worktrees\wave0-model-contract`.
- Canonical worktree: `<repo>`.

## File and Interface Map

Execution changes no tracked file. Create these ignored human-authored files under the fresh workspace:

| Path | Responsibility |
|---|---|
| `task-1-entry-gate-v4.ps1` | Audit copy of exact Git, preservation, absence, executable, and authority entry proof. |
| `task-1-evidence-module-red-v4.psm1` | Fresh test-first RED subject with no recorder exports. |
| `task-1-evidence-tests-v4.ps1` | Complete absolute-path RED/GREEN module and structural tests. |
| `task-1-red-command-v4.json` | Canonical immutable executable/working-directory/argv brief. |
| `task-1-bootstrap-command-static-v4.ps1` | Verify command-brief bytes, schema, canonical form, argv, and validated import flow. |
| `task-1-bootstrap-red-brief-v4.md` | Index exact static tool result and formal RED command/result contract. |
| `task-1-evidence-module-green-v4.psm1` | Validate manifests, capture raw children, publish results, and verify machine files. |
| `task-1-evidence-host-v4.ps1` | Minimal non-recursive leaf host. |
| `task-1-static-verifier-v4.ps1` | Parser, AST, path-flow, writer, import, write-site, and forbidden-command gates. |
| `task-1-synthetic-fixture-v4.ps1` | Deterministic raw, volume, argv, nonzero, and timeout behavior. |
| `task-1-invalid-executable-v4.exe` | Deterministic ASCII non-executable start-failure subject. |
| `task-1-invalid-manifests-v4.ps1` | Read-only closed-schema, path, collision, and link-rejection tests. |
| `task-1-preexisting-v4.stdout.bin` | Apply-patch no-clobber sentinel. |
| `task-1-closure-verifier-v4.ps1` | Independent source/brief/manifest/machine/result/inventory closure. |
| `task-1-report.md` | Final evidence index and first exact terminal. |

Create eight canonical manifests:

| Manifest | Command ID | Planned result |
|---|---|---|
| `task-1-manifest-hostv4-001-unit-green.json` | `hostv4-001-unit-green` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv4-002-raw.json` | `hostv4-002-raw` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv4-003-high-volume.json` | `hostv4-003-high-volume` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv4-004-argv.json` | `hostv4-004-argv` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv4-005-nonzero.json` | `hostv4-005-nonzero` | exit 23, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv4-006-timeout.json` | `hostv4-006-timeout` | `COMMAND_TIMEOUT` |
| `task-1-manifest-hostv4-007-start-failure.json` | `hostv4-007-start-failure` | exit -1, `COMMAND_START_FAILURE` |
| `task-1-manifest-hostv4-008-closure.json` | `hostv4-008-closure` | exit 0, `COMMAND_COMPLETE` |

Each command creates exactly `.stdout.bin`, `.stderr.bin`, `.result.json`, and `.result.sha256` under `machine/`, for 32 machine files total.

The GREEN module exports exactly:

```powershell
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

The host accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [string] $A11HostManifestPath,
    [Parameter(Mandatory)] [string] $A11HostModulePath,
    [Parameter(Mandatory)] [string] $A11HostExpectedWorkspace
)
```

The test accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Red', 'Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $ModulePath,
    [Parameter(Mandatory)] [string] $ExpectedModulePath,
    [Parameter(Mandatory)] [long] $ExpectedModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [string] $HostPath,
    [string] $FixturePath,
    [string] $InvalidManifestTestPath
)
```

The closure verifier accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [string[]] $ExpectedCommandIds,
    [switch] $RequireFinalInventory
)
```

---

### Task 1: Prove entry, materialize canonical argv, and obtain the intended RED

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-entry-gate-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-evidence-module-red-v4.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-evidence-tests-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-red-command-v4.json`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-bootstrap-command-static-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-bootstrap-red-brief-v4.md`

**Interfaces:**
- Consumes: exact plan/design lineage, two preserved NO_GO inventories, four absent older machine paths, signed PowerShell identity, and clean linked/canonical worktrees.
- Produces: one `BOOTSTRAP_ARGV_STATIC_PASS` and one immutable RED with exit 41, exact stdout, empty stderr, and zero machine files.

- [ ] **Step 1: Run the exact read-only entry before creating the workspace**

Execute from the linked worktree. Normalize Git paths before comparing them.

```powershell
$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery'
$V3Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery'
$V2Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery.md'
$ExpectedBranch = 'codex/wave0-model-contract'
$ExpectedDesign = 'b01372fcb147ac1d38ae2ad4ae45cf9f890e8152'
$ExpectedPlan = git rev-parse HEAD

$ObservedRoot = [IO.Path]::GetFullPath((git rev-parse --show-toplevel))
if (-not [StringComparer]::OrdinalIgnoreCase.Equals($ObservedRoot, $RepositoryRoot)) { throw 'worktree root mismatch' }
$GitDir = [IO.Path]::GetFullPath((git rev-parse --git-dir), $RepositoryRoot)
$GitCommon = [IO.Path]::GetFullPath((git rev-parse --git-common-dir), $RepositoryRoot)
if ([StringComparer]::OrdinalIgnoreCase.Equals($GitDir, $GitCommon)) { throw 'not a linked worktree' }
if (-not [string]::IsNullOrEmpty([string](git rev-parse --show-superproject-working-tree))) { throw 'submodule detected' }
if ((git branch --show-current) -cne $ExpectedBranch) { throw 'branch mismatch' }
if ((git rev-parse 'HEAD^') -cne $ExpectedDesign) { throw 'plan parent mismatch' }
$Changed = @(git diff-tree --no-commit-id --name-only -r HEAD)
if ($Changed.Count -ne 1 -or $Changed[0] -cne $PlanPath) { throw 'plan path mismatch' }
if ((git show -s --format='%an <%ae>' HEAD) -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'author mismatch' }
if ((git show -s --format='%cn <%ce>' HEAD) -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'committer mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree dirty' }
if (@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'canonical worktree dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging nonempty' }
if (Test-Path -LiteralPath $Workspace) { throw 'fresh workspace already exists' }
if ((git rev-parse "${ExpectedDesign}:$DesignPath") -cne '36ee24379b81e6c6cb0622ae5c7cb4f6475d0630') { throw 'design blob mismatch' }

$ExpectedV3 = [ordered]@{
    'task-1-bootstrap-path-static-v3.ps1' = @(7521, '636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9')
    'task-1-entry-gate-v3.ps1' = @(5151, 'fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19')
    'task-1-evidence-module-red-v3.psm1' = @(97, 'c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136')
    'task-1-evidence-tests-v3.ps1' = @(9012, 'db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c')
}
$ExpectedV2 = [ordered]@{
    'task-1-entry-gate.ps1' = @(3541, '3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b')
    'task-1-evidence-module-red.psm1' = @(103, 'a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc')
    'task-1-evidence-tests.ps1' = @(4420, '8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65')
}
foreach ($Inventory in @(@($V3Workspace, $ExpectedV3), @($V2Workspace, $ExpectedV2))) {
    $Root = [string] $Inventory[0]
    $Expected = $Inventory[1]
    $Files = @(Get-ChildItem -LiteralPath $Root -File -Recurse -Force)
    if ($Files.Count -ne $Expected.Count) { throw "preserved inventory count mismatch: $Root" }
    foreach ($Entry in $Expected.GetEnumerator()) {
        $Path = Join-Path $Root $Entry.Key
        if ((Get-Item -LiteralPath $Path).Length -ne $Entry.Value[0]) { throw "preserved byte mismatch: $($Entry.Key)" }
        if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant() -cne $Entry.Value[1]) { throw "preserved hash mismatch: $($Entry.Key)" }
    }
    if (Test-Path -LiteralPath (Join-Path $Root 'machine')) { throw "preserved machine directory appeared: $Root" }
}

$FailedMachine = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\machine'
foreach ($Name in @('preformal-003-recorder-red-verify.stdout.bin','preformal-003-recorder-red-verify.stderr.bin','preformal-003-recorder-red-verify.result.json','preformal-003-recorder-red-verify.result.sha256')) {
    if (Test-Path -LiteralPath (Join-Path $FailedMachine $Name)) { throw "preserved absent path appeared: $Name" }
}
$Pwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if ((Get-Item -LiteralPath $Pwsh).Length -ne 301368) { throw 'PowerShell byte count mismatch' }
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Pwsh).Hash.ToLowerInvariant() -cne 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f') { throw 'PowerShell digest mismatch' }
if ((Get-AuthenticodeSignature -LiteralPath $Pwsh).Status -cne 'Valid') { throw 'PowerShell signature invalid' }

"BOOTSTRAP_ARGV_ENTRY_PASS|plan=$ExpectedPlan|workspace=absent|v3_files=4|v2_files=3|linked=clean|canonical=clean"
```

Require the exact PASS prefix. Any failure stops with no new workspace.

- [ ] **Step 2: Create the audit entry, RED module, and complete test first**

Use `apply_patch`. The audit entry contains Step 1 with the literal plan commit emitted by the PASS and is never executed after workspace creation.

Create `task-1-evidence-module-red-v4.psm1` with LF and UTF-8 without BOM:

```powershell
Set-StrictMode -Version Latest

# Intentional hostv4 RED subject: recorder exports do not exist.
```

Require 97 bytes and SHA-256 `dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb`.

Create the complete test before any GREEN source. Its closed file validator is:

```powershell
function Assert-A11AbsoluteFile {
    param(
        [Parameter(Mandatory)] [string] $Candidate,
        [Parameter(Mandatory)] [string] $ExpectedPath,
        [Parameter(Mandatory)] [string] $AllowedRoot,
        [Parameter(Mandatory)] [long] $ExpectedByteCount,
        [Parameter(Mandatory)] [string] $ExpectedSha256
    )
    if (-not [IO.Path]::IsPathFullyQualified($Candidate)) { throw 'path is not fully qualified' }
    if (-not [IO.Path]::IsPathFullyQualified($ExpectedPath)) { throw 'expected path is not fully qualified' }
    if (-not [IO.Path]::IsPathFullyQualified($AllowedRoot)) { throw 'allowed root is not fully qualified' }
    $Canonical = [IO.Path]::GetFullPath($Candidate)
    $ExpectedCanonical = [IO.Path]::GetFullPath($ExpectedPath)
    $RootCanonical = [IO.Path]::GetFullPath($AllowedRoot)
    if (-not [StringComparer]::OrdinalIgnoreCase.Equals($Canonical, $ExpectedCanonical)) { throw 'canonical path mismatch' }
    $Relative = [IO.Path]::GetRelativePath($RootCanonical, $Canonical)
    if ([IO.Path]::IsPathFullyQualified($Relative) -or $Relative -eq '..' -or $Relative.StartsWith('..' + [IO.Path]::DirectorySeparatorChar, [StringComparison]::Ordinal)) { throw 'path escapes allowed root' }
    if (-not (Test-Path -LiteralPath $Canonical -PathType Leaf)) { throw 'ordinary file missing' }
    $Cursor = Get-Item -LiteralPath $Canonical -Force
    while ($null -ne $Cursor) {
        if (($Cursor.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw 'linked path rejected' }
        $Cursor = $Cursor.Parent
    }
    if ((Get-Item -LiteralPath $Canonical).Length -ne $ExpectedByteCount) { throw 'file byte count mismatch' }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Canonical).Hash.ToLowerInvariant() -cne $ExpectedSha256) { throw 'file digest mismatch' }
    return $Canonical
}
```

The test imports exactly once and only through the validated return value:

```powershell
$ValidatedModulePath = Assert-A11AbsoluteFile -Candidate $ModulePath -ExpectedPath $ExpectedModulePath -AllowedRoot $WorkspacePath -ExpectedByteCount $ExpectedModuleByteCount -ExpectedSha256 $ExpectedModuleSha256
$LibraryOnly = 'caller-sentinel'
$BeforePid = $PID
$Module = Import-Module -Name $ValidatedModulePath -Scope Local -Force -PassThru
if ($LibraryOnly -cne 'caller-sentinel') { throw 'caller LibraryOnly changed' }
if ($BeforePid -ne $PID) { throw 'caller PID changed' }
$ExpectedExports = @('Invoke-A11RecordedChild','Read-A11EvidenceManifest','Test-A11MachineEvidence') | Sort-Object
$ActualExports = @($Module.ExportedFunctions.Keys | Sort-Object)
if ($Mode -ceq 'Red') {
    if ($ActualExports.Count -ne 0) { throw 'RED export set is not empty' }
    [Console]::Out.WriteLine('EXPECTED_RED|required export set missing')
    exit 41
}
if ($ActualExports.Count -ne $ExpectedExports.Count) { throw 'GREEN export count mismatch' }
for ($Index = 0; $Index -lt $ExpectedExports.Count; $Index++) {
    if ($ActualExports[$Index] -cne $ExpectedExports[$Index]) { throw "GREEN export mismatch at index $Index" }
}
```

The GREEN branch also parses module, host, fixture, and invalid-manifest test by validated absolute path; rejects dot-source, `Invoke-Expression`, `Start-Process`, module top-level `return`/`exit`, and assignments to automatic/constant/read-only variables; invokes the invalid-manifest suite with validated module/workspace/host/fixture paths; requires its sole output `INVALID_MANIFEST_TESTS_PASS`; then emits only `EVIDENCE_TEST_SUITE_PASS` plus newline. Neither RED nor GREEN test flow contains `JsonSerializer.Serialize` or `ConvertTo-Json`.

- [ ] **Step 3: Create the canonical command brief and static verifier with apply_patch**

Create `task-1-red-command-v4.json` as exactly this one compact line plus LF:

```json
{"schema_version":1,"executable_path":"C:\\Users\\<user>\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\powershell\\pwsh.exe","executable_byte_count":301368,"executable_sha256":"db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f","working_directory":"<repo>\\.worktrees\\wave0-model-contract","argv":["-NoProfile","-NonInteractive","-File","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\\task-1-evidence-tests-v4.ps1","-Mode","Red","-ModulePath","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\\task-1-evidence-module-red-v4.psm1","-ExpectedModulePath","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\\task-1-evidence-module-red-v4.psm1","-ExpectedModuleByteCount","97","-ExpectedModuleSha256","dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb","-WorkspacePath","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery"]}
```

Require 1,461 bytes and SHA-256 `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6` before formal static execution.

Create `task-1-bootstrap-command-static-v4.ps1` with this exact interface:

```powershell
param(
    [Parameter(Mandatory)] [string] $TestPath,
    [Parameter(Mandatory)] [string] $ExpectedTestPath,
    [Parameter(Mandatory)] [long] $ExpectedTestByteCount,
    [Parameter(Mandatory)] [string] $ExpectedTestSha256,
    [Parameter(Mandatory)] [string] $ModulePath,
    [Parameter(Mandatory)] [string] $ExpectedModulePath,
    [Parameter(Mandatory)] [long] $ExpectedModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedModuleSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [string] $CommandBriefPath,
    [Parameter(Mandatory)] [long] $ExpectedCommandBriefByteCount,
    [Parameter(Mandatory)] [string] $ExpectedCommandBriefSha256
)
```

It duplicates the closed absolute/containment/link/bytes/hash helper without importing a module. It parses the test and requires exactly one `Import-Module`; the `-Name` element must be `$ValidatedModulePath`, never `$ModulePath`.

Read the command brief as bytes, reject BOM, require final byte `0x0A` and no other whitespace after the root object, parse with `JsonDocument`, reject duplicate root property names, require exact property order and types, and require the exact six-field values above. Rebuild canonical bytes without a serializer:

```powershell
$Buffer = [Buffers.ArrayBufferWriter[byte]]::new()
$Options = [Text.Json.JsonWriterOptions]::new()
$Options.Indented = $false
$Options.Encoder = [Text.Encodings.Web.JavaScriptEncoder]::UnsafeRelaxedJsonEscaping
$Writer = [Text.Json.Utf8JsonWriter]::new($Buffer, $Options)
$Writer.WriteStartObject()
$Writer.WritePropertyName('schema_version')
$Writer.WriteNumberValue([int] 1)
$Writer.WritePropertyName('executable_path')
$Writer.WriteStringValue([string] $ExecutablePath)
$Writer.WritePropertyName('executable_byte_count')
$Writer.WriteNumberValue([long] 301368)
$Writer.WritePropertyName('executable_sha256')
$Writer.WriteStringValue('db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f')
$Writer.WritePropertyName('working_directory')
$Writer.WriteStringValue([string] $RepositoryRoot)
$Writer.WritePropertyName('argv')
$Writer.WriteStartArray()
foreach ($Argument in $ExpectedArguments) { $Writer.WriteStringValue([string] $Argument) }
$Writer.WriteEndArray()
$Writer.WriteEndObject()
$Writer.Flush()
$CanonicalWithoutLf = $Buffer.WrittenMemory.ToArray()
$Canonical = [byte[]]::new($CanonicalWithoutLf.Length + 1)
[Array]::Copy($CanonicalWithoutLf, $Canonical, $CanonicalWithoutLf.Length)
$Canonical[-1] = 0x0A
if ($Canonical.Length -ne $BriefBytes.Length) { throw 'command brief canonical length mismatch' }
for ($Index = 0; $Index -lt $Canonical.Length; $Index++) {
    if ($Canonical[$Index] -ne $BriefBytes[$Index]) { throw "command brief canonical byte mismatch at index $Index" }
}
```

The verifier also requires exact argv order, unique switch tokens, deliberate equality only for the two module-path values, four fully qualified path-bearing values, no predecessor fragment, no dynamic serializer, and no machine path.

Success emits only:

```text
BOOTSTRAP_ARGV_STATIC_PASS|brief=canonical|absolute_args=4|validated_imports=1|dynamic_serializers=0|predecessor_args=0
```

- [ ] **Step 4: Perform preformal parser/API review without executing the static verifier**

Parse the test and static verifier through frozen PowerShell 7.6.4 and Windows PowerShell 5.1 parser APIs. Inspect AST/text and require zero parser errors, no `JsonSerializer.Serialize`, no `ConvertTo-Json` in the static verifier, no shell-string invocation, and the exact `Utf8JsonWriter` calls above. Recompute the RED module and brief bytes/hashes. Require no `machine/` directory.

This review may inspect source and exercise an isolated in-memory `Utf8JsonWriter` microcheck that does not import or invoke any new workspace source. It may not execute the static verifier or RED test. Any source defect discovered here requires a new unused append-only source path before formal start.

- [ ] **Step 5: Run the formal static verifier exactly once**

Measure the immutable test identity, then invoke frozen PowerShell with literal absolute path arguments and the observed scalar identity:

```powershell
$Test = '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-tests-v4.ps1'
$TestBytes = (Get-Item -LiteralPath $Test).Length
$TestSha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath $Test).Hash.ToLowerInvariant()
& 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' `
    -NoProfile -NonInteractive `
    -File '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-bootstrap-command-static-v4.ps1' `
    -TestPath '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-tests-v4.ps1' `
    -ExpectedTestPath '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-tests-v4.ps1' `
    -ExpectedTestByteCount $TestBytes `
    -ExpectedTestSha256 $TestSha256 `
    -ModulePath '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-module-red-v4.psm1' `
    -ExpectedModulePath '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-module-red-v4.psm1' `
    -ExpectedModuleByteCount 97 `
    -ExpectedModuleSha256 'dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb' `
    -WorkspacePath '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery' `
    -CommandBriefPath '<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-red-command-v4.json' `
    -ExpectedCommandBriefByteCount 1461 `
    -ExpectedCommandBriefSha256 'b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6'
```

Require exact static PASS, exit 0, empty stderr, and unchanged sources. Any difference is `BOOTSTRAP_ARGV_STATIC_REJECTED / NO_GO`; preserve and stop without RED.

- [ ] **Step 6: Freeze the RED brief and execute the new RED exactly once**

After static PASS, use `apply_patch` to create `task-1-bootstrap-red-brief-v4.md` recording executable/brief/test/module/static identities, literal working directory, environment, exact argv, static tool result, expected exit/stdout/stderr, and zero machine destinations. Do not edit it after creation.

Run the exact executable and argv from `task-1-red-command-v4.json` once. Require exit 41, stdout exactly `EXPECTED_RED|required export set missing` plus the platform newline, empty stderr, zero machine files, and unchanged source/brief identities.

Any path, import, parser, output, exit, or inventory difference is `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`. Preserve it and stop; never change an argument, source, brief, working directory, or environment and never rerun.

---

### Task 2: Implement the GREEN recorder and non-recursive host

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-evidence-module-green-v4.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-evidence-host-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-static-verifier-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-synthetic-fixture-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-invalid-executable-v4.exe`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-invalid-manifests-v4.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-preexisting-v4.stdout.bin`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-closure-verifier-v4.ps1`

**Interfaces:**
- Consumes: exact intended RED, immutable v4 test, and canonical bootstrap brief/static PASS.
- Produces: side-effect-free three-export module, three-parameter leaf host, deterministic fixtures, independent closure, and GREEN static PASS before any machine child.

- [ ] **Step 1: Implement private path and canonical-manifest helpers**

Only after the RED passes, create the GREEN module. Module scope permits `Set-StrictMode`, function definitions, and final `Export-ModuleMember` only.

Define private `Assert-A11AbsolutePath` with `Candidate`, `ExpectedPath`, `AllowedRoot`, `ExpectedKind`, optional byte/hash identity, and a private test-only attribute provider. Reject null/whitespace, wildcard, provider-qualified, URI, UNC, device, ADS, trailing ambiguity, relative, escaping, linked, wrong-kind, wrong-byte-count, and wrong-hash paths. Return one canonical backslash-form path.

Define `ConvertFrom-A11CanonicalManifestBytes`. Decode with strict `UTF8Encoding(false, true)`, reject BOM, duplicate properties recursively, extra/missing/reordered fields, noncompact bytes, and missing/multiple terminal LF. Rebuild with ordered dictionaries and `ConvertTo-Json -Compress -Depth 12`, append LF, and require byte equality.

The root manifest fields are exactly:

```powershell
@(
    'schema_version','command_id','purpose',
    'host_source_path','host_source_byte_count','host_source_sha256',
    'module_source_path','module_source_byte_count','module_source_sha256',
    'executable_path','executable_byte_count','executable_sha256',
    'argv','working_directory','environment_allowlist','stdin_policy',
    'stdout_capture_path','stderr_capture_path','result_path','result_digest_path',
    'timeout_policy','permitted_child_count',
    'command_source_paths','command_source_byte_counts','command_source_sha256'
)
```

Require schema 4, command ID `^hostv4-[0-9]{3}-[a-z0-9-]+$`, environment order `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, timeout order `mode`, `milliseconds`, stdin `closed`, child count 1, lowercase 64-hex hashes, equal source-vector lengths, exact source identities, and four absent command-derived destinations.

- [ ] **Step 2: Implement manifest read and independent machine verification**

Define:

```powershell
function Read-A11EvidenceManifest {
    param(
        [Parameter(Mandatory)] [string] $ManifestPath,
        [Parameter(Mandatory)] [string] $ExpectedWorkspace,
        [Parameter(Mandatory)] [string] $ExpectedHostPath,
        [Parameter(Mandatory)] [string] $ExpectedModulePath
    )
}
```

Validate all inputs before file access. Read exact manifest bytes, verify host/module/executable/source identities, require working directory exactly the repository root, and require all outputs under the fresh `machine` directory. Return an ordered manifest enriched only in memory with `manifest_path`, `manifest_byte_count`, and `manifest_sha256`.

Define:

```powershell
function Test-A11MachineEvidence {
    param([Parameter(Mandatory)] [System.Collections.IDictionary] $Manifest)
}
```

Require exactly four ordinary non-linked files. Recompute raw byte counts/hashes, parse canonical result order/bytes, verify manifest/executable/argv/environment/path/result fields, enforce terminal/exit/timeout/start-exception consistency, and verify digest-file bytes. Return an ordered verification object and write nothing.

- [ ] **Step 3: Implement one-child raw capture and create-new publication**

Define:

```powershell
function Invoke-A11RecordedChild {
    param([Parameter(Mandatory)] [System.Collections.IDictionary] $Manifest)
}
```

Construct only `ProcessStartInfo`:

```powershell
$StartInfo = [Diagnostics.ProcessStartInfo]::new()
$StartInfo.FileName = [string] $Manifest.executable_path
$StartInfo.WorkingDirectory = [string] $Manifest.working_directory
$StartInfo.UseShellExecute = $false
$StartInfo.RedirectStandardInput = $true
$StartInfo.RedirectStandardOutput = $true
$StartInfo.RedirectStandardError = $true
$StartInfo.CreateNoWindow = $true
$StartInfo.Environment.Clear()
foreach ($Entry in $Manifest.environment_allowlist.GetEnumerator()) { $StartInfo.Environment[[string] $Entry.Key] = [string] $Entry.Value }
foreach ($Argument in @($Manifest.argv)) { [void] $StartInfo.ArgumentList.Add([string] $Argument) }
```

Never populate `Arguments`. Open stdout/stderr with `FileMode.CreateNew`, `FileAccess.Write`, `FileShare.None`, 65,536-byte buffers, async and write-through options. Start one process; store ID only in `$ChildProcessId`; close stdin; begin both `BaseStream.CopyToAsync` calls; and wait for the same process.

For timeout `none`, wait once. For `bounded`, race `WaitForExitAsync` and one `Task.Delay`; if delay wins, call `Kill($true)` once and await the same PID. Always await both copy tasks, flush, close, and recompute raw identities. Start exception produces zero-byte streams, PID -1, exit -1, nonempty exception type/message, and `COMMAND_START_FAILURE`. Normal completion produces `COMMAND_COMPLETE`; bounded kill produces `COMMAND_TIMEOUT`.

Publish canonical ordered result JSON and lowercase digest plus LF through create-new streams. Result fields are exactly:

```powershell
@(
    'schema_version','command_id','manifest_path','manifest_byte_count','manifest_sha256',
    'executable_path','executable_byte_count','executable_sha256','argv','working_directory',
    'environment_allowlist','stdin_policy','started_at_utc','finished_at_utc',
    'monotonic_start','monotonic_finish','child_process_id','exit_code','timed_out',
    'start_exception_type','start_exception_message',
    'stdout_path','stdout_byte_count','stdout_sha256',
    'stderr_path','stderr_byte_count','stderr_sha256','terminal'
)
```

Export exactly the three public functions.

- [ ] **Step 4: Implement the minimal absolute leaf host**

Create the host with the exact three parameters. Validate and canonicalize all three before import, require manifest/module below the expected workspace, read frozen host/module identities from the manifest with `JsonDocument`, verify bytes/hashes, and import only `$ValidatedModulePath` with local scope.

Require exact exports. Call `Read-A11EvidenceManifest`, `Invoke-A11RecordedChild`, and `Test-A11MachineEvidence` once each. Never dot-source, self-capture, recurse, replace a manifest, retry, or choose another path.

Success emits:

```powershell
[Console]::Out.WriteLine("HOST_CAPTURE_COMPLETE|command_id=$($Verification.command_id)|terminal=$($Verification.terminal)")
```

Before-machine static rejection is `EVIDENCE_HOST_STATIC_REJECTED / NO_GO`; missing/partial four-file evidence is `EVIDENCE_HOST_UNPROVABLE / NO_GO`; a complete invalid set is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`.

- [ ] **Step 5: Create deterministic fixtures and invalid-manifest tests**

Create the fixture:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Raw','HighVolume','Argv','Nonzero','Timeout')] [string] $Mode,
    [Parameter(ValueFromRemainingArguments)] [string[]] $Payload
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
switch ($Mode) {
    'Raw' {
        $Stdout = [byte[]] (0x41,0x00,0xE4,0xB8,0xAD,0x0A,0x5A)
        $Stderr = [byte[]] (0x45,0x52,0x52,0x00,0xFF)
        [Console]::OpenStandardOutput().Write($Stdout, 0, $Stdout.Length)
        [Console]::OpenStandardError().Write($Stderr, 0, $Stderr.Length)
        exit 0
    }
    'HighVolume' {
        $OutBlock = [byte[]]::new(1048576)
        $ErrBlock = [byte[]]::new(1048576)
        for ($Index = 0; $Index -lt $OutBlock.Length; $Index++) { $OutBlock[$Index] = 0x4F }
        for ($Index = 0; $Index -lt $ErrBlock.Length; $Index++) { $ErrBlock[$Index] = 0x45 }
        [Console]::OpenStandardOutput().Write($OutBlock, 0, $OutBlock.Length)
        [Console]::OpenStandardError().Write($ErrBlock, 0, $ErrBlock.Length)
        exit 0
    }
    'Argv' { [Console]::Out.Write((ConvertTo-Json -InputObject @($Payload) -Compress)); exit 0 }
    'Nonzero' { [Console]::Out.Write('controlled-out'); [Console]::Error.Write('controlled-error'); exit 23 }
    'Timeout' { [Console]::Out.Write('timeout-started'); [Console]::Out.Flush(); Start-Sleep -Seconds 5; exit 0 }
}
```

Create invalid executable as exact ASCII `A11 V4 INVALID EXECUTABLE` plus LF and sentinel as exact ASCII `A11-V4-PREEXISTING-SENTINEL` plus LF.

The invalid-manifest test imports the validated GREEN module and uses manifest 002, whose outputs are absent while command 001 runs, as its valid baseline. Through module-scope calls to private pure validators, construct in-memory byte cases without writing JSON. Require rejection of relative, UNC, provider, URI, ADS, escaping, linked, duplicate, extra, missing, reordered, noncanonical-hash, source-vector mismatch, output collision, and preexisting sentinel cases. Require sentinel hash unchanged. Emit only `INVALID_MANIFEST_TESTS_PASS`.

- [ ] **Step 6: Create closure/static verifiers and run the GREEN static gate once**

The closure verifier is complete before any host child. It reads only absolute validated paths, writes nothing, verifies explicit command IDs and identities, rejects missing/extra human or machine files, and supports pre-report and final-report inventories.

The static verifier parses test, GREEN module, host, invalid-manifest test, fixture, and closure under PowerShell 7.6.4 and Windows PowerShell 5.1. AST gates require no dot-source, dynamic evaluation, `Start-Process`, shell string, redirection syntax, module top-level side effect, or assignment to automatic/constant/read-only variables. Require exact host parameters and exports, validated path flows, create-new write sites limited to 32 destinations, no predecessor source/path execution, and no Docker/GPU/A11/product/Git/network/runtime command.

Run once and require:

```text
EVIDENCE_HOST_STATIC_PASS|exports=3|absolute_flows=all|dot_source=0|forbidden_assignments=0|forbidden_commands=0
```

No machine path may exist. Any failure is `EVIDENCE_HOST_STATIC_REJECTED / NO_GO`; freeze all executable GREEN sources after PASS.

---

### Task 3: Author and execute eight unique hostv4 captures

**Files:**
- Create: eight `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-manifest-hostv4-*.json` files.
- Create by host only: 32 `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/machine/hostv4-*` files.
- Modify existing source: none.

**Interfaces:**
- Consumes: frozen GREEN/static PASS and exact source identities.
- Produces: seven behavior captures plus one independent closure capture; each ID runs at most once.

- [ ] **Step 1: Freeze identities and create all manifests with apply_patch**

Measure literal canonical path, byte count, and lowercase SHA-256 for host, module, PowerShell, test, fixture, invalid executable, invalid-manifest test, closure verifier, sentinel, bootstrap brief, and every command source. Manually author compact schema-4 JSON; do not synthesize it.

Every manifest uses fully qualified paths, repository-root working directory, environment order `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, stdin `closed`, one child, and four exact absent destinations. Commands 001-006 and 008 use frozen PowerShell; 007 uses the invalid executable with empty argv.

PowerShell argv tails are:

| ID | argv after `-NoProfile -NonInteractive -File` |
|---|---|
| 001 | absolute test path; `-Mode Green`; GREEN module path and same expected path; literal module bytes/hash; workspace, host, fixture, invalid-manifest-test paths |
| 002 | fixture path; `-Mode Raw` |
| 003 | fixture path; `-Mode HighVolume` |
| 004 | fixture path; `-Mode Argv -Payload`; `alpha beta`; empty string; `quote"value`; `中 文` |
| 005 | fixture path; `-Mode Nonzero` |
| 006 | fixture path; `-Mode Timeout` |
| 008 | closure path; workspace; literal `-ExpectedCommandIds` values 001 through 007 |

Timeout is `none`/0 for 001-005, 007, 008 and `bounded`/500 for 006. Require all 32 destinations absent, every manifest canonical/ordinary/non-linked, all identities exact, and no relative or predecessor path.

- [ ] **Step 2: Execute hostv4-001 exactly once**

Invoke frozen PowerShell with literal absolute host, 001 manifest, GREEN module, and workspace arguments. Require host exit 0, `HOST_CAPTURE_COMPLETE`, exactly four 001 files, child exit 0, `COMMAND_COMPLETE`, stdout exactly `EVIDENCE_TEST_SUITE_PASS` plus newline, empty stderr, and independent result/digest recomputation. Stop on any difference; never start 001 again.

- [ ] **Step 3: Execute hostv4-002 exactly once**

Require stdout bytes `41 00 E4 B8 AD 0A 5A`, stderr bytes `45 52 52 00 FF`, exit 0, `COMMAND_COMPLETE`, and complete result/digest. Stop on mismatch.

- [ ] **Step 4: Execute hostv4-003 exactly once**

Require exactly 1,048,576 stdout bytes all `0x4F`, 1,048,576 stderr bytes all `0x45`, exit 0, no timeout/deadlock, and complete result/digest. Stop on mismatch.

- [ ] **Step 5: Execute hostv4-004 exactly once**

Require compact JSON stdout for exactly `alpha beta`, empty string, `quote"value`, and `中 文`, no terminal newline, empty stderr, result argv equal manifest argv, exit 0, and complete result/digest. Stop on mismatch.

- [ ] **Step 6: Execute hostv4-005 exactly once**

Require stdout `controlled-out`, stderr `controlled-error`, exit 23, `timed_out=false`, terminal `COMMAND_COMPLETE`, and host exit 0 because capture completed. Stop on mismatch.

- [ ] **Step 7: Execute hostv4-006 exactly once**

Require stdout begins `timeout-started`, `timed_out=true`, terminal `COMMAND_TIMEOUT`, one killed PID, completion after start, complete stderr/result/digest, and host exit 0. Stop on mismatch; never restart it.

- [ ] **Step 8: Execute hostv4-007 exactly once**

Require zero-byte stdout/stderr, PID -1, exit -1, `timed_out=false`, nonempty Win32 exception type/message, `COMMAND_START_FAILURE`, complete result/digest, and host exit 0. Stop on mismatch; never substitute an executable.

- [ ] **Step 9: Execute hostv4-008 exactly once**

Require child exit 0, `COMMAND_COMPLETE`, stdout exact prefix `EVIDENCE_MACHINE_CLOSURE_PASS|commands=7|machine_files=28`, empty stderr, and its own complete four-file set. Its closure child rejects any missing, extra, linked, noncanonical, colliding, wrong-path, wrong-terminal, or digest-mismatched evidence in 001-007.

---

### Task 4: Close the 32-file inventory and publish the terminal

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/task-1-report.md`
- Read: all 23 human-authored workspace files, 32 machine files, both predecessor inventories, and Git state.
- Modify tracked files: none.

**Interfaces:**
- Consumes: exact eight hostv4 results, frozen sources, bootstrap brief/static/RED evidence, and preserved predecessors.
- Produces: one immutable report and either first exact NO_GO or `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.

- [ ] **Step 1: Run direct pre-report closure for all eight IDs**

Run frozen closure verifier directly with absolute workspace and eight literal IDs, without `-RequireFinalInventory`. It starts no child and writes nothing.

Require:

```text
EVIDENCE_HOST_RECOVERY_CLOSURE_PASS|commands=8|machine_files=32|absolute_paths=all|brief=canonical
```

It verifies command brief, static/RED evidence, all source/manifest/raw/result/digest identities, expected exits/terminals, exact 32 machine and pre-report human-file inventory, sentinel, both preserved NO_GO inventories and absent machine directories, four old absent paths, HEAD/linked/canonical cleanliness, and prohibited-action non-occurrence. Any mismatch is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`.

- [ ] **Step 2: Create the final report once with apply_patch**

Record design/plan commits/blobs/identities; worktree topology; both predecessor terminals and frozen sources; root-cause diagnostic; bootstrap command-brief bytes/hash/canonical proof; exact static and RED commands/results; GREEN source/parser/AST identities; every manifest/argv/environment/timeout; all outer host results; all 32 machine paths/counts/hashes/result fields/digests; closure result; final inventory; and explicit non-occurrence of every forbidden action.

Index raw files; do not replace bytes with decoded text. Do not infer a missing value. Once created, never edit the report.

- [ ] **Step 3: Run final-report closure once**

Run the frozen verifier with the eight literal IDs and `-RequireFinalInventory`. Require report ordinary/non-linked and internally consistent with machine evidence. It reports report bytes/hash and emits exactly:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

Contradiction or missing evidence is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`; never edit the report after observation.

- [ ] **Step 4: Prove repository and authority closure**

Require HEAD remains this plan commit; tracked/staged/untracked scope clean; ignored additions confined exactly to the fresh workspace; canonical worktree clean; both predecessor workspaces unchanged; no external evidence or formal identity created; and no commit after the plan.

Do not proceed to Docker readiness, GPU observation, entry child, product Tasks 2-8, or runtime. A later approved plan must consume the hostv4 PASS identities immutably.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserve both NO_GO workspaces and never rerun | Global Constraints; Task 1 Step 1; Task 4 Steps 1,4 |
| Remove dynamic bootstrap serialization | Task 1 Steps 3-5 |
| Human-authored canonical command brief | Task 1 Step 3 |
| Explicit Utf8JsonWriter reconstruction | Task 1 Steps 3-4 |
| Duplicate-switch versus equal-value semantics | Task 1 Step 3 |
| Literal absolute argv and receiver validation | Task 1 Steps 2-6; Task 2 Steps 1-4 |
| Intended test-first RED | Task 1 Steps 2,6 |
| Three-export side-effect-free GREEN module | Task 2 Steps 1-3 |
| Non-recursive host and raw concurrent capture | Task 2 Steps 3-4 |
| Closed schema-4 manifests and create-new outputs | Task 2 Steps 1-3; Task 3 Step 1 |
| Unique hostv4 behavior set | Task 3 Steps 2-9 |
| Independent 32-file closure and report | Task 2 Step 6; Task 3 Step 9; Task 4 Steps 1-3 |
| Exact PASS is not entry authorization | Global Constraints; Task 4 Steps 3-4 |
| No Docker/GPU/runtime/OwnerAuthorizationId | Global Constraints; Task 2 Step 6; Task 4 Steps 1,4 |

## Plan Completion Gate

Before execution, require:

1. this plan is one file in a direct-child commit of `b01372fcb147ac1d38ae2ad4ae45cf9f890e8152`;
2. author, committer, subject, and only changed path are exact;
3. all design requirements map to concrete steps in the coverage matrix;
4. file/function/parameter/schema/property/terminal/ID/machine names are consistent across all tasks;
5. no unresolved authoring marker, conflict marker, vague error case, or unspecified code behavior remains;
6. every PowerShell code block parses under PowerShell 7.6.4 and Windows PowerShell 5.1 where its API is parse-compatible;
7. command-brief content is exactly 1,461 bytes with SHA-256 `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6` when authored with LF and UTF-8 without BOM;
8. linked and canonical worktrees are clean, immediate predecessor has four frozen files, older predecessor has three frozen files, neither has machine output, and fresh workspace is absent; and
9. plan authoring executed no predecessor source, formal static verifier, RED, evidence host, Docker, GPU, entry, product, model, or runtime command.
