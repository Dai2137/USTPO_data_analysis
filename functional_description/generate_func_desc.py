"""
Phase 1: SmolVLM-500M-Instruct (ローカルVLM, HuggingFace) を使って
意匠特許の機能文を生成する。

モデル: HuggingFaceTB/SmolVLM-500M-Instruct
  - 500M params / ~500MB (fp16) → 2GB VRAM に余裕で収まる
  - transformers 5.x と完全互換
  - API キー不要・完全ローカル

出力: data/processed/func_search/funcdesc.csv
  - patent_id, functional_description

実行例:
  # Locarno大分類で層化サンプリング 1000件
  python functional_description/generate_func_desc.py --sample 1000

  # テスト: 先頭5件だけ
  python functional_description/generate_func_desc.py --sample 5

  # 全件（未処理のみ）
  python functional_description/generate_func_desc.py
"""

import argparse
import csv
import math
import os
import random
from collections import defaultdict
from pathlib import Path

import torch
from PIL import Image
from tqdm import tqdm
from transformers import (
    AutoProcessor,
    SmolVLMForConditionalGeneration,
)

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
OUTPUT_DIR = PROCESSED_DIR / "func_search"
OUTPUT_CSV = OUTPUT_DIR / "funcdesc.csv"
METADATA_CSV = PROCESSED_DIR / "patents_metadata.csv"

MODEL_ID = "HuggingFaceTB/SmolVLM-500M-Instruct"

USER_PROMPT_TEMPLATE = (
    "This is a design patent drawing for '{title}' "
    "(Locarno classification: {locarno}).\n"
    "Look carefully at the specific shapes, contours, and structural features visible in the drawing. "
    "In 2-3 sentences, describe the design intent: "
    "(1) What distinctive visual form or structural feature does this design have? "
    "(2) What functional purpose do those specific shapes serve? "
    "Explain WHY this product is shaped this way — how does its form enable its function."
)


# ---------- サンプリング ----------

def extract_major_class(locarno: str) -> str:
    """'02-01' → '02'"""
    return locarno.strip().split("-")[0].zfill(2) if locarno.strip() else "99"


