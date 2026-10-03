# 事後学習によるVLMの細かい視覚的識別能力の向上 — 手法の先行研究調査レポート

## TL;DR
- 「見た目が紛らわしい対象を細かく見分ける」能力は、先行研究では VLM の**接地された知覚（grounded perception）**の欠損、より具体的には CLIP 系ビジョンエンコーダの「CLIP-blind pairs」問題として概念化されており、これは推論の前提条件でありながらモデルサイズやデータ量のスケールでは埋まらない「根本ギャップ」として位置づけられている。人間は MMVP で平均95.7%正答するのに対し、GPT-4V は人間比で50pt超劣後する（Tong et al., CVPR 2024）。
- 事後学習で当該能力を伸ばす主要アプローチは4系統に整理できる：(1) ビジョンエンコーダの生成的/自己教師あり後付け最適化（DIVA, GenHancer, un²CLIP）、(2) ハードネガティブ対比学習・選好最適化（S-VCO, AHNPL, Finedefics）、(3) 検証可能報酬による強化学習（Visual-RFT, Visual Jigsaw, PIVOT, TWIN）、(4) 高品質識別データによる指示チューニング（Cambrian-1/CV-Bench, Molmo/PixMo, Fine-R1）。改善幅は MMVP-VLM で +3〜13.3pt、fine-grained分類で最大 +24.3pt。
- ただしこれらは診断的ベンチマークの根本ギャップを**部分的にしか埋めていない**（NaturalBench で最良の GPT-4o が依然人間に52%劣後、オープン系は55〜70%劣後）。この研究がメインカンファレンスを狙うなら、「意匠識別精度」ではなく「シルエット同型・意味カテゴリ相違という統制条件下での fine-grained discrimination という能力プローブ」と「事後学習レシピの転移性」に軸足を置くべきである。

## Key Findings

1. **「細かい視覚的識別」は VLM の中核的欠損として確立された研究テーマである。** Tong et al. (CVPR 2024, "Eyes Wide Shut?") が CLIP-blind pairs（CLIPでは近いが DINOv2 では遠い画像対）で MMVP を構築し、これが VLM の「systematic shortcomings（体系的欠陥）」であること、CLIP のインスタンスレベル対比事前学習が方向・数・小さな文字などを符号化できないことに根本原因があること、そしてスケールでは改善しないことを示した。依頼者のベンチマーク（DINOv2埋め込みで正解と酷似した誤答肢を選ぶ）は、まさにこの CLIP-blind pairs の方法論を意匠図面ドメインに拡張したものと位置づけられる。

2. **事後学習の効き方は「どこを・何で学習するか」で系統立てられる。** ①エンコーダ側の生成的フィードバック（DIVA/GenHancer/un²CLIP: MMVP-VLM を +3〜13.3pt）、②対比・選好最適化（S-VCO: 幻覚を最大22%削減、Finedefics: 属性記述でFGVR向上）、③検証可能報酬RL（Visual-RFT: 約100サンプルの1-shot fine-grained 分類で +24.3%、同設定のSFTは-4.3%と低下）、④識別志向データのSFT（Molmo/PixMo のポインティング、Cambrian-1 の vision-centric データ配合）。

3. **RLはSFTより「視覚表現そのもの」を書き換える。** "RL makes MLLMs see better than SFT"（ICLR 2026, PIVOT）は、事後学習が vision encoder の表現を再構成し、RL（DPO）がSFTより強く・局所的に精緻な視覚表現を生むことを勾配可視化で示した。これは依頼者の LoRA（SFT系）による +1.9pt という小さい改善幅が「手法選択の問題」である可能性を強く示唆する。

4. **根本ギャップは部分的にしか埋まっていない。** 個別手法は特定ベンチマークで数〜十数ポイント改善するが、NaturalBench では最良の GPT-4o でも人間（>90%）に52%劣後し、オープン系は55〜70%劣後。fine-grained タスクでは LVLM が専用モデルに依然及ばない（FG-BMK の診断）。ここに「まだ埋まっていない手法上のギャップ＝研究機会」がある。

