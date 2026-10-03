# 2025〜2026年トップ会議における「VLMに画像の対象を答えさせる」研究：生成・データ・学習・評価の設計分析

## TL;DR
- 2025〜2026年のトップ会議で「VLMに写っている対象を答えさせる」研究の**新規性は圧倒的に「生成（推論時の工夫）」と「評価（新ベンチマーク提案）」の2つに集中**しており、学習データと学習手法は既存のFGVRデータセット（CUB／Stanford Cars／FGVC-Aircraft／iNaturalist 等）と標準的な SFT／GRPO／対照学習から「借りてくる」のが定型。純粋な学習なし（training-free）論文がこの領域では非常に多く、主流の型の一つ。
- 評価の**定番は「多肢選択の正解率（FOCI型：CLIPで採掘した視覚的に近い hard negative）」と「vocabulary-free の cACC/sACC（クラスタリング精度＋Sentence-BERT 意味類似度）」の二本立て**で、自由記述を厳密に採点する論文は少数。LLM-as-judge は一般 VQA では普及するが、対象命名タスクでは多肢選択か embedding 写像に置き換えられている。
- **あなたの4つの設計要素（質問文なしの粒度切り替え／手がかりの局所性の測定／当て直し（retrieval・listener）による採点／未学習カテゴリでの一般化）のうち、「当て直しによる採点」を対象命名で使った査読付き2025-2026論文は、本調査の範囲では見つからなかった**。これが最も差別化できる余地。残り3つは部分的に先行例があるが、4つを1本に統合した例は確認できない。

## Key Findings

### 全体像
Lin による大規模計量調査「Vision Language Models: A Survey of 26K Papers」（arXiv:2510.09586、CVPR・ICLR・NeurIPS の26,104本の要旨を解析）は「By 2025, the VLM share reaches 39.5% at CVPR and 40.7% at ICLR」と報告しており、VLM 研究は主要会議の約4割を占める巨大な母集団になっている。この中で「画像を見せて対象が何かを答えさせる」研究は、大きく4つの型に分かれる。

1. **推論時の工夫＋学習なし＋既存ベンチ**（最多）：DyFo (CVPR2025), MLLMs Know Where to Look (ICLR2025), AutoSEP (NeurIPS2025), E-FineR (ICCVW2025), SARE (arXiv2026)
2. **新データ＋事後学習＋既存ベンチ**：Finedefics (ICLR2025), Fine-R1 (ICLR2026), NeaR (TMLR2025)
3. **診断・ベンチ提案主体（手法を出さない）**：FOCI (EMNLP2024, 基礎), Finer (EMNLP2024, 基礎), 各種2025-2026 fine-grained 診断ベンチ
4. **表現学習（CLIP系）**：FLAIR (CVPR2025), FG-CLIP (ICML2025)

### 観点1：生成（推論）
- **凍結モデル＋プロンプト**が最も多い。DyFo（CVPR2025、採録論文の上位13.5%の Poster Highlight）は Focus Tree Search（MCTS ベース）で視覚専門家（Lang-SAM）と LMM（Qwen2-VL／LLaVA-1.5）を双方向に対話させ、追加学習なしに注目領域を動的に絞る。
- **推論時の切り出し・ズーム**：V*/SEAL（CVPR2024, 基礎）の guided visual search が起点。MLLMs Know Where to Look（ICLR2025）はモデル内部の attention/gradient マップだけで小領域を特定し切り出す完全 training-free。ZoomEye (EMNLP2025)、Chain-of-Focus 系が続く。推論コストの目安として、SEAL は「an average of 4.65 cropped image regions per query at inference time」（Reinforcing VLMs, arXiv:2506.14821 の報告）と、クロップ数まで報告される傾向が強まっている。
- **段階を踏ませる（CoT／属性先出し）**：Finer（EMNLP2024）の ATTRSEEK は「まず識別的な物理属性を生成→それを使って最終予測」。Fine-R1（ICLR2026）は CoT-SFT＋RL で「視覚分析→候補下位カテゴリ→比較→予測」の連鎖を学習。
- **外部検索・検出器を挟む**：RAR（retrieving and ranking）系、SARE（arXiv2026）は「高速な候補検索＋必要時のみ細粒度推論」のカスケード。

