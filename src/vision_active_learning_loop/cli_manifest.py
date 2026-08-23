"""AST-built command discovery without importing command modules."""

from __future__ import annotations

import ast
import importlib
from collections.abc import Callable, Iterator, Sequence
from pathlib import Path
from typing import Any, TypeVar


class CommandManifestError(ValueError):
    """Base class for invalid command manifests."""


class DuplicateCommandError(CommandManifestError):
    """Raised when two callables claim the same command path."""


class InvalidCommandError(CommandManifestError):
    """Raised when command metadata does not identify a callable."""


_Callable = TypeVar("_Callable", bound=Callable[..., Any])


def command(path: str) -> Callable[[_Callable], _Callable]:
    """Declare a CLI command path on a callable."""

    def decorate(function: _Callable) -> _Callable:
        setattr(function, "__val_command_path__", path)
        return function

    return decorate


class CommandManifest:
    """Map command paths to import targets."""

    def __init__(self) -> None:
        self._targets: dict[str, str] = {}

    def __getitem__(self, path: str) -> str:
        return self._targets[path]

    def __iter__(self) -> Iterator[str]:
        return iter(self._targets)

    def add(self, path: str, target: str) -> None:
        if not path or any(not part for part in path.split(" ")):
            raise InvalidCommandError(f"invalid command path: {path!r}")
        module, separator, callable_name = target.partition(":")
        if not separator or not module or not callable_name:
            raise InvalidCommandError(f"command target must name a callable: {target!r}")
        if path in self._targets:
            raise DuplicateCommandError(f"duplicate command path: {path}")
        self._targets[path] = target

    def resolve(self, arguments: Sequence[str]) -> tuple[Callable[..., Any], list[str]]:
        for path in sorted(self._targets, key=lambda value: len(value.split()), reverse=True):
            words = path.split()
            if list(arguments[: len(words)]) != words:
                continue
            module_name, callable_name = self._targets[path].split(":", maxsplit=1)
            module = importlib.import_module(module_name)
            selected = getattr(module, callable_name, None)
            if not callable(selected):
                raise InvalidCommandError(
                    f"command target is not callable: {self._targets[path]}"
                )
            return selected, list(arguments[len(words) :])
        raise InvalidCommandError(f"unknown command: {' '.join(arguments)}")


def _command_path(decorator: ast.expr) -> str | None:
    if not isinstance(decorator, ast.Call) or len(decorator.args) != 1:
        return None
    function = decorator.func
    if not (
        isinstance(function, ast.Name)
        and function.id == "command"
        or isinstance(function, ast.Attribute)
        and function.attr == "command"
    ):
        return None
    argument = decorator.args[0]
    if not isinstance(argument, ast.Constant) or not isinstance(argument.value, str):
        raise InvalidCommandError("@command path must be a string literal")
    return argument.value


def _module_name(source_root: Path, source_file: Path) -> str:
    relative = source_file.relative_to(source_root).with_suffix("")
    parts = list(relative.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def build_manifest(source_root: Path) -> CommandManifest:
    """Discover decorated command functions using syntax trees only."""

    manifest = CommandManifest()
    if not source_root.is_dir():
        return manifest
    for source_file in sorted(source_root.rglob("*.py")):
        tree = ast.parse(source_file.read_text(encoding="utf-8"), filename=str(source_file))
        for node in tree.body:
            decorators = getattr(node, "decorator_list", ())
            paths = [path for item in decorators if (path := _command_path(item))]
            if not paths:
                continue
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                raise InvalidCommandError(
                    f"@command in {source_file} must decorate a function"
                )
            for path in paths:
                manifest.add(path, f"{_module_name(source_root, source_file)}:{node.name}")
    return manifest
