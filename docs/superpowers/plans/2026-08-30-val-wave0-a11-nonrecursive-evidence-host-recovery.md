# Wave 0 A11 Non-Recursive Evidence Host Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a scope-isolated, non-recursive PowerShell evidence host with complete synthetic raw-stream and result evidence, while preserving every earlier A11 failure and leaving the complete entry gate unauthorized.

**Architecture:** A frozen signed PowerShell executable is the explicit coordination root. It starts a minimal leaf host that imports a side-effect-free `.psm1` in module scope and records exactly one manifest-authorized synthetic child; the host never records itself, and missing child evidence fails closed. TDD first proves the RED module lacks the required exports, then static gates and eight unique synthetic captures prove the GREEN module, host, raw bytes, argv, failures, timeout, and closure inventory.

**Tech Stack:** PowerShell 7.6.4; Windows PowerShell 5.1 parser compatibility; .NET `System.Diagnostics.Process`, `FileStream`, `Task`, `Stopwatch`, `System.Text.Json`, and SHA-256; Git; Markdown; ignored append-only evidence files.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract`.
- Design commit is exactly `4843cfe1579d9dc31f4994c6efa09f9de19fbdce`; this plan commit must be its one-file direct child.
- Design path is `docs/superpowers/specs/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery-design.md`, Git blob `62df9b839bdfc61b7cd6a6d4416a0bff52011972`, 21,093 bytes.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- The consumed restart-aware plan commit `23e841a42c5cdb8f0fdd3356c3b8bfc1f52aa02f` and its workspace are immutable.
- The consumed report remains 6,536 bytes with SHA-256 `446a785ed2397ab3340ef2084536382a8cf0c065138879673ac6bd91e9b33c7c` and terminal `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`.
- The four absent `preformal-003-recorder-red-verify` machine files remain absent; do not create, infer, reconstruct, replace, or retry them.
- The earlier `CUDA_OBSERVATION_UNPROVABLE / NO_GO` and all earlier artifacts, images, leases, inventories, digests, reports, authorizations, and attempts remain immutable.
- The only new workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/`, and it must be absent at entry.
- Create every human-authored ignored file with `apply_patch`; never use shell redirection, `Set-Content`, `Out-File`, transcript capture, or a generated source file.
- The evidence host may create only the exact predetermined `machine/*.stdout.bin`, `machine/*.stderr.bin`, `machine/*.result.json`, and `machine/*.result.sha256` paths in this plan.
- Once an executed process consumes a source, test, fixture, manifest, command ID, or destination, that object is immutable.
- An authoring defect found before the first child start requires a new append-only source or manifest path. Any defect after the first host child starts closes this plan; do not repair or retry it.
- Do not execute or inspect Docker CLI, Docker Desktop processes, Docker/WSL pipes, images, containers, builders, cache, volumes, GPU, `nvidia-smi`, CUDA, CPU baseline, dependencies, model, A11 launcher, entry child, validation runtime, Wave 1, or Tasks 2-8.
- Do not create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`.
- Do not modify product code, the seven-file A11 implementation allowlist, external evidence, another repository, a remote, or Git history.
- Do not push, merge, tag, release, amend, rebase, reset, stash, or delete preserved evidence.
- The only success terminal is `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`; it does not authorize Task 1 entry execution.

## Normative Inputs

- Approved design: Git blob `62df9b839bdfc61b7cd6a6d4416a0bff52011972` at the design path above.
- Failed recovery report: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-report.md`.
- Failed command manifest: `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-command-manifest-preformal-003.json`; read only its frozen identity fields, never its consumed sources.
- Frozen PowerShell path: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`.
- Frozen PowerShell SHA-256: `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`.
- Repository root: `<repo>\.worktrees\wave0-model-contract`.
- Canonical worktree: `<repo>`.

## File and Interface Map

The implementation changes no tracked file. It creates only these ignored human-authored files below the fresh workspace:

| Path | Responsibility |
|---|---|
| `task-1-entry-gate.ps1` | Prove exact Git, lineage, absence, frozen-input, and forbidden-process entry conditions without external runtime inspection. |
| `task-1-evidence-module-red.psm1` | Immutable RED subject with no recorder exports. |
| `task-1-evidence-tests.ps1` | RED export test and complete GREEN structural/module test suite. |
| `task-1-evidence-module-green.psm1` | Closed manifest validation, raw process capture, canonical result publication, and machine verification. |
| `task-1-evidence-host.ps1` | Minimal leaf host; imports the module in local module scope and records one child. |
| `task-1-static-verifier.ps1` | AST, import, automatic-variable, path, write-site, and forbidden-command checks before any child. |
| `task-1-synthetic-fixture.ps1` | Deterministic raw, high-volume, argv, nonzero, and timeout child behavior. |
| `task-1-invalid-executable.exe` | ASCII non-executable fixture that deterministically exercises process-start failure. |
| `task-1-invalid-manifests.ps1` | Read-only tests for duplicate, extra, escaping, collision, missing, and linked manifest cases using in-memory JSON plus frozen sentinel paths. |
| `task-1-preexisting.stdout.bin` | Apply-patch-authored sentinel whose bytes must remain exact during collision rejection. |
| `task-1-closure-verifier.ps1` | Recompute manifest/source/raw/result digests, terminals, inventory, and forbidden-action closure. |
| `task-1-report.md` | Final human index of all immutable coordination and machine evidence. |

Create exactly eight canonical manifests:

| Manifest | Command ID | Child purpose | Expected child result |
|---|---|---|---|
| `task-1-manifest-hostv2-001-unit-green.json` | `hostv2-001-unit-green` | Run the complete GREEN tests | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv2-002-raw.json` | `hostv2-002-raw` | Emit exact binary stdout and stderr | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv2-003-high-volume.json` | `hostv2-003-high-volume` | Fill both redirected pipes | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv2-004-argv.json` | `hostv2-004-argv` | Prove argument boundaries | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv2-005-nonzero.json` | `hostv2-005-nonzero` | Preserve a controlled nonzero exit | exit 23, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv2-006-timeout.json` | `hostv2-006-timeout` | Prove bounded kill and partial raw capture | timeout, `COMMAND_TIMEOUT` |
| `task-1-manifest-hostv2-007-start-failure.json` | `hostv2-007-start-failure` | Prove complete start-exception result | exit -1, `COMMAND_START_FAILURE` |
| `task-1-manifest-hostv2-008-closure.json` | `hostv2-008-closure` | Verify commands 001-007 and source inventory | exit 0, `COMMAND_COMPLETE` |

