# 画像キャプション生成サーベイの系譜と、識別的キャプション課題の位置づけ

## TL;DR
- 画像キャプション生成のサーベイは、深層学習初期（Bernardi et al. 2016 JAIR、Hossain et al. 2019 ACM CSUR）→ Transformer 期（Stefanini et al. 2022 TPAMI「From Show to Tell」、Ghandi et al. 2023 ACM CSUR）→ 視覚言語大規模モデル期（2023年以降、主に arXiv／二次誌）と三世代に分けられ、分類軸は「生成 vs 検索」「手法カテゴリ列挙」から「視覚エンコーダ／言語モデル／学習戦略」の直交軸へと洗練されてきた。
- あなたの課題（似た候補と区別できる名前・記述を出させ、聞き手が正しい対象を当て直せるかで評価する）は、主要サーベイでは**独立章として立てられておらず**、Stefanini らでは「diversity（多様性）」metric と SPICE-U の「uniqueness（一意性）」property の中に、また controllable/novel object captioning の variant の周辺に散在する。最も近い既存名称は **discriminative / distinctive captioning** と **referring expression generation（REG）／語用論（RSA）** だが、後者はキャプションサーベイ本流からほぼ切り離されている。
- 「決め手の手がかりの在り処が対象ごとに異なるのに、モデルは常に同じ粒度で見ている——これを測り対象ごとに見方を切り替える」という主張を**独立した未解決問題として挙げているサーベイは見当たらない**。最も近いのは Stefanini らの「Generalization, diversity, long-tail concepts」と、visual encoding 章の「global 特徴は粒度を欠き fine-grained な記述が難しい」という記述、および controllable captioning の「どこを describe するか」の制御である。

## Key Findings

1. **査読付き主要サーベイは4本が軸**：Bernardi et al. 2016（JAIR、査読付き）、Hossain et al. 2019（ACM CSUR、査読付き）、Stefanini et al. 2022/2023（IEEE TPAMI、査読付き）、Ghandi et al. 2023/2024（ACM CSUR、査読付き）。VLM 期は査読付き総説がまだ確立しておらず、arXiv／二次誌が中心。

2. **分類軸の変遷**：2016（Bernardi）は「description を generation problem とみなすか retrieval problem とみなすか」という概念軸。2019（Hossain）は手法カテゴリの列挙（visual space/multimodal space、supervised/other DL、dense/whole-scene、encoder-decoder/compositional、attention、LSTM/CNN 言語モデル等9分類）。2022（Stefanini）は「visual encoding／language modeling／training strategies」の直交3軸＋variants＋metrics。

3. **識別性・弁別性（distinctiveness/discriminative captioning）**：どの主要サーベイも**独立章にしていない**。Stefanini は "distinctiveness" という語を使わず、"uniqueness"（SPICE-U）と "diversity" metric の中で部分的に扱う。

4. **語用論・聞き手モデル（REG/RSA/speaker-listener）**：キャプションサーベイ本流ではほぼ扱われず、別コミュニティ（REG、object naming）のサーベイ（Silberer et al. 2020 LREC）が担う。

5. **見る場所・粒度の適応制御**：Stefanini では visual encoding 章（global→grid attention→region attention→graph→self-attention）と、controllable captioning variant（ユーザ信号で describe 対象を制御）に分散。「対象ごとに手がかりの粒度が違う」という測定可能な性質としての定式化は未提示。

6. **自己検索評価（self-retrieval / 聞き手による同定）**：標準評価としては**認められていない**。Stefanini は self-retrieval 専用の metric 節を持たず、reference-free の CLIP-S/TIGEr/Coverage を強調。discriminative captioning 文献（Luo et al. 2018、Liu et al. 2018）では retrieval metric が中心的だが、これはサーベイでは周辺的扱い。

7. **長尾・未知カテゴリ**：novel object captioning は Stefanini の variant「Dealing with the lack of training data」に、nocaps（Agrawal et al. 2019 ICCV）が標準ベンチマークとして位置づけられている。

## Details

### 1. レビュー論文の一覧（年代順）

#### (A) 深層学習初期

