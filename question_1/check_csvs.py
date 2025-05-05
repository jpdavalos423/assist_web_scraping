import pandas as pd
import os

def check_csv_columns(folder_path):
    required_columns = {"UC Name", "Group ID", "Set ID", "Num Required", "Receiving", "Courses Group 1"}
    all_files = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

    print("🔍 Checking CSVs in folder...\n")

    for file_name in all_files:
        file_path = os.path.join(folder_path, file_name)
        try:
            df = pd.read_csv(file_path)
            present_cols = set(df.columns.str.strip())

            missing = required_columns - present_cols
            if not missing:
                print(f"✅ {file_name}: All required columns present.")
            else:
                print(f"❌ {file_name}: Missing columns: {', '.join(sorted(missing))}")
        except Exception as e:
            print(f"⚠️ {file_name}: Failed to read. Error: {e}")

if __name__ == "__main__":
    folder_path = input("Enter the path to the folder of CSV files: ")
    check_csv_columns(folder_path)
