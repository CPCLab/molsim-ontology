## Customize Makefile settings for molsim
##
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

# ---------------------------------------------------------------------------
# QC: SPARQL validation checks
# ---------------------------------------------------------------------------
# Declared HERE, not in the main Makefile, because the main Makefile is
# ODK-generated and says "DO NOT EDIT" at the top: a `make update_repo` (ODK
# version bump) regenerates it and would silently drop any custom entries.
# Losing them is the bad kind of failure -- the queries in ../sparql/ would
# still exist, but nothing would run them, so CI would go green while
# enforcing neither invariant.
#
# `include molsim.Makefile` is the LAST line of the main Makefile, and
# SPARQL_VALIDATION_QUERIES is a recursively-expanded (`=`) variable, so the
# value set here wins wherever the list is expanded during the build.
#
#   stock ODK checks : owldef-self-reference iri-range label-with-iri
#                      multiple-replaced_by dc-properties
#   MOLSIM-specific  : verification-state    -- every MOLSIM term must be in
#                        exactly one state (verified / unverified / deprecated)
#                      noncanonical-marker   -- the (UNVERIFIED) marker must be
#                        the last thing in the definition string, because the
#                        verification pipeline strips it by string matching
SPARQL_VALIDATION_CHECKS = owldef-self-reference iri-range label-with-iri \
                           multiple-replaced_by dc-properties \
                           verification-state noncanonical-marker

# ---------------------------------------------------------------------------
# QC: SSSOM mapping file
# ---------------------------------------------------------------------------
# Nothing in the ODK build reads mappings/molsim.sssom.tsv: MAPPINGS is empty,
# so MAPPING_FILES expands to nothing and the file is neither tested nor
# released. Validate it explicitly and hang it off `test`, so CI covers it.
#
# Call `sssom validate` with NO -V flag on purpose. The tool advertises five
# validation types but only implements three; the default is exactly those
# three (JsonSchema, PrefixMapCompleteness, StrictCurieFormat). Passing
# -V Shacl or -V Sparql raises NotImplementedError from an empty stub for any
# input, which would make the build permanently red for no reason.
#
# The path is literal because MAPPINGDIR is not defined by the ODK Makefile.
SSSOM_FILE = mappings/molsim.sssom.tsv

# Two checks, because they catch different things:
#
#   sssom validate            -- is the FILE well formed? (columns, declared
#                                prefixes, CURIE shape). It never opens an
#                                ontology, so it accepts a mapping whose subject
#                                does not exist: rewriting a row to
#                                MOLSIM:009999 -> NCIT:C99999999 still exits 0.
#
#   check_sssom_subjects.py   -- is the mapping TRUE on our side? Every subject
#                                must be declared, not deprecated, and its label
#                                and type must match molsim-edit.owl. This is
#                                the failure that actually happens: a mistyped
#                                ID that lands on a real but different term.
#                                Offline and deterministic, so it is safe in CI.
#
# The OBJECT side is NOT checked here -- it needs the network, which would break
# offline builds and depend on OLS uptime. Run src/scripts/audit_sssom_objects.py
# by hand instead (before a release, after a mapping batch, or every few months).
.PHONY: sssom_test
sssom_test:
	sssom validate $(SSSOM_FILE)
	python3 ../scripts/check_sssom_subjects.py --mapping-file $(SSSOM_FILE)

test: sssom_test

# Custom import modules. Guarded by IMP=true (like the standard rules in the main
# Makefile) so that when imports are NOT being rebuilt (IMP=false, e.g. in CI/QC),
# the committed imports/*_import.owl are treated as static files and do not require
# the mirror/*.owl sources to be present. Only an actual import refresh (IMP=true,
# MIR=true) needs the mirrors.
ifeq ($(IMP),true)
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/uo_terms.txt \
		--output $@

$(IMPORTDIR)/so_import.owl: $(MIRRORDIR)/so.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/so_terms.txt \
		--output $@

# GO: bounded MIREOT (upper == lower) so only the listed leaf terms are pulled,
# NOT their ancestors — this deliberately avoids dragging in GO cellular_component,
# COB, or BFO upper-ontology classes (MOLSIM policy: no new upper-ontology imports).
$(IMPORTDIR)/go_import.owl: $(MIRRORDIR)/go.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/go_terms.txt \
		--upper-terms $(IMPORTDIR)/go_terms.txt \
		--output $@

# STATO: bounded MIREOT (upper == lower). STATO's ancestors run
# STATO:0000039 statistic -> IAO:0000027 data item -> IAO:0000030 information content
# entity -> BFO:0000031 -> BFO:0000001, so an unbounded extraction would inject IAO and
# BFO upper-ontology parentage (MOLSIM policy: no new upper-ontology imports).
$(IMPORTDIR)/stato_import.owl: $(MIRRORDIR)/stato.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/stato_terms.txt \
		--upper-terms $(IMPORTDIR)/stato_terms.txt \
		--output $@

$(IMPORTDIR)/chebi_import.owl: $(MIRRORDIR)/chebi.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/chebi_terms.txt \
		--output $@
endif

$(COMPONENTSDIR)/molsim_units_component.owl: $(SRC) templates/molsim_units_component.tsv
	$(ROBOT) template --template templates/molsim_units_component.tsv \
		--prefix "MOLSIM: http://purl.obolibrary.org/obo/MOLSIM_" \
		--ontology-iri $(ONTBASE)/components/molsim_units_component.owl \
		annotate --ontology-iri $(ONTBASE)/$@ --output $@

.PHONY: release-nobfo
release-nobfo: all
	@echo "Scrubbing BFO from release files..."
	$(ROBOT) remove -i $(ONT)-full.owl \
		--term BFO:0000001 \
		--select "self descendants" \
		--preserve-structure false \
		-o $(ONT)-full.owl
	$(ROBOT) remove -i $(ONT).owl \
		--term BFO:0000001 \
		--select "self descendants" \
		--preserve-structure false \
		-o $(ONT).owl
	$(ROBOT) remove -i $(ONT)-base.owl \
		--term BFO:0000001 \
		--select "self descendants" \
		--preserve-structure false \
		-o $(ONT)-base.owl
	@echo "Done! BFO hierarchy has been removed."