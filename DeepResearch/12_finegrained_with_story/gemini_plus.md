# **大規模視覚言語モデルを用いた細粒度画像認識手法の網羅的調査および深層分析報告書**

細粒度画像認識（Fine-Grained Visual Recognition / Classification: 以下、FGVRまたはFGVC）は、鳥の種別、航空機のモデル、花の品種など、同一の広範な上位カテゴリ（メタカテゴリ）に属する視覚的に極めて類似した下位カテゴリを識別するタスクである。一般的な物体認識とは異なり、FGVRはクラス間の差異が極めて微小であり、かつ姿勢や照明、背景などに起因するクラス内の分散が非常に大きいという特有の困難を抱えている。  
近年、大規模視覚言語モデル（MLLM / LVLM）が視覚的推論や画像理解において目覚ましい成果を挙げている一方で、FGVRの推論プロセスにこれらのモデルを直接適用する試みは驚くほど少ない。本報告書は、2023年から2026年までの主要な国際会議および学術論文誌を対象に、推論にLLMまたはMLLMを用いるFGVR手法を網羅的に調査した結果をまとめたものである。厳密なスクリーニングの結果、事前調査で特定されていた6件に加え、新たに5件の適合手法が発掘された。本稿では、指定された分類木に沿った体系的な配置、各手法の技術的深層、および「画像の局所（クロップ）を明示的に入力として活用する手法」の有無に関する最重要の発見を詳述する。

## **1\. 提案手法の分類木への配置**

収集された全11件の手法を、事後学習の有無、対象カテゴリの閉集合・開集合（未知カテゴリへの汎化）、見本の使用有無、および全体と局所の表現の組み合わせ方という観点から分類木に配置した。新規に発掘された5件の手法には【新規】と付記している。  
B-1. 事後学習する（事前学習済みの MLLM・LVLM のパラメータを、細粒度認識のデータで更新する） B-1-a. 事後学習とテストのカテゴリが同じである必要がある（閉集合） └─ 全体のみ ├─ Finedefics (ICLR 2025\) └─ Visual-RFT (ICCV 2025\) 【新規】 B-1-b. 事後学習にないカテゴリがテストに出ても対応できる（未知カテゴリへの汎化。base-to-novel など） ├─ 全体のみ ├─ Fine-R1 (ICLR 2026\) ├─ Taxonomy-Aware Representation Alignment (TARA) (CVPR 2026\) 【新規】 └─ SpeciaRL (2026) 【新規】 └─ 全体と局所・配分がサンプルごと └─ 局所もサンプルごとに選ぶ └─ ToolFG (arXiv 2026\) 【新規】  
B-2. 事後学習しない B-2-a. テストと同じカテゴリの見本を少数使う └─ 全体のみ ├─ SARE (arXiv 2026\) ├─ RAR └─ Zero-Shot Fine-Grained Image Classification Using Large Vision-Language Models (EMNLP Findings 2025\) B-2-b. 見本を使わず、候補名と画像だけで推論する（ゼロショット） └─ 全体のみ ├─ CascadeVLM (EMNLP Findings 2024\) └─ FruitEnsemble (arXiv 2026\) 【新規】

## **2\. 最重要の報告：「全体と局所・配分がサンプルごと（局所もサンプルごとに選ぶ）」手法の発見**

