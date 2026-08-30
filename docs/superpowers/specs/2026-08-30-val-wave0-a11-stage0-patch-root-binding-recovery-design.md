# Wave 0 A11 Stage 0 Patch-Root-Binding Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `03bc963ac69e26da1d338a448481c82f35f66f1d`

**Required parent plan blob:** `17f42b6019dd6575fb98e3501ed55cce89afa06c`

## Purpose

Recover the read-only A11 entry-verifier milestone from one preserved v9
materialization-path failure. The predecessor plan passed its complete read-only
entry gate, but its first `apply_patch` operation resolved repository-relative
patch headers against the shared Codex workspace root instead of the linked
worktree. The two exact seed files were therefore created outside the repository
and the plan closed before any controller or child process ran.

This successor introduces a fresh v10 lineage and proves the patch root with one
non-executable, append-only marker before any executable source is materialized.
Only an exact root-binding PASS may admit fresh v10 Stage 0, parser-identity,
scalar-identity, inventory, static, formal, report, and closure work.

The owner approved the architecture on 2026-08-30 with the exact statement:

```text
核准此 A11 Stage 0 patch-root-binding recovery 設計（方案 A）。
```

The final success boundary remains:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

## Preserved v9 incident

The approved predecessor lineage is:

| Object | Commit | Blob |
|---|---|---|
| Stage 0 Unicode transport design | `c71d824d3d249e92fe92dfc872aa53ba3d53facd` | `e3785d6bb305cf57b05114bdf9cd17a884e14491` |
| Stage 0 Unicode transport plan | `03bc963ac69e26da1d338a448481c82f35f66f1d` | `17f42b6019dd6575fb98e3501ed55cce89afa06c` |

The v9 plan admitted:

- exact branch `codex/wave0-model-contract`;
- exact linked-worktree topology and non-submodule state;
- exact direct-child commit/blob lineage;
- clean linked and canonical worktrees and empty staging;
- exact four-file v7 preservation;
- absent v8 and consumed-v6 runtime namespaces;
- exact PowerShell 7.6.4 Core and Windows PowerShell 5.1 Desktop executable
  identities;
- exact two role-specific `Microsoft.PowerShell.Security` manifests and nested
  DLLs, signatures, signer identities, versions, link policies, parent chains,
  and command provenance; and
- both complete seed blocks parsing with zero errors under the exact PowerShell
  7 and explicit Windows PowerShell 5.1 parsers.

The seed source identities were:

| File | Bytes | SHA-256 |
|---|---:|---|
| `task-1-stage0-transport-controller-v9.ps1` | 17,994 | `795c64dd6e729365b5360480de6e60651b82ca7c2f3a7907df86320da02d77ff` |
| `task-1-stage0-v9.ps1` | 20,258 | `34e504d1c012ec77bdeed578703f90008278ef2bc2f8b0fadfacc1b9d774f4f3` |

One `apply_patch` call was then constructed with headers relative to the
repository:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery/task-1-stage0-transport-controller-v9.ps1
.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery/task-1-stage0-v9.ps1
```

The patch API resolved those headers against its actual authority root:

```text
<workspace>
```

The resulting immutable external directory is:

```text
<workspace>\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery
```

It contains exactly the two source identities above and no directory child. The
intended repository directory remains absent:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery
```

The mismatch was detected by the first post-materialization identity check.
No executable source was invoked. In particular:

- controller invocations: `0`;
- Stage 0 child starts: `0`;
- parser RED/GREEN invocations: `0`;
- dual-parser starts: `0`;
- scalar RED/GREEN invocations: `0`;
- static/formal/closure invocations: `0`;
- Docker/GPU/A11 runtime/model/network actions: `0`; and
- repository mutations after the approved plan commit: `0`.

HEAD remained `03bc963ac69e26da1d338a448481c82f35f66f1d`;
linked and canonical worktrees and staging remained clean. The exact terminal is
permanently:

```text
ENTRYV9_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO
```

The two external files are evidence of a failed materialization procedure. They
are not v9 runtime success evidence and may never be moved, copied into the
repository, renamed, edited, deleted, executed, or reinterpreted as a PASS.

## Root cause

The predecessor plan bound runtime paths but did not bind the path-resolution
semantics of the authoring tool that creates those runtime files.

`exec_command` accepts an explicit `workdir`, while `apply_patch` has no
per-call working-directory argument and resolves relative headers against the
Codex task's shared filesystem root. Nesting both tools in the same orchestration
call did not make their roots identical. The predecessor materializer therefore
combined:

```text
assumed patch root: linked worktree
actual patch root:  <workspace>
patch header:       .superpowers/sdd/...
```

Because `<workspace>\.superpowers` was a valid creatable path, the patch
operation succeeded rather than reporting a missing directory. Its opaque
completion result did not echo the canonical targets. The following independent
filesystem check found the intended namespace absent and correctly stopped the
plan.

The defect is not in the seed bytes, encoding, PowerShell parsers, Unicode path,
Git worktree, executables, Security providers, preserved evidence, or Stage 0
controller. It is an unbound authoring-tool root at the patch-header-to-file
boundary.

A longer runtime path inside a source file cannot correct this boundary. The
recovery must first prove where `apply_patch` itself writes.

## Decision

Use a non-executable root-binding marker and a fresh full v10 recovery.

1. Preserve the external v9 directory, intended-v9 absence, and exact v9 NO_GO.
2. Commit this docs-only design and a separately approved docs-only
   implementation plan before creating a v10 runtime object.
3. Use one fresh ignored v10 namespace.
4. The first and only initial materialization is a text marker whose patch header
   is expressed relative to the known shared authority root, not relative to the
   repository.
5. Verify the marker at its exact canonical repository target, its exact bytes
   and digest, the one-file v10 inventory, all defined shadow-path absences, and
   unchanged v9 evidence.
6. Treat that first materialization as single-use. Any uncertainty or wrong
   target closes v10 without another marker attempt.
7. Only exact root-binding PASS permits fresh v10 executable source
   materialization using the same frozen header prefix.
8. Every later patch operation is independently followed by canonical target,
   identity, count, and shadow-path checks before its file can be consumed.
9. Fresh v10 Stage 0 and all downstream phases retain the approved
   Unicode-file, structured-argv, parser, provider, scalar, inventory, static,
   formal, and closure architecture.
10. Stop at the entry-verifier milestone. Child-exit recovery and every model
    runtime remain unauthorized.

This design does not repair v9. It creates a new proof boundary before any v10
source can exist.

## Alternatives considered

### A. Shared-root-relative patch header plus root-binding marker — selected

This matches the observed patch API contract, proves the actual target before
executable authoring, leaves a permanent audit object, and requires no shell
writer or new task. The marker isolates authoring-root proof from runtime-source
identity.

### B. Move execution into a new task rooted at the linked worktree — rejected

A different task might change the implicit patch root, but that would substitute
a new environmental assumption for the failed one. It would also split the
append-only evidence history across tasks without proving the patch API's
canonical target.

### C. Write files with an absolute shell path — rejected

PowerShell, Python, redirection, `Set-Content`, or another shell writer could
name the canonical target directly, but would violate the repository's
`apply_patch`-only authoring rule and the global file-edit constraint. It would
also create a new unreviewed byte-serialization boundary.

### D. Move or copy the exact external v9 seeds into the repository — rejected

Their identities are consumed evidence under a closed v9 terminal. Relocation
would erase the proof of the failure, retroactively repair a frozen attempt, and
violate both append-only and fresh-source requirements.

## Authority and non-goals

This design authorizes only:

- one one-file docs-only design commit;
- after owner approval of this written specification, one one-file docs-only
  implementation-plan commit;
