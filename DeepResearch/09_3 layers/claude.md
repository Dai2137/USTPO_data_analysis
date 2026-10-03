# 微細形状識別ベンチマークのための事後学習手法：能力3層分解による包括的文献調査

## TL;DR
- **層A（視覚的保持）は事後学習で最も明快に伸ばせる**：DIVA・GenHancer・un²CLIP・FG-CLIP が MMVP-VLM で一貫して +3〜13ポイント改善し、「エンコーダ表現の書き換えでゼロショットを壊さない」レシピが確立している。ただし改善幅は小さく、MMVP-VLM の最良 CLIP（DFN ViT-H-14）でも平均39.3%で、人間の95.7%に遠く及ばない。
- **層B（視覚-意味接地）は「保持できているのに接地で落ちる」失敗を減らす方向で進展**：S-VCO・RLHF-V・Finedefics 等の対照・選好学習が幻覚を最大22%削減する。ただし多くは自然画像・領域テキスト前提で、線画×タイトルN択という設問形式への直接転移は未検証。
- **層Reasoning（比較推論）は「推論を伸ばしても知覚が律速する」証拠が急増**：Perception-R1 は既存RLVRが知覚を統計的に有意に改善しないこと（McNemar検定）を示し、失敗の72〜78%が知覚エラーと報告した。事後学習の投下先としては、知覚側（層A/B）の費用対効果が高いことを示唆する。

## Key Findings
1. 本ベンチマークが測る能力は、先行研究の用語では A=「visual detail retention / CLIP-blind / encoder bottleneck」、B=「visual-semantic grounding / grounded perception / modality alignment / object-category alignment」、Reasoning=「visual comparative reasoning / difference reasoning / fine-grained visual CoT」に対応する。
2. 「blindな当てずっぽうを封じる」設計思想は NaturalBench（対で逆答えを要求）と MMVP（CLIP-blindペア）が確立済みで、本研究の設問設計はこの系譜に正当に位置づけられる。
3. 事後学習の投下先としては、複数の attribution 研究が「知覚（perception）が律速であり reasoning 増強だけでは頭打ち」と結論する。ただし本設定は「DINOv2 埋め込みで酷似化した誤答」を使うため、層Aの改善余地自体が構造的に限られる可能性があり、層Bの「接地」が主戦場になりうる。
4. SFT と DPO/RL の比較では、DPO/RL の方が視覚エンコーダ表現を質的に改善する（線形プローブ・Grad-CAM局在）という一次証拠がある（PIVOT）。

---

## 層A：視覚的保持（visual retention / encoder bottleneck）

### 1. 呼称と定義
先行研究はこの能力を「fine-grained visual perception / visual detail capturing ability」（DIVA, un²CLIP）、「CLIP-blind」（Tong et al., "Eyes Wide Shut?"）、「visual shortcomings」と呼ぶ。核心は、CLIP のようなコントラスト学習の視覚埋め込みが、向き・数・色・構造など微細差を保持できず、コサイン類似度上ほぼ同一に潰れる「CLIP-blind pair」を生む点にある。命名・言語は関与せず、埋め込み段階で情報が落ちれば下流で復元不能、という切り分けが本層の定義に対応する。

### 2. 診断法・ベンチ
- **MMVP-VLM**（Tong et al., CVPR 2024）：CLIP-blind ペアを9つの視覚パターン（向き、数、色、構造など）に整理し、CLIP系エンコーダ単体の判別力を測る。各パターンは15の text-image ペアで表現される。人間が平均95.7%正答するのに対し、最良 CLIP（DFN ViT-H-14, 224²）でも平均39.3%にとどまり、論文は「9つの視覚パターンのうち7つは、いかなる大規模 CLIP でも解決できない」と結論する。
- **CLIP vs DINOv2 の埋め込み距離分析**：CLIP コサイン類似 >0.95 かつ DINOv2 <0.6 で CLIP-blind ペアを機械抽出（本研究が DINOv2 埋め込みで誤答を作る手法と同型）。
- **linear probe / segmentation probe**：エンコーダを固定し表現の質を測る（ImageNet 線形プローブ、ADE20K・Pascal Context のセグメンテーション）。

