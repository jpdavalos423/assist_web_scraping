#!/usr/bin/env python3
"""
Iterate over every *_allUC.csv in results/ and create a single filtered
CSV per CC under filtered_results/.

Usage:  python post_process.py          # no args needed
"""

import os
import csv

from course_reqs import UC_REQUIREMENTS

# ----- UC name → abbreviation mapping -----------------------------
UC_ABBREVIATIONS = {
    "University of California San Diego":      "UCSD",
    "University of California Irvine":         "UCI",
    "University of California Davis":          "UCD",
    "University of California Riverside":      "UCR",
    "University of California Los Angeles":    "UCLA",
    "University of California Berkeley":       "UCB",
    "University of California Merced":         "UCM",
    "University of California Santa Cruz":     "UCSC",
    "University of California Santa Barbara":  "UCSB",
}

# ----- Base directory configuration --------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")
FILTERED_DIR = os.path.join(BASE_DIR, "..", "filtered_results")

# ------------------------------------------------------------------
def match_requirement(uc_abbr: str, receiving_course: str):
    """
    Return a list of (group_id, set_id, num_required) tuples from
    UC_REQUIREMENTS that match the given receiving‑course string.
    """
    matches = []
    reqs = UC_REQUIREMENTS.get(uc_abbr, {})
    for group_id, entries in reqs.items():
        if not isinstance(entries[0], list):
            entries = [entries]  # normalize single entry
        for course_code, set_id, num_required in entries:
            if course_code.lower() in receiving_course.lower():
                matches.append((group_id, set_id, num_required))
    return matches


def process_csv(csv_path):
    """
    Read one *_allUC.csv file and return a list of matched-row dicts.
    """
    matched_rows = []
    total, matched_total = 0, 0

    with open(csv_path, newline='', encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            total += 1
            uc_abbr = UC_ABBREVIATIONS.get(row["UC Campus"].strip())
            if not uc_abbr:
                continue

            receiving = row["UC Course Requirement"].strip()
            if not receiving or receiving == "Not Articulated":
                continue

            matches = match_requirement(uc_abbr, receiving)
            if not matches:
                continue

            matched_total += 1
            or_groups = [
                row[k].strip()
                for k in row
                if k.startswith("Courses Group") and row[k].strip()
            ]

            for group_id, set_id, num_required in matches:
                matched_rows.append(
                    {
                        "UC Name": uc_abbr,
                        "Group ID": group_id,
                        "Set ID": set_id,
                        "Num Required": num_required,
                        "Receiving": receiving,
                        "OR Groups": or_groups,
                    }
                )

    cc = os.path.basename(csv_path).replace("_allUC.csv", "")
    print(f"📄 {cc}: scanned {total:>4} → matched {matched_total:>3}")
    return cc, matched_rows


def save_filtered_csv(cc_name, rows):
    """
    Write filtered_<CC>.csv into filtered_results/.
    """
    if not rows:
        print(f"⚠️  {cc_name}: no matched rows, skipping file.")
        return

    os.makedirs(FILTERED_DIR, exist_ok=True)
    out_path = os.path.join(FILTERED_DIR, f"{cc_name}_filtered.csv")

    max_or = max(len(r["OR Groups"]) for r in rows)
    headers = (
        ["UC Name", "Group ID", "Set ID", "Num Required", "Receiving"]
        + [f"Courses Group {i+1}" for i in range(max_or)]
    )

    with open(out_path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=headers)
        writer.writeheader()

        for r in rows:
            out = {
                "UC Name": r["UC Name"],
                "Group ID": r["Group ID"],
                "Set ID": r["Set ID"],
                "Num Required": r["Num Required"],
                "Receiving": r["Receiving"],
            }
            for i, val in enumerate(r["OR Groups"]):
                out[f"Courses Group {i+1}"] = val
            writer.writerow(out)

    print(f"✅  Saved → {out_path}")


def main():
    if not os.path.isdir(RESULTS_DIR):
        print(f"❌ No 'results/' directory found at expected path: {RESULTS_DIR}")
        return

    csv_files = [
        os.path.join(RESULTS_DIR, f)
        for f in os.listdir(RESULTS_DIR)
        if f.endswith("_allUC.csv")
    ]

    if not csv_files:
        print("❌ No *_allUC.csv files found in 'results/'.")
        return

    for csv_path in csv_files:
        cc_name, rows = process_csv(csv_path)
        save_filtered_csv(cc_name, rows)


if __name__ == "__main__":
    main()
