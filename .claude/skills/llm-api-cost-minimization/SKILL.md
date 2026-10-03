---
name: llm-api-cost-minimization
description: Whenever writing, reviewing, or planning code that calls a paid third-party LLM/VLM API (OpenAI, Anthropic, Google, etc.) in this project — actively look for ways to minimize cost before running at any scale beyond a handful of items: cheapest model that could plausibly work, image detail/resolution reduction, output-token and reasoning-effort minimization, Batch API for non-latency-sensitive runs, and a small-sample cost/accuracy check before any large run. Apply proactively whenever a script/notebook is about to make a paid API call over more than a few items, even if the user doesn't mention cost, price, or budget.
---

# 外部LLM/VLM APIのコストを最小化する

## 背景

`shape_discrimination_benchmark/build_shape_discrimination_benchmark.ipynb` フェーズ7で
OpenAI GPT-5-nanoを使う際、全31,470件をいきなり高解像度・高コストなモデルで流すと
$100超になり得ることが判明した（見積もり: gpt-4o通常APIで約$113）。一方、最安モデル
（gpt-5-nano）・画像の事前ダウンスケール・`detail: "low"`・Batch APIを組み合わせると、
同じ件数を$1未満まで下げられる。**この10倍以上のコスト差は「気をつければ避けられる」もの
であり、実装時に毎回チェックリストとして意識すべき。**

このプロジェクトは有料APIを繰り返し・大量に叩く場面（ベンチマーク評価、機能文生成など）が
多いため、以下を新しい外部API呼び出しコードを書く・レビューするたびに確認する。

## チェックリスト

### 1. 大量実行の前に、必ず少数件（1〜20件程度）でコスト・精度を検証する

いきなり全件は流さない。実際のレスポンスの `usage`（プロンプト/出力トークン数）を見て、
想定件数に外挿したコストを本人に提示してから全件実行の判断を仰ぐ。トークン数は画像サイズ・
プロンプト長・モデルの内部トークナイズ方式（タイル方式 vs パッチ方式）で見積もりが外れやすく、
実測するのが一番確実。

### 2. 最も安いモデルからまず試す

`nano` / `mini` 系（例: `gpt-5-nano`, `gpt-4.1-nano`, `gpt-4o-mini`）を既定の第一候補とする。
精度が要件に満たない場合だけ、段階的に上位モデル（`gpt-5-mini` → `gpt-5` / `gpt-4.1` →
`gpt-4o`）へ上げる。最初から旗艦モデルを選ばない。

### 3. 画像入力: detail/resolutionを必ず確認する

- OpenAI系APIの`detail`パラメータは`low`/`high`（新しいモデルでは`original`/`auto`も）を
  取り、`low`は512×512相当に固定縮小されて大幅に安い。線画・単純な図形など細部が精度に
  効かないタスクでは`low`を既定候補にする。
- `detail`だけでなく、**送信前に画像自体を縮小する**のも有効（512px程度にリサイズしてから
  送ると、`high`でもタイル数/パッチ数が減りトークンが数分の1になる）。特に高解像度スキャン
  画像（このプロジェクトのUSPTO意匠図面TIFFなど）は、そのまま送ると無駄に高コストになりやすい。
- どちらの効き方も実際にはモデルによって挙動が異なる（`detail`パラメータを無視するモデルの
  報告例もある）ため、必ず1.のusage実測で確認する。

### 4. 出力トークンを絞る

`max_tokens` / `max_completion_tokens` を実際に必要な分だけに設定する（例: 4択の記号1文字
だけが欲しいなら十数トークンで十分。長い自由記述が要る場合のみ増やす）。

### 5. reasoningモデルはreasoning_effortを絞る

GPT-5系などの推論モデルは、出力とは別に課金対象の reasoning token を消費しうる。単純な
分類・選択タスクでは `reasoning_effort: "minimal"`（対応モデルの場合）を既定にし、reasoning
tokenの浪費を防ぐ。

### 6. レイテンシが問題にならない大量処理はBatch APIを使う

即時レスポンスが不要な評価・生成ジョブ（このプロジェクトのベンチマーク評価はほぼ全てこれに
該当する）では、Batch APIで通常の50%引きにできる。全件評価のような大量ジョブを組むときは、
同期APIをループで叩く実装ではなくBatch APIを第一候補として検討する。

### 7. 事前に概算を出してから実行判断を仰ぐ

「1件あたりの想定トークン数 × 件数 × モデル価格」で全体コストをざっくり計算し、実行前に
提示する。モデル・APIモード（通常/Batch）を横に並べた比較表があると判断しやすい。

## 適用範囲

このプロジェクトで外部の有料LLM/VLM APIを呼ぶあらゆる箇所（ベンチマーク評価、機能文生成、
将来追加されうるOpenAI/Anthropic/Google API連携など）。ローカルGPUで動かす自前モデル
（Qwen-VL, DINOv2, ModernBERTなど）には課金の概念がないため対象外（そちらの解像度上限は
[[qwen-vl-resolution-cap]] 参照）。
