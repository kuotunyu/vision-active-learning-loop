# Wave 0 A11 Bootstrap Path-Resolution Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish an absolute-path bootstrap contract, obtain one intended recorder RED, and complete the full non-recursive synthetic evidence-host proof under fresh `hostv3-*` identities.

**Architecture:** Layer 0 supplies literal absolute paths and freezes their identities before execution. Every receiving script independently rejects non-fully-qualified input, canonicalizes and contains each path, verifies ordinary-file bytes and SHA-256, and passes only the validated value to module/file/process APIs. After one intended RED, a scope-isolated `.psm1` and minimal leaf host capture eight unique synthetic children into 32 create-new machine files; Docker, GPU, A11 entry, product code, and runtime remain unauthorized.

**Tech Stack:** PowerShell 7.6.4; Windows PowerShell 5.1 parser compatibility; .NET `System.IO.Path`, `StringComparer`, `FileStream`, `System.Diagnostics.Process`, `Task`, `Stopwatch`, `System.Text.Json`, and SHA-256; Git; Markdown; ignored append-only evidence files.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract`.
- Approved design commit is exactly `c685f0eff5be878d6a15060e0c61f90b770285ed`; this plan commit must be its one-file direct child.
- Design path is `docs/superpowers/specs/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery-design.md`, Git blob `8261b57778c0724ff3785db37f2cab495d4127c4`, 20,776 bytes.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Predecessor plan commit `890466f71c6730e07774c4568c7b50f70db8ebe2` and its ignored workspace are immutable.
- Predecessor terminal remains `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`; never rerun its RED process.
- Predecessor workspace contains exactly three frozen files and no `machine/` directory.
- Earlier `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, `CUDA_OBSERVATION_UNPROVABLE / NO_GO`, artifacts, images, leases, inventories, digests, reports, owner identities, and attempts remain immutable.
- The only new workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/`, and it must be absent at entry.
- Create every human-authored ignored file with `apply_patch`; never generate source or manifest JSON with a script or shell redirection.
- The evidence host may create only the exact 32 predetermined `machine/hostv3-*` files.
- Once a process consumes a source, fixture, test, manifest, command ID, or destination, it is immutable.
- Any defect before the new RED start requires a new append-only identity. Any defect after the new RED starts closes this plan; do not fix, replace, or retry it.
- Every path-bearing process argument is a literal absolute `D:\...` or frozen absolute PowerShell executable path; no receiving script supports a relative fallback.
- Do not inspect or execute Docker CLI, Docker Desktop processes, Docker/WSL pipes, builders, images, containers, caches, volumes, GPU, `nvidia-smi`, CUDA, CPU baseline, dependencies, model, A11 launcher, entry child, formal runtime, Wave 1, or Tasks 2-8.
- Do not create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`.
- Do not modify product code, the seven-file A11 implementation allowlist, external evidence, another repository, a remote, or Git history.
- Do not push, merge, tag, release, amend, rebase, reset, stash, or delete preserved evidence.
- The only success terminal is `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.
- Execution creates ignored evidence only; there is no tracked implementation commit after this plan commit.

## Normative Inputs

- Approved design: Git blob `8261b57778c0724ff3785db37f2cab495d4127c4` at the design path above.
- Predecessor design and plan: commits `4843cfe1579d9dc31f4994c6efa09f9de19fbdce` and `890466f71c6730e07774c4568c7b50f70db8ebe2`.
- Predecessor workspace: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/`.
- Predecessor files:
  - `task-1-entry-gate.ps1`, 3,541 bytes, SHA-256 `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b`;
  - `task-1-evidence-module-red.psm1`, 103 bytes, SHA-256 `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc`;
  - `task-1-evidence-tests.ps1`, 4,420 bytes, SHA-256 `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65`.
