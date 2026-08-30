# Wave 0 A11 Stage 0 Unicode Transport Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `ab84df410605c824ba42ecd274bbcd6ba4670f19`

## Purpose

Recover the entry-verifier parser-identity milestone from one consumed v8 Stage
0 Unicode-transport failure without rerunning, repairing, completing, or
reinterpreting that failed Stage 0. The successor uses one fresh v9 namespace
and replaces UTF-8 source-over-stdin with identity-pinned UTF-8 files plus a
structured `ProcessStartInfo.ArgumentList` `-File` boundary.

The owner approved the architecture on 2026-08-30 with the exact statement:

```text
核准此 A11 Stage 0 Unicode transport recovery 設計（方案 A）。
```

The approved scope is a fresh recovery of the same read-only parser-identity
milestone. It may re-establish Stage 0 under the new transport and, only after
that exact gate passes, perform fresh v9 versions of the previously approved
parser-identity TDD, dual-parser, scalar-comparator, static, formal, and closure
phases. No v8 executable source, process result, output, or implied PASS is an
input to v9 success.

The final success boundary remains:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

## Preserved v8 incident

The immutable predecessor lineage is:

| Object | Commit | Blob |
|---|---|---|
| Original parser-identity design | `0788f6143691d5a39730fb06508be3949de1b3f0` | `a837d94d58d8ad2ee1c71fd51de64257fe49d060` |
| Security-provider amendment | `5d7500abef12ff724d0fb9c256a1894979bd8677` | `20661c3572d8723d7c52c4d745703a5f7741b8dd` |
| v8 implementation plan | `ab84df410605c824ba42ecd274bbcd6ba4670f19` | `4bd91b8b9aeec55c18d8c14056b1176e511be967` |

The committed v8 Stage 0 source was exact LF/UTF-8 without BOM:

```text
byte count: 14198
SHA-256: 5c9de5a85ae6e90fa5d4bd23c7e8f7fc49061a85d2f3c55a39524d9f48b19c70
```

An initial attempt to carry that source with `-EncodedCommand` failed inside
the parent `Process.Start()` call with a Windows filename-or-extension-too-long
error. No child process existed, so that preflight did not consume Stage 0. A
separate ASCII-only, no-side-effect stdin transport preflight then passed.

The actual v8 Stage 0 started once with:

```text
executable: C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe
argv: -NoLogo -NoProfile -NonInteractive -Command -
child PID: 34976
source byte count: 14198
source SHA-256: 5c9de5a85ae6e90fa5d4bd23c7e8f7fc49061a85d2f3c55a39524d9f48b19c70
```

The process exited `1`, returned zero stdout bytes, and returned 156 stderr
bytes. The captured stderr text was:

```text
Push-Location: Cannot find path '<workspace>\CC_github?��?\vision-active-learning-loop\.worktrees\wave0-model-contract' because it does not exist.
```

No raw stderr artifact or digest was persisted; this specification does not
invent one. The exact terminal is permanently:

```text
ENTRYV8_STAGE0_UNPROVABLE / NO_GO
```

The process start consumed v8 Stage 0 even though it failed before any Stage 0
admission assertion. It must never be launched again under stdin, `-File`,
`-EncodedCommand`, a copied source, or any other transport.

A later read-only diagnostic did not execute the v8 source. It proved that the
exact PowerShell 7 child reports stdin encoding `big5`, code page `950`, while
the parent supplied the committed command body as UTF-8 bytes. The intended
path component `部隊` is U+90E8 U+968A and has UTF-8 bytes
`E9 83 A8 E9 9A 8A`. Big5 decoding therefore corrupted the path literal before
PowerShell executed `Push-Location`.

After the failure:

- HEAD remained `ab84df410605c824ba42ecd274bbcd6ba4670f19`;
- linked and canonical worktrees were clean and staging was empty;
- the v8 workspace remained absent;
- no RED, GREEN, worker, controller, inventory, static, formal, closure, or
  report source was created;
- no Docker, GPU, lease, A11 runtime, product, model, or network phase ran; and
- no `OwnerAuthorizationId` was requested, synthesized, or consumed.

These facts are a failed procedure record, not a statistical or runtime
observation.

## Root cause

