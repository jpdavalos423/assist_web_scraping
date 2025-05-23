import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import os

def can_transfer_to_uc(df, uc_name):
    # Get all requirements for this UC
    uc_requirements = df[df['UC Name'] == uc_name]
    unarticulated_courses = []
    
    # Group requirements by Group ID to handle sets
    grouped_reqs = uc_requirements.groupby('Group ID')
    
    # Check each group of requirements
    for group_id, group_data in grouped_reqs:
        # If there are multiple Set IDs, only one needs to be satisfied
        set_ids = group_data['Set ID'].unique()
        if len(set_ids) > 1:
            # Check if at least one set is satisfied
            set_satisfied = False
            best_set_unarticulated = []
            min_unarticulated = float('inf')
            
            for set_id in set_ids:
                set_data = group_data[group_data['Set ID'] == set_id]
                current_set_unarticulated = []
                
                for _, row in set_data.iterrows():
                    for col in [col for col in df.columns if col.startswith('Courses Group')]:
                        if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                            current_set_unarticulated.append(row['Receiving'])
                            
                if len(current_set_unarticulated) == 0:
                    set_satisfied = True
                    break
                elif len(current_set_unarticulated) < min_unarticulated:
                    min_unarticulated = len(current_set_unarticulated)
                    best_set_unarticulated = current_set_unarticulated
                    
            if not set_satisfied:
                unarticulated_courses.extend(best_set_unarticulated)
        else:
            # Single set ID - all courses must be satisfied
            for _, row in group_data.iterrows():
                for col in [col for col in df.columns if col.startswith('Courses Group')]:
                    if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                        unarticulated_courses.append(row['Receiving'])
    
    return unarticulated_courses

def count_transfer_options(file_path):
    """
    Reads a “_filtered.csv” articulation file and returns:
      - college_name
      - DataFrame with columns [UC Name, counts, unarticulated_courses]
        where `unarticulated_courses` is a '\n'-joined list of
        "Group X: course1, course2, …" lines.
    """
    df = pd.read_csv(file_path)
    college_name = os.path.basename(file_path).replace('_filtered.csv', '')
    
    records = []
    for uc in df['UC Name'].unique():
        uc_df = df[df['UC Name'] == uc]
        # gather unarticulated courses by group, considering Set IDs
        grouped = {}
        for group_id, group_data in uc_df.groupby('Group ID'):
            # Check if this group has multiple Set IDs
            set_ids = group_data['Set ID'].unique()
            if len(set_ids) > 1:
                # For multiple Set IDs, check if any set is fully articulated
                set_satisfied = False
                best_set_courses = None
                min_unarticulated = float('inf')
                
                for set_id in set_ids:
                    set_data = group_data[group_data['Set ID'] == set_id]
                    current_set_unarticulated = set()
                    
                    for _, row in set_data.iterrows():
                        for col in [c for c in df.columns if c.startswith('Courses Group')]:
                            if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                                current_set_unarticulated.add(row['Receiving'])
                    
                    if len(current_set_unarticulated) == 0:
                        set_satisfied = True
                        break
                    elif len(current_set_unarticulated) < min_unarticulated:
                        min_unarticulated = len(current_set_unarticulated)
                        best_set_courses = current_set_unarticulated
                
                if not set_satisfied and best_set_courses:
                    grouped[group_id] = best_set_courses
            else:
                # Single Set ID - check all courses
                unarticulated = set()
                for _, row in group_data.iterrows():
                    for col in [c for c in df.columns if c.startswith('Courses Group')]:
                        if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                            unarticulated.add(row['Receiving'])
                if unarticulated:
                    grouped[group_id] = unarticulated
        
        # build the multi-line string
        if grouped:
            lines = []
            for gid, courses in sorted(grouped.items()):
                courses_list = sorted(courses)
                lines.append(f"{gid}: {', '.join(courses_list)}")
            detail = "\n".join(lines)
            count = 0
        else:
            detail = ""    # fully articulated → blank cell
            count = 1
    
        records.append({
            'UC Name': uc,
            'counts': count,
            'unarticulated_courses': detail
        })
    
    return college_name, pd.DataFrame(records)
    
