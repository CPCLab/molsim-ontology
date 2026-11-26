# Writing data with MOLSIM terms

This page shows how to describe simulation data with MOLSIM terms, written as RDF in Turtle. It covers three patterns: 1) a quantity with a unit, 2) a statistic over a run, and 3) a fact recorded with a data property. A check that tests data against these patterns, written in SHACL, is being prepared and is not published yet.

## 1. A quantity with a unit

**In short:** a number with a unit is written as a node of its own. The node says which MOLSIM class it belongs to, holds one number and one unit from the Unit Ontology (UO), and says what it describes.

This applies to every MOLSIM class that carries a unit rule and a value rule: 100 classes, measured 2026-11-16.

### Example

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix ex:  <http://example.org/my_simulation/> .

ex:SimRun_A rdf:type obo:MOLSIM_000003 .          # simulation execution

ex:Cutoff_Setting_1 rdf:type obo:MOLSIM_001187 ;  # non-bonded cutoff distance
    obo:IAO_0000136 ex:SimRun_A ;                 # is about
    obo:IAO_0000004 "10.0"^^xsd:decimal ;         # has measurement value
    obo:IAO_0000039 obo:UO_0000019 .              # has measurement unit label: angstrom
```

### Rules

1. **The quantity is a node of its own**, with the MOLSIM class as its type, for example `MOLSIM:001187 non-bonded cutoff distance` (class). The node may have its own web address, as above, or be an unnamed node (a blank node, written `[]` in Turtle). Prefer a URI instead of blank node as other data cannot link to an unnamed node, and many tools handle unnamed nodes badly.

2. **Exactly one value**, through `IAO:0000004 has measurement value` (data property). The value is an `xsd:decimal` or an `xsd:integer`. Text such as `"ten"` is not a value. An `xsd:double` is not accepted either, because the OWL rule on the class does not accept it.

3. **Exactly one unit**, through `IAO:0000039 has measurement unit label` (object property). The unit is the web address of a single UO unit, for example `obo:UO_0000019` for angstrom.

   **The unit must fit the quantity.** Each quantity class accepts one kind of unit. A cutoff distance is a length, so angstrom and nanometre are accepted, but picosecond is not. In UO, the length units sit beneath `UO:0000001 length unit` (class).

   In MOLSIM's data annotation in a semantic format, these values are not accepted as a unit:

   - **A text**, such as `"Å"` or `"angstrom"`. Use the web address of the UO unit instead.
   - **A unit from another unit vocabulary.** MOLSIM's units come from UO only.
   - **The kind of unit itself**, such as `UO:0000001 length unit` (class). It names a group of units, so you cannot measure in it.

4. **At least one link to the thing described**, through `IAO:0000136 is about` (object property). The 'thing' can be a simulation run, but it may be a system or a trajectory. A quantity with no link is a number that describes nothing.

### What this pattern does not cover yet

- **Energy per mole**, such as kJ/mol and kcal/mol. UO accepted these units in November 2026, but they are not in a UO release yet. Until they are, the classes that need them have no unit rule.
- **Volumes on the scale of a simulation box.** UO accepted the cubic nanometre in November 2026, but it is not in a UO release yet. UO has no cubic ångström, so a volume given in Å³ has to be converted to nm³.
- **Lists of numbers**, such as the three lengths of a box. MOLSIM records these as data properties holding a text.

## 2. A statistic over a run

**In short:** a statistic, such as the mean temperature of a run, is a quantity with two types. The STATO type says how the number was computed. The MOLSIM type says what was measured. Everything in section 1 still applies.

MOLSIM does not have classes such as "mean temperature". Any statistic can be combined with any quantity this way, so MOLSIM needs no class for each pair.

### Example

The mean temperature in the output log of run A is 300.1 K:

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix ex:  <http://example.org/my_simulation/> .

ex:SimRun_A rdf:type obo:MOLSIM_000003 .           # simulation execution

ex:Mean_Temperature_A rdf:type obo:STATO_0000401 , # sample mean
                               obo:MOLSIM_001537 ; # temperature
    obo:IAO_0000136 ex:SimRun_A ;                  # is about
    obo:IAO_0000004 "300.1"^^xsd:decimal ;         # has measurement value
    obo:IAO_0000039 obo:UO_0000012 .               # has measurement unit label: kelvin
```

### The rules

1. **Two types.** One STATO class for the statistic and one MOLSIM class for the quantity.
2. **The rules of section 1 apply.** The value and the unit belong to the quantity: a mean temperature is a temperature, so its unit is a temperature unit.
3. **"Is about" points at what the statistic summarises**: a simulation run, a stage of a run, or a trajectory.

