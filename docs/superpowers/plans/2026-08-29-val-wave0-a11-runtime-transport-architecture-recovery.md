# Wave 0 A11 Runtime-Transport Architecture Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `subagent-driven-development` or `executing-plans` to implement this plan task-by-task. Use `test-driven-development` for Tasks 2–5, `requesting-code-review` in Task 6, and `verification-before-completion` before the implementation commit and diagnostic terminal. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the cardinality-specific A11 preservation code with a source-controlled five-attempt registry and make locked uv dependency downloads survive only reviewed transient transport failures, without changing the runtime contract or starting a formal A11 attempt.

**Architecture:** A closed JSON Schema and tracked registry declare the immutable evidence for all five consumed attempts; one PowerShell loader validates, hashes, observes, and compares that registry generically before any write. A dependency-only Python wrapper runs either of the two frozen uv commands at most three times inside one BuildKit cache-mounted Docker `RUN`; after one implementation commit passes every repository and preservation gate, one non-exporting dependency-stage diagnostic is permitted and then execution stops.

**Tech Stack:** PowerShell 7.6.4 with Windows PowerShell 5.1 parser compatibility; Python 3.12.11; pytest 9.0.2; JSON Schema draft 2020-12; Docker Engine 29.6.1 / BuildKit; exact uv 0.8.15; Git.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-08-29-val-wave0-a11-runtime-transport-architecture-recovery-design.md` at commit `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`.
- The original plan commit is `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`; it is the direct child of the design commit and changes only this plan file.
- Erratum authority (2026-08-29): after a read-only entry review proved that placing diagnostic evidence below the artifact root would change the frozen 64,306-file historical baseline, the owner authorized proceeding under professional judgment with the proposed narrow correction. This append-only erratum moves only the diagnostic evidence root outside the artifact root; it does not relax or replace any other requirement.
- This erratum commit must be the direct child of the original plan commit and must change only this plan file.
- The implementation must be one append-only commit, the direct child of this erratum commit, changing exactly the seven paths in the file map below.
- Author and committer must both be exactly `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- Do not amend, reset, rebase, squash, stash, cherry-pick, clean historical evidence, push, merge, tag, release, or modify another repository.
- Do not invoke `scripts/run_wave0_a11.ps1`, generate or guess an `OwnerAuthorizationId`, acquire a GPU lease, initialize a model, create a calibration or validation identity, access RDD, or start Wave 1.
- `OWNER-A11-RUNTIME-20260828-01`, `steven001`, `steven002`, `steven003`, and `steven004` are consumed immutable evidence. Test owners must contain the marker `TEST`.
- The only Docker invocation permitted to execute image stages is the one dependency-only diagnostic in Task 7, after the implementation commit and all earlier gates pass. The `docker buildx build --check` parser calls in Tasks 5–6 are permitted but may not execute or export a stage. The diagnostic may be invoked once and must never be retried.
- Keep Python `3.12.11`, uv `0.8.15`, CUDA `12.6`, base digest `sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356`, every dependency version, and `uv.lock` byte-identical at SHA-256 `530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93`.
- Keep all model, receipt, statistical, threshold, replica, split, acquisition, data-firewall, lease, validation, and Wave 1 contracts unchanged.
- Existing A11 runs, images, leases, receipts, checkpoints, and logs are read-only. Any preservation mismatch is a stop, not a repair instruction.
- CPU tests must use `PYTHONDONTWRITEBYTECODE=1` and `-p no:cacheprovider`; they may not use the network, Docker, GPU, model loading, CUDA, or the external artifact root.
- The diagnostic is not a formal A11 attempt. It has no owner ID, run ID, image export, project container, model process, or statistical meaning.

## Frozen preservation envelope

The five current records are:

| Ordinal | State | Calibration run | Peer validation run | Owner | Source | Files | Directories | Run inventory SHA-256 |
| ---: | --- | --- | --- | --- | --- | ---: | ---: | --- |
| 1 | `launcher-stage-failure` | `wave0-a11-calibration-20260828T045848083Z-b9917463` | `wave0-a11-validation-20260828T045848091Z-084431a4` | `OWNER-A11-RUNTIME-20260828-01` | `2622e402e4f536b94326ac34f9b20c90b513002b` | 48 | 18 | `fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b` |
| 2 | `image-build-timeout` | `wave0-a11-calibration-20260828T114911289Z-fe8b7000` | `wave0-a11-validation-20260828T114911296Z-3107aff0` | `steven001` | `1445a90b799b6306d6c1f7abc94b4a201afe5dc6` | 5 | 5 | `8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b` |
| 3 | `foundation-stream-contract-failure` | `wave0-a11-calibration-20260828T172921151Z-a0f55fa1` | `wave0-a11-validation-20260828T172921161Z-70928997` | `steven002` | `ff5cfac5820415662e608886f1a10d7892f3ee00` | 60 | 18 | `628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2` |
| 4 | `aggregate-cache-inventory-contract-failure` | `wave0-a11-calibration-20260829T050706309Z-f5a0129e` | `wave0-a11-validation-20260829T050706319Z-c6652f48` | `steven003` | `77f8eecb3b8c0f471a4e980269187ac02a3b9ebc` | 137 | 30 | `f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717` |
| 5 | `dependency-transport-build-failure` | `wave0-a11-calibration-20260829T123151657Z-bf516632` | `wave0-a11-validation-20260829T123151664Z-7af53ca8` | `steven004` | `ed6f157c7cbd545895b9d047f6e094968a1f9d94` | 10 | 5 | `b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448` |

All records bind specification `b59b0d4407b98b460f6166ea7288ba6021dc7a78` and original A11 plan `7dbd3a7576ea76beccfc64f748c4e495259ea89b`. The actual image envelope contains only the calibration images for ordinals 1, 3, and 4. The actual lease envelope contains only the `.released` and `.release.json` pairs for ordinals 1, 3, and 4. There are no validation roots, active leases, or project containers.

