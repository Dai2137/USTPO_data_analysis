# ViT以後（2020年〜）の視覚言語モデルにおける「どこを・どの粒度で見るか」の制御技術：網羅的調査

## TL;DR（3行）
- **本件の核心課題（質問文なし・対象ごとに全体/局所を切り替え・疎な線画で似た意匠を識別）に4条件すべて同時充足する既存研究は存在しない。** ただし各要素は個別に成熟しており、V*/SEAL・ZoomEye・ViCrop・FOCUSといった「見直し」技術と、DeepPatent系の線画検索、CVPR2024のスケッチ説明可能性研究を組み合わせる転用余地が大きい。
- 「トークンを増やせば細部が救えるか」への答えは条件付きで否。解像度/タイル増加（AnyRes・native resolution）はOCR・小物体には効くが、CLIP系エンコーダ自体の「盲点」（MMVP：9パターン中7つがスケールに関わらず未解決）は解像度スケールでほぼ改善せず、圧縮（Q-Former・2×2マージ・剪定）は細粒度の空間情報を系統的に失う。トークン数より「どこを再エンコードするか」の制御が効く。
- 「いつ拡大するか」のゲートは、ZoomEye・FOCUSなど自己申告信頼度やトークン確信度を信号にする研究が2024〜2026年に急増したが、そのほぼ全てが**質問文に依存**する。質問文なし設定で動く純粋なゲートは事実上の空白領域である。

## Key Findings（要点）

1. **ViT特有のトークン粒度問題は「解像度」と「エンコーダ表現」の2層に分かれる。** LLaVA-NeXTのAnyRes、Qwen2-VLのNaive Dynamic Resolution、InternVLの動的タイリングは入力解像度を上げ、細部タスク（OCR・fine-grained VQA）を改善する。しかしTong et al.のMMVP（CVPR2024, arXiv:2401.06209）は、CLIPエンコーダには「CLIP-blindペア」（CLIP埋め込みは酷似するがDINOv2では明確に異なる画像対）が存在し、ネットワークサイズや解像度をスケールしても**識別された9つの視覚パターンのうち7つはスケールに関わらず未解決のまま**であることを示した。人間の正解率95.7%に対し最良のGPT-4Vでも38.7%（多くのモデルはランダム水準25%以下、最低6.0%）、CLIPとMLLMの失敗パターン相関は0.7超。つまり細部識別の失敗は解像度不足だけでなくエンコーダの表現不足に起因する。

2. **視覚トークン圧縮は必然的に細粒度を失う。** FastV・SparseVLM・VisionZipなどの剪定/マージ研究は、深い層で視覚トークンの冗長性が高いことを利用するが、UniPruneBench等のベンチは「積極的な剪定は細部タスクで深刻な性能低下を招く」と報告。Q-Former（BLIP-2）のような固定長クエリは空間情報を強く拡散させ、情報ボトルネックとして細粒度の空間精度を制限する。Qwen系の2×2隣接パッチマージも空間解像度を1/4に落とす。

3. **「どこを見るか」の制御は3系統に整理できる。** (a) モデル内部信号から切り出す（ViCrop=注意/勾配、FOCUS=キャッシュされたトークン類似度、HAVC=ヘッド選択）、(b) 探索して拡大する（V*/SEAL=外部検出器＋LLM誘導探索、ZoomEye=木探索＋自己申告信頼度、DeepEyes/Chain-of-Focus=強化学習で学習したズーム方策）、(c) 領域を明示指定する（red circle視覚プロンプト、領域トークン）。制御信号は手法ごとに質問文・確信度・外部検出器・学習方策と異なる。

4. **「いつ拡大するか」のゲートはほぼ全て質問文依存。** ZoomEyeは「回答確信度が閾値を超えたら探索終了」、FOCUSは最高確信度領域のみでVQAを実行、LookWiseはグローバル予測のトークン確信度をルーティング信号にする。いずれも「質問に答えるための」信号であり、画像だけから名前を出す設定には未対応。

