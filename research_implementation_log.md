# 研究・実装記録：意匠特許クロスモーダル検索システム

面接・振り返り用。研究上の判断・実装上の困難と工夫を時系列で記録する。
**Claude Code に追記・更新の指示あり（CLAUDE.md 参照）。**

---

## 研究概要

**課題:** テキストクエリで意匠特許画像DBを検索するクロスモーダル検索システムの構築
**データセット:** IMPACT（USPTO意匠特許, 2007–2022, 約43万件）
**モデル:** COrAL（Contrastive Representation with Asymmetric Loss）
**目標指標:** Recall@1/5/10, MRR（text→image 検索）
**締切:** CVPR November 2026

---

## 研究上の判断

### 0. 問題設定：なぜ従来手法では不十分か

#### 従来システムの能力と限界

既存の意匠検索（USPTO・J-PlatPat・Espacenet等）は「**タイトル + ロカルノ分類コードによるキーワード検索**」が主流である。クエリ側にも DB 側にも、意匠出願時に申請するタイトルとロカルノ分類は付与されているため、**テキストクエリ → 画像 DB** の検索自体は従来システムでも可能である。

**従来システムが対応できないのは「機能文クエリ」である。**

タイトルは "Glove"・"Toothbrush" のような**カテゴリ語（名詞1〜2語）**が大半を占める（IMPACT 2022 年データで平均23文字、中央値17文字）。そのため BM25 等のキーワードマッチは、クエリに同じ語が含まれる場合にしか機能しない。

#### 実際の検索ニーズと語彙ギャップ

デザイナーや審査官が本当に知りたいのは、タイトルの一致ではなく、**特定の機能・用途・使用文脈を持つ意匠がどのような形状として実現されているか**という「形状と機能の対応関係」である。

**例：** "Toothbrush" というタイトルでヒットする意匠は多数存在するが、そのうち「幼児向けに太いグリップで握りやすく設計されたもの」と「電動ブラシのヘッドを交換しやすくした構造のもの」は、外観も機能も本質的に異なる設計思想を持っている。タイトル検索ではこの違いを取り出せない。

**語彙ギャップの具体例：**

| 機能文クエリ | 対応タイトル | BM25 でマッチするか |
|---|---|---|
| 「手を保護するスポーツ用グローブ」 | "Glove" | △（"glove" が含まれれば可） |
| 「打撃時の衝撃を吸収する掌保護具」 | "Glove" | ✗（語彙ギャップ） |
| 「幼児向けに太いグリップで握りやすい歯ブラシ」 | "Toothbrush" | ✗（機能の違いを区別できない） |

#### 本研究の解決策

意匠は「**外観（形状）と機能が連動するように設計される**」ものであり、形状の違いはそのまま機能・用途の違いを反映している。

**→ 機能と形状の対応関係を埋め込み空間に学習させ、機能文をクエリとして形状画像を検索するシステムを実現する。**

- **クエリ**：機能文（機能・用途・使用文脈を含むテキスト。形状記述あり/なし両対応）
- **DB**：画像のみ（全意匠にテキスト付与は莫大コストのため、retrieval time はテキスト不使用）
- **学習時のみ** title + AI生成 caption（機能文）をテキストとして使用

#### ベースラインとの比較

| 手法 | 機能文対応 | ドメイン適応 |
|---|---|---|
| BM25（タイトル） | ✗ 語彙ギャップ | — |
| CLIP zero-shot | ○ | ✗ 意匠特許未適応 |
| **COrAL（本研究）** | ○ | ○ IMPACT で学習 |

---

### 1. モデル選択：なぜ COrAL か

**状況:** 意匠特許は「形状・機能はテキストに書ける部分と画像にしか現れない部分がある」という非対称な情報構造を持つ。

