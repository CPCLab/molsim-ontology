#!/usr/bin/env bash
# Warn when the built release no longer matches the ontology it came from.
#
# The release files at the repository root are built by hand, so they can fall
# behind src/ontology/molsim-edit.owl without anyone noticing. That is not a
# theoretical risk. The COB alignment removed BFO from the edit file, nobody
# rebuilt the release, and for 2 days every download still contained 17 BFO
# classes while the repository said the upper ontology had been removed.
#
# This warns; it never fails the build. A release that has fallen behind is
# fixed in its own commit, and blocking an unrelated term edit would not help.
#
# Run by the CI workflow, and usable by hand from the repository root.
set -uo pipefail

ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
[ -n "$ROOT" ] || { echo "not inside a git repository"; exit 0; }
cd "$ROOT" || exit 0

EDIT=src/ontology/molsim-edit.owl
RELEASE=molsim.obo

base="${GITHUB_BASE_REF:-main}"
ref="origin/$base"
git rev-parse --verify -q "$ref" >/dev/null || ref="$base"
git rev-parse --verify -q "$ref" >/dev/null || {
  echo "  Cannot see the $base branch, so no comparison is possible."
  echo "  The checkout needs fetch-depth: 0 for this check to work."
  exit 0
}

warned=0

# 1. Has the edit file moved on since the release was last built?
last_rel=$(git log -1 --format=%H -- molsim.owl 2>/dev/null)
if [ -z "$last_rel" ]; then
  echo "  No release artefact is committed yet, so there is nothing to compare."
else
  behind=$(git log --oneline "$last_rel"..HEAD -- "$EDIT" | wc -l)
  if [ "$behind" -gt 0 ]; then
    warned=1
    printf '::warning file=%s::The release artefacts are behind the edit file. %s commit(s) changed %s after the last release build, so molsim.owl and molsim.obo no longer describe this ontology. Rebuild them before releasing.\n' \
      "$EDIT" "$behind" "$EDIT"
    printf '  BEHIND: %s edit-file commit(s) since the last release build.\n' "$behind"
  else
    echo "  The release is level with the edit file."
  fi
fi

# 2. Has an ontology appeared in the release that was not there before?
# This is the check that would have caught the 17 BFO classes.
if git show "$ref:$RELEASE" >/dev/null 2>&1 && [ -f "$RELEASE" ]; then
  appeared=$(comm -13 \
    <(git show "$ref:$RELEASE" | grep -oP '^id: \K[A-Z]+' | sort -u) \
    <(grep -oP '^id: \K[A-Z]+' "$RELEASE" | sort -u) | paste -sd' ')
  if [ -n "$appeared" ]; then
    warned=1
    printf '::warning file=%s::Classes from %s now appear in the release and did not appear on %s. An unbounded import can pull in an upper ontology nobody chose, which is how 17 BFO classes reached a published release. Confirm this was intended.\n' \
      "$RELEASE" "$appeared" "$base"
    printf '  NEW IN THE RELEASE: %s\n' "$appeared"
  else
    echo "  No ontology newly appears in the release."
  fi
fi

[ "$warned" -eq 0 ] && echo "  Nothing to warn about."
echo "  This check only reports. It never fails the build."
exit 0
