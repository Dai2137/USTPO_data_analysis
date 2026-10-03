# **2025〜2026年トップ会議における視覚言語モデルの対象認識と細粒度グラウンディングに関する研究動向調査**

## **1\. 全体像：2025〜2026年における研究の主流と少数派**

2025年から2026年にかけてのコンピュータビジョンおよび機械学習のトップ会議（CVPR、ICLR、NeurIPS、IJCAI等）において、視覚言語モデル（VLM）に画像内の対象を認識・命名させる研究は、根本的なパラダイムシフトの最中にある。従来の「画像全体のコンテキストからもっともらしいキャプションやラベルを生成する」タスクは、GPT-4oやQwen2.5-VLなどの強力な基盤モデルの登場により飽和状態に達している。現在の学術研究の主眼は、巨視的な認識から微視的な認識へと移行しており、具体的には「細粒度（Fine-grained）の視覚的詳細の認識」、「視覚とテキストの厳密な局所的グラウンディング（対応付け）」、および「言語バイアスに起因するハルシネーション（幻覚）の抑制」に集中している。  
このトレンドの背景には、「Words Over Pixels（ピクセルより単語を優先する）」と名付けられたVLMの構造的欠陥の発見がある1。最新の分析によれば、現在のVLMは視覚タスクを解く際、ピクセルレベルの視覚特徴を直接比較・推論しているのではなく、視覚情報を言語空間の既知の概念（単語）にマッピングし、言語モデルの推論能力に依存する「ショートカット」を学習している2。この現象は「Semantic Anchors（意味的アンカー）」仮説として提唱されており、モデルが名付けることのできる（事前学習データに頻出する）対象に対しては高い性能を示す一方で、事前学習に現れない未知の対象や、明確な名前を持たない局所的な視覚特徴に対しては、内部表現に十分な情報が存在するにもかかわらず認識に失敗することが証明されている3。  
このような背景のもと、2025〜2026年の研究アプローチは大きく二つの潮流に分かれている。  
主流となっているのは、モデルの重みを再学習させずに推論時の工夫のみで性能を向上させる「学習不要（Training-free）な介入・探索手法」である。数十億から数百億パラメータを持つ大規模VLMの事前学習や微調整には膨大な計算資源が必要となるため、多くの研究者は凍結されたモデルの内部状態を操作する手法を採用している。例えば、推論時のアテンションマップや勾配を監視して視覚情報の欠落を防ぐ手法や、画像内の重要な局所領域を自動的にクロップして再入力するマルチターン探索手法が数多く提案されている5。これらの研究は、計算コストを抑えつつ、既存モデルの性能限界を推論時のアルゴリズムによって引き上げることを目的としている。  
一方で、少数派ながら影響力の大きいアプローチとして、事前学習のデータセットそのものや、学習の目的関数を根本から見直す研究が存在する。画像全体のテキストペアを用いた従来の対照学習（Contrastive Learning）では、対象の局所的な対応関係が学習されないという問題に対し、画像内のオブジェクトとテキスト内のエンティティを直接結びつけるような合成データを数十万から数千万件規模で構築し、モデル全体や軽量なアダプターを学習させる手法がCVPR等で採択され始めている8。これらの研究は、VLMが抱える根本的なグラウンディング不足をデータ駆動で解決しようとする試みである。

## **2\. 4観点による代表的論文の配置構造**

2025年・2026年の主要会議から、本調査の目的に合致する代表的な論文を抽出し、「生成（推論）」「学習データ」「学習手法」「評価」の4観点で整理した結果を以下の表に示す。これらの論文は、それぞれ異なるアプローチでVLMの対象認識能力の向上または限界の解明に挑んでいる。

