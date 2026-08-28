# Wave 0 A11 Third Failure-Recovery Design

## Status and authority

The owner authorized this design, its written specification, implementation
plan, CPU-only TDD implementation, review, verification, and repair commit on
2026-08-29. The authorization is unattended and delegates the bounded design
choices in this document to the implementing agent.

This authority does not permit a new A11 launcher invocation, Docker build,
cache download, GPU lease, model initialization, calibration or validation
replica, RDD access, Wave 1, push, merge, tag, release, or publication. It does
not permit use of `steven003`. A later runtime attempt requires a separate
owner review of the final committed candidate and a new exact authorization
bound to that source commit.

The original A11 statistical-replay contract remains
`docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`,
Section 5.2.15. The reviewed original A11 specification and plan commits remain:

- specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`

The implementation starting point is:

- branch: `codex/wave0-model-contract`
- source: `ff5cfac5820415662e608886f1a10d7892f3ee00`
- first recovery implementation: `f10822e67ee90013c8e7a9d423d97c64993e676a`
- preserved-attempt implementation: `1445a90b799b6306d6c1f7abc94b4a201afe5dc6`
- second recovery implementation: `ff5cfac5820415662e608886f1a10d7892f3ee00`

All three failed A11 attempts are immutable. None may be retried, repaired,
completed, renamed, moved, deleted, retagged, or reinterpreted.

## Authoritative observed failure

The one authorized attempt using `OwnerAuthorizationId=steven002` passed its
read-only entry gate, fresh no-cache image build and inspection, cache
preflight, lease acquisition, environment stage, and model-assets stage. The
model-contract process then returned exit code 0 and exact stdout bytes
`PASS\n`. It published a regular, phase-confined receipt with normative status
`PASS`, an empty error list, and no false invariant.

The process also emitted 1,362 bytes to stderr:

1. a Transformers `Loading weights` progress display; and
2. an RT-DETR load report listing expected missing
   `num_batches_tracked` buffers.

The stderr SHA-256 is
`05a5801f0f54bdc7d8a5d6494f46b5b5d08df990d6137fdae012f753d96d79ce`.
The successful model-contract receipt SHA-256 is
`307c95414578af6c6a90dc742fe359a5b985d2d6bd2e76e9228caf1475de4eaa`.
`Invoke-A11DockerStage` correctly retained its registered stream contract and
failed because successful stages require empty stderr.

This is a presentation-control defect at the launcher process boundary, not a
model-contract semantic failure. The same presentation output appears in the
immutable successful A7 model-contract and training-feasibility logs. The
current A11 replicas call the same
`RTDetrForObjectDetection.from_pretrained(...)` path and also require empty
stderr, so repairing only `32-model-contract` would knowingly move the same
failure to the first replica.

The pinned local stack proves the two sources independently:

- Transformers 5.15.0 imports its loading `tqdm` through
  `transformers.utils.logging`; that adapter reads Hugging Face progress-bar
  state at import time.
- Transformers 5.15.0 writes the load report with `logger.warning`.
- Hugging Face Hub 1.28.0 reads `HF_HUB_DISABLE_PROGRESS_BARS` at import time.
- Transformers reads `TRANSFORMERS_VERBOSITY` when it creates the library root
  logger.

A CPU-only import probe on the pinned environment produced:

```text
default:  progress_disabled=False | transformers_verbosity=30
proposed: progress_disabled=True  | transformers_verbosity=40
```

The proposed state used exactly:

```text
HF_HUB_DISABLE_PROGRESS_BARS=1
TRANSFORMERS_VERBOSITY=error
```

Neither setting changes model weights, tensor operations, warnings captured by
the normative Python warning contract, exit codes, stdout, or receipts. A real
model-loading error still raises, returns a nonzero process exit, and fails the
launcher. Any stderr that remains after the controls also still fails.

## Preserved attempt baseline

The historical non-A11 baseline remains exactly 64,306 files with inventory
SHA-256
`e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`
and 21 images with inventory SHA-256
`9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.

### Attempt 1: launcher-stage failure

The first attempt remains bound exactly as specified by the two earlier
recovery designs:

- run ID: `wave0-a11-calibration-20260828T045848083Z-b9917463`
- preregistered validation ID:
  `wave0-a11-validation-20260828T045848091Z-084431a4`
