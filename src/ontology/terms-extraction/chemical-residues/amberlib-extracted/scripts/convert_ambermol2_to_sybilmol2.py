import os
import glob
import subprocess
import sys

def convert_file(file_path):
    """
    Runs antechamber to convert a single Amber Mol2 file to Sybyl Mol2.
    """
    filename = os.path.basename(file_path)
    directory = os.path.dirname(file_path)
    
    # Construct output filename: name.mol2 -> name_sybyl.mol2
    output_filename = filename.replace(".mol2", "_sybyl.mol2")
    output_path = os.path.join(directory, output_filename)
    
    # Skip if output already exists (optional, prevents re-work)
    if os.path.exists(output_path):
        print(f"Skipping {filename} (Output exists)")
        return

    # Antechamber Command
    # -i  : Input file
    # -fi : Input format (mol2)
    # -o  : Output file
    # -fo : Output format (mol2)
    # -at : Atom Type (sybyl) <--- The key parameter
    # -dr : Doctor (n=no) - Prevents modifying connectivity
    # -c  : Charge method (gas) - Calculates Gasteiger charges if missing
    # -pf : Par file (y) - Cleanup intermediate files
    cmd = [
        'antechamber',
        '-i', file_path,
        '-fi', 'mol2',
        '-o', output_path,
        '-fo', 'mol2',
        '-at', 'sybyl',
        '-dr', 'n',
        '-c', 'gas',
        '-pf', 'y'
    ]
    
    try:
        # Run command silently
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Converted: {filename} -> {output_filename}")
    except subprocess.CalledProcessError:
        print(f"FAILED: {filename} (Antechamber error)")
    except Exception as e:
        print(f"ERROR: {filename}: {e}")

def main():
    # 1. Determine Target Directory
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        target_dir = os.getcwd()
        
    print(f"--- Converting Amber Mol2 to Sybyl Mol2 ---")
    print(f"Target Directory: {target_dir}")
    
    # 2. Find all .mol2 files
    # We use glob to find files matching *.mol2
    all_files = glob.glob(os.path.join(target_dir, "*.mol2"))
    
    if not all_files:
        print("No .mol2 files found.")
        return

    count = 0
    for f in all_files:
        # 3. Filter loop
        # Don't try to convert files we just created (ending in _sybyl.mol2)
        if f.endswith("_sybyl.mol2"):
            continue
            
        convert_file(f)
        count += 1
        
    print("-" * 40)
    print(f"Job Complete. Processed {count} files.")

if __name__ == "__main__":
    main()