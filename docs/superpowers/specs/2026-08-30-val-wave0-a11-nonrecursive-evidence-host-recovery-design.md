# Wave 0 A11 Non-Recursive Evidence Host Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `23e841a42c5cdb8f0fdd3356c3b8bfc1f52aa02f`

## Purpose

Recover only the A11 controller evidence-capture substrate after the preserved
restart-aware recovery stopped before Docker readiness with:

```text
EVIDENCE_CAPTURE_UNPROVABLE / NO_GO
```

The recovery replaces the recursive, dot-sourced recorder arrangement with a
small non-recursive evidence host and a scope-isolated PowerShell module. It
must prove, using synthetic children only, that exact raw stdout, raw stderr,
process result, and result digest files are created atomically and can be
independently recomputed.

This design does not retry, repair, reinterpret, or complete the failed
`preformal-003` command. It does not execute Docker, inspect Docker process or
pipe state, query a GPU, start an A11 entry child, build an image, run a model,
consume an `OwnerAuthorizationId`, change product code, or execute Tasks 2-8.
Passing this recovery establishes an eligible evidence substrate for a later,
separately reviewed complete Task 1 plan; it is not `ENTRY_GATE_PASS`.

## Preserved failure and authoritative facts

The consumed workspace remains:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/
```

Its report is exactly:

| Property | Value |
|---|---|
| Path | `.superpowers/sdd/2026-08-30-val-wave0-a11-restart-aware-docker-readiness-evidence-capture-recovery/task-1-report.md` |
| Bytes | `6536` |
| SHA-256 | `446a785ed2397ab3340ef2084536382a8cf0c065138879673ac6bd91e9b33c7c` |
| Terminal | `EVIDENCE_CAPTURE_UNPROVABLE / NO_GO` |

The report preserves two distinct defects:

1. `preformal-001-recorder-red-verify` attempted to assign `$Pid`. PowerShell
   variable names are case-insensitive, so this targeted the constant,
   all-scope automatic variable `$PID`. The recorder retained a complete
   `COMMAND_START_FAILURE` result and started no child.
2. The append-only overlay for `preformal-003-recorder-red-verify` dot-sourced
   the base script with `-LibraryOnly`. Dot-sourced parameter binding shared the
   caller scope and changed the overlay's own `$LibraryOnly` value to true. The
   overlay returned before manifest parsing, child creation, or evidence writes.

The outer tool process for `preformal-003` exited 0 with empty stdout and
stderr. All four required machine files are absent:

```text
machine/preformal-003-recorder-red-verify.stdout.bin
machine/preformal-003-recorder-red-verify.stderr.bin
machine/preformal-003-recorder-red-verify.result.json
machine/preformal-003-recorder-red-verify.result.sha256
```

That absence is authoritative. No source edit, replacement command, inferred
payload, reconstructed stream, synthesized result, or retry may be associated
with that command ID or plan. `preformal-004` also remains unexecuted. No Docker
or GPU observation was made by the failed plan.

The previous `CUDA_OBSERVATION_UNPROVABLE / NO_GO`, every earlier A11 attempt,
all owner authorization identities, all artifacts, images, leases, inventories,
digests, reports, and recovery workspaces remain immutable.

## Decision

Adopt a three-layer, non-recursive trust model:

1. **Layer 0: coordination root.** The already frozen signed PowerShell
   executable starts one minimal evidence host with an exact source hash, argv,
   working directory, and environment allowlist. The outer tool result is
   coordination metadata, not child command evidence.
2. **Layer 1: evidence host.** The host imports a `.psm1` module into module
   scope, validates a closed manifest, starts exactly the permitted synthetic
   child, captures both streams concurrently as raw bytes, and publishes the
   four predetermined create-new machine files.
3. **Layer 2: recorded child.** Only the nested process described by the
   manifest is a recorded command. Its machine files are the authoritative
   output and result evidence.

The evidence host is intentionally not required to record itself. Requiring a
host to record its own complete result before that host can be trusted creates
an infinite bootstrap regress and made abrupt-host-loss handling impossible.
Instead, the host is the explicit, minimal trusted computing base. Its behavior
must be constrained statically and proven dynamically with synthetic children
before it can become eligible for a later Task 1.

If a host invocation exits, hangs, throws, or disappears without publishing all
four valid child files, the absence is sufficient only to close the recovery:

```text
EVIDENCE_HOST_UNPROVABLE / NO_GO
```

The outer tool output can never fill a missing child stream or result. A host
capture gap is not eligible for repair, replacement, or retry under the same
implementation plan.

## Alternatives considered

### A. Scope-isolated module plus minimal leaf host — selected

This removes both preserved causes: module scope prevents dot-sourced parameter
leakage, and an automatic-variable assignment gate prevents `$PID` collisions.
The explicit Layer 0 boundary removes self-capture recursion while retaining a
small auditable root of trust.

### B. Generate a complete standalone recorder for every command — rejected

This avoids shared scope but duplicates security-critical process, hashing, and
serialization logic. Copies can drift, and comparing many generated hosts adds
more evidence than it removes.

### C. Build a compiled .NET recorder executable — deferred

A compiled recorder could provide a narrow process boundary, but it would add a
binary build, toolchain identity, dependency, signing, and artifact provenance
problem. That is disproportionate to the PowerShell scope-isolation defect and
would expand the approved repository surface.

## Authority and non-goals

This recovery is authorized to:

- create one new docs-only design commit and, after written-spec approval, one
  docs-only implementation-plan commit;
- create a fresh ignored recovery workspace with `apply_patch`;
- author immutable PowerShell module, host, manifest, tests, static verifiers,
  synthetic child fixtures, briefs, and reports in that workspace;
- start only frozen signed PowerShell processes required for static checks and
  synthetic evidence-host tests; and
- create only predetermined synthetic machine-evidence paths using the evidence
  host's create-new implementation.

It is not authorized to:

- modify or delete any existing tracked or ignored file;
- execute or inspect Docker CLI, Docker Desktop process, named-pipe, WSL,
  Hyper-V, image, container, builder, cache, or volume state;
- execute `nvidia-smi`, CUDA, a model, a CPU baseline, dependency diagnostic,
  A11 launcher, entry child, validation run, Wave 1, or Tasks 2-8;
- create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`;
- change any artifact, image, lease, preserved-attempt registry, inventory,
  digest, historical report, or external evidence directory;