| 論文名 / 会議・年 | 観点1: 生成（推論） | 観点2: 学習データ | 観点3: 学習手法 | 観点4: 評価 (ベンチマーク+採点方法) | 実装公開 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **VLMs Need Words** (ICLR 2025\)3 | 段階的推論 (CoT)。意味的アンカー（名前）がない対象に対し、ピクセルレベルでの直接比較を強制するプロンプトを与えて生成。 | 未知の図形や部位を含むSPair-71k等を独自に拡張・構築。名前あり/なしでデータを分割し数千件規模で検証。 | **学習する (検証目的)**。タスク特化型の軽量な微調整（特定の未知対象にダミーの名前を割り当てる学習）を実施。 | **評価:** SPair-71k, 独自の形状マッチング。 **採点:** 完全一致、およびLogit Lensを用いた内部トークンの意味的解決度の測定。 | あり |
| **MLLMs Know Where to Look** (ICLR 2025\)6 | **推論時の介入**。内部のアテンションと勾配マップを抽出し、モデルが注目すべき小さな視覚的詳細を自動的にクロップして再入力する。 | 既存の学習済みモデルをそのまま利用するため、独自の学習データは構築しない。 | **学習しない**。凍結された汎用VLMをそのまま利用。追加の計算コストは推論時のフォワードパス増加分のみ。 | **評価:** V\*Bench 等の7つのVQAベンチマーク。 **採点:** 正答率（Accuracy）およびアテンション分布の因果的寄与度に基づく評価。 | あり |
| **Devils in Middle Layers** (CVPR 2025\)7 | **推論時の介入**。中間層での視覚情報の濃縮段階に着目し、複数ヘッド間で矛盾するアテンションを推論時に統合・制御して幻覚を防ぐ。 | （学習なし） | **学習しない**。凍結モデル（LLaVA等）の中間層アテンションを操作。 | **評価:** CHAIR, POPE。 **採点:** 生成テキストの構文解析を通じた、幻覚オブジェクトと実在オブジェクトの割合（CHAIR I/S）。 | あり |
| **FLAIR** (CVPR 2025\)8 | テキストを条件としたアテンション・プーリング。局所的な画像トークンを抽出し、細粒度の視覚的詳細を取得する生成機構。 | 3,000万件の画像と長文の合成キャプション（MLLMを用いて再生成されたDreamLIPデータ等）を使用。 | **学習する**。モデル全体またはエンコーダを、大域的および局所的（マルチポジティブ）なロスで対照学習。 | **評価:** 自作の細粒度検索タスク、ゼロショットセマンティックセグメンテーション。 **採点:** 埋め込みの類似度（Retrieval R@1）、mIoU。 | あり |
| **MMCS** (CVPR 2026\)9 | 凍結されたLLMに、テキストエンティティを視覚オブジェクトの埋め込みに置き換えた（コードスイッチング）表現を入力して生成。 | 77.3万件の合成データ。詳細キャプションからエンティティを抽出し、DINOでBounding Boxを付与して対応付け。 | **学習する**。プロジェクター（2層MLP）のみを視覚-言語の局所的グラウンディング目的で学習。 | **評価:** COCO等を用いたCKA（Centered Kernel Alignment）での特徴量アライメント測定、視覚グラウンディング。 | 未確認 |
| **Micro Edit Detection** (NeurIPS 2025\)10 | 視覚的な微細な差異（編集された画像と元画像）を見分けるための推論。既存のVLMアーキテクチャを使用。 | DOCCIおよびVisual Genomeを基に、意味的に重要な微細編集を施したペア画像を合成・構築。 | **学習する**。特徴量の一貫性を保つ正則化（Feature consistency regularization）を目的関数に追加し微調整。 | **評価:** 新規提案のMEDベンチマーク。 **採点:** 識別精度（微細な変更に対する幻覚の減少度合い、複数選択）。 | あり |
| **Chain-of-Focus** (ICLR 2026\)5 | 初期視覚トークンから情報を得て、不十分な場合は適応的にズームイン（クロップ）を繰り返すマルチターン推論。 | Visual Probe Datasetを構築（数千の高解像度画像と複雑な探索質問を含む）。 | **学習する**。強化学習（RL）を用いて、ズームと推論の意思決定ポリシーを学習。 | **評価:** V\* Bench, HR-Bench 4K。 **採点:** マルチターンでの最終的な回答の完全一致およびLLMによる判定。 | あり |

抽出された研究群から読み取れるのは、生成（推論）の工夫に主眼を置く研究は「学習しない（凍結モデル）」ことを前提とし、学習データや学習手法に主眼を置く研究は「標準的な推論」を用いるという明確なトレードオフである。これは、現在のVLM研究において「推論コストの増加」と「学習コストの増加」の両方を同時に要求する手法は、比較対象との公平性や実用性の観点から正当化が難しいためであると推測される。

## **3\. ベンチマークの使用頻度と「定番」の整理**

2025〜2026年の研究において、「VLMに画像内の対象を答えさせる・認識させる」タスクを評価するために使用されるベンチマークは、目的別に明確に細分化されている。この分野で新規の手法を提案し論文を執筆する場合、以下の表に挙げるカテゴリからそれぞれ代表的なベンチマークを選択し、複合的な評価環境を構築することが「定番」となっている。

