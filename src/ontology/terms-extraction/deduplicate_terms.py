#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Aggressive Terms Deduplication using a Clustering (Connected Components) Algorithm

This script implements deduplication by identifying "semantic clusters" of 
related terms and selecting a single champion from each.

Architecture:
-   **Graph-Based Clustering**: Treats rows as nodes in a graph where an edge
    exists if two rows share a canonical 'Term' or 'Variable'. It then finds
    all "connected components" (clusters) in this graph. This correctly groups
    entries like (A, B) and (B, C) into a single cluster (A, B, C).
-   **One Champion Per Cluster**: For each discovered cluster, a single "champion"
    is selected based on a priority score. All other members of the cluster are
    aggressively removed.
-   This approach solves the problem of related items not being
    grouped because they didn't share the *exact same* key.

Usage:
    python deduplicate_terms.py <path_to_input_csv>
"""

import csv
import sys
import os
import re
from collections import defaultdict
from typing import Dict, Any, Tuple, List, Set

# --- Configuration ---
TERM_STOP_WORDS = {
    'a', 'an', 'the', 'of', 'for', 'in', 'with', 'on', 'at', 'by',
    'and', 'or', 'is', 'are', 'was', 'be', 'to', 'as',
    'energy', 'potential', 'parameter', 'method', 'algorithm', 'system',
    'option', 'control', 'type', 'scheme', 'correction', 'value', 'file',
    'selector', 'model', 'area', 'surface', 'coordinate', 'restart', 'information',
    'born', 'generalized'
}

def get_canonical_form(text: str) -> str:
    """
    Creates a standardized, sorted key from a string to group similar terms.
    """
    if not text:
        return ""
    words = re.split(r'[\s_-]+', text.lower())
    meaningful_words = sorted([word for word in words if word and word not in TERM_STOP_WORDS])
    return " ".join(meaningful_words)

def parse_row_data(row: Dict[str, str], original_index: int) -> Dict[str, Any]:
    """
    Parses a CSV row into a structured dictionary with typed and canonical data.
    """
    try:
        term = row.get('Term', '')
        variable = row.get('Variable', '')
        category_col_name = next((k for k in row if 'Category' in k), None)
        categories = row.get(category_col_name, '')

        return {
            'term': term,
            'variable': variable,
            'canonical_term': get_canonical_form(term),
            'canonical_variable': get_canonical_form(variable),
            'description': row.get('Description', ''),
            'categories': categories,
            'found': row.get('really found?', 'no'),
            'count': int(row.get('occurrence_count', 0)),
            'original_row': row,
            'original_index': original_index,
        }
    except (ValueError, TypeError) as e:
        print(f"Warning: Could not parse row {original_index + 1}. Error: {e}. Skipping.", file=sys.stderr)
        return None

def get_priority_score(parsed_row: Dict[str, Any]) -> Tuple:
    """
    Calculates a sortable score to determine which row is the "best" in a group.
    """
    num_categories = parsed_row['categories'].count('|') + 1 if parsed_row['categories'] else 0
    found_score = 1 if parsed_row['found'] == 'yes' else 0
    return (
        parsed_row['count'],
        len(parsed_row['description']),
        len(parsed_row['term']),
        num_categories,
        found_score,
        -parsed_row['original_index']
    )

def deduplicate_terms(input_path: str):
    """
    Main function to drive the clustering-based deduplication process.
    """
    # --- Step 1: Read and Parse CSV ---
    print(f"Reading and parsing data from '{input_path}'...")
    try:
        with open(input_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            header = reader.fieldnames
            parsed_data = [parse_row_data(row, i) for i, row in enumerate(reader)]
            parsed_data = [p for p in parsed_data if p]
            row_data_map = {p['original_index']: p for p in parsed_data}
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'", file=sys.stderr)
        return

    # --- Step 2: Build Graph Indices ---
    print("Building indices for graph traversal...")
    group_to_rows = defaultdict(list)
    row_to_groups = defaultdict(list)

    for p_row in parsed_data:
        idx = p_row['original_index']
        # Map canonical keys to row indices
        if p_row['canonical_term']:
            group_to_rows[p_row['canonical_term']].append(idx)
            row_to_groups[idx].append(p_row['canonical_term'])
        if p_row['canonical_variable'] and p_row['canonical_variable'] != p_row['canonical_term']:
            group_to_rows[p_row['canonical_variable']].append(idx)
            row_to_groups[idx].append(p_row['canonical_variable'])

    # --- Step 3: Find Connected Components (Clusters) ---
    print("Finding semantic clusters using graph traversal...")
    clusters: List[List[int]] = []
    visited_rows: Set[int] = set()

    for i in range(len(parsed_data)):
        if i in visited_rows:
            continue

        current_cluster: List[int] = []
        queue: List[int] = [i]
        visited_rows.add(i)

        while queue:
            current_row_idx = queue.pop(0)
            current_cluster.append(current_row_idx)

            # Find all neighbors via shared groups
            for group_key in row_to_groups[current_row_idx]:
                for neighbor_idx in group_to_rows[group_key]:
                    if neighbor_idx not in visited_rows:
                        visited_rows.add(neighbor_idx)
                        queue.append(neighbor_idx)
        
        clusters.append(current_cluster)

    # --- Step 4: Process each cluster to find one champion ---
    print(f"Processing {len(clusters)} clusters to select one champion from each...")
    kept_rows = []
    redundant_rows = []

    for cluster_indices in clusters:
        if not cluster_indices:
            continue
        
        # If a cluster has only one item, it's automatically kept
        if len(cluster_indices) == 1:
            kept_rows.append(row_data_map[cluster_indices[0]])
            continue
            
        # Get the full data for all rows in the cluster
        cluster_data = [row_data_map[idx] for idx in cluster_indices]
        
        # Sort by priority to find the champion
        cluster_data.sort(key=get_priority_score, reverse=True)
        
        champion = cluster_data[0]
        kept_rows.append(champion)

        # All others are redundant
        for i in range(1, len(cluster_data)):
            redundant_item = cluster_data[i]
            reason = (f"Lower-priority member of semantic cluster led by row "
                      f"{champion['original_index'] + 1} (Champion: '{champion['term']}')")
            redundant_item['original_row']['removal_reason'] = reason
            redundant_rows.append(redundant_item)

    # --- Step 5: Write output files ---
    print(f"Deduplication complete. Kept: {len(kept_rows)}. Removed: {len(redundant_rows)}.")
    
    kept_rows.sort(key=lambda x: x['original_index'])
    redundant_rows.sort(key=lambda x: x['original_index'])
    
    base_name = os.path.basename(input_path)
    name, ext = os.path.splitext(base_name)
    deduplicated_path = f"{name}_deduplicated{ext}"
    redundant_path = f"{name}_redundant-removed{ext}"
    
    print(f"Writing deduplicated entries to '{deduplicated_path}'...")
    with open(deduplicated_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=header, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows([r['original_row'] for r in kept_rows])

    if redundant_rows:
        print(f"Writing removed entries to '{redundant_path}'...")
        redundant_header = header + ['removal_reason']
        with open(redundant_path, 'w', newline='', encoding='utf-8') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=redundant_header, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows([r['original_row'] for r in redundant_rows])

    print("\nProcess finished successfully.")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: python {os.path.basename(__file__)} <path_to_input_csv>", file=sys.stderr)
        sys.exit(1)

    deduplicate_terms(sys.argv[1])