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

## Modify the content of the molsim-odk.yaml Configuration file

To implement MIREOT extraction, use custom mode in the `/src/ontology/molsim-odk.yaml` configuration. This can be achieved by:

```yaml
allow_equivalents: all

import_group:
 products:
   - id: uo
     module_type: custom
```

Save the configuration file.

### 2. Configure Terms to Import

Add the list of terms you want to import to `src/ontology/imports/uo_terms.txt`, for example:

```
UO:0000019 # angstrom
UO:0000063 # nanosecond
UO:0000030 # meter per second
UO:0000150 # millimolar
UO:0000094 # unit of molarity
```

### 3. Update molsim.Makefile

Add the following rule to the `molsim.Makefile` to specify how the import should be generated:

```makefile
$(IMPORTDIR)/uo_import.owl: $(MIRRORDIR)/uo.owl
    $(ROBOT) extract --input $< \
        --method MIREOT \
        --lower-terms $(IMPORTDIR)/uo_terms.txt \
        --output $@
```

This rule tells ROBOT to use the MIREOT method to extract terms from the mirrored UO ontology based on the terms listed in `uo_terms.txt`.

Then run:

```bash
sh run.sh make update_repo

sh run.sh make refresh-uo
```

This will create a file `/src/ontology/imports/uo_import.owl`, which includes a subset of the desired terms as specified in the `[src/ontology/]imports/uo_terms.txt` file, along with their superclasses.

### 4. Update molsim-edit.owl

Assuming you have your MOLSIM ontology file already converted to the OFN format and placed as `[src/ontology/moslim-edit.owl`, open it and get into the following linfe for MOLSIM ontology declaration:

```
Ontology(<http://purl.obolibrary.org/obo/molsim.owl>
```

Below that line, add the import statement:

```
Import(<http://purl.obolibrary.org/obo/molsim/imports/uo_import.owl>)
```

and save the file.

### 5. Update src/ontology/catalog-v001.xml

Add the following line within the `<group>` tag:

```xml
<uri name="http://purl.obolibrary.org/obo/molsim/imports/uo_import.owl" uri="imports/uo_import.owl"/>
```

This redirects the PURL URI to the local file containing the extracted terms.

## Integration

To integrate the extraction result with the MOLSIM ontology, run:

```bash
sh run.sh make prepare_release
```

This completes the custom import process, allowing you to use the specified UO terms and their superclasses in your MOLSIM ontology.

### Additional Reading

- [ODK Documentation](https://github.com/INCATools/ontology-development-kit/blob/master/docs/index.md)
- [ROBOT Documentation on extract](http://robot.obolibrary.org/extract)