### 3. 事後学習でAを改善した手法（表）

| 手法 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチ | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| DIVA | 2024/25 | ICLR 2025 | OpenAI/EVA/MetaCLIP/SigLIP系CLIP | 拡散モデルの生成フィードバック（自己教師、画像のみ）＋dense recap | CC-3M中心 | MMVP-VLM, LLaVA, MMBench, ADE20K, Pascal Context | MMVP-VLM +3〜7% | 29の分類・検索ベンチでゼロショット維持 | arxiv.org/abs/2407.20171 |
| un²CLIP | 2025 | NeurIPS 2025 | OpenAI/OpenCLIP/SigLIP | unCLIP生成器の逆変換で画像エンコーダを微調整 | 画像のみ、Stable unCLIP基盤（SD2ベース） | MMVP-VLM | OpenAI ViT-L-14@224 で 19.3→32.6%（DIVA の25.9% を上回る） | テキストエンコーダとの整合を保持 | arxiv.org/abs/2505.24517 |
| GenHancer | 2025 | ICCV 2025 | OpenAICLIP/MetaCLIP/SigLIP | 軽量生成器を2段階でスクラッチ学習し表現強化（Stage2でLoRA rank16） | CC3M 各1エポック | MMVP-VLM | OpenAICLIP +6.0%（19.3→31.9） | MLLMにプラグインしvision-centric向上 | arxiv.org/abs/2503.19480 |
| FG-CLIP | 2025 | ICML 2025 | CLIP | 大規模再学習型（長文キャプション＋領域監督＋ハードネガ）2段階階層学習 | 16億長文キャプションペア、1200万画像・4000万領域ボックス、1000万ハードネガ（FineHARD） | 細粒度理解・retrieval | 細粒度理解で既存CLIPを上回る | 双方向retrieval維持 | arxiv.org/abs/2505.05071 |

### 4. 「エンコーダ表現だけを書き換える」ことの限界と副作用
DIVA/GenHancer/un²CLIP は LLM・projector を触らずエンコーダ表現を改善する路線だが、限界がある：(1) 改善幅は MMVP-VLM で数〜十数ポイントに留まり、人間水準（95.7%）とは依然大差。(2) 領域テキストペア収集がボトルネック（FG-CLIP は1000万ハードネガを人手・生成で用意）。(3) un²CLIP論文が指摘するように、アーキ変更・追加エンコーダ・高コスト再学習を避けつつ「テキスト整合性の保持」と「細部保持」を両立させる設計が必要で、両者はトレードオフしうる（GenHancer は「完璧な生成が必ずしも良い表現を生まない」と報告）。

**この研究への含意**：層Aの事後学習レシピ（生成フィードバックでエンコーダ表現を書き換え、ゼロショットを壊さない）は確立され、破滅的忘却を避ける方法論も揃っている。ただし本ベンチは「DINOv2 埋め込みで酷似化した誤答」を使うため、DINOv2的な形状特徴を足しても誤答との分離が進みにくい可能性がある。層A単独の改善は必要条件だが十分ではない、という位置づけが妥当。

---

## 層B：視覚-意味接地（visual-semantic grounding）

### 1. 呼称と定義
「grounded perception」「visual grounding」「modality alignment」「object-category alignment」（Finedefics）など。狭義は領域局在（bounding box）、広義は「回答が視覚証拠に固定されていること（言語プライアに流れない）」。本研究の失敗形「尤もらしいが画像に裏付けのない説明の捏造」は後者＝ungrounded hallucination に対応する。Finedefics は FGVR の失敗を「物体情報の抽出・カテゴリ知識の保持・物体-カテゴリ整合」に分解し、根本原因を「整合（alignment）の失敗」と位置づけた。

