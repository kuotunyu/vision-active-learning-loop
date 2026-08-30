# Wave 0 A11 Bootstrap Ancestor-Chain Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prove path-string ancestor traversal against real file and directory inputs, obtain one intended fresh recorder RED, and complete the non-recursive synthetic evidence-host proof under fresh `hostv5-*` identities.

**Architecture:** A dedicated behavioral test first catches the preserved `FileInfo.Parent` break in an intentional RED subject, then proves the actual production static source in `AncestorContract` mode. The frozen source enters `Formal` mode once to admit a human-authored canonical recorder-RED command brief. After the intended recorder RED, a side-effect-free three-export module and minimal leaf host capture eight unique children into 32 create-new machine files.

**Tech Stack:** PowerShell 7.6.4; Windows PowerShell 5.1 parser compatibility; .NET `System.IO.Path`, `System.IO.Directory.GetParent`, `FileInfo`, `DirectoryInfo`, `StringComparer`, `JsonDocument`, `Utf8JsonWriter`, `ProcessStartInfo.ArgumentList`, `FileStream`, `Task`, `Stopwatch`, and SHA-256; Git; Markdown; ignored append-only evidence.

## Global Constraints

- Branch is exactly `codex/wave0-model-contract`.
- Approved design commit is exactly `cec959042358b5c650ba655167818656814ddf5f`; this plan commit must be its one-file direct child.
- Design path is `docs/superpowers/specs/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery-design.md`, Git blob `277872347206034ee2ee4bf3aa41d57a315b8a38`.
- Author and committer are exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Preserved plan commits `e91853594324565a8f31129060ac85e507c160a3`, `c579527e91abf5d9bde23a26aedcbc73f362dc5d`, and `890466f71c6730e07774c4568c7b50f70db8ebe2`, their workspaces, sources, terminals, and absent machine paths are immutable.
- The immediate predecessor terminal remains `BOOTSTRAP_ARGV_STATIC_REJECTED / NO_GO`; never execute its static verifier, test, RED module, or command brief.
- The v3 terminal remains `BOOTSTRAP_PATH_STATIC_REJECTED / NO_GO`; never execute its static verifier, test, or RED module.
- The v2 terminal remains `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`; never execute its test or RED module.
- Earlier `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, `CUDA_OBSERVATION_UNPROVABLE / NO_GO`, artifacts, images, inventories, digests, reports, leases, owner identities, and attempts remain immutable.
- The only new execution workspace is `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/`, and it must be absent at entry.
- Create every human-authored ignored file with `apply_patch`; never generate source, command-brief JSON, manifest JSON, or report content with a script or shell redirection.
- Run the ancestor-contract RED subject exactly once, the production static source in `AncestorContract` mode exactly once, the same frozen source in `Formal` mode exactly once, the recorder RED exactly once, and each `hostv5-*` ID exactly once.
- Once a process consumes a source, test, brief, fixture, manifest, command ID, or destination, it is immutable.
- Any unexpected contract RED/GREEN, formal static, recorder RED, host, or closure result closes this plan; do not fix, replace, or retry it.
- Every filesystem ancestor walk stores a canonical path string and calls `[IO.Directory]::GetParent($Cursor)`. No filesystem item returned by `Get-Item` is queried for `.Parent`.
- Every path-bearing process argument is a literal fully qualified Windows path. No receiver supports relative fallback, module-name search, PATH search, or alternate candidate.
- Bootstrap executable sources contain no `JsonSerializer.Serialize` or `ConvertTo-Json`; command-brief reconstruction uses explicit `Utf8JsonWriter` methods with `UnsafeRelaxedJsonEscaping`.
- The evidence host may create only the exact 32 predetermined `machine/hostv5-*` files.
- Do not inspect or execute Docker CLI, Docker Desktop processes, Docker/WSL pipes, builders, images, containers, caches, volumes, GPU, `nvidia-smi`, CUDA, CPU baseline, dependencies, model, A11 launcher, entry child, formal runtime, Wave 1, or product Tasks 2-8.
- Do not create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`.
- Do not modify product code, the seven-file A11 implementation allowlist, external evidence, another repository, a remote, or Git history.
- Do not push, merge, tag, release, amend, rebase, reset, stash, or delete preserved evidence.
- The only success terminal is `EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED`.
- Execution creates ignored evidence only; there is no tracked implementation commit after this plan commit.

