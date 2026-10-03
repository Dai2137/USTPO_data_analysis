# 画像キャプション生成における「どこを・どの粒度で見るか」の工夫の変遷 — 古典から現在まで

## TL;DR
- 「見る場所と粒度」の制御は、①格子への一様注意（Show, Attend and Tell, 2015）→②注意するか否かの切替（Knowing When to Look, 2017）→③物体領域単位の注意（Bottom-Up/Top-Down, 2018）→④近年の「拡大するかどうかを入力ごとに判断する」MLLM手法（ZoomEye/ViRGo/LookWise, 2024–2026）へと進化してきた。本件が抱える「対象ごとに必要な見方が違う」という問題設定に最も近いのは、この④の適応的ズーム系（特にViRGoとLookWise）である。
- ただし④の適応的手法はほぼ全て「自然画像・混雑シーン・小さな物体の読み取り（OCR・属性認識）」を主戦場としており、**テクスチャも色もない白背景線画（意匠特許図面）で製品名を当てる**という設定を扱った既存研究は確認できなかった。線画・特許図面側の研究（DeepPatent系）は検索・分類止まりで、「どこを拡大して見るか」を制御する発想と結合していない。ここに明確な新規性の余地が残る。
- 本件への転用候補として最有力なのは、(1) 信頼度ゲートで「拡大するか否か」を入力ごとに切り替えるLookWise型、(2) 学習した軽量ルータで見方を選ぶViRGo型、(3) 識別的キャプション/対比学習（Contrastive/Discriminability）を8択の「当て直せるか」評価と接続する系統、の3つ。いずれも線画向けの学習データ構築が最大の落とし穴になる。

## Key Findings

### 全体像
「どこを見るか」の扱いは大きく5世代に整理できる。各世代の課題と解決は年表（Details参照）にまとめた。重要なのは、**「全体を見る／一部を拡大して見る」を対象ごとに切り替える機構は、古典期には存在せず（注意の重みは連続的に変わるが、"拡大して見直す"という離散的行動はない）、2024年以降のMLLM系で初めて明示的に登場した**という点である。本件の診断（Aタイプ＝面の内側の微小手がかりは外す、Bタイプ＝全体輪郭で決まるものは当たる、視覚表現が図面1枚80トークンで外形が均される）は、まさにこの「適応的な拡大の欠如」と「トークン粒度の粗さ」に対応している。

### 最も近い既存研究
本件の「必要な見方が対象ごとに違う」に最も近いのは以下の3系統。
1. **適応的ズーム系MLLM（2024–2026）**：ZoomEye（EMNLP 2025）は画像を木構造とみなし、答えられる確信度が閾値を超えるまで再帰的にズームする。LookWiseは回答トークンの平均信頼度で「拡大するか否か」を、質問文由来のクロスアテンションで「どこを拡大するか」を決める。ViRGoは物体スケール（localization headsから推定）＋トークン信頼度＋画像解像度を特徴として軽量ルータ（XGBoost）が「global / attention-crop / patch-retrieval」を選ぶ。これらは「入力ごとに見る粒度を切り替える」という本件の核心をまさに主張している。
2. **識別的・対比的キャプション（2017–2023）**：Contrastive Learning for Image Captioning（Dai & Lin, 2017）やDiscriminability objective（Luo et al., 2018）は「似た画像と区別できる記述」を目標にし、評価に「生成文で対象画像を検索し直せるか（self-retrieval）」を使う。本件の8択（似た特許7つと区別）と評価思想が一致する。
3. **細粒度の視覚説明（2016–2018）**：Generating Visual Explanations（Hendricks et al., ECCV 2016）は鳥の種を区別する「class-discriminative」な記述を強化学習で生成する。「種を決める微小部位（赤い目・白いうなじ）に言及させる」という発想は、本件Aタイプ（差込口・レンズ・LED粒）に直結する。

### 何が残されているか（否定的情報）
- 適応的ズーム系は**制御信号が「質問文」または「回答の信頼度」に依存**する。本件は製品名を1つ生成するタスクで明示的な質問文がなく、Aタイプ（面内の微小手がかり）では「どこを拡大すべきか」を質問から導けない。ViRGo/LookWiseの「where」機構は本件では弱くなる可能性が高い。
- これらの手法は**自然画像・高解像度・混雑シーンが前提**で、白背景・単色線画での有効性は未検証。線画はCLIP系エンコーダが訓練分布外であり、attention/gradientマップの信頼性が担保されない。
- 特許図面研究（DeepPatent, WACV 2022 / DeepPatent2, Nature Sci. Data 2023）は**検索・分類・製図理解のデータセット整備**が主で、「見る粒度の適応制御」は扱っていない。線画×適応的ズーム×製品名同定の組合せは空白。