### 2. 診断法・ベンチ
- **NaturalBench**（NeurIPS 2024, Datasets & Benchmarks）：2画像×2質問で答えを交替させ「blind solution」を封殺。10,000の人手検証VQAサンプル。BLIP-3・LLaVA-OneVision・Cambrian-1・Qwen2-VL・GPT-4o を含む53のVLMが人間（90%超）に50〜70%劣後。本研究の「設問文だけからは等尤」設計と同型の思想。
- **MMVP**（150ペア300問）：CLIP-blind を言語質問化。
- **POPE**：物体存在の Yes/No ポーリング（random/popular/adversarial の3設定）で物体幻覚を測定。
- **HallusionBench**（CVPR 2024）：455の視覚-質問制御ペア（346図、1129問）で言語幻覚と視覚錯覚を切り分ける人手診断。
- **SPEC**（CVPR 2024）：size/position/existence/count を1属性だけ変えた候補群で診断（4つの主要VLMがほぼ偶然レベル）。

### 3. 事後学習でBを改善した手法（表）

| 手法 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチ | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| RLHF-V | 2023/24 | CVPR 2024 | Muffin/LLaVA | セグメント単位の訂正的人間フィードバック＋dense DPO（DDPO） | 人手訂正フィードバック（少量で効率的） | Object HalBench, MHumanEval等5種 | Object HalBenchの物体幻覚を相対75.8%減 | helpfulness（MMHalBench, VQAv2）維持 | arxiv.org/abs/2312.00849 |
| S-VCO | 2025 | ACL 2025 | LLaVA-Interleave系VLM | 対称視覚コントラスト最適化（DPO系）＋最小視覚差データMVC | MVC（視覚反実仮想を自動フィルタ・拡張） | 幻覚・vision-centric系 | 幻覚を最大22%削減、視覚依存が高いベンチほど改善大 | ScienceQA等知識系のみ微減 | arxiv.org/abs/2502.13928 |
| Finedefics | 2025 | ICLR 2025 | Idefics2 | 属性拡張アラインメント（A³）＋対照学習（ハードネガ＝類似誤カテゴリ） | 開/閉集合FGVRデータ | 6 FGVRデータセット | Idefics2/Qwen-VL-Chatを有意に上回る（LLaVA1.5に適用で平均+13.97%） | 汎用性を確認 | arxiv.org/abs/2501.15140 |
| AHNPL | 2025 | IJCAI 2025 | CLIP | テキストハードネガを視覚領域へ変換＋動的マージン対照学習 | ARO/VALSE/SugarCrepe | 構成推論（CR） | CE-CLIP超え、CLIP比+3.5〜4.8% | — | arxiv.org/abs/2505.15576 |
| CLoVe | 2024 | arXiv（高被引用） | CLIP | 合成キャプション＋ハードネガテキスト＋model patching | 合成キャプション画像 | ARO等構成性、ImageNet | 構成性ベンチ+10%超 | patch（α≈0.4-0.7）で物体認識性能を保持し忘却を緩和 | arxiv.org/abs/2402.15021 |

### 4. 「A成立・B失敗」を示した分析
Finedefics は「MLLMは物体情報抽出・カテゴリ知識保持は概ね可能だが、物体を下位カテゴリに整合させる段で失敗する」ことを実証し、A（保持）が成立してもB（接地）で落ちる典型を示した。S-VCO も「VLMは画像内容を無視し言語プライアに過度依存する」ことを前提に、視覚細部とテキストトークンの整合を明示的に学習させる設計であり、失敗を接地段に帰属させている。

