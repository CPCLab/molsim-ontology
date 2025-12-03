import os
import glob
import subprocess
import re

# --- CONFIGURATION ---
LIB_DIR = "/home/fathoni/src/miniforge3/envs/ambertools/dat/leap/lib"
TEMP_SCRIPT_NAME = "process_mol2.in"

def get_residues_directly(lib_path):
    """
    Reads the .lib file as text and extracts unit names using Regex.
    This bypasses tleap's display issues entirely.
    """
    residues = []
    try:
        with open(lib_path, 'r', errors='ignore') as f:
            content = f.read()
            
            # Standard Amber Lib Format (OFF) looks like:
            # !entry.RESIDUENAME.unit.atoms
            # We capture the RESIDUENAME part.
            matches = re.findall(r'!entry\.([a-zA-Z0-9\+\-]+)\.unit\.atoms', content)
            
            for m in matches:
                if m not in residues:
                    residues.append(m)
    except Exception as e:
        print(f"Error reading file {lib_path}: {e}")
        
    return residues

def run_tleap_generation(lib_path, residues):
    """
    Writes a tleap script to file and runs it to generate mol2s.
    """
    filename = os.path.basename(lib_path)
    
    # We construct the tleap commands
    # We load standard forcefields first to prevent "Unknown atom type" errors
    commands = [
        "source leaprc.protein.ff14SB",
        "source leaprc.DNA.OL15",
        "source leaprc.water.tip3p",
        "source leaprc.gaff",
        f"loadoff {lib_path}"
    ]
    
    for res in residues:
        out_name = f"{filename}_{res}.mol2"
        # saveMol2: unit, filename, format(0)
        commands.append(f"saveMol2 {res} {out_name} 0")
        
    commands.append("quit")
    
    # Write to temp file
    with open(TEMP_SCRIPT_NAME, "w") as f:
        f.write("\n".join(commands))
        
    # Run tleap using the file flag (-f)
    # This avoids the "interactive" error
    subprocess.run(
        ['tleap', '-f', TEMP_SCRIPT_NAME], 
        stdout=subprocess.DEVNULL, # Mute output to keep terminal clean
        stderr=subprocess.STDOUT
    )
    
    # Cleanup
    if os.path.exists(TEMP_SCRIPT_NAME):
        os.remove(TEMP_SCRIPT_NAME)

def main():
    lib_files = glob.glob(os.path.join(LIB_DIR, "*.lib"))
    
    if not lib_files:
        print(f"No .lib files found in {LIB_DIR}")
        return

    print(f"Found {len(lib_files)} lib files.")
    print("-" * 40)

    total_generated = 0
    
    for lib_path in lib_files:
        filename = os.path.basename(lib_path)
        
        # 1. Direct Parse (No tleap involved)
        residues = get_residues_directly(lib_path)
        
        if not residues:
            print(f"Skipping {filename}: No units found in file text.")
            continue
            
        print(f"Processing {filename}: Found {len(residues)} units {residues}")
        
        # 2. Run tleap only for generation
        run_tleap_generation(lib_path, residues)
        total_generated += len(residues)

    print("-" * 40)
    print(f"Job Complete. Attempted to generate {total_generated} mol2 files.")

if __name__ == "__main__":
    main()
