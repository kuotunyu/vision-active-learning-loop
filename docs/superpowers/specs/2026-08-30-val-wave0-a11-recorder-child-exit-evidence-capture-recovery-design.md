# Wave 0 A11 Recorder Child-Exit Evidence-Capture Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `f022d22f642a9cdd0295ea7b829d918c99f9c101`

## Purpose

Recover the synthetic evidence-host bootstrap from one preserved observation-
boundary failure without modifying or replaying the failed attempt. The new
recovery introduces a statically admitted child-process observer that records
the real `Process.ExitCode`, raw stdout identity, and raw stderr identity inside
one trusted process before returning exit 0 to the outer execution harness.

The predecessor ancestor-chain recovery proved its real `FileInfo` and
`DirectoryInfo` path-string contract, passed its fresh formal static admission,
and executed its recorder RED once. The recorder emitted the exact expected
stdout, but the outer PowerShell command boundary exposed exit 1 instead of the
required child exit 41. The frozen terminal is therefore:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
```

An isolated diagnostic later proved that the nested PowerShell process can set
`$LASTEXITCODE` to 41 while the outer command boundary reports 1. That
diagnostic explains the boundary but cannot retroactively supply evidence for
the consumed recorder attempt. This successor never reuses that attempt.

Complete success remains evidence-host success only:

```text
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

## Preserved predecessor state

The immediately consumed design and plan remain:

| Object | Commit |
|---|---|
| Bootstrap ancestor-chain design | `cec959042358b5c650ba655167818656814ddf5f` |
| Bootstrap ancestor-chain plan | `f022d22f642a9cdd0295ea7b829d918c99f9c101` |

