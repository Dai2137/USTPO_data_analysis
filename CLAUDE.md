# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project documents

| File | Role |
| --- | --- |
| `README.md` | **user-facing docs** — project overview, setup steps, pipeline commands |
| `CLAUDE.md` | **AI instructions** — guidance for Claude Code when working in this repo |
| `uspto_data_sources.md` | **API reference** — USPTO and related API field definitions, endpoints, data access policy |
| `research_ideas.md` | **research notes** — RQ brainstorming, concerns, design ideas (Japanese) |
| `DeepResearch/deep-research-report.md` | **research report** — detailed survey of design patent data availability across US/JP/KR |

## Running scripts

Data processing pipeline — must be run in this order after placing `.tar` files in `data/`:

```bash
python "Data processing/extract_tar.py"   # 1. Unpack .tar files
python "Data processing/folder_organize.py" # 2. Keep only DESIGN subfolders
python "Data processing/unzip.py"          # 3. Unzip patents into data/processed/
python "Data processing/process_xml.py"   # 4. Parse XML → data/processed/patents_metadata.csv
```

Analysis scripts (require `data/processed/patents_metadata.csv`):

```bash
python locarno_distribution.py   # Locarno major-class counts + bar chart
python no_figs_distribution.py   # no_figs histograms (all + per Locarno class)
```

Citation fetching (requires `data/processed/patents_metadata.csv` and `.env` with `MY_API_KEY`):

```bash
python fetch_citations.py                # 引用データを取得（処理済みをスキップ）
python fetch_citations.py --no-skip-existing  # 全件再処理
```

出力先: `data/processed/citations/`
- `citations.json` — 特許IDごとのAPIレスポンス生データ
- `citation_pairs.csv` — patents_metadata.csv と結合用のペア形式（`cited_patent_id`, `citing_publication_number`, `citing_in_dataset`, `citation_category_code` 等）

Install dependencies:

```bash
pip install -r requirements.txt
pip install matplotlib  # not listed in requirements.txt but required
```

## Architecture

The project is a linear ETL + analysis pipeline with no shared library code.

**Data flow:**

```
data/*.tar
  → extract_tar.py     → data/I2026xxxx/ (extracted tar contents)
  → folder_organize.py → deletes non-DESIGN and *SUPP subdirs in place
  → unzip.py           → data/processed/USD*/  (XML + TIF per patent)
                          data/raw/I2026xxxx/   (original folders moved here)
  → process_xml.py     → data/processed/patents_metadata.csv
  → locarno_distribution.py / no_figs_distribution.py → data/processed/*.png + *.csv
  → fetch_citations.py  → data/processed/citations/citations.json
                           data/processed/citations/citation_pairs.csv
```

**Key facts:**
- All paths are resolved relative to `__file__` with `os.path.abspath`, so scripts work from any working directory.
- `data/` and `*.csv` are gitignored — no data is committed.
- `locarno_class` is stored as a raw string like `"02-01"`. Both analysis scripts use the same `extract_major_class()` helper (duplicated, not shared) that strips the leading two digits as the major class.
- `patents_metadata.csv` is written with `utf-8-sig` (BOM) for Excel compatibility.
- `fetch_citations.py` uses the USPTO Enriched Citations API (`enriched_cited_reference_metadata/v2`). It queries by `citedDocumentIdentifier` (= `patent_id`) and flags whether the citing patent (`publicationNumber`) is also in the dataset (`citing_in_dataset`). `citation_pairs.csv` is also written with `utf-8-sig`.
