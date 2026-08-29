# Wave 0 A11 Runtime-Transport Architecture Recovery Design

## Status and authority

The owner approved this design direction on 2026-08-29 with the exact statement:

```text
核准此 A11 recovery architecture design，並同意以此設計取代第四 recovery spec 的 fifth-implementation hard stop。
```

This approval supersedes only the sentence in
`docs/superpowers/specs/2026-08-29-val-wave0-a11-fourth-failure-recovery-design.md`
that makes a fifth implementation path a hard stop. Every other boundary in
that design, the original A11 statistical-replay contract, and the original
A11 plan remains in force unless this document states a narrower replacement.

This written specification still requires owner review before an implementation
plan is written. It permits the append-only design/specification, implementation
plan, CPU-only TDD implementation, review, repository verification, and the one
bounded dependency-only Docker diagnostic defined here after their respective
review gates. It does not authorize a new A11 launcher invocation, formal image
campaign, GPU lease, model initialization, calibration or validation replica,
RDD access, Wave 1, push, merge, tag, release, or publication. It does not
permit reuse of any consumed authorization or synthesis of a future
`OwnerAuthorizationId`.

The unchanged original A11 identities are:

- specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- original plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`
- branch: `codex/wave0-model-contract`
- fifth-attempt source: `ed6f157c7cbd545895b9d047f6e094968a1f9d94`

All five failed A11 attempts are immutable. None may be retried, repaired,
completed, renamed, moved, deleted, retagged, used as a calibration
observation, or reinterpreted as a statistical result.

## Authoritative fifth failure

The single launcher invocation authorized by `OwnerAuthorizationId=steven004`
passed the exact no-write entry gate and preregistered one fresh calibration
identity and one distinct validation identity. It created only the calibration
root and initial audit records, then invoked the exact fresh no-cache Docker
build once.

The build failed in the first dependency sync:

```text
RUN UV_HTTP_TIMEOUT=300 uv sync --frozen --no-dev --no-install-project
```

The relevant stderr is:

```text
× Failed to download `triton==3.7.0`
├─▶ Failed to write to the distribution cache
├─▶ error decoding response body
├─▶ request or response body error
├─▶ error reading a body from connection
╰─▶ stream error received: unspecific protocol error detected
```

The process returned exit code 1. The locked x86-64 wheel is 201,457,567
bytes and has SHA-256
`8f111161d49bf903c0eaedde3962353a3d841c08a836839b7cc1025b8426efcf`.
No evidence indicates a version-resolution, lock, wheel-hash, model, fixture,
GPU, replica, checkpoint, metric, or statistical-gate failure.

The launcher preserved the build stdout/stderr, published its immutable
failure diagnostic, historical-preservation record, result, manifest, and
closure, and stopped at:

```text
WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN
```

No image tag or ID was created. No lease was acquired, so no release record
was required. No cache preflight, model receipt, replica, checkpoint,
calibration threshold receipt, validation root, or Wave 1 object exists.

## Root-cause analysis

The external trigger was an HTTP/2 response-body stream failure while
downloading a large locked wheel. The architectural defect was allowing one
unhandled transport failure inside a cold, no-cache dependency build to
consume an otherwise valid formal A11 authorization.

Three facts bind this diagnosis:

1. `docker/wave0.Dockerfile` installs and runs exact `uv==0.8.15`.
2. uv's official 0.8.x changelog records retry handling for HTTP/2 streaming
   I/O errors in 0.8.16, after the pinned version. uv 0.9.1 later broadened
   the behavior to all HTTP/2 errors.
3. The build used `docker build --no-cache` without a BuildKit uv cache mount.
   All successfully fetched distributions lived only in the failed build
   step and were unavailable to a bounded subsequent dependency-sync process.

The fix must not merely special-case `triton`, widen a timeout until the
symptom disappears, or upgrade the normative runtime toolchain. It must make
the transport boundary explicit while retaining the approved environment and
cryptographic dependency identities.

Primary references:

- `https://github.com/astral-sh/uv/blob/main/changelogs/0.8.x.md`
- `https://github.com/astral-sh/uv/blob/main/changelogs/0.9.x.md`
- `https://docs.astral.sh/uv/reference/environment/`
- `https://docs.astral.sh/uv/guides/integration/docker/`
- `https://docs.docker.com/reference/dockerfile/`
- `https://docs.docker.com/build/exporters/`

## Preserved evidence envelope

The historical non-A11 baseline remains exactly 64,306 files with inventory
SHA-256
`e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`
and 21 images with inventory SHA-256
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.

The first four A11 attempts remain exactly registered by the previous
append-only recovery specifications. The complete current envelope is exactly:

