![Build Status](https://github.com/CPCLab/molsim-ontology/actions/workflows/qc.yml/badge.svg)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

# Molecular Simulation Ontology (MOLSIM)

## Introduction

**MOLSIM** is an interoperable domain ontology designed to semantically represent platform-agnostic atomistic biomolecular simulations as **FAIR** (Findable, Accessible, Interoperable, and Reusable) datasets. 

The primary goal of this ontology is to standardize the representation of molecular simulation data, processes, and methodologies across disparate simulation platforms, engines (e.g., GROMACS, AMBER, NAMD), and analysis tools.

## Development Status

⚠️ **Active Development**

MOLSIM is currently in an **active development phase (Alpha)**. The hierarchy, class definitions, and relationships are subject to change. It is not yet recommended for production environments.

We are preparing MOLSIM for submission to the [OBO Foundry](http://obofoundry.org/). Once accepted, the persistent URL (PURL) for the latest release will be:
> http://purl.obolibrary.org/obo/molsim.owl

*(Note: This URL will not be active until OBO Foundry acceptance.)*

## Scope

MOLSIM provides a semantic framework for the following aspects of molecular simulation:

*   **Computational Processes:** Molecular dynamics and energy minimization protocols.
*   **Algorithms & Methods:** Integration algorithms, thermostats, barostats, and enhanced sampling methods.
*   **Software & Hardware:** Simulation engines, analysis tools, and computing infrastructure (GPUs/CPUs).
*   **Data Structures:** File formats, coordinate representations, and topologies.
*   **System Specifications:** Molecular systems, force fields, and boundary conditions.
*   **Analysis & Outputs:** Trajectories, thermodynamic properties, and structural descriptors.

## Access and Usage

### For Editors and Developers
Development is conducted in the `src` directory. Editors should work with the source edit file:
*   [src/ontology/molsim-edit.owl](src/ontology/molsim-edit.owl)

### For Users (Pre-Release)
Until the official OBO PURL is active, you can access the latest compiled version of the ontology directly from this repository:
*   [molsim.owl (Latest Snapshot)](molsim.owl)

## Contributing

The MOLSIM project is open to contributions and collaboration.

*   **Term Requests:** If you need a specific term added to MOLSIM, please open a [New Issue](https://github.com/CPCLab/molsim-ontology/issues) with the label `term request`.
*   **Bug Reports:** If you find an error in a definition or hierarchy, please report it via the [Issue Tracker](https://github.com/CPCLab/molsim-ontology/issues).
*   **Discussion:** For broader discussions regarding modeling decisions, please use the issue tracker or contact the maintainers.

## License

MOLSIM is available under the [Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International](https://creativecommons.org/licenses/by-nc-sa/4.0/) license (CC BY-NC-SA 4.0).

## Acknowledgements

This ontology repository was created using the [Ontology Development Kit (ODK)](https://github.com/INCATools/ontology-development-kit).