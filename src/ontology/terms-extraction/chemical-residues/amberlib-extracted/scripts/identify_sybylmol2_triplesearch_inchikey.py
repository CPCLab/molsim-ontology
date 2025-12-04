import glob
import subprocess
import re
import os
import csv
import hashlib
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import AllChem

# --- CONFIGURATION ---
OUTPUT_CSV = "residue_detailed_analysis_inchikey.csv"
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
    clean_name = basename.replace(INPUT_FORMAT, "")
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

def query_single_inchikey(inchikey):
    """
    Queries PubChem using InChIKey.
    Note: InChIKey search is strictly EXACT. 
    The 'Fuzziness' comes from which version of the key we send (Raw, Canon, or Flat).
    """
    if not inchikey or inchikey == "Error":
        return "-", "-", "-"

    cid = "-"
    chebi = "-"
    name = "No Match"

    try:
        # Search by InChIKey
        compounds = pcp.get_compounds(inchikey, namespace='inchikey')

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

def generate_inchikey_variants(mol2_file):
    """
    Generates 3 versions of InChIKeys:
    1. Raw: Directly from OpenBabel (Trusts the file explicitly).
    2. Canon: RDKit processed (Standardized Stereo).
    3. Flat: RDKit processed (Stereo Removed + Neutralized).
       - This effectively performs a 'Skeleton Search' (Block 1).
    """
    raw_key = "Error"
    canon_key = "Error"
    flat_key = "Error"

    try:
        # 1. RAW InChIKey (via OpenBabel)
        cmd_key = ['obabel', '-imol2', mol2_file, '-oinchikey'] 
        result_key = subprocess.run(cmd_key, capture_output=True, text=True)
        if result_key.returncode == 0 and result_key.stdout.strip():
            raw_key = result_key.stdout.strip()

        # 2. Get SMILES for RDKit Input
        cmd_smi = ['obabel', '-imol2', mol2_file, '-osmiles']
        result_smi = subprocess.run(cmd_smi, capture_output=True, text=True)
        
        if result_smi.returncode == 0 and result_smi.stdout.strip():
            raw_smiles = result_smi.stdout.strip().split()[0]
            mol = Chem.MolFromSmiles(raw_smiles)

            if mol:
                # Variant 2: Canonical (Standard RDKit generation)
                canon_key = Chem.MolToInchiKey(mol)

                # Variant 3: Flat (Skeleton / Block 1 Equivalent)
                # To emulate searching just the skeleton (Block 1), we:
                #   a. Remove Stereochemistry
                #   b. Remove Hydrogens (Neutralize)
                # This generates a key ending in UHFFFAOYSA-N usually.
                Chem.RemoveStereochemistry(mol)
                mol_flat = Chem.RemoveHs(mol) 
                flat_key = Chem.MolToInchiKey(mol_flat)
            else:
                # Fallback if RDKit crashes
                canon_key = raw_key
                flat_key = raw_key

    except Exception:
        pass

    return raw_key, canon_key, flat_key

# --- MAIN EXECUTION ---
def main():
    search_pattern = f"*{INPUT_FORMAT}"
    files = glob.glob(search_pattern)
    
    # Define Column Headers
    headers = [
        "Filename", "Residue_Code", "MOL2_SHA256_Hash",
        "Raw_InChIKey", "Raw_CID", "Raw_ChEBI", "Raw_Name",
        "Canon_InChIKey", "Canon_CID", "Canon_ChEBI", "Canon_Name",
        "Flat_InChIKey", "Flat_CID", "Flat_ChEBI", "Flat_Name"
    ]

    print(f"Starting detailed InChIKey analysis of {len(files)} files...")
    
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
                
                # 1. Get Variants
                raw_k, canon_k, flat_k = generate_inchikey_variants(f)
                
                # 2. Query Databases
                raw_res = query_single_inchikey(raw_k)
                canon_res = query_single_inchikey(canon_k)
                flat_res = query_single_inchikey(flat_k)
                
                # 3. Bundle Data
                data = {
                    'raw_k': raw_k, 'raw_db': raw_res,
                    'canon_k': canon_k, 'canon_db': canon_res,
                    'flat_k': flat_k, 'flat_db': flat_res
                }
                
                if file_hash != "Hash_Error":
                    HASH_CACHE[file_hash] = data

            # --- STEP C: Write Row ---
            r_cid, r_chebi, r_name = data['raw_db']
            c_cid, c_chebi, c_name = data['canon_db']
            f_cid, f_chebi, f_name = data['flat_db']

            row = [
                f, res_code, file_hash,
                data['raw_k'], r_cid, r_chebi, r_name,
                data['canon_k'], c_cid, c_chebi, c_name,
                data['flat_k'], f_cid, f_chebi, f_name
            ]
            
            writer.writerow(row)

    print("-" * 60)
    print(f"Analysis Complete. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()