The v8 plan froze the Stage 0 source bytes but did not freeze the child process'
stdin decoder or prove that decoder compatible with those bytes. PowerShell's
`-Command -` reads its command body through the host input encoding, which on
this Windows host was Big5/code page 950. The parent wrote UTF-8 bytes. A source
identity can therefore remain exact at the parent boundary while the executed
character stream differs inside the child.

The defect is not the repository path, the `部隊` directory, Git worktree
topology, executable identity, provider identity, PowerShell parser, or v7
evidence. It is an unbound byte-to-character transport contract at the Stage 0
process boundary.

The recovery must make source identity and process transport one closed
contract. Merely checking the parent source digest again would not prove what
the child decoded.

## Decision

Use two plan-pinned UTF-8 files and one structured child start:

1. Materialize a transport controller and a Stage 0 source in a fresh v9
   namespace from exact blocks in the committed successor plan.
2. Validate both files by canonical path, containment, type, ordinary parent
   chain, strict UTF-8 decoding, byte-for-byte UTF-8 re-encoding, BOM/CR/final-
   LF policy, byte count, and SHA-256 before any consuming invocation.
3. Invoke the controller through one literal ASCII relative path in the exact
   PowerShell 7 controller shell. No source crosses stdin or a command-line
   payload boundary.
4. The controller self-attests its process and both source identities, then
   starts exactly one Stage 0 child with the exact frozen `pwsh.exe` and
   `ProcessStartInfo.ArgumentList`.
5. The child argv is exactly:

   ```text
   -NoLogo
   -NoProfile
   -NonInteractive
   -File
   <repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery\task-1-stage0-v9.ps1
   ```

6. The controller redirects stdin to an empty pipe, closes that pipe immediately
   after the child starts, and never writes a byte. It captures stdout and
   stderr concurrently as raw bytes.
7. Stage 0 self-attests the exact process identity, `$PSCommandPath`, its own
   raw bytes and digest, controller identity, and approved repository evidence
   before emitting PASS.

Windows carries `ProcessStartInfo.ArgumentList` values through the native
Unicode process boundary. PowerShell 7 reads the materialized no-BOM script as
UTF-8. The same literal source bytes validated by the controller are therefore
the bytes read from the child script file, and the child proves that identity
again from inside the running process.

## Alternatives considered

### A. Plan-pinned UTF-8 file plus structured `-File` argv — selected

This uses native Unicode argv and PowerShell's supported script-file decoder.
It keeps the executable source visible, hashable, dual-parser-checkable, and
free of dynamic evaluation. It also avoids Windows command-line length limits.

### B. ASCII Base64 envelope plus a short bootstrap — rejected

An ASCII bootstrap could survive Big5 stdin and decode a UTF-8 Base64 payload
in memory. Executing the decoded source would require `ScriptBlock.Create`,
`Invoke-Expression`, `PowerShell.AddScript`, or an equivalent dynamic execution
surface. That contradicts the existing evidence-gate security policy and adds
a second source-identity boundary.

### C. Encode the Stage 0 source as Big5 — rejected

This would bind correctness to the ambient locale, abandon the approved UTF-8
source identity, and fail for characters outside the active code page. It would
also leave the child decoder implicit rather than eliminating the boundary.

### D. Compress or shorten `-EncodedCommand` — rejected

This remains sensitive to Windows argv limits and introduces an in-memory
decode/execute path. Reducing whitespace or security checks merely to fit the
transport would weaken Stage 0.

## Authority and non-goals

This design authorizes only:

- this one-file docs-only design commit;
- after written-spec approval, one one-file implementation-plan commit;
- after separate implementation-plan approval, exact materialization and
  static verification of fresh ignored v9 sources;
- one single-use v9 transport-controller invocation and at most one exact Stage
  0 child start;
- after exact Stage 0 PASS, fresh CPU-only/read-only v9 parser-identity TDD,
  dual-parser, comparator, inventory, static, formal, report, and closure work;
  and
- read-only inspection of the already approved repository, executable,
  Security-provider, and preserved-evidence identities required by those gates.

It does not authorize:

- rerunning or invoking any v8 Stage 0 or other predecessor executable source;
- editing, renaming, moving, deleting, completing, or converting predecessor
  evidence;
