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

# ---------------------------------------------------------------------------
# Mirror download for go, overriding the generated rule
# ---------------------------------------------------------------------------
# The generated Makefile writes a download rule for every ontology in its IMPORTS
# list. Until `make update_repo` was run on 2026-08-13 that list read
# "ro iao omo uo chebi", so SO, GO and STATO had no download rule at all, and 3
# rules were written here by hand. The regenerated list now reads
# "ro iao omo uo so go stato chebi", so the SO and STATO rules became exact
# duplicates and were deleted. This 1 stays, because the generated version of it
# does not work.
#
# GO must be downloaded uncompressed. molsim-odk.yaml sets use_gzipped: TRUE for
# it, so the generated rule asks for http://purl.obolibrary.org/obo/go.owl.gz,
# and that address answers 404. go.owl answers 200 and is 130 MB. Both checked on
# 2026-08-12 and again on 2026-08-13. The longer --max-time reflects the size:
# 200 seconds would demand 650 KB/s for the whole download.
#
# Make warns "overriding recipe for target 'mirror-go'", keeps the LATER
# definition and discards the earlier one. `include molsim.Makefile` is the last
# line of the generated Makefile, so the working rule is the one that runs. That
# warning is deliberate here. Do not silence it by deleting this rule.
#
# DELETE THIS SECTION if the OBO server ever starts publishing go.owl.gz, or if
# use_gzipped is turned off for GO in molsim-odk.yaml. Check the address answers
# 200 before removing it.
#
# Why the original gap was worth fixing at all, recorded so it is not relearned.
# The failure was silent, not loud. Tested by counterfactual on 2026-08-12: with
# no rule present, `make mirror/go.owl MIR=true` did NOT fail. It answered
# "Nothing to be done for 'mirror/go.owl'", because make finds a file that
# exists, finds no rule that can remake it, and treats it as a source file it was
# handed. A mirror refresh looked like it had succeeded while quietly skipping 3
# ontologies, and the import modules were then built from whatever copy happened
# to be on disk, however old. The loud failure only arrives on a machine that
# does not already have the file, and mirror/ is gitignored, so that means every
# fresh clone.
ifeq ($(MIR),true)

.PHONY: mirror-go
.PRECIOUS: $(MIRRORDIR)/go.owl
mirror-go: | $(TMPDIR)
	curl -L $(OBOBASE)/go.owl --create-dirs -o $(TMPDIR)/go-download.owl --retry 4 --max-time 1200 && \
	$(ROBOT) convert -i $(TMPDIR)/go-download.owl -o $(TMPDIR)/$@.owl

endif # MIR=true

# Custom import modules. Guarded by IMP=true (like the standard rules in the main
# Makefile) so that when imports are NOT being rebuilt (IMP=false, e.g. in CI/QC),
# the committed imports/*_import.owl are treated as static files and do not require
# the mirror/*.owl sources to be present. Only an actual import refresh (IMP=true,
# MIR=true) needs the mirrors.
ifeq ($(IMP),true)
# NOTE on the two mirrors that are not present locally, measured 2026-08-12.
# mirror/uo.owl does not exist at all, and the ChEBI mirror is mirror/chebi.owl.gz while
# the rule below asks for mirror/chebi.owl. Both rules are correct as written and both now
# depend on their terms file, but neither can be rebuilt offline: make stops with "No rule
# to make target". This is a cold cache rather than a defect, because the generated
# Makefile does hold a download rule for each of them, so MIR=true and a network
# connection restore both. The go and stato rules were tested and both now rebuild when
# their terms file changes.
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl $(IMPORTDIR)/uo_terms.txt
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/uo_terms.txt \
		--output $@

# SO: two extractions from the same mirror, merged into one file.
# Two extractions are needed because the two groups of terms want opposite treatment.
#
# (1) so_terms.txt -- UNBOUNDED MIREOT (no --upper-terms).
#     Unbounded means robot also brings in each term's ancestors. This group needs that:
#       - the MDDB base modifications, SO:0001918 5_methylcytosine and its siblings, get
#         their place in the tree from SO:0000305 modified_DNA_base;
#       - SO:0001078 polypeptide_secondary_structure needs its link up to
#         SO:0001070 polypeptide_structural_region, which molsim-edit.owl in turn places
#         under MOLSIM:002090 molecular entity.
#     Bound this group and those classes arrive with no parent, breaking both.
#
# (2) so_ss_terms.txt -- BOUNDED MIREOT (--upper-terms same as --lower-terms).
#     Bounded means no ancestors at all: each class arrives bare. That is what we want
#     here, because molsim-edit.owl states the parents itself. It puts
#     SO:0001114 peptide_helix under MOLSIM:001781 secondary structure, and puts the three
#     helix types under SO:0001114 peptide_helix.
#     Staying bare avoids two problems:
#       - SO:0001116 right_handed_peptide_helix would come along as well. It is an extra
#         level between the helix and its types that MOLSIM has no use for.
#       - the path up to SO:0001078 polypeptide_secondary_structure would be added a
#         second time, so SO:0001114 peptide_helix would reach the same ancestor by two
#         routes. Harmless to the reasoner, but confusing to read.
#
# Merging the two results keeps this a single import module. That means no extra Import()
# line in molsim-edit.owl, no extra catalog-v001.xml entry, and no new ODK import_group
# product (which would also need a mirror of its own).
#
# The two terms files are listed as prerequisites deliberately. Without them make only
# compares the module against the mirror, finds the module is newer, and does nothing when
# you edit a terms list. The uo, go, stato and chebi rules in this file still have that
# gap, so editing their terms lists needs a forced rebuild.
$(IMPORTDIR)/so_import.owl: $(MIRRORDIR)/so.owl $(IMPORTDIR)/so_terms.txt $(IMPORTDIR)/so_ss_terms.txt
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/so_terms.txt \
		--output $(TMPDIR)/so_base.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/so_ss_terms.txt \
		--upper-terms $(IMPORTDIR)/so_ss_terms.txt \
		--output $(TMPDIR)/so_secondary_structure.owl
	$(ROBOT) merge --input $(TMPDIR)/so_base.owl \
		--input $(TMPDIR)/so_secondary_structure.owl \
		--output $@

