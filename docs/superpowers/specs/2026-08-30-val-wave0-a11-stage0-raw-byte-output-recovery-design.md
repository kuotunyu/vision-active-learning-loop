# Wave 0 A11 Stage 0 Raw-Byte Output Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `0997117b53cca977e232e44eeda85e426a4e9328`

**Required parent plan blob:** `7ad8da8cbedfa614fd5d2e85b89b0ee43801861f`

## Purpose

Recover only the A11 Stage 0 transport boundary from one consumed v10 child-
output failure. The successor does not rerun, edit, complete, repair, or
reinterpret the v10 controller or Stage 0. It creates a fresh v11 namespace and
uses an exact raw-byte output protocol at both the child-to-controller and
controller-to-evidence-host boundaries.

The scope is deliberately narrower than the v10 plan. A successful v11 attempt
proves deterministic Stage 0 and transport output, then stops. Parser identity,
scalar identity, dual-parser execution, preserved-inventory construction,
static/formal entry, report creation, child-exit recovery, and every model
runtime remain outside this design.

The owner selected the recommended narrow v11 boundary and raw-byte architecture
on 2026-08-30 with the exact statement:

```text
我相信你的專業，都照你專業推薦的方式進行
```

The success boundary is:

```text
ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
```

## Preserved v10 incident

The immutable predecessor lineage is:

| Object | Commit | Blob |
|---|---|---|
| Stage 0 patch-root-binding design | `17bef41a33439fe47de42cce252118b10cee9af1` | `c97f5ac2f2ed30b6b8d2036e53c3957c359a43b0` |
| Stage 0 patch-root-binding plan | `0997117b53cca977e232e44eeda85e426a4e9328` | `7ad8da8cbedfa614fd5d2e85b89b0ee43801861f` |

The v10 plan first proved its patch authority with one exact non-executable
marker. It then materialized and admitted exactly these three ordinary files:

| File | Bytes | SHA-256 |
|---|---:|---|
| `task-0-patch-root-binding-v10.txt` | 1,058 | `d3b65530b7ed78e8da147bd81d9a2f9865de0ef87381367590ef58e72549dee5` |
| `task-1-stage0-transport-controller-v10.ps1` | 22,802 | `2629a28c20814f31da3a012f1a6dcbe74995482d0d864ff23d5bcca7ee7de78e` |
| `task-1-stage0-v10.ps1` | 25,072 | `5a3f978059241accafa439c5b45c905192b4876ffb20c83e666b8ee874d904fa` |

