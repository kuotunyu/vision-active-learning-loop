# Wave 0 A11 steven004 Preserved-Attempt Inventory Recovery Implementation Plan

> **For Codex:** Execute with the `executing-plans` skill. This plan is
> owner-approved for Inline Execution. Stop on a preserved NO_GO, a newly
> required external authorization, or a newly required destructive action.
> Never invoke the formal launcher.

**Goal:** Extend the fail-closed A11 prior-attempt registry from four to five
attempts so the immutable `steven004` image-build failure and the complete
historical artifact/image envelope are independently and exactly proven.

**Architecture:** Keep the frozen historical canonicalizer unchanged at
64,306 non-A11 files and 21 non-A11 images. Extend the separate
`prior_a11_attempts` registry with one exact, canonical ten-file attempt record.
Production collection and preflight validation both close over all five
attempts, and `steven004` becomes a consumed authorization. No artifact is
modified and no runtime is started.

**Tech stack:** PowerShell 7 and Windows PowerShell 5.1 parser, Python 3.12,
pytest, Black, Ruff, uv, Git, Docker Desktop read-only image inspection.

## Frozen identities and scope

```text
RECOVERY_PARENT|3d6bf48df416e4673537c172f38cb9adf51819f6
DESIGN_COMMIT|feb9be992dd68a2b6c703cb16ca2fcf0965e586d
DESIGN_BLOB|45e79838ebef85e36a6226bf89451cd16f172bd9
DESIGN_IDENTITY|8627|7c395f56b7e538a5e3ed2ec7d7b0d7413bf46838885f05708c67c0d0a7bbdcfd
SPECIFICATION_COMMIT|b59b0d4407b98b460f6166ea7288ba6021dc7a78
ORIGINAL_PLAN_COMMIT|7dbd3a7576ea76beccfc64f748c4e495259ea89b
FIFTH_SOURCE_COMMIT|ed6f157c7cbd545895b9d047f6e094968a1f9d94
FIFTH_OWNER|steven004
FIFTH_RUN_ID|wave0-a11-calibration-20260829T123151657Z-bf516632
FIFTH_PEER_ID|wave0-a11-validation-20260829T123151664Z-7af53ca8
FIFTH_RUN_INVENTORY|10|e6a0b5bb9e0781c11989962d117fd0015d3411223c46d457dc4d1e37eabc0e64
HISTORICAL_FILE_INVENTORY|64306|e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
HISTORICAL_IMAGE_INVENTORY|21|9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
ARTIFACT_TREE_PARTITION|64306+48+5+60+137+10+6=64572
```

The implementation tracked-file allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
tests/gates/test_wave0_a11_launcher.py
```

A third implementation path is a hard stop. Docs are committed separately.
The implementation commit identity is exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

The implementation subject is exactly:

```text
fix: register A11 steven004 preserved attempt
```

## Exact fifth-attempt contract

Production and test-owned preflight evidence must use these ordered file
records, without deriving an expected value from production output:

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

Closed fifth-attempt state:

```text
state=image-build-failure
directories=audit,wave0,wave0/checkpoints,wave0/model_cache,wave0/receipts
image_tags_present=0
lease_paths_present=0
validation_present=false
payload_file_paths_present=0
closure_paths_present=78,79,80,81,82
latest_write_utc=2026-08-29T13:39:47.0148945Z
links_absent=true
```

## Task 1: Re-enter and prove the design boundary

**Files:** read only.

1. Require branch `codex/wave0-model-contract`, HEAD equal to the design
   commit, linked and canonical worktrees clean, and staging empty.
2. Require the design direct parent, one-path scope, subject, author,
   committer, blob, byte count, SHA-256, UTF-8/LF form, and exact frozen
   records above.
3. Require no recovery plan path yet and no new A11 run, image, lease,
   container, or `steven005` identity materialization.
4. Read the fifth identity and all ten files. Recompute its canonical JSON and
   require exact count/digest, directory inventory, closure, timestamp, link
   absence, and absent peer/image/lease/payload destinations.
5. Recompute the complete physical partition and require exactly 64,572
   ordinary files: 64,306 historical, 260 A11 run files, and 6 released lease
   files.
6. Require Docker `linux|29.6.1`, exact 21-image historical digest, exact three
   earlier A11 tags, and absent fifth calibration/validation tags.

Any difference stops before plan commit.

## Task 2: Commit this implementation plan

**Files:**

- Create and commit only:
  `docs/superpowers/plans/2026-08-31-val-wave0-a11-steven004-preserved-attempt-inventory-recovery.md`.

1. Read the complete plan and reject unresolved tokens, inconsistent frozen
   identities, missing TDD steps, runtime commands, or scope wider than the two
   implementation paths.
2. Require UTF-8 without BOM, LF-only endings, one final LF, and
   `git diff --check` success.
3. Commit with exact identity and subject:

```text
docs: plan A11 steven004 preserved attempt recovery
```

4. Require the plan commit direct parent to be the design commit and its sole
   path to be this plan. Require both worktrees clean.

## Task 3: Write test-owned five-attempt evidence and prove RED

**Files:**

- Modify: `tests/gates/test_wave0_a11_launcher.py`.
- Read only: `scripts/run_wave0_a11.ps1`.

1. Add independent fifth-attempt constants: run/peer IDs, tags, owner, source,
   run digest, exact ten records, directories, closures, and timestamp.
2. Extend `_prior_attempts()` to return five ordered runs, five authorization
   records, and five closed attempt objects while retaining the exact three
   image tags and six lease filenames.
3. Rename the positive tests from four to five attempts and require the new
   fifth closed-key schema.
4. Extend consumed-owner coverage with `steven004`.
5. Add mutations for every fifth-attempt identity, record/digest, ordering,
   presence/absence, closure, timestamp, and link field. Add structural tests
   for deleted/substituted fifth records and moved fifth authorization.
6. Extend the filesystem-backed inventory fixture with a fifth run containing
   ten ordinary files, five directories, full closure, and no image/lease/peer
   materialization. Add link, payload, validation, image, lease, missing
   closure, extra directory, and extra-file defects.
7. Run without Python bytecode/cache output:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'preflight or prior_attempt'
```

