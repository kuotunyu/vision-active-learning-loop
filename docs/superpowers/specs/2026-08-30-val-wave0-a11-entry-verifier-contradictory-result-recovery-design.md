# Wave 0 A11 Entry-Verifier Contradictory-Result Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `68cd174c64a17e4b8c42771caf046ecb23c3eb06`

## Purpose

Recover the entry-verification control boundary from one preserved contradictory
result without retrying, overwriting, or retroactively passing that attempt.
The successor proves a persistent, behaviorally tested scalar identity
comparator and uses it in one fresh read-only formal inventory verification.

The consumed recorder child-exit recovery plan is:

| Object | Identity |
|---|---|
| Plan commit | `68cd174c64a17e4b8c42771caf046ecb23c3eb06` |
| Plan blob | `d36d0b09dbb4ff19fe17c18c139e4897dee41cfe` |
| Plan path | `docs/superpowers/plans/2026-08-30-val-wave0-a11-recorder-child-exit-evidence-capture-recovery.md` |

Its first complete read-only entry command stopped on:

```text
inventory hash rejected: <repo>\.worktrees\wave0-model-contract\.superpowers\sdd\2026-08-30-val-wave0-a11-bootstrap-path-resolution-recovery\task-1-evidence-module-red-v3.psm1
```

No v6 execution workspace was created and no observer, formal static source,
recorder child, host, Docker, GPU, A11 entry, product, model, or runtime command
ran. A later independent read-only measurement found that the named artifact
was still exactly 97 bytes with SHA-256:

```text
c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136
```

That later observation does not convert the failed entry to PASS. It proves
only that the rejection and the retained artifact identity are contradictory.
The successor records both facts and never presents either as proof of the
other.

The success boundary of this design is intentionally narrow:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Success does not resume the consumed v6 plan and does not authorize a child-
exit observer, evidence host, Docker, GPU, A11 entry, or runtime attempt.

## Root cause and control defect

The failed entry logic was submitted as an ad hoc in-memory command. Its full
source did not exist as a frozen artifact before it evaluated the preserved
inventory. The error path was retained, but there is no immutable verifier
source or typed comparison record from that evaluation with which to determine
whether the cause was command authoring, value shape, coercion, or evaluation.

The defensible root cause is therefore a control defect, not predecessor
artifact drift: identity-critical comparison was allowed to occur before its
implementation, tests, types, and per-item actual/expected record were frozen.
The successor removes that sequencing defect. It does not claim a more
specific mechanism that the available evidence cannot prove.

## Decision

Use a standalone, two-stage entry-verifier recovery milestone.

1. A minimal Stage 0 admits only Git lineage, linked-worktree isolation, clean
   state, fresh workspace absence, and the preserved absence of the consumed
   v6 workspace. It performs no predecessor byte or digest comparison.
2. After Stage 0 PASS, human-authored ignored files are created with
   `apply_patch` under one fresh `entryv7-*` workspace.
3. A behavioral test first catches an intentional equal-scalar rejection.
4. A side-effect-free comparator then proves exact scalar type, byte-count,
   digest-format, and ordinal digest equality behavior.
5. A canonical human-authored inventory freezes every v2-v5 path, byte count,
   SHA-256, absent machine path, frozen PowerShell identity, and the consumed
   contradiction facts.
6. A separately authored static verifier admits the production comparator and
   formal entry source before either consumes predecessor inventory.
7. The formal entry verifier runs exactly once, produces an in-memory
   actual/expected record for every file, and writes nothing.
8. An independent closure verifies the frozen evidence and one immutable
   report, publishes the success boundary, and stops.

## Alternatives considered

### A. Dedicated entry-verifier milestone — selected

This isolates the failed control boundary and produces one reusable, audited
entry fact before any observer or host behavior can occur. It adds one approval
cycle but has the smallest failure surface and clearest evidence boundary.

### B. Fold the verifier into a complete `hostv7-*` recovery — rejected

This would reduce documentation cycles, but it would combine comparator TDD,
four predecessor inventories, observer admission, recorder RED, GREEN capture,
and machine evidence in one formal attempt. A later host failure would make it
harder to distinguish entry proof from runtime proof and would weaken the one-
gated-milestone rule.

### C. Treat the later direct hash measurement as a retroactive PASS — rejected

The later measurement did not execute the same frozen verifier because no such
verifier artifact existed. Using it to pass the consumed attempt would rewrite
the observed result and violate the explicit no-retry/no-overwrite authority.

## Authority and non-goals

This recovery may:

- create this one-file docs-only design commit and, after written-spec
  approval, one one-file docs-only implementation-plan commit;
