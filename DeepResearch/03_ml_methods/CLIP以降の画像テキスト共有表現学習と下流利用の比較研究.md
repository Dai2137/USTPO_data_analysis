# CLIP以降の画像テキスト共有表現学習と下流利用の比較研究

## エグゼクティブサマリ

本稿は、CLIPを原点とする画像–テキスト共有表現学習を、CLIPそのものの拡張だけに限定せず、CLIP型の二塔対比学習を拡張した研究、共有空間に融合器や生成器を重ねた研究、凍結したCLIP系表現を下流検索に使う研究まで含めて、代表的な **10 本**を比較したものである。

全体像はかなり明瞭で、研究の主戦場は大きく三つに分かれる。

1. **データ・凍結戦略系** — CLIP / ALIGN / LiT / MetaCLIP のように、基本の対称 softmax 型コントラスト損失を維持しつつ、データ規模・データ品質・凍結戦略で性能を押し上げる系統。
2. **fine-grained grounding 系** — ALBEF / BLIP のように、共有空間の coarse alignment だけでは不足する fine-grained grounding を、ITM・MLM・LM といった補助損失で補う系統。
3. **下流転用系** — Pic2Word / SEARLE のように、凍結した CLIP 系表現空間そのものは変えず、画像を「疑似単語」に写像して画像+テキスト検索へ転用する系統。

FILIP と SigLIP は、そのちょうど中間に位置する重要な分岐で、前者は類似度関数を、後者は損失正規化そのものを差し替えた。

損失関数の観点で見ると、CLIP以降の改善はほぼ次の四類型に整理できる。

| 類型 | 代表論文 | 改善の方向 |
| --- | --- | --- |
| 共有空間を保ったまま大規模化 | CLIP / ALIGN / LiT / MetaCLIP | データ規模・品質・凍結戦略 |
| loss 側に局所対応を埋め込む | FILIP | 画像パッチと単語の token-wise late interaction |
| 対比損失に補助損失を追加 | ALBEF / BLIP | マッチング (ITM)・言語生成 (LM・MLM) |
| softmax 対比を pairwise sigmoid に置換 | SigLIP | 大域正規化依存を下げ分散実装を容易に |

**意匠検索への結論**: 最も実務的な構成は、**強い dual-encoder をベースに据え、軽量 composer で参照画像と修飾文を合成し、最後に cross-encoder reranker で詰める三段構え**である。ベースエンコーダには MetaCLIP か SigLIP、問い合わせ合成には Pic2Word（複雑な相対文なら SEARLE）、再ランキングには ALBEF / BLIP の ITM 的なクロスエンコーダが有力候補となる。

---

## 1. 調査範囲と整理軸

本稿は、CLIPを含む 2021 年以降の代表研究を中心に、次の基準で選んだ。

- 共有表現の学習そのものが中心であること、または CLIP 系共有空間を下流検索の共有部として使うことが主眼であること
- 損失関数・学習プロトコル・主要結果が論文から追えること

日本語の一次情報は少なく、公式論文 PDF と公式 GitHub / 研究コードが主な根拠となった。表中の著者欄は可読性のため第一著者 et al. に簡略化している。

研究の違いは結局、**どこで相互作用させるか**、**損失で何を正例・負例として扱うか**、**既存表現を凍結するか否か**に集約できる。

この分類に従うと：

- **検索専用に強い** → dual-encoder 系（CLIP / ALIGN / LiT / MetaCLIP / SigLIP）
- **再ランキングや複雑な照合に強い** → ALBEF / BLIP 系
- **画像+テキストクエリをそのまま実務投入しやすい** → Pic2Word / SEARLE 系

LiT はその中で例外的に、共有損失は CLIP 型のまま画像塔だけ凍結することでゼロショット転移を極端に高めた。

---

## 2. 主要論文の比較表

> TR = image→text retrieval、IR = text→image retrieval。特記なき限り数値は論文中の代表設定。

