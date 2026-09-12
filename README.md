# vision-active-learning-loop

RT-DETR（`PekingU/rtdetr_r18vd`）在 RDD 道路損壞資料上的主動學習實驗基礎建設。
目標是比較 random / entropy / margin / core-set / hybrid 五種選樣策略在固定預算下的偵測表現。

**現況（2026-09-12）：v0.3 五策略第一輪比較完成，主要入口為 `main`。**

前一輪 v0.2.1 已於 2026-09-11 跑完。在固定 epoch 規則（`fixed-epochs`，每個 fit `max(200, 18 × floor(N/8))` 步）下重跑三個 seed（30 個 fit），並為兩種訓練長度規則各跑三個全標籤參考基線（2,255 張）。
entropy 與 margin 的配對 nAUBC 差對 random 在新規則下**仍然三個 seed 都是正的**（與固定 1,000 步的 v0.2-lite 相同，兩種規則各 3/3）；20% 預算時 entropy／margin 約達同 seed 參考基線的 0.49 到 0.63，random 0.30 到 0.45。
一個負面結果：v0.2-lite 報告的「20% 最低類別 recall 三個 arm 區間不重疊」在固定 epoch 規則下不成立。
**v0.3（2026-09-12）補齊 core-set 與 hybrid**（DINOv2-small 向量、貪婪 k-center；hybrid 先用 entropy 篩候選），同樣三個 seed、固定 epoch 規則、實驗內與 random 配對：hybrid 對 random 三個 seed 都為正（3/3）；core-set 在一個 seed 為負（2/3），依預先登記的規則寫「不一致」。五種策略的第一輪比較到此完成，見 [docs/results/2026-09-12-v0.3-diversity.md](docs/results/2026-09-12-v0.3-diversity.md)（含 12 對 random arm 的同機重播差，最大 0.0075，是讀所有配對差量值的尺度）。
結果、每個設定的影像／框／負樣本數、步數與秒數、能說與不能說的界線見 [docs/results/2026-09-11-v0.2.1-training-rule.md](docs/results/2026-09-11-v0.2.1-training-rule.md)；磁碟核對腳本與輸出在 [docs/status/2026-09-11-v0.2.1-disk-verification.py](docs/status/2026-09-11-v0.2.1-disk-verification.py) 與同名 `.json`。

![主動學習迴圈（30 秒）：三個 arm 從同一個 46 張起點分岔，三個 seed 的 margin − random 配對差都為正](docs/media/val-loop-short.gif)

上面的動畫由 [docs/media/manim/](docs/media/manim/) 渲染，數字直接讀自 `docs/results/` 的 summary 與收據；它只做說明，不是證據。

上一輪 v0.2-lite（2026-09-09，固定 1,000 步）的三 seed 結果原樣保留：[docs/results/2026-09-09-lite-czech-three-seeds.md](docs/results/2026-09-09-lite-czech-three-seeds.md)。
v0.2.1 的預先登記協定（規則、常數、判定條件，看到結果前後未改）在 [docs/superpowers/specs/2026-09-10-val-v0.2.1-training-rule-protocol.md](docs/superpowers/specs/2026-09-10-val-v0.2.1-training-rule-protocol.md)；
開始前的 CPU sanity audit（含 seed 43 跑了兩次這件事，當整條 pipeline 的同機重播對照）在 [docs/status/2026-09-10-lite-sanity-audit.md](docs/status/2026-09-10-lite-sanity-audit.md)；
2026-09-11 的交接與執行順序在 [docs/status/2026-09-11-v0.2.1-handoff.md](docs/status/2026-09-11-v0.2.1-handoff.md)。
原 Wave 0 分支停在模型契約與單步訓練可行性；復活工作依 v0.2-lite 協定進行。
完整評估見 [docs/status/2026-09-09-revival-assessment.md](docs/status/2026-09-09-revival-assessment.md)，
已核可的降規協定見 [docs/superpowers/specs/2026-09-09-val-v0.2-lite-protocol.md](docs/superpowers/specs/2026-09-09-val-v0.2-lite-protocol.md)。

