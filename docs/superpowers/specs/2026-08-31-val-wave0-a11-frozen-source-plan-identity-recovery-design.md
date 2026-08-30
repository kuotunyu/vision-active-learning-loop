# Wave 0 A11 Frozen-Source Plan-Identity Recovery Design

## Status and authority

This document defines the fresh v13 recovery for the v12 plan-review failure.
The owner approved recommended approach A and authorized design, written-spec,
implementation-plan, and Inline Execution work in one instruction on
2026-08-31. The authority is limited to this recovery and ends at the v13
Stage 0 transport boundary.

Repository and branch are frozen as:

- repository: `<repo>\.worktrees\wave0-model-contract`;
- canonical read-only checkout: `<repo>`;
- branch: `codex/wave0-model-contract`;
- v12 plan-review commit: `97acd06f61fdac5df11e3a8fb21b641101b9f482`;
- v12 plan blob: `c11c95c5a4ce32c373599a41d755da7931640681`.

The approved authority does not authorize rewriting v12, amending history,
retrying an old attempt, Docker, WSL, GPU, CUDA, model work, formal A11 entry,
Wave 1, push, merge, release, or an `OwnerAuthorizationId` flow.

## Preserved v12 plan-review failure

The v12 plan was committed with exact subject:

```text
docs: plan A11 Stage 0 preflight expression recovery
```

Both plan-pinned v12 sources instead contain exactly one lineage comparison
against the stale v11 subject:

```text
docs: plan A11 Stage 0 raw byte output recovery
```

The comparisons are parser-valid but guaranteed to reject the actual v12 HEAD
before child start. The mandatory execution-plan review detected the mismatch
before materialization. No v12 namespace or source was created; materialization
calls, Windows PowerShell parser processes, controller invocations, and child
starts are all zero. The preserved record is:

```text
PRESERVED_V12_PLAN_REVIEW|plan_commit=97acd06f61fdac5df11e3a8fb21b641101b9f482|materializations=0|windows_parser_processes=0|controller_invocations=0|child_starts=0|fault=frozen_source_plan_subject_stale|terminal=ENTRYV12_MATERIALIZATION_UNPROVABLE / NO_GO
```

The v12 plan commit, design, source blocks, source identities, and absence of
the v12 runtime namespace are immutable evidence. They are never amended,
materialized, executed, copied, repaired, deleted, or reinterpreted as a
runtime attempt.

## Root cause

The v12 source blocks were derived from the v11 source architecture. Paths,
roles, terminals, and the expression repair were updated, but the exact HEAD
identity comparison in both sources retained the v11 plan subject. Parser and
AST-shape checks admitted the files because the stale value is a valid string.
The plan lacked a semantic gate connecting that string to the actual committed
plan identity.

The defect is therefore not PowerShell syntax, runtime state, or transport.
It is a missing cross-boundary identity-consistency assertion between:

1. the committed implementation plan;
2. the identity record expected by each frozen source; and
3. the identity record observed by each source at runtime.

## Decision

Use a fresh v13 namespace and two fresh plan-pinned sources. Preserve the v12
plan-review NO_GO and retain the admitted raw-byte architecture. Change only
the recovery lineage, namespace, filenames, v13 terminals, and plan-identity
contract required by the fresh attempt.

The v13 design commit is a direct child of the preserved v12 plan commit. The
v13 plan commit is a direct child of the v13 design commit and has exact
subject:

```text
docs: plan A11 frozen source plan identity recovery
```

Both frozen v13 sources require the exact author, author email, committer,
committer email, and subject record:

```text
kuotunyu|61350295+kuotunyu@users.noreply.github.com|kuotunyu|61350295+kuotunyu@users.noreply.github.com|docs: plan A11 frozen source plan identity recovery
```

They also require the v13 plan parent to be the exact v13 design commit, and
the v13 design parent to be preserved v12 plan commit
`97acd06f61fdac5df11e3a8fb21b641101b9f482`.

## Alternatives

### A. Fresh v13 with identity-consistency RED/GREEN — selected

This retains immutable evidence, avoids consuming the guaranteed-failing v12
controller, and makes the missing semantic relationship independently
testable before source execution.

### B. Modify or amend the v12 plan — rejected

Changing the approved v12 commit would rewrite preserved evidence, violate the
no-amend boundary, and make the prior review finding non-reproducible.

### C. Override the expected identity at runtime — rejected

An environment variable, argument, wrapper, or fallback would add an unpinned
authority channel and could tune identity expectations after observation.

## Fresh v13 namespace and components