5. **識別性を目的にした学習はCLIP側修復とMLLM選好最適化に分かれる。** NegCLIP（ARO、ICLR2023）はハードネガで対照学習を修正、DIVA（ICLR2025）は拡散モデルの生成フィードバックで、un²CLIPはunCLIP反転でCLIPの細部把握を強化。これらは主に**視覚側（エンコーダ）**を変える。評価はMMVP-VLM・SugarCrepe・Winoground等。ただしSugarCrepe論文（Hsieh et al., NeurIPS2023, arXiv:2306.14610）はNegCLIP系のARO改善が「アーティファクト過学習」で誇張されていると警告（「NegCLIPはアーティファクトを利用することを学習し、実際には構成性を改善していない」）。SugarCrepe上ではNegCLIPの改善幅は「どれも10%を超えない」。

6. **線画・特許図面ではViT以後の研究が薄い。** DeepPatent（WACV2022、35万図/4.5万設計特許）とDeepPatent2（Ajayi et al., Scientific Data 10, 772 (2023)、米国設計特許14年分から抽出した270万超の技術図面・13.2万物体名・2.2万視点、計314GB）が基盤データ。Transformer系検索（Higuchi & Yanai, SwinV2でmAP 0.856）とDensity-Refine（Lin, Hung, Lee, ASME JMD 2025、密度クラスタリングで教師なし局所領域抽出）が最も近い。Awale et al.（ECIR2025）はInstructBLIPで特許図面の物体名をゼロショット/少数ショット分類したが、自然画像で事前学習したMLLMは特許線画でゼロショット性能が低いと報告。

7. **疎な線画での勾配/注意マップの信頼性は明示的に否定されている。** Bandyopadhyay et al.「What Sketch Explainability Really Means for Downstream Tasks」（CVPR2024, arXiv:2403.09480）は、ピクセル単位の帰属は「空白の白ピクセルが多い疎なスケッチでは意味のある説明を与えない（such pixel attribution does not provide meaningful explanations when interpreting sparse human-drawn sketches (many empty white pixels)）」と明言し、ストロークレベル帰属（SLA/P-SLA）に切り替えた（TU-Berlin/Sketchyで検証）。VLMに遮蔽帰属を線画で適用した研究は発見できなかった。

## Details（詳細）

### 1. ViT以後の系譜（2020年〜現在）を3本の流れで整理

#### 流れA：視覚トークンの粒度と情報の損失

**解像度・タイル分割系**：LLaVA-NeXT（2024）のAnyResは画像を{2×2, 1×{2,3,4}, {2,3,4}×1}のグリッドに分割し各タイルを独立エンコードすることで、公式ブログによれば入力解像度を「4倍のピクセル」に増やし（3つのアスペクト比、最大672×672・336×1344・1344×336をサポート）、OCRと細部VQAを改善した。同ブログのアブレーションは「解像度のスケーリングはトークン数のスケーリングより効果的（the scaling of resolution is more effective than the scaling of token numbers）」と述べる。Qwen2-VL（arXiv:2409.12191）のNaive Dynamic Resolutionは任意解像度を可変長トークンにマッピングし、M-RoPEで空間位置を保持。InternVLは448×448タイルを動的数だけ切り出しサムネイルを付加する。これらは「小さな手がかり」がタイル境界内に収まれば救えるが、面の内側の微小な差（本件のAタイプ）は、そのタイル全体がさらにViTで均されるため、依然として粒度が粗い。BlueLM-V-3B（arXiv:2411.10640）はLLaVA-NeXTとInternVLの「誇張された画像拡大」問題（小さい画像を最大25倍に拡大しトークンを浪費）を指摘した。

