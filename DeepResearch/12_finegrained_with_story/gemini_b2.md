# **細粒度画像認識における完全生成型・語彙非依存MLLM推論の網羅的調査と深層分析**

細粒度画像認識（Fine-Grained Visual Recognition / Classification: FGVR / FGVC）のパラダイムは、従来の識別型モデル（CLIP等）による特徴空間の距離学習から、大規模マルチモーダルモデル（MLLM / LVLM）を用いた自己回帰的な言語生成へと移行しつつある。しかし、MLLMを推論時に動的に稼働させ（条件1）、かつ「所与の有限な集合（カテゴリ一覧や多肢選択）」に一切依存せず、オープンワールドな環境下で完全な自由記述により下位カテゴリ名を解答させる（条件2）という厳格なアプローチは、極めて野心的な試みである。  
本報告書は、2023年から2026年に発表された主要な国際会議およびプレプリントを網羅的に調査し、指定された2つの条件を完全に満たす手法の特定、ならびに境界線上にある手法の厳密な分類を行った結果を取りまとめたものである。事前調査で特定された3件（Fine-R1、DiVE-k、SpeciaRL）に加えて、本調査で新たに条件を満たすと判定された手法は「わずか1件」のみであった。この「極端な少なさ」自体が、現在のMLLMアーキテクチャが抱える生成の不確実性と、細粒度認識が要求する決定論的精度の間の構造的な衝突（Granularity Fallback現象やExact Match評価の限界）を浮き彫りにしている。  
以下に、条件を満たす手法の詳細分析、条件を満たさない（B-1）手法の構造的要因、対象範囲外（除外1〜3）の分類、およびベンチマーク論文に基づく学術的洞察を詳述する。

## **1\. 条件を完全に満たす手法の一覧**

事前提示された3件（Fine-R11、DiVE-k2、SpeciaRL3）を除き、今回の網羅的調査において条件1および条件2を完全に満たすと判定された新規手法は以下の1件のみである。

* **Enhancing Cognition and Explainability of Multimodal Foundation Models with Self-Synthesized Data**  
  \[cite: 4, 5\]

本手法は、事前のラベル集合や候補リストに依存せず、画像固有の「概念のボトルネック」を抽出し、それを用いてMLLMに説明付きの細粒度カテゴリ名を自由記述で生成させる枠組みを提案している。

## **2\. 詳細分析表（条件達成手法）**

以下の表は、新たに特定された手法のアーキテクチャ、推論プロセス、および評価の仕組みを解剖したものである。

| 項目 | 詳細内容 |
| :---- | :---- |
| **論文名（正式タイトル）** | Enhancing Cognition and Explainability of Multimodal Foundation Models with Self-Synthesized Data4 |
| **筆頭著者** | Yucheng Shi6 |
| **会場と年** | ICLR 20254 |
| **arXiv番号** | 2502.140444 |
| **条件2の判定と根拠** | **【判定：満たす】** 推論時に有限な選択肢や候補リストを与えず、自由記述による生成を行っている。 **【推論プロンプトと手順の原文引用】** 推論時の定式化について： Let fθ denote the LMM model, X be the input image, and q be the query prompt. The model's answer is denoted as y \= fθ(X, q), where y is expected to correctly predict the label and explain its prediction by using the visual features observed in the image. \[cite: 5\] 実際の評価時のプロンプト構造について： These answers are obtained by prompting the model with questions like “What is the \[item\] in this image? Please provide your reasoning.” The “item” here is set to be an coarse-level label, like bird, airplane. \[cite: 5\] **【日本語の要約と根拠】** 入力画像 X とクエリプロンプト q のみから、直接ラベルと視覚的根拠を含むテキスト y を生成している。プロンプト内に bird や airplane といった上位カテゴリ名が一語（coarse-level label）含まれるが、推論プロセス自体は多肢選択やカテゴリ一覧の絞り込みを一切必要としない完全なオープンエンドの生成構造である。これは、ユーザー定義の「プロンプトに上位カテゴリ名が一語入っているだけで、それを外しても手法が成り立つものは満たす」という判定ルールに完全に合致する。 |
| **事後学習の有無** | **【あり】** ベースモデル（LLaVA-1.5-7B等）に対し、自己合成した説明付きデータを用いたLoRAによる教師あり微調整（SFT）を実施する。また、報酬モデルを用いないリジェクションサンプリング（棄却サンプリング）を利用し、説明の品質と分類精度を反復的に向上させている6。 |
| **画像の扱い** | **【全体のみ】** 推論時および学習時において、クロップや局所領域の明示的な抽出は行わず、画像全体（X）を入力として扱う定式化となっている5。 |
| **評価データセットと評価方法** | **【データセット】** CUB-200-2011（鳥類）、HAM10000（皮膚病変）など8。 **【評価方法】** 自由記述による評価のため、生成されたテキスト Y と、専門家が定義した概念セット Z、および画像 X との間の「3者間相互情報量（Three-way Mutual Information）」の最大化という情報理論に基づく指標を用いて説明の品質を採点・抽出している。その上で、細粒度ラベルの予測精度を測定している5。 |