**この研究への含意**：本ベンチの主戦場は層Bである可能性が高い。誤答がDINOv2で酷似化されている＝形状特徴の「保持」だけでは分離できず、微細差を正しい製品タイトル（概念）に接地する能力が問われる。S-VCO/Finedefics型の「最小視覚差ハードネガ＋対照/選好学習」は、本ベンチのLoRA後の伸び悩み（+1.9pt）を超えるレシピの最有力候補。DINOv2で作った酷似ペアはそのまま「最小視覚差ハードネガ」に転用できる。ただし既存手法は自然画像・領域テキスト前提で、線画×タイトルN択への転移は未検証のギャップ。

---

## 層Reasoning：比較推論（visual comparative reasoning）

### 1. 呼称と定義
「visual comparative reasoning」「difference reasoning / spot-the-difference」「fine-grained visual CoT」「multi-image reasoning」。酷似候補を明示的に見比べ、差分を根拠に判断を導く能力。

### 2. 診断法・ベンチ
- **BLINK**（ECCV 2024）：相対深度・視覚対応・多視点など14の古典CV課題を3,807問のMCQに再構成。人間が平均95.70%正答するのに対し、最良のGPT-4V が51.26%、Gemini が45.72%で、これは偶然当てより13.17pt・7.63pt高いだけであり、論文は「こうした知覚能力はまだ出現していない」と結論する。
- **CV-Bench**（Cambrian-1, NeurIPS 2024）：2,638の手検査済み例で2D/3D空間理解を測る vision-centric ベンチ（MMVPの8.8倍規模）。
- **BLINK-Twice**（2025）：自然な敵対的画像ペア＋推論チェーン注釈で「見る（see）」を超えた「観察（observe）」を要求。
- **Visual Jigsaw / spot-the-difference系**：多画像比較・並べ替え。

### 3. 事後学習で比較推論を改善した手法（表）

| 手法 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチ | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| Visual-RFT | 2025 | ICCV 2025 | Qwen2-VL-2B/7B | GRPO＋検証可能報酬（IoU等の知覚報酬） | 少数（~100サンプル規模から） | 細粒度分類・few-shot検出・reasoning grounding | 1-shot細粒度分類で+24.3%、COCO 2-shot検出で+21.9、LVISで+15.4 | SFTより汎化良好 | arxiv.org/abs/2503.01785 |
| Visual Jigsaw | 2025 | ICLR 2026（採択、暫定） | Qwen2.5-VL系 | 自己教師RL（パッチ並べ替え、検証可能報酬、注釈不要） | 追加注釈なし（画像/動画/3D） | 細粒度知覚・時間理解・3D空間 | 各所で一貫改善 | vision-centric全般に転移 | arxiv.org/abs/2509.25190 |
| Perception-R1 | 2025 | ICLR 2026（採択、暫定） | Qwen2-VL-7B/2.5-VL-7B | RLVR（GRPO）＋視覚知覚報酬（judging LLMで注釈と応答の整合を判定） | わずか1,442サンプル | MathVista, MathVerse等 | 全ベンチSOTA級（200Kデータのvision-R1を上回る） | データ効率が極めて高い | arxiv.org/abs/2506.07218 |
| ViCrit | 2025 | NeurIPS 2025 | Qwen2.5-VL-7B/72B | GRPO＋キャプションに注入した幻覚スパンの特定（完全一致報酬） | 875Kの画像-改変キャプションペア | MathVision, VLMsAreBlind, ChartXiv等 | 72Bで8ベンチ平均59.78→63.16（7B/72Bで+2.4/+3.4%）、CHAIR幻覚も減 | 汎用VLベンチで7/8タスクSOTA | arxiv.org/abs/2506.10128 |
| TPO（Temporal Preference Optimization） | 2025 | CVPR 2025 | LongVA-7B, LLaVA-Video | DPOによる時間的接地の選好学習（無関係/不完全フレームで選好ペア構築） | 自動生成選好ペア | Video-MME, MLVU, LongVideoBench | LongVA-7Bで+2.9〜3.1%、LLaVA-Videoで+2.3%（7B最良級） | 時間的接地を強化 | arxiv.org/abs/2501.13919 |

