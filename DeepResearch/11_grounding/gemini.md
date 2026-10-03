# **切り出された単一物体の語彙非依存型認識と意味的紐付けに関する深層調査報告書**

## **1\. 仕組みの分類：切り出された物体を名前に結びつけるアーキテクチャの型**

画像内に単独で存在する（位置が自明な）物体を入力とし、それを意味や名前に結びつける認識プロセスの工夫について、コンピュータビジョンのトップ会議における最新の研究を6つの型に分類して詳述する。本節では、各手法の入力、判断の信号、学習の要否、およびその内部メカニズムを明らかにする。

### **1.1 部分と全体の関係を使う（部位の動的抽出と構造的照合）**

物体全体のマクロな特徴だけでなく、識別に寄与する局所的な部位（パーツ）を抽出し、それらを組み合わせて最終的な判断を下すアプローチである。この型は、細粒度画像認識（Fine-Grained Visual Classification: FGVC）において主流となっている。

* **代表的研究**: TransFG (AAAI 2022\)1、Deformable ProtoPNet (CVPR 2022\)4  
* **入力**: 切り出し済みの単一物体画像。  
* **判断の信号**:  
  * TransFG: Transformerの自己注意（Self-Attention）マップから算出される局所パッチのアテンション重みと、それに基づく分類トークンとの対比。  
  * Deformable ProtoPNet: 事前学習された局所プロトタイプ（部位の原型）と、入力画像から動的に位置合わせされたパッチとの潜在空間におけるL2距離。  
* **学習の要否**: いずれも要（閉鎖語彙に対する事後学習を前提とする）。  
* **メカニズムの詳細**:  
  * **TransFG**は、Vision Transformer (ViT) の自己注意機構を応用し、画像パッチ間の関係性を計算する。Part Selection Module (PSM) と呼ばれる機構を通じ、すべてのアテンションヘッドから生の重みを統合してアテンションマップを生成し、最も重みの大きい（識別に重要と判断された）パッチトークンを動的に選択する1。これら選択された局所トークンと、画像全体を表現するグローバルトークンを結合（Concatenate）し、最終層で統合的な判断を下す。さらに、類似するサブクラス間の特徴表現の距離を広げるために対照学習（Contrastive Loss）を適用している1。  
  * **Deformable ProtoPNet**は、「この入力画像のこの部分は、学習したプロトタイプのこの部分に似ている」という事例ベースの推論を行う4。特筆すべきは、プロトタイプと照合する際、入力画像に応じて照合位置の空間的オフセットを動的に計算（Deformable Convolutionの応用）し、プロトタイプ側に空間的な柔軟性を持たせている点である4。

### **1.2 属性・記述を経由する（概念ボトルネックとプロンプト生成）**

画像を直接クラス名にマッピングするのではなく、「色」「形」「素材」などの属性（概念）の有無や、自然言語による詳細な視覚的記述を中間表現として経由する手法である。

* **代表的研究**: Label-free CBM (ICLR 2023\)7、CuPL (ICCV 2023\)10  
* **入力**: 切り出し済みの単一物体画像。  
* **判断の信号**:  
  * Label-free CBM: 画像特徴と、LLMが生成した属性概念群のテキスト埋め込みとのコサイン類似度に基づく活性値。  
  * CuPL: 画像特徴と、LLMが事前生成した「対象の詳細な視覚的記述」のテキスト埋め込みとのコサイン類似度。  
* **学習の要否**:  
  * Label-free CBM: 要（概念の正解ラベルは不要だが、最終層の重みの学習が必要）。  
  * CuPL: 不要（凍結された視覚言語モデルを使用）。  
* **メカニズムの詳細**:  
  * **Label-free CBM**は、GPT-3などのLLMを用いてカテゴリごとの属性（概念）リストを自動生成し、CLIPを用いて画像からそれら概念の活性値を計算するコンセプトボトルネックモデルである9。最終的な認識は、これら概念の活性状況に対する疎（スパース）な線形結合によって行われる。高価な概念アノテーションを不要にしつつ、解釈性を担保している7。  
  * **CuPL (Customized Prompts via Language models)** は、従来の「～の写真」という単純なプロンプトの代わりに、LLMに対して「カモノハシはどのような見た目か？」と問いかけ、「ビーバーのような尾を持ち、アヒルのような嘴を持つ」といった詳細な記述を多数生成させる10。これらをテキスト特徴量として平均化し、入力画像との類似度を測ることで、外形以外の細かい手掛かりを言語モデルの知識から引き出し、ゼロショット分類の精度を向上させる11。

### **1.3 外部知識・検索を使う（検索拡張型語彙非依存認識）**

固定の語彙リスト（候補リスト）を持たず、入力画像の特徴をクエリとして外部の大規模データベースを検索し、そこから候補となる名前を動的に抽出して最終決定を下す手法である。

