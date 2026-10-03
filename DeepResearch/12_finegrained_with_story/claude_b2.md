# 細粒度画像認識で「推論時に LLM を動かし」かつ「候補集合なしで自由記述の名前を答える」手法の網羅調査

結論から言うと、既知の3本（Fine-R1、DiVE-k、SpeciaRL）以外に条件を満たす手法は3本しか見つかりませんでした。このうち明確に満たすのは、局所領域も使う KFRA（CVPR 2026）だけです。残る VL-Taxon と SelfSynthX（ICLR 2025、確認依頼の 2502.14044）は境界例です。「条件を満たす手法はきわめて少ない」という手元の見立ては、おおむね正しいと判断します。

## TL;DR
- 新たに条件を満たすと判定したのは3本です。明確に満たすのは KFRA（CVPR 2026、arXiv 2603.03762）です。Web 画像検索で仮説を立て、Wikipedia で特徴を引き、画像の局所に照合するエージェントで、局所の選び方がサンプルごとに変わります。境界例は\[1\] VL-Taxon（arXiv 2601.14610、上位から下位へ自由記述で絞る＋SFT/GRPO）と SelfSynthX（ICLR 2025、2502.14044）の2本です。
- 確認依頼の3本の判定です。2502.14044 は条件2を満たします（境界）。NeurIPS 2024 の "Why are Visually-Grounded Language Models Bad at Image Classification?" は、汎用の画像分類を対象にした分析が中心なので除外2です。CVPR\[2\]\[3\] 2024 の "Object Recognition as Next Token Prediction" は、COCO/OpenImages の多ラベル汎用認識なので除外2です。後の2本はどちらも\[4\] FGVC の文脈には置かれていません。
- 近い研究の多くは、次のどれかの理由で落ちます。LLM を準備段階でしか使わない（FiNDR、NeaR、E-FineR）、推論時に候補・検索記憶・上位カテゴリのリストを与える（Finer/ATTRSEEK、DeepTaxon、HyMOR）、高解像度 VQA のズーム研究である（除外1）。既分類のうち DiVE-k は、OpenReview 上で ICLR 2026 採録になっており、「arXiv 2025」から訂正が必要です。

## Key Findings

### 1. 条件を満たす手法の一覧（既知の3本を除く）

| # | 手法 | 判定 | 優先度の理由 |
|---|---|---|---|
| 1 | KFRA（Seeing as Experts Do） | 満たす | 方向4（Web・百科事典の検索）と方向5（局所の利用）の両方に当たる。局所の選び方がサンプルごとに変わる |
| 2 | VL-Taxon（Learning Consistent Taxonomic Classification through Hierarchical Reasoning）\[5\] | 満たす（境界） | 方向2・3（上位から下位へ自由記述で推論＋RL） |
| 3 | SelfSynthX（Enhancing Cognition and Explainability …） | 満たす（境界） | 方向2（事後学習、候補なしで名前と根拠を生成） |

### 2. 論文ごとの詳細表

**(1) KFRA**