The namespace is:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-patch-root-binding-recovery
```

The exact marker PASS was:

```text
ENTRYV10_PATCH_ROOT_PASS|authority=workspace|marker_files=1|shadow_paths=0|writes=1|retries=0
```

After complete materialization, static, identity, encoding, path, inventory,
shadow-path, predecessor, and Git gates passed, the v10 transport controller was
invoked exactly once through its plan-pinned literal relative path. The
controller started its Stage 0 child exactly once.

The controller reached the assertion at source line 295 and rejected the child
stdout bytes. Reaching that assertion proves its immediately preceding result
gate passed: child start count was one, child exit code was zero, and captured
child stderr length was zero. The controller process exited one. Its
parent-visible combined tool capture contained two lines formatted as:

```text
System.Threading.Tasks.VoidTaskResult
System.Threading.Tasks.VoidTaskResult
```

and then the exception whose stable message was:

```text
Stage 0 child stdout bytes rejected
```

The controller did not preserve the actual child stdout byte count, digest, or
payload before throwing. This design therefore does not invent any of them and
does not claim that a particular newline sequence was observed. It records only
the facts proved by source progression and the captured parent result.

Immediately after failure, read-only closure proved all three v10 files retained
the exact identities above, the workspace still contained exactly three files
and no directory child, HEAD and branch were unchanged, staging was empty, and
linked and canonical worktrees were clean. No downstream v10 file was created.

The immutable terminal is:

```text
ENTRYV10_STAGE0_UNPROVABLE / NO_GO
```

The v10 controller and child are consumed. They may never be invoked, imported,
dot-sourced, copied, renamed, moved, edited, deleted, completed, or reinterpreted
as success evidence.

## Root cause and evidence limit

The failure exposes two independent output-contract defects.

First, the v10 controller called these methods as bare pipeline expressions:

```powershell
$StdoutTask.GetAwaiter().GetResult()
$StderrTask.GetAwaiter().GetResult()
```

On this host those calls emitted two `System.Threading.Tasks.VoidTaskResult`
objects into controller stdout. This defect is directly proved by the frozen
source and the parent-visible capture. Even if the child byte comparison had
passed, parent stdout could not have matched the required two-line protocol.

Second, Stage 0 emitted its terminal through the PowerShell success pipeline,
while the controller compared the resulting process stdout to one exact
UTF-8/LF byte array. The plan pinned the expected bytes but did not bind the
host's success-stream-to-native-stdout serialization. The captured child bytes
were rejected, but they were not exposed or persisted. A platform newline is a
plausible explanation, not an observed fact, and is not promoted to evidence.

The broader defect is an unbound serialization boundary. Source text, process
identity, Unicode argv, child exit, and stderr can all be correct while the
bytes crossing stdout differ from an expected protocol. The recovery must make
the emitted bytes explicit rather than relax the comparison to an ambient host
format.

## Decision

Use a fresh, Stage-0-only v11 recovery with a raw-byte protocol at both output
boundaries.

1. Preserve v10 and all earlier incidents and evidence exactly.
2. Commit this one-file docs-only design and a separately reviewed one-file
   implementation plan before creating any v11 runtime object.
3. Use one fresh ignored v11 namespace containing exactly two executable source
   files.
4. Retain the proven shared-root-relative patch mapping from v10 and use its
   exact authority-prefix semantics for v11 materialization.
5. Make Stage 0 generate its terminal byte array with the strict no-BOM UTF-8
   encoder and write that byte array directly to the standard-output base
   stream with exactly one LF and no CR.
6. Make the controller capture child stdout and stderr concurrently as raw
   bytes, explicitly discard both async completion results, and compare the
   captured bytes ordinally to the plan-pinned child terminal bytes.
7. After exact child admission, make the controller generate and write the two
   parent protocol lines directly as one plan-pinned raw UTF-8/LF byte array.
8. Require the evidence host to observe exit zero and exactly those two lines
   with no additional byte. Any other observation is failure.
9. Perform one final read-only preservation closure and stop. Do not begin the
   downstream entry-verifier recovery in the same plan.

This design neither patches v10 nor tunes an expectation to the consumed
result. It replaces implicit formatting with an explicit byte protocol in a new
lineage.

## Alternatives considered

### A. Raw-byte output at both boundaries — selected

This closes both observed defects without accepting platform-dependent output.
The same plan-pinned byte array is the producer contract, capture contract, and
evidence-host contract. It retains strict UTF-8/LF semantics and introduces no
additional process role.

### B. Accept Windows CRLF and suppress async results — rejected

This is a smaller source change, but it would make the protocol depend on the
host's line formatting and would preserve an implicit serialization boundary.
It would also turn an unobserved CRLF hypothesis into policy merely because it
fits the failure.

### C. Add an independent recorder process — rejected

A third process could capture controller stdout and stderr separately and
persist richer evidence, but it adds a new executable identity, start boundary,
timeout, and failure surface. Exact successful combined output and nonzero-exit
failure diagnostics do not require that complexity at this milestone.

### D. Edit or wrap the v10 sources — rejected

Both v10 executable identities and their invocation are consumed evidence.
Changing or wrapping either file would repair a frozen attempt and destroy the
append-only meaning of `ENTRYV10_STAGE0_UNPROVABLE / NO_GO`.

## Authority and non-goals

This design authorizes only:

- one one-file docs-only design commit;
- after owner approval of this written specification, one one-file docs-only
  implementation-plan commit;
- after separate implementation-plan approval, one `apply_patch` operation
  that creates the two fresh v11 sources and one complete read-only admission;
- one single-use v11 controller invocation and at most one v11 Stage 0 child
  start;
- read-only verification of approved Git, repository, preserved artifact,
  executable, Security-provider, signature, and process identities; and
- one final read-only v11 preservation closure.

It does not authorize:

- invoking, modifying, moving, copying, renaming, deleting, completing, or
  repairing any v10, v9, v8, v7, or earlier executable/evidence object;
- parser-identity RED/GREEN, scalar-identity RED/GREEN, dual-parser execution,
  canonical preserved-inventory creation, static/formal entry, report creation,
  or child-exit recovery;
- Docker, Docker Desktop, WSL, Hyper-V, GPU, `nvidia-smi`, CUDA, WDDM, A11
  launcher/runtime, artifact campaign, product source, model initialization,
  calibration, validation, RDD, Wave 1, or network action;
- requesting, creating, inferring, incrementing, reserving, synthesizing, or
  consuming an `OwnerAuthorizationId`;
- source transport over stdin, `-Command`, `-EncodedCommand`, Base64 execution,
  dynamic evaluation, dot-sourcing, profile loading, PATH lookup, alternate
  executable, alternate script, fallback, retry, sleep, or tuning;
- shell file writers, generated repair files, temporary files, transcripts,
  result sidecars, cache, bytecode, or machine directories;
- modifying another repository or the canonical checkout; or
- remote creation, push, merge, rebase, reset, stash, amend, squash,
  cherry-pick, tag, release, publication, or deployment.

General owner trust does not widen these boundaries. New external authority,
destructive action, downstream recovery, or model runtime requires a separate
approved design and plan.

## Append-only lineage

This design changes exactly:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery-design.md
```