**Bernardi et al. 2016（JAIR、査読付き）**
- 書誌：R. Bernardi, R. Cakici, D. Elliott, A. Erdem, E. Erdem, N. Ikizler-Cinbis, F. Keller, A. Muscat, B. Plank, "Automatic Description Generation from Images: A Survey of Models, Datasets, and Evaluation Measures," *Journal of Artificial Intelligence Research*, vol. 55, pp. 409–442, 2016. DOI: 10.1613/jair.4900（arXiv:1601.03896）。
- 対象範囲：静止画像への description generation。深層学習台頭直前～初期（2015年頃まで）。テンプレート充填・人手 NLG・検索ベースを含む古典手法が主対象。
- 分類軸：著者自身の言葉で「we classify the existing approaches based on how they conceptualize this problem, viz., models that cast description as either generation problem or as a retrieval problem over a visual or multimodal representational space」（JAIR 版原文）。すなわち **generation vs retrieval** の概念的二分法＋3カテゴリ。
- 未解決問題：future research directions を第4節で議論（評価尺度の改善、データセット、モデルの一般化）。
- 被引用：多数（arXiv/JAIR 版合算で数百規模。scite.ai は約257 citation statements と報告）。

**Hossain et al. 2019（ACM Computing Surveys、査読付き）**
- 書誌：Md. Z. Hossain, F. Sohel, M. F. Shiratuddin, H. Laga, "A Comprehensive Survey of Deep Learning for Image Captioning," *ACM Computing Surveys (CSUR)*, vol. 51, no. 6, Article 118, 36 pp., 2019. DOI: 10.1145/3295748（arXiv:1810.04020）。
- 対象範囲：深層学習ベースのキャプション（2018年頃まで）。
- 分類軸：手法を9カテゴリに列挙——(1) Visual space-based、(2) Multimodal space-based、(3) Supervised learning、(4) Other deep learning、(5) Dense captioning、(6) Whole scene-based、(7) Encoder-Decoder Architecture-based、(8) Compositional Architecture-based、(9) LSTM 等言語モデル別。ペアワイズ比較形式。
- 未解決問題：第6節 future research directions（新奇物体の記述、教師なし・GAN による多様性、評価尺度、grammatically correct な生成のための言語モデル依存性）。特に novel object captioning（rarely-seen と never-seen の区別）を課題として明記。
- 被引用：Semantic Scholar 集計で693 Citations（うち Methods Citations 340、Background 112）。当該分野で最も引用されるサーベイの一つ。

#### (B) Transformer 期

**Stefanini et al. 2022/2023（IEEE TPAMI、査読付き）——本調査の中核**
- 書誌：M. Stefanini, M. Cornia, L. Baraldi, S. Cascianelli, G. Fiameni, R. Cucchiara, "From Show to Tell: A Survey on Deep Learning-based Image Captioning," *IEEE Transactions on Pattern Analysis and Machine Intelligence*, vol. 45, no. 1, pp. 539–559, 2023（online 2022）. DOI: 10.1109/TPAMI.2022.3148210（arXiv:2107.06912）。
- 対象範囲：2015年以降の深層生成モデル（RNN→attention→強化学習→Transformer→BERT 系 early-fusion）。
- 分類軸：**直交3軸**。(II) Visual Encoding = {global CNN features / grid attention / region attention / graph-based / self-attention}、言語モデリング、training strategies = {cross-entropy / masked language model / 強化学習（SCST）/ VL pre-training}。加えて (VII) variants、(V) metrics（standard / diversity / embedding-based / learning-based）。
- Variants（第VII章）：4カテゴリに整理——VII-A「Dealing with the lack of training data」(Novel Object Captioning, Unpaired, Continual)、VII-B「Focusing on the visual input」(Dense Captioning, Text-based/OCR Captioning [TextCaps], Change Captioning)、VII-C「Focusing on the textual output」(Diverse, Multilingual, Application-specific)、VII-D「Addressing user requirements」(Personalized, **Controllable Captioning**, Image Captioning Editing)。
- 未解決問題（第VIII章、3本柱）：(1)「Procedural and architectural challenges」(pre-training データ公開、モデル巨大化への低計算代替、early-fusion vs encoder-decoder の二分)、(2)「Generalization, diversity, long-tail concepts」(ドメイン特化・スタイル、naturalness/diversity、long-tail 概念、novel object/controllable captioning の活用、subword tokenization による稀語対応)、(3)「Design of trustworthy AI solutions」(bias、fairness、interpretability、reference-free 評価・reproducible プロトコル)。
- 被引用：Semantic Scholar が TPAMI 版に対し211 Citations（Methods Citations 111、Results 49）と報告（実際の Google Scholar 値はさらに高いと見られる）。