* **代表的研究**: CaSED (NeurIPS 2023\)13、E-FineR (ICCV 2025 / arXiv 2025\)15  
* **入力**: 切り出し済みの単一物体画像。  
* **判断の信号**:  
  * CaSED: 外部データベースから検索されたキャプション内の名詞群と、入力画像とのマルチモーダル類似度スコア。  
  * E-FineR: 未ラベル画像群から抽出した候補名に対し、VLMを用いて生成した豊かな文脈的記述と、視覚特徴の結合表現における類似度。  
* **学習の要否**: 両者とも不要（完全な推論時処理）。  
* **メカニズムの詳細**:  
  * **CaSED (Category Search from External Databases)** は、語彙非依存（Vocabulary-free）の代表的アプローチである。入力画像のCLIP埋め込みを用いて、外部の巨大な視覚言語データベース（PMDなど）から類似するキャプションを検索する13。検索された文から自然言語処理によって候補となる名詞（カテゴリ名）を抽出し、動的な候補リストを構築する。最後に、元の画像と各候補カテゴリを再度CLIPでスコアリングし、最もマッチする名前を出力する13。  
  * **E-FineR** は、外部検索に加え、VLMを用いて対象の視覚的文脈を豊かにする記述（Enriched Context）を自動生成し、視覚とテキストの埋め込みを結合することで、より精緻な細粒度認識を学習なしで実現している16。

### **1.4 比較で決める（微細な差異の最適輸送によるアライメント）**

紛らわしい候補や、画像内の局所領域とテキスト概念の対応関係を「比較」および「最適輸送」の観点から厳密に最適化して決定する手法である。

* **代表的研究**: DOT-CBM (CVPR 2025\)17  
* **入力**: 切り出し済みの単一物体画像。  
* **判断の信号**: 画像の局所パッチとテキスト概念間の最適輸送（Optimal Transport）コストから導出される細粒度アライメントスコア。  
* **学習の要否**: 要。  
* **メカニズムの詳細**:  
  * **DOT-CBM (Disentangled Optimal Transport CBM)** は、画像全体を単一のベクトルとして扱う従来型CBMの欠点を克服するため、局所的な画像パッチ群とテキスト概念群の間の対応付けを「最適輸送問題」として定式化する17。これにより、「鳥の頭」という概念が背景のパッチと結びつくような偽の相関（Spurious correlation）を排除し、パッチと概念間の厳密な比較と紐付けを行う17。

### **1.5 段階を踏む（階層的・粗密推論）**

まず大まかな分類（粗いカテゴリ）を特定し、その後、より詳細な名前に降りていく、あるいはその両方を同時に最適化する階層的なアプローチである。

* **代表的研究**: HIL-CBM (NeurIPS 2024\)19  
* **入力**: 切り出し済みの単一物体画像。  
* **判断の信号**: 階層化された二つの分類ヘッド（抽象度の高い概念と具体的な概念）からの出力ロジットと、階層間の視覚的一貫性ロス。  
* **学習の要否**: 要。  
* **メカニズムの詳細**:  
  * **HIL-CBM**は、人間の認知プロセスを模倣し、概念ボトルネックを階層化している。上位レベルで全体的な特徴（例：一般的な体型）を捉え、下位レベルで微細な特徴（例：特定の部位の形状）を捉える20。特徴的なのは、高レベルと低レベルの概念間に明示的な関係ラベルを与えなくても、勾配ベースの視覚的一貫性ロス（Visual Consistency Loss）を用いて、両者が画像の同じ空間領域に注目するように制約をかけ、段階的な推論を実現している点である19。

### **1.6 機能・用途から推論する（アフォーダンスと文脈抽出）**

対象が何であるかを純粋な外見形状だけでなく、「それがどう使えるか（アフォーダンス）」や「どのような文脈で存在するか」という観点から結びつけるアプローチである。

* **代表的研究**: 認知科学におけるアフォーダンス理論22、およびそれを応用したVLMプロンプティング。  
* **入力**: 切り出し済みの単一物体画像。  
* **判断の信号**: 画像内の形状から推測される物理的な相互作用の可能性や用途の言語化表現。  
* **学習の要否**: 凍結されたVLMのプロンプトエンジニアリングの場合は不要。  
* **メカニズムの詳細**:  
  * 現代のVLMは、対象の明示的な名前が不明な場合でも、「この物体はどのような目的で使用されるか？」と問うことで機能を言語化できる。前述のCuPL10 のような属性抽出アプローチを機能面に拡張することで、「液体を注ぐための筒状の部品」といった機能的記述を中間表現とし、未知の道具などの名称を推論することが可能である。

## **2\. 上位カテゴリや語彙が与えられない設定における認識メカニズム**

ユーザの設定である「上位カテゴリが分からない」「質問文がない（語彙リストがない）」という制約下での認識メカニズムについて分析する。

### **2.1 語彙を与えない認識・命名 (Vocabulary-free Image Classification)**