The historical non-A11 baseline is exactly 64,306 files with SHA-256 `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95`; its 21-image inventory SHA-256 is `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.

The three exact published images are:

| Ordinal | Tag | Image ID |
| ---: | --- | --- |
| 1 | `vision-active-learning-loop:wave0-a11-calibration-2622e402e4f5-20260828T045848083Z-b9917463` | `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5` |
| 3 | `vision-active-learning-loop:wave0-a11-calibration-ff5cfac58204-20260828T172921151Z-a0f55fa1` | `sha256:0a92de665d56dc4c4dc859cc3723444cb4b6c06e04308ee574f93befd4da7efd` |
| 4 | `vision-active-learning-loop:wave0-a11-calibration-77f8eecb3b8c-20260829T050706309Z-f5a0129e` | `sha256:94c7d9fd58debdb3cf39ee3e593b8b20dc3b2603da85cbacbf88f8492e1fdf7e` |

Their release-record/released-lease SHA-256 pairs are respectively:

```text
ordinal 1  35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060 / 146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322
ordinal 3  72e83702c440007a91a01c06e7b0231f6fcc565cc500ff4662735b904c823f93 / a9c1cbf68c88c0b3e6fa7d1f9815d5cb31bc6da40876546d6d2b08793334301f
ordinal 4  aefe15f2369bc1f186d090658f249e720319d982b2e11efb693a14c264ef84d1 / b7f51ddc665be97ce9b972daa3c0018289168d30788646ea40d836b6c3e4243c
```

## Implementation file map and allowlist

- Create `configs/a11/preserved-attempts.json`: declarative, ordered evidence for the five immutable attempts; never written by the launcher.
- Create `schemas/a11-preserved-attempts.schema.json`: closed draft-2020-12 schema, including state-specific presence/absence rules.
- Create `scripts/run_uv_sync_with_retries.py`: dependency-build-only uv transport wrapper with a fixed command set, retry classifier, process limit, logging, and backoff.
- Modify `scripts/run_wave0_a11.ps1`: generic registry loader/observer/verifier, registry digest binding, identity audit binding, and unchanged single Docker build path.
- Modify `docker/wave0.Dockerfile`: named dependency stage, exact wrapper calls, and locked BuildKit uv cache mount.
- Modify `tests/gates/test_wave0_a11_launcher.py`: registry/schema/launcher/Dockerfile TDD and five-attempt adversarial coverage.
- Create `tests/scripts/test_run_uv_sync_with_retries.py`: isolated wrapper TDD with injected subprocess, sleep, environment, and binary streams.

No other tracked path may change. In particular, do not edit `pyproject.toml`, `uv.lock`, `configs/environment/wave0-lock.json`, receipt schemas, `src/`, statistical code, or model code.

---

### Task 1: Re-freeze lineage, preservation, and the no-diagnostic entry state

**Files:**
- Modify: none
- Read: Git topology, Docker/GPU state, all five A11 run roots, image and lease inventories, approved design

**Interfaces:**
- Consumes: design commit `db047dcb8ad602fc4ac316a743ab4ddec3168cd5`
- Produces: a captured read-only entry report used as the comparison baseline in Tasks 6 and 7

- [ ] **Step 1: Prove the plan lineage and exact commit scope**

Run from the linked worktree:

```powershell
$Design = 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5'
$PlanPath = 'docs/superpowers/plans/2026-08-29-val-wave0-a11-runtime-transport-architecture-recovery.md'
$OriginalPlan = 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350'
$Erratum = (git rev-parse HEAD).Trim()
if ((git rev-parse "$Erratum^").Trim() -cne $OriginalPlan) { throw 'erratum parent mismatch' }
if ((git rev-parse "$OriginalPlan^").Trim() -cne $Design) { throw 'original plan parent mismatch' }
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') {
    throw 'branch mismatch'
}
foreach ($Commit in @($OriginalPlan, $Erratum)) {
    $Paths = @(git diff-tree --no-commit-id --name-only -r $Commit)
    if ($Paths.Count -ne 1 -or $Paths[0] -cne $PlanPath) { throw 'plan/erratum scope mismatch' }
    $Identity = @(git show -s --format='%an <%ae>|%cn <%ce>' $Commit)
    if ($Identity.Count -ne 1 -or $Identity[0] -cne (
        'kuotunyu <61350295+kuotunyu@users.noreply.github.com>|' +
        'kuotunyu <61350295+kuotunyu@users.noreply.github.com>'
    )) { throw 'plan/erratum identity mismatch' }
}
$Canonical = '<repo>'
if (@(git status --porcelain=v1).Count -ne 0) { throw 'linked worktree dirty' }
if (@(git -C $Canonical status --porcelain=v1).Count -ne 0) {
    throw 'canonical worktree dirty'
}
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }
git worktree list --porcelain
```

Require the linked worktree to have a distinct Git directory but the same common Git directory as the canonical worktree. Stop without reset, stash, checkout, cleanup, or file deletion on any mismatch.

- [ ] **Step 2: Rehash every run with the production inventory convention**

Use this read-only function and the exact expectation map:

```powershell
function Get-RunInventory {
    param([Parameter(Mandatory=$true)][string]$Path)
    $Root = [IO.Path]::GetFullPath($Path)
    $Records = @(
        Get-ChildItem -LiteralPath $Root -File -Recurse -Force |
            ForEach-Object {
                [pscustomobject][ordered]@{
                    path = $_.FullName.Substring($Root.Length + 1).Replace('\', '/')
                    size = [long]$_.Length
                    sha256 = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
                }
            } | Sort-Object path -CaseSensitive
    )
    $Json = $Records | ConvertTo-Json -Depth 8 -Compress
    $Hash = [Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes($Json))
    [pscustomobject]@{
        files = $Records.Count
        directories = @(Get-ChildItem -LiteralPath $Root -Directory -Recurse -Force).Count
        sha256 = [Convert]::ToHexString($Hash).ToLowerInvariant()
        latest_write_utc = (@(Get-ChildItem -LiteralPath $Root -File -Recurse -Force) |
            Sort-Object LastWriteTimeUtc | Select-Object -Last 1).LastWriteTimeUtc.ToString('o')
        links = @(Get-ChildItem -LiteralPath $Root -Recurse -Force |
            Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count
    }
}

$ArtifactRoot = 'D:\vision-active-learning-loop-artifacts\wave0'
$Expected = [ordered]@{
    'wave0-a11-calibration-20260828T045848083Z-b9917463' = @(48,18,'fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b','2026-08-28T06:06:15.8277603Z')
    'wave0-a11-calibration-20260828T114911289Z-fe8b7000' = @(5,5,'8e3a1a880d2724819739ab6c793825c51358bf4433667b1b85e02f5203d0f62b','2026-08-28T12:17:12.8122776Z')
    'wave0-a11-calibration-20260828T172921151Z-a0f55fa1' = @(60,18,'628a33f5e57da99647d2f19baf6a2f1fc0556999c704be3c71087fa2b2b8c7e2','2026-08-28T18:10:34.6753199Z')
    'wave0-a11-calibration-20260829T050706309Z-f5a0129e' = @(137,30,'f426e5ffd6f0d872539d581d5d3f01167e017606fb86c8f2afe999175df5c717','2026-08-29T06:13:25.1659510Z')
    'wave0-a11-calibration-20260829T123151657Z-bf516632' = @(10,5,'b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448','2026-08-29T13:39:47.0148945Z')
}
$ObservedNames = @(Get-ChildItem -LiteralPath "$ArtifactRoot\a11-runs" -Directory -Force |
    Sort-Object Name -CaseSensitive | ForEach-Object Name)
if (($ObservedNames | ConvertTo-Json -Compress) -cne
    (@($Expected.Keys) | ConvertTo-Json -Compress)) { throw 'A11 run envelope mismatch' }
foreach ($Name in $Expected.Keys) {
    $Observed = Get-RunInventory "$ArtifactRoot\a11-runs\$Name"
    $Value = $Expected[$Name]
    if ($Observed.files -ne $Value[0] -or $Observed.directories -ne $Value[1] -or
        $Observed.sha256 -cne $Value[2] -or $Observed.latest_write_utc -cne $Value[3] -or
        $Observed.links -ne 0) { throw "preserved run mismatch: $Name" }
}
```

Require the fifth run's exact five directories and ten file records from the approved design, not merely its aggregate digest.

- [ ] **Step 3: Prove the complete external envelope is unchanged and idle**

Read and compare the exact three image tags/IDs and six lease file hashes already frozen in the design and earlier recovery plans. Require:

```text
five calibration run roots
zero validation run roots
three A11 image tags
six A11 lease-history files
zero active GPU lease files
zero vision-active-learning-loop containers in any state
zero numeric CUDA compute processes
64,306 historical files / e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95
21 historical images / 9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f
```

Allowed commands are `docker info`, `docker ps --all`, `docker inspect`, `docker image inspect`, `docker image ls`, `nvidia-smi`, `Get-ChildItem`, `Get-Item`, `Get-FileHash`, and Git reads. Do not call Docker build/run/prune or the launcher. Require that `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics` contains no identity record whose `source_commit` equals the future implementation commit; at this stage the implementation commit does not exist.

---

### Task 2: Add RED registry, schema, and generic-verifier tests

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: the five frozen records and existing `_invoke_functions(...)` PowerShell AST test adapter
- Produces: the required PowerShell interfaces `Read-A11PreservedAttemptRegistry`, `Assert-A11PreservedAttemptRegistryUnchanged`, and the generic form of `Get-A11PriorAttemptInventory`

- [ ] **Step 1: Add exact file and fifth-attempt fixtures**

Add these paths and identity constants beside the existing launcher constants:

```python
_REGISTRY = _ROOT / "configs" / "a11" / "preserved-attempts.json"
_REGISTRY_SCHEMA = _ROOT / "schemas" / "a11-preserved-attempts.schema.json"
_TRANSPORT_RUN_ID = "wave0-a11-calibration-20260829T123151657Z-bf516632"
_TRANSPORT_VALIDATION_ID = "wave0-a11-validation-20260829T123151664Z-7af53ca8"
_TRANSPORT_OWNER = "steven004"
_TRANSPORT_SOURCE = "ed6f157c7cbd545895b9d047f6e094968a1f9d94"
_TRANSPORT_RUN_SHA256 = (
    "b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448"
)
_TRANSPORT_LATEST_WRITE = "2026-08-29T13:39:47.0148945Z"
```

Copy the ten fifth-attempt file records and five directory names exactly from the approved design into `_TRANSPORT_KEY_FILES` and `_TRANSPORT_DIRECTORIES`. Extend the pure `_prior_attempts()` fixture to five ordered attempts and consumed owners; do not read the external artifact root in tests.

- [ ] **Step 2: Specify the production registry loader with RED tests**

Add tests with these exact assertions:

```python
def test_preserved_attempt_registry_is_closed_valid_and_exactly_five() -> None:
    registry = json.loads(_REGISTRY.read_text(encoding="utf-8"))
    assert registry["schema_version"] == 1
    assert [item["ordinal"] for item in registry["attempts"]] == [1, 2, 3, 4, 5]
    assert [item["owner_authorization_id"] for item in registry["attempts"]] == [
        _FAILED_OWNER,
        _TIMEOUT_OWNER,
        _STREAM_OWNER,
        _AGGREGATE_OWNER,
        _TRANSPORT_OWNER,
    ]
    completed = subprocess.run(
        [
            "pwsh", "-NoProfile", "-NonInteractive", "-Command",
            "$raw=Get-Content -Raw -LiteralPath $args[0]; "
            "if(-not($raw | Test-Json -SchemaFile $args[1])){exit 2}",
            str(_REGISTRY), str(_REGISTRY_SCHEMA),
        ],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
```

Add AST-adapter tests proving `Read-A11PreservedAttemptRegistry`:

- accepts only schema version 1 and the exact sorted property sets;
- returns the exact file SHA-256 and parsed attempts together;
- rejects a missing schema/registry, malformed JSON, schema failure, unknown field, explicit `null`, duplicate/unordered ordinal, duplicate owner/current/peer/image/destination, path escape, rooted registry path, and unknown state;
- never writes either input file; and
- makes no Docker, GPU, network, artifact-root, or owner-ID allocation call.

- [ ] **Step 3: Specify generic observed-versus-expected verification**

Refactor the synthetic filesystem builder to create five attempts from one list and add mutation cases for every fifth-attempt scalar, directory, file record, absence flag, current/peer identity, and destination. Add tests that require:

```python
assert observed["run_names"] == [item["run_id"] for item in registry["attempts"]]
assert observed["registry_sha256"] == hashlib.sha256(_REGISTRY.read_bytes()).hexdigest()
assert len(observed["attempts"]) == 5
assert all(item["links_absent"] is True for item in observed["attempts"])
```

Parameterize rejection of an extra or missing run, image, lease, owner, destination, key file, directory, replica directory, checkpoint, closure, success receipt, validation root, release record, and link/reparse point. Prove all five consumed owners fail reuse while `OWNER-A11-TEST-FRESH` passes the pure read-only gate.

- [ ] **Step 4: Specify registry digest stability and identity binding**

Add tests that load a copied registry, change one byte after load, and require `Assert-A11PreservedAttemptRegistryUnchanged` to fail before a stubbed `Initialize-A11Phase` can write. Add a positive test proving both preregistered phase identities carry the same lowercase 64-hex `preserved_attempt_registry_sha256` and that `audit/00-identity.json` contains it.

- [ ] **Step 5: Run focused RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'preserved_attempt_registry or prior_attempt or preflight or destination or identity_binding'
```

Require failures caused by the absent registry/schema/functions and current four-attempt hard-coding. A syntax error, external artifact access, or Docker invocation is not acceptable RED.

---

### Task 3: Implement the registry and generic fail-closed launcher verifier

**Files:**
- Create: `configs/a11/preserved-attempts.json`
- Create: `schemas/a11-preserved-attempts.schema.json`
- Modify: `scripts/run_wave0_a11.ps1`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: `Read-A11PreservedAttemptRegistry -ArtifactRoot <absolute> [-RegistryPath <absolute>] [-SchemaPath <absolute>]`
- Produces: `{schema_version, registry_path, registry_sha256, attempts}` plus derived `{run_names, image_tags, lease_names, authorization_evidence, links_absent}`; `Assert-A11PreservedAttemptRegistryUnchanged -Registry <object>` returns `$true` or throws

- [ ] **Step 1: Create the closed schema**

Use draft 2020-12, `additionalProperties: false` at every object level, and these reusable definitions:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "a11-preserved-attempts.schema.json",
  "type": "object",
  "additionalProperties": false,
  "required": ["schema_version", "attempts"],
  "properties": {
    "schema_version": {"const": 1},
    "attempts": {
      "type": "array",
      "minItems": 1,
      "items": {"$ref": "#/$defs/attempt"}
    }
  },
  "$defs": {
    "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
    "commit": {"type": "string", "pattern": "^[0-9a-f]{40}$"},
    "run_id": {"type": "string", "pattern": "^wave0-a11-(calibration|validation)-[0-9]{8}T[0-9]{9}Z-[0-9a-f]{8}$"},
    "image_id": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
    "image_tag": {"type": "string", "pattern": "^vision-active-learning-loop:wave0-a11-(calibration|validation)-[^\\r\\n]+$"},
    "relative_path": {"type": "string", "pattern": "^(?![A-Za-z]:)(?!/)(?!.*(?:^|/)\\.\\.(?:/|$))[^\\\\\\r\\n]+$"},
    "file_record": {
      "type": "object",
      "additionalProperties": false,
      "required": ["path", "size", "sha256"],
      "properties": {
        "path": {"$ref": "#/$defs/relative_path"},
        "size": {"type": "integer", "minimum": 0},
        "sha256": {"$ref": "#/$defs/sha256"}
      }
    },
    "image": {
      "type": "object",
      "additionalProperties": false,
      "required": ["tag", "id"],
      "properties": {
        "tag": {"$ref": "#/$defs/image_tag"},
        "id": {"$ref": "#/$defs/image_id"}
      }
    },
    "release": {
      "type": "object",
      "additionalProperties": false,
      "required": ["record_path", "record_sha256", "released_path", "released_sha256"],
      "properties": {
        "record_path": {"$ref": "#/$defs/relative_path"},
        "record_sha256": {"$ref": "#/$defs/sha256"},
        "released_path": {"$ref": "#/$defs/relative_path"},
        "released_sha256": {"$ref": "#/$defs/sha256"}
      }
    },
    "attempt": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "ordinal", "state", "run_id", "peer_run_id", "source_commit",
        "specification_commit", "plan_commit", "owner_authorization_id",
        "registered_run_ids", "registered_image_tags", "registered_destinations",
        "run_file_count", "run_directory_count", "run_inventory_sha256",
        "directory_names", "key_file_records", "replica_directory_names_present",
        "checkpoint_file_paths_present", "closure_paths_present",
        "success_receipt_present", "validation_present",
        "latest_write_utc", "links_absent"
      ],
      "properties": {
        "ordinal": {"type": "integer", "minimum": 1},
        "state": {
          "enum": [
            "launcher-stage-failure",
            "image-build-timeout",
            "foundation-stream-contract-failure",
            "aggregate-cache-inventory-contract-failure",
            "dependency-transport-build-failure"
          ]
        },
        "run_id": {"$ref": "#/$defs/run_id"},
        "peer_run_id": {"$ref": "#/$defs/run_id"},
        "source_commit": {"$ref": "#/$defs/commit"},
        "specification_commit": {"const": "b59b0d4407b98b460f6166ea7288ba6021dc7a78"},
        "plan_commit": {"const": "7dbd3a7576ea76beccfc64f748c4e495259ea89b"},
        "owner_authorization_id": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._:-]{2,127}$"},
        "registered_run_ids": {
          "type": "array", "minItems": 2, "maxItems": 2, "uniqueItems": true,
          "items": {"$ref": "#/$defs/run_id"}
        },
        "registered_image_tags": {
          "type": "array", "minItems": 2, "maxItems": 2, "uniqueItems": true,
          "items": {"$ref": "#/$defs/image_tag"}
        },
        "registered_destinations": {
          "type": "array", "minItems": 16, "maxItems": 16, "uniqueItems": true,
          "items": {"$ref": "#/$defs/relative_path"}
        },
        "run_file_count": {"type": "integer", "minimum": 1},
        "run_directory_count": {"type": "integer", "minimum": 1},
        "run_inventory_sha256": {"$ref": "#/$defs/sha256"},
        "directory_names": {
          "type": "array", "minItems": 1, "uniqueItems": true,
          "items": {"$ref": "#/$defs/relative_path"}
        },
        "key_file_records": {
          "type": "array", "minItems": 1, "uniqueItems": true,
          "items": {"$ref": "#/$defs/file_record"}
        },
        "replica_directory_names_present": {
          "type": "array", "uniqueItems": true,
          "items": {"$ref": "#/$defs/relative_path"}
        },
        "checkpoint_file_paths_present": {
          "type": "array", "uniqueItems": true,
          "items": {"$ref": "#/$defs/relative_path"}
        },
        "closure_paths_present": {
          "type": "array", "uniqueItems": true,
          "items": {"$ref": "#/$defs/relative_path"}
        },
        "success_receipt_present": {"const": false},
        "validation_present": {"const": false},
        "latest_write_utc": {"type": "string", "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9:.]+Z$"},
        "links_absent": {"const": true},
        "image": {"$ref": "#/$defs/image"},
        "release": {"$ref": "#/$defs/release"}
      },
      "allOf": [
        {
          "if": {
            "properties": {
              "state": {
                "enum": [
                  "launcher-stage-failure",
                  "foundation-stream-contract-failure",
                  "aggregate-cache-inventory-contract-failure"
                ]
              }
            },
            "required": ["state"]
          },
          "then": {"required": ["image", "release"]},
          "else": {
            "not": {
              "anyOf": [
                {"required": ["image"]},
                {"required": ["release"]}
              ]
            }
          }
        }
      ]
    }
  }
}
```

The schema above is the exact structural contract. States with published image
and release evidence require those two objects; the two build-time failures
forbid both. Ordered arrays remain order-sensitive in the production comparer.

```text
ordinal
state
run_id
peer_run_id
source_commit
specification_commit
plan_commit
owner_authorization_id
registered_run_ids
registered_image_tags
registered_destinations
run_file_count
run_directory_count
run_inventory_sha256
directory_names
key_file_records
replica_directory_names_present
checkpoint_file_paths_present
closure_paths_present
success_receipt_present
validation_present
latest_write_utc
links_absent
optional image = {tag, id}
optional release = {record_path, record_sha256, released_path, released_sha256}
```

The schema state enum is exactly the five states in the frozen table. `specification_commit` is constant `b59b0d4407b98b460f6166ea7288ba6021dc7a78`; `plan_commit` is constant `7dbd3a7576ea76beccfc64f748c4e495259ea89b`; `success_receipt_present`, `validation_present`, and `links_absent` are respectively constant `false`, `false`, and `true` for this registry revision.

- [ ] **Step 2: Create the exact five-record registry**

Use two-space UTF-8 JSON with LF endings and a final newline. For every record:

```json
{
  "ordinal": 5,
  "state": "dependency-transport-build-failure",
  "run_id": "wave0-a11-calibration-20260829T123151657Z-bf516632",
  "peer_run_id": "wave0-a11-validation-20260829T123151664Z-7af53ca8",
  "source_commit": "ed6f157c7cbd545895b9d047f6e094968a1f9d94",
  "specification_commit": "b59b0d4407b98b460f6166ea7288ba6021dc7a78",
  "plan_commit": "7dbd3a7576ea76beccfc64f748c4e495259ea89b",
  "owner_authorization_id": "steven004",
  "registered_run_ids": [
    "wave0-a11-calibration-20260829T123151657Z-bf516632",
    "wave0-a11-validation-20260829T123151664Z-7af53ca8"
  ],
  "registered_image_tags": [
    "vision-active-learning-loop:wave0-a11-calibration-ed6f157c7cbd-20260829T123151657Z-bf516632",
    "vision-active-learning-loop:wave0-a11-validation-ed6f157c7cbd-20260829T123151664Z-7af53ca8"
  ],
  "registered_destinations": [
    "a11-runs/wave0-a11-calibration-20260829T123151657Z-bf516632",
    "a11-runs/wave0-a11-calibration-20260829T123151657Z-bf516632/wave0/model_cache",
    "a11-runs/wave0-a11-calibration-20260829T123151657Z-bf516632/audit/active-lease.json",
    "leases/wave0-a11-calibration-20260829T123151657Z-bf516632.released",
    "leases/wave0-a11-calibration-20260829T123151657Z-bf516632.release.json",
    "a11-runs/wave0-a11-calibration-20260829T123151657Z-bf516632/audit",
    "a11-runs/wave0-a11-calibration-20260829T123151657Z-bf516632/wave0/receipts",
    "a11-runs/wave0-a11-calibration-20260829T123151657Z-bf516632/wave0/checkpoints",
    "a11-runs/wave0-a11-validation-20260829T123151664Z-7af53ca8",
    "a11-runs/wave0-a11-validation-20260829T123151664Z-7af53ca8/wave0/model_cache",
    "a11-runs/wave0-a11-validation-20260829T123151664Z-7af53ca8/audit/active-lease.json",
    "leases/wave0-a11-validation-20260829T123151664Z-7af53ca8.released",
    "leases/wave0-a11-validation-20260829T123151664Z-7af53ca8.release.json",
    "a11-runs/wave0-a11-validation-20260829T123151664Z-7af53ca8/audit",
    "a11-runs/wave0-a11-validation-20260829T123151664Z-7af53ca8/wave0/receipts",
    "a11-runs/wave0-a11-validation-20260829T123151664Z-7af53ca8/wave0/checkpoints"
  ],
  "run_file_count": 10,
  "run_directory_count": 5,
  "run_inventory_sha256": "b4c8948a1909b585a4b104d0623bfec6dd8075311bcf87a00a17a35afd506448",
  "directory_names": ["audit", "wave0", "wave0/checkpoints", "wave0/model_cache", "wave0/receipts"],
  "key_file_records": [
    {"path": "audit/00-identity.json", "size": 2873, "sha256": "9fb7f3572e8341af986f24473c2ee66933d17d736b632b95e0c3a64c91e9d67d"},
    {"path": "audit/01-gpu-preflight.json", "size": 125, "sha256": "de80ae6951e9b941a2777c38d2872b093aa7a83bdd84aabfb99e248e555e2bb7"},
    {"path": "audit/10-build.json", "size": 1234, "sha256": "3ef76de20f776e977f172d2ba9c3277185db693bd3a7fc9949bfe42b39af6f68"},
    {"path": "audit/10-build.stderr.log", "size": 865248, "sha256": "e53b9598c39343785aea27be4381f1755accb5f91553630af64d1b71712e82c5"},
    {"path": "audit/10-build.stdout.log", "size": 0, "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"},
    {"path": "audit/78-failure-diagnostic.json", "size": 766, "sha256": "cc0e391fdb743dac2c2c80362d690703da08b9ae38c5a8294031ace8bef9c311"},
    {"path": "audit/79-historical-preservation-final.json", "size": 301, "sha256": "927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d"},
    {"path": "audit/80-campaign-result.json", "size": 751, "sha256": "346b4aa69f8e6c440262f463e4cbb756f39dd1dde0df51124f533093ffe8b651"},
    {"path": "audit/81-campaign-file-manifest.json", "size": 1885, "sha256": "8be8ee5adadb296d269c5dda0c1827d8ef9ee56d024872aa3ee6e0cb74bbedd6"},
    {"path": "audit/82-campaign-closure.json", "size": 659, "sha256": "a3ba8ef72165dde8443ac85ffcaaf27b307afd15af10c8a0d347ca7f30cfcaa1"}
  ],
  "replica_directory_names_present": [],
  "checkpoint_file_paths_present": [],
  "closure_paths_present": [
    "78-failure-diagnostic.json",
    "79-historical-preservation-final.json",
    "80-campaign-result.json",
    "81-campaign-file-manifest.json",
    "82-campaign-closure.json"
  ],
  "success_receipt_present": false,
  "validation_present": false,
  "latest_write_utc": "2026-08-29T13:39:47.0148945Z",
  "links_absent": true
}
```

For ordinals 1–4, build `registered_destinations` with this exact deterministic
code after assigning the record's two frozen run IDs:

```powershell
$RegisteredDestinations = foreach ($RegisteredId in $RegisteredRunIds) {
    "a11-runs/$RegisteredId"
    "a11-runs/$RegisteredId/wave0/model_cache"
    "a11-runs/$RegisteredId/audit/active-lease.json"
    "leases/$RegisteredId.released"
    "leases/$RegisteredId.release.json"
    "a11-runs/$RegisteredId/audit"
    "a11-runs/$RegisteredId/wave0/receipts"
    "a11-runs/$RegisteredId/wave0/checkpoints"
}
```

Insert `key_file_records` after `directory_names`. For ordinal 5 it is the exact
ten-record array above. For ordinals 1–4, migrate the immutable declarations
from these exact reviewed sources without computing values from the live
artifact root:

| Ordinal | Declaration source | Required migration detail |
| ---: | --- | --- |
| 1 | `docs/superpowers/specs/2026-08-28-val-wave0-a11-preserved-attempt-preflight-design.md` and the committed `$Attempt1` block | exact 18-directory list; select `audit/79-historical-preservation-final.json` as its key record; empty replica/checkpoint/closure lists |
| 2 | `_TIMEOUT_FILES` and the committed `$Attempt2` block | all five files as key records; exact five-directory list; empty replica/checkpoint/closure lists |
| 3 | `_STREAM_DIRECTORIES`, `_STREAM_KEY_FILES`, and the committed `$Attempt3` block | exact 18 directories, 15 key records, five closure names, empty replica/checkpoint lists |
| 4 | `_AGGREGATE_DIRECTORIES`, `_AGGREGATE_KEY_FILES`, and the committed `$Attempt4` block | exact 30 directories, 16 key records, twelve replica directories, twelve checkpoint files, five closure names |

Ordinal 1's exact directory list is:

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

For ordinal 1 the selected key record is exactly size 301 and SHA-256
`927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`.
Add `run_directory_count`, the common specification/plan commits, exact
latest-write timestamps from the frozen table, and empty uniform lists where
the source state has no such object. Do not change any existing hash.

- [ ] **Step 3: Implement one registry loader and digest guard**

Add these functions before `Get-A11PriorAttemptInventory`:

```powershell
function Read-A11PreservedAttemptRegistry {
    param(
        [Parameter(Mandatory=$true)][string]$ArtifactRoot,
        [string]$RegistryPath = ([IO.Path]::Combine($PSScriptRoot, '..', 'configs', 'a11', 'preserved-attempts.json')),
        [string]$SchemaPath = ([IO.Path]::Combine($PSScriptRoot, '..', 'schemas', 'a11-preserved-attempts.schema.json'))
    )
    foreach ($Path in @($RegistryPath, $SchemaPath)) {
        $Item = Get-Item -LiteralPath $Path -Force -ErrorAction Stop
        if (-not $Item.PSIsContainer -and
            -not ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) {
            continue
        }
        throw "A11 preserved-attempt input is not a regular non-link file: $Path"
    }
    $Bytes = [IO.File]::ReadAllBytes([IO.Path]::GetFullPath($RegistryPath))
    if ($Bytes.Length -ge 3 -and $Bytes[0] -eq 0xEF -and
        $Bytes[1] -eq 0xBB -and $Bytes[2] -eq 0xBF) {
        throw 'A11 preserved-attempt registry must not contain a UTF-8 BOM'
    }
    $Utf8 = [Text.UTF8Encoding]::new($false, $true)
    $Raw = $Utf8.GetString($Bytes)
    if (-not ($Raw | Test-Json -SchemaFile $SchemaPath -ErrorAction Stop)) {
        throw 'A11 preserved-attempt registry schema validation failed'
    }
    $Document = $Raw | ConvertFrom-Json -DateKind String -ErrorAction Stop
    $DigestBytes = [Security.Cryptography.SHA256]::HashData($Bytes)
    $Digest = [Convert]::ToHexString($DigestBytes).ToLowerInvariant()
    # Apply the exact property-set, ordinal, identity, and destination loops
    # specified immediately below before returning the closed result object.
}

