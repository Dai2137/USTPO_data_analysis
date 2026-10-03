# 推論にLLM/MLLMを用いる細粒度画像認識（FGVR）手法の網羅調査と分類（2023〜2026）

**結論：推論にMLLM・LVLMを用いる細粒度認識の手法で、画像から明示的に切り出した局所（クロップ、領域、部位トークン）をMLLMに入力するものは、今回の調査では1本も見つかりませんでした。したがって「全体と局所・配分がサンプルごと・局所もサンプルごとに選ぶ」に入る手法も見つかっていません。** 既知の6本に加えて追加できたのは約8本です（うち数本は境界例）。すべて「全体のみ」に入ります。

## TL;DR
- 追加できたのは、DiVE-k、ReFine-RFT、Finer（AttrSeek／学習ミックス）、AutoSEP、nlg2choice、UniFGVC、VR-RAG系などです。すべて「全体のみ」で、局所をMLLMに入れる細粒度認識の手法は見つかりませんでした。事後学習する側（B-1）は強化学習とCoTの論文が中心で、2025〜2026年に急に増えています。
- 「MLLM＋クロップ／ズーム」の研究はたくさんありますが、どれもV*Bench、HR-Bench、TextVQA、ZoomBenchなどで評価する高解像度VQA（除外1）です。細粒度認識のデータセットでクロップを使う手法は、分類器がCLIP＋線形層で、LLMを使っていません（除外3）。
- つまり、MLLMが最終予測を出し、全体と局所の配分をサンプルごとに決め、局所もサンプルごとに選ぶ細粒度認識の手法は、調べた範囲では空白です。新しく提案する場合、B-1-b（未知カテゴリへの汎化を伴う事後学習）とB-2-b（ゼロショット）のどちらでも先行例は見つかりませんでした。

## 1. 分類木への配置

```
B-1. 事後学習する
 ├─ B-1-a. 閉集合
 │    └─ 全体のみ：Finedefics（ICLR 2025）※既知
 │                 Finer学習ミックスでのLLaVA-1.5の指示チューニング（EMNLP 2024）
 │                 ReFine-RFT（CVPR Findings 2026）※a／bの別は未確認、暫定でa
 │                 ［境界・除外2寄り］Visual-RFT（ICCV 2025）の細粒度分類の実験
 │    └─ 局所のみ／全体と局所（固定・サンプルごと）：該当なし
 └─ B-1-b. 未知カテゴリへの汎化
      └─ 全体のみ：Fine-R1（ICLR 2026）※既知
                   DiVE-k（arXivのみ 2025）
                   ［境界・除外2寄り］CLS-RL（arXivのみ 2025、base-to-new）
      └─ 局所のみ／全体と局所（固定・サンプルごと）：該当なし
B-2. 事後学習しない
 ├─ B-2-a. 見本を使う
 │    └─ 全体のみ：SARE（arXiv 2026）※既知
 │                 RAR ※既知（判定に注記あり、後述）
 │                 Zero-Shot FG Image Classification Using LVLMs（EMNLP Findings 2025）※既知
 │                 AutoSEP（NeurIPS 2025）※見本はラベルのない画像
 │                 ［境界］UniFGVC（arXivのみ 2025）※最終判定は埋め込み検索
 │    └─ 局所のみ／全体と局所（固定・サンプルごと）：該当なし
 └─ B-2-b. ゼロショット
      └─ 全体のみ：CascadeVLM（EMNLP Findings 2024）※既知
                   AttrSeekプロンプト（Finer, EMNLP 2024）
                   nlg2choice（WACV 2026）
                   ［要確認］VR-RAG（arXivのみ 2025）
      └─ 局所のみ／全体と局所（固定・サンプルごと）：該当なし
```

## 2. 論文ごとの表（新しく見つけたもの）

