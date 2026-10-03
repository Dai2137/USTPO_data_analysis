# **難関視覚タスクおよび工業製品・専門機器ドメインにおける細粒度画像分類・VLM評価ベンチマーク包括調査報告書**

意匠特許（Design Patents）の図面画像から製品名や詳細カテゴリを予測する視覚言語モデル（VLM）のドメイン特化ファインチューニングにおいて、モデルの優位性を客観的かつ定量的に実証するためには、学術的・産業的に広く認知された評価ベンチマークでの定量的検証が不可欠である。GPT-4VやGemini、CLIPなどの汎用VLMは、日常的な自然画像領域において極めて高いゼロショット認識性能を示す一方で、一般に流通していない専門的な機械要素、工業部品、高密度な商業製品（SKU）の細粒度識別においては著しい精度低下を招くことが報告されている1。  
本調査報告書では、意匠特許データセット（IMPACT等）3 での学習設定と親和性が高く、出力形式がシンプル（画像入力から単一ラベルまたは特定カテゴリ予測）であり、汎用VLMや既存SOTAモデルにとっても「難関（Challenging）」と定義されている公開ベンチマークを網羅的に抽出し、その技術的特性とドメイン適合性を分析する。

## **工業製品・専門機器・細粒度プロダクト画像分類ベンチマーク一覧**

本調査において選定した、難関とされる工業製品・専門機器および細粒度プロダクト分類の主要公開ベンチマークの全体像を以下の表にまとめる。タスク優先度として、最優先である「細粒度画像分類（FGVC）／カテゴリ予測」を軸とし、必要に応じてVQAおよび検索ベンチマークを補完的に配置している。

| ベンチマーク名 | 提供元 / 公開年 | タスク種別 & 主要評価指標 | データ規模 | 画像の性質 | SOTA / 汎用VLMの課題・難易度の理由 | ドメイン親和性 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **OmniMech** | arXiv / 20262 | 2D機械図面理解・幾何推論 (Top-1 Acc, Geometric Consistency) | 251,000ペア (2D機械投影図＋3D/CAD) | 2D機械製図・線画（寸法・公差注記付き） | 最新VLM（GPT-5クラス、Gemini 3.5、Qwen 3.5等）でも2D図面の幾何位相・細部注記の制約解釈に失敗2 | 極めて高い |
| **MCB (Mechanical Components Benchmark)** | ECCV / 20204 | 機械部品の細粒度分類・検索 (Top-1 Accuracy, Recall@K) | 58,696モデル (163K注記), 68クラス (ICS標準体系) | 3D CADレンダー画像 (2D多視点/投影) | 類別間類似度が極めて高く、重度のクラス不均衡が存在。専門的な機械工学体系の理解が必要4 | 極めて高い |
| **SIP-17 (Synthetic Industrial Parts)** | Kaggle / arXiv / 20246 | 工業部品の細粒度Sim-to-Real分類 (Top-1 Accuracy) | 合成66,000枚 (学習/検証), 実写566枚 (テスト), 17クラス | 合成CG (学習) ↔ 工業現場実写写真 (テスト) | ネジの有無やOリング装着等の微小構造変化、金属反射による極度の識別困難とドメインシフト6 | 高い |
| **MVIP** | IMPROVE / 20257 | マルチモーダル・多視点工業部品識別 (Top-1 / Top-5 Accuracy) | RGBD多視点画像＋物理特性・自然言語・上位クラス | 実際の工場環境で撮影された工業用機械部品 | 実用上Top-5精度100%近くが求められる中、外観が酷似した部品やスケール変動で従来手法が失速7 | 高い |
| **Products-10K** | CVPR / 20209 | 超大規模細粒度EC製品分類 (Top-1 Accuracy, mAP) | 141,931枚 (学習), 55,376枚 (テスト), 9,691クラス | 商業製品の実写写真・スタジオ撮影画像 | クラス数が1万近くと極めて多く、長尾（Long-tail）分布と極度のパッケージ類似性が存在9 | 中〜高い |
| **RP2K** | CVPRW / 202112 | 小売商品SKUの細粒度画像分類 (Top-1 Accuracy, mAP) | 350,000枚以上, 2,384クラス | 実際の店舗棚・商品実写写真 | 汎用CLIP（Zero-shot）の精度は41%にとどまり、微小テキストやロゴの識別が必須1 | 中〜高い |
| **iMaterialist (Furniture / Decor)** | FGVC / Kaggle14 | 家具・インテリアデザイン細粒度属性・カテゴリ分類 (Top-1 Acc, F1) | 128クラス (Furniture), 数十万枚規模 | EC実写写真・インテリア空間クロップ | デザイン意匠の微細な相違（脚の形状、材質、構造）の識別が必要で、事前学習モデルが誤認しやすい15 | 中〜高い |
| **HSS-IAD** | arXiv / 202417 | 同種異種工業部品の画像識別・異常判定 (Image-level / Pixel-level Acc) | 8,580枚, 7主カテゴリ (金属・鋳物・整流子等) | 実際の工場で生産された金属系工業部品 | 同一製品カテゴリ内での微小な構造変化や微細欠陥、切削痕ノイズの混在による判定難度17 | 中等度 |
| **UniAD** | MDPI / 202518 | 実生産ライン電子部品のマルチクラス認識 (Image Acc, AUROC) | 25,000枚以上, 7カテゴリ (基板・電子部品) | 実際の製造ラインで撮影された高解像度画像 | 複雑な基板環境下における微小電子部品の識別およびマルチクラスでの識別限界18 | 中等度 |