It must be a direct child of:

```text
0997117b53cca977e232e44eeda85e426a4e9328
```

Its exact author and committer are:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Its exact subject is:

```text
docs: design A11 Stage 0 raw byte output recovery
```

After written-spec approval, the implementation plan may add exactly:

```text
docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery.md
```

The plan must be a one-file direct child of this design commit with the same
author and committer. It must pin this design commit and blob, complete
predecessor lineage, all preserved v10 identities and failure facts, both full
v11 source blocks and identities, complete patch headers, argv, raw byte arrays,
static requirements, timeout, invocation, failure schema, closure, and terminal
before v11 materialization.

The design commit does not authorize plan authoring until the owner approves
this written specification. The plan commit does not authorize materialization
or execution until the owner separately approves the plan and an explicitly
supported execution mode.

## Fresh v11 namespace and materialization

The canonical ignored workspace is:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery
```

Its repository-relative spelling is:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery/
```

It must be absent when the implementation plan is committed and at the final
pre-materialization entry gate. The successful inventory is exactly:

```text
task-1-stage0-raw-byte-controller-v11.ps1
task-1-stage0-v11.ps1
```

No marker is recreated. The exact v10 marker remains the immutable proof that
`apply_patch` resolves the approved full header prefix against
`<workspace>`. The v11 plan must use the same shared-root-relative prefix
with only the new namespace and leaf names changed, and it must freeze both
complete headers.

Both sources are created together by one `apply_patch` call after exact v11
absence and source-block admission. The call is single-use at invocation. An
API error, timeout, disconnect, empty or ambiguous result, wrong target, or
partial materialization consumes the attempt.

Before either file can be invoked, read-only verification requires:

1. both canonical targets exist exactly once and the namespace has exactly two
   files and no directory child;
2. canonical containment, ordinary file and parent-chain policy, no reparse
   point, no link, and one default data stream;
