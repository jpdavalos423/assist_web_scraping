import os
import requests
from urllib.parse import urlencode

# Adjust these imports to match your actual file/module paths
# (e.g., if AssistAPIInformationGetter.py is in the same directory, do `from AssistAPIInformationGetter import ...`)
from AssistAPIInformationGetter import (
    getAPIData,        # method returning JSON from Assist.org endpoints
    getCCIdList,       # returns all Community College IDs
    getSchoolFromID    # returns the name of an institution, given its ID
)

############################################################
# 1) Dictionary of UC IDs and EXACT 'Computer Science' labels
############################################################
uc_cs_labels = {
    7:   "CSE: Computer Science B.S.",            # UC San Diego
    46:  "Computer Science, B.S.",                # UC Riverside
    79:  "Electrical Engineering & Computer Sciences, B.S.", # UC Berkeley
    89:  "Computer Science B.S.",                 # UC Davis
    117: "Computer Science/B.S.",                 # UCLA
    120: "Computer Science, B.S.",                # UC Irvine
    128: "Computer Science, B.S.",                # UC Santa Barbara
    132: "Computer Science B.S.",                 # UC Santa Cruz
    144: "Computer Science and Engineering, B.S. " # UC Merced
}


############################################################
# 2) Identify all UC IDs (category=1, not CC)
############################################################
def getUCIdList():
    """
    Returns a list of UC institution IDs (category=1, isCommunityCollege=False).
    """
    data = getAPIData("institutions")
    uc_ids = []
    for inst in data:
        if (inst.get("category") == 1) and (not inst.get("isCommunityCollege")):
            uc_ids.append(inst["id"])
    return uc_ids


############################################################
# 3) find_computer_science_key using EXACT matching
############################################################
def find_computer_science_key(cc_id, uc_id, year=75):
    """
    Fetches the major agreements for CC->UC (major category),
    looks for the EXACT label from `uc_cs_labels[uc_id]`,
    and returns the key if found (or None otherwise).
    """
    # 1) If no known label for this UC, skip
    if uc_id not in uc_cs_labels:
        return None
    desired_label = uc_cs_labels[uc_id]

    # 2) Call the agreements endpoint
    base_api = "https://assist.org/api/agreements"
    params = {
        "receivingInstitutionId": uc_id,
        "sendingInstitutionId": cc_id,
        "academicYearId": year,
        "categoryCode": "major"
    }
    resp = requests.get(base_api, params=params)
    data = resp.json()

    # 3) Search for the EXACT label
    for report in data.get("reports", []):
        if report.get("label") == desired_label:
            return report["key"]  # e.g. "75/113/to/117/Major/e15774d6-339f-..."

    return None


############################################################
# 4) Build final articulation URL in correct format
############################################################
def build_articulation_url(year, cc_id, uc_id, key):
    """
    Builds the final articulation URL in the format:
      https://assist.org/transfer/results?year={year}&institution={cc_id}
        &agreement={uc_id}&agreementType=to&view=agreement&viewBy=major
        &viewSendingAgreements=false&viewByKey={key}
    """
    base_url = "https://assist.org/transfer/results"
    params = {
        "year": year,
        "institution": cc_id,
        "agreement": uc_id,
        "agreementType": "to",
        "view": "agreement",
        "viewBy": "major",
        "viewSendingAgreements": "false",
        "viewByKey": key,
    }
    query_str = urlencode(params)
    return f"{base_url}?{query_str}"


############################################################
# 5) Generate & Save All CS URLs for a Single UC
############################################################
def generate_cs_urls_for_uc(uc_id, output_dir="cs_urls", year=75):
    """
    For a given UC, iterates over all Community Colleges (CCs),
    finds the 'Computer Science' major key (if any),
    builds the final articulation URL, and saves it to a file (one line per CC).

    The output file is placed inside output_dir. Each line has:
      CCName [tab] final_url
    """
    os.makedirs(output_dir, exist_ok=True)

    cc_ids = getCCIdList()
    uc_name = getSchoolFromID(uc_id)

    # e.g. "University of California, Los Angeles" => "University_of_California_Los_Angeles"
    uc_name_sanitized = uc_name.replace(" ", "_").replace(",", "")
    output_file = os.path.join(output_dir, f"cs_urls_{uc_name_sanitized}.txt")

    with open(output_file, "w", encoding="utf-8") as f:
        for cc_id in cc_ids:
            cs_key = find_computer_science_key(cc_id, uc_id, year=year)
            if cs_key:
                final_url = build_articulation_url(year, cc_id, uc_id, cs_key)
                cc_name = getSchoolFromID(cc_id)
                f.write(f"{cc_name}\t{final_url}\n")

    print(f"✅ Wrote {uc_name} Computer Science URLs to {output_file}")


############################################################
# 6) Main: Generate for All UCs
############################################################
def main():
    """
    Example usage: build all Computer Science articulation URLs for each UC,
    storing them in 'cs_urls/' (one file per UC).
    """
    # Identify all UC IDs
    uc_ids = getUCIdList()

    for uc_id in uc_ids:
        generate_cs_urls_for_uc(uc_id, output_dir="cs_urls", year=75)  # e.g. 2024-2025

    print("Done generating Computer Science URLs for all UCs!")


if __name__ == "__main__":
    main()
