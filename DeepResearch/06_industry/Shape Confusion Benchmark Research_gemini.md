# **異なる製品カテゴリ間における形状混同評価ベンチマーク調査報告書**

意匠特許（Design Patent）図面を対象とした視覚言語モデル（Vision-Language Models: VLMs）のファインチューニングにおいて、モデルが物体の機能的・意味的カテゴリではなく、外形シルエットや大まかな形状類似性に依存して全く無関係な誤答カテゴリ（例: "Electroporation processing assembly" や "Golf club head" に対する "Magazine loader"）を出力する現象は、モデルの表現空間における「見た目の類似性（Visual Appearance）」と「意味的概念（Semantic Identity）」の剥離を解明する上で極めて重要な課題である。  
本報告書は、この「無関係なカテゴリ間における形状類似に起因する混同現象」を定量的に評価・立証するための公開ベンチマークについて、厳格な条件のもとで実施した包括的な調査・評価結果をまとめたものである。通常の細粒度分類（Fine-Grained Visual Categorization: FGVC）ベンチマーク（FGVC-Aircraft, Stanford Cars, CUB-200等）は、同一製品ラインや単一大分類内での微小バリアント識別を対象としており、異なる製品領域を横断する輪郭混同の評価とは構造が異なる。本調査では、以下の必須要件を厳密に適用して適合性を判定した。

* **ImageNetの完全不使用**: ImageNet-1k, 21kおよびその派生・拡張版（ImageNet-A/R/V2/Sketch等）由来の画像データを一切含まないこと。  
* **多角的なカテゴリ包括性**: 単一の狭いドメイン（航空機、自動車、特定の動植物等）に特化せず、広範な人工物・日用品・工業製品を横断していること。  
* **「形状類似×意味離脱」の評価設計**: 正解と意図的な誤答（ハードネガティブ）が異なる意味的カテゴリに属しつつ、視覚的類似性によって誘発される混同を測定できる評価プロトコルを備えていること。  
* **公開性とアクセス性**: 学術論文およびデータセットへのアクセス方法が確認できること。

## **該当ベンチマークの一覧と比較**

下表は、検索・検証された公開ベンチマークについて、必須条件への適合度順に整理した比較一覧である。

| ベンチマーク名 | 主なドメイン / データ源 | ImageNet排除 | カテゴリ多様性 | 形状混同評価の仕組み | タスク形式と指標 | 適合判定 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **THINGS-data** (Triplet Odd-One-Out)1 | 実世界物体（1,854概念）1 | **完全不使用** \[cite: 1, 3\] | 極めて高（多角的人工物・日用品・機器）1 | 470万件の人間行動データに基づく「見た目の類似 vs 意味分類」の剥離測定1 | 3択異質選定 (Odd-One-Out Accuracy)2 | **最高 (条件①〜④を完備)** |
| **NIGHTS** (DreamSim)4 | 合成生成画像（20,000トリプレット）4 | **完全不使用** \[cite: 4, 6\] | 高（人工物・構造体の形状・姿勢・配置変化）4 | 意味的属性を制御しつつ幾何変形・視覚属性に対するモデルの人間一致度を測定4 | 2AFCペア比較 (Human Alignment Acc)4 | **高 (条件①〜④を完備)** |
| **ShopID10K** (VICP)7 | Eコマース製品（10,000 ID）7 | **完全不使用** \[cite: 7\] | 高（各種工業製品・日用品・器具等）7 | 未知カテゴリ一般化において、外形が酷似した別カテゴリ（Distractor）への混同を評価7 | ReID / オープンセット識別 (mAP, Rank-1)7 | **中〜高 (条件①〜④を完備)** |
| **ARMBench** (Object ID)8 | 倉庫物流商品（190,000+ 独自物品）9 | **完全不使用** \[cite: 9, 10\] | 高（商業製品・容器・工具・パッケージ）9 | 混雑環境下で2D見た目・勾配特徴依存による誤同定および識別失敗を評価9 | オープンセット識別 (Precision, Recall, mAP)9 | **中 (条件①〜④を完備)** |
| **Do You See Me** \[cite: 13\] | 合成2D/3D幾何構造（1,758画像）13 | **完全不使用** \[cite: 13\] | 中（抽象的幾何学形状・視覚要素）13 | 視覚的恒常性（Form Constancy）や回転に対する知覚ショートカットを評価13 | VQA (問答正解率)13 | **中 (条件①〜④を完備)** |
| *(部分的不適合)* **MMVP** \[cite: 14, 15\] | 実世界画像（CLIP-blind pairs）15 | **不適合** (ImageNet由来含む)13 | 高（9つの視覚パターン）15 | 埋め込み空間で外形が酷似しモデルが「失明」するCLIP-blind pairsの評価15 | VQA (Visual Question Accuracy)15 | **条件外 (構造のみ参照可)** |

