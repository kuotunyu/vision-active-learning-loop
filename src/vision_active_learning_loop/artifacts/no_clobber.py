"""Atomic create-if-absent primitives for immutable Wave 0 evidence."""

from __future__ import annotations

import errno
import os
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO


class NoClobberError(FileExistsError):
    """Raised when an immutable evidence destination already exists."""


class NoClobberUnsupportedError(OSError):
    """Raised when the filesystem cannot guarantee safe publication."""


@dataclass
class StagingFile:
    """One exclusively created same-directory staging file."""

    path: Path
    handle: BinaryIO


def _is_link_or_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (callable(is_junction) and bool(is_junction()))


def _verified_parent(path: Path) -> Path:
    parent = Path(path).parent
    if _is_link_or_junction(parent):
        raise OSError("evidence parent link or junction is forbidden")
    try:
        resolved = parent.resolve(strict=True)
    except OSError as error:
        raise OSError("evidence parent directory is unavailable") from error
    if not resolved.is_dir() or resolved != parent.absolute():
        raise OSError("evidence parent must be an existing non-link directory")
    return parent


def create_directory_no_clobber(path: Path) -> Path:
    """Atomically claim one absent directory below an existing verified parent."""
    target = Path(path)
    _verified_parent(target)
    try:
        target.mkdir(parents=False, exist_ok=False)
    except OSError as error:
        if isinstance(error, FileExistsError) or error.errno == errno.EEXIST:
            raise NoClobberError(
                f"immutable evidence destination already exists: {target.name}"
            ) from error
        raise
    return target


def open_unique_staging_file(destination: Path) -> StagingFile:
    """Exclusively open one UUID-named stage beside an immutable destination."""
    target = Path(destination)
    parent = _verified_parent(target)
    stage = parent / f".{target.name}.{uuid.uuid4().hex}.staging"
    return StagingFile(path=stage, handle=stage.open("xb"))


def publish_staged_file_no_clobber(staging: Path, destination: Path) -> None:
    """Atomically create an absent destination as a hard link to a complete stage."""
    stage = Path(staging)
    target = Path(destination)
    stage_parent = _verified_parent(stage)
    target_parent = _verified_parent(target)
    if stage_parent.absolute() != target_parent.absolute():
        raise OSError("staging file must share the destination directory")
    if _is_link_or_junction(stage) or not stage.is_file():
        raise OSError("staging path must be a regular non-link file")
    try:
        os.link(stage, target, follow_symlinks=False)
    except OSError as error:
        if isinstance(error, FileExistsError) or error.errno == errno.EEXIST:
            raise NoClobberError(
                f"immutable evidence destination already exists: {target.name}"
            ) from error
        unsupported = {
            errno.EPERM,
            errno.EXDEV,
            getattr(errno, "EOPNOTSUPP", errno.EPERM),
            getattr(errno, "ENOTSUP", errno.EPERM),
        }
        if error.errno in unsupported:
            raise NoClobberUnsupportedError(
                error.errno,
                "filesystem cannot guarantee atomic no-clobber publication",
            ) from error
        raise
