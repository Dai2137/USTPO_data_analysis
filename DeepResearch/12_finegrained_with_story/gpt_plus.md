# 細粒度画像認識のLLM推論手法の分類

- **B-1. 事後学習する（細粒度データでMLLMを微調整）**  
  - **B-1-a. 閉集合（テストカテゴリは学習カテゴリと同じ）** – 全体のみ: Finedefics (ICLR 2025), Visual-RFT (arXiv 2025).  
  - **B-1-b. 開集合（未知カテゴリへの汎化）** – 全体のみ: DiVE-k (arXiv 2025), Fine-R1 (ICLR 2026).  

- **B-2. 事後学習しない**  
  - **B-2-a. 少数ショット利用** –  
    - 全体のみ: SARE (arXiv 2026), Zero-Shot FG (EMNLP Findings 2025), *RAR（未確認）*。  
    - 全体と局所・配分がサンプルごと: UniFGVC (arXiv 2025).  
  - **B-2-b. ゼロショット（見本なし）** – 全体のみ: CascadeVLM (EMNLP Findings 2024).  

## 論文一覧と分類・要約

| 論文名（筆頭著者・会場年） | 葉 | 判定根拠（英語引用）・要約 | 使用MLM/LLM | 評価データセット | 局所利用方法 |
|:---------------------------|:--:|:------------------------------|:-----------:|:---------------:|:-------------|
| *Analyzing and Boosting the Power of Fine-Grained Visual Recognition for MLLMs*<br>（Hulingxiao He ら, ICLR 2025） | B-1-a 全体のみ | “we present Finedefics, an MLLM that enhances the model’s FGVR capability by incorporating informative attribute descriptions of objects into the training phase...we employ contrastive learning on object-attribute pairs and attribute-category pairs...”。**要約:** 属性記述を学習時に組み込み、属性・カテゴリ間のコントラスト学習で表現を強化する手法。 | MLLM（内部モデル、論文では非公開） | CUB, Stanford Cars など複数のFGVRベンチ | なし（全体のみ） |
| *Visual-RFT: Visual Reinforcement Fine-Tuning*<br>（Ziyu Liu ら, arXiv 2025） | B-1-a 全体のみ | “Visual-RFT...extends RFT to visual tasks...The LVLM receives an image and prompt, generates multiple response trajectories with reasoning tokens, and is updated by policy optimization... Visual-RFT improves accuracy by 24.3% over the baseline in one-shot fine-grained classification。”**要約:** 画像とプロンプトから複数の推論経路を生成し、GRPO強化学習でLVLMを微調整。少数ショットの細粒度分類精度が大幅に向上。 | Qwen2.5-VL-7B | Flowers102, Stanford Dogs, Aircraft, Stanford Cars など | なし（全体のみ） |
| *DiVE-k: Differential Visual Reasoning for Fine-Grained Image Recognition*<br>（Raja Kumar ら, arXiv 2025） | B-1-b 全体のみ | “In the standard base-to-novel generalization setting, DIVE-k achieves ... improvements of +10.04% and +6.16% respectively over QWEN2.5-VL-7B and ViRFT baselines”<br>“DiVE-k… leverages the model’s own top-$k$ predictions as multiple-choice options during training, so that the model must perform fine-grained differential reasoning among plausible options。”**要約:** モデル自身の上位生成を選択肢とする複数選択問題を作り、GRPO強化学習で差分推論能力を学習。ベースから未知クラスへのゼロショット性能を大幅に改善。 | Qwen2.5-VL-7B | CUB-200, OxfordFlowers-102, Stanford Dogs, Stanford Cars, FGVC-Aircraft | なし（全体のみ） |
| *Fine-R1: ... FGVR by Chain-of-Thought Reasoning*<br>（Hulingxiao He ら, ICLR 2026） | B-1-b 全体のみ | “we propose Fine-R1, an MLLM tailored for FGVR through an R1-style training framework: (1) Chain-of-Thought Supervised Fine-tuning... (2) Triplet Augmented Policy Optimization... With only 4-shot training, Fine-R1 outperforms existing general and reasoning MLLMs...in identifying both seen and unseen sub-categories。”**要約:** CoT事前微調整と3点間強化学習でMLLMを学習。わずか4ショットの学習で既知・未知両方の細粒度カテゴリ認識精度をCLIP系手法や従来MLLMより向上。 | MLLM（論文ではLLaVAまたはQwen2-VL推定） | CUB-200, Stanford Dogs, Flowers102 など（FGVRベンチ） | なし（全体のみ） |
| *SARE: Sample-wise Adaptive Reasoning for FGVR*<br>（Jingxiao Yang ら, arXiv 2026） | B-2-a 全体のみ | “SARE adopts a cascaded design that combines fast candidate retrieval with fine-grained reasoning, invoking the latter only when necessary... SARE incorporates a self-reflective experience mechanism that leverages past failures to provide transferable discriminative guidance during inference, without any parameter updates。”**要約:** サンプルごとにCLIP類モデルで候補を絞り、LLMによる詳細推論は必要時のみ実行。過去の失敗経験を自己参照し識別的手がかりを補う訓練不要のフレームワーク。 | 既存のLVLM（例: LLaVA、InternVL等） | CUB-200, Stanford Cars, Flowers102, Pets37, Aircraft など（5データセット） | なし（全体のみ） |
| *Zero-Shot FG Image Classification using LVLMs*<br>（Atabuzzaman ら, EMNLP Findings 2025） | B-2-a 全体のみ | “we present a novel method that transforms zero-shot fine-grained classification into a visual question answering framework, leveraging LVLMs’ comprehensive understanding rather than relying on direct class name generation。”**要約:** 直接クラス名を生成する代わりにVQA形式でLLMに問い、イテレーティブなMCQ方式で細粒度分類するゼロショット手法。 | LLaVA, InternVL, Qwen2-VL 等のLVLM | CUB-200, Stanford Cars, Flowers102, Pets37, Aircraft（5つのFGデータセット） | なし（全体のみ） |
| *UniFGVC: Universal Training-Free Few-Shot FGVC*<br>（Tianzhuo Mao ら, arXiv 2025） | B-2-a 全体＋局所（サンプルごと） | “Our CDV-Captioner… adopts a chain-of-thought prompting strategy to progressively guide MLLM in identifying and articulating the most discriminative regions through comparative reasoning with reference samples. It then converts these region-level insights into structured textual descriptions…。”**要約:** まず類似例画像を参照し、MLLMのCoT推論で対象画像の判別的部位を特定・記述。部位属性を統合した構造化テキストを生成し、テンプレート画像データベースとの類似度検索で分類（MLLMは推論時に使用）。 | GPT-4V, Qwen-VL 等のMLLM | CUB-200, Stanford Cars, Flowers102, Dogs, Aircraft, iNaturalist 等（12データセット） | 参照画像と比較しサンプルごとに部位を発見・記述し、それらの属性記述を最終特徴として使用（global＋local, 動的配分） |
| *CascadeVLM: Enhancing FG Classification via Cascaded VLMs*<br>（Canshi Wei ら, EMNLP Findings 2024） | B-2-b 全体のみ | “we introduce CascadeVLM, which integrates the complementary capabilities of CLIP-like models and LVLMs to perform fine-grained image classification. The key idea is to leverage the CLIP-like models as a class filter for LVLMs。”**要約:** まずCLIPモデルで候補クラスを絞り込み、その後LVLMに最終判断をさせる2段階推論。CLIPの確信度でLVLMの使用有無を制御し、ゼロショット/少数ショット分類を実現。 | CLIP類モデル + LLaVA等のLVLM | Stanford Cars, iNaturalist, SUN397 など（6データセット） | なし（全体のみ） |

