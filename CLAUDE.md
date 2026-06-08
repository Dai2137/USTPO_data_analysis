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
| `DeepResearch/deep-research-report.md` | **research report** — detailed survey of design patent data availability across US/JP/KR |
| `DeepResearch/意匠・テキストマルチモーダル検索システムにおける情報量損失抑制のための相違表現抽出技術調査報告書1.md` | **tech survey** — shared/private representation disentanglement methods for multimodal search |

## Running scripts

### Data processing pipeline

Must be run in this order after placing `.tar` files in `data/`:

```bash
python "Data processing/extract_tar.py"    # 1. Unpack .tar files
python "Data processing/folder_organize.py" # 2. Keep only DESIGN subfolders
python "Data processing/unzip.py"           # 3. Unzip patents into data/processed/
python "Data processing/process_xml.py"    # 4. Parse XML → data/processed/patents_metadata.csv
```

### Analysis scripts

Require `data/processed/patents_metadata.csv`:

```bash
python locarno_distribution.py    # Locarno major-class counts + bar chart
python no_figs_distribution.py    # no_figs histograms (all + per Locarno class)
```

### Enriched citation fetching

Require `data/processed/patents_metadata.csv` and `.env` with `MY_API_KEY`:

```bash
python fetch_citations.py                 # 引用データを取得（処理済みをスキップ）
python fetch_citations.py --no-skip-existing  # 全件再処理
```

出力先: `data/processed/citations/`

- `citations.json` — 特許IDごとのAPIレスポンス生データ
- `citation_pairs.csv` — `cited_patent_id`, `citing_publication_number`, `citing_in_dataset`, `citation_category_code` 等

### Office Action citation fetching

```bash
python fetch_oa_citations.py                 # OA引用データを取得（処理済みをスキップ）
python fetch_oa_citations.py --no-skip-existing  # 全件再処理
```

出力先: `data/processed/oa_citations/`

- `oa_citations.json` — 特許IDごとのAPIレスポンス生データ
- `oa_citation_pairs.csv` — `cited_patent_id`, `citing_application_number`, `examinerCitedReferenceIndicator` 等

### Office Action text fetching

```bash
python fetch_oa_texts.py                 # OAテキストを取得（処理済みをスキップ）
python fetch_oa_texts.py --no-skip-existing  # 全件再処理
```

出力先: `data/processed/oa_texts/`

- `oa_texts.json` — 特許IDごとのAPIレスポンス生データ
- `oa_text_records.csv` — 拒絶理由テキスト等の主要フィールド（`sections.*` 展開済み）

### Functional description & multimodal search (3-phase pipeline)

Require `data/processed/patents_metadata.csv`. GPU推奨（Phase 1はSmolVLM、Phase 2はCLIP）:

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

```text
data/processed/patents_metadata.csv  +  data/processed/USD*/*.TIF
  → generate_func_desc.py  [Phase 1: SmolVLM-500M-Instruct]
       → data/processed/func_search/funcdesc.csv

  → build_embeddings.py    [Phase 2: CLIP + sentence-transformers]
       → data/processed/func_search/faiss_image.index
       → data/processed/func_search/faiss_text.index
       → data/processed/func_search/index_map.json

  → search.py              [Phase 3: query → Top-K patents]
       input:  text query string
       output: stdout (ranked patent list)
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
- **Phase 2 (build_embeddings.py)**: Uses `openai/clip-vit-base-patch32` for image embeddings (512-dim) and `sentence-transformers` for text embeddings (768-dim). Stores in separate FAISS flat indexes.
- **Phase 3 (search.py)**: Blends image and text similarity scores with `--alpha` weight (default 0.5). Higher alpha = more weight to image similarity.
