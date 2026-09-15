# 2026-09-09 復活評估與現況入口

範圍：只讀既有程式、測試、文件與外部證據；做低負載 CPU 診斷；不啟動 GPU 工作、Docker 建置、付費服務或公開發布；不重啟 A11 救援。
基準：`main` = `8217a93`；`codex/wave0-model-contract` = `10d866c`（147 個 commit，與 `origin` 同步）。

## 1. 四個問題的答案

### Q1 是否已具備一輪「基線 → 選樣 → 加入標註 → 重訓 → 同測試集比較」？

**沒有。** 五個環節沒有任何一個存在：

| 環節 | 需要的元件 | 目前狀態 |
|---|---|---|
| 基線 | 資料 manifest、多 epoch 訓練器、固定測試切分 | 未實作（Wave 1/2 計畫） |
| 選樣 | 五種策略（§7）、DINOv2 embedding | 未實作（Wave 3 計畫）；`src/` 內沒有 entropy / margin / core-set 任何程式 |
| 加入標註 | 模擬 oracle、queue ledger | 未實作（Wave 3 計畫） |
| 重訓 | 從同一預訓練底重訓 | 只有單步訓練探針（`probe training-feasibility`，`epoch=0, step=1`） |
| 同測試集比較 | pycocotools mAP、預算曲線 | 未實作（Wave 6 計畫）；`pycocotools` 只在鎖檔中 |

Wave 0 的目標是「在碰資料之前證明模型契約與單步訓練可行」；整個開發分支從 8/23 到 8/31 都停在這一層。

### Q2 哪些只有契約／fixture，哪些真的跑過？

**真的在 RTX 4090 + Docker 上跑過，證據在磁碟上：**

| 元件 | 證據 | 最終結果 |
|---|---|---|
| `environment check` | 每次 campaign 的 `environment.json` | PASS |
| `assets verify`（HF 下載、revision、SHA-256、授權） | `receipts/model-assets.json` 等 | PASS |
| `probe model-contract`（兩張合成影像） | 每次 campaign 的 `model-contract.json` | PASS（A2 之後含四類 reset） |
| `probe training-feasibility`（一個 BF16 步 + checkpoint 往返） | A2–A6 各 attempt；A11 `steven003`/`steven006` 各 12 副本 | 單一副本全部 PASS |
| `gate wave0` 彙總 | `a6-runs/wave0-a6-20260825T125943018Z/gate/wave0-gate-receipt.json`（唯一一份 gate receipt） | **FAIL**：離散狀態完全一致，但數值重播超出 A3 界限 |
| `diagnose grid-sample-attribution` | `a7-runs/wave0-a7-20260827T034653088Z/audit/27-aggregate.json` | ATTRIBUTED：差異來自 `grid_sampler_2d_backward_cuda` 的 atomicAdd |

**只有契約／CPU 測試，從未產生正式 receipt：**

- `gate statistical-replay calibrate` / `validate`（A11）：程式與 1,346 行測試存在，但 6 次啟動皆在彙總前失敗，沒有任何 `statistical-replay-calibration.json`。
- `scripts/run_wave0_a11.ps1`（3,199 行）與 `scripts/start_wave0_a7.ps1`（3,116 行）：靠 adapter 測試驗證，真實執行紀錄就是上面的失敗清單。
- Wave 0 「兩次乾淨環境重現 + gate PASS」的原始出口條件：從未達成。

**連契約都沒有：** Wave 1–7 的全部程式。`main` 與開發分支都只有計畫文件。

### Q3 原 A11 阻塞是否仍是完成核心實驗的必要前提？

**不是。** 理由分三層：

1. **A11 只是協定上的前提，不是技術上的前提。** A11 要證明的是「同機、同 seed 的單步訓練在統計包絡內可重播」。它不影響能不能寫出資料管線、選樣策略、訓練迴圈與評估；它只影響能不能在原協定下宣稱「Wave 0 PASS」。
2. **A11 現在已經雙重過期。** 每次 A11 嘗試都綁定一個 source commit、一個 Docker 映像與一份 64,306 檔的歷史清單摘要。證據根目錄在 9/2 搬到 `<private-evidence>\...` 後，歷史區只剩 1,124 個檔案（uv 快取沒有一起搬），凍結摘要無法重現；任何重跑都會在 read-only preflight 停下，且需要再一次 source commit 與新的 `OwnerAuthorizationId`。
3. **A11 想回答的數值問題，用既有的 12 個 GPU 副本在 CPU 上就能回答。** 見 §3 的離線重算。

