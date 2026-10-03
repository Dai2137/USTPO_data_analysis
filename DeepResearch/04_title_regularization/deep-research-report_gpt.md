# 意匠特許タイトルの正規化・統合に関する既存研究サーベイ

## 全体像

ご提示の問題設定は、**自由記述の短い名詞句ラベルを、そのまま閉集合分類の正解ラベルに使うには表記ゆれ・言い換え・粒度差が大きすぎる**一方で、**Locarno という既存の粗い階層コードは既にある**、という点で、一般的な「テキスト分類」よりもむしろ **entity normalization / concept normalization / taxonomy refinement / hierarchical weak supervision** の交点にあります。IMPACT は約 50 万件の USPTO 意匠特許と 361 万枚の図面を収録した大規模データセットで、Locarno は WIPO が管理する意匠の国際分類です。USPTO も、意匠特許の書誌データに付く Locarno designation は「その特許の original classification」を示すと明記しています。したがって、**Locarno を親ラベル、title 正規化後ラベルを子ラベルとする中間粒度の体系を構築する**、という方向は既存研究の潮流とよく整合します。 citeturn7search1turn39view0turn39view1

今回確認した主要ソース群では、**IMPACT や設計図面タスクに対して、title を意味的に名寄せして中粒度ラベルへ統合すること自体を主題にした研究は見当たりませんでした**。近い研究は、特許分野では **Locarno / IPC / CPC など既存コードへの分類**、あるいは **図面と説明文を使う multimodal classification / retrieval** が中心です。ACL 2025 の特許サーベイは patent classification・retrieval・generation を大きな柱として整理しており、design patent の最近の研究も、短いテキスト・画像・メタデータを統合して **Locarno 系コードを予測する**方向が主です。つまり、**あなたの課題は「特許分類」よりも「ラベル体系の再編成」寄りであり、直接の先行研究は薄いが、隣接分野には強い類推先がある**、というのが結論です。 citeturn40view0turn40view1turn35search2turn35search5

その隣接分野の中で、最も近いのは **生物医学用語正規化**です。ここでは短い表層語が多数の同義表現・略語・上位下位関係を持ち、最終的に UMLS のような標準概念へマップされます。UMLS は 2026AA 時点で 353 万超の概念と 1,806 万超の名前を統合しており、WordNet も synset・hypernym などの概念関係を提供します。したがって、**意匠特許 title を「概念正規化」の問題として扱う**のが、既存研究に最も素直に接続できる見方です。 citeturn39view3turn39view2turn27search0

結論を先に言うと、あなたの設定に最も適用しやすいのは次の三系統です。  
第一に、**Locarno 内で埋め込みクラスタリングを行い、クラスタ代表名を人手または LLM で決める方法**。第二に、**Locarno を制約とした LLM ベースの正規化・タクソノミー拡張**。第三に、**上の二つを組み合わせ、分類学習時には階層損失や多粒度ラベル学習を使うハイブリッド**です。特に、完全に LLM だけに寄せるより、**Locarno 制約つき埋め込みクラスタリング + 限定的 human-in-the-loop** が、精度・コスト・再現性のバランスで最有力です。 citeturn39view5turn36view1turn36view2turn36view6turn36view7

## ラベル統合の方法論

自由記述ラベルの正規化には、大きく分けて **候補検索と再ランキング**、**埋め込み空間でのクラスタリング**、**知識ベースを使った概念統合**、**LLM による正規化・再命名** が使われています。生物医学では BioEL の標準的枠組みとして、まず candidate generation で候補概念を広く拾い、次に entity disambiguation / reranking で最終概念を選ぶ二段階が定着しています。これはそのまま、意匠特許でも **title → 候補 canonical label → 最終 canonical label** に移植できます。 citeturn41view0

