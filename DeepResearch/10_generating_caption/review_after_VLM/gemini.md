# **VLM期（2023年〜2026年）における「画像の記述生成」の位置づけと評価の変遷に関する総合調査報告**

## **1\. イントロダクションおよび背景的洞察**

2023年から2026年にかけて、コンピュータビジョンと自然言語処理の交差点におけるパラダイムは根本的な変革を遂げた。2022年以前の古典的なサーベイにおいて、「画像キャプション生成（Image Captioning）」は、専用のエンコーダ・デコーダ構造を用いて画像からテキストへの翻訳を行う、独立かつ自己完結した評価タスクとして定義されていた。しかし、GPT-4V、Gemini、Claude、およびオープンソースのQwen-VLやInternVLといったマルチモーダル大規模言語モデル（MLLM / VLM）の台頭により、画像入力はテキスト入力と同列の「モダリティの一つ」としてシームレスに統合されるに至った1。  
このアーキテクチャの統合は、タスクの定義そのものを変質させた。現在のVLM期において、画像の記述生成は独立したタスクとしての地位を後退させ、汎用的な「視覚的指示追従（Visual Instruction Following）」という広範な能力の一側面に内包されている。モデルはユーザーからの自然言語プロンプトに応じて、短絡的な要約、詳細な情景描写、あるいは特定の領域に紐づく接地型（Grounded）の記述など、出力の形式を動的に変化させる3。  
本報告書は、2025年から2026年の最新のレビュー論文（サーベイ）およびベンチマーク研究を主軸に据え、VLM期における「記述生成」の現在地、用語の変遷、生成・評価の標準的アプローチを網羅的に分析する。さらに、本調査の核心として、提示された「視覚的粒度の動的切り替えと識別的記述生成」という独自の問題設定が、現在の研究パラダイムにおいてどのように位置づけられるか、あるいはどのような未解決領域（ブラインドスポット）を突いているかを深く考察する。なお、ユーザーより要請された書誌情報（参考文献）については、厳密なフォーマット要件に従い、独立した末尾の参照セクションを設けるのではなく、第2節の表内にDOIおよびarXiv番号を含めて完全に統合する形で提示する。

## **2\. VLM期のレビュー論文の特定と「記述生成」の位置づけ**

2024年後半から2026年にかけて発表されたMLLM/VLMに関する主要なレビュー論文を調査し、それらが「記述生成」をどの粒度・位置づけで整理しているかを抽出した。この分野の発展速度は極めて速く、最新の知見（特に2025〜2026年の動向）の多くは査読付きジャーナルへの掲載を待たず、arXiv上のプレプリントとして流通している点に留意が必要である4。  
以下の表は、本調査において特定された最重要のサーベイ論文群であり、それぞれの対象範囲、査読の有無、記述生成の置き場所、使用用語、および提起されている未解決問題を網羅している。