Each command produces exactly four files under `machine/` using its command ID and these suffixes: `.stdout.bin`, `.stderr.bin`, `.result.json`, and `.result.sha256`. The complete expected machine inventory is therefore 32 files.

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
    [Parameter(Mandatory)] [string] $A11HostModulePath
)
```

The test script accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Red', 'Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $ModulePath,
    [string] $HostPath,
    [string] $FixturePath,
    [string] $InvalidManifestTestPath,
    [string] $WorkspacePath
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

### Task 1: Prove clean entry and establish the intended RED

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-entry-gate.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-module-red.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-tests.ps1`

**Interfaces:**
- Consumes: exact plan commit, approved design blob, frozen failed report, frozen PowerShell path/hash, clean linked and canonical worktrees.
- Produces: `EVIDENCE_HOST_ENTRY_PASS` and one immutable bootstrap RED whose only failure is the missing three-function export set.

- [ ] **Step 1: Execute the read-only outer eligibility gate before creating the workspace**

Run these checks directly from the linked worktree. Do not create the workspace until every assertion passes:

```powershell
$RepositoryRoot = '<repo>\.worktrees\wave0-model-contract'
$CanonicalRoot = '<repo>'
$Workspace = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery'
$DesignPath = 'docs/superpowers/specs/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery-design.md'
$PlanPath = 'docs/superpowers/plans/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery.md'
$ExpectedBranch = 'codex/wave0-model-contract'
$ExpectedDesign = '4843cfe1579d9dc31f4994c6efa09f9de19fbdce'
$ExpectedPlan = git rev-parse HEAD

if ((git branch --show-current) -cne $ExpectedBranch) { throw 'branch mismatch' }
if ((git rev-parse 'HEAD^') -cne $ExpectedDesign) { throw 'plan parent mismatch' }
if (@(git diff-tree --no-commit-id --name-only -r HEAD).Count -ne 1) { throw 'plan path count mismatch' }
if ((git diff-tree --no-commit-id --name-only -r HEAD) -cne $PlanPath) { throw 'plan path mismatch' }
if ((git show -s --format='%an <%ae>' HEAD) -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'author mismatch' }
if ((git show -s --format='%cn <%ce>' HEAD) -cne 'kuotunyu <61350295+kuotunyu@users.noreply.github.com>') { throw 'committer mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree dirty' }
if (@(git -C $CanonicalRoot status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'canonical worktree dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging nonempty' }
if (Test-Path -LiteralPath $Workspace) { throw 'new workspace already exists' }
if ((git rev-parse "${ExpectedDesign}:$DesignPath") -cne '62df9b839bdfc61b7cd6a6d4416a0bff52011972') { throw 'design blob mismatch' }

$Report = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\task-1-report.md'
if ((Get-Item -LiteralPath $Report).Length -ne 6536) { throw 'failed report byte count mismatch' }
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Report).Hash.ToLowerInvariant() -cne '446a785ed2397ab3340ef2084536382a8cf0c065138879673ac6bd91e9b33c7c') { throw 'failed report digest mismatch' }

$OldMachineRoot = Join-Path $RepositoryRoot '.superpowers\sdd\2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery\machine'
$ForbiddenOld = @(
    'preformal-003-recorder-red-verify.stdout.bin',
    'preformal-003-recorder-red-verify.stderr.bin',
    'preformal-003-recorder-red-verify.result.json',
    'preformal-003-recorder-red-verify.result.sha256'
)
foreach ($Name in $ForbiddenOld) {
    if (Test-Path -LiteralPath (Join-Path $OldMachineRoot $Name)) { throw "preserved absent path appeared: $Name" }
}

$Pwsh = 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe'
if ((Get-FileHash -Algorithm SHA256 -LiteralPath $Pwsh).Hash.ToLowerInvariant() -cne 'db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f') { throw 'PowerShell digest mismatch' }
if ((Get-AuthenticodeSignature -LiteralPath $Pwsh).Status -cne 'Valid') { throw 'PowerShell signature invalid' }

"EVIDENCE_HOST_ENTRY_PASS|plan=$ExpectedPlan|workspace=absent|linked=clean|canonical=clean"
```