| 論文（正式タイトル） | 筆頭著者・会場・年 | 葉 | 判定根拠（原文引用 → 日本語要約） | LLM・MLLM | 評価データセット | 局所 |
|---|---|---|---|---|---|---|
| DiVE-k: Differential Visual Reasoning for Fine-Grained Image Recognition（arXiv 2511.18305。HTML版の表記） | Raja Kumar（University of Southern California。共著者はArka Sadhu、Ram Nevatia）／arXivのみ 2025 | B-1-b・全体のみ | "For each training image, DiVE-k creates a multiple-choice question from the model's top-k outputs and uses RL to train the model to select the correct answer." "In the standard base-to-novel generalization setting, DiVE-k surpasses the QWEN2.5-VL-7B and ViRFT by 10.04% and 6.16% on the Harmonic Mean metric" → モデル自身の上位k個の予測から多肢選択問題を作り、強化学習で事後学習する。base-to-novelで評価しているのでB-1-b。本文には "mixed-domain zero-shot base-to-novel generalization setting, where we achieve improvements of 9.03% against QWEN2.5-VL-7B and 4.02% against ViRFT" ともある。 | Qwen2.5-VL-7B | 「five standard fine-grained datasets」（個別のデータセット名は未確認） | なし |
| Can Textual Reasoning Improve the Performance of MLLMs on Fine-grained Visual Classification?（ReFine-RFT） | Jie Zhu／CVPR Findings 2026（arXiv 2601.06993） | B-1・全体のみ（a／bは未確認） | "ReFine-RFT, a framework that combines ensemble rewards with MRN to constrain reasoning length while providing dense accuracy-oriented feedback." → FGVCではCoTが長いほど精度が下がる（"Cost of Thinking"）ことを示し、報酬を組み合わせたRFTで推論の長さを抑える。 |\[1\] Qwen2-VL系（Visual-RFTの学習構成を土台にする）。対象モデルの詳細は未確認\[2\] | 「four FGVC datasets」（個別名は未確認） | なし |\[3\]
| Finer: Investigating and Enhancing Fine-Grained Visual Concept Recognition in Large Vision Language Models | Jeonghwan Kim／EMNLP 2024 | ベンチマーク＋手法2つ：AttrSeek＝B-2-b・全体のみ、Finerでの指示チューニング＝B-1-a・全体のみ（閉集合かどうかは暫定） | "we (i) prompt the VLMs to generate the most distinctive physical attributes visible in the concepts in an image, and (ii) feed the generated set of at[tributes]…" → まず属性を生成させ、その属性を使って最終予測させる2段階のプロンプト。 | LLaVA-1.5、InstructBLIP、GPT-4V | iNaturalist-2021、CUB、FGVC-Aircraft、Stanford Dogs、NABirds、Stanford Cars | なし |\[4\]\[5\]\[6\]
| Unlabeled Data Improves Fine-Grained Image Zero-shot Classification with Multimodal LLMs（AutoSEP） | Yunqi Hong／NeurIPS 2025 | B-2-a・全体のみ（見本はラベルのない画像） | "The MLLM then makes the final classification based on the original image and the additional textual description" → 記述生成用のプロンプトを、ラベルのない画像で最適化する。パラメータは更新しない。MLLMが最終判定を出す。 | Gemini 1.5 Flash、GPT-4o、Qwen2-VL-72B | CUB、iNat21、Stanford Dogs、VegFruの3クラスずつのサブセット | なし |\[7\]
| You May Speak Freely: Improving the Fine-Grained Visual Recognition Capabilities of Multimodal Large Language Models with Answer Extraction（nlg2choice） | Logan Lawrence／WACV 2026（著者のページで確認。ICCV 2025ワークショップでの発表は未確認） | B-2-b・全体のみ | "a simple two-stage method which first asks the MLLM an open-ended question for the task with minimal constraints, then uses text-only constrained decoding to predict the most likely choice." → まず自由記述で答えさせ、次にテキストのみの制約付きデコードで選択肢に対応づける。 | Qwen-2.5VL-7B、Llama-3.2V-11B、InternVL3-8B | CUB-200、NABirds、iNat-Birds、Stanford Carsなど7つ | なし |\[8\]\[9\]
| UniFGVC: Universal Training-Free Few-Shot Fine-Grained Vision Classification via Attribute-Aware Multimodal Retrieval | Hongyu Guo／arXivのみ 2025 | ［境界］B-2-a・全体のみ | "off-the-shelf vision and text encoders embed query and template pairs, and FGVC is accomplished by retrieving the nearest template in the joint space." → 推論時にMLLMがテスト画像の属性記述を作るが、最終判定は埋め込みの最近傍検索。除外3に近い。 | 複数のMLLM（CDV-Captioner）＋既製のエンコーダ | 「12 FGVC benchmarks」 | なし |\[10\]\[11\]
| VR-RAG（Visual Re-ranking Retrieval-Augmented Generation）。arXiv 2505.05635で、現在のタイトルは"Neural Catalog: Scaling Species Recognition with Catalog of Life–Augmented Generation" | Faizan Farooq Khan（共著者にJun Chen、Mohamed Elhoseiny）／arXivのみ 2025（v1は2025年5月8日） | ［要確認］B-2-b・全体のみ | "We distill Wikipedia articles for 11,202 bird species into concise, discriminative summaries and retrieve candidates from these summaries." → 候補を検索で絞り、要約を添えてMLLMに最終判断させる（CascadeVLMに近い）。見本画像を使うか（B-2-aか）は未確認。 | Qwen2.5-VL（"VR-RAG improves the average performance of the state-of-the-art Qwen2.5-VL model by 18.0%"） | CUBを含む5つの鳥類データセット（"five bird classification benchmarks and two additional domains"） | なし |
| ［境界・除外2寄り］Visual-RFT: Visual Reinforcement Fine-Tuning | Ziyu Liu／ICCV 2025 | B-1-a・全体のみ（few-shotの細粒度分類） | "Extensive experiments show that Visual-RFT excels in fine-grained classification, open vocabulary detection, reasoning grounding and few-shot learning tasks." → 汎用の視覚RFTで、細粒度分類は評価タスクの1つにすぎない。問題設定の中心ではない。 | Qwen2-VL | Flowers、Pets、Cars、Aircraftなど（詳細は未確認） | なし |\[12\]
| ［境界・除外2寄り］CLS-RL: Image Classification with Rule-Based Reinforcement Learning（arXiv 2503.16188。現在のタイトルは"Think or Not Think: A Study of Explicit Thinking in Rule-Based Visual Reinforcement Fine-Tuning"） | Ming Li／arXivのみ 2025 | B-1-b・全体のみ（base-to-new） | "We discovered that CLS-RL outperforms SFT in most datasets and has a much higher average accuracy on both base-to-new and few-shot learning setting." → 画像分類全般が対象で、細粒度に限らない。 | 未確認 | 11個の分類データセット（細粒度を含む）。v1本文に "we conducted experiments on eleven datasets and two settings: few-shot and base-to-new" とある | なし |

