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
JSON_OUTPUT_DIR = DATA_DIR / "oa_citations"
PROCESSED_LOG_PATH = DATA_DIR / "fetch_oa_citations_log.txt"
METADATA_CSV = DATA_DIR / "patents_metadata.csv"
MY_API_KEY = os.getenv("MY_API_KEY")

_EXCLUDE_FIELDS = {"createUserIdentifier", "obsoleteDocumentIdentifier", "createDateTime", "id"}

API_URL = "https://api.uspto.gov/api/v1/patent/oa/oa_citations/v2/records"
ROWS_PER_PAGE = 100


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logger.addHandler(handler)
    return logger


def normalize_patent_id(raw_id):
    raw_id = str(raw_id).strip()
    if raw_id.startswith("D"):
        return "D" + str(int(raw_id[1:]))
    elif raw_id.isdigit():
        return str(int(raw_id))
    return raw_id


def fetch_page(criteria, start, api_key, logger):
    payload = {"criteria": criteria, "start": start, "rows": ROWS_PER_PAGE}
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    if api_key:
        headers["X-API-KEY"] = api_key

    try:
        resp = requests.post(API_URL, headers=headers, data=payload, timeout=30)
        if resp.status_code != 200:
            logger.warning(f"HTTP {resp.status_code} | criteria={criteria!r}")
            resp.raise_for_status()
        return resp.json().get("response", {})
    except requests.exceptions.RequestException as e:
        logger.error(f"通信エラー: {e} | criteria={criteria!r}")
        return None


def fetch_oa_citations(patent_id, api_key, logger):
    """
    OA Citations API でデザイン特許番号を検索する。
    parsedReferenceIdentifier（数値部）でヒット数を絞り込む。
    ページネーションで全件取得。
    """
    num = patent_id.lstrip("D")
    # parsedReferenceIdentifier はハイフンなし数値文字列
    criteria = f"parsedReferenceIdentifier:({num})"

    all_docs = []
    start = 0
    while True:
        body = fetch_page(criteria, start, api_key, logger)
        if body is None:
            return None

        docs = body.get("docs", [])
        num_found = body.get("numFound", 0)
        all_docs.extend(
            {k: v for k, v in doc.items() if k not in _EXCLUDE_FIELDS}
            for doc in docs
        )
        start += len(docs)
        if start >= num_found or not docs:
            break
        time.sleep(0.3)

    return all_docs


def export_pairs(all_results, output_dir):
    rows = []
    for cited_id, data in all_results.items():
        for rec in data.get("records", []):
            rows.append({
                "cited_patent_id": cited_id,
                "citing_application_number": rec.get("patentApplicationNumber"),
                "reference_identifier": rec.get("referenceIdentifier"),
                "parsed_reference_identifier": rec.get("parsedReferenceIdentifier"),
                "examiner_cited_reference_indicator": rec.get("examinerCitedReferenceIndicator"),
                "applicant_cited_examiner_reference_indicator": rec.get("applicantCitedExaminerReferenceIndicator"),
                "office_action_citation_reference_indicator": rec.get("officeActionCitationReferenceIndicator"),
                "group_art_unit_number": rec.get("groupArtUnitNumber"),
                "tech_center": rec.get("techCenter"),
                "work_group": rec.get("workGroup"),
                "legal_section_code": rec.get("legalSectionCode"),
                "action_type_category": rec.get("actionTypeCategory"),
                "paragraph_number": rec.get("paragraphNumber"),
            })
    if not rows:
        print("出力する引用ペアが0件でした。")
        return
    df_pairs = pd.DataFrame(rows)
    pairs_path = output_dir / "oa_citation_pairs.csv"
    df_pairs.to_csv(pairs_path, index=False, encoding="utf-8-sig")
    print(f"oa_citation_pairs.csv: {len(df_pairs):,}件 → {pairs_path}")


def process(skip_existing: bool = True):
    logger = setup_logger("fetch_oa_citations")
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_meta = pd.read_csv(METADATA_CSV)
    print(f"patents_metadata.csv から {len(df_meta):,} 件の特許IDを読み込みました。")

    processed_ids = set()
    if PROCESSED_LOG_PATH.exists():
        with open(PROCESSED_LOG_PATH, encoding="utf-8") as f:
            processed_ids = {line.strip() for line in f if line.strip()}
    print(f"処理済み: {len(processed_ids)}件\n")

    json_path = JSON_OUTPUT_DIR / "oa_citations.json"
    all_results: dict = {}
    if json_path.exists():
        try:
            with open(json_path, encoding="utf-8") as f:
                all_results = json.load(f)
        except json.JSONDecodeError:
            pass

    patent_ids = [normalize_patent_id(x) for x in df_meta["patent_id"].dropna().unique()]

    for target_patent in tqdm(patent_ids, desc="特許", unit="件"):
        if skip_existing and target_patent in processed_ids:
            continue

        docs = fetch_oa_citations(target_patent, api_key=MY_API_KEY, logger=logger)
        time.sleep(0.5)

        if docs is None:
            tqdm.write(f"  [ERROR] {target_patent}: 通信エラー。次回再試行します。")
            continue

        if docs:
            all_results[target_patent] = {"citations_found": len(docs), "records": docs}
            tqdm.write(f"  {target_patent}: {len(docs)}件")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        processed_ids.add(target_patent)
        with open(PROCESSED_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(target_patent + "\n")

    export_pairs(all_results, JSON_OUTPUT_DIR)
    print("\n完了")


def main():
    parser = argparse.ArgumentParser(
        description="USPTO Office Action Citations fetcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "出力先: data/processed/oa_citations/\n"
            "  oa_citations.json    — 特許IDごとのAPIレスポンス生データ\n"
            "  oa_citation_pairs.csv — 引用ペア形式（citing_application_number 等）"
        ),
    )
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
