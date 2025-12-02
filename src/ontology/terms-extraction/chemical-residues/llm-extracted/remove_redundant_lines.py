import pandas as pd
import sys
import os

def remove_redundant_rows(input_file, output_file):
    # check if file exists
    if not os.path.exists(input_file):
        print(f"Error: The file '{input_file}' was not found.")
        return

    try:
        # Read the CSV file
        df = pd.read_csv(input_file)

        # Define the columns that determine redundancy
        subset_columns = [
            'AMBER Residue Name',
            'Likely ChEBI Entity',
            'Actual CHEBI Label',
            'Synonyms',
            'ChEBI IRI'
        ]

        # Check if these columns actually exist in the file to prevent errors
        missing_cols = [col for col in subset_columns if col not in df.columns]
        if missing_cols:
            print(f"Error: The following columns are missing from the CSV: {missing_cols}")
            return

        # Calculate original count
        original_count = len(df)

        # Drop duplicates based ONLY on the subset columns
        # keep='first' keeps the first occurrence and removes subsequent ones
        df_cleaned = df.drop_duplicates(subset=subset_columns, keep='first')

        # Calculate removed count
        removed_count = original_count - len(df_cleaned)

        # Save to new CSV
        df_cleaned.to_csv(output_file, index=False)

        print(f"Process complete.")
        print(f"Original rows: {original_count}")
        print(f"Redundant rows removed: {removed_count}")
        print(f"Saved to: {output_file}")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    # You can change these filenames as needed
    input_csv = 'amber-residues-gmpro-3.0_updated_edit.csv' # Or whatever your file is named
    output_csv = 'amber-residues-gmpro-3.0_updated_edit_non-redundant.csv'
    
    remove_redundant_rows(input_csv, output_csv)