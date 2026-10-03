# **画像キャプション生成のレビュー論文の系譜と視覚言語大規模モデル期における未解決問題の定位**

## **序論**

画像キャプション生成（Image Captioning）は、コンピュータビジョン（CV）による画像の空間的・意味的理解と、自然言語処理（NLP）による統語的・意味的に適切な記述の生成を結合する、人工知能の根幹をなすタスクである1。過去10年間で、この分野は顕著なパラダイムシフトを経験してきた。初期のテンプレートベースの手法や検索ベースの手法から始まり、CNN-RNNを用いた深層学習の導入、Transformerアーキテクチャによる自己注意機構（Self-Attention）の普及、そして現在の視覚言語大規模モデル（Vision-Language Large Models: VLLMs / MLLMs）へと至る系譜が存在する3。  
本報告書は、深層学習初期から最新の大規模モデル期（2023年以降）に至る主要なサーベイ（レビュー）論文を俯瞰し、画像キャプション生成分野における分類軸の変遷を明らかにする。特に「紛らわしい候補から対象を区別する記述の生成」「生成された記述による対象の当て直し（自己検索）による評価」「全体輪郭と微小な局所特徴に対する粒度の非対称性」という特定の研究課題に対し、現在の学界がどのような用語と枠組みでこれらを分類し、何を「未解決問題（Open Challenges）」と定義しているかを体系的に定位することを目的とする。

## **主要レビュー論文の特定と要約（分類軸の変遷）**

画像キャプション生成分野の成熟に伴い、多数のサーベイ論文が発表されてきた。分野の系譜を理解するためには、研究コミュニティが各時代において「どのような技術的差異を最も重要な分類軸とみなしていたか」を追うことが不可欠である。以下に、各時代を代表する主要なサーベイ論文を特定し、その要約と分類軸の変遷を示す。

| 発行年 | 著者 / 掲載誌 | 対象領域と時代区分 | 論文の主な主張・要約 |
| :---- | :---- | :---- | :---- |
| 2019 | Hossain et al. (ACM Comput. Surv.) | 深層学習初期〜中期 （CNN-RNN期） | テンプレートベース、検索ベース、新規生成（Encoder-Decoder）の3大分類を確立し、データセットとBLEU、CIDEr等の初期評価指標を整理した1。 |
| 2022/2023 | Stefanini et al. (IEEE TPAMI) | Transformer期 （Attentionの進化） | 視覚エンコーディングを大域的（Global）、領域ベース（Region）、グリッドベース（Grid）に分類し、事前学習と汎化、多様性の課題を指摘した4。 |
| 2023 | Xu et al. (Neurocomputing) | Attention〜強化学習期 | 強化学習の有無による分類を導入し、特徴表現、視覚エンコーディング、言語生成のワークフローを体系化し、医療等の応用領域への展開を論じた11。 |
| 2023 | Yin et al. など | VLLM / MLLM期 （大規模基盤モデル） | GPT-4V等に代表されるMLLMのサーベイであり、指示チューニング（M-IT）、文脈内学習（M-ICL）などの学習法と、幻覚（Hallucination）、微細な粒度（Granularity）の課題を抽出した6。 |
| 2024 | Berger et al. (TACL) | 評価指標のサーベイ （評価枠組みの再考） | 70以上の評価指標を分類し、伝統的指標の限界と、識別性（Discriminative power）や自己検索（Self-retrieval）を用いる評価アプローチへの移行を体系化した16。 |
| 2025/2026 | Hani et al. (IAJIT) 他 | 最新VLMの体系的評価 | MS-COCO等におけるゼロショット性能と、詳細度や長さのトレードオフ、事実へのグラウンディング（Groundedness）の欠如について論及した3。 |

