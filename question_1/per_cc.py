import pandas as pd
from itertools import permutations
from io import StringIO
import requests
import os
from contextlib import redirect_stdout

uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

def generate_combinations(uc_schools):
    return list(permutations(uc_schools, 3))

def count_required_courses(df, selected_schools, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_schools = [school.strip().lower() for school in selected_schools]
    filtered_df = df[df['UC Name'].isin(selected_schools)]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, group_id), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        group_fulfilled = False
        fallback_set_courses = []
        fallback_num_required = float('inf')

        for set_id, set_df in group_df.groupby('Set ID'):
            num_required = int(set_df['Num Required'].iloc[0])
            receiving_to_articulated = {}

            for _, row in set_df.iterrows():
                receiving_courses = [c.strip() for c in str(row['Receiving']).split(';') if c.strip() and c.strip().lower() != 'not articulated']

                cc_articulated = False
                for col in row.index:
                    if col.lower().startswith("courses group"):
                        val = str(row[col]).strip().lower()
                        if val and val != "not articulated":
                            cc_articulated = True
                            break

                for course in receiving_courses:
                    if course not in receiving_to_articulated:
                        receiving_to_articulated[course] = cc_articulated
                    else:
                        receiving_to_articulated[course] = receiving_to_articulated[course] or cc_articulated

            # Count how many receiving courses are articulated
            articulated_list = [course for course, is_art in receiving_to_articulated.items() if is_art]
            if len(articulated_list) >= num_required:
                articulated_courses.update((uc, course) for course in articulated_list[:num_required])
                group_fulfilled = True
                break  # Stop checking other sets once one is fulfilled

            # Save fallback info in case none are fulfilled
            if len(receiving_to_articulated) < fallback_num_required:
                fallback_num_required = num_required
                fallback_set_courses = list(receiving_to_articulated.keys())[:num_required]

        if not group_fulfilled and fallback_set_courses:
            unarticulated_courses.update((uc, course) for course in fallback_set_courses)

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated), new_articulated, new_unarticulated

def process_combinations(df, uc_list):
    all_combinations = generate_combinations(uc_list)
    print(f"Total UC combinations generated: {len(all_combinations)}")

    uc_role_totals = {
        uc: {'1st': {'articulated': 0, 'unarticulated': 0},
             '2nd': {'articulated': 0, 'unarticulated': 0},
             '3rd': {'articulated': 0, 'unarticulated': 0}} for uc in uc_list
    }

    for uc1, uc2, uc3 in all_combinations:
        articulated_tracker = set()
        unarticulated_tracker = set()
        total_unique_courses = 0
        results = []

        for idx, uc in enumerate([uc1, uc2, uc3]):
            role = f"{idx + 1}st" if idx == 0 else f"{idx + 1}nd" if idx == 1 else f"{idx + 1}rd"
            articulated_count, unarticulated_count, _, _ = count_required_courses(
                df, [uc], articulated_tracker, unarticulated_tracker
            )
            uc_role_totals[uc][role]['articulated'] += articulated_count
            uc_role_totals[uc][role]['unarticulated'] += unarticulated_count
            total_unique_courses += articulated_count + unarticulated_count
            results.append(f"{uc.upper()} ({role}): {articulated_count} Courses, {unarticulated_count} Unarticulated")

        print(f"\nProcessing combination: {uc1}, {uc2}, {uc3}")
        print(f"Total Unique Courses Required: {total_unique_courses}")
        for res in results:
            print(res)

    print("\n--- Final Totals Per UC by Role in Combination ---\n")
    for uc in uc_list:
        print(f"{uc}:")
        for role in ['1st', '2nd', '3rd']:
            art = uc_role_totals[uc][role]['articulated']
            unart = uc_role_totals[uc][role]['unarticulated']
            print(f"  As {role}: {art} Courses, {unart} Unarticulated")
        print()

def load_csv(file_path):
    return pd.read_csv(file_path)

if __name__ == "__main__":
    file_path = "/Users/yasminkabir/assist_web_scraping/district_csvs/Merced_Community_College_District.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    df = pd.read_csv(file_path)
    uc_list = uc_schools

    # Set output file name
    output_file = "articulation_output.txt"

    with open(output_file, "w") as f:
        with redirect_stdout(f):
            process_combinations(df, uc_list)