### 観点2：学習データ
- **既存 FGVR データセットの流用が圧倒的**：CUB-200-2011、Stanford Cars-196、FGVC-Aircraft、Stanford Dogs、Oxford Flowers-102、Oxford-IIIT Pets-37、iNaturalist、Food-101 が定番の6〜8点セット。
- **合成・LLM 生成データ**：Finedefics（ICLR2025）は Wikipedia 等から属性記述を集め object-attribute／attribute-category ペアを構成。E-FineR（ICCVW2025）は Gemini-2.0 でクラス別の文脈記述を自動生成。Fine-R1 は CoT rationale データを構成。多くが「LLM で属性・記述を生成し、CLIP／人手で品質担保」という型。
- **規模**：FLAIR（CVPR2025）は結論部で「Trained on 30M recaptioned images, FLAIR outperforms baselines trained on billions of images across standard, fine-grained, and long-form image-text retrieval tasks」と述べ、30M の再キャプション画像で billions 規模を上回ると主張。事後学習系は few-shot も多く、Fine-R1 は4-shot／カテゴリ。
- **分布関係**：多くが訓練カテゴリと評価カテゴリを分割（open-set／novel category）。vocabulary-free 系は評価時に語彙を与えない。

### 観点3：学習手法
- **学習なし（training-free）がこの領域の主要な型**：DyFo、MLLMs Know Where to Look、AutoSEP、E-FineR、SARE、FineR 系。対象命名の主要論文群のうち、およそ半分近くが training-free。
- **学習する場合**：
  - 対照学習：Finedefics は「We employ contrastive learning on object-attribute pairs and attribute-category pairs simultaneously and use examples from similar but incorrect categories as hard negatives」（OpenReview）。ほか FLAIR、FG-CLIP。
  - SFT＋RL(GRPO)：Fine-R1（CoT-SFT＋Triplet Augmented Policy Optimization という R1 スタイル RL）、Visual-RFT（GRPO を fine-grained classification／detection に適用）。
  - 弱教師 CLIP 微調整：NeaR（TMLR2025、MLLM 生成ラベルで CLIP を cross-entropy 微調整、GMM で clean/noisy 分離）。
- **目的関数**：交差エントロピー（分類・SFT）、対照学習、GRPO／選好最適化。Lin のサーベイは全体傾向として「contrastive objectives recede relative to cross-entropy/ranking and distillation」と報告。
- **計算資源**：LoRA／adapter 等の軽量適応が主流（Lin サーベイ）。

### 観点4：評価（ベンチマークと採点方法）
**使用ベンチマーク（対象命名に直接関係するもの）**
- **FOCI**（Fine-grained Object ClassIfication、EMNLP2024）：5つの分類データセット＋ImageNet-21k の4サブセット。**4択（正解1＋CLIP 採掘の hard negative 3）**、多肢選択正解率。
- **Finer**（EMNLP2024）：iNaturalist／FGVC-Aircraft 等6ベンチに属性を付与、複数粒度（super-ordinate／coarse／fine）で EM 採点。
- **FGVR データセット群**（CUB／Cars／Aircraft／Dogs／Flowers／Pets／iNaturalist／Food-101）：vocabulary-free では cACC（クラスタリング精度）＋sACC（Sentence-BERT 意味類似度）。
- **知覚限界系**：V*Bench（CVPR2024）、HR-Bench、MMVP、BLINK、MME-RealWorld。小領域・高解像度の知覚を測る。
- **一般総合系**：MMMU、MMBench、SEED-Bench、MME（補助ベンチとして併用）。

**採点方法の採用状況**
- **多肢選択正解率**：FOCI, Finedefics（FOCI 併用）。実装が容易で曖昧性がない。
- **embedding 写像（cACC／sACC）**：vocabulary-free 系（FineR, E-FineR, NeaR）。自由記述の同義語・粒度問題を回避。
- **EM（完全一致・正規化一致）**：Finer。分類 accuracy：AutoSEP, SARE, Fine-R1。
- **LLM-as-judge**：一般 VQA・記述生成では普及（人手一致率 κ=0.94、一致率97.2%のような報告例：MemEye）が、**対象命名タスクでは多肢選択か embedding 写像に置き換えられている**。
- **retrieval／listener（当て直し）採点**：対象命名タスクの査読付き2025-2026論文では未確認（後述）。

**1本あたりのベンチ数**：手法論文は主ベンチ（FGVR 5-6点）＋補助（V*Bench／HR-Bench 等の知覚系、MME／MMBench 等の総合系）で計6〜10点が標準。