本調査における最大の技術的成果であり、ユーザーが最優先課題として指定した「推論に LLM を用いる手法で、画像の局所（クロップ、領域、部位）も入力に使う手法」は存在した。分類木の「B-1-b」配下、「全体と局所・配分がサンプルごと（局所もサンプルごとに選ぶ）」に該当する画期的な手法である『ToolFG』が新たに発見された1。  
MLLMに高解像度の局所クロップを複数同時に提示する従来のアプローチ（除外対象となったV\*やFOCUSなどのVQA向け手法）は、視覚トークン数の爆発的な増加による計算コストの増大や、言語モデルの注意機構がノイズトークンに圧倒される現象を引き起こすという根本的な制約を抱えていた。ToolFGは、この問題を「MLLMを外部ツールを自律的に操作するエージェントとして扱う」という全く新しいパラダイムによって解決している1。  
具体的には、ToolFGはモンテカルロ木探索（MCTS）に誘導された知識蒸留を通じて、画像のどの部位に注目すべきかをMLLM自身に動的に推論させる。例えば、鳥の画像を分類する際、MLLMは単に全体画像を眺めるのではなく、推論の過程で自律的に bird\_color\_histogram("breast")（胸部の色分布を取得）や bird\_geometry("tail\_to\_bird")（鳥の全長に対する尾の比率を測定）といった外部ツールを関数呼び出しとして実行する1。ツールは要求された特定の局所領域（部位）を切り出し、計測結果や視覚的証拠（Visual Cues）をテキストまたは視覚表現としてMLLMの推論チェーン（Chain-of-Thought）に返却する1。  
このメカニズムは、入力画像の内容や候補となるカテゴリに応じて「どの局所情報が必要か」をサンプルごとに動的に決定する（局所もサンプルごとに選ぶ）ものであり、全体画像から得られる大局的な文脈と局所的な確証を明確な比率・順序で組み合わせる（配分がサンプルごと）設計となっている。また、ToolFGはCUB-200-2011やStanford CarsなどのデータセットにおいてBase-to-Novel（未知カテゴリへの汎化）設定で評価されており1、B-1-bの要件を完全に満たしている。

## **3\. 新規特定手法の詳細分析**

今回の調査で新たに発掘された5件の論文について、それぞれの技術的貢献、構造的特徴、およびFGVRにおける位置づけを詳述する。

### **3.1. ToolFG：ツール統合型の能動的局所探索**

ToolFGは、MLLMによる細粒度認識において、受動的な全体画像の観察から、能動的な局所証拠の収集へとパラダイムを転換させた。

| 項目 | 内容 |
| :---- | :---- |
| **論文名** | ToolFG: Towards Well-Grounded Fine-Grained Image Classification |
| **筆頭著者** | Yu Xue |
| **会場と年** | arXiv 2026 (arXiv:2606.02518) |
| **葉** | B-1-b・全体と局所・配分がサンプルごと（局所もサンプルごとに選ぶ） |
| **判定根拠（原文）** | "ToolFG enables MLLMs to autonomously and flexibly use external tools during the reasoning process... takes as input the name of a bird part (e.g., breast or wing) and returns the HSV and RGB color histograms"1. |
| **判定根拠（要約）** | ToolFGは、MLLMが推論中に外部ツールを自律的かつ柔軟に使用することを可能にする。例えば、鳥の部位（胸や翼など）の名前を入力として受け取り、HSVおよびRGBカラーヒストグラムを返すツールなどを活用する。 |
| **使用LLM/MLLM** | 未確認（独自の高度なMLLMから蒸留された小規模MLLMを使用と記述あり） |
| **評価データセット** | CUB-200-2011, FGVC-Aircraft, Stanford Cars, Oxford Pets-371 |
| **局所の使い方** | MCTSを用いた探索により、MLLMが画像内容や推論状態に応じて特定の部位（胸、翼、尾など）を指定してツールを呼び出す。ツールが切り出した局所の色や幾何学的特徴を、全体画像の推論を裏付ける証拠として推論チェーン内に動的に組み込む。 |

ToolFGの革新性は、人間の専門家が図鑑と計測器具を用いて未知の種を同定するプロセスを模倣している点にある。微細な特徴を識別するためには、画像を単に高解像度化するだけでは不十分であり、注目すべき部位を正確に切り出し、定量的に比較するプロセスが必要である。本手法は、モデルとツール群を相互に適応させる「モデル・ツール共進化メカニズム（model-tool co-evolution mechanism）」を導入しており、細粒度認識におけるMLLMの推論をより信頼性の高い（well-grounded）ものへと進化させている1。

### **3.2. Visual-RFT：強化学習による視覚的推論の最適化**

事後学習のパラダイムを、従来の教師あり微調整（SFT）から検証可能な報酬に基づく強化学習（RL）へと昇華させたのがVisual-RFTである。