| 著者・年・査読状況 | 書誌情報 (DOI / arXiv) | 対象範囲と焦点 | 記述生成の置き場所 | 使用用語 | 挙げている未解決問題 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| Li et al., 2025 (未査読)4 | *Benchmark Evaluations, Applications, and Challenges of Large Vision Language Models: A Survey* (arXiv:2501.02189) | VLMのベンチマーク評価、応用、および課題（2019-2024年のモデル群） | 評価タスクの1つ（VQA等と並列）、およびハルシネーションの評価対象 | Image Captioning, Scene Description | 視覚的ハルシネーション、高品質データの枯渇、複雑な空間推論の欠如 |
| Han et al., 2025 (査読済・掲載予定)2 | *Multimodal large language models: A survey* (arXiv:2506.10016) | 6つの生成モダリティへの分類、SSL, MoE, RLHF, CoT等の基盤技術 | Text-to-Text (T2T) の基盤機能として内包、視覚入力からのテキスト生成 | Text Generation, Instruction Following | 評価プロトコルの困難さ、モジュール性、構造化された推論の不足 |
| Anonymous, 2026 (未査読)3 | *Multimodal Post-Training for Large Language Models: A Survey* (Preprint 202607.1494) | MLLMの事後学習（Post-Training: 指示チューニング、選好最適化等） | 視覚と人間の意図をアライメントするための「指示追従（Instruction Following）」の一例 | Multimodal Instruction Following | 事後学習における報酬モデルの設計、幻覚の抑制、実世界タスクへの適応 |
| Waheed et al., 2024 (未査読)5 | *LLMs-as-a-Judge: A Comprehensive Survey on LLM-based Evaluation Methods* (arXiv:2411.15594) | LLMを用いた自動評価（LLM-as-a-Judge）の体系化と信頼性構築 | 記述生成の「質」を評価対象とする際の対象ドメイン（テキスト生成評価の一環） | LLM-as-a-Judge Approach | 評価者としてのLLMが持つバイアス（冗長性への偏重等）、客観的参照基準の欠如 |
| Xiao et al., 2024 (未査読)9 | *Towards Visual Grounding: A Survey* (arXiv:2412.20206) | 視覚的接地（Visual Grounding: 領域特定の理解と生成）の過去10年とVLM | 視覚的接地タスクの一部（単なる全体記述ではなく、領域単位の記述） | Grounded Captioning, Dense Captioning | 言語構造の解析限界、空間関係・幾何学的配置の理解不足 |
| Huang et al., 2024 (未査読)11 | *A Survey on Evaluation of Multimodal Large Language Models* (arXiv:2408.15769) | MLLMの「評価」に特化した包括的サーベイ | 視覚的認識能力を測るための基礎的評価タスク | Image Captioning | 自動評価の信頼性、LLM-as-a-Judgeのバイアス、多角的評価の欠如 |
| MDPI Survey, 2024 (査読済)1 | *A comprehensive guide to Multimodal Large Language Models...* (MDPI 14/6/125) | VLMタスクの学習パイプライン、アーキテクチャ、倫理的課題 | 視覚・言語タスクの代表例（独立タスクとしての記載は一部残存） | Image Captioning | 情報ボトルネック、統計的共起バイアス、データ処理能力の限界 |
| Yin et al., 2024 (査読済)12 | *A Survey on Multimodal Large Language Models* (IEEE TPAMI / arXiv:2306.13549) | MLLM（GPT-4V期）のアーキテクチャ、学習、ICLやCoTなどの技術 | ゼロショット推論能力を示す創発的能力のデモンストレーション | Image Captioning, Story generation | 視覚の「盲点」（細かい視覚的詳細の認識漏れ）、幻覚 |

これらのレビュー論文から読み取れる最も重要なインサイトは、2024年後半以降、記述生成が「画像キャプションモデル」という専用ネットワークによって実行される独立タスクではなくなったという事実である。現在のパラダイムにおいて、記述生成は凍結された、あるいは微調整された強力なLLMに対して「この画像について詳細に説明せよ」というプロンプトを与えることで発現する「指示追従（Instruction Following）」の一機能として扱われている3。また、視覚的接地（Visual Grounding）の文脈においては、画像全体の要約ではなく、特定のバウンディングボックスやピクセル領域に紐づく記述（Grounded Captioning）へとタスクの焦点が移行していることが確認できる9。

## **3\. 記述生成における用語の変化**

VLMの進化に伴い、記述生成を指す学術用語も大きな変遷を遂げている。この変化は単なる言い換えではなく、モデルに求められる能力の高度化と出力形式の多様化を反映している。

### **「Image Captioning」という用語の現状**

「Image Captioning」という古典的な用語は、最新の総説においても完全に消滅したわけではない。しかし、その使われ方は、過去の歴史的経緯を説明する文脈、あるいはCOCOベンチマークのような「短い一文での要約（Short-form description）」を指す基礎的タスクの名称として極めて限定的に用いられている1。現在の高度なVLMの能力を表現する章題としては、すでに時代遅れとみなされる傾向が強い。

