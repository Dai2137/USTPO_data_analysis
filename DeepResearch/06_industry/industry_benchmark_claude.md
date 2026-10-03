# 意匠特許ドメイン特化VLMの評価に使える「難しい」公開画像ベンチマーク調査

## TL;DR（要点）
- 条件（工業製品・専門機器ドメイン／単一ラベル出力寄り／SOTA・汎用VLMが伸び悩む／公開・論文あり）に最も合致するのは **FOCI（Geigle, Timofte, Glavaš, "African or European Swallow? Benchmarking Large Vision-Language Models for Fine-Grained Object Classification," EMNLP 2024, arXiv:2406.14496, pp. 2653–2669）** と **RP2K**、次いで **Products-10K / iMaterialist-Product 2019**、専門ドメイン図面VQAとしての **MechVQA（ICML 2026, arXiv:2605.30794）**、テキスト↔画像検索の **ILIAS（Kordopatis-Zilos et al., CVPR 2025, arXiv:2502.11748）** である。FOCIは分類を4択多肢選択に変換した形式で、意匠特許の「図面→タイトル」を多肢選択化すれば最も接続しやすい。
- 純粋な「工業部品→単一ラベル」で写真・大規模・公開・SOTAありのFGVCベンチマークは実は稀少で、既存の主力（RP2K, Products-10K, iMaterialist）はいずれも小売SKU中心。ニッチ工業部品を直接の分類対象とする公開ベンチは MCB（ただし3D／対象外）やnyris Clips-and-Connectors（検索・社内データ／対象外）に偏り、「写真・単一ラベル・公開」を厳密に満たすものは実質存在しないため、汎用FGVCベンチ上で「専門性が高いサブセット」を選ぶ戦略が現実的である。
- 論文の説得力（「汎用VLMが弱い」を定量的に示す）には FOCI が最有力。原論文は **"Crucially, CLIP models exhibit dramatically better performance than LVLMs. Since the image encoders of LVLMs come from these CLIP models, this points to inadequate alignment for fine-grained object distinction between the encoder and the LLM"** と断定しており、man-made objects（IN-Artifact, 2631クラス）でも最良LVLM（Idefics-2）で52.56%どまりであることが報告されている。

## Key Findings（主要な発見）
1. **分類/FGVCで条件に最も近いのはFOCIとRP2K。** FOCIは既存FGVCデータセットを「画像＋4択の多肢選択」に変換し、CLIP（OpenCLIP ViT-L/14）で難しい誤答候補をマイニングすることで難易度を維持している（乱数ベースライン25%）。RP2Kは2,388 SKU・実店舗棚撮影画像で、原論文（Jingtian Peng, Chang Xiao, Yifan Li, arXiv:2006.12634）本文が **"we collect more than 500,000 images of retail products on shelves belonging to 2000 different products"** と述べる大規模データであり、SOTA細粒度手法（CBL, API-Net）が **"they did not surpass even a simple ResNet-34 network on RP2K dataset"** ——単純なResNet-34すら上回れないほど難しい。
2. **「汎用VLMがニッチ工業製品・細粒度対象に弱い」ことを定量化した論文は複数存在する。** FOCI（CLIP>LVLMを明示）、FG-BMK（LVLMは特化モデルに劣後）、MIMEX（小売28カテゴリでCLIP/BLIPのzero-shotが不十分）、そしてfashion属性のzero-shot評価では Shubham Shukla & Kunal Sonalkar, "Can GPT-4o mini and Gemini 2.0 Flash Predict Fine-Grained Fashion Product Attributes?"（arXiv:2507.09950, 2025年7月）が DeepFashion-MultiModal の18属性で **"Gemini 2.0 Flash demonstrates the strongest overall performance with a macro F1 score of 56.79% across all attributes, while GPT-4o-mini scored a macro F1 score of 43.28%"** と、汎用VLMの細粒度属性認識の限界を数値で示している。
3. **純工業部品の「画像→ラベル」公開FGVCは手薄。** 機械部品のMCB（Purdue, 2020）は3D形状（対象外）、nyrisのClips-and-Connectors（ファスナー12,531種）は検索タスクかつ社内データ（対象外）。工業製品ドメインで「写真・単一ラベル・公開・SOTAあり」を厳密に満たす大規模ベンチは乏しく、ここが研究の空白であると同時にIMPACTの新規性主張の余地でもある。
4. **図面という画像性質の近さではMechVQAが際立つ。** 機械製図（線画・多視点・寸法記号）を対象にしたVQAで、意匠特許図面と画像特性が非常に近い。ただしタスクはVQAで出力形式がやや複雑。
5. **テキスト↔画像検索ではILIASが「難しい・公開・SOTAあり」を満たす。** インスタンスレベル検索で、text-to-image検索プロトコルを備え、原論文が **"models fine-tuned on specific domains, such as landmarks or products, excel in that domain but fail on ILIAS"** と述べるとおり既存の特化モデルが軒並み失敗する。