| 項目 | 内容 |
| :---- | :---- |
| **論文名** | Visual-RFT: Visual Reinforcement Fine-Tuning |
| **筆頭著者** | Ziyu Liu |
| **会場と年** | ICCV 2025 |
| **葉** | B-1-a・全体のみ |
| **判定根拠（原文）** | "Visual-RFT enhances Large Vision-Language Models (LVLMs) through reinforcement learning with visual perception verifiable rewards... Experimental results on fine-grained image classification..."2. |
| **判定根拠（要約）** | Visual-RFTは、視覚的知覚の検証可能な報酬を用いた強化学習によってLVLMを強化する手法であり、細粒度画像分類などにおいて有効性を実証している。 |
| **使用LLM/MLLM** | Qwen2-VL-2/7B, Qwen2.5-VL4 |
| **評価データセット** | Flower102, Pets37, FGVC-Aircraft, Stanford Cars5 |
| **局所の使い方** | 局所クロップや部位の明示的な抽出は行わず、画像全体をモデルに入力する。 |

細粒度分類において、SFTは正解ラベルの暗記に陥りやすく、クラス間の微妙な差異を論理的に推論する能力を養うことが難しい。Visual-RFTは、OpenAIのo1やDeepSeek-R1に代表される推論モデルの強化学習手法を視覚領域に拡張し、GRPO（Group Relative Policy Optimization）を用いてモデルの「推論過程」を最適化する3。分類タスクにおいては、正解クラスを導き出せたかどうかの単純なバイナリ報酬を検証可能報酬として用いながらも、モデル自身が多様な推論軌跡（Trajectories）を探索することで、わずか100サンプル程度のfew-shot設定でもベースラインと比較して飛躍的な精度向上（+24.3%など）を達成している2。

### **3.3. FruitEnsemble：多段推論による計算効率と精度の調停**

大規模なラベル空間においてMLLMを全サンプルに適用する非効率性を解消する現実的なアプローチとして、FruitEnsembleが提案されている。

| 項目 | 内容 |
| :---- | :---- |
| **論文名** | FruitEnsemble: MLLM-Guided Arbitration for Heterogeneous ensemble in Fine-Grained Fruit Recognition |
| **筆頭著者** | Enhui Yu |
| **会場と年** | arXiv 2026 (arXiv:2605.20892) |
| **葉** | B-2-b・全体のみ |
| **判定根拠（原文）** | "when ensemble confidence falls below 0.6, a multimodal large language model (MLLM) is triggered to perform rigorous visual verification by integrating external botanical descriptions using Chain-of-Thought (CoT) reasoning."7. |
| **判定根拠（要約）** | 視覚モデルのアンサンブルの確信度が0.6を下回った場合のみ、MLLMが起動する。MLLMは外部の植物学的記述とCoT推論を統合して、候補クラスの厳密な視覚的検証を行う。 |
| **使用LLM/MLLM** | Qwen-VL-Plus7 |
| **評価データセット** | Fruit-306 (独自構築の細粒度果物データセット)7 |
| **局所の使い方** | 軽量視覚モデルの出力に基づく候補名と全体画像を入力とする。局所の切り出しは行わない。 |

この手法は、既に特定されているCascadeVLMに極めて近い設計思想を持つ。農業分野における果物の品種識別のような実世界の細粒度タスクでは、照明や熟度によるクラス内分散が非常に大きい。FruitEnsembleは、ResNet50などの軽量なCNN/ViTアンサンブルで大半の容易なサンプルを高速に処理し、確信度が閾値（0.6）を下回る境界例（Hard samples）に対してのみ、MLLMを「仲裁者（Arbitrator）」として起動する7。起動されたMLLMは事後学習を伴わず、候補カテゴリの植物学的な属性記述（テキスト）と入力画像を照合して最終判断を下す。これにより、精度と推論コストの最適なトレードオフを実現している7。

### **3.4. Taxonomy-Aware Representation Alignment (TARA)**

細粒度認識を「平坦なラベル分類」から「階層的構造の理解」へと引き上げる手法がTARAである。

