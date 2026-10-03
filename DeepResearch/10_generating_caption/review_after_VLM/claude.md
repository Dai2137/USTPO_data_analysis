# VLM 期（2023年〜）のレビュー論文における「画像の記述生成」の位置づけ

## TL;DR
- 2023年以降、キャプション生成は独立タスクではなく「MLLM の一機能／評価軸の一つ」として総説に組み込まれた。この移行を正面から扱う査読付き総説はまだ少なく、最も近いのは Sarto ら（IJCAI 2025 Survey Track, 査読済み）と Berger ら（TACL 2025, 査読済み）である。Sarto らは「With the advent of Multimodal Large Language Models (MLLMs), image captioning has become a core task」と明記する。
- 「image captioning」という用語は今も章題・タスク総称として広く残っているが、詳細記述の文脈では detailed/dense/long caption、fine-grained perception、grounded/region captioning へと語が分化している。
- あなたの問題設定（弁別性・聞き手テスト・対象ごとに見る粒度を変える・長尾記述）は、VLM 期の主要サーベイでは独立課題として扱われていない。最も近いのは Berger ら TACL 2025 の「retrieval-based 評価（self-retrieval）」「candidate diversity（CIDErBtw / Self-CIDEr）」の項だが、そこでも周辺的な位置づけにとどまる。この空白そのものが、あなたの研究の新規性を示す。

## Key Findings

1. **移行を扱う総説は存在するが、査読付きは少数。** キャプション生成を MLLM の一機能・一評価軸として扱う査読付き総説として、Sarto ら「Image Captioning Evaluation in the Age of Multimodal LLMs」(IJCAI 2025 Survey Track) と Berger ら「Surveying the Landscape of Image Captioning Evaluation」(TACL 2025) が確認できる。arXiv のみの総説（MME-Survey, 幻覚サーベイ, ベンチマークサーベイ等）が多数を占め、この分野は査読付き総説が追いついていない。

2. **用語の変化。** 「image captioning」はタスクの総称として存続（歴史語ではなく現役）。詳細記述は detailed caption / dense caption / long caption、領域単位は region captioning / grounded captioning、能力軸としては fine-grained perception が定着しつつある。

3. **標準的なやり方。** 生成は「凍結モデルへのプロンプト＋指示チューニング（SFT）＋選好最適化（DPO/RLAIF）」。学習データは強いモデルによる recaptioning が主流化。評価は参照一致（CIDEr 等）から参照なし（CLIPScore 系）・幻覚指標（CHAIR, POPE）・LLM-as-judge へ重心が移動。

4. **あなたの問題設定は VLM 期サーベイでは独立課題として扱われていない。** 弁別性・聞き手モデル・見る粒度の対象依存性・記述の長尾はいずれも中心項目になっていない。見つからないこと自体が重要な発見である。

## Details

### 1. VLM 期のレビュー論文一覧