A11 的六次嘗試沒有一次死在統計門檻上；它們死在 environment 階段、映像建置、model-contract 階段、`model cache inventory mismatch`、`invocation stdout path must be absolute`。這些都是 Windows 啟動器 → Linux 驗證器之間的序列化與清單問題，8/28–8/31 為此累積了 24 對 design/plan 文件（約 3 萬行），每修一個就需要一次新的 GPU 授權。這是典型的「修啟動器」迴圈，不是研究阻塞。

### Q4 最小且有求職價值的復活範圍是什麼？

**一條看得到曲線的主動學習迴圈，而不是一個更完整的 Wave 0。** 面試時能講的東西：

- 一張「預算 vs mAP」曲線，至少 random / entropy / margin 三條，一個 seed，四個預算點。
- 一段誠實的可重現性說明：同機重播的差異來源已歸因到 `grid_sample` CUDA backward，量級已量化（§3），因此以「seed 固定 + 記錄重播離散度」取代「bitwise 一致」。
- 一個 5 分鐘能跑的 CPU 入口（README + pytest + 合成 fixture）。

不做：五個 arm 全上、三個 seed、66 個 fit、oracle 防火牆容器化、A11、evaluator 封印。這些留在原規格作為「完整協定」的設計證明，不再是前置條件。

## 2. 時間軸（由 git log 與證據目錄核對）

| 日期 | 事件 | 終端結果 |
|---|---|---|
| 8/23 | 規格與 8-wave 計畫核准（`main`） | — |
| 8/24 | Wave 0 Task 1–4 實作；Option A 首次 GPU 執行 | Task 5 FAIL：labeled loss 類別維度 80 vs 4 |
| 8/24–25 | A2 修四類 reset，5 次 campaign | 最後一次 NORMATIVE_FAIL：要求 bitwise CUDA backward 一致，結構上不可能 |
| 8/25 | A3 改為有界數值重播；A4 修 source hash；A5 保留 warning 清單 | 各一次 campaign，都在前置檢查停下 |
| 8/25 | A6 強制 Math-only SDPA，2 次 campaign | 第 2 次：5 個 stage 個別 PASS，彙總 FAIL（見 §3） |
| 8/25–27 | A7 歸因診斷，10 次 campaign（前 9 次死於啟動器） | 第 10 次 ATTRIBUTED |
| 8/27 | A8–A10 修快取、下載日誌、stdout 位元組 | 啟動器修補 |
| 8/28–31 | A11 統計重播，6 次 campaign，24 對救援文件 | 全部 NORMATIVE_FAIL；最後修補 `10d866c` 未再執行 |
| 9/2 | 證據目錄搬遷 | 歷史清單摘要失效 |

## 3. 低負載 CPU 診斷結果

### 3.1 A6 數值重播差異（既有 gate receipt，直接讀取）

同一 seed、同一映像、同一 GPU 的兩次單步訓練（`clean_a_a` 對 primary A）：

| 量 | 觀察值 | A3 界限 |
|---|---|---|
| 梯度範數 | 2992.56 vs 2988.58（相對差 1.3e-3） | rel 1e-5 |
| backbone 參數更新 relative L2 | 0.059 | 0.001 |
| detector 參數更新 relative L2 | 0.021 | 0.001 |
| backbone 更新 cosine | 0.99825 | ≥ 0.99999 |
| loss（hex） | 完全一致 | — |

結論：loss 與離散狀態 bitwise 一致，梯度與更新向量有 1e-3 到 6e-2 量級的同機離散。這是 CUDA atomicAdd 累加順序造成的，A7 已歸因。

### 3.2 用既有 12 個 A11 副本離線重算 13 個配對指標

來源：`a11-runs/wave0-a11-calibration-20260831T051426556Z-b3e22466`（`steven006`）的 12 份 PASS receipt 與 12 個經 SHA-256 驗證的 checkpoint。方法：呼叫 repo 內既有的 `compare_statistical_pair` 與 `derive_calibration_thresholds`，CPU float64，66 個配對。只讀，不寫入證據目錄。

