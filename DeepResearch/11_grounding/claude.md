# 切り出し済み単一物体の「命名」段階に関する研究調査:上位カテゴリ不明・質問文なし・長尾対象への転用可能性

調べた範囲では、「上位カテゴリを与えず、質問文もなく、画像1枚だけから珍しい物体の名前を出す」設定をそのまま解いている査読付き研究はありませんでした。現状いちばん近いのは、CaSED(NeurIPS 2023)の「外部キャプションDBを検索して候補名を作る」方式と、FineR/FiNDRの「属性を言語化してLLMに名前を推論させる」方式の2系統です。ただしFineR/FiNDRは「メタクラス内の細粒度」を前提にしています。また、「識別手がかりが全体形状にあるか局所部位にあるかを入力ごとに判断して統合重みを変える」仕組みを明示的に扱った研究は見つかりませんでした。これは提案手法にとって空白地帯です。

## TL;DR
- **命名の仕組みは6型に整理できますが、上位カテゴリを本当に前提にしないのは少数です。** 語彙なしで名前を生成するのはCaSED(検索型)、LMMの自由生成(Conti et al., ICCV 2025の評価)、FineR/E-FineR/FiNDR(属性→LLM推論)です。FineR系とFiNDRは「メタクラス内」を前提としており、SARE・RAR・FuDD・CHiLS・階層比較法はいずれも候補語彙を必要とします。
- **「手がかりの在り処が対象ごとに違う」への直接の答えは「明示的に扱った研究は無い」です。** 近い仕組みは次の4つです:入力ごとにエントロピーでビュー(クロップ)を重み付けするAWT、判定の曖昧さに応じて推論を起動するSAREのトリガー、画像ごとの紛らわしい候補に応じて差分属性を選ぶFuDD、領域注意βで部位を入力依存に重み付けするPart Prototype Network。全体と局所の統合は、固定平均(microCLIP)かカスケード(SARE)が主流です。
- **転用の第一候補はCaSED(凍結・学習不要でそのまま動く)とFiNDR/FineR(メタクラス推定段を外す改造が必要)です。** 事後学習設定ではFine-R1(ICLR 2026)の「視覚分析→候補→比較→予測」型CoT+強化学習が有力です。評価はConti et al.のTI/LI/SS/CS指標群をそのまま採用すべきです。

## Key Findings

### 1. 仕組みの分類(入力/判断の信号/学習の要否)

**型A:部分と全体の関係を使う手法**
- **FineR(ICLR 2024)**:画像からVQAモデルで部位レベルの視覚属性をテキストとして抽出し、LLMに渡して下位カテゴリ名を推論させます。名前の候補は、VLMを使うNoisy Name Denoiserで絞り込みます。入力は少数の無ラベル画像、判断の信号は部位属性テキスト+LLMの世界知識+CLIP類似度で、学習は不要です。公開された中間結果には「super-class」が含まれており、最初にメタクラスを推定する段があります。
- **Part Prototype Network(PPN, CVPR 2024 Workshops)**:VinVL検出器の上位30領域(R=30、2048次元)を入力とし、領域ごとに属性注意αでクラス属性埋め込みを組み立て、領域注意βで重み付けして双線形スコアを合計します。人手のクラス属性ベクトルとword2vecが必要で、学習も必要です(CUB上でGZSL H=66.8)。部位ごとのプロトタイプ照合の代表例ですが、閉じたクラス集合(seen/unseen)を前提にしています。
- 部分間の関係を構造(グラフ等)として扱う単一物体の命名研究は、2022年以降のトップ会議では見つかりませんでした。行動認識では、部位レベルのアフォーダンスグラフを使うEgoAffordがあります。

**型B:属性・記述を経由する手法**
- **Classification by Description(Menon & Vondrick, ICLR 2023 Oral)**:GPT-3で各クラスの記述子(「虎なら縞、爪…」)を生成し、画像と記述子のCLIP類似度でクラスを決めます。凍結・学習不要ですが、候補クラスのリストが必要です。
- **Conti et al.(ICCV 2025)のCoT**:LMMに属性を分解させてからラベルを出させると、細粒度での精度が上がります。
- **Fine-R1(ICLR 2026)**:原文で \"visual analysis, candidate sub-categories, comparison, and prediction\" と書かれる形(視覚分析→候補下位カテゴリ→比較→予測)のCoTデータでSFTしたあと、Triplet Augmented Policy Optimization(同一クラス内と異クラス間の軌跡拡張)で強化学習します。He, Geng, Pengは動機として、既存MLLMが \"tend to overfit to seen sub-categories and generalize poorly to unseen ones\"(既知の下位カテゴリに過適合し、未知のものへの汎化が弱い)ことを挙げています。そのうえで、4-shotの学習で未知の下位カテゴリにも汎化すると報告しています。

