# Wave 0 A11 Bootstrap Argv-Materialization Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `c579527e91abf5d9bde23a26aedcbc73f362dc5d`

## Purpose

Recover the synthetic evidence-host bootstrap from one preserved command-
materialization failure without modifying, rerunning, or interpreting away the
failed attempt. The recovery replaces dynamically serialized bootstrap argv
with one human-authored, identity-frozen JSON command brief and completes the
full non-recursive synthetic host proof under fresh `hostv4-*` identities.

The predecessor absolute-path recovery passed its exact entry gate and authored
its RED subject and complete RED/GREEN test before any GREEN implementation. Its
only formal static-gate invocation did not reach the verifier body because the
outer PowerShell command failed to produce the mandatory `PlannedArgvJson`
argument. The applicable terminal is therefore:

```text
BOOTSTRAP_PATH_STATIC_REJECTED / NO_GO
```

This successor removes runtime JSON construction from the bootstrap boundary.
It does not resume the predecessor plan. It creates a new append-only lineage,
workspace, source set, RED, command brief, command namespace, manifests, and
machine destinations. If every gate passes, its success remains evidence-host
success only:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

## Preserved failures and evidence

The immediately consumed design and plan remain:

| Object | Commit |
|---|---|
| Bootstrap path-resolution design | `c685f0eff5be878d6a15060e0c61f90b770285ed` |
| Bootstrap path-resolution plan | `c579527e91abf5d9bde23a26aedcbc73f362dc5d` |

The consumed workspace is exactly:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery/
```

It contains exactly four immutable files and no `machine/` directory:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `task-1-bootstrap-path-static-v3.ps1` | 7,521 | `636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9` |
| `task-1-entry-gate-v3.ps1` | 5,151 | `fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19` |
| `task-1-evidence-module-red-v3.psm1` | 97 | `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136` |
| `task-1-evidence-tests-v3.ps1` | 9,012 | `db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c` |

The formal outer invocation exited 1. Its first error was:

```text
Cannot find an overload for "Serialize" and the argument count: "1".
```

The frozen PowerShell child was then started without `PlannedArgvJson` and
rejected the missing mandatory parameter. It emitted no static PASS, started no
RED test, imported no RED module, and created no machine destination. The four
files above were unchanged at closure.

The older non-recursive predecessor workspace remains immutable with exactly
its three recorded source identities and no `machine/` directory. Its terminal
remains `EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO`. The still earlier
`EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, `CUDA_OBSERVATION_UNPROVABLE / NO_GO`,
four absent `preformal-003-recorder-red-verify` paths, artifacts, images,
inventories, reports, leases, owner identities, and attempts also remain
immutable.

No predecessor static verifier, RED test, RED module, host, command ID, or
destination may be executed, copied over, repaired, renamed, deleted, or reused.

## Root cause

PowerShell 7.6.4 exposes `System.Text.Json.JsonSerializer.Serialize` overloads
whose usable signatures require at least a value plus type/options metadata.
The outer bootstrap command called:

```powershell
[Text.Json.JsonSerializer]::Serialize([string[]] $Values)
```

PowerShell could not select a one-argument overload. Read-only reflection and an
isolated in-memory diagnostic reproduced the same overload error. A typed
three-argument call succeeded, proving that JSON content and Unicode values were
not the failure.

The defect exists at two boundaries. The outer command used the invalid
one-argument call to create `PlannedArgvJson`, and the frozen static verifier
contained the same call for its round-trip comparison. Supplying the missing
argument alone would therefore only move the failure into the verifier.

Repository examples consistently use `ConvertTo-Json`; no working one-argument
`JsonSerializer.Serialize` precedent exists. The previous design also said to
reject duplicate argv elements while its exact command intentionally repeated
the same module path in the distinct `-ModulePath` and
`-ExpectedModulePath` value positions. The successor removes this ambiguity by
distinguishing duplicate switches from deliberately equal values.

The root cause is an unproven dynamic serialization contract at the Layer 0
command boundary, not path resolution, file absence, PowerShell identity, or
the RED module.

## Decision

Use one manually materialized canonical command brief and no runtime serializer
at the bootstrap boundary.

1. After fresh RED test and module identities are measured, `apply_patch`
   creates one compact UTF-8 JSON command brief containing the frozen executable,
   working directory, and exact ordered RED argv.
2. The brief has no BOM, has exactly one terminal LF, and is frozen by literal
   absolute path, byte count, and lowercase SHA-256 before any formal process.
3. The static verifier receives only scalar absolute paths, byte counts, hashes,
   and the absolute brief path. No JSON string crosses its process-argument
   boundary.