## 分支與位置

| 項目 | 位置 |
|---|---|
| `main`（目前成果與重現入口） | 包含 v0.2-lite、v0.2.1 與已完成的 v0.3 五策略第一輪比較；`7cc404c` 記錄 v0.3 完成結果 |
| 歷史 Wave 0 分支 `codex/wave0-model-contract`（非目前開發入口） | `10d866c`，147 個 commit，已推到私人 GitHub |
| 復活分支 `codex/revival-entry-20260909`（已併入 `main` 並於 2026-09-11 刪除） | 由 `10d866c` 分出。加入 README、現況文件、v0.2-lite 與 v0.2.1 協定、`lite/` 模組與兩輪結果；不改動任何既有 Wave 0 程式、測試、腳本或證據 |
| GPU 執行證據（不進 Git） | `<evidence-root>\wave0`（2026-09-02 由 `D:\vision-active-learning-loop-artifacts` 搬入） |
| 設計規格 | [docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md](docs/superpowers/specs/2026-08-23-vision-active-learning-loop-design.md) |
| 計畫索引 | [docs/superpowers/plans/2026-08-23-vision-active-learning-loop-plan-index.md](docs/superpowers/plans/2026-08-23-vision-active-learning-loop-plan-index.md) |

## 程式碼裡有什麼

下圖說明預設 random／entropy／margin 三 arm 的 lite 路徑；v0.3 的 core-set／hybrid 擴充與執行方式見下方及 v0.3 結果報告。節點是實際註冊的 `val lite` 命令與它們寫出的檔案；圖源在 [docs/diagrams/](docs/diagrams/)，改程式時一起改。

```mermaid
flowchart TD
    M["manifest.json（切分與標註）<br/>public-pool.json（無標籤的 pool 視圖）"] --> B["val lite baseline<br/>共享 2% 起點 fit（46 張）"]
    B --> BM["metrics-shared-0.02.json<br/>fits/shared-0.02/fit-receipt.json + checkpoint.pt"]
    BM --> G1{"val lite gate<br/>loss 前 10% 中位數 > 後 10%？<br/>allowlist warning 恰 9？"}
    G1 -->|FAIL：exit 2| STOP["停止：不重試、不覆寫<br/>failure.json + transcript log"]
    G1 -->|PASS| R["val lite reference（v0.2.1）<br/>pool 全部 2,255 張的 fit"]
    R --> RM["metrics-reference-1.00.json<br/>fits/reference-1.00/fit-receipt.json"]
    RM --> G2{"val lite gate --role reference"}
    G2 -->|FAIL：exit 2| STOP
    G2 -->|PASS| RUN["val lite run --rule fixed-steps／fixed-epochs<br/>3 arm × 3 輪：打分 → 選前 k → fit → 評估<br/>random 凍結序；entropy／margin 依分數"]
    RUN --> OUT["metrics.csv、curve.svg<br/>ledger-random／entropy／margin.json<br/>experiment-receipt.json"]
    OUT --> S["val lite summarize（三 seed，--reference）<br/>summary.json、summary.csv、mean-curve.svg"]
    S --> V["docs/status/2026-09-11-v0.2.1-disk-verification.py<br/>雜湊、步數、warning、ledger 巢狀"]

    classDef cmd fill:#90EE90,stroke:#333,stroke-width:2px,color:#0B3D0B
    classDef file fill:#E6E6FA,stroke:#333,stroke-width:2px,color:#1A1A5E
    classDef gate fill:#FFD700,stroke:#333,stroke-width:2px,color:#000
    classDef stop fill:#FFB6C1,stroke:#DC143C,stroke-width:2px,color:#000
    class B,R,RUN,S,V cmd
    class M,BM,RM,OUT file
    class G1,G2 gate
    class STOP stop
```

以下是原 Wave 0 CLI 的歷史命令與執行紀錄；目前 `val lite` 命令與已完成模組見下表：

