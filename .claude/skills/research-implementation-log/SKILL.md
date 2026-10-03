---
name: research-implementation-log
description: Whenever you discover and fix a data-quality issue, implementation bug, or non-obvious engineering workaround in this project (e.g. mining/filtering logic that let bad examples through, a corrupted or ambiguous field, a performance bottleneck, a threshold/heuristic that needed calibrating) — proactively record it as a new entry in `research_implementation_log.md` under `## 実装上の困難と解決策`. Also fires for a diagnostic/isolation ("切り分け") investigation — attributing an observed failure or effect to one of several candidate causes (e.g. "which layer/stage/component is responsible", A/B/Reasoning-style attribution, a bug-vs-environment isolation, a decision tree over metrics) — which goes under `## 研究上の判断` if it's a research/evaluation-design attribution, or `## 実装上の困難と解決策` if it's a bug/environment root-cause hunt; log the reasoning (candidates considered, decision criteria fixed before results, actual results, verdict) not just the conclusion — and when the isolation runs over several rounds (a result exposes a new hypothesis or confound, which drives the next check), append each round as it lands, including rejected test designs, measurement bugs that changed the interpretation, and corrected premises. Applies proactively without waiting for the user to ask, even when the user's own request was just "fix X", "why does this fail", or "figure out which of these it is."
---

# Logging implementation findings to research_implementation_log.md

`research_implementation_log.md` is the primary interview/retrospective artifact for this project (per CLAUDE.md). A fix that isn't logged here effectively didn't happen, for the purpose of that document's job — so log proactively, the moment a fix lands, not only when asked.

## When this fires

Any of these, discovered or resolved during this session's work:
- A data-quality defect found via inspection (sample check, quantified audit) rather than an obvious crash — e.g. near-synonym contamination in benchmark distractors, a corrupted/mismatched field, silently-wrong output that still "ran successfully."
- A threshold, heuristic, or calibration value chosen or adjusted, especially when the reasoning is "good enough for now, revisit later" rather than a fully principled choice.
- A non-obvious engineering workaround (I/O bottleneck fix, environment-specific quirk, a design choice made to avoid a subtler failure mode).
- A **diagnostic isolation ("切り分け")** investigation — deciding which of several candidate causes explains an observed effect, rather than just measuring performance. Two flavors, both logged the same way (see "Logging a 切り分け" below), just to different sections:
  - Bug/environment root-cause hunts ("is this an upstream bug or my install", "OOM from batch size or from checkpointing being off") → `## 実装上の困難と解決策`, same as any other 困難 entry.
  - Research/evaluation-design attribution ("which processing layer/stage is responsible for the failure", A/B/Reasoning-style attribution, a decision tree over metrics defined before seeing results) → `## 研究上の判断`, using the extra structure below.

Routine code cleanup, renames, or mechanical edits with no judgment call behind them do **not** need an entry — the log is for things future-you would otherwise have to re-derive or forget.

## Entry template

Add a new `### 困難 N：<short title>` subsection (find the next number via existing `### 困難 N` headings) before the closing `---` / `## 今後の課題` boundary. Structure, following the pattern established by 困難9 (synonym contamination in `shape_discrimination_benchmark`):

1. **発覚の経緯** — how it was found (a sample check, a user-reported anomaly, a quantified audit). One or two sentences; this grounds the entry as a real event, not a hypothetical.
2. **定量化 with a real-data table** — this is the part most worth insisting on. Don't just say "some titles were near-duplicates" — pull the actual flagged/affected examples (ids, values, scores) into a small markdown table, and state the affected count/percentage if you computed one. A future reader (including you, in an interview) needs the concrete evidence, not a paraphrase.
3. **原因** — the mechanism, stated precisely enough that the same class of bug is recognizable next time (e.g. "exact-string exclusion doesn't catch synonymy" is a transferable insight; "there was a bug" is not).
4. **対応** — what was actually changed (function/parameter names are fine here, unlike in weekly reports — this is an implementation log, not a research summary), and any operational caveat (e.g. a resumable job's skip-by-id logic silently preserving stale pre-fix output unless old files are deleted first).
5. **教訓** (optional but valuable) — the generalizable lesson, one or two sentences, framed so it's useful to a different future problem, not just this one.

If a value chosen in step 4 is explicitly provisional (chosen to unblock progress rather than fully tuned), say so plainly — "0.80 は暫定値、パイプライン完成後に再調整" reads honestly in a retrospective; a value presented as final when it wasn't does not.

## Logging a 切り分け (diagnostic isolation)

A 切り分け investigation's value isn't the final number — it's the reasoning that turned an ambiguous failure into a located cause: what candidates were on the table, what evidence would have counted as pointing to each, and how the actual evidence lined up (or didn't). Logging only the conclusion throws that away, and makes it impossible to tell in retrospect whether the conclusion was principled or a story fitted after the fact to whatever number came out.

**The core discipline: fix the decision criteria before the results exist.** Draft the candidates and decision criteria (points 2–3 below) while planning the experiment — before the numbers come in — and copy them into the log close to verbatim rather than re-deriving softer ones once the result is known. If a design doc or notebook already states a decision tree, reuse it as-is.

