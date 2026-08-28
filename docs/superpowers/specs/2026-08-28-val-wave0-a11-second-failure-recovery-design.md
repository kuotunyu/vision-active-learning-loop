# Wave 0 A11 Second Failure-Recovery Design

## Status and authority

The owner approved this design on 2026-08-28 after the one authorized A11
attempt using `OwnerAuthorizationId=steven001` terminated before calibration.
This document authorizes only a written implementation plan and a subsequent
CPU-only, TDD implementation of the recovery described here. It does not
authorize repairing or reusing either preserved A11 run, invoking the A11
launcher, building an image, downloading the model cache, acquiring a GPU
lease, running a model campaign, accessing RDD, starting Wave 1, or performing
any push, merge, tag, release, or publication.

Plan drafting begins only after the owner approves this written specification.
Code repair begins only after the owner approves the resulting implementation
plan.

A future runtime attempt requires a separate owner review after the recovery
implementation is committed and verified. That review must supply a new,
previously unused owner authorization identifier. `steven001` is consumed and
must never be reused.

## Authoritative starting state

The isolated implementation worktree is
`<repo>\.worktrees\wave0-model-contract`
on branch `codex/wave0-model-contract` at source commit
`1445a90b799b6306d6c1f7abc94b4a201afe5dc6`. Its direct parent is preserved-
attempt plan commit `7330b16d495b478a4c2fee52fbeb7080773a406d`.
The linked and canonical worktrees are clean. The reviewed original A11
specification and plan remain
`b59b0d4407b98b460f6166ea7288ba6021dc7a78` and
`7dbd3a7576ea76beccfc64f748c4e495259ea89b` respectively.

The historical non-A11 baseline remains exactly 64,306 files with inventory
SHA-256
`e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`,
and 21 historical images with inventory SHA-256
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.
Neither recovery may redefine, regenerate, or weaken this baseline.

Two immutable A11 calibration attempts now exist.

### Preserved attempt 1: launcher-stage failure

- Run ID: `wave0-a11-calibration-20260828T045848083Z-b9917463`
- Source commit: `2622e402e4f536b94326ac34f9b20c90b513002b`
- File count: 48
- Run inventory SHA-256:
  `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b`
- Image tag:
  `vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463`
- Image ID:
  `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`
- Final historical-preservation record SHA-256:
  `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`
- Released lease SHA-256:
  `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`
- Release record SHA-256:
  `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`
- Closure files `78`, `80`, `81`, and `82` are absent and remain absent by
  contract.

### Preserved attempt 2: image-build timeout

- Run ID: `wave0-a11-calibration-20260828T114911289Z-fe8b7000`
- Preregistered validation ID:
  `wave0-a11-validation-20260828T114911296Z-3107aff0`
- Source commit: `1445a90b799b6306d6c1f7abc94b4a201afe5dc6`
- Owner authorization identifier: `steven001`
- File count: 5
- Run inventory SHA-256:
  `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b`
- Build audit SHA-256:
  `d6fe3823a1d4f7980feecf0531d210158630287b2d6f9379353fbff0c7edae66`
- Build stderr SHA-256:
  `50d3bf5bf6cfc3dcde1edca56c4bd84db0e7da77fd108dd47abdd1db6b9b881e`
- Build stdout SHA-256:
  `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- The registered image tag was never created.
- No GPU lease, container, receipt, checkpoint, cache, calibration replica,
  validation directory, or validation replica exists.
- Closure files `78-failure-diagnostic.json` through
  `82-campaign-closure.json` are all absent.
- The latest file modification time is `2026-08-28T12:17:12.8122776Z`.

The five files and their registered hashes are:

| Relative path | Size | SHA-256 |
| --- | ---: | --- |
| `audit/00-identity.json` | 2,873 | `df1b6f37bfd9f7bce399f3a8b481bba564b5cacdd397ca82723100802b4bcec3` |
| `audit/01-gpu-preflight.json` | 125 | `de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7` |
| `audit/10-build.json` | 1,234 | `d6fe3823a1d4f7980feecf0531d210158630287b2d6f9379353fbff0c7edae66` |
| `audit/10-build.stderr.log` | 865,210 | `50d3bf5bf6cfc3dcde1edca56c4bd84db0e7da77fd108dd47abdd1db6b9b881e` |
| `audit/10-build.stdout.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

