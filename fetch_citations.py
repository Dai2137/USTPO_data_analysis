import argparse
import os
import json
import time
import logging
import requests
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data" / "processed"
JSON_OUTPUT_DIR = DATA_DIR / "citations"
PROCESSED_LOG_PATH = DATA_DIR / "fetch_citations_log.txt"
METADATA_CSV = DATA_DIR / "patents_metadata.csv"
MY_API_KEY = os.getenv("MY_API_KEY")

_EXCLUDE_FIELDS = {"createUserIdentifier", "obsoleteDocumentIdentifier",
                   "qualitySummaryText", "createDateTime", "id"}


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


def normalize_patent_id(raw_id):
    raw_id = str(raw_id).strip()
    if raw_id.startswith('D'):
        return 'D' + str(int(raw_id[1:]))
    elif raw_id.isdigit():
        return str(int(raw_id))
    return raw_id


def fetch_citations(prior_art_number, api_key, logger):
    url = "https://developer.uspto.gov/ds-api/enriched_cited_reference_metadata/v2/records"
    num = prior_art_number.replace("D", "")
    criteria = f'citedDocumentIdentifier:(*D{num}*)'

    payload = {"criteria": criteria, "start": 0, "rows": 50}
    headers = {"Accept": "application/json", "Content-Type": "application/x-www-form-urlencoded"}
    if api_key:
        headers["X-API-KEY"] = api_key

    context = f"patent={prior_art_number}"
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        if response.status_code != 200:
            logger.warning(f"HTTP {response.status_code} | {context}")
            response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"通信エラー: {e} | {context}")
        return None

    docs = response.json().get("response", {}).get("docs", [])
    result = []
    for doc in docs:
        if not doc.get("officeActionDate"):
            continue
        result.append({k: v for k, v in doc.items() if k not in _EXCLUDE_FIELDS})
    return result


def export_pairs(all_results, output_dir):
    rows = []
    for cited_id, data in all_results.items():
        for rec in data.get("records", []):
            pub_num = rec.get("publicationNumber")
            pub_norm = normalize_patent_id(pub_num) if pub_num else None
            rows.append({
                "cited_patent_id": cited_id,
                "citing_publication_number": pub_norm,
                "citing_application_number": rec.get("patentApplicationNumber"),
                "citing_in_dataset": rec.get("citing_in_dataset", False),
                "citation_category_code": rec.get("citationCategoryCode"),
                "office_action_date": rec.get("officeActionDate"),
            })
    if not rows:
        return
    df_pairs = pd.DataFrame(rows)
    pairs_path = output_dir / "citation_pairs.csv"
    df_pairs.to_csv(pairs_path, index=False, encoding="utf-8-sig")
    in_dataset = df_pairs["citing_in_dataset"].sum()
    print(f"📊 citation_pairs.csv: {len(df_pairs)}件 (うちデータセット内ペア: {in_dataset}件) → {pairs_path}")


def process(skip_existing: bool = True):
    logger = setup_logger("fetch_citations")
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_meta = pd.read_csv(METADATA_CSV)
    known_ids = set(df_meta["patent_id"].dropna().apply(normalize_patent_id))
    print(f"🔍 patents_metadata.csv から {len(known_ids):,} 件の特許IDを読み込みました。")

    processed_ids = set()
    if PROCESSED_LOG_PATH.exists():
        with open(PROCESSED_LOG_PATH, encoding="utf-8") as f:
            for line in f:
                processed_ids.add(line.strip())
    print(f"🔄 処理済み: {len(processed_ids)}件\n")

    json_path = JSON_OUTPUT_DIR / "citations.json"
    all_results = {}
    if json_path.exists():
        try:
            with open(json_path, encoding="utf-8") as f:
                all_results = json.load(f)
        except json.JSONDecodeError:
            pass

    for raw_id in tqdm(df_meta["patent_id"].dropna().unique(), desc="特許", unit="件"):
        target_patent = normalize_patent_id(raw_id)

        if skip_existing and target_patent in processed_ids:
            continue

        docs = fetch_citations(target_patent, api_key=MY_API_KEY, logger=logger)
        time.sleep(0.5)

        if docs is None:
            tqdm.write(f"  [ERROR] {target_patent}: 通信エラー。次回再試行します。")
            continue

        if docs:
            for doc in docs:
                pub_num = doc.get("publicationNumber")
                pub_norm = normalize_patent_id(pub_num) if pub_num else None
                doc["citing_in_dataset"] = pub_norm in known_ids if pub_norm else False

            all_results[target_patent] = {
                "citations_found": len(docs),
                "records": docs,
            }
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=2)
            tqdm.write(f"  📄 {target_patent}: {len(docs)}件")

        processed_ids.add(target_patent)
        with open(PROCESSED_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(target_patent + "\n")

    export_pairs(all_results, JSON_OUTPUT_DIR)
    print("\n✅ 完了")


def main():
    parser = argparse.ArgumentParser(description="USPTO citation fetcher")
    parser.add_argument(
        "--no-skip-existing",
        dest="skip_existing",
        action="store_false",
        help="処理済みレコードを上書き再処理する（デフォルト: スキップ）",
    )
    parser.set_defaults(skip_existing=True)
    args = parser.parse_args()
    process(skip_existing=args.skip_existing)


if __name__ == "__main__":
    main()
