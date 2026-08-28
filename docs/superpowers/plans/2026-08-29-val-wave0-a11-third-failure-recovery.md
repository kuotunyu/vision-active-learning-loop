# Wave 0 A11 Third Failure-Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the A11 launcher so every Transformers model-loading subprocess suppresses only non-normative presentation output while strict stderr rejection remains intact, and admit a future fresh attempt only after exactly preserving all three immutable prior A11 attempts.

**Architecture:** Keep the repair inside the launcher boundary. One closed helper supplies two exact import-time presentation environment values to model-contract and replica containers; the existing exit/stdout/stderr/receipt/checkpoint gates remain unchanged. Extend the existing explicit prior-attempt inventory and preflight from two to three state-specific records, binding the third run's complete inventory, key files, image, lease history, closure, absent validation, and consumed authorization before any fresh destination is created.

**Tech Stack:** PowerShell 7/Windows PowerShell 5.1, Python 3.12, pytest 9, uv 0.8.15, Docker CLI argument construction tests, Git.

## Global Constraints

- Execution workspace is exactly `<repo>\.worktrees\wave0-model-contract` on branch `codex/wave0-model-contract`.
- Plan drafting starts at design commit `fc9aa0d8f9f94280ba0f38ee41b2007ba53a5676`, whose direct parent is `ff5cfac5820415662e608886f1a10d7892f3ee00` and whose only changed path is `docs/superpowers/specs/2026-08-29-val-wave0-a11-third-failure-recovery-design.md`. Implementation entry HEAD must be the separate plan-only direct child of that design commit.
- Original A11 specification and runtime plan identities remain `b59b0d4407b98b460f6166ea7288ba6021dc7a78` and `7dbd3a7576ea76beccfc64f748c4e495259ea89b`.
- The plan commit changes only `docs/superpowers/plans/2026-08-29-val-wave0-a11-third-failure-recovery.md`.
- The implementation allowlist is exactly `scripts/run_wave0_a11.ps1` and `tests/gates/test_wave0_a11_launcher.py`.
- Implementation uses strict RED/GREEN TDD and ends in one append-only implementation commit whose direct parent is the plan commit.
- Every commit uses `kuotunyu <61350295+kuotunyu@users.noreply.github.com>` for author and committer.
- Do not amend, reset, rebase, stash, cherry-pick, clean historical artifacts, push, merge, tag, release, publish, or modify another repository.
- Do not invoke `scripts/run_wave0_a11.ps1`, `docker build`, `docker run`, a model campaign, CUDA initialization, a real GPU lease, RDD, or Wave 1.
- Do not use, record, infer, or synthesize `steven003`; `steven002` is consumed and may appear only as immutable attempt-3 evidence.
- Preserve the non-A11 baseline at 64,306 files / `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95` and 21 images / `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.
- Preserve attempt 3 at 60 files / `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2`, 18 directories, image `sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd`, release record `72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93`, and released lease `a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f`.
- Set `PYTHONDONTWRITEBYTECODE=1` for every Python command and disable pytest cache with `-p no:cacheprovider`.

---

### Task 1: Enter the reviewed plan boundary and create RED three-attempt preservation tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py:17-182`
- Modify: `tests/gates/test_wave0_a11_launcher.py:486-640`
- Modify: `tests/gates/test_wave0_a11_launcher.py:1206-1614`
- Inspect: `scripts/run_wave0_a11.ps1:217-458`
- Inspect: `scripts/run_wave0_a11.ps1:746-1002`

**Interfaces:**
- Consumes: design commit `fc9aa0d8f9f94280ba0f38ee41b2007ba53a5676`; existing `_prior_attempts()`, `_preflight()`, `_run_prior_attempt_inventory()`, `Get-A11PriorAttemptInventory`, and `Test-A11ReadOnlyPreflight`.
- Produces: test-only attempt-3 constants and a closed three-attempt fixture used by all later destination/preflight tests.

- [ ] **Step 1: Verify the implementation entry gate before editing**

Run:

```powershell
$PlanHead = (git rev-parse HEAD).Trim()
$ExpectedDesignHead = 'fc9aa0d8f9f94280ba0f38ee41b2007ba53a5676'
$ExpectedPlanPath = 'docs/superpowers/plans/2026-08-29-val-wave0-a11-third-failure-recovery.md'
if ((git rev-parse "$PlanHead^").Trim() -cne $ExpectedDesignHead) { throw 'third recovery plan parent mismatch' }
if (@(git diff-tree --no-commit-id --name-only -r $PlanHead).Count -ne 1) { throw 'third recovery plan scope mismatch' }
if ((git diff-tree --no-commit-id --name-only -r $PlanHead).Trim() -cne $ExpectedPlanPath) { throw 'third recovery plan path mismatch' }
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'third recovery branch mismatch' }
if ((git config user.name).Trim() -cne 'kuotunyu') { throw 'Git user.name mismatch' }
if ((git config user.email).Trim() -cne '61350295+kuotunyu@users.noreply.github.com') { throw 'Git user.email mismatch' }
if (@(git status --porcelain=v1).Count -ne 0) { throw 'linked worktree dirty at implementation entry' }
if (@(git -C '<repo>' status --porcelain=v1).Count -ne 0) { throw 'canonical worktree dirty at implementation entry' }
```

Expected: no output and exit 0. Do not repair any mismatch.

- [ ] **Step 2: Add exact attempt-3 test constants**

Add these constants after the attempt-2 constants:

```python
_STREAM_RUN_ID = "wave0-a11-calibration-20260828T172921151Z-a0f55fa1"
_STREAM_VALIDATION_ID = "wave0-a11-validation-20260828T172921161Z-70928997"
_STREAM_OWNER = "steven002"
_STREAM_SOURCE = "ff5cfac5820415662e608886f1a10d7892f3ee00"
_STREAM_RUN_SHA256 = "628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2"
_STREAM_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "ff5cfac58204-20260828T172921151Z-a0f55fa1"
)
_STREAM_VALIDATION_TAG = (
    "vision-active-learning-loop:wave0-a11-validation-"
    "ff5cfac58204-20260828T172921161Z-70928997"
)
_STREAM_IMAGE_ID = (
    "sha256:0a92de665d56dc4c4dc859cc3723444c"
    "b4b6c06e04308ee574f93befd4da7efd"
)
_STREAM_RELEASE_SHA256 = (
    "72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93"
)
_STREAM_RELEASED_SHA256 = (
    "a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f"
)
```

Add the exact directory and key-record constants:

```python
_STREAM_DIRECTORIES = [
    "audit",
    "wave0",
    "wave0/checkpoints",
    "wave0/model_cache",
    "wave0/model_cache/snapshots",
    "wave0/model_cache/snapshots/facebook--dinov2-small",
    "wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056",
    "wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache",
    "wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface",
    "wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/download",
    "wave0/model_cache/snapshots/facebook--dinov2-small/ed25f3a31f01632728cabb09d1542f84ab7b0056/.cache/huggingface/trees",
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd",
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d",
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache",
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface",
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/download",
    "wave0/model_cache/snapshots/PekingU--rtdetr_r18vd/cc5b50f32f0100caaa3bd275343e2fb17762c73d/.cache/huggingface/trees",
    "wave0/receipts",
]
_STREAM_KEY_FILES = [
    {"path": "audit/00-identity.json", "size": 2873, "sha256": "e9c0743ef1b2311aac15b51e4208ff204ad7766581d1a440206bc2903d989461"},
    {"path": "audit/10-build.json", "size": 1234, "sha256": "2ea371296b5eedf28074a8fb966b1fe58a985629f966c89a348c8bc4ab00b4ab"},
    {"path": "audit/11-image-inspect.json", "size": 682, "sha256": "98e6a4b0f547c95ebd00d21caeec620283543906d839a24eabb67adc6945fffc"},
    {"path": "audit/20-cache-preflight.json", "size": 1900, "sha256": "9827ccd8ea4d9f3625e26db1caecda276ac1a452f0cb4dad409eed2d9eeb7236"},
    {"path": "audit/30-environment.json", "size": 1995, "sha256": "5523fce88357798387b5934baf32f311150f148ed95871f396539ab1682ef656"},
    {"path": "audit/31-model-assets.json", "size": 2051, "sha256": "9e9e0e88a94b217d26e96741dfc34db499b72f579460a1465a5a988f2cf7ba66"},
    {"path": "audit/32-model-contract.json", "size": 1910, "sha256": "4f2e6992aa40d9df1a0322565a6bdc2484f45fe6163eb5203e8efe911d3a85f8"},
    {"path": "audit/32-model-contract.stderr.log", "size": 1362, "sha256": "05a5801f0f54bdc7d8a5d6494f46b5b5d08df990d6137fdae012f753d96d79ce"},
    {"path": "audit/32-model-contract.stdout.log", "size": 5, "sha256": "c26de83abdc9496cd1301470918ec39ecca1cf389ef0ae1c6504da1800d1c431"},
    {"path": "audit/78-failure-diagnostic.json", "size": 853, "sha256": "f50f883e74594752d9c4e6e4b857814c9072f0bfc0d75d0dcd229d2081b12676"},
    {"path": "audit/79-historical-preservation-final.json", "size": 301, "sha256": "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d"},
    {"path": "audit/80-campaign-result.json", "size": 764, "sha256": "1787120f4635a02ba14e6b08d390b896ca03e855efc22cdf710983bf94dd8bab"},
    {"path": "audit/81-campaign-file-manifest.json", "size": 16740, "sha256": "ab28d20479a0b44a82bcb9c555f867c0c879a2da0cc0c117d2c4c8667749adf3"},
    {"path": "audit/82-campaign-closure.json", "size": 660, "sha256": "75267ce8cc36bc25a6c7e985c4b836038241706477656211fe1328dd102bf76a"},
    {"path": "wave0/receipts/model-contract.json", "size": 9623, "sha256": "307c95414578af6c6a90dc742fe359a5b985d2d6bd2e76e9228caf1475de4eaa"},
]
```