- five calibration run directories;
- zero validation run directories;
- three calibration image tags;
- six release-history files;
- zero active GPU lease files;
- zero project containers; and
- five consumed owner identities:
  `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`,
  and `steven004`.

### Attempt 5: dependency-transport build failure

- state: `dependency-transport-build-failure`
- calibration run:
  `wave0-a11-calibration-20260829T123151657Z-bf516632`
- preregistered validation:
  `wave0-a11-validation-20260829T123151664Z-7af53ca8`
- owner: `steven004`
- source: `ed6f157c7cbd545895b9d047f6e094968a1f9d94`
- specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- original plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`
- file count: 10
- directory count: 5
- run inventory SHA-256:
  `b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448`
- latest write UTC: `2026-08-29T13:39:47.0148945Z`
- latest path: `audit/82-campaign-closure.json`
- image, active lease, release, replica, checkpoint, success receipt, and
  validation root: absent

The exact directory list is:

```text
audit
wave0
wave0/checkpoints
wave0/model_cache
wave0/receipts
```

The exact file records are:

| Relative path | Size | SHA-256 |
| --- | ---: | --- |
| `audit/00-identity.json` | 2,873 | `9fb7f3572e8341af986f24473c2ee66933d17d736b632b95e0c3a64c91e9d67d` |
| `audit/01-gpu-preflight.json` | 125 | `de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7` |
| `audit/10-build.json` | 1,234 | `3ef76de20f776e977f172d2ba9c3277185db693bd3a7fc9949bfe42b39af6f68` |
| `audit/10-build.stderr.log` | 865,248 | `e53b9598c39343785aea27be4381f1755accb5f91553630af64d1b71712e82c5` |
| `audit/10-build.stdout.log` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `audit/78-failure-diagnostic.json` | 766 | `cc0e391fdb743dac2c2c80362d690703da08b9ae38c5a8294031ace8bef9c311` |
| `audit/79-historical-preservation-final.json` | 301 | `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d` |
| `audit/80-campaign-result.json` | 751 | `346b4aa69f8e6c440262f463e4cbb756f39dd1dde0df51124f533093ffe8b651` |
| `audit/81-campaign-file-manifest.json` | 1,885 | `8be8ee5adadb296d269c5dda0c1827d8ef9ee56d024872aa3ee6e0cb74bbedd6` |
| `audit/82-campaign-closure.json` | 659 | `a3ba8ef72165dde8443ac85ffcaaf27b307afd15af10c8a0d347ca7f30cfcaa1` |

## Approaches considered

### Selected: registry-backed preservation plus bounded transport recovery

Move exact prior-attempt declarations out of executable PowerShell branches
and into one schema-validated, source-controlled registry. The launcher uses
one generic fail-closed verifier for all registered attempts. Separately,
retain uv 0.8.15 but execute dependency sync through a small tested wrapper
that retries only recognized transport failures, at most three total process
attempts, with a persistent BuildKit uv cache mount.

This addresses both repeated architectural problems without changing the
model, runtime stack, lockfile, thresholds, or formal one-invocation boundary.

### Rejected: one more hard-coded attempt branch

Adding a fifth set of PowerShell constants and conditionals is the smallest
diff but repeats the architecture that required four recovery commits. It
contradicts the reason the previous specification established a hard stop and
provides no bounded way to admit a later preserved failure.

### Rejected: upgrade normative uv

uv 0.8.16 or 0.9.1 contains relevant upstream transport fixes, but the
approved environment configuration, runtime receipts, schemas, model
contract, and original A11 specification bind uv 0.8.15. Upgrading would be a
new environment/model-contract decision, not a failure recovery.

### Deferred fallback: offline wheelhouse or dependency-foundation image

A separately signed wheelhouse or foundation image could remove build-time
network access. It would add a new supply-chain artifact, retention policy,
platform-selection contract, and base-image ancestry. That is disproportionate
unless the selected bounded recovery fails its separately approved diagnostic.

## Recovery architecture

### Unit A: source-controlled preserved-attempt registry

Create:

```text
configs/a11/preserved-attempts.json
schemas/a11-preserved-attempts.schema.json
```

The registry has `schema_version=1` and an ordered `attempts` array. Each
record contains only declarative evidence:

- chronological ordinal and closed state;
- current and preregistered peer run IDs;
- owner authorization, source, specification, and original-plan commits;
- registered run IDs, image tags, and artifact/lease destinations;
- exact run file and directory counts plus complete run inventory SHA-256;
- exact directory names and selected key file records;
- optional image tag/ID and optional release hashes;
- expected replica/checkpoint/closure sets;
- explicit success-receipt and validation-presence booleans;
- exact latest-write timestamp; and
- `links_absent=true`.

The initial registry contains exactly the five existing attempts in
chronological order. Attempts 1 through 4 must preserve the constants and
state-specific expectations already approved by their respective recovery
specifications. Attempt 5 must match this document exactly.

The registry is an expected-state declaration, never a discovery or import
mechanism. The launcher must not generate, update, normalize, repair, or
append it. A future recovery may append a new reviewed record only through a
new source commit. Earlier array entries must remain byte-for-byte unchanged
in that commit's diff.

The exact authorized source commit remains the trust boundary. The loader
computes the SHA-256 of the exact registry file bytes once, retains that digest
with the parsed in-memory value, and rehashes the file immediately before the
first permitted write. A mismatch stops before write. The digest is recorded
in the later launcher's identity audit, but is not stored inside the registry,
so no self-referential canonicalization rule exists. The registry does not
authorize a runtime attempt, an owner identity, or a destination by itself.

### Unit B: generic fail-closed registry verifier

Refactor `Get-A11PriorAttemptInventory`, `Test-A11ReadOnlyPreflight`, and
`Test-A11PhaseDestinationsAbsent` to consume the validated registry rather
than cardinality-specific branches.

The generic verifier must:

1. reject unknown schema versions, unknown fields, duplicate or unordered
   ordinals, duplicate current/peer IDs, duplicate image tags, duplicate
   destinations, and duplicate owner identities;
2. require every path to remain under the exact artifact root and reject
   every link/reparse point at registered roots, descendants, and files;
3. re-enumerate each run and compare file count, directory count, exact
   directory list, inventory SHA-256, key records, latest write, success and
   validation absence/presence, image identity, and lease history;
4. require the complete registered envelope to equal the actual A11 run,
   image, and lease envelope, so an extra unregistered object fails entry;
5. return all consumed owners and all registered destinations to the existing
   uniqueness/no-clobber gate; and
6. perform no write, Docker mutation, GPU mutation, cleanup, or inference.

State-specific optional fields are defined by the JSON schema. Absence and
JSON `null` are not interchangeable. The registry loader must compare an
explicit sorted property set before converting values.

### Unit C: bounded dependency-sync wrapper

Create a small Python module used only during image construction:

```text
scripts/run_uv_sync_with_retries.py
```

Its public CLI accepts the exact uv argument vector after `--`. Production
invocations are fixed to the existing two commands:

```text
uv sync --frozen --no-dev --no-install-project
uv sync --frozen --no-dev
```

The wrapper contract is:

- exact maximum: three total uv processes, including the first;
- exact backoff before process 2 and 3: 5 and 10 seconds;
- `UV_HTTP_TIMEOUT=300` for every process;
- no owner ID, run ID, model, GPU, artifact-root, threshold, or receipt input;
- emit `A11_UV_SYNC_ATTEMPT n/3` before each process;
- capture stdout and stderr as bytes, re-emit each complete byte stream to the
  matching parent stream without text rewriting, and use a separate UTF-8
  `errors=replace` decoding of stderr only for signature classification;
- return immediately on success;
- return immediately on a non-transport failure;
- retry only when stderr contains a reviewed transport signature; and
- after exhaustion, return the final uv exit code.

The wrapper constructs a child environment from its own environment and sets
`UV_HTTP_TIMEOUT=300`, overriding any inherited value. If the child terminates
by signal, the wrapper re-emits its output and returns `128 + signal_number`
without retry. It never invokes a shell and passes the post-`--` argument
vector to the child unchanged.

The initial retryable signature set is exact and case-sensitive:

```text
error decoding response body
request or response body error
error reading a body from connection
stream error received:
Failed to download distribution due to network timeout
connection reset by peer
```

At least one signature must be present. The wrapper must not retry lock drift,
resolution conflicts, hash mismatches, invalid wheel/ZIP validation, disk
capacity errors, permission errors, Python build errors, project install
errors, or an unclassified nonzero exit.

The wrapper is transport handling inside one Docker `RUN`; it is not a second
launcher call, Docker build, A11 run, or model attempt.

### Unit D: BuildKit cache and Docker stages

Keep exact `uv==0.8.15`, Python 3.12.11, `uv.lock`, all dependency versions,
the requested CUDA base digest, and the final runtime environment contract.
Do not edit `uv.lock`.

Add the stable Dockerfile syntax directive and an `a11-dependencies` named
stage. Both uv sync instructions use:

```text
--mount=type=cache,id=val-wave0-uv-0.8.15-cu126-v1,target=/root/.cache/uv,sharing=locked
```

Set `UV_LINK_MODE=copy` for the sync processes because the cache mount and
virtual environment are different filesystems. Cache contents are not copied
into the resulting image. The lockfile's package versions and distribution
hashes remain authoritative; cache entries are disposable and untrusted.

The launcher retains one exact `docker build --no-cache --progress plain`
call. `--no-cache` continues to force every image layer to execute. The cache
mount may reuse verified distribution bytes but may not reuse an image layer,
source tree, receipt, model cache, or prior A11 image.

The final default stage copies application source/configuration, performs the
second wrapped sync, and retains `ENTRYPOINT ["val"]`.

### Unit E: one dependency-only Docker diagnostic

After all CPU tests, parser/lint/schema gates, preservation rehashes, and code
review pass, the implementation plan may invoke exactly one diagnostic build:

```text
docker buildx build
  --no-cache
  --progress=plain
  --target a11-dependencies
  --output=type=cacheonly
  --file docker/wave0.Dockerfile
  .
