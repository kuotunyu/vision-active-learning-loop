# Wave 0 A11 Preserved-Inventory Digest Inconsistency Recovery Design

**Status:** Approved architecture design; written-spec review pending

**Date:** 2026-08-30

**Branch:** `codex/wave0-model-contract`

**Parent commit:** `101bb79369399cc3947f1c667f0a11988f916638`

## Purpose

Recover the A11 runtime-transport implementation path from an internally
inconsistent preserved-attempt digest without modifying any historical
artifact, weakening the preservation boundary, or starting a runtime action.

The approved runtime-transport design and implementation plan freeze the fifth
attempt's complete ten-file record vector and also freeze an aggregate run
inventory SHA-256. The exact records still match the external artifact
byte-for-byte, but the aggregate value in those documents cannot be reproduced
from those records by the serialization algorithm required by the plan.

This design supersedes only that inconsistent digest declaration and the Git
lineage made obsolete by this additional recovery cycle. Every other approved
runtime-transport requirement remains unchanged.

## Authority and non-authority

The owner approved an append-only recovery design with these constraints:

- do not modify an existing artifact;
- prove the correction from exact records and canonical serialization;
- rerun the complete Task 1 entry gate after the correction; and
- retain the existing Git history rather than rewriting an approved commit.

This design does not authorize an `OwnerAuthorizationId`, launcher invocation,
Docker build or run, GPU lease, model initialization, A11 runtime attempt,
dependency diagnostic, Wave 1 action, push, merge, release, tag, rebase, reset,
stash, or change to another repository.

## Frozen Git and evidence context

The recovery starts from:

```text
branch                         codex/wave0-model-contract
runtime-transport design      db047dcb8ad602fc4ac316a743ab4ddec3168cd5
runtime-transport plan        e31fc0c10fe34b480f7b2ee3d12a2e55530c6350
diagnostic-root erratum        101bb79369399cc3947f1c667f0a11988f916638
attempt 5 source              ed6f157c7cbd545895b9d047f6e094968a1f9d94
approved A11 specification    b59b0d4407b98b460f6166ea7288ba6021dc7a78
original A11 plan             7dbd3a7576ea76beccfc64f748c4e495259ea89b
```

The linked and canonical worktrees were clean when this recovery was designed.
The existing artifact root remains read-only:

```text
D:\vision-active-learning-loop-artifacts\wave0
```

The separate dependency-diagnostic root introduced by the preceding erratum
does not exist and remains outside the artifact baseline:

```text
D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics
```

## Failure evidence and root cause

The corrected Task 1 lineage gate passed at erratum commit
`101bb79369399cc3947f1c667f0a11988f916638`. The preservation gate then
rehash-verified attempts 1 through 4 before stopping at attempt 5.

For attempt 5, the observed state is:

```text
run ID              wave0-a11-calibration-20260829T123151657Z-bf516632
files               10
directories         5
links                0
latest write UTC     2026-08-29T13:39:47.0148945Z
canonical bytes      1283
computed SHA-256     e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64
frozen SHA-256       b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448
```

The five exact directories still equal the approved declaration:

```text
audit
wave0
wave0/checkpoints
wave0/model_cache
wave0/receipts
```

The ten exact records still equal the approved declaration:

```json
[
  {
    "path": "audit/00-identity.json",
    "size": 2873,
    "sha256": "9fb7f3572e8341af986f24473c2ee66933d17d736b632b95e0c3a64c91e9d67d"
  },
  {
    "path": "audit/01-gpu-preflight.json",
    "size": 125,
    "sha256": "de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7"
  },
  {
    "path": "audit/10-build.json",
    "size": 1234,
    "sha256": "3ef76de20f776e977f172d2ba9c3277185db693bd3a7fc9949bfe42b39af6f68"
  },
  {
    "path": "audit/10-build.stderr.log",
    "size": 865248,
    "sha256": "e53b9598c39343785aea27be4381f1755accb5f91553630af64d1b71712e82c5"
  },
  {
    "path": "audit/10-build.stdout.log",
    "size": 0,
    "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  },
  {
    "path": "audit/78-failure-diagnostic.json",
    "size": 766,
    "sha256": "cc0e391fdb743dac2c2c80362d690703da08b9ae38c5a8294031ace8bef9c311"
  },
  {
    "path": "audit/79-historical-preservation-final.json",
    "size": 301,
    "sha256": "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d"
  },
  {
    "path": "audit/80-campaign-result.json",
    "size": 751,
    "sha256": "346b4aa69f8e6c440262f463e4cbb756f39dd1dde0df51124f533093ffe8b651"
  },
  {
    "path": "audit/81-campaign-file-manifest.json",
    "size": 1885,
    "sha256": "8be8ee5adadb296d269c5dda0c1827d8ef9ee56d024872aa3ee6e0cb74bbedd6"
  },
  {
    "path": "audit/82-campaign-closure.json",
    "size": 659,
    "sha256": "a3ba8ef72165dde8443ac85ffcaaf27b307afd15af10c8a0d347ca7f30cfcaa1"
  }
]
```