**選択:** COrAL（共有パス + 固有パス × 2の3経路分解）
- **共有パス:** 画像とテキスト両方から学習される表現 → クロスモーダル検索に使用
- **固有パス:** 各モダリティ固有の情報（画像：形状細部、テキスト：機能説明）を分離
- **なぜ DeCUR や CLIP でなく COrAL?** 共有/固有の直交性損失により「クロスモーダルに使える表現」と「各モダリティ固有の表現」を明示的に分離できる。CLIP は共有表現のみで固有成分を捨てる。

**トレードオフ:** 実装の複雑さ（3経路の損失設計）と評価の難しさ（共有路のみ使うべき推論時に固有路と混同するリスク）がある。

---

### 2. train/test スプリット：なぜ時系列分割か

**選択:** 2021年 → train（32,536件）、2022年 → test（33,541件）

**理由:** ランダムスプリットでは「同時期に出願された意匠は視覚的・意味的に類似する」というデータリークが生じる。時系列分割は実際の検索ユースケース（過去の意匠から新しい意匠を検索）に対応する。

---

### 3. エンコーダ選択

| モダリティ | モデル | 出力 | 理由 |
|---|---|---|---|
| 画像 | DINOv2-base | (B, 257, 768) パッチトークン列 | テキストとの事前アライメントなし（純粋な視覚エンコーダ）。COrAL はモダリティ間アライメントを自前で学習する設計のため、CLIPの事前アライメントは不要・むしろ邪魔になりうる |
| テキスト | ModernBERT-base | (B, 128, 768) トークン列 | 多言語対応・長文対応。意匠のcaptionはAI生成の英文で、短文なので128トークンで十分 |

---

## 実装上の困難と解決策

### 困難 1：Locarno分類がCSVに存在しない

**状況:** per-class 評価のためロカルノ分類が必要。IMPACTのCSV `class` 列を確認したところ、USPTOのデザインクラスコード（例: `"D21.1"`）が入っており、ロカルノ形式（`"01-01"`）ではなかった。

**試みたこと:**
- `patents_metadata.csv`（別パイプライン由来）との紐付け → IDレンジが全く重複せず失敗

**解決策:** IMPACT XMLから直接抽出
```
<classification-locarno>
  <main-classification>0101</main-classification>  → "01-01"
```
- `re` + `ThreadPoolExecutor(8)` で並列処理
- 全年（2007–2022）434,498件を100%カバー
- 各年のCSVに `locarno_class` 列として追記

**なぜこの方法?** XMLは元データであり最も信頼できる。外部APIは不要。ThreadPoolExecutor はI/Oバウンドなファイル読み込みに適切（CPUバウンドではないのでGILの影響を受けない）。

---

### 困難 2：Google Drive I/O ボトルネック（5時間→1分）

**状況:** Colabの学習ループがDrive経由の画像読み込みでボトルネック。3.2万枚の TIFファイルをDriveからColabローカルSSDにコピーしようとした。

**試みたこと・失敗:**
1. `rsync` → 進捗が見えない
2. `tqdm` + `shutil.copy2`（1ファイルずつ） → **1.88 files/s → 推定5時間**。Drive のファイル単位レイテンシが原因。
3. スキップ判定のバグ → `len(dst.glob('*.TIF')) > 0` で判定していたため、195件でも「完了済み」とみなして32,341件をスキップ

**解決策:** zip一括転送
1. Windows でフォルダをzip化（2.2GB/年）
2. Driveに置いた zip をColab側で単一ファイルコピー（**38秒**）
3. zipfile で展開（**7秒**）、zip削除

**結果:** 5時間 → 約1分。学習速度も 0.14 it/s → **0.72 it/s（5倍改善）**。

**スキップ判定の正しいロジック:**
```python
if dst_n == src_n:  # ファイル数が一致したときだけスキップ
    ...
```

---

### 困難 3：COrAL の推論パスの混同

**状況:** `eval_retrieval.py` 実装時、クロスモーダル検索のための推論パスを誤って実装した。

**誤った実装:** `encoders[0]`（共有パス用DINOv2）+ `lin_mod`/`pooling_layers`（これは**固有パス**専用）を組み合わせた不正なハイブリッド。