**圧縮・剪定系の損失分析**：
- FastV（ECCV2024）：LLaVA-1.5で視覚トークンへの注意が深い層で急減することを発見し、低注意トークンを剪定。だが「関連する視覚情報のシフト」（arXiv:2604.12358）は、静的剪定が復号時に必要な情報を落とすと分析。
- トークンマージ（ToMe系）：削除より情報損失を抑えるが、平均化で細粒度を失う。VisionZipは剪定＋マージのハイブリッドだがアンカートークンが代表に失敗しうる。
- Q-Former（BLIP-2）：固定長クエリで大量の視覚特徴を少数の潜在トークンに圧縮。「Cross-Layer Visual Anchors」論文（arXiv:2603.25088）は「Q-Formerでは空間情報が既に高度に拡散している」と指摘。
- **重要な切り分け**：トークン数を増やすこと自体は細部の「入り口」を広げるが、(i) CLIP系エンコーダの盲点（MMVP）、(ii) 圧縮での空間拡散、の2要因は数を増やしても解けない。「Position: Reasoning After Perception」（arXiv:2507.16863）はQwen2.5-VLで「視覚エンコーダを更新する設定だけが実質的な改善をもたらし、言語側やアダプタのみの更新はほぼ無効」と報告、これは細部の限界が視覚エンコーディング段階の情報損失に由来することの直接証拠。

#### 流れB：どこを見るかの制御

| 手法 | 制御信号 | 機構 |
|---|---|---|
| ViCrop（arXiv:2310.16033） | 質問文誘導の注意/勾配マップ | 訓練不要、Q-Former注意と回答勾配でヒートマップ生成→切り出し |
| FOCUS（NeurIPS2025, arXiv:2506.21710） | キャッシュされたトークン類似度（内部表現） | 訓練不要、tree searchや勾配に依存しない、FlashAttention互換 |
| HAVC（arXiv:2601.22483） | OCR診断で選抜した注意ヘッド＋空間エントロピー＋勾配 | 訓練不要、ヘッド選択で注意ノイズを低減 |
| V*/SEAL（CVPR2024, arXiv:2312.14135） | LLMの世界知識＋外部検出器 | LLM誘導視覚探索、要fine-tuning、A100で1標的あたり約6秒 |
| 視覚プロンプト（red circle, arXiv:2304.06712） | 人手/外部指定の領域 | 画像に赤丸を描きCLIPの注意を誘導 |

ViCropは「テキスト読み取り・物体属性・分類」の質問で一貫して改善するが「位置特定・カウント」では悪化すると報告（本件の識別タスクは分類寄りなので好適）。red circle論文（ICCV2023）はCUBデータセットでキーポイント命名精度46.5%（切り出し25.5%、ランダム8.2%）を達成し、切り出しより文脈を保持できることを示した。

#### 流れC：いつ拡大するかのゲート（最重要）

- **ZoomEye**（EMNLP2025 Oral, arXiv:2411.16044）：画像を階層木として扱い、各ノードで関連物体の存在を問う自己申告確信度でノード優先度を決め、確信度が閾値を超えたら探索終了。**InternVL2.5-8BでHR-Benchが+15.71%と+17.69%、LLaVA-v1.5-7BでV*Bench +34.57%、Qwen2.5VL-3BはHR-Bench 8Kで68.38%とGPT-4o（55.5%）を上回った。** **信号＝自己申告確信度、閾値＝事前定義、質問文必須。**
- **DyFo**（arXiv:2606.26196で言及）：Monte Carlo木探索による訓練不要の動的視覚探索。
- **DeepEyes**（arXiv:2505.14362）：cold-start SFTなしのend-to-end RLでズームイン関数をネイティブに起動。「各テキストCoT後に直接回答するかズームインするかを自律的に決定」。**信号＝学習した方策（結果報酬）、質問文必須。**
- **LookWise**（arXiv:2603.00171）：初回グローバル予測のトークン確信度をルーティング信号にし、「多くの訓練不要手法が全入力を切り出して視覚的に単純なサンプルで計算を浪費する」問題を回避。
- **CARES**（arXiv:2510.19496）：Context-Aware Resolution Selectorで、必要な解像度を入力ごとに選択。ナイーブな縮小より高精度を低計算で回復。
- **閾値の移植性**：これらの閾値較正は各ベンチ（V*Bench・HR-Bench）で調整されており、別ドメイン（線画）への移植性は検証されていない。

### 2. 論文一覧の表（査読済みを優先、arXivは明示）