No future code or operation may backfill, close, delete, rename, retag, move,
reuse, or reinterpret either preserved attempt. Their different partial states
are evidence, not cleanup candidates.

## Observed failures and root causes

### 1. Bounded network operation was too short for a CUDA wheel

The second attempt's unique Docker build reached `wave0.Dockerfile:32` and
executed `uv sync --frozen --no-dev --no-install-project`. `uv` failed while
downloading and extracting
`nvidia-cusolver-cu12==11.7.1.2`. The audit explicitly reports a network
timeout and `UV_HTTP_TIMEOUT (current value: 30s)`. The build returned exit code
1, and the launcher correctly did not inspect a new image, acquire the GPU
lease, or start replicas.

The dependency graph, locked version, base-image digest, and no-cache build
contract remain valid. The defect is the absence of a reviewed timeout suitable
for multi-hundred-megabyte CUDA wheels. No evidence justifies an automatic
rebuild, unbounded timeout, dependency change, alternative index, mutable
wheelhouse, or cache reuse.

### 2. Failure closure used a scalar under StrictMode

`Close-A11Phase` constructs its initial error list through an `if` expression:

```powershell
$ErrorList = if ([string]::IsNullOrWhiteSpace($Failure)) { @() } else { @($Failure) }
```

PowerShell pipeline enumeration unwraps the non-empty, single-element result to
`System.String`. With the production script's
`Set-StrictMode -Version Latest`, `$ErrorList.Count` then raises
`The property 'Count' cannot be found on this object`. Both PowerShell 7.6.4
and Windows PowerShell 5.1 reproduce this behavior.

The launcher surfaced the closure exception exactly once and returned
`WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`, so validation remained forbidden.
However, the exception occurred before the first closure publication; records
78 through 82 were therefore absent.

### 3. The test harness omitted the production StrictMode contract

The AST-based production-function harness sets `$ErrorActionPreference='Stop'`
but does not set StrictMode. Outside StrictMode, PowerShell exposes scalar
collection adaptation and the existing single-failure closure test passes.
Consequently, the test exercised the production function text under different
language semantics from the launcher entry point.

### 4. The current preflight admits exactly one prior A11 attempt

`Get-A11PriorAttemptInventory` and `Test-A11ReadOnlyPreflight` are hard-coded to
one run, one A11 image, and two lease-history files. That was correct before the
second attempt. It is now intentionally false. A future fresh attempt must be
blocked until the launcher binds both immutable attempts and their distinct
states; merely changing an expected run count would not provide sufficient
evidence.

## Approaches considered

### Selected: complete three-boundary recovery

Repair StrictMode-safe closure aggregation, apply a fixed 300-second timeout to
both Dockerfile `uv sync` commands, and replace the one-attempt preflight object
with an exact two-attempt preservation object. This is the smallest approach
that addresses every observed blocker while retaining one build per run ID,
`--no-cache`, locked dependencies, no image/cache reuse, and no runtime retry.

### Rejected: closure and preflight only

This would make the next timeout close correctly but leave the evidenced
30-second network boundary unchanged. It would knowingly admit a fresh attempt
into the same avoidable build failure and is therefore not an adequate recovery.

### Rejected: host wheelhouse or reusable dependency cache

Pre-downloading CUDA wheels or mounting a reusable build cache could reduce
network exposure, but it would introduce new mutable assets, provenance,
locking, hash inventory, mount, and cleanup contracts. No current evidence
requires that broader architecture. The fixed bounded timeout is sufficient and
keeps the reviewed supply chain unchanged.

## Recovery architecture

The recovery has three independent implementation units and one unchanged
runtime boundary.

### Unit A: StrictMode-safe error aggregation

`Close-A11Phase` must create a typed
`System.Collections.Generic.List[string]` before historical inventory work.
Every known error is appended explicitly. Aggregate receipt errors, the
historical-preservation error, and the default normative failure are appended
through the same typed interface. The function may convert the list to an array
only when serializing the diagnostic document.