| 項目 | 内容 |
|---|---|
| 正式タイトル | Seeing as Experts Do: A Knowledge-Augmented Agent for Open-Set Fine-Grained Visual Understanding\[1\]\[6\] |
| 筆頭著者 | Junhan Chen（北京郵電大学）\[1\] |
| 会場・年 | CVPR 2026（pp. 41446–41455）\[6\] |
| arXiv | 2603.03762 |
| 条件1 | 満たす。Qwen3-A3B をコントローラに、LMM（Qwen2.5-VL / Qwen3-VL / GLM-4.5V）をテスト画像ごとに3段階で動かす\[1\]\[7\] |
| 条件2 | 満たす。原文："It first performs open-vocabulary detection and web-scale retrieval to generate category hypotheses." 仮説空間の説明の原文："where 𝒴_i represents the open-set label space inferred from the retrieved content" および "This stage departs from conventional closed-set classification by constructing a retrieval-augmented hypothesis space"。要約：候補カテゴリは固定の一覧ではない。テスト画像ごとに Google Lens の Web 画像検索の結果から LMM が生成する。仮説ごとに Wikipedia の記述を検索して判別的な手がかりを取り出し、最後に LMM が名前を決める。固定リスト、クラスごとの見本、taxonomy\[1\] のどれも前提にしない。質問文 q の実際の文面は未確認\[6\] |
| 事後学習 | しない（原文："without any task-specific retraining"）\[1\] |
| 画像の扱い | 全体と局所、配分はサンプルごと。局所の選び方：Grounding-DINO による開放語彙検出で物体領域 x_i を切り出す。次に仮説ごとの手がかり（"red beak" など）を、CLIP 風類似度（大域）とパッチ注意の精緻化（局所）で照合してマスクを作る。整合度が閾値未満のとき（原文："When fine details are missing or misaligned (i.e., max_k s_{i,c}^{(k)} < τ)"）は、OseDiff 超解像で最も確信度の高い領域を復元し、再照合する。低確信時は前段に戻る自己修正ループも持つ |
| 評価 | ①自作の FGExpertBench（画像300枚・QA 1,500組・6次元。複数物体・複雑な文脈を意図的に含む）。②従来の FGIC 6データセット（CUB-200-2011、Stanford Cars、Stanford Dogs、Oxford 102 Flowers、FGVC-Aircraft、Oxford-IIIT Pets）。②は原文 "each question corresponds to a visual query with one correct answer among multiple candidates" のとおり多肢選択の正答率で評価しており、自由記述の採点は行っていない。GLM-4.5V 版で平均 90.24%、Qwen2.5-VL-7B 版で 85.10%（基盤モデル比 +23.61）\[1\]\[6\]\[8\] |
| 注意 | 本文の問題設定は「細粒度の視覚理解」で、認識より広い（属性・行動・数え上げ・知識推論を含む）。ただし物体認識が中心の次元で、FGIC\[1\] 6データセットで分類性能も主張しているため、対象に含めた。FGExpertBench の複数物体画像は除外1に近い性質を持つが、評価は TextVQA / V*Bench 系ではない\[8\] |

**(2) VL-Taxon**

| 項目 | 内容 |
|---|---|
| 正式タイトル | Learning Consistent Taxonomic Classification through Hierarchical Reasoning |
| 筆頭著者 | Zhenghong Li（Stony Brook University）\[5\] |
| 会場・年 | arXiv のみ（2026）。会場は未確認（arXiv v1 の著者は Zhenghong Li、Kecheng Zheng〔Ant Research〕、Haibin Ling） |
| arXiv | 2601.14610 |
| 条件1 | 満たす（Qwen2.5-VL-7B を2段階で推論）\[5\] |
| 条件2 | 満たす（境界）。Stage 1 の原文："To reflect realistic deployment scenarios and prevent information leakage from fixed answer sets, the question-answering in this stage is formulated in an open-set manner, where the model must generate the correct category name rather than select from a predefined list." 手順の原文："we explicitly instruct the model to perform top-down reasoning, from the general level to the specific level. The final output is the predicted name of the most specific category"。要約：Stage 1 では候補なしに、界から種まで上から順に自分で書き出し、最も具体的な名前を自由記述で出す。taxonomy は入力として与えず、SFT でモデルに覚えさせる。Stage 2 はベンチマークの多肢選択問題に答える段で、Stage 1 の予測を条件に使う（原文："For Stage 2 training samples, the reward is assigned if the predicted answer letter is correct, which aligns with the multiple-choice formulation"）。境界とした理由：公開されている評価の全体が多肢選択の枠組みで、Stage\[5\] 1 単独の自由記述精度は本文から確認できない。Stage 1 の実際のプロンプト文面は図中にあり、未確認\[5\] |
| 事後学習 | する。学習集合を種で二分し、前半で SFT（taxonomy 知識を注入）、後半で GRPO。Stage 1 の報酬は完全一致（原文："the reward is granted only when the predicted category name exactly matches the ground-truth label"）。LoRA\[5\] を使う\[5\] |
| 画像の扱い | 全体のみ |
| 評価 | iNat21-Animal、iNat21-Plant、CUB-200。Tan et al. のベンチマークに従い、SigLIP 類似度で紛らわしい選択肢を選ぶ similar-choice の多肢選択形式。指標は HCA（全階層正解）と Acc_leaf。iNat21-Plant で HCA 63.04（Qwen2.5-VL-72B は 32.82）\[5\] |
| 注意 | 本文の問題設定は階層（taxonomic）分類。末端は種レベルで iNat/CUB を使うため、細粒度認識の文脈にあると判断した\[5\] |

