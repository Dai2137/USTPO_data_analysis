# まとめ：VLM 期（2023年〜）のレビュー論文における「画像の記述生成」（2本の調査結果より）

作成: 2026-09-22

対象となった調査結果（同フォルダ）

- `claude.md`（以下 **報告A**。書誌情報・章の対応が詳しい）
- `gemini.md`（以下 **報告B**。論調は強いが出典が弱い）

問いは3つだった。(1) キャプション生成が独立タスクから指示追従の一機能へ移ったことを扱う総説はあるか、(2) 「image captioning」という語は生きているか、(3) こちらの問題設定はどこに位置づくか。

---

## 0. 結論：VLM 期のキャプション生成には、定番の総説がまだ存在しない

サーベイ4本を全文で読んで確認した結論。

- **定番と呼べるキャプション生成の総説は、Stefanini（TPAMI 2022）と Hossain（ACM CSUR 2019）で止まっている。** どちらも対象は2023年頃まで。
- **VLM 期（2023年〜）を対象にした「定番の総説」は無い。** 今回読んだ4本の位置づけは、Berger（TACL 2025）＝評価指標の使われ方の実証調査、Sarto（IJCAI 2025 Survey Track）＝9ページの評価サーベイ、Abdulgalil（Elsevier NLP Journal 2025）＝掲載先がマイナーで中身も2022年までのモデル比較が中心、Xiao（TPAMI 2025）＝grounding の総説。**キャプション生成そのものの決定版は無い。**
- 理由は3つ。(1) 査読誌は投稿から出版まで1〜2年かかり、対象期間が出版年より古い（Berger は対象が2010〜2024年で、2024年は「データ収集が年内終了前」として分析から除外）、(2) キャプション生成の研究自体が MLLM の整合・幻覚・データ構築の研究に吸収され、**「キャプション生成」という名前で総説が書かれなくなった**、(3) その新しい話題を扱う総説は MLLM 側にあり、ほとんどが arXiv のみ。
- **隣の領域は最新まで追えている。** Xiao の grounding サーベイ（TPAMI 2025年11月）は MLLM を44回扱い、Ferret・Shikra・GREC・DINO-X まで入る。つまり遅れているのは**キャプションという枠**であって、査読の遅さだけが原因ではない。

**論文での扱い**：「分野が2023年で止まっている」とは書けない。正確には「**キャプション生成の枠で書かれた総説は2023年頃までを対象としており、現在の実務は MLLM 側の文献と手法論文にある**」。生成・学習の話は手法論文を引き、評価の話は Sarto と Berger を引く。**総説とMLLM側文献の間に落ちている論点（識別性・当て直し・粒度の切り替え）を拾う**、という位置づけが取れる。

**注意**：以下の第3節「いまの標準的なやり方」は、**総説が描く標準（〜2023年）と現在の実務が混ざっている**。総説側は「交差エントロピー ＋ SCST ＋ 視覚言語事前学習 ／ MS-COCO の Karpathy 分割 ／ 5指標」で、これは **COCO のリーダーボードを競っていた時代の標準**。現在の実務（凍結 VLM ＋ プロンプト、指示データでの微調整と選好最適化、recaptioning、参照なし・幻覚・LLM 判定の評価）は**総説には書かれていない**ので、手法論文を根拠にする。

---

## 1. 移行を扱う査読付き総説は、実質2本

| 総説 | 掲載 | 位置づけ |
|---|---|---|
| **Sarto, Cornia, Cucchiara 2025**「Image Captioning Evaluation in the Age of Multimodal LLMs」 | IJCAI 2025 Survey Track（査読、DOI:10.24963/ijcai.2025/1180、arXiv:2503.14604） | 「MLLM の登場で captioning は **core task** になった」と明記。評価軸として整理 |
| **Berger, Stanovsky, Abend, Frermann 2025**「Surveying the Landscape of Image Captioning Evaluation」 | TACL 13:1597–1644（査読、DOI:10.1162/TACL.a.52、arXiv:2408.04909） | 2010–2024年・15会場・314論文から71指標を分類。**retrieval ベース評価と candidate diversity を独立の分類軸に置く** |
| Abdulgalil & Basir 2025「Next-generation image captioning」 | Natural Language Processing Journal 12:100159（査読） | Transformer → MLLM の移行を1節で扱う。限界として幻覚・grounding・**長尾物体認識** |
| Xiao et al. 2025「Towards Visual Grounding: A Survey」 | IEEE TPAMI 2025（査読） | region captioning / 参照表現生成を grounding の下位に置く |

