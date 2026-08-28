"""PowerShell adapter tests for the Wave 0 A11 two-phase launcher."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "run_wave0_a11.ps1"
_SOURCE = "1" * 40
_SPEC = "b59b0d4407b98b460f6166ea7288ba6021dc7a78"
_PLAN = "2" * 40
_BRANCH = "codex/wave0-model-contract"
_OWNER = "OWNER-A11-TEST"
_BASE = "sha256:8aef630a54bc5c5146ae5ce68e6af5caa3df0fb690bb91544175c91f307e4356"
_GPU = "GPU-7639cc81-2a55-164e-e5be-c5cd71752a63"
_HISTORICAL_FILES_SHA256 = (
    "e1ff7a7d7ede1ae479f9525d35cedece14949d64991c9acf6cc6b11bcf1fba95"
)
_HISTORICAL_IMAGES_SHA256 = (
    "9a41d2c8e277f230400187874547b33ea0d9a3376707b46da4f267ee0cb3231f"
)
_FAILED_RUN_ID = "wave0-a11-calibration-20260828T045848083Z-b9917463"
_FAILED_RUN_SHA256 = "fb6009c0618b8a520c217c627ceab906bef8952cc7270d9e7928dd815896479b"
_FAILED_OWNER = "OWNER-A11-RUNTIME-20260828-01"
_FAILED_IMAGE_TAG = (
    "vision-active-learning-loop:wave0-a11-calibration-"
    "2622e402e4f5-20260828T045848083Z-b9917463"
)
_FAILED_IMAGE_ID = (
    "sha256:52b62e99d65269649d1e75e7397e9cab" "7d20cc5fe0e5dc46d661b1ec6625b0d5"
)


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
        "lease_names": [
            f"{_FAILED_RUN_ID}.release.json",
            f"{_FAILED_RUN_ID}.released",
        ],
        "links_absent": True,
    }


def _ps(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _invoke_functions(
    names: tuple[str, ...], body: str
) -> subprocess.CompletedProcess[str]:
    if not _SCRIPT.is_file():
        raise AssertionError("production A11 launcher script is missing")
    requested = ",".join(_ps(name) for name in names)
    script = f"""
$ErrorActionPreference = 'Stop'
$Tokens = $null
$Errors = $null
$Ast = [Management.Automation.Language.Parser]::ParseFile(
    {_ps(str(_SCRIPT))}, [ref]$Tokens, [ref]$Errors
)
if ($Errors.Count -ne 0) {{ throw ($Errors | ForEach-Object Message) -join '; ' }}
foreach ($FunctionName in @({requested})) {{
    $Matches = @($Ast.FindAll({{
        param($Node)
        $Node -is [Management.Automation.Language.FunctionDefinitionAst] -and
            $Node.Name -eq $FunctionName
    }}, $true))
    if ($Matches.Count -ne 1) {{ throw "function AST mismatch: $FunctionName" }}
    Invoke-Expression $Matches[0].Extent.Text
}}
{body}
"""
    return subprocess.run(
        ["pwsh", "-NoProfile", "-NonInteractive", "-Command", script],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )


def _file_record(path: Path) -> dict[str, object]:
    content = path.read_bytes()
    return {
        "path": path.resolve().as_posix(),
        "size": len(content),
        "sha256": hashlib.sha256(content).hexdigest(),
    }


def _stage_receipt(
    run_id: str, *, status: str = "PASS", errors: list[str] | None = None
) -> dict[str, object]:
    return {
        "schema_version": 1,
        "metadata": {"run_id": run_id},
        "normative": {
            "status": status,
            "errors": [] if errors is None else errors,
        },
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


def _run_cache_stream_contract(
    tmp_path: Path, stdout: str
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    cache = campaign / "wave0" / "model_cache"
    audit.mkdir(parents=True)
    cache.mkdir(parents=True)
    (cache / "config.json").write_text("cache", encoding="utf-8")
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(cache))}; run_id='wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64); audit_records=[ordered]@{{}}
    cache_inventory_sha256=$null
}}
function Invoke-A11Native {{
    return [pscustomobject]@{{ ExitCode=0; Stdout={_ps(stdout)}; Stderr='' }}
}}
Invoke-A11CachePreflight -Identity $Identity -Worktree 'D:/repo' |
    ConvertTo-Json -Depth 8 -Compress
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11JsonSha256",
            "New-A11CachePreflightArguments",
            "Get-A11CacheInventorySha256",
            "Invoke-A11CachePreflight",
        ),
        body,
    )


def _run_replica_stream_contract(
    tmp_path: Path, stdout: str
) -> subprocess.CompletedProcess[str]:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    cache = campaign / "wave0" / "model_cache"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    cache.mkdir(parents=True)
    model_contract = receipts / "model-contract.json"
    model_contract.write_text(
        json.dumps(_stage_receipt("wave0-a11-calibration-test")),
        encoding="utf-8",
    )
    model_record = _file_record(model_contract)
    replica_receipt = receipts / "calibration-00.json"
    checkpoint = campaign / "wave0" / "checkpoints" / "calibration-00" / "step.pt"
    cid = audit / "calibration-00.cid"
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(cache))}; run_id='wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64)
    replica_records=[Collections.Generic.List[object]]::new()
    foundation_receipts=[ordered]@{{
        model_contract=({_ps(json.dumps(model_record))} | ConvertFrom-Json)
    }}
}}
function Invoke-A11Native {{
    [IO.Directory]::CreateDirectory({_ps(str(checkpoint.parent))}) | Out-Null
    [IO.File]::WriteAllText({_ps(str(checkpoint))}, 'checkpoint')
    [IO.File]::WriteAllText(
        {_ps(str(replica_receipt))},
        '{{"metadata":{{"timestamp":"2026-08-28T00:00:00Z"}}}}'
    )
    [IO.File]::WriteAllText({_ps(str(cid))}, ('a' * 64))
    return [pscustomobject]@{{ ExitCode=0; Stdout={_ps(stdout)}; Stderr='' }}
}}
Invoke-A11Replica -Identity $Identity -ReplicaId 'calibration-00'
"""
    return _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "New-A11ReplicaValArguments",
            "New-A11ReplicaArguments",
            "Invoke-A11Replica",
        ),
        body,
    )


def _preflight() -> dict[str, object]:
    return {
        "worktree_path": "D:/repo/.worktrees/a11",
        "git_dir": "D:/repo/.git/worktrees/a11",
        "common_dir": "D:/repo/.git",
        "linked_worktree": True,
        "branch": _BRANCH,
        "head": _SOURCE,
        "spec_commit": _SPEC,
        "plan_commit": _PLAN,
        "plan_parent_is_spec": True,
        "linked_status": "",
        "canonical_status": "",
        "val_data_root_present": False,
        "docker_context": "desktop-linux",
        "docker_os": "linux",
        "docker_server_version": "29.6.1",
        "gpu_rows": [
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": _GPU,
                "compute_process_count": 0,
            }
        ],
        "project_containers": [],
        "active_leases": [],
        "prior_a11_attempt": _prior_attempt(),
        "historical_file_count": 64306,
        "historical_image_count": 21,
        "historical_file_inventory_sha256": _HISTORICAL_FILES_SHA256,
        "historical_image_inventory_sha256": _HISTORICAL_IMAGES_SHA256,
        "historical_preserved": True,
    }


def _preflight_body(evidence: dict[str, object], *, owner: str = _OWNER) -> str:
    return f"""
$Result = Test-A11ReadOnlyPreflight `
    -EvidenceJson {_ps(json.dumps(evidence))} `
    -ExpectedSourceCommit {_ps(_SOURCE)} `
    -ExpectedSpecCommit {_ps(_SPEC)} `
    -ExpectedPlanCommit {_ps(_PLAN)} `
    -ExpectedBranch {_ps(_BRANCH)} `
    -OwnerAuthorizationId {_ps(owner)}
$Result | ConvertTo-Json -Depth 8 -Compress
"""


