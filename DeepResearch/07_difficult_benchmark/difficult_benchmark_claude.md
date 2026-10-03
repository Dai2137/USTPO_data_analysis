# 意匠特許ドメインの手法評価に適した「概念的に難しい」画像認識ベンチマーク調査

## TL;DR
- **著名性・「概念的難しさ」・意匠特許ドメイン（多様な工業製品・専門機器のニッチなカテゴリ）との接続性を総合すると、最有力は FOCI（arXiv:2406.14496、多肢選択の細粒度物体分類）と、その素材である古典的FGVCデータセット群（FGVC-Aircraft／Stanford Cars／iNaturalist）である。** FOCIは「汎用VLMは視覚を捉えても正しい概念に結び付けられない（=画像エンコーダとLLMの整合不足＝モダリティギャップ）」ことを定量的に示しており、意匠図面の「見た目は似ているが概念が異なる工業製品」という課題と構造が一致する。
- 難易度の根拠が「画風」ではなく「概念そのもの」にあり、かつ汎用VLM（GPT-4V／GPT-4o／Gemini／CLIP）のスコアが定量報告されているベンチマークとして、**FOCI・FINER・iNaturalist（FGVC）・FungiCLEF・INQUIRE・MMMU/MMMU-Pro** を推奨する。「専門知識がないと人間でも間違える」ことが論文で最も明示的なのは iNaturalist・FungiCLEF・CUB（Turkラベル誤り率>4%）・GPQA（テキスト参照点）である。
- 一方、意匠特許に「対象物のドメイン（工業製品・機械部品）」まで一致させたい場合、純粋な工業部品の画像分類VLMベンチマークは希少である。MCB（機械部品／ただし3D CAD・非VLM）やRP2K/Products-10K（小売SKU）が近いが、いずれも「VLMが概念で苦戦する」ことを主眼にした評価ではない点に注意が必要。

## Key Findings

1. **「概念的難しさ」を最も直接的に、かつVLM評価として定式化しているのはFOCIである。** FOCIは既存分類データセットから4択問題を構成し、CLIPで「意味的に最も近い誤選択肢（hard negatives）」をマイニングすることで難易度を保持する。12個の公開LVLMを評価し、最良のIdefics-2でも平均64.13%、人気のLLaVA-1.5は46.75%、最下位Idefics-1は42.19%にとどまる。決定的な発見は「LVLMの画像エンコーダはCLIP由来なのに、CLIPの方がLVLMより一貫して高精度」という点で、原論文は要旨で *"CLIP models exhibit dramatically better performance than LVLMs. Since the image encoders of LVLMs come from these CLIP models, this points to inadequate alignment for fine-grained object distinction between the encoder and the LLM"* と述べている。これは依頼者が示したい「視覚的特徴と意味的知識の間のギャップ」そのものであり、LoRAで整合を改善するという主張を直接支える。

2. **古典的FGVCデータセット（iNaturalist, FGVC-Aircraft, Stanford Cars, CUB-200, NABirds, Stanford Dogs）は、汎用VLMが概念レベルで壊滅的に苦戦することが複数論文で定量化されている。** FINER（Kim & Ji, EMNLP 2024 main）は、粒度が細かくなるほど精度が崩壊することを示し、逐語で *"average drop of 65.58 in EM for Stanford Dogs for LLaVA-1.5"* と報告している。iNaturalistのfine（species）粒度ではGPT-4Vが約18.75%、LLaVA-1.5(13B)が約1.56%まで低下する一方、superordinate（上位）カテゴリではほぼ100%であり、これは「概念の粒度」起因の難しさの明確な証拠である。

3. **iNaturalist系（種の同定）は「専門知識がないと人間でも見分けられない」ことが最も明示的なドメイン。** FungiCLEF（キノコ種同定）は「正確な同定には微視的検査が必要」と明記し、毒/食用の識別など専門知識を要求する。INQUIRE（Vendrow+, MIT/UCL/Edinburgh, NeurIPS 2024 Datasets & Benchmarks Track）は生態学者・鳥類学者・昆虫学者・海洋学者ら専門家由来の250クエリ（iNat24=500万枚、33,000一致）を用い、逐語で *"the best models failing to achieve an mAP@50 above 50%"*、リランクでは *"the highest AP of 59.6, achieved by GPT-4o, is far below the perfect score of 100"* と報告している。

