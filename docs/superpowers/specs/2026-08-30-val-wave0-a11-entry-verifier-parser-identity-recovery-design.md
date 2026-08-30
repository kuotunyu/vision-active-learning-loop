# Wave 0 A11 Entry-Verifier Parser-Identity Recovery Design

**Date:** 2026-08-30

**Status:** Approved architecture; written specification pending owner review

**Branch:** `codex/wave0-model-contract`

**Required parent:** `483cf5fd7886bdbc26aefb82d800333d9e001d6d`

## Purpose

Recover the entry-verification boundary from a preserved v7 procedure failure
without rerunning, repairing, deleting, or retroactively accepting any v7 gate.
The successor proves the identity of each parser process before accepting its
syntax result, repeats the comparator contract in a fresh v8 namespace, and
performs one new read-only formal inventory verification.

The success boundary remains intentionally narrow:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Success does not resume the consumed recorder child-exit plan and does not
authorize Docker, GPU, CUDA, A11 entry, a model, a product task, or runtime.

## Preserved v7 incident

The consumed v7 implementation plan is immutable:

| Object | Identity |
|---|---|
| Plan commit | `483cf5fd7886bdbc26aefb82d800333d9e001d6d` |
| Plan blob | `5ed0f6819deb12b0ab6b204624a9278e9b35289e` |
| Plan path | `docs/superpowers/plans/2026-08-30-val-wave0-a11-entry-verifier-contradictory-result-recovery.md` |
| Parent design commit | `c558c0a9a1ce02c3162305b4b7bf6592a905432a` |
| Parent design blob | `5bfa3ded2c55acf48b3e193a9fbb53d126e945ad` |

Its Stage 0 passed exactly:

```text
ENTRYV7_STAGE0_PASS|workspace=absent|v6=absent|linked=clean|canonical=clean
```

The scalar RED was then executed once and returned its exact expected result:

```text
SCALAR_IDENTITY_TEST_RED_PASS|fault=equal_scalar_rejected
```

The RED child exited 0, produced 59 UTF-8 stdout bytes including CRLF, produced
zero stderr bytes, changed no workspace file, and left `machine/` absent. The
GREEN module was created after that RED but its GREEN test never ran.

The required Windows PowerShell 5.1 parser precondition was not established
before the RED. The command presented as that check ran in the Codex frozen
PowerShell 7.6.4 Core process and printed a caller-authored `PS51_PARSE_PASS`
label without first asserting the actual parser executable, engine version, or
edition. A later read-only host check established that the controlling process
was:

```text
C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe
PowerShell 7.6.4
PSEdition Core
```

That later observation does not repair or reinterpret the consumed sequence.
The preserved v7 terminal is:

```text
ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO
```

The v7 workspace contains exactly these four ignored artifacts:

| File | Bytes | SHA-256 | Status |
|---|---:|---|---|
| `task-1-stage0-audit-v7.ps1` | 3,849 | `ceb694a82311d8d16bc229dd21cfb9264fa3fc661727bc4b82f286b95998819b` | Stage 0 audit; never executed |
| `task-1-scalar-identity-tests-v7.ps1` | 8,849 | `977ac4ea6021d074fdcd6e2af0bf48f71dc53186b1e8a09c518ccf33651403d9` | RED consumed; GREEN not run |
| `task-1-scalar-identity-red-v7.psm1` | 991 | `34952e60feb34ad405544d82dcb9fff38dfdd567ae457e5d07ddf640430dc919` | Consumed RED subject |
| `task-1-scalar-identity-green-v7.psm1` | 2,553 | `a3a7d78145b74f7051ac195b8e167fb6d199e7aad25d652a4294fe5b439f5210` | Authored but untested |

The v7 `machine/` directory and `task-1-report.md` are absent. No v7 source may
be imported, dot-sourced, invoked, copied as an executable subject, edited, or
deleted by this recovery.

## Root cause