- [ ] **Step 3: Extend `_prior_attempts()` to a closed third state**

Keep attempts 1 and 2 unchanged. Add one authorization evidence row and this third attempt object:

```python
{
    "state": "foundation-stream-contract-failure",
    "run_id": _STREAM_RUN_ID,
    "source_commit": _STREAM_SOURCE,
    "specification_commit": _SPEC,
    "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
    "registered_run_ids": [_STREAM_RUN_ID, _STREAM_VALIDATION_ID],
    "registered_image_tags": [_STREAM_IMAGE_TAG, _STREAM_VALIDATION_TAG],
    "registered_paths": _registered_paths(
        artifact_root, [_STREAM_RUN_ID, _STREAM_VALIDATION_ID]
    ),
    "owner_authorization_id": _STREAM_OWNER,
    "run_file_count": 60,
    "run_inventory_sha256": _STREAM_RUN_SHA256,
    "directory_names": _STREAM_DIRECTORIES,
    "key_file_records": _STREAM_KEY_FILES,
    "image_tag": _STREAM_IMAGE_TAG,
    "image_id": _STREAM_IMAGE_ID,
    "release_record_sha256": _STREAM_RELEASE_SHA256,
    "released_lease_sha256": _STREAM_RELEASED_SHA256,
    "validation_present": False,
    "replica_directory_names_present": [],
    "checkpoint_file_paths_present": [],
    "closure_paths_present": [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ],
    "latest_write_utc": "2026-08-28T18:10:34.6753199Z",
    "links_absent": True,
}
```

Update `run_names`, `image_tags`, and `lease_names` to their exact three-run, two-image, and four-file chronological inventories.

- [ ] **Step 4: Extend the temporary inventory harness to materialize the third distinct state**

Create the exact 18 directories under `expected_run3`. Write the identity, key files, and enough deterministic filler files under the registered cache tree to make exactly 60 files. Create attempt 3's two lease-history files. Make the native-process fake return both exact image tags from `docker image ls` and the matching image ID for each inspect request.

Add defect controls for:

```python
(
    "run3-link",
    "extra-run",
    "stream-missing-closure",
    "stream-extra-directory",
    "stream-validation",
    "stream-replica",
    "stream-checkpoint",
    "stream-release-missing",
    "stream-unexpected-image",
    "docker-failure",
)
```

Return `(completed, run1_root, run2_root, run3_root, lease_root)`.

- [ ] **Step 5: Rename and extend the public preflight behavior tests**

