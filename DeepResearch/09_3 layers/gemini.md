# **VLMの微細視覚識別における事後学習手法の体系的調査：視覚的保持・視覚-意味接地・比較推論の3層解析**

意匠特許図面（線画・無背景・質感なし）を用いた多肢選択判別のように、言語的・意味的プライア（単語の共起、ドメイン固有の名称、シーン文脈）が一切機能しない条件下では、Vision-Language Model（VLM）は純粋な幾何形状・輪郭・比率の微細な差分のみに頼って判別を行う必要がある。DINOv2等の視覚埋め込みによってシルエットが酷似したハードネガティブ候補（意味カテゴリは全く異なるが幾何形状が極めて類似している選択肢）を揃えた設問構成では、標準的なゼロショットインファレンスや単純なSupervised Fine-Tuning（SFT/LoRA）による精度向上が頭打ちになる現象（例：GPT-5ゼロショットで8択中51%程度、LoRAで+1.9pt程度の改善にとどまる現象）が顕著に現れる。  
本調査レポートでは、VLMがこのような微細視覚識別において失敗する根本原因を、「A. 視覚的保持（Visual Retention）」、「B. 視覚-意味接地（Visual-Semantic Grounding）」、「Reasoning. 比較推論（Visual Comparative Reasoning）」の3つの階層に分解し、2023年から2026年にかけてのトップカンファレンス（CVPR, ICCV, ECCV, NeurIPS, ICLR, IJCAI等）における先行研究と事後学習（Post-training）手法を体系的に整理・分析する。

## **1\. 層A：視覚的保持（Visual Retention / Encoder Bottleneck）**

### **1.1 呼称と学術的定義**

層Aは、VLMの視覚エンコーダ（Vision Encoder）が画像を入力した段階で、幾何構造、輪郭線、面取り、パーツの有無、アスペクト比、曲率といった微細な幾何学的特徴を言語非依存の内部埋め込み空間（Embedding Space）に保持できているかを表す能力である。  
先行研究では、この層における失敗や能力不足を以下の概念で定義している。

* **Visual Detail Retention / Fine-Grained Visual Discriminability**: 高次の意味カテゴリ（「椅子」や「車」など）に不変な特徴へ落とし込まれる前の、局所的な形状・輪郭の解像度を保持する能力。  
* **CLIP-Blindness / Visual Myopia**: 対照学習（Contrastive Learning）で事前学習されたCLIP型エンコーダが、大まかな記述（Coarse Captions）と画像を適合させる過程で、テキスト側で言及されない細部の視覚トークンを捨象・圧縮してしまう現象1。  
* **Encoder Bottleneck / Representation Collapse**: 視覚エンコーダの最終層表現がグローバルな意味特徴に過剰に最適化され、幾何学的に重要な局所高周波成分（Edges, Curvatures）が消失し、下流の投影層（Projector）やLLM側で復元不能になる情報ボトルネック2。

### **1.2 単独切り出しのための診断法・ベンチマーク**

視覚エンコーダが微細な幾何情報を「言語非依存に保持しているか」をLLMの推論能力や言語プライアから分離して切り出すため、以下の手法が用いられる。

> 1. **MMVP-VLM（CLIP-Blind Pairs）**: 人間には一目で区別できるが、CLIPの視覚埋め込みコサイン類似度が極めて高く同一表現として潰れてしまう画像ペア（CLIP-blind pairs）を集積したベンチマーク1。言語生成を介さず、画像埋め込み間の距離だけで評価する。  
> 2. **DINOv2 vs CLIPのLinear Probing分析**: テキスト対照学習（CLIP）と自己教師あり視覚特徴学習（DINOv2）の特徴量上に線形分類器（Linear Probe）を設置し、無背景線画や同シルエット製品の幾何特徴判別精度を直接比較する手法。DINOv2は幾何構造の保持に優れる一方、CLIPは局所特徴の欠落が著しいことが定量的に示される1。  
> 3. **拡散モデル・反転生成による再構成プローブ（UnCLIP / Diffusion Inversion Probe）**: 視覚エンコーダから出力された埋め込みベクトル（\[CLS\]またはパッチトークン）のみを条件（Condition）として固定し、拡散モデルで画像を再構成させる手法1。再構成画像においてパーツの欠損や面取りの潰れが発生した場合、エンコーダ段階で情報が永久に失われていることが直感的に証明される。

### **1.3 事後学習による層A改善手法の網羅的整理**

視覚エンコーダの細部保持能力を高めるため、テキスト対照学習の枠組みを超えた生成フィードバック（Generative Feedback）や領域特化対照学習による事後学習手法が提案されている。

