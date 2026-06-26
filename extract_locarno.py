"""
IMPACT XMLファイルから Locarno 分類を抽出し、各年の CSV に locarno_class 列を追加する。

XML内の形式: <main-classification>0101</main-classification>  → "01-01"
出力: data/IMPACT/{year}.csv に locarno_class 列を追加 (in-place)

Usage:
    python extract_locarno.py              # 全年 (2007-2022)
    python extract_locarno.py --year 2022  # 1年のみ
    python extract_locarno.py --dry_run    # 更新せず集計のみ
"""

import argparse
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm

IMPACT_ROOT = Path(__file__).parent / "data" / "IMPACT"
ALL_YEARS   = list(range(2007, 2023))

_LOC_PAT  = re.compile(
    r'<classification-locarno>.*?<main-classification>(\d+)</main-classification>',
    re.DOTALL
)
_ID_PAT   = re.compile(r'USD(\d{7})-')


def fmt_locarno(raw: str) -> str:
    """'0101' → '01-01',  '1401' → '14-01'"""
    raw = raw.zfill(4)
    return f"{raw[:2]}-{raw[2:]}"


def extract_one(xml_path: Path):
    """XMLファイルから (patent_id, locarno_class) を返す。失敗時は None。"""
    m_id = _ID_PAT.search(xml_path.stem)
    if not m_id:
        return None
    patent_id = f"D{m_id.group(1)}"

    try:
        text = xml_path.read_text(encoding='utf-8', errors='ignore')
        m_loc = _LOC_PAT.search(text)
        if m_loc:
            return patent_id, fmt_locarno(m_loc.group(1))
        return patent_id, None
    except Exception:
        return None


def process_year(year: int, dry_run: bool = False) -> dict:
    xml_dir = IMPACT_ROOT / str(year) / str(year)
    csv_path = IMPACT_ROOT / f"{year}.csv"

    if not xml_dir.exists() or not csv_path.exists():
        print(f"[{year}] スキップ (フォルダまたはCSVが見つからない)")
        return {}

    xmls = [p for p in xml_dir.rglob("*.XML") if not p.name.startswith('.')]
    print(f"[{year}] XMLファイル: {len(xmls):,} 件")

    locarno_map = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(extract_one, x): x for x in xmls}
        for fut in tqdm(as_completed(futs), total=len(xmls), desc=f"{year}", leave=False):
            result = fut.result()
            if result and result[1] is not None:
                locarno_map[result[0]] = result[1]

    hit = len(locarno_map)
    print(f"[{year}] Locarno抽出: {hit:,} / {len(xmls):,} 件")

    if dry_run:
        return locarno_map

    # CSV に locarno_class 列を追加
    df = pd.read_csv(csv_path, dtype=str)
    df['locarno_class'] = df['id'].map(locarno_map)
    null_count = df['locarno_class'].isna().sum()
    print(f"[{year}] CSV更新: null={null_count:,} / {len(df):,}")

    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"[{year}] 保存完了 → {csv_path}")
    return locarno_map


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', type=int, default=None)
    parser.add_argument('--dry_run', action='store_true')
    args = parser.parse_args()

    years = [args.year] if args.year else ALL_YEARS

    total_hit = 0
    for yr in years:
        m = process_year(yr, dry_run=args.dry_run)
        total_hit += len(m)

    print(f"\n完了: 合計 {total_hit:,} 件の Locarno 分類を抽出")


if __name__ == '__main__':
    main()
