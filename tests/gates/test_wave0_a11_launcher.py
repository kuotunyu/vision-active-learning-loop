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
        "existing_destinations": [],
        "historical_file_count": 64306,
        "historical_image_count": 21,
        "historical_file_inventory_sha256": _HISTORICAL_FILES_SHA256,
        "historical_image_inventory_sha256": _HISTORICAL_IMAGES_SHA256,
        "historical_preserved": True,
    }


def _preflight_body(evidence: dict[str, object]) -> str:
    return f"""
$Result = Test-A11ReadOnlyPreflight `
    -EvidenceJson {_ps(json.dumps(evidence))} `
    -ExpectedSourceCommit {_ps(_SOURCE)} `
    -ExpectedSpecCommit {_ps(_SPEC)} `
    -ExpectedPlanCommit {_ps(_PLAN)} `
    -ExpectedBranch {_ps(_BRANCH)} `
    -OwnerAuthorizationId {_ps(_OWNER)}
$Result | ConvertTo-Json -Depth 8 -Compress
"""


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
        "New-A11BuildArguments",
        "Invoke-A11CachePreflight",
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


def test_read_only_preflight_accepts_exact_closed_evidence() -> None:
    completed = _invoke_functions(
        ("Test-A11ReadOnlyPreflight",), _preflight_body(_preflight())
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["head"] == _SOURCE


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
        ("existing_destinations", ["calibration-root"]),
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
    assert events[:5] == [
        "preflight",
        "identity:calibration",
        "identity:validation",
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


def test_calibration_failure_prohibits_validation_and_second_invocation() -> None:
    body = f"""
$script:Events = [Collections.Generic.List[string]]::new()
function Resolve-A11Worktree {{ [void]$script:Events.Add('preflight'); return @{{}} }}
function Test-A11ReadOnlyPreflight {{ return @{{}} }}
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
