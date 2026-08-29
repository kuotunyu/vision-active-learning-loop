# Wave 0 A11 Fourth Failure-Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `executing-plans` to implement this plan task-by-task. Use `test-driven-development` for Tasks 2–5 and `verification-before-completion` for Task 6. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove the host-dependent cache-inventory ordering defect that caused the fourth A11 attempt to fail after twelve successful calibration replicas, then extend the launcher’s fail-closed preservation contract to the complete four-attempt evidence envelope without starting another runtime attempt.

**Architecture:** Both cache inventory producers first normalize each regular file to its relative POSIX path and then order those strings with Unicode ordinal semantics before canonical JSON hashing. Python uses its native string ordering; PowerShell uses `StringComparer.Ordinal`. The launcher retains its current historical validators and adds one exact fourth-attempt record, so any missing, extra, linked, mutated, or reused object continues to block entry.

**Tech Stack:** Python 3.12.11; pytest 9.0.2; PowerShell 7 and Windows PowerShell 5.1 parser checks; Git; the existing `uv`/`uvx` toolchain. Docker and GPU runtime are deliberately excluded from this recovery implementation.

## Authority and non-negotiable constraints

- The approved design is `docs/superpowers/specs/2026-08-29-val-wave0-a11-fourth-failure-recovery-design.md` at commit `9b508969776eb4a9c5d755ff5685384c13c7c393`.
- This plan commit must be the direct child of that design commit and must change only this plan file.
- Implementation is authorized inline. The implementation commit must be the direct child of the plan commit, must be a single append-only commit, and must change exactly these four tracked paths:
  - `scripts/run_wave0_a11.ps1`
  - `tests/gates/test_wave0_a11_launcher.py`
  - `src/vision_active_learning_loop/gates/statistical_replay.py`
  - `tests/gates/test_statistical_replay.py`
- Author and committer must both be exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, push, merge, tag, release, or change another repository.
- Do not build or run Docker images or containers; do not acquire a GPU lease; do not launch calibration or validation; do not run Wave 1.
- Do not generate, infer, reserve, or reuse an `OwnerAuthorizationId`. `steven003` is consumed evidence and may only appear as the immutable identity of the fourth attempt.
- Never repair a dirty or mismatched entry state. Preserve it and stop with evidence.
- Existing A11 run directories, images, leases, receipts, checkpoints, logs, and historical non-A11 objects are read-only.

## Fixed fourth-attempt evidence

The new launcher contract must require this exact record:

```text
state                         aggregate-cache-inventory-contract-failure
calibration run              wave0-a11-calibration-20260829T050706309Z-f5a0129e
preregistered validation     wave0-a11-validation-20260829T050706319Z-c6652f48
owner                         steven003
source                        77f8eecb3b8c0f471a4e980269187ac02a3b9ebc
specification                 b59b0d4407b98b460f6166ea7288ba6021dc7a78
original A11 plan             7dbd3a7576ea76beccfc64f748c4e495259ea89b
run files                     137
run inventory SHA-256         f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717
directories                   30
replica directories           calibration-00 through calibration-11
checkpoint files              calibration-NN/step-000001.pt for NN 00 through 11
image tag                     vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e
image ID                      sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e
release record SHA-256        aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1
released lease SHA-256        b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c
latest write UTC              2026-08-29T06:13:25.1659510Z
success calibration receipt   absent
validation root/image/lease   absent
closure files                 78, 79, 80, 81, and 82 present
active lease/container        absent
```

