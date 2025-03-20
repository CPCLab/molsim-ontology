# CSV to Excel Converter

A Python script that collects CSV files from a directory, combines them into a single Excel workbook with each CSV on a separate sheet, and formats URIs as clickable hyperlinks.

## Features

- Automatically finds all CSV files in a specified directory

- Creates a single Excel workbook with each CSV file on its own sheet

- Converts URI columns into clickable hyperlinks

- Handles sheet name length limitations

## Requirements

- Python 3.6+

- pandas

- openpyxl

## Installation

1. Install required packages:

bash

`sudo apt install python3-pandas python3-openpyxl`

Or if using a virtual environment:

bash

`python3 -m venv venv source venv/bin/activate pip install pandas openpyxl`

## Usage

bash

`python csv_to_excel.py [directory_path]`

## Arguments

- `directory_path`: (Optional) Path to the directory containing CSV files. Defaults to the current directory.

- `--output` or `-o`: (Optional) Name of the output Excel file. Defaults to "collected_terms.xlsx".

## Examples

Convert all CSV files in the current directory:

bash

`python csv_to_excel.py`

Convert all CSV files in a specific directory:

bash

`python csv_to_excel.py /path/to/csv/files`

Specify a custom output filename:

bash

`python csv_to_excel.py --output my_terms.xlsx`

## How It Works

1. The script scans the specified directory for all files with a `.csv` extension

2. Each CSV file is read into a pandas DataFrame

3. The script creates a new Excel workbook using openpyxl

4. Each DataFrame is written to a separate sheet in the workbook

5. Sheet names are derived from the CSV filenames (truncated to 31 characters if necessary)

6. Any values in columns named "URI" are converted to clickable hyperlinks

7. The final workbook is saved as "collected_terms.xlsx" (or the specified output name)
