"""
Phase 2: CLIP 画像埋め込み + sentence-transformers テキスト埋め込みを生成し、
FAISS インデックスに保存する。

前提: generate_func_desc.py を先に実行して funcdesc.csv が存在すること。

出力: data/processed/func_search/
  - faiss_image.index   ... CLIP 画像ベクトルの FAISS インデックス
  - faiss_text.index    ... 機能文テキストベクトルの FAISS インデックス
  - index_map.json      ... FAISS の行番号 → patent_id の対応表

実行:
  python functional_description/build_embeddings.py
"""

import csv
import json
from pathlib import Path

import faiss
import numpy as np
import torch
from PIL import Image
from tqdm import tqdm
from transformers import CLIPModel, CLIPProcessor
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FUNC_DIR = PROCESSED_DIR / "func_search"

CLIP_MODEL_ID = "openai/clip-vit-base-patch32"   # ~600MB、2GB VRAM に余裕で収まる
ST_MODEL_ID = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"  # 日本語対応


def get_representative_tif(row: dict, processed_dir: Path) -> Path | None:
    outer = row["patent_folder_outer"]
    inner = row["patent_folder_inner"]
    files = [f.strip() for f in row["file_names"].split("|")]
    for priority in ["D00001", "D00002", "D00003"]:
        for f in files:
            if priority in f and f.upper().endswith(".TIF"):
                return processed_dir / outer / inner / f
    for f in files:
        if "D00000" not in f and f.upper().endswith(".TIF"):
            return processed_dir / outer / inner / f
    return None


def load_clip(device: str):
    print(f"Loading CLIP ({CLIP_MODEL_ID})...")
    model = CLIPModel.from_pretrained(CLIP_MODEL_ID).to(device)
    proc = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
    model.eval()
    return model, proc


def load_st():
    print(f"Loading sentence-transformers ({ST_MODEL_ID})...")
    return SentenceTransformer(ST_MODEL_ID)


def embed_image(model, proc, image: Image.Image, device: str) -> np.ndarray:
    inputs = proc(images=image, return_tensors="pt").to(device)
    with torch.no_grad():
        vec = model.get_image_features(**inputs)
    vec = vec.cpu().numpy().astype("float32")
    vec /= np.linalg.norm(vec, axis=1, keepdims=True) + 1e-8
    return vec[0]


def build():
    FUNC_DIR.mkdir(parents=True, exist_ok=True)

    # --- データ読み込み ---
    funcdesc_path = FUNC_DIR / "funcdesc.csv"
    if not funcdesc_path.exists():
        print(f"ERROR: {funcdesc_path} が見つかりません。先に generate_func_desc.py を実行してください。")
        return

    funcdesc: dict[str, str] = {}
    with open(funcdesc_path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["functional_description"].strip():
                funcdesc[row["patent_id"]] = row["functional_description"]

    metadata: dict[str, dict] = {}
    with open(PROCESSED_DIR / "patents_metadata.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if row["patent_id"] in funcdesc:
                metadata[row["patent_id"]] = row

    target_ids = [pid for pid in funcdesc if pid in metadata]
    print(f"Embedding {len(target_ids)} patents...")

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    clip_model, clip_proc = load_clip(device)
    st_model = load_st()

    image_vecs: list[np.ndarray] = []
    text_vecs: list[np.ndarray] = []
    valid_ids: list[str] = []

    # バッチサイズ（テキスト埋め込みはまとめて処理）
    BATCH = 128
    pending_texts: list[str] = []
    pending_ids_for_text: list[str] = []  # image が成功したIDのみ

    for pid in tqdm(target_ids, desc="Image embeddings"):
        row = metadata[pid]
        tif_path = get_representative_tif(row, PROCESSED_DIR)
        if tif_path is None or not tif_path.exists():
            continue
        try:
            img = Image.open(tif_path).convert("RGB")
            img_vec = embed_image(clip_model, clip_proc, img, device)
            image_vecs.append(img_vec)
            pending_ids_for_text.append(pid)
            pending_texts.append(funcdesc[pid])
            valid_ids.append(pid)
        except Exception as e:
            tqdm.write(f"[WARN] {pid}: {e}")

    # テキスト埋め込みをバッチで一括処理
    print(f"Computing {len(pending_texts)} text embeddings...")
    text_vecs_np = st_model.encode(
        pending_texts,
        batch_size=BATCH,
        normalize_embeddings=True,
        show_progress_bar=True,
    ).astype("float32")

    # --- FAISS インデックス構築 ---
    image_matrix = np.stack(image_vecs).astype("float32")  # (N, 512)
    text_matrix = text_vecs_np                              # (N, 768)

    img_dim = image_matrix.shape[1]
    txt_dim = text_matrix.shape[1]

    img_index = faiss.IndexFlatIP(img_dim)  # コサイン類似度（正規化済みベクトルの内積）
    img_index.add(image_matrix)

    txt_index = faiss.IndexFlatIP(txt_dim)
    txt_index.add(text_matrix)

    faiss.write_index(img_index, str(FUNC_DIR / "faiss_image.index"))
    faiss.write_index(txt_index, str(FUNC_DIR / "faiss_text.index"))

    with open(FUNC_DIR / "index_map.json", "w", encoding="utf-8") as f:
        json.dump(valid_ids, f, ensure_ascii=False)

    print(f"\nDone. {len(valid_ids)} patents indexed.")
    print(f"  faiss_image.index : {img_dim}次元, {img_index.ntotal} vectors")
    print(f"  faiss_text.index  : {txt_dim}次元, {txt_index.ntotal} vectors")
    print(f"  index_map.json    : {len(valid_ids)} IDs")


if __name__ == "__main__":
    build()