function Assert-A11PreservedAttemptRegistryUnchanged {
    param([Parameter(Mandatory=$true)][object]$Registry)
    $Observed = (Get-FileHash -LiteralPath $Registry.registry_path -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Observed -cne [string]$Registry.registry_sha256) {
        throw 'A11 preserved-attempt registry changed after preflight'
    }
    return $true
}
```

Read with `[IO.File]::ReadAllBytes`, reject a UTF-8 BOM, decode through `UTF8Encoding($false, $true)`, and compute SHA-256 from the same byte array. Reject a registry or schema link/reparse point. Resolve each relative destination against the exact artifact root and require `GetFullPath(relative, artifact_root)` to remain below `artifact_root + DirectorySeparatorChar` with `OrdinalIgnoreCase`; reject rooted paths, `.`/`..` segments, backslashes, duplicates, and alternate spellings.

Use `ConvertFrom-Json -DateKind String` both here and when reopening closed
preflight evidence so exact seven-digit UTC timestamps never become locale- or
runtime-formatted `DateTime` objects.

The loop after parsing must compare the top-level property set to
`schema_version,attempts`; compare each attempt property set to the schema's
common set plus exactly `image,release` for the three publishing states; and
maintain separate ordinal `HashSet[string]` values for owners, current IDs,
peer IDs, image tags, and normalized destinations. Require ordinal `index + 1`,
`registered_run_ids == [run_id, peer_run_id]`, and image tags whose phase/source
prefixes match those two identities. Return only:

```powershell
[pscustomobject][ordered]@{
    schema_version = 1
    registry_path = [IO.Path]::GetFullPath($RegistryPath)
    registry_sha256 = $Digest
    attempts = @($Document.attempts)
}
```

- [ ] **Step 4: Replace the four-branch observer with a generic loop**

Change the interface to:

```powershell
function Get-A11PriorAttemptInventory {
    param(
        [Parameter(Mandatory=$true)][string]$ArtifactRoot,
        [object]$Registry = (Read-A11PreservedAttemptRegistry -ArtifactRoot $ArtifactRoot)
    )
    foreach ($Expected in @($Registry.attempts)) {
        $RunRoot = [IO.Path]::Combine($ArtifactRoot, 'a11-runs', [string]$Expected.run_id)
        $IdentityPath = [IO.Path]::Combine($RunRoot, 'audit', '00-identity.json')
        $Identity = Get-Content -Raw -LiteralPath $IdentityPath | ConvertFrom-Json
        if ([string]$Identity.current.run_id -cne [string]$Expected.run_id -or
            [string]$Identity.preregistered_peer.run_id -cne [string]$Expected.peer_run_id -or
            [string]$Identity.current.owner_authorization_id -cne
                [string]$Expected.owner_authorization_id) {
            throw "A11 preserved attempt $($Expected.ordinal) identity drifted"
        }
        # Enumerate files/directories once with normalized ordinal relative paths;
        # derive every presence set from those records; inspect image/release only
        # when their schema-bound objects exist; compare each field exactly.
    }
    # After the loop, derive and compare the complete actual versus registered
    # run/image/lease/owner/destination sets, then return the closed evidence.
}
```

Use one `StringComparer.Ordinal` ordering for relative POSIX paths and one `StringComparer.OrdinalIgnoreCase` containment/Windows destination set. A record mismatch throws a message containing its ordinal and field. Do not retain attempt-number-specific constants, `if ($Attempts.Count -eq N)` branches, or a fixed `ValidateCount(4,4)`.

Return `run_names` in registry ordinal order, `authorization_evidence` in the
same order, and `image_tags`/`lease_names` after sorting both the expected and
actual complete sets with `StringComparer.Ordinal`. This preserves the current
lexical image order `ordinal 1, ordinal 4, ordinal 3` without coupling the
verifier to that cardinality.

- [ ] **Step 5: Bind the registry digest through preflight and before write**

Return `registry_path` and `registry_sha256` inside `prior_a11_attempts`. Update the closed preflight key checks accordingly. Add `[string]$PreservedAttemptRegistrySha256` to `New-A11PhaseIdentity`, validate it with `^[0-9a-f]{64}$`, and store it as `preserved_attempt_registry_sha256` on both phase identities.

Immediately before each `Initialize-A11Phase` call, execute:

```powershell
Assert-A11PreservedAttemptRegistryUnchanged `
    -Registry $RawPreflight.prior_a11_attempts | Out-Null
```

