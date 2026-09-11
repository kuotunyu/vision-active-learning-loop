# Manim 說明動畫

README 用的 30 秒短版（`ValLoopShort`）。只做說明，不產生任何證據；所有數字由 `val_explainer/data.py` 從 `docs/results/` 的 summary 與各 seed 的實驗收據讀出。畫面文字凍結在 `val_explainer/copy.py`，規格在 [../../superpowers/specs/2026-09-11-val-explainer-manim-short-design.md](../../superpowers/specs/2026-09-11-val-explainer-manim-short-design.md)。

獨立環境（不碰主 `.venv`）：

```powershell
uv sync --project docs/media/manim
```

測試（在 `docs/media/manim`）：

```powershell
uv run pytest -q                                     # 資料綁定、文字守門、字型
$env:VAL_EXPLAINER_RENDER = "1"; uv run pytest -q    # 加上六個場景的 manim --dry_run 冒煙
```

渲染（repo 根目錄）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Check   # 只 dry run
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1          # 1080p60 mp4 -> GIF
```

長版（作品集頁面用，約 2 分鐘，只出 1080p60 mp4、不做 GIF、不進 git）：

```powershell
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Scene ValLoopLong -Check
powershell -ExecutionPolicy Bypass -File docs\media\manim\render.ps1 -Scene ValLoopLong
```

長版 = 短版四段 ＋ 三章（訓練長度規則、全標籤參考基線、最低類別 recall 的負面結果）＋ 結尾卡；規格在 [../../superpowers/specs/2026-09-11-val-explainer-manim-long-design.md](../../superpowers/specs/2026-09-11-val-explainer-manim-long-design.md)。單章檢查：`uv run python -m manim -ql -s --media_dir media val_explainer/scenes_long.py <ChapterRules|ChapterReference|ChapterRecall|Closing>`。句子裡的主張（3/3、範圍互不重疊或重疊、欠訓）在 `render_copy_long` 內對資料驗證，資料變了會拒絕渲染而不是講錯。

輸出：`docs/media/val-loop-short.gif`（進 git，≤ 8 MB）；mp4 複製到 `<evidence-root>\media\`（不進 git）。單段檢查用 `uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py <TitleSegment|PoolSegment|LoopSegment|CurveSegment|OutroSegment>`，最後一幀輸出到 `media/images/scenes_short/`。

字型：Microsoft JhengHei（備援 Noto Sans TC）。沒有 LaTeX 也能渲染：文字用 Pango `Text`，計數器的數字用 `DecimalNumber(mob_class=Text 子類別)`。