**Ghandi et al. 2023/2024（ACM Computing Surveys、査読付き）**
- 書誌：T. Ghandi, H. Pourreza, H. Mahyar, "Deep Learning Approaches on Image Captioning: A Review," *ACM Computing Surveys*, vol. 56, no. 3, pp. 1–39, 2024（arXiv:2201.12944, 2022提出）. DOI: 10.1145/3617592。
- 対象範囲：2018年以降を重点に、encoder-decoder／attention／graph-based／Transformer／VLP／強化学習／教師なし。
- 分類軸：method category 別の構造化 taxonomy（Hossain の構造を踏襲しつつ category ごとに独立節）。
- 未解決問題：object hallucination、missing context、illumination、contextual understanding、referring expressions、dataset bias、image-text 情報の misalignment、評価ツールの改善。**referring expressions を challenge として明示的に挙げる数少ないキャプションサーベイ**。
- 被引用：中規模（新しめ）。

#### (C) VLM 大規模モデル期（2023年以降、多くは arXiv／二次誌）
- Sharma & Padha 2023（*Artificial Intelligence Review*, 56(11):13619–13661、査読付き, DOI:10.1007/s10462-023-10488-2）：handcrafted→deep learning、template/retrieval/encoder-decoder の時代区分＋多言語＋open research issues。被引用約32。
- 「Next-generation image captioning: ... from transformers to Multimodal Large Language Models」（*ScienceDirect*, 2025, S2949719125000354）：MLLM（LLaVA、IDEFICS 等）を明示的に扱う。
- 評価特化：「Surveying the Landscape of Image Captioning Evaluation」（TACL 2024/2025、arXiv:2408.04909）、「Image Captioning Evaluation in the Age of Multimodal LLMs」（arXiv:2503.14604）。CHAIR/ALOHa 等の hallucination 尺度、CLIP-S/PAC-S/BRIDGE 等 learnable metric を扱う。
- これらは**査読付き総説として TPAMI/CSUR 級のものはまだ確立していない**点に注意。

### 2. 分類軸の変遷（サーベイごと）

| 世代 | サーベイ | 分類の中核軸 |
|---|---|---|
| 初期 | Bernardi 2016 | 概念軸：generation problem vs retrieval problem |
| 初期 | Hossain 2019 | 手法カテゴリ列挙（9分類、ペアワイズ比較） |
| Transformer | Stefanini 2022 | 直交3軸：visual encoding／language modeling／training strategy ＋ variants ＋ metrics |
| Transformer | Ghandi 2023 | method category ごとの独立節 taxonomy |
| VLM | Sharma&Padha 2023 ほか | 時代区分（template→retrieval→encoder-decoder→VLP/MLLM）＋ open issues |

変遷の本質：「問題の概念化」（2016）→「アーキテクチャの分類学」（2019, 2022, 2023）→「訓練パラダイム・基盤モデルとの接続」（VLM 期）。あなたの課題のような**タスク定義レベルの再構成（識別性を軸に据える）は、どのサーベイの第一分類軸にもなっていない**。

### 3. 4つの論点の対応表

| 論点 | Bernardi 2016 | Hossain 2019 | Stefanini 2022 | Ghandi 2023 |
|---|---|---|---|---|
| **識別性・弁別性（distinctiveness）** | 触れていない | 触れていない | 独立章なし。"uniqueness"（SPICE-U）と diversity metric に埋没 | 触れていない（referring expressions を challenge に列挙するのみ） |
| **記述の粒度・制御（controllable/dense）** | 触れていない | dense captioning を手法カテゴリに含む | variant として Dense（VII-B）と Controllable（VII-D）を明示 | dense/controllable を taxonomy 内で扱う |
| **語用論・聞き手モデル（REG/RSA）** | 触れていない | 触れていない | 触れていない（image retrieval は change captioning の auxiliary task として一度だけ言及） | referring expressions を challenge として名前だけ挙げる |
| **見る場所・粒度の適応制御（attention/region）** | 触れていない | attention を手法カテゴリに含む | visual encoding 章の中核（global→grid→region→graph→self-attention）＋saliency/human attention | attention を taxonomy 内で扱う |