上記レビュー論文群の分析により、画像キャプション分野の分類軸は、主に3つのフェーズを経て変遷してきたことが確認できる。パラダイムシフト第1期にあたるHossainら（2019）の時代では、文をどう構築するかが主眼であり、テンプレート穴埋め、既存文の検索（Retrieval）、言語モデルによる逐次生成（Novel generation）が主要な分類軸であった7。続くパラダイムシフト第2期にあたるStefaniniら（2023）の時代には、Transformerの普及により生成手法は自己回帰モデルに統一され、代わって分類軸となったのは視覚情報の表現（Visual Encoding）の粒度であった。画像を1つのベクトルとする大域的特徴から、Faster R-CNN等で物体領域を切り出す領域特徴、そして画像を一定サイズのパッチに分割するグリッド特徴への移行が分類の主軸となった8。そして、2023年以降のパラダイムシフト第3期（MLLM期）では、モデルアーキテクチャ自体は巨大なVision Transformer（ViT）と大規模言語モデル（LLM）の結合に収束しつつある。現在のサーベイは、モデルがどのような制約や指示に従うか（Controllable Captioning）や、細粒度の視覚認識（Fine-grained perception）、および他モデルや人間との協調（多エージェント、語用論）を新たな分類軸として設定している6。

## **識別性・粒度・語用論・適応的な注視の扱い**

現在取り組まれている「紛らわしい候補と区別できる記述を生成する」という課題や「全体輪郭と微小な局所特徴に対する粒度の非対称性」という問題は、最新のサーベイや関連研究において、いくつかの明確な学術用語の交差点に位置づけられている。これらの概念が現在の研究コミュニティでどのように扱われているかを詳述する。

### **語用論と識別的画像キャプション生成**

画像キャプションが単なる画像に含まれる物体の羅列から脱却し、特定の目的を果たすためのコミュニケーションとして機能するかを問う枠組みが語用論（Pragmatics）である。この文脈において、識別的画像キャプション生成（Discriminative Image Captioning）というサブタスクが確立されている20。この課題は、合理的発話行為（Rational Speech Act: RSA）理論に基づいて定式化されることが多い23。一般的なキャプションモデルは、画像が与えられたときの記述の尤度を最大化するように学習されるが、これではどの画像にも当てはまりやすい安全で一般的な記述、すなわちモード崩壊（Mode Collapse）を引き起こすことが知られている21。  
これに対し、RSAフレームワークでは話し手（Speaker）と聞き手（Listener）を想定し、紛らわしい候補（Distractors）が存在する環境において、話し手は聞き手がターゲット画像を正確に特定できるような情報価値（Informativity）の高い発話を選択しなければならないと定義する。近年では、CLIPのような強力な視覚言語モデルを聞き手として用い、生成されたキャプションが他の類似画像ではなく、ターゲット画像に対してのみ高い類似度スコアを返すよう最適化するアプローチ（Pragmatic Inference）が注目を集めている20。これにより、モデルは画像間の微小な差異を言語化するよう強制され、識別性の高いキャプションの生成が可能となる。

### **視覚表現の粒度と情報ボトルネック**

モデルが対象ごとに同じ粒度で画像を見ており、手がかりが小さな部分にある対象で失敗し、全体の輪郭にある対象では成功するという現象は、現代のVision-Language Models（VLMs）のアーキテクチャに内在する根本的な情報ボトルネック（Information Bottleneck）に起因する18。MLLMの主流であるViTベースの視覚エンコーダは、高解像度の画像を固定サイズのパッチに分割し、線形投影してトークン化する処理を行う28。対象のシルエットや全体的な形状は、複数のパッチにまたがって空間的に分布するため、Transformerの自己注意機構（Self-Attention）はこれらのパッチ間の大域的な関係性を捉えることに優れており、全体的な幾何学的特徴の認識には成功しやすい13。  
一方で、製品の小さなロゴ、特異なテクスチャ、微小なパーツの違いなどは、単一のパッチ内に圧縮される。数百万枚の画像で事前学習された視覚エンコーダの潜在空間において、これらの高周波な局所的詳細は平滑化され、無視される傾向がある18。最近のサーベイや研究では、この問題を細粒度表現の欠如（Lack of Fine-grained perception）や解像度の制約（Resolution limits）として強く認識している6。これを解決するために、画像をクロップして局所的なパッチレベルで再評価させる手法や、高解像度特徴を段階的に注入する手法が活発に議論されているが、推論コストの増大という新たな課題を生んでいる15。