The ignored evidence workspace is:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-frozen-source-plan-identity-recovery
```

It contains exactly two ordinary files:

1. `task-1-stage0-plan-identity-controller-v13.ps1` — self-attests lineage,
   source, predecessor, runtime/provider, signature, path, and Git facts;
   starts the Stage 0 child once; captures raw streams; and emits the exact
   two-line parent byte array.
2. `task-1-stage0-v13.ps1` — independently attests the read-only envelope and
   emits one exact raw Stage 0 terminal.

No report, result, marker, transcript, manifest, cache, bytecode, temporary,
repair, machine, or nested directory is allowed.

## Identity-consistency TDD contract

The implementation plan must freeze complete v13 source blocks and exact
source identities before materialization.

RED reads the committed v12 plan as data, extracts both v12 frozen source
blocks, and proves for each source:

- exactly one HEAD identity comparison exists;
- the comparison contains the stale v11 subject;
- the comparison does not contain the actual v12 subject;
- comparing the actual v12 HEAD record to the frozen expected record is false;
- v12 materializations, parser processes, controller invocations, and child
  starts remain zero.

GREEN reads both admitted v13 source files as data and proves for each source:

- exactly one HEAD identity comparison exists;
- its expected identity record equals the actual v13 HEAD identity record;
- the stale v11 and v12 plan subjects are absent from that comparison;
- the v13 plan parent/design parent chain is exact;
- parser errors are zero in PowerShell 7.6.4 and Windows PowerShell 5.1;
- the corrected predecessor-absence condition retains two command ASTs, two
  `LiteralPath` parameters, two parentheses, and one Boolean `Or`;
- no command contains a duplicate named parameter; and
- process-start and raw-output topology remains exact.

Any RED or GREEN uncertainty is fail-closed. It never authorizes source repair,
expectation relaxation, alternate materialization, or retry.

## Materialization and execution boundary

The plan commit pins complete source bytes, lowercase SHA-256 values, full
shared-root-relative patch headers, runtime/provider identities, signatures,
parser gates, raw child and parent arrays, timeout, diagnostic schema, and
closure checks.

One `apply_patch` call materializes both sources. The patch is consumed when
invoked. Any empty, ambiguous, disconnected, partial, timed-out, or erroneous
result preserves the state and stops. Shell writers, copy, move, rename,
repair, deletion, cleanup, and alternate patch roots are forbidden.

Windows PowerShell 5.1 is started once only for parser admission. It never
executes either source. The v13 controller is invoked once only after every
RED/GREEN, identity, parser, predecessor, runtime/provider, signature, path,
stream, and Git gate passes. A successful child `Process.Start()` consumes
Stage 0 immediately.

## Raw-byte protocol

The child terminal family is:

```text
ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
```

The transport terminal family is:

```text
ENTRYV13_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

Stage 0 writes the child line plus one LF through
`Console.OpenStandardOutput()` exactly once and flushes once. The controller
uses the frozen PowerShell 7 executable and structured five-argument child
argv, closes stdin without writing, captures stdout and stderr concurrently as
raw bytes, suppresses async completion objects, requires exit zero and empty
stderr, compares child stdout byte-for-byte, and writes the exact two-line
parent array once.

No CRLF normalization, decoded-line capture, formatting object, prefix,
suffix, blank line, fallback encoding, or expectation relaxation is allowed.

## Failure handling

Every boundary is fail-closed:

- pre-materialization differences stop with no v13 namespace;
- materialization uncertainty preserves any created bytes and stops;
- parser-process uncertainty consumes the one parser admission and stops;
- controller uncertainty before child start preserves a controller NO_GO;
- any child start followed by timeout, disconnect, incomplete capture, exit,
  stdout, stderr, identity, or side-effect difference preserves a Stage 0
  NO_GO; and
- no failure permits a second patch, parser process, controller, or child.

Diagnostics contain only facts available in memory: phase, child-start state,
start count, exit code when available, timeout state, capture-completion state,
byte counts and digests when complete, and a stable failure digest. Missing
facts are `unavailable`; they are never synthesized.

## Successful closure

Successful observation is controller exit zero, empty stderr, and exactly the
Stage 0 line followed by the transport line, each terminated by one LF and no
other byte.

One final read-only closure rechecks:

- exact v13 design/plan lineage, identities, subjects, paths, and blobs;
- exact two-file v13 source inventory and all shadow absences;
- immutable v12 plan-review NO_GO and absent v12 namespace;
- immutable v11/v10 incidents and exact inherited v10/v9/v8/v7/v6 facts;
- runtime/provider files, versions, links, streams, signatures, signers, and
  command provenance;
- unchanged HEAD/branch, empty staging, and clean linked/canonical worktrees;
- no unexpected object; and
- v13 controller invocations one, child starts one, retries zero, and every
  prohibited action zero.

Only exact closure records:

```text
ENTRYV13_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
```

This is not a third controller output line and authorizes no downstream work.

## Commit and verification gates

The design commit:

- has direct parent `97acd06f61fdac5df11e3a8fb21b641101b9f482`;
- changes only this design path;
- uses exact author and committer
  `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`;
- has exact subject `docs: design A11 frozen source plan identity recovery`;
- preserves strict UTF-8 without BOM, LF-only, and one final LF; and
- executes no v12/v13/predecessor source, parser child, controller, Docker,
  GPU, model, network, owner, or external runtime command.

The plan commit is a direct child of the design commit, changes only one plan
path, uses the same exact identity, and has exact subject
`docs: plan A11 frozen source plan identity recovery`.

The owner has already authorized transition from this written spec to the
implementation plan and Inline Execution. No additional approval is required
between those stages. Execution still stops on the first preserved NO_GO, new
external authority requirement, or destructive action.
