# 細粒度画像認識の先行研究サーベイ：上位カテゴリの扱いと全体・局所の配分による分類（提案手法の葉「B-2-b-ii／局所の選び方もサンプルごとに変わる」の既存手法チェック）

提案手法の葉（全体と局所の配分がサンプルごとに変わり、局所の選び方もサンプルごとに変わる）には、学習型の動的推論手法 GFNet（Glance and Focus Networks, NeurIPS 2020／TPAMI 2022）がすでに入ります。二値的・段階的な形ではあります。一方、VLM・CLIP を使うゼロショットや学習不要の細粒度認識に限ると、両方の条件を満たす手法は今回の調査では確認できませんでした。最も近いのは LAGO（arXiv 2026）、ABS（ICML 2025）、AWT（NeurIPS 2024）で、いずれもどちらか一方の条件を欠いています。

## TL;DR
- **既存手法あり（最重要）**：GFNet（TPAMI 2022）は、学習した方針で局所パッチを選びます。さらに確信度で途中終了するので、「全体（低解像度の glance）だけで判定するか、局所も足して判定するか」がサンプルごとに変わります。これは判定ルール3の「二値」の特殊ケースとして提案手法の葉に入ります。ただし、単一データセットでの学習（A-1）、計算効率の最適化が目的、VLM 非使用という点で提案手法と異なります。もう1本、MGE-CNN（ICCV 2019）も提案手法の葉に入ることを原文で確認しました。前の専門家の Grad-CAM 注意で切り出した領域を次の専門家に渡し（〔second expert is cropped based on attention map from previous input before zooming into the size of first input〕、テスト時は予測ラベルを使う）、〔The gating network determines the contribution of each expert to the final predictions.〕ので、局所の選び方も全体・局所の配分もサンプルごとに変わります。FG-MoE（S. Yang ほか、Pattern Recognition 175 (2026) 113050、会場は対象外）もサンプルごとのゲートで専門家（全体系・局所系）の寄与を変えますが、局所の選び方は未確認です。
- **VLM・ゼロショット系には空白がある**：LAGO は局所をサンプルごとに選びます（FastSAM の提案領域と確信度に応じたテキスト誘導）。しかし全体と局所の最終的な補間係数 λ はデータセットごとに決める固定値で、B-2-b-i に入ります。ABS は注意で局所を選びますが、配分は N:N で固定です。AWT と MTA は配分がサンプルごとに変わりますが、局所はランダムです。つまり「選択」と「配分」の片方ずつを満たす手法はあるものの、学習不要の CLIP・VLM 系で両方を満たす手法は見つかりませんでした。
- **今後の課題として明記した論文**：microCLIP の記述（依頼文に記載済み）に加えて、GC-CLIP が "Strategies to weight contexts dynamically can be investigated in future works." と書いています。提案手法の新規性を主張する根拠として引用できます。

## Key Findings

### 1. 分類木への配置（木の形）

