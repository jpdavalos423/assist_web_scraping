import pandas as pd
import os

# List of UC schools
uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

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

def count_required_courses(df, selected_school, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_school = selected_school[0].lower()

    filtered_df = df[df['UC Name'] == selected_school]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, req_group), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        selected_courses = set()
        for set_id, set_df in group_df.groupby('Set ID'):
            num_required = set_df['Num Required'].iloc[0]
            possible_combinations = []
            unmet_requirements = num_required

            for _, row in set_df.iterrows():
                cc_course_options = []
                if pd.notna(row['Courses Group 1']):
                    cc_course_options.append(set(map(str.strip, row['Courses Group 1'].split(";"))))
                for col in row.index[6:]:
                    if pd.notna(row[col]):
                        cc_course_options.append(set(map(str.strip, row[col].split(";"))))

                if cc_course_options:
                    best_option = min(cc_course_options, key=len)
                    possible_combinations.append(best_option)

            possible_combinations.sort(key=len)
            for combination in possible_combinations:
                if unmet_requirements > 0:
                    selected_courses.update(combination)
                    unmet_requirements -= 1

            if unmet_requirements == 0:
                articulated_courses.update(selected_courses)
                break

        if unmet_requirements > 0:
            missing_courses = set_df['Receiving'].dropna().unique()
            for _ in range(unmet_requirements):
                if missing_courses.size > 0:
                    unarticulated_courses.add(missing_courses[0])

    # Calculate only newly added courses
    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated)

def process_combinations_with_roles(df, uc_list, global_counts):
    all_combinations = generate_combinations(uc_list)

    for combo in all_combinations:
        articulated_tracker = set()
        unarticulated_tracker = set()

        for idx, uc in enumerate(combo):
            role = f"{idx+1}st" if idx == 0 else f"{idx+1}nd" if idx == 1 else f"{idx+1}rd"

            art, unart = count_required_courses(
                df, [uc], articulated_tracker, unarticulated_tracker
            )

            global_counts[uc][role][0] += art
            global_counts[uc][role][1] += unart

    return global_counts

def process_folder(folder_path):
    uc_list = uc_schools
    overall_counts = {uc: {'1st': [0, 0], '2nd': [0, 0], '3rd': [0, 0]} for uc in uc_list}
    num_files = 0  # <<< FIXED: Initialize file counter

    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            num_files += 1
            print(f"\n--- Processing {filename} ---")
            df = load_csv(os.path.join(folder_path, filename))

            file_counts = {uc: {'1st': [0, 0], '2nd': [0, 0], '3rd': [0, 0]} for uc in uc_list}
            process_combinations_with_roles(df, uc_list, file_counts)

            for uc in uc_list:
                print(f"\n{uc}:")
                for role in ['1st', '2nd', '3rd']:
                    a, u = file_counts[uc][role]
                    print(f"  As {role}: {a} Courses, {u} Unarticulated")

            for uc in uc_list:
                for role in ['1st', '2nd', '3rd']:
                    overall_counts[uc][role][0] += file_counts[uc][role][0]
                    overall_counts[uc][role][1] += file_counts[uc][role][1]

    # Final totals
    print("\n=== FINAL TOTAL ACROSS ALL FILES ===")
    for uc in uc_list:
        print(f"\n{uc}:")
        for role in ['1st', '2nd', '3rd']:
            a, u = overall_counts[uc][role]
            print(f"  As {role}: {a} Courses, {u} Unarticulated")

    # Averages
    print("\n=== AVERAGE PER FILE ===")
    if num_files > 0:
        for uc in uc_list:
            print(f"\n{uc}:")
            for role in ['1st', '2nd', '3rd']:
                a, u = overall_counts[uc][role]
                avg_a = round(a / num_files, 2)
                avg_u = round(u / num_files, 2)
                print(f"  As {role}: {avg_a} Avg Courses, {avg_u} Avg Unarticulated")
    else:
        print("No CSV files processed.")

import sys
from contextlib import redirect_stdout

if __name__ == "__main__":
    folder_path = input("Enter path to folder with CSV files: ")
    output_file = "total_combination_order.txt"  # You can customize the output filename

    with open(output_file, "w") as f:
        with redirect_stdout(f):
            process_folder(folder_path)

    print(f"\n✅ All output has been saved to '{output_file}'")


    #/workspaces/assist_web_scraping/district_csvs