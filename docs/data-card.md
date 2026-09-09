# Data card: RDD2022 Czech train subset (v0.2-lite)

本文件記錄 v0.2-lite 使用的唯一資料來源與其取得過程。影像、標註、壓縮檔一律不進 Git。

## 來源與授權

- 資料集：RDD2022（Sekilab RoadDamageDetector，CRDDC 2022 釋出）。
- 官方 README 列的單國 S3 連結（`.../Country_Specific_Data_CRDDC2022/RDD2022_Czech.zip`）於 2026-09-09 對該 bucket 所有物件回 HTTP 403，已不可用。
- 實際來源：README 同樣指向的官方 FigShare 鏡像。
  - 文章：https://figshare.com/articles/dataset/RDD2022_-_The_multi-national_Road_Damage_Dataset_released_through_CRDDC_2022/21431547
  - DOI：`10.6084/m9.figshare.21431547.v1`
  - 檔案：`RDD2022_released_through_CRDDC2022.zip`，下載 URL `https://ndownloader.figshare.com/files/38030910`
- 授權：FigShare 頁面標示 CC BY 4.0；README 標示 CC BY-SA 4.0。本專案沿用 v0.1 設計規格的保守處理，以 CC BY-SA 4.0 對待，保留來源標示與 share-alike 義務。
- 引用：Arya, D., Maeda, H., Ghosh, S. K., Toshniwal, D., Sekimoto, Y. RDD2022: A multi-national image dataset for automatic Road Damage Detection. FigShare, 2022.

## 下載與驗證（2026-09-09，由 owner 授權本 session 代為執行）

| 項目 | 值 |
|---|---|
| 開始 / 結束（UTC） | 2026-09-09T05:39:44Z / 2026-09-09T06:04:28Z |
| HTTP | 200，1,483.8 秒，約 8.9 MB/s |
| 大小 | 13,264,172,619 bytes |
| MD5 | `b62bd51d2ffcfaa76c60f234f0cc2bb3`（與 FigShare API `computed_md5` 一致） |
| SHA-256 | `5d230a2941e8f2ac5fbca1a0faddee393314368dd17f9304effc11ec532845b6` |
| 存放 | `<data-root>\rdd2022\`（依私有證據根目錄規則保留不重打包） |

外層檔只含七個國別 zip（`RDD2022/{China_Drone,China_MotorBike,Czech,India,Japan,Norway,United_States}.zip`）。只抽出 `RDD2022/Czech.zip`，其餘六國不解出、不使用。

| 項目 | 值 |
|---|---|
| `Czech.zip` 大小 | 257,117,218 bytes |
| `Czech.zip` SHA-256 | `94c65a4e6cfed187b193ba967f0a2b16bd4287dfe313d0962f3711afce75bf1d` |
| 解出前綴 | `Czech/train/`（`images/*.jpg`、`annotations/xmls/*.xml`） |
| 解出檔案數 | 5,658（2,829 影像 + 2,829 XML） |
| 未解出 | `Czech/test/`（無標註，協定不用） |
| 紀錄檔 | `rdd2022\download.log`、`rdd2022\czech-extraction.json` |

## manifest（`val lite manifest`，2026-09-09）

`--archive-sha256` 綁定的是 `Czech.zip` 的 SHA-256（manifest 直接來源）；外層檔的雜湊是來源鏈錨點，記於上表。

| 項目 | 值 |
|---|---|
| manifest SHA-256 | `3d961040969e9008b1c534740f5c1c5b4f019c6394db7170acd99cddd8f9388d` |
| 影像 | 2,829（全部 600×600） |
| 有效框 | 1,745：D00 988、D10 399、D20 161、D40 197 |
| 捨棄框（未知標籤） | 0 |
| 完全重複 alias | 0 |
| 負樣本（無有效框） | 1,757（62.1%） |
| 切分 | test 574 張（327 框：D00 194、D10 62、D20 27、D40 44；負樣本 365）；pool 2,255 張（1,418 框：D00 794、D10 337、D20 134、D40 153；負樣本 1,392） |
| 覆蓋審核 | 通過（test 每類 ≥ 20 框；pool ≥ 1,500 張） |
| 預算 B(p) | 2% = 46、5% = 113、10% = 226、20% = 451 |
| `split_group_id` fallback 率 | 100%（Czech 檔名為連續編號，無拍攝段資訊） |
| 存放 | `<evidence-root>\lite\data\czech\{manifest.json, public-pool.json}` |

值得注意：Czech 子集有 62% 的影像沒有任何四類損壞框。2% 起點的 46 張影像預期只有十幾張帶框，基線 mAP 會很低；這是資料本身的性質，不是流程錯誤。
