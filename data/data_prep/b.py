import pandas as pd
import os

# Load the Excel file
excel_file = '34070DO004_202223.xlsx'

# Create a folder with the name of the Excel file (without extension)
folder_name = excel_file.split(".")[0]
folder_name = folder_name + "_cleaned"
os.makedirs(folder_name, exist_ok=True)

# Read the Excel file with all sheets
sheets = pd.ExcelFile(excel_file)

# Loop through all sheets to process the data
for sheet_name in sheets.sheet_names:
    print(f"Processing sheet: {sheet_name}")

    # Read the current sheet into a DataFrame
    df = pd.read_excel(excel_file, sheet_name=sheet_name)

    # Clean the data by forward-filling empty cells (if needed)
    df = df.ffill(axis=0)

    # Create an empty list to store the cleaned data for this sheet
    data = []

    # Variables to keep track of the current direction and visa group
    current_direction = None
    current_visa_group = None

    # Loop through rows to extract meaningful data
    for index, row in df.iterrows():
        if pd.notna(row[0]):  # If 'Direction' is present in the first column
            current_direction = row[0]  # Update the direction

        if pd.notna(row[1]):  # If a new 'Visa Group' is defined
            current_visa_group = row[1]  # Update the visa group

        # Extract visa type and year-wise counts
        visa_type = row[1] if pd.notna(row[1]) else None  # Visa type from column 2
        for year in df.columns[2:]:  # Loop through all year columns
            count = row[year]
            data.append([sheet_name, current_direction, current_visa_group, visa_type, year, count])

    # Convert the collected data into a DataFrame
    cleaned_df = pd.DataFrame(data, columns=[
        'Sheet', 'Direction', 'Visa Group', 'Visa Type', 'Year', 'Count'
    ])

    # Save the cleaned DataFrame as a CSV in the main folder
    cleaned_csv_path = os.path.join(folder_name, f"{sheet_name}_cleaned.csv")
    cleaned_df.to_csv(cleaned_csv_path, index=False)

    print(f"Saved cleaned data for {sheet_name} to {cleaned_csv_path}")
