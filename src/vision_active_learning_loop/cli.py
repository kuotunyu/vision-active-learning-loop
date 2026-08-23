"""Top-level lazy command dispatcher."""

from __future__ import annotations

import sys
from collections.abc import Sequence
from pathlib import Path

from .cli_manifest import CommandManifestError, build_manifest


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    source_root = Path(__file__).resolve().parents[1]
    manifest = build_manifest(source_root)
    try:
        selected, remaining = manifest.resolve(arguments)
    except CommandManifestError as error:
        print(error, file=sys.stderr)
        return 2
    result = selected(remaining)
    return int(result) if result is not None else 0