**COrAL のアーキテクチャ理解:**
```
共有パス:   encoders[i] → FusionTransformer(concat) → head → (B, 512)
固有パス:   unique_encoders[i] → lin_mod[i] → pooling_layers[i] → uni_head_i → (B, 512)
```
`encoders` と `unique_encoders` は別の重みを持つ（deepcopy で初期化）。

**解決策:** ゼロマスキングによる単一モダリティ推論
```python
# 画像のみ→共有表現
z_img  = enc_img(imgs)                            # (B, 257, 768)
z_zero = torch.zeros(B, 128, 768, device=device)  # テキスト分をゼロ埋め
z_fused = fusion([z_img, z_zero])                 # FusionTransformer
img_emb = head(z_fused)                           # (B, 512)
```
**なぜゼロマスキングが有効?** COrAL は非対称マスキング（asymmetric masking）で学習するため、片方のモダリティがゼロになる状況は訓練分布内。

---

### 困難 4：実験条件の管理（チェックポイントの混同）

**状況:** `checkpoints/impact/coral-impact-epoch=009.ckpt` が2022年データで学習したモデルだったのに、2021年学習の実験でそのチェックポイントからresumeしてしまった。

**解決策:** チェックポイントディレクトリにハイパーパラメータ全てを埋め込む
```
checkpoints/y{years}_bs{batch_size}_lr{lr}_wd{wd}_uf{unfreeze}/
# 例: y2021_bs64_lr1e-4_wd1e-3_uf0/
```
- TensorBoard のログ名も同じタグを使用
- ノートブックのハイパラセルで `RUN_TAG` を定義し、学習・評価セルで一貫して参照

---

### 困難 5：Colabランタイム切断対策

**状況:** A100インスタンスでも途中でランタイムがリセットされることがあり、学習状態・ファイルが消える。

**解決策（多層防御）:**

| 失うもの | 対策 |
|---|---|
| 学習済みモデル | `every_n_epochs=1` でDriveにチェックポイント保存 |
| 学習の再開 | 起動時に最新チェックポイントを自動検出してresume |
| 画像ファイル | Driveのzip(2.2GB)から毎セッション高速再展開（~1分） |
| 評価結果 | チェックポイントと同じDriveディレクトリに保存（`eval_2022_shared.json`） |

---

### 困難 6：BERTTokenEncoderのdeepcopy問題（Windows固有）

**状況:** COrAL は MMFusion 構築時に `deepcopy(encoder)` で固有パス用エンコーダを複製する。ModernBERTのRustバックエンドTokenizerは `deepcopy` 非対応でクラッシュ。

**解決策:** Tokenizer を lazy プロパティ化（初回アクセス時に初期化、シリアライズ対象外にする）
```python
@property
def tokenizer(self):
    if self._tokenizer is None:
        self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    return self._tokenizer
```

---

### 困難 7：CLIPエンコーダが「整合済み空間」を使えていなかった

**状況:** COrAL に CLIP ViT-B/32 をエンコーダとして採用し（DINOv2+ModernBERT版に対する比較実験）、2021年データで学習・評価したところ、CLIP zero-shot（追加学習ゼロ）に COrAL が全件 R@1 で約78倍もの差をつけられて大敗した。

**誤った実装:** `CLIPVisionModel` / `CLIPTextModel` の `last_hidden_state`（= projection 前のパッチ・トークン列）をそのまま FusionTransformer に渡していた。

```python
# 誤り: projection前の未整合トークン列
out = self.model(pixel_values=pixel_values)
return out.last_hidden_state  # (B, 50, 768) 画像 / (B, 77, 768) テキスト
```

**原因の特定:** CLIP のクロスモーダル整合（画像とテキストが同一空間に揃う性質）は、`visual_projection` / `text_projection` を通過した**後**の512次元空間にしか存在しない。`last_hidden_state` はCLIPのバックボーンで抽出しただけの、画像・テキスト間で整合されていない生の特徴量だった。つまり「CLIPを使っている」つもりが、CLIPの最大の強みである事前整合を全く活用できていなかった。