**型C:機能・用途から推論する手法**
- 単独物体の命名を機能・用途から推論する研究は、調べた範囲では**見つかりませんでした**。「affordance」で検索して出てきたのは、アフォーダンス・グラウンディング(位置決め。例:One-Shot Open Affordance Learning, CVPR 2024; A4-Agent; TokAG)とロボット操作だけで、対象外です。

**型D:外部知識・検索を使う手法**
- **CaSED(NeurIPS 2023)**:入力画像で外部の視覚言語DBから関連キャプションを検索し、そこから候補カテゴリ名を抽出します。そのうえで、画像→テキストの類似度と、検索キャプション重心→テキストの類似度で分類します。凍結・学習不要で、語彙を与えません。
- **RAR**:CLIPベースの検索器でカテゴリごとの明示的メモリを作り、推論時にtop-kを検索してMLLMに順位付けさせます。13,204クラスのV3Detでも評価していますが、メモリ構築にはカテゴリ名が必要です。
- **OVEN(ICCV 2023)**:6,063,945件のWikipedia実体から1つを選ぶタスクです。入力は画像+意図を示すテキストクエリで、質問文ありの設定です。

**型E:比較で決める手法**
- **FuDD(ICLR 2024)**:まず画像ごとにVLMで紛らわしいクラス群を特定し、LLMにそれらを見分ける差分記述を生成させて再分類します(例:スズメとミソサザイは色ではなく嘴の形で区別する)。学習不要ですが、候補語彙が必要です。
- **ChatGPT-Powered Hierarchical Comparisons(NeurIPS 2023)**:LLMでクラスを再帰的に比較・グループ化して階層を作り、上から下へ画像とテキストの埋め込みを比較して降りていきます。学習不要で、候補語彙が必要です。

**型F:段階を踏む手法(粗→細)**
- **CHiLS(ICML 2023)**:クラスごとにサブクラス集合を(既存の階層またはGPT-3で)作り、サブクラス空間でゼロショット分類してから親クラスへ写像します。既知の階層がある場合の改善幅は版によって表現が異なり、OpenReview版アブストラクトは \"gains of over 30%\"(30%超)、arXiv/ICML版の貢献節は \"up to 30% accuracy gains\"(最大30%)としています。階層が無い場合の改善は小さめです。
- **SARE(arXiv 2026)**:System 1(CLIPプロトタイプ検索)で候補をtop-10に絞り、必要なときだけSystem 2(LVLMによる推論)を起動するカスケードです。
- **Hedging Your Bets(Deng et al., CVPR 2012)**:意味階層上で、不確かなときは上位概念に退避して「正確さと特異度」のトレードオフを最適化します(DARTS)。

### 2. 上位カテゴリ・語彙を与えない設定の研究
- **Vocabulary-free Image Classification(CaSED)**:タスク定義そのものが「既知語彙なしに、制約のない言語意味空間のクラスを割り当てる」ことです。照合先は外部DBから検索したキャプション由来の候補名で、上位カテゴリは**前提にしていません**。評価は、予測クラスと正解ラベルの意味的一致を測る独自の指標群で行います。
- **LMMの開放世界分類(Conti et al., ICCV 2025)**:「What is the main object in the image?」と尋ねて自由記述ラベルを出させ、13モデルを10ベンチマークで評価しています。支配的な誤りは**過度に一般的な予測(正しい上位語を答えてしまう)**で、細粒度になるほど性能が急落すると報告されています。上位カテゴリは前提にしていませんが、最小限の質問プロンプトは使っています。
- **FineR/E-FineR/FiNDR**:「語彙なし」をうたいますが、FiNDRは「メタクラス内の視覚的に似たカテゴリを識別する」と明記しています。**上位カテゴリ(メタクラス)は前提**で、データセット単位の無ラベル画像群からクラス集合を作ってから分類します。
- **Efficient VF-FGVR(Kuchibhotla et al., arXiv 2025)**:MLLMで無ラベル訓練画像ごとに候補ラベル集合を作り、GMMでclean/noisyに分けたうえで分類器を学習します。学習が必要で、細粒度ドメイン内が前提です。
- **長尾・未知の扱い**:FineRは独自のPokemon-10データセットで、正解10カテゴリ中7カテゴリを発見しました。OVENは訓練で見ていない実体(UNSEEN)を含む600万候補から選ばせる設計で、PaLI-17Bのテスト調和平均は20.2、検索エンジンを使う人間は77.7でした。事前学習に無い対象に対しては、外部知識(Wikipedia/キャプションDB)への検索が唯一の体系的な手段になっています。
- **オープン語彙検出の「切り出し後の分類部分」**:RARは検出データセットで提案領域を切り出してぼかし、CLIP検索→MLLM順位付けで分類しています。照合先はカテゴリ名から作ったメモリです。