| 命令 | 作用 | 實際在 GPU 跑過 |
|---|---|---|
| `environment check` | 比對 Python / torch / CUDA / GPU 與 `configs/environment/wave0.yaml` | 是 |
| `assets verify` | 下載並驗證 RT-DETR 與 DINOv2 的 revision、safetensors SHA-256、授權 | 是 |
| `probe model-contract` | 用兩張合成影像觀察 RT-DETR 的 300 query / 4 類輸出契約 | 是 |
| `probe training-feasibility` | 一個 BF16 訓練步、AdamW 更新、checkpoint 存讀驗證 | 是（多次；最後一次 12 個副本） |
| `gate wave0` | 彙總上述收據並做同機重播比對 | 是，結果 `FAIL`（數值重播超出 A3 界限） |
| `diagnose grid-sample-attribution` | 把重播差異歸因到 `grid_sampler_2d_backward_cuda` | 是，結果 `ATTRIBUTED` |
| `gate statistical-replay calibrate` / `validate` | A11 統計重播包絡（12+12 副本） | 否；6 次啟動皆在彙總前失敗 |

原 Wave 0 尚未實作 RDD manifest、多輪訓練器、pycocotools 評估與預算曲線；這些已由下列 lite pipeline 完成。原 8-wave 正式協定與 lite 研究的驗證範圍分開保留。

已完成的 lite 模組（`src/vision_active_learning_loop/lite/`；表中測試數為各輪完成時的紀錄）：

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
| `gate.py` | 已完成。`val lite gate`：§8 門檻（基線 loss 前 10% 中位數 > 後 10% 中位數；CUDA 時 allowlist warning 恰為 9），輸出 `PASS/FAIL {...}`，退出碼 0／2／3；`--role reference` 對參考基線做同一門檻 |
| `train.py` 的訓練規則（v0.2.1） | 已完成，2026-09-11 在 GPU 跑完三 seed。`TrainingRule`：`fixed-steps`（1,000 步，原協定）與 `fixed-epochs`（`max(200, 18 × floor(N/8))` 步）；所有 `val lite` 命令加 `--rule`；fit 收據記錄規則、實際步數、開始的 epoch 數與秒數；實驗收據記錄 fit／打分／評估各階段秒數 |
| `reference.py`（v0.2.1） | 已完成，2026-09-11 兩種規則各跑三個 seed。`val lite reference`：用 pool 全部 2,255 張與全部標籤訓練一個 fit 並在凍結 test 評估，輸出 `metrics-reference-1.00.json`；不讀 test 做任何選擇 |
| `diversity.py`（v0.3） | 已完成 DINOv2-small 向量、core-set 貪婪 k-center 與 entropy 候選後的 hybrid；三 seed 結果與限制見 [v0.3 報告](docs/results/2026-09-12-v0.3-diversity.md) |
| `summary.py`（v0.2.1 擴充） | `val lite summarize` 加 `--reference`：報告訓練規則、各設定平均步數與秒數、跨 seed 的最小／最大**範圍**（不是信賴區間）、20% 相對參考基線的比例；對舊收據輸出的 nAUBC、配對差與曲線與已發布的 `summary-3seeds` 逐位元相同 |

設 `VAL_LITE_SNAPSHOT` 可另跑用真 RT-DETR 在 CPU 走完整路徑的整合測試（fit、評估、基線命令、完整實驗；已通過）。`scripts/run_lite_seed17.ps1` 是把以上串起來的唯一啟動點，有 Windows PowerShell 5.1 解析檢查與 dry-run 測試。

真實資料：RDD2022 Czech train 子樹已於 2026-09-09 取得並建好 manifest（2,829 張、1,745 框、test 574／pool 2,255），來源、雜湊與計數見 [docs/data-card.md](docs/data-card.md)。
三輪的結果檔在 [docs/results/](docs/results/)：每個實驗與參考基線一個目錄，加上跨 seed 的 [summary-3seeds/](docs/results/summary-3seeds/)（v0.2-lite）、[summary-ep18-3seeds/](docs/results/summary-ep18-3seeds/) 與 [summary-3seeds-with-reference/](docs/results/summary-3seeds-with-reference/)（v0.2.1），以及 [summary-ep18-div-3seeds/](docs/results/summary-ep18-div-3seeds/)（v0.3）。