## Details

### 1. 系譜の年表（2014年頃〜現在）

**2014–2015｜エンコーダ・デコーダの原型（課題：画像→文の生成そのもの）**
- **Show and Tell (NIC)**（Vinyals et al., CVPR 2015, arXiv:1411.4555）。CNNで画像を1本のベクトルに圧縮しLSTMで文生成。**「どこを見るか」の概念はなく、画像全体を1ベクトルに均す**。被引用数は非常に多く、レビュー記事では5000件超と記載される（概数）。→ 本件の「80トークンで外形が均される」現状と本質的に同じ弱点。

**2015｜注意機構の導入（課題：全体1ベクトルでは細部が消える）**
- **Show, Attend and Tell**（Xu et al., ICML 2015, arXiv:1502.03044）。CNN下層の**格子状特徴（L個のD次元ベクトル）に空間注意**をかけ、単語ごとに注視位置を変える。soft注意（決定的・逆伝播可能）とhard注意（確率的サンプリング・REINFORCE/変分下界で学習）の2種。注意の単位は**格子（grid）**、決め方は**学習（デコーダ隠れ状態に条件付け）**、粒度の対象別切替は**なし（常に格子上で連続的に注視）**。レビュー記事では被引用7900件超と記載される（概数）。

**2016｜意味属性・単語検出器の経由（課題：低次特徴だけでは概念語が出ない）**
- **Image Captioning with Semantic Attention**（You et al., CVPR 2016）。外部の**属性/概念検出器**が出す語候補に注意。top-down（画像の要旨）とbottom-up（部分から語）を融合。注意の単位は**意味概念**、決め方は**外部検出器＋学習**。

**2016–2017｜注意を向けるか否かの切替（課題：機能語には視覚不要）**
- **Knowing When to Look / Adaptive Attention**（Lu et al., CVPR 2017, arXiv:1612.01887）。**visual sentinel**（デコーダが既に知っていることの潜在表現）を導入し、sentinel gate β_t（0〜1）で「画像を見る」か「言語モデルに頼る」かを単語ごとに切替。原論文は "the" や "of" のような非視覚語、あるいは "behind a red stop" の後の "sign" のように言語モデルだけで信頼的に予測できる語には視覚が不要だと指摘する。**「視覚に頼るか言語に頼るか」を明示的にゲートした最初期の研究**。注意の単位は格子＋sentinel、決め方は学習、粒度切替は「見る/見ない」の2値。→ 本件の「Bタイプは言語先行でも当たる／Aタイプは視覚を強く見る必要」に概念的に対応。

**2017｜チャネル＋空間の両注意（課題：空間注意だけでは"何を"が弱い）**
- **SCA-CNN**（Chen et al., CVPR 2017, arXiv:1611.05594）。CNN特徴が本来「空間的・チャネル的・多層的」であることに着目し、**空間注意（where）とチャネル注意（what）を多層で同時適用**。注意の単位は空間格子＋チャネル、決め方は学習。Flickr8k/30k/MSCOCOで既存の空間注意モデルを上回ると報告。

**2017｜学習目標側の工夫（課題：交差エントロピーと評価指標の乖離・露出バイアス）**
- **Self-Critical Sequence Training (SCST)**（Rennie et al., CVPR 2017, arXiv:1612.00563）。REINFORCEの派生で、**テスト時の貪欲デコード出力自身をベースライン**にしてCIDErなど非微分指標を直接最適化。注意の単位そのものではなく、**「どんな記述を良しとするか」を報酬で制御できる枠組み**を提供。→ 本件で「製品名を当て直せたら報酬」という設計に直結。

**2018｜物体領域を単位にする（課題：格子は物体境界と無関係）**
- **Bottom-Up and Top-Down Attention (Up-Down)**（Anderson et al., CVPR 2018, arXiv:1707.07998）。**Faster R-CNN（Visual Genomeで事前学習）が提案する物体領域**を注意の単位にし、top-down機構が領域重みを決定。原論文abstract逐語では "our results on the MSCOCO test server establish a new state-of-the-art... achieving CIDEr / SPICE / BLEU-4 scores of 117.9, 21.5 and 36.9"、さらに "first place in the 2017 VQA Challenge, achieving 70.3% overall accuracy on the VQA v2.0 test-standard server"。注意の単位は**領域（region）**、決め方は**外部検出器＋学習**、粒度切替は領域集合内での重み付け。
- **Neural Baby Talk**（Lu et al., CVPR 2018, arXiv:1803.09845）。文の**テンプレート（スロット）を生成→物体検出器が同定した視覚概念でスロットを充填**。古典的スロット充填と神経キャプションの折衷で、記述を画像内エンティティに明示的にグラウンディング。COCO/Flickr30kでSOTA。注意の単位は**検出領域**、粒度切替はスロット単位。

