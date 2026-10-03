# まとめ：ViT 以後（2020年〜）の「どこを・どの粒度で見るか」（2本の調査結果より）

作成: 2026-09-21

対象となった調査結果（同フォルダ）

- `compass_artifact_wf-9d46348d-57cf-569b-a8c6-17badaa3538c_text_markdown.md`（以下 **報告A**）
- `ViT細粒度注目制御の調査.md`（以下 **報告B**）

前提は、意匠図面（白背景の線画・正面図1枚）から製品名を当てるタスク。Qwen3-VL-4B のゼロショット8択で正解率42%、誤答の約8割が「図面を正しい製品名に結びつけられていない」問。図面は A（決め手が面の内側の小領域）と B（決め手が全体の輪郭）に分かれる。

---

## 1. 両報告が一致している点

### 1-1. トークンを増やしても細部は救いきれない

- **視覚エンコーダ側の盲点**：MMVP（Tong et al., CVPR 2024, arXiv:2401.06209）は、CLIP 埋め込みではほぼ同一だが DINOv2 では明確に違う画像対（CLIP-blind ペア）の存在を示し、**識別された9つの視覚パターンのうち7つはモデル規模・解像度を上げても未解決**と報告。人間 95.7% に対し GPT-4V 38.7%。
- **圧縮で空間情報が拡散する**：Q-Former の固定長クエリ、隣接パッチのマージ（Qwen 系の2×2結合）、注意による剪定（FastV, ECCV 2024）はいずれも細粒度の空間情報を系統的に失う。
- LLaVA-NeXT の公式報告では「**解像度のスケーリングのほうがトークン数のスケーリングより効果的**」。
- 「Position: Reasoning After Perception」（arXiv:2507.16863）は Qwen2.5-VL で**視覚エンコーダを更新する設定だけが実質的な改善をもたらし、言語側やアダプタのみの更新はほぼ無効**と報告（報告A）。

→ **単にトークン数・解像度を増やす方向は、やるべきでないと両報告が明言。**

### 1-2. 「どこを見るか」の制御は3系統

| 系統 | 代表 | 制御信号 |
|---|---|---|
| モデル内部信号で切り出す | ViCrop、FOCUS（NeurIPS 2025, arXiv:2506.21710）、HAVC | 注意・勾配・トークン類似度 |
| 探索して拡大する | V*/SEAL（CVPR 2024）、ZoomEye（EMNLP 2025 Oral）、DeepEyes（arXiv:2505.14362）、Chain-of-Focus | LLM の誘導、自己申告確信度、学習した方策 |
| 領域を明示指定する | 赤丸などの視覚プロンプト（ICCV 2023, arXiv:2304.06712）、領域トークン | 外部指定 |

ZoomEye は InternVL2.5-8B で HR-Bench +15.71/+17.69 ポイント、LLaVA-v1.5-7B で V*Bench +34.57 ポイント。赤丸プロンプトは CUB のキーポイント命名で 46.5%（切り出し 25.5%、ランダム 8.2%）。

### 1-3. 線画・特許図面は手薄

- DeepPatent（WACV 2022, mAP 0.376）→ Wang & Zhang 2023（0.712）→ Higuchi & Yanai（World Patent Information 74, 2023, SwinV2, mAP 0.856）。
- DeepPatent2（Nature Scientific Data 10, 772, 2023）：技術図面270万枚超、物体名13.2万、視点2.2万。
- **Density-Refine**（Lin, Hung, Lee, ASME J. Mech. Des. 147(8):081703, 2025, DOI:10.1115/1.4067749）：密度クラスタリングで教師なしに局所領域を抽出して特徴融合。**線画側で「どこを見るか」を決める唯一の先行例。**
- Awale et al.（ECIR 2025, arXiv:2501.12751）：InstructBLIP で特許図面の物体名を分類。**自然画像で事前学習した VLM は特許線画でゼロショット性能が低い**と報告。PatentLMM（arXiv:2501.15074）も GPT-4V のゼロショットが弱いと報告。

### 1-4. 識別性の学習は視覚側と言語側に分かれる