| 著者・年 | タイトル | 掲載／査読 | 対象範囲 | 記述生成の置き場所 | 用語 | 主な未解決問題 |
|---|---|---|---|---|---|---|
| Sarto, Cornia, Cucchiara 2025 | Image Captioning Evaluation in the Age of Multimodal LLMs: Challenges and Future Perspectives | IJCAI 2025 Survey Track（**査読済み**, DOI 10.24963/ijcai.2025/1180、arXiv:2503.14604） | キャプション評価指標の変遷 | 「MLLM 時代にキャプション生成は core task になった」と明記し、評価軸として整理 | image captioning を継続使用。longer/detailed captions に言及 | 長い記述への指標適応、幻覚検出、説明可能性、指標の個人化 |
| Berger, Stanovsky, Abend, Frermann 2025 | Surveying the Landscape of Image Captioning Evaluation: A Comprehensive Taxonomy, Trends and Metrics Analysis | TACL 2025, Vol.13, pp.1597–1644（**査読済み**, DOI 10.1162/TACL.a.52、arXiv:2408.04909） | 2010–2024年、15会場、314論文から71自動指標＋5人手評価方式 | 評価タスクとして体系化。retrieval-based（self-retrieval）と candidate diversity を独立の分類軸として明記 | image captioning。distinctiveness 系（CIDErBtw, Self-CIDEr）を diversity 指標として収録 | 分野が5指標（BLEU/CIDEr/METEOR/ROUGE/SPICE）に過度依存し人手評価と弱相関 |
| Abdulgalil, Basir 2025 | Next-generation image captioning: from transformers to Multimodal Large Language Models | Natural Language Processing Journal（Elsevier）Vol.12, 100159（**査読済み**, DOI 10.1016/j.nlp.2025.100159、オープンアクセス） | Transformer→MLLM への移行 | MLLM を「captioning の次の発展段階」として1節（§4.4）に配置 | image captioning を主軸に維持 | 幻覚、grounding、評価指標の不足、計算コスト、長尾物体認識 |
| Bai ら 2024（改訂 2025） | Hallucination of Multimodal Large Language Models: A Survey | arXiv:2404.18930（**arXiv のみ**、40頁改訂版 v2, 228 references） | MLLM 幻覚の分類・検出・緩和 | 幻覚はキャプション生成で顕在化。CHAIR/POPE を中心に評価 | LVLM/MLLM。captioning は幻覚評価の題材 | 幻覚の測定・緩和、contrastive decoding、RL 系手法の台頭 |
| Fu ら 2024 | MME-Survey: A Comprehensive Survey on Evaluation of Multimodal LLMs | arXiv:2411.15296（**arXiv のみ**） | MLLM 評価全般 | captioning は perception/instruction-following の一部 | image captioning, instruction following | 評価の体系化、データ汚染、指標の信頼性 |
| Li ら 2024 | A Survey on Benchmarks of Multimodal Large Language Models | arXiv:2408.08632（**arXiv のみ**、200+ベンチ） | MLLM ベンチマーク | captioning は perception/understanding の1カテゴリ | image captioning | ベンチの氾濫、系統的評価の欠如 |
| Caffagni ら 2024 | The Revolution of Multimodal Large Language Models: A Survey | arXiv:2402.12451（**arXiv のみ**、ACL 2024 Findings 版あり） | MLLM 総説 | captioning は基本タスク。visual grounding を別節（§3.1）で扱う | captioning, region captioning, grounded captioning | grounding、細粒度視覚タスク |
| Xiao ら 2025 | Towards Visual Grounding: A Survey | TPAMI 2025（**査読済み**, 2025年10月30日採録） | 視覚的接地 | region captioning / REG を grounding の下位に配置 | visual grounding, referring expression | 接地の統一枠組み |

補足：古典的サーベイ（Bernardi 2016 JAIR, Hossain 2019 CSUR, Stefanini 2022 TPAMI, Ghandi 2024 CSUR）はいずれもキャプション生成を独立タスクとして扱っており、上記 VLM 期サーベイとの最大の違いは「独立タスク→MLLM の一機能・一評価軸」という位置づけの転換にある。

### 2. 用語の変遷（いつ、何から何へ）

- **〜2022年頃：** 「image captioning」が独立タスク名。dense captioning（Johnson ら 2016 由来）は領域単位の下位タスク。
- **2023〜2024年：** MLLM の指示追従の一機能へ。ShareGPT4V 等の登場で「detailed caption」「fine-grained caption」が学習データ文脈で定着。
- **2025〜2026年：**
  - 「detailed / dense / long caption」＝長く密な記述（DOCCI, DCI, ImageInWords, PixelProse 等のデータセットが牽引）。
  - 「region captioning / grounded captioning」＝領域・座標付き記述（grounding サーベイ系）。
  - 「fine-grained perception」＝能力軸としての細粒度知覚。
  - 「image captioning」自体は総称・章題として存続（Sarto ら, Abdulgalil ら とも継続使用）。歴史的経緯としてのみ登場する語ではなく、現役の総称。
- **定着した語：** detailed/dense caption、fine-grained perception、grounded/region captioning、recaptioning。
- **まだ揺れている語：** long caption と detailed caption はほぼ同義で混在。hyper-detailed（ImageInWords）等の新語も出現。distinctive/discriminative captioning は古典系の語で VLM 期総説にはほぼ継承されていない。

### 3. 現在の標準的なやり方（サーベイの記述を根拠に）