**2016–2020｜識別的・対比的キャプション＋参照表現（課題：generic captionは対象を特定できない）**
- **Generating Visual Explanations**（Hendricks et al., ECCV 2016, arXiv:1603.08507）。CUB鳥類でclass-discriminative＋image-relevantな説明を、サンプリングと強化学習に基づくloss（class specificityを大域的文特性として報酬化）で生成。既存キャプション手法より識別的な説明を生成できると報告。
- **Contrastive Learning for Image Captioning**（Dai & Lin, NeurIPS 2017, arXiv:1710.02534）。正しい画像-文ペアに高確率、ランダム負例ペアに低確率を与える2つの制約で**distinctiveness**を促進しつつ全体品質を維持。
- **Discriminability objective for training descriptive captions**（Luo et al., CVPR 2018, arXiv:1803.04376）。生成文から対象画像を**検索し直せるか（self-retrieval）**を目的に加える。話者・聞き手（speaker-listener, Andreas & Klein 2016：話者が生成→聞き手が正画像を選好→テスト時に聞き手が再ランキング）や文脈抑制（Vedantam et al. 2017：target/distractorで共通の要素を抑制）も同系統。ただしこの2者は生成時にdistractorの提示が必要な点で異なる。
- **参照表現生成（RSA/語用論）**：Rational Speech Act（Frank & Goodman 2012）を基に、literal listener→pragmatic speaker→pragmatic listenerの再帰で「聞き手が一意に同定できる表現」を選ぶ（Monroe & Potts 2015, arXiv:1510.06807; RefCOCO/RefCOCO+, arXiv:2205.07795）。評価は**一致度指標＋聞き手による同定成功率**の両輪。→ 本件の8択正解率はまさに「pragmatic listenerの同定成功率」に相当。
- 評価の潮流：BLEU/CIDEr/SPICEのような一致度指標に加え、**self-retrieval（生成文で画像を当て直す）**やDisWordRate等のdistinctiveness指標が用いられる（Compare and Reweight, ECCV 2020, arXiv:2007.06877; Ref-DIC, arXiv:2306.14259）。

**2017–2021｜細粒度認識の部位注目（課題：部位教師なしで識別部位を見つける）**
- **RA-CNN**（Fu et al., CVPR 2017 Oral）。**Attention Proposal Network (APN)** が全体画像から粗→細へ注視領域を再帰生成し、注視領域を拡大して次段に入力。**bounding box/部位アノテーション不要**、段内分類損失＋段間ランキング損失で学習し端から端まで最適化可能。CUB Birds/Stanford Dogs/Stanford Carsでそれぞれ相対精度3.3%/3.7%/3.8%向上。→ 「面の内側の微小部位を教師なしで拡大していく」本件Aタイプに最も近い古典的発想。
- 関連：MA-CNN（複数注意で意味的に近いチャネルを部位に分離, ICCV 2017）、NTS-Net（Learning to Navigate, ECCV 2018）、Focus Longer to See Better（再帰的注意, arXiv:2005.10979）。いずれも部位位置を**教師なし**で決める。