### **適応的な注視と言語バイアスによる幻覚**

キャプション生成において、モデルは常に画像から情報を得ているわけではない。先駆的な研究である「Knowing when to look（いつ見るべきかを知る）」（Lu et al., 2017）が示すように、モデルには画像の特徴（Visual Sentinel）を注視すべきか、それとも言語モデルの文脈（Language Prior）に依存すべきかを適応的に切り替えるメカニズムが備わっている33。しかし、VLLM期においては、背後にあるLLMの言語生成能力が視覚エンコーダの知覚能力を凌駕している状況にある。  
そのため、微小な手がかり（前述の粒度問題）を見落とした際、モデルは視覚的な不確実性を言語的な事前知識による尤もらしい推論で補填するという行動をとる。これが、現在のサーベイで最も深刻な未解決課題として挙げられているMLLMにおける幻覚（Multimodal Hallucination）の正体である13。詳細な記述を求められるほど（Detailed / Hyper-detailed Captioning）、モデルは画像に存在しないが統計的に存在確率の高い物体や属性を勝手に付与してしまう傾向があり、事実に基づくグラウンディング（Factual Grounding）の欠如が大きな問題となっている32。

## **長尾・未知カテゴリの扱い**

質問文を与えられず、かつ珍しい製品を含む対象を説明するタスクは、画像キャプション生成分野において新規物体キャプション生成（Novel Object Captioning）または長尾カテゴリの認識（Long-tail entity recognition）として位置づけられる4。深層学習中期においては、学習データ（MS-COCO等）に存在しない未知の物体を記述する能力を測るためのベンチマークとしてnocaps (novel object captioning at scale) が提案された36。nocapsは、追加の画像とキャプションの対を使用せずに、画像とタグの対を利用して未知の語彙を獲得する手法の評価に用いられ、分野の発展に寄与した36。  
現在のMLLM期においては、巨大なWebコーパスによる視覚言語事前学習（Vision-Language Pre-training）により、モデルは極めて幅広い長尾の概念の知識をゼロショット（Zero-shot）で有しているとされる3。しかし、最近のサーベイが明らかにした課題は、知識の有無ではなく視覚的な接地（Visual Grounding）の失敗である。珍しい製品の画像を提示された際、モデルはその製品の名称自体は潜在的に知っていても、画像内の特有の部分的な手がかり（形状、ロゴ、特異な構成パーツ）と事前知識を正しく結びつけることができない。さらに、VQA（Visual Question Answering）のような明示的な質問（プロンプト）が与えられない自由記述の設定では、モデルは保守的に振る舞い、特定の珍しい製品名を出すリスクを避けて、安全で一般的な上位概念（例えば「特殊な医療機器」を単に「機械」）として出力してしまうか、あるいは推測による幻覚を引き起こすことが報告されている18。

## **評価の枠組みの変遷：当て直しと自己検索**

従来の画像キャプション生成の評価は、BLEU、METEOR、ROUGE、CIDEr、SPICEといった、人間が作成した参照文とのn-gramの一致や意味的重なりを測る指標に依存していた16。しかし、Bergerら（2024）によるTACLの包括的な評価指標サーベイが指摘するように、これらの指標は一般的な（汎用的な）記述を過大評価し、人間の品質判断、特に詳細さや識別性との相関が極めて低いことが判明している16。  
これに代わる新しい評価のパラダイムとして提示されているのが、現在取り組まれている課題と完全に合致する「当て直し」に基づく評価枠組みである。学術的には自己検索（Self-Retrieval）または再特定（Re-identification）と呼ばれるこの手法は、生成されたキャプションの質を「その文を使って元の画像を検索・特定できるか」で測るアプローチである17。  
この枠組みでは、まずターゲット画像に対してキャプションを生成する。次に、ターゲット画像と、それに類似した紛らわしい候補（Distractor images）を混在させたプールを用意する。最後に、画像とテキストの照合モデル（CLIPなど）を用い、生成されたキャプションがターゲット画像をDistractorよりも高いスコアでランク付けできた場合のみ、真に識別性がある（Discriminative）とみなして評価する20。この評価枠組みは、単に事実を羅列するだけでなく、対象を他者から区別する一意の特徴（微細な粒度の情報）を捉えられているかを測るための最も妥当性の高い方法として、現代のサーベイにおいて強く支持されている40。