## Details（候補ベンチマーク一覧）

### 一覧表

| ベンチマーク | 提供元/年 | タスク | 指標 | 規模（画像/クラス） | 画像性質 | 難しさ・SOTA・VLMスコア |
|---|---|---|---|---|---|---|
| **FOCI**（African or European Swallow?） | Würzburg大（Geigle, Timofte, Glavaš）/ EMNLP 2024 | 分類（4択多肢選択） | 多肢選択Accuracy（乱数25%） | 5既存FGVC＋ImageNet-21k 4サブセット（IN-Artifact 2631クラス等、10枚/クラス） | 実写 | 最良LVLM（Idefics-2）平均64.13%、man-made（IN-Artifact）で52.56%。「CLIP > LVLM」を明示 |
| **RP2K** | Pinlan Data（Peng, Xiao, Li）/ 2020 | FGVC分類 | Top-1/Top-5 Acc | 500,000枚超 / 2,388 SKU | 実写（棚撮影） | ResNet-34が約95%だが酒類・化粧品で低下。CBL・API-Netが単純ResNet-34を超えられない |
| **Products-10K** | JD.com / 2020 | FGVC分類 | Top-1 Acc / mAP | 約21.4万枚 / 9,691〜10,000 SKU | 実写（屋内外） | 長尾・高類似SKU。ICPR2020コンペのベンチ |
| **iMaterialist-Product 2019** | Malong / FGVC6・CVPR2019 | FGVC分類 | 誤り率 | / 2,019カテゴリ（4階層） | 実写 | 階層構造・製品カテゴリ。難関コンペ |
| **MechVQA** | ICML 2026（Kou, Shi et al.）| VQA（10サブタスク） | Accuracy | 3.3k図面 / 21k QA | 線画（機械製図） | 特化モデルMechVLが最強クローズドモデルを合計7.57pt上回る＝汎用MLLMが弱い |
| **ILIAS** | CTU Prague（Kordopatis-Zilos et al.）/ CVPR 2025 | 画像/テキスト↔画像検索 | mAP@1k | 1,000インスタンス（クエリ1,232・positives 4,715）＋1億distractor | 実写 | 特化モデルが軒並み失敗。t2i検索プロトコルあり |
| **FG-BMK** | 東南大（SEU-VIP）/ ICLR 2026 | 分類＋検索（診断的） | Acc / Recall | 101万問・28万画像（13データセット） | 実写 | LVLMは特化モデルに一貫して劣後（FGVC-Aircraft short-answer 66.19% vs 特化95.40%） |
| **MIMEX** | UniTN（MIMEX EUプロジェクト）/ IEEE 2024 | zero-shot分類 | Acc | / 28カテゴリ | 実写 | CLIP/BLIP zero-shotが不十分と報告 |
| **nyris VPS Benchmark**（Clips-and-Connectors等） | nyris / 2026 | 画像↔画像検索（工業部品） | R@1, mAP@20 | ファスナー12,531種・ギャラリー20万CG | 実写＋CGレンダ | **対象外**（画像↔画像retrieval）。参考情報 |
| **MCB** | Purdue / 2020 | 3D形状分類・検索 | Acc | 58,696モデル / 68クラス | 3D/CADレンダ | **対象外**（3D）。参考情報 |