The complete A11 envelope is exactly four calibration run directories, three calibration image tags, six release-history files, and four consumed owner identities. The immutable historical non-A11 baseline remains 64,306 files with inventory SHA-256 `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`; the 21-image historical baseline remains `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.

---

### Task 1: Re-freeze the entry identity and preservation envelope

**Files:**
- Modify: none
- Read: Git topology, the approved design and plan, A11 artifacts, historical artifact inventory, Docker metadata

- [ ] **Step 1: Prove the docs lineage and worktree topology**

Run from the linked worktree:

```powershell
$Design = '9b508969776eb4a9c5d755ff5685384c13c7c393'
$PlanPath = 'docs/superpowers/plans/2026-08-29-val-wave0-a11-fourth-failure-recovery.md'
$Plan = (git log -1 --format='%H' -- $PlanPath).Trim()
if ((git rev-parse "$Plan^").Trim() -cne $Design) { throw 'plan parent mismatch' }
if (@(git diff-tree --no-commit-id --name-only -r $Plan).Count -ne 1) {
    throw 'plan commit scope mismatch'
}
git branch --show-current
git worktree list --porcelain
git status --short
git diff --cached --name-only
git -C '<repo>' status --short
```

Require branch `codex/wave0-model-contract`, HEAD equal to the plan commit, the plan as its only path, clean linked and canonical worktrees, empty staging, and a shared Git common directory. Stop without repair on any mismatch.

- [ ] **Step 2: Independently rehash all preserved evidence**

Use read-only enumeration and the launcher's existing hashing conventions. Require the four exact run names, three exact A11 image tags, six exact lease-history names, no active lease, no project container, no validation destination for attempt four, and no links/reparse points anywhere in the registered prior-attempt paths. Recompute every attempt inventory and key-record digest, including the fixed fourth-attempt values above. Recompute both historical baselines.

- [ ] **Step 3: Prove no runtime side effect occurred**

Record in the execution notes that Task 1 used only `docker info`, `docker image inspect`, `docker ps`, filesystem reads, and Git reads. Do not call the launcher or any Docker/GPU mutation command.

---

### Task 2: Add RED cross-platform cache-order tests

**Files:**
- Modify: `tests/gates/test_statistical_replay.py`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: those same files

- [ ] **Step 1: Add a Python mixed-case ordinal-order regression**

Create a cache fixture whose relative paths deliberately distinguish Windows culture/path ordering from ordinal code-point ordering:

```python
def test_model_cache_inventory_uses_relative_posix_ordinal_order(
    tmp_path: Path,
) -> None:
    cache = tmp_path / "model_cache"
    files = {
        "snapshots/PekingU--rtdetr_r18vd/weights.bin": b"detector",
        "snapshots/facebook--dinov2-small/weights.bin": b"backbone",
    }
    for relative, content in files.items():
        path = cache / Path(relative)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    records = [
        {
            "path": relative,
            "size": len(files[relative]),
            "sha256": hashlib.sha256(files[relative]).hexdigest(),
        }
        for relative in sorted(files)
    ]
    expected = canonical_json_sha256({"files": records})

    assert statistical_replay._model_cache_inventory_sha256(cache) == expected
```

The expected order is `PekingU...` then `facebook...`, derived from explicit normalized strings rather than `Path` ordering.

- [ ] **Step 2: Strengthen the PowerShell/Python parity fixture**

In `test_cache_inventory_digest_matches_python_canonical_json`, replace the all-lowercase fixture with the same `PekingU--...` and `facebook--...` paths. Build the expected record list by sorting explicit `relative.as_posix()` strings, not `sorted(cache.rglob("*"))`. Keep the download-metadata timestamp-normalization assertion.

- [ ] **Step 3: Run the focused tests and capture RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_statistical_replay.py::test_model_cache_inventory_uses_relative_posix_ordinal_order `
  tests/gates/test_wave0_a11_launcher.py::test_cache_inventory_digest_matches_python_canonical_json
```

Require both tests to fail only because the observed digest follows the old host-dependent ordering. If either passes before production changes, stop and re-evaluate the fixture; do not weaken the assertion.

---

### Task 3: Implement one canonical cache-inventory order

**Files:**
- Modify: `src/vision_active_learning_loop/gates/statistical_replay.py`
- Modify: `scripts/run_wave0_a11.ps1`
- Test: `tests/gates/test_statistical_replay.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

- [ ] **Step 1: Normalize before sorting in Python**

In `_model_cache_inventory_sha256`, retain every link/type/metadata validation but collect `(relative_posix, path)` pairs before hashing:

```python
inventory_files: list[tuple[str, Path]] = []
for path in root.rglob("*"):
    if path.is_symlink():
        raise StatisticalReplayError("model cache links are forbidden")
    if path.is_dir():
        continue
    if not path.is_file():
        raise StatisticalReplayError("model cache contains a non-file entry")
    inventory_files.append((path.relative_to(root).as_posix(), path))

for relative, path in sorted(inventory_files, key=lambda item: item[0]):
    # Preserve the existing metadata normalization and file hashing exactly.
```

Do not case-fold, locale-transform, lower-case, or introduce a fallback digest.

- [ ] **Step 2: Normalize before sorting in PowerShell**

In `Get-A11CacheInventorySha256`, replace `Sort-Object FullName -CaseSensitive` with a typed list ordered by `StringComparer.Ordinal` over normalized relative paths:

```powershell
$InventoryFiles = [Collections.Generic.List[object]]::new()
foreach ($Item in @(Get-ChildItem -LiteralPath $Resolved -File -Recurse -Force)) {
    $Relative = $Item.FullName.Substring($Resolved.Length).TrimStart('\', '/')
    $Relative = $Relative.Replace('\', '/')
    $InventoryFiles.Add([pscustomobject][ordered]@{
        relative = $Relative
        item = $Item
    })
}
$InventoryFiles.Sort(
    [Collections.Generic.Comparer[object]]::Create(
        [Comparison[object]]{
            param($Left, $Right)
            return [StringComparer]::Ordinal.Compare(
                [string]$Left.relative,
                [string]$Right.relative
            )
        }
    )
)
foreach ($Entry in $InventoryFiles) {
    $Relative = [string]$Entry.relative
    $Item = $Entry.item
    # Preserve metadata normalization and SHA-256 calculation exactly.
}
```

Retain the existing reparse-point checks and canonical JSON record shape. This implementation must parse under both PowerShell 7 and Windows PowerShell 5.1.

- [ ] **Step 3: Run GREEN and the adjacent inventory tests**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_statistical_replay.py -k 'model_cache_inventory' `
  tests/gates/test_wave0_a11_launcher.py -k 'cache_inventory'
```

Require the new cross-platform tests and existing metadata/link tests to pass.

---

### Task 4: Add RED fourth-attempt preservation tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

- [ ] **Step 1: Encode the immutable fourth-attempt fixture**

Add constants for the run/validation IDs, source, owner `steven003`, image tag/ID, run digest, release digests, directory list, exact key file records, twelve replica directories, twelve checkpoint paths, five closure paths, and latest-write timestamp from the fixed evidence section. Extend `_prior_attempts()` to model four attempts, three image tags, six lease files, and four authorization-evidence records.

The attempt object uses the closed key set:

```python
{
    "state": "aggregate-cache-inventory-contract-failure",
    "run_id": _AGGREGATE_RUN_ID,
    "source_commit": _AGGREGATE_SOURCE,
    "specification_commit": _SPEC,
    "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
    "registered_run_ids": aggregate_run_ids,
    "registered_image_tags": [_AGGREGATE_IMAGE_TAG, _AGGREGATE_VALIDATION_TAG],
    "registered_paths": _registered_paths(artifact_root, aggregate_run_ids),
    "owner_authorization_id": "steven003",
    "run_file_count": 137,
    "run_inventory_sha256": _AGGREGATE_RUN_SHA256,
    "directory_names": _AGGREGATE_DIRECTORIES,
    "key_file_records": _AGGREGATE_KEY_FILES,
    "image_tag": _AGGREGATE_IMAGE_TAG,
    "image_id": _AGGREGATE_IMAGE_ID,
    "release_record_sha256": _AGGREGATE_RELEASE_SHA256,
    "released_lease_sha256": _AGGREGATE_RELEASED_SHA256,
    "validation_present": False,
    "replica_directory_names_present": [f"calibration-{i:02d}" for i in range(12)],
    "checkpoint_file_paths_present": [
        f"wave0/checkpoints/calibration-{i:02d}/step-000001.pt"
        for i in range(12)
    ],
    "success_receipt_present": False,
    "closure_paths_present": [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ],
    "latest_write_utc": "2026-08-29T06:13:25.1659510Z",
    "links_absent": True,
}
```

- [ ] **Step 2: Extend the synthetic filesystem inventory fixture**

Update `_run_prior_attempt_inventory` to create attempt four and return its root. Add defect cases for a run-4 junction, unexpected validation root, missing/extra replica, missing/extra checkpoint, unexpected success receipt, altered key file, extra run/image/lease, and attempt-four authorization/source/state drift.

- [ ] **Step 3: Update preflight and destination tests to the four-attempt envelope**

Adjust all exact cardinality and ordered-equality assertions. Add one positive assertion and focused negative tests proving every fourth-attempt field fails closed. Preserve the existing attempt 1–3 negative tests unchanged in intent.