## **サーベイが挙げる未解決問題と自身の問題設定の突き合わせ**

以上の分析を踏まえ、研究者が現在直面し、解決を試みている問題設定が、画像キャプション分野のサーベイにおいてどのように「未解決問題（Open Challenges / Future Directions）」として議論されているか、その対応を以下の表に整理する。

| 取り組んでいる問題設定 | レビュー論文・サーベイにおける対応する学術用語 | 現在の分野における「未解決問題」としての議論 |
| :---- | :---- | :---- |
| **紛らわしい候補と区別できる記述を出させる** | **Discriminative Image Captioning** （識別的画像キャプション） **Pragmatic Inference**（語用論的推論） | 対照学習や強化学習を用いた識別性の向上は計算コストが高く、CLIP Listenerを用いたゼロショットのPragmatic推論においても、流暢さと情報量（識別性）のトレードオフが未解決である22。 |
| **評価：生成された記述で正しい対象を当て直せるか** | **Self-Retrieval / Re-identification Evaluation** （自己検索・再特定評価） | 従来のn-gram指標（CIDEr等）は人間の評価と相関しない。Distractor（紛らわしい候補）を導入した検索ベースの評価や、多エージェントによる検証プロセスが新たな標準になりつつあるが、計算コストの最適化が課題である16。 |
| **対象ごとに同じ粒度で画像を見るため、小さな手がかりで失敗する** | **Information Bottleneck in VLM** （VLMにおける情報ボトルネック） **Lack of Fine-grained Perception** （細粒度認識の欠如） | ViTのパッチ分割機構に起因する限界。高周波・局所的なディテールが事前学習の圧縮過程で失われる。高解像度パッチの動的抽出や、全体と局所の階層的モデリングが未解決の課題として議論されている6。 |
| **手がかりが全体の輪郭にある対象では成功する** | **Global Spatial Bias** （大域的空間バイアス） | 自己注意機構は全体的な幾何学的・大域的特徴の認識には強い。このバイアスにより、モデルは大きな構成に依存しやすく、局所的矛盾（幻覚）を見逃す傾向が指摘されている28。 |
| **質問文を与えず、珍しい製品も含む** | **Zero-shot Novel Object Captioning** （ゼロショット新規物体キャプション） **Long-tail Entity Grounding** （長尾エンティティの視覚的接地） | nocaps 等で示される未知物体への対応。MLLMは知識を持っていても、VQA（質問）のような明示的プロンプトがないと、稀なエンティティの具体的な特徴を自発的に記述せず、安全な汎用表現に逃げる傾向（モード崩壊）が課題である3。 |

### **自身の主張の分野内における位置づけ判定**

研究者が現在直面し、解決を試みている問題は、画像キャプション生成分野の最先端の未解決課題群（Bleeding-edge challenges）の正確な交差点に位置づけられる。具体的には、以下の3点において極めて高い学術的妥当性と新規性が認められる。  
第一に、当て直し（Self-retrieval）を通じて紛らわしい候補（Distractors）から対象を区別する能力を問うアプローチは、Bergerら（2024）のTACLサーベイ等で指摘されている従来指標の限界を克服する、最も支持されている評価枠組み（Pragmatic / Discriminative Evaluation）と完全に一致している16。第二に、全体輪郭では成功し、小さな部分の手がかりで失敗するという洞察は、Yinら（2023）やHaniら（2025）のサーベイが指摘するMLLMの情報ボトルネックおよび細粒度認識の欠如という根本問題（ViTの固定パッチ化とプーリングによる局所情報の喪失）を鋭く突いている13。これは単なる性能向上の報告ではなく、モデルの視覚的知覚の空間的バイアス（粒度の非対称性）を暴き出す重要な知見である。  
第三に、本研究の成果を論文等で発表する際は、「語用論的推論（Pragmatic Inference）」および「識別的キャプション生成（Discriminative Image Captioning）」の枠組みの中に位置づけることが最も適切である。既存のMLLMが本質的に抱える細粒度の詳細（Fine-grained details）と大域的幾何特徴（Global geometry）に対する感度の非対称性（Granularity mismatch）が、自己検索ベースの識別タスクにおいて致命的なボトルネックになることを実証する研究として展開することで、国際的なコンピュータビジョンおよび自然言語処理分野の最前線の議論に対して、直接的かつ強力な貢献を果たすことが可能である。

