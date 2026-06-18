# 週次MTGレポート — 2026-06-04

## 1. 今週やったこと

### 1-1. 意匠特許 機能文検索システムの設計・実装

「**意匠の機能文をクエリとして、外観と機能の両面から類似意匠を検索するシステム**」の実装を開始した。

#### 背景・動機

- 意匠審査では「その意匠がどういう製品として使われるか（機能・用途）」が非自明性・類似性判断の前提となる
- USPTO データセット（13,187 件）には title・Locarno 分類しかなく、**製品機能の情報が欠落している**
- VLM（Vision-Language Model）を使ってTIF図面から機能文を自動生成することで、機能ベースの検索を可能にする
- デザインは「外観と機能は連動する」ように設計されているはず
  - IMPACTデータセットを見た感じその観点が欠如している．と思ったが，論文で挙げられている以下の3例はユーザの観点からの機能が出力されている．ただ一般的な記述(歯ブラシなら当たり前のことしか言及していない)で，差別化が足りない．
    - Title: Oral care implement
    - Caption: The image is a drawing of a toothbrush, which is an oral care implement used for cleaning teeth. The toothbrush has a long handle and a head with bristles, designed to effectively remove plaque and food particles from teeth and gums. The toothbrush is an essential tool for maintaining good oral hygiene and preventing dental issues such as cavities and gum disease.
    - Title: Utility rack
    - Caption: The image is a rectangle, and it features a wooden utility rack with several hooks. The functionality of the utility rack is to provide a convenient and organized storage solution for various items, such as tools, utensils, or small equipment. The hooks allow users to hang items on the rack, keeping them off the countertops and keeping the workspace tidy and clutter-free.
    - Title: Portion of a socket
    - Caption: The image is a black and white drawing of a cylindrical object with a hexagonal pattern. The object is a portion of a socket, which is a type of electrical connector that allows for the safe and secure attachment of electrical devices, such as light fixtures or appliances, to an electrical supply. Sockets are designed to provide a stable and secure connection between the device and the electrical supply, ensuring that the device can operate safely and efficiently.

#### システム構成（3フェーズ）

```text
Phase 1: 機能文生成
  TIF図面 + タイトル + Locarno分類
      → SmolVLM-500M-Instruct（ローカルVLM）
      → 機能文テキスト（例: "A protective glove used in sports to shield the hand during grip-intensive activities."）
      プロンプト：This is a design patent drawing for a product titled '{title}'
                (Locarno classification: {locarno}).
                In 2-3 sentences describe:
                (1) what this product is,
                (2) how a user would use it in daily life,
                (3) any notable functional features visible in the design.

      → funcdesc.csv

Phase 2: 埋め込み生成
  TIF図面      → CLIP（openai/clip-vit-base-patch32）→ 画像ベクトル (512次元)
  機能文テキスト → sentence-transformers (multilingual) → テキストベクトル (768次元)
  → FAISS インデックス（2本）
- 小橋さんコメント
Phase2に工夫が入れられそう．画像から分かることとテキストから分かることの共通部分，特に相違部分を捉えられるように学習．別々で独立にやらず．同じモデルで学習．画像とテキストが似たベクトルになると損．参照→2026_06_04mtg_小橋さん提案.docx

Phase 3: 検索
  クエリ（機能文）
      → CLIP テキストエンコーダ → 画像インデックス検索
      → sentence-transformers   → テキストインデックス検索
      → Reciprocal Rank Fusion で統合
      → Top-K 特許を表示
```

#### モデル選定の経緯

| 検討したモデル | 結果 |
| --- | --- |
| moondream2 (vikhyatk/moondream2) | transformers 5.9 との API 非互換で断念 |
| moondream SDK (pip install moondream) | デフォルトがクラウド API → ローカル不可 |
| **SmolVLM-500M-Instruct (HuggingFaceTB)** | **採用**。500M params / ~500MB、完全ローカル・無料 |

- **完全無料**（HuggingFace 公式モデル、APIキー不要、ローカル推論）
- CUDA なし環境（CPU only）でも動作確認済み

---

### 1-2. 実装したスクリプト

| ファイル | 役割 |
| --- | --- |
| `functional_description/generate_func_desc.py` | Phase 1: VLM で機能文生成 |
| `functional_description/build_embeddings.py` | Phase 2: CLIP + FAISS インデックス構築 |
| `functional_description/search.py` | Phase 3: CLI 検索インターフェース |

機能文生成スクリプトの主な仕様:

- **Locarno 大分類による層化サンプリング** (`--sample N`)：全 200+ クラスから比例配分でサンプリング
- **再開機能**：途中で止めても処理済みをスキップして再開可能
- **ETA 表示**：推定残り時間を自動計算

検索コマンド例:

```bash
python functional_description/search.py "a glove used to protect hands during sports"
python functional_description/search.py "調理用品として使われる容器" --alpha 0.7
```

---

### 1-3. データ確認

- 処理対象: **13,187 件**の USPTO 意匠特許（2026年1〜3月分）
- Locarno 大分類: **200+ クラス**（食品・衣類・家具・電子機器 等）
- 今回の計画: **1,000 件の層化サンプル**で動作実証

---

## 2. 現在の課題・技術的ボトルネック

### ボトルネック: CPU 推論速度

| 環境 | 1件あたり | 1,000件合計 |
| --- | --- | --- |
| CPU（現状） | ~6〜9分 | **約4〜6日** |
| GPU (CUDA) | ~30秒 | **約8時間** |

- 現在のマシンは CUDA 非対応 PyTorch（`torch==2.12.0+cpu`）が入っている
- 2GB VRAM は存在するが CUDA ドライバ/PyTorch CUDA ビルドがない状態
- 夜間バックグラウンド実行で数日かけて蓄積する方針

### 解決済みの技術課題

| 問題 | 原因 | 対処 |
| --- | --- | --- |
| `AttributeError: all_tied_weights_keys` | transformers 5.9 + moondream2 非互換 | SmolVLM に切り替え |
| `ValueError: Unrecognized image processor` | AutoProcessor がキャッシュの config を誤検出 | `preprocessor_config.json` の `image_processor_type` を `SmolVLMImageProcessor` に修正 |
| TIF ファイルが見つからない | パスが `outer/inner/file` の2段構造なのを見落とし | `patent_folder_outer / patent_folder_inner / file` に修正 |
| `UnicodeEncodeError` | Windows (cp932) 環境で `≈` を含む文字列を出力 | ASCII 代替に置換 |

---

### 2-2. 動作確認結果（2件テスト）

SmolVLMProcessor への切り替えと `preprocessor_config.json` パッチ後、機能文の生成に成功した。

| patent_id | Locarno | 生成された機能文（抜粋） |
| --- | --- | --- |
| D1111777 | 0610 | "A curtain position limiting device is a device that restricts the movement of a curtain or drape..." |
| D1110594 | 2705 | "(1) The product is a lighter. (2) A user would use it in daily life by holding it and pressing the ignition button..." |

意匠カテゴリ（カーテン固定具・ライター）に合致した機能文が生成されており、品質は良好。

---

## 3. 来週の予定

1. **1,000件の機能文生成を完了させる**（夜間バックグラウンド実行、あと5日で終わる見込み）
2. **FAISS インデックス構築・検索デモ**（Phase 2 & 3 実行）
3. **検索品質の定性評価**：
   - クエリ例で上位10件を確認
   - 機能文の品質チェック（VLM出力が意味をなしているか）
