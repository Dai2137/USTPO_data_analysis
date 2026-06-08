"""
Phase 3: 機能文テキストクエリで意匠特許を検索する。

前提: build_embeddings.py を先に実行して FAISS インデックスが存在すること。

実行例:
  python functional_description/search.py "a glove used to protect hands during sports"
  python functional_description/search.py "手を保護するスポーツ用グローブ" --topk 5
  python functional_description/search.py "chair for office use with adjustable height" --alpha 0.7

オプション:
  --topk   : 返す件数（デフォルト 10）
  --alpha  : 画像類似度の重み 0〜1（デフォルト 0.5）
             1.0 = 画像のみ / 0.0 = テキストのみ
"""

import argparse
import csv
import json
import sys
from pathlib import Path

import faiss
import numpy as np
import torch
from transformers import CLIPModel, CLIPProcessor
from sentence_transformers import SentenceTransformer

BASE_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = BASE_DIR / "data" / "processed"
FUNC_DIR = PROCESSED_DIR / "func_search"

CLIP_MODEL_ID = "openai/clip-vit-base-patch32"
ST_MODEL_ID = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"


# ---------- データ読み込み ----------

def load_index():
    img_index = faiss.read_index(str(FUNC_DIR / "faiss_image.index"))
    txt_index = faiss.read_index(str(FUNC_DIR / "faiss_text.index"))
    with open(FUNC_DIR / "index_map.json", encoding="utf-8") as f:
        patent_ids: list[str] = json.load(f)
    return img_index, txt_index, patent_ids


def load_metadata():
    metadata: dict[str, dict] = {}
    with open(PROCESSED_DIR / "patents_metadata.csv", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            metadata[row["patent_id"]] = row

    funcdesc: dict[str, str] = {}
    funcdesc_path = FUNC_DIR / "funcdesc.csv"
    if funcdesc_path.exists():
        with open(funcdesc_path, encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                funcdesc[row["patent_id"]] = row["functional_description"]

    return metadata, funcdesc


# ---------- 埋め込み生成 ----------

def embed_query_clip(query: str, device: str) -> np.ndarray:
    model = CLIPModel.from_pretrained(CLIP_MODEL_ID).to(device)
    proc = CLIPProcessor.from_pretrained(CLIP_MODEL_ID)
    model.eval()
    inputs = proc(text=[query], return_tensors="pt", truncation=True, max_length=77).to(device)
    with torch.no_grad():
        vec = model.get_text_features(**inputs)
    vec = vec.cpu().numpy().astype("float32")
    vec /= np.linalg.norm(vec, axis=1, keepdims=True) + 1e-8
    return vec  # (1, 512)


def embed_query_st(query: str) -> np.ndarray:
    model = SentenceTransformer(ST_MODEL_ID)
    vec = model.encode([query], normalize_embeddings=True).astype("float32")
    return vec  # (1, 768)


# ---------- 検索 ----------

def reciprocal_rank_fusion(
    img_ids: np.ndarray,
    txt_ids: np.ndarray,
    patent_ids: list[str],
    alpha: float,
    top_k: int,
) -> list[tuple[str, float]]:
    """
    Reciprocal Rank Fusion で画像・テキストの順位を統合。
    score = alpha * 1/(1+img_rank) + (1-alpha) * 1/(1+txt_rank)
    """
    n = len(patent_ids)
    img_rank = {patent_ids[idx]: rank for rank, idx in enumerate(img_ids[0])}
    txt_rank = {patent_ids[idx]: rank for rank, idx in enumerate(txt_ids[0])}

    scores = {}
    for pid in patent_ids:
        r_img = img_rank.get(pid, n)
        r_txt = txt_rank.get(pid, n)
        scores[pid] = alpha * (1 / (1 + r_img)) + (1 - alpha) * (1 / (1 + r_txt))

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]


def search(query: str, top_k: int = 10, alpha: float = 0.5) -> list[tuple[str, float]]:
    device = "cuda" if torch.cuda.is_available() else "cpu"

    img_index, txt_index, patent_ids = load_index()
    n = len(patent_ids)

    print(f"Embedding query with CLIP ({device})...")
    clip_vec = embed_query_clip(query, device)

    print("Embedding query with sentence-transformers...")
    st_vec = embed_query_st(query)

    # 全件スコアを取得（rank fusion のため n 件取得）
    _, img_ids = img_index.search(clip_vec, n)
    _, txt_ids = txt_index.search(st_vec, n)

    return reciprocal_rank_fusion(img_ids, txt_ids, patent_ids, alpha, top_k)


# ---------- 結果表示 ----------

def display(results: list[tuple[str, float]], metadata: dict, funcdesc: dict):
    sep = "-" * 72
    print(f"\n{'='*72}")
    print(f"  検索結果 Top {len(results)}")
    print(f"{'='*72}")
    for rank, (pid, score) in enumerate(results, 1):
        row = metadata.get(pid, {})
        fd = funcdesc.get(pid, "(機能文なし)")
        print(f"\n#{rank}  {pid}  score={score:.4f}")
        print(f"  タイトル  : {row.get('title', '')}")
        print(f"  Locarno   : {row.get('locarno_class', '')}")
        print(f"  出願日    : {row.get('application_date', '')}")
        print(f"  機能文    : {fd[:120]}{'...' if len(fd) > 120 else ''}")
        print(sep)


# ---------- メイン ----------

def main():
    parser = argparse.ArgumentParser(description="意匠特許 機能文検索システム")
    parser.add_argument("query", nargs="+", help="検索クエリ（機能文テキスト）")
    parser.add_argument("--topk", type=int, default=10, help="返す件数")
    parser.add_argument(
        "--alpha", type=float, default=0.5,
        help="画像類似度の重み（0=テキストのみ, 1=画像のみ）"
    )
    args = parser.parse_args()

    query = " ".join(args.query)
    print(f"Query  : {query}")
    print(f"Top-K  : {args.topk}")
    print(f"Alpha  : {args.alpha} (image={args.alpha:.0%} / text={1-args.alpha:.0%})")

    if not (FUNC_DIR / "faiss_image.index").exists():
        print("\nERROR: インデックスが見つかりません。先に build_embeddings.py を実行してください。")
        sys.exit(1)

    results = search(query, top_k=args.topk, alpha=args.alpha)
    metadata, funcdesc = load_metadata()
    display(results, metadata, funcdesc)


if __name__ == "__main__":
    main()
