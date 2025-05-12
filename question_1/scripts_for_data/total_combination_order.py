import pandas as pd
from itertools import permutations
import os

uc_schools = ["UCSD", "UCSB", "UCSC", "UCLA", "UCB", "UCI", "UCD", "UCR", "UCM"]

def generate_combinations(uc_schools):
    return list(permutations(uc_schools, 3))

def count_required_courses(df, selected_schools, articulated_tracker, unarticulated_tracker):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()
    selected_schools = [school.lower().strip() for school in selected_schools]
    filtered_df = df[df['UC Name'].isin(selected_schools)]

    articulated_courses = set()
    unarticulated_courses = set()

    for (uc, group_id), group_df in filtered_df.groupby(['UC Name', 'Group ID']):
        fulfilled = False
        fallback_receiving = None

        for set_id, set_df in group_df.groupby('Set ID'):
            all_cc_courses = set()
            all_receiving_courses = set()

            for _, row in set_df.iterrows():
                receiving = [r.strip() for r in str(row['Receiving']).split(';') if r.strip()]
                all_receiving_courses.update(receiving)

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
                fulfilled = True
                new_courses = all_cc_courses - set(c for (_, c) in articulated_tracker)
                articulated_courses.update((uc, course) for course in new_courses)
                break

            if fallback_receiving is None or len(all_receiving_courses) < len(fallback_receiving):
                fallback_receiving = all_receiving_courses

        if not fulfilled and fallback_receiving:
            for course in fallback_receiving:
                unarticulated_courses.add((uc, course))

    new_articulated = articulated_courses - articulated_tracker
    new_unarticulated = unarticulated_courses - unarticulated_tracker

    articulated_tracker.update(new_articulated)
    unarticulated_tracker.update(new_unarticulated)

    return len(new_articulated), len(new_unarticulated)

def process_combinations_order_sensitive(df, uc_list):
    all_combinations = generate_combinations(uc_list)

    uc_role_totals = {
        uc: {'1st': {'articulated': 0, 'unarticulated': 0},
             '2nd': {'articulated': 0, 'unarticulated': 0},
             '3rd': {'articulated': 0, 'unarticulated': 0}} for uc in uc_list
    }

    for uc1, uc2, uc3 in all_combinations:
        articulated_tracker = set()
        unarticulated_tracker = set()

        for idx, uc in enumerate([uc1, uc2, uc3]):
            role = f"{idx + 1}st" if idx == 0 else f"{idx + 1}nd" if idx == 1 else f"{idx + 1}rd"
            art_count, unart_count = count_required_courses(
                df, [uc], articulated_tracker, unarticulated_tracker
            )
            uc_role_totals[uc][role]['articulated'] += art_count
            uc_role_totals[uc][role]['unarticulated'] += unart_count

    return uc_role_totals

