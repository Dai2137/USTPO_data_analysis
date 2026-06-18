# 週次MTGレポート — 2026-06-11

## 1. 今週やったこと

### 1-1. ストーリー作成

**やりたいこと：**

- **クエリ**：テキスト（機能・用途文脈を含む機能文。形状・幾何情報が含まれる場合と含まれない場合がある）
- **検索データベース**：画像のみ（全意匠データに VLM で説明文を付与するのは莫大なコストのため、テキストなし）

→ テキストクエリから画像データベースを検索するクロスモーダル検索システムを作りたい。

**前提（仮定）：**

テキストと画像には**共通部分**と**固有部分**がある。

| モダリティ | 共通部分 | 固有部分 |
| --- | --- | --- |
| テキスト | 製品の概念 | 製品名，機能・用途文脈 |
| 画像 | 製品の概念 | 形状・幾何構造 |

**解決の方向性：**

1. **Embedding モデルの構築**：共通部分と固有部分を分けて表現できるベクトル空間が好ましい。
   1. Embeddingモデル
      1. Embeddingモデルをフルスクラッチで学習→現実的ではない
      2. 既存のマルチモーダルEmbeddingモデル(CLIP・DesignCLIP・PatentCLIPなど)の重みを初期値とし学習データ(IMPACTなど(画像, 機能文）ペア))でfine-tuning
      3. マルチモーダルEmbeddingモデルAPIをzero-shotで利用(比較手法)
2. **検索アルゴリズムの構築**：学習済みの Embeddingモデル を使い、テキストクエリから画像データベース内の類似意匠をマッチさせる。

CLIP 式の単純なアライメントでは画像とテキストを「似すぎる」ベクトルに揃えてしまい、各モダリティの固有部分が失われる。そのため、共通・固有を分離する手法のサーベイを実施（→ 1-2）。

**このストーリーに基づくシステム構成（Phase 1 / 2 / 3）：**

| フェーズ | 内容 | ステータス |
| --- | --- | --- |
| **Phase 1**：学習データ準備 | VLM で意匠画像 → 機能文を生成し（画像, 機能文）ペアを作成 ．or IMPACTをそのまま使う（学習データ量は増やせるが，機能的側面をテキストが表現できているか不明）．| 1,000 件 生成済み |
| **Phase 2**：Embedding モデル構築 | 既存モデルを fine-tuning し共有・固有分離空間を学習。全意匠画像をエンコードし FAISS DB を構築 | 未着手（設計中） |
| **Phase 3**：クロスモーダル検索 | テキストクエリ → text encoder → FAISS 画像 DB を検索 → Top-K 意匠を返す | 未着手 |

---

### 1-2. 文献調査：Phase 2 改善に向けた技術サーベイ

#### (a) 旧世代論文 6 本の概要を把握

これらの論文が提案する損失関数は、下記の3項に整理できる：

$$\mathcal{L}_{\text{total}} = \alpha\mathcal{L}_{\text{align}} + \beta\mathcal{L}_{\text{diff}} + \gamma\mathcal{L}_{\text{diversity}}$$

| 項 | 役割 | 対応論文 |
| --- | --- | --- |
| $\mathcal{L}_{\text{align}}$ | 共有サブスペース同士を引き寄せる（画像とテキストの共通部分を揃える） | ①DSN、③MISA、④ |
| $\mathcal{L}_{\text{diff}}$ | 共有ベクトルと固有ベクトルを直交させる（共通部分と固有部分が混ざらないようにする） | ①DSN、③MISA、④ |
| $\mathcal{L}_{\text{diversity}}$ | 固有ベクトルの各次元間の冗長性を削減する（固有成分が潰れてゼロになるのを防ぐ） | ②Barlow Twins、⑤CLUB |

| # | 論文 | 会議/年 | 所感 |
| --- | --- | --- | --- |
| 1 | Domain Separation Networks | NeurIPS 2016 | $\mathcal{L}_{\text{diff}}$ の元祖。CLIP 以前の先行研究 |
| 2 | Barlow Twins | ICML 2021 | Modal Collapse 防止の現代標準 |
| 3 | MISA | ACM MM 2020 | 画像・音声・テキストへの直接適用例 |
| 4 | Disentangled Cross-Modal Retrieval | ACM MM 2021 | 本研究に最も直近の先行研究 |
| 5 | Disentangled MM Learning for Rec | WSDM 2023 | CLUB を $\mathcal{L}_{\text{diversity}}$ に使用 |
| 6 | Cross-Modal Disentanglement Networks | — | DSN の CLIP 空間拡張 |

→ 6 本中 4 本はマルチモーダルが流行る前の手法。CLIP 登場以降の最先端を別途調査が必要と判断。

#### (b) CLIP 以降（2021〜2026）の最先端手法サーベイ

DeepResearch として以下 2 本のレポートを作成・格納（`DeepResearch/03_ml_methods/`）：