- Frozen PowerShell executable: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`.
- Frozen PowerShell SHA-256: `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`.
- Repository root: `<repo>\.worktrees\wave0-model-contract`.
- Canonical worktree: `<repo>`.

## File and Interface Map

The implementation changes no tracked file. Create these ignored human-authored files below the fresh workspace:

| Path | Responsibility |
|---|---|
| `task-1-entry-gate-v3.ps1` | Exact Git, predecessor, absence, executable, and authority entry proof. |
| `task-1-bootstrap-path-static-v3.ps1` | Prove literal absolute RED argv and validated data flow before RED execution. |
| `task-1-bootstrap-red-brief-v3.md` | Freeze exact RED executable, argv, working directory, environment, sources, hashes, and expected terminal. |
| `task-1-evidence-module-red-v3.psm1` | Fresh RED subject with no recorder exports. |
| `task-1-evidence-tests-v3.ps1` | Absolute-path RED and complete GREEN structural/module tests. |
| `task-1-evidence-module-green-v3.psm1` | Absolute manifest validation, raw process capture, result publication, and machine verification. |
| `task-1-evidence-host-v3.ps1` | Minimal non-recursive leaf host with absolute module/manifest inputs. |
| `task-1-static-verifier-v3.ps1` | Parser, AST, path-flow, automatic-variable, import, write-site, and forbidden-command gates. |
| `task-1-synthetic-fixture-v3.ps1` | Deterministic raw, high-volume, argv, nonzero, and timeout child behavior. |
| `task-1-invalid-executable-v3.exe` | ASCII non-executable used for one deterministic start failure. |
| `task-1-invalid-manifests-v3.ps1` | Read-only malformed/colliding/path-contract manifest tests. |
| `task-1-preexisting-v3.stdout.bin` | Apply-patch sentinel whose bytes must remain unchanged. |
| `task-1-closure-verifier-v3.ps1` | Independent source/manifest/machine/result/inventory closure. |
| `task-1-report.md` | Final evidence index and first exact terminal. |

Create exactly eight canonical manifests:

| Manifest | Command ID | Expected child result |
|---|---|---|
| `task-1-manifest-hostv3-001-unit-green.json` | `hostv3-001-unit-green` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv3-002-raw.json` | `hostv3-002-raw` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv3-003-high-volume.json` | `hostv3-003-high-volume` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv3-004-argv.json` | `hostv3-004-argv` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv3-005-nonzero.json` | `hostv3-005-nonzero` | exit 23, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv3-006-timeout.json` | `hostv3-006-timeout` | `COMMAND_TIMEOUT` |
| `task-1-manifest-hostv3-007-start-failure.json` | `hostv3-007-start-failure` | exit -1, `COMMAND_START_FAILURE` |
| `task-1-manifest-hostv3-008-closure.json` | `hostv3-008-closure` | exit 0, `COMMAND_COMPLETE` |

Each command produces these four exact suffixes under `machine/`: `.stdout.bin`, `.stderr.bin`, `.result.json`, `.result.sha256`. Eight commands produce exactly 32 machine files.

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

### Task 1: Prove entry, freeze the absolute-path contract, and obtain the intended RED

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-entry-gate-v3.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-bootstrap-path-static-v3.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-bootstrap-red-brief-v3.md`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-evidence-module-red-v3.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-evidence-tests-v3.ps1`

**Interfaces:**
- Consumes: exact plan commit, design blob, frozen predecessor sources/NO_GO, signed PowerShell identity, clean linked/canonical worktrees.
- Produces: `BOOTSTRAP_PATH_STATIC_PASS` and one immutable RED with exit 41 and missing-export output.

- [ ] **Step 1: Run exact read-only entry before creating the workspace**

Execute from the linked worktree. Normalize Git's forward-slash output with `[IO.Path]::GetFullPath` before comparing the worktree root; do not compare raw slash spelling.