## Details

### 4観点の一覧表

| 論文 | 会議・年 | 生成（推論） | 学習データ | 学習手法 | 評価（ベンチマーク＋採点） | 公開 |
|---|---|---|---|---|---|---|
| **DyFo** (Li et al.) | CVPR 2025 (Highlight, 上位13.5%) | 凍結LMM＋視覚専門家(Lang-SAM)の双方向対話、Focus Tree Search(MCTS)で動的フォーカス | なし（training-free） | 学習なし | POPE, A-OKVQA, V*Bench 等の細粒度・幻覚ベンチ。多肢選択/VQA accuracy | GitHub有 |
| **MLLMs Know Where to Look** (Zhang et al.) | ICLR 2025 | 内部attention/gradientマップで小領域特定→切り出し（複数手法） | なし | 学習なし | 7つのVQAベンチ（TextVQA等含む）。VQA accuracy | GitHub有 |
| **Finedefics** (He et al.) | ICLR 2025 | 生成（属性→カテゴリ）、Idefics2-8Bベース | 6 FGVRデータセット訓練セット＋Wikipedia属性記述 | 対照学習（object-attribute/attribute-categoryペア、hard negative） | 6 FGVRデータセット＋FOCI。生成accuracy＋多肢選択 | GitHub有 |
| **Fine-R1** (He et al.) | ICLR 2026 | CoT（視覚分析→候補→比較→予測）、生成命名 | CoT rationaleデータ、4-shot/カテゴリ | CoT-SFT＋Triplet Augmented Policy Optimization (GRPO系RL) | 6 FGVRデータセット。closed/open-world生成accuracy | GitHub有 |
| **AutoSEP** (Hong et al.) | NeurIPS 2025 | 凍結MLLM＋反復的自己教師ありプロンプト学習、記述プロンプト最適化 | 未ラベルデータ | 学習なし（プロンプト最適化のみ） | 細粒度zero-shotデータセット。分類accuracy | 有 |
| **NeaR** (Kuchibhotla et al.) | TMLR 2025（査読付き論文誌） | MLLMが候補ラベル生成→CLIP分類 | MLLM生成の弱教師ラベル | CLIP微調整（cross-entropy、GMMでclean/noisy分離） | vocabulary-free FGVR。CLIP写像accuracy | 有 |
| **E-FineR** (Demidov et al.) | ICCV 2025 Workshop (MMFM) | LLM(Gemini-2.0)でクラス記述生成＋soft class-name filtration、CLIP zero-shot | なし | 学習なし | CUB-200/Cars-196/Dogs-120/Flowers-102/Pets-37。cACC＋sACC | 有 |
| **SARE** (Yang, He et al.) | arXiv-only (2026)【未確認】 | 高速候補検索＋必要時のみ細粒度推論のカスケード、経験再利用 | なし | 学習なし | Aircraft/Birdsnap/Dogs/Cars等。分類accuracy(平均87.68%) | — |
| **FOCI** (Geigle et al.) | EMNLP 2024（基礎） | ベンチマーク（LVLMに多肢選択を解かせる） | 5分類データセット＋ImageNet-21k 4サブセット | なし（評価論文） | 多肢選択accuracy（4択＝正解1＋CLIP hard negative 3） | GitHub有 |
| **FLAIR** (Xiao et al.) | CVPR 2025 | CLIP系、text-conditioned attention pooling | 30M 再キャプション image-textペア | 対照学習＋局所トークン | 検索ベンチ＋zero-shotセグメンテーション。R@1等 | GitHub有 |

### ベンチマーク使用頻度の一覧

