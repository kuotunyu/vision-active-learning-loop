"""Atomic, content-verified training checkpoints."""

from __future__ import annotations

import copy
import hashlib
import math
import os
import random
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch

from ..artifacts.digests import sha256_file
from ..artifacts.no_clobber import (
    open_unique_staging_file,
    publish_staged_file_no_clobber,
)


class CheckpointVerificationError(ValueError):
    """Raised before resume when checkpoint bytes or state are untrustworthy."""


_CHECKPOINT_MAGIC = "vision-active-learning-loop-checkpoint"
_CHECKPOINT_SCHEMA_VERSION = 1
_RNG_KEYS = frozenset({"python", "numpy", "torch_cpu", "torch_cuda"})


@dataclass(frozen=True)
class CheckpointState:
    """Every state required to resume one deterministic training stream."""

    model_state: Mapping[str, Any]
    optimizer_state: Mapping[str, Any]
    scheduler_state: Mapping[str, Any] | None
    scaler_state: Mapping[str, Any] | None
    epoch: int
    step: int
    sampler_order_digest: str
    rng_state: Mapping[str, Any]
    input_digests: Mapping[str, str]


def capture_rng_state() -> dict[str, object]:
    """Capture Python, NumPy, torch CPU, and initialized CUDA RNG streams."""
    numpy_state = np.random.get_state()
    cuda_states = (
        [state.cpu().clone() for state in torch.cuda.get_rng_state_all()]
        if torch.cuda.is_initialized()
        else []
    )
    return {
        "python": random.getstate(),
        "numpy": {
            "bit_generator": str(numpy_state[0]),
            "keys": numpy_state[1].astype(np.uint32, copy=False).tolist(),
            "position": int(numpy_state[2]),
            "has_gauss": int(numpy_state[3]),
            "cached_gaussian": float(numpy_state[4]),
        },
        "torch_cpu": torch.get_rng_state().cpu().clone(),
        "torch_cuda": cuda_states,
    }


def restore_rng_state(state: Mapping[str, Any]) -> None:
    """Restore a previously validated RNG capture without changing its streams."""
    _validate_rng_state(state)
    python_state = state["python"]
    numpy_state = state["numpy"]
    torch_cpu = state["torch_cpu"]
    torch_cuda = state["torch_cuda"]
    assert isinstance(numpy_state, Mapping)
    assert isinstance(torch_cpu, torch.Tensor)
    assert isinstance(torch_cuda, list)
    random.setstate(_as_tuple_tree(python_state))
    np.random.set_state(
        (
            str(numpy_state["bit_generator"]),
            np.asarray(numpy_state["keys"], dtype=np.uint32),
            int(numpy_state["position"]),
            int(numpy_state["has_gauss"]),
            float(numpy_state["cached_gaussian"]),
        )
    )
    torch.set_rng_state(torch_cpu.cpu())
    if torch_cuda:
        torch.cuda.set_rng_state_all([item.cpu() for item in torch_cuda])


def checkpoint_state_digests(state: CheckpointState) -> dict[str, str]:
    """Return ordered component digests used for round-trip verification."""
    _validate_checkpoint_state(state)
    return {
        "model": _structured_digest(state.model_state),
        "optimizer": _structured_digest(state.optimizer_state),
        "scheduler": _structured_digest(state.scheduler_state),
        "scaler": _structured_digest(state.scaler_state),
        "rng": _structured_digest(state.rng_state),
        "sampler": state.sampler_order_digest,
    }


def checkpoint_state_sha256(state: CheckpointState) -> str:
    """Bind component digests to progress counters and immutable inputs."""
    return _structured_digest(
        {
            "schema_version": _CHECKPOINT_SCHEMA_VERSION,
            "state_digests": checkpoint_state_digests(state),
            "epoch": state.epoch,
            "step": state.step,
            "input_digests": dict(state.input_digests),
        }
    )