This guarantees that zero, one, or multiple errors expose a real `.Count`
property under both supported PowerShell runtimes. It must not change closure
file order, schemas, terminal strings, paths, no-clobber semantics, or the rule
that a closure-publication failure is returned once and never repaired in place.

The AST function harness must enable `Set-StrictMode -Version Latest` before it
loads any production function. Tests that intentionally depend on non-strict
PowerShell adaptation are not permitted.

### Unit B: bounded Docker dependency timeout

Both Dockerfile commands must use an inline, literal
`UV_HTTP_TIMEOUT=300` environment assignment:

```dockerfile
RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev --no-install-project
...
RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev
```

The value is seconds, fixed in the reviewed Dockerfile, and scoped only to the
individual build command. It must not persist as a runtime environment
variable, become a caller-controlled build argument, add a retry loop, change
the package index, remove `--frozen`, remove `--no-cache` from the launcher, or
alter any dependency or base-image identity.

If a future build still times out, it remains a terminal build failure for that
fresh run ID and must publish the normal failure closure. The launcher may not
rebuild the same tag or resume the same campaign.

### Unit C: exact two-attempt preservation preflight

The one-attempt preflight result must become an ordered collection of two closed
preservation records. Each record has an explicit state contract rather than a
shared least-common-denominator schema.

Attempt 1 binds its 48-file inventory, image tag and ID, final historical
record, released lease, release record, absence of the four never-published
closure records, and absence of links.

Attempt 2 binds its five exact file records and aggregate inventory hash,
consumed authorization identifier, absent registered image tag, absent active
and released lease destinations, absent validation directory, absent cache,
receipts, checkpoints, replicas, containers, and closure records, and absence
of links. File content hashes are authoritative; filesystem timestamps are
reported as context but are not preservation identities.

The A11 root must contain exactly these two run directories before any new
identity is generated. The A11 image inventory must contain exactly attempt 1's
image. The A11 lease-history inventory must contain exactly attempt 1's two
release files. No artifact bearing `steven001` may exist outside attempt 2's
registered identity evidence.

After this preservation object passes, the launcher may generate one new
calibration identity and one preregistered validation identity in memory. The
destination gate must prove that both run roots, cache roots, image tags, lease
paths, release paths, receipts, checkpoints, audit paths, and authorization
identifier are new and absent. It must compare them against both preserved
attempts and against each other before `Initialize-A11Phase` performs the first
write.

### Unchanged runtime boundary

The two-phase A11 statistical replay, 12 calibration replicas, 12 validation
replicas, fixed cohorts, metrics, thresholds, ceilings, schemas, GPU identity,
CUDA runtime, model contract, cache-content contract, lease protocol, and
terminal strings remain unchanged. Calibration must close and release before
validation. Validation failure continues to forbid Wave 1. A final PASS still
ends at `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED` and
does not authorize Wave 1.

## Failure and evidence flow

```text
read-only Git/Docker/GPU/historical/two-attempt preflight
  -> generate fresh calibration + validation identities in memory
  -> prove every fresh destination absent
  -> atomically initialize calibration root
  -> one no-cache Docker build with 300-second uv operation timeout
     -> failure: typed error list -> publish 78,79,80,81,82 -> stop
     -> closure publication failure: expose closure_error once -> stop
     -> success: continue existing image/cache/lease/replica/gate sequence
  -> calibration closes and releases
  -> validation may start
  -> validation closes and releases
  -> PASS remains Wave 1 review-only
```

Before the calibration root exists, every failure remains write-free. After a
fresh root is claimed, every normal stage failure attempts the complete
no-clobber closure exactly once. A closure-publication error preserves whatever
was created and is never followed by a repair, retry, validation, or cleanup.

## Test design

Implementation must follow TDD. Each defect starts with a focused RED test that
fails for the observed reason, followed by the smallest production change and a
GREEN rerun.

### StrictMode and closure tests

- Make the shared AST harness enable `Set-StrictMode -Version Latest`.
- Execute the real `Close-A11Phase` with one non-empty failure string and fixed
  in-memory historical inventories; require ordered 78-through-82 publication.
