---
name: resumable-batch-jobs
description: Whenever writing, scaffolding, or reviewing a long-running batch script in this project (embedding extraction, hard-negative mining, any per-item loop over thousands of images/rows) that is meant to run on Colab or another interruption-prone environment — make it resumable via periodic checkpointing, instead of holding all results in memory and writing output only at the very end. This applies proactively even if the user doesn't say "resumable" or "checkpoint" explicitly (e.g. "write a script that embeds all the images", "loop over the dataset and build X"). Motivation: free-tier Colab GPU sessions disconnect/time out unpredictably (idle timeout, 12h hard cap, runtime disconnects), and this project's jobs run against ~30k+ images per year of IMPACT data — losing all progress on disconnect is a real, recurring cost, not a hypothetical.
---

# Making long-running batch jobs resumable

## The problem

A script that processes N items (encode N images, mine hard negatives for N queries, call an API N times, ...) and only writes its result at the very end loses **all** progress if the process is killed partway — and on Colab free tier, that's not a rare event: idle timeouts, the ~12h hard session cap, and plain disconnects happen routinely, especially on long jobs. For this project's scale (IMPACT has 20k-35k patents per year), a multi-hour job re-run from scratch after a late-stage disconnect is a real, recurring cost — see `shape_discrimination_benchmark/build_image_index.py` and `build_hard_negative_mcq.py` for reference implementations of the two patterns below.

## The pattern: checkpoint to persistent storage, skip what's already done on restart

Two concrete shapes, depending on whether the job produces one array-like result or a stream of independent per-item records:

### Pattern A — batched array output (e.g. embedding extraction)

Used when the job accumulates into one big array (embeddings, features) that gets bulk-written (FAISS index, `.npy`) at the end.

1. On startup, look for `{out_dir}/_checkpoint_*` files. If present, load them — they contain the ids/rows already processed and their results.
2. Filter the input (dataset/dataframe/list) to exclude already-done ids **before** building the dataloader/iterator — never re-touch what's done.
3. Every `--checkpoint-every N` batches, concatenate the new results onto the loaded checkpoint and overwrite the checkpoint files. Checkpoint saves must be cheap relative to N batches of work, so N shouldn't be so small that I/O dominates.
4. After the loop, do the final bulk write (index, CSV, ...) from the full combined array, then delete the checkpoint files — their job is done and leaving them around risks a future run silently reading stale partial state.

Reference: `shape_discrimination_benchmark/build_image_index.py` (`_load_checkpoint`, `_save_checkpoint`, `_clear_checkpoint`, `CoverImageDataset(skip_ids=...)`).

### Pattern B — independent per-item records (e.g. mining/generation/API calls per row)

Used when each item's result is independent of the others (no final bulk-write step needed) — this is the simpler and generally preferable pattern when it applies.

1. Output format is **JSONL, not a single JSON array** — one line per item, so partial output is always structurally valid and directly appendable.
2. Open the output file in append mode; write + `flush()` after **every** item (not batched) — the whole point is that a kill at any moment loses at most the one in-flight item, not a buffer of unflushed work.
3. On startup, read the existing output file (if any) and collect the set of ids already present — including ids that were explicitly logged as "skipped/failed" (write a `{"id": ..., "skipped": true}` marker line for those too), so a chronically-failing item doesn't get expensively retried every single resume.
4. Filter the work list to exclude those ids before starting the loop.

Reference: `shape_discrimination_benchmark/build_hard_negative_mcq.py` (`_load_done_ids`, append-mode `open(..., "a")` with `f.flush()` per item).

## When NOT to bother

- Jobs that complete in a couple minutes even from scratch — checkpointing overhead/complexity isn't worth it below roughly the 10-15 minute mark.
- Pure local CPU jobs with no risk of external interruption (though even then, a crash mid-script is still possible — err on the side of Pattern B's JSONL-append approach when it's nearly free to do, since it costs little beyond "don't buffer everything in memory").

## Where output must live

Checkpoint/output files must be written to storage that survives the interruption — for Colab, that means the Drive-mounted path (`/content/drive/MyDrive/...`), never the ephemeral local Colab VM disk (`/content/...` outside the Drive mount), since a disconnect wipes the VM entirely.
