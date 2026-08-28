# Wave 0 A11 Preserved-Attempt Preflight Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the A11 launcher admit one entirely fresh calibration/validation attempt while proving that the registered failed attempt remains exact and every new destination is absent before the first write.

**Architecture:** Replace the original empty-A11-root assumption with a closed prior-attempt evidence object, then generate two in-memory phase identities and validate their exact destinations before initialization. Keep the existing two-phase campaign, no-clobber publication, failure closure, statistical replay, model, GPU, and receipt contracts unchanged.

**Tech Stack:** PowerShell 7 and Windows PowerShell 5.1 parser; Python 3.12.11; pytest 9.0.2; Black and Ruff; Git linked worktree; read-only Docker/image inspection for preservation and destination verification only.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-08-28-val-wave0-a11-preserved-attempt-preflight-design.md` at commit `764fba49bb00c5b26832ea9a9414eb68be04f460`.
- This plan commit must be that design commit's direct child and must add only this plan file.
- The implementation starting candidate is `f10822e67ee90013c8e7a9d423d97c64993e676a`; the design and plan commits are documentation-only descendants.
- The original Section 5.2.15 specification and plan identities remain `b59b0d4407b98b460f6166ea7288ba6021dc7a78` and `7dbd3a7576ea76beccfc64f748c4e495259ea89b`.
- The failed run `wave0-a11-calibration-20260828T045848083Z-b9917463`, image `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`, and authorization `OWNER-A11-RUNTIME-20260828-01` are immutable and must never be reused, repaired, renamed, moved, or completed.
- This authorization covers a CPU-only/TDD launcher repair. Do not invoke `scripts/run_wave0_a11.ps1`, build or run an image, download a cache, acquire a GPU lease, initialize a model, run a replica, start calibration or validation, access RDD data, or start Wave 1.
- Do not infer or synthesize a future `OwnerAuthorizationId`. No new runtime authorization identity may appear during implementation.
- The implementation tracked-file allowlist is exactly `scripts/run_wave0_a11.ps1` and `tests/gates/test_wave0_a11_launcher.py`. A third implementation path is a hard stop for owner review.
- Keep the 12+12 cohorts, all 66-pair and 13-metric contracts, thresholds, ceilings, receipt schemas, model/cache/GPU identities, phase order, stream contracts, lease semantics, closure behavior, and every Python production module unchanged.
- Preserve the failed run at 48 files and canonical inventory SHA-256 `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b`.
- Preserve 64,306 historical files at inventory SHA-256 `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95` and 21 historical images at inventory SHA-256 `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.
- Preserve failed-run history record SHA-256 `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`, released lease SHA-256 `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`, and release record SHA-256 `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`.
- Keep `78-failure-diagnostic.json`, `80-campaign-result.json`, `81-campaign-file-manifest.json`, and `82-campaign-closure.json` absent from the failed run.
- Keep staging empty through every RED/GREEN cycle. After every gate passes, create one implementation commit with author and committer `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- No amend, rebase, squash, reset, stash, history rewrite, cleanup, push, merge, tag, Release, publication, or change to another repository is permitted.

## File Responsibility Map

- `scripts/run_wave0_a11.ps1`: collect and validate the prior A11 baseline, guard exact fresh destinations, accept a verified existing campaign parent, and order those checks before initialization.
- `tests/gates/test_wave0_a11_launcher.py`: CPU-only production-function adapters and regressions for prior evidence, destination collisions, parent safety, and orchestration order.
- `docs/superpowers/specs/2026-08-28-val-wave0-a11-preserved-attempt-preflight-design.md`: immutable requirements; inspect only.
- `docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md`: immutable Section 5.2.15 contract; inspect only.

---

### Task 1: Freeze the implementation entry state

**Files:**
- Modify: none
- Inspect: Git lineage, linked/canonical worktrees, prior A11 objects, historical artifacts, images, leases, and containers

**Interfaces:**
- Consumes: approved design commit `764fba49bb00c5b26832ea9a9414eb68be04f460` and this plan commit
- Produces: one read-only entry transcript and a clean two-file implementation gate

- [ ] **Step 1: Verify plan lineage and worktree isolation**

Run from the linked worktree:

```powershell
$PlanCommit = (git rev-parse HEAD).Trim()
$DesignCommit = '764fba49bb00c5b26832ea9a9414eb68be04f460'
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'branch mismatch' }
if ((git rev-parse "$PlanCommit^").Trim() -cne $DesignCommit) { throw 'plan parent mismatch' }
$PlanPaths = @(git diff-tree --no-commit-id --name-only -r $PlanCommit)
if (
    $PlanPaths.Count -ne 1 -or
    $PlanPaths[0] -cne 'docs/superpowers/plans/2026-08-28-val-wave0-a11-preserved-attempt-preflight.md'
) { throw 'plan scope mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree is dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }
if (-not [string]::IsNullOrWhiteSpace((git rev-parse --show-superproject-working-tree))) { throw 'worktree is a submodule' }
if ((git rev-parse --absolute-git-dir).Trim() -ceq (git rev-parse --path-format=absolute --git-common-dir).Trim()) { throw 'linked worktree isolation missing' }
```

Use `git worktree list --porcelain` to identify the canonical worktree and require its status to be empty. Preserve and report any mismatch; do not repair it.

- [ ] **Step 2: Recompute the immutable entry baseline read-only**

Using the same sorted record algorithm as `Get-A11JsonSha256`, require:

```text
failed run files: 48
failed run digest: fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b
historical files: 64306
historical digest: e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
historical images: 21
historical image digest: 9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
```

Also require the three fixed evidence hashes from Global Constraints, exact one-item A11 run and image-tag inventories, the failed image ID, the four absent closure paths, no active `GPU-*.json` lease, and no running project container. Docker calls are limited to `docker info`, `docker ps`, `docker inspect`, `docker image ls`, and `docker image inspect`.

- [ ] **Step 3: Run the clean CPU baseline**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider
```

Expected: the committed suite passes with no tracked or untracked output. If it fails, stop before edits.

---

### Task 2: Collect and validate the registered prior A11 attempt

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Modify: `scripts/run_wave0_a11.ps1`

**Interfaces:**
- Consumes: `Get-A11FileRecord`, `Get-A11JsonSha256`, `Invoke-A11Native`, `Resolve-A11Worktree`, `Test-A11ReadOnlyPreflight`
- Produces: `Get-A11PriorAttemptInventory -ArtifactRoot string` and closed `prior_a11_attempt` preflight evidence

- [ ] **Step 1: Add the closed Python evidence fixture**

Replace `_preflight()`'s `existing_destinations` member with this exact object and add constants for the registered values:

```python
_FAILED_RUN_ID = "wave0-a11-calibration-20260828T045848083Z-b9917463"
_FAILED_RUN_SHA256 = "fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b"
_FAILED_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "2622e402e4f5-20260828T045848083Z-b9917463"
)
_FAILED_IMAGE_ID = "sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5"


def _prior_attempt() -> dict[str, object]:
    return {
        "run_names": [_FAILED_RUN_ID],
        "run_file_count": 48,
        "run_inventory_sha256": _FAILED_RUN_SHA256,
        "historical_preservation_sha256": (
            "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d"
        ),
        "released_lease_sha256": (
            "146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322"
        ),
        "release_record_sha256": (
            "35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060"
        ),
        "closure_paths_present": [],
        "image_tags": [_FAILED_IMAGE_TAG],
        "image_id": _FAILED_IMAGE_ID,
        "lease_names": [f"{_FAILED_RUN_ID}.release.json", f"{_FAILED_RUN_ID}.released"],
        "links_absent": True,
    }
```

Set `"prior_a11_attempt": _prior_attempt()` in `_preflight()`.

- [ ] **Step 2: Add RED tests for closed preflight evidence**

Add these parameterized defects:

```python
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("run_names", []),
        ("run_names", [_FAILED_RUN_ID, "wave0-a11-unknown"]),
        ("run_file_count", 47),
        ("run_inventory_sha256", "0" * 64),
        ("historical_preservation_sha256", "0" * 64),
        ("released_lease_sha256", "0" * 64),
        ("release_record_sha256", "0" * 64),
        ("closure_paths_present", ["80-campaign-result.json"]),
        ("image_tags", []),
        ("image_tags", [_FAILED_IMAGE_TAG, "vision-active-learning-loop:wave0-a11-extra"]),
        ("image_id", "sha256:" + "0" * 64),
        ("lease_names", []),
        ("lease_names", [f"{_FAILED_RUN_ID}.released", "wave0-a11-extra.released"]),
        ("links_absent", False),
    ],
)
def test_read_only_preflight_rejects_prior_a11_drift(
    field: str, value: object
) -> None:
    evidence = _preflight()
    prior = dict(evidence["prior_a11_attempt"])
    prior[field] = value
    evidence["prior_a11_attempt"] = prior

    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0
    assert "prior A11" in completed.stderr
```

Update the existing identity/contention parameterization by deleting the obsolete `existing_destinations` row. Run:

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_read_only_preflight_accepts_exact_closed_evidence `
  tests/gates/test_wave0_a11_launcher.py::test_read_only_preflight_rejects_prior_a11_drift `
  tests/gates/test_wave0_a11_launcher.py::test_read_only_preflight_rejects_identity_contention_or_drift
```

Expected: FAIL because production still requires `existing_destinations` and has no `prior_a11_attempt` contract.

- [ ] **Step 3: Implement the closed prior-attempt comparison**

In `Test-A11ReadOnlyPreflight`, replace `existing_destinations` in `$ExpectedKeys` with `prior_a11_attempt`, then require the exact nested keys and registered values:

```powershell
$Prior = $Evidence.prior_a11_attempt
$ExpectedPriorKeys = @(
    'run_names', 'run_file_count', 'run_inventory_sha256',
    'historical_preservation_sha256', 'released_lease_sha256',
    'release_record_sha256', 'closure_paths_present', 'image_tags',
    'image_id', 'lease_names', 'links_absent'
)
if (Compare-Object ($ExpectedPriorKeys | Sort-Object) @($Prior.PSObject.Properties.Name | Sort-Object)) {
    throw 'A11 prior A11 evidence fields mismatch'
}
$ExpectedRunId = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
$ExpectedImageTag = 'vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
$RunNames = @($Prior.run_names)
$ClosurePaths = @($Prior.closure_paths_present)
$ImageTags = @($Prior.image_tags)
$LeaseNames = @($Prior.lease_names)
if (
    $RunNames.Count -ne 1 -or [string]$RunNames[0] -cne $ExpectedRunId -or
    [int]$Prior.run_file_count -ne 48 -or
    [string]$Prior.run_inventory_sha256 -cne 'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b' -or
    [string]$Prior.historical_preservation_sha256 -cne '927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d' -or
    [string]$Prior.released_lease_sha256 -cne '146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322' -or
    [string]$Prior.release_record_sha256 -cne '35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060' -or
    $ClosurePaths.Count -ne 0 -or
    $ImageTags.Count -ne 1 -or [string]$ImageTags[0] -cne $ExpectedImageTag -or
    [string]$Prior.image_id -cne 'sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5' -or
    $LeaseNames.Count -ne 2 -or
    [string]$LeaseNames[0] -cne "$ExpectedRunId.release.json" -or
    [string]$LeaseNames[1] -cne "$ExpectedRunId.released" -or
    $Prior.links_absent -cne $true
) { throw 'A11 prior A11 attempt drifted' }
```

Remove `existing_destinations` from the resource-contention condition; running project containers and active GPU leases remain forbidden.

- [ ] **Step 4: Add RED inventory-collector tests**

Create a temp artifact root containing the registered run name, `audit/79-historical-preservation-final.json`, and the two registered lease files. Stub `Invoke-A11Native` so `docker image ls` returns the registered tag and `docker image inspect` returns the registered image ID. Assert that `Get-A11PriorAttemptInventory` returns sorted run/image/lease names, the Python-recomputed run count/digest, the three file hashes, empty closure presence, and `links_absent == true`.

Add three failure cases:

```python
@pytest.mark.parametrize("defect", ["run-link", "lease-link", "docker-failure"])
def test_prior_attempt_inventory_rejects_links_or_docker_failure(
    tmp_path: Path, defect: str
) -> None:
    artifact = tmp_path / "artifacts"
    a11_root = artifact / "a11-runs"
    expected_run = a11_root / _FAILED_RUN_ID
    outside_run = tmp_path / "outside-run"
    run_root = outside_run if defect == "run-link" else expected_run
    expected_leases = artifact / "leases"
    outside_leases = tmp_path / "outside-leases"
    lease_root = outside_leases if defect == "lease-link" else expected_leases
    (run_root / "audit").mkdir(parents=True)
    lease_root.mkdir(parents=True)
    (run_root / "audit" / "79-historical-preservation-final.json").write_text(
        "history", encoding="utf-8"
    )
    (lease_root / f"{_FAILED_RUN_ID}.released").write_text(
        "released", encoding="utf-8"
    )
    (lease_root / f"{_FAILED_RUN_ID}.release.json").write_text(
        "release", encoding="utf-8"
    )
    junctions = []
    if defect == "run-link":
        a11_root.mkdir(parents=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_run))} "
            f"-Target {_ps(str(outside_run))} | Out-Null"
        )
    if defect == "lease-link":
        artifact.mkdir(exist_ok=True)
        junctions.append(
            f"New-Item -ItemType Junction -Path {_ps(str(expected_leases))} "
            f"-Target {_ps(str(outside_leases))} | Out-Null"
        )
    native = (
        "return [pscustomobject]@{ExitCode=125;Stdout='';Stderr='daemon unavailable'}"
        if defect == "docker-failure"
        else f"""
if ($ArgumentList[1] -ceq 'ls') {{
    return [pscustomobject]@{{ExitCode=0;Stdout={_ps(_FAILED_IMAGE_TAG + chr(10))};Stderr=''}}
}}
return [pscustomobject]@{{
    ExitCode=0;Stdout={_ps(json.dumps([{'Id': _FAILED_IMAGE_ID}]))};Stderr=''
}}
"""
    )
    body = f"""
{chr(10).join(junctions)}
function Invoke-A11Native {{ param($FilePath,$ArgumentList) {native} }}
Get-A11PriorAttemptInventory -ArtifactRoot {_ps(str(artifact))} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Get-A11FileRecord",
            "Get-A11JsonSha256",
            "Get-A11PriorAttemptInventory",
        ),
        body,
    )
    assert completed.returncode != 0
```

For `run-link` and `lease-link`, create a Windows junction or symbolic link only inside `tmp_path`; skip with the existing platform helper if link creation is unavailable. For `docker-failure`, return exit 125 and nonempty stderr from the stub.

Run:

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_prior_attempt_inventory_returns_closed_sorted_evidence `
  tests/gates/test_wave0_a11_launcher.py::test_prior_attempt_inventory_rejects_links_or_docker_failure
```

Expected: FAIL because `Get-A11PriorAttemptInventory` does not exist.

- [ ] **Step 5: Implement `Get-A11PriorAttemptInventory` and wire `Resolve-A11Worktree`**

Add the function after `Get-A11HistoricalImageInventory`. It must:

```powershell
function Get-A11PriorAttemptInventory {
    param([Parameter(Mandatory = $true)][string]$ArtifactRoot)
    $RunId = 'wave0-a11-calibration-20260828T045848083Z-b9917463'
    $ImageTag = 'vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463'
    $A11Root = [IO.Path]::Combine($ArtifactRoot, 'a11-runs')
    $RunRoot = [IO.Path]::Combine($A11Root, $RunId)
    $LeaseRoot = [IO.Path]::Combine($ArtifactRoot, 'leases')
    $ReleasedPath = [IO.Path]::Combine($LeaseRoot, "$RunId.released")
    $ReleaseRecordPath = [IO.Path]::Combine($LeaseRoot, "$RunId.release.json")

    foreach ($Path in @($A11Root, $RunRoot, $LeaseRoot, $ReleasedPath, $ReleaseRecordPath)) {
        $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "A11 prior attempt path contains a link: $Path"
        }
    }
    $Linked = @(Get-ChildItem -LiteralPath $RunRoot -Recurse -Force | Where-Object {
        $_.Attributes -band [IO.FileAttributes]::ReparsePoint
    })
    if ($Linked.Count -ne 0) { throw 'A11 prior attempt tree contains a link' }

    $Records = @(Get-ChildItem -LiteralPath $RunRoot -File -Recurse -Force |
        Sort-Object FullName | ForEach-Object {
            [ordered]@{
                path = $_.FullName.Substring($RunRoot.Length + 1).Replace('\', '/')
                size = [long]$_.Length
                sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        })
    $RunNames = @(Get-ChildItem -LiteralPath $A11Root -Directory -Force |
        Sort-Object Name -CaseSensitive | ForEach-Object Name)
    $LeaseNames = @(Get-ChildItem -LiteralPath $LeaseRoot -File -Force |
        Where-Object { $_.Name -like 'wave0-a11-*' } |
        Sort-Object Name -CaseSensitive | ForEach-Object Name)
    $ClosurePresent = @('78-failure-diagnostic.json','80-campaign-result.json','81-campaign-file-manifest.json','82-campaign-closure.json') |
        Where-Object { Test-Path -LiteralPath ([IO.Path]::Combine($RunRoot, 'audit', $_)) }

    $List = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
        'image','ls','--filter','reference=vision-active-learning-loop:wave0-a11-*',
        '--format','{{.Repository}}:{{.Tag}}'
    )
    if ($List.ExitCode -ne 0 -or $List.Stderr -cne '') { throw 'A11 prior image inventory failed' }
    $ImageTags = @($List.Stdout -split "`r?`n" | Where-Object {
        -not [string]::IsNullOrWhiteSpace($_)
    } | Sort-Object -CaseSensitive -Unique)
    $Inspect = Invoke-A11Native -FilePath 'docker' -ArgumentList @('image','inspect','--',$ImageTag)
    if ($Inspect.ExitCode -ne 0 -or $Inspect.Stderr -cne '') { throw 'A11 prior image inspect failed' }
    $Images = @($Inspect.Stdout | ConvertFrom-Json)
    if ($Images.Count -ne 1) { throw 'A11 prior image inspect count mismatch' }

    return [pscustomobject][ordered]@{
        run_names = $RunNames
        run_file_count = $Records.Count
        run_inventory_sha256 = Get-A11JsonSha256 -Value $Records -Depth 6
        historical_preservation_sha256 = (Get-FileHash -LiteralPath ([IO.Path]::Combine($RunRoot,'audit','79-historical-preservation-final.json')) -Algorithm SHA256).Hash.ToLowerInvariant()
        released_lease_sha256 = (Get-FileHash -LiteralPath $ReleasedPath -Algorithm SHA256).Hash.ToLowerInvariant()
        release_record_sha256 = (Get-FileHash -LiteralPath $ReleaseRecordPath -Algorithm SHA256).Hash.ToLowerInvariant()
        closure_paths_present = @($ClosurePresent)
        image_tags = $ImageTags
        image_id = [string]$Images[0].Id
        lease_names = $LeaseNames
        links_absent = $true
    }
}
```

In `Resolve-A11Worktree`, call the helper and emit `prior_a11_attempt = $PriorA11`; delete the old `$A11ImageTags`, `$A11LeaseDestinations`, `$ExistingDestinations`, and `existing_destinations` logic.

- [ ] **Step 6: Run Task 2 GREEN and keep staging empty**

Run all Task 2 selectors plus the complete preflight group:

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -k 'preflight or prior_attempt or active_lease or gpu_inventory'
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging changed during TDD' }
```

Expected: PASS and only the two allowlisted unstaged files are dirty.

---

### Task 3: Reject exact fresh-destination collisions before initialization

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Modify: `scripts/run_wave0_a11.ps1`

**Interfaces:**
- Consumes: `New-A11PhaseIdentity`, `Invoke-A11Native`, `Invoke-A11Campaign`
- Produces: `Test-A11PhaseDestinationsAbsent -Identities object[]` and the order `host preflight -> identities -> destination gate -> initialization`

- [ ] **Step 1: Add RED tests for identity and path collisions**

Build calibration and validation identities with fixed timestamp/nonce tokens. Parameterize collision cases over:

```python
(
    "campaign_root",
    "cache_root",
    "lease_path",
    "lease_lock_path",
    "released_path",
    "release_record_path",
)
```

For each path, create a file or directory at the exact derived destination under `tmp_path`, invoke the real helper with a stub `Invoke-A11Native` returning no image tags, and require a nonzero process with `A11 fresh runtime destination exists`.

Also clone one identity and reuse each distinct field:

```python
@pytest.mark.parametrize(
    "field", ["run_id", "image_tag", "campaign_root", "cache_root", "lease_id", "lease_path"]
)
def test_phase_destination_gate_rejects_cross_phase_identity_reuse(
    tmp_path: Path, field: str
) -> None:
    calibration = {
        "phase": "calibration",
        "run_id": "wave0-a11-calibration-20260828T010101001Z-aaaaaaaa",
        "image_tag": "vision-active-learning-loop:wave0-a11-calibration-a",
        "campaign_root": str(tmp_path / "calibration"),
        "cache_root": str(tmp_path / "calibration" / "wave0" / "model_cache"),
        "lease_id": "wave0-a11-calibration-lease-20260828T010101001Z-aaaaaaaa",
        "lease_path": str(tmp_path / "calibration" / "audit" / "active-lease.json"),
        "lease_lock_path": str(tmp_path / "leases" / f"{_GPU}.json"),
    }
    validation = {
        "phase": "validation",
        "run_id": "wave0-a11-validation-20260828T010101002Z-bbbbbbbb",
        "image_tag": "vision-active-learning-loop:wave0-a11-validation-b",
        "campaign_root": str(tmp_path / "validation"),
        "cache_root": str(tmp_path / "validation" / "wave0" / "model_cache"),
        "lease_id": "wave0-a11-validation-lease-20260828T010101002Z-bbbbbbbb",
        "lease_path": str(tmp_path / "validation" / "audit" / "active-lease.json"),
        "lease_lock_path": str(tmp_path / "leases" / f"{_GPU}.json"),
    }
    validation[field] = calibration[field]
    body = f"""