**arXiv のみ**：MLLM の幻覚サーベイ（arXiv:2404.18930）、MME-Survey（arXiv:2411.15296）、ベンチマークのサーベイ（arXiv:2408.08632）、Caffagni et al. の MLLM 総説（arXiv:2402.12451）。

→ **「移行を正面から扱った査読付き総説は、まだ2本程度しかない」**が現状。ここは論文で「この分野は総説が追いついていない」と書ける。

---

## 2. 「image captioning」は古い語ではない

- **総称・章題としては現役**（Sarto, Abdulgalil とも継続使用）。歴史的経緯としてのみ出てくる語ではない。
- ただし**語が分化した**。

| 語 | 指すもの |
|---|---|
| detailed / dense / long caption | 長く密な記述（DOCCI, DCI, ImageInWords, PixelProse が牽引） |
| region captioning / grounded captioning | 領域・座標付きの記述 |
| fine-grained perception | 能力軸としての細粒度知覚 |
| recaptioning | 既存データの記述を強いモデルで書き直すこと |

- **distinctive / discriminative captioning は古典系の語で、VLM 期の総説にはほぼ継承されていない**（報告A）。
- 揺れているのは long / detailed / hyper-detailed の使い分け。

---

## 3. いまの標準的なやり方

- **生成**：凍結モデルへのプロンプト ＋ 指示チューニング（SFT）が標準。近年は**選好最適化（DPO / RLAIF）**が急増。
- **学習データ**：**recaptioning が主流**。ShareGPT4V（arXiv:2311.12793, ECCV 2024）は GPT-4V による10万件の高品質キャプションから120万件へ拡張。**危険は誤りの増幅**で、Hunyuan-Recap100M は DPO で非幻覚率 48.3% → 77.9% と報告（自己申告）。
- **評価**：参照文一致（CIDEr 等）は長い記述に不適合と両総説が指摘。**参照なし（CLIPScore, PAC-S, BRIDGE）／幻覚（CHAIR, POPE, ALOHa）／LLM-as-judge（CLAIR, FLEUR）**へ重心が移動。Berger は「**大多数の論文が5つの単純な指標しか使っておらず、人手評価との相関が弱い**」と警告。
- **ベンチマーク（長い・密な記述）**：DOCCI（段落記述）、DCI（マスク整合の長記述）、ImageInWords（超詳細）、PixelProse（大規模）、DetailCaps-4870（事実性）、DOCCI-Critique（文単位の事実性、NeurIPS 2025, arXiv:2506.07631）。

→ **これらは記述の忠実さ・密度を測るが、識別性は測らない。** こちらの評価との差分はここ。

---

## 4. こちらの4つの論点の扱い（両報告の判定）

| 論点 | 判定 | 根拠 |
|---|---|---|
| **紛らわしい候補と区別できる記述**（識別性・語用論・聞き手） | **扱われていない** | 唯一の接点は Berger の candidate diversity（CIDErBtw, Self-CIDEr）と retrieval ベース評価。Sarto・Abdulgalil には distinctiveness / discriminative / pragmatic の語が無い |
| **当て直し評価（self-retrieval / listener accuracy）** | **標準ではない** | Berger が recall@n の text-to-image retrieval を**多数あるプロトコルの一つ**として収録。標準指標としては扱っていない |
| **見る粒度を対象ごとに変える** | **総説では独立項目化されていない** | 手法レベル（V*, Chain-of-Spot, CropVLM, Mini-Monkey, Mixture-of-Resolution 等）は活発だが、章立てにはなっていない。扱いも**高解像度処理の効率化・小物体 VQA の精度**という文脈 |
| **事前学習に無い対象・長尾** | **記述の長尾としては扱われていない** | Abdulgalil が「長尾物体**認識**」を限界として挙げるのみ。幻覚サーベイでは「珍しい概念で視覚証拠ではなく言語知識で補完する」問題構造として認識されている |

---

## 5. 共通の未解決問題と、こちらの主張の判定

**共通して挙がる未解決問題**

1. 視覚的幻覚・事実性
2. **情報ボトルネックと固定解像度の限界**（視覚エンコーダ段階で細部が落ちる）
3. 長い・詳細な記述に対する評価指標の不備
4. grounding・領域整合
5. 参照指標への過度依存
6. 計算コスト・効率

**こちらの主張**

