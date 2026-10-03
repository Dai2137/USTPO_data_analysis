# 週次MTGレポート — 2026-08-20

## 背景・目標

見た目が紛らわしい製品を汎用AIが見分けられないことを前回までの実験で確認．意匠特許の図面画像から「見た目が紛らわしい製品同士を正しく見分けられるか」を測る多肢選択ベンチマークを新規に構築し、ファインチューニングなしの汎用マルチモーダルAIでの最初の評価結果を得た。

---

## 1. 今週の結果

### 1-1. 形状類似製品を見分ける4択ベンチマークの構築

意匠図面1枚を見せて、正しい製品名1つと、見た目が紛らわしい誤答3つの計4択から選ばせる形式のベンチマークを構築した。

構築の流れは以下の通り。

1. **画像の特徴ベクトル化:** 各意匠特許の表紙図面を、物体認識用に自己教師あり学習された画像エンコーダ（DINOv2）に通し、画像全体を要約する768次元のベクトルを取得する。
2. **類似画像の検索:** 全件分のベクトルを使って類似画像検索の索引を作り、ある1件（出題対象）について、見た目が近い順に他の意匠を検索できるようにする。
3. **誤答候補の絞り込み:** 見た目が近い順に候補を見ていき、(a) 出題対象と製品名が完全に同じもの、(b) 製品名が意味的にほぼ同じ言い換え・表記ゆれのもの（例：同じ製品を指す "Suitcase" と "Luggage" のような組み合わせ。製品名を別の埋め込みモデルでベクトル化し、意味的な近さがしきい値を超えるものを除外）、をどちらも除外する。
4. **段階的な検索範囲拡張:** 上記の除外後に3件の誤答候補が集まらなければ、検索範囲を倍々に広げて再試行する（"container" のように非常に頻出する製品名だと、上位の類似画像がほぼ同じ製品名で埋まってしまい、絞り込みに広い範囲が必要になるケースがあるため）。それでも3件集まらない場合はその意匠を出題対象から除外する。
5. **4択の完成:** 正解1件＋誤答3件をランダムな順番に並べ替えて4択問題として確定する。

この結果、誤答は「意味的に近い言い換え」を機械的に除いた上で、なお見た目としては紛らわしいものが残る設計になっている。工程3の同義語除外の基準（しきい値）は最初から完璧だったわけではなく、サンプル確認で見つかった混入をもとに調整した経緯がある（詳細は1-2参照）。最終的に2022年データ全件（31,470件、画面UI・アイコン意匠は対象外）に対して4択問題セットを完成させている。

### 1-2. サンプル20件の目視確認

ベンチマークがちゃんと機能しているか（画像と設問がずれていないか、誤答が見た目の紛らわしさとして妥当か）を確認するため、先頭20件を画像付きで目視確認した。

**設問1**
<img src="images/mcq_sample_D0949851.png" alt="設問1" width="320">
- A. **Battery pack（ゼロショット予測・ファインチューニング後予測）**
- B. Water heater
- C. Data output interface
- D. **Data reader（正解）**

**設問2**
<img src="images/mcq_sample_D0971479.png" alt="設問2" width="320">
- A. Panel tread for a paving system
- B. Organizer system and components of the organizer system
- C. **Panel light（正解・ゼロショット予測・ファインチューニング後予測）**
- D. Medication case

**設問3**
<img src="images/mcq_sample_D0959008.png" alt="設問3" width="320">
- A. Flip mount
- B. Optical end effector
- C. Night vision goggle
- D. **Massager（正解・ゼロショット予測・ファインチューニング後予測）**

**設問4**
<img src="images/mcq_sample_D0965975.png" alt="設問4" width="320">
- A. Small trolley case
- B. Storage cabinet handle
- C. **Luggage（正解・ゼロショット予測・ファインチューニング後予測）**
- D. Travel kit

**設問5**
<img src="images/mcq_sample_D0942735.png" alt="設問5" width="320">
- A. Electronic non-contact infrared thermometer X5
- B. Motor vehicle body, toy replica and/or other replica
- C. Articulating blade assembly for hair removal device
- D. **Wall-mounted safe（正解・ゼロショット予測・ファインチューニング後予測）**

**設問6**
<img src="images/mcq_sample_D0964203.png" alt="設問6" width="320">
- A. Dial
- B. Decorative element for jewellery
- C. Watch case
- D. **Pair of earrings（正解・ゼロショット予測・ファインチューニング後予測）**

**設問7**
<img src="images/mcq_sample_D0948964.png" alt="設問7" width="320">
- A. Trash can
- B. Air purifier
- C. **Container（正解・ゼロショット予測・ファインチューニング後予測）**
- D. Vacuum bottle

**設問8**
<img src="images/mcq_sample_D0964065.png" alt="設問8" width="320">
- A. Dispenser
- B. Ultrasonic imaging diagnostic device
- C. **Razor hanger（正解）**
- D. **Hat hook for wall mount（ゼロショット予測・ファインチューニング後予測）**