**解決策:** `visual_projection` / `text_projection` 適用後の整合済みベクトルを使う `clip_aligned` エンコーダを新規実装。

```python
out     = self.vision_model(pixel_values=pixel_values)
pooled  = out.pooler_output               # (B, 768) CLS after post_layernorm
aligned = self.visual_projection(pooled)  # (B, 512) CLIP整合済み空間
return self.out_proj(aligned).unsqueeze(1)  # (B, 1, out_dim) 長さ1のトークン列
```

**トレードオフ（トークン数減少による表現力低下）:** 画像・テキストとも1トークンに集約されるため、FusionTransformerへの入力長は127→2トークンに激減する。2トークン間のself-attentionは数学的には成立するが、実質的には `output = α×img_embed + (1-α)×txt_embed` という学習済み重み付き混合に近く、127トークン版が学習できていた「どの画像パッチとどの単語が対応するか」という細粒度な対応関係は原理的に学習できない。固有パス（unique path）も、ゼロマスク時に渡る1トークンの画像埋め込みが既にCLIPのCLS（全体要約）であるため、パッチレベルの局所的視覚情報が残っておらず「画像固有の情報」を取り出す意味が薄くなる。

**DeCUR との設計思想の違い（この変更がなぜ許容できるかの根拠）:** DeCUR は1本のベクトルの**次元を分割**して shared/unique を分離する設計だが、COrAL は**別ネットワーク（FusionTransformerとuniqueパス）が役割を分担**する設計。そのため `clip_aligned` でFusionTransformerが2トークンしか受け取らなくても、「共通情報を取り出すネットワーク」という役割自体は構造的に成立する。ただしDeCUR的な非アライン・多トークン設計（DINOv2+ModernBERT版）が持っていた細粒度なcross-modal attentionの学習余地は、CLIP整合済み1トークン設計では原理的に失われるというトレードオフは残る。

**ステータス（2026-07-09時点）:** `clip_aligned` は実装・設計のみ完了。学習・評価は未実施（[weekly_report_20260709.md](weekly_reports/weekly_report_20260709.md) 1-5節参照）。

---

## 研究上の観察

### caption の識別力：同ロカルノクラス内で事実上区別不能

**調査日:** 2026-06-28  
**対象:** IMPACTデータセット 2022年, ロカルノクラス 14-04（表示画面・GUI意匠）

同クラス内の4件（D0949194 / D0949195 / D0951992 / D0951993）を目視確認したところ、
画像は外観が大きく異なるにもかかわらず、AI生成 `caption` はほぼ同一内容だった。

| 特許ID | 画像の外観 | caption の骨子 |
|---|---|---|
| D0951992 | 星・ダイヤ形アイコンを並べたUI | "square-shaped display screen with animated GUI, buttons, icons..." |
| D0951993 | 丸角正方形のローディング表示 | "square-shaped display screen with GUI, buttons, icons, menus..." |
| D0949194 | アニメキャラクター風アバターのUI | "square-shaped display screen with transitional GUI, icons, buttons..." |
| D0949195 | 手のジェスチャー風アニメーションアイコン | "square-shaped display panel with animated computer icon..." |

**示唆:**
- `caption` は製品カテゴリレベルの説明であり、同クラス内の個別意匠の外観差を反映していない
- これは14-04（GUI）だけでなく、**意匠特許全般にわたる構造的問題**と考えられる（意匠の差異は形状・装飾にあり、機能はクラス内で共通するため）
- `caption` のみを positive ペアのラベルとして使うと、同クラス内の異なる意匠が「似たもの」と誤って扱われるリスクがある

**対応方針（検討中）:**
- `title`（短いが固有名詞・形状語を含む）と `caption` を組み合わせる
- 検索クエリは「機能文」だが、学習時ラベルには `title` の識別力を活用する設計を検討

### 追調査（2026-07-01）：同ロカルノ分類・同タイトルでも区別不能

同クラスに加えて**同タイトル**（= 同製品名）でさらに絞り込んで比較したところ、状況は悪化した。