| ベンチマーク | 何を測る | 規模 | 使用論文数（概数） | 2025-2026新規? |
|---|---|---|---|---|
| CUB-200-2011 | 鳥種細粒度分類 | 200種/11,788枚 | 多数（定番） | いいえ（2011） |
| Stanford Cars | 車種細粒度分類 | 196種/16,185枚 | 多数（定番） | いいえ（2013） |
| FGVC-Aircraft | 航空機細粒度分類 | 100-102型/10,000枚 | 多数（定番） | いいえ（2013） |
| iNaturalist | 生物種・長尾 | 約10,000クラス | 複数 | いいえ（2018/2021） |
| Stanford Dogs | 犬種 | 120種 | 複数 | いいえ |
| Oxford Flowers-102 / Pets-37 / Food-101 | 花/ペット/食品 | 102/37/101 | 複数 | いいえ |
| **FOCI** | LVLM細粒度分類（多肢選択・hard negative） | 5データセット＋ImageNet-21k 4サブセット | 複数（新標準） | いいえ（2024だが2025-26で標準化） |
| **Finer** | 属性中心・複数粒度 | 6ベンチ拡張 | 複数 | いいえ（2024） |
| V*Bench | 高解像度・小領域知覚 | 191枚(属性認識115問4択＋空間関係76問2択、平均2246×1582px) | 多数（知覚系の定番） | いいえ（2024） |
| HR-Bench | 高解像度知覚 | 4K/8K | 複数 | いいえ（2024/AAAI2025） |
| MMVP | CLIP-blindペア視覚欠陥 | 150ペア | 多数 | いいえ（2024） |
| BLINK | 知覚できるが推論できない | 14タスク | 複数 | いいえ（2024） |
| MME-RealWorld | 高解像度実世界 | 大規模 | 複数 | いいえ（2024） |
| MMMU/MMBench/SEED-Bench | 総合能力（補助） | 大規模 | 多数（補助） | いいえ |

**定番の推奨**：この分野で対象命名を出すなら、まず **(A) 細粒度分類の中核：CUB＋Stanford Cars＋FGVC-Aircraft（＋iNaturalist で長尾）**、**(B) LVLM 専用の対象命名標準：FOCI（多肢選択）＋Finer（複数粒度）**、**(C) 知覚限界の診断：V*Bench＋HR-Bench（手がかりが小領域にある対象向け）**、の3層で測るのが定型。

### ストーリーの型の分析
- **新規性の置き所の分布**：2025-2026の対象命名研究では、**「生成（推論時の工夫）」に新規性を置く型が最多**（DyFo, MLLMs Know Where to Look, AutoSEP, SARE）。次いで**「評価・ベンチマーク提案」**（FOCI／Finer の系譜と各種 fine-grained 診断ベンチ）。**「学習手法」に主軸を置く型は相対的に少数**で、置く場合もデータ生成とセット（Finedefics, Fine-R1）。純粋に「学習データ」だけを新規性にする例は稀。
- **残り観点の「標準」採用根拠**：学習データは「先行研究の踏襲（CUB／Cars／Aircraft の6点セット）」がほぼ無条件の標準。評価は「FOCI が多肢選択の曖昧性問題を解決した」ことを根拠に採用。FOCI は「Existing evaluation methods for fine-grained object classification, such as open-ended question answering, are ill-defined due to ambiguous answer granularity and incomplete admissible label sets」（abstract）と、自由記述採点の限界を明示的に正当化している。
- **観点間の依存の筋**：training-free 系は「学習データ不要→凍結モデルの内部情報（attention）or 外部専門家で推論を強化→既存ベンチで検証」という筋。学習系は「FGVR 失敗は object-category misalignment が原因（診断）→だからこの対照学習／CoT データが要る→FGVR データセット＋FOCI で検証」という筋。
- **ablation の集中先**：生成型は推論コンポーネント（クロップ数、探索深さ、専門家の種類）に集中。学習型はデータ構成（属性の有無、hard negative の有無）と目的関数に集中。
- **典型的な型と主張の担保**：
  - **型1「推論時の工夫＋学習なし＋既存ベンチ」**（DyFo, MLLMs Know Where to Look）：担保は「複数の凍結モデル・複数ベンチで一貫した改善」＋「training-free ゆえ汎用」。V*/SEAL は V*Bench 全体で75.39%を達成し、GPT-4V(54.97%)・Gemini Pro(48.16%) を上回ることで「視覚探索機構の必要性」を主張（arXiv:2312.14135, Table 1）。
  - **型2「新データ＋事後学習＋（既存＋提案）ベンチ」**（Finedefics, Fine-R1）：担保は「同規模モデルの SOTA 超え」＋「診断→処方の論理」。
  - **型3「診断・ベンチ提案（手法なし）」**（FOCI, Finer, MMVP 系）：担保は「多数モデルの横断評価」＋「既存ベンチとの相補性の実証」。FOCI は12の public LVLM を評価し「Crucially, CLIP models exhibit dramatically better performance than LVLMs」という反直感的発見（エンコーダと LLM の alignment gap）で価値を主張している。