| ベンチマーク名 | 測定対象と用途 | 規模 | 使用頻度 | 新規提案 | 評価の特性と役割 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **POPE** | ハルシネーション（対象の有無） | 3カテゴリ×数千件 | 非常に多い | 既存 | 対象が画像内に存在するかをYes/Noで問う。幻覚評価の事実上の標準基盤として必ず含まれる。 |
| **CHAIR** | ハルシネーション（生成テキスト内） | COCO基盤 | 非常に多い | 既存 | 生成された説明文の中に、画像にないオブジェクトがどれだけ含まれるかを厳密に測定（CHAIR-I / CHAIR-S）する7。 |
| **MMVP** | 視覚的錯乱（Distractor）への耐性 | 210ペア | 多い | 既存(24) | CLIPが混同する「視覚的に似ているが意味が異なる」画像ペア（Distractor）を用い、純粋な視覚認識力を問う10。 |
| **V\*Bench** | 高解像度・微小対象の探索 | 多数 | 多い | 既存(24) | 全体画像の中から極めて小さなオブジェクトを見つけ出す「視覚的探索」能力を測定。ズームやクロップ系手法の定番5。 |
| **DOCCI / DCI** | 記述の質・細粒度の正確性 | 1.5万件等 | 増加傾向 | 既存(24) | 単なる短いキャプションではなく、1画像あたり数百〜数千語の超詳細な記述。空間関係や属性を評価するための基盤として25-26年で多用される13。 |
| **MM-ID** | 複数対象の同定・一貫性 | 585サンプル | 少ない | **新規(25)** | 映画のキャラクターや特定個体（ID）を、リファレンス画像と照らし合わせて別のシーンから同定する能力を測定する15。 |
| **MED** | 意味的な微小変化の検出 | 新規構築 | 少ない | **新規(25)** | 元画像と、意味を変える微小な編集（Micro Edit）を施した画像のペアを用い、モデルが変化を検知できるかを測定する10。 |
| **SABRE** | 自動生成ストレステスト | 動的生成 | 少ない | **新規(26)** | テスト仕様から自動的に画像を合成・編集し、VLMの弱点を突くベンチマークを動的に生成するフレームワーク16。 |
| **CapArena-Auto** | 詳細キャプションの自動評価 | 600サンプル | 少ない | **新規(25)** | 人間の好みに相関するLLM-as-a-Judgeを用いたペアワイズの評価ベンチマーク。詳細な記述の評価を低コストで行う18。 |

新しいベンチマークを提案する論文（例えば、MM-ID15 や MED10）の評価設計を見ると、提案ベンチマークだけで評価を済ませている論文はトップ会議には存在しない。1本の論文における標準的な検証構成は、「主ベンチマーク（提案手法の新規性を証明する特定のタスク）」と「補助ベンチマーク（POPEやMMBenchなどの広範な既存指標）」の組み合わせである。これは、特定のタスクに特化することで、一般的な視覚認識能力（汎化性能）が犠牲になっていないことを証明する義務が著者に課せられているためである。

## **4\. ストーリーの型の分析：論文の設計構造と依存関係**

集められた論文の構造を分析すると、4つの観点（推論・データ・学習・評価）がどのように配置され、どの観点に新規性が置かれているかによって、3つの典型的な「ストーリーの型」が存在することが分かる。それぞれの型において、著者は自らの選択を異なるロジックで正当化している。

### **型1：診断・分析主導型（新規性は「評価・分析」に置く）**

この型は、現在のVLMが抱える根本的な欠陥を明らかにし、そのメカニズムを解明することに主眼を置く。代表例として *VLMs Need Words* (ICLR 2025\)3 や *Words Over Pixels?* (IJCAI 2025\)1 が挙げられる。 これらの論文では、新規性は「独自に構築した評価手法や仮説の証明」に置かれる。生成手法や学習データは既存のオープンソースVLM（LLaVAやQwen-VL等）をそのまま「標準」として採用する。なぜなら、彼らの目的は新しいモデルを作ることではなく、既存の標準モデルが「視覚的詳細（Pixels）を見ておらず、言語の単語（Semantic Anchors）に依存している」という普遍的な事実を証明することだからである。 主張の強さを担保するため、ablation（切り分け実験）はモデルの内部状態の解析に厚く割かれる。例えば、Logit Lensと呼ばれる手法を用いて中間層の隠れ状態を語彙にデコードし、モデルが視覚情報をどのように言語概念に変換しているかを可視化する3。手法を出さずとも、「コミュニティが見落としていた欠陥のメカニズムを実証した」という診断的価値が高く評価され、トップ会議に採択されている。

