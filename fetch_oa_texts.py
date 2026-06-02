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
JSON_OUTPUT_DIR = DATA_DIR / "oa_texts"
PROCESSED_LOG_PATH = DATA_DIR / "fetch_oa_texts_log.txt"
METADATA_CSV = DATA_DIR / "patents_metadata.csv"
MY_API_KEY = os.getenv("MY_API_KEY")

API_URL = "https://api.uspto.gov/api/v1/patent/oa/oa_actions/v1/records"
ROWS_PER_PAGE = 20  # bodyText を含むため小さめに

_EXCLUDE_FIELDS = {"createUserIdentifier", "obsoleteDocumentIdentifier", "createDateTime", "id"}

# CSV に出力するフラットフィールド（sections.* は別途展開）
_FLAT_FIELDS = [
    "patentNumber",
    "patentApplicationNumber",
    "inventionTitle",
    "inventionSubjectMatterCategory",
    "actionTypeCategory",
    "submissionDate",
    "filingDate",
    "grantDate",
    "legalSectionCode",
    "groupArtUnitNumber",
    "techCenter",
    "workGroup",
    "nationalClass",
    "nationalSubclass",
    "hasRej101",
    "hasRej102",
    "hasRej103",
    "hasRej112",
    "hasRejDP",
    "aliceIndicator",
    "bilskiIndicator",
    "myriadIndicator",
    "mayoIndicator",
    "allowedClaimIndicator",
    "cite103Max",
    "closingMissing",
    "headerMissing",
    "accessLevelCategory",
    "sourceSystemName",
    "legacyDocumentCodeIdentifier",
    "legacyCMSIdentifier",
]

# sections.* のうち抽出するテキストフィールド
_SECTION_TEXT_FIELDS = [
    "section101RejectionText",
    "section101RejectionFormParagraphText",
    "section102RejectionText",
    "section102RejectionFormParagraphText",
    "section103RejectionText",
    "section103RejectionFormParagraphText",
    "section112RejectionText",
    "section112RejectionFormParagraphText",
    "summaryText",
    "withdrawalRejectionText",
    "terminalDisclaimerStatusText",
    "detailCitationText",
    "officeActionIdentifier",
    "submissionDate",
    "grantDate",
    "patentApplicationNumber",
    "groupArtUnitNumber",
    "nationalSubclass",
    "workGroupNumber",
    "techCenterNumber",
    "examinerEmployeeNumber",
    "specificationTitleText",
    "filingDate",
]


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
        resp = requests.post(API_URL, headers=headers, data=payload, timeout=60)
        if resp.status_code != 200:
            logger.warning(f"HTTP {resp.status_code} | criteria={criteria!r}")
            resp.raise_for_status()
        return resp.json().get("response", {})
    except requests.exceptions.RequestException as e:
        logger.error(f"通信エラー: {e} | criteria={criteria!r}")
        return None


def fetch_oa_texts(patent_id, api_key, logger):
    """
    patentNumber フィールドでデザイン特許番号を検索し、
    Office Action の全文テキストを取得する。
    ページネーションで全件取得。
    """
    # patentNumber フィールドは "D123456" 形式の付与番号をリストで保持している
    criteria = f"patentNumber:({patent_id})"

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
        time.sleep(0.5)

    return all_docs


def flatten_record(cited_id, rec):
    """1レコードをCSV用にフラット化する。sections はプレフィックス付きで展開。"""
    row = {"cited_patent_id": cited_id}

    for field in _FLAT_FIELDS:
        row[field] = rec.get(field)

    sections_list = rec.get("sections", [])
    # sections が複数ある場合は最初の1件のみ使用（通常は1件）
    sections = sections_list[0] if isinstance(sections_list, list) and sections_list else (
        sections_list if isinstance(sections_list, dict) else {}
    )
    for field in _SECTION_TEXT_FIELDS:
        row[f"sections_{field}"] = sections.get(field)

    return row


def export_csv(all_results, output_dir):
    rows = []
    for cited_id, data in all_results.items():
        for rec in data.get("records", []):
            rows.append(flatten_record(cited_id, rec))
    if not rows:
        print("出力する OA テキストレコードが0件でした。")
        return
    df = pd.DataFrame(rows)
    csv_path = output_dir / "oa_text_records.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"oa_text_records.csv: {len(df):,}件 → {csv_path}")


def process(skip_existing: bool = True):
    logger = setup_logger("fetch_oa_texts")
    JSON_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df_meta = pd.read_csv(METADATA_CSV)
    print(f"patents_metadata.csv から {len(df_meta):,} 件の特許IDを読み込みました。")

    processed_ids = set()
    if PROCESSED_LOG_PATH.exists():
        with open(PROCESSED_LOG_PATH, encoding="utf-8") as f:
            processed_ids = {line.strip() for line in f if line.strip()}
    print(f"処理済み: {len(processed_ids)}件\n")

    json_path = JSON_OUTPUT_DIR / "oa_texts.json"
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

        docs = fetch_oa_texts(target_patent, api_key=MY_API_KEY, logger=logger)
        time.sleep(0.5)

        if docs is None:
            tqdm.write(f"  [ERROR] {target_patent}: 通信エラー。次回再試行します。")
            continue

        if docs:
            all_results[target_patent] = {"oa_actions_found": len(docs), "records": docs}
            tqdm.write(f"  {target_patent}: {len(docs)}件")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)

        processed_ids.add(target_patent)
        with open(PROCESSED_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(target_patent + "\n")

    export_csv(all_results, JSON_OUTPUT_DIR)
    print("\n完了")


def main():
    parser = argparse.ArgumentParser(
        description="USPTO Office Action Text Retrieval fetcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "出力先: data/processed/oa_texts/\n"
            "  oa_texts.json        — 特許IDごとのAPIレスポンス生データ\n"
            "  oa_text_records.csv  — 拒絶理由テキスト等の主要フィールド（sections.* 展開済み）"
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