### 各ベンチの詳細

**FOCI（Fine-grained Object ClassIfication, arXiv:2406.14496, EMNLP 2024, pp. 2653–2669）**
- 著者：Gregor Geigle, Radu Timofte, Goran Glavaš（University of Würzburg）。既存の分類データセットを「画像＋4択ラベル」の多肢選択に変換したベンチマーク。5つの人気FGVC（FGVC-Aircraft 100, Flowers102, Food101, Oxford-Pet 37, Stanford-Cars 196）に加え、ImageNet-21kから4つのドメインサブセット（IN-Animal 1322, IN-Plant 957, IN-Food 563, **IN-Artifact＝man-made objects 2631クラス**）を構成。各ImageNet-21kサブセットは10枚/クラスをサンプリング。
- 12個の公開LVLMを評価。最良はIdefics-2（平均64.13%）とQwen-VL-Chat（62.41%）、最下位はIdefics-1（42.19%）、LLaVA 1.5は46.75%。man-made objects（IN-Artifact）では最良で52.56%（Idefics-2）、最低41.90%（Idefics-1）、LLaVA 1.5は45.61%。
- 決定的な発見（逐語）：**"Crucially, CLIP models exhibit dramatically better performance than LVLMs. Since the image encoders of LVLMs come from these CLIP models, this points to inadequate alignment for fine-grained object distinction between the encoder and the LLM."** CLIPが誤ると対応LVLMはほぼ乱数（25%）に落ちる（Figure 4）。
- LVLM–CLIPギャップはドメインで大きく異なり、IN-Artifactで<10pt、Oxford-Petsで40–50pt。SigLIPへのエンコーダ差し替えでIN-Artifactは40.33→47.44に改善。
- 重要な注：**この論文はGPT-4V/Geminiなどプロプライエタリを評価していない**（全て7B以下の公開モデル）。また、per-subsetのCLIP zero-shot精度は数表ではなく散布図（Figure 3）でのみ提示されている。

**RP2K（arXiv:2006.12634, Jingtian Peng, Chang Xiao, Yifan Li, 2020）**
- 実店舗の棚で撮影された小売製品の細粒度分類。2,388 SKU、本文の逐語で **"more than 500,000 images"**（要旨も50万枚超と一致、初期版本文には35万枚の記述もあり版で揺れがある）。ResNet-34で約95%だが、酒類・化粧品など見た目が似たカテゴリで精度が大きく低下。CBL・API-Netなど当時のSOTA細粒度手法が **"did not surpass even a simple ResNet-34 network on RP2K dataset"**——単純なResNet-34を超えられなかったと明記。

**Products-10K（arXiv:2008.10545, JD.com, 2020）**
- 9,691〜10,000のSKUレベル製品、約21.4万枚。長尾分布・高い視覚類似性。ICPR2020のコンペ課題（Kaggle）。人手ラベルでエラー率0.5%未満。

**iMaterialist-Product 2019（Malong Technologies / FGVC6・CVPR 2019）**
- 2,019カテゴリを4階層のツリーで構成した製品認識コンペ。細粒度・階層構造が特徴。関連するiMaterialist系（2017 FGVC4は381属性、2018 FGVC5は家具、Fashion系は属性/セグメンテーション）はタスクがやや異なる点に注意。

**MechVQA（arXiv:2605.30794, ICML 2026, Qian Kou, Xiaofeng Shi et al.）**
- 機械製図理解のVQA。3.3k枚の高密度図面・21k QA、Recognition/Reasoning/Judgingの3レベル10サブタスク。特化モデルMechVL-4B-RLがeasy 94%/medium 79%/hard 75%を達成し、**最強クローズドソースモデルを合計スコアで7.57pt上回る**＝汎用MLLMが図面で弱いことを定量化。画像が線画・多視点図面である点で意匠特許図面に最も近い。コード公開（github.com/xiaofengShi/MechVQA）。