### **型2：推論時介入型（新規性は「生成（推論）」に置く）**

この型は、モデルの重みを更新することなく、推論時のアルゴリズムを工夫することで性能を引き上げるアプローチである。代表例として *Devils in Middle Layers* (CVPR 2025\)7 や *MLLMs Know Where to Look* (ICLR 2025\)6 がある。 ここでは、新規性は「生成（推論）時の工夫」に集中する。学習データと学習手法は意図的に「なし（凍結モデルを使用）」とされる。この選択の正当化の根拠は、「大規模モデルの再学習には莫大な計算コストがかかり、また独自の微調整はモデルが本来持つ汎用的な推論能力（General Knowledge）を破壊するリスクがある」という実用的な制約に基づく。 実験の厚みは、介入アルゴリズムのハイパーパラメータ（例：どの層のアテンションに介入するか、クロップする解像度の閾値をどう設定するか）のablationに置かれる。また、POPEやV\*Benchなどの既存ベンチマークを広く用いることで、「学習コストゼロでありながら、既存のあらゆるモデルにプラグアンドプレイで適用でき、一貫して性能を向上させる」という普遍性を主張の根拠としている6。

### **型3：データ駆動型グラウンディング（新規性は「データ」と「学習手法」に置く）**

この型は、既存のVLMの限界は事前学習データと目的関数に起因すると考え、新しいデータセットとそれに適した学習手法を提案する。代表例として *MMCS* (CVPR 2026\)9 や *FLAIR* (CVPR 2025\)8 が該当する。 新規性は「合成データの作り方」と「局所的な対照学習手法」に置かれる。既存のCLIP等で用いられる画像全体とテキストのペア学習では、局所的な対象の対応関係（グラウンディング）が学習されないため、テキスト内のエンティティと画像内のバウンディングボックスを直接結びつけるような数十万から数千万規模のデータセットを構築する。生成（推論）の仕組みは通常のフォワードパスを標準として採用し、推論時のトリックには依存しないことをアピールする。 主張の強さは、膨大な計算資源を投じた学習結果と、データサイズやロスの有無に関する詳細なスケーリング則の提示によって担保される。実験では、ゼロショットの検索タスクやセグメンテーションでの性能向上が強調される。

## **5\. 評価方法の整理：厳密な採点手順と信頼性の議論**

2025〜2026年の研究では、単純な「完全一致（Exact Match）」による採点は、表現の揺らぎや長文記述の評価において限界を迎えており、より洗練された評価手順が採用されている。

### **ハルシネーションの厳密な測定（CHAIR指標）**

対象の名前を答えさせる際、余計なものを答えていないかを測る手法としてCHAIR（Captioning with HAllucination InseRtion）が多用される7。 判定手順は極めて厳密である。まず、VLMに画像を説明させるテキストを生成させる。次に、生成されたテキストを自然言語処理ツール（NLTKやSpaCyなど）を用いて構文解析し、名詞（オブジェクト）を抽出する。最後に、MS COCOなどのグラウンドトゥルース（正解のオブジェクトリスト）と照合し、画像に存在しない名詞が生成されていればハルシネーションと判定する。指標として、文中の幻覚オブジェクトの割合を示すCHAIR-Iと、幻覚を含む文の割合を示すCHAIR-Sが報告され、手順がアルゴリズム化されているため再現性が高い。

### **視覚的錯乱肢（Distractor）を用いた複数選択評価**

対象の細粒度の認識力を測るため、MMVP12 や MED10 では、「視覚的には非常に似ているが、重要な手がかりが異なる画像」をDistractor（錯乱肢）として用意する。 候補の作り方には明確な基準がある。例えばMMVPでは、CLIPの画像埋め込み類似度スコアが0.95以上の「極めて視覚的に似ている候補」を意図的にスクリーニングし、その上で意味的な違い（例：視線が左か右か、特定の部品があるかないか）を持つペアを構築する10。この手法により、ランダムな候補を用いた評価では見逃されてしまう「VLMが本当に細部の違いを認識しているか」を厳密に測定することが可能となっている。

### **大規模言語モデルによる判定（LLM-as-a-Judge）と信頼性**

自由記述での命名や説明の採点において、GPT-4等を用いた判定が標準化している。しかし、単に「合っているか」を聞くプロンプトでは信頼性が低いため、判定手順を厳密に規定したフレームワーク（例：Multi-Crit19 や CapArena-Auto18）が用いられる。 判定モデルには、対象となる画像（または正解の超詳細記述）と、評価すべきVLMの回答を与え、「情報の網羅性」「属性の正確性」「ハルシネーションの有無」といった複数の明確なルーブリック（採点基準）に基づくスコアを出力させる。論文においては、このLLMによる判定が人間の評価とどの程度一致するか（Pearson相関係数やSpearman順位相関係数）を報告することが義務付けられつつあり、最新の手法では人間との一致率94.3%を達成していることが信頼性の根拠として議論されている18。