- **生成：** 凍結モデルへのプロンプト＋指示チューニング（SFT）が標準。近年は選好最適化（DPO/RLAIF）が急増し、特に detailed/video captioning では DPO ベース手法が競技会で1位を取る例もある（SynPO, AVC-DPO）。Bai ら幻覚サーベイは「RL 系手法が momentum を得ている」「contrastive decoding が cornerstone 技術になった」と総括する。
- **学習データ（recaptioning）：** 強いモデル（GPT-4V 等）で既存の alt-text を書き直す流れが主流。ShareGPT4V は「a curated 100K high-quality captions collected from advanced GPT4-Vision and has been expanded to 1.2 million with a superb caption model trained on this subset」（arXiv:2311.12793, ECCV 2024）。利点は image-text 整合の細粒度化。危険は誤りの増幅で、Hunyuan-Recap100M は continuous DPO により「the non-hallucination caption rate on a held-out test set increases from 48.3% to 77.9% for a 7B-size model」と報告（arXiv:2504.13123, arXiv のみ）。
- **評価：** 参照一致（CIDEr 等）は依然使われるが、Sarto ら・Berger らとも「長い MLLM 記述に不適合」と指摘。参照なし指標（CLIPScore, PAC-S, BRIDGE, HiFi-S）、幻覚指標（CHAIR, POPE, ALOHa）、LLM-as-judge（CLAIR, FLEUR）へ重心移動。Berger らは「the vast majority of examined papers use only five simple metrics (BLEU, METEOR, ROUGE, CIDEr, SPICE)」で、これらは人手評価と弱相関だと警告する。Sarto らの評価軸は (1) 人手判断との相関、(2) ペアランキング精度、(3) 幻覚感度、の3つ。
- **ベンチマーク（詳細・密な記述）：**
  - **DOCCI**：長い段落記述の人手アノテーション。
  - **DCI（Densely Captioned Images）**：マスク整合の長記述で、VLM の領域理解を測定。
  - **ImageInWords**：hyper-detailed（超詳細）記述。
  - **PixelProse**：大規模な密記述データセット。
  - **DetailCaps-4870**：詳細記述の事実性評価。
  - **DOCCI-Critique（NeurIPS 2025, arXiv:2506.07631）**：段落記述の文単位事実性（100画像・14 VLM・1,400記述に対し 10,216 の人手判定）。

### 4. あなたの問題設定に対応する項目があるか（対応表）

| あなたの設定 | VLM 期サーベイでの扱い | どの章／扱われていないか |
|---|---|---|
| 紛らわしい候補と区別できる記述（識別性・弁別性・語用論・聞き手モデル） | **中心的には扱われていない。** Berger ら TACL 2025 が candidate diversity の下で CIDErBtw / Self-CIDEr を、また retrieval-based 評価を収録するのが唯一の接点。Sarto ら・Abdulgalil らには distinctiveness/discriminative/pragmatic の語が皆無 | Berger ら §4.1.1（retrieval）・§4.1.3（candidate diversity）に断片的。他の総説は扱いなし |
| 生成記述で対象を当て直す評価（self-retrieval / listener accuracy） | **標準評価としては扱われていない。** Berger らが「recall@n による text-to-image retrieval」を評価プロトコルの一つとして明記し、人手評価類型にも retrieval を含めるが、あくまで周辺的位置づけ | Berger ら §4.1.1・§4.2。「多数あるプロトコルの一つ」で標準指標ではない |
| 見る粒度を対象ごとに変える（全体 vs 一部拡大） | **総説では独立項目化されていない。** 手法論文（V*, Chain-of-Spot, CropVLM, HIDE, Mixture-of-Resolution 等の zoom-in 群）が活発だが、サーベイの章立てにはなっていない | 扱われていない（手法レベルのみ） |
| 事前学習に現れない対象・記述の長尾 | 長尾物体認識は Abdulgalil ら が limitation として言及。ただし「記述の長尾」ではなく「認識の長尾」 | Abdulgalil ら §5（限界）に限定的言及。記述の長尾としては扱いなし |

### 5. 未解決問題の共通リストと、あなたの主張の判定

複数サーベイが共通して挙げる未解決問題：
1. **幻覚・事実性**（Bai ら, Sarto ら, Abdulgalil ら, MME-Survey 共通）。
2. **長い／詳細な記述に対する評価指標の不備**（Sarto ら, Berger ら）。
3. **grounding／領域整合**（Caffagni ら, Xiao ら）。
4. **参照指標への過度依存**（Berger ら）。
5. **計算コスト・効率**（Abdulgalil ら, efficiency survey 系）。

