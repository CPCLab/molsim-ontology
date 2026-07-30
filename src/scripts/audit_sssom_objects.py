#!/usr/bin/env python3
"""OCCASIONAL AUDIT: check the OBJECT side of the SSSOM mapping file online.

This is NOT part of `make test`, on purpose
-------------------------------------------
Every object term lives in someone else's ontology, and MOLSIM deliberately
MAPS to most of them rather than importing them, so there is no local copy to
check against. Verifying them means going over the network, which is fine for an
audit but wrong for a build gate: it would break offline builds, depend on OLS
being up, and hit rate limits on every pull request.

So run this by hand every so often -- see "When to run it" below.

What it checks, per mapping row
-------------------------------
  1. the object CURIE's prefix is declared in the file's curie_map;
  2. the object IRI actually RESOLVES to a term in OLS;
  3. `object_label` matches what the source ontology actually calls that term.

Check 3 is the one that catches slow rot: source ontologies relabel and
obsolete terms over time, and nothing tells us when they do.

What it CANNOT check
--------------------
Whether the mapping is *correct* -- that the two terms really mean the same
thing. That is a judgement call and stays a human job. A resolving IRI with a
matching label can still be a false friend: `MI:1053 data source` resolves
perfectly and is nonetheless a curation-provenance slot, not a database, so it
was rejected. See dev-artefacts/external-ontology-decisions.md.

When to run it
--------------
  * before cutting a release, so published mappings are known-live;
  * after adding a batch of mappings, as a second pair of eyes;
  * roughly every few months, to catch upstream relabels and obsoletions;
  * before submitting to OBO Foundry.

How to run it
-------------
Needs network access. No dependencies beyond the standard library, so plain
python3 is enough -- no Docker needed:

    # from the repo root
    python3 src/scripts/audit_sssom_objects.py

    # quieter: only show problems
    python3 src/scripts/audit_sssom_objects.py --quiet

    # be gentle with the OLS API (default 0.2s between calls)
    python3 src/scripts/audit_sssom_objects.py --delay 0.5

    # point at a different mapping file
    python3 src/scripts/audit_sssom_objects.py --mapping-file path/to/other.sssom.tsv

Roughly 80 rows takes about a minute. Exits 0 if everything resolves with
matching labels, 1 if anything needs attention.

Known API quirk
---------------
OLS `short_form` can name the wrong ontology (`AFO__0001025` is really
`PATO_0001025`), so this script matches on the full IRI and never trusts
short_form. Non-OBO sources still work as long as OLS indexes them: EDAM, KiSAO
(`biomodels.net/kisao/...`) and SWO all resolve by IRI.
"""

import argparse
import csv
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

OLS_SEARCH = "https://www.ebi.ac.uk/ols4/api/search"
DEFAULT_MAPPING = Path("src/ontology/mappings/molsim.sssom.tsv")


def read_curie_map(raw: str):
    """Pull the prefix -> namespace map out of the '#' header comment block."""
    return {
        m.group(1): m.group(2)
        for m in re.finditer(r"#\s{3}([\w.]+):\s+(http\S+)", raw)
    }


def read_rows(raw: str):
    lines = [line for line in raw.splitlines() if line and not line.startswith("#")]
    return list(csv.DictReader(lines, delimiter="\t"))


def resolve(iri: str, timeout: int = 25):
    """Return the OLS label for an exact IRI match, or None if not found."""
    url = (
        OLS_SEARCH
        + "?q="
        + urllib.parse.quote(iri)
        + "&queryFields=iri&exact=true&rows=5"
    )
    with urllib.request.urlopen(url, timeout=timeout) as response:
        data = json.load(response)
    for doc in data.get("response", {}).get("docs", []):
        # Match on the full IRI: OLS short_form is unreliable (see docstring).
        if doc.get("iri") == iri:
            return doc.get("label", "")
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mapping-file", default=str(DEFAULT_MAPPING))
    parser.add_argument("--delay", type=float, default=0.2, help="seconds between API calls")
    parser.add_argument("--quiet", action="store_true", help="only print problems")
    args = parser.parse_args()

    path = Path(args.mapping_file)
    if not path.exists():
        print(f"ERROR: cannot find {path}", file=sys.stderr)
        return 2

    raw = path.read_text(encoding="utf-8")
    curie_map = read_curie_map(raw)
    rows = read_rows(raw)

    resolved = 0
    problems = []

    for row in rows:
        curie = row.get("object_id", "")
        file_label = (row.get("object_label") or "").strip()
        prefix, _, local = curie.partition(":")

        if prefix not in curie_map:
            problems.append((curie, "prefix not declared in curie_map", ""))
            continue
        iri = curie_map[prefix] + local

        try:
            ols_label = resolve(iri)
        except Exception as exc:  # network hiccup should not abort the whole run
            problems.append((curie, "lookup error", type(exc).__name__))
            continue

        if ols_label is None:
            problems.append((curie, "does not resolve in OLS", f"file says {file_label!r}"))
            continue

        resolved += 1
        if ols_label.strip().lower() != file_label.lower():
            problems.append(
                (curie, "object_label differs from source", f"OLS={ols_label!r} file={file_label!r}")
            )
        elif not args.quiet:
            print(f"OK   {curie:18} {ols_label}")

        time.sleep(args.delay)

    print(
        f"\nSUMMARY  {len(rows)} row(s): {resolved} resolved, "
        f"{len(problems)} problem(s)"
    )
    if problems:
        print("\nPROBLEMS -- each needs a human decision:")
        for curie, what, detail in problems:
            print(f"  {curie:18} {what}" + (f"  [{detail}]" if detail else ""))
        print(
            "\nA relabel upstream usually just means updating object_label here.\n"
            "A term that no longer resolves may have been obsoleted -- check the\n"
            "source ontology and record the decision in\n"
            "dev-artefacts/external-ontology-decisions.md."
        )
        return 1

    print("All object terms resolve and every label matches the source ontology.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