Require the exact `EVIDENCE_HOST_ENTRY_PASS` prefix. Any failure stops without creating the workspace.

- [ ] **Step 2: Create the fresh workspace and immutable RED subject with apply_patch**

Use `apply_patch` to add `task-1-entry-gate.ps1` containing the exact Step 1 checks with `$ExpectedPlan` replaced by the literal plan commit. Create `task-1-evidence-module-red.psm1` with exactly:

```powershell
Set-StrictMode -Version Latest

# Intentional RED subject: the approved recorder exports do not exist.
```

Do not execute the entry script again; its committed source is an audit record of the already completed read-only eligibility gate.

- [ ] **Step 3: Write the complete RED/GREEN test harness before GREEN implementation**

Use `apply_patch` to create `task-1-evidence-tests.ps1`. Its common helpers are exact and case-sensitive:

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Assert-A11True([bool] $Condition, [string] $Message) {
    if (-not $Condition) { throw $Message }
}

function Get-A11ExportNames([string] $Path) {
    $LibraryOnly = 'caller-sentinel'
    $BeforePid = $PID
    $Module = Import-Module -Name $Path -Scope Local -Force -PassThru
    Assert-A11True ($LibraryOnly -ceq 'caller-sentinel') 'caller LibraryOnly changed'
    Assert-A11True ($BeforePid -eq $PID) 'caller PID changed'
    return @($Module.ExportedFunctions.Keys | Sort-Object)
}

$ExpectedExports = @(
    'Invoke-A11RecordedChild',
    'Read-A11EvidenceManifest',
    'Test-A11MachineEvidence'
) | Sort-Object

if ($Mode -ceq 'Red') {
    try {
        $Actual = @(Get-A11ExportNames -Path $ModulePath)
        Assert-A11True (($Actual | ConvertTo-Json -Compress) -ceq ($ExpectedExports | ConvertTo-Json -Compress)) 'required export set missing'
        throw 'RED subject unexpectedly passed'
    } catch {
        if ($_.Exception.Message -cne 'required export set missing') { throw }
        [Console]::Out.WriteLine('EXPECTED_RED|required export set missing')
        exit 41
    }
}
```

The `Green` branch must use the same export assertion and perform these exact assertions without writing a file or starting a process:

```powershell
$HostTokens = $null
$HostErrors = $null
$ModuleTokens = $null
$ModuleErrors = $null
$HostAst = [System.Management.Automation.Language.Parser]::ParseFile($HostPath, [ref] $HostTokens, [ref] $HostErrors)
$ModuleAst = [System.Management.Automation.Language.Parser]::ParseFile($ModulePath, [ref] $ModuleTokens, [ref] $ModuleErrors)
Assert-A11True (@($HostErrors).Count -eq 0) 'host parser error'
Assert-A11True (@($ModuleErrors).Count -eq 0) 'module parser error'
Assert-A11True ($null -eq $ModuleAst.ParamBlock) 'module script-level param block present'

