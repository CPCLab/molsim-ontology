# Custom Ontology Import Tutorial for MOLSIM via ODK

This tutorial explains how to import specific terms from external ontologies into the MOLSIM ontology using the Ontology Development Kit (ODK). MOLSIM uses custom imports to fetch relevant terms along with their superclasses.

Ontology Diagram

## Example: Importing Terms from Unit Ontology (UO)

For example, we extract the following terms from the unit ontology (UO):

```
UO:0000019 # angstrom
UO:0000063 # nanosecond
UO:0000030 # meter per second
UO:0000150 # millimolar
UO:0000094 # unit of molarity
```

## Desired Extraction Result

In our ideal use case, we extract these terms along with their superclasses. The resulting extraction hierarchy would look like:

```
unit
├── length unit
│   └── angstrom based unit
│       └── angstrom
├── concentration unit
│   └── unit of molarity
│       └── molar based unit
│           └── millimolar
├── time unit
│   └── second based unit
│       ├── picosecond
│       └── nanosecond
└── speed/velocity unit
    └── meter per second based unit
        └── meter per second
```

## ROBOT vs ODK Approach

While this can be done individually using ROBOT with MIREOT as the extraction method:

```bash
sh run.sh robot extract --method MIREOT \
 --input mirror/uo.owl \
 --lower-term "UO:0000019" \
 --lower-term "UO:0000063" \
 --lower-term "UO:0000030" \
 --lower-term "UO:0000150" \
 --lower-term "UO:0000094" \
 --output extracted_unit.owl
```

We prefer using ODK for its streamlined approach to ontology development, which includes import management, CI/CD, and documentation. ODK integrates ROBOT in its package, but its YAML configuration doesn't directly support MIREOT as an extraction method.

## Configuration Steps

To implement custom imports with ODK, configure these four main files:

### 1. Initial molsim-odk.yaml Configuration

This file creates the initial seed. Pay particular attention to:

```yaml
allow_equivalents: all

import_group:
 products:
   - id: uo
```

After saving, run the seed command:

```bash
curl https://raw.githubusercontent.com/INCATools/ontology-development-kit/refs/heads/master/seed-via-docker.sh | bash -s -- --clean -C molsim-odk.yaml
```

A successful seeding command will generate a set of files and folders. Push the content of the `target` directory to GitHub. Check `/src/ontology/molsim-odk.yaml` for the detailed configuration made for MOLSIM.

### 2. Modify the content of the molsim-odk.yaml Configuration file

To implement MIREOT extraction, use custom mode in the `/src/ontology/molsim-odk.yaml` configuration. This can be achieved by:

```yaml
allow_equivalents: all

import_group:
 products:
   - id: uo
     module_type: custom
```

Save the configuration file.

### 3. Configure Terms to Import

Add the list of terms you want to import to `src/ontology/imports/uo_terms.txt`, for example:

```
UO:0000019 # angstrom
UO:0000063 # nanosecond
UO:0000030 # meter per second
UO:0000150 # millimolar
UO:0000094 # unit of molarity
```

### 4. Update molsim.Makefile

Add the following rule to the `molsim.Makefile` to specify how the import should be generated:

```makefile
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl
    $(ROBOT) extract --input $< \
        --method MIREOT \
        --lower-terms $(IMPORTDIR)/uo_terms.txt \
        --output $@
```

This rule tells ROBOT to use the MIREOT method to extract terms from the mirrored UO ontology based on the terms listed in `uo_terms.txt`. For details:

This line is a Makefile rule that defines how to create the file `$(IMPORTDIR)/uo_import.owl` from the file `$(MIRRORDIR)/uo.owl`. The rule has two parts:

1. The dependency declaration: `$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl`
   - This states that the target file `$(IMPORTDIR)/uo_import.owl` depends on the prerequisite file `$(MIRRORDIR)/uo.owl`
   - If the prerequisite file is newer than the target, or if the target doesn't exist, the commands will be executed

2. The command: `$(ROBOT) extract --input $< --method MIREOT --lower-terms $(IMPORTDIR)/uo_terms.txt --output $@`
   - This command uses the ROBOT tool to extract a subset of an ontology
   - It performs a MIREOT extraction
   - `$<` is a special variable that refers to the first prerequisite (`$(MIRRORDIR)/uo.owl`)
   - `$@` is a special variable that refers to the target (`$(IMPORTDIR)/uo_import.owl`)
   - The extraction uses terms listed in the file `$(IMPORTDIR)/uo_terms.txt` as the lower boundary
   - The MIREOT method preserves the hierarchy of the input ontology but doesn't try to preserve the full set of logical entailments

In the end, this rule creates a subset of the Units of Measurement (UO) ontology by extracting only the terms specified in the terms file, using the ROBOT ontology tool with the MIREOT extraction method.

Once the molsim.Makefile is modified, run:

```bash
sh run.sh make update_repo

sh run.sh make refresh-uo
```

This will create a file `/src/ontology/imports/uo_import.owl`, which includes a subset of the desired terms as specified in the `src/ontology/imports/uo_terms.txt` file, along with their superclasses.

### 5. Update molsim-edit.owl

Assuming you have your MOLSIM ontology file already converted to the OFN format and placed as `src/ontology/moslim-edit.owl`, open it and get into the following linfe for MOLSIM ontology declaration:

```
Ontology(<http://purl.obolibrary.org/obo/molsim.owl>
```

Below that line, add the import statement:

```
Import(<http://purl.obolibrary.org/obo/molsim/imports/uo_import.owl>)
```

and save the file.

### 6. Update src/ontology/catalog-v001.xml

Add the following line within the `<group>` tag:

```xml
<uri name="http://purl.obolibrary.org/obo/molsim/imports/uo_import.owl" uri="imports/uo_import.owl"/>
```

This redirects the PURL URI to the local file containing the extracted terms.

### 7. Integration

To integrate the extraction result with the MOLSIM ontology, run:

```bash
sh run.sh make prepare_release
```

This completes the custom import process, allowing you to use the specified UO terms and their superclasses in your MOLSIM ontology.


### Acknnowledgement

Thanks to Damien Goutte-Gattat (at gouttegd) and Nico Matentzoglu (at matentzn) for the help with setting up ODK and the import configuration.


### Additional Reading

- [ODK Documentation](https://github.com/INCATools/ontology-development-kit/blob/master/docs/index.md)
- [ROBOT Documentation on extract](http://robot.obolibrary.org/extract)
