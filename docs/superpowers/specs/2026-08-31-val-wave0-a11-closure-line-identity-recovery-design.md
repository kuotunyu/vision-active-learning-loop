# Wave 0 A11 v14 Closure Line-Identity Recovery Design

## Status and authority

The owner approved recommended approach A on 2026-08-31 and authorized this
design, written specification, implementation plan, and end-to-end Inline
Execution. The authority also covers deletion of the 52 pytest-generated
untracked `.pyc` files and their 17 empty `__pycache__` directories. That
cleanup completed only after exact path, type, containment, and count checks;
both linked and canonical worktrees were clean immediately afterward.

This recovery is limited to the closure-only defect observed after the v13
Stage 0 observation. It is not a new A11 Tasks 7-8 attempt, does not consume an
`OwnerAuthorizationId`, and authorizes no Docker, WSL, GPU, CUDA, model,
network, Wave 1, push, merge, release, or other-repository operation.

Frozen repository identity:

- linked worktree: `<repo>\.worktrees\wave0-model-contract`;
- canonical read-only worktree: `<repo>`;
- branch: `codex/wave0-model-contract`;
- v13 design commit: `84b0f64fa5565d785e32fe3fbe5de1dc473f23aa`;
- v13 plan commit: `62fa510c335c24e6b8bec81083aa93339913b639`;
- v13 plan blob: `f8da0fb7c166c95a97cef00d77bae4deab1cb99b`.

## Preserved v13 result

The v13 controller was invoked exactly once. The child started exactly once,
no retry occurred, the process exited zero, stderr was empty, and parent-visible
stdout was the exact two-line UTF-8/LF payload captured in the task record:

```text
ENTRYV13_STAGE0_PASS|v12=preserved_plan_no_go|v11=preserved_no_go|v10=preserved_no_go|v9=preserved_no_go|v8=preserved_no_go|output=raw_utf8_lf|seed_files=2|v11_files=2|v10_files=3|v7_files=4|runtimes=2|providers=2|linked=clean|canonical=clean
ENTRYV13_RAW_BYTE_TRANSPORT_PASS|child_bytes=utf8_lf|parent_bytes=utf8_lf|stdin_bytes=0|starts=1|retries=0
```

The subsequent closure command was invoked exactly once and stopped with:

```text
closure v11 source line rejected
```

The observation PASS and closure NO_GO are both immutable. v14 must not rerun,
reuse, wrap, edit, or reinterpret the v13 controller or child. The v13 runtime
workspace remains an exact two-file preserved inventory:

```text
SOURCE_IDENTITY|task-1-stage0-plan-identity-controller-v13.ps1|31491|dc57b046223a15d1cf2f862a7e82062666b95c2343138901ea545ed0851e8086
SOURCE_IDENTITY|task-1-stage0-v13.ps1|24403|18b7c0d097efed27805908c5892939257e561b124f0a0eaf12ab338879ecd967
```

No exact v13 failure terminal was defined for this post-observation closure
exception. This document therefore preserves the literal exception and does
not synthesize a terminal retroactively.

## Root cause

The v13 final closure reads the preserved v11 controller and compares line 171
with an ordinal string. The actual line is 142 UTF-8 bytes, has SHA-256
`1ef50cf9ad6633f4da88ea82c2ca16c7abd9864416ae38510806638b88a2fd2b`,
and contains exactly four leading ASCII spaces:

```text
    if (Test-Path -LiteralPath $V8Workspace -or Test-Path -LiteralPath $ConsumedV6Workspace) { throw 'consumed predecessor namespace exists' }
```

The v13 closure expectation begins at `if` and omits those four spaces. The
preserved file itself remains 28,071 bytes with SHA-256
`e15b9115da4800a4833338a5b756e4cce54a3a1c38e3681705c762ef7f65ecb9`.
Thus the closure rejected a line-identity literal, not the v13 observation,
source identities, transport result, or v11 semantic evidence.

## Decision