- owner authorization: `OWNER-A11-RUNTIME-20260828-01`
- source: `2622e402e4f536b94326ac34f9b20c90b513002b`
- file count: 48
- run inventory SHA-256:
  `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b`
- image ID:
  `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`
- released lease SHA-256:
  `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`
- release record SHA-256:
  `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`

Its records 78, 80, 81, and 82 remain absent by contract.

### Attempt 2: image-build timeout

- run ID: `wave0-a11-calibration-20260828T114911289Z-fe8b7000`
- preregistered validation ID:
  `wave0-a11-validation-20260828T114911296Z-3107aff0`
- owner authorization: `steven001`
- source: `1445a90b799b6306d6c1f7abc94b4a201afe5dc6`
- file count: 5
- run inventory SHA-256:
  `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b`
- image, cache payload, lease, replica, checkpoint, validation root, and
  closure records: absent

Its five exact file records and five directory names remain those registered in
`docs/superpowers/specs/2026-08-28-val-wave0-a11-second-failure-recovery-design.md`.

### Attempt 3: foundation stream-contract failure

- run ID: `wave0-a11-calibration-20260828T172921151Z-a0f55fa1`
- preregistered validation ID:
  `wave0-a11-validation-20260828T172921161Z-70928997`
- owner authorization: `steven002`
- source: `ff5cfac5820415662e608886f1a10d7892f3ee00`
- specification: `b59b0d4407b98b460f6166ea7288ba6021dc7a78`
- plan: `7dbd3a7576ea76beccfc64f748c4e495259ea89b`
- state: `foundation-stream-contract-failure`
- file count: 60
- run inventory SHA-256:
  `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2`
- directory count: 18
- image tag:
  `vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1`
- image ID:
  `sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd`
- release record SHA-256:
  `72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93`
- released lease SHA-256:
  `a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f`
- latest observed write time:
  `2026-08-28T18:10:34.6753199Z`

The 18 exact directory names are:

```text
audit
wave0
wave0/checkpoints
wave0/model_cache
wave0/model_cache/snapshots
wave0/model_cache/snapshots/facebook--dinov2-small
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download
wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download
wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees
wave0/receipts
```

The following key file records bind the failure and closure:

| Relative path | Size | SHA-256 |
| --- | ---: | --- |
| `audit/00-identity.json` | 2,873 | `e9c0743ef1b2311aac15b51e4208ff204ad7766581d1a440206bc2903d989461` |
| `audit/10-build.json` | 1,234 | `2ea371296b5eedf28074a8fb966b1fe58a985629f966c89a348c8bc4ab00b4ab` |
| `audit/11-image-inspect.json` | 682 | `98e6a4b0f547c95ebd00d21caeec620283543906d839a24eabb67adc6945fffc` |
| `audit/20-cache-preflight.json` | 1,900 | `9827ccd8ea4d9f3625e26db1caecda276ac1a452f0cb4dad409eed2d9eeb7236` |
| `audit/30-environment.json` | 1,995 | `5523fce88357798387b5934baf32f311150f148ed95871f396539ab1682ef656` |
| `audit/31-model-assets.json` | 2,051 | `9e9e0e88a94b217d26e96741dfc34db499b72f579460a1465a5a988f2cf7ba66` |
| `audit/32-model-contract.json` | 1,910 | `4f2e6992aa40d9df1a0322565a6bdc2484f45fe6163eb5203e8efe911d3a85f8` |
| `audit/32-model-contract.stdout.log` | 5 | `c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431` |
| `audit/32-model-contract.stderr.log` | 1,362 | `05a5801f0f54bdc7d8a5d6494f46b5b5d08df990d6137fdae012f753d96d79ce` |
| `wave0/receipts/model-contract.json` | 9,623 | `307c95414578af6c6a90dc742fe359a5b985d2d6bd2e76e9228caf1475de4eaa` |
| `audit/78-failure-diagnostic.json` | 853 | `f50f883e74594752d9c4e6e4b857814c9072f0bfc0d75d0dcd229d2081b12676` |
| `audit/79-historical-preservation-final.json` | 301 | `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d` |
| `audit/80-campaign-result.json` | 764 | `1787120f4635a02ba14e6b08d390b896ca03e855efc22cdf710983bf94dd8bab` |
| `audit/81-campaign-file-manifest.json` | 16,740 | `ab28d20479a0b44a82bcb9c555f867c0c879a2da0cc0c117d2c4c8667749adf3` |
| `audit/82-campaign-closure.json` | 660 | `75267ce8cc36bc25a6c7e985c4b836038241706477656211fe1328dd102bf76a` |