4. The verifier parses the exact brief with `JsonDocument`, validates its closed
   schema and decoded values, rebuilds canonical bytes with explicit
   `Utf8JsonWriter.WriteStartObject`, `WritePropertyName`, `WriteStringValue`,
   `WriteStartArray`, and `WriteEnd*` calls, appends one LF, and requires byte
   equality. It never invokes `JsonSerializer.Serialize` or `ConvertTo-Json`.
5. The formal RED command is a literal transcription of the admitted brief. It
   runs once. Only the intended missing-export result admits GREEN authoring.
6. GREEN/static proof and eight fresh `hostv4-*` synthetic captures follow only
   after the new RED passes.

## Alternatives considered

### A. Human-authored canonical command brief — selected

This removes overload selection, PowerShell pipeline enumeration, quoting, and
Unicode serialization behavior from command construction. A reviewer can audit
the exact bytes and every argv position before execution. The verifier uses only
explicit writer methods with fixed signatures.

### B. Typed three-argument `JsonSerializer.Serialize` — rejected

The typed overload works in the isolated diagnostic and would be a small code
change. It still leaves the formal gate dependent on PowerShell overload binding
and runtime production of the value whose correctness the gate is meant to
prove. It also requires the same correction at two separate components.

### C. `ConvertTo-Json -InputObject ... -Compress` — rejected

This matches repository precedent but retains PowerShell pipeline and array-
enumeration semantics. Its Unicode spelling differs from the explicit JSON
writer and adds a version-sensitive canonicalization choice at the most fragile
boundary. It remains appropriate inside non-bootstrap code only where exact
bytes are independently reconstructed and verified.

## Authority and non-goals

This recovery may:

- create this one-file docs-only design commit and, after written-spec approval,
  one one-file docs-only implementation-plan commit;
- create a new ignored workspace and human-authored test, source, command brief,
  manifest, fixture, verifier, and report files with `apply_patch`;
- run the frozen signed PowerShell executable for read-only entry, parser/static
  checks, one fresh RED, and the planned synthetic evidence-host commands; and
- create exactly 32 predetermined fresh machine files through the approved
  create-new recorder.

It may not:

- modify or execute either preserved failed recovery workspace;
- retry the consumed static gate or either predecessor RED;
- inspect or execute Docker CLI, Docker Desktop processes, pipes, WSL, Hyper-V,
  builders, images, containers, caches, or volumes;
- execute `nvidia-smi`, GPU/CUDA observation, CPU baseline, dependency stage,
  model, A11 launcher, entry child, formal runtime, Wave 1, or Tasks 2-8;
- create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`;
- modify product code, the seven-file A11 implementation allowlist, external
  evidence, another repository, a remote, or Git history; or
- push, merge, tag, release, amend, rebase, reset, stash, or delete preserved
  evidence.

General owner trust does not broaden these boundaries. A later explicit plan is
required before any Docker, GPU, entry, product, or runtime activity.

## Append-only lineage and workspace

This design commit must change only this file and be a direct child of
`c579527e91abf5d9bde23a26aedcbc73f362dc5d`. Author and committer are exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

After written-spec approval, the implementation plan is a one-file direct child
of this design commit with the same identity.

Execution uses only this fresh path:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery/
```

Before creating it, entry proves exact linked-worktree topology, branch, design
and plan lineage, changed paths, blobs, authors, committers, linked/canonical
cleanliness, fresh workspace absence, frozen PowerShell identity, the current
four-file NO_GO inventory and absent machine directory, the older three-file
NO_GO inventory and absent machine directory, and the four still-absent
`preformal-003` paths.

All new human-authored files use `apply_patch`. Once any process consumes a
source, brief, fixture, manifest, command ID, or destination, that object is
immutable. An authoring defect before the formal static invocation requires a
new unused source identity. Any unexpected formal static, RED, host, or closure
result closes this recovery and cannot be corrected or retried.

## Canonical bootstrap command brief

The brief is a compact ordered object with exactly these root properties:

```text
schema_version
executable_path
executable_byte_count
executable_sha256
working_directory
argv
```

`schema_version` is 1. The executable is the frozen signed PowerShell 7.6.4
binary. `working_directory` is the exact linked worktree root. `argv` is an
array of JSON strings in this exact semantic order. The byte-count and digest
rows name values that must be measured and written as literals before the brief
exists; those descriptions are not themselves argv strings:

```text
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-tests-v4.ps1
-Mode
Red
-ModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-module-red-v4.psm1
-ExpectedModulePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery\task-1-evidence-module-red-v4.psm1
-ExpectedModuleByteCount
the literal decimal identity measured before brief authoring
-ExpectedModuleSha256
the literal lowercase SHA-256 measured before brief authoring
-WorkspacePath
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-argv-materialization-recovery
```