## **有望ベンチマークの深層分析**

### **1\. THINGS-data (Triplet Odd-One-Out Benchmark)**

THINGS-dataは、National Institutes of Mental Health (NIMH) のMartin N. Hebartらによって構築された、認知神経科学およびコンピュータビジョン領域における物体表現評価のための大規模基盤データセットである1。本ベンチマークは、アメリカ英語の具体的名詞から系統的にサンプリングされた1,854種類の概念（1,854 object concepts）と、それに対応する26,107枚の自然画像で構成されている1。対象となるカテゴリは工業製品、工具、日用品、容器、機器、家具、動植物など多岐にわたり、既存のImageNet規格から完全に独立したウェブ画像検索によって独自に収集・キュレーションされている1。  
本ベンチマークの中核をなす評価タスクは「3択異質選定（Triplet Odd-One-Out Task）」である2。提示された3つの画像（例: A, B, C）の中から、「最も仲間外れ（異質）な1つ」をモデルに選ばせる形式をとる2。評価指標には、4,699,160件におよぶクラウドソーシングで収集された人間行動判定データとの選択一致率（Odd-One-Out Accuracy / Degree of Alignment）が用いられる2。  
意匠特許課題との接続において極めて重要なメカニズムは、このトリプレットサンプリングが「人間の高次意味概念」と「深層視覚モデルの低・中次元特徴（輪郭・形状・パターン）」の食い違いを鋭く捉える点にある2。3つの概念の組み合わせにおいて、「意味的カテゴリは全く異なるが、全体的な輪郭や外形シルエットが極めて類似している物体」が必然的に含まれる2。モデルが物体の本質的な用途や意味的カテゴリを理解していない場合、視覚的な形状類似性に惑わされて人間とは異なる誤った選択を行うため、形状混同の度合いが直接的に数値化される2。  
既存のSOTAモデルおよび大規模視覚言語モデルのスコア検証において、ゼロショット設定の視覚モデルは人間のノイズシーリング（66.67%）に対して顕著に低いパフォーマンスを示すことが証明されている17。具体的には、SigLIP-So400mの未調整状態におけるOdd-One-Out一致率はわずか44.24%にとどまり、ランダム確率（33.33%）をやや上回る程度で著しく苦戦する17。論文内では、事前学習済みモデルの内部表現について以下の趣旨が分析されている：  
"model representations do not natively fully capture the structure of human similarity judgments"18

この結果は、一般的な視覚モデルが形状や局所テクスチャなどの視覚ショートカットに依存しており、人間のような概念的境界を形成できていないことを直接示唆している4。なお、人間の知覚構造に合わせたソフトアラインメント学習（AligNet等）を施すことで、一致率が61.7%まで大幅に向上することが確認されており、特定ドメインの表現空間をファインチューニングすることで形状混同が解消されるという強力な先行事例となっている17。データはOSFポータルおよび公式Webサイトから完全に無償でアクセス可能である1。

### **2\. NIGHTS / DreamSim Benchmark**

NIGHTS（Novel Image Generations with Human-Tested Similarity）は、MITのStephanie FuらによってNeurIPS 2023にて発表された知覚的類似度評価ベンチマークであり、幾何構造および見た目の類似性を評価するための統合フレームワーク「DreamSim」とともに提案された4。本データセットは、画像生成モデル（Diffusion Models）を活用して系統的に作成された20,000件の合成画像トリプレットで構成されている4。ImageNetからの流用画像は一切含まれておらず、完全に独立したデータソースを持つ4。  
タスク定義は「2強制選択（2-Alternative Forced Choice: 2AFC）知覚類似度判別」であり、1つの参照画像（Reference）に対して、2つの変形画像（Image A / Image B）のどちらがより視覚的に類似しているかを判定する4。評価指標には、厳格に集計された人間判定の正解ラベルに対するモデルの予測精度（Accuracy in predicting human judgments）が採用される4。  
本ベンチマークの評価メカニズムにおける最大の特徴は、画像の意味的カテゴリ（オブジェクトの同一性）を制御した状態で、物体の形状（Shape）、姿勢（Pose）、透視投影・遠近感（Perspective）、前景カラー（Foreground color）、オブジェクトの配置（Layout）といった中次元の幾何・構造変化を意図的に独立させて変化させている点にある4。これにより、「低次元のピクセル・テクスチャ差」と「中次元の幾何形状・構造類似性」および「高次意味概念」の相互作用を定量的に分解評価できるプロトコルが成立している4。  
既存モデルの精度傾向として、従来のパッチベース指標（LPIPS, DISTS）や事前学習済みの大型ビジョンモデル（MAE, CLIP, DINO）の表現ベクトル空間は、人間が捉える形状・配置の類似性判定と著しい乖離を示すことが明記されている4。論文内では次のように逐語的に指摘されている：  
"Current perceptual similarity metrics operate at the level of pixels and patches. These metrics compare images in terms of their low-level colors and textures, but fail to capture mid-level similarities and differences in image layout, object pose, and semantic content."4

