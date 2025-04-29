import os
import pandas as pd
from itertools import combinations

# List of UC schools
uc_schools = ["UCSD", "UCSB", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM", "UCSC"]

def load_csv(file_path):
    return pd.read_csv(file_path)

def generate_combinations(uc_schools):
    combinations = []
    for i in range(len(uc_schools)):
        for j in range(len(uc_schools)):
            if j == i:
                continue
            for k in range(len(uc_schools)):
                if k == i or k == j:
                    continue
                combinations.append((uc_schools[i], uc_schools[j], uc_schools[k]))
    return combinations

def count_required_courses(df, selected_schools, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_schools = [school.strip().lower() for school in selected_schools]
    filtered_df = df[df['UC Name'].isin(selected_schools)]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, req_group), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        best_set_articulated = set()
        best_set_unarticulated = set()
        min_unmet = float('inf')

        for set_id, set_df in group_df.groupby('Set ID'):
            num_required = set_df['Num Required'].iloc[0]
            possible_combinations = []
            unmet = num_required
            temp_selected = set()
            temp_unarticulated = set()

            for _, row in set_df.iterrows():
                cc_course_options = []
                if pd.notna(row['Courses Group 1']):
                    options = [opt.strip() for opt in row['Courses Group 1'].split(";") if opt.strip() and opt.strip().lower() != "not articulated"]
                    if options:
                        cc_course_options.append(set(options))

                for col in row.index[6:]:
                    if pd.notna(row[col]):
                        options = [opt.strip() for opt in row[col].split(";") if opt.strip() and opt.strip().lower() != "not articulated"]
                        if options:
                            cc_course_options.append(set(options))

                if cc_course_options:
                    best_option = min(cc_course_options, key=len)
                    possible_combinations.append(best_option)

            possible_combinations.sort(key=len)
            for combination in possible_combinations:
                if unmet > 0:
                    temp_selected.update(combination)
                    unmet -= 1

            if unmet > 0:
                missing_courses = set_df['Receiving'].dropna().unique()
                for _ in range(unmet):
                    if missing_courses.size > 0:
                        temp_unarticulated.add(missing_courses[0])

            # Save the best (lowest unmet) set
            if len(temp_unarticulated) < min_unmet:
                min_unmet = len(temp_unarticulated)
                best_set_articulated = temp_selected
                best_set_unarticulated = temp_unarticulated

        articulated_courses.update(best_set_articulated)
        unarticulated_courses.update(best_set_unarticulated)

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated)


def process_file(file_path, uc_list, grand_totals):
    print(f"\nProcessing file: {os.path.basename(file_path)}")
    df = load_csv(file_path)
    all_combinations = generate_combinations(uc_list)

    uc_totals = {uc: {'articulated': 0, 'unarticulated': 0} for uc in uc_list}

    for uc_combination in all_combinations:
        articulated_tracker = set()
        unarticulated_tracker = set()

        for uc in uc_combination:
            art, unart = count_required_courses(df, [uc], articulated_tracker, unarticulated_tracker)
            uc_totals[uc]['articulated'] += art
            uc_totals[uc]['unarticulated'] += unart

    print("\nTotal for each UC")
    for uc in uc_list:
        art = uc_totals[uc]['articulated']
        unart = uc_totals[uc]['unarticulated']
        print(f"{uc}: {art} Courses and {unart} Unarticulated Courses")
        grand_totals[uc]['articulated'] += art
        grand_totals[uc]['unarticulated'] += unart

def process_folder(folder_path):
    uc_list = ["UCSD", "UCSB", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM", "UCSC"]
    grand_totals = {uc: {'articulated': 0, 'unarticulated': 0} for uc in uc_list}

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(folder_path, filename)
            process_file(file_path, uc_list, grand_totals)

    print("\n========== Grand Totals Across All Files ==========")
    for uc in uc_list:
        art = grand_totals[uc]['articulated']
        unart = grand_totals[uc]['unarticulated']
        print(f"{uc}: {art} Courses and {unart} Unarticulated Courses")

import sys
from contextlib import redirect_stdout

if __name__ == "__main__":
    folder_path = input("Enter path to folder with CSV files: ")
    output_file = "uc_combinations_totals.txt"  # You can customize the file name
    with open(output_file, "w") as f:
        with redirect_stdout(f):
            process_folder(folder_path)

    print(f"\n✅ All output has been saved to '{output_file}'")




#path: /Users/yasminkabir/assist_web_scraping-1/filtered_results