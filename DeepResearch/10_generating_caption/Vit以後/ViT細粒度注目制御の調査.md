# **意匠特許線画識別におけるViT・MLLMの粒度制御および局所注視機構に関する包括的調査報告書**

## **1\. ViT以後（2020年〜現在）における技術的系譜**

2020年のVision Transformer（ViT）の登場以降、視覚と言語の統合表現処理は、従来の畳み込み神経回路網（CNN）と再帰型神経回路網（LSTM）の組み合わせから、ViTを基盤とする視覚エンコーダと大規模言語モデル（LLM）の統合体である視覚言語モデル（MLLM）へと完全に移行した。この技術的転換期において、「画像のどの領域をどのような解像度・粒度で抽出して言語空間へ投影すべきか」という問題は、画像理解の精度と計算効率を決定づける核心的な課題として定立されてきた。本節では、2020年以降に展開された主要な研究動向を、「視覚トークンの粒度と情報損失」「注目領域の制御機構」「拡大・再観察の切り替えゲート機構」「識別性を目的とした学習手法」「線画・技術図面への適応性」の5つの視点から整理・試論する。

### **1.1 視覚トークンの粒度と情報の損失（ViT特有の問題）**

ViT基盤モデルにおける視覚エンコーディングは、入力画像を固定あるいは動的なパッチ（例：![][image1] や ![][image2] ピクセル）に分割し、線形投影を経てトークン化するプロセスを辿る。初期の固定解像度モデル（224×224や336×336ピクセル）では、入力段階でのダウンサンプリングにより高周波な幾何的細部（線画の微小な不連続性、スリット、極小の穴等）が不可逆的に平滑化される問題が生じていた1。この制限を克服するため、近年ではアスペクト比を維持しながら画像を複数タイルに分割する動的タイリング（Dynamic Tiling / AnyRes）や、可変長トークン表現を可能にするネイティブ解像度（Native Resolution）エンコーディングが主流となっている1。  
しかし、LLM側のコンテキスト長膨張と計算コストを抑える目的で挿入される「視覚トークン圧縮・結合メカニズム」が、新たな情報損失を引き起こす原因となっている1。Q-Formerによる固定長クエリ変換、コネクタにおける隣接 ![][image3] パッチの平均・線形結合、あるいはトークンプーリングやマージ技術は、トークン数を削減する一方で、パッチ内部の微細な空間配置情報を消失させる1。  
特に、FIRM（CVPR 2026）による空間分析では、コネクタ段階で複数パッチの特徴量を単一の視覚トークンベクトルへ集約・圧縮する際、トークン内部のサブセルレベル（Sub-cell Level）に存在するバイナリ構造や細部幾何形状が完全に平滑化される問題（Intra-token Spatial Structural Loss）が定量的に証明されている3。白背景の線画のように情報が極めて稀釈で疎（Sparse）な画像においては、数ピクセル幅の差込口スリットや皿の僅かな凹凸線が周囲の広大な余白（白背景）パッチと平均化されることで、ベクトル特徴空間上で希釈され完全に掻き消される現象が発生する3。  
ここで重要な学術的問いが生じる。「視覚トークン数（解像度）を単に増やせば極小の細部は救えるのか、それとも他の構造要因がボトルネックとなっているのか」という点である。分析の結果、トークン数の増加は必要条件であっても十分条件ではないことが判明している。

* **トークン数増加の直接的効果**: 原理的にパッチサイズを小さくしトークン数を増やすことで、極小構造が単一パッチ内に独立して収まる確率が高まり、幾何情報の空間的分解能は物理的に向上する1。  
* **トークン数増加を相殺する3つの阻害要因**:  
  * **事前学習表現の抽象化バイアス**: CLIP等に代表される大規模視覚エンコーダの対照学習目標は、画像全体の大域的な概念・クラス・輪郭特徴を優先的に獲得するようバイアスがかかっている7。このため、入力トークン数を1000個以上に引き上げても、エンコーダが出力する個々のトークンベクトル自体が極小の幾何変化に感度を持たない場合がある7。  
  * **無情報余白へのアテンション拡散（Visual Clutter）**: HueManity（2025）等の知見によれば、高解像度化に伴って無情報な白背景領域のトークンが大量に生成されると、LLMの自己注意機構（Self-Attention）において注意の重みが広大な余白へ飛散・拡散し、結果として内側の微細な特定トークンを誤って無視・抑圧する現象が発生する9。  
  * **コネクタでの構造的破壊**: 入力解像度を高めても、LLMに与える直前のコネクタ部でトークン結合やマージが適用されれば、結局のところトークン内空間構造の崩壊を免れ得ない3。

### **1.2 どこを見るかを制御する機構（ViT / MLLM期）**

入力画像内の特定領域（面の内側の微小構造等）へモデルの着目を誘導する制御機構は、制御信号の生成メカニズムに基づき、主に「自己アテンション・勾配誘導型」「探索・ズーム方策型」「明示的視覚プロンプト型」の3系統に分かれる。

#### **自己アテンション・勾配誘導抽出（Attention / Gradient-based Cropping）**

モデル内部のSelf-Attentionマップや、生成されたLogitに対する勾配度合いを解析し、注目度の高い座標領域（RoI）を算出して切り出すアプローチである2。

* **制御信号**: 1パス目のフォワード処理で得られるアテンション分布、あるいは出力からのバックプロパゲーション勾配。  
* **メカニズム**: Vision-RL2（ICLR 2026）におけるSelf-Distilled Region Proposal Network（SD-RPN）は、MLLMの内部アテンション応答からノイズを除去したグラウンディング信号を自己蒸留し、外部質問や別のアノテーションを必要とせずに高い注目領域を座標ボックスとして提案する2。

#### **探索・ズーム方策（Search and Zoom Policy / Reinforcement Learning）**

画像を大まかに観察した後、どの領域を追加で拡大観察すべきかを階層的・逐次的に決定する動的探索手法である10。

* **制御信号**: 分類確信度スコア、価値関数の予測値、または強化学習（RL）を通じて最適化された方策ネットワークの出力11。  
* **メカニズム**: Q-Guide（2026）は、LLMエージェントが「現在の視野では細部情報が不足している」と自己判断した際に、専用のクロップツール（Zoom Tool）を能動的に呼び出して局所領域を高解像度で再取得する10。また、GFNet（Glance and Focus）やAdaFocusシリーズでは、大域画像（Glance）から得られた特徴量に基づき、情報利得を最大化する局所位置をRL方策により導出し、そこを選択的に高解像度処理する11。

#### **明示的視覚プロンプト・領域トークン（Visual Prompting / Region Tokens）**

画像に直接マーク（赤枠、サークル、マスク）を描画するか、座標トークン（例：\<box\>）を入力列に与えることで、注視領域を指定する方式である7。

* **制御信号**: ユーザー指示テキスト、あるいは外部の物体検出器（YOLO, Grounding DINO等）が出力する検出座標7。  
* **メカニズム**: BLINKベンチマークにおける各種評価で用いられるように、入力画像上にバウンディングボックスやマスクをオーバレイ重畳することで、アテンションを物理的にその局所領域へ固定する7。

### **1.3 「いつ拡大するか」のゲート機構**

全領域を均一に高解像度処理するアプローチは計算コストの観点から非実用的であり、全体像で回答可能か、あるいは一部を拡大して再観察すべきかを「入力ごとに適応的に切り替えるゲート機構」が極めて重要となる。

#### **判断信号の種類**

切り替えのトリガーとして用いられる信号には以下の種類が存在する。

> 1. **1位の予測確率（Top-1 Probability）**: 1パス目の分類出力における最大ソフトマックス確率が一定値未満の場合に不確実とみなす11。  
> 2. **1位と2位の確率差（Margin Score）**: 尤度1位と2位のクラスの差分（![][image4]）を算出し、この値が小さい（競合している）場合に細部鑑別が必要と判断する11。  
> 3. **予測分布のエントロピー（Entropy）**: 出力確率分布の平均情報量を測定し、不確定度が高いサンプルを抽出する11。  
> 4. **自己申告による確信度（Self-Reported Logprobs / Language Confidence）**: 生成トークンの対数確率値（Logprobs）や、LLMが言語的に出力する確信度表現（「確信がない」等）を利用する17。  
> 5. **学習されたルータ（Learned Router / Policy Network）**: Glance and Focus（GFNet）のように、大域特徴から「この画像は局所拡大が必要か」を直接二値分類予測する軽量ネットワークを設ける11。

#### **閾値の設定とドメイン移植性**

拡大を実行するか否かを分ける閾値（例：Margin ![][image5]）は、検証データセット上における精度と計算コスト（FLOPs / トークン数）のトレードオフ曲線（Pareto Frontier）から最小コストで最大精度を達成する地点として同定される11。  
この閾値の**ドメイン移植性（Portability）は低く、自然画像から白背景線画（意匠図面）へ移転する際には厳密な再較正（Recalibration）が不可欠**となる。線画画像では自然画像と比較して全体的なモデルの出力Logitが不確実側にシフトしやすく、標準的な閾値では過剰に拡大が発動する、あるいは逆に拡大が全くトリガーされないという現象が生じるためである。

