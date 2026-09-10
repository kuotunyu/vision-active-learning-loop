"""Contracts for `val lite gate`, the Section 8 check between baseline and run."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from vision_active_learning_loop.lite.gate import gate_main


def _experiment(
    root: Path,
    *,
    decreased: bool = True,
    warnings: int | None = 9,
    suffix: str = "shared-0.02",
) -> Path:
    fit = root / "fits" / suffix
    fit.mkdir(parents=True)
    (root / f"metrics-{suffix}.json").write_text(
        json.dumps(
            {
                "loss": {
                    "decreased": decreased,
                    "final": 1.0,
                    "first_window_median": 2.0,
                    "last_window_median": 1.0 if decreased else 3.0,
                },
                "metrics": {"mAP50_95": 0.123},
            }
        ),
        encoding="utf-8",
    )
    environment = {"device": "cuda"}
    if warnings is not None:
        environment["allowlisted_backward_warnings"] = warnings
    (fit / "fit-receipt.json").write_text(
        json.dumps({"normative": {"environment": environment}}), encoding="utf-8"
    )
    return root


def test_gate_passes_when_loss_decreased_and_nine_warnings_on_cuda(
    tmp_path: Path, capsys
) -> None:
    root = _experiment(tmp_path / "exp")

    exit_code = gate_main(["--experiment-dir", str(root), "--device", "cuda"])

    out = capsys.readouterr().out
    assert exit_code == 0
    assert out.startswith("PASS ")
    assert '"mAP50_95": 0.123' in out


def test_gate_fails_when_loss_did_not_decrease(tmp_path: Path, capsys) -> None:
    root = _experiment(tmp_path / "exp", decreased=False)

    exit_code = gate_main(["--experiment-dir", str(root), "--device", "cuda"])

    assert exit_code == 2
    assert capsys.readouterr().out.startswith("FAIL ")


@pytest.mark.parametrize("warnings", [8, 10, None])
def test_gate_fails_on_cuda_without_exactly_nine_warnings(
    tmp_path: Path, capsys, warnings
) -> None:
    root = _experiment(tmp_path / "exp", warnings=warnings)

    exit_code = gate_main(["--experiment-dir", str(root), "--device", "cuda"])

    assert exit_code == 2
    assert capsys.readouterr().out.startswith("FAIL ")


def test_gate_ignores_the_warning_count_on_cpu(tmp_path: Path, capsys) -> None:
    root = _experiment(tmp_path / "exp", warnings=None)

    exit_code = gate_main(["--experiment-dir", str(root), "--device", "cpu"])

    assert exit_code == 0
    assert capsys.readouterr().out.startswith("PASS ")


def test_gate_can_check_the_reference_fit_instead(tmp_path: Path, capsys) -> None:
    root = _experiment(tmp_path / "ref", suffix="reference-1.00", decreased=False)

    exit_code = gate_main(
        ["--experiment-dir", str(root), "--device", "cuda", "--role", "reference"]
    )

    assert exit_code == 2
    assert capsys.readouterr().out.startswith("FAIL ")
    # The default role still looks for the shared fit, which this root lacks.
    assert gate_main(["--experiment-dir", str(root), "--device", "cuda"]) == 3


def test_gate_reports_missing_evidence_as_an_input_error(tmp_path: Path) -> None:
    exit_code = gate_main(
        ["--experiment-dir", str(tmp_path / "absent"), "--device", "cuda"]
    )

    assert exit_code == 3
