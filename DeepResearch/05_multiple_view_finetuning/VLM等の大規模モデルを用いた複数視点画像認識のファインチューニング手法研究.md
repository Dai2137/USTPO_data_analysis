# **複数視点画像におけるVision-Language Modelの適応とファインチューニング技術に関する研究動向報告書**

大規模Vision-Language Model（VLM）や基礎視覚モデル（Vision Foundation Models）の飛躍的発展に伴い、単一画像にとどまらず、同一対象物やシーンを複数視点から撮影したマルチビュー（Multi-View）画像群を入力として高精度な画像認識・3D形状認識を行う研究が急速に発展している1。複数の視点画像から整合性のある大域的表現を抽出する課題に対して、事前学習済みモデルが持つ強力な2D視覚・言語表現空間を活用しつつ、パラメータ効率的ファインチューニング（PEFT: Parameter-Efficient Fine-Tuning）や高度な視点統合機構を適用する手法が注目を集めている1。  
本報告書では、複数視点画像を用いた画像認識・分類タスクにおいて、VLM等の大規模モデルを適用・微調整する主要な代表的研究を包括的に分析する。特に、ファインチューニング手法（プロンプトチューニング、アダプター、選択的レイヤーチューニング等）およびマルチビュー統合メカニズムに焦点を当て、高被引用数を誇る金字塔的研究から主要国際会議（CVPR, ICCV, ICLR, NeurIPS）で発表された最新の代表的手法までを比較・考察する。

## **複数視点視覚認識における大規模モデル適応の基本構造**

数十億規模の画像・テキスト対で対照学習されたCLIPなどの事前学習済みVLMは、未知のカテゴリに対しても優れたゼロショット転移能力を発揮する2。しかし、複数視点から得られる視覚情報を統合して単一のカテゴリや形状として認識する場合、各視点画像を個別にエンコードして単純な平均（Mean Pooling）をとるのみでは、視点間の幾何学的相関や局所的・大域的な空間依存関係を十分に捉えきれない限界が存在する1。  
一方で、大規模モデルのバックボーン全体をエンドツーエンドでフルファインチューニング（Full Fine-Tuning）するアプローチは、膨大な計算リソースとGPUメモリを消費するだけでなく、事前学習によって獲得された汎用的な視覚・言語対照空間を破壊し、特定のデータセットへ過剰適合（Overfitting）を引き起こすリスクが高い1。  
この課題を克服するため、近年の研究体系は「パラメータ効率的ファインチューニング（PEFT）」と「構造的マルチビュー統合機構」の融合を中心に標準化が進んでいる2。事前学習済みバックボーンのパラメータの大半をフリーズ（固定）した上で、軽量なプロンプト（Prompt Tokens）、挿入型アダプター（Adapter Networks）、あるいはアテンション層などの特定モジュールのみを解凍・追加学習させる設計が主流となっている2。

## **視点統合（Multi-View Integration）の技術的アプローチ**

複数視点の画像群を単一の識別的ベクトル表現へと集約するメカニズムは、モデルの表現力、計算効率、および視点順序不変性（Permutation Invariance）の保持において核心的な役割を果たす1。既存研究における代表的な視点統合アプローチは、構造的特性と情報伝播の形式に応じて明確に体系化される1。  
最も単純な統合手法である要素別平均または最大化（Mean / Max Pooling）は、各視点画像の埋め込みベクトルを個別抽出した後に要素ごとの統計量を算出する1。この手法は追加パラメータを一切必要とせず、任意の視点数や撮影順序に対して完全な順序不変性を保持する利点を持つ2。しかしながら、視点間の局所的な幾何的対応や遮蔽（Occlusion）関係を動的に考慮することができないため、緻密な幾何構造や属性の識別において限界が生じる1。  
これに対し、残差型インタービュー・アダプター（Inter-View Adapter）は、全視点の特徴量を連結（Concatenate）してボトルネック構造の線形層に入力し、大域的なコンテキスト表現を抽出した上で、各視点の特徴量へ残差接続で書き戻すアーキテクチャを採用する3。この設計により、視点ごとの固有情報と全視点の大域情報の双方が保持され、少人数（Few-shot）学習下においても効率的な適応が可能となる3。  
さらに柔軟な幾何的相互作用を実現する手法として、クロスビュー・アテンション（Cross-View Attention）が挙げられる2。Vision Transformer（ViT）のアテンション層を多視点画像トークン空間へ拡張し、視点を跨いだパッチ間・フレーム間の関連性を直接計算する2。これにより、モデルは物体の姿勢（Pose）情報に依存することなく、視点間の補完的な特徴を適応的に抽出することが可能となり、入力視点数が変動するリアルタイム環境にも対応する2。  
また、近年の研究では階層的チャンク集約（Hierarchical Chunk Aggregation）も提案されている1。近接する視点群を小規模な「チャンク」として段階的に集約し、局所的な視点間パターンを捉えた後に、広域的な視点間関係を上位レイヤーで集約する1。この二段階アプローチにより、過度な計算負荷を回避しつつ、局所詳細と全体構造の双方を高精度に表現できる1。