**(3) SelfSynthX（確認依頼の 2502.14044）**

| 項目 | 内容 |
|---|---|
| 正式タイトル | Enhancing Cognition and Explainability of Multimodal Foundation Models with Self-Synthesized Data\[9\] |
| 筆頭著者 | Yucheng Shi（University of Georgia）\[10\] |
| 会場・年 | ICLR 2025（PDF に "Published as a conference paper at ICLR 2025"）\[10\] |
| arXiv | 2502.14044 |
| 条件1 | 満たす（微調整した LLaVA-1.5-7B が、テスト画像ごとに名前と根拠を生成する）\[10\] |
| 条件2 | 満たす（境界）。推論時の質問の原文："These answers are obtained by prompting the model with questions like “What is the {item} in this image? Please provide your reasoning.” The “item” here is set to be an coarse-level label, like bird, airplane."\[10\] 要約：推論時の入力は画像と、上位カテゴリ名が一語入った質問だけで、候補の一覧は与えない。上位カテゴリ語は、依頼のルールにいう「一語入っているだけ」に当たると判断した（例示には "Identify this bird. What features led to your conclusion?" のような形もある）。境界とした理由：学習データの合成の核に、クラスごとの専門家定義の概念リスト（原文："Each label class c is associated with a set of expert-defined visual concepts Z"）が要る。これはクラスごとの記述の有限集合に当たる。ただし必要なのは学習時だけで、推論時には不要である。また学習と評価が同じクラス集合で行われ、未知クラスへの自由記述の汎化は検証されていない\[10\] |
| 事後学習 | する。情報ボトルネックで画像ごとの概念を選び、根拠つきの回答を合成して LoRA SFT を行う。その後、報酬モデルを使わない棄却サンプリング（InfoNCE で概念との整合を測り、正解ラベルを含む回答だけを残す）で反復微調整する（4反復）\[10\] |
| 画像の扱い | 全体のみ |
| 評価 | CUB-200、Stanford Dogs、FGVC-Aircraft に加え、HAM10000、Chest X-ray、PLD（植物病害）。採点は含有判定（原文："success defined as the presence of the ground truth label in the model’s response"）。CUB で 85.02%（Base 2.69%）。説明の質は GPT-4o による EE/CS と perplexity で測る\[10\] |

### 3. 既に分類済みの論文への指摘

- **DiVE-k**：会場は「arXiv 2025」ではありません。OpenReview では "ICLR 2026 Poster" となっています。B-2\[11\] の判定には同意します。推論時の選択肢はモデル自身の top-k 生成であり、外から与える有限集合ではないからです。\[12\]
- **SpeciaRL**：CVPR 2026 の公式バーチャルサイトのポスター一覧に掲載されており（"Poster Sun, Jun 7, 2026 • 2:30 PM – 4:30 PM PDT ExHall A 491"）、CVPR 2026 採録を一次情報で確認しました。表記は「arXiv 2026」から CVPR 2026 に更新すべきです。
- **ReFine-RFT**（Can Textual Reasoning Improve …）：CVF Open Access の "CVPR2026F" 枠に掲載されています（CVPR 2026 Findings と見られます）。B-1\[13\] の判定は変えません。
- **Finedefics**：学習データに開放型 QA（"What is the species of the bird shown in the image?"）を含みます。ただし評価は多肢選択です。B-1\[14\]\[15\] の判定は妥当ですが、推論機構だけを見れば自由記述も出せるので、境界に近い点は付記しておきます。

### 4. 条件2を満たさないと判定した論文（新規分）