特に重要なのは、**表層一致ではなく「概念同一性」を学習する埋め込み**です。BioSyn は不完全な同義語集合から表現を学習し、候補検索を反復的に難化させることで entity normalization を改善しました。SapBERT は UMLS 同義語対で自己整列する metric learning により、概念表現空間全体を synonym-aware に再構成しました。BERGAMOT はさらに、UMLS グラフ上の近傍構造まで取り込んで inter-concept / intra-concept interaction を表現へ埋め込みます。**短い名詞句の言い換え・同義語・上位下位語を区別しながら近づけたい**というあなたの要件に、最も近いのはこの系統です。 citeturn8search4turn29search10turn36view3

LLM 側では、**正規化そのものを「推論付きランキング問題」として解く**流れが出ています。COLING 2025 の biomedical terminology normalization 論文は、training-free の multi-agent 方式で、候補取得時に知識カードを作り、最終段階では LLM に候補標準語のランキングをさせています。これは、意匠特許でも **複数候補の canonical title の中から最も適切な統合先を LLM に選ばせる**設計に極めて近いです。ただし、この論文自身も LLM 推論コストを制約として挙げています。 citeturn39view4

完全教師なしクラスタリングの現実的な雛形としては、CDE harmonization の 2025 年研究が参考になります。これは heterogeneous な Common Data Elements を **LLM 埋め込み + HDBSCAN** でクラスタ化し、さらに **LLM 要約でクラスタ名を付け、最後に新規要素を既存クラスタへ割り当てる分類器**まで作っています。設計としては、今回の「title 群をまず統合し、その後で画像分類用の閉集合ラベルへ落とす」構成と非常に相似です。 citeturn39view5

### 代表手法の整理

| 手法・論文 | 入力 | 既存タクソノミー | 統合アルゴリズム | 評価 | 実装 | 使いどころ | 出典 |
|---|---|---|---|---|---|---|---|
| **BioSyn** (ACL 2020) | 短い mention と概念同義語群 | あり | 同義語学習 + iterative candidate retrieval | 正規化精度 | 公開あり | 表層差が大きい短句の名寄せ | citeturn8search4turn30search0 |
| **SapBERT** (NAACL 2021) | 短い mention / 概念名 | あり | UMLS 同義語対による metric learning | 6 benchmark で SOTA 報告 | 公開あり | 同義語を近づける埋め込み学習 | citeturn8search1turn29search10turn29search0 |
| **BERGAMOT** (NAACL Findings 2024) | 概念名 + 知識グラフ近傍 | あり | PLM + GNN + graph contrastive objectives | 多言語 UMLS 系評価 | 公開あり | synonym だけでなく概念近傍も使いたいとき | citeturn36view3turn28search4 |
| **LLM-based Biomedical Terminology Normalization** (COLING 2025) | 短い非標準表現 | あり | 候補取得 + knowledge cards + LLM ranking | accuracy / hit rate 改善 | 論文上は training-free、実装未確認 | 少量高難度の曖昧ペア検証 | citeturn39view4 |
| **CDE Semantic Grouping** (2025) | 異種 CDE の短文ラベル | 弱くあり | LLM embeddings + HDBSCAN + LLM summarization + classifier | ARI / NMI / accuracy | 実装未確認 | 完全教師なし寄りの初期ラベル統合 | citeturn23search3turn39view5 |
| **WordNet / UMLS 型知識ベース利用** | 語彙ラベル | あり | synonym / hypernym / concept links に基づく統合 | 個別タスク依存 | 資源公開 | “car/automobile”, “shoe/footwear” 型の語彙統合 | citeturn39view2turn39view3 |

この表から見えるのは、**完全に同一概念の統合**には SapBERT/BioSyn 型が強く、**上位下位関係の扱い**には WordNet/UMLS/BERGAMOT 型が強く、**クラスタ命名や曖昧ケースの最終判断**には LLM が効く、という分業です。したがって、意匠特許 title の実務パイプラインでも、**一発クラスタリング単独より「埋め込みで候補集合を絞り、LLM/人手で確定する」方が研究的にも実践的にも自然**です。 citeturn41view0turn36view3turn39view4

## 既存タクソノミーを足場にした精緻化