**2023–2026｜MLLMでの「見る場所」制御（課題：ViT固定解像度で細部が潰れる／視覚トークンが均される）**
- **高解像度タイル分割・可変解像度**：LLaVA-NeXTのAnyRes（native解像度をタイル分割、最大672×672/336×1344/1344×336の3アスペクト比）、InternVLの動的タイリング（448×448タイルを1〜数十枚、最大4K）、Qwen2-VL/Qwen2.5-VLの2D-RoPEによる任意解像度、LLaVA-UHD（最大672×1008, arXiv:2403.11703）。**細部保持には効くが、どのタイルが重要かの選択は別問題**。
- **視覚トークンの選択・圧縮**：FastV（LLMの浅層attentionで低注意の視覚トークンを2層目以降で剪定、約50%削減で性能維持, ECCV 2024）、SparseVLM（テキスト誘導・訓練不要）、VisionSelector（微分可能Top-Kで学習的に重要トークンを選択, arXiv:2510.16598）。→ 本件の「80トークンで均される」問題の直接の対処領域だが、圧縮は"減らす"方向で"拡大して見直す"方向ではない。
- **画像内を探索してから答える（visual search）**：V*/SEAL（Wu & Xie, CVPR 2024, arXiv:2312.14135）。LLMの世界知識でどこを探すか誘導し、高解像度画像から対象を探索。公式記述では "we build a benchmark V*Bench based on 191 high-resolution images from SAM with an average image resolution of 2246 × 1582"（属性認識115・空間関係推論76サンプル）。SEALはV*Benchで視覚グラウンディング精度 "75.39% in visual grounding accuracy"。
- **段階的注視・ズーム推論**：Chain-of-Spot（質問からROIを生成→切り出して再質問, arXiv:2403.12966）、Chain-of-Focus（SFT＋RLで適応的にズーム, arXiv:2505.15436）、Visual Sketchpad（描画を挟む視覚的CoT）、Zoom-Refine（高解像度cropで自己修正, 訓練不要）。
- **適応的に「拡大するか否か」を判断する系統（本件に最も近い）**：
  - **ZoomEye**（Shen et al., EMNLP 2025, arXiv:2411.16044）。画像を木構造（根＝全体、子＝ズームした部分）とみなし、**回答確信度が閾値（約0.6）を超えるまで再帰的にズーム**する訓練不要・モデル非依存の木探索。abstract逐語 "LLaVA-v1.5-7B increases by 34.57% on V* Bench and 17.88% on HR-Bench"。Qwen2.5VL-3B＋ZoomEyeはHR-Bench 8Kで68.38%を達成し、GPT-4oの55.5%を上回る。
  - **MLLMs Know Where to Look (ViCrop)**（Zhang et al., ICLR 2025, arXiv:2502.17422）。**モデル自身のattention/gradientマップ**でcrop位置を決める訓練不要手法。「モデルは誤答時でも"どこを見るべきか"は分かっている」＝失敗は"見る"のではなく"細部を解像する"側にある、と主張。ただし「常にcrop」で、global-vs-zoomのゲートは持たない。LLaVA-1.5/InstructBLIP＋7つのVQAベンチ（TextVQA, DocVQA, GQA, AOKVQA, POPE, V*, VQAv2）で検証。attention対象層はTextVQA検証データで選択。
  - **LookWise**（Shen et al., arXiv:2603.00171, 2026）。**回答トークンの平均softmax信頼度Cで「いつ拡大するか」を、質問文由来ターゲット語のクロスアテンションで「どこを拡大するか」を決める**訓練不要2段階法。逐語 "the performance peaks at 73.10% when λ=1.5, which derives an optimal threshold of τ=0.734"（AOKVQA、ベースライン71.44%・全crop 71.96%を上回る）、開放領域では固定τ=0.96が頑健。LLaVA-1.5-7BでV*Bench 62.80（+14.12）、Qwen2.5-VL-3BでV*Bench 86.38（+10.48）・HR-Bench 8K 70.00（+11.12, SOTA）。HR-Bench 8KでZoomEye比約4.0倍高速。逐語 "On AOKVQA, we are able to skip redundant cropping for 67.60% of the samples, effectively halving the inference time without compromising accuracy"（全crop比で精度+1.14）。
  - **ViRGo（Look Before You Zoom）**（Tran et al., arXiv:2606.21968, 2026）。初回globalパスから**①localization headsが出す物体スケール、②最上位トークン確率、③画像解像度**の3特徴を抽出し、**軽量XGBoostルータ（max_depth=2）が {global / attention-crop(ViCrop) / patch-retrieval(RAP)} を選択**。LLaVA-v1.5-7Bで加重平均63.2%（baseline 54.6, +8.6）、推論時間を約50%削減（RAP比89,185秒→44,626秒）。Oracleルータ72.4%との差が残ると自認。
  - 関連（探索の網羅）：CropVLM（RLで訓練しズーム, CVPRW 2026）、Region-to-Image Distillation（ズームを訓練時primitiveに内部化, arXiv:2602.11858）。

