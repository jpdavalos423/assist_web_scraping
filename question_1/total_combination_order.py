import pandas as pd
from itertools import permutations
import os

uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

def load_csv(file_path):
    return pd.read_csv(file_path)

def generate_combinations(uc_schools):
    return list(permutations(uc_schools, 3))

def count_required_courses(df, selected_schools, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_schools = [school.strip().lower() for school in selected_schools]
    filtered_df = df[df['UC Name'].isin(selected_schools)]

    articulated_courses = set()
    unarticulated_courses = set()
    group_fulfilled = set()

    for (uc, req_group), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        group_fulfilled_flag = False

        for set_id, set_df in group_df.groupby('Set ID'):
            num_required = set_df['Num Required'].iloc[0]
            possible_combinations = []
            unmet_requirements = num_required
            selected_courses = set()

            for _, row in set_df.iterrows():
                cc_course_options = []
                if pd.notna(row['Courses Group 1']) and row['Courses Group 1'] != "Not Articulated":
                    cc_course_options.append(set(map(str.strip, row['Courses Group 1'].split(";"))))

                for col in row.index[6:]:
                    if pd.notna(row[col]) and row[col] != "Not Articulated":
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
                group_fulfilled_flag = True
                break

        if not group_fulfilled_flag and req_group not in group_fulfilled:
            for _, row in group_df.iterrows():
                if pd.notna(row['Receiving']) and row['Receiving'] != "Not Articulated":
                    unarticulated_courses.add(row['Receiving'])
                    break
            group_fulfilled.add(req_group)

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated)

def process_folder(folder_path):
    uc_list = uc_schools
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]
    role_count_per_uc = 56
    num_files = 0
    roles = ['1st', '2nd', '3rd']

    overall_totals = {
        uc: {role: {'articulated': 0, 'unarticulated': 0} for role in roles} for uc in uc_list
    }

    # For final CSV output (accumulating per order, per CC)
    per_order_cc_totals = {role: [] for role in roles}
    per_order_cc_averages = {role: [] for role in roles}

    with open("total_combination_order.txt", "w") as f:
        f.write("")
    with open("average_combination_order.txt", "w") as f:
        f.write("")

    for file_name in all_files:
        file_path = os.path.join(folder_path, file_name)
        df = load_csv(file_path)

        required_cols = {"UC Name", "Group ID", "Set ID", "Num Required", "Receiving", "Courses Group 1"}
        if not required_cols.issubset(set(df.columns)):
            print(f"Skipping {file_name} — missing required columns.\n")
            continue

        num_files += 1
        uc_role_totals = {
            uc: {role: {'articulated': 0, 'unarticulated': 0} for role in roles} for uc in uc_list
        }

        for uc1, uc2, uc3 in generate_combinations(uc_list):
            articulated_tracker = set()
            unarticulated_tracker = set()
            for idx, uc in enumerate([uc1, uc2, uc3]):
                role = roles[idx]
                art_count, unart_count = count_required_courses(
                    df, [uc], articulated_tracker, unarticulated_tracker
                )
                uc_role_totals[uc][role]['articulated'] += art_count
                uc_role_totals[uc][role]['unarticulated'] += unart_count

        # Write .txt totals
        with open("total_combination_order.txt", "a") as f:
            f.write(f"--- Processing {file_name} ---\n")
            for uc in uc_list:
                f.write(f"{uc}:\n")
                for role in roles:
                    art = uc_role_totals[uc][role]['articulated']
                    unart = uc_role_totals[uc][role]['unarticulated']
                    f.write(f"  As {role}: {art} Courses, {unart} Unarticulated\n")
                    overall_totals[uc][role]['articulated'] += art
                    overall_totals[uc][role]['unarticulated'] += unart
                f.write("\n")

        # Write .txt averages
        with open("average_combination_order.txt", "a") as f:
            f.write(f"--- Averages for {file_name} ---\n")
            for uc in uc_list:
                f.write(f"{uc}:\n")
                for role in roles:
                    art = uc_role_totals[uc][role]['articulated']
                    unart = uc_role_totals[uc][role]['unarticulated']
                    f.write(f"  As {role}: {art / role_count_per_uc:.2f} Avg Courses, {unart / role_count_per_uc:.2f} Avg Unarticulated\n")
                f.write("\n")

        # Save row for CSVs per order
        for role in roles:
            row_total = {"Community College": file_name}
            row_avg = {"Community College": file_name}
            for uc in uc_list:
                art = uc_role_totals[uc][role]['articulated']
                unart = uc_role_totals[uc][role]['unarticulated']
                row_total[f"{uc} Articulated"] = art
                row_total[f"{uc} Unarticulated"] = unart
                row_avg[f"{uc} Articulated"] = round(art / role_count_per_uc, 2)
                row_avg[f"{uc} Unarticulated"] = round(unart / role_count_per_uc, 2)
            per_order_cc_totals[role].append(row_total)
            per_order_cc_averages[role].append(row_avg)

    # Final .txt output
    with open("total_combination_order.txt", "a") as f:
        f.write("--- GRAND TOTALS ACROSS ALL FILES ---\n")
        for uc in uc_list:
            f.write(f"{uc}:\n")
            for role in roles:
                art = overall_totals[uc][role]['articulated']
                unart = overall_totals[uc][role]['unarticulated']
                f.write(f"  As {role}: {art} Courses, {unart} Unarticulated\n")
            f.write("\n")

    with open("average_combination_order.txt", "a") as f:
        f.write("--- OVERALL AVERAGES ACROSS ALL FILES ---\n")
        for uc in uc_list:
            f.write(f"{uc}:\n")
            for role in roles:
                total_art = overall_totals[uc][role]['articulated']
                total_unart = overall_totals[uc][role]['unarticulated']
                divisor = role_count_per_uc * num_files
                f.write(f"  As {role}: {total_art / divisor:.2f} Avg Courses, {total_unart / divisor:.2f} Avg Unarticulated\n")
            f.write("\n")

    # Write CSVs for each order
    for role in roles:
        pd.DataFrame(per_order_cc_totals[role]).to_csv(f"order_{role[0]}_totals.csv", index=False)
        pd.DataFrame(per_order_cc_averages[role]).to_csv(f"order_{role[0]}_averages.csv", index=False)

    print("✅ All totals, averages, and CSVs written successfully.")

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder of CSV files: ")
    process_folder(folder_path)




    #/workspaces/assist_web_scraping/district_csvs
    #path: /Users/yasminkabir/assist_web_scraping-1/question_1/question_1/order_1_totals.csv
    #path: /Users/yasminkabir/assist_web_scraping-1/district_csvs