| 論文名 | 年・会議 | 査読 | 視覚エンコーダ/入力粒度 | どこを見るか | いつ拡大するか | 質問文 | ドメイン | 線画検証 | 実装公開 |
|---|---|---|---|---|---|---|---|---|---|
| Eyes Wide Shut?（MMVP） | CVPR2024 | ○ | CLIP ViT各種 | — | — | 対で提示 | 自然画像 | × | ○ |
| V*/SEAL | CVPR2024 | ○ | CLIP+外部検出器 | LLM誘導探索 | 探索停止規則 | 必須 | 高解像度自然画像 | × | ○ |
| ZoomEye | EMNLP2025 | ○ | 任意MLLM/木構造 | 木探索 | 自己申告確信度＋閾値 | 必須 | 高解像度自然画像 | × | ○ |
| FOCUS | NeurIPS2025 | ○ | LLaVA/OneVision | トークン類似度 | 最高確信度領域 | 必須 | V*Bench, HR-Bench | × | ○ |
| red circle視覚プロンプト | ICCV2023 | ○ | CLIP | 外部指定領域 | — | 任意 | 自然画像・RefExp | × | ○ |
| NegCLIP（ARO） | ICLR2023 | ○ | CLIP（対照学習改） | — | — | — | 合成/自然 | × | ○ |
| DIVA | ICLR2025 | ○ | CLIP＋拡散feedback | — | — | — | MMVP-VLM等 | × | ○ |
| Sketch Explainability（SLA） | CVPR2024 | ○ | SBIRネット（CLIP+prompt learning） | ストローク帰属 | — | — | **スケッチ** | **○** | ○ |
| DeepPatent/PatentNet | WACV2022 | ○ | ResNet50（mAP 0.376） | — | — | — | **設計特許線画** | **○** | ○ |
| Patent img. retrieval (metric) | World Patent Info 2023 | ○ | SwinV2 (mAP 0.856) | — | — | — | **特許線画** | **○** | 一部 |
| Density-Refine | ASME JMD 2025 | ○ | ViT＋密度クラスタ | 密度で教師なし領域抽出 | — | — | **特許線画** | **○** | 不明 |
| Patent Figure Classification (LVLM) | ECIR2025 | ○ | InstructBLIP | — | — | 必須 | **設計特許図面** | **○** | 一部 |
| ViCrop | arXiv:2310.16033 | △ | BLIP/MLLM | 注意/勾配 | 常時切り出し | 必須 | 自然画像VQA | × | ○ |
| FastV | ECCV2024 | ○ | LLaVA | 注意で剪定 | — | 依存 | 汎用VQA | × | ○ |
| DeepEyes | arXiv:2505.14362 | × | Qwen2.5-VL | RL方策 | 学習した方策 | 必須 | 高解像度 | × | ○ |
| LookWise | arXiv:2603.00171 | × | MLLM | 内部信号 | トークン確信度ルータ | 必須 | fine-grained VQA | × | 不明 |
| HAVC | arXiv:2601.22483 | × | LLaVA/InstructBLIP | ヘッド選択注意 | 常時切り出し | 必須 | fine-grained VQA | × | 不明 |
| Zooming without Zooming (R2I) | arXiv:2602.11858 | × | MLLM | 訓練時に内在化 | 単一フォワード | 必須 | fine-grained VQA | × | 不明 |
| CropVLM | arXiv:2511.19820 | × | SmolVLM等 | 学習したクロッパ | — | 必須 | DocVQA等 | × | 一部 |
| un²CLIP | arXiv:2505.24517 | × | CLIP（unCLIP反転） | — | — | — | MMVP-VLM | × | 一部 |

（注：arXiv番号のうち2026年以降の一部プレプリントは査読前。ECCV/NeurIPS/EMNLP採択は査読済みとして扱った。ViCropはWACV系で査読状況が版により異なるため△とした。）

### 3. 3つの問いへの直接回答

**Q3-1：質問文が無い状態で、全体と局所を対象ごとに切り替える研究はあるか。**
→ **ほぼ無い（実質的な空白）。** 調べた範囲（V*/SEAL、ZoomEye、FOCUS、DeepEyes、Chain-of-Focus、DyFo、LookWise、Zoom-Refine、CARES、DC2）では、切り替え/拡大の判断信号がすべて「与えられた質問に答えるための確信度」に基づいており、質問文を前提とする。最も近いのは**CARES**（入力ごとに解像度を選択）だが、これも下流タスク性能で較正される。R2I（Zooming without Zooming）は「訓練時にズームを内在化し単一フォワードで細部を見る」が、これは切り替えを消す方向であり動的ゲートではない。**画像単独から「これは全体を見るべきか内側を見るべきか」を判定する純粋なゲートは発見できなかった。**

