from __future__ import annotations

import copy
import hashlib
import random
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
import torch
from torch import nn

import vision_active_learning_loop.training.checkpoint_io as checkpoint_io
from vision_active_learning_loop.training.checkpoint_io import (
    CheckpointState,
    CheckpointVerificationError,
    capture_rng_state,
    checkpoint_state_digests,
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


def test_atomic_replace_failure_preserves_existing_checkpoint(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch a failed publication destroying the last verified checkpoint."""
    target = tmp_path / "step-000001.pt"
    save_checkpoint_atomic(_state(), target)
    original = target.read_bytes()

    monkeypatch.setattr(
        checkpoint_io.os,
        "replace",
        lambda *args: (_ for _ in ()).throw(OSError("injected rename failure")),
    )

    with pytest.raises(OSError, match="injected rename failure"):
        save_checkpoint_atomic(_state(), target)

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


def test_checkpoint_fsyncs_parent_after_atomic_replace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Catch acknowledging a checkpoint before its renamed directory entry is durable."""
    events: list[str] = []
    parent_descriptor = 999
    original_replace = checkpoint_io.os.replace

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

    def record_replace(source: Path, destination: Path) -> None:
        events.append("replace")
        original_replace(source, destination)

    monkeypatch.setattr(checkpoint_io.os, "replace", record_replace)

    save_checkpoint_atomic(_state(), tmp_path / "step-000001.pt")

    assert events == [
        "file-fsync",
        "parent-open",
        "parent-fsync",
        "parent-close",
        "replace",
        "parent-open",
        "parent-fsync",
        "parent-close",
    ]
