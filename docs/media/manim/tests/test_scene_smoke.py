import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
SHORT_SCENES = ["TitleSegment", "PoolSegment", "LoopSegment", "CurveSegment", "OutroSegment", "ValLoopShort"]
LONG_SCENES = ["ChapterRules", "ChapterReference"]

pytestmark = pytest.mark.slow


@pytest.mark.skipif(os.environ.get("VAL_EXPLAINER_RENDER") != "1", reason="set VAL_EXPLAINER_RENDER=1 to run manim")
@pytest.mark.parametrize(
    "scene_file,scene",
    [("scenes_short.py", s) for s in SHORT_SCENES] + [("scenes_long.py", s) for s in LONG_SCENES],
)
def test_dry_run_constructs_the_scene(scene_file, scene):
    completed = subprocess.run(
        [
            sys.executable, "-m", "manim", "--dry_run", "-ql",
            "--media_dir", str(PROJECT / "media"),
            str(PROJECT / "val_explainer" / scene_file), scene,
        ],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
