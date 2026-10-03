---
name: design-drawing-dashed-lines
description: Whenever writing or reviewing any prompt that shows a design-patent drawing (IMPACT / USPTO design drawings, D00001 cover drawings, benchmark images) to an LLM or VLM — benchmark construction (judging, filtering, captioning, orientation or quality checks that look at the product), evaluation/inference (asking a model to name or describe the product), baselines and reproductions run on the benchmark, or training data built from model outputs — state explicitly in the prompt that dashed/dotted lines are only an aid to understanding and show things outside the product. For inference prompts that ask the model to name the product, also have it tell dashed from solid lines and, when dashed lines are present, answer as "<solid-line part> for <dashed-line whole>" (the way ground-truth titles of partial designs are written). Applies even when the user only says "write the eval prompt", "add a judge", "run baseline X on the benchmark", or "generate captions for the drawings".
---

# 意匠の図面を LLM・VLM に見せるときは、点線の意味をプロンプトに明記する

意匠の図面では、**点線（破線・一点鎖線）は理解を助けるために描かれたもので、製品の範囲外**を表す。周りの物（テールランプのレンズの図面に描かれた車体など）や、権利を主張しない部分がこれに当たる。製品名（`title`）が指すのは、実線で描かれた部分である。

モデルはこの約束事を知らないことが多い。点線の部分まで製品の形として扱うと、判定も推論も誤る。例：車体が点線で描かれたテールランプのレンズを「車」と答える、点線の周りの物を含めて「大まかな形で分かる」と判定する。

## いつ使うか

意匠の図面を LLM・VLM に見せるプロンプトは、すべて対象にする（ユーザーの判断、2026-10-02）。

- ベンチマークの作成：判定（例：「大まかな形で分かるか」）、絞り込み、キャプションの生成、製品を見て判断する品質の確認
- 推論・評価：製品名を答えさせる、説明させる、選ばせる
- ベースラインや再現実装（SpeciaRL、Fine-R1 など）をこのベンチで動かすとき
- モデルの出力から学習データを作るとき

向きの判定（「FIG」の文字の向きを聞く）のように、製品の形を見ない問いでは要らない。

## 文面

英語のプロンプトでは、次の文をそのまま使う（`freeform_shape_benchmark/judge_with_qwen.py` と `resolution_check.py` と同じ文面）：

```text
Dashed or dotted lines are drawn only to aid understanding: they show things
that are not part of the product, such as its surroundings.
```

- 図面の前置き（「This is a drawing of a product, ...」）の直後、製品名や問いの前に置く
- 「shown alone with no surroundings（周りはない）」とは書かない。点線で周りの物が描かれていることがあり、矛盾する。「with no background（背景はない）」と書く
- 形を問うときは「the shape of the product itself」のように、製品そのものの形であることを示す
- 日本語のプロンプトなら「点線は分かりやすくするためのもので、製品の範囲外（周りの物など）を表す」

## 推論（評価）では「点線（全体）の中の実線（一部）」の形で答えさせる

（2026-10-03、ユーザーの判断）製品の全体を点線で描き、一部だけを実線で描いた図面（部分の意匠）がある。例：チェーンソーの全体は点線で、伐採の目印だけ実線（正解「Felling marks」）。正解の製品名は、こうした図面では「実線の部分 + for / of + 点線の全体」の形で書かれていることが多い（Battery attachment interface for a tool、Portion of a rack for …、Fireplace or stove door）。

製品名を答えさせる推論のプロンプトでは、上の注記に加えて、点線と実線を区別させ、点線があるときはこの形で答えさせる。出力の粒度を正解の書き方に揃えるため。

```text
If the drawing has dashed or dotted lines, the product is only the part drawn in
solid lines; answer in the form "<solid-line part> for <dashed-line whole>"
(for example, "door for a columbarium"). If there are no dashed lines, answer
with the product name only.
```

- 部分の意匠を問題から除いたり、採点で部分点にしたりはしない
- 判定（「大まかな形で分かるか」など、正解の製品名を教えて聞く問い）には、この答え方の指示は要らない。点線の注記だけでよい

## プロンプトを変えたら

- ハッシュでプロンプトを管理している処理（例：判定の `prompt_hash`）は、注記を足すとハッシュが変わる。古い出力は `superseded/` に移し、検証としきい値の決め直しからやり直す。古い出力と混ぜない
- 設計書に、注記を足したこと・文面・やり直す範囲を書く（`feedback_record_processing_in_design_doc` の決まり）
- ベンチで比べる全モデルに、同じ文面を渡す（モデルごとに条件を変えない）
