# Troubleshooting

### Issue: Error after updating the repository

When updating the repository (`sh run.sh update_repo` ), you may encounter an error like the one below:

```
INFO:root:OUT: UNKNOWN ARG ERROR unknown command or option: odk:import

...

Exception: Failed: robot odk:import -i molsim-edit.owl --exclusive true --add http://purl.obolibrary.org/obo/molsim/imports/uo_import.owl --add http://purl.obolibrary.org/obo/molsim/imports/chebi_import.owl --add http://purl.obolibrary.org/obo/molsim/imports/ncit_import.owl --add http://purl.obolibrary.org/obo/molsim/components/molsim_units_component.owl convert -f ofn -o molsim-edit.owl
```

### Possible Cause

This issue typically occurs when there is a problem with **imported ontologies** in your configuration.

### Recommended Fix

1. Identify the ontology import suspected to cause the issue.  
2. Remove or comment it (in this case, ncit) out from the following files:

   - `molsim-odk.yaml`
   - `molsim-edit.owl`
   - `catalog-v0001.xml`
   - `molsim.Makefile`

3. Rebuild the ontology using the usual ODK commands (`sh run.sh update_repo` or the corresponding step in your workflow).

### Reference Example

You can look at **commit [`1232391bdcb6b41964ce71d7cd73335dfe4ef096`](https://github.com/CPCLab/molsim-ontology/commit/1232391bdcb6b41964ce71d7cd73335dfe4ef096)** opn the files mentioned above for an example of how these changes were made.