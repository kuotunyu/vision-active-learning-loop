# 設計：Manim 短版說明動畫（主動學習迴圈與三 seed 配對差）

狀態：2026-09-11 與 owner 逐段確認後寫定。範圍只有 README 用的短版；長版另立規格。

## 0. 目的與觀眾

- 觀眾：打開 GitHub repo 的人。目標是在 30 秒內看懂兩件事：這個專案跑的「主動學習迴圈」長什麼樣；「三個 seed 的配對 nAUBC 差都為正」是什麼意思。
- 形式：約 30 秒、16:9、無旁白、可循環的 GIF，放在 README 現況段下方。
- 語言：畫面文字用繁體中文；指標與 arm 名稱（mAP50–95、nAUBC、random／entropy／margin）維持英文。
- 動畫只做說明，不產生任何證據。現有的 `curve.svg`、`mean-curve.svg` 仍由 `val lite summarize` 產生，不被取代。

## 1. 分鏡與畫面文字（凍結）

畫面文字集中在 `copy.py`，就是下表這些句子；改句子等於改本規格。

| 時間 | 畫面 | 畫面文字 |
|---|---|---|
| 0–3 s | 標題卡 | 「主動學習迴圈｜RDD2022 Czech × RT-DETR r18」；小字「v0.2.1・固定 epoch 規則・3 個 seed」 |
| 3–8 s | 2,255 個小方塊排成 pool；右側獨立框是 test；46 個方塊亮起 | 「未標註 pool 2,255 張」「test 574 張：凍結，不參與選樣與訓練」「共享起點 2%＝46 張」 |
| 8–17 s | 從同一個 46 分成三條 lane（random／entropy／margin）。一輪完整演出：模型對 pool 打分（entropy／margin 的方塊依不確定度深淺著色，random 不著色）→ 前 k 個方塊飛進已標註集合，計數 46→113 →「重訓」→ 到 test「評估 mAP50-95」。之後快轉 113→226→451 | 「同一起點、同一 recipe、同一 test；只有選圖規則不同」 |
| 17–27 s | 座標軸：x＝預算 2／5／10／20%，y＝mAP50-95。先畫 seed 17 的 random 與 margin 曲線，兩線之間著色；再疊上 seed 29、43 的細線 | 「配對差（margin − random）」旁邊列三個 seed 的 nAUBC 差（從 summary.json 讀，格式 `+0.0019`）；「3 個 seed 都為正（3/3）」；小字「三個 seed 的最大最小是範圍，不是信賴區間」 |
| 27–31 s | 結尾卡 | 「固定步數與固定 epoch 兩種規則下都是 3/3（entropy 亦同）」「20% 預算約達全標籤參考基線的一半」「不宣稱降低標註成本；同機重播並非位元相同」；小字「docs/results/2026-09-11-v0.2.1-training-rule.md」 |

取捨：

- 曲線段只畫 margin 對 random。同時畫兩塊著色區在 10 秒內會糊掉；entropy 的 3/3 由結尾卡一句帶過。
- 用規則 B（v0.2.1）的數字，因為它是現況。seed 17 的 margin 差最小（+0.0019）也照畫，不挑 seed。
- 「約達一半」對應 summary 的 20% 佔參考基線比例（entropy 0.53–0.63、margin 0.49–0.57）；這句是定性描述，數字本身在結果文件。

## 2. 檔案配置

```
docs/media/manim/
  pyproject.toml          manim==0.21.0，requires-python ==3.12.11，獨立 .venv（uv run --project）
  .gitignore              .venv/ media/ __pycache__/ .pytest_cache/
  README.md               渲染、檢查、輸出位置
  val_explainer/
    __init__.py
    data.py               讀 summary.json 與各 seed 的 experiment-receipt.json 組成 dataclass；缺檔或缺欄位拋 ExplainerDataError
    copy.py               畫面文字 dict（§1 的句子）
    style.py              字型、顏色、字級、方塊尺寸
    scenes_short.py       ValLoopShort(Scene)；construct 依序呼叫 title / pool / loop / curve / outro 五個函式
  tests/
    test_data.py
    test_copy.py
    test_scene_smoke.py   標記 slow，設 VAL_EXPLAINER_RENDER=1 才跑
  render.ps1              渲染 mp4 → 轉 GIF → 大小門檻 → 複製 mp4 到私有證據目錄；-Check 只跑 dry run
docs/media/val-loop-short.gif   唯一進 git 的渲染產物
```

主環境不動：不改根目錄的 `pyproject.toml`、`uv.lock`，不在主 `.venv` 裝 manim。Manim 的環境由 `uv run --project docs/media/manim` 建在 `docs/media/manim/.venv`，Python 用 uv 已管理的 3.12.11。

## 3. 資料綁定

原則：動畫裡沒有任何手打的數字。

| 數字 | 來源 |
|---|---|
| pool 2,255、test 574、預算 46／113／226／451 | `docs/results/lite-czech-ep18-s17-20260911T0546Z/experiment-receipt.json` 的 `normative.pool_size`、`test_image_count`、`budgets` |
| 三個 seed 的 nAUBC 差（margin、entropy）、seeds、`claim_rule` | `docs/results/summary-ep18-3seeds/summary.json` 的 `per_seed[*].delta_vs_random`、`seeds` |
| 每 seed 每 arm 的四個曲線點（2%／5%／10%／20% 的 mAP50–95） | `summary.json` 的 `per_seed[*].experiment_id` 對應的 `docs/results/<experiment_id>/experiment-receipt.json` 的 `normative.fits[*]`（`arm`、`budget_fraction`、`metrics.mAP50_95`）；2% 用 `arm == "shared"` 那筆，三個 arm 共用 |

