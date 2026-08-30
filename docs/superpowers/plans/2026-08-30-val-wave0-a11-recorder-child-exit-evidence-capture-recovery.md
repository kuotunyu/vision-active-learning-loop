# Wave 0 A11 Recorder Child-Exit Evidence-Capture Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove a statically admitted observer preserves a real child exit 41 and exact raw stream identities, then complete the non-recursive synthetic evidence-host proof under fresh `hostv6-*` identities.

**Architecture:** A behavioral test first catches intentional nonzero-exit collapse, then proves the same production observer with a real synthetic exit-41 child. A one-shot formal static gate admits a canonical observer/child brief, after which the observer runs one fresh recorder RED and returns exit 0 only when the child exit and raw stream hashes are exact. Fresh GREEN recorder/host sources then capture eight unique children into 32 create-new machine files.

**Tech Stack:** PowerShell 7.6.4; Windows PowerShell 5.1 parser compatibility; .NET `System.Diagnostics.Process`, `ProcessStartInfo.ArgumentList`, `Process.ExitCode`, `Stream.CopyToAsync`, `MemoryStream`, `System.IO.Path`, `System.IO.Directory.GetParent`, `JsonDocument`, `Utf8JsonWriter`, `ArrayBufferWriter<byte>`, `SHA256`, `StringComparer`, `FileStream`, `Task`, and `Stopwatch`; Git; Markdown; ignored append-only evidence.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract`.
- Approved design commit is exactly `644cfb43f76a745896b4ae40c0b17126f336f145`; this plan commit must be its one-file direct child.
- Design path is `docs/superpowers/specs/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery-design.md`, Git blob `5d6701247efd4eed333c38e6e5aa8924d29a0cd6`.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- The v5 terminal remains `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`; its exact eight-file workspace and absent `machine/` directory are immutable.
- Preserved v4, v3, and v2 NO_GO workspaces contain exactly five, four, and three files respectively, with no machine directory.
- Never execute, modify, delete, rename, replace, copy over, retry, or schedule any v5/v4/v3/v2 source, brief, subject, command, destination, or workspace.
- The only new execution workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/`, and it must be absent at entry.
- Create every human-authored ignored file with `apply_patch`; never generate source, command-brief JSON, manifest JSON, binary fixture, sentinel, or report content with a script or shell redirection.
- Run the intentional observer RED exactly once, the production observer in `Contract` mode exactly once, the formal static source exactly once, the production observer in `Formal` mode exactly once, and each `hostv6-*` ID exactly once.
- Once a process consumes a source, test, brief, fixture, manifest, command identity, or destination, it is immutable.
- Any unexpected observer RED/GREEN, formal static, recorder RED, host, or closure result closes this plan; do not fix, replace, or retry it.
- Every filesystem ancestor walk stores a canonical path string and calls `[IO.Directory]::GetParent($Cursor)`. No filesystem item returned by `Get-Item` is queried for `.Parent`.
- Every path-bearing process argument is a literal fully qualified Windows path. No receiver supports relative fallback, module-name search, PATH search, or alternate candidate.
- Observer and bootstrap executable sources contain no `ConvertTo-Json` or `JsonSerializer.Serialize`; canonical reconstruction uses explicit `Utf8JsonWriter` calls with `UnsafeRelaxedJsonEscaping`.
- The observer creates no file. Before fresh recorder RED PASS, the `machine/` directory and every sidecar/transcript/result path remain absent.
- The evidence host may create only the exact 32 predetermined `machine/hostv6-*` files.
- Do not inspect or execute Docker CLI, Docker Desktop processes, Docker/WSL/Hyper-V pipes, builders, images, containers, caches, volumes, GPU, `nvidia-smi`, CUDA, CPU baseline, dependencies, model, A11 launcher, entry child, formal runtime, Wave 1, or product Tasks 2-8.
- Do not create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`.
- Do not modify product code, the seven-file A11 implementation allowlist, external evidence, another repository, a remote, or Git history.
- Do not push, merge, tag, release, amend, rebase, reset, stash, or delete preserved evidence.
- The only success terminal is `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.
- Execution creates ignored evidence only; there is no tracked implementation commit after this plan commit.

## Normative Inputs

- Approved design: commit `644cfb43f76a745896b4ae40c0b17126f336f145`, blob `5d6701247efd4eed333c38e6e5aa8924d29a0cd6`.
- Required plan parent: `644cfb43f76a745896b4ae40c0b17126f336f145`.
- Frozen PowerShell: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`, 301,368 bytes, SHA-256 `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`, valid Authenticode signature.
- Repository root: `<repo>\.worktrees\wave0-model-contract`.
- Canonical worktree: `<repo>`.
- Expected recorder stdout: ASCII `EXPECTED_RED|required export set missing` plus CRLF, exactly 42 bytes, SHA-256 `76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0`.
- Expected empty stderr: 0 bytes, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
- Fresh recorder RED module: 97 bytes, SHA-256 `ce397973b2befb90d573547d5154a1c3ca5b415c6647464592828fe08d1d878e`.

The immediate v5 workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/`:

| File | Bytes | SHA-256 |
|---|---:|---|
| `task-1-ancestor-chain-red-v5.ps1` | 1,436 | `dfa8f9b572ff31439b8198acd014d53c0efbc408ab50cbce156423293e92b9ac` |
| `task-1-ancestor-chain-tests-v5.ps1` | 8,798 | `07dc9df03102dd64c6d79326c25281fcd143246618777a0c55abfb917623ca09` |
| `task-1-bootstrap-command-static-v5.ps1` | 20,783 | `8ae484662c7f5165b721ad70e3213f1aad43f4b5d238af5282e6ecda1df051f9` |
| `task-1-bootstrap-red-brief-v5.md` | 5,003 | `5d5a95ef800a34f5cfb9a65833367191bde725f6741bb2d79fce0c626644da27` |
| `task-1-entry-gate-v5.ps1` | 6,250 | `2d1b8f10842d6abdc8bea772d258f593b733b2fa7a8af21522c569199fb7dee1` |
| `task-1-evidence-module-red-v5.psm1` | 97 | `efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071` |
| `task-1-evidence-tests-v5.ps1` | 12,339 | `21b59e3e4264706d095c5135a9c1a71fc7ada45dfb2731c02badf0134818c92b` |
| `task-1-red-command-v5.json` | 1,437 | `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3` |

## File and Interface Map

Execution changes no tracked file. Create these ignored human-authored files:

| Path | Responsibility |
|---|---|
| `task-1-entry-gate-v6.ps1` | Audit copy of exact entry/preservation proof. |
| `task-1-observer-contract-tests-v6.ps1` | Launch and assert the real observer RED/GREEN subjects. |
| `task-1-observer-exit-fixture-v6.ps1` | Emit fixed 42-byte stdout, empty stderr, and exit 41. |
| `task-1-observer-red-v6.ps1` | Intentional nonzero-to-one observer RED. |
| `task-1-observer-contract-command-v6.json` | Canonical synthetic-child contract. |
| `task-1-recorder-child-observer-v6.ps1` | Production in-memory child-exit/raw-stream observer. |
| `task-1-recorder-module-red-v6.psm1` | Fresh recorder RED with no exports. |
| `task-1-recorder-tests-v6.ps1` | Complete recorder RED/GREEN test using path-string ancestry. |
| `task-1-recorder-formal-command-v6.json` | Canonical observer and fresh recorder child contract. |
| `task-1-recorder-child-exit-static-v6.ps1` | One-shot parser/AST/path/canonical formal admission. |
| `task-1-bootstrap-red-brief-v6.md` | Observer contract/static/recorder-RED identity index. |
| `task-1-evidence-module-green-v6.psm1` | Schema-6 manifest validation, raw capture, result publication, verification. |
| `task-1-evidence-host-v6.ps1` | Minimal non-recursive leaf host. |
| `task-1-static-verifier-v6.ps1` | GREEN parser, AST, path-flow, write-site, and forbidden-command gate. |
| `task-1-synthetic-fixture-v6.ps1` | Deterministic raw, volume, argv, nonzero, and timeout behavior. |
| `task-1-invalid-executable-v6.exe` | Deterministic ASCII non-executable. |
| `task-1-invalid-manifests-v6.ps1` | Read-only malformed/colliding/path-contract manifest tests. |
| `task-1-preexisting-v6.stdout.bin` | Apply-patch no-clobber sentinel. |
| `task-1-closure-verifier-v6.ps1` | Independent contract/source/machine/result/inventory closure. |
| `task-1-report.md` | Final evidence index and first exact terminal. |

Create eight schema-6 manifests:

| Manifest | Command ID | Planned result |
|---|---|---|
| `task-1-manifest-hostv6-001-unit-green.json` | `hostv6-001-unit-green` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv6-002-raw.json` | `hostv6-002-raw` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv6-003-high-volume.json` | `hostv6-003-high-volume` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv6-004-argv.json` | `hostv6-004-argv` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv6-005-nonzero.json` | `hostv6-005-nonzero` | exit 23, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv6-006-timeout.json` | `hostv6-006-timeout` | `COMMAND_TIMEOUT` |
| `task-1-manifest-hostv6-007-start-failure.json` | `hostv6-007-start-failure` | exit -1, `COMMAND_START_FAILURE` |
| `task-1-manifest-hostv6-008-closure.json` | `hostv6-008-closure` | exit 0, `COMMAND_COMPLETE` |

Each command creates `.stdout.bin`, `.stderr.bin`, `.result.json`, and `.result.sha256`, for exactly 32 machine files. Total human-authored ignored files are exactly 28.

The production observer accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Contract', 'Formal')] [string] $Mode,
    [Parameter(Mandatory)] [string] $CommandBriefPath
)
```