# GO: bounded MIREOT (upper == lower) so only the listed leaf terms are pulled,
# NOT their ancestors — this deliberately avoids dragging in GO cellular_component,
# COB, or BFO upper-ontology classes (MOLSIM policy: no new upper-ontology imports).
$(IMPORTDIR)/go_import.owl: $(MIRRORDIR)/go.owl $(IMPORTDIR)/go_terms.txt
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/go_terms.txt \
		--upper-terms $(IMPORTDIR)/go_terms.txt \
		--output $@

# STATO: bounded MIREOT (upper == lower). STATO's ancestors run
# STATO:0000039 statistic -> IAO:0000027 data item -> IAO:0000030 information content
# entity -> BFO:0000031 -> BFO:0000001, so an unbounded extraction would inject IAO and
# BFO upper-ontology parentage (MOLSIM policy: no new upper-ontology imports).
$(IMPORTDIR)/stato_import.owl: $(MIRRORDIR)/stato.owl $(IMPORTDIR)/stato_terms.txt
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/stato_terms.txt \
		--upper-terms $(IMPORTDIR)/stato_terms.txt \
		--output $@

$(IMPORTDIR)/chebi_import.owl: $(MIRRORDIR)/chebi.owl $(IMPORTDIR)/chebi_terms.txt
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/chebi_terms.txt \
		--output $@

# IAO: take EXACTLY the requested terms and nothing above them.
#
# The generic ODK rule uses --method BOT over a seed built from the whole ontology.
# IAO's own classes are BFO subclasses, so that pulls BFO's entire top level into the
# module and into every release. Measured 2026-08-12: 12 BFO classes were published
# while no MOLSIM class had a BFO parent. Editing the terms file does not fix it,
# because the properties MOLSIM uses pull their domains and ranges, and those are the
# BFO subclasses.
#
# Bounded MIREOT does not work here either: MIREOT is class-oriented, and every seed
# in iao_terms.txt is currently a property, so it produced an empty module. `filter`
# with `self` takes each named term with its own annotations and no ancestry, which is
# the same approach the RO import already uses.
#
# THIS RULE MUST STAY INSIDE THE IMP=true GUARD. It sat outside it from 2026-08-12
# until later the same day, and CI failed with "No rule to make target
# 'mirror/iao.owl'". The reason is that mirror/ is gitignored, so a CI checkout has an
# empty mirror directory. With IMP=false the committed imports/*_import.owl are meant
# to be treated as static files that need no mirror at all, and a rule declared outside
# the guard breaks that promise: make sees the dependency, cannot satisfy it, and stops
# before any test runs. It passed locally only because this machine happens to have a
# copy of the mirror.
$(IMPORTDIR)/iao_import.owl: $(MIRRORDIR)/iao.owl $(IMPORTDIR)/iao_terms.txt
	$(ROBOT) filter --input $< \
		--term-file $(IMPORTDIR)/iao_terms.txt \
		--select "self annotations" \
		--signature true \
		--trim true \
		annotate --ontology-iri $(ONTBASE)/imports/iao_import.owl \
		convert -f ofn \
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


# RO: overrides the ODK-generated rule at Makefile:413.
#
# ro_terms.txt asks for 7 terms but only 5 arrived. The 2 missing are
# BFO:0000051 has part and BFO:0000063 precedes, which RO declares under a BFO
# URI prefix, as the terms file itself notes. The generated recipe deleted them
# with `remove --axioms external --base-iri .../RO`, which keeps only the RO
# namespace. Adding the BFO namespace lets the 2 requested properties survive.
#
# Nothing of BFO's hierarchy comes with them. The SECOND remove below keeps only
# the terms listed in ro_terms.txt, so BFO:0000003 occurrent, the domain and
# range of precedes, and its property chains are all dropped. Each property
# arrives bare: a declaration, a label and a definition, exactly like the 5
# already there.
$(IMPORTDIR)/ro_import.owl: $(MIRRORDIR)/ro.owl $(IMPORTDIR)/ro_terms.txt $(IMPORTSEED) | all_robot_plugins
	$(ROBOT) annotate --input $< --remove-annotations \
		 odk:normalize --add-source true \
		 extract --term-file $(IMPORTDIR)/ro_terms.txt $(T_IMPORTSEED) \
		         --copy-ontology-annotations true --force true --method BOT \
		 remove --axioms external --preserve-structure false --trim false \
		        --base-iri http://purl.obolibrary.org/obo/RO \
		        --base-iri http://purl.obolibrary.org/obo/BFO \
		 remove $(foreach p, $(ANNOTATION_PROPERTIES), --term $(p)) \
		        --term rdfs:label \
		        --term IAO:0000115 \
		        --term OMO:0002000 \
		        --term-file $(IMPORTDIR)/ro_terms.txt $(T_IMPORTSEED) \
		        --select complement \
		 odk:normalize --base-iri http://purl.obolibrary.org/obo \
		               --subset-decls true --synonym-decls true \
		 repair --merge-axiom-annotations true \
		 $(ANNOTATE_CONVERT_FILE)
