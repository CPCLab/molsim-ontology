## SPARQL Queries Example for validating MOLSIM

SPARQL Queries can be used to check the ontology consistencies. In Protégé, the queries can be done via its SPARQL Query window. This is activated via *Window -> Tabs -> SPARQL Query*.

Here are some examples:

1. Get distinct Classes or Properties without `rdfs:comment`.

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
PREFIX owl: <http://www.w3.org/2002/07/owl#> 

SELECT DISTINCT ?entity ?label ?type 
WHERE { 
    { 
        ?entity a owl:DatatypeProperty . 
        BIND("Data Property" AS ?type) 
    }     
   UNION { 
        ?entity a owl:ObjectProperty . 
        BIND("Object Property" AS ?type) 
   } 
    UNION { 
        ?entity a owl:Class . 
        BIND("Class" AS ?type) 
    } 
    OPTIONAL { ?entity rdfs:label ?label } 
    FILTER NOT EXISTS { ?entity rdfs:comment ?comment } } 
ORDER BY ?type ?entity
```

2. Get classes or properties in which its `rdfs:comments` does not have language tag

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT DISTINCT ?entity ?comment ?type
WHERE {
  {
    ?entity a owl:Class ;
            rdfs:comment ?comment .
    BIND("Class" AS ?type)
  } 
  UNION 
  {
    ?entity a rdf:Property ;
            rdfs:comment ?comment .
    BIND("Property" AS ?type)
  }

  FILTER (lang(?comment) = "")
}
ORDER BY ?type ?entity
```

3. Get classes or properties without IAO `definition` (`obo:IAO_0000115`)

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT DISTINCT ?class ?classLabel ?property ?propertyValue
WHERE {

# Find all classes in the ontology

  ?class a owl:Class .

# Get the class label if available

  OPTIONAL { ?class rdfs:label ?classLabel . }

# Get properties and their values for these classes

  OPTIONAL { ?class ?property ?propertyValue . }

# Filter out the rdf:type triple as it's not informative here

  FILTER (?property != rdf:type)

# Filter out deprecated classes

  FILTER NOT EXISTS { ?class owl:deprecated true }

# Filter out blank nodes

  FILTER (!isBlank(?class))

# Exclude classes that have a definition (obo:IAO_0000115)

  FILTER NOT EXISTS { ?class obo:IAO_0000115 ?definition }
}
ORDER BY ?class ?property
```
3. Get classes or properties without language tag accompanying `definition` (`obo:IAO_0000115`) property

```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX obo: <http://purl.obolibrary.org/obo/>

SELECT DISTINCT ?entity ?definition ?type
WHERE {
  {
    ?entity a owl:Class ;
            obo:IAO_0000115 ?definition .
    BIND("Class" AS ?type)
  } 
  UNION 
  {
    ?entity a rdf:Property ;
            obo:IAO_0000115 ?definition .
    BIND("Property" AS ?type)
  }

  FILTER (lang(?definition) = "")
}
ORDER BY ?type ?entity
```