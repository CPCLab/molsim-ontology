import glob
import subprocess
import re
import os
import csv
import hashlib
import requests
import time
import sys
import pubchempy as pcp
from rdkit import Chem  # Required for local atom counting

# --- CONFIGURATION ---
OUTPUT_CSV = "residue_fragment_atom_counts.csv"
INPUT_FORMAT = "_sybyl.mol2"

# --- CACHE ---
HASH_CACHE = {}
UNICHEM_URL = "https://www.ebi.ac.uk/unichem/rest/src_compound_id_from_inchikey"

def check_api_connectivity():
    print("--- PRE-FLIGHT CHECK: Testing API Connectivity ---")
    try:
        pcp.get_compounds('Alanine', 'name')
        print("✅ PubChem Connection: OK")
        requests.get(f"{UNICHEM_URL}/test", timeout=5)
        print("✅ UniChem Connection: OK")
        print("--------------------------------------------------")
        sys.stdout.flush()
    except Exception as e:
        print("\n❌ CRITICAL ERROR: Could not connect to APIs.")
        sys.exit(1)

def get_file_hash(filepath):
    hasher = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return "Hash_Error"

def get_residue_code(filename):
    basename = os.path.basename(filename)
    clean_name = basename.replace(INPUT_FORMAT, "")
    parts = clean_name.rsplit('_', 1)
    if len(parts) > 1: return parts[1]
    return "Unknown"

def get_chebi_from_unichem(inchikey):
    if not inchikey: return "-"
    for attempt in range(3):
        try:
            url = f"{UNICHEM_URL}/{inchikey}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                for entry in data:
                    if entry.get('src_id') == '7':
                        return f"CHEBI:{entry.get('src_compound_id')}"
            return "-" 
        except Exception:
            time.sleep(2)
    return "-"

def get_fragment_smiles(mol2_file):
    smiles = None
    try:
        cmd = ['obabel', '-imol2', mol2_file, '-osmiles']
        res = subprocess.run(cmd, capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            smiles = res.stdout.strip().split()[0]
    except Exception:
        pass
    return smiles

def get_local_atom_count(smiles):
    """
    Uses RDKit to count heavy atoms in the SMILES string locally.
    """
    if not smiles: return 0
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol:
            return mol.GetNumHeavyAtoms()
    except:
        pass
    return 0

def find_parent_molecule_robust(fragment_smiles, filename):
    if not fragment_smiles: return "-", "-", "No SMILES", "-", 0
    
    cid = "-"
    chebi = "-"
    name = "No Match"
    parent_inchikey = None
    parent_atom_count = 0

    for attempt in range(3):
        try:
            hits = []
            
            # STRATEGY A: Substructure Search
            try:
                hits = pcp.get_compounds(fragment_smiles, namespace='smiles', searchtype='substructure', listkey_count=5)
            except Exception as e_sub:
                print(f"  ⚠️ [Substructure Failed] Switching to Similarity...")
                # STRATEGY B: Similarity Search
                hits = pcp.get_compounds(fragment_smiles, namespace='smiles', searchtype='similarity', threshold=95, listkey_count=5)

            if hits:
                # Parsimony Sort (Smallest heavy atom count first)
                hits.sort(key=lambda x: getattr(x, 'heavy_atom_count', 9999))
                parent = hits[0] 
                
                cid = str(parent.cid)
                name = parent.synonyms[0] if parent.synonyms else parent.iupac_name
                parent_inchikey = parent.inchikey
                
                # Get the atom count from the Parent (PubChem)
                parent_atom_count = getattr(parent, 'heavy_atom_count', 0)
                
                if parent.synonyms:
                    pattern = re.compile(r'CHEBI:(\d+)', re.IGNORECASE)
                    for syn in parent.synonyms:
                        match = pattern.search(syn)
                        if match:
                            chebi = f"CHEBI:{match.group(1)}"
                            break
            break 

        except Exception as e:
            print(f"  ⚠️ [API Error] {filename} (Attempt {attempt+1}/3): {e}")
            sys.stdout.flush()
            time.sleep(2 * (attempt + 1))
            if attempt == 2: name = f"API Error: {str(e)}"

    return cid, chebi, name, parent_inchikey, parent_atom_count

# --- MAIN EXECUTION ---
def main():
    check_api_connectivity()
    search_pattern = f"*{INPUT_FORMAT}"
    files = glob.glob(search_pattern)
    
    headers = [
        "Filename", "Residue_Code", "File_Hash",
        "Fragment_SMILES", "Frag_Heavy_Atoms",  # New Column
        "Parent_CID", "Parent_ChEBI", "Parent_Name", "Parent_Heavy_Atoms" # New Column
    ]

    print(f"Starting ATOM COUNT analysis of {len(files)} files...")
    
    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)

        for idx, f in enumerate(files):
            res_code = get_residue_code(f)
            file_hash = get_file_hash(f)
            
            if file_hash in HASH_CACHE:
                data = HASH_CACHE[file_hash]
                print(f"[{idx+1}/{len(files)}] {res_code}: Duplicate (Using Cache)")
            else:
                print(f"[{idx+1}/{len(files)}] {res_code}: Querying...")
                sys.stdout.flush()
                
                # 1. Get raw fragment & count its atoms locally
                frag_smi = get_fragment_smiles(f)
                frag_count = get_local_atom_count(frag_smi)
                
                # 2. Find Parent & get its atom count from API
                cid, chebi, name, p_key, p_count = find_parent_molecule_robust(frag_smi, f)
                
                # 3. UniChem Backup
                if chebi == "-" and p_key:
                    u_chebi = get_chebi_from_unichem(p_key)
                    if u_chebi != "-": chebi = u_chebi + " (UniChem)"
                
                time.sleep(1) 

                data = {
                    'smi': frag_smi, 'f_count': frag_count,
                    'cid': cid, 'chebi': chebi, 'name': name,
                    'p_count': p_count
                }
                
                if file_hash != "Hash_Error":
                    HASH_CACHE[file_hash] = data

            row = [
                f, res_code, file_hash,
                data['smi'], data['f_count'],
                data['cid'], data['chebi'], data['name'], data['p_count']
            ]
            writer.writerow(row)
            sys.stdout.flush()

    print("-" * 60)
    print(f"Analysis Complete. Saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()