### **1.4 識別性を目的にした学習手法（ViT / MLLM期）**

類似した細部デザインや微小差分を精度高く区別するために、2020年以降のViT/MLLM期では単なるクラス分類クロスエントロピーを超えた学習アプローチが展開されている。

#### **ハードネガティブ対照学習・選好最適化（Fine-Grained DPO / Visual Preference Optimization）**

視覚的に極めて酷似しているが異なるラベルを持つ画像対（ハードネガティブ）を生成し、直接選好最適化（DPO）を適用する手法である18。

* **改変対象**: 目的関数および言語モデル（LLM）側のデコーダパラメータ18。  
* **メカニズム**: 同一カテゴリに見えるが微小な構造（スリットの有無等）が異なる画像を入力し、誤った製品名を生成した応答をReject、正解をAcceptとしてDPO損失を計算することで、類似意匠間の境界線における識別確率を高める18。

#### **細粒度識別を目的とした視覚エンコーダの後追い学習**

事前学習済みCLIPの限界を克服すべく、視覚エンコーダ側（またはコネクタ）自体を細粒度構造保持に向けて追加学習する8。

* **改変対象**: 視覚エンコーダ（ViT）およびコネクタ（Projector）のパラメータ20。  
* **メカニズム**: DINOv2やDINOv3等の自己教示型学習（Self-Supervised Learning）は、画素・パッチレベルの密な構造特徴（Dense Features）を保持するため、クラスレベルの抽象化を行うCLIPよりも線画の局所幾何構造の差分を強く保持できる21。特許ドメインにおいては、DeepPatent2等で階層的特許分類タスクを利用したマルチポジティブ対照学習（Hierarchical Multi-Positive Contrastive Loss）により視覚エンコーダのパラメータが再最適化されている20。

#### **細粒度評価ベンチマーク**

* **BLINK (ECCV 2024\)**: 人間が一瞬で判断できるがMLLMが苦手とする14の知覚タスク（対応点合わせ、相対深度、視覚的類似性等）を定量評価する体系7。  
* **BLINK-Twice (2025/2026)**: 単なる表面的な認識（See）を超えて、細部を注意深く観察・考察（Observe）しなければ解けない自然対照画像対ベンチマーク17。  
* **HueManity (2025)**: 石原式色覚検査表のように、複雑な視覚ノイズ・背景混雑（Visual Clutter）の中に埋もれた微小な幾何パターンや文字を認識させるテスト体系。現行MLLMが人間の100%や細粒度CNN（ResNet50）の96.5%に遠く及ばない3%前後の精度しか出せないことを証明し、MLLMの細粒度視覚知覚の構造的弱点を白日の下に晒した9。

### **1.5 線画・スケッチ・技術図面・特許画像（ViT以後）**

自然画像中心に発達したViTおよびMLLMを、テクスチャや色彩情報を持たない「白背景の線画・技術図面・特許画像」に適用する場合、特有のドメインギャップと挙動の差異が観察される。

#### **ドメインギャップとアテンションマップの信頼性**

* **ViTのセマンティック抽出能力**: Composite Sketch Recognition（2022）等の知見では、ViTのSelf-Attention機構は、色彩を欠くスケッチ表現に対しても物体の構成要素（例：顔の目や鼻、機械の主要パーツ）へ比較的強い注意を割り当てられることが確認されている26。  
* **線画特有のアテンションノイズ**: しかし、最新のSketchSense（2026）等の研究では、空間的に疎（Sparse）なユーザー線画や技術図面においては、広大な「白背景領域」が原因で、アテンションマップや勾配マップに広域な背景ノイズ（Background Drift）が発生することが報告されている27。線画のストロークが局所的であるため、大域的な注意の重みが外郭の閉曲線（シルエット）へ不釣り合いに集中しやすく、面の内側にひっそりと存在するスリットや小さな穴に対する注意の強度が相対的に低下する傾向が定量的にも認められる27。

#### **特許図面からの教師なし局所領域抽出**

特許図面や線画から、人間の教示アノテーションなしに重要局所領域を切り出す技術として、DINOv2等の自己蒸留ViTのパッチ特徴量を活用した「Unsupervised Part Discovery（教師なしパーツ発見）」手法（COLER, MaskCut等）が有効性を示している28。これらの手法は、自己注目行列のスペクトラルクラスタリング（Normalized Cuts）を行うことで、画像内の幾何的領域（外郭と内部パーツ）を教師なしで明確に分離・セグメンテーション可能である29。

## **2\. ViT / MLLM期における主要研究の比較**

以下に示す一覧表は、2020年以降に提案された視覚トークン粒度制御、注目領域切り替え、動的拡大処理に関する代表的研究を比較・整理したものである。

| 論文名 | 年・会議 | 査読 | 視覚エンコーダと入力粒度 | どこを見るかの決め方 | いつ拡大するかの決め方 | 質問文が必要か | 評価ドメイン | 線画検証 | 実装公開 |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| **Glance and Focus (GFNet)** \[cite: 11, 16\] | 2020 NeurIPS / 2023 TPAMI | 査読有 | CNN / ViT (縮小大域 \+ 局所パッチ) | 強化学習による提案器 (Policy Net)11 | Glance段階の分類確信度（閾値処理）11 | **不要**（画像分類）11 | ImageNet, Video16 | なし | 有 |
| **AdaFocus / AdaFocusV2** \[cite: 12, 13\] | 2021 ICCV / 2022 TPAMI | 査読有 | ResNet / ViT (動的パッチ抽出) | 微分可能補間パッチ選択12 | タスク依存の計算予算と確信度12 | **不要**（画像/動画分類）12 | Dynamic Video/Image12 | なし | 有 |
| **AdaViT** \[cite: 31\] | 2022 CVPR | 査読有 | ViT (レイヤー別パッチ/ヘッド選択) | 判定決定器 (Decision Block)31 | 層ごとのトークン維持スコア31 | **不要**（画像分類） | ImageNet | なし | 有 |
| **DINOv2 (NCut / Part Discovery)** \[cite: 22, 29, 30\] | 2023 / 2024 ECCV | 査読有 | ViT-S/B/L/g (密パッチ特徴量)21 | パッチ特徴の自己類似度グラフラプラシアン30 | 固定（全高注目領域の解析） | **不要**（自己教示特徴） | Natural Images, Cell19 | 一部（スケッチ） | 有 |
| **BLINK Benchmark** \[cite: 7, 15\] | 2024 ECCV | 査読有 | 多種 MLLM (GPT-4V, LLaVA等)7 | 視覚プロンプト (丸印、ボックス、マスク)7 | 固定（ベンチマーク問題規定） | 必要 (VQA形式)7 | Core Visual Perception7 | 一部（対応点） | 有 |
| **FocusLLaVA** \[cite: 1\] | 2024 arXiv | 査読前 | Multi-scale ViT (動的領域圧縮) | 視覚ガイド sampler \+ テキストガイド sampler1 | トークン冗長性と命令関連度1 | 必要 (テキストガイド時)1 | MLLM Benchmarks1 | なし | 有 |
| **DeepPatent2 (Patent Contrastive)** \[cite: 20\] | 2024 arXiv | 査読前 | ViT / CLIP (大域特徴)20 | 画像全体の階層的特徴空間 | 拡大なし（多重正例対照学習）20 | **不要**（画像検索）20 | 特許図面 (DeepPatent2)20 | **有（特許線画）** \[cite: 20\] | 有 |
| **HueManity** \[cite: 9\] | 2025 OpenReview | 査読前 | 各種 MLLM (GPT-4o, Gemini等)9 | 石原式色覚検査表パターン9 | 評価ベンチマーク（単一パス） | 必要 (VQA形式)9 | 細粒度視覚知覚9 | なし | 有 |
| **PVC (Progressive Token Comp)** \[cite: 6\] | 2025 CVPR | 査読有 | Dynamic ViT (静的動画拡張)6 | 時系列プログレッシブ抽出6 | フレーム反復による補完制御6 | 必要 (VQA形式) | Long/Short Video, OCR6 | なし | 有 |
| **Blink (Dynamic Token Res)** \[cite: 32\] | 2026 CVPR | 査読有 | ViT \+ LLM (レイヤー間動的トークン)32 | 内部レイヤーのSaliencyマップ32 | Saliencyスコアのレイヤー間動的閾値32 | **不要**（アテンション駆動）32 | General MLLM Bench32 | なし | 有 |
| **Vision-RL2 (SD-RPN)** \[cite: 2\] | 2026 ICLR | 査読有 | Dynamic ViT (大域128トークン+RoI)2 | 注意マップ蒸留 RPN (SD-RPN)2 | 1パス目の回答貢献度スコア (Reader)2 | 必要 (VQA)2 | ZoomBench, Fine-grained2 | なし | 有 |
| **FIRM (Intra-token Mask)** \[cite: 3\] | 2026 CVPR | 査読有 | ViT \+ Connector (![][image3] 結合)3 | トークン内サブセルコード (![][image6])3 | 常時（全圧縮トークンに適用）3 | 必要 (Reasoning Seg)3 | Satellite, UAV (LaSeRS等)3 | なし | 有 |
| **SketchSense** \[cite: 27\] | 2026 arXiv | 査読前 | Diffusion / ViT Dual-branch27 | 自律的線画信頼度予測 (Reliability Predictor)27 | 空間ゲート予測器による動的適用27 | 条件による | 線画インペインティング27 | **有（線画・スケッチ）** \[cite: 27\] | 有 |
| **Q-Guide** \[cite: 10\] | 2026 arXiv | 査読前 | MLLM \+ Agent Tool10 | LLMエージェントによるツール呼出10 | 不足視覚証拠の言語的検出10 | 必要 (Document VQA)10 | 文書理解, 細粒度VQA | なし | 有 |