今回の設定で最も重要なのは、**Locarno を単なる補助特徴ではなく、ラベル体系生成の制約として使う**ことです。これに近い研究群は、hierarchical text classification や taxonomy expansion で発達しています。TELEClass は、ラベル名しかない極少監督条件で、**LLM による taxonomy enrichment** と **corpus から掘った class-indicative features** を併用し、さらに LLM ベースのデータ annotation / generation を行います。重要なのは、TELEClass が「生の taxonomy skeleton は弱すぎる」と明示し、その内側を追加的特徴で埋めていく設計を取っている点です。これはまさに、**Locarno はあるが粗すぎる**というあなたの問題設定に合います。 citeturn36view1turn38view0turn38view2

HiLA は、**既存階層の最下層に LLM で子ノードを生成して階層を深くする**という、より直接的な方法です。しかも、taxonomic granularity を cosine-similarity ベースで事前診断し、**その階層が深める価値を持つかどうか**を測る指標まで提案しています。これは、「Locarno subclass の内側を title から中粒度に深掘りしたい」という要求にほぼ直結します。Locarno を親に固定し、その下に “chair / office chair / dining chair” のような child layer を作る発想は、HiLA の最も自然な転用先の一つです。 citeturn36view2turn38view3turn30search2

より広い taxonomy expansion では、TAXMAP が **LLM encoder と collaborative mapping** で taxonomy を拡張し、TaxoAdapt は **LLM 生成 taxonomy をコーパスに動的適応**させます。Amazon Science の 2026 年の interactive taxonomy development は、topic modeling と LLM を組み合わせ、**人間が反復的に taxonomic split / merge / re-map を行える UI** を提示しています。したがって、意匠特許でも、人間が最終責任を持つ形で **Locarno 内クラスタを提案 → 受理 / 却下 / 再配置**する human-in-the-loop 設計には、十分な先行事例があります。 citeturn25search4turn32search15turn36view6turn32search16

### 既存タクソノミーを使う研究の整理

| 手法・論文 | 入力 | 既存タクソノミー | 中核アイデア | 評価 | 実装 | IMPACT への含意 | 出典 |
|---|---|---|---|---|---|---|---|
| **TELEClass** (WWW 2025) | 文書 + raw taxonomy + unlabeled corpus | 必須 | taxonomy enrichment + LLM annotation/generation | HTC 性能、LLM 直接推論とのコスト比較 | 公開あり | Locarno 内で title clusters を語彙・コーパス知識で補強 | citeturn36view1turn38view2turn30search1 |
| **HiLA** (ACL 2024) | 文書 + label hierarchy | 必須 | LLM で leaf の下に child labels を生成 | ZS-HTC 精度、granularity 指標 | 公開あり | Locarno subclass の直下に中粒度ラベル層を追加 | citeturn36view2turn38view3turn19search3 |
| **TAXMAP** (SAC 2025) | taxonomy + new concepts | 必須 | collaborative LLM mapping による taxonomy expansion | baseline 比較 | 実装未確認 | 新しい title 表現を既存体系へ吸収 | citeturn25search0turn25search4 |
| **TaxoAdapt** (ACL 2025) | コーパス + LLM-generated taxonomy | あり | taxonomy を corpus に適応し width/depth を調整 | scientific corpora 上の SOTA 報告 | 公開あり | Locarno 内部をデータ分布に合わせて再編可能 | citeturn25search5turn32search7 |
| **Interactive Taxonomy Development** (CHI 2026) | 大規模コーパス + 初期 taxonomy | あり | topic modeling + LLM + interactive UI | 事例検証 | 実装未確認 | split / merge / re-map を人間が安全に確定 | citeturn36view6turn32search16 |
| **Insert or Attach** (ACL 2024) | existing taxonomy + novel concepts | 必須 | box embedding による taxonomy completion | MRR / Hit@1 / Prec@1 | 実装未確認 | 既存体系への新ノード挿入問題として定式化可能 | citeturn18search21 |

