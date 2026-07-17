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
  <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">
    <img src="https://img.shields.io/badge/License-CC_BY--NC--SA_4.0-blue.svg" alt="License: CC BY-NC-SA 4.0">
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
**MOLSIM** is an interoperable domain ontology designed to semantically represent platform-agnostic atomistic biomolecular simulations as **FAIR** (Findable, Accessible, Interoperable, and Reusable) datasets. 

The primary goal of this ontology is to standardize the representation of molecular simulation data, processes, and methodologies across disparate simulation platforms, engines (e.g., GROMACS, AMBER, NAMD), and analysis tools, while ensuring these terms are interoperable with existing life sciences ontologies.

### At a Glance
| | |
|---|---|
| **Prefix** | `MOLSIM` |
| **Namespace** | `http://purl.obolibrary.org/obo/MOLSIM_` |
| **Size** | ~2,040 classes · 16 object properties · 94 data properties |
| **Hierarchy** | Domain-oriented (no upper ontology yet — see [Ontology Alignment](#ontology-alignment-planned-currently-deferred)) |
| **Management** | ODK (Ontology Development Kit) + ROBOT, reasoned with ELK |
| **Source serialization** | OWL Functional Syntax — [`src/ontology/molsim-edit.owl`](src/ontology/molsim-edit.owl) |
| **License** | CC BY-NC-SA 4.0 |

## Development Status
> ⚠️ **Active Development (Alpha)**
> MOLSIM is currently in an active development phase. The hierarchy, class definitions, and relationships are subject to change. It is not yet recommended for production environments.

We are preparing MOLSIM for submission to the [OBO Foundry](http://obofoundry.org/). Once accepted, the persistent URL (PURL) for the latest release will be:
`http://purl.obolibrary.org/obo/molsim.owl`
*(Note: This URL will not be active until official OBO Foundry acceptance.)*

### Ontology Alignment (Planned, Currently Deferred)
MOLSIM currently uses a domain-oriented class hierarchy chosen for browsability by molecular-simulation domain experts, without alignment to an upper ontology. Alignment with OBO Foundry ontologies, including the Basic Formal Ontology (BFO), is planned but **deliberately deferred** for now. During the ongoing domain-expert verification phase, we prioritize a hierarchy that domain experts can readily read and validate, and we avoid the additional abstraction that upper-ontology alignment (e.g., BFO) would introduce at this stage. Once the ontology has matured through domain-expert review, MOLSIM will be aligned with the OBO Foundry, BFO, and related ontologies accordingly.

## Scope
MOLSIM provides a semantic framework spanning the full molecular-simulation lifecycle (system setup, execution, and analysis):

* **Computational processes:** molecular dynamics, energy minimization, equilibration and production stages, enhanced-sampling and free-energy workflows, constant-pH MD, and QM/MM.
* **Algorithms & methods:** numerical integrators, thermostats and barostats, constraint algorithms (SHAKE/LINCS/SETTLE), long-range electrostatics (PME/Ewald) and cutoff schemes, energy-minimization algorithms, and enhanced-sampling methods (metadynamics, replica exchange, umbrella sampling).
* **Force fields & parameterization:** additive and polarizable force fields, water/solvent models, ligand charge models (e.g., RESP), and options such as hydrogen-mass repartitioning.
* **System specifications:** molecular systems (protein, nucleic acid, lipid/membrane, ligand, carbohydrate, ion, and solvent), simulation-box types and periodic boundary conditions, thermodynamic ensembles (NVE/NVT/NPT), restraints and constraints, ionic strength, and pH.
* **Software & hardware:** simulation engines (e.g., GROMACS, AMBER, NAMD, LAMMPS, OpenMM), setup and analysis tools, and computing infrastructure (CPUs/GPUs, HPC).
* **Data structures & formats:** topology, coordinate, and trajectory file formats; coordinate representations; structural identifiers; and physical units.
* **Analysis & outputs:** trajectories and conformational ensembles; thermodynamic, structural, and kinetic properties (e.g., RMSD, RMSF, radius of gyration, potential of mean force, Markov state models); correlation functions; and unit-bearing quantities.
* **Provenance & metadata:** simulation parameters and schedules, system-composition counts, system-classification labels, and per-term editorial provenance — supporting FAIR, machine-actionable simulation metadata.

## Competency Questions
MOLSIM is designed to represent simulations in enough detail to answer questions such as:

* Which **MD engine and version** produced this trajectory, and on what **hardware**?
* What **integration timestep**, **thermostat**, and **barostat** were used, and in which **ensemble** (NVT/NPT)?
* Which **force field(s)** and **water/solvent model** parameterize the system, and was **hydrogen-mass repartitioning** applied?
* What **molecular system** was simulated (protein, nucleic acid, lipid membrane, ligand, ions), and what is its **composition** (atom/residue counts)?
* Which **enhanced-sampling** or **free-energy** method was applied, and with what **collective variables / restraints**?
* What **analyses** were run (e.g., RMSD, RMSF, PMF, Markov state models), and in what **units** are the results expressed?

> **Modeling example.** The class `non-bonded cutoff distance` is modeled as a length quantity carrying two universal restrictions — a UO length-unit restriction and a decimal value restriction — so that a cutoff such as "1.2 nm" is captured in a unit-aware, machine-readable way rather than as free text.

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

## Contributing
The MOLSIM project is open to contributions and collaboration.
* **Term Requests:** If you need a specific term added to MOLSIM, please open a [new issue](https://github.com/CPCLab/molsim-ontology/issues) with the label `term request`.
* **Bug Reports:** If you find an error in a definition or hierarchy, please report it via the [Issue Tracker](https://github.com/CPCLab/molsim-ontology/issues).
* **Discussion:** For broader discussions regarding modeling decisions, please use the issue tracker or contact the maintainers.

## License
MOLSIM is available under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International license (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/).

## Acknowledgements
This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).