## 3. 最重要の報告：「全体と局所・配分がサンプルごと・局所もサンプルごとに選ぶ」手法はあるか

**ありませんでした。** 自分での約18回の検索と、サブエージェントによる約15回の独立した検索と取得の両方で、同じ結論になりました。さらに一段ゆるい条件、つまり局所を一切MLLMに入れる細粒度認識の手法（局所のみ、または全体と局所・配分固定）も見つかっていません。

近い研究とそれぞれ条件を満たさない理由は次のとおりです。
- **CLIP-Guided Label-Free Discriminative Region Scoring for Fine-Grained Classification**（Yujie Zhu, arXiv 2607.13437, 2026）：細粒度データ（CUB、Flowers、Pets、Cars、Aircraft）で、SAMのマスクやランダムクロップをCLIPで採点し、上位k個をsoftmaxの重みで集約します。ただし "The aggregated local representation r is concatenated with the global image embedding ĝ… fed into a lightweight linear classifier." とあり、分類器はCLIP＋線形層で、全体と局所は連結されるだけです。したがって除外3（LLMを使わない）です。仮にMLLMに置き換えても「配分固定」にあたります。ランダムクロップがSAMマスクを5データセットすべてで上回ったと報告しています。\[13\]
- **LookWise**（arXiv 2603.00171）：初期確信度で「いつ見るか」を決め、注意に閾値をかけて「どこを見るか」を決めます。仕組みとしては「サンプルごと×局所選択」の形ですが、評価はAOKVQAやPOPEなどのVQAです（除外1）。\[14\]\[15\]
- **Vision-RL²**（arXiv 2609.19745）と、その前の**SD-RPN**（ICLR 2026）："Across six fine-grained benchmarks (V*, ZoomBench, HR-Bench 4K/8K, MME-RealWorld EN/CN)" とあり、"fine-grained" と書いていても高解像度VQAです（除外1）。\[16\]\[17\]

