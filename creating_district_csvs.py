import os
import pandas as pd
import json
from collections import defaultdict

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

# Merge and deduplicate per district
for district, dfs in district_data.items():
    combined_df = pd.concat(dfs, ignore_index=True)

    # Drop duplicate 'Receiving' courses keeping the first articulated one found
    combined_df = combined_df.sort_values(by=['Receiving']).drop_duplicates(subset=['Receiving'], keep='first')

    # Save to CSV
    district_filename = district.replace(' ', '_').replace('/', '_') + '.csv'
    combined_df.to_csv(os.path.join(output_folder, district_filename), index=False)

print("Finished creating district CSVs!")

#/Users/yasminkabir/assist_web_scraping-3/filtered_results