- 視覚側：NegCLIP/ARO（ICLR 2023）、DIVA（ICLR 2025, arXiv:2407.20171、拡散の生成フィードバック）、un²CLIP（arXiv:2505.24517）。
- **注意**：SugarCrepe（NeurIPS 2023, arXiv:2306.14610）は、NegCLIP 系の改善が**ベンチのアーティファクトへの過学習**で誇張されていると警告。改善幅はどれも10%を超えない。ハードネガで学習するときの一般的な落とし穴。

---

## 2. 両報告が食い違っている点（重要）

### Q1. 質問文なしで、全体と局所を対象ごとに切り替える研究はあるか

| | 回答 | 根拠 |
|---|---|---|
| 報告A | **ほぼ無い（空白）** | V*/SEAL, ZoomEye, FOCUS, DeepEyes, LookWise, CARES 等はすべて「質問に答えるための確信度」が信号で、質問文が前提 |
| 報告B | **明確に存在する** | **Glance-and-Focus（GFNet, NeurIPS 2020）、AdaFocus（ICCV 2021）**など、画像分類の動的推論（dynamic inference）の系統。質問文なしで、1位の確率・エントロピー・1位と2位の差で早期終了するか局所を拡大するかを決める |

**この食い違いは、報告B が正しく、報告A の探索範囲が MLLM 期に偏っていたと読むのが妥当。** 報告Bが挙げる GFNet / AdaFocus は、まさに「画像だけから、全体で十分か局所を見るかを確信度で決める」枠組み。

**したがって、こちらの提案の新規性は「確信度ゲートで拡大する」ことそのものには無い。** 主張は次に置く必要がある。

- 疎な**線画**でそれが成立するか（未検証）。
- **どこを拡大するか**を、質問文なしで決める方法（GFNet は分類用の方策ネットワークを学習する。線画向けは未確立）。
- **A/B という手がかりの在り処の分類**そのもの。
- 似た意匠との**識別**（8択）への接続。

### Q2. 疎な線画で注意マップ・勾配マップは信頼できるか

| | 回答 |
|---|---|
| 報告A | **検証はなく、むしろ否定されている。** Bandyopadhyay et al.「What Sketch Explainability Really Means for Downstream Tasks」（CVPR 2024, arXiv:2403.09480）は、**ピクセル単位の帰属は白い空白が大半を占める疎なスケッチでは意味のある説明を与えない**と明言し、ストロークレベルの帰属に切り替えている |
| 報告B | ViT の自己注意は線画でも識別的な幾何パーツに集中することが確認されている一方、白背景が原因で広域のノイズが出て、**注意が外郭に不釣り合いに集中し、面の内側の小さなスリットや穴への強度が著しく下がる**（"SketchSense (2026)" を引用。**出典が確認できない**） |

**結論としては両者とも同じ方向**：**線画では注意・勾配をそのまま切り替え器に使うのは危険**。報告Aの CVPR 2024 の一次情報は確実なので、これを根拠にする。

### Q3. 遮蔽で依存部分を調べた研究はあるか

| | 回答 |
|---|---|
| 報告A | 自然画像では成熟（Captum の Occlusion など）。**線画・スケッチに VLM の遮蔽帰属を適用した研究は発見できず**＝空白。自前でやる価値がある |
| 報告B | 「存在する」とし、さらに**「Qwen3-VL を対象とした視覚遮蔽研究で、シルエットを遮蔽すると大きく落ちるが面内部を遮蔽してもロジットがほとんど変化しない」**と記述。**出典が示されておらず、こちらの仮説と都合よく一致しすぎている。鵜呑みにしない** |

---

## 3. 出典が確認できない・要注意の記述（報告B 由来が多い）

| 記述 | 状態 |
|---|---|
| Blink（CVPR 2026、テキスト命令に依存せず内部 saliency で局所トークンを再展開） | 会議名・内容とも未確認 |
| SketchSense（2026、線画の注意ノイズ） | 未確認 |
| Vision-RL2 / Q-Guide | 未確認 |
| 「Qwen3-VL を対象とした Visual Ablation 研究」 | 出典なし。**結論が本件の仮説と一致するため特に注意** |
| FIRM（トークン内のサブセル構造を補うコネクタ改変） | 未確認 |
| CropVLM | 報告A は arXiv:2511.19820、前回のまとめでは CVPRW 2026。**番号が不一致** |
| ViCrop の arXiv 番号 | 報告A は arXiv:2310.16033、前回のまとめ（ViT以前フォルダ）は arXiv:2502.17422（ICLR 2025 "MLLMs Know Where to Look"）。**別物の可能性。要確認** |
| LookWise / HAVC / R2I / Density-Refine の数値 | 査読前または本文未確認 |