```
A. 上位カテゴリを前提にする
   A-1. 明示的に与える
        ├ Finedefics (ICLR 2025) [既分類]
        ├ TransFG (AAAI 2022) [既分類; B-2-b-i と併記]
        ├ GFNet (NeurIPS 2020 / TPAMI 2022) ※評価設定として。仕組みは B-2-b-ii
        ├ MGE-CNN (ICCV 2019) ※評価設定として。仕組みは B-2-b-ii（局所もサンプル依存、原文で確認済み）
        ├ FG-MoE (Pattern Recognition 2026, 会場対象外) ※仕組みは B-2-b-ii 候補（要確認）
        ├ RA-CNN (CVPR 2017, 古典) ※仕組みは B-2-b-i
        ├ DCAL (CVPR 2022) ※仕組みは B-2-b-i（詳細未確認）
        ├ RealBirdID (arXiv 2026, arXivのみ) ベンチマーク（属を与える）
        ├ Fine-R1 (arXiv 2026, arXivのみ)（詳細未確認）
        └ Zero-Shot FG Classification Using LVLMs (EMNLP Findings 2025, 会場対象外・参考)
   A-2. 暗黙に頼る
        ├ CaSED (NeurIPS 2023) [既分類]
        ├ On Large Multimodal Models as Open-World Image Classifiers (ICCV 2025) [既分類]
        └ RAR (会場未確認; OpenReview 投稿・PubMed 収載あり)
B. 上位カテゴリを前提にしない
   B-1. 上位カテゴリを推定して取り戻す
        └ FineR (ICLR 2024)
   B-2. 見る場所を画像だけから決める
        B-2-a. 局所だけを使う
             ├ WCA (ICML 2024)（全体は局所の重み計算にだけ使う）
             ├ BiFTA (TMLR 2026, 会場対象外・参考)
             ├ FAIR (WACV 2026, 会場対象外・参考)
             └ LaZSL (ICCV 2025)（全体表現を含むかは未確認）
        B-2-b. 全体と局所を統合
             B-2-b-i. 配分が全サンプルで同じ
                  ├ TransFG (AAAI 2022) [既分類]
                  ├ microCLIP (ACL Findings 2026) [既分類]
                  ├ ABS (ICML 2025) ← 局所はサンプル依存（注意）
                  ├ LAGO (arXiv 2026, arXivのみ) ← 局所はサンプル依存（提案領域＋確信度適応のテキスト誘導）、λはデータセットごとに固定
                  ├ GC-CLIP (arXiv 2023, 参考) ← 局所はサンプル依存（検出器）、マージン均等平均
                  ├ CALIP (AAAI 2023) ← テキスト条件付きの注意、固定係数（詳細未確認）
                  ├ Temperature Scaling for Calibrating TPT (arXiv 2026, arXivのみ) ← 係数はクラス集合で決まり画像に依存しない
                  └ RA-CNN (CVPR 2017), DCAL (CVPR 2022)
             B-2-b-ii. 配分がサンプルごとに変わる
                  ・局所の選び方は固定・ランダム
                  ├ AWT (NeurIPS 2024) [既分類]
                  ├ MTA (CVPR 2024)
                  ├ ZERO (NeurIPS 2024)（二値：確信度の高いビューだけを残す。元画像が候補に入るかは未確認）
                  └ TTP (arXiv 2025, arXivのみ; 敵対的頑健性)
                  ・局所の選び方もサンプルごとに変わる ← 提案手法の葉
                  ├ GFNet (NeurIPS 2020 / TPAMI 2022)【既存手法：二値・段階的、学習型】
                  ├ MGE-CNN (ICCV 2019)【既存手法：Grad-CAM 注意で切り出した領域を次の専門家へ渡し、ゲートで専門家の寄与をサンプルごとに決める。学習型】
                  └ FG-MoE (Pattern Recognition 2026)【要確認・会場対象外】
[新枝] C. 推論の深さの適応
        ├ SARE (arXiv 2026) [既分類]
        └ CascadeVLM (EMNLP Findings 2024, 会場対象外・参考)
[新枝] D. 質問文・テキストが見る場所を決める
        ├ DyFo (CVPR 2025) [既分類]
        ├ V* (CVPR 2024)
        ├ MLLMs Know Where to Look / ViCrop (ICLR 2025)
        ├ CropVLM (arXiv 2025, arXivのみ)
        ├ Chain-of-Focus (arXiv 2025, arXivのみ)
        └ AwaRes (arXiv 2026, arXivのみ)
[新枝] E. 局所ビューを適応（パラメータ更新）の信号にだけ使う
        ├ TPT (NeurIPS 2022)
        ├ R-TPT (CVPR 2025)
        └ A-TPT (ICML 2026)（注意で守った拡張ビューの TV 重み付けアンサンブルも併用）
[新枝] F. ズームを学習時に内在化する（推論時は全体1枚のみ）
        └ Zooming without Zooming / ZwZ (arXiv 2026, arXivのみ)
```

収録は約40本です。目安の40〜60本の下限に当たります。検索予算の制約で、古典的な CNN 系（NTS-Net、PMG、TASN など）は網羅できていません。

### 2. 既分類論文の判定について（指摘）
- **AWT**：同意します。原文に "This set includes N augmented images alongside the original (denoted as the 0 index)." とあり、元画像（全体）がエントロピー重み付けの対象に含まれます。B-2-b-ii（局所はランダム）で妥当です。
- **microCLIP**：同意します。原文は "we fuse the local and global logits by computing their average, ensuring a symmetric representation." です。会場は ACL Findings 2026 と確認できました。優先会場リストには入っていないので、その旨を注記しています。
- **WCA**（未分類でしたが注意点）：全体の埋め込みはクロップの重みを計算するためだけに使われ、最終スコアには全体の項がないと理解しています。そのためルール2に従い B-2-a に入れました。ただし、最終スコアに元画像の項があるかどうかは原文の式で確認していません。
- **TransFG**：A-1 かつ B-2-b-i に同意します。

