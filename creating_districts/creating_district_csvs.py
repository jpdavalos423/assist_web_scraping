import os
import pandas as pd
import json
from collections import defaultdict

def count_total_courses(row, course_group_cols):
    """Helper to count total required courses (count semicolons across all course groups)."""
    total = 0
    for col in course_group_cols:
        cell = str(row.get(col, ""))
        if cell and cell != "Not Articulated":
            total += cell.count(';') + 1  # Semicolons mean multiple required courses
    return total

# --- Determine paths based on script location ---
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir   = os.path.dirname(script_dir)

districts_json_path = os.path.join(script_dir, 'districts.json')
input_folder        = os.path.join(root_dir, 'filtered_results')
output_folder       = os.path.join(root_dir, 'district_csvs')

# Make sure output folder exists
os.makedirs(output_folder, exist_ok=True)

# --- Load district mapping ---
with open(districts_json_path, 'r') as f:
    districts_data = json.load(f)['districts']

# Build college -> district lookup
college_to_district = {}
for district, info in districts_data.items():
    for college in info['colleges']:
        college_to_district[college] = district

# --- Collect data by district ---
district_data = defaultdict(list)

print(f"Reading all college CSVs from: {input_folder}")
for filename in os.listdir(input_folder):
    if not filename.endswith('.csv'):
        continue

    college_name = filename.replace('_filtered.csv', '').replace('_', ' ')
    file_path    = os.path.join(input_folder, filename)
    df           = pd.read_csv(file_path)

    if college_name not in college_to_district:
        print(f"  ⚠️  Warning: {college_name} not found in districts.json, skipping.")
        continue

    district_name = college_to_district[college_name]
    df.insert(0, 'College Name', college_name)
    district_data[district_name].append(df)

# --- Merge and pick best articulations per district ---
print("\nCombining into district files...")
for district, dfs in district_data.items():
    combined = pd.concat(dfs, ignore_index=True)

    # Identify course‐group columns
    base_cols         = ['College Name', 'UC Name', 'Group ID', 'Set ID', 'Num Required', 'Receiving']
    course_group_cols = [c for c in combined.columns if c not in base_cols]

    final_rows = []
    grouped    = combined.groupby(['UC Name', 'Group ID', 'Set ID', 'Receiving'])

    for _, group_df in grouped:
        # Prefer articulated rows
        articulated = group_df[group_df['Courses Group 1'] != 'Not Articulated']

        if not articulated.empty:
            # Take the one with fewest total courses
            articulated = articulated.copy()
            articulated['Total Courses'] = articulated.apply(
                lambda r: count_total_courses(r, course_group_cols), axis=1
            )
            best_row = articulated.sort_values('Total Courses').iloc[0].drop('Total Courses')
        else:
            # Make a synthetic “Not Articulated” row
            example_row = group_df.iloc[0].copy()
            example_row['College Name']    = 'Not Articulated'
            example_row['Courses Group 1'] = 'Not Articulated'
            for col in course_group_cols[1:]:
                example_row[col] = ''
            best_row = example_row

        final_rows.append(best_row)

    final_df = pd.DataFrame(final_rows)

    # Write out
    safe_name      = district.replace(' ', '_').replace('/', '_')
    out_csv        = os.path.join(output_folder, f"{safe_name}.csv")
    final_df.to_csv(out_csv, index=False)
    print(f"  ✓ Saved {out_csv}")

print("\nAll district CSVs created successfully!")