| 論文 | 会場 | 理由 |
|---|---|---|
| Finer: Investigating and Enhancing Fine-Grained Visual Concept Recognition in Large Vision Language Models（Jeonghwan Kim、arXiv 2402.16315） | EMNLP 2024 main\[16\] | 上位カテゴリの候補リストを与える段が推論手順の核にある。iNaturalist の上位段の原文："Provide your answer after \"Answer:\" from one of the following categories: ['Arachnids', 'Mammals', … 'Fungi']"。下位段では親カテゴリ名を注入して生成範囲を絞る（原文："we decided to input the coarse-level label … to condition the generation of the fine-grained output within a specified category space"）。Aircraft ではメーカー30社、Cars では車体型7種の候補リストも与える。最下位の名前自体は自由記述だが、上位カテゴリ名の注入が手法の核なので、「一語を外しても成り立つ」には当たらない。ATTRSEEK\[17\] の推論プロンプトそのものは本文に原文がなく未確認（図のみ） |
| DeepTaxon（arXiv 2604.24029） | arXiv のみ（2026） | 検索用の記憶に依存する。原文："retrieves the top-𝑘 candidate species with 𝑛 exemplar images each from a retrieval index"。「新種」と判定したときは名前を生成しない\[18\] |
| HyMOR: Bridging Coarse and Fine Recognition（arXiv 2604.16785） | arXiv のみ（2026） | MLLM が担うのは上位の粗い認識と振り分けだけで、細粒度の同定は CLIP が担う（原文："the CLIP model specializes in fine-grained identification of domain-specific objects such as animals and plants"）。CLIP\[19\] 側はカテゴリ一覧を必要とすると判断した（一覧の詳細は未確認）。上位カテゴリも "plant", "animal", "other" に制約されている。問題設定も教育ゲーム向けで、除外2にも当たる\[20\] |

### 5. 除外1〜3に当たるため外した論文

| 論文 | 区分 | 理由 |
|---|---|---|
| Why are Visually-Grounded Language Models Bad at Image Classification?（Yuhui Zhang、NeurIPS 2024、arXiv 2405.18415） | 除外2（分析が中心） | 対象は汎用の画像分類（ImageNet など）で、FGVC の文脈には置かれていない。提案は分類データを VLM 学習に混ぜるデータ介入にとどまる。評価は開放世界と閉世界（原文："feeding\[3\] each image and a list of class names (in the closed-world setting) to the VLM as context"）で、採点は含有判定\[2\]\[3\] |
| Object Recognition as Next Token Prediction（Kaiyu Yue、CVPR 2024、arXiv 2312.02142） | 除外2 | 画像埋め込みから言語デコーダ（LLaMA を間引いたもの）で自由にラベルを生成するので、推論時に LLM を使い、語彙も開いている。ただし評価は CC3M / COCO / OpenImages の多ラベル汎用認識で、FGVC\[4\]\[21\] の文脈には置かれていない |
| Thinking Beyond Labels / FiNDR（Dmitry Demidov、CVPR 2026、arXiv 2512.18897） | 除外3 | 推論 LMM は語彙の発見にだけ使う。原文："the verified names instantiate a lightweight multi-modal classifier used at inference time"\[22\] |
| Efficient Vocabulary-Free FGVR in the Age of MLLMs / NeaR（Hari Chandana Kuchibhotla、TMLR 2025、arXiv 2505.01064） | 除外3 | MLLM で学習集合にラベルを付け、推論は微調整した CLIP で行う。原文："querying these models for each test input is impractical"\[23\]\[24\] |
| E-FineR（arXiv 2507.23070） | 除外3 | 学習不要で、LLM は記述生成と名前候補の生成に使う。分類は CLIP の類似度で行う\[25\] |
| Region-Level Policy Optimization（arXiv 2609.19745）、Vision-OPD（arXiv 2605.18740）、FOCUS（arXiv 2506.21710） | 除外1 | 高解像度・小物体の VQA 向けの RoI・クロップ研究（ZoomBench、V*Bench など）\[26\]\[27\]\[28\] |
| AgriScope（arXiv 2609.20325） | 除外2 | 農業画像のピクセル単位グラウンディング MLLM で、単一物体の細粒度名当てではない\[29\] |
| TaxonRL（arXiv 2603.04380） | 除外2（課題が異なる） | Birds-to-Words で2枚の画像が同じ分類群かを判定する検証課題で、名前を生成しない\[30\] |
| CLS-RL（arXiv 2503.16188） | 除外2 | 11データセットの汎用少数ショット分類。推論時に選択肢を与えるかどうかは未確認\[31\] |
| Reliability-Prioritized Fine-Grained Generation / GranFact（arXiv 2606.29573） | 対象範囲外（複数物体） | DPO による細粒度生成の手法だが、複数物体画像での記述生成が対象\[32\] |

