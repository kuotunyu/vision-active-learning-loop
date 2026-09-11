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

輸出：`docs/media/val-loop-short.gif`（進 git，≤ 8 MB）；mp4 複製到 `<evidence-root>\media\`（不進 git）。單段檢查用 `uv run python -m manim -ql -s --media_dir media val_explainer/scenes_short.py <TitleSegment|PoolSegment|LoopSegment|CurveSegment|OutroSegment>`，最後一幀輸出到 `media/images/scenes_short/`。

字型：Microsoft JhengHei（備援 Noto Sans TC）。沒有 LaTeX 也能渲染：文字用 Pango `Text`，計數器的數字用 `DecimalNumber(mob_class=Text 子類別)`。