**ILIAS（arXiv:2502.11748, DOI:10.1109/CVPR52734.2025.01377, CVPR 2025, Kordopatis-Zilos et al., CTU Prague）**
- インスタンスレベル画像検索。1,000オブジェクトインスタンスに対しクエリ1,232画像・positives 4,715画像、加えて **"100 million distractor images from YFCC100M"**。画像↔画像（i2i）だけでなくtext-to-image（t2i）検索プロトコルを提供（テキストは物体の詳細記述）。逐語：**"models fine-tuned on specific domains, such as landmarks or products, excel in that domain but fail on ILIAS"** かつ t2i性能はi2iに驚くほど近い。指標はmAP@1k。

**FG-BMK（arXiv:2606.19053 / 2504.14988, 東南大SEU-VIP, ICLR 2026採択）**
- 101万問・28万画像（13データセット；版により349万問・332万画像の表記もあり）の大規模診断ベンチ。human-oriented（対話）とmachine-oriented（検索・分類）を統合。逐語：**"on FGVC Aircraft, LVLMs achieve 66.19% accuracy with short-answer questions and 78.88% with linear probing, whereas the fine-grained tailored model reaches 95.40%"**——LVLMが特化モデルに一貫して劣後することを示す。専門ドメイン（リモセンMTARSI等）を含む。

**MIMEX（arXiv:2409.14963, IEEE 2024, UniTN／MIMEX EUプロジェクト）**
- 小売28カテゴリのzero-shot分類。チョコ・スナック・飲料・調味料など高い商品間類似性。CLIP/BLIPなどのVLMがfine-grained識別で不十分と報告し、CLIP＋DINOv2アンサンブル＋visual prototypeを提案。

**参考（明示的に対象外）：**
- **nyris Visual Product Search Benchmark（arXiv:2603.17186, 2026）**：Clips-and-Connectors v1はファスナー12,531種・ギャラリー20万CGレンダ・クエリ実写と、ニッチ工業部品を扱う点は非常に参考になるが、タスクは画像↔画像retrieval（対象外）かつ主要データは社内（nyris）由来。
- **MCB（Purdue, 2020）**：機械部品68クラス・58,696モデルだが3D形状認識（対象外）。

## Recommendations（推奨・親和性上位5件と採否）

意匠特許のドメイン特化ファインチューニング（図面・専門工業製品カテゴリの理解）との親和性が高い順に上位5件を挙げる。

**1位：FOCI（最推奨）**
- 利点：出力形式が「画像＋4択→1ラベル」で最もシンプル。IMPACTのタイトル/カテゴリを正解ラベルとし、CLIPで難しい誤答候補を混ぜれば**同一プロトコルを自前データに適用でき、「汎用VLMが弱い（CLIP>LVLM）」という論文の主張とストーリーが完全に一致する**。man-made objects（IN-Artifact, 2631クラス）は工業物体寄りで、意匠特許の対象と親和的。公式コードあり。
- 懸念：IN-Artifactは日用工業物体寄りで、意匠特許のニッチ部品とは粒度がずれる。**GPT-4V/Geminiのスコアは原論文になく、自分で追試する必要がある**（原論文は7B級公開モデルのみ）。多肢選択は自由記述より易しくなるため、コサイン類似度採点の既存評価と併用するのが望ましい。

**2位：RP2K**
- 利点：純粋な「画像→単一ラベル」FGVCで公開・SOTA明確。「SOTA細粒度手法が単純ResNet-34を超えられない」という難しさが明示され、IMPACTの分類設定にそのまま乗せやすい。
- 懸念：ドメインが小売SKU（実写棚画像）で、図面でも工業部品でもない。画像性質（線画 vs 実写）の乖離が大きく、ドメイン近接性は低い。

