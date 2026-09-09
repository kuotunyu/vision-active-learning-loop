# vision-active-learning-loop

RT-DETR（`PekingU/rtdetr_r18vd`）在 RDD 道路損壞資料上的主動學習實驗基礎建設。
目標是比較 random / entropy / margin / core-set / hybrid 五種選樣策略在固定預算下的偵測表現。

**現況（2026-09-09）：三個登記 seed（17、29、43）各跑完一輪完整的「基線 → 選樣 → 加入標註 → 重訓 → 同測試集比較」**，共 30 個 fit，在 RDD2022 Czech 子集與 RTX 4090 上完成。
entropy 與 margin 的配對 nAUBC 差對 random **三個 seed 都是正的**；20% 預算時最低類別 recall 三個 arm 區間不重疊（margin 是 random 的 2.6 到 4.7 倍）。
結果、能說與不能說的界線見 [docs/results/2026-09-09-lite-czech-three-seeds.md](docs/results/2026-09-09-lite-czech-three-seeds.md)。
原 Wave 0 分支停在模型契約與單步訓練可行性；復活工作依 v0.2-lite 協定進行。
完整評估見 [docs/status/2026-09-09-revival-assessment.md](docs/status/2026-09-09-revival-assessment.md)，
已核可的降規協定見 [docs/superpowers/specs/2026-09-09-val-v0.2-lite-protocol.md](docs/superpowers/specs/2026-09-09-val-v0.2-lite-protocol.md)。

## 分支與位置

| 項目 | 位置 |
|---|---|
| `main` | `8217a93`，只有設計規格與 8 個 wave 的計畫文件 |
| 主要開發分支 `codex/wave0-model-contract` | `10d866c`，147 個 commit，已推到私人 GitHub |
| 復活分支 `codex/revival-entry-20260909` | 由 `10d866c` 分出。加入 README、現況文件、v0.2-lite 協定與 `lite/` 模組；不改動任何既有 Wave 0 程式、測試、腳本或證據 |
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

沒有的東西：RDD 資料下載與 manifest、多輪訓練器、pycocotools 評估、預算曲線。

v0.2-lite 復活進度（`src/vision_active_learning_loop/lite/`）：

| 模組 | 狀態 |
|---|---|
| `acquisition.py` | 已完成。entropy / margin 逐 query 不確定度、影像分數（前 20 個 query 平均）、random 與 shared-start 排序、預算選取；28 個 CPU 測試 |
| `manifest.py` | 已完成。VOC 解析、item_id、完全重複收攏、凍結雜湊切分、覆蓋審核、公開視圖，以及 `val lite manifest` 命令；27 + 8 個 CPU 測試 |
| `dataset.py` | 已完成。影像索引、樣本載入、確定性翻轉與色彩抖動、COCO 標註載荷、批次前處理、畫布幾何反算；23 個 CPU 測試 |
| `train.py` | 已完成。1,000 步固定迴圈、每 epoch 重洗取樣、warm-up 加 cosine 排程、梯度裁切、fit 收據；20 個 CPU 測試 |
| `evaluate.py` | 已完成。原始 query 轉偵測（前 100、無 NMS 無門檻）、pycocotools mAP 與四類 recall、nAUBC；13 個 CPU 測試 |
| `loop.py` | 已完成。`fit_once`（載入 pinned 快照、四類 reset、增強批次、固定步迴圈、checkpoint 與收據的無覆寫發布）、`evaluate_checkpoint`、`shared_start_items`，以及 `val lite baseline` 命令 |
| `rounds.py` | 已完成。精確預算 `ceil(p·N)`、每輪選樣（random 凍結序的下一段、uncertainty 依分數取前 k）、ledger、策略只看得到的無標籤列；13 個 CPU 測試 |
| `experiment.py` | 已完成。整體排程（共享起點 → 三 arm × 三輪 → 全部 checkpoint 一次評估）、池打分、`metrics.csv`、`curve.svg`、nAUBC 與對 random 的差、experiment receipt，以及 `val lite run` 命令；10 個排程測試用可注入的 fitter／scorer／evaluator 驗證巢狀預算、標籤隔離與產出檔 |
| `summary.py` | 已完成。`val lite summarize`：跨 seed 彙總（每 seed 的 nAUBC、對 random 的配對差、平均與中位數、正負號一致性、各預算平均 mAP、20% 時最低類別 recall），輸出 `summary.json` 與 `summary.csv`；7 個 CPU 測試 |
| `gate.py` | 已完成。`val lite gate`：§8 門檻（基線 loss 前 10% 中位數 > 後 10% 中位數；CUDA 時 allowlist warning 恰為 9），輸出 `PASS/FAIL {...}`，退出碼 0／2／3；7 個 CPU 測試 |

