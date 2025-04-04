## Customize Makefile settings for molsim
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/uo_terms.txt \
		--output $@
$(IMPORTDIR)/chebi_import.owl: $(MIRRORDIR)/chebi.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/chebi_terms.txt \
		--output $@
#$(IMPORTDIR)/ncit_import.owl: $(MIRRORDIR)/ncit.owl
#	$(ROBOT) extract --input $< \
#		--method MIREOT \
#		--lower-terms $(IMPORTDIR)/ncit_terms.txt \
#		--output $@
$(COMPONENTSDIR)/molsim_units_component.owl: $(SRC) templates/molsim_units_component.tsv
	$(ROBOT) template --template templates/molsim_units_component.tsv \
		--prefix "MOLSIM: http://purl.obolibrary.org/obo/MOLSIM_" \
		--ontology-iri $(ONTBASE)/components/molsim_units_component.owl \
	annotate --ontology-iri $(ONTBASE)/@ --output $(COMPONENTSDIR)/molsim_units_component.owl
