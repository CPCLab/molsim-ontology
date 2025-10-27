

## Importing and Defining Unit Terms

This guide explains two methods for incorporating unit terms into the MOLSIM ontology:

1.  **Importing Existing Terms**: For terms that already exist in an ontology like the Unit Ontology (UO).
2.  **Defining New Terms**: For custom terms that are not available in imported ontologies.

### Method 1: Importing Existing Unit Terms from UO

This method is ideal when the unit terms you need are already defined in the Unit Ontology.

#### 1. Add Terms to the Import File

Open `/src/ontology/imports/uo_terms.txt` and add the unique identifiers (IRIs) of the UO terms you wish to import, each on a new line.

For example:
```
UO:0000010
UO:0000109
```

#### 2. Extract the Terms

Run the following ROBOT command to extract the specified terms and their related axioms from the Unit Ontology:

```bash
sh run.sh robot extract --method MIREOT \
    --input mirror/uo.owl \
    --lower-terms imports/uo_terms.txt \
    --output imports/uo_import.owl
```

**Explanation of the command:**
*   `--method MIREOT`: This specifies the "Minimum Information to Reference an External Ontology Term" method, which is recommended when you primarily need the term's hierarchy and basic information.
*   `--input mirror/uo.owl`: The source ontology from which to extract terms.
*   `--lower-terms imports/uo_terms.txt`: The file containing the list of term IDs to be extracted.
*   `--output imports/uo_import.owl`: The file where the extracted subset of the ontology will be saved.

#### 3. Integrate the Imported Terms

Finally, run the following ODK commands to update the repository and integrate the newly imported terms into the MOLSIM ontology:

```bash
sh run.sh make update_repo         # Update the repository
sh run.sh make refresh-uo          # Refresh the Unit Ontology import
sh run.sh make prepare_release     # Integrate ontology imports with components
```

### Method 2: Defining New Custom Unit Terms

Use this method when a required unit term is not available in the UO or other imported ontologies. This process uses ROBOT templates to create new terms within the MOLSIM ontology.

#### 1. Modify the Template File

Open the template file at `/src/ontology/templates/molsim_units_component.tsv` and add a new row for each custom term you want to define. Follow the existing structure of the TSV file, providing a unique `ID`, `Label`, `Alternative Term`, `Definition`, and `Parent Class`.

For example, to add a new unit, you would add a line like this:

```
MOLSIM:010006    newton per meter    N/m    A unit of stiffness.    UO:0000111
```

#### 2. Rebuild the Component and Integrate

After modifying and saving the template, run the following commands to generate the new ontology component and integrate it into the main ontology:

```bash
sh run.sh make components/molsim_units_component.owl  # Rebuild the component
sh run.sh make prepare_release     # Integrate ontology imports with components
```

By following these steps, you can systematically expand the MOLSIM ontology with both existing and custom unit terms to meet the specific needs of your domain.