従来のゼロショット学習では、推論時に「犬、猫、鳥…」といった候補となる語彙リスト（Vocabulary）を与える必要があった。しかし、**CaSED**13 や **E-FineR**15 は、この語彙リストを一切必要としない（Vocabulary-free）。 CaSEDは、画像をクエリとして数億規模の外部画像・テキストペアデータベース（LAIONやPMD）を検索し、意味的に類似するテキストの中から名詞を抽出して動的に候補リストを生成する13。**これらの手法は、上位カテゴリ（例：「これは動物である」）を一切前提としていない**。対象が世界に存在するあらゆる概念（数百万規模）のどれであるかを、外部知識の海から直接引き上げるアプローチをとっている23。

### **2.2 オープン語彙の認識における切り出し後の照合プロセス**

オープン語彙認識（Open-Vocabulary Recognition）において、物体領域が切り出された後の分類は、主にCLIPなどの大規模な視覚言語事前学習モデル（VLM）の潜在空間における「テキスト埋め込み」との照合によって行われる。Contiら（ICCV 2025）の研究25 が示すように、LMM（Large Multimodal Models）は「画像内の主要なオブジェクトは何ですか？」というオープンエンドなプロンプトに対し、直接自然言語で回答を生成できる。ここでは、固定の語彙と照合するのではなく、モデル内部に蓄積されたパラメトリックな知識ベース（重み）と照合して名前を生成している。これも上位カテゴリを前提としない。

### **2.3 未知カテゴリ・長尾（Long-tail）の命名**

事前学習データにほとんど現れない珍しい対象（長尾分布に属する物体）の命名は、視覚的なショートカット（背景など）に依存しやすいという問題がある27。これを克服するため、**CuPL**11 はLLMの広範なテキスト知識を活用し、珍しいカテゴリに関する「詳細な記述」を生成して照合に用いる。また、**FG-BMK**（arXiv 2025）29 などの最新のベンチマーク研究では、VLMが未知・長尾のカテゴリに対して、視覚的な外観の知覚能力は高いものの、それを正確なカテゴリ名に結びつける「推論能力」に課題があることが示されている30。上位カテゴリがない場合、この傾向はさらに顕著になる。

## **3\. 手がかりの在り処が一定でない場合の扱いに対する回答**

「全体の輪郭で決まるものと、面の内側の小さな部分で決まるものが混在する」というユーザの課題に対し、3つの問いに直接回答する。

### **Q1: 識別に効く部位が対象ごとに違うことを扱った研究があるか？**

**回答：存在する。**

* **TransFG**1 では、対象オブジェクトのどの部分が識別に重要であるかが画像ごとに異なる問題に直接対処している。自己注意（Self-Attention）機構を利用し、固定の空間グリッドではなく「その入力画像において最もアテンション重みの高いパッチ」を動的に選択することで、対象ごとの識別に効く部位（ある鳥ではくちばし、ある車ではヘッドライトなど）を特定している。  
* **Deformable ProtoPNet**4 では、照合すべきプロトタイプ（原型パーツ）の相対的な空間位置を、入力画像の特徴に応じて動的に変化（オフセットを学習）させている。これにより、対象ごとにパーツの配置やスケールが異なっていても柔軟に照合できる。

### **Q2: 全体の形と局所の特徴をどう統合しているか？**

**回答：局所特徴を動的に抽出し、大域特徴（全体の形）と結合（Concatenate）、あるいは最適輸送によって統合するアプローチが主流である。**

* **結合（Concatenation）による統合**: TransFGでは、局所の微細な手がかりを持つパッチ群（局所特徴）を選択した後、それらを画像全体を表す分類用トークン（グローバルトークン：大域特徴）と連結し、最終のTransformer層に入力して統合判断を下す1。これにより、全体の輪郭情報と局所の詳細情報を並行して評価している。  
* **最適輸送による統合（確率的マッピング）**: DOT-CBM18 では、画像全体の粗い特徴から概念を予測する従来手法の欠点を克服するため、局所パッチ群とテキスト概念群の間の対応付けを「最適輸送行列」を用いて統合している。これにより、全体と局所の情報を確率的なマッピングとして混ぜ合わせている17。  
* **階層的な統合**: HIL-CBM20 は、上位層で大域的な抽象特徴を、下位層で局所的な具体特徴を処理し、両者間の視覚的一貫性ロスを用いて階層的に統合している。

### **Q3: 統合の重みを入力ごとに変える仕組みがあるか？あるなら、重みを何から決めているか？**

**回答：存在する。主に「自己注意のスコア」または「テキストを条件としたクエリ」から、入力画像ごとに動的に決定している。**

* **自己注意からの決定**: TransFGをはじめとするViTベースの手法では、入力画像そのもののパッチ間の類似度（クエリとキーの内積）からアテンション重みが計算されるため、画像が入力されるたびに、どの局所パッチを重視するかの重みが動的に変化する6。  
* **テキスト条件からの決定**: FLAIR（CVPR 2025）32 は、大域特徴と局所特徴を統合する際、テキスト特徴（例：「長い耳」などの詳細な記述）をクエリとして用い、画像内の局所パッチに対する「テキスト条件付きアテンションプーリング」を行う。これにより、何の物体を探そうとしているか（またはどんな属性が記述されているか）という言語的文脈に基づいて、画像ごとの局所特徴の統合重みが決定される32。

