#!/usr/bin/env python3
"""Build the mappings component from the SSSOM file.

WHY THIS EXISTS
    MOLSIM curates cross-ontology mappings in mappings/molsim.sssom.tsv, but
    nothing in the ODK build reads that file: MAPPINGS is empty in the
    generated Makefile, so MAPPING_FILES expands to nothing and the mapping
    set is never a release product. Measured 2026-09-17, the built molsim.owl
    contained 0 references to CHMO, EDAM, NCIT or KiSAO and exactly 1 MOLSIM
    class with any cross-reference at all, against 92 curated mappings.

    This script turns those rows into an OWL component that the edit file
    imports, so a consumer of a release can see them.

WHAT IT EMITS, AND WHAT IT DELIBERATELY DOES NOT
    One AnnotationAssertion per row, using the SKOS predicate the curator
    recorded. Decided 2026-09-17: SKOS only, never owl:equivalentClass.
    Equivalence would assert the two classes are the same in every model,
    which 29 exactMatch rows at 0.9 confidence do not claim, and it would
    pull each target's logical context into MOLSIM's reasoning.

    That is also why this is a script rather than `sssom convert`: the output
    shape stays under our control and cannot change under us.

USAGE
    python3 src/scripts/build_mappings_component.py
    python3 src/scripts/build_mappings_component.py --check   # verify only
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

DEFAULT_MAPPINGS = Path("src/ontology/mappings/molsim.sssom.tsv")
DEFAULT_OUT = Path("src/ontology/components/molsim_mappings_component.owl")
ONT_IRI = "http://purl.obolibrary.org/obo/molsim/components/molsim_mappings_component.owl"

# Only these 3 are curated in this file. A row carrying anything else is a
# curation error rather than something to render, so it stops the build.
ALLOWED = {"skos:exactMatch", "skos:closeMatch", "skos:relatedMatch"}


def read_curie_map(path: Path) -> dict[str, str]:
    """The prefix declarations, which live in the leading comment block."""
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            break
        m = re.match(r"#\s+([A-Za-z0-9._]+):\s*(\S+)\s*$", line)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def read_rows(path: Path) -> list[dict]:
    body = [l for l in path.read_text(encoding="utf-8").splitlines()
            if not l.startswith("#")]
    return list(csv.DictReader(body, delimiter="\t"))


def expand(curie: str, curie_map: dict[str, str]) -> str:
    """A CURIE to a full IRI. Longest prefix wins, so SWO.interface beats SWO."""
    for pfx in sorted(curie_map, key=len, reverse=True):
        if curie.startswith(pfx + ":"):
            return curie_map[pfx] + curie[len(pfx) + 1:]
    raise SystemExit(f"ERROR  no prefix declared for {curie!r}")


def build(mapping_file: Path) -> tuple[str, int]:
    curie_map = read_curie_map(mapping_file)
    rows = read_rows(mapping_file)
    lines = [
        "Prefix(owl:=<http://www.w3.org/2002/07/owl#>)",
        "Prefix(rdf:=<http://www.w3.org/1999/02/22-rdf-syntax-ns#>)",
        "Prefix(xml:=<http://www.w3.org/XML/1998/namespace>)",
        "Prefix(xsd:=<http://www.w3.org/2001/XMLSchema#>)",
        "Prefix(rdfs:=<http://www.w3.org/2000/01/rdf-schema#>)",
        "Prefix(skos:=<http://www.w3.org/2004/02/skos/core#>)",
        "",
        f"Ontology(<{ONT_IRI}>",
        "",
        "Declaration(AnnotationProperty(skos:exactMatch))",
        "Declaration(AnnotationProperty(skos:closeMatch))",
        "Declaration(AnnotationProperty(skos:relatedMatch))",
        "",
    ]
    n = 0
    for r in rows:
        subj, pred, obj = (r.get("subject_id") or "").strip(), \
                          (r.get("predicate_id") or "").strip(), \
                          (r.get("object_id") or "").strip()
        if not subj or not pred or not obj:
            continue
        if pred not in ALLOWED:
            raise SystemExit(f"ERROR  row {subj}: predicate {pred!r} is not one of {sorted(ALLOWED)}")
        lines.append(
            f"AnnotationAssertion({pred} <{expand(subj, curie_map)}> <{expand(obj, curie_map)}>)"
        )
        n += 1
    lines += ["", ")", ""]
    return "\n".join(lines), n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--mapping-file", type=Path, default=DEFAULT_MAPPINGS)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--check", action="store_true",
                    help="report what would be written; write nothing")
    a = ap.parse_args()

    if not a.mapping_file.exists():
        print(f"ERROR  no mapping file at {a.mapping_file}", file=sys.stderr)
        return 2

    text, n = build(a.mapping_file)
    if a.check:
        cur = a.output.read_text(encoding="utf-8") if a.output.exists() else ""
        state = "up to date" if cur == text else "OUT OF DATE, rebuild it"
        print(f"{n} mapping(s) from {a.mapping_file}; {a.output} is {state}")
        return 0 if cur == text else 1

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(text, encoding="utf-8")
    print(f"wrote {a.output} with {n} mapping assertion(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
