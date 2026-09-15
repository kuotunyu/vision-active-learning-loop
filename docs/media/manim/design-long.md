# 設計：Manim 長版說明影片（訓練長度規則、參考基線、負面結果）

狀態：2026-09-11 與 owner 逐段確認後寫定。前置：[短版規格](design-short.md)（已完成，`docs/media/val-loop-short.gif`）。本規格只新增，不改短版的畫面與文字。

## 0. 目的與觀眾

- 用途：作品集頁面自動播放，無旁白，畫面字幕自讀；觀眾不在旁邊聽解釋。
- 內容：短版的四段（標題、pool、迴圈、曲線，約 30 秒）原樣沿用，接三章各約 25 到 30 秒，再接 6 秒結尾卡。全長約 1 分 50 秒到 2 分 10 秒。
- 三章：（1）訓練長度的混淆與兩種規則；（2）全標籤參考基線與相對比例；（3）20% 最低類別 recall 的負面結果。owner 決定不做「還不能宣稱什麼」專章，但結尾卡保留兩句否定句（§1）。
- 形式：1080p60 mp4 一支；不做 GIF；不進 git。
- 語言與邊界同短版：繁體中文畫面、指標名稱英文；不宣稱降低標註成本、不宣稱 deterministic 或跨機可重現、三個 seed 的最大最小只叫「範圍」。

## 1. 分鏡與畫面文字（凍結）

畫面文字集中在 `copy.py` 的 `COPY_LONG`；改句子等於改本規格。含 `{}` 的欄位由資料填入，下面括號內是目前資料的值。

### 第 1 章：訓練長度的混淆與兩種規則（約 30 秒）

| 畫面 | 畫面文字 |
|---|---|
| 章名卡 | 「為什麼要跑第二輪」；小字「固定步數把預算和訓練長度綁在一起」 |
| 四根長條：2%／5%／10%／20% 的張數（46／113／226／451）；每根上方是規則 A 下該 fit 的 epoch 數（200／72／36／18），隨預算變大而縮 | 「規則 A：每個 fit 固定 {steps_a} 步」（1,000）；「{start} 張跑 {epochs_a_02} 個 epoch，{n20} 張只跑 {epochs_a_20} 個」（46、200、451、18） |
| 切換到規則 B：長條上方改為步數（200／252／504／1,008）與 epoch（40／18／18／18） | 「規則 B：固定 {epochs_b} 個 epoch，最低 {min_steps} 步」（18、200）；「步數隨張數放大；2% 被最低步數托住」 |
| 左右兩個小曲線圖：規則 A、規則 B 的三 arm 平均曲線；各自下方「Δ entropy {n}/{total}」「Δ margin {n}/{total}」 | 「兩種規則下，entropy 與 margin 對 random 的配對差都是 {total} 個 seed 為正」；小字「兩種規則回答不同的問題，不預設哪一個公平」 |

規則 A 的 epoch 數不在舊收據裡，由步數與張數依訓練程式的規則算出（`ceil(steps ÷ floor(images ÷ batch))`，每 epoch 只取整批），畫面小字註明「依規則算出」。

### 第 2 章：全標籤參考基線（約 25 秒）

| 畫面 | 畫面文字 |
|---|---|
| 規則 B 的三 arm 平均曲線；上方一條虛線在參考基線平均（0.0664） | 「全標籤參考基線：{pool} 張全部標註、{epochs_b} 個 epoch」；小字「三個 seed 範圍 {ref_b_range}」（0.0656–0.0670） |
| 20% 那一點到虛線之間標比例 | 「20% 預算佔參考基線：random {ratio_random}、entropy {ratio_entropy}、margin {ratio_margin}」（0.30–0.45、0.53–0.63、0.49–0.57） |
| 再畫一條較低的帶狀區在規則 A 參考基線的範圍（0.0347–0.0425） | 「規則 A 的參考基線只有 {steps_a} 步（{epochs_ref_a} 個 epoch），是欠訓的」（1,000、4）；「固定 GPU 成本下，全部標籤沒有比 20% 多換到 mAP；這不能拿來說 20% 已經足夠」 |

### 第 3 章：一個負面結果（約 25 秒）

| 畫面 | 畫面文字 |
|---|---|
| 章名卡 | 「一個負面結果」；小字「20% 預算的最低類別 recall」 |
| 點圖：x 軸三個 arm，每 arm 三個點（三個 seed）；先畫規則 A，三組範圍互不重疊，括號標出 | 「v0.2-lite（規則 A）：三個 arm 的範圍互不重疊」；「random {rec_a_random}、entropy {rec_a_entropy}、margin {rec_a_margin}」（0.056–0.115、0.189–0.239、0.241–0.300） |
| 點移到規則 B 的值，括號重疊 | 「規則 B：random {rec_b_random} 與 entropy、margin 重疊」（0.107–0.281）；「這條證據跟訓練長度規則有關，不再單獨當作結論」 |

### 結尾卡（約 6 秒）

「不宣稱降低標註成本；同機重播並非位元相同」；「三個 seed 的最大最小是範圍，不是信賴區間」；小字為 `docs/results/2026-09-11-v0.2.1-training-rule.md`。

## 2. 資料綁定

原則同短版：沒有手打的數字；缺檔或缺欄位拋 `ExplainerDataError`，沒有預設值。

