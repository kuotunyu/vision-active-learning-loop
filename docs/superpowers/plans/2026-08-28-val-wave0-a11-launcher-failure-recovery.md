# Wave 0 A11 Launcher Failure-Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Repair the checked-in A11 launcher so its real foundation command contracts succeed, every normal failure closes with bound 78–82 evidence, closure failures remain explicit, and exactly one campaign result reaches the entry point.

**Architecture:** Keep the existing two-phase launcher and add small PowerShell contract helpers around receipt path validation, receipt re-hashing, and result cardinality. Exercise the production helpers from the existing Python/PowerShell AST harness while replacing only native Docker/GPU and historical-inventory boundaries; retain the exact cache and replica stream contracts.

**Tech Stack:** PowerShell 7 and Windows PowerShell 5.1 parser; Python 3.12.11; pytest 9.0.2; Black and Ruff; Git linked worktree; read-only Docker/image inspection for preservation verification only.

## Global Constraints

- The approved supplemental design is `docs/superpowers/specs/2026-08-28-val-wave0-a11-launcher-failure-recovery-design.md` at commit `5972b8453d8f33465c15f27f02e402315a3c886e`.
- The existing A11 implementation is commit `2622e402e4f536b94326ac34f9b20c90b513002b`; this plan commit must be its design commit's direct child and must add only this plan file.
- The failed run `wave0-a11-calibration-20260828T045848083Z-b9917463`, image `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`, and authorization `OWNER-A11-RUNTIME-20260828-01` are immutable and must never be reused or repaired in place.
- This authorization covers CPU-only TDD repair. Do not run the A11 launcher, build an image, download a cache, acquire a GPU lease, initialize a model, run a replica, access RDD data, start validation, or start Wave 1.
- Do not synthesize or reuse an owner authorization identifier. A future runtime attempt needs a new owner review and a new explicit identifier.
- The implementation tracked-file allowlist is exactly `scripts/run_wave0_a11.ps1` and `tests/gates/test_wave0_a11_launcher.py`. A third implementation path is a hard stop for owner review.
- Keep the 12+12 cohorts, all 66-pair and 13-metric contracts, thresholds, ceilings, receipt schemas, model/cache/GPU identities, phase order, cache-preflight stream contract, replica stream contract, lease semantics, and every Python production module unchanged.
- Preserve 64,306 historical files at inventory SHA-256 `e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95` and 21 historical images at inventory SHA-256 `9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f`.
- Preserve failed-run record `79-historical-preservation-final.json` at SHA-256 `927c57d5390bf2267b22b6af2718035530f48071ea48cc926329a696397b319d`, released lease at SHA-256 `146c280df6f4c7f3b2d38078cac303324ab24755c09cdead0c567ec7d7f73322`, and release record at SHA-256 `35cd6e614bade69f663dbe10a152af6a6b471d269828ba0715b33d7c7a117060`.
- Do not create `78-failure-diagnostic.json`, `80-campaign-result.json`, `81-campaign-file-manifest.json`, or `82-campaign-closure.json` inside the preserved failed run.
- Keep staging empty through every RED/GREEN cycle. After all gates pass, create one implementation commit with author and committer `kuotunyu <61350295+kuotunyu@users.noreply.github.com>`.
- No amend, rebase, squash, reset, stash, history rewrite, cleanup, push, merge, tag, Release, publication, or change to another repository is permitted.

## File Responsibility Map

| Path | Responsibility |
|---|---|
| `scripts/run_wave0_a11.ps1` | Validate command-specific foundation streams and receipts, bind consumed receipts, suppress helper output leakage, publish complete failure closure, expose closure errors, and enforce one entry-point result |
| `tests/gates/test_wave0_a11_launcher.py` | CPU-only production-function regression tests for foundation contracts, receipt confinement/mutation, unchanged cache/replica streams, closure binding, closure-error propagation, and result cardinality |

---

### Task 1: Freeze the recovery entry state

**Files:**
- Modify: none
- Inspect: linked and canonical worktrees, failed-run evidence, historical artifacts, project images, leases and containers

**Interfaces:**
- Consumes: approved design commit `5972b8453d8f33465c15f27f02e402315a3c886e` and this reviewed plan commit
- Produces: a read-only preservation baseline and a clean two-file implementation entry gate

