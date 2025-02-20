## Customize Makefile settings for molsim
## 
## If you need to customize your Makefile, make
## changes here rather than in the main Makefile
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl
	$(ROBOT) extract --input $< \
		--method MIREOT \
		--lower-term "UO:0000019" \
		--lower-term "UO:0000063" \
		--lower-term "UO:0000030" \
		--lower-term "UO:0000150" \
		--lower-term "UO:0000094" \
		--output $@
