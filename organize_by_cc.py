import os
from collections import defaultdict

# Directories
input_directory = "cs_urls"  # Directory containing UC text files
output_directory = "cc_agreements"  # Main output folder for community colleges

# Ensure the output directory exists
os.makedirs(output_directory, exist_ok=True)

# Dictionary to store agreements for each community college
cc_data = defaultdict(dict)

def process_uc_file(file_path, uc_name):
    """Reads a UC agreement file and organizes data into a dictionary."""
    with open(file_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            parts = line.strip().split("https://")
            if len(parts) == 2:
                college_name = parts[0].strip()  # Extract community college name
                url = "https://" + parts[1].strip()  # Extract URL
                
                # Store data in dictionary (college_name -> { uc_name -> url })
                cc_data[college_name][uc_name] = url

# Process each UC file in the input directory
for filename in os.listdir(input_directory):
    if filename.endswith(".txt"):
        uc_name = filename.replace("cs_urls_", "").replace(".txt", "").replace("_", " ")  # Extract UC name
        input_path = os.path.join(input_directory, filename)

        print(f"Processing {filename} for {uc_name}...")

        process_uc_file(input_path, uc_name)

# Write sorted agreements to files
for college_name, uc_links in cc_data.items():
    # Format folder-safe college name
    safe_college_name = college_name.replace(" ", "_").replace("/", "-")

    # Create a directory for this community college
    college_folder = os.path.join(output_directory, safe_college_name)
    os.makedirs(college_folder, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(college_folder, "agreements.txt")

    # Sort UC agreements alphabetically
    sorted_uc_links = sorted(uc_links.items())  # Sort by UC name

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for uc_name, url in sorted_uc_links:
            outfile.write(f"{uc_name}: {url}\n")

print("✅ All files processed successfully, with URLs sorted alphabetically by UC!")