## **3\. 条件2を満たさないと判定した論文の一覧（B-1）**

FGVRを対象とし、推論時にMLLMを使用しているものの、手法の核となる部分で「所与の有限な集合」や「分類階層の直接入力」を前提としているため、条件2を満たさない（B-1）と判定された主要な論文群を以下に示す。ユーザーから確認依頼があった候補論文も含まれる。

* **Can Textual Reasoning Improve the Performance of MLLMs on Fine-grained Visual Classification? (Visual-RFT / CLS-RL)**  
  \[cite: 10, 11\]  
  * **判定理由:** 推論時に候補となるクラス名のリストをプロンプトとして明示的に与える多肢選択（Closed-form）形式を大前提としており、自由記述生成ではない。  
  * **根拠:** 原文にて In this paper, we mainly focus on closed-form classification for MLLMs, where a subset of class names is provided for selection. と明記されている11。本研究はThinking-RFTとNo-Thinking-RFTの比較において、少数ショット分類でもリスト提供に依存している。  
* **Taxonomy-Aware Representation Alignment for Hierarchical Visual Recognition with Large Multimodal Models (TARA)**  
  \[cite: 12\]  
  * **判定理由:** 分類階層（taxonomy）をマルチスケールで出力させる優れた枠組みであるが、推論時のプロンプトにおいて具体的な選択肢のリストを提示している。  
  * **根拠:** 推論プロンプトが Please choose one from list \[similar class, ground...\] と定義されており、有限集合の絞り込みタスクとなっている12。  
* **ToolFG: Towards Well-Grounded Fine-Grained Image Classification**  
  \[cite: 13, 14\]  
  * **判定理由:** 推論時に外部ツールを呼び出して視覚的証拠を収集する枠組みだが、探索空間が事前に定義されたツール群とモンテカルロ木探索（MCTS）の木構造候補に依存している。  
  * **根拠:** MCTSの展開において expand the tree by adding a small set of candidate next tool invocations. とあり、純粋な自由記述生成ではなく、候補からの絞り込みを核としている13。  
* **AutoSEP: Democratizing Fine-Grained Visual Recognition with Large Vision-Language Models**  
  \[cite: 15, 16\]  
  * **判定理由:** ゼロショット予測を改善するために、インスタンスレベルの記述を外部から検索（Retrieval）する仕組みを採用しており、検索用の記憶（データベース）の存在を前提としている。  
  * **根拠:** 手法の核が based on instance-level description retrieval と明記されており、外部記憶への依存がある16。  
* **Uncertainty-Aware Listwise Reinforcement Fine-Tuning for Fine-Grained Visual Classification**  
  \[cite: 17\]  
  * **判定理由:** タイトルにある通り、「Listwise（リスト単位の）」という強化学習の定式化を用いており、複数の候補リスト（選択肢）の相対的なランキングや評価を前提とするClosed-worldな学習・推論構造に依存していると判断される。  