5. **メイン採択の型は「能力プローブ＋根本原因＋転移するレシピ」である。** 成功例（Eyes Wide Shut, Cambrian-1, NaturalBench, Visual-RFT, PIVOT）は共通して、(i) 失敗をエンコーダ/整合の体系的限界として根本原因化し、(ii) 能力を切り出す vision-centric な診断ベンチマークを提示し、(iii) タスク横断で転移する一般的事後学習レシピを出し、(iv)「接地された知覚は推論の前提」という大きな主張に接続する。

---

## A. 「細かい視覚的識別」はVLMのどの能力として概念化されているか

先行研究は「fine-grained visual discrimination」を、単なる分類精度ではなく、**VLM が視覚信号を正確に接地（ground）して意味に結びつける能力**の指標として概念化している。

- **CLIP-blind pairs / 視覚的接地の欠損（Tong et al., CVPR 2024, "Eyes Wide Shut?"）**：CLIP の埋め込み空間で酷似する（しかし視覚的に明確に異なる）画像対を VLM が見分けられないことを「systematic shortcomings」と呼ぶ。原因は CLIP のインスタンスレベル対比事前学習が「orientation, counting, small text」などを明示的に符号化しないこと。重要なのは、これがダウンストリームの MLLM に「継承される（inherited）」盲点であり、視覚推論・visual grounding の前提条件が崩れている、という位置づけである。人間はこの MMVP で平均95.7%正答する一方、GPT-4V は人間比で「exceeding 50%」の差で劣後する。arXiv:2401.06209。
- **接地された知覚が推論の前提（Cambrian-1, NeurIPS 2024 Oral）**：「design choices for vision components are often insufficiently explored... This gap hinders accurate sensory grounding in real-world scenarios」と述べ、視覚表現の質＝MLLM能力の決定要因と位置づける。arXiv:2406.16860。
- **fine-grained能力が上位能力の土台（Finedefics, ICLR 2025）**：FGVR の失敗が「object-centric visual question answering and reasoning」といった高次能力に負の波及を及ぼす、と明示。すなわち fine-grained discrimination は下流のVQA・推論の前提条件。arXiv:2501.15140。
- **知覚と推論の分離（VisOnlyQA など）**：VisOnlyQA は「純粋な視覚知覚能力を推論から独立に評価する」ことを狙い、fine-grained知覚を推論から切り離して測る枠組みを提供。perception-focused ベンチマークでの fine-tuning だけでは根本改善に不十分と報告。
- **診断的枠組み（FG-BMK, arXiv:2504.14988）**：LVLM の fine-grained 失敗を「視覚表現の不足／視覚-意味接地の弱さ／fine-grainedな知識の欠如」のどれに由来するか切り分ける diagnostic 設計。fine-grained discrimination は「feature-level visual discriminability」と「dialogue-level semantic recognition」の2軸で測る。

**この研究への含意**：依頼者のベンチマークは「意味カテゴリは異なるがシルエットが同型」という統制条件を持つため、A の系譜で言えば「意味的手がかり（language shortcut）を封じて純粋な視覚的識別を測る」probe として非常に強い。論文では「意匠識別」ではなく「grounded fine-grained visual discrimination の診断」として能力を抽象化して定義すべきである。特に「N=4→8への難化」は Cambrian-1/NaturalBench 流の "blind solution 排除" と同じ設計思想として明示できる。

---

## B.【中心】事後学習でVLMの細かい視覚的識別能力を向上させた研究

以下、アプローチ系統ごとに代表研究を表にまとめる。

### B-1. ビジョンエンコーダの生成的/自己教師あり後付け最適化