3. strict UTF-8 round trip, no BOM, no CR, exact one final LF, byte count, and
   SHA-256 match the committed plan blocks;
4. all complete patch headers and defined shadow paths match the plan;
5. v10 remains the exact three-file preserved NO_GO and every earlier required
   predecessor record remains exact;
6. linked and canonical worktrees remain clean, staging is empty, and HEAD and
   branch are exact; and
7. no process, import, source execution, runtime, network, or external action
   occurred during materialization admission.

Any difference freezes every located v11 object as:

```text
ENTRYV11_MATERIALIZATION_UNPROVABLE / NO_GO
```

There is no alternate header, root, writer, copy, move, repair, cleanup, or
second patch.

## Stage 0 raw-byte producer

Stage 0 v11 retains the approved read-only admission envelope required to prove
the same repository state that v10 attempted to prove. It uses fresh v11
lineage, source identity, paths, inventory, role, and terminal.

Before success it proves at least:

- exact v11 design/plan parentage, blobs, author, committer, subject, branch,
  linked-worktree topology, non-submodule state, staging, and linked/canonical
  cleanliness;
- exact v10 design/plan lineage, marker/controller/Stage 0 identities,
  three-file inventory, marker PASS, consumed start/result facts, immutable
  NO_GO, and zero downstream-v10-file state;
- exact preserved v9, v8, and v7 incidents and the predecessor absences needed
  by the v10 Stage 0 envelope;
- exact v11 controller and Stage 0 `$PSCommandPath`, bytes, digest, encoding,
  containment, link, stream, and ordinary parent-chain identities;
- exact PowerShell 7 and Windows PowerShell 5.1 executable identities and their
  approved role-specific Security-provider manifests, assemblies, signatures,
  signers, versions, link policies, and command provenance;
- current process path is the exact frozen PowerShell 7 executable, version is
  `7.6.4`, and edition is `Core`;
- v11 inventory contains exactly the two admitted files; and
- zero write, parser child, predecessor execution, Docker/GPU/A11/model,
  network, owner, or external action.

The child terminal family is:

```text
ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
```

Stage 0 constructs exactly that ASCII text plus one LF, encodes it with
`System.Text.UTF8Encoding(false, true)`, and writes the resulting byte array
directly to `Console.OpenStandardOutput()`. It writes once, flushes once, and
disposes no process-owned standard stream. It does not emit the terminal as a
bare string or use `Write-Output`, `Write-Host`, `Out-String`, formatting,
redirection, transcript, console-encoding mutation, or another output API.

Every helper or method capable of producing a success-stream object is consumed
explicitly. Stage 0 produces no success-stream object before or after the raw
write. Any unbound output is a protocol failure at the controller.

## Transport controller

The controller is invoked once through a plan-pinned literal ASCII relative
path from the linked worktree. It self-attests its current process, its own
source, the child source, the two-file namespace, preserved v10 evidence, plan
lineage, executable/provider identities, and Git cleanliness before starting a
child.

The child start uses the exact frozen PowerShell 7 executable and structured
`ProcessStartInfo.ArgumentList` with exactly:

```text
-NoLogo
-NoProfile
-NonInteractive
-File
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-raw-byte-output-recovery\task-1-stage0-v11.ps1
```

`UseShellExecute` is false. Standard input, output, and error are redirected.
Immediately after the sole successful start, the controller closes child stdin
without writing any byte. It starts stdout and stderr `BaseStream.CopyToAsync`
drains before waiting for exit, uses one plan-pinned bounded timeout, and has
exactly one timeout-only child-tree kill path.

Both async completions are consumed with an explicit no-output construct such
as:

```powershell
[void]$StdoutTask.GetAwaiter().GetResult()
[void]$StderrTask.GetAwaiter().GetResult()
```

Bare `GetResult()`, `Wait()`, or another task result expression is forbidden.