The observer behavioral test accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Red', 'Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $SubjectPath,
    [Parameter(Mandatory)] [string] $ExpectedSubjectPath,
    [Parameter(Mandatory)] [long] $ExpectedSubjectByteCount,
    [Parameter(Mandatory)] [string] $ExpectedSubjectSha256,
    [Parameter(Mandatory)] [string] $CommandBriefPath,
    [Parameter(Mandatory)] [string] $ExpectedCommandBriefPath,
    [Parameter(Mandatory)] [long] $ExpectedCommandBriefByteCount,
    [Parameter(Mandatory)] [string] $ExpectedCommandBriefSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath
)
```

The GREEN recorder module exports exactly `Read-A11EvidenceManifest`, `Invoke-A11RecordedChild`, and `Test-A11MachineEvidence`. The leaf host accepts exactly `A11HostManifestPath`, `A11HostModulePath`, and `A11HostExpectedWorkspace`.

---

### Task 1: Prove entry and complete observer-contract RED→GREEN

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-entry-gate-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-observer-contract-tests-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-observer-exit-fixture-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-observer-red-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-observer-contract-command-v6.json`
- Create after RED: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-recorder-child-observer-v6.ps1`

**Interfaces:**
- Consumes: exact design/plan lineage, four frozen NO_GO inventories, signed PowerShell identity, clean linked/canonical worktrees, and no fresh workspace.
- Produces: one intentional normalization RED, one real exit-41 observer GREEN, and frozen production observer/fixture/contract identities with no file side effect.

- [ ] **Step 1: Run the complete read-only entry before workspace creation**

Verify linked-worktree topology and non-submodule state; branch; HEAD direct parent `644cfb43f76a745896b4ae40c0b17126f336f145`; one changed plan path; author/committer; linked/canonical clean state; empty staging; fresh workspace absence; design blob; exact v5 eight-file hashes and no machine directory; v4/v3/v2 exact inventories and no machine directories; four older absent `preformal-003` paths; and frozen PowerShell bytes/hash/signature.

Construct the terminal without a commit placeholder:

```powershell
$ExpectedPlan = git rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $ExpectedPlan -notmatch '^[0-9a-f]{40}$') { throw 'plan commit identity rejected' }
"CHILD_EXIT_RECOVERY_ENTRY_PASS|plan=$ExpectedPlan|workspace=absent|v5=8|v4=5|v3=4|v2=3|linked=clean|canonical=clean"
```

Any failure stops without creating the workspace.

- [ ] **Step 2: Create the audit, test, fixture, contract brief, and intentional RED**

Use `apply_patch`. The audit entry is never executed after workspace creation. The behavioral test validates subject and brief absolute/canonical/contained/ordinary bytes/hash identities with a path-string ancestor walker; launches the subject through frozen PowerShell using `ProcessStartInfo.ArgumentList`; captures subject stdout/stderr in memory; and requires zero sidecar/machine paths.

Create the exact fixture as LF/UTF-8 without BOM:

```powershell
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [ValidateSet('RecorderRed')] [string] $Mode
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

if ($Mode -cne 'RecorderRed') { throw 'fixture mode rejected' }
$Payload = [Text.Encoding]::ASCII.GetBytes("EXPECTED_RED|required export set missing`r`n")
$Stdout = [Console]::OpenStandardOutput()
try {
    $Stdout.Write($Payload, 0, $Payload.Length)
    $Stdout.Flush()
}
finally {
    $Stdout.Dispose()
}
exit 41
```

Require 478 bytes and SHA-256 `55fe8ce2197136aafeb669fc63faae09a2a5643c4c5de48acdaf06bcfbc2c842`.

Create `task-1-observer-contract-command-v6.json` as one compact UTF-8 line plus LF with exact content:

```json
{"schema_version":1,"brief_kind":"contract","command_id":"observerv6-contract-001","child_executable_path":"C:\\Users\\<user>\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\powershell\\pwsh.exe","child_executable_byte_count":301368,"child_executable_sha256":"db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f","child_working_directory":"<repo>\\.worktrees\\wave0-model-contract","child_argv":["-NoProfile","-NonInteractive","-File","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\\task-1-observer-exit-fixture-v6.ps1","-Mode","RecorderRed"],"child_sources":[{"path":"<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\\task-1-observer-exit-fixture-v6.ps1","byte_count":478,"sha256":"55fe8ce2197136aafeb669fc63faae09a2a5643c4c5de48acdaf06bcfbc2c842"}],"expected_exit_code":41,"expected_stdout_byte_count":42,"expected_stdout_sha256":"76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0","expected_stderr_byte_count":0,"expected_stderr_sha256":"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","sidecar_paths":[]}
```

Require 1,412 bytes and SHA-256 `7e6b3c5e529413ae81540915503cc6aea3c5bc10cc07f337c7ae2dbae04d1583`.

The intentional observer implements the production two-parameter interface with `Contract` only. It parses the exact contract brief, starts the synthetic child once, concurrently captures both streams, reads the real child exit, deliberately normalizes every nonzero exit to 1, requires the real exit was 41 and normalized exit is 1, emits only `EXPECTED_CHILD_EXIT_RED|observed=1|expected=41`, and exits 43. It creates no file.

- [ ] **Step 3: Run the observer RED exactly once**

Parse audit/test/fixture/RED under PowerShell 7.6.4 and Windows PowerShell 5.1. Require exact source and brief identities, no machine directory, no sidecar path, one child start, and the behavioral test authored before the subject.

Run the behavioral test in `Red` mode with the RED subject and exact contract brief identities. It independently requires subject exit 43, exact stdout plus CRLF, empty stderr, and zero files. Its sole output is:

```text
CHILD_EXIT_OBSERVER_TEST_RED_PASS|fault=nonzero_collapsed|observed=1|expected=41
```

Any difference is `CHILD_EXIT_OBSERVER_UNPROVABLE / NO_GO`; do not rerun.

- [ ] **Step 4: Implement the production observer after exact RED**

Use `apply_patch`. Share one private parser/validator and one private child runner across both modes. The runner's required data flow is:

```powershell
$StartInfo = [Diagnostics.ProcessStartInfo]::new()
$StartInfo.FileName = $ValidatedChildExecutable
$StartInfo.WorkingDirectory = $ValidatedChildWorkingDirectory
$StartInfo.UseShellExecute = $false
$StartInfo.CreateNoWindow = $true
$StartInfo.RedirectStandardInput = $true
$StartInfo.RedirectStandardOutput = $true
$StartInfo.RedirectStandardError = $true
foreach ($Argument in $ValidatedChildArgv) { [void] $StartInfo.ArgumentList.Add([string] $Argument) }