- `data.py` 只提供一個入口 `load_explainer_data(results_root: Path, summary_dir: str) -> ExplainerData`。`summary_dir` 預設 `summary-ep18-3seeds`；長版要畫規則 A 時傳 `summary-3seeds-with-reference`。
- `ExplainerData` 欄位：`pool_size`、`test_size`、`budgets: dict[str, int]`、`seeds: list[int]`、`delta: dict[str, dict[int, float]]`（arm → seed → 值）、`curves: dict[int, dict[str, list[tuple[float, float]]]]`（seed → arm → [(fraction, mAP)]）。
- 任何檔案不存在、JSON 缺鍵、某 seed 的收據少於 10 個 fit，一律拋 `ExplainerDataError` 並中止；沒有預設值。`metrics.csv` 不讀。
- 曲線段顯示的 `+0.0019` 這類字串由 `f"{value:+.4f}"` 產生。

## 4. 視覺與字型

- 字型 `Microsoft JhengHei`（系統 `msjh.ttc`），備援 `Noto Sans TC`；`style.py` 啟動時用 `manimpango.list_fonts()` 確認，兩者皆無則拋錯。不用 `MathTex`／`Tex`（本機沒有 LaTeX）。
- 顏色用 Okabe-Ito：random `#999999`、entropy `#0072B2`、margin `#E69F00`；背景深色（Manim 預設）。
- pool 用 2,255 個小方塊排成矩形網格（約 60 × 38），test 用同樣的方塊排在右側獨立框。影像一律用抽象方塊，不放 RDD2022 影像。
- 不確定度著色只在 entropy／margin lane 出現；random lane 的方塊維持同一灰色，表示「不看分數」。

## 5. 渲染與輸出

- 主檔：`uv run --project docs/media/manim manim -qh --media_dir docs/media/manim/media val_explainer/scenes_short.py ValLoopShort`，得到 1080p mp4。
- GIF：`render.ps1` 用 ffmpeg 兩段式（`palettegen` → `paletteuse`）從 mp4 轉出 960×540、12 fps 的 GIF；大小超過 8 MB 就改 800×450、10 fps 再轉一次；仍超過就報錯、不覆寫既有 GIF。
- mp4 複製到 `<evidence-root>\media\`（不進 git）；GIF 寫到 `docs/media/val-loop-short.gif`，重渲染覆寫同名檔。
- `render.ps1 -Check`：只跑 `manim --dry_run -ql`，不寫任何檔。
- README：現況段下方加一行 `![主動學習迴圈（30 秒）](docs/media/val-loop-short.gif)` 與一句說明，連到結果文件。

## 6. 測試與檢查

- `tests/test_data.py`：用 repo 內的真實檔案。`pool_size == 2255`、`test_size == 574`、預算等於收據的 `budgets`；三個 seed 的 delta 等於 `summary.json`；每 seed 每 arm 恰四個點且 fraction 遞增；把 `results_root` 指到空目錄時拋 `ExplainerDataError`。
- `tests/test_copy.py`：每句非空、每行不超過 `style.MAX_CHARS_PER_LINE`；禁詞守門：句子含「降低標註成本」「信賴區間」「deterministic」「可重現」時，同一句必須含「不宣稱」「不是」「並非」之一，否則失敗。
- `tests/test_scene_smoke.py`：以 subprocess 執行 `manim --dry_run -ql`，回傳碼 0；標記 slow，環境變數 `VAL_EXPLAINER_RENDER=1` 才跑。
- 人工檢查：先 `-ql` 渲染並抽關鍵幀（標題卡、pool 亮起、lane 分岔、著色區、結尾卡）確認中文字型正確、版面不溢出、著色區在正確的兩條線之間；再 `-qh`。GIF 由 owner 看過才進 README。

## 7. 邊界

- 不動主環境、`src/`、`tests/lite`、`scripts/`；證據目錄與 `docs/results/` 只讀。
- 不宣稱降低標註成本、不宣稱 deterministic 或跨機可重現、三個 seed 的最大最小只叫「範圍」。畫面文字守門測試就是這三條。
- 不用 RDD2022 影像；不放任何 checkpoint 或資料集內容。
- 長版（1–3 分鐘、含固定步數 vs 固定 epoch 與「還不能宣稱什麼」）不在本規格；本規格只要求五個畫面函式各自接收 `(data, copy, style)`，之後可重排。
- 產出 commit 在 `main`；push 由 owner 決定。

## 8. 完成的定義

1. `uv run --project docs/media/manim pytest docs/media/manim/tests -q` 全部通過（slow 測試除外）。
2. `render.ps1` 從乾淨狀態一條指令產出 GIF 與 mp4，GIF ≤ 8 MB。
3. owner 看過 GIF 並同意放進 README。
4. README 一行嵌入與說明；spec、程式、GIF、README 同一個或連續的 commit。