### **生成結果からの逆検索（Retrieval-based Evaluation）**

生成した答えから対象を検索し直す評価は、FLAIR8 等で採用されている。VLM（またはエンコーダ）が生成した局所的な視覚・言語特徴量を用いて、大量の画像プール（またはテキストプール）から最も類似度が高いものをコサイン類似度で検索し、Top-1 (R@1) や Top-5 の精度で採点する。これは、表現の揺らぎを吸収しつつ、モデルが対象をどの程度正確に特徴空間にマッピングできているかを定量化する有効な手段である。

## **6\. 依頼者の設定に近い上位5件の詳細と重なり**

依頼者の設定（質問文なし、稀な製品名、手がかりの局所性の違い、凍結/事後学習の双方、候補からの当て直し評価、自前ベンチマーク）に最も近い順に、2025〜2026年の主要論文5件を詳解し、計画と重なる部分を分析する。

### **1位：VLMs Need Words: Vision Language Models Ignore Visual Detail In Favor of Semantic Anchors (ICLR 2025\)**

3  
この研究は、VLMが未知の対象や明確な名前を持たない対象に対して、ピクセルレベルの視覚詳細を無視し、無理やり既知の言語概念（Semantic Anchors）に当てはめようとして失敗することを証明している。推論では段階的推論（CoT）を用い、学習においては未知の図形にランダムな名前を紐付ける微調整を実施している。評価はSPair-71k等の形状マッチングを用い、内部表現のLogit Lensでメカニズムを解明している。**重なる部分（計画の裏付け）：** 依頼者の「事前学習にほとんど現れない珍しい製品を含む」という設定は、まさにこの論文が指摘する「Semantic Anchorsを持たない対象でのVLMの破綻」という最前線の課題と完全に合致する。この論文の知見を引用することで、稀な製品を対象とすることの学術的意義を強力に裏付けることができる。

### **2位：MLLMs Know Where to Look: Training-free Perception of Small Visual Details (ICLR 2025\)**

6  
凍結されたVLMの内部アテンションと勾配マップを監視し、対象が小さい（局所的である）と判断した場合、その領域を自動でクロップして再入力する推論時の介入手法を提案している。学習は行わず、V\*Bench等の探索ベンチマークで精度を評価している。**重なる部分：** 「手がかりが小さな部分にある対象で失敗し、全体の輪郭にある対象では成功する（必要な粒度が対象ごとに違う）」という依頼者の課題意識と完全に一致している。この論文は「モデルはどこを見るべきかは知っているが、大域的な入力では解像度不足で認識に失敗する」ことを証明しており、粒度切り替えのアプローチの正当性を示している。

### **3位：FLAIR: VLM with Fine-grained Language-informed Image Representations (CVPR 2025\)**

8  
3000万件の長文合成キャプションデータを用い、テキストを条件としたアテンション・プーリングによって局所的な画像トークンを抽出する手法を学習させている。評価は細粒度の検索タスク（Retrieval）で行われている。**重なる部分：** 大域的な特徴と局所的な特徴のギャップを埋めるアプローチであり、「当て直しによる評価（Retrieval）」を主指標に置いている点が依頼者の評価設計と一致する。また、細粒度の認識力を向上させるために事後学習を想定している点も共通している。

### **4位：MultiModal Code-Switching (MMCS) (CVPR 2026\)**

9  
テキストエンティティを視覚オブジェクトの埋め込み（Bounding Boxに基づく）に置き換えた「コードスイッチング」表現を入力とする推論と学習手法を提案している。77.3万件の合成データを用い、プロジェクターのみを微調整している。**重なる部分：** 特定の対象（製品）を正確に同定するためには、画像全体のコンテキストではなく、オブジェクトレベルでの直接的な視覚・言語のグラウンディングが必要であるという根本的な主張が重なる。

### **5位：Micro Edit Detection (MED) benchmark (NeurIPS 2025\)**

