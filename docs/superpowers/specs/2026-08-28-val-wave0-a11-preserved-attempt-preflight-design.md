# Wave 0 A11 Preserved-Attempt Preflight Design

## Status and authority

The owner approved this design direction on 2026-08-28 after the checked-in A11
launcher failure-recovery candidate was committed and verified. This design
authorizes a written implementation plan and a CPU-only/TDD repair of the A11
launcher preflight. It does not authorize an A11 launcher invocation, Docker
build or run, cache download, GPU lease, model initialization, calibration or
validation replica, RDD access, Wave 1, remote operation, push, merge, tag,
Release, or publication.

The statistical replay mathematics, receipt schemas, model stack, phase order,
and Wave 1 boundary remain defined by
`docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`,
Section 5.2.15. The command, receipt, pipeline, and closure behavior repaired by
`docs/superpowers/specs/2026-08-28-val-wave0-a11-launcher-failure-recovery-design.md`
also remains unchanged.

The implementation starting point is:

- branch: `codex/wave0-model-contract`
- candidate: `f10822e67ee90013c8e7a9d423d97c64993e676a`
- original A11 specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- original A11 plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`
- launcher failure-recovery design: `5972b8453d8f33465c15f27f02e402315a3c886e`
- launcher failure-recovery plan: `200fd7907f5c49ae7f0c59450b49181f31358e2d`

The earlier failed attempt and its authorization remain immutable and unusable:

- run ID: `wave0-a11-calibration-20260828T045848083Z-b9917463`
- owner authorization: `OWNER-A11-RUNTIME-20260828-01`
- image tag: `vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463`
- image ID: `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`
- terminal: `WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`

A future runtime attempt still requires a separate owner review and a new
explicit `OwnerAuthorizationId`. The launcher and the executing agent must not
infer or synthesize that identifier.

## Observed blocker

The repaired launcher is CPU-verified, but its original single-attempt preflight
cannot admit a second attempt while preserving the first one.

`Resolve-A11Worktree` currently adds all of the following to
`existing_destinations`:

1. the `a11-runs` parent directory whenever it exists;
2. every `vision-active-learning-loop:wave0-a11-*` image tag; and
3. every `leases/wave0-a11-*` release or released record.

`Test-A11ReadOnlyPreflight` requires `existing_destinations` to be empty. The
approved failed attempt necessarily makes every one of those categories
nonempty. In addition, `Initialize-A11Phase` unconditionally creates the
calibration campaign parent; it therefore rejects the preserved, legitimate
`a11-runs` parent before creating a new child run.

Deleting, moving, renaming, completing, or repairing the failed attempt would
violate its immutable evidence contract. Relaxing the broad checks without
binding the prior attempt would allow undetected drift and would weaken the
no-clobber boundary. The launcher therefore needs a baseline-aware preflight,
not cleanup and not a blanket exception.

## Registered prior-attempt baseline

Before any future run identity is materialized, the read-only preflight must
require this exact prior A11 set:

- the only directory directly below `a11-runs` is
  `wave0-a11-calibration-20260828T045848083Z-b9917463`;
- its complete recursive inventory contains 48 regular non-link files and has
  canonical inventory SHA-256
  `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b`;
- `audit/79-historical-preservation-final.json` has SHA-256
  `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`;
- `leases/wave0-a11-calibration-20260828T045848083Z-b9917463.released`
  has SHA-256
  `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`;
- `leases/wave0-a11-calibration-20260828T045848083Z-b9917463.release.json`
  has SHA-256
  `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`;
- `78-failure-diagnostic.json`, `80-campaign-result.json`,
  `81-campaign-file-manifest.json`, and `82-campaign-closure.json` remain
  absent from that run;
- the only A11 image tag is the registered failed image tag above and it still
  resolves to the registered image ID; and
- no active `GPU-*.json` lease and no running project container exists.

The complete historical A2 through A10 baseline remains independently fixed at
64,306 files with inventory SHA-256
`e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`
and 21 images with inventory SHA-256
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.

The prior-attempt inventory rejects reparse points at the `a11-runs` parent,
failed-run root, every descendant directory, every file, and both lease-record
paths. Missing, extra, linked, renamed, or mutated prior A11 objects fail before
new phase identities or destinations are created.

## Design

### 1. Baseline-aware read-only host preflight

Replace the broad `existing_destinations` evidence with a closed
`prior_a11_attempt` evidence object. It records the registered run inventory,
fixed file records, A11 run-name inventory, A11 image tag and image ID inventory,
lease release records, closure-file absence, and link-safety result.

`Resolve-A11Worktree` continues to collect the protected Git, Docker Linux,
idle registered RTX 4090, running project container, active GPU lease, and
historical A2 through A10 evidence. `Test-A11ReadOnlyPreflight` accepts the
preserved parent only when every registered prior-attempt value is exact.
Unknown prior A11 runs, image tags, lease records, or changed bytes fail closed.

The evidence object remains an internal preflight surface. It does not amend a
runtime receipt schema or reinterpret the failed attempt as a closed success.

### 2. Exact fresh-destination gate

After the host preflight succeeds, `New-A11PhaseIdentity` may generate the two
in-memory phase identities. Before `Initialize-A11Phase` performs its first
filesystem write, a new `Test-A11PhaseDestinationsAbsent` helper checks both
identities as one atomic decision.

For calibration and validation it requires all of these exact destinations to
be absent:

- campaign root;
- image tag;
- cache root;
- lease lock path, released path, and release-record path;
- phase receipt, checkpoint, aggregate, audit, result, manifest, and closure
  roots implied by the campaign root.

The two identities must also have different run IDs, image tags, campaign roots,
cache roots, lease IDs, lease paths, timestamps, and nonces. A collision in
either phase prohibits initialization of both. An image-tag check is read-only
and distinguishes the expected not-found result from Docker command failure.

The generated strings are not evidence and create no runtime object. A failed
fresh-destination gate writes no campaign directory, audit, image, cache, lease,
receipt, or checkpoint.

### 3. Existing-parent-safe phase initialization

`Initialize-A11Phase` treats the `a11-runs` parent consistently for both phases:

- if the parent is absent during calibration initialization, create it once;
- if it exists, require a regular non-link directory;
- never overwrite, rename, or enumerate a prior child as the new phase; and
- create the exact fresh campaign child with no-clobber semantics.

The fresh-destination gate is defense in depth; `New-Item` and
`Write-A11NewText` continue to fail on an exact collision. The existing failed
run is never opened for write by initialization or closure.

### 4. Execution lineage

The future runtime still passes the original Section 5.2.15 specification and
plan commits to the launcher because those commits define the receipt schemas
and Tasks 7–8. The final source commit is the future implementation HEAD. Its
ancestry must contain, in order, the original A11 implementation, the launcher
failure-recovery design/plan/implementation, this design, its reviewed plan, and
its implementation commit.

The later written runtime authorization must name the final source commit, the
original specification and plan commits, both supplemental design/plan commit
pairs, the branch, both calibration and validation phases if both are
authorized, and one never-used owner authorization identifier. This external
authorization binding adds no receipt fields and does not weaken the launcher's
existing commit checks.

### 5. Failure behavior

Prior-baseline, protected-Git, Docker, GPU, lease, historical-preservation, or
fresh-destination failure stops before phase initialization and creates no new
runtime evidence. There is no retry and no cleanup.

After phase initialization, the existing repaired failure behavior remains
normative: release an acquired lease when possible, publish the complete 78–82
failure chain once, surface any closure error, preserve every artifact, prohibit
validation after calibration failure, and never invoke the launcher a second
time.

## Test architecture

CPU-only tests load the real production PowerShell functions through the
existing AST harness and replace only Docker/native-process and external
inventory boundaries. Mandatory RED/GREEN coverage is:

1. the current registered 48-file prior attempt, image, and two release records
   pass the host preflight;
2. a missing, extra, linked, renamed, or hash-mutated prior run file fails;
3. an unknown A11 run, image tag, or lease record fails;
4. a running project container or active `GPU-*.json` lease remains forbidden;
5. an exact calibration or validation campaign-root collision fails before
   initialization;
6. an exact image-tag or lease-path collision fails before initialization;
7. Docker inspection failure is distinct from a confirmed absent image tag;
8. calibration initialization accepts the verified existing non-link parent,
   preserves a sentinel prior child byte-for-byte, and creates only its fresh
   child;
9. a linked or non-directory campaign parent fails; and
10. campaign orchestration orders host preflight, identity generation, exact
    destination validation, and initialization without output leakage.

Existing launcher, receipt, closure, cache, replica, pipeline, statistical
replay, and complete CPU suites remain mandatory. No test may call a real Docker
build/run, GPU workload, model, external cache download, or A11 launcher entry
point.

## Tracked-file and commit boundaries

The design commit changes exactly this file. The future plan commit adds exactly
one corresponding file under `docs/superpowers/plans/`.

The implementation allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
tests/gates/test_wave0_a11_launcher.py
```