**Q3-2：疎な線画で、注意マップや勾配マップが意味のある領域を指すことを検証した研究はあるか。**
→ **検証した研究は無く、むしろ否定されている。** Bandyopadhyay et al.（CVPR2024, arXiv:2403.09480）は「ピクセル帰属は空白の白ピクセルが多い疎なスケッチでは意味のある説明を与えない」と原文で明言し、ストロークレベル帰属（SLA/P-SLA）に切り替えた。一般のsaliency忠実性ベンチ（Saliency-Bench等）はすべて自然画像（VOC・COCO・ImageNet）で、線画は対象外。**「疎な線画では標準的なGrad-CAM/勾配saliencyは信頼できない」ことが、暗黙にではなく明示的に示されている**点が本件に極めて重要。

**Q3-3：遮蔽で、視覚言語モデルがどの部分に依存しているかを調べた研究はあるか。**
→ **自然画像では成熟、線画では発見できず。** 遮蔽/パッチドロップによる帰属はCLIP ViTで確立（「Intriguing Properties of LLVMs」等がRandom/Salient PatchDropを適用）し、Captumの`Occlusion`など道具も揃う。しかし**線画・スケッチ・抽象画像に対してVLMの遮蔽帰属を適用した研究は発見できなかった。** これは本件で自前実装する価値のある空白。

### 4. 空白の特定（否定的情報も明示）

本件の要件＝〈疎な線画〉×〈質問文なし〉×〈対象ごとの粒度切り替え〉×〈似た意匠との識別〉の4条件同時充足。既存研究との差分：

- **質問文なしゲート**：既存の拡大ゲートは全て質問文依存（空白）。
- **線画でのsaliency信頼性**：疎な線画では標準saliencyは不適とCVPR2024が明示。線画向けはストロークレベル帰属のみで、これはSBIRネット用でありMLLM用ではない（空白）。
- **線画での遮蔽帰属**：VLM×線画の遮蔽研究は皆無（空白）。
- **粒度切り替えの自動判定**：全体（Bタイプ）か内側（Aタイプ）かを画像から判定する研究は無い。CARESは解像度選択だが線画未検証。
- **設計特許×MLLM×製品名**：Awale et al.（ECIR2025）が最も近いが、自然画像事前学習MLLMは特許線画でゼロショット性能が低いと報告。PatentLMM（arXiv:2501.15074）もGPT-4Vのゼロショットが弱い（brief BLEU平均18.68）と報告。
- **識別性学習の移植性**：NegCLIP系はSugarCrepeで「アーティファクト過学習」が指摘され、細粒度改善が誇張されている可能性。線画ハードネガでの検証は無い。

### 5. 転用候補（5件）

**候補1：ViCrop/FOCUS型の内部信号クロッピングを「質問文なし」に改造**
- 内容：製品名候補を仮の「質問」として各名前でのモデル注意/トークン類似度マップを生成→最も活性の高い領域を切り出して再エンコード→尤度再計算。
- データ：不要（訓練不要）。計算コスト：低（1〜数フォワード）。落とし穴：CVPR2024の警告どおり、疎な線画では注意マップ自体が信頼できない可能性が高い。まず遮蔽帰属（下記候補3）で注意マップの妥当性を検証してから使うべき。

**候補2：Density-Refine型の教師なし密度クラスタリングで局所領域を先取り**
- 内容：線画のインク画素の空間密度をDBSCAN系でクラスタリングし、密な部分領域（差込口・レンズ・LED等が集中する箇所）を検出→その領域を高解像度で再エンコードしAタイプを救う。
- データ：不要（教師なし）。学習：任意（特徴融合を学ぶなら要）。計算コスト：低〜中。落とし穴：Bタイプ（輪郭が手がかり）ではクラスタが全体に散り局所化が逆効果。密度分布の分散から「A/B」を判定するゲートに転用できる可能性（これ自体が新規性）。