| 指標（66 配對） | 最大值 | 1.5 × 最大值 | A11 實務上限 | 在上限內 |
|---|---:|---:|---:|:---:|
| gradient_norm.relative_difference | 2.81e-3 | 4.22e-3 | 1e-2 | 是 |
| model_update.backbone.relative_l2 | 6.35e-2 | 9.53e-2 | 1e-1 | 是（最接近上限） |
| model_update.backbone.cosine_defect | 2.02e-3 | 3.03e-3 | 5e-3 | 是 |
| model_update.detector.relative_l2 | 2.19e-2 | 3.29e-2 | 1e-1 | 是 |
| model_update.detector.cosine_defect | 2.40e-4 | 3.60e-4 | 5e-3 | 是 |
| optimizer_state.backbone.exp_avg.relative_l2 | 1.46e-2 | 2.19e-2 | 1e-1 | 是 |
| optimizer_state.backbone.exp_avg.cosine_defect | 1.06e-4 | 1.59e-4 | 5e-3 | 是 |
| optimizer_state.backbone.exp_avg_sq.relative_l2 | 3.19e-2 | 4.79e-2 | 1e-1 | 是 |
| optimizer_state.backbone.exp_avg_sq.cosine_defect | 4.59e-4 | 6.88e-4 | 5e-3 | 是 |
| optimizer_state.detector.exp_avg.relative_l2 | 3.06e-3 | 4.59e-3 | 1e-1 | 是 |
| optimizer_state.detector.exp_avg.cosine_defect | 7.36e-7 | 1.10e-6 | 5e-3 | 是 |
| optimizer_state.detector.exp_avg_sq.relative_l2 | 5.62e-3 | 8.43e-3 | 1e-1 | 是 |
| optimizer_state.detector.exp_avg_sq.cosine_defect | 1.02e-9 | 1.54e-9 | 5e-3 | 是 |

66 個配對全部通過 A3 的離散欄位精確比對（`exact` 無錯誤）；`derive_calibration_thresholds` 對這 66 對回傳 13 個門檻而沒有拋出上限錯誤。完整最小值／中位數／最大值在 [2026-09-09-a11-offline-pair-metrics.json](../archive/wave0/2026-09-09-a11-offline-pair-metrics.json)，腳本在 [2026-09-09-a11-offline-pair-metrics.py](../archive/wave0/2026-09-09-a11-offline-pair-metrics.py)。

12 個副本的 loss 全部是 `0x1.b1c6ea0000000p+8`；梯度範數落在 2984.49–2992.91；峰值 VRAM 921 MiB；單步 GPU 時間 1.4–2.05 秒。

結論：A11 校準階段想要的數值答案已經在這 12 個副本裡。若 8/31 那次啟動器沒有在路徑序列化上失敗，校準會以 `RECORDED` 收尾，且 13 個門檻都在實務上限內；最接近上限的是 backbone 參數更新的 relative L2（門檻 0.095 對上限 0.10）。這個結果只說明「同機同 seed 的單步重播離散度可量化且有界」，不構成 A11 receipt，也不構成 Wave 0 PASS；它的用途是讓後續協定可以引用一個已量化的離散量級，而不必再跑 12+12 副本。

### 3.3 CPU 測試套件

在 `.venv` 以預設環境執行 `python -m pytest -q -p no:cacheprovider`（`PYTHONDONTWRITEBYTECODE=1`，不隱藏 GPU，不啟動 Docker）：

| 結果 | 數量 | 說明 |
|---|---:|---|
| passed | 773 | 收據、摘要、no-clobber、模型契約、訓練探針、checkpoint、數值／統計重播、A7 微檢查等 Python 層全部通過 |
| failed | 569 | 全部在 `tests/gates/test_wave0_a11_launcher.py`（349）與 `tests/gates/test_wave0_a7_launcher.py`（220） |
| skipped | 14 | 平台條件（Linux 檔案系統契約等） |

569 個失敗中 568 個是 `FileNotFoundError: [WinError 2]`，另 1 個是同一原因造成的 `TypeError`：兩個啟動器測試檔直接以 `subprocess` 呼叫 `pwsh`（PowerShell 7），而本機目前 PATH 只有 Windows PowerShell 5.1。這是環境缺件，不是程式回歸；A11 規格本來就要求 PowerShell 7 加 5.1 兩個解析器。裝回 PowerShell 7 後應重跑這兩個檔案確認。

另外兩個觀察：先前以 `CUDA_VISIBLE_DEVICES=""` 執行時，checkpoint 相關測試會因 `CUDA RNG device-count mismatch` 大量失敗，因為 `load_checkpoint_verified` 要求本機 CUDA 裝置數等於 checkpoint 內記錄的 1；測試收集本身需約 224 秒。

### 3.4 本機 runtime 盤點（只讀）