補足（原文根拠）：
- Stefanini は global CNN features について「this paradigm also leads to excessive compression of information and lacks granularity, making it hard for a captioning model to produce specific and fine-grained descriptions」と述べ、粒度不足を明示。これはあなたの「同じ粒度で見る」問題に最も近い記述。
- Controllable captioning は「puts the users in the loop by asking them to select and give priorities to what should be described in an image」——制御信号（領域・visual words・mouse traces）でどこを describe するかを指定。ただし「対象ごとに最適粒度が異なる」ことをモデルが自律的に決める話ではない。
- 語用論について、キャプション文献側（Cohn-Gordon et al. 2018「Pragmatically Informative Image Captioning with Character-Level Inference」、Vedantam et al. 2017「Context-aware captions from context-agnostic supervision」）は RSA の speaker-listener 枠組みで「distractor の中から target を当てさせる」を扱うが、これらはキャプション**サーベイ**には取り込まれていない。REG 側は Silberer, Zarrieß, Boleda 2020「Object Naming in Language and Vision: A Survey and a New Dataset」（LREC 2020）や Schüz et al. の REG レビューが担当し、別分野として切り離されている。

### 4. 自己検索評価と紛らわしい候補の扱い

- **self-retrieval / 聞き手同定を標準評価と認めるサーベイは無い。** Stefanini の metrics 章（V-B）は Standard（BLEU/METEOR/ROUGE/CIDEr/SPICE）、Diversity、Embedding-based、Learning-based の4分類で、self-retrieval 専用節は存在しない。distinctiveness は SPICE-U の "uniqueness" として一文で触れられるのみ。この uniqueness は Wang, Feng, Narasimhan & Russakovsky「Towards Unique and Informative Captioning of Images」（ECCV 2020, arXiv:2009.03949）で「Un(p) = (# images not containing p)/(# images total)」と定義され、著者自身が「This is similar to the notion of inverse document frequency (IDF) in text retrieval」と述べる、テキスト検索の IDF に類似した概念単位の一意性尺度である。
- distinctiveness の背景（generic な記述では似た対象を区別できない）は同 Wang et al. 2020 が明快に述べる：「state of the art image captioning models produce generic captions, leaving out important image details... these systems may even misrepresent the image in order to produce a simpler caption consisting of common concepts」。
- 個別手法群では self-retrieval / listener test が中心的評価：Luo et al. 2018「Discriminability objective for training descriptive captions」（AMT で target/distractor pair の識別テスト）、Liu et al. 2018「Show, Tell and Discriminate: ... Self-retrieval」、Wang & Chan の between-set CIDEr（原論文 verbatim：「although the generated captions can accurately describe the image, they are generic for similar images and lack distinctiveness... we propose a distinctiveness metric—between-set CIDEr (CIDErBtw)」；ECCV 2020 → TPAMI 45(2):2088–2103 に拡張）、および TrueMatch/RD100 のような distractor 集合を用いた最近の評価（"Revisiting Self-Retrieval for Fine-Grained Image Captioning", TMLR 2025）。
- **紛らわしい候補（hard negative / distractor）を含む評価**は、RSA 系（Cohn-Gordon 2018 の distractor 内 target 同定）、group-based distinctive captioning（DifDisCap、CLIP guided group optimization）、および TrueMatch などに存在するが、いずれも**サーベイの標準評価節には昇格していない**。あなたの「8択聞き手テスト」はこの系譜（context-aware / discriminative captioning + listener accuracy）に直接連なる。

### 5. 未解決問題の共通リストと、あなたの主張の判定

複数サーベイが共通して挙げる未解決問題：
1. **一般化・long-tail・novel object**（Hossain, Stefanini, Ghandi）
2. **多様性・naturalness の欠如、safe/generic 出力への偏り**（Stefanini の diversity、Ghandi）
3. **object hallucination・image-text misalignment**（Ghandi、VLM 期サーベイの中心）
4. **評価尺度の不備（reference-based metric が discriminative/長い記述を不当に低評価）**（Bernardi, Stefanini, 評価特化サーベイ）
5. **dataset bias / fairness / interpretability**（Stefanini「trustworthy AI」、Ghandi）
6. **controllability / grounding（どこを describe するか）**（Stefanini variant、Ghandi）

**あなたの主張の判定**：
> 「記述の決め手になる手がかりの在り処（全体の輪郭か、ごく一部か）は対象ごとに異なるのに、モデルは常に同じ粒度で見ている。この性質を測り、対象ごとに見方を切り替える」

- **独立した未解決課題として挙げているサーベイは存在しない。**
- 最も近い既存課題名は、優先順に：
  1. **Fine-grained / distinctive (discriminative) captioning**——「generic な記述では似た対象を区別できない」問題。あなたの評価（聞き手同定）と直結。ただしサーベイでは metric property（uniqueness/diversity）に留まる。
  2. **Adaptive attention / where-to-look 制御**——Stefanini の visual encoding 章。「global は粒度不足」という認識はあるが「対象ごとに最適粒度を切り替える」定式化は無い。関連個別手法に adaptive attention（Lu et al. "Knowing when to look"）や visual sentinel、task-adaptive attention がある。
  3. **Long-tail / novel object captioning**——珍しい製品＝事前学習に現れない対象、という側面。nocaps がベンチマーク。
  4. **Referring expression generation の pragmatics（RSA）**——「聞き手が当て直せる記述」という評価哲学の源流。キャプションサーベイ外。

すなわちあなたの貢献は、これら分散した4系譜（distinctiveness＋adaptive granularity＋long-tail＋pragmatic listener eval）を横断し、「手がかりの在り処の対象依存性を測り、視方を対象ごとに適応させる」という**新しい交差点**を定義する点にあり、既存サーベイのどの単一章にも収まらない。これは論文の novelty 主張として使える。

### 長尾・未知カテゴリの扱い（詳細）
- Stefanini：Novel Object Captioning を variant VII-A に置き「describing objects not appearing in the training set, thus enabling a zero-shot learning setting」と定義。long-tail は第VIII章の第2の柱で「models which can deal with long-tail concepts offer a valuable promise of modeling real-life scenarios」。
- Hossain：novel object（rarely-seen と never-seen の区別）を future direction に明示。
- ベンチマーク：**nocaps**（H. Agrawal et al., "nocaps: novel object captioning at scale," ICCV 2019、arXiv:1812.08658）。原文では「'nocaps'... consists of 166,100 human-generated captions describing 15,100 images from the Open Images validation and test sets」——検証4,500＋テスト10,600画像、1画像あたり11キャプション（自動評価用10＋人間ベースライン1）。「nearly 400 object classes seen in test images have no or very few associated training captions (hence, nocaps)」。in-domain / near-domain / out-of-domain の3分割で COCO 外クラスへの汎化を測る。あなたの「珍しい製品」は out-of-domain に相当。関連手法：VIVO、Oscar、VinVL、NOC-REK、RCA-NOC。

## Recommendations
1. **論文の関連研究節を4本柱で構成せよ**：(1) discriminative/distinctive captioning（Luo 2018, Liu 2018, Wang et al. 2020, Wang & Chan CIDErBtw, Dessì 2023）、(2) pragmatic/RSA & REG（Cohn-Gordon 2018, Vedantam 2017, Silberer 2020）、(3) adaptive attention / where-to-look、(4) novel object / long-tail（nocaps）。各柱の「サーベイでの位置づけ」を Stefanini の章立てに紐づけて示すと、査読者に地図が伝わる。
2. **サーベイ引用は査読付き4本を主軸に**：Bernardi 2016（JAIR）、Hossain 2019（CSUR）、Stefanini 2022（TPAMI）、Ghandi 2023/2024（CSUR）。VLM 期は arXiv/二次誌と明記して区別。
3. **「未解決問題」主張の書き方**：既存サーベイが distinctiveness を独立課題にしていない事実（＝gap）を明示的に指摘し、あなたの定式化を Stefanini「Generalization/diversity/long-tail」柱と visual encoding の「granularity 不足」認識の交差点として positioning せよ。
4. **評価の正当化**：self-retrieval/listener test が標準評価節に無いこと（周辺的扱い）を逆手に取り、「reference-based metric では測れない識別性を直接測る」動機として使う。distractor（8択）設計は RSA 系と group-based distinctive captioning に前例があると引用。
5. **ベンチマーク接続**：珍しい製品を nocaps out-of-domain 文脈に接続するか、独自 distractor 集合（hard negatives）を TrueMatch/RD100 の設計思想に沿って構築せよ。
- 判断を変える基準：もし2025–2026年に distinctiveness/discriminative captioning を独立章に立てた査読付きサーベイが出た場合、あなたの「gap」主張は弱まるため、投稿前に ACM CSUR/TPAMI/IJCV の最新号を再確認すること。

## Caveats
- Stefanini サーベイの章番号は版により異なる（variants は arXiv v3 で第VII章、metrics は第V章、challenges は第VIII章）。本報告は arXiv v3／ar5iv 全文に基づく。
- 被引用数は Semantic Scholar/scite など第三者集計に基づく概数で、重複レコードにより過小の可能性がある。Google Scholar の実数はより大きい（Hossain 2019=693、Stefanini 2022=211、Bernardi 2016≈257 はいずれも下限とみなすべき）。
- 「触れていない」判定は、各サーベイの全文（Stefanini は完全確認、他は abstract＋目次＋本文断片）に基づく。Bernardi/Hossain の全文精読では細部の言及を見落とす可能性が残る。
- VLM 期はまだ TPAMI/CSUR 級の決定版総説が確立しておらず、本報告の該当部分は arXiv/二次誌に依存している。

## 参考文献
- R. Bernardi, R. Cakici, D. Elliott, A. Erdem, E. Erdem, N. Ikizler-Cinbis, F. Keller, A. Muscat, B. Plank. "Automatic Description Generation from Images: A Survey of Models, Datasets, and Evaluation Measures." *Journal of Artificial Intelligence Research*, 55:409–442, 2016. DOI: 10.1613/jair.4900（arXiv:1601.03896）【査読付き】
- Md. Z. Hossain, F. Sohel, M. F. Shiratuddin, H. Laga. "A Comprehensive Survey of Deep Learning for Image Captioning." *ACM Computing Surveys (CSUR)*, 51(6), Article 118, 2019. DOI: 10.1145/3295748（arXiv:1810.04020）【査読付き】
- M. Stefanini, M. Cornia, L. Baraldi, S. Cascianelli, G. Fiameni, R. Cucchiara. "From Show to Tell: A Survey on Deep Learning-based Image Captioning." *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 45(1):539–559, 2023. DOI: 10.1109/TPAMI.2022.3148210（arXiv:2107.06912）【査読付き】
- T. Ghandi, H. Pourreza, H. Mahyar. "Deep Learning Approaches on Image Captioning: A Review." *ACM Computing Surveys*, 56(3):1–39, 2024. DOI: 10.1145/3617592（arXiv:2201.12944）【査読付き】
- H. Sharma, D. Padha. "A comprehensive survey on image captioning: from handcrafted to deep learning-based techniques, a taxonomy and open research issues." *Artificial Intelligence Review*, 56(11):13619–13661, 2023. DOI: 10.1007/s10462-023-10488-2【査読付き】
- C. Silberer, S. Zarrieß, G. Boleda. "Object Naming in Language and Vision: A Survey and a New Dataset." *Proceedings of LREC 2020*, pp. 5792–5801, 2020.【査読付き（会議）】
- H. Agrawal, K. Desai, Y. Wang, X. Chen, R. Jain, M. Johnson, D. Batra, D. Parikh, S. Lee, P. Anderson. "nocaps: novel object captioning at scale." *ICCV 2019*（arXiv:1812.08658）.【ベンチマーク】
- Z. Wang, B. Feng, K. Narasimhan, O. Russakovsky. "Towards Unique and Informative Captioning of Images." *ECCV 2020*（arXiv:2009.03949）.【SPICE-U / uniqueness の出典】
- J. Wang, W. Xu, Q. Wang, A. B. Chan. "On Distinctive Image Captioning via Comparing and Reweighting." *IEEE TPAMI*, 45(2):2088–2103, 2022（ECCV 2020 拡張）. DOI: 10.1109/TPAMI.2022.3159811.【CIDErBtw / distinctiveness】
- R. Luo, B. Price, S. Cohen, G. Shakhnarovich. "Discriminability objective for training descriptive captions." *CVPR 2018*（arXiv:1803.04376）.【discriminative captioning + listener test】
- X. Liu, H. Li, J. Shao, D. Chen, X. Wang. "Show, Tell and Discriminate: Image Captioning by Self-retrieval with Partially Labeled Data." *ECCV 2018*（arXiv:1803.08314）.【self-retrieval】
- R. Cohn-Gordon, N. Goodman, C. Potts. "Pragmatically Informative Image Captioning with Character-Level Inference." *NAACL 2018*（arXiv:1804.05417）.【RSA / speaker-listener】
- R. Vedantam, S. Bengio, K. Murphy, D. Parikh, G. Chechik. "Context-aware Captions from Context-agnostic Supervision." *CVPR 2017*.【context-aware discriminative captioning】
- （評価特化サーベイ、arXiv のみ）"Surveying the Landscape of Image Captioning Evaluation" (arXiv:2408.04909, TACL 2024/2025); "Image Captioning Evaluation in the Age of Multimodal LLMs" (arXiv:2503.14604).
- （VLM 期、arXiv／二次誌）"Next-generation image captioning: ... from transformers to Multimodal Large Language Models," ScienceDirect S2949719125000354, 2025.