## **主要候補ベンチマークの技術的詳細・難易度構造解析**

### **OmniMech: 機械製図およびCADモデルの高度マルチモーダル理解**

OmniMechは、2D機械投影図面およびCADモデルのマルチモーダル理解と3D再構成を目的に構築された大容量ベンチマークである2。データセットは251,000件に及ぶ実際の機械設計図面と3Dモデルのペアで構成され、各インスタンスには平均15.62個の寸法・公差注記（GD\&T）を含む公式な2D機械製図（線画）が紐付けられている2。  
本ベンチマークが極めて難関とされる理由は、2Dの線画表現から立体幾何構造やトポロジー、寸法制約を視覚シンボリックに同時解釈する必要がある点に求められる2。実験結果によれば、GPT-5クラスの最新大型視覚言語モデルやGemini 3.5、Qwen 3.5等の強力なVLMであっても、2D図面内の微細な寸法注記のグラウンディングに失敗し、構造的に不整合な予測を頻発することが報告されている2。特許図面という線画ドメインでの構造予測において、汎用モデルの限界とドメイン特化モデルの優位性を直接比較・証明できる最も強力な基盤である2。

### **MCB (Mechanical Components Benchmark)**

MCBは、国際標準化機構の分類体系（ICS: International Classification for Standards）に準拠して構築された、大規模な機械要素部品の細粒度分類・検索ベンチマークである4。全体で163,000件の注記付き3Dモデル（主要分類セットとして58,696モデル、68クラス）を含み、ボルト、ナット、ベアリング、ギヤ、フランジ、ブラケット等の機械要素が包括されている4。  
MCBの難易度を跳ね上げている主因は、類別間類似度の圧倒的な高さとクラス不均衡の深刻さにある4。例えば、円筒形状を基礎とする「カラー」「フランジ」「ベアリング」などのクラスは全体幾何形状が酷似しており、微細な段差やタップ穴、角取り（面取り）の有無といった工学的特徴を捕縛できなければ正しく識別できない4。また、最大クラスが7,058サンプルを保持する一方で最小クラスは47サンプルしか存在しないという鋭い分布偏重があり（正規化エントロピー0.814）4、ImageNet等で事前学習された通常の畳み込みニューラルネットワーク（CNN）やVision Transformer（ViT）では少数クラスの誤認識が多発する4。

### **SIP-17 (Synthetic Industrial Parts Dataset)**

SIP-17は、実際の産業用アセンブリおよび品質検査ラインにおける部品分類を模した、Sim-to-Real（シミュレーションから実環境への適応）評価用細粒度画像分類ベンチマークである6。データセットはエアガン、電気コネクタ、フック、各種ギア、ピン、ホイール、Oリング付き構造など6つのユースケース・17カテゴリで構成されている6。学習・検証用として66,000枚の合成レンダリング画像（Syn\_R/Syn\_O）が提供され、テスト用として実際の工場環境で撮影された566枚のリアル写真が用意されている6。  
SIP-17の技術的難しさは、同種部品間における極微小な差分の識別に焦点を当てている点にある6。「ネジが存在するバックホイール（BwS）」と「ネジが存在しないバックホイール（BwoS）」、あるいは「Oリングが装着されたパーツ」と「非装着パーツ」など、画像の大部分が同一でありながら特定の数ピクセルの領域のみでラベルが変化する構造をとっている6。さらに、金属表面特有の光沢や光の反射（Albedo）がドメインギャップを増幅させるため、ドメイン適応を行わない標準モデルや汎用VLMのゼロショット識別性能は著しく低迷する6。

