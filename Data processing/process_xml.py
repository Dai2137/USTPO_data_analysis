import os
import csv
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
PROCESSED_DIR = os.path.join(DATA_DIR, "processed")
OUTPUT_CSV = os.path.join(PROCESSED_DIR, "patents_metadata.csv")

FIELDNAMES = [
    "title",
    "patent_id",
    "publication_date",
    "application_date",
    "claim",
    "locarno_class",
    "us_class",
    "class_search",
    "applicant_org",
    "assignee_org",
    "inventor_names",
    "inventor_countries",
    "applicant_countries",
    "no_figs",
    "sheets",
    "file_names",
    "fig_desc",
    "patent_folder",
]


def get_text(elem):
    if elem is None or elem.text is None:
        return ""
    return elem.text.strip()


def unique_preserve_order(items):
    seen = set()
    result = []
    for x in items:
        if x and x not in seen:
            seen.add(x)
            result.append(x)
    return result


def join_list(items, sep=" | "):
    return sep.join(unique_preserve_order([str(x).strip() for x in items if str(x).strip()]))


def parse_patent_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    biblio = root.find(".//us-bibliographic-data-grant")

    title = get_text(root.find(".//invention-title"))
    patent_id = get_text(root.find(".//publication-reference/document-id/doc-number"))
    publication_date = get_text(root.find(".//publication-reference/document-id/date"))
    application_date = get_text(root.find(".//application-reference/document-id/date"))
    claim = get_text(root.find(".//claims/claim/claim-text"))
    locarno_class = get_text(root.find(".//classification-locarno/main-classification"))

    us_class = ""
    if biblio is not None:
        us_class = get_text(biblio.find("./classification-national/main-classification"))

    class_search_items = []
    class_search_node = root.find(".//us-field-of-classification-search")
    if class_search_node is not None:
        for elem in class_search_node.findall("./classification-national/main-classification"):
            txt = get_text(elem)
            if txt:
                class_search_items.append(txt)
        for elem in class_search_node.findall("./classification-cpc-text"):
            txt = get_text(elem)
            if txt:
                class_search_items.append(txt)
    class_search = join_list(class_search_items)

    applicant_orgs = []
    applicant_countries = []
    for applicant in root.findall(".//us-applicants/us-applicant"):
        applicant_orgs.append(get_text(applicant.find(".//addressbook/orgname")))
        applicant_countries.append(get_text(applicant.find(".//addressbook/address/country")))
        applicant_countries.append(get_text(applicant.find(".//residence/country")))
    applicant_org = join_list(applicant_orgs)
    applicant_countries = join_list(applicant_countries)

    assignee_orgs = []
    for assignee in root.findall(".//assignees/assignee"):
        assignee_orgs.append(get_text(assignee.find(".//addressbook/orgname")))
    assignee_org = join_list(assignee_orgs)

    inventor_names = []
    inventor_countries = []
    for inventor in root.findall(".//inventors/inventor"):
        first_name = get_text(inventor.find(".//addressbook/first-name"))
        last_name = get_text(inventor.find(".//addressbook/last-name"))
        full_name = " ".join([x for x in [first_name, last_name] if x]).strip()
        if full_name:
            inventor_names.append(full_name)
        inventor_countries.append(get_text(inventor.find(".//addressbook/address/country")))
    inventor_names = join_list(inventor_names)
    inventor_countries = join_list(inventor_countries)

    sheets = get_text(root.find(".//figures/number-of-drawing-sheets"))
    no_figs = get_text(root.find(".//figures/number-of-figures"))

    file_names = []
    for img in root.findall(".//drawings/figure/img"):
        file_attr = img.get("file")
        if file_attr:
            file_names.append(file_attr)
    file_names = join_list(file_names)

    fig_desc_list = []
    for p in root.findall(".//description-of-drawings/p"):
        txt = " ".join(t.strip() for t in p.itertext() if t and t.strip())
        if txt:
            fig_desc_list.append(txt)
    fig_desc = join_list(fig_desc_list)

    patent_folder = os.path.basename(os.path.dirname(xml_path))

    return {
        "title": title,
        "patent_id": patent_id,
        "publication_date": publication_date,
        "application_date": application_date,
        "claim": claim,
        "locarno_class": locarno_class,
        "us_class": us_class,
        "class_search": class_search,
        "applicant_org": applicant_org,
        "assignee_org": assignee_org,
        "inventor_names": inventor_names,
        "inventor_countries": inventor_countries,
        "applicant_countries": applicant_countries,
        "no_figs": no_figs,
        "sheets": sheets,
        "file_names": file_names,
        "fig_desc": fig_desc,
        "patent_folder": patent_folder,
    }


def main():
    if not os.path.exists(PROCESSED_DIR):
        raise FileNotFoundError(f"Processed directory not found: {PROCESSED_DIR}")

    xml_files = []

    # processed/USD.../*.xml を対象
    for patent_folder in os.listdir(PROCESSED_DIR):
        patent_path = os.path.join(PROCESSED_DIR, patent_folder)
        if not os.path.isdir(patent_path):
            continue

        for file_name in os.listdir(patent_path):
            if file_name.lower().endswith(".xml"):
                xml_files.append(os.path.join(patent_path, file_name))

    xml_files = sorted(xml_files)

    print(f"Found {len(xml_files)} XML files")

    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)

    success_count = 0
    error_count = 0

    with open(OUTPUT_CSV, mode="w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES)
        writer.writeheader()

        for xml_path in xml_files:
            try:
                row = parse_patent_xml(xml_path)
                writer.writerow(row)
                success_count += 1
            except Exception as e:
                error_count += 1
                print(f"[ERROR] {xml_path}: {e}")

    print(f"Saved to: {OUTPUT_CSV}")
    print(f"Success: {success_count}")
    print(f"Errors : {error_count}")


if __name__ == "__main__":
    main()