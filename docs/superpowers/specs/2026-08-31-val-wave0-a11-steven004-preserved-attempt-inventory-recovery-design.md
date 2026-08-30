# Wave 0 A11 steven004 Preserved-Attempt Inventory Recovery Design

## Status and authority

The owner approved approach A and authorized design, written specification,
implementation planning, TDD, one implementation commit, and end-to-end
verification on 2026-08-31. This recovery preserves the failed `steven004`
attempt and the later `steven005` preflight NO_GO. It is not a runtime attempt
and authorizes no formal launcher invocation, Docker build, container start,
GPU observation, lease acquisition, model campaign, Wave 1, push, merge, or
release.

Frozen repository identity at entry:

- linked worktree: `<repo>\.worktrees\wave0-model-contract`;
- canonical worktree: `<repo>`;
- branch: `codex/wave0-model-contract`;
- recovery parent commit: `3d6bf48df416e4673537c172f38cb9adf51819f6`;
- original specification commit: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`;
- original plan commit: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`.

The `steven005` authority remains bound to source commit
`3d6bf48df416e4673537c172f38cb9adf51819f6`. Its read-only preflight stopped
before the formal launcher because the Docker Linux API pipe was absent. The
formal launcher invocation count and `steven005` identity-materialization count
are both zero. This recovery will make that source identity stale and will stop
for a separately approved source commit and fresh `OwnerAuthorizationId`.

## Preserved fifth attempt

The fifth preserved calibration root is:

```text
D:\vision-active-learning-loop-artifacts\wave0\a11-runs\wave0-a11-calibration-20260829T123151657Z-bf516632
```

Its identity preregisters validation root
`wave0-a11-validation-20260829T123151664Z-7af53ca8` and binds both phases to:

```text
source_commit=ed6f157c7cbd545895b9d047f6e094968a1f9d94
specification_commit=b59b0d4407b98b460f6166ea7288ba6021dc7a78
plan_commit=7dbd3a7576ea76beccfc64f748c4e495259ea89b
owner_authorization_id=steven004
```

The calibration root has exactly five ordinary directories, ten ordinary
files, no reparse point, and no payload below `wave0`. Canonical records are
sorted by full path, represented as ordered `path`, `size`, `sha256` objects,
serialized by PowerShell `ConvertTo-Json -Depth 6 -Compress`, encoded as UTF-8,
and hashed with SHA-256. That process yields:

```text
run_file_count=10
run_inventory_sha256=e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64
latest_write_utc=2026-08-29T13:39:47.0148945Z
```

Exact file records:

```text
audit/00-identity.json|2873|9fb7f3572e8341af986f24473c2ee66933d17d736b632b95e0c3a64c91e9d67d
audit/01-gpu-preflight.json|125|de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7
audit/10-build.json|1234|3ef76de20f776e977f172d2ba9c3277185db693bd3a7fc9949bfe42b39af6f68
audit/10-build.stderr.log|865248|e53b9598c39343785aea27be4381f1755accb5f91553630af64d1b71712e82c5
audit/10-build.stdout.log|0|e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
audit/78-failure-diagnostic.json|766|cc0e391fdb743dac2c2c80362d690703da08b9ae38c5a8294031ace8bef9c311
audit/79-historical-preservation-final.json|301|927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d
audit/80-campaign-result.json|751|346b4aa69f8e6c440262f463e4cbb756f39dd1dde0df51124f533093ffe8b651
audit/81-campaign-file-manifest.json|1885|8be8ee5adadb296d269c5dda0c1827d8ef9ee56d024872aa3ee6e0cb74bbedd6
audit/82-campaign-closure.json|659|a3ba8ef72165dde8443ac85ffcaaf27b307afd15af10c8a0d347ca7f30cfcaa1
```

`audit/10-build.json` records exit code 1. The diagnostic and closure record
`WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`. The preregistered validation
root, both registered image tags, all active/released/release lease paths, and
all success receipts are absent. The five closure files are present. The
closed state name is therefore `image-build-failure`.