4. **専門知識が本質的に必要な難しさの「頂点」はMMMU/MMMU-Proだが、これは分類ではなく推論寄り。** MMMUはGPT-4Vで56%、GPT-4oでも69.1%程度、Gemini Ultra 59%（人間専門家≈90%）。MMMU-Proでは各モデルが大幅低下し、要旨で *"model performance is substantially lower on MMMU-Pro than on MMMU, ranging from 16.8% to 26.9% across models"*、4択→10択の効果として *"GPT-4o (0513) experienced a decrease of 10.7%, from 64.7% to 54.0%"* と述べる。工学（Tech & Engineering）分野を含むが、意匠特許の「物体カテゴリ識別」とはタスク性質が異なる。

## Details（候補一覧・著名性×概念的難しさ順）

下表は「著名性」と「概念的難しさ（＝画風ではなくカテゴリ/概念そのものの識別困難性）」が高い順。ImageNetベースかどうかも明記した。

| # | ベンチマーク（提供元・年・論文） | タスク／指標 | データ規模 | なぜ「概念的に難しい」か | 難易度の数値（SOTA・汎用VLM・人間） | 著名性の根拠 | ImageNetベース？ | 入手方法 |
|---|---|---|---|---|---|---|---|---|
| 1 | **FOCI** (Geigle, Timofte & Glavaš, U. Würzburg, 2024, arXiv:2406.14496) | 4択の細粒度物体分類／accuracy | 9サブセット。標準5種（航空機100 variant・車196・料理101・花102・ペット37）＋ImageNet-21k由来4種（動物1322・植物957・食品563・人工物2631クラス） | CLIPで「意味的に最も近い誤選択肢」をマイニングし近縁カテゴリの識別を強制。汎用VLMが視覚を捉えても概念に結び付けられない「エンコーダ-LLM整合の不足」を示す設計 | 最良LVLM Idefics-2=**64.13%**、Qwen-VL-Chat=62.41%、LLaVA-1.5=46.75%、最下位Idefics-1=42.19%。CLIPがLVLMを一貫して上回り、gapはIN-Artifactで<10%〜Oxford-Petで40-50%。FGVC-Aircraftが最難（最良56.23%）。12公開LVLMのみ評価（プロプライエタリ非評価） | LVLM細粒度分類の代表的評価。多数の後続論文が引用（FG-BMK等） | **一部Yes**（4サブセットがImageNet-21k由来。他5つは独立） | GitHub: gregor-ge/FOCI-Benchmark（MITライセンス、コードで9データセット構成を公開） |
| 2 | **iNaturalist 2021 (iNat21)** (Van Horn+, CVPR, visipedia) | 種の細粒度分類／top-1 acc | 約270万枚・**10,000種**（mini=各種50枚で計50万枚） | 生物種は種間差が微妙で種内変動が大きく、専門家（分類学者）でないと同定困難。日常常識では対応不可 | FINER報告: iNaturalistでGPT-4Vのfine精度≈**18.75%**、LLaVA-1.5(13B)≈**1.56%**（superordinateはほぼ100%）。CascadeVLM論文: iNat18でMAWS CLIP=20.8%, OpenCLIP ViT-G/14=7.5% | FGVCの事実上の標準。CVPR系で定着、多数の派生（iNat24等） | No（独立に構築、ImageNet非依存） | github.com/visipedia/inat_comp、TensorFlow Datasets |
| 3 | **FINER** (Kim & Ji, UIUC, EMNLP 2024 main, arXiv:2402.16315) | 細粒度概念認識＋属性生成／EM | iNat21・FGVC-Aircraft・Stanford Dogs・Stanford Cars・NABirds・CUB-200の6設定 | LVLMの「モダリティギャップ」（同一概念でもテキスト入力と画像入力で応答が乖離）を精密に測定。粒度が細かくなるほど精度が崩壊 | Stanford DogsでLLaVA-1.5のEMが平均**65.58ポイント低下**。iNaturalistのfineでGPT-4V=18.75%、+CoTでも20〜24%程度 | EMNLP 2024採択。細粒度LVLM研究で頻繁に引用 | 素材データの一部（Stanford Dogs等）はImageNet近縁だが独立 | GitHub: wjdghks950/Finer（CC BY-NC 4.0） |
| 4 | **FungiCLEF**（LifeCLEF/CVPR-FGVC, 毎年） | キノコ種の細粒度分類／top-k acc, macro-F1 | 1,400種超（年により変動） | 「正確な同定には微視的検査が必要」と明記。毒キノコと食用の識別など専門知識必須。種間差が極めて微妙 | 2024上位解: private test accuracy=78.4%, macro-F1=0.577（専用モデル・強学習）。ゼロショット汎用VLMは大きく劣る | LifeCLEF/FGVCワークショップの定番タスク | No | Kaggle（FGVCx Fungi / FungiCLEF各年） |
| 5 | **INQUIRE** (Vendrow+, MIT/UCL/Edinburgh, NeurIPS 2024, arXiv:2411.02537) | 専門家クエリのテキスト→画像検索／mAP@50, nDCG | iNat24=**500万枚**・10,000種、250の専門家クエリ、33,000一致 | 生態学者・鳥類学者・昆虫学者・海洋学者らのクエリ。種同定・行動・状態など専門知識と細かな視覚理解が必要 | 「最良モデルでもmAP@50が50%未満」。GPT-4oのリランクAP=**59.6**（全モデル中最高、満点100から大きく乖離） | NeurIPS 2024 Datasets & Benchmarks Track。MIT等の著名グループ、報道あり | No（iNat24は独立構築） | github（visipedia/inquire系）、HuggingFace |
| 6 | **MMMU / MMMU-Pro** (Yue+, CVPR 2024 / ACL 2025, arXiv:2311.16502 / 2409.02813) | 専門分野マルチモーダルQA／accuracy | 11.5K問、6分野30科目183サブフィールド（工学含む） | 大学・専門家レベルの知識が必要。図・化学構造・回路図など専門的視覚要素の理解が必須 | GPT-4V=56%、GPT-4o=69.1%、Gemini Ultra=59%。人間専門家≈90%。MMMU-Proでは各モデル**16.8〜26.9%**、GPT-4oは64.7%→54.0%（4択→10択で-10.7pt） | 最も広く使われるVLM専門知識ベンチ。CVPR 2024、極めて高被引用 | No | HuggingFace: MMMU/MMMU、MMMU-Pro |
| 7 | **FGVC-Aircraft** (Maji+, Oxford VGG, 2013) | 航空機variant分類／平均クラス精度 | 10,000枚・100 variant（102 family, 41 manufacturer） | variant差はわずかな局所形状（A320 vs A321等）。専門知識なしでは区別困難。剛体で画風要因が少なく「概念差」が純粋 | CLIPゼロショット<12%と極端に低い（数値ラベル起因）。LVLM系: CascadeVLM=36.80%、LaBo=32.73%。SOTA専用CNN(AP-CNN)=94.1% | FGVCの古典的標準。多数引用 | No（独立） | robots.ox.ac.uk/~vgg/data/fgvc-aircraft |
| 8 | **Stanford Cars** (Krause+, ICCV-W 2013) | 車のmake/model/year分類／acc | 16,185枚・196クラス | make/model/yearの組合せで、Coupe vs Convertibleなど極めて微細。専門知識が必要 | ゼロショットCLIP≈56.7%。LVLM系: CascadeVLM=85.60%だがモデル間で大きなばらつき（Idefics-1はFOCIで29.42%、Idefics-2は80.25%） | FGVCの古典的標準 | No（ImageNetは車10クラスのみ＝より細粒度） | Stanford AIサイト（近年ホスティング変更あり、要確認） |
| 9 | **CUB-200-2011 / NABirds** (Caltech / Cornell Lab of Ornithology) | 鳥種の細粒度分類／acc | CUB=11,788枚・200種；NABirds=48,562枚・400種超（555カテゴリ） | 鳥種はmale/female・繁殖羽など微細差。専門家（鳥類学者）でも困難。CUBはMechanical Turkのラベル誤り率>4%と報告 | InternVL3: CUBでclass級99.76%→species級61.18%（多肢選択）に低下。SOTA専用モデル≈90% | FGVCで最も基礎的。極めて高被引用 | No | CUB: Caltech；NABirds: Cornell |
| 10 | **OmniBenchmark** (Zhang+, ECCV 2022, arXiv:2207.07106) | 21意味領域の表現汎化評価／linear probe acc | 1,074,346枚・7,372概念・21領域 | WordNet専門知識で領域を定義、概念重複を排除。多様な意味領域への汎化を要求 | 論文は表現学習汎化の評価が主眼で、汎用VLMの「概念的苦戦」の直接数値は限定的 | ECCV 2022 | 概念はImageNet-21k/Wikidata由来だが重複排除 | zhangyuanhan-ai.github.io/OmniBenchmark |
| 11 | **RP2K / Products-10K**（小売SKU） | SKU級細粒度分類／acc | RP2K=約35〜50万枚・約2000 SKU；Products-10K=1万SKU | 同一ブランドの容量・味違いなど、見た目酷似のSKUを区別。工業製品的な「バリアント識別」に近い | RP2K論文: 「SOTA細粒度手法も単純ResNetを上回らなかった」。自己教師学習で最大99.22%（フルFT）の報告もあり難易度は前処理依存 | 小売認識で定着 | No | RP2K: arXiv:2006.12634；Products-10K: products-10k.github.io |
| 12 | **MCB (Mechanical Components Benchmark)** (Kim+, ECCV 2020) | 機械部品の分類・検索／acc | 大規模3D CADモデル（ICS国際分類標準準拠） | 機械部品の注釈には工学知識が必要。ISO国際分類標準に基づく専門的分類体系 | **3D形状記述子の評価が主眼で、汎用VLMの2D画像分類での苦戦は未報告** | ECCV 2020 | No | GitHub: stnoah1/mcb |
| （参考） | **GPQA / GPQA Diamond** (Rein+, NYU/Anthropic, 2024) | 大学院レベル科学QA／acc | 448問（Diamond=198問） | 「Google-proof」。PhD専門家でも65%、非専門家は30分のWeb検索でも34% | GPT-4ベースライン=39%。人間PhD=65〜74% | 科学推論ベンチの標準 | N/A（画像なし・テキスト中心） | HuggingFace/GitHub |