Rename the acceptance test to
`test_read_only_preflight_accepts_exact_three_attempt_evidence`. Require the
three state names in exact order. Add independent mutations for every attempt-3
field, including `steven002`, run/peer IDs, source/spec/plan, count/digest,
directories, key records, image/tag, lease hashes, closure list, validation,
replicas, checkpoints, latest timestamp, and links. Require test-only `_OWNER`
to pass and require `_STREAM_OWNER` to fail with
`A11 prior owner authorization cannot be reused`.

- [ ] **Step 6: Run the attempt-3 focused tests and verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -q -k "three_attempt or prior_attempt_inventory or read_only_preflight or prior_a11_drift"
```

Expected: FAIL because production still requires exactly two attempts, one A11 image, and two A11 lease-history files. The first relevant failure must contain `A11 prior A11 envelope drifted` or `A11 prior attempt root inventory drifted`; syntax, fixture, collection, or unrelated failures do not satisfy RED.

---

### Task 2: Implement exact three-attempt inventory and preflight GREEN

**Files:**
- Modify: `scripts/run_wave0_a11.ps1:217-458`
- Modify: `scripts/run_wave0_a11.ps1:746-1002`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: closed `_prior_attempts()` test shape from Task 1 and immutable attempt-3 artifacts registered in the design.
- Produces: `Get-A11PriorAttemptInventory` with three records and `Test-A11ReadOnlyPreflight` that accepts only the exact three-attempt envelope.

- [ ] **Step 1: Register the third identity and host paths in `Get-A11PriorAttemptInventory`**

Add exact constants:

```powershell
$Run3Id = 'wave0-a11-calibration-20260828T172921151Z-a0f55fa1'
$Attempt3ImageTag = 'vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1'
$Run3Root = [IO.Path]::Combine($A11Root, $Run3Id)
$Run3ReleasedPath = [IO.Path]::Combine($LeaseRoot, "$Run3Id.released")
$Run3ReleaseRecordPath = [IO.Path]::Combine($LeaseRoot, "$Run3Id.release.json")
```

Include all three paths in the non-link root check and all three attempt roots in the recursive link scan. Require `run_names` to equal the three run IDs, `image_tags` to equal attempt 1 and attempt 3, and `lease_names` to equal attempt 1's and attempt 3's release/released pairs in ordinal order.

- [ ] **Step 2: Compute and validate attempt-3 filesystem state**

Parse `audit/00-identity.json`, bind its current and preregistered peer IDs, owners, source/specification/plan, image tags, and registered paths. Compute `Records3` with the existing canonical path/size/SHA-256 algorithm and `Directories3` with ordinal relative names. Compute the exact five closure names, replica directory names, checkpoint file paths, validation presence, and key file records.

Before returning, require:

```powershell
$Records3.Count -eq 60
$Directories3.Count -eq 18
$Closure3Present.Count -eq 5
$ReplicaDirectories3.Count -eq 0
$CheckpointFiles3.Count -eq 0
$Validation3Present -eq $false
```

Also require every exact directory name from the design. Missing or extra state throws `A11 prior attempt foundation-stream state drifted`.

- [ ] **Step 3: Bind both historical A11 images and attempt-3 lease history**

Inspect both registered tags independently and require one object per tag. Bind attempt 1 to its existing ID and attempt 3 to:

```text
sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd
```

Require attempt 3's current image labels to bind source
`ff5cfac5820415662e608886f1a10d7892f3ee00`, original specification and plan,
base digest, and current run ID. Hash the two attempt-3 lease records with the
existing `Get-FileHash` contract.

- [ ] **Step 4: Return the closed attempt-3 evidence object**

Return the exact field shape produced by Task 1. Add the third
`authorization_evidence` row for `steven002`. Preserve the first two attempt
objects byte-for-byte in meaning and keep `links_absent = $true` only after all
link checks pass.

- [ ] **Step 5: Extend `Test-A11ReadOnlyPreflight` with closed constants**

Require cardinalities `3` run names, `2` image tags, `4` lease names, `3`
authorization rows, and `3` attempt objects. Extend the authorization key loop
to `0..2`. Define a third state-specific key set matching Task 1; do not reuse
attempt 1 or 2's schema.

Require attempt 3's exact:

- current/peer IDs and image tags;
- source/specification/plan commits;
- registered paths and `steven002`;
- 60-file count and inventory SHA-256;
- 18 directory names and 15 key file records;
- image tag/ID and two lease-history hashes;
- complete ordered closure list;
- absent validation, replicas, and checkpoints;
- valid UTC latest-write value; and
- `links_absent == $true`.

Keep the existing final prior-owner membership test so
`OwnerAuthorizationId=steven002` fails before identity creation.

- [ ] **Step 6: Run focused preservation tests and verify GREEN**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -q -k "three_attempt or prior_attempt_inventory or read_only_preflight or prior_a11_drift or phase_destination"
```