**設問9**
<img src="images/mcq_sample_D0942553.png" alt="設問9" width="320">
- A. **Toy（正解・ゼロショット予測・ファインチューニング後予測）**
- B. Buckle dinosaur pillow
- C. Unicorn shaped game board
- D. Inflatable toy

**設問10**
<img src="images/mcq_sample_D0947978.png" alt="設問10" width="320">
- A. Firearm suppressor
- B. Flashlight with an electronic insect repellent
- C. **Single shot protection device（正解）**
- D. **Flashlight（ゼロショット予測・ファインチューニング後予測）**

**設問11**
<img src="images/mcq_sample_D0970824.png" alt="設問11" width="320">
- A. **In vitro diagnostic device (IVD)（ファインチューニング後予測）**
- B. Cat feeder
- C. **Charging plug（ゼロショット予測）**
- D. **Pet feeding station（正解）**

**設問12**
<img src="images/mcq_sample_D0946806.png" alt="設問12" width="320">
- A. Folding table
- B. Display sign
- C. **Adjustable free standing sneeze guard（ゼロショット予測・ファインチューニング後予測）**
- D. **Plant grow light（正解）**

**設問13**
<img src="images/mcq_sample_D0959225.png" alt="設問13" width="320">
- A. Power grinder
- B. Disc cutter
- C. **Portable electric circular saw（正解・ゼロショット予測・ファインチューニング後予測）**
- D. Holster

**設問14**
<img src="images/mcq_sample_D0946496.png" alt="設問14" width="320">
- A. Cable management device
- B. Exercise weight device
- C. **Tire for automobile（ゼロショット予測・ファインチューニング後予測）**
- D. **Tire for motorcycle（正解）**

**設問15**
<img src="images/mcq_sample_D0945180.png" alt="設問15" width="320">
- A. **Toilet paper holder（正解・ゼロショット予測・ファインチューニング後予測）**
- B. Angled hinge hanger with elongated vertical tube
- C. Door handle
- D. Faucet

**設問16**
<img src="images/mcq_sample_D0946865.png" alt="設問16" width="320">
- A. Men's recovery garment
- B. **Underwear with folded diagonal fly（正解）**
- C. **Underwear（ゼロショット予測・ファインチューニング後予測）**
- D. Underwear with pouch with curved double darts

**設問17**
<img src="images/mcq_sample_D0943214.png" alt="設問17" width="320">
- A. Vacuum insulated bowl
- B. Flask
- C. Ultrasonic transducer for a fish finder
- D. **Powder compact（正解・ゼロショット予測・ファインチューニング後予測）**

**設問18**
<img src="images/mcq_sample_D0952203.png" alt="設問18" width="320">
- A. Head light
- B. Vehicle taillamp
- C. **Vehicle front headlamp daytime running lights（正解・ゼロショット予測・ファインチューニング後予測）**
- D. Taillight for a vehicle

**設問19**
<img src="images/mcq_sample_D0943587.png" alt="設問19" width="320">
- A. Cut stone for jewelry
- B. Animal habitat
- C. **Scope warmer apparatus（ゼロショット予測・ファインチューニング後予測）**
- D. **Sanitizable device case（正解）**

**設問20**
<img src="images/mcq_sample_D0952065.png" alt="設問20" width="320">
- A. **Stepper（正解・ファインチューニング後予測）**
- B. Footwear midsole and outsole
- C. Shoe
- D. **Shoe sole tread（ゼロショット予測）**

#### 分かったこと

1. **画像と設問のズレは見つからなかった。** 20件全て、表示されている図面と正解タイトルが正しく対応している。
2. **誤答は「意味的に近い」だけでなく「見た目としても紛らわしい」ものが選ばれている。** 例えば設問20は正解が「Stepper」（足踏み運動器具）だが、誤答には靴底・靴のパーツ関連が3つ並んでおり、実際の画像も足裏の形をした凹凸のある面という、靴のインソール・アウトソールと見分けが難しい形状になっている。誤答が単なる同義語の言い換えではなく、本当に形状ベースで紛らわしい候補になっていることが確認できた。
3. **同一カテゴリ内の細かい違いを問う設問もある。** 設問16は「下着」を示す選択肢が3つあり，どれも正解であるので，問題として成立していない．詳しい修飾を抜けば同じ単語になる選択肢は排除する方法を要検討．
4. **この20件だけ見ても、ファインチューニング後にゼロショット・ファインチューニング後どちらも予測を並べて確認したところ、20件中18件は両モデルとも同じ予測だった一方、設問11, 20が異なる予測だった。** ．


### 1-3. zero-shot, ファインチューニング後モデルでの評価結果