- `.venv`：Python 3.12.11、torch 2.12.0+cu126、torchvision 0.27.0+cu126、transformers 5.15.0、scipy 1.18.0、pycocotools 2.0.10，與鎖檔一致。
- GPU：RTX 4090，driver 591.86；Docker Desktop 正在為另一個專案運行，本專案 25 個映像（每個 16.8 GB）仍在；WSL `docker-desktop` 運行中。PowerShell 7（`pwsh`）目前不在 PATH。
- 證據目錄：1,529 個檔案，約 11 GB；其中 `a11-runs` 6.1 GB（主要是兩個 12 副本 cohort 的 checkpoint，各 230 MB）。

## 4. 核心缺口

1. 沒有資料層：RDD 下載、XML→COCO、去重、切分、測試集凍結。
2. 沒有選樣層：§7.3 的 entropy / margin 公式、§7.4 的 k-center。
3. 沒有訓練迴圈：只有單步探針；缺 dataloader、augmentation、30-epoch schedule、resume。
4. 沒有評估：pycocotools mAP、預算曲線、AUBC。
5. 入口債：根目錄原本沒有 README；A11 文件佔 docs 的九成，會讓讀者誤以為專案主體是啟動器工程。

## 5. 建議：續做，但先把協定降規

**續做的理由：** 模型契約、四類 reset、BF16 單步、checkpoint 往返、receipt/no-clobber 基礎都真的跑通了；RT-DETR 的原始輸出契約（300 query、final/penultimate box、sigmoid 前景分數）正是 §7.3 不確定性公式需要的輸入，可以直接沿用。硬體、映像、venv 都在。

**暫停原協定的理由：** 原協定把「同機統計重播包絡」放在資料之前，導致 9 天內 26 次 GPU campaign 沒有一次接觸資料。66 個 fit 的正式矩陣對單人單卡的復活也不成比例。

**降規後的協定（v0.2-lite，待你確認）：**

- 資料：RDD 單一國別子集起步（建議 Czech；下載前確認大小與條款），train/test 以 hash 切分並凍結。
- 模型：沿用 `PekingU/rtdetr_r18vd` 與四類 reset。
- arm：random、entropy、margin（core-set / hybrid 待 DINOv2 embedding 上線後再加）。
- seed：17；預算：2%、5%、10%、20%；epoch：12（原 30，先降）。
- 可重現性宣稱：seed 固定、每個 fit 記錄 receipt、引用 §3.2 的同機離散量級；不宣稱 bitwise。
- 不做：evaluator 封印、oracle 容器化、A11、公開發布。

## 6. 有限步驟的復活方案

| 步 | 內容 | 資源 | 完成判準 |
|---:|---|---|---|
| 0 | 本輪：README、本文件、離線診斷、分支 `codex/revival-entry-20260909` | CPU | 已交付 |
| 1 | 寫 v0.2-lite 協定文件（§5 內容成文，一頁） | CPU，半天 | 你核可 |
| 2 | 選樣模組：§7.3 entropy / margin 公式 + 手算合成測試；沿用 `RawDetectorOutput` | CPU，1 天 | pytest 綠，score 對 query 置換不變 |
| 3 | 資料模組：RDD XML→COCO manifest、去重、hash 切分、合成 fixture 測試 | CPU，1 天 | 不下載真資料也能跑測試 |
| 4 | 訓練器：多 epoch loop、dataloader、augmentation、pycocotools 評估；先在合成 fixture 上跑 2 epoch | CPU 可驗流程；GPU 需另行同意 | 合成資料上 loss 下降、mAP 可算 |
| 5 | 下載 Czech 子集，跑 2% 基線一個 fit | GPU，需另行同意，約 1 小時 | 基線 mAP 合理、checkpoint receipt 齊 |
| 6 | 跑 3 arm × 4 預算，1 seed，輸出曲線 CSV 與圖 | GPU，粗估 3–4 小時 | 曲線文件 + 結果表 |
| 7 | 結果文件與 README 更新；可選加 seed 29/43 | CPU | — |

每一步都可以單獨停；第 5 步之前完全不需要 GPU 或資料。若第 5 步基線訓練不收斂，先修訓練器再進第 6 步，不回頭修 A11。

## 7. 本輪未做與保留

- 未修改任何 `src/`、`tests/`、`scripts/`、schema 或既有文件；A11 的 24 對救援文件原樣保留。
- 未刪除或移動任何證據、映像、lease。
- 未執行 Docker 建置、GPU campaign、資料下載、公開發布。
- 離線診斷腳本與 JSON 附在 `docs/archive/wave0/` 供核對；它不是 A11 receipt，也不是 Wave 0 PASS。