| 手法名 | 発表年 | 会議・ジャーナル | ベースモデル | 事後学習の種類 | 学習データと規模 | 評価ベンチ | 向上幅（人間性能ギャップ） | 他能力への影響 | 入手先URL |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **DIVA** | 2024/2025 | ICLR 20256 | CLIP ViT-L/14, MetaCLIP8 | 生成的フィードバック（T2I Diffusionによる自己教師あり学習）6 | テキストなしの画像単体データ（Unlabeled Images）6 | MMVP-VLM, Dense Segmentation4 | MMVP-VLMにてスコア **\+3.0%〜+7.0%** 向上6 | 29の画像分類・検索ベンチマークで高いゼロショット性能を完全に維持6 | [GitHub](https://github.com/baaivision/DIVA) \[cite: 7\] |
| **un²CLIP** | 2025 | NeurIPS 202510 | OpenAI CLIP ViT-L/14, OpenCLIP ViT-H/14, SigLIP ViT-SO/3844 | 拡散生成器（unCLIP）の反転による視覚エンコーダ微調整（生成器固定）1 | Stable unCLIPチェックポイント＋画像データ10 | MMVP-VLM, CV-Bench 2D COCO, Dense Segmentation1 | MMVP-VLMおよびCV-Benchにて既存のDIVAを一貫して上回る大幅改善1 | テキストエンコーダとの空間的整列を保持し、一般MLLMタスクでもグローバル意味を維持1 | [GitHub](https://github.com/LiYinqi/un2CLIP) \[cite: 10\] |
| **GenHancer** | 2025 | ICCV 202514 / arXiv (v3: 2025/07)5 | OpenAI CLIP ViT-L/145 | 軽量デノイザーを用いた2段階生成事後学習（Class Token条件付け）5 | 画像単体データ＋軽量デノイザー5 | MMVP-VLM5 | OpenAI CLIP上でMMVP-VLM精度 **\+6.0%** 向上（DIVAを超える精度向上）5 | 軽量なモジュール追加により他タスクでの埋め込み崩壊を回避5 | [Project Page](https://mashijie1028.github.io/GenHancer/) \[cite: 16\] |
| **FineCLIP** | 2024 | NeurIPS 202417 | ViT-B/16, ViT-L/142 | リアルタイム自己蒸留＋パッチ・領域単位の対照学習17 | 生成された領域-テキストペアデータ（Regional Crop-Text Pairs）17 | オープンボキャブラリー検出/分割、画像・領域検索17 | 領域レベルの認識精度（Box/Mask Top-1）で従来CLIPを著しく更新2 | グローバルな視覚-意味的一貫性を保持しつつ拡大性（Scaling）を提示17 | [NeurIPS Proceedings](https://proceedings.neurips.cc/paper_files/paper/2024/file/3122aaa22b2fe83f9cead1a696f65ceb-Paper-Conference.pdf) \[cite: 17\] |
| **FG-CLIP / FG-CLIP 2** | 2025 | ICML 202518 | ViT-B/16, ViT-L/142 | マルチグレイン対照学習＋ハードネガティブ対照損失18 | FineHARD（1.6Bキャプション＋10Mハードネガティブ）18 | 細粒度画像検索、ADE20K, MS COCO, MLLMベンチマーク18 | 局所領域・極小の視覚差異判別においてSOTAを達成18 | 1.6億超の長文アノテーションによりグローバル意味表現も同時に強化18 | [GitHub](https://github.com/360CVGroup/FG-CLIP) \[cite: 19\] |
| **SFF-CLIP** | 2025/2026 | arXiv (2026/07: v1)2 ※暫定 | ViT-B/16, ViT-L/142 | 自己アノテーション型細粒度アライメント（フレーズ熱マップ＋モーメンタム損失）2 | 追加アノテーション不要の標準画像-テキストペア2 | MS COCO, ADE20K, 領域表現ベンチマーク2 | MS COCO Box Top-1精度で **31.2% → 36.9%** (ViT-L) へ向上2 | 外部領域提案やアノテーション追加なしでグローバル表現を維持2 | [arXiv](https://arxiv.org/abs/2607.13661) \[cite: 2\] |
| **CLIP-IN** | 2025 | NeurIPS 202521 | CLIP / MLLM Visual Encoder21 | 画像編集データを用いた対称ハードネガティブ対照学習21 | Instruction-Editingハードネガティブペア21 | MMVP, 細粒度視覚認識, MLLMハルシネーション評価21 | MMVP精度を大きく向上させ、MLLM統合時のハルシネーションを抑制21 | 事前学習の堅牢なゼロショット分類・検索性能を一切阻害しない21 | [NeurIPS Proceedings](https://neurips.cc/virtual/2025/poster/118953) \[cite: 21\] |

### **1.4 視覚エンコーダのみの書き換えに伴う限界と副作用**

LLMやProjectorを触らず、視覚エンコーダ（CLIP ViT等）の表現のみを事後学習で書き換えるアプローチには明確な限界と副作用が存在する。

* **クロスモーダル・アライメントの崩壊（Feature Drift）**: 視覚エンコーダが高周波な幾何・幾何学的差異を捉えられるよう空間を補正しても、ペアとなる言語エンコーダ（Text Encoder）を同時に更新しない場合、視覚埋め込みとテキスト埋め込みの幾何的・距離的対応関係が歪む1。  
* **ゼロショット一般化能力の低下（Catastrophic Forgetting）**: 特定の局所幾何（線画やシルエット）にエンコーダのパラメータを最適化しすぎると、広域なセマンティクスに基づく画像分類や概念検索といった事前学習時の汎用表現が劣化する傾向がある6。  
* **計算コストの肥大化**: DIVAやun²CLIPなどの拡散モデル（Diffusion Models）のデノイジングフィードバックを用いる手法は、順伝播・逆伝播時に重い生成モデルを計算グラフに保持するため、標準的な対照学習に比べてメモリ・計算コストが膨大になる6。

### **この研究への含意**

意匠特許図面のような無背景・線画データにおいては、一般的なCLIPが事前学習で獲得した高次セマンティクス空間はほぼ無効化され、エンコーダ段階で面取りやパーツ比率といった幾何特徴が情報除去されている可能性が極めて高い。したがって、下流のLLMやLoRAをいくら調整しても物理的な情報上限（Encoder Bottleneck）に阻まれるため、まず層Aを強化するun²CLIPやGenHancer型の自己教師あり事後学習を前処理として適用することが不可欠である。

## **2\. 層B：視覚-意味接地（Visual-Semantic Grounding）**

### **2.1 呼称と学術的定義**

層Bは、視覚エンコーダが保持した幾何的・微細な視覚差分を、テキスト側の正確な概念・指示対象・属性記述へと正しく結びつける能力を表す。

* **Visual Grounding / Grounded Perception / Sensory Grounding / Modality Alignment**: 生成される言語応答や選択肢の判断が、画像内の実際の視覚的証拠（Visual Evidence）に1対1で強固に固定（Anchor）されている状態。  
* **狭義の接地 vs 広義の接地**:  
  * **狭義の接地**: 画像内の特定のバウンディングボックス（Bounding Box）や画素領域（Segmentation Mask）とテキストの物理的局在を一致させる能力（Referring Expression Comprehension等）。  
  * **広義の接地**: テキスト生成および多肢選択において、画像に存在しない属性や関係性を捏造せず、画像から抽出された事実に完全に基づいて回答を誘導する能力（Hallucination Suppression / Grounded Decision-Making）21。  
* **Ungrounded Hallucination**: 画像表現上には正解の手がかりが存在するにもかかわらず、LLMの持つ強大な言語プライア（単語の共起や「〇〇という名前ならこういう形状であるはずだ」という先入観）に引っ張られ、画像に根拠のない説明を捏造して誤答を選ぶ現象22。

### **2.2 単独切り出しのための診断法・ベンチマーク**

層Bの失敗（画像には映っているが言語に正しく接地できない、あるいは言語プライアで誤答する）を孤立して評価するための診断法には以下がある。

> 1. **NaturalBench**: 自然に発生した対照的画像・質問ペア（Natural Adversarial Samples）により、画像を見ずに言語文脈のみで答える「Blind Solution」を徹底的に排除したベンチマーク1。質問に対して画像コンテンツを正しく参照しているかのみを精密に測定する。  
> 2. **POPE / HallusionBench**: 存在しないオブジェクトや属性に対するモデルの回答を測定し、言語プライアによるハルシネーション（Ungrounded hallucination）の発生率を評価する13。  
> 3. **SPEC / Counterfactual Visual Evaluation**: 画像内の特定の細部形状や位置関係を変更したカウンタファクチュアル（反実仮想）な画像対を用意し、モデルが視覚変化を捉えて回答を正しく変更できるかを検証する。

### **2.3 事後学習による層B改善手法の網羅的整理**

アテンションや投影層（Projector）、言語モデル層を事後学習し、視覚証拠とテキスト生成の結合を強化する手法を整理する。

| 手法名 | 発表年 | 会議・ジャーナル | ベースモデル | 事後学習の種類 | 学習データと規模 | 評価ベンチ | 向上幅（人間性能ギャップ） | 他能力への影響 | 入手先URL |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **S-VCO** | 2025 | ACL 202525 | 標準的VLMバックボーン25 | 対象的視覚対照最適化（Symmetrical Visual Contrastive Optimization）25 | 微細な対向ペアデータ（Symmetrical Contrastive Pairs）25 | Grounding / Visual Hallucinationベンチマーク25 | 視覚フィードバックの非対称性を解消し、ハルシネーションを著しく低減25 | 指示追従能力および一般的な言語対話性能を維持25 | [ACL Anthology](https://aclanthology.org/2025.acl-long.1462.pdf) \[cite: 25\] |
| **Finedefics** | 2025 | ICLR 202526 | LLaVA-1.5, Qwen-VL等のMLLM26 | 細粒度属性抽出モジュール＋知覚に基づく回答導出（SFT/Prompting）26 | 属性アノテーション付き細粒度画像-テキストデータ30 | FGIC (Fine-Grained Image Classification: CUB, Flowers等)26 | 同一パラメータ規模の既存MLLMを大幅に上回る識別精度を達成26 | モジュール化設計によりモデルの解釈性と適応性が大幅に向上29 | [GitHub](https://github.com/PKU-ICST-MIPL/Finedefics_ICLR2025) \[cite: 27\] |
| **RLHF-V** | 2024 | CVPR / ResearchGate22 | LLaVA等22 | 細粒度人件フィードバックによる人行動アライメント（Segment/Token-level RLHF）22 | モデル生成ハルシネーションを修正した正負選好データセット22 | POPE, MME, HallusionBench22 | 視覚ハルシネーション率を劇的に低下させ、信頼性を大幅向上22 | 一般的テキスト応答の品質を落とさずに応答精度を均一化22 | [ResearchGate](https://www.researchgate.net/publication/384208523) \[cite: 22\] |
| **AHNPL** | 2025 | IJCAI 202533 | VLM/CLIPバックボーン33 | 適応的ハードネガティブ摂動学習（テキストハードネガティブの視覚ドメイン写像＋動的マージン損失）33 | 意味的摂動を加えた画像・テキストハードネガティブ33 | Winoground, SugarCREPE, Compositional Reasoning (CR)33 | 複合的構成推論（CR）において従来アライメント手法を凌駕33 | 難度の高い正負ペアの接地品質を動的最適化35 | [GitHub](https://github.com/nynu-BDAI/AHNPL) \[cite: 33\] |
| **CLoVe** | 2024/2025 | Continual Learning Workshop36 | VLM / MLLM36 | 継続学習に基づく接地選好最適化（Loss Vector Clustering）36 | 段階的タスクデータ（Incremental VQA Datasets）36 | CLOVE-function, VQACL36 | 破滅的忘却を防ぎつつ視覚接地能力を維持28 | 既習タスクでの精度維持率が極めて高い28 | [GitHub](https://github.com/YuyangSunshine/Awesome-Continual-learning-of-Vision-Language-Models) \[cite: 36\] |
| **AutoSEP** | 2025 | ICLR 202531 | MLLM (Black-box access)31 | 反復的自己増強プロンプト学習（無認可データを用いたプロンプト自己最適化）31 | ラベルなし画像・対照ペアラベル31 | 細粒度画像分類 (FGIC)31 | 微妙な視覚細部に着目するプロンプトを自動生成し分類精度を向上31 | 重みの更新を必要としないため、汎用対話能力を完全に保持31 | [OpenReview](https://openreview.net/forum?id=VNTj7PGlrz) \[cite: 31\] |
| **HCG-LVLM** | 2025 | OpenReview (2025)40 ※暫定 | Large Vision-Language Models40 | 階層的文脈接地（Hierarchical Contextual Grounding）事後学習40 | 細粒度視覚言語接地データセット40 | Fine-Grained Visual-Language Understanding40 | 細粒度な視覚言語アライメントと構成的理解において大幅改善40 | 頑健な接地能力の付与によりハルシネーションを抑制40 | [OpenReview](https://openreview.net/forum?id=vRmehPBiM1) \[cite: 40\] |

### **2.4 「保持成立・接地失敗（A成立・B失敗）」の実証・分析研究**

分析研究によれば、「視覚表現としては内部に判別情報が存在するのに、LLMが誤った回答を出力する」という**A成立・B失敗**の事例が多数報告されている。

* **分析手法**: DINOv2や補正後のCLIP特徴量に対してLinear Probeを学習させると幾何差分を90%以上の精度で分離できるのに対し、同一の視覚特徴量を接続したVLM（LLaVA等）にテキスト問いかけを行うと正解率が50%（チャンスレベル）近くまで低下する現象。  
* **原因の解明**: これは投影層（Projector）およびLLMのアテンションメカニズムが、視覚トークンの局所的な幾何的差異よりも、入力テキストに含まれる製品タイトルや一般的な概念の統計的共起確率（Language Prior）を過剰に優先するために起こる。モデルは「画像を見る」ことをスキップし、言語的にもっともらしい選択肢を選んでしまう。

### **この研究への含意**

本研究のベンチマーク（意匠特許図面＋DINOv2による酷似選択肢）は、言語文脈が一切手がかりにならない「Pure Visual Discrimination」の実験系である。したがって、モデルが言語プライアに頼って推論しようとする傾向（層Bの失敗）を断ち切るため、AHNPLやS-VCOのようにハードネガティブを用いた「画像証拠にアテンションを強制固定する」事後学習目的関数を適用することが極めて有効である。

## **3\. 層Reasoning：比較推論（Visual Comparative Reasoning）**

### **3.1 呼称と学術的定義**

層Reasoningは、正しく保持され（層A）、意味的に接地された（層B）微細な視覚的特徴をもとに、複数の候補画像や画像内の複数の局所パーツを明示的に見比べ（Spot-the-difference）、その対比的差分から説得力のある根拠を導出して判別を行う高次推論能力である。

* **Visual Comparative Reasoning / Difference Reasoning / Difference Spotting**: 1つの画像内、または複数画像（Multi-image）の対応する部位をアラインメントし、位相的・幾何学的な「違い」を検知して推論に組み込む能力41。  
* **Fine-Grained Visual Chain-of-Thought (CoT)**: 単に「答えはA」と出力するのではなく、「画像Aの右上のアール（曲率）は直角に近いが、選択肢Bの記載は丸みを帯びている」といった局所視覚事実の段階的言語化を行う思考プロセス43。

### **3.2 単独切り出しのための診断法・ベンチマーク**

モデルが単一画像の絶対的な理解にとどまらず、「比較・見比べ」を行えているかを対照的に測定する手法は以下の通りである。

> 1. **BLINK / CV-Bench (2D Spatial & Relative Perception)**: 視覚的トレース、絶対・相対位置、幾何学的アライメント、間違い探し（Spot-the-difference）に特化したベンチマーク1。  
> 2. **SPATIALRGPT-Bench**: 複雑な幾何学的構造や位置関係の論理推論能力を測定するベンチマーク45。  
> 3. **Multi-Candidate Contrastive Prompting**: 複数選択肢の画像を同時にグリッド配置、または並列入力し、「選択肢1と選択肢2の形状の差分を箇条書きで述べてから選べ」という指示に対する正答率とCoTの整合性を評価する手法。

### **3.3 事後学習による比較推論改善手法の網羅的整理**

推論段階での視覚比較能力を高める事後学習手法（特にRLHF/GRPO/DPOを用いた選好最適化）を整理する。

| 手法名 | 発表年 | 会議・ジャーナル | ベースモデル | 事後学習の種類 | 学習データと規模 | 評価ベンチ | 向上幅（人間性能ギャップ） | 他能力への影響 | 入手先URL |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Visual-RFT** | 2025 | ICCV 202546 | Qwen2-VL-2/7B46 | GRPOに基づく強化学習事後学習（検証可能な視覚知覚報酬関数の導入）43 | わずか **100〜239枚** の極小画像サンプル43 | 1-shot Fine-grained Classification, Few-shot Detection43 | 1-shot微細分類にて精度 **\+24.3%** 向上（SFTは-4.3%低下）43 | 少数のサンプルで極めて強力な汎化性能とドメインシフト耐性を発揮43 | [GitHub](https://github.com/Liuziyu77/Visual-RFT) \[cite: 46\] |
| **PIVOT** | 2024/2025 | ICLR 202550 | 凍結VLM (GPT-4V/PaLM-E等)51 | 反復的視覚プロンプティング（画像上に直接矢印・マーカーを描画するVisual CoT）50 | 反復描画軌跡データ50 | Actionable Reasoning, Embodied Navigation/Manipulation50 | ゼロショット環境下での空間・対比推論精度を大幅に引き上げ50 | 重み更新を伴わないため事前学習知識の崩壊リスクがゼロ50 | [arXiv](https://arxiv.org/abs/2404.13046) \[cite: 50\] |
| **fDPO (SpatialReasoner-R1)** | 2025 | Google/UIUC (TuniX)53 | オープンVLMバックボーン53 | 細粒度直接選好最適化（Segment-specific Preference Granularity）54 | 空間論理選好ペアデータ（fDPO Preference Dataset）54 | SPATIALRGPT-Bench45 | 最も強力なベースラインを **\+9.8%** 上回るSOTAを更新45 | 細粒度の空間論理と多段階CoTの整合性が飛躍的に安定54 | [Google Blog](https://opensource.googleblog.com/2025/12/spatialreasoner-teaching-vlms-to-see-structure-accelerated-with-tunix-on-tpus.html) \[cite: 53\] |
| **Fine-R1** | 2026 | ICLR 202627 ※暫定 | MLLM (Qwen2-VL等)44 | 細粒度視覚識別に特化したChain-of-Thought推論事後学習44 | 細粒度認識CoTアノテーションデータ44 | 細粒度視覚認識ベンチマーク44 | 複雑な類似カテゴリ識別においてCoT推論による精度跳躍を実現44 | 細粒度領域に対するモデルの幻覚を防止し推論プロセスを透明化44 | [GitHub](https://github.com/PKU-ICST-MIPL/MRA_TIP) \[cite: 27\] |
| **TPO (Thought Preference Optimization)** | 2025 | IBM Granite 3.257 | Granite 3.2 Instruct / Vision57 | 思考選好最適化に基づくRL（人間アノテーション不要のCoT強化）57 | モデル生成思考軌跡と評価器モデルによる選好データ59 | 指示追従、複雑理由付けベンチマーク57 | 8BモデルでCoTをオンにすることでGPT-4o/Claude 3.5 Sonnetに匹敵57 | 推論機能をトグル可能にし、一般タスク性能の劣化を回避57 | [IBM Announcement](https://www.ibm.com/new/announcements/ibm-granite-3-2-open-source-reasoning-and-vision) \[cite: 57\] |
| **Visual Jigsaw** | 2025 | NeurIPS 202541 | MLLM41 | 画像を分割・シャッフルし幾何アライメントを復元させる自己教師あり事後学習41 | シャッフルされた画像入力（追加アノテーション不要）41 | 全体的な視覚理解・構造把握ベンチマーク41 | MLLMの本質的な視覚理解・幾何推論精度を飛躍的に補強41 | 単一タスクへの過剰適合を起こさず広範な視覚問題へ汎化41 | [Project Page](https://penghao-wu.github.io/visual_jigsaw/) \[cite: 42\] |
| **Reason-RFT** | 2025 | NeurIPS 202549 | VLM / MLLM49 | SFTとGRPOを組み合わせた2段階選好強化学習49 | 多様な推論タスク CoTデータセット49 | Counting, Structural Perception, Spatial Transformation49 | SOTAを更新し、ドメインシフト下での堅牢性を大幅向上49 | 過剰適合を排除し高い汎化性能とデータ効率を両立49 | [OpenReview](https://openreview.net/forum?id=NdScoAix25) \[cite: 49\] |

### **3.4 視覚CoT・推論強化と知覚能力の相互作用の定量化**

「推論能力（Reasoning）を強化すれば知覚（Perception）のボトルネックを越えられるか」に関する定量的研究では、双方向の重要な証拠が得られている。

* **推論が知覚のボトルネックを超えることはできない（Perception Bottleneck Theory）**: エンコーダ（層A）において最初から特徴量が潰れている場合、どれほどCoTトークンを長く生成させても（Inference-time Scalingを行っても）、存在しない視覚情報を「妄想」して補完する結果（Hallucinated CoT）に陥る。知覚能力が推論能力の絶対的な上限（Rate-Limiting Factor）として機能する。  
* **対比型推論（Comparative CoT）による知覚の補強効果**: 一方、エンコーダ内に潜在的に特徴量が保持されている（層A成立）場合、直接回答を出力させるよりも「候補1と候補2の図面における角のR処理の違いを比較せよ」というComparative Promptingを与えたり、Visual-RFTのようにGRPOで「正誤の対比ステップ」に報酬を与えることで、アテンションが解像度の高い局所領域へと誘導（Active Foveation）され、実質的な知覚判別精度が劇的に向上することが確認されている43。

### **この研究への含意**

本研究の8択問題に対しては、単に1枚の図面を説明させるSFTではなく、Visual-RFTやSpatialReasoner-R1（fDPO）のパラダイムを応用することが極めて有効である。「正解候補とDINOv2で選ばれた酷似誤答候補の幾何学的差分」を明示的に記述させる比較型CoTを構築し、RLVR（ルールベース検証可能報酬）によって学習させることで、最小限のデータ量で判別精度を劇的に向上させられる可能性がある。

## **4\. 層をまたぐ「原因の帰属」（Attribution Across Layers）**

### **4.1 エラー原因を切り分ける診断フレームワーク**

VLMが誤答した際、その失敗がA（保持）、B（接地）、Reasoning（推論）のどの層に起因するのかを厳密に切り分けるためのステップバイステップの診断論理を提案する。

> 1. **Step 1: エンコーダ表現力テスト（層Aの切り出し）**  
   * 誤答した画像対から視覚エンコーダの埋め込みベクトルを取り出し、Linear Probe（SVMまたは軽量MLP）を訓練するか、コサイン類似度を測定する。  
   * **判定**: 線形分離が不可能、またはコサイン類似度が極めて1に近い（例: \>0.98）場合、失敗は「層A（Encoder Bottleneck）」に帰属する。  
> 2. **Step 2: 直接記述・抽出テスト（層Bの切り出し）**  
   * 線形分離が可能な場合、VLMに対して選択肢を与えず、「画像内の局所特徴（例: 正面フレームの曲率やパーツの有無）を詳細に説明せよ」と問う（Captioning / Attribute Extraction）。  
   * **判定**: 視覚的には明らかな特徴を文章化できず捏造した場合、失敗は「層B（Visual-Semantic Grounding）」に帰属する。  
> 3. **Step 3: 比較対比テスト（層Reasoningの切り出し）**  
   * 局所特徴の記述は正しく行えるにもかかわらず、8択のタイトル選択で誤答する場合、または単一比較で判別を誤る場合。  
   * **判定**: 失敗は「層Reasoning（Visual Comparative Reasoning）」に帰属する。

### **4.2 SFTとDPO/RLにおける内部表現・アテンション・判別境界の比較**

事後学習の手法（SFT vs DPO/GRPO）によって、モデル内部の視覚表現・アテンション・判別境界がどのように変化するかを先行研究の可視化分析から比較する。

* **Supervised Fine-Tuning (SFT)**:  
  * **変化**: SFTは主に言語モデル層の出力分布を教師データの形式（フォーマット）に適合させる。  
  * **副作用**: 視覚アテンションマップ（Cross-Attention）は滑らか（Smooth/Blurred）になりがちで、特定の判別領域に集中しない。また、学習データに含まれる言語的な定型句を暗記（Memorization）する傾向が強く、判別境界（Decision Boundary）は過剰適合を起こしやすい49。  
* **Direct Preference Optimization (DPO) / Reinforcement Learning (GRPO)**:  
  * **変化**: 誤答（ハードネガティブ）と正答の対比フィードバックを受けるため、モデルは正誤を分ける「決定的な幾何領域」にアテンションを激しく集中させる（Attention Sharpening）。  
  * **利点**: 内部表現空間において、DINOv2によって選ばれた酷似した誤答クラスタの境界上にマージン（Margin）を強制的に形成するため、微細な差分に対する判別境界が非常に精緻化される35。

### **4.3 事後学習の投下先における費用対効果（ROI）の比較分析**

事後学習の計算リソースやデータ収集コストを「どこに投入すべきか」について、先行研究の知見をまとめる。

> 1. **層A（エンコーダ再学習）への投資**:  
   * **コスト**: 非常に高い（拡散モデルを用いた生成フィードバックや、億単位のペアデータが必要）6。  
   * **効果**: 一度改善されればすべての下流タスクの絶対的な性能上限が引き上がる（基盤的価値）。  
> 2. **層B（SFT / Projector調整）への投資**:  
   * **コスト**: 低〜中程度（数万〜数十万のデータセットで十分）。  
   * **効果**: ハルシネーションの低減や指示追従の改善には即効性があるが、幾何的難問に対しては言語プライアによるショートカットを誘発しやすく、精度の伸び代が飽和しやすい。  
> 3. **層Reasoning（選好最適化 / Visual-RFT）への投資**:  
   * **コスト**: **最も費用対効果（ROI）が高い**。  
   * **根拠**: Visual-RFTが実証したように、適切な検証可能報酬（Verifiable Rewards）を設計すれば、わずか数百（100〜200程度）の高品質な比較データとGRPOを用いるだけで、1-shot精度が+24.3%跳躍するなど、最小のデータ・計算量で極めて大きな精度向上が得られる43。

## **5\. 論文のポジショニング戦略**

### **5.1 トップカンファレンスにおける「識別ベンチマーク＋事後学習」型論文の標準構成**

メインカンファレンス（CVPR, ICCV, ECCV, NeurIPS, ICLR）に採択された成功例（*Eyes Wide Shut*, *Cambrian-1*, *NaturalBench*, *SPEC*, *Visual-RFT*, *PIVOT*）を分析すると、単なる「特定ドメインの応用（Application/Industry track）」ではなく、「VLMの根本的知覚メカニズムの解明と一般論化」として論文を構成する明確なパターンが存在する。  
成功する論文の標準的な4段構成は以下の通りである。

> 1. **概念化（Conceptualization）**: 対象タスク（意図特許図面判別）を、単なる「特許の検索」ではなく、「**言語プライアが一切通用しない純粋幾何識別（Pure Visual Discrimination under Zero Language-Prior）**」というVLMの極限的な知覚能力プローブとして再定義する。  
> 2. **根本原因の可視化と診断（Diagnostic Probing）**: 既存のSOTAモデル（GPT-4o, Gemini 1.5 Pro, Qwen2-VL）がなぜ失敗するのかを本レポートの3層（A/B/Reasoning）に沿って実験的に解剖し、「問題の根本はLLMの推論力ではなく、エンコーダの幾何情報脱落言語プライアへの依存にある」ことを立証する。  
> 3. **一般転移可能な事後学習レシピの提案（Transferable Post-training Paradigm）**: 特定ドメイン知識を暗記させるアプローチ（ニッチ製品名のLoRA学習）を意図的に排除し、「幾何特徴を保持しつつ、対比推論を誘発する汎用的な事後学習フレームワーク（例: Contrastive RLVR \+ Generative Visual Retention）」を提案する。  
> 4. **タスク横断的評価（Cross-Task Generalization）**: 自作ベンチマークだけでなく、MMVP, NaturalBench, CV-Bench, BLINKなどの標準的VLM知覚・推論ベンチマークに提案手法を適用し、汎用的に視覚知覚能力が向上したことを示す1。

### **5.2 特定ドメイン色を排した一般能力（General Capability）としての提示技法**

タイトルや要旨から「USPTO Patent」というドメイン固有のフレーズを前面に出さず、コンピュータビジョン全般の基礎研究として提示するためのタイトリングおよび主張の対比を以下に示す。

* **避けるべきドメイン依存のタイトル例**:  
  * *❌ "Improving Design Patent Retrieval using LoRA Fine-Tuning on USPTO Drawings"*（Industry trackとみなされ落とされる典型例）  
* **採択されやすい一般能力志向のタイトル例**:  
  * *⭕ "Eyes Wide Shut in Pure Geometry: Benchmarking and Enhancing Fine-Grained Visual Discrimination in VLMs without Language Priors"*  
  * *⭕ "Beyond Language Shortcuts: Tri-Layer Post-Training for Fine-Grained Visual Comparative Reasoning"*  
* **主張の並べ方（Abstract / Introductionのフレームワーク）**:  
  * **Hook**: 現代のVLMは高度な対話能力を見せるが、テキスト文脈のない純粋な線画・幾何形状の微細差分（Fine-grained Geometry）の識別に着目すると、最新モデル（GPT-5等）でも著しく性能が崩壊する。  
  * **Core Problem**: この原因は、対照学習による視覚エンコーダの細部脱落（層A）と、言語プライアへの過剰適合（層B）の複合作用にある。  
  * **Method**: 我々は、幾何学的保持を最強化する事後学習と、検証可能報酬（Verifiable Rewards）を用いた対比型強化学習（Visual Comparative RL）を提案する。  
  * **Result**: 本手法は、極小データセットでありながら特許図面識別精度を大幅に向上させると同時に、MMVPやCV-Benchといった一般的な細粒度視覚ベンチマークにおいてもSOTAを更新した。

## **6\. まとめ：現時点の主張と手法上のギャップ**

これまでの調査に基づき、視覚的保持（A）、視覚-意味接地（B）、比較推論（Reasoning）の3層に関して事後学習の観点から導き出される現在の確立された主張と、未だ解決されていない技術的ギャップを箇条書きで整理する。

### **6.1 層別の事後学習に関する合意事項（現時点で言える主張）**

* **層A（視覚的保持）に関する主張**:  
  * 視覚エンコーダに対する生成モデル（T2I Diffusion / unCLIP）からのデノイジング・フィードバックや反転学習（DIVA, un²CLIP, GenHancer）は、事前学習で捨象された高周波の幾何・輪郭情報を再復元させる上で極めて効果的である1。  
  * 既存の事前学習テキストエンコーダとのアライメントを保つためには、生成モデル側を完全に固定（Frozen）し、条件付け経路のみを最適化する手法（un²CLIP等）が最も副作用が少ない1。  
* **層B（視覚-意味接地）に関する主張**:  
  * 言語プライアによるハルシネーション（Ungrounded Hallucination）を抑制するには、単一の正解ペアだけでなく、意味的・視覚的に厳密に構成されたハードネガティブペアを用いた対照最適化（AHNPL, S-VCO, CLIP-IN）が不可欠である21。  
  * SFTのみの学習はモデルに特定の応答パターンを暗記させやすく、言語プライアによるショートカット学習を促進してしまうリスクがある49。  
* **層Reasoning（比較推論）に関する主張**:  
  * 推論段階における思考プロセス（CoT）の強化は、適切な報酬設計がなされていれば、モデルのアテンションを識別領域へアクティブに誘導し、知覚精度を飛躍的に向上させる43。  
  * 強化学習（GRPO/RFT）を用いた選好最適化は、SFTに比べて圧倒的なデータ効率（100〜200サンプル程度）を誇り、ドメイン外データへの高い汎化性能を提供する43。

### **6.2 手法上の未解消ギャップ（調査から見えた技術的課題）**

* **ギャップ1：無背景・幾何線画（Line Drawings）に特化した自己教師あり生成フィードバックの不在**:  
  * 現在の層A改善手法（DIVA, GenHancer等）は、自然画像（Stable Diffusion等）で訓練された生成モデルの事前学習知識に依存している5。質感や背景が存在しない「純粋な幾何線画や3D CADシルエット」に対して最適な拡散フィードバックを与える手法は確立されていない。  
* **ギャップ2：知覚学習（Perception）と言語推論（Reasoning）の同時最適化における勾配衝突（Gradient Conflict）**:  
  * 視覚エンコーダの幾何特徴抽出（低レベル知覚）と言語モデルの多段階推論（高次論理）を同一のエンドツーエンド学習で同時に最適化しようとすると、目的関数の勾配が干渉し合い、パフォーマンスが相互に低下する問題（EgoMotionで指摘された知覚-推論の交絡問題）が存在する62。  
* **ギャップ3：バウンディングボックス非依存の「純粋幾何対比」に対する検証可能報酬（Verifiable Reward）の不足**:  
  * 従来のVisual-RFT等は、物体検出のIoUや単一カテゴリの正誤結果を強化学習の報酬として用いている43。しかし、8択の類似シルエット間における「局所的な輪郭・曲率・幾何差異の整合性」を直接数式化してGRPOにフィードバックする自動報酬関数（Verifiable Geometric Reward）の設計手法は未だ未拓である。  
* **ギャップ4：視覚エンコーダ調整時の言語アライメント維持とゼロショット保持のトレードオフ**:  
  * 視覚エンコーダの幾何保持能を極限まで高めることと、既存のLLM/Projectorとのクロスモーダル表現の整合性を破綻させずに維持することの完全な両立手法は未解決であり、依然として軽量な再アライメント工程の手探りが続いている1。

#### **引用文献**

> 1. un$^2$CLIP: Improving CLIP's Visual Detail Capturing Ability via, [https://www.alphaxiv.org/abs/2505.24517](https://www.alphaxiv.org/abs/2505.24517)  
> 2. Fine-grained CLIP fine-tuning with self-annotated region alignment, [https://arxiv.org/html/2607.13661v1](https://arxiv.org/html/2607.13661v1)  
> 3. Scalable Knowledge Distillation from Diffusion Models \- NeurIPS 2026, [https://neurips.cc/virtual/2025/poster/116899](https://neurips.cc/virtual/2025/poster/116899)  
> 4. Improving CLIP's Visual Detail Capturing Ability via Inverting unCLIP, [https://neurips.cc/virtual/2025/poster/116340](https://neurips.cc/virtual/2025/poster/116340)  
> 5. GenHancer: Imperfect Generative Models are Secretly Strong Vision, [https://arxiv.org/abs/2503.19480](https://arxiv.org/abs/2503.19480)  
> 6. Diffusion Feedback Helps CLIP See Better \- OpenReview, [https://openreview.net/forum?id=tLFWU6izoA](https://openreview.net/forum?id=tLFWU6izoA)  
> 7. baaivision/DIVA \- Diffusion Feedback Helps CLIP See Better \- GitHub, [https://github.com/baaivision/DIVA](https://github.com/baaivision/DIVA)  
> 8. BAAI/DIVA \- Hugging Face, [https://huggingface.co/BAAI/DIVA](https://huggingface.co/BAAI/DIVA)  
> 9. DIVA \- GitHub Pages, [https://rubics-xuan.github.io/DIVA/](https://rubics-xuan.github.io/DIVA/)  
> 10. GitHub \- LiYinqi/un2CLIP: \[NeurIPS'25\] A work to improve CLIP's, [https://github.com/LiYinqi/un2CLIP](https://github.com/LiYinqi/un2CLIP)  
> 11. State Key Laboratory of AI Safety has 11 Papers Accepted by, [http://english.ict.cas.cn/events/an/202511/t20251113\_1115427.html](http://english.ict.cas.cn/events/an/202511/t20251113_1115427.html)  
> 12. Improving CLIP's Visual Detail Capturing Ability via Inverting unCLIP, [https://huggingface.co/papers/2505.24517](https://huggingface.co/papers/2505.24517)  
> 13. Improving CLIP's Visual Detail Capturing Ability via Inverting unCLIP, [https://openreview.net/forum?id=kpdFjNitGW](https://openreview.net/forum?id=kpdFjNitGW)  
> 14. GenHancer: Imperfect Generative Models are Secretly ... \- GitHub, [https://github.com/zhaoyang97/Paper-Notes-en/blob/main/docs/ICCV2025/image\_generation/genhancer\_imperfect\_generative\_models\_are\_secretly\_strong\_vision-centric\_enhance.md](https://github.com/zhaoyang97/Paper-Notes-en/blob/main/docs/ICCV2025/image_generation/genhancer_imperfect_generative_models_are_secretly_strong_vision-centric_enhance.md)  
> 15. Strong Vision-Centric Enhancers Supplementary Material, [https://openaccess.thecvf.com/content/ICCV2025/supplemental/Ma\_GenHancer\_Imperfect\_Generative\_ICCV\_2025\_supplemental.pdf](https://openaccess.thecvf.com/content/ICCV2025/supplemental/Ma_GenHancer_Imperfect_Generative_ICCV_2025_supplemental.pdf)  
> 16. GenHancer: Imperfect Generative Models are Secretly Strong Vision, [https://mashijie1028.github.io/GenHancer/](https://mashijie1028.github.io/GenHancer/)  
> 17. FineCLIP: Self-distilled Region-based CLIP for Better Fine-grained, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/3122aaa22b2fe83f9cead1a696f65ceb-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/3122aaa22b2fe83f9cead1a696f65ceb-Paper-Conference.pdf)  
> 18. \[2505.05071\] FG-CLIP: Fine-Grained Visual and Textual Alignment, [https://arxiv.org/abs/2505.05071](https://arxiv.org/abs/2505.05071)  
> 19. FG-CLIP 2: 中英双语视觉语言对齐模型 \- GitHub, [https://github.com/360CVGroup/FG-CLIP](https://github.com/360CVGroup/FG-CLIP)  
> 20. VLM with Fine-grained Language-informed Image Representations, [https://huggingface.co/papers/2412.03561](https://huggingface.co/papers/2412.03561)  
> 21. NeurIPS Poster VITRIX-CLIPIN: Enhancing Fine-Grained Visual, [https://neurips.cc/virtual/2025/poster/118953](https://neurips.cc/virtual/2025/poster/118953)  
> 22. RLHF-V: Towards Trustworthy MLLMs via Behavior Alignment from, [https://www.researchgate.net/publication/384208523\_RLHF-V\_Towards\_Trustworthy\_MLLMs\_via\_Behavior\_Alignment\_from\_Fine-Grained\_Correctional\_Human\_Feedback](https://www.researchgate.net/publication/384208523_RLHF-V_Towards_Trustworthy_MLLMs_via_Behavior_Alignment_from_Fine-Grained_Correctional_Human_Feedback)  
> 23. Evaluating Vision-Language Models on Natural Adversarial Samples, [https://arxiv.org/abs/2410.14669](https://arxiv.org/abs/2410.14669)  
> 24. NaturalBench: Evaluating Vision-Language Models on Natural, [https://linzhiqiu.github.io/papers/naturalbench/](https://linzhiqiu.github.io/papers/naturalbench/)  
> 25. Aligning Vision-Language Models with Minimal Contrastive Images, [https://aclanthology.org/2025.acl-long.1462.pdf](https://aclanthology.org/2025.acl-long.1462.pdf)  
> 26. Track: Poster Session 6 \- ICLR 2027, [https://iclr.cc/virtual/2025/session/31976](https://iclr.cc/virtual/2025/session/31976)  
> 27. 北京大学多媒体信息处理研究室：源代码, [https://mipl.pku.edu.cn/paper/codeShare.php](https://mipl.pku.edu.cn/paper/codeShare.php)  
> 28. Continual Learning for VLMs: A Survey and Taxonomy Beyond, [https://www.researchgate.net/publication/394362666\_Continual\_Learning\_for\_VLMs\_A\_Survey\_and\_Taxonomy\_Beyond\_Forgetting](https://www.researchgate.net/publication/394362666_Continual_Learning_for_VLMs_A_Survey_and_Taxonomy_Beyond_Forgetting)  
> 29. A Survey on Compositional Visual Reasoning \- arXiv, [https://arxiv.org/html/2508.17298v2](https://arxiv.org/html/2508.17298v2)  
> 30. Daily Papers \- Hugging Face, [https://huggingface.co/papers?q=multi-modal](https://huggingface.co/papers?q=multi-modal)  
> 31. Unlabeled Data Improves Fine-Grained Image Zero-shot, [https://openreview.net/forum?id=VNTj7PGlrz](https://openreview.net/forum?id=VNTj7PGlrz)  
> 32. ToolFG: Towards Well-Grounded Fine-Grained Image Classification, [https://arxiv.org/html/2606.02518v1](https://arxiv.org/html/2606.02518v1)  
> 33. Visual Perturbation and Adaptive Hard Negative Contrastive ... \- IJCAI, [https://www.ijcai.org/proceedings/2025/605](https://www.ijcai.org/proceedings/2025/605)  
> 34. Visual Perturbation and Adaptive Hard Negative Contrastive ... \- arXiv, [https://arxiv.org/abs/2505.15576](https://arxiv.org/abs/2505.15576)  
> 35. Visual Perturbation and Adaptive Hard Negative Contrastive ... \- arXiv, [https://arxiv.org/pdf/2505.15576](https://arxiv.org/pdf/2505.15576)  
> 36. Awesome Continual Learning for Vision-Language Models & MLLMs, [https://github.com/YuyangSunshine/Awesome-Continual-learning-of-Vision-Language-Models](https://github.com/YuyangSunshine/Awesome-Continual-learning-of-Vision-Language-Models)  
> 37. ICML 2026 Papers, [https://icml.cc/virtual/2026/papers.html](https://icml.cc/virtual/2026/papers.html)  
> 38. Continual Learning for VLMs: A Survey and Taxonomy Beyond, [https://arxiv.org/html/2508.04227v1](https://arxiv.org/html/2508.04227v1)  
> 39. publications | Massimiliano Mancini \- GitHub Pages, [https://mancinimassimiliano.github.io/publications/](https://mancinimassimiliano.github.io/publications/)  
> 40. Bidirectional Hierarchical Reasoning for Fine-grained Visual, [https://openreview.net/forum?id=vRmehPBiM1](https://openreview.net/forum?id=vRmehPBiM1)  
> 41. Visual Jigsaw Post-Training Improves MLLMs | alphaXiv, [https://www.alphaxiv.org/abs/2509.25190](https://www.alphaxiv.org/abs/2509.25190)  
> 42. Visual Jigsaw Post-Training Improves MLLMs \- Penghao Wu, [https://penghao-wu.github.io/visual\_jigsaw/](https://penghao-wu.github.io/visual_jigsaw/)  
> 43. Visual-RFT: Visual Reinforcement Fine-Tuning \- arXiv, [https://arxiv.org/html/2503.01785v1](https://arxiv.org/html/2503.01785v1)  
> 44. Fine-R1: Make Multi-modal LLMs Excel in Fine-Grained Visual, [https://arxiv.org/html/2602.07605v1](https://arxiv.org/html/2602.07605v1)  
> 45. AutoSpatial: Visual-Language Reasoning for Social Robot, [https://www.researchgate.net/publication/398058890\_AutoSpatial\_Visual-Language\_Reasoning\_for\_Social\_Robot\_Navigation\_through\_Efficient\_Spatial\_Reasoning\_Learning](https://www.researchgate.net/publication/398058890_AutoSpatial_Visual-Language_Reasoning_for_Social_Robot_Navigation_through_Efficient_Spatial_Reasoning_Learning)  
> 46. Official repository of 'Visual-RFT: Visual Reinforcement Fine-Tuning, [https://github.com/Liuziyu77/Visual-RFT](https://github.com/Liuziyu77/Visual-RFT)  
> 47. \[2503.01785\] Visual-RFT: Visual Reinforcement Fine-Tuning \- arXiv, [https://arxiv.org/abs/2503.01785](https://arxiv.org/abs/2503.01785)  
> 48. (PDF) Visual-RFT: Visual Reinforcement Fine-Tuning \- ResearchGate, [https://www.researchgate.net/publication/389581647\_Visual-RFT\_Visual\_Reinforcement\_Fine-Tuning](https://www.researchgate.net/publication/389581647_Visual-RFT_Visual_Reinforcement_Fine-Tuning)  
> 49. Reason-RFT: Reinforcement Fine-Tuning for Visual Reasoning of, [https://openreview.net/forum?id=NdScoAix25](https://openreview.net/forum?id=NdScoAix25)  
> 50. VTInstructor: Visual Trajectory Prompting for Navigation Instruction, [https://arxiv.org/html/2608.15284v1](https://arxiv.org/html/2608.15284v1)  
> 51. ImagineNav++: Prompting Vision-Language Models as Embodied, [https://arxiv.org/html/2512.17435v3](https://arxiv.org/html/2512.17435v3)  
> 52. ‪Kuang-Huei Lee‬ \- ‪Google Scholar‬, [https://scholar.google.com/citations?user=rE7-N30AAAAJ\&hl=en](https://scholar.google.com/citations?user=rE7-N30AAAAJ&hl=en)  
> 53. SpatialReasoner: Teaching VLMs to "see" structure, [https://opensource.googleblog.com/2025/12/spatialreasoner-teaching-vlms-to-see-structure-accelerated-with-tunix-on-tpus.html](https://opensource.googleblog.com/2025/12/spatialreasoner-teaching-vlms-to-see-structure-accelerated-with-tunix-on-tpus.html)  
> 54. Google Open Source Blog: December 2025, [https://opensource.googleblog.com/2025/12/](https://opensource.googleblog.com/2025/12/)  
> 55. SpatiO: Adaptive Test-Time Orchestration of Vision-Language, [https://arxiv.org/html/2604.21190](https://arxiv.org/html/2604.21190)  
> 56. VistaHop: Benchmarking Long-Horizon Visual DeepSearch \- arXiv, [https://arxiv.org/html/2606.03273v2](https://arxiv.org/html/2606.03273v2)  
> 57. IBM Granite 3.2: open source reasoning and vision, [https://www.ibm.com/new/announcements/ibm-granite-3-2-open-source-reasoning-and-vision](https://www.ibm.com/new/announcements/ibm-granite-3-2-open-source-reasoning-and-vision)  
> 58. AI Distilled | Packt Learning Hub, [https://www.packtpub.com/en-us/learning/aidistilled?orderBy=most-viewed\&page=2](https://www.packtpub.com/en-us/learning/aidistilled?orderBy=most-viewed&page=2)  
> 59. Reasoning Beyond Limits: Advances and Open Problems for LLMs, [https://www.researchgate.net/publication/390354644\_Reasoning\_Beyond\_Limits\_Advances\_and\_Open\_Problems\_for\_LLMs](https://www.researchgate.net/publication/390354644_Reasoning_Beyond_Limits_Advances_and_Open_Problems_for_LLMs)  
> 60. IBM Granite 3.2 adds Enhanced Reasoning to its AI mix \- ZDNET, [https://www.zdnet.com/article/ibm-granite-3-2-adds-enhanced-reasoning-to-its-ai-mix/](https://www.zdnet.com/article/ibm-granite-3-2-adds-enhanced-reasoning-to-its-ai-mix/)  
> 61. Visual Jigsaw Post-Training Improves MLLMs \- OpenReview, [https://openreview.net/forum?id=tBf2SUzfZw](https://openreview.net/forum?id=tBf2SUzfZw)  
> 62. Hong Chang \- CatalyzeX, [https://www.catalyzex.com/author/Hong%20Chang](https://www.catalyzex.com/author/Hong%20Chang)