Expected: all selected tests pass; no warning or bytecode/cache artifact is created.

---

### Task 3: Create RED model-loading presentation boundary tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py:247-435`
- Modify: `tests/gates/test_wave0_a11_launcher.py:862-1204`
- Modify: `tests/gates/test_wave0_a11_launcher.py:2087-2284`
- Inspect: `scripts/run_wave0_a11.ps1:1222-1245`
- Inspect: `scripts/run_wave0_a11.ps1:1335-1382`
- Inspect: `scripts/run_wave0_a11.ps1:1617-1697`

**Interfaces:**
- Consumes: exact observed stderr trigger and existing real-function AST harness.
- Produces: behavior tests for model-contract and replica container argv plus strict residual-stderr rejection.

- [ ] **Step 1: Add a real-foundation argv harness**

Exercise real `Invoke-A11Foundation`. The fake `Invoke-A11Native` records every
argument list, writes schema-valid stage receipts, and behaves as follows for
the model-contract call:

```powershell
$HasProgress = (@($ArgumentList) -join "`n").Contains("HF_HUB_DISABLE_PROGRESS_BARS=1")
$HasVerbosity = (@($ArgumentList) -join "`n").Contains("TRANSFORMERS_VERBOSITY=error")
$Stderr = if ($HasProgress -and $HasVerbosity) { '' } else { "`rLoading weights: 100%`n[transformers] RTDetrForObjectDetection LOAD REPORT`n" }
return [pscustomobject]@{ ExitCode=0; Stdout="PASS`n"; Stderr=$Stderr }
```

Environment retains empty stdout; assets and model-contract retain `PASS\n`.
The test requires environment and assets argv not to contain either control,
and model-contract argv to contain each exact `-e`, value pair once, in order,
before the image ID.

- [ ] **Step 2: Add replica behavior and argv tests**

Exercise real `New-A11ReplicaArguments` and real `Invoke-A11Replica`. Make the
native fake publish the existing receipt/checkpoint/cid evidence but emit the
same presentation stderr unless both exact controls are present. Require
successful invocation only with both controls and require each pair once before
the image ID.

- [ ] **Step 3: Add strict residual-stderr regression cases**

Parameterize model-contract and replica calls with exact stdout and valid
evidence but `Stderr='unexpected diagnostic'`. Require both to fail. Assert the
source still contains both production predicates:

```powershell
$Result.Stderr -ceq ''
```

Do not assert acceptance by trimming, matching, or parsing stderr.

- [ ] **Step 4: Add closed-control source assertions**

Require the source to contain the two exact values once in one helper, to call
that helper from only model-contract and replica argument construction, and to
exclude:

```text
HF_HUB_VERBOSITY
TRANSFORMERS_NO_ADVISORY_WARNINGS
--env-file
stderr allowlist
Trim()
```

The `Trim()` exclusion is scoped to stream comparisons, not unrelated Git
identity reads.

- [ ] **Step 5: Run presentation tests and verify RED**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -q -k "model_load_presentation or foundation_model_contract or replica_model_load or residual_stderr"
```

Expected: model-contract and replica presentation tests fail because neither
production argv currently includes both exact controls. Residual-stderr tests
may already pass and are regression evidence, not the RED trigger.

---

### Task 4: Implement exact presentation controls and verify GREEN

**Files:**
- Modify: `scripts/run_wave0_a11.ps1:461-491`
- Modify: `scripts/run_wave0_a11.ps1:1335-1382`
- Modify: `scripts/run_wave0_a11.ps1:1617-1697`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: Task 3 RED behavior tests.
- Produces: `New-A11ModelLoadPresentationArguments`, an explicit model-contract switch on `Invoke-A11DockerStage`, and exact replica container controls.