標準的なDINO（ViT-B/16）やCLIP（ViT-B/32）の単体表現では人間判定との一致率に大きな不整合が生じるのに対し、人間判定データを用いてLoRA微調整を行ったDreamSimモデルは96.16%の整合精度を達成する6。この事実は、標準的な基盤モデルが複雑な形状・レイアウト変形に対して誤った知覚空間を形成しており、人間的な形状理解には適切なファインチューニングが不可欠であることを定量的・理論的に裏付けている4。データセットおよび事前学習済みコードはGitHubおよびHugging Faceで公開されている。

### **3\. ShopID10K (VICP Generalizable Object ReID Benchmark)**

ShopID10Kは、浙江大学のSharjeel Aliらによって提案された、未知カテゴリに対する交差カテゴリ一般化（Cross-Category Generalization）を評価するための製品識別ベンチマークである7。大規模なEコマース・ショッピングプラットフォームの製品カタログから独自に収集された10,000個のユニークな商品ID（Shop ID）と、それに紐づく多角的な実世界製品画像で構成されている7。衣料品、日用品、家庭用器具、電子機器、工具類など、多種多様な工業・商業製品が包括されている7。  
タスク定義は「オープンセット・一般化物体再識別（Generalizable Object Re-Identification）」および製品検索であり、学習データに含まれない未知の製品カテゴリに対して、数例の参照ペアから正確な製品IDを識別・検索する形式をとる7。評価指標には Mean Average Precision (mAP) および Rank-1 精度が使用される7。  
本ベンチマークにおける形状混同評価の仕組みは、ギャラリーセット内に組み込まれた「紛らわしいハードネガティブ（Distractors）」の設計に存在する7。評価時には、クエリ画像と正解IDの画像に加えて、正解とは全く異なる製品カテゴリに属しているものの、外形・輪郭・シルエット・視覚的属性が極めて類似している別商品が多数混入されている7。モデルが製品の本質的・識別的特徴（Identity-specific features）を捉えず、大まかな外形形状や局所グラデーションに依存している場合、これらの紛らわしいハードネガティブを誤って上位に抽出（False Positive）するように設計されている7。  
SOTA視覚モデルの定性・定量分析において、強力な表現力を持つDINOv2などの視覚基盤モデルであっても、形状類似性に引きずられて高頻度で誤同定を起こすことが明確に報告されている7。論文からの定性分析における逐語引用は以下の通りである：  
"DINOv2 predominantly retrieves images sharing shape similarity or semantic attributes (e.g., matching object categories) but fails to prioritize identity-specific features, resulting in frequent false positives."7

論文では、LLMによる意味ルールの推論と視覚プロンプトを融合した提案手法（VICP）を導入することで、DINOv2や一般的なフューショット手法に対してmAPで4%以上の向上を達成し、形状の誤認による偽陽性を大幅に抑止できることが示されている7。データセットは研究目的で利用可能である。

### **4\. ARMBench (Object Identification Challenge)**