| レポート | 主な内容 |
| --- | --- |
| `意匠・テキストマルチモーダル検索システムにおける情報量損失抑制のための相違表現抽出技術調査報告書1` | DSN→MISA→DeCUR の系譜、損失関数の数理、意匠データへの適用可否 |
| `意匠検索における非冗長マルチモーダル埋め込み表現学習の最先端技術調査とシステム応用1` | CLIP 以降の最新手法（DeCUR / COrAL / Adaptive Barlow Twins / ReCo）の詳細比較 |

主要調査対象：

| 手法 | 論文名 | 発表 | 概要 |
| --- | --- | --- | --- |
| **DeCUR** | Decoupling Common and Unique Representations for Multimodal Self-supervised Learning | ECCV 2024 Oral (arXiv:2309.05300) | Barlow Twins の自然なマルチモーダル拡張。共通次元と固有次元を明示的に分割し直交化 |
| **COrAL** | Orthogonalized Multimodal Contrastive Learning with Asymmetric Masking for Structured Representations | arXiv:2602.14983 (2026) | Redundant / Unique / Synergistic の 3 成分分解。非対称マスキングで相乗情報を抽出 |
| **Adaptive Barlow Twins** | A Multimodal Approach to Heritage Preservation in the Context of Climate Change | arXiv:2510.14136 (2025) ※遺産保存タスクの論文内の損失変種 | ターゲット相関行列を部分アライメントに緩和。画像・テキストが「似すぎない」制約を自然に組み込む |
| **ReCo** | Relaxing Contrastiveness | — (論文名未確認) | 既に直交している負例へのペナルティを除去。潜在空間の自由度を保存 |

**意匠データへの示唆：**
- **意匠では「形状と機能は連動する」ため、画像・テキスト固有成分を完全に無相関化することは不適切**
- DeCUR の「共通次元のアライメント ＋ 固有次元の直交化」は意匠に素直に当てはまる
- COrAL の「相乗（Synergistic）情報」の抽出は、意匠の「外観から機能が示唆される」構造とフィットする可能性

#### (c) テキスト＋画像を両方扱う共有・固有分離手法（追記 2026-06-14）

上記 (b) の手法のうち **DeCUR** は RGB+Depth や RGB+Audio など画像系センサー間の組み合わせを想定しており、テキストモダリティを直接扱う設計ではない。
一方 **COrAL・FLAVA・FactorCL** はテキスト＋画像を明示的に扱う。本研究の設定（テキストクエリ → 画像 DB）には以下が直接関連する。

| 手法 | 論文名 | 発表 | 共有・固有の扱い |
| --- | --- | --- | --- |
| **COrAL** | Orthogonalized Multimodal Contrastive Learning with Asymmetric Masking for Structured Representations | arXiv:2602.14983 (2026) | Redundant（共有）・Unique（固有）・Synergistic（相乗）の3成分に分解。非対称マスキングで相乗情報を抽出。テキスト＋画像に適用 |
| **FLAVA** | FLAVA: A Foundational Language And Vision Alignment Model | CVPR 2022 (Meta AI) | ユニモーダル目標（画像のみ MIM ＋ テキストのみ MLM）でモダリティ**固有**表現を保持し、マルチモーダル目標（ITC＋ITM＋MMLM）で**共有**表現を整合。テキスト・画像の両エンコーダに独立した固有成分が残る |
| **FactorCL** | Factorized Contrastive Learning: Going Beyond Multi-view Redundancy | NeurIPS 2023 | 情報理論に基づき Content（モダリティ間**共有**情報）と Style（モダリティ**固有**情報）を明示的に因子化。テキスト＋画像ペアに適用可能。共有・固有を同時に最大化する損失設計 |

**本研究との対応：**

| 本研究の概念 | FLAVA | FactorCL |
| --- | --- | --- |
| 共通部分（製品の概念） | マルチモーダル目標（ITC/ITM）が整合 | Content 成分が対応 |
| テキスト固有部分（機能・用途文脈） | テキストエンコーダの MLM 目標が保持 | Style (text) 成分が対応 |
| 画像固有部分（形状・幾何構造） | 画像エンコーダの MIM 目標が保持 | Style (image) 成分が対応 |

→ (b) の手法と組み合わせる場合、**損失関数の設計** は DeCUR / COrAL を参考にしつつ、**モデル骨格（エンコーダ構成）** は FLAVA 的なテキスト＋画像の2エンコーダ構成を採用するアプローチが現実的。

---

### 1-3. CVPR 向け WBS 作成

`WBS_until_CVPR.xlsx` を作成し、11 月〆切に向けたタスク管理を開始。

---

### 1-4. Phase 1 実行

1,000 件層化サンプルの機能文生成を実行済み。

| 環境 | 1件あたり | 1,000 件合計 |
| --- | --- | --- |
| CPU（現状） | ~6〜9 分 | **約 4〜6 日** |

6/11 時点で完了。

---

## 2. 現在の課題

### Phase 1 — 学習データの機能文をどう作るか（未決）

Phase 2 の fine-tuning に使う（画像, 機能文）ペアのテキスト品質が学習結果を左右する。

