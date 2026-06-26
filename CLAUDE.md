# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project documents

| File | Role |
| --- | --- |
| `README.md` | **user-facing docs** — project overview, setup steps, pipeline commands |
| `CLAUDE.md` | **AI instructions** — guidance for Claude Code when working in this repo |
| `research_implementation_log.md` | **interview/retrospective log** — research decisions and implementation challenges with rationale |
| `uspto_data_sources.md` | **API reference** — USPTO and related API field definitions, endpoints, data access policy |
| `research_ideas.md` | **research notes** — RQ brainstorming, design examination criteria (US/JP/KR), concerns (Japanese) |
| `impact_data_information.md` | **field reference** — column-by-column explanation of `patents_metadata.csv` fields |
| `WBS_until_CVPR.xlsx` | **WBS** — task schedule toward CVPR November deadline |
| `weekly_reports/` | **weekly reports** — MTG reports by date (`weekly_report_YYYYMMDD.md`) |
| `DeepResearch/01_data_availability/deep-research-report.md` | **research report** — detailed survey of design patent data availability across US/JP/KR |
| `DeepResearch/03_ml_methods/意匠・テキストマルチモーダル検索システムにおける情報量損失抑制のための相違表現抽出技術調査報告書1.md` | **tech survey** — shared/private representation disentanglement methods (DSN→MISA→DeCUR lineage) |
| `DeepResearch/03_ml_methods/意匠検索における非冗長マルチモーダル埋め込み表現学習の最先端技術調査とシステム応用1.md` | **tech survey** — modern methods post-CLIP: DeCUR / COrAL / Adaptive Barlow Twins / ReCo comparison |
| `DeepResearch/03_ml_methods/CLIP以降の画像テキスト共有表現学習と下流利用の比較研究.md` | **tech survey** — 10-paper comparison of CLIP-era shared representation learning (ALIGN, LiT, ALBEF, BLIP, SigLIP, Pic2Word, SEARLE…) |

## Research & implementation log

`research_implementation_log.md` には研究上の判断・実装上の困難と解決策を記録している。**面接・振り返り用の一次資料。**

以下のタイミングで必ず追記・更新すること:

- 新しい技術的困難を解決したとき（「なぜそうしたか」の理由を含めて）
- 研究の方向性・モデル・評価設計に関する重要な判断をしたとき
- 実験結果（Recall@K, MRR 等）が出たとき（数値と考察を記録）
- 実装上のバグ・ワークアラウンドで後で参照価値がありそうなもの

追記は「## 研究上の判断」「## 実装上の困難と解決策」「## 今後の課題」のいずれかに分類して書く。

## IMPACT dataset

**現在のプロジェクトはこのデータセットのみを使用する。** `data/processed/`, `data/raw/`, `patents_metadata.csv` は使わない。

### ディレクトリ構造

```text
data/IMPACT/
├── 2007.csv                        # メタデータ CSV（caption列あり、全年共通）
├── 2008.csv
│   ...
├── 2022.csv
├── 2007/
│   └── 2007/
│       ├── processed_xml_2007.csv  # メタデータ CSV（caption列なし）
│       └── USD<7digits>-<date>/    # 特許ごとの画像フォルダ
│           ├── USD<7digits>-<date>-D<5digits>.TIF  # 意匠図面
│           └── USD<7digits>-<date>.XML              # XML原本
├── ...
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
| `caption` | AI生成の視覚的説明文（全年の外側CSV に存在） |

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

### COrAL training on IMPACT (multimodal self-supervised)

ディレクトリ: `論文/論文再現実装/COrAL/`。著者実装をベースに、IMPACTデータ用のエンコーダ・データセットを追加した。

```bash
cd 論文/論文再現実装/COrAL

# スモークテスト（CPU、2022年データ、3バッチ）
python main_impact.py --years 2022 --max_epochs 1 --batch_size 4 --num_workers 0 --limit_batches 3

# GPUサーバーでのフル学習
python main_impact.py --years 2020 2021 2022 --max_epochs 100 --batch_size 64 --num_workers 4

# 全年（2007-2022、約44万件）
python main_impact.py --max_epochs 100 --batch_size 64 --num_workers 4
```

**新規追加ファイル（著者実装への追加分）:**

| ファイル | 役割 |
| --- | --- |
| `dataset/impact.py` | IMPACT用 Dataset / LightningDataModule。title+caption をテキスト、D00000.TIF を画像として返す。D00000.TIF の端の "Fig. X" ラベルを下部8%クロップで除去。アスペクト比ヒューリスティックで2枚並び画像を左半分に切り出す |
| `modules/dinov2_encoder.py` | `DINOv2Encoder`: `AutoModel` をラップし `last_hidden_state` (B, 257, 768) を返す。テキスト事前アライメントなしの純粋な視覚エンコーダ |
| `modules/clip_encoder.py` | `CLIPPatchEncoder`: 旧実装（CLIP ViT-B/32）。現在は `dinov2_encoder.py` に置き換え済み |
| `modules/bert_encoder.py` | `BERTTokenEncoder`: `AutoModel` をラップし `last_hidden_state` (B, 128, 768) を返す。デフォルトは `answerdotai/ModernBERT-base`。Rustバックエンドのtokenizerをlazyプロパティ化し `deepcopy` 問題を回避 |
| `main_impact.py` | エントリポイント。`MMFusion(encoders=[DINOv2Encoder, BERTTokenEncoder])` → `COrAL` を構築してTrainer.fitを呼ぶ |

**アーキテクチャ:**

- 画像: DINOv2-base (`facebook/dinov2-base`) → (B, 257, 768) パッチトークン列
- テキスト: ModernBERT-base (`answerdotai/ModernBERT-base`) → (B, 128, 768) トークン列
- 共有パス: FusionTransformer (CLS結合+self-attention) → (B, 768) → MLP → (B, 512)
- 固有パス: lin_layer 768→384 + AttentionPooling → (B, 384) → MLP → (B, 512)
- 損失: InfoNCE × 3（共有・画像固有・テキスト固有）+ 直交性損失 × 2

**Windows固有の注意:**

- `enable_progress_bar=False` を Trainer に設定済み（rich が cp932 端末でクラッシュするため）
- CLIP/BERT の HuggingFace キャッシュはシンボリックリンク警告が出るが無害

**ファイル編集の注意:**

- COrAL コードは Google Drive for Desktop で同期されており、実行環境（Colab）は Drive 上のファイルを使用する
- **必ず Drive パス（`G:\マイドライブ\松尾研究室\LLMATCH\USPTO_data_analysis\論文\論文再現実装\COrAL\`）を直接編集すること**
- ローカルパス（`C:\Users\Barre\松尾研\LLMATCH\USPTO_data_analysis\論文\論文再現実装\COrAL\`）を編集しても Colab に反映されない

### Install dependencies

```bash
pip install -r requirements.txt
pip install matplotlib  # not listed in requirements.txt but required
```

`requirements.txt` には以下が含まれる: `pandas`, `lxml`, `tqdm`, `torch`, `transformers`, `Pillow`, `faiss-cpu`, `sentence-transformers`, `accelerate`

COrAL追加依存: `pytorch-lightning`, `omegaconf`, `tensorboard`, `scikit-learn`, `torchmetrics`, `einops`

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