10  
DOCCIなどを基に、意味的に重要な微細編集（Micro Edit）を施したペア画像を合成し、視覚的な微小な差異を見分ける能力を測定する新規ベンチマークを提案している。学習においては特徴量の一貫性を保つ正則化を導入している。**重なる部分：** 「視覚的に似た別製品を混ぜた8択で採点する」という依頼者の設定は、実装上の都合とされているが、学術的にはこの論文の「微細な編集（Distractor）を見抜く」というタスクと軌を一にする。高い類似度を持つ候補からの選択は、モデルの真の知覚限界を測る手法として正当化できる。

## **7\. 被りの判定と独自性の評価**

依頼者の計画する4つのポイントについて、2025〜2026年のトップ会議における「被り（既出）」の状況と「独自性（新規性）」を判定する。

> 1. **質問文なしの粒度切り替え（画像のみからの同定）**  
   * **判定：極めて新規性が高い。未解決の空白地帯である。**  
   * **理由：** 現在の「局所へのズームやクロップ」を行う研究（*Chain-of-Focus*5 や *V*\*23）は、例外なく「テキストの質問文（プロンプト）を手がかりにして探索領域を絞る」アプローチを採用している。「質問文を与えず、画像のみから対象の特性を判断し、自律的に必要な粒度（局所か全体か）を推定して切り替える」というアプローチは、今回の網羅的な調査範囲内に該当する研究が存在しない。これは論文の最大の強みとなる。  
> 2. **手がかりの局所性の測定（必要な粒度が対象ごとに違うことの証明）**  
   * **判定：概念としては一部既出だが、対象ドメイン（製品特性）への適用は新規。**  
   * **理由：** 対象のサイズ（局所性）によってVLMの認識率が低下することは *MLLMs Know Where to Look*6 等で証明されている。しかし、同論文は一般的な物体（COCO等の汎用オブジェクト）を対象としている。依頼者の「特定の製品を見分ける際、製品Aは全体シルエットで分かるが、製品Bはロゴや端子などの極めて局所を見ないと分からない」という、「対象クラスの特性に依存する手がかりの局所性の非対称性」を測定・モデル化した研究は見当たらない。  
> 3. **当て直しによる評価（視覚的に似た別製品を混ぜた採点）**  
   * **判定：手法としては既出（標準的）だが、説得力のある評価基盤になり得る。**  
   * **理由：** 候補からの検索（Retrieval）による評価は *FLAIR*8 で、視覚的Distractorを用いた評価は *MMVP*12 や *MED*10 で既に行われている。したがって、この評価手法自体に目新しさはないが、裏を返せば「2025-2026年のトップ会議で正当性が認められている堅牢な評価プロトコル」である。論文を書く際、MMVPやMEDの設計思想を引用することで、「実装上の都合」ではなく「意図的かつ高度なDistractor評価」として洗練させることができる。  
> 4. **未学習カテゴリ（事前学習に現れない珍しい製品）での一般化**  
   * **判定：トレンドに完全に合致しており、強い主張の根拠となる。**  
   * **理由：** *VLMs Need Words*3 が示す通り、現在のVLMの最大の弱点は「名付けられない（学習データにない）対象に対するピクセルレベルの推論の欠如」である。依頼者の設定は、まさにこの最前線の課題に対する直接的なテストベッドとなる。

**結論として、依頼者の研究計画は、2025〜2026年のトップ会議のトレンド（細粒度グラウンディング、局所的視覚理解）の中心に位置しつつ、「プロンプトなし（Promptless）での自律的な粒度切り替え」という明確な新規性を持っている。** ストーリーの組み立てとしては、「型1（診断・分析）」と「型2（推論時介入）」のハイブリッドが最適である。すなわち、「VLMは事前知識（プロンプト）なしには、製品ごとに異なる必要な粒度を判断できない」という脆弱性を自作のDistractorベンチマークで証明し、その解決策として「画像のみから必要な粒度を推定し適応的に切り替える推論手法」を提案する構成にすれば、トップ会議に十分に通用する強力な論文設計となる。

## **8\. 抽出論文の詳細書誌データ**

本調査で抽出・言及した2025〜2026年の主要な研究の書誌情報を以下に示す。

