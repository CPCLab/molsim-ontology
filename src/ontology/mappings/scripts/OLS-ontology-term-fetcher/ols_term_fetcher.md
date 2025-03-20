# OLS Term URI Fetcher

A Python script for retrieving URIs and labels for ontology terms from the EBI Ontology Lookup Service (OLS).

## Overview

This script allows users tobatch-processs a list of terms and retrieve their corresponding URIs and official labels from any ontology hosted in the EBI Ontology Lookup Service. It's handy for standardizing term references in scientific data or publications.

## Requirements

- Python 3.6+

- `requests` library

Install dependencies:

bash

`pip install requests`

## Usage

bash

`python ols_term_fetcher.py <ontology_id> <input_file> <output_file>`

## Parameters

- `<ontology_id>`: The ontology identifier (e.g., CHEBI, GO, HP)

- `<input_file>`: Path to a text file with terms (one per line)

- `<output_file>`: Path for the output CSV file

## Example

bash

`python ols_term_fetcher.py CHEBI terms.txt results.csv`

## Input Format

The input file should contain one term per line:

text

`peroxide `

`water `

`glucose`

## Output Format

The script generates a CSV file with three columns:

1. **Original Term**: The term as provided in the input file

2. **URI**: The unique resource identifier for the term

3. **Ontology Label**: The official label from the ontology

Example output:

text

`Original Term,URI,Ontology Label `

`peroxide,http://purl.obolibrary.org/obo/CHEBI_44785,peroxide `

`water,http://purl.obolibrary.org/obo/CHEBI_15377,water `

`glucose,http://purl.obolibrary.org/obo/CHEBI_17234,glucose`

## Features

- Exact term matching using the OLS API

- Rate limiting to avoid overwhelming the API

- Error handling for terms not found in the ontology

- Preservation of original term order in the output

## Limitations

- Case-sensitive term matching (follows OLS API behavior)

- Only returns the first match for each term

- Limited to ontologies available in the EBI OLS