| 手法名 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチマーク | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| DIVA | 2024/25 | ICLR 2025 | CLIP各種(OpenAI/MetaCLIP/SigLIP等) | 拡散モデルの生成的フィードバックによる自己教師あり最適化（画像のみ、テキスト不要） | CC-3M等の画像データ | MMVP-VLM, LLaVA, MMBench | MMVP-VLM +3〜7%（OpenAI ViT-L: 19.3→25.9, +6.6pt） | 29の分類/検索ベンチでゼロショット性能維持、セグメンテーション向上 | arxiv.org/abs/2407.20171 |
| GenHancer | 2025 | ICCV 2025 | CLIP各種 | 軽量デノイザによる2段階の生成的後学習（globalトークンのみ条件付け） | 画像データ | MMVP-VLM, CV-Bench, NaturalBench | MMVP-VLM +6.0%(OpenAICLIP, →31.9)、色知覚 46.7→80.0% | MLLMのvision-centric性能向上 | arxiv.org/abs/2503.19480 |
| un²CLIP | 2025 | NeurIPS 2025 | CLIP各種 | unCLIP生成モデルを反転してCLIP画像エンコーダを微調整 | 画像データ | MMVP-VLM | OpenAI ViT-L: 19.3→32.6%（+13.3pt、DIVA25.9/GenHancer31.9を上回る）、色知覚53.3→80.0%、OpenCLIP ViT-H: 28.9→36.3% | ゼロショット・下流MLLM性能維持/向上 | arxiv.org/abs/2505.24517 |
| Kernel-based Embedding Alignment | 2025 | arXiv(preprint) | CLIP各種 | DINOv2埋め込みへのカーネルベース教師なし整合 | 画像データ | MMVP-VLM, MMVP(LLaVA) | MMVP-VLM +2.2〜3.0%、LLaVA置換で誤答率減 | 下流MLLMに転移 | arxiv.org/abs/2506.02557 |

### B-2. ハードネガティブ対比学習・選好最適化

| 手法名 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチマーク | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| S-VCO (+MVC) | 2025 | ACL 2025 | LLaVA系VLM | 対称的視覚対比の選好最適化（最小差分画像対で視覚詳細への注意を強制） | MVC（視覚counterfactual対を自動フィルタ・拡張） | MMVP, CV-Bench, MMHal, MMVet等 | 幻覚を最大22%削減、vision-centricで大幅向上 | DPO/mDPOを上回り、general性能も維持/向上 | arxiv.org/abs/2502.13928 |
| AHNPL | 2025 | IJCAI 2025 | CLIP系VLM | 画像側ハードネガティブ生成＋動的マージン対比学習 | 3公開compositionalデータセット | compositional reasoning系 | CRタスクで一貫向上 | 視覚エンコーダの訓練不足を補正 | ijcai.org/proceedings/2025/605 |
| Finedefics | 2025 | ICLR 2025 | Idefics2ベース | 属性記述を介した対比整合＋分類中心の指示チューニング（類似誤カテゴリをハードネガティブに） | 6 FGVRデータセット | CUB, Stanford Dogs/Cars, FGVC-Aircraft等 | 同規模MLLMを凌駕、Idefics2/Qwen-VL-Chat比で大幅向上 | 汎用能力を保持 | arxiv.org/abs/2501.15140 |
| CLoVe | 2024 | arXiv | 対比VLM(CLIP) | 合成キャプション＋ハードネガティブ微調整＋model patching | 合成キャプション画像 | compositionality系 | 構成性を大幅改善 | 他タスク性能をpatchingで保持 | arxiv.org/abs/2402.15021 |

### B-3. 検証可能報酬による強化学習（RLVR/GRPO/DPO）

