#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CSV Duplicate Reordering Script for Ontology Terms

This script reads a CSV file (such as the output from the term_verifier),
identifies rows with duplicate values in the 'Term' or 'Variable' columns
(case-insensitively), and reorders the file to group these duplicates together
at the top.

The output CSV will have:
1. All rows that are part of a duplicate group listed first.
2. Within the duplicates, rows are grouped by their common term/variable.
3. All rows with unique Term/Variable values are listed at the end.

Usage:
    python reorder_duplicates.py <path_to_input_csv>

Example:
    python reorder_duplicates.py verified_ontology_terms.csv
"""

import csv
import sys
import os
import collections
from typing import List, Dict, Set

def get_grouping_key(row: Dict[str, str], duplicate_keys: Set[str]) -> str:
    """
    Determines the primary sorting key for a row that is part of a duplicate group.

    It checks the 'Term' and 'Variable' (lower-cased) against the set of
    known duplicate keys and returns the first one it finds. This ensures that
    all rows sharing a common duplicate term get the same sorting key.

    Args:
        row: A dictionary representing a row from the CSV.
        duplicate_keys: A set of lower-cased strings known to be duplicates.

    Returns:
        The lower-cased duplicate string to be used for grouping.
    """
    term_lower = row.get('Term', '').lower().strip()
    if term_lower in duplicate_keys:
        return term_lower

    var_lower = row.get('Variable', '').lower().strip()
    if var_lower in duplicate_keys:
        return var_lower
    
    # This fallback should ideally not be reached for rows in the duplicate list,
    # but it provides a stable sort key just in case.
    return term_lower

def reorder_csv_by_duplicates(input_path: str, output_path: str) -> None:
    """
    Reads a CSV, finds duplicates in 'Term'/'Variable' columns, and writes a
    reordered CSV with duplicate groups at the top.
    
    Args:
        input_path: The path to the source CSV file.
        output_path: The path where the reordered CSV will be saved.
    """
    # --- Step 1: Read the CSV data into memory ---
    print(f"Reading data from '{input_path}'...")
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            header = reader.fieldnames
            if not header or 'Term' not in header or 'Variable' not in header:
                print("Error: CSV must contain a header with 'Term' and 'Variable' columns.", file=sys.stderr)
                sys.exit(1)
            data = list(reader)
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    if not data:
        print("Input file is empty. Nothing to do.")
        return

    # --- Step 2: Count frequencies of all terms and variables (case-insensitive) ---
    term_counts = collections.Counter()
    for row in data:
        # Get unique, non-empty, lowercased terms from the row
        row_values = {
            val.lower().strip() for val in [row.get('Term'), row.get('Variable')] if val and val.strip()
        }
        # Update the master counter with the values from this row
        term_counts.update(row_values)

    # --- Step 3: Identify all keys that are duplicates ---
    duplicate_keys = {key for key, count in term_counts.items() if count > 1}
    print(f"Found {len(duplicate_keys)} unique terms/variables that appear in multiple rows.")

    if not duplicate_keys:
        print("No duplicates found. Output file will be a copy of the input.")
        # If no duplicates, we can simply write the original data back
        # For simplicity, we let the logic continue, and it will correctly
        # place all rows in `unique_rows` and write them out.

    # --- Step 4: Partition data into duplicate and unique rows ---
    duplicate_rows = []
    unique_rows = []
    for row in data:
        term_lower = row.get('Term', '').lower().strip()
        var_lower = row.get('Variable', '').lower().strip()
        
        if term_lower in duplicate_keys or var_lower in duplicate_keys:
            duplicate_rows.append(row)
        else:
            unique_rows.append(row)
            
    print(f"Categorized {len(duplicate_rows)} rows as part of a duplicate group and {len(unique_rows)} as unique.")

    # --- Step 5: Sort the duplicate rows to group them together ---
    # The key is a tuple for multi-level sorting:
    # 1. Primary sort: by the grouping key (e.g., 'pymol').
    # 2. Secondary sort: by the original 'Term' value for stable ordering within a group.
    # 3. Tertiary sort: by the original 'Variable' value.
    duplicate_rows.sort(key=lambda row: (
        get_grouping_key(row, duplicate_keys),
        row.get('Term', ''),
        row.get('Variable', '')
    ))

    # --- Step 6: Combine the lists and write to the output file ---
    final_data = duplicate_rows + unique_rows
    
    print(f"Writing reordered data to '{output_path}'...")
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(final_data)
    except IOError as e:
        print(f"Error writing to output file '{output_path}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nReordering complete!")
    print(f"Output successfully saved to '{output_path}'")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python reorder_duplicates.py <path_to_input_csv>", file=sys.stderr)
        sys.exit(1)

    input_csv_path = sys.argv[1]
    
    # Generate a descriptive output filename
    base_name = os.path.basename(input_csv_path)
    name, ext = os.path.splitext(base_name)
    output_csv_path = f"{name}_reordered{ext}"

    reorder_csv_by_duplicates(input_csv_path, output_csv_path)