### 4. 推論強化と知覚能力の関係（双方向の証拠）
- **知覚が律速（reasoning増強だけでは不足）**：Perception-R1 は McNemar 検定で「既存の RLVR 手法は MLLM の多モーダル知覚能力を有効に強化できない」と示した（ベースモデル比で p=0.22 と非有意）。同論文は、Qwen2-VL-7B-IT で MathVista/MathVerse の失敗の72%・68%、Qwen2.5-VL-7B-IT で78%・76%が「多モーダル知覚エラーに起因する」と報告する。別の attribution 研究も「画像を単純なテキスト記述に置換すると Claude系で平均20点以上向上＝知覚が拘束条件」と結論。
- **知覚を直接報酬化すれば改善**：ViCrit/Visual-RFT は知覚そのものを検証可能報酬にすることで perception を伸ばし下流推論も改善。Perception-R1 も視覚知覚報酬を加えると McNemar 検定で有意（p=0.04）に改善する。「推論を伸ばす」より「知覚を報酬化する」方が効く、という非対称性が見える。

**この研究への含意**：本ベンチはCoT・多肢対比を促す層Reasoningの介入余地があるが、複数の一次研究が「知覚が律速」を示すため、reasoning強化単独では GPT-5 の51%を大きく超えにくい。むしろ ViCrit/Visual-RFT の「知覚を検証可能報酬にする」設計（＝正解タイトルと誤答タイトルの微細形状差をスパン単位で当てさせる報酬）を本設定に翻訳するのが有望。

---

## 層をまたぐ原因の帰属（attribution）

### 切り分け方法論
- **encoder bottleneck vs extraction bottleneck vs reasoning failure**：Perception-R1 は CoT 軌跡を人手分類し失敗を知覚/推論に帰属した（失敗の7割超が知覚）。"Downscaling Intelligence"（2025）は LLM 縮小時に perception と reasoning を分離評価し「小型モデルでは知覚が critical bottleneck」と結論、visual extraction tuning を提案。PuzzleVQA は正解説明を段階投入し「知覚/帰納/演繹」のどこで詰まるか特定する手法を示した。
- **入力置換法**：画像を正確なテキスト記述に置換して性能が跳ねれば失敗は知覚側、というアッパーバウンド法（"Disentangling Perception and Reasoning in Multimodal LLMs via Reward Design"）。
- **統合が真のボトルネックとの反論**："Compose and Fuse: Revisiting the Foundational Bottlenecks in Multimodal Reasoning"（OpenReview）は「知覚ではなく統合（integration）が主障壁」とし、アテンションが事実の有用性を符号化できていないこと、初期層でのモダリティ融合制御が有効なことを示す。原因帰属には論争がある。

### SFT vs DPO/RL の表現・アテンション変化
PIVOT（"RL makes MLLMs see better than SFT", ICLR 2026 採択・暫定）が最も直接的：SFT と DPO で学習後、視覚エンコーダを切り離し線形プローブ・Grad-CAM で比較する。DPO は ImageNet 線形プローブで SigLIP2-So/16+Qwen-3B で+1.83pt、SigLIP2-L/16+Qwen-1.5B で+1.96pt 高く、Grad-CAM 勾配が質問関連領域により強く整合し、vision-centric VQA で+2.4〜4.2pt 上回る。DPOのみがデータスケーリングで表現品質が向上する。「SFT Memorizes, RL Generalizes」も RL が視覚認識精度を副産物的に上げ、SFT は劣化させると報告する。

### 投下先の費用対効果
attribution 研究群は総じて「知覚（層A・B）側が律速」を示唆し、reasoning 単独増強の費用対効果は低いと読める。一方、事後学習手法としては RL/DPO が SFT より視覚表現を改善するため、**「知覚を検証可能報酬にした RL/DPO」が最も費用対効果が高い**という仮説が、複数の一次証拠から支持される。