```powershell
$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery'
$OldWorkspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery.md'
$ExpectedBranch = 'codex/wave0-model-contract'
$ExpectedDesign = 'c685f0eff5be878d6a15060e0c61f90b770285ed'
$ExpectedPlan = git rev-parse HEAD

$ObservedRoot = [IO.Path]::GetFullPath((git rev-parse --show-toplevel))
if (-not [StringComparer]::OrdinalIgnoreCase.Equals($ObservedRoot, $RepositoryRoot)) { throw 'worktree root mismatch' }
$GitDir = [IO.Path]::GetFullPath((git rev-parse --git-dir), $RepositoryRoot)
$GitCommon = [IO.Path]::GetFullPath((git rev-parse --git-common-dir), $RepositoryRoot)
if ([StringComparer]::OrdinalIgnoreCase.Equals($GitDir, $GitCommon)) { throw 'not a linked worktree' }
if (-not [string]::IsNullOrEmpty([string](git rev-parse --show-superproject-working-tree))) { throw 'submodule detected' }
if ((git branch --show-current) -cne $ExpectedBranch) { throw 'branch mismatch' }
if ((git rev-parse 'HEAD^') -cne $ExpectedDesign) { throw 'plan parent mismatch' }
$PlanPaths = @(git diff-tree --no-commit-id --name-only -r HEAD)
if ($PlanPaths.Count -ne 1 -or $PlanPaths[0] -cne $PlanPath) { throw 'plan path mismatch' }
if ((git show -s --format='%an <%ae>' HEAD) -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'author mismatch' }
if ((git show -s --format='%cn <%ce>' HEAD) -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'committer mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree dirty' }
if (@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'canonical worktree dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging nonempty' }
if (Test-Path -LiteralPath $Workspace) { throw 'fresh workspace already exists' }
if ((git rev-parse "${ExpectedDesign}:$DesignPath") -cne '8261b57778c0724ff3785db37f2cab495d4127c4') { throw 'design blob mismatch' }

$ExpectedOld = [ordered]@{
    'task-1-entry-gate.ps1' = [ordered]@{ bytes = 3541; sha = '3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b' }
    'task-1-evidence-module-red.psm1' = [ordered]@{ bytes = 103; sha = 'a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc' }
    'task-1-evidence-tests.ps1' = [ordered]@{ bytes = 4420; sha = '8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65' }
}
$OldFiles = @(Get-ChildItem -LiteralPath $OldWorkspace -File -Recurse -Force)
if ($OldFiles.Count -ne 3) { throw 'predecessor file count mismatch' }
foreach ($Entry in $ExpectedOld.GetEnumerator()) {
    $Path = Join-Path $OldWorkspace $Entry.Key
    if ((Get-Item -LiteralPath $Path).Length -ne $Entry.Value.bytes) { throw "predecessor bytes mismatch: $($Entry.Key)" }
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash.ToLowerInvariant() -cne $Entry.Value.sha) { throw "predecessor digest mismatch: $($Entry.Key)" }
}
if (Test-Path -LiteralPath (Join-Path $OldWorkspace 'machine')) { throw 'predecessor machine directory appeared' }

$Pwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Pwsh).Hash.ToLowerInvariant() -cne 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f') { throw 'PowerShell digest mismatch' }
if ((Get-AuthenticodeSignature -LiteralPath $Pwsh).Status -cne 'Valid') { throw 'PowerShell signature invalid' }

"BOOTSTRAP_PATH_ENTRY_PASS|plan=$ExpectedPlan|workspace=absent|predecessor_files=3|linked=clean|canonical=clean"
```

Require the exact PASS prefix. Any failure stops with no new workspace.

- [ ] **Step 2: Create the fresh RED subject and complete test first**

Use `apply_patch` to create `task-1-entry-gate-v3.ps1` with the Step 1 checks and the literal plan commit. Create `task-1-evidence-module-red-v3.psm1` as:

```powershell
Set-StrictMode -Version Latest

# Intentional hostv3 RED subject: recorder exports do not exist.
```

With LF line endings and UTF-8 without BOM, this exact RED module is 97 bytes and has SHA-256 `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136`. Require both values before creating the RED brief.

The entry source is an audit copy of the already completed absence gate. Do not execute it after the workspace exists.

Create `task-1-evidence-tests-v3.ps1` before any GREEN source. Its absolute-file helper is:

```powershell
function Assert-A11AbsoluteFile {
    [CmdletBinding()]
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
    $ObservedSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $Canonical).Hash.ToLowerInvariant()
    if ($ObservedSha -cne $ExpectedSha256) { throw 'file digest mismatch' }
    return $Canonical
}
```

The RED branch uses only the validated return value:

```powershell
$ValidatedModulePath = Assert-A11AbsoluteFile `
    -Candidate $ModulePath `
    -ExpectedPath $ExpectedModulePath `
    -AllowedRoot $WorkspacePath `
    -ExpectedByteCount $ExpectedModuleByteCount `
    -ExpectedSha256 $ExpectedModuleSha256

$LibraryOnly = 'caller-sentinel'
$BeforePid = $PID
$Module = Import-Module -Name $ValidatedModulePath -Scope Local -Force -PassThru
if ($LibraryOnly -cne 'caller-sentinel') { throw 'caller LibraryOnly changed' }
if ($BeforePid -ne $PID) { throw 'caller PID changed' }
$ExpectedExports = @('Invoke-A11RecordedChild','Read-A11EvidenceManifest','Test-A11MachineEvidence') | Sort-Object
$ActualExports = @($Module.ExportedFunctions.Keys | Sort-Object)