$Assignments = @($HostAst.FindAll({ param($Node) $Node -is [System.Management.Automation.Language.AssignmentStatementAst] }, $true)) +
               @($ModuleAst.FindAll({ param($Node) $Node -is [System.Management.Automation.Language.AssignmentStatementAst] }, $true))
$ForbiddenVariables = @('PID','HOME','HOST','ERROR','ARGS','INPUT','MATCHES','MYINVOCATION','PSBOUNDPARAMETERS','PSSCRIPTROOT','PSCOMMANDPATH','LASTEXITCODE')
foreach ($Assignment in $Assignments) {
    $Name = $Assignment.Left.Extent.Text.TrimStart('$').ToUpperInvariant()
    Assert-A11True ($ForbiddenVariables -cnotcontains $Name) "forbidden assignment: $Name"
}

$ActualExports = @(Get-A11ExportNames -Path $ModulePath)
Assert-A11True (($ActualExports | ConvertTo-Json -Compress) -ceq ($ExpectedExports | ConvertTo-Json -Compress)) 'GREEN export mismatch'
& $InvalidManifestTestPath -ModulePath $ModulePath -WorkspacePath $WorkspacePath
if ($LASTEXITCODE -ne 0) { throw 'invalid-manifest tests failed' }
[Console]::Out.WriteLine('EVIDENCE_TEST_SUITE_PASS')
exit 0
```

Also require the Green branch to assert that the AST contains no dot-source command, `Invoke-Expression`, `Start-Process`, top-level `return`/`exit`, or unexpected `Export-ModuleMember`; Task 2 freezes the authoritative static implementation of these checks.

- [ ] **Step 4: Run the exact bootstrap RED once**

Freeze the RED module and test bytes and SHA-256 values in the coordination notes, then run exactly:

```powershell
& 'C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe' `
    -NoProfile -NonInteractive -File `
    '.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-tests.ps1' `
    -Mode Red `
    -ModulePath '.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-module-red.psm1'
```

Require exit 41, stdout exactly `EXPECTED_RED|required export set missing` plus the platform newline, empty stderr, and no machine or child file. This is Layer 0 bootstrap coordination evidence, not machine command evidence. Any other result publishes `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO` and stops.

---

### Task 2: Implement the GREEN module and host, then pass static gates

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-module-green.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-evidence-host.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-static-verifier.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-invalid-manifests.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-preexisting.stdout.bin`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-closure-verifier.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-synthetic-fixture.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-invalid-executable.exe`

**Interfaces:**
- Consumes: intended RED from Task 1; no child has started.
- Produces: exact three-function module, two-parameter host, static PASS, immutable implementation hashes, invalid-manifest tests, and generic closure verifier.

- [ ] **Step 1: Implement closed manifest decoding first**

Use `apply_patch` to create `task-1-evidence-module-green.psm1`. Define no script-level parameter and execute no top-level action except `Set-StrictMode`, function definitions, and the final exact export statement. `Read-A11EvidenceManifest` has this signature:

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

It must read bytes with `[IO.File]::ReadAllBytes`, decode with strict `[Text.UTF8Encoding]::new($false, $true)`, reject BOM, require exactly one terminal LF and no CR/LF in the JSON body, parse with `System.Text.Json.JsonDocument`, reject duplicate properties by enumerating every object's properties into a case-sensitive `HashSet[string]`, and require this exact root property order:

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

Require `schema_version = 2`, command ID `^hostv2-[0-9]{3}-[a-z0-9-]+$`, `stdin_policy = closed`, `permitted_child_count = 1`, timeout policy to have only `mode` then `milliseconds`, environment order exactly `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, all vector lengths consistent, and all hashes lowercase 64-character hexadecimal. Rebuild the parsed object with ordered dictionaries, serialize with `ConvertTo-Json -Compress -Depth 12`, append one LF as strict UTF-8 without BOM, and require byte-for-byte equality with the input. Resolve every path with `[IO.Path]::GetFullPath`; reject UNC, device, relative, linked/reparse-point, escaping, duplicate, or colliding paths. Require the four output paths absent and exactly equal to the command-ID-derived paths under `machine/`. Verify host, module, executable, and every command source byte count/hash before returning one ordered manifest object.

Use private helpers `ConvertFrom-A11CanonicalManifestBytes` and `Assert-A11OrdinaryPath`. The latter accepts a private, test-only attribute-provider script block whose default calls `[IO.File]::GetAttributes`; production callers never supply it. This permits the Green test to inject `FileAttributes.ReparsePoint` and prove linked-path rejection without creating a link. Neither private helper is exported. Enrich the returned in-memory object with derived `manifest_path`, `manifest_byte_count`, and `manifest_sha256` fields after canonical input validation; these derived fields are not serialized back into the manifest.