zero-shotと全く同じテストセット・同じ聞き方で、意匠タイトルの自由記述予測用に別途LoRAファインチューニング済みのモデル（2021年データで学習）にも解かせた。このモデルは4択の見分け方自体を学習したことは一度もなく、「タイトルを言い当てる」学習で得た知識がこの4択タスクにどこまで転移するかを見る位置づけ。

#### 精度結果（n=31,470、zero-shotと同一テストセット）

| 指標 | zero-shot | タイトル特化ファインチューニング後 |
| --- | --- | --- |
| 正答率 | 54.84% | 56.36% |

#### ロカルノ大分類別 正答率（zero-shot・LoRA後どちらかの下位10件の和集合、LoRA後の低い順）

| 分類コード | 内容 | 件数 | zero-shot | LoRA後 | 差分 |
| --- | --- | --- | --- | --- | --- |
| 31 | 調理用機械・器具 | 132 | 51.5% | 48.5% | -3.0pt |
| 12 | 輸送・搬送機器 | 2,439 | 50.8% | 51.1% | +0.3pt |
| 07 | 家庭用品（他に分類されないもの） | 1,930 | 圏外（良好） | 52.8% | — |
| 23 | 流体供給・衛生・空調機器等 | 1,961 | 圏外（良好） | 53.7% | — |
| 13 | 電気機器（発電・変電・配電） | 1,612 | 49.8% | 53.7% | +3.9pt |
| 25 | 建築ユニット・建築部材 | 547 | 50.1% | 53.9% | +3.8pt |
| 26 | 照明用機器 | 1,525 | 48.6% | 54.0% | +5.4pt |
| 08 | 工具・金物類 | 1,501 | 圏外（良好） | 54.0% | — |
| 10 | 時計・計測機器 | 989 | 46.1% | 54.8% | +8.7pt |
| 14 | 記録・通信・データ処理機器 | 2,843 | 53.6% | 55.0% | +1.4pt |
| 01 | 食料品 | 121 | 37.2% | 圏外（改善） | — |
| 24 | 医療・実験用器具 | 1,874 | 46.7% | 圏外（改善） | — |
| 15 | 機械（他に分類されないもの） | 1,372 | 53.1% | 圏外（改善） | — |

「圏外」＝両モデルそれぞれの下位10分類には入らなかった分野（zero-shotの10位が53.6%、LoRA後の10位が55.0%なので、少なくともそれ以上の正答率）。

#### 分かったこと

1. **ファインチューニング後は正答率が+1.51pt向上した（54.84%→56.36%）が，大きな向上には至らなかった。** 予測を間違えるようなニッチ/難しい概念の意匠と同じニッチ/概念の意匠は過去に学習データとしてないため，テストデータの正解率を上げるに寄与しないことが原因の1つとして考えられる．現状学習データは1年のみなので，学習データを増やせば大きく正答率を上げる可能性はある．件数が多い輸送・搬送機器，記録・通信・データ処理機器の向上が小さい．過去の意匠が未来の意匠の参考になっていない可能性があるため，個別対処することも検討されるが，研究のメインアイデアにはなりにくそうなので優先度は低め．
2. **分野間に正答率の違いはあまり見受けられない** 

   

#### 参考: 学習データ（2021年）と評価データ（2022年）のロカルノ大分類別件数

<img src="images/locarno_distribution_2021_2022.png" alt="2021年・2022年のロカルノ大分類別件数分布" width="700">

上記の分野ごとの正答率変化が、学習データと評価データの分野構成の偏りだけで説明できるかを確認するため分布を比較した。今回悪化・新規に下位入りした分類（調理用機械・器具、家庭用品、工具・金物類、流体供給・衛生・空調機器等）も、大幅に改善した分類（食料品、医療・実験用器具、時計・計測機器など）も、2021年と2022年で件数比率に大きな偏りは見られない。正答率が低い分野の顔ぶれの入れ替わりは、学習データの分野別の量の偏りだけでは説明できず、各分野内での意匠の見た目の傾向差など、別の要因を見る必要がありそうだ。

---

## 2. 今後やること

1. Titleの正規化．粒度を揃える．
選択肢の粒度が揃っていないことにより誤答した具体例．Underwearが3つある．

具体例
**設問16**
- A. Men's recovery garment
- B. **Underwear with folded diagonal fly（正解）**
- C. **Underwear（ゼロショット予測・ファインチューニング後予測）**
- D. Underwear with pouch with curved double darts

2. ベンチマークの画像を複数視点にする．
fig descに複数視点の説明が書いてあるのでうまく使いたい

3. 推論方法の検討
どういう風に推論すれば正解に近づけるか，人間ならどう判断するか考える．それをAIで表現するには？

## 3. FB
ベンチマークの提案は2つ方針がある．

実用的→意匠の実用の方ならindustry track 

学術的→GPTなど既存の良いモデルでも見分けられない理由が必要．
タスクはいくらでも難しくできると思うので，最先端のモデルでも解けない．事後学習で多少なりとも解けるようになればいい．

---

作成: 2026-08-20