- [ ] **Step 1: Verify Git identity and plan lineage**

Run from the linked worktree:

```powershell
$PlanCommit = (git rev-parse HEAD).Trim()
$DesignCommit = '5972b8453d8f33465c15f27f02e402315a3c886e'
if ((git branch --show-current).Trim() -cne 'codex/wave0-model-contract') { throw 'branch mismatch' }
if ((git rev-parse "$PlanCommit^").Trim() -cne $DesignCommit) { throw 'plan parent mismatch' }
$PlanPaths = @(git diff-tree --no-commit-id --name-only -r $PlanCommit)
if ($PlanPaths.Count -ne 1 -or $PlanPaths[0] -cne 'docs/superpowers/plans/2026-08-28-val-wave0-a11-launcher-failure-recovery.md') { throw 'plan scope mismatch' }
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'linked worktree is dirty' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty' }
```

Use `git worktree list --porcelain` and `git rev-parse --path-format=absolute --git-common-dir` to identify the canonical worktree. Require the same common directory and a clean canonical worktree. Preserve and report any mismatch; do not repair it.

- [ ] **Step 2: Recompute the immutable runtime baseline read-only**

Hash the entire preserved failed-run directory as sorted records of relative path, byte size, and lowercase SHA-256. Record its file count and canonical JSON digest in the execution transcript. Separately require the three fixed evidence hashes from Global Constraints, confirm the released lease is inactive, and confirm the four absent closure paths remain absent.

Load `Get-A11HistoricalArtifactInventory` and `Get-A11HistoricalImageInventory` from the production script through the existing AST technique. Require the fixed 64,306-file and 21-image counts/digests. Read-only `docker image inspect` must bind the failed image tag to `sha256:52b62e99d65269649d1e75e7397e9cab7d20cc5fe0e5dc46d661b1ec6625b0d5`; require no running project container and no active A11 lease. Do not invoke `docker build`, `docker run`, or the launcher.

- [ ] **Step 3: Confirm exact edit scope before RED**

```powershell
$Allowed = @('scripts/run_wave0_a11.ps1', 'tests/gates/test_wave0_a11_launcher.py')
if (@(git status --porcelain=v1 --untracked-files=all).Count -ne 0) { throw 'candidate is not clean before RED' }
if (@(git diff --cached --name-only).Count -ne 0) { throw 'staging is not empty before RED' }
$Allowed | ForEach-Object { if (-not (Test-Path -LiteralPath $_ -PathType Leaf)) { throw "missing allowlisted path: $_" } }
```

---

### Task 2: Enforce command-specific foundation and receipt contracts

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Modify: `scripts/run_wave0_a11.ps1`

**Interfaces:**
- Consumes: `Invoke-A11Native`, `Write-A11ProcessAudit`, `Get-A11FileRecord`, `New-A11ReplicaArguments`
- Produces: `Get-A11VerifiedStageReceipt`, `Assert-A11FileRecordUnchanged`, `Invoke-A11DockerStage -ExpectedStdout -ReceiptPath`, and `Identity.foundation_receipts`

- [ ] **Step 1: Add the RED production-adapter harness and canonical success cases**

Add a Python helper that creates `campaign_root/audit` and `campaign_root/wave0/receipts`, writes this closed receipt shape, extracts the real production functions, and replaces only `Invoke-A11Native`:

```python
def _stage_receipt(run_id: str, *, status: str = "PASS", errors: list[str] | None = None) -> dict[str, object]:
    return {
        "schema_version": 1,
        "metadata": {"run_id": run_id},
        "normative": {"status": status, "errors": [] if errors is None else errors},
    }


def _run_foundation_stage(
    tmp_path: Path,
    *,
    name: str,
    stdout: str,
    expected_stdout: str,
    receipt_name: str,
    receipt: dict[str, object] | None,
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    receipt_path = receipts / receipt_name
    if receipt is not None:
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    audit_records=[ordered]@{{}}
}}
function Invoke-A11Native {{
    return [pscustomobject]@{{ ExitCode=0; Stdout={_ps(stdout)}; Stderr='' }}
}}
Invoke-A11DockerStage -Identity $Identity -Name {_ps(name)} `
    -Command @('probe') -ExpectedStdout {_ps(expected_stdout)} `
    -ReceiptPath {_ps(str(receipt_path))} | ConvertTo-Json -Depth 8 -Compress
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Write-A11ProcessAudit",
            "Get-A11VerifiedStageReceipt",
            "Invoke-A11DockerStage",
        ),
        body,
    )


def _run_untrusted_receipt_case(
    tmp_path: Path,
    *,
    defect: str,
    receipt: dict[str, object] | None,
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipt_root = campaign / "wave0" / "receipts"
    outside = tmp_path / "outside"
    audit.mkdir(parents=True)
    receipt_root.mkdir(parents=True)
    outside.mkdir()
    junction_setup = ""
    if defect == "outside":
        receipt_path = outside / "environment.json"
        write_path = receipt_path
    elif defect == "junction":
        target = outside / "linked"
        target.mkdir()
        receipt_path = campaign / "wave0" / "linked" / "environment.json"
        write_path = target / "environment.json"
        junction_setup = (
            f"New-Item -ItemType Junction -Path {_ps(str(receipt_path.parent))} "
            f"-Target {_ps(str(target))} | Out-Null"
        )
    else:
        receipt_path = receipt_root / "environment.json"
        write_path = receipt_path
    if receipt is not None:
        write_path.write_text(json.dumps(receipt), encoding="utf-8")
    body = f"""
{junction_setup}
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    audit_records=[ordered]@{{}}
}}
function Invoke-A11Native {{
    return [pscustomobject]@{{ ExitCode=0; Stdout=''; Stderr='' }}
}}
Invoke-A11DockerStage -Identity $Identity -Name '30-environment' `
    -Command @('environment','check') -ExpectedStdout '' `
    -ReceiptPath {_ps(str(receipt_path))} | Out-Null
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Write-A11ProcessAudit",
            "Get-A11VerifiedStageReceipt",
            "Invoke-A11DockerStage",
        ),
        body,
    )
```

Add `test_foundation_stages_enforce_registered_stream_and_receipt_contracts`, parameterized with these exact tuples:

```python
(
    ("30-environment", "", "environment.json"),
    ("31-model-assets", "PASS\n", "model-assets.json"),
    ("32-model-contract", "PASS\n", "model-contract.json"),
)
```

For every row, invoke real `Invoke-A11DockerStage` with exit 0, the registered stdout, empty stderr, and a PASS receipt. Assert return code 0 and that the stage audit's `receipt` path/size/SHA-256 recompute to the file.

- [ ] **Step 2: Run the canonical stage test and verify RED**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py::test_foundation_stages_enforce_registered_stream_and_receipt_contracts
```

Expected: FAIL because `Invoke-A11DockerStage` does not accept `ExpectedStdout` or `ReceiptPath`, and environment still requires `PASS\n`.

- [ ] **Step 3: Add RED rejection cases for streams, paths, contents, and mutation**

Add these focused tests against production functions. The first is complete; the
parameterized test uses the same `_run_foundation_stage` helper, except `junction`
creates a PowerShell directory junction inside the phase root targeting an outside
directory and `outside` passes the outside receipt path directly:

```python
def test_environment_rejects_noncanonical_pass_stdout(tmp_path: Path) -> None:
    completed = _run_foundation_stage(
        tmp_path,
        name="30-environment",
        stdout="PASS\n",
        expected_stdout="",
        receipt_name="environment.json",
        receipt=_stage_receipt("wave0-a11-calibration-test"),
    )
    assert completed.returncode != 0
    assert "A11 stage failed: 30-environment" in completed.stderr

@pytest.mark.parametrize("defect", ["missing", "junction", "outside", "wrong-run", "fail", "errors"])
def test_foundation_stage_rejects_untrusted_receipt(tmp_path: Path, defect: str) -> None:
    receipt = {
        "missing": None,
        "wrong-run": _stage_receipt("wrong-run"),
        "fail": _stage_receipt("wave0-a11-calibration-test", status="FAIL"),
        "errors": _stage_receipt("wave0-a11-calibration-test", errors=["injected"]),
    }.get(defect, _stage_receipt("wave0-a11-calibration-test"))
    completed = _run_untrusted_receipt_case(tmp_path, defect=defect, receipt=receipt)
    assert completed.returncode != 0
    assert completed.stderr