- after separate plan approval, one single-use v10 root-binding marker
  materialization and its read-only verification;
- after exact marker PASS, fresh v10 read-only/CPU-only source
  materialization, Stage 0, parser/scalar TDD, dual-parser, inventory, static,
  formal, report, and closure phases described here; and
- read-only verification of approved repository, Git, runtime, provider,
  signature, and preserved-evidence identities.

It does not authorize:

- editing, deleting, moving, renaming, copying, invoking, importing, parsing as
  executable input, or completing either external v9 file;
- creating anything in the intended v9 namespace;
- rerunning any v8 or v9 Stage 0, controller, parser, scalar, formal, or closure
  source;
- using a shell writer, generated source, temporary file, repair file, fallback
  path, alternate header, retry, or cleanup operation;
- Docker, Docker Desktop, WSL, Hyper-V, image/container/cache/volume inspection,
  GPU, `nvidia-smi`, CUDA, WDDM, A11 launcher/runtime, artifact campaign, model
  initialization, calibration, validation, RDD, Wave 1, product work, or network
  access;
- requesting, creating, consuming, inferring, incrementing, reserving, or
  synthesizing an `OwnerAuthorizationId`;
- modifying another repository or the canonical checkout; or
- remote creation, push, merge, rebase, reset, stash, amend, squash,
  cherry-pick, tag, release, or publication.

General owner trust does not widen these boundaries. A new external authority,
destructive action, or expanded runtime scope requires separate approval.

## Append-only lineage

This design changes exactly:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery-design.md
```

It must be a direct child of:

```text
03bc963ac69e26da1d338a448481c82f35f66f1d
```

Its exact author and committer are:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Its exact subject is:

```text
docs: design A11 Stage 0 patch root binding recovery
```

After written-spec approval, the implementation plan may add exactly:

```text
docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery.md
```

The plan must be a one-file direct child of this design commit with the same
author and committer. It must pin this design commit and blob, predecessor
lineage, external v9 identities, patch-root contract, marker schema, every v10
executable source block and identity, phase interface, file count, and terminal
before execution.

The plan commit does not itself authorize execution. Execution requires a
separate owner approval and an explicit supported execution mode.

## Fresh v10 namespace

The canonical ignored workspace is:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery
```

Its repository-relative spelling is:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/
```

It must be absent when the implementation plan is committed and immediately
before marker materialization.

The first admitted inventory is exactly one ordinary file:

```text
task-0-patch-root-binding-v10.txt
```

After exact marker PASS, the initial executable seed inventory becomes exactly
three files:

```text
task-0-patch-root-binding-v10.txt
task-1-stage0-transport-controller-v10.ps1
task-1-stage0-v10.ps1
```

The final successful workspace contains exactly 16 human-authored files: the
marker plus fresh v10 counterparts of the predecessor plan's 15-file map. It
never contains `machine/`, cache, bytecode, temporary, transcript, sidecar,
result, digest, alternate manifest, repair, or copied predecessor files.

Once a v10 file is first materialized, its path and bytes are immutable. A
wrong path, encoding, byte count, digest, stream, link, property order, static
property, inventory count, or shadow-path observation freezes the v10 namespace
and stops.

## Patch-authority contract

The patch authority root is exactly:

```text
<workspace>
```

Every v10 `apply_patch` target begins with this exact forward-slash prefix:

```text
CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/
```

The first complete patch header is exactly:

```text
CC_github部隊/vision-active-learning-loop/.worktrees/wave0-model-contract/.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery/task-0-patch-root-binding-v10.txt
```

Interpreted against the approved authority root, it maps to exactly:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery\task-0-patch-root-binding-v10.txt
```

No patch header begins with `.superpowers`, `docs`, a drive letter, slash,
backslash, `..`, environment-variable token, home token, URI, provider prefix,
UNC prefix, device prefix, or alternate repository spelling.