| 項目 | 内容 |
| :---- | :---- |
| **論文名** | Taxonomy-Aware Representation Alignment for Hierarchical Visual Recognition with Large Multimodal Models |
| **筆頭著者** | Hulingxiao He |
| **会場と年** | CVPR 2026 |
| **葉** | B-1-b・全体のみ |
| **判定根拠（原文）** | "By aligning the intermediate representations of visual features with those of BFMs, LMMs are encouraged to extract discriminative visual cues well structured in the taxonomy tree."9. |
| **判定根拠（要約）** | LMMの視覚特徴の中間表現を、生物学基盤モデル（BFM）の表現とアラインさせることで、分類木内で構造化された識別的な視覚手がかりを抽出するように促す。 |
| **使用LLM/MLLM** | 未確認 |
| **評価データセット** | 未確認（生物学的な階層分類データセット） |
| **局所の使い方** | 局所の切り出しは行わない。 |

一般的なMLLMは、鳥の特定種を別の鳥類ではなく「航空機」と間違えるような、分類学的にあり得ない致命的なエラーを犯すことがある。TARAは、階層的対照学習によって生物学的な進化系統や関係性をエンコードした基盤モデル（Biology Foundation Models: BFMs）の潜在空間に、MLLMの中間表現を近づける（Representation Alignment）というアプローチをとる9。これにより、未知のカテゴリ（Base-to-novel）に対しても、階層的に一貫した推論（Hierarchical Consistency）を可能にし、極端な誤分類を抑制しながら細粒度認識の精度を向上させている。

### **3.5. SpeciaRL：オープンワールド環境での特異性の促進**

未知のカテゴリが存在する環境下でのMLLMの応答傾向を制御する強化学習アプローチである。

| 項目 | 内容 |
| :---- | :---- |
| **論文名** | A novel reinforcement learning framework called SpeciaRL is proposed to improve the specificity of large multimodal models in open-world fine-grained image classification... (正式タイトルは概要からの引用) |
| **筆頭著者** | 未確認 |
| **会場と年** | 2026年 (arXiv等)11 |
| **葉** | B-1-b・全体のみ |
| **判定根拠（原文）** | "SpeciaRL introduces a dynamic, verifier-based reward signal... promoting specificity... in open-world fine-grained image classification"11. |
| **判定根拠（要約）** | SpeciaRLは、オープンワールドの細粒度画像分類において、動的で検証器に基づく報酬信号を導入し、モデルの予測の特異性（より詳細なカテゴリを当てること）を促進する。 |
| **使用LLM/MLLM** | 未確認 |
| **評価データセット** | オープンワールド設定の細粒度ベンチマーク11 |
| **局所の使い方** | 局所の切り出しは行わない。 |

オープンワールド設定（B-1-b）において、MLLMは自信がない場合に「安全な回答（例：特定の鳥の種名ではなく、単に"鳥"と答える）」に逃げる傾向がある。SpeciaRLは強化学習における報酬関数を工夫し、動的な検証器（Verifier）を用いて、単に正解することだけでなく、より細粒度で具体的な（Specificityの高い）回答を行うプロセスに高い報酬を与える11。これにより、正確性と特異性の最適なトレードオフを実現している。

## **5\. 既存分類済み論文との技術的連関と再評価**

ユーザーによって既に特定されていた6件の論文についても、新たに発掘された論文群と照らし合わせることで、技術的進化の系譜がより鮮明になる。