```

The command is one logical diagnostic invocation. It is CPU/network-only,
does not request GPU access, uses no `OwnerAuthorizationId`, creates no A11
run ID or campaign root, exports no image, starts no project container, and
does not initialize a model. Its sole intended persistent side effect is
BuildKit cache data.

Before the diagnostic, require clean linked and canonical worktrees, healthy
Linux Docker, no project container, no active lease, and zero numeric CUDA
compute processes. Write the exact argv, exit code, stdout, stderr, source
identity, Docker/Buildx versions, start/end timestamps, and file hashes to a
fresh append-only diagnostic directory outside `a11-runs`. The path and exact
naming rule must be frozen by the implementation plan before execution.

If the diagnostic fails, preserve its evidence, publish a diagnostic NO_GO,
and stop. Do not run it again, modify the candidate, request an owner ID, or
invoke the A11 launcher. A passing diagnostic proves only dependency-stage
transport handling; it is not a Wave 0 or A11 result.

### Unit F: unchanged formal A11 boundaries

This recovery does not change:

- twelve calibration and twelve validation replicas;
- 66-pair and thirteen-metric inventories;
- calibration/validation thresholds, ceilings, formulas, schemas, or
  semantic validators;
- model, processor, revisions, seed, fixture, optimizer, scheduler, CUDA,
  driver, GPU, VRAM, or checkpoint contracts;
- runtime uv 0.8.15 or any approved Python/package version;
- model-cache download and verification rules after image construction;
- leases, phase order, no-clobber writes, failure closure, and historical
  preservation;
- exact stdout/empty-stderr contracts for model processes; or
- prohibitions on formal retry, partial rescue, threshold feedback, RDD,
  Wave 1, push, merge, release, or publication.

A later formal launcher invocation still requires one new, explicit owner
authorization bound to the exact recovery source commit, original
specification, original A11 plan, and branch. It still generates fresh,
distinct calibration and validation identities and may be invoked exactly
once. Wrapper retries are fully inside that invocation's single image build.

## Error handling and stopping rules

- Registry parse, shape, source/file-digest binding, envelope, identity, link,
  inventory, image, lease, owner, or destination mismatch: stop before any
  write.
- Wrapper receives invalid arguments or an unclassified nonzero uv result:
  stop the current build immediately without retry.
- Recognized transport failure succeeds within three uv processes: continue
  the same Docker build and preserve attempt markers in the build log.
- Recognized transport failure exhausts three uv processes: fail the build,
  preserve the formal failure closure if inside a later authorized launcher,
  and prohibit validation.
- Dependency-only diagnostic failure: preserve diagnostic evidence and stop
  before any formal authorization or launcher invocation.
- Any Docker/GPU/lease/model side effect outside the specified diagnostic or
  a later separately authorized formal invocation: hard failure and review.

## TDD and verification design

Implementation starts with focused RED tests against the committed plan
parent. Tests may use synthetic owners but must not introduce a guessed real
future owner ID.

### Registry tests

- Validate one exact five-attempt fixture against the schema and production
  loader.
- Exercise the real generic verifier against synthetic filesystem, image, and
  lease adapters.
- Mutate each fifth-attempt field independently and require pre-write failure.
- Reject missing/extra/reordered attempts; changed earlier records; duplicate
  owner/run/image/path; unknown field/state/schema; malformed SHA/timestamp;
  path escape; link; inventory drift; extra A11 run/image/lease; and unexpected
  validation/success objects.
- Require exact registry-file SHA-256 stability from load through the first
  permitted write and record that digest in the synthetic identity audit.
- Require all five consumed owners to fail reuse and one clearly synthetic
  test-only fresh owner to pass the pure read-only gate.

### Wrapper tests

- Success on process 1 executes once and returns 0.
- Recognized transport failures followed by success execute exactly two or
  three times with exact attempt markers and backoff requests.
- Three recognized failures return the third exit code.
- Each unclassified/deterministic failure executes once.
- Missing separator, empty argv, attempts beyond the fixed maximum, signal
  termination, and stdout/stderr binary-decoding edge cases fail closed.
- Tests replace subprocess and sleep adapters; they do not use network,
  Docker, GPU, or the external artifact root.

### Dockerfile and launcher tests

- Require the exact named stage, cache ID/target/sharing, `UV_LINK_MODE=copy`,
  two wrapper invocations, and unchanged two uv argument vectors.
- Require exact uv 0.8.15 and unchanged lockfile digest.
- Require one launcher Docker build, one `--no-cache`, no Docker-level retry
  loop, no cleanup command, and no new model/runtime path.
- Require Docker/Buildx `--check` to accept the Dockerfile without executing a
  build.

### Repository and evidence gates

- Complete focused and full CPU pytest with bytecode/cache writes disabled.
- Targeted Black and Ruff for changed Python files.
- `uv lock --check`, schema validation, `git diff --check`, and both
  PowerShell parser gates.
- Full five-attempt, historical, image, lease, container, GPU, and Git
  preservation checks before and after the implementation commit.
- Exact tracked-file and staged-file allowlists; no generated cache/bytecode.
- Independent cold review with Critical=0 and Important=0.
- One dependency-only diagnostic only after every preceding gate passes.

No CPU test may invoke the launcher entry point, a real Docker build/run, a
GPU lease, model loading, CUDA, or mutate external artifacts.

## File, commit, and lineage boundaries

This design commit changes exactly this file:

```text
docs/superpowers/specs/2026-08-29-val-wave0-a11-runtime-transport-architecture-recovery-design.md
```

The future plan commit may add exactly:

```text
docs/superpowers/plans/2026-08-29-val-wave0-a11-runtime-transport-architecture-recovery.md
```

The implementation plan must freeze a minimal allowlist drawn from these
candidate paths and justify every included path:

```text
configs/a11/preserved-attempts.json
schemas/a11-preserved-attempts.schema.json
scripts/run_uv_sync_with_retries.py
scripts/run_wave0_a11.ps1
docker/wave0.Dockerfile
tests/gates/test_wave0_a11_launcher.py
tests/scripts/test_run_uv_sync_with_retries.py
```

No environment config, receipt schema, model/statistical code, dependency
version, or lockfile may change. If implementation proves another tracked path
is necessary, stop and amend this written specification through owner review;
do not silently expand the plan allowlist.

Design, plan, and implementation are three append-only commits. Each must be
the direct child of the previous approved commit. Author and committer are
exactly:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, reset, rebase, squash, stash, cherry-pick, cleanup of historical
evidence, push, merge, tag, release, or modification of another repository is
permitted.

## Acceptance and stopping gate

The recovery candidate is eligible for the one dependency-only diagnostic
only when:

1. the approved design, plan, and implementation commits form a direct parent
   chain from `ed6f157c7cbd545895b9d047f6e094968a1f9d94`;
2. every commit has the exact author/committer and file scope;
3. the registry contains exactly five immutable attempts and the production
   verifier rejects every tested mutation before write;
4. all five prior runs, three images, six lease-history files, five consumed
   owners, 64,306 historical files, and 21 historical images rehash exactly;
5. wrapper RED/GREEN tests prove exact retry classification, cardinality,
   logging, backoff, and fail-closed behavior;
6. runtime uv remains 0.8.15, `uv.lock` remains byte-identical, and no model,
   receipt, schema, threshold, or environment contract changes;
7. Dockerfile/Buildx checks and all CPU/style/lock/parser/schema/review gates
   pass;
8. linked and canonical worktrees are clean after the implementation commit;
9. no new A11 run, image, lease, container, receipt, checkpoint, validation
   root, model process, or owner identity exists; and
10. the diagnostic has not yet been invoked.

The plan then executes the diagnostic exactly once. A diagnostic PASS stops at
`A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED`. A diagnostic
failure stops at `A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN`.

Neither terminal authorizes the A11 launcher. A later formal runtime attempt
requires a separately supplied exact `OwnerAuthorizationId` and explicit
authorization bound to the resulting source commit, specification commit
`b59b0d4407b98b460f6166ea7288ba6021dc7a78`, original plan commit
`7dbd3a7576ea76beccfc64f748c4e495259ea89b`, and branch
`codex/wave0-model-contract`.