### 評価方法の再現可能な詳細
- **FOCI の手順（最も厳密に記述された例）**：原論文 Figure 2 は「We compute the CLIP cosine similarity between a test image and class labels; we select the correct label and the three most similar (wrong) labels to formulate a multiple-choice problem, which is given to the LVLM who has to predict the correct choice」と記述。すなわち **①テスト画像と各クラスラベルの CLIP コサイン類似度を計算→②正解ラベルと最も類似する誤りラベル3つを選び4択を構成→③LVLM に正解の選択肢を予測させる**。正解位置は A-D で均衡化し、CLIP zero-shot 分類を上限（upper bound）として併記。
- **vocabulary-free（E-FineR／FineR）の手順**：cACC＝予測クラスタと真ラベルのハンガリアンマッチング後の精度、sACC＝予測名と真名の Sentence-BERT 埋め込みコサイン類似度。自由記述の同義語・粒度問題を吸収する。
- **候補集合の作り方**：FOCI は視覚的近さ（CLIP 類似度）で hard negative を採掘、候補数は4。あなたの8択（視覚的に近い別製品7）は FOCI と同系統だが候補数が多い（より難しい設定）。

### こちらの設定に近い順・上位5件

1. **FOCI（EMNLP2024、基礎だが最も近い）**：画像から対象名を多肢選択で答えさせ、**視覚的に近い hard negative を CLIP で採掘**する点があなたの8択と完全に同型。あなたの「7つの視覚的に似た製品名を混ぜた8択」は FOCI の4択を拡張したもの。重なり：候補集合の作り方（視覚的近さ）、多肢選択採点。相違：FOCI は質問文（選択肢）を与える多肢選択、あなたは画像だけから名前を出させる。→**並べるべき第一の既存ベンチ**。

2. **Finedefics（ICLR2025）**：FGVR 失敗を object-category misalignment と診断し対照学習で処方。あなたが「事後学習」を想定する場合の最も近い設計。FOCI も評価に併用。重なり：FGVR データセット、hard negative、事後学習。相違：あなたの珍しい製品（事前学習にほぼ現れない）に対する未学習カテゴリ一般化は未対応。

3. **E-FineR（ICCVW2025）／ FineR 系**：vocabulary-free（語彙を与えない）で、質問文なしに近い。cACC／sACC で自由記述を採点。重なり：質問文／語彙なしでの命名、training-free、珍しいカテゴリ。相違：採点が embedding 写像であなたの多肢選択と異なる（採点方式の格上げ候補）。

4. **DyFo（CVPR2025）／ MLLMs Know Where to Look（ICLR2025）**：**手がかりが小さな部分にある対象での失敗**というあなたの観察に直結。小領域を切り出す推論時の工夫。重なり：局所的手がかりの重要性、training-free。相違：これらは「どこを見るか」を測るが「粒度が対象ごとに違う」ことは明示的に測っていない。

5. **AutoSEP（NeurIPS2025）／ SARE（arXiv2026）**：未ラベルデータや適応的推論で細粒度 zero-shot 分類を強化。凍結汎用 VLM を前提とする点があなたの一方の設定（学習なし）に一致。重なり：training-free、凍結 VLM、細粒度。相違：製品ドメイン・当て直し採点なし。

### 被りの判定（あなたの4つの設計要素）
1. **質問文なしの粒度切り替え（必要な粒度が対象ごとに違う）**：Finer（EMNLP2024）が複数粒度（super-ordinate／coarse／fine）を測る枠組みを持つが、**「対象ごとに必要粒度が動的に変わる」ことを主軸に測った査読付き2025-2026論文は未確認**。部分的先行のみ。→**新規性あり**。
2. **手がかりの局所性の測定**：V*Bench／DyFo／MLLMs Know Where to Look が「小領域の手がかり」を扱うが、**「手がかりが局所か大域かで成否が分かれることを対象命名で体系的に測る」枠組みは未確認**。→**新規性あり**。
3. **当て直し（retrieval／listener）による採点**：**対象命名タスクの査読付き2025-2026論文では皆無**。listener／reference-game の枠組みは arXiv-only（Vision-Language Model Dialog Games, arXiv:2502.02740）か、非命名文脈（Listener-Rewarded Thinking, arXiv:2506.22832、v3は撤回）のみ。→**最も差別化できる**。
4. **未学習カテゴリでの一般化（事前学習にほぼ現れない珍しい製品）**：vocabulary-free／open-set FGVR（E-FineR, FineR, NeaR）が近いが、**製品ドメインの真の長尾・未学習カテゴリを主対象にした査読付き例は少ない**。→**部分的新規性**。

