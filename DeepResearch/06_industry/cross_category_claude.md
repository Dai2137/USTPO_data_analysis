# 意匠特許ドメイン向け：「異なる意味カテゴリが形状類似で混同される」現象を評価する既存ベンチマーク調査

## TL;DR
- **完全一致する「ど真ん中」のベンチマークは事実上存在しない。** 条件①(ImageNet不使用)②(多様なカテゴリ)③(意味的に別カテゴリ同士が視覚類似で混同される設計)を最もよく満たすのは **MVI-Bench(arXiv:2511.14159, 2025年11月)** の "Visual Resemblance"(視覚的類似)カテゴリで、その定義「視覚的に似ているが意味的に異なる物体、または別カテゴリの物体と混同するケース」はユーザーの現象そのもの。
- 補完候補として **OmniBenchmark(ECCV 2022, 21意味realm・7,372概念・1,074,346枚, ImageNet不使用)**、**NaturalBench(NeurIPS 2024, CLIP混同ペア由来の10,000 VQA, ImageNet不使用)**、認知科学系の **THINGS-data(1,854物体概念・470万件の類似性判断, ImageNet不使用)** が挙げられる。ただしいずれも「形状ハードネガティブによる別カテゴリ混同」を主目的に設計してはいない。
- ユーザー例示の MMVP・cue-conflict(Geirhos)・FOCIの一部・BareBonesはいずれもImageNet(1k/21k/S)またはLAION由来を含むため条件①で除外または部分失格。ARMBench・DeepPatentは画像↔画像 retrieval/instance identification のため対象外。**結論として「自前ベンチマーク構築」を強く推奨する。**

## Key Findings

### 1. 最有力候補：MVI-Bench(条件①②③を最も直接的に満たす)
MVI-Bench(*A Comprehensive Benchmark for Evaluating Robustness to Misleading Visual Inputs in LVLMs*, arXiv:2511.14159, Huiyi Chen ら, 2025年11月)は、視覚的に紛らわしい入力に対するLVLMのロバスト性を評価する初のペアVQAベンチマーク。6カテゴリ・1,248インスタンス(624ペア)。

- **条件①(ImageNet不使用):完全にクリア。** 画像は3ソースのみ ——(1) 国際的なSNSプラットフォームから収集した自然画像、(2) 生成モデルSeedreamで生成した合成画像、(3) 人手で編集した画像。ImageNet/派生は一切使用・言及されていない(CLIP-Largeは類似度計算にのみ使用)。原論文§3.2で3ソースが逐語的に列挙されている。
- **条件③(別カテゴリ間の形状混同):最も直接的な一致。** 6カテゴリのうち "Visual Concept" レベルに属する **Visual Resemblance(視覚的類似)** の定義は逐語で「Cases where models may confuse an object with a visually similar but semantically different object or an object from a different category.(モデルが、視覚的に似ているが意味的に異なる物体、または別カテゴリの物体と混同するケース)」。まさにユーザーの記述する現象。
- **評価指標:** 正常画像精度(Acc_n)と誤導画像精度(Acc_m)、および両者の相対劣化を測る **MVI-Sensitivity = |Acc_n − Acc_m| / Acc_n**(低いほどロバスト)。各インスタンスをペアにすることで「盲目的な」正解を防ぐ。
- **モデル成績(Table 2, 18モデル):** 全体でGPT-4o = Acc_m 53.37% / Sensitivity 27.28%、GPT-4.1 = 62.82% / 20.80%、Claude-3.7-Sonnet = 42.13% / 42.10%(クローズド最弱)、Qwen2-VL-72B = 58.17% / 32.38%(オープン最強)、Molmo-7B = 37.66% / 48.69%(最弱)。論文は「all evaluated LVLMs exhibit substantial performance degradation when exposed to misleading visual cues」と報告。
- **重要な留保:** Visual Resemblanceサブカテゴリに限ると、モデルは相対的に**得意**(多くが50%超のAcc_m、Qwen2-VL-72Bで76.19% / Sensitivity 15.79%)。論文自身が「LVLMs consistently show high and stable robustness on these two categories [visual resemblance and representation confusion]」と述べており、この構造は「最も苦戦する誤答モード」ではない。混同が激しいのはむしろVisual Illusion / Mirror Reflection / Occlusion側(例：GPT-5-Chatが視覚錯覚で90.00%→61.00%、Gemini-2.5-Proが鏡像反射で86.54%→54.81%)。
- **入手:** GitHub github.com/chenyil6/MVI-Bench、HuggingFace kittyhy/MVI-Bench。
- **エピステミック注記:** 2025年11月の非常に新しいプレプリントで、査読状況は不明(第三者サーベイに"ICML 2026"の記載があるが論文本体は venue "–" 表示で未検証)。Visual Resemblanceの正確なインスタンス数は論文本文に明記なし。「roughly balanced」で6カテゴリ均等なら約208インスタンス/カテゴリ、Table 2の精度分母(例：76.19%=80/105)から**105ペア(約210インスタンス)と推定**されるが、これは逐語記載ではなく推定値である。

