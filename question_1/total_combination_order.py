import pandas as pd
import os
from contextlib import redirect_stdout

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
    # Normalize column headers
    df.columns = df.columns.str.replace('\u200b', '', regex=False).str.strip().str.lower()

    if 'uc name' not in df.columns:
        raise ValueError(f"'UC Name' column not found. Found columns: {list(df.columns)}")

    df['uc name'] = df['uc name'].str.lower().str.strip()
    selected_school = selected_school[0].lower()
    filtered_df = df[df['uc name'] == selected_school]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, req_group), group_df in filtered_df.groupby(['uc name', 'group id']):
        group_fulfilled = False

        for set_id, set_df in group_df.groupby('set id'):
            num_required = set_df['num required'].iloc[0]

            fulfilled = set()
            unfulfilled = set()

            for _, row in set_df.iterrows():
                receiving_course = row['receiving']
                course_group_1 = str(row['courses group 1']).strip().lower()

                if course_group_1 != "not articulated":
                    fulfilled.add(receiving_course)
                else:
                    unfulfilled.add(receiving_course)

            if len(fulfilled) >= num_required:
                articulated_courses.update(fulfilled)
                group_fulfilled = True
                break

        if not group_fulfilled:
            first_set_id = next(iter(group_df.groupby('set id')))
            set_df = group_df[group_df['set id'] == first_set_id[0]]
            num_required = set_df['num required'].iloc[0]

            fulfilled = set()
            unfulfilled = set()

            for _, row in set_df.iterrows():
                receiving_course = row['receiving']
                course_group_1 = str(row['courses group 1']).strip().lower()

                if course_group_1 != "not articulated":
                    fulfilled.add(receiving_course)
                else:
                    unfulfilled.add(receiving_course)

            articulated_courses.update(fulfilled)
            num_unmet = num_required - len(fulfilled)
            for uc_course in list(unfulfilled)[:num_unmet]:
                unarticulated_courses.add(uc_course)

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated)

def process_combinations_with_roles(df, uc_list, file_counts):
    all_combinations = generate_combinations(uc_list)

    for combo in all_combinations:
        articulated_tracker = set()
        unarticulated_tracker = set()

        for idx, uc in enumerate(combo):
            role = f"{idx+1}st" if idx == 0 else f"{idx+1}nd" if idx == 1 else f"{idx+1}rd"
            art, unart = count_required_courses(
                df, [uc], articulated_tracker, unarticulated_tracker
            )
            file_counts[uc][role][0] += art
            file_counts[uc][role][1] += unart

def process_folder(input_folder):
    uc_list = uc_schools
    overall_counts = {uc: {'1st': [0, 0], '2nd': [0, 0], '3rd': [0, 0]} for uc in uc_list}
    num_files = 0

    role_columns = [f"{uc} Art" for uc in uc_list] + [f"{uc} Unart" for uc in uc_list]
    df_1st = pd.DataFrame(columns=role_columns)
    df_2nd = pd.DataFrame(columns=role_columns)
    df_3rd = pd.DataFrame(columns=role_columns)

    for filename in os.listdir(input_folder):
        if (
            filename.endswith(".csv")
            and not filename.startswith("order_")
            and "combination_totals" not in filename.lower()
        ):
            district_name = os.path.splitext(filename)[0]
            num_files += 1
            print(f"\n--- Processing {filename} ---")
            df = load_csv(os.path.join(input_folder, filename))

            file_counts = {uc: {'1st': [0, 0], '2nd': [0, 0], '3rd': [0, 0]} for uc in uc_list}
            process_combinations_with_roles(df, uc_list, file_counts)

            for uc in uc_list:
                print(f"\n{uc}:")
                for role in ['1st', '2nd', '3rd']:
                    a, u = file_counts[uc][role]
                    print(f"  As {role}: {round(a / 56, 2)} Courses, {round(u / 56, 2)} Unarticulated")

            for uc in uc_list:
                for role in ['1st', '2nd', '3rd']:
                    overall_counts[uc][role][0] += file_counts[uc][role][0]
                    overall_counts[uc][role][1] += file_counts[uc][role][1]

            row_1st, row_2nd, row_3rd = {}, {}, {}
            for uc in uc_list:
                row_1st[f"{uc} Art"] = round(file_counts[uc]['1st'][0] / 56, 2)
                row_1st[f"{uc} Unart"] = round(file_counts[uc]['1st'][1] / 56, 2)
                row_2nd[f"{uc} Art"] = round(file_counts[uc]['2nd'][0] / 56, 2)
                row_2nd[f"{uc} Unart"] = round(file_counts[uc]['2nd'][1] / 56, 2)
                row_3rd[f"{uc} Art"] = round(file_counts[uc]['3rd'][0] / 56, 2)
                row_3rd[f"{uc} Unart"] = round(file_counts[uc]['3rd'][1] / 56, 2)

            df_1st.loc[district_name] = row_1st
            df_2nd.loc[district_name] = row_2nd
            df_3rd.loc[district_name] = row_3rd

    print("\n=== FINAL TOTAL ACROSS ALL FILES (DIVIDED BY 56) ===")
    for uc in uc_list:
        print(f"\n{uc}:")
        for role in ['1st', '2nd', '3rd']:
            a, u = overall_counts[uc][role]
            print(f"  As {role}: {round(a / 56, 2)} Courses, {round(u / 56, 2)} Unarticulated")

    print("\n=== AVERAGE PER FILE ===")
    if num_files > 0:
        for uc in uc_list:
            print(f"\n{uc}:")
            for role in ['1st', '2nd', '3rd']:
                a, u = overall_counts[uc][role]
                avg_a = round(a / num_files / 56, 2)
                avg_u = round(u / num_files / 56, 2)
                print(f"  As {role}: {avg_a} Avg Courses, {avg_u} Avg Unarticulated")
    else:
        print("No CSV files processed.")

    # ✅ Save outputs to a clean output folder
    output_dir = os.path.join(input_folder, "question_1")
    os.makedirs(output_dir, exist_ok=True)

    df_1st.to_csv(os.path.join(output_dir, "order_1_totals.csv"))
    df_2nd.to_csv(os.path.join(output_dir, "order_2_totals.csv"))
    df_3rd.to_csv(os.path.join(output_dir, "order_3_totals.csv"))

    print(f"\n✅ CSVs saved to: {output_dir}")
    print("  - order_1_totals.csv")
    print("  - order_2_totals.csv")
    print("  - order_3_totals.csv")

# Redirect output to a text file
if __name__ == "__main__":
    folder_path = input("Enter path to folder with CSV files: ")
    output_file = "total_combination_order.txt"
    with open(output_file, "w") as f:
        with redirect_stdout(f):
            process_folder(folder_path)
    print(f"\n✅ All printed output saved to '{output_file}'")


    #/workspaces/assist_web_scraping/district_csvs
    #path: /Users/yasminkabir/assist_web_scraping-1/district_csvs