**候補3：遮蔽帰属で「モデルがどこに依存しているか」を診断（まず着手すべき）**
- 内容：正面図をグリッドで系統的に遮蔽し、正解製品名の尤度低下を測る→依存領域マップを作成。Aタイプ（内側依存）とBタイプ（輪郭依存）を客観的に切り分けられる。
- データ：不要。計算コスト：中（グリッド数×フォワード）。落とし穴：白背景遮蔽はOOD入力を作りうる（遮蔽色の選択に注意）。ただし線画は背景が白なので白遮蔽の副作用は自然画像より小さいと期待。**線画×VLM遮蔽帰属は空白領域なので、この診断自体が論文化可能。**

**候補4：DIVA/un²CLIP型の生成フィードバックでCLIPエンコーダを線画向けに後追い学習**
- 内容：DeepPatent2の線画で拡散feedbackまたはunCLIP反転を用い、CLIP系エンコーダの細部把握を線画ドメインで強化→MMVP的な「線画blindペア」を減らす。
- データ：DeepPatent2（270万図・教師なしで可）。学習：要（視覚側のみ）。計算コスト：中〜高。落とし穴：拡散モデルが線画分布を学習していないと反転が不安定。線画専用の生成器が要るかもしれない。

**候補5：ハードネガ選好最適化（視覚的に酷似する別特許の製品名）**
- 内容：本件の8択構成（正解＋視覚的に似た7つ）をそのままハードネガとしてDPO/対照学習。最小視覚差の識別を明示的に目的化。
- データ：既存の8択セット＋類似特許ペア。学習：要（言語側の選好、または視覚側の対照）。計算コスト：中。落とし穴：SugarCrepeの教訓どおりアーティファクト過学習のリスク。ホールドアウトの意匠クラスで汎化を必ず確認。

### 6. 参考文献（主要）
- Tong et al. "Eyes Wide Shut? Exploring the Visual Shortcomings of Multimodal LLMs." CVPR 2024. arXiv:2401.06209.
- Wu & Xie. "V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs." CVPR 2024. arXiv:2312.14135. https://github.com/penghao-wu/vstar
- Shen et al. "ZoomEye: Enhancing Multimodal LLMs with Human-Like Zooming Capabilities through Tree-Based Image Exploration." EMNLP 2025 (Oral). arXiv:2411.16044. https://github.com/om-ai-lab/ZoomEye
- FOCUS. "Internal MLLM Representations for Efficient Fine-Grained Visual Question Answering." NeurIPS 2025. arXiv:2506.21710. https://focus-mllm-vqa.github.io/
- Shtedritski et al. "What does CLIP know about a red circle? Visual prompt engineering for VLMs." ICCV 2023. arXiv:2304.06712.
- Yuksekgonul et al. "When and why VLMs behave like bags-of-words? (NegCLIP/ARO)." ICLR 2023. arXiv:2210.01936.
- Hsieh et al. "SugarCrepe: Fixing Hackable Benchmarks for Vision-Language Compositionality." NeurIPS 2023. arXiv:2306.14610.
- Wang et al. "Diffusion Feedback Helps CLIP See Better (DIVA)." ICLR 2025. arXiv:2407.20171.
- Bandyopadhyay, Chowdhury, Bhunia, Sain, Xiang, Song. "What Sketch Explainability Really Means for Downstream Tasks." CVPR 2024. arXiv:2403.09480.
- Kucer, Oyen, Castorena, Wu. "DeepPatent: Large Scale Patent Drawing Recognition and Retrieval." WACV 2022.
- Ajayi et al. "DeepPatent2: A Large-Scale Benchmarking Corpus for Technical Drawing Understanding." Nature Scientific Data 10, 772 (2023).
- Higuchi & Yanai. "Patent image retrieval using transformer-based deep metric learning." World Patent Information 74 (2023) 102217.
- Lin, Hung, Lee. "Density-Refine: Patent Image Retrieval by Density-Based Region Extraction and Feature Fusion." ASME J. Mech. Des. 147(8):081703 (2025). DOI:10.1115/1.4067749.
- Awale, Müller-Budack, Ewerth. "Patent Figure Classification Using Large Vision-Language Models." ECIR 2025. arXiv:2501.12751.
- "PatentLMM: Large Multimodal Model for Generating Descriptions for Patent Figures." AAAI 2025関連. arXiv:2501.15074.
- Chen et al. "FastV: An Image is Worth 1/2 Tokens After Layer 2." ECCV 2024.
- Bai et al. "Qwen2-VL." arXiv:2409.12191.
- Chen et al. "ViCrop: Perceiving Small Visual Details in Zero-shot VQA." arXiv:2310.16033.
- Zheng et al. "DeepEyes: Incentivizing Thinking with Images via RL." arXiv:2505.14362.