- [ ] **Step 2: Implement raw child capture and canonical publication**

Define `Invoke-A11RecordedChild` with this exact signature:

```powershell
function Invoke-A11RecordedChild {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [System.Collections.IDictionary] $Manifest
    )
}
```

Its process setup must follow this structure without a shell string:

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

This is the required `ProcessStartInfo.ArgumentList` boundary; do not populate the legacy single `Arguments` string.

Open stdout and stderr with `FileMode.CreateNew`, `FileAccess.Write`, `FileShare.None`, 65,536-byte buffers, and `FileOptions.Asynchronous -bor FileOptions.WriteThrough` before process start. Start exactly one `System.Diagnostics.Process`; store its ID only in `$ChildProcessId`. Close standard input immediately. Start both `BaseStream.CopyToAsync` operations before waiting.

For `timeout_policy.mode = none`, wait once for completion. For `bounded`, race `WaitForExitAsync()` against `Task.Delay(milliseconds)`; when delay wins, call `Kill($true)` once, wait for the same process, and set `timed_out = true`. Always await both copy tasks, flush with `Flush($true)`, and dispose raw streams.

On process-start exception, publish zero-byte stdout and stderr, PID `-1`, exit `-1`, the exception type/message, and `COMMAND_START_FAILURE`. On a completed process publish `COMMAND_COMPLETE`; on bounded kill publish `COMMAND_TIMEOUT`. Never throw after raw files exist without attempting the create-new result and digest publication; any incomplete four-file set is a terminal capture gap.

The ordered result properties are exactly:

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

Serialize as compact UTF-8 JSON without BOM plus one LF. Publish result and digest through create-new `FileStream`; digest content is the lowercase result SHA-256 plus one LF.

- [ ] **Step 3: Implement independent machine verification and exact exports**

Define `Test-A11MachineEvidence` with this exact signature:

```powershell
function Test-A11MachineEvidence {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory)] [System.Collections.IDictionary] $Manifest
    )
}
```

It requires exactly four ordinary non-linked files, recomputes raw byte counts/hashes, requires result canonicalization and closed property order, verifies every identity/result field, verifies that the terminal is one of the three closed terminals and internally consistent with timeout/start-exception fields, verifies the digest-file bytes, and returns one ordered verification object without writing. Expected scenario-specific exit/terminal pairs are enforced by the already frozen test and closure verifiers. End the module with exactly:

```powershell
Export-ModuleMember -Function @(
    'Read-A11EvidenceManifest',
    'Invoke-A11RecordedChild',
    'Test-A11MachineEvidence'
)
```

- [ ] **Step 4: Implement the minimal leaf host**

Use `apply_patch` to create `task-1-evidence-host.ps1`. After its exact parameter block, it may only set strict/error policy, canonicalize the two inputs, prove both remain below `$PSScriptRoot`, read the manifest's frozen host/module identity with `JsonDocument`, compare current byte counts/hashes, import the exact module with `Import-Module -Name $A11HostModulePath -Scope Local -Force -PassThru`, compare the exact export set, call `Read-A11EvidenceManifest`, call `Invoke-A11RecordedChild` once, and call `Test-A11MachineEvidence` once.

It emits exactly one of these host lines and exits 0 only for the first:

```text
HOST_CAPTURE_COMPLETE|command_id=$($Manifest.command_id)|terminal=$($Verification.terminal)
EVIDENCE_HOST_STATIC_REJECTED / NO_GO
EVIDENCE_HOST_UNPROVABLE / NO_GO
EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO
```

The first line is the exact PowerShell double-quoted source expression; it emits literal values from the validated manifest and verification result. The host contains no dot-source operator, `LibraryOnly`, self-capture, recursive host start, alternate module, fallback, replacement manifest, or output reconstruction.

- [ ] **Step 5: Create fixtures, then implement invalid-manifest and static verifiers**

Before the static verifier runs, create `task-1-synthetic-fixture.ps1` with this exact source:

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
        $Json = ConvertTo-Json -InputObject @($Payload) -Compress
        [Console]::Out.Write($Json)
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

Create `task-1-invalid-executable.exe` with exact ASCII `A11 INVALID EXECUTABLE` plus one LF. Freeze both paths, byte counts, and SHA-256 values; do not execute them in this task.