def stratified_sample(all_rows: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Locarno 大分類で層化サンプリング（比例配分）。"""
    rng = random.Random(seed)

    # 大分類ごとにグループ化
    groups: dict[str, list[dict]] = defaultdict(list)
    for row in all_rows:
        cls = extract_major_class(row["locarno_class"])
        groups[cls].append(row)

    total = len(all_rows)
    sampled: list[dict] = []

    # 比例配分（最低1件/クラス保証）
    quotas: dict[str, int] = {}
    for cls, rows in groups.items():
        quota = max(1, round(len(rows) / total * n))
        quotas[cls] = quota

    # 合計を n に調整（丸め誤差の補正）
    diff = n - sum(quotas.values())
    sorted_cls = sorted(quotas, key=lambda c: len(groups[c]), reverse=True)
    for i in range(abs(diff)):
        cls = sorted_cls[i % len(sorted_cls)]
        quotas[cls] += 1 if diff > 0 else -1
        quotas[cls] = max(1, quotas[cls])

    # クラスごとに無作為抽出
    for cls, rows in groups.items():
        k = min(quotas.get(cls, 1), len(rows))
        sampled.extend(rng.sample(rows, k))

    rng.shuffle(sampled)
    return sampled[:n]


def print_distribution(rows: list[dict], label: str):
    counts: dict[str, int] = defaultdict(int)
    for row in rows:
        counts[extract_major_class(row["locarno_class"])] += 1
    print(f"\n--- {label} (計{len(rows)}件) ---")
    for cls in sorted(counts):
        bar = "#" * min(40, counts[cls])
        print(f"  {cls}: {counts[cls]:4d}  {bar}")


# ---------- モデル ----------

def load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading {MODEL_ID} on {device} (fp16)...")

    processor = AutoProcessor.from_pretrained(MODEL_ID)

    model = SmolVLMForConditionalGeneration.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.float16,
        _attn_implementation="eager",
    ).to(device)
    model.eval()
    print(f"Model ready. Params: {sum(p.numel() for p in model.parameters()) / 1e6:.0f}M")
    return model, processor, device


# ---------- TIF パス解決 ----------

def load_tif_as_rgb(tif_path: Path) -> Image.Image:
    """TIF を RGB に変換し、SmolVLM が扱える最大 512px にリサイズする。"""
    img = Image.open(tif_path).convert("RGB")
    img.load()
    # patch_size=14 の倍数かつ 512px 以内に縮小
    max_size = 448  # 14*32 = 448 (patch_size の倍数で 512 以内の最大値)
    w, h = img.size
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        new_w = max(14, (int(w * scale) // 14) * 14)
        new_h = max(14, (int(h * scale) // 14) * 14)
        img = img.resize((new_w, new_h), Image.LANCZOS)
    return img


def get_representative_tif(row: dict) -> Path | None:
    """D00001（透視図）を優先、なければ D00002, D00003 の順で選ぶ。
    実際のパス: data/processed/{outer}/{inner}/{file}
    """
    outer = row["patent_folder_outer"]
    inner = row["patent_folder_inner"]
    files = [f.strip() for f in row["file_names"].split("|")]
    for priority in ["D00001", "D00002", "D00003"]:
        for f in files:
            if priority in f and f.upper().endswith(".TIF"):
                return PROCESSED_DIR / outer / inner / f
    for f in files:
        if "D00000" not in f and f.upper().endswith(".TIF"):
            return PROCESSED_DIR / outer / inner / f
    return None


# ---------- 推論 ----------

def generate_description(
    model, processor, device, image: Image.Image, title: str, locarno: str
) -> str:
    user_text = USER_PROMPT_TEMPLATE.format(title=title, locarno=locarno)
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image"},
                {"type": "text", "text": user_text},
            ],
        }
    ]
    prompt = processor.tokenizer.apply_chat_template(
        messages, add_generation_prompt=True, tokenize=False
    )
    inputs = processor(text=prompt, images=[image], return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=120,
            do_sample=False,
        )

    input_len = inputs["input_ids"].shape[1]
    generated = output_ids[0][input_len:]
    return processor.tokenizer.decode(generated, skip_special_tokens=True).strip()


# ---------- メイン ----------

def load_done_ids(output_csv: Path) -> set[str]:
    if not output_csv.exists():
        return set()
    with open(output_csv, encoding="utf-8-sig") as f:
        return {row["patent_id"] for row in csv.DictReader(f)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sample", type=int, default=None,
        help="Locarno大分類で層化サンプリングする件数（例: --sample 1000）"
    )
    parser.add_argument("--seed", type=int, default=42, help="乱数シード")
    parser.add_argument(
        "--output", type=Path, default=OUTPUT_CSV,
        help="出力CSVのパス（デフォルト: funcdesc.csv）"
    )
    args = parser.parse_args()

    output_csv: Path = args.output
    output_csv.parent.mkdir(parents=True, exist_ok=True)

    # 全件読み込み
    all_rows: list[dict] = []
    with open(METADATA_CSV, encoding="utf-8-sig") as f:
        all_rows = list(csv.DictReader(f))

    # サンプリング
    if args.sample:
        rows = stratified_sample(all_rows, args.sample, seed=args.seed)
        print_distribution(rows, f"層化サンプル（seed={args.seed}）")
    else:
        rows = all_rows

    # 処理済みをスキップ
    done = load_done_ids(output_csv)
    rows = [r for r in rows if r["patent_id"] not in done]

    if not rows:
        print("All patents already processed.")
        return

    already = args.sample - len(rows) if args.sample else len(done)
    print(f"\n処理対象: {len(rows)}件（スキップ済み: {already}件）")
    if args.sample:
        secs_per = 520  # CPUでの実測値 ~9分
        eta_h = len(rows) * secs_per / 3600
        print(f"推定所要時間（CPU）: {eta_h:.1f}時間 (~{eta_h/24:.1f}日)")
        print("  ヒント: 夜間バックグラウンド実行推奨")

    model, processor, device = load_model()

    write_header = not output_csv.exists() or os.path.getsize(output_csv) == 0

    with open(output_csv, "a", newline="", encoding="utf-8-sig") as out_f:
        writer = csv.writer(out_f)
        if write_header:
            writer.writerow(["patent_id", "functional_description"])

        for row in tqdm(rows, desc="Generating"):
            pid = row["patent_id"]
            tif_path = get_representative_tif(row)

            if tif_path is None or not tif_path.exists():
                writer.writerow([pid, ""])
                out_f.flush()
                continue

            try:
                image = load_tif_as_rgb(tif_path)
                desc = generate_description(
                    model, processor, device, image,
                    title=row["title"],
                    locarno=row["locarno_class"],
                )
                writer.writerow([pid, desc])
                tqdm.write(f"  {pid} [{extract_major_class(row['locarno_class'])}]: {desc[:80]}...")
            except Exception as e:
                tqdm.write(f"[WARN] {pid}: {e}")
                writer.writerow([pid, ""])

            out_f.flush()

    print(f"\nDone. Results saved to {output_csv}")


if __name__ == "__main__":
    main()