$Process = [Diagnostics.Process]::new()
$Process.StartInfo = $StartInfo
$StdoutMemory = [IO.MemoryStream]::new()
$StderrMemory = [IO.MemoryStream]::new()
try {
    if (-not $Process.Start()) { throw 'child process did not start' }
    $Process.StandardInput.Close()
    $StdoutTask = $Process.StandardOutput.BaseStream.CopyToAsync($StdoutMemory)
    $StderrTask = $Process.StandardError.BaseStream.CopyToAsync($StderrMemory)
    $Process.WaitForExit()
    $ChildExitCode = $Process.ExitCode
    $StdoutTask.GetAwaiter().GetResult()
    $StderrTask.GetAwaiter().GetResult()
    $StdoutBytes = $StdoutMemory.ToArray()
    $StderrBytes = $StderrMemory.ToArray()
}
finally {
    $Process.Dispose()
    $StdoutMemory.Dispose()
    $StderrMemory.Dispose()
}
```

The complete source validates strict UTF-8 canonical brief bytes, recursive duplicates, kind-specific property order/types, executable signature, child source identities, one child, expected raw facts, `sidecar_paths=[]`, and absent machine directory. It contains exactly one `.Start()`, one `.WaitForExit()`, and one `.ExitCode` read; no retry loop, timeout retry, shell, sidecar, file write, or predecessor path.

`Contract` emits only:

```text
CHILD_EXIT_OBSERVER_CONTRACT_PASS|child_exit=41|stdout_bytes=42|stderr_bytes=0|sidecars=0
```

`Formal` emits only the recorder terminal specified in Task 2.

- [ ] **Step 5: Run the same behavioral test against production observer once**

Before execution, parse all Task 1 sources under both parsers; AST-require one start/wait/exit-code data path, concurrent `CopyToAsync`, no filesystem `.Parent`, sidecar, write, retry, shell string, dynamic evaluation, redirection, Docker/GPU/A11/product/Git/network command, or machine directory. Freeze exact source identities.

Run the behavioral test in `Green` mode. It invokes the production observer in `Contract` mode with the exact contract brief. Require observer exit 0, exact contract terminal plus CRLF, empty stderr, and no file. The test emits only:

```text
CHILD_EXIT_OBSERVER_TEST_GREEN_PASS|child_exit=41|stdout_bytes=42|stderr_bytes=0
```

Any difference is `CHILD_EXIT_OBSERVER_UNPROVABLE / NO_GO`; never edit or rerun. Exact PASS freezes the behavioral test, fixture, contract brief, and production observer.

---

### Task 2: Admit and observe one fresh recorder RED

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-recorder-module-red-v6.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-recorder-tests-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-recorder-formal-command-v6.json`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-recorder-child-exit-static-v6.ps1`
- Create after static PASS: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-bootstrap-red-brief-v6.md`

**Interfaces:**
- Consumes: frozen observer contract RED/GREEN identities and no sidecar/machine state.
- Produces: one formal static PASS and one observer-proven fresh recorder RED with exact child exit 41 and raw identities.

- [ ] **Step 1: Create the fresh recorder RED and complete RED/GREEN test first**

Create the RED module with LF/UTF-8 no BOM:

```powershell
Set-StrictMode -Version Latest

# Intentional hostv6 RED subject: recorder exports do not exist.
```

Require 97 bytes and SHA-256 `ce397973b2befb90d573547d5154a1c3ca5b415c6647464592828fe08d1d878e`.

Create the complete recorder test before GREEN source. Its exact leading interface is:

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

It validates the module with path-string ancestry, imports only `Import-Module -Name $ValidatedModulePath`, proves caller `LibraryOnly` and `$PID` unchanged, and compares exact exports. RED emits `EXPECTED_RED|required export set missing` and exits 41. GREEN parses module/host/fixture/invalid-test sources, rejects forbidden behavior, invokes invalid-manifest tests, and emits only `EVIDENCE_TEST_SUITE_PASS`. It contains no dynamic serializer.

- [ ] **Step 2: Freeze identities and author the canonical formal brief**

Measure and print one immutable identity table for production observer, recorder test, RED module, frozen PowerShell, and workspace. Use those literal decimal byte counts and lowercase hashes in `apply_patch`; do not generate JSON.