| 手法名 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチマーク | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| Visual-RFT | 2025 | ICCV 2025 | Qwen2-VL-2B/7B | GRPO＋検証可能報酬（分類はCLS報酬、検出はIoU報酬） | 少数（1-shot〜4-shot、約100サンプル） | fine-grained分類(Flower102/Pets37/Cars/Aircraft), 検出, grounding | 1-shot fine-grained分類で +24.3%（同設定SFTは-4.3%）、4-shot検出平均+25.9 | SFTを一貫して凌駕、強い汎化・データ効率 | arxiv.org/abs/2503.01785 |
| Visual Jigsaw | 2025 | arXiv(preprint) | Qwen2.5-VL等 | 自己教師ありRLVR（パッチ順序復元、アノテーション不要） | 自動生成（画像/動画/3D） | fine-grained知覚, 時間推論, 3D空間 | fine-grained知覚で一貫向上 | 生成モジュール不要、text-only出力と互換 | arxiv.org/abs/2509.25190 |
| PIVOT ("RL makes MLLMs see better than SFT") | 2025/26 | ICLR 2026 | CLIP/SigLIP + LLM | DPO中心のRLをvision encoder補助学習として再定式化 | 3M指示データ＋20K選好対 | ImageNet分類, セグメンテーション, vision-centric VQA | RLがSFTより強く局所的な視覚表現、標準vision事前学習の<1%計算量で上回る | vision encoderを根本的に書き換え | arxiv.org/abs/2510.16333 |
| Latent Visual Reasoning (LVR) | 2025 | arXiv(preprint) | Qwen2.5-VL-3B | 潜在視覚トークン再構成＋GRPO | ViRLデータ | MMVP, V*Bench | MMVP 66.67→71.67% | perception-intensive VQAで向上 | arxiv.org/abs/2509.24251 |
| Same or Not? (TWIN) | 2025 | arXiv(preprint) | Qwen2.5-VL-3B, InternVL3.5-1B | 二値outcome報酬のRL（同一インスタンスか否かのペア判定） | TWIN（画像対クエリ、大規模） | FGVQA（MET/INQUIRE/CUB/ILIAS/LANDMARKS） | FGVQAで最大 +19.3% | general VQA性能を損なわず | arxiv.org/abs/2512.23592 |

### B-4. 高品質な識別志向データによる指示チューニング

| 手法名 | 年 | 会議 | ベースモデル | 事後学習の種類 | 学習データ・規模 | 評価ベンチマーク | 向上幅 | 他能力への影響 | URL |
|---|---|---|---|---|---|---|---|---|---|
| Cambrian-1 (SVA + vision-centric data) | 2024 | NeurIPS 2024 Oral | 各種LLM＋20+ vision encoder | Spatial Vision Aggregator接続子＋vision-centric指示チューニング | 公開ソースからキュレートした指示データ | CV-Bench（新規vision-centric） | vision-centricで SOTA、SSL特徴統合でgrounding向上 | 汎用MLLM能力も向上 | arxiv.org/abs/2406.16860 |
| Molmo / PixMo | 2024/25 | CVPR 2025 | 各種 | ポインティング・カウンティング・密キャプションデータのSFT（VLM蒸留なし） | PixMo（点付き参照表現、162k注釈/73k画像等） | 学術ベンチ＋人手評価 | オープン系でSOTA、grounding/counting強化 | 幅広いタスクで強い | arxiv.org/abs/2409.17146 |
| Fine-R1 | 2026 | ICLR 2026 | Qwen2.5-VL-3B/7B | Chain-of-Thought＋RFT（視覚分析→候補→比較→予測） | FGVR CoTデータ（GPT-4o生成） | Stanford Cars, FGVC-Aircraft, ImageWikiQA | seen +7.73%(7B)、unseen +9.28%、SigLIP-Lも凌駕 | 汎用VQAで維持/向上 | arxiv.org/abs/2602.07605 |

**この研究への含意**：依頼者の現状（Qwenへのタイトル特化LoRA=SFT系で+1.9pt）は、B-3の知見（RL/選好最適化がSFTより視覚表現を強く書き換える）と対照的である。意匠図面のように「正解／視覚的酷似誤答」のペア構造が自然に得られるドメインは、S-VCO（最小差分画像対）や TWIN（同一か否かのペア判定RL）、Visual-RFT（検証可能報酬）の設計と極めて相性が良い。手法貢献の中心を「SFTからRLVR/対比選好への転換」に置くのが有望。

---

## C. これらの事後学習が「診断的ベンチマーク」上の根本ギャップをどこまで埋めたか

**部分的には埋めたが、人間性能とのギャップは依然大きい。**