- [ ] **Step 1: Add the closed presentation helper**

Add exactly:

```powershell
function New-A11ModelLoadPresentationArguments {
    return @(
        '-e', 'HF_HUB_DISABLE_PROGRESS_BARS=1',
        '-e', 'TRANSFORMERS_VERBOSITY=error'
    )
}
```

The helper has no parameter and does not read the host environment.

- [ ] **Step 2: Add the explicit Docker-stage switch**

Add `[switch]$SuppressModelLoadPresentation` to
`Invoke-A11DockerStage`. Materialize:

```powershell
$PresentationArguments = if ($SuppressModelLoadPresentation) {
    @(New-A11ModelLoadPresentationArguments)
} else { @() }
```

Insert `$PresentationArguments` after `CUBLAS_WORKSPACE_CONFIG=:4096:8` and
before `VAL_ARTIFACT_ROOT`. Do not change the stream predicate, receipt
verification, or audit publication.

- [ ] **Step 3: Enable the switch only for model-contract**

Keep environment and assets calls unchanged. Add
`-SuppressModelLoadPresentation` only to the `32-model-contract`
`Invoke-A11DockerStage` call.

- [ ] **Step 4: Add the same helper output to replica Docker arguments**

Build `New-A11ReplicaArguments` as the existing prefix through
`CUBLAS_WORKSPACE_CONFIG=:4096:8`, concatenate
`@(New-A11ModelLoadPresentationArguments)`, then append the existing mounts,
image ID, and unchanged `val probe training-feasibility` arguments. Do not add
the controls to cache preflight, environment, or model-assets.

- [ ] **Step 5: Run focused presentation tests and verify GREEN**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -q -k "model_load_presentation or foundation_model_contract or replica_model_load or residual_stderr or foundation_stages or cache_preflight_and_replica"
```

Expected: all selected tests pass. Exact stdout, empty stderr, receipt,
checkpoint, and cache-preflight contracts remain green.

---

### Task 5: Run complete non-runtime verification and independent review

**Files:**
- Verify: `scripts/run_wave0_a11.ps1`
- Verify: `tests/gates/test_wave0_a11_launcher.py`
- Preserve: `D:\vision-active-learning-loop-artifacts\wave0`

**Interfaces:**
- Consumes: Tasks 1 through 4 GREEN candidate.
- Produces: complete test/style/parser/preservation/review evidence eligible for the single implementation commit.

- [ ] **Step 1: Run the complete A11 launcher suite**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -q
```

Expected: all tests pass.

- [ ] **Step 2: Run original A11 focused suites**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_numerical_replay.py `
  tests/probes/test_training_feasibility.py `
  tests/probes/test_model_contract.py `
  tests/models/test_assets.py `
  tests/training/test_checkpoint_io.py `
  tests/gates/test_wave0_gate.py -q
```

Expected: all tests pass.