function Invoke-A11Native {{
    return [pscustomobject]@{{ExitCode=0;Stdout='';Stderr=''}}
}}
$Identities = {_ps(json.dumps([calibration, validation]))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent -Identities $Identities | Out-Null
"""
    completed = _invoke_functions(
        ("Test-A11PhaseDestinationsAbsent",), body
    )
    assert completed.returncode != 0
    assert field in completed.stderr
```

Run both tests and observe FAIL because the helper is missing.

- [ ] **Step 2: Add RED image inspection tests**

Stub `Invoke-A11Native` for the two `docker image ls` calls:

```python
@pytest.mark.parametrize(
    ("exit_code", "stdout", "stderr", "accepted"),
    [
        (0, "requested-tag\n", "", False),
        (125, "", "daemon unavailable", False),
        (0, "", "warning", False),
        (0, "", "", True),
    ],
)
def test_phase_destination_gate_distinguishes_image_collision_from_docker_failure(
    tmp_path: Path,
    exit_code: int,
    stdout: str,
    stderr: str,
    accepted: bool,
) -> None:
    identities = [
        {
            "phase": phase,
            "run_id": f"wave0-a11-{phase}-20260828T01010100{index}Z-{'a' * 7}{index}",
            "image_tag": f"vision-active-learning-loop:wave0-a11-{phase}-{index}",
            "campaign_root": str(tmp_path / phase),
            "cache_root": str(tmp_path / phase / "wave0" / "model_cache"),
            "lease_id": f"wave0-a11-{phase}-lease-{index}",
            "lease_path": str(tmp_path / phase / "audit" / "active-lease.json"),
            "lease_lock_path": str(tmp_path / "leases" / f"{_GPU}.json"),
        }
        for index, phase in enumerate(("calibration", "validation"), start=1)
    ]
    body = f"""
function Invoke-A11Native {{
    return [pscustomobject]@{{
        ExitCode={exit_code};Stdout={_ps(stdout)};Stderr={_ps(stderr)}
    }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent -Identities $Identities | Out-Null
"""
    completed = _invoke_functions(
        ("Test-A11PhaseDestinationsAbsent",), body
    )
    assert (completed.returncode == 0) is accepted
    if not accepted:
        assert completed.stderr
```

The canonical absent case is exit 0, empty stdout, and empty stderr for both identities and must pass.

- [ ] **Step 3: Implement `Test-A11PhaseDestinationsAbsent`**

Add after `New-A11PhaseIdentity`:

```powershell
function Test-A11PhaseDestinationsAbsent {
    param(
        [Parameter(Mandatory = $true)]
        [ValidateCount(2, 2)]
        [object[]]$Identities
    )
    if (
        [string]$Identities[0].phase -cne 'calibration' -or
        [string]$Identities[1].phase -cne 'validation'
    ) { throw 'A11 phase destination identities are not ordered' }
    foreach ($Name in @('run_id','image_tag','campaign_root','cache_root','lease_id','lease_path')) {
        if ([string]$Identities[0].$Name -ceq [string]$Identities[1].$Name) {
            throw "A11 phase runtime identity is reused: $Name"
        }
    }
    $Timestamps = [Collections.Generic.List[string]]::new()
    $Nonces = [Collections.Generic.List[string]]::new()
    foreach ($Identity in $Identities) {
        $Match = [regex]::Match([string]$Identity.run_id, '^wave0-a11-(calibration|validation)-([0-9]{8}T[0-9]{9}Z)-([0-9a-f]{8})$')
        if (-not $Match.Success) { throw 'A11 phase run identity is malformed' }
        [void]$Timestamps.Add($Match.Groups[2].Value)
        [void]$Nonces.Add($Match.Groups[3].Value)
    }
    if ($Timestamps[0] -ceq $Timestamps[1] -or $Nonces[0] -ceq $Nonces[1]) {
        throw 'A11 phase timestamp or nonce is reused'
    }

    $CheckedPaths = [Collections.Generic.HashSet[string]]::new([StringComparer]::OrdinalIgnoreCase)
    foreach ($Identity in $Identities) {
        $LeaseRoot = [IO.Path]::GetDirectoryName([string]$Identity.lease_lock_path)
        $Paths = @(
            [string]$Identity.campaign_root,
            [string]$Identity.cache_root,
            [string]$Identity.lease_path,
            [string]$Identity.lease_lock_path,
            [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).released"),
            [IO.Path]::Combine($LeaseRoot, "$($Identity.run_id).release.json"),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'audit'),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'receipts'),
            [IO.Path]::Combine([string]$Identity.campaign_root, 'wave0', 'checkpoints')
        )
        foreach ($Path in $Paths) {
            if ($CheckedPaths.Add([IO.Path]::GetFullPath($Path)) -and (Test-Path -LiteralPath $Path)) {
                throw "A11 fresh runtime destination exists: $Path"
            }
        }
        $List = Invoke-A11Native -FilePath 'docker' -ArgumentList @(
            'image','ls','--filter',"reference=$($Identity.image_tag)",
            '--format','{{.Repository}}:{{.Tag}}'
        )
        if ($List.ExitCode -ne 0 -or $List.Stderr -cne '') {
            throw "A11 image destination inspection failed: $($Identity.image_tag)"
        }
        $Tags = @($List.Stdout -split "`r?`n" | Where-Object {
            -not [string]::IsNullOrWhiteSpace($_)
        })
        if ($Tags.Count -ne 0) { throw "A11 image tag exists: $($Identity.image_tag)" }
    }
    return $true
}
```

- [ ] **Step 4: Add RED orchestration-order and no-write tests**

Update `test_campaign_orders_both_phases_and_never_retries` to stub the new helper, append `destinations` to `$script:Events`, and require:

```python
assert events[:6] == [
    "preflight",
    "identity:calibration",
    "identity:validation",
    "destinations",
    "init:calibration",
    "build:calibration",
]
```

Add `test_campaign_destination_failure_precedes_initialization_and_writes_nothing`: the destination stub throws, the initialization stub increments a counter, and the test requires the direct campaign invocation to fail with zero initialization calls and no created temp files.

Run both tests. Expected: the order test fails because production does not call the helper; the injected failure never occurs.

- [ ] **Step 5: Wire the destination gate and repair campaign harness stubs**

Immediately after both `New-A11PhaseIdentity` calls in `Invoke-A11Campaign`, add:

```powershell
Test-A11PhaseDestinationsAbsent -Identities @($Calibration, $Validation) | Out-Null
```

In every existing test body that extracts real `Invoke-A11Campaign`, add this default stub unless the test is specifically exercising the helper:

```powershell
function Test-A11PhaseDestinationsAbsent { return $true }
```

Update the required-functions source assertion to require exactly one definition of `Get-A11PriorAttemptInventory` and `Test-A11PhaseDestinationsAbsent`.

- [ ] **Step 6: Run Task 3 GREEN and pipeline regressions**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py -k 'destination or campaign_orders or campaign_suppresses or calibration_failure or stage_failure or closure_write'
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
```

Expected: PASS; staging remains empty.

---

### Task 4: Accept only a verified existing campaign parent

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Modify: `scripts/run_wave0_a11.ps1`

**Interfaces:**
- Consumes: `Initialize-A11Phase`, `Write-A11NewText`, `Get-A11FileRecord`, `ConvertTo-A11GpuRows`
- Produces: existing-parent-safe calibration initialization with unchanged child no-clobber behavior

- [ ] **Step 1: Add the RED preserved-parent initialization test**

Create `tmp_path/a11-runs/prior/sentinel.bin` with fixed bytes, then construct a calibration identity whose campaign root is a different child. In the PowerShell body, stub `nvidia-smi` so the GPU inventory returns the registered RTX 4090 and the compute inventory is empty. Invoke the real `Initialize-A11Phase` and require:

```python
assert completed.returncode == 0, completed.stderr
assert sentinel.read_bytes() == b"immutable-prior"
assert new_root.is_dir()
assert sorted(path.name for path in new_root.iterdir()) == ["audit", "wave0"]
assert not peer_root.exists()
```

Run the selector. Expected: FAIL because calibration initialization attempts to recreate the existing `a11-runs` parent.

- [ ] **Step 2: Add RED linked/non-directory parent tests**

Parameterize `parent_kind` over `file` and `junction`. Invoke the same real function and require a nonzero result containing `campaign parent is not a non-link directory`. The junction target and link exist only below `tmp_path`.

- [ ] **Step 3: Implement existing-parent-safe initialization**

Replace the parent branch at the beginning of `Initialize-A11Phase` with:

```powershell
$CampaignParent = [IO.Path]::GetDirectoryName([string]$Identity.campaign_root)
if (Test-Path -LiteralPath $CampaignParent) {
    $ParentItem = Get-Item -LiteralPath $CampaignParent -Force -ErrorAction Stop
    if (-not $ParentItem.PSIsContainer -or ($ParentItem.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
        throw 'A11 campaign parent is not a non-link directory'
    }
} elseif ($Identity.phase -ceq 'calibration') {
    New-Item -ItemType Directory -Path $CampaignParent -ErrorAction Stop | Out-Null
} else {
    throw 'A11 validation campaign parent is missing'
}
```

Keep the next `New-Item -ItemType Directory -Path $Identity.campaign_root` unchanged so an exact child collision still fails.

- [ ] **Step 4: Add and run child no-clobber GREEN**

Pre-create the exact new campaign child with a sentinel, invoke initialization, require a nonzero result, and verify the sentinel bytes are unchanged. Then run:

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py -k 'parent or initialize or no_clobber'
```

Expected: all initialization and existing no-clobber tests pass.

- [ ] **Step 5: Run the complete launcher module before review**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Expected: PASS; staging empty and only the two implementation files dirty.

---

### Task 5: Verify, review, preserve, and create the single implementation commit

**Files:**
- Stage and commit only: `scripts/run_wave0_a11.ps1`
- Stage and commit only: `tests/gates/test_wave0_a11_launcher.py`
- Historical and prior-attempt evidence: read-only

**Interfaces:**
- Consumes: Tasks 1–4 and the immutable entry transcript
- Produces: one reviewed, clean implementation commit; no runtime attempt

- [ ] **Step 1: Run focused and complete CPU tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider
```

- [ ] **Step 2: Run static and parser gates**

Use the project Python 3.12 environment for Black to avoid the known cached Black/Python 3.14 incompatibility:

```powershell
uvx --offline --python .venv\Scripts\python.exe black --check tests/gates/test_wave0_a11_launcher.py
uvx --offline --python .venv\Scripts\python.exe ruff check tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
```

Parse `scripts/run_wave0_a11.ps1` with `[Management.Automation.Language.Parser]::ParseFile` under both `pwsh -NoProfile -NonInteractive` and `powershell -NoProfile -NonInteractive`; require both error arrays empty.

- [ ] **Step 3: Review exact scope and contracts**

Require staging empty and the union of tracked/untracked candidate paths exactly equal the two-file implementation allowlist. Review this design, the launcher failure-recovery design, and Section 5.2.15 line by line. Require Critical=0 and Important=0, specifically checking:

- prior A11 evidence has a closed key set and exact registered values;
- prior tree and lease paths reject links and root drift;
- historical A2–A10 evidence remains independent and exact;
- unknown prior runs, images, or lease records fail closed;
- exact new filesystem, image-tag, and lease destinations are absent before initialization;
- Docker inspection failure is not treated as tag absence;
- identities precede only the read-only destination gate, not runtime writes;
- existing non-link parent is accepted while new child remains no-clobber;
- all preflight/destination failures precede initialization and create no evidence;
- no changed cohort, metric, threshold, ceiling, schema, model, stream, retry, closure, or Wave 1 behavior exists.

For each Critical or Important finding, first add a focused failing test and observe RED, then make the minimal two-file correction and observe GREEN. Repeat every affected full gate.

- [ ] **Step 4: Repeat the full read-only preservation gate**

Repeat Task 1 Step 2 with the identical algorithms. Require every count and digest to equal the entry transcript, the exact one-item A11 run/image inventories, the two-item prior A11 lease inventory, four absent closure paths, no active lease/container, and no new run/image/cache/receipt/checkpoint/audit/authorization identity. Require the canonical worktree clean and the linked worktree dirty only at the two allowlisted paths.

- [ ] **Step 5: Create one append-only implementation commit**

Only after every gate passes:

```powershell
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git add -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
$Staged = @(git diff --cached --name-only)
$Allowed = @('scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')
if ($Staged.Count -ne 2 -or @($Staged | Where-Object { $_ -cnotin $Allowed }).Count -ne 0) {
    throw 'staged scope mismatch'
}
git diff --cached --check
git commit -m 'fix: admit preserved A11 attempt baseline'
```

- [ ] **Step 6: Verify the committed candidate and stop before runtime**

Require the implementation commit's direct parent to be this plan commit; exact author/committer identity; exact two-file diff; and both worktrees clean. Repeat the PowerShell 7/5.1 parsers and complete launcher module from the committed tree.

Report design, plan, and implementation SHAs; RED/GREEN evidence; focused/complete test counts; static/parser results; failed-run/historical/image/lease preservation evidence; and Critical=0/Important=0 review.

Do not invoke `scripts/run_wave0_a11.ps1`. Do not reuse or replace `OWNER-A11-RUNTIME-20260828-01`. The later runtime review must name the final candidate and provide a new explicit `OwnerAuthorizationId` before one fresh launcher invocation may begin.
