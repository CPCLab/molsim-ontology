#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ontology Term Candidate Verifier for PDF Manuals

This script verifies the occurrence of ontology terms from a CSV file directly
within large PDF documents, such as biomolecular simulation manuals. It is
designed for efficiency, robustness, and low memory usage by processing the
PDF one page at a time.

Key Features:
- Direct PDF Processing: Analyzes PDF files on-the-fly without requiring
  prior text extraction.
- Memory Efficient: Processes the PDF page-by-page, suitable for very large
  manuals (100MB+, 900+ pages).
- Robust Text Extraction: Uses `pdfminer.six` to handle complex layouts,
  multi-column text, and special characters.
- Advanced Search: Performs case-insensitive, multi-word searching that
  handles flexible whitespace and terms broken across lines within a page.
- Comprehensive Output: Enriches the input CSV with verification status,
  page numbers, and total occurrence counts.
- Self-Contained Testing: Includes a `--test` mode to generate sample
  files and validate the script's functionality.
"""

import csv
import re
import sys
import argparse
import logging
import os
from typing import List, Dict, Tuple, Any

# --- PDF Processing Library ---
# We use pdfminer.six for its robust handling of complex PDF layouts.
try:
    from pdfminer.high_level import extract_pages
    from pdfminer.layout import LTTextContainer
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfparser import PDFSyntaxError
    from pdfminer.psparser import PSSyntaxError
except ImportError:
    print("Error: pdfminer.six is not installed. Please install it using 'pip install pdfminer.six'", file=sys.stderr)
    sys.exit(1)

# --- Configuration ---
MAX_PAGE_NUMBERS_TO_REPORT = 100
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

def setup_logging():
    """Configures the global logger."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def create_regex_pattern(term_string: str) -> re.Pattern:
    """
    Creates a robust, case-insensitive regex pattern for a given term.

    This function is critical for accurate matching. It handles:
    1.  Special Characters: Escapes them using `re.escape()`.
    2.  Multi-word Terms: Replaces whitespace with `\s+` to match across
        spaces, tabs, and line breaks within a single extracted page text.
    3.  Whole Word Matching: Uses robust word boundaries `(?<!\w)` and `(?!\w)`
        to prevent partial matches (e.g., 'on' in 'ion') without failing on
        terms that start/end with symbols.
    """
    if not term_string:
        return None
    # Escape all special regex characters in the term
    pattern = re.escape(term_string.strip())
    # Replace escaped spaces with flexible whitespace matcher
    pattern = pattern.replace(r'\ ', r'\s+')
    # Use robust word boundaries
    final_pattern = r'(?<!\w)' + pattern + r'(?!\w)'
    try:
        return re.compile(final_pattern, re.IGNORECASE)
    except re.error as e:
        logging.warning(f"Could not compile regex for term '{term_string}'. Error: {e}. Skipping term.")
        return None