- [ ] **Step 3: Run the complete CPU suite**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider -q
```

Expected: all tests pass with no GPU/model campaign.

- [ ] **Step 4: Run style, lock, diff, and parser gates**

Run:

```powershell
uv run --no-sync black --check tests/gates/test_wave0_a11_launcher.py
uv run --no-sync ruff check tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
pwsh -NoProfile -NonInteractive -Command '$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path "scripts/run_wave0_a11.ps1"),[ref]$tokens,[ref]$errors);if($errors.Count){$errors|ForEach-Object Message;exit 1}'
powershell.exe -NoProfile -NonInteractive -Command '$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path "scripts/run_wave0_a11.ps1"),[ref]$tokens,[ref]$errors);if($errors.Count){$errors|ForEach-Object Message;exit 1}'
```

Expected: every command exits 0.

- [ ] **Step 5: Audit exact implementation scope and forbidden capability**

Run:

```powershell
$Allowed = @('scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')
$Changed = @(git diff --name-only)
if ($Changed.Count -ne 2 -or @($Changed | Where-Object { $_ -cnotin $Allowed }).Count -ne 0) { throw 'third recovery implementation scope mismatch' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging must remain empty before final gate' }
if (@(Get-ChildItem -LiteralPath src,tests,scripts -Recurse -Force | Where-Object { $_.Name -eq '__pycache__' -or $_.Extension -eq '.pyc' }).Count -ne 0) { throw 'Python cache artifact detected' }
if ((git -C '<repo>' status --porcelain=v1).Count -ne 0) { throw 'canonical worktree changed' }
```

Inspect the diff and require no launcher invocation, retry, cleanup, Wave 1,
arbitrary env forwarding, stderr normalization, or use of `steven003`.

- [ ] **Step 6: Recompute read-only runtime preservation evidence**

Load production inventory and preflight function definitions through the AST
harness without invoking the script entry point. Require:

```text
historical files: 64306 / e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
historical images: 21 / 9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
A11 runs: 3
A11 images: 2
A11 lease-history files: 4
active leases: 0
project containers: 0
attempt 3 files: 60 / 628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2
attempt 3 directories: 18
validation root: absent
replicas/checkpoints: absent
steven003 identity records: 0
```

Also require Docker to report Linux and numeric CUDA compute rows to be zero.
This is read-only evidence; do not create an identity or destination.

- [ ] **Step 7: Perform Critical/Important review**

Review the complete candidate against:

```text
docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md §5.2.15
docs/superpowers/specs/2026-08-28-val-wave0-a11-launcher-failure-recovery-design.md
docs/superpowers/specs/2026-08-28-val-wave0-a11-preserved-attempt-preflight-design.md
docs/superpowers/specs/2026-08-28-val-wave0-a11-second-failure-recovery-design.md
docs/superpowers/specs/2026-08-29-val-wave0-a11-third-failure-recovery-design.md
```

Require Critical=0 and Important=0. Fix any finding through a new RED/GREEN
cycle and repeat affected gates. Do not commit with an open finding.

---

### Task 6: Create the single implementation commit and verify the committed tree

**Files:**
- Commit: `scripts/run_wave0_a11.ps1`
- Commit: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: all Task 5 gates green and Critical=0/Important=0.
- Produces: one reviewed implementation commit; no runtime attempt.

- [ ] **Step 1: Stage only the implementation allowlist**

Run:

```powershell
git add -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
$Staged = @(git diff --cached --name-only)
if ($Staged.Count -ne 2 -or $Staged[0] -cne 'scripts/run_wave0_a11.ps1' -or $Staged[1] -cne 'tests/gates/test_wave0_a11_launcher.py') { throw 'staged implementation allowlist mismatch' }
git diff --cached --check
```

Expected: exactly the two allowlisted paths and no diff error.

- [ ] **Step 2: Commit once with exact identity**

Run:

```powershell
git commit -m "fix: recover A11 model-load stream boundary"
```

Expected: one new commit whose direct parent is this plan commit and whose
author/committer are exact.

- [ ] **Step 3: Repeat committed-tree focused, parser, and scope checks**

Run:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run --no-sync pytest -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -q
pwsh -NoProfile -NonInteractive -Command '$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path "scripts/run_wave0_a11.ps1"),[ref]$tokens,[ref]$errors);if($errors.Count){$errors|ForEach-Object Message;exit 1}'
powershell.exe -NoProfile -NonInteractive -Command '$tokens=$null;$errors=$null;[void][Management.Automation.Language.Parser]::ParseFile((Resolve-Path "scripts/run_wave0_a11.ps1"),[ref]$tokens,[ref]$errors);if($errors.Count){$errors|ForEach-Object Message;exit 1}'
git diff HEAD^ --check
git status --short --branch
git show -1 --format='%H|%P|%an|%ae|%cn|%ce|%s' --name-only
```

Expected: tests and parsers pass; linked worktree is clean; commit changes
exactly the two implementation paths; parent is the plan commit.

- [ ] **Step 4: Repeat the complete read-only preservation gate**

Re-run Task 5 Step 6 from the committed tree. Expected: every count, digest,
absence, Docker/GPU safety value, and unused-authorization check remains exact.

- [ ] **Step 5: Stop without runtime**

Report design, plan, and implementation commits; RED/GREEN evidence; focused,
full, style, lock, diff, parser, review, and preservation results. State
explicitly that no launcher, Docker build/run, GPU/model campaign, validation,
Wave 1, push, merge, or release occurred, and that `steven003` remains unused.
