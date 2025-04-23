import os
import json
import pandas as pd
import csv

def load_districts():
    with open('districts.json', 'r') as f:
        data = json.load(f)
    return data['districts']

def get_college_to_district_mapping(districts):
    mapping = {}
    for district_name, district_info in districts.items():
        for college in district_info['colleges']:
            normalized_name = college.replace(' ', '_')
            mapping[normalized_name] = district_name
    return mapping

def process_district_articulation():
    # Create districts_results directory if it doesn't exist
    if not os.path.exists('districts_results'):
        os.makedirs('districts_results')

    districts = load_districts()
    college_to_district = get_college_to_district_mapping(districts)
    
    # Group CSV files by district
    district_files = {}
    filtered_results_dir = 'filtered_results'
    
    for filename in os.listdir(filtered_results_dir):
        if filename.endswith('_filtered.csv'):
            college_name = filename.replace('_filtered.csv', '')
            for normalized_name, district in college_to_district.items():
                if normalized_name in college_name:
                    if district not in district_files:
                        district_files[district] = []
                    district_files[district].append(os.path.join(filtered_results_dir, filename))
                    break

    # Process each district
    for district, files in district_files.items():
        if not files:
            continue

        # Create output file for district
        output_file = os.path.join('districts_results', f'{district.replace(" ", "_")}_articulation.csv')
        
        # Read first file to get structure
        base_df = pd.read_csv(files[0])
        combined_data = {}

        # Process all files in the district
        for file in files:
            df = pd.read_csv(file)
            for _, row in df.iterrows():
                key = (row['UC Name'], row['Group ID'], row['Set ID'])
                
                # Check if any course is articulated and store receiving course
                articulated = False
                receiving_course = row['Receiving']
                
                course_columns = [col for col in df.columns if col.startswith('Courses Group')]
                for col in course_columns:
                    if pd.notna(row[col]) and 'Not Articulated' not in str(row[col]):
                        articulated = True
                        break
                
                if key not in combined_data:
                    combined_data[key] = {
                        'articulated': articulated,
                        'receiving': receiving_course
                    }
                else:
                    # If already articulated, keep existing data
                    if not combined_data[key]['articulated'] and articulated:
                        combined_data[key] = {
                            'articulated': articulated,
                            'receiving': receiving_course
                        }

        # Create output dataframe
        output_rows = []
        for key, data in combined_data.items():
            output_rows.append({
                'UC Name': key[0],
                'Group ID': key[1],
                'Set ID': key[2],
                'UC Course': data['receiving'],
                'Articulation Status': 'Articulated' if data['articulated'] else 'Not Articulated'
            })

        # Save to CSV
        output_df = pd.DataFrame(output_rows)
        output_df.to_csv(output_file, index=False)

if __name__ == "__main__":
    process_district_articulation()