- Require zero, one, and multiple error cardinalities to remain typed and
  schema-correct.
- Execute the real campaign build-failure branch and require one terminal
  result, no validation, no second build, and one closure attempt.
- Preserve the existing sentinel-file closure-publication test and require the
  original file bytes to remain unchanged.
- Run the production-function tests under PowerShell 7. Parse the final script
  under both PowerShell 7 and Windows PowerShell 5.1.

### Dockerfile timeout tests

- Require exactly two inline `UV_HTTP_TIMEOUT=300` assignments, each directly
  bound to one existing frozen `uv sync` command.
- Reject a global `ENV UV_HTTP_TIMEOUT`, caller-controlled timeout `ARG`, shell
  retry loop, second build invocation, package-index override, dependency
  change, or removal of either frozen flag.
- Require the launcher build argv to retain exactly one `docker build`,
  `--no-cache`, the fixed base digest, the reviewed Dockerfile, and five exact
  OCI labels.

### Two-attempt preservation tests

- Construct exact temporary representations of both preserved attempts and
  require the read-only preflight to pass.
- Mutate every bound field independently: directory count, file count, size,
  SHA-256, link status, authorization location, image tag/ID, lease
  presence, validation root, closure file, cache, receipt, checkpoint, replica,
  and container. Each mutation must fail before initialization.
- Require attempt 1 and attempt 2 to keep their distinct state contracts; one
  may not satisfy the other's schema.
- Require new calibration and validation identities to be distinct from both
  prior runs and from each other, and require all destinations absent before the
  first write.
- Require the fixed 64,306-file and 21-image historical inventories and the
  eight fixed A10 hashes to remain exact.

### Regression and repository gates

- Run every focused A11 launcher, calibration, statistical replay, model,
  feasibility, orchestration, and receipt-validator suite required by the
  original plan and both existing supplemental plans.
- Run the complete CPU suite with no pytest cache.
- Run Black check, Ruff check, Git diff checks, lock verification, PowerShell 7
  parser, and Windows PowerShell 5.1 parser.
- Repeat the complete read-only historical, image, two-attempt, lease,
  container, GPU, and Git preservation gate after implementation.
- Perform an independent Critical/Important review; both counts must be zero
  before committing.

No test may build an image, initialize CUDA, download a model, acquire the real
GPU lease, mutate the real artifact root, import production evidence as a test
fixture, or synthesize a runtime authorization identifier.

## Implementation scope and lineage

The future implementation plan may modify exactly these three production/test
paths:

1. `docker/wave0.Dockerfile`
2. `scripts/run_wave0_a11.ps1`
3. `tests/gates/test_wave0_a11_launcher.py`

No other production, configuration, dependency, lock, schema, or test file is
in scope. The implementation plan is a separate single-file documentation
commit whose direct parent is this design commit. The implementation is one
append-only commit whose direct parent is the approved plan commit and whose
diff contains exactly the three allowlisted paths.

All commits use author and committer identity:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, rebase, reset, stash, cherry-pick, cleanup, push, merge, tag, release,
or modification of another repository is authorized.

## Acceptance criteria before another runtime review

The recovery is eligible for a new runtime review only when all of the following
are true:

1. The design, implementation plan, and implementation form the required direct
   parent chain from `1445a90b799b6306d6c1f7abc94b4a201afe5dc6`.
2. The implementation diff contains exactly the three allowlisted paths.
3. Both existing A11 attempts and all historical evidence rehash exactly to the
   values in this design.
4. Focused and full CPU tests, style, lock, diff, parser, and preservation gates
   pass from the committed tree.
5. Critical and Important review findings are zero.
6. Both linked and canonical worktrees are clean.
7. No Docker build, new A11 image, model cache, GPU lease, container, replica,
   receipt, checkpoint, validation directory, or runtime authorization has been
   created during implementation.
8. The owner reviews the final committed candidate and separately supplies a
   fresh, unused authorization identifier for exactly one new attempt.

Even after these criteria pass, the implementation has not passed A11 and has
not started Wave 1. It only becomes eligible for a separately authorized,
fresh, one-shot runtime attempt.