## **4\. 輪郭だけでは決まらない対象の扱い**

外形が単純な箱状の機器や筒状の部品など、形だけでは種類が決まらない対象を認識するためには、スケール、素材、文脈、機能といった画像に写りにくい情報を補完する仕組みが必要である。これについては以下の手法が対応している。

> 1. **詳細な視覚的属性（素材・テクスチャ・色）の言語化**: 輪郭が同じでも素材が異なる（例：金属の箱とプラスチックの箱）場合、**CuPL**10 や **Label-free CBM**12 のような属性抽出アプローチが有効である。これらはLLMを用いて「木目でできている」「光沢のある表面を持つ」といった詳細な属性プロンプトを事前に生成し、CLIPのテキストエンコーダを通じて画像のテクスチャ特徴と照合する。輪郭の形状特徴に依存せず、表面の微細なテクスチャや色空間の特徴を言語ベクトルとして引き出すことができる。  
> 2. **外部文脈の検索拡張（RAG的アプローチ）**: **CaSED**13 は、輪郭だけでは名前が特定できない対象に対し、外部データベース（画像とキャプションの巨大ペア）を検索する。検索された類似画像のキャプションには、その物体が置かれている「文脈」や「用途」が含まれていることが多い。例えば、単なる筒状の部品の画像であっても、DB上で似た画像が「配管工事に使われる塩ビパイプ」というキャプションを持っていれば、形状以外の知識（用途・文脈）を借りて名前を推論することが可能になる。  
> 3. **VLMによる機能的・推論的記述の生成**: **E-FineR**16 は、画像から直接クラス名を当てるのではなく、VLMに対して「この対象の特徴や文脈を詳細に記述せよ」と指示を出す。VLMは事前学習で得た知識から、対象の質感や潜在的な機能を言語化し、これをリッチなテキスト表現（Enriched Context）として扱うことで、単純な外形以外の情報を補い、分類精度を向上させている。

## **5\. 評価手法とデータセットの性質**

「切り出された物体の語彙非依存型認識」において、従来のような固定のラベルリストが存在しない場合、評価方法は非常に複雑化している。

### **5.1 認識の採点方法**

> 1. **文字列の包含・完全一致 (Text Inclusion)**: 予測されたテキストの中に、正解ラベルの文字列が含まれているかを単純に判定する。LMMの自由記述回答の評価に用いられる26。  
> 2. **埋め込みの類似度 (Semantic Similarity / Semantic IoU)**: 予測された名前と正解ラベルをSentence-BERT等の言語モデルで埋め込み、そのコサイン類似度や意味的IoUを計測する。これにより、「dog」と「hound」のような同義語や、粒度の違いを許容した評価が可能になる13。  
> 3. **大規模言語モデルによる判定 (LLM-as-a-judge)**: 最新の研究（Conti et al., ICCV 202526）では、Llama 3などのLLMに正解クラスと予測クラスを入力し、「この予測は正解クラスと同じ物体を指しているか、あるいはその下位分類か？」を質問して正誤判定を行わせる手法（Llama inclusion）が提案されている。オープン語彙環境ではこれが最も人間の評価に近いとされる。

### **5.2 使用されるデータセットの性質**

単一物体・細粒度分類の評価には、以下のデータセットが頻繁に用いられる。

* **CUB-200-2011**, **Stanford Cars**, **FGVC-Aircraft**: これらは対象が画面の中心に大きく写っており（ユーザーの設定に合致）、輪郭だけでなく微細なパーツ（くちばしの色、ヘッドライトの形状など）を見なければ識別できない性質を持つ。対象の種類は数百規模であり、ラベルの粒度は極めて細かい1。  
* **FG-BMK** (arXiv 2025): 101万件の質問と28万枚の画像を含む、VLMの細粒度視覚タスクに特化した巨大ベンチマーク29。単なる認識精度だけでなく、属性認識や知識バイアスなどを対話形式（ヒューマンオリエンテッド）および表現レベル（マシンオリエンテッド）で評価する30。

## **6\. 抽出された研究文献の詳細情報および一覧表**

本調査で抽出した主要論文のメタデータと、各手法の入力・出力・学習要否の対応関係を以下の表に集約する。これらの研究は、位置決め（物体検出）を主目的とせず、単一物体の認識・命名に特化した部分を評価の対象としている。