```

Add `test_foundation_rehashes_environment_and_assets_before_model_contract` with
three native-call events. Calls 1 and 2 publish the valid environment and asset
receipts; immediately before call 3, replace `environment.json` with different
bytes. Assert process failure, stderr contains `changed`, and the recorded event
list contains only calls 1 and 2. Add
`test_replica_rehashes_model_contract_before_native_launch` with a stored
`foundation_receipts.model_contract` record followed by a byte mutation; assert
stderr contains `changed` and the native-call counter remains zero.

Create the `junction` case with a PowerShell directory junction below the phase root that targets a receipt directory outside it. This proves every path component is checked without requiring symbolic-link privilege.

- [ ] **Step 4: Run all new receipt tests and verify RED for the named missing behavior**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_environment_rejects_noncanonical_pass_stdout `
  tests/gates/test_wave0_a11_launcher.py::test_foundation_stage_rejects_untrusted_receipt `
  tests/gates/test_wave0_a11_launcher.py::test_foundation_rehashes_environment_and_assets_before_model_contract `
  tests/gates/test_wave0_a11_launcher.py::test_replica_rehashes_model_contract_before_native_launch
```

Expected: FAIL because receipt confinement/content verification and dependent-use rehashing do not exist.

- [ ] **Step 5: Implement minimal receipt validation and command-specific stage behavior**

Add production helpers with these exact interfaces:

```powershell
function Get-A11VerifiedStageReceipt {
    param(
        [Parameter(Mandatory = $true)][object]$Identity,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Root = [IO.Path]::GetFullPath([string]$Identity.campaign_root)
    $FullPath = [IO.Path]::GetFullPath($Path)
    $Relative = [IO.Path]::GetRelativePath($Root, $FullPath)
    if (
        [IO.Path]::IsPathRooted($Relative) -or $Relative -ceq '..' -or
        $Relative.StartsWith('..\', [StringComparison]::Ordinal) -or
        $Relative.StartsWith('../', [StringComparison]::Ordinal)
    ) { throw "A11 stage receipt escapes the phase root: $Path" }
    $Segments = @($Relative.Split(
        [char[]]@([IO.Path]::DirectorySeparatorChar, [IO.Path]::AltDirectorySeparatorChar),
        [StringSplitOptions]::RemoveEmptyEntries
    ))
    if ($Segments.Count -eq 0) { throw "A11 stage receipt path is invalid: $Path" }
    $Cursor = $Root
    for ($Index = -1; $Index -lt $Segments.Count; $Index++) {
        if ($Index -ge 0) { $Cursor = [IO.Path]::Combine($Cursor, $Segments[$Index]) }
        $Item = Get-Item -LiteralPath $Cursor -Force -ErrorAction Stop
        if ($Item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            throw "A11 stage receipt path contains a link: $Path"
        }
        if ($Index -lt ($Segments.Count - 1) -and -not $Item.PSIsContainer) {
            throw "A11 stage receipt ancestor is not a directory: $Path"
        }
        if ($Index -eq ($Segments.Count - 1) -and $Item.PSIsContainer) {
            throw "A11 stage receipt is not a regular file: $Path"
        }
    }
    $Document = Get-Content -Raw -LiteralPath $FullPath | ConvertFrom-Json
    if (
        [string]$Document.metadata.run_id -cne [string]$Identity.run_id -or
        [string]$Document.normative.status -cne 'PASS' -or
        @($Document.normative.errors).Count -ne 0
    ) { throw "A11 stage receipt contract failed: $Path" }
    return Get-A11FileRecord -Path $FullPath
}

function Assert-A11FileRecordUnchanged {
    param(
        [Parameter(Mandatory = $true)][object]$Expected,
        [Parameter(Mandatory = $true)][string]$Path
    )
    $Observed = Get-A11FileRecord -Path $Path
    if (
        [string]$Observed.path -cne [string]$Expected.path -or
        [long]$Observed.size -ne [long]$Expected.size -or
        [string]$Observed.sha256 -cne [string]$Expected.sha256
    ) { throw "A11 verified receipt changed before use: $Path" }
    return $true
}
```

Extend `Write-A11ProcessAudit` with optional `[object]$ReceiptRecord = $null` and include `receipt = $ReceiptRecord` in its JSON. Extend `Invoke-A11DockerStage` with mandatory `[AllowEmptyString()][string]$ExpectedStdout` and `[string]$ReceiptPath`. Require exact exit/stdout/stderr first, validate the receipt, write the bound audit, and return its file record.

Preserve process evidence on rejected streams or receipts with this control flow:

```powershell
$StreamsSucceeded = (
    $Result.ExitCode -eq 0 -and $Result.Stdout -ceq $ExpectedStdout -and
    $Result.Stderr -ceq ''
)
$ReceiptRecord = $null
$ReceiptFailure = $null
if ($StreamsSucceeded) {
    try {
        $ReceiptRecord = Get-A11VerifiedStageReceipt -Identity $Identity -Path $ReceiptPath
    } catch {
        $ReceiptFailure = $_
    }
}
$Identity.audit_records[$Name] = Write-A11ProcessAudit `
    -Identity $Identity -Name $Name -Argv (@('docker') + $Arguments) `
    -Result $Result -ReceiptRecord $ReceiptRecord
if (-not $StreamsSucceeded) { throw "A11 stage failed: $Name" }
if ($null -ne $ReceiptFailure) { throw $ReceiptFailure.Exception }
return $ReceiptRecord
```

Register the three exact host receipt paths and stdout values in `Invoke-A11Foundation`. Capture all stage returns, rehash environment and assets immediately before model-contract, and store all three records in a new `[ordered]@{}` `foundation_receipts` member created by `New-A11PhaseIdentity`. In `Invoke-A11Replica`, rehash `foundation_receipts.model_contract` before `Invoke-A11Native`.

- [ ] **Step 6: Run GREEN for foundation and dependent-use tests**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_foundation_stages_enforce_registered_stream_and_receipt_contracts `
  tests/gates/test_wave0_a11_launcher.py::test_environment_rejects_noncanonical_pass_stdout `
  tests/gates/test_wave0_a11_launcher.py::test_foundation_stage_rejects_untrusted_receipt `
  tests/gates/test_wave0_a11_launcher.py::test_foundation_rehashes_environment_and_assets_before_model_contract `
  tests/gates/test_wave0_a11_launcher.py::test_replica_rehashes_model_contract_before_native_launch
```

Expected: all selected cases PASS with no Docker or GPU process.

- [ ] **Step 7: Prove cache and replica stream contracts did not weaken**

Add `test_cache_preflight_and_replica_keep_exact_pass_stream_contracts`. Invoke the real functions through native stubs and parameterize stdout as `""`, `"PASS"`, `"PASS\r\n"`, and `"PASS\nextra\n"`; each must fail. The sole accepted value remains `"PASS\n"`, with exit 0 and empty stderr. For the accepted replica case, publish exactly one receipt, checkpoint, and 64-hex cid required by the existing adapter.

Run RED before any correction to these test fixtures, then GREEN:

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py::test_cache_preflight_and_replica_keep_exact_pass_stream_contracts
```

- [ ] **Step 8: Keep the cumulative candidate uncommitted and staging empty**

```powershell
git diff --check -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
git diff --cached --name-only
git status --short
```

Require exactly the two allowlisted modified paths and no staged path.

---

### Task 3: Publish complete failure closure and expose closure errors

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Modify: `scripts/run_wave0_a11.ps1`

**Interfaces:**
- Consumes: `Write-A11NewText` with `FileMode.CreateNew`, `Get-A11FileRecord`, `Close-A11Phase`, `Invoke-A11Campaign`
- Produces: ordered bound failure files 78–82 and result property `closure_error` on publication failure

- [ ] **Step 1: Add a RED real-closure binding test**

Add `test_close_a11_phase_publishes_complete_bound_failure_chain`. Extract and execute the real `Write-A11NewText`, `Get-A11FileRecord`, and `Close-A11Phase`; replace only the two historical inventory functions with fixed in-memory arrays of 64,306 and 21 elements and their registered digests. Use a fully populated calibration identity and failure `injected:foundation`.

Assert all five files exist and have this exact relationship:

```python
def _file_record(path: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {
        "path": path.resolve().as_posix(),
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


names = [
    "78-failure-diagnostic.json",
    "79-historical-preservation-final.json",
    "80-campaign-result.json",
    "81-campaign-file-manifest.json",
    "82-campaign-closure.json",
]
assert [path.name for path in sorted(audit.glob("7*.json")) + sorted(audit.glob("8*.json"))] == names
assert result["failure_diagnostic"] == _file_record(audit / names[0])
assert result["historical_preservation"] == _file_record(audit / names[1])
assert closure["result"] == _file_record(audit / names[2])
assert closure["manifest"] == _file_record(audit / names[3])
```

Recompute every manifest record from disk. Require the manifest includes 78, 79, and 80, but excludes itself and 82.

- [ ] **Step 2: Run the closure binding test and verify RED**

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py::test_close_a11_phase_publishes_complete_bound_failure_chain
```

Expected: FAIL because the production order begins with 79 and the observed failure path does not guarantee the complete chain.

- [ ] **Step 3: Add a RED no-retry closure-publication failure test**

Add `test_campaign_surfaces_closure_write_failure_without_retry`. Execute the real `Invoke-A11Campaign` and `Close-A11Phase`; stub preflight, Git, phase identity, and historical inventories. Have `Initialize-A11Phase` create the audit directory, pre-create immutable `78-failure-diagnostic.json` with sentinel bytes, and throw `injected:initialize`. Count calls to each historical inventory function.

Assert the campaign emits exactly one result with:

```python
assert result["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
assert result["error"] == "injected:initialize"
assert "already exists" in result["closure_error"].lower()
assert artifact_inventory_calls == image_inventory_calls == 1
assert diagnostic.read_bytes() == b"sentinel"
```

This proves real `FileMode.CreateNew` failure is explicit, closure is attempted once, and the existing file is not overwritten.

- [ ] **Step 4: Run the closure-error test and verify RED**

```powershell
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py::test_campaign_surfaces_closure_write_failure_without_retry
```

Expected: FAIL because the campaign currently swallows the closure exception and omits `closure_error`.

- [ ] **Step 5: Implement precomputed ordered closure and explicit error propagation**

Refactor `Close-A11Phase` so it computes historical inventories, `Preserved`, the final terminal, complete `ErrorList`, the diagnostic/history documents, and all destination paths before the first write. For normative failure, publish 78 and capture its file record, publish 79 and capture its record, then construct and publish 80, inventory all pre-manifest files into 81, and bind 80/81 in 82. Keep success behavior diagnostic-free and publish 79–82. Every write continues to use `Write-A11NewText` and `FileMode.CreateNew`.

Replace the empty campaign catch with exactly one closure attempt:

```powershell
try {
    Close-A11Phase $Identity 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' $Failure | Out-Null
} catch {
    return [pscustomobject]@{
        terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
        error = $Failure
        closure_error = $_.Exception.Message
    }
}
return [pscustomobject]@{
    terminal = 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN'
    error = $Failure
}
```

If `$Identity.current_stage -ceq 'closure'`, return the same normative-failure shape with `error = 'A11 phase closure publication failed'` and the caught message in `closure_error`; do not call `Close-A11Phase` again. Never proceed to validation after either failure shape.

- [ ] **Step 6: Run GREEN and existing failure-order regressions**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_close_a11_phase_publishes_complete_bound_failure_chain `
  tests/gates/test_wave0_a11_launcher.py::test_campaign_surfaces_closure_write_failure_without_retry `
  tests/gates/test_wave0_a11_launcher.py::test_calibration_failure_prohibits_validation_and_second_invocation `
  tests/gates/test_wave0_a11_launcher.py::test_each_calibration_stage_failure_closes_once_without_retry
```

Expected: all selected cases PASS; the test harness creates only temporary CPU-side files.

---

### Task 4: Enforce a single campaign result and suppress helper leakage

**Files:**
- Modify: `tests/gates/test_wave0_a11_launcher.py`
- Modify: `scripts/run_wave0_a11.ps1`

**Interfaces:**
- Consumes: `Invoke-A11Campaign`, `Invoke-A11CachePreflight`
- Produces: `Get-A11SingleCampaignResult -Values object[]` and guarded entry-point serialization

- [ ] **Step 1: Add RED campaign leakage and cardinality tests**

Add `test_campaign_suppresses_cache_evidence_and_emits_one_result`. Use the existing production `Invoke-A11Campaign` AST harness; make the cache stub emit `[pscustomobject]@{ cache = 'evidence' }`, fail calibration at foundation, and have closure succeed. Materialize output with `$Values = @(Invoke-A11Campaign $SourceCommit $SpecCommit $PlanCommit $Branch $AuthorizationId)` and assert `count == 1` plus the normative-failure terminal.

Add `test_single_campaign_result_rejects_zero_or_multiple_values`, parameterized with zero and two objects. Invoke the production `Get-A11SingleCampaignResult` and require a nonzero process plus `A11 campaign result cardinality mismatch: expected 1, observed N`.

```python
@pytest.mark.parametrize(
    ("values", "observed"),
    [
        ("$Values = @()", 0),
        (
            "$Values = @([pscustomobject]@{terminal='one'}, "
            "[pscustomobject]@{terminal='two'})",
            2,
        ),
    ],
)
def test_single_campaign_result_rejects_zero_or_multiple_values(
    values: str, observed: int
) -> None:
    body = f"""
{values}
Get-A11SingleCampaignResult -Values $Values | Out-Null
"""
    completed = _invoke_functions(("Get-A11SingleCampaignResult",), body)
    assert completed.returncode != 0
    assert (
        f"A11 campaign result cardinality mismatch: expected 1, observed {observed}"
        in completed.stderr
    )
```

- [ ] **Step 2: Run the pipeline tests and verify RED**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_campaign_suppresses_cache_evidence_and_emits_one_result `
  tests/gates/test_wave0_a11_launcher.py::test_single_campaign_result_rejects_zero_or_multiple_values
```

Expected: the first test observes two outputs and the second cannot find the new production function.

- [ ] **Step 3: Implement minimal single-result discipline**

Pipe the cache-preflight call in `Invoke-A11Campaign` to `Out-Null`. Audit every other orchestration-helper call: capture its return or pipe it to `Out-Null`, except the one intended final `PSCustomObject`.

Add:

```powershell
function Get-A11SingleCampaignResult {
    param(
        [Parameter(Mandatory = $true)]
        [AllowEmptyCollection()]
        [object[]]$Values
    )
    if ($Values.Count -ne 1) {
        throw "A11 campaign result cardinality mismatch: expected 1, observed $($Values.Count)"
    }
    $Result = $Values[0]
    if ($null -eq $Result -or $null -eq $Result.PSObject.Properties['terminal']) {
        throw 'A11 campaign result terminal is missing'
    }
    return $Result
}
```

At the entry point, use `$A11Values = @(Invoke-A11Campaign $ExpectedSourceCommit $ExpectedSpecCommit $ExpectedPlanCommit $ExpectedBranch $OwnerAuthorizationId)`, call `Get-A11SingleCampaignResult` before terminal access, serialize only that object, and write `closure_error` to stderr when the property exists and is nonempty. Keep exit 0 exclusive to `WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED`; every other result or cardinality error exits 2.

Extend the static source test with ordered guards:

```python
values_index = source.index("$A11Values = @(")
guard_index = source.index("Get-A11SingleCampaignResult -Values $A11Values")
terminal_index = source.index("$A11Result.terminal", guard_index)
assert values_index < guard_index < terminal_index
assert "$A11Result.closure_error" in source
assert "[Console]::Error.WriteLine" in source
```

- [ ] **Step 4: Run GREEN and source capability assertions**

```powershell
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_wave0_a11_launcher.py::test_campaign_suppresses_cache_evidence_and_emits_one_result `
  tests/gates/test_wave0_a11_launcher.py::test_single_campaign_result_rejects_zero_or_multiple_values `
  tests/gates/test_wave0_a11_launcher.py::test_launcher_has_exact_parameters_and_required_functions `
  tests/gates/test_wave0_a11_launcher.py::test_launcher_source_has_no_cleanup_retry_or_wave1_capability
```

Expected: all selected cases PASS and source still contains no cleanup, retry, synthesized authorization, or Wave 1 command.

---

### Task 5: Verify, review, and create the single implementation commit

**Files:**
- Stage and commit only: `scripts/run_wave0_a11.ps1`
- Stage and commit only: `tests/gates/test_wave0_a11_launcher.py`
- Historical and runtime evidence: read-only

**Interfaces:**
- Consumes: Tasks 1–4 plus the immutable entry baseline
- Produces: one reviewed clean candidate commit; no runtime attempt

- [ ] **Step 1: Run the complete launcher and original A11 focused suites**

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
uv run pytest -q -p no:cacheprovider tests/gates/test_wave0_a11_launcher.py
uv run pytest -q -p no:cacheprovider `
  tests/gates/test_numerical_replay.py `
  tests/gates/test_statistical_replay.py `
  tests/artifacts/test_receipts.py `
  tests/artifacts/test_statistical_replay_receipts.py `
  tests/gates/test_wave0_a11_launcher.py
```

- [ ] **Step 2: Run the complete CPU suite and static gates**

```powershell
uv run pytest -q -p no:cacheprovider
uvx --offline black --check tests/gates/test_wave0_a11_launcher.py
uvx --offline ruff check tests/gates/test_wave0_a11_launcher.py
uv lock --check
git diff --check
```

Parse `scripts/run_wave0_a11.ps1` with `[Management.Automation.Language.Parser]::ParseFile` under both `pwsh -NoProfile -NonInteractive` and `powershell -NoProfile -NonInteractive`. Require both error arrays to be empty.

- [ ] **Step 3: Review exact scope and contracts**

Require staging empty and the union of tracked/untracked candidate paths exactly equal the two-file implementation allowlist. Review the approved supplemental design and original Section 5.2.15 line-by-line. Require Critical=0 and Important=0, specifically checking:

- environment accepts only exit 0, empty stdout, empty stderr, and a bound PASS receipt;
- assets and model-contract accept only exit 0, `PASS\n`, empty stderr, and bound PASS receipts;
- receipt path chains reject reparse points and root escape, and every dependent use rehashes;
- cache and replica accept only their unchanged `PASS\n`/empty-stderr contracts;
- normal failure publishes bound 78–82 records once; closure failure is explicit and never retried;
- campaign output cardinality is exactly one before terminal access;
- no altered cohort, metric, threshold, ceiling, schema, identity, retry, cleanup, or Wave 1 behavior exists.

- [ ] **Step 4: Repeat the read-only preservation gate**

Repeat Task 1 Step 2 with the identical algorithms. Require the failed-run file count and canonical inventory digest exactly equal the entry transcript; require all fixed historical, image, record, lease, and release hashes; require the four absent failed-run closure files still absent; require no new A11 run/image/cache/lease/container/receipt/checkpoint/audit identity. Require the canonical worktree clean and the linked worktree dirty only at the two allowlisted candidate paths.

- [ ] **Step 5: Fix only evidenced findings and rerun every affected RED/GREEN and full gate**

For each Critical or Important finding, first add a focused failing test and observe the expected failure. Make the minimal launcher change, observe GREEN, then repeat Steps 1–4. A third path or a required runtime invocation stops for owner review.

- [ ] **Step 6: Create the one append-only implementation commit**

Require every gate above to have fresh passing evidence, then:

```powershell
$env:GIT_AUTHOR_NAME = 'kuotunyu'
$env:GIT_AUTHOR_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
$env:GIT_COMMITTER_NAME = 'kuotunyu'
$env:GIT_COMMITTER_EMAIL = '61350295+kuotunyu@users.noreply.github.com'
git add -- scripts/run_wave0_a11.ps1 tests/gates/test_wave0_a11_launcher.py
$Staged = @(git diff --cached --name-only)
if ($Staged.Count -ne 2 -or $Staged[0] -cnotin @('scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py') -or $Staged[1] -cnotin @('scripts/run_wave0_a11.ps1','tests/gates/test_wave0_a11_launcher.py')) { throw 'staged scope mismatch' }
git diff --cached --check
git commit -m 'fix: recover A11 launcher failure closure'
```

- [ ] **Step 7: Verify the committed candidate and stop before runtime**

Require the implementation commit's direct parent to be this plan commit; require exact author/committer identity; require its diff to contain exactly the two allowlisted paths; require both worktrees clean; repeat parser and focused launcher tests from the committed tree. Report design, plan, and implementation SHAs, test counts, static/parser results, preservation evidence, and Critical=0/Important=0 review.

Do not invoke `scripts/run_wave0_a11.ps1`. Do not reuse `OWNER-A11-RUNTIME-20260828-01`. A future attempt remains owner-review-required and must use fresh run, image, cache, lease, container, receipt, checkpoint, timestamp, audit, and authorization identities.