Expected RED: test-owned five-attempt evidence is rejected by the current
four-attempt production launcher. A fixture, import, PowerShell availability,
or unrelated test failure is invalid RED.

## Task 4: Implement the minimal closed fifth-attempt registry

**Files:**

- Modify: `scripts/run_wave0_a11.ps1`.

1. In `Get-A11PriorAttemptInventory`, add only the fifth run identity/root,
   exact ordinary-path checks, records/directories/payload/closure/image/lease/
   validation observations, registered paths, latest timestamp, authorization
   evidence, and the `image-build-failure` attempt object.
2. Expand exact root, identity, authorization, and attempt cardinalities from
   four to five. Keep the image list exactly three and the lease list exactly
   six.
3. Use the existing `Get-A11JsonSha256` unchanged. Do not introduce a second
   serializer or update the historical file/image constants.
4. In `Test-A11ReadOnlyPreflight`, independently add fifth expected identities,
   closed keys, exact records, canonical digest, absences, closure, timestamp,
   and owner-consumption check.
5. Do not change parameter surfaces, campaign code, retries, build/run/lease
   logic, artifact writers, Task 7-8 capability, or any file outside the two
   allowlisted paths.

## Task 5: Prove focused GREEN and mutation closure

**Files:** the two implementation paths only.

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
```

Require every positive, consumed-owner, mutation, structural, fixture-backed,
link, Docker-failure, and no-retry adapter test to pass. These tests mock native
Docker boundaries and must not use Docker or GPU.

## Task 6: Complete verification, preservation rehash, and implementation commit

**Files:** stage and commit exactly the two implementation paths only after
all gates pass.

1. Run the original Task 6 CPU gates:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider
uvx --offline black --check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uvx --offline ruff check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  src/vision_active_learning_loop/artifacts/statistical_replay_receipts.py `
  src/vision_active_learning_loop/artifacts/receipts.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
```

2. Parse `scripts/run_wave0_a11.ps1` under `pwsh` and `powershell`; both error
   arrays must be empty.
3. Require the exact two-path uncommitted scope, empty staging, no `.pyc`, no
   `__pycache__`, no pytest cache, and both worktrees otherwise clean.
4. Review the design, this plan, original specification Section 5.2.15, and
   original plan Tasks 1-6 line-by-line. Require Critical=0 and Important=0.
5. With the implementation still uncommitted, rerun the exact fifth-attempt
   canonicalization, physical 64,572-file partition, complete 64,306-file
   historical hash, 21-image hash, three A11 image identities/labels, fifth
   image absence, lease absence, project-container absence, and Git protection
   checks. Any drift is NO_GO; do not repair it.
6. Stage exactly the two allowlisted paths, run `git diff --cached --check`, and
   commit once with the frozen identity and subject.
7. Verify the implementation commit direct parent is this plan commit, author
   and committer are exact, its sole diff is the two-path allowlist, both
   worktrees are clean, Docker has no project container, no lease is active,
   and no new A11 runtime object exists.
8. Stop and report commit identities and all gate results. Do not invoke Tasks
   7-8. The stale `steven005` authorization is not reusable; a new runtime
   source commit and a separately approved new `OwnerAuthorizationId` are
   required.