def _run_prior_attempt_inventory(
    tmp_path: Path, defect: str = ""
) -> tuple[subprocess.CompletedProcess[str], Path, Path]:
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
    (run_root / "payload.bin").write_bytes(b"payload")
    (lease_root / f"{_FAILED_RUN_ID}.released").write_text("released", encoding="utf-8")
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
    return [pscustomobject]@{{
        ExitCode=0;Stdout={_ps(_FAILED_IMAGE_TAG + chr(10))};Stderr=''
    }}
}}
return [pscustomobject]@{{
    ExitCode=0
    Stdout={_ps(json.dumps([{'Id': _FAILED_IMAGE_ID}]))}
    Stderr=''
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
    return completed, run_root, lease_root


def _phase_destination_identities(tmp_path: Path) -> list[dict[str, str]]:
    lease_lock = tmp_path / "leases" / f"{_GPU}.json"
    return [
        {
            "phase": "calibration",
            "run_id": "wave0-a11-calibration-20260828T010101001Z-aaaaaaaa",
            "image_tag": "vision-active-learning-loop:wave0-a11-calibration-a",
            "campaign_root": str(tmp_path / "calibration"),
            "cache_root": str(tmp_path / "calibration" / "wave0" / "model_cache"),
            "lease_id": ("wave0-a11-calibration-lease-20260828T010101001Z-aaaaaaaa"),
            "lease_path": str(tmp_path / "calibration" / "audit" / "active-lease.json"),
            "lease_lock_path": str(lease_lock),
        },
        {
            "phase": "validation",
            "run_id": "wave0-a11-validation-20260828T010101002Z-bbbbbbbb",
            "image_tag": "vision-active-learning-loop:wave0-a11-validation-b",
            "campaign_root": str(tmp_path / "validation"),
            "cache_root": str(tmp_path / "validation" / "wave0" / "model_cache"),
            "lease_id": ("wave0-a11-validation-lease-20260828T010101002Z-bbbbbbbb"),
            "lease_path": str(tmp_path / "validation" / "audit" / "active-lease.json"),
            "lease_lock_path": str(lease_lock),
        },
    ]


def _run_phase_destination_gate(
    identities: list[dict[str, str]],
    *,
    exit_code: int = 0,
    stdout: str = "",
    stderr: str = "",
    setup: str = "",
    present_only: str | None = None,
) -> subprocess.CompletedProcess[str]:
    boundary = (
        ""
        if present_only is None
        else f"""
function Test-A11PathEntryPresent {{
    param($Path)
    return [IO.Path]::GetFullPath($Path) -ceq `
        [IO.Path]::GetFullPath({_ps(present_only)})
}}
"""
    )
    body = f"""
{setup}
{boundary}
function Invoke-A11Native {{
    return [pscustomobject]@{{
        ExitCode={exit_code}; Stdout={_ps(stdout)}; Stderr={_ps(stderr)}
    }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent -Identities $Identities | Out-Null
"""
    return _invoke_functions(
        ("Test-A11PathEntryPresent", "Test-A11PhaseDestinationsAbsent"), body
    )


def _run_initialize_phase(
    tmp_path: Path,
    *,
    parent_kind: str = "directory",
    child_exists: bool = False,
) -> tuple[subprocess.CompletedProcess[str], Path, Path, Path]:
    artifact = tmp_path / "artifacts"
    parent = artifact / "a11-runs"
    target = tmp_path / "junction-target"
    junction_setup = ""
    if parent_kind == "directory":
        (parent / "prior").mkdir(parents=True)
        sentinel = parent / "prior" / "sentinel.bin"
    elif parent_kind == "file":
        artifact.mkdir(parents=True)
        sentinel = parent
    elif parent_kind == "junction":
        artifact.mkdir(parents=True)
        (target / "prior").mkdir(parents=True)
        sentinel = target / "prior" / "sentinel.bin"
        junction_setup = (
            f"New-Item -ItemType Junction -Path {_ps(str(parent))} "
            f"-Target {_ps(str(target))} | Out-Null"
        )
    else:
        raise AssertionError(f"unsupported parent kind: {parent_kind}")
    sentinel.write_bytes(b"immutable-prior")

    new_root = parent / "wave0-a11-calibration-20260828T010101001Z-aaaaaaaa"
    peer_root = parent / "wave0-a11-validation-20260828T010101002Z-bbbbbbbb"
    if child_exists:
        new_root.mkdir(parents=True)
        sentinel = new_root / "sentinel.bin"
        sentinel.write_bytes(b"immutable-child")
    body = f"""
{junction_setup}
function nvidia-smi {{
    $FlatArgs = @($args | ForEach-Object {{ $_ }})
    if (($FlatArgs -join ' ') -like '*--query-gpu=name uuid driver_version*') {{
        return 'NVIDIA GeForce RTX 4090, {_GPU}, 591.86'
    }}
    return ''
}}
$Identity = New-A11PhaseIdentity `
    -Phase calibration -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(artifact))} `
    -TimestampToken '20260828T010101001Z' -Nonce 'aaaaaaaa'
$Peer = New-A11PhaseIdentity `
    -Phase validation -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(artifact))} `
    -TimestampToken '20260828T010101002Z' -Nonce 'bbbbbbbb'
Initialize-A11Phase -Identity $Identity -Peer $Peer | Out-Null
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "ConvertTo-A11GpuRows",
            "New-A11PhaseIdentity",
            "Initialize-A11Phase",
        ),
        body,
    )
    return completed, new_root, peer_root, sentinel


def test_launcher_has_exact_parameters_and_required_functions() -> None:
    source = _SCRIPT.read_text(encoding="utf-8")
    expected_parameters = (
        "ExpectedSourceCommit",
        "ExpectedSpecCommit",
        "ExpectedPlanCommit",
        "ExpectedBranch",
        "OwnerAuthorizationId",
    )
    parameter_section = source[source.index("param(") : source.index(")\n\n")]
    for name in expected_parameters:
        assert parameter_section.count(f"${name}") == 1
    for name in (
        "Resolve-A11Worktree",
        "Get-A11ActiveLeasePaths",
        "Test-A11ReadOnlyPreflight",
        "Confirm-A11ProtectedGit",
        "New-A11PhaseIdentity",
        "Get-A11PriorAttemptInventory",
        "Test-A11PathEntryPresent",
        "Test-A11PhaseDestinationsAbsent",
        "New-A11BuildArguments",
        "Invoke-A11CachePreflight",
        "Get-A11VerifiedStageReceipt",
        "Assert-A11FileRecordUnchanged",
        "New-A11ReplicaValArguments",
        "New-A11Lease",
        "Invoke-A11Replica",
        "New-A11GateArguments",
        "Invoke-A11Gate",
        "Confirm-A11CalibrationReceipt",
        "Release-A11Lease",
        "Confirm-A11Release",
        "Close-A11Phase",
        "Test-A11CrossPhaseIdentity",
        "Get-A11SingleCampaignResult",
        "Invoke-A11Campaign",
    ):
        assert source.count(f"function {name}") == 1
    assert source.count("ConvertTo-A11GpuRows") == 3
    assert (
        source.count("--query-compute-apps=gpu_uuid,pid,process_name,used_gpu_memory")
        == 2
    )
    assert source.count("'CUBLAS_WORKSPACE_CONFIG=:4096:8'") == 2
    assert "OwnerAuthorizationId =" not in source
    assert "gate wave1" not in source.lower()


def test_write_a11_new_text_is_true_no_clobber_and_preserves_empty_bytes(
    tmp_path: Path,
) -> None:
    output = tmp_path / "audit.log"
    body = f"""
Write-A11NewText -Path {_ps(str(output))} -Text ''
try {{
    Write-A11NewText -Path {_ps(str(output))} -Text 'replacement'
    throw 'second write unexpectedly succeeded'
}} catch [System.IO.IOException] {{}}
[IO.File]::ReadAllBytes({_ps(str(output))}).Length
"""
    completed = _invoke_functions(("Write-A11NewText",), body)

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "0"
    assert output.read_bytes() == b""


@pytest.mark.parametrize(
    ("name", "stdout", "receipt_name"),
    [
        ("30-environment", "", "environment.json"),
        ("31-model-assets", "PASS\n", "model-assets.json"),
        ("32-model-contract", "PASS\n", "model-contract.json"),
    ],
)
def test_foundation_stages_enforce_registered_stream_and_receipt_contracts(
    tmp_path: Path, name: str, stdout: str, receipt_name: str
) -> None:
    completed = _run_foundation_stage(
        tmp_path,
        name=name,
        stdout=stdout,
        expected_stdout=stdout,
        receipt_name=receipt_name,
        receipt=_stage_receipt("wave0-a11-calibration-test"),
    )

    assert completed.returncode == 0, completed.stderr
    receipt_path = tmp_path / "campaign" / "wave0" / "receipts" / receipt_name
    expected_record = _file_record(receipt_path)
    assert json.loads(completed.stdout) == expected_record
    audit_path = tmp_path / "campaign" / "audit" / f"{name}.json"
    audit = json.loads(audit_path.read_text(encoding="utf-8"))
    assert audit["receipt"] == expected_record


def test_process_audit_omits_receipt_when_no_receipt_is_bound(
    tmp_path: Path,
) -> None:
    audit = tmp_path / "audit"
    audit.mkdir()
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(tmp_path))}
}}
$Result = [pscustomobject]@{{ ExitCode=0; Stdout=''; Stderr='' }}
Write-A11ProcessAudit -Identity $Identity -Name '10-build' `
    -Argv @('docker','build') -Result $Result | Out-Null
Get-Content -Raw -LiteralPath {_ps(str(audit / '10-build.json'))}
"""
    completed = _invoke_functions(
        ("Write-A11NewText", "Get-A11FileRecord", "Write-A11ProcessAudit"),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    document = json.loads(completed.stdout)
    assert "receipt" not in document


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


@pytest.mark.parametrize(
    "defect", ["missing", "junction", "outside", "wrong-run", "fail", "errors"]
)
def test_foundation_stage_rejects_untrusted_receipt(
    tmp_path: Path, defect: str
) -> None:
    receipt = {
        "missing": None,
        "wrong-run": _stage_receipt("wrong-run"),
        "fail": _stage_receipt("wave0-a11-calibration-test", status="FAIL"),
        "errors": _stage_receipt("wave0-a11-calibration-test", errors=["injected"]),
    }.get(defect, _stage_receipt("wave0-a11-calibration-test"))

    completed = _run_untrusted_receipt_case(tmp_path, defect=defect, receipt=receipt)

    assert completed.returncode != 0
    assert completed.stderr


def test_foundation_rehashes_environment_and_assets_before_model_contract(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    environment = receipts / "environment.json"
    assets = receipts / "model-assets.json"
    model_contract = receipts / "model-contract.json"
    for path in (environment, assets, model_contract):
        path.write_text(
            json.dumps(_stage_receipt("wave0-a11-calibration-test")),
            encoding="utf-8",
        )
    body = f"""
$script:Calls = 0
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    audit_records=[ordered]@{{}}; foundation_receipts=[ordered]@{{}}
}}
function Invoke-A11Native {{
    $script:Calls++
    if ($script:Calls -eq 2) {{
        [IO.File]::AppendAllText({_ps(str(environment))}, ' ')
    }}
    $Stdout = if ($script:Calls -eq 1) {{ '' }} else {{ "PASS`n" }}
    return [pscustomobject]@{{ ExitCode=0; Stdout=$Stdout; Stderr='' }}
}}
try {{
    Invoke-A11Foundation -Identity $Identity
    throw 'foundation unexpectedly succeeded'
}} catch {{
    [ordered]@{{ calls=$script:Calls; error=$_.Exception.Message }} |
        ConvertTo-Json -Compress
}}
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "Write-A11ProcessAudit",
            "Invoke-A11DockerStage",
            "Invoke-A11Foundation",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result["calls"] == 2
    assert "changed" in result["error"]


def test_replica_rehashes_model_contract_before_native_launch(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    receipts = campaign / "wave0" / "receipts"
    audit.mkdir(parents=True)
    receipts.mkdir(parents=True)
    model_contract = receipts / "model-contract.json"
    original = _stage_receipt("wave0-a11-calibration-test")
    model_contract.write_text(json.dumps(original), encoding="utf-8")
    expected = _file_record(model_contract)
    model_contract.write_text(
        json.dumps({**original, "mutated": True}), encoding="utf-8"
    )
    body = f"""
$script:Calls = 0
$Identity = [pscustomobject]@{{
    phase='calibration'; campaign_root={_ps(str(campaign))}
    cache_root={_ps(str(campaign / 'wave0' / 'model_cache'))}
    run_id='wave0-a11-calibration-test'; image_id='sha256:' + ('a' * 64)
    replica_records=[Collections.Generic.List[object]]::new()
    foundation_receipts=[ordered]@{{
        model_contract=({_ps(json.dumps(expected))} | ConvertFrom-Json)
    }}
}}
function Invoke-A11Native {{
    $script:Calls++
    return [pscustomobject]@{{ ExitCode=0; Stdout="PASS`n"; Stderr='' }}
}}
try {{
    Invoke-A11Replica -Identity $Identity -ReplicaId 'calibration-00'
    throw 'replica unexpectedly succeeded'
}} catch {{
    [ordered]@{{ calls=$script:Calls; error=$_.Exception.Message }} |
        ConvertTo-Json -Compress
}}
"""
    completed = _invoke_functions(
        (
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
            "New-A11ReplicaValArguments",
            "New-A11ReplicaArguments",
            "Invoke-A11Replica",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    assert result == {
        "calls": 0,
        "error": f"A11 verified receipt changed before use: {model_contract}",
    }


def test_dependent_use_rejects_identical_receipt_through_new_junction(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    receipts = campaign / "wave0" / "receipts"
    outside = tmp_path / "outside"
    receipts.mkdir(parents=True)
    outside.mkdir()
    receipt = receipts / "model-contract.json"
    content = json.dumps(_stage_receipt("wave0-a11-calibration-test"))
    receipt.write_text(content, encoding="utf-8")
    expected = _file_record(receipt)
    receipt.unlink()
    receipts.rmdir()
    (outside / "model-contract.json").write_text(content, encoding="utf-8")
    body = f"""
New-Item -ItemType Junction -Path {_ps(str(receipts))} `
    -Target {_ps(str(outside))} | Out-Null
$Identity = [pscustomobject]@{{
    campaign_root={_ps(str(campaign))}; run_id='wave0-a11-calibration-test'
}}
$Expected = {_ps(json.dumps(expected))} | ConvertFrom-Json
try {{
    Assert-A11FileRecordUnchanged -Identity $Identity `
        -Expected $Expected -Path {_ps(str(receipt))} | Out-Null
    throw 'junction unexpectedly accepted'
}} catch {{
    $_.Exception.Message
}}
"""
    completed = _invoke_functions(
        (
            "Get-A11FileRecord",
            "Get-A11VerifiedStageReceipt",
            "Assert-A11FileRecordUnchanged",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    assert "link" in completed.stdout.lower()


@pytest.mark.parametrize("component", ["cache", "replica"])
@pytest.mark.parametrize(
    ("stdout", "accepted"),
    [
        ("PASS\n", True),
        ("", False),
        ("PASS", False),
        ("PASS\r\n", False),
        ("PASS\nextra\n", False),
    ],
)
def test_cache_preflight_and_replica_keep_exact_pass_stream_contracts(
    tmp_path: Path, component: str, stdout: str, accepted: bool
) -> None:
    run = (
        _run_cache_stream_contract
        if component == "cache"
        else _run_replica_stream_contract
    )
    completed = run(tmp_path, stdout)

    if accepted:
        assert completed.returncode == 0, completed.stderr
    else:
        assert completed.returncode != 0
        assert completed.stderr


def test_read_only_preflight_accepts_exact_closed_evidence() -> None:
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(_preflight())
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["head"] == _SOURCE


def test_read_only_preflight_rejects_registered_prior_authorization() -> None:
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",),
        _preflight_body(_preflight(), owner=_FAILED_OWNER),
    )

    assert completed.returncode != 0
    assert "prior owner authorization" in completed.stderr


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
        (
            "image_tags",
            [
                _FAILED_IMAGE_TAG,
                "vision-active-learning-loop:wave0-a11-extra",
            ],
        ),
        ("image_id", "sha256:" + "0" * 64),
        ("lease_names", []),
        (
            "lease_names",
            [f"{_FAILED_RUN_ID}.released", "wave0-a11-extra.released"],
        ),
        ("links_absent", False),
    ],
)
def test_read_only_preflight_rejects_prior_a11_drift(field: str, value: object) -> None:
    evidence = _preflight()
    prior = dict(evidence["prior_a11_attempt"])
    prior[field] = value
    evidence["prior_a11_attempt"] = prior

    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0
    assert "prior A11" in completed.stderr


def test_gpu_inventory_ignores_wddm_na_rows_but_counts_numeric_cuda() -> None:
    body = f"""
$Rows = ConvertTo-A11GpuRows `
    -GpuCsv 'NVIDIA GeForce RTX 4090, {_GPU}' `
    -ComputeCsv @'
{_GPU}, 1096, Desktop Window Manager, [N/A]
{_GPU}, 4321, python.exe, 2048
'@
$Rows | ConvertTo-Json -Depth 4 -Compress
"""
    completed = _invoke_functions(("ConvertTo-A11GpuRows",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == {
        "name": "NVIDIA GeForce RTX 4090",
        "uuid": _GPU,
        "compute_process_count": 1,
    }


def test_gpu_inventory_rejects_unknown_memory_state() -> None:
    body = f"""
ConvertTo-A11GpuRows `
    -GpuCsv 'NVIDIA GeForce RTX 4090, {_GPU}' `
    -ComputeCsv '{_GPU}, 1096, Desktop Window Manager, unknown'
"""
    completed = _invoke_functions(("ConvertTo-A11GpuRows",), body)

    assert completed.returncode != 0
    assert "memory state" in completed.stderr


def test_active_lease_inventory_excludes_release_evidence(tmp_path: Path) -> None:
    active = tmp_path / f"{_GPU}.json"
    release = tmp_path / f"{_GPU}.json.release.json"
    released = tmp_path / f"{_GPU}.json.released"
    for path in (active, release, released):
        path.write_text("{}", encoding="utf-8")
    body = f"""
Get-A11ActiveLeasePaths -LeaseRoot {_ps(str(tmp_path))} |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("Get-A11ActiveLeasePaths",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == active.resolve().as_posix()

    active.unlink()
    without_active = _invoke_functions(("Get-A11ActiveLeasePaths",), body)
    assert without_active.returncode == 0, without_active.stderr
    assert without_active.stdout.strip() == ""


def test_prior_attempt_inventory_returns_closed_sorted_evidence(
    tmp_path: Path,
) -> None:
    completed, run_root, lease_root = _run_prior_attempt_inventory(tmp_path)

    assert completed.returncode == 0, completed.stderr
    evidence = json.loads(completed.stdout)
    records = []
    for path in sorted(run_root.rglob("*")):
        if path.is_file():
            content = path.read_bytes()
            records.append(
                {
                    "path": path.relative_to(run_root).as_posix(),
                    "size": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    expected_digest = hashlib.sha256(
        json.dumps(records, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    assert evidence == {
        "run_names": [_FAILED_RUN_ID],
        "run_file_count": len(records),
        "run_inventory_sha256": expected_digest,
        "historical_preservation_sha256": hashlib.sha256(b"history").hexdigest(),
        "released_lease_sha256": hashlib.sha256(b"released").hexdigest(),
        "release_record_sha256": hashlib.sha256(b"release").hexdigest(),
        "closure_paths_present": [],
        "image_tags": [_FAILED_IMAGE_TAG],
        "image_id": _FAILED_IMAGE_ID,
        "lease_names": sorted(path.name for path in lease_root.iterdir()),
        "links_absent": True,
    }


@pytest.mark.parametrize("defect", ["run-link", "lease-link", "docker-failure"])
def test_prior_attempt_inventory_rejects_links_or_docker_failure(
    tmp_path: Path, defect: str
) -> None:
    completed, _, _ = _run_prior_attempt_inventory(tmp_path, defect)

    assert completed.returncode != 0
    assert completed.stderr


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("linked_worktree", False),
        ("branch", "main"),
        ("head", "f" * 40),
        ("plan_parent_is_spec", False),
        ("linked_status", " M file"),
        ("canonical_status", "?? other"),
        ("val_data_root_present", True),
        ("docker_context", "default"),
        ("docker_os", "windows"),
        ("docker_server_version", ""),
        ("project_containers", ["running"]),
        ("active_leases", ["active.json"]),
        ("historical_file_count", 64305),
        ("historical_image_count", 20),
        ("historical_file_inventory_sha256", "0" * 64),
        ("historical_image_inventory_sha256", "0" * 64),
        ("historical_preserved", False),
    ],
)
def test_read_only_preflight_rejects_identity_contention_or_drift(
    field: str, value: object
) -> None:
    evidence = _preflight()
    evidence[field] = value

    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0
    assert completed.stderr


@pytest.mark.parametrize(
    "gpu_rows",
    [
        [],
        [
            {
                "name": "NVIDIA GeForce RTX 3090",
                "uuid": _GPU,
                "compute_process_count": 0,
            }
        ],
        [
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": _GPU,
                "compute_process_count": 1,
            }
        ],
        [
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": _GPU,
                "compute_process_count": 0,
            },
            {
                "name": "NVIDIA GeForce RTX 4090",
                "uuid": "GPU-other",
                "compute_process_count": 0,
            },
        ],
    ],
)
def test_read_only_preflight_requires_one_idle_registered_rtx4090(
    gpu_rows: list[dict[str, object]],
) -> None:
    evidence = _preflight()
    evidence["gpu_rows"] = gpu_rows
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(evidence)
    )

    assert completed.returncode != 0


def test_phase_identities_are_preregistered_and_fully_distinct(tmp_path: Path) -> None:
    body = f"""
$Calibration = New-A11PhaseIdentity `
    -Phase calibration -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(tmp_path))} `
    -TimestampToken '20260828T010101001Z' -Nonce 'aaaaaaaa'
$Validation = New-A11PhaseIdentity `
    -Phase validation -SourceCommit {_ps(_SOURCE)} `
    -SpecCommit {_ps(_SPEC)} -PlanCommit {_ps(_PLAN)} `
    -OwnerAuthorizationId {_ps(_OWNER)} -ArtifactRoot {_ps(str(tmp_path))} `
    -TimestampToken '20260828T010101002Z' -Nonce 'bbbbbbbb'
@{{ calibration = $Calibration; validation = $Validation }} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("New-A11PhaseIdentity",), body)

    assert completed.returncode == 0, completed.stderr
    identities = json.loads(completed.stdout)
    calibration = identities["calibration"]
    validation = identities["validation"]
    for name in (
        "run_id",
        "image_tag",
        "campaign_root",
        "cache_root",
        "lease_id",
        "lease_path",
    ):
        assert calibration[name] != validation[name]
    assert calibration["lease_lock_path"] == validation["lease_lock_path"]
    assert calibration["cache_root"].endswith("wave0\\model_cache")
    assert calibration["source_commit"] == validation["source_commit"] == _SOURCE
    assert calibration["owner_authorization_id"] == _OWNER


def test_phase_destination_gate_accepts_two_fresh_identities(
    tmp_path: Path,
) -> None:
    completed = _run_phase_destination_gate(_phase_destination_identities(tmp_path))

    assert completed.returncode == 0, completed.stderr


@pytest.mark.parametrize(
    "field",
    ["run_id", "image_tag", "campaign_root", "cache_root", "lease_id", "lease_path"],
)
def test_phase_destination_gate_rejects_cross_phase_identity_reuse(
    tmp_path: Path, field: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    identities[1][field] = identities[0][field]

    completed = _run_phase_destination_gate(identities)

    assert completed.returncode != 0
    assert field in completed.stderr


@pytest.mark.parametrize(
    "collision",
    [
        "calibration-root",
        "validation-root",
        "calibration-cache-root",
        "validation-lease-path",
        "lease-lock",
        "calibration-released",
        "validation-release-record",
    ],
)
def test_phase_destination_gate_rejects_exact_path_collision(
    tmp_path: Path, collision: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    paths = {
        "calibration-root": Path(identities[0]["campaign_root"]),
        "validation-root": Path(identities[1]["campaign_root"]),
        "calibration-cache-root": Path(identities[0]["cache_root"]),
        "validation-lease-path": Path(identities[1]["lease_path"]),
        "lease-lock": Path(identities[0]["lease_lock_path"]),
        "calibration-released": (
            Path(identities[0]["lease_lock_path"]).parent
            / f"{identities[0]['run_id']}.released"
        ),
        "validation-release-record": (
            Path(identities[1]["lease_lock_path"]).parent
            / f"{identities[1]['run_id']}.release.json"
        ),
    }
    path = paths[collision]
    target_specific = collision in {"calibration-cache-root", "validation-lease-path"}
    if not target_specific:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.mkdir() if collision.endswith("root") else path.write_text(
            "occupied", encoding="utf-8"
        )

    completed = _run_phase_destination_gate(
        identities, present_only=str(path) if target_specific else None
    )

    assert completed.returncode != 0
    assert "fresh runtime destination exists" in completed.stderr
    assert str(path) in completed.stderr


@pytest.mark.parametrize("reused_token", ["timestamp", "nonce"])
def test_phase_destination_gate_rejects_timestamp_or_nonce_reuse(
    tmp_path: Path, reused_token: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    if reused_token == "timestamp":
        identities[1]["run_id"] = "wave0-a11-validation-20260828T010101001Z-bbbbbbbb"
    else:
        identities[1]["run_id"] = "wave0-a11-validation-20260828T010101002Z-aaaaaaaa"

    completed = _run_phase_destination_gate(identities)

    assert completed.returncode != 0
    assert "timestamp or nonce is reused" in completed.stderr


def test_phase_destination_gate_queries_each_exact_phase_image_tag(
    tmp_path: Path,
) -> None:
    identities = _phase_destination_identities(tmp_path)
    body = f"""
$script:RequestedTags = [Collections.Generic.List[string]]::new()
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    $Reference = @($ArgumentList | Where-Object {{ $_ -like 'reference=*' }})
    if ($Reference.Count -ne 1) {{ throw 'unexpected Docker image query' }}
    [void]$script:RequestedTags.Add($Reference[0].Substring(10))
    return [pscustomobject]@{{ ExitCode=0; Stdout=''; Stderr='' }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent -Identities $Identities | Out-Null
$script:RequestedTags | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(
        ("Test-A11PathEntryPresent", "Test-A11PhaseDestinationsAbsent"), body
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) == [
        identities[0]["image_tag"],
        identities[1]["image_tag"],
    ]


def test_phase_destination_gate_rejects_validation_only_image_collision(
    tmp_path: Path,
) -> None:
    identities = _phase_destination_identities(tmp_path)
    validation_tag = identities[1]["image_tag"]
    body = f"""
function Invoke-A11Native {{
    param($FilePath, $ArgumentList)
    $Reference = @($ArgumentList | Where-Object {{ $_ -like 'reference=*' }})[0]
    $Tag = $Reference.Substring(10)
    $Stdout = if ($Tag -ceq {_ps(validation_tag)}) {{ "$Tag`n" }} else {{ '' }}
    return [pscustomobject]@{{ ExitCode=0; Stdout=$Stdout; Stderr='' }}
}}
$Identities = {_ps(json.dumps(identities))} | ConvertFrom-Json
Test-A11PhaseDestinationsAbsent -Identities $Identities | Out-Null
"""
    completed = _invoke_functions(
        ("Test-A11PathEntryPresent", "Test-A11PhaseDestinationsAbsent"), body
    )

    assert completed.returncode != 0
    assert validation_tag in completed.stderr


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
    completed = _run_phase_destination_gate(
        _phase_destination_identities(tmp_path),
        exit_code=exit_code,
        stdout=stdout,
        stderr=stderr,
    )

    assert (completed.returncode == 0) is accepted
    if not accepted:
        assert completed.stderr


@pytest.mark.parametrize("destination_kind", ["file", "directory"])
def test_phase_destination_gate_rejects_dangling_reparse_point(
    tmp_path: Path, destination_kind: str
) -> None:
    identities = _phase_destination_identities(tmp_path)
    if destination_kind == "file":
        destination = Path(identities[0]["lease_lock_path"])
        target = tmp_path / "file-target.bin"
        target.write_bytes(b"target")
        item_type = "SymbolicLink"
    else:
        destination = Path(identities[0]["campaign_root"])
        target = tmp_path / "directory-target"
        target.mkdir()
        item_type = "Junction"
    destination.parent.mkdir(parents=True, exist_ok=True)
    moved_target = target.with_name(f"{target.name}-moved")
    setup = f"""
New-Item -ItemType {item_type} -Path {_ps(str(destination))} `
    -Target {_ps(str(target))} | Out-Null
Move-Item -LiteralPath {_ps(str(target))} -Destination {_ps(str(moved_target))}
"""

    completed = _run_phase_destination_gate(identities, setup=setup)

    if destination_kind == "file" and (
        "Administrator privilege required" in completed.stderr
    ):
        pytest.skip("creating a Windows file symlink requires unavailable privilege")
    assert completed.returncode != 0
    assert "fresh runtime destination exists" in completed.stderr


def test_phase_destination_gate_does_not_trust_test_path_false_negative(
    tmp_path: Path,
) -> None:
    identities = _phase_destination_identities(tmp_path)
    destination = Path(identities[0]["lease_lock_path"])
    destination.parent.mkdir(parents=True)
    destination.write_bytes(b"occupied")
    setup = "function Test-Path { return $false }"

    completed = _run_phase_destination_gate(identities, setup=setup)

    assert completed.returncode != 0
    assert "fresh runtime destination exists" in completed.stderr


def test_initialize_calibration_accepts_existing_parent_and_preserves_prior(
    tmp_path: Path,
) -> None:
    completed, new_root, peer_root, sentinel = _run_initialize_phase(tmp_path)

    assert completed.returncode == 0, completed.stderr
    assert sentinel.read_bytes() == b"immutable-prior"
    assert new_root.is_dir()
    assert sorted(path.name for path in new_root.iterdir()) == ["audit", "wave0"]
    assert not peer_root.exists()


@pytest.mark.parametrize("parent_kind", ["file", "junction"])
def test_initialize_rejects_linked_or_non_directory_campaign_parent(
    tmp_path: Path, parent_kind: str
) -> None:
    completed, _new_root, _peer_root, sentinel = _run_initialize_phase(
        tmp_path, parent_kind=parent_kind
    )

    assert completed.returncode != 0
    assert "campaign parent is not a non-link directory" in completed.stderr
    assert sentinel.read_bytes() == b"immutable-prior"


def test_initialize_keeps_exact_campaign_child_no_clobber(tmp_path: Path) -> None:
    completed, _new_root, peer_root, sentinel = _run_initialize_phase(
        tmp_path, child_exists=True
    )

    assert completed.returncode != 0
    assert sentinel.read_bytes() == b"immutable-child"
    assert not peer_root.exists()


def test_build_arguments_have_exact_independent_labels() -> None:
    body = f"""
$Identity = [pscustomobject]@{{
    run_id = 'wave0-a11-calibration-20260828T010101001Z-aaaaaaaa'
    image_tag = 'vision-active-learning-loop:wave0-a11-calibration-test'
    source_commit = {_ps(_SOURCE)}
    specification_commit = {_ps(_SPEC)}
    plan_commit = {_ps(_PLAN)}
}}
New-A11BuildArguments -Identity $Identity -BaseDigest {_ps(_BASE)} |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11BuildArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:6] == [
        "build",
        "--no-cache",
        "--progress",
        "plain",
        "--file",
        "docker/wave0.Dockerfile",
    ]
    labels = [
        arguments[index + 1]
        for index, value in enumerate(arguments)
        if value == "--label"
    ]
    assert len(labels) == 5
    assert all(" " not in label for label in labels)
    assert arguments[-3:] == [
        "--tag",
        "vision-active-learning-loop:wave0-a11-calibration-test",
        ".",
    ]


def test_cache_preflight_arguments_are_networked_cpu_only() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'calibration'; campaign_root = 'D:/a11/calibration'
    cache_root = 'D:/a11/calibration/wave0/model_cache'; image_id = 'sha256:' + ('a' * 64)
    run_id = 'wave0-a11-calibration-test'
}
New-A11CachePreflightArguments -Identity $Identity -Worktree 'D:/repo' |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11CachePreflightArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:3] == ["run", "--rm", "--network"]
    assert arguments[3] == "bridge"
    assert "--gpus" not in arguments
    assert "--download" in arguments
    assert "VAL_ARTIFACT_ROOT=/a11/calibration" in arguments
    assert "/a11/calibration/wave0/model_cache" in arguments


def test_cache_inventory_digest_matches_python_canonical_json(tmp_path: Path) -> None:
    cache = tmp_path / "model_cache"
    (cache / "nested").mkdir(parents=True)
    metadata_parent = cache / "snapshot" / ".cache" / "huggingface" / "download"
    metadata_parent.mkdir(parents=True)
    (cache / "a.bin").write_bytes(b"alpha")
    (cache / "nested" / "b.bin").write_bytes(b"beta")
    (metadata_parent / "config.json.metadata").write_text(
        "a" * 40 + "\n" + "b" * 64 + "\n123.5\n", encoding="utf-8"
    )
    records = []
    for path in sorted(cache.rglob("*")):
        if path.is_file():
            relative = path.relative_to(cache).as_posix()
            if (
                relative.endswith(".metadata")
                and "/.cache/huggingface/download/" in f"/{relative}"
            ):
                lines = path.read_text(encoding="utf-8").splitlines()
                content = f"{lines[0]}\n{lines[1]}\n".encode()
            else:
                content = path.read_bytes()
            records.append(
                {
                    "path": relative,
                    "size": len(content),
                    "sha256": hashlib.sha256(content).hexdigest(),
                }
            )
    expected = hashlib.sha256(
        json.dumps(
            {"files": records},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    body = f"""
Get-A11CacheInventorySha256 -CacheRoot {_ps(str(cache))}
"""
    completed = _invoke_functions(("Get-A11CacheInventorySha256",), body)

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == expected

    (metadata_parent / "config.json.metadata").write_text(
        "a" * 40 + "\n" + "b" * 64 + "\n999.25\n", encoding="utf-8"
    )
    changed_timestamp = _invoke_functions(("Get-A11CacheInventorySha256",), body)
    assert changed_timestamp.returncode == 0, changed_timestamp.stderr
    assert changed_timestamp.stdout.strip() == expected


def test_replica_arguments_are_fresh_offline_gpu_processes() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'calibration'; campaign_root = 'D:/a11/calibration'
    cache_root = 'D:/a11/calibration/wave0/model_cache'; image_id = 'sha256:' + ('a' * 64)
    run_id = 'wave0-a11-calibration-test'
}
New-A11ReplicaArguments -Identity $Identity -Worktree 'D:/repo' `
    -ReplicaId 'calibration-00' `
    -ModelContractPath 'D:/a11/calibration/wave0/receipts/model-contract.json' `
    -ReceiptPath 'D:/a11/calibration/wave0/receipts/calibration-00.json' `
    -CheckpointRoot 'D:/a11/calibration/wave0/checkpoints/calibration-00' |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(
        ("New-A11ReplicaValArguments", "New-A11ReplicaArguments"), body
    )

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments[:7] == [
        "run",
        "--rm",
        "--gpus",
        "all",
        "--network",
        "none",
        "--workdir",
    ]
    assert "HF_HUB_OFFLINE=1" in arguments
    assert "TRANSFORMERS_OFFLINE=1" in arguments
    assert (
        "D:/a11/calibration/wave0/model_cache:/a11/calibration/wave0/model_cache:ro"
        in arguments
    )
    assert "D:/a11/calibration:/a11/calibration:rw" in arguments
    assert "sha256:" + "a" * 64 in arguments
    assert arguments.count("training-feasibility") == 1
    assert arguments[arguments.index("--cidfile") + 1].endswith("calibration-00.cid")


def test_replica_val_arguments_are_the_exact_container_argv() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'calibration'; campaign_root = 'D:/a11/calibration'
    run_id = 'wave0-a11-calibration-test'
}
New-A11ReplicaValArguments -Identity $Identity -ReplicaId 'calibration-00' |
    ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11ReplicaValArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    assert arguments == [
        "probe",
        "training-feasibility",
        "--model-contract",
        "/a11/calibration/wave0/receipts/model-contract.json",
        "--checkpoint-root",
        "/a11/calibration/wave0/checkpoints/calibration-00",
        "--run-id",
        "wave0-a11-calibration-test",
        "--output",
        "/a11/calibration/wave0/receipts/calibration-00.json",
    ]


def test_validation_gate_mount_precedes_image_and_preserves_command_order() -> None:
    body = """
$Identity = [pscustomobject]@{
    phase = 'validation'; campaign_root = 'D:/a11/validation'
    image_id = 'sha256:' + ('b' * 64)
}
New-A11GateArguments -Identity $Identity -Worktree 'D:/repo' `
    -CalibrationRoot 'D:/a11/calibration' | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("New-A11GateArguments",), body)

    assert completed.returncode == 0, completed.stderr
    arguments = json.loads(completed.stdout)
    image_index = arguments.index("sha256:" + "b" * 64)
    assert arguments.index("D:/a11/calibration:/a11/calibration:ro") < image_index
    assert arguments[image_index + 1 : image_index + 4] == [
        "gate",
        "statistical-replay",
        "validate",
    ]
    assert arguments[arguments.index("--phase-root") + 1] == "/a11/validation"
    assert (
        arguments[arguments.index("--calibration-receipt") + 1]
        == "/a11/calibration/wave0/receipts/statistical-replay-calibration.json"
    )


def test_gpu_lease_is_atomic_and_release_is_run_scoped(tmp_path: Path) -> None:
    lease_root = tmp_path / "leases"
    lease_root.mkdir()
    lease_path = lease_root / f"{_GPU}.json"
    released_path = lease_root / "wave0-a11-calibration-test.released"
    release_record = lease_root / "wave0-a11-calibration-test.release.json"
    body = f"""
$Identity = [pscustomobject]@{{
    phase = 'calibration'; run_id = 'wave0-a11-calibration-test'
    source_commit = {_ps(_SOURCE)}; image_id = 'sha256:' + ('a' * 64)
    image_tag = 'vision-active-learning-loop:wave0-a11-calibration-test'
    campaign_root = 'D:/a11/calibration'; cache_root = 'D:/a11/calibration/cache'
    lease_id = 'wave0-a11-calibration-lease-test'
}}
$Lease = New-A11Lease -Identity $Identity -GpuUuid {_ps(_GPU)} `
    -LeasePath {_ps(str(lease_path))}
$Release = Release-A11Lease -Identity $Identity `
    -ActivePath {_ps(str(lease_path))} `
    -ReleasedPath {_ps(str(released_path))} `
    -RecordPath {_ps(str(release_record))}
@{{ lease = $Lease; release = $Release }} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "New-A11Lease",
            "Release-A11Lease",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    assert not lease_path.exists()
    assert released_path.is_file()
    release = json.loads(release_record.read_text(encoding="utf-8"))
    assert release["original_lease_sha256"]
    assert release["run_id"] == "wave0-a11-calibration-test"


def _identity(phase: str) -> dict[str, object]:
    marker = "a" if phase == "calibration" else "b"
    return {
        "static": {
            "source": _SOURCE,
            "spec": _SPEC,
            "plan": _PLAN,
            "base": _BASE,
            "model": "model",
            "gpu": _GPU,
        },
        "runtime": {
            "run_id": f"wave0-a11-{phase}-{marker}",
            "image_tag": f"vision-active-learning-loop:wave0-a11-{phase}-{marker}",
            "image_id": "sha256:" + marker * 64,
            "campaign_root": f"D:/a11/{phase}",
            "cache_root": f"D:/a11/{phase}/cache",
            "lease_id": f"wave0-a11-{phase}-lease",
            "lease_path": f"D:/leases/{phase}.json",
            "container_ids": [marker * 64],
            "receipt_paths": [f"D:/a11/{phase}/receipt.json"],
            "receipt_hashes": [marker * 64],
            "checkpoint_paths": [f"D:/a11/{phase}/checkpoint.pt"],
            "checkpoint_hashes": [(marker.upper().lower()) * 64],
            "timestamps": [f"2026-08-28T0{1 if phase == 'calibration' else 2}:00:00Z"],
            "audit_paths": [f"D:/a11/{phase}/audit.json"],
        },
    }


def test_cross_phase_identity_accepts_equal_static_and_disjoint_runtime() -> None:
    body = f"""
$Calibration = {_ps(json.dumps(_identity('calibration')))} | ConvertFrom-Json
$Validation = {_ps(json.dumps(_identity('validation')))} | ConvertFrom-Json
Test-A11CrossPhaseIdentity -Calibration $Calibration -Validation $Validation |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Test-A11CrossPhaseIdentity",), body)

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["valid"] is True


def test_calibration_receipt_is_rehashed_and_identity_checked_before_validation(
    tmp_path: Path,
) -> None:
    receipt = tmp_path / "wave0" / "receipts" / "statistical-replay-calibration.json"
    receipt.parent.mkdir(parents=True)
    document = {
        "receipt_type": "statistical-replay-calibration",
        "schema_version": 1,
        "normative": {
            "phase": "calibration",
            "status": "RECORDED",
            "errors": [],
            "terminal": (
                "WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / " "WAVE1_FORBIDDEN"
            ),
            "threshold_inventory_sha256": "a" * 64,
        },
        "metadata": {
            "run_id": "wave0-a11-calibration-test",
            "source_commit": _SOURCE,
            "specification_commit": _SPEC,
            "plan_commit": _PLAN,
            "image_tag": "vision-active-learning-loop:wave0-a11-calibration-test",
            "image_id": "sha256:" + "b" * 64,
            "owner_authorization_id": _OWNER,
        },
    }
    receipt.write_text(json.dumps(document), encoding="utf-8")
    receipt_size = receipt.stat().st_size
    receipt_sha256 = hashlib.sha256(receipt.read_bytes()).hexdigest()
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; run_id='wave0-a11-calibration-test'
    campaign_root={_ps(str(tmp_path))}; source_commit={_ps(_SOURCE)}
    specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
    image_tag='vision-active-learning-loop:wave0-a11-calibration-test'
    image_id='sha256:' + ('b' * 64); owner_authorization_id={_ps(_OWNER)}
    aggregate_receipt=[pscustomobject]@{{
        path={_ps(receipt.resolve().as_posix())}; size={receipt_size}
        sha256={_ps(receipt_sha256)}
    }}
}}
Confirm-A11CalibrationReceipt -Identity $Identity `
    -OwnerAuthorizationId {_ps(_OWNER)} | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(
        ("Get-A11FileRecord", "Confirm-A11CalibrationReceipt"), body
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout) is True

    receipt.write_text(json.dumps({**document, "tampered": True}), encoding="utf-8")
    tampered = _invoke_functions(
        ("Get-A11FileRecord", "Confirm-A11CalibrationReceipt"), body
    )
    assert tampered.returncode != 0
    assert "changed" in tampered.stderr


def test_close_a11_phase_publishes_complete_bound_failure_chain(
    tmp_path: Path,
) -> None:
    campaign = tmp_path / "campaign"
    audit = campaign / "audit"
    audit.mkdir(parents=True)
    body = f"""
$Identity = [pscustomobject]@{{
    phase='calibration'; run_id='wave0-a11-calibration-test'
    campaign_root={_ps(str(campaign))}; source_commit={_ps(_SOURCE)}
    specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
    image_tag='vision-active-learning-loop:wave0-a11-calibration-test'
    image_id='sha256:' + ('a' * 64); owner_authorization_id={_ps(_OWNER)}
    lease_acquired=$false; current_stage='foundation'; terminal=$null
}}
function Get-A11HistoricalArtifactInventory {{
    return [pscustomobject]@{{
        records=[object[]]::new(64306)
        sha256={_ps(_HISTORICAL_FILES_SHA256)}
    }}
}}
function Get-A11HistoricalImageInventory {{
    return [pscustomobject]@{{
        records=[object[]]::new(21)
        sha256={_ps(_HISTORICAL_IMAGES_SHA256)}
    }}
}}
$script:Writes = [Collections.Generic.List[string]]::new()
$script:ProductionWrite = (Get-Command Write-A11NewText).ScriptBlock
function Write-A11NewText {{
    param([string]$Path, [AllowEmptyString()][string]$Text)
    [void]$script:Writes.Add([IO.Path]::GetFileName($Path))
    & $script:ProductionWrite -Path $Path -Text $Text
}}
$Closure = Close-A11Phase -Identity $Identity `
    -Terminal 'WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN' `
    -Failure 'injected:foundation'
[ordered]@{{ writes=$script:Writes; closure=$Closure }} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        ("Write-A11NewText", "Get-A11FileRecord", "Close-A11Phase"), body
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    names = [
        "78-failure-diagnostic.json",
        "79-historical-preservation-final.json",
        "80-campaign-result.json",
        "81-campaign-file-manifest.json",
        "82-campaign-closure.json",
    ]
    assert output["writes"] == names
    assert sorted(path.name for path in audit.glob("*.json")) == names
    diagnostic = json.loads((audit / names[0]).read_text(encoding="utf-8"))
    result = json.loads((audit / names[2]).read_text(encoding="utf-8"))
    manifest = json.loads((audit / names[3]).read_text(encoding="utf-8"))
    closure = json.loads((audit / names[4]).read_text(encoding="utf-8"))
    assert diagnostic["failed_stage"] == "foundation"
    assert diagnostic["errors"] == ["injected:foundation"]
    assert result["failure_diagnostic"] == _file_record(audit / names[0])
    assert result["historical_preservation"] == _file_record(audit / names[1])
    assert closure == output["closure"]
    assert closure["result"] == _file_record(audit / names[2])
    assert closure["manifest"] == _file_record(audit / names[3])
    manifest_paths = {record["path"] for record in manifest["files"]}
    expected_manifest_paths = {
        (audit / name).resolve().as_posix() for name in names[:3]
    }
    assert manifest_paths == expected_manifest_paths
    for record in manifest["files"]:
        assert record == _file_record(Path(record["path"]))


@pytest.mark.parametrize(
    "reuse", ["static", "run_id", "container_ids", "receipt_hashes"]
)
def test_cross_phase_identity_rejects_static_drift_or_runtime_reuse(reuse: str) -> None:
    calibration = _identity("calibration")
    validation = _identity("validation")
    if reuse == "static":
        validation["static"]["gpu"] = "GPU-other"
    else:
        validation["runtime"][reuse] = calibration["runtime"][reuse]
    body = f"""
$Calibration = {_ps(json.dumps(calibration))} | ConvertFrom-Json
$Validation = {_ps(json.dumps(validation))} | ConvertFrom-Json
Test-A11CrossPhaseIdentity -Calibration $Calibration -Validation $Validation |
    Out-Null
"""
    completed = _invoke_functions(("Test-A11CrossPhaseIdentity",), body)

    assert completed.returncode != 0


def test_campaign_orders_both_phases_and_never_retries() -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
function Resolve-A11Worktree {{ [void]$script:Events.Add('preflight'); return @{{}} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{
    [void]$script:Events.Add('destinations')
    return $true
}}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    [void]$script:Events.Add("identity:$Phase")
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; source_commit={_ps(_SOURCE)}
        specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
        image_tag="tag-$Phase"; image_id="sha256:$Phase"
        campaign_root="root-$Phase"; cache_root="cache-$Phase"
        cache_inventory_sha256='cache'; gpu_driver='driver'
        lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
        lease_lock_path='global-lock'; replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; lease_acquired=$false; release=$null
        current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{ param($Identity,$Peer); [void]$script:Events.Add("init:$($Identity.phase)") }}
function Invoke-A11Build {{ param($Identity); [void]$script:Events.Add("build:$($Identity.phase)") }}
function Invoke-A11CachePreflight {{ param($Identity); [void]$script:Events.Add("cache:$($Identity.phase)") }}
function Confirm-A11CalibrationReceipt {{ [void]$script:Events.Add('calibration-precheck') }}
function New-A11Lease {{ param($Identity); $Identity.lease_acquired=$true; [void]$script:Events.Add("lease:$($Identity.phase)"); return @{{}} }}
function Invoke-A11Foundation {{ param($Identity); [void]$script:Events.Add("foundation:$($Identity.phase)") }}
function Invoke-A11Replica {{ param($Identity,$ReplicaId); [void]$script:Events.Add("replica:$($Identity.phase):$ReplicaId") }}
function Invoke-A11Gate {{
    param($Identity)
    [void]$script:Events.Add("gate:$($Identity.phase)")
    if ($Identity.phase -eq 'calibration') {{ return {_ps('WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN')} }}
    return {_ps('WAVE0_A11_PASS / WAVE1_NOT_STARTED / OWNER_WAVE1_REVIEW_REQUIRED')}
}}
function Assert-A11AggregateReceipt {{ param($Identity); [void]$script:Events.Add("verify:$($Identity.phase)") }}
function Release-A11Lease {{ param($Identity); $Identity.lease_acquired=$false; $Identity.release=@{{ok=$true}}; [void]$script:Events.Add("release:$($Identity.phase)") }}
function Confirm-A11Release {{ return $true }}
function Close-A11Phase {{ param($Identity); [void]$script:Events.Add("close:$($Identity.phase)") }}
function Test-A11CrossPhaseIdentity {{ [void]$script:Events.Add('cross-phase') }}
Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)} | Out-Null
$script:Events | ConvertTo-Json -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    events = json.loads(completed.stdout)
    assert events[:6] == [
        "preflight",
        "identity:calibration",
        "identity:validation",
        "destinations",
        "init:calibration",
        "build:calibration",
    ]
    for phase in ("calibration", "validation"):
        replicas = [event for event in events if event.startswith(f"replica:{phase}:")]
        assert replicas == [
            f"replica:{phase}:{phase}-{index:02d}" for index in range(12)
        ]
        assert events.index(f"cache:{phase}") < events.index(f"lease:{phase}")
        assert events.index(f"lease:{phase}") < events.index(replicas[0])
        assert events.index(replicas[-1]) < events.index(f"gate:{phase}")
        assert events.index(f"gate:{phase}") < events.index(f"release:{phase}")
    assert events.index("release:calibration") < events.index("init:validation")
    cross_indexes = [
        index for index, event in enumerate(events) if event == "cross-phase"
    ]
    assert len(cross_indexes) == 2
    assert (
        events.index("cache:validation")
        < events.index("calibration-precheck")
        < cross_indexes[0]
    )
    assert (
        events.index("calibration-precheck")
        < cross_indexes[0]
        < events.index("lease:validation")
    )
    assert (
        events.index("release:validation")
        < cross_indexes[1]
        < events.index("close:validation")
    )
    assert events.count("gate:calibration") == events.count("gate:validation") == 1
    assert events[-1] == "close:validation"


def test_campaign_destination_failure_precedes_initialization_and_writes_nothing(
    tmp_path: Path,
) -> None:
    marker = tmp_path / "initialize-called"
    body = f"""
function Resolve-A11Worktree {{ return @{{}} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function New-A11PhaseIdentity {{
    param($Phase)
    return [pscustomobject]@{{ phase=$Phase; current_stage='preregistered' }}
}}
function Test-A11PhaseDestinationsAbsent {{ throw 'injected:destination' }}
function Confirm-A11ProtectedGit {{ return $true }}
function Initialize-A11Phase {{
    [IO.File]::WriteAllText({_ps(str(marker))}, 'called')
    throw 'injected:initialize'
}}
function Close-A11Phase {{}}
Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} `
    {_ps(_BRANCH)} {_ps(_OWNER)} | Out-Null
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode != 0
    assert "injected:destination" in completed.stderr
    assert not marker.exists()


def test_campaign_surfaces_closure_write_failure_without_retry(
    tmp_path: Path,
) -> None:
    calibration = tmp_path / "calibration"
    validation = tmp_path / "validation"
    diagnostic = calibration / "audit" / "78-failure-diagnostic.json"
    body = f"""
$script:ArtifactInventoryCalls = 0
$script:ImageInventoryCalls = 0
function Resolve-A11Worktree {{ return @{{}} }}
function Test-A11ReadOnlyPreflight {{}}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    $Root = if ($Phase -ceq 'calibration') {{
        {_ps(str(calibration))}
    }} else {{
        {_ps(str(validation))}
    }}
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; campaign_root=$Root
        source_commit={_ps(_SOURCE)}; specification_commit={_ps(_SPEC)}
        plan_commit={_ps(_PLAN)}; image_tag="tag-$Phase"
        image_id='sha256:' + ('a' * 64); owner_authorization_id={_ps(_OWNER)}
        cache_root="$Root/cache"; cache_inventory_sha256=$null; gpu_driver=$null
        lease_id="lease-$Phase"; lease_path="$Root/lease"
        lease_lock_path="$Root/lease-lock"; lease_acquired=$false; release=$null
        replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{
    param($Identity)
    [IO.Directory]::CreateDirectory(
        [IO.Path]::Combine($Identity.campaign_root, 'audit')
    ) | Out-Null
    [IO.File]::WriteAllBytes(
        [IO.Path]::Combine(
            $Identity.campaign_root, 'audit', '78-failure-diagnostic.json'
        ),
        [Text.Encoding]::UTF8.GetBytes('sentinel')
    )
    throw 'injected:initialize'
}}
function Get-A11HistoricalArtifactInventory {{
    $script:ArtifactInventoryCalls++
    return [pscustomobject]@{{
        records=[object[]]::new(64306)
        sha256={_ps(_HISTORICAL_FILES_SHA256)}
    }}
}}
function Get-A11HistoricalImageInventory {{
    $script:ImageInventoryCalls++
    return [pscustomobject]@{{
        records=[object[]]::new(21)
        sha256={_ps(_HISTORICAL_IMAGES_SHA256)}
    }}
}}
$Values = @(Invoke-A11Campaign `
    {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)})
[ordered]@{{
    count=$Values.Count
    result=$Values[0]
    artifact_inventory_calls=$script:ArtifactInventoryCalls
    image_inventory_calls=$script:ImageInventoryCalls
}} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(
        (
            "Write-A11NewText",
            "Get-A11FileRecord",
            "Close-A11Phase",
            "Invoke-A11Campaign",
        ),
        body,
    )

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["count"] == 1
    result = output["result"]
    assert result["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    assert result["error"] == "injected:initialize"
    assert "exists" in result["closure_error"].lower()
    assert output["artifact_inventory_calls"] == 1
    assert output["image_inventory_calls"] == 1
    assert diagnostic.read_bytes() == b"sentinel"


def test_campaign_suppresses_cache_evidence_and_emits_one_result() -> None:
    body = f"""
function Resolve-A11Worktree {{ return @{{}} }}
function Test-A11ReadOnlyPreflight {{}}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{
    param($Phase)
    return [pscustomobject]@{{
        phase=$Phase; run_id="run-$Phase"; source_commit={_ps(_SOURCE)}
        specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
        image_tag="tag-$Phase"; image_id='sha256:' + ('a' * 64)
        campaign_root="root-$Phase"; cache_root="cache-$Phase"
        cache_inventory_sha256=$null; gpu_driver=$null
        lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
        lease_lock_path='global-lock'; lease_acquired=$false; release=$null
        replica_records=[Collections.Generic.List[object]]::new()
        audit_records=[ordered]@{{}}; current_stage='preregistered'; terminal=$null
    }}
}}
function Initialize-A11Phase {{}}
function Invoke-A11Build {{}}
function Invoke-A11CachePreflight {{
    return [pscustomobject]@{{ cache='evidence' }}
}}
function New-A11Lease {{ param($Identity); $Identity.lease_acquired=$true }}
function Invoke-A11Foundation {{ throw 'injected:foundation' }}
function Release-A11Lease {{
    param($Identity)
    $Identity.lease_acquired=$false
    $Identity.release=[pscustomobject]@{{ released=$true }}
}}
function Close-A11Phase {{}}
$Values = @(Invoke-A11Campaign `
    {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)})
[ordered]@{{ count=$Values.Count; result=$Values[-1] }} |
    ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    output = json.loads(completed.stdout)
    assert output["count"] == 1
    assert output["result"]["terminal"] == (
        "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    )
    assert output["result"]["error"] == "injected:foundation"


@pytest.mark.parametrize(
    ("values", "observed"),
    [
        ("$Values = @()", 0),
        (
            "$Values = @([pscustomobject]@{terminal='one'}, "
            + "[pscustomobject]@{terminal='two'})",
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


def test_calibration_failure_prohibits_validation_and_second_invocation() -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
function Resolve-A11Worktree {{ [void]$script:Events.Add('preflight'); return @{{}} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{ param($Phase); return [pscustomobject]@{{
    phase=$Phase; source_commit={_ps(_SOURCE)}; specification_commit={_ps(_SPEC)}
    plan_commit={_ps(_PLAN)}; image_tag="tag-$Phase"; image_id="sha256:$Phase"
    campaign_root="root-$Phase"; cache_root="cache-$Phase"; cache_inventory_sha256='cache'
    gpu_driver='driver'; lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
    lease_lock_path='global-lock'; replica_records=[Collections.Generic.List[object]]::new()
    audit_records=[ordered]@{{}}; lease_acquired=$false; release=$null
    current_stage='preregistered'; terminal=$null
}} }}
function Initialize-A11Phase {{ param($Identity,$Peer); [void]$script:Events.Add("init:$($Identity.phase)") }}
function Invoke-A11Build {{ param($Identity); [void]$script:Events.Add("build:$($Identity.phase)") }}
function Invoke-A11CachePreflight {{ param($Identity); [void]$script:Events.Add("cache:$($Identity.phase)") }}
function New-A11Lease {{ param($Identity); $Identity.lease_acquired=$true; [void]$script:Events.Add("lease:$($Identity.phase)") }}
function Invoke-A11Foundation {{ param($Identity); [void]$script:Events.Add("foundation:$($Identity.phase)") }}
function Invoke-A11Replica {{ param($Identity,$ReplicaId); [void]$script:Events.Add("replica:$($Identity.phase):$ReplicaId") }}
function Invoke-A11Gate {{ param($Identity); [void]$script:Events.Add("gate:$($Identity.phase)"); return 'FAIL' }}
function Assert-A11AggregateReceipt {{ throw 'must not verify failed calibration' }}
function Release-A11Lease {{ param($Identity); $Identity.lease_acquired=$false; $Identity.release=@{{ok=$true}}; [void]$script:Events.Add("release:$($Identity.phase)") }}
function Confirm-A11Release {{ return $true }}
function Close-A11Phase {{ param($Identity); [void]$script:Events.Add("close:$($Identity.phase)") }}
function Test-A11CrossPhaseIdentity {{ throw 'must not compare phases' }}
$Result = Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)}
@{{ events=$script:Events; result=$Result }} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    events = result["events"]
    assert events.count("gate:calibration") == 1
    assert not any("validation" in event for event in events)
    assert result["result"]["terminal"] == "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"


@pytest.mark.parametrize(
    "failed_stage",
    [
        "initialize",
        "build",
        "cache",
        "lease",
        "foundation",
        "replica",
        "gate",
        "verify",
        "release",
    ],
)
def test_each_calibration_stage_failure_closes_once_without_retry(
    failed_stage: str,
) -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
$script:FailAt = {_ps(failed_stage)}
function Step {{
    param($Name,$Phase)
    [void]$script:Events.Add("$Name`:$Phase")
    if ($Name -ceq $script:FailAt) {{ throw "injected:$Name" }}
}}
function Resolve-A11Worktree {{ return @{{}} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
function Test-A11PhaseDestinationsAbsent {{ return $true }}
function Confirm-A11ProtectedGit {{ return $true }}
function New-A11PhaseIdentity {{ param($Phase); return [pscustomobject]@{{
    phase=$Phase; run_id="run-$Phase"; source_commit={_ps(_SOURCE)}
    specification_commit={_ps(_SPEC)}; plan_commit={_ps(_PLAN)}
    image_tag="tag-$Phase"; image_id="sha256:$Phase"
    campaign_root="root-$Phase"; cache_root="cache-$Phase"; cache_inventory_sha256='cache'
    gpu_driver='driver'; lease_id="lease-$Phase"; lease_path="lease-path-$Phase"
    lease_lock_path='global-lock'; replica_records=[Collections.Generic.List[object]]::new()
    audit_records=[ordered]@{{}}; lease_acquired=$false; release=$null
    current_stage='preregistered'; terminal=$null
}} }}
function Initialize-A11Phase {{ param($Identity,$Peer); Step initialize $Identity.phase }}
function Invoke-A11Build {{ param($Identity); Step build $Identity.phase }}
function Invoke-A11CachePreflight {{ param($Identity); Step cache $Identity.phase }}
function New-A11Lease {{
    param($Identity)
    Step lease $Identity.phase
    $Identity.lease_acquired=$true
}}
function Invoke-A11Foundation {{ param($Identity); Step foundation $Identity.phase }}
function Invoke-A11Replica {{ param($Identity,$ReplicaId); Step replica $Identity.phase }}
function Invoke-A11Gate {{
    param($Identity)
    Step gate $Identity.phase
    return {_ps('WAVE0_A11_CALIBRATION_RECORDED / WAVE0_NOT_PASSED / WAVE1_FORBIDDEN')}
}}
function Assert-A11AggregateReceipt {{ param($Identity); Step verify $Identity.phase }}
function Release-A11Lease {{
    param($Identity)
    Step release $Identity.phase
    $Identity.lease_acquired=$false
    $Identity.release=@{{ok=$true}}
}}
function Confirm-A11Release {{ return $true }}
function Close-A11Phase {{ param($Identity); [void]$script:Events.Add("close:$($Identity.phase)") }}
function Test-A11CrossPhaseIdentity {{ throw 'validation must remain forbidden' }}
$Result = Invoke-A11Campaign {_ps(_SOURCE)} {_ps(_SPEC)} {_ps(_PLAN)} {_ps(_BRANCH)} {_ps(_OWNER)}
@{{ events=$script:Events; result=$Result }} | ConvertTo-Json -Depth 8 -Compress
"""
    completed = _invoke_functions(("Invoke-A11Campaign",), body)

    assert completed.returncode == 0, completed.stderr
    result = json.loads(completed.stdout)
    events = result["events"]
    assert events.count(f"{failed_stage}:calibration") == 1
    assert events.count("close:calibration") == 1
    assert not any(event.endswith(":validation") for event in events)
    assert result["result"]["terminal"] == (
        "WAVE0_A11_NORMATIVE_FAIL / WAVE1_FORBIDDEN"
    )


def test_launcher_source_has_no_cleanup_retry_or_wave1_capability() -> None:
    source = _SCRIPT.read_text(encoding="utf-8")

    assert "Remove-Item" not in source
    assert "docker image rm" not in source.lower()
    assert "--retry" not in source.lower()
    assert "OwnerAuthorizationId =" not in source
    assert source.count("for ($Index = 0; $Index -lt 12; $Index++)") == 1
    values_index = source.index("$A11Values = @(")
    guard_index = source.index("Get-A11SingleCampaignResult -Values $A11Values")
    terminal_index = source.index("$A11Result.terminal", guard_index)
    assert values_index < guard_index < terminal_index
    assert "$A11Result.closure_error" in source
    assert "[Console]::Error.WriteLine" in source
