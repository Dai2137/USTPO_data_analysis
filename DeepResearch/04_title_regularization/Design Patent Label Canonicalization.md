# **意匠特許タイトル文字列の正規化・統合と画像分類ラベル体系構築に関する包括的サーベイ報告書**

## **1\. 課題設定と意匠特許タイトルのドメイン特性**

米国特許商標庁（USPTO）のIMPACTデータセット等を用いた意匠特許図面からの製品タイトル予測において、自由記述の英語タイトル（titleフィールド）を深層学習（画像分類モデル）の教示ラベルとして直接使用することには明確な原理的限界が存在する。実データを詳細に検証すると、同一の意匠形態を指す表現群が極めて高い表記多様性を持っている。第一に単語自体の語彙が異なる「真の同義語」（"Coffee Maker" と "Coffeemaker"、"Bicycle" と "Bike"、"Automobile" と "Car"）、第二に共通トークンを保持しない「構文的パラフレーズ」（"Beverage cooler" と "Cooler for beverages"、"Beverage-making machine" と "Machine for producing a beverage"）、第三に概念の包含関係に基づく「抽象度・粒度の不一致」（"Shoe" と "Footwear"、"Chair" と "Office chair"、"Vehicle" と "Automobile"）が大量に混在している。  
これらの名詞句ペアは、単語レベルの重複率が極めて低いかゼロであるにもかかわらず、汎用的な文埋め込みモデル（Sentence Transformers等）によるコサイン類似度は0.8から1.0の極めて高い領域に集中する。その結果、小文字化、語尾削除（ステミング/レマタイズ）、語順ソートなどの従来の規則ベースな語彙正規化（Lexical Normalization）では同義性の検出が不可能である。  
一方で、データセットには世界知的所有権機関（WIPO）が定めるロカルノ国際意匠分類（Locarno Classification）の階層的コード（例：Class 02 Subclass 04 "02-04"＝履物）が全件に割り当てられている1。この分類コードは構造化されたカテゴリとして利用可能であるものの、粒度が粗く、1つのサブクラス内に「オフィスチェア」「ダイニングチェア」「折りたたみ椅子」など全く異なる幾何形状を持つ製品群が数千件単位で混在する課題がある。したがって、本研究の目標はゼロから新たな分類体系を自動生成することではなく、既存の粗い階層コード（Locarno）を固定的な足場（Anchor）とし、その各サブクラス内部で自由記述タイトルを意味的に統合・標準化することで、画像分類に適した「中間粒度（Intermediate-grained）のクリーンな閉集合ラベル体系」を構築することに定式化される。

## **2\. ラベル正規化・統合の手法論**

自由記述テキストや名詞句の集合から、意味的に同一・類似の対象を指す標準的表現（Canonical Label）へと集約・整理する手法は、分散表現の幾何学的性質を利用するアプローチから、知識構造の利用、そして大規模言語モデル（LLM）の推論能力を活用するアプローチへと進化を遂げている。

### **2.1 埋め込みベースのクラスタリングとエンティティ正規化**

テキストを分散表現（Dense Vector）へ変換し、ベクトル空間上の近接性に基づいてクラスタリングを行う手法は、表記ゆれ吸収の標準的枠組みである。しかし、汎用の言語モデルや文埋め込み（Word2Vec, FastText, 標準SBERT）をそのまま適用した場合、同一文脈に出現しやすい異なる概念（例："Office chair" と "Gaming chair"）が過度に近接し、高精度なカテゴリ分離が困難になる問題が指摘されている2。この問題に対し、SANTA（Scalable Attribute Normalization）などの手法では、生タイトルと属性表現のペアに対してトリプレット損失（Triplet Loss）を伴うツインネットワーク（Twin Network）を適用し、表記異形（Surface Forms）と標準形（Canonical Forms）の間の距離を自己教師あり学習によって最適化する手法が提案されている2。また、Eコマースドメインにおいては、Doc2Vec（DBOW構造）による特徴抽出とコサイン距離に基づく階層的クラスタリング（Hierarchical Agglomerative Clustering; HAC）を組み合わせ、類似タイトル群のセントロイドから標準タイトルを導出する手法が実証されている4。

### **2.2 知識グラフ・オントロジー・タクソノミー誘導**

外部の構造化知識（WordNet, UMLS等）やテキストコーパスから自動的に概念階層（Taxonomy Induction）を抽出する手法は、上位語・下位語（Hypernymy/Hyponymy）関係の整理に強みを持つ。非構造化テキストから自動的に知識グラフを構築するEDC（Extract-Define-Canonicalize）フレームワークでは、開放型情報抽出（Open IE）を行った後に、LLMによるスキーマ定義と事後正規化（Post-hoc Canonicalization）を実行することで、事前定義スキーマが存在しない、あるいはスキーマが長大でプロンプトに収まらない設定下でも高品質な標準表現群を自動生成する6。

### **2.3 LLMを用いたラベル正規化・カテゴリ統一**

LLMの高度な文脈理解と命令追従能力（Instruction Following）を活用し、自由記述ラベルをダイレクトに標準カテゴリへマッピングするアプローチが急速に普及している。TnT-LLM（Taxonomy and Text Classification with LLMs）は、大規模コーパスからゼロショットかつ多段階推論（Multi-stage Reasoning）を用いてラベルタクソノミーを反復的に生成・洗練し、テキストに対してプライマリラベルを割り当てるパイプラインを提供する7。LLMを活用することで、構文が丸ごと異なるパラフレーズや暗黙のドメイン知識を要する同義語の統合において、従来の文字列一致や固定埋め込みを超える柔軟な正規化が可能となる7。また、Legal-LLMにみられるように、法的なカテゴリ分類等の複雑なラベル割り当てにおいても、指示チューニング（Instruction-tuning）を施したモデルが人間と同等以上の整合性でラベルを標準化できることが示されている9。

### **2.4 人間参加型（Human-in-the-Loop）によるコスト制御**