### 3. 第3節の3つの問いへの直接の回答
- **識別部位が対象ごとに違うことの扱い**:**明示的な研究は無い**という結論です。SAREは「同じ全体精度70%でもサブカテゴリごとに必要な信頼度閾値が大きく異なる」ことを示し、判定が難しいかどうかがサンプルごとに不均一であることを扱っていますが、手がかりが「どこにあるか」は扱っていません。FuDDは画像ごとの紛らわしい候補に応じて「どの属性で区別するか」を変えるので、言語側では最も近いものです。PPNの領域注意βは入力依存の部位重み付けです。
- **全体と局所の統合の仕方**:(a) **固定の重み付け混合**:microCLIPは全体の[CLS]ロジットと局所の[FG]ロジットを1/2ずつの単純平均で融合します。アブレーションでは全体のみ17.26%、局所のみ57.84%、平均64.27%でした。(b) **選択(カスケード)**:SAREは確信度が十分ならSystem 1の全体埋め込み検索で確定し、不十分ならSystem 2で局所の手がかりを推論させます。(c) **ビューの入力依存な重み付け**:AWTは画像変換で作った複数ビュー(クロップ)を予測エントロピーで動的に重み付けし、最適輸送で画像とテキストの距離を計算します。(d) **階層的処理**:CHiLS・階層比較法です。
- **統合の重みを入力ごとに変える仕組み**:**ある(ただし全体と局所の二者択一としてではない)**。AWTの重みは各ビューの予測エントロピーから、microCLIPの多視点クロップの重みは全体埋め込みとのsoftmax類似度から決まります(トークン融合そのものは固定平均)。SAREのトリガーは、融合確信度、Hoeffding型の履歴ペナルティ、候補間エントロピーの3つから推論を起動するかどうかを決めます。PPNのβは領域特徴から学習されます。「このクラスは輪郭で決まる、このクラスは内部の小部品で決まる」という判断を重みとして明示的に推定する手法は**見つかりませんでした**。

### 4. 輪郭だけでは決まらない対象の扱い
- 箱状の機器や筒状の部品のように、外形が単純で形だけでは種類が決まらない対象に焦点を当てた命名研究は、**見つかりませんでした**。検索範囲は、細粒度認識、語彙なし分類、LMMの開放世界分類、アフォーダンス関連です。
- 大きさ・素材・文脈のように画像に写りにくい情報を明示的に補う単独物体の命名研究も、**見つかりませんでした**。間接的な手段は3つあります:OVENのテキストクエリ(ただし質問文ありの設定)、CaSEDやRARの外部検索(キャプションが文脈を運ぶ)、Classification by DescriptionやFineRの属性言語化(素材・色を記述として明示できる)です。

