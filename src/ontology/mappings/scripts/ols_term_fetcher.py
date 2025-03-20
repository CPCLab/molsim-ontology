#!/usr/bin/env python3
"""
OLS Term URI Fetcher

This script fetches URIs for ontology terms from the EBI Ontology Lookup Service.
It takes an ontology ID and a text file with terms as input and produces a CSV file
with the terms and their corresponding URIs.

Usage:
    python ols_term_fetcher.py <ontology_id> <input_file> <output_file>

Example:
    python ols_term_fetcher.py CHEBI terms.txt output.csv
"""

import sys
import csv
import requests
import time
from typing import Dict, List, Tuple, Optional


def fetch_term_uri(term: str, ontology_id: str) -> Optional[str]:
    """
    Fetch the URI for a given term from the specified ontology.
    
    Args:
        term: The term to search for
        ontology_id: The ontology ID (e.g., CHEBI)
        
    Returns:
        The URI of the term if found, None otherwise
    """
    # Base URL for the OLS API
    base_url = "https://www.ebi.ac.uk/ols/api/search"
    
    # Parameters for the API request
    params = {
        "q": term,
        "ontology": ontology_id,
        "exact": "false"
    }
    
    try:
        # Make the request to the OLS API
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # Check if any results were found
        if data["response"]["numFound"] > 0:
            # Get the first result (most relevant match)
            result = data["response"]["docs"][0]
            return result.get("iri")
        else:
            print(f"No match found for term: {term}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URI for term '{term}': {e}")
        return None


def process_terms(ontology_id: str, input_file: str, output_file: str) -> None:
    """
    Process a list of terms from an input file and write the results to a CSV file.
    
    Args:
        ontology_id: The ontology ID (e.g., CHEBI)
        input_file: Path to the input file containing terms (one per line)
        output_file: Path to the output CSV file
    """
    terms = []
    
    # Read terms from the input file
    try:
        with open(input_file, 'r') as f:
            terms = [line.strip() for line in f if line.strip()]
    except IOError as e:
        print(f"Error reading input file: {e}")
        sys.exit(1)
    
    results = []
    
    # Process each term
    for term in terms:
        uri = fetch_term_uri(term, ontology_id)
        results.append((term, uri))
        
        # Add a small delay to avoid overwhelming the API
        time.sleep(0.5)
    
    # Write results to the output CSV file
    try:
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Term", "URI"])
            for term, uri in results:
                writer.writerow([term, uri])
        
        print(f"Results written to {output_file}")
    except IOError as e:
        print(f"Error writing to output file: {e}")
        sys.exit(1)


def main():
    """Main function to handle command line arguments and run the script."""
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <ontology_id> <input_file> <output_file>")
        sys.exit(1)
    
    ontology_id = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    process_terms(ontology_id, input_file, output_file)


if __name__ == "__main__":
    main()
