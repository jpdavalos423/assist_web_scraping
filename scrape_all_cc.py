import os
import json
import csv
import time
import traceback
import scraping  # Importing existing scraping functions

# Directories
AGREEMENTS_DIR = "cc_agreements"
RESULTS_DIR = "results"

# Ensure results directory exists
os.makedirs(RESULTS_DIR, exist_ok=True)


def find_agreement_urls(cc_name):
    """Finds all articulation agreement URLs for a given community college."""
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
    """Scrapes articulation data from a UC agreement page using scraping.py."""
    print(f"🔍 Scraping {uc_name} => {url}")

    for attempt in range(3):  # Retry logic
        try:
            html = scraping.get_dynamic_html(url)  # Uses function from scraping.py
            articulations = scraping.parse_articulations(html)  # Parse with existing function
            return articulations
        except Exception as e:
            print(f"❌ Error scraping {uc_name} (Attempt {attempt+1}/3): {e}")
            traceback.print_exc()
            time.sleep(5)  # Wait before retrying
    
    print(f"❌ Failed to scrape {uc_name} after 3 retries.")
    return None


def process_sending_courses(sending_courses):
    """Formats sending courses into OR-separated groups for CSV."""
    if sending_courses == "Not Articulated":
        return ["Not Articulated"]
    if not sending_courses:
        return ["Not Articulated"]
    
    if isinstance(sending_courses, list) and all(isinstance(x, list) for x in sending_courses):
        return ["; ".join(group) for group in sending_courses]
    elif isinstance(sending_courses, list):
        return ["; ".join(sending_courses)]
    
    return [str(sending_courses)]


def write_csv(cc_name, all_rows):
    """Writes the final CSV file with correctly structured columns."""
    safe_cc_name = cc_name.replace(" ", "_").replace("/", "-")
    csv_path = os.path.join(RESULTS_DIR, f"{safe_cc_name}_allUC.csv")

    # Determine maximum OR groups for CSV columns
    max_or_columns = max(len(row["OR Groups"]) for row in all_rows)

    headers = [
        "UC Campus",
        "CC",
        "Requirement group ID",
        "Set ID",
        "Num required from set",
        "UC Course Requirement"
    ]
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


def main():
    """Main function to scrape and process articulation data for a given CC."""
    cc_name = input("Enter the Community College name (e.g., 'De Anza College'): ").strip()

    uc_urls = find_agreement_urls(cc_name)
    if not uc_urls:
        print("❌ No URLs found!")
        return

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
                "Requirement group ID": "A",
                "Set ID": "A",
                "Num required from set": "1",
                "UC Course Requirement": "; ".join(receiving),
                "OR Groups": process_sending_courses(sending)
            }

            all_rows.append(row_dict)

    # Save JSON (for debugging)
    json_path = os.path.join(RESULTS_DIR, f"{cc_name.replace(' ', '_')}_allUC.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(all_rows, jf, indent=4)
    print(f"✅ JSON saved: {json_path}")

    # Save CSV
    write_csv(cc_name, all_rows)


if __name__ == "__main__":
    main()
