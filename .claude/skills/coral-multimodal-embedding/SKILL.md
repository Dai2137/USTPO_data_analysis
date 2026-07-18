---
name: coral-multimodal-embedding
description: Reference for this project's COrAL multimodal embedding architecture on the IMPACT design-patent dataset — encoder choices (DINOv2/ModernBERT vs CLIP), FusionTransformer's CLS-token self-attention fusion, why encoder token-sequence length determines how much the FusionTransformer can actually learn, the CLIP-alignment pitfall (unaligned last_hidden_state vs. projected/aligned space), and how COrAL's shared/unique decomposition differs from DeCUR's. Use this whenever the user asks about COrAL's architecture, adding/swapping an image or text encoder, why a retrieval eval underperforms, CLS tokens, or how COrAL relates to DeCUR/CLIP — even if they don't name the file or say "COrAL" explicitly (e.g. "why does the fusion step not learn anything", "should I use CLIP for the image side").
---

# COrAL multimodal embedding architecture (IMPACT)

Reference for `論文/論文再現実装/COrAL/` (edit only the Drive path — see CLAUDE.md). Read this before changing an encoder, debugging a retrieval eval, or explaining the architecture, so you don't re-derive conclusions already reached (and documented) in this project.

## Why this exists

Two design mistakes already cost real debugging time in this project (see `research_implementation_log.md` 困難3, 困難7). Both came from treating an encoder's output tensor shape as an implementation detail instead of checking what it means for the FusionTransformer downstream. This skill exists so that check happens *before* a training run, not after.

## Architecture at a glance

```
image ──▶ image encoder ──▶ (B, T_img, D) token sequence ──┐
                                                             ├─▶ FusionTransformer (shared path)
text  ──▶ text  encoder ──▶ (B, T_txt, D) token sequence ──┘        │
                                                                     ▼
                                                          prepend learned CLS,
                                                          self-attention over
                                                          [CLS, img tokens, txt tokens],
                                                          take CLS output → MLP → (B, 512)

each modality also feeds a separate "unique" path (zero-mask the other
modality, same FusionTransformer-style module, different weights) → (B, 512) each

loss = 3× InfoNCE (shared, img-unique, txt-unique) + 2× orthogonality
```

Code: `modules/mmfusion.py` (`FusionTransformer_new`, CLS logic at lines ~57-97), `modules/dinov2_encoder.py`, `modules/bert_encoder.py`, `modules/clip_encoder.py` (deprecated raw-token CLIP), `modules/clip_image_encoder.py` / `clip_text_encoder.py` (aligned CLIP), `main_impact.py` (`build_coral`, wires encoders into `MMFusion`).

## The one number that matters: token-sequence length T

Every encoder returns `(B, T, D)`. **T determines whether the FusionTransformer's self-attention can do anything meaningful**, independent of how good the encoder itself is.

| Encoder | Output shape | T | What T represents |
| --- | --- | --- | --- |
| `DINOv2Encoder` (`facebook/dinov2-base`) | (B, 257, 768) | 257 | CLS + 256 image patches (16×16 grid) |
| `BERTTokenEncoder` (ModernBERT) | (B, 128, 768) | 128 | word/subword tokens |
| `CLIPPatchEncoder` (deprecated) | (B, 50, 768) | 50 | CLS + 49 patches, **not** in CLIP's aligned space (see pitfall below) |
| `CLIPImageEncoder` / `clip_aligned` | (B, 1, 768) | 1 | a single pooled, CLIP-aligned vector — all patch structure already collapsed |

With DINOv2+ModernBERT, `FusionTransformer` sees a 257+128+1(CLS) ≈ 386-token sequence: enough for self-attention to learn genuine cross-modal correspondences (e.g. a word attending to the image patches it describes).

With `clip_aligned` on both sides, the sequence collapses to 1+1+1(CLS) = 3 tokens. Self-attention over 2 non-CLS tokens is not meaningfully different from a learned scalar gate:

```
output ≈ α · img_embed + (1-α) · txt_embed
```

**Rule of thumb:** before wiring in any new encoder, check its `seq_len`/output shape. If it returns a single pooled vector, the FusionTransformer step is nearly vestigial for that modality — don't expect self-attention to add expressive power it structurally can't have. This isn't a bug, just a design fact to account for when interpreting results.

## Pitfall: "using CLIP" doesn't mean "using CLIP's alignment"

CLIP's cross-modal alignment (the property that makes zero-shot CLIP retrieval strong) lives **only** in the 512-dim space *after* `visual_projection` / `text_projection`. `CLIPVisionModel(...).last_hidden_state` / `CLIPTextModel(...).last_hidden_state` are pre-projection patch/token features — extracted by CLIP's backbone, but **not aligned** across modalities.

This project hit exactly this bug: `modules/clip_encoder.py` (`CLIPPatchEncoder`) fed `last_hidden_state` into COrAL, so COrAL trained on two unaligned feature spaces and lost badly to CLIP zero-shot (R@1 ratio ≈ 78×, see `weekly_report_20260709.md` §1-3④). The fix, `modules/clip_image_encoder.py` / `clip_text_encoder.py`, explicitly routes through `visual_projection`/`text_projection` before handing COrAL a `(B, 1, 768)` aligned vector — trading token count (see above) for actually using CLIP's pretrained alignment.

If you're asked to add or debug a CLIP-based encoder, check which of these two patterns it follows — this single distinction explains most of the "CLIP loses to zero-shot" surprise in this project's history.

## COrAL vs DeCUR: why COrAL tolerates T=1, DeCUR wouldn't

- **DeCUR** disentangles shared/unique information by **splitting the dimensions of a single embedding vector** (e.g. first half = shared, second half = unique). It has no separate "fusion network" — the split IS the mechanism.
- **COrAL** disentangles by **routing the same input through structurally different networks**: the shared path (`FusionTransformer`, sees both modalities) vs. the unique path (zero-masked FusionTransformer-style module + `AttentionPooling`, sees one modality at a time). The separation is architectural, not a dimension split.

Consequence: COrAL's shared/unique decomposition still "works" (in the sense of being well-defined) even when each modality is a single aligned token — the shared network and the unique network are still different networks. What's lost with T=1 is not the shared/unique separation itself, but the *fine-grained* signal the shared network could otherwise learn from (patch↔word attention). With DeCUR's dimension-split approach, collapsing to a single pooled-and-aligned vector per modality would be a much more fundamental problem, since there's no separate network to fall back on — the disentanglement itself depends on having enough raw dimensions to split.

## Where the fuller writeups live

- `research_implementation_log.md` 困難3 — COrAL's shared-path vs. unique-path inference wiring (zero-masking mechanics)
- `research_implementation_log.md` 困難7 — the CLIP alignment bug above, full before/after code
- `research_implementation_log.md` 研究上の判断 §1 — why COrAL over DeCUR/CLIP for this project's synergy/uniqueness/redundancy goals
- `weekly_reports/weekly_report_20260709.md` §1-3〜1-5 — the quantitative retrieval results that surfaced these issues (CLIP zero-shot vs. COrAL raw/clip/clip_aligned)
- `modules/mmfusion.py` docstring (`FusionTransformer_new`, line 57) — "pooling: cls, concatenation over tokens + self-attention for fusion"

Don't restate these documents' content from memory — re-read the relevant one if a number or code snippet needs to be exact, since implementation details (RUN_TAG naming, exact recall numbers) change as experiments continue.