全自動でのラベル統合は過剰統合（異なる概念の同一化）や過少統合（同義語の残留）のリスクを常にはらむため、モデルの予測不確定性（Entropy）やクラスタ境界のサンプルのみを人間（ドメインエキスパート）にアノテーション依頼するアクティブ・キャノニカリゼーションが実践されている7。特にLLMによる自己修正・批判ステップ（Self-Critique）を導入し、人間の介入が必要な低信頼度サンプルを能動的に抽出することで、作業コストを大幅に削減しながら高品質なラベル体系を確保するアプローチが効果を上げている10。

| 手法名・文献 | 生ラベル形式 | 既存タクソノミー | 統合・正規化アルゴリズム | 評価方法・指標 | 公開実装 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **SANTA** \[cite: 2, 3\] | 属性の表記異形（Surface Forms） | なし | Twin Network ＋ Triplet Loss による自己教師あり埋め込み学習とコサイン類似度マッピング | 識別精度（Accuracy）、Top-k Accuracy | なし（数理モデル定義） |
| **EDC Framework** \[cite: 6\] | 非構造化テキスト・生名詞句 | 任意（無段階で対応可能） | 情報抽出 ➔ LLMによるスキーマ自動定義 ➔ RAG型事後正規化（Post-hoc Canonicalization） | 抽出トリプレット精度・再現率、F1スコア | github.com/clear-nus/edc \[cite: 6\] |
| **TnT-LLM** \[cite: 7\] | 自由記述テキストコーパス | なし（ゼロショット生成） | 多段階推論による反復的タクソノミー洗練 ＋ プロンプトによる割り当て | Taxonomy Coverage（カバー率）、Label Accuracy (Pairwise Hit Rate) | プロンプト仕様公開7 |
| **Doc2Vec \+ HAC** \[cite: 4, 5\] | 商品タイトル（短名詞句） | なし | Doc2Vec (DBOW) 特徴抽出 ＋ 階層的クラスタリング（HAC） | 正規化相互情報量（NMI） | なし（パラメータ明記） |
| **LLM-KB Canonicalization** \[cite: 8\] | LLMからの生成テキスト・エンティティ | なし | 局所的プロンプトの統合 ➔ Graph Expansion ➔ LLMエンティティ曖昧性解消・クラス正規化 | 人手評価による整合性度合い、概念被覆率 | なし（フレームワーク提案） |

## **3\. 既存の粗い分類体系を足場にしたラベル精緻化**

上位カテゴリ（既存タクソノミー）がすでに存在する状況下で、その内部構造を分解・補完して細粒度なラベル体系を作り上げる技術は、「Taxonomy Refinement」「Taxonomy Expansion」「Taxonomy Completion」として体系化されている。

### **3.1 タクソノミー拡張・補完（Taxonomy Expansion & Completion）**

既存の粗い階層構造（Seed Taxonomy）に対し、新出現の概念や自由記述テキスト（Query Entities）を適切な親ノード（Parent）または兄弟ノード（Sibling）として追加挿入するアプローチである。

* **TMN（Topic Matching Network）**: 既存のタクソノミーにおける（親ノード, 子ノード）のペアに対し、新規クエリ概念が収まるべき「位置」をニューラルテンソルネットワーク（Neural Tensor Network）によりOne-to-Pairマッピングとして算出・補完する11。  
* **DNG（Directed Non-Gaussianity Model）**: タクソノミーにおける特徴の継承（ParentからChildへの方向的伝律）を定式化し、非ガウス制約（Non-Gaussian Constraint）を課すことで、不可逆な包含関係を高精度にモデル化して新規クエリの挿入位置を特定する12。  
* **TaxoInstruct**: LLMに対して「兄弟ノードの発見」と「親ノードの発見」の2つの基本スキルを指示チューニング（Instruction Tuning）により学習させ、単一のフレームワークで自動タクソノミー拡張を実現する13。  
* **TopicExpan**: コーパスのテキスト情報と階層構造のトポロジーを同時に活用し、低頻度語を含む新たなサブトピックを階層意識型フレーズ生成（Hierarchy-aware Phrase Generation）によって直接抽出し、タクソノミー内に挿入する14。

### **3.2 既存分類コードと自由記述テキストの融合**

実用ドメイン（特許、産業分類、商品管理）では、記号的分類コード（Locarno, IPC, CPC）と自由記述テキストの双方を活用したハイブリッドな精緻化が行われている16。特許分野におけるPatent Landscape Study（PLS）等の研究では、既知のCPC/IPCコードを文書表現の前提（コンディショニング制約）としてテキスト埋め込みと結合させることで、分類コード単体では表現不可能なドメイン固有の細粒度カテゴリを再構築している17。粗いコードによる大枠の空間分割（Partitioning）と、内部における自由記述テキストの意味的統合を段階的に適用することで、検索・分類の精度が大幅に向上することが実証されている17。

| 手法名・文献 | 入力形式 | 既存タクソノミーの役割 | 階層精緻化・挿入アルゴリズム | 評価方法・指標 | 公開実装 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **TaxoInstruct** \[cite: 13\] | 既存タクソノミー ＋ 未知クエリエンティティ | 概念の探索空間および教示データとして利用 | LLMに対する「親・兄弟発見タスク」の指示チューニングと相互強化 | 位置予測精度（Accuracy）、Wu & Palmer類似度、Macro F1 | github.com/yanzhen4/TaxoInstruct \[cite: 13\] |
| **DNG Model** \[cite: 12\] | タクソノミーグラフ ![][image1] ＋ 新規クエリ ![][image2] | 有向非巡回グラフ（DAG）構造として固定 | 継承特徴（Inherited Feature）と非ガウス制約による不可逆関係モデル化 | Precision@K, MRR (Mean Reciprocal Rank) | なし（数理モデル提示） |
| **TopicExpan** \[cite: 14, 15\] | 既存トピック階層 ＋ コーパステキスト | 局所的・大域的階層関係のコンディショニング | 階層意識型トピックフレーズ生成（Hierarchy-aware Phrase Generation） | トピック一貫性（Coherence）、Taxonomy Coverage | なし（論文内詳細） |
| **Partial Label Model (PLM)** \[cite: 19\] | 部分的に注釈されたテキストデータ | 新旧のエンティティ型タクソノミー関係 | 擬似ラベル生成 ＋ KLダイバージェンス損失最小化による多階層予測 | Precision, Recall, Micro/Macro F1 | なし（理論・実験提示） |
| **PLS Classification** \[cite: 17\] | 特許テキスト ＋ IPC/CPC分類コード | 推論・統合時の絶対的固定制約（Anchor） | IPC/CPC表現と特許本文のベクトル結合による多レベル分類 | Classification Accuracy, F1-score | なし（適用事例） |