この系統から引ける実務上の示唆は明快です。**Locarno を無視して全 title を一括クラスタリングするより、まず Locarno で分割し、その内部だけを深掘りする方が研究的にも正当化しやすい**。さらに、人手コストをかけるなら、全件にではなく **クラスタ境界が曖昧な部分、上位下位関係が絡む部分、LLM と埋め込みが不一致な部分**に集中させるべきです。 citeturn36view6turn38view2turn38view3

## ノイズ自由記述ラベルからの画像分類学習

WebVision や Clothing1M は、**Web 由来の弱教師ラベルをそのまま画像学習に使う**代表例ですが、ここで重要なのは、これらがラベル体系そのものを再設計するより、**与えられた閉集合ラベルのノイズ耐性を上げる**研究として使われてきた点です。WebVision は ImageNet の 1,000 semantic concepts をクエリに 240 万超の Web 画像を集め、title / description / tags などのメタ情報も持ちます。一方 Clothing1M はオンラインショッピングサイトの周辺テキストからラベルを付与した 14 クラスの実世界 noisy-label データです。つまり、**自由記述テキストは取得時のラベル源ではあるが、最終学習ラベルは既に固定カテゴリ**であり、あなたが必要としている「自由記述 label 自体の統合」とは少しズレます。 citeturn12search0turn12search11turn12search8turn33search21turn13search9

この分野が役に立つのは、**正規化しきれない残余ノイズを学習時にどう吸収するか**という点です。CVPR 2024 の Learning with Structural Labels は、ノイズラベル学習において **class distribution の追加情報**を structural labels として使うと性能が上がることを示しました。これは、あなたのケースでは **canonicalized title label に加え、その親 Locarno や近隣クラスタ分布を補助ターゲットとして持たせる**設計に相当します。また、NeurIPS 2024 の VLM-based noisy label detector は、**テキスト・画像の alignment を使ってノイズラベル検出**を行います。これは、title 正規化後でも図面とタイトルが整合しない例を弾く二次フィルタとして有効です。 citeturn11search13turn31search4turn33search15

さらに、階層・多粒度ラベル学習は、統合後ラベルが完全に単一粒度に揃わない場合の保険になります。CHiLS は、既存または GPT 生成の subclasses を使って、**coarse label の中身を下位概念集合へ展開し、最終予測を親へ戻す**ことで zero-shot 分類を改善しました。Label Relation Graphs Enhanced Hierarchical Residual Network は、粗粒度と細粒度の間で階層知識を伝播させ、**一部サンプルが coarse-only / fine-only でも扱える**設定を明示しています。したがって、完全な label cleanup が難しいなら、**学習器側で coarse-fine の混在を許す**ことも研究的に妥当です。 citeturn36view4turn38view5turn10search3turn10search18

### 画像分類側の関連研究

| 手法・データ | 生ラベルの性質 | ラベル統合そのものを行うか | 学習時の主な対処 | 実装 | IMPACT への含意 | 出典 |
|---|---|---|---|---|---|---|
| **WebVision** | Web メタデータ由来、閉集合 1000 クラス | ほぼ行わない | noisy supervision 下で分類学習 | データ公開 | title メタ情報はあるが class names は固定 | citeturn12search0turn12search8 |
| **Clothing1M** | 周辺テキストから遠隔付与、14 クラス | 行わない | label noise 耐性学習 | データ・コードあり | EC タイトル起源のノイズ例として有用 | citeturn13search9turn33search21turn12search1 |
| **Learning with Structural Labels** (CVPR 2024) | noisy closed-set labels | 行わない | 追加の構造ラベルを使い頑健化 | 実装未確認 | canonical title だけでなく Locarno も併用すべき | citeturn11search13turn31search4 |
| **CHiLS** (ICML 2023) | coarse / uninformative class names | 擬似的に行う | subclasses を生成し zero-shot 推論後に親へ戻す | 公開あり | Locarno から下位 label set を作る発想に近い | citeturn36view4turn28search2 |
| **Label Relation Graphs Enhanced HRN** (CVPR 2022) | multi-granularity labels | しない | coarse-fine 間の階層伝播 | 実装未確認 | 統合後も粒度混在が残る場合の学習器候補 | citeturn10search3turn10search18 |
| **Vision-Language Models are Strong Noisy Label Detectors** (NeurIPS 2024) | noisy image labels | しない | VLM alignment で noisy labels を検出 | 実装未確認 | 図面と canonical title の不整合検出に有効 | citeturn33search15 |