## **3\. 核心的問いへの直接回答**

### **質問1：質問文が無い状態（画像のみ）で、全体と局所を対象ごとに切り替える研究はあるか？**

#### **回答**

**明確に存在する。**

#### **詳細と分析**

MLLM（視覚言語モデル）の枠組み以前から発展してきた**動的推論（Dynamic Inference / Adaptive Inference）分野の研究**（Glance and Focus / GFNet11、AdaFocus / AdaFocusV212 など）は、テキスト質問が存在しない純粋な画像分類・識別タスクを対象として構築されている。  
これらの手法では、1パス目に縮小した画像全体をエンコーダに与え（Glanceステップ）、出力された分類ソフトマックス確率の最大値（Top-1確率）やエントロピー、Margin（1位と2位の確率差）を計算する11。

* **切り替え判定**: Softmax確率の最大値が閾値 ![][image7] を超えている場合（例：![][image8]）、モデルは大域シルエット（輪郭）だけで十分確信を持っていると判断し、推論を即座に終了（Early Exiting）する11。  
* **局所拡大**: ![][image9] の場合、画像は「大域のみでは識別不可能な難解サンプル（タイプAに相当）」と判定され、強化学習や微分可能補間によって学習されたポリシーネットワーク（Focusステップ）が、面内部の最も情報密度の高い局所領域（内側の微小パーツ）の座標を自動計算して切り出し、高解像度で再評価する11。

また、最新のMLLM研究においても、**Blink（CVPR 2026）** のように、テキスト命令に依存せず、Transformerの内部レイヤーにおける視覚トークン間のSaliency（著しく高いアテンション値）を直接監視し、単一のフォワードパス内で顕著な局所トークンのみを動的に再展開・高解像度化する技術が実証されている32。

### **質問2：疎な線画で、注意マップや勾配マップが意味のある領域を指すことを検証した研究はあるか？**

#### **回答**

**意匠特許図面（正面線画）における定量的検証は「存在しない（文献上の空白領域）」。ただし、一般的なスケッチ・線画に対する定性的・定量的検証は存在する。**

#### **詳細と分析**

ArXiv、CVPR、ECCV、ICLR、IEEE TPAMIの2020年〜2026年の文献群において、「Patent Drawing」「Line Art」「Sketch」「Attention Map Reliability」「Gradient Saliency」を交差検索した結果、以下の事実が判明した。

* **ViTのセマンティック抽出能力**: Composite Sketch Recognition（2022）等の研究により、ViTのSelf-Attention機構は、色彩やテクスチャを欠く線画入力であっても、アームや先端構造などの「識別的な幾何学的パーツ」にアテンションの集中を生じさせることが確認されている26。  
* **線画特有のアテンションノイズ**: 一方で、SketchSense（2026）等の最新研究では、疎な線画入力において、画素の大部分を占める「白背景領域」が原因で、標準的なアテンションマップや勾配マップに広範域のノイズ（Background Drift）が発生することが判明している27。線画のストロークが局所的かつ疎であるため、アテンションの重みが単なる閉曲線の外郭（シルエット）へ不釣り合いに集中しやすく、面の内側にある小さなスリットや穴に対する注意の強度が相対的に著しく低下することが報告されている27。  
* **小結**: 「疎な線画であってもViTのアテンションは全体構造を指す」ことは確認されているが、「面の内側の微小な差込口や穴などの高次識別パーツを正確かつ安定的（ノイズなし）に指し示せるか」という点については、標準的なアテンション/勾配手法では信頼性が低い（補正機構が必要である）ことが示唆されている27。

### **質問3：遮蔽（領域を隠して出力の変化を見る）で、視覚言語モデルがどの部分に依存しているかを調べた研究はあるか？**

#### **回答**

**明確に存在する（Visual Ablation / Visual Dependence Studies）。**

#### **詳細と分析**

2025年〜2026年にかけて、MLLMが本当に画像（視覚トークン）を見て回答しているのか、それとも言語モデルの事前知識（Language Priors）や質問文のバイアスで回答しているのかを解明するための「視覚遮蔽（Visual Ablation / Spatial Occlusion）」研究が急速に増加している33。

* **遮蔽アプローチの手法**: 画像内の特定グリッドパッチや、バウンディングボックス領域、背景領域、あるいは面内部の特定オブジェクトをパッチ単位で黒塗りマスク（Occlusion）またはガウスノイズ置換し、LLMの出力確率（Logit）の変化や最終回答の変化を追跡する33。  
* **研究事例と知見**: Qwen-VLやLLaVA系の評価において、画像を段階的に遮蔽しながら言語モデルの出力尤度変化を測定した研究（Qwen3-VLを対象としたVisual Ablation研究など）では、MLLMが「物体の外郭（シルエット）を遮蔽すると著しくパフォーマンスが低下する」一方で、「面内部の微細構造を遮蔽しても出力Logitがほとんど変化しない」ケースが多いことが判明している33。これは、現在のMLLMの視覚表現がシルエットや全体概念（Macro-level Semantics）に極度に依存しており、内側の局所幾何変化に対する視覚依存度（Visual Reliance）が構造的に極めて低いことを定量的に裏付けている33。

## **4\. 本課題における既存研究の空白（Gap Analysis）**

本課題である「白背景の正面図線画1枚」「質問文なし（ゼロショット8択識別）」「対象（タイプA/B）に応じた解像度・注視領域の動的切り替え」「酷似した意匠（ハードネガティブ）との精密識別」という条件と、既存研究の間には以下の4つの明確なギャップ（空白領域）が存在する。

### **1\. 「高密度自然画像前提」と「極小線画構造」のギャップ**

既存のトークン圧縮やAnyResタイリング技術（LLaVA-NeXT, Qwen2-VL, FocusLLaVA等）は、自然画像の色彩・テクスチャ情報が豊富に存在する高密度データを前提としている1。白背景線画では、90%以上のパッチが「単なる白背景」であり、残り数%のパッチに幾何情報が集中する。既存のトークンプーリングや ![][image10] パッチ結合をそのまま適用すると、微小なスリットや線画の不連続性が「背景」として平滑化され、完全に失われる3。

### **2\. 「テキスト質問依存（VQA）」と「画像完結型識別」のギャップ**

近年提案されている高精度な注目領域抽出モデル（Vision-RL2, Q-Guide等）は、「〇〇の文字を読め」「〇〇の部品はどこにあるか」といった明示的なテキスト質問（Query）をアンカーとして視覚アテンションを誘導する2。本課題のように「質問文が存在せず、画像だけを見て正解クラスを推測する」設定では、アテンションを導くテキストアンカーが存在しないため、既存のVQAベースのズーム機構をそのまま適用することはできない2。

### **3\. 「マクロ分類アラインメント」と「ミクロ意匠差分」のギャップ**

CLIPやQwen-VLの視覚エンコーダは、大域的なセマンティクス（例：「皿」「シューズ」）を揃えるように事前学習されている7。このため、モデルは「タイプB（シルエットで決まる製品）」には高い判別力を示すが、「タイプA（皿の深さやくぼみ、差込口のスリット形状だけで製品カテゴリが変わる製品）」に対しては、視覚エンコーダの潜在空間（Embedding Space）レベルで差分を認識できていない。

### **4\. 線画に対する注意マップの評価・教師なし切り出しの未成熟**

特許図面のような疎な線画から、人間のアノテーション（教師データ）なしで「内側の重要な幾何構造パーツ」のみを精度高く判定・切り出す専用のフレームワークは、特許検索・画像処理分野においても未だ確立されていない20。

## **5\. 本タスクへの転用候補（4選）**

上記分析を踏まえ、現行の Qwen3-VL-4B の精度（約42%）を大幅に改善するために、既存研究の要素技術を本課題へ移植・応用する具体的アーキテクチャ案を4件提案する。

### **転用候補1：Glance-and-Focus 方式の「2-Stage Logit Margin 判定型 Gated Zoom パイプライン」**