**あなたの主張の判定：**
「記述の決め手になる手がかりの在り処（全体の輪郭か、ごく一部か）は対象ごとに異なるのに、モデルは常に同じ粒度で見ている。この性質を測り、対象ごとに見方を切り替える。質問文もラベルも使わない」

- この主張に**完全に対応する独立課題は、VLM 期の主要サーベイには存在しない。**
- 最も近い既存の課題名は3つに分散している：(a) **fine-grained perception / visual detail の限界**（Abdulgalil ら の長尾・細粒度、幻覚サーベイの perception 起因幻覚）、(b) **distinctive/discriminative captioning**（Berger ら の diversity/retrieval 軸。ただし Luo 2018, Wang&Chan の Self-CIDEr など古典手法系の収録）、(c) **adaptive/high-resolution perception**（手法レベルの zoom-in 群で、サーベイ未整理）。
- 「対象ごとに手がかりの粒度が異なる」という測定・切替の視点、および「質問文なし・ラベルなしで弁別的記述を出させ、8択の聞き手テストで評価する」という設定は、**独立した課題としては挙げられていない**。これはあなたの研究の新規性を示す重要な空白である。

## Recommendations

1. **査読付き総説の骨格として Sarto ら（IJCAI 2025）と Berger ら（TACL 2025）を主軸に引用する。** 両者が「captioning は MLLM の core task／評価軸」という移行を査読付きで裏付ける、現時点で唯一の組み合わせ。Abdulgalil ら（NLP Journal 2025）と Xiao ら（TPAMI 2025）を補助的に併用する。

2. **弁別性・聞き手評価の系譜は総説ではなく手法論文で補強する。** Luo ら 2018（Show, Tell and Discriminate: self-retrieval）、Dai & Lin 2017（Contrastive Learning for Image Captioning）、Wang & Chan（Self-CIDEr）、Wang ら 2020（CIDErBtw）、Dessì ら 2023（discriminative finetuning）を引き、Berger ら TACL 2025 を「これらを収録した唯一の VLM 期サーベイ」として橋渡しに使う。

3. **新規性の主張は「空白」を根拠に立てる。** 「対象依存の手がかり粒度の測定・切替」＋「質問なし・ラベルなしの弁別的記述＋聞き手テスト」は VLM 期サーベイに独立課題として存在しないことを明記し、(a)(b)(c) の3課題を横断・統合する位置づけとして提示する。

4. **ベンチマーク比較では DOCCI / DCI / ImageInWords / PixelProse / DetailCaps を「長い記述の事実性・密度」を測るものと位置づけ、あなたの「弁別性・当て直し（8択聞き手テスト）」評価との差分を強調する。** これらは faithfulness/density を測るが discriminability は測らない、という対比が有効。

5. **判断が変わる閾値：** もし 2026年以降に「discriminative/pragmatic captioning」を独立タスクとして章立てする、あるいは「self-retrieval / listener accuracy を標準評価とする」査読付き総説が現れた場合、新規性の主張を「空白の充填」から「既存課題への貢献」へ調整すること。同様に、zoom-in 系（V*, CropVLM 等）を体系化するサーベイが出た場合は、設定(c) の位置づけを見直すこと。

## Caveats
- この分野は査読付き総説が追いついておらず、重要な総説の多くが arXiv のみ（MME-Survey, Bai ら幻覚, Li ら ベンチ, Caffagni ら）。本報告では査読済み（Sarto, Berger, Abdulgalil, Xiao）と arXiv のみを明確に区別した。「移行を正面から扱う査読付き総説はまだ少ない」というのが正確な現状である。
- recaptioning の効果数値（Hunyuan-Recap の 48.3%→77.9% 等）は当該手法論文の自己申告であり、独立検証ではない（判定モデルが同系列という指摘あり）。ShareGPT4V の 10万→120万件も同論文の記述による。推測と事実を区別のこと。
- Berger ら TACL 2025 は self-retrieval（recall@n retrieval）を「多数あるプロトコルの一つ」として収録しており、「標準評価」とは位置づけていない。過大評価しないこと。
- 「見る粒度の対象依存性」に関する zoom-in 系（V*, Chain-of-Spot, CropVLM, HIDE 等）は 2024–2026 に活発だが、いずれも手法論文であり、サーベイの章立てには未反映。時期的に今後サーベイ化される可能性がある。
- 用語「image captioning」の存続とその分化（detailed/dense/grounded 等）は複数の査読済み・arXiv 総説から一貫して確認できるが、語の揺れ（long vs detailed vs hyper-detailed）は現在進行中であり、今後さらに統廃合が進む見込み。