## **4\. ノイズを含む自由記述ラベルからの分類学習**

テキスト処理段階で同義語やパラフレーズを完全に一次元のクリーンな単一ラベルへ収束させることが困難な場合、あるいは抽象度の異なるラベルが残存する場合、画像分類モデル（Vision Backbone）側の学習アルゴリズムによってラベルノイズや多粒度性を吸収するアプローチが必要となる。

### **4.1 Web由来ノイズラベル学習（Noisy Label Learning）**

画像分類分野におけるWebVision, Clothing1M, iNaturalist等の研究では、テキスト検索やユーザーの自由記述から取得した弱教師ラベル（Noisy Web Labels）に含まれる表記不一致や誤ラベルの対処法が確立されている。代表的手法であるConfident Learning（コンフィデント・ラーニング）は、以下の3つの理論的ステップでモデルの堅牢性を保証する20。

> 1. **Pruning（プルーニング）**: 現在のモデルの予測確率分布と付与されているラベルの不一致度合いを測定し、ノイズと判定されたサンプルを学習セットから除去または割り当てを修正する20。  
> 2. **Counting（カウンティング）**: 類別遷移確率（Class-conditional Label Noise Matrix）を非パラメトリックに推計し、どのクラス間へ表記ブレや混乱が発生しているかを定量化する20。  
> 3. **Ranking（ランキング）**: ラベルの正当性の信頼度順にサンプルをソートし、損失関数における勾配の寄与度（Loss Weighting）を調整する20。

### **4.2 オープンボキャブラリから閉集合クラスへの変換**

CLIPやAlignに代表される多角的分散表現空間（Vision-Language Joint Embedding Space）を利用することで、自由記述のテキストラベルをプロンプト（例："A design patent drawing of a {canonical\_label}"）を介して埋め込み空間上の点として多次元展開する。入力画像の特徴ベクトルと、候補となる各正規化クラスプロンプトとのコサイン類似度を算出し、Softmax関数に通すことで、オープンボキャブラリを円滑に閉集合分類（Closed-set Classification）のロジット（Logits）へと変換できる。

### **4.3 階層的・多粒度ラベル学習（Hierarchical & Multi-Granularity Learning）**

ラベル空間に上位概念（Locarno Subclass等）と下位概念（正規化された精緻タイトル）が共存する場合、単一レベルのCross-Entropy損失を用いると抽象度の相違が学習を阻害する。このため、粗いラベルの予測損失 ![][image3] と細粒度ラベルの予測損失 ![][image4] をマルチタスク構造で同時に最適化する多粒度学習（Multi-granularity Label Learning）が有効である。  
![][image5]  
これにより、視覚的に分類が困難な極小カテゴリであっても、上位のLocarnoサブクラスとしての視覚的共通性を正しく学習しつつ、精緻なタイトル予測能力を補完することが可能となる。

| 手法名・文献 | 弱教師・生ラベル形式 | 学習・補正アルゴリズム | 階層/多粒度統合手法 | 評価方法・指標 | 公開実装 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **Confident Learning (Cleanlab)** \[cite: 20\] | ノイズを含むカテゴリラベル | Pruning（削除）, Counting（ノイズ行列推定）, Ranking（信頼度ソート） | 任意（単一/多階層ラベルへ適用可能） | Label Noise Estimation Precision, Downstream Test Accuracy | github.com/cleanlab/cleanlab \[cite: 20\] |
| **Legal-LLM Multi-Labeling** \[cite: 9\] | 複数ラベル混在テキスト | Instruction-tuning ＋ 逆頻度重み付け損失（Weighted Loss） | 多ラベル構造のシーケンス生成・閉集合変換 | Multi-label F1-score, Exact Match | なし（手法・記述明記） |
| **Distribution Alignment for LLMs** \[cite: 21\] | 不確実性のある複数ラベル | Max Probability Over Generation Steps による確率分布整列 | アンノテーター分布とモデル予測確率のアライメント | Top-1 Accuracy, Distribution Alignment F1 | なし（論文内アルゴリズム） |

## **5\. 近接ドメインにおける実例**

名詞句タイトルの正規化、表記ゆれの名寄せ、および既存分類コードとの融合は、Eコマース、生物医学、特許の各産業ドメインにおいて先進的な実例が存在する。

### **5.1 Eコマースにおける商品タイトル・属性正規化**

Amazon, Rakuten, Alibaba等のEコマースプラットフォームでは、出品者が入力する自由記述のタイトルや属性値（例："Win 10 Pro", "Windows 10", "W10"）を、共通の標準属性値（"Windows 10"）へマッピングする課題が分析されている2。

* **SANTA**: 属性の表面形式（Surface Form）と標準形式（Canonical Form）のペアに対し、商品タイトル文脈を含めた自己教師ありツインネットワークを学習させ、構文的類似性のみでは解けない完全な同義語（"720p" ＝ "HD"）の正規化を達成している2。  
* **検索クエリのブランド・エンティティリンキング**: 2段階のNamed Entity Recognition (NER) とエンティティ曖昧性解消（Disambiguation）、あるいはExtreme Multi-class Classificationを用いて、曖昧な短文クエリを既知のグローバルブランドエンティティへ紐づける23。

### **5.2 生物医学分野の用語正規化**