| 數字 | 來源 |
|---|---|
| 規則 B 各預算步數與 epoch | 規則 B 收據 `fits[*].steps`、`fits[*].epochs_started`（三個 seed 必須一致，否則拋錯） |
| 規則 A 各預算步數 | 舊收據 `runtime.steps`；`batch` 取 `runtime.batch_size` |
| 規則 A 各預算 epoch | 算出：`ceil(steps ÷ (images // batch))` |
| 三 arm 平均曲線（兩種規則） | 各 summary 的 `mean_map50_95[arm][fraction]`（含 `shared` 的 2%） |
| 參考基線（每 seed mAP、步數、張數）、平均 | summary 的 `reference.per_seed`、`reference.mean_map50_95` |
| 規則 B 參考基線的 epoch | 規則 B 參考基線目錄的 `fits/reference-1.00/fit-receipt.json` 的 `epochs_started`（18）；規則 A 參考基線的 epoch 同樣讀該收據（4） |
| 20% 佔參考基線比例、20% 最低類別 recall | summary 的 `per_seed[*].fraction_of_reference_at_0.20`、`min_class_recall_at_0.20` |
| 配對差正號數 | 沿用短版的 `positive_seed_count(arm)` |

- `data.py`：`ExplainerData` 新增欄位 `rule_name`、`steps`、`epochs`、`batch_size`、`mean_curve`、`reference`（seed → mAP、steps、images、epochs）、`reference_mean`、`ratio_20`、`min_recall_20`；短版不用的欄位給預設值，短版程式與測試不改。新增 `load_rule_pair(results_root) -> RulePair(rule_a, rule_b)`，A 讀 `summary-3seeds-with-reference`，B 讀 `summary-ep18-3seeds`。新增 `range_text(values, decimals) -> "低–高"`。
- `copy.py`：新增 `COPY_LONG` 與 `render_copy_long(pair) -> dict[str, str]`；守門規則同短版（顯示寬度 ≤ 34、禁詞需否定）。

## 3. 檔案

```
docs/media/manim/val_explainer/
  data.py          擴充如 §2
  copy.py          新增 COPY_LONG、render_copy_long
  scenes_short.py  不改；長版匯入其 text()、_axes()、_line()、title/pool/loop/curve 四段
  scenes_long.py   chapter_rules_segment、chapter_reference_segment、chapter_recall_segment、closing_segment；
                   Scene：ChapterRules、ChapterReference、ChapterRecall、Closing、ValLoopLong
docs/media/manim/tests/
  test_data.py     加規則對、epoch 計算、參考基線、range_text
  test_copy.py     對 COPY_LONG 跑同一套守門
  test_scene_smoke.py 加四個單章 Scene 與 ValLoopLong
docs/media/manim/render.ps1   加 -Scene 參數
docs/media/manim/README.md    加長版段落
```

## 4. 視覺

- 字型、顏色、字級沿用 `style.py`；圖表工具沿用短版（`_axes`、`_line`）。
- 第 1 章長條：張數用 `pool` 灰、epoch 標籤用 `start` 黃；規則切換用 `Transform` 讓 epoch 數字與長條高度變化，不重畫。
- 第 2 章：參考基線虛線用 `muted`；規則 A 參考基線用半透明帶狀 `Rectangle` 標示範圍。
- 第 3 章點圖：三個 arm 各自的顏色；範圍括號用細線。規則 A 到規則 B 的切換用 `Transform` 讓點移動。
- 每章之間 `FadeOut` 全部再進下一章；章名卡 2 秒。

## 5. 渲染與輸出

- `render.ps1 -Scene ValLoopLong`：`manim -qh` 出 1080p60 mp4，時長門檻 130 秒；不做 GIF；mp4 複製到 `<evidence-root>\media\val-loop-long-<UTC 時間戳>.mp4`。`-Scene ValLoopShort`（預設）行為與現在相同。
- 根目錄 README 不改；`docs/media/manim/README.md` 加長版的渲染指令與輸出位置。要放作品集頁面或 GitHub release 由 owner 決定。

## 6. 測試與檢查

- `test_data.py`：`load_rule_pair()` 兩份都載入；規則 B 的 `steps` 為 200／252／504／1,008、`epochs` 為 40／18／18／18；規則 A 的 `steps` 全為 1,000、`epochs` 為 200／72／36／18；參考基線每 seed 的 mAP 等於 summary；`range_text([0.302, 0.445], 2) == "0.30–0.45"`；缺 reference 鍵拋錯。
- `test_copy.py`：`COPY_LONG` 每句非空、顯示寬度 ≤ 34；禁詞守門；三句否定句（結尾卡兩句與第 2 章的「不能拿來說」）原文存在；數字欄位由資料填入。
- `test_scene_smoke.py`：`ChapterRules`、`ChapterReference`、`ChapterRecall`、`Closing`、`ValLoopLong` 的 `--dry_run` 回傳 0。
- 人工檢查：每章用 `-ql -s` 抽最後一幀；`-ql` 完整渲染量時長（110 到 130 秒）；1080p60 成品由 owner 看過。

## 7. 邊界

- 不動主環境、`src/`、`tests/lite`、`scripts/`；`docs/results/` 與證據目錄只讀。
- 不改短版的畫面、文字、GIF。
- 第 2 章對規則 A 參考基線的敘述只說「欠訓」與「不能拿來說 20% 已經足夠」，不與任何外部數字比較。
- mp4 不進 git；不公開資料集影像。

## 8. 完成的定義

1. `uv run pytest -q` 全部通過；設 `VAL_EXPLAINER_RENDER=1` 後冒煙測試也通過。
2. `render.ps1 -Scene ValLoopLong` 一條指令產出 mp4，時長 110 到 130 秒。
3. owner 看過 1080p60 成品。
4. spec、程式、`docs/media/manim/README.md` 更新 commit 在 `main`；push 由 owner 決定。