* **その他の事前提示済みB-1手法群 (Finedefics, SARE, RAR, UniFGVC, VR-RAG / Neural Catalog, Zero-Shot FG Classification Using LVLMs, FruitEnsemble, CascadeVLM, nlg2choice)**  
  * **判定理由:** これらはすべて、推論時にCLIP等の視覚・言語埋め込みを用いた全カテゴリリストとの類似度計算による絞り込みを行うか、プロンプトに有限の多肢選択肢を埋め込んでロジットを制約する手法であり、条件2の「所与の有限な集合に依存しない」という基準に明白に抵触する。

## **4\. 対象範囲外（除外1〜3）となる手法の一覧**

問題設定や推論アーキテクチャの根本的な違いにより、本調査のスコープから除外された主要な論文を分類する。

### **除外1：局所領域の探索・クロップ・ズームを主目的とする手法**

細粒度な対象を識別するというよりは、画像内の微小な物体を探索する、あるいは高解像度画像から意図的に領域を切り出してVQAやGroundingを行う設定であり、画像に物体が1つ大きく写っている一般的なFGVR設定から外れるもの。

* **DeepPerception: Advancing R1-like Cognitive Visual Perception in MLLMs for Knowledge-Intensive Visual Grounding**  
  \[cite: 18, 19\]  
  * **理由:** 独自構築した「KVG-Bench」を用いて評価を行っているが、タスクの定義が対象をバウンディングボックスで特定するVisual Grounding（predict a bounding box B）であり、カテゴリ名の自由記述による分類（FGVC）ではない18。  
* **Simple-VGC: Enhancing Visual Grounding in Multimodal Reasoning via Adaptive Tool Composition**  
  \[cite: 20\]  
  * **理由:** zoom\_in や focus\_area といった動的なツール操作を用いて局所領域を探索する手法であり、評価もHR-BenchやVStarBenchといったGroundingタスクで行われている20。  
* **Zooming without Zooming: Region-to-Image Distillation for Fine-Grained Multimodal Perception**  
  \[cite: 21\]  
  * **理由:** 強力な教師モデルがクロップ画像から作成したVQAデータを全体画像に蒸留し、推論時はツールなしで1回のフォワードパスで知覚させる手法。ただし、問題設定が汎用的なマルチモーダル認知やVQAの改善に置かれており、純粋なFGVCの枠組みではない21。

### **除外2：細粒度認識（FGVC）を主眼としない汎用手法**

汎用的な画像分類やデコーディング手法の提案であり、たまたま評価実験の一部としてCUBなどのFGVCデータセットの数値が報告されているに過ぎないもの。

* **Object Recognition as Next Token Prediction (CVPR 2024\)**22 （※ユーザー確認候補）  
  * **理由:** 自己回帰的なテキスト生成（Next Token Prediction）として物体認識を解き、非因果的マスクを用いたOne-shotサンプリングを提案する。しかし、主眼はImageNet等の汎用物体認識であり、論文内でも「汎用データを使用しているため、細粒度領域では性能が劣る（underperforms in this area due to the use of general, rather than fine-grained, training data）」と明記されており、FGVCを対象とした手法ではない22。  
* **Rationale-Enhanced Decoding for Multi-modal Chain-of-Thought (RED)**  
  \[cite: 24, 25\]  
  * **理由:** LVLM全般におけるChain-of-Thought（CoT）のデコーディングにおいて、中間推論（Rationale）に基づく確率を再重み付けする汎用手法であり、FGVCに特化した問題設定を持たない25。

### **除外3：推論時にLLMを使用しない手法**

準備段階（ラベル生成、擬似ラベル作成、概念抽出）でのみ重いMLLMを利用し、実際のテスト画像に対する推論はCLIP等の軽量な類似度計算で行うもの。

* **Efficient Vocabulary-Free Fine-Grained Visual Recognition in the Age of Multimodal LLMs (NeaR)**  
  \[cite: 26, 27\]  
  * **理由:** MLLMを用いて未ラベル画像に対する擬似ラベルを生成し、ノイズを考慮した上で下流のCLIPモデルを事後学習（Prompt Tuningなど）する。論文内で「推論時にMLLMを使用することはコストと時間がかかりすぎて非現実的である（test input is impractical because of high costs and prohibitive inference times）」と明記されており、テスト画像ごとにLLMを動かす条件1を満たさない27。  
