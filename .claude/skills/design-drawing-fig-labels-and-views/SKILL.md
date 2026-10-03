---
name: design-drawing-fig-labels-and-views
description: Whenever processing design-patent drawings (IMPACT / USPTO design drawings, D00001 cover drawings, benchmark images) or writing/reviewing any prompt that shows them to an LLM or VLM — benchmark construction (judging, filtering, naming groups or blocks, captioning, quality checks), evaluation/inference (asking a model to name or describe the product), baselines, or training data — account for two facts: figure-number labels such as "FIG. 1" / "Fig. 2" are often printed inside the drawing and are not part of the product, and one drawing image may contain several views of the same product (FIG. 1 and FIG. 2 side by side, a perspective view plus a top view). State both explicitly in the prompt and keep both in mind when designing image processing (cropping, shape features, counting objects). Applies even when the user only says "write the eval prompt", "add a judge", "name the blocks", or "run baseline X".
---

# 意匠の図面の「図番号の文字」と「複数の視点の図」を考慮する

意匠の図面（IMPACT の表紙図面 D00001 など）には、次の2つがよくある（ユーザーの指摘、2026-10-03）。

1. **図番号の文字**：図の中に「FIG. 1」「Fig. 2」「Figure 1」「1.1」のような図番号が書かれている。製品の一部ではない
2. **複数の視点の図**：1 枚の画像の中に、同じ製品を別の向きから見た図が複数入っている（FIG. 1 と FIG. 2 を並べたもの、斜視図と上面図など）。別々の製品ではなく、1 つの製品

モデルはこれを知らないと誤る。図番号を製品の刻印と読む、2 つの視点の図を 2 つの製品（「セット」「ペア」）と答える、などが起きる。

## プロンプトに入れる文面

意匠の図面を LLM・VLM に見せるプロンプトには、点線の注記（`design-drawing-dashed-lines`）に続けて、次の 2 文を入れる。

英語（1 枚の図のとき）：

```text
Labels such as "FIG. 1" are figure numbers, not part of the product. The image
may show the same product from several viewpoints; treat those views as one product.
```

複数の図を並べて見せるとき（ブロックの名前づけなど）は「The image may …」を「One drawing may …」にする。

日本語：「FIG. 1 などの文字は図番号で、製品の一部ではない。1 枚の図に、同じ製品を複数の視点から描いた図が入っていることがあり、それらは 1 つの製品として扱う」

対象：判定、絞り込み、ブロックやグループの名前づけ、キャプションの生成、推論・評価（製品名を答えさせる、説明させる）、ベースラインの実行、学習データづくり。

## 画像の加工で気をつけること

- **複数の視点の図は切り分けない**（そのまま 1 枚として使う）。切り分ける場合は、設計書に規則を書いてから行う
- 形の特徴（DINOv2 の埋め込みなど）は、図番号の文字や、複数の図の並び方にも引きずられる。形の近さを解釈するときは、この影響があり得ることを念頭に置く
- 図番号の文字は、向きの判定（「FIG」の文字が横書きで読めるか）では逆に手がかりとして使っている。消してはいけない

## プロンプトを変えたら

- ハッシュでプロンプトを管理している処理は、文面を足すとハッシュが変わる。古い出力は `superseded/` に移し、検証からやり直す。古い出力と混ぜない
- 設計書に、足したこと・文面・やり直す範囲を書く（`feedback_record_processing_in_design_doc` の決まり）
- ベンチで比べる全モデルに、同じ文面を渡す