- **エンコーダ後付け系（DIVA/GenHancer/un²CLIP）**：MMVP-VLM で顕著な改善（+3〜13.3pt）を出すが、絶対値は依然低水準（OpenAI ViT-L で un²CLIP でも32.6%）。これは「CLIP-blind の根本原因を緩和しつつも解消はしていない」ことを示す。
- **MLLM側の知覚（MMVP本体）**：LVR で Qwen2.5-VL の MMVP を 66.67→71.67% に改善したが、人間（MMVPで95.7%）には遠い。
- **NaturalBench**：53のSOTA VLMを評価し（human-verified 10,000 VQAサンプル）、最良のGPT-4oでも人間（>90%）に52%劣後、オープン系（BLIP-3, Cambrian-1, LLaVA-OneVision, Llama3.2-Vision, Molmo, Qwen2-VL）は55〜70%劣後。事後学習で個別に改善しても、この「人間なら容易・モデルは困難」の構造的ギャップは残存。
- **FG-BMK の診断**：LVLM は「視覚表現・意味接地・モダリティ整合・カテゴリ知識」が絡み合ったボトルネックを持ち、fine-grained では依然専用モデルに劣る。直接的なfine-grained微調整は汎用性能を落とす（catastrophic forgetting）ことも報告（"Towards Fine-Grained Recognition..." arXiv:2512.10384）。
- **知覚は訓練データ omission か構造的限界か**：VisOnlyQA は「perception-focused ベンチマークでの fine-tuning だけでは根本改善に不十分」と報告し、単純なデータ追加では埋まらない部分があることを示す。

**この研究への含意**：依頼者の GPT-5 ゼロショット8択51%という数字は、まさに C の「根本ギャップが残存している」証拠として提示できる。すなわち、この研究の価値は「意匠識別を解く」ことではなく、「既存の事後学習レシピが統制された fine-grained discrimination probe 上でどこまで／なぜ限界を持つか」を診断し、そのギャップを突く新レシピを示すことにある。人間性能（意匠専門家 or 一般被験者）を測っておくとギャップ提示が強力になる。

---

## D. 論文のポジショニング — メインカンファレンス採択の型

「識別ベンチマーク＋事後学習手法」型が applications/industry track ではなくメイン（CVPR/ICCV/ECCV/NeurIPS/ICLR）に通る際の共通の型は、以下4要素の組み合わせである。

1. **根本原因の一般化（root-cause framing）**：失敗を特定ドメインではなく「ビジョンエンコーダ／モダリティ整合の体系的限界」に帰属させる。
   - Eyes Wide Shut：「visual capabilities... still exhibit systematic shortcomings」＋CLIP-blind pairs を根本原因として特定（CVPR 2024）。
   - PIVOT：「a void in the understanding of the vision encoder, which determines how MLLMs perceive images」（ICLR 2026）。
2. **能力を切り出す vision-centric 診断ベンチマーク**：言語ショートカットを封じて特定能力を isolate する設計。
   - NaturalBench：「vision-centric design by pairing each question with two images that yield different answers, preventing 'blind' solutions」（NeurIPS 2024）。
   - Cambrian-1：CV-Bench を導入し既存ベンチの限界を批判的に検討（NeurIPS 2024 Oral）。
3. **タスク横断で転移する一般的事後学習レシピ**：単一データセットの精度でなく、複数タスク・複数バックボーンへの転移を示す。
   - Visual-RFT：「competitive performance and advanced generalization ability... compared with SFT」（ICCV 2025）。
   - PIVOT：「a PIVOT-trained vision encoder outperforms even larger and more heavily-trained counterparts... <1% of the computational cost」（ICLR 2026）。
4. **「接地された知覚は推論の前提」という大きな主張への接続**：Cambrian-1（sensory grounding）、Finedefics（FGVRがVQA・推論に波及）。

