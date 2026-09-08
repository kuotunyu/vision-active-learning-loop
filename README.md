# vision-active-learning-loop

RT-DETR（`PekingU/rtdetr_r18vd`）在 RDD 道路損壞資料上的主動學習實驗基礎建設。
目標是比較 random / entropy / margin / core-set / hybrid 五種選樣策略在固定預算下的偵測表現。

**現況（2026-09-09）：尚未有任何一輪「基線 → 選樣 → 加入標註 → 重訓 → 同測試集比較」。**
目前程式碼全部屬於 Wave 0（模型契約與單步訓練可行性），資料、選樣、多輪訓練與評估（Wave 1–3）只有計畫文件。
完整評估見 [docs/status/2026-09-09-revival-assessment.md](docs/status/2026-09-09-revival-assessment.md)。

## 分支與位置

| 項目 | 位置 |
|---|---|
| `main` | `8217a93`，只有設計規格與 8 個 wave 的計畫文件 |
| 主要開發分支 `codex/wave0-model-contract` | `10d866c`，147 個 commit，已推到私人 GitHub |
| 本評估分支 `codex/revival-entry-20260909` | 由 `10d866c` 分出，只加入 README 與現況文件，不改動程式 |
| GPU 執行證據（不進 Git） | `<evidence-root>\wave0`（2026-09-02 由 `D:\vision-active-learning-loop-artifacts` 搬入） |
| 設計規格 | [docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md](docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md) |
| 計畫索引 | [docs/superpowers/plans/2026-08-23-vision-active-learning-loop-plan-index.md](docs/superpowers/plans/2026-08-23-vision-active-learning-loop-plan-index.md) |

## 程式碼裡有什麼

`val` CLI（`src/vision_active_learning_loop/`）目前有 8 個命令，全部是 Wave 0：

| 命令 | 作用 | 實際在 GPU 跑過 |
|---|---|---|
| `environment check` | 比對 Python / torch / CUDA / GPU 與 `configs/environment/wave0.yaml` | 是 |
| `assets verify` | 下載並驗證 RT-DETR 與 DINOv2 的 revision、safetensors SHA-256、授權 | 是 |
| `probe model-contract` | 用兩張合成影像觀察 RT-DETR 的 300 query / 4 類輸出契約 | 是 |
| `probe training-feasibility` | 一個 BF16 訓練步、AdamW 更新、checkpoint 存讀驗證 | 是（多次；最後一次 12 個副本） |
| `gate wave0` | 彙總上述收據並做同機重播比對 | 是，結果 `FAIL`（數值重播超出 A3 界限） |
| `diagnose grid-sample-attribution` | 把重播差異歸因到 `grid_sampler_2d_backward_cuda` | 是，結果 `ATTRIBUTED` |
| `gate statistical-replay calibrate` / `validate` | A11 統計重播包絡（12+12 副本） | 否；6 次啟動皆在彙總前失敗 |

沒有的東西：RDD 資料下載與 manifest、去重與切分、五種選樣策略、多 epoch 訓練器、pycocotools 評估、預算曲線。

## 在本機（CPU）檢查

```powershell
cd .worktrees\wave0-model-contract
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

- `.venv` 已是 Python 3.12.11 + torch 2.12.0+cu126 + transformers 5.15.0，與鎖定版本一致。
- 測試不啟動 Docker、不做 GPU 運算，但 checkpoint 載入器會讀取 CUDA RNG 狀態，因此需要本機看得到一顆 GPU（不要設 `CUDA_VISIBLE_DEVICES=""`）。
- 測試收集約需 4 分鐘（啟動器測試會解析大型 PowerShell 腳本）。
- 2026-09-09 實測：773 passed、569 failed、14 skipped。569 個失敗全部是兩個啟動器測試檔找不到 `pwsh`（PowerShell 7 目前不在 PATH），Python 層測試全數通過。
- 用既有 12 個 GPU 副本在 CPU 上重算 A11 的 13 個配對指標，全部落在實務上限內；數字與腳本在 `docs/status/`。

## 重要邊界

- 原 8-wave 協定要求 Wave 0 `PASS` 才能碰資料；Wave 0 至今沒有 `PASS`。復活評估的結論是這個前提可以重新界定，不必先完成 A11。
- 證據根目錄已搬遷，A11 啟動器凍結的 64,306 檔歷史清單已無法重現，任何 A11 重跑都會在 preflight 停下。
- 本 repo 不放 RDD 影像、標註、權重、checkpoint。
