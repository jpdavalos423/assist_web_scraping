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

# Load district mapping
with open('districts.json', 'r') as f:
    districts_data = json.load(f)['districts']

# Build college -> district lookup
college_to_district = {}
for district, info in districts_data.items():
    for college in info['colleges']:
        college_to_district[college] = district

# Ask user for folder path
input_folder = input("Enter the path to the folder containing the Community College CSVs: ").strip()
output_folder = "district_csvs"
os.makedirs(output_folder, exist_ok=True)

# Collect data by district
district_data = defaultdict(list)

# Process each college CSV
print("Reading all college CSVs...")
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        college_name = filename.replace('_filtered.csv', '').replace('_', ' ')
        file_path = os.path.join(input_folder, filename)
        df = pd.read_csv(file_path)

        if college_name not in college_to_district:
            print(f"Warning: {college_name} not found in districts.json, skipping.")
            continue

        district_name = college_to_district[college_name]

        # Add College Name column
        df.insert(0, 'College Name', college_name)

        district_data[district_name].append(df)

# Merge and select best articulations per district
print("Combining into district files...")
for district, dfs in district_data.items():
    combined = pd.concat(dfs, ignore_index=True)

    # Identify course group columns
    base_cols = ['College Name', 'UC Name', 'Group ID', 'Set ID', 'Num Required', 'Receiving']
    course_group_cols = [col for col in combined.columns if col not in base_cols]

    final_rows = []

    # Group by (UC Name, Group ID, Set ID, Receiving)
    grouped = combined.groupby(['UC Name', 'Group ID', 'Set ID', 'Receiving'])

    for group_keys, group_df in grouped:
        # Filter out unarticulated rows
        articulated = group_df[group_df['Courses Group 1'] != 'Not Articulated']

        if not articulated.empty:
            # Pick the row with fewest total courses
            articulated = articulated.copy()
            articulated['Total Courses'] = articulated.apply(lambda r: count_total_courses(r, course_group_cols), axis=1)
            best_row = articulated.sort_values('Total Courses').iloc[0].drop('Total Courses')
        else:
            # Create a Not Articulated row
            example_row = group_df.iloc[0]
            best_row = example_row.copy()
            best_row['College Name'] = 'Not Articulated'
            best_row['Courses Group 1'] = 'Not Articulated'
            for col in course_group_cols[1:]:
                best_row[col] = ''

        final_rows.append(best_row)

    # Create final DataFrame
    final_df = pd.DataFrame(final_rows)

    # Save to CSV
    district_filename = district.replace(' ', '_').replace('/', '_') + '.csv'
    final_df.to_csv(os.path.join(output_folder, district_filename), index=False)

    print(f"Saved {district_filename}")

print("\nAll district CSVs created successfully!")

#/Users/yasminkabir/assist_web_scraping-3/filtered_results