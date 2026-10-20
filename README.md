<p align="center">
  <img src="./assets/molsim-logo.svg" alt="MOLSIM Ontology Logo" width="175">
</p>

<h1 align="center">Molecular Simulation Ontology (MOLSIM)</h1>

<p align="center">
  <a href="https://github.com/CPCLab/molsim-ontology/actions/workflows/qc.yml">
    <img src="https://github.com/CPCLab/molsim-ontology/actions/workflows/qc.yml/badge.svg" alt="QC Status">
  </a>
  <a href="https://github.com/CPCLab/molsim-ontology/actions/workflows/docs.yml">
    <img src="https://github.com/CPCLab/molsim-ontology/actions/workflows/docs.yml/badge.svg" alt="Docs Build Status">
  </a>
  <a href="https://github.com/INCATools/ontology-development-kit">
    <img src="https://img.shields.io/badge/Powered_by-ODK-blue.svg" alt="Powered by ODK">
  </a>
  <a href="http://robot.obolibrary.org/">
    <img src="https://img.shields.io/badge/Powered_by-ROBOT-blue.svg" alt="Powered by ROBOT">
  </a>
  <a href="https://creativecommons.org/licenses/by/4.0/">
    <img src="https://img.shields.io/badge/License-CC_BY_4.0-blue.svg" alt="License: CC BY 4.0">
  </a>
</p>

**MOLSIM** is an ontology for biomolecular simulation, both all-atom and coarse-grained. It gives shared names and definitions to the parts of a molecular dynamics study: its methods, parameters, software, file formats and the data it produces. With these names, people and machines can find, read and reuse a simulation, whichever engine produced it, for example GROMACS, AMBER or NAMD. This makes simulation data **FAIR**: Findable, Accessible, Interoperable and Reusable.