if ($Mode -ceq 'Red') {
    if ($ActualExports.Count -ne 0) { throw 'RED export set is not empty' }
    if (($ActualExports | ConvertTo-Json -Compress) -ceq ($ExpectedExports | ConvertTo-Json -Compress)) { throw 'RED subject unexpectedly passed' }
    [Console]::Out.WriteLine('EXPECTED_RED|required export set missing')
    exit 41
}
```

The GREEN branch reuses the validated absolute module value, requires exact exports, parses host/module with absolute paths, rejects dot-source, `Invoke-Expression`, `Start-Process`, top-level module `return`/`exit`, and assignments to automatic/constant/read-only variables, then runs the read-only invalid-manifest test and emits only `EVIDENCE_TEST_SUITE_PASS` plus one newline.

The production change each test catches is explicit: allowing a relative module argument, importing the unvalidated candidate, accepting an escaping/linked/wrong-identity file, leaking caller variables, or omitting one of the three exports makes the test fail.

- [ ] **Step 3: Create and run the static absolute-path gate once**

Use `apply_patch` to create `task-1-bootstrap-path-static-v3.ps1`. It accepts literal absolute test/module/workspace paths plus expected test/module byte counts and hashes. It must:

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
    [Parameter(Mandatory)] [string] $PlannedArgvJson
)
```

`PlannedArgvJson` is compact JSON over the exact string array printed in Step 4. The static verifier parses it with `JsonDocument`, rejects duplicate or non-string elements, and requires byte-for-byte argument order after compact reserialization. It writes nothing and imports no module. It must:

- call the same closed absolute/containment/link/identity checks without importing the module;
- parse the test with `Parser.ParseFile` and require zero parser errors;
- locate exactly one `Import-Module` AST used by `Get-A11ExportNames`/RED flow;
- require its `-Name` argument to be the variable `$ValidatedModulePath`, never `$ModulePath`;
- require the source contains the `IsPathFullyQualified`, `GetFullPath`, `GetRelativePath`, `OrdinalIgnoreCase`, reparse, byte-count, and SHA-256 gates;
- freeze an exact argv vector whose `-File`, `-ModulePath`, `-ExpectedModulePath`, and `-WorkspacePath` values are fully qualified and equal their expected canonical literals; and
- require the old workspace/test/module paths absent from the new argv.

Run it once through the frozen PowerShell executable. Require:

```text
BOOTSTRAP_PATH_STATIC_PASS|absolute_args=4|validated_imports=1|relative_args=0|predecessor_args=0
```

Any failure publishes `BOOTSTRAP_PATH_STATIC_REJECTED / NO_GO` and stops before RED.

- [ ] **Step 4: Freeze the exact RED brief with apply_patch**

Create `task-1-bootstrap-red-brief-v3.md` after the static PASS. Record literal PowerShell executable identity, test/module/workspace paths, source bytes/hashes, working directory, environment, exact argv order, expected exit/stdout/stderr, zero machine destinations, and the static gate tool result. The exact RED argv is:

```text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-evidence-tests-v3.ps1
-Mode
Red
-ModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-evidence-module-red-v3.psm1
-ExpectedModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-evidence-module-red-v3.psm1
-ExpectedModuleByteCount
97
-ExpectedModuleSha256
c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136
-WorkspacePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery
```

- [ ] **Step 5: Execute the new RED exactly once**

Run the frozen executable and literal argv from the brief. Require exit 41, stdout exactly `EXPECTED_RED|required export set missing` plus the platform newline, empty stderr, zero machine file, and unchanged sources.

Any import/path/parser/output/exit difference is `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`. Preserve it and stop; do not change an argument, source, working directory, or environment and do not rerun.

---

### Task 2: Implement the absolute GREEN module and non-recursive host

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-evidence-module-green-v3.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-evidence-host-v3.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-static-verifier-v3.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-synthetic-fixture-v3.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-invalid-executable-v3.exe`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-invalid-manifests-v3.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-preexisting-v3.stdout.bin`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-closure-verifier-v3.ps1`

**Interfaces:**
- Consumes: intended RED from Task 1; exact immutable absolute-path test contract.
- Produces: three-export GREEN module, three-parameter leaf host, fixtures/verifiers, parser PASS, and `EVIDENCE_HOST_STATIC_PASS` before any host child.

- [ ] **Step 1: Implement private absolute-path and canonical-manifest helpers**

Create `task-1-evidence-module-green-v3.psm1` with no script-level parameters. At module scope permit only `Set-StrictMode`, function definitions, and the final exact `Export-ModuleMember`.

Define private `Assert-A11AbsolutePath` with parameters `Candidate`, `ExpectedPath`, `AllowedRoot`, `ExpectedKind`, optional byte/hash identity, and a private test-only attribute provider. It implements the Task 1 helper plus rejection of wildcard, provider-qualified, URI, UNC, device, ADS, and trailing ambiguity. It returns one canonical backslash-form absolute path. Production callers use the real attribute provider; the injected provider exists only for linked-path unit behavior and is not exported.

Define private `ConvertFrom-A11CanonicalManifestBytes`. Decode with strict `UTF8Encoding(false, true)`, reject BOM, require compact JSON plus one LF, parse with `JsonDocument`, reject duplicate properties recursively, require exact property order, reconstruct ordered dictionaries, serialize with `ConvertTo-Json -Compress -Depth 12`, append LF, and require byte equality.

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

Require schema 3, command ID `^hostv3-[0-9]{3}-[a-z0-9-]+$`, environment order `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, timeout order `mode`, `milliseconds`, stdin `closed`, child count 1, lowercase 64-hex hashes, consistent source vectors, absolute path contract for every path, and four absent command-ID-derived machine destinations.