**示唆**：「確信度などで局所を使うかをサンプルごとに決め、注意や検出器で選んだ部位クロップをMLLMに入れて下位カテゴリ名を答えさせる」手法は、調べた範囲で前例がありません。B-1-bとB-2-bのどちらに置いても新規性を主張できそうです。ただし、学習を伴わないB-2-bの場合、LookWiseのような高解像度VQA側の手法を細粒度認識に移しただけと見られるおそれがあります。その差（単一の大きな物体で、部位の違いが決め手になる点）をはっきり示す必要があります。

## 4. 既知の6本の判定について
- **Finedefics**：B-1-a・全体のみで妥当です。論文の "global representations from the last layer of LLMs" は系列全体の表現のことで、局所ではありません。\[18\]
- **Fine-R1**：B-1-b・全体のみで妥当です（"few-shot base-to-new generalization setting"）。\[19\]
- **SARE**、**Zero-Shot FG（EMNLP Findings 2025）**：全体のみで妥当です。後者の注意介入（attention intervention）は、画像を切り出さないので局所には数えません。後者が見本画像を使うかどうか（B-2-aかB-2-bか）は、今回は再確認していません。\[20\]
- **RAR**：注意点が2つあります。(1) 本文の問題設定は汎用の視覚認識で、"5 fine-grained visual recognition benchmarks, 11 few-shot image recognition datasets, and the 2 object detection datasets under the zero-shot recognition setting" と書かれています。細粒度専用ではないため、除外2に当たる可能性があります。(2)\[21\] 細粒度ベンチマークはゼロショットの設定で評価しているとの記述があり、その実験だけならB-2-bにあたる可能性があります。PubMedに収録されているので学術誌に掲載されたとみられますが、誌名は未確認です。
- **CascadeVLM**：B-2-b・全体のみで妥当です。

## 5. 除外した論文の一覧

**除外1（高解像度・複数物体でのズーム／クロップVQA）**
- Vision-RL²: Region-Level Policy Optimization for Fine-grained MLLM Perception（arXiv 2609.19745）：評価はV*、ZoomBench、HR-Bench、MME-RealWorld\[16\]\[17\]
- Catching the Details: Self-Distilled RoI Predictors for Fine-Grained MLLM Perception（SD-RPN, ICLR 2026）\[22\]
- CropVLM（CVPR 2026 Workshop）：TextVQAなど\[23\]
- Zooming without Zooming: Region-to-Image Distillation（arXiv 2602.11858）：クロップは学習データを作るときだけ使い、評価はZoomBench\[24\]\[25\]
- LookWise（arXiv 2603.00171）、Visual Funnel（arXiv 2512.10362）、Zoom-Refine（arXiv 2506.01663）、FOCUS（NeurIPS 2025）、FineRS（arXiv 2510.21311）、RewardMap（arXiv 2510.02240）、Learning to Focus and Precise Cropping（arXiv 2603.27494）\[15\]\[26\]\[27\]\[28\]\[29\]\[30\]

**除外2（汎用の手法で、細粒度は評価に使う数字の1つにすぎないもの）**
- Visual-RFT（ICCV 2025）と CLS-RL（arXiv 2025）：上で境界例として挙げたとおり、厳密に解釈すれば除外です。
- Grasp Any Region（ICLR 2026）、Groma（ECCV 2024）：領域レベルのMLLMで、細粒度分類を問題設定にしていません。\[31\]\[32\]\[33\]\[34\]
- Rethinking Visual Information Processing in Multimodal LLMs（arXiv 2511.10301）：CLIPの複数の層の特徴を連結する汎用手法です。\[35\]

**除外3（推論にLLMを使わない、またはLLMを準備段階だけで使うもの）**
- FiNDR / Thinking Beyond Labels（CVPR 2026）："the verified names instantiate a lightweight multi-modal classifier used at inference time"\[36\]
- NeaR / Efficient Vocabulary-Free FGVR in the Age of MLLMs（arXiv 2505.01064）："finetunes a downstream CLIP model using labels generated by an MLLM"\[37\]
- FineR（ICLR 2024）\[38\]
- CLIP-Guided Label-Free Discriminative Region Scoring（arXiv 2607.13437）：局所は使うが、分類器はCLIP＋線形層\[13\]