画像完結型（質問文なし）で動的切り替えを実現する、最も実装が容易で即効性の高いアプローチである11。

#### **処理プロセスとアルゴリズム**

> 1. **Stage 1 (Glance)**: 画像全体（例：448×448）を Qwen3-VL-4B に入力し、8つの選択肢に対する出力対数確率（Logits）を取得する。  
> 2. **ゲート判定**: 1位の確率 ![][image11] と2位の確率 ![][image12] の差分（Margin ![][image13]）を計算する。  
   * Margin ![][image14]（例：![][image15]）の場合：モデルは外郭（シルエット）だけで十分確信を持っている（タイプB）と判断し、Stage 1の予測結果をそのまま採用して終了する。  
   * Margin ![][image16] の場合：大域情報だけでは判別不能（タイプA）と判定し、Stage 2（Focus）を起動する。  
> 3. **Stage 2 (Focus)**: 画像の外形輪郭線をマスク（画像処理的マスクまたはDINOv2特徴量で背景・外輪郭を除去）し、「面の内側の線画要素が存在する領域」のバウンディングボックスを抽出して拡大クロップ（高解像度化）する。  
> 4. **統合推論**: Stage 1の大域LogitとStage 2の局所クロップLogitを加算（加重平均）し、最終的な製品名を判定する。

#### **定量的・技術的仕様**

| 評価項目 | 詳細内容 |
| :---- | :---- |
| **必要なデータ** | チューニング不要（Zero-shot動作可能）。閾値 ![][image7] の決定用に数十〜数百枚の検証用図面のみ使用。 |
| **学習の有無** | **学習不要（Training-Free）**。 |
| **計算コスト** | タイプB（確信度高）のサンプルでは従来通り1パス。タイプA（不確実サンプル）のみ2回の推論が発生し、平均推論時間は約1.3〜1.5倍に抑制11。 |
| **想定される落とし穴** | 拡大領域（RoI）の抽出において、アテンションマップだけに頼ると余白や外郭に引っ張られる。Cannyエッジ抽出や輪郭距離変換（Distance Transform）などの伝統的画像処理を用いて「外郭シルエットを意図的に除外した内側中心領域」をクロップする幾何ルールの併用が必須。 |

### **転用候補2：DINOv2 密特徴量スペクトラルクラスタリングによる「内側パーツ自動抽出プロポーザル」**

CLIP系エンコーダの弱点（大域アライメント過多）を補うため、自己教示型モデル（DINOv2）の密特徴量を利用して内側の微小幾何構造を自動特定する21。

#### **処理プロセスとアルゴリズム**

> 1. **DINOv2エンコーディング**: 入力線画を DINOv2 (ViT-L/14) に通過させ、各パッチのDense Token Vector（![][image1] ピクセル単位の特徴量）を取得する21。  
> 2. **スペクトラルグラフラプラシアン分割（NCut）**: 白背景パッチを除外し、線画が存在するパッチ同士のコサイン類似度行列を作成する30。Normalized Cuts (NCut) を適用して、外郭（シルエット）を形成するパッチ群と、面内部（差込口、凹凸、LEDなど）を形成するパッチ群を完全自己学習（教師なし）で2〜3個のクラスタに分離する29。  
> 3. **内側パーツのズーム提示**: 内部クラスタに属するパッチの最小外接矩形を計算し、その領域を「注目局所画像」として Qwen3-VL の視覚トークン列に追加（マルチ画像入力またはタイル分割入力）する。

#### **定量的・技術的仕様**

| 評価項目 | 詳細内容 |
| :---- | :---- |
| **必要なデータ** | アノテーションデータ不要（完全教師なし動作）30。 |
| **学習の有無** | **学習不要（Zero-shot）**30。 |
| **計算コスト** | 低コスト。DINOv2の1パスおよび小規模行列のNCut計算（数ミリ秒）。 |
| **想定される落とし穴** | 正面図の中に図面枠線や寸法線、補助線が含まれている場合、それらが「内側構造」として誤検出されるリスクがある。前処理として図面外枠のトリミングが必要。 |

### **転用候補3：特許分類階層を用いた「Hard Negative Visual Preference Optimization (DPO)」**

LLM側の選択空間において、外形が似ている別特許（ハードネガティブ）と真の製品名を明確に差別化できるように直接選好最適化を行う18。

#### **処理プロセスとアルゴリズム**

> 1. **データセット構築**: 意匠特許の分類コード（Locarno分類等）を利用し、同一大分類（例：皿、器）に属しシルエットは似ているが、細部（内側の構造）が異なり間違えやすい製品の組（Hard Negative Pairs）を作成する。  
> 2. **DPOペアの作成**:  
   * **Prompt**: 「この図面の製品名を選択肢から選べ」  
   * **Winning Response (![][image17])**: 正解の製品名およびその製品を決める根拠（例：「内側の楕円状スリットが存在するため製品Xである」）  
   * **Losing Response (![][image18])**: 誤答しやすい似た製品名（タイプAの誤答事例）  
> 3. **Direct Preference Optimization (DPO)**: Qwen3-VL-4B のLoRAファインチューニングを行い、視覚トークンから微小差分を読み取って正しい製品名を回答する確率を直接引き上げる18。

#### **定量的・技術的仕様**

| 評価項目 | 詳細内容 |
| :---- | :---- |
| **必要なデータ** | 数百〜数千件の特許図面と製品名ペア、および類似特許の誤答選択肢ペア（ハードネガティブ）18。 |
| **学習の有無** | **LoRAによるファインチューニングが必要**（LLM層およびProjector層）18。 |
| **計算コスト** | 中程度（A100/H100 GPU 1〜2台で数時間の学習）。 |
| **想定される落とし穴** | 訓練データに存在する製品カテゴリに過適応（Overfitting）し、未見の製品カテゴリ（Zero-shot）に対する汎化性能が低下するリスクがある。これを防ぐため、DPO損失のKLダイバージェンス係数 ![][image19] を厳密に制御する必要がある18。 |

### **転用候補4：トークン内空間構造補正デコーダ（FIRMアプローチ）のコネクタ適用**

パッチ結合（コネクタ）段階で潰れる微小スリット情報を、トークン内部の補完構造として言語モデルに伝える構造改変案である3。

#### **処理プロセスとアルゴリズム**

> 1. **Intra-Token Gridの定義**: 視覚エンコーダとLLMを繋ぐコネクタにおいて、パッチを ![][image10] 等で結合して1トークン化する際、単なる平均プーリングを行わず、各トークン領域をさらに ![][image6] のサブセル（Sub-cell）に分解する3。  
> 2. **Sub-cell Binary Pattern Codeの生成**: サブセル内の線画の有無（0/1パターン）を軽量なLookup Tableまたは可変ビットコードとして特徴量に付加（Concat）し、LLMへ入力する3。  
> 3. これにより、1つの視覚トークンの中に「内部に横方向のスリット線が存在する」という空間幾何情報が明示的に保存された状態でLLMに入力される3。

#### **定量的・技術的仕様**

| 評価項目 | 詳細内容 |
| :---- | :---- |
| **必要なデータ** | 意匠図面データ（数千件）。 |
| **学習の有無** | **コネクタ（Projector）の再学習が必要**3。 |
| **計算コスト** | 訓練コストは低〜中程度（コネクタのみの学習であるため軽量）。 |
| **想定される落とし穴** | Qwen3-VLの内部ソースコード（モジュール構造）を直接改変する必要があり、実装の難易度が転用候補1〜3と比較して著しく高い。 |

## **6\. 結論と推奨ロードマップ**

意匠特許の正面線画識別における現状の誤答（約80%が製品名への結びつけ失敗、タイプAの局所見落とし）は、最新のViT/MLLMが抱える「大域アライメント過多」および「視覚トークン結合時の空間構造損失」という本質的課題と一致している3。  
今後のプロジェクト推進においては、以下の3段階のステップで対策を講じることを推奨する。

> 1. **Phase 1（即座に適用可能な訓練不要アプローチ）**: 「転用候補1：2-Stage Logit Margin 判定型 Gated Zoom パイプライン」を構築する。Qwen3-VL-4B の1パス目のLogit Marginスコアから不確実サンプル（タイプA）を検知し、外郭シルエットを除去する画像処理的クロップ（またはDINOv2特徴量クロップ）を適用して2パス目の高解像度推論を行う。これにより、追加学習なしでタイプAの精度底上げを図る11。  
> 2. **Phase 2（教師なし局所領域抽出の強化）**: 「転用候補2：DINOv2 密特徴量スペクトラルクラスタリング」を導入し、線画の面内部に隠れた微細構造領域のクロップ精度を自動化・高度化する30。  
> 3. **Phase 3（類似意匠鑑別アラインメント）**: 十分な特許図面データが確保できた段階で、「転用候補3：Hard Negative DPO」を適用し、酷似した意匠対における局所視覚差分に対するLLMの感受性を直接最適化する18。