### **RP2K および Products-10K (細粒度プロダクトSKU識別)**

RP2KおよびProducts-10Kは、大規模な商業製品やリテールSKUを対象とした細粒度画像分類ベンチマークである10。RP2Kは実際の店舗棚や商品写真から収集された350,000枚以上・2,384カテゴリのデータを収録しており9、Products-10Kは9,691カテゴリ・141,931枚の学習画像を含む超大規模なロングテールデータセットである9。  
これらのベンチマークが直面する難題は、極めて高いクラス数と、それに伴うパッケージ・外観デザインの類似性である9。とりわけRP2Kにおいては、OpenAIの汎用CLIP（ViT-B/32）を用いたゼロショット分類精度が41%という低い水準にとどまることが定量的に示されている1。対象ドメインでのファインチューニングを実施したモデルが89%から93%の精度を達成するのに対し1、Webテキスト・画像ペアで事前学習された汎用VLMはパッケージ上の微細な製品名テキストやロゴの微小な差異を読み取れず、製品の正確な同定に失敗する1。

## **意匠特許ドメイン学習設定との親和性評価および上位5選の選定**

意匠特許データセット（IMPACT等）は、特許出願書類に記載された多視点線画図面と、それに対応する意匠のタイトル・クレーム・カテゴリ分類（Locarno分類やUPC分類）から構成されている3。Qwen3-VL-4B等のVLMをLoRAでチューニングし、「図面画像から製品名・カテゴリを予測する」タスクで学術的優位性を主張するためには、選択するベンチマークが以下の条件を満たしている必要がある：  
第一に、評価メディアとしての視覚表現（線画・構造プロファイル・無背景幾何）の相同性である。第二に、入力プロンプトに対する出力形式が単一の識別ラベルまたは構造的カテゴリ名であり、指示チューニング（Instruction Tuning）のパイプラインにそのまま組み込めることである。第三に、汎用VLM（GPT-4V/Gemini）やベースモデルのZero-shot精度が低く、ドメイン特化チューニングによる精度上昇幅を明瞭に提示できることである。  
これらを総合的に鑑み、採用価値が最も高い上位5件のベンチマークを選定し、それぞれの採用における利点、懸念点、およびIMPACTデータセットとの設定統合アライメントを詳述する。

### **第1位: OmniMech (2D Mechanical Drawing Benchmark)**

OmniMechは、2Dの機械投影図面（正投影図・断面図・寸法線付き線画）を入力とし、その幾何構造や構成部品を正確に認識・推論する能力を測定するベンチマークである2。

* **採用の利点**:  
  * IMPACTデータセットの最大の特色である「意匠特許の多視点線画図面」と視覚モダリティが完全に一致する2。一般的な自然画像で学習されたモデルが線画の空間幾何を解釈できない弱点を直撃できる。  
  * 最新の論文（2026年公開）であり、GPT-4V/5やGemini 3.5 Proなどの最高峰VLMであっても2D図面の幾何注記やトポロジー理解において著しい解釈失敗を起こすことが示されているため、評価結果の学術的インパクトが非常に大きい2。  
* **懸念点と課題**:  
  * 本来のOmniMechは可逆的なCADプログラム合成や3D一貫性評価を含む多機能な評価体系を持っている2。単一の画像分類タスクとして利用するためには、図面から部品カテゴリや構造属性を識別させる「Diagram-to-3D Reasoning」内の分類・属性予測サブタスクに形式を絞り込む必要がある2。  
* **IMPACTデータとの学習設定統合プロトコル**:  
  * IMPACTでの事前学習時におけるプロンプト形式（例: "\<image\>\\nPredict the primary category and structural type of this design patent figure."）を、OmniMechの図面理解プロンプト（"\<image\>\\nIdentify the exact mechanical component class and functional geometry depicted in this 2D orthographic drawing."）と同一のInstruction形式に統一する。これにより、IMPACTで獲得した視覚的構造表現力をそのままOmniMech上でZero-shot/Few-shot分類精度として転移測定できる。