- stdin command transport, `-EncodedCommand`, command compression, dynamic
  evaluation, dot-sourcing, shell-string fallback, alternate executable/path,
  code-page mutation, console-encoding mutation, profile loading, or retry;
- Docker, GPU, CUDA, WDDM observation, lease, A11 launcher/runtime attempt,
  artifact campaign, model initialization, calibration, validation, RDD,
  Wave 1, or product-source work;
- an `OwnerAuthorizationId` request, synthesis, reservation, or consumption;
- installation, update, repair, replacement, trust-store, execution-policy,
  PATH, `PSModulePath`, host, or certificate mutation; or
- push, merge, rebase, reset, stash, amend, squash, cherry-pick, tag, release,
  publication, remote creation, or modification of another repository.

General owner trust does not widen these boundaries. A new external authority,
destructive action, or expanded runtime scope requires a separate approval.

## Append-only lineage and namespace

This design commit changes exactly:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery-design.md
```

It must be a direct child of:

```text
ab84df410605c824ba42ecd274bbcd6ba4670f19
```

Its exact author and committer are:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Its exact subject is:

```text
docs: design A11 Stage 0 Unicode transport recovery
```

After written-spec approval, the implementation plan may add exactly:

```text
docs/superpowers/plans/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery.md
```

That plan must be a one-file direct child of this design commit with the same
author and committer. It must pin this design commit and blob, the complete v8
lineage, every executable source block, every materialized source byte count and
digest, every phase interface, every file count, and every terminal before any
v9 executable source is materialized.

The fresh ignored runtime namespace is:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-stage0-unicode-transport-recovery/
```

It must be absent when the committed plan is admitted. The plan may initially
materialize exactly two files there:

```text
task-1-stage0-transport-controller-v9.ps1
task-1-stage0-v9.ps1
```

Both files are append-only once their first byte is materialized. A path,
content, encoding, count, digest, or static-policy mismatch freezes the v9
namespace and stops; it is never repaired in place.

The v8 namespace remains absent. No v9 source is copied into it and no v8 name
is reused as a success identity.

## Transport controller

The controller has one purpose: prove and execute the exact Unicode `-File`
boundary. It depends only on the exact current PowerShell 7 process, the two
plan-pinned v9 files, and the plan-pinned Stage 0 executable identity.

Before `Process.Start()` it must prove:

- current process path, version, edition, executable bytes, SHA-256, signature,
  signer, link policy, and ordinary parent chain match the frozen PowerShell 7
  controller identity;
- its own `$PSCommandPath` is the exact canonical controller path and its own
  file bytes match the plan;
- the Stage 0 path is fully qualified, canonical, inside the exact v9 namespace,
  ordinary, not a link/reparse point, and matches the exact plan-pinned bytes;
- the namespace contains exactly the two initial files, with no nested
  directory, stream, link, reparse point, cache, bytecode, temporary, machine,
  or sidecar object;
- the v8 namespace is absent; and
- the exact child executable and working directory are frozen literals.

The controller must use `UseShellExecute=false`, structured `ArgumentList`,
stdout/stderr redirection, and `RedirectStandardInput=true`. Immediately after
the sole successful child start, it closes `StandardInput` without calling any
write method. It may have exactly one `Process.Start()` call site and one
successful child start. There is no PATH lookup, command discovery, fallback
executable, alternate script, retry loop, sleep, environment mutation, or child
input byte.

Stdout and stderr are drained concurrently from their base streams. The
controller must not use line-oriented events or decoded `ReadToEnd()` as the
evidence source. It computes raw byte counts and SHA-256 values in memory,
strictly decodes UTF-8 only after the child exits, and rejects BOM, CR, invalid
UTF-8, missing final LF, extra lines, or any stderr byte.

The implementation plan must set one bounded timeout appropriate for this
read-only gate and freeze it before execution. A timeout permits only termination
of the exact admitted child tree, records the attempt as unprovable, and never
permits retry.

The controller writes no file and emits output only after the exact child
protocol has passed.

## Stage 0 v9 admission

Stage 0 is a new source, process identity, and terminal. It is not a transport
wrapper around the v8 command body. It retains the approved v8 semantic checks
but adds the new lineage and transport self-attestation.

Before PASS it must prove:

- exact v9 design/plan lineage, author, committer, subject, branch, linked
  worktree topology, non-submodule state, empty staging, and clean linked and
  canonical worktrees;
- the preserved v8 design, amendment, plan, source identity, failed terminal,
  absent namespace, and zero downstream-v8-artifact state described here;
- the preserved v7 workspace, exact four-file NO_GO, and required absences;
- the consumed v6 workspace and all other previously frozen evidence conditions
  required by the predecessor design;
- exact controller and Stage 0 `$PSCommandPath`, raw bytes, SHA-256, strict
  UTF-8/LF policy, containment, link policy, and ordinary parent chains;
- exact PowerShell 7 and Windows PowerShell 5.1 executable-file identities;
- exact role-specific Microsoft PowerShell Security provider manifests and
  nested assemblies from the approved amendment; and
- zero repository/product/runtime/evidence mutation and zero parser child start.

Stage 0 must reject any standard-input content. It must not read
`[Console]::In`, `$input`, `Read-Host`, stdin streams, environment payloads, or
command-line source text. `$PSCommandPath` is the only executable Stage 0 source
path.

Its exact PASS family is:

```text
ENTRYV9_STAGE0_PASS|v8=preserved_no_go|transport=file|seed_files=2|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
```

The implementation plan must reproduce that line exactly, including field
order and casing. The controller validates it as the child's sole stdout line,
then emits one separately plan-pinned transport PASS line. The combined parent-
visible stdout is exactly two LF-terminated ASCII lines and stderr is empty.

No later phase may infer PASS from file existence, a matching digest, a decoded
path, or partial output.

## Fresh v9 downstream recovery

An exact Stage 0 PASS authorizes only the fresh v9 continuation defined in the
successor plan. It does not resume the v8 plan in place.

The successor plan must:

- use new v9 filenames, phase IDs, process identities, output terminals,
  manifests, inventories, and report paths;
- treat the v8 plan blocks as reviewed requirements only, never executable
  evidence;
- re-freeze every v9 executable source with exact bytes and digest;
- retain the parser-runtime and Security-provider contracts from the approved
  v8 design and amendment;
- execute fresh parser-identity RED/GREEN and fresh scalar-comparator RED/GREEN
  cycles under distinct v9 identities;
- use exactly two self-attesting parser children in each approved dual-parser
  phase, with no lookup or retry;
- create a new canonical inventory that explicitly preserves the v8 transport
  incident and its absent workspace;
- recompute and freeze all file/workspace/absence counts rather than carrying
  v8 counts forward by assumption;
- run new static admission before one formal entry and independent closure; and
- stop at child-exit recovery without Docker, GPU, A11 runtime, or model work.

No v8 source block may be materialized byte-for-byte and then relabeled v9.
Shared semantic helpers must be freshly authored, named, lineage-bound, and
identity-frozen in the successor plan.

## Error handling and consumption

All checks are fail-closed.

- A dirty worktree, wrong HEAD/lineage/identity, predecessor drift, unexpected
  file, changed source, link/reparse point, noncanonical path, invalid UTF-8,
  source-policy violation, or unapproved process capability stops before the
  controller invocation.
- Once the plan-pinned controller is invoked, that controller identity is
  single-use. Any uncertain controller result freezes the v9 namespace and
  requires a new separately approved design; it is not permission to invoke the
  controller again.
- The Stage 0 attempt is consumed when its exact child process successfully
  starts. Exit failure, timeout, disconnect, truncated capture, unexpected
  stdout/stderr, identity mismatch, or missing terminal is:

  ```text
  ENTRYV9_STAGE0_UNPROVABLE / NO_GO
  ```

- A controller failure before a Stage 0 child start is:

  ```text
  ENTRYV9_TRANSPORT_CONTROLLER_UNPROVABLE / NO_GO
  ```

  It also prohibits retry because the consuming controller invocation is no
  longer independently reproducible.
- The first unexpected downstream v9 observation freezes all existing v9 files
  and stops at the phase-specific `NO_GO` terminal.
- No error permits code-page changes, alternate argv, alternate source,
  alternate executable, deletion, overwrite, cleanup, repair, or tuning to the
  result.

## TDD and verification design

