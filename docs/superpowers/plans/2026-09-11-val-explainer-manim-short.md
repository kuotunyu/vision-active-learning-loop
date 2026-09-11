# Manim 短版說明動畫 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 做出一支約 30 秒、繁體中文、可循環的 README GIF，演出主動學習迴圈與三個 seed 的配對 nAUBC 差，所有數字從 `docs/results/` 的證據檔讀出。

**Architecture:** `docs/media/manim/` 是一個獨立的 uv 專案（manim 0.21.0，自己的 `.venv`），內含 `val_explainer` 套件：`data.py` 讀 summary 與各 seed 的實驗收據成 `ExplainerData`；`copy.py` 放凍結的畫面文字；`style.py` 放字型與顏色；`scenes_short.py` 用五個獨立的 segment 函式組成 `ValLoopShort`。`render.ps1` 渲染 mp4、轉 GIF、檢查大小。主環境完全不動。

**Tech Stack:** Manim Community 0.21.0（Cairo renderer）、manimpango、ffmpeg（已在 PATH）、uv、pytest、Windows PowerShell 5.1。

## Global Constraints

- 規格：[docs/superpowers/specs/2026-09-11-val-explainer-manim-short-design.md](../specs/2026-09-11-val-explainer-manim-short-design.md)。畫面文字以規格 §1 為準，改文字等於改規格。
- `manim==0.21.0`；`requires-python = "==3.12.11"`；不改根目錄的 `pyproject.toml`、`uv.lock`，不在主 `.venv` 裝任何東西。
- 動畫裡沒有任何手打的數字：2,255、574、46／113／226／451、三個 nAUBC 差、曲線點全部由 `data.py` 從 `docs/results/summary-ep18-3seeds/summary.json` 與各 seed 的 `experiment-receipt.json` 讀出；缺檔或缺欄位拋 `ExplainerDataError`，沒有預設值。
- 字型 `Microsoft JhengHei`，備援 `Noto Sans TC`；不用 `MathTex`／`Tex`（本機無 LaTeX）。
- 顏色 Okabe-Ito：random `#999999`、entropy `#0072B2`、margin `#E69F00`。
- 禁詞守門：畫面文字含「降低標註成本」「信賴區間」「deterministic」「可重現」時，同一句必須含「不宣稱」「不是」「並非」之一。
- 不用 RDD2022 影像，只用抽象方塊。`docs/results/` 與私有證據目錄只讀。
- 唯一進 git 的渲染產物是 `docs/media/val-loop-short.gif`（≤ 8 MB）；mp4 複製到 `<evidence-root>\media\`。
- 所有指令都從 repo 根目錄 `<repo>` 執行；manim 相關指令用 `uv run --project docs/media/manim ...`，並在 `docs/media/manim` 目錄內執行（下面每條指令都有寫）。
- 每個 task 結束 commit 到 `main`；不 push。
- 跑 Python 時設 `PYTHONDONTWRITEBYTECODE=1`，避免 `__pycache__` 進 git status。

---

## 檔案結構

| 檔案 | 責任 |
|---|---|
| `docs/media/manim/pyproject.toml` | uv 專案：manim 0.21.0、pytest；hatchling 讓 `val_explainer` 以 editable 安裝 |
| `docs/media/manim/.gitignore` | `.venv/`、`media/`、`__pycache__/`、`.pytest_cache/` |
| `docs/media/manim/README.md` | 渲染、檢查、輸出位置 |
| `docs/media/manim/val_explainer/__init__.py` | 空 |
| `docs/media/manim/val_explainer/data.py` | `ExplainerData`、`ExplainerDataError`、`load_explainer_data()`、`format_delta()` |
| `docs/media/manim/val_explainer/copy.py` | `COPY` dict（凍結文字，含 `{}` 樣板欄位）與 `render_copy()` |
| `docs/media/manim/val_explainer/style.py` | `resolve_font()`、`Style` dataclass、`default_style()` |
| `docs/media/manim/val_explainer/scenes_short.py` | 五個 segment 函式、五個單段 Scene（供抽幀檢查）、`ValLoopShort` |
| `docs/media/manim/tests/test_data.py` | 資料綁定測試 |
| `docs/media/manim/tests/test_copy.py` | 文字守門測試 |
| `docs/media/manim/tests/test_style.py` | 字型解析測試 |
| `docs/media/manim/tests/test_scene_smoke.py` | `--dry_run` 冒煙（slow） |
| `docs/media/manim/render.ps1` | mp4 → GIF → 大小門檻 → 複製 mp4；`-Check` 只 dry run |
| `docs/media/val-loop-short.gif` | 渲染產物 |
| `README.md`（根目錄） | 現況段下方加 GIF 一行 |

---

### Task 1: 建立 uv 專案骨架並確認 manim 與字型可用

**Files:**
- Create: `docs/media/manim/pyproject.toml`
- Create: `docs/media/manim/.gitignore`
- Create: `docs/media/manim/val_explainer/__init__.py`
- Create: `docs/media/manim/tests/__init__.py`

**Interfaces:**
- Produces: 可用的 `docs/media/manim/.venv`，內有 `manim`、`manimpango`、`pytest`，且 `import val_explainer` 成功。

- [ ] **Step 1: 寫 `pyproject.toml`**

```toml
[project]
name = "val-explainer"
version = "0.1.0"
description = "Manim explainer scenes for vision-active-learning-loop (README animation; no evidence is produced here)"
requires-python = "==3.12.11"
dependencies = [
    "manim==0.21.0",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["val_explainer"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "slow: runs manim; only with VAL_EXPLAINER_RENDER=1",
]
```

- [ ] **Step 2: 寫 `.gitignore`**

```gitignore
.venv/
media/
__pycache__/
.pytest_cache/
*.png
*.mp4
*.gif
```

（`*.gif` 只擋這個子目錄；README 用的 GIF 在上一層 `docs/media/`，不受影響。）

- [ ] **Step 3: 建立空的套件與測試目錄**

`docs/media/manim/val_explainer/__init__.py` 內容：

```python
"""Manim explainer scenes for vision-active-learning-loop. Reads committed evidence; produces none."""
```

`docs/media/manim/tests/__init__.py` 空檔。

- [ ] **Step 4: 同步環境**

Run（repo 根目錄）：

```powershell
uv sync --project docs/media/manim
```

Expected：最後幾行列出 `+ manim==0.21.0`、`+ manimpango==...`、`+ pytest==...`、`+ val-explainer==0.1.0 (from file:///.../docs/media/manim)`，退出碼 0。若 manimpango 抱怨缺 DLL，回報停止，不要改主環境。

- [ ] **Step 5: 確認版本、套件可匯入、中文字型存在**

Run（在 `docs/media/manim` 目錄）：

```powershell
cd docs\media\manim
uv run python -c "import manim, manimpango, val_explainer; print(manim.__version__); fonts = manimpango.list_fonts(); print('JhengHei' , 'Microsoft JhengHei' in fonts); print('NotoTC', 'Noto Sans TC' in fonts)"
cd ..\..\..
```

Expected：`0.21.0`、`JhengHei True`（Noto 可 True 可 False）。

- [ ] **Step 6: Commit**

```powershell
git add docs/media/manim/pyproject.toml docs/media/manim/.gitignore docs/media/manim/val_explainer/__init__.py docs/media/manim/tests/__init__.py docs/media/manim/uv.lock
git commit -m "chore: scaffold the Manim explainer project under docs/media/manim"
```

（`uv sync` 會產生 `docs/media/manim/uv.lock`，要一起進 git，之後渲染才能重現同一組版本。）

---

### Task 2: `data.py`：從證據檔讀出動畫需要的全部數字

**Files:**
- Create: `docs/media/manim/val_explainer/data.py`
- Test: `docs/media/manim/tests/test_data.py`

**Interfaces:**
- Produces:
  - `class ExplainerDataError(ValueError)`
  - `@dataclass(frozen=True) class ExplainerData` 欄位：`pool_size: int`、`test_size: int`、`budgets: dict[str, int]`（鍵 `"0.02"`…）、`seeds: list[int]`、`delta: dict[str, dict[int, float]]`（`"entropy"`／`"margin"` → seed → 值）、`curves: dict[int, dict[str, list[tuple[float, float]]]]`（seed → `"random"`／`"entropy"`／`"margin"` → 四個 `(fraction, mAP50_95)` 遞增）、`claim_rule: str`；方法 `positive_seed_count(arm: str) -> int`、`start_count() -> int`（= `budgets["0.02"]`）
  - `load_explainer_data(results_root: Path = DEFAULT_RESULTS_ROOT, summary_dir: str = "summary-ep18-3seeds") -> ExplainerData`
  - `format_delta(value: float) -> str`（`f"{value:+.4f}"`）
  - 常數 `DEFAULT_RESULTS_ROOT`（= repo 的 `docs/results`）、`ARMS = ("random", "entropy", "margin")`

- [ ] **Step 1: 寫失敗的測試**

`docs/media/manim/tests/test_data.py`：

```python
import json
import shutil
from pathlib import Path

import pytest

from val_explainer.data import (
    ARMS,
    DEFAULT_RESULTS_ROOT,
    ExplainerDataError,
    format_delta,
    load_explainer_data,
)

SUMMARY = DEFAULT_RESULTS_ROOT / "summary-ep18-3seeds" / "summary.json"


def _summary() -> dict:
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def test_results_root_points_at_the_repo():
    assert DEFAULT_RESULTS_ROOT.name == "results"
    assert DEFAULT_RESULTS_ROOT.parent.name == "docs"
    assert SUMMARY.is_file()


def test_pool_test_and_budgets_come_from_the_receipt():
    data = load_explainer_data()
    first = _summary()["per_seed"][0]["experiment_id"]
    receipt = json.loads((DEFAULT_RESULTS_ROOT / first / "experiment-receipt.json").read_text(encoding="utf-8"))["normative"]
    assert data.pool_size == receipt["pool_size"]
    assert data.test_size == receipt["test_image_count"]
    assert data.budgets == {k: int(v) for k, v in receipt["budgets"].items()}
    assert list(data.budgets) == ["0.02", "0.05", "0.10", "0.20"]
    assert data.start_count() == data.budgets["0.02"]


def test_deltas_match_the_summary_per_seed():
    data = load_explainer_data()
    summary = _summary()
    assert data.seeds == [int(s) for s in summary["seeds"]]
    for entry in summary["per_seed"]:
        seed = int(entry["seed"])
        for arm in ("entropy", "margin"):
            assert data.delta[arm][seed] == pytest.approx(entry["delta_vs_random"][arm])
    assert data.claim_rule == summary["claim_rule"]


def test_positive_seed_count_counts_strictly_positive_deltas():
    data = load_explainer_data()
    for arm in ("entropy", "margin"):
        expected = sum(1 for v in data.delta[arm].values() if v > 0)
        assert data.positive_seed_count(arm) == expected


def test_curves_have_four_ascending_points_per_arm_and_share_the_start():
    data = load_explainer_data()
    for seed in data.seeds:
        start = data.curves[seed]["random"][0]
        for arm in ARMS:
            points = data.curves[seed][arm]
            assert len(points) == 4
            fractions = [p[0] for p in points]
            assert fractions == sorted(fractions)
            assert fractions == [0.02, 0.05, 0.10, 0.20]
            assert points[0] == start


def test_curve_points_match_the_receipt_fits():
    data = load_explainer_data()
    for entry in _summary()["per_seed"]:
        seed = int(entry["seed"])
        receipt = json.loads((DEFAULT_RESULTS_ROOT / entry["experiment_id"] / "experiment-receipt.json").read_text(encoding="utf-8"))["normative"]
        for fit in receipt["fits"]:
            arm = fit["arm"]
            fraction = float(fit["budget_fraction"])
            expected = float(fit["metrics"]["mAP50_95"])
            arms = ARMS if arm == "shared" else (arm,)
            for a in arms:
                got = dict(data.curves[seed][a])[fraction]
                assert got == pytest.approx(expected)


def test_missing_results_root_raises(tmp_path: Path):
    with pytest.raises(ExplainerDataError):
        load_explainer_data(results_root=tmp_path)


def test_truncated_receipt_raises(tmp_path: Path):
    shutil.copytree(DEFAULT_RESULTS_ROOT / "summary-ep18-3seeds", tmp_path / "summary-ep18-3seeds")
    for entry in _summary()["per_seed"]:
        src = DEFAULT_RESULTS_ROOT / entry["experiment_id"]
        dst = tmp_path / entry["experiment_id"]
        dst.mkdir()
        receipt = json.loads((src / "experiment-receipt.json").read_text(encoding="utf-8"))
        receipt["normative"]["fits"] = receipt["normative"]["fits"][:9]
        (dst / "experiment-receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
    with pytest.raises(ExplainerDataError, match="fits"):
        load_explainer_data(results_root=tmp_path)


def test_format_delta_keeps_the_sign_and_four_decimals():
    assert format_delta(0.0019409691678418661) == "+0.0019"
    assert format_delta(-0.00051) == "-0.0005"
```

- [ ] **Step 2: 跑測試確認失敗**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_data.py -q
cd ..\..\..
```

Expected：collection error，`ModuleNotFoundError: No module named 'val_explainer.data'`。

- [ ] **Step 3: 寫 `data.py`**

```python
"""Read the committed evidence the explainer animates. Nothing here is hand-typed."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# docs/media/manim/val_explainer/data.py -> parents[3] is docs/
DEFAULT_RESULTS_ROOT = Path(__file__).resolve().parents[3] / "results"
DEFAULT_SUMMARY_DIR = "summary-ep18-3seeds"
ARMS = ("random", "entropy", "margin")
SHARED_ARM = "shared"
FITS_PER_EXPERIMENT = 10
POINTS_PER_ARM = 4


class ExplainerDataError(ValueError):
    """Raised when the committed evidence is missing or malformed."""


@dataclass(frozen=True)
class ExplainerData:
    pool_size: int
    test_size: int
    budgets: dict[str, int]
    seeds: list[int]
    delta: dict[str, dict[int, float]]
    curves: dict[int, dict[str, list[tuple[float, float]]]]
    claim_rule: str

    def positive_seed_count(self, arm: str) -> int:
        return sum(1 for value in self.delta[arm].values() if value > 0)

    def start_count(self) -> int:
        return self.budgets["0.02"]


def format_delta(value: float) -> str:
    return f"{value:+.4f}"


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ExplainerDataError(f"missing evidence file: {path}")
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except ValueError as error:
        raise ExplainerDataError(f"{path} is not valid JSON: {error}") from error
    if not isinstance(document, dict):
        raise ExplainerDataError(f"{path} must hold a JSON object")
    return document


def _require(document: dict[str, Any], key: str, path: Path) -> Any:
    if key not in document:
        raise ExplainerDataError(f"{path} lacks key {key!r}")
    return document[key]


def _receipt_points(fits: list[dict[str, Any]], path: Path) -> dict[str, list[tuple[float, float]]]:
    shared = [fit for fit in fits if fit.get("arm") == SHARED_ARM]
    if len(shared) != 1:
        raise ExplainerDataError(f"{path} must list exactly one shared fit, found {len(shared)}")
    start = (float(shared[0]["budget_fraction"]), float(shared[0]["metrics"]["mAP50_95"]))
    curves: dict[str, list[tuple[float, float]]] = {}
    for arm in ARMS:
        rest = sorted(
            (float(fit["budget_fraction"]), float(fit["metrics"]["mAP50_95"]))
            for fit in fits
            if fit.get("arm") == arm
        )
        points = [start, *rest]
        if len(points) != POINTS_PER_ARM:
            raise ExplainerDataError(f"{path}: arm {arm!r} has {len(points)} points, expected {POINTS_PER_ARM}")
        curves[arm] = points
    return curves


def load_explainer_data(
    results_root: Path = DEFAULT_RESULTS_ROOT,
    summary_dir: str = DEFAULT_SUMMARY_DIR,
) -> ExplainerData:
    root = Path(results_root)
    summary_path = root / summary_dir / "summary.json"
    summary = _load_json(summary_path)
    seeds = [int(seed) for seed in _require(summary, "seeds", summary_path)]
    claim_rule = str(_require(summary, "claim_rule", summary_path))
    per_seed = _require(summary, "per_seed", summary_path)

    delta: dict[str, dict[int, float]] = {"entropy": {}, "margin": {}}
    curves: dict[int, dict[str, list[tuple[float, float]]]] = {}
    header: tuple[int, int, dict[str, int]] | None = None

    for entry in per_seed:
        seed = int(_require(entry, "seed", summary_path))
        experiment_id = str(_require(entry, "experiment_id", summary_path))
        deltas = _require(entry, "delta_vs_random", summary_path)
        for arm in delta:
            if arm not in deltas:
                raise ExplainerDataError(f"{summary_path}: seed {seed} lacks delta for {arm!r}")
            delta[arm][seed] = float(deltas[arm])

        receipt_path = root / experiment_id / "experiment-receipt.json"
        normative = _require(_load_json(receipt_path), "normative", receipt_path)
        pool_size = int(_require(normative, "pool_size", receipt_path))
        test_size = int(_require(normative, "test_image_count", receipt_path))
        budgets = {str(k): int(v) for k, v in _require(normative, "budgets", receipt_path).items()}
        if header is None:
            header = (pool_size, test_size, budgets)
        elif header != (pool_size, test_size, budgets):
            raise ExplainerDataError(f"{receipt_path}: pool/test/budgets differ from the first seed")
        fits = _require(normative, "fits", receipt_path)
        if len(fits) != FITS_PER_EXPERIMENT:
            raise ExplainerDataError(f"{receipt_path} lists {len(fits)} fits, expected {FITS_PER_EXPERIMENT}")
        curves[seed] = _receipt_points(fits, receipt_path)

    if header is None or sorted(curves) != sorted(seeds):
        raise ExplainerDataError(f"{summary_path}: per_seed entries do not cover seeds {seeds}")
    pool_size, test_size, budgets = header
    return ExplainerData(
        pool_size=pool_size,
        test_size=test_size,
        budgets=budgets,
        seeds=seeds,
        delta=delta,
        curves=curves,
        claim_rule=claim_rule,
    )
```

- [ ] **Step 4: 跑測試確認通過**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_data.py -q
cd ..\..\..
```

Expected：`9 passed`。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/data.py docs/media/manim/tests/test_data.py
git commit -m "feat(explainer): bind the animation numbers to the committed evidence"
```

---

### Task 3: `copy.py`：凍結的畫面文字與禁詞守門

**Files:**
- Create: `docs/media/manim/val_explainer/copy.py`
- Test: `docs/media/manim/tests/test_copy.py`

**Interfaces:**
- Produces:
  - `COPY: dict[str, str]`（鍵見下；含 `{pool}` 等樣板欄位）
  - `MAX_CHARS_PER_LINE = 30`
  - `render_copy(data: ExplainerData) -> dict[str, str]`：把樣板欄位填入 `data` 的數字，回傳新 dict；`delta_lines` 這種每 seed 一行的內容以 `delta_seed_{seed}` 為鍵展開
  - `NEGATIONS = ("不宣稱", "不是", "並非")`、`BANNED = ("降低標註成本", "信賴區間", "deterministic", "可重現")`

- [ ] **Step 1: 寫失敗的測試**

`docs/media/manim/tests/test_copy.py`：

```python
import pytest

from val_explainer.copy import BANNED, COPY, MAX_CHARS_PER_LINE, NEGATIONS, render_copy
from val_explainer.data import format_delta, load_explainer_data

EXPECTED_KEYS = {
    "title", "title_sub",
    "pool_label", "test_label", "start_label",
    "lane_random", "lane_entropy", "lane_margin", "score", "retrain", "evaluate", "loop_caption",
    "axis_x", "axis_y", "delta_title", "delta_seed", "sign", "range_note",
    "outro_1", "outro_2", "outro_3", "outro_path",
}


def test_copy_has_exactly_the_frozen_keys():
    assert set(COPY) == EXPECTED_KEYS


def test_every_line_is_non_empty_and_fits():
    rendered = render_copy(load_explainer_data())
    for key, text in rendered.items():
        assert text.strip(), key
        for line in text.split("\n"):
            assert len(line) <= MAX_CHARS_PER_LINE, (key, line)


@pytest.mark.parametrize("phrase", BANNED)
def test_banned_phrases_only_appear_negated(phrase):
    rendered = render_copy(load_explainer_data())
    for key, text in rendered.items():
        if phrase.lower() in text.lower():
            assert any(neg in text for neg in NEGATIONS), (key, text)


def test_rendered_numbers_come_from_data():
    data = load_explainer_data()
    rendered = render_copy(data)
    assert f"{data.pool_size:,}" in rendered["pool_label"]
    assert str(data.test_size) in rendered["test_label"]
    assert str(data.start_count()) in rendered["start_label"]
    for seed in data.seeds:
        line = rendered[f"delta_seed_{seed}"]
        assert str(seed) in line
        assert format_delta(data.delta["margin"][seed]) in line
    n = data.positive_seed_count("margin")
    assert f"{n}/{len(data.seeds)}" in rendered["sign"]


def test_the_three_frozen_negative_sentences_are_present():
    rendered = render_copy(load_explainer_data())
    assert rendered["range_note"] == "三個 seed 的最大最小是範圍，不是信賴區間"
    assert rendered["outro_3"] == "不宣稱降低標註成本；同機重播並非位元相同"
```

- [ ] **Step 2: 跑測試確認失敗**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_copy.py -q
cd ..\..\..
```

Expected：`ModuleNotFoundError: No module named 'val_explainer.copy'`。

- [ ] **Step 3: 寫 `copy.py`**

```python
"""On-screen wording, frozen by the design spec (Section 1). Change the spec before changing this."""

from __future__ import annotations

from .data import ExplainerData, format_delta

MAX_CHARS_PER_LINE = 30
NEGATIONS = ("不宣稱", "不是", "並非")
BANNED = ("降低標註成本", "信賴區間", "deterministic", "可重現")

COPY: dict[str, str] = {
    "title": "主動學習迴圈｜RDD2022 Czech × RT-DETR r18",
    "title_sub": "v0.2.1・固定 epoch 規則・{n_seeds} 個 seed",
    "pool_label": "未標註 pool {pool} 張",
    "test_label": "test {test} 張：凍結，不參與選樣與訓練",
    "start_label": "共享起點 2%＝{start} 張",
    "lane_random": "random",
    "lane_entropy": "entropy",
    "lane_margin": "margin",
    "score": "打分",
    "retrain": "重訓",
    "evaluate": "評估 mAP50-95",
    "loop_caption": "同一起點、同一 recipe、同一 test；只有選圖規則不同",
    "axis_x": "預算（pool 的比例）",
    "axis_y": "mAP50-95（test）",
    "delta_title": "配對差（margin − random）",
    "delta_seed": "seed {seed}：nAUBC {delta}",
    "sign": "{n} 個 seed 都為正（{n}/{total}）",
    "range_note": "三個 seed 的最大最小是範圍，不是信賴區間",
    "outro_1": "固定步數與固定 epoch 兩種規則下都是 3/3（entropy 亦同）",
    "outro_2": "20% 預算約達全標籤參考基線的一半",
    "outro_3": "不宣稱降低標註成本；同機重播並非位元相同",
    "outro_path": "docs/results/2026-09-11-v0.2.1-training-rule.md",
}


def render_copy(data: ExplainerData) -> dict[str, str]:
    """Fill the templates with evidence-bound numbers; one `delta_seed_<seed>` line per seed."""
    total = len(data.seeds)
    filled = {
        key: text.format(
            n_seeds=total,
            pool=f"{data.pool_size:,}",
            test=data.test_size,
            start=data.start_count(),
            n=data.positive_seed_count("margin"),
            total=total,
            seed="{seed}",
            delta="{delta}",
        )
        for key, text in COPY.items()
    }
    for seed in data.seeds:
        filled[f"delta_seed_{seed}"] = COPY["delta_seed"].format(
            seed=seed, delta=format_delta(data.delta["margin"][seed])
        )
    del filled["delta_seed"]
    return filled
```

- [ ] **Step 4: 跑測試確認通過**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_copy.py -q
cd ..\..\..
```

Expected：`8 passed`（`BANNED` 有四個參數化案例）。若 `test_every_line_is_non_empty_and_fits` 因某句超過 30 字失敗，調高 `MAX_CHARS_PER_LINE` 到 34 並在 commit 訊息註明；不要改句子。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/copy.py docs/media/manim/tests/test_copy.py
git commit -m "feat(explainer): freeze the on-screen wording and guard it"
```

---

### Task 4: `style.py`：字型解析、顏色、尺寸

**Files:**
- Create: `docs/media/manim/val_explainer/style.py`
- Test: `docs/media/manim/tests/test_style.py`

**Interfaces:**
- Produces:
  - `FONT_CANDIDATES = ("Microsoft JhengHei", "Noto Sans TC")`
  - `resolve_font(available: list[str] | None = None) -> str`（`available=None` 時呼叫 `manimpango.list_fonts()`；都沒有就拋 `RuntimeError`）
  - `@dataclass(frozen=True) class Style`：`font: str`、`colors: dict[str, str]`（鍵 `random`、`entropy`、`margin`、`start`、`pool`、`test`、`text`、`muted`）、`sizes: dict[str, int]`（鍵 `title`、`sub`、`label`、`caption`、`small`、`counter`）、`cell: float`、`cell_gap: float`
  - `default_style() -> Style`

- [ ] **Step 1: 寫失敗的測試**

`docs/media/manim/tests/test_style.py`：

```python
import pytest

from val_explainer.style import FONT_CANDIDATES, Style, default_style, resolve_font


def test_prefers_jhenghei_then_noto():
    assert resolve_font(["Arial", "Noto Sans TC", "Microsoft JhengHei"]) == "Microsoft JhengHei"
    assert resolve_font(["Arial", "Noto Sans TC"]) == "Noto Sans TC"


def test_raises_when_no_cjk_font():
    with pytest.raises(RuntimeError, match="Microsoft JhengHei"):
        resolve_font(["Arial"])


def test_default_style_uses_an_installed_candidate_and_okabe_ito():
    style = default_style()
    assert isinstance(style, Style)
    assert style.font in FONT_CANDIDATES
    assert style.colors["random"] == "#999999"
    assert style.colors["entropy"] == "#0072B2"
    assert style.colors["margin"] == "#E69F00"
    assert style.cell > 0 and style.cell_gap >= 0
    for key in ("title", "sub", "label", "caption", "small", "counter"):
        assert style.sizes[key] > 0
```

- [ ] **Step 2: 跑測試確認失敗**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_style.py -q
cd ..\..\..
```

Expected：`ModuleNotFoundError: No module named 'val_explainer.style'`。

- [ ] **Step 3: 寫 `style.py`**

```python
"""Font, colours and sizes. Okabe-Ito colours; a CJK font is mandatory."""

from __future__ import annotations

from dataclasses import dataclass, field

FONT_CANDIDATES = ("Microsoft JhengHei", "Noto Sans TC")


def resolve_font(available: list[str] | None = None) -> str:
    if available is None:
        import manimpango

        available = list(manimpango.list_fonts())
    for candidate in FONT_CANDIDATES:
        if candidate in available:
            return candidate
    raise RuntimeError(f"no CJK font installed; expected one of {FONT_CANDIDATES}")


@dataclass(frozen=True)
class Style:
    font: str
    colors: dict[str, str] = field(
        default_factory=lambda: {
            "random": "#999999",
            "entropy": "#0072B2",
            "margin": "#E69F00",
            "start": "#F0E442",
            "pool": "#3A3A3A",
            "test": "#2B4C6F",
            "text": "#FFFFFF",
            "muted": "#BBBBBB",
        }
    )
    sizes: dict[str, int] = field(
        default_factory=lambda: {
            "title": 48,
            "sub": 28,
            "label": 26,
            "caption": 24,
            "small": 20,
            "counter": 32,
        }
    )
    cell: float = 0.085
    cell_gap: float = 0.025


def default_style() -> Style:
    return Style(font=resolve_font())
```

- [ ] **Step 4: 跑測試確認通過**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_style.py -q
cd ..\..\..
```

Expected：`3 passed`。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/style.py docs/media/manim/tests/test_style.py
git commit -m "feat(explainer): resolve the CJK font and fix the palette"
```

---

### Task 5: `scenes_short.py` 第一部分：標題卡與 pool 畫面，加冒煙測試

**Files:**
- Create: `docs/media/manim/val_explainer/scenes_short.py`
- Test: `docs/media/manim/tests/test_scene_smoke.py`

**Interfaces:**
- Produces（後續 task 沿用）：
  - `@dataclass class Context`：`data: ExplainerData`、`copy: dict[str, str]`、`style: Style`
  - `def make_context() -> Context`
  - `def text(ctx: Context, key: str, size: str = "label", color: str | None = None) -> Text`（用 `ctx.copy[key]` 建 `Text`，字型與字級由 ctx 決定）
  - `@dataclass class PoolLayout`：`pool: VGroup`（`pool_size` 個 `Square`）、`test: VGroup`、`test_box: SurroundingRectangle`、`start_indices: list[int]`、`labels: VGroup`
  - `def title_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None`
  - `def build_pool_layout(ctx: Context) -> PoolLayout`
  - `def pool_segment(scene: Scene, ctx: Context, layout: PoolLayout) -> None`（不 fade out；loop 段接著用同一組 mobject）
  - Scene 類別：`TitleSegment`、`PoolSegment`、`ValLoopShort`（本 task 只含前兩段）

- [ ] **Step 1: 寫冒煙測試**

`docs/media/manim/tests/test_scene_smoke.py`：

```python
import os
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]
SCENE_FILE = PROJECT / "val_explainer" / "scenes_short.py"

pytestmark = pytest.mark.slow


@pytest.mark.skipif(os.environ.get("VAL_EXPLAINER_RENDER") != "1", reason="set VAL_EXPLAINER_RENDER=1 to run manim")
@pytest.mark.parametrize("scene", ["TitleSegment", "PoolSegment", "ValLoopShort"])
def test_dry_run_constructs_the_scene(scene):
    completed = subprocess.run(
        [sys.executable, "-m", "manim", "--dry_run", "-ql", "--media_dir", str(PROJECT / "media"), str(SCENE_FILE), scene],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
```

- [ ] **Step 2: 寫 `scenes_short.py`（標題與 pool）**

```python
"""The 30-second README explainer. Five segments; each takes (scene, ctx, ...) and can be re-sequenced."""

from __future__ import annotations

import random
from dataclasses import dataclass

from manim import (
    DOWN, LEFT, RIGHT, UP,
    FadeIn, FadeOut, LaggedStart, Scene, Square, SurroundingRectangle, Text, VGroup,
)

from .copy import render_copy
from .data import ExplainerData, load_explainer_data
from .style import Style, default_style

POOL_COLS = 61
TEST_COLS = 24
START_SEED = 17  # only picks which abstract squares light up; not tied to the experiment seed


@dataclass
class Context:
    data: ExplainerData
    copy: dict[str, str]
    style: Style


def make_context() -> Context:
    data = load_explainer_data()
    return Context(data=data, copy=render_copy(data), style=default_style())


def text(ctx: Context, key: str, size: str = "label", color: str | None = None) -> Text:
    return Text(
        ctx.copy[key],
        font=ctx.style.font,
        font_size=ctx.style.sizes[size],
        color=color or ctx.style.colors["text"],
    )


# ------------------------------------------------------------------ title

def title_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None:
    title = text(ctx, "title", "title")
    sub = text(ctx, "title_sub", "sub", ctx.style.colors["muted"]).next_to(title, DOWN, buff=0.4)
    scene.play(FadeIn(title, shift=UP * 0.2), run_time=0.8)
    scene.play(FadeIn(sub), run_time=0.5)
    scene.wait(1.3)
    if fade_out:
        scene.play(FadeOut(title), FadeOut(sub), run_time=0.4)


# ------------------------------------------------------------------ pool

@dataclass
class PoolLayout:
    pool: VGroup
    test: VGroup
    test_box: SurroundingRectangle
    start_indices: list[int]
    labels: VGroup


def _grid(count: int, cols: int, color: str, style: Style) -> VGroup:
    squares = VGroup(*[
        Square(side_length=style.cell, fill_color=color, fill_opacity=1.0, stroke_width=0)
        for _ in range(count)
    ])
    squares.arrange_in_grid(cols=cols, buff=style.cell_gap)
    return squares


def build_pool_layout(ctx: Context) -> PoolLayout:
    style = ctx.style
    pool = _grid(ctx.data.pool_size, POOL_COLS, style.colors["pool"], style)
    pool.to_edge(LEFT, buff=0.6).shift(DOWN * 0.2)
    test = _grid(ctx.data.test_size, TEST_COLS, style.colors["test"], style)
    test.to_edge(RIGHT, buff=0.8).align_to(pool, UP)
    test_box = SurroundingRectangle(test, color=style.colors["muted"], buff=0.15, stroke_width=2)
    pool_label = text(ctx, "pool_label").next_to(pool, UP, buff=0.25)
    test_label = text(ctx, "test_label", "small", style.colors["muted"]).next_to(test_box, DOWN, buff=0.2)
    start_label = text(ctx, "start_label", "label", style.colors["start"]).next_to(pool, DOWN, buff=0.25)
    picker = random.Random(START_SEED)
    start_indices = sorted(picker.sample(range(ctx.data.pool_size), ctx.data.start_count()))
    return PoolLayout(
        pool=pool,
        test=test,
        test_box=test_box,
        start_indices=start_indices,
        labels=VGroup(pool_label, test_label, start_label),
    )


def pool_segment(scene: Scene, ctx: Context, layout: PoolLayout) -> None:
    pool_label, test_label, start_label = layout.labels
    scene.play(FadeIn(layout.pool, lag_ratio=0.0005), FadeIn(pool_label), run_time=1.2)
    scene.play(FadeIn(layout.test), FadeIn(layout.test_box), FadeIn(test_label), run_time=0.8)
    scene.wait(0.6)
    start_squares = [layout.pool[i] for i in layout.start_indices]
    scene.play(
        LaggedStart(*[sq.animate.set_fill(ctx.style.colors["start"]) for sq in start_squares], lag_ratio=0.02),
        FadeIn(start_label),
        run_time=1.6,
    )
    scene.wait(0.8)


# ------------------------------------------------------------------ scenes

class TitleSegment(Scene):
    def construct(self) -> None:
        title_segment(self, make_context(), fade_out=False)


class PoolSegment(Scene):
    def construct(self) -> None:
        ctx = make_context()
        pool_segment(self, ctx, build_pool_layout(ctx))


class ValLoopShort(Scene):
    def construct(self) -> None:
        ctx = make_context()
        title_segment(self, ctx)
        layout = build_pool_layout(ctx)
        pool_segment(self, ctx, layout)
```

- [ ] **Step 3: 跑冒煙測試**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest tests/test_scene_smoke.py -q
Remove-Item Env:VAL_EXPLAINER_RENDER
cd ..\..\..
```

Expected：`3 passed`。若 `Text` 抱怨字型，回頭看 Task 4 的 `resolve_font`；若 `arrange_in_grid` 參數錯，改用 `rows=` 計算（`rows = -(-count // cols)`）。

- [ ] **Step 4: 低畫質渲染兩段的最後一幀並看圖**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py TitleSegment
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py PoolSegment
cd ..\..\..
```

輸出在 `docs/media/manim/media/images/scenes_short/TitleSegment_ManimCE_v0.21.0.png` 與 `PoolSegment_ManimCE_v0.21.0.png`。用 Read 工具打開兩張圖檢查：中文字型正確（不是方框）、標題置中、pool 網格在左、test 在右且有外框、46 個黃色方塊散布、三個標籤不與網格重疊、沒有任何元素超出畫面。有問題就調 `POOL_COLS`、`cell`、`buff`，再渲染一次。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_short.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): title card and pool layout segments"
```

---

### Task 6: loop 畫面：三條 lane、打分、選圖飛入、重訓、評估、快轉

**Files:**
- Modify: `docs/media/manim/val_explainer/scenes_short.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`（parametrize 加 `"LoopSegment"`）

**Interfaces:**
- Consumes：`Context`、`PoolLayout`、`text()`（Task 5）
- Produces：
  - `@dataclass class LaneSet`：`lanes: dict[str, VGroup]`（arm → 該 lane 的 box＋標籤＋計數器）、`counters: dict[str, Integer]`、`caption: Text`
  - `def loop_segment(scene: Scene, ctx: Context, layout: PoolLayout, fade_out: bool = True) -> LaneSet`
  - Scene 類別 `LoopSegment`

- [ ] **Step 1: 在冒煙測試的 parametrize 加入 `"LoopSegment"`**

```python
@pytest.mark.parametrize("scene", ["TitleSegment", "PoolSegment", "LoopSegment", "ValLoopShort"])
```

- [ ] **Step 2: 加入 loop 段程式**

在 `scenes_short.py` 的 import 加上：

```python
from manim import (
    DOWN, LEFT, RIGHT, UP, ORIGIN,
    Arrow, ChangeDecimalToValue, FadeIn, FadeOut, Indicate, Integer, LaggedStart, Rectangle,
    Scene, Square, SurroundingRectangle, Text, VGroup,
)
```

在 `pool_segment` 之後加入：

```python
# ------------------------------------------------------------------ loop

FLY_PER_ROUND = 14  # representative squares that visibly fly per lane per round
ROUND_KEYS = ("0.05", "0.10", "0.20")


@dataclass
class LaneSet:
    lanes: dict[str, VGroup]
    counters: dict[str, Integer]
    caption: Text


def _lane(ctx: Context, arm: str, width: float, height: float) -> tuple[VGroup, Integer]:
    color = ctx.style.colors[arm]
    box = Rectangle(width=width, height=height, stroke_color=color, stroke_width=3, fill_color=color, fill_opacity=0.08)
    name = text(ctx, f"lane_{arm}", "label", color).next_to(box.get_left(), RIGHT, buff=0.2)
    counter = Integer(ctx.data.start_count(), font_size=ctx.style.sizes["counter"], color=ctx.style.colors["text"])
    counter.next_to(box.get_right(), LEFT, buff=0.3)
    return VGroup(box, name, counter), counter


def loop_segment(scene: Scene, ctx: Context, layout: PoolLayout, fade_out: bool = True) -> LaneSet:
    style = ctx.style
    data = ctx.data
    # compact the pool and test to make room for the lanes
    pool_label, test_label, start_label = layout.labels
    scene.play(
        layout.pool.animate.scale(0.72).to_edge(LEFT, buff=0.4).shift(UP * 0.3),
        FadeOut(pool_label), FadeOut(start_label),
        VGroup(layout.test, layout.test_box).animate.scale(0.55).to_corner(DOWN + RIGHT, buff=0.4),
        test_label.animate.scale(0.8),
        run_time=0.8,
    )
    test_label.next_to(layout.test_box, UP, buff=0.1)
    scene.add(test_label)

    lanes: dict[str, VGroup] = {}
    counters: dict[str, Integer] = {}
    stack = VGroup()
    for arm in ("random", "entropy", "margin"):
        lane, counter = _lane(ctx, arm, width=4.6, height=0.9)
        lanes[arm] = lane
        counters[arm] = counter
        stack.add(lane)
    stack.arrange(DOWN, buff=0.35).next_to(layout.pool, RIGHT, buff=0.9).align_to(layout.pool, UP)
    score_label = text(ctx, "score", "small", style.colors["muted"]).next_to(stack, UP, buff=0.15)
    retrain = text(ctx, "retrain", "small", style.colors["muted"])
    evaluate = text(ctx, "evaluate", "small", style.colors["muted"])
    retrain_arrow = Arrow(stack.get_right() + RIGHT * 0.1, stack.get_right() + RIGHT * 1.1, buff=0, color=style.colors["muted"], stroke_width=3)
    retrain.next_to(retrain_arrow, UP, buff=0.1)
    eval_arrow = Arrow(retrain_arrow.get_end(), layout.test_box.get_top(), buff=0.1, color=style.colors["muted"], stroke_width=3)
    evaluate.next_to(eval_arrow.get_center(), RIGHT, buff=0.15)
    caption = text(ctx, "loop_caption", "caption").to_edge(DOWN, buff=0.35)

    scene.play(LaggedStart(*[FadeIn(lane, shift=RIGHT * 0.2) for lane in stack], lag_ratio=0.2), run_time=0.9)
    scene.play(FadeIn(score_label), FadeIn(retrain_arrow), FadeIn(retrain), FadeIn(eval_arrow), FadeIn(evaluate), run_time=0.6)

    picker = random.Random(START_SEED + 1)
    unlabeled = [i for i in range(data.pool_size) if i not in set(layout.start_indices)]

    def one_round(key: str, run_time: float, show_scoring: bool) -> None:
        target = data.budgets[key]
        if show_scoring:
            # uncertainty shading: entropy/margin lanes "see" scores; random does not
            shade = picker.sample(unlabeled, min(len(unlabeled), 400))
            scene.play(
                LaggedStart(*[
                    layout.pool[i].animate.set_fill(style.colors["margin"], opacity=0.35 + 0.65 * picker.random())
                    for i in shade
                ], lag_ratio=0.002),
                Indicate(score_label, color=style.colors["margin"]),
                run_time=run_time * 0.35,
            )
        flights = []
        for arm in ("random", "entropy", "margin"):
            chosen = picker.sample(unlabeled, FLY_PER_ROUND)
            for i in chosen:
                ghost = layout.pool[i].copy().set_fill(style.colors[arm], opacity=1.0)
                flights.append(ghost.animate.move_to(lanes[arm][0].get_center() + RIGHT * picker.uniform(-1.4, 1.4)).scale(0.6))
                scene.add(ghost)
        scene.play(
            LaggedStart(*flights, lag_ratio=0.01),
            *[ChangeDecimalToValue(counters[arm], target) for arm in counters],
            run_time=run_time * 0.4,
        )
        for mob in list(scene.mobjects):
            if mob not in (layout.pool, layout.test, layout.test_box, stack, score_label, retrain_arrow, retrain, eval_arrow, evaluate, caption, test_label) and mob not in stack:
                if isinstance(mob, Square):
                    scene.remove(mob)
        scene.play(Indicate(retrain, color=style.colors["text"]), Indicate(retrain_arrow, color=style.colors["text"]), run_time=run_time * 0.12)
        scene.play(Indicate(evaluate, color=style.colors["text"]), Indicate(eval_arrow, color=style.colors["text"]), run_time=run_time * 0.13)
        if show_scoring:
            scene.play(*[layout.pool[i].animate.set_fill(style.colors["pool"], opacity=1.0) for i in shade], run_time=0.2)

    one_round(ROUND_KEYS[0], run_time=3.6, show_scoring=True)
    scene.play(FadeIn(caption), run_time=0.3)
    one_round(ROUND_KEYS[1], run_time=1.4, show_scoring=False)
    one_round(ROUND_KEYS[2], run_time=1.4, show_scoring=False)
    scene.wait(0.5)

    lane_set = LaneSet(lanes=lanes, counters=counters, caption=caption)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)
    return lane_set
```

並新增 Scene 類別，`ValLoopShort.construct` 也接上：

```python
class LoopSegment(Scene):
    def construct(self) -> None:
        ctx = make_context()
        layout = build_pool_layout(ctx)
        self.add(layout.pool, layout.test, layout.test_box, layout.labels)
        for i in layout.start_indices:
            layout.pool[i].set_fill(ctx.style.colors["start"])
        loop_segment(self, ctx, layout, fade_out=False)
```

```python
class ValLoopShort(Scene):
    def construct(self) -> None:
        ctx = make_context()
        title_segment(self, ctx)
        layout = build_pool_layout(ctx)
        pool_segment(self, ctx, layout)
        loop_segment(self, ctx, layout)
```

- [ ] **Step 3: 跑冒煙測試**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest tests/test_scene_smoke.py -q
Remove-Item Env:VAL_EXPLAINER_RENDER
cd ..\..\..
```

Expected：`4 passed`。常見錯誤：`Indicate` 對 `Arrow` 需要 mobject 而非 list；`ChangeDecimalToValue` 目標要是 `int`；`scene.mobjects` 迭代時不要邊移除邊迭代（程式用 `list(...)` 複製）。

- [ ] **Step 4: 低畫質渲染 loop 段最後一幀並看圖**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py LoopSegment
cd ..\..\..
```

用 Read 打開 `media/images/scenes_short/LoopSegment_ManimCE_v0.21.0.png` 檢查：三條 lane 各自有 arm 名稱與計數器 451；lane 顏色對應 Okabe-Ito；重訓箭頭與評估箭頭不壓到文字；壓縮後的 pool 與 test 都在畫面內；底部說明句完整。若 lane 太寬與 test 重疊，把 `_lane(... width=4.6 ...)` 降到 4.0。

- [ ] **Step 5: 完整渲染一次看動態（低畫質）**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
uv run python -m manim -ql --media_dir media val_explainer/scenes_short.py ValLoopShort
ffprobe -v error -show_entries format=duration -of csv=p=0 media/videos/scenes_short/480p15/ValLoopShort.mp4
cd ..\..\..
```

Expected：mp4 產生；目前長度約 17 到 19 秒（標題 3 ＋ pool 5 ＋ loop 9 到 11）。若超過 20 秒，把 `one_round` 的 `run_time` 等比例縮小。

- [ ] **Step 6: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_short.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): loop segment with three lanes, scoring, selection and retrain"
```

---

### Task 7: curve 畫面：seed 17 兩條曲線、著色區、三個 seed 的配對差

**Files:**
- Modify: `docs/media/manim/val_explainer/scenes_short.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`（parametrize 加 `"CurveSegment"`）

**Interfaces:**
- Consumes：`Context`、`text()`、`ExplainerData.curves`、`ExplainerData.delta`、`ctx.copy["delta_seed_<seed>"]`
- Produces：
  - `def curve_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None`
  - Scene 類別 `CurveSegment`

- [ ] **Step 1: parametrize 加入 `"CurveSegment"`**

```python
@pytest.mark.parametrize("scene", ["TitleSegment", "PoolSegment", "LoopSegment", "CurveSegment", "ValLoopShort"])
```

- [ ] **Step 2: 加入 curve 段程式**

import 補上：

```python
from manim import Axes, Create, Polygon, Write
```

在 `loop_segment` 之後加入：

```python
# ------------------------------------------------------------------ curve

X_TICKS = {0.02: "2%", 0.05: "5%", 0.10: "10%", 0.20: "20%"}


def _axes(ctx: Context, y_max: float) -> Axes:
    step = 0.01 if y_max <= 0.05 else 0.02
    axes = Axes(
        x_range=[0, 0.22, 0.05],
        y_range=[0, y_max, step],
        x_length=7.4,
        y_length=4.0,
        tips=False,
        axis_config={"include_numbers": False, "stroke_color": ctx.style.colors["muted"]},
    )
    axes.x_axis.add_labels(
        {x: Text(label, font=ctx.style.font, font_size=ctx.style.sizes["small"], color=ctx.style.colors["muted"]) for x, label in X_TICKS.items()}
    )
    y_labels = {}
    value = step
    while value <= y_max + 1e-9:
        y_labels[value] = Text(f"{value:.2f}", font=ctx.style.font, font_size=ctx.style.sizes["small"], color=ctx.style.colors["muted"])
        value = round(value + step, 6)
    axes.y_axis.add_labels(y_labels)
    return axes


def _line(axes: Axes, points: list[tuple[float, float]], color: str, width: float, opacity: float = 1.0):
    graph = axes.plot_line_graph(
        x_values=[p[0] for p in points],
        y_values=[p[1] for p in points],
        line_color=color,
        stroke_width=width,
        add_vertex_dots=True,
        vertex_dot_radius=0.05,
        vertex_dot_style={"fill_color": color},
    )
    graph.set_opacity(opacity)
    return graph


def curve_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None:
    style = ctx.style
    data = ctx.data
    first, *others = data.seeds
    y_max = max(p[1] for seed in data.seeds for arm in ("random", "margin") for p in data.curves[seed][arm]) * 1.15
    y_max = round(y_max + 0.005, 2)
    axes = _axes(ctx, y_max).to_edge(LEFT, buff=0.7).shift(DOWN * 0.2)
    x_label = text(ctx, "axis_x", "small", style.colors["muted"]).next_to(axes.x_axis, DOWN, buff=0.45)
    y_label = text(ctx, "axis_y", "small", style.colors["muted"]).rotate(90 * 3.14159 / 180).next_to(axes.y_axis, LEFT, buff=0.35)
    scene.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=0.8)

    rand = _line(axes, data.curves[first]["random"], style.colors["random"], 4)
    marg = _line(axes, data.curves[first]["margin"], style.colors["margin"], 4)
    scene.play(Create(rand), run_time=1.0)
    scene.play(Create(marg), run_time=1.0)

    forward = [axes.c2p(x, y) for x, y in data.curves[first]["margin"]]
    backward = [axes.c2p(x, y) for x, y in reversed(data.curves[first]["random"])]
    area = Polygon(*forward, *backward, fill_color=style.colors["margin"], fill_opacity=0.3, stroke_width=0)

    panel = VGroup(text(ctx, "delta_title", "label", style.colors["margin"]))
    lines = {seed: text(ctx, f"delta_seed_{seed}", "label") for seed in data.seeds}
    for seed in data.seeds:
        panel.add(lines[seed])
    sign = text(ctx, "sign", "label", style.colors["start"])
    note = text(ctx, "range_note", "small", style.colors["muted"])
    panel.add(sign, note)
    panel.arrange(DOWN, aligned_edge=LEFT, buff=0.22).to_edge(RIGHT, buff=0.6).shift(UP * 0.2)

    scene.play(FadeIn(area), FadeIn(panel[0]), Write(lines[first]), run_time=1.2)
    scene.wait(0.4)
    for seed in others:
        thin_r = _line(axes, data.curves[seed]["random"], style.colors["random"], 2, opacity=0.55)
        thin_m = _line(axes, data.curves[seed]["margin"], style.colors["margin"], 2, opacity=0.55)
        scene.play(Create(thin_r), Create(thin_m), Write(lines[seed]), run_time=1.1)
    scene.play(FadeIn(sign, shift=UP * 0.1), run_time=0.5)
    scene.play(FadeIn(note), run_time=0.4)
    scene.wait(1.6)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


class CurveSegment(Scene):
    def construct(self) -> None:
        curve_segment(self, make_context(), fade_out=False)
```

`ValLoopShort.construct` 加一行 `curve_segment(self, ctx)`。

- [ ] **Step 3: 跑冒煙測試**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest tests/test_scene_smoke.py -q
Remove-Item Env:VAL_EXPLAINER_RENDER
cd ..\..\..
```

Expected：`5 passed`。若 `add_labels` 不接受 `Text`，改成先 `axes.x_axis` 不加標籤、用 `VGroup` 手動 `next_to(axes.c2p(x, 0), DOWN)` 放四個 `Text`。

- [ ] **Step 4: 渲染最後一幀並看圖**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py CurveSegment
cd ..\..\..
```

用 Read 打開 `media/images/scenes_short/CurveSegment_ManimCE_v0.21.0.png` 檢查：x 軸四個刻度 2%／5%／10%／20%；y 軸標籤是兩位小數；橘色著色區確實夾在 seed 17 的橘線與灰線之間（若某段 margin 低於 random，著色會交叉，這是資料的實情，照畫）；右側面板依序是標題、三行 seed 差、黃色 3/3 句、灰色範圍註記；面板不與座標軸重疊。三行 seed 差的數字要與 `docs/results/summary-ep18-3seeds/summary.csv` 的 `delta_margin` 四位小數一致（+0.0019／+0.0064／+0.0087）。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_short.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): budget curves with the paired delta panel"
```

---

### Task 8: 結尾卡、完整場景時長

**Files:**
- Modify: `docs/media/manim/val_explainer/scenes_short.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`（parametrize 加 `"OutroSegment"`）

**Interfaces:**
- Produces：`def outro_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None`、Scene 類別 `OutroSegment`；`ValLoopShort` 五段齊全

- [ ] **Step 1: parametrize 加入 `"OutroSegment"`**

```python
@pytest.mark.parametrize("scene", ["TitleSegment", "PoolSegment", "LoopSegment", "CurveSegment", "OutroSegment", "ValLoopShort"])
```

- [ ] **Step 2: 加入 outro 段**

```python
# ------------------------------------------------------------------ outro

def outro_segment(scene: Scene, ctx: Context, fade_out: bool = True) -> None:
    style = ctx.style
    lines = VGroup(
        text(ctx, "outro_1", "label"),
        text(ctx, "outro_2", "label"),
        text(ctx, "outro_3", "label", style.colors["start"]),
    ).arrange(DOWN, buff=0.35)
    path = text(ctx, "outro_path", "small", style.colors["muted"]).next_to(lines, DOWN, buff=0.6)
    scene.play(LaggedStart(*[FadeIn(line, shift=UP * 0.15) for line in lines], lag_ratio=0.35), run_time=1.4)
    scene.play(FadeIn(path), run_time=0.4)
    scene.wait(2.0)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


class OutroSegment(Scene):
    def construct(self) -> None:
        outro_segment(self, make_context(), fade_out=False)


class ValLoopShort(Scene):
    def construct(self) -> None:
        ctx = make_context()
        title_segment(self, ctx)
        layout = build_pool_layout(ctx)
        pool_segment(self, ctx, layout)
        loop_segment(self, ctx, layout)
        curve_segment(self, ctx)
        outro_segment(self, ctx)
```

（把先前的 `ValLoopShort` 定義換成這個，檔案裡只留一份。）

- [ ] **Step 3: 跑全部測試（含冒煙）**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest -q
Remove-Item Env:VAL_EXPLAINER_RENDER
cd ..\..\..
```

Expected：全部通過（9 ＋ 8 ＋ 3 ＋ 6）。

- [ ] **Step 4: 低畫質完整渲染，量時長，看結尾幀**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
uv run python -m manim -ql --media_dir media val_explainer/scenes_short.py ValLoopShort
ffprobe -v error -show_entries format=duration -of csv=p=0 media/videos/scenes_short/480p15/ValLoopShort.mp4
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py OutroSegment
cd ..\..\..
```

Expected：時長 28 到 32 秒。超過 32 秒就縮 `curve_segment` 末尾的 `wait(1.6)` 與 `outro_segment` 的 `wait(2.0)`；低於 28 秒可以不動。用 Read 看 `OutroSegment_ManimCE_v0.21.0.png`：三行置中、第三行黃色、路徑小字在下。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_short.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): outro card; ValLoopShort runs all five segments"
```

---

### Task 9: `render.ps1` 與專案 README

**Files:**
- Create: `docs/media/manim/render.ps1`
- Create: `docs/media/manim/README.md`

**Interfaces:**
- Produces：`render.ps1 [-Check] [-Quality h|l]`；成功時寫 `docs/media/val-loop-short.gif` 並複製 mp4 到 `<evidence-root>\media\`

- [ ] **Step 1: 寫 `render.ps1`**

```powershell
<#
.SYNOPSIS
Render the README explainer: mp4 (manim) -> GIF (ffmpeg, palette) -> size gate -> copy mp4 to the private evidence root.

.EXAMPLE
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Check
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1
#>
[CmdletBinding()]
param(
    [switch]$Check,
    [ValidateSet('h', 'l')][string]$Quality = 'h',
    [string]$EvidenceMediaDir = '<evidence-root>\media'
)

Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

$Project = $PSScriptRoot
$SceneFile = Join-Path $Project 'val_explainer\scenes_short.py'
$MediaDir = Join-Path $Project 'media'
$GifOut = Join-Path (Split-Path -Parent $Project) 'val-loop-short.gif'
$MaxGifBytes = 8MB
$MaxSeconds = 32.0
$env:PYTHONDONTWRITEBYTECODE = '1'

Push-Location $Project
try {
    if ($Check) {
        & uv run python -m manim --dry_run -ql --media_dir $MediaDir $SceneFile ValLoopShort
        if ($LASTEXITCODE -ne 0) { throw "dry run failed ($LASTEXITCODE)" }
        Write-Host 'check ok (dry run; nothing written)'
        exit 0
    }

    & uv run python -m manim "-q$Quality" --media_dir $MediaDir $SceneFile ValLoopShort
    if ($LASTEXITCODE -ne 0) { throw "manim failed ($LASTEXITCODE)" }
    $folder = if ($Quality -eq 'h') { '1080p60' } else { '480p15' }
    $Mp4 = Join-Path $MediaDir "videos\scenes_short\$folder\ValLoopShort.mp4"
    if (-not (Test-Path -LiteralPath $Mp4)) { throw "expected output missing: $Mp4" }

    $duration = [double](& ffprobe -v error -show_entries format=duration -of csv=p=0 $Mp4)
    Write-Host ("duration {0:N1} s" -f $duration)
    if ($duration -gt $MaxSeconds) { throw "clip is $duration s, longer than $MaxSeconds s" }

    $attempts = @(@{ Width = 960; Fps = 12 }, @{ Width = 800; Fps = 10 })
    $tmpGif = Join-Path $MediaDir 'val-loop-short.tmp.gif'
    $palette = Join-Path $MediaDir 'palette.png'
    $ok = $false
    foreach ($a in $attempts) {
        $filters = "fps=$($a.Fps),scale=$($a.Width):-1:flags=lanczos"
        & ffmpeg -y -v error -i $Mp4 -vf "$filters,palettegen=stats_mode=diff" $palette
        if ($LASTEXITCODE -ne 0) { throw 'palettegen failed' }
        & ffmpeg -y -v error -i $Mp4 -i $palette -lavfi "$filters[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle" $tmpGif
        if ($LASTEXITCODE -ne 0) { throw 'paletteuse failed' }
        $size = (Get-Item -LiteralPath $tmpGif).Length
        Write-Host ("gif {0}x? @{1}fps = {2:N1} MB" -f $a.Width, $a.Fps, ($size / 1MB))
        if ($size -le $MaxGifBytes) { $ok = $true; break }
    }
    if (-not $ok) { throw "GIF exceeds $($MaxGifBytes / 1MB) MB at every setting; existing GIF left untouched" }

    Move-Item -LiteralPath $tmpGif -Destination $GifOut -Force
    Remove-Item -LiteralPath $palette -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path -LiteralPath $EvidenceMediaDir)) { New-Item -ItemType Directory -Path $EvidenceMediaDir | Out-Null }
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmZ')
    Copy-Item -LiteralPath $Mp4 -Destination (Join-Path $EvidenceMediaDir "val-loop-short-$stamp.mp4")
    Write-Host "gif  -> $GifOut"
    Write-Host "mp4  -> $EvidenceMediaDir\val-loop-short-$stamp.mp4"
    exit 0
} finally {
    Pop-Location
}
```

- [ ] **Step 2: 寫專案 README**

`docs/media/manim/README.md`：

```markdown
# Manim 說明動畫

README 用的 30 秒短版（`ValLoopShort`）。只做說明，不產生任何證據；所有數字由 `val_explainer/data.py` 從 `docs/results/` 讀出。畫面文字凍結在 `val_explainer/copy.py`，規格在 [../../superpowers/specs/2026-09-11-val-explainer-manim-short-design.md](../../superpowers/specs/2026-09-11-val-explainer-manim-short-design.md)。

獨立環境（不碰主 `.venv`）：

```powershell
uv sync --project docs/media/manim
```

測試（在 `docs/media/manim`）：

```powershell
uv run pytest -q                       # 資料綁定、文字守門、字型
$env:VAL_EXPLAINER_RENDER = "1"; uv run pytest -q   # 加上 manim --dry_run 冒煙
```

渲染（repo 根目錄）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Check   # 只 dry run
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1          # 1080p mp4 -> GIF
```

輸出：`docs/media/val-loop-short.gif`（進 git，≤ 8 MB）；mp4 複製到 `<evidence-root>\media\`（不進 git）。單段檢查用 `uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py <TitleSegment|PoolSegment|LoopSegment|CurveSegment|OutroSegment>`，最後一幀輸出到 `media/images/scenes_short/`。

字型：Microsoft JhengHei（備援 Noto Sans TC）。沒有 LaTeX 也能渲染。
```

- [ ] **Step 3: 跑 `-Check`**

Run（repo 根目錄）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Check
```

Expected：manim 的 dry run 訊息後印 `check ok (dry run; nothing written)`，退出碼 0。

- [ ] **Step 4: 用低畫質跑完整流程驗證腳本邏輯**

Run（repo 根目錄）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Quality l
```

Expected：印出 `duration 2x.x s`、`gif 960x? @12fps = ... MB`、`gif -> ...val-loop-short.gif`、`mp4 -> ...`。確認 `docs/media/val-loop-short.gif` 存在、私有目錄多一個 mp4。這是低畫質產物，下一個 task 會用高畫質覆寫。

- [ ] **Step 5: Commit（不含 GIF）**

```powershell
git add docs/media/manim/render.ps1 docs/media/manim/README.md
git commit -m "feat(explainer): one-command render with GIF size gate"
```

---

### Task 10: 高畫質渲染、owner 審閱、README 嵌入

**Files:**
- Create: `docs/media/val-loop-short.gif`（渲染產物）
- Modify: `README.md`（根目錄，現況段之後）

- [ ] **Step 1: 高畫質渲染**

Run（repo 根目錄）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1
```

Expected：1080p60 渲染（可能 10 到 25 分鐘）；`duration` 28 到 32 秒；GIF ≤ 8 MB；mp4 複製到私有目錄。

- [ ] **Step 2: 自己先看**

用 Read 打開 `docs/media/val-loop-short.gif`（或先用 ffmpeg 抽 6 張幀：`ffmpeg -v error -i docs\media\val-loop-short.gif -vf "fps=0.2" docs\media\manim\media\frame_%02d.png`，再逐張 Read）。檢查：中文無方框、無元素出界、三行 seed 差數字與 `summary.csv` 一致、著色區在兩線之間、結尾第三行是「不宣稱降低標註成本；同機重播並非位元相同」。有問題回到對應 task 修。

- [ ] **Step 3: 請 owner 看 GIF（審閱門）**

用 SendUserFile 把 `docs/media/val-loop-short.gif` 送給 owner，附一句「這是要放 README 的版本，長 xx 秒、x.x MB；同意才進 README」。**等 owner 回覆同意再做下一步。**

- [ ] **Step 4: README 嵌入**

在根目錄 `README.md` 現況段（`**現況（2026-09-11）：v0.2.1 跑完。**` 那一段）之後、`上一輪 v0.2-lite` 那一段之前，插入：

```markdown
![主動學習迴圈（30 秒）：三個 arm 從同一個 46 張起點分岔，三個 seed 的 margin − random 配對差都為正](docs/media/val-loop-short.gif)

上面的動畫由 [docs/media/manim/](docs/media/manim/) 渲染，數字直接讀自 `docs/results/` 的 summary 與收據；它只做說明，不是證據。
```

- [ ] **Step 5: 最後檢查與 commit**

Run（repo 根目錄）：

```powershell
git status --short
(Get-Item docs\media\val-loop-short.gif).Length / 1MB
```

Expected：只有 `README.md` 修改與 `docs/media/val-loop-short.gif` 新增（`docs/media/manim/media/` 與 `.venv` 被忽略）；GIF ≤ 8 MB。

```powershell
git add README.md docs/media/val-loop-short.gif
git commit -m "docs: embed the 30-second active-learning explainer in the README"
```

push 由 owner 決定；回報 commit 雜湊與 GIF 大小。

---

## Self-review

- **Spec coverage**：§0 目的（Task 10 嵌入）；§1 分鏡五段（Task 5、6、7、8）與凍結文字（Task 3）；§2 檔案配置（Task 1、9）；§3 資料綁定（Task 2；`metrics.csv` 不讀）；§4 字型與顏色（Task 4）、方塊網格（Task 5）；§5 渲染與輸出、README（Task 9、10）；§6 四類測試與人工檢查（Task 2、3、4、5–8 的抽幀、Task 10）；§7 邊界（Global Constraints）；§8 完成定義（Task 8 全測、Task 9 一條指令、Task 10 審閱門與 commit）。
- **Placeholder scan**：無 TBD／TODO；每個程式步驟都有完整程式碼。
- **Type consistency**：`Context`、`PoolLayout`、`LaneSet` 的欄位與各 task 的使用一致；`text(ctx, key, size, color)` 簽名在 Task 5 定義、6–8 沿用；`ctx.copy["delta_seed_<seed>"]` 由 Task 3 的 `render_copy` 產生；`ExplainerData.start_count()`、`positive_seed_count()` 在 Task 2 定義、Task 3 與 5–7 使用。