### The statistics MOLSIM uses

All five are imported from STATO, the statistics ontology:

- `STATO:0000401 sample mean` (class)
- `STATO:0000150 minimum observed value` (class)
- `STATO:0000151 maximum observed value` (class)
- `STATO:0000237 standard deviation` (class)
- `STATO:0000037 standard error of the mean` (class)

## 3. A fact recorded with a data property

**In short:** a fact without a unit that is read off a system, a file or the program output is written as one triple. The thing described points straight at the value through a MOLSIM data property. Counts, yes/no facts, names, file paths and dates are written this way.

### Example

System A has 23,558 atoms, and its total charge is zero:

```turtle
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix obo: <http://purl.obolibrary.org/obo/> .
@prefix ex:  <http://example.org/my_simulation/> .

ex:System_A rdf:type obo:MOLSIM_001887 ;           # molecular simulation system
    obo:MOLSIM_001122 "23558"^^xsd:integer ;       # number of total atoms
    obo:MOLSIM_002193 "true"^^xsd:boolean .        # is charge neutral
```

### The rules

1. **Only for a fact without a unit.** A number with a unit follows section 1. A setting typed into a program, such as `MOLSIM:002294 number of integration steps` (class), is a class and is written as in section 1 too, without a unit if it has none.
2. **The value has the type the data property names**: `xsd:integer` for a count, `xsd:boolean` for yes/no, `xsd:string` for text and `xsd:dateTime` for a date.
3. **A list of values with a unit is a text that carries its unit**, for example "91.8 x 71.0 x 75.8 angstrom" for the three edge lengths of a box.
4. **When a class says the same as a yes/no fact, use the class.** For example, a run that used hydrogen mass repartitioning points at `MOLSIM:001337 hydrogen mass repartitioning analysis` (class) through `MOLSIM:002311 uses method` (object property). MOLSIM has no yes/no term for it.

### Why MOLSIM differs from most OBO ontologies here

Most OBO ontologies define very few data properties of their own. Counted on 2026-11-26: IAO defines four, OBI four, STATO one and RO one, while GO, ChEBI and PSI-MS define none. These ontologies make each kind of value a class, and attach the number with one general data property, as section 1 does. PSI-MS, the OBO vocabulary for mass spectrometry runs, makes even counts classes, such as `MS:1003059 number of peaks` (class).

MOLSIM keeps data properties for facts read off a record, for three reasons:

- **MOLSIM turns flat metadata records into a graph.** A record such as the JSON written by AmberMeta holds each fact in one field, and one field becomes one triple.
- **Queries stay short.** Finding the number of atoms takes one line of SPARQL, not three.
- **COB, the ontology MOLSIM uses for its top level, does the same** for a count that belongs to a molecule: `COB:0000801 has number of atomic nuclei` is a data property.

The cost: the OBO format cannot hold data properties, so they appear only in MOLSIM's OWL and JSON releases.

### Data properties that could become classes

If MOLSIM later follows the usual OBO practice, these 68 data properties are the candidates, listed on 2026-11-26. Each would be retired and replaced by a class. A count or a position would be written as in section 1, with `UO:0000189 count unit` where a unit is needed. A yes/no fact would become a class for each answer. The 29 data properties that hold text and the one that holds a date would stay, because OBO ontologies seldom record names, file paths or messages at all. The groups in the second column are data properties too.

**MOLSIM changes them one at a time, when a record needs it.** A data property holds only the bare value. When a record needs to say more about a value, such as which file it was read from, or that it is the mean over several replicas, MOLSIM turns that one data property into a class, written as in section 1, and as in section 2 for a statistic. Until then, the data property stays.

#### Counts: 48