**3位：Products-10K / iMaterialist-Product 2019**
- 利点：大規模・多カテゴリ・長尾で分類設定が確立。製品カテゴリFGVCの標準ベンチとして引用価値が高い。
- 懸念：日用消費財中心でニッチ工業部品は少ない。GPT-4V/Gemini公式スコアは未整備。

**4位：MechVQA**
- 利点：画像が線画・機械製図で**意匠特許図面に最も近い**。「汎用MLLMが弱い→特化で勝つ（7.57pt）」が既に定量化されており、論文ストーリーの追随に好適。
- 懸念：タスクがVQA（出力が単一ラベルでない）。IMPACTのタイトル/クレームからQAを合成する追加設計が必要で、「シンプル出力優先」の方針からはやや外れる。

**5位：ILIAS（検索の次点として）**
- 利点：text-to-image検索で「テキストクエリ→該当製品画像」を評価でき、IMPACTのタイトル↔図面ペアを検索設定に流用可能。難関・公開・SOTAあり。
- 懸念：本来はインスタンス検索で、意匠特許の「別視点図面対応付け」（対象外）に近い側面もある。用途を「テキスト→図面」に限定して使う必要がある。

**判断を変える閾値：**
- 査読者に「工業ドメインでの直接性」を強く求められるなら、1位をMechVQA（図面性質の近さ）に繰り上げる。
- 「単一ラベル・シンプル出力」を最優先するなら、**FOCI＋RP2Kの2本立て**で分類SOTA比較を固め、VLM劣位はFOCIプロトコル（自前でGPT-4V/Gemini追試を追加）で示すのが最短。
- 純工業部品FGVCが必要なら、公開の該当ベンチが乏しいため、**IMPACTから工業部品サブセットを切り出し「新ベンチマーク」として提案**する方が説得力が出る（FOCIのプロトコルを踏襲して多肢選択化すると既存研究との接続が良い）。

## Caveats（留意点）
- **純粋な「工業部品→単一ラベル」公開FGVCベンチは実質的に不在。** 該当候補は3D（MCB, 対象外）か検索（nyris, 対象外・社内データ）に偏る。分類で工業ドメインを主張するには、汎用FGVCの専門サブセット（FOCIのIN-Artifact等）を使うか、IMPACT自体を新ベンチ化するのが現実的。
- **GPT-4V/Geminiの直接スコアは多くのベンチで未整備。** FOCIは公開7B級モデルのみ、MechVQA・FG-BMKはクローズド/特化モデルとの比較あり。GPT-4V/Geminiの数値が論文に必要なら自前で追試が要る（fashion属性のarXiv:2507.09950はGPT-4o-mini 43.28% / Gemini 2.0 Flash 56.79%のmacro-F1を報告しており、追試設計の参考になる）。
- **多肢選択（FOCI形式）は自由記述より容易。** コサイン類似度による自由記述採点と多肢選択採点は難易度が異なるため、両方を併記して比較可能性を担保すべき。
- **RP2Kの規模は情報源で記述が揺れる。** 本文の逐語は "more than 500,000 images"、初期版本文には35万枚の記述もある。採用時は自分でダウンロードして実数を確認すべき。
- **バージョン・年・査読状況に注意。** FG-BMKは版により「101万問・28万画像」と「349万問・332万画像」の両表記があり、arXiv版番号で確認が必要（ICLR 2026採択）。MechVQA（ICML 2026）・ILIAS一部・nyrisは2026年表記のプレプリントを含み、本レポート作成時点（2026年8月）で一部査読・数値が流動的な可能性がある。
- **対象外項目は除外済み。** 多視点検索（DeepPatent系）・SBIR・3D・画像↔画像retrieval・意匠特許図面ベンチ（DeepPatent, PatentNet等）は対象外として除外し、nyris/MCBのみ参考掲載にとどめた。