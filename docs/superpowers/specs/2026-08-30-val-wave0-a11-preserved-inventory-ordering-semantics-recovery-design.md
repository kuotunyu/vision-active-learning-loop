# Wave 0 A11 Preserved-Inventory Ordering-Semantics Recovery Design

**Status:** Approved architecture design; written-spec review pending

**Date:** 2026-08-30

**Branch:** `codex/wave0-model-contract`

**Parent commit:** `03115325f36da31b135b4593fb8df1689eac9a35`

## Purpose

Recover the A11 runtime-transport implementation path from a second
specification-boundary contradiction: one universal ordinal run-inventory
sort cannot reproduce the frozen digests of the earlier preserved attempts.

This recovery introduces explicit, per-attempt canonicalization versions. It
preserves every artifact byte and every already approved digest. It does not
reinterpret a failed attempt, learn a replacement value from observed state,
or weaken the complete preserved-evidence envelope.

This design supersedes only the universal run-inventory ordering requirements
in:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery-design.md
docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-digest-recovery.md
```

Every unaffected lineage, registry, transport-wrapper, Docker, TDD,
preservation, single-commit, diagnostic, and runtime boundary in those
documents and their predecessors remains in force.

## Authority and non-authority

The owner approved this recovery direction with the exact statement:

```text
核准制定 A11 preserved-inventory ordering-semantics recovery design；採 versioned canonicalization，保留所有既有 artifact 與 frozen digest。
```

The owner subsequently delegated the deterministic legacy comparer choice and
remaining design decisions to the implementing agent. The selected comparer is
`StringComparer.OrdinalIgnoreCase`, with collision rejection, for the
legacy-compatible version.

This authority permits this append-only design document. It does not yet
authorize an implementation plan, implementation-file edit, artifact edit,
`OwnerAuthorizationId`, launcher invocation, Docker build or run, dependency
diagnostic, GPU lease, model initialization, A11 runtime attempt, Wave 1
action, push, merge, release, tag, rebase, reset, stash, or modification of
another repository.

## Frozen lineage and evidence context

The recovery starts from:

```text
branch                              codex/wave0-model-contract
ordering-recovery parent            03115325f36da31b135b4593fb8df1689eac9a35
digest-recovery design              2db13d302da97a241daeaba3578cd9cec1c8073b
digest-recovery plan                03115325f36da31b135b4593fb8df1689eac9a35
runtime-transport design            db047dcb8ad602fc4ac316a743ab4ddec3168cd5
runtime-transport plan              e31fc0c10fe34b480f7b2ee3d12a2e55530c6350
diagnostic-root erratum             101bb79369399cc3947f1c667f0a11988f916638
attempt-5 source                    ed6f157c7cbd545895b9d047f6e094968a1f9d94
approved A11 specification          b59b0d4407b98b460f6166ea7288ba6021dc7a78
original A11 plan                   7dbd3a7576ea76beccfc64f748c4e495259ea89b
```

The artifact root remains read-only:

```text
D:\vision-active-learning-loop-artifacts\wave0
```

The linked and canonical worktrees were clean when this recovery was
designed. No repository-local `AGENTS.md` applies to this worktree.

## Preserved Task 1 failure and root cause

The digest-recovery Task 1 gate passed lineage, identity, isolation,
`uv.lock`, and the committed attempt-5 vector proof at parent commit
`03115325f36da31b135b4593fb8df1689eac9a35`. It then stopped on the first
preserved run, as required.

The first run evidence was:

```text
run ID                 wave0-a11-calibration-20260828T045848083Z-b9917463
expected files         48
observed files         48
expected directories   18
observed directories   18
expected latest write  2026-08-28T06:06:15.8277603Z
observed latest write  2026-08-28T06:06:15.8277603Z
links absent           true
canonical bytes        9220
frozen digest          fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b
universal-v2 digest    72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c
```

The file count, directory count, latest-write value, and link state all
matched. A subsequent path-only comparison showed that the artifact did not
drift: the legacy producer order and ordinal order place the same 48 paths in
different sequences at 30 positions. The first difference is the ordering of
the lowercase `facebook--dinov2-small` subtree and uppercase
`PekingU--rtdetr_r18vd` subtree.

Repository history identifies two distinct evidence contracts:

1. `run_inventory_sha256` for preserved A11 runs was produced by
   `Sort-Object FullName`, whose effective ordering for these paths is
   case-insensitive and places `facebook--...` before `PekingU--...`.
2. The fourth recovery intentionally changed the separate model-cache
   inventory to explicit ordinal order so Windows and Linux would place
   `PekingU--...` before `facebook--...`.

The preceding digest-recovery design incorrectly applied the model-cache
ordering decision to all historical run inventories. It also claimed that
the ordinal algorithm reproduced attempts 1 through 4. The preserved Task 1
gate disproved that claim before any implementation.

Read-only path comparisons across all five runs provide the ordering proof:

| Attempt | Files | Legacy order equals deterministic v1 | Legacy order equals ordinal v2 |
| ---: | ---: | :---: | :---: |
| 1 | 48 | yes | no |
| 2 | 5 | yes | yes |
| 3 | 60 | yes | no |
| 4 | 137 | yes | no |
| 5 | 10 | yes | yes |

Directory-order comparisons independently provide the same boundary:

| Attempt | Directories | Legacy order equals deterministic v1 | Legacy order equals ordinal v2 |
| ---: | ---: | :---: | :---: |
| 1 | 18 | yes | no |
| 2 | 5 | yes | yes |
| 3 | 18 | yes | no |
| 4 | 30 | yes | no |
| 5 | 5 | yes | yes |

Attempts 1, 3, and 4 each have twelve directory positions that differ between
v1 and v2. Attempts 2 and 5 happen to have the same order under both
comparers; that coincidence does not erase their explicit algorithm identity.

## Frozen attempt digests

This recovery does not change any approved aggregate. The registry and entry
gate must retain exactly:

| Attempt | Required algorithm | Frozen run-inventory SHA-256 |
| ---: | --- | --- |
| 1 | `a11-run-inventory-json-ordinal-ignore-case-v1` | `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b` |
| 2 | `a11-run-inventory-json-ordinal-ignore-case-v1` | `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b` |
| 3 | `a11-run-inventory-json-ordinal-ignore-case-v1` | `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2` |
| 4 | `a11-run-inventory-json-ordinal-ignore-case-v1` | `f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717` |
| 5 | `a11-run-inventory-json-ordinal-v2` | `e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64` |

The attempt-5 superseded declaration
`b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448`
remains historical failure evidence only and must never be accepted for the
approved ten-record vector.

The first attempt's universal-v2 digest
`72259c2206ef41d909e904bca97ed27c123e6c23a4b177af9be633479ddf7e3c`
is a negative test vector only. It must never replace or be accepted alongside
the frozen v1 digest.

## Approaches considered

### Selected: explicit per-attempt algorithm IDs with deterministic comparers

Add a required `run_inventory_algorithm` field to each registry record. Use a
legacy-compatible deterministic v1 for attempts 1 through 4 and ordinal v2
for attempt 5. Dispatch through a closed algorithm table rather than attempt
ordinal, state, date, or a digest fallback.

This preserves all frozen values, removes locale dependence from future
verification, keeps one shared serializer, and makes the historical boundary
reviewable.

### Rejected: freeze literal `zh-TW` PowerShell collation

Executing `Sort-Object FullName` under a frozen `zh-TW` culture most literally
copies the original producer. It still depends on PowerShell, .NET, operating
system, culture tables, and comparison behavior. Those dependencies are not
part of the artifact evidence and are unnecessary because
`StringComparer.OrdinalIgnoreCase` reproduces every current legacy file and
directory order.

### Rejected: store complete ordered file vectors for every attempt

A registry containing every path, size, and file hash could avoid defining a
legacy comparer. It would substantially enlarge the source-controlled
registry, duplicate existing manifests and key-record evidence, and broaden
the implementation without improving the immutable artifact boundary.

### Rejected: recompute all historical digests with ordinal v2

This would modify frozen evidence to match a new algorithm. It violates the
owner's explicit preservation requirement and would convert a verifier defect
into an artifact-history rewrite.

## Versioned canonicalization contract

### Common validated record and byte contract

Both algorithms use the same closed pipeline:

1. Resolve the run root to an absolute path without modifying it.
2. Reject a missing or non-directory root and every reparse point or link at
   the root, an ancestor inside the artifact boundary, or a descendant.
3. Recursively enumerate regular files without trusting enumeration order.
4. Convert each file to a run-root-relative path with `/` separators and
   observed case unchanged. Reject rooted paths and `.` or `..` segments.
5. Create one ordered record with exactly `path`, `size`, and `sha256`.
6. Require a non-negative integer size and lowercase 64-character SHA-256 of
   the exact file bytes.
7. Reject duplicate normalized paths under `StringComparer.Ordinal` before
   algorithm-specific sorting.
8. Apply the selected algorithm's additional uniqueness rule and comparer.
9. Serialize exactly one compact JSON array with record field order
   `path,size,sha256`.
10. Encode as strict UTF-8 without BOM or trailing line terminator.
11. Compute lowercase SHA-256 over those exact bytes.

The algorithm ID is registry metadata. It is not inserted into the canonical
record array and therefore does not alter any preserved run digest.

### Algorithm v1: deterministic legacy compatibility

```text
a11-run-inventory-json-ordinal-ignore-case-v1
```

V1 sorts normalized relative paths with
`StringComparer.OrdinalIgnoreCase`. Before sorting, it must reject any two
paths that compare equal under that comparer. Collision rejection makes the
ordering total for the admitted path set and prevents filesystem enumeration
order from breaking ties.

The same comparer and collision rule apply to exact directory-name arrays.
Attempts 1 through 4 require v1. Production verification must not call
`Sort-Object`, read `CurrentCulture`, or depend on Windows path collation.

### Algorithm v2: ordinal canonical order

```text
a11-run-inventory-json-ordinal-v2
```

V2 sorts normalized relative paths with `StringComparer.Ordinal`. It rejects
ordinal duplicates. The same comparer applies to exact directory-name arrays.
Attempt 5 requires v2.

V2 is the forward canonicalization version for this recovery, but this design
does not authorize or define a future attempt. Any future registry append
still requires separate reviewed source and runtime authority.

### Closed dispatch

The schema requires `run_inventory_algorithm` on every attempt and restricts
it to the two exact values above. The production dispatcher accepts only
those values. Missing, null, differently cased, aliased, or unknown IDs fail
before artifact hashing or any write.

Dispatch must not depend on:

- attempt ordinal or array index;
- state or source commit;
- expected or observed digest;
- current culture or host platform; or
- retrying with another algorithm after a mismatch.

An attempt whose record bytes happen to produce the same digest under both
comparers still passes only when the configured algorithm ID is the exact
approved value.

## Recovery units

### Unit A: append-only design and plan lineage

This design is one new file whose commit is the direct child of
`03115325f36da31b135b4593fb8df1689eac9a35`. It does not edit the preceding
design or plan.

After written-spec approval, one new implementation plan may be added as the
direct child of this design commit. That plan must supersede only:

- the universal-ordinal Task 1 run and directory verification;
- the registry schema omission of `run_inventory_algorithm`;
- the canonical inventory API that lacked an algorithm parameter; and
- the now-obsolete implementation-parent lineage.

The plan must retain the seven-path implementation allowlist:

```text
configs/a11/preserved-attempts.json
schemas/a11-preserved-attempts.schema.json
scripts/run_uv_sync_with_retries.py
scripts/run_wave0_a11.ps1
docker/wave0.Dockerfile
tests/gates/test_wave0_a11_launcher.py
tests/scripts/test_run_uv_sync_with_retries.py
```

Tasks before the existing verification task create no commit. The
verification task creates one implementation commit only after every required
gate passes. The existing at-most-once dependency-only diagnostic remains a
separate later task and is not executed by this design.

### Unit B: corrected full Task 1 gate

Before any implementation-path edit, the new plan must run one complete
read-only gate from its exact clean parent.

For each run, the gate hashes each regular file once into an in-memory,
unsorted closed record set. It may sort copies of those records multiple ways
without rereading file bytes.

The gate must prove:

1. exact design/plan lineage, one-file documentation scopes, commit identity,
   branch, linked-worktree isolation, clean linked and canonical worktrees,
   empty staging, and unchanged `uv.lock` SHA-256
   `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`;
2. attempts 1 through 4 have v1 file and directory order identical to their
   legacy producer order and reproduce their four frozen digests;
3. attempt 1 under v2 reproduces the negative digest `72259c...e3c` and is
   rejected rather than adopted;
4. attempt 5 has the exact ten file records and five directories already
   approved, and two independent v2 encoders produce byte-identical output,
   1,283 bytes, and digest `e6a0...e64`;
5. all five exact run identities, file/directory counts, latest-write values,
   absence rules, and owner evidence remain unchanged;
6. exactly three frozen A11 images and six frozen lease-history files remain;
7. zero validation roots, active leases, project containers, numeric CUDA
   compute processes, links, or dependency-diagnostic identities exist;
8. exactly 64,306 historical non-A11 files retain SHA-256
   `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`;
9. exactly 21 historical images retain SHA-256
   `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`;
   and
10. the complete CPU baseline passes with bytecode and pytest-cache writes
    disabled.

Any failure stops the plan before implementation and preserves a `NO_GO`.

### Unit C: version-bound registry

The not-yet-created registry keeps `schema_version=1` and adds the required
`run_inventory_algorithm` property to each attempt. No registry migration is
needed because no registry file exists at this design parent.

The first four records carry v1 and the fifth carries v2. The registry loader
returns the exact registry-file byte hash with the parsed closed object. The
launcher rehashes the file immediately before its first permitted write.

The registry remains expected-state source data. Production must not generate,
normalize, repair, append, or reorder it. The algorithm field grants neither
runtime authority nor permission to create a destination.

### Unit D: algorithm-explicit inventory boundary

The production inventory API accepts an explicit run root and exact algorithm
ID. It has three isolated responsibilities:

1. validate and materialize closed records and directory names;
2. select a comparer from the closed algorithm table; and
3. serialize and hash the sorted records.

The generic prior-attempt verifier supplies the registry field unchanged to
this API and compares its result with the same record's frozen digest and
directory list. No state-specific inventory branches remain.

### Unit E: TDD binding

Focused launcher tests must be RED before production changes for at least:

- the current universal-ordinal implementation against an attempt-1-style
  mixed-case fixture;
- the missing registry algorithm field; and
- v1 collision rejection.

GREEN coverage must require:

- exact v1 and v2 algorithm IDs and closed dispatch;
- `facebook--...` before `PekingU--...` under v1 and the reverse under v2;
- identical v1 output under multiple current-culture settings;
- rejection of v1 case-insensitive path collisions;
- rejection of missing, null, unknown, or differently cased algorithm IDs;
- the shared `path,size,sha256`, compact JSON, UTF-8, no-BOM, no-newline byte
  contract;
- the exact attempt-5 1,283-byte `e6a0...e64` vector;
- rejection of attempt-5 `b4c894...` and attempt-1 `72259c...` as accepted
  frozen values;
- registry assignment of v1 to attempts 1 through 4 and v2 to attempt 5;
- generic-verifier failure when an algorithm ID is changed even if that
  fixture's comparer output happens to be identical; and
- fixture-only tests that never read or mutate the external artifact root.

The existing wrapper, Dockerfile, generic registry, preservation, parser,
style, lock, full CPU pytest, review, single-commit, and post-commit tests
remain required.

### Unit F: unchanged runtime and diagnostic boundary

This recovery does not change or execute the bounded uv retry wrapper,
BuildKit cache, Docker stage, dependency-only diagnostic, model, statistical
contract, replica counts, thresholds, leases, phase order, failure closure,
or runtime authorization process.

No `OwnerAuthorizationId` is consumed by design, planning, Task 1,
implementation, repository verification, or the dependency-only diagnostic.
A future formal launcher attempt remains separately authorized and out of
scope.

## Data flow

```text
registry attempt
  |-- required algorithm ID
  |-- frozen digest
  |-- exact directory expectations
  v