- [ ] **Step 2: Implement public manifest read**

Define:

```powershell
function Read-A11EvidenceManifest {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [string] $ManifestPath,
        [Parameter(Mandatory)] [string] $ExpectedWorkspace,
        [Parameter(Mandatory)] [string] $ExpectedHostPath,
        [Parameter(Mandatory)] [string] $ExpectedModulePath
    )
}
```

Validate all four inputs as fully qualified before file access. Read exact bytes, invoke canonical parsing, verify host/module/executable/source paths and identities, require working directory exactly the repository root, require outputs below the fresh workspace `machine` directory, and return an ordered manifest enriched in memory with `manifest_path`, `manifest_byte_count`, and `manifest_sha256`. Derived fields are never written back into the manifest.

- [ ] **Step 3: Implement raw capture with create-new publication**

Define:

```powershell
function Invoke-A11RecordedChild {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [System.Collections.IDictionary] $Manifest
    )
}
```

Use only `System.Diagnostics.ProcessStartInfo`:

```powershell
$StartInfo = [System.Diagnostics.ProcessStartInfo]::new()
$StartInfo.FileName = [string] $Manifest.executable_path
$StartInfo.WorkingDirectory = [string] $Manifest.working_directory
$StartInfo.UseShellExecute = $false
$StartInfo.RedirectStandardInput = $true
$StartInfo.RedirectStandardOutput = $true
$StartInfo.RedirectStandardError = $true
$StartInfo.CreateNoWindow = $true
$StartInfo.Environment.Clear()
foreach ($Entry in $Manifest.environment_allowlist.GetEnumerator()) {
    $StartInfo.Environment[[string] $Entry.Key] = [string] $Entry.Value
}
foreach ($Argument in @($Manifest.argv)) {
    [void] $StartInfo.ArgumentList.Add([string] $Argument)
}
```

This is the required `ProcessStartInfo.ArgumentList` boundary. Never populate the legacy `Arguments` string. Open stdout/stderr with `FileMode.CreateNew`, `FileAccess.Write`, `FileShare.None`, 65,536-byte buffers, and async/write-through options. Start one process, store its ID only in `$ChildProcessId`, close stdin, begin both `BaseStream.CopyToAsync` calls, and wait for the same process.

For timeout mode `none`, wait once. For `bounded`, race `WaitForExitAsync` and one `Task.Delay`; if delay wins, call `Kill($true)` once and wait for the same PID. Always await both copy tasks, flush to disk, close raw streams, and compute raw bytes/hashes.

Start exception produces zero-byte streams, PID -1, exit -1, exception type/message, and `COMMAND_START_FAILURE`. Normal completion produces `COMMAND_COMPLETE`; bounded kill produces `COMMAND_TIMEOUT`.

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

- [ ] **Step 4: Implement public independent machine verification and exports**

Define:

```powershell
function Test-A11MachineEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [System.Collections.IDictionary] $Manifest
    )
}
```

Require exactly four ordinary non-linked files, recompute raw counts/hashes,
parse canonical result order/bytes, verify manifest/executable/argv/environment/
path/result fields, enforce terminal consistency, and verify digest-file bytes.
Return an ordered verification object with `command_id`, `terminal`, `exit_code`,
`timed_out`, raw counts/hashes, and result digest. Write nothing.

Export exactly:

```powershell
Export-ModuleMember -Function @(
    'Read-A11EvidenceManifest',
    'Invoke-A11RecordedChild',
    'Test-A11MachineEvidence'
)
```

- [ ] **Step 5: Implement the minimal absolute leaf host**

Create `task-1-evidence-host-v3.ps1` with the exact three-parameter interface. Before importing, require all inputs fully qualified; canonicalize them; require manifest/module below the expected workspace; use `JsonDocument` only to read frozen host/module identities; verify current host/module bytes and hashes; then import only `$ValidatedModulePath` with `Import-Module -Scope Local -Force -PassThru`.