Every path is one literal canonical backslash-form fully qualified Windows path.
The brief contains no relative, provider, URI, UNC, device, ADS, environment,
home, wildcard, predecessor, or alternate-candidate path.

Root property names are unique and exact. Every argv element is a string. Switch
tokens are unique and must appear once in their exact positions. Equal values
are forbidden except for the deliberate equality between the values following
`-ModulePath` and `-ExpectedModulePath`. Thus exact path identity is expressed
without contradicting duplicate-switch rejection.

The formal static invocation never creates this JSON in memory. It passes the
brief path and expected identity as ordinary scalar arguments. The verifier
reads exact bytes, rejects BOM/trailing bytes/extra whitespace, rejects duplicate
properties, requires exact order and value types, independently checks all path
and source identities, and reconstructs canonical bytes with `Utf8JsonWriter`.

## Static admission and Layer 0 execution

Before formal static admission, read-only source inspection requires:

- frozen PowerShell and every source path fully qualified and identity-exact;
- test and verifier parse with zero errors under PowerShell 7.6.4 and Windows
  PowerShell 5.1;
- no one-argument or any `JsonSerializer.Serialize` call in executable bootstrap
  sources;
- no `ConvertTo-Json`, shell string, dynamic evaluation, dot-source, redirection,
  or alternate path fallback in executable bootstrap sources;
- exactly one validated `Import-Module -Name $ValidatedModulePath` flow in the
  test; and
- current and older predecessor path fragments absent from executable argv.

The static verifier is invoked once through frozen PowerShell with literal
scalar arguments. Its only PASS is:

```text
BOOTSTRAP_ARGV_STATIC_PASS|brief=canonical|absolute_args=4|validated_imports=1|dynamic_serializers=0|predecessor_args=0
```

Any parser, parameter-binding, path, identity, canonicalization, source-flow,
output, or exit difference publishes:

```text
BOOTSTRAP_ARGV_STATIC_REJECTED / NO_GO
```

After PASS, the formal RED process is started once with the literal executable,
working directory, environment, and argv frozen in the brief. No serializer,
array conversion, command-string reconstruction, path search, fallback, or retry
is permitted between static PASS and process creation.

## TDD bootstrap

The fresh workspace receives new `v4` RED module and complete RED/GREEN test
sources before any GREEN source. They are not copies over either predecessor
identity.

The test independently rejects relative, escaping, linked, wrong-path,
wrong-byte-count, and wrong-hash module input before import. It imports only the
validated absolute module path, proves caller `LibraryOnly` and `$PID` state are
unchanged, and compares the exact three-export contract.

The new RED module has no recorder exports. Its only admitted result is:

```text
exit: 41
stdout: EXPECTED_RED|required export set missing
stderr: empty
machine files: zero
```

Any path, import, parser, output, exit, or inventory difference publishes:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
```

The RED starts once. Only its exact intended result permits GREEN authoring.

## Non-recursive GREEN architecture

After the intended RED, `apply_patch` creates a new side-effect-free `v4` module
and minimal leaf host. The module has no script parameter, dot-source, top-level
process/file/console action, caller-scope mutation, automatic-variable assignment,
dynamic evaluation, shell command string, or predecessor reference.

It exports exactly:

```text
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

Every module, file, manifest, executable, working-directory, source, and output
path passes the same closed absolute/canonical/containment/link/type/bytes/hash
contract before use. `Import-Module`, `Parser.ParseFile`, file APIs, and
`ProcessStartInfo` receive only validated absolute values.

The host imports the module locally, validates one canonical manifest, starts
exactly one permitted child with `ProcessStartInfo.ArgumentList`, concurrently
captures stdout and stderr as raw bytes, and publishes one create-new result and
digest. It never captures itself, recurses, retries, changes a manifest, chooses
another path, or reconstructs missing evidence.

The trust layers remain:

1. frozen Layer 0 executable, command brief, literal invocation, and static PASS;
2. statically constrained Layer 1 host/module; and
3. manifest-authorized Layer 2 child plus four authoritative machine files.

Outer output never substitutes for incomplete Layer 2 evidence.

## Hostv4 manifests and machine evidence

Every GREEN manifest is compact strict UTF-8 JSON without BOM plus one LF. It
uses the previously approved closed schema for command identity, host/module/
executable/source identities, argv, working directory, environment, stdin,
timeout, child count, and four output destinations. Canonical parsing rejects
duplicates, extra/missing/reordered properties, ambiguous paths, colliding
destinations, and noncanonical bytes.

The new command namespace is `hostv4-*`. It cannot reuse a `hostv3-*`,
`hostv2-*`, `preformal-*`, readiness, entry, CUDA, CPU, dependency, owner, or
runtime identity.

