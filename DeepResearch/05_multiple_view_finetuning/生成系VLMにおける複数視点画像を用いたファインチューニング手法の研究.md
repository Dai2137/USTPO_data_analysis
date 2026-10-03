# **生成系Vision-Language Modelにおけるマルチビュー画像ファインチューニング技術の総合調査報告**

## **1\. 序論および概念的フレームワーク**

### **1.1 VLMアーキテクチャの進歩とマルチビュー入力の意義**

Vision-Language Model（VLM）およびLarge Multimodal Model（LMM）のアーキテクチャは、初期の2塔型対照学習モデル（CLIP等）や、凍結された言語モデルに対して単一画像特徴量を射影する構成から、自己回帰型（Causal / Decoder-based）の大規模言語モデル（LLM）を基幹骨格（Trunk）とし、視覚エンコーダをアダプタやプロジェクタを介して接続する生成型アーキテクチャへと急速に移行している1。この構造的変化に伴い、単一画像のキャプション生成や視覚問答（VQA）にとどまらず、複数視点（マルチビュー）画像群を同時に入力し、空間的な相互参照、3Dシーンの構造理解、クロスビューでの一貫性推論を行う高度な視覚言語タスクの実現が強く求められている3。  
マルチビュー画像群の導入は、従来の3D点群（Point Cloud）入力に伴う幾何学的制約やテクスチャ情報の欠落、専用の3Dエンコーダによるドメインギャップといった課題を克服する有効なアプローチである3。高精細な2D RGB画像群をそのまま入力として活用することで、大規模な2D事前学習によって得られた強力な視覚的表現力と一般化能力（2D Visual Priors）を維持したまま、高度な3D空間認識能力をモデルに付与することが可能となる3。

### **1.2 事前学習とファインチューニング段階の役割分担**

マルチビュー視覚情報の獲得において、事前学習（Pre-training）段階とファインチューニング（Instruction Tuning / Domain Adaptation）段階の役割分担は明確化されつつある。巨大な単一画像・テキスト対データセットで事前学習された汎用視覚言語基盤モデルに対し、事前学習の初期段階から大規模なマルチビューデータを投入することは、計算リソースやデータ収集コストの観点から容易ではない5。  
そのため近年の研究動向では、単一画像処理能力を備えた2D VLM基盤に対し、ファインチューニング段階（視覚指示チューニングやドメイン適応）においてマルチビュー画像群と位置情報・相互参照命令を与える手法が主流となっている4。大規模なマルチビュー事前学習を行わなくとも、多様なインターリーブ形式や3D位置埋め込み、適応的プロジェクタを導入した指示チューニングを実施することで、モデルはマルチビュー間の共参照、クロスビュー比較、3D境界ボックス出力といった創発的（Emergent）な空間推論能力を獲得することが実証されている4。

## **2\. マルチビュー画像統合のアーキテクチャ・パラダイム**

生成系（Causal LM）VLMのファインチューニング段階でマルチビュー画像群を入力として取り扱う手法は、視覚トークンの空間・系列表現への変換方式に基づき、大きく4つの主要パラダイムに分類される。

### **2.1 トークンインターリーブ・系列結合方式**

トークンインターリーブ方式は、複数の視界画像を時系列または視点順に並べ、テキストプロンプトのコンテキスト内に複数画像トークンを埋め込んでCausal Transformerに入力するアプローチである4。各画像は独立して2D Vision Encoder（CLIP ViT等）を通され、視覚プロジェクタによってLLMの埋め込み空間に射影される4。LLM内部のSelf-Attention機構が、異なる視点画像トークン間の相互関連性や時間・空間的対応関係を自動的に学習する仕組みとなっている4。この方式は3D専用のモジュール構造を追加することなく、汎用的なマルチ画像指示データを用いた指示チューニングのみで適用できる柔軟性を有している4。

### **2.2 3D位置エンコーディング・空間パッチ統合方式**

3D位置エンコーディング方式は、2Dの視覚トークンに対し、カメラの内部・外部パラメタや3D空間座標に基づいた位置埋め込み（3D Position Embedding）を明示的に付与する手法である5。マルチビュー画像から抽出された各2Dパッチトークンに対し、該当する視点の3D空間座標を符号化した3D位置エンコーディングを加算して「3D Patch Visual Tokens」を構築する7。その後、空間的な縮約（3D Pooling）を経てLLMに入力される7。2D VLMのパラメータ構造をほとんど変更せずに幾何学的な位置関係を直接トークンに注入できるため、従来モデルと比較して著しく高速な学習収束を実現する5。