Require the exact export set. Call `Read-A11EvidenceManifest` once, `Invoke-A11RecordedChild` once, and `Test-A11MachineEvidence` once. Do not dot-source, self-capture, recurse, replace a manifest, try another path, or reconstruct output.

Success emits and exits 0:

```powershell
[Console]::Out.WriteLine("HOST_CAPTURE_COMPLETE|command_id=$($Verification.command_id)|terminal=$($Verification.terminal)")
```

Before-machine static rejection emits `EVIDENCE_HOST_STATIC_REJECTED / NO_GO`; a missing/partial four-file set emits `EVIDENCE_HOST_UNPROVABLE / NO_GO`; a complete but invalid set emits `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`. Each exits nonzero.

- [ ] **Step 6: Create deterministic fixtures and invalid-manifest tests**

Create `task-1-synthetic-fixture-v3.ps1`:

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
    'Argv' {
        [Console]::Out.Write((ConvertTo-Json -InputObject @($Payload) -Compress))
        exit 0
    }
    'Nonzero' {
        [Console]::Out.Write('controlled-out')
        [Console]::Error.Write('controlled-error')
        exit 23
    }
    'Timeout' {
        [Console]::Out.Write('timeout-started')
        [Console]::Out.Flush()
        Start-Sleep -Seconds 5
        exit 0
    }
}
```

Create `task-1-invalid-executable-v3.exe` as exact ASCII `A11 V3 INVALID EXECUTABLE` plus LF. Create sentinel `task-1-preexisting-v3.stdout.bin` as exact ASCII `A11-V3-PREEXISTING-SENTINEL` plus LF.

Create `task-1-invalid-manifests-v3.ps1`. It imports the GREEN module by validated absolute path and uses manifest 002, whose outputs are absent while command 001 runs, as a valid baseline. Through module-scope invocation of private pure validators, construct byte-array cases without writing JSON. Require rejection of relative path, UNC, provider path, URI, ADS, escaping path, duplicate key, extra/missing/reordered key, output collision, preexisting sentinel, injected `ReparsePoint`, noncanonical hash, and source-vector mismatch. Require sentinel hash unchanged. Return only `INVALID_MANIFEST_TESTS_PASS`; assertion failure throws.

- [ ] **Step 7: Create closure/static verifiers and run parser/static gates once**

Create `task-1-closure-verifier-v3.ps1` before any host child. It reads only absolute validated paths, writes nothing, recomputes explicit command-ID manifest/source/raw/result/digest identities, validates expected terminal/exit pairs, and rejects missing/extra machine or human files. With `-RequireFinalInventory`, require `task-1-report.md`; without it, require the exact pre-report inventory.

Create `task-1-static-verifier-v3.ps1`. Parse tests, GREEN module, host, invalid-manifest tests, fixture, and closure verifier. Under both PowerShell 7.6.4 and Windows PowerShell 5.1 require zero parser errors. AST gates require:

- no dot-source, `Invoke-Expression`, `Start-Process`, shell-string invocation, redirection syntax, or write cmdlet;
- no module script parameter or top-level side effect;
- no assignment to `PID`, `HOME`, `HOST`, `ERROR`, `ARGS`, `INPUT`, `MATCHES`, `MYINVOCATION`, `PSBOUNDPARAMETERS`, `PSSCRIPTROOT`, `PSCOMMANDPATH`, `LASTEXITCODE`, or any live Constant/ReadOnly variable;
- exact host parameters and three module exports;
- every module/file/parser/process path data flow comes from an absolute validator;
- raw/result writes use create-new and remain below fresh `machine/`;
- no predecessor source/path scheduled for execution; and
- no Docker/GPU/A11/product/Git mutation/network/runtime command.

Run the static verifier once. Require:

```text
EVIDENCE_HOST_STATIC_PASS|exports=3|absolute_flows=all|dot_source=0|forbidden_assignments=0|forbidden_commands=0
```

No machine path may exist. Any failure stops with `EVIDENCE_HOST_STATIC_REJECTED / NO_GO`. Freeze all executable GREEN sources after PASS.

---

### Task 3: Author and execute eight unique hostv3 captures

**Files:**
- Create: eight `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-manifest-hostv3-*.json` manifests.
- Create by host only: 32 `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/machine/hostv3-*` files.
- Modify existing source: none.

**Interfaces:**
- Consumes: frozen GREEN/static PASS and exact absolute source identities.
- Produces: seven behavior captures plus one closure capture; every ID runs at most once.

- [ ] **Step 1: Freeze identities and create all manifests with apply_patch**

Measure literal canonical absolute path, byte count, and lowercase SHA-256 for host, module, PowerShell, tests, fixture, invalid executable, invalid-manifest test, closure verifier, sentinel, and every consumed source. Use those observed literals in manually authored compact schema-3 JSON; do not synthesize JSON with code.

Every path field is fully qualified. Every manifest uses repository root working directory, environment order `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, stdin `closed`, one child, and four exact fresh output paths. Commands 001-006 and 008 use frozen PowerShell; 007 uses the invalid executable with empty argv.