The formal brief root property order is exactly:

```text
schema_version
brief_kind
command_id
observer_executable_path
observer_executable_byte_count
observer_executable_sha256
observer_source_path
observer_source_byte_count
observer_source_sha256
observer_working_directory
observer_argv
child_executable_path
child_executable_byte_count
child_executable_sha256
child_working_directory
child_argv
child_sources
expected_exit_code
expected_stdout_byte_count
expected_stdout_sha256
expected_stderr_byte_count
expected_stderr_sha256
sidecar_paths
```

Fixed values are `schema_version=1`, `brief_kind=formal`, `command_id=observerv6-formal-recorder-red-001`, both executables equal frozen PowerShell, both working directories equal repository root, expected exit 41, stdout 42/`76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0`, stderr 0/`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, and empty sidecars.

`observer_argv` is exactly:

```text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\task-1-recorder-child-observer-v6.ps1
-Mode
Formal
-CommandBriefPath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\task-1-recorder-formal-command-v6.json
```

`child_argv` is exactly:

```text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\task-1-recorder-tests-v6.ps1
-Mode
Red
-ModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\task-1-recorder-module-red-v6.psm1
-ExpectedModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery\task-1-recorder-module-red-v6.psm1
-ExpectedModuleByteCount
97
-ExpectedModuleSha256
ce397973b2befb90d573547d5154a1c3ca5b415c6647464592828fe08d1d878e
-WorkspacePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery
```

`child_sources` contains exactly two ordered objects with property order `role,path,byte_count,sha256`: role `recorder_test`, then role `recorder_red_module`. Immediately recompute strict UTF-8/LF bytes and SHA-256 and freeze the brief.

- [ ] **Step 3: Create and non-consumingly prove the formal static source**

Create a formal static source with this exact interface:

```powershell
param(
    [Parameter(Mandatory)] [string] $ObserverPath,
    [Parameter(Mandatory)] [string] $ExpectedObserverPath,
    [Parameter(Mandatory)] [long] $ExpectedObserverByteCount,
    [Parameter(Mandatory)] [string] $ExpectedObserverSha256,
    [Parameter(Mandatory)] [string] $RecorderTestPath,
    [Parameter(Mandatory)] [string] $ExpectedRecorderTestPath,
    [Parameter(Mandatory)] [long] $ExpectedRecorderTestByteCount,
    [Parameter(Mandatory)] [string] $ExpectedRecorderTestSha256,
    [Parameter(Mandatory)] [string] $RedModulePath,
    [Parameter(Mandatory)] [string] $ExpectedRedModulePath,
    [Parameter(Mandatory)] [long] $ExpectedRedModuleByteCount,
    [Parameter(Mandatory)] [string] $ExpectedRedModuleSha256,
    [Parameter(Mandatory)] [string] $FormalBriefPath,
    [Parameter(Mandatory)] [string] $ExpectedFormalBriefPath,
    [Parameter(Mandatory)] [long] $ExpectedFormalBriefByteCount,
    [Parameter(Mandatory)] [string] $ExpectedFormalBriefSha256,
    [Parameter(Mandatory)] [string] $WorkspacePath
)
```

It validates every path with canonical path-string ancestry; parses observer/test under both parsers; requires test import from `$ValidatedModulePath`; counts exactly one observer `.Start()`, `.WaitForExit()`, `.ExitCode`, two `CopyToAsync`, and zero file writes/retry/sidecar/shell/dynamic serializer/predecessor execution; validates formal brief schema/order/types/argv/source identities; verifies executable signature; reconstructs canonical JSON with `Utf8JsonWriter`; and requires absent machine directory.

Before consuming it, run an isolated in-memory writer microcheck against the formal brief bytes and parse every source under PowerShell 7.6.4 and Windows PowerShell 5.1.

- [ ] **Step 4: Run formal static exactly once**

Invoke frozen PowerShell with literal source/brief/workspace paths and the frozen identity table. Require exit 0, empty stderr, and sole stdout:

```text
RECORDER_CHILD_EXIT_STATIC_PASS|observer=contract-proven|brief=canonical|child_exit=41|exitcode_reads=1|sidecars=0|retries=0
```

Any difference is `RECORDER_CHILD_EXIT_STATIC_REJECTED / NO_GO`; preserve and stop without recorder RED.

- [ ] **Step 5: Freeze bootstrap evidence and run observer Formal exactly once**

After static PASS, create the Markdown bootstrap brief with exact entry, observer RED/GREEN commands/results, fixture/contract/observer/test/module/formal-brief/static/executable identities, expected raw facts, observer argv, child argv, and zero sidecar/machine identities. Never edit it.

Run frozen PowerShell with the exact `observer_argv` from the formal brief. Require outer observer exit 0, empty stderr, no file, and sole stdout:

```text
RECORDER_RED_OBSERVER_PASS|child_exit=41|stdout_bytes=42|stdout_sha256=76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0|stderr_bytes=0|stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

The observer must have started the fresh recorder child exactly once. Any exit, output, identity, process count, side effect, or inventory difference is `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`; never rerun observer Formal or the child.

---