### 5. 線画・技術図面・意匠/特許画像の扱い
- **DeepPatent**（Kucer et al., WACV 2022）：45,000件の意匠特許・350,000枚超の図面から成る画像検索ベンチマーク。ResNetベースのPatentNetでMAP 0.376。特許図面は「白黒の抽象線画で、モダリティが自然画像と大きく異なり、従来手法の単純適用では望む性能が出ない」と明言される。後にWang & Zhang（2023, EfficientNet-B0）がMAP 0.712まで改善。
- **DeepPatent2**（Oyen et al., Nature Scientific Data 2023）：13万以上の物体名・複数視点・分割図を含む、技術図面理解のための大規模コーパス。ただしタスクは製図理解・検索が中心。
- 画像単独での特許分類は難度が高く、Jiang et al.（2021）はCNNで8クラス分類54.32%と、テキストベースに劣ると報告。**線画×製品名同定×適応粒度制御を扱った研究は見当たらない**。
- 隣接領域：sketch-based image retrieval（SBIR）、ImageNet-Sketch、QuickDraw、Diagram Image Retrieval（sketch-based転移学習, arXiv:2004.10780）。いずれも線画の検索・分類で、「どこを拡大して見るか」の制御とは結合していない。

### 2. 論文一覧の表

| 論文名 | 年・会議 | 注意の単位 | 粒度の決め方 | 対象ごとに粒度を変えられるか | 有効性の根拠実験 | 本件への適用可能性 |
|---|---|---|---|---|---|---|
| Show and Tell (NIC) | CVPR 2015 | 画像全体1ベクトル | なし | ✗（常に全体を均す） | COCO/Flickr, BLEU | 低（現状の素朴手法と同型＝現状の問題そのもの） |
| Show, Attend and Tell | ICML 2015 | 格子（L個のD次元） | 学習（デコーダ条件付け） | △（連続的に注視位置は動くが"拡大"はない） | Flickr8k/30k/COCO, SOTA | 中（注意可視化で診断に使える） |
| Image Captioning w/ Semantic Attention | CVPR 2016 | 意味概念/属性 | 外部検出器＋学習 | △ | COCO/Flickr30k | 中（製品部位の属性語検出に転用余地） |
| Knowing When to Look | CVPR 2017 | 格子＋visual sentinel | 学習（sentinel gate） | △（見る/見ないの2値） | COCO/Flickr30k, SOTA | 中（A/Bタイプの視覚依存度切替の思想） |
| SCA-CNN | CVPR 2017 | 空間格子＋チャネル | 学習 | △ | Flickr8k/30k/COCO | 中（"何を"見るかのチャネル注意） |
| Self-Critical Sequence Training | CVPR 2017 | （学習目標） | 報酬設計 | ―（目標側） | COCO test server SOTA | 高（"当て直せたら報酬"に直結） |
| Bottom-Up and Top-Down (Up-Down) | CVPR 2018 | 物体領域 | 外部検出器＋学習 | △（領域集合内で重み付け） | COCO CIDEr 117.9 / VQA 70.3% | 中（線画に検出器を効かせるのが課題） |
| Neural Baby Talk | CVPR 2018 | 検出領域（スロット） | 外部検出器＋学習 | △ | COCO/Flickr30k SOTA | 中（グラウンディング志向） |
| Generating Visual Explanations | ECCV 2016 | 画像全体＋class報酬 | RL（class specificity） | ―（記述内容の識別性） | CUB鳥類, 人手評価 | 高（種＝製品名を区別する記述） |
| Contrastive Learning for Captioning | NeurIPS 2017 | ― | 対比損失 | ―（識別性） | COCO, distinctiveness | 高（8択の区別と一致） |
| Discriminability objective | CVPR 2018 | ― | self-retrieval目的 | ―（識別性） | COCO, retrieval recall | 高（当て直し評価と一致） |
| RA-CNN | CVPR 2017 | 再帰的注視領域 | 学習（APN, 教師なし） | ✓（粗→細へ再帰的拡大） | CUB/Dogs/Cars +3.3/3.7/3.8% | 高（面内微小部位を教師なし拡大） |
| V*/SEAL | CVPR 2024 | 探索した部分領域 | LLM誘導探索 | ✓（探索して拡大） | V*Bench 75.39% | 中〜高（質問依存が課題） |
| FastV / VisionSelector | ECCV2024 / 2025 | 視覚トークン | 注意/学習で選択 | △（減らす方向） | COCO/VQA各種 | 中（80トークン問題の緩和） |
| ZoomEye | EMNLP 2025 | 木構造の部分画像 | 確信度で再帰ズーム | ✓（答えられるまで拡大） | V*Bench +34.57% | 高（質問不要の確信度駆動） |
| MLLMs Know Where to Look (ViCrop) | ICLR 2025 | attention/gradient由来crop | モデル内部信号 | △（常にcrop） | 7 VQAベンチ | 高（線画でattentionが効くか要検証） |
| LookWise | arXiv 2026 | 信頼度ゲート＋質問crop | 信頼度＋質問文 | ✓（拡大する/しない切替） | V*Bench +14.12 等 | 高（信頼度ゲートは質問なしにも応用可） |
| ViRGo | arXiv 2026 | ルータが3択 | 学習ルータ（スケール＋信頼度） | ✓（global/crop/retrieval選択） | 加重平均+8.6, 時間-50% | 高（"見方を選ぶ"の最直系） |
| DeepPatent / DeepPatent2 | WACV 2022 / Nature SD 2023 | （検索・分類） | ― | ― | MAP 0.376→0.712 | 高（線画データ源・前処理の参照） |

