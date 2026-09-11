# Manim 長版說明影片 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 做出約 2 分鐘、繁體中文字幕自讀的 1080p60 mp4：短版四段接三章（訓練長度規則、全標籤參考基線、最低類別 recall 負面結果）再接結尾卡，所有數字從 `docs/results/` 讀出。

**Architecture:** 沿用 `docs/media/manim/` 的 uv 專案。`data.py` 擴充 `ExplainerData`（步數、epoch、平均曲線、參考基線、20% 比例與 recall）並新增 `load_rule_pair()` 同時載入規則 A 與 B；`copy.py` 新增 `COPY_LONG` 與 `render_copy_long()`，句子裡的「都為正」「互不重疊」「重疊」等主張在渲染文字時對資料驗證，不成立就拋錯；`scenes_long.py` 三章各一個函式加結尾卡，`ValLoopLong` 重用短版的四段函式。`render.ps1` 加 `-Scene`。

**Tech Stack:** Manim Community 0.21.0、manimpango、ffmpeg、uv、pytest、Windows PowerShell 5.1。

## Global Constraints

- 規格：[docs/superpowers/specs/2026-09-11-val-explainer-manim-long-design.md](../specs/2026-09-11-val-explainer-manim-long-design.md)。畫面文字以規格 §1 為準。
- 不改短版的畫面、文字與 `docs/media/val-loop-short.gif`；`scenes_short.py` 不改。
- 動畫裡沒有任何手打的數字：規則 B 步數與 epoch 讀收據 `fits[*].steps`／`epochs_started`；規則 A 步數讀舊收據 `runtime.steps`，epoch 算 `ceil(steps ÷ (images // batch))`；平均曲線讀 summary `mean_map50_95`；參考基線讀 summary `reference.per_seed` 與各參考基線目錄的 `fit-receipt.json`（`epochs_started`）；20% 比例與最低類別 recall 讀 `per_seed`。缺檔或缺欄位拋 `ExplainerDataError`。
- 禁詞守門與顯示寬度上限（34）沿用 `copy.py`；句子的主張（3/3、互不重疊、重疊）在 `render_copy_long` 內驗證。
- 顏色、字型沿用 `style.py`（Okabe-Ito；Microsoft JhengHei）。
- 長版只出 1080p60 mp4，時長門檻 130 秒，不做 GIF，mp4 不進 git，複製到 `<evidence-root>\media\val-loop-long-<UTC 時間戳>.mp4`。
- 指令都在 `docs/media/manim` 目錄內以 `uv run ...` 執行（下面每條都寫全）；跑 Python 時設 `PYTHONDONTWRITEBYTECODE=1`。
- Manim 以檔案路徑載入場景，套件內一律用絕對 import（`from val_explainer.xxx import ...`）。
- 每個 task 結束 commit 到 `main`；不 push。

---

## 檔案結構

| 檔案 | 責任 |
|---|---|
| `docs/media/manim/val_explainer/data.py` | 擴充 `ExplainerData`、新增 `Reference`、`RulePair`、`load_rule_pair()`、`range_text()` |
| `docs/media/manim/val_explainer/copy.py` | 新增 `COPY_LONG`、`render_copy_long(pair)`（含主張驗證） |
| `docs/media/manim/val_explainer/scenes_long.py` | `LongContext`、`make_long_context()`、`text_long()`、三章函式、`closing_segment()`、五個 Scene |
| `docs/media/manim/tests/test_data.py` | 加規則對、epoch、參考基線、`range_text` 測試 |
| `docs/media/manim/tests/test_copy.py` | 加 `COPY_LONG` 守門與主張測試 |
| `docs/media/manim/tests/test_scene_smoke.py` | 加五個長版 Scene |
| `docs/media/manim/render.ps1` | `-Scene` 參數，長版不做 GIF |
| `docs/media/manim/README.md` | 長版段落 |

---

### Task 1: `data.py` 擴充：規則對、步數與 epoch、參考基線、20% 比例與 recall

**Files:**
- Modify: `docs/media/manim/val_explainer/data.py`
- Test: `docs/media/manim/tests/test_data.py`

**Interfaces:**
- Consumes：現有 `ExplainerData`、`load_explainer_data`、`_load_json`、`_require`、`ExplainerDataError`、`ARMS`。
- Produces：
  - `@dataclass(frozen=True) class Reference`：`map50_95: float`、`steps: int`、`images: int`、`epochs: int`
  - `ExplainerData` 新欄位（皆有預設值）：`rule_name: str = ""`、`batch_size: int = 0`、`steps: dict[str, int]`（預算鍵 → 每 fit 步數）、`epochs: dict[str, int]`、`mean_curve: dict[str, list[tuple[float, float]]]`（arm → 四點）、`reference: dict[int, Reference]`、`reference_mean: float = 0.0`、`ratio_20: dict[int, dict[str, float]]`、`min_recall_20: dict[int, dict[str, float]]`
  - `ExplainerData.arm_values_20(table: str, arm: str) -> list[float]`（`table` 是 `"ratio_20"` 或 `"min_recall_20"`，依 `seeds` 順序）
  - `@dataclass(frozen=True) class RulePair`：`rule_a: ExplainerData`、`rule_b: ExplainerData`
  - `load_rule_pair(results_root: Path = DEFAULT_RESULTS_ROOT) -> RulePair`（A 讀 `summary-3seeds-with-reference`，B 讀 `summary-ep18-3seeds`；`rule_name` 必須分別是 `fixed-steps`、`fixed-epochs`）
  - `range_text(values: list[float], decimals: int) -> str`（`"低–高"`，en dash）
  - `BUDGET_KEYS = ("0.02", "0.05", "0.10", "0.20")`

- [ ] **Step 1: 在 `tests/test_data.py` 末尾加失敗的測試**

```python
from val_explainer.data import BUDGET_KEYS, Reference, RulePair, load_rule_pair, range_text


def test_rule_pair_loads_both_rules():
    pair = load_rule_pair()
    assert isinstance(pair, RulePair)
    assert pair.rule_a.rule_name == "fixed-steps"
    assert pair.rule_b.rule_name == "fixed-epochs"
    assert pair.rule_a.seeds == pair.rule_b.seeds
    assert pair.rule_a.batch_size == 8 and pair.rule_b.batch_size == 8


def test_rule_b_steps_and_epochs_come_from_receipts():
    b = load_rule_pair().rule_b
    assert b.steps == {"0.02": 200, "0.05": 252, "0.10": 504, "0.20": 1008}
    assert b.epochs == {"0.02": 40, "0.05": 18, "0.10": 18, "0.20": 18}


def test_rule_a_steps_from_runtime_and_epochs_computed_with_full_batches():
    a = load_rule_pair().rule_a
    assert a.steps == {k: 1000 for k in BUDGET_KEYS}
    # ceil(1000 / (images // 8)) with images 46/113/226/451 -> 200/72/36/18
    assert a.epochs == {"0.02": 200, "0.05": 72, "0.10": 36, "0.20": 18}


def test_mean_curve_has_four_points_per_arm_and_matches_summary():
    b = load_rule_pair().rule_b
    summary = _summary()
    for arm in ARMS:
        points = b.mean_curve[arm]
        assert [p[0] for p in points] == [0.02, 0.05, 0.10, 0.20]
        assert points[0][1] == pytest.approx(summary["mean_map50_95"]["shared"]["0.02"])
        assert points[3][1] == pytest.approx(summary["mean_map50_95"][arm]["0.20"])


def test_reference_per_seed_matches_summary_and_receipt():
    pair = load_rule_pair()
    for data, summary_dir in ((pair.rule_a, "summary-3seeds-with-reference"), (pair.rule_b, "summary-ep18-3seeds")):
        summary = json.loads((DEFAULT_RESULTS_ROOT / summary_dir / "summary.json").read_text(encoding="utf-8"))
        for seed in data.seeds:
            ref = data.reference[seed]
            entry = summary["reference"]["per_seed"][str(seed)]
            assert isinstance(ref, Reference)
            assert ref.map50_95 == pytest.approx(entry["mAP50_95"])
            assert ref.steps == entry["steps"] and ref.images == entry["images"]
            receipt = json.loads((DEFAULT_RESULTS_ROOT / entry["experiment_id"] / "fit-receipt.json").read_text(encoding="utf-8"))["normative"]
            assert ref.epochs == receipt["epochs_started"]
        assert data.reference_mean == pytest.approx(summary["reference"]["mean_map50_95"])
    assert pair.rule_b.reference[17].epochs == 18
    assert pair.rule_a.reference[17].epochs == 4


def test_ratio_and_min_recall_at_20_match_summary():
    b = load_rule_pair().rule_b
    summary = _summary()
    for entry in summary["per_seed"]:
        seed = int(entry["seed"])
        for arm in ARMS:
            assert b.ratio_20[seed][arm] == pytest.approx(entry["fraction_of_reference_at_0.20"][arm])
            assert b.min_recall_20[seed][arm] == pytest.approx(entry["min_class_recall_at_0.20"][arm])
    assert b.arm_values_20("ratio_20", "random") == [b.ratio_20[s]["random"] for s in b.seeds]


def test_range_text_formats_min_and_max():
    assert range_text([0.302, 0.445, 0.363], 2) == "0.30–0.45"
    assert range_text([0.0656, 0.0670, 0.0666], 4) == "0.0656–0.0670"
    assert range_text([0.3], 3) == "0.300–0.300"


def test_missing_reference_block_raises(tmp_path: Path):
    shutil.copytree(DEFAULT_RESULTS_ROOT / "summary-ep18-3seeds", tmp_path / "summary-ep18-3seeds")
    for entry in _summary()["per_seed"]:
        shutil.copytree(DEFAULT_RESULTS_ROOT / entry["experiment_id"], tmp_path / entry["experiment_id"])
    summary_path = tmp_path / "summary-ep18-3seeds" / "summary.json"
    document = json.loads(summary_path.read_text(encoding="utf-8"))
    del document["reference"]
    summary_path.write_text(json.dumps(document), encoding="utf-8")
    with pytest.raises(ExplainerDataError, match="reference"):
        load_explainer_data(results_root=tmp_path)
```

