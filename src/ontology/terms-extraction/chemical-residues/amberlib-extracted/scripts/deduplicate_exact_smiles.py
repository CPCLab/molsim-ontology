import pandas as pd

def deduplicate_exact_smiles(input_file, output_file):
    """
    Deduplicates a CSV file based on Canon_SMILES. 
    Falls back to Raw_SMILES if Canon_SMILES is missing.
    """
    try:
        # 1. Read the CSV file
        df = pd.read_csv(input_file)
        print(f"Original row count: {len(df)}")

        # 2. Create a reliable key for deduplication
        # We prefer 'Canon_SMILES' as it is normalized. 
        # If that's missing (NaN), we use 'Raw_SMILES'.
        df['dedup_key'] = df['Canon_SMILES'].fillna(df['Raw_SMILES'])
        
        # 3. Drop duplicates
        # keep='first' retains the first occurrence
        df_distinct = df.drop_duplicates(subset=['dedup_key'], keep='first')
        
        # Remove the helper column
        df_distinct = df_distinct.drop(columns=['dedup_key'])

        # Calculate stats
        removed_count = len(df) - len(df_distinct)
        print(f"Removed {removed_count} redundant rows.")
        print(f"Final distinct row count: {len(df_distinct)}")

        # 4. Save to new CSV
        df_distinct.to_csv(output_file, index=False)
        print(f"Cleaned data saved to: {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")

# --- Usage ---
if __name__ == "__main__":
    input_csv = 'exact_smiles_unique-hash.csv'
    output_csv = 'distinct_chemical_entities_exact_smiles.csv'
    
    deduplicate_exact_smiles(input_csv, output_csv)