この領域の教訓は、**学習時ロバスト化は必要だが、ラベル統合の代替にはならない**ということです。WebVision や Clothing1M の系統だけでは、`Coffee Maker` と `Coffeemaker` や `Car` と `Automobile` を一つの教師クラスへまとめることはできません。したがって、**まずラベル体系を整理し、その後に noisy-label learning を足す**順序が妥当です。 citeturn12search0turn13search9turn33search15

## 近接ドメインでの実例

### Eコマース

Eコマースは、あなたのケースに次いで近い産業応用です。商品タイトルは短く、販促語やブランド語が混じり、同一商品でも表現が揺れます。TMIS 2020 の product categorization 論文は、EC プラットフォームが **3〜10 層・数千 leaf node の taxonomy tree** を持つことを前提にしています。ACL Workshop 2024 の dual-expert system は、まず candidate categories を絞り、その後 LLM expert が微妙なカテゴリ差を判断する構成で、**候補生成 + LLM 精査**という設計が、タイトル正規化にもそのまま効きます。OA-Mine はさらに、product title を「attribute values の袋」とみなし、**弱監督で attribute value 候補を抽出し、属性クラスタへまとめる**ことで open-world の新属性まで扱いました。これは、**title を単一ラベルとしてではなく意味要素の集合として分解してから統合する**方向を示しています。 citeturn15search12turn17search11turn15search5

商品名寄せそのものでは、internet-scale product matching や multimodal product matching の研究が、**テキストと画像の双方を使って同一商品を判定**しています。2022 年の internet-scale product matching は、異表現 listings を同一 product に寄せるスケール課題を扱い、2025 年の LLM-based verification や 2024 年の end-to-end multimodal matching は、初段を軽量候補検索、後段を重い照合器や LLM にする設計を取ります。**title canonicalization でも、全組み合わせ比較ではなく、「埋め込みで近傍候補を引く → LLM or 人手で最終統合」**が定石です。 citeturn16search5turn17search0turn14search3turn14search13

### 医療・生物医学

生物医学では **concept normalization** が主タスクであり、評価枠組みも非常に参考になります。EMNLP 2023 の包括評価は、entity linking を **candidate generation と disambiguation の二段階**で統一評価し、recall@1 と recall@5 を主要指標として比較しました。また、性能だけでなく scalability・adaptability・usability・zero-shot robustness まで見る枠組みを提示しています。意匠特許でも、**まず title 正規化器そのものの recall@k を見る**、**次に最終 canonical label の top-1 正解率を測る**、**さらに下流の画像分類精度を見る**、という三層評価が妥当です。 citeturn41view0

### 特許・知財

特許分野では、現状の主流は title 名寄せではなく、**既存分類コードを予測する patent classification** です。ACL 2025 の patent survey は、特許分類の中心を IPC / CPC のような階層分類に置いています。design patent 側でも、Springer 2025 の設計特許分類研究は、**テキストが非常に短く冗長であるため、画像や assignee の Locarno 履歴まで組み合わせる**方向を取っています。IMPACT と DesignCLIP も、図面・キャプション・multimodal retrieval / classification を中心に据えており、title canonicalization は主目的ではありません。したがって、**特許そのものの先行研究より、医療概念正規化と EC taxonomy engineering の方が、今回の課題には実装上近い**と言えます。 citeturn40view0turn40view1turn35search4turn35search2

### 近接ドメイン事例の比較