def process_all_csvs(folder_path):
    total_txt = "total_combination_order.txt"
    avg_txt = "average_combination_order.txt"
    excluded_txt = "excluded_cc_uc_pairs.txt"

    open(total_txt, 'w').close()
    open(avg_txt, 'w').close()
    open(excluded_txt, 'w').close()

    overall_totals = {
        uc: {'1st': {'articulated': 0, 'unarticulated': 0},
             '2nd': {'articulated': 0, 'unarticulated': 0},
             '3rd': {'articulated': 0, 'unarticulated': 0}} for uc in uc_schools
    }

    csv_files = [f for f in os.listdir(folder_path) if f.endswith('.csv')]
    average_results_list = []

    for idx, file in enumerate(csv_files):
        print(f"Processing {idx+1}/{len(csv_files)}: {file}")
        file_path = os.path.join(folder_path, file)
        df = pd.read_csv(file_path)
        results = process_combinations_order_sensitive(df, uc_schools)

        for uc in uc_schools:
            for role in ['1st', '2nd', '3rd']:
                overall_totals[uc][role]['articulated'] += results[uc][role]['articulated']
                overall_totals[uc][role]['unarticulated'] += results[uc][role]['unarticulated']

        with open(total_txt, "a") as f:
            f.write(f"--- Processing {file} ---\n\n")
            for uc in uc_schools:
                f.write(f"{uc}:\n")
                for role in ['1st', '2nd', '3rd']:
                    art = results[uc][role]['articulated']
                    unart = results[uc][role]['unarticulated']
                    f.write(f"  As {role}: {art} Courses, {unart} Unarticulated\n")
                f.write("\n")

        avg = {
            uc: {role: {
                'articulated': round(results[uc][role]['articulated'] / 56, 2),
                'unarticulated': round(results[uc][role]['unarticulated'] / 56, 2)
            } for role in ['1st', '2nd', '3rd']} for uc in uc_schools
        }
        average_results_list.append(avg)

        with open(avg_txt, "a") as f:
            f.write(f"--- Processing {file} ---\n\n")
            for uc in uc_schools:
                f.write(f"{uc}:\n")
                for role in ['1st', '2nd', '3rd']:
                    art = avg[uc][role]['articulated']
                    unart = avg[uc][role]['unarticulated']
                    f.write(f"  As {role}: {art} Courses, {unart} Unarticulated\n")
                f.write("\n")

    # Append grand totals and averages
    with open(total_txt, "a") as f:
        f.write("\n--- Grand Totals Across All Files ---\n\n")
        for uc in uc_schools:
            f.write(f"{uc}:\n")
            for role in ['1st', '2nd', '3rd']:
                art = overall_totals[uc][role]['articulated']
                unart = overall_totals[uc][role]['unarticulated']
                f.write(f"  As {role}: {art} Courses, {unart} Unarticulated\n")
            f.write("\n")

        n = len(csv_files)
        f.write("--- Averages (Total ÷ # Files) ---\n\n")
        for uc in uc_schools:
            f.write(f"{uc}:\n")
            for role in ['1st', '2nd', '3rd']:
                art_avg = round(overall_totals[uc][role]['articulated'] / n, 2)
                unart_avg = round(overall_totals[uc][role]['unarticulated'] / n, 2)
                f.write(f"  As {role}: {art_avg} Courses, {unart_avg} Unarticulated\n")
            f.write("\n")

    with open(avg_txt, "a") as f:
        f.write("--- Average of Averages ---\n\n")
        n = len(average_results_list)
        for uc in uc_schools:
            f.write(f"{uc}:\n")
            for role in ['1st', '2nd', '3rd']:
                art_total = sum(avg[uc][role]['articulated'] for avg in average_results_list)
                unart_total = sum(avg[uc][role]['unarticulated'] for avg in average_results_list)
                art_avg = round(art_total / n, 2)
                unart_avg = round(unart_total / n, 2)
                f.write(f"  As {role}: {art_avg} Courses, {unart_avg} Unarticulated\n")
            f.write("\n")

    # Create per-order average CSVs with filtered average row
    for idx, role in enumerate(['1st', '2nd', '3rd']):
        data = []
        filtered_pairs = []
        filtered_sum = {}
        filtered_count = {}

        for file_name, avg in zip(csv_files, average_results_list):
            row = {"Community College": file_name}
            for uc in uc_schools:
                art = avg[uc][role]['articulated']
                unart = avg[uc][role]['unarticulated']
                row[f"{uc} Articulated"] = art
                row[f"{uc} Unarticulated"] = unart

                if unart == 0:
                    filtered_sum[f"{uc} Articulated"] = filtered_sum.get(f"{uc} Articulated", 0) + art
                    filtered_count[f"{uc} Articulated"] = filtered_count.get(f"{uc} Articulated", 0) + 1
                else:
                    filtered_pairs.append((file_name, uc))
            data.append(row)

        df = pd.DataFrame(data)

        avg_row = {"Community College": "AVERAGE"}
        for col in df.columns[1:]:
            avg_row[col] = round(df[col].mean(), 2)
        df = pd.concat([df, pd.DataFrame([avg_row])], ignore_index=True)

        # Add filtered average row
        transfer_avg_row = {"Community College": "TRANSFERABLE AVERAGE"}
        for col in df.columns[1:]:
            if col.endswith("Articulated"):
                if filtered_count.get(col, 0) > 0:
                    transfer_avg_row[col] = round(filtered_sum[col] / filtered_count[col], 2)
                else:
                    transfer_avg_row[col] = 0.0
            else:
                transfer_avg_row[col] = 0.0
        df = pd.concat([df, pd.DataFrame([transfer_avg_row])], ignore_index=True)

        df.to_csv(f"order_{idx+1}_averages.csv", index=False)

        # Append filtered average to average_combination_order.txt
        with open(avg_txt, "a") as f:
            f.write(f"--- Transferable Average of Averages for Order {idx+1} ---\n\n")
            for col in df.columns[1:]:
                if col != "Community College":
                    f.write(f"{col}: {transfer_avg_row[col]}\n")
            f.write("\n")

        # Write excluded pairs to txt file
        with open(excluded_txt, "a") as f:
            f.write(f"--- Order {idx+1} ---\n")
            cc_grouped = {}
            for cc, uc in filtered_pairs:
                cc_grouped.setdefault(cc, []).append(uc)
            for cc in sorted(cc_grouped):
                ucs = ", ".join(cc_grouped[cc])
                f.write(f"{cc}: {ucs}\n")
            f.write("\n")

if __name__ == "__main__":
    folder_path = "/Users/yasminkabir/assist_web_scraping/district_csvs"
    process_all_csvs(folder_path)