| Data property | Group |
|---|---|
| `MOLSIM:001122 number of total atoms` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001124 number of total residues` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001126 number of ligands` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001127 number of charged ligands` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001128 number of ligand conformers` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001129 number of total atoms in the largest residue` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001130 number of extra points` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002122 number of solvent molecules` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002215 protein atom count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002216 nucleic acid atom count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002217 lipid atom count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002218 ion atom count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002219 solvent atom count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002220 other atom count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002221 protein residue count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002222 nucleic acid residue count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002223 lipid residue count` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002224 number of nucleosomes` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002225 number of nucleotides per DNA strand` | `MOLSIM:001121 has composition count` |
| `MOLSIM:002316 number of solute residues` | `MOLSIM:001121 has composition count` |
| `MOLSIM:001132 number of total bonds with hydrogens` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001133 number of total bonds without hydrogens` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001134 number of total angles with hydrogens` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001135 number of total angles without hydrogens` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001136 number of total dihedral angles with hydrogens` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001137 number of total dihedral angles without hydrogens` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001138 number of total excluded atom pairs` | `MOLSIM:001131 has topological count` |
| `MOLSIM:002125 number of total angles` | `MOLSIM:001131 has topological count` |
| `MOLSIM:002126 number of total dihedrals` | `MOLSIM:001131 has topological count` |
| `MOLSIM:001140 number of total bonds with constraints` | `MOLSIM:001139 has constraint count` |
| `MOLSIM:001141 number of total angles with constraints` | `MOLSIM:001139 has constraint count` |
| `MOLSIM:001142 number of total dihedrals with constraints` | `MOLSIM:001139 has constraint count` |
| `MOLSIM:001123 number of total distinct atoms` | `MOLSIM:001143 has force field parameter count` |
| `MOLSIM:001144 number of total unique bond types` | `MOLSIM:001143 has force field parameter count` |
| `MOLSIM:001145 number of total unique angle types` | `MOLSIM:001143 has force field parameter count` |
| `MOLSIM:001146 number of total unique dihedral types` | `MOLSIM:001143 has force field parameter count` |
| `MOLSIM:001147 number of total atom types in the parameter file` | `MOLSIM:001143 has force field parameter count` |
| `MOLSIM:001148 number of total distinct hydrogen bond pair types` | `MOLSIM:001143 has force field parameter count` |
| `MOLSIM:001150 number of total perturbed bonds` | `MOLSIM:001149 has alchemical transformation count` |
| `MOLSIM:001151 number of total perturbed angles` | `MOLSIM:001149 has alchemical transformation count` |
| `MOLSIM:001152 number of total perturbed dihedrals` | `MOLSIM:001149 has alchemical transformation count` |
| `MOLSIM:001153 number of total bonds with all atoms in the perturbed group` | `MOLSIM:001149 has alchemical transformation count` |
| `MOLSIM:001154 number of total angles with all atoms in perturbed groups` | `MOLSIM:001149 has alchemical transformation count` |
| `MOLSIM:001155 number of total dihedrals with all atoms in perturbed groups` | `MOLSIM:001149 has alchemical transformation count` |
| `MOLSIM:002123 number of atoms per frame` | `MOLSIM:002137 has trajectory metadata` |
| `MOLSIM:002138 number of frames` | `MOLSIM:002137 has trajectory metadata` |
| `MOLSIM:002127 number of constraint failures` | `MOLSIM:002149 has diagnostic record` |
| `MOLSIM:002201 total simulation steps` | none |

#### Positions in a list: 2

| Data property | Group |
|---|---|
| `MOLSIM:001125 last solute residue number` | `MOLSIM:002284 has topology index` |
| `MOLSIM:002121 first solvent molecule index` | `MOLSIM:002284 has topology index` |

#### Yes/no facts: 18

| Data property | Group |
|---|---|
| `MOLSIM:001157 has ligand` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:001158 has added salt` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:001160 has multiple starting conformations` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002128 has completion status` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002134 has box dimensions flag` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002193 is charge neutral` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002242 contains antibody` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002243 contains nanobody` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002244 contains linker histone` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002245 histone tails present` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002261 has symmetric leaflet composition` | `MOLSIM:001156 has state descriptor` |
| `MOLSIM:002183 is degraded extraction mode` | `MOLSIM:002149 has diagnostic record` |
| `MOLSIM:002200 HMR inferred from timestep flag` | `MOLSIM:002149 has diagnostic record` |
| `MOLSIM:002130 coordinate wrapping flag` | `MOLSIM:002288 has file content flag` |
| `MOLSIM:002135 has velocities flag` | `MOLSIM:002288 has file content flag` |
| `MOLSIM:002179 has coordinates array` | `MOLSIM:002288 has file content flag` |
| `MOLSIM:002180 has forces array` | `MOLSIM:002288 has file content flag` |
| `MOLSIM:002181 has time array` | `MOLSIM:002288 has file content flag` |

## Open points

- **The kinds of unit have not been checked by domain experts.** Each unit rule names a kind of unit, such as a length unit. A check that enforces a wrong kind would reject correct data.
- **"Is about" was made for information.** IAO says that only an information entity can be about something, and MOLSIM's release includes that statement through its IAO import. A reasoner therefore concludes that every quantity with an "is about" link is an information entity. For example, it treats a temperature value as information about the run. This causes no contradiction, but MOLSIM has not decided that quantities are information.
- **Rules also apply to subclasses.** A record typed with a subclass must follow the rules of every class above it as well. A program that checks data therefore needs MOLSIM's class hierarchy next to the data.
