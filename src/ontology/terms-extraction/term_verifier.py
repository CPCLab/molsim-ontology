#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ontology Term Verifier for Biomolecular Simulation Manuals (v4 - Final)

This script verifies the occurrence of ontology terms within large text files,
such as simulation software manuals. It reads terms from a structured CSV file,
searches for them in the target manual, and outputs an annotated CSV with
occurrence counts and line numbers.

Version 4 Fixes:
- **CRITICAL FIX**: Replaced the faulty `re.sub` logic in `create_regex_pattern`
  with simple and reliable `string.replace()` calls. This permanently resolves the
  'bad escape \s' error and ensures that valid regex patterns are generated
  for ALL terms, simple or complex.
- The new regex generation is now much clearer, more robust, and less prone to
  subtle escaping errors.

Key Features:
- Efficiently processes large files (250k+ lines) with a single-pass approach.
- Searches for both a human-readable 'Term' and a technical 'Variable'.
- Performs case-insensitive matching.
- Handles special characters, multi-word terms, and terms spanning line breaks.
- Uses a bisect algorithm for rapid conversion of match offsets to line numbers.
- Limits line number reporting for high-frequency terms to maintain readability.

Usage:
    python term_verifier_fixed_v3.py <path_to_ontology_csv> <path_to_manual_txt>

Example:
    python term_verifier_fixed_v3.py ontology_terms.csv gromacs_manual.txt