## Details

### 3. 論文ごとの表

表記：「〔〕」内は原文そのままの英語引用です。その後ろが日本語の要約です。原文を確認できなかったものは「未確認」と書きました。

| 論文名 / 筆頭著者 / 会場・年 | 葉 | 判定根拠（原文引用＋要約） | 評価データセット | 上位カテゴリの扱い | 全体と局所の統合方法 / 配分のサンプル依存 | 局所の選び方 |
|---|---|---|---|---|---|---|
| Glance and Focus Networks for Dynamic Visual Recognition (GFNet) / Yulin Wang / NeurIPS 2020, TPAMI 2022 | **B-2-b-ii（局所もサンプル依存）・二値/段階的**＋評価はA-1 | 〔first extracts a quick global representation of the input image at a low resolution scale, and then strategically attends to a series of salient (small) regions to learn finer features. The sequential process naturally facilitates adaptive inference at test time, as it can be terminated once the model is sufficiently confident about its prediction〕低解像度の全体を見てから顕著な小領域を順に見る。確信度が十分なら途中で止める。 | ImageNet ほか（細粒度データセットでの評価は未確認） | 与える（データセットごとに学習） | 逐次の特徴統合（RNN）。何ステップで止めるかがサンプルごとに変わる＝局所の寄与がサンプル依存（二値・段階的） | 学習した方針（強化学習による patch proposal）。アブレーションで学習した方針がランダム方針を上回ると報告 |
| Learning a Mixture of Granularity-Specific Experts for Fine-Grained Categorization (MGE-CNN) / Lianbo Zhang / ICCV 2019 | **B-2-b-ii（局所もサンプル依存）**＋A-1 | 〔The gating network determines the contribution of each expert to the final predictions.〕〔The second one is the gradient-based attention module, which is used to extract attention region and transform the training data into a new one for the following expert.〕〔In the train phase we use ground-truth label and during test time, we use predicted class labe[l].〕ゲートネットワークが各専門家の寄与を決める。Grad-CAM の注意からしきい値で箱を推定して切り出し、次の専門家に渡す。テスト時は予測ラベルを使う。 | CUB-200-2011 ほか | 与える | ゲートによる専門家の加重（サンプル依存）。原文〔second expert is cropped based on attention map from previous input before zooming into the size of first input〕より、第1の専門家が元画像（全体）、後続の専門家が注意で切り出した局所を担う | 勾配ベースの注意（Grad-CAM）で切り出す（サンプル依存） |
| FG-MoE: Heterogeneous mixture of experts model for fine-grained visual classification / S. Yang / Pattern Recognition 175 (2026) 113050（会場対象外） | B-2-b-ii 候補（**要確認**）＋A-1 | 〔five specialized experts: global structure, regional attributes, local details, texture patterns, and part interactions. A spatial gating network enables dynamic expert routing〕全体構造・局所詳細などの5つの専門家を空間ゲートで動的に振り分ける。 | 未確認 | 与える | 空間ゲートで動的にルーティング（サンプル依存と推定。詳細は未確認） | 未確認 |
| Towards Fine-Grained Visual Recognition in LMMs (Finedefics) / 筆頭未確認 / ICLR 2025 | A-1 [既分類] | 既分類のため再調査していない | 未確認 | 与える（プロンプト） | — | — |
| CaSED / Alessandro Conti / NeurIPS 2023 | A-2 [既分類] | 既分類 | 未確認 | 暗黙に頼る | — | — |
| On Large Multimodal Models as Open-World Image Classifiers / 筆頭未確認 / ICCV 2025 | A-2 [既分類] | 既分類 | 未確認 | 暗黙に頼る | — | — |
| RAR: Retrieving And Ranking Augmented MLLMs for Visual Recognition / Ziyu Liu / 会場未確認（OpenReview 投稿と PubMed 41525633 への収載のみ確認） | A-2（記憶はデータセットのカテゴリから作るので実質A-1寄り） | 〔We initially establish a multi-modal retriever based on CLIP to create and store explicit memory for different categories beyond the immediate context window. During inference, RAR retrieves the top-k similar results from the memory and uses MLLMs to rank and make the final predictions.〕CLIP で候補を上位 k 件検索し、MLLM が順位付けする。 | 細粒度5種、少数ショット11種（Stanford Cars、Flowers102、Pets など）、検出2種 | 暗黙に頼る（候補はメモリ由来） | 全体画像のみ | なし |
| Democratizing Fine-grained Visual Recognition with LLMs (FineR) / Mingxuan Liu / ICLR 2024 | **B-1** | 〔As an initial step, we employ our VQA-based Visual Information Extractor (VIE) to initially identify these super-categories from the input images.〕〔we do not presume any super-category affiliation for a target dataset a-priori.〕VQA でまず上位カテゴリを推定し、それを手がかりに細粒度名を LLM で推論する。 | CUB-200、Stanford Cars、Stanford Dogs、Flowers-102、Oxford Pets、Pokemon | 推定する | 全体画像のみ（部位属性はテキスト化） | 局所クロップなし（部位はVQAで記述） |
| Visual-Text Cross Alignment (WCA) / Jinhao Li / ICML 2024 | B-2-a | 〔This method begins with a localized visual prompting technique, designed to identify local visual areas within the query image. The local visual areas are then cross-aligned with the finer descriptions by creating a similarity matrix using the pre-trained VLM.〕局所領域と細かな記述を類似度行列で照合する。後続研究による記述では〔It uses random crops to augment image samples and utilizes cosine similarity to extract informative patches.〕 | ImageNet、CUB、Pets、DTD、Food101、Places365 など | 不要（候補名は与える） | クロップの重み付け和。全体は重み計算に使う（最終スコアに全体の項があるかは未確認） | ランダム |
| On the test-time zero-shot generalization of VLMs (MTA) / Maxime Zanella / CVPR 2024 | B-2-b-ii（局所ランダム） | 〔MTA incorporates a quality assessment variable for each view directly into its optimization process, termed as the inlierness score.〕各ビューの inlierness スコアを最適化に組み込む。ビューはランダムクロップと元画像（付録に〔cropping (RandomCrop) and the original image〕とある）。 | 15データセット | 不要 | MeanShift のモード推定。inlierness による重みはサンプルごとに最適化 | ランダム |
| AWT / Yuhan Zhu / NeurIPS 2024 | B-2-b-ii（局所ランダム）[既分類] | 〔dynamically weighting inputs based on the prediction entropy.〕〔This set includes N augmented images alongside the original (denoted as the 0 index).〕予測エントロピーで元画像と拡張ビューを動的に重み付けする。 | 14のゼロショットデータセット＋ImageNet 変種4種 | 不要 | 負のエントロピーの softmax 重み → OT（Sinkhorn）。サンプル依存 | ランダム（random resized crop） |
| From Local Details to Global Context (ABS) / Lincan Cai / ICML 2025 | **B-2-b-i（局所はサンプル依存）** | 〔we propose an Attention-Based Selection (ABS) method from local details to global context, which applies attention-guided cropping in both raw images and feature space, supplement global semantic information through strategic feature selection.〕原画像と特徴空間の両方で注意に導かれたクロップを行う。最終スコアは生クロップ N 個と特徴クロップ N 個の重みなし和で、比は 1:1 に固定。 | ImageNet、V2、Sketch、A、R、CUB、Pets、DTD、Food101、Places365 | 不要 | 生クロップと特徴空間クロップ（CLS と相互作用）を連結。配分は固定（N:N） | DINO の注意の上位パッチを中心にする（中心はサンプル依存、サイズはランダム） |
| LAGO: Language-Guided Adaptive Object-Region Focus / Junyi Hu / arXiv 2026（arXivのみ） | **B-2-b-i（局所はサンプル依存）**、最も近い手法 | 〔Crucially, the strength of semantic guidance is not fixed, but is instead adaptively controlled by the sample-specific intermediate confidence score〕〔We optionally calibrate the fusion weights (β, α_dc, λ) per dataset using a parameter-free score-level procedure〕局所を選ぶときのテキスト誘導の強さ γ は確信度でサンプルごとに変わる。一方、全体の logits との補間係数 λ はデータセットごとに決める。 | ImageNet、CUB、Oxford Pets、DTD、Food101、Places365、ImageNet-V2/R/S/A | 不要 | z_final = λ z_dc + (1−λ) z_full（λ は固定）。物体チャネルと文脈チャネル内のクロップ重みはサンプル依存 | FastSAM の提案領域＋確信度適応のテキスト誘導による探索（サンプル依存） |
| Zero-Shot Visual Classification with Guided Cropping (GC-CLIP) / Piyapat Saranrittichai / arXiv 2023（参考。会場条件外） | B-2-b-i（局所はサンプル依存） | 〔we use an off-the-shelf zero-shot object detection model in a preprocessing step to increase focus of zero-shot classifier to the object of interest〕〔logits computed from images cropped by these final boxes are then averaged to get the final logit score.〕〔Strategies to weight contexts dynamically can be investigated in future works.〕OWL-ViT の箱を 0〜1 のマージンで均等に広げ（1 は元画像に相当）、均等平均する。動的な重み付けを今後の課題と明記。 | ImageNetS919、CUB（小物体サブセット -SM を含む） | 不要（CLIP の上位 k=5 クラスに候補を絞る） | 複数マージンの logits を均等平均（固定） | 検出器（上位 k クラス名で OWL-ViT に問い合わせる＝テキスト条件付き） |
| microCLIP / Sathira Silva / ACL Findings 2026 | B-2-b-i [既分類] | 〔we fuse the local and global logits by computing their average, ensuring a symmetric representation.〕局所と全体の logits を平均する。 | 細粒度13ベンチマーク | 不要 | 平均（1/2 固定） | 顕著性（SOAP による [FG] トークン） |
| TransFG / Ju He / AAAI 2022 | A-1 かつ B-2-b-i [既分類] | 既分類 | CUB、Stanford Cars、Dogs、NABirds など | 与える | 選んだパッチと CLS を最終層に入力 | 注意 |
| Interpretable ZSL with Locally-Aligned VLM (LaZSL) / Shiming Chen / ICCV 2025 | B-2-a（全体表現を含むかは未確認） | 〔LaZSL employs local visual-semantic alignment via optimal transport to perform interaction between visual regions and their associated attributes〕視覚領域と属性を OT で照合する。 | 9データセット（詳細未確認） | 不要 | OT。配分は未確認 | 未確認（Vision Set の作り方は未確認） |
| Let's Roll a BiFTA / Yuhao Sun / TMLR 2026（会場対象外） | B-2-a | 〔we observe that both the LLM-generated textual descriptions and the randomly cropped image patches often exhibit redundant content.〕ランダムクロップの冗長性を取り除いて照合する。 | ImageNet、CUB、Pets、DTD、Food101、Places365 | 不要 | クロップと記述の照合 | ランダム＋冗長性除去 |
| Towards Fine-Grained Adaptation of CLIP via a Self-Trained Alignment Score (FAIR) / 筆頭未確認 / WACV 2026（会場対象外） | B-2-a | 〔introduces a Learned Alignment Score (LAS) based on selected local image crops and adaptive class representations.〕選んだ局所クロップで学習済み照合スコアを作る。 | 13データセット | 不要 | クロップの重み（CLS 類似度）で上位 k 件を選ぶ | CLS 類似度による選択（サンプル依存） |
| CALIP / Ziyu Guo / AAAI 2023 | B-2-b-i（詳細未確認） | 〔we guide visual and textual representations to interact with each other and explore cross-modal informative features via attention.〕視覚とテキストをパラメータなしの注意で相互作用させる。 | 14データセット | 不要 | 未確認（固定係数で結合と理解しているが原文未確認） | テキスト条件付きの注意 |
| Bridging the Confidence Gap: Temperature Scaling for Calibrating TPT / 筆頭未確認 / arXiv 2026（arXivのみ） | B-2-b-i（局所ランダム） | 〔we balance the predictions from weak and strong augmentations using an adaptive weight〕〔α … is the average pairwise cosine similarity among the K normalized text embeddings〕元画像（弱拡張）と強拡張の平均の比 α を、テキスト埋め込みの平均類似度で決める。α はクラス集合で決まり、入力画像には依存しない。 | 未確認 | 不要 | α による補間（画像に依存しない＝固定） | ランダム＋エントロピー選択 |
| RA-CNN / Jianlong Fu / CVPR 2017（古典） | B-2-b-i＋A-1 | 二次情報（サーベイ）：〔By progressively refining attention regions from coarse to fine, RA-CNN mimics a human-like perception process〕原文は未確認 | CUB、Stanford Dogs、Stanford Cars | 与える | 複数スケールの特徴を結合（固定と理解。原文未確認） | 注意（再帰的にズーム） |
| Dual Cross-Attention Learning (DCAL) / Haowei Zhu / CVPR 2022 | B-2-b-i＋A-1（未確認） | 未確認 | 未確認 | 与える | 未確認 | 注意（高応答パッチ、未確認） |
| ZERO (Frustratingly Easy TTA) / Matteo Farina / NeurIPS 2024 | B-2-b-ii（ランダム・二値） | 〔augment N times, predict, retain the most confident predictions, and marginalize after setting the Softmax temperature to zero〕N 回拡張して予測し、確信度の高い予測だけを残し、Softmax の温度を 0 にして周辺化する。 | 未確認 | 不要 | 確信度で残すか捨てるか（二値）→ 投票 | ランダム |
| TTP: Test-Time Padding / 筆頭未確認 / arXiv 2025（arXivのみ） | B-2-b-ii（ランダム）＊元画像が含まれるかは未確認 | 〔a similarity-aware ensemble that assigns adaptive weights to each augmented view〕拡張ビューを類似度で適応的に重み付けする。 | 細粒度分類データセット（詳細未確認） | 不要 | ビューごとに適応重み | ランダム拡張＋パディング |
| TPT / Manli Shu / NeurIPS 2022 | 新枝 E | 二次情報：〔the prompt is optimized by minimizing the entropy of averaged prediction distribution over augmented views with confidence selection.〕 | ImageNet 系＋細粒度10種 | 不要 | 局所ビューはプロンプト更新にだけ使う | ランダム＋確信度選択 |
| R-TPT / Lijun Sheng / CVPR 2025 | 新枝 E | 二次情報：〔R-TPT performs image-level augmentation and proposes pointwise entropy optimization for textual prompts across views.〕 | 未確認 | 不要 | 未確認（信頼度による重み付けアンサンブルと理解。原文未確認） | ランダム |
| Towards Fine-Grained Robustness: Attention-Guided TPT (A-TPT) / Jia-Wei Hai / ICML 2026 | 新枝 E（B-2-b-ii 的な要素あり） | 〔we leverage them to guide the spatially varying augmentation intensities and multi-view ensemble for prompt tuning and inference.〕〔we use TV to measure the reliability of each view and obtain weights w_i for the final prediction〕注意の高い領域を守る拡張ビューを作り、注意マップの TV でビューを重み付けする。 | 9データセット（細粒度8種＋ImageNet） | 不要 | ビューの TV 重み（サンプル依存）。ただしビューは全体スケールの拡張で、局所クロップではない | 注意（GAR 改良版）で拡張の強度を空間的に変える |
| CascadeVLM / 筆頭未確認 / EMNLP Findings 2024（会場対象外） | 新枝 C | 〔integrating an entropy threshold, τ, to balance efficiency and accuracy, culminating in LVLM's adaptive classification.〕エントロピーが閾値以下なら CLIP だけで判定し、それ以外は LVLM で判定する。 | Stanford Cars、iNaturalist など | 暗黙に頼る（CLIP 上位 k 件） | 全体のみ（深さだけを変える） | なし |
| SARE / — / arXiv 2026 | 新枝 C [既分類] | 既分類 | 14データセット | — | — | — |
| DyFo / — / CVPR 2025 | 新枝 D [既分類] | 既分類 | — | — | — | 質問文 |
| V*: Guided Visual Search / Penghao Wu / CVPR 2024 | 新枝 D | 未確認 | V* Bench | 不要 | 未確認 | 質問文による視覚探索 |
| MLLMs Know Where to Look (ViCrop) / Jiarui Zhang / ICLR 2025 | 新枝 D | 〔we then propose training-free visual intervention methods that leverage the internal knowledge of any MLLM itself, in the form of attention and gradient maps, to enhance its perception of small visual details.〕MLLM 自身の注意や勾配マップで切り出す場所を決める。 | TextVQA、V*、POPE、DocVQA、GQA、AOKVQA、VQAv2 | 不要 | 元画像とクロップのトークンを並べて入力（配分の仕組みは明示されていない） | 質問に条件付けた注意・勾配 |
| CropVLM / 筆頭未確認 / arXiv 2025（arXivのみ） | 新枝 D | 未確認 | 未確認 | 不要 | 未確認 | 学習したズーム（質問条件付きと推定、未確認） |
| Chain-of-Focus / Xintong Zhang / arXiv 2025（arXivのみ） | 新枝 D | 未確認（タイトル "Adaptive visual search and zooming for multimodal reasoning via rl" のみ確認） | 未確認 | 不要 | 未確認 | 強化学習で探索・ズーム |
| Look Where It Matters (AwaRes) / 筆頭未確認 / arXiv 2026（arXivのみ） | 新枝 D | 未確認（図の説明から、質問が指す領域を適応的にクロップすることのみ確認） | 未確認 | 不要 | 未確認 | 質問条件付きクロップ |
| Zooming without Zooming (ZwZ) / 筆頭未確認 / arXiv 2026（arXivのみ） | 新枝 F | 〔Region-to-Image Distillation, which transforms zooming from an inference-time tool into a training-time primitive〕ズームを学習時の蒸留に移し、推論時は1回の順伝播で済ませる。 | 知覚系ベンチマーク | 不要 | 推論時は全体のみ | 学習時に教師モデルが微小領域を切り出す |
| RealBirdID / 筆頭未確認 / arXiv 2026（arXivのみ） | A-1（ベンチマーク） | 〔Using range map information to restrict the list of species under consideration significantly increases classification performance across all models〕分布域の情報で候補種を絞ると、どのモデルでも精度が大きく上がる。 | RealBirdID | 与える（属を与える） | — | — |
| Fine-R1 / 筆頭未確認 / arXiv 2026（arXivのみ） | A-1（未確認） | 未確認（CoT で細粒度認識を強化する MLLM であることのみ確認） | 未確認 | 未確認 | 未確認 | 未確認 |
| Zero-Shot Fine-Grained Image Classification Using LVLMs / Md. Atabuzzaman / EMNLP Findings 2025（会場対象外・参考） | A-1（多肢選択） | 〔Given an image I and a set of N possible class descriptions, the LVLM iteratively selects a small subset of m options〕LVLM が多肢から少数の選択肢を繰り返し選んで絞り込む。 | CUB など | 与える（候補集合） | 全体のみ | なし |