設 `VAL_LITE_SNAPSHOT` 可另跑用真 RT-DETR 在 CPU 走完整路徑的整合測試（fit、評估、基線命令、完整實驗；已通過）。`scripts/run_lite_seed17.ps1` 是把以上串起來的唯一啟動點，有 Windows PowerShell 5.1 解析檢查與 dry-run 測試。

真實資料：RDD2022 Czech train 子樹已於 2026-09-09 取得並建好 manifest（2,829 張、1,745 框、test 574／pool 2,255），來源、雜湊與計數見 [docs/data-card.md](docs/data-card.md)。
三個 seed 的結果檔在 [docs/results/](docs/results/)：每個 seed 一個目錄，加上跨 seed 的 [summary-3seeds/](docs/results/summary-3seeds/)。

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

## 跑 GPU 實驗（一條指令）

開任何一個 PowerShell（不需要 `cd`、不需要啟用 venv、不需要改 execution policy）。下面用絕對路徑呼叫，從任何目錄貼上都一樣。

先只做檢查，不啟動任何東西：

```powershell
powershell -ExecutionPolicy Bypass -File "<repo>\.worktrees\wave0-model-contract\scripts\run_lite_seed17.ps1" -DryRun
```

每一行都是 `ok` 才往下。正式執行（GPU 被別的工作占用時會每 30 秒等一次，最多 4 小時）：

```powershell
powershell -ExecutionPolicy Bypass -File "<repo>\.worktrees\wave0-model-contract\scripts\run_lite_seed17.ps1" -WaitForGpu
```

換 seed 就在後面加 `-Seed 29` 或 `-Seed 43`。腳本檔名固定不變，seed 由參數決定，輸出目錄與紀錄檔會自動帶上該 seed。

腳本會依序：共享 2% 基線 fit 與評估 → §8 門檻（loss 下降、9 個 allowlist warning）→ 完整實驗（3 arm × 3 輪，共 10 個 fit）。任一步失敗就停，不重試、不覆寫；`RUNNING.lock` 防止同時跑兩份。全部輸出與逐字紀錄在 `<evidence-root>\lite\`：`lite-czech-s17-<時間戳>\{metrics.csv, curve.svg, ledger-*.json, experiment-receipt.json}` 與 `run-lite-seed17-<時間戳>.log`。

失敗時看兩個地方：逐字紀錄 `run-lite-seed17-<時間戳>.log`（val 的 stdout 與 stderr 都在裡面），以及實驗目錄下的 `failure.json`（基線失敗時寫入，含完整診斷）。2026-09-09 第一次 GPU 基線就是被 warning 契約擋下（11 個而非 9 個），原因與修正記在協定 §3。

不要做的事：不要同時開第二個視窗再跑一次；不要在 GPU 有別的工作時去掉 `-WaitForGpu`（腳本會直接以代碼 4 退出，不會硬擠）。

## 重要邊界

- 原 8-wave 協定要求 Wave 0 `PASS` 才能碰資料；Wave 0 至今沒有 `PASS`。復活評估的結論是這個前提可以重新界定，不必先完成 A11。
- 證據根目錄已搬遷，A11 啟動器凍結的 64,306 檔歷史清單已無法重現，任何 A11 重跑都會在 preflight 停下。
- 本 repo 不放 RDD 影像、標註、權重、checkpoint。
