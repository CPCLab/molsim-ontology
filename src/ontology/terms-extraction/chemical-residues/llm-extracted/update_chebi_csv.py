import csv
import requests
import argparse
import os
from urllib.parse import quote
import time

def fetch_chebi_details(chebi_iri):
    """
    Fetches the label and synonyms for a given ChEBI IRI from the OLS API.

    Args:
        chebi_iri (str): The full ChEBI IRI (e.g., "http://purl.obolibrary.org/obo/CHEBI_50320").

    Returns:
        tuple: A tuple containing the label (str) and a comma-separated list of synonyms (str).
               Returns (None, None) if the request fails or the term is not found.
    """
    if not chebi_iri:
        return None, None

    # The OLS API requires the IRI to be double URL encoded.
    encoded_iri = quote(quote(chebi_iri, safe=''), safe='')
    
    # Construct the API URL
    api_url = f"https://www.ebi.ac.uk/ols/api/ontologies/chebi/terms/{encoded_iri}"
    
    try:
        response = requests.get(api_url, timeout=10)
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        data = response.json()
        
        label = data.get("label", "")
        synonyms = ", ".join(data.get("synonyms", []))
        
        return label, synonyms
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            print(f"Warning: ChEBI term not found for IRI {chebi_iri}")
        else:
            print(f"HTTP Error for {chebi_iri}: {e}")
        return None, None
    except requests.exceptions.RequestException as e:
        print(f"Request failed for {chebi_iri}: {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred for {chebi_iri}: {e}")
        return None, None

def process_csv(input_file_path, output_file_path):
    """
    Reads a CSV file, adds ChEBI labels and synonyms by querying the OLS API,
    and writes to a new CSV file.
    """
    print(f"Starting processing for {input_file_path}...")
    try:
        with open(input_file_path, 'r', newline='', encoding='utf-8') as infile, \
             open(output_file_path, 'w', newline='', encoding='utf-8') as outfile:

            reader = csv.reader(infile)
            writer = csv.writer(outfile)

            # Read the header and write the new header to the output file
            try:
                header = next(reader)
                writer.writerow(header + ["Actual CHEBI Label", "Synonyms"])
            except StopIteration:
                print("Error: Input CSV file is empty.")
                return

            # Process each row
            for i, row in enumerate(reader):
                # Assuming the ChEBI IRI is in the 5th column (index 4)
                if len(row) > 4:
                    chebi_iri = row[4]
                    print(f"Processing row {i+1}: Fetching data for {chebi_iri}...")
                    label, synonyms = fetch_chebi_details(chebi_iri)
                    
                    # Add a small delay to be respectful to the API server
                    time.sleep(0.1) 
                    
                    writer.writerow(row + [label or "", synonyms or ""])
                else:
                    # Handle rows that are too short
                    writer.writerow(row + ["", ""])
                    
        print(f"\nProcessing complete. Output saved to {output_file_path}")

    except FileNotFoundError:
        print(f"Error: The file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred during file processing: {e}")

def main():
    """
    Main function to parse command-line arguments and initiate CSV processing.
    """
    parser = argparse.ArgumentParser(
        description="Fetch ChEBI labels and synonyms from the OLS API and add them to a CSV file.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_file",
        help="The path to the input CSV file."
    )
    parser.add_argument(
        "-o", "--output_file",
        help="The path for the output CSV file.\nIf not provided, it defaults to 'input_file_updated.csv'."
    )

    args = parser.parse_args()

    # Determine the output file path
    if args.output_file:
        output_file_path = args.output_file
    else:
        base, ext = os.path.splitext(args.input_file)
        output_file_path = f"{base}_updated{ext}"

    process_csv(args.input_file, output_file_path)

if __name__ == "__main__":
    main()