| 略称 / キーワード | 正式タイトル | 著者 | 会議・年 | arXiv番号 / 備考 | 実装URL |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **VLMs Need Words** | VLMs Need Words: Vision Language Models Ignore Visual Detail In Favor of Semantic Anchors | H. S. Shahgir, X. Chen, Y. Fu, et al. | ICLR 2025 | arXiv:2604.024863 | github.com/Patchwork53/VLMs-Need-Words-COLM2026 |
| **MLLMs Know Where to Look** | MLLMs Know Where to Look: Training-free Perception of Small Visual Details with Multimodal LLMs | J. Zhang, M. Khayatkhoei, P. Chhikara, et al. | ICLR 2025 | arXiv:2502.174226 | github.com/saccharomycetes/mllms\_know |
| **Devils in Middle Layers** | Devils in Middle Layers of Large Vision-Language Models: Interpreting, Detecting and Mitigating Object Hallucinations via Attention Lens | Z. Jiang, Y. Yeo | CVPR 2025 | arXiv:2411.167247 | github.com/ZhangqiJiang07/middle\_layers\_indicating\_hallucinations |
| **FLAIR** | FLAIR: VLM with Fine-grained Language-informed Image Representations | R. Xiao, S. Kim, M.-I. Georgescu, et al. | CVPR 2025 | arXiv:2412.035618 | 公開予定（論文内記載） |
| **MMCS** | MultiModal Code-Switching: Interleaving Visual Objects into Language for Explicit Object-Level Alignment | (著者情報省略/プレプリント準拠) | CVPR 2026 | arXiv:2608.111679 | 未確認 |
| **MED** | Micro Edit Detection (MED): Evaluating Fine-Grained Vision-Language Reasoning | (NeurIPS プロシーディングス準拠) | NeurIPS 2025 | (NeurIPS 2025\)10 | github.com/Relaxed-System-Lab/hallu\_med |
| **Chain-of-Focus** | Chain-of-Focus: Adaptive visual search and zooming for multimodal reasoning via RL | X. Zhang, et al. | ICLR 2026 | arXiv:2505.154365 | 公開予定（論文内記載） |
| **SABRE** | SABRE: Scalable and Automated Benchmarking of VLMs under Stress | Z. Lan, L. Sun, M. R. Walter, J. Zhou | 未確認(26年) | arXiv:2608.0743516 | 未確認 |
| **Words Over Pixels** | Words Over Pixels? Rethinking Vision in Multimodal Large Language Models | A. Jain, M. Vatsa, R. Singh | IJCAI 2025 | (IJCAI 2025\)1 | なし (サーベイ/分析論文) |
| **Multi-Crit** | Multi-Crit: Benchmarking Multimodal Judges on Pluralistic Criteria-Following | T. Xiong, Y. Ge, M. Li, et al. | CVPR 2026 | (CVPR 2026\)19 | 未確認 |
| **CapArena-Auto** | CapArena-Auto: Automated Benchmark for Detailed Image Captioning | (ACL Findings 準拠) | ACL 2025 | (ACL Findings 2025\)18 | 未確認 |
| **DOCCI** | DOCCI: Descriptions of Connected and Contrasting Images | Y. Onoe, et al. | ECCV 2024 | (ECCV 2024\)14 | 既存評価基盤として参照 |
| **MMVP** | MMVP: Multimodal Visual Patterns | (NeurIPS プロシーディングス準拠) | NeurIPS 2024 | (NeurIPS 2024\)10 | 既存評価基盤として参照 |
| **V\*** | V\*: Guided visual search as a core mechanism in multimodal llms | P. Wu, S. Xie | CVPR 2024 | (CVPR 2024 / ICLR 2025\)23 | 既存探索基盤として参照 |

#### **引用文献**

