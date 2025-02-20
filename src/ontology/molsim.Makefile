## Customize Makefile settings for molsim
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-terms $(IMPORTDIR)/uo_terms.txt \
		--output $@