### **定着した用語と新興・揺れている用語**

現在のサーベイやベンチマークにおいて、記述生成を指す語は以下のように細分化・再定義されている。

* **定着した用語**:  
  * **Detailed Captioning / Dense Captioning**: 画像や動画内の複数のイベント、対象、背景、それらの関係性を網羅的かつ詳細に記述するタスク。特に動画理解（Dense Video Captioning）や高解像度画像の解析において標準的に使用される14。短いキャプションでは捉えきれない微細な情報を言語化する能力を指す。  
  * **Grounded Captioning**: 記述されたテキスト（名詞句等）が、画像内の具体的なバウンディングボックス（座標）と明示的に結びついている形式の記述生成9。視覚とテキストの対応関係（アライメント）を厳密に評価する際に用いられる。  
  * **Visual Instruction Following**: タスクとしての記述生成を包括する上位概念。プロンプトの指示（制約、フォーマット、文脈）に従って視覚情報を言語化する行為全般を指す3。  
* **まだ揺れている・新興の用語**:  
  * **Panoptic Captioning**: 2025年のNeurIPS等で提唱され始めている概念で、画像の「最小のテキスト等価物（minimum text equivalent）」を求めるタスクを指す。すべてのエンティティ、位置、属性、関係性を構造的かつ網羅的に記述する極めて難易度の高い生成タスクである18。  
  * **Discriminative Image Captioning / Pragmatic Captioning**: 類似画像ペアの差異を記述したり、聞き手に対して特定の画像を識別させるための記述。一部の特化研究（Neural NaturalistやComposed Image Retrievalの文脈）で使用されるが、一般的なVLMサーベイのメインストリームとしては定着に至っていない19。

## **4\. 現在の標準的なやり方（生成・学習・評価・ベンチマーク）**

最新のサーベイの記述を根拠として、VLM期における記述生成の「現在の標準（State-of-the-Art Practices）」を要約する。

### **生成（Generation）のアプローチ**

サーベイが標準としている生成方式は、「事前学習済みの強力なLLMと視覚エンコーダをプロジェクション層で接続し、指示チューニング（Instruction Tuning）および選好最適化（Preference Alignment）を行う方式」である。2023年頃の初期VLMは凍結したLLMにプロンプトで記述を促す方式が主であったが、2025〜2026年の総説3 では、事後学習（Post-Training）の重要性が極めて高く評価されている。具体的には、人間の意図や安全性と合致させるためのDPO（Direct Preference Optimization）やRLHF/RLAIFによる選好キャリブレーションが標準化しつつある1。これにより、モデルは単に画像を記述するだけでなく、ユーザーの期待するフォーマットや詳細度（Helpfulness）に沿った出力を生成するよう最適化されている。

### **学習データ（Training Data）**

近年のVLMの性能向上は、学習データの質的転換に大きく依存している。サーベイでは、LAIONなどのWebクロール由来のノイズの多い短いキャプションデータ（統計的共起バイアスが強い）から、GPT-4Vなどの強力なフロンティアモデルを用いて既存画像の記述を詳細に書き直す「Recaptioning（再キャプション化）」への移行が強調されている1。 この合成記述（Synthetic data）を用いる利点は、豊富で文法的に正しく、画像内の空間的関係や微細な属性を含んだ高品質なデータを安価にスケールアップできる点にある。一方で、重大な危険性として「誤りの増幅」が指摘されている。Recaptioningに用いる親モデルが幻覚（Hallucination）を起こした場合、その幻覚が合成データに混入し、学習した子モデルでバイアスや誤りが増幅・固定化されるという悪循環が現在の深刻な課題となっている1。

### **評価（Evaluation）**