> 記述の決め手になる手がかりの在り処（全体の輪郭か、ごく一部か）は対象ごとに異なるのに、モデルは常に同じ粒度で見ている。この性質を測り、対象ごとに見方を切り替える。質問文もラベルも使わない。

- **独立した課題として挙げている総説は無い**（両報告が一致）。
- 最も近い既存の名前は3つに分散している。
  1. **情報ボトルネック／固定解像度の限界、fine-grained perception**（共通の未解決問題2）
  2. **Dynamic visual resolution / adaptive cropping**（手法レベル。目的は効率化と小物体の精度）
  3. **Distinctive / discriminative captioning**（古典系。Berger が diversity・retrieval 軸として収録）

→ **こちらの貢献は、この3つを横断する点**にある。特に「**質問文もラベルも無しで、モデル自身が手がかりの在り処を測って粒度を決める**」は、どの総説にも項目が無い。

---

## 6. 論文への含意

1. **査読付きの軸は Sarto（IJCAI 2025）と Berger（TACL 2025）。** 「captioning は MLLM の core task ／評価軸になった」という移行を査読付きで裏づけられるのはこの2本。Abdulgalil（NLP Journal 2025）と Xiao（TPAMI 2025）を補助に。
2. **識別性・聞き手評価の系譜は、総説ではなく手法論文で補強する。** Dai & Lin（NeurIPS 2017）、Luo et al.（CVPR 2018）、Liu et al.（ECCV 2018）、CIDErBtw / Self-CIDEr、Dessì et al.（CVPR 2023）。**Berger を「これらを収録した唯一の VLM 期総説」として橋渡しに使う。**
3. **評価の並べ方**：参照文一致も併記したうえで、長い記述では機能しないという分野共通の認識（Sarto, Berger）を引き、聞き手テストを足す形にする。
4. **ベンチとの差分**：DOCCI・DCI・ImageInWords・DetailCaps は**忠実さと密度**を測る。こちらは**識別性**を測る、という対比が効く。
5. **導入で使える論点（仮説として）**：現在の VLM は「親切で詳しい記述」に向けて調整されているため、冗長で網羅的な記述に寄り、**識別に効く一点を言わない**傾向がある。報告Bの主張だが出典が弱いので、**こちらのデータ（当たり障りのない上位語に逃げる誤答）で裏づけてから書く。**

---

## 7. 情報の確度

- **報告Bは断定が強すぎる。** 「完全に抜け落ちている」「全く扱われていない」と書いているが、Berger は retrieval ベース評価を一プロトコルとして収録している。**「標準ではない」が正確な言い方。**
- recaptioning の効果数値（48.3% → 77.9%、10万→120万件）は**当該手法論文の自己申告**で、独立検証ではない。
- 手法側の arXiv 番号は報告間で食い違いがある（CropVLM が arXiv:2511.19820／CVPRW 2026）。引用時に要確認。
- zoom-in 系（V*, Chain-of-Spot, CropVLM, Mini-Monkey 等）は2024〜2026年に活発だが**サーベイ未整理**。**今後サーベイ化されると、こちらの位置づけが変わる**ので、投稿前に再確認する。
- 同様に、識別性や self-retrieval を独立章にした査読付き総説が出た場合、gap の主張を「空白の充填」から「既存課題への貢献」に調整する。

---

## 8. 参考文献

**査読付き総説**

| 文献 | 掲載 |
|---|---|
| Sarto, Cornia, Cucchiara. Image Captioning Evaluation in the Age of Multimodal LLMs: Challenges and Future Perspectives | IJCAI 2025 Survey Track, pp.10632–10640. DOI:10.24963/ijcai.2025/1180 ／ arXiv:2503.14604 |
| Berger, Stanovsky, Abend, Frermann. Surveying the Landscape of Image Captioning Evaluation: A Comprehensive Taxonomy, Trends and Metrics Analysis | TACL 13:1597–1644, 2025. DOI:10.1162/TACL.a.52 ／ arXiv:2408.04909 |
| Abdulgalil & Basir. Next-generation image captioning: from transformers to Multimodal Large Language Models | Natural Language Processing Journal 12:100159, 2025. DOI:10.1016/j.nlp.2025.100159 |
| Xiao, Yang, Lan, Wang, Xu. Towards Visual Grounding: A Survey | IEEE TPAMI, 2025 |

**arXiv のみの総説**