The consumed workspace is exactly:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-bootstrap-ancestor-chain-recovery/
```

It contains exactly eight immutable files and no `machine/` directory:

| Path | Bytes | SHA-256 |
|---|---:|---|
| `task-1-ancestor-chain-red-v5.ps1` | 1,436 | `dfa8f9b572ff31439b8198acd014d53c0efbc408ab50cbce156423293e92b9ac` |
| `task-1-ancestor-chain-tests-v5.ps1` | 8,798 | `07dc9df03102dd64c6d79326c25281fcd143246618777a0c55abfb917623ca09` |
| `task-1-bootstrap-command-static-v5.ps1` | 20,783 | `8ae484662c7f5165b721ad70e3213f1aad43f4b5d238af5282e6ecda1df051f9` |
| `task-1-bootstrap-red-brief-v5.md` | 5,003 | `5d5a95ef800a34f5cfb9a65833367191bde725f6741bb2d79fce0c626644da27` |
| `task-1-entry-gate-v5.ps1` | 6,250 | `2d1b8f10842d6abdc8bea772d258f593b733b2fa7a8af21522c569199fb7dee1` |
| `task-1-evidence-module-red-v5.psm1` | 97 | `efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071` |
| `task-1-evidence-tests-v5.ps1` | 12,339 | `21b59e3e4264706d095c5135a9c1a71fc7ada45dfb2731c02badf0134818c92b` |
| `task-1-red-command-v5.json` | 1,437 | `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3` |

The observed predecessor stages are immutable facts:

| Stage | Observation |
|---|---|
| Entry | `ANCESTOR_CHAIN_ENTRY_PASS` |
| Intentional ancestor RED | child exit 43; exact RED stdout; empty stderr |
| Ancestor GREEN | `ANCESTOR_CHAIN_TEST_GREEN_PASS` |
| Formal static | `BOOTSTRAP_ANCESTOR_STATIC_PASS` |
| Recorder RED outer observation | exit 1; exact `EXPECTED_RED|required export set missing` stdout; empty stderr |
| Machine evidence | absent |

The v4 five-file, v3 four-file, and v2 three-file NO_GO workspaces and
their absent machine directories remain immutable. All still earlier
`EVIDENCE_CAPTURE_UNPROVABLE / NO_GO`, `CUDA_OBSERVATION_UNPROVABLE / NO_GO`,
artifact, image, inventory, digest, report, lease, owner, and attempt evidence
also remains immutable.

No v5 source, brief, subject, command, path, or identity may be executed,
edited, deleted, renamed, copied over, or used as the child in this recovery.

## Root cause and evidence boundary

The recorder test itself contains one deterministic RED branch. When the fresh
RED module exports no recorder functions, it writes:

```text
EXPECTED_RED|required export set missing
```

and requests process exit 41. The predecessor direct invocation nested that
process below an outer PowerShell execution shell. The child nonzero code was
available as `$LASTEXITCODE` inside the outer process, but the tool-facing outer
process normalized its own nonzero completion to 1. The outer result therefore
did not preserve the exact child fact required by the gate.

The failure was not caused by the path-string algorithm, source identity,
canonical JSON, executable signature, recorder RED output, or machine writes.
The missing boundary is one explicit trusted component that reads the child
process object's `ExitCode` before any shell or tool boundary can transform it.

The expected fresh recorder stdout is ASCII plus CRLF:

| Fact | Value |
|---|---|
| Bytes | `42` |
| SHA-256 | `76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0` |
| Stderr bytes | `0` |
| Empty SHA-256 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

These are independent literal expectations, not values computed from the child
implementation during the formal attempt.

## Decision

Use a dedicated statically admitted child-process observer and complete the
full synthetic host proof under fresh `hostv6-*` identities.

1. The observer starts the child directly with
   `System.Diagnostics.ProcessStartInfo.ArgumentList`.
2. It sets `UseShellExecute=false`, redirects both streams, closes stdin, and
   begins concurrent raw stdout/stderr reads before waiting.
3. It calls `WaitForExit` once and reads `Process.ExitCode` from the process
   object while that process object is still alive.
4. It computes raw byte counts and SHA-256 identities in memory. It does not
   decode child output to decide byte identity and creates no sidecar file.
5. It accepts a canonical, human-authored command brief containing the exact
   executable, working directory, ordered argv, and expected raw result.
6. It emits one observer terminal and exits 0 only when every child fact is
   exact. Any difference throws, emits no PASS, and closes the recovery.
7. The outer harness observes only the observer's zero/nonzero success gate;
   the exact child exit is carried in the admitted observer terminal rather
   than delegated to shell exit propagation.
8. After the exact fresh recorder RED observation, fresh GREEN recorder/host
   work and eight `hostv6-*` captures may proceed.

## Alternatives considered

### A. Dedicated process observer — selected

The observer reads the authoritative child process object before returning to
the outer harness. It provides one unit that can be behaviorally tested against
a synthetic exit-41 child, statically inspected for `ExitCode` data flow, and
used without files or retries. Its own exit 0 is preserved by the existing
outer boundary.

### B. Shell wrapper with explicit exit propagation — rejected

A wrapper could execute the child and call `exit $LASTEXITCODE`. That retains a
shell boundary, introduces command-string or wrapper-source interpretation,
and still relies on how another outer PowerShell host maps a nonzero final
status. It does not move evidence collection to the authoritative process
object.

### C. Child-exit sidecar file — rejected

A wrapper or child could write exit 41 to a file. This creates evidence before
the GREEN recorder is admitted and expands the contract to path authorization,
create-new semantics, crash consistency, canonical serialization, digest,
no-clobber, and partial-file recovery. An in-memory observer proves the same
fact with less surface.

## Authority and non-goals

This recovery may:

- create this one-file docs-only design commit and, after written-spec approval,
  one one-file docs-only implementation-plan commit;
- create one fresh ignored workspace with `apply_patch` for every human-
  authored source, brief, fixture, manifest, verifier, and report;
- run the frozen signed PowerShell executable for read-only entry, one observer
  contract RED, one observer contract GREEN, parser/static checks, one formal
  static admission, one fresh recorder RED through the observer, and the
  planned synthetic host commands; and
- create exactly 32 predetermined fresh machine files through the approved
  create-new recorder after all bootstrap gates pass.

It may not:

- modify, execute, delete, rename, replace, retry, or use any v5, v4, v3, or v2
  source, command, destination, or workspace as a fresh subject;
- use the predecessor recorder stdout as proof for the fresh attempt;
- create a sidecar, transcript, or machine file before the recorder RED passes;
- inspect or execute Docker CLI, Docker Desktop processes, pipes, WSL, Hyper-V,
  builders, images, containers, caches, or volumes;
- execute `nvidia-smi`, GPU/CUDA observation, CPU baseline, dependency stage,
  model, A11 launcher, entry child, formal runtime, Wave 1, or product Tasks 2-8;
- create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`;
- modify product code, the seven-file A11 implementation allowlist, external
  evidence, another repository, a remote, or Git history; or
- push, merge, tag, release, amend, rebase, reset, stash, or delete preserved
  evidence.

