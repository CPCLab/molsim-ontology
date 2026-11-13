# Writing data with MOLSIM terms

This page shows how to describe simulation data with MOLSIM terms, written as RDF in Turtle. It covers patterns: 1) a quantity with a unit, and 2) a statistic over a run. A check that tests data against these patterns, written in SHACL, is being prepared and is not published yet.

## 1. A quantity with a unit

**In short:** a number with a unit is written as a node of its own. The node says which MOLSIM class it belongs to, holds one number and one unit from the Unit Ontology (UO), and says what it describes.

This applies to every MOLSIM class that carries a unit rule and a value rule: 101 classes, measured 2026-11-12.

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

## Open points

- **The kinds of unit have not been checked by domain experts.** Each unit rule names a kind of unit, such as a length unit. A check that enforces a wrong kind would reject correct data.
- **"Is about" was made for information.** IAO says that only an information entity can be about something, and MOLSIM's release includes that statement through its IAO import. A reasoner therefore concludes that every quantity with an "is about" link is an information entity. For example, it treats a temperature value as information about the run. This causes no contradiction, but MOLSIM has not decided that quantities are information.
- **Rules also apply to subclasses.** A record typed with a subclass must follow the rules of every class above it as well. A program that checks data therefore needs MOLSIM's class hierarchy next to the data.