* **Finedefics (ICLR 2025\)** および **Fine-R1 (ICLR 2026\)** は、事後学習パラダイムの進化を示している。Finedeficsがオブジェクトと属性のペアを用いた対照学習（B-1-a）に留まっているのに対し、Fine-R1はVisual-RFTと同様にChain-of-Thought（CoT）推論を活用したR1スタイルのトレーニングフレームワークを構築している12。これにより、未知カテゴリへの汎化（B-1-b）を実現しており、RLベースのアプローチがFGVRの主流になりつつあることを裏付けている。  
* **Zero-Shot Fine-Grained Image Classification Using Large Vision-Language Models (EMNLP Findings 2025\)** は、LLMの幻覚（Hallucination）を防ぐために、クラス名の直接生成を避け、反復的な多肢選択式質問応答（Iterative MCQA）フレームワークを採用している14。これはFruitEnsembleが外部記述とCoTを統合する手法と軌を一にしている。  
* **CascadeVLM (EMNLP Findings 2024\)** は、CLIPによる候補の絞り込みと、LVLMによる最終判断を組み合わせた多段推論の先駆である16。この思想はFruitEnsembleへと直接的に受け継がれており、大規模なクラス空間を持つFGVRにおいては、エントロピーや確信度に基づく閾値判定でLVLMの起動を制御するアプローチが、計算効率の観点から事実上の標準（デファクトスタンダード）となっている。

## **6\. 除外対象手法の体系的整理と概念的境界**

本調査では、FGVRの厳密な定義（単一の大きく写った物体の下位カテゴリ分類）を維持するため、数多くの有望な手法を除外した。これらの除外理由は、FGVRと一般的な視覚的質問応答（VQA）や物体検出との境界を明確にする上で重要である。

| 論文名・手法名 | 除外理由の分類 | 詳細な除外理由と背景 |
| :---- | :---- | :---- |
| **FOCUS** (Fine-grained visual Object Cropping Using cached token Similarity)18 | 除外1（複数物体・高解像度からの局所抽出） | MLLMのKVキャッシュを用いてVQAのための関連領域を探索・クロップする手法。評価がV\*BenchやHRBenchなどの高解像度VQAベンチマークであり、単一物体の下位カテゴリ分類を目的としていない。 |
| **Vision-RL2** (Region-Level Policy Optimization for Fine-grained MLLM Perception)21 | 除外1（複数物体・高解像度からの局所抽出） | 領域レベルの強化学習によりVQA用のクロップを最適化する。解像度とトークンコストのトレードオフを論じているが、主眼はV\*やZoomBenchなどの汎用高解像度タスクにある。 |
| **DeepAlign** (Mitigating Modality Conflict through Modality-Specific Alignment)24 | 除外2（FGVRを問題設定としていない汎用手法） | CVPR 2026。パッチレベルの類似度を用いて視覚とテキストのモダリティ競合を緩和する手法。微細な知覚に寄与するものの、FGVR固有の課題設定を持たない。 |
| **Visual-ARFT** (Visual Agentic Reinforcement Fine-Tuning)4 | 除外2（FGVRを問題設定としていない汎用手法） | Webブラウザ操作やコード記述を通じた汎用的なエージェント機能の強化を目的とする強化学習手法であり、細粒度認識タスクではない。 |
| **PSCL** (Part-level Semantic-guided Contrastive Learning)25 | 除外3（推論にLLMを使用しない） | ICLR 2026。LLMを中間粒度のカテゴリ概念の抽出（テキスト特徴量の準備段階）にのみ使用し、推論自体は対照学習で最適化された視覚特徴（CLIPベース等）の類似度計算で行う。 |
| **MP-FGVC** (Delving into Multimodal Prompting for Fine-Grained Visual Classification)27 | 除外3（推論にLLMを使用しない） | AAAI 2024。CLIPモデルに対するマルチモーダルプロンプト手法であり、推論にLLMの生成能力を用いていない。 |
| **FG-VPL** (Fine-grained visual prompt learning)28 | 除外3（推論にLLMを使用しない） | ACM MM 2023。同じくCLIP等のVLMに対するプロンプト学習に留まる。 |

## **7\. 評価基盤としてのベンチマーク提案手法**

手法自体の提案ではないものの、MLLMの細粒度認識能力を正確に測定するために不可欠なデータセットや評価プロトコルを提案している論文群を以下に示す。これらは、現在のMLLMがいかにFGVRを苦手としているかを浮き彫りにしている。