Three independent inputs produce the same canonical payload and digest:

1. records freshly observed from the read-only attempt-5 directory;
2. the record vector embedded in the approved implementation plan; and
3. a manual encoder that does not call PowerShell `ConvertTo-Json`.

The production-compatible PowerShell encoder and the independent manual
encoder produce byte-identical output. Both produce 1,283 UTF-8 bytes and
SHA-256
`e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64`.
No prefix containing one through ten of the ordered records produces the
frozen `b4c894...` value.

Repository history shows that the unreproducible value first appears in the
runtime-transport design commit and is then copied into its plan. It is not a
digest stored by the preserved attempt-5 evidence. The failure therefore lies
at the specification boundary: the aggregate constant contradicts the exact
record vector and the stated serialization algorithm. There is no evidence of
artifact drift, and artifact repair is forbidden.

## Approaches considered

### Selected: append-only supersession plus a canonical test vector

Add this recovery design and a subsequent recovery implementation plan. Leave
all earlier commits and documents in Git history. The new documents explicitly
supersede the attempt-5 aggregate value, define the byte contract, and require
the corrected full entry gate before any implementation file changes.

This preserves auditability, retains the aggregate integrity check, and limits
the correction to the proven contradiction.

### Rejected: remove the aggregate digest

Exact records are stronger than an unexplained aggregate by themselves, but
removing the aggregate would weaken the common five-attempt registry contract
and create a state-specific exception. The inconsistency can be resolved
without removing this defense.

### Rejected: adopt a new JSON canonicalization standard for all attempts

Replacing the established inventory serializer with RFC 8785 or another new
standard would require recomputing attempts 1 through 4 and expand the approved
implementation scope. The existing algorithm already reproduces their frozen
digests. A portfolio-wide serialization migration is unnecessary for this
recovery.

## Canonical run-inventory byte contract

The aggregate run inventory SHA-256 is defined over a JSON array built as
follows:

1. Resolve the run root to an absolute path without modifying it.
2. Recursively enumerate regular files. Reject every reparse point or link at
   the run root, in an ancestor, or in a descendant.
3. For each file, create one ordered record with exactly these fields:
   `path`, `size`, `sha256`.
4. `path` is the run-root-relative path with `/` separators. It is not rooted,
   contains no `.` or `..` segment, and uses the observed case unchanged.
5. `size` is a non-negative base-10 integer with no quoting or alternate
   numeric representation.
6. `sha256` is the lowercase 64-character SHA-256 of the exact file bytes.
7. Sort records by `path` using `StringComparer.Ordinal`.
8. Serialize exactly one JSON array. Each record retains the field order
   `path,size,sha256`. Emit no insignificant whitespace.
9. Encode that JSON string as strict UTF-8 without a BOM and without a final
   line terminator.
10. Compute SHA-256 over those exact bytes and render lowercase hexadecimal.

The serializer is not general-purpose JSON canonicalization. It is a narrow,
closed encoding of a validated record type. The registry file's own byte hash
is a separate contract and must not be confused with this run-inventory hash.

## Canonical attempt-5 test vector

The ten records above, in the displayed order and shape, are the normative
test vector:

```text
record count          10
canonical byte count  1283
canonical SHA-256     e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64
superseded SHA-256    b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448
```

The superseded value must never be accepted as the digest of this record
vector. It may remain in historical commits and may be mentioned only as
superseded failure evidence in new documents or tests.

## Recovery units

### Unit A: append-only specification and plan lineage

This design commit must be the direct child of
`101bb79369399cc3947f1c667f0a11988f916638`, change only this new design file,
and use the approved author and committer identity:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

After written-spec approval, one new implementation plan commit must be the
direct child of this design commit and add only its new plan file. The plan
must supersede only:

- the attempt-5 run inventory digest;
- the original Task 1 check that consumes that digest; and
- the implementation-parent lineage invalidated by this recovery cycle.

The implementation remains one commit changing exactly the same seven paths
approved by the runtime-transport plan:

```text
configs/a11/preserved-attempts.json
schemas/a11-preserved-attempts.schema.json
scripts/run_uv_sync_with_retries.py
scripts/run_wave0_a11.ps1
docker/wave0.Dockerfile
tests/gates/test_wave0_a11_launcher.py
tests/scripts/test_run_uv_sync_with_retries.py
```

No old design or plan file is edited. The new plan references the earlier
documents and explicitly records the narrow supersession.

