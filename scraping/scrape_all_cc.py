import os
import csv
import time
import traceback
import scraping  # Importing existing scraping functions

# Directories
AGREEMENTS_DIR = "cc_agreements"
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def find_agreement_urls(cc_name):
    safe_cc_name = cc_name.replace(" ", "_").replace("/", "-")
    cc_folder = os.path.join(AGREEMENTS_DIR, safe_cc_name)
    agreement_file = os.path.join(cc_folder, "agreements.txt")

    if not os.path.exists(agreement_file):
        print(f"❌ No agreements found for '{cc_name}' at: {agreement_file}")
        return []

    urls = []
    with open(agreement_file, "r", encoding="utf-8") as file:
        for line in file:
            if ":" in line:
                parts = line.split(":", 1)
                uc_name = parts[0].strip()
                url = parts[1].strip()
                if url.startswith("http"):
                    urls.append((uc_name, url))
    return urls

def scrape_uc_data(uc_name, url):
    print(f"🔍 Scraping {uc_name} => {url}")
    for attempt in range(3):
        try:
            html = scraping.get_dynamic_html(url)
            return scraping.parse_articulations(html)
        except Exception as e:
            print(f"❌ Error scraping {uc_name} (Attempt {attempt+1}/3): {e}")
            traceback.print_exc()
            time.sleep(5)
    print(f"❌ Failed to scrape {uc_name} after 3 retries.")
    return None

def process_sending_courses(sending_courses):
    if sending_courses == "Not Articulated" or not sending_courses:
        return ["Not Articulated"]
    if isinstance(sending_courses, list) and all(isinstance(x, list) for x in sending_courses):
        return ["; ".join(group) for group in sending_courses]
    elif isinstance(sending_courses, list):
        return ["; ".join(sending_courses)]
    return [str(sending_courses)]

def write_csv(cc_name, all_rows):
    safe_cc_name = cc_name.replace(" ", "_").replace("/", "-")
    csv_path = os.path.join(RESULTS_DIR, f"{safe_cc_name}_allUC.csv")

    max_or_columns = max(len(row["OR Groups"]) for row in all_rows)

    headers = ["UC Campus", "CC", "UC Course Requirement"]
    for i in range(1, max_or_columns + 1):
        headers.append(f"Courses Group {i}")

    with open(csv_path, "w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        for row in all_rows:
            row_data = dict(row)
            or_groups = row_data.pop("OR Groups")
            for i in range(max_or_columns):
                row_data[f"Courses Group {i+1}"] = or_groups[i] if i < len(or_groups) else ""
            writer.writerow(row_data)

    print(f"✅ CSV saved: {csv_path}")

def process_all_ccs():
    cc_folders = [f for f in os.listdir(AGREEMENTS_DIR) if os.path.isdir(os.path.join(AGREEMENTS_DIR, f))]
    for folder in cc_folders:
        cc_name = folder.replace("_", " ").replace("-", "/")
        print(f"\n📘 Processing: {cc_name}")

        uc_urls = find_agreement_urls(cc_name)
        if not uc_urls:
            print(f"⚠️ Skipping {cc_name} due to missing URLs.")
            continue

        all_rows = []
        for uc_name, url in uc_urls:
            articulations = scrape_uc_data(uc_name, url)
            if not articulations:
                continue

            for record in articulations:
                receiving = record["Receiving Courses"]
                sending = record["Sending Courses"]

                row_dict = {
                    "UC Campus": uc_name,
                    "CC": cc_name,
                    "UC Course Requirement": "; ".join(receiving),
                    "OR Groups": process_sending_courses(sending)
                }

                all_rows.append(row_dict)

        if all_rows:
            write_csv(cc_name, all_rows)
        else:
            print(f"⚠️ No data extracted for {cc_name}.")

def main():
    process_all_ccs()

if __name__ == "__main__":
    main()