### 2. 補完候補：OmniBenchmark(多様性と非ImageNetは満点、③は間接的)
OmniBenchmark(*Benchmarking Omni-Vision Representation through the Lens of Visual Realms*, arXiv:2207.07106, ECCV 2022, Yuanhan Zhang ら)。
- **①:クリア。** WordNet+Wikidataで概念を拡張しFlickrから画像をクロール(CC-BYライセンス)。ImageNet不使用。むしろ「ImageNet-1kは realm カバレッジが限定的で omni-vision 評価に不適」と明示的に批判。
- **②:非常に強い。** 論文アブストラクト逐語で「It includes 21 realm-wise datasets with 7,372 concepts and 1,074,346 images. Without semantic overlapping, these datasets cover most visual realms comprehensively and meanwhile efficiently.」realm同士は概念重複なし。人工物realm(device, instrumentality, consumer_goods など)を含み、哺乳類から航空機まで横断。
- **③:間接的。** 主目的は「realm横断の汎化能力」評価(linear probing, top-1精度)であり、視覚ハードネガティブのマイニングや別カテゴリ混同を意図的に組み込む設計ではない。ただし realm間の汎化崩壊を測る点で、ドメイン特化学習の効果を示す材料にはなる。
- **入手:** プロジェクトページ zhangyuanhan-ai.github.io/OmniBenchmark。

### 3. 補完候補：NaturalBench(CLIP混同ペア由来、VQA、非ImageNet)
NaturalBench(*Evaluating Vision-Language Models on Natural Adversarial Samples*, arXiv:2410.14669, NeurIPS 2024, Baiqi Li ら)。
- **①:クリア。** Flickr30K・DOCCI・XM3600から収集。ImageNet不使用。
- **②:多様な自然画像。** 10,000 human-verified VQAサンプル。
- **③:部分的に一致。** 収集パイプラインが「CLIPやBLIP-2が取り違える confounding ペア(視覚的・意味的に類似したペア)」を起点にする点はハードネガティブ的。ただし問う内容は属性・関係・数え上げなど compositional 要素が中心で、純粋な「別カテゴリの形状混同」ではない。
- **難易度:** NeurIPS 2024アブストラクト逐語で「We evaluate 53 state-of-the-art VLMs on NaturalBench, showing that models like BLIP-3, LLaVA-OneVision, Cambrian-1, InternLM-XC2, Llama3.2-Vision, Molmo, Qwen2-VL, and even the (closed-source) GPT-4o lag 50%-70% behind human performance (which is above 90%).」