### 上位5件の意匠特許ドメイン接続性：利点・懸念

**1. FOCI（最推奨）**
- 利点: 「多肢選択で近縁カテゴリを区別させる」フォーマットが意匠特許の「見た目が似た工業製品カテゴリの識別」と構造的に一致。人工物（man-made objects, 2631クラス）サブセットを含み、工業製品ドメインに最も近い。CLIP＞LVLMという「モダリティギャップ」の枠組みは、LoRAで整合を改善したという論文の主張を直接支える。コードが公開されており多肢選択の再現が容易。
- 懸念: 4サブセットがImageNet-21k由来のためImageNet-freeを厳格に求める場合は残り5サブセット（航空機・車・料理・花・ペット）に限定する必要がある。GPT-4V/Geminiは原論文で未評価（≤7B級公開LVLM 12個のみ）なので、汎用VLM比較は自前で追加測定が必要。

**2. iNaturalist（FGVC）**
- 利点: 「専門知識がないと人間でも見分けられない」という概念的難しさの最も明確な例。10,000クラスの大規模で、汎用VLMが壊滅的（GPT-4V fine≈18.75%）という数値が複数論文にある。ImageNet-freeでLoRA微調整の効果を示しやすい。
- 懸念: 対象が生物種であり、意匠特許の「工業製品」とドメインが大きく異なる。図面（線画）ではなく実写。意匠ドメインへの接続は「細粒度・専門知識が必要」という抽象レベルでの類推に留まる。