The consumed v8 Stage 0 is the observed RED for the transport defect. It is not
rerun merely to obtain a smaller or more convenient failure. The successor plan
must map its exact root cause to static assertions over the new controller and
Stage 0 before the first v9 invocation.

Pre-invocation verification must prove:

- both source blocks parse with zero errors under the exact PowerShell 7 parser
  and the explicit Windows PowerShell 5.1 parser API without executing them;
- exact strict UTF-8/no-BOM/LF/final-LF bytes and plan-pinned identities;
- the controller contains exactly one structured Stage 0 process start;
- child argv is the exact five-element sequence above and uses the canonical
  absolute Unicode script path;
- `RedirectStandardInput` is exactly `true`, `StandardInput` is closed exactly
  once immediately after the successful start, and no stdin `Write`,
  `WriteLine`, async writer, payload, or alternate input site exists;
- no `-Command`, `-EncodedCommand`, Base64 source payload, command compression,
  dynamic evaluation, dot-source, `UseShellExecute=true`, shell-string child
  execution, PATH lookup, fallback, or retry;
- controller raw-stream capture is concurrent and output decoding occurs only
  after byte capture and process exit;
- Stage 0 reads only its own plan-pinned file as executable source and performs
  no parser child start or write; and
- the repository, predecessor evidence, runtimes, providers, v8 absence, and
  two-file v9 seed inventory are exact immediately before invocation.

The first exact Stage 0 child is the GREEN observation for Unicode transport.
Its self-attested `$PSCommandPath`, own byte identity, exact Unicode repository
root, and exact PASS prove that the file transport preserved the source. A
later direct file measurement cannot substitute for this observation.

After that GREEN, all production comparator and parser controls continue with
fresh RED-before-GREEN tests. Every RED and GREEN is single-use, has a distinct
source/process identity, requires exact exit/stdout/stderr and zero unauthorized
side effects, and is preserved regardless of outcome.

Final verification must include:

- exact design/plan/branch/commit identity and direct-child lineage;
- clean linked and canonical worktrees and empty staging;
- exact v8 failure preservation and absent v8 namespace;
- exact v9 file inventory with no cache, bytecode, temporary, machine, or
  unapproved external object;
- all dual-parser/static/formal/closure terminals and raw evidence identities;
- zero Docker/GPU/A11/runtime/model/owner-authorization action; and
- a final immutable report followed by independent closure.

## Written-spec and implementation gates

Before committing this design, verify:

1. it is the only changed path;
2. its parent is exactly `ab84df410605c824ba42ecd274bbcd6ba4670f19`;
3. that parent has the exact approved author, committer, and subject;
4. the v8 plan blob is
   `4bd91b8b9aeec55c18d8c14056b1176e511be967`;
5. the document is strict UTF-8 without BOM, contains LF only, and has one final
   LF;
6. no placeholder, conflict marker, unresolved choice, retry path, dynamic
   execution path, runtime authority, or invented evidence digest remains; and
7. linked and canonical worktrees were clean before this file and staging
   contains only this exact path at commit time.

The design commit does not authorize plan authoring until the owner approves
this written specification. The future plan commit does not authorize execution
until the owner separately approves that implementation plan and chooses Inline
Execution or another explicitly supported execution mode.

## Success criteria

This recovery design is satisfied only when:

1. this written specification and its implementation plan are one-file,
   direct-child commits with the exact required identity;
2. v8 remains permanently `ENTRYV8_STAGE0_UNPROVABLE / NO_GO` and its runtime
   namespace remains absent from the filesystem;
3. the v9 controller and Stage 0 are exact plan-pinned UTF-8 files and no
   executable source crosses stdin or encoded command transport;
4. structured Unicode argv starts exactly one Stage 0 child and both controller
   and child self-attest exact source/process identities;
5. Stage 0 proves the complete approved evidence envelope with no parser start
   or write and emits its sole exact PASS;
6. all downstream parser-identity, scalar-comparator, inventory, static, formal,
   report, and closure work uses fresh v9 identities and passes exactly once;
7. no Docker, GPU, A11 runtime, model, `OwnerAuthorizationId`, Wave 1, push,
   merge, or release action occurs; and
8. final closure emits exactly:

   ```text
   ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
   ```

Success stops there. Child-exit recovery and every runtime phase remain outside
this design.
