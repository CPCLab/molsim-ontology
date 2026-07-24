## Customize Makefile settings for molsim
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile

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