> 1. Words Over Pixels? Rethinking Vision in Multimodal Large ... \- IJCAI, [https://www.ijcai.org/proceedings/2025/1164.pdf](https://www.ijcai.org/proceedings/2025/1164.pdf)  
> 2. VLMs Need Words: Vision Language Models Ignore Visual Detail In, [https://arxiv.org/html/2604.02486v2](https://arxiv.org/html/2604.02486v2)  
> 3. VLMs Need Words: Vision Language Models Ignore Visual Detail In, [https://arxiv.org/html/2604.02486v3](https://arxiv.org/html/2604.02486v3)  
> 4. VLMs Need Words: Vision Language Models Ignore Visual Detail In, [https://www.alphaxiv.org/abs/2604.02486](https://www.alphaxiv.org/abs/2604.02486)  
> 5. Adaptive Visual Search and Zooming for Multimodal Reasoning via RL, [https://www.researchgate.net/publication/391954558\_Chain-of-Focus\_Adaptive\_Visual\_Search\_and\_Zooming\_for\_Multimodal\_Reasoning\_via\_RL](https://www.researchgate.net/publication/391954558_Chain-of-Focus_Adaptive_Visual_Search_and_Zooming_for_Multimodal_Reasoning_via_RL)  
> 6. Training-free Perception of Small Visual Details with Multimodal LLMs, [https://www.researchgate.net/publication/389315251\_MLLMs\_Know\_Where\_to\_Look\_Training-free\_Perception\_of\_Small\_Visual\_Details\_with\_Multimodal\_LLMs](https://www.researchgate.net/publication/389315251_MLLMs_Know_Where_to_Look_Training-free_Perception_of_Small_Visual_Details_with_Multimodal_LLMs)  
> 7. Devils in Middle Layers of Large Vision-Language Models \- arXiv, [https://arxiv.org/html/2411.16724v3](https://arxiv.org/html/2411.16724v3)  
> 8. FLAIR: VLM with Fine-grained Language-informed Image ... \- CVPR, [https://cvpr.thecvf.com/virtual/2025/poster/33533](https://cvpr.thecvf.com/virtual/2025/poster/33533)  
> 9. MultiModal Code-Switching: Interleaving Visual Objects into ... \- arXiv, [https://arxiv.org/pdf/2608.11167](https://arxiv.org/pdf/2608.11167)  
> 10. Controlled Visual Editing and Fine-Grained Multimodal Learning, [https://proceedings.neurips.cc/paper\_files/paper/2025/file/c518f504ad5894ccb264a9890f0f5544-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2025/file/c518f504ad5894ccb264a9890f0f5544-Paper-Conference.pdf)  
> 11. Devils in Middle Layers of Large Vision-Language Models \- arXiv, [https://arxiv.org/html/2411.16724v1](https://arxiv.org/html/2411.16724v1)  
> 12. How Vision-Language Tasks Benefit from Large Pre-trained Models, [https://arxiv.org/html/2412.08158v1](https://arxiv.org/html/2412.08158v1)  
> 13. \[Literature Review\] DOCCI: Descriptions of Connected and, [https://www.themoonlight.io/en/review/docci-descriptions-of-connected-and-contrasting-images](https://www.themoonlight.io/en/review/docci-descriptions-of-connected-and-contrasting-images)  
> 14. DOCCI: Descriptions of Connected and Contrasting Images \- arXiv, [https://arxiv.org/html/2404.19753v1](https://arxiv.org/html/2404.19753v1)  
> 15. IDA-VLM: TOWARDS MOVIE UNDERSTANDING VIA ID-AWARE, [https://proceedings.iclr.cc/paper\_files/paper/2025/file/82dcb6da1b408d59d15f68afdebf1489-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2025/file/82dcb6da1b408d59d15f68afdebf1489-Paper-Conference.pdf)  
> 16. SABRE: Scalable and Automated Benchmarking of VLMs under Stress, [https://arxiv.org/html/2608.07435v1](https://arxiv.org/html/2608.07435v1)  
> 17. SABRE: Scalable and Automated Benchmarking of VLMs under Stress, [https://www.aimodels.fyi/papers/arxiv/sabre-scalable-automated-benchmarking-vlms-under-stress](https://www.aimodels.fyi/papers/arxiv/sabre-scalable-automated-benchmarking-vlms-under-stress)  
> 18. CapArena: Benchmarking and Analyzing Detailed Image Captioning, [https://aclanthology.org/2025.findings-acl.724.pdf](https://aclanthology.org/2025.findings-acl.724.pdf)  
> 19. MAIN CONFERENCE PROGRAM \- EventHosts, [https://media.eventhosts.cc/Conferences/CVPR2026/CVPR\_main\_conf\_2026\_15.pdf](https://media.eventhosts.cc/Conferences/CVPR2026/CVPR_main_conf_2026_15.pdf)  
> 20. MLLMs Know Where to Look: Training-free Perception of Small, [https://openreview.net/forum?id=DgaY5mDdmT](https://openreview.net/forum?id=DgaY5mDdmT)  
> 21. FLAIR: VLM with Fine-grained Language-informed Image, [https://www.computer.org/csdl/proceedings-article/cvpr/2025/436400y884/299bIQJeolG](https://www.computer.org/csdl/proceedings-article/cvpr/2025/436400y884/299bIQJeolG)  
> 22. MultiModal Code-Switching: Interleaving Visual Objects into ... \- arXiv, [https://arxiv.org/html/2608.11167](https://arxiv.org/html/2608.11167)  
> 23. FOCUS: Internal MLLM Representations for Efficient Fine-Grained, [https://arxiv.org/html/2506.21710v2](https://arxiv.org/html/2506.21710v2)  
> 24. ImageInWords: Unlocking Hyper-Detailed Image Descriptions, [https://aclanthology.org/2024.emnlp-main.6.pdf](https://aclanthology.org/2024.emnlp-main.6.pdf)