def structured_state_sha256(value: object) -> str:
    """Hash nested tensor state independently of tensor device placement."""
    return _structured_digest(value)


def save_checkpoint_atomic(state: CheckpointState, target: Path) -> str:
    """Atomically publish a content-bound checkpoint and return its file digest."""
    _validate_checkpoint_state(state)
    target = Path(target)
    envelope = {
        "magic": _CHECKPOINT_MAGIC,
        "schema_version": _CHECKPOINT_SCHEMA_VERSION,
        "state": _state_payload(state),
        "state_digests": checkpoint_state_digests(state),
        "state_sha256": checkpoint_state_sha256(state),
    }
    stage = open_unique_staging_file(target)
    try:
        try:
            torch.save(envelope, stage.handle)
            stage.handle.flush()
            os.fsync(stage.handle.fileno())
        finally:
            stage.handle.close()
        digest = sha256_file(stage.path)
        _fsync_parent(target.parent)
        publish_staged_file_no_clobber(stage.path, target)
        return digest
    finally:
        if not stage.handle.closed:
            stage.handle.close()
        try:
            stage.path.unlink()
        except OSError:
            pass


def load_checkpoint_verified(
    target: Path,
    expected_digest: str,
    *,
    expected_input_digests: Mapping[str, str] | None = None,
) -> CheckpointState:
    """Verify exact bytes and internal state bindings before deserializing for resume."""
    target = Path(target)
    if not _is_sha256(expected_digest):
        raise CheckpointVerificationError("expected checkpoint digest is invalid")
    try:
        actual_digest = sha256_file(target)
    except OSError as error:
        raise CheckpointVerificationError("checkpoint is unavailable") from error
    if actual_digest != expected_digest:
        raise CheckpointVerificationError("checkpoint digest mismatch")
    try:
        envelope = torch.load(target, map_location="cpu", weights_only=True)
    except Exception as error:
        raise CheckpointVerificationError("checkpoint payload is unreadable") from error
    if not isinstance(envelope, Mapping):
        raise CheckpointVerificationError("checkpoint envelope must be an object")
    if set(envelope) != {
        "magic",
        "schema_version",
        "state",
        "state_digests",
        "state_sha256",
    }:
        raise CheckpointVerificationError("checkpoint envelope fields mismatch")
    if envelope.get("magic") != _CHECKPOINT_MAGIC:
        raise CheckpointVerificationError("checkpoint magic mismatch")
    if envelope.get("schema_version") != _CHECKPOINT_SCHEMA_VERSION:
        raise CheckpointVerificationError("checkpoint schema mismatch")
    state = _state_from_payload(envelope.get("state"))
    expected_states = checkpoint_state_digests(state)
    if envelope.get("state_digests") != expected_states:
        raise CheckpointVerificationError("checkpoint state digest mismatch")
    if envelope.get("state_sha256") != checkpoint_state_sha256(state):
        raise CheckpointVerificationError("checkpoint state content mismatch")
    _verify_input_digests(state.input_digests, expected_input_digests)
    return state