- [ ] **Step 4: Capture RED before launcher changes**

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'prior_attempt or preflight or destination'
```

Require failures to identify the current three-attempt production contract. A fixture-construction or syntax error is not acceptable RED.

---

### Task 5: Extend the launcher to preserve exactly four attempts

**Files:**
- Modify: `scripts/run_wave0_a11.ps1`
- Test: `tests/gates/test_wave0_a11_launcher.py`

- [ ] **Step 1: Extend `Get-A11PriorAttemptInventory`**

Add attempt-four constants and paths. Enumerate and validate the fourth run with the same no-link, exact-file, exact-directory, exact-image, exact-lease, exact-identity, and exact-registered-destination helpers already used for attempts 1–3. Require:

- the calibration run exists and validation peer does not;
- all 137 files and 30 directories match exactly;
- twelve replica directories and twelve `step-000001.pt` checkpoints exist;
- every calibration replica receipt is present and the aggregate success receipt is absent;
- the five closure artifacts exist;
- the calibration image tag resolves to the exact ID and the validation tag is absent;
- the release record and released lease hashes match;
- no active lease, container, link/reparse point, or unregistered path exists.

Return `$Attempt4`, append the fourth authorization-evidence record, and return `attempts = @($Attempt1, $Attempt2, $Attempt3, $Attempt4)`.

- [ ] **Step 2: Extend `Test-A11ReadOnlyPreflight`**

Require exact ordered arrays for four run names, three image tags, six lease names, four authorization records, and four attempt records. Add `$ExpectedAttempt4Keys`, compare its key set, then validate every fixed value and exact list from this plan. Add `steven003` to consumed owners so any future caller using it is rejected. Do not loosen the owner ID syntax or uniqueness rules.

- [ ] **Step 3: Extend destination-absence cardinality without changing creation behavior**

Change `Test-A11PhaseDestinationsAbsent` and any adapter contract from exactly three prior attempts to exactly four. Continue rejecting every registered prior path/tag/run/owner. Do not add reuse, cleanup, retry, or overwrite behavior.

- [ ] **Step 4: Run the full launcher suite GREEN**

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Require all positive and adversarial launcher adapter tests to pass without invoking Docker or GPU operations.

---

### Task 6: Verify, review, and create the one implementation commit

**Files:**
- Modify: none beyond the four-file implementation allowlist
- Verify: all project tests and immutable evidence

- [ ] **Step 1: Run focused and adjacent suites**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider
```

- [ ] **Step 2: Run format, lint, lock, parser, and whitespace gates**

```powershell
uvx --offline black --check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py
uvx --offline ruff check `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
pwsh -NoProfile -NonInteractive -Command `
  '$null=$t=$e=$null; [Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e) | Out-Null; if($e.Count){throw ($e.Message -join "; ")}'
powershell.exe -NoProfile -NonInteractive -Command `
  '$null=$t=$e=$null; [Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e) | Out-Null; if($e.Count){throw ($e.Message -join "; ")}'
```

- [ ] **Step 3: Re-run read-only preservation and scope gates**

Recompute the complete four-attempt and historical baselines exactly as in Task 1. Use a clearly synthetic in-memory test owner only when calling the pure read-only preflight validator; do not write or reserve it. Require no runtime object change since Task 1.

Require the working tree union to be exactly:

```text
scripts/run_wave0_a11.ps1
src/vision_active_learning_loop/gates/statistical_replay.py
tests/gates/test_statistical_replay.py
tests/gates/test_wave0_a11_launcher.py
```

Require staging empty before review. Inspect `git diff --stat`, `git diff --name-only`, `git diff`, forbidden strings, and the absence of generated `__pycache__`, `.pyc`, `.pytest_cache`, or runtime artifacts.

- [ ] **Step 4: Perform an independent cold review**

Review against the approved design and this plan, focusing on:

- normalization occurs before sorting in both languages;
- both sort paths are Unicode ordinal and produce the same canonical JSON;
- no alternate/fallback digest, case folding, locale dependency, or compatibility escape exists;
- attempts 1–3 remain byte-for-byte protected in behavior;
- attempt four is exact and fail closed;
- no launcher/runtime path became reachable during recovery verification.

Resolve any issue with a fresh RED test before implementation changes.

- [ ] **Step 5: Stage exactly four files and commit once**

```powershell
git add -- `
  scripts/run_wave0_a11.ps1 `
  src/vision_active_learning_loop/gates/statistical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/gates/test_wave0_a11_launcher.py
if ((git diff --cached --name-only).Count -ne 4) { throw 'staged scope mismatch' }
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git commit -m 'fix: canonicalize A11 cache inventory order'
```

- [ ] **Step 6: Verify the committed candidate and stop before runtime**

Require the implementation commit parent to be the plan commit, the exact four changed paths, exact author/committer identity, clean linked and canonical worktrees, empty staging, and unchanged four-attempt/historical preservation hashes. Re-run at least the two focused suites and parser checks from the committed tree.

Report the plan and implementation commit hashes, all gate results, the preserved evidence identities, and explicitly state that no Docker build/run, GPU campaign, calibration, validation, Wave 1, push, merge, or release occurred. A future runtime attempt requires a newly supplied exact `OwnerAuthorizationId` and a separate authorization bound to the committed source/specification/original-plan/branch identities; do not infer or request that ID during this plan.
