"""Contracts for scripts/run_lite_seed17.ps1 that hold without a GPU."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "run_lite_seed17.ps1"
POWERSHELL = shutil.which("powershell")
requires_powershell = pytest.mark.skipif(
    POWERSHELL is None, reason="Windows PowerShell is required"
)


def _run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            POWERSHELL,
            "-NoProfile",
            "-NonInteractive",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(SCRIPT),
            *arguments,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )


def _overrides(root: Path, *, manifest_exists: bool = True) -> list[str]:
    (root / "images").mkdir(parents=True)
    (root / "snapshot").mkdir()
    (root / "public-pool.json").write_text("{}", encoding="utf-8")
    if manifest_exists:
        (root / "manifest.json").write_text("{}", encoding="utf-8")
    return [
        "-Manifest",
        str(root / "manifest.json"),
        "-PublicView",
        str(root / "public-pool.json"),
        "-Images",
        str(root / "images"),
        "-Snapshot",
        str(root / "snapshot"),
        "-OutputRoot",
        str(root / "out"),
    ]


@requires_powershell
def test_script_parses_under_windows_powershell() -> None:
    probe = (
        "$tokens=$null;$errors=$null;"
        "[System.Management.Automation.Language.Parser]::ParseFile("
        f"'{SCRIPT}',[ref]$tokens,[ref]$errors)|Out-Null;"
        "Write-Output $errors.Count"
    )
    completed = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", probe],
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "0"


@requires_powershell
def test_dry_run_reports_every_input_and_launches_nothing(tmp_path: Path) -> None:
    completed = _run("-DryRun", *_overrides(tmp_path))

    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "preflight ok (dry run; nothing launched)" in completed.stdout
    assert "MISSING" not in completed.stdout
    assert not (tmp_path / "out" / "RUNNING.lock").exists()


@requires_powershell
def test_dry_run_fails_closed_on_a_missing_input(tmp_path: Path) -> None:
    completed = _run("-DryRun", *_overrides(tmp_path, manifest_exists=False))

    assert completed.returncode == 3
    assert "MISSING manifest" in completed.stdout