General owner trust does not broaden these boundaries. Any later Docker, GPU,
entry, product, or runtime activity requires a separately approved plan.

## Append-only lineage and workspace

This design commit must change only this file and be a direct child of:

```text
f022d22f642a9cdd0295ea7b829d918c99f9c101
```

Author and committer are exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

After written-spec approval, the implementation plan is a one-file direct child
of this design commit with the same identity.

Execution uses only this fresh path:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery/
```

Before creating it, entry proves exact worktree topology, branch, design/plan
lineage, changed paths, blobs, author/committer, linked/canonical cleanliness,
fresh workspace absence, frozen PowerShell identity, v5 eight-file inventory
and absent machine directory, v4/v3/v2 inventories and absent machine
directories, and all still-absent older machine paths.

All human-authored files use `apply_patch`. Once a process consumes a source,
test, brief, fixture, manifest, command identity, or destination, it is
immutable. An authoring defect before observer contract RED may use a new
unused identity. Any unexpected observer RED, observer GREEN, formal static,
recorder RED, host, or closure result closes the plan and cannot be corrected
or retried.

## Fresh components and interfaces

The implementation plan must define exact paths, parameters, property orders,
bytes, hashes, and terminals for these focused units:

| Unit | Responsibility |
|---|---|
| Entry audit | Prove lineage, preservation, authority, and fresh absence. |
| Observer behavioral test | Detect nonzero-exit collapse and prove the production observer with a real child. |
| Synthetic exit child | Emit a fixed 42-byte stdout payload, empty stderr, and exit 41. |
| Intentional observer RED | Replace the authoritative child exit with normalized value 1. |
| Production observer | Capture exact child exit and raw streams in memory without side effects. |
| Contract command brief | Authorize only the synthetic exit child and exact expected identities. |
| Fresh recorder RED module/test | Provide a new no-export RED attempt under v6 paths. |
| Formal command brief | Authorize only the fresh recorder RED child and exact expected identities. |
| Formal static verifier | Admit observer source, child source, briefs, argv, identity flow, and no-sidecar behavior. |
| GREEN recorder/host | Validate schema-6 manifests and capture child evidence into create-new files. |
| Static and closure verifiers | Prove sources, manifests, results, inventories, and prohibited-action absence. |

The production observer has two mutually exclusive modes:

```text
Contract
Formal
```

Both modes consume one canonical brief by absolute path and identity. Contract
mode accepts only the synthetic child contract. Formal mode accepts only the
fresh recorder RED contract. Neither mode supports a relative fallback, PATH
lookup, module search, alternate brief, retry, timeout retry, or sidecar path.

## Observer contract TDD

Author the behavioral test, synthetic exit child, contract brief, and
intentional RED observer before the production observer exists. The test names
one mutation: replacing the real `Process.ExitCode` with a normalized boolean
nonzero result.

The synthetic child writes exactly the same 42 stdout bytes expected from the
fresh recorder RED, writes no stderr, and exits 41. It has no filesystem side
effect.

The intentional RED observer starts that synthetic child but deliberately
publishes observed exit 1. The behavioral test must see only:

```text
EXPECTED_CHILD_EXIT_RED|observed=1|expected=41
```

from the subject and then emit only:

```text
CHILD_EXIT_OBSERVER_TEST_RED_PASS|fault=nonzero_collapsed|observed=1|expected=41
```

Any unexpected exit, output, stderr, process count, or path is
`CHILD_EXIT_OBSERVER_UNPROVABLE / NO_GO`. The intentional subject is never
edited or admitted for formal use.

After exact RED, create the production observer. The same immutable behavioral
test runs the observer once in `Contract` mode. The observer must start the
synthetic child exactly once, capture child exit 41, stdout 42 bytes with
SHA-256 `76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0`,
stderr 0 bytes with SHA-256
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`,
create no file, and return exit 0.

The subject contract terminal is:

```text
CHILD_EXIT_OBSERVER_CONTRACT_PASS|child_exit=41|stdout_bytes=42|stderr_bytes=0|sidecars=0
```

The behavioral test independently verifies that terminal and emits only:

```text
CHILD_EXIT_OBSERVER_TEST_GREEN_PASS|child_exit=41|stdout_bytes=42|stderr_bytes=0
```

A mismatch freezes `CHILD_EXIT_OBSERVER_UNPROVABLE / NO_GO`; no source edit or
retry follows. Exact GREEN freezes the production observer, behavioral test,
fixture, and contract-brief identities.