### **2.3 クロスモーダル特徴量集約・幾何学的バウンディング方式**

クロスモーダル特徴量集約方式は、マルチビュー画像から特定領域や物体（Instance）の2D特徴量を抽出し、それらを3D空間上の幾何学的オブジェクトとして集約した上でLLMに入力するアプローチである5。2D視覚基盤モデルを用いて各視点画像からオブジェクト固有の特徴量を抽出し、Multi-view Cross-Modal Fusion（MCMF）等の融合モジュールを介して3D幾何特徴と結合する7。集約されたインスタンスレベルおよびシーンレベルのトークンがLLMの入力として提示されることで、オブジェクト指向の複雑な3Dシーン問答や3Dバウンディングボックス回帰において高い精度を発揮する5。

### **2.4 鳥瞰図（BEV）変換および3D再構成指示チューニング方式**

鳥瞰図変換方式および再構成指示チューニング方式は、自動運転やロボット操作など広域な環境認識が必要とされる領域で用いられる2。車載やロボットの複数カメラ映像から得られる視覚トークンをBird's Eye View（BEV: 鳥瞰図）空間表現に変換するか、あるいは単眼・多視点ビデオ列から直接3D形状を再構成するタスク（Reconstructive Instruction Tuning）をファインチューニング課題として与える2。外部の明示的な3Dセンサや点群データに依存せず、純粋な2Dマルチビュー画像列から高度な空間的推論と行動予測（Planning）を統合的に行うことが可能となる2。

## **3\. 主要モデルの比較解析およびケーススタディ**

生成系VLMにおけるマルチビューファインチューニングの代表的手法について、基幹VLM、統合メカニズム、学習戦略、および主要成果を比較した結果を以下の表に示す。

### **3.1 主要手法の統合比較**

| モデル名 | 基幹VLM / LLM | マルチビュー入力の統合メカニズム | ファインチューニング段階での学習戦略・データセット | 主な技術的特徴・成果 |
| :---- | :---- | :---- | :---- | :---- |
| **LLaVA-NeXT-Interleave** | LLaVA-NeXTベース / Causal LLM | トークンインターリーブ方式（マルチ画像・動画・3Dビューの一体統合）4 | M4-Instruct（117万件の複数画像・3D指示データ）によるSFT4 | 3D点群非依存でマルチビュー画像のみから屋内・屋外3Dシーン理解の最高性能を達成4 |
| **LLaVA-3D** | LLaVA（CLIP \+ Vicuna/Llama） | 2Dパッチへの3D位置埋め込み付与 ＋ 3D Pooling7 | 2D/3D視覚言語指示データを用いた共同指示チューニング（Joint Tuning）5 | 既存3D-LMM比で3.5倍高速収束。2D VQA性能を損なわずに3Dバウンディングボックスを直接デコード5 |
| **Inst3D-LMM** | Causal LLM \+ 2D VFM | Multi-view Cross-Modal Fusion (MCMF) による2D意味論と3D幾何特徴の融合13 | インスタンス・シーンレベルトークンに対する端対端マルチモーダル指示チューニング13 | オブジェクト間空間関係の精密把握とインファクトな3Dインスタンス理解13 |
| **Mantis / Med-Mantis** | Idefics2 / LLaVA-Medベース | マルチ画像コンテキスト結合プロジェクタ8 | Mantis-Instruct / Med-MIM（多視点・多画像医療VQAデータ）8 | 単一画像VLMに対し、事前学習なしの指示チューニングのみで他視点比較・時系列推論を獲得8 |
| **VLM-3R** | 汎用Causal VLM | 単眼マルチビュー/ビデオフレームの幾何再構成トークン結合14 | 3D再構成目標を組み込んだ指示チューニング（Reconstructive Tuning）14 | 実行時の3D再構成処理や深度センサなしに、カメラ移動と幾何構造を推論14 |
| **SpatialMosaic (フレームワーク)** | 汎用VLM (Qwen-VL等) | マルチビュー画像系列＋クロスビュー整合性プロンプト6 | SpatialMosaicデータセット（200万QAペア、屋内/屋外対応）6 | 屋内・屋外双方の複雑なマルチビュー空間整合性と問答能力の大幅な向上6 |

### **3.2 事例研究：LLaVA-NeXT-Interleave**

