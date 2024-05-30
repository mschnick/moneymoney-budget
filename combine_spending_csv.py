import os
import sys
import pandas as pd

def parse_csv(file_path, month):
    data = pd.read_csv(file_path, delimiter=';', header=None, names=['Kategorie', 'Value', 'Currency'])
    data = data.dropna(how='all')  # Remove rows where all elements are NaN
    
    # Create a new DataFrame to store parsed data
    parsed_data = pd.DataFrame(columns=['Category', month])
    
    # Extract data for each category
    category = None
    for index, row in data.iterrows():
        if pd.notna(row['Kategorie']) and pd.isna(row['Value']):
            category = row['Kategorie'].strip()
        elif pd.notna(row['Kategorie']) and pd.notna(row['Value']):
            subcategory = row['Kategorie'].strip()
            amount = row['Value'].replace(',', '.').strip()
            amount = float(amount) if amount else 0.0
            if category:
                full_category = f"{category} - {subcategory}"
                parsed_data = pd.concat([parsed_data, pd.DataFrame({'Category': [full_category], month: [amount]})])
            else:
                parsed_data = pd.concat([parsed_data, pd.DataFrame({'Category': [subcategory], month: [amount]})])
    
    return parsed_data.reset_index(drop=True)

def combine_csv_files(directory, year):
    combined_data = pd.DataFrame(columns=['Category'])
    months = [f"{year}-{str(month).zfill(2)}" for month in range(1, 13)]

    # Print the contents of the directory to verify the files are there
    print(f"Searching for files in directory: {os.path.abspath(directory)}")
    print(f"Contents of directory {directory}:")
    print(os.listdir(directory))
    
    for month in months:
        month_filename = f"Kategorien-{month}.csv"
        file_path = os.path.join(directory, month_filename)
        if os.path.exists(file_path):
            print(f"Processing file: {file_path}")
            monthly_data = parse_csv(file_path, month)
            print(f"Monthly data for {month}:\n", monthly_data.head())
            combined_data = pd.merge(combined_data, monthly_data, on='Category', how='outer')
        else:
            print(f"File not found for {month}: Adding empty column.")
            combined_data[month] = pd.NA
    
    combined_data = combined_data.fillna(0)
    combined_data = combined_data.sort_values(by='Category').reset_index(drop=True)
    
    return combined_data

def main(directory, year):
    combined_data = combine_csv_files(directory, year)
    output_filename = f'combined_spending_{year}.csv'
    combined_data.to_csv(output_filename, index=False, sep=';')
    print(f"Combined data saved to {output_filename}")

def print_help():
    print("Usage: python combine_spending_csv.py [OPTIONS]")
    print("Options:")
    print("  --directory DIR   Specify the directory containing the CSV files")
    print("  --year YEAR       Specify the year to process")
    print("  --help            Show this help message and exit")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--directory', type=str, default='.', help='Directory containing the CSV files')
    parser.add_argument('--year', type=str, required=True, help='Year to process')
    parser.add_argument('--help', action='store_true', help='Show this help message and exit')
    args = parser.parse_args()

    if args.help:
        print_help()
        sys.exit(0)

    directory = args.directory
    year = args.year

    main(directory, year)
