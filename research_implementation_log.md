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

## 今後の課題

- [ ] 100エポック学習完走 → 評価指標の改善確認
- [ ] `--unfreeze 2` でエンコーダ末尾層のfine-tuning実験
- [ ] Locarnoクラス別の検索精度分析
- [ ] Caption 列（AI生成）vs title のテキストとしての有効性比較
- [ ] image-only DB でのゼロショット検索（完成後のターゲット）