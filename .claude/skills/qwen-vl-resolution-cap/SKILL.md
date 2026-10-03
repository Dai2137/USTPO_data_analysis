---
name: qwen-vl-resolution-cap
description: Whenever loading a Qwen2-VL/Qwen2.5-VL/Qwen3-VL (or any other "native resolution" vision-transformer) AutoProcessor in this project to run on IMPACT design patent images — always pass explicit min_pixels/max_pixels to AutoProcessor.from_pretrained(), reusing this project's established value (min_pixels=256*28*28, max_pixels=512*28*28) rather than guessing a new one or omitting it. Apply proactively any time code loads a Qwen-VL-family processor for inference or training on this project's patent drawing images, even if the user doesn't mention resolution, memory, or OOM.
---

# Qwen-VL family: always cap input resolution for IMPACT images

## The problem

Qwen2-VL/Qwen2.5-VL/Qwen3-VL use a "native resolution" vision transformer: the number of
vision tokens scales with the input image's pixel count, and self-attention memory scales
with the **square** of the token count. USPTO design patent drawings (this project's
`data/IMPACT/*.TIF` images) are high-resolution scans, not typical web photos — feeding
them through `AutoProcessor.from_pretrained(model_name)` with no resolution cap lets the
processor pass the image through at (close to) full resolution, and vision-tower
self-attention can then try to allocate tens of GB for a **single image**.

This is not hypothetical: `shape_discrimination_benchmark/build_shape_discrimination_benchmark.ipynb`
hit `OutOfMemoryError: CUDA out of memory. Tried to allocate 21.36 GiB` on a T4 (14.56 GiB
total) on the very first image of a 20-item smoke test, purely because `min_pixels`/
`max_pixels` were never set. See `research_implementation_log.md` 困難12 for the full
traceback and root-cause writeup.

## The fix: always set min_pixels/max_pixels explicitly

```python
qwen_processor = AutoProcessor.from_pretrained(
    QWEN_MODEL_NAME, min_pixels=256 * 28 * 28, max_pixels=512 * 28 * 28,
)
```

**Use these exact values, don't re-derive new ones.** This is not an arbitrary starting
guess — it's the value already validated in this project's oldest/most-tested Qwen-VL
notebook, `qwen_eval/train_qwen_lora_title_2021_2022_multiview.ipynb` (chosen there because
even the single-view LoRA training run was "事実上不可能なほど遅く・OOMしやすかった"
without a cap), and reused as-is in `shape_discrimination_benchmark/build_shape_discrimination_benchmark.ipynb`
phase 5. Reusing the same constant keeps:
- memory behavior predictable and already-proven across notebooks/GPUs
- what different eval runs actually "see" comparable to each other (a different pixel
  budget changes how much detail the model has access to, which can shift accuracy)

If a future task has a specific reason to need higher fidelity (e.g. reading fine text off
a drawing, which none of this project's tasks do so far — titles/categories are answered
from options, not read off the image), raise the cap deliberately and document why, rather
than defaulting to "no cap" or picking a new number ad hoc.

## Why this is easy to miss

`qwen_eval/eval_qwen_zeroshot_title.ipynb` (the free-text zero-shot title-prediction eval)
does **not** set a pixel cap and still "works" — but only because it happened to run on an
A100-SXM4-80GB, where 80GB of headroom hides the problem. The same code would OOM on a T4.
**Don't treat an uncapped notebook that "worked" as proof the cap is unnecessary** — check
what GPU it actually ran on before copying its processor-loading code as a reference.

## Where this applies

Any `AutoProcessor.from_pretrained(...)` call for a Qwen-VL-family model in this project,
whether for zero-shot inference, LoRA training, or a new eval harness — not just the two
notebooks named above.