---

### 参考文献（正式タイトル・著者・掲載・DOI/arXiv）

**査読付き総説**
- Sara Sarto, Marcella Cornia, Rita Cucchiara. "Image Captioning Evaluation in the Age of Multimodal LLMs: Challenges and Future Perspectives." IJCAI 2025, Survey Track, pp.10632–10640. DOI: 10.24963/ijcai.2025/1180（arXiv:2503.14604）
- Uri Berger, Gabriel Stanovsky, Omri Abend, Lea Frermann. "Surveying the Landscape of Image Captioning Evaluation: A Comprehensive Taxonomy, Trends and Metrics Analysis." Transactions of the ACL (TACL), Vol.13, pp.1597–1644, 2025. DOI: 10.1162/TACL.a.52（arXiv:2408.04909）
- Huda Diab Abdulgalil, Otman A. Basir. "Next-generation image captioning: A survey of methodologies and emerging challenges from transformers to Multimodal Large Language Models." Natural Language Processing Journal (Elsevier), Vol.12, Article 100159, 2025. DOI: 10.1016/j.nlp.2025.100159
- Linhui Xiao, Xiaoshan Yang, Xiangyuan Lan, Yaowei Wang, Changsheng Xu. "Towards Visual Grounding: A Survey." IEEE TPAMI, 2025（採録 2025-10-30）

**arXiv のみの総説**
- Zechen Bai, Pichao Wang, Tianjun Xiao, Tong He, Zongbo Han, Zheng Zhang, Mike Zheng Shou. "Hallucination of Multimodal Large Language Models: A Survey." arXiv:2404.18930（v2, 2025-04-01）
- Chaoyou Fu ら. "MME-Survey: A Comprehensive Survey on Evaluation of Multimodal LLMs." arXiv:2411.15296（2024）
- Jian Li ら. "A Survey on Benchmarks of Multimodal Large Language Models." arXiv:2408.08632（2024）
- Davide Caffagni, Federico Cocchi ら (Cucchiara group). "The Revolution of Multimodal Large Language Models: A Survey." arXiv:2402.12451（2024, ACL 2024 Findings 版あり）

**手法・データセット・ベンチマーク（本文で参照）**
- Lin Chen ら. "ShareGPT4V: Improving Large Multi-Modal Models with Better Captions." arXiv:2311.12793（ECCV 2024）
- Xinsong Zhang ら. "Low-hallucination Synthetic Captions for Large-Scale Vision-Language Model Pre-training."（Hunyuan-Recap100M）arXiv:2504.13123（2025）
- "Unblocking Fine-Grained Evaluation of Detailed Captions: An Explaining AutoRater and Critic-and-Revise Pipeline."（DOCCI-Critique）arXiv:2506.07631（NeurIPS 2025）
- Ruotian Luo, Brian Price, Scott Cohen, Gregory Shakhnarovich. "Discriminability Objective for Training Descriptive Captions." CVPR 2018 ／ Xihui Liu ら "Show, Tell and Discriminate: Image Captioning by Self-retrieval with Partially Labeled Data." ECCV 2018
- Bo Dai, Dahua Lin. "Contrastive Learning for Image Captioning." NeurIPS 2017
- Jiuniu Wang, Wenjia Xu ら. "Compare and Reweight: Distinctive Image Captioning Using Similar Images Sets."（CIDErBtw）ECCV 2020 ／ Self-CIDEr（Wang & Chan 2019）
- Roberto Dessì ら. "Cross-domain image captioning with discriminative finetuning." CVPR 2023
- zoom-in 系手法：V* (Guided Visual Search)、Chain-of-Spot、CropVLM（arXiv:2511.19820）、HIDE（arXiv:2510.00054）、Mixture-of-Resolution Adaptation（ICLR 2025）ほか