Exact PowerShell argv tails are:

| ID | argv after `-NoProfile -NonInteractive -File` |
|---|---|
| 001 | absolute test path; `-Mode Green`; absolute GREEN module path and same expected path; literal module bytes/hash; absolute workspace, host, fixture, and invalid-manifest-test paths |
| 002 | absolute fixture path; `-Mode Raw` |
| 003 | absolute fixture path; `-Mode HighVolume` |
| 004 | absolute fixture path; `-Mode Argv -Payload`; `alpha beta`; empty string; `quote"value`; `中 文` |
| 005 | absolute fixture path; `-Mode Nonzero` |
| 006 | absolute fixture path; `-Mode Timeout` |
| 008 | absolute closure path; absolute workspace; literal `-ExpectedCommandIds` values 001 through 007 |

Timeout is `none`/0 for 001-005, 007, 008 and `bounded`/500 for 006. Require all 32 destinations absent, every manifest canonical/ordinary/non-linked, all source identities exact, and no relative/predecessor path in any manifest.

- [ ] **Step 2: Execute hostv3-001 once and require complete GREEN**

Invoke frozen PowerShell with literal absolute host, manifest, module, and workspace arguments:

```text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-evidence-host-v3.ps1
-A11HostManifestPath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-manifest-hostv3-001-unit-green.json
-A11HostModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-evidence-module-green-v3.psm1
-A11HostExpectedWorkspace
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery
```

Require host exit 0, `HOST_CAPTURE_COMPLETE`, exactly four 001 machine files, child exit 0, terminal `COMMAND_COMPLETE`, stdout exactly `EVIDENCE_TEST_SUITE_PASS` plus newline, empty stderr, and result/digest recomputation. Stop on any difference; never start 001 again.

- [ ] **Step 3: Execute hostv3-002 once and verify exact raw bytes**

Use the same frozen absolute host/module/workspace arguments and the 002 manifest. Require stdout bytes `41 00 E4 B8 AD 0A 5A`, stderr bytes `45 52 52 00 FF`, exit 0, `COMMAND_COMPLETE`, and complete result/digest. Stop on mismatch.

- [ ] **Step 4: Execute hostv3-003 once and verify concurrent high volume**

Require exactly 1,048,576 stdout bytes all `0x4F`, 1,048,576 stderr bytes all `0x45`, exit 0, no timeout/deadlock, and complete result/digest. Stop on mismatch.

- [ ] **Step 5: Execute hostv3-004 once and verify argv boundaries**

Require compact JSON stdout for exactly `alpha beta`, empty string, `quote"value`, `中 文`, without terminal newline; empty stderr; result argv exactly equal manifest argv; exit 0; and complete result/digest. Stop on mismatch.

- [ ] **Step 6: Execute hostv3-005 once and preserve nonzero result**

Require stdout `controlled-out`, stderr `controlled-error`, exit 23, `timed_out=false`, terminal `COMMAND_COMPLETE`, and host exit 0 because capture completed. Stop on mismatch.

- [ ] **Step 7: Execute hostv3-006 once and preserve bounded timeout**

Require stdout begins with `timeout-started`, `timed_out=true`, terminal `COMMAND_TIMEOUT`, one killed PID, completion after start, complete stderr/result/digest, and host exit 0 because the planned timeout was captured. Stop on mismatch; never restart the timeout fixture.

- [ ] **Step 8: Execute hostv3-007 once and preserve start failure**

Require zero-byte stdout/stderr, PID -1, exit -1, `timed_out=false`, nonempty Win32 exception type/message, `COMMAND_START_FAILURE`, complete result/digest, and host exit 0 because the planned start failure was captured. Stop on mismatch; never substitute an executable.

- [ ] **Step 9: Execute hostv3-008 once and capture closure of 001-007**

Require child exit 0, `COMMAND_COMPLETE`, stdout exact prefix `EVIDENCE_MACHINE_CLOSURE_PASS|commands=7|machine_files=28`, empty stderr, and its own complete four-file set. The closure child rejects any missing, extra, linked, noncanonical, colliding, wrong-path, wrong-terminal, or digest-mismatched evidence in 001-007.

