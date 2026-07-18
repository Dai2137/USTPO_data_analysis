"""
L3 caption discriminability filter for IMPACT design patents.

3条件ANDで判定（ピアなしの特許は条件1+2のみ）:
  C1+C2: [Image D + Caption] D の形状-機能の関係性を記述し、同名意匠と区別できるか
  C3:    [Caption vs Peer]   caption がピア意匠（同ロカルノクラス）には当てはまらないか

判定フロー:
  画像なし                                  → no_image
  C1+C2 = N                                → discard
  C1+C2 = Y + peers あり + C3 全員 Y       → keep   ← ピア全員に当てはまらない
  C1+C2 = Y + peers あり + C3 1件でも N    → discard ← 1件でも当てはまる
  C1+C2 = Y + peers なし (クラス1件のみ)   → keep   ← 22件のみ

VLM: Qwen2.5-VL-7B-Instruct (default).
Requires: pip install transformers qwen-vl-utils

GPU 目安 (batch_size_patents=8, n_peers=10):
  A100 80GB : 約3〜5時間 (2021, 32k件)
  A100 40GB : batch_size_patents=4 推奨
  L4   24GB : batch_size_patents=2 推奨

Usage (Colab)
-------------
!pip install -q transformers qwen-vl-utils

!python filter_l3_captions.py \\
    --year 2021 \\
    --flat_img_dir /content/IMPACT_local/2021_D00001 \\
    --impact_root  /content/drive/MyDrive/.../data/IMPACT \\
    --out_dir      /content/drive/MyDrive/.../data/processed/l3_filter \\
    --n_peers      10 \\
    --batch_size_patents 8
"""

import argparse
import math
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from PIL import Image
from tqdm import tqdm

IMPACT_ROOT = Path(__file__).resolve().parents[1] / "data" / "IMPACT"
OUT_DIR     = Path(__file__).resolve().parents[1] / "data" / "processed" / "l3_filter"
VLM_MODEL   = "Qwen/Qwen2.5-VL-7B-Instruct"


# ---------------------------------------------------------------------------
# Image loading
# ---------------------------------------------------------------------------

def _load_image(flat_img_dir: Path, row: pd.Series, impact_root: Path = None):
    """Try flat dir first, then fall back to IMPACT nested structure."""
    digits = str(row["id"]).lstrip("D")
    date   = str(int(float(row["date"])))
    fname  = f"USD{digits}-{date}-D00001.TIF"

    candidates = [flat_img_dir / fname]
    if impact_root is not None:
        year = date[:4]
        candidates.append(impact_root / year / year / f"USD{digits}-{date}" / fname)

    for path in candidates:
        if path.exists():
            try:
                return Image.open(path).convert("RGB")
            except Exception:
                pass
    return None


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

# Phase 1: C1+C2 — show patent image and ask if caption is shape-function + unique
PROMPT_COND12 = (
    'Caption: "{caption}"\n'
    '\n'
    'Look at the design patent drawing above.\n'
    '\n'
    'Answer "Y" only if BOTH conditions hold:\n'
    '  1. [This drawing] SHAPE-FUNCTION — the caption describes a specific part of this design, '
    'its shape, and how that shape enables a particular function '
    '(e.g. "the tapered leg distributes load evenly"). '
    'NOT a generic category description.\n'
    '  2. [Caption text] UNIQUE PHILOSOPHY — reading the caption alone reveals a design intent '
    'or shape-function relationship that distinguishes this design from others with the same product name.\n'
    '\n'
    'Answer "N" if either condition fails.\n'
    'Answer with only "Y" or "N".'
)

# Phase 2: C3 — show a PEER image and ask if the caption is specific to a DIFFERENT design
# Y = caption does NOT match this peer (discriminative); N = caption matches this peer (generic)
# ALL peers must answer Y to keep  (even one N → discard)
PROMPT_COND3 = (
    'Caption: "{caption}"\n'
    '\n'
    'Look at this design patent drawing.\n'
    '\n'
    'This caption was written for a DIFFERENT design in the same product category.\n'
    'Answer "Y" if this caption does NOT describe this design '
    '(i.e. the caption is specific to some other design).\n'
    'Answer "N" if this caption DOES describe this design.\n'
    'Answer with only "Y" or "N".'
)


# ---------------------------------------------------------------------------
# VLM setup & batched inference
# ---------------------------------------------------------------------------

def load_vlm(model_name: str, max_pixels: int):
    from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor

    print(f"Loading VLM: {model_name}")
    processor = AutoProcessor.from_pretrained(
        model_name,
        min_pixels=256 * 28 * 28,
        max_pixels=max_pixels,
    )
    processor.tokenizer.padding_side = "left"

    try:
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
            attn_implementation="flash_attention_2",
        )
        print("  flash_attention_2: enabled")
    except Exception as e:
        print(f"  flash_attention_2: not available ({e}), using default")
        model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name,
            torch_dtype=torch.bfloat16,
            device_map="auto",
        )
    model.eval()
    return model, processor