- modify product code or the existing seven-file implementation allowlist;
- create a remote, push, merge, tag, release, amend, rebase, reset, stash, or
  touch another repository.

Broad owner trust does not expand these boundaries. Any newly required external
authority stops the recovery for explicit review.

## Append-only lineage and workspace

The design commit must:

- be a one-file direct child of
  `23e841a42c5cdb8f0fdd3356c3b8bfc1f52aa02f`;
- change only this design path;
- use author and committer
  `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`; and
- leave linked and canonical worktrees clean.

After owner approval of this written specification, its implementation plan
must be a one-file direct child of the design commit with the same identity.
Execution may begin only from the exact plan commit and a clean repository.

The implementation plan must use this fresh ignored workspace:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-nonrecursive-evidence-host-recovery/
```

Before creating it, entry eligibility must prove the exact path absent, linked
worktree topology correct, branch exact, plan lineage exact, staging empty,
tracked and untracked scope empty, canonical worktree clean, and every directly
consumed previous file equal to its frozen byte count and SHA-256.

All new human-authored files are created with `apply_patch`. Once a source,
manifest, command ID, or report is used by an executed process, it is immutable.
A pre-execution authoring defect may be corrected only by a new append-only path
and new identity. Any post-start capture defect closes the plan and cannot be
superseded.

## Component 1: evidence module

The recorder core is a human-authored `.psm1` file with these structural rules:

- no script-level `param` block;
- no dot-source expression;
- no top-level `return`, `exit`, process start, file write, console write, or
  environment mutation;
- no `Invoke-Expression`, `Start-Process`, shell command string, script-string
  interpolation, alias-dependent command, or dynamic code download;
- no assignment to automatic, constant, or preference variables;
- no mutation of caller variables or global/session state;
- one explicit, exact `Export-ModuleMember -Function` list; and
- only deterministic helper definitions at import time.

The implementation plan must freeze the exact export names. At minimum, the
module separates these responsibilities:

- canonical manifest decoding and closed-field validation;
- canonical path and containment validation;
- executable, source, and environment identity validation;
- create-new raw file creation;
- concurrent raw stdout/stderr process capture;
- closed result-object creation and canonical JSON serialization;
- SHA-256 computation; and
- machine-inventory verification.

The process runner uses `System.Diagnostics.Process` directly with
`UseShellExecute = false`. It passes argv using `ProcessStartInfo.ArgumentList`
and never a shell command string. Standard input is closed unless the manifest
declares an exact frozen byte payload. Standard output and error are drained
concurrently as bytes so either stream cannot deadlock the other.

Process identity variables use descriptive names such as `$ChildProcessId`.
The static gate treats PowerShell variable names case-insensitively and rejects
assignment to at least `PID`, `HOME`, `Host`, `Error`, `Args`, `Input`,
`Matches`, `MyInvocation`, `PSBoundParameters`, `PSScriptRoot`,
`PSCommandPath`, `LASTEXITCODE`, and every variable whose live options include
`Constant` or `ReadOnly`.

## Component 2: minimal evidence host

The host is a separate `.ps1` leaf executable. Its parameter names use the
`A11Host` prefix and may identify only the frozen manifest and module paths. It:

1. resolves its own and the module's canonical ordinary-file paths;
2. checks their exact byte counts and SHA-256 values against Layer 0 frozen
   coordination inputs;
3. imports the module by absolute path with `Import-Module -Scope Local
   -PassThru`;
4. proves the imported module path and exact exported-function set;
5. validates the manifest before any child or machine-file creation;
6. starts exactly the manifest-permitted child count;
7. delegates raw capture and result publication to the module; and
8. returns one closed host terminal.

The host must not dot-source the module or another executable script. It must
not contain a `LibraryOnly` mode, self-capture buffer, recursive host invocation,
fallback recorder, replacement manifest, alternate executable, or console
reconstruction path.

The host's console output is informational. A PASS is derived only from complete
child machine files that an independent read-only verifier recomputes. Empty,
truncated, or unavailable outer console output never converts missing files into
evidence.

## Component 3: closed manifest and machine files

Every host invocation consumes one immutable canonical compact UTF-8 JSON
manifest with one terminal LF. The implementation plan freezes exact property
order and schemas. A child command record contains at least:

```text
schema_version
command_id
purpose
host_source_path
host_source_byte_count
host_source_sha256
module_source_path
module_source_byte_count
module_source_sha256
executable_path
executable_byte_count
executable_sha256
argv
working_directory
environment_allowlist
stdin_policy
stdout_capture_path
stderr_capture_path
result_path
result_digest_path
timeout_policy
permitted_child_count
command_source_paths
command_source_byte_counts
command_source_sha256
```

All paths are canonical absolute paths. Executable and source identities are
verified before child start. Unknown, duplicate, missing, reordered, linked,
escaping, colliding, or mismatched fields stop with zero child starts and zero
machine files.

For each synthetic command ID, the only allowed machine writes are:

```text
machine/<command-id>.stdout.bin
machine/<command-id>.stderr.bin
machine/<command-id>.result.json
machine/<command-id>.result.sha256
```

Every destination must be absent and remain beneath the exact fresh workspace.
Files use create-new/no-clobber semantics. The host never deletes, truncates,
appends, moves, renames over, repairs, or rewrites a path. It closes and flushes
the raw streams before serializing the result, closes the result before
publishing its digest, and never treats partial publication as PASS.

The result is canonical compact UTF-8 JSON with one terminal LF. It freezes
manifest identity, executable identity, argv, environment, start and completion
timestamps, monotonic values, child PID, exit code, timeout/start-exception
state, raw-stream byte counts and SHA-256 values, and terminal. The digest file
contains the lowercase SHA-256 of the exact result bytes plus one LF.

## Component 4: explicit bootstrap boundary

The evidence host cannot prove its own first correct execution without assuming
it already works. This design makes that bootstrap boundary explicit rather
than hiding it in recursive self-capture.

The implementation plan must follow test-first ordering:

1. create an immutable RED subject module that lacks the required recorder
   behavior;
2. create the behavioral and structural tests before the GREEN module;
3. execute one exact Layer 0 RED test command through the frozen signed
   PowerShell executable and require failure only for the missing behavior;
4. create, at new paths, the GREEN module and minimal host;
5. pass static AST and identity gates before the host may start a child; and
6. run the complete behavioral suite as a Layer 2 child through the host.

The RED command's outer tool result is bootstrap coordination evidence only.
It cannot admit Docker, GPU, entry, or later A11 work. If its exact intended RED
cannot be established, the terminal is:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
```