### 4. 両条件を満たす手法の有無と、提案手法との違い

**結論：学習型の画像認識には既存手法があります（GFNet、および細粒度認識の MGE-CNN）。VLM を使うゼロショットや学習不要の細粒度認識では、確認できる範囲で見つかっていません。**

**既存手法 GFNet（TPAMI 2022）と提案手法の違い（提案手法が CLIP・VLM による学習不要の細粒度認識だという前提での推定）**
1. **配分の形**：GFNet の配分は「途中で止めるステップ」で決まる二値的・段階的なものです。提案手法が全体と局所の比を連続値でサンプルごとに決めるなら、そこが違いになります。
2. **目的と前提**：GFNet は計算量の削減が主目的で、データセットごとに学習する前提（A-1）です。上位カテゴリなし（B）のまま、学習なしで細粒度の名前に届くことを目指す設計ではありません。
3. **局所の選び方**：GFNet は強化学習で方針を学習します。VLM 内部の注意・顕著性・検出器を学習なしで使う方式とは実装の前提が異なります。なお、GFNet を細粒度データセットで評価したかどうかは未確認です。

**確認済みの既存手法 MGE-CNN と、要確認の FG-MoE**：MGE-CNN（ICCV 2019）が両条件を満たすことは原文で確認しました。前の専門家の Grad-CAM 注意で切り出した領域を次の専門家に渡し（〔The second one is the gradient-based attention module, which is used to extract attention region and transform the training data into a new one for the following expert.〕、テスト時は予測ラベルを使う）、ゲートが専門家（元画像を見る第1の専門家と、注意で切り出した局所を見る後続の専門家）の寄与をサンプルごとに決めます。提案手法との違いは、データセットごとに学習する前提（A-1）であること、ゲートの学習が必要なこと、VLM を使わないことです。FG-MoE（S. Yang ほか、Pattern Recognition 2026）は全体構造と局所詳細の専門家を空間ゲートで振り分けますが、局所をどう選ぶかは原文の手法節で確認する必要があります。