After exit, the controller requires one successful start, exit zero, empty
stderr, unchanged workspace, and child stdout exactly equal in byte count,
SHA-256, strict UTF-8 decode, and ordinal text to the plan-pinned Stage 0 byte
array. It neither normalizes nor accepts CRLF, platform newlines, whitespace,
extra objects, prefixes, suffixes, blank lines, or alternate encodings.

The parent transport terminal family is:

```text
ENTRYV11_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

Only after complete child admission, the controller constructs one output byte
array containing the exact Stage 0 terminal line followed by the exact
transport terminal line, each with one LF. It writes that array directly to
the standard-output base stream once and flushes once. It emits no PowerShell
success-stream object and no stderr byte on success.

The controller writes no file. It may not invoke any predecessor, parser,
Docker/GPU/A11/model/runtime, or network process.

## Failure evidence and consumption

All gates are fail-closed.

- A pre-materialization difference stops without creating v11.
- The source `apply_patch` is consumed when called, not when its targets are
  later found.
- A controller invocation is consumed when issued, regardless of result.
- A successful `Process.Start()` consumes Stage 0 immediately.
- Any controller uncertainty before child start is:

  ```text
  ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO
  ```

- Any child start followed by timeout, disconnect, incomplete capture, exit,
  stdout, stderr, identity, or side-effect difference is:

  ```text
  ENTRYV11_STAGE0_UNPROVABLE / NO_GO
  ```

The implementation plan must require failure diagnostics to expose only facts
actually available in memory: phase, whether start succeeded, start count, exit
code when available, stdout/stderr byte counts and SHA-256 values when complete,
timeout state, and the first stable rejection code. It must never fabricate a
missing digest, payload, PID, or stream separation. A payload is not printed
merely to diagnose formatting.

Failure diagnostics are ASCII and must not appear on stdout. Diagnostic
emission does not convert a failure to a retryable preflight. Timeout permits
only termination of the exact admitted child tree. No failure permits rerun,
alternate output formatting, expectation relaxation, source edit, fallback,
repair, deletion, or cleanup.

## TDD and pre-invocation verification

The consumed v10 attempt is the behavioral RED for this output-contract defect.
It is never rerun to obtain missing bytes or a more convenient failure. The v11
plan maps the observed RED to complete pre-materialization and pre-invocation
tests.

Before source materialization, the committed plan blob is the sole source of
both complete v11 blocks. Their bytes are computed without newline
normalization and matched to unique plan-pinned identity records.

Before controller invocation, verification must prove without executing either
source:

- both complete files parse with zero errors under the exact PowerShell 7.6.4
  parser and the explicit Windows PowerShell 5.1 parser API;
- exact strict UTF-8/no-BOM/LF/single-final-LF identities;
- exact `$PSCommandPath` self-attestation and unique plan-identity lookup in
  both sources;
- exactly one controller `Process.Start()` call site and exact five-element
  structured child argv;
- `UseShellExecute=false`, all three redirects true, exactly one post-start
  stdin close, zero input writes, concurrent raw capture, one bounded wait, and
  one timeout-only recursive kill;
- exactly two async completion calls and both results statically bound to
  `[void]` or an equivalent no-output assignment;
- zero bare task-completion expressions, line-oriented output capture, decoded
  `ReadToEnd`, retry, fallback, sleep, alternate executable, shell-string child,
  dynamic execution, profile, stdin source, or console-encoding mutation;
- Stage 0 has zero process starts and exactly one standard-output base-stream
  write site using the plan-pinned byte array;
- controller has exactly one successful-protocol standard-output base-stream
  write site using the plan-pinned two-line byte array;
- neither source contains a bare success terminal, `Write-Output`, `Write-Host`,
  output redirection, transcript, formatter, or unconsumed helper call capable
  of emitting a success-stream object;
- the child and parent expected byte arrays independently equal the exact
  plan-pinned strings encoded by strict no-BOM UTF-8 with LF only;
- all source, runtime, provider, marker, predecessor, path, inventory, absence,
  and Git identities are exact; and
- v10 source bytes do not appear as an executable block in the v11 plan.

An AST-only or byte-array behavioral assertion may exercise pure in-memory
construction during admission. It may not invoke v10, create a temporary file,
start another PowerShell process, write to a console stream, or consume the v11
controller/child.

Any difference before controller invocation is:

```text
ENTRYV11_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO
```

The two v11 files remain frozen and no process starts.

## Successful observation and closure

The sole successful controller observation is exit zero, no additional output,
and parent-visible stdout exactly:

```text
ENTRYV11_STAGE0_PASS|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
ENTRYV11_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