この段階的アプローチをとることで、モデルや学習コードを大きく改変することなく、既存の Qwen3-VL-4B のポテンシャルを最大限に引き出し、タイプAの過失原因である「ミクロ幾何構造の見落とし」を効果的に解消することが可能となる。

#### **引用文献**

> 1. arXiv:2411.14228v1 \[cs.CV\] 21 Nov 2024, [https://arxiv.org/pdf/2411.14228?](https://arxiv.org/pdf/2411.14228)  
> 2. Region-Level Policy Optimization for Fine-grained MLLM Perception, [https://cspaper.org/openprint/20260918.0006v1.pdf](https://cspaper.org/openprint/20260918.0006v1.pdf)  
> 3. FIRM: Fine-Grained Intra-Token Representation of Masks for ... \- arXiv, [https://arxiv.org/html/2608.13980v1](https://arxiv.org/html/2608.13980v1)  
> 4. Zero-shot 3D Question Answering via Voxel-based Dynamic Token, [https://cvpr.thecvf.com/virtual/2025/poster/33335](https://cvpr.thecvf.com/virtual/2025/poster/33335)  
> 5. visiontrim: unified vision token compression \- ICLR Proceedings, [https://proceedings.iclr.cc/paper\_files/paper/2026/file/2b5454315b4e4408e6c97e82323766ea-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2026/file/2b5454315b4e4408e6c97e82323766ea-Paper-Conference.pdf)  
> 6. PVC: Progressive Visual Token Compression for Unified Image and, [https://openaccess.thecvf.com/content/CVPR2025/papers/Yang\_PVC\_Progressive\_Visual\_Token\_Compression\_for\_Unified\_Image\_and\_Video\_CVPR\_2025\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2025/papers/Yang_PVC_Progressive_Visual_Token_Compression_for_Unified_Image_and_Video_CVPR_2025_paper.pdf)  
> 7. BLINK: Multimodal Large Language Models Can See but Not Perceive, [https://www.alphaxiv.org/abs/2404.12390](https://www.alphaxiv.org/abs/2404.12390)  
> 8. GitHub \- HKUST-LongGroup/Awesome-MLLM-Benchmarks, [https://github.com/HKUST-LongGroup/Awesome-MLLM-Benchmarks](https://github.com/HKUST-LongGroup/Awesome-MLLM-Benchmarks)  
> 9. HueManity: Probing Fine-Grained Visual Perception in MLLMs, [https://openreview.net/pdf?id=munNPK7yA7](https://openreview.net/pdf?id=munNPK7yA7)  
> 10. Question-Guided Evidence Acquisition for Multimodal Visual ... \- arXiv, [https://arxiv.org/html/2608.19739v2](https://arxiv.org/html/2608.19739v2)  
> 11. (PDF) Glance and Focus: a Dynamic Approach to Reducing Spatial, [https://www.researchgate.net/publication/344621750\_Glance\_and\_Focus\_a\_Dynamic\_Approach\_to\_Reducing\_Spatial\_Redundancy\_in\_Image\_Classification](https://www.researchgate.net/publication/344621750_Glance_and_Focus_a_Dynamic_Approach_to_Reducing_Spatial_Redundancy_in_Image_Classification)  
> 12. AdaFocus V2: End-to-End Training of Spatial Dynamic Networks for, [https://arxiv.org/html/2112.14238v2](https://arxiv.org/html/2112.14238v2)  
> 13. a Dynamic Approach to Reducing Spatial Redundancy in Image, [https://www.semanticscholar.org/paper/Glance-and-Focus%3A-a-Dynamic-Approach-to-Reducing-in-Wang-Lv/9fa283d4f9c2ed991383c0434ef6043bee0dc8e2](https://www.semanticscholar.org/paper/Glance-and-Focus%3A-a-Dynamic-Approach-to-Reducing-in-Wang-Lv/9fa283d4f9c2ed991383c0434ef6043bee0dc8e2)  
> 14. From Structure to Synergy: A Survey of Vision-Language Perception, [https://arxiv.org/html/2606.26196v1](https://arxiv.org/html/2606.26196v1)  
> 15. BLINK: Multimodal Large Language Models Can See but Not Perceive, [https://www.researchgate.net/publication/385423833\_BLINK\_Multimodal\_Large\_Language\_Models\_Can\_See\_but\_Not\_Perceive](https://www.researchgate.net/publication/385423833_BLINK_Multimodal_Large_Language_Models_Can_See_but_Not_Perceive)  
> 16. Glance and Focus Networks for Dynamic Visual Recognition, [https://www.computer.org/csdl/journal/tp/2023/04/09851927/1FFHb8gJcVG](https://www.computer.org/csdl/journal/tp/2023/04/09851927/1FFHb8gJcVG)  
> 17. BLINK-Twice: You see, but do you observe? A Reasoning ... \- arXiv, [https://arxiv.org/html/2510.09361v1](https://arxiv.org/html/2510.09361v1)  
> 18. Aligning Multimodal LLM with Human Preference: A Survey \- arXiv, [https://arxiv.org/html/2503.14504v1](https://arxiv.org/html/2503.14504v1)  
> 19. Cell-DINO: Self-supervised image-based embeddings ... \- PMC \- NIH, [https://pmc.ncbi.nlm.nih.gov/articles/PMC12826486/](https://pmc.ncbi.nlm.nih.gov/articles/PMC12826486/)  
> 20. Hierarchical Multi-Positive Contrastive Learning for Patent Image, [https://arxiv.org/html/2506.13496v3](https://arxiv.org/html/2506.13496v3)  
> 21. 9\. Learning to See Without Labels: A Technical Tour of Meta's DINO, [https://medium.com/@aminfadaeinejad.edu/learning-to-see-without-labels-a-technical-tour-of-metas-dino-dinov2-and-dinov3-d2d4b2a89504](https://medium.com/@aminfadaeinejad.edu/learning-to-see-without-labels-a-technical-tour-of-metas-dino-dinov2-and-dinov3-d2d4b2a89504)  
> 22. DINOv2: Learning Robust Visual Features without Supervision \- arXiv, [https://arxiv.org/html/2304.07193v2](https://arxiv.org/html/2304.07193v2)  
> 23. Motion-Refined DINOSAUR for Unsupervised Multi-Object Discovery, [https://arxiv.org/html/2509.02545v1](https://arxiv.org/html/2509.02545v1)  
> 24. BLINK-Twice: You see, but do you observe? A Reasoning, [https://www.alphaxiv.org/abs/2510.09361](https://www.alphaxiv.org/abs/2510.09361)  
> 25. HueManity: Probing Fine-Grained Visual Perception in MLLMs \- arXiv, [https://www.arxiv.org/pdf/2506.03194v3](https://www.arxiv.org/pdf/2506.03194v3)  
> 26. Transformer-based Representation for Face Attribute Evaluation, [https://arxiv.org/html/2207.05456v1](https://arxiv.org/html/2207.05456v1)  
> 27. Learning to Interpret Imperfect Sketch Guidance for Image Inpainting, [https://arxiv.org/pdf/2608.13186](https://arxiv.org/pdf/2608.13186)  
> 28. PartCraft : Créer des Objets Créatifs par Parties | Articles de, [https://hyper.ai/fr/papers/eccv\_\_2024\_\_01451](https://hyper.ai/fr/papers/eccv__2024__01451)  
> 29. Relaxing Part Discovery Constraints with Vision Transformers \- ECVA, [https://www.ecva.net/papers/eccv\_2024/papers\_ECCV/papers/11397.pdf](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/11397.pdf)  
> 30. Enhancing Object Discovery for Unsupervised Instance, [https://openreview.net/forum?id=QVzb9c3VCy](https://openreview.net/forum?id=QVzb9c3VCy)  
> 31. EFFICIENT DISTILLATION OF VISION TRANSFORMERS WITH, [https://openreview.net/pdf/7687726bd6e7a12d7e87dfb0f0cb60a8eb3d153a.pdf](https://openreview.net/pdf/7687726bd6e7a12d7e87dfb0f0cb60a8eb3d153a.pdf)  
> 32. Blink: Dynamic Visual Token Resolution for Enhanced Multimodal, [https://openaccess.thecvf.com/content/CVPR2026/papers/Feng\_Blink\_Dynamic\_Visual\_Token\_Resolution\_for\_Enhanced\_Multimodal\_Understanding\_CVPR\_2026\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2026/papers/Feng_Blink_Dynamic_Visual_Token_Resolution_for_Enhanced_Multimodal_Understanding_CVPR_2026_paper.pdf)  
> 33. Spatial4D-Bench: A Versatile 4D Spatial Intelligence Benchmark, [https://arxiv.org/html/2601.00092v1](https://arxiv.org/html/2601.00092v1)  
> 34. Spatial4D-Bench: A Versatile 4D Spatial Intelligence Benchmark, [https://arxiv.org/html/2601.00092v2](https://arxiv.org/html/2601.00092v2)  
> 35. Image-to-CAD Generation via Sequence-Based Diffusion \- arXiv, [https://arxiv.org/html/2605.13293v1](https://arxiv.org/html/2605.13293v1)  
> 36. Beyond NL2Code: A Structured Survey of Multimodal Code ... \- arXiv, [https://arxiv.org/html/2606.15932v3](https://arxiv.org/html/2606.15932v3)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAZCAYAAACFHfjcAAABq0lEQVR4Xu2WsUpDQRBFR0SwEEVBBFFBCxErwc7KHxBsrO1EUaz8ALGys7XzAyzsbdRCsBbs7EVsBD9A72WzMZlk3gxJXqo9cAlvdjczd5h9iUihUCgUCv0wAm3poMEF9KyDQ2QeOtJBgzXoUAc159Ab9Al9Qydtq92ZhX6hF71QM+vQB/Qj8fz7kva7vjahHWhB0hd7Bzg1nIZoIYNkGtqGZiSe/1XSXs9XkzmJNeIO2pV4IVOSGmcxCh3oYIBI/j1oVWK+mkQawWm4hsYkVgjh3jNoUS804NqDDgbw8i9DjxLz1YZ3YBK6bXn2CtFcSrthr0EeXn5OLq+Q56sD78ApdNPy7BWioXE2IxvvdRIyVfmXJL1LiOerA+/Ak6SfoUxVIRZsBs2vND57nQZi5WeOK0nXmHi+OrAO8AuPoXEVtwrx4FR8SbrD/WDlv5f/aSCWLxPrwISkdwMTW9JnLIYxEbo2LfqsxGqEhVWIBSeB5jN1vywzG9C7xH3V2og8Cdq0FY8QzR9uBDfo8clJuo2R3kdVJRnkHyrWo3Nnaawr3c1ToVAoFApB/gAUkoo2tdfGFAAAAABJRU5ErkJggg==>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEIAAAAZCAYAAACFHfjcAAACVElEQVR4Xu2Xz0tVQRTHT1QQpGVtpDLIFqJhIkgQbXRXm4LCRdQ+Elzqqk0UQohuhVoIQYQiRQRBtGnbRncVQYG0kXAj9AfU98u545t7dH707D1czAe++OacYe7M956ZO4oUCoVCobAXDkBXbNDQDd2HHkOjJtdOTkMTNmg4KDrPWdF5R3kIfYZ+QVvQZC3b4Bj0FLotahgn8kbaa8YFaAP6Df2BPtXTNb5Dr6rfnO9P6HkjvZMR6DrUIzpwyIhHog/noIT92L6z3aP1nIDGoJMSN6IfWoV6qzargf0/bPeIwM4hI7h4DmQd7TDt3TguamIIlu89G8wgZMSwaDXYSu2SxkuMEjPilOiDud8IF5fLYWgKOmsTFcx9tMEMQka4Su2r2qyiLAMcMSPGRQdfgs5UsWXR/ZrLE6kvOGVQipAR70RzPB/uilbcLdG585xLEjPCucyScwxAX6AhLxaDC6cZbuHNVoIjZARjzM1Bh6qY29p8fpIcI/wzgnuO7s9IfunRDC7+fPW32WogKSNGTZwxvrgkMSOuig7k53hQrkDfoEEvnoJvZVMaJ3qzhIzgnJiz9wbGqCQxIy5L2AhuF57UObSjIp5JC43gXuMg3HeOTui16HY54sVDsBK4eEerDstL0LrsrFL2ZyUmiRlBOMhbr30OWoOuebEQrhLsokPxHEJG8KW8gG6aOPu/NLEa7iC04kP88uKnZwF6D82LXscfePkQ//NC5W6Iu8nyFfoBLYp+5i/W03uDX4dp0X9ieCXfzxyFboheAsfqqUKhUCj8M38BBhCQ/qqdmB8AAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAADYAAAAXCAYAAABAtbxOAAABbklEQVR4Xu2VsStHURTHj1BCBiKSYpHFIIuSSAYDRdmVlV0ym00WmywGyapIStmU3WQ1+gP4ftx7c10/vVd+z0+5n/r06537e69z7jn3PbNMJpPJZDJ/lg45J1v9dbMckdOyzcdgTC779TKMyhvZlC54buVmGqwnF/JcnsgueSXv5JN8NJfYiryUZ/536P3OYsbNJZ8WR9G14nWDB2+b68KrPJYzPj4vn+WuPA03+P/tR9dFPNjnzlAU3aqsKFiQnXJAvsj1aG3WXGGTUQwo7CiJFTFhrjjGudJOBcIZmpL3cvhjybbMFdEexVp8bCeKlYXOsVFlz+iPIdlD+5os54wuxqzKa9mXxIv49Y4BY0gRi0mc3aWLATbgQO6ZS6zHyu0+RdGtUEzlb8NAGDnOWoARTUduzccoiCI3orXvaNhbERhDEo6hi3SMF0iAjjKadGlJ9kZrtWj4d6xfDiYxkulOYkBRnK/wMc9kMv+QN5TnOOSmW+7mAAAAAElFTkSuQmCC>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEQAAAAaCAYAAAAOl/o1AAACIElEQVR4Xu2Xz0tVQRTHv1GBRJm4MBCMF0EQuVE3SotE3LVpkeCqlkUIQtBC3AiuFBeC6N6FGQguBNsFLQN/bAKhMGgRtGgj9Afo98t5lzfvJNd5z6v3BfOBL3jnjHfOPXPmzHlAIpFIJBKXyW3qjlNb3YzW4QrViX/9vR5OOg83YS/cpY6pe9VnqYfar47r71Yg27wfML+6q8/SfeqwOt6e/UOzZAt4HlIH1AJ1zdnKRL6e5u8I9Yea8IZGUBrq5TveQCqwLPkC24VWQFktfze9gQxSv6gN2Lym6IAtsOoN5Aks4lsoIA0LogLzd9aNixcw2zLOkdHPYR+tj/fswRYorGgVwBT1lXrgDeQn9ReW9U2j+qDjogIV8gj28hU3XiY3qA+w43IrGFcAhqkjajoYb5he6hv1kZoPpNS7G8zLGIdV+rIYhW3Se9T7O0Z1BfNU795S72A3ZzQ6LjoST73B8YxaRHxxVbbNoN7pPMWmuI6L/O3zBsc6NQSri8qa2PdjG7ZAmH55xAbkosj6orwPlH/KemW/mKRe18z5ZI1MLGUHRMflLH91Aayh5qd6kqi+JOs/VLFjKTMgWf/xyRtyGIBteu4tqUD0Uy9hC6gTVdsb08iUEZCr1GPqDczfz7CfEjG/t3QjLfnBIikjIM2gjJiDBVMM10zF8r8EREX0VfB81i3aMGqEvsNS9jfsuLUq2jD5GaoSTkgkEomiOAHqU2d++HMFJAAAAABJRU5ErkJggg==>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACEAAAAaCAYAAAA5WTUBAAAA30lEQVR4XmNgGAWjYBSMgmEIsoH4GrogvYA4ELcB8RwgVkeToylgBOJlQPyUAeIIUkEQEF8E4v84MAdCKXZgDMQbgbgQiIXQ5IgBIA98ZsC0GIY/IJSiAlYgPsEAcT1BV+IB8kC8G41/GomPE/gyQCwPZIA4hprAA4hvoQviAsxAvJ+B8pBAB3uBeAW6ID4AcogtEF8H4lQ0OXLBayDuQRckFoAS12IgfsRAXu4AAT4GiCPs0SVIBaCE9RKI+9EliAAGQHwOiBXQxCkCpJaYoLTFiy5IDQBKN6NgFAx/AAAADieF6eEehgAAAABJRU5ErkJggg==>

[image6]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC0AAAAaCAYAAAAjZdWPAAABA0lEQVR4Xu2Uvw4BQRCHRygUev8ar4BEq1GIRKVRKhVq4gHUep3wAFpPQKWQeAOJB/AA/CZrc5fNnjNcRGS+5CvM7N79du4ckaIoiqIon5OFY7fo0IUDt5gEW7iBK1iEJ7iGM5gJrfORggdY89T7nnoUogx88QlMwxs8k5lgD+5hPlgayRAeQ79tYD7MK4gztGAOluAVtslsmMNOaF0cfGMOXif/5J8hzsBNpknmZpWgJYYnfoENtxHDWxl40xJO3YaATybNiDPwi78jc9J34MA8ZRvUvs+S4OIMIzJ/APuYJCT19RBnWJDZIMUGq7qNB1EH8iHOUIBlt/hlfiGDoih/zR2/mjGob4jw+QAAAABJRU5ErkJggg==>

[image7]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAoAAAAXCAYAAAAyet74AAAAYUlEQVR4XmNgGAXDBPACcTMQ/8eBo0GKWIF4BxBrQ/QwKACxPZSNAgKBmA+Nr4DExwrEgHg/EDOiS6ADkJWv0QWxga1AfBldEBt4AMR70QWxAVBQJKELYgNmQMyMLjjAAADCMw+8bZc67gAAAABJRU5ErkJggg==>

[image8]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGoAAAAaCAYAAABfA8lWAAAD90lEQVR4Xu2Y26tNURSHh1DKcQ8hHCkRcnsR6UhKbkVRoijxRErxhJJrScmLIpGUTpRyzQPhQei4hCLFi5QH5cUfwPjO2LM117DXvqy9tU/nrK9+nbXGXGftueaYY44xp0hBQUFBQUFBQUHfZJhqrNOg1BMFLadNzDGvVH9UU0r3aKLqTcnOdW9kvOqeaq9qveqn6kDqiWyGqj6qzqrOq76JvS/mkdj4daleij3DPeOei69iL/DMEOvMadUA19Yb6BT7vsAu1S9Vv8hWjoGqU6oRkY1JzvtwYCA4Kui36kTUXhd0Knjd0y4WVS/EoqyVdIjN9pG+IScMKN+9OrIxGS+odke2ctD+2RuVL5L+3xuqFdF9QwwX6/AV3yA2OCwHtyU9U1rFGbHlY7JvyMFcsRm+3NlZyhiLSnkaZzBmRFbMd9XW6L6pjtog5gyc4nkt5TvUaoiqQ6pbqgWurVYYbCIAh3n7B9U0Z48hFz0WGxsmzmDVPklHJwRHHVE9KV3nHkvyD8ueT4QzxWbcOWfvSexUfVItUfV3bdWo5Khyds9sSXIPkUQ+8uCoO6odqrViTqV4qZtZYmvtfbHkGET4ToqeazYsK5u8sQGYpVRt71SbXVsWWQ7JsnuIuAeqPZI47KqkU8Ri1bjovl0s52+PbDXBsucTajnYa23xxhxQJa0Tq7QoUJrNSrElid+oVrllOSTLHsMEfy+JU8hrrD6MJctcFqPEIo9Ia3NtFSEMefkQ3+DYqLrujQ3AhzXTUSGieCd/a4F8wbZknrMfVT1TjXH2GBxJYePBeeR7oE9cH0+au52Dk+quovlBHFUNNmskbn9qsUgs9EmmQOf4QEKe61VSfmY201H0hyWPSKonTxEVfLuvymqp+vi/uAwP4GQiC1gaeQ7nBQiIm1J9IqQI+ycqnGowC1BgtOqhJMsLEfc2ae4euFA1sRG8LOkPb9RRoeq7JvmrPuD74xlPPnmumh7ZuOY5fivAtzPYnrti3wrsyXh3PHmWiUXZ0siWCYM7X7VNrAPki6lSec30jqLYCCEORA3RGYhDm9+jKlqYNDfkKN5L9XTRN+SgU9L9PiwWEXF+Y5/FOMX9XaP6oZoQ2YgWoodIDVA4xEXTU/n3/U0lOIpiYI5YiDP4geCocMzk12A+NC5Y8jiK2UgUNetkIsCMPyhW7db77g6x/90v5Zd4IC2cLCmkiP9GcBSdOSaWsMNaDERL7LjYUTiPqOXcMJDHUfXknz4LlRF555IkJ+mEOvsIZiLnY3EE4Rie5VSZHBh24+Q2kikRhrrEluCCJsJg++MPCoRyZWaIKF8lFvQQcCSVE9FHwVLQQ+HYiZ15OIoqKOjd/AUqydU5voArVwAAAABJRU5ErkJggg==>

[image9]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFEAAAAaCAYAAADPELCZAAACs0lEQVR4Xu2Yz8sNURjHv0IpvxNK4cqP8iu/IpTejRVZKDYUWSgLKRs7m5cspGRjIURJohRFino3FL1+hFJEJGVh6Q/g++2ZY+Y+XnPnmpl7R86nvnXPec7Mnfnec57znAtEIpFIJBJpPpOpmU7j2kZEcpkAM+0p9YOal7Sl2dTzpF+f/xWWUhd8Zy/4ADPLs5h6Q52ixrhY0xhFraHeUYddrHb05TJw2AdICzYbH8NmZxPZDnu+XehjGpoCM/GyD5AB6ht1m5rkYv1Ghsm4IWqLi/WcHTCjZJjnGczgsT7QR45SH2FLV6uoDBOpr7B39PpO7U6H5qN8p6U8y/UrQetGZ11/v1A6OUFdhT1bWbSyruF384JeUct+jc5Bg95Sd6mTGe2h5mTGVY3urVzWLQupzzAzy3ID7SlKq66VaRdGS1mub/UBh2rJwlM7h0XUPtgSOuNiRZlLnabOw0ytAqWFm7Dl3TV3YCZ2ungndd13lkC76d+amEXPrZLmFsrlxwHqgO8synuYiZ14AntQf5rZSB2ixidtxTRGSX80tY1akMSyVGWi0Hfvp+5Rm1ysKMeozb6zCKE+fO0DI6D8IQWmUw+Q/vqaqS+SzzoF6YU0RmygBtE+U6o0MYt+uCHqoQ/ksJb6RE1z/bnoZVZTe2Em6kQyH/byf8KbqI1HZVFgJWxWC91HY8P9NDtVsLeStqjLRCEj9TxFOQjzofYTWTBxKrUCNv2/ZOLBRD2IN1HoWLkq067TxG5R+lnnO+sgmCizjsPKE9WQgfVITfUmqozQEpuRtEWTTOwZmkUvqYtI/9HRzqjcp7ryHNKztcxTTrpCXYLl3JAPtQsOIy1o71NLklgnjsA2uCJ6lFzTOHT088e/sBtnyc5EzT5/TaQDMlUFsGZoVYXwf8dytB8fI5GR+Ql+xIVzWy959wAAAABJRU5ErkJggg==>

[image10]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAAZCAYAAABOxhwiAAABg0lEQVR4Xu2Vvy8EURSFr4hE4neBRIhIRKVAJdGTyEal8i9QUmi0RCcqpWgIrUYkClEItURC7c/gHG92c+d68+ZNdkf1vuRkM+fO7Hzzdt+uSCKRSNRFF7KHHCMbSF9+/C/QYVacw6FEOPDEK3V8inwjDdXVTY84h5HseECcw1frDA8fyJY6nkQekRdkWvV1siLOoVt1dKB8oQOHTK/qNrNuR3U+hpAJWyoosmpLD/vi7neuulKHV+TTdKUXZfAjvkOm7EDcbFf8M8u8OId11cU6tBhDHpB7ZNTMfFDwSPKC7PgeMdJF8HqKxzj8wifkBct2EECLVlnpEHTg/ovmTUp2cwFcdcpTmq/tsCTOIeqXbRC5RBbtIJLmV4bSM2ZWBTo82zIEf8+f1HF/llg6seJ8eDrMqa7Qgf9Y28i46W+RNdP56NTmpMON6YYl4MDvETcBV1znHVlQ5xVxIP4VrrrydDiTvMOFBBy4e325lsDHlNGpP6AT+Xv/ZsocEolEok1+AFH1UukOqjanAAAAAElFTkSuQmCC>

[image11]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAbCAYAAACTHcTmAAAA90lEQVR4Xu2Tvw4BQRCHRyg0/lQkCqWGWutN1DpRegWR6PQegkahJNGRSEjUCqUHYH6ZO/YmZ/f2Qndf8jX7253bndslysgwqbB1ZTEyw5Mx+3Q4YkvhAh+uJAXiOJFkBR24wKK7HgzYkeQ1Hdiokixa6CAAH0Ne1oGNDsmioQ6YHEn20IGLKbtnG2q8zW7YOXnuEkdfsgd2xk4CtyS7Qz/z79kJwdHP7Io+BWGfbZIc3wRjTrA79KylAwXyLkmbnODoKJrkcuOloR1OfP5soqLhdTnq4AvWogjNtx06MCfFYC2alr8W1dcsNT32RtKmC7uOxhm/5gVH+juWt3DplwAAAABJRU5ErkJggg==>

[image12]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAbCAYAAACTHcTmAAABJ0lEQVR4Xu2Uu04CQRSGDxESGi8VJBQmNjb6QFbUVhLpfASICR2FhYnvoLaWQkwsNJKQSE1B6QPA+Tkz7MxhmdldLPdLvoTMPzPMmcsSlZS4HLNNZd3rkZM7dhnxlj20A/IwI5kgjQlJVtVBDAxa6EbDiCRv6CDECcmgJx0Y8GfIj3QQ4pJkUEcHTIUk+9NBjHv2g22p9gv2jR1SzlWi9Bf2ix2wfeM7yeqwnweb3hlB6VP2lZIJYZs9JSnf0jXZmdOWClaHPTvXgQMewiMlK35mf5N4G5SOSUOXGy8M24CqAA50151eU+RkH9i5brTY6/KtgwgoHXvrgXLsu3a9djulUGN7tOfHRoMJb8zv0MFmAtt0RfJAxsYfr0cB7Om7W/Xp9Sj5d1bcFEP6LMr2lwAAAABJRU5ErkJggg==>

[image13]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAFoAAAAaCAYAAAA38EtuAAACMUlEQVR4Xu2YvUtcQRTFTxAhCH6QoIIgJCA2CRJNYxDiB8EIKiGQkMaPVlCwEUSwNAgSEBQbOxFshHQp/AMCsdBCCxsF+zSCf4Dew30vO3vZ9T0NOrMyPzjs27nz4Ly7M3PvWyASiUQikUjksfBE1GzUJKp2JwUEfVm/z6DPETT1on7RmWhN1ILCA8yKTkXborr0Bo9UiRpF86Ir0TcUJ3xDdCmaQqCJH4Ya56dlABqbsQGPrEM9cVG4MLnfoYvjjYkFwS7UeK0NCN3QGOeEAhNJT6VYQHgL4x+HKG98AhrjtgwF+vlrB4Wnoi3o8fHZxIKAxo/toPBOdC6aRjhnXgPULxNqSc/uLhvIi62yWWLRyEsN1NxPM87EHokuEFYH8hrql4XahauZXk/MeDB8gBrfEa0kWhZ9dScldIj67OAD8wO6y1gQU7+Lol5nDhfaIPQ5Rp1xr7B4sLXrtAGHt9Djgysmb5F5j0IisvQquScLHhu/oLuvVOFOWRLNicaghbO1OPzwvIAWQq6OPGcwTedN9H3wBeXbUBfO4conbAF/Q1/CMtm/pdr0tkyGoBWanUUefCd6FZrEdhsw7InGk2vWrD/JpzfS/vm5DZTBd6Jv6p9LwSLOH+fOXcj/wtfYHmhRofFPyHeO+Uo0vX2EeqXonc+QxQj0aKw4fCX6LnAVv0yu2UHxP52KoVISzR2w6XxnZ3NTlxIMk6IDFLYu26s8W9cXqc9UbGEjkUgkUqFcA5nWdNlkYJh9AAAAAElFTkSuQmCC>

[image14]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACEAAAAaCAYAAAA5WTUBAAAA4UlEQVR4XmNgGAWjYBSMgiEEWoD4CBCzokvQEzADsS0QXwTiVDS5AQGMQLwMiJ8CsTiaHCkgiAHiqf84MAdCKW4gD8QvgbgfXYIIAPLIZwZMi2H4A0Ip8aAWiO8DsTEDxAJ8AOT43Wj800h8igAvEN8C4o3oEgSABwNEH8UAFhLaDIRDAh3sBeIV6IKkAFDCbAPiOUCsiiZHLHgNxD3ogoQALHeAfE5J7gABPgaII+zRJfABUMIDxXkhAyQNUAoMgPgcECugiWMFnUB8goH6JSaoLCDaMyDLQaXmKBgFowAGAGbnJ5m8dk0QAAAAAElFTkSuQmCC>

[image15]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAEsAAAAaCAYAAAD/nKG4AAACW0lEQVR4Xu2Xz0tVQRTHv2KuskCjxDBxFUIGuXHTQhHJoFq0CAQhSFq0EFy1aFuU0iZaGORaRBDalLuEBIMibOHCaCcRtGjZH2Dn65npnTvv3rnvufD2ZD7w5d3zvXN/zLkzZ+YBiUQikUgkEseC06LXoieiW6KfoleZFsVcFm2JHonei/ZF/ZkWwIbzv4g+i364uNM2ahWei36Z+KaLO4yXB5PyQdTu4m7RO2jSzjqP+GR5/RE9M+dbhhPQDswFPkfKC1Fb4Ftmode+zPH461kTTZq4ZemFdu5B4LOzHBFnAt8yLNpBNhFMMu9313iHTtYpaG2ww9Jqutb0SGAn+NywM4x/i0YDP4afvvy1+GQ9hk5bHpdN8QNWUZ8gq6Fa01x6mlRsGpFYsvL8PFirrkIL9zfUP5PJeiu6D11A2G490yKH29CVx8YDJq6CoqQU+TEuiT6K7iGbMCaS090zIPoqmjFeFN6MBZTTskqKklLkl3EHutrxtwjWQdZDjriGtg+sBawJVXMFmpQbgc8C/R3xssBpfi3H4/1831ibePz0XwtNEBP1Cdq+FBZ5foFm4aauGbGexDgH7Zxd6kkjqyFXQl573ng+Wb5vF13Mth7OpjfQKcvnl7IHfZn/AX75ZRP7Lz9mvEFop1eMt+s8W4evO2/RxdzHcVT5jSsZhz5zzHhReMOl0KwI7uD58r4os0BzZNjlfQL6zpw6ngXRNmrXdUFHzKbogm8ELeZTJuZ53j9cNQsZQTbbVcMXfwhNXF9wrgwW83noxjb8X+g5CW1D8TiRSCQSiUSUv/wJi4C3brriAAAAAElFTkSuQmCC>

[image16]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACEAAAAaCAYAAAA5WTUBAAAA7UlEQVR4XmNgGAWjYBQMI6ANxHPRBekFGIHYGIhvAXEhmhzNQSAQnwDiKCDmQJOjOQBZCLJ4PxB7ocnRHNQC8X0GSNCDooASEATEF4H4Pw6MEbLiQNwGxMsYIImPUgDywGcGTIth+ANCKSpQBeJHDBDHUALkgXg3Gv80Ep8gAGnoB+I5DBBHUQN4MEByFVmAlwGieSMDZeljLxCvQBckBXADcSoQ7wBiWzQ5YsFrIO5BFyQXMDNAsuwRdAk8gI8B4gh7dAlKAMghBuiCeABI7TkgVkATpysAlQWgtDV0QBkQnyQSH4XqGQWjgGYAACGZMCQkKxYOAAAAAElFTkSuQmCC>

[image17]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABYAAAAaCAYAAACzdqxAAAABRElEQVR4Xu2TLUuDYRSGz5iCDIM6NjG5ICaDGDUIw7bkYM1mERRExGAWi0VkLGibmjUtLgqCzKAgKPoLBIs/wN035zzbeSYD3yrvBRfvc87z/fGKpKSk/EO24RP8snJgwfI5l0vENZyE77Dt8jvwB4643J9ZheOinTnIsat7hJ8uTsSYfUuig3CiAOMHFyeGq72ARy7Hc+UODl0uMUV4B9dcriTxDrJwGY5anDEJLzmUI1jxChctZudT2BQ9qhW4B29g3dpwd3nRATuiC/kFO/Nl1Cw+gN9w1+INOA8/4DqcgC3pr/JKdJKhFOA0LIsew4yr48vhPfA+KqKTBKquHNGAZwMxL86fGycMO+D7vrcyJ5q1ckS4/UuLueUXuNRr0ecZnsNNeCu6mJOoxQBvcAvui/59c3F1D14qXxDhbqbsmzKcLlJuMNgAIyoyAAAAAElFTkSuQmCC>

[image18]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAZCAYAAAA4/K6pAAABAklEQVR4XmNgGAWjYLABGSCWA2JGdAliQDYQXwLid1A2DOhAxbmQxDCAKBBbQtn/gXgvktxCqBgM8DBA1KMADiitAMSvgdgeIQXmn0bibwXiyUh8FBDHAFEggCQGsh3kChi4zABRhwHEgPgoELsgiSkwYLoI5D1hJD4cGADxHSgNAyDDzjFADAIBkMtmATELTAEyAIXDEiAOhfJLgfgzEOfDVTAwhACxBRIfA6gB8XMGSKBtBuK7DKjOb2bA4XwQmArEE9H4oACEJSqQ4aAAVAXiApgiGAApAikGhQEMgFxyEIkPCo8HQJwIxIFI4nBwC4gzgLiYAWKQCqo0GLBC8XADAOA3KkGN2APmAAAAAElFTkSuQmCC>

[image19]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAYCAYAAAAs7gcTAAAA8klEQVR4Xu2SPwtBYRSHj2JisFA2FpNJGQxSJvIRbDIYfAGzfIBLFpEsdosyWRgMFoPVYpFF+QD8zvt669yTGx/AU0/d++vc9885l+jPdyJwB1uwC88w5Kt4E4Z9GBUZf1AQ74YEXMKiyjuwrTJqwhHZ1R38PIZlkRkWsKKyDDzAmMrNCnE4gE94h0dYkkUOPhevMCFbuIUnmJdFTBYmdQiG8KLDKvkv5vDIHskH9/ITc1LFabiWgeAGNzLgHvKtNTz2B6mBzOCUbE8dDbL/hBy7YQVz8Ep2AHuyW9dkkaOngyC4XXUdBsGD4IH8REoHQbwA2y8kK3/u8M0AAAAASUVORK5CYII=>