MOLSIM reuses terms from other [OBO Foundry](https://obofoundry.org/) ontologies where they fit, and defines its own terms where they do not.

> ⚠️ **Alpha.** MOLSIM is under active development. Terms, definitions and the hierarchy can still change, so it is not yet recommended for production use.

## Contents

- [At a glance](#at-a-glance)
- [Status](#status)
- [Scope](#scope)
- [Competency questions](#competency-questions)
- [Reuse of other ontologies](#reuse-of-other-ontologies)
- [Documentation and files](#documentation-and-files)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## At a glance

|                           |                                                                                                                 |
| ------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **Prefix**                | `MOLSIM`                                                                                                        |
| **Namespace**             | `http://purl.obolibrary.org/obo/MOLSIM_`                                                                        |
| **Live terms**            | 2,265: 2,056 classes, 119 data properties, 19 object properties, 70 named individuals and 1 annotation property |
| **Retired terms**         | 37, kept so that their web addresses keep working                                                               |
| **Checked by a reviewer** | 609 of the 2,265 live terms. The definitions of the other 1,656 end with `(UNVERIFIED)`                         |
| **Hierarchy**             | 13 top-level branches, organised by topic, and aligned with COB at the top                                      |
| **Built with**            | ODK (Ontology Development Kit) and ROBOT, checked with the ELK reasoner                                         |
| **Source file**           | [`src/ontology/molsim-edit.owl`](src/ontology/molsim-edit.owl), in OWL Functional Syntax                        |
| **License**               | CC BY 4.0                                                                                                       |

The figures were measured on 2026-10-19.

## Status

**Expert review is the main work now.** The definitions that have not been checked yet were drafted with AI assistance. A definition ending with `(UNVERIFIED)` has not been checked by a domain expert, so please read it as a draft. A checked term names its reviewer by ORCID in `IAO:0000117 term editor`.

**OBO Foundry.** We are preparing MOLSIM for submission to the OBO Foundry. After acceptance, the latest release will be available at `http://purl.obolibrary.org/obo/molsim.owl`. That address does not work yet.

## Scope

MOLSIM covers the whole life of a simulation, from setting it up to running it and analysing the results:

- **Computational processes:** molecular dynamics, energy minimization, equilibration and production stages, enhanced-sampling and free-energy workflows, constant-pH molecular dynamics, and QM/MM.
- **Algorithms and methods:** integrators, thermostats and barostats, constraint algorithms such as SHAKE and LINCS, long-range electrostatics such as PME, and enhanced-sampling methods such as metadynamics.
- **Force fields and parameters:** additive and polarizable force fields, water and solvent models, ligand charge models such as RESP, and hydrogen mass repartitioning.
- **System specifications:** the molecules simulated (protein, nucleic acid, membrane, ligand, ions), box types, periodic boundary conditions, ensembles (NVT, NPT), restraints, and pH.
- **Software and hardware:** simulation engines such as GROMACS, AMBER, NAMD and OpenMM, setup and analysis tools, and computing hardware such as GPUs and HPC clusters.
- **Data and formats:** topology, coordinate and trajectory file formats, structural identifiers, and units.
- **Analysis and results:** trajectories, and the results computed from them, such as RMSD, radius of gyration, potential of mean force and Markov state models.
- **Metadata:** simulation parameters and schedules, counts of what a system contains, and where input data came from.

### How we decide what belongs

The list above says what MOLSIM covers. The rules below decide whether a *new* term belongs, so that the scope stays stable as MOLSIM grows.

**The test.** For any candidate term, we ask:

> **Would a complete record of a simulation dataset need to state it?**

Such a record states 4 kinds of information:

- what was **configured**, such as the timestep, thermostat or force field
- what was **computed**, such as RMSD, potential of mean force or free energies
- where the inputs **came from**, such as a PDB entry, a UniProt accession or a publication
- what the simulation **ran on**: engine, version and hardware

If a complete dataset record would not mention a term, MOLSIM does not need it.

We draw the line by **use** rather than by subject. "Anything about molecular simulation" has no clear edge, because in computational chemistry every topic connects to every other. "What a dataset record must state" can be checked by opening a real file. This is also how MOLSIM was built: its terms come from the keywords used in AMBER, cpptraj and GROMACS, and from metadata specifications.

**A depth limit for neighbouring fields.** MOLSIM touches other fields, such as quantum chemistry, materials science and structural biology. Where it does, it names the tools and choices from that field that a simulation record mentions, and stops there. In practice, terms go **at most 2 levels** below the point where the other field first enters MOLSIM.

Quantum chemistry is the clearest example. Most biomolecular simulations treat atoms as balls joined by springs, which is fast. Sometimes one small region, such as the spot where a chemical reaction happens, is calculated with quantum chemistry instead, which describes the electrons. Mixing the 2 in one simulation is called QM/MM.

| Where quantum chemistry enters MOLSIM | 1 level below         | What MOLSIM does *not* describe                                                     |
| ------------------------------------- | --------------------- | ----------------------------------------------------------------------------------- |
| `quantum chemistry engine`            | `Gaussian`, `Q-Chem`  | how each program calculates the electrons                                           |
| `basis set`                           | `auxiliary basis set` | which mathematical functions a basis set is made of, and how many are used per atom |

A basis set is the set of mathematical functions a quantum chemistry program uses to describe where the electrons can be. A simulation record says, for example, "the QM region was computed with Gaussian, using basis set 6-31G\*", and MOLSIM can record that. A record never states the equations Gaussian solves, or how 6-31G\* is built. MOLSIM leaves those details to the ontologies of quantum chemistry, and links to them with mappings where useful.

**These rules apply to terms added from 2026-07-29 onward.** Older terms stay, and are not extended where they fall outside the rules. No term is ever deleted: a term that is withdrawn is marked with `owl:deprecated`, and where a replacement exists it points to it with `IAO:0100001 term replaced by`.

**Materials-modelling ontologies.** [EMMO](https://emmo-repo.github.io/), OSMO and VISO, developed around the European Materials Modelling Council, also describe simulation, using a different top-level framework. MOLSIM focuses on **biomolecular** simulation and is meant to complement that work. Where concepts correspond, we plan to publish [SSSOM](https://mapping-commons.github.io/sssom/) mappings rather than share an upper ontology, because the 2 frameworks cannot be combined directly.

## Competency questions

Competency questions are the questions an ontology is built to answer. MOLSIM is designed to describe simulations in enough detail to answer questions such as:

- Which **simulation engine and version** produced this trajectory, and on what **hardware**?
- What **integration timestep**, **thermostat** and **barostat** were used, and in which **ensemble** (NVT, NPT)?
- Which **force fields** and **water model** describe the system, and was **hydrogen mass repartitioning** used?
- What **molecular system** was simulated (protein, nucleic acid, lipid membrane, ligand, ions), and what does it contain (atom and residue counts)?
- Which **enhanced-sampling** or **free-energy** method was used, and with which **collective variables** and **restraints**?
- Which **analyses** were run (for example RMSD, RMSF, potential of mean force, Markov state models), and in which **units** are the results?

## Reuse of other ontologies

MOLSIM's hierarchy is organised by topic, so that simulation experts can browse it. When another OBO ontology already has a term we need, we reuse that term and place it inside our hierarchy. We do this only when it adds no extra layers of more general classes above our own terms.

| Ontology  | What MOLSIM reuses                                                                                                                                                | How it is used                                                                                                                   |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **STATO** | 7 statistics classes, such as `p-value`, `standard deviation` and `correlation coefficient`                                                                       | placed under our `statistical property` branch. 8 MOLSIM duplicates were retired and point to the STATO terms                    |
| **SO**    | 29 classes: protein domains, protein secondary structure (helix types and coil) and modified nucleic-acid bases                                                   | our `protein domain` and `secondary structure` classes sit under SO classes. 4 MOLSIM helix classes were retired in favour of SO |
| **UO**    | 55 unit classes                                                                                                                                                   | the units for 101 MOLSIM quantity classes, across 14 kinds of unit. MOLSIM never defines its own units                           |
| **IAO**   | 6 classes, such as `information content entity`, `plan specification`, `document` and `publication`, and the annotation properties `definition` and `term editor` | 15 MOLSIM classes sit under 4 of these IAO classes                                                                               |
| **OMO**   | the standard OBO metadata properties                                                                                                                              | definitions, synonyms and other term metadata                                                                                    |
| **RO**    | 7 relations, such as `has part`, `participates in`, `has input` and `has output`                                                                                  | reused instead of defining our own                                                                                               |
| **OBI**   | 4 relations: `has specified input`, `has specified output` and their 2 inverses                                                                                   | declared as narrower versions of RO's `has input` and `has output`                                                               |
| **GO**    | 1 class, `nucleosome`                                                                                                                                             | placed under a MOLSIM parent                                                                                                     |

**Units.** `MOLSIM:001187 non-bonded cutoff distance` (class) says that its unit is a length unit from UO, and that its value is a decimal number. A cutoff such as "1.2 nm" can then be recorded as a value with a unit, not as free text. Quantities such as times and energies follow the same pattern. These statements describe the class. They do not check data. OWL assumes that missing information may exist elsewhere, so it does not report a record that has no unit, or that has the wrong one. Checking records needs a separate validation language such as [SHACL](https://www.w3.org/TR/shacl/). MOLSIM does not provide SHACL rules yet.

**Only the chosen terms are copied in.** Where a source ontology would also bring in its upper-level parents, we copy the term without its parents. Each MOLSIM class that sits under a term from another ontology was placed there on purpose. The release contains no BFO class. It does contain 2 relations with BFO identifiers, `has part` and `precedes`, because RO publishes them under those identifiers.

**COB at the top.** Since 2026-08-12, MOLSIM aligns with [COB](https://obofoundry.org/COB/), the Core Ontology for Biology and Biomedicine. OBO Foundry [Principle 5](https://obofoundry.org/principles/fp-005-delineated-content.html) says that mid- and upper-level terms "should be considered for" COB. The link is small on purpose. MOLSIM retired its own `information content entity` in favour of `IAO:0000030 information content entity`, which is a top-level COB class. It also retired its own `plan specification` in favour of `IAO:0000104 plan specification`. COB uses BFO's own identifiers where the 2 overlap, so a full BFO alignment could be added later without retiring or moving any MOLSIM term. COB has no class for software, so MOLSIM's software branch stays a top-level branch of its own.

**Mappings instead of imports.** When another ontology describes the same thing but models it differently, we record the link as an [SSSOM](https://mapping-commons.github.io/sssom/) mapping in [`src/ontology/mappings/`](src/ontology/mappings/) and import nothing. For example, PSI-MI treats scientific databases as classes, while MOLSIM treats each database as a named individual. The release also publishes these mappings as SKOS annotations on the MOLSIM terms, so a tool can follow them without reading a separate file. The mappings reach 14 other vocabularies, among them EDAM for file formats.

## Documentation and files

- **Browse the hierarchy** on [BioPortal](https://bioportal.bioontology.org/ontologies/MOLSIM).
- **Development guides** are on the [documentation site](https://cpclab.github.io/molsim-ontology/). To edit MOLSIM, start with [Editing MOLSIM](https://cpclab.github.io/molsim-ontology/custom/EditingMOLSIM/), which explains how to set up Protégé.
- **Terms reference**, generated with pyLODE: [all terms on one page](https://cpclab.github.io/molsim-ontology/pylode.html). There, each definition is shown as `skos:definition`, copied from `IAO:0000115 definition`. The ontology itself uses `IAO:0000115 definition`.

**Release files.** Until the OBO address above works, the latest build is in this repository. The files are [`molsim.owl`](molsim.owl), [`molsim.obo`](molsim.obo) and [`molsim.json`](molsim.json). Each also comes as a `-base` and a `-full` variant. The `.obo` files hold only classes and object properties, because the OBO format cannot represent data properties or named individuals. Use the OWL or JSON files if you need those.

**Editing.** All changes are made in [`src/ontology/molsim-edit.owl`](src/ontology/molsim-edit.owl). The other files are generated from it with ODK.

## Contributing

MOLSIM is open to contributions.

- **Contact:** the maintainers read the [issue tracker](https://github.com/CPCLab/molsim-ontology/issues) and [Discussions](https://github.com/CPCLab/molsim-ontology/discussions), so please use those for any question.
- **Suggest a term or report a problem:** open a [new issue](https://github.com/CPCLab/molsim-ontology/issues/new/choose) and pick the matching form, such as "Add new term" or "Revise text definition".
- **Discuss a modelling decision** in Discussions.
- **Domain experts** help most by checking definitions. To join the review, say so in Discussions or in an issue.

## License

MOLSIM is available under the [Creative Commons Attribution 4.0 International license (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

## Acknowledgements

This ontology repository was created with the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).