### 5. 評価
- **完全一致**:SARE・RAR・CHiLS・FuDDなど語彙ありの手法はtop-1精度を使います。OVENは約600万実体中の厳密一致で、SEEN/UNSEEN精度の調和平均をEntity SplitとQuery Splitで計算し、さらにそれらの調和平均を取ります。
- **語彙への写像**:CaSEDとFineR系は生成名をクラス集合に写像してから精度を測ります。"Multimodal LLMs as Image Classifiers"(arXiv 2026)は、開放世界出力をテキストエンコーダで埋め込み、最近傍のクラス名に写像します。OVENのPaLIベースラインは生成名をBM25でWikipediaタイトルに写像します。
- **埋め込み類似度・LLM判定**:Conti et al.は4指標を提案しています。Text Inclusion(文字列包含)、Llama Inclusion(LLMによる判定)、Semantic Similarity(Sentence-BERT埋め込みの連続値)、Concept Similarity(文の部分単位)です。Fine-R1の開放世界評価は相対的意味類似度で報告されています。
- **人手評価**:OVENにはhuman evalの分割(24,867例)があります。
- **データセット**:ほぼすべての研究が「単独物体が画面の大部分を占める」細粒度データセットを使っています:CUB-200、Stanford Dogs/Cars、FGVC-Aircraft、Oxford Pets/Flowers、Birdsnap、Food-101です。これらはいずれも単一ドメインで、ラベルは種・車種・機種の粒度です。上位カテゴリが混在する単独物体データセットとしては、Caltech-101やImageNet系が使われています。**工業部品や箱状機器のような「形が単純で長尾」の単独物体データセットは、評価に使われていません。**

## Details

### 論文一覧表

| 論文名 | 会議・年 | 査読 | 入力(切り出し済みか) | 上位カテゴリ前提 | 語彙前提 | 判断の信号 | 学習 | 評価方法 | 実装公開 |
|---|---|---|---|---|---|---|---|---|---|
| Vocabulary-free Image Classification (CaSED) | NeurIPS 2023 | 有 | 画像全体(単一物体中心) | 無 | 無(外部DB) | 検索キャプション由来の候補+画像/テキスト類似度 | 不要 | 意味一致指標群 | 有 |
| On LMMs as Open-World Image Classifiers | ICCV 2025 | 有 | 画像全体+最小限の質問 | 無 | 無 | LMMの自由生成(CoT) | 不要(評価研究) | TI/LI/SS/CS | 有 |
| FineR | ICLR 2024 | 有 | 画像全体(少数無ラベル群) | 有(メタクラス推定) | 無 | 部位属性テキスト→LLM推論+CLIP | 不要 | 語彙写像後の精度 | 有 |
| E-FineR | ICCV 2025 Workshop | 有(WS) | 同上 | 有 | 無 | LLM文脈付与+ソフトフィルタ | 不要 | 同上 | 有(論文記載) |
| FiNDR | CVPR 2026 | 有 | 同上 | 有(メタクラス内) | 無 | 推論LMMの候補→VLM選別→軽量分類器 | 軽量分類器の構築 | 同上 | 有 |
| Efficient VF-FGVR | arXiv 2025 | 無 | 無ラベル訓練画像群 | 有(ドメイン内) | 無 | MLLM候補集合+ノイズラベル学習 | 要 | 精度 | 未確認 |
| RAR | IEEE TIP 2026(arXiv 2024) | 有 | 画像/切り出し領域 | 無 | 有(メモリ) | CLIP検索top-k+MLLM順位付け | 不要(メモリ構築) | top-1精度 | 未確認 |
| SARE | arXiv 2026 | 無 | 画像全体 | 無 | 有(k-shot支援集合) | 融合確信度トリガー+経験ライブラリ付き推論 | 不要(パラメータ更新なし) | top-1精度(14データセット) | 未確認 |
| Classification by Description | ICLR 2023 | 有 | 画像全体 | 無 | 有 | 記述子とのCLIP類似度 | 不要 | top-1精度 | 有(未検証) |
| FuDD | ICLR 2024 | 有 | 画像全体 | 無 | 有 | 画像ごとの曖昧クラス間の差分記述 | 不要 | top-1精度(12データセット) | 有 |
| ChatGPT-Powered Hierarchical Comparisons | NeurIPS 2023 | 有 | 画像全体 | 無 | 有 | LLM構築の階層を降りる比較 | 不要 | top-1精度 | 有 |
| CHiLS | ICML 2023 | 有 | 画像全体 | 無 | 有(親クラス) | サブクラス空間での分類→親へ写像 | 不要 | top-1精度 | 有 |
| AWT | NeurIPS 2024 | 有 | 画像全体(複数ビュー生成) | 無 | 有 | エントロピー重み付けビュー+最適輸送 | 不要(ゼロショット時) | top-1精度 | 有 |
| microCLIP | ACL Findings 2026 | 有 | 画像全体 | 無 | 有 | [CLS]と[FG]ロジットの固定平均 | 要(教師なし適応) | top-1精度(13データセット) | 有 |
| Part Prototype Network | CVPR 2024 Workshops | 有(WS) | VinVL上位30領域 | 無 | 有(属性付きクラス) | 領域×属性注意の双線形照合 | 要 | GZSL調和平均 | 未確認 |
| Fine-R1 | ICLR 2026 | 有 | 画像全体 | 無 | 無(開放世界評価あり) | CoT SFT+三つ組拡張RL | 要(4-shot) | 閉世界精度+相対意味類似度 | 有(github.com/PKU-ICST-MIPL/FineR1_ICLR2026) |
| OVEN | ICCV 2023 | 有 | 画像+テキストクエリ | 無 | 無(約606万実体) | 生成+BM25写像/CLIP検索 | 要(ベースライン) | SEEN/UNSEEN調和平均 | 有 |

