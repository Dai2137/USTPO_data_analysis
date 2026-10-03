---
name: colab-notebook-conventions
description: Two conventions for any code/notebook in this project meant to be executed on Colab (GPU work — embedding extraction, model training/fine-tuning, any script needing a GPU the local machine doesn't have). (1) Create and edit these files directly under the Google Drive for Desktop path (`G:\マイドライブ\松尾研究室\LLMATCH\USPTO_data_analysis\...`), not the local project path (`C:\Users\Barre\松尾研\LLMATCH\USPTO_data_analysis\...`) — Colab only ever sees the Drive mount, so anything written to the local path is invisible to Colab no matter how correct the code is; this generalizes the COrAL-specific rule already in CLAUDE.md ("COrALは必ずDriveパスを直接編集") to any new Colab-bound project folder, not just COrAL. (2) Any Colab notebook driving a long/batch GPU job should end with a cell that calls `google.colab.runtime.unassign()` to release the runtime once work completes, so a free-tier GPU allocation doesn't sit idle after the job finishes. Apply both proactively whenever creating a new folder/notebook/script intended for Colab execution, even if the user doesn't explicitly ask for either.
---

# Colab notebook conventions for this project

## 1. Colab-bound files live on the Drive for Desktop path, not the local path

This project's local checkout (`C:\Users\Barre\松尾研\LLMATCH\USPTO_data_analysis\`) and its Google Drive for Desktop mount (`G:\マイドライブ\松尾研究室\LLMATCH\USPTO_data_analysis\`) are **two separate directory trees on disk**, not a symlink/junction of each other. Colab's `drive.mount()` only ever sees the Drive tree. CLAUDE.md already documents this for COrAL specifically ("COrAL コードは Google Drive for Desktop で同期されており... 必ず Drive パスを直接編集すること。ローカルパスを編集しても Colab に反映されない") — **this is not COrAL-specific; it applies to any new folder meant to run on Colab.**

Confirmed first-hand (2026-08): a whole new benchmark-construction folder (`shape_discrimination_benchmark/`) got built and iterated on entirely under the local path before this was caught, meaning none of that work would have been visible to Colab until manually copied over. The fix applied then: copy the finished local folder to the Drive path once (`cp -r <local>/shape_discrimination_benchmark <drive>/shape_discrimination_benchmark`), delete the now-redundant local copy, and do all further edits directly on the Drive path from that point on.

**Practical implications:**
- Both `C:\...` and `G:\マイドライブ\...` are ordinary Windows paths, fully readable/writable/executable by local tools (Bash, PowerShell, the local Python venv) — there is no technical reason to prefer editing locally first. Just target the Drive path directly with Write/Edit/Bash from the start for anything Colab-bound.
- The local Python venv can `import`/execute scripts living on the Drive path directly (`sys.path.insert(0, r'G:\...')`, or just running `python` against a `G:\...` script path) — useful for local sanity-testing (syntax, data-loading logic, non-GPU code paths) without needing GPU or Colab at all, while keeping the Drive copy as the single source of truth (no separate local copy to keep in sync).
- If a task is *not* going to be run on Colab (pure local analysis, data wrangling, one-off scripts), the local path remains the normal/default place — this rule only applies to code that will actually execute inside a Colab runtime.

## 2. End long/batch Colab jobs with a runtime-shutdown cell

Any notebook driving a job expected to run for more than a few minutes unattended (embedding extraction over thousands of images, training, hard-negative mining, ...) should end with a final cell:

```python
from google.colab import runtime
runtime.unassign()
```

This disconnects and releases the runtime once the preceding cells finish, instead of leaving an idle GPU session running until the user notices — relevant on free-tier Colab where GPU availability is quota-limited and shared. Precede it with a short markdown cell noting what it does, so it isn't mistaken for an accidental stray cell by someone reading the notebook later.

Reference implementation: `shape_discrimination_benchmark/build_shape_discrimination_benchmark.ipynb` (final markdown + code cell pair).
