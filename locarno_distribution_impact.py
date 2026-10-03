"""
IMPACTデータセット（2007-2022年）から Locarno 分類（大分類）の分布を集計する。

data/IMPACT/{year}.csv の locarno_class 列を使用する。年によっては
Excelによる日付誤変換で "1月1日" / "Jan-99" のような形式に化けているため、
fix_locarno() で "NN-NN" 形式に復元してから集計する。

Usage:
    python locarno_distribution_impact.py
    python locarno_distribution_impact.py --years 2020 2021 2022
"""

import argparse
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
IMPACT_DIR = BASE_DIR / "data" / "IMPACT"
OUTPUT_CSV = IMPACT_DIR / "locarno_major_distribution.csv"
OUTPUT_PNG = IMPACT_DIR / "locarno_major_distribution.png"
OUTPUT_PNG_BY_YEAR = IMPACT_DIR / "locarno_major_distribution_by_year.png"

ALL_YEARS = list(range(2007, 2023))

MONTH_ABBR = {m: i + 1 for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"])}
_DATE_PAT = re.compile(r"^(\d{1,2})月(\d{1,2})日$")
_DASH_PAT = re.compile(r"^(\d{1,2})-(\d{1,2})$")
_ABBR_PAT = re.compile(r"^([A-Za-z]{3})-(\d{1,2})$")


def fix_locarno(v) -> str | None:
    """Excel日付誤変換された locarno_class を 'NN-NN' 形式に復元する。"""
    if not isinstance(v, str):
        return None
    v = v.strip()
    if m := _DASH_PAT.match(v):
        return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    if m := _DATE_PAT.match(v):
        return f"{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    if (m := _ABBR_PAT.match(v)) and m.group(1) in MONTH_ABBR:
        return f"{MONTH_ABBR[m.group(1)]:02d}-{int(m.group(2)):02d}"
    return None


def major_class(fixed: str) -> str:
    return fixed.split("-")[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", type=int, nargs="+", default=ALL_YEARS)
    args = parser.parse_args()

    total_counter = Counter()
    per_year_counter = {}
    unrecognized = Counter()

    for year in args.years:
        csv_path = IMPACT_DIR / f"{year}.csv"
        if not csv_path.exists():
            print(f"[{year}] スキップ (CSVが見つからない: {csv_path})")
            continue

        df = pd.read_csv(csv_path, dtype=str, usecols=["locarno_class"])
        year_counter = Counter()

        for raw in df["locarno_class"]:
            if pd.isna(raw):
                year_counter["UNKNOWN"] += 1
                continue
            fixed = fix_locarno(raw)
            if fixed is None:
                unrecognized[raw] += 1
                year_counter["UNKNOWN"] += 1
                continue
            year_counter[major_class(fixed)] += 1

        per_year_counter[year] = year_counter
        total_counter.update(year_counter)
        print(f"[{year}] {len(df):,} 件処理")

    if unrecognized:
        print(f"\n復元できなかった値: {len(unrecognized)} 種類 (例: {list(unrecognized)[:5]})")

    def sort_key(item):
        cls, _ = item
        if cls == "UNKNOWN":
            return (10**9, cls)
        return (int(cls), cls)

    sorted_items = sorted(total_counter.items(), key=sort_key)
    classes = [c for c, _ in sorted_items]
    counts = [v for _, v in sorted_items]

    # --- CSV保存 (全年合計 + 年別) ---
    year_cols = sorted(per_year_counter.keys())
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(["locarno_major_class", "total"] + [str(y) for y in year_cols]) + "\n")
        for c, total in sorted_items:
            row = [c, str(total)] + [str(per_year_counter[y].get(c, 0)) for y in year_cols]
            f.write(",".join(row) + "\n")

    # --- 全年合計の棒グラフ ---
    plt.figure(figsize=(10, 5))
    plt.bar(classes, counts)
    plt.xlabel("Locarno Major Class")
    plt.ylabel("Count")
    plt.title(f"Locarno Class Distribution (IMPACT {min(args.years)}-{max(args.years)})")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG)
    plt.close()

    # --- 年別積み上げ棒グラフ ---
    plt.figure(figsize=(12, 6))
    bottom = [0] * len(classes)
    for y in year_cols:
        vals = [per_year_counter[y].get(c, 0) for c in classes]
        plt.bar(classes, vals, bottom=bottom, label=str(y))
        bottom = [b + v for b, v in zip(bottom, vals)]
    plt.xlabel("Locarno Major Class")
    plt.ylabel("Count")
    plt.title(f"Locarno Class Distribution by Year (IMPACT {min(args.years)}-{max(args.years)})")
    plt.xticks(rotation=45)
    plt.legend(ncol=2, fontsize=8)
    plt.tight_layout()
    plt.savefig(OUTPUT_PNG_BY_YEAR)
    plt.close()

    print(f"\nSaved CSV : {OUTPUT_CSV}")
    print(f"Saved PNG : {OUTPUT_PNG}")
    print(f"Saved PNG : {OUTPUT_PNG_BY_YEAR}")


if __name__ == "__main__":
    main()
