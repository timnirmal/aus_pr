import pandas as pd
import os

# Load the Excel file (replace 'your_file.xlsx' with your actual file path)
excel_file = '34070DO004_202223.xlsx'

# Create a folder with the name of the Excel file (without extension)
folder_name = excel_file.split(".")[0]
os.makedirs(folder_name, exist_ok=True)

# Read the Excel file with all sheets
sheets = pd.ExcelFile(excel_file)

# Loop through each sheet and save it as a CSV file in its corresponding subfolder
for sheet_name in sheets.sheet_names:
    # # Create a subfolder for each sheet
    # sheet_folder = os.path.join(folder_name, sheet_name)
    # os.makedirs(sheet_folder, exist_ok=True)

    # Read the sheet into a DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Save the DataFrame to a CSV file in the subfolder
    csv_filename = os.path.join(folder_name, f"{sheet_name}.csv")
    df.to_csv(csv_filename, index=False)

    print(f"Saved {csv_filename}")