- [ ] **Step 2: 跑測試確認失敗**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_data.py -q
cd ..\..\..
```

Expected：`ImportError: cannot import name 'BUDGET_KEYS'`（collection error）。

- [ ] **Step 3: 改寫 `data.py`（整檔內容如下，保留原有行為）**

```python
"""Read the committed evidence the explainer animates. Nothing here is hand-typed."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# docs/media/manim/val_explainer/data.py -> parents[3] is docs/
DEFAULT_RESULTS_ROOT = Path(__file__).resolve().parents[3] / "results"
DEFAULT_SUMMARY_DIR = "summary-ep18-3seeds"
RULE_A_SUMMARY_DIR = "summary-3seeds-with-reference"
ARMS = ("random", "entropy", "margin")
SHARED_ARM = "shared"
BUDGET_KEYS = ("0.02", "0.05", "0.10", "0.20")
FITS_PER_EXPERIMENT = 10
POINTS_PER_ARM = 4


class ExplainerDataError(ValueError):
    """Raised when the committed evidence is missing or malformed."""


@dataclass(frozen=True)
class Reference:
    map50_95: float
    steps: int
    images: int
    epochs: int


@dataclass(frozen=True)
class ExplainerData:
    pool_size: int
    test_size: int
    budgets: dict[str, int]
    seeds: list[int]
    delta: dict[str, dict[int, float]]
    curves: dict[int, dict[str, list[tuple[float, float]]]]
    claim_rule: str
    rule_name: str = ""
    batch_size: int = 0
    steps: dict[str, int] = field(default_factory=dict)
    epochs: dict[str, int] = field(default_factory=dict)
    mean_curve: dict[str, list[tuple[float, float]]] = field(default_factory=dict)
    reference: dict[int, Reference] = field(default_factory=dict)
    reference_mean: float = 0.0
    ratio_20: dict[int, dict[str, float]] = field(default_factory=dict)
    min_recall_20: dict[int, dict[str, float]] = field(default_factory=dict)

    def positive_seed_count(self, arm: str) -> int:
        return sum(1 for value in self.delta[arm].values() if value > 0)

    def start_count(self) -> int:
        return self.budgets["0.02"]

    def arm_values_20(self, table: str, arm: str) -> list[float]:
        rows: dict[int, dict[str, float]] = getattr(self, table)
        return [rows[seed][arm] for seed in self.seeds]


@dataclass(frozen=True)
class RulePair:
    rule_a: ExplainerData
    rule_b: ExplainerData


def format_delta(value: float) -> str:
    return f"{value:+.4f}"


def range_text(values: list[float], decimals: int) -> str:
    return f"{min(values):.{decimals}f}–{max(values):.{decimals}f}"


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


def _budget_key(fraction: float) -> str:
    return f"{fraction:.2f}"


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


def _steps_and_epochs(fits: list[dict[str, Any]], runtime: dict[str, Any], budgets: dict[str, int], path: Path) -> tuple[dict[str, int], dict[str, int]]:
    """Per-budget steps and epochs. New receipts carry both per fit; old ones give steps in runtime and epochs are computed."""
    batch = int(_require(runtime, "batch_size", path))
    steps: dict[str, int] = {}
    epochs: dict[str, int] = {}
    for fit in fits:
        key = _budget_key(float(fit["budget_fraction"]))
        if "steps" in fit and "epochs_started" in fit:
            value_steps, value_epochs = int(fit["steps"]), int(fit["epochs_started"])
        else:
            value_steps = int(_require(runtime, "steps", path))
            value_epochs = math.ceil(value_steps / (budgets[key] // batch))
        if key in steps and (steps[key], epochs[key]) != (value_steps, value_epochs):
            raise ExplainerDataError(f"{path}: fits at budget {key} disagree on steps/epochs")
        steps[key], epochs[key] = value_steps, value_epochs
    if set(steps) != set(BUDGET_KEYS):
        raise ExplainerDataError(f"{path}: budgets covered {sorted(steps)}, expected {BUDGET_KEYS}")
    return steps, epochs


def _mean_curve(summary: dict[str, Any], path: Path) -> dict[str, list[tuple[float, float]]]:
    table = _require(summary, "mean_map50_95", path)
    if "shared" not in table or "0.02" not in table["shared"]:
        raise ExplainerDataError(f"{path}: mean_map50_95 lacks the shared 2% point")
    start = (0.02, float(table["shared"]["0.02"]))
    curves: dict[str, list[tuple[float, float]]] = {}
    for arm in ARMS:
        if arm not in table:
            raise ExplainerDataError(f"{path}: mean_map50_95 lacks arm {arm!r}")
        curves[arm] = [start] + [(float(key), float(table[arm][key])) for key in ("0.05", "0.10", "0.20")]
    return curves


def _references(root: Path, summary: dict[str, Any], seeds: list[int], path: Path) -> tuple[dict[int, Reference], float]:
    block = _require(summary, "reference", path)
    per_seed = _require(block, "per_seed", path)
    references: dict[int, Reference] = {}
    for seed in seeds:
        entry = per_seed.get(str(seed))
        if entry is None:
            raise ExplainerDataError(f"{path}: reference block lacks seed {seed}")
        receipt_path = root / str(_require(entry, "experiment_id", path)) / "fit-receipt.json"
        receipt = _require(_load_json(receipt_path), "normative", receipt_path)
        references[seed] = Reference(
            map50_95=float(_require(entry, "mAP50_95", path)),
            steps=int(_require(entry, "steps", path)),
            images=int(_require(entry, "images", path)),
            epochs=int(_require(receipt, "epochs_started", receipt_path)),
        )
    return references, float(_require(block, "mean_map50_95", path))


def load_explainer_data(
    results_root: Path = DEFAULT_RESULTS_ROOT,
    summary_dir: str = DEFAULT_SUMMARY_DIR,
) -> ExplainerData:
    root = Path(results_root)
    summary_path = root / summary_dir / "summary.json"
    summary = _load_json(summary_path)
    seeds = [int(seed) for seed in _require(summary, "seeds", summary_path)]
    claim_rule = str(_require(summary, "claim_rule", summary_path))
    rule_name = str(_require(summary, "training_rule", summary_path))
    per_seed = _require(summary, "per_seed", summary_path)

    delta: dict[str, dict[int, float]] = {"entropy": {}, "margin": {}}
    curves: dict[int, dict[str, list[tuple[float, float]]]] = {}
    ratio_20: dict[int, dict[str, float]] = {}
    min_recall_20: dict[int, dict[str, float]] = {}
    header: tuple[int, int, dict[str, int]] | None = None
    steps_epochs: tuple[dict[str, int], dict[str, int]] | None = None
    batch_size = 0

    for entry in per_seed:
        seed = int(_require(entry, "seed", summary_path))
        experiment_id = str(_require(entry, "experiment_id", summary_path))
        deltas = _require(entry, "delta_vs_random", summary_path)
        for arm in delta:
            if arm not in deltas:
                raise ExplainerDataError(f"{summary_path}: seed {seed} lacks delta for {arm!r}")
            delta[arm][seed] = float(deltas[arm])
        ratios = _require(entry, "fraction_of_reference_at_0.20", summary_path)
        recalls = _require(entry, "min_class_recall_at_0.20", summary_path)
        ratio_20[seed] = {arm: float(ratios[arm]) for arm in ARMS}
        min_recall_20[seed] = {arm: float(recalls[arm]) for arm in ARMS}

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
        runtime = _require(normative, "runtime", receipt_path)
        batch_size = int(_require(runtime, "batch_size", receipt_path))
        current = _steps_and_epochs(fits, runtime, budgets, receipt_path)
        if steps_epochs is None:
            steps_epochs = current
        elif steps_epochs != current:
            raise ExplainerDataError(f"{receipt_path}: steps/epochs differ from the first seed")

    if header is None or steps_epochs is None or sorted(curves) != sorted(seeds):
        raise ExplainerDataError(f"{summary_path}: per_seed entries do not cover seeds {seeds}")
    pool_size, test_size, budgets = header
    steps, epochs = steps_epochs
    references, reference_mean = _references(root, summary, seeds, summary_path)
    return ExplainerData(
        pool_size=pool_size,
        test_size=test_size,
        budgets=budgets,
        seeds=seeds,
        delta=delta,
        curves=curves,
        claim_rule=claim_rule,
        rule_name=rule_name,
        batch_size=batch_size,
        steps=steps,
        epochs=epochs,
        mean_curve=_mean_curve(summary, summary_path),
        reference=references,
        reference_mean=reference_mean,
        ratio_20=ratio_20,
        min_recall_20=min_recall_20,
    )


def load_rule_pair(results_root: Path = DEFAULT_RESULTS_ROOT) -> RulePair:
    rule_a = load_explainer_data(results_root, RULE_A_SUMMARY_DIR)
    rule_b = load_explainer_data(results_root, DEFAULT_SUMMARY_DIR)
    if rule_a.rule_name != "fixed-steps" or rule_b.rule_name != "fixed-epochs":
        raise ExplainerDataError(f"unexpected rules: {rule_a.rule_name!r}, {rule_b.rule_name!r}")
    if rule_a.seeds != rule_b.seeds:
        raise ExplainerDataError("the two rules do not share the same seeds")
    return RulePair(rule_a=rule_a, rule_b=rule_b)
```

- [ ] **Step 4: 跑全部資料測試（含短版的舊測試）確認通過**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_data.py tests/test_copy.py tests/test_style.py -q
cd ..\..\..
```

Expected：全部通過（9 ＋ 8 ＋ 9 ＋ 3 ＝ 29）。`test_truncated_receipt_raises` 仍要通過：它複製的 summary 目錄含 `reference` 區塊，但參考基線目錄沒複製，會先在 fits 數量那裡拋錯（訊息含 `fits`），符合 `match="fits"`。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/data.py docs/media/manim/tests/test_data.py
git commit -m "feat(explainer): load both training rules with steps, epochs, references and 20% tables"
```

---

### Task 2: `copy.py`：長版文字、樣板填入與主張驗證

**Files:**
- Modify: `docs/media/manim/val_explainer/copy.py`
- Test: `docs/media/manim/tests/test_copy.py`

**Interfaces:**
- Consumes：`RulePair`、`ExplainerData.arm_values_20`、`positive_seed_count`、`range_text`、`BUDGET_KEYS`（Task 1）；現有 `MAX_CHARS_PER_LINE`、`NEGATIONS`、`BANNED`、`display_width`。
- Produces：
  - `COPY_LONG: dict[str, str]`（鍵見 Step 3）
  - `render_copy_long(pair: RulePair) -> dict[str, str]`：填入數字；另外產生每預算的 `bar_images_<key>`、`bar_epochs_a_<key>`、`bar_steps_b_<key>`、`bar_epochs_b_<key>`；主張不成立時拋 `ExplainerDataError`
  - `intervals_overlap(a: list[float], b: list[float]) -> bool`

- [ ] **Step 1: 在 `tests/test_copy.py` 末尾加失敗的測試**

```python
from val_explainer.copy import COPY_LONG, intervals_overlap, render_copy_long
from val_explainer.data import BUDGET_KEYS, ExplainerDataError, load_rule_pair, range_text

EXPECTED_LONG_KEYS = {
    "ch1_title", "ch1_sub", "ch1_rule_a", "ch1_rule_a_epochs", "ch1_rule_b", "ch1_rule_b_note", "ch1_computed",
    "ch1_sign_a", "ch1_sign_b", "ch1_both", "ch1_fair", "ch1_axis_a", "ch1_axis_b",
    "ch2_ref_line", "ch2_ref_range", "ch2_ratio", "ch2_ref_a", "ch2_ref_a_note",
    "ch3_title", "ch3_sub", "ch3_a", "ch3_a_ranges", "ch3_b", "ch3_b_note",
    "close_1", "close_2", "close_path",
}


def test_copy_long_has_exactly_the_frozen_keys():
    assert set(COPY_LONG) == EXPECTED_LONG_KEYS


def test_long_lines_fit_and_banned_phrases_are_negated():
    rendered = render_copy_long(load_rule_pair())
    for key, text in rendered.items():
        assert text.strip(), key
        for line in text.split("\n"):
            assert display_width(line) <= MAX_CHARS_PER_LINE, (key, line, display_width(line))
        for phrase in BANNED:
            if phrase.lower() in text.lower():
                assert any(neg in text for neg in NEGATIONS), (key, text)


def test_long_numbers_come_from_data():
    pair = load_rule_pair()
    a, b = pair.rule_a, pair.rule_b
    rendered = render_copy_long(pair)
    assert f"{a.steps['0.02']:,}" in rendered["ch1_rule_a"]
    assert str(a.epochs["0.02"]) in rendered["ch1_rule_a_epochs"] and str(a.epochs["0.20"]) in rendered["ch1_rule_a_epochs"]
    assert str(b.epochs["0.20"]) in rendered["ch1_rule_b"] and str(b.steps["0.02"]) in rendered["ch1_rule_b"]
    assert range_text([r.map50_95 for r in b.reference.values()], 4) in rendered["ch2_ref_range"]
    assert range_text(b.arm_values_20("ratio_20", "random"), 2) in rendered["ch2_ratio"]
    assert str(a.reference[17].epochs) in rendered["ch2_ref_a"]
    assert range_text(a.arm_values_20("min_recall_20", "margin"), 3) in rendered["ch3_a_ranges"]
    assert range_text(b.arm_values_20("min_recall_20", "random"), 3) in rendered["ch3_b"]
    for key in BUDGET_KEYS:
        assert rendered[f"bar_images_{key}"] == f"{b.budgets[key]} 張"
        assert rendered[f"bar_epochs_a_{key}"] == f"{a.epochs[key]} epoch"
        assert rendered[f"bar_steps_b_{key}"] == f"{b.steps[key]:,} 步"
        assert rendered[f"bar_epochs_b_{key}"] == f"{b.epochs[key]} epoch"


def test_intervals_overlap():
    assert intervals_overlap([0.1, 0.3], [0.2, 0.5])
    assert not intervals_overlap([0.1, 0.2], [0.3, 0.4])
    assert intervals_overlap([0.1, 0.3], [0.3, 0.4])


def test_claims_are_verified_against_data():
    pair = load_rule_pair()
    rendered = render_copy_long(pair)
    assert rendered["close_1"] == "不宣稱降低標註成本；同機重播並非位元相同"
    assert rendered["close_2"] == "三個 seed 的最大最小是範圍，不是信賴區間"
    # forge a pair whose rule-A recall intervals overlap: the "互不重疊" sentence must refuse to render
    import dataclasses
    forged_recall = {seed: dict(row) for seed, row in pair.rule_a.min_recall_20.items()}
    first = pair.rule_a.seeds[0]
    forged_recall[first]["random"] = forged_recall[first]["margin"]
    forged_a = dataclasses.replace(pair.rule_a, min_recall_20=forged_recall)
    with pytest.raises(ExplainerDataError, match="ch3_a"):
        render_copy_long(dataclasses.replace(pair, rule_a=forged_a))
```

- [ ] **Step 2: 跑測試確認失敗**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_copy.py -q
cd ..\..\..
```

Expected：`ImportError: cannot import name 'COPY_LONG'`。

- [ ] **Step 3: 在 `copy.py` 末尾加入**

```python
# ------------------------------------------------------------------ long version

COPY_LONG: dict[str, str] = {
    "ch1_title": "為什麼要跑第二輪",
    "ch1_sub": "固定步數把預算和訓練長度綁在一起",
    "ch1_rule_a": "規則 A：每個 fit 固定 {steps_a} 步",
    "ch1_rule_a_epochs": "{start} 張跑 {epochs_a_02} 個 epoch，{n20} 張只跑 {epochs_a_20} 個",
    "ch1_rule_b": "規則 B：固定 {epochs_b} 個 epoch，最低 {min_steps} 步",
    "ch1_rule_b_note": "步數隨張數放大；2% 被最低步數托住",
    "ch1_computed": "規則 A 的 epoch 依規則算出",
    "ch1_sign_a": "Δ entropy {n_e_a}/{total}・Δ margin {n_m_a}/{total}",
    "ch1_sign_b": "Δ entropy {n_e_b}/{total}・Δ margin {n_m_b}/{total}",
    "ch1_both": "兩種規則下，entropy 與 margin 對 random 的配對差都是 {total} 個 seed 為正",
    "ch1_fair": "兩種規則回答不同的問題，不預設哪一個公平",
    "ch1_axis_a": "規則 A（固定步數）",
    "ch1_axis_b": "規則 B（固定 epoch）",
    "ch2_ref_line": "全標籤參考基線：{pool} 張全部標註、{epochs_ref_b} 個 epoch",
    "ch2_ref_range": "三個 seed 範圍 {ref_b_range}",
    "ch2_ratio": "20% 預算佔參考基線：random {ratio_random}、entropy {ratio_entropy}、margin {ratio_margin}",
    "ch2_ref_a": "規則 A 的參考基線只有 {steps_a} 步（{epochs_ref_a} 個 epoch），是欠訓的",
    "ch2_ref_a_note": "固定 GPU 成本下，全部標籤沒有比 20% 多換到 mAP；這不能拿來說 20% 已經足夠",
    "ch3_title": "一個負面結果",
    "ch3_sub": "20% 預算的最低類別 recall",
    "ch3_a": "v0.2-lite（規則 A）：三個 arm 的範圍互不重疊",
    "ch3_a_ranges": "random {rec_a_random}、entropy {rec_a_entropy}、margin {rec_a_margin}",
    "ch3_b": "規則 B：random {rec_b_random} 與 entropy、margin 重疊",
    "ch3_b_note": "這條證據跟訓練長度規則有關，不再單獨當作結論",
    "close_1": "不宣稱降低標註成本；同機重播並非位元相同",
    "close_2": "三個 seed 的最大最小是範圍，不是信賴區間",
    "close_path": "docs/results/2026-09-11-v0.2.1-training-rule.md",
}


def intervals_overlap(a: list[float], b: list[float]) -> bool:
    return max(min(a), min(b)) <= min(max(a), max(b))


def render_copy_long(pair: RulePair) -> dict[str, str]:
    """Fill COPY_LONG from both rules and refuse to render sentences whose claim the data no longer supports."""
    a, b = pair.rule_a, pair.rule_b
    total = len(b.seeds)
    first_seed = b.seeds[0]
    values = {
        "steps_a": f"{a.steps['0.02']:,}",
        "start": b.start_count(),
        "epochs_a_02": a.epochs["0.02"],
        "n20": b.budgets["0.20"],
        "epochs_a_20": a.epochs["0.20"],
        "epochs_b": b.epochs["0.20"],
        "min_steps": b.steps["0.02"],
        "n_e_a": a.positive_seed_count("entropy"),
        "n_m_a": a.positive_seed_count("margin"),
        "n_e_b": b.positive_seed_count("entropy"),
        "n_m_b": b.positive_seed_count("margin"),
        "total": total,
        "pool": f"{b.pool_size:,}",
        "epochs_ref_b": b.reference[first_seed].epochs,
        "ref_b_range": range_text([r.map50_95 for r in b.reference.values()], 4),
        "ratio_random": range_text(b.arm_values_20("ratio_20", "random"), 2),
        "ratio_entropy": range_text(b.arm_values_20("ratio_20", "entropy"), 2),
        "ratio_margin": range_text(b.arm_values_20("ratio_20", "margin"), 2),
        "epochs_ref_a": a.reference[first_seed].epochs,
        "rec_a_random": range_text(a.arm_values_20("min_recall_20", "random"), 3),
        "rec_a_entropy": range_text(a.arm_values_20("min_recall_20", "entropy"), 3),
        "rec_a_margin": range_text(a.arm_values_20("min_recall_20", "margin"), 3),
        "rec_b_random": range_text(b.arm_values_20("min_recall_20", "random"), 3),
    }
    # claims the sentences make
    if not all(values[k] == total for k in ("n_e_a", "n_m_a", "n_e_b", "n_m_b")):
        raise ExplainerDataError("ch1_both: not every paired delta is positive under both rules")
    rec_a = {arm: a.arm_values_20("min_recall_20", arm) for arm in ARMS}
    if intervals_overlap(rec_a["random"], rec_a["entropy"]) or intervals_overlap(rec_a["entropy"], rec_a["margin"]) or intervals_overlap(rec_a["random"], rec_a["margin"]):
        raise ExplainerDataError("ch3_a: rule-A recall ranges overlap; the sentence would be false")
    rec_b = {arm: b.arm_values_20("min_recall_20", arm) for arm in ARMS}
    if not (intervals_overlap(rec_b["random"], rec_b["entropy"]) and intervals_overlap(rec_b["random"], rec_b["margin"])):
        raise ExplainerDataError("ch3_b: rule-B random range does not overlap both arms; the sentence would be false")
    if a.reference[first_seed].epochs >= b.reference[first_seed].epochs:
        raise ExplainerDataError("ch2_ref_a: rule-A reference is not the under-trained one")
    filled = {key: text.format(**values) for key, text in COPY_LONG.items()}
    for key in BUDGET_KEYS:
        filled[f"bar_images_{key}"] = f"{b.budgets[key]} 張"
        filled[f"bar_epochs_a_{key}"] = f"{a.epochs[key]} epoch"
        filled[f"bar_steps_b_{key}"] = f"{b.steps[key]:,} 步"
        filled[f"bar_epochs_b_{key}"] = f"{b.epochs[key]} epoch"
    return filled
```

並把檔案開頭的 import 改成：

```python
from .data import ARMS, BUDGET_KEYS, ExplainerData, ExplainerDataError, RulePair, format_delta, range_text
```

- [ ] **Step 4: 跑測試確認通過**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; uv run pytest tests/test_copy.py -q
cd ..\..\..
```

Expected：全部通過（原 9 ＋ 新 5）。若 `ch2_ref_a_note` 或 `ch1_both` 超過 34 顯示寬度，不改句子，改 `MAX_CHARS_PER_LINE` 到剛好夠的值並在 commit 訊息註明（畫面上由 `text()` 的寬度上限保護）。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/copy.py docs/media/manim/tests/test_copy.py
git commit -m "feat(explainer): long-version wording with data-verified claims"
```

---

### Task 3: `scenes_long.py` 第一章：兩種規則

**Files:**
- Create: `docs/media/manim/val_explainer/scenes_long.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`

**Interfaces:**
- Consumes：`load_rule_pair`、`render_copy_long`（Task 1、2）；短版的 `Context`、`make_context`、`text`、`_axes`、`_line`、`_tick`、`X_TICKS`、`title_segment`、`build_pool_layout`、`pool_segment`、`loop_segment`、`curve_segment`、`MAX_TEXT_WIDTH`。
- Produces：
  - `@dataclass class LongContext`：`pair: RulePair`、`copy: dict[str, str]`、`style: Style`、`short: Context`
  - `make_long_context() -> LongContext`
  - `text_long(ctx: LongContext, key: str, size: str = "label", color: str | None = None) -> Text`
  - `chapter_card(scene, ctx, title_key, sub_key) -> None`（2 秒章名卡，自己 fade out）
  - `chapter_rules_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None`
  - Scene：`ChapterRules`

- [ ] **Step 1: 在冒煙測試加入長版場景（先只加 `ChapterRules`）**

把 `test_scene_smoke.py` 改成兩個參數化：

```python
SHORT_SCENES = ["TitleSegment", "PoolSegment", "LoopSegment", "CurveSegment", "OutroSegment", "ValLoopShort"]
LONG_SCENES = ["ChapterRules"]


@pytest.mark.skipif(os.environ.get("VAL_EXPLAINER_RENDER") != "1", reason="set VAL_EXPLAINER_RENDER=1 to run manim")
@pytest.mark.parametrize("scene_file,scene", [("scenes_short.py", s) for s in SHORT_SCENES] + [("scenes_long.py", s) for s in LONG_SCENES])
def test_dry_run_constructs_the_scene(scene_file, scene):
    completed = subprocess.run(
        [sys.executable, "-m", "manim", "--dry_run", "-ql", "--media_dir", str(PROJECT / "media"), str(PROJECT / "val_explainer" / scene_file), scene],
        cwd=PROJECT,
        capture_output=True,
        text=True,
        timeout=900,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
```

（刪掉原本的 `SCENE_FILE` 常數與舊的 parametrize。）

- [ ] **Step 2: 寫 `scenes_long.py`（第一章）**

```python
"""The long portfolio explainer: the short segments, three chapters, a closing card."""

from __future__ import annotations

from dataclasses import dataclass

from manim import (
    DOWN,
    LEFT,
    RIGHT,
    UP,
    Create,
    FadeIn,
    FadeOut,
    GrowFromEdge,
    LaggedStart,
    Rectangle,
    Scene,
    Text,
    Transform,
    VGroup,
)

from val_explainer.copy import render_copy_long
from val_explainer.data import ARMS, BUDGET_KEYS, RulePair, load_rule_pair
from val_explainer.scenes_short import (
    MAX_TEXT_WIDTH,
    X_TICKS,
    Context,
    _axes,
    _line,
    _tick,
    build_pool_layout,
    curve_segment,
    loop_segment,
    make_context,
    pool_segment,
    title_segment,
)
from val_explainer.style import Style


@dataclass
class LongContext:
    pair: RulePair
    copy: dict[str, str]
    style: Style
    short: Context


def make_long_context() -> LongContext:
    short = make_context()
    pair = load_rule_pair()
    return LongContext(pair=pair, copy=render_copy_long(pair), style=short.style, short=short)


def text_long(ctx: LongContext, key: str, size: str = "label", color: str | None = None) -> Text:
    mobject = Text(
        ctx.copy[key],
        font=ctx.style.font,
        font_size=ctx.style.sizes[size],
        color=color or ctx.style.colors["text"],
    )
    if mobject.width > MAX_TEXT_WIDTH:
        mobject.scale_to_fit_width(MAX_TEXT_WIDTH)
    return mobject


def chapter_card(scene: Scene, ctx: LongContext, title_key: str, sub_key: str) -> None:
    title = text_long(ctx, title_key, "title")
    sub = text_long(ctx, sub_key, "sub", ctx.style.colors["muted"]).next_to(title, DOWN, buff=0.4)
    scene.play(FadeIn(title, shift=UP * 0.2), FadeIn(sub), run_time=0.7)
    scene.wait(1.3)
    scene.play(FadeOut(title), FadeOut(sub), run_time=0.4)


# ------------------------------------------------------------------ chapter 1: two training-length rules

BAR_WIDTH = 1.3
BAR_MAX_HEIGHT = 3.0


def _bars(ctx: LongContext) -> tuple[VGroup, VGroup, VGroup]:
    """Four budget bars (images), their tick labels, and image-count labels."""
    b = ctx.pair.rule_b
    biggest = max(b.budgets.values())
    bars, ticks, counts = VGroup(), VGroup(), VGroup()
    for key in BUDGET_KEYS:
        height = max(BAR_MAX_HEIGHT * b.budgets[key] / biggest, 0.18)
        bar = Rectangle(width=BAR_WIDTH, height=height, fill_color=ctx.style.colors["pool"], fill_opacity=1.0, stroke_width=0)
        bars.add(bar)
    bars.arrange(RIGHT, buff=1.0, aligned_edge=DOWN).move_to(DOWN * 0.7)
    for key, bar in zip(BUDGET_KEYS, bars):
        ticks.add(_tick(ctx.short, X_TICKS[float(key)]).next_to(bar, DOWN, buff=0.15))
        counts.add(Text(ctx.copy[f"bar_images_{key}"], font=ctx.style.font, font_size=ctx.style.sizes["small"], color=ctx.style.colors["muted"]).next_to(bar, DOWN, buff=0.45))
    return bars, ticks, counts


def _epoch_labels(ctx: LongContext, bars: VGroup, prefix: str, color: str) -> VGroup:
    labels = VGroup()
    for key, bar in zip(BUDGET_KEYS, bars):
        label = Text(ctx.copy[f"{prefix}_{key}"], font=ctx.style.font, font_size=ctx.style.sizes["label"], color=color)
        labels.add(label.next_to(bar, UP, buff=0.15))
    return labels


def _mini_axes(ctx: LongContext, data, title_key: str, sign_key: str) -> VGroup:
    """A small three-arm mean-curve panel with its rule title and sign line."""
    y_max = round(max(p[1] for arm in ARMS for p in data.mean_curve[arm]) * 1.2 + 0.005, 2)
    axes = _axes(ctx.short, y_max)
    lines = VGroup(*[_line(axes, data.mean_curve[arm], ctx.style.colors[arm], 3) for arm in ARMS])
    title = text_long(ctx, title_key, "label").next_to(axes, UP, buff=0.3)
    sign = text_long(ctx, sign_key, "small", ctx.style.colors["start"]).next_to(axes, DOWN, buff=0.55)
    return VGroup(axes, lines, title, sign).scale(0.62)


def chapter_rules_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None:
    style = ctx.style
    chapter_card(scene, ctx, "ch1_title", "ch1_sub")

    bars, ticks, counts = _bars(ctx)
    epochs_a = _epoch_labels(ctx, bars, "bar_epochs_a", style.colors["start"])
    rule_a = text_long(ctx, "ch1_rule_a", "label").to_edge(UP, buff=0.5)
    rule_a_note = text_long(ctx, "ch1_rule_a_epochs", "caption", style.colors["muted"]).next_to(rule_a, DOWN, buff=0.2)
    computed = text_long(ctx, "ch1_computed", "small", style.colors["muted"]).to_corner(DOWN + RIGHT, buff=0.35)
    scene.play(FadeIn(rule_a), FadeIn(rule_a_note), run_time=0.5)
    scene.play(LaggedStart(*[GrowFromEdge(bar, DOWN) for bar in bars], lag_ratio=0.15), FadeIn(ticks), FadeIn(counts), run_time=1.0)
    scene.play(LaggedStart(*[FadeIn(label, shift=UP * 0.1) for label in epochs_a], lag_ratio=0.15), FadeIn(computed), run_time=0.9)
    scene.wait(1.8)

    steps_b = _epoch_labels(ctx, bars, "bar_steps_b", style.colors["text"])
    epochs_b = _epoch_labels(ctx, bars, "bar_epochs_b", style.colors["start"])
    for step_label, epoch_label in zip(steps_b, epochs_b):
        epoch_label.next_to(step_label, UP, buff=0.08)
    rule_b = text_long(ctx, "ch1_rule_b", "label").to_edge(UP, buff=0.5)
    rule_b_note = text_long(ctx, "ch1_rule_b_note", "caption", style.colors["muted"]).next_to(rule_b, DOWN, buff=0.2)
    scene.play(
        Transform(rule_a, rule_b), Transform(rule_a_note, rule_b_note), Transform(epochs_a, epochs_b),
        FadeIn(steps_b), FadeOut(computed),
        run_time=1.0,
    )
    scene.wait(2.0)

    scene.play(FadeOut(bars), FadeOut(ticks), FadeOut(counts), FadeOut(epochs_a), FadeOut(steps_b), FadeOut(rule_a), FadeOut(rule_a_note), run_time=0.5)
    panel_a = _mini_axes(ctx, ctx.pair.rule_a, "ch1_axis_a", "ch1_sign_a")
    panel_b = _mini_axes(ctx, ctx.pair.rule_b, "ch1_axis_b", "ch1_sign_b")
    panels = VGroup(panel_a, panel_b).arrange(RIGHT, buff=0.8).move_to(UP * 0.4)
    both = text_long(ctx, "ch1_both", "caption").to_edge(DOWN, buff=0.75)
    fair = text_long(ctx, "ch1_fair", "small", style.colors["muted"]).next_to(both, DOWN, buff=0.15)
    scene.play(Create(panel_a[0]), Create(panel_b[0]), FadeIn(panel_a[2]), FadeIn(panel_b[2]), run_time=0.8)
    scene.play(Create(panel_a[1]), Create(panel_b[1]), run_time=1.2)
    scene.play(FadeIn(panel_a[3]), FadeIn(panel_b[3]), run_time=0.5)
    scene.play(FadeIn(both), run_time=0.5)
    scene.play(FadeIn(fair), run_time=0.4)
    scene.wait(2.2)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


# ------------------------------------------------------------------ scenes


class ChapterRules(Scene):
    def construct(self) -> None:
        chapter_rules_segment(self, make_long_context(), fade_out=False)
```

- [ ] **Step 3: 跑冒煙測試**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest tests/test_scene_smoke.py -q
Remove-Item Env:VAL_EXPLAINER_RENDER
cd ..\..\..
```

Expected：`7 passed`。若 `Transform(epochs_a, epochs_b)` 抱怨子物件數不同，改成 `ReplacementTransform`；若 `_axes` 的 y 標籤太密（y_max 小於 0.05 時 step 0.01），可接受。

- [ ] **Step 4: 渲染最後一幀並看圖**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_long.py ChapterRules
cd ..\..\..
```

用 Read 打開 `media/images/scenes_long/ChapterRules_ManimCE_v0.21.0.png`：兩個小曲線圖並排、各自標題與黃色的「Δ entropy 3/3・Δ margin 3/3」、底部兩句說明不與圖重疊、無元素出界。太擠就把 `_mini_axes` 的 `scale(0.62)` 降到 0.55。另外用 `--format png -ql` 不方便看中段（長條圖那段），改用暫時的 Scene：在 `ChapterRules.construct` 裡先呼叫 `chapter_rules_segment` 的前半段不容易切，因此加一個小 Scene `ChapterRulesBars`（只做到長條與規則 B 標籤、不 fade out）供檢查，看完再刪除或保留（保留也無妨，不進 smoke 參數）。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_long.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): chapter 1, the two training-length rules"
```

---

### Task 4: 第二章：全標籤參考基線

**Files:**
- Modify: `docs/media/manim/val_explainer/scenes_long.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`（`LONG_SCENES` 加 `"ChapterReference"`）

**Interfaces:**
- Consumes：`LongContext`、`text_long`、`_axes`、`_line`（Task 3）。
- Produces：`chapter_reference_segment(scene, ctx, fade_out=True) -> None`、Scene `ChapterReference`。

- [ ] **Step 1: `LONG_SCENES` 加入 `"ChapterReference"`**

```python
LONG_SCENES = ["ChapterRules", "ChapterReference"]
```

- [ ] **Step 2: 加入第二章程式**

import 補上 `DashedLine`、`Polygon`：

```python
from manim import DashedLine, Polygon
```

在 `# ---- scenes` 之前加入：

```python
# ------------------------------------------------------------------ chapter 2: full-label reference


def chapter_reference_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None:
    style = ctx.style
    a, b = ctx.pair.rule_a, ctx.pair.rule_b
    ref_b = [r.map50_95 for r in b.reference.values()]
    ref_a = [r.map50_95 for r in a.reference.values()]
    y_max = round(max(ref_b) * 1.2 + 0.005, 2)
    axes = _axes(ctx.short, y_max).to_edge(LEFT, buff=0.7).shift(UP * 0.2)
    lines = VGroup(*[_line(axes, b.mean_curve[arm], style.colors[arm], 4) for arm in ARMS])
    scene.play(Create(axes), run_time=0.6)
    scene.play(Create(lines), run_time=1.2)

    ref_line = DashedLine(axes.c2p(0, b.reference_mean), axes.c2p(0.22, b.reference_mean), color=style.colors["muted"], stroke_width=3)
    panel = VGroup(
        text_long(ctx, "ch2_ref_line", "label"),
        text_long(ctx, "ch2_ref_range", "small", style.colors["muted"]),
    ).arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
    for mob in panel:
        if mob.width > 5.6:
            mob.scale_to_fit_width(5.6)
    panel.arrange(DOWN, aligned_edge=LEFT, buff=0.15).to_edge(RIGHT, buff=0.6).shift(UP * 1.6)
    scene.play(Create(ref_line), FadeIn(panel), run_time=1.0)
    scene.wait(1.2)

    ratio = text_long(ctx, "ch2_ratio", "caption")
    if ratio.width > 5.6:
        ratio.scale_to_fit_width(5.6)
    ratio.next_to(panel, DOWN, buff=0.5, aligned_edge=LEFT)
    scene.play(FadeIn(ratio), run_time=0.6)
    scene.wait(2.0)

    band = Polygon(
        axes.c2p(0, min(ref_a)), axes.c2p(0.22, min(ref_a)), axes.c2p(0.22, max(ref_a)), axes.c2p(0, max(ref_a)),
        fill_color=style.colors["muted"], fill_opacity=0.25, stroke_width=0,
    )
    ref_a_text = text_long(ctx, "ch2_ref_a", "caption", style.colors["start"])
    ref_a_note = text_long(ctx, "ch2_ref_a_note", "small", style.colors["muted"])
    notes = VGroup(ref_a_text, ref_a_note).arrange(DOWN, buff=0.15).to_edge(DOWN, buff=0.4)
    scene.play(FadeIn(band), FadeIn(ref_a_text), run_time=0.8)
    scene.play(FadeIn(ref_a_note), run_time=0.5)
    scene.wait(2.4)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


class ChapterReference(Scene):
    def construct(self) -> None:
        chapter_reference_segment(self, make_long_context(), fade_out=False)
```

（`ChapterReference` 類別放在 `# ---- scenes` 區塊。）

- [ ] **Step 3: 冒煙測試與最後一幀**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest tests/test_scene_smoke.py -q
Remove-Item Env:VAL_EXPLAINER_RENDER
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_long.py ChapterReference
cd ..\..\..
```

Expected：`8 passed`。看 `media/images/scenes_long/ChapterReference_ManimCE_v0.21.0.png`：虛線在三條曲線之上、灰色帶狀區在中間高度（規則 A 參考基線 0.035 到 0.043）與 20% 的 margin 曲線重疊是資料的實情；右側面板與底部兩行不與座標軸重疊；`ch2_ref_a_note` 那句最長，若被 `scale_to_fit_width` 縮得太小，把 `notes` 改成 `to_edge(DOWN, buff=0.3)` 並讓 `_axes` 的 `y_length` 由 4.0 改成 3.6（在本檔內 `axes.scale(0.9)`，不改短版）。

- [ ] **Step 4: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_long.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): chapter 2, the full-label reference baselines"
```

---

### Task 5: 第三章：最低類別 recall 的負面結果

**Files:**
- Modify: `docs/media/manim/val_explainer/scenes_long.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`（`LONG_SCENES` 加 `"ChapterRecall"`）

**Interfaces:**
- Produces：`chapter_recall_segment(scene, ctx, fade_out=True) -> None`、Scene `ChapterRecall`。

- [ ] **Step 1: `LONG_SCENES` 加入 `"ChapterRecall"`**

- [ ] **Step 2: 加入第三章程式**

import 補上 `Axes`、`Dot`、`Line`：

```python
from manim import Axes, Dot, Line
```

加入：

```python
# ------------------------------------------------------------------ chapter 3: minimum-class recall

ARM_X = {"random": 1.0, "entropy": 2.0, "margin": 3.0}


def _recall_axes(ctx: LongContext, y_max: float) -> Axes:
    axes = Axes(
        x_range=[0, 4, 1],
        y_range=[0, y_max, 0.1],
        x_length=6.0,
        y_length=4.0,
        tips=False,
        axis_config={"include_numbers": False, "stroke_color": ctx.style.colors["muted"]},
    )
    axes.x_axis.add_labels({ARM_X[arm]: _tick(ctx.short, arm) for arm in ARMS}, font_size=ctx.style.sizes["small"])
    labels = {}
    value = 0.1
    while value <= y_max + 1e-9:
        labels[round(value, 6)] = _tick(ctx.short, f"{value:.1f}")
        value = round(value + 0.1, 6)
    axes.y_axis.add_labels(labels, font_size=ctx.style.sizes["small"])
    return axes


def _recall_marks(ctx: LongContext, axes: Axes, data) -> tuple[VGroup, VGroup]:
    """Dots per (arm, seed) and a bracket per arm spanning min..max."""
    dots, brackets = VGroup(), VGroup()
    offsets = [-0.18, 0.0, 0.18]
    for arm in ARMS:
        values = data.arm_values_20("min_recall_20", arm)
        color = ctx.style.colors[arm]
        for offset, value in zip(offsets, values):
            dots.add(Dot(axes.c2p(ARM_X[arm] + offset, value), radius=0.09, color=color))
        x = ARM_X[arm] + 0.42
        low, high = axes.c2p(x, min(values)), axes.c2p(x, max(values))
        bracket = VGroup(
            Line(low, high, color=color, stroke_width=3),
            Line(low + LEFT * 0.08, low + RIGHT * 0.08, color=color, stroke_width=3),
            Line(high + LEFT * 0.08, high + RIGHT * 0.08, color=color, stroke_width=3),
        )
        brackets.add(bracket)
    return dots, brackets


def chapter_recall_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None:
    style = ctx.style
    a, b = ctx.pair.rule_a, ctx.pair.rule_b
    chapter_card(scene, ctx, "ch3_title", "ch3_sub")
    y_max = round(max(v for d in (a, b) for arm in ARMS for v in d.arm_values_20("min_recall_20", arm)) * 1.25 + 0.05, 1)
    axes = _recall_axes(ctx, y_max).to_edge(LEFT, buff=0.9).shift(UP * 0.2)
    y_label = text_long(ctx, "ch3_sub", "small", style.colors["muted"]).next_to(axes, UP, buff=0.25)
    scene.play(Create(axes), FadeIn(y_label), run_time=0.7)

    dots_a, brackets_a = _recall_marks(ctx, axes, a)
    head_a = text_long(ctx, "ch3_a", "label")
    ranges_a = text_long(ctx, "ch3_a_ranges", "small", style.colors["muted"])
    panel = VGroup(head_a, ranges_a).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    for mob in panel:
        if mob.width > 5.4:
            mob.scale_to_fit_width(5.4)
    panel.arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(RIGHT, buff=0.5).shift(UP * 1.2)
    scene.play(LaggedStart(*[FadeIn(dot, scale=0.5) for dot in dots_a], lag_ratio=0.05), run_time=1.0)
    scene.play(Create(brackets_a), FadeIn(panel), run_time=0.9)
    scene.wait(2.2)

    dots_b, brackets_b = _recall_marks(ctx, axes, b)
    head_b = text_long(ctx, "ch3_b", "label")
    note_b = text_long(ctx, "ch3_b_note", "small", style.colors["muted"])
    panel_b = VGroup(head_b, note_b).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    for mob in panel_b:
        if mob.width > 5.4:
            mob.scale_to_fit_width(5.4)
    panel_b.arrange(DOWN, aligned_edge=LEFT, buff=0.2).to_edge(RIGHT, buff=0.5).shift(DOWN * 1.0)
    scene.play(Transform(dots_a, dots_b), Transform(brackets_a, brackets_b), run_time=1.4)
    scene.play(FadeIn(head_b), run_time=0.5)
    scene.play(FadeIn(note_b), run_time=0.5)
    scene.wait(2.4)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.5)


class ChapterRecall(Scene):
    def construct(self) -> None:
        chapter_recall_segment(self, make_long_context(), fade_out=False)
```

- [ ] **Step 3: 冒煙測試與最後一幀**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest tests/test_scene_smoke.py -q
Remove-Item Env:VAL_EXPLAINER_RENDER
uv run python -m manim -ql -s --media_dir media val_explainer/scenes_long.py ChapterRecall
cd ..\..\..
```

Expected：`9 passed`。看最後一幀：三個 arm 各三個點與括號（規則 B 的位置），random 的括號與另外兩個 arm 的括號在 y 上重疊；右側兩個面板不重疊、不出界。若 `Transform(dots_a, dots_b)` 讓點的顏色錯亂，改成 `*[Transform(x, y) for x, y in zip(dots_a, dots_b)]`。

- [ ] **Step 4: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_long.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): chapter 3, the minimum-class recall negative result"
```

---

### Task 6: 結尾卡與 `ValLoopLong`、時長

**Files:**
- Modify: `docs/media/manim/val_explainer/scenes_long.py`
- Modify: `docs/media/manim/tests/test_scene_smoke.py`（`LONG_SCENES` 加 `"Closing"`、`"ValLoopLong"`）

**Interfaces:**
- Produces：`closing_segment(scene, ctx, fade_out=True) -> None`、Scene `Closing`、Scene `ValLoopLong`。

- [ ] **Step 1: `LONG_SCENES` 補齊**

```python
LONG_SCENES = ["ChapterRules", "ChapterReference", "ChapterRecall", "Closing", "ValLoopLong"]
```

- [ ] **Step 2: 加入結尾卡與完整場景**

```python
# ------------------------------------------------------------------ closing


def closing_segment(scene: Scene, ctx: LongContext, fade_out: bool = True) -> None:
    style = ctx.style
    lines = VGroup(
        text_long(ctx, "close_1", "label", style.colors["start"]),
        text_long(ctx, "close_2", "label"),
    ).arrange(DOWN, buff=0.35)
    path = text_long(ctx, "close_path", "small", style.colors["muted"]).next_to(lines, DOWN, buff=0.6)
    scene.play(LaggedStart(*[FadeIn(line, shift=UP * 0.15) for line in lines], lag_ratio=0.4), run_time=1.2)
    scene.play(FadeIn(path), run_time=0.4)
    scene.wait(3.0)
    if fade_out:
        scene.play(FadeOut(*scene.mobjects), run_time=0.6)


class Closing(Scene):
    def construct(self) -> None:
        closing_segment(self, make_long_context(), fade_out=False)


class ValLoopLong(Scene):
    def construct(self) -> None:
        ctx = make_long_context()
        title_segment(self, ctx.short)
        layout = build_pool_layout(ctx.short)
        pool_segment(self, ctx.short, layout)
        loop_segment(self, ctx.short, layout)
        curve_segment(self, ctx.short)
        chapter_rules_segment(self, ctx)
        chapter_reference_segment(self, ctx)
        chapter_recall_segment(self, ctx)
        closing_segment(self, ctx)
```

- [ ] **Step 3: 全部測試與低畫質完整渲染量時長**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
$env:PYTHONDONTWRITEBYTECODE = "1"; $env:VAL_EXPLAINER_RENDER = "1"; uv run pytest -q
Remove-Item Env:VAL_EXPLAINER_RENDER
uv run python -m manim -ql --media_dir media val_explainer/scenes_long.py ValLoopLong
ffprobe -v error -show_entries format=duration -of csv=p=0 media/videos/scenes_long/480p15/ValLoopLong.mp4
cd ..\..\..
```

Expected：測試全部通過（資料 17、文字 14、字型 3、冒煙 11）；時長 110 到 130 秒。超過 130 秒就先縮各章末尾的 `wait`（2.2／2.4／2.4 → 1.8）；低於 100 秒不必動。

- [ ] **Step 4: 抽 8 張幀看動態**

Run（在 `docs/media/manim`）：

```powershell
cd docs\media\manim
ffmpeg -v error -y -i media\videos\scenes_long\480p15\ValLoopLong.mp4 -vf "fps=1/15" media\long_frame_%02d.png
cd ..\..\..
```

用 Read 逐張看 `media/long_frame_01.png` 到 `08`：每章的章名卡、長條圖、兩個小曲線圖、參考基線虛線與帶狀區、recall 點圖、結尾卡；確認沒有出界、沒有方框字、沒有兩段殘留在同一畫面（每章結束有 FadeOut）。

- [ ] **Step 5: Commit**

```powershell
git add docs/media/manim/val_explainer/scenes_long.py docs/media/manim/tests/test_scene_smoke.py
git commit -m "feat(explainer): closing card; ValLoopLong runs the short segments and three chapters"
```

---

### Task 7: `render.ps1 -Scene`、README、高畫質渲染與 owner 審閱

**Files:**
- Modify: `docs/media/manim/render.ps1`
- Modify: `docs/media/manim/README.md`

- [ ] **Step 1: 改 `render.ps1`**

參數區改成：

```powershell
param(
    [switch]$Check,
    [ValidateSet('h', 'l')][string]$Quality = 'h',
    [ValidateSet('ValLoopShort', 'ValLoopLong')][string]$Scene = 'ValLoopShort',
    [string]$EvidenceMediaDir = '<evidence-root>\media'
)
```

變數區改成：

```powershell
$Project = $PSScriptRoot
$IsLong = ($Scene -eq 'ValLoopLong')
$SceneFile = Join-Path $Project $(if ($IsLong) { 'val_explainer\scenes_long.py' } else { 'val_explainer\scenes_short.py' })
$SceneModule = if ($IsLong) { 'scenes_long' } else { 'scenes_short' }
$OutputStem = if ($IsLong) { 'val-loop-long' } else { 'val-loop-short' }
$MediaDir = Join-Path $Project 'media'
$GifOut = Join-Path (Split-Path -Parent $Project) 'val-loop-short.gif'
$MaxGifBytes = 8MB
$MaxSeconds = if ($IsLong) { 130.0 } else { 32.0 }
$env:PYTHONDONTWRITEBYTECODE = '1'
```

`-Check` 與渲染那兩行的 `ValLoopShort` 改成 `$Scene`；mp4 路徑改成：

```powershell
$Mp4 = Join-Path $MediaDir "videos\$SceneModule\$folder\$Scene.mp4"
```

時長檢查之後、GIF 之前加：

```powershell
if ($IsLong) {
    if (-not (Test-Path -LiteralPath $EvidenceMediaDir)) { New-Item -ItemType Directory -Path $EvidenceMediaDir | Out-Null }
    $stamp = (Get-Date).ToUniversalTime().ToString('yyyyMMddTHHmmZ')
    $dest = Join-Path $EvidenceMediaDir "$OutputStem-$stamp.mp4"
    Copy-Item -LiteralPath $Mp4 -Destination $dest
    Write-Host "mp4  -> $dest"
    exit 0
}
```

短版的 mp4 複製那行改用 `$OutputStem`：

```powershell
Copy-Item -LiteralPath $Mp4 -Destination (Join-Path $EvidenceMediaDir "$OutputStem-$stamp.mp4")
Write-Host "mp4  -> $EvidenceMediaDir\$OutputStem-$stamp.mp4"
```

- [ ] **Step 2: README 加長版段落**

在 `docs/media/manim/README.md` 的「渲染（repo 根目錄）」程式碼區塊之後加：

```markdown
長版（作品集頁面用，約 2 分鐘，只出 1080p60 mp4、不做 GIF、不進 git）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Scene ValLoopLong -Check
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Scene ValLoopLong
```

長版 = 短版四段 ＋ 三章（訓練長度規則、全標籤參考基線、最低類別 recall 的負面結果）＋ 結尾卡；規格在 [../../superpowers/specs/2026-09-11-val-explainer-manim-long-design.md](../../superpowers/specs/2026-09-11-val-explainer-manim-long-design.md)。單章檢查：`uv run python -m manim -ql -s --media_dir media val_explainer/scenes_long.py <ChapterRules|ChapterReference|ChapterRecall|Closing>`。句子裡的主張（3/3、範圍互不重疊或重疊、欠訓）在 `render_copy_long` 內對資料驗證，資料變了會拒絕渲染而不是講錯。
```

- [ ] **Step 3: `-Check` 兩種場景、短版低畫質回歸**

Run（repo 根目錄）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Check
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Scene ValLoopLong -Check
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Quality l
```

Expected：三條都 exit 0；第三條會覆寫 `docs/media/val-loop-short.gif`，之後用 `git checkout -- docs/media/val-loop-short.gif` 還原（短版 GIF 不變）。

- [ ] **Step 4: 高畫質渲染長版**

Run（repo 根目錄，約 10 到 20 分鐘）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Scene ValLoopLong
```

Expected：`duration 1xx.x s`、`mp4 -> ...\val-loop-long-<時間戳>.mp4`。

- [ ] **Step 5: 自己抽幀檢查，再請 owner 看**

```powershell
ffmpeg -v error -y -i "<evidence-root>\media\val-loop-long-<時間戳>.mp4" -vf "fps=1/12" docs\media\manim\media\hq_frame_%02d.png
```

逐張 Read；沒問題就用 SendUserFile 把 mp4 送給 owner（附時長與大小），**等 owner 回覆**。

- [ ] **Step 6: Commit**

```powershell
git status --short
git add docs/media/manim/render.ps1 docs/media/manim/README.md
git commit -m "feat(explainer): render the long explainer with -Scene ValLoopLong"
```

確認 `git status` 沒有 `docs/media/val-loop-short.gif` 的修改（Step 3 已還原）與 `media/` 產物。push 由 owner 決定；回報 commit 雜湊、mp4 路徑、時長。

---

## Self-review

- **Spec coverage**：§0 用途（Task 6 的 `ValLoopLong`、Task 7 的 mp4）；§1 三章與結尾卡文字（Task 2 的 `COPY_LONG`；Task 3、4、5、6 的畫面）；§2 資料綁定每一列（Task 1：`_steps_and_epochs`、`_mean_curve`、`_references`、`ratio_20`、`min_recall_20`、`load_rule_pair`、`range_text`）；§3 檔案（Task 1 到 7）；§4 視覺（Task 3 長條與 `Transform`、Task 4 虛線與帶狀 `Polygon`、Task 5 點與括號、章名卡 2 秒、每章 `FadeOut`）；§5 渲染（Task 7 `-Scene`、130 秒門檻、不做 GIF、mp4 命名）；§6 測試與人工檢查（Task 1、2 的 pytest；Task 3 到 6 的冒煙與抽幀；Task 7 的 owner 審閱）；§7 邊界（Global Constraints；短版不改）；§8 完成定義（Task 6 全測、Task 7 一條指令與審閱）。
- **Placeholder scan**：無 TBD／TODO；程式步驟皆有完整程式碼。`<時間戳>` 是執行時由腳本印出的值，不是佔位。
- **Type consistency**：`LongContext.copy` 由 `render_copy_long` 產生，鍵名與 `COPY_LONG` 及 `bar_*_<key>` 一致；`arm_values_20(table, arm)` 在 Task 1 定義、Task 2 與 5 使用；`_axes(ctx.short, y_max)`、`_line(axes, points, color, width)`、`_tick(ctx.short, label)` 與短版簽名一致；`Reference.map50_95` 在 Task 1、2、4 一致。