LLaVA-NeXT-Interleaveは、単一画像中心であった従来のオープンLMMの枠組みを拡張し、マルチ画像（Multi-image）、マルチフレーム（Video）、マルチビュー（3D）、マルチパッチ（Single-image high-res）の4つのシナリオを統一的に扱う指示チューニング・フレームワークである4。  
3D空間の理解にあたり、本モデルは点群エンコーダなどの外部モジュールを一切使用せず、マルチビューRGB画像群のみを入力として受け取る設計を採用している4。個々の視点画像から得られる視覚トークンは、テキストプロンプトと相互に挟み込まれる（Interleaved）形でCausal LLMに入力される4。ファインチューニング段階では、4つのプライマリドメインから14タスク・41データセットを集約した「M4-Instruct」（約117万7千サンプル）を用いて学習を行う4。  
この結果、点群データを直接入力とする従来の3D-LLMやPoint-LLMと比較して、屋内・屋外双方のシーン対話やタスク分解ベンチマークにおいて高いスコアを記録した15。さらに、複数視点画像間のオブジェクト照合やクロスモーダルなタスク転移といった創発的能力の獲得が確認されている4。

### **3.3 事例研究：LLaVA-3D**

LLaVA-3Dは、事前学習済みの2D LMM（LLaVA）に対し、最小限の構造変更で強力な3D空間認識能力を付与する効率的なファインチューニング手法である5。  
LLaVA-3Dにおける情報処理パイプラインは、まず入力されたマルチビューRGB画像群を固定または微調整される2D Vision Transformer（ViT）に入力し、各視点の2Dパッチ特徴量を抽出することから始まる7。続いて、各パッチの3D空間座標に対応する3D位置エンコーディングが2Dパッチトークンに直接加算され、空間幾何情報を包含した3Dパッチトークンが形成される7。このトークン群は3D Poolingによる空間的縮約を経た後、視覚プロジェクタを介してLLMの埋め込み空間へと射影される7。最終的に、ユーザーからのテキスト指示プロンプトとともにCausal LLMデコーダ（VicunaやLlama等）へ供給され、自然言語による応答や3Dバウンディングボックス座標が自己回帰的にデコードされる5。  
ファインチューニングにあたっては、高速かつ安定した学習を実現するため、3D視覚言語指示データセットと2D視覚言語指示データセットを混合した「共同指示チューニング（Joint 2D & 3D Instruction Tuning）」が適用される5。オフスキャン3Dセグメンタや点群エンコーダを必要とする従来の3D LMMと比較して、トレーニングの収束速度が3.5倍加速し、高精度な3Dバウンディングボックスの直接デコード能力を獲得しながら元のLLaVAが持つ優れた2D VQAや会話能力を維持することに成功している5。

### **3.4 事例研究：Inst3D-LMMおよびSpatialMosaic**

3Dシーン理解において、空間全体の大まかな把握だけでなく、個々の物体（インスタンス）とその相互関係を正確に認識するため、マルチビュー融合モジュールや大規模専用データセットを用いた指示チューニング手法が提案されている。  
Inst3D-LMMは、3D空間内のインスタンスレベル視覚表現を精緻化するため、Multi-view Cross-Modal Fusion（MCMF）モジュールを導入している13。2D VFMから抽出されたマルチビューの文脈特徴量を3D幾何特徴に注入し、さらに空間的条件付きSelf-Attentionを介してオブジェクト間のペアワイズな3D関係性をキャプチャする13。これらのトークンをLLMに入力し、端対端のマルチタスク指示チューニングを行うことで、密な3Dキャプション生成や空間問答の精度を大幅に向上させている13。  
SpatialMosaicは、マルチビュー画像入力時における「視点間の整合性（Cross-View Consistency）」の欠如に対処するための指示チューニング手法およびデータセットである6。屋内および屋外の広範なレイアウトを網羅する200万件のマルチビュー問答ペアで構成され、クロスビューでの幾何的推論をCausal VLMに直接学習させることで、従来モデルの課題であった視点切り替え時のハルシネーション（幻覚）を低減させている6。

### **3.5 事例研究：Mantisおよび領域特化型展開**