- execute one minimal read-only Stage 0 from the later approved plan;
- create one fresh ignored workspace with `apply_patch` for every human-
  authored test, RED subject, module, canonical inventory, verifier, static
  gate, closure source, and report;
- execute frozen signed PowerShell for comparator RED, comparator GREEN,
  parser/static checks, one formal entry verification, and closure; and
- read bytes, metadata, hashes, link properties, Git state, and Authenticode
  state required by those gates.

It may not:

- rerun, reinterpret, repair, replace, or declare PASS for the failed v6 entry;
- create the consumed v6 workspace or reuse any v6 command identity;
- execute, modify, delete, rename, replace, copy over, or use any v5/v4/v3/v2
  source as a child or command;
- modify any preserved workspace, artifact, digest, report, machine file, or
  absence fact;
- create machine evidence, child-process evidence, sidecars, transcripts, or
  runtime output;
- inspect or execute Docker CLI, Docker Desktop processes, WSL, Hyper-V,
  builders, images, containers, caches, volumes, GPU, `nvidia-smi`, CUDA, CPU
  baseline, dependencies, models, A11 launcher, entry child, product task,
  Wave 1, or runtime;
- create, consume, infer, increment, or synthesize an `OwnerAuthorizationId`;
- modify product code, another repository, a remote, or Git history; or
- push, merge, tag, release, amend, rebase, reset, stash, or delete evidence.

General owner trust does not broaden these boundaries.

## Append-only lineage and workspace

This design commit changes only this file and is a direct child of:

```text
68cd174c64a17e4b8c42771caf046ecb23c3eb06
```

The implementation plan, after written-spec approval, is a one-file direct
child of this design commit. Author and committer for both are exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