## 6. ベンチマークだけを提案する論文（または主にベンチマーク）
- Benchmarking Large Vision-Language Models on Fine-Grained Image Tasks: A Comprehensive Evaluation（FG-BMK, arXiv 2504.14988）と、その拡張版「From Evaluation to Diagnosis」（arXiv 2606.19053）\[39\]\[40\]
- RealBirdID: Benchmarking Bird Species Identification in the Era of MLLMs（arXiv 2603.27033）：判定を控える（abstention）ことの評価\[9\]\[41\]
- FROW（Fine-grained Recognition Open World, arXiv 2512.10384）：ベンチマークに加え、mosaic dataやopen-world dataによる学習の工夫も提案しています。\[42\]手法の部分はB-1-a・全体のみにあたりますが、主な貢献はベンチマークです。
- Revisiting MLLMs: An In-Depth Analysis of Image Classification Abilities（arXiv 2412.16418）：分析論文\[43\]
- Finer（EMNLP 2024）：ベンチマーク部分（手法部分は表に掲載）

## Caveats
- 検索は予算の上限（約18回と、サブエージェントの約15回）に達しました。取りこぼしがありうるのは、2026年のワークショップ論文、クロップを付録やアブレーションだけで試している論文、中国語など英語以外の会場です。
- ReFine-RFTの閉集合／未知カテゴリの別、CLS-RLの使用モデル、使用データセットの一部は未確認です。
- AutoSEPの改善幅は版によって違います（arXiv版は "5% over the best-performing baselines"、NeurIPS版は3%）。nlg2choiceの改善幅（例：Qwen-2.5VL-7Bで+16.97）は二次情報のサイトの値で、本文では未確認です。\[7\]\[8\]\[44\]
- 「推論にLLMを用いる細粒度認識の手法は少なく、しかも全部が全体のみ」ということ自体が、今回の主な結果です。

## 出典