| ドメイン | 典型入力 | 足場となる体系 | 代表タスク | IMPACT への転用可能性 | 出典 |
|---|---|---|---|---|---|
| Eコマース分類 | 商品タイトル・画像 | 商品 taxonomy | taxonomy mapping / product matching | 非常に高い。短文・販促語・表記ゆれが近い | citeturn15search12turn17search11turn16search5 |
| Biomedical normalization | mention・略語・概念名 | UMLS / ontology | concept normalization | 非常に高い。短句の同義語統合・上位下位関係が近い | citeturn39view3turn41view0turn36view3 |
| Patent classification | title / abstract / claims / image | IPC / CPC / Locarno | code classification | 中程度。既存階層利用は近いが title 名寄せは薄い | citeturn40view0turn40view1 |
| Design patent multimodal understanding | 図面・title・captions | Locarno | classification / retrieval | 中程度。画像側の下流タスク設計に有用 | citeturn35search2turn35search5 |

## 評価設計と推奨アプローチ

### 評価の考え方

近年論文を見ると、ラベル統合の質は単一指標では捉えられていません。BioEL では **recall@1 / recall@5** が候補検索と最終正規化の双方を見る標準指標です。CDE harmonization では **ARI / NMI** を外部基準との一致評価に使い、TELEClass は **最終分類性能と推論コスト** を比較し、Hierarchical Text Classification の最近の研究は **hierarchical F1 や階層専用指標**を使うべきだと強く主張しています。したがって、意匠特許でも、**ラベル統合の intrinsic 評価・階層整合性・画像分類への下流効果・推論/アノテーションコスト**を分けて測るべきです。 citeturn41view0turn39view5turn38view2turn36view7turn38view4

推奨する評価設計は次のようになります。  
まず、Locarno ごとに小さな gold set を作り、title ペアや title→canonical label の正解を人手で付けて **top-1 / top-5 正規化精度** を測る。次に、統合後ラベルと Locarno 親子関係の整合を **hierarchical F1** や tree-distance 系で測る。さらに、統合前後で画像分類モデルを同条件学習し、**top-1 accuracy, macro-F1, calibration, confusion concentration** を比較する。最後に、**1 accepted merge あたりの人手時間**、**1,000 件あたりの LLM 推論費**、**新規 title の incremental assignment 時間**を運用指標として足す。TELEClass は、LLM 直接推論より学習済み方式がはるかに低コストであることを示しており、この観点は非常に重要です。 citeturn38view2turn36view7turn41view0

### 三つの主要アプローチの比較

| アプローチ | 何をするか | 長所 | 弱点 | IMPACT への適性 |
|---|---|---|---|---|
| **LLM でラベルを正規化してから閉集合分類** | title 群を LLM に canonical name へ直接写像させる | paraphrase に強い。クラスタ命名がしやすい。説明文も出せる | コスト・再現性・幻覚。全件推論は高価。粒度一貫性の維持が難しい | **中〜高**。少数候補の最終決定には良いが、全件一次処理は重い citeturn39view4turn38view2 |
| **埋め込みクラスタリングで正規化** | title を embedding 化し、Locarno 内でクラスタ化して canonical label を付与 | スケーラブル。新規データの増分処理が容易。再現性が高い | 上位下位語の混同や過分割に注意。クラスタ名は別途必要 | **高**。最初の統合母体を作るのに最有力 citeturn39view5turn8search4turn29search10 |
| **Locarno を制約として使う方法** | まず Locarno で空間を分け、その内部だけを enrichment / clustering / canonicalization | 検索空間が狭まり、誤統合が減る。階層評価しやすい。運用しやすい | Locarno 自体の粗さ・誤記・複数コード問題は残る | **最も高い**。今回のデータ特性に最も自然 citeturn39view1turn36view1turn36view2 |

端的に言えば、**LLM 単独**は強いが高価、**埋め込みクラスタリング単独**は安いが粒度判断が難しい、**Locarno 制約つきハイブリッド**はその両方の欠点をかなり打ち消せます。研究上も、taxonomy enrichment 系と normalization 系と noisy-label learning 系をつなぐと、この第三案が最も筋がよいです。 citeturn36view1turn36view2turn39view4turn39view5

### 推奨する方法