### **第2位: MCB (Mechanical Components Benchmark \- 2D View Setting)**

MCBは、国際標準ICS分類体系に基づき、多様な機械要素部品の3D形状および2D多視点レンダリング画像を分類・検索する伝統的かつ標準的なベンチマークである4。

* **採用の利点**:  
  * 機械工学分野における工業部品分類の金字塔的ベンチマークであり、査読者に対する認知度と納得感が極めて高い4。  
  * 意匠特許における「ロカルノ国際分類」と同様の階層的カテゴリ構造（ICSコード）を備えており、ドメイン特化モデルが示す専門的知識の定量化に適している5。  
* **懸念点と課題**:  
  * 画像データが3D CADモデルからのレンダー画像（シェーディング付き立体像）主体であるため、特許図面の純粋な「黒白の線画」とはテクスチャが一部異なる4。  
* **IMPACTデータとの学習設定統合プロトコル**:  
  * MCBの2D多視点レンダリング像を意匠特許の多視点配置画像（1枚の画像に正面図・側面図等を結合したグリッド）と同様の入力フォーマットに変換する。入力に対して "\<image\>\\nClassify this engineering component into its corresponding ICS category." という指示を与えることで、1枚の画像から単一のカテゴリ文字列を出力する完璧なFGVCタスクとして設定できる。

### **第3位: SIP-17 (Synthetic Industrial Parts Dataset)**

SIP-17は、実際の製造・検査工程で発生する「ネジの有無」「Oリングの装着」「微細なギア歯数の相違」といった、超細粒度な工業部品識別タスクを提供するベンチマークである6。

* **採用の利点**:  
  * タスク形式が「1枚の画像入力 → 17種類の部品ラベルの単一予測」という極めてシンプルな画像分類（FGVC）であり、評価パイプラインの構築が容易である6。  
  * 汎用VLMが最も苦手とする「画像全体の意味論的には同じに見えるが、数ピクセルの局所的構造変化によってラベルが変わる」ケースを評価できる6。  
* **懸念点と課題**:  
  * クラス数が17と限定的であるため、語彙力や大規模概念空間の評価というよりは、「局所的微小特徴に対する感度」の評価に特化する形となる6。  
* **IMPACTデータとの学習設定統合プロトコル**:  
  * IMPACTデータセットでチューニングされたQwen3-VL-4Bに対し、"\<image\>\\nDetermine the fine-grained industrial part category, attending to minute structural elements such as screws, rings, or pins." というプロンプトを入力し、Top-1識別精度を算出する。

### **第4位: Products-10K**

Products-10Kは、約1万カテゴリにおよぶ商業製品・プロダクトデザインの画像を対象とした超大規模なロングテール細粒度分類ベンチマークである9。

* **採用の利点**:  
  * 約10,000クラスという広大な語彙空間における長尾分布分類であり、意匠特許の多種多様な製品タイトル（ニッチな専門器具から消費財まで）をカバーする大容量識別能力を実証するのに最適である3。  
  * CVPRで発表された著名なベンチマークであり、最新のConvNeXtやViT等のSOTA分類モデルのベンチマークスコア（Top-1 Accuracy等）が揃っているため比較が容易である9。  
* **懸念点と課題**:  
  * 画像が実写の製品写真中心であるため、意匠図面（線画）で学習したモデルを入力する際には、ドメイン転移（線画から実写プロダクトへの概念汎化）の能力が問われる10。  
* **IMPACTデータとの学習設定統合プロトコル**:  
  * IMPACTのタイトル予測（テキスト出力）でファインチューニングされたVLMに対し、Products-10Kの画像を直接提示し、"\<image\>\\nSpecify the precise product class for this item." というゼロショット分類形式で出力を生成させ、Top-1 / Top-5 AccuracyおよびmAPを算出する。

### **第5位: RP2K**

RP2Kは、2,384種類のリテールSKU商品を対象とし、同一製品の微小なバリエーション違いを高精度に判別することを求める細粒度画像分類ベンチマークである9。