The active lease and preregistered validation root are absent. There are no
replica directories or checkpoint files. The calibration image remains present
with exact source/specification/plan/base/run labels; the validation image is
absent. The terminal remains
`WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN`.

The complete A11 envelope before a future attempt is therefore exactly three
calibration run directories, two A11 image tags, four A11 lease-history files,
three authorization identities, no active lease, and no project container.

## Approaches considered

### Selected: exact model-load presentation controls plus three-attempt baseline

Add the two fixed presentation environment values only to A11 subprocesses
that load the pinned Transformers model: `32-model-contract` and every
calibration or validation replica. Keep exact exit code, stdout, empty stderr,
receipt, checkpoint, and no-clobber contracts unchanged. Extend the preflight
to bind all three immutable attempts according to their distinct states.

This is the smallest complete repair. It prevents both already observed and
statically proven next-stage presentation failures without broadening success
criteria or changing Python/model behavior.

### Rejected: accept or normalize known stderr

The progress display contains variable rates and update counts. Load-report row
order and paths can vary in presentation while remaining semantically
equivalent. An allowlist would either be brittle or broad enough to admit
unreviewed warnings. Trimming, regex deletion, substring acceptance, or storing
stderr while declaring success would weaken the registered stream contract.

### Rejected: change the Python model loader

Programmatically disabling logs or progress in the Python probe would affect
all callers and add a Python production path to the recovery allowlist. The
launcher owns subprocess presentation and can set import-time controls before
any package is loaded. No evidence justifies changing model-contract or
training-feasibility implementation.

## Recovery architecture

### Unit A: closed model-load presentation arguments

Add one launcher helper returning exactly this ordered Docker argument list:

```text
-e HF_HUB_DISABLE_PROGRESS_BARS=1
-e TRANSFORMERS_VERBOSITY=error
```

`Invoke-A11DockerStage` receives an explicit model-load-presentation switch.
Only the `32-model-contract` call enables it. The environment and model-assets
foundation calls do not receive the two values.

`New-A11ReplicaArguments` always includes the same exact argument list because
every replica loads RT-DETR. The values occur before the image ID so Docker
applies them to the container, not to the `val` command.

No caller controls the values. No wildcard, arbitrary environment map, host
environment forwarding, env file, secret, token, retry, stderr normalization,
or alternative verbosity is permitted. Cache preflight retains its separate
existing Hub download controls. The launcher still requires exact stdout and
empty stderr after process completion.

### Unit B: exact three-attempt preservation preflight

`Get-A11PriorAttemptInventory` expands from two to three explicitly registered
attempts. It must:

1. require exactly the three calibration run names in chronological order;
2. reject reparse points at each parent, attempt root, descendant, and lease
   record;
3. parse and bind all three current/preregistered identity pairs;
4. compute each recursive file inventory and its canonical SHA-256;
5. require the distinct attempt-specific partial or closed state;
6. require exactly the two registered A11 image tags and IDs;
7. require exactly the four registered lease-history files and hashes;
8. require the third attempt's exact 18-directory structure, 60-file inventory,
   key records, complete 78-through-82 closure, cache, absent validation,
   absent active lease, absent replicas, and absent checkpoints; and
9. return a closed ordered evidence object with three authorization records and
   three attempt records.

`Test-A11ReadOnlyPreflight` requires the same closed fields and constants. The
future `OwnerAuthorizationId` must differ from all three consumed identifiers.
Changing only a count, accepting an unknown state, sharing one schema across
the three attempts, or treating closure existence as sufficient is forbidden.

The destination gate continues to compare both newly generated phase identities
against every `registered_run_id`, image tag, path, and authorization in all
three prior attempts before the first write.

### Unit C: unchanged normative and failure boundaries

The repair does not change:

- the 12 calibration and 12 validation replicas;
- the 66-pair and 13-metric inventories;
- thresholds, ceilings, formulas, receipt schemas, or semantic validators;
- model, processor, weights, reset, seed, fixtures, warnings, optimizer,
  scheduler, CUDA, driver, GPU, VRAM, or checkpoint contracts;
- build timeout, no-cache build, cache content, lease lifecycle, or phase order;
- failure closure order and no-clobber behavior; or
- the prohibition on retry, Wave 1, RDD, push, merge, release, or publication.

