import xml.etree.ElementTree as ET
import glob
import os
import csv

# =========================
# パス設定
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "..", "data", "Sample data")
OUTPUT_CSV = os.path.join(BASE_DIR, "..", "data", "Sample data", "sample_data.csv")

os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

# =========================
# XML取得
# =========================
xml_files = glob.glob(os.path.join(INPUT_DIR, "**", "*.XML"), recursive=True)

print(f"Found {len(xml_files)} XML files")

# =========================
# CSV書き込み
# =========================
with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csv_file:

    fieldnames = [
        'title', 'id', 'claim', 'date',
        'class', 'class_search', 'inv_country',
        'no_figs', 'sheets', 'file_names', 'fig_desc'
    ]

    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for file in xml_files:
        try:
            tree = ET.parse(file)
            root = tree.getroot()

            def get_text(elem):
                return elem.text if elem is not None else ""

            patent_title = get_text(root.find('.//invention-title'))
            patent_id = get_text(root.find('.//doc-number'))
            claim = get_text(root.find('.//claim-text'))
            date = get_text(root.find('.//date'))

            class_USPC = get_text(root.find('.//classification-national/main-classification'))
            class_USPC_fur = root.find('.//classification-national/further-classification')

            search = root.findall('.//main-classification')
            search_list = [elem.text for elem in search if elem is not None]

            sheets = get_text(root.find('.//number-of-drawing-sheets'))
            no_figs = get_text(root.find('.//number-of-figures'))

            countries = ','.join([
                c.find('.//country').text
                for c in root.findall('.//inventor')
                if c.find('.//country') is not None
            ])

            file_names = [
                img.get('file')
                for img in root.findall('.//img')
                if img.get('file') is not None
            ]

            # 図説明
            fig_list = []
            max_figs = int(no_figs) if no_figs.isdigit() else 0

            for i, p in enumerate(root.iter('p')):
                if i >= max_figs:
                    break
                texts = list(p.itertext())
                fig_list.append(' '.join(t.strip() for t in texts))

            writer.writerow({
                'title': patent_title,
                'id': patent_id,
                'claim': claim,
                'date': date,
                'class': class_USPC + ',' + class_USPC_fur.text if class_USPC_fur is not None else class_USPC,
                'class_search': search_list,
                'inv_country': countries,
                'no_figs': no_figs,
                'sheets': sheets,
                'file_names': file_names,
                'fig_desc': fig_list
            })

        except Exception as e:
            print(f"[ERROR] {file}: {e}")

print(f"Saved to: {OUTPUT_CSV}")