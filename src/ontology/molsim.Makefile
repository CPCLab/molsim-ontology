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
# $(IMPORTDIR)/ncit_import_no_intermediate.owl: $(MIRRORDIR)/ncit.owl
#	$(ROBOT) extract --input $< \
#		--method MIREOT \
#		--lower-terms $(IMPORTDIR)/ncit_terms.txt \
#		--intermediates none \
#		--output $@
# $(IMPORTDIR)/iao_import_no_intermediate.owl: $(MIRRORDIR)/iao.owl
#	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/iao_terms.txt \
		--intermediates none \
		--output $@
$(COMPONENTSDIR)/molsim_units_component.owl: $(SRC) templates/molsim_units_component.tsv
	$(ROBOT) template --template templates/molsim_units_component.tsv \
		--prefix "MOLSIM: http://purl.obolibrary.org/obo/MOLSIM_" \
		--ontology-iri $(ONTBASE)/components/molsim_units_component.owl \
	annotate --ontology-iri $(ONTBASE)/@ --output $(COMPONENTSDIR)/molsim_units_component.owl