マルチビューファインチューニングの手法は、汎用的な3Dシーン理解にとどまらず、特定ドメインの高度なタスクへ応用されている。  
Mantisは、大規模なマルチ画像事前学習を行わずとも、指示チューニング（Mantis-Instruct）のみで複数画像間の比較・推理・共参照能力を獲得できることを証明した8。この手法を医療画像領域に応用したMed-MantisおよびMIM-LLaVA-Medでは、マルチビューのCT/MRIスライス画像や経時的なX線画像群を指示チューニング段階で入力し、疾患の立体的な進展や複数画像にまたがる病変の比較診断において成果を上げている16。  
自動運転分野のBEV-InMLLMでは、車載のマルチビューカメラ映像（前後左右）をコンテキストとして受け取り、LLM内部でBEV特徴と統合して周囲車両の行動予測や危険認知を行う指示チューニングを実施している2。また、ロボティクス・産業作業支援の分野では、Compositional Context Fine-Tuning（CCFT）を用い、作業者のマルチビュー映像から「動詞・対象物・工具」の要素に分解した視覚問答ペアを構築し、Qwen2.5-VL等の生成系VLMをLoRA（Low-Rank Adaptation）によって層分割交互学習（LP-AT）させることで、決定論的で解釈可能な作業認識を実現している17。

## **4\. ファインチューニング最適化手法と計算効率**

マルチビュー画像を生成系VLMに入力する際、最大の問題となるのは視覚トークン量の爆発に伴う計算コストとメモリ消費（KVキャッシュの急増）、および単一画像認識能力の劣化（破滅的忘却）である5。これらを抑えつつモデルを最適化するため、いくつかのファインチューニング戦略が確立されている。

### **4.1 パラメータ効率的ファインチューニング（PEFT）とモジュール選択**

VLMのファインチューニングにおいては、モデル全体のパラメータを全更新するのではなく、特定のモジュールのみを凍結・解除、あるいはパラメータ効率的ファインチューニング（PEFT）技術を適用する設計が一般的である17。  
具現化AI（Embodied AI）や多視点空間認識タスクに関する実験分析（例: VLM4VLA）によると、LLM単体のファインチューニングよりも、Vision Encoder（視覚エンコーダ）の凍結を解除して適応学習させることが空間推論能力の向上に極めてクリティカルであることが示されている18。視覚エンコーダの表現空間を制御関連・空間関連の教師信号に適合させることがパフォーマンス向上に寄与する18。また、Qwen2.5-VL等の軽量～中規模モデルの適応においては、特定のトランスフォーマー層に低ランクアダプタ（LoRA）を挿入し、視覚要素ごとに異なる層群を交互に訓練する層分割交互学習（Layer-Partitioned Alternating Training）などが用いられ、少量の学習データでも高い一般化性能を達成している17。

### **4.2 2D機能保持のための共同指示チューニング**

マルチビューや3D空間認識のデータセットのみでファインチューニングを行うと、基底モデルが持っていた優れた2D視覚理解能力や一般会話能力が損なわれるリスクがある5。この対策として、2D視覚言語データセットと3D/マルチビュー視覚言語データセットを一定比率で混合して学習させる「Joint Instruction Tuning」が適用される5。LLaVA-3Dでは、この共同指示チューニングを採用することで、2Dタスクのベンチマーク性能を完全に維持しながら3Dタスクの能力向上を実現している5。

### **4.3 トークン削減と計算コスト制御**

複数画像を入力すると、トークン数が画像数に比例して線形に増加し、LLMのコンテキスト長を圧迫する。これを回避するため、3D Pooling（LLaVA-3D）などの空間的縮約処理を用いて近接パッチや同一オブジェクト由来の視覚トークンを平均化・圧縮してLLMに引き渡す手法や、質問プロンプトに関連する重要な視界・領域のみを動的に選択してトークン化するダイナミック・クロッピング（Dynamic Cropping）が活用されている7。

## **5\. 応用分野と実践的インプリケーション**

生成系VLMに対するマルチビューファインチューニング技術の確立は、以下に示す先進的領域において直接的なイノベーションをもたらしている。

> 1. **3D空間認識およびシーン理解**: 点群スキャナなどの高価な3Dセンサに依存せず、スマートフォンの多角撮影や標準的なマルチカメラ画像から、部屋全体の立体構造、家具のバウンディングボックス位置、物体間の詳細な空間関係を自然言語で対話・出力することが可能となった3。  
> 2. **具現化AI・ロボティクス**: 自律走行ロボットやアームロボットが、複数カメラ（エゴセントリック視点・俯瞰視点）の映像を統合して状況を把握し、指定されたオブジェクトを操作するための高レベル命令から、カメラ間の視差を考慮した精緻な行動計画を直接導出できるようになった2。  
> 3. **高度医療診断**: CT/MRIのマルチスライス画像や、複数角度から撮影されたレントゲン写真を一括して生成系VLMに入力・ファインチューニング（Med-Mantis等）することで、単一画像では発見が困難な立体的な病変の深さや組織の経時的変化の比較診断支援が実現している16。  
> 4. **産業アセンブリ・作業支援**: 工場や作業現場での人間のマルチビュー動作映像から、「使用中の工具」「対象部材」「作業動作」を精度高く認識・分解し、リアルタイムで作業手順のチェックや安全確認を行うシステムへ応用されている17。

## **6\. 技術的課題と将来の展望**

マルチビューファインチューニングを適用した生成系VLMの研究は飛躍的に進展しているものの、実用化および大規模展開に向けてはいくつかの課題が残されている。

### **6.1 残された技術的課題**

視点数が増大した際、Causal TransformerのAttention計算量およびKVキャッシュメモリが膨大になり、長時間のマルチビュービデオ流や超高解像度画像の取り扱いにはインフラ上の制約が存在する4。また、純粋な言語モデルのSelf-Attentionに頼るインターリーブ方式では、カメラの物理的な線形代数幾何（エピポーラ幾何等）を完全には捕捉できない場合があり、視界の遮蔽（Occlusion）や照明変化が起きた際に虚偽の空間関係を出力するハルシネーションの抑制が課題となっている6。さらに、高精度な3Dバウンディングボックスやマルチビュー間の対応関係アノテーションが付与された指示チューニングデータ（M4-Instruct, SpatialMosaic等）の構築には膨大なコストがかかるため、データのスケールアップがボトルネックとなっている4。

### **6.2 将来の展望**

今後は、幾何学的知覚（Geometric Perception）と生成型言語推論（Generative Reasoning）のより密接な融合が進むと予想される。特に、明示的な3D位置埋め込み（LLaVA-3D等）と、ビデオMLLMで培われた時間軸統合モジュールとの融合により、「時空間マルチビュー（Spatio-Temporal Multi-View）」をシームレスに処理する基盤モデルが登場する可能性が高い5。  
さらに、視覚エンコーダ自体を対照学習由来の静的表現から、生成型言語モデルと同一の目標で共同事前学習・ファインチューニングされた動的エンコーダ（例: Penguin-Encoder等）へと置き換えることで、視覚表現抽出の段階からマルチビュー幾何特性を自然に保持する次世代のCausal VLMアーキテクチャの台頭が期待されている20。

## **7\. 結論**

本調査報告では、デコーダ型（Causal LM）Vision-Language Modelにおけるマルチビュー画像群を用いたファインチューニング技術について、その理論的背景、アーキテクチャ分類、主要なモデル事例、および最適化手法を総合的に分析した。  
事前学習済みの強力な2D VLM基盤に対し、ファインチューニング段階でトークンインターリーブ、3D位置埋め込み、クロスモーダル特徴融合、BEV・再構成タスクといった構造的工夫や指示データを導入することにより、重い点群エンコーダや膨大なマルチビュー事前学習を行わなくとも、高精度な3D空間推論能力やクロスビュー整合性を付与できることが実証されている4。  
視覚エンコーダの選択的適応（PEFT/LoRA）や、2D/3Dの共同指示チューニングによる機能保持、トークン縮約技術の進展に伴い、マルチビュー入力対応の生成系VLMは、具現化AI、自動運転、医療診断、産業支援をはじめとする多様な実世界アプリケーションにおける基盤技術として確立されつつある2。

#### **引用文献**

> 1. Benchmark and Evaluations, RL Alignment, Applications, and Challenges of Large Vision Language Models \- GitHub, [https://github.com/zli12321/Vision-Language-Models-Overview](https://github.com/zli12321/Vision-Language-Models-Overview)  
> 2. Visual Large Language Models for Generalized and Specialized Applications \- arXiv, [https://arxiv.org/html/2501.02765v1](https://arxiv.org/html/2501.02765v1)  
> 3. 3D Aware Region Prompted Vision Language Model \- arXiv, [https://arxiv.org/html/2509.13317v1](https://arxiv.org/html/2509.13317v1)  
> 4. \[2407.07895\] LLaVA-NeXT-Interleave: Tackling Multi-image, Video, and 3D in Large Multimodal Models \- arXiv, [https://arxiv.org/abs/2407.07895](https://arxiv.org/abs/2407.07895)  
> 5. LLaVA-3D: A Simple yet Effective Pathway to Empowering LMMs with 3D Capabilities \- CVF Open Access, [https://openaccess.thecvf.com/content/ICCV2025/papers/Zhu\_LLaVA-3D\_A\_Simple\_yet\_Effective\_Pathway\_to\_Empowering\_LMMs\_with\_ICCV\_2025\_paper.pdf](https://openaccess.thecvf.com/content/ICCV2025/papers/Zhu_LLaVA-3D_A_Simple_yet_Effective_Pathway_to_Empowering_LMMs_with_ICCV_2025_paper.pdf)  
> 6. SpatialMosaic: A Multi-View VLM Dataset for Partial Visibility \- arXiv, [https://arxiv.org/html/2512.23365v2](https://arxiv.org/html/2512.23365v2)  
> 7. LLaVA-3D: A Simple yet Effective Pathway to Empowering LMMs with 3D Capabilities, [https://arxiv.org/html/2409.18125v3](https://arxiv.org/html/2409.18125v3)  
> 8. Mantis: Interleaved Multi-Image Instruction Tuning \- arXiv, [https://arxiv.org/html/2405.01483v3](https://arxiv.org/html/2405.01483v3)  
> 9. Mantis: Interleaved Multi-Image Instruction Tuning \- arXiv, [https://arxiv.org/html/2405.01483v2](https://arxiv.org/html/2405.01483v2)  
> 10. LLaVA-NeXT-Interleave: Tackling Multi-image, Video, and 3D in Large Multimodal Models, [https://www.researchgate.net/publication/382145591\_LLaVA-NeXT-Interleave\_Tackling\_Multi-image\_Video\_and\_3D\_in\_Large\_Multimodal\_Models](https://www.researchgate.net/publication/382145591_LLaVA-NeXT-Interleave_Tackling_Multi-image_Video_and_3D_in_Large_Multimodal_Models)  
> 11. LLaVA-OneVision: Easy Visual Task Transfer \- arXiv, [https://arxiv.org/html/2408.03326v1](https://arxiv.org/html/2408.03326v1)  
> 12. LLaVA-3D: A Simple yet Effective Pathway to Empowering LMMs with 3D-awareness \- arXiv, [https://arxiv.org/html/2409.18125v1](https://arxiv.org/html/2409.18125v1)  
> 13. Inst3D-LMM: Instance-Aware 3D Scene Understanding with Multi-modal Instruction Tuning \- CVF Open Access, [http://openaccess.thecvf.com/content/CVPR2025/papers/Yu\_Inst3D-LMM\_Instance-Aware\_3D\_Scene\_Understanding\_with\_Multi-modal\_Instruction\_Tuning\_CVPR\_2025\_paper.pdf](http://openaccess.thecvf.com/content/CVPR2025/papers/Yu_Inst3D-LMM_Instance-Aware_3D_Scene_Understanding_with_Multi-modal_Instruction_Tuning_CVPR_2025_paper.pdf)  
> 14. VLM-3R: Vision-Language Models Augmented with Instruction-Aligned 3D Reconstruction, [https://arxiv.org/html/2505.20279v3](https://arxiv.org/html/2505.20279v3)  
> 15. Tackling Multi-image, Video, and 3D in Large Multimodal Models \- LLaVA-NeXT, [https://llava-vl.github.io/blog/2024-06-16-llava-next-interleave/](https://llava-vl.github.io/blog/2024-06-16-llava-next-interleave/)  
> 16. Medical Large Vision Language Models with Multi-Image Visual Ability \- arXiv, [https://arxiv.org/html/2505.19031v1](https://arxiv.org/html/2505.19031v1)  
> 17. Compositional Context Fine-Tuning Vision-Language Model for Complex Assembly Action Understanding from Videos \- arXiv, [https://arxiv.org/html/2607.10797v1](https://arxiv.org/html/2607.10797v1)  
> 18. VLM4VLA: Revisiting Vision-Language-Models in Vision-Language-Action Models \- arXiv, [https://arxiv.org/html/2601.03309v2](https://arxiv.org/html/2601.03309v2)  
> 19. PointCLIP: Point Cloud Understanding by CLIP | Request PDF \- ResearchGate, [https://www.researchgate.net/publication/363910072\_PointCLIP\_Point\_Cloud\_Understanding\_by\_CLIP](https://www.researchgate.net/publication/363910072_PointCLIP_Point_Cloud_Understanding_by_CLIP)  
> 20. Penguin-VL: Exploring the Efficiency Limits of VLM with LLM-based Vision Encoders \- arXiv, [https://arxiv.org/html/2603.06569v2](https://arxiv.org/html/2603.06569v2)