**VLM 系で最も近い3本と、足りないもの**
1. **LAGO（arXiv 2026）**：局所の選び方はサンプル依存です。確信度によってテキスト誘導の強さ γ もサンプルごとに変わります。足りないのは、全体の logits と局所の統合の比 λ がデータセットごとの固定値である点です（〔We optionally calibrate the fusion weights (β, α_dc, λ) per dataset〕）。確信度を使っているのは「どこを見るか」であって、「全体と局所をどれだけ混ぜるか」ではありません。
2. **ABS（ICML 2025）**：DINO の注意でクロップ中心を選ぶので、局所の選び方はサンプル依存です。足りないのは、生クロップと特徴空間クロップの比が N:N で固定であり、全体と局所の比を入力ごとに変える仕組みがない点です。限界の節にも適応的な重み付けへの言及はありません。
3. **AWT（NeurIPS 2024）**：元画像を含む全ビューを負のエントロピーで重み付けするので、配分はサンプル依存です。足りないのは、局所が random resized crop で、注意・顕著性・検出器による選択がない点です。MTA（CVPR 2024）も同じ構図です。

このため、「局所の選択（ABS・LAGO 系）」と「全体を含む配分の適応（AWT・MTA 系）」をつなぐ部分が、提案手法の新規性として主張しやすい空白になっています。