Use a fresh v14 closure-only namespace and one plan-pinned PowerShell verifier.
The verifier reads immutable Git and filesystem evidence, checks the exact
four-space v11 line identity, and emits one new v14 recovery terminal. It does
not start a child process and does not call the v13 sources.

The design commit must be a direct child of v13 plan commit
`62fa510c335c24e6b8bec81083aa93339913b639`. The implementation-plan commit
must be a direct child of the design commit. Both commits use:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Exact subjects:

```text
docs: design A11 closure line identity recovery
docs: plan A11 closure line identity recovery
```

## Fresh namespace and output contract

The ignored runtime workspace is:

```text
<repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-31-val-wave0-a11-closure-line-identity-recovery
```

It contains exactly one ordinary file:

```text
task-1-v13-closure-line-identity-v14.ps1
```

No report, transcript, marker, result, manifest, cache, temporary file,
subdirectory, copied v13 source, or alternate verifier is permitted.

On success the verifier writes exactly one LF-terminated line:

```text
ENTRYV14_CLOSURE_LINE_IDENTITY_PASS|v13_observation=preserved_pass|v13_closure=preserved_no_go|v11_line=171|leading_spaces=4|linked=clean|canonical=clean
```

The execution wrapper may close only this recovery with:

```text
ENTRYV14_RECOVERY_PASS / A11_RUNTIME_NOT_AUTHORIZED
```

Neither terminal changes the preserved v13 closure result or authorizes a new
A11 runtime attempt.

## Verifier contract

Before emitting its terminal, the v14 verifier must fail closed unless all of
the following are true:

1. the working directory, branch, HEAD identity, author/committer identity,
   exact plan subject, direct parent, and plan blob match the committed v14
   plan;
2. the v14 plan records the v13 observation and closure facts exactly once;
3. the v13 plan/design commit chain, subjects, identities, and plan blob match
   their frozen values;
4. the v13 workspace contains exactly the two ordinary source files with the
   byte counts and SHA-256 values above;
5. the unmaterialized v12 namespace remains absent;
6. the v11 controller remains exactly 28,071 bytes with its frozen SHA-256;
7. line 171 is ordinal-equal to the exact four-space string, contains exactly
   four leading ASCII spaces, is 142 UTF-8 bytes, and has the frozen line hash;
8. the stale zero-indent expectation is absent from the v14 verifier;
9. linked and canonical worktrees are clean except for the one ignored v14
   source itself;
10. the verifier AST contains no process-start, external invocation, dynamic
    evaluation, write, Docker, GPU, model, network, or authorization surface.

The verifier reads only. It may write its exact terminal to stdout and nothing
else. Any failed assertion, unexpected output, nonzero exit, stderr byte,
identity difference, or side effect is a fresh preserved v14 NO_GO. The source
is not repaired or retried after formal invocation.

## TDD and execution sequence

The implementation plan freezes the complete verifier source plus its decimal
UTF-8/LF byte count and lowercase SHA-256 before materialization.

RED reads the committed v13 plan and exact v11 source as data. It extracts the
v13 closure's zero-indent expectation and proves that it is not ordinal-equal
to actual line 171, while the actual line has four leading spaces and the
frozen identity above. RED starts no process.

Materialization uses exactly one `apply_patch` call and creates only the one
approved source. Admission verifies path containment, ordinary file type,
single data stream, UTF-8 without BOM, LF-only endings, one final LF, exact
byte count, and exact SHA-256.

GREEN parses and reads the admitted source as data. It proves the corrected
four-space expectation and static no-start/no-write/no-runtime topology. A
separate invocation-boundary check repeats identities and cleanliness before
the formal call.

The verifier is then invoked exactly once with the plan-pinned PowerShell 7
executable. Exit code, stderr bytes, stdout bytes, file identity, inventory,
and both worktrees are checked once in final closure. Any failure preserves all
evidence and stops without retry.

## Stop conditions

Stop immediately on the first preserved NO_GO, a newly required external
authorization, or a newly required destructive action. Otherwise proceed
through design commit, plan commit, RED, materialization, GREEN, boundary,
single invocation, and closure without further approval pauses.