### Unit B: corrected read-only Task 1 entry gate

Before modifying any of the seven implementation paths, the new plan must
rerun the complete Task 1 entry gate. It must require:

1. exact design/plan/erratum/recovery lineage and commit scopes;
2. clean linked and canonical worktrees and empty staging;
3. exact `uv.lock` SHA-256
   `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`;
4. all five run roots, their exact file/directory counts, inventory digests,
   latest-write values, identities, and absence rules;
5. for attempt 5, exact equality of the ten records and five directory names
   above before computing the aggregate;
6. byte equality between the production-compatible and independent attempt-5
   canonical encoders;
7. exact attempt-5 canonical byte count and corrected digest;
8. exactly three A11 images with their frozen IDs;
9. exactly six A11 lease-history files with their frozen hashes;
10. zero validation roots, active leases, project containers, numeric CUDA
    compute processes, links, or dependency-diagnostic identities;
11. exactly 64,306 historical non-A11 files with SHA-256
    `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`;
12. exactly 21 historical images with SHA-256
    `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`;
    and
13. the complete CPU baseline with `PYTHONDONTWRITEBYTECODE=1` and
    `-p no:cacheprovider`.

The entry report is evidence only. It creates no repository file, artifact,
identity, run, lease, image, container, or diagnostic directory.

### Unit C: TDD binding of the canonical vector

The subsequent implementation retains the original runtime-transport TDD
sequence and adds these RED-before-GREEN requirements to the launcher tests:

- the exact ten-record vector produces 1,283 bytes and the corrected digest;
- the superseded digest is rejected;
- changing any record path, size, file digest, record order, field order, JSON
  shape, whitespace, UTF-8 BOM, or final newline changes or invalidates the
  canonical payload;
- path ordering is ordinal and independent of current culture;
- the registry's fifth record carries the corrected digest;
- attempts 1 through 4 retain their exact approved digests; and
- unit tests use embedded fixtures and never read the external artifact root.

Production code must build records with the same closed field order and use
one explicit ordinal sorter. It must not learn expected values from observed
artifacts, update the registry, accept both digests, or special-case ordinal 5
after the registry has been loaded.

## Data flow

```text
approved exact records
        |
        v
closed record validation --failure--> preserved NO_GO
        |
        v
ordinal path sort
        |
        v
compact ordered JSON array
        |
        v
strict UTF-8 bytes (no BOM/newline)
        |
        +--> byte count == 1283 --failure--> preserved NO_GO
        |
        v
SHA-256 == e6a0...e64 --failure--> preserved NO_GO
        |
        v
complete Task 1 preservation and CPU gates
        |
        +--> failure: stop, no implementation
        |
        v
original runtime-transport Tasks 2-6 become eligible
```

## Failure handling

Every comparison is fail-closed. Any of these conditions produces a preserved
`NO_GO` and stops before implementation:

- an exact record or directory differs;
- the two canonical encoders differ at any byte;
- the canonical byte count or corrected digest differs;
- an earlier attempt, image, lease, historical baseline, Git state, lockfile,
  Docker state, or GPU-idle condition differs;
- a link or extra object appears; or
- a baseline CPU test fails.

A `NO_GO` is not permission to update an artifact, regenerate evidence, change
the expected record vector, weaken a check, retry a formal attempt, or tune a
constant to a newly observed state. A new contradiction requires another
explicit recovery design.

## Verification and evidence closure

Before the design commit:

- require parent `101bb79369399cc3947f1c667f0a11988f916638`;
- require only this new file changed;
- validate the embedded JSON record vector;
- reproduce the 1,283-byte payload and corrected digest from that vector;
- scan for placeholders, ambiguous authority, and conflicting digest values;
- run `git diff --check`; and
- require the canonical worktree to remain clean.

After the design commit:

- require the exact parent, one-file scope, author, and committer;
- require linked and canonical worktrees clean and staging empty;
- re-run the embedded-vector proof from the committed document; and
- require `git show --check HEAD` to pass.

Only after the owner approves the committed written spec may an implementation
plan be written. Only after that plan is approved may the corrected Task 1 gate
run. No implementation or runtime eligibility exists before those approvals.

## Success criteria

This recovery design succeeds when:

1. the exact attempt-5 records remain unchanged;
2. two independent encoders reproduce the same 1,283 canonical bytes;
3. those bytes hash to
   `e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64`;
4. the unreproducible `b4c894...` value is retained only as superseded history;
5. the full corrected Task 1 entry gate passes from a clean repository before
   implementation;
6. the original seven-path implementation, TDD, preservation, review, and
   single-commit boundaries remain intact; and
7. no artifact, runtime, GPU, Docker stage, owner identity, diagnostic, Wave 1
   object, remote, merge, or release is created by the recovery itself.