### 4. 認知科学系候補：THINGS / THINGS-data(混同性データはあるが分類ベンチではない)
THINGS-data(*eLife* 2023, Hebart ら)。
- **①:クリア。** 独自収集の1,854物体概念。ImageNet不使用。
- **②:非常に多様。** 人工物・自然物1,854概念、上位カテゴリ注釈付き(THINGSplus〔Stoinski 2024, *Behavior Research Methods* 56(3):1583–1603〕は53 high-level categories・26,107枚の自然物画像を追加提供)。
- **③:人間の「混同性」データが豊富。** eLife論文逐語で「THINGS-data also includes 4.70 million human similarity judgements collected via online crowdsourcing for 1854 object images. In a triplet odd-one-out task, participants (N=12,340) were presented with three objects」。SPoSE/VICEによる解釈可能な類似性埋め込みで「どの物体同士がヒトにとって紛らわしいか」を定量化。ただしVLM分類ベンチマークとしての標準スコアは存在せず、課題形式もodd-one-out類似性判断(分類/FGVC/VQAではない)。研究者が独自にVLM評価へ転用する必要あり。
- **入手:** things-initiative.org、OSFリポジトリ。

### 5. 明示的に除外・部分失格とした候補
- **MMVP(CVPR 2024, 2401.06209):** CLIP-blindペアで構造は近いが、画像がImageNet-1k+LAION-Aesthetics由来のため**条件①で失格**。300画像。難易度は魅力的で、CVPR 2024 open-access版で「human participants accurately answer an average of 95.7% of the questions」に対しGPT-4Vは約56%、オープン勢(LLaVA-1.5/InstructBLIP等)は14–28%、9視覚パターン中7つが最大モデルでも50%未満。
- **cue-conflict(Geirhos et al. 2019):** shape/textureバイアス測定の定番だが、ImageNetサンプルからstyle transferで合成、かつ16スーパークラスのみ。**①②で失格**。
- **FOCI(EMNLP 2024, 2406.14496):** 参考にした基準ベンチマーク。5データセット(Aircraft/Flowers102/Food101/Oxford-Pet/Stanford-Cars, 非ImageNet)+ImageNet-21k由来4サブセット。非ImageNet部分は単一ドメインFGVCで**②を満たさず**、全体としてはImageNet-21kを含む。ただしCLIPハードネガティブマイニング(image-labelコサイン類似度で最難4誤答を選択)の手法は転用可能。
- **BareBones/WTP-Bench(2604.10528):** シルエットベースの幾何理解ベンチで Qwen3-VL 4B も評価されており魅力的だが、ImageNet-S等のセグメンテーション由来を含み**条件①で部分失格**。Pokémonシルエット中心で人工物カテゴリ横断ではない。
- **ARMBench(ICRA 2023, 2303.16382) / DeepPatent:** 多様な倉庫商品(190K+物体)を扱い非ImageNetだが、タスクが object identification / 画像↔画像 retrieval のため**ユーザー除外条件により対象外**。
- **ObjectNet(NeurIPS 2019):** 家庭用品313クラスだが113クラスがImageNetと重複、かつ視点/背景バイアス制御が主目的で「別カテゴリの形状混同」設計ではない。**①③とも弱い**。

## Details

### 候補比較表(条件充足度の高い順)