| 文献 | 出典 |
|---|---|
| Bai et al. Hallucination of Multimodal Large Language Models: A Survey | arXiv:2404.18930 |
| Fu et al. MME-Survey: A Comprehensive Survey on Evaluation of Multimodal LLMs | arXiv:2411.15296 |
| Li et al. A Survey on Benchmarks of Multimodal Large Language Models | arXiv:2408.08632 |
| Caffagni et al. The Revolution of Multimodal Large Language Models: A Survey | arXiv:2402.12451（ACL 2024 Findings 版あり） |

**手法・データ・ベンチマーク**

| 文献 | 出典 |
|---|---|
| ShareGPT4V: Improving Large Multi-Modal Models with Better Captions | arXiv:2311.12793（ECCV 2024） |
| Low-hallucination Synthetic Captions for Large-Scale VLM Pre-training（Hunyuan-Recap100M） | arXiv:2504.13123 |
| DOCCI-Critique（詳細記述の文単位の事実性） | arXiv:2506.07631（NeurIPS 2025） |
| Contrastive Learning for Image Captioning | Dai & Lin, NeurIPS 2017 |
| Discriminability Objective for Training Descriptive Captions | Luo et al., CVPR 2018 |
| Show, Tell and Discriminate: Self-retrieval with Partially Labeled Data | Liu et al., ECCV 2018 |
| Compare and Reweight（CIDErBtw）／Self-CIDEr | ECCV 2020 ／ Wang & Chan 2019 |
| Cross-domain image captioning with discriminative finetuning | Dessì et al., CVPR 2023 |
| zoom-in 系（V*, Chain-of-Spot, CropVLM, Mini-Monkey, Mixture-of-Resolution Adaptation） | 各手法論文（サーベイ未整理） |

---

## 9. 一次情報での確認（サーベイ4本を全文で読んだ結果、2026-09-22）

同フォルダの PDF 4本を全文検索・精読して確かめた。**調査結果には3か所、はっきりした誤りがあった。**

### 9-1. Sarto et al., IJCAI 2025 Survey Track（9ページ）

- 冒頭の主張は確認できた：「**With the advent of Multimodal Large Language Models (MLLMs), image captioning has become a core task**, increasing the need for robust and reliable evaluation metrics」。
- **これは評価指標のサーベイであり、生成手法の総説ではない。** 指標の分類（参照文あり／なし × rule-based／learnable／LLM-based／幻覚特化）と、人手相関・ペアランキング・幻覚感度の実験が中身。
- 語の出現：**distinctive / discriminative / self-retrieval / pragmatic / listener / retrieval はすべて0回**。hallucination は23回。
- §4 の未解決問題は4つ：**(1) ベンチの進化**（既存データは COCO 風の短いキャプション中心で、MLLM の長く詳細な出力との間にギャップ。同義語・言い換え・**ドメイン固有語**への対応が要る）、(2) 指標の説明可能性、(3) 幻覚の検出、(4) **指標の個人化**（詳しさ・簡潔さ・スタイル・ドメイン関連性をユーザが優先できるように）。
- → **こちらの接続先は (1) と (4)。** 「何を重視した記述を良しとするか」が定まっていない、という認識がある。

### 9-2. Berger et al., TACL 2025（44ページ）— **報告Aの位置づけは誤り**

- **「multimodal large language」0回、「MLLM」0回。** 中身は 2010〜2024年・15会場・314論文から71指標を集めた**評価指標の使われ方のサーベイ**で、**VLM 期への移行を扱った総説ではない**。
- 報告Aは「移行を査読付きで裏づける2本のうちの1本」としていたが、**これは過大評価**。移行を明示しているのは Sarto と Abdulgalil の2本。
- distinctive / discriminative / pragmatic / listener は**参考文献リストにのみ**出現（Wang & Chan の CIDErBtw、Dessì et al.、Cohn-Gordon et al.、Ou et al. の CLIP listener）。**本文の分類項目にはなっていない。**
- ただし当て直し評価は分類体系に載っている。§4.1.2「**Retrieval-based methods: A popular evaluation protocol involves using text-to-image retrieval on the test set** ... recall@n is applied as the evaluation metric」。人手評価の類型にも「Retrieval（参加者に候補文から画像を探させる）」があり、Wang & Chan 2019 と Ou et al. 2023 を引いている。
- **引用に使える強い事実**：「since 2015, five metrics – BLEU, CIDEr, METEOR, ROUGE, and SPICE – have been used substantially more frequently than all other metrics」、1論文あたりの指標数は4〜5で頭打ち、**人手評価の実施率は2015年以降低下**、結論でも「most papers rely on five metrics that have only a weak correlation with human ratings」。