The implementation plan must freeze the complete patch header for every
materialized file. Orchestration may construct an `apply_patch` payload in
memory, but may not change, shorten, infer, normalize, or prepend the target
after the plan gate.

## Root-binding marker

The marker is non-executable strict UTF-8 text without BOM, CR, blank terminal
line, or alternate data stream. It ends with exactly one LF.

Its closed ordered fields are:

```text
schema_version
binding_id
source_plan_commit
source_design_commit
source_design_blob
patch_authority_root
patch_header
repository_root
workspace_path
canonical_target
failed_v9_terminal
```

Required values and types are frozen by the implementation plan. The
`source_plan_commit` is the exact 40-hex HEAD observed and frozen by the
read-only execution entry gate. All other values are literal plan-pinned
strings; `schema_version` is the exact decimal integer `1`; `binding_id` is
`entryv10-patch-root-binding-001`.

The marker is created by one `apply_patch` call. That call is single-use whether
the API reports success, failure, timeout, disconnect, empty output, or an
uncertain result.

After the call, a read-only verifier requires:

- exact canonical marker presence, ordinary-file type, containment, parent
  chain, bytes, SHA-256, stream inventory, strict UTF-8 round trip, field order,
  and values;
- the v10 workspace contains exactly the marker and no directory child;
- the external v9 directory and both file identities remain exact;
- the intended v9 namespace remains absent;
- all plan-defined v10 shadow candidates are absent;
- linked and canonical worktrees remain clean and staging empty;
- HEAD and branch remain exact; and
- zero process start, source import, source execution, Docker/GPU/runtime,
  network, repository, or external mutation occurred.

The sole successful marker terminal is:

```text
ENTRYV10_PATCH_ROOT_PASS|authority=workspace|marker_files=1|shadow_paths=0|writes=1|retries=0
```

Any missing target, wrong target, unexpected duplicate, identity mismatch,
uncertain tool result, unexpected child, or side effect is:

```text
ENTRYV10_PATCH_ROOT_UNPROVABLE / NO_GO
```

The marker and every located unintended object are preserved. The marker call
is never retried with a changed header, alternate root, absolute path, shell
writer, copy, or move.

## Post-marker materialization

Exact marker PASS authorizes only the next plan-defined `apply_patch` operation.
Every later patch header uses the identical frozen prefix and changes only its
plan-pinned leaf name.

After each patch operation and before any consumer, verification requires:

1. every new canonical target exists exactly once;
2. every target path, containment relation, type, parent chain, stream,
   encoding, byte count, and SHA-256 is exact;
3. the whole v10 inventory contains the exact permitted files and nothing else;
4. every defined shadow candidate remains absent;
5. the marker and all earlier v10 files remain byte-identical;
6. external v9 evidence remains exact and intended v9 remains absent;
7. linked/canonical Git state remains clean; and
8. no unapproved process or external action occurred.

A mismatch freezes every existing v10 object. No later phase may repair,
replace, delete, regenerate, or consume the mismatched source.

## Fresh v10 Stage 0

The v10 controller and Stage 0 are newly authored source identities. They are
not copies or renamed versions of either external v9 file. They retain the
approved semantic contract while adding:

- exact patch-marker identity and PASS;
- preserved v9 plan/design lineage, external file identities, intended
  namespace absence, terminal, and zero-execution facts;
- exact v10 design/plan lineage and fresh file map;
- v10-only role names, terminals, source names, and inventory fields; and
- independent verification that no v9 path is imported, invoked, or used as a
  source target.

Before controller invocation, both complete source blocks must parse without
execution under exact PowerShell 7.6.4 Core and explicit Windows PowerShell 5.1
Desktop parser APIs. Static verification retains the approved single-start,
structured `ArgumentList`, Unicode `-File`, empty/closed stdin, concurrent raw
stream capture, timeout-only kill, no retry/fallback, and no dynamic execution
requirements.