## **パラメータ効率的ファインチューニング（PEFT）の適用手法**

VLMなどの基礎モデルを複数視点認識タスクへと適応させる際、バックボーンに対する介入位置と学習対象パラメータの選定が性能と汎化性のトレードオフを決定づける3。  
テキストエンコーダーの入力側を対象とするプロンプトチューニング（Prompt Tuning）では、手動設計された固定テキストプロンプトを学習可能な連続ベクトル（Learnable Prompt Tokens）に置き換え、勾配降下法によってタスク最適化を図る3。さらに近年の高度な展開として、大規模言語モデル（LLM）を用いて対象オブジェクトの形状・質感・視点依存の属性記述を生成し、これを動的にテキストプロンプトへ注入する手法が定着している12。視覚エンコーダー側へプロンプトを挿入するVisual Prompt Tuning（VPT）も併用され、画像トークン系列にタスク専用トークンを直接埋め込むアプローチが用いられる8。  
バックボーンの内部あるいは出力層付近に配置される特徴アダプター（Feature Adapters）は、事前学習済み特徴量を非線形変換する軽量なボトルネック回路（通常は2層のMLP）で構成される3。元の特徴量 ![][image1] とアダプター出力の差分をスケール因子 ![][image2] を介して融合する残差構成が標準的であり、事前学習によって得られた広大な概念空間を揺るがすことなく、特定の多視点視覚ドメインへの滑らかな適応を実現する3。  
また、モジュールを新設する代わりに、アテンション投射行列（Query, Key, Value）やトランスフォーマーブロックの最終 ![][image3] レイヤーなどの特定パラメータを選択的に解凍して更新する選択的レイヤーチューニング（Selective Layer Tuning）も極めて有効な選択肢である2。モデル構造に無駄な遅延を発生させることなく、複数視点間の空間相互作用を直接学習させるアプローチとして評価されている2。

## **代表的研究の比較分析**

複数視点画像およびVLMを用いた画像認識・分類分野において、学術的発展に寄与した基幹研究から、最新のトップカンファレンス採録論文までの比較を以下の表に示す。

