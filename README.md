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

## Table of Contents

- [Introduction](#introduction)
- [Development Status](#development-status)
- [Scope](#scope)
- [Competency Questions](#competency-questions)
- [Documentation](#documentation)
- [Access and Usage](#access-and-usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgements](#acknowledgements)

## Introduction

**MOLSIM** is a domain (application) ontology designed to semantically represent platform-agnostic biomolecular simulations (all-atom and coarse-grained) as **FAIR** (Findable, Accessible, Interoperable, and Reusable) datasets. As an application ontology, it reuses terms from established OBO ontologies where they fit and defines its own where they do not.

The primary goal of this ontology is to standardize the representation of molecular simulation data, processes, and methodologies across disparate simulation platforms, engines (e.g., GROMACS, AMBER, NAMD), and analysis tools, while ensuring these terms are interoperable with existing life sciences ontologies.

### At a Glance

|                          |                                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------ |
| **Prefix**               | `MOLSIM`                                                                                                           |
| **Namespace**            | `http://purl.obolibrary.org/obo/MOLSIM_`                                                                           |
| **Size**                 | 2,049 live classes · 113 data properties · 16 object properties · 70 live named individuals (2,268 terms declared, 20 retired) |
| **Hierarchy**            | Domain-oriented (no upper ontology yet; see [Ontology Alignment](#ontology-alignment-reuse-now-abstraction-later)) |
| **Management**           | ODK (Ontology Development Kit) + ROBOT, reasoned with ELK                                                          |
| **Source serialization** | OWL Functional Syntax: [`src/ontology/molsim-edit.owl`](src/ontology/molsim-edit.owl)                              |
| **License**              | CC BY 4.0                                                                                                          |

## Development Status

> ⚠️ **Active Development (Alpha)**
> MOLSIM is currently in an active development phase. The hierarchy, class definitions, and relationships are subject to change. It is not yet recommended for production environments.

We are preparing MOLSIM for submission to the [OBO Foundry](http://obofoundry.org/). Once accepted, the persistent URL (PURL) for the latest release will be:
`http://purl.obolibrary.org/obo/molsim.owl`
*(Note: This URL will not be active until official OBO Foundry acceptance.)*

### Ontology Alignment: reuse now, abstraction later

MOLSIM uses a domain-oriented class hierarchy chosen for browsability by molecular-simulation domain experts. Our alignment work is split by a single test: **does reusing a term add a layer of abstraction above our hierarchy, or not?**

**Already done: reuse that adds no abstraction.** Where an OBO ontology owns a concept we need, we reuse its term directly and place it *inside* our existing hierarchy, under a MOLSIM parent. This removes duplication without making the tree more abstract, so it costs domain experts nothing in readability. Implemented so far:

| Ontology      | What we reuse                                                                                                                                            | How it is attached                                                                                                      |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| **STATO**     | statistics — `p-value`, `standard deviation`, `correlation coefficient`, Pearson's, Spearman's, coefficient of determination, standard error of the mean | 7 classes under our `statistical property` branch; 8 former MOLSIM duplicates retired and redirected with `IAO:0100001` |
| **SO**        | sequence features — `polypeptide_domain`, nucleic-acid base modifications                                                                                | our `protein domain` sits under `SO:0000417`; SO umbrellas bridged under MOLSIM parents                                 |
| **UO**        | units of measurement                                                                                                                                     | used as the unit filler in our quantity pattern; we never invent units                                                  |
| **GO**        | `nucleosome`                                                                                                                                             | bridged under a MOLSIM parent                                                                                           |
| **RO**        | relations (`participates in`, `has part` family)                                                                                                         | reused instead of minting our own equivalents                                                                           |
| **IAO / OMO** | annotation properties and standard OBO metadata                                                                                                          | infrastructure (definitions, term editors, license), not domain content                                                 |

To keep this safe we extract these terms with **bounded MIREOT** where the source ontology's parents would drag in an upper ontology; that is, we take the term itself and none of its ancestors. As a result **no MOLSIM class is currently placed under a BFO or COB class.**

**Deferred: alignment that would add abstraction.** Aligning MOLSIM to an upper ontology, principally the **Basic Formal Ontology (BFO)**, is planned but **deliberately postponed**. Upper-ontology alignment inserts abstract parents (for example *continuant*, *occurrent*, *information content entity*) above our domain branches. During the ongoing domain-expert verification phase we prioritise a hierarchy that experts can read and validate directly, so we avoid that extra abstraction for now. 

**Where correspondence is enough, we map instead of importing.** When another ontology describes the same thing but models it differently (for instance PSI-MI treats scientific databases as classes while MOLSIM treats each specific database as an individual) we record the correspondence as an [SSSOM](https://mapping-commons.github.io/sssom/) mapping in `src/ontology/mappings/` and import nothing. This keeps interoperability without importing a structure that conflicts with ours.

## Scope

MOLSIM provides a semantic framework spanning the full molecular-simulation lifecycle (system setup, execution, and analysis):

* **Computational processes:** molecular dynamics, energy minimization, equilibration and production stages, enhanced-sampling and free-energy workflows, constant-pH MD, and QM/MM.
* **Algorithms & methods:** numerical integrators, thermostats and barostats, constraint algorithms (SHAKE/LINCS/SETTLE), long-range electrostatics (PME/Ewald) and cutoff schemes, energy-minimization algorithms, and enhanced-sampling methods (metadynamics, replica exchange, umbrella sampling).
* **Force fields & parameterization:** additive and polarizable force fields, water/solvent models, ligand charge models (e.g., RESP), and options such as hydrogen-mass repartitioning.
* **System specifications:** molecular systems (protein, nucleic acid, lipid/membrane, ligand, carbohydrate, ion, and solvent), simulation-box types and periodic boundary conditions, thermodynamic ensembles (NVE/NVT/NPT), restraints and constraints, ionic strength, and pH.
* **Software & hardware:** simulation engines (e.g., GROMACS, AMBER, NAMD, LAMMPS, OpenMM), setup and analysis tools, and computing infrastructure (CPUs/GPUs, HPC).
* **Data structures & formats:** topology, coordinate, and trajectory file formats; coordinate representations; structural identifiers; and physical units.
* **Analysis & outputs:** trajectories and conformational ensembles; thermodynamic, structural, and kinetic properties (e.g., RMSD, RMSF, radius of gyration, potential of mean force, Markov state models); correlation functions; and unit-bearing quantities.
* **Provenance & metadata:** simulation parameters and schedules, system-composition counts, system-classification labels, and per-term editorial provenance, supporting FAIR, machine-actionable simulation metadata.

### Where the boundary is

The list above says what MOLSIM covers. This says how we decide whether a *new* term belongs, so that the scope stays stable as the ontology grows.

**The membership test.** For any candidate term, ask:

> **Would a complete record of a simulation dataset need to state it?**

That spans four things: what was **configured** (timestep, thermostat, force field), what was **computed** (RMSD, potential of mean force, free energies), where the inputs **came from** (a PDB entry, a UniProt accession, a publication), and what it **ran on** (engine, version, hardware). If a full dataset record would not mention it, MOLSIM does not need it, however closely related it may seem.

We deliberately draw the boundary by **use case** rather than by subject matter. "Anything about molecular simulation" has no natural edge: in computational chemistry everything connects to everything, so two people applying that rule reach different answers and the scope drifts. "What a dataset record must state" is a question anyone can answer by opening a real file, which is also how MOLSIM was built — its terms were extracted from AMBER, cpptraj and GROMACS keyword frequencies and from metadata specifications, not from a textbook index.

**Depth limit for neighbouring fields.** MOLSIM necessarily touches quantum chemistry, computational materials science and structural biology. Where it does, terms go **at most two levels** below the point where they attach. So we record *which* QM engine was used, whether QM/MM was active, and which basis set parameterised a force field — because a dataset record states those. We do not model the internal machinery of quantum-chemical methods, because it does not appear in that record and belongs to whoever owns that domain.

**This rule governs new terms.** It applies to terms added from 2026-07-29 onward. Existing terms are retained; where one sits outside the rule it is kept for stability and simply not extended. Terms are never deleted in any case — a published IRI is a permanent commitment, so anything withdrawn is deprecated with `owl:deprecated` and, where a successor exists, an `IAO:0100001` ("term replaced by") pointer.

**Relationship to EMMO-based materials-modelling ontologies.** A separate ecosystem — [EMMO](https://emmo-repo.github.io/), OSMO and VISO, developed around the European Materials Modelling Council — also describes simulation, using a different top-level framework. MOLSIM is the OBO-aligned ontology for **biomolecular** simulation metadata and is intended to **complement** rather than compete with that work; the two focus on different communities and different kinds of system. Where concepts correspond we will publish [SSSOM](https://mapping-commons.github.io/sssom/) mappings rather than adopt a shared upper ontology, since the two frameworks are not directly interoperable.


## Competency Questions

MOLSIM is designed to represent simulations in enough detail to answer questions such as:

* Which **MD engine and version** produced this trajectory, and on what **hardware**?
* What **integration timestep**, **thermostat**, and **barostat** were used, and in which **ensemble** (NVT/NPT)?
* Which **force field(s)** and **water/solvent model** parameterize the system, and was **hydrogen-mass repartitioning** applied?
* What **molecular system** was simulated (protein, nucleic acid, lipid membrane, ligand, ions), and what is its **composition** (atom/residue counts)?
* Which **enhanced-sampling** or **free-energy** method was applied, and with what **collective variables / restraints**?
* What **analyses** were run (e.g., RMSD, RMSF, PMF, Markov state models), and in what **units** are the results expressed?

> **Modeling example.** The class `non-bonded cutoff distance` is modeled as a length quantity carrying two universal restrictions (a UO length-unit restriction and a decimal value restriction) so that a cutoff such as "1.2 nm" is captured in a unit-aware, machine-readable way rather than as free text.

## Documentation

* **Class & Property Hierarchy:** Explore the ontology structure on [BioPortal](https://bioportal.bioontology.org/ontologies/MOLSIM).
* **Technical Documentation:** Access the [development guides and technical details](https://cpclab.github.io/molsim-ontology/).
* **Terms Overview:** Review the generated [ontology terms reference](https://cpclab.github.io/molsim-ontology/pylode.html).

> **Note on the Terms Overview:** To simplify the generated reference, `ChEBI` classes have been omitted, and `iao:definition` is temporarily rendered as `dcterms:description`. The source ontology itself consistently uses `iao:definition` for all concept definitions.

## Access and Usage

### For Editors and Developers

Development is conducted in the `src` directory. Editors should work with the source edit file:

* [`src/ontology/molsim-edit.owl`](src/ontology/molsim-edit.owl)

### For Users (Pre-Release)

Until the official OBO PURL is active, you can access the latest compiled version of the ontology directly from this repository:

* [`molsim.owl` (Latest Snapshot)](molsim.owl)
* The .obo release does not include MOLSIM's 113 data properties or its 70 named individuals: the OBO format cannot represent data properties, and named individuals are dropped in conversion, so the .obo file is a class-only view. Use the OWL or JSON release if you need the full ontology.

## Contributing

The MOLSIM project is open to contributions and collaboration.

* **Term Requests:** If you need a specific term added to MOLSIM, please open a [new issue](https://github.com/CPCLab/molsim-ontology/issues) with the label `term request`.
* **Bug Reports:** If you find an error in a definition or hierarchy, please report it via the [Issue Tracker](https://github.com/CPCLab/molsim-ontology/issues).
* **Discussion:** For broader discussions regarding modeling decisions, please use the issue tracker or contact the maintainers.

## License

MOLSIM is available under the [Creative Commons Attribution 4.0 International license (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).