4. **Phase2の工夫調査**：画像とテキスト両方の旨味を引き出すための既存手法を調査する（小橋さんコメント参照: `2026_06_04mtg_小橋さん提案.docx`）

   以下6論文を読む。→全部古い．マルチモーダルが流行る前．

   | # | 論文名 | 会議/年 | 著者 | 被引用数 | カテゴリ |
   | --- | --- | --- | --- | --- | --- |
   | 1 | **Domain Separation Networks** | NeurIPS 2016 | Bousmalis et al. (Google Brain) | ~5,750 | Shared/Private分離の元祖 |
   | 2 | **Barlow Twins: Self-Supervised Learning via Redundancy Reduction** | ICML 2021 | Zbontar et al. (Meta AI) | ~2,200 | Modal Collapse防止の現代標準 |
   | 3 | **MISA: Modality-Invariant and -Specific Representations for Multimodal Sentiment Analysis** | ACM MM 2020 | CMU (Morency lab) | ~450 | マルチモーダル分離の教科書的論文 |
   | 4 | **Learning Disentangled Representations for Cross-Modal Retrieval** | ACM MM 2021 | Deepak Gupta et al. | — | クロスモーダル検索への直接適用 |
   | 5 | **Disentangled Multimodal Representation Learning for Recommendation** | WSDM 2023 | — | — | CLUB（相互情報量上界）を $\mathcal{L}_{\text{diversity}}$ に使用 |
   | 6 | **Cross-Modal Disentanglement Networks for Deep Joint Embedding** | — | — | — | DSN の CLIP 空間拡張 |

   **各論文の立ち位置（意匠システムにおける根拠）:**

   1. **Domain Separation Networks (NeurIPS 2016)**
      - $\mathcal{L}_{\text{diff}}$（共通と固有を直交させる損失）を世界で初めて明確に定義した元祖論文。現在のマルチモーダル表現分離研究ほぼ全てのルーツ。
      - 小橋さんへの説明: 「Google BrainのDSN（NeurIPS 2016、被引用5750件超）の数理モデルをCLIP空間に拡張して適用します」という学術的妥当性の根拠。
      - 損失対応: $\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{task}} + \alpha\mathcal{L}_{\text{recon}} + \beta\mathcal{L}_{\text{difference}} + \gamma\mathcal{L}_{\text{similarity}}$

   2. **Barlow Twins (ICML 2021)**
      - Modal Collapse / Redundancy を防ぐ「CLIP登場以降の現代デファクトスタンダード」。出力ベクトルのクロス相関行列を単位行列に近づけることで、各次元が異なる特徴をコードするよう強制する。
      - 小橋さんへの説明: 「CLIP空間のModal Collapseを防ぐ制約として、Meta AIのBarlow Twins（ICML 2021、被引用2200件超）の非冗長性損失を固有サブスペースに採用します」。
      - 損失対応: $\mathcal{L}_{\text{diversity}}$ の実装として採用

   3. **MISA (ACM MM 2020)**
      - 画像・音声・テキストのマルチモーダルから Modality-Invariant と Modality-Specific を同時に抽出。提示された3損失（align, diff, diversity）の組み合わせを感情分析タスクで実際に実証した教科書的論文。
      - 意匠システムへの立ち位置: 意匠図面（画像）+ 機能文（テキスト）という2モダリティへの適用の先行事例。MMD（分布整合）を $\mathcal{L}_{\text{align}}$ に使っている点が参考になる。

   4. **Learning Disentangled Representations for Cross-Modal Retrieval (ACM MM 2021)**
      - 「画像・テキストのクロスモーダル検索」に3要素ロスを組んだ、本研究への最も直接的な先行研究。$\mathcal{L}_{\text{diff}}$ として同一モダリティ内の直交性制約を導入している。
      - 意匠システムへの立ち位置: 「Modal Collapseを防ぎ検索精度を劇的に向上させたACM MMのトップ研究を、意匠データ（図面と機能文）に適合させた」という直接根拠。

   5. **Disentangled Multimodal Representation Learning for Recommendation (WSDM 2023)**
      - 商品画像（視覚固有: デザイン）+ 商品説明文（テキスト固有: スペック）の分離。$\mathcal{L}_{\text{diversity}}$ として CLUB（Contrastive Log-ratio Upper Bound）= 相互情報量上界の最小化を明示的に組み込んでいる。
      - 意匠システムへの立ち位置: 意匠の「図面固有の幾何情報（画像）」と「法的機能記述（テキスト）」の分離に同様の構造を使えるか。ただし**「画像と テキストの固有情報は無相関であるべき」という前提は意匠には合わない（形状と機能は連動する）→ CLUB の適用範囲を要確認**。

   **$\mathcal{L}_{\text{total}} = \alpha\mathcal{L}_{\text{align}} + \beta\mathcal{L}_{\text{diff}} + \gamma\mathcal{L}_{\text{diversity}}$ との対応まとめ:**

   | 損失項 | 内容 | 対応論文 |
   | --- | --- | --- |
   | $\mathcal{L}_{\text{align}}$ | 共有サブスペース間の類似度最大化（InfoNCE / Triplet / CORAL） | ①DSN の $\mathcal{L}_{\text{similarity}}$、③MISA、④ |
   | $\mathcal{L}_{\text{diff}}$ | 共有と固有の直交性強制（Frobenius ノルム差分損失） | ①DSN の $\mathcal{L}_{\text{difference}}$、③MISA、④ |
   | $\mathcal{L}_{\text{diversity}}$ | 固有ベクトルの次元間冗長性削減（Barlow Twins / CLUB / HSIC） | ②Barlow Twins、⑤CLUB、⑥HSICを用いた実装（要文献確認） |

5. 国際学会どれ出すか
CVPRを目指して頑張りたい（11月〆切）
学会候補　https://matsuolab-geniac.notion.site/2869a903acd081d6a139f32e4e4271ff


---

## 4. 参考：サンプリング分布（上位10クラス）

| Locarno | 件数（全体） | サンプル | カテゴリ例 |
| --- | --- | --- | --- |
| 1404 | 783 | 58 | 包装容器 |
| 2605 | 380 | 28 | スポーツ用品 |
| 2101 | 421 | 31 | 食品・飲料 |
| 1302 | 436 | 32 | 繊維・衣料 |
| 1303 | 345 | 25 | 衣料アクセサリー |
| 2402 | 350 | 26 | 医療器具 |
| 0204 | 528 | 39 | 厨房・調理用品 |
| 2301 | 327 | 24 | 情報通信機器 |
| 2304 | 321 | 23 | コンピュータ周辺 |
| 1402 | 319 | 23 | 靴・履き物 |

---

作成: 2026-06-03
