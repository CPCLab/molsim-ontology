# Using ROBOT Templates with MOLSIM Ontology

This tutorial explains how to add custom components to the MOLSIM ontology using ROBOT templates for terms that are not available in imported ontologies, such as the Unit Ontology (UO).

## Overview

ROBOT templates provide a spreadsheet-based approach to ontology development, allowing domain experts to contribute to ontologies without needing to write OWL directly. This approach is particularly useful for adding multiple similar terms with consistent structure.

## Step-by-Step Process

### 1. Create a Template File

Create a TSV (Tab-Separated Values) file listing the terms you want to add, including their ID, Label, Alternative Term, Definition, and Parent Class. These are mapped to ontological terms in the header row.

Save this file as `/src/ontology/templates/molsim_units_component.tsv`:

```
ID	Label	Alternative Term	Definition	Parent Class
ID	A rdfs:label	A oboInOwl:hasExactSynonym	A IAO:0000115	SC %
MOLSIM:000214	femtosecond	fs	An SI unit of time equal to 10^-15 seconds or one quadrillionth of a second.	UO:1000010
MOLSIM:000215	atmosphere	atm	A unit of pressure defined as 101,325 pascals (Pa) or 1.01325 bar, approximately equal to the average atmospheric pressure at sea level on Earth.	UO:0000109
MOLSIM:000464	angstrom per nanosecond	Å/ns|angstrom/nanosecond	A unit of velocity, representing one angstrom (10^-10 meters) of distance traveled per nanosecond (10^-9 seconds) of time. It is commonly used in molecular dynamics simulations and studies of atomic-scale processes.	UO:0000060
MOLSIM:000485	kilocalorie per mole	kcal/mol|kilocalorie/mole	A unit of energy per amount of substance, defined as one kilocalorie of energy (1000 thermochemical gram calories) per one mole of substance. It is commonly used in chemistry and biology for thermodynamic quantities.	UO:0000111
MOLSIM:000486	kilocalorie per mole per square angstrom	kcal/mol/Å^2|kilocalorie/mole/angstrom^2	A unit of energy per amount of substance per area, commonly used in molecular dynamics simulations for expressing force constants and restraint weights.	UO:0000111
```

### 2. Update the Makefile

Open `/src/ontology/molsim.Makefile` and add the following rule to specify how the component should be generated:

```makefile
$(COMPONENTSDIR)/molsim_units_component.owl: $(SRC) templates/molsim_units_component.tsv
	$(ROBOT) template --template templates/molsim_units_component.tsv \
	--prefix "MOLSIM: http://purl.obolibrary.org/obo/MOLSIM_" \
	--ontology-iri $(ONTBASE)/components/molsim_units_component.owl \
	annotate --ontology-iri $(ONTBASE)/@ --output $(COMPONENTSDIR)/molsim_units_component.owl
```

This rule tells ROBOT to:
- Use the template file we created
- Define the MOLSIM prefix
- Set the appropriate ontology IRI
- Output the result to the components directory

### 3. Create Components Directory

Create the directory `/src/ontology/components/` if it doesn't already exist:

```bash
mkdir -p src/ontology/components/
```

### 4. Generate the Component File

Run the following command to create the component file:

```bash
sh run.sh make components/molsim_units_component.owl
```

This will process the template and generate `/src/ontology/components/molsim_units_component.owl`.

### 5. Update the ODK Configuration

Open `/src/ontology/molsim-odk.yaml` and add the following configuration to register the component:

```yaml
components:
  products:
    - filename: molsim_units_component.owl    
```

This tells ODK to include this component in the ontology build process.

### 6. Update and Integrate

Run the following ODK commands to update the repository and integrate the new component:

```bash
sh run.sh make update_repo         # update the repository
sh run.sh make refresh-uo          # refresh unit ontology import
sh run.sh make components/molsim_units_component.owl  # rebuild the component
sh run.sh make prepare_release     # integrate ontology imports with components
```

### 7. Verify the Results

After running these commands, verify that the components have been added to the ontology following the class hierarchy specified in the TSV template.

## Template Structure Explanation

The template uses the following columns:
- **ID**: The unique identifier for the term (MOLSIM:xxxxxx)
- **Label**: The primary name of the term (rdfs:label)
- **Alternative Term**: Synonyms for the term (oboInOwl:hasExactSynonym)
- **Definition**: The formal definition of the term (IAO:0000115)
- **Parent Class**: The superclass of the term (SC %)

Multiple alternative terms can be specified using the pipe character (|) as a separator.

## Further Resources

- [ROBOT Template Documentation](http://robot.obolibrary.org/template)
- [ODK Documentation](https://github.com/INCATools/ontology-development-kit/blob/master/docs/index.md)
- [OBO Foundry Principles](https://obofoundry.org/principles/fp-000-summary.html)