### Task 3: Implement and statically prove the GREEN recorder/host

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-evidence-module-green-v6.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-evidence-host-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-static-verifier-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-synthetic-fixture-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-invalid-executable-v6.exe`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-invalid-manifests-v6.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-preexisting-v6.stdout.bin`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-closure-verifier-v6.ps1`

**Interfaces:**
- Consumes: exact observer-proven fresh recorder RED and frozen bootstrap identities.
- Produces: side-effect-free three-export module, leaf host, deterministic fixtures, closure verifier, and static PASS before any machine child.

The module public interfaces are exactly:

```powershell
function Read-A11EvidenceManifest {
    param(
        [Parameter(Mandatory)] [string] $ManifestPath,
        [Parameter(Mandatory)] [string] $ExpectedWorkspace
    )
}

function Invoke-A11RecordedChild {
    param([Parameter(Mandatory)] [pscustomobject] $ManifestRecord)
}

function Test-A11MachineEvidence {
    param(
        [Parameter(Mandatory)] [pscustomobject] $ManifestRecord,
        [Parameter(Mandatory)] [pscustomobject] $CaptureRecord
    )
}
```

`Read-A11EvidenceManifest` returns one enriched in-memory manifest record. `Invoke-A11RecordedChild` returns one in-memory capture record after publishing four create-new files. `Test-A11MachineEvidence` returns one verified record and writes nothing. The host stores each return value and invokes each export exactly once.

- [ ] **Step 1: Implement path and canonical schema-6 helpers**

Only after recorder RED PASS, create the GREEN module. Module scope permits `Set-StrictMode`, function definitions, and final `Export-ModuleMember` only.

Private path validation rejects null/whitespace, wildcard, provider, URI, UNC, device, ADS, relative, escaping, wrong-kind, linked, wrong-byte, and wrong-hash inputs. Every ancestor chain uses:

```powershell
$Cursor = [IO.Path]::GetFullPath($CanonicalPath)
while ($true) {
    if (Test-Path -LiteralPath $Cursor) {
        $Item = Get-Item -LiteralPath $Cursor -Force
        if ($Item -isnot [IO.FileInfo] -and $Item -isnot [IO.DirectoryInfo]) { throw 'filesystem item type rejected' }
        $LinkProperty = $Item.PSObject.Properties['LinkType']
        if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or
            ($null -ne $LinkProperty -and -not [string]::IsNullOrEmpty([string] $LinkProperty.Value))) { throw 'linked path rejected' }
    }
    $Parent = [IO.Directory]::GetParent($Cursor)
    if ($null -eq $Parent) { break }
    $Cursor = $Parent.FullName
}
```

Manifest root property order is exactly `schema_version,command_id,host_path,host_byte_count,host_sha256,module_path,module_byte_count,module_sha256,executable_path,executable_byte_count,executable_sha256,working_directory,argv,environment,stdin,timeout,expected_child_count,sources,stdout_path,stderr_path,result_path,result_sha256_path`. Require schema 6, command regex `^hostv6-[0-9]{3}-[a-z0-9-]+$`, environment order `SystemRoot,WINDIR,TEMP,TMP,USERPROFILE`, timeout order `mode,milliseconds`, stdin `closed`, expected child count 1, ordered source objects `role,path,byte_count,sha256`, and four absent unique command-derived destinations.

- [ ] **Step 2: Implement exact public exports and canonical result publication**

Implement:

```powershell
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

Manifest read validates all source identities before file access and enriches only in memory. Raw capture uses `ProcessStartInfo.ArgumentList`, cleared allowlisted environment, closed stdin, concurrent `BaseStream.CopyToAsync`, create-new raw streams, one wait or one bounded delay/kill, and create-new result/digest.

Result property order is exactly `schema_version,command_id,terminal,started,pid,exit_code,timed_out,duration_ms,stdout_byte_count,stdout_sha256,stderr_byte_count,stderr_sha256,exception_type,exception_hresult,exception_message,child_count,manifest_path,manifest_byte_count,manifest_sha256`. Digest file is the lowercase SHA-256 of exact result bytes plus one LF. Start failure yields zero streams, PID/exit -1, nonempty exception fields, and `COMMAND_START_FAILURE`; timeout yields `COMMAND_TIMEOUT`; normal exit, including 23, yields `COMMAND_COMPLETE`.

Independent verification recomputes all four files, canonical result fields/order, raw identities, terminal consistency, and digest bytes and writes nothing.

- [ ] **Step 3: Implement the minimal leaf host**

Use exact parameters `A11HostManifestPath`, `A11HostModulePath`, and `A11HostExpectedWorkspace`. Validate every path with path-string ancestry, read frozen source identities from the manifest, import only the validated module, require exact exports, and call each once.

Success constructs exactly:

```powershell
"HOST_CAPTURE_COMPLETE|command_id=$CommandId|terminal=$Terminal"
```

where both variables came from the validated manifest/result pair. Missing/partial Layer 2 is `EVIDENCE_HOST_UNPROVABLE / NO_GO`; complete invalid evidence is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`. Never self-capture, recurse, retry, replace a manifest, or choose an alternate path.

- [ ] **Step 4: Create deterministic fixtures and invalid-manifest tests**

The fixture interface is exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Raw', 'HighVolume', 'Argv', 'Nonzero', 'Timeout')] [string] $Mode,
    [Parameter(ValueFromRemainingArguments)] [AllowEmptyString()] [string[]] $Payload
)
```