def restore_checkpoint_state(
    state: CheckpointState,
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any | None,
    scaler: Any | None,
    expected_input_digests: Mapping[str, str],
) -> dict[str, str]:
    """Restore all state and prove the live objects match before training continues."""
    _validate_checkpoint_state(state)
    _verify_input_digests(state.input_digests, expected_input_digests)
    if (scheduler is None) != (state.scheduler_state is None):
        raise CheckpointVerificationError("scheduler presence mismatch")
    if (scaler is None) != (state.scaler_state is None):
        raise CheckpointVerificationError("scaler presence mismatch")
    backup_model = _clone_to_cpu(model.state_dict())
    backup_optimizer = _clone_to_cpu(optimizer.state_dict())
    backup_scheduler = _clone_to_cpu(
        None if scheduler is None else scheduler.state_dict()
    )
    backup_scaler = _clone_to_cpu(None if scaler is None else scaler.state_dict())
    backup_rng = capture_rng_state()
    try:
        _load_live_state(
            model=model,
            optimizer=optimizer,
            scheduler=scheduler,
            scaler=scaler,
            model_state=state.model_state,
            optimizer_state=state.optimizer_state,
            scheduler_state=state.scheduler_state,
            scaler_state=state.scaler_state,
        )
        restore_rng_state(state.rng_state)
        observed = {
            "model": _structured_digest(model.state_dict()),
            "optimizer": _structured_digest(optimizer.state_dict()),
            "scheduler": _structured_digest(
                None if scheduler is None else scheduler.state_dict()
            ),
            "scaler": _structured_digest(
                None if scaler is None else scaler.state_dict()
            ),
            "rng": _structured_digest(capture_rng_state()),
            "sampler": state.sampler_order_digest,
        }
        expected = checkpoint_state_digests(state)
        if observed != expected:
            raise CheckpointVerificationError("restored state mismatch")
        return observed
    except Exception as error:
        try:
            _load_live_state(
                model=model,
                optimizer=optimizer,
                scheduler=scheduler,
                scaler=scaler,
                model_state=backup_model,
                optimizer_state=backup_optimizer,
                scheduler_state=backup_scheduler,
                scaler_state=backup_scaler,
            )
            restore_rng_state(backup_rng)
        except Exception as rollback_error:
            raise CheckpointVerificationError(
                "checkpoint restore failed and rollback failed"
            ) from rollback_error
        raise CheckpointVerificationError("checkpoint restore failed") from error


def _state_payload(state: CheckpointState) -> dict[str, object]:
    return {
        "model_state": copy.deepcopy(dict(state.model_state)),
        "optimizer_state": copy.deepcopy(dict(state.optimizer_state)),
        "scheduler_state": copy.deepcopy(
            None if state.scheduler_state is None else dict(state.scheduler_state)
        ),
        "scaler_state": copy.deepcopy(
            None if state.scaler_state is None else dict(state.scaler_state)
        ),
        "epoch": state.epoch,
        "step": state.step,
        "sampler_order_digest": state.sampler_order_digest,
        "rng_state": copy.deepcopy(dict(state.rng_state)),
        "input_digests": dict(state.input_digests),
    }


def _state_from_payload(value: object) -> CheckpointState:
    if not isinstance(value, Mapping):
        raise CheckpointVerificationError("checkpoint state must be an object")
    required = {
        "model_state",
        "optimizer_state",
        "scheduler_state",
        "scaler_state",
        "epoch",
        "step",
        "sampler_order_digest",
        "rng_state",
        "input_digests",
    }
    if set(value) != required:
        raise CheckpointVerificationError("checkpoint state fields mismatch")
    for name in ("model_state", "optimizer_state", "rng_state", "input_digests"):
        if not isinstance(value[name], Mapping):
            raise CheckpointVerificationError(f"{name} must be an object")
    for name in ("scheduler_state", "scaler_state"):
        if value[name] is not None and not isinstance(value[name], Mapping):
            raise CheckpointVerificationError(f"{name} must be an object or null")
    state = CheckpointState(
        model_state=value["model_state"],
        optimizer_state=value["optimizer_state"],
        scheduler_state=value["scheduler_state"],
        scaler_state=value["scaler_state"],
        epoch=value["epoch"],
        step=value["step"],
        sampler_order_digest=value["sampler_order_digest"],
        rng_state=value["rng_state"],
        input_digests=value["input_digests"],
    )
    _validate_checkpoint_state(state)
    return state


