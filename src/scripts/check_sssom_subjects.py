#!/usr/bin/env python3
"""Check the SUBJECT side of the SSSOM mapping file against the ontology.

Why this exists
---------------
`sssom validate` only checks the mapping FILE: required columns, declared
prefixes, well-formed CURIEs. It never opens an ontology and never resolves an
IRI, so it happily accepts a mapping whose subject does not exist at all.
Demonstrated: rewriting a row to `MOLSIM:009999 -> NCIT:C99999999` (neither term
exists) still exits 0, silently.

The failure that actually happens is a *wrong* subject, not a malformed one --
a mistyped ID that lands on a real but different term. During the EDAM batch,
six hand-typed MOLSIM IDs were all wrong; `atom ID` would have pointed at
MOLSIM:001612, which is `atomtype`. No syntax checker can catch that.

This script checks the half that can be verified offline and deterministically,
which is also the half where our own typos live. For every mapping row:

  1. the subject term is DECLARED in the edit file;
  2. `subject_label` matches the term's actual rdfs:label;
  3. `subject_type` matches the term's actual declaration (class / named
     individual / object property / data property);
  4. the subject is NOT deprecated -- mapping a retired term would send
     consumers to something we have withdrawn.

Check 2 also catches drift: relabel a term later and the mapping file goes
stale silently today.

The OBJECT side is deliberately not checked here. Objects live in other
ontologies, most of which MOLSIM maps to rather than imports, so verifying them
needs the network. That belongs in an occasional audit, not a build gate -- see
`audit_sssom_objects.py`.

Usage
-----
    python3 ../scripts/check_sssom_subjects.py            # from src/ontology
    python3 src/scripts/check_sssom_subjects.py --repo-root .

Exits 0 if every row passes, 1 otherwise, so `make test` fails on a problem.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

# Declaration keyword in OWL functional syntax -> the SSSOM subject_type value.
# SSSOM spec values are lowercase with spaces, e.g. "owl class".
DECL_TO_SSSOM_TYPE = {
    "Class": "owl class",
    "NamedIndividual": "owl named individual",
    "ObjectProperty": "owl object property",
    "DataProperty": "owl data property",
}


def read_ontology(edit_file: Path):
    """Return (kind_by_id, label_by_id, deprecated_ids) for MOLSIM entities."""
    text = edit_file.read_text(encoding="utf-8")

    kind = {}
    for decl, sssom_type in DECL_TO_SSSOM_TYPE.items():
        pattern = r"Declaration\(" + decl + r"\(obo:(MOLSIM_\d+)\)\)"
        for term_id in re.findall(pattern, text):
            kind[term_id] = sssom_type

    label = dict(re.findall(r'rdfs:label obo:(MOLSIM_\d+) "([^"]*)"', text))
    deprecated = set(re.findall(r"owl:deprecated obo:(MOLSIM_\d+)", text))
    return kind, label, deprecated


def read_mappings(mapping_file: Path):
    """Return the mapping rows, skipping the '#' YAML-ish header block."""
    lines = [
        line
        for line in mapping_file.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#")
    ]
    return list(csv.DictReader(lines, delimiter="\t"))


def check(edit_file: Path, mapping_file: Path):
    kind, label, deprecated = read_ontology(edit_file)
    rows = read_mappings(mapping_file)

    problems = []
    for line_no, row in enumerate(rows, start=2):  # +1 header, +1 for 1-based
        subject = row.get("subject_id", "")
        if not subject.startswith("MOLSIM:"):
            # Not our term to check. A mapping set may legitimately carry rows
            # whose subject belongs to someone else.
            continue
        term_id = subject.replace("MOLSIM:", "MOLSIM_")

        if term_id not in kind:
            problems.append(
                (line_no, subject, "subject is not declared in the edit file", "")
            )
            continue

        if term_id in deprecated:
            problems.append(
                (line_no, subject, "subject is a RETIRED (deprecated) term", label.get(term_id, ""))
            )

        expected_label = label.get(term_id)
        if row.get("subject_label") != expected_label:
            problems.append(
                (
                    line_no,
                    subject,
                    "subject_label does not match rdfs:label",
                    f"file={row.get('subject_label')!r} ontology={expected_label!r}",
                )
            )

        if row.get("subject_type") != kind[term_id]:
            problems.append(
                (
                    line_no,
                    subject,
                    "subject_type does not match the declaration",
                    f"file={row.get('subject_type')!r} ontology={kind[term_id]!r}",
                )
            )

    return rows, problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        default="..",
        help="Repo-relative base. Default '..' suits being run from src/ontology.",
    )
    parser.add_argument("--edit-file", default=None)
    parser.add_argument("--mapping-file", default=None)
    args = parser.parse_args()

    root = Path(args.repo_root)
    # When run from src/ontology, root='..' means root/ontology/... resolves.
    edit_file = Path(args.edit_file) if args.edit_file else root / "ontology" / "molsim-edit.owl"
    mapping_file = (
        Path(args.mapping_file)
        if args.mapping_file
        else root / "ontology" / "mappings" / "molsim.sssom.tsv"
    )

    if not edit_file.exists() or not mapping_file.exists():
        # Fall back to repo-root-relative paths (running from the repo root).
        edit_file = root / "src" / "ontology" / "molsim-edit.owl"
        mapping_file = root / "src" / "ontology" / "mappings" / "molsim.sssom.tsv"

    for path in (edit_file, mapping_file):
        if not path.exists():
            print(f"ERROR: cannot find {path}", file=sys.stderr)
            return 2

    rows, problems = check(edit_file, mapping_file)

    if problems:
        print(f"FAIL {len(problems)} subject-side problem(s) in {mapping_file}:")
        for line_no, subject, what, detail in problems:
            print(f"  line {line_no}: {subject} -- {what}" + (f"  [{detail}]" if detail else ""))
        return 1

    print(
        f"PASS sssom subject check: {len(rows)} mapping(s); every subject exists, "
        "is not deprecated, and its label and type match the ontology"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
