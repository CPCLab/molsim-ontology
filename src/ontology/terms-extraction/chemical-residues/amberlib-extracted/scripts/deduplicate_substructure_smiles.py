import pandas as pd

def remove_redundant_smiles(input_file, output_file):
    """
    Reads a CSV file, removes rows with duplicate Fragment_SMILES,
    and saves the result to a new CSV file.
    """
    try:
        # 1. Read the CSV file
        df = pd.read_csv(input_file)
        print(f"Original row count: {len(df)}")

        # 2. Drop duplicates based on 'Fragment_SMILES'
        # keep='first' retains the first instance found and discards the others
        df_distinct = df.drop_duplicates(subset=['Fragment_SMILES'], keep='first')
        
        # Calculate how many were removed
        removed_count = len(df) - len(df_distinct)
        print(f"Removed {removed_count} redundant rows.")
        print(f"Final distinct row count: {len(df_distinct)}")

        # 3. Save the cleaned data to a new CSV
        df_distinct.to_csv(output_file, index=False)
        print(f"Cleaned data saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- Usage ---
if __name__ == "__main__":
    # Replace with your actual file name if different
    input_csv = 'mol2_smiles_chebiandpubchem.csv'
    output_csv = 'distinct_smiles_chemical_entities.csv'
    
    remove_redundant_smiles(input_csv, output_csv)