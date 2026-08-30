# Wave 0 A11 Stage 0 Preflight Expression Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `30735e992d8670991beb0c2882b8f225ff89d978`

**Required parent plan blob:** `c677fa4280965e52a5b46e1452fa3b4d3bc22413`

## Purpose

Recover only the A11 Stage 0 controller preflight from one consumed v11
PowerShell command-expression binding failure. The successor must preserve the
v11 controller and Stage 0 as immutable evidence, create a fresh v12 namespace,
repair the one proven expression shape, prove that shape semantically before
execution, and retain the raw UTF-8/LF transport architecture admitted by v11.

A successful v12 attempt proves only Stage 0 and its raw-byte transport. It
does not authorize parser/scalar recovery, canonical preserved-inventory
construction, formal A11 entry, report creation, Docker, GPU, model work, or
any downstream active-learning milestone.

The owner approved recommended approach A on 2026-08-30 with the exact
statement:

```text
核准此 A11 v12 preflight expression recovery 設計（方案 A）。
```

The success boundary is:

```text
ENTRYV12_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
```

## Preserved v11 incident

The immutable predecessor lineage is:

| Object | Commit | Blob |
|---|---|---|
| Stage 0 raw-byte output design | `29470670c4fe2095c0cedcf5ab389c2c82190e9c` | `8ead81be4da26dbd3e17badade45b7c746e8f8ce` |
| Stage 0 raw-byte output plan | `30735e992d8670991beb0c2882b8f225ff89d978` | `c677fa4280965e52a5b46e1452fa3b4d3bc22413` |

The v11 plan admitted and materialized exactly these two ignored ordinary
files with one `apply_patch` call:

| File | Bytes | SHA-256 |
|---|---:|---|
| `task-1-stage0-raw-byte-controller-v11.ps1` | 28,071 | `e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9` |
| `task-1-stage0-v11.ps1` | 21,104 | `c800436da3365b77e4d5c9da456a1ae128b7cdf35a934f17bdd7efec74ac73aa` |

Before formal invocation, v11 passed its complete materialization gate,
preservation gate, immutable-v10 behavioral RED, PowerShell 7.6.4 parser,
one Windows PowerShell 5.1 parser-only process, static raw-output GREEN, and
final invocation-boundary gate. The fixed expected raw arrays were child
bytes `186` with SHA-256
`4eca538ea77ef602a4e9d64c17583f753500dac3086a9c4190e231997064e45d`
and parent bytes `293` with SHA-256
`4a05611a769196e4881e252ad084fa4a075fa4bd3a85dcedefa8d6baba8a2848`.
No v11 source had been invoked at that point.

The v11 controller was then invoked exactly once. It exited one and emitted
exactly this diagnostic on stderr:

```text
ENTRYV11_CONTROLLER_DIAGNOSTIC|phase=controller_preflight|child_started=false|starts=0|exit=unavailable|timed_out=false|stdout_complete=false|stdout_bytes=0|stdout_sha256=unavailable|stderr_complete=false|stderr_bytes=0|stderr_sha256=unavailable|exception_sha256=7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191
```

The controller invocation is consumed. Its Stage 0 child was not started, so
the observed counts are controller invocations `1`, child starts `0`, and
retries `0`. Read-only failure preservation then proved that both v11 files,
the three v10 files, the branch, HEAD, staging, and linked/canonical worktrees
remained exact and clean. No v11 report, result, cache, temporary, machine, or
downstream object was created.

The immutable v11 terminal is:

```text
ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO
```

Neither v11 file may be invoked, imported, dot-sourced, edited, copied, moved,
renamed, deleted, completed, repaired, or reinterpreted as success evidence.

## Root cause and proof

The v11 controller line 171 contains:

```powershell
if (Test-Path -LiteralPath $V8Workspace -or Test-Path -LiteralPath $ConsumedV6Workspace) { throw 'consumed predecessor namespace exists' }
```

This text is syntactically valid in both admitted PowerShell parsers, but it
does not form two command expressions joined by a Boolean operator. In
PowerShell command-argument mode, the condition forms one `CommandAst` with
two `LiteralPath` parameters and no `BinaryExpressionAst` whose operator is
`Or`. Runtime parameter binding therefore fails before `Test-Path` can return.

A read-only minimal reproduction of the same expression shape produced the
exact exception message:

```text
Cannot bind parameter because parameter 'LiteralPath' is specified more than once. To provide multiple values to parameters that can accept multiple values, use the array syntax. For example, "-parameter value1,value2,value3".
```

