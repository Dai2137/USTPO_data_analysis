import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

def is_processed(path):
    """処理済み判定（DESIGNだけ残っている状態）"""
    sub_dirs = next(os.walk(path))[1]
    return sub_dirs == ["DESIGN"] or sub_dirs == []


directories = next(os.walk(DATA_DIR))[1]

for dir_name in directories:
    dir_path = os.path.join(DATA_DIR, dir_name)

    # .tarと同名フォルダだけ対象にする
    if not os.path.isdir(dir_path):
        continue

    # スキップ判定
    if is_processed(dir_path):
        print(f"Skip (already organized): {dir_name}")
        continue

    print(f"Processing: {dir_name}")

    try:
        # -----------------------------
        # ① SUPP削除
        # -----------------------------
        sub_dirs = next(os.walk(dir_path))[1]
        for sub_dir in sub_dirs:
            if sub_dir.endswith("SUPP"):
                full_path = os.path.join(dir_path, sub_dir)
                shutil.rmtree(full_path)
                print(f"Deleted SUPP: {full_path}")

        # -----------------------------
        # ② DESIGN以外削除
        # -----------------------------
        sub_dirs = next(os.walk(dir_path))[1]

        for sub_dir in sub_dirs:
            sub_dir_path = os.path.join(dir_path, sub_dir)

            # 例: I20260106/I20260106/
            if not os.path.isdir(sub_dir_path):
                continue

            sub_sub_dirs = next(os.walk(sub_dir_path))[1]

            for sub_sub_dir in sub_sub_dirs:
                sub_sub_dir_path = os.path.join(sub_dir_path, sub_sub_dir)

                if sub_sub_dir.upper() != "DESIGN":
                    shutil.rmtree(sub_sub_dir_path)
                    print(f"Deleted: {sub_sub_dir_path}")

    except Exception as e:
        print(f"Error at {dir_name}: {e}")

print("Done.")