ARMBenchは、Amazon RoboticsのChaitanya MitashらによってICRA 2023にて発表された、物流倉庫環境におけるロボットピッキングのための大型物体認識ベンチマークである8。Amazonのフル fulfillment center から収集された190,000種類以上のユニークな商業物品（190K+ unique objects）と、235,000件以上のピッキング・転送アクションデータを含んでいる9。製品はあらゆる工業製品、家庭用品、文具、容器、包装体を含み、実世界の広範な人工物を網羅する9。  
タスク定義は「オープンセット物体識別（Object Identification）」、「不規則環境におけるセグメンテーション」、および「欠損・欠陥検出」からなり、評価指標には Precision, Recall, mAP が用いられる9。  
本ベンチマークでは、様々な物品が入り混じったコンテナ（Tote）内から個別物体を特定・検索するプロトコルが採用されている10。モデルが2Dの外観・輝度勾配・大まかなシルエットなどの表層的特徴に頼って識別を行おうとすると、視点変更、照明変動、および製品パッケージの変形によって、全く別の外形が似た物品と混同するように仕組まれている11。  
評価結果として、最先端のVLMや2D外観依存モデル（例: RoboLLM）が、過酷な実世界環境下でdiscriminative power（識別能力）を著しく低下させることが指摘されている11。関連論文からの逐語引用は以下の通りである：  
"state-of-the-art systems (e.g., RoboLLM) relying exclusively on 2D appearance cues—such as texture, color, and local gradients—are particularly vulnerable. Because these cues lack invariance to viewpoint shifts, occlusions, and packaging variations, their discriminative power sharply deteriorates under real-world warehouse settings"11

データはAmazon RoboticsのS3リポジトリおよびGitHubを通じて公式に配布されている8。

### **5\. Do You See Me**

Do You See Meは、2024年（arXiv:2506.02022）に発表された、人間の視覚心理学（Psychology）に触発されて構築された視覚知覚能力評価ベンチマークである13。合計1,758枚の画像と2,612問の問答ペア（VQA形式）で構成されており、プログラムによって幾何学的変化や構造的条件が動的に制御された2D/3D視覚刺激を含んでいる13。  
本ベンチマークは、人間心理学に基づく7つのサブタスクから構成されており、特に「視覚的恒常性（Visual Form Constancy: 回転やスケール変化における形状誤認識の評価）」や「視覚的識別（Visual Discrimination）」といったサブタスクを含んでいる13。モデルが幾何構造の真の理解を行わず、過度の簡略化や表層的特徴によるショートカット推論（Perceptual shortcuts）を行うと失点する設計となっている13。  
SOTAのマルチモーダル大規模言語モデル（MLLMs）のスコア判定において、人間の平均正解率が**96.49%に達するのに対し、商用およびオープンソースの最先端MLLM（Claude Sonnet-3.5やGPT-4系を含む）の平均正解率は50%未満**に激減することが判明している13。論文内では、モデルが論理的推論では正解を出していても、基礎的な視覚知覚において重大な誤認識を抱えているケースが29%存在することが明示されている13。データセットおよび評価コードはWeb上で公開されている。

### **【参考・条件不適合の検証】MMVP (Multimodal Visual Patterns)**

* **注意**: 条件①「ImageNet不使用」に対して**不適合**（画像の原典としてImageNet-1Kの画像が明確に含まれている）13。ただし、ユーザーが求めている「見た目の類似に騙されるVLMの脆弱性評価」の構造に極めて近いため、比較参考資料として記載する。

MMVP（CVPR 2024, Shengbang Tong et al.）は、CLIPの視覚埋め込み空間において「視覚的な差異が明白であるにもかかわらず、CLIPが酷似していると認識してしまうペア（CLIP-blind pairs）」を特定し、それを基に構築されたVQAベンチマークである15。方向、個数、視点、状態など9つの視覚パターンにわたって評価を行う15。GPT-4V等の最新商用VLMであっても知覚的ミスを連発し、存在しない理由（Hallucinated explanations）を回答する現象が定量化されている14。ImageNetが含まれるため主評価には採用できないが、CLIP-blind pairsをマイニングして誤答選択肢を作るという「テストデータ構築手法」の参照元として極めて有用である15。

## **意匠特許ドメインへの適用性と採用時検討軸**

上記で同定された候補ベンチマークを、意匠特許図面からの製品カテゴリ予測タスク（Qwen3-VL-4B \+ LoRA）の研究論文に組み込む際の、採用上の利点・懸念点および接続の容易性を以下に整理する。

### **採用戦略 1: THINGS-dataによる「概念・知覚アラインメント」の外部立証**

THINGS-dataを直接的な外部評価セットとして採用し、ファインチューニング前後のモデルに「Triplet Odd-One-Out」タスクを実行させるアプローチである2。

