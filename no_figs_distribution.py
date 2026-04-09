import csv
import math
import os
from collections import defaultdict

import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "patents_metadata.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "processed")

OUTPUT_ALL_PNG = os.path.join(OUTPUT_DIR, "no_figs_hist_all.png")
OUTPUT_BY_LOCARNO_PNG = os.path.join(OUTPUT_DIR, "no_figs_hist_by_locarno.png")


def extract_major_class(locarno_value: str) -> str:
    """locarno_class から大カテゴリ（先頭2桁）を取り出す。"""
    if not locarno_value:
        return "UNKNOWN"

    value = str(locarno_value).strip()
    if not value:
        return "UNKNOWN"

    for sep in ["-", " ", "/", "_"]:
        if sep in value:
            head = value.split(sep)[0].strip()
            if head.isdigit():
                return head.zfill(2)

    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) >= 2:
        return digits[:2]
    if len(digits) == 1:
        return digits.zfill(2)

    return "UNKNOWN"


def parse_int_safe(value):
    if value is None:
        return None
    s = str(value).strip()
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def sort_locarno_classes(classes):
    def key_func(x):
        if x == "UNKNOWN":
            return (10**9, x)
        return (int(x), x)

    return sorted(classes, key=key_func)


def choose_bins(values):
    """全体と各カテゴリである程度見やすいビン数を自動設定。"""
    if not values:
        return 10

    vmin = min(values)
    vmax = max(values)
    if vmin == vmax:
        return max(1, vmax - vmin + 1)

    # no_figs は整数なので、値域が狭ければ整数幅で刻む
    unique_count = len(set(values))
    if vmax - vmin <= 40 and unique_count <= 40:
        return range(vmin, vmax + 2)

    # それ以外は最大30ビン程度
    return min(30, max(10, int(math.sqrt(len(values)))))


def plot_all_histogram(values, output_path):
    plt.figure(figsize=(10, 6))
    plt.hist(values, bins=choose_bins(values), edgecolor="black")
    plt.xlabel("no_figs")
    plt.ylabel("Frequency")
    plt.title("Distribution of no_figs (All Patents)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_locarno_subplots(no_figs_by_locarno, output_path):
    classes = sort_locarno_classes(no_figs_by_locarno.keys())
    n = len(classes)

    if n == 0:
        raise ValueError("No Locarno classes found.")

    ncols = 4
    nrows = math.ceil(n / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(4.5 * ncols, 3.4 * nrows),
        squeeze=False,
    )

    for ax, cls in zip(axes.flat, classes):
        values = no_figs_by_locarno[cls]
        ax.hist(values, bins=choose_bins(values), edgecolor="black")
        ax.set_title(f"Locarno {cls} (n={len(values)})", fontsize=10)
        ax.set_xlabel("no_figs")
        ax.set_ylabel("Freq")

    # 余った subplot を消す
    for ax in axes.flat[n:]:
        ax.axis("off")

    fig.suptitle("Distribution of no_figs by Locarno Major Class", fontsize=16)
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def main():
    if not os.path.exists(INPUT_CSV):
        raise FileNotFoundError(f"CSV file not found: {INPUT_CSV}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    no_figs_all = []
    no_figs_by_locarno = defaultdict(list)

    total_rows = 0
    valid_no_figs_rows = 0

    with open(INPUT_CSV, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        required_columns = {"locarno_class", "no_figs"}
        missing = required_columns - set(reader.fieldnames or [])
        if missing:
            raise KeyError(f"Missing columns: {', '.join(sorted(missing))}")

        for row in reader:
            total_rows += 1

            no_figs = parse_int_safe(row.get("no_figs"))
            if no_figs is None:
                continue

            locarno_major = extract_major_class(row.get("locarno_class"))

            no_figs_all.append(no_figs)
            no_figs_by_locarno[locarno_major].append(no_figs)
            valid_no_figs_rows += 1

    if not no_figs_all:
        raise ValueError("No valid no_figs values were found.")

    plot_all_histogram(no_figs_all, OUTPUT_ALL_PNG)
    plot_locarno_subplots(no_figs_by_locarno, OUTPUT_BY_LOCARNO_PNG)

    print(f"Total rows            : {total_rows}")
    print(f"Valid no_figs rows    : {valid_no_figs_rows}")
    print(f"Saved                 : {OUTPUT_ALL_PNG}")
    print(f"Saved                 : {OUTPUT_BY_LOCARNO_PNG}")


if __name__ == "__main__":
    main()