Strict no-BOM UTF-8 hashing of that message yields exactly the diagnostic
SHA-256
`7b998330838b1cc066caf7f29ecd0cfffdc3113eb270bbb8175fb12197525191`.
This equality proves the root cause without rerunning v11.

The corrected expression is:

```powershell
if (
    (Test-Path -LiteralPath $V8Workspace) -or
    (Test-Path -LiteralPath $ConsumedV6Workspace)
) {
    throw 'consumed predecessor namespace exists'
}
```

Its parser shape is two `CommandAst` nodes, each with exactly one
`LiteralPath` parameter, inside two `ParenExpressionAst` nodes and joined by
exactly one `BinaryExpressionAst` whose operator is `Or`.

## Decision

Use a fresh, Stage-0-only v12 recovery with the smallest semantic repair and a
new AST-shape gate.

1. Preserve v11 and all earlier incidents exactly.
2. Commit this one-file docs-only design and a separately reviewed one-file
   implementation plan before creating a v12 runtime object.
3. Create a fresh ignored v12 namespace containing exactly one controller and
   one Stage 0 source.
4. Retain the v11 raw-byte child and parent transport architecture.
5. Replace only the proven invalid v11 condition shape with two separately
   parenthesized `Test-Path` command expressions joined by `-or`.
6. Update all lineage, role, path, source-identity, incident, terminal, and
   v12 inventory records; do not reuse a v11 identity or terminal.
7. Add an AST semantic gate that rejects the v11 shape even though it parses
   with zero errors.
8. Invoke the v12 controller once only after every entry, identity, parser,
   semantic, raw-byte, predecessor, runtime/provider, and Git gate passes.
9. Complete one read-only preservation closure and stop at the Stage 0
   transport boundary.

## Alternatives considered

### A. Fresh v12 with a narrow expression repair and AST gate — selected

This preserves the evidence firewall, fixes only the proven fault, and closes
the verification gap that allowed parser-valid but runtime-invalid command
binding. It adds no runtime role and keeps the successful raw-byte design.

### B. Extract a reusable preflight module — rejected

A module could make every predicate directly testable, but it would add a
third file, an import boundary, another source identity, and additional
success-stream and provenance surfaces. The single proven defect does not
justify that expansion.

### C. Remove the v8/v6 absence check — rejected

Removing the condition would avoid the failing line but weaken predecessor
admission. The absence facts remain required evidence and must be checked
correctly rather than omitted.

## Authority and non-goals

This design authorizes only:

- one one-file docs-only design commit;
- after owner approval of this written specification, one one-file docs-only
  implementation-plan commit;
- after separate plan approval and execution-mode selection, one single-use
  materialization of the plan-pinned v12 sources;
- read-only verification of approved repository, Git, artifact, runtime,
  provider, signature, parser, path, stream, and source identities;
- one single-use v12 controller invocation and at most one v12 Stage 0 child
  start; and
- one final read-only preservation closure.

It does not authorize:

- any invocation or mutation of v11, v10, v9, v8, v7, or earlier executable
  or evidence objects;
- repair in place, retry, alternate header, alternate writer, fallback,
  cleanup, deletion, expectation relaxation, or tuning to a formal result;
- a reusable preflight module, extra runtime process, recorder, report,
  result sidecar, transcript, cache, temporary object, bytecode, or machine
  directory;
- dynamic evaluation, dot-sourcing, source over stdin, `-Command` source
  execution, `-EncodedCommand`, Base64 transport, profile loading, PATH
  lookup, alternate executable, or shell-string child argv;
- parser/scalar worker phases, canonical preserved-inventory construction,
  static/formal A11 entry, report creation, or child-exit recovery;
- Docker, Docker Desktop, WSL, Hyper-V, GPU, `nvidia-smi`, CUDA, WDDM, A11
  launcher/runtime, model initialization, artifact campaign, calibration,
  validation, RDD, Wave 1, product, or network work;
- requesting, creating, inferring, incrementing, reserving, synthesizing, or
  consuming an `OwnerAuthorizationId`; or
- remote creation, push, merge, rebase, reset, stash, amend, squash,
  cherry-pick, tag, release, publication, deployment, another repository, or
  modification of the canonical checkout.

General owner trust does not widen these boundaries. A downstream recovery or
model runtime requires a separately approved design and plan.

## Append-only lineage and commit contract

