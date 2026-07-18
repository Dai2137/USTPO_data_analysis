"""
L3 caption filter (filter_l3_captions.py) の結果を検証するためのローカル分析ツール。

l3_labels_{year}.csv (id, title, locarno_class, l3_label) と
data/IMPACT/{year}.csv (caption, date を含む) を結合し、

  1. examples: 同じロカルノクラス内で keep/discard された caption を並べて表示
     → フィルタが「意味のある基準」で分けているかを目視確認する
  2. plot:     ロカルノクラスごとの件数分布を フィルタ前 (total) / フィルタ後 (keep) で
     棒グラフ比較 → どのクラスが根こそぎ落とされているか可視化する

Usage
-----
# keep率が極端に高い/低いクラスを自動選択して例を表示 (デフォルト各3クラス)
python analyze_l3_filter.py examples

# クラスを指定
python analyze_l3_filter.py examples --locarno_class 14-04 08-08 --n 8

# 2021のみ、分布グラフ
python analyze_l3_filter.py plot --year 2021

# l3_labels_2022.csv がまだ Drive に同期されていない場合は自動でスキップされる
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    plt.rcParams["font.family"] = "Yu Gothic"
    plt.rcParams["axes.unicode_minus"] = False

BASE_DIR          = Path(__file__).resolve().parents[1]
IMPACT_ROOT_DEFAULT = BASE_DIR / "data" / "IMPACT"
L3_DIR_DEFAULT      = Path(r"G:\マイドライブ\松尾研究室\LLMATCH\USPTO_data_analysis\data\processed\l3_filter")
OUT_DIR_DEFAULT     = BASE_DIR / "data" / "processed" / "l3_filter_analysis"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_year(year: int, l3_dir: Path, impact_root: Path):
    label_csv = l3_dir / f"l3_labels_{year}.csv"
    if not label_csv.exists():
        print(f"[skip] {label_csv} が見つかりません（未処理 or 未同期）")
        return None

    labels = pd.read_csv(label_csv, dtype=str)
    meta = pd.read_csv(
        impact_root / f"{year}.csv",
        usecols=["id", "caption", "date"],
        dtype=str,
    )
    df = labels.merge(meta, on="id", how="left")
    df["year"] = str(year)
    return df


def load_years(years, l3_dir: Path, impact_root: Path) -> pd.DataFrame:
    dfs = [d for d in (load_year(y, l3_dir, impact_root) for y in years) if d is not None]
    if not dfs:
        raise SystemExit("読み込める l3_labels_*.csv がありません。--l3_dir を確認してください。")
    return pd.concat(dfs, ignore_index=True)


def extract_major_class(cls) -> str:
    if cls is None or pd.isna(cls):
        return "unknown"
    s = str(cls).strip()
    if "-" in s:
        head = s.split("-")[0]
        if head.isdigit():
            return head.zfill(2)
    digits = "".join(ch for ch in s if ch.isdigit())
    return digits[:2] if len(digits) >= 2 else "unknown"


def find_image_path(row: pd.Series, impact_root: Path):
    try:
        digits = str(row["id"]).lstrip("D")
        date = str(int(float(row["date"])))
    except (ValueError, TypeError):
        return None
    year = date[:4]
    fname = f"USD{digits}-{date}-D00001.TIF"
    candidates = [
        impact_root / f"{year}_D00001" / fname,
        impact_root / year / year / f"USD{digits}-{date}" / fname,
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


# ---------------------------------------------------------------------------
# examples
# ---------------------------------------------------------------------------

def keep_rate_table(df: pd.DataFrame, min_size: int) -> pd.DataFrame:
    grp = df.groupby("locarno_class")["l3_label"].agg(
        total="count", keep=lambda x: (x == "keep").sum()
    )
    grp = grp[grp["total"] >= min_size]
    grp["keep_rate"] = grp["keep"] / grp["total"]
    return grp


def pick_auto_classes(grp: pd.DataFrame, k: int) -> tuple[list[str], list[str]]:
    top = grp.nlargest(k, "keep_rate").index.tolist()
    bot = grp.nsmallest(k, "keep_rate").index.tolist()
    return top, bot


def cmd_examples(args):
    df = load_years(args.year, args.l3_dir, args.impact_root)

    classes = args.locarno_class
    lines: list[str] = []
    records: list[dict] = []

    def emit(text: str = ""):
        print(text)
        lines.append(text)

    if not classes:
        grp = keep_rate_table(df, args.min_class_size)
        top, bot = pick_auto_classes(grp, args.auto_k)

        emit(f"ロカルノクラス別 keep率 トップ{args.auto_k} (クラスサイズ>={args.min_class_size}):")
        emit(grp.loc[top, ["total", "keep", "keep_rate"]].to_string())
        emit(f"\nロカルノクラス別 keep率 ワースト{args.auto_k} (クラスサイズ>={args.min_class_size}):")
        emit(grp.loc[bot, ["total", "keep", "keep_rate"]].to_string())

        classes = list(dict.fromkeys(top + bot))  # dedupe, preserve order

    for cls in classes:
        sub = df[df["locarno_class"] == cls]
        if sub.empty:
            emit(f"\n=== {cls}: データなし ===")
            continue

        total = len(sub)
        keep_n = (sub["l3_label"] == "keep").sum()
        emit(f"\n{'=' * 78}")
        emit(f"ロカルノクラス {cls}   total={total}  keep={keep_n}  keep_rate={keep_n / total * 100:.1f}%")
        emit("=" * 78)

        for label, jp in [("keep", "KEEP（識別可能と判定）"), ("discard", "DISCARD（汎用的と判定）")]:
            pool = sub[sub["l3_label"] == label]
            rows = pool.sample(n=min(args.n, len(pool)), random_state=args.seed) if len(pool) else pool
            emit(f"\n--- {jp}  {len(rows)}/{len(pool)}件 ---")
            for _, row in rows.iterrows():
                img = find_image_path(row, args.impact_root)
                caption = row.get("caption", "(なし)")
                emit(f"[{row['id']}] ({row['year']}) {row.get('title', '')}")
                emit(f"  caption: {caption}")
                if img:
                    emit(f"  image  : {img}")
                records.append({
                    "locarno_class": cls, "l3_label": label, "id": row["id"],
                    "year": row["year"], "title": row.get("title", ""),
                    "caption": caption, "image_path": str(img) if img else "",
                })

    if not args.no_save:
        args.out_dir.mkdir(parents=True, exist_ok=True)
        tag = "auto" if not args.locarno_class else "_".join(args.locarno_class)
        years_tag = "-".join(str(y) for y in args.year)
        stem = f"examples_{years_tag}_{tag}"

        txt_path = args.out_dir / f"{stem}.txt"
        txt_path.write_text("\n".join(lines), encoding="utf-8")

        csv_path = args.out_dir / f"{stem}.csv"
        pd.DataFrame(records).to_csv(csv_path, index=False, encoding="utf-8-sig")

        print(f"\nSaved: {txt_path}")
        print(f"Saved: {csv_path}")


# ---------------------------------------------------------------------------
# plot
# ---------------------------------------------------------------------------

def plot_grouped_bar(grp: pd.DataFrame, xlabel: str, title: str, out_path: Path):
    x = np.arange(len(grp))
    width = 0.4
    fig, ax = plt.subplots(figsize=(max(8, len(grp) * 0.35), 5))
    ax.bar(x - width / 2, grp["before"], width, label="フィルタ前 (全件)")
    ax.bar(x + width / 2, grp["after"], width, label="フィルタ後 (keep)")
    ax.set_xticks(x)
    ax.set_xticklabels(grp.index, rotation=45, ha="right")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("件数")
    ax.set_title(title)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"Saved: {out_path}")


def plot_for_group(sub: pd.DataFrame, tag: str, out_dir: Path, top_n: int):
    # 大分類（2桁）: 全クラスをクラス番号順に表示
    grp_major = sub.groupby("major_class")["l3_label"].agg(
        before="count", after=lambda x: (x == "keep").sum()
    )
    grp_major = grp_major.reindex(
        sorted(grp_major.index, key=lambda c: (c == "unknown", c))
    )
    plot_grouped_bar(
        grp_major, "Locarno 大分類",
        f"ロカルノ大分類別 件数 フィルタ前後 — {tag}",
        out_dir / f"l3_major_before_after_{tag}.png",
    )

    # 細分類: 件数上位 top_n のみ（全クラス表示すると読めないため）
    grp_sub = sub.groupby("locarno_class")["l3_label"].agg(
        before="count", after=lambda x: (x == "keep").sum()
    ).sort_values("before", ascending=False).head(top_n)
    plot_grouped_bar(
        grp_sub, "Locarno 細分類",
        f"ロカルノ細分類別 件数上位{top_n} フィルタ前後 — {tag}",
        out_dir / f"l3_sub_top{top_n}_before_after_{tag}.png",
    )


def cmd_plot(args):
    df = load_years(args.year, args.l3_dir, args.impact_root)
    df["major_class"] = df["locarno_class"].apply(extract_major_class)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    for year in sorted(df["year"].unique()):
        plot_for_group(df[df["year"] == year], year, args.out_dir, args.top_n)

    if df["year"].nunique() > 1:
        plot_for_group(df, "all", args.out_dir, args.top_n)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_argparser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--year", type=int, nargs="+", default=[2021, 2022])
    common.add_argument("--l3_dir", type=Path, default=L3_DIR_DEFAULT)
    common.add_argument("--impact_root", type=Path, default=IMPACT_ROOT_DEFAULT)

    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    p_ex = sub.add_parser("examples", parents=[common],
                           help="keep/discard の caption をロカルノクラスごとに並べて表示")
    p_ex.add_argument("--locarno_class", nargs="+", default=None,
                       help="表示するクラス（例: 14-04 08-08）。未指定なら keep率 上位/下位を自動選択")
    p_ex.add_argument("--n", type=int, default=5, help="keep/discard それぞれの表示件数")
    p_ex.add_argument("--min_class_size", type=int, default=100,
                       help="自動選択時、このサイズ未満のクラスは対象外")
    p_ex.add_argument("--auto_k", type=int, default=5, help="自動選択時、上位/下位それぞれ何クラス選ぶか")
    p_ex.add_argument("--seed", type=int, default=42)
    p_ex.add_argument("--out_dir", type=Path, default=OUT_DIR_DEFAULT, help="出力(.txt/.csv)の保存先")
    p_ex.add_argument("--no_save", action="store_true", help="ファイル保存せず標準出力のみ")
    p_ex.set_defaults(func=cmd_examples)

    p_pl = sub.add_parser("plot", parents=[common],
                           help="ロカルノクラス別の分布をフィルタ前後で棒グラフ保存")
    p_pl.add_argument("--top_n", type=int, default=25, help="細分類グラフで表示する上位クラス数")
    p_pl.add_argument("--out_dir", type=Path, default=OUT_DIR_DEFAULT)
    p_pl.set_defaults(func=cmd_plot)

    return p


def main():
    args = build_argparser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
