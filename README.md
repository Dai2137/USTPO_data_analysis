# USPTO Design Patent Data Analysis

USPTOが公開するデザイン特許データ（TAR形式）を取得・処理し、Locarnoクラス分布や図面枚数分布を分析するパイプラインです。

## データソース

[USPTO Bulk Data](https://data.uspto.gov/bulkdata/datasets/ptgrdt) から以下を取得します。

- **Patent Grant Full Text Data with Embedded TIFF Images (Grant Red Book based on WIPO ST.36) - XML (JAN 2001 - PRESENT)**
- ファイル形式: `.tar`（週次リリース）

## プロジェクト構成

```
USPTO_data_analysis/
├── data/
│   ├── I20260106.tar          # USPTOからダウンロードしたTARファイル
│   ├── I20260113.tar
│   ├── ...
│   ├── raw/                   # unzip.py実行後に移動された展開済みフォルダ
│   └── processed/
│       ├── USD**/             # 特許ごとの展開フォルダ (XML + TIF)
│       └── patents_metadata.csv  # process_xml.py が生成するメタデータ
├── Data processing/
│   ├── extract_tar.py         # TARファイルを展開
│   ├── folder_organize.py     # DESIGNフォルダ以外を削除
│   ├── unzip.py               # ZIPを processed/ に展開
│   └── process_xml.py         # XMLを解析してCSVを生成
├── locarno_distribution.py    # Locarno大分類の分布を集計・可視化
├── no_figs_distribution.py    # 図面枚数の分布を集計・可視化
└── requirements.txt
```

## セットアップ

```bash
pip install -r requirements.txt
```

`requirements.txt` には `pandas`, `lxml`, `tqdm`, `matplotlib` が必要です（`matplotlib` は別途インストールしてください）。

## データ処理パイプライン

`data/` 直下にTARファイルを配置した後、以下の順に実行します。

### 1. TARを展開

```bash
python "Data processing/extract_tar.py"
```

`data/*.tar` を検出し、同名フォルダに展開します（展開済みはスキップ）。

### 2. DESIGNフォルダ以外を削除

```bash
python "Data processing/folder_organize.py"
```

各週次フォルダ内の `DESIGN` 以外のサブフォルダ（UTILITY, PLANTなど）と `*SUPP` フォルダを削除します。

### 3. ZIPを展開して processed/ に配置

```bash
python "Data processing/unzip.py"
```

`DESIGN/*.ZIP` を `data/processed/<特許番号>/` に展開します。元の週次フォルダは `data/raw/` に移動されます。

展開後のフォルダ構成例:
```
data/processed/
└── USD0939806-20220104/
    ├── USD0939806-20220104.xml
    └── USD0939806-20220104-D00001.TIF
```

### 4. XMLを解析してCSVを生成

```bash
python "Data processing/process_xml.py"
```

`data/processed/` 以下の全XMLを解析し、`data/processed/patents_metadata.csv` を生成します。

**CSVのカラム:**

| カラム | 内容 |
|---|---|
| `title` | 発明名称 |
| `patent_id` | 特許番号 |
| `publication_date` | 公開日 |
| `application_date` | 出願日 |
| `claim` | クレーム |
| `locarno_class` | Locarno分類 |
| `us_class` | US分類 |
| `class_search` | 検索分類 |
| `applicant_org` | 出願人（組織） |
| `assignee_org` | 譲受人（組織） |
| `inventor_names` | 発明者名 |
| `inventor_countries` | 発明者国 |
| `applicant_countries` | 出願人国 |
| `no_figs` | 図面枚数 |
| `sheets` | 図面シート数 |
| `file_names` | TIFファイル名 |
| `fig_desc` | 図面の説明 |
| `patent_folder` | フォルダ名 |

## 分析スクリプト

### Locarno大分類の分布

```bash
python locarno_distribution.py
```

`locarno_class` の先頭2桁（大カテゴリ）ごとの件数を集計します。

**出力:**
- `data/processed/locarno_major_distribution.csv`
- `data/processed/locarno_major_distribution.png`

### 図面枚数の分布

```bash
python no_figs_distribution.py
```

`no_figs`（図面枚数）の分布を全体およびLocarno大分類別に可視化します。

**出力:**
- `data/processed/no_figs_hist_all.png` — 全特許の図面枚数ヒストグラム
- `data/processed/no_figs_hist_by_locarno.png` — Locarno大分類別のサブプロット