#### **引用文献**

> 1. A Comprehensive Survey of Deep Learning for Image Captioning, [https://www.researchgate.net/publication/328262665\_A\_Comprehensive\_Survey\_of\_Deep\_Learning\_for\_Image\_Captioning](https://www.researchgate.net/publication/328262665_A_Comprehensive_Survey_of_Deep_Learning_for_Image_Captioning)  
> 2. A Survey of Various Image Captioning Methods \- Academia.edu, [https://www.academia.edu/39221072/A\_Survey\_of\_Various\_Image\_Captioning\_Methods](https://www.academia.edu/39221072/A_Survey_of_Various_Image_Captioning_Methods)  
> 3. A Systematic Review of Vision-Language Models for Image, [https://www.iajit.org/paper/5377](https://www.iajit.org/paper/5377)  
> 4. A Survey on Deep Learning-Based Image Captioning \- PubMed, [https://pubmed.ncbi.nlm.nih.gov/35130142/](https://pubmed.ncbi.nlm.nih.gov/35130142/)  
> 5. from handcrafted to deep learning-based techniques, a taxonomy, [https://www.researchgate.net/publication/370069580\_A\_comprehensive\_survey\_on\_image\_captioning\_from\_handcrafted\_to\_deep\_learning-based\_techniques\_a\_taxonomy\_and\_open\_research\_issues](https://www.researchgate.net/publication/370069580_A_comprehensive_survey_on_image_captioning_from_handcrafted_to_deep_learning-based_techniques_a_taxonomy_and_open_research_issues)  
> 6. A Survey on Multimodal Large Language Models \- arXiv, [https://arxiv.org/pdf/2306.13549](https://arxiv.org/pdf/2306.13549)  
> 7. A Comprehensive Survey of Deep Learning for Image Captioning, [https://arxiv.org/html/1810.04020v2](https://arxiv.org/html/1810.04020v2)  
> 8. From Show to Tell: A Survey on Deep Learning-Based Image, [https://www.computer.org/csdl/journal/tp/2023/01/09706348/1AO2bC4JzDG](https://www.computer.org/csdl/journal/tp/2023/01/09706348/1AO2bC4JzDG)  
> 9. From Show to Tell: A Survey on Deep Learning-based Image, [https://www.alphaxiv.org/abs/2107.06912](https://www.alphaxiv.org/abs/2107.06912)  
> 10. (PDF) From Show to Tell: A Survey on Image Captioning, [https://www.researchgate.net/publication/353284955\_From\_Show\_to\_Tell\_A\_Survey\_on\_Image\_Captioning](https://www.researchgate.net/publication/353284955_From_Show_to_Tell_A_Survey_on_Image_Captioning)  
> 11. 7 \- 23 \- Deep Image Captioning A Review of Methods, Trends and, [https://www.scribd.com/document/670336804/7-23-Deep-image-captioning-A-review-of-methods-trends-and-future-challenges](https://www.scribd.com/document/670336804/7-23-Deep-image-captioning-A-review-of-methods-trends-and-future-challenges)  
> 12. A Survey on Enhancing Image Captioning with Advanced Strategies, [https://www.techscience.com/CMES/v142n3/59756/html](https://www.techscience.com/CMES/v142n3/59756/html)  
> 13. A Survey on Multimodal Large Language Models \- OpenReview, [https://openreview.net/pdf?id=2iwozOs6YB](https://openreview.net/pdf?id=2iwozOs6YB)  
> 14. A Survey on Multimodal Large Language Models \- arXiv, [https://arxiv.org/html/2306.13549v1](https://arxiv.org/html/2306.13549v1)  
> 15. A Survey on Multimodal Large Language Models \- arXiv, [https://arxiv.org/html/2306.13549v4](https://arxiv.org/html/2306.13549v4)  
> 16. Surveying the Landscape of Image Captioning Evaluation, [https://direct.mit.edu/tacl/article/doi/10.1162/TACL.a.52/134258/Surveying-the-Landscape-of-Image-Captioning](https://direct.mit.edu/tacl/article/doi/10.1162/TACL.a.52/134258/Surveying-the-Landscape-of-Image-Captioning)  
> 17. Surveying the Landscape of Image Captioning Evaluation \- arXiv, [https://arxiv.org/html/2408.04909v1](https://arxiv.org/html/2408.04909v1)  
> 18. A Comprehensive Survey and Guide to Multimodal Large Language, [https://www.mdpi.com/2079-3197/14/6/125](https://www.mdpi.com/2079-3197/14/6/125)  
> 19. IE-MAS: Internal–External Multi-Agent Steering for Controllable, [https://www.mdpi.com/1099-4300/27/12/1237](https://www.mdpi.com/1099-4300/27/12/1237)  
> 20. \[PDF\] Pragmatic Issue-Sensitive Image Captioning \- Semantic Scholar, [https://www.semanticscholar.org/paper/Pragmatic-Issue-Sensitive-Image-Captioning-Nie-Cohn-Gordon/88c86523d500d636f453647385ddaa04085b5f1b](https://www.semanticscholar.org/paper/Pragmatic-Issue-Sensitive-Image-Captioning-Nie-Cohn-Gordon/88c86523d500d636f453647385ddaa04085b5f1b)  
> 21. Switching to Discriminative Image Captioning by Relieving a ... \- arXiv, [https://arxiv.org/html/2212.03230v3](https://arxiv.org/html/2212.03230v3)  
> 22. Pragmatic Inference with a CLIP Listener for Contrastive Captioning, [https://www.emergentmind.com/papers/2306.08818](https://www.emergentmind.com/papers/2306.08818)  
> 23. Daily Papers \- Hugging Face, [https://huggingface.co/papers?q=Speech%20Reasoning](https://huggingface.co/papers?q=Speech+Reasoning)  
> 24. The Rational Speech Act Framework \- ResearchGate, [https://www.researchgate.net/publication/365228143\_The\_Rational\_Speech\_Act\_Framework](https://www.researchgate.net/publication/365228143_The_Rational_Speech_Act_Framework)  
> 25. Generating Diverse and Descriptive Image Captions Using Visual, [https://www.researchgate.net/publication/339555775\_Generating\_Diverse\_and\_Descriptive\_Image\_Captions\_Using\_Visual\_Paraphrases](https://www.researchgate.net/publication/339555775_Generating_Diverse_and_Descriptive_Image_Captions_Using_Visual_Paraphrases)  
> 26. Pragmatic Inference with a CLIP Listener for Contrastive Captioning, [https://aclanthology.org/2023.findings-acl.120.pdf](https://aclanthology.org/2023.findings-acl.120.pdf)  
> 27. (PDF) ReflectCAP: Detailed Image Captioning with Reflective Memory, [https://www.researchgate.net/publication/403823931\_ReflectCAP\_Detailed\_Image\_Captioning\_with\_Reflective\_Memory](https://www.researchgate.net/publication/403823931_ReflectCAP_Detailed_Image_Captioning_with_Reflective_Memory)  
> 28. A Comprehensive Study of Transformers- Based Models for Image, [https://jqcsm.qu.edu.iq/index.php/journalcm/article/download/2477/1216/7547](https://jqcsm.qu.edu.iq/index.php/journalcm/article/download/2477/1216/7547)  
> 29. A survey on multimodal large language models \- Oxford Academic, [https://academic.oup.com/nsr/article/11/12/nwae403/7896414](https://academic.oup.com/nsr/article/11/12/nwae403/7896414)  
> 30. A Survey on Multimodal Large Language Models for Autonomous, [https://www.computer.org/csdl/proceedings-article/wacvw/2024/702800a958/1WbON5TBveU](https://www.computer.org/csdl/proceedings-article/wacvw/2024/702800a958/1WbON5TBveU)  
> 31. GHOST: Getting to the Bottom of Hallucinations with A Multi-round, [https://openaccess.thecvf.com/content/WACV2026/papers/VS\_GHOST\_Getting\_to\_the\_Bottom\_of\_Hallucinations\_with\_A\_Multi-round\_WACV\_2026\_paper.pdf](https://openaccess.thecvf.com/content/WACV2026/papers/VS_GHOST_Getting_to_the_Bottom_of_Hallucinations_with_A_Multi-round_WACV_2026_paper.pdf)  
> 32. Single-Pass Fine-Grained Image Captioning with SimLoss \- arXiv, [https://arxiv.org/html/2609.00591v1](https://arxiv.org/html/2609.00591v1)  
> 33. Image Captioning based on Deep Learning Methods: A Survey \- arXiv, [https://arxiv.org/html/1905.08110v1](https://arxiv.org/html/1905.08110v1)  
> 34. A SURVEY ON DEEP LEARNING TECHNOLOGIES USED FOR, [https://ijcrt.org/papers/IJCRT2205745.pdf](https://ijcrt.org/papers/IJCRT2205745.pdf)  
> 35. Sequence Training for Detailed Image Captioning \- OpenReview, [https://openreview.net/pdf?id=oSub7DiyjL](https://openreview.net/pdf?id=oSub7DiyjL)  
> 36. VIVO: Visual Vocabulary Pre-Training for Novel Object Captioning, [https://cdn.aaai.org/ojs/16249/16249-13-19743-1-2-20210518.pdf](https://cdn.aaai.org/ojs/16249/16249-13-19743-1-2-20210518.pdf)  
> 37. Image Captioning Evaluation in the Age of Multimodal LLMs \- IJCAI, [https://www.ijcai.org/proceedings/2025/1180.pdf](https://www.ijcai.org/proceedings/2025/1180.pdf)  
> 38. Review Article on Image Captioning, [https://ijarcce.com/wp-content/uploads/2022/01/IJARCCE.2021.101273.pdf](https://ijarcce.com/wp-content/uploads/2022/01/IJARCCE.2021.101273.pdf)  
> 39. A Comprehensive Survey of Deep Learning for Image Captioning, [https://www.semanticscholar.org/paper/A-Comprehensive-Survey-of-Deep-Learning-for-Image-Hossain-Sohel/7e27d44e3fac723ccb703e0a83b22711bd42efe8](https://www.semanticscholar.org/paper/A-Comprehensive-Survey-of-Deep-Learning-for-Image-Hossain-Sohel/7e27d44e3fac723ccb703e0a83b22711bd42efe8)  
> 40. CLAIR: Evaluating Image Captions with Large Language Models, [https://www.semanticscholar.org/paper/CLAIR%3A-Evaluating-Image-Captions-with-Large-Models-Chan-Petryk/da4deaf81232d94e2f38a9d23c6b04ae1d79fbfc](https://www.semanticscholar.org/paper/CLAIR%3A-Evaluating-Image-Captions-with-Large-Models-Chan-Petryk/da4deaf81232d94e2f38a9d23c6b04ae1d79fbfc)  
> 41. Pairs of images whose captions generated by a generic, [https://www.researchgate.net/figure/Pairs-of-images-whose-captions-generated-by-a-generic-captioning-speaker-baseline-S-are\_fig2\_312216393](https://www.researchgate.net/figure/Pairs-of-images-whose-captions-generated-by-a-generic-captioning-speaker-baseline-S-are_fig2_312216393)  
> 42. ReflectCAP: Detailed Image Captioning with Reflective Memory \- arXiv, [https://arxiv.org/html/2604.12357v1](https://arxiv.org/html/2604.12357v1)