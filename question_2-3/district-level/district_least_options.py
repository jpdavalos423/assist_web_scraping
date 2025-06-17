import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def can_transfer_to_uc(df, uc_name):
    # Get all requirements for this UC
    uc_requirements = df[df['UC Name'] == uc_name]
    
    # Group requirements by Group ID
    grouped_requirements = uc_requirements.groupby('Group ID')
    
    for group_id, group_df in grouped_requirements:
        # Get unique Set IDs for this group
        set_ids = group_df['Set ID'].unique()
        
        # If there's only one Set ID, all courses in the group must be articulated
        if len(set_ids) == 1:
            for _, row in group_df.iterrows():
                if row['College Name'] == 'Not Articulated':
                    return False
                # Check all course groups for "Not Articulated"
                for col in [col for col in df.columns if col.startswith('Courses Group')]:
                    if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                        return False
        else:
            # For multiple Set IDs, at least one set must be fully articulated
            valid_set_found = False
            for set_id in set_ids:
                set_df = group_df[group_df['Set ID'] == set_id]
                set_valid = True
                
                for _, row in set_df.iterrows():
                    if row['College Name'] == 'Not Articulated':
                        set_valid = False
                        break
                    # Check all course groups for "Not Articulated"
                    for col in [col for col in df.columns if col.startswith('Courses Group')]:
                        if pd.notna(row[col]) and 'Not Articulated' in str(row[col]):
                            set_valid = False
                            break
                    if not set_valid:
                        break
                
                if set_valid:
                    valid_set_found = True
                    break
            
            if not valid_set_found:
                return False
    
    return True

def count_transfer_options(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Get district name from file path
    district_name = os.path.basename(file_path).replace('.csv', '').replace('_', ' ')
    
    # Get unique UCs
    unique_ucs = df['UC Name'].unique()
    
    # Count UCs where all requirements can be satisfied (no "Not Articulated" courses)
    transfer_counts = []
    for uc in unique_ucs:
        can_transfer = 1 if can_transfer_to_uc(df, uc) else 0
        transfer_counts.append({'UC Name': uc, 'counts': can_transfer})
    
    transfer_counts_df = pd.DataFrame(transfer_counts)
    return district_name, transfer_counts_df

def analyze_all_districts(directory):
    all_data = []
    
    # Process all CSV files in the directory
    for file in os.listdir(directory):
        if file.endswith('.csv'):
            file_path = os.path.join(directory, file)
            district_name, transfer_counts = count_transfer_options(file_path)
            
            # Add district name to each row
            transfer_counts['District'] = district_name
            all_data.append(transfer_counts)
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def create_bar_plot(data):
    # Calculate total transfer options per district
    total_options = data.groupby('District')['counts'].sum().sort_values()
    
    # Create bar plot with increased figure size for better label spacing
    plt.figure(figsize=(20, 10))
    ax = total_options.plot(kind='bar')
    plt.title('Number of Valid UC Transfer Paths by Community College District')
    plt.xlabel('Community College District')
    plt.ylabel('Number of UCs with All Courses Articulated')
    
    # Rotate x-axis labels and adjust their position
    plt.xticks(rotation=90, ha='center')
    
    # Adjust layout to prevent label cutoff
    plt.subplots_adjust(bottom=0.2)
    plt.tight_layout()
    # Save to the same directory as the script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'district_total_transfer_availability.png')
    plt.savefig(output_path)
    plt.close()

def create_simple_bar_plot(data):
    """
    Creates a simplified bar plot showing the distribution of how many UCs
    each district has complete articulation with.
    """
    # Calculate how many UCs each district has complete articulation with
    district_complete_counts = {}
    for district in data['District'].unique():
        district_data = data[data['District'] == district]
        complete_count = sum(district_data['counts'])
        district_complete_counts[district] = complete_count
    
    # Count frequency of each number of complete articulations (0-9 UCs)
    frequency = {i: 0 for i in range(10)}  # 0 to 9 UCs
    for count in district_complete_counts.values():
        frequency[count] += 1
    
    # Create bar plot
    plt.figure(figsize=(12, 6))
    x = list(frequency.keys())
    y = list(frequency.values())
    
    bars = plt.bar(x, y)
    
    # Add value labels on top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.title('Distribution of Complete UC Articulations per District')
    plt.xlabel('Number of UCs with Complete Articulation')
    plt.ylabel('Number of Districts')
    plt.xticks(range(10))
    
    # Save the plot
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'district_simple_total_transfer_availability.png'
    )
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_horizontal_heatmap(data):
    # Pivot the data for the heatmap - swap index and columns
    heatmap_data = data.pivot(index='UC Name', columns='District', values='counts')
    
    # Set font sizes
    # plt.rcParams.update({'font.size': 22})  # Increase base font size
    # Create a figure with adjusted size for flipped axes
    plt.figure(figsize=(40, 25))  # Swapped dimensions
    
    # Create heatmap with a different colormap to emphasize binary nature
    sns.heatmap(heatmap_data, annot=False, cbar=False, cmap='RdYlGn', fmt='g', vmin=0, vmax=1, linewidths=1, linecolor='black', square=True)
    plt.title('Valid Transfer Paths to UCs by District\n(Green=All courses articulated, Red=Some courses not articulated)', pad=20, fontsize=20)
    plt.ylabel('UC Campus', fontsize=30)  # Swapped labels
    plt.xlabel('Community College District', fontsize=30)
    
    # Adjust rotation for the new axis orientation
    plt.xticks(rotation=90, ha='center', fontsize=20)
    plt.yticks(rotation=0, fontsize=20)
    
    plt.tight_layout()
    # Save to the same directory as the script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'district_transfer_availability_horizontal_heatmap.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_vertical_heatmap(data):
    # Pivot the data for the heatmap
    heatmap_data = data.pivot(index='District', columns='UC Name', values='counts')
    
    # Create a figure with larger size
    plt.figure(figsize=(15, 30))  # Increased height to accommodate all districts
    plt.rcParams.update({'font.size': 18})  # Increase base font size
    
    # Create heatmap with a different colormap to emphasize binary nature
    sns.heatmap(heatmap_data, annot=False, cbar=False, cmap='RdYlGn', fmt='g', vmin=0, vmax=1, linewidths=1, linecolor='black')
    plt.title('Valid Transfer Paths to UCs by District\n(1=All courses articulated, 0=Some courses not articulated)', pad=20)
    plt.ylabel('Community College District')
    plt.xlabel('UC Campus')
    
    # Rotate x-axis labels and adjust their position
    plt.xticks(rotation=30, ha='right')
    # Keep y-axis labels horizontal for better readability
    plt.yticks(rotation=0)
    
    plt.tight_layout()
    # Save to the same directory as the script
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'district_transfer_availability_vertical_heatmap.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
def main():
    # Directory containing the district CSV files
    script_dir = os.path.dirname(os.path.abspath(__file__))
    directory = os.path.normpath(os.path.join(script_dir, '../../district_csvs'))
    
    # Analyze all districts
    combined_data = analyze_all_districts(directory)
    
    # Create visualizations
    
    create_bar_plot(combined_data)
    
    create_simple_bar_plot(combined_data)

    create_horizontal_heatmap(combined_data)

    create_vertical_heatmap(combined_data)

if __name__ == "__main__":
    main()