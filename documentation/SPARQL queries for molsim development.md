SPARQL Queries can be used to check the ontology consistencies. In Protégé, the queries can be done via its SPARQL Query window. This is activated via *Window -> Tabs -> SPARQL* Query.

Here are some examples:

1. *Get distinct Classes or Properties without rdfs:comment*

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
        ?entity a owl:Class . 
        BIND("Class" AS ?type) } 
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