* **採用の利点**:  
  * **「汎用VLMのZero-shot限界」を示す明確な先行データが存在する**: 無改造の汎用CLIP（ViT-B/32）のTop-1精度が41%**に低迷するのに対し、ドメイン特化チューニングを行ったモデルは**89%〜93%の精度を叩き出すことが検証されている1。論文執筆時、「汎用マルチモーダルモデル（GPT-4V/CLIP等）はニッチ・細粒度製品の識別で40%前後に留まるが、我々の特化モデルはこれを圧倒する」という説得力のある定量的ストーリーを展開できる1。  
* **懸念点と課題**:  
  * 純粋な立体形状（幾何構造）だけでなく、パッケージ上のテキスト情報やロゴの意匠に依存するサンプルが多く含まれる1。  
* **IMPACTデータとの学習設定統合プロトコル**:  
  * IMPACTデータで学習させたモデルの「細粒度プロダクト表現力」をテストするため、RP2Kのテストセットに対するゼロショット分類プロンプトを実行し、既存のCLIP BaseやGPT-4VのZero-shot精度に対する上振れ幅を比較測定する1。

## **結論および研究展開の提言**

本調査を通じて、意匠特許（IMPACTデータセット）の図面画像とタイトル・クレームテキストを用いたドメイン特化VLM（Qwen3-VL-4B LoRA等）の評価においては、視覚的・構造的・領域的特性に応じた多角的なベンチマーク選定が極めて効果的であることが明らかになった3。  
具体的には、論文構成上のメインとなる第一の実験軸として、特許図面と最も類似した2D線画・構造表現を扱う**OmniMech**2 および機械要素分類の標準である**MCB**4 を配置することが推奨される。これにより、「汎用VLMは線画の幾何構造や専門的な機械要素の解釈に失敗するが、提案モデルは正確に認識できる」というコアの主張を強固に確立できる2。  
続いて第二の実験軸として、局所的な微小構造差分を測る**SIP-17**6、ならびに超大規模なプロダクトSKU分類を要求する**RP2K**や**Products-10K**10 を組み合わせる。特にRP2Kにおいては、汎用CLIPのゼロショット精度が41%程度に失速するという強力なベースライン結果が報告されているため1、ドメイン特化チューニングによってこれを劇的に上回る定量的証拠を提示することで、学術的・実用的な論文の説得力を最大化することが可能である。  
すべての評価は、"\<image\>\\nPredict the product name/category." という統一されたInstructionプロンプトを通じて実施し、単一ラベルの正確性（Top-1 Accuracy / Top-5 Accuracy）としてスコア化することで、IMPACTデータセット上でのファインチューニングパイプラインと完全に調和したスマートな実験展開が実現される2。

#### **引用文献**

