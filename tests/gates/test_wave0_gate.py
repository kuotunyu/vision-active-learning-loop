from __future__ import annotations

import copy
import hashlib
import json
import random
import shutil
import subprocess
from pathlib import Path

import numpy as np
import pytest
import torch

from vision_active_learning_loop.artifacts import receipts
from vision_active_learning_loop.artifacts.digests import canonical_json_sha256
from vision_active_learning_loop.artifacts.receipts import (
    _canonical_storage_bytes,
    _receipt_content_sha256,
    atomic_write_receipt,
    validate_receipt,
)
from vision_active_learning_loop.cli_manifest import build_manifest
from vision_active_learning_loop.gates.wave0 import (
    ReplayReceiptPaths,
    Wave0Inputs,
    _AttemptEvidence,
    _semantic_environment_identities_match,
    evaluate_wave0,
    main,
)
from vision_active_learning_loop.models.assets import load_pinned_asset_specs
from vision_active_learning_loop.probes import training_feasibility as feasibility_probe
from vision_active_learning_loop.training.checkpoint_io import (
    CheckpointState,
    capture_rng_state,
    checkpoint_state_digests,
    checkpoint_state_sha256,
    load_checkpoint_verified,
    save_checkpoint_atomic,
    structured_state_sha256,
)

from ..artifacts.test_receipts import (
    MODEL_CONTRACT_INVARIANTS,
    build_valid_environment_receipt,
    build_valid_model_contract_receipt,
)
from ..models.test_assets import CONFIG_PATH, _valid_model_asset_receipt
from ..probes.test_training_feasibility import _receipt as valid_feasibility_receipt