The controller is invoked once through a plan-pinned literal relative path from
the linked repository. It starts at most one exact v10 Stage 0 child.

The exact Stage 0 PASS family is:

```text
ENTRYV10_STAGE0_PASS|v9=preserved_no_go|v8=preserved_no_go|patch_root=bound|seed_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
```

The exact transport PASS family is:

```text
ENTRYV10_UNICODE_TRANSPORT_PASS|source=utf8-file|argv=unicode|stdin_bytes=0|starts=1|retries=0
```

Controller stderr is empty and parent-visible stdout contains exactly those two
LF-terminated ASCII lines in that order.

## Fresh v10 downstream recovery

Only exact marker, Stage 0, and transport PASS may admit downstream work.

The implementation plan must freshly author and identity-freeze:

- parser-identity behavioral test;
- intentional parser RED module;
- parser GREEN module;
- self-attesting parser worker;
- exact dual-parser controller;
- scalar-identity behavioral test;
- intentional scalar RED module;
- scalar GREEN module;
- canonical preserved inventory;
- formal entry verifier;
- static verifier;
- independent closure verifier; and
- final report.

Every filename, function, role, phase, manifest, terminal, and process identity
uses v10. No v9 executable block may be materialized byte-for-byte, imported,
dot-sourced, invoked, or relabeled.

Parser identity and scalar identity each follow fresh RED-before-GREEN TDD.
Every RED, GREEN, dual-parser phase, static gate, formal entry, pre-report
closure, and final closure is single-use with exact exit/stdout/stderr and
zero unauthorized side effects.

## Canonical preserved inventory

The v10 inventory explicitly represents three failed predecessors:

1. v9 materialization-root failure, including both exact external file records,
   external directory, intended-directory absence, zero process counts, and no
   retroactive PASS;
2. v8 Unicode stdin-transport failure and absent v8 runtime namespace; and
3. v7 contradictory-result procedure failure and exact four-file workspace.

It also carries the approved 20 v2-v5 preserved records, two parser executable
identities, two Security-provider records containing four provider files, and
all required absence paths.

The root property order is closed and the implementation plan must freeze it.
All byte counts use `System.Int64`, digests and paths are scalar strings, and
incident semantics are exact Booleans. The two external v9 files are counted
separately from the 24 v2-v7 preserved files; no report may disguise their
external location by rewriting them as repository-relative paths.

Canonical serialization uses strict UTF-8 without BOM and exactly one final LF.
A runtime serializer may validate but may not generate or repair the
human-authored inventory.

## TDD and verification

The preserved v9 wrong-path materialization is the observed RED for the
patch-root defect. It is never recreated merely to demonstrate the failure.

The root-binding GREEN is the exact marker at its canonical target plus exact
shadow absence. File existence alone is insufficient; the verifier binds the
marker's content, header, authority root, repository root, plan/design lineage,
inventory, and v9 preservation.

After root binding:

- all executable source blocks are extracted from the committed plan and
  identity-checked before materialization;
- PowerShell sources parse under both approved parser APIs without execution;
- parser-role and scalar comparators follow fresh behavioral RED/GREEN cycles;
- each dual-parser phase starts exactly the two approved executable identities
  with provider-attested results;
- static verification rejects unbound patch headers, predecessor execution,
  copy/move/delete/repair paths, dynamic execution, shell writers, extra starts,
  forbidden commands, and inconsistent inventories;
- formal verification independently recomputes typed ordinal identity records;
  and
- closure independently proves every source, preserved file, absence, terminal,
  Git fact, and prohibited-action non-occurrence.

Before any success claim, final verification requires:

- exact design and plan commits, blobs, changed paths, parentage, author,
  committer, and subjects;
- exact 16-file v10 inventory and immutable marker;
- exact external v9 two-file inventory and intended-v9 absence;
- exact v8/v7 preservation and 20 older records;
- exact runtime/provider identities, signatures, provenance, link policies, and
  parent chains;