### 6. ベンチマーク・分析だけの論文（自由記述の評価方法として参考になる順）

1. **On Large Multimodal Models as Open-World Image Classifiers**（Alessandro Conti、ICCV 2025）：自由記述の分類を LLM と埋め込み類似度で採点し、予測を correct/specific と generic/wrong などに分ける。SpeciaRL の6段階（Wrong, Abstain, Generic, Less Specific, Specific, More Specific）の土台になっている。10ベンチマークを粒度別（prototypical、fine-grained、very\[33\]\[34\] fine-grained、non-prototypical）に評価している。\[35\]
2. **FIKA-Bench**（arXiv 2605.13193、arXiv のみ）：外部検索を前提にした自由記述の細粒度認識で、311例。閉じた状態で解ける例を除き、証拠も人手で検証している。最良システムでも 25.1% で、道具を持たせるだけでは改善しない（失敗の主因は誤った実体の検索と視覚判断の誤り）。方向4の手法の評価に向く。\[36\]
3. **Finer**（EMNLP 2024）：手法も含むが、主に分析。変形 EM（原文："considers the output label correct if the ground-truth label string exists within a pre-defined maximum number of tokens, m (we set m = 20)"）と F1 を使い、上位・粗・細の3階層で評価する。iNaturalist で GPT-4V の細粒度 EM は 18.752 から ATTRSEEK で 53.125 に上がったが、LLaVA-1.5-13B は 1.562 のままだった。\[17\]
4. **GranFact**（arXiv 2606.29573）：自由記述の応答を実体に分解し、粗から細までの正解階層に割り当てる、階層を考慮した採点。正しさと具体性を分けて測れる（複数物体向け）。\[32\]
5. **Why are Visually-Grounded Language Models Bad at Image Classification?**（NeurIPS 2024）：開放世界と閉世界の比較で、採点は含有判定。\[2\]\[37\]
6. **FGExpertBench**（KFRA 論文内）：6次元の QA ベンチマーク。\[1\]\[6\]
7. **RealBirdID**（Logan Lawrence ほか、arXiv 2603.27033、要旨に "Accepted to CVPR26"）：鳥の画像に対し、種名を答えるか、根拠つきで回答を控えるかを求める鳥種同定ベンチマーク（原文："given an image of a bird, a system should either answer with a species or abstain with a concrete, evidence-based rationale: 'requires vocalization,' 'low quality image,' or 'view obstructed'"）。属ごとに回答可能な例と回答不能な例を対にしている。回答可能な集合での精度は、原文 "less than 13% accuracy for MLLMs including GPT-5 and Gemini-2.5 Pro" のとおり 13% 未満。
8. **FishNet++**（arXiv 2509.25564）：海洋生物の MLLM 分析で、35,133 種の記述を使った開放語彙認識。\[38\]

## Details：判断の要点

- **「少ない」理由**：推論時に LLM を使う細粒度手法の多くは、多肢選択（Finedefics、DiVE-k 以前の RFT 系）か、検索で得た候補一覧（RAR、DeepTaxon、VR-RAG）で答えの空間を閉じています。自由記述では文字列一致の報酬や採点が不安定で、SpeciaRL\[12\] が扱う「上位語に逃げる」問題も起きるためです。語彙なし（VF-FGVR）の系統は、推論コストを理由に\[34\] LLM を準備段階へ追い出す設計が主流です（NeaR の原文："querying these models for each test input is impractical"）。\[23\]
- **最優先（局所を使う）方向**で条件を満たすのは KFRA だけでした。ただし KFRA の FGIC 評価は多肢選択なので、「自由記述で局所を使ったときの細粒度精度」を実測した研究は、今回の範囲では見つかっていません。\[1\]
- **coarse-to-fine の生成**（方向3）の系統は2つです。Finer は上位カテゴリの候補リストと親カテゴリ名の注入が核なので B-1 としました。VL-Taxon は上位を自分で生成するので B-2（境界）としました。\[5\]