---

## 4. こちらの計画への影響（結論）

1. **遮蔽による診断を最初にやる**、は両報告とも第1段階に置いている。報告A は「線画×VLM の遮蔽帰属は空白なので、この診断自体が論文になりうる」とまで書いている。**方針は変えない。**
2. **注意マップを切り替え器に使う案は、優先度を下げる。** 疎な線画ではピクセル帰属が意味を持たないことが CVPR 2024 で明言されている。使うとしても、遮蔽で作った正解と照合して**信頼できるか先に確かめる**手順にする。
3. **どこを拡大するかは、画像処理側で決める案が現実的。** 具体的には
   - インク画素の密度クラスタリング（Density-Refine 型、報告A）
   - **DINOv2 の密な特徴を正規化カットで分割し、外郭のパッチ群と面内部のパッチ群を教師なしで分離**（報告B の転用候補2）。CLIP 系より DINOv2 のほうが細部を保つという MMVP の知見とも整合。
4. **確信度ゲートは GFNet（NeurIPS 2020）を引用する。** 「1位と2位の差が小さいときだけ拡大する」は既存の枠組みなので、そこを新規性にしない。
5. **前処理として、図枠・参照番号・寸法線の除去が必須**（両報告が指摘）。密度でもクラスタリングでも、文字が高密度領域として誤検出される。「図ラベル除去はしない」という既存方針の見直しが要る。
6. **解像度・トークン数を単に増やす案は採らない**（MMVP と Position 論文）。
7. **ハードネガでの学習をやるときは、アーティファクト過学習に注意**（SugarCrepe）。未見のカテゴリでの汎化を必ず確認する。

---

## 5. 一次情報に当たる優先順

1. **Glance and Focus（GFNet, NeurIPS 2020）／AdaFocus（ICCV 2021）** — 質問文なしの確信度ゲートの原典。こちらの提案の位置づけが決まる。
2. **What Sketch Explainability Really Means for Downstream Tasks**（CVPR 2024, arXiv:2403.09480）— 線画で帰属が使えない根拠。
3. **MMVP / Eyes Wide Shut?**（CVPR 2024, arXiv:2401.06209）— 解像度を上げても解けない根拠。
4. **Density-Refine**（ASME JMD 147(8):081703, 2025, DOI:10.1115/1.4067749）— 線画からの教師なし領域抽出。
5. **ZoomEye**（EMNLP 2025, arXiv:2411.16044）— 確信度駆動のズームの実装。
6. **Awale et al.**（ECIR 2025, arXiv:2501.12751）— 特許図面での VLM ゼロショットの弱さの定量。
7. **SugarCrepe**（NeurIPS 2023, arXiv:2306.14610）— ハードネガ学習の落とし穴。

---

## 6. 参考文献（両報告に出てきた主要なもの）