| 論文名 (略称) | 著者 / 会議・年 / arXiv | 査読 | 入力(切出済) | 上位カテゴリ前提 | 語彙の前提 | 判断の信号 | 学習要否 | 評価方法 | 実装URL (または有無) |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **CaSED** | A. Conti et al. NeurIPS 2023 arXiv:2306.0091713 | 有 | はい | なし | なし (Vocab-free) | CLIP類似度 (外部DB検索経由) | 不要 | 正解一致率, 意味的IoU, クラスタ精度 | [公開](https://github.com/altndrr/vic?utm_source=gemini) |
| **CuPL** | S. Pratt et al. ICCV 2023 arXiv:2209.0332010 | 有 | はい | なし | あり (Closed) | LLM生成記述とのCLIP類似度 | 不要 | 正解一致率 (Top-1 Accuracy) | [公開](https://github.com/sarahpratt/CuPL?utm_source=gemini) |
| **Label-free CBM** | T. Oikarinen et al. ICLR 2023 arXiv:2304.061297 | 有 | はい | なし | あり (Closed) | 概念活性値の線形結合 | 要 (最終層) | 正解一致率, 人手評価 (解釈性) | [公開](https://github.com/Trustworthy-ML-Lab/Label-free-CBM?utm_source=gemini) |
| **TransFG** | J. He et al. AAAI 2022 arXiv:2103.079761 | 有 | はい | あり (特定ドメイン) | あり (Closed) | Attention重み \+ 大域トークン | 要 (事後学習) | 正解一致率 (Top-1 Accuracy) | [公開](https://github.com/TACJu/TransFG?utm_source=gemini) |
| **E-FineR** | D. Demidov et al. ICCV 2025 arXiv:2507.2307015 | 有 | はい | なし | なし (Vocab-free) | 視覚・言語結合特徴の類似度 | 不要 | 正解一致率 (Top-1/Top-5) | [公開](https://github.com/demidovd98/e-finer?utm_source=gemini) |
| **Conti et al. (OWC)** | A. Conti et al. ICCV 2025 arXiv:2503.2185126 | 有 | はい | なし | なし (Open-World) | LMM生成テキスト | 不要 | LLM判定(Llama), 意味的類似度 | [公開](https://github.com/altndrr/lmms-owc?utm_source=gemini) |
| **DOT-CBM** | X. Xie et al. CVPR 2025 (arXiv未確認)17 | 有 | はい | なし | あり (Closed) | 最適輸送コスト (パッチ⇔概念) | 要 (事後学習) | 正解一致率, 解釈性(ヒートマップ) | 補足資料内 |
| **HIL-CBM** | M. K. B. C. et al. NeurIPS 2024 arXiv:2604.0246819 | 有 | はい | なし | あり (Closed) | 階層的ロジット \+ 一貫性ロス | 要 (事後学習) | 正解一致率, 概念予測精度 | 未確認 |
| **Deformable ProtoPNet** | J. Donnelly et al. CVPR 2022 (arXiv未確認)4 | 有 | はい | あり (特定ドメイン) | あり (Closed) | 動的プロトタイプとのL2距離 | 要 (事後学習) | 正解一致率 | 未確認 |
| **FLAIR** | R. Xiao et al. CVPR 2025 (arXiv未確認)32 | 有 | はい | なし | あり (Open-Vocab) | テキスト条件付Attention Pooling | 要 (事前学習) | 検索R@1, セグメンテーションmIoU | 未確認 |

*(注: 「上位カテゴリの前提」について、TransFGやDeformable ProtoPNetは鳥や車などの特定ドメインデータセットで学習・評価を行うため「あり」とした。CaSEDやE-FineRは任意の画像に対して推論を行うため「なし」である。)*

## **7\. 転用候補5件とその具体策**

ユーザの「上位カテゴリ不明」「質問文なし」「画面全体に1つの対象」「珍しい対象を含む」「VLMの凍結または事後学習」という設定に対し、そのまま動くか、またはどう改変すれば動くかを5件提案する。

### **候補1: CaSED (Category Search from External Databases)**

13

* **概要**: 画像からCLIP特徴を抽出し、外部の巨大キャプションデータベースを検索して候補単語を抽出し、再度CLIPでスコアリングして名前を決める手法。  
* **そのまま動くか**: **完全にそのまま動く**。語彙リストも上位カテゴリも不要であり、凍結VLMを使用するため学習も不要である。珍しい対象も、外部データベース（LAIONやPMDなど）に存在すれば検索・特定可能である。  
* **変える必要がある部分**: 汎用データベースを用いると「背景の風景」や「抽象的な概念」を名詞として拾うリスクがある。転用する際は、検索用データベースを「物体の名前や機能が記載された図鑑や工業部品のカタログ、ECサイトの商品説明」などに意図的に絞り込む（フィルタリングする）ことで、純粋な「物体名」の推論精度が劇的に向上する。

### **候補2: E-FineR (Enriched Contextually Grounded Vision-Language Model)**

15

* **概要**: VLMを用いて対象の詳細な視覚的文脈を生成し、それらと視覚特徴を結合して分類する語彙非依存の手法。  
* **そのまま動くか**: 動く。訓練不要・語彙非依存であり、微細な違い（手がかりの在り処が違う対象）にも対応可能である。  
* **変える必要がある部分**: 元の論文では未ラベル画像群から何らかの形でクラス候補を抽出する前提がある。完全に質問文も候補もない設定の場合、画像を入力して強力なLMM（GPT-4Vなど）に「考えられる具体的な候補名10個とその詳細な視覚的属性」を生成させ、それらをCLIPのテキストエンコーダにかけて画像自身の埋め込みと照合する**自己生成型・自己検証型のパイプライン**に改変すると良い。

### **候補3: Label-free CBM (Concept Bottleneck Models)**

7

* **概要**: LLMを用いて属性（概念）を自動生成し、CLIPを用いて画像から属性を抽出し、その組み合わせの線形結合で名前を決定する。  
* **そのまま動くか**: そのままでは動かない。元の手法は最終層の分類器を特定の語彙セットに対して学習させる必要があるため、語彙非依存の要件を満たさない。  
* **変える必要がある部分**: 最終層の線形分類器を取り払い、**「画像から抽出された属性のベクトル」と「辞書・Wikipedia等からLLMに抽出させた全対象物の属性ベクトル」とのコサイン類似度マッチング**に変更する。これにより、上位カテゴリ不明かつ珍しい対象であっても、「金属製、筒状、ネジ山がある」といった属性群の合致度プロファイルから対象を特定するオープンエンドなアーキテクチャに変換できる。

### **候補4: FLAIR (Fine-grained Language-informed Image Representations)**

32

* **概要**: テキスト特徴をクエリとして用い、画像内の局所パッチに対する「テキスト条件付きアテンションプーリング」を行う手法。  
* **そのまま動くか**: 動かない。推論時に「対象を絞り込むためのテキストクエリ」を必要とするため、「質問文なし」の要件に反する。  
* **変える必要がある部分**: 2段階の推論パイプラインを構築する。まず、汎用VLMを用いて画像から大まかな構造的特徴や属性をテキストとして抽出する。次に、その**抽出されたテキスト群を自律的なクエリとしてFLAIRにフィードバック入力**し、局所特徴のプーリング重みを動的に決定させる。これにより、外部からの質問文なしで、モデル自身が注目すべき局所パーツを決定しながら認識を深めることが可能になる。

### **候補5: TransFG (Part Selection Module搭載 Transformer)**

1

* **概要**: ViTのアテンションマップを用いて、識別に有用な局所パッチを動的に選択・統合する手法。手がかりの在り処が対象ごとに違う問題に極めて強い。  
* **そのまま動くか**: 動かない。固定クラスに対する教師あり分類ヘッドを前提としているため、上位カテゴリ不明・語彙非依存の要件を満たさない。  
* **変える必要がある部分**: 事後学習が可能な設定を活かす。TransFGの分類ヘッド（Linear層）を破棄し、**出力をCLIPの画像エンコーダの潜在空間（テキスト埋め込み空間）に射影する**ように、対照学習（Contrastive Learning）を用いてファインチューニングする。これにより、「局所の重要なパーツを強調した視覚表現」を任意のテキスト（名前）と直接比較可能なオープン語彙の埋め込み空間に昇華できる。

## **8\. 着想の源泉となる理論とアプローチ**

実用的なディープラーニングの実装とは別に、本課題を解決するための根源的なアイデアとなり得る認知科学や古典的アプローチを提示する。これらの知見は、新たなネットワーク構造やプロンプト設計の着想に結びつく。

* **Recognition-by-Components (RBC) / Geon理論 (Biederman, 1987\)**  
  \[cite: 35, 36, 37\]  
  * **概要**: 人間は物体を認識する際、それを「Geon（円柱、ブロック、円錐などの3次元の基本幾何学部品）」の組み合わせとして分解しているという認知心理学の古典的理論である。Geonは約36種類しかなく、これらを「どう接合しているか（空間的構造関係）」で無数の物体を表現する35。  
  * **着想のポイント**: 輪郭だけで決まらない未知の対象や珍しい部品（筒状の部品など）に直面した際、現代のニューラルネットワークはテクスチャなどの表面的な「ショートカット」に依存しがちである27。しかし、RBC理論の「基本パーツへの分解と構造的関係の抽出」という概念をプロンプトとしてVLMに与える（例：「この物体を基本的な3D幾何学形状の組み合わせとして記述せよ」）ことで、表面のテクスチャや背景に惑わされず、物体の本質的な立体構造に基づいた強靭なオープン語彙認識が可能になる。  
* **Spotting the Difference (差異の発見) アプローチ / Finer-CAM (CVPR 2025\)**  
  \[cite: 38, 39\]  
  * **概要**: 細粒度の視覚的説明において、「比較強度」を調整することで、大まかな輪郭に注目するか、微細で識別的なディテールに注目するかを切り替える手法である38。  
  * **着想のポイント**: 上位カテゴリが不明な状況では、最初はマクロな輪郭（全体像）で検索範囲を絞り、候補がいくつか挙がった段階で、モデル自身のAttentionの焦点をミクロ（局所的な差異）に動的に切り替える「ズームイン推論（Coarse-to-Fine）」のアーキテクチャ設計に直結する。  
* **アフォーダンス理論 (Gibson, 1977\)**  
  \[cite: 22\]  
  * **概要**: 環境が動物に対して提供する「意味や価値」こそが知覚の対象であるとする理論。物体を「それが何であるか」ではなく「それがどう使えるか」で認識する。  
  * **着想のポイント**: 工業部品や未知の工具を命名する際、外見の一致よりも「穴が空いているから何かを通すものだ」「尖っているから削るものだ」というアフォーダンス的推論をVLMの中間出力として強制することで、機能名（例：カッター、ジョイント）を導出するブレークスルーとなる。

#### **引用文献**

> 1. TransFG: A Transformer Architecture for Fine-grained Recognition, [https://www.researchgate.net/publication/350087413\_TransFG\_A\_Transformer\_Architecture\_for\_Fine-grained\_Recognition](https://www.researchgate.net/publication/350087413_TransFG_A_Transformer_Architecture_for_Fine-grained_Recognition)  
> 2. TransFG: A Transformer Architecture for Fine-Grained Recognition, [https://cdn.aaai.org/ojs/19967/19967-13-23980-1-2-20220628.pdf](https://cdn.aaai.org/ojs/19967/19967-13-23980-1-2-20220628.pdf)  
> 3. TransFG: A Transformer Architecture for Fine-grained Recognition, [https://arxiv.org/abs/2103.07976](https://arxiv.org/abs/2103.07976)  
> 4. Deformable ProtoPNet: An Interpretable Image Classifier Using, [https://www.computer.org/csdl/proceedings-article/cvpr/2022/694600k0255/1H1itlIWCwo](https://www.computer.org/csdl/proceedings-article/cvpr/2022/694600k0255/1H1itlIWCwo)  
> 5. An Interpretable Image Classifier Using Deformable Prototypes \- arXiv, [https://arxiv.org/html/2111.15000v3](https://arxiv.org/html/2111.15000v3)  
> 6. TransFG: A Transformer Architecture for Fine-grained Recognition, [https://www.alphaxiv.org/abs/2103.07976](https://www.alphaxiv.org/abs/2103.07976)  
> 7. Label-free Concept Bottleneck Models for ICLR 2023 \- IBM Research, [https://research.ibm.com/publications/label-free-concept-bottleneck-models](https://research.ibm.com/publications/label-free-concept-bottleneck-models)  
> 8. Label-Free Concept Bottleneck Models \- Emergent Mind, [https://api.emergentmind.com/papers/2304.06129](https://api.emergentmind.com/papers/2304.06129)  
> 9. Label-Free Concept Bottleneck Models \[Quick Review\] \- Liner, [https://liner.com/review/labelfree-concept-bottleneck-models](https://liner.com/review/labelfree-concept-bottleneck-models)  
> 10. CuPL: Custom Prompts for Image Class. | PDF \- Scribd, [https://www.scribd.com/document/842576537/Pratt-What-Does-a-Platypus-Look-Like-Generating-Customized-Prompts-for-ICCV-2023-Paper](https://www.scribd.com/document/842576537/Pratt-What-Does-a-Platypus-Look-Like-Generating-Customized-Prompts-for-ICCV-2023-Paper)  
> 11. What does a platypus look like? Generating customized prompts for, [https://arxiv.org/abs/2209.03320](https://arxiv.org/abs/2209.03320)  
> 12. Label-Free Concept Bottleneck Models \- alphaXiv, [https://www.alphaxiv.org/abs/2304.06129](https://www.alphaxiv.org/abs/2304.06129)  
> 13. Vocabulary-free Image Classification, [https://papers.neurips.cc/paper\_files/paper/2023/file/619cbddb92b8c6fecaf2b86463153be9-Paper-Conference.pdf](https://papers.neurips.cc/paper_files/paper/2023/file/619cbddb92b8c6fecaf2b86463153be9-Paper-Conference.pdf)  
> 14. Vocabulary-free Image Classification and Semantic Segmentation, [https://alessandroconti.me/papers/2404.10864.html](https://alessandroconti.me/papers/2404.10864.html)  
> 15. Vocabulary-free Fine-grained Visual Recognition via ... \- arXiv, [https://arxiv.org/pdf/2507.23070?](https://arxiv.org/pdf/2507.23070)  
> 16. E-FineR: Vocabulary-free Fine-grained Visual Recognition \- GitHub, [https://github.com/demidovd98/e-finer](https://github.com/demidovd98/e-finer)  
> 17. CVPR Poster Discovering Fine-Grained Visual-Concept Relations, [https://cvpr.thecvf.com/virtual/2025/poster/33751](https://cvpr.thecvf.com/virtual/2025/poster/33751)  
> 18. Discovering Fine-Grained Visual-Concept Relations by, [https://openaccess.thecvf.com/content/CVPR2025/papers/Xie\_Discovering\_Fine-Grained\_Visual-Concept\_Relations\_by\_Disentangled\_Optimal\_Transport\_Concept\_Bottleneck\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Xie_Discovering_Fine-Grained_Visual-Concept_Relations_by_Disentangled_Optimal_Transport_Concept_Bottleneck_CVPR_2025_paper.pdf)  
> 19. Hierarchical, Interpretable, Label-Free Concept Bottleneck Model, [https://arxiv.org/abs/2604.02468](https://arxiv.org/abs/2604.02468)  
> 20. Hierarchical, Interpretable, Label-Free Concept Bottleneck Model, [https://arxiv.org/pdf/2604.02468](https://arxiv.org/pdf/2604.02468)  
> 21. Hierarchical, Interpretable, Label-Free Concept Bottleneck Model, [https://arxiv.org/html/2604.02468v1](https://arxiv.org/html/2604.02468v1)  
> 22. MET:Affordance Theory \- UBC Wiki, [https://wiki.ubc.ca/MET:Affordance\_Theory](https://wiki.ubc.ca/MET:Affordance_Theory)  
> 23. Vocabulary-free Image Classification \- Alessandro Conti, [https://alessandroconti.me/papers/2306.00917.html](https://alessandroconti.me/papers/2306.00917.html)  
> 24. \[2306.00917\] Vocabulary-free Image Classification \- arXiv, [https://arxiv.org/abs/2306.00917](https://arxiv.org/abs/2306.00917)  
> 25. ICCV 2025 Open Access Repository, [https://www.openaccess.thecvf.com/content/ICCV2025/html/Conti\_On\_Large\_Multimodal\_Models\_as\_Open-World\_Image\_Classifiers\_ICCV\_2025\_paper.html](https://www.openaccess.thecvf.com/content/ICCV2025/html/Conti_On_Large_Multimodal_Models_as_Open-World_Image_Classifiers_ICCV_2025_paper.html)  
> 26. On Large Multimodal Models as Open-World Image Classifiers, [https://openaccess.thecvf.com/content/ICCV2025/papers/Conti\_On\_Large\_Multimodal\_Models\_as\_Open-World\_Image\_Classifiers\_ICCV\_2025\_paper.pdf](https://openaccess.thecvf.com/content/ICCV2025/papers/Conti_On_Large_Multimodal_Models_as_Open-World_Image_Classifiers_ICCV_2025_paper.pdf)  
> 27. Discover and Cure: Concept-aware Mitigation of Spurious Correlation, [https://proceedings.mlr.press/v202/wu23w/wu23w.pdf](https://proceedings.mlr.press/v202/wu23w/wu23w.pdf)  
> 28. Understanding the Fine-Grained Knowledge Capabilities of Vision, [https://www.alphaxiv.org/abs/2602.17871](https://www.alphaxiv.org/abs/2602.17871)  
> 29. Benchmarking Large Vision-Language Models on Fine-Grained, [https://arxiv.org/abs/2606.19053](https://arxiv.org/abs/2606.19053)  
> 30. Benchmarking Large Vision-Language Models on Fine-Grained, [https://arxiv.org/html/2606.19053v1](https://arxiv.org/html/2606.19053v1)  
> 31. benchmarking large vision-language models \- ICLR Proceedings, [https://proceedings.iclr.cc/paper\_files/paper/2026/file/4a0a8ab1552821883f6cd41a6c6fc8f3-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/4a0a8ab1552821883f6cd41a6c6fc8f3-Paper-Conference.pdf)  
> 32. FLAIR: VLM with Fine-grained Language-informed Image ... \- CVPR, [https://cvpr.thecvf.com/virtual/2025/poster/33533](https://cvpr.thecvf.com/virtual/2025/poster/33533)  
> 33. Fine-Grained Image Classification for Vehicle Makes & Models, [http://cs230.stanford.edu/projects\_spring\_2019/reports/18681590.pdf](http://cs230.stanford.edu/projects_spring_2019/reports/18681590.pdf)  
> 34. On Large Multimodal Models as Open-World Image Classifiers \- arXiv, [https://arxiv.org/abs/2503.21851](https://arxiv.org/abs/2503.21851)  
> 35. Recognition-by-components theory \- Wikipedia, [https://en.wikipedia.org/wiki/Recognition-by-components\_theory](https://en.wikipedia.org/wiki/Recognition-by-components_theory)  
> 36. Recognition-by-Components: A Theory of Human Image ... \- SciSpace, [https://scispace.com/pdf/recognition-by-components-a-theory-of-human-image-2d038hmxno.pdf](https://scispace.com/pdf/recognition-by-components-a-theory-of-human-image-2d038hmxno.pdf)  
> 37. Geon \- Psychology Glossary, [https://www.psychology-lexicon.com/cms/glossary/40-glossary-g/1830-geon.html](https://www.psychology-lexicon.com/cms/glossary/40-glossary-g/1830-geon.html)  
> 38. \[2501.11309\] Finer-CAM: Spotting the Difference Reveals ... \- arXiv, [https://arxiv.org/abs/2501.11309](https://arxiv.org/abs/2501.11309)  
> 39. Spotting the Difference Reveals Finer Details for Visual Explanation, [https://arxiv.org/html/2501.11309v2](https://arxiv.org/html/2501.11309v2)