Each of eight commands creates exactly four absent files under the fresh
`machine/` directory using create-new/no-clobber semantics:

```text
machine/hostv4-NNN-role.stdout.bin
machine/hostv4-NNN-role.stderr.bin
machine/hostv4-NNN-role.result.json
machine/hostv4-NNN-role.result.sha256
```

The recorder never deletes, truncates, appends, renames over, repairs, or
reconstructs evidence. Result JSON is a closed canonical object and its digest
file is lowercase SHA-256 plus LF.

## Synthetic execution set

After GREEN parser/AST/static PASS, execute these distinct commands once each:

| Command | Proof |
|---|---|
| `hostv4-001-unit-green` | export, scope, AST, path, canonical manifest, invalid input, and no-clobber behavior |
| `hostv4-002-raw` | exact NUL, UTF-8, non-ASCII, invalid-UTF-8, and no-terminal-newline bytes |
| `hostv4-003-high-volume` | concurrent one-megabyte stdout/stderr drain without deadlock |
| `hostv4-004-argv` | spaces, quotes, empty string, and Unicode retain argument boundaries |
| `hostv4-005-nonzero` | controlled exit 23 with complete raw streams and result |
| `hostv4-006-timeout` | one bounded tree kill with partial output and timeout result |
| `hostv4-007-start-failure` | deterministic invalid executable and complete start-exception result |
| `hostv4-008-closure` | independent verification of 001-007 and frozen source/manifest inventory |

Each ID starts at most once. These are independent behavior cases, not retries.
The first unexpected state closes the plan before the next command.

## Error handling and terminals

The first applicable exact terminal is one of:

```text
BOOTSTRAP_ARGV_STATIC_REJECTED / NO_GO
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
EVIDENCE_HOST_STATIC_REJECTED / NO_GO
EVIDENCE_HOST_UNPROVABLE / NO_GO
EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

No exception is converted into PASS. Parameter-binding failure, missing output,
partial output, unexpected console text, wrong exit, timeout, start exception,
digest difference, or inventory mismatch is evidence of the corresponding
NO_GO unless that exact behavior is the planned synthetic case.

Sources and outputs are never edited after observation. Explanation, owner
preference, outer console output, or a newly supplied argument cannot repair a
formal failure. A new design lineage is required after any NO_GO.

## Verification and closure

Before `hostv4-001`, parser and AST verification under PowerShell 7.6.4 and
Windows PowerShell 5.1 requires zero errors and proves:

- exact host parameters and three module exports;
- no dot-source, `Invoke-Expression`, `Start-Process`, shell string,
  redirection, or automatic/constant/read-only variable assignment;
- no module top-level side effect;
- every file/module/parser/process path flows from the absolute validator;
- every write site uses create-new and is limited to the 32 scheduled files;
- no bootstrap dynamic serializer;
- no predecessor source/path/ID scheduled for execution; and
- no Docker, GPU, A11, product, Git mutation, network, or runtime command.

An independent closure verifier is authored and frozen before the first host
child. It writes nothing and recomputes all source, brief, manifest, raw stream,
result, digest, terminal, and inventory facts.

After commands 001-008 pass, one apply-patch report indexes the design/plan
lineage, both preserved NO_GO workspaces, bootstrap brief/static/RED identities,
all GREEN sources and gates, all eight manifests and outer results, all 32
machine files, and explicit non-occurrence of prohibited actions. A final
read-only closure verifies the report and publishes the first exact terminal.

Success proves only the synthetic evidence-host boundary. It does not authorize
Docker readiness, GPU observation, entry, product Tasks 2-8, or runtime.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD and branch equal the required parent and branch;
2. linked and canonical worktrees are clean before authoring;
3. this design path and the fresh execution workspace were absent;
4. the immediate failed workspace has exactly four frozen files and no machine
   directory;
5. the older failed workspace has exactly three frozen files and no machine
   directory;
6. only this design path changed;
7. placeholder, conflict-marker, trailing-whitespace, and Markdown checks pass;
8. root cause, alternatives, exact duplicate semantics, authority, TDD,
   hostv4 identities, terminals, and closure are internally consistent;
9. commit parent, author, committer, subject, and changed path are exact; and
10. authoring executed no predecessor source, formal static gate, RED, host,
    Docker, GPU, entry, product, model, or runtime command.

After this one-file commit, stop for owner review of the written specification.
Invoke `writing-plans` only after explicit written-spec approval.

## Success criteria

This design succeeds when a later implementation proves that bootstrap argv is
an immutable admitted artifact rather than a dynamically serialized transient
value, obtains one intended fresh RED, and completes the full non-recursive
`hostv4-*` synthetic evidence proof without modifying any predecessor evidence
or crossing into A11 runtime authority.