For a research/evaluation-design attribution, add a `### N. <what is being isolated>` entry under `## 研究上の判断` with:

1. **切り分けたい問い** — the ambiguous observation and the question it raises, in one or two sentences.
2. **候補原因** — the enumerated candidate loci, stated so each is falsifiable/distinguishable, not just named.
3. **判定基準（事前定義）** — the metric(s), threshold/calibration method, and decision tree that route an outcome to a candidate, written down *before* results. State explicitly what would make the criteria themselves suspect (a "contradiction" quadrant, a floor effect) — that's part of the criteria, not an afterthought.
4. **結果** — the actual numbers, as a table when comparing candidates/conditions, including whatever comparison the criteria call for (e.g. correct vs. wrong-answer distributions), not just the isolated metric.
5. **判定** — which branch of the decision tree the result actually falls into. If it's ambiguous, contradicts the naive read, or trips one of the "measurement is suspect" flags from step 3, say that plainly rather than smoothing it into a clean story (e.g. "名目象限は(小,大)だが実態は…、ただし mean-pool 自体が分離力を過小評価している疑いが強い").
6. **次の一手** — what the verdict rules in/out and what to isolate next. This is what keeps a multi-experiment plan (実験1→2→3…) coherent across sessions.

If steps 1–3 were already written during planning (e.g. sitting in a design doc or memory file), a results addendum to the same entry (a dated sub-heading) covers 4–6 — don't create a duplicate entry.

A bug/environment root-cause hunt uses the same "candidates → what would confirm each → evidence → verdict" shape, but folds into the ordinary `### 困難 N` template above (原因 step) rather than the 6-point structure — it's still a 困難 entry, just one whose 原因 section shows the elimination process instead of jumping straight to the answer.

**Reference example:** the attribution-diagnosis project memory (layer A/B/Reasoning isolation for the 8-choice shape-discrimination benchmark, `attribution_diagnosis/design_doc.md` and `project_attribution_diagnosis_plan.md`) is a complete worked example: candidates (層A-encoder / 層A-merger / 下流B・Reasoning) enumerated before running anything, a decision tree fixed in advance, then a results addendum that reports the numbers, states the nominal quadrant, and flags that the measurement itself (mean-pooling) likely under-detects separability — driving a concrete next step (re-measure with centering/max-pool/token-pairs) rather than prematurely closing the question.

## 複数ラウンドにわたる切り分け（思考の過程を残す）

切り分けは1回で終わらないことが多い。最初の結果が「測り方そのものが怪しい」を示し、そこから新しい仮説 → 区別する検証 → 結果 → 新たな交絡…と連鎖する（例：実験1でマージャ前の表現が潰れた → 共通成分か mean-pool か → トークン単位 0.938 / mean-pool 0.999 → 白背景パッチの交絡が残る → LayerNorm 後のトークンで再検証）。この連鎖の各段が思考の過程そのもので、結論だけ残すと「なぜ次にその検証を選んだか」が失われる。

- **ラウンドごとに、結果が出たその場で追記する。** 最終結論を待たない。同じエントリの下に `#### ラウンドN（YYYY-MM-DD）：<問い>` を積む。
- 各ラウンドに書くこと：
  1. **仮説** — 候補を並べる。前ラウンドの結果から出てきたものならその旨
  2. **区別する予測** — 各仮説が正しければ何が観測されるか。仮説間で予測が同じなら「この検証では区別できない」と明記
  3. **検証** — 何を、どの規模で（サンプリングならシード・件数）
  4. **結果** — 数値（比較は表で）
  5. **更新された解釈** — どれが支持/棄却されたか。両方効いているならその内訳
  6. **残る交絡・未解決点** — この検証で分けられなかったこと。これが次ラウンドの問いになる
- **誤り・遠回りも残す。** 測定バグ（別の量を測っていた等）で解釈が変わったら、訂正した事実と「バグ前にどう読みかけていたか」を1行残す。バグの詳細は `### 困難 N` に分けて書き、相互参照する。ユーザーの指摘で前提を訂正した場合も、どの前提が誤りだったかを残す。
- **採らなかった検証案も1行残す。** 例：「全件・決定的な要因計画も検討したが過剰と判断し、ランダム抽出の簡易検証にした」。

## Keep updates in sync across docs, not just the log

When a fix changes a concrete value referenced elsewhere (a default threshold, a magic number in a design doc's addendum, a notebook markdown cell explaining the same parameter), update those in the same pass — the log entry is the durable record of *why*, but stale numbers in the design doc or notebook actively mislead the next person (including future-you) who reads them without also reading the log.

## Reference example

See `research_implementation_log.md` 困難9 (「4択ベンチマークのハードネガティブへの同義語混入」) for a complete worked example: discovery via sample check → quantified at 12.99%/4,088 items with a 6-row real-example table (Luggage/Suitcase, Head lamp for an automobile/Head lamp for automobile, ...) → root cause (exact-title exclusion misses synonymy) → fix (embedding-based exclusion, `--synonym-threshold`) → a later follow-up entry recording the threshold being loosened from 0.85 to 0.80 as a deliberate provisional call, with the reasoning stated rather than left implicit.
