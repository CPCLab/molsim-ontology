import glob
import subprocess
import re
import os
import csv
import hashlib
import pubchempy as pcp
from rdkit import Chem

# --- CONFIGURATION ---
OUTPUT_CSV = "residue_analysis.csv"

def get_file_hash(filepath):
    """Calculates SHA256 hash of the file to verify identical content."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Read in chunks to handle large files efficiently
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return "Hash_Error"

def get_residue_code_from_filename(filename):
    """
    Extracts residue code assuming pattern: [LIBNAME]_[RESIDUE].pdb
    We split from the right to handle underscores in library names.
    """
    basename = os.path.basename(filename)
    # Split from the right side exactly once
    parts = basename.rsplit('_', 1)
    
    if len(parts) > 1:
        # parts[1] will be something like "ALA.pdb"
        return parts[1].replace('.pdb', '')
    return "Unknown"

def get_smiles_robust(pdb_file):
    """
    Converts PDB -> SMILES. 
    Falls back to raw OpenBabel SMILES if RDKit finds valence errors.
    """
    smiles_final = None
    try:
        # 1. Open Babel: Generate raw SMILES
        cmd = ['obabel', pdb_file, '-osmiles'] 
        result = subprocess.run(cmd, capture_output=True, text=True)
        smiles_raw = result.stdout.strip().split()[0]
        
        # 2. RDKit: Try to Clean/Canonicalize
        mol = Chem.MolFromSmiles(smiles_raw)
        if mol:
            smiles_final = Chem.MolToSmiles(mol, isomericSmiles=False, canonical=True)
        else:
            # 3. Fallback for "Illegal" Valences (e.g. N-terminals)
            mol_loose = Chem.MolFromSmiles(smiles_raw, sanitize=False)
            if mol_loose:
                smiles_final = smiles_raw # Trust Open Babel
    except Exception:
        pass
        
    return smiles_final

def find_chebi_id_in_synonyms(synonyms):
    pattern = re.compile(r'CHEBI:(\d+)', re.IGNORECASE)
    for syn in synonyms:
        match = pattern.search(syn)
        if match:
            return f"CHEBI:{match.group(1)}"
    return "-"

def query_databases(smiles):
    identity = "Unknown"
    pubchem_cid = "-"
    chebi_id = "-"
    
    if not smiles:
        return identity, pubchem_cid, chebi_id

    try:
        # 1. Exact Match
        compounds = pcp.get_compounds(smiles, namespace='smiles')
        
        # 2. Parent Match (Superstructure)
        if not compounds:
            hits = pcp.get_compounds(smiles, namespace='smiles', searchtype='superstructure', listkey_count=1)
            compounds = [hits[0]] if hits else []
            
        if compounds:
            c = compounds[0]
            pubchem_cid = str(c.cid)
            
            if c.synonyms:
                identity = c.synonyms[0]
                chebi_id = find_chebi_id_in_synonyms(c.synonyms)
            elif c.iupac_name:
                identity = c.iupac_name
            else:
                identity = f"Compound_{pubchem_cid}"
                
    except Exception:
        pass

    return identity, pubchem_cid, chebi_id

# --- MAIN EXECUTION ---
def main():
    files = glob.glob("*.pdb")
    
    # Define CSV Headers
    headers = [
        "Filename", 
        "Residue_Code", 
        "PubChem_CID", 
        "ChEBI_ID", 
        "Identity_Name", 
        "SMILES", 
        "PDB_SHA256_Hash"
    ]
    
    print(f"Starting analysis of {len(files)} files...")
    print(f"Results will be saved to: {OUTPUT_CSV}")

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        count = 0
        for f in files:
            # 1. Basic Metadata
            res_code = get_residue_code_from_filename(f)
            file_hash = get_file_hash(f)
            
            # 2. Chemical Structure
            smiles = get_smiles_robust(f)
            
            if not smiles:
                # Handle Read Errors
                writer.writerow([f, res_code, "-", "-", "Read Error", "-", file_hash])
                print(f"Processed {f} [ERROR]")
                continue

            # 3. Database Query
            name, cid, chebi = query_databases(smiles)
            if name is None: name = "Unknown"
            
            # 4. Write Row
            writer.writerow([f, res_code, cid, chebi, name, smiles, file_hash])
            
            count += 1
            if count % 10 == 0:
                print(f"Processed {count}/{len(files)} files...")

    print("-" * 50)
    print("Analysis Complete.")

if __name__ == "__main__":
    main()