### 3. 問題設定が最も近い既存研究と、その主張範囲・残された点

**最も近いのはViRGo（arXiv:2606.21968）とLookWise（arXiv:2603.00171）**。両者は「入力ごとに、全体を見るか一部を拡大して見るかを切り替える」という本件の核心をそのまま主張している。
- **ViRGoの主張範囲**：物体スケール（localization headsから）＋トークン信頼度＋解像度で「見方」を3択（global/attention-crop/patch-retrieval）から選ぶ。**切替判断は学習した軽量ルータ**。→ 本件の「Aは拡大、Bは全体」を自動判定する枠組みに直接対応。
- **残された点（ViRGo）**：①制御信号が自然画像の物体スケール前提で、線画の"面内スリット"のような微小手がかりのスケール推定は未検証。②Oracleルータ72.4%に対し実測63.2%で**切替判断自体がまだ不完全**。③質問がある前提（VQA）で、製品名を無条件生成する本件とは入力形態が異なる。
- **LookWiseの主張範囲**：回答トークンの平均信頼度で「拡大するか否か」を、質問文で「どこを拡大するか」を決める。**"いつ"と"どこ"を分離**した点が本件に有用。
- **残された点（LookWise）**：①"どこ"はクロスアテンションの質問語依存で、**質問文がない製品名生成では"どこ"が導けない**。②閾値τ（AOKVQAでτ=0.734、開放領域でτ=0.96）は各ベンチにフィットさせた値で、線画での較正が別途必要。③CLIP系attentionが線画で信頼できるかは未検証。

**古典側で最も近いのはRA-CNN（CVPR 2017）**。**部位アノテーション不要で粗→細へ再帰的に拡大**する点が、本件Aタイプ（面内の微小手がかり）にそのまま対応する。ただしRA-CNNは分類タスクで、記述生成・製品名同定には接続していない。

**明確な空白（新規性の所在）**：
1. **線画×適応的ズーム**：適応ズーム系は全て自然画像・高解像度・混雑シーン前提。白背景・単色線画での「拡大するか否か」判断は誰も検証していない。
2. **質問なしの"どこ"決定**：既存の"where"機構は質問文かモデルattentionに依存。製品名を無条件生成する設定で「Aタイプは面内、Bタイプは輪郭」を自動判別する機構は未確立。
3. **識別性目的×適応粒度の結合**：Contrastive/Discriminability系（識別性目的）と適応ズーム系（粒度制御）は別々に発展しており、**「似た特許7つと区別するために、対象ごとに最適な粒度で見る」統合は空白**。ここが本件の新規性の中核になり得る。

### 4. 本件に転用できる候補（3〜5件）

**候補1：信頼度ゲート型の適応ズーム（LookWise/ZoomEye型）**
- 内容：Qwen3-VL-4Bにまず全体（低粒度80トークン）で製品名を出させ、**回答の信頼度（尤度）が閾値未満なら図面の一部を拡大して再入力**する。ZoomEye型なら確信度が閾値を超えるまで木探索的にズーム。
- 必要データ：閾値較正用に、正解付き図面の検証セット（数百枚）。**学習は不要（訓練フリー運用可）**。
- 落とし穴：①"どこを拡大するか"を質問文から導けない（製品名生成には質問がない）。→ Aタイプでは「面の内側」を一般に優先探索するヒューリスティクスか、モデルattention（ViCrop流）で代替する必要。②線画でCLIP系attentionが信頼できるか要事前検証。③診断で「誤答の8割が図面→製品名の結合失敗」＝拡大しても言語側で正しい製品名に結べない可能性。拡大は"見る"問題を解くが"結ぶ"問題は別。