Use literal raw bytes `41 00 E4 B8 AD 0A 5A` and `45 52 52 00 FF`; one-megabyte `0x4F`/`0x45` streams; compact argv JSON; controlled exit 23; and `timeout-started` followed by five seconds.

Create invalid executable as ASCII `A11 V6 INVALID EXECUTABLE` plus LF and sentinel as ASCII `A11-V6-PREEXISTING-SENTINEL` plus LF. Invalid-manifest tests accept exactly `ModulePath`, `WorkspacePath`, `HostPath`, and `FixturePath`; cover relative/UNC/provider/URI/ADS/escaping/linked/duplicate/extra/missing/reordered/noncanonical/source-vector/collision/preexisting failures; preserve sentinel identity; and emit only `INVALID_MANIFEST_TESTS_PASS`.

- [ ] **Step 5: Create closure/static verifiers and run static gate once**

Closure is complete before any host child and writes nothing. Its exact interface is:

```powershell
param(
    [Parameter(Mandatory)] [string] $WorkspacePath,
    [Parameter(Mandatory)] [ValidateCount(7, 8)] [string[]] $CommandIds,
    [switch] $RequireFinalInventory
)
```

It verifies explicit IDs, observer RED/GREEN/static/recorder evidence, source/brief/manifest/machine/result identities, and pre-report/final inventories.

The GREEN static verifier accepts `WorkspacePath` plus explicit path/expected-path/byte-count/SHA-256 quartets for module, host, recorder test, synthetic fixture, invalid-manifest test, and closure verifier. It accepts the invalid executable and sentinel as explicit path/expected-path/byte-count/SHA-256 quartets as well. No argument is optional.

Static verifier parses all complete sources under both parsers; requires exact exports/host parameters, one frozen observer evidence chain, no filesystem `.Parent`, dot-source, dynamic evaluation, `Start-Process`, shell string, redirection, top-level module side effect, protected-variable assignment, predecessor execution, or Docker/GPU/A11/product/Git/network/runtime command. Require validated absolute flows and create-new writes limited to 32 destinations.

Run once and require:

```text
EVIDENCE_HOST_STATIC_PASS|exports=3|observer=child-exit-proven|ancestor=path-string|absolute_flows=all|forbidden_assignments=0|forbidden_commands=0
```

No machine path may exist. Any failure is `EVIDENCE_HOST_STATIC_REJECTED / NO_GO`; freeze all GREEN sources after PASS.

---

### Task 4: Author and execute eight unique hostv6 captures

**Files:**
- Create: eight `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-manifest-hostv6-*.json` files.
- Create by host only: 32 `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/machine/hostv6-*` files.
- Modify existing source: none.

**Interfaces:**
- Consumes: frozen GREEN/static PASS and exact source identities.
- Produces: seven behavior captures and one independent closure capture.

- [ ] **Step 1: Freeze identities and create all manifests with apply_patch**

Measure host/module/PowerShell/test/fixture/invalid executable/invalid tests/closure/sentinel/observer/bootstrap sources and every command source. Manually author compact schema-6 JSON with the exact property orders from Task 3, absolute paths, repository working directory, ordered environment, closed stdin, one child, and four absent unique destinations.

Commands 001-006 and 008 use frozen PowerShell; 007 uses invalid executable. Command 001 runs recorder tests in Green mode. Commands 002-006 run fixture Raw/HighVolume/Argv/Nonzero/Timeout. Command 004 payload is `alpha beta`, empty string, `quote"value`, `中 文`. Command 008 closes IDs 001-007. Timeout is `bounded`/500 only for 006 and `none`/0 otherwise.

- [ ] **Step 2: Execute hostv6-001 once**

Require host exit 0, exact capture terminal, four 001 files, child exit 0/`COMMAND_COMPLETE`, stdout `EVIDENCE_TEST_SUITE_PASS` plus CRLF, empty stderr, and independent result/digest verification.

- [ ] **Step 3: Execute hostv6-002 once**

Require exact raw stdout/stderr bytes, exit 0, `COMMAND_COMPLETE`, and complete result/digest.

- [ ] **Step 4: Execute hostv6-003 once**

Require exactly 1,048,576 bytes of `0x4F` stdout and `0x45` stderr, exit 0, no timeout/deadlock, and complete result/digest.

- [ ] **Step 5: Execute hostv6-004 once**

Require compact JSON stdout for the four literal payload values with no newline, empty stderr, exact argv, exit 0, and complete result/digest.

- [ ] **Step 6: Execute hostv6-005 once**

Require `controlled-out`, `controlled-error`, exit 23, `timed_out=false`, `COMMAND_COMPLETE`, and host exit 0.

- [ ] **Step 7: Execute hostv6-006 once**

Require stdout begins `timeout-started`, one killed PID, `timed_out=true`, `COMMAND_TIMEOUT`, complete files, and host exit 0.

- [ ] **Step 8: Execute hostv6-007 once**

Require zero raw streams, PID/exit -1, nonempty Win32 exception fields, `timed_out=false`, `COMMAND_START_FAILURE`, complete files, and host exit 0.

