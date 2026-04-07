import os
import zipfile
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

RAW_DIR = os.path.join(DATA_DIR, "raw")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)


def is_unzipped(folder_name):
    folder_path = os.path.join(PROCESSED_DIR, folder_name)
    if not os.path.exists(folder_path):
        return False

    for _, _, files in os.walk(folder_path):
        for f in files:
            if f.lower().endswith((".xml", ".tif")):
                return True
    return False


directories = next(os.walk(DATA_DIR))[1]

for dir_name in directories:
    if dir_name in ["raw", "processed"]:
        continue

    src_dir_path = os.path.join(DATA_DIR, dir_name)
    raw_dir_path = os.path.join(RAW_DIR, dir_name)

    if not os.path.exists(raw_dir_path):
        print(f"Move to raw: {dir_name}")
        shutil.move(src_dir_path, raw_dir_path)
    else:
        print(f"Already in raw: {dir_name}")

    design_path = os.path.join(raw_dir_path, dir_name, "DESIGN")
    if not os.path.exists(design_path):
        continue

    print(f"Processing ZIPs in: {dir_name}")

    try:
        zip_files = [f for f in os.listdir(design_path) if f.endswith(".ZIP")]

        for zip_file in zip_files:
            patent_name = os.path.splitext(zip_file)[0]
            zip_path = os.path.join(design_path, zip_file)

            if is_unzipped(patent_name):
                print(f"Skip: {zip_file}")
                continue

            # ここがポイント:
            # 展開先を processed 直下にする
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(PROCESSED_DIR)

            print(f"Unzipped → {os.path.join(PROCESSED_DIR, patent_name)}")

    except Exception as e:
        print(f"Error at {dir_name}: {e}")

print("Done.")