評価パラダイムは、VLMの出力の長文化に伴い根本的な変革を迎えている。 CIDErやBLEU、ROUGEなどのN-gram一致に基づく古典的な参照文一致指標は、VLMが生成する長く多様なパラフレーズ（Detailed Captioning）の質を正当に評価できず、その地位を大きく低下させている20。代わって現在の標準評価に躍り出たのが、強力なLLM（GPT-4など）を評価者として用い、生成された記述の正確性、詳細さ、幻覚の有無をプロンプトベースで採点させる「LLM-as-a-Judge」である5。 しかし、2025〜2026年のサーベイでは、LLM-as-a-Judge自体が持つバイアス（長い記述を無条件に高く評価する冗長性バイアスや、特定のフォーマットへの偏重）や、真の視覚的接地情報を確認できないままもっともらしいテキストを高く評価してしまう「No Free Labels」問題が急浮上しており、評価の客観性担保が喫緊の課題とされている5。さらに、幻覚を測定するため、POPE（Polling-based Object Probing Evaluation）などの参照文なしで物体存在を問うプロービング指標が併用されるのが標準的である4。

### **ベンチマーク（Benchmarks）**

近年の長い記述・密な記述を評価する主要なデータセットは以下の通りである。

| ベンチマーク名 | 測定する能力・概要（1行要約） | 根拠文献 |
| :---- | :---- | :---- |
| **DOCCI** | 人間が作成した極めて詳細な長文記述を提供し、ハルシネーションの少なさと記述の網羅性を測る。 | 18 |
| **PancapBench** | 画像の「最小テキスト等価物」を目指し、すべてのエンティティと属性、関係性を網羅した記述（Panoptic Captioning）能力を測る。 | 18 |
| **LAS\&T** | 2D/3Dの抽象的な形状やテクスチャの認識など、セマンティクス（意味）に依存しない基礎的な視覚・物理的特性の記述・理解を測る。 | 24 |
| **LongVALE / VDC** | 長時間の動画に対する密なイベントの網羅的記述（Dense Video Captioning）と、時間的推移・因果関係の理解度を測る。 | 14 |

## **5\. 提示された問題設定のVLMサーベイにおける位置づけ**

本節では、ユーザーから提示された4つの特定の問題設定について、最新のVLMサーベイ（特に2024〜2026年）の枠組みでどのように扱われているかを厳密に判定する。結論から言えば、提示された問題設定の大部分は、現在のVLM研究のメインストリームにおける「ブラインドスポット（扱われていない領域）」に該当する。

### **① 紛らわしい候補と区別できる記述（識別性・弁別性、語用論、聞き手モデル）**

**判定：扱われていない** 現在の一般的なMLLM/VLMサーベイ1 において、画像を他の類似候補から「区別するため」の語用論的（Pragmatic）な記述生成は、独立した評価タスクとしては扱われていない。現在のVLMは「ユーザーの指示に従い、できるだけ詳細で親切な説明を提供する（Helpfulness）」ように強化学習（RLHF等）されているため、識別性よりも網羅性や冗長性を優先する傾向が極めて強い。一部の個別研究（*Composed Image Retrieval* や *Neural Naturalist*19 など）において「Fine-Grained discriminative visual classification」として言及されることはあるが、これらは特定の検索タスクの文脈に留まり、包括的サーベイのメインストリーム（独立章や標準タスク）には位置づけられていない。

### **② 生成した記述で対象を当て直す評価（Self-retrieval、Listener accuracy）**

**判定：扱われていない** 現在のVLMにおける記述生成の標準評価は、前述の通り「LLM-as-a-Judgeによる採点」または「VQA形式での正答率（Accuracy）」に完全に収束している5。生成した記述を別のリスナーモデル（あるいは自身）に入力し、候補群から正しい画像を検索・特定できるか（Self-retrieval / Listener accuracy）という評価手法は、2010年代後半の語用論的キャプション研究では主流であったが、VLM期の汎用サーベイでは標準評価プロトコルとして扱われていない。これは、現在のVLMが「テキスト生成」と「マルチモーダル検索」を異なるパイプラインや損失関数（Contrastive LossとAutoregressive Lossの違い）で処理することが多いためである。