| 論文 | 著者 | 年/会議 | 目的タスク | CLIPとの関係・利用様式 | 学習プロトコル | 主要実験結果 | 実装 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **CLIP** | Radford et al. | 2021 / ICML | ゼロショット分類、画像–テキスト検索 | 原著 | 4億件の画像–テキスト対でスクラッチ学習。best model は ViT-L/14@336px | ImageNet zero-shot top-1 **76.2%**。共有空間を用いるゼロショット転移の基準点 | [openai/CLIP](https://github.com/openai/CLIP) |
| **ALIGN** | Jia et al. | 2021 / ICML | 画像–テキスト検索、ゼロショット分類、転移学習 | CLIP型損失の大規模化・模倣 | 18億件の noisy alt-text、EfficientNet-L2 + BERT-Large、LAMB、global batch 16,384、1.2M steps、temperature learned、label smoothing 0.1 | Flickr30K zero-shot TR R@1 **88.6** / IR R@1 **75.7**、MSCOCO zero-shot IR R@1 45.6、ImageNet zero-shot 76.4% | 公式実装リンクなし |
| **ALBEF** | Li et al. | 2021 / NeurIPS | 検索、VQA、NLVR2、VE | CLIP型対比 + 融合器 + MoD | 4.0M / 14.1M images、ViT-B/16 + BERT-base、30 epochs、batch 512、AdamW、queue 65,536、image 256 pretrain / 384 fine-tune | 14M pretrain で Flickr30K fine-tuned TR R@1 **95.9** / IR R@1 **85.6**、COCO TR R@1 77.6 / IR R@1 60.7 | [salesforce/ALBEF](https://github.com/salesforce/ALBEF) |
| **LiT** | Zhai et al. | 2022 / CVPR | ゼロショット分類、検索 | 固定（画像塔固定）+ CLIP型損失 | 事前学習済み画像塔を lock、text tower を contrastive tuning。私有 40億画像対、batch 32k、約 18B seen pairs | ImageNet zero-shot **84.5%**、ObjectNet **81.1%**。CLIP / ALIGN より大幅に高いゼロショット転移 | [google-research/big_vision](https://github.com/google-research/big_vision) |
| **FILIP** | Yao et al. | 2022 / ICLR | ゼロショット分類、画像–テキスト検索 | CLIP型損失の類似度関数改変 | FILIP300M を含む大規模データ。LAMB、warm-up 3000、30 epochs。global batch 40,960、LR 2e-3、wd 3e-3 | ImageNet zero-shot top-1 **77.1%**。MSCOCO zero-shot TR R@1 61.3 / IR R@1 45.9、fine-tuned Flickr30K TR R@1 96.6 / IR R@1 87.1 | 公式実装リンクなし |
| **BLIP** | Li et al. | 2022 / ICML | 検索、キャプション、VQA、ビデオ転用 | CLIP型対比 + ITM + 生成 LM | ViT-B/16 または L/16、20 epochs、batch 2880 / 2400、AdamW、wd 0.05、14M images（CapFilt + LAION で 129M 設定も評価） | 129M + ViT-L/16 で COCO FT TR@1 **82.4** / IR@1 **65.1**、Flickr zero-shot TR@1 96.7 / IR@1 86.7 | [salesforce/BLIP](https://github.com/salesforce/BLIP) |
| **SigLIP** | Zhai et al. | 2023 / ICCV | 共有表現学習効率、ゼロショット分類 | CLIP型損失の softmax→sigmoid 置換 | pairwise sigmoid loss。WebLI、batch 4k〜32k（最大 100万 batch まで検証）、4〜32 TPUv4 | SigLIP B/16 で ImageNet zero-shot **73.4%**、SigLiT g/14 で **84.5%** を 4 TPUv4・2日で達成。batch 利得は 32k 前後で飽和 | [google-research/big_vision](https://github.com/google-research/big_vision) |
| **MetaCLIP** | Xu et al. | 2024 / ICLR | ゼロショット分類、検索、データキュレーション | 模倣（CLIP と同一 training setup を固定し、データだけ変更） | CommonCrawl から metadata-balanced に 400M / 1B / 2.5B を構成。CLIP と同一 training setup、global batch 32,768、12.8B seen pairs | ViT-B/16 で ImageNet **70.8%** vs CLIP 68.3%、1B で **72.4%**、ViT-bigG/14 で **82.1%** | [facebookresearch/MetaCLIP](https://github.com/facebookresearch/MetaCLIP) |
| **Pic2Word** | Saito et al. | 2023 / CVPR | Zero-shot composed image retrieval | 固定 CLIP + 疑似単語 composer | OpenAI CLIP ViT-L/14 を凍結。3-layer MLP（約 0.8M params）を CC3M 上で AdamW、lr 1e-4、wd 0.1、batch 1024、8 V100 | CIRR test R@1 **23.9** / R@10 65.3 / R@50 87.8、Fashion-IQ 平均 R@10 24.7 / R@50 43.7 | [google-research/composed_image_retrieval](https://github.com/google-research/composed_image_retrieval) |
| **SEARLE** | Baldrati et al. | 2023 / ICCV | Zero-shot composed image retrieval | 固定 CLIP + textual inversion + distillation | 凍結 CLIP 上で二段階学習。まず OTI で pseudo-word を生成し、次に textual inversion network へ distillation | CIRR test R@1 **24.0** / R@10 66.82 / R@50 89.78、CIRCO test mAP@50 **11.84**（SEARLE-XL: **15.12**）。FashionIQ でも Pic2Word を上回る設定あり | [ABaldrati/SEARLE](https://github.com/miccunifi/SEARLE) |

---

## 3. 損失関数の比較

| 損失系列 | 代表論文 | 数式 | 役割 | 強み | 注意点 |
| --- | --- | --- | --- | --- | --- |
| 対称 softmax 対比 | CLIP, ALIGN, LiT, MetaCLIP | $\mathcal{L} = \frac{1}{2}(\mathcal{L}_{i \to t} + \mathcal{L}_{t \to i})$、$\mathcal{L}_{i \to t} = -\frac{1}{N}\sum_i \log \frac{\exp(s_{ii}/\tau)}{\sum_j \exp(s_{ij}/\tau)}$ | 画像埋め込みと文埋め込みを同一共有空間へ押し込む最小構成 | 実装が単純で ANN 検索や zero-shot transfer と相性がよい | 大域特徴中心なので局所属性や関係理解が弱い。大きい global batch に依存しやすい |
| token-wise late interaction 対比 | FILIP | 画像トークン $f_i^k$、文トークン $g_j^r$ に対し、$s_{ij}^I = \frac{1}{n_1}\sum_k \max_r (f_i^k \cdot g_j^r)$、$s_{ij}^T = \frac{1}{n_2}\sum_r \max_k (f_i^k \cdot g_j^r)$。その上で CLIP 型対称対比損失を計算 | パッチ–単語の局所対応を loss 側から導入する | cross-encoder を使わずに fine-grained retrieval を改善できる | 類似度計算が重くなるため、トークン選別や mixed precision などの工夫が必要 |
| ITC + ITM + MLM + MoD | ALBEF | $\mathcal{L} = \mathcal{L}_{itc} + \mathcal{L}_{mlm} + \mathcal{L}_{itm}$、MoD: $\mathcal{L}_{itc}^{mod} = (1-\alpha)\mathcal{L}_{itc} + \frac{\alpha}{2}(KL(q^{i2t} \| p^{i2t}) + KL(q^{t2i} \| p^{t2i}))$ | coarse な共有空間整列（ITC）と対ごとの細粒度整合（ITM）、文脈補完（MLM）を同時に学習 | 検索だけでなく VQA / NLVR2 にも効く。hard negative mining と相性がよい | dual-encoder 単体より重い。推論は top-k rerank を前提にすると実用的 |
| ITC + ITM + LM | BLIP | $\mathcal{L} = \mathcal{L}_{itc} + \mathcal{L}_{itm} + \mathcal{L}_{lm}$（LM は画像条件付き自己回帰の cross-entropy、label smoothing 0.1） | 共有表現を保ちながら生成能力を追加する | 検索・キャプション・VQA を一つの枠組みで扱いやすい | 構成要素が多く、純検索だけなら過剰な場合がある |
| pairwise sigmoid loss | SigLIP | $\mathcal{L} = -\frac{1}{N}\sum_{i,j} \log \sigma(y_{ij}(t \cdot z_i^\top z_j + b))$、$y_{ii} = 1$、$y_{ij} = -1\ (i \neq j)$ | softmax 正規化を捨て、各 image-text pair を独立に判定する | full-batch 正規化が不要で分散実装が簡単。小〜中 batch でも効きやすい | bias 項や pairwise 行列実装を丁寧に扱う必要がある。極端な大 batch の利益は飽和する |
| 疑似単語 cycle 対比 | Pic2Word | $\mathcal{L} = \mathcal{L}_{t2i}(p, v) + \mathcal{L}_{i2t}(p, v)$（$p$: 疑似単語埋め込み、$v$: 画像埋め込み） | 画像を text encoder が読める疑似トークンへ写像し、画像+テキスト query を組めるようにする | 既存 CLIP をそのまま使える。学習対象が小さい | prompt に依存しやすく、相対文の複雑性が高いと表現力の上限が来る |
| OTI + GPT 正則化 + distillation 対比 | SEARLE | $\mathcal{L}_{OTI} = \lambda_{cos}\mathcal{L}_{cos} + \lambda_{OTI}^{gpt}\mathcal{L}_{gpt}$、$\mathcal{L}_{gpt} = 1 - \cos(t, t^*)$。次に teacher / student pseudo-word 間で対称 contrastive $\mathcal{L}_{distil}$ を適用 | 疑似単語を人間の相対文と相互作用しやすい token manifold に載せつつ、高速化のために distill する | Pic2Word より expressive で、複数 CIR ベンチマークで強い | OTI 生成と distillation の二段階で、実装は Pic2Word より複雑 |

**表からの重要な示唆**: 性能差の本質は「損失ファミリの選択」よりも、**「loss がどの粒度の整合性を強制するか」**にある。CLIP / ALIGN / LiT / MetaCLIP はすべて同族であり、改善の源泉はむしろデータと凍結戦略にある。一方で FILIP・ALBEF・BLIP・SEARLE は、「共有空間だけでは拾えない差分」を loss で埋める。意匠検索のような細かな属性差分や参照画像との差分記述が本質のタスクでは、単純な CLIP loss のままでは足りない可能性が高い。

---

## 4. 各論文の要点

### CLIP

後続研究のほぼすべてが参照する「最小十分」な共有空間学習の基準点である。二塔 encoder、L2 正規化、対称 softmax 対比という単純さゆえに、インデックス化しやすく検索系に強い。一方で、画像と文の対応をグローバル特徴に押し込むため、「赤い襟だけ変える」「袖だけ長くする」といった相対属性操作では情報が薄くなりやすい。

### ALIGN

CLIP と非常によく似た loss のまま、よりノイジーで大規模な **18 億データ**へ振り切った研究である。重要なのは、「複雑な cross-modal fusion を足さなくても、dual-encoder + normalized softmax + 大規模データで retrieval は強くなる」ことを明確に示した点にある。他方で、学習は private data 依存で表現はやはり global matching に寄るため、後の ALBEF / FILIP のような fine-grained 化の動機も同時に生んだ。

### ALBEF

「まず整列してから融合する」という発想で、CLIP 型の dual-encoder と cross-encoder の折衷を作った点が決定的に重要である。ITC が大まかな共有空間を作り、その空間で hard negatives を拾って ITM が細部を詰めるので、検索では **first-stage retrieval + second-stage rerank** の形が自然に組める。意匠検索で top-K 候補の再順位付けをしたい場合、この設計思想は今でも非常に有効である。欠点は、純 dual-encoder より重く、実装も複雑になることだ。

### LiT

「画像塔はもう十分に強いのだから、壊さずに読ませる側だけ学習すればよい」という逆転の発想にある。実際、画像塔を lock した方が、同じ contrastive setting でもゼロショット転移が強くなり、ImageNet と ObjectNet で非常に高い値を達成した。下流が検索中心で、画像表現をなるべく安定に保ちたい場合に向いている。弱点は、画像–文の深い相互作用や生成タスクをそのまま扱う設計ではないことだ。

### FILIP

「loss は対比学習のままでも、類似度関数に局所対応を埋め込めば fine-grained alignment は大きく改善する」ことを示した。画像パッチごとに最も近い単語、単語ごとに最も近い画像パッチを取る late interaction は、shared space の索引性を壊さずに細粒度性を足せるのが利点である。その代わり、計算量は vanilla CLIP より確実に増えるため、top-25% token のような効率化が必要だった。属性語や部位語が効く意匠検索では、FILIP 的な発想は今でも価値が高い。

### BLIP

ALBEF をさらに一歩進めて、**理解タスクと生成タスクを一つの pretraining 枠組み**にまとめた研究として捉えるのが適切である。ITC と ITM に加えて LM を入れたことで、検索だけでなく captioning や VQA まで射程に入った。さらに CapFilt によって noisy web text をそのまま飲み込まず、captioner と filter でデータ側もブートストラップした点が大きい。欠点は、純検索向けには少し重く、ベースエンコーダというより「検索 + rerank + 生成」まで含めた総合モデルであることだ。

### SigLIP

CLIP 系研究の中で最も「損失そのもの」を正面から置き換えた代表例である。softmax 対比では全 batch を見渡す正規化が必要だが、SigLIP は pairwise sigmoid によってそれを不要にし、少ない TPU 数でも大きい batch を回しやすくした。論文の最重要メッセージは、**「batch をとにかく大きくすればよいわけではなく、利益は 32k 前後でかなり飽和する」**という点で、実装予算を考えるうえで非常に実用的だ。

### MetaCLIP

architecture や loss を変えなくても、**データのキュレーション戦略だけでかなり勝てる**ことを示した非常に重要な研究である。著者らは CLIP と同一 training setup に固定し、CommonCrawl から metadata-balanced にサブセットを構成することで、400M 規模でも CLIP を上回った。意匠検索でも「人気概念ばかり多いデータ」より、概念分布を意識してバランスさせたデータの方が shared representation を良くする可能性を強く示唆する。弱点は、方法の中心がデータパイプラインであり、下流 composer や reranker は別途設計が必要な点だ。

### Pic2Word

凍結 CLIP を実際の検索 UX に近い形へ持っていった最初の重要論文の一つである。発想は明快で、**画像を 1 個の疑似単語に写像し、その疑似単語を相対文の中に埋め込む**。これにより、画像+テキストの composed query を、CLIP の text encoder だけで処理できる。学習対象が小さく構成も単純なので、意匠検索の初期プロトタイプには非常に向いているが、複雑な相対文や高度な属性干渉では SEARLE ほどの表現力は出にくい。

### SEARLE

Pic2Word 系の「画像→単語」設計を一段洗練させたものとみなせる。特徴は、まず optimization-based textual inversion で高品質な pseudo-word を作り、その知識を軽量ネットワークに distill する点にある。これにより、Pic2Word と同じく推論時は forward-only でありながら、pseudo-word が人間の相対文と相互作用しやすい token manifold に載るよう工夫されている。特に CIRCO のように、参照画像と相対文の両方が本当に必要なベンチマークでは強い。これは意匠検索の評価ベンチ設計にもそのまま示唆を与える（単一 ground truth ではなく multiple ground truths と mAP を採用すべき）。

---

## 5. 意匠検索への推奨設計

以下は、上記文献の比較に基づく設計推論である。**共有表現層・composer 層・reranker 層を分離した三層設計**が最も堅い。shared space の学習と query composition と fine-grained re-ranking を一モデルに押し込むより、役割分担した方が失敗しにくい。

### 三層アーキテクチャ

```text
[共有表現層]  MetaCLIP / SigLIP 系 dual-encoder
      ↓ corpus 全体を索引化（FAISS ANN）
[Composer 層] Pic2Word（MLP）または SEARLE（OTI + distillation）
      画像 + テキスト → composed query を shared space で処理
      ↓ top-100 候補を取得
[Reranker 層] ALBEF / BLIP 系 cross-encoder（ITM）
      候補ごとに image-text pair の細粒度判定
      → 最終 Top-K
```

### 各層の選択指針

**共有表現層**:

- **MetaCLIP 系** — 意匠検索で概念の偏りが強い場合に特に重要。同じ CLIP training budget でも、データ分布を整える方が効く。自前データの質を設計できる場合に有効。
- **SigLIP 系** — pairwise loss で実装が扱いやすく、計算資源が限られていても強い shared encoder を作りやすい。

**Composer 層**:

- **Pic2Word 型**（最初の実装に推奨） — 凍結した共有空間に対して MLP 一つで画像を疑似単語に変換するだけ。「この形を保ったまま色だけ青に」「このレイアウトで曲線を増やして」といった問い合わせに対応しやすい。
- **SEARLE 型**（長い相対文やドメイン文体が重要な場合） — GPT 正則化つき pseudo-word が人間の相対文と相互作用しやすい token manifold に載る。

**Reranker 層**:

- **ALBEF 系**（純検索が目的） — top-k candidates にのみ ITM を計算して高速化。production search の再ランキング戦略としてそのまま移植しやすい。
- **BLIP 系**（captioning や query rewriting も統合したい場合） — 検索・生成を同一基盤で扱える。

### 学習戦略

データが少ない間は凍結寄り（LiT / Pic2Word / SEARLE 型）、増えたら fine-grained 化（FILIP / ALBEF / BLIP 型の hard negative ITM）がよい。特に部位・色・材質・パターンの組み合わせが重要なドメインでは、global embedding だけに依存しないことが性能の分岐点になる。

### 評価ベンチ設計への示唆

SEARLE が指摘するように、CIRR には「相対文だけで正解できてしまう」クエリが少なくない。意匠検索では、**参照画像が本当に必要で、かつ正解が複数ありうる評価セット**を作るべきで、SEARLE の CIRCO はその方向性を示している。自ドメイン評価でも、単一 ground truth ではなく **multiple ground truths と mAP** を採用するのが望ましい。

### 推奨構成まとめ

| 優先度 | 共有表現層 | Composer 層 | Reranker 層 | 対象ケース |
| --- | --- | --- | --- | --- |
| **第一候補** | MetaCLIP / SigLIP | Pic2Word | ALBEF ITM | 最初の実装。バランスがよく再現性が高い |
| **第二候補** | MetaCLIP / SigLIP | **SEARLE** | ALBEF ITM | 相対文が長く複雑で query composition の表現力が重要な場合 |
| **第三候補** | MetaCLIP / SigLIP | SEARLE | **BLIP** | 検索だけでなく説明文生成や query rewriting まで統合したい場合 |

---

## 参考文献

| 論文 | リンク |
| --- | --- |
| CLIP (Radford et al., ICML 2021) | [PDF](https://proceedings.mlr.press/v139/radford21a/radford21a.pdf) / [GitHub](https://github.com/openai/CLIP) |
| ALIGN (Jia et al., ICML 2021) | [PDF](https://proceedings.mlr.press/v139/jia21b/jia21b.pdf) |
| ALBEF (Li et al., NeurIPS 2021) | [PDF](https://proceedings.neurips.cc/paper_files/paper/2021/file/505259756244493872b7709a8a01b536-Paper.pdf) / [GitHub](https://github.com/salesforce/ALBEF) |
| LiT (Zhai et al., CVPR 2022) | [PDF](https://openaccess.thecvf.com/content/CVPR2022/papers/Zhai_LiT_Zero-Shot_Transfer_With_Locked-Image_Text_Tuning_CVPR_2022_paper.pdf) / [GitHub](https://github.com/google-research/big_vision) |
| FILIP (Yao et al., ICLR 2022) | [PDF](https://openreview.net/pdf/e8f6807c88ea1d0d0090f2c381f21739b217efb9.pdf) |
| BLIP (Li et al., ICML 2022) | [PDF](https://proceedings.mlr.press/v162/li22n/li22n.pdf) / [GitHub](https://github.com/salesforce/BLIP) |
| SigLIP (Zhai et al., ICCV 2023) | [PDF](https://openaccess.thecvf.com/content/ICCV2023/papers/Zhai_Sigmoid_Loss_for_Language_Image_Pre-Training_ICCV_2023_paper.pdf) / [GitHub](https://github.com/google-research/big_vision) |
| MetaCLIP (Xu et al., ICLR 2024) | [PDF](https://proceedings.iclr.cc/paper_files/paper/2024/file/d1450d6c10c6b6cf1b80964357f5fa08-Paper-Conference.pdf) / [GitHub](https://github.com/facebookresearch/MetaCLIP) |
| Pic2Word (Saito et al., CVPR 2023) | [PDF](https://openaccess.thecvf.com/content/CVPR2023/papers/Saito_Pic2Word_Mapping_Pictures_to_Words_for_Zero-Shot_Composed_Image_Retrieval_CVPR_2023_paper.pdf) / [GitHub](https://github.com/google-research/composed_image_retrieval) |
| SEARLE (Baldrati et al., ICCV 2023) | [PDF](https://flore.unifi.it/retrieve/2e218d2f-adfa-4bfe-9725-e0a4bdf88cf1/Baldrati_Zero-Shot_Composed_Image_Retrieval_with_Textual_Inversion_ICCV_2023_paper.pdf) / [GitHub](https://github.com/miccunifi/SEARLE) |