def _validate_checkpoint_state(state: CheckpointState) -> None:
    if not isinstance(state, CheckpointState):
        raise CheckpointVerificationError("checkpoint state type mismatch")
    if not isinstance(state.model_state, Mapping) or not state.model_state:
        raise CheckpointVerificationError("model state must be a non-empty object")
    if not isinstance(state.optimizer_state, Mapping) or not state.optimizer_state:
        raise CheckpointVerificationError("optimizer state must be a non-empty object")
    for name, value in (("epoch", state.epoch), ("step", state.step)):
        if type(value) is not int or value < 0:
            raise CheckpointVerificationError(f"{name} must be a non-negative integer")
    if not _is_sha256(state.sampler_order_digest):
        raise CheckpointVerificationError("sampler order digest is invalid")
    if not isinstance(state.input_digests, Mapping) or not state.input_digests:
        raise CheckpointVerificationError("input digests must be a non-empty object")
    if any(
        not isinstance(name, str) or not name or not _is_sha256(digest)
        for name, digest in state.input_digests.items()
    ):
        raise CheckpointVerificationError("input digest is invalid")
    _validate_rng_state(state.rng_state)
    _reject_non_finite(state)


def _validate_rng_state(state: Mapping[str, Any]) -> None:
    if not isinstance(state, Mapping) or set(state) != _RNG_KEYS:
        raise CheckpointVerificationError("RNG state fields mismatch")
    numpy_state = state.get("numpy")
    if not isinstance(numpy_state, Mapping) or set(numpy_state) != {
        "bit_generator",
        "keys",
        "position",
        "has_gauss",
        "cached_gaussian",
    }:
        raise CheckpointVerificationError("NumPy RNG state fields mismatch")
    try:
        python_state = _as_tuple_tree(state.get("python"))
        random.Random().setstate(python_state)
    except Exception as error:
        raise CheckpointVerificationError("Python RNG state is invalid") from error
    try:
        numpy_tuple = (
            str(numpy_state["bit_generator"]),
            np.asarray(numpy_state["keys"], dtype=np.uint32),
            int(numpy_state["position"]),
            int(numpy_state["has_gauss"]),
            float(numpy_state["cached_gaussian"]),
        )
        np.random.RandomState().set_state(numpy_tuple)
    except Exception as error:
        raise CheckpointVerificationError("NumPy RNG state is invalid") from error
    torch_cpu = state.get("torch_cpu")
    if (
        not isinstance(torch_cpu, torch.Tensor)
        or torch_cpu.dtype != torch.uint8
        or torch_cpu.ndim != 1
    ):
        raise CheckpointVerificationError("torch CPU RNG state is missing")
    try:
        torch.Generator(device="cpu").set_state(torch_cpu.cpu())
    except Exception as error:
        raise CheckpointVerificationError("torch CPU RNG state is invalid") from error
    cuda_state = state.get("torch_cuda")
    if not isinstance(cuda_state, list) or any(
        not isinstance(item, torch.Tensor)
        or item.dtype != torch.uint8
        or item.ndim != 1
        for item in cuda_state
    ):
        raise CheckpointVerificationError("torch CUDA RNG state is invalid")
    if cuda_state:
        if not torch.cuda.is_available():
            raise CheckpointVerificationError("CUDA RNG state cannot be restored")
        if len(cuda_state) != torch.cuda.device_count():
            raise CheckpointVerificationError("CUDA RNG device-count mismatch")
        for index, item in enumerate(cuda_state):
            try:
                torch.Generator(device=f"cuda:{index}").set_state(item.cpu())
            except Exception as error:
                raise CheckpointVerificationError(
                    "torch CUDA RNG state is invalid"
                ) from error


def _load_live_state(
    *,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: Any | None,
    scaler: Any | None,
    model_state: Mapping[str, Any],
    optimizer_state: Mapping[str, Any],
    scheduler_state: Mapping[str, Any] | None,
    scaler_state: Mapping[str, Any] | None,
) -> None:
    model.load_state_dict(model_state, strict=True)
    optimizer.load_state_dict(optimizer_state)
    if scheduler is not None:
        scheduler.load_state_dict(scheduler_state)
    if scaler is not None:
        scaler.load_state_dict(scaler_state)