Create the sentinel with apply_patch as exact ASCII bytes `A11-PREEXISTING-SENTINEL` plus one LF. `task-1-invalid-manifests.ps1` imports the module and uses `task-1-manifest-hostv2-002-raw.json`, whose machine destinations are still absent while command 001 runs, as its valid baseline. It invokes private pure validators in module scope to construct byte-array variants without writing JSON. It asserts case-sensitive rejection before process start for duplicate key, extra key, missing key, reordered key, escaping path, output collision, preexisting sentinel, injected `FileAttributes.ReparsePoint`, noncanonical hash, and vector-length mismatch. It recomputes the sentinel SHA-256 before and after, requires equality, writes exactly `INVALID_MANIFEST_TESTS_PASS`, and exits 0; an assertion failure exits nonzero.

`task-1-static-verifier.ps1` parses host, GREEN module, tests, invalid-manifest tests, fixture, and closure verifier. Use AST node types rather than text matching for assignments and dot-source detection. Reject the forbidden variable names from Task 1 plus every live variable whose `Options` contains `Constant` or `ReadOnly`. Require module top-level statements to be only strict mode, function definitions, and exact export. Require host parameters and module exports exact; forbid `Invoke-Expression`, `Start-Process`, shell-string invocation, redirection syntax, write cmdlets, Docker, `nvidia-smi`, CUDA, A11 launcher, Git mutation, network, and external-evidence paths.

Create `task-1-closure-verifier.ps1` now, before any GREEN execution. It reads only manifests, sources, and machine files; it never invokes an external command or writes a file. It verifies an explicit command-ID vector, expected four-file sets, exact manifest and source hashes, result canonicalization/digests, and the absence of any additional `machine/` file. With `-RequireFinalInventory`, it also requires the exact human-file inventory from this plan and final report.

- [ ] **Step 6: Parse and run the static verifier once**

First parse every complete `.ps1`/`.psm1` source with frozen PowerShell 7.6.4 and Windows PowerShell 5.1 without executing it. Then run `task-1-static-verifier.ps1` once through the frozen PowerShell path with literal absolute paths.

Require exact terminal:

```text
EVIDENCE_HOST_STATIC_PASS|exports=3|dot_source=0|forbidden_assignments=0|forbidden_commands=0
```

No host child or machine file may exist. Any parser/static failure publishes `EVIDENCE_HOST_STATIC_REJECTED / NO_GO` and stops. Do not modify any consumed GREEN source after this point.

---

### Task 3: Execute eight unique synthetic captures

**Files:**
- Read immutable: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-synthetic-fixture.ps1`
- Read immutable: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-invalid-executable.exe`
- Create: the eight exact `task-1-manifest-hostv2-*.json` files from the File and Interface Map.
- Create by evidence host only: 32 exact `machine/hostv2-*` files.

**Interfaces:**
- Consumes: immutable GREEN module/host/tests/verifiers and `EVIDENCE_HOST_STATIC_PASS`.
- Produces: seven distinct behavior captures plus one closure capture, with no retry or reused identity.

- [ ] **Step 1: Revalidate the immutable fixture and invalid executable**

Require the Task 2-frozen paths, byte counts, and SHA-256 values unchanged. The fixture accepts `Mode` plus remaining arguments and must still equal this exact source:

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
        $Json = ConvertTo-Json -InputObject @($Payload) -Compress
        [Console]::Out.Write($Json)
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

Require `task-1-invalid-executable.exe` still equals exact ASCII `A11 INVALID EXECUTABLE` plus one LF. It is a source fixture, never a generated binary.

- [ ] **Step 2: Freeze sources and create all eight canonical manifests with apply_patch**

Record the literal canonical path, byte count, and lowercase SHA-256 for the host, GREEN module, PowerShell executable, fixture, tests, invalid executable, invalid-manifest tests, closure verifier, and each manifest. Insert the literal observed values; do not leave a symbolic token or let a script generate JSON.

All manifests use schema 2, `permitted_child_count: 1`, `stdin_policy: "closed"`, the frozen PowerShell environment allowlist `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, and `USERPROFILE`, and the repository root working directory. Commands 001-006 and 008 use the frozen PowerShell executable. Command 007 uses `task-1-invalid-executable.exe` as its executable with empty argv.

Freeze these exact argv tails:

| ID | argv after `-NoProfile -NonInteractive -File` |
|---|---|
| 001 | test path, `-Mode`, `Green`, `-ModulePath`, GREEN module path, `-HostPath`, host path, `-FixturePath`, fixture path, `-InvalidManifestTestPath`, invalid-manifest test path, `-WorkspacePath`, workspace path |
| 002 | fixture path, `-Mode`, `Raw` |
| 003 | fixture path, `-Mode`, `HighVolume` |
| 004 | fixture path, `-Mode`, `Argv`, `-Payload`, `alpha beta`, empty string, `quote"value`, `中 文` |
| 005 | fixture path, `-Mode`, `Nonzero` |
| 006 | fixture path, `-Mode`, `Timeout` |
| 008 | closure path, `-WorkspacePath`, workspace path, `-ExpectedCommandIds`, literal IDs 001 through 007 |

