import pandas as pd
import os
import re  # Import regex module

# Define the folder path where the CSV files are located
folder_path = '../data/data_prep/34070DO003_202223/'  # Adjust path as needed

# Initialize a list to store dataframes from all CSV files
data_frames = []

# Map file suffix to territory names
territory_mapping = {
    '1': 'Australia',
    '2': 'New South Wales',
    '3': 'Victoria',
    '4': 'Queensland',
    '5': 'South Australia',
    '6': 'Western Australia',
    '7': 'Tasmania',
    '8': 'Northern Territory',
    '9': 'Australian Capital Territory'
}

# Function to clean column names by removing parentheses and content inside them
def clean_column_names(columns):
    return [re.sub(r'\(.*?\)', '', col).strip() for col in columns]

# Iterate over all files in the folder
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        # Extract the territory code from the filename (e.g., .1.csv -> '1')
        suffix = file_name.split('.')[-2]

        # Get the corresponding territory name from the mapping
        territory = territory_mapping.get(suffix, 'Unknown')

        # Read each CSV into a DataFrame
        df = pd.read_csv(os.path.join(folder_path, file_name))

        # Clean column names
        df.columns = clean_column_names(df.columns)

        # Add a 'Territory' column to the DataFrame
        df['Territory'] = territory

        # Show the cleaned column names and the added 'Territory' column
        print(f"Loaded data for {territory}")
        print(df.columns)
        print("\n\n\n")

        # Store the DataFrame for further analysis
        data_frames.append(df)

# Combine all DataFrames into one and save to a new CSV
combined_df = pd.concat(data_frames, ignore_index=True)
combined_df.to_csv('cleaned_departures_data.csv', index=False)

print("Data cleaned, combined, and saved successfully.")