def _clone_to_cpu(value: object) -> Any:
    if isinstance(value, torch.Tensor):
        return value.detach().cpu().clone()
    if isinstance(value, Mapping):
        return {key: _clone_to_cpu(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return tuple(_clone_to_cpu(item) for item in value)
    if isinstance(value, list):
        return [_clone_to_cpu(item) for item in value]
    return copy.deepcopy(value)


def _verify_input_digests(
    actual: Mapping[str, str], expected: Mapping[str, str] | None
) -> None:
    if expected is not None and dict(actual) != dict(expected):
        raise CheckpointVerificationError("checkpoint input digest mismatch")


def _structured_digest(value: object) -> str:
    digest = hashlib.sha256()
    _update_digest(digest, value)
    return digest.hexdigest()


def _update_digest(digest: Any, value: object) -> None:
    if value is None:
        digest.update(b"none;")
    elif type(value) is bool:
        digest.update(b"bool:1;" if value else b"bool:0;")
    elif type(value) is int:
        digest.update(f"int:{value};".encode("ascii"))
    elif type(value) is float:
        if not math.isfinite(value):
            raise CheckpointVerificationError("checkpoint contains non-finite value")
        digest.update(f"float:{value.hex()};".encode("ascii"))
    elif isinstance(value, str):
        encoded = value.encode("utf-8")
        digest.update(f"str:{len(encoded)}:".encode("ascii"))
        digest.update(encoded)
    elif isinstance(value, bytes):
        digest.update(f"bytes:{len(value)}:".encode("ascii"))
        digest.update(value)
    elif isinstance(value, torch.Tensor):
        tensor = value.detach().cpu().contiguous()
        digest.update(b"tensor:")
        _update_digest(digest, str(tensor.dtype))
        _update_digest(digest, list(tensor.shape))
        raw = tensor.reshape(-1).view(torch.uint8).numpy().tobytes()
        digest.update(f"raw:{len(raw)}:".encode("ascii"))
        digest.update(raw)
    elif isinstance(value, Mapping):
        digest.update(f"mapping:{len(value)}:".encode("ascii"))
        for key in sorted(value, key=lambda item: (type(item).__name__, repr(item))):
            _update_digest(digest, key)
            _update_digest(digest, value[key])
    elif isinstance(value, tuple):
        digest.update(f"tuple:{len(value)}:".encode("ascii"))
        for item in value:
            _update_digest(digest, item)
    elif isinstance(value, list):
        digest.update(f"list:{len(value)}:".encode("ascii"))
        for item in value:
            _update_digest(digest, item)
    elif isinstance(value, np.generic):
        _update_digest(digest, value.item())
    else:
        raise CheckpointVerificationError(
            f"unsupported checkpoint value: {type(value).__name__}"
        )


def _reject_non_finite(value: object) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise CheckpointVerificationError("checkpoint contains non-finite value")
    if isinstance(value, torch.Tensor) and (
        value.is_floating_point() or value.is_complex()
    ):
        if not bool(torch.isfinite(value).all()):
            raise CheckpointVerificationError("checkpoint contains non-finite tensor")
    elif isinstance(value, Mapping):
        for item in value.values():
            _reject_non_finite(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_non_finite(item)
    elif hasattr(value, "__dict__"):
        for item in vars(value).values():
            _reject_non_finite(item)


def _as_tuple_tree(value: object) -> tuple[Any, ...]:
    if not isinstance(value, (tuple, list)):
        raise CheckpointVerificationError("Python RNG state is invalid")
    return tuple(
        _as_tuple_tree(item) if isinstance(item, (tuple, list)) else item
        for item in value
    )


def _is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _fsync_parent(directory: Path) -> None:
    try:
        descriptor = os.open(directory, os.O_RDONLY)
    except PermissionError:
        if os.name == "nt":
            return
        raise
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
