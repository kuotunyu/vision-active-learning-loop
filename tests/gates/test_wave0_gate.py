from __future__ import annotations

import copy
import json
import shutil
import subprocess
from pathlib import Path

import pytest

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
    evaluate_wave0,
    main,
)
from vision_active_learning_loop.models.assets import load_pinned_asset_specs

from ..artifacts.test_receipts import (
    MODEL_CONTRACT_INVARIANTS,
    build_valid_environment_receipt,
    build_valid_model_contract_receipt,
)
from ..models.test_assets import CONFIG_PATH, _valid_model_asset_receipt
from ..probes.test_training_feasibility import _receipt as valid_feasibility_receipt


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
    return ReplayReceiptPaths(
        environment=root / "environment.json",
        model_assets=root / "model-assets.json",
        model_contract=root / "model-contract.json",
        feasibility_a=root / "feasibility-a.json",
        feasibility_b=root / "feasibility-b.json",
    )


def _publish_attempt(attempt_root: Path, run_id: str = "run-a") -> ReplayReceiptPaths:
    paths = _paths(attempt_root)
    paths.environment.parent.mkdir(parents=True)
    specs = load_pinned_asset_specs(CONFIG_PATH)
    asset_receipt = _valid_model_asset_receipt(specs)
    asset_receipt["metadata"]["run_id"] = run_id
    model_contract = build_valid_model_contract_receipt()
    feasibility = valid_feasibility_receipt()
    if run_id != "run-a":
        raise AssertionError("test helper only supports the canonical fixture run")
    for path, document in (
        (paths.environment, build_valid_environment_receipt(run_id)),
        (paths.model_assets, asset_receipt),
        (paths.model_contract, model_contract),
        (paths.feasibility_a, feasibility),
        (paths.feasibility_b, copy.deepcopy(feasibility)),
    ):
        atomic_write_receipt(path, document)
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


def test_complete_a2_inputs_pass_with_exact_terminal_interpretation(
    valid_inputs: Wave0Inputs,
) -> None:
    result = evaluate_wave0(valid_inputs)

    assert not result.errors
    assert all(result.invariants.values())
    document = result.as_dict()
    assert document["normative"]["status"] == "PASS"
    assert (
        document["normative"]["interpretation"] == "WAVE0_A2_PASS / WAVE1_NOT_STARTED"
    )


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


def test_feasibility_ab_deterministic_divergence_is_rejected(
    valid_inputs: Wave0Inputs,
) -> None:
    _rewrite(
        valid_inputs.primary.feasibility_b,
        lambda document: document["normative"]["comparison"].update(
            {"sha256": "b" * 64}
        ),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["feasibility_ab_deterministic"] is False


def test_clean_replay_normative_divergence_is_rejected(
    valid_inputs: Wave0Inputs,
) -> None:
    _rewrite(
        valid_inputs.clean_b.feasibility_a,
        lambda document: document["normative"]["comparison"].update(
            {"sha256": "b" * 64}
        ),
    )

    result = evaluate_wave0(valid_inputs)

    assert result.invariants["clean_replays_deterministic"] is False


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