**この研究への含意**：本研究は attribution を「A/B/Reasoningのどこで落ちるか」を切り分ける診断章を持つべき。入力置換法（線画をテキスト記述化）、線形プローブ（エンコーダ単体でのペア分離）、CoT誤り分類の3点セットで帰属を実証すれば、メインカンファレンス級の「根本原因の一般化」に接続できる。ただし「知覚律速」説と「統合律速」説は割れているため、自前の診断で決着させる必要がある。

---

## 論文のポジショニング

### メインカンファレンスに通る「識別ベンチ＋事後学習」型の構成
成功例の主張の並べ方には共通の型がある：
1. **能力プローブ化**：Eyes Wide Shut? はCLIP-blindを9パターンに一般化し「特定ドメイン」臭を消した。NaturalBench は「blind solution 封殺」という一般原理を前面に。
2. **根本原因の一般化**：Cambrian-1 は「vision-centric」という枠で視覚表現学習全体の課題に接続し、CV-Bench という一般ベンチを提示。
3. **タスク横断で転移するレシピ**：Visual-RFT/Visual Jigsaw は「1タスクの報酬設計が多タスクに転移」を示し applications 臭を回避。
4. **「接地知覚は推論の前提」への接続**：Perception-R1/ViCrit は「知覚が推論の律速」を示し、知覚改善を一般能力向上として提示。

### ドメイン語を出さない提示の事例
- MMVP / Eyes Wide Shut?：素材はCLIP-blindペアだが、タイトル・要旨は「MLLMのvisual shortcomings」という一般能力の話に抽象化。
- SPEC（"Synthesize, Diagnose, and Optimize"）：合成画像で size/position/existence/count という**一般属性**を測るとし、生成パイプラインを主役に据える。
- NaturalBench：「natural adversarial samples」「vision-centric評価」という一般語で提示し、Flickr30K等の一般画像から構築。

**この研究への含意**：本研究はタイトル・要旨から "patent" を消し、「線画という色・質感・文脈を欠く条件下での純粋形状識別＝接地知覚のストレステスト」として提示すべき。意匠図面は「言語プライアを構造的に封じる理想的テストベッド」という一般的価値で正当化し、事後学習レシピ（知覚を検証可能報酬にするRL/DPO＋最小視覚差ハードネガ）がMMVP/BLINK/NaturalBench等の既存ベンチにも転移することを示せば、industry track でなくメインに通る。

---

## Recommendations（段階的な次の一手）

**Stage 1（診断・帰属の確立）**：まず attribution を実証する。(a) 線画をテキスト記述に置換して性能が跳ねるか（知覚 vs 推論のアッパーバウンド法）、(b) エンコーダ（DINOv2/CLIP）単体の線形プローブで正解-誤答ペアが分離可能か（層A上限）、(c) GPT-5のCoT誤りを知覚/接地/推論に人手分類。閾値：置換で+15pt以上なら知覚律速＝層A/Bに投資、+5pt未満なら統合/推論を疑う。

**Stage 2（層B主軸の事後学習）**：S-VCO/Finedefics 型の「最小視覚差ハードネガ＋対照/選好学習」を線画×タイトルN択に翻訳。DINOv2 で作った酷似ペアをそのまま最小視覚差ハードネガに転用できる。目標：LoRA後の+1.9ptを明確に超える（+5pt以上）かが成否判定。CLoVe型の model patching で汎用性の破滅的忘却を防ぐ。

**Stage 3（知覚を報酬化したRL）**：ViCrit/Visual-RFT の設計を移植し、「正解と誤答の微細形状差」を検証可能報酬（正しいタイトル選択＝完全一致報酬）でGRPO学習。PIVOTの知見に従いSFTでなくDPO/RLを主軸に。閾値：8択でGPT-5ゼロショットの約51%を超えれば主要貢献。Perception-R1が1,442サンプルでSOTA級を出した事実は、少データでも成立しうることを示す。