## Recommendations

- 既存の B-2 リストに加えるべきなのは KFRA です。VL-Taxon と SelfSynthX は「境界」の注記をつけて扱うのが妥当です。
- 局所を使う自由記述の細粒度認識の比較対象としては、KFRA が事実上唯一の先行手法です。これと差をつけるなら、自由記述の採点（Conti et al. の LLM 判定や SpeciaRL の6段階）で評価することが、そのまま新規性になります。
- DiVE-k の会場表記は ICLR 2026 に直してください。

## Caveats

- 検索予算の制約（約18回の検索）により、網羅性は完全ではありません。ACL/EMNLP 2025、AAAI 2026、NeurIPS 2025 の採録一覧を個別には走査していないので、漏れがありうる領域として残ります。
- KFRA の質問文 q の文面、VL-Taxon の Stage 1 プロンプト、Finer の ATTRSEEK 推論プロンプトは、いずれも図の中にあって原文を確認できませんでした（未確認）。
- VL-Taxon の会場は一次情報で未確認です（SpeciaRL は CVPR 2026 公式サイトのポスター一覧で採録を確認しました）。
- KFRA の数値は著者による報告で、FGExpertBench は著者自身が作ったベンチマークです。\[6\]

## 出典

1. <https://arxiv.org/pdf/2603.03762>
2. [Why are Visually-Grounded Language Models Bad at Image Classification?](https://papers.nips.cc/paper_files/paper/2024/file/5c7024041be305c94d7311cfcc53d93e-Paper-Conference.pdf)
3. [\[2405.18415\] Why are Visually-Grounded Language Models Bad at Image Classification?](https://arxiv.org/abs/2405.18415)
4. [GitHub - kaiyuyue/nxtp: PyTorch Implementation of Object Recognition as Next Token Prediction \[CVPR'24 Highlight\] · GitHub](https://github.com/kaiyuyue/nxtp)
5. [Learning Consistent Taxonomic Classification through Hierarchical Reasoning](https://arxiv.org/html/2601.14610)
6. [CVPR 2026 Open Access Repository](https://openaccess.thecvf.com/content/CVPR2026/html/Chen_Seeing_as_Experts_Do_A_Knowledge-Augmented_Agent_for_Open-Set_Fine-Grained_CVPR_2026_paper.html)
7. [\[Paper Note\] Seeing as Experts Do: A Knowledge-Augmented Agent for Open-Set Fine-Grained Visual Understanding](https://en.papernotes.org/CVPR2026/llm_agent/seeing_as_experts_do_a_knowledge-augmented_agent_for_open-set_fine-grained_visua/)
8. [Seeing as Experts Do: A Knowledge-Augmented Agent for](https://openaccess.thecvf.com/content/CVPR2026/papers/Chen_Seeing_as_Experts_Do_A_Knowledge-Augmented_Agent_for_Open-Set_Fine-Grained_CVPR_2026_paper.pdf)
9. [arxiv.org](https://arxiv.org/abs/2502.14044)
10. <https://www.arxiv.org/pdf/2502.14044>
11. [DiVE-k: DIFFERENTIAL VISUAL REASONING FOR FINE-GRAINED IMAGE RECOGNITION](https://openreview.net/forum?id=flE6M5zFL6)
12. [\[Paper Note\] DiVE-k: Differential Visual Reasoning for Fine-grained Image Recognition](https://en.papernotes.org/ICLR2026/reinforcement_learning/dive-k_differential_visual_reasoning_for_fine-grained_image_recognition/)
13. [CVPR 2026 Open Access Repository](https://openaccess.thecvf.com/content/CVPR2026F/html/Zhu_Can_Textual_Reasoning_Improve_the_Performance_of_MLLMs_on_Fine-Grained_CVPRF_2026_paper.html)
14. [Analyzing and Boosting the Power of Fine-Grained Visual ...](https://iclr.cc/media/iclr-2025/Slides/28323_8XlLqgr.pdf)
15. [Analyzing and Boosting the Power of Fine-Grained Visual Recognition for Multi-modal Large Language Models](https://arxiv.org/pdf/2501.15140)
16. [Finer: Investigating and Enhancing Fine-Grained Visual Concept Recognition in Large Vision Language Models - ACL Anthology](https://aclanthology.org/2024.emnlp-main.356/)
17. [Finer: Investigating and Enhancing Fine-Grained Visual Concept Recognition in Large Vision Language Models](https://arxiv.org/pdf/2402.16315)
18. [DeepTaxon: An Interpretable Retrieval-Augmented Multimodal](https://arxiv.org/pdf/2604.24029)
19. [Bridging Coarse and Fine Recognition: A Hybrid Approach for Open-Ended Multi-Granularity Object Recognition in Interactive Educational Games](https://arxiv.org/html/2604.16785)
20. [Bridging Coarse and Fine Recognition: A Hybrid Approach for Open-Ended Multi-Granularity Object Recognition in Interactive Educational Games](https://arxiv.org/pdf/2604.16785)
21. [Object Recognition as Next Token Prediction](https://openaccess.thecvf.com/content/CVPR2024/html/Yue_Object_Recognition_as_Next_Token_Prediction_CVPR_2024_paper.html)
22. [Thinking Beyond Labels: Vocabulary‑Free Fine‑Grained Recognition using Reasoning-Augmented LMMs](https://arxiv.org/html/2512.18897)
23. [Efficient Vocabulary-Free Fine-Grained Visual Recognition in the Age of Multimodal LLMs](https://arxiv.org/html/2505.01064)
24. [Efficient Vocabulary-Free Fine-Grained Visual Recognition in the Age of Multimodal LLMs — Lacuna](https://lacuna.tiptreesystems.com/work/efficient-vocabulary-free-fine-grained-visual-recognition-in-the-age-of/wrk_4c107d1ead514d8ce56298ed9e286f43)
25. [Vocabulary-free Fine-grained Visual Recognition](https://arxiv.org/html/2507.23070v1)
26. [Region-Level Policy Optimization for Fine-grained MLLM Perception](https://arxiv.org/pdf/2609.19745)
27. [Vision-OPD: Learning to See Fine Details for](https://arxiv.org/pdf/2605.18740v3)
28. [Internal MLLM Representations for Efficient Fine-Grained ...](https://arxiv.org/pdf/2506.21710)
29. [AgriScope: Pixel-Grounded Multimodal Understanding for Agricultural Images](https://arxiv.org/html/2609.20325v1)
30. [TaxonRL: Reinforcement Learning with Intermediate Rewards for Interpretable Fine-Grained Visual Reasoning](https://arxiv.org/html/2603.04380)
31. [(PDF) CLS-RL: Image Classification with Rule-Based Reinforcement Learning](https://www.researchgate.net/publication/390038446_CLS-RL_Image_Classification_with_Rule-Based_Reinforcement_Learning)
32. [Reliability-Prioritized Fine-Grained Generation in Multimodal Large Language Models](https://arxiv.org/html/2606.29573)
33. [Specificity-aware reinforcement learning for fine-grained open-world classification](https://arxiv.org/pdf/2603.03197)
34. [Specificity-aware reinforcement learning for fine-grained open-world classification — Lacuna](https://lacuna.tiptreesystems.com/work/specificity-aware-reinforcement-learning-for-fine-grained-open-world/wrk_4eddcf2c3afc6f098cd71f7637a288de)
35. [On Large Multimodal Models as Open-World Image Classiﬁers](https://openaccess.thecvf.com/content/ICCV2025/papers/Conti_On_Large_Multimodal_Models_as_Open-World_Image_Classifiers_ICCV_2025_paper.pdf)
36. [FIKA-Bench: From Fine-grained Recognition to Fine-Grained Knowledge Acquisition](https://arxiv.org/html/2605.13193v1)
37. [(PDF) Why are Visually-Grounded Language Models Bad at Image Classification?](https://www.researchgate.net/publication/380935842_Why_are_Visually-Grounded_Language_Models_Bad_at_Image_Classification)
38. [FishNet++: Analyzing the capabilities of Multimodal Large Language Models in marine biology](https://arxiv.org/pdf/2509.25564)