Timeout mode is `none` with milliseconds 0 for 001-005, 007, and 008. Command 006 uses `bounded` with 500 milliseconds. Before any host start, require all 32 machine destinations absent and every human-authored manifest/source ordinary, non-linked, immutable, and exact.

- [ ] **Step 3: Execute command 001 once and require GREEN**

Invoke the frozen PowerShell executable with:

```text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery\task-1-evidence-host.ps1
-A11HostManifestPath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery\task-1-manifest-hostv2-001-unit-green.json
-A11HostModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery\task-1-evidence-module-green.psm1
```

Use literal absolute paths when executing. Require host exit 0, `HOST_CAPTURE_COMPLETE`, four files only for `hostv2-001-unit-green`, child exit 0, terminal `COMMAND_COMPLETE`, stdout exactly `EVIDENCE_TEST_SUITE_PASS` plus newline, and empty stderr. If any condition fails, preserve it as the first applicable `NO_GO` and stop without command 002.

- [ ] **Step 4: Execute command 002 once and verify exact binary bytes**

Require the raw stdout bytes `41 00 E4 B8 AD 0A 5A`, raw stderr bytes `45 52 52 00 FF`, exit 0, complete result/digest, and no decoded-stream substitution. Stop on any mismatch.

- [ ] **Step 5: Execute command 003 once and verify concurrent drain**

Require exactly 1,048,576 stdout bytes all `0x4F`, exactly 1,048,576 stderr bytes all `0x45`, exit 0, no timeout, and complete result/digest. Stop on any mismatch.

- [ ] **Step 6: Execute command 004 once and verify argv boundaries**

Require stdout to be the compact JSON array for exactly four payload elements: `alpha beta`, empty string, `quote"value`, and `中 文`, with no terminal newline; require empty stderr, exit 0, and exact manifest/result argv equality. Stop on any mismatch.

- [ ] **Step 7: Execute command 005 once and preserve controlled nonzero exit**

Require stdout bytes for `controlled-out`, stderr bytes for `controlled-error`, result exit 23, `timed_out = false`, terminal `COMMAND_COMPLETE`, and host exit 0 because capture itself completed. Stop on any mismatch.

- [ ] **Step 8: Execute command 006 once and preserve bounded timeout**

Require stdout begins with exact bytes for `timeout-started`, `timed_out = true`, terminal `COMMAND_TIMEOUT`, a finished timestamp, monotonic finish after start, the same child PID killed once, complete stderr and result/digest, and host exit 0 because the expected timeout was captured. Never start this fixture again.

- [ ] **Step 9: Execute command 007 once and preserve process-start failure**

Require zero-byte stdout and stderr, child PID `-1`, exit `-1`, `timed_out = false`, nonempty Win32 start-exception type/message, terminal `COMMAND_START_FAILURE`, complete result/digest, and host exit 0 because the expected start failure was captured. Never substitute another invalid executable.

- [ ] **Step 10: Execute command 008 once and capture closure of 001-007**

Require closure child exit 0, terminal `COMMAND_COMPLETE`, stdout exact prefix `EVIDENCE_MACHINE_CLOSURE_PASS|commands=7|machine_files=28`, empty stderr, and its own complete four-file set. The closure child must reject any missing, extra, linked, noncanonical, colliding, or digest-mismatched evidence among commands 001-007.

---

### Task 4: Verify final inventory and publish the recovery terminal

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/task-1-report.md`
- Read: all human-authored sources/manifests and 32 machine files.
- Modify tracked files: none.

**Interfaces:**
- Consumes: exact eight completed synthetic command identities and immutable workspace.
- Produces: one closure report and either the first exact `NO_GO` or `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.

- [ ] **Step 1: Run final direct read-only closure for all eight commands**

Run the already frozen closure verifier directly through the frozen signed PowerShell executable with the eight literal IDs and without `-RequireFinalInventory`. This Layer 0 verifier writes nothing and starts no nested process. It requires the exact pre-report human inventory and all 32 machine files; the final-inventory mode is reserved for Step 3 after the report exists.

Require exact terminal prefix:

```text
EVIDENCE_HOST_RECOVERY_CLOSURE_PASS|commands=8|machine_files=32
```

It must also require:

- every manifest/source byte count and SHA-256 exact;
- all 32 machine files ordinary, non-linked, canonical, and recomputable;
- result terminal/exit pairs exact for every command;
- host/module source and exported functions unchanged;
- the preexisting sentinel unchanged;
- the four old `preformal-003` paths still absent;
- the consumed report still 6,536 bytes and exact digest;
- linked tracked/staged/untracked scope clean except ignored workspace;
- canonical worktree clean; and
- zero Docker, GPU, entry, CPU, dependency, model, runtime, owner-ID, Tasks 2-8, push, merge, tag, or release evidence attributable to this recovery.

Any closure mismatch publishes `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO` and stops without a report that claims PASS.

- [ ] **Step 2: Create the final report once with apply_patch**

Create `task-1-report.md` only after closure PASS. Record:

- design and plan commit IDs, blobs, byte counts, SHA-256 values, author, committer, branch, and worktree topology;
- frozen consumed report identity and old absent-path proof;
- exact RED command, source hashes, exit 41, stdout/stderr, and `EXPECTED_RED` rationale;
- exact static verifier source/hash and terminal;
- host/module/tests/fixtures/verifiers paths, byte counts, SHA-256 values, and interfaces;
- every manifest path, byte count, SHA-256, argv, environment, timeout, and expected destination;
- every outer host tool exit and exact informational terminal;
- all 32 machine paths, byte counts, SHA-256 values, result fields, and digest verification;
- final closure command/tool result and workspace inventory;
- explicit proof of every forbidden action's non-occurrence; and
- the first exact terminal.

Do not quote decoded binary as a replacement for raw files and do not infer an absent value. The report is an index of immutable evidence, not evidence synthesis.

- [ ] **Step 3: Re-run final closure including the report identity**

Run the same frozen closure verifier once more only in its separately planned final-report mode, which performs no host or child start and was frozen before Task 3. It may read the newly created report, require it ordinary/non-linked, and output its byte count/SHA-256. This is a planned read-only verification, not a retry of a command or machine capture.

Require:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

If the report contradicts machine evidence, publish `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`; do not edit the report.

- [ ] **Step 4: Prove repository and authority closure**

Require HEAD remains this plan commit, no tracked/staged/untracked repository change, ignored changes confined exactly to the new workspace, canonical worktree clean, old workspaces byte-identical, no new external artifact directory, and no commit after the plan. Record that no implementation commit exists because this recovery creates ignored evidence infrastructure only.

Do not proceed to the complete A11 Task 1 entry gate. That requires a later approved plan consuming this PASS and its exact evidence identities.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserved `preformal-003` gap and no retry | Global Constraints; Task 1 Step 1; Task 4 Step 1 |
| Explicit Layer 0 coordination root | Architecture; Task 1 Step 4; Task 4 Steps 1,3 |
| Scope-isolated module and no dot-source | Task 2 Steps 1,4-6; Task 3 Step 3 |
| No self-capture or recursive host | Task 2 Steps 4-6 |
| Automatic-variable rejection | Task 1 Step 3; Task 2 Step 5 |
| Closed manifest and exact exports | File and Interface Map; Task 2 Steps 1,3-5 |
| Raw concurrent stdout/stderr | Task 2 Step 2; Task 3 Steps 4-5 |
| Canonical result and digest | Task 2 Steps 2-3; Task 3 Steps 3-10 |
| Create-new/no-clobber | Global Constraints; Task 2 Steps 1-3,5 |
| TDD RED before GREEN | Task 1 Steps 2-4; Task 2 |
| Unique identities and no retry | File and Interface Map; Task 3 Steps 2-10 |
| Start failure, nonzero, timeout | Task 3 Steps 7-9 |
| Independent recomputation | Task 3 Step 10; Task 4 Steps 1,3 |
| Exact final terminal, not entry PASS | Global Constraints; Task 4 Steps 3-4 |
| No Docker/GPU/runtime/OwnerAuthorizationId | Global Constraints; Task 2 Step 5; Task 4 Steps 1,4 |

## Plan Completion Gate

Before execution, require:

1. this plan is one file in a direct-child commit of `4843cfe1579d9dc31f4994c6efa09f9de19fbdce`;
2. commit author and committer are exact and its only changed path is this plan;
3. every design requirement maps to a task in the coverage matrix;
4. every file, function, parameter, command ID, terminal, machine suffix, and test expectation is type/name consistent;
5. no unresolved authoring marker, conflict marker, omitted error case, or unspecified implementation step remains;
6. linked and canonical worktrees are clean and the new workspace is absent; and
7. plan authoring executed no PowerShell test subject, evidence host, Docker, GPU, entry, model, or runtime command.