**この研究への含意**：依頼者は「意匠特許画像検索・分類（industry寄り）」から「fine-grained visual discrimination の能力プローブ＋事後学習レシピ（main寄り）」へと軸足を移すべきである。具体的には、(a) 意匠図面を「意味カテゴリは異なるがシルエット同型」という統制条件で fine-grained discrimination を isolate する診断ベンチマークとして提示し、(b) DINOv2ベースの誤答肢構築を「CLIP-blind pairs の意匠ドメイン一般化」として根本原因に接続し、(c) 提案事後学習が意匠以外のドメイン（既存のMMVP/NaturalBench/FGVR）にも転移することを示すことで、industry track の外に出られる。

---

## E. 指導教員フィードバック3点への回答

### フィードバック1：「このベンチマーク／事後学習はマルチモーダルVLMの"何の能力"を伸ばしているのか」

**事後学習の観点から現時点で言えそうな主張：**
- 伸ばしているのは「grounded fine-grained visual discrimination」＝視覚信号を正確に接地し、言語ショートカットに頼らず微細な視覚差を意味に結びつける能力。先行研究では CLIP-blind pairs 問題（Eyes Wide Shut, CVPR 2024）、visual detail capturing（un²CLIP）、fine-grained discriminability（FG-BMK）として概念化されている。
- この能力は「下流の visual grounding・VQA・推論の前提条件」であり（Finedefics, Cambrian-1）、単独タスク精度ではなく汎用能力の土台として意味づけられる。
- 事後学習手法の種類によって「エンコーダの表現（DIVA/PIVOT）」「モダリティ整合（Finedefics/S-VCO）」「推論プロセス（Fine-R1/Visual-RFT）」のどこを改善するかが分かれ、これ自体が「何の能力か」を分解する軸になる。

**まだ埋まっていない手法上のギャップ（＝この研究が突けるところ）：**
- 既存の fine-grained 研究は「自然種（鳥・車・航空機）」中心で、「意味カテゴリが異なるのにシルエットが同型」という条件を統制した probe が存在しない。依頼者のベンチマークはこの空白を埋める。
- 「N択の難化（4→8）」で識別能力を連続的に測る枠組みは、既存の二値対（MMVP/NaturalBench）より細かい能力解像度を与えられる。

### フィードバック2：「人間ならできるのにVLMは何の能力が欠けてできないのか」

**事後学習の観点から現時点で言えそうな主張：**
- 欠けているのは主に「ビジョンエンコーダのインスタンスレベル対比事前学習が捨てている微細な視覚情報」であり（Eyes Wide Shut）、この盲点が下流MLLMに継承される。人間はMMVPで95.7%、NaturalBenchで>90%正答する一方、GPT-4V/GPT-4oは大きく劣後（MMVPで50pt超、NaturalBenchでGPT-4oが52%劣後）。
- RLがSFTより視覚表現を強く書き換える（PIVOT）ことから、欠損は「知識」ではなく「事後学習の目的関数が視覚詳細への接地を明示的に報酬化していないこと」に一因がある（S-VCO の仮説「existing VLMs are not explicitly trained to generate texts that are accurately grounded in fine-grained image details」）。

**まだ埋まっていない手法上のギャップ：**
- 「シルエット同型・意味相違」という条件下で、VLMの失敗が (i) エンコーダの特徴分離不足か、(ii) 視覚-意味接地の弱さか、(iii) 言語事前分布への過依存か、を切り分ける診断がまだ意匠ドメインで行われていない。FG-BMK的な切り分けを意匠 probe に適用すれば、根本原因議論に直接接続できる。

### フィードバック3：「industry track に見えないよう、VLMの本質的限界の議論につなげたい」

**事後学習の観点から現時点で言えそうな主張：**
- メイン採択の型（root-cause化＋vision-centric診断ベンチ＋転移するレシピ＋grounded perception への接続）に沿えば、意匠識別は「本質的限界のケーススタディ」に昇格できる。
- 特に「事後学習しても根本ギャップは部分的にしか埋まらない」（NaturalBench の52〜70%ギャップ残存、VisOnlyQAのfine-tuning不十分報告）という否定的知見は、本質的限界の議論そのものであり、強い論文の芯になる。