Execution uses only this fresh path:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery/
```

The namespace for commands and terminals is `entryv7-*`. No v6, `hostv6-*`,
preformal, readiness, entry-runtime, CUDA, CPU, dependency, owner, or model
identity is reused.

Before Stage 0, the new workspace and consumed v6 workspace are absent. Stage 0
itself creates nothing. After Stage 0 PASS, the implementation plan may create
only the exact human-authored files it enumerates. No `machine/` directory is
permitted at any time.

The human-authored execution inventory is exactly nine files:

| Path | Responsibility |
|---|---|
| `task-1-stage0-audit-v7.ps1` | Immutable audit copy of the admitted Stage 0 source and result; never executed. |
| `task-1-scalar-identity-tests-v7.ps1` | One RED and one GREEN behavioral contract. |
| `task-1-scalar-identity-red-v7.psm1` | Intentional equal-scalar rejection subject. |
| `task-1-scalar-identity-green-v7.psm1` | Side-effect-free production comparator. |
| `task-1-preserved-inventory-v7.json` | Canonical incident, executable, inventory, and absence record. |
| `task-1-entry-verifier-v7.ps1` | One-shot formal read-only inventory verifier. |
| `task-1-static-verifier-v7.ps1` | Parser, AST, type-flow, canonicalization, and forbidden-action gate. |
| `task-1-closure-verifier-v7.ps1` | Independent read-only closure before and after the report. |
| `task-1-report.md` | Immutable final evidence index and first exact terminal. |

No additional source, fixture, brief, manifest, transcript, sidecar, result,
digest, temporary file, or machine file is allowed.

## Stage 0 admission

Stage 0 is deliberately too small to reproduce the failed comparison. It
verifies only:

- branch `codex/wave0-model-contract`;
- approved design/plan direct-child lineage and exact commit identity;
- linked worktree topology and non-submodule state;
- empty linked and canonical status and staging;
- new entryv7 workspace absence;
- consumed v6 workspace absence; and
- exact frozen signed PowerShell bytes, digest, and valid signature.

It does not enumerate, hash, or compare v2-v5 files. Its sole success is:

```text
ENTRYV7_STAGE0_PASS|workspace=absent|v6=absent|linked=clean|canonical=clean
```

Any Stage 0 failure stops with the workspace absent. Stage 0 is not entry proof
and cannot be consumed by a later child-exit plan.

After Stage 0, an audit copy of its exact source and result is authored into the
fresh workspace but is never executed. The implementation plan must pin the
Stage 0 command text and hash before execution so a tool-call reconstruction is
not the only retained source.

## Scalar comparator contract

The comparator module is side-effect free and exports exactly:

```powershell
Compare-A11ScalarIdentity
```

Its four inputs are received as objects so invalid collection shapes can be
rejected before PowerShell binding or comparison can coerce them:

```text
ActualByteCount
ExpectedByteCount
ActualSha256
ExpectedSha256
```

The comparator requires:

- both byte counts have runtime type `System.Int64`, are nonnegative, and are
  compared as scalar integers;
- both digests have runtime type `System.String` and match exactly 64 lowercase
  hexadecimal characters;
- neither input is an array, collection, enumerable wrapper, null, or converted
  display string; and
- digest equality is evaluated only by
  `[StringComparer]::Ordinal.Equals($ActualSha256, $ExpectedSha256)`.

It returns one in-memory record with exact property order:

```text
actual_byte_count
expected_byte_count
byte_count_match
actual_sha256
expected_sha256
sha256_match
identity_match
```

It emits no console output and writes no file.

## Comparator TDD

The behavioral test and intentional RED module are authored before the GREEN
module. The test names one mutation: an equal scalar identity is rejected even
though both typed values are exact.

The intentional RED returns `identity_match=false` for one exact 97-byte,
frozen-hash pair. The test requires that behavior and emits only:

```text
SCALAR_IDENTITY_TEST_RED_PASS|fault=equal_scalar_rejected
```

The RED module and its test invocation run exactly once and are never edited or
reused for formal verification.

After exact RED, the GREEN module is created. The same frozen behavioral test
proves, with literal expectations:

1. exact `Int64` byte counts and exact scalar hashes match;
2. an object-array hash is rejected before comparison;
3. an object-array byte count is rejected before comparison;
4. one changed hash nibble does not match;
5. one changed byte count does not match;
6. uppercase, short, long, whitespace, null, and non-string hashes are rejected;
7. negative and non-`Int64` byte counts are rejected; and
8. the returned record has the exact closed property order and Boolean types.

GREEN emits only:

```text
SCALAR_IDENTITY_TEST_GREEN_PASS|cases=8|comparison=ordinal|collections=rejected
```

Any unexpected RED or GREEN output, exit, exception, or side effect is:

```text
ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO
```

The consumed comparator subject is never edited or rerun.

## Canonical preserved-inventory record

The inventory is one compact strict UTF-8 JSON document without BOM plus one
LF. It is human-authored with `apply_patch`; it is never generated from the
filesystem. Its closed root property order is:

```text
schema_version
inventory_id
source_plan_commit
failed_attempt
frozen_powershell
workspaces
absent_paths
```

Fixed values include `schema_version=1`,
`inventory_id=entryv7-preserved-inventory-001`, and source plan commit
`68cd174c64a17e4b8c42771caf046ecb23c3eb06`.

`failed_attempt` records, in closed property order, the consumed plan/blob,
reported path, reported rejection class, later 97-byte observation, later
matching SHA-256, `success_terminal_emitted=false`, and
`retroactive_pass_allowed=false`.

`frozen_powershell` records the absolute executable path, 301,368 bytes,
SHA-256 `db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f`,
and required valid signature.

`workspaces` contains exactly four ordered objects: v5, v4, v3, then v2. Each
object has exact property order `generation,path,file_count,files`; each file
has exact property order `path,byte_count,sha256`. The counts are 8, 5, 4, and
3, for exactly 20 immutable files. The plan must reproduce every already
approved literal byte count and SHA-256, not discover expected values from the
live filesystem.

The 20 expected file records are exactly:

| Generation | Path | Bytes | SHA-256 |
|---|---|---:|---|
| v5 | `task-1-ancestor-chain-red-v5.ps1` | 1,436 | `dfa8f9b572ff31439b8198acd014d53c0efbc408ab50cbce156423293e92b9ac` |
| v5 | `task-1-ancestor-chain-tests-v5.ps1` | 8,798 | `07dc9df03102dd64c6d79326c25281fcd143246618777a0c55abfb917623ca09` |
| v5 | `task-1-bootstrap-command-static-v5.ps1` | 20,783 | `8ae484662c7f5165b721ad70e3213f1aad43f4b5d238af5282e6ecda1df051f9` |
| v5 | `task-1-bootstrap-red-brief-v5.md` | 5,003 | `5d5a95ef800a34f5cfb9a65833367191bde725f6741bb2d79fce0c626644da27` |
| v5 | `task-1-entry-gate-v5.ps1` | 6,250 | `2d1b8f10842d6abdc8bea772d258f593b733b2fa7a8af21522c569199fb7dee1` |
| v5 | `task-1-evidence-module-red-v5.psm1` | 97 | `efafc826c36991da1ba816180e85b4f3dd6177a635ebb1b1d8b48061eeb53071` |
| v5 | `task-1-evidence-tests-v5.ps1` | 12,339 | `21b59e3e4264706d095c5135a9c1a71fc7ada45dfb2731c02badf0134818c92b` |
| v5 | `task-1-red-command-v5.json` | 1,437 | `8f500139120bdbe88dc0b648f55dbf224f5d2db950cc7eb42bf67c3d8bc0cbd3` |
| v4 | `task-1-bootstrap-command-static-v4.ps1` | 12,532 | `e17d575e0ff8287ea7424c28c08b14bd7625e5603651b07f0283e4a5ced72a68` |
| v4 | `task-1-entry-gate-v4.ps1` | 5,562 | `8e35c0ab663116587448ecb6840bf6c6ecc876c367fe25f4fa86a3e2616b764d` |
| v4 | `task-1-evidence-module-red-v4.psm1` | 97 | `dc989723f0d0149c5f731fc4d8505d8f117653120cfa61bcc828ed7239a46edb` |
| v4 | `task-1-evidence-tests-v4.ps1` | 8,824 | `aca02e4a213baa1703eec9c0a82a638240de46ecfb77cd0b944c3ab778f7a863` |
| v4 | `task-1-red-command-v4.json` | 1,461 | `b7b4372d4164c5a248c660670ab8afcec19837885eff830f8bc99a90cab06bc6` |
| v3 | `task-1-bootstrap-path-static-v3.ps1` | 7,521 | `636f64e93d1efa6989fbdc60255918fde777a8a35233a46708c25eb2caaa61b9` |
| v3 | `task-1-entry-gate-v3.ps1` | 5,151 | `fbcbdd427c86125eaed73c7ac607dc549ed453e48fec9873bb3a2e7768280b19` |
| v3 | `task-1-evidence-module-red-v3.psm1` | 97 | `c8f5ccbd382ead232f759a4a4a4a69bf16f3121a2c511cc2b66e729e5451d136` |
| v3 | `task-1-evidence-tests-v3.ps1` | 9,012 | `db17560f09113173d491b7c3d0e041d84a411e38d864ba71ae8bfc7156981c9c` |
| v2 | `task-1-entry-gate.ps1` | 3,541 | `3225e909752f3420aab62e3acd9fa2b0dd560ba382973d20f7a9843c9e872a1b` |
| v2 | `task-1-evidence-module-red.psm1` | 103 | `a4e61e11e8802da9ccc02b57732d75623df3b2b6ff9275377d46fc123b8c66dc` |
| v2 | `task-1-evidence-tests.ps1` | 4,420 | `8460df3c0b017f2dcfb0eec286b4577dd446a0953d45e3cb4f80ebf5bf7cdf65` |

`absent_paths` contains the four frozen `preformal-003-recorder-red-verify.*`
machine paths, the four preserved workspace `machine/` directories, the
consumed v6 workspace, and the fresh entryv7 `machine/` directory: exactly 10
ordered absence records.

The inventory's byte count and SHA-256 are frozen before the formal verifier
source exists.

## Static admission

A human-authored static verifier is complete before formal entry. It validates:

- PowerShell 7.6.4 and Windows PowerShell 5.1 parser acceptance;
- exact test, RED module, GREEN module, inventory, formal verifier, and closure
  source identities;
- side-effect-free module scope and the single exported function;
- exact comparator parameters and return property order;
- explicit runtime type rejection before comparison;
- exactly one `StringComparer.Ordinal.Equals` digest comparison;
- no identity comparison through `-eq`, `-ceq`, `Compare-Object`, string
  interpolation, array containment, pipeline aggregation, or collection
  truthiness;
- canonical JSON reconstruction with explicit `Utf8JsonWriter` calls and no
  dynamic serializer;
- path-string ancestry using `[IO.Directory]::GetParent($Cursor)` and no
  filesystem-object `.Parent`;
- read-only APIs only in the formal verifier and closure;
- no retry loop, alternate path, PATH/module search, shell command string,
  dynamic evaluation, redirection, transcript, sidecar, or file write; and
- no predecessor execution or Docker/GPU/A11/product/Git-mutation/network/
  runtime command.

Its sole PASS is:

```text
ENTRY_VERIFIER_STATIC_PASS|exports=1|types=scalar|comparison=ordinal|writes=0|retries=0
```

Any difference is:

```text
ENTRY_VERIFIER_STATIC_REJECTED / NO_GO
```

Formal entry never runs after static rejection.

## Formal entry verification

The formal verifier accepts only explicit absolute actual/expected path,
byte-count, and SHA-256 identities for the GREEN comparator module, canonical
inventory, and expected fresh workspace. No parameter is optional and no
receiver supports relative fallback.

It validates the inventory bytes canonically before using any inventory value.
For each of the 20 expected files it:

1. validates absolute, canonical, contained, ordinary, non-linked path ancestry;
2. converts the expected JSON byte count explicitly to `System.Int64`;
3. obtains the actual file length explicitly as `System.Int64`;
4. obtains the actual lowercase SHA-256 explicitly as one `System.String`;
5. preserves the expected lowercase SHA-256 as one `System.String`;
6. calls `Compare-A11ScalarIdentity` exactly once;
7. stores the complete returned record in memory; and
8. rejects the inventory if any `identity_match` is not exactly Boolean true.

It separately verifies exact file counts, absent machine paths, four older
absent preformal paths, the consumed v6 workspace absence, frozen PowerShell
bytes/hash/signature, Git lineage, and linked/canonical cleanliness.

It emits no per-file console output and writes no file. Its only success is:

```text
ENTRY_VERIFIER_FORMAL_PASS|workspaces=4|files=20|comparison=ordinal|contradiction=preserved|v6=absent
```

Formal entry runs exactly once. Any exit, output, exception, type, path,
identity, inventory, absence, or state mismatch is:

```text
ENTRY_VERIFIER_RECOVERY_UNPROVABLE / NO_GO
```

The formal verifier, inventory, comparator, and every path they consumed are
immutable after that observation. No corrected source, alternate inventory, or
second formal invocation is permitted.

## Closure and report

An independent closure verifier is authored and frozen before formal entry. It
writes nothing and does not invoke the formal verifier. After formal PASS, it
recomputes source and inventory identities, rechecks the 20 file records through
its own explicit scalar/ordinal logic, verifies all absence and Git facts, and
requires the exact formal PASS captured by the outer harness.

Before the report it emits only:

```text
ENTRY_VERIFIER_CLOSURE_PASS|workspaces=4|files=20|formal=exact|writes=0
```

One final report is then authored with `apply_patch`. It indexes lineage,
authority, the preserved contradictory result, Stage 0, comparator RED/GREEN,
all source identities, canonical inventory identity, static PASS, formal PASS,
20 actual/expected records, absence facts, and prohibited-action
non-occurrence. It explicitly states that the consumed entry was not retried or
converted to PASS.

Final closure runs once, requires the immutable report identity and exact final
human-authored inventory, and emits only:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Contradiction, omission, or unexpected state is
`ENTRY_VERIFIER_RECOVERY_UNPROVABLE / NO_GO`; the report is never repaired.

## Failure handling and immutability

- Stage 0 failure stops before workspace creation.
- Comparator RED or GREEN failure freezes the fresh workspace and stops before
  canonical inventory consumption.
- Static failure freezes sources and stops before formal entry.
- Formal failure preserves the exact formal result and stops without a retry.
- Closure or report failure preserves the first result and stops without
  repair.
- A PASS at any earlier layer authorizes only the next layer named in the later
  approved implementation plan.
- No exception, later direct measurement, or manual comparison is converted to
  PASS.

## Written-spec and commit gates

Before committing this design, require:

1. HEAD is exactly `68cd174c64a17e4b8c42771caf046ecb23c3eb06` on the required branch;
2. linked and canonical worktrees are clean with empty staging;
3. this design path, the entryv7 workspace, and the consumed v6 workspace are
   absent before authoring;
4. only this design path changes;
5. the recorded target is currently 97 bytes with exact frozen SHA-256, without
   treating that observation as retroactive PASS;
6. placeholder, conflict-marker, trailing-whitespace, and Markdown checks pass;
7. purpose, alternatives, root cause, comparator contract, TDD, inventory,
   static admission, formal entry, failure handling, authority, and closure are
   internally consistent;
8. the design does not authorize observer, host, machine, Docker, GPU, A11,
   product, model, or runtime execution;
9. the commit has the required direct parent, author, committer, subject, and
   sole changed path; and
10. authoring executes no failed entry, predecessor source, comparator, formal
    verifier, closure, Docker, GPU, A11, product, model, or runtime command.

After this one-file commit, stop for owner review of the written specification.
Invoke `writing-plans` only after explicit written-spec approval.

## Success criteria

This design succeeds when a later approved implementation plan proves, with a
persistent TDD-tested comparator and one canonical inventory, that all 20
preserved v2-v5 file identities and required absences match under explicit
scalar/ordinal semantics, while preserving the consumed contradictory entry as
a failed non-PASS fact and stopping before child-exit recovery.