closed path/link/record validation --failure--> preserved NO_GO
  |
  v
closed algorithm dispatch --unknown/mismatch--> preserved NO_GO
  |
  +-- v1: OrdinalIgnoreCase + collision rejection
  |
  +-- v2: Ordinal
  v
shared compact ordered JSON + strict UTF-8
  |
  v
SHA-256 comparison --failure--> preserved NO_GO
  |
  v
remaining full preservation and CPU gates
  |
  +-- failure: stop before implementation
  v
TDD implementation in existing seven-file boundary
```

## Failure handling

Every comparison is fail-closed. These conditions stop before the next
mutating boundary:

- artifact, record, directory, timestamp, image, lease, historical baseline,
  Git, lockfile, Docker, GPU, or diagnostic state differs;
- an algorithm ID is absent, unknown, misassigned, or changed;
- a normalized path collides under its selected algorithm;
- legacy order and deterministic v1 differ for attempts 1 through 4;
- either independent attempt-5 encoder differs;
- a byte count or frozen digest differs;
- a test, parser, schema, style, lock, diff, or review gate fails; or
- an unallowlisted tracked or generated file appears.

A failure does not authorize changing an artifact, adopting an observed
digest, trying the other algorithm, accepting both values, editing an old
document, retrying a formal attempt, or tuning to the result. Another
contradiction requires another explicit recovery design.

## File, commit, and identity boundaries

This design commit adds exactly:

```text
docs/superpowers/specs/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery-design.md
```

Its direct parent is:

```text
03115325f36da31b135b4593fb8df1689eac9a35
```

The future plan may add exactly:

```text
docs/superpowers/plans/2026-08-30-val-wave0-a11-preserved-inventory-ordering-semantics-recovery.md
```

Design, plan, and implementation are separate append-only commits. Author and
committer are exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, reset, rebase, squash, stash, cherry-pick, cleanup of preserved
evidence, push, merge, tag, release, or other-repository edit is permitted.

## Verification and evidence closure

Before the design commit:

- require exact parent `03115325f36da31b135b4593fb8df1689eac9a35`;
- require a clean starting worktree and only this new file changed;
- reproduce the five file-order and directory-order comparison tables using
  path-only reads;
- scan for placeholders, contradictory algorithm assignments, mutable
  artifact instructions, and digest conflicts;
- run `git diff --check`; and
- require the canonical worktree to remain clean.

After the design commit:

- require exact parent, one-file scope, author, and committer;
- require linked and canonical worktrees clean and staging empty;
- require the committed algorithm table and all five digest assignments to
  match this design;
- run `git show --check HEAD`; and
- make no implementation or runtime action.

Only after owner approval of the committed written spec may the new
implementation plan be written.

## Success criteria

This design succeeds when:

1. all five artifact trees remain byte-for-byte untouched;
2. attempts 1 through 4 retain their four v1 digests;
3. attempt 5 retains the exact ten records, 1,283 bytes, and v2 digest
   `e6a0...e64`;
4. the schema and registry bind an explicit closed algorithm ID per attempt;
5. v1 is deterministic, culture-independent, and rejects comparer collisions;
6. v2 remains ordinal and is not applied retroactively to frozen v1 records;
7. the full corrected Task 1 gate passes before any implementation edit;
8. the original seven-file, TDD, preservation, review, single-commit, and
   at-most-once diagnostic boundaries remain intact; and
9. no artifact, owner identity, launcher, Docker stage, GPU/model process,
   runtime attempt, Wave 1 object, remote, merge, or release is created by the
   recovery design itself.