### 5. 「全体と局所の適応的な重み付け」を今後の課題として挙げている記述
- **GC-CLIP**：〔Strategies to weight contexts dynamically can be investigated in future works.〕（文脈、つまり元画像寄りの広いマージンをどれだけ重視するかを動的に決めることを、今後の課題としている）
- **microCLIP**：依頼文に記載済み（適応的な重み付けを今後の課題と明記）。
- **LAGO**：限界の節は〔LAGO still depends on the quality of external proposals and offline text descriptions〕で、配分の適応には触れていません。
- **ABS**：限界の節は注意マップの質、拡張の多様化、他のモダリティについてで、配分への言及はありません。

## 新しく作った枝の一覧と定義
- **C. 推論の深さの適応**：全体と局所の視覚的な配分は変えず、処理の深さや計算量（検索だけにするか、LVLM で推論するか、など）だけをサンプルごとに変える手法。
- **D. 質問文・テキストが見る場所を決める**：ユーザーの質問文やテキストクエリが、注視・ズームする領域を決める手法。
- **E. 局所ビューを適応（パラメータ更新）の信号にだけ使う**：拡張ビュー・局所ビューをテスト時のプロンプトやパラメータの更新にだけ使い、最終予測は主に全体画像で行う手法。
- **F. ズームを学習時に内在化する**：学習時にだけ局所へのズームを使って教師信号を作り、推論時は全体画像1枚で判断する手法。