## Recommendations（推奨・段階的）

**第1段階（今すぐ・訓練不要）：遮蔽帰属で診断（候補3）。** 現行Qwen3-VL-4Bで、正面図をグリッド遮蔽し正解名の尤度低下マップを作る。これでA/Bの切り分けが客観化でき、注意マップが線画で信頼できるか（CVPR2024の警告が本件でも成り立つか）を検証できる。**閾値：遮蔽マップが局所集中（Aと整合）か分散（Bと整合）かで、後段の粒度戦略を分岐。**

**第2段階（低コスト・訓練不要）：候補2の密度クラスタリング＋候補1のクロッピングを結合。** 遮蔽マップと密度マップが一致する領域を高解像度再エンコード。**判断基準：Aタイプで再エンコード後に尤度1位が正解になる率が第1段階比で+10pt超なら本命化。** ZoomEyeがInternVL2.5-8BでHR-Benchを+15〜17pt改善した実績は、この方向の上限の目安になる（ただし自然画像・質問文ありでの値である点に留意）。

**第3段階（要データ・要学習）：候補4（視覚エンコーダ後追い学習）または候補5（ハードネガ選好）。** 第2段階でも救えない「面の内側に隠れる決め手」が残るなら、エンコーダ表現不足（MMVP型）が原因なので視覚側を触る。**移行基準：第2段階の頭打ちが確認され、かつ誤答の主因が依然「図面→製品名の結合失敗」（尤度で正解が1位にならない）であること。**

**やるべきでないこと**：単純にトークン数/解像度だけを増やすこと。MMVP（9パターン中7つがスケール無効）とPosition論文（言語側更新は無効・視覚側更新のみ有効）が示すとおり、CLIP系エンコーダの盲点と圧縮での空間拡散は数のスケールで解けない。

## Caveats（留保）
- 2026年の一部arXivプレプリント（LookWise, HAVC, R2I, CropVLM, Density-Refineの数値詳細等）は査読前または本文非公開で、数値は要一次確認。特にDensity-RefineのDeepPatent上のmAP実数は有料誌本文（ASME JMD 147(8):081703）にあり本調査では未検証。DeepPatentの比較基準としては、PatentNet（ResNet50）でmAP 0.376、Wang & Zhang(2023)で0.712、Higuchi & Yanai(2023, SwinV2)で0.856が既報。
- Awale et al.（ECIR2025）の物体名ゼロショットTop-1精度の実数はTable 2にあるが本調査では未取得。特許図面でのMLLMゼロショット性能の定量は一次PDF参照が必要。
- 本件タスク（意匠特許の製品名当て・質問文なし・粒度切り替え）に完全一致する研究は存在せず、上記は近接研究からの転用提案である。「見つからなかった」こと自体が、この領域の新規性の余地を示す重要な情報。
- red circleのCUB数値（キーポイント命名46.5%）、ZoomEyeのHR-Bench改善幅、V*の探索コスト（A100で1標的あたり約6秒）、MMVPの人間95.7%/GPT-4V 38.7%等は原論文値であり、本件ドメイン（白背景・正面図1枚の設計特許線画）での再現は未検証。
- 「査読の有無」列は、会議採択（CVPR/ICCV/ECCV/NeurIPS/EMNLP/ICLR/WACV/ECIR）と専門誌（World Patent Information, ASME JMD, Nature Scientific Data）を査読済みとし、arXiv単独のものを査読前とした。ViCropは版により査読状況が異なる。