# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project documents

| File | Role |
| --- | --- |
| `README.md` | **user-facing docs** — project overview, setup steps, pipeline commands |
| `CLAUDE.md` | **AI instructions** — guidance for Claude Code when working in this repo |
| `uspto_data_sources.md` | **API reference** — USPTO and related API field definitions, endpoints, data access policy |
| `research_ideas.md` | **research notes** — RQ brainstorming, design examination criteria (US/JP/KR), concerns (Japanese) |
| `impact_data_information.md` | **field reference** — column-by-column explanation of `patents_metadata.csv` fields |
| `WBS_until_CVPR.xlsx` | **WBS** — task schedule toward CVPR November deadline |
| `weekly_reports/` | **weekly reports** — MTG reports by date (`weekly_report_YYYYMMDD.md`) |
| `DeepResearch/01_data_availability/deep-research-report.md` | **research report** — detailed survey of design patent data availability across US/JP/KR |
| `DeepResearch/03_ml_methods/意匠・テキストマルチモーダル検索システムにおける情報量損失抑制のための相違表現抽出技術調査報告書1.md` | **tech survey** — shared/private representation disentanglement methods (DSN→MISA→DeCUR lineage) |
| `DeepResearch/03_ml_methods/意匠検索における非冗長マルチモーダル埋め込み表現学習の最先端技術調査とシステム応用1.md` | **tech survey** — modern methods post-CLIP: DeCUR / COrAL / Adaptive Barlow Twins / ReCo comparison |
| `DeepResearch/03_ml_methods/CLIP以降の画像テキスト共有表現学習と下流利用の比較研究.md` | **tech survey** — 10-paper comparison of CLIP-era shared representation learning (ALIGN, LiT, ALBEF, BLIP, SigLIP, Pic2Word, SEARLE…) |

## IMPACT dataset

**現在のプロジェクトはこのデータセットのみを使用する。** `data/processed/`, `data/raw/`, `patents_metadata.csv` は使わない。

### ディレクトリ構造

```text
data/IMPACT/
├── 2020.csv                        # メタデータ CSV（caption列あり）
├── 2021.csv
├── 2022.csv
├── 2020/
│   └── 2020/
│       ├── processed_xml_2020.csv  # メタデータ CSV（caption列なし）
│       └── USD<7digits>-<date>/    # 特許ごとの画像フォルダ
│           ├── USD<7digits>-<date>-D<5digits>.TIF  # 意匠図面
│           └── USD<7digits>-<date>.XML              # XML原本
├── 2021/
│   └── 2021/ ...
└── 2022/
    └── 2022/ ...
```

### CSVの列

| 列 | 内容 |
| --- | --- |
| `title` | 特許タイトル |
| `id` | 特許ID（例: `D0949851`） |
| `claim` | クレームテキスト |
| `date` | 登録日（YYYYMMDD） |
| `class` | Locarnoクラス |
| `class_search` | 検索クラスリスト |
| `inv_country` | 発明者の国 |
| `no_figs` | 図面枚数 |
| `sheets` | シート数 |
| `file_names` | TIFファイル名リスト |
| `fig_desc` | 図面説明文リスト |
| `caption` | AI生成の視覚的説明文（**外側CSVのみ**: `2020.csv` / `2021.csv` / `2022.csv`） |

### 画像フォルダとCSVの紐付け

- CSV `id`: `D0949851` → 数字7桁: `0949851`
- フォルダ名: `USD0949851-20220426` → `USD`以降の7桁: `0949851`
- 最初の画像（`D00000.TIF`）が表紙図面

## Running scripts

### Functional description & multimodal search (3-phase pipeline)

IMPACTデータセットを使用。GPU推奨（Phase 1はSmolVLM、Phase 2はCLIP）:

```bash
# Phase 1: VLMで意匠画像から機能文を生成
python functional_description/generate_func_desc.py --sample 1000  # 層化サンプリング1000件
python functional_description/generate_func_desc.py --sample 5     # テスト（先頭5件）
python functional_description/generate_func_desc.py                 # 全件（未処理のみ）

# Phase 2: CLIP画像埋め込み + テキスト埋め込みをFAISSインデックスに保存
python functional_description/build_embeddings.py

# Phase 3: テキストクエリでマルチモーダル検索
python functional_description/search.py "a glove used to protect hands during sports"
python functional_description/search.py "手を保護するスポーツ用グローブ" --topk 5
python functional_description/search.py "chair for office use" --alpha 0.7  # alpha: 画像重み(0〜1)
```

出力先: `data/processed/func_search/`

- `funcdesc.csv` — `patent_id`, `functional_description`（Phase 1出力）
- `faiss_image.index` — CLIP画像ベクトルのFAISSインデックス（Phase 2出力）
- `faiss_text.index` — 機能文テキストベクトルのFAISSインデックス（Phase 2出力）
- `index_map.json` — FAISSの行番号 → patent_idの対応表（Phase 2出力）

### Install dependencies

```bash
pip install -r requirements.txt
pip install matplotlib  # not listed in requirements.txt but required
```