## 最重要の発見

「全体と局所・配分がサンプルごと」に該当する手法として**UniFGVC**が見つかりました。この手法はB-2-a（事後学習なし・few-shot）に属します。UniFGVCでは、各入力画像に対して類似参考画像を取り込み、MLLMに比較推論させて最も判別的な領域（部位）を検出・記述します。このように局所的情報をサンプルごとに動的に利用する点が特徴です。

## 除外論文一覧

- **除外1（画像内複数物体・高解像度小物対象）**：画像内の小物をズーム/クロップして認識する手法（例: **Chain-of-Focus**、**CropVLM**、**ViCrop**、**DyFo** など）。これらはFine-grained認識をタスクとせず、VQAや文書解析ベンチマーク（TextVQA, DocVQA, V*Bench, HR-Benchなど）向けの手法です。
- **除外2（汎用手法で設定外）**：問題設定が細粒度ではなく、CUB/Carsの結果のみ報告する一般手法（例: テスト時適応やキャリブレーション研究など）。CLIPゼロショットや汎用変換モデルの性能改善研究は対象外とします。
- **除外3（LLM非推論）**：推論時にLLMを用いず、クラス記述生成など準備段階のみでLLMを使う手法（例: **FineR** (ICLR 2024)、**microCLIP**, **FAIR**, **LAGO**, **CuPL** など）。いずれもLLMで特徴生成するが、最終判定はCLIP類似度など従来手法です。
- **除外4（ベンチマーク提案のみ）**：細粒度タスクに対する新たな評価基準やデータセットのみを提案する論文。研究手法提案を含まないものは報告対象外ですが、発見し次第別途リスト化します。

