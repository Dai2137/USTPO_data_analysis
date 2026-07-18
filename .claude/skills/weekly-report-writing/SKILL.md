---
name: weekly-report-writing
description: Writing conventions for this project's weekly MTG reports (`weekly_reports/weekly_report_YYYYMMDD.md`). Use whenever creating or updating a weekly report file, or drafting content intended to go into one.
---

# Weekly report writing conventions

Reference for `weekly_reports/weekly_report_YYYYMMDD.md`. Read this before writing or editing a weekly report.

## Don't put file names / paths in the report body

Weekly reports describe what was done and what was found — not which file it lives in. Do not write things like "評価コードは `eval_qwen_l3filtered.ipynb`" or "`qwen_eval/locarno_class_distribution.csv`に保存済み" inside the report prose.

**Why:** File names and paths are implementation detail that changes as the project reorganizes (e.g. notebooks got moved from `COrAL/` to `qwen_eval/` mid-project). A report that names files goes stale or becomes misleading when files move, even though the underlying finding is still valid. The report should stand on its own as a record of decisions/results, not as a pointer into the current directory layout.

**How to apply:** Describe experiments, methods, and results by what they are ("L3フィルタ済みデータでのzero-shot評価", "クラス別性能分析"), not by which script produced them. If a specific file needs to be referenced for someone to reproduce or find the code, that belongs in conversation/commit messages/CLAUDE.md, not the weekly report.

## Don't put tooling/implementation debugging detail in the report body

Weekly reports record research findings and decisions, not incidental bugs hit while building the analysis tooling itself (e.g. a TIFF rendering glitch in a visualization script, a pandas dtype quirk, a notebook file getting too large to edit). Even when such a bug is real and worth noting somewhere, it does not belong in the WR unless it materially changes how a result should be interpreted (and even then, state the interpretive caveat, not the debugging story).

**Why:** The user explicitly cut this kind of content after it was added ("WRには描画不具合とか書かないで"). The WR is read as a record of the research, not a debugging log — implementation noise dilutes it.

**How to apply:** Before adding a paragraph about something that broke or looked wrong, ask whether it's a finding about the data/model or a story about fixing a tool. If the latter, leave it out of the WR entirely (it can stay in conversation/commit history if needed).

## Don't name code-level identifiers (function names, column names, variable names)

Do not write things like "`compute_ranks_locarno_filter`関数で再計算した" or "`major_class`列を`locarno_class`から生成した". Describe the operation in plain research language instead: "同一ロカルノクラス内に候補を絞ってランクを再計算した", "ロカルノ大分類は正式なロカルノ分類コードから求めた".

**Why:** Function/column/variable names are implementation vocabulary, not research vocabulary — a reader (including future-you) shouldn't need to know the code's internal naming to understand what was measured or found. This is the same principle as the file-names rule above, one level more granular: it applies even when no file is named, to identifiers alone.

**How to apply:** Read each sentence and ask "would this sentence make sense to someone who has never opened the code?" If it only makes sense to someone who has, rewrite it in plain terms or cut it.

## Weight the report toward results and what's next, not a blow-by-blow of what was done

The report is not a session transcript. For each item: state what was investigated/built (briefly), then spend the real space on **what was found** and **what it implies for next steps**. The "今後やること" section is the most important part of the report, not an appendix — give it real substance (concrete next actions grounded in this week's findings), not a leftover bullet list.

**Why:** The user explicitly asked to stop reporting at the level of "関数名とか、列の名前とか" and to make results + next-steps the main content ("もっと大事なのはこれからやること"). A report that narrates implementation steps buries the two things a reader actually needs: what do we know now, and what happens next.

**How to apply:** When drafting or editing a section, check the ratio — if setup/method description is longer than the findings+implications, trim the former. When drafting "今後やること", derive each item explicitly from a finding stated earlier in the report rather than restating a generic backlog item.