| ベンチマーク | 公開年/会議 | 論文ID | タスク形式 | 規模(画像/カテゴリ) | ①ImageNet不使用 | ②多様なカテゴリ | ③別カテゴリ形状混同を意図的評価 | SOTA/汎用VLMの苦戦 | 入手 |
|---|---|---|---|---|---|---|---|---|---|
| **MVI-Bench** | 2025.11 / (査読中?) | 2511.14159 | ペアVQA | 1,248インスタンス(624ペア)/6カテゴリ | ◎ 完全 | ○ SNS+合成+編集の多様物体 | ◎ "Visual Resemblance"が定義そのもの | △ 全体では大幅劣化するがResは相対的に得意 | GitHub/HF公開 |
| **OmniBenchmark** | 2022 / ECCV | 2207.07106 | 分類(linear probe) | 1,074,346枚/7,372概念・21realm | ◎ Flickr由来 | ◎ 人工物含む21realm | △ realm汎化評価で間接的 | 一部モデルで大幅な realm 間汎化差 | プロジェクトページ |
| **NaturalBench** | 2024 / NeurIPS | 2410.14669 | VQA(二択/MCQ) | 10,000サンプル/自然画像全般 | ◎ Flickr/DOCCI/XM3600 | ○ 自然画像多様 | △ CLIP混同ペア由来だがcompositional中心 | ◎ 53モデルが人間比50-70pt低下 | HF公開 |
| **THINGS-data** | 2023 / eLife | (biorxiv 2022.07.22) | odd-one-out類似性判断 | 数千枚/1,854概念 | ◎ 独自収集 | ◎ 人工物・自然物広範 | ○ ヒト混同性データは豊富(VLMベンチではない) | N/A(標準VLMスコアなし) | things-initiative.org |
| MMVP | 2024 / CVPR | 2401.06209 | ペアVQA | 300枚/9視覚パターン | ✕ ImageNet+LAION | ○ | ◎ CLIP-blindペア | ◎ 人間95.7% vs GPT-4V約56% | HF公開(①失格) |
| FOCI | 2024 / EMNLP | 2406.14496 | 4択分類 | 5+4データセット | △ 一部ImageNet-21k | △ 非IN部は単一ドメイン | ◎ CLIPハードネガティブ | ◎ LVLM<CLIP | GitHub公開 |
| BareBones | 2026 / — | 2604.10528 | シルエット認識 | 6データセット | △ ImageNet-S含む | △ | ○ 形状のみ、ただし種内混同中心 | ◎ Qwen3-VL 4B等が壊滅的 | 記載あり(①部分失格) |
| ARMBench | 2023 / ICRA | 2303.16382 | 物体識別/retrieval | 190K+物体/235K+動作 | ◎ Amazon倉庫 | ◎ 多様商品 | — retrieval(対象外) | — | armbench.com |

### 意匠特許ドメインでの示唆(ドメイン特化学習の効果)
ユーザーの「ドメイン特化学習で精度が向上する先行事例」という判断基準に直接対応する材料として、意匠特許図面に特化したVLM研究が存在する:
- **PatFig(arXiv:2501.12751, ECIR 2025):** 特許図面のVQA/分類用に PatFigVQA・PatFigCLS を構築し、LVLM(InstructBLIP等)をファインチューニング。多数クラスを扱うためのtournament-style(多肢選択の勝ち抜き)分類戦略を提案。混同行列で「edible products と equipment for preparing/serving food」のような近縁カテゴリ間の取り違えを明示的に分析しており、ユーザーの誤答パターン分析と方法論的に一致。
- **DesignCLIP(arXiv:2508.15297):** 米国意匠特許の大規模データでCLIPを特化学習する統一フレームワーク。「特許図はスケッチで抽象的・構造的要素が中心のため視覚コンテキストが乏しく、先行技術調査で曖昧性を生む」と問題を明示。ドメイン特化が有効である傍証。

これらは「探しているベンチマーク」そのものではないが、意匠特許ドメインでの学習が形状類似による混同を改善しうるという先行事例になる。

### 自前ベンチマーク構築の材料候補
ImageNet非依存で多様な人工物カテゴリを含み、FOCI方式のハードネガティブマイニングに転用できる素材:
- **ABO(Amazon Berkeley Objects):** AWS Open Data Registry逐語で「Amazon Berkeley Objects (ABO) is a collection of 147,702 product listings with multilingual metadata and 398,212 unique catalog images」。ライセンスは CC BY-NC 4.0、576 product types(arXiv:2505.02867)。日用品・工具・家具など意匠特許と親和的な人工物を横断。
- **OmniBenchmark人工物realm** + **THINGSのヒト類似性埋め込み**(「人間にとっての形状類似ハードネガティブ」の正解ラベルとして)。

## Recommendations

**第1段階(即採用・主評価):MVI-Bench の Visual Resemblance サブセットを主要な外部ベンチマークに。**
条件①②③を最も直接的に満たす唯一の既存公開ベンチマーク。VQAペア形式なので、意匠特許の「図面→用途/カテゴリ」タスクを「この物体はAとBのどちらの用途か」形式に翻案しやすい。まずGitHub/HFからダウンロードし、zero-shot Qwen3-VL-4B と LoRA後モデルの Acc_m と MVI-Sensitivity を比較する。
- *ベンチマーク変更の閾値:* Visual Resemblanceのインスタンス数が実測で約210と小さいため、これ単独では統計的有意性が不足しうる。zero-shot と LoRA後の95%信頼区間が重なる場合は下記候補を併用すること。