**候補2：学習ルータで見方を選ぶ（ViRGo型）**
- 内容：図面をA（面内微小手がかり）/B（輪郭で決まる）に自動分類する軽量ルータを学習し、Aには拡大crop、Bには全体を割り当てる。本件の診断（A/Bの二分＋Aの中の外形/面内の細分）はルータの教師ラベル設計にそのまま使える。
- 必要データ：**A/Bラベル付き図面（数百〜千枚）**。ルータ自体はXGBoost等で小規模学習可能。
- 落とし穴：①A/Bの境界が曖昧な図面（Aだが外形にも手がかり）で誤ルーティング。②localization headsによるスケール推定が線画で機能するか未知。③ルータの上限（ViRGoのOracleとの差が示すように）が残る＝完全自動判定は困難。

**候補3：識別性目的での微調整（Contrastive / Discriminability / self-retrieval）**
- 内容：8択（似た特許7つと区別）を「生成した製品名で正しい図面を当て直せるか（self-retrieval）」の対比損失／SCST報酬に変換し、Qwen3-VL-4Bを微調整。「似た特許と区別する語」を出すよう学習目標側で誘導。
- 必要データ：**似た特許のグループ（distractor集合）付き図面-製品名ペア**。既に8択ベンチがあるので流用可。
- 落とし穴：①distinctivenessを上げすぎると流暢さ・正確さが落ちるトレードオフ（先行研究で既知）。②線画でのCLIP/検索エンコーダの品質。③微調整データ量。

**候補4：教師なし部位拡大（RA-CNN型）＋記述生成**
- 内容：APN的な再帰ズームで面内の識別部位を教師なしに特定し、その拡大パッチをMLLMに追加入力。Aタイプの「差込口スリット・レンズ・LED粒・皿のくぼみ」を狙い撃つ。
- 必要データ：部位アノテーション不要（RA-CNNの利点）。ただしランキング損失学習用のペアが要る。
- 落とし穴：①RA-CNNは分類用で、MLLMのトークン入力への接続を自作する必要。②線画は情報密度が低くAPNの注視が不安定になりうる。

**候補5：視覚トークン粒度の増強（AnyResタイル＋トークン選択）**
- 内容：図面1枚80トークンの粗さを、タイル分割（AnyRes/動的解像度）で局所解像度を上げつつ、VisionSelector/FastV流で重要トークンだけ残す。
- 必要データ：なし（推論時工夫）〜トークン選択器の軽微な学習。
- 落とし穴：①"減らす"方向の圧縮は面内微小手がかりを落とすリスク。②タイル境界の空間整合性劣化。③根本の"結合失敗"は解かない。

**推奨順序**：まず**候補1（訓練フリーの信頼度ゲート＋ViCrop流attention crop）を線画で成立するか小規模検証**（線画でattentionが機能するかの一次判定を兼ねる）。並行して**候補3（self-retrieval/対比目的の微調整）**で「結合失敗」の本丸に対処。両者が有望なら**候補2（A/Bルータ）**で統合。

### 参考文献（arXiv・実装）

- Show and Tell: arXiv:1411.4555 / 実装 github.com/nikhilmaram/Show_and_Tell
- Show, Attend and Tell: arXiv:1502.03044
- Image Captioning with Semantic Attention: CVPR 2016 openaccess (You et al.)
- Knowing When to Look: arXiv:1612.01887 / 実装 github.com/jiasenlu/AdaptiveAttention
- SCA-CNN: arXiv:1611.05594 / 実装 github.com/zjuchenlong/sca-cnn.cvpr17
- Self-Critical Sequence Training: arXiv:1612.00563
- Bottom-Up and Top-Down Attention: arXiv:1707.07998 / 実装 github.com/peteanderson80/bottom-up-attention
- Neural Baby Talk: arXiv:1803.09845 / 実装 github.com/jiasenlu/NeuralBabyTalk
- Generating Visual Explanations: arXiv:1603.08507
- Contrastive Learning for Image Captioning: arXiv:1710.02534
- Discriminability objective for descriptive captions: arXiv:1803.04376
- Compare and Reweight (distinctive): arXiv:2007.06877 / Ref-DIC: arXiv:2306.14259
- RSA referring expressions: arXiv:2205.07795 / Monroe & Potts arXiv:1510.06807
- RA-CNN: CVPR 2017 / 実装 github.com/Jianlong-Fu/Recurrent-Attention-CNN
- V*/SEAL: arXiv:2312.14135 / 実装 github.com/penghao-wu/vstar
- FastV: ECCV 2024 / VisionSelector: arXiv:2510.16598
- LLaVA-UHD: arXiv:2403.11703 / LLaVA-NeXT AnyRes
- Chain-of-Spot: arXiv:2403.12966 / Chain-of-Focus: arXiv:2505.15436
- ZoomEye: arXiv:2411.16044 / 実装 github.com/om-ai-lab/ZoomEye
- MLLMs Know Where to Look (ViCrop): arXiv:2502.17422 / 実装 github.com/saccharomycetes/mllms_know
- LookWise: arXiv:2603.00171 / 実装 github.com/Xiaoxiang100/LookWise
- ViRGo (Look Before You Zoom): arXiv:2606.21968
- CropVLM: CVPRW 2026 / Region-to-Image Distillation: arXiv:2602.11858
- DeepPatent: WACV 2022 / DeepPatent2: Nature Scientific Data 2023 / Diagram Image Retrieval: arXiv:2004.10780