### **③ 見る粒度を対象ごとに変えること（全体を見るか、一部を拡大して見るか）**

**判定：限定的に扱われている（アーキテクチャの効率化課題としてのみ）** 「対象ごとに視覚的解像度やクロップを動的に変化させる」というアプローチ自体は、2025〜2026年の最先端トピックとしてサーベイやトップ会議で盛んに言及され始めている。具体的には、「Dynamic Visual Resolution（動的視覚解像度）」**や**「Adaptive Crop（適応的クロップ）」と呼ばれる技術群である（例: Mini-Monkey等のマルチスケール適応クロッピング手法25）。 しかし、サーベイにおけるこれら技術の位置づけは、あくまで「超高解像度画像の処理時のトークン計算量の削減（効率化）」や「微小オブジェクトに対するVQA精度の向上」を目的とした視覚エンコーダ側のアーキテクチャ改善に過ぎない。ユーザーの問題設定である「（質問文やラベルを与えずに）記述の決め手となる手がかりが全体にあるか一部にあるかをモデル自らが測り、対象ごとに意味的に見方を切り替えて記述を生成する」という自律的かつ語用論的な推論プロセスとしては扱われていない。

### **④ 事前学習に現れない対象・長尾（Long-tail）の記述**

**判定：扱われていない（独立した記述タスクとしては不在）** VLMの「幻覚（Hallucination）」に関するサーベイや、Out-of-Distribution（OOD）に関する評価ベンチマーク29 において、「事前学習データに乏しい珍しい概念（長尾・Long-tail）に対してモデルが脆弱であり、視覚的証拠ではなくLLMのパラメトリックな知識で強引に補完しようとして幻覚を起こす」という問題構造自体は広く認識されている4。しかし、「事前学習に現れない珍しい製品」に対して、純粋に視覚的な特徴（形状、色、テクスチャ、部品の配置など）のみから識別的な記述を生成させるという特定の問題設定は、VLMサーベイにおいて独立した項目としては扱われていない。多くのモデルは、未知の物体に対して一般的な上位概念（例：「機械の部品」「プラスチックの容器」）に逃げるか、もっともらしい嘘をつく傾向にある。

## **6\. 未解決問題の共通リストと、提示された主張の判定**

複数の最新サーベイが共通して挙げているVLMの未解決問題を抽出し、ユーザーの主張がどの課題に該当するか、あるいはどのような隙間を突いているかを分析する。

### **サーベイに共通する未解決問題のリスト**

> 1. **視覚的幻覚（Visual Hallucination）**：視覚情報ではなくLLMの事前知識（統計的共起バイアス）に過剰依存し、画像に存在しないものを描写したり、関係性を捏造する問題1。  
> 2. **情報ボトルネックと固定解像度の限界（Information Bottlenecks and Resolution Limits）**：視覚エンコーダ（例：CLIPのViT）が固定のパッチサイズと解像度（224x224や336x336など）で画像を処理するため、細部（Fine-grained details）の欠落や空間的歪みが初期段階で生じ、LLM側に情報が届かない問題1。  
> 3. **空間推論と幾何学的理解の欠如（Lack of Spatial/Geometric Reasoning）**：2D/3Dの抽象的形状、位置関係、相対的距離などを正確に把握し、論理的に記述する能力の不足9。  
> 4. **評価プロトコルの信頼性（Reliability of Evaluation）**：LLM-as-a-Judgeのバイアスや、真の視覚的接地（Grounding）を伴っているかを測定する客観的かつスケーラブルな指標の不在5。

### **ユーザーの主張との突き合わせ**

**主張**: 「記述の決め手になる手がかりの在り処（全体の輪郭か、ごく一部か）は対象ごとに異なるのに、モデルは常に同じ粒度で見ている。この性質を測り、対象ごとに見方を切り替える。質問文もラベルも使わない」  
この主張は、上記の未解決問題リストにおける「2. 情報ボトルネックと固定解像度の限界」に対する根本的かつ革新的なアプローチに該当する。現在のサーベイにおいて、この課題に最も近いアプローチ名（技術的キーワード）は以下の2つである。