This must occur after `Confirm-A11ProtectedGit` and before `current_stage = 'initialize'`. The digest then appears in `audit/00-identity.json` through the existing identity serialization. Keep `Test-A11PhaseDestinationsAbsent` data-driven with a manual `PriorAttempts.Count -ge 1` check and no fixed maximum.

Add mandatory `ArtifactRoot` to `Test-A11PhaseDestinationsAbsent`. Replace its
old `registered_paths` loop with `registered_destinations`; resolve each
registry-relative value by `GetFullPath(value, ArtifactRoot)` before comparing
it to the absolute candidate paths. Pass the exact preflight artifact root from
`Invoke-A11Campaign`. Tests must reject an alternate root, rooted destination,
path escape, and case-insensitive Windows alias.

- [ ] **Step 6: Run registry GREEN and the complete launcher suite**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'preserved_attempt_registry or prior_attempt or preflight or destination or identity_binding'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
```

Require both commands to pass without real Docker/GPU/artifact access. Search the launcher and require consumed owners, fixed run IDs, fixed image IDs, and attempt-specific file hashes to exist only in the registry/tests, not in executable PowerShell.

---

### Task 4: Add RED bounded uv transport-wrapper tests

**Files:**
- Create: `tests/scripts/test_run_uv_sync_with_retries.py`
- Test: `tests/scripts/test_run_uv_sync_with_retries.py`

**Interfaces:**
- Consumes: `run_uv_sync(argv, *, runner, sleeper, environ, stdout, stderr) -> int` and `main(argv: Sequence[str] | None = None) -> int`
- Produces: exact retry/cardinality/logging behavior consumed by the Dockerfile in Task 5

- [ ] **Step 1: Add isolated subprocess fixtures**

Import the script by file path so no package or `pyproject.toml` change is needed. Use `subprocess.CompletedProcess[bytes]`, `io.BytesIO`, and injected adapters:

```python
def result(code: int, stdout: bytes = b"", stderr: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    return subprocess.CompletedProcess(args=["uv"], returncode=code, stdout=stdout, stderr=stderr)

def invoke(results: list[subprocess.CompletedProcess[bytes]], argv: list[str]):
    calls: list[tuple[list[str], dict[str, str]]] = []
    sleeps: list[float] = []
    out = io.BytesIO()
    err = io.BytesIO()

    def runner(command, *, stdout, stderr, env, shell, check):
        calls.append((list(command), dict(env)))
        return results[len(calls) - 1]

    code = module.run_uv_sync(
        argv,
        runner=runner,
        sleeper=sleeps.append,
        environ={"UV_HTTP_TIMEOUT": "1", "PATH": "test"},
        stdout=out,
        stderr=err,
    )
    return code, calls, sleeps, out.getvalue(), err.getvalue()
```

- [ ] **Step 2: Specify success, retry, and exhaustion**

Parameterize every exact case-sensitive retry signature:

```python
RETRYABLE = [
    b"error decoding response body",
    b"request or response body error",
    b"error reading a body from connection",
    b"stream error received:",
    b"Failed to download distribution due to network timeout",
    b"connection reset by peer",
]
```

Require first-process success to produce one call, no sleep, marker `A11_UV_SYNC_ATTEMPT 1/3`, exact raw child stdout/stderr, and code 0. Require transport-fail/success and transport-fail/fail/success to use exactly two or three calls, sleeps `[5.0]` or `[5.0, 10.0]`, and one marker per process. Require three transport failures to return only the third exit code.

- [ ] **Step 3: Specify every fail-closed case**

Require exactly one child process and no sleep for lock drift, resolution conflict, hash mismatch, invalid wheel/ZIP, disk-full, permission, Python build, project install, capitalized/non-exact signature, stdout-only signature, and unclassified exit. Require negative child return code `-9` to return `137` without retry.

Require `main` to reject missing `--`, empty post-separator argv, any executable other than `uv`, any command outside the two frozen vectors, and pseudo-options such as `--max-attempts=4`; no child process may run for invalid input. Prove `shell=False`, `check=False`, exact argument-vector forwarding, and `UV_HTTP_TIMEOUT=300` overriding inherited values.

Use invalid UTF-8 bytes around a retry signature to prove raw bytes are preserved while the decoded classification copy uses `errors='replace'`.

- [ ] **Step 4: Run focused RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
```

Require collection to succeed and tests to fail only because `scripts/run_uv_sync_with_retries.py` is absent or lacks the specified interfaces.

---

### Task 5: Implement the wrapper and Docker dependency stage

**Files:**
- Create: `scripts/run_uv_sync_with_retries.py`
- Modify: `docker/wave0.Dockerfile`
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Test: `tests/scripts/test_run_uv_sync_with_retries.py`
- Test: `tests/gates/test_wave0_a11_launcher.py`

**Interfaces:**
- Consumes: the wrapper interfaces and exact command vectors specified by Task 4
- Produces: Docker target `a11-dependencies`; final default image stage with unchanged `ENTRYPOINT ["val"]`

- [ ] **Step 1: Implement the minimal wrapper**

Use immutable module constants and dependency injection:

```python
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (5.0, 10.0)
ALLOWED_COMMANDS = {
    ("uv", "sync", "--frozen", "--no-dev", "--no-install-project"),
    ("uv", "sync", "--frozen", "--no-dev"),
}
RETRYABLE_STDERR = (
    "error decoding response body",
    "request or response body error",
    "error reading a body from connection",
    "stream error received:",
    "Failed to download distribution due to network timeout",
    "connection reset by peer",
)
```

`run_uv_sync` copies the environment, sets `UV_HTTP_TIMEOUT` to `300`, calls `runner(list(argv), stdout=PIPE, stderr=PIPE, env=child_env, shell=False, check=False)`, re-emits complete returned byte streams, and classifies only decoded stderr. Emit attempt markers as UTF-8 bytes to parent stderr and flush both parent streams after every process. A negative return code maps to `128 + abs(returncode)` and returns immediately. `main` requires an exact leading `--`, validates one of the two allowed tuples, and returns 2 with one concise stderr line on invalid input.

- [ ] **Step 2: Run wrapper GREEN**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
```

Require all wrapper tests to pass with no subprocess beyond injected fakes.

- [ ] **Step 3: Add RED Dockerfile structure assertions**

Replace the old timeout-only Dockerfile test with assertions for exact structure:

```python
source = _DOCKERFILE.read_text(encoding="utf-8")
assert source.startswith("# syntax=docker/dockerfile:1\n")
assert source.count(" AS a11-dependencies") == 1
assert source.count("uv==0.8.15") == 1
assert source.count("UV_LINK_MODE=copy") == 1
mount = (
    "--mount=type=cache,id=val-wave0-uv-0.8.15-cu126-v1,"
    "target=/root/.cache/uv,sharing=locked"
)
assert source.count(mount) == 2
wrapper_runs = [
    chunk for chunk in source.split("RUN ")
    if "/opt/python/bin/python3.12 scripts/run_uv_sync_with_retries.py" in chunk
]
assert len(wrapper_runs) == 2
assert "uv sync --frozen --no-dev --no-install-project" in wrapper_runs[0]
assert "uv sync --frozen --no-dev" in wrapper_runs[1]
assert "--no-install-project" not in wrapper_runs[1]
assert source.count('ENTRYPOINT ["val"]') == 1
```

Also require `New-A11BuildArguments` still contains one `build`, one `--no-cache`, one `--progress plain`, the unchanged Dockerfile path, and no Docker-level loop/retry command.

- [ ] **Step 4: Refactor the Dockerfile minimally**

The final shape is:

```dockerfile
# syntax=docker/dockerfile:1
FROM nvidia/cuda@sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356 AS a11-dependencies

# Preserve the existing labels, Python build arguments, exact Python build,
# exact uv==0.8.15 install, PATH, and WORKDIR instructions byte-for-byte in behavior.
ENV UV_LINK_MODE=copy
COPY pyproject.toml uv.lock ./
COPY scripts/run_uv_sync_with_retries.py ./scripts/run_uv_sync_with_retries.py
RUN --mount=type=cache,id=val-wave0-uv-0.8.15-cu126-v1,target=/root/.cache/uv,sharing=locked \
    /opt/python/bin/python3.12 scripts/run_uv_sync_with_retries.py -- \
    uv sync --frozen --no-dev --no-install-project

FROM a11-dependencies AS final
COPY src ./src
COPY configs ./configs
RUN --mount=type=cache,id=val-wave0-uv-0.8.15-cu126-v1,target=/root/.cache/uv,sharing=locked \
    /opt/python/bin/python3.12 scripts/run_uv_sync_with_retries.py -- \
    uv sync --frozen --no-dev

ENTRYPOINT ["val"]
```

The comment in this plan is explanatory; retain the actual existing Python-build instructions in the tracked Dockerfile. Do not add a package upgrade, cache export, wheel special case, shell retry loop, cleanup of the cache mount, or second final image target.

- [ ] **Step 5: Run Dockerfile and launcher GREEN without building**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/scripts/test_run_uv_sync_with_retries.py
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py `
  -k 'dockerfile or build_arguments or campaign_orders or no_cleanup_retry'
docker buildx build --check --file docker/wave0.Dockerfile .
```

The Buildx `--check` call is a Dockerfile validation only. Require exit 0 and no image, project container, A11 run, or lease change. Do not run a target build in this step.

---

### Task 6: Verify, review, and create the one implementation commit

**Files:**
- Modify: none beyond the seven-path implementation allowlist
- Verify: all project tests, schema/parser/style/lock gates, Git scope, and immutable external evidence

**Interfaces:**
- Consumes: the complete uncommitted implementation from Tasks 2–5
- Produces: one reviewed implementation commit whose parent is this erratum commit

- [ ] **Step 1: Run focused and full CPU tests**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider `
  tests/scripts/test_run_uv_sync_with_retries.py `
  tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py `
  tests/scripts/test_run_uv_sync_with_retries.py
uv run pytest -q -p no:cacheprovider
```

Require three exit-0 runs and report exact passed/skipped counts from fresh output.

- [ ] **Step 2: Run schema, format, lint, lock, parser, Dockerfile, and whitespace gates**

```powershell
$Registry = 'configs/a11/preserved-attempts.json'
$Schema = 'schemas/a11-preserved-attempts.schema.json'
$Raw = Get-Content -Raw -LiteralPath $Registry
if (-not ($Raw | Test-Json -SchemaFile $Schema)) { throw 'registry schema invalid' }
uvx --offline black --check `
  scripts/run_uv_sync_with_retries.py `
  tests/gates/test_wave0_a11_launcher.py `
  tests/scripts/test_run_uv_sync_with_retries.py
uvx --offline ruff check `
  scripts/run_uv_sync_with_retries.py `
  tests/gates/test_wave0_a11_launcher.py `
  tests/scripts/test_run_uv_sync_with_retries.py
uv lock --check
if ((Get-FileHash -LiteralPath 'uv.lock' -Algorithm SHA256).Hash.ToLowerInvariant() -cne
  '530124ac42e2b7e83cd0e28bdd5dc7aaaca63faa72248b59fcf120653ab8ba93') {
    throw 'uv.lock changed'
}
pwsh -NoProfile -NonInteractive -Command `
  '$null=$t=$e=$null; [Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e) | Out-Null; if($e.Count){throw ($e.Message -join "; ")}'
powershell.exe -NoProfile -NonInteractive -Command `
  '$null=$t=$e=$null; [Management.Automation.Language.Parser]::ParseFile("scripts/run_wave0_a11.ps1",[ref]$t,[ref]$e) | Out-Null; if($e.Count){throw ($e.Message -join "; ")}'
docker buildx build --check --file docker/wave0.Dockerfile .
git diff --check
```

Do not substitute a real build for the `--check` command.

- [ ] **Step 3: Enforce scope and forbidden-capability gates**

Require the exact unstaged union:

```powershell
$Expected = @(
  'configs/a11/preserved-attempts.json',
  'docker/wave0.Dockerfile',
  'schemas/a11-preserved-attempts.schema.json',
  'scripts/run_uv_sync_with_retries.py',
  'scripts/run_wave0_a11.ps1',
  'tests/gates/test_wave0_a11_launcher.py',
  'tests/scripts/test_run_uv_sync_with_retries.py'
) | Sort-Object
$Observed = @(git status --porcelain=v1 | ForEach-Object { $_.Substring(3) }) | Sort-Object
if (($Observed | ConvertTo-Json -Compress) -cne ($Expected | ConvertTo-Json -Compress)) {
    throw 'implementation allowlist mismatch'
}
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging must be empty before review' }
rg -n 'steven005|OWNER-A11-RUNTIME-20260829|docker buildx build.*--target|Wave 1|wave1' `
  configs/a11 scripts/run_uv_sync_with_retries.py docker/wave0.Dockerfile
if ($LASTEXITCODE -eq 0) { throw 'forbidden capability or future owner found' }
if ($LASTEXITCODE -ne 1) { throw 'forbidden-string scan failed' }
```

The search must contain no synthesized future owner, embedded diagnostic invocation, or Wave 1 capability. The registry may contain only the five consumed owners. Require no `__pycache__`, `.pyc`, `.pytest_cache`, runtime artifact, or diagnostic directory inside the repository.

- [ ] **Step 4: Re-run the complete preservation gate**

Repeat Task 1 Steps 2–3 and compare the captured entry report byte-for-byte except for read timestamps. Require exact five-run, three-image, six-lease, zero-active-lease, zero-project-container, zero-compute-process, 64,306-file, and 21-image results. Require no dependency-diagnostic identity for the uncommitted candidate.

- [ ] **Step 5: Perform a cold requirements and code review**

Use `requesting-code-review` and review the complete diff against the approved design, original plan, and this erratum. The reviewer must report `Critical=0` and `Important=0` for:

- registry/schema property closure and state-specific absence rules;
- path containment, links, duplicate identities, unordered ordinals, and extra external objects;
- file SHA stability from load until the first write and identity-audit binding;
- removal of executable attempt-specific constants without weakening attempts 1–4;
- exact retry signatures, byte preservation, backoffs, process count, signal handling, and non-transport fail-fast;
- exact uv 0.8.15, lock/base/runtime preservation, two cache mounts, one launcher build, and no Docker-level retry;
- no formal runtime, GPU, model, owner synthesis, RDD, Wave 1, push, merge, or release path.

Resolve a finding with a new failing test followed by the smallest implementation change, then rerun every affected gate and repeat review.

- [ ] **Step 6: Stage exactly seven paths and commit once**

```powershell
git add -- `
  configs/a11/preserved-attempts.json `
  schemas/a11-preserved-attempts.schema.json `
  scripts/run_uv_sync_with_retries.py `
  scripts/run_wave0_a11.ps1 `
  docker/wave0.Dockerfile `
  tests/gates/test_wave0_a11_launcher.py `
  tests/scripts/test_run_uv_sync_with_retries.py
$Staged = @(git diff --cached --name-only | Sort-Object)
$Expected = @(
  'configs/a11/preserved-attempts.json',
  'docker/wave0.Dockerfile',
  'schemas/a11-preserved-attempts.schema.json',
  'scripts/run_uv_sync_with_retries.py',
  'scripts/run_wave0_a11.ps1',
  'tests/gates/test_wave0_a11_launcher.py',
  'tests/scripts/test_run_uv_sync_with_retries.py'
) | Sort-Object
if (($Staged | ConvertTo-Json -Compress) -cne ($Expected | ConvertTo-Json -Compress)) {
    throw 'staged scope mismatch'
}
git diff --cached --check
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git commit -m 'fix: harden A11 dependency transport boundary'
```

- [ ] **Step 7: Verify the committed candidate before diagnostic eligibility**

Require the implementation parent to equal the erratum commit, whose parent is the original plan commit `e31fc0c10fe34b480f7b2ee3d12a2e55530c6350`, exact seven changed paths, exact author/committer, clean linked and canonical worktrees, empty staging, unchanged `uv.lock`, and unchanged preservation report. Re-run the wrapper suite, full launcher suite, both parser gates, schema validation, Dockerfile `--check`, and `git show --check HEAD` from the committed tree.

Do not describe the formal A11 runtime as fixed or passing. At this point the only permitted claim is that the source candidate passed CPU/repository/preservation review and is eligible for the one dependency-only diagnostic.

---

### Task 7: Execute and preserve exactly one dependency-only diagnostic

**Files:**
- Modify in repository: none
- Create outside repository and outside the artifact baseline: one append-only directory under `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics`
- Docker effect: BuildKit cache data only; no image export

**Interfaces:**
- Consumes: the clean implementation commit and Docker target `a11-dependencies`
- Produces: one immutable diagnostic terminal, either `A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED` or `A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN`

- [ ] **Step 1: Prove diagnostic eligibility without creating its directory**

Repeat Task 6 Step 7. Additionally require:

```powershell
$Source = (git rev-parse HEAD).Trim()
$Erratum = (git rev-parse 'HEAD^').Trim()
$OriginalPlan = (git rev-parse 'HEAD^^').Trim()
if ($OriginalPlan -cne 'e31fc0c10fe34b480f7b2ee3d12a2e55530c6350' -or
    (git rev-parse 'HEAD^^^').Trim() -cne 'db047dcb8ad602fc4ac316a743ab4ddec3168cd5') {
    throw 'design/original-plan/erratum/source lineage mismatch'
}
if ((docker info --format '{{.OSType}}|{{.ServerVersion}}').Trim() -cnotmatch '^linux\|[^|]+$') {
    throw 'Docker Linux engine unavailable'
}
$Active = @(Get-ChildItem -LiteralPath 'D:\vision-active-learning-loop-artifacts\wave0\leases' `
    -File -Force | Where-Object { $_.Name -cmatch '^GPU-[A-Za-z0-9-]+\.json$' })
if ($Active.Count -ne 0) { throw 'active lease exists' }
$Compute = @(& nvidia-smi --query-compute-apps=pid --format=csv,noheader,nounits |
    Where-Object { $_ -match '^\s*[0-9]+\s*$' })
if ($Compute.Count -ne 0) { throw 'CUDA compute process exists' }
```

Require zero project containers using the same inspect-based inventory as Task 1. Snapshot `docker image ls --no-trunc --digests` and all preservation hashes. Scan every existing `D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics\*\00-identity.json`; if any contains this exact `$Source`, stop because this source already consumed its diagnostic.

- [ ] **Step 2: Create one fresh append-only diagnostic identity**

Freeze the naming rule:

```text
parent: D:\vision-active-learning-loop-diagnostics\wave0\a11-dependency-diagnostics
child:  a11-dependencies-<first 12 source hex>-<yyyyMMddTHHmmssfffZ>-<8 lowercase GUID hex>
```

Create the parent only if absent and non-link. Create the child exactly once with `New-Item -ErrorAction Stop`; reject any parent/child reparse point. The exact evidence names are:

```text
00-identity.json
10-build.stdout.log
10-build.stderr.log
11-result.json
12-file-manifest.json
13-closure.json
```

Write `00-identity.json` with `FileMode.CreateNew`, UTF-8 without BOM, one final LF, and this closed content:

```text
schema_version = 1
diagnostic_type = a11-dependency-transport
diagnostic_id
source_commit
recovery_plan_commit = e31fc0c10fe34b480f7b2ee3d12a2e55530c6350
recovery_plan_erratum_commit
design_commit = db047dcb8ad602fc4ac316a743ab4ddec3168cd5
specification_commit = b59b0d4407b98b460f6166ea7288ba6021dc7a78
original_plan_commit = 7dbd3a7576ea76beccfc64f748c4e495259ea89b
branch = codex/wave0-model-contract
docker_ostype
docker_server_version
docker_buildx_version
started_utc
argv = [docker, buildx, build, --no-cache, --progress=plain, --target, a11-dependencies, --output=type=cacheonly, --file, docker/wave0.Dockerfile, .]
formal_runtime_authorized = false
owner_authorization_id_present = false
gpu_requested = false
```

- [ ] **Step 3: Invoke the exact diagnostic once**

From the clean linked worktree, run this command once and only once:

```powershell
& docker buildx build `
  --no-cache `
  --progress=plain `
  --target a11-dependencies `
  --output=type=cacheonly `
  --file docker/wave0.Dockerfile `
  . `
  1> (Join-Path $DiagnosticPath '10-build.stdout.log') `
  2> (Join-Path $DiagnosticPath '10-build.stderr.log')
$DiagnosticExitCode = $LASTEXITCODE
```

Do not invoke this command through a retry loop, shell loop, second terminal, launcher, or automation. Do not run it again if Codex disconnects after the process starts; inspect the evidence/process state and preserve a NO_GO if completion cannot be proven.

- [ ] **Step 4: Publish the immutable result, manifest, and closure**

Write `11-result.json` with exact argv, exit code, start/end UTC, stdout/stderr file records, observed attempt markers, and one terminal:

```text
exit 0    -> A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED
nonzero   -> A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN
```

The attempt-marker list is every case-sensitive
`A11_UV_SYNC_ATTEMPT [123]/3` occurrence observed in the two logs, retained in
log order even when BuildKit prefixes the containing line. Do not reinterpret a
nonzero exit as success even if retry markers appear.

Write `12-file-manifest.json` over exactly `00-identity.json`, both build logs, and `11-result.json`, each with relative path, byte size, and SHA-256 sorted by ordinal relative path. Write `13-closure.json` containing the result file record, manifest file record, the same terminal, `formal_runtime_invoked=false`, and `wave1_started=false`. All three JSON files use create-new semantics, closed property sets, UTF-8 without BOM, and one final LF.

- [ ] **Step 5: Re-prove preservation and stop at the diagnostic terminal**

Repeat Task 1 Steps 2–3 and require the implementation Git worktrees remain clean. Compare the pre/post Docker image inventories byte-for-byte; `cacheonly` must not create a tagged or dangling exported image. Require zero new A11 run, validation root, lease, project container, receipt, checkpoint, owner identity, model process, and Wave 1 object.

If exit 0 and all post-gates pass, report:

```text
A11_DEPENDENCY_DIAGNOSTIC_PASS / FORMAL_RUNTIME_NOT_AUTHORIZED
```

Otherwise preserve all six evidence files and report:

```text
A11_DEPENDENCY_DIAGNOSTIC_NO_GO / FORMAL_RUNTIME_FORBIDDEN
```

Stop in either case. Do not request, infer, reserve, or consume another `OwnerAuthorizationId`; a later formal attempt needs a separate owner authorization bound to the exact implementation source, original specification, original A11 plan, and branch.