※「実装公開」は論文・リポジトリの記載に基づきます。「未確認」は今回の調査でリポジトリを確認できなかったものです。

### 数値の出典と注意
- SAREは平均精度87.68%(12データセット)と報告しており、FineDeficsを15.88ポイント、VT-FSLを1.64ポイント上回るとしています。ただし未査読で、k=3-shotのラベル付き支援集合を使うため、「学習不要」でも語彙は閉じています。同表ではFineRが平均60.60%で、SAREの設定ではCLIP-B/32単体(57.80%)をわずかに上回る程度です。
- FiNDRの「従来比で相対最大18.8%改善」「正解名を使うゼロショットを上回る」は、アブストラクトでの主張です。
- Fine-R1の「開放世界で相対意味類似度74.80%、Qwen2.5-VL-7B比+23.75%」は、二次要約サイト(Liner)の \"Fine-R1-7B sets a new state-of-the-art with 74.80% relative semantic similarity, representing a substantial improvement of 23.75% over Qwen2.5-VL-7B\" という記載によるものです。原論文の表では確認できておらず、未検証の数値として扱ってください。
- microCLIPは13データセット平均68.68%(ViT-B/32)で、ゼロショットCLIPの61.34%、DPAの65.78%を上回ると報告しています。

### 書誌・実装情報(第6項に対応)