## Root cause

The launcher at the recovery parent commit was last changed before the
`steven004` attempt. `Get-A11PriorAttemptInventory` and
`Test-A11ReadOnlyPreflight` close over exactly four runs and four consumed
owner authorizations, ending at `steven003`. The filesystem now contains a
fifth immutable run. The launcher consequently rejects the true preserved
inventory before a new runtime can be considered.

This is registry lag, not artifact corruption. The original historical
canonicalizer intentionally excludes `a11-runs/*`, `leases/wave0-a11-*`, and
the active GPU lock path. The complete ordinary-file partition is:

```text
historical files                            64306
four already registered A11 run files        250
steven004 A11 run files                        10
released/release A11 lease files                6
total artifact-tree files                   64572
```

The historical file envelope therefore remains 64,306 files with frozen
digest `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`.
Fresh Docker inspection also proves the historical image envelope remains 21
images with digest
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.
The A11 image set remains the three earlier calibration tags; both `steven004`
registered tags are absent.

## Options considered

### A. Extend the closed registry and retain the frozen historical envelope

Add one exact fifth-attempt record to the existing prior-attempt registry,
expand cardinality and owner-consumption checks from four to five, and leave
the historical canonicalization/count/digest unchanged. This preserves the
existing boundary and makes every new fact independently testable.

### B. Fold A11 evidence into the historical digest

Recompute one new digest over all 64,572 files. This would invalidate the
frozen historical boundary and erase the distinction between protected prior
data and append-only A11 attempt evidence. It is rejected.

### C. Ignore the fifth run or delete it

Either choice would make preflight pass by hiding evidence. It violates the
preservation contract and is rejected.

## Decision and architecture

Use approach A. Change only the two existing implementation-allowlist paths:

```text
scripts/run_wave0_a11.ps1
tests/gates/test_wave0_a11_launcher.py
```

`Get-A11PriorAttemptInventory` will:

1. require the fifth calibration root as an ordinary non-linked tree;
2. parse its exact identity and require matching current/peer authorization;
3. canonicalize all ten file records using the existing serializer;
4. require the exact five-directory, zero-payload, zero-image, zero-lease,
   no-validation, five-closure state;
5. append exact authorization evidence and an `image-build-failure` attempt;
6. keep the existing exact three-image and six-lease inventories unchanged.

`Test-A11ReadOnlyPreflight` will independently revalidate the fifth record:
closed keys, identities, registered paths, all ten ordered records, canonical
digest, directory inventory, absent resources, closure inventory, timestamp,
and link absence. It will reject `steven004` as consumed while accepting only a
fresh owner ID. The 64,306-file and 21-image historical envelope checks remain
byte-for-byte unchanged.

## TDD and verification

RED first updates test-owned evidence to five attempts and adds exact
`steven004` mutation/structural cases. The current four-attempt production
launcher must reject that evidence. Production code is changed only after a
valid RED.

GREEN requires the focused launcher suite to pass without Docker or GPU use.
Full verification then runs the original Task 6 focused and complete pytest
suites, Black, Ruff, `uv lock --check`, `git diff --check`, and both PowerShell
parsers. A live read-only preservation gate recomputes the exact fifth attempt,
the 64,306-file digest, the 21-image digest, A11 image absence, lease absence,
clean Git, and exact tracked scope.

Docs use separate append-only design and plan commits. Implementation uses
one append-only commit containing exactly the two allowlisted paths and exact
identity:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No implementation commit is created unless every gate passes.

## Failure handling and stop boundary

Any count, record, digest, ordering, identity, path, parser, test, lint, Docker
readiness, image, lease, or cleanliness mismatch is a preserved NO_GO. Do not
repair existing artifacts, weaken a comparison, retry a formal attempt, or
reuse `steven005`. On success, stop after the implementation commit and final
verification. A later runtime requires a separately approved exact new source
commit and new `OwnerAuthorizationId`.