* **Vocabulary-free Fine-grained Visual Recognition via Enriched Contextually Grounded Vision-Language Model (FiNDR)**  
  \[cite: 28\]  
  * **理由:** クラスラベルの「発見フェーズ（Discovery step）」でのみQwen等のLLMを動かす。しかし「推論時（Inference time）」には視覚とテキストの埋め込みを結合した線形分類器（Unified vision-language classifier）を用いて高速にラベルを割り当てるため、テスト画像ごとのLLM稼働という条件から外れる28。

## **5\. ベンチマーク・分析だけの論文**

FGVC領域におけるMLLMの挙動や限界を深く分析しているが、新しいアーキテクチャや推論アルゴリズムの提案を主目的としない論文を以下に挙げる。これらは自由記述型FGVRの評価方法や、モデルが失敗する原因の理解において極めて有用な示唆を与える。

* **Why are Visually-Grounded Language Models Bad at Image Classification? (NeurIPS 2024\)**29 （※ユーザー確認候補）  
  * **概要と意義:** MLLMが画像分類（オープンワールドおよびクラス名を与えるクローズドワールド設定の双方）においてCLIP等の従来手法に大きく劣る原因を実験的に分析した論文。評価として、候補クラス数 ![][image1] を100、20、5、2と減らした場合の推移を検証しているが、相対的なエラー率は依然として高いままであることを実証した30。MLLMの分類性能の低さは推論アルゴリズムの欠陥ではなく、事前学習および指示チューニングにおける「特定のクラスの出現頻度（class exposure）」との強い相関に起因することを証明した。これは、自由記述によるFGVCにおいてマイナーな下位カテゴリが出力されにくい現象の根本原因を説明するものである29。  
* **Seeing as Experts Do: A Knowledge-Augmented Agent for Open-Set Fine-Grained (FGExpertBench) (CVPR 2026\)**  
  \[cite: 31\]  
  * **概要と意義:** 細粒度認識における単なる認識精度を超え、推論の深さと未知タスクへの汎化性を測定するための新たなベンチマーク「FGExpertBench」の提案。モデルが専門家レベルの領域知識をいかに統合できるかを評価するための枠組みを提供する。

## **6\. 深層考察：指定された方向性に基づく解析と「手法の極端な少なさ」の意味**

ユーザーが指定した「特に探してほしい5つの方向性」に沿って調査結果を分析し、なぜ条件を満たす手法がこれほどまでに少ないのかについて、構造的および技術的な観点から深層的な洞察を提供する。

### **1\. 語彙なし（Vocabulary-free）・オープンワールドでの生成手法の枯渇**

今回の調査で、純粋な語彙非依存・推論時LLM生成の条件を満たすものは、既知の3件（Fine-R11、DiVE-k2、SpeciaRL3）と、今回特定した1件（Enhancing Cognition...5）の計4件にとどまった。この少なさは、生成モデルであるMLLMに決定論的な分類を要求することの難しさを反映している。MLLMは事前学習の分布に従うため、マイナーな下位カテゴリ（例："Acadian Flycatcher"）ではなく、安全な上位カテゴリ（例："Bird"）へと出力を抽象化してしまう「Granularity Fallback（粒度の後退）」を起こしやすい12。この問題を避けるため、ほとんどの研究者は有限なリストを用いたClosed-world設定（B-1手法群）に逃避しているのが現状である。

### **2\. 強化学習（RL）やCoTの事後学習による具体性の向上**