## Canonical formal brief and static admission

Only after observer contract GREEN may the workspace receive a fresh recorder
test, fresh no-export RED module, and formal command brief. No v5 source is
copied or scheduled.

The formal brief is compact strict UTF-8 without BOM plus one LF. Its closed
ordered schema records:

- schema version and formal command identity;
- observer executable, source path, bytes, and SHA-256;
- observer working directory and ordered argv;
- child executable path, bytes, SHA-256, and valid signature;
- child working directory and exact ordered argv;
- child source paths, bytes, and SHA-256;
- expected child exit 41;
- expected stdout bytes/hash and stderr bytes/hash; and
- zero sidecar and zero pre-machine destinations.

The formal static verifier runs once. It uses only path-string ancestor
traversal with `Directory.GetParent`; verifies both PowerShell parsers; proves
the production observer imports or executes only validated absolute values;
requires one `Process.Start`, one wait, concurrent stream reads, one
`Process.ExitCode` data flow, and observer exit 0 only after exact comparison;
and rejects shell strings, redirection, dynamic evaluation, retry loops,
sidecars, machine writes, predecessor arguments, Docker, GPU, A11, product,
Git-mutation, and network commands.

It independently reconstructs canonical brief bytes with explicit
`Utf8JsonWriter` calls and `UnsafeRelaxedJsonEscaping`. It contains no dynamic
serializer.

Its sole PASS is:

```text
RECORDER_CHILD_EXIT_STATIC_PASS|observer=contract-proven|brief=canonical|child_exit=41|exitcode_reads=1|sidecars=0|retries=0
```

Any parser, identity, path, AST, canonicalization, argv, output, or exit
difference publishes:

```text
RECORDER_CHILD_EXIT_STATIC_REJECTED / NO_GO
```

No observer Formal invocation follows static rejection.

## Fresh recorder RED observation

After formal static PASS, create one immutable bootstrap brief that indexes all
contract RED/GREEN, source, executable, formal-static, command-brief, expected
raw, and zero-machine identities.

Then run the production observer once in `Formal` mode. It launches the fresh
recorder RED child exactly once. The child must exit 41, write the exact 42-byte
stdout payload, and write zero stderr bytes. The observer must emit only:

```text
RECORDER_RED_OBSERVER_PASS|child_exit=41|stdout_bytes=42|stdout_sha256=76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0|stderr_bytes=0|stderr_sha256=e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

and return exit 0 with empty stderr. The outer harness exit is evidence only of
observer success; the terminal carries the statically admitted child facts.

An exit, output, hash, process count, source identity, side-effect, or inventory
difference is:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
```

The recorder RED child and observer Formal mode are never retried.

## GREEN recorder and host architecture

Only after exact recorder observer PASS may GREEN source exist. The fresh module
exports exactly:

```text
Read-A11EvidenceManifest
Invoke-A11RecordedChild
Test-A11MachineEvidence
```

The module is side-effect free at import. It validates absolute/canonical/
contained/ordinary path identities, parses a closed canonical schema-6
manifest, starts one child with `ProcessStartInfo.ArgumentList`, concurrently
captures raw stdout/stderr, and publishes create-new result and digest files.
Every ancestor walk stores a canonical path string and uses
`Directory.GetParent`; no filesystem item supplies `.Parent`.

The minimal leaf host imports only the validated absolute module, calls each
export once, never captures itself, never recurses, never retries, and never
substitutes outer output for incomplete Layer 2 evidence.

The trust layers are:

1. frozen signed PowerShell, contract-proven observer, canonical formal brief,
   and formal static PASS;
2. statically constrained GREEN host/module; and
3. manifest-authorized child plus four authoritative machine files.

## Hostv6 manifests and synthetic set

Every GREEN manifest is compact strict UTF-8 without BOM plus one LF. It uses a
closed ordered schema for command, host/module/executable/source identities,
argv, working directory, environment, stdin, timeout, child count, and four
output destinations. It rejects duplicates, extra/missing/reordered
properties, ambiguous paths, collisions, noncanonical bytes, wrong source
vectors, and preexisting destinations.

The new namespace is `hostv6-*`. It cannot reuse `hostv5-*`, `hostv4-*`,
`hostv3-*`, `hostv2-*`, `preformal-*`, readiness, entry, CUDA, CPU,
dependency, owner, or runtime identities.

Execute exactly these distinct cases once each:

| Command | Proof |
|---|---|
| `hostv6-001-unit-green` | export, scope, AST, observer, path, manifest, invalid-input, and no-clobber behavior |
| `hostv6-002-raw` | exact NUL, UTF-8, non-ASCII, invalid-UTF-8, and no-terminal-newline bytes |
| `hostv6-003-high-volume` | concurrent one-megabyte stdout/stderr drain |
| `hostv6-004-argv` | spaces, quotes, empty string, and Unicode argument boundaries |
| `hostv6-005-nonzero` | exit 23 with complete streams/result |
| `hostv6-006-timeout` | one bounded tree kill with partial output |
| `hostv6-007-start-failure` | deterministic invalid executable and complete exception result |
| `hostv6-008-closure` | independent verification of 001-007 and frozen inventory |

Each command creates exactly `.stdout.bin`, `.stderr.bin`, `.result.json`, and
`.result.sha256` under the fresh `machine/` directory. Eight commands create
exactly 32 files. Each ID starts at most once; the first unexpected state stops
all later IDs.

## Static verification, terminals, and closure

Before `hostv6-001`, parse all complete sources under PowerShell 7.6.4 and
Windows PowerShell 5.1. Static verification requires:

- exact host parameters and three module exports;
- one proven observer exit-code data path and path-string ancestry;
- no filesystem-object `.Parent`, dot-source, dynamic evaluation,
  `Start-Process`, shell string, redirection, top-level module side effect, or
  protected-variable assignment;
- validated absolute flows into module/file/parser/process APIs;
- create-new write sites limited to 32 scheduled destinations;
- no predecessor source/path/ID scheduled for execution; and
- no Docker, GPU, A11, product, Git mutation, network, or runtime command.

The first applicable terminal is one of:

```text
CHILD_EXIT_OBSERVER_UNPROVABLE / NO_GO
RECORDER_CHILD_EXIT_STATIC_REJECTED / NO_GO
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
EVIDENCE_HOST_STATIC_REJECTED / NO_GO
EVIDENCE_HOST_UNPROVABLE / NO_GO
EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

No exception is converted to PASS. Missing/partial output, unexpected console
text, wrong exit, timeout, start exception, digest difference, or inventory
mismatch is NO_GO unless it is the exact planned synthetic behavior. Sources
and outputs are never edited after observation.

An independent closure verifier is authored and frozen before the first host
child. It recomputes all source, observer-contract, formal-brief, static,
manifest, raw stream, result, digest, terminal, and inventory facts and writes
nothing.

After commands 001-008 pass, one apply-patch report indexes lineage, all four
preserved bootstrap NO_GO workspaces, observer RED/GREEN evidence, formal
brief/static, fresh recorder RED, GREEN sources, eight manifests, all 32
machine files, and prohibited-action non-occurrence. Final read-only closure
verifies the report and publishes the first exact success terminal.

Success does not authorize Docker readiness, GPU observation, A11 entry,
product Tasks 2-8, or runtime.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD and branch equal the required parent and branch;
2. linked and canonical worktrees were clean before authoring;
3. this design path and fresh execution workspace were absent;
4. v5 contains exactly eight frozen files and no machine directory;
5. v4 contains exactly five frozen files and no machine directory;
6. v3 contains exactly four frozen files and no machine directory;
7. v2 contains exactly three frozen files and no machine directory;
8. only this design path changed;
9. placeholder, conflict-marker, trailing-whitespace, and Markdown checks pass;
10. root cause, alternatives, observer contract, TDD, formal evidence, hostv6
    IDs, terminals, authority, and closure are internally consistent;
11. expected recorder stdout is exactly 42 bytes with SHA-256
    `76f2f0c8c66f58a392e6dec102d0c674a50a06d9af4c725b32f4b7e2020de2b0`;
12. commit parent, author, committer, subject, and changed path are exact; and
13. authoring executed no predecessor source, observer contract, formal static,
    recorder RED, host, Docker, GPU, entry, product, model, or runtime command.

After this one-file commit, stop for owner review of the written specification.
Invoke `writing-plans` only after explicit written-spec approval.

## Success criteria

This design succeeds when a later implementation proves, against a real
synthetic exit-41 child, that a statically admitted observer preserves the
authoritative child exit and raw stream identities before the outer harness
boundary, then completes the full non-recursive `hostv6-*` synthetic evidence
proof without changing predecessor evidence or crossing into A11 runtime
authority.
