# このコードは、data フォルダの中にある .tar を全部見つけて、
# それぞれ同名のフォルダに展開する スクリプトです。

import os
import tarfile

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

tar_files = [
    f for f in os.listdir(DATA_DIR)
    if f.endswith(".tar")
]

for tar_file in tar_files:
    tar_file_path = os.path.join(DATA_DIR, tar_file)
    extract_dir = os.path.splitext(tar_file_path)[0]

    if os.path.exists(extract_dir) and os.listdir(extract_dir):
        print(f"Skip: {tar_file}")
        continue

    os.makedirs(extract_dir, exist_ok=True)

    with tarfile.open(tar_file_path) as tar:
        tar.extractall(path=extract_dir)

    print(f"Extracted: {tar_file}")

print("Extraction is complete.")