import os
import csv

# Define the expected full set of UC campuses
EXPECTED_UCS = {
    "University of California San Diego",
    "University of California Irvine",
    "University of California Davis",
    "University of California Riverside",
    "University of California Los Angeles",
    "University of California Berkeley",
    "University of California Merced",
    "University of California Santa Cruz",
    "University of California Santa Barbara"
}

RESULTS_DIR = "results"
REPORT_PATH = "missing_uc_agreements_report.txt"

def analyze_results_folder():
    missing_report = {}

    for file in os.listdir(RESULTS_DIR):
        if not file.endswith("_allUC.csv"):
            continue

        cc_name = file.replace("_allUC.csv", "").replace("_", " ")
        file_path = os.path.join(RESULTS_DIR, file)
        found_ucs = set()

        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                uc = row["UC Campus"].strip()
                if uc:
                    found_ucs.add(uc)

        missing_ucs = EXPECTED_UCS - found_ucs
        if missing_ucs:
            missing_report[cc_name] = sorted(missing_ucs)

    return missing_report

def print_and_save_report(missing_report):
    if not missing_report:
        print("✅ All community colleges have articulation data for all UCs!")
        return

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        for cc, missing_ucs in sorted(missing_report.items()):
            line = f"{cc}: Missing {len(missing_ucs)} → {', '.join(missing_ucs)}"
            print(line)
            f.write(line + "\n")

    print(f"\n📄 Report saved to {REPORT_PATH}")

def main():
    report = analyze_results_folder()
    print_and_save_report(report)

if __name__ == "__main__":
    main()