### 9-3. Abdulgalil & Basir, NLP Journal 2025（20ページ）— **「標準のやり方」の記述は裏が取れない**

- 語の出現：**distinctive / discriminative / self-retrieval / listener / pragmatic / zoom / crop / DPO / RLHF / recaption はすべて0回**。instruction も2回のみ。
- → **報告Aが「現在の標準」として書いていた「プロンプト＋SFT＋DPO/RLAIF」「recaptioning が主流」は、査読付き総説4本のどれにも書かれていない。** 手法論文由来の記述なので、論文で述べるなら手法論文を直接引く必要がある。
- 構成は、指標 → 特徴表現（領域・グリッド・ハイブリッド）→ 手法の分類（注意・事前学習・融合）→ **限界（§5、MLLM の限界は §5.4）** → 議論 → **未来の方向（§7）**。
- §7 の柱は、視覚特徴表現の強化、マルチモーダルの整合、学習の複雑さと効率、**§7.4 希少物体と記述の一貫性**、MLLM 時代の評価。
- §7.4 の中身：「**Effectively handling long-tail objects**, accurately identifying object relationships, and ensuring consistency ... These limitations often lead to **hallucinations or misclassifications**, especially in cases involving rare objects」。
- granularity は2回で、いずれも「global 特徴は粒度と細部を失う」という文脈。
- → **長尾の接続先はここが唯一。** ただし「認識の長尾」であって「記述の長尾」ではない。

### 9-4. Xiao et al., TPAMI 2025「Toward Visual Grounding: A Survey」（30ページ）

- REC 260回、MLLM 44回。**参照表現生成（REG）は §2.4 に「最も密接に関連する領域」として置かれ**、当初は grounding が REG の補助タスクだったが、近年は**逆に REG が疑似ラベル生成に使われる**関係にある、と整理されている。
- 話者・聞き手モデルへの言及あり：Yu et al. 2017 の speaker-listener-reinforcer が「報酬損失を使って**より識別的な表現**をサンプリングする」と紹介される。listener は3回。
- 課題：RefCOCO 等の**データセットの飽和**、事前学習モデルが生成した疑似ラベルのノイズ（**model poisoning**）、**「1画像に参照対象は1つ」という強い仮定が現実と合わない**、動画、スケーリング。
- → 「聞き手が特定できる識別的な表現を出す」という発想は **grounding 側には生きている**。ただし**画像全体の記述（captioning）には持ち込まれていない。**

### 9-5. 前節までの記述の訂正

1. **Berger（TACL 2025）は「移行を扱う総説」ではない**（MLLM の語が0回）。査読付きで移行を明示するのは **Sarto と Abdulgalil の2本**。
2. **「recaptioning が主流」「DPO/RLAIF が標準」は査読付き総説には書かれていない。** 手法論文を根拠にすること。
3. 「VLM 期にキャプション生成は指示追従の一機能になった」という言い方は、**査読付き総説の言葉ではない**。Sarto は「**MLLM の core task になった**」と書いている。論文では後者の表現を使うのが安全。

### 9-6. 4本を読んで確定したこと

| 論点 | 4本での扱い |
|---|---|
| 識別性（distinctive / discriminative） | **4本とも本文の項目に無い**。Berger の参考文献と、Xiao の REG 節（speaker-listener）にだけ痕跡がある |
| 当て直し評価 | Berger の §4.1.2 に**評価プロトコルとして記載**（指標ではない）。他の3本は0回 |
| 粒度の適応制御（zoom / crop） | **4本とも0回**。手法レベルのみで、総説には未反映 |
| 長尾 | Abdulgalil §7.4 が唯一の明示的な扱い（認識の長尾、幻覚の原因として） |
| 評価の現状 | Berger：5指標が支配的で人手相関が弱い。Sarto：長い記述に既存指標が不適合、ドメイン固有語への対応が課題 |

**論文での使い方**：導入は Sarto の「core task になった」＋ Berger の「5指標に依存し人手評価と弱相関」で始め、**識別性と当て直しが総説の項目になっていない**ことを gap として示す。長尾は Abdulgalil §7.4 に接続する。粒度の切り替えは総説に無いので、手法論文（V*, ZoomEye, GFNet 系）に対して位置づける。