| クラス | タイトル | 件数 | captionの状況 |
|---|---|---|---|
| 04-02 | Shoe | 758件 | 全件「a piece of footwear designed to protect and comfort the foot」の言い換え |
| 23-01 | Faucet | 179件 | 全件「a device used to control the flow of water」の言い換え |
| 06-01 | Chair | 151件 | 一部に "wire" / "wooden" 等の素材語あり、それ以外は無差別 |
| 09-01 | Bottle | 123件 | 形状語（"round top and cylindrical body" 等）が断片的に出るが不安定 |

captionが識別できる粒度はせいぜい**製品カテゴリ（suitcase vs backpack）レベル**であり、同一製品カテゴリ内の外観差はほぼ反映されていない。これはIMPACTのキャプション生成VLM（SmolVLM等）の限界である可能性と、意匠図面（白黒線画）の情報量の薄さ両方に起因すると考えられる。

**次のステップ（検討中）:**
- **高品質VLMで再確認**: GPT-4o / Gemini等の高精度APIで同タイトル意匠群のキャプションを生成し直し、識別力が上がるかサンプル確認
- **人手アノテーション**: 少数サンプルで「形状・差分の言語記述」を人手で付与し、ファインチューニングの素材とする（コスト大）
- **既存VLMの限界か、意匠情報自体の限界かを切り分ける**: 高級APIで改善しないなら問題は「意匠の外観差をテキストで表現すること自体の難しさ」→ それ自体がRQになりうる

### 追調査（2026-07-01）：USPTO OA文書の内容と拒絶理由の種類

Patent File Wrapper API で取得したShoe意匠出願（29754396）のNon-Final Rejection（DOCX）を精査した結果、以下が判明した。

**意匠特許の拒絶理由は図面品質だけではない:**

| 拒絶種別 | 内容 | 新規性言語の有無 |
|---|---|---|
| §112(a)(b) | 図面の明確性・不開示（破線の品質、陰影なし、図面間の不整合） | なし。ただし意匠固有の視覚特徴が言語化される（後述） |
| §102 | 新規性欠如（先行意匠との類似） | **あり**。「この意匠はXに比べてここが類似/異なる」の比較言語が含まれる |
| §103 | 非自明性欠如（複数先行意匠の組み合わせ） | あり |

意匠特許では§112（図面品質）で拒絶されることが多く、その場合は先行意匠との比較テキストは含まれない。
§102/§103拒絶まで進むケースが何割あるかは未確認。

**§112文書でも意匠固有の視覚特徴が断片的に言語化される:**

今回のShoe (29754396) の§112文書例：
- "nine chevron shapes made up of broken lines on the tongue and lacing system"
- "zig zag line on the left side of the toe cap"
- "broken lines merging with solid lines of the claimed features"

これはcaptionが一切捉えていない意匠固有の形状記述であり、§112文書でも利用価値がある可能性がある。

**DOCX内には参照図が埋め込まれている:**

"Please see below for figure 2..." という形で審査官が比較用に埋め込んだ図面画像が存在する（`doc.inline_shapes` で取得可能）。テキストと画像のペアとして扱える可能性あり。

**実用方針:**
- OA Rejections APIの `hasRej102=1` フラグで§102拒絶のある意匠特許を絞り込み、そのCTNF/CTFR DOCXを取得すると比較言語が得られる
- §112文書も視覚特徴の言語化源として捨てがたい（フィルタリングすれば使える）
- 出願人Remarksは全件スキャンPDFのためOCR必要、大規模利用は困難

---

## 今後の課題

- [ ] 100エポック学習完走 → 評価指標の改善確認
- [ ] `--unfreeze 2` でエンコーダ末尾層のfine-tuning実験
- [ ] Locarnoクラス別の検索精度分析
- [x] Caption 列（AI生成）vs title のテキストとしての有効性比較 → 同クラス内でcaptionの識別力が著しく低いことを確認（上記観察を参照）
- [ ] image-only DB でのゼロショット検索（完成後のターゲット）