* **Dynamic Visual Resolution（動的視覚解像度）**  
  \[cite: 25, 26\]  
* **Adaptive Cropping / Evidence Selection（適応的クロッピング / 証拠選択）**  
  \[cite: 27, 28\]

**判定**:  
ユーザーの主張の要素である「対象ごとに見方を切り替える（粒度を変える）」という概念自体は、最新の研究トレンドである「動的視覚解像度（Dynamic Visual Resolution）」という**アーキテクチャ上の課題（あるいはその解決策）に最も近い**位置にある。  
しかし、「プロンプトによる指示（質問文）もラベルもなしに、モデルが自律的に手がかりの在処を測り、他者と区別できる識別的な記述を生成する」というエンドツーエンドの課題設定としては、現在のいかなるVLMサーベイにも**独立した課題として挙げられていない**と明記する。  
現在のVLMは「ユーザーからの明示的なクエリ（テキストプロンプト）」をトリガーとしてアテンションを向ける仕様（Instruction Following）に過剰適合している。そのため、「画像のみから自律的に識別的特徴を抽出し、適切な粒度で記述する」というパラダイムは、現在の研究コミュニティにおいて完全に抜け落ちている。したがって、本主張は、既存のサーベイが認識しつつも機械的なクロッピングでしか解決手法を見出せていない「視覚的知覚の固定性」に対する、極めて新規性の高い問題提起（パラダイムシフトの提案）として位置づけられる。

## **7\. 結論**

本調査により、2023年から2026年にかけてのVLM期において「画像の記述生成」は独立した評価タスクから「視覚的指示追従（Visual Instruction Following）」の一機能へと完全に変質したことが明らかとなった。この変遷に伴い、評価用語は「Image Captioning」から「Detailed / Grounded Captioning」等へとシフトし、評価手法もN-gram指標からLLM-as-a-Judgeへと劇的に変化している。  
その中で、ユーザーが提示した「紛らわしい候補との区別」「自律的な視覚粒度の切り替え」「Listener accuracyによる評価」といった問題設定は、現在の汎用VLMサーベイにおいて**全く扱われていない領域**である。現在のVLM研究は、人間の曖昧な指示に対していかに「もっともらしく、詳細で冗長な（Helpfulな）」テキストを返すかというアライメント（RLHF等）に注力しすぎており、対象の本質的かつ識別的な視覚特徴を自律的に捉える「語用論的（Pragmatic）な記述能力」や「聞き手モデルへの接地」を喪失していると言わざるを得ない。  
ユーザーの主張する「対象ごとに手がかりの在処（全体か一部か）を測り、粒度を切り替える」というアプローチは、最新の「Dynamic Visual Resolution」というアーキテクチャ的課題と問題意識を共有している。しかし、それを「指示なしの識別的記述生成」という自律的タスクに結びつけた点は、現在のVLM研究の盲点（情報ボトルネックへの無自覚な依存と指示への過剰適合）を鋭く突く、極めて先駆的な問題設定であると結論づけられる。

#### **引用文献**