候補一覧なしで下位カテゴリを答えさせる試みとして、強化学習（RL）やChain-of-Thought（CoT）の導入は最新のトレンドである。既知の *Fine-R1* はCoTのSFTとTriplet Augmented Policy Optimization（TAPO）を用いており1、*SpeciaRL* はVerifierを用いた動的な報酬信号によるRLを適用している3。一方、今回特定された *Enhancing Cognition...* は、厳密なRL（PPOやGRPO）ではなく、情報理論（相互情報量の最大化）に基づくリジェクションサンプリングによるデータフィルタリングを用いてSFTを反復するアプローチをとっている5。 興味深いことに、*Visual-RFT (CLS-RL)* のようなGRPOを用いた最新手法であっても、オープンワールドの自由記述では評価や報酬の設計が困難なため、多肢選択形式（リスト提供）に依存している11。自由記述に対する報酬信号の設計（正解ラベルとの意味的同一性の判定など）が技術的な大きな壁となっている。

### **3\. 上位から下位への段階的絞り込み（Coarse-to-fine）**

この方向性については、*TARA*12 のような階層的推論を行う手法が存在するが、それらも各階層で選択肢リストを提供しているため、条件2から外れる。完全な自由記述において自己回帰的にCoarse-to-fineを展開する手法は、現時点で条件を満たす論文群の中には見出されなかった。これは、自己回帰生成の過程で一度誤った上位概念を生成すると、その後の下位カテゴリ生成が破綻する（Exposure Bias）という生成モデルの弱点に起因すると考えられる。

### **4\. 推論中の外部知識（Web検索等）の自律的参照**

外部知識を利用する手法として *ToolFG*13 や *AutoSEP*16 が存在するが、これらはあらかじめ定義されたツールツリーの探索や、用意された記述データベースとの照合を前提としており、純粋なオープンワールド・リスト非依存の要件を満たさない。固定のカテゴリ一覧を前提とせずに、動的に検索を行って名前を特定し自由記述するエンドツーエンドの手法は、推論コストと安定性の問題から未だ確立されていない。

### **5\. 画像の局所（クロップ等）を入力に用いる手法**

*DeepPerception*18 や *Simple-VGC*20、*Zooming without Zooming*21 など、局所領域を利用する優れた研究は多数存在する。しかし、これらの研究はすべて、バウンディングボックスの予測（Visual Grounding）や、微小なテキスト・物体のVQAを目的としており、「画面に大きく写った1つの物体の細粒度分類（FGVC）」という本調査の問題設定には該当しなかった。FGVCにおいて、全体画像からの自由記述生成と局所クロップの動的抽出を組み合わせた（条件を満たす）手法は確認されなかった。

### **結論と今後の展望**

「推論時にLLMを動かし、かつ有限な選択肢を与えずに自由記述で細粒度分類を行う」という設定は、MLLM研究において現在最も困難なフロンティアの一つである。従来の「完全一致（Exact String Match）」による評価指標が、同義語や表現の揺れを含む自由記述モデルに対して不当に低いスコアを与えるという構造的問題（Evaluation Bottleneck）があるため、多くの研究者がこのタスクを敬遠し、多肢選択やCLIPの埋め込み検索（除外3）へ流れている。  
しかし、*Fine-R1* や *SpeciaRL*、そして今回特定した *Enhancing Cognition...* に見られるように、意味的同一性を判定するVerifierの導入や、相互情報量に基づく自己合成データの活用といった革新的なアプローチにより、選択肢に依存しない「真のオープンワールドFGVR」への突破口が開かれつつある。見つかった論文の少なさは、この領域が未成熟であることを示すと同時に、次世代のマルチモーダル推論システム（Test-time computeやSystem 2思考）において極めて高い学術的価値と発展の余地を残していることを証明している。

#### **引用文献**

