#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 13:27:53 2025

@author: hannah
"""


import xml.etree.ElementTree as ET
import re
import html
import pandas as pd
# import numpy as np
import time
import os
import requests
import json
from collections import OrderedDict
# import csv
import sys
import yaml
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from datetime import date
# import nltk
# nltk.download("punkt_tab")
# nltk.download("wordnet")

def find_files(directory):
    xlsx_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".xlsx") and (file == "isa.study.xlsx" or file == "isa.assay.xlsx"):
                path = os.path.join(root, file)
                xlsx_files.append(path)
    return xlsx_files
    

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# getting the namespace abbreviation based on the namespace url
def namespacing(elem):
    # remove brackets from etree parsing
    sep = elem[1:].split("}")
    # getting the namespace abbreviation from the namespaces dict
    if sep[0] in namespaces:
        sep[0] = namespaces[sep[0]]
    # join the element back together the way it is written in the owl file
    sep = ":".join(sep)
    # returning the joined string
    return sep

# getting the attribute information of a parsed object
def ns_att(elem):
    # ignore None elements
    if elem == {}:
        # returning None
        return ""
    # join the attribute dict together as a string
    for key in elem:
        ns = namespacing(key) + '="' + elem[key] + '"'
        # print("RES", elem[key])
        # returning the joined string
        return ns
    
################ mask html characters ###################
def html_characters(text):
    return html.escape(text)
################ mask html characters ###################


#################### parsing one owl object ##################
def parse_element(element, i=0):
    # declaring the output dict
    if len(element) == 0:
        result = None
    else:
        result = {}
    # iterating over all top level children of the object
    for child in element:
        # getting the namespace annotation
        owl_object = ""
        owl_object = owl_object + namespacing(child.tag)

        # getting the resource annotation
        attributes = ns_att(child.attrib)

        # creating the key from the namespace and resource annotation        
        if attributes != None:
            tag = owl_object + " " + attributes
        else:
            tag = owl_object
        
        # allow key duplication
        if tag in result.keys():
            tag = tag + "REP" + str(i)
            i += 1
        
        # checking if leaf level is reached, if not, call the parser again
        if len(child) > 0:
            result[tag] = parse_element(child, i)
        # if leaf level is reached, save text if exists
        else:
            if child.text == None:
                result[tag] = ""
            else:
                result[tag] = html_characters(child.text.strip())
    # return the parsed dict
    return result
####################

################# writing the body #################
def write_body(elem, f, indent=1, is_top_level=True):
    duplication_pattern = r"REP\d+"
    for idx, (key, value) in enumerate(elem.items()):
        match = re.findall(duplication_pattern, key)
        if match:
            key = key[:-len(match[0])]
        if isinstance(value, dict):
            f.write("\t" * indent + f"<{key}>\n")
            write_body(value, f, indent + 1, is_top_level=False)
            f.write("\t" * indent + f'</{key.split(" ")[0]}>\n')
        else:
            if value == "":
                f.write("\t" * indent + "<" + key + "/>\n")
            elif value == None:
                f.write("\t" * indent + "<" + key + "/>\n\n")
            else:
                f.write("\t" * indent + "<" + key + f">{value}</" + key.split(" ")[0] + ">\n")
        if is_top_level and idx <= len(elem) - 1 and value != None:
            f.write("\n")
################# writing the body #################

################# extracting labels from class dict #################
def find_lables(dictionary):
    results = []
    search_key = "rdfs:label"
    definition_key = "obo:IAO_0000115"
    
    def search_recursion(subdict, parent_key=""):
        # output = tuple()
        label = None
        definition = None
        if isinstance(subdict, dict):
            for key, value in subdict.items():
                if search_key in key:
                    label = value
                if definition_key in key:
                    definition = value
                if isinstance(value, dict):
                    search_recursion(value, key)
            if search_key in key:
                parent_key = parent_key.split('"')[1]
                results.append((value, parent_key, definition))
    search_recursion(dictionary)
    return results
################# extracting labels from class dict #################

################# replace unicode hexcode with semicolon  #################
def replace_semicolon(element):
    return [entry.replace("&#x27s;", "'") if isinstance(entry, str) else entry for entry in element]
################# replace unicode hexcode with semicolon  #################


################# replace unicode hexcode with semicolon  #################
def replace_semicolon_list(element):
    if isinstance(element, list):
        return [replace_semicolon_list(entry) for entry in element]
    elif isinstance(element, str):
        return element.replace("&#x27;", "'")  # Replace with apostrophe
    else:
        return element  # Leave other data types unchanged
################# replace unicode hexcode with semicolon  #################


################ reading the base input file ##############
wd = os.getcwd()
wd="/home/hannah/UsadellabARCs_small/molsim-ontology/"

# if len(sys.argv) != 2:
#     print("Usage: python3 prep_BD_files.py <config.yml>")
#     sys.exit(1)

# config_path = sys.argv[1]
config_path = os.path.join(wd, "src/ontology/mappings/check_api.yml")

if not os.path.exists(config_path):
    print("Error: the yml file you put in doesn't exist or the file path is wrong.")
    sys.exit(1)
    
with open(config_path, "r") as f:
    config = yaml.safe_load(f)
    
input_file = os.path.join(wd, config["input"]["filled_ontology_file"])
obo_ontologies_file = os.path.join(wd, config["input"]["obo_ontologies_file"])
output_file = os.path.join(wd, config["output"]["term_suggestion_list"])


makedirs(os.path.dirname(output_file))
# opening a base ontology structure to be parsed
with open(input_file, "r") as file:
    owl_content = file.read()
################ reading the base input file ##############

################ parsing the base header ################
parsing_start = time.time()
# pre-defining the header as rdf
onto_head = {"rdf:RDF":{}}
header = re.search(r'<rdf:RDF([^>]*)>', owl_content)
namespaces = {}
# searching for the RDF header to parse
if header:
    # finding all attributes of the header
    rdf_rdf_attributes = header.group(1)
    attributes = re.findall(r'([\w:]+)=["\'](.*?)["\']', rdf_rdf_attributes)
    # saving the header attributes in a dict
    for key, value in attributes:
        onto_head["rdf:RDF"][key] = value
        if len(key.split(":")) == 1:
            pass
        else: 
            namespaces[value] = key.split(":")[1]
else:
    print("rdf:RDF element not found in the file.")
################ parsing the base header ################



################ parsing the content ################
tree = ET.parse(input_file)
root = tree.getroot()
terms = {}
ontology = {}
annotation_properties = {}
classes = {}
object_properties = {}
data_properties = {}
axioms = {}
instances = {}
tans = {}
sources = {}


# iterating over all ontology elements
for child in root[:]:
    # getting the namespace annotation
    owl_object = ""
    owl_object = owl_object + (namespacing(child.tag))

    # getting the resource annotation
    attribs = ns_att(child.attrib)
    res = owl_object + " " + attribs
    
    # parsing the object
    parsed_element = parse_element(child)
    
    # saving the parsed object
    if "Ontology" in owl_object:
        ontology[res] = parsed_element
    elif "AnnotationProperty" in owl_object:
        annotation_properties[res] = parsed_element
    elif "ObjectProperty" in owl_object:
        object_properties[res] = parsed_element
    elif "Class" in owl_object:
        classes[res] = parsed_element
    elif "DatatypeProperty" in owl_object:
        data_properties[res] = parsed_element
    elif "NamedIndividual" in owl_object:
        instances[res] = parsed_element
    elif "Axiom" in owl_object:
        axioms[res] = parsed_element
    terms[res] = parsed_element
parsing_end = time.time()
################ parsing the content ################


labels = find_lables(classes)
labels = replace_semicolon(labels)

with open(obo_ontologies_file, "r") as f:
    ontologies_json = json.load(f)
ontologies = [entry["id"] for entry in ontologies_json["ontologies"]]
ontologies = ""
for entry in ontologies_json["ontologies"]:
    ontologies = ontologies + entry["id"] + "," 
if ontologies[-1] == ",":
    ontologies = ontologies[:-1]


# TS4TIB API
# api_url = "https://service.tib.eu/ts4tib/api/search"
# options = OrderedDict()
# options["schema"] = "collection"
# options["classification"] = "DataPLANT"
# options["exclusiveFilter"] = "false"
# options["obsoletes"] = "false"
# options["local"] = "false"

# OLS4 API
api_url = "https://www.ebi.ac.uk/ols4/api/search"
options = OrderedDict()
options["ontology"] = ontologies
options["queryFields"] = "label"
options["obsoletes"] = "false"
options["local"] = "true"
options["exact"] = "false"

suggestions = {}


def preprocess_label(rdfslabel):
    return {lemmatizer.lemmatize(word.lower()) for word in word_tokenize(rdfslabel) }


def jaccard(term1, term2):
    set1 = preprocess_label(term1)
    set2 = preprocess_label(term2)
    return len(set1 & set2) / len(set1 | set2)

model = SentenceTransformer("all-MiniLM-L6-v2")
lemmatizer = WordNetLemmatizer()


i = 0
for query in labels[:]:
    print(i)
    if "MOLSIM" in query[1] and "DEPRECATED" not in query[1]:
        options["q"] = query[0]
    
    
        test_url = api_url + "?"
        for key, value in options.items():
            test_url = test_url + key + "=" + value + "&"
        
        response = requests.get(test_url)
        results = json.loads(response.content)["response"]["docs"]
        for elem in results[:10]:
            iri = elem["iri"]
            obo_id = elem["obo_id"]
            label = elem["label"]
            if "ontology_prefix" in elem:
                on = elem["ontology_prefix"]
            elif "ontology_name" in elem:
                on = elem["ontology_name"]
            else:
                print("no ontology prefix")
                on = ""
            key = query[1] + "###" + obo_id
            
            if ":" not in obo_id:
                obo_id = on + ":" + obo_id
            if "description" in elem:
                if len(elem["description"]) > 0:
                    description = " ".join(elem["description"])
                else:
                    description = ""
            else:
                description = ""
            if key not in suggestions:
                vector1 = model.encode(query[2]).reshape(1, -1)
                vector2 = model.encode(description).reshape(1, -1)
                definition_score = cosine_similarity(vector1, vector2)[0][0]
                
                label_score = jaccard(query[0], label)
                score = (0.7*label_score) + (0.3*definition_score)
                
                if score > 0.7:
                    suggestions[key]= (query[0], query[1].split("org/obo/")[1].replace("_", ":").lower(), label, obo_id, on, score)
                # print(query[0], "\t", label, "\t", label_score, "\t", definition_score, "\t", score)

            
    i += 1


data = [value for value in suggestions.values()]
df = pd.DataFrame(data, columns=["subject_label", "subject_id", "object_label", "object_id", "object_source", "confidence"])

ns_dict = {}

api_url = "https://www.ebi.ac.uk/ols4/api/ontologies/"

for query in df["object_source"].unique():
    test_url = api_url + query
    response = requests.get(test_url)
    results = json.loads(response.content)
    
    version_iri = results["config"]["versionIri"]
    file_location = results["config"]["fileLocation"]
    ns_dict[query] = (file_location, version_iri)


df["object_source"] = df["object_source"].map(lambda x: ns_dict[x][0])
df["object_source_version"] = df["object_source"].map(lambda x: next((value[1] for key, value in ns_dict.items() if value[0] == x), None))
df["predicate_id"] = "skos:closeMatch"
df["mapping_justification"] = "semapv:CompositeMatching"
df["mapping_date"] = date.today()
df["mapping_tool"] = "https://github.com/CPCLab/molsim-ontology/tree/main/src/ontology/mappings/query_OBO_space.py"
df["creator_id"] = "orcid:0000-0002-0476-9699"

df.to_csv(output_file, sep="\t", index=False)