The GREEN suite is authoritative only when its four machine files are complete
and independently verified. Implementation source is never edited in response
to a GREEN observation. Any defect discovered after the first GREEN host child
starts is preserved and closes this plan; it requires a new reviewed recovery,
not tuning against the observed result.

## Component 5: static and behavioral proof

Before the first host child, a read-only AST verifier must prove:

- host and module parse under frozen PowerShell 7.6.4;
- Windows PowerShell 5.1 parsing is also clean for compatible syntax;
- the module has no script-level parameters or top-level actions;
- neither source contains dot-sourcing or forbidden dynamic execution;
- every assignment target passes the case-insensitive automatic-variable gate;
- host parameter names and module exports are exact;
- import uses the exact absolute module path and local module scope;
- process construction uses no shell and exact argv-array semantics;
- all machine write sites enforce create-new and workspace containment; and
- no Docker, GPU, launcher, model, repository mutation, or external-artifact
  command appears in executable source or manifests.

The behavioral suite must cover at least:

- caller variables named `LibraryOnly` and `PID` remain unchanged after module
  import and host execution;
- exact exported-function identity and absence of import-time side effects;
- raw stdout containing UTF-8, non-ASCII, NUL, and no-terminal-newline bytes;
- raw stderr captured simultaneously with high-volume stdout;
- zero, nonzero, timeout, and process-start-failure result records;
- exact argv boundaries including spaces, quotes, empty arguments, and Unicode;
- exact environment allowlist and closed standard input;
- canonical JSON field order, UTF-8 encoding, terminal LF, and SHA-256 values;
- missing, extra, linked, escaping, duplicate, or colliding paths rejected before
  child start;