**3. FINER**
- 利点: 「モダリティギャップ」を精密に定量化しており、LoRAで視覚-意味整合を改善するという主張の理論的支柱になる。GPT-4Vの数値（EM 65.58pt低下等）が引用しやすい。
- 懸念: 素材が動物・車・鳥中心で工業製品ドメインではない。属性生成評価が含まれ、単純な分類より実装がやや複雑。

**4. FungiCLEF**
- 利点: 「専門知識（微視的検査）が必須」「毒/食用の誤りが致命的」という難しさの説得力が非常に高い。毎年のコンペで著名性・リーダーボードが明確。
- 懸念: キノコ種という極めて特殊なドメインで、意匠特許との接続は弱い。汎用VLMの直接スコアは論文により散在し、統一比較が乏しい。

**5. MMMU / MMMU-Pro**
- 利点: 「専門知識が本質的に必要」で最も著名。工学（Tech & Engineering）分野を含み、専門用語・図面理解が問われる。GPT-4V/GPT-4o/Geminiの数値が豊富で権威ある比較が可能。
- 懸念: タスクが「分類」ではなく「推論を伴うQA」。意匠特許の「図面→製品名/カテゴリ」という分類タスクとは性質が異なり、直接の手法比較には無理がある。LoRA微調整の効果を示す土俵としては不適合の可能性が高い。

## Recommendations

**段階的な採用方針:**