**Stage 4（転移の実証）**：本レシピがMMVP/BLINK/NaturalBench/CV-Benchにも転移することを示し、「patent固有でない一般能力」を証明。これがメイン採択の鍵。

**方針変更のトリガー**：Stage 1で置換しても性能が上がらない（＝統合が障壁）なら "Compose and Fuse" 型の early-fusion 制御に切替。層A線形プローブで既にペア分離可能なら層Aは投資対象から外し、層B/Reasoningに集中。

## Caveats
- 2026年 arXiv 番号（Perception-R1=2506.07218 の ICLR 2026 採択、Visual Jigsaw=2509.25190 の ICLR 2026、PIVOT=2510.16333 の ICLR 2026）は査読/採択状況を暫定として扱う。検索で観測された2600番台 arXiv（DiffSpot 2605.29615, DO-Bench 2604.22822, FineBench 2605.19846 等）は実在・査読状況とも未確認で、本文では周辺情報としてのみ言及した。
- MMVP-VLM の CLIP 最良39.3%、un²CLIP の32.6%等は各一次論文の報告値だが、ベース設定（解像度・バックボーン）が異なるため直接比較は注意。
- 「知覚が律速」と「統合が律速」は attribution 研究間で結論が割れており、本研究は自前の診断で決着させる必要がある。決め打ちは避ける。
- 多くの層B/Reasoning手法は自然画像・領域テキスト・キャプション前提であり、線画×タイトルN択への転移可能性は本調査時点で未実証（＝最大の手法上ギャップ）。
- TPO は「Temporal Preference Optimization」（動画の時間的接地）を指し、本ベンチの静止画・比較推論とは対象がずれる。選好最適化を視覚接地に使う手法例として参照した。

## 各層の「現時点で言えること」と「手法上のギャップ」

**層A（視覚的保持）**
- 言えること：生成フィードバックでエンコーダ表現を書き換え、ゼロショットを壊さず MMVP-VLM を+3〜13pt改善するレシピ（DIVA/GenHancer/un²CLIP）が確立。DINOv2的形状特徴の注入や unCLIP 逆変換が有効。破滅的忘却を避ける設計（29ベンチでゼロショット維持）も揃う。
- ギャップ：改善は依然として人間水準（95.7%）に遠い。本ベンチはDINOv2で誤答を酷似化しているため、DINOv2的形状特徴の追加が誤答分離に効くとは限らない。線画ドメインでの層A改善（生成フィードバックが線画に有効か）の実証がない。

**層B（視覚-意味接地）**
- 言えること：最小視覚差ハードネガ＋対照/選好学習（S-VCO は幻覚を最大22%減、Finedefics は LLaVA1.5 適用で平均+13.97%）が「A成立・B失敗」を明示的に標的化できる。RL/DPOはSFTより視覚表現・局在を改善（PIVOT: ImageNet線形プローブ+1.8〜2.0pt、vision-centric VQA +2.4〜4.2pt）。
- ギャップ：既存手法は自然画像・領域テキスト・キャプション前提。線画×製品タイトルN択という「色・質感・文脈ゼロ」条件への転移が未検証。ハードネガをDINOv2ペアで作る発想は既存だが、線画×タイトルでの選好データ構築レシピは空白。

**層Reasoning（比較推論）**
- 言えること：知覚を検証可能報酬にするRL（ViCrit で72Bが平均+3.4%、Visual-RFT で1-shot分類+24.3%）が有効。ただし複数の一次研究が「推論増強だけでは知覚が律速」（Perception-R1: 既存RLVRは知覚を統計的に有意に改善せず、失敗の72〜78%が知覚エラー）と示し、reasoning単独の費用対効果は低い。
- ギャップ：多画像・spot-the-difference型の明示的比較を線画N択で報酬化した事後学習は未報告。「差分をスパン単位で当てさせる報酬」を本設定に翻訳する手法が空白。CoTが線画識別で知覚を助けるか害するかの定量が未知。