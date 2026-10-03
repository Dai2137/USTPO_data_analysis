---
name: fgvc-single-object-scope
description: Scope rule for deciding which prior work counts as related work for this project's fine-grained recognition line (benchmark + global/local diagnosis + per-sample global/local weighting method). This project only targets single-object, object-centric fine-grained visual recognition (FGVC in the CUB-200-2011 / Stanford Cars / FGVC-Aircraft / Stanford Dogs / NABirds sense) — one object fills the image and the task is to name its subordinate category. Papers that say "fine-grained" but actually search a cluttered or high-resolution scene for a small object, then zoom/crop/upsample it to answer a VQA question (V*, ViCrop/"MLLMs Know Where to Look", Chain-of-Focus, CropVLM, AwaRes, Zooming without Zooming, DyFo-style visual search, TextVQA/DocVQA/HR-Bench/V*Bench evaluations) are OUT of scope and must be excluded, not classified as competitors. Also exclude papers that are not framed as FGVC in their own text even if they report numbers on CUB/Cars/Aircraft (general CLIP zero-shot classification, test-time adaptation/prompt tuning, calibration, adversarial robustness, efficiency-oriented dynamic networks evaluated on ImageNet). Use whenever collecting, screening, classifying or citing related work, writing a deep-research prompt, summarizing survey results, building the literature classification tree, or organizing the paper PDF folders — even if the user only says "fine-grained" or "look for similar methods".
---

# FGVC の対象範囲：画像に物体が1つだけ写る細粒度認識に限る

## 対象
- 画像に対象物が1つ大きく写っていて、その下位カテゴリ名を当てるタスク。
- データセットの例：CUB-200-2011、Stanford Cars、FGVC-Aircraft、Stanford Dogs、NABirds、Oxford Flowers、iNaturalist。
- 論文自身が、自分の研究を細粒度認識（FGVC / FGVR / FGIC、subordinate-level categories）の文脈に置いていること。

## 除外する（関連研究の分類木に入れない）
1. **小物体の探索・ズーム・VQA 系**
   - 複数の物が写った画像や高解像度画像から、小さく写った対象を探し、ズーム・クロップ・高解像度化して質問に答えるもの。"fine-grained perception" や "fine-grained details" と書いていても除外する。
   - 例：V*（SEAL）、ViCrop（MLLMs Know Where to Look）、Chain-of-Focus、CropVLM、AwaRes、Zooming without Zooming、DyFo。
   - 目印：評価が TextVQA / DocVQA / V*Bench / HR-Bench / POPE / GQA、質問文が見る場所を決める、small object / high-resolution が動機。
2. **FGVC の文脈に置かれていない汎用手法**
   - CUB や Cars の数字を報告していても、本文が細粒度認識を問題にしていなければ除外する。"fine-grained" がテキスト記述の細かさや、評価データセットの呼び名としてしか出てこない場合も同じ。
   - 例：汎用の CLIP ゼロショット分類（WCA、BiFTA、CALIP、ABS、GC-CLIP、AWT）、テスト時適応・プロンプト調整（TPT、MTA、ZERO）、キャリブレーション（CoTS）、敵対的頑健性（R-TPT、TTP）、効率目的の動的ネットワーク（GFNet、ImageNet 評価）、解釈可能 ZSL（LaZSL）、解釈可能モデル・一般化ゼロショット学習（DOT-CBM、HIL-CBM、Part Prototype Network。CUB で評価するが、問題設定は解釈可能性や GZSL）、汎用の VLM 事前学習（FLAIR）。

## 判定の手順
1. アブストラクトと導入を読み、細粒度認識が研究の問題設定かどうかを見る。評価表のデータセット名だけでは判断しない。
2. 評価データセットを見る。物体中心の細粒度データセットか、VQA・高解像度ベンチか。
3. 迷ったら除外側に置き、「除外理由」を1文書く。実験のベースラインとして使うのは構わない。ただし関連研究の分類木には入れない。

## 理由
本研究の問いは「物体は1つで、写っている場所も分かっている。そのうえで、名前を決める手がかりが全体の形にあるのか、局所にあるのか」。小物体探索系の「どこに物があるか分からないから探す」問題とは、探す対象が違う。混ぜると、既存手法が提案手法の葉を埋めているように見えたり、差分の説明がずれたりする。

## 用語：上位カテゴリとカテゴリを厳密に分ける
- **上位カテゴリ**（super-category）：鳥、車、航空機のような大分類。
- **カテゴリ**（category、subordinate category）：鳥の種のような下位の分類。CUB のクラス名に当たる。
- 分類木の軸はこの区別に依存する（B-1：テストの上位カテゴリが学習と違うときに対応できるか。B-2：テストと同じ上位カテゴリの画像を手法の中で用いるか）。「カテゴリ」と書くときは、どちらの意味かを確かめる。