- clean linked and canonical worktrees and empty staging;
- zero cache, bytecode, temporary, machine, repair, result, sidecar, or
  unapproved object;
- zero Docker/GPU/A11/model/owner/network action; and
- one immutable report followed by independent final closure.

## Error handling and consumption

All gates are fail-closed.

- A pre-marker entry mismatch stops without creating v10.
- The marker `apply_patch` call is consumed when invoked, not when its canonical
  target is later found.
- Any marker uncertainty closes as
  `ENTRYV10_PATCH_ROOT_UNPROVABLE / NO_GO`.
- Any post-marker materialization mismatch closes as
  `ENTRYV10_MATERIALIZATION_UNPROVABLE / NO_GO`.
- A controller uncertainty before Stage 0 start closes as
  `ENTRYV10_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO`.
- A Stage 0 start followed by timeout, disconnect, output, identity, or
  side-effect difference closes as `ENTRYV10_STAGE0_UNPROVABLE / NO_GO`.
- Any downstream difference closes at its plan-defined v10 phase terminal.

No NO_GO authorizes retry, alternate patch header, alternate root, cleanup,
copy, move, source edit, changed expectation, fallback executable, or tuning to
the result. Existing objects remain evidence for a later separately approved
design.

## Report and continuation

After exact formal and pre-report closure, the final report is created once with
the frozen shared-root-relative patch prefix. It records:

- all design/plan lineage and Git identities;
- exact v9 patch request, actual root, external paths, file identities,
  intended-path absence, zero execution, and NO_GO;
- marker header, authority root, canonical mapping, bytes, digest, inventory,
  shadow checks, and PASS;
- all v10 source identities and TDD/dual-parser/static/formal terminals;
- canonical preserved inventory and all typed comparisons;
- exact 16-file final workspace;
- every prohibited action's non-occurrence; and
- the first exact final terminal.

Independent final closure reads but writes nothing. Success emits exactly:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Success authorizes no v7-v9 resumption, child-exit recovery, Docker/GPU
observation, A11 runtime, model work, Wave 1, push, merge, or release. A later
separately approved design and plan must consume the final v10 evidence
immutably.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD is exactly `03bc963ac69e26da1d338a448481c82f35f66f1d`;
2. branch is exactly `codex/wave0-model-contract`;
3. linked and canonical worktrees were clean and staging empty before authoring;
4. this design and the fresh v10 namespace were absent;
5. the external v9 directory contains exactly the two frozen files;
6. the intended v9 namespace remains absent;
7. only this design path changed;
8. document encoding is strict UTF-8 without BOM, LF-only, with one final LF;
9. placeholder, conflict-marker, whitespace, Markdown, scope, authority,
   retry-semantics, path-mapping, count, and terminal checks pass;
10. the commit parent, changed path, author, committer, and subject are exact;
    and
11. design authoring executed no marker, v9 source, Stage 0, parser, Docker, GPU,
    A11, product, model, network, or external runtime command.

The design commit does not authorize plan authoring until the owner approves
this written specification. The future plan commit does not authorize execution
until the owner separately approves it and chooses Inline Execution or another
explicitly supported mode.

## Success criteria

This design is satisfied only when a later approved implementation:

1. preserves the v9 terminal, external files, and intended-path absence exactly;
2. proves the shared-root-relative patch mapping with one immutable marker and
   zero shadow paths;
3. creates only fresh v10 executable identities after marker PASS;
4. starts exactly one v10 Stage 0 through the approved UTF-8 file and structured
   Unicode argv contract;
5. completes fresh parser/scalar TDD, dual-parser, inventory, static, formal,
   report, and closure phases exactly once;
6. leaves all linked, canonical, external, and predecessor evidence within their
   approved immutable states;
7. performs no prohibited runtime, owner, repository-integration, or external
   action; and
8. emits exactly:

   ```text
   ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
   ```

Success stops there.