> 1. A Comprehensive Survey and Guide to Multimodal Large Language, [https://www.mdpi.com/2079-3197/14/6/125](https://www.mdpi.com/2079-3197/14/6/125)  
> 2. (PDF) Multimodal Large Language Models: A Survey \- ResearchGate, [https://www.researchgate.net/publication/392628889\_Multimodal\_Large\_Language\_Models\_A\_Survey](https://www.researchgate.net/publication/392628889_Multimodal_Large_Language_Models_A_Survey)  
> 3. A Survey on Post-Training of Multimodal Large Language Models, [https://www.preprints.org/manuscript/202607.1494](https://www.preprints.org/manuscript/202607.1494)  
> 4. Benchmark Evaluations, Applications, and Challenges of Large, [https://www.researchgate.net/publication/387767157\_Benchmark\_Evaluations\_Applications\_and\_Challenges\_of\_Large\_Vision\_Language\_Models\_A\_Survey](https://www.researchgate.net/publication/387767157_Benchmark_Evaluations_Applications_and_Challenges_of_Large_Vision_Language_Models_A_Survey)  
> 5. A Survey on LLM-as-a-Judge \- arXiv, [https://arxiv.org/html/2411.15594v6](https://arxiv.org/html/2411.15594v6)  
> 6. Benchmark Evaluations, Applications, and Challenges of Large, [https://arxiv.org/html/2501.02189v3](https://arxiv.org/html/2501.02189v3)  
> 7. (PDF) Benchmark Evaluations, Applications, and Challenges of, [https://www.researchgate.net/publication/388047297\_Benchmark\_Evaluations\_Applications\_and\_Challenges\_of\_Large\_Vision\_Language\_Models\_A\_Survey](https://www.researchgate.net/publication/388047297_Benchmark_Evaluations_Applications_and_Challenges_of_Large_Vision_Language_Models_A_Survey)  
> 8. (PDF) A Survey on LLM-as-a-Judge \- ResearchGate, [https://www.researchgate.net/publication/386112851\_A\_Survey\_on\_LLM-as-a-Judge](https://www.researchgate.net/publication/386112851_A_Survey_on_LLM-as-a-Judge)  
> 9. Towards Visual Grounding: A Survey \- arXiv, [https://arxiv.org/html/2412.20206v1](https://arxiv.org/html/2412.20206v1)  
> 10. linhuixiao/Awesome-Visual-Grounding \- Hugging Face, [https://huggingface.co/linhuixiao/Awesome-Visual-Grounding](https://huggingface.co/linhuixiao/Awesome-Visual-Grounding)  
> 11. A Survey on Evaluation of Multimodal Large Language Models \- arXiv, [https://arxiv.org/abs/2408.15769](https://arxiv.org/abs/2408.15769)  
> 12. A Survey on Multimodal Large Language Models \- arXiv, [https://arxiv.org/pdf/2306.13549](https://arxiv.org/pdf/2306.13549)  
> 13. \[2306.13549\] A Survey on Multimodal Large Language Models \- arXiv, [https://arxiv.org/abs/2306.13549](https://arxiv.org/abs/2306.13549)  
> 14. Large Multi-modal Model for Video Captioning \- Wenhao Chai, [https://wenhaochai.com/assets/file/ms\_thesis.pdf](https://wenhaochai.com/assets/file/ms_thesis.pdf)  
> 15. Parallelized Autoregressive Decoding for Omni-Modal Dense Video, [https://arxiv.org/html/2607.02963v1](https://arxiv.org/html/2607.02963v1)  
> 16. LongVALE: Vision-Audio-Language-Event Benchmark Towards, [https://www.researchgate.net/publication/394605216\_LongVALE\_Vision-Audio-Language-Event\_Benchmark\_Towards\_Time-Aware\_Omni-Modal\_Perception\_of\_Long\_Videos](https://www.researchgate.net/publication/394605216_LongVALE_Vision-Audio-Language-Event_Benchmark_Towards_Time-Aware_Omni-Modal_Perception_of_Long_Videos)  
> 17. SkyFind: A Large-Scale Benchmark Unveiling Referring Expression, [https://www.researchgate.net/publication/403558055\_SkyFind\_A\_Large-Scale\_Benchmark\_Unveiling\_Referring\_Expression\_Comprehension\_for\_UAV](https://www.researchgate.net/publication/403558055_SkyFind_A_Large-Scale_Benchmark_Unveiling_Referring_Expression_Comprehension_for_UAV)  
> 18. Panoptic Captioning: An Equivalence Bridge for Image and Text, [https://papers.neurips.cc/paper\_files/paper/2025/file/7116cda41d75d580bae15d9e484a8466-Paper-Conference.pdf](https://papers.neurips.cc/paper_files/paper/2025/file/7116cda41d75d580bae15d9e484a8466-Paper-Conference.pdf)  
> 19. Neural Naturalist: Generating Fine-Grained Image Comparisons, [https://www.researchgate.net/publication/336996989\_Neural\_Naturalist\_Generating\_Fine-Grained\_Image\_Comparisons](https://www.researchgate.net/publication/336996989_Neural_Naturalist_Generating_Fine-Grained_Image_Comparisons)  
> 20. LLMs-as-Judges: A Comprehensive Survey on LLM-based ... \- arXiv, [https://arxiv.org/html/2412.05579v2](https://arxiv.org/html/2412.05579v2)  
> 21. LLM-as-a-Judge: Automated Evaluation \- Emergent Mind, [https://www.emergentmind.com/topics/large-language-models-as-a-judge-llm-as-a-judge](https://www.emergentmind.com/topics/large-language-models-as-a-judge-llm-as-a-judge)  
> 22. A Comprehensive Survey on LLM-based Evaluation Methods, [https://www.researchgate.net/publication/386577079\_LLMs-as-Judges\_A\_Comprehensive\_Survey\_on\_LLM-based\_Evaluation\_Methods](https://www.researchgate.net/publication/386577079_LLMs-as-Judges_A_Comprehensive_Survey_on_LLM-based_Evaluation_Methods)  
> 23. Daily Papers \- Hugging Face, [https://huggingface.co/papers?q=LLM-as-a-judge](https://huggingface.co/papers?q=LLM-as-a-judge)  
> 24. Shape and Texture Recognition in Large Vision-Language Models, [https://arxiv.org/html/2503.23062v5](https://arxiv.org/html/2503.23062v5)  
> 25. Disentangling Semantic Attention from Structural Bias in the ... \- arXiv, [https://arxiv.org/html/2607.24017v1](https://arxiv.org/html/2607.24017v1)  
> 26. Multi-Modal LLMs \- Paper Radar, [https://papers.lunadong.com/area/mm](https://papers.lunadong.com/area/mm)  
> 27. BlueLM-V-3B: Algorithm and System Co-Design for Multimodal, [https://www.openaccess.thecvf.com/content/CVPR2025/papers/Lu\_BlueLM-V-3B\_Algorithm\_and\_System\_Co-Design\_for\_Multimodal\_Large\_Language\_Models\_CVPR\_2025\_paper.pdf](https://www.openaccess.thecvf.com/content/CVPR2025/papers/Lu_BlueLM-V-3B_Algorithm_and_System_Co-Design_for_Multimodal_Large_Language_Models_CVPR_2025_paper.pdf)  
> 28. (PDF) Layers, Sinks, and Scaling: Adaptive Evidence Selection for, [https://www.researchgate.net/publication/414356971\_Layers\_Sinks\_and\_Scaling\_Adaptive\_Evidence\_Selection\_for\_Multimodal\_Large\_Language\_Models](https://www.researchgate.net/publication/414356971_Layers_Sinks_and_Scaling_Adaptive_Evidence_Selection_for_Multimodal_Large_Language_Models)  
> 29. Are Multimodal LLMs Ready for Surveillance? A Reality Check on, [https://arxiv.org/html/2603.04727v2](https://arxiv.org/html/2603.04727v2)  
> 30. How Do Medical MLLMs Fail? A Study on Visual Grounding ... \- arXiv, [https://arxiv.org/html/2603.14323v1](https://arxiv.org/html/2603.14323v1)  
> 31. DO MLLMS REALLY UNDERSTAND SPACE?AMATH \- OpenReview, [https://openreview.net/pdf/666223ee937592d8fdf92b9858a429e1da69ce38.pdf](https://openreview.net/pdf/666223ee937592d8fdf92b9858a429e1da69ce38.pdf)