**最有力は、Locarno 制約つき埋め込みクラスタリング + LLM/人手での canonical naming** です。  
具体的には、Locarno subclass ごとに title を分け、SapBERT/BioSyn 型の metric-learning 発想で学習した short-phrase embedding か、高品質 sentence embedding を作り、HDBSCAN あるいは agglomerative clustering でクラスタ化します。その後、各クラスタの medoid title を仮代表名にし、LLM には **代表名の正規化・クラスタ説明・上位下位の警告**だけをさせます。最後に、人手は **クラスタ merge / split / relabel の確認**にだけ入る。この方式は、CDE harmonization のクラスタ生成パイプライン、生物医学の candidate generation + reranking、interactive taxonomy development の HITL 設計を最もうまく合わせたものです。 citeturn39view5turn41view0turn36view6turn8search4turn29search10

**第二候補は、TELEClass / HiLA 型の Locarno 内タクソノミー拡張**です。  
Locarno の leaf あるいは subclass を親として、その中に LLM で **候補 child labels** を生やし、コーパス頻出 title と画像近傍例で候補を絞り、最終的に closed-set classifier を訓練します。これは、最初から「中粒度ラベル体系を作る」ことを明示的に行いたい場合に向いています。とくに **“chair / office chair / folding chair” のような細分が欲しい**なら、クラスタリングよりも最初から階層拡張問題として扱う方がきれいです。弱点は、LLM が作る child label の品質が Locarno ごとにばらつくことです。HiLA が提案する granularity 診断を併用すると、深掘りの価値がある subclass とそうでない subclass を事前に分けられます。 citeturn36view2turn38view3turn36view1

**第三候補は、統合後も粒度混在を許す階層学習方式**です。  
もし `Chair` と `Office chair` を完全には統合しきれないなら、Label Relation Graphs や structural labels の考え方を使って、**親ラベル Locarno / 中粒度 canonical label / 必要なら粗粒度 alias 群**を同時に持たせる multi-granularity 学習が有効です。これは前処理の不完全さに強く、画像分類器の頑健性も上げやすい。ただし、**最終的に閉集合の単一 class index が欲しい**という要件が強いなら、これは第一候補の補助策として使うのがよいです。 citeturn10search3turn11search13

### 最終提案

あなたのデータ特性に最も合うのは、次の順で実装する案です。  
まず **Locarno subclass ごとに title を分割**します。次に **title 埋め込みの近傍グラフ**を作り、同義語候補・パラフレーズ候補・上位下位候補をまとめたクラスタ候補を作ります。三段目で、**WordNet と domain-specific ルール**を使って lexical synonym / hypernym を補助し、さらに **LLM にはクラスタの canonical name 付けと曖昧クラスタの ranking だけ**を担当させます。四段目で human-in-the-loop により **split / merge / relabel** を最小限実施し、最後に **画像分類は canonical label と Locarno 親ラベルの両方を使う階層学習**で訓練する。この形が、既存研究の知見を最も無理なく接続した設計です。 citeturn39view2turn39view5turn39view4turn36view6turn36view7

実務上の推奨順位を明示すると、**第一推奨は「Locarno 制約つき埋め込みクラスタリング」**、**第二推奨は「TELEClass / HiLA 型の taxonomy enrichment」**、**第三推奨は「LLM 直接 canonicalization を曖昧ケースに限定して使う」**です。逆に、**最初から title 全体を LLM に一括で正規化させる**やり方は、コスト・再現性・粒度制御の観点で、研究的にも運用的にも第一選択にはなりにくいです。 citeturn38view2turn36view2turn39view4

今回確認した範囲では、**意匠特許タイトルの名寄せそのもの**に真正面から取り組んだ先行研究は薄い一方、**生物医学概念正規化、EC taxonomy engineering、hierarchical weak supervision** には、そのまま転用できる部品がかなり揃っています。したがって、このテーマは「先行研究がない」よりも、**異分野の成熟手法を design patent に接ぎ木する余地が大きい研究テーマ**と位置づけるのが適切です。 citeturn40view0turn40view1turn41view0turn36view1turn39view5