"""

import csv
import sys
import re
import bisect
import os
from typing import List, Dict, Any

# --- Configuration ---
# Maximum number of line numbers to report for any single term.
MAX_LINE_NUMBERS_TO_REPORT = 100

def create_regex_pattern(term_string: str) -> str:
    """
    Creates a robust, case-insensitive regex pattern for a given term.

    This function has been corrected to use simple string replacement, which is
    a reliable and clear way to construct the final regex pattern.

    1.  **Escaping**: Escapes the term to treat special characters as literals.
    2.  **Flexible Whitespace**: Replaces spaces with `\s+` to handle multiple
        whitespace characters, including newlines.
    3.  **Optional Whitespace around Brackets (FIXED)**: Uses direct and simple
        `string.replace()` calls to make whitespace around parentheses and brackets
        optional. This is the most robust way to achieve this and avoids all
        previous `re.sub` related bugs.
    4.  **Robust Word Boundaries**: Uses `(?<!\w)` and `(?!\w)` (negative lookarounds)
        to ensure whole-word matching.

    Args:
        term_string: The string term to be converted into a regex pattern.

    Returns:
        A string representing the regex pattern to be compiled.
    """
    if not term_string:
        return ""
    term = term_string.strip()
    if not term:
        return ""

    # 1. Escape the entire term to handle all special characters literally
    pattern = re.escape(term)

    # 2. Replace escaped spaces with flexible whitespace `\s+`
    pattern = pattern.replace(r'\ ', r'\s+')

    # 3. FIX: Use simple string replacement to make whitespace around brackets optional.
    # This is much safer and clearer than using re.sub on a regex string.
    # Example: 'number\s+\(cn\)' becomes 'number\s*\(cn\)'
    pattern = pattern.replace(r'\s+\(', r'\s*\(') # Before opening parenthesis
    pattern = pattern.replace(r'\)\s+', r'\)\s*') # After closing parenthesis
    pattern = pattern.replace(r'\s+\[', r'\s*\[') # Before opening bracket
    pattern = pattern.replace(r'\]\s+', r'\]\s*') # After closing bracket

    # 4. Use robust word boundaries to ensure whole-word matching
    return r'(?<!\w)' + pattern + r'(?!\w)'


def build_newline_index(text_content: str) -> List[int]:
    """
    Creates an index of the starting character offset of each line for fast lookups.
    """
    print("Building line number index for efficient lookups...")
    index = [0]
    for match in re.finditer(r'\n', text_content):
        index.append(match.start() + 1)
    print(f"Index built for {len(index)} lines.")
    return index

def offset_to_line_number(offset: int, newline_index: List[int]) -> int:
    """
    Converts a character offset to a 1-based line number using the bisect algorithm.
    """
    return bisect.bisect_right(newline_index, offset)

def verify_terms(csv_path: str, manual_path: str, output_path: str) -> None:
    """
    Main processing function to verify terms and generate the output CSV.
    """
    # --- Step 1: Read ontology terms and dynamically get header ---
    print(f"Reading ontology terms from '{csv_path}'...")
    original_header = []
    ontology_data = []
    try:
        with open(csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            original_header = reader.fieldnames
            if not original_header:
                 print(f"Error: Could not read header from CSV file '{csv_path}'.", file=sys.stderr)
                 sys.exit(1)

            required_cols = {'Term', 'Variable'}
            if not required_cols.issubset(original_header):
                print(f"Error: Input CSV must contain 'Term' and 'Variable' columns.", file=sys.stderr)
                sys.exit(1)

            ontology_data = list(reader)
            if not ontology_data:
                print("Warning: Input CSV contains a header but no data rows.")
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at '{csv_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading CSV file: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 2: Read manual into memory and build line index ---
    print(f"Reading large manual file '{manual_path}' into memory...")
    try:
        with open(manual_path, mode='r', encoding='utf-8', errors='replace') as infile:
            manual_content = infile.read()
    except FileNotFoundError:
        print(f"Error: Manual file not found at '{manual_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading manual file: {e}", file=sys.stderr)
        sys.exit(1)

    newline_index = build_newline_index(manual_content)
    manual_content_lower = manual_content.lower()

    # --- Step 3: Iterate through terms, search, and collect results ---
    print(f"Verifying {len(ontology_data)} terms. This may take a while...")
    
    for i, entry in enumerate(ontology_data, 1):
        term = entry.get("Term", "").strip()
        variable = entry.get("Variable", "").strip()
        
        print(f"  [{i}/{len(ontology_data)}] Processing Term: '{term}', Variable: '{variable}'")

        if not term and not variable:
            entry['really found?'] = "no"
            entry['line_numbers'] = ""
            entry['occurrence_count'] = 0
            continue

        all_match_offsets = set()
        search_queries = {q.lower() for q in [term, variable] if q}

        for query in search_queries:
            try:
                pattern_str = create_regex_pattern(query)
                # Use finditer for memory-efficient iteration over all matches
                for match in re.finditer(pattern_str, manual_content_lower):
                    all_match_offsets.add(match.start())
            except re.error as e:
                print(f"    Warning: Could not compile regex for '{query}'. Error: {e}. Skipping.", file=sys.stderr)

        # --- Step 4: Process and format the results for the current entry ---
        total_occurrences = len(all_match_offsets)

        if total_occurrences > 0:
            entry['really found?'] = "yes"
            entry['occurrence_count'] = total_occurrences
            unique_line_numbers = sorted({offset_to_line_number(offset, newline_index) for offset in all_match_offsets})

            if len(unique_line_numbers) > MAX_LINE_NUMBERS_TO_REPORT:
                entry['line_numbers'] = ",".join(map(str, unique_line_numbers[:MAX_LINE_NUMBERS_TO_REPORT]))
            else:
                entry['line_numbers'] = ",".join(map(str, unique_line_numbers))
        else:
            entry['really found?'] = "no"
            entry['occurrence_count'] = 0
            entry['line_numbers'] = ""

    # --- Step 5: Write the updated data to the output CSV ---
    print(f"Writing results to '{output_path}'...")
    output_header = list(original_header)
    new_columns = ['really found?', 'line_numbers', 'occurrence_count']
    for col in new_columns:
        if col not in output_header:
            output_header.append(col)
    
    try:
        with open(output_path, mode='w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(ontology_data)
    except IOError as e:
        print(f"Error: Could not write to output file '{output_path}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)

    print("\nVerification complete!")
    print(f"Output successfully saved to '{output_path}'")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python term_verifier_fixed_v3.py <path_to_ontology_csv> <path_to_manual_txt>", file=sys.stderr)
        print("Example: python term_verifier_fixed_v3.py terms.csv manual.txt", file=sys.stderr)
        sys.exit(1)

    csv_file_path = sys.argv[1]
    manual_file_path = sys.argv[2]
    
    base_name = os.path.basename(csv_file_path)
    name, ext = os.path.splitext(base_name)
    output_file_path = f"{name}_verified{ext}"

    verify_terms(csv_file_path, manual_file_path, output_file_path)