## Recommendations

1. **第一段階（学習なし、まず着手）**：候補1を線画で検証。Qwen3-VL-4Bのattention/gradientマップ（ViCrop流）が白背景線画で意味ある領域を指すかをまず目視＋定量で確認。同時に「回答尤度（信頼度）」がAタイプで低くBタイプで高い、という診断と整合するかを測る。**信頼度がA/Bを分離できれば、信頼度ゲートによる適応ズームが成立する強い証拠**（LookWiseがτ=0.734〜0.96で信頼度ゲートを成立させた前例あり）。
2. **第二段階（並行）**：候補3を試す。既存8択のdistractorを使い、self-retrieval／対比損失またはSCST（"正しい製品名に当て直せたら報酬"）でQwen3-VL-4Bを微調整。診断の「誤答8割が図面→製品名の結合失敗」に直接効くのはこちら。拡大（候補1）は"見る"問題、微調整（候補3）は"結ぶ"問題に対応し、両輪で当たるべき。
3. **第三段階（第一・第二が有望なら）**：候補2のA/Bルータで統合。本件診断のA/B二分＋Aの外形/面内細分をラベル設計に流用。
4. **判断を変える閾値（ベンチマーク）**：①候補1でAタイプ正解率がBタイプ（現状で相対的に高い）に近づくか。②self-retrieval recall@1が現状の8択42%を有意に上回るか。③線画でattentionが無意味（一様/背景に張り付く）なら候補1を捨て、候補4（RA-CNN型の教師なし部位拡大）か候補5に切替。
5. **新規性の主張先**：論文化するなら「線画×質問なし×適応粒度×識別性目的の結合」を前面に。既存の適応ズーム（ViRGo/LookWise/ZoomEye）は自然画像・質問前提であり、この4条件の同時充足は空白である点を明示。

## Caveats
- **推測と事実の区別**：本報告の年表・手法説明・数値（CIDEr 117.9, V*Bench 75.39%, ZoomEye V*Bench +34.57%, LookWise τ=0.734等）は各原論文/公式実装/enricher検証済みの逐語引用に基づく事実。一方、「本件への適用可能性」「新規性の所在」「A/Bと各手法の対応づけ」は筆者の分析・推論であり、線画での実証は行われていない。
- **2026年preprintの扱い**：ViRGo（arXiv:2606.21968）とLookWise（arXiv:2603.00171）は査読前arXivで、数値は著者申告値。ViRGoは自らOracle（72.4%）との差を、LookWiseは閾値のベンチフィットを限界として認めている。査読済み（ZoomEye=EMNLP 2025, ViCrop=ICLR 2025, V*=CVPR 2024, Up-Down=CVPR 2018）と区別して扱うこと。
- **被引用数**：Show and Tell「5000件超」、Show, Attend and Tell「7900件超」はレビュー記事記載の概数であり、時点により変動する。正確な値はGoogle Scholar等で都度確認を推奨。
- **線画での未検証性**：本報告が挙げた全ての適応ズーム・トークン選択手法は自然画像で評価されており、白背景単色線画（意匠図面）での有効性は原論文では一切検証されていない。特許図面は「白黒の抽象線画でモダリティが自然画像と大きく異なり従来手法の単純適用では性能が出ない」とDeepPatent著者が明言しており、CLIP系エンコーダの訓練分布外である点は繰り返し留意が必要。
- **探索範囲の限界**：DeepPatent2の製図理解タスクの詳細、"MLLMs know where to look"の各ベンチ別の正確な数値、ViRGo/LookWiseの査読状況は、検索budget制約により一次ソースで完全確認できていない部分がある（サブエージェント経由の確認に依拠した箇所を含む）。