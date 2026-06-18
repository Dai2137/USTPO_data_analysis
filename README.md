# USPTO Design Patent Data Analysis

IMPACTデータセット（USPTO意匠特許）を用いて、マルチモーダル検索システムの研究開発を行うプロジェクトです。

## データセット: IMPACT

`data/IMPACT/` 以下に格納されたIMPACTデータセットを使用します。

```
data/IMPACT/
├── 2020.csv                        # メタデータ CSV（caption列あり）
├── 2021.csv
├── 2022.csv
├── 2020/
│   └── 2020/
│       ├── processed_xml_2020.csv
│       └── USD<7digits>-<date>/    # 特許ごとの画像フォルダ
│           ├── USD<7digits>-<date>-D<5digits>.TIF
│           └── USD<7digits>-<date>.XML
├── 2021/ ...
└── 2022/ ...
```

### CSVの主要列

| 列 | 内容 |
| --- | --- |
| `title` | 特許タイトル |
| `id` | 特許ID（例: `D0949851`） |
| `claim` | クレームテキスト |
| `date` | 登録日（YYYYMMDD） |
| `class` | Locarnoクラス |
| `no_figs` | 図面枚数 |
| `file_names` | TIFファイル名リスト |
| `caption` | AI生成の視覚的説明文（外側CSVのみ） |

## セットアップ

```bash
pip install -r requirements.txt
pip install matplotlib  # requirements.txtに含まれないが必要
```

## 機能文生成 & マルチモーダル検索パイプライン

テキストクエリで意匠画像データベースを検索するクロスモーダル検索システムです。GPU推奨。

### Phase 1: 機能文生成（SmolVLM）

意匠図面画像からテキストの機能説明文を生成します。

```bash
# 層化サンプリング（Locarnoクラス別）
python functional_description/generate_func_desc.py --sample 1000

# テスト用（先頭5件）
python functional_description/generate_func_desc.py --sample 5

# 全件処理（未処理のみ）
python functional_description/generate_func_desc.py
```

出力: `data/processed/func_search/funcdesc.csv`（`patent_id`, `functional_description`）

### Phase 2: 埋め込み構築（CLIP + FAISS）

```bash
python functional_description/build_embeddings.py
```

出力:

- `data/processed/func_search/faiss_image.index` — CLIP画像ベクトル
- `data/processed/func_search/faiss_text.index` — テキストベクトル
- `data/processed/func_search/index_map.json` — FAISSインデックス → patent_id

### Phase 3: テキストクエリ検索

```bash
python functional_description/search.py "a glove used to protect hands during sports"
python functional_description/search.py "手を保護するスポーツ用グローブ" --topk 5
python functional_description/search.py "chair for office use" --alpha 0.7
```

`--alpha`: 画像スコアの重み（0〜1、デフォルト0.5）

## プロジェクト構成

```
USPTO_data_analysis/
├── functional_description/
│   ├── generate_func_desc.py    # Phase 1: SmolVLM で機能文生成
│   ├── build_embeddings.py      # Phase 2: CLIP埋め込み + FAISSインデックス
│   └── search.py                # Phase 3: テキストクエリ検索
├── DeepResearch/
│   ├── 01_data_availability/    # データ取得可能性調査
│   ├── 02_use_cases/            # ユースケース調査
│   └── 03_ml_methods/           # 手法調査（DeCUR、CLIP系など）
├── weekly_reports/              # 週次MTGレポート
├── CLAUDE.md                    # AI向け開発ガイド
├── research_ideas.md            # リサーチクエスチョンのメモ
├── impact_data_information.md   # データフィールド詳細
├── uspto_data_sources.md        # USPTO API リファレンス
└── requirements.txt
```

## 関連ドキュメント

| ファイル | 内容 |
| --- | --- |
| `research_ideas.md` | RQ・設計検討基準（US/JP/KR）・懸念事項 |
| `impact_data_information.md` | `patents_metadata.csv` カラム詳細 |
| `uspto_data_sources.md` | USPTO API フィールド定義・エンドポイント |
| `DeepResearch/01_data_availability/` | US/JP/KR意匠データ取得可能性の調査報告 |
| `DeepResearch/03_ml_methods/` | DeCUR・CLIP系マルチモーダル手法の技術調査 |