The root cause is an execution-identity assertion gap at the orchestration
boundary. A tool shell selector named `powershell` resolved to PowerShell 7.6.4
Core, while the script printed a hard-coded Windows PowerShell 5.1 success
label. The check proved only that a PowerShell parser accepted the files; it did
not prove which parser accepted them.

Three missing assertions made the label spoof possible:

1. the child did not compare its real process path from
   `Process.GetCurrentProcess().MainModule.FileName` with an expected absolute
   executable path;
2. the child did not require the expected `$PSVersionTable.PSVersion` family
   and `$PSVersionTable.PSEdition`; and
3. the controller did not bind the claimed role to exact executable bytes,
   digest, signature, and link policy before accepting stdout.

This is a sequencing and evidence defect, not evidence of a syntax defect in
the v7 sources. The absence of the required precondition is sufficient for
NO_GO; a later parser run cannot satisfy an earlier gate.

## Decision

Use a fresh v8 entry-verifier recovery with an identity-attested dual-parser
control and two independent TDD contracts.

1. A minimal Stage 0 preserves v7 and admits exact repository, lineage,
   workspace-absence, and executable-file facts without running either parser.
2. A pure parser-runtime identity contract first demonstrates the exact
   `declared role trusted` mutation and then rejects it.
3. The implementation plan carries the exact parser-policy RED/GREEN sources
   and proves that those source blocks parse under both pinned parsers before
   the docs-only plan commit. Their execution-time RED/GREEN behavior runs only
   under the frozen PowerShell 7 process and does not claim a v8 dual-parser
   PASS.
4. Only after parser-policy GREEN may the workspace worker and controller be
   created. They use the production runtime-identity comparator and two
   explicit absolute executable paths to prove every later parser result.
5. A completely new scalar comparator RED and GREEN run only after the
   pre-RED dual-parser gate passes.
6. A canonical v8 inventory preserves the v7 NO_GO, all four v7 artifacts, the
   earlier 20 v2-v5 artifacts, and every required absence.
7. One static admission, one formal read-only inventory verification, one
   pre-report closure, and one final closure complete the milestone.

No v7 gate, module, test invocation, stdout label, or command identity is
reused as a v8 success input.

## Alternatives considered

### A. Fresh v8 with process self-attestation and full verifier replay — selected

This has the clearest causal boundary. The negative policy test catches the
actual failure mode, every parser identifies itself, and the scalar RED/GREEN
sequence is new rather than retroactively completed.

### B. Run Windows PowerShell 5.1 now and continue v7 — rejected

This would perform the missing action after the single-use RED was consumed.
Even an exact parse result would be a new observation, not the required prior
precondition, and would rewrite the meaning of preserved v7 evidence.

### C. Remove the Windows PowerShell 5.1 parser requirement — rejected

This would avoid the orchestration issue by weakening the approved
compatibility contract. It would not repair the identity-control defect and
would make the successor less rigorous than its predecessor.

### D. Add a general tracked dual-parser framework — rejected

A reusable product utility could be valuable later, but it would expand the
tracked allowlist, product API, tests, and maintenance surface. This recovery
needs one evidence-only control, not a new repository subsystem.

## Authority and non-goals

This recovery may:

- create this one-file docs-only design commit and, after written-spec
  approval, one one-file docs-only implementation-plan commit;
- run one plan-pinned Stage 0 that reads repository, v7, and executable-file
  evidence without executing either parser;
- create one fresh ignored v8 workspace using `apply_patch` for each human-
  authored file;
- launch only the two pinned PowerShell executables for named, single-use
  parser-policy and syntax phases;
- execute fresh v8 parser-policy and scalar RED/GREEN behavioral tests through
  the frozen PowerShell 7 executable; and
- run one v8 static verifier, formal entry verifier, pre-report closure, and
  final closure.

It may not:

- rerun, repair, reinterpret, replace, delete, or declare PASS for v7;
- execute or import any v7 or v2-v6 source;
- create the consumed v6 workspace or any `machine/` directory;
- accept a runtime role from a caller label without child self-attestation;
- use `powershell`, `pwsh`, PATH lookup, an alias, a shim, a relative path, a
  shell command string, or fallback executable selection for a formal gate;
- retry a failed Stage 0, RED, GREEN, parser phase, static gate, formal gate,
  closure, or report;
- modify product code, configuration, schema, test, Dockerfile, dependency,
  artifact, image, lease, run, or another repository;
- inspect or execute Docker, WSL, Hyper-V, GPU, `nvidia-smi`, CUDA, A11,
  product, model, campaign, Wave 1, or network activity;
- create, consume, infer, increment, or synthesize an
  `OwnerAuthorizationId`; or
- push, merge, release, tag, amend, rebase, reset, stash, or delete evidence.

General owner trust does not broaden these boundaries.

## Append-only lineage and workspace

This design commit changes only this file and is a direct child of:

```text
483cf5fd7886bdbc26aefb82d800333d9e001d6d
```

After written-spec approval, the implementation plan is a one-file direct
child of this design commit. Both commits use exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

The fresh ignored execution workspace is:

```text
.superpowers/sdd/2026-08-30-val-wave0-a11-entry-verifier-parser-identity-recovery/
```

The namespace is `entryv8-*`. Before Stage 0, that workspace is absent. After
Stage 0, the final human-authored inventory is exactly 14 files:

| File | Responsibility |
|---|---|
| `task-1-stage0-audit-v8.ps1` | Exact admitted Stage 0 source and observation; never executed. |
| `task-1-parser-identity-tests-v8.ps1` | RED/GREEN behavioral contract for runtime-role binding. |
| `task-1-parser-identity-red-v8.psm1` | Intentional implementation that trusts the declared role. |
| `task-1-parser-identity-green-v8.psm1` | Pure production parser-runtime identity comparator. |
| `task-1-parser-worker-v8.ps1` | Self-attesting syntax worker executed by each pinned runtime. |
| `task-1-dual-parser-controller-v8.ps1` | Starts exactly two pinned workers and accepts only attested results. |
| `task-1-scalar-identity-tests-v8.ps1` | Fresh scalar identity RED/GREEN behavior contract. |
| `task-1-scalar-identity-red-v8.psm1` | Fresh intentional equal-scalar rejection subject. |
| `task-1-scalar-identity-green-v8.psm1` | Fresh production scalar comparator. |
| `task-1-preserved-inventory-v8.json` | Canonical incident, executable, artifact, and absence inventory. |
| `task-1-entry-verifier-v8.ps1` | One-shot read-only 24-file formal verifier. |
| `task-1-static-verifier-v8.ps1` | Parser, AST, type-flow, process-count, and forbidden-action gate. |
| `task-1-closure-verifier-v8.ps1` | Independent pre-report and final closure. |
| `task-1-report.md` | Immutable evidence index and first exact final terminal. |

There are 13 human files before report creation and 14 afterward. No fixture,
brief, transcript, sidecar, result, digest, temporary, cache, or machine file is
permitted.

## Pinned executable identities

The implementation plan freezes these two executable-file identities before
Stage 0. Stage 0 must revalidate them exactly.

### PowerShell 7

```text
path: C:\Users\<user>\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\powershell\pwsh.exe
bytes: 301368
SHA-256: db6dd81183fe57d22e03b911ec9a30a2fd7c40542e97743615355a6fb44f458f
engine version: 7.6.4
edition: Core
file version: 7.6.4.500
signature: Valid
signer thumbprint: AB172913A2960A224809EE8A0C371CD47A079B72
signer: CN=Microsoft Corporation, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
leaf link type: none
```

### Windows PowerShell 5.1

