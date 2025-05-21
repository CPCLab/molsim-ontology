import pathlib
import sys # Though not strictly necessary for this modification, it's often useful.

def escape_csv_cell(cell_content):
    """
    Escapes a cell content for CSV format.
    If the content contains a comma, a double quote, or a newline,
    it will be enclosed in double quotes. Existing double quotes
    within the content will be doubled.
    """
    cell_content = str(cell_content)
    if '"' in cell_content or ',' in cell_content or '\n' in cell_content:
        # Double up existing double quotes
        escaped_content = cell_content.replace('"', '""')
        # Enclose in double quotes
        return f'"{escaped_content}"'
    else:
        return cell_content

def convert_markdown_table_to_csv(markdown_content):
    """
    Converts a markdown table string into a CSV string.
    Assumes the first line of the table is the header,
    the second is the separator line, and subsequent lines are data.
    """
    lines = markdown_content.splitlines()
    
    markdown_table_rows_only = []
    
    # Extract only lines that are part of the markdown table
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("--- START OF FILE"): # Skip the marker line
            continue
        if not stripped_line:  # Skip empty lines
            continue
            
        # A markdown table row starts and ends with a pipe '|'
        if stripped_line.startswith('|') and stripped_line.endswith('|'):
            markdown_table_rows_only.append(stripped_line)

    if not markdown_table_rows_only or len(markdown_table_rows_only) < 2:
        # Not enough lines for a header and a separator (or no table found)
        print("Warning: No valid Markdown table structure found or table is too short.", file=sys.stderr)
        return ""

    csv_output_lines = []

    # The first extracted markdown table line is the header
    header_md_line = markdown_table_rows_only[0]
    
    # The lines from the third onwards are data rows (index 2)
    # markdown_table_rows_only[1] is the separator line, which we skip
    data_md_lines = markdown_table_rows_only[2:]

    def parse_and_escape_md_row(md_row_string):
        # Remove leading/trailing pipes from the line
        content_between_pipes = md_row_string.strip()[1:-1]
        # Split by pipe to get raw cell contents
        raw_cells = content_between_pipes.split('|')
        # Trim whitespace from each cell and then CSV escape it
        processed_cells = [escape_csv_cell(cell.strip()) for cell in raw_cells]
        return ",".join(processed_cells)

    # Process header
    csv_output_lines.append(parse_and_escape_md_row(header_md_line))

    # Process data rows
    for data_md_line in data_md_lines:
        csv_output_lines.append(parse_and_escape_md_row(data_md_line))
        
    return "\n".join(csv_output_lines)

if __name__ == "__main__":
    # Get the directory where the script is located
    script_dir = pathlib.Path(__file__).resolve().parent

    # Define input and output file names
    input_filename = "terms-table.md"
    output_filename = "terms-table.csv"

    # Construct full paths
    input_filepath = script_dir / input_filename
    output_filepath = script_dir / output_filename

    markdown_input_content = ""
    try:
        with open(input_filepath, 'r', encoding='utf-8') as f_in:
            markdown_input_content = f_in.read()
        print(f"Successfully read from '{input_filepath}'")
    except FileNotFoundError:
        print(f"Error: Input file '{input_filepath}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file '{input_filepath}': {e}", file=sys.stderr)
        sys.exit(1)

    if not markdown_input_content.strip():
        print("Error: Input file is empty.", file=sys.stderr)
        sys.exit(1)

    csv_output_content = convert_markdown_table_to_csv(markdown_input_content)

    if csv_output_content: # Only write if there's something to write
        try:
            with open(output_filepath, 'w', encoding='utf-8', newline='') as f_out:
                f_out.write(csv_output_content)
            print(f"Successfully converted and wrote to '{output_filepath}'")
        except Exception as e:
            print(f"Error writing to file '{output_filepath}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("No CSV content generated, so no output file was written.", file=sys.stderr)