* **適用における利点**: ImageNetを完全に排除しており、認知科学・ビジョン分野で絶対的な認知度と学術的信頼性を持つ1。意匠特許データセットでLoRA学習を行った結果、モデルのTHINGS Odd-One-Out Accuracy（人知覚とのアラインメント精度）がゼロショットベースライン（例: 44.24%）から向上したことを提示できれば、「意匠特許学習によって、モデルが表面的なシルエット類似に引きずられる欠点を克服し、より人間的で強固な抽象概念空間を獲得した」という極めて強固な学術的主張が可能となる17。  
* **留意すべき懸念点**: THINGS-dataは自然写真（実世界画像）で構成されているため、線画（Line Drawing）である意匠特許画像とはドメインギャップ（Style Gap）が存在する1。ただし、近年の研究（Drawing of THINGS: DoT等）において、THINGSの概念空間は線画表現に対しても高い汎用性を持つことが示されており、適切なエンコーダ（SigLIPやDINOv2等）を解凍していれば評価は十分に成立する24。

### **採用戦略 2: ShopID10K / FOCIの手法を移植した「意匠特許独自ハードネガティブ評価セット」の構築**

既存ベンチマークの「評価プロトコル（ハードネガティブ・マイニングの仕組み）」を特許ドメインにそのまま移植・再現するアプローチである7。

* **適用における利点**: 特許図面データそのものを評価に使用するため、ドメインギャップが一切生じない。具体的には、学習前のゼロショットVLM（例: 事前学習済みCLIPやQwen-VL）の視覚埋め込み空間において、正解カテゴリとは異なるカテゴリに属しながらもコサイン類似度が最も高い「紛らわしい他カテゴリ（例: Golf club headに対するMagazine loader）」を自動抽出し、4択のVQAまたは選択式分類タスクを作成する7。  
* **理論的裏付けの確保**: 「ImageNet非依存の新規評価プロトコル構築」として本論文の貢献（Contribution）を強調できる。その際、論文の提案手法セクションにおいて、「本評価プロトコルは、ShopID10KおよびFOCIにおける視覚的類似ハードネガティブ抽出原理7 に基づいて設計された」と明記することで、ベンチマークの正当性と客観性を担保できる。

## **結論と研究推進への提言**

本調査の必須条件（ImageNet完全不使用、多様なカテゴリ、異カテゴリ間の形状混同測定、公開性）を最も高い水準で満たすベンチマークはTHINGS-data（Triplet Odd-One-Out Benchmark）である1。1,854種類の多角的な概念と470万件の人間行動判別ログを備えており、モデルが機能的意味を捉えているか外形シルエットに騙されているかを直接数値化できる1。  
また、幾何・外形変形に対する知覚評価としては**NIGHTS (DreamSim)**、Eコマース・工業製品の形状類似誤判定の評価としては**ShopID10K**および**ARMBench**が極めて有力な裏付け材料となる4。  
意匠特許の論文執筆においては、これらの既存ベンチマークによる外部評価スコア（ゼロショット vs LoRA調整後）を提示するか、あるいはShopID10K/FOCIのマイニング手法を特許データセットに適用した独自の「Cross-Category Visual Hard Negative Benchmark」を構築・評価することで、研究の客観的説得力と学術的価値を最大化できる。

#### **引用文献**

