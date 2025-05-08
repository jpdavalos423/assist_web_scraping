import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def can_transfer_to_uc(df, uc_name):
    # Get all requirements for this UC
    uc_requirements = df[df['UC Name'] == uc_name]
    
    # Group requirements by Group ID to handle sets
    grouped_reqs = uc_requirements.groupby('Group ID')
    
    # Check each group of requirements
    for group_id, group_data in grouped_reqs:
        # If there are multiple Set IDs, only one needs to be satisfied
        set_ids = group_data['Set ID'].unique()
        if len(set_ids) > 1:
            # Check if at least one set is satisfied
            set_satisfied = False
            for set_id in set_ids:
                set_data = group_data[group_data['Set ID'] == set_id]
                # Check if this set has any "Not Articulated" courses
                has_not_articulated = False
                for _, row in set_data.iterrows():
                    for col in [col for col in df.columns if col.startswith('Courses Group')]:
                        if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                            has_not_articulated = True
                            break
                    if has_not_articulated:
                        break
                if not has_not_articulated:
                    set_satisfied = True
                    break
            if not set_satisfied:
                return False
        else:
            # Single set ID - all courses must be satisfied
            for _, row in group_data.iterrows():
                for col in [col for col in df.columns if col.startswith('Courses Group')]:
                    if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                        return False
    return True

def count_transfer_options(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Get college name from file path
    college_name = os.path.basename(file_path).replace('_filtered.csv', '')
    
    # Get unique UCs
    unique_ucs = df['UC Name'].unique()
    
    # Count UCs where all requirements can be satisfied (no "Not Articulated" courses)
    transfer_counts = []
    for uc in unique_ucs:
        can_transfer = 1 if can_transfer_to_uc(df, uc) else 0
        transfer_counts.append({'UC Name': uc, 'counts': can_transfer})
    
    transfer_counts_df = pd.DataFrame(transfer_counts)
    return college_name, transfer_counts_df

def analyze_all_colleges(directory):
    all_data = []
    
    # Process all CSV files in the directory
    for file in os.listdir(directory):
        if file.endswith('_filtered.csv'):
            file_path = os.path.join(directory, file)
            college_name, transfer_counts = count_transfer_options(file_path)
            
            # Remove underscores and replace with spaces
            college_name = college_name.replace('_', ' ')
            
            # Add college name to each row
            transfer_counts['College'] = college_name
            all_data.append(transfer_counts)
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def create_heatmap(data):
    # Pivot the data for the heatmap
    heatmap_data = data.pivot(index='College', columns='UC Name', values='counts')
    
    # Create a figure with larger size
    plt.figure(figsize=(10, 30))  # Increased height to accommodate all colleges
    
    # Create heatmap with a different colormap to emphasize binary nature
    sns.heatmap(heatmap_data, annot=True, cmap='RdYlGn', cbar=False, fmt='g', vmin=0, vmax=1, linewidths=1, linecolor='black')
    plt.title('Valid Transfer Paths to UCs\n(1=All courses articulated, 0=Some courses not articulated)', pad=20)
    plt.ylabel('Community College')
    plt.xlabel('UC Campus')
    
    # Rotate x-axis labels and adjust their position
    plt.xticks(rotation=30, ha='right')
    # Keep y-axis labels horizontal for better readability
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    # Save to the same directory as the script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'transfer_availability_heatmap.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_bar_plot(data):
    # Calculate total transfer options per college
    total_options = data.groupby('College')['counts'].sum().sort_values()
    
    # Create bar plot with increased figure size for better label spacing
    plt.figure(figsize=(20, 10))
    ax = total_options.plot(kind='bar')
    plt.title('Number of Valid UC Transfer Paths by Community College')
    plt.xlabel('Community College')
    plt.ylabel('Number of UCs with All Courses Articulated')
    
    # Rotate x-axis labels and adjust their position
    plt.xticks(rotation=90, ha='center')
    
    # Adjust layout to prevent label cutoff
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    # Save to the same directory as the script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'total_transfer_availability.png')
    plt.savefig(output_path)
    plt.close()

def main():
    # Directory containing the filtered CSV files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.normpath(os.path.join(script_dir, '../../filtered_results'))
    
    # Analyze all colleges
    combined_data = analyze_all_colleges(directory)
    
    # Create visualizations
    create_heatmap(combined_data)
    create_bar_plot(combined_data)
    
    # Find college with fewest options
    # total_options = combined_data.groupby('College')['counts'].sum()
    # min_college = total_options.idxmin()
    # min_count = total_options.min()
    
    # print(f"\nCollege with fewest valid UC transfer paths: {min_college}")
    # print(f"Number of UCs with all courses articulated: {min_count}")
    
    # # Show which UCs have all courses articulated for the college with fewest options
    # college_data = combined_data[combined_data['College'] == min_college]
    # available_ucs = college_data[college_data['counts'] == 1]['UC Name'].tolist()
    # print(f"\nUCs with all courses articulated:")
    # for uc in available_ucs:
    #     print(f"- {uc}")

if __name__ == "__main__":
    main()