- [ ] **Step 9: Execute hostv6-008 once**

Require exit 0, `COMMAND_COMPLETE`, stdout prefix `EVIDENCE_MACHINE_CLOSURE_PASS|commands=7|machine_files=28`, empty stderr, and its own complete four-file set.

The first mismatch stops all later IDs; never rerun a consumed ID.

---

### Task 5: Close inventory and publish the terminal

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/task-1-report.md`
- Read: 28 human-authored files, 32 machine files, four predecessor inventories, and Git state.
- Modify tracked files: none.

**Interfaces:**
- Consumes: exact observer/static/RED/GREEN/host evidence.
- Produces: one immutable report and first exact NO_GO or success terminal.

- [ ] **Step 1: Run direct pre-report closure for eight IDs**

Run frozen closure directly without `RequireFinalInventory`. Require:

```text
EVIDENCE_HOST_RECOVERY_CLOSURE_PASS|commands=8|machine_files=32|observer=child-exit-proven|absolute_paths=all|brief=canonical
```

It verifies observer RED/GREEN, formal static, recorder RED, source/brief/manifest/raw/result/digest/terminal/inventory/sentinel, four predecessor workspaces, Git cleanliness, and prohibited-action facts. Any mismatch is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`.

- [ ] **Step 2: Create the final report once with apply_patch**

Index design/plan commits/blobs; worktree topology; v5/v4/v3/v2 terminals and sources; observer contract RED/GREEN; production observer identity; formal brief/static; fresh recorder RED; GREEN parser/AST identities; every manifest/argv/environment/timeout; every host result; all 32 machine paths/bytes/hashes/result fields/digests; closure; final inventory; and forbidden-action non-occurrence. Do not decode raw evidence as a substitute for bytes. Never edit after creation.

- [ ] **Step 3: Run final-report closure once**

Run frozen closure with eight IDs and `RequireFinalInventory`. Require report ordinary/non-linked and internally consistent. Exact success is:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

Contradiction or missing evidence is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`; never repair the report.

- [ ] **Step 4: Prove repository and authority closure**

Require HEAD remains this plan commit; tracked/staged/untracked scope clean; ignored additions confined to the fresh workspace; canonical worktree clean; all predecessor workspaces unchanged; no external evidence/identity/commit created; and no Docker/GPU/entry/product/runtime action.

Do not continue to A11 entry. A later approved plan must consume hostv6 PASS identities immutably.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserve v5/v4/v3/v2 and never replay | Global Constraints; Task 1 Step 1; Task 5 Steps 1,4 |
| Real exit-41 observer TDD | Task 1 Steps 2-5 |
| Catch nonzero-to-one mutation | Task 1 Steps 2-3 |
| In-memory raw concurrent capture, no sidecar | Task 1 Step 4; Task 2 Steps 3-5 |
| Freeze production observer before Formal | Task 1 Step 5; Task 2 Steps 2-5 |
| Canonical formal observer/child brief | Task 2 Steps 2-4 |
| One fresh recorder RED | Task 2 Steps 1,5 |
| Exact child exit/stdout/stderr evidence | Task 2 Steps 3-5 |
| Side-effect-free three-export GREEN module | Task 3 Steps 1-3 |
| Closed schema-6 manifests/create-new outputs | Task 3 Steps 1-2; Task 4 Step 1 |
| Unique hostv6 synthetic behavior set | Task 4 Steps 2-9 |
| Independent 32-file closure/report | Task 3 Step 5; Task 4 Step 9; Task 5 Steps 1-3 |
| Exact PASS is not entry authorization | Global Constraints; Task 5 Steps 3-4 |
| No Docker/GPU/runtime/OwnerAuthorizationId | Global Constraints; Task 3 Step 5; Task 5 Steps 1,4 |

## Plan Completion Gate

Before execution, require:

1. this plan is one file in a direct-child commit of `644cfb43f76a745896b4ae40c0b17126f336f145`;
2. author, committer, subject, and only changed path are exact;
3. every design requirement maps to a concrete coverage row;
4. file/function/parameter/schema/property/terminal/ID/machine names are consistent;
5. no unresolved marker, conflict marker, vague error case, or unspecified behavior remains;
6. every PowerShell code block parses under PowerShell 7.6.4 and Windows PowerShell 5.1 where applicable;
7. the exact fixture block is 478 bytes with SHA-256 `55fe8ce2197136aafeb669fc63faae09a2a5643c4c5de48acdaf06bcfbc2c842` when authored LF/UTF-8 no BOM;
8. the contract JSON block is 1,412 bytes with SHA-256 `7e6b3c5e529413ae81540915503cc6aea3c5bc10cc07f337c7ae2dbae04d1583` when authored LF/UTF-8 no BOM;
9. the fresh RED module block is 97 bytes with SHA-256 `ce397973b2befb90d573547d5154a1c3ca5b415c6647464592828fe08d1d878e`;
10. linked/canonical worktrees are clean, v5/v4/v3/v2 inventories and absent machine paths are exact, and fresh workspace is absent; and
11. plan authoring executed no predecessor source, observer contract, formal static, recorder RED, host, Docker, GPU, entry, product, model, or runtime command.
