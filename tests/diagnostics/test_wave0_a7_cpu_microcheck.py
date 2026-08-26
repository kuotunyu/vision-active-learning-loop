"""Behavior tests for the production-only Wave 0 A7 CPU micro-check."""

from __future__ import annotations

import builtins
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "run_wave0_a7_cpu_microcheck.py"
_SOURCE_PATHS = (
    "scripts/start_wave0_a7.ps1",
    "scripts/run_wave0_a7_cpu_microcheck.py",
    "scripts/run_wave0_a7.ps1",
    "src/vision_active_learning_loop/diagnostics/grid_sample_attribution.py",
    "src/vision_active_learning_loop/diagnostics/tensor_evidence.py",
    "src/vision_active_learning_loop/artifacts/receipts.py",
    "schemas/grid-sample-attribution-receipt.schema.json",
)


def _load_microcheck() -> ModuleType:
    if not _SCRIPT.is_file():
        raise AssertionError("production A7 CPU micro-check script is missing")
    spec = importlib.util.spec_from_file_location("a7_cpu_microcheck", _SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_workspace(tmp_path: Path) -> tuple[Path, Path]:
    workspace = tmp_path / "workspace"
    for relative in _SOURCE_PATHS:
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        source = _ROOT / relative
        if source.is_file():
            shutil.copyfile(source, destination)
        elif relative == "scripts/start_wave0_a7.ps1":
            destination.write_text("param()\n", encoding="utf-8")
        else:
            raise AssertionError(f"missing source fixture: {relative}")

    files = []
    for relative in _SOURCE_PATHS:
        payload = (workspace / relative).read_bytes()
        files.append({"path": relative, "sha256": hashlib.sha256(payload).hexdigest()})
    inventory = {
        "schema_version": 1,
        "source_commit": "a" * 40,
        "files": files,
    }
    inventory_path = tmp_path / "source-inventory.json"
    inventory_path.write_text(
        json.dumps(inventory, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    return workspace, inventory_path


def test_microcheck_discovers_a7_command_before_diagnostic_import(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)
    observed: list[str] = []
    real_import = builtins.__import__

    def recording_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "vision_active_learning_loop.cli_manifest":
            observed.append(name)
        if name == "vision_active_learning_loop.diagnostics" and (
            "grid_sample_attribution" in fromlist
        ):
            observed.append(
                "vision_active_learning_loop.diagnostics.grid_sample_attribution"
            )
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", recording_import)

    result = module.run_microcheck(workspace, inventory_path)

    assert result["manifest_target"] == (
        "vision_active_learning_loop.diagnostics.grid_sample_attribution:main"
    )
    assert observed.index("vision_active_learning_loop.cli_manifest") < observed.index(
        "vision_active_learning_loop.diagnostics.grid_sample_attribution"
    )


def test_microcheck_rejects_changed_source_inventory(tmp_path: Path) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)
    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    inventory["files"][0]["sha256"] = "0" * 64
    inventory_path.write_text(
        json.dumps(inventory, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )

    with pytest.raises(module.MicrocheckError, match="^source inventory mismatch$"):
        module.run_microcheck(workspace, inventory_path)


def test_microcheck_does_not_import_pytest_tests_or_models(tmp_path: Path) -> None:
    _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)
    driver = tmp_path / "driver.py"
    driver.write_text(
        """
import builtins
import importlib.util
import json
import pathlib
import sys

script, workspace, inventory = map(pathlib.Path, sys.argv[1:])
real_import = builtins.__import__

def guarded(name, globals=None, locals=None, fromlist=(), level=0):
    if name == "pytest" or name.startswith("tests") or name.startswith(
        "vision_active_learning_loop.models"
    ):
        raise ImportError(f"forbidden production import: {name}")
    return real_import(name, globals, locals, fromlist, level)

builtins.__import__ = guarded
spec = importlib.util.spec_from_file_location("a7_cpu_microcheck_subprocess", script)
module = importlib.util.module_from_spec(spec)
assert spec is not None and spec.loader is not None
spec.loader.exec_module(module)
print(json.dumps(module.run_microcheck(workspace, inventory), sort_keys=True))
""".strip()
        + "\n",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    completed = subprocess.run(
        [
            sys.executable,
            str(driver),
            str(_SCRIPT),
            str(workspace),
            str(inventory_path),
        ],
        cwd=_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert json.loads(completed.stdout)["status"] == "RECORDED"


def test_microcheck_proves_four_canonical_dtypes(tmp_path: Path) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)

    result = module.run_microcheck(workspace, inventory_path)

    assert result["canonical_dtypes"] == [
        "bfloat16",
        "float16",
        "float32",
        "float64",
    ]


def test_microcheck_round_trips_exact_27_tensor_snapshot(tmp_path: Path) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)
    expected_names = sorted(
        f"decoder-{decoder}/feature-{feature}.{role}"
        for decoder in range(3)
        for feature in range(3)
        for role in (
            "forward_value",
            "forward_grid",
            "incoming_result_gradient",
        )
    )

    result = module.run_microcheck(workspace, inventory_path)

    assert result["snapshot_tensor_count"] == 27
    assert result["snapshot_names"] == expected_names


def test_microcheck_rejects_corrupted_snapshot(tmp_path: Path) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)

    result = module.run_microcheck(workspace, inventory_path)

    assert result["snapshot_corruption_rejected"] is True


def test_microcheck_validates_four_closed_receipt_kinds(tmp_path: Path) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)

    result = module.run_microcheck(workspace, inventory_path)

    assert result["receipt_kinds"] == [
        "control",
        "instrumented",
        "isolated-vjp",
        "aggregate",
    ]


def test_microcheck_exercises_three_literal_classifier_branches(
    tmp_path: Path,
) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)

    result = module.run_microcheck(workspace, inventory_path)

    assert result["classifier_statuses"] == [
        "ATTRIBUTED",
        "INCONCLUSIVE",
        "NOT_ATTRIBUTED",
    ]


def test_microcheck_finishes_without_cuda_initialization(tmp_path: Path) -> None:
    module = _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)

    result = module.run_microcheck(workspace, inventory_path)

    assert result["cuda_initialized"] is False


def test_microcheck_cli_emits_one_json_line(tmp_path: Path) -> None:
    _load_microcheck()
    workspace, inventory_path = _write_workspace(tmp_path)
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"

    completed = subprocess.run(
        [
            sys.executable,
            str(_SCRIPT),
            "--workspace-root",
            str(workspace),
            "--source-inventory",
            str(inventory_path),
        ],
        cwd=_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stderr == ""
    assert completed.stdout.endswith("\n")
    assert len(completed.stdout.splitlines()) == 1
    assert json.loads(completed.stdout)["status"] == "RECORDED"