def _ask_vlm_batch(model, processor, prompt_template: str,
                   images: list, captions: list) -> list[str]:
    """Batch VLM inference. Returns list of 'Y' or 'N'."""
    from qwen_vl_utils import process_vision_info

    texts, all_image_inputs = [], []
    for img, cap in zip(images, captions):
        messages = [{"role": "user", "content": [
            {"type": "image", "image": img},
            {"type": "text",  "text": prompt_template.format(caption=cap)},
        ]}]
        texts.append(processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True))
        all_image_inputs.extend(process_vision_info(messages)[0])

    inputs = processor(
        text=texts, images=all_image_inputs,
        padding=True, return_tensors="pt",
    ).to(model.device)

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=8)
        trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, generated_ids)]

    results = []
    for decoded in processor.batch_decode(trimmed, skip_special_tokens=True):
        answer = "N"
        for ch in decoded.strip().upper():
            if ch in ("Y", "N"):
                answer = ch
                break
        results.append(answer)
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="L3 caption filter (C1+C2+C3; sole-class patents → C1+C2 only)")
    parser.add_argument("--year",               type=int, required=True)
    parser.add_argument("--flat_img_dir",        type=str, default=None,
                        help="Flat dir of D00001.TIF files.")
    parser.add_argument("--n_peers",             type=int, default=10,
                        help="Number of peer patents for C3 comparison.")
    parser.add_argument("--batch_size_patents",  type=int, default=8,
                        help="Patents per Phase-1 batch. Phase-2 uses same size.")
    parser.add_argument("--max_pixels",          type=int, default=512 * 28 * 28)
    parser.add_argument("--impact_root",         type=str, default=None)
    parser.add_argument("--out_dir",             type=str, default=None)
    parser.add_argument("--model",               type=str, default=VLM_MODEL)
    parser.add_argument("--seed",                type=int, default=42)
    args = parser.parse_args()

    rng          = np.random.default_rng(args.seed)
    impact_root  = Path(args.impact_root) if args.impact_root else IMPACT_ROOT
    flat_img_dir = Path(args.flat_img_dir) if args.flat_img_dir else Path("/dev/null/nonexistent")
    out_dir      = Path(args.out_dir) if args.out_dir else OUT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    out_csv = out_dir / f"l3_labels_{args.year}.csv"

    # ---- load CSV ----
    df = pd.read_csv(
        impact_root / f"{args.year}.csv",
        usecols=["id", "title", "caption", "date", "locarno_class"],
        dtype=str,
    ).dropna(subset=["caption"]).reset_index(drop=True)
    print(f"Loaded {args.year}.csv: {len(df):,} patents with captions")

    # ---- build peer index ----
    cls_to_indices: dict[str, list[int]] = defaultdict(list)
    for i, row in df.iterrows():
        cls = str(row.get("locarno_class", "") or "").strip() or "unknown"
        cls_to_indices[cls].append(i)

    n_classes = len(cls_to_indices)
    n_sole    = sum(1 for v in cls_to_indices.values() if len(v) == 1)
    print(f"Locarno classes: {n_classes}  (sole-class patents: {n_sole} → C1+C2 only)")

    # ---- resume ----
    done_ids: set[str] = set()
    results: list[dict] = []
    if out_csv.exists():
        df_done = pd.read_csv(out_csv, dtype=str)
        done_ids = set(df_done["id"].tolist())
        results  = df_done.to_dict("records")
        print(f"Resuming: {len(done_ids):,} done, {len(df) - len(done_ids):,} remaining")

    # ---- build work queue ----
    # (row_i, caption, title, cls, peer_indices)
    work_queue = []
    for i, row in df.iterrows():
        if row["id"] in done_ids:
            continue
        cls     = str(row.get("locarno_class", "") or "").strip() or "unknown"
        caption = str(row["caption"])
        title   = str(row.get("title", ""))
        pool    = [j for j in cls_to_indices[cls] if j != i]
        if pool:
            peer_indices = rng.choice(
                pool, size=min(args.n_peers, len(pool)), replace=False
            ).tolist()
        else:
            peer_indices = []
        work_queue.append((i, caption, title, cls, peer_indices))

    p2_calls_est = sum(len(pi) for _, _, _, _, pi in work_queue)
    print(f"Work queue: {len(work_queue):,} patents")
    print(f"  Phase-1 calls (C1+C2): {len(work_queue):,}")
    print(f"  Phase-2 calls (C3) est (if all pass C1+C2): {p2_calls_est:,}")

    # ---- load VLM ----
    model, processor = load_vlm(args.model, args.max_pixels)

    # ---- batched loop ----
    BS = args.batch_size_patents
    n_batches = math.ceil(len(work_queue) / BS)
    new_keep = new_discard = new_no_image = new_p1_pass = 0
    pbar = tqdm(range(n_batches), desc=f"L3 filter {args.year}")

    for batch_idx in pbar:
        batch = work_queue[batch_idx * BS: (batch_idx + 1) * BS]

        # ---- Phase 1: C1+C2 ----
        p1_images, p1_captions, p1_slots = [], [], []
        for slot, (row_i, caption, title, cls, peer_indices) in enumerate(batch):
            img = _load_image(flat_img_dir, df.iloc[row_i], impact_root)
            if img is not None:
                p1_images.append(img)
                p1_captions.append(caption)
                p1_slots.append(slot)

        p1_answers: dict[int, str] = {}
        if p1_images:
            for slot, ans in zip(
                    p1_slots,
                    _ask_vlm_batch(model, processor, PROMPT_COND12,
                                   p1_images, p1_captions)):
                p1_answers[slot] = ans
                if ans == "Y":
                    new_p1_pass += 1

        # ---- Phase 2: C3 (only for patents that passed C1+C2 and have peers) ----
        # Collect all (slot, caption, peer_img) tasks for this batch
        p2_tasks: list[tuple[int, str, Image.Image]] = []
        for slot, (row_i, caption, title, cls, peer_indices) in enumerate(batch):
            if p1_answers.get(slot) != "Y" or not peer_indices:
                continue
            for peer_i in peer_indices:
                peer_img = _load_image(flat_img_dir, df.iloc[peer_i], impact_root)
                if peer_img is not None:
                    p2_tasks.append((slot, caption, peer_img))

        # Process Phase-2 tasks in chunks of BS to avoid OOM
        p2_slot_answers: dict[int, list[str]] = defaultdict(list)
        for chunk_start in range(0, len(p2_tasks), BS):
            chunk = p2_tasks[chunk_start: chunk_start + BS]
            chunk_ans = _ask_vlm_batch(
                model, processor, PROMPT_COND3,
                [t[2] for t in chunk],
                [t[1] for t in chunk],
            )
            for (slot, _, _), ans in zip(chunk, chunk_ans):
                p2_slot_answers[slot].append(ans)

        # ---- label assignment ----
        for slot, (row_i, caption, title, cls, peer_indices) in enumerate(batch):
            row    = df.iloc[row_i]
            p1_ans = p1_answers.get(slot)  # None → no_image

            if p1_ans is None:
                label = "no_image"
            elif p1_ans == "N":
                label = "discard"
            else:
                # C1+C2 = Y
                if not peer_indices:
                    # sole-class member: skip C3, keep
                    label = "keep"
                else:
                    peer_ans = p2_slot_answers.get(slot, [])
                    if not peer_ans:
                        # all peer images missing → treat as no peers
                        label = "keep"
                    else:
                        # ALL peers must say Y (caption doesn't match any peer) → keep
                        # even one N (caption matches a peer) → discard
                        label = "keep" if "N" not in peer_ans else "discard"

            results.append({"id": row["id"], "title": title,
                            "locarno_class": cls, "l3_label": label})
            done_ids.add(row["id"])
            if label == "keep":      new_keep += 1
            elif label == "discard": new_discard += 1
            else:                    new_no_image += 1

        if batch_idx % 10 == 0:
            pbar.set_postfix(p1_pass=new_p1_pass, keep=new_keep,
                             discard=new_discard, done=len(results))

        if len(results) % 200 < BS:
            pd.DataFrame(results).to_csv(out_csv, index=False, encoding="utf-8-sig")

    # ---- final save ----
    df_out = pd.DataFrame(results)
    df_out.to_csv(out_csv, index=False, encoding="utf-8-sig")

    n_keep     = (df_out["l3_label"] == "keep").sum()
    n_discard  = (df_out["l3_label"] == "discard").sum()
    n_no_image = (df_out["l3_label"] == "no_image").sum()
    total      = len(df_out)
    print(f"\n=== L3 filter {args.year} (total) ===")
    print(f"  keep     (L3) : {n_keep:>6,}  ({n_keep/total*100:.1f}%)")
    print(f"  discard  (L2) : {n_discard:>6,}  ({n_discard/total*100:.1f}%)")
    print(f"  no_image      : {n_no_image:>6,}  ({n_no_image/total*100:.1f}%)")
    print(f"  total         : {total:>6,}")
    session_new = new_keep + new_discard + new_no_image
    if session_new > 0:
        c3_filtered = new_p1_pass - new_keep
        print(f"\n  [this session: {session_new:,} patents]")
        print(f"  Phase-1 pass (C1+C2=Y) : {new_p1_pass:>6,}  ({new_p1_pass/session_new*100:.1f}%)")
        print(f"  keep     (L3)          : {new_keep:>6,}  ({new_keep/session_new*100:.1f}%)")
        print(f"  C3 filtered            : {c3_filtered:>6,}  "
              f"({c3_filtered/max(new_p1_pass,1)*100:.1f}% of Phase-1 passes)")
    print(f"Saved → {out_csv}")


if __name__ == "__main__":
    main()