**総合判定**：あなたの4要素を**1本に統合した研究は本調査の範囲では確認できなかった**。特に「当て直し採点」と「粒度が対象ごとに動的に変わることの測定」が最も未開拓。8択の多肢選択は FOCI と同系で「実装上の都合」という認識は正しく、embedding 写像や当て直しへ移行すれば差別化が明確になる。

## Recommendations

**第1段階（すぐやる）：ベンチマーク接続の確定**
- **FOCI を第一の比較対象に据える**。あなたの8択は FOCI の4択・CLIP hard negative 採掘と同型。FOCI プロトコルであなたの製品ベンチを再構成し、直接比較可能にする。
- 併せて **CUB＋Stanford Cars＋FGVC-Aircraft（＋iNaturalist）**で汎用性を示し、**V*Bench／HR-Bench** で「局所手がかり」仮説を裏付ける。
- しきい値：FOCI 型多肢選択で SOTA VLM（Qwen2.5-VL, InternVL3）との差が明確に出るなら、製品ドメインの固有性が主張できる。

**第2段階：採点方法の格上げ**
- 多肢選択（実装都合）から、**vocabulary-free の cACC／sACC（FineR／E-FineR 系）**と**当て直し（retrieval／listener）採点**へ拡張。当て直し採点は査読付き2025-2026で空白なので、ここを主要な方法論的貢献にできる。
- LLM-as-judge を使うなら、判定モデル・プロンプト・人手一致率（κ）を必ず報告（MemEye の κ=0.94、97.2%一致が良い前例）。その信頼性の議論（位置バイアス・verbosity バイアス）も明記する。

**第3段階：新規性の配置**
- 新規性を**「評価（粒度切り替え＋局所性測定＋当て直し採点）」に置く診断・ベンチ型**にするのが、既存の空白と最も整合する。FOCI や Finer が「評価の曖昧性解決」で価値を得た筋を踏襲。
- 事後学習を加えるなら、Finedefics 型（診断→対照学習／CoT）か Fine-R1 型（CoT-SFT＋GRPO）を借用し、新規性は評価側に残す。
- ベンチマーク単独か手法も出すかの判断しきい値：あなたのデータで既存 VLM が体系的に失敗する（局所手がかりで顕著に落ちる）パターンを定量化できれば、診断型単独でもトップ会議の価値がある（FOCI・MMVP の前例）。

## Caveats
- **検索範囲**：CVPR／ICCV／ECCV／WACV／NeurIPS／ICLR／ICML／AAAI／EMNLP／ACL の2025-2026採録を中心に、fine-grained／vocabulary-free／visual search／対象命名の各観点で調査。網羅的ではなく、ニッチな語彙の論文を取りこぼす可能性がある（Lin サーベイも「recall may miss niche synonyms」と注意）。
- **arXiv のみ／未確認**：SARE（arXiv2026）は査読付き採録未確認。当て直し採点関連（arXiv:2502.02740, arXiv:2506.22832）は arXiv のみで、後者 v3 は撤回。これらは本文で別枠明記した。NeaR は会議ではなく論文誌 TMLR、E-FineR は ICCV 本会議ではなくワークショップ（MMFM）である点に注意。
- **「見つからなかった」の明示**：対象命名タスクで (a) 当て直し（retrieval／listener）採点、(b) 対象ごとの動的粒度切り替えを主軸にした査読付き2025-2026論文は、上記検索範囲では確認できなかった。これは「空白＝機会」を意味する重要な発見だが、検索の限界による見落としの可能性は残る。
- **数値の出典**：VLM シェア（39.5%／40.7%）は Lin (arXiv:2510.09586、要旨のみの解析)。SEAL のクロップ数4.65は二次引用（arXiv:2506.14821）。FOCI の4択構成と CLIP hard negative は原論文 Figure 2 で確認済み。V*Bench の75.39% は原論文 Table 1。venue 確認は各会議ページ・OpenReview・ML Anthology・CVF Open Access で検証済み。

