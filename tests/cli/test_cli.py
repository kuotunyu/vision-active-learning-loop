import sys
from pathlib import Path

import pytest

from vision_active_learning_loop.cli_manifest import (
    DuplicateCommandError,
    InvalidCommandError,
    build_manifest,
)


def _write_command_module(source_root: Path) -> None:
    package = source_root / "vision_active_learning_loop"
    package.mkdir(parents=True)
    (package / "evaluation.py").write_text(
        """
from vision_active_learning_loop.cli_manifest import command

@command("probe model-contract")
def main() -> int:
    return 0
""".lstrip(),
        encoding="utf-8",
    )


def test_cli_manifest_is_lazy_and_rejects_duplicate_paths(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    _write_command_module(source_root)

    sys.modules.pop("vision_active_learning_loop.evaluation", None)
    manifest = build_manifest(source_root)

    assert manifest["probe model-contract"] == (
        "vision_active_learning_loop.evaluation:main"
    )
    assert "vision_active_learning_loop.evaluation" not in sys.modules
    with pytest.raises(DuplicateCommandError):
        manifest.add("probe model-contract", "duplicate.module:main")


def test_cli_manifest_rejects_missing_callable(tmp_path: Path) -> None:
    source_root = tmp_path / "src"
    package = source_root / "vision_active_learning_loop"
    package.mkdir(parents=True)
    (package / "broken.py").write_text(
        '@command("probe model-contract")\nclass NotACommand:\n    pass\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidCommandError, match="must decorate a function"):
        build_manifest(source_root)