- preexisting output rejected with original bytes unchanged;
- partial or absent machine publication never accepted;
- unexpected child count rejected; and
- independent byte/digest recomputation matches every published result.

Synthetic fixtures may do no work beyond deterministic byte emission, bounded
waiting, controlled exit, and local ignored-workspace collision tests. They may
not inspect host services, network, Docker, GPU, repository state, or external
artifacts.

## Component 6: unique identities and no retry

The implementation plan assigns a new namespace that cannot collide with any
earlier `preformal-*` or readiness command. Exact names are frozen by that plan
and must include a monotonically ordered host-version prefix.

Each scheduled RED, static, GREEN, negative, and verification role has one
unique source path, manifest path, command ID, and expected machine inventory.
No earlier source, manifest, ID, or machine destination is reused.

Multiple planned synthetic commands are not retries when they exercise distinct
frozen cases with unique IDs. A failed case is never rerun. The first unexpected
host gap, malformed result, unplanned child, timeout outside the expected
timeout fixture, identity mismatch, or verification mismatch closes the entire
recovery.

## Terminals and continuation

The implementation plan publishes the first applicable exact terminal:

```text
EVIDENCE_BOOTSTRAP_UNPROVABLE / NO_GO
EVIDENCE_HOST_STATIC_REJECTED / NO_GO
EVIDENCE_HOST_UNPROVABLE / NO_GO
EVIDENCE_CHILD_CAPTURE_UNPROVABLE / NO_GO
EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED
```

`EVIDENCE_HOST_RECOVERY_PASS / ENTRY_GATE_NOT_AUTHORIZED` requires:

- exact clean entry and lineage;
- immutable RED evidence with the intended failure;
- complete static gates;
- exact module isolation and host identity;
- every scheduled synthetic child result complete and independently verified;
- no missing or extra workspace file;
- a complete apply-patch-authored report and read-only closure verifier;
- linked worktree unchanged except the approved documentation lineage;
- canonical worktree clean; and
- proof that Docker, GPU, entry child, CPU baseline, dependency diagnostic,
  model, formal runtime, OwnerAuthorizationId, Tasks 2-8, push, merge, and
  release were not used.

This PASS does not resume the stopped plan and does not authorize its
`preformal-003`, readiness observation, or entry child. A later plan must consume
the new host/module/test/report identities immutably, re-run the complete Task 1
entry gate from a fresh workspace and fresh IDs, and retain every inherited
Docker, launcher, artifact, image, lease, WDDM, CPU, and one-shot rule.

Any `NO_GO` preserves the new workspace and stops for redesign. It is never
converted into a PASS by explanation, inferred output, or owner preference.

## Review and commit gates

Before committing this written specification, require:

1. HEAD and branch equal the required parent and branch;
2. linked and canonical worktrees were clean before authoring;
3. the new design path was absent;
4. only this path changed;
5. placeholder, conflict-marker, line-ending, whitespace, and Markdown-structure
   checks pass;
6. the document names both preserved root causes and all four absent files;
7. the document explicitly removes self-capture and dot-sourcing;
8. scope includes no Docker, GPU, entry child, runtime, or product change;
9. the design is self-reviewed against the approved architecture; and
10. the commit author, committer, parent, and changed path are exact.

After the commit, stop for owner review of the written specification. Invoke
the `writing-plans` workflow only after explicit written-spec approval.

## Success criteria

This design is successful when a later implementation can prove a small,
scope-isolated evidence host with synthetic machine evidence and without
recursive trust. It deliberately trades the impossible promise of recorder
self-attestation for an explicit, frozen, statically constrained root of trust.

It does not claim A11 entry, Docker readiness, CUDA idleness, CPU success,
implementation completion, dependency success, or formal runtime success.
