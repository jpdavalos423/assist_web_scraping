import pandas as pd
from itertools import combinations
import os

uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

def generate_combinations(uc_schools):
    combinations_list = []
    for i in range(len(uc_schools) - 2):
        for j in range(i + 1, len(uc_schools) - 1):
            remaining_schools = [s for s in uc_schools if s != uc_schools[i] and s != uc_schools[j]]
            for third in remaining_schools:
                combinations_list.append((uc_schools[i], uc_schools[j], third))
    return combinations_list

def count_required_courses(df, selected_schools, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_schools = [s.lower() for s in selected_schools]
    filtered_df = df[df['UC Name'].isin(selected_schools)]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, req_group), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        selected_courses = set()
        unmet_requirements_total = 0
        missing_courses_total = []

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
            else:
                unmet_requirements_total += unmet_requirements
                missing_courses = set_df['Receiving'].dropna().unique()
                missing_courses_total.extend(missing_courses[:unmet_requirements])

        for course in missing_courses_total:
            if course not in articulated_tracker and course not in unarticulated_tracker:
                unarticulated_courses.add(course)

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated)


def process_folder(folder_path):
    uc_totals = {uc: {'articulated': 0, 'unarticulated': 0} for uc in uc_schools}
    all_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]

    for file in all_files:
        print(f"\n--- Processing file: {file} ---")
        df = pd.read_csv(os.path.join(folder_path, file))
        uc_combos = generate_combinations(uc_schools)

        # Per-college UC counters
        cc_uc_counts = {uc: {'articulated': 0, 'unarticulated': 0} for uc in uc_schools}

        for combo in uc_combos:
            articulated_tracker = set()
            unarticulated_tracker = set()
            for uc in combo:
                art, unart = count_required_courses(df, [uc], articulated_tracker, unarticulated_tracker)
                cc_uc_counts[uc]['articulated'] += art
                cc_uc_counts[uc]['unarticulated'] += unart

        print(f"\nPer-UC Totals for {file}:")
        for uc in uc_schools:
            a = cc_uc_counts[uc]['articulated']
            u = cc_uc_counts[uc]['unarticulated']
            print(f"{uc}: {a} Articulated, {u} Unarticulated")
            uc_totals[uc]['articulated'] += a
            uc_totals[uc]['unarticulated'] += u

    print("\n=== FINAL AGGREGATE TOTALS ACROSS ALL COMMUNITY COLLEGES ===")
    for uc in uc_schools:
        print(f"{uc}: {uc_totals[uc]['articulated']} Articulated, {uc_totals[uc]['unarticulated']} Unarticulated")

# Example usage
folder_path = input("Enter path to folder with CSVs: ")
process_folder(folder_path)



#path: /Users/yasminkabir/assist_web_scraping-1/filtered_results