## 参考文献（正式タイトル・著者・会議・年・arXiv・実装）
1. G. Geigle, R. Timofte, G. Glavaš. "African or European Swallow? Benchmarking Large Vision-Language Models for Fine-Grained Object Classification (FOCI)." EMNLP 2024 (main), pp.2653–2669. arXiv:2406.14496. https://github.com/gregor-ge/FOCI-Benchmark
2. J. Kim, H. Ji. "Finer: Investigating and Enhancing Fine-Grained Visual Concept Recognition in Large Vision Language Models." EMNLP 2024 (main). arXiv:2402.16315. https://github.com/wjdghks950/Finer
3. H. He, G. Li, Z. Geng, J. Xu, Y. Peng. "Analyzing and Boosting the Power of Fine-Grained Visual Recognition for Multi-Modal Large Language Models (Finedefics)." ICLR 2025 (Poster). arXiv:2501.15140. https://github.com/PKU-ICST-MIPL/Finedefics_ICLR2025
4. H. He, Z. Geng, Y. Peng. "Fine-R1: Make Multi-modal LLMs Excel in Fine-Grained Visual Recognition by Chain-of-Thought Reasoning." ICLR 2026. arXiv:2602.07605. https://github.com/PKU-ICST-MIPL/FineR1_ICLR2026
5. G. Li, J. Xu, Y. Zhao, Y. Peng. "DyFo: A Training-Free Dynamic Focus Visual Search for Enhancing LMMs in Fine-Grained Visual Understanding." CVPR 2025 (Highlight). arXiv:2504.14920. https://github.com/PKU-ICST-MIPL/DyFo_CVPR2025
6. J. Zhang, M. Khayatkhoei, P. Chhikara, F. Ilievski. "MLLMs Know Where to Look: Training-free Perception of Small Visual Details with Multimodal LLMs." ICLR 2025. arXiv:2502.17422. https://github.com/saccharomycetes/mllms_know
7. (AutoSEP) T.-Y. Hong et al. "Unlabeled Data Improves Fine-Grained Image Zero-shot Classification with Multimodal LLMs." NeurIPS 2025 (Poster). arXiv:2506.03195. OpenReview: VNTj7PGlrz
8. H. C. Kuchibhotla, S. S. Kancheti, A. G. Reddy, V. N. Balasubramanian. "Efficient Vocabulary-Free Fine-Grained Visual Recognition in the Age of Multimodal LLMs (NeaR)." TMLR 2025（査読付き論文誌）. arXiv:2505.01064. OpenReview: FvA0UMw9X2
9. (E-FineR) Demidov et al. "Vocabulary-free Fine-grained Visual Recognition via Enriched Contextually Grounded Vision-Language Model." ICCV 2025 Workshop (MMFM). arXiv:2507.23070. CVF Open Access（ICCVW2025）
10. Yang, He et al. "SARE: Sample-wise Adaptive Reasoning for Training-free Fine-grained Visual Recognition." arXiv-only 2026. arXiv:2603.17729【査読付き採録未確認】
11. R. Xiao, S. Kim, M.-I. Georgescu, Z. Akata, S. Alaniz. "FLAIR: VLM with Fine-grained Language-informed Image Representations." CVPR 2025. arXiv:2412.03561. https://github.com/ExplainableML/flair
12. P. Wu, S. Xie. "V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs (SEAL, V*Bench)." CVPR 2024（基礎）. arXiv:2312.14135
13. F. Lin. "Vision Language Models: A Survey of 26K Papers (CVPR, ICLR, NeurIPS 2023–2025)." arXiv:2510.09586（計量調査）
14. Z. Liu et al. "RAR: Retrieving And Ranking Augmented MLLMs for Visual Recognition." arXiv:2403.13805（基礎）
15. H. Shen et al. "ZoomEye: Enhancing Multimodal LLMs with Human-Like Zooming Capabilities through Tree-Based Image Exploration." EMNLP 2025. arXiv:2411.16044
16. Z. Yuan et al. "Visual-RFT: Visual Reinforcement Fine-Tuning." arXiv:2503.01785（GRPO for fine-grained classification/detection の代表例）
17.（参考・別枠 arXiv／非命名文脈）K. Konyushkova et al. "Vision-Language Model Dialog Games for Self-Improvement." arXiv:2502.02740；A. Gambashidze et al. "Listener-Rewarded Thinking in VLMs for Image Preferences." arXiv:2506.22832（v3撤回）