UMLS（Unified Medical Language System）概念正規化やSapBERTの研究分野では、臨床ノートや論文中の多様な表記（例："heart attack" と "myocardial infarction"）を単一の概念コード（CUI）へ集約する。ドメイン特化型トリプレット学習や概念階層グラフを用いたアプローチは、意匠特許タイトルの標準化処理における同義語統合・上位語統合と数学的に同値の構造を持つ。

### **5.3 特許・知的財産（IP）ドメインにおける名寄せ・統合**

特許分析分野では、文字表現の近接性のみならず、特許の文脈（ClaimsやDescription）を用いた埋め込み表現による統合が重視されている。

* **PatentSBERTa**: 特許クレーム（Claims）のテキストデータを用い、Augmented SBERTの手法でドメイン特化ファインチューニングを施した文埋め込みモデルである18。特許間の技術的距離（Patent-to-Patent Distance）をベクトルの類似度として精度高く算出し、k近傍法（KNN）と組み合わせることで、多ラベルのCPCサブクラス（600種類以上）予測において極めて高い精度（Accuracy 54%, F1 \> 66%）を達成している18。  
* **PatentBERT**: 大規模な特許文脈を用いてBERTを適応させたモデルであり、特許タイトルや要約、クレームから自動的に特許分類コードを事前予測する標準モデルとして機能する25。

意匠特許分野（Design Patents）では、技術特許のIPC/CPCの代わりにロカルノ分類（Locarno Classification）が用いられるが、上記の手法体系（特許文脈埋め込み ＋ 構造化分類コードの結合）は、そのまま意匠特許タイトルの正規化パイプラインへと移植可能である17。

| 手法名・ドメイン | 対象テキスト | 既存コード/タクソノミー | 名寄せ・標準化手法 | 評価方法・指標 | 公開実装 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **SANTA**（Eコマース）2 | 属性値・商品タイトル | なし | Twin Network ＋ Triplet Loss による分散表現学習 | Accuracy, Top-k Accuracy | なし（アルゴリズム詳細） |
| **E-Commerce Brand Entity Linking** \[cite: 23\] | 短い検索クエリ | グローバルブランドKB | NER ＋ Disambiguation / Extreme Multi-Class Classification | Offline Recall, Customer Engagement (A/B Test) | なし（産業事例） |
| **PatentSBERTa**（特許・IP）18 | 特許クレーム・タイトル | CPC / IPC分類体系 | Augmented SBERT ＋ KNNによるセマンティック距離推計・多ラベル予測 | CPC Subclass Accuracy, F1-score | huggingface.co/AI-Growth-Lab/PatentSBERTa \[cite: 18, 28\] |
| **Rakuten Product Categorization** \[cite: 22\] | 商品タイトル・説明文 | 5階層 Eコマースタクソノミー | Deep Belief Nets ＋ Deep Autoencoders | Category Matching Accuracy (81%) | なし（産業事例） |

## **6\. 評価方法とラベル粒度の決定基準**

自由記述タイトルを統合・正規化して構築された正解ラベル体系の「質」の定量評価、および「どの程度まで同義語・上位語としてまとめるべきか」という粒度制御（Stopping Criteria）は、ラベル生成モデルの評価と下流の画像分類性能の評価の両面から規定される。

### **6.1 統合ラベル体系の定量評価指標**

> 1. **クラスタリング品質指標**: 生タイトル群をクラスタリングによって集約する場合、**クラスタ純度（Purity）**、**正規化相互情報量（NMI）**、および調整ランド指数（ARI）が標準的に使用される4。  
> 2. **LLM生成タクソノミー評価指標**: TnT-LLM等で提唱されている評価軸7。  
   * **Taxonomy Coverage（カバー率）**: 生成された正規化ラベル体系がコーパス全体を網羅しているか。割り当て時に「Other / Undefined」カテゴリへ分類されたサンプルの比率が低いほど高いカバー率を示す7。  
   * **Label Accuracy（ラベル精度）**: 各サンプルに対する正解ラベルと、同タクソノミー内のランダムな負例ラベルを提示し、評価者（人間または評価用LLM）が正解を正しく識別できる確率（Pairwise Hit Rate）で測定する7。  
> 3. **語彙収縮率（Vocabulary Reduction Ratio）**: 生タイトルの異彩数（Unique Raw Titles）に対する正規化後のクラス数（Unique Canonical Labels）の圧縮比率。

### **6.2 下流タスク（画像分類）への影響評価**

統合されたラベル体系を正解ラベルとして用いて訓練された画像分類モデル（Vision Backbone）に対し、非公開のテストセットを用いて以下の指標を測定する18。

* **Top-1 / Top-5 Accuracy**: クリーンな検証画像に対する正確なクラス予測率25。  
* **Macro F1-score**: マイナーな製品カテゴリ（Long-tail Classes）に対する分類器の過学習を防げているかを評価する9。  
* **Cross-Modal Alignment Score**: 入力画像の視覚特徴量と、予測された正規化タイトルのテキスト埋め込み（CLIPテキストエンコーダー等）とのコサイン類似度。

### **6.3 統合粒度の決定基準（Stopping Criteria）**

タイトルの抽象度整理において、どこまで概念をまとめるかを決定するための客観的基準は以下の通りである。

> 1. **シルエット係数（Silhouette Coefficient）の極大化**: 埋め込み空間におけるクラスタ内の凝集度とクラスタ間の離隔度のバランスが崩れる手前で統合を停止する。  
> 2. **最小画像サンプル数制約（Minimum Instance Threshold）**: 画像分類器の学習に必要な画像数（例：1クラスあたり最小10〜20件）を下回る極小タイトルは、自動的に直近の上位概念（Hypernym）または親クラスタへ強制統合する。  
> 3. **情報量損失と純度のトレードオフ**: 過剰統合（例：すべての椅子を "Furniture" にまとめる）による視覚的・意味的情報損失と、過少統合によるラベルノイズ残存の交点を探索する。

