import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
SCENE_FILE = PROJECT / "val_explainer" / "scenes_short.py"

pytestmark = pytest.mark.slow


@pytest.mark.skipif(os.environ.get("VAL_EXPLAINER_RENDER") != "1", reason="set VAL_EXPLAINER_RENDER=1 to run manim")
@pytest.mark.parametrize("scene", ["TitleSegment", "PoolSegment", "LoopSegment", "CurveSegment", "ValLoopShort"])
def test_dry_run_constructs_the_scene(scene):
    completed = subprocess.run(
        [sys.executable, "-m", "manim", "--dry_run", "-ql", "--media_dir", str(PROJECT / "media"), str(SCENE_FILE), scene],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
