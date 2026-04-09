import csv
import os
from collections import Counter
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "patents_metadata.csv")
OUTPUT_CSV = os.path.join(BASE_DIR, "data", "processed", "locarno_major_distribution.csv")
OUTPUT_PNG = os.path.join(BASE_DIR, "data", "processed", "locarno_major_distribution.png")


def extract_major_class(locarno_value: str) -> str:
    if not locarno_value:
        return "UNKNOWN"

    value = locarno_value.strip()

    for sep in ["-", " ", "/", "_"]:
        if sep in value:
            head = value.split(sep)[0].strip()
            if head.isdigit():
                return head.zfill(2)

    digits = "".join(ch for ch in value if ch.isdigit())
    if len(digits) >= 2:
        return digits[:2]

    return "UNKNOWN"


def sort_key(item):
    cls, _ = item
    if cls == "UNKNOWN":
        return (10**9, cls)
    return (int(cls), cls)


def main():
    counter = Counter()

    with open(INPUT_CSV, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            major = extract_major_class(row.get("locarno_class", ""))
            counter[major] += 1

    sorted_items = sorted(counter.items(), key=sort_key)

    classes = [c for c, _ in sorted_items]
    counts = [v for _, v in sorted_items]

    # --- CSV保存 ---
    with open(OUTPUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["locarno_major_class", "count"])
        for c, v in sorted_items:
            writer.writerow([c, v])

    # --- グラフ描画 ---
    plt.figure()
    plt.bar(classes, counts)
    plt.xlabel("Locarno Major Class")
    plt.ylabel("Count")
    plt.title("Locarno Class Distribution")
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(OUTPUT_PNG)
    plt.close()

    print(f"Saved CSV : {OUTPUT_CSV}")
    print(f"Saved PNG : {OUTPUT_PNG}")


if __name__ == "__main__":
    main()