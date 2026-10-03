"""
IMPACTデータセット（2007-2022年）の Locarno 大分類分布グラフに、
指定したサブクラス（デフォルト: "14-04", "32-00"）の内訳を積み上げ表示する。

locarno_major_distribution.png と同じ全大分類バーに対して、
対象サブクラスが属する大分類バーだけを「対象サブクラス / それ以外」の
2色積み上げにする（対象サブクラスが0件の大分類は実質単色のまま）。

Usage:
    python locarno_major_with_subclass_breakdown.py
    python locarno_major_with_subclass_breakdown.py --classes 14-04 32-00
"""

import argparse
import re
from collections import Counter
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent
IMPACT_DIR = BASE_DIR / "data" / "IMPACT"

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


def sort_key(item):
    cls, _ = item
    if cls == "UNKNOWN":
        return (10**9, cls)
    return (int(cls), cls)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--classes", type=str, nargs="+", default=["14-04", "32-00"])
    parser.add_argument("--years", type=int, nargs="+", default=ALL_YEARS)
    args = parser.parse_args()

    target_classes = set(args.classes)
    target_majors = {c.split("-")[0] for c in target_classes}
    suffix = "_".join(c.replace("-", "") for c in args.classes)
    output_csv = IMPACT_DIR / f"locarno_major_with_subclass_breakdown_{suffix}.csv"
    output_png = IMPACT_DIR / f"locarno_major_with_subclass_breakdown_{suffix}.png"

    major_total = Counter()
    subclass_total = Counter()

    for year in args.years:
        csv_path = IMPACT_DIR / f"{year}.csv"
        if not csv_path.exists():
            print(f"[{year}] スキップ (CSVが見つからない: {csv_path})")
            continue

        df = pd.read_csv(csv_path, dtype=str, usecols=["locarno_class"])
        for raw in df["locarno_class"]:
            fixed = fix_locarno(raw) if pd.notna(raw) else None
            major = fixed.split("-")[0] if fixed else "UNKNOWN"
            major_total[major] += 1
            if fixed in target_classes:
                subclass_total[fixed] += 1

        print(f"[{year}] {len(df):,} 件処理")

    sorted_items = sorted(major_total.items(), key=sort_key)
    classes = [c for c, _ in sorted_items]

    highlight_vals = []
    other_vals = []
    for c in classes:
        total = major_total[c]
        if c in target_majors:
            hv = sum(subclass_total[sc] for sc in target_classes if sc.split("-")[0] == c)
        else:
            hv = 0
        highlight_vals.append(hv)
        other_vals.append(total - hv)

    # --- CSV保存 ---
    with open(output_csv, "w", encoding="utf-8-sig", newline="") as f:
        f.write("locarno_major_class,total,highlight_subclass_count,other_count\n")
        for c, hv, ov in zip(classes, highlight_vals, other_vals):
            f.write(f"{c},{hv + ov},{hv},{ov}\n")

    # --- 積み上げ棒グラフ ---
    label_highlight = " / ".join(sorted(target_classes))
    plt.figure(figsize=(12, 6))
    plt.bar(classes, highlight_vals, label=label_highlight, color="tab:orange")
    plt.bar(classes, other_vals, bottom=highlight_vals, label="Other", color="tab:blue")
    plt.xlabel("Locarno Major Class")
    plt.ylabel("Count")
    plt.title(f"Locarno Class Distribution with Subclass Breakdown (IMPACT {min(args.years)}-{max(args.years)})")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_png)
    plt.close()

    print(f"\n対象サブクラス合計: {dict(subclass_total)}")
    print(f"Saved CSV : {output_csv}")
    print(f"Saved PNG : {output_png}")


if __name__ == "__main__":
    main()