> 1. MAKE MULTI-MODAL LLMS EXCEL IN FINE-GRAINED VISUAL, [https://proceedings.iclr.cc/paper\_files/paper/2026/file/6f6dd92b03ff9be7468a6104611c9187-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/6f6dd92b03ff9be7468a6104611c9187-Paper-Conference.pdf)  
> 2. dive-k: differential visual reasoning for \- ICLR Proceedings, [https://proceedings.iclr.cc/paper\_files/paper/2026/file/ada418ae9b6677dcda32d9dca0f7441f-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/ada418ae9b6677dcda32d9dca0f7441f-Paper-Conference.pdf)  
> 3. Specificity-aware reinforcement learning for fine-grained open-world, [https://alessandroconti.me/papers/2603.03197.html](https://alessandroconti.me/papers/2603.03197.html)  
> 4. Enhancing Cognition and Explainability of Multimodal Foundation, [https://arxiv.org/abs/2502.14044](https://arxiv.org/abs/2502.14044)  
> 5. ENHANCING COGNITION AND EXPLAINABILITY OF MULTIMODAL, [https://proceedings.iclr.cc/paper\_files/paper/2025/file/d51cd79a85833b022841f7a2383b32d3-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2025/file/d51cd79a85833b022841f7a2383b32d3-Paper-Conference.pdf)  
> 6. Enhancing Cognition and Explainability of Multimodal Foundation, [https://huggingface.co/papers/2502.14044](https://huggingface.co/papers/2502.14044)  
> 7. Computer Vision and Pattern Recognition Feb 2025 \- arXiv, [https://www.arxiv.org/list/cs.CV/2025-02?skip=1000\&show=2000](https://www.arxiv.org/list/cs.CV/2025-02?skip=1000&show=2000)  
> 8. YuchengShi/LLaVA-v1.5-7B-HAM10000 \- Hugging Face, [https://huggingface.co/YuchengShi/LLaVA-v1.5-7B-HAM10000](https://huggingface.co/YuchengShi/LLaVA-v1.5-7B-HAM10000)  
> 9. YuchengShi/LLaVA-v1.5-7B-CUB-200 \- Hugging Face, [https://huggingface.co/YuchengShi/LLaVA-v1.5-7B-CUB-200](https://huggingface.co/YuchengShi/LLaVA-v1.5-7B-CUB-200)  
> 10. Can Textual Reasoning Improve the Performance of MLLMs on Fine, [https://huggingface.co/papers/2601.06993](https://huggingface.co/papers/2601.06993)  
> 11. A Study of Thinking in Rule-Based Visual Reinforcement Fine-Tuning, [https://arxiv.org/html/2503.16188v6](https://arxiv.org/html/2503.16188v6)  
> 12. Taxonomy-Aware Representation Alignment for Hierarchical Visual, [https://openaccess.thecvf.com/content/CVPR2026/papers/He\_Taxonomy-Aware\_Representation\_Alignment\_for\_Hierarchical\_Visual\_Recognition\_with\_Large\_Multimodal\_CVPR\_2026\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026/papers/He_Taxonomy-Aware_Representation_Alignment_for_Hierarchical_Visual_Recognition_with_Large_Multimodal_CVPR_2026_paper.pdf)  
> 13. ToolFG: Towards Well-Grounded Fine-Grained Image Classification, [https://arxiv.org/pdf/2606.02518](https://arxiv.org/pdf/2606.02518)  
> 14. Yu Xue \- CatalyzeX, [https://www.catalyzex.com/author/Yu%20Xue](https://www.catalyzex.com/author/Yu%20Xue)  
> 15. Unlabeled Data Improves Fine-Grained Image Zero-shot ... \- arXiv, [https://arxiv.org/pdf/2506.03195](https://arxiv.org/pdf/2506.03195)  
> 16. Unlabeled Data Improves Fine-Grained Image Zero-shot ... \- arXiv, [https://arxiv.org/html/2506.03195v2](https://arxiv.org/html/2506.03195v2)  
> 17. 北京大学多媒体信息处理研究室：主要论文, [https://mipl.pku.edu.cn/paper/](https://mipl.pku.edu.cn/paper/)  
> 18. DeepPerception, [https://deepperception-kvg.github.io/](https://deepperception-kvg.github.io/)  
> 19. DeepPerception: Advancing R1-like Cognitive Visual Perception in, [https://www.alphaxiv.org/abs/2503.12797v1](https://www.alphaxiv.org/abs/2503.12797v1)  
> 20. Simple-VGC: Enhancing Visual Grounding in Multimodal Reasoning, [https://aclanthology.org/2026.acl-long.223.pdf](https://aclanthology.org/2026.acl-long.223.pdf)  
> 21. Region-to-Image Distillation for Fine-Grained Multimodal Perception, [https://www.researchgate.net/publication/400742104\_Zooming\_without\_Zooming\_Region-to-Image\_Distillation\_for\_Fine-Grained\_Multimodal\_Perception](https://www.researchgate.net/publication/400742104_Zooming_without_Zooming_Region-to-Image_Distillation_for_Fine-Grained_Multimodal_Perception)  
> 22. Object Recognition as Next Token Prediction \- arXiv, [https://arxiv.org/html/2312.02142v4](https://arxiv.org/html/2312.02142v4)  
> 23. CVPR Poster Object Recognition as Next Token Prediction, [https://cvpr.thecvf.com/virtual/2024/poster/31732](https://cvpr.thecvf.com/virtual/2024/poster/31732)  
> 24. Rationale-Enhanced Decoding for Multi-modal Chain-of-Thought, [https://www.openaccess.thecvf.com/content/CVPR2026/papers/Yamaguchi\_Rationale-Enhanced\_Decoding\_for\_Multi-modal\_Chain-of-Thought\_CVPR\_2026\_paper.pdf](https://www.openaccess.thecvf.com/content/CVPR2026/papers/Yamaguchi_Rationale-Enhanced_Decoding_for_Multi-modal_Chain-of-Thought_CVPR_2026_paper.pdf)  
> 25. Rationale-Enhanced Decoding for Multi-modal Chain-of-Thought, [https://arxiv.org/pdf/2507.07685](https://arxiv.org/pdf/2507.07685)  
> 26. Efficient Vocabulary-Free Fine-Grained Visual Recognition in the, [https://arxiv.org/abs/2505.01064](https://arxiv.org/abs/2505.01064)  
> 27. Efficient Vocabulary-Free Fine-Grained Visual Recognition in the, [https://openreview.net/forum?id=FvA0UMw9X2](https://openreview.net/forum?id=FvA0UMw9X2)  
> 28. Vocabulary‑Free Fine‑Grained Recognition using Reasoning ... \- arXiv, [https://arxiv.org/html/2512.18897v1](https://arxiv.org/html/2512.18897v1)  
> 29. Why are Visually-Grounded Language Models Bad at Image ... \- NIPS, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/5c7024041be305c94d7311cfcc53d93e-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/5c7024041be305c94d7311cfcc53d93e-Paper-Conference.pdf)  
> 30. Why are Visually-Grounded Language Models Bad at Image, [https://plenarius.org/paper?uid=019f99b8-6edf-7693-872a-767b2d337798](https://plenarius.org/paper?uid=019f99b8-6edf-7693-872a-767b2d337798)  
> 31. A Knowledge-Augmented Agent for Open-Set Fine-Grained Visual, [https://openaccess.thecvf.com/content/CVPR2026/papers/Chen\_Seeing\_as\_Experts\_Do\_A\_Knowledge-Augmented\_Agent\_for\_Open-Set\_Fine-Grained\_CVPR\_2026\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026/papers/Chen_Seeing_as_Experts_Do_A_Knowledge-Augmented_Agent_for_Open-Set_Fine-Grained_CVPR_2026_paper.pdf)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAAA9klEQVR4Xu2TMQrCQBBFR7SwEEQFLRWsxE4Q7Gw9haA3EDyA59BC7AQbLyDGThC0sLW0s/QA+j+zwbhsTNJKHjzCzmQnu5tZkZT/JQ+LdjACznHCRA1e4Qu2zTj4gTJcwiMcwUIg5+QuWszFAF5g1k64yIkW4uqClODCPGNTES22seIenFixSIbwKbodnuHMjBPDLc7hGTbgVnSVlLlE9EQP/wYPJjYWLTb1X4oLt8iJa9GWIHV4gntYNbFY7ESL2Y3YNXH7p/wkrL9YnPGHnQjD7y8evgtuk/mWnQiSgR35HLQHm/J9TXiFeH2YX8G+6LyUlDi8AeV1LO48f9iuAAAAAElFTkSuQmCC>