class _GateGroupedModel(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.detector = torch.nn.Linear(2, 1)
        self.model = torch.nn.Module()
        self.model.backbone = torch.nn.Linear(2, 1)


def _checkpoint_fixture(
    model_contract_digest: str,
) -> tuple[CheckpointState, dict[str, object]]:
    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    model = _GateGroupedModel()
    baseline = feasibility_probe._capture_parameter_baseline(model)
    parameter_digest_before = feasibility_probe.trainable_parameter_sha256(model)
    optimizer = feasibility_probe.build_optimizer(model)
    scheduler = feasibility_probe.build_scheduler(optimizer)
    optimizer_groups = feasibility_probe._optimizer_group_evidence(optimizer)
    scheduler_before = structured_state_sha256(scheduler.state_dict())
    loss = sum(parameter.square().sum() for parameter in model.parameters())
    loss.backward()
    optimizer.step()
    scheduler.step()
    sampler_digest = hashlib.sha256(b'["wide-gradient","tall-checker"]').hexdigest()
    state = CheckpointState(
        model_state=copy.deepcopy(model.state_dict()),
        optimizer_state=copy.deepcopy(optimizer.state_dict()),
        scheduler_state=copy.deepcopy(scheduler.state_dict()),
        scaler_state=None,
        epoch=0,
        step=1,
        sampler_order_digest=sampler_digest,
        rng_state=capture_rng_state(),
        input_digests={"model_contract_receipt": model_contract_digest},
    )
    evidence = {
        "parameter_digest_before": parameter_digest_before,
        "parameter_digest_after": feasibility_probe.trainable_parameter_sha256(model),
        "parameter_inventory": [dict(item) for item in baseline.inventory],
        "update_groups": feasibility_probe._measure_parameter_update_groups(
            model, baseline
        ),
        "optimizer_groups": [dict(item) for item in optimizer_groups],
        "scheduler_state_before_sha256": scheduler_before,
        "sampler_order_digest": sampler_digest,
        "model_state_inventory": [
            dict(item) for item in feasibility_probe._model_state_inventory(model)
        ],
        "state_digests": checkpoint_state_digests(state),
        "checkpoint_state_sha256": checkpoint_state_sha256(state),
    }
    return state, evidence


def _bind_checkpoint_evidence(
    document: dict[str, object],
    *,
    model_contract: dict[str, object],
    model_contract_digest: str,
    checkpoint_digest: str,
    evidence: dict[str, object],
) -> None:
    normative = document["normative"]
    assert isinstance(normative, dict)
    normative["parent_model_contract"] = copy.deepcopy(model_contract)
    normative["model_contract_receipt_sha256"] = model_contract_digest
    normative["checkpoint_sha256"] = checkpoint_digest
    normative["checkpoint_state_sha256"] = evidence["checkpoint_state_sha256"]
    normative["state_digests"] = copy.deepcopy(evidence["state_digests"])
    normative["parameter_inventory"] = copy.deepcopy(evidence["parameter_inventory"])
    normative["update_groups"] = {
        name: {"l2_norm": value} for name, value in evidence["update_groups"].items()
    }
    step = normative["step"]
    assert isinstance(step, dict)
    step["trainable_parameter_count"] = len(evidence["parameter_inventory"])
    step["parameter_digest_before"] = evidence["parameter_digest_before"]
    step["parameter_digest_after"] = evidence["parameter_digest_after"]
    exact = normative["exact_comparison"]
    assert isinstance(exact, dict)
    exact["parameter_digest_before"] = evidence["parameter_digest_before"]
    exact["parameter_inventory"] = copy.deepcopy(evidence["parameter_inventory"])
    exact["optimizer_groups"] = copy.deepcopy(evidence["optimizer_groups"])
    exact["scheduler_state_before_sha256"] = evidence["scheduler_state_before_sha256"]
    exact["sampler_order_digest"] = evidence["sampler_order_digest"]
    exact["model_state_inventory"] = copy.deepcopy(evidence["model_state_inventory"])
    state_digests = evidence["state_digests"]
    assert isinstance(state_digests, dict)
    exact["state_digests"] = {
        name: state_digests[name] for name in ("scheduler", "scaler", "rng", "sampler")
    }
    exact["sha256"] = canonical_json_sha256(
        {name: value for name, value in exact.items() if name not in {"rule", "sha256"}}
    )
    checkpoint = normative["checkpoint"]
    assert isinstance(checkpoint, dict)
    checkpoint.update(
        {
            "file_sha256": checkpoint_digest,
            "verified_file_sha256": checkpoint_digest,
            "live_model_state_sha256_after_step": state_digests["model"],
            "state_sha256_before_save": evidence["checkpoint_state_sha256"],
            "state_sha256_after_load": evidence["checkpoint_state_sha256"],
            "state_digests_before_save": copy.deepcopy(state_digests),
            "state_digests_after_load": copy.deepcopy(state_digests),
            "state_digests_after_restore": copy.deepcopy(state_digests),
            "input_digests_verified": True,
        }
    )


@pytest.fixture(autouse=True)
def _bind_minimal_asset_documents(monkeypatch: pytest.MonkeyPatch) -> None:
    empty_hash = canonical_json_sha256({})
    monkeypatch.setattr(
        receipts,
        "_APPROVED_MODEL_DOCUMENT_HASHES",
        {
            name: {"config": empty_hash, "processor": empty_hash}
            for name in ("rtdetr", "dinov2")
        },
    )


def _paths(attempt_root: Path) -> ReplayReceiptPaths:
    root = attempt_root / "wave0" / "receipts"
    checkpoints = attempt_root / "wave0" / "checkpoints"
    return ReplayReceiptPaths(
        environment=root / "environment.json",
        model_assets=root / "model-assets.json",
        model_contract=root / "model-contract.json",
        feasibility_a=root / "feasibility-a.json",
        feasibility_b=root / "feasibility-b.json",
        checkpoint_a=checkpoints / "feasibility-a" / "step-000001.pt",
        checkpoint_b=checkpoints / "feasibility-b" / "step-000001.pt",
    )


def _publish_attempt(attempt_root: Path, run_id: str = "run-a") -> ReplayReceiptPaths:
    paths = _paths(attempt_root)
    paths.environment.parent.mkdir(parents=True)
    specs = load_pinned_asset_specs(CONFIG_PATH)
    asset_receipt = _valid_model_asset_receipt(specs)
    asset_receipt["metadata"]["run_id"] = run_id
    model_contract = build_valid_model_contract_receipt()
    if run_id != "run-a":
        raise AssertionError("test helper only supports the canonical fixture run")
    for path, document in (
        (paths.environment, build_valid_environment_receipt(run_id)),
        (paths.model_assets, asset_receipt),
        (paths.model_contract, model_contract),
    ):
        atomic_write_receipt(path, document)
    model_contract = json.loads(paths.model_contract.read_text(encoding="utf-8"))
    assert isinstance(model_contract, dict)
    model_contract_digest = hashlib.sha256(
        paths.model_contract.read_bytes()
    ).hexdigest()
    for suffix in ("a", "b"):
        checkpoint_path = getattr(paths, f"checkpoint_{suffix}")
        checkpoint_path.parent.mkdir(parents=True)
        state, evidence = _checkpoint_fixture(model_contract_digest)
        checkpoint_digest = save_checkpoint_atomic(state, checkpoint_path)
        feasibility = valid_feasibility_receipt()
        _bind_checkpoint_evidence(
            feasibility,
            model_contract=model_contract,
            model_contract_digest=model_contract_digest,
            checkpoint_digest=checkpoint_digest,
            evidence=evidence,
        )
        atomic_write_receipt(getattr(paths, f"feasibility_{suffix}"), feasibility)
    return paths


@pytest.fixture
def valid_inputs(tmp_path: Path) -> Wave0Inputs:
    return Wave0Inputs(
        run_id="run-a",
        primary=_publish_attempt(tmp_path / "primary"),
        clean_a=_publish_attempt(tmp_path / "clean-a"),
        clean_b=_publish_attempt(tmp_path / "clean-b"),
    )


def _rewrite(path: Path, mutation: object) -> None:
    document = json.loads(path.read_text(encoding="utf-8"))
    assert callable(mutation)
    mutation(document)
    document["metadata"]["receipt_content_sha256"] = _receipt_content_sha256(document)
    path.write_bytes(_canonical_storage_bytes(document))


def test_complete_a3_inputs_pass_with_exact_terminal_interpretation(
    valid_inputs: Wave0Inputs,
) -> None:
    result = evaluate_wave0(valid_inputs)

    assert not result.errors
    assert all(result.invariants.values())
    document = result.as_dict()
    assert document["normative"]["status"] == "PASS"
    assert (
        document["normative"]["interpretation"] == "WAVE0_A3_PASS / WAVE1_NOT_STARTED"
    )
    comparison_keys = {
        "primary_b",
        "clean_a_a",
        "clean_a_b",
        "clean_b_a",
        "clean_b_b",
    }
    assert set(document["normative"]["exact_comparisons"]) == comparison_keys
    assert set(document["normative"]["numerical_replay_comparisons"]) == comparison_keys
    assert all(
        value["passed"] is True
        for value in document["normative"]["exact_comparisons"].values()
    )
    assert all(
        value["passed"] is True
        for value in document["normative"]["numerical_replay_comparisons"].values()
    )


def test_attempts_must_share_one_exact_semantic_environment() -> None:
    def attempt(gpu_uuid: str) -> _AttemptEvidence:
        return _AttemptEvidence(
            documents={
                "environment": {
                    "normative": {
                        "observed": {
                            "gpu_uuid": gpu_uuid,
                            "driver": "580.88",
                            "runtime_image_digest": "sha256:" + "a" * 64,
                        }
                    }
                }
            },
            stored_hashes={},
            checkpoints={},
        )

    canonical = attempt("GPU-11111111-1111-1111-1111-111111111111")
    same = attempt("GPU-11111111-1111-1111-1111-111111111111")
    different = attempt("GPU-22222222-2222-2222-2222-222222222222")

    assert _semantic_environment_identities_match(
        {"primary": canonical, "clean_a": same, "clean_b": same}
    )
    assert not _semantic_environment_identities_match(
        {"primary": canonical, "clean_a": same, "clean_b": different}
    )


@pytest.mark.parametrize("mode", ["missing", "corrupt", "wrong-receipt-hash"])
def test_missing_corrupt_or_wrong_hash_checkpoint_fails_before_comparison(
    valid_inputs: Wave0Inputs, mode: str
) -> None:
    checkpoint = valid_inputs.primary.checkpoint_b
    if mode == "missing":
        checkpoint.unlink()
    elif mode == "corrupt":
        checkpoint.write_bytes(b"not a checkpoint")
    else:
        _rewrite(
            valid_inputs.primary.feasibility_b,
            lambda document: (
                document["normative"].update({"checkpoint_sha256": "0" * 64}),
                document["normative"]["checkpoint"].update(
                    {
                        "file_sha256": "0" * 64,
                        "verified_file_sha256": "0" * 64,
                    }
                ),
            ),
        )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["primary_complete_pass"] is False
    assert result.invariants["numerical_replays_within_bounds"] is False
    assert result.errors


def test_historical_feasibility_version_is_rejected_by_a3_gate(
    valid_inputs: Wave0Inputs,
) -> None:
    _rewrite(
        valid_inputs.clean_a.feasibility_a,
        lambda document: document.update({"schema_version": 1}),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["historical_evidence_not_used"] is False
    assert result.invariants["clean_a_complete_pass"] is False


def test_post_update_checkpoint_drift_fails_registered_numerical_bound(
    valid_inputs: Wave0Inputs,
) -> None:
    receipt_path = valid_inputs.clean_b.feasibility_b
    document = json.loads(receipt_path.read_text(encoding="utf-8"))
    normative = document["normative"]
    checkpoint_path = valid_inputs.clean_b.checkpoint_b
    state = load_checkpoint_verified(
        checkpoint_path,
        normative["checkpoint_sha256"],
        expected_input_digests={
            "model_contract_receipt": normative["model_contract_receipt_sha256"]
        },
    )
    model_state = dict(state.model_state)
    first_name = normative["parameter_inventory"][0]["name"]
    first_tensor = model_state[first_name]
    model_state[first_name] = first_tensor + torch.full_like(first_tensor, 0.1)
    changed = CheckpointState(
        model_state=model_state,
        optimizer_state=state.optimizer_state,
        scheduler_state=state.scheduler_state,
        scaler_state=state.scaler_state,
        epoch=state.epoch,
        step=state.step,
        sampler_order_digest=state.sampler_order_digest,
        rng_state=state.rng_state,
        input_digests=state.input_digests,
    )
    checkpoint_path.unlink()
    new_digest = save_checkpoint_atomic(changed, checkpoint_path)
    new_state_digest = checkpoint_state_sha256(changed)
    new_digests = checkpoint_state_digests(changed)

    def rebind(changed_document: dict[str, object]) -> None:
        changed_normative = changed_document["normative"]
        changed_normative["checkpoint_sha256"] = new_digest
        changed_normative["checkpoint_state_sha256"] = new_state_digest
        changed_normative["state_digests"] = copy.deepcopy(new_digests)
        checkpoint_evidence = changed_normative["checkpoint"]
        checkpoint_evidence.update(
            {
                "file_sha256": new_digest,
                "verified_file_sha256": new_digest,
                "live_model_state_sha256_after_step": new_digests["model"],
                "state_sha256_before_save": new_state_digest,
                "state_sha256_after_load": new_state_digest,
                "state_digests_before_save": copy.deepcopy(new_digests),
                "state_digests_after_load": copy.deepcopy(new_digests),
                "state_digests_after_restore": copy.deepcopy(new_digests),
            }
        )

    _rewrite(receipt_path, rebind)

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["clean_replays_exact_fields_match"] is True
    assert result.invariants["numerical_replays_within_bounds"] is False
    assert any("clean_b_b" in error for error in result.errors)


@pytest.mark.parametrize(
    "stage",
    ["environment", "model_assets", "model_contract", "feasibility_a", "feasibility_b"],
)
def test_missing_or_corrupt_parent_fails_closed(
    valid_inputs: Wave0Inputs, stage: str
) -> None:
    getattr(valid_inputs.primary, stage).unlink()

    result = evaluate_wave0(valid_inputs)

    assert result.errors
    assert result.invariants["primary_complete_pass"] is False


def test_different_parent_run_id_is_rejected(valid_inputs: Wave0Inputs) -> None:
    _rewrite(
        valid_inputs.clean_b.environment,
        lambda document: document["metadata"].update({"run_id": "different-run"}),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["all_run_ids_match"] is False
    assert result.errors


@pytest.mark.parametrize(
    ("stage", "field"),
    [
        ("model_contract", "environment_receipt_content_sha256"),
        ("feasibility_a", "model_contract_receipt_sha256"),
        ("feasibility_b", "model_contract_receipt_sha256"),
    ],
)
def test_wrong_parent_hash_binding_is_rejected(
    valid_inputs: Wave0Inputs, stage: str, field: str
) -> None:
    _rewrite(
        getattr(valid_inputs.primary, stage),
        lambda document: document["normative"].update({field: "0" * 64}),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["all_parent_bindings_match"] is False


@pytest.mark.parametrize("field", ["loss_source_sha256", "synthetic_target_sha256"])
def test_narrower_historical_model_contract_is_rejected(
    valid_inputs: Wave0Inputs, field: str
) -> None:
    _rewrite(
        valid_inputs.primary.model_contract,
        lambda document: document["normative"].pop(field),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["historical_evidence_not_used"] is False


@pytest.mark.parametrize("invariant", MODEL_CONTRACT_INVARIANTS)
def test_every_a2_model_invariant_is_fail_closed(
    valid_inputs: Wave0Inputs, invariant: str
) -> None:
    _rewrite(
        valid_inputs.primary.model_contract,
        lambda document: document["normative"]["invariants"].update({invariant: False}),
    )

    assert evaluate_wave0(valid_inputs).errors


def test_feasibility_ab_exact_divergence_is_rejected(
    valid_inputs: Wave0Inputs,
) -> None:
    _rewrite(
        valid_inputs.primary.feasibility_b,
        lambda document: document["normative"]["exact_comparison"].update(
            {"sha256": "b" * 64}
        ),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["feasibility_ab_exact_fields_match"] is False


def test_clean_replay_exact_divergence_is_rejected(
    valid_inputs: Wave0Inputs,
) -> None:
    _rewrite(
        valid_inputs.clean_b.feasibility_a,
        lambda document: document["normative"]["exact_comparison"].update(
            {"sha256": "b" * 64}
        ),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["clean_replays_exact_fields_match"] is False


def test_data_root_presence_is_rejected(valid_inputs: Wave0Inputs) -> None:
    _rewrite(
        valid_inputs.clean_a.environment,
        lambda document: document["normative"]["observed"].update(
            {"data_root_unset": False}
        ),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["data_root_unset"] is False


def test_cli_refuses_existing_output_without_changing_it(
    tmp_path: Path, valid_inputs: Wave0Inputs
) -> None:
    output = tmp_path / "gate.json"
    output.write_bytes(b"historical")

    exit_code = main(
        [
            "--run-id",
            valid_inputs.run_id,
            "--primary-root",
            str(valid_inputs.primary.environment.parents[2]),
            "--clean-a-root",
            str(valid_inputs.clean_a.environment.parents[2]),
            "--clean-b-root",
            str(valid_inputs.clean_b.environment.parents[2]),
            "--output",
            str(output),
        ]
    )

    assert exit_code != 0
    assert output.read_bytes() == b"historical"


def test_gate_cli_is_registered_and_creates_no_capability(
    tmp_path: Path, valid_inputs: Wave0Inputs
) -> None:
    manifest = build_manifest(Path(__file__).parents[2] / "src")
    assert manifest["gate wave0"].endswith("gates.wave0:main")

    output = tmp_path / "wave0-gate.json"
    assert (
        main(
            [
                "--run-id",
                valid_inputs.run_id,
                "--primary-root",
                str(valid_inputs.primary.environment.parents[2]),
                "--clean-a-root",
                str(valid_inputs.clean_a.environment.parents[2]),
                "--clean-b-root",
                str(valid_inputs.clean_b.environment.parents[2]),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    stored = json.loads(output.read_text(encoding="utf-8"))
    validate_receipt(
        stored, Path(__file__).parents[2] / "schemas/wave0-gate-receipt.schema.json"
    )
    assert not list(tmp_path.rglob("*.pass"))
    assert not list(tmp_path.rglob("*wave1*"))


def test_powershell_writer_publishes_zero_byte_log_for_empty_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch successful silent stages failing before their audit log is created."""
    powershell = shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is unavailable")

    project_root = Path(__file__).parents[2]
    output = tmp_path / "empty-stage.log"
    monkeypatch.setenv(
        "VAL_TEST_WAVE0_SCRIPT", str(project_root / "scripts/run_wave0_clean.ps1")
    )
    monkeypatch.setenv("VAL_TEST_EMPTY_LOG", str(output))
    command = r"""
$ErrorActionPreference = 'Stop'
$Tokens = $null
$ParseErrors = $null
$Ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $env:VAL_TEST_WAVE0_SCRIPT,
    [ref]$Tokens,
    [ref]$ParseErrors
)
if ($ParseErrors.Count -ne 0) { throw 'Wave 0 script did not parse' }
$WriteFunction = $Ast.Find({
    param($Node)
    $Node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $Node.Name -eq 'Write-NewText'
}, $true)
if ($null -eq $WriteFunction) { throw 'Write-NewText was not found' }
Invoke-Expression $WriteFunction.Extent.Text
Write-NewText -Path $env:VAL_TEST_EMPTY_LOG -Text ''
"""

    completed = subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert output.read_bytes() == b""


def _run_powershell_native_capture(
    monkeypatch: pytest.MonkeyPatch, native_command: str
) -> subprocess.CompletedProcess[str]:
    powershell = shutil.which("powershell")
    if powershell is None:
        pytest.skip("Windows PowerShell is unavailable")

    project_root = Path(__file__).parents[2]
    monkeypatch.setenv(
        "VAL_TEST_WAVE0_SCRIPT", str(project_root / "scripts/run_wave0_clean.ps1")
    )
    monkeypatch.setenv("VAL_TEST_NATIVE_COMMAND", native_command)
    command = r"""
$ErrorActionPreference = 'Stop'
$Tokens = $null
$ParseErrors = $null
$Ast = [System.Management.Automation.Language.Parser]::ParseFile(
    $env:VAL_TEST_WAVE0_SCRIPT,
    [ref]$Tokens,
    [ref]$ParseErrors
)
if ($ParseErrors.Count -ne 0) { throw 'Wave 0 PowerShell script did not parse' }
$CaptureFunction = $Ast.Find({
    param($Node)
    $Node -is [System.Management.Automation.Language.FunctionDefinitionAst] -and
        $Node.Name -eq 'Invoke-NativeCommandCapture'
}, $true)
if ($null -eq $CaptureFunction) { throw 'Invoke-NativeCommandCapture was not found' }
Invoke-Expression $CaptureFunction.Extent.Text
$Result = Invoke-NativeCommandCapture -FilePath 'cmd.exe' -ArgumentList @(
    '/d', '/c', $env:VAL_TEST_NATIVE_COMMAND
)
[pscustomobject]@{
    text = $Result.Text
    exit_code = $Result.ExitCode
    error_action_preference = $ErrorActionPreference.ToString()
} | ConvertTo-Json -Compress
"""
    return subprocess.run(
        [powershell, "-NoProfile", "-NonInteractive", "-Command", command],
        check=False,
        capture_output=True,
        text=True,
    )


def test_powershell_native_capture_allows_stderr_with_zero_exit(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch successful native stderr being promoted to a terminating error."""
    completed = _run_powershell_native_capture(
        monkeypatch, "echo download-progress 1>&2 & exit /b 0"
    )

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["exit_code"] == 0
    assert payload["text"].strip() == "download-progress"
    assert payload["error_action_preference"] == "Stop"


@pytest.mark.parametrize(
    ("native_command", "expected_exit_code", "expected_lines"),
    [
        ("exit /b 0", 0, []),
        ("echo normal & echo failure 1>&2 & exit /b 7", 7, ["normal", "failure"]),
    ],
)
def test_powershell_native_capture_preserves_empty_and_nonzero_results(
    monkeypatch: pytest.MonkeyPatch,
    native_command: str,
    expected_exit_code: int,
    expected_lines: list[str],
) -> None:
    """Catch empty logs or nonzero native exit codes being reinterpreted."""
    completed = _run_powershell_native_capture(monkeypatch, native_command)

    assert completed.returncode == 0, completed.stderr
    payload = json.loads(completed.stdout)
    assert payload["exit_code"] == expected_exit_code
    assert [line.strip() for line in payload["text"].splitlines()] == expected_lines
    assert payload["error_action_preference"] == "Stop"


def test_powershell_and_bash_scripts_have_equivalent_fail_closed_stages() -> None:
    project_root = Path(__file__).parents[2]
    powershell = (project_root / "scripts/run_wave0_clean.ps1").read_text(
        encoding="utf-8"
    )
    bash = (project_root / "scripts/run_wave0_clean.sh").read_text(encoding="utf-8")
    required = (
        "environment.json",
        "model-assets.json",
        "model-contract.json",
        "feasibility-a.json",
        "feasibility-b.json",
    )
    for script in (powershell, bash):
        assert all(stage in script for stage in required)
        assert "gate wave1" not in script.lower()
        assert "wave1 start" not in script.lower()
        assert "VAL_DATA_ROOT" in script
        assert "--network none" in script
        assert ":/workspace:ro" in script
        assert "--force" not in script.lower()
        assert "rm -rf" not in script.lower()
        assert "remove-item" not in script.lower()
