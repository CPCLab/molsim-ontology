import glob
import subprocess
import re
import os
import csv
import hashlib
import pubchempy as pcp
from rdkit import Chem

# --- CONFIGURATION ---
OUTPUT_CSV = "residue_detailed_analysis_mol2.csv"
INPUT_FORMAT = "_sybyl.mol2" # Pattern to match your sybyl files

# --- CACHE ---
HASH_CACHE = {}

def get_file_hash(filepath):
    """Calculates SHA256 hash to detect identical file content."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return "Hash_Error"

def get_residue_code(filename):
    """Extracts 'ALA' from 'all_amino03.lib_ALA_sybyl.mol2'."""
    basename = os.path.basename(filename)
    # Remove the known suffix first
    clean_name = basename.replace(INPUT_FORMAT, "")
    # Now split by underscore to get the code (assuming pattern LIB_CODE)
    parts = clean_name.rsplit('_', 1)
    if len(parts) > 1:
        return parts[1]
    return "Unknown"

def find_chebi_id_in_synonyms(synonyms):
    pattern = re.compile(r'CHEBI:(\d+)', re.IGNORECASE)
    for syn in synonyms:
        match = pattern.search(syn)
        if match:
            return f"CHEBI:{match.group(1)}"
    return "-"

def query_single_smiles(smiles):
    """Queries PubChem for a specific SMILES string."""
    if not smiles or smiles == "Error":
        return "-", "-", "-"

    cid = "-"
    chebi = "-"
    name = "No Match"

    try:
        # 1. Exact Match
        compounds = pcp.get_compounds(smiles, namespace='smiles')
        
        # 2. Parent Match (Fallback)
        if not compounds:
            hits = pcp.get_compounds(smiles, namespace='smiles', searchtype='superstructure', listkey_count=1)
            compounds = [hits[0]] if hits else []
            if compounds: name = "[Parent] Found"

        if compounds:
            c = compounds[0]
            cid = str(c.cid)
            
            if c.synonyms:
                name = c.synonyms[0]
                chebi = find_chebi_id_in_synonyms(c.synonyms)
            elif c.iupac_name:
                name = c.iupac_name
            else:
                name = f"Compound_{cid}"
                
    except Exception:
        name = "API Error"
        
    return cid, chebi, name

def generate_smiles_variants(mol2_file):
    """
    Generates 3 versions of SMILES from a MOL2 input:
    1. Raw (from OpenBabel reading Mol2)
    2. Canonical (Isomeric=True)
    3. Flat (Isomeric=False)
    """
    raw = None
    canon = None
    flat = None

    try:
        # 1. RAW (via OpenBabel)
        # We explicitly tell obabel the input format is mol2 (-imol2)
        cmd = ['obabel', '-imol2', mol2_file, '-osmiles'] 
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout.strip():
            raw_str = result.stdout.strip().split()[0]
            raw = raw_str

            # 2. RDKit Processing
            mol = Chem.MolFromSmiles(raw_str)
            
            if mol:
                # Variant 2: Canonical but KEEP Stereochemistry (@)
                canon = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
                
                # Variant 3: Canonical and REMOVE Stereochemistry (Flat)
                flat = Chem.MolToSmiles(mol, isomericSmiles=False, canonical=True)
            else:
                canon = raw_str
                flat = raw_str
        else:
            raw = "Error"
            canon = "Error"
            flat = "Error"
            
    except Exception:
        raw = "Error"
        canon = "Error"
        flat = "Error"

    return raw, canon, flat

# --- MAIN EXECUTION ---
def main():
    # Update glob to look for the specific suffix (e.g., *_sybyl.mol2)
    search_pattern = f"*{INPUT_FORMAT}"
    files = glob.glob(search_pattern)
    
    # Define Column Headers
    headers = [
        "Filename", "Residue_Code", "MOL2_SHA256_Hash",
        "Raw_SMILES", "Raw_CID", "Raw_ChEBI", "Raw_Name",
        "Canon_SMILES", "Canon_CID", "Canon_ChEBI", "Canon_Name",
        "Flat_SMILES", "Flat_CID", "Flat_ChEBI", "Flat_Name"
    ]

    print(f"Starting detailed analysis of {len(files)} files matching '{search_pattern}'...")
    
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for idx, f in enumerate(files):
            # --- STEP A: Metadata & Hash ---
            res_code = get_residue_code(f)
            file_hash = get_file_hash(f)
            
            # --- STEP B: Check Cache ---
            if file_hash in HASH_CACHE and file_hash != "Hash_Error":
                data = HASH_CACHE[file_hash]
                print(f"[{idx+1}/{len(files)}] {res_code}: Duplicate found (Skipping API)")
            else:
                print(f"[{idx+1}/{len(files)}] {res_code}: New structure (Querying API...)")
                
                # 1. Get Variants (From Mol2 now)
                raw_s, canon_s, flat_s = generate_smiles_variants(f)
                
                # 2. Query Databases
                raw_res = query_single_smiles(raw_s)
                canon_res = query_single_smiles(canon_s)
                flat_res = query_single_smiles(flat_s)
                
                # 3. Bundle Data
                data = {
                    'raw_s': raw_s, 'raw_db': raw_res,
                    'canon_s': canon_s, 'canon_db': canon_res,
                    'flat_s': flat_s, 'flat_db': flat_res
                }
                
                if file_hash != "Hash_Error":
                    HASH_CACHE[file_hash] = data

            # --- STEP C: Write Row ---
            r_cid, r_chebi, r_name = data['raw_db']
            c_cid, c_chebi, c_name = data['canon_db']
            f_cid, f_chebi, f_name = data['flat_db']

            row = [
                f, res_code, file_hash,
                data['raw_s'], r_cid, r_chebi, r_name,
                data['canon_s'], c_cid, c_chebi, c_name,
                data['flat_s'], f_cid, f_chebi, f_name
            ]
            
            writer.writerow(row)

    print("-" * 60)
    print(f"Analysis Complete. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()