`requirements.txt` には以下が含まれる: `pandas`, `lxml`, `tqdm`, `torch`, `transformers`, `Pillow`, `faiss-cpu`, `sentence-transformers`, `accelerate`

## Architecture

The project is a linear ETL + analysis pipeline with no shared library code. Aside from the base pipeline, there are three independent data-enrichment branches (citations, OA citations, OA texts) and a multimodal search system.

### Base data flow

```text
data/*.tar
  → extract_tar.py      → data/I2026xxxx/ (extracted tar contents)
  → folder_organize.py  → deletes non-DESIGN and *SUPP subdirs in place
  → unzip.py            → data/processed/USD*/  (XML + TIF per patent)
                           data/raw/I2026xxxx/   (original folders moved here)
  → process_xml.py      → data/processed/patents_metadata.csv
```

### Analysis branch

```text
data/processed/patents_metadata.csv
  → locarno_distribution.py  → data/processed/locarno_*.png + *.csv
  → no_figs_distribution.py  → data/processed/no_figs_*.png
```

### Citation data branches

```text
data/processed/patents_metadata.csv
  → fetch_citations.py      → data/processed/citations/citations.json
                               data/processed/citations/citation_pairs.csv
  → fetch_oa_citations.py   → data/processed/oa_citations/oa_citations.json
                               data/processed/oa_citations/oa_citation_pairs.csv
  → fetch_oa_texts.py       → data/processed/oa_texts/oa_texts.json
                               data/processed/oa_texts/oa_text_records.csv
```

### Multimodal search pipeline

Goal: text query → image-only database cross-modal retrieval (no text annotations on the DB side).

```text
data/processed/patents_metadata.csv  +  data/processed/USD*/*.TIF

  Phase 1 — Training data preparation
  → generate_func_desc.py  [SmolVLM-500M-Instruct, local]
       → data/processed/func_search/funcdesc.csv   (patent_id, functional_description)

  Phase 2 — Embedding model construction + image DB
  → build_embeddings.py    [baseline: CLIP image encoder + sentence-transformers]
       → data/processed/func_search/faiss_image.index   (512-dim, all patent images)
       → data/processed/func_search/faiss_text.index    (768-dim, funcdesc text; baseline only)
       → data/processed/func_search/index_map.json      (FAISS row → patent_id)
       Target: fine-tune shared/unique-separated encoder (DeCUR-based); image-only FAISS DB

  Phase 3 — Text-to-image cross-modal search
  → search.py              [baseline: RRF over image + text FAISS indexes]
       input:  text query (functional description; may or may not include shape/geometry)
       output: stdout (Top-K ranked patent list)
       Target: text encoder → shared vector → image-only FAISS DB → Top-K
```

## Key facts

- All paths are resolved relative to `__file__` with `Path(__file__).resolve().parent`, so scripts work from any working directory.
- `data/` and `*.csv` are gitignored — no data is committed.
- `locarno_class` is stored as a raw string like `"02-01"`. Both analysis scripts use the same `extract_major_class()` helper (duplicated, not shared) that strips the leading two digits as the major class.
- `patents_metadata.csv` is written with `utf-8-sig` (BOM) for Excel compatibility. Same for all output CSVs.
- **fetch_citations.py** uses the USPTO Enriched Citations API (`enriched_cited_reference_metadata/v2`). Queries by `citedDocumentIdentifier` (= `patent_id`). Flags whether the citing patent is also in the dataset (`citing_in_dataset`).
- **fetch_oa_citations.py** uses the USPTO OA Citations API (`oa/oa_citations/v2/records`). Queries by `parsedReferenceIdentifier` (numeric part of patent ID, e.g. `"123456"` for `"D123456"`). Records examiner-cited vs. applicant-cited reference flags.
- **fetch_oa_texts.py** uses the USPTO OA Actions API (`oa/oa_actions/v1/records`). Queries by `patentNumber` (full ID, e.g. `"D123456"`). Returns Office Action full-text including rejection reason texts (`section101/102/103/112RejectionText`). `sections.*` fields are flattened in the CSV output.
- All three fetch scripts use resume logic: a `.txt` log file tracks processed IDs to allow safe restart. `--no-skip-existing` forces full reprocessing.
- **Phase 1 (generate_func_desc.py)**: Uses `HuggingFaceTB/SmolVLM-500M-Instruct` locally (no API key needed). Stratified sampling by Locarno major class with `--sample N`. Skips already-processed patents.
- **Phase 2 (build_embeddings.py)**: Baseline uses `openai/clip-vit-base-patch32` for image embeddings (512-dim) and `sentence-transformers/paraphrase-multilingual-mpnet-base-v2` for text embeddings (768-dim), stored in separate FAISS flat indexes. Target: fine-tune a shared/unique-separated encoder (DeCUR-based) and build an image-only FAISS DB.
- **Phase 3 (search.py)**: Baseline blends image-FAISS and text-FAISS ranks via Reciprocal Rank Fusion (`score = alpha * 1/(1+img_rank) + (1-alpha) * 1/(1+txt_rank)`). Target: text query → fine-tuned text encoder → image-only FAISS DB → Top-K (no text index on DB side).