**第2段階(規模と多様性の補強):OmniBenchmark で「realm横断の汎化」を測定。**
7,372概念という規模で、人工物realm内外での混同を混同行列として自前で集計すれば、「別realm(=別意味カテゴリ)への取り違え」を定量化できる。ImageNet完全非依存で意匠特許の多様な人工物カテゴリと相性が良い。
- *採用の閾値:* 自前でCLIP/VLM埋め込みによるハードネガティブ4択化(FOCI方式)を実装できるリソースがあるなら、OmniBenchmarkの人工物realmを母集団に「別カテゴリだが形状類似」の選択肢を自作するのが、ユーザーの現象に最も忠実な評価になる。

**第3段階(現象の存在証明・診断):自前ベンチマークの構築を推奨(本命)。**
正直に言えば、ユーザーの現象(用途も分類も全く異なるが外形が似た人工物同士の混同)を**主目的**に据えた、ImageNet非依存・多カテゴリ・分類/FGVC形式の広く認知されたベンチマークは現存しない。したがって最も確実なのは、**FOCIのCLIPハードネガティブマイニング手法を、OmniBenchmarkやABO(CC BY-NC)などのImageNet非依存な人工物データセットに適用して自作する**こと。THINGSのヒト混同性埋め込みを「人間にとっての形状類似ハードネガティブ」の正解ラベルとして使えば、認知科学的裏付けのある評価軸にもなる。

**測定すべき診断指標:** 混同行列の非対角要素で「意味距離が遠い(WordNet/上位カテゴリが異なる)のに繰り返し取り違えられるペア」を抽出し、LoRA前後でその頻度がどれだけ減るかを追う。これがユーザーの "Magazine loader" 反復誤答現象の定量指標になる。

## Caveats
- **完全一致ベンチマークの不在:** 「別意味カテゴリ同士が形状類似で混同されること」を主目的に設計し、かつImageNet非依存・多カテゴリ・分類/FGVC(またはVQA)形式で広く認知された既存ベンチマークは、本調査の範囲では確認できなかった。MVI-Benchが最も近いが、新しく(2025年11月)、小規模で、皮肉にもVisual Resemblanceは相対的に易しいサブタスクである。
- **MVI-Benchの成熟度・検証状況:** プレプリント段階で査読・引用の蓄積が乏しい。Visual Resemblanceの正確なインスタンス数は論文に明記されておらず、105ペア(約210インスタンス)という値はTable 2の精度分母からの推定である。ベンチマークとしての安定性・再現性は今後の検証待ち。
- **THINGS参加者数の情報不一致:** 参加者数について eLife論文本文は「N=12,340」、公式サイト things-initiative.org は「14,025 participants」と異なる値を示す。母集団定義(全モダリティ横断か行動データのみか)の差の可能性があり、引用時は出典を明記のこと。
- **タスク形式の差:** MVI-Bench・NaturalBenchはVQA、OmniBenchmarkはlinear probing分類、THINGSはodd-one-out類似性判断であり、ユーザーの「図面→製品名/カテゴリ」の開放分類とは形式が異なる。翻案が前提。
- **意匠特許図面との視覚ドメインギャップ:** 上記候補はいずれも自然写真・SNS画像・商品写真であり、線画・スケッチである意匠特許図面とは視覚統計が大きく異なる。ベンチマーク上の傾向がそのまま図面に転移する保証はない。DesignCLIP/PatFigが指摘する通り、図面固有のドメイン特化が別途必要。
- **情報の確度:** MVI-Benchの数値・定義はサブエージェントが原論文(arXiv HTML/PDF)およびGitHubから逐語確認済み。OmniBenchmark・NaturalBench・THINGS・MMVP・FOCIの規模と設計は複数の一次情報源(arXiv・ECCV/NeurIPS/eLife公式・データセット公式ページ)で相互確認済み。BareBonesは比較的新しいプレプリントであり、記載のモデル成績は原論文のみに基づく単一ソースである。