| 論文 | 発表 | 出典 |
|---|---|---|
| Eyes Wide Shut? Exploring the Visual Shortcomings of Multimodal LLMs（MMVP） | Tong et al., CVPR 2024 | arXiv:2401.06209 |
| V*: Guided Visual Search as a Core Mechanism in Multimodal LLMs | Wu & Xie, CVPR 2024 | arXiv:2312.14135 ／ github.com/penghao-wu/vstar |
| ZoomEye: Enhancing MLLMs with Human-Like Zooming Capabilities through Tree-Based Image Exploration | Shen et al., EMNLP 2025 Oral | arXiv:2411.16044 ／ github.com/om-ai-lab/ZoomEye |
| FOCUS: Internal MLLM Representations for Efficient Fine-Grained VQA | NeurIPS 2025 | arXiv:2506.21710 |
| What does CLIP know about a red circle? | Shtedritski et al., ICCV 2023 | arXiv:2304.06712 |
| When and why VLMs behave like bags-of-words?（NegCLIP/ARO） | Yuksekgonul et al., ICLR 2023 | arXiv:2210.01936 |
| SugarCrepe: Fixing Hackable Benchmarks for Vision-Language Compositionality | Hsieh et al., NeurIPS 2023 | arXiv:2306.14610 |
| Diffusion Feedback Helps CLIP See Better（DIVA） | ICLR 2025 | arXiv:2407.20171 |
| un²CLIP | — | arXiv:2505.24517 |
| What Sketch Explainability Really Means for Downstream Tasks | Bandyopadhyay et al., CVPR 2024 | arXiv:2403.09480 |
| Glance and Focus（GFNet） | NeurIPS 2020 | 報告B が引用（要一次確認） |
| AdaFocus / AdaFocusV2 | ICCV 2021 ほか | 報告B が引用（要一次確認） |
| DeepPatent: Large Scale Patent Drawing Recognition and Retrieval | Kucer et al., WACV 2022 | mAP 0.376 |
| DeepPatent2 | Ajayi et al., Nature Scientific Data 10, 772 (2023) | 技術図面270万枚超 |
| Patent image retrieval using transformer-based deep metric learning | Higuchi & Yanai, World Patent Information 74 (2023) 102217 | SwinV2, mAP 0.856 |
| Density-Refine: Patent Image Retrieval by Density-Based Region Extraction and Feature Fusion | Lin, Hung, Lee, ASME J. Mech. Des. 147(8):081703 (2025) | DOI:10.1115/1.4067749 |
| Patent Figure Classification Using Large Vision-Language Models | Awale et al., ECIR 2025 | arXiv:2501.12751 |
| PatentLMM: Large Multimodal Model for Generating Descriptions for Patent Figures | 2025 | arXiv:2501.15074 |
| FastV: An Image is Worth 1/2 Tokens After Layer 2 | ECCV 2024 | — |
| Qwen2-VL | 2024 | arXiv:2409.12191 |
| DeepEyes: Incentivizing Thinking with Images via RL | 2025 | arXiv:2505.14362 |
| ViCrop（Perceiving Small Visual Details in Zero-shot VQA） | — | arXiv:2310.16033（前回まとめの arXiv:2502.17422 と要突合） |
| Position: Reasoning After Perception | — | arXiv:2507.16863 |
| CARES: Context-Aware Resolution Selector | — | arXiv:2510.19496 |

---

## 7. 追記（2026-09-22）：Glance-and-Focus 系列との関係と、提案の骨子

### 7-1. 同一著者による系列として扱う

粒度切り替えの直系は、GFNet → AdaFocus → AdaFocusV2 → 長尺動画版（2026, arXiv:2605.12954）という**一連のシリーズ**。位置づけはこの系列に対して行う。

**名前の衝突に注意**：「AdaFocus」は2つある。

| | 設定 | 注視位置の決め方 | 停止・起動の判断 |
|---|---|---|---|
| GFNet（NeurIPS 2020）／AdaFocus（ICCV 2021）／AdaFocusV2（CVPR 2022） | **質問文なし**の分類（画像・動画） | **対象データセットのラベルで学習した方針ネットワーク**。V1 は強化学習（正解で報酬）、V2 は微分可能化（STN で切り出し、分類誤差の勾配を方針に逆伝播） | 確信度による早期終了 |
| AdaFocus（2026, 長尺動画 LLM, arXiv:2605.12954） | **質問文あり**の動画QA | **質問文とのクロスアテンションを逆引き**してヒートマップを作り、質問語の意味ベクトルとの一致で絞り込み、RoI を高解像度で読み直す（Zero-Cache Look-back） | 出力分布のエントロピー等、**不確実性トリガー** |

### 7-2. この系列が既に閉じている穴

- **不確実性で拡大を起動する**：GFNet の早期終了、長尺動画版の look-back、ZoomEye・LookWise と同じ。**新規性にならない。**
- **質問文なしで注視位置を決める**：AdaFocus V1/V2 が方針ネットワークで実現済み。**「質問文なしの where」も空白ではない。**

### 7-3. それでも残る差（提案の芯）