> 1. Image Embedding Models: Which to Use and Why Fine-Tuning Wins in 2026 | Width.ai, [https://www.width.ai/post/image-embedding-models](https://www.width.ai/post/image-embedding-models)  
> 2. OmniMech: All-in-one Multimodal Mechanical Benchmark for 3D Reconstruction \- arXiv, [https://arxiv.org/html/2608.05539v1](https://arxiv.org/html/2608.05539v1)  
> 3. IMPACT: A Large-scale Integrated Multimodal Patent Analysis and Creation Dataset for Design Patents, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/e3301977b92f28e32639ec99eb08f4a1-Paper-Datasets\_and\_Benchmarks\_Track.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/e3301977b92f28e32639ec99eb08f4a1-Paper-Datasets_and_Benchmarks_Track.pdf)  
> 4. Optimizing Multi-View CNN for CAD Mechanical Model Classification: An Evaluation of Pruning and Quantization Techniques \- MDPI, [https://www.mdpi.com/2079-9292/14/5/1013](https://www.mdpi.com/2079-9292/14/5/1013)  
> 5. A Large-Scale Annotated Mechanical Components Benchmark for Classification and Retrieval Tasks with Deep Neural Networks \- Academia.edu, [https://www.academia.edu/96771321/A\_Large\_Scale\_Annotated\_Mechanical\_Components\_Benchmark\_for\_Classification\_and\_Retrieval\_Tasks\_with\_Deep\_Neural\_Networks](https://www.academia.edu/96771321/A_Large_Scale_Annotated_Mechanical_Components_Benchmark_for_Classification_and_Retrieval_Tasks_with_Deep_Neural_Networks)  
> 6. Towards Sim-to-Real Industrial Parts Classification with Synthetic Dataset \- arXiv, [https://arxiv.org/html/2404.08778v1](https://arxiv.org/html/2404.08778v1)  
> 7. \[2502.15448\] MVIP \-- A Dataset and Methods for Application Oriented Multi-View and Multi-Modal Industrial Part Recognition \- arXiv, [https://arxiv.org/abs/2502.15448](https://arxiv.org/abs/2502.15448)  
> 8. MVIP \- A Dataset and Methods for Application Oriented Multi-View and Multi-Modal Industrial Part Recognition \- arXiv, [https://arxiv.org/html/2502.15448v1](https://arxiv.org/html/2502.15448v1)  
> 9. Benchmarking Image Embeddings for E-Commerce: Evaluating Off-the Shelf Foundation Models, Fine-Tuning Strategies and Practical Trade-offs \- arXiv, [https://arxiv.org/html/2504.07567v1](https://arxiv.org/html/2504.07567v1)  
> 10. Unveiling the Power of Diffusion Features For Personalized Segmentation and Retrieval, [https://arxiv.org/html/2405.18025v1](https://arxiv.org/html/2405.18025v1)  
> 11. Find your Needle: Small Object Image Retrieval via Multi-Object Attention Optimization \- arXiv, [https://arxiv.org/html/2503.07038v1](https://arxiv.org/html/2503.07038v1)  
> 12. DeepACO: A Robust Deep Learning-Based Automatic Checkout System \- CVF Open Access, [https://openaccess.thecvf.com/content/CVPR2022W/AICity/papers/Pham\_DeepACO\_A\_Robust\_Deep\_Learning-Based\_Automatic\_Checkout\_System\_CVPRW\_2022\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2022W/AICity/papers/Pham_DeepACO_A_Robust_Deep_Learning-Based_Automatic_Checkout_System_CVPRW_2022_paper.pdf)  
> 13. Hier-COS: Making Deep Features Hierarchy-aware via Composition of Orthogonal Subspaces \- arXiv, [https://arxiv.org/html/2503.07853v2](https://arxiv.org/html/2503.07853v2)  
> 14. Daily Papers \- Hugging Face, [https://huggingface.co/papers?q=Textile%20material%20identification](https://huggingface.co/papers?q=Textile+material+identification)  
> 15. Universal Image Embedding: Retaining and Expanding Knowledge With Multi-Domain Fine-Tuning \- ResearchGate, [https://www.researchgate.net/publication/370082023\_Universal\_Image\_Embedding\_Retaining\_and\_Expanding\_Knowledge\_with\_multi-domain\_fine-tuning](https://www.researchgate.net/publication/370082023_Universal_Image_Embedding_Retaining_and_Expanding_Knowledge_with_multi-domain_fine-tuning)  
> 16. How to estimate the accuracy upper limit of any CNN model over a computer vision classification task \- AI Stack Exchange, [https://ai.stackexchange.com/questions/19880/how-to-estimate-the-accuracy-upper-limit-of-any-cnn-model-over-a-computer-vision](https://ai.stackexchange.com/questions/19880/how-to-estimate-the-accuracy-upper-limit-of-any-cnn-model-over-a-computer-vision)  
> 17. HSS-IAD: A Heterogeneous Same-Sort Industrial Anomaly Detection Dataset \- arXiv, [https://arxiv.org/html/2504.12689v1](https://arxiv.org/html/2504.12689v1)  
> 18. UniAD: A Real-World Multi-Category Industrial Anomaly Detection Dataset with a Unified CLIP-Based Framework \- MDPI, [https://www.mdpi.com/2078-2489/16/11/956](https://www.mdpi.com/2078-2489/16/11/956)  
> 19. RetailDet: An Efficient Fusion Attention Network for Joint Product and Vacancy Identification in Smart Retail \- ResearchGate, [https://www.researchgate.net/publication/396507051\_RetailDet\_An\_Efficient\_Fusion\_Attention\_Network\_for\_Joint\_Product\_and\_Vacancy\_Identification\_in\_Smart\_Retail](https://www.researchgate.net/publication/396507051_RetailDet_An_Efficient_Fusion_Attention_Network_for_Joint_Product_and_Vacancy_Identification_in_Smart_Retail)  
> 20. Principles and Metrics for Curating Large Engineering Simulation Data Sets for ML, [https://www.honda-ri.de/pubs/pdf/6438.pdf](https://www.honda-ri.de/pubs/pdf/6438.pdf)