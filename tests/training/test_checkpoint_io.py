from __future__ import annotations

import copy
import errno
import hashlib
import os
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

import numpy as np
import pytest
import torch
from torch import nn

from vision_active_learning_loop.artifacts.no_clobber import (
    NoClobberError,
    NoClobberUnsupportedError,
)
from vision_active_learning_loop.training import checkpoint_io
from vision_active_learning_loop.training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    capture_rng_state,
    checkpoint_state_digests,
    checkpoint_state_sha256,
    load_checkpoint_verified,
    restore_checkpoint_state,
    restore_rng_state,
    save_checkpoint_atomic,
    structured_state_sha256,
)

HASH = "a" * 64


def _objects() -> tuple[nn.Module, torch.optim.Optimizer, object]:
    model = nn.Sequential(nn.Linear(3, 4), nn.GELU(), nn.Linear(4, 2))
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.LambdaLR(optimizer, lambda _: 1.0)
    loss = model(torch.ones(2, 3)).square().mean()
    loss.backward()
    optimizer.step()
    scheduler.step()
    return model, optimizer, scheduler


def _state() -> CheckpointState:
    random.seed(17)
    np.random.seed(17)
    torch.manual_seed(17)
    model, optimizer, scheduler = _objects()
    return CheckpointState(
        model_state=copy.deepcopy(model.state_dict()),
        optimizer_state=copy.deepcopy(optimizer.state_dict()),
        scheduler_state=copy.deepcopy(scheduler.state_dict()),
        scaler_state=None,
        epoch=0,
        step=1,
        sampler_order_digest=hashlib.sha256(
            b'["wide-gradient","tall-checker"]'
        ).hexdigest(),
        rng_state=capture_rng_state(),
        input_digests={"model_contract_receipt": HASH},
    )


def test_checkpoint_round_trip_preserves_every_required_state(tmp_path: Path) -> None:
    """Catch a checkpoint omitting model, optimizer, scheduler, RNG, or sampler state."""
    state = _state()
    target = tmp_path / "step-000001.pt"

    digest = save_checkpoint_atomic(state, target)
    loaded = load_checkpoint_verified(
        target,
        digest,
        expected_input_digests={"model_contract_receipt": HASH},
    )

    assert checkpoint_state_digests(loaded) == checkpoint_state_digests(state)
    assert loaded.epoch == 0
    assert loaded.step == 1
    assert loaded.sampler_order_digest == state.sampler_order_digest
    assert target.is_file()
    assert not target.with_name(f"{target.name}.partial").exists()


def test_restore_checkpoint_rehydrates_objects_and_rng_before_resume(
    tmp_path: Path,
) -> None:
    """Catch a verified load that does not actually restore resumable state."""
    state = _state()
    target = tmp_path / "step-000001.pt"
    digest = save_checkpoint_atomic(state, target)
    loaded = load_checkpoint_verified(target, digest)
    model, optimizer, scheduler = _objects()
    for parameter in model.parameters():
        parameter.data.zero_()
    random.random()
    np.random.random()
    torch.rand(1)

    restored = restore_checkpoint_state(
        loaded,
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        scaler=None,
        expected_input_digests={"model_contract_receipt": HASH},
    )

    assert restored == checkpoint_state_digests(state)