## Normative Inputs

- Approved design: commit `cec959042358b5c650ba655167818656814ddf5f`, blob `277872347206034ee2ee4bf3aa41d57a315b8a38`.
- Immediate v4 failed workspace: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/`.
- V4 files:
  - `task-1-bootstrap-command-static-v4.ps1`, 12,532 bytes, SHA-256 `e17d575e0ff8287ea7424c28c08b14bd7625e5603651b07f0283e4a5ced72a68`;
  - `task-1-entry-gate-v4.ps1`, 5,562 bytes, SHA-256 `8e35c0ab663116587448ecb6840bf6c6ecc876c367fe25f4fa86a3e2616b764d`;
  - `task-1-evidence-module-red-v4.psm1`, 97 bytes, SHA-256 `dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb`;
  - `task-1-evidence-tests-v4.ps1`, 8,824 bytes, SHA-256 `aca02e4a213baa1703eec9c0a82a638240de46ecfb77cd0b944c3ab778f7a863`;
  - `task-1-red-command-v4.json`, 1,461 bytes, SHA-256 `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6`.
- V3 failed workspace: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/`, exactly four frozen files and no machine directory:
  - `task-1-bootstrap-path-static-v3.ps1`, 7,521 bytes, SHA-256 `636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9`;
  - `task-1-entry-gate-v3.ps1`, 5,151 bytes, SHA-256 `fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19`;
  - `task-1-evidence-module-red-v3.psm1`, 97 bytes, SHA-256 `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136`;
  - `task-1-evidence-tests-v3.ps1`, 9,012 bytes, SHA-256 `db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c`.
- V2 failed workspace: `.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/`, exactly three frozen files and no machine directory:
  - `task-1-entry-gate.ps1`, 3,541 bytes, SHA-256 `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b`;
  - `task-1-evidence-module-red.psm1`, 103 bytes, SHA-256 `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc`;
  - `task-1-evidence-tests.ps1`, 4,420 bytes, SHA-256 `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65`.
- Frozen PowerShell: `C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe`, 301,368 bytes, SHA-256 `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`, valid Authenticode signature.
- Repository root: `<repo>\.worktrees\wave0-model-contract`.
- Canonical worktree: `<repo>`.

## File and Interface Map

Execution changes no tracked file. Create these ignored human-authored files:

| Path | Responsibility |
|---|---|
| `task-1-entry-gate-v5.ps1` | Audit copy of exact entry/preservation proof. |
| `task-1-ancestor-chain-tests-v5.ps1` | Launch and assert the real RED/GREEN ancestor-contract subjects. |
| `task-1-ancestor-chain-red-v5.ps1` | Intentional `FileInfo.Parent` RED subject. |
| `task-1-bootstrap-command-static-v5.ps1` | Production path-string walker, contract mode, and formal static admission. |
| `task-1-evidence-module-red-v5.psm1` | Fresh recorder RED with no exports. |
| `task-1-evidence-tests-v5.ps1` | Complete recorder RED/GREEN tests using path-string ancestry. |
| `task-1-red-command-v5.json` | Canonical immutable recorder-RED executable/working-directory/argv brief. |
| `task-1-bootstrap-red-brief-v5.md` | Ancestor/static/recorder-RED command and identity index. |
| `task-1-evidence-module-green-v5.psm1` | Manifest validation, raw capture, result publication, and machine verification. |
| `task-1-evidence-host-v5.ps1` | Minimal non-recursive leaf host. |
| `task-1-static-verifier-v5.ps1` | Parser, AST, ancestry, path-flow, import, write-site, and forbidden-command gates. |
| `task-1-synthetic-fixture-v5.ps1` | Deterministic raw, volume, argv, nonzero, and timeout child behavior. |
| `task-1-invalid-executable-v5.exe` | Deterministic ASCII non-executable. |
| `task-1-invalid-manifests-v5.ps1` | Read-only malformed/colliding/path-contract manifest tests. |
| `task-1-preexisting-v5.stdout.bin` | Apply-patch no-clobber sentinel. |
| `task-1-closure-verifier-v5.ps1` | Independent source/contract/brief/machine/result/inventory closure. |
| `task-1-report.md` | Final evidence index and first exact terminal. |

Create eight schema-5 manifests:

| Manifest | Command ID | Planned result |
|---|---|---|
| `task-1-manifest-hostv5-001-unit-green.json` | `hostv5-001-unit-green` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv5-002-raw.json` | `hostv5-002-raw` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv5-003-high-volume.json` | `hostv5-003-high-volume` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv5-004-argv.json` | `hostv5-004-argv` | exit 0, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv5-005-nonzero.json` | `hostv5-005-nonzero` | exit 23, `COMMAND_COMPLETE` |
| `task-1-manifest-hostv5-006-timeout.json` | `hostv5-006-timeout` | `COMMAND_TIMEOUT` |
| `task-1-manifest-hostv5-007-start-failure.json` | `hostv5-007-start-failure` | exit -1, `COMMAND_START_FAILURE` |
| `task-1-manifest-hostv5-008-closure.json` | `hostv5-008-closure` | exit 0, `COMMAND_COMPLETE` |

Each command creates `.stdout.bin`, `.stderr.bin`, `.result.json`, and `.result.sha256`, for exactly 32 machine files.

The production static source accepts exactly:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('AncestorContract','Formal')] [string] $Mode,
    [string] $ContractFilePath,
    [string] $ContractDirectoryPath,
    [string] $ExpectedContractRoot,
    [string] $TestPath,
    [string] $ExpectedTestPath,
    [long] $ExpectedTestByteCount,
    [string] $ExpectedTestSha256,
    [string] $ModulePath,
    [string] $ExpectedModulePath,
    [long] $ExpectedModuleByteCount,
    [string] $ExpectedModuleSha256,
    [string] $WorkspacePath,
    [string] $CommandBriefPath,
    [long] $ExpectedCommandBriefByteCount,
    [string] $ExpectedCommandBriefSha256
)
```

The GREEN recorder module exports exactly `Read-A11EvidenceManifest`, `Invoke-A11RecordedChild`, and `Test-A11MachineEvidence`. The leaf host keeps the exact three-parameter interface from the approved v4 design, with v5 paths only.

---

### Task 1: Prove entry and complete ancestor-contract RED→GREEN

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-entry-gate-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-ancestor-chain-tests-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-ancestor-chain-red-v5.ps1`
- Create after RED: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-bootstrap-command-static-v5.ps1`

**Interfaces:**
- Consumes: exact design/plan lineage, three frozen NO_GO inventories, signed PowerShell identity, and clean linked/canonical worktrees.
- Produces: exact `EXPECTED_ANCESTOR_RED` and `ANCESTOR_CHAIN_CONTRACT_PASS`; freezes production static source before formal use.

- [ ] **Step 1: Run exact read-only entry before workspace creation**

Verify linked-worktree topology, no superproject, branch, HEAD direct parent `cec959042358b5c650ba655167818656814ddf5f`, one changed plan path, author/committer, linked/canonical clean state, empty staging, new workspace absence, design blob, exact v4/v3/v2 file counts/hashes and absent machine directories, four absent `preformal-003` paths, and frozen PowerShell bytes/hash/signature. Emit only:

```powershell
$ExpectedPlan = git rev-parse HEAD
if ($LASTEXITCODE -ne 0 -or $ExpectedPlan -notmatch '^[0-9a-f]{40}$') { throw 'plan commit identity rejected' }
"ANCESTOR_CHAIN_ENTRY_PASS|plan=$ExpectedPlan|workspace=absent|v4=5|v3=4|v2=3|linked=clean|canonical=clean"
```

The audit entry created next freezes the observed literal 40-hex plan commit. Any failure stops without creating the workspace.

- [ ] **Step 2: Create the audit entry and behavioral test before either subject**

Use `apply_patch`. The audit entry is never executed after workspace creation.

The behavioral test accepts:

```powershell
param(
    [Parameter(Mandatory)] [ValidateSet('Red','Green')] [string] $Mode,
    [Parameter(Mandatory)] [string] $SubjectPath,
    [Parameter(Mandatory)] [string] $ExpectedSubjectPath,
    [Parameter(Mandatory)] [long] $ExpectedSubjectByteCount,
    [Parameter(Mandatory)] [string] $ExpectedSubjectSha256,
    [Parameter(Mandatory)] [string] $ContractFilePath,
    [Parameter(Mandatory)] [string] $ContractDirectoryPath,
    [Parameter(Mandatory)] [string] $ExpectedContractRoot
)
```

Before starting a subject, require all inputs fully qualified, canonical subject equality, subject ordinary-file type/bytes/hash, file `FileInfo`, directory `DirectoryInfo`, containment below the expected root, and ordinary ancestor chains using only canonical path strings and `[IO.Directory]::GetParent`. Launch frozen PowerShell with `ProcessStartInfo.ArgumentList`, redirect stdout/stderr, and pass:

```powershell
foreach ($Argument in [string[]] @(
    '-NoProfile', '-NonInteractive', '-File', $ValidatedSubjectPath,
    '-Mode', 'AncestorContract',
    '-ContractFilePath', $ValidatedContractFilePath,
    '-ContractDirectoryPath', $ValidatedContractDirectoryPath,
    '-ExpectedContractRoot', $ValidatedContractRoot
)) {
    [void] $StartInfo.ArgumentList.Add($Argument)
}
```

The mutation caught is explicit: replacing `Directory.GetParent($Cursor)` with `$Item.Parent` makes the real FileInfo case fail.

- [ ] **Step 3: Create and run the intentional ancestor RED exactly once**

Use `apply_patch` to create the RED subject. It validates mode and real file type, then intentionally accesses `$Item.Parent` under strict mode. Catch only `PropertyNotFoundStrict`, emit exactly:

```text
EXPECTED_ANCESTOR_RED|fileinfo_parent_missing
```

and exit 43 with empty stderr. If `.Parent` unexpectedly exists, throw without emitting the terminal.

Run the behavioral test in `Red` mode with the RED subject as both subject and expected path, the test file itself as `ContractFilePath`, the fresh workspace as `ContractDirectoryPath` and `ExpectedContractRoot`, plus observed subject bytes/hash. Require test exit 0 and sole output:

```text
ANCESTOR_CHAIN_TEST_RED_PASS|subject_exit=43|file=FileInfo
```

The test independently requires child exit 43, exact expected stdout plus newline, and empty stderr. Any difference is `ANCESTOR_CHAIN_UNPROVABLE / NO_GO`; do not rerun.

- [ ] **Step 4: Implement the production path-string walker and both static modes**

Only after exact contract RED, create the production static source. Its shared helper is:

```powershell
function Test-A11OrdinaryAncestorChain {
    param([Parameter(Mandatory)] [string] $CanonicalPath)
    $Cursor = [IO.Path]::GetFullPath($CanonicalPath)
    $FirstType = $null
    $LastPath = $null
    $Count = 0
    while ($true) {
        if (Test-Path -LiteralPath $Cursor) {
            $Item = Get-Item -LiteralPath $Cursor -Force
            if ($Item -isnot [IO.FileInfo] -and $Item -isnot [IO.DirectoryInfo]) { throw 'filesystem item type rejected' }
            if ($null -eq $FirstType) { $FirstType = $Item.GetType().Name }
            if (($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0 -or -not [string]::IsNullOrEmpty([string] $Item.LinkType)) { throw 'linked path rejected' }
        }
        $Count++
        if ($Count -gt 128) { throw 'ancestor chain bound exceeded' }
        $LastPath = $Cursor
        $Parent = [IO.Directory]::GetParent($Cursor)
        if ($null -eq $Parent) { break }
        if ([StringComparer]::OrdinalIgnoreCase.Equals($Parent.FullName, $Cursor)) { throw 'ancestor chain stalled' }
        $Cursor = $Parent.FullName
    }
    [pscustomobject][ordered]@{ first_type = $FirstType; last_path = $LastPath; node_count = $Count }
}
```

`AncestorContract` mode requires only contract arguments, calls the helper once for the file and once for the directory, requires first types `FileInfo`/`DirectoryInfo`, drive-root last paths equal, positive bounded node counts, no output files, and emits only:

```text
ANCESTOR_CHAIN_CONTRACT_PASS|file=FileInfo|directory=DirectoryInfo|root=bounded
```

`Formal` mode rejects any contract argument and requires every formal argument. It contains complete absolute path, parser/import, canonical command-brief, executable identity, argv, serializer, predecessor, and no-machine gates from the approved v4 design, but every file/directory/brief/workspace ancestor check calls the helper above. It contains no filesystem-object `.Parent` access.

- [ ] **Step 5: Run the same behavioral test against production static exactly once**

Before execution, parse test, RED subject, and production static with PowerShell 7.6.4 and Windows PowerShell 5.1; require zero errors. AST inspection distinguishes syntax-tree `.Parent` from filesystem code and requires no member named `Parent` whose expression is `$Item`, `$FileItem`, `$DirectoryItem`, or a `Get-Item` pipeline result. Require exact RED/test/source identities and no machine directory.

Run the same test in `Green` mode with production static as subject/expected path and the same real contract file/directory/root. Require test exit 0 and sole output:

```text
ANCESTOR_CHAIN_TEST_GREEN_PASS|subject_exit=0|file=FileInfo|directory=DirectoryInfo
```

The test independently requires exact subject contract PASS plus newline and empty stderr. Any difference is `ANCESTOR_CHAIN_UNPROVABLE / NO_GO`; never edit or rerun. Exact PASS freezes test and production static identities.

---

### Task 2: Admit canonical argv and obtain the recorder RED

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-evidence-module-red-v5.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-evidence-tests-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-red-command-v5.json`
- Create after static PASS: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-bootstrap-red-brief-v5.md`

**Interfaces:**
- Consumes: frozen ancestor RED/GREEN evidence and production static source.
- Produces: one formal static PASS and one immutable recorder RED with exit 41, exact stdout, empty stderr, and zero machine files.

- [ ] **Step 1: Create recorder RED and complete test first**

Create RED module with LF/UTF-8 no BOM:

```powershell
Set-StrictMode -Version Latest

# Intentional hostv5 RED subject: recorder exports do not exist.
```

Require 97 bytes and SHA-256 `efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071`.

Create the complete RED/GREEN test before GREEN source. It uses a fresh path-string helper, validates module absolute/canonical/contained/ordinary/bytes/hash identity, imports only `$ValidatedModulePath`, proves caller `LibraryOnly` and `$PID` unchanged, and requires exact exports. RED emits `EXPECTED_RED|required export set missing` and exits 41. GREEN compares the three sorted names directly without JSON serialization, parses module/host/fixture/invalid-test sources, rejects forbidden AST behavior, invokes invalid-manifest tests, and emits only `EVIDENCE_TEST_SUITE_PASS`.

- [ ] **Step 2: Create and freeze the canonical recorder-RED command brief**

Create `task-1-red-command-v5.json` with `apply_patch` as one compact UTF-8 line plus LF. Its exact content is:

```json
{"schema_version":1,"executable_path":"C:\\Users\\<user>\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\native\\powershell\\pwsh.exe","executable_byte_count":301368,"executable_sha256":"db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f","working_directory":"<repo>\\.worktrees\\wave0-model-contract","argv":["-NoProfile","-NonInteractive","-File","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery\\task-1-evidence-tests-v5.ps1","-Mode","Red","-ModulePath","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery\\task-1-evidence-module-red-v5.psm1","-ExpectedModulePath","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery\\task-1-evidence-module-red-v5.psm1","-ExpectedModuleByteCount","97","-ExpectedModuleSha256","efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071","-WorkspacePath","<repo>\\.worktrees\\wave0-model-contract\\.superpowers\\sdd\\2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery"]}
```

Require 1,437 bytes and SHA-256 `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3`.

- [ ] **Step 3: Perform non-consuming parser/API/static review**

Parse production static, recorder test, and RED module under both parsers. Require no dynamic serializer, shell string, dot-source, redirection, predecessor path, filesystem-object `.Parent`, or unvalidated module import. Recompute all source and brief identities. Use an isolated in-memory `Utf8JsonWriter` microcheck, not the production source, to require canonical writer output equals the 1,437-byte brief. Require no machine directory.

- [ ] **Step 4: Run production static in Formal mode exactly once**

Invoke frozen PowerShell with `-Mode Formal`, literal absolute test/module/workspace/brief paths, observed test bytes/hash, module bytes/hash 97/`efafc826...`, and brief bytes/hash 1437/`8f5001...`. Pass no contract arguments.

Formal mode reuses the already contract-proven helper, validates exact import AST and canonical brief bytes/argv, verifies executable identity/signature, requires four absolute path-bearing argv values, unique switches with only the two module values equal, no predecessor fragments, and no machine directory. Require sole stdout:

```text
BOOTSTRAP_ANCESTOR_STATIC_PASS|ancestor=contract-proven|brief=canonical|absolute_args=4|validated_imports=1|dynamic_serializers=0|predecessor_args=0
```

with exit 0 and empty stderr. Any difference is `BOOTSTRAP_ANCESTOR_STATIC_REJECTED / NO_GO`; preserve and stop without recorder RED.

- [ ] **Step 5: Freeze the bootstrap brief and execute recorder RED once**

After static PASS, create the Markdown brief with exact ancestor RED/GREEN, static contract/formal, executable, source, command-brief, working-directory, environment, argv, expected recorder result, and zero machine identities. Never edit it.

Run the exact executable and argv from the JSON brief once. Require exit 41, stdout `EXPECTED_RED|required export set missing` plus platform newline, empty stderr, zero machine files, and unchanged source/brief identities. Any difference is `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`; never rerun.

---

### Task 3: Implement and statically prove the GREEN recorder/host

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-evidence-module-green-v5.psm1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-evidence-host-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-static-verifier-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-synthetic-fixture-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-invalid-executable-v5.exe`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-invalid-manifests-v5.ps1`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-preexisting-v5.stdout.bin`
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-closure-verifier-v5.ps1`

**Interfaces:**
- Consumes: intended recorder RED and immutable ancestry/bootstrap evidence.
- Produces: side-effect-free three-export module, leaf host, deterministic fixtures, independent closure, and static PASS before any machine child.

- [ ] **Step 1: Implement private path-string and canonical-manifest helpers**

Only after recorder RED, create GREEN module. Module scope permits `Set-StrictMode`, function definitions, and final `Export-ModuleMember` only.

Private path validation rejects null/whitespace, wildcard, provider, URI, UNC, device, ADS, relative, escaping, wrong-kind, linked, wrong-byte, and wrong-hash inputs. Every ancestor chain uses `Directory.GetParent` and never filesystem-object `.Parent`.

Canonical manifest parsing uses strict UTF-8 no BOM, one LF, recursive duplicate rejection, exact property order, schema 5, command regex `^hostv5-[0-9]{3}-[a-z0-9-]+$`, environment order `SystemRoot`, `WINDIR`, `TEMP`, `TMP`, `USERPROFILE`, timeout order `mode`,`milliseconds`, stdin `closed`, child count 1, exact source vectors, and four absent command-derived destinations.

- [ ] **Step 2: Implement public manifest read, raw capture, and machine verification**

Implement exact exports:

```powershell
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

Manifest read validates all absolute source identities before file access and enriches only in memory with manifest path/bytes/hash. Raw capture uses only `ProcessStartInfo.ArgumentList`, cleared allowlisted environment, closed stdin, concurrent `BaseStream.CopyToAsync`, create-new raw streams, one wait or one bounded delay/kill, and create-new canonical result/digest. Start failure yields zero streams, PID/exit -1, exception fields, and `COMMAND_START_FAILURE`; timeout yields `COMMAND_TIMEOUT`; normal child exit, including 23, yields `COMMAND_COMPLETE`.

Independent verification recomputes all four files, canonical result fields/order, raw identities, terminal consistency, and digest bytes and writes nothing.

- [ ] **Step 3: Implement the minimal leaf host**

Use exact parameters `A11HostManifestPath`, `A11HostModulePath`, and `A11HostExpectedWorkspace`. Validate all paths with path-string ancestry, read frozen source identities from the manifest, import only the validated module, require exact exports, and call each once. Never self-capture, recurse, retry, replace a manifest, or choose another path.

Success emits `HOST_CAPTURE_COMPLETE|command_id=...|terminal=...`; missing/partial Layer 2 is `EVIDENCE_HOST_UNPROVABLE / NO_GO`; complete invalid evidence is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`.

- [ ] **Step 4: Create deterministic fixtures and invalid-manifest tests**

Fixture modes are `Raw`, `HighVolume`, `Argv`, `Nonzero`, and `Timeout`. Use literal raw bytes `41 00 E4 B8 AD 0A 5A` and `45 52 52 00 FF`; one-megabyte `0x4F`/`0x45` streams; compact argv JSON; controlled exit 23; and `timeout-started` followed by five seconds.

Create invalid executable as ASCII `A11 V5 INVALID EXECUTABLE` plus LF and sentinel as ASCII `A11-V5-PREEXISTING-SENTINEL` plus LF. Invalid-manifest tests construct in-memory cases for relative/UNC/provider/URI/ADS/escaping/linked/duplicate/extra/missing/reordered/noncanonical/source-vector/collision/preexisting failures, preserve sentinel identity, and emit only `INVALID_MANIFEST_TESTS_PASS`.

- [ ] **Step 5: Create closure/static verifiers and run static gate once**

Closure is complete before any host child and writes nothing. It verifies explicit IDs, ancestry contract evidence, source/brief/manifest/machine/result identities, and pre-report/final inventories.

Static verifier parses all complete sources under both parsers; requires exact exports/host parameters, no filesystem-object `.Parent`, dot-source, dynamic evaluation, `Start-Process`, shell string, redirection, top-level module side effect, protected-variable assignment, predecessor execution, or Docker/GPU/A11/product/Git/network/runtime command. Require validated absolute flows and create-new writes limited to 32 destinations.

Run once and require:

```text
EVIDENCE_HOST_STATIC_PASS|exports=3|ancestor=path-string|absolute_flows=all|dot_source=0|forbidden_assignments=0|forbidden_commands=0
```

No machine path may exist. Any failure is `EVIDENCE_HOST_STATIC_REJECTED / NO_GO`; freeze all GREEN sources after PASS.

---

### Task 4: Author and execute eight unique hostv5 captures

**Files:**
- Create: eight `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-manifest-hostv5-*.json` files.
- Create by host only: 32 `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/machine/hostv5-*` files.
- Modify existing source: none.

**Interfaces:**
- Consumes: frozen GREEN/static PASS and exact source identities.
- Produces: seven behavior captures and one independent closure capture.

- [ ] **Step 1: Freeze identities and create all manifests with apply_patch**

Measure host/module/PowerShell/test/fixture/invalid executable/invalid tests/closure/sentinel/ancestor sources/bootstrap brief and every command source. Manually author compact schema-5 JSON with absolute paths, repository working directory, ordered environment, closed stdin, one child, and four absent unique destinations.

Commands 001-006 and 008 use frozen PowerShell; 007 uses invalid executable. Command 001 runs recorder tests in Green mode. Commands 002-006 run fixture Raw/HighVolume/Argv/Nonzero/Timeout. Command 004 payload is `alpha beta`, empty string, `quote"value`, `中 文`. Command 008 closes IDs 001-007. Timeout is `bounded`/500 only for 006 and `none`/0 otherwise.

- [ ] **Step 2: Execute hostv5-001 once**

Require host exit 0, exact capture terminal, four 001 files, child exit 0/`COMMAND_COMPLETE`, stdout `EVIDENCE_TEST_SUITE_PASS` plus newline, empty stderr, and independent result/digest verification.

- [ ] **Step 3: Execute hostv5-002 once**

Require exact raw stdout/stderr bytes, exit 0, `COMMAND_COMPLETE`, and complete result/digest.

- [ ] **Step 4: Execute hostv5-003 once**

Require exactly 1,048,576 bytes of `0x4F` stdout and `0x45` stderr, exit 0, no timeout/deadlock, and complete result/digest.

- [ ] **Step 5: Execute hostv5-004 once**

Require compact JSON stdout for the four literal payload values with no newline, empty stderr, exact argv, exit 0, and complete result/digest.

- [ ] **Step 6: Execute hostv5-005 once**

Require `controlled-out`, `controlled-error`, exit 23, `timed_out=false`, `COMMAND_COMPLETE`, and host exit 0.

- [ ] **Step 7: Execute hostv5-006 once**

Require stdout begins `timeout-started`, one killed PID, `timed_out=true`, `COMMAND_TIMEOUT`, complete files, and host exit 0.

- [ ] **Step 8: Execute hostv5-007 once**

Require zero raw streams, PID/exit -1, nonempty Win32 exception fields, `timed_out=false`, `COMMAND_START_FAILURE`, complete files, and host exit 0.

- [ ] **Step 9: Execute hostv5-008 once**

Require exit 0, `COMMAND_COMPLETE`, stdout prefix `EVIDENCE_MACHINE_CLOSURE_PASS|commands=7|machine_files=28`, empty stderr, and its own complete four-file set.

The first mismatch stops all later IDs; never rerun a consumed ID.

---

### Task 5: Close inventory and publish the terminal

**Files:**
- Create: `.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/task-1-report.md`
- Read: 25 human-authored files, 32 machine files, three predecessor inventories, and Git state.
- Modify tracked files: none.

**Interfaces:**
- Consumes: exact contract/static/RED/GREEN/host evidence.
- Produces: one immutable report and first exact NO_GO or success terminal.

- [ ] **Step 1: Run direct pre-report closure for eight IDs**

Run frozen closure directly without `RequireFinalInventory`. Require:

```text
EVIDENCE_HOST_RECOVERY_CLOSURE_PASS|commands=8|machine_files=32|ancestor=contract-proven|absolute_paths=all|brief=canonical
```

It verifies all ancestor RED/GREEN, formal static, recorder RED, source, brief, manifest, raw, result, digest, terminal, inventory, sentinel, three predecessor, Git cleanliness, and prohibited-action facts. Any mismatch is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`.

- [ ] **Step 2: Create final report once with apply_patch**

Index design/plan commits/blobs; worktree topology; v4/v3/v2 terminals and sources; ancestor RED/GREEN commands/results; production static identity and formal result; canonical brief; recorder RED; GREEN parser/AST identities; every manifest/argv/environment/timeout; every host result; all 32 machine paths/bytes/hashes/result fields/digests; closure; final inventory; and forbidden-action non-occurrence. Do not decode raw evidence as a substitute for bytes. Never edit after creation.

- [ ] **Step 3: Run final-report closure once**

Run frozen closure with eight IDs and `RequireFinalInventory`. Require report ordinary/non-linked and internally consistent. Exact success is:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

Contradiction or missing evidence is `EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO`; never repair the report.

- [ ] **Step 4: Prove repository and authority closure**

Require HEAD remains this plan commit; tracked/staged/untracked scope clean; ignored additions confined to the fresh workspace; canonical worktree clean; all predecessor workspaces unchanged; no external evidence/identity/commit created; and no Docker/GPU/entry/product/runtime action.

Do not continue to A11 entry. A later approved plan must consume hostv5 PASS identities immutably.

## Spec Coverage Matrix

| Design requirement | Plan task/step |
|---|---|
| Preserve v4/v3/v2 and never rerun | Global Constraints; Task 1 Step 1; Task 5 Steps 1,4 |
| Path-string `Directory.GetParent` ancestry | Task 1 Step 4; Tasks 2-3 |
| Real FileInfo/DirectoryInfo contract RED→GREEN | Task 1 Steps 2-5 |
| Freeze production static before Formal | Task 1 Step 5; Task 2 Steps 3-4 |
| Canonical human-authored command brief | Task 2 Steps 2-4 |
| Intended recorder RED | Task 2 Steps 1,5 |
| Side-effect-free three-export GREEN module | Task 3 Steps 1-3 |
| Non-recursive raw concurrent host | Task 3 Steps 2-3 |
| Closed schema-5 manifests/create-new outputs | Task 3 Steps 1-2; Task 4 Step 1 |
| Unique hostv5 synthetic behavior set | Task 4 Steps 2-9 |
| Independent 32-file closure/report | Task 3 Step 5; Task 4 Step 9; Task 5 Steps 1-3 |
| Exact PASS is not entry authorization | Global Constraints; Task 5 Steps 3-4 |
| No Docker/GPU/runtime/OwnerAuthorizationId | Global Constraints; Task 3 Step 5; Task 5 Steps 1,4 |

## Plan Completion Gate

Before execution, require:

1. this plan is one file in a direct-child commit of `cec959042358b5c650ba655167818656814ddf5f`;
2. author, committer, subject, and only changed path are exact;
3. every design requirement maps to a concrete coverage row;
4. file/function/parameter/schema/property/terminal/ID/machine names are consistent;
5. no unresolved marker, conflict marker, vague error case, or unspecified behavior remains;
6. every PowerShell code block parses under PowerShell 7.6.4 and Windows PowerShell 5.1 where applicable;
7. the recorder command-brief block is exactly 1,437 bytes with SHA-256 `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3` when authored with LF/UTF-8 no BOM;
8. linked/canonical worktrees are clean, v4/v3/v2 inventories and absent machine paths are exact, and fresh workspace is absent; and
9. plan authoring executed no predecessor source, ancestor contract, formal static, recorder RED, host, Docker, GPU, entry, product, model, or runtime command.