This design changes exactly:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery-design.md
```

It must be a direct child of:

```text
30735e992d8670991beb0c2882b8f225ff89d978
```

The parent plan blob must be exactly:

```text
c677fa4280965e52a5b46e1452fa3b4d3bc22413
```

Its exact author and committer are:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Its exact subject is:

```text
docs: design A11 Stage 0 preflight expression recovery
```

After written-spec approval, the implementation plan may add exactly:

```text
docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery.md
```

The plan must be a one-file direct child of this design commit with the same
author and committer and exact subject:

```text
docs: plan A11 Stage 0 preflight expression recovery
```

The plan must pin the design commit and blob, full predecessor lineage, v11
incident and failure digest, both complete v12 source blocks and identities,
full patch headers, parser and AST gates, raw arrays, argv, timeout, failure
schema, single-use invocation, preservation closure, and stop terminal.

## Fresh v12 namespace and components

The canonical ignored workspace is:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-preflight-expression-recovery
```

Its successful inventory is exactly:

```text
task-1-stage0-preflight-controller-v12.ps1
task-1-stage0-v12.ps1
```

The controller owns repository, predecessor, source, runtime/provider,
signature, semantic-preflight, child-start, raw-capture, failure-diagnostic,
and parent-output responsibilities. Stage 0 owns the same read-only admission
envelope required at child time and the one-line raw UTF-8/LF producer role.
Neither component writes a file.

The namespace must be absent when the implementation plan is committed and at
the final materialization entry gate. Both complete sources are extracted
from the committed plan blob and created together by one `apply_patch` call
using full `<workspace>` shared-root-relative headers. The call is consumed
when invoked. Any API error, ambiguity, wrong target, partial materialization,
identity mismatch, or unexpected object preserves v12 as materialization
NO_GO and permits no second patch.

## TDD and semantic admission

The consumed v11 attempt is the behavioral RED. It is never rerun. The future
plan must independently prove all of these RED facts from immutable records:

- exact v11 two-file identities and inventory;
- controller invocations one, child starts zero, retries zero;
- exact `controller_preflight` diagnostic fields and exception SHA-256;
- exact v11 line 171 text;
- parser errors zero for that text;
- one `CommandAst`, two `LiteralPath` parameters, zero `Or`
  `BinaryExpressionAst`, and zero separating `ParenExpressionAst`; and
- exact minimal-reproduction message digest equality without invoking v11.

Before any v12 source invocation, GREEN requires:

1. both v12 sources match plan-pinned bytes, SHA-256, strict UTF-8/no-BOM,
   LF-only, one-final-LF, path, containment, stream, and ordinary-link policy;
2. both exact PowerShell 7.6.4 and Windows PowerShell 5.1 parsers admit both
   files with zero errors, with Windows PowerShell used only once as a
   parser-only process;
3. the corrected predecessor-absence condition contains exactly two
   `CommandAst` nodes and two `LiteralPath` parameters, one per command;
4. those commands are separated by exactly two `ParenExpressionAst` nodes and
   exactly one `BinaryExpressionAst` with operator `Or`;
5. no condition in either source contains one `CommandAst` with duplicate
   `LiteralPath` parameters or another duplicate named parameter;
6. controlled read-only evaluation in the verifier, not through either v12
   source, proves both approved consumed-predecessor paths are absent and the
   corrected Boolean result is false without a binding exception;
7. the complete v11 raw-capture/output static contract remains true: one
   controller child-start site, zero Stage 0 start site, exact structured
   argv, redirected empty stdin, concurrent raw stdout/stderr capture, bounded
   wait, timeout-only recursive kill, both task results explicitly suppressed,
   and one raw output write per successful role; and
8. all lineage, predecessor, runtime/provider, signature, inventory, absence,
   shadow-path, HEAD, branch, staging, and linked/canonical cleanliness facts
   remain exact.

The semantic gate must operate on parsed AST and ordinary read-only
`Test-Path` calls. It may not dynamically evaluate extracted source, create a
temporary script, import a v12 file, dot-source a function, or consume the
controller or child.

A mutation check parses two plan-pinned in-memory condition literals without
executing either one: the exact frozen v11 literal must fail the semantic gate,
while the exact corrected v12 literal must pass it. Both literals must still
produce zero parser errors. The check does not alter either source file.

## Stage 0 and raw-byte transport

The v12 plan retains the frozen PowerShell 7 executable and structured child
argv architecture from v11. The future plan must pin the exact executable,
five arguments, source identities, expected child and parent byte arrays,
counts, SHA-256 values, timeout, and diagnostic schema before materialization.

The child terminal family is:

```text
ENTRYV12_STAGE0_PASS|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
```

Stage 0 encodes exactly that ASCII line plus one LF with strict no-BOM UTF-8
and writes the bytes directly to `Console.OpenStandardOutput()` once, then
flushes once. It emits no PowerShell success-stream object.

The transport terminal family is:

```text
ENTRYV12_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

The controller starts the exact Stage 0 child at most once, closes stdin
without writing, captures both output streams concurrently as raw bytes,
explicitly suppresses async completion results, requires exit zero and empty
stderr, and compares child stdout byte-for-byte with the plan-pinned child
array. It then writes the exact two-line parent array through the raw standard
output stream once and flushes once. CRLF normalization, decoded line capture,
formatting objects, prefixes, suffixes, blank lines, fallback encodings, and
expectation relaxation are forbidden.

## Failure evidence and consumption

Every boundary is fail-closed.

- A pre-materialization difference stops without creating v12.
- The materialization patch is single-use at invocation.
- A controller invocation is consumed when issued, regardless of result.
- A successful child `Process.Start()` consumes Stage 0 immediately.
- Parser-only Windows PowerShell admission is single-use and may not execute a
  source AST.
- Any controller uncertainty before child start becomes a preserved v12
  controller NO_GO.
- Any child start followed by timeout, disconnect, incomplete capture, exit,
  stdout, stderr, identity, or side-effect difference becomes a preserved v12
  Stage 0 NO_GO.

Failure diagnostics may expose only facts available in memory: phase, whether
start succeeded, start count, exit code when available, timeout state,
capture-completion states, byte counts and digests when complete, and a stable
exception/rejection digest. A missing value is `unavailable`; it is never
invented. Diagnostics are ASCII on stderr and do not authorize a retry.

No failure permits source repair, expectation tuning, alternate expression,
second patch, second controller, second child, cleanup, deletion, or a move to
downstream work.

## Successful observation and closure

A successful evidence-host observation is controller exit zero, empty stderr,
and exactly the Stage 0 line followed by the transport line, each terminated
by one LF, with no other byte.

After that observation, one read-only closure must recheck:

- exact v12 design/plan commits, blobs, parentage, paths, author, committer,
  subjects, and both source identities;
- exact two-file v12 inventory and all shadow-path absences;
- exact preserved v11 two-file NO_GO, controller invocation count one, child
  starts zero, failure diagnostic, source line, and exception digest;
- exact v10/v9/v8/v7 and consumed-v6 records and absences required by the
  inherited Stage 0 envelope;
- exact runtime/provider files, versions, signatures, signer identities,
  command provenance, links, streams, and paths;
- unchanged HEAD and branch, empty staging, clean linked/canonical worktrees,
  and no cache, bytecode, temporary, result, report, repair, transcript, or
  machine object; and
- controller invocations one, child starts one, retries zero, and every
  prohibited action zero.

Only exact closure records:

```text
ENTRYV12_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
```

This is not a third controller output line and authorizes no continuation.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD is exactly `30735e992d8670991beb0c2882b8f225ff89d978` on
   `codex/wave0-model-contract`;
2. the parent plan blob is exactly
   `c677fa4280965e52a5b46e1452fa3b4d3bc22413`;
3. linked and canonical worktrees are clean and staging is empty before
   authoring;
4. v11 contains exactly its two frozen files and its controller is not
   invoked again;
5. only this design path changes;
6. the document is strict UTF-8 without BOM, LF-only, with one final LF;
7. placeholder, conflict-marker, unresolved-choice, internal-consistency,
   Markdown, whitespace, scope, authority, retry, terminal, path, identity,
   and evidence-limit checks pass;
8. the commit parent, changed path, author, committer, and subject are exact;
   and
9. design authoring executes no v11/v12/predecessor source, parser child,
   Docker, GPU, A11, model, network, owner, or external runtime command.

The design commit does not authorize implementation-plan authoring until the
owner approves this written specification. The future plan commit does not
authorize v12 materialization or execution until the owner separately
approves that plan and an explicitly supported execution mode.

## Success criteria

This design is satisfied only when a later approved implementation:

1. preserves v11 permanently as
   `ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO` with controller
   invocations one, child starts zero, and no second invocation;
2. creates exactly two fresh v12 sources from one plan-pinned patch and admits
   every source, path, inventory, predecessor, runtime/provider, and Git fact;
3. proves the corrected `Test-Path` condition has two separately
   parenthesized command expressions joined by one Boolean `Or`, and rejects
   the parser-valid v11 AST shape;
4. retains exact raw UTF-8/LF child and parent output with no success-stream or
   async-result leakage;
5. invokes the v12 controller once and starts the v12 child at most once;
6. completes exact read-only closure without a report or downstream object;
7. performs no prohibited predecessor, parser/scalar, Docker/GPU/A11/model,
   owner, network, integration, or publication action; and
8. records exactly:

   ```text
   ENTRYV12_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
   ```

Success stops there.