1. **目的が違う：効率 vs 能力。** この系列は一貫して計算量削減（同じ精度をより少ない計算で）。本件は「手がかりが局所にある対象で解けるようにする」という能力の問題。
2. **学習前提が違う。** 方針ネットワークは**対象データセットのラベルで学習**する。本件は凍結した汎用 VLM に開いた語彙で名前を出させる設定で、対象分布での学習をしない。**ラベルなしで粒度を決める**必要がある。
3. **「拡大しても解けない対象」がある。** 分類タスクではラベルは必ず画像から決まるが、本件では決め手が写っていない対象が混ざる。**不確実性は「見えていない」と「本質的に曖昧」を区別できない**（B タイプの誤答＝輪郭が似た別カテゴリは、拡大しても直らない）。
4. **未知カテゴリ。** 2026年版は質問文があるので未知物体も指せるが、質問文のない記述生成では使えない。V1/V2 は学習分布に縛られ、**未知カテゴリでの検証が無い**。

### 7-4. 提案の骨子

> 注視位置の制御は、これまで **質問文**（テキストとの対応付け）か **対象分布での学習**（タスク損失で最適化した方針）のどちらかに依存してきた。記述生成では質問文が無く、対象は事前学習に無い製品も含む。本研究は、**手がかりの空間的な集中度（cue locality）**という画像側の性質を、質問文もラベルも使わずに測り、それに基づいて見る粒度を決める。**ゼロショットの手法**と、**未知カテゴリへ一般化する事後学習**の両方を示す。

**貢献を3つに分ける**

1. **診断**：遮蔽で手がかりの局所性を測る指標を定義し、(a) 対象ごとに大きく違う、(b) 現行モデルの失敗がそこに集中する、(c) **モデルが実際に見ている位置と本当の決め手のずれが、珍しい対象ほど大きくなる**、を示す。(c) が図1になる。
2. **ゼロショット手法**：質問文なしで局所性を推定し、粒度を切り替える。
3. **事後学習**：局所性の予測器（切り替え方策）を学習し、**学習に使わなかったカテゴリで評価**して未知カテゴリへの一般化を示す（9/3 FB の「未学習クラスへの汎化」と接続）。

**必須のベースライン**

| 引き金 | 由来 | 目的 |
|---|---|---|
| 常に全体 | 現状 | 下限 |
| 常に拡大 | ViCrop 型 | 拡大そのものの効果 |
| 確信度（1位と2位の差） | GFNet / ZoomEye / 長尺動画版 | **不確実性ゲートを上回れるかが勝負** |
| 汎用プロンプト＋注意クロップ | 「What product is this?」を疑似質問にした ViCrop / FOCUS | **「既存手法で足りる」への反論として必須** |
| 局所性（提案） | — | — |
| オラクル | 問ごとに良い方 | 上限 |

**データセット**：主＝一般物体のロングテール（未知カテゴリ評価ができるもの）、副＝細粒度（CUB, Stanford Cars 等）、**極端例として意匠図面**。意匠は3つ目に置き、線画特化に見せない。

**残るリスク**

- 遮蔽は画像あたり数十回の推論が要る。論文では「遮蔽は正解ラベルを作る道具、推論時は軽量な予測器」と役割を分ける。
- 「拡大しても解けない対象」の比率を正直に出す。確信度ゲートとの差別化の核なので、ここを測らないと主張が立たない。
- **V1/V2 が「人や動体を見る汎用的な勘を学んでいるだけ」というのは現時点では推測。** 一次情報で確認するまで断定しない。実測（注視位置のずれを馴染み度で層別）に置き換える。

### 7-5. 追加の参考文献

| 論文 | 発表 | 出典 |
|---|---|---|
| Glance and Focus（GFNet） | NeurIPS 2020 | 質問文なし・確信度で早期終了 |
| AdaFocus | ICCV 2021 | 強化学習で注視位置の方針を学習 |
| AdaFocusV2 | CVPR 2022 | 微分可能化（STN）で座標を直接最適化 |
| AdaFocus（長尺動画 LLM 版） | 2026 | arXiv:2605.12954 ／ 質問文とのクロスアテンション逆引き＋不確実性トリガーの look-back |