1. **第一段階（主軸）: FOCIを採用し、特に人工物（man-made objects）サブセットとFGVC-Aircraft/Stanford Carsサブセットを重点評価する。** これらは「工業製品」「専門的variant識別」という意匠特許ドメインに最も近く、多肢選択フォーマットが図面分類タスクに転用しやすい。**閾値:** 自前のQwen3-VL-4B+LoRAが、原論文の最良LVLM（Idefics-2, 64.13%）または同規模のQwen-VL-Chat（62.41%）を上回れば「概念的難しさで汎用VLMを超えた」と主張できる。特にFGVC-Aircraftサブセット（原論文最良56.23%）は「概念差が純粋」なため訴求力が高い。

2. **第二段階（汎用性の補強）: iNaturalist（またはFOCI経由のFGVC-Aircraft）で、GPT-4V/GPT-4oの公表値（fine精度≈18.75%等）を参照点に、LoRA微調整が「専門知識ギャップ」を埋めることを示す。** ImageNet-freeを厳守する場合はiNaturalist・FGVC-Aircraft・FungiCLEFを選ぶ（いずれもImageNet非依存）。

3. **第三段階（理論的裏付け）: FINERの「モダリティギャップ」フレームとFOCIの「エンコーダ-LLM整合不足」の主張を引用し、LoRAが視覚エンコーダとLLMの整合を改善するという機序を論証する。** MMMU/MMMU-Proは「専門知識が必要なタスクで汎用VLMが苦戦する」一般的文脈の引用にとどめ、直接のスコア競争には使わない。

4. **意匠特許との「ドメイン一致」を最重視する場合**は、RP2K/Products-10K（小売SKUのvariant識別）を補助的に検討。ただしこれらは「汎用VLMが概念で苦戦」を主眼にした評価ではないため、自前でGPT-4V/CLIPベースラインを測定する必要がある。

**方針を変える基準:** もし「工業製品ドメインでの実写画像・VLM評価」の既存の著名ベンチマークが新たに見つかれば（例: 機械部品の2D画像VLM分類）、それを主軸に切り替えるべき。現状はそのような「工業部品×VLM×概念難しさ」を三拍子揃えた著名ベンチマークは確認できず、FOCIの人工物サブセットが最も近い代替である。

## Caveats

- **CLIPがFOCIでLVLMを上回る「平均差」の単一数値は原論文に存在しない。** 論文はFigure 3の散布図と、データセット別のgap範囲（IN-Artifactで<10%〜Oxford-Petで40-50%）のみを示す。「CLIPが平均でX%上回る」という数値主張はできないので注意（定性的には要旨が "dramatically better" と明言）。
- **FOCIの総問題数は原論文に明記されていない。** 5つの標準データセットは全テスト分割、4つのImageNet-21kサブセットは各クラス10枚使用（合計約5.5万問と概算できるが、著者は総数を示していない）。
- **FOCI原論文はGPT-4V/Geminiなどプロプライエタリモデルを評価していない**（≤7B級の公開LVLM 12個のみ。要旨: *"We benchmark 12 public LVLMs on FOCI"*）。汎用VLMとの比較を論文に載せるには自前測定が必要。
- iNaturalistのVLMスコアは論文・設定（クラス数、mini/full、プロンプト、EM/多肢選択）により大きく変動する。FINERのGPT-4V=18.75%は特定の評価設定（fine granularity, EM）での値であり、他論文の数値と直接比較する際は設定の統一が必要。
- **MCB（機械部品）は3D CAD形状の分類・検索ベンチマークであり、2D画像でのVLM評価は行われていない。** 意匠図面（2D線画）への転用は容易でなく、「汎用VLMが概念で苦戦」を示すデータもない。安易に「工業製品のVLMベンチマーク」として引用しないこと。
- 依頼者が既知候補として挙げた新しいベンチマーク（FG-BMK, MVI-Bench, MechVQA等）は極めて新しく、被引用・定着度が未確立。著名性を重視するなら本表の上位を優先すべき。なお MechVQA (arXiv:2605.30794) は付番から将来日付の可能性があり、実在・詳細を一次情報で再確認することを推奨する（本調査では確証を得られなかった）。
- 「専門知識がないと人間でも間違える」ことが論文で最も明示的なのはGPQA（テキスト：非専門家34% vs PhD 65%）・iNaturalist/FungiCLEF（種同定）・CUB（Turkラベル誤り率>4%）である。意匠特許の「専門知識が必要」という主張の傍証として引用可能。