| ベンチマーク名 | 提案の意義と特徴 |
| :---- | :---- |
| **FG-BMK** (Benchmarking Large Vision-Language Models on Fine-Grained Image Tasks)29 | 349万の質問と332万の画像からなる巨大な細粒度評価ベンチマーク。人間指向（多肢選択式QA等）と機械指向（検索・分類）の両面からMLLMを評価し、生成パラダイムよりも対照学習パラダイムの方が微細な特徴表現に優れていることを実証した。 |
| **FIKA-Bench** (From Fine-grained Recognition to Fine-Grained Knowledge Acquisition)32 | 単なる閉集合の視覚的識別ではなく、外部証拠（ウェブ上の知識等）を能動的に検索・検証して細粒度の知識を獲得できるか（Knowledge Acquisition）をエージェント向けに評価するベンチマーク。現状の最高性能システムでも正答率が30%未満に留まる難易度を示す。 |
| **FOCI** (Fine-grained Object ClassIfication)35 | 既存の巨大なLVLMが、ゼロショットのCLIPエンコーダ単体にさえFGVRタスクで劣るという衝撃的な事実を明らかにした評価研究。視覚モジュールとテキストモジュールの間で、微細な詳細に関するアライメントが致命的に不足していることを指摘している。 |

## **8\. 総括と将来展望：なぜ推論にMLLMを用いるFGVR手法は少ないのか**

本調査の根本的な目的である「推論にMLLMを用いるFGVR手法がこれほどまでに少ないのか」という疑問に対し、調査結果から明確な技術的メカニズムが浮かび上がった。  
最大の障壁は、「解像度と視覚トークン数のジレンマ」である。鳥のくちばしの僅かな曲がり具合や航空機のエンジンファンの形状など、FGVRには高解像度の視覚的特徴が不可欠である。しかし、全体画像を単純に高解像度化してMLLMに入力すると、視覚トークン数が数千から数万に膨れ上がり、計算コストが非現実的になるだけでなく、言語モデルの注意機構がノイズトークンに圧倒される（Lost-in-the-middle現象）という致命的な問題が生じる。V\*やFOCUSといった汎用VQA手法が採用する「単純にクロップを追加プロンプトとして投げる」アプローチは、大局的な相対関係（例：頭と胴体のプロポーション）と局所的な微細特徴の同時並行的な推論を必要とするFGVRにおいては、むしろ精度低下を招く。  
このジレンマに対する現在の最前線の解答が、今回発見された**ToolFG**である。ToolFGは、MLLMを単なるエンドツーエンドの分類器としてではなく、独自の仮説に基づいて能動的に外部計測ツールを操作する「エージェント」として再定義した。これにより、必要な局所情報のみを抽出・言語化して推論に取り込むことが可能となり、FGVRにおけるMLLM活用の巨大なブレイクスルーとなる可能性を秘めている。  
さらに、**事後学習の強化学習（RL）へのパラダイムシフト**が見逃せない。Visual-RFT、Fine-R1、SpeciaRLが示すように、FGVRの学習は単なるラベルの模倣（SFT）から、CoTを用いた「推論軌跡の最適化」へと急速に移行している。細粒度認識は「属性の抽出→部位ごとの比較→候補の絞り込み」という複雑な論理的推論を内包しており、検証可能報酬（Verifiable Rewards）を用いた強化学習は、極めて少数のデータでこの推論能力を獲得する上で劇的な効果をもたらしている。  
結論として、推論にLLMを用いる細粒度認識の手法が現在6〜11本程度しか存在しないという事実は、研究の停滞ではなく、**「単純なLLMへの画像入力ではFGVRは解けない」という技術的限界にコミュニティが直面し、それをエージェント化（ToolFG等）や強化学習（Visual-RFT等）という全く新しいパラダイムで乗り越えようとしている黎明期**であることを強く示唆している。

#### **引用文献**