Both lines end with LF, including the second. There is no CR, BOM, blank line,
prefix, suffix, formatting object, or stderr byte.

After that observation, one read-only closure rechecks:

- exact design/plan commits, blobs, paths, parentage, author, committer, and
  subjects;
- exact two-file v11 inventory, source identities, path/stream/link/encoding
  policies, and all defined shadow-path absences;
- exact three-file v10 preserved inventory and immutable NO_GO;
- exact required v9, v8, v7, runtime, and provider identities and absences;
- HEAD, branch, linked/canonical cleanliness, and empty staging;
- no cache, bytecode, temporary, result, report, machine, or unapproved object;
  and
- zero prohibited process, Docker/GPU/A11/model/owner/network/repository action.

Only exact closure allows the executor to record the milestone:

```text
ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
```

This milestone is not a third controller output line and is not an authorization
to continue. A later separately approved design and plan must consume the v11
evidence immutably before any parser/scalar or entry-verifier work.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD is exactly `0997117b53cca977e232e44eeda85e426a4e9328`;
2. branch is exactly `codex/wave0-model-contract`;
3. the parent plan blob is exactly
   `7ad8da8cbedfa614fd5d2e85b89b0ee43801861f`;
4. linked and canonical worktrees were clean and staging empty before authoring;
5. v10 contains exactly the three frozen files and v11 is absent;
6. only this design path changed;
7. the document is strict UTF-8 without BOM, LF-only, with one final LF;
8. placeholder, conflict-marker, unresolved-choice, internal-consistency,
   Markdown, whitespace, scope, authority, retry, terminal, path, identity, and
   evidence-limit reviews pass;
9. the commit parent, changed path, author, committer, and subject are exact;
   and
10. design authoring executed no v10/v11/predecessor source, parser, Docker,
    GPU, A11, product, model, network, owner, or external runtime command.

The design commit does not authorize plan authoring until the owner approves
this written specification. The future plan commit does not authorize v11
materialization or execution until the owner separately approves that plan and
chooses Inline Execution or another explicitly supported execution mode.

## Success criteria

This design is satisfied only when a later approved implementation:

1. preserves v10 permanently as `ENTRYV10_STAGE0_UNPROVABLE / NO_GO` with its
   exact three-file inventory and no second invocation;
2. creates exactly two fresh v11 sources from one plan-pinned, single-use patch
   and admits their complete identities before execution;
3. starts exactly one v11 Stage 0 child through the frozen Unicode `-File` argv
   with empty stdin and concurrent raw stream capture;
4. emits the child terminal and parent protocol through explicit raw UTF-8/LF
   writes, with no PowerShell success-stream or async-result leakage;
5. observes exact child and parent bytes, exit codes, stderr, identities, Git
   facts, and zero side effects once;
6. completes exact final read-only closure without creating any downstream or
   report artifact;
7. performs no prohibited predecessor, parser/scalar, Docker/GPU/A11/model,
   owner, network, integration, or publication action; and
8. records exactly:

   ```text
   ENTRYV11_STAGE0_TRANSPORT_PASS / DOWNSTREAM_NOT_AUTHORIZED
   ```

Success stops there.