| 評価観点・カテゴリ | 定量評価指標 / 定義 | 適用シナリオ | 粒度制御・決定基準 | 代表的研究文献 |
| :---- | :---- | :---- | :---- | :---- |
| **クラスタリング品質** | NMI (Normalized Mutual Information), Purity, ARI | 埋め込みベクトルのクラスタリングによる正規化 | シルエット係数の極大化、距離閾値 ![][image6] の設定 | Doc2Vec \+ HAC4 |
| **LLMタクソノミー品質** | Coverage (1 \- Undefined Ratio), Pairwise Hit Rate | LLMを用いたゼロショット/In-contextラベル生成 | 「Other」比率の閾値（例：\<5%）、反復洗練の収束 | TnT-LLM7 |
| **下流タスク性能** | Top-1/Top-5 Accuracy, Macro F1-score | 構築されたラベルを用いた画像分類モデルの学習 | 下流画像分類器の検証セットにおけるMacro F1最大化 | PatentSBERTa18, Legal-LLM9 |
| **実用性・データ規模** | Vocabulary Reduction Ratio, Min Instance / Class | 大規模長尾データセット（Long-tail Dataset）の整理 | 1クラスあたり最小サンプル数 ![][image7] | SANTA2, EDC6 |

## **7\. 意匠特許データへの推奨アプローチと3大手法の比較**

意匠特許タイトルのドメイン特性（「短い名詞句」「同義語・言い換え・粒度違いの混在」「ロカルノ分類という既存の粗い階層の存在」）に最も適合するパイプラインを設計し、要素技術の比較分析を行う。

### **7.1 推奨アプローチ（3選）**

#### **【推奨1】Locarno制約付きLLM 2段階正規化パイプライン（EDC/TnT-LLM 拡張型）**

* **構成**: 各ロカルノ・サブクラス（例："02-04" 履物）ごとにデータをパーティション分割（ハード制約）し、その内部に存在する自由記述タイトル集合をLLM（GPT-4oやClaude-3.5-Sonnet等）に与える。  
  * **ステージ1（標準クラス生成）**: サブクラス内の全生タイトルをLLMに提示し、「このサブクラスに含まれる製品を包括する中間粒度の標準カテゴリ名リスト（10〜30個程度）」を抽出・定義させる（TnT-LLM方式）7。  
  * **ステージ2（マッピングと正規化）**: 定義された標準カテゴリリストに基づき、各特許の生タイトルを最も適切な標準カテゴリへとマッピング・集約する（EDC方式）6。  
* **推奨理由**: 完全無制約でLLMを動かすとコンテキスト長超過やハルシネーションが発生するが、Locarnoサブクラスでコンテキストを限定することで、極めて高い整合性と妥当性を持つ正解ラベル体系が得られる。

#### **【推奨2】PatentSBERTa/SANTA 埋め込み ＋ Locarno内条件付きトリプレットクラスタリング**

* **構成**: 特許ドメインで事前学習されたPatentSBERTa18 またはSANTA型のツインネットワーク2 を用いて全タイトルの高次元ベクトルを取得する。Locarnoサブクラスの枠組みの中で階層的クラスタリング（HAC）を実行し、コサイン類似度が高いタイトル群を同一クラスタとして統合する。クラスタの代表名には、クラスタ内で最も出現頻度が高い生タイトル（またはメドイドタイトル）を採用する。  
* **推奨理由**: LLMの推論コストを一切かけず、数十万件規模の意匠特許データを即座かつ決定論的に処理できる。

#### **【推奨3】Confident Learning ＋ 多粒度（Locarno \+ Canonical Title）画像分類アーキテクチャ**

* **構成**: 推奨1または2で生成された正規化タイトルを初期ターゲットラベルとしつつ、Vision Transformer（ViTやSwin Transformer）等の画像分類モデルの訓練時にConfident Learning（Cleanlab）20 を導入する。さらに、損失関数として上位のLocarnoコードと細粒度の正規化タイトルの双方を予測するマルチタスク損失（Hierarchical Multi-task Loss）を構築する。  
* **推奨理由**: テキスト処理のみでは判別不可能な不完全な統合（過不足）が存在しても、画像側の特徴から誤ラベルを自動検知して学習から除外・修正できるため、最終的な画像分類器の堅牢性が最大化される20。

### **7.2 3大アプローチの詳細比較分析**

「LLMによるラベル正規化（アプローチA）」、「埋め込みクラスタリングによる正規化（アプローチB）」、「既存タクソノミー（Locarno）を制約として使うアプローチ（アプローチC）」の3つの基本的な枠組みを多角的な評価軸で比較する。

| 比較評価軸 | アプローチA: LLMによる正規化・カテゴリ統一 | アプローチB: 埋め込みクラスタリングによる正規化 | アプローチC: 既存タクソノミー（Locarno）制約アプローチ |
| :---- | :---- | :---- | :---- |
| **処理アルゴリズムの核心** | インコンテキスト推論による同義語・パラフレーズの認識と標準ラベルのダイレクト生成 | 密ベクトル空間におけるコサイン類似度算出と閾値に基づく距離クラスタリング | 記号的コードによる検索・識別空間のハード分割（Hard Partitioning） |
| **同義語・パラフレーズへの対応力** | **極めて高い**。"Beverage cooler" と "Cooler for beverages" のような無重複構文も完全に同一化7。 | **中〜高**。PatentSBERTa等の適切なモデルを使えば高類似度を示すが、閾値設定に依存2。 | **不可（単体時）**。コード内での文字・意味統合能力はなく、A/Bの枠組みとして機能。 |
| **抽象度・粒度不一致の解決力** | **極めて高い**。"Chair" と "Office chair" の概念包摂関係を推論し指定の粒度へ統一可能7。 | **低い**。ベクトル距離が近すぎるため、上位語と下位語が誤って同一クラスタに併合されやすい。 | **高（粗粒度のみ）**。Locarnoコードにより最上位概念（履物 vs 家具）の混同は100%防止1。 |
| **計算コスト・スケーラビリティ** | **低い（高コスト）**。大規模データセット全件に対するLLM API呼び出しや推論時間が大。 | **極めて高い**。ベクトル化とクラスタリングは高速で、数百万件規模へ容易に拡張可能18。 | **極めて高い**。メタデータ上のフィルタリングのみであり、計算コストは実質ゼロ。 |
| **未定義語・ドメイン専門用語の対応** | **高い**。LLMの広範な事前学習知識により新製品や複合名詞の意味を解釈可能。 | **中程度**。Out-of-Vocabularyや独特の造語において埋め込みが不安定になるリスク。 | **完全**。全特許に特許庁審査官によって付与されているため未定義が存在しない29。 |
| **結果の解釈性・透明性** | **高い**。LLMに統合理由の根拠（Rationale）を出力させることが可能10。 | **低い**。高次元ベクトルのクラスタリングであり、統合境界の解釈がブラックボックス化。 | **極めて高い**。WIPOが定義した明確なテキスト定義とガイドラインが存在1。 |
| **画像分類用ラベルとしての適合性** | 明瞭な人間が理解可能な標準名詞句が得られ、CLIP等のプロンプト生成に最適。 | クラスタIDとなりやすく、標準ラベル名の決定に追加処理（メドイド抽出等）が必要。 | 粗すぎて単体では画像分類の正解ラベルとして機能しない（アンダーフィッティング）。 |