> 1. ToolFG: Towards Well-Grounded Fine-Grained Image Classification, [https://arxiv.org/pdf/2606.02518](https://arxiv.org/pdf/2606.02518)  
> 2. Visual-RFT: Visual Reinforcement Fine-Tuning \- Hugging Face, [https://huggingface.co/papers/2503.01785](https://huggingface.co/papers/2503.01785)  
> 3. Visual-RFT: Visual Reinforcement Fine-Tuning \- arXiv, [https://arxiv.org/html/2503.01785v1](https://arxiv.org/html/2503.01785v1)  
> 4. Official repository of 'Visual-RFT: Visual Reinforcement Fine-Tuning, [https://github.com/Liuziyu77/Visual-RFT](https://github.com/Liuziyu77/Visual-RFT)  
> 5. Visual-RFT: Visual Reinforcement Fine-Tuning \- alphaXiv, [https://www.alphaxiv.org/abs/2503.01785](https://www.alphaxiv.org/abs/2503.01785)  
> 6. Visual Reinforcement Fine-Tuning A. Model and Data Sources, [https://www.openaccess.thecvf.com/content/ICCV2025/supplemental/Liu\_Visual-RFT\_Visual\_Reinforcement\_ICCV\_2025\_supplemental.pdf](https://www.openaccess.thecvf.com/content/ICCV2025/supplemental/Liu_Visual-RFT_Visual_Reinforcement_ICCV_2025_supplemental.pdf)  
> 7. FruitEnsemble: MLLM-Guided Arbitration for Heterogeneous ... \- arXiv, [https://arxiv.org/html/2605.20892v1](https://arxiv.org/html/2605.20892v1)  
> 8. FruitEnsemble: MLLM-Guided Arbitration for Heterogeneous ... \- arXiv, [https://arxiv.org/abs/2605.20892](https://arxiv.org/abs/2605.20892)  
> 9. Taxonomy-Aware Representation Alignment for Hierarchical Visual, [https://openaccess.thecvf.com/content/CVPR2026/papers/He\_Taxonomy-Aware\_Representation\_Alignment\_for\_Hierarchical\_Visual\_Recognition\_with\_Large\_Multimodal\_CVPR\_2026\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026/papers/He_Taxonomy-Aware_Representation_Alignment_for_Hierarchical_Visual_Recognition_with_Large_Multimodal_CVPR_2026_paper.pdf)  
> 10. Taxonomy-Aware Representation Alignment for Hierarchical Visual, [https://arxiv.org/abs/2603.00431](https://arxiv.org/abs/2603.00431)  
> 11. Specificity-aware reinforcement learning for fine-grained open-world, [https://huggingface.co/papers/2603.03197](https://huggingface.co/papers/2603.03197)  
> 12. Peking University Unveils Open-Source Fine-Grained Visual ... \- 36氪, [https://eu.36kr.com/en/p/3678574192993156](https://eu.36kr.com/en/p/3678574192993156)  
> 13. Make Multi-modal LLMs Excel in Fine-Grained Visual Recognition, [https://arxiv.org/abs/2602.07605](https://arxiv.org/abs/2602.07605)  
> 14. Zero-Shot Fine-Grained Image Classification Using Large Vision, [https://www.researchgate.net/publication/396249269\_Zero-Shot\_Fine-Grained\_Image\_Classification\_Using\_Large\_Vision-Language\_Models](https://www.researchgate.net/publication/396249269_Zero-Shot_Fine-Grained_Image_Classification_Using_Large_Vision-Language_Models)  
> 15. Zero-Shot Fine-Grained Image Classification Using Large Vision, [https://aclanthology.org/2025.findings-emnlp.1280.pdf](https://aclanthology.org/2025.findings-emnlp.1280.pdf)  
> 16. Enhancing Fine-Grained Image Classifications via Cascaded Vision, [https://aclanthology.org/2024.findings-emnlp.102.pdf](https://aclanthology.org/2024.findings-emnlp.102.pdf)  
> 17. Enhancing Fine-Grained Image Classifications via Cascaded Vision, [https://arxiv.org/html/2405.11301v1](https://arxiv.org/html/2405.11301v1)  
> 18. FOCUS: Internal MLLM Representations for Efficient Fine-Grained, [https://focus-mllm-vqa.github.io/](https://focus-mllm-vqa.github.io/)  
> 19. FOCUS: Internal MLLM Representations for Efficient Fine-Grained, [https://arxiv.org/html/2506.21710v2](https://arxiv.org/html/2506.21710v2)  
> 20. FOCUS: Internal MLLM Representations for Efficient Fine-Grained, [https://openreview.net/forum?id=8I1XNt70lj](https://openreview.net/forum?id=8I1XNt70lj)  
> 21. Region-Level Policy Optimization for Fine-grained MLLM Perception, [https://huggingface.co/papers/2609.19745](https://huggingface.co/papers/2609.19745)  
> 22. (PDF) Region-Level Policy Optimization for Fine-grained MLLM, [https://www.researchgate.net/publication/414443568\_Region-Level\_Policy\_Optimization\_for\_Fine-grained\_MLLM\_Perception](https://www.researchgate.net/publication/414443568_Region-Level_Policy_Optimization_for_Fine-grained_MLLM_Perception)  
> 23. Region-Level Policy Optimization for Fine-grained MLLM Perception, [https://arxiv.org/abs/2609.19745](https://arxiv.org/abs/2609.19745)  
> 24. DeepAlign: Mitigating Modality Conflict through Modality-Specific, [https://openaccess.thecvf.com/content/CVPR2026/papers/Li\_DeepAlign\_Mitigating\_Modality\_Conflict\_through\_Modality-Specific\_Alignment\_CVPR\_2026\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026/papers/Li_DeepAlign_Mitigating_Modality_Conflict_through_Modality-Specific_Alignment_CVPR_2026_paper.pdf)  
> 25. PART-LEVEL SEMANTIC-GUIDED CONTRASTIVE LEARNING FOR, [https://proceedings.iclr.cc/paper\_files/paper/2026/file/660cf2a1eabe448920a3ab6754555adb-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/660cf2a1eabe448920a3ab6754555adb-Paper-Conference.pdf)  
> 26. Part-level Semantic-guided Contrastive Learning for Fine-grained, [https://openreview.net/forum?id=Bzmb5LeCKx](https://openreview.net/forum?id=Bzmb5LeCKx)  
> 27. Delving into Multimodal Prompting for Fine-Grained Visual, [https://ojs.aaai.org/index.php/AAAI/article/view/28034](https://ojs.aaai.org/index.php/AAAI/article/view/28034)  
> 28. Fine-Grained Visual Prompt Learning of Vision-Language Models, [https://hexiangteng.github.io/papers/ACM%20MM%202023%20FGVPL.pdf](https://hexiangteng.github.io/papers/ACM%20MM%202023%20FGVPL.pdf)  
> 29. Benchmarking Large Vision-Language Models on Fine-Grained, [https://arxiv.org/html/2504.14988v1](https://arxiv.org/html/2504.14988v1)  
> 30. (PDF) Benchmarking Large Vision-Language Models on Fine, [https://www.researchgate.net/publication/390990908\_Benchmarking\_Large\_Vision-Language\_Models\_on\_Fine-Grained\_Image\_Tasks\_A\_Comprehensive\_Evaluation](https://www.researchgate.net/publication/390990908_Benchmarking_Large_Vision-Language_Models_on_Fine-Grained_Image_Tasks_A_Comprehensive_Evaluation)  
> 31. Benchmarking Large Vision-Language Models on Fine-Grained, [https://openreview.net/forum?id=cVc74MLspe](https://openreview.net/forum?id=cVc74MLspe)  
> 32. FIKA-Bench: From Fine-grained Recognition to Fine-Grained ... \- arXiv, [https://arxiv.org/html/2605.13193v1](https://arxiv.org/html/2605.13193v1)  
> 33. \[2605.13193\] FIKA-Bench: From Fine-grained Recognition to ... \- arXiv, [https://arxiv.org/abs/2605.13193](https://arxiv.org/abs/2605.13193)  
> 34. oking0197/FIKA-Bench · Datasets at Hugging Face, [https://huggingface.co/datasets/oking0197/FIKA-Bench](https://huggingface.co/datasets/oking0197/FIKA-Bench)  
> 35. African or European Swallow? Benchmarking Large Vision, [https://aclanthology.org/2024.emnlp-main.154.pdf](https://aclanthology.org/2024.emnlp-main.154.pdf)