import os
import sys
import csv
from collections import defaultdict
from course_reqs import UC_REQUIREMENTS

# Full name to abbreviation mapping
UC_ABBREVIATIONS = {
    "University of California San Diego": "UCSD",
    "University of California Irvine": "UCI",
    "University of California Davis": "UCD",
    "University of California Riverside": "UCR",
    "University of California Los Angeles": "UCLA",
    "University of California Berkeley": "UCB",
    "University of California Merced": "UCM",
    "University of California Santa Cruz": "UCSC",
    "University of California Santa Barbara": "UCSB"
}

def match_requirement(uc_abbr, receiving_course):
    matches = []
    reqs = UC_REQUIREMENTS.get(uc_abbr, {})
    for group_id, entries in reqs.items():
        if not isinstance(entries[0], list):
            entries = [entries]
        for course_code, set_id, num_required in entries:
            if course_code.lower() in receiving_course.lower():
                matches.append((group_id, set_id, num_required))
    return matches

def process_csv(input_csv_path):
    all_matched_rows = []
    total = 0
    matched_total = 0

    with open(input_csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            uc_full = row["UC Campus"].strip()
            uc_abbr = UC_ABBREVIATIONS.get(uc_full)
            cc_name = row["CC"].strip()
            receiving = row["UC Course Requirement"].strip()

            if not uc_abbr or not receiving or receiving == "Not Articulated":
                continue

            matches = match_requirement(uc_abbr, receiving)
            if not matches:
                continue

            matched_total += 1

            or_groups = [row[k].strip() for k in row if k.startswith("Courses Group") and row[k].strip()]

            for group_id, set_id, num_required in matches:
                all_matched_rows.append({
                    "UC Name": uc_abbr,
                    "Group ID": group_id,
                    "Set ID": set_id,
                    "Num Required": num_required,
                    "Receiving": receiving,
                    "OR Groups": or_groups,
                    "CC": cc_name
                })

    print(f"🔍 Total rows scanned: {total}")
    print(f"✅ Rows matched to requirements: {matched_total}")
    return all_matched_rows

def save_combined_csv(cc_name, rows):
    if not rows:
        print("⚠️ No matched data to save.")
        return

    folder = os.path.join("post_processed", cc_name.replace(" ", "_"))
    os.makedirs(folder, exist_ok=True)
    output_path = os.path.join(folder, f"{cc_name.replace(' ', '_')}_combined.csv")

    max_or = max(len(row["OR Groups"]) for row in rows)
    headers = ["UC Name", "Group ID", "Set ID", "Num Required", "Receiving"] + \
              [f"Courses Group {i+1}" for i in range(max_or)]

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for row in rows:
            out_row = {
                "UC Name": row["UC Name"],
                "Group ID": row["Group ID"],
                "Set ID": row["Set ID"],
                "Num Required": row["Num Required"],
                "Receiving": row["Receiving"]
            }
            for i, val in enumerate(row["OR Groups"]):
                out_row[f"Courses Group {i+1}"] = val
            writer.writerow(out_row)

    print(f"✅ Combined CSV saved: {output_path}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python post_process_combined.py <path_to_allUC.csv>")
        sys.exit(1)

    input_csv = sys.argv[1].strip()
    cc_name = os.path.basename(input_csv).replace("_allUC.csv", "")

    rows = process_csv(input_csv)
    save_combined_csv(cc_name, rows)

if __name__ == "__main__":
    main()