@pytest.mark.parametrize("mode", ["truncate", "flip"], ids=["truncated", "corrupt"])
def test_corrupt_checkpoint_fails_before_deserialization(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    """Catch corrupted bytes reaching torch.load before their digest is verified."""
    target = tmp_path / "step-000001.pt"
    digest = save_checkpoint_atomic(_state(), target)
    raw = target.read_bytes()
    target.write_bytes(raw[: len(raw) // 2] if mode == "truncate" else raw[:-1] + b"x")
    called = False

    def forbidden_load(*args: object, **kwargs: object) -> object:
        nonlocal called
        called = True
        raise AssertionError("torch.load must not run for corrupt checkpoint bytes")

    monkeypatch.setattr(checkpoint_io.torch, "load", forbidden_load)

    with pytest.raises(CheckpointVerificationError, match="digest mismatch"):
        load_checkpoint_verified(target, digest)
    assert called is False


def test_input_digest_mismatch_fails_before_any_resume_mutation(tmp_path: Path) -> None:
    """Catch resuming a checkpoint created from a different model-contract receipt."""
    target = tmp_path / "step-000001.pt"
    digest = save_checkpoint_atomic(_state(), target)

    with pytest.raises(CheckpointVerificationError, match="input digest mismatch"):
        load_checkpoint_verified(
            target,
            digest,
            expected_input_digests={"model_contract_receipt": "b" * 64},
        )


@pytest.mark.parametrize(
    "mutation",
    [
        lambda state: CheckpointState(
            **{**state.__dict__, "rng_state": {}},
        ),
        lambda state: CheckpointState(
            **{**state.__dict__, "sampler_order_digest": "not-a-digest"},
        ),
        lambda state: CheckpointState(
            **{**state.__dict__, "scaler_state": {"scale": float("inf")}},
        ),
    ],
    ids=["rng-omission", "sampler-mismatch", "non-finite"],
)
def test_invalid_state_is_rejected_without_publication(
    tmp_path: Path, mutation: object
) -> None:
    """Catch incomplete or non-finite state being published as resumable."""
    assert callable(mutation)
    target = tmp_path / "step-000001.pt"

    with pytest.raises(CheckpointVerificationError):
        save_checkpoint_atomic(mutation(_state()), target)

    assert not target.exists()
    assert not target.with_name(f"{target.name}.partial").exists()


@pytest.mark.parametrize("existing_kind", ["file", "directory", "symlink", "junction"])
def test_checkpoint_destination_never_replaces_preexisting_path(
    tmp_path: Path, existing_kind: str
) -> None:
    """Catch any exact destination type being overwritten or reused."""
    target = tmp_path / "step-000001.pt"
    prior = b"prior-checkpoint-evidence"
    if existing_kind == "file":
        target.write_bytes(prior)
    elif existing_kind == "directory":
        target.mkdir()
        (target / "prior.bin").write_bytes(prior)
    elif existing_kind == "symlink":
        source = tmp_path / "source.bin"
        source.write_bytes(prior)
        try:
            target.symlink_to(source)
        except OSError as error:
            pytest.skip(f"file symlink unavailable: {error}")
    else:
        if os.name != "nt":
            pytest.skip("Windows junction case")
        source = tmp_path / "source-directory"
        source.mkdir()
        (source / "prior.bin").write_bytes(prior)
        completed = subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(target), str(source)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode != 0:
            pytest.skip(f"junction unavailable: {completed.stderr}")

    with pytest.raises(NoClobberError):
        save_checkpoint_atomic(_state(), target)

    if existing_kind == "file":
        assert target.read_bytes() == prior
    elif existing_kind in {"directory", "junction"}:
        assert (target / "prior.bin").read_bytes() == prior
    else:
        assert target.read_bytes() == prior


def test_two_checkpoint_writers_race_publishes_exactly_one_complete_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "step-000001.pt"
    first = _state()
    changed_model = copy.deepcopy(dict(first.model_state))
    first_name = next(iter(changed_model))
    changed_model[first_name] = changed_model[first_name] + 1
    second = replace(first, model_state=changed_model)
    barrier = Barrier(2)
    original_publish = checkpoint_io.publish_staged_file_no_clobber

    def synchronized_publish(stage: Path, destination: Path) -> None:
        barrier.wait()
        original_publish(stage, destination)

    monkeypatch.setattr(
        checkpoint_io, "publish_staged_file_no_clobber", synchronized_publish
    )

    def save(state: CheckpointState) -> object:
        try:
            return save_checkpoint_atomic(state, target)
        except NoClobberError as error:
            return error

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(save, (first, second)))

    digests = [result for result in results if isinstance(result, str)]
    assert len(digests) == 1
    assert sum(isinstance(result, NoClobberError) for result in results) == 1
    loaded = load_checkpoint_verified(target, digests[0])
    assert checkpoint_state_sha256(loaded) in {
        checkpoint_state_sha256(first),
        checkpoint_state_sha256(second),
    }


@pytest.mark.parametrize(
    "error_code",
    [
        errno.EPERM,
        getattr(errno, "EOPNOTSUPP", errno.EPERM),
        getattr(errno, "ENOTSUP", errno.EPERM),
        errno.EXDEV,
    ],
)
def test_checkpoint_publication_rejects_unsupported_link_semantics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, error_code: int
) -> None:
    target = tmp_path / "step-000001.pt"
    monkeypatch.setattr(
        checkpoint_io.os,
        "link",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            OSError(error_code, "unsupported")
        ),
    )

    with pytest.raises(NoClobberUnsupportedError):
        save_checkpoint_atomic(_state(), target)

    assert not target.exists()
    assert not list(tmp_path.glob("*.staging"))