| 選択肢 | メリット | 懸念 |
| --- | --- | --- |
| **IMPACT データセットのキャプション流用** | 既存データをそのまま使える | 記述が一般的すぎる（「歯ブラシは歯を磨くもの」レベル）。固有の機能情報が薄い |
| **現行の SmolVLM プロンプトで 1,000 件生成** | 実装済み・実行中。用途文脈（3 点構成）を引き出す設計 | プロンプトの品質が十分か未検証。CPU 環境では全件生成に数日 |

→ **要決定**：いずれかを選ぶか、両者を比較評価するか。

### Phase 2 — Embedding モデル設計の決断（未決）

| 選択肢 | メリット | 懸念 |
| --- | --- | --- |
| **DeCUR ベース** | Barlow Twins の素直な拡張、コード公開済み | 固有次元の完全直交化が意匠に合うか？（形状↔機能は連動する） |
| **COrAL ベース** | 相乗情報を明示的に抽出、2026 年最新 | arXiv プレプリント（査読未完）、実装難度高 |
| **Adaptive Barlow Twins** | 部分アライメントで連動性を保ちつつ冗長性削減 | 実装例が少ない |
| **zero-shot（既存 API 利用）** | 実装コスト最小 | 共有・固有の分離は期待できない |

---

## 3. 来週の予定

1. **Phase 1 完了確認**：`funcdesc.csv` の件数確認・品質チェック（50 件程度を目視）
2. **Phase 1 テキスト方針を決定**：IMPACT キャプション vs 現行 SmolVLM プロンプト
3. **Phase 2 設計を決定**：DeCUR ベースを軸に意匠向けカスタマイズ方針を確定
4. **学会スケジュール確認**：CVPR 11 月〆切に向けて実験計画を立てる

---

## 4. 参考：システム構成（Phase 1 / 2 / 3）

### Phase 1 — 学習データ準備：機能文生成（`generate_func_desc.py`）

**役割：** Phase 2 の fine-tuning 用に（画像, 機能文）ペアを作る。

**モデル:** `HuggingFaceTB/SmolVLM-500M-Instruct`（500M params、完全ローカル・APIキー不要）

**入力:** TIF 図面 + `title` + `locarno_class`（`patents_metadata.csv`）

**現行プロンプト:**

```text
This is a design patent drawing for a product titled '{title}'
(Locarno classification: {locarno}).
In 2-3 sentences describe:
(1) what this product is,
(2) how a user would use it in daily life,
(3) any notable functional features visible in the design.
```

**出力例（動作確認済み）:**

| patent_id | Locarno | 生成された機能文 |
| --- | --- | --- |
| D1111777 | 0610 | "A curtain position limiting device is a device that restricts the movement of a curtain. It is a vertical column with a cylindrical body and a cylindrical cap. The cylindrical body is connected to the cylindrical cap by a threaded rod." |
| D1110594 | 2705 | "(1) The product is a lighter. (2) A user would use it in daily life by holding it in their hand to light a cigarette. (3) Notable functional features include a handle on the top for carrying and a base for attaching to a lighter holder." |

**サンプリング:** Locarno 大分類ごとに比例配分（層化サンプリング）、`--sample 1000` で 1,000 件

**実行コマンド:**

```bash
python functional_description/generate_func_desc.py --sample 1000
python functional_description/generate_func_desc.py --sample 5     # テスト
python functional_description/generate_func_desc.py                 # 全件（未処理のみ）
```

**出力先:** `data/processed/func_search/funcdesc.csv`（`patent_id`, `functional_description`）

---

### Phase 2 — Embedding モデル構築・画像 DB 作成（`build_embeddings.py`）

**役割：** Phase 1 の（画像, 機能文）ペアで既存モデルを fine-tuning し、共有・固有分離空間を学習。全意匠画像をエンコードして検索用 FAISS DB を構築する。

**現状（ベースライン）:**

```text
funcdesc.csv + TIF ファイル
  → CLIP image encoder  → 512-dim → faiss_image.index
  → ST text encoder     → 768-dim → faiss_text.index
```

**改善方針（検討中）:** DeCUR ベースで image encoder / text encoder を共同 fine-tuning し、共通次元・固有次元を分離。全意匠画像を image encoder でエンコードして FAISS DB を構築（テキストインデックスは不要になる）。

**実行コマンド:**

```bash
python functional_description/build_embeddings.py
```

---

### Phase 3 — テキスト→画像 クロスモーダル検索（`search.py`）

**役割：** テキストクエリを text encoder でベクトル化し、画像のみの FAISS DB と照合して Top-K 意匠を返す。

**現状（ベースライン）:**

```text
クエリ文字列
  → CLIP text encoder → 512-dim → faiss_image.index 検索
  → ST text encoder   → 768-dim → faiss_text.index  検索
  → Reciprocal Rank Fusion で統合 → Top-K 表示
```

**改善後（目標）:**

```text
クエリ文字列（機能文。形状記述あり/なし両対応）
  → fine-tuned text encoder → 共通ベクトル + テキスト固有ベクトル
  → 画像のみの FAISS DB と照合
  → Top-K 意匠を返す
```

**実行コマンド例:**

```bash
python functional_description/search.py "a glove used to protect hands during sports"
python functional_description/search.py "手を保護するスポーツ用グローブ" --topk 5
```

---

作成: 2026-06-10