def analyze_all_colleges(directory):
    all_data = []
    
    # Process all CSV files in the directory
    for file in os.listdir(directory):
        if file.endswith('_filtered.csv'):
            file_path = os.path.join(directory, file)
            college_name, transfer_counts = count_transfer_options(file_path)
            
            # Add college name to each row
            transfer_counts['College'] = college_name
            all_data.append(transfer_counts)
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def create_heatmap(data):
    """
    Creates two files:
      - transfer_availability_heatmap.png  (binary 0/1 overview)
      - detailed_transfer_availability_heatmap.png
    The detailed version overlays each group’s missing courses
    on the red cells, one line per group.
    """
    # --- binary overview (unchanged) ---
    # plt.figure(figsize=(20, 30))
    # hm = data.pivot(index='College', columns='UC Name', values='counts')
    # sns.heatmap(hm, annot=True, cmap='RdYlGn', fmt='g', vmin=0, vmax=1)
    # plt.title('Valid Transfer Paths to UCs\n(1 = all articulated, 0 = some missing)', pad=20)
    # plt.ylabel('Community College')
    # plt.xlabel('UC Campus')
    # plt.xticks(rotation=30, ha='right')
    # plt.tight_layout()
    # plt.savefig('transfer_availability_heatmap.png', dpi=300, bbox_inches='tight')
    # plt.close()

    # --- detailed view with per-group lines ---
    plt.figure(figsize=(30, 80))
    detailed = data.pivot(index='College', columns='UC Name', values='unarticulated_courses')
    # blank → NaN so that isna()==True means "good" → green
    detailed = detailed.replace('', np.nan)
    status = detailed.isna().astype(int)

    sns.heatmap(
        status,
        cmap='RdYlGn',
        cbar=False,
        vmin=0,
        vmax=1,
        linewidths=1,
        linecolor='black',
        square=False,  # Allow rectangular cells
        annot=False
    )

    # overlay each cell’s multi-line detail
    for i, college in enumerate(detailed.index):
        for j, uc in enumerate(detailed.columns):
            text = detailed.iat[i, j]
            if pd.notna(text):
                plt.text(
                    j + 0.5, i + 0.5,
                    text,
                    ha='center', va='center',
                    wrap=True, fontsize=8,
                    color='white', fontweight='bold'
                )

    plt.title('Detailed Articulation (Green = OK, Red = Missing)', pad=20)
    plt.ylabel('Community College')
    plt.xlabel('UC Campus')
    plt.xticks(rotation=30, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    detailed_out = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'detailed_transfer_availability_heatmap.png'
    )
    plt.savefig(detailed_out, dpi=300, bbox_inches='tight')
    plt.close()

# def create_bar_plot(data):
#     # Calculate total transfer options per college
#     total_options = data.groupby('College')['counts'].sum().sort_values()
    
#     plt.figure(figsize=(20, 10))
#     ax = total_options.plot(kind='bar')
#     plt.title('Number of Valid UC Transfer Paths by Community College')
#     plt.xlabel('Community College')
#     plt.ylabel('Number of UCs with All Courses Articulated')
#     plt.xticks(rotation=90, ha='center')
#     plt.subplots_adjust(bottom=0.2)
#     plt.tight_layout()
#     output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'total_transfer_availability.png')
#     plt.savefig(output_path)
#     plt.close()

def main():
    # Directory containing the filtered CSV files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.normpath(os.path.join(script_dir, '../../filtered_results'))
    
    # Analyze all colleges
    combined_data = analyze_all_colleges(directory)
    
    # Create visualizations
    create_heatmap(combined_data)
    # create_bar_plot(combined_data)
    
    # Find college with fewest options
    total_options = combined_data.groupby('College')['counts'].sum()
    min_college = total_options.idxmin()
    min_count = total_options.min()
    
    print(f"\nCollege with fewest valid UC transfer paths: {min_college}")
    print(f"Number of UCs with all courses articulated: {min_count}")
    
    # Show which UCs have all courses articulated and which courses are not articulated
    college_data = combined_data[combined_data['College'] == min_college]
    print(f"\nDetailed transfer information for {min_college}:")
    for _, row in college_data.iterrows():
        if row['counts'] == 1:
            print(f"- {row['UC Name']}: All courses articulated")
        else:
            print(f"- {row['UC Name']}: Missing articulation for {row['unarticulated_courses']}")

if __name__ == "__main__":
    main()