## 在本機（CPU）檢查

```powershell
cd "<repo>"
.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
```

- `.venv` 在 repo 根目錄（2026-09-11 移除 worktree 後以 `uv sync --frozen` 重建），Python 3.12.11 + torch 2.12.0+cu126 + transformers 5.15.0，與鎖定版本一致。
- 測試不啟動 Docker、不做 GPU 運算，但 checkpoint 載入器會讀取 CUDA RNG 狀態，因此需要本機看得到一顆 GPU（不要設 `CUDA_VISIBLE_DEVICES=""`）。
- 測試收集約需 4 分鐘（啟動器測試會解析大型 PowerShell 腳本）。
- 2026-09-09 實測：773 passed、569 failed、14 skipped。569 個失敗全部是兩個啟動器測試檔找不到 `pwsh`（PowerShell 7 目前不在 PATH），Python 層測試全數通過。
- 2026-09-10 `tests/lite`：209 passed、7 skipped（skipped 是設 `VAL_LITE_SNAPSHOT` 才跑的 CPU 整合測試）；2026-09-11 在根目錄重建的環境：210 passed、7 skipped。
- 用既有 12 個 GPU 副本在 CPU 上重算 A11 的 13 個配對指標，全部落在實務上限內；數字與腳本在 `docs/status/`。

## 跑 GPU 實驗（一條指令）

開任何一個 PowerShell（不需要 `cd`、不需要啟用 venv、不需要改 execution policy）。下面用絕對路徑呼叫，從任何目錄貼上都一樣。

先只做檢查，不啟動任何東西：

```powershell
powershell -ExecutionPolicy Bypass -File "<repo>\scripts\run_lite_seed17.ps1" -DryRun
```

每一行都是 `ok` 才往下。正式執行（GPU 被別的工作占用時會每 30 秒等一次，最多 4 小時）：

```powershell
powershell -ExecutionPolicy Bypass -File "<repo>\scripts\run_lite_seed17.ps1" -WaitForGpu
```

換 seed 就在後面加 `-Seed 29` 或 `-Seed 43`。腳本檔名固定不變，seed 由參數決定，輸出目錄與紀錄檔會自動帶上該 seed。

v0.2.1（固定 epoch 規則加全標籤參考基線）用同一支腳本，多兩個參數；2026-09-11 已照下面的順序跑完三個 seed。pilot 先只跑 seed 17：

```powershell
powershell -ExecutionPolicy Bypass -File "<repo>\scripts\run_lite_seed17.ps1" -WaitForGpu -Rule fixed-epochs -Reference
```