A third tracked implementation path is a hard stop for owner review. The design,
plan, and implementation are three append-only commits using:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, rebase, squash, reset, stash, history rewrite, cleanup, push, merge,
tag, Release, publication, or change to another repository is permitted.

## Verification and stopping gate

Before the implementation commit, require:

- focused RED then GREEN evidence for every new test;
- the complete launcher and original A11 focused suites;
- the complete CPU suite;
- targeted Black and Ruff;
- `uv lock --check` and `git diff --check`;
- PowerShell 7 and Windows PowerShell 5.1 parser success;
- exact two-file implementation scope and empty staging until the final commit;
- clean linked and canonical worktrees outside the candidate;
- complete recomputation of the registered failed-attempt, lease, historical
  artifact, and image baselines;
- no new A11 run, image, cache, lease, container, receipt, checkpoint, audit, or
  authorization identity; and
- Critical=0 and Important=0 review against this design, both earlier A11
  designs, and Section 5.2.15.

After the implementation commit, repeat the parser and launcher tests from the
committed tree and stop. Report the design, plan, and implementation commits and
all verification evidence. Do not invoke `scripts/run_wave0_a11.ps1`.

Only a later owner review with a new explicit `OwnerAuthorizationId` may
authorize one fresh launcher invocation covering the named phase or phases.
Even an A11 PASS stops at
`WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED` and does not
authorize RDD access or Wave 1.