| 正式タイトル | 著者 | 会議・年 | arXiv | 実装 |
|---|---|---|---|---|
| Vocabulary-free Image Classification | Conti, Fini, Mancini, Rota, Wang, Ricci | NeurIPS 2023 | 2306.00917 | github.com/altndrr/vic |
| On Large Multimodal Models as Open-World Image Classifiers | Conti, Mancini, Fini, Wang, Rota, Ricci | ICCV 2025 | 2503.21851 | github.com/altndrr/lmms-owc |
| Democratizing Fine-grained Visual Recognition with Large Language Models | Liu, Roy, Li, Zhong, Sebe, Ricci | ICLR 2024 | 2401.13837 | github.com/OatmealLiu/FineR |
| Vocabulary-free Fine-grained Visual Recognition via Enriched Contextually Grounded Vision-Language Model | Demidov ほか | ICCV 2025 Workshop (MMFM) | 2507.23070 | 論文に記載 |
| Thinking Beyond Labels: Vocabulary-Free Fine-Grained Recognition using Reasoning-Augmented LMMs | Demidov, Zaheer, Han, Thawakar, Anwer | CVPR 2026 | 2512.18897 | github.com/demidovd98/FiNDR |
| Efficient Vocabulary-Free Fine-Grained Visual Recognition in the Age of Multimodal LLMs | Kuchibhotla, Kancheti, Reddy, Balasubramanian | arXiv 2025 | 2505.01064 | 未確認 |
| RAR: Retrieving And Ranking Augmented MLLMs for Visual Recognition | Liu, Sun, Zang, Li, Zhang, Dong, Xiong, Lin, Wang | IEEE TIP 2026(arXiv 2024) | 2403.13805 | 未確認 |
| SARE: Sample-wise Adaptive Reasoning for Training-free Fine-grained Visual Recognition | Yang, He, Pan, Su ほか | arXiv 2026 | 2603.17729 | 未確認 |
| Visual Classification via Description from Large Language Models | Menon, Vondrick | ICLR 2023 | 2210.07183 | 未確認 |
| Follow-Up Differential Descriptions: Language Models Resolve Ambiguities for Image Classification | Esfandiarpoor, Bach | ICLR 2024 | 2311.07593 | github.com/BatsResearch/fudd |
| ChatGPT-Powered Hierarchical Comparisons for Image Classification | Ren, Su, Liu | NeurIPS 2023 | 2311.00206 | github.com/Zhiyuan-R/ChatGPT-Powered-Hierarchical-Comparisons-for-Image-Classification |
| CHiLS: Zero-Shot Image Classification with Hierarchical Label Sets | Novack, McAuley, Lipton, Garg | ICML 2023 | 2302.02551 | github.com/acmi-lab/CHILS |
| AWT: Transferring Vision-Language Models via Augmentation, Weighting, and Transportation | Zhu, Ji, Zhao, Wu, Wang | NeurIPS 2024 | 2407.04603 | github.com/MCG-NJU/AWT |
| microCLIP: Unsupervised CLIP Adaptation via Coarse-Fine Token Fusion for Fine-Grained Image Classification | Silva, Ali, Arora, Khan | ACL Findings 2026 | 2510.02270 | github.com/sathiiii/microCLIP |
| 'Eyes of a Hawk and Ears of a Fox': Part Prototype Network for Generalized Zero-Shot Learning | Feinglass, Thiagarajan, Anirudh, Jayram, Yang | CVPR 2024 Workshops | 2404.08761 | 未確認 |
| Fine-R1: Make Multi-modal LLMs Excel in Fine-Grained Visual Recognition by Chain-of-Thought Reasoning | He, Geng, Peng | ICLR 2026 | 2602.07605 | github.com/PKU-ICST-MIPL/FineR1_ICLR2026 |
| Open-domain Visual Entity Recognition: Towards Recognizing Millions of Wikipedia Entities | Hu, Luan, Chen, Khandelwal, Joshi, Lee, Toutanova, Chang | ICCV 2023 | 2302.11154 | github.com/edchengg/oven_eval |
| Multimodal Large Language Models as Image Classifiers | Kisel, Volkov, Janouskova, Matas | arXiv 2026 | 2603.06578 | 未確認 |
| From Large Scale Image Categorization to Entry-Level Categories | Ordonez, Deng, Choi, Berg, Berg | ICCV 2013 | — | — |
| Hedging Your Bets: Optimizing Accuracy-Specificity Trade-offs in Large Scale Visual Recognition | Deng, Krause, Berg, Fei-Fei | CVPR 2012 | — | — |
| Coarse Blobs or Fine Edges? Evidence That Information Diagnosticity Changes the Perception of Complex Visual Stimuli | Oliva, Schyns | Cognitive Psychology 1997 | — | — |

## Recommendations

### 転用候補5件
1. **CaSED(凍結・学習不要)**:**そのまま動きます。** 上位カテゴリも質問文も要らず、画像埋め込みで外部DBを検索するだけです。変更が必要なのはDBで、珍しい対象を扱うには、その対象名を含むキャプションや製品カタログをDBに追加する必要があります。検索の照合は画像全体の埋め込みなので、面の内側の小部品で決まる対象には弱いと予想されます(推測)。
2. **FiNDR/FineR(凍結・学習不要)**:**改造が必要です。** 両者ともメタクラス内の細粒度を前提にし、データセット単位の無ラベル画像群からクラス集合を作ります。そのため、(a) メタクラス推定段を外すか、上位語を複数仮説として並列に保持すること、(b) 画像1枚単位で「属性の言語化→LLMによる命名候補→VLMによる検証」を回すように改めること、が必要です。部位属性の言語化は「内部の小部品」を拾う入口になり得ます。
3. **FuDD(凍結・学習不要)**:**候補語彙の供給源を差し替えれば動きます。** 候補リストの代わりに、CaSEDかLMMの自由生成のtop-k名を「紛らわしい候補」として使い、LLMに差分記述を作らせて再照合します。画像ごとに「どの属性(輪郭か内部部品か)で区別するか」が変わるので、手がかりの在り処の可変性を言語側で吸収できる、最も安価な構成です。
4. **AWT(凍結・学習不要)**:**語彙が必要ですが、ビュー重み付けの部分は単独で転用できます。** 画像全体と複数の局所クロップを作り、各ビューの予測エントロピーで重みを決めれば、「輪郭で決まる対象では全体ビューが、小部品で決まる対象では局所クロップが低エントロピーになる」ことを利用できます。その際、エントロピーの基準にする候補集合はCaSEDなどで動的に作る必要があります。
5. **Fine-R1(事後学習)**:**事後学習設定では最有力です。** 「視覚分析→候補下位カテゴリ→比較→予測」の形のCoT SFTと、クラス内・クラス間の三つ組RLを、上位カテゴリが混在する単独物体データで行います。現状は細粒度ドメイン内の評価なので、上位語から下位名まで降りるCoT(例:「工具→レンチ→トルクレンチ」)にデータ形式を拡張し、報酬を意味類似度(SS/LI)にする変更が必要です。