順序是：2% 基線（200 步）→ 門檻 → 參考基線（2,255 張、5,058 步）→ 門檻 → 完整實驗（10 個 fit）。輸出目錄帶 `ep18`：`lite-czech-ep18-s17-<時間戳>\`、`lite-czech-ref-fixed-epochs-s17-<時間戳>\`。pilot 通過後再加 `-Seed 29`、`-Seed 43`；規則 A 的參考基線用 `-Rule fixed-steps -ReferenceOnly`（只跑參考 fit 與它的門檻，不重跑已完成的固定步數基線與實驗）。

v0.3（core-set 與 hybrid，協定在 [docs/superpowers/specs/2026-09-11-val-v0.3-diversity-protocol.md](docs/superpowers/specs/2026-09-11-val-v0.3-diversity-protocol.md)）先算一次 pool 的 embedding（GPU 空閒時約 1 分鐘；`--device cpu` 約 5 分鐘）：

```powershell
<repo>\.venv\Scripts\val.exe lite embed --manifest "<evidence-root>\lite\data\czech\manifest.json" --images "<data-root>\rdd2022\czech\images" --snapshot "<evidence-root>\wave0\model_cache\snapshots\facebook--dinov2-small\ed25f3a31f01632728cabb09d1542f84ab7b0056" --output-dir "<evidence-root>\lite\data\czech" --device cuda
```

再用同一支啟動器跑 `random + coreset + hybrid`（實驗 id 帶 `div`；`-Seed 29`、`-Seed 43` 同理）：

```powershell
powershell -ExecutionPolicy Bypass -File "<repo>\scripts\run_lite_seed17.ps1" -WaitForGpu -Rule fixed-epochs -Arms random,coreset,hybrid -Embeddings "<evidence-root>\lite\data\czech\embeddings-dinov2-small.npz"
```

腳本會依序：共享 2% 基線 fit 與評估 → §8 門檻（loss 下降、9 個 allowlist warning）→ 完整實驗（3 arm × 3 輪，共 10 個 fit）。任一步失敗就停，不重試、不覆寫；`RUNNING.lock` 防止同時跑兩份。全部輸出與逐字紀錄在 `<evidence-root>\lite\`：`lite-czech-s17-<時間戳>\{metrics.csv, curve.svg, ledger-*.json, experiment-receipt.json}` 與 `run-lite-seed17-<時間戳>.log`。

啟動器的實際順序、退出碼與停止點，由 `scripts/run_lite_seed17.ps1` 導出：

```mermaid
sequenceDiagram
    participant O as 👤 owner（PowerShell 5.1）
    participant L as run_lite_seed17.ps1
    participant N as nvidia-smi
    participant V as val.exe
    participant E as 證據目錄 lite\

    O->>L: -WaitForGpu -Rule fixed-epochs -Reference [-Seed N]
    L->>L: preflight：val、python、manifest、影像、模型快照
    Note over L: 缺任一輸入 → exit 3（-DryRun 在此停止，exit 0）
    L->>E: 建立 RUNNING.lock
    Note over L,E: 鎖檔已存在 → exit 3，不啟動第二份
    loop 每 30 秒取樣，直到連續兩次低於 4,000 MiB 且低於 5%
        L->>N: 查記憶體與利用率
        N-->>L: used、util
    end
    Note over L,N: 沒帶 -WaitForGpu 且 GPU 忙 → exit 4；等超過 4 小時 → exit 4
    L->>V: lite baseline（共享 2% 起點）
    V-->>E: metrics-shared-0.02.json、fit 收據、checkpoint.pt
    L->>V: lite gate
    Note over L,V: 任一階段回傳非 0 → exit 2，不重試、不覆寫
    L->>V: lite reference（-Reference）
    V-->>E: metrics-reference-1.00.json、fit 收據
    L->>V: lite gate --role reference
    Note over L: -ReferenceOnly：到此 exit 0，不跑完整實驗
    L->>V: lite run（3 arm × 3 輪，10 個 fit）
    V-->>E: metrics.csv、curve.svg、ledger-*.json、experiment-receipt.json
    L->>E: 刪除 RUNNING.lock，關閉 transcript（run-lite-…log）
    L-->>O: done. results: lite-czech-…（exit 0）
```

失敗時看兩個地方：逐字紀錄 `run-lite-seed17-<時間戳>.log`（val 的 stdout 與 stderr 都在裡面），以及實驗目錄下的 `failure.json`（基線失敗時寫入，含完整診斷）。2026-09-09 第一次 GPU 基線就是被 warning 契約擋下（11 個而非 9 個），原因與修正記在協定 §3。

不要做的事：不要同時開第二個視窗再跑一次；不要在 GPU 有別的工作時去掉 `-WaitForGpu`（腳本會直接以代碼 4 退出，不會硬擠）。

## 重要邊界

- 原 8-wave 協定要求 Wave 0 `PASS` 才能碰資料；Wave 0 至今沒有 `PASS`。復活評估的結論是這個前提可以重新界定，不必先完成 A11。
- 證據根目錄已搬遷，A11 啟動器凍結的 64,306 檔歷史清單已無法重現，任何 A11 重跑都會在 preflight 停下。
- 本 repo 不放 RDD 影像、標註、權重、checkpoint。
