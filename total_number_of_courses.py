import pandas as pd
import os

def count_required_courses(df):
    df.columns = df.columns.str.strip()
    df['UC Name'] = df['UC Name'].str.lower().str.strip()

    articulated_courses = set()
    total_unarticulated_count = 0

    # Process each UC and Group ID (Requirement Group)
    for (uc, group_id), group_df in df.groupby(['UC Name', 'Group ID']):
        best_set_missing = float('inf')
        best_set_articulated = set()

        # Try each Set ID (subgroup) within the group
        for set_id, set_df in group_df.groupby('Set ID'):
            num_required = set_df['Num Required'].iloc[0]
            found = 0
            articulated_in_set = set()

            for _, row in set_df.iterrows():
                cc_entry = str(row['Courses Group 1']).strip().lower()
                if cc_entry == "not articulated":
                    continue
                cc_courses = [c.strip() for c in row['Courses Group 1'].split(';') if c.strip().lower() != 'not articulated']
                for course in cc_courses:
                    if course not in articulated_in_set:
                        articulated_in_set.add(course)
                        found += 1
                    if found >= num_required:
                        break

            missing = max(0, num_required - found)

            # Update the best set if it has fewer missing requirements
            if missing < best_set_missing:
                best_set_missing = missing
                best_set_articulated = articulated_in_set

        # Update global totals
        total_unarticulated_count += best_set_missing
        articulated_courses.update(best_set_articulated)

    return len(articulated_courses), total_unarticulated_count




def process_files(folder_path):
    total_articulated = 0
    total_unarticulated = 0

    for filename in os.listdir(folder_path):
        if not filename.endswith(".csv"):
            continue

        filepath = os.path.join(folder_path, filename)
        print(f"\nProcessing: {filename}")

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

        df.columns = df.columns.str.strip()

        if 'UC Name' not in df.columns or 'Group ID' not in df.columns:
            print(f"Skipping {filename} due to missing columns.")
            continue

        if df['UC Name'].nunique() == 0:
            print(f"No UC campuses found in {filename}")
            continue
        else:
            print(f"UC campuses found: {df['UC Name'].unique()}")

        articulated, unarticulated = count_required_courses(df)
        print(f"Articulated: {articulated}, Unarticulated: {unarticulated}")

        total_articulated += articulated
        total_unarticulated += unarticulated

    print("\nSummary of UC Articulated and Unarticulated Course Requirements:")
    print(f"Total Articulated Community College Courses: {total_articulated}")
    print(f"Total Unfilled Course Requirements (Unarticulated): {total_unarticulated}")


if __name__ == "__main__":
    folder_path = input("Enter folder path containing all CC CSVs: ").strip()
    process_files(folder_path)


#path: /Users/yasminkabir/assist_web_scraping-1/filtered_results
