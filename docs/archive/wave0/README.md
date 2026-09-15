# Wave 0 封存

原 8-wave 協定的設計與 Wave 0 工程紀錄，只供溯源，不是目前的工作佇列。目前的研究見 repo 根目錄的 README。

## 結論

| 階段 | 結果 |
|---|---|
| A2：四類 reset，5 次 campaign | NORMATIVE_FAIL：要求 CUDA backward 位元一致，結構上無法達成 |
| A6：Math-only SDPA，2 次 campaign | 5 個 stage 個別 PASS；`gate wave0` 彙總 FAIL，數值重播超出 A3 界限 |
| A7：歸因診斷，10 次 campaign | ATTRIBUTED：重播差異來自 `grid_sampler_2d_backward_cuda` |
| A11：統計重播，6 次 campaign | 全部在彙總前失敗，沒有產生 calibration receipt |

Wave 0 從未 PASS。2026-09-09 的復活評估（`docs/decisions/2026-09-09-revival-assessment.md`）決定不以 A11 為前提，改依 lite 協定進行研究。

## 內容

| 檔案 | 內容 |
|---|---|
| `2026-08-23-vision-active-learning-loop-design.md` | 原 8-wave 正式設計規格，標頭記錄各階段最終狀態 |
| `plans/` | 計畫索引與 Wave 0–7 八份計畫 |
| `runbook-a2.md` | Wave 0 A2 重播 runbook |
| `environment-boundary.md` | Wave 0 的 Linux OCI／WSL2 執行邊界 |
| `2026-09-09-a11-offline-pair-metrics.py`、`.json` | 以既有 12 個 A11 GPU 副本在 CPU 重算 13 個配對指標；不是 A11 receipt |

## 已移除的文件

2026-09-15 整理時移除 A2–A11 的 39 份實作與復原計畫、28 份復原設計，以及 lite 的 3 份已完成實作清單與 v0.2.1 交接文件。整理前的完整內容保留在 tag `pre-docs-reorg-2026-09-15`：

```powershell
git show pre-docs-reorg-2026-09-15:docs/superpowers/plans/<檔名>
git checkout pre-docs-reorg-2026-09-15 -- docs/superpowers
```

## 程式碼

Wave 0 的程式、測試與啟動器仍在 `src/`、`tests/`、`scripts/`，因為 lite 重用其中的 `artifacts`、`models`、`probes`、`training` 模組，而 `probes` 又依賴 `gates` 與 `environment`。`scripts/run_wave0_*.ps1` 與 `scripts/start_wave0_a7.ps1` 綁定的 source commit 在 2026-09-15 歷史改寫後已不存在，引用的文件路徑也已搬移；這些啟動器不能再執行，只作為紀錄保留。