### 評価設計への推奨
- Conti et al.の4指標(TI/LI/SS/CS)を主指標にし、「過度に一般的な予測」を別枠で数えるべきです。同研究が示したとおり、完全一致だけでは上位語の正答が全誤答扱いになり、手法差を見誤ります。
- 階層上の部分点(正しい上位語で止まる)は、Deng et al.(2012)の正確さと特異度のトレードオフの枠組みで評価すると、長尾対象での「分からないときの退避」を正当に評価できます。

## 着想として面白いもの(実用性とは別に)
- **診断性に基づく尺度選択(Oliva & Schyns, 1997; Schyns & Oliva, 1999)**:人間は粗い塊(低空間周波数)と細かいエッジ(高空間周波数)を両方同時に登録しています。そのうえで、課題にとって診断的な尺度を柔軟に選ぶことが示されました。同じハイブリッド画像でも、課題が変わると知覚される尺度が変わります。これは「手がかりの在り処が対象ごとに違う」問題への認知科学的な答えで、「候補仮説を立ててから、その仮説を区別するのに診断的な尺度を選ぶ」というトップダウン型の重み決定の発想源になります。
- **エントリーレベル・カテゴリ(Ordonez et al., ICCV 2013, Marr賞)**:人が物体を呼ぶ名前は、分類器の葉ノードではなく、Webのn-gram頻度で測る「自然さ」と階層上の距離のバランスで決まるとし、それを予測するモデルを初めて学習した研究です。語彙なし命名で「どの粒度の名前を出すか」を決める問題に直結します。
- **Hedging Your Bets(Deng et al., CVPR 2012)**:不確かなときは上位概念に退避して情報量を最大化する、という誤り率保証付きの枠組みです。LMMが「過度に一般的な予測」をしてしまう問題を、逆に制御された退避として設計し直す視点を与えます。
- **SAREのSystem 1/System 2と誤り経験ライブラリ**:判定の難しさに応じて推論の深さを変え、過去の失敗から「決め手となる属性」の規則を蒸留して再利用します。「この種の対象は内部部品で決まる」という知識を、経験として蓄積する仕組みに転用できます。
- **FuDDの差分記述**:「識別に効く属性は、対象そのものではなく競合候補との関係で決まる」という発想です。手がかりの在り処が一定でない理由を、対象の性質ではなく候補集合の性質として説明し直せます。

## Caveats
- 検索はweb検索で合計約18回に限られ、2022〜2026年のトップ会議を中心に調べました。機能・用途からの命名、形状が単純な物体、大きさ・素材の補完については「見つからなかった」と書いていますが、存在しないことの証明ではありません。
- SARE、Efficient VF-FGVR、Multimodal LLMs as Image Classifiersは未査読のarXivです。E-FineRとPPNはワークショップ論文です。RARはPubMedの書誌によるとIEEE Transactions on Image Processing(2026年、35巻388–401頁、doi:10.1109/TIP.2025.3644175)に掲載された査読付きジャーナル論文です。
- 各手法の数値は論文ごとに設定(バックボーン、shot数、データセット)が異なり、直接比較はできません。とくにSAREの表中のFineR等の数値は、SARE著者による再現値です。
- 調べた研究のほぼすべてが、単一ドメインの細粒度データセット(鳥・犬・車・航空機・花)で評価されています。上位カテゴリが混在し、形が単純な長尾対象での性能は未知で、ここでの転用可能性の判断は仕組みからの推測を含みます。