---

### Task 4: Close the 32-file inventory and publish the terminal

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/task-1-report.md`
- Read: all new human files, eight manifests, 32 machine files, predecessor identities, and Git state.
- Modify tracked files: none.

**Interfaces:**
- Consumes: exact eight hostv3 results and immutable sources.
- Produces: one report and either first exact NO_GO or `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.

- [ ] **Step 1: Run direct pre-report closure for all eight IDs**

Run the frozen closure verifier directly with absolute workspace path and eight literal IDs, without `-RequireFinalInventory`. It starts no child and writes nothing.

Require:

```text
EVIDENCE_HOST_RECOVERY_CLOSURE_PASS|commands=8|machine_files=32|absolute_paths=all
```

It must verify all manifest/source/raw/result/digest identities, expected exits/terminals, 32-file inventory, host/module/test identity, sentinel, predecessor three-file inventory, predecessor no-machine state, old `preformal-003` absence, HEAD/linked/canonical cleanliness, and prohibited-action non-occurrence. Any mismatch stops as `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`.

- [ ] **Step 2: Create the final report once with apply_patch**

Record design/plan commits/blobs/identities, worktree topology, predecessor NO_GO and three sources, absolute-path static gate, exact RED command/result, all GREEN source/parser/AST identities, each manifest/argv/environment/timeout, every outer host tool result, all 32 machine paths/counts/hashes/results/digests, closure result, final inventory, and explicit non-occurrence of every forbidden action.

Index raw files; do not replace binary evidence with decoded text. Do not infer a missing value. Once created, do not edit the report.

- [ ] **Step 3: Run final-report closure once**

Run the already frozen verifier directly with the eight literal IDs and `-RequireFinalInventory`. It writes nothing, starts no child, requires the report ordinary/non-linked, verifies its consistency with machine evidence, and reports its bytes/hash.

Require exact terminal:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

Contradiction or missing evidence is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`; never edit the report after observation.

- [ ] **Step 4: Prove repository and authority closure**

Require HEAD remains this plan commit; tracked/staged/untracked scope clean; ignored changes confined exactly to the fresh workspace; canonical worktree clean; predecessor workspaces unchanged; no external evidence or formal identity created; and no commit after the plan.

Do not proceed to Docker readiness, GPU observation, entry child, product Tasks 2-8, or runtime. A later approved plan must consume the hostv3 PASS identities immutably.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserve predecessor NO_GO/sources and never rerun | Global Constraints; Task 1 Step 1; Task 4 Steps 1,4 |
| Literal absolute Layer 0 argv | Task 1 Steps 3-5; Task 3 Steps 1-2 |
| Receiver absolute/canonical/containment/link/identity validation | Task 1 Step 2; Task 2 Steps 1-2,5-7 |
| Import only validated absolute module | Task 1 Steps 2-3; Task 2 Step 5 |
| Intended test-first RED | Task 1 Steps 2-5 |
| Non-recursive host and no self-capture | Task 2 Steps 3-5,7 |
| Closed schema-3 manifests and exact exports | File Map; Task 2 Steps 1-5; Task 3 Step 1 |
| Concurrent raw streams and create-new result/digest | Task 2 Steps 3-4; Task 3 Steps 2-9 |
| Unique hostv3 IDs and no retry | File Map; Task 3 Steps 1-9 |
| Raw, volume, argv, nonzero, timeout, start failure | Task 2 Step 6; Task 3 Steps 3-8 |
| Independent 32-file closure and report | Task 2 Step 7; Task 3 Step 9; Task 4 Steps 1-3 |
| Exact PASS is not entry authorization | Global Constraints; Task 4 Steps 3-4 |
| No Docker/GPU/runtime/OwnerAuthorizationId | Global Constraints; Task 2 Step 7; Task 4 Steps 1,4 |

## Plan Completion Gate

Before execution, require:

1. this plan is one file in a direct-child commit of `c685f0eff5be878d6a15060e0c61f90b770285ed`;
2. author, committer, subject, and only changed path are exact;
3. all design requirements map to concrete steps in the coverage matrix;
4. file/function/parameter/schema/property/terminal/ID/machine names are consistent across all tasks;
5. no unresolved authoring marker, conflict marker, vague error case, or unspecified code behavior remains;
6. every PowerShell code block parses under PowerShell 7.6.4 and Windows PowerShell 5.1;
7. linked and canonical worktrees are clean, predecessor workspace has exactly three frozen files, and fresh workspace is absent; and
8. plan authoring executed no PowerShell test, path-static verifier, evidence host, Docker, GPU, entry, model, or runtime command.