```text
path: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
bytes: 454656
SHA-256: 7600ffe12da441fe89d035b13801e8e91d064bc544a27b19a5cf49f6ab8b18f5
engine version policy: major 5, minor 1
edition: Desktop
file version: 10.0.26100.8875 (WinBuild.160101.0800)
product version: 10.0.26100.8875
signature: Valid
signer thumbprint: DC91E564D5BC1E3A8E02D6A8508682ABEA8A2443
signer: CN=Microsoft Windows, O=Microsoft Corporation, L=Redmond, S=Washington, C=US
leaf link type: HardLink
```

The Windows system executable's observed `HardLink` is an explicit, closed
exception. It is allowed only for the exact System32 path, byte count, digest,
file/product versions, signature, signer, and thumbprint above, with the
`ReparsePoint` attribute absent. Symbolic links, junctions, other reparse
points, alternate hard-link paths, and any reparse point in either executable's
parent chain are rejected. The controller never searches the component store
or follows a fallback candidate.

The Windows executable's 10.0 file version is not treated as its PowerShell
engine version. The child independently requires engine major 5, minor 1 and
edition `Desktop` from `$PSVersionTable`.

## Stage 0 admission

The plan pins the exact LF/UTF-8 Stage 0 source, byte count, and SHA-256 before
execution. Stage 0 performs no parser process start. It requires:

- exact approved design/plan lineage, commit identity, and branch;
- linked-worktree topology, non-submodule state, empty staging, and clean
  tracked/untracked linked and canonical worktrees;
- the v8 workspace absent;
- the consumed v6 workspace absent;
- the v7 workspace present with exactly four files and the exact identities
  listed above;
- v7 `machine/` and report absent;
- the exact two executable identities, signatures, allowed link policies, and
  non-reparse parent chains; and
- no Docker, GPU, runtime, project source, or predecessor-source execution.

Its sole success is:

```text
ENTRYV8_STAGE0_PASS|v7=preserved_no_go|files=4|workspace=absent|runtimes=2|linked=clean|canonical=clean
```

Any difference stops with the v8 workspace absent. Stage 0 never converts v7
to PASS.

## Parser-runtime identity contract

The pure production comparator accepts closed expected and observed records.
Each record contains exactly:

```text
role
process_path
powershell_version
ps_edition
executable_byte_count
executable_sha256
file_version
product_version
signature_status
signer_subject
signer_thumbprint
leaf_link_type
leaf_reparse_point
parent_chain_reparse_points
```

It rejects nulls, arrays, enumerables, duplicate or additional properties,
wrong runtime types, malformed digests, unsupported role names, relative or
noncanonical paths, and policy/identity mismatches. Windows path equality is
`StringComparer.OrdinalIgnoreCase`; digests, editions, versions, roles,
signature values, signer fields, and terminals use
`StringComparer.Ordinal`. Byte counts are nonnegative `System.Int64`; Boolean
fields are exact `System.Boolean` values.

The intentional RED trusts `role=windows-powershell-5.1` even when the observed
process path, version, and edition describe the frozen PowerShell 7 executable.
The RED test names that mutation and emits only:

```text
PARSER_IDENTITY_TEST_RED_PASS|fault=declared_role_trusted
```

The RED subject and invocation are consumed once. The GREEN test then proves:

1. the exact PowerShell 7 record passes;
2. the exact Windows PowerShell record passes with the closed HardLink policy;
3. PowerShell 7 declared as Windows PowerShell 5.1 is rejected;
4. Windows PowerShell declared as PowerShell 7 is rejected;
5. path, engine-version, or edition mutation is rejected;
6. bytes, digest, file/product version, signature, signer, or thumbprint
   mutation is rejected;
7. leaf-link or parent-reparse mutation is rejected; and
8. missing, additional, array, null, malformed, or wrongly typed fields are
   rejected.

GREEN emits only:

```text
PARSER_IDENTITY_TEST_GREEN_PASS|cases=8|roles=bound|labels=untrusted
```

Any unexpected test result, output, exit, type, property, or side effect is:

```text
ENTRYV8_PARSER_IDENTITY_UNPROVABLE / NO_GO
```

## Identity-attested dual-parser gate

The implementation plan contains the complete parser-policy test, RED, GREEN,
worker, and controller source blocks verbatim with exact bytes and SHA-256.
Plan completion uses each pinned executable's parser API to parse those exact
in-memory blocks before the docs-only plan is committed; it executes no v7,
project, or runtime source. Those authoring checks prove that the future
materialized bytes are syntactically acceptable, but they are not v8 execution
PASS evidence.

At execution, parser-policy RED and GREEN run under the exact frozen PowerShell
7 executable. The worker and controller do not exist until parser-policy GREEN
passes. They are then materialized unchanged from the plan-pinned source and
are never reconstructed from a shell string.

The workspace worker's first operations are strictly ordered:

1. obtain the real executable path from the current process;
2. obtain engine version and edition from `$PSVersionTable`;
3. inspect its executable bytes, digest, versions, signature, signer, link
   state, and path-string parent chain;
4. call the GREEN runtime-identity comparator with the closed expected role;
5. stop before parsing if identity does not match; and
6. parse only the explicit, identity-frozen target files with its own
   `System.Management.Automation.Language.Parser` API.

It performs no import other than the exact GREEN identity module, no PATH or
command lookup, and no process start, file write, Git command, predecessor
execution, or runtime action.

The controller runs only under the frozen PowerShell 7 executable. It uses
`ProcessStartInfo` with `UseShellExecute=false`, redirected stdout/stderr, and
literal argv. It starts exactly:

1. the frozen absolute `pwsh.exe`; and
2. the frozen absolute System32 `powershell.exe`.

It never invokes the command names `pwsh` or `powershell`. Each worker must
exit 0, produce empty stderr, emit only its role-specific attested PASS, and
leave the complete workspace file-name/byte/hash inventory unchanged. The
controller accepts no caller-authored role label without the child's matching
identity record.

Parser phases are individually frozen and single-use. The plan enumerates the
exact target identities for each phase. A failed phase is never retried, and a
later phase cannot repair it. The three permitted combined successes are
exactly:

```text
ENTRYV8_DUAL_PARSER_PASS|phase=scalar-red|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|starts=2|writes=0
ENTRYV8_DUAL_PARSER_PASS|phase=scalar-green|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|starts=2|writes=0
ENTRYV8_DUAL_PARSER_PASS|phase=static|pwsh=7.6.4-Core|windowspowershell=5.1-Desktop|starts=2|writes=0
```

Any child-start, process-identity, output, exit, stderr, parser, target-
identity, count, or side-effect difference is:

```text
ENTRYV8_DUAL_PARSER_UNPROVABLE / NO_GO
```

## Fresh scalar comparator TDD

The v8 scalar test, RED module, and GREEN module are newly authored files. They
do not import or execute a v7 file. Before scalar RED, the identity-attested
dual-parser phase must parse the audit, parser-policy sources, worker,
controller, scalar test, and scalar RED under both runtimes.

The scalar interface and typed behavior remain the approved v7 contract:

- byte counts are nonnegative `System.Int64` scalars;
- digests are exact lowercase 64-character hexadecimal `System.String`
  scalars;
- nulls, arrays, enumerables, malformed values, and wrong runtime types are
  rejected before comparison;
- byte counts use scalar numeric equality;
- digest equality uses only `StringComparer.Ordinal.Equals`; and
- the returned seven-property ordered record contains exact Boolean matches.

The fresh intentional RED always rejects the same exact 97-byte/digest scalar
pair and emits only:

```text
SCALAR_IDENTITY_TEST_RED_PASS|fault=equal_scalar_rejected
```

After exact RED, the GREEN module is created once. A separate single-use
identity-attested parser phase parses the frozen test and GREEN source under
both runtimes before GREEN runs. GREEN repeats the eight approved scalar cases
and emits only:

```text
SCALAR_IDENTITY_TEST_GREEN_PASS|cases=8|comparison=ordinal|collections=rejected
```

Any difference preserves:

```text
ENTRY_VERIFIER_CONTRACT_UNPROVABLE / NO_GO
```

No scalar source or consumed invocation is edited or rerun.

## Canonical preserved inventory

The v8 inventory is one compact strict UTF-8 JSON document without BOM plus
one LF. It is human-authored with `apply_patch` and is never generated from the
live filesystem.

It preserves:

- the exact v7 plan/design lineage and terminal;
- explicit facts that the required pre-RED Windows PowerShell parser gate was
  false, the v7 RED ran once, the GREEN module exists, the GREEN test did not
  run, no final success terminal was emitted, and retroactive PASS is false;
- the exact four v7 file records and exact v7 file count;
- the previously approved 20 v2-v5 records and workspace counts;
- both pinned executable-file identities and runtime-role policies; and
- exactly 12 persistent absences: the ten approved v7 inventory absences, the
  v7 report, and the v8 `machine/` directory.

The resulting preserved set is five workspaces and 24 files. All expected
values are literals carried forward from approved records; live measurements
are actual values only and never become new expected values.

Property order, duplicate rejection, types, canonical serialization, one-LF
termination, byte count, and digest are frozen before formal/static/closure
sources exist.

## Static admission

The static verifier is complete and frozen before formal entry. It proves:

- exact identities for all 13 pre-report human files;
- exact public interfaces, exports, record property orders, and runtime type
  checks;
- the parser-role spoof mutation is behaviorally rejected;
- only the two pinned absolute executable paths can reach
  `ProcessStartInfo.FileName`;
- the controller starts exactly two workers per named parser phase and has no
  retry, fallback, sleep, PATH lookup, alias, shell string, or alternate
  executable;
- each worker self-attests before its first parser call;
- the explicit legacy HardLink exception cannot accept any other path or
  reparse point;
- the scalar comparator has exactly one ordinal digest comparison and no
  collection truthiness;
- formal and closure sources are read-only and cannot invoke a predecessor;
- the inventory is reconstructed canonically; and
- no write, dynamic evaluation, dot-source, redirection, transcript, sidecar,
  machine path, Docker/GPU/A11/product/Git-mutation/network/runtime command,
  or `OwnerAuthorizationId` flow exists.

The static verifier itself is parsed under both identity-attested runtimes
before it runs once. Its sole success is:

```text
ENTRYV8_STATIC_PASS|parser_roles=bound|scalar=ordinal|files=24|writes=0|retries=0
```

Any difference is:

```text
ENTRYV8_STATIC_REJECTED / NO_GO
```

Formal entry never runs after static rejection.

## Formal entry verification

The formal verifier accepts only explicit absolute actual/expected identities
for the v8 inventory, production scalar comparator, expected workspace, plan,
and design. It writes nothing and starts no process.

It validates canonical inventory bytes before using any value. It then:

1. verifies exact repository lineage, linked/canonical cleanliness, staging,
   the closed v8 namespace inventory, and every enumerated preserved ignored
   record;
2. verifies exact v7 workspace count, four file identities, v7 report/machine
   absences, and v7 NO_GO facts;
3. verifies the earlier v2-v5 workspace counts and 20 file identities;
4. verifies all 12 persistent absences;
5. revalidates both pinned executable-file identities without executing them;
6. calls the v8 scalar comparator exactly once for each of the 24 preserved
   files; and
7. retains all 24 actual/expected typed records in memory.

Its sole success is:

```text
ENTRYV8_FORMAL_PASS|workspaces=5|files=24|v7=no_go_preserved|comparison=ordinal|writes=0
```

Formal entry runs exactly once. Any mismatch, exception, output difference,
side effect, or unprovable observation is:

```text
ENTRYV8_RECOVERY_UNPROVABLE / NO_GO
```

