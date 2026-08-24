from __future__ import annotations

import errno
import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

from vision_active_learning_loop.artifacts import no_clobber
from vision_active_learning_loop.artifacts.no_clobber import (
    NoClobberError,
    NoClobberUnsupportedError,
    create_directory_no_clobber,
    open_unique_staging_file,
    publish_staged_file_no_clobber,
)


def _make_directory_link(link: Path, target: Path, *, junction: bool) -> None:
    target.mkdir()
    if junction:
        if os.name != "nt":
            pytest.skip("Windows junction case")
        completed = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            pytest.skip(f"junction unavailable: {completed.stderr}")
        return
    try:
        link.symlink_to(target, target_is_directory=True)
    except OSError as error:
        pytest.skip(f"directory symlink unavailable: {error}")


@pytest.mark.parametrize(
    "existing_kind",
    ["empty-directory", "nonempty-directory", "file", "symlink", "junction"],
)
def test_feasibility_cli_rejects_preexisting_checkpoint_root_before_execution(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    existing_kind: str,
) -> None:
    """Catch reuse, merging, or cleanup of any prior checkpoint-root path."""
    checkpoint_root = tmp_path / "checkpoint-root"
    evidence = b"prior-evidence"
    if existing_kind == "empty-directory":
        checkpoint_root.mkdir()
    elif existing_kind == "nonempty-directory":
        checkpoint_root.mkdir()
        (checkpoint_root / "prior.bin").write_bytes(evidence)
    elif existing_kind == "file":
        checkpoint_root.write_bytes(evidence)
    else:
        target = tmp_path / f"{existing_kind}-target"
        _make_directory_link(
            checkpoint_root, target, junction=existing_kind == "junction"
        )
        (target / "prior.bin").write_bytes(evidence)

    output = tmp_path / "feasibility.json"
    model_contract = tmp_path / "model-contract.json"
    called = False

    def unexpected_execute(*args: object) -> dict[str, object]:
        nonlocal called
        called = True
        raise AssertionError("probe/GPU execution must not begin")

    monkeypatch.setattr(
        "vision_active_learning_loop.probes.training_feasibility.resolve_cli_paths",
        lambda *args: (model_contract, checkpoint_root, output),
    )
    monkeypatch.setattr(
        "vision_active_learning_loop.probes.training_feasibility._execute_probe",
        unexpected_execute,
    )

    from vision_active_learning_loop.probes.training_feasibility import main

    exit_code = main(
        [
            "--model-contract",
            str(model_contract),
            "--checkpoint-root",
            str(checkpoint_root),
            "--run-id",
            "run-a",
            "--output",
            str(output),
        ]
    )

    assert exit_code == 2
    assert called is False
    assert not output.exists()
    assert checkpoint_root.exists()
    if existing_kind == "file":
        assert checkpoint_root.read_bytes() == evidence
    elif existing_kind in {"nonempty-directory", "symlink", "junction"}:
        assert (checkpoint_root / "prior.bin").read_bytes() == evidence


def test_create_directory_no_clobber_has_exactly_one_race_winner(
    tmp_path: Path,
) -> None:
    """Catch check-then-mkdir allowing two workers to share one evidence root."""
    target = tmp_path / "checkpoint-root"
    barrier = Barrier(2)

    def claim() -> object:
        barrier.wait()
        try:
            return create_directory_no_clobber(target)
        except NoClobberError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(lambda _: claim(), range(2)))

    assert sum(result == target for result in results) == 1
    assert sum(isinstance(result, NoClobberError) for result in results) == 1
    assert target.is_dir()


def test_claimed_checkpoint_root_is_preserved_after_later_probe_failure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch failure cleanup erasing the newly claimed run evidence root."""
    checkpoint_root = tmp_path / "checkpoint-root"
    output = tmp_path / "feasibility.json"
    model_contract = tmp_path / "model-contract.json"
    monkeypatch.setattr(
        "vision_active_learning_loop.probes.training_feasibility.resolve_cli_paths",
        lambda *args: (model_contract, checkpoint_root, output),
    )

    from vision_active_learning_loop.probes.training_feasibility import (
        FeasibilityError,
        main,
    )

    monkeypatch.setattr(
        "vision_active_learning_loop.probes.training_feasibility._execute_probe",
        lambda *args: (_ for _ in ()).throw(FeasibilityError("later failure")),
    )

    assert (
        main(
            [
                "--model-contract",
                str(model_contract),
                "--checkpoint-root",
                str(checkpoint_root),
                "--run-id",
                "run-a",
                "--output",
                str(output),
            ]
        )
        == 2
    )
    assert checkpoint_root.is_dir()
    assert not output.exists()


def test_unique_stage_and_decisive_publication_are_same_directory(
    tmp_path: Path,
) -> None:
    destination = tmp_path / "checkpoint.pt"
    stage = open_unique_staging_file(destination)
    stage.handle.write(b"complete")
    stage.handle.flush()
    os.fsync(stage.handle.fileno())
    stage.handle.close()

    publish_staged_file_no_clobber(stage.path, destination)

    assert stage.path.parent == destination.parent
    assert destination.read_bytes() == b"complete"


@pytest.mark.parametrize(
    "error_code",
    [
        errno.EPERM,
        getattr(errno, "EOPNOTSUPP", errno.EPERM),
        getattr(errno, "ENOTSUP", errno.EPERM),
        errno.EXDEV,
    ],
)
def test_publish_fails_closed_when_safe_hard_link_is_unsupported(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error_code: int
) -> None:
    destination = tmp_path / "checkpoint.pt"
    stage = tmp_path / ".checkpoint.stage"
    stage.write_bytes(b"complete")
    monkeypatch.setattr(
        no_clobber.os,
        "link",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            OSError(error_code, "unsupported")
        ),
    )

    with pytest.raises(NoClobberUnsupportedError):
        publish_staged_file_no_clobber(stage, destination)

    assert not destination.exists()
    assert stage.read_bytes() == b"complete"
