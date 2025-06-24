The following directory contains:

- `amber-terms-10k-splits-raw.csv` - list of terms extracted from AmberMD's LaTeX manual automatically (which was split as chunks, each with 10k lines) , not yet processed.

- `cpptraj-terms-10k-splits-raw.csv`  - list of terms extracted from CPPTRAJ's LaTeX manual automatically (which was split as chunks, each with 10k lines), not yet processed.

- `amber-terms-10k-splits-raw_verified.csv `- list of terms extracted from AmberMD's LaTeX manual as above, now appended with whether the term can actually be found in the Amber manual file, and if so, which line numbers in the text (up to 100 occurrences), and the count of occurrences.

- `cpptraj-terms-10k-splits-raw_verified.cs`v - akin to above but for the cpptraj manual.

- `term_verifier.py` - Python script to verify/count the terms occurrence for generating the verified CSVs above. Usage: `python term_verifier.py <path_to_ontology_csv> <path_to_manual_txt>`