## Recommendations
1. **GFNet を関連研究で必ず扱う**：GFNet を「学習型・二値的・効率目的の既存例」として明示してください。提案手法との違いは、連続的な配分、学習不要、上位カテゴリなしの細粒度認識の3点で示すのが安全です。
2. **MGE-CNN を既存手法として関連研究で扱い、FG-MoE の原文を確認する**：MGE-CNN は、Grad-CAM 注意による切り出しとゲートによるサンプルごとの専門家加重を併せ持つ細粒度の既存手法です（原文で確認済み）。提案手法との違いは、学習不要であること、VLM を使うこと、上位カテゴリなしで動くことで示してください。FG-MoE は手法節を確認し、専門家の入力が注意に基づくズーム領域なら提案手法の葉に追加してください。
3. **LAGO との比較実験を最優先にする**：LAGO は FastSAM と確信度適応を使う最新（2026年5月）の最も近い手法です。λ を固定した LAGO と提案手法を比べれば、配分をサンプルごとに変えることの効果を直接示せます。
4. **比較対象を揃える**：ABS（注意による選択と固定配分）と AWT・MTA（ランダム局所と適応配分）を並べるアブレーションを組むと、「選択」と「配分」のどちらが効いているかを分けて示せます。
5. **新規性の根拠として引用する**：GC-CLIP と microCLIP の「今後の課題」の記述を引用できます。

## Caveats
- 検索予算の上限に達したため、収録は約40本で目安の下限です。NTS-Net、PMG、TASN、CAL、IELT などの古典的・学習型の細粒度手法は網羅できていません。この系統に、ゲートで全体と局所を融合する手法がほかにもある可能性は残ります。
- LAGO は2026年5月の arXiv 論文で、査読を経ていません。λ を「データセットごとに校正する」のは任意（optionally）の設定です。既定の λ がどう決まるかは、付録 A.5 を確認していないため未確認です。
- GC-CLIP は2023年の arXiv で、会場条件（arXiv のみは2025〜2026年に限る）の外です。「今後の課題」の記述を示すための参考として載せました。
- FG-MoE、RA-CNN、DCAL、CALIP、R-TPT は、手法の細部を原文で確認できていないか、二次情報に頼っています。表では「未確認」「二次情報」と明記しました。
- RAR の会場は確認できていません（OpenReview への投稿と PubMed 41525633 への収載のみ確認）。