def verify_terms_in_pdf(csv_path: str, pdf_path: str, output_path: str):
    """
    Core function to process the CSV and PDF, and generate the output.
    """
    # --- 1. Read and Prepare Ontology Terms ---
    logging.info(f"Reading ontology terms from '{csv_path}'...")
    try:
        with open(csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            header = reader.fieldnames
            if not all(key in header for key in ["Term", "Variable"]):
                logging.error("CSV file must contain 'Term' and 'Variable' columns.")
                return

            # Prepare data structure for processing
            ontology_terms = []
            for row in reader:
                term_pattern = create_regex_pattern(row.get("Term", ""))
                var_pattern = create_regex_pattern(row.get("Variable", ""))
                # Only process if at least one valid pattern can be created
                if term_pattern or var_pattern:
                    ontology_terms.append({
                        "original_row": row,
                        "term_pattern": term_pattern,
                        "variable_pattern": var_pattern,
                        "matches": []  # Stores (page_number, count) tuples
                    })
                else:
                    logging.warning(f"Skipping invalid row with Term='{row.get('Term')}' and Variable='{row.get('Variable')}'")
    except FileNotFoundError:
        logging.error(f"Input CSV file not found: '{csv_path}'")
        return
    except Exception as e:
        logging.error(f"Failed to read or parse CSV file: {e}")
        return

    # --- 2. Process PDF Page by Page ---
    logging.info(f"Starting direct processing of PDF: '{pdf_path}'")
    total_pages = 0
    try:
        # Get total page count for progress reporting without loading the whole file
        with open(pdf_path, 'rb') as f:
            total_pages = len(list(PDFPage.get_pages(f, check_extractable=False)))
        logging.info(f"PDF contains {total_pages} pages.")
    except (PDFSyntaxError, PSSyntaxError) as e:
        logging.error(f"PDF file '{pdf_path}' appears to be corrupted or malformed. Error: {e}")
        return
    except Exception as e:
        logging.warning(f"Could not determine total page count. Progress will not show total. Error: {e}")


    try:
        # `extract_pages` is a generator, processing one page at a time. This is memory-efficient.
        for page_layout in extract_pages(pdf_path):
            page_num = page_layout.pageid
            if total_pages > 0:
                print(f"\rProcessing page {page_num}/{total_pages}...", end="")
            else:
                print(f"\rProcessing page {page_num}...", end="")

            page_text = ""
            # Recursively extract text from all text-containing elements on the page
            for element in page_layout:
                if isinstance(element, LTTextContainer):
                    page_text += element.get_text()

            # Search for each ontology term on the current page
            for term_data in ontology_terms:
                page_occurrences = 0
                if term_data["term_pattern"]:
                    page_occurrences += len(term_data["term_pattern"].findall(page_text))
                
                # Avoid double-counting if Term and Variable are identical
                if row.get("Term", "").lower() != row.get("Variable", "").lower():
                    if term_data["variable_pattern"]:
                        page_occurrences += len(term_data["variable_pattern"].findall(page_text))
                
                if page_occurrences > 0:
                    term_data["matches"].append({"page": page_num, "count": page_occurrences})

    except (PDFSyntaxError, PSSyntaxError) as e:
        logging.error(f"\nFailed to process PDF. File may be encrypted or corrupted. Error: {e}")
        return
    except Exception as e:
        logging.error(f"\nAn unexpected error occurred during PDF processing: {e}")
        return
    
    print("\nPDF processing complete.")

    # --- 3. Finalize Results and Write Output CSV ---
    logging.info(f"Finalizing results and writing to '{output_path}'...")
    output_header = header + ['really found?', 'page_numbers', 'occurrence_count']
    
    final_rows = []
    for term_data in ontology_terms:
        total_occurrences = sum(m['count'] for m in term_data['matches'])
        page_numbers = sorted(list(set(m['page'] for m in term_data['matches'])))

        row_to_write = term_data['original_row']
        if total_occurrences > 0:
            row_to_write['really found?'] = "yes"
            row_to_write['occurrence_count'] = total_occurrences
            row_to_write['page_numbers'] = ",".join(map(str, page_numbers[:MAX_PAGE_NUMBERS_TO_REPORT]))
        else:
            row_to_write['really found?'] = "no"
            row_to_write['occurrence_count'] = 0
            row_to_write['page_numbers'] = ""
        final_rows.append(row_to_write)
        
    try:
        with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_header, quoting=csv.QUOTE_ALL, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(final_rows)
    except IOError as e:
        logging.error(f"Failed to write output file '{output_path}'. Reason: {e}")
        return
        
    logging.info("Verification complete. Output successfully saved.")

def run_test_mode():
    """
    Creates temporary sample files and runs the verification process to test functionality.
    """
    logging.info("--- Running in Test Mode ---")
    
    # 1. Create a dummy CSV file
    test_csv_path = "test_ontology.csv"
    test_csv_content = [
        ["Term", "Variable", "Description", "Category Candidates"],
        ["Gibbs Free Energy", "gibbs_fe", "A key thermodynamic potential.", "thermodynamics"],
        ["multi-word term", "multi_word_var", "A term that spans lines.", "testing"],
        ["Non-existent term", "no_such_var", "This should not be found.", "testing"],
        ["-remlog", "-remlog", "A symbol-heavy flag.", "flag"]
    ]
    with open(test_csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(test_csv_content)
    logging.info(f"Created test CSV: '{test_csv_path}'")

    # 2. Create a dummy PDF file using reportlab
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
    except ImportError:
        logging.error("ReportLab is not installed. Please run 'pip install reportlab' to use --test mode.")
        return
        
    test_pdf_path = "test_manual.pdf"
    c = canvas.Canvas(test_pdf_path, pagesize=letter)
    
    # Page 1
    c.drawString(72, 800, "Page 1: An introduction to Gibbs Free Energy calculations.")
    c.drawString(72, 780, "The gibbs_fe variable is important.")
    c.showPage()
    
    # Page 2
    c.drawString(72, 800, "Page 2: Here we test a multi-word")
    c.drawString(72, 788, "term that should be found across lines.")
    c.drawString(72, 750, "We also mention Gibbs Free Energy again.")
    c.showPage()

    # Page 3
    c.drawString(72, 800, "Page 3: Testing special flags like -remlog is crucial.")
    c.showPage()
    
    c.save()
    logging.info(f"Created test PDF: '{test_pdf_path}'")

    # 3. Run the verifier on the test files
    test_output_path = "test_occurenced_ontology.csv"
    verify_terms_in_pdf(test_csv_path, test_pdf_path, test_output_path)
    
    # 4. Print results and clean up
    logging.info("--- Test Mode Results ---")
    if os.path.exists(test_output_path):
        with open(test_output_path, 'r', encoding='utf-8') as f:
            print(f.read())
    
    logging.info("--- Cleaning up test files ---")
    os.remove(test_csv_path)
    os.remove(test_pdf_path)
    os.remove(test_output_path)
    logging.info("Test complete.")


def main():
    """Main entry point for the script."""
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Verify ontology term occurrences directly in large PDF manuals.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("csv_file", nargs='?', default=None, help="Path to the input ontology CSV file.")
    parser.add_argument("pdf_file", nargs='?', default=None, help="Path to the input PDF manual.")
    parser.add_argument(
        "-o", "--output", dest="output_file",
        help="Path for the output CSV file. (default: [csv_file]_occurence.csv)"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run a self-contained test with sample files to verify functionality."
    )
    args = parser.parse_args()

    if args.test:
        run_test_mode()
        return

    if not args.csv_file or not args.pdf_file:
        parser.error("the following arguments are required: csv_file, pdf_file (unless using --test)")

    output_path = args.output_file
    if not output_path:
        base, ext = os.path.splitext(args.csv_file)
        output_path = f"{base}_occurence.csv"

    verify_terms_in_pdf(args.csv_file, args.pdf_file, output_path)

if __name__ == '__main__':
    main()
    