No formal input can be edited or rerun after that observation.

## Closure and report

The independent closure verifier does not import the scalar or parser-runtime
modules and never invokes the formal verifier. In `PreReport`, it independently
reconstructs the inventory, checks all 24 records and 12 absences, requires the
exact formal terminal, requires 13 human files and no report/machine path, and
emits only:

```text
ENTRYV8_CLOSURE_PASS|workspaces=5|files=24|formal=exact|writes=0
```

After exact pre-report closure, the report is authored once with `apply_patch`.
It records literal commit/blob identities, executable policies, Stage 0,
parser-policy RED/GREEN, every dual-parser phase, scalar RED/GREEN, inventory,
static, formal, closure, all 24 actual/expected records, all 12 absences, the
14-file final inventory, prohibited-action non-occurrence, and the v7 NO_GO
without reinterpretation. It contains the final success terminal exactly once
as evidence text and is never edited after creation.

In `Final`, closure requires the exact report bytes and digest, exactly 14
human files, no machine file, unchanged source/inventory/executable/v7 facts,
clean repository state, and emits only:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Any contradiction, omission, output difference, or state change is:

```text
ENTRYV8_RECOVERY_UNPROVABLE / NO_GO
```

The report and final closure are never repaired or rerun.

## Error handling and single-use semantics

Every consuming phase has a distinct identity and terminal. A phase is
consumed when its exact child process or formal verifier starts, even if the
tool disconnects, output is truncated, or the process exits before emitting a
record. An uncertain result is unprovable, not permission to retry.

No PASS may be inferred from a later direct file measurement, a matching
digest, an output label, or a parser result produced by an unverified process.
The first unexpected observation freezes all existing v8 files and stops. A
new attempt would require another separately approved design and plan.

## Testing and verification

Before any formal parser phase:

- parser-policy RED proves the caller-label trust mutation exists;
- parser-policy GREEN rejects role/path/version/edition spoofing and every
  identity/link/type mutation;
- plan-pinned source blocks parse under both exact executable paths;
- controller static checks prove two starts, two absolute paths, zero lookup,
  zero retry, and child attestation before parsing; and
- workspace inventory snapshots prove zero writes.

Before formal entry:

- fresh scalar RED and GREEN both produce exact terminals;
- every complete PowerShell source parses under both attested runtimes;
- canonical inventory reconstruction matches exact bytes;
- static admission emits its sole PASS;
- linked and canonical worktrees are clean, staging is empty, the v8 namespace
  contains exactly the 13 allowed pre-report files, and all enumerated older
  ignored evidence remains unchanged; and
- no `machine/`, cache, bytecode, temporary, runtime, or external evidence path
  exists.

Final verification requires the same evidence plus the immutable report and
14-file final v8 inventory. No Docker/GPU/runtime verification is part of this
milestone.

## Success criteria

This recovery is complete only when:

1. this design and its implementation plan are exact one-file direct-child
   commits with the required identity;
2. Stage 0 preserves the exact v7 NO_GO and admits both executable-file
   identities without starting a parser;
3. the parser-policy RED/GREEN cycle proves labels are untrusted and process
   identity is load-bearing;
4. every parser phase self-attests exact executable path, engine, edition,
   bytes, digest, signature, signer, and link policy before parsing;
5. the fresh v8 scalar RED/GREEN cycle passes without using a v7 source;
6. the canonical inventory preserves five workspaces, 24 files, 12 absences,
   and the complete v7 incident semantics;
7. static, one formal entry, pre-report closure, report, and final closure each
   pass exactly once with no side effect; and
8. final closure emits exactly:

```text
ENTRY_VERIFIER_RECOVERY_PASS / CHILD_EXIT_RECOVERY_NOT_AUTHORIZED
```

Success stops there. Child-exit recovery, Docker, GPU, A11, product, model,
campaign, and Wave 1 remain unauthorized.
