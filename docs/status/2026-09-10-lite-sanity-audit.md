# v0.2-lite 資料與證據 sanity audit（2026-09-10）

下一輪方法驗證（v0.2.1）開始前，用 CPU 從磁碟重算既有證據。腳本 [2026-09-10-lite-sanity-audit.py](2026-09-10-lite-sanity-audit.py)，輸出 [2026-09-10-lite-sanity-audit.json](2026-09-10-lite-sanity-audit.json)。只讀不寫，不重跑任何訓練。

```powershell
.venv\Scripts\python.exe docs\status\2026-09-10-lite-sanity-audit.py
```

## 檢查結果

| 項目 | 方法 | 結果 |
|---|---|---|
| 切分 | 對 manifest 全部 2,829 筆以 `item_id` 重算 `assign_split` | 0 筆不一致；test 574／pool 2,255 |
| 標註轉換 | 固定亂數（20260910）抽 200 個原始 XML，重新解析、以影像位元組重算 `item_id`，逐框比對 manifest | 200/200 框集合一致、尺寸一致 |
| 類別覆蓋 | test 每類框數 | D00 194、D10 62、D20 27、D40 44（≥ 20，符合 §2.3） |
| 模型初始化 | 四個實驗共 40 個 fit 收據的 `model_sha256` | 全部同一值（`bb736d53…`），即 reset 後的起始權重一致 |
| 訓練規則 | 40 個收據的 `steps`、warning 數、SDPA 後端 | 全部 1,000 步、9 個 allowlist warning、`MATH` |
| 收據 | checkpoint 位元組 SHA-256 對 fit 收據與實驗收據 | 40/40 三方一致 |
| ledger | 每輪張數、`item_id` 唯一、random 無分數、uncertainty 全有分數 | 全部符合 67／113／225 |
| loss | 前 10% 步中位數 > 後 10% | 40/40 |

manifest 摘要 `3d961040…9388d`；預算 46／113／226／451；pool 全量 2,255（v0.2.1 參考基線的訓練集大小）。

## 之前沒有記錄的事實：seed 43 跑了兩次

`lite-czech-s43-20260909T1640Z`（16:40Z 啟動，3,749 s，exit 0）與 `lite-czech-s43-20260909T1755Z`（17:55Z，5,157 s，exit 0）都是完整的 10-fit 實驗，同 seed、同 manifest、同模型、同機。前一份沒有進任何報告；[2026-09-09 三 seed 報告](../results/2026-09-09-lite-czech-three-seeds.md) 只用了 1755Z。兩份都保留，這裡把它們當成**整條 pipeline 的同機重播對照**。

| 項目 | 1640Z | 1755Z | 差 |
|---|---:|---:|---:|
| 共享 2% checkpoint | `11936055…` | 不同 | 位元組不同（CUDA `grid_sample` backward 不可重播，v0.1 §5.2.15） |
| nAUBC random | 0.01073 | 0.01184 | +0.0011 |
| nAUBC entropy | 0.01275 | 0.01585 | +0.0031 |
| nAUBC margin | 0.02177 | 0.02064 | −0.0011 |
| Δ entropy − random | +0.0020 | +0.0040 | |
| Δ margin − random | +0.0110 | +0.0088 | |
| mAP50–95 @20%：random / entropy / margin | 0.0201 / 0.0215 / 0.0431 | 0.0222 / 0.0263 / 0.0352 | +0.0020 / +0.0048 / **−0.0079** |
| 最低類別 recall @20% | 0.115 / 0.245 / 0.255 | 0.056 / 0.222 / 0.263 | |

選樣本身也不重播：random 的 ledger 三輪 100% 相同（凍結序），但 entropy 與 margin 在兩次之間每輪只有 **21–37%** 的影像重疊（第 1 輪 15/67 與 14/67，第 3 輪 67/225 與 83/225）。不確定性分數由不可重播的 checkpoint 產生，排序在前 k 附近的微小差異就會換掉大部分影像。

### 這對結論的影響

1. 單一 fit 的 mAP 重播離散度在整條 pipeline 層級可達 **0.0079**（margin @20%），比三 seed 報告引用的基線對照（最大 0.0051）更大。三 seed 報告的「20% 時 margin 是 random 的 1.61 倍」是平均值，個別點的離散度必須一起看。
2. 配對 nAUBC 差的**正負號**在兩次重播中都保持（entropy 與 margin 皆為正，margin > entropy），與三個 seed 的 3/3 一致。目前撐得住的仍是正負號一致性與最低類別 recall 的區間分離（兩次重播的 random 0.056–0.115、entropy 0.222–0.245、margin 0.255–0.263，仍不重疊）。
3. 因此 v0.2.1 的判定規則沿用正負號一致，不對 nAUBC 差的量值設門檻；報告時把這一對重播當成量值的尺度來引用。
4. 這一對只有 n = 1，不是統計包絡；不用它宣稱任何離散度上限。

## 目前的訓練規則在各預算實際跑了幾個 epoch

固定 1,000 步、batch 8、只取完整批次：

| 預算 | 張數 | 每 epoch 批次 | 約 epoch 數 | 收據末段 loss 中位數（s17，random arm） |
|---:|---:|---:|---:|---:|
| 2% | 46 | 5 | 174 | 4.5 |
| 5% | 113 | 14 | 71 | 6.2 |
| 10% | 226 | 28 | 35 | 8.2 |
| 20% | 451 | 56 | 18 | 10.6 |

（「約 epoch 數」以 1,000×8／張數 估；一個 epoch 尾端不足一批的樣本留到下一 epoch 重洗。）末段 loss 隨預算單調上升（entropy 與 margin arm 同樣如此，見 JSON），就是預算與訓練長度混淆的直接證據；v0.2.1 就是要把這個混淆拿掉。