### **7.3 結論**

比較分析から明らかなように、単一のアプローチのみで意匠特許タイトルの課題を完結させることは困難である。最も優位性の高い設計は、**「アプローチC（Locarno制約）」により大枠の概念境界を100%保証した上で、その内部において「アプローチA（LLM正規化）」を適用して自由記述タイトルの同義語・パラフレーズ・粒度違いを高度に集約し、さらに「アプローチB（埋め込み）」および「Confident Learning」によって大規模データ処理の効率化と画像分類学習時のラベルノイズ除去を行う統合的ハイブリッドアーキテクチャ**である。この多段階パイプラインを適用することにより、USPTO IMPACTデータセットから画像分類モデルの正解ラベルとして最も堅牢かつ高品質な中間粒度のラベル体系を構築することが可能となる。

#### **引用文献**

> 1. What You Need to Know About Searching Patents Using Patent Classifications \- PatSeer, [https://www.patseer.com/what-you-need-to-know-about-searching-patents-using-patent-classifications/](https://www.patseer.com/what-you-need-to-know-about-searching-patents-using-patent-classifications/)  
> 2. arXiv:2106.09493v1 \[cs.CL\] 12 Jun 2021, [https://arxiv.org/pdf/2106.09493](https://arxiv.org/pdf/2106.09493)  
> 3. Scalable Approach for Normalizing E-commerce Text Attributes (SANTA) \- ACL Anthology, [https://aclanthology.org/2021.ecnlp-1.12.pdf](https://aclanthology.org/2021.ecnlp-1.12.pdf)  
> 4. Optimizing Product Matching in E-Commerce with DOC2VEC: Leveraging Hierarchical Clustering Parameters Based on Product Titles | ECTI Transactions on Computer and Information Technology (ECTI-CIT) \- ThaiJo, [https://ph01.tci-thaijo.org/index.php/ecticit/article/view/256164](https://ph01.tci-thaijo.org/index.php/ecticit/article/view/256164)  
> 5. Optimizing Product Matching in E-Commerce with DOC2VEC: Leveraging Hierarchical Clustering Parameters Based on Product Titles \- ResearchGate, [https://www.researchgate.net/publication/382807567\_Optimizing\_Product\_Matching\_in\_E-Commerce\_with\_DOC2VEC\_Leveraging\_Hierarchical\_Clustering\_Parameters\_Based\_on\_Product\_Titles](https://www.researchgate.net/publication/382807567_Optimizing_Product_Matching_in_E-Commerce_with_DOC2VEC_Leveraging_Hierarchical_Clustering_Parameters_Based_on_Product_Titles)  
> 6. Extract, Define, Canonicalize: An LLM-based Framework for Knowledge Graph Construction, [https://aclanthology.org/2024.emnlp-main.548/](https://aclanthology.org/2024.emnlp-main.548/)  
> 7. TnT-LLM: Text Mining at Scale with Large Language Models \- arXiv, [https://arxiv.org/html/2403.12173v1](https://arxiv.org/html/2403.12173v1)  
> 8. GPTKB: Building Very Large Knowledge Bases from Language Models \- arXiv, [https://arxiv.org/html/2411.04920v1](https://arxiv.org/html/2411.04920v1)  
> 9. Improving the Accuracy and Efficiency of Legal Document Tagging with Large Language Models and Instruction Prompts \- arXiv, [https://arxiv.org/html/2504.09309v1](https://arxiv.org/html/2504.09309v1)  
> 10. Building Multi-turn Intent Classification with LLM-based Labeling \- ACL Anthology, [https://aclanthology.org/2026.customnlp4u-1.8/](https://aclanthology.org/2026.customnlp4u-1.8/)  
> 11. Taxonomy Completion via Triplet Matching Network \- AAAI Publications, [https://ojs.aaai.org/index.php/AAAI/article/view/16596/16403](https://ojs.aaai.org/index.php/AAAI/article/view/16596/16403)  
> 12. DNG: Taxonomy Expansion by Exploring the Intrinsic Directed Structure on Non-gaussian Space \- AAAI Publications, [https://ojs.aaai.org/index.php/AAAI/article/view/25810/25582](https://ojs.aaai.org/index.php/AAAI/article/view/25810/25582)  
> 13. arXiv:2402.13405v5 \[cs.CL\] 23 May 2025, [https://arxiv.org/pdf/2402.13405](https://arxiv.org/pdf/2402.13405)  
> 14. Topic Taxonomy Expansion via Hierarchy-Aware Topic Phrase Generation \- ACL Anthology, [https://aclanthology.org/2022.findings-emnlp.122.pdf](https://aclanthology.org/2022.findings-emnlp.122.pdf)  
> 15. Topic Taxonomy Expansion via Hierarchy-Aware Topic Phrase Generation \- ACL Anthology, [https://aclanthology.org/2022.findings-emnlp.122/](https://aclanthology.org/2022.findings-emnlp.122/)  
> 16. IPC vs CPC Classification: Which Patent System Should You Use? | Wicely Resources, [https://wicely.com/resources/ipc-vs-cpc-classification-guide](https://wicely.com/resources/ipc-vs-cpc-classification-guide)  
> 17. Neural Patent Classification beyond Title and Abstract: Leveraging Patent Text and Metadata \- heiDOK, [https://archiv.ub.uni-heidelberg.de/volltextserver/35223/](https://archiv.ub.uni-heidelberg.de/volltextserver/35223/)  
> 18. PatentSBERTa: A Deep NLP based Hybrid Model for Patent Distance and Classification using Augmented SBERT \- GitHub, [https://github.com/AI-Growth-Lab/PatentSBERTa](https://github.com/AI-Growth-Lab/PatentSBERTa)  
> 19. Taxonomy Expansion for Named Entity Recognition \- ACL Anthology, [https://aclanthology.org/2023.emnlp-main.426.pdf](https://aclanthology.org/2023.emnlp-main.426.pdf)  
> 20. Confident Learning-Based Label Correction for Retinal Image Segmentation \- MDPI, [https://www.mdpi.com/2075-4418/15/14/1735](https://www.mdpi.com/2075-4418/15/14/1735)  
> 21. Large Language Models Do Multi-Label Classification Differently \- ACL Anthology, [https://aclanthology.org/2025.emnlp-main.126/](https://aclanthology.org/2025.emnlp-main.126/)  
> 22. Large-scale Multi-class and Hierarchical Product Categorization for an E-commerce Giant \- ACL Anthology, [https://aclanthology.org/C16-1051.pdf](https://aclanthology.org/C16-1051.pdf)  
> 23. Query Brand Entity Linking in E-Commerce Search \- arXiv, [https://arxiv.org/pdf/2502.01555](https://arxiv.org/pdf/2502.01555)  
> 24. PatentSBERTa: A Deep NLP based Hybrid Model for Patent Distance and Classification using Augmented SBERT \- ResearchGate, [https://www.researchgate.net/publication/350311418\_PatentSBERTa\_A\_Deep\_NLP\_based\_Hybrid\_Model\_for\_Patent\_Distance\_and\_Classification\_using\_Augmented\_SBERT](https://www.researchgate.net/publication/350311418_PatentSBERTa_A_Deep_NLP_based_Hybrid_Model_for_Patent_Distance_and_Classification_using_Augmented_SBERT)  
> 25. PatentSBERTa: A Deep NLP based Hybrid Model for Patent Distance and Classification using Augmented SBERT \- arXiv, [https://arxiv.org/pdf/2103.11933](https://arxiv.org/pdf/2103.11933)  
> 26. PatentSBERTa: A Deep NLP based Hybrid Model for Patent Distance and Classification using Augmented SBERT \- IDEAS/RePEc, [https://ideas.repec.org/p/arx/papers/2103.11933.html](https://ideas.repec.org/p/arx/papers/2103.11933.html)  
> 27. Large Language Models for Patent Classification: Strengths, Trade-offs, and the Long Tail Effect \- arXiv, [https://arxiv.org/html/2601.23200v1](https://arxiv.org/html/2601.23200v1)  
> 28. AI-Growth-Lab/PatentSBERTa \- Hugging Face, [https://huggingface.co/AI-Growth-Lab/PatentSBERTa](https://huggingface.co/AI-Growth-Lab/PatentSBERTa)  
> 29. IPC prediction of patent documents using neural network with attention for hierarchical structure \- PMC, [https://pmc.ncbi.nlm.nih.gov/articles/PMC9980776/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9980776/)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAaCAYAAAC3g3x9AAABHElEQVR4XmNgGAWjgGywBIj/A3E2EPtC8Qwg/gzElUhiJ6DqCILLQJyHxGcB4llAfA6IFZDEbYD4CRIfK+AA4lA0MQsGiEaQ65CBDhDvRRPDAGpALI8mlsMA8Zo9mjiIvwFNjChwnAFiIMj1VAEg7xIV+MQAkKtAhp1Gl0ACNUDcxUCkDyQZIAYuRJeAAh8g1gViHiBeDsR8qNKYABQhrxkwIwQEQoD4DhJ/MhCvRuJjAJAXQC4DeVcKTQ4EmhlQDZzIAEmrOAHIVSDX5aNLQAHINegGIvPhQByINYF4GQMk/NqA2AuIxYCYFUndCgYiDSQWgHIOuoH4UgNB4AHEz5H4oPDGlRqIBoYMiFKpmgE1SMgGDgyQMB4FDAwALEoz686m4IcAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAaCAYAAAC+aNwHAAABHElEQVR4Xu2TMUtCYRSG37CmMnBsiXIIJ+kXVEPg3B/Q1dYQpDmCCKHayiFoiSAc2xR/gKOru0NjPyDfl3Pjfvfcq9dRwgeewe/9PPdwz7nAmtVmgzbpK/2gV8l4PiX6A/tjSJH+worN5ZD2aYtuuUwoUxF1l2IXFvZ8EHAO667uA1Vs0yk9S0YJjumEdnxwC3v6hQ8cp/SbPvlgBCuw5wOHWte9Gx/oUOYxgN078sGyBdS+7m36YJkCeoG6c+cDodGEBTTSE8Tz3qHvsCVSlqIBK1KlFVqOzt/ofpQNo7NMtHX3sE27DM4f6Jg+w1Y8l21agxXTqL7odZBr2Q6C37l8Im69QB+RMYFFdBFPSGZ9YAvRav9N6MVl/4UZ0LY5ImbqyCoAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADgAAAAZCAYAAABkdu2NAAACSElEQVR4Xu2XzYvNURjHH6HIazRshIWFsvGSYmwuKTVqZEGKJCthIdkgm7ETSSIppIw00ygiG1ZeMotRKEUWFspOyh/A9+N5js49c2c30j39PvXpnt9zfi/nOS+/37lmDQ0NDf+RqXKdfCivFnVV8EL+ylzWXt29HJE/5dw4fmye4Na/Z3Q5H+Tn7HjYPMGUcFezRX6R64t4FUyTV8xHbHZRVwUHzadilaMHt80TnF9W1MJ78wSrheRIskqYliR4p6yohRPykVxQVgSLbfznY7pcI5dkMVgkt8lZHeLlZmGK7DW/F78b2qv/fHu5V9kuzu+z8c/uyFL5Un6So/Kc7M/q0+fjmvmNgYaxlTskH8gdEacjbsid8pV5BwDJ3or4M3k34jR+RN6UB+S9iMN2813UHvP9cOKwfG5+r6Es3hEa/F0OyJY8bb5Ny/egP+SZOB9WW/tO57h5YuflWBa/JF+bN/RbFv8o95v3/jF5X143vwefqgTPuGA+8psi1jKfbbBZDkZ5QnrkKvMRScyQa81HEsvpcVZ+LWLAC4qGJvjskCC/b7I4DaeTElxHwiVPzTv4ndwYMTrxrfmM2yvnRHxSYRqx20nwt2qm+cgz5RJ0Qss8SRoGvMwux29qHFN2YZQT+8y3jXDSvJMYBK7Nd1k8e9I5Kp9kx4zybvN1kabYSvP1SaN4M1+MMv9UuD69rEiSUWed59AhK6LM9buizLpbHmVm2qko/xNYM+WelTU9r4gBcRoETPlUJumJRoHlgyU8k2c3VM9vlcBj+Uj3iNMAAAAASUVORK5CYII=>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACwAAAAZCAYAAABKM8wfAAACEElEQVR4Xu2Wz0uVQRSG37AgsSKSFEKLINwEQYogKHiRwEUQuGlVm3IRBGpQm8JN0EbcRPgDd4JuFFpEuRCihbqQaBUESlELoV0E/QH1vpyZmnvuFRS+Dya4DzxwZ87ce8/Md2bmAxo0aJAVTbSHvqKzLpYlm/R34oXqcD7cp7/oqdB+A0v42t8RmfGJfk7aq7CE4wSyYoh+o72uP0uO0hnYip5wsSy5A3v0/8XqikVYwqd9IFc+whI+LEfoJdriA2WjZJX0YXlP78IumPQk2YE9tVJQGSjhJR84AErsCj3j+vtpq+srjIf0NWr/NNKO2uNOYy/SFdgtqKs80kFPJm19Vp+4SoeTWOQYLBbH7ct5ukV36TadojeSeDzu5mE/GnlAX9A12HeOh/7r9Dldh01KR6TiKp2b9DadoINhvNDvbtBR2AJUklgVGviDPoUNegK7ltN3iJ90Moz3KLk+13cLVsuapCardhfdowNhjNr3wucK/R4+K59l2hnaNZyll2E7PaKV6oatityvTMQ4Pec7YaUz4vre4l9NKxYnOg1bJD3lOVSXUqHoz5WEp42+g008Ppl0RVXvKg/FH8PKSrdrRHuhOWkXhpKodwzqfeQr7F36UehLS0cb7gusFMZgq/0hxIQmoVovHJVDvRUWqsX01IgbMuLjQidRKe8w2hAv6QJ95mJZok2mG6zi+kvnD7S+UzNgGt3XAAAAAElFTkSuQmCC>

[image5]: <data:image/png;base64,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>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAXCAYAAAAyet74AAAAYUlEQVR4XmNgGAXDBPACcTMQ/8eBo0GKWIF4BxBrQ/QwKACxPZSNAgKBmA+Nr4DExwrEgHg/EDOiS6ADkJWv0QWxga1AfBldEBt4AMR70QWxAVBQJKELYgNmQMyMLjjAAADCMw+8bZc67gAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAXCAYAAABzjqNHAAAClUlEQVR4Xu2YzatOURTGH6EkJOJG1GWgyMBHbspASfkYKCZiYMDEQIlMxIhM7oiQMiKSMqIYkQFCGJgoIuUPMPEHsH7W3s5+103u7XY+dM+vnu7Ze5337dy1n73WPq/U09PT09NTI+dNPwsdHgxrreljimXdHbijR3NMQ6a38gQ9MM0r4tNNi0zvTJ9Ny+WfaZMzpgVxsgvcNO2WJ/JqiMFz0+Y42SIs/DfTLdO0EGuFGaZjcgeSxA+D4d88NS2Oky2DG3HlfdPGEGscHLYkXT+TJ7JM2CzToWLcRXjG96ZXppkh1ggkCDfCKXkS91ZhLVW3tvLfIHk8N8k8GGK1QvKuF+PV8u18W766sNW08M8d3WeXvPwcUfU/1AoOexLmtsndeEH+EDSdyXJAzWwzmswd01c12MHZyqUTITeYN6ZheWeeDNRXFqpuN4/Im8wJ09wQqxVsz3aNkEASedF0OcS6BO6mmbTWUACH5M5cwlYmid81tjNzRstbZYtpR7rmYM5Zc1kaA/dtL8bcQwnhL1uP+1cV8YlA86CJUAP5vlag3h2PkwkaDofuuA1JKDXzh2k0za0zPVb1NnMvzfP9K0w7TZvS3Dn5GxDNa0Oau6SJvQV9kte9Vg/ZrNoe+YO8Nu1PcxGSxVYuH/ak3Ik4YGWaoxyQKMDVL9M1jmSLsRj5VXKf/MjEIZnvzY1rdoqPBxbmv4cknE7XOQnZSZQB6mwG58Y3INw/nK45132pQlMHnJfrXOk8IIEk8qzciZw3STKJW6OxzsOl/OhBfaO+TgnY9tdUHWKPyjt55qHphtytQMlA1EugNpbOvGJ6ZFpfzP0LStB49EJekjpJ2QSoeeVPZ4zLRkTS43h+MaYuNnYo7ukQvwA1H2vWiG7dEwAAAABJRU5ErkJggg==>