def test_checkpoint_never_calls_replace_or_changes_existing_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch a failed publication destroying the last verified checkpoint."""
    target = tmp_path / "step-000001.pt"
    save_checkpoint_atomic(_state(), target)
    original = target.read_bytes()

    replace_called = False

    def forbidden_replace(*args: object) -> None:
        nonlocal replace_called
        replace_called = True
        raise AssertionError("os.replace is forbidden")

    monkeypatch.setattr(checkpoint_io.os, "replace", forbidden_replace)

    with pytest.raises(NoClobberError):
        save_checkpoint_atomic(_state(), target)

    assert replace_called is False
    assert target.read_bytes() == original
    assert not target.with_name(f"{target.name}.partial").exists()


def test_rng_preflight_failure_does_not_mutate_any_rng_stream(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Catch late CUDA validation after Python, NumPy, or CPU RNG was changed."""
    bad_rng = copy.deepcopy(capture_rng_state())
    bad_rng["torch_cuda"] = [torch.zeros(16, dtype=torch.uint8)]
    before = structured_state_sha256(capture_rng_state())
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    with pytest.raises(CheckpointVerificationError, match="CUDA RNG"):
        restore_rng_state(bad_rng)

    assert structured_state_sha256(capture_rng_state()) == before


def test_late_restore_failure_rolls_back_every_live_state() -> None:
    """Catch an incompatible optimizer leaving an already-mutated model behind."""
    target = _state()
    changed_model = copy.deepcopy(dict(target.model_state))
    first_name = next(iter(changed_model))
    changed_model[first_name] = changed_model[first_name] + 1
    invalid_optimizer = copy.deepcopy(dict(target.optimizer_state))
    invalid_optimizer["param_groups"][0]["params"] = []
    invalid = replace(
        target,
        model_state=changed_model,
        optimizer_state=invalid_optimizer,
    )
    model, optimizer, scheduler = _objects()
    before = {
        "model": structured_state_sha256(model.state_dict()),
        "optimizer": structured_state_sha256(optimizer.state_dict()),
        "scheduler": structured_state_sha256(scheduler.state_dict()),
        "rng": structured_state_sha256(capture_rng_state()),
    }

    with pytest.raises(CheckpointVerificationError, match="restore failed"):
        restore_checkpoint_state(
            invalid,
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            scaler=None,
            expected_input_digests={"model_contract_receipt": HASH},
        )

    after = {
        "model": structured_state_sha256(model.state_dict()),
        "optimizer": structured_state_sha256(optimizer.state_dict()),
        "scheduler": structured_state_sha256(scheduler.state_dict()),
        "rng": structured_state_sha256(capture_rng_state()),
    }
    assert after == before


def test_checkpoint_fsyncs_complete_stage_before_decisive_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch publication before complete staged bytes and parent durability."""
    events: list[str] = []
    parent_descriptor = 999
    original_link = checkpoint_io.os.link

    monkeypatch.setattr(
        checkpoint_io.os,
        "open",
        lambda directory, flags: events.append("parent-open") or parent_descriptor,
    )
    monkeypatch.setattr(
        checkpoint_io.os,
        "fsync",
        lambda descriptor: events.append(
            "parent-fsync" if descriptor == parent_descriptor else "file-fsync"
        ),
    )
    monkeypatch.setattr(
        checkpoint_io.os,
        "close",
        lambda descriptor: events.append("parent-close"),
    )

    def record_link(
        source: Path, destination: Path, *, follow_symlinks: bool = True
    ) -> None:
        events.append("link")
        original_link(source, destination, follow_symlinks=follow_symlinks)

    monkeypatch.setattr(checkpoint_io.os, "link", record_link)

    save_checkpoint_atomic(_state(), tmp_path / "step-000001.pt")

    assert events == [
        "file-fsync",
        "parent-open",
        "parent-fsync",
        "parent-close",
        "link",
    ]


def test_stage_cleanup_failure_cannot_invalidate_committed_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch best-effort stage cleanup removing or invalidating the winner."""
    target = tmp_path / "step-000001.pt"
    original_unlink = Path.unlink

    def fail_stage_cleanup(path: Path, *args: object, **kwargs: object) -> None:
        if path.suffix == ".staging":
            raise PermissionError("injected stage cleanup failure")
        original_unlink(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_stage_cleanup)

    digest = save_checkpoint_atomic(_state(), target)

    assert load_checkpoint_verified(target, digest).step == 1
    assert target.is_file()