**まだ埋まっていない手法上のギャップ：**
- 既存のRLVR/選好最適化（Visual-RFT, S-VCO, TWIN）は自然画像中心で、意匠図面のような「線画・低テクスチャ・シルエット支配」ドメインでの有効性が未検証。ここは新規性を主張できる。
- 「どの事後学習がどの根本原因を埋め、どれが埋めないか」を統制ベンチ上で体系比較した研究がない。依頼者は「意匠 discrimination probe 上での事後学習レシピの体系的診断＋新レシピ」という構成で、industry を超える貢献を主張できる。

## 具体的な次アクション（推奨）
1. **手法軸の転換（最優先）**：現行のタイトル特化LoRA（SFT）を、①S-VCO型の最小差分画像対による選好最適化、②Visual-RFT/TWIN型の検証可能報酬RL（正解/酷似誤答のペア構造をそのまま報酬に使える）、の2系統で置き換え実験する。ベンチマークは「意匠 discrimination probe（4択・8択）」＋転移確認用の MMVP/NaturalBench。**判断基準**：RL系がSFT系（現行+1.9pt）を有意に上回れば「手法貢献」として成立。上回らなければ、エンコーダ側（DIVA/un²CLIP型のDINOv2整合）にボトルネックがある可能性が高く、そちらへ軸を移す。
2. **診断の実装**：FG-BMK流に「視覚表現の分離不足／視覚-意味接地／言語事前分布依存」の3切り分けを意匠 probe で実施。**判断基準**：エンコーダ特徴（DINOv2 vs CLIP）で線形分離可能なのに VLM が誤答するなら「接地の問題」＝事後学習で埋められる余地が大きい、と主張できる。
3. **人間性能の測定**：意匠図面 probe で一般被験者（と可能なら意匠審査経験者）の正答率を取り、MMVP(95.7%)/NaturalBench(>90%)と同型の「人間-モデルギャップ」を提示する。
4. **転移の実証**：意匠データで学習した事後学習が、自然画像の fine-grained ベンチ（MMVP/CUB/Cars）にも転移するか（あるいはしないか）を測る。転移すれば「一般的レシピ」、転移しなければ「ドメイン特有の限界の発見」として、いずれもメイン級の主張になる。

## Caveats
- 数値の出典・査読状況：MMVP(CVPR2024)、Cambrian-1(NeurIPS2024)、NaturalBench(NeurIPS2024 D&B)、DIVA(ICLR2025)、Finedefics(ICLR2025)、Visual-RFT(ICCV2025)、S-VCO(ACL2025)、AHNPL(IJCAI2025)、GenHancer(ICCV2025)、un²CLIP(NeurIPS2025)、PIVOT/"RL makes MLLMs see better"(ICLR2026)、Molmo(CVPR2025)、Fine-R1(ICLR2026) は査読付き。Kernel-based alignment、Visual Jigsaw、LVR、TWIN、FG-BMK はarXivプレプリント段階（2025-2026）であり、数値は暫定値として扱うべき。
- GPT-4V の MMVP 具体値（一般に約38.7%と引用される）は論文の図から読み取られる値であり、本文テキストでは「人間との差が50pt超（exceeding 50%）」という形で述べられている点に注意。
- TWIN の「RLとSFTの正確な差分」は abstract の「最大+19.3%」がヘッドライン値であり、表内の RL単独セルの厳密値は原論文（arXiv:2512.23592）で要確認。TWIN は執筆時点で査読会議未確定のプレプリント。
- 依頼者の GPT-5 ゼロショット結果および Qwen LoRA +1.9pt は独自実験値であり、外部先行研究と直接比較する際はプロンプト・設問形式・N択数の差に留意が必要。
- Visual-RFT の +24.3% は「1-shot・約100サンプル」という特殊な少数データ設定での値であり、フルデータ設定では改善幅が縮む点に注意。改善幅の絶対値はベースモデル・データ規模・タスクに強く依存するため、系統横断の単純比較は避けるべき。