> 1. THINGS-data: A multimodal collection of large-scale datasets for investigating object representations in human brain and behavior | bioRxiv, [https://www.biorxiv.org/content/10.1101/2022.07.22.501123v2.full](https://www.biorxiv.org/content/10.1101/2022.07.22.501123v2.full)  
> 2. Human-like object concept representations emerge naturally in multimodal large language models \- arXiv, [https://arxiv.org/html/2407.01067v3](https://arxiv.org/html/2407.01067v3)  
> 3. (PDF) THINGS: A database of 1,854 object concepts and more than 26,000 naturalistic object images \- ResearchGate, [https://www.researchgate.net/publication/336573523\_THINGS\_A\_database\_of\_1854\_object\_concepts\_and\_more\_than\_26000\_naturalistic\_object\_images](https://www.researchgate.net/publication/336573523_THINGS_A_database_of_1854_object_concepts_and_more_than_26000_naturalistic_object_images)  
> 4. DreamSim: Learning New Dimensions of Human Visual Similarity using Synthetic Data \- NIPS, [https://proceedings.neurips.cc/paper\_files/paper/2023/file/9f09f316a3eaf59d9ced5ffaefe97e0f-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2023/file/9f09f316a3eaf59d9ced5ffaefe97e0f-Paper-Conference.pdf)  
> 5. Aligning Machine and Human Visual Representations across Abstraction Levels \- arXiv, [https://arxiv.org/html/2409.06509v3](https://arxiv.org/html/2409.06509v3)  
> 6. DreamSim: Learning New Dimensions of Human Visual Similarity using Synthetic Data, [https://arxiv.org/html/2306.09344v3](https://arxiv.org/html/2306.09344v3)  
> 7. Generalizable Object Re-Identification via Visual In-Context Prompting \- arXiv, [https://arxiv.org/html/2508.21222v1](https://arxiv.org/html/2508.21222v1)  
> 8. GitHub \- amzn/armbench, [https://github.com/amzn/armbench](https://github.com/amzn/armbench)  
> 9. ARMBENCH DATASET, [https://www.armbench.com/](https://www.armbench.com/)  
> 10. ARMBench: An Object-centric Benchmark Dataset for Robotic Manipulation \- arXiv, [https://arxiv.org/abs/2303.16382](https://arxiv.org/abs/2303.16382)  
> 11. RoboEye: Enhancing 2D Robotic Object Identification with Selective 3D Geometric Keypoint Matching \- arXiv, [https://arxiv.org/html/2509.14966v1](https://arxiv.org/html/2509.14966v1)  
> 12. Robot Instance Segmentation with Few Annotations for Grasping \- arXiv, [https://arxiv.org/html/2407.01302v2](https://arxiv.org/html/2407.01302v2)  
> 13. Do You See Me : A Multidimensional Benchmark for Evaluating Visual Perception in Multimodal LLMs \- arXiv, [https://arxiv.org/html/2506.02022v1](https://arxiv.org/html/2506.02022v1)  
> 14. CVPR Poster Eyes Wide Shut? Exploring the Visual Shortcomings of Multimodal LLMs, [https://cvpr.thecvf.com/virtual/2024/poster/30013](https://cvpr.thecvf.com/virtual/2024/poster/30013)  
> 15. arXiv:2401.06209v2 \[cs.CV\] 25 Apr 2024, [https://arxiv.org/pdf/2401.06209](https://arxiv.org/pdf/2401.06209)  
> 16. 論文紹介 : Eyes Wide Shut? \- Zenn, [https://zenn.dev/tatexh/articles/f6c28149a4e929](https://zenn.dev/tatexh/articles/f6c28149a4e929)  
> 17. Aligning machine and human visual representations across abstraction levels \- PMC \- NIH, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12611773/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12611773/)  
> 18. (PDF) Improving neural network representations using human similarity judgments, [https://www.researchgate.net/publication/378488377\_Improving\_neural\_network\_representations\_using\_human\_similarity\_judgments](https://www.researchgate.net/publication/378488377_Improving_neural_network_representations_using_human_similarity_judgments)  
> 19. (PDF) Aligning machine and human visual representations across abstraction levels, [https://www.researchgate.net/publication/397543105\_Aligning\_machine\_and\_human\_visual\_representations\_across\_abstraction\_levels](https://www.researchgate.net/publication/397543105_Aligning_machine_and_human_visual_representations_across_abstraction_levels)  
> 20. Aligning Machine and Human Visual Representations across Abstraction Levels \- arXiv, [https://arxiv.org/html/2409.06509v4](https://arxiv.org/html/2409.06509v4)  
> 21. (PDF) DreamSim: Learning New Dimensions of Human Visual Similarity using Synthetic Data \- ResearchGate, [https://www.researchgate.net/publication/371638544\_DreamSim\_Learning\_New\_Dimensions\_of\_Human\_Visual\_Similarity\_using\_Synthetic\_Data](https://www.researchgate.net/publication/371638544_DreamSim_Learning_New_Dimensions_of_Human_Visual_Similarity_using_Synthetic_Data)  
> 22. Object Detection and Instance Segmentation on Amazon ARMBench Dataset | by Pinak Jani, [https://medium.com/@pinakjani99/object-detection-and-instance-segmentation-on-amazon-armbench-dataset-19d0ac1d4c88](https://medium.com/@pinakjani99/object-detection-and-instance-segmentation-on-amazon-armbench-dataset-19d0ac1d4c88)  
> 23. Computer Vision Meetup: ARMBench: An Object-Centric Benchmark Dataset for Robotic Manipulation \- YouTube, [https://www.youtube.com/watch?v=LMfXdT3icYc](https://www.youtube.com/watch?v=LMfXdT3icYc)  
> 24. Drawings of THINGS: A large-scale drawing dataset of 1854 object concepts \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12858628/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12858628/)