A calibration failure still prevents validation. A future A11 PASS still stops
at `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`.

## TDD and verification design

The implementation must start with focused RED tests that fail against
`ff5cfac5820415662e608886f1a10d7892f3ee00` for the intended reasons.

### Presentation-control tests

- Exercise real `Invoke-A11Foundation` with a native-process boundary that
  emits the observed model-load stderr unless both exact controls are present.
  Require environment and assets to retain their existing argv and
  model-contract to receive the two controls exactly once and in order.
- Exercise real replica argument construction and real `Invoke-A11Replica`.
  Require the two controls exactly once before the image ID.
- Require any nonempty stderr that remains after the controls to fail both
  model-contract and replica execution.
- Require exact stdout and receipt/checkpoint bindings to remain unchanged.
- Reject `HF_HUB_VERBOSITY`, global env forwarding, alternate values, duplicate
  pairs, stderr trimming, stderr allowlists, and any removal of the strict
  `$Result.Stderr -ceq ''` predicates.

### Three-attempt preservation tests

- Build isolated temporary representations of all three distinct attempt
  states and exercise the real production inventory and preflight functions.
- Require the exact three-run, two-image, four-lease, three-authorization
  envelope.
- Mutate the third attempt's run ID, peer ID, owner ID, source/spec/plan, file
  count, file digest, key file record, directory structure, image tag/ID,
  image labels, lease record/hash, closure, validation absence, cache,
  replica/checkpoint absence, or link safety; each mutation must fail before
  initialization.
- Require `steven002` to be rejected as reused and a synthetic test-only fresh
  identifier to pass. Tests must never introduce `steven003`.
- Keep attempt 1, attempt 2, and attempt 3 field sets distinct and closed.

### Repository gates

Before the implementation commit, run:

- focused RED and GREEN tests with recorded expected failure reasons;
- complete `tests/gates/test_wave0_a11_launcher.py`;
- all original A11 focused suites named by the original and supplemental plans;
- complete CPU pytest with cache disabled and bytecode writing disabled;
- targeted Black and Ruff for the changed Python test;
- `uv lock --check` and `git diff --check`;
- PowerShell 7 and Windows PowerShell 5.1 parse checks;
- exact tracked-file and staging audits;
- full read-only historical, three-attempt, image, lease, container, GPU, Git,
  and unused-authorization preservation checks; and
- independent review with Critical=0 and Important=0.

No test may invoke the launcher entry point, Docker build or run, model loading,
CUDA, the real GPU lease, or mutate the external artifact root.

## File, commit, and lineage boundaries

This design commit changes exactly this file:

```text
docs/superpowers/specs/2026-08-29-val-wave0-a11-third-failure-recovery-design.md
```

The plan commit will add exactly:

```text
docs/superpowers/plans/2026-08-29-val-wave0-a11-third-failure-recovery.md
```

The implementation allowlist is exactly:

```text
scripts/run_wave0_a11.ps1
tests/gates/test_wave0_a11_launcher.py
```

The implementation must be one append-only commit whose direct parent is the
plan commit. A third implementation path is a hard stop. All commits use:

```text
kuotunyu <61350295+kuotunyu@users.noreply.github.com>
```

No amend, reset, rebase, stash, cherry-pick, cleanup of historical evidence,
push, merge, tag, release, or modification of another repository is permitted.

## Acceptance and stopping gate

The recovery is complete only when:

1. design, plan, and implementation commits form a direct parent chain from
   `ff5cfac5820415662e608886f1a10d7892f3ee00`;
2. the implementation diff contains exactly the two allowlisted paths;
3. focused tests prove the observed presentation defect RED then GREEN for both
   model-contract and replica boundaries;
4. strict stderr rejection remains effective;
5. all three A11 attempts, two A11 images, four lease-history files, 64,306
   historical files, and 21 historical images rehash exactly;
6. no new A11 run, image, cache, lease, container, replica, receipt, checkpoint,
   validation root, or runtime authorization exists;
7. every required CPU, style, lock, diff, parser, and review gate passes;
8. linked and canonical worktrees are clean after the implementation commit;
   and
9. `steven003` remains unused.

After the implementation commit and post-commit verification, stop and report
the exact commits and evidence. Do not invoke `scripts/run_wave0_a11.ps1`. The
candidate becomes eligible only for a later, separately authorized, fresh,
single runtime attempt.
