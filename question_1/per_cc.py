import pandas as pd
from itertools import permutations
import os
from contextlib import redirect_stdout

# List of UC campuses
uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

# Generate all 3-UC permutations
def generate_combinations(uc_schools):
    return list(permutations(uc_schools, 3))

# Fixed logic for counting articulated and unarticulated courses
def count_required_courses(df, selected_schools, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_schools = [school.strip().lower() for school in selected_schools]
    filtered_df = df[df['UC Name'].isin(selected_schools)]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, group_id), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        group_fulfilled = False
        best_set_cc_courses = None

        for set_id, set_df in group_df.groupby('Set ID'):
            all_cc_courses = set()
            for _, row in set_df.iterrows():
                best_option = None
                for col in row.index:
                    if col.lower().startswith("courses group"):
                        val = str(row[col]).strip()
                        if val and val.lower() != "not articulated" and val.lower() != "nan":
                            option = [v.strip() for v in val.split(';') if v.strip()]
                            if best_option is None or len(option) < len(best_option):
                                best_option = option
                if best_option:
                    all_cc_courses.update(best_option)

            if all_cc_courses:
                group_fulfilled = True
                best_set_cc_courses = all_cc_courses
                break

        if group_fulfilled and best_set_cc_courses:
            new_courses = best_set_cc_courses - set(c for (_, c) in articulated_tracker)
            articulated_courses.update((uc, course) for course in new_courses)
        else:
            unarticulated_courses.add((uc, f"UNART_{group_id}"))

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated), new_articulated, new_unarticulated

# Run all 3-UC combinations and count totals per UC by order
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

# CSV loader
def load_csv(file_path):
    return pd.read_csv(file_path)

# Run everything
if __name__ == "__main__":
    file_path = "/Users/yasminkabir/assist_web_scraping/district_csvs/Merced_Community_College_District.csv"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"❌ File not found: {file_path}")

    df = pd.read_csv(file_path)
    uc_list = uc_schools

    output_file = "articulation_output.txt"
    with open(output_file, "w") as f:
        with redirect_stdout(f):
            process_combinations(df, uc_list)