1. [Can Textual Reasoning Improve the Performance of MLLMs on Fine-grained Visual Classification?](https://arxiv.org/html/2601.06993v1)
2. [GitHub - jiezhu23/ReFine-RFT: \[CVPRF 2026\] Repository for "Can Textual Reasoning Improve the Performance of MLLMs on Fine-grained Visual Classification?" · GitHub](https://github.com/jiezhu23/ReFine-RFT)
3. [Can Textual Reasoning Improve the Performance of MLLMs on Fine-grained Visual Classification?](https://arxiv.org/html/2601.06993)
4. [Finer: Investigating and Enhancing Fine-Grained Visual ...](https://arxiv.org/html/2402.16315)
5. [Finer: Investigating and Enhancing Fine-Grained Visual ...](https://blender.cs.illinois.edu/paper/finer2024.pdf)
6. [Finer: Investigating and Enhancing Fine-Grained Visual Concept Recognition in Large Vision Language Models](https://arxiv.org/pdf/2402.16315)
7. <https://arxiv.org/pdf/2506.03195>
8. [You May Speak Freely: Improving the Fine-Grained Visual Recognition Capabilities of Multimodal Large Language Models with Answer Extraction — Lacuna](https://lacuna.tiptreesystems.com/work/you-may-speak-freely-improving-the-fine-grained-visual-recognition-capabilities/wrk_8c61d0c8b000c78a7ff86fd2d1b084fc)
9. [Logan Lawrence](https://www.loganlawrence.info/)
10. [UniFGVC: Universal Training-Free Few-Shot Fine-Grained Visual Classification via Attribute-Aware Multimodal Retrieval](https://arxiv.org/html/2508.04136)
11. [\[2508.04136\] UniFGVC: Universal Training-Free Few-Shot Fine-Grained Vision Classification via Attribute-Aware Multimodal Retrieval](https://arxiv.org/abs/2508.04136)
12. [Visual-RFT: Visual Reinforcement Fine-Tuning](https://arxiv.org/pdf/2503.01785)
13. <https://arxiv.org/html/2607.13437>
14. [LookWise: Knowing When and Where to Look for Fine-Grained Visual Reasoning in Multimodal Large Language Models · Pith](https://pith.science/paper/2603.00171)
15. [LookWise: Knowing When and Where to Look for Fine-Grained Visual Reasoning in Multimodal Large Language Models](https://arxiv.org/pdf/2603.00171)
16. [Paper page - Region-Level Policy Optimization for Fine-grained MLLM Perception](https://huggingface.co/papers/2609.19745)
17. [\[2609.19745\] Region-Level Policy Optimization for Fine-grained MLLM Perception](https://arxiv.org/abs/2609.19745)
18. [Analyzing and Boosting the Power of Fine-Grained Visual Recognition for Multi-modal Large Language Models](https://arxiv.org/html/2501.15140v3)
19. [Fine-R1: Make Multi-modal LLMs Excel in Fine-Grained Visual Recognition by Chain-of-Thought Reasoning](https://arxiv.org/pdf/2602.07605)
20. [Zero-Shot Fine-Grained Image Classification Using Large Vision-Language Models](https://arxiv.org/pdf/2510.03903)
21. [RAR: Retrieving and Ranking Augmented MLLMs for Visual Recognition | Request PDF](https://www.researchgate.net/publication/399708667_RAR_Retrieving_And_Ranking_Augmented_MLLMs_for_Visual_Recognition)
22. [arxiv.org](https://arxiv.org/pdf/2509.16944v3)
23. [\[2511.19820\] CropVLM: Learning to Zoom for Fine-Grained Vision-Language Perception](https://arxiv.org/abs/2511.19820)
24. [Zooming without Zooming: Region-to-Image Distillation for Fine-Grained Multimodal Perception](https://arxiv.org/html/2602.11858v1)
25. [arxiv.org](https://arxiv.org/abs/2602.11858v1)
26. [arxiv.org](https://arxiv.org/abs/2603.27494)
27. [arxiv.org](https://arxiv.org/pdf/2506.21710v2)
28. [Visual Funnel: Resolving Contextual Blindness in Multimodal Large Language Models](https://arxiv.org/pdf/2512.10362)
29. [RewardMap: Tackling Sparse Rewards in Fine-grained Visual Reasoning via Multi-Stage Reinforcement Learning](https://arxiv.org/pdf/2510.02240)
30. [FineRS: Fine-grained Reasoning and Segmentation of Small Objects with Reinforcement Learning](https://arxiv.org/pdf/2510.21311)
31. [Groma: Localized Visual Tokenization for Grounding ...](https://www.ecva.net/papers/eccv_2024/papers_ECCV/papers/01023.pdf)
32. [arxiv.org](https://arxiv.org/pdf/2510.18876v3)
33. [www.arxiv.org](https://www.arxiv.org/pdf/2404.13013)
34. [License: CC BY 4.0](https://arxiv.org/html/2510.18876v3)
35. [Rethinking Visual Information Processing in Multimodal LLMs](https://arxiv.org/pdf/2511.10301)
36. [Thinking Beyond Labels: Vocabulary-Free Fine-Grained Recognition using Reasoning-Augmented LMMs — Computer Vision](https://awesomepapers.io/computer-vision/papers/2512.18897)
37. [Efficient Vocabulary-Free Fine-Grained Visual Recognition ...](https://arxiv.org/pdf/2505.01064)
38. [Democratizing Fine-grained Visual Recognition with Large Language Models | OpenReview](https://openreview.net/forum?id=c7DND1iIgb)
39. [Benchmarking Large Vision-Language Models on Fine-Grained Image Tasks: A Comprehensive Evaluation](https://arxiv.org/pdf/2504.14988)
40. [Benchmarking Large Vision-Language Models on Fine-Grained Image Tasks: From Evaluation to Diagnosis](https://arxiv.org/pdf/2606.19053)
41. [RealBirdID: Benchmarking Bird Species Identification in the Era of MLLMs](https://arxiv.org/html/2603.27033)
42. <https://arxiv.org/abs/2512.10384>
43. [Revisiting MLLMs: An In-Depth Analysis of Image Classification Abilities](https://arxiv.org/pdf/2412.16418)
44. [Unlabeled Data Improves Fine-Grained Image Zero-shot Classification with Multimodal LLMs | OpenReview](https://openreview.net/forum?id=VNTj7PGlrz)