| 研究名・モデル | 発表年・主要会議 | ベースモデル | ファインチューニング手法 (PEFT) | マルチビュー統合手法 | 被引用数・主要成果および技術的特徴 |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **PointCLIP** | 2022 (CVPR) | CLIP (ViT / ResNet) | **Inter-View Adapter**（ボトルネック残差MLP） | 視点特徴の連結＋大域残差融合 | **600回超**19。3D点群をマルチビュー深度マップに投影し2D-VLMへ適応。少人数タスクで高い転移性能を実証3。 |
| **PointCLIP V2** | 2023 (ICCV) | CLIP \+ GPT-3/4 | **LLM-assisted Prompting**（幾何属性プロンプト） | リアル投影＋属性別プロンプト集約 | **200回超**19。LLMを用いて多角的なテキスト記述を生成し、プロンプトチューニングなしで高精度なオープンワールド学習を実現14。 |
| **ULIP / ULIP-2** | 2023/2024 (CVPR) | CLIP / SLIP | ポイントクラウド/視覚エンコーダーの対照学習 | 画像・言語・点群のトライモーダル整列 | **高被引用**17。画像・テキスト・3D構造を共通潜有空間に整列させる多模態事前学習基盤モデルを確立2。 |
| **Duoduo CLIP** | 2025 (ICLR) | CLIP (OpenCLIP) | **選択的レイヤーチューニング**（Attention層/最終6層） | **Cross-View Attention** ＋ 平均集約 | ICLR 2025採録24。点群を用いずマルチビュー画像のみで3D形状を認識。計算コストを従来比1/8以下に削減2。 |
| **DINO Eats CLIP (DEC)** | 2024/2026 (arXiv) | DINO \+ CLIP | **Multi-View Chunk Adapter** \+ 仮想特徴合成 (VFS) | 局所チャンク集約＋広域交差融合 | DINOの局所視覚表現力とCLIPの言語空間を融合。未知クラスへの過剰適合を防ぐVFS正則化を提案1。 |
| **LAMP** | 2025 (ICCV) | CLIP \+ LLM | **Action-aware Multi-modal Prompt Tuning** | 適応的相互作用モジュール (Adaptive Interaction) | ICCV 2025採録13。LLMから行動・状態の概念を抽出してプロンプト化。複合属性および動的関係の細粒度アライメントを実現12。 |

## **主要手法の詳細メカニズムとアーキテクチャ**

### **PointCLIPとPointCLIP V2**

PointCLIPは、2D写真画像で事前学習されたCLIPを3D点群の理解へと適用した先駆的研究である3。3D点群をレンダリング処理を経ずに複数の直交視点から見た2D深度マップ（Depth Maps）へ投影し、これをマルチビュー画像としてCLIPの画像エンコーダーに入力する3。  
ゼロショット認識では視点ごとの予測ロジットを単純平均するが、少人数（Few-shot）ファインチューニング設定ではInter-View Adapterを導入する3。全視点の特徴量 ![][image4] を連結し、2層のボトルネック線形層を通過させて全視点の大域的特徴ベクトル ![][image5] を算出する3。各視点特徴に対して大域情報を残差結合で加算することにより、各視点表現へ全視点相互作用がエンコードされる3。画像およびテキストエンコーダーの大部分をフリーズさせたままアダプターのみを学習させることで、過剰適合を防止しつつ優れた転移精度を実現した3。  
PointCLIP V2は、PointCLIPにおける「投影深度マップの幾何的ギャップ」と「手動プロンプトの記述力不足」という課題を克服した発展型である14。点群からより緻密でリアルな外観を模した視覚投影を行う Realistic Shape Projection を導入した14。さらに、GPT-3やGPT-4などの大規模言語モデルを活用し、各3Dオブジェクトの構造・パーツ・機能に関する膨大なテキストプロンプト群を自動生成させた14。生成されたプロンプト群をCLIPテキストエンコーダーでアンサンブル処理することで、学習不要のゼロショット設定および小規模データ適応下でオープンワールド認識の精度を大きく更新した14。

### **Duoduo CLIP**

ICLR 2025に採録されたDuoduo CLIPは、従来主流であった点群処理バックボーン（Point Cloud Encoders）を全廃し、純粋な「マルチビュー画像表現」のみで3D形状理解を行うアプローチである2。  
モデル内部のVision Transformerにおいて、アテンションの計算範囲を複数視点（フレーム）を跨ぐ空間へ拡張した Cross-View Attention を設計した2。これにより、入力画像群の撮影順序に影響されない順序不変性と、物体の絶対姿勢を必要としない姿態フリー（Pose-free）特性を同時に達成している2。  
ファインチューニングの戦略として、事前学習済みCLIPモデルのバックボーン全体を更新するのではなく、アテンション層の重み、または最終ブロックの特定レイヤー（例: 最終6層）を選択的に学習させる手法を採る2。この構成により、10億パラメータ規模の点群モデル（Uni3D等）が480 A100 GPU時間を要して学習していたタスクに対し、Duoduo CLIPは僅か8700万パラメータ・57 A5000 GPU時間で同等以上の識別・検索汎化性能を達成した2。

### **DINO Eats CLIP (DEC)**

DINO Eats CLIP (DEC) は、自己教示学習モデルであるDINOの局所視覚表現力と、CLIPの言語整列表現力を融合させたマルチビュー検索・分類手法である1。  
DINOの画像エンコーダーから得られる各視点特徴に対し、視点群を小グループに分解して局所パターンを段階的に集約する Multi-View Chunk Adapter を適用する1。また、ファインチューニング中に既知クラスへ過剰適合する問題を軽減するため、DINOの視覚空間、CLIPの視覚空間、およびテキスト空間を線形補間・結合して未知クラスの「仮想視覚特徴（Virtual Visual Features）」を合成する Virtual Feature Synthesis (VFS) モジュールを提示した1。  
DINOのベースエンコーダーをフリーズしたままアダプターとVFSモジュールをファインチューニングすることにより、既知カテゴリでの識別性能を高めつつ、未知カテゴリ（Open-set）に対する高い検索・分類汎化性能を両立している1。

### **LLM-enhanced Action-aware Multi-modal Prompt Tuning (LAMP)**

ICCV 2025に採録されたLAMPは、マルチビュー画像や高次元視覚データにおける「行動（Action）」や「オブジェクト間相互作用」などの細粒度（Fine-Grained）な概念を正確に識別するためのプロンプトチューニング手法である12。  
従来のプロンプトが単一の物体カテゴリ名に依存していたのに対し、LLMを用いて「主語-動詞-目的語」で構成される行動トリプレットプロンプト（Action Triplet Prompt）と、変化状態を示す行動状態プロンプト（Action State Prompt）を自動生成する12。視覚側には Adaptive Interaction Module を挿入し、これらの言語的プロンプト情報を条件として各視点画像の特徴を適応的に融合・ファインチューニングする12。複雑な属性や動的関係を含むマルチビュー認識において、詳細なレベルでの視覚・言語アライメントを実現した12。

## **技術的動向の考察と将来展望**

複数視点画像に対するVLMの適用と微調整技術の発展を紐解くと、ドメイン適応と計算効率を同時に達成するための構造的メカニズムが浮かび上がる1。  
第一に、2D視覚事前分布の保持とドメインギャップ縮小の連動性である。3D認識分野において、点群データを直接エンコードする手法は離散的かつ不均一な空間を扱うため、2D自然画像で大規模学習されたCLIPの初期重みを十分に活用しきれない課題があった2。これに対し、Duoduo CLIPやPointCLIPのように「複数枚の2D画像」として入力を処理する手法は、ViTが本来持つ空間的アテンションフィルタや強力な2D視覚事前分布を100%保持できる2。  
![][image6]  
この数式で表されるように、ベースとなる視覚エンコーダーをフリーズさせたまま、数パーセントのパラメータ（アテンション層や軽量アダプター）のみを微調整するアプローチが、最も高い汎化精度と計算効率をもたらす2。  
第二に、視点間相関モデリングによる表現崩壊の防止機構である。フリーズ状態のVLMによる単純平均ポーリングは強力なゼロショットベースラインを提供するが、この状態で下流タスクの損失関数を用いて全層ファインチューニングを行うと、特定の視点や特定の視覚特徴に過剰に依存するショートカット学習が発生しやすい1。これを防ぐため、Cross-View Attentionによるトークン間の相互参照や、VFSモジュールによる仮想特徴を用いた正則化など、視点間の幾何的依存関係を維持しながら特徴空間を更新する設計が必須となっている1。  
第三に、LLMを外部知識生成器とするマルチモーダルプロンプト空間の拡張である。単一のテキスト名から埋め込みを得る従来のCoOp型アプローチから、LLMを活用してオブジェクトの多角的な視点属性や空間的関係を記述する高度なプロンプト構築へと進化している4。これにより、視点遮蔽や視角変化が存在する困難なマルチビュー画像群に対しても、言語側からの強力な事前誘導が作用し、より堅牢な分類が可能となっている12。

## **結論**

複数視点画像を用いた大規模モデル（VLM等）の画像認識・分類技術は、単一画像の単純な集約から、パラメータ効率的ファインチューニング（PEFT）と高度な視点間相互作用モジュールを融合させた高度な設計へと進化を遂げた1。  
ファインチューニング手法においては、モデル全体の再学習を避け、Inter-View Adapter、アテンション層の選択的チューニング、およびLLM連携プロンプトチューニングを用いるアプローチが主流となっている2。マルチビュー統合手法においても、単純な平均処理を超えて、フレーム間トークン結合を動的に計算する Cross-View Attention や階層的チャンク集約が導入され、高い識別能力と汎化性能が実証されている1。  
今後は、ロボティクスやリアルタイム3Dシーン理解における極小視点（Sparse Views）からの即時適応や、動的な時間軸を含むマルチビュー・動画理解への拡張が重要な研究課題となると展望される2。

#### **引用文献**

> 1. DINO Eats CLIP: Adapting Beyond Knowns for Open-set 3D Object Retrieval \- arXiv, [https://arxiv.org/html/2604.19432v1](https://arxiv.org/html/2604.19432v1)  
> 2. DUODUO CLIP: EFFICIENT 3D UNDERSTANDING WITH MULTI-VIEW IMAGES \- ICLR Proceedings, [https://proceedings.iclr.cc/paper\_files/paper/2025/file/77d8a1387c3dbceab2a90c9af0e8d830-Paper-Conference.pdf](https://proceedings.iclr.cc/paper_files/paper/2025/file/77d8a1387c3dbceab2a90c9af0e8d830-Paper-Conference.pdf)  
> 3. PointCLIP: Point Cloud Understanding by CLIP \- CVF Open Access, [https://openaccess.thecvf.com/content/CVPR2022/papers/Zhang\_PointCLIP\_Point\_Cloud\_Understanding\_by\_CLIP\_CVPR\_2022\_paper.pdf](https://openaccess.thecvf.com/content/CVPR2022/papers/Zhang_PointCLIP_Point_Cloud_Understanding_by_CLIP_CVPR_2022_paper.pdf)  
> 4. PLPP: Prompt Learning with Perplexity Is Self-Distillation for Vision-Language Models, [https://arxiv.org/html/2412.15277v1](https://arxiv.org/html/2412.15277v1)  
> 5. Efficient and Long-Tailed Generalization for Pre-trained Vision-Language Model \- arXiv, [https://arxiv.org/html/2406.12638v1](https://arxiv.org/html/2406.12638v1)  
> 6. OpenDlign: Open-World Point Cloud Understanding with Depth-Aligned Images \- NIPS, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/b739cbaa0e94bfd7669d9573e9235411-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/b739cbaa0e94bfd7669d9573e9235411-Paper-Conference.pdf)  
> 7. Multi-view Masked Contrastive Representation Learning for Endoscopic Video Analysis \- NIPS, [https://proceedings.neurips.cc/paper\_files/paper/2024/file/55cb562b1f5af71f6707f3ff3c7941e6-Paper-Conference.pdf](https://proceedings.neurips.cc/paper_files/paper/2024/file/55cb562b1f5af71f6707f3ff3c7941e6-Paper-Conference.pdf)  
> 8. Prompt-based Adaptation in Large-scale Vision Models: A Survey Project Page: https://yunbeizhang.github.io/Awesome-Visual-Prompt-Tuning/ \- arXiv, [https://arxiv.org/html/2510.13219v2](https://arxiv.org/html/2510.13219v2)  
> 9. \[2112.02413\] PointCLIP: Point Cloud Understanding by CLIP \- ar5iv \- arXiv, [https://ar5iv.labs.arxiv.org/html/2112.02413](https://ar5iv.labs.arxiv.org/html/2112.02413)  
> 10. Duoduo CLIP: Efficient 3D Understanding with Multi-View Images \- arXiv, [https://arxiv.org/html/2406.11579v2](https://arxiv.org/html/2406.11579v2)  
> 11. Awesome-Vision-Language-Finetune/README.md at main \- GitHub, [https://github.com/Hodasia/Awesome-Vision-Language-Finetune/blob/main/README.md](https://github.com/Hodasia/Awesome-Vision-Language-Finetune/blob/main/README.md)  
> 12. LLM-enhanced Action-aware Multi-modal Prompt Tuning for Image-Text Matching \- arXiv, [https://arxiv.org/html/2506.23502v1](https://arxiv.org/html/2506.23502v1)  
> 13. LLM-enhanced Action-aware Multi-modal Prompt Tuning for Image-Text Matching \- CVF Open Access, [https://openaccess.thecvf.com/content/ICCV2025/papers/Tian\_LLM-enhanced\_Action-aware\_Multi-modal\_Prompt\_Tuning\_for\_Image-Text\_Matching\_ICCV\_2025\_paper.pdf](https://openaccess.thecvf.com/content/ICCV2025/papers/Tian_LLM-enhanced_Action-aware_Multi-modal_Prompt_Tuning_for_Image-Text_Matching_ICCV_2025_paper.pdf)  
> 14. CLIP for Point Cloud Understanding \- MSpace, [https://mspace.lib.umanitoba.ca/bitstreams/46107c8c-39a8-4347-9aa7-47fb72a4a1d5/download](https://mspace.lib.umanitoba.ca/bitstreams/46107c8c-39a8-4347-9aa7-47fb72a4a1d5/download)  
> 15. Enhancing CLIP with GPT-4: Harnessing Visual Descriptions as Prompts, [https://www.computer.org/csdl/proceedings-article/iccvw/2023/074400a262/1TaodPG4t4Q](https://www.computer.org/csdl/proceedings-article/iccvw/2023/074400a262/1TaodPG4t4Q)  
> 16. Unlocking the Multi-modal Potential of CLIP for Generalized Category Discovery \- arXiv, [https://arxiv.org/html/2403.09974v3](https://arxiv.org/html/2403.09974v3)  
> 17. PointCLIP: Point Cloud Understanding by CLIP | Request PDF \- ResearchGate, [https://www.researchgate.net/publication/363910072\_PointCLIP\_Point\_Cloud\_Understanding\_by\_CLIP](https://www.researchgate.net/publication/363910072_PointCLIP_Point_Cloud_Understanding_by_CLIP)  
> 18. GitHub \- 3dlg-hcvc/DuoduoCLIP: \[ICLR 2025\] Duoduo CLIP: Efficient 3D Understanding with Multi-View Images, [https://github.com/3dlg-hcvc/DuoduoCLIP](https://github.com/3dlg-hcvc/DuoduoCLIP)  
> 19. \[PDF\] PointCLIP: Point Cloud Understanding by CLIP \- Semantic Scholar, [https://www.semanticscholar.org/paper/PointCLIP%3A-Point-Cloud-Understanding-by-CLIP-Zhang-Guo/f3ce9ba3fcec362b70263a7ed63d9404975496a0](https://www.semanticscholar.org/paper/PointCLIP%3A-Point-Cloud-Understanding-by-CLIP-Zhang-Guo/f3ce9ba3fcec362b70263a7ed63d9404975496a0)  
> 20. (PDF) PointLLM-V2: Empowering Large Language Models to Better Understand Point Clouds \- ResearchGate, [https://www.researchgate.net/publication/393891118\_PointLLM-V2\_Empowering\_Large\_Language\_Models\_to\_Better\_Understand\_Point\_Clouds](https://www.researchgate.net/publication/393891118_PointLLM-V2_Empowering_Large_Language_Models_to_Better_Understand_Point_Clouds)  
> 21. TeDA: Boosting Vision-Lanuage Models for Zero-Shot 3D Object Retrieval via Testing-time Distribution Alignment \- arXiv, [https://arxiv.org/html/2505.02325v1](https://arxiv.org/html/2505.02325v1)  
> 22. Track: Poster Session 6 & Exhibit Hall \- CVPR, [https://cvpr.thecvf.com/virtual/2024/session/32088](https://cvpr.thecvf.com/virtual/2024/session/32088)  
> 23. ULIP-2: Towards Scalable Multimodal Pre-training for 3D Understanding \- ChatPaper, [https://chatpaper.com/zh-CN/chatpaper/paper/46367](https://chatpaper.com/zh-CN/chatpaper/paper/46367)  
> 24. \[2406.11579\] Duoduo CLIP: Efficient 3D Understanding with Multi-View Images \- arXiv, [https://arxiv.org/abs/2406.11579](https://arxiv.org/abs/2406.11579)  
> 25. ICLR Poster Duoduo CLIP: Efficient 3D Understanding with Multi-View Images, [https://iclr.cc/virtual/2025/poster/28703](https://iclr.cc/virtual/2025/poster/28703)  
> 26. Self-supervised learning for pre-training 3D point clouds: A survey \- SciOpen, [https://www.sciopen.com/article/10.26599/CVM.2025.9450514](https://www.sciopen.com/article/10.26599/CVM.2025.9450514)

[image1]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAkAAAAbCAYAAACuj6WAAAAAeklEQVR4XmNgGEmAEYjlgDgQiNuB2BdVmoHBCIj/A/FBIFaEskFYB6aAA4iXAPFnBogpIIChSByITwDxHSA2gAmiA4KKWIA4BoivAfETIM5hgDhYEJcikBuqsSkCAZh1IEXuaHJwMCQViQLxWSD+wABRdBWIT6KoGAUAancksQO5RlQAAAAASUVORK5CYII=>

[image2]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA0AAAAbCAYAAACnZAX6AAAAxUlEQVR4Xu2RsQ5BQRBFR5AoVAoqUUjUFBIiClp0fkFF6RcUNKLVSvQSlUQh0en9hMYfcMbuynpPJ7o9ySn23p1k3zyRQOAvpHGALcxEuhgVvGLHnnV4iWNMYBc3tntRxBP2/RDqeMESznDql1t8YMoPoWDzIe6w6gq9qMXRBR5ZMd0cm36Rt8XaDy1u6Cbmu964oZ4fWnR72q2ihXveJJIncWS72JBSw7OYTal7bIsZXOAdD2K2/IG+uYHlL3lOzH8L/MwTe3YexKIWDBcAAAAASUVORK5CYII=>

[image3]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABMAAAAaCAYAAABVX2cEAAABDElEQVR4Xu2TMW7CQBBFPwoFBUqDCCJNam5Ah5Qe2nQpqJFouEJOgNLQ0eQAqWgQkaBBUFPlBilzAPjfg/F6ZXtdIz/pFzsz+z3jsYGK+6VBdRw9pNMRbVhdkCbM5EidqW/qMVVhZkPqlxrD7hSyhRn9Ua9eTshg4gezqMMK1ZG6O1G9VAUwoJ68WCYtWLGQmTRL0hFT2EODvCMplInM/pM0nqkf55yLTBbOWeNpTBnGG1TXq1tFAX1q7cW0AC3ig6pRS1j3QVTkdia0CG32QL1QO9hDg2yQvHwXmWhU5eewDoNoxK4fhF2OF1FqRL1grTyPT5ihPp1c9P+NqC9qT71dYz7xIkqNWFHhcAGuqChorg+mRgAAAABJRU5ErkJggg==>

[image4]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAKMAAAAZCAYAAABdPZ6TAAADzklEQVR4Xu2azatPQRjHH6GU1yyI0PVekth5WVwLRVyFUhYiCyUpG8nNjmxYIEWXLGxsRJK8FFkglEiSFHUTWdgofwDP18w44zFzfuec38z53XOaT32798ycM2eeO995OTOXKJFIJBKJRCKRSCQSQVnOesCazpos8sAi1h7WcVa/yOuWaaTKPcmaKPLaQqgYx5FqoyGZUZQJrF8F9ZZUw9cNzHhfJjKjWdtI1e2b/gmNsW/qgtukynvH+sF6xJr5zx3NJ0aMZ2VCWWxTHhB5U0m9AHnrRV4d+Mw4TKpO8/S1qX+3HWYS6xapsnaw1rF+6utd1n1NJmaMUc0IMAQjb5/MqAGfGU19UXeAXv2ZNervHdVYyvrA+kjq3Wi4c6zz+vc2EDPGKGaEAfdTtk7DNI0K101RM4YC70MjmYZqIzFjjGJGpF0jtSgFD/V13UgzzmBtpqy+2/U1Ok+3oAzE/0ULv6NsvLMtxI4xqBkx+qFyb/S1MWMnMD1ifYn7i6rIqNbJjDv1dWgzouyjFLahRgKxYwxqRqmiZsS2wGXWixI6/OfJfKQZDWXrVxQzhaHsXnyw1UHMGIOa0YyMz/V16MYuSzJjeGLGGNSMvjVjryhjRkxBx1gvqfrC3NdQA6xLrFWse6xNVl7T8MVowPYYDhoOygxmC6kpfqXM0EQxo/ya7hVlzbiGdYjCm/EGZSc8c1mPWbOy7Ebhi9GwgXWC/jfWHFJ/26ekTm5cyGdK4zJjWer6gDG4zGhADD4zria1z+bD11AYFU9b1zIfLGCtFWk2ODXCiJK3F4p4xstEC5SB9+SVUTVGA5Zq6GjSdBgV0SHz9ptHhBljEdKMaEA8g9MGH50aCkxhvWYtFOnmWNJ3JIklBPIx8rhAeSj3Kvk7KkYm1H+rzNCEiPEUqVnmFatPp2GgMV/ivikaVDajbUKXXBWtG2lG1EnWE7LxmRG8Z30ld2PD2LJc+cedTeq0Z6xIBzdZ38n/7o2sT6z5MkOD0w+cggyS39A4unvCWiIzLLqNsV//NB5YxtpNavvnGfnrBmRZrUKasQh5ZgQryN1QRbjC2isTLbDFlffuuqgaI54x/yyBjoMpGaMxRkaYFJ0tj2RGQZ4ZMaJdkIkFwHOYZg1HSDW4BCdCeSNHHVSNEdhLCKwZ71IWDzoi0vJIZhTAjC6jgAHWdZlYAIwOw5Rt2GO66rPyAabwOyKtF1SNEWvCM9Y1tvZs82ENedG6dtF6M2LPC2udENtMvvVaCBaTey1ZNzFj9AEjo42GZEabsL/8Wt3rGo79YZlINJffdKopTmlQ+IkAAAAASUVORK5CYII=>

[image5]: <data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAC4AAAAYCAYAAACFms+HAAACLklEQVR4Xu2WPUscURSGT4gBCSEJ8YtALFIkprBQKztBhFgYiGCpBjvRFClsgnZ2NiKiiGAhWkgEiYWgSLDws9FGDBgUtgiksAn4A+L75tzLXA+7s+64xSzsAw/MnDtz9uy9586MSJkyZUqGp3AMTsA6M5ZKGuE/eAHfwVN3Ph5elDYq4IxooaOif+Lcnae6cLbEkWih781YqinJwp+IFmz9HF6URtjfvfCnaMHT8AN8G16UVsJWKWSmuVo1NpiFSlhrg3lg7oc2aElSeIPo9T/sgOE1vIYndiCGPdHcVXbAkqRwwmd9vw1m4RB+tcEY2KbMnZekhf+GrTaYhT+w0wZj6BHNnZe4wtlnW7APbsIDF38O50U3t4fnC3BIouvY3xn4DU7BJRcn23AQros+HDwborlieQyP4V/Rwn/BWRd/AIdF+5QsS9TTXM6wTepFv28eid7HpxOLfglXRL+BmkTfyKQFfnTHbCN+anju2oI5GYFXwTl/1Cfkp4DfPL4n/eyz4EXRleQK+kcrW4CT0ya383KGJ4NzTk7ejRkHl3bNHXMWfUJf6Bv4BXaIPjk8nyTqUebw7MA50T/jZ55cwmbYJdFKMndiWMC+aNFcVi4/j1loBg7AbvgK7uot/+E97F3CVeNK8D4WzpZqh2dunOfcX8zBopmbG565iwKXmT3qYS/TEL5knpkYeSG54/xDbC0ee/hSs7kLgrNVLdFnLzdYSfAdropunHv1XLG5AZ6VbNeNkai2AAAAAElFTkSuQmCC>

[image6]: <data:image/png;base64,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>