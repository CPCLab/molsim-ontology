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
from datetime import date, datetime
import subprocess
# import nltk
# nltk.download("punkt_tab")
# nltk.download("wordnet")

    

def makedirs(path):
    if not os.path.exists(path):
        os.makedirs(path)

# getting the namespace abbreviation based on the namespace url
def namespacing(elem, namespaces):
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
def ns_att(elem, namespaces):
    # ignore None elements
    if elem == {}:
        # returning None
        return ""
    # join the attribute dict together as a string
    for key in elem:
        ns = namespacing(key, namespaces) + '="' + elem[key] + '"'
        # print("RES", elem[key])
        # returning the joined string
        return ns
    
################ mask html characters ###################
def html_characters(text):
    return html.escape(text)
################ mask html characters ###################


#################### parsing one owl object ##################
def parse_element(element, namespaces, i=0):
    # declaring the output dict
    if len(element) == 0:
        result = None
    else:
        result = {}
    # iterating over all top level children of the object
    for child in element:
        # getting the namespace annotation
        owl_object = ""
        owl_object = owl_object + namespacing(child.tag, namespaces)

        # getting the resource annotation
        attributes = ns_att(child.attrib, namespaces)

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
            result[tag] = parse_element(child, namespaces, i)
        # if leaf level is reached, save text if exists
        else:
            if child.text == None:
                result[tag] = ""
            else:
                result[tag] = html_characters(child.text.strip())
    # return the parsed dict
    return result
####################

################# extracting labels from class dict #################
def find_lables(dictionary):
    print("Extracting terms from ontology.")
    results = []
    search_key = "rdfs:label"
    definition_key = "obo:IAO_0000115"
    
    def search_recursion(subdict, parent_key=""):
        # output = tuple()
        # label = None
        definition = None
        if isinstance(subdict, dict):
            for key, value in subdict.items():
                # if search_key in key:
                #     label = value
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

################# replace unicode hexcode with apostrophe  #################
def replace_apostrophe(element):
    print("Replacing apostrophe in extracted terms.")
    return [entry.replace("&#x27s;", "'") if isinstance(entry, str) else entry for entry in element]
################# replace unicode hexcode with apostrophe  #################


################# replace unicode hexcode with apostrophe  #################
def replace_semicolon_list(element):
    if isinstance(element, list):
        return [replace_apostrophe_list(entry) for entry in element]
    elif isinstance(element, str):
        return element.replace("&#x27;", "'")  # Replace with apostrophe
    else:
        return element  # Leave other data types unchanged
################# replace unicode hexcode with apostrophe  #################

################# preprocess concept labels  #################
def preprocess_label(rdfslabel, lemmatizer):
    return {lemmatizer.lemmatize(word.lower()) for word in word_tokenize(rdfslabel) }
################# preprocess concept labels  #################

################# calculate jaccard index #################
def jaccard(term1, term2, lemmatizer):
    set1 = preprocess_label(term1, lemmatizer)
    set2 = preprocess_label(term2, lemmatizer)
    return len(set1 & set2) / len(set1 | set2)
################# calculate jaccard index #################

################# opening the ontology file #################
# opening a base ontology structure to be parsed
def read_rdfxml(file):
    print("reading ontology rdf/xml file")
    with open(file, "r") as file:
        owl_content = file.read()
    return owl_content
################# opening the ontology file #################

################ parsing the base header ################
def parse_ontology_header(owl_content):
    print("Parsing ontology header.")
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
    
    return namespaces
################ parsing the base header ################

################ parsing the content ################
def parse_ontology(file, namespaces):
    print("Parsing ontology.")
    tree = ET.parse(file)
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
        owl_object = owl_object + (namespacing(child.tag, namespaces))
    
        # getting the resource annotation
        attribs = ns_att(child.attrib, namespaces)
        res = owl_object + " " + attribs
        
        # parsing the object
        parsed_element = parse_element(child, namespaces)
        
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
        
    return terms, ontology, annotation_properties, classes, object_properties, data_properties, axioms, instances, tans, sources
################ parsing the content ################

################ retrieving all ontologies in obo foundry from their json ################
# uses the public json file from here: http://obofoundry.org/registry/ontologies.jsonld
def get_obo_foundry_ontologies(obo_ontologies_file):
    print("Retrieving OBO Foundry ontology names.")
    with open(obo_ontologies_file, "r") as f:
        ontologies_json = json.load(f)
    ontologies = [entry["id"] for entry in ontologies_json["ontologies"]]
    ontologies = ""
    for entry in ontologies_json["ontologies"]:
        ontologies = ontologies + entry["id"] + "," 
    if ontologies[-1] == ",":
        ontologies = ontologies[:-1]
    
    ontologies_df = pd.DataFrame.from_dict(ontologies_json["ontologies"])
    ontologies_df.index = ontologies_df["id"]
    ontologies_df = ontologies_df[["activity_status"]]
    
    ontologies_df.to_csv(ontology_status, sep="\t")
    
    return ontologies
################ retrieving all ontologies in obo foundry from their json ################

################ mapping terms against ols4 ################
def ols4_mapping(ontologies, idspace, searchobject, searchtype="class,property,individual,ontology", number_of_inputs=None, number_of_hits=10, label_weight=0.7, description_weight=0.3, threshold=0.7):
    print("Mapping in progress.")
    # OLS4 API
    api_url = "https://www.ebi.ac.uk/ols4/api/search"
    options = OrderedDict()
    options["ontology"] = ontologies
    options["queryFields"] = "label"
    options["obsoletes"] = "false"
    options["local"] = "true"
    options["exact"] = "false"
    options["type"] = searchtype
    
    suggestions = {}
    
    model = SentenceTransformer("all-MiniLM-L6-v2")
    input_lemmatizer = WordNetLemmatizer()
    
    i = 0
    for query in searchobject[:number_of_inputs]:
        if idspace in query[1] and "DEPRECATED" not in query[1] and "obsolete" not in query[1] and "Obsolete" not in query[1]:
            print(i)
            options["q"] = query[0]
        
        
            test_url = api_url + "?"
            for key, value in options.items():
                test_url = test_url + key + "=" + value + "&"
            
            response = requests.get(test_url)
            results = json.loads(response.content)["response"]["docs"]
            for elem in results[:number_of_hits]:
                # iri = elem["iri"]
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
                    # consider if no definition is given
                    if description == "":
                        score = jaccard(query[0], label, input_lemmatizer)
                        if score > 0.7:
                            suggestions[key]= (query[0], query[1].split("org/obo/")[1].replace("_", ":").lower(), label, obo_id, on.lower(), score)
                    else:
                        if query[2] == None:
                            input_definition = ""
                        else:
                            input_definition = query[2]
                        vector1 = model.encode(input_definition).reshape(1, -1)
                        vector2 = model.encode(description).reshape(1, -1)
                        definition_score = cosine_similarity(vector1, vector2)[0][0]
                        
                        label_score = jaccard(query[0], label, input_lemmatizer)
                        score = (label_weight*label_score) + (description_weight*definition_score)
                        
                        if score > threshold:
                            suggestions[key]= (query[0], query[1].split("org/obo/")[1].replace("_", ":").lower(), label, obo_id, on.lower(), score)
                        # print(query[0], "\t", label, "\t", label_score, "\t", definition_score, "\t", score)
    
        i += 1
    
    
    data = [value for value in suggestions.values()]
    df = pd.DataFrame(data, columns=["subject_label", "subject_id", "object_label", "object_id", "object_source", "confidence"])
    
    return df
################ mapping terms against ols4 ################

################ get ontology urls ################
def get_ontology_urls(ontologies):
    print("Retrieving OBO Foundry ontology URLs.")
    ontology_list = ontologies.split(",")

    ns_dict = {}
    
    api_url = "https://www.ebi.ac.uk/ols4/api/ontologies/"
    
    for query in ontology_list:
        test_url = api_url + query
        response = requests.get(test_url)
        if response.status_code == 200:
            results = json.loads(response.content)
            
            version_iri = results["config"]["versionIri"]
            file_location = results["config"]["fileLocation"]
            ns_dict[query] = (file_location, version_iri)
    
    return ns_dict
################ get ontology urls ################

################ create sssom mapping file ################
def create_sssom_mapping_file(df, ns_dict, file_location, save_output=False):
    print("Creating output sssom file.")
    df["object_source"] = df["object_source"].map(lambda x: ns_dict[x][0])
    df["object_source_version"] = df["object_source"].map(lambda x: next((value[1] for key, value in ns_dict.items() if value[0] == x), None))
    df["predicate_id"] = "skos:closeMatch"
    df["mapping_justification"] = "semapv:CompositeMatching"
    df["mapping_date"] = date.today()
    df["mapping_tool"] = "https://github.com/CPCLab/molsim-ontology/tree/main/src/ontology/mappings/query_OBO_space.py"
    df["creator_id"] = "orcid:0000-0002-0476-9699"
    
    
    if save_output:
        directory, file = os.path.split(file_location)
        file = str(datetime.now()).split(".")[0].replace(" ", "_").replace(":", "-")[:-3] + "_" + file
        
        df.to_csv(os.path.join(directory, file), sep="\t", index=False)
################ create sssom mapping file ################





################ reading the base input file ##############
if __name__ == "__main__":
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
    input_obo_ontologies_file = os.path.join(wd, config["input"]["obo_ontologies_file"])
    input_label_weight = config["parameters"]["label_weight"]
    input_description_weight = config["parameters"]["description_weight"]
    input_threshold = config["parameters"]["threshold"]
    owl_file = os.path.join(wd, config["output"]["owl_file"])
    class_suggestion_list = os.path.join(wd, config["output"]["class_suggestion_list"])
    object_property_suggestion_list = os.path.join(wd, config["output"]["object_property_suggestion_list"])
    data_property_suggestion_list = os.path.join(wd, config["output"]["data_property_suggestion_list"])
    ontology_status = os.path.join(wd, config["output"]["ontology_status"])
    
    makedirs(os.path.dirname(class_suggestion_list))
    makedirs(os.path.dirname(ontology_status))
    
    subprocess.run(["robot", "convert", "--input", input_file, "--output", owl_file, "--format", "owl"])
    
    input_content = read_rdfxml(owl_file)
    input_namespaces = parse_ontology_header(input_content)
    input_terms, input_ontology, input_annotation_properties, input_classes, input_object_properties, input_data_properties, input_axioms, input_instances, input_tans, input_sources = parse_ontology(owl_file, input_namespaces)
    
    # retrieve input ontologies
    input_ontologies = get_obo_foundry_ontologies(input_obo_ontologies_file)
    input_ns_dict = get_ontology_urls(input_ontologies)
    
    # mapping classes
    print("Mapping classes.")
    input_labels = find_lables(input_classes)
    input_labels = replace_apostrophe(input_labels)
    input_classes_df = ols4_mapping(input_ontologies, idspace="MOLSIM", searchobject=input_labels, searchtype="class", label_weight=input_label_weight, description_weight=input_description_weight, threshold=input_threshold, number_of_inputs=3)
    create_sssom_mapping_file(input_classes_df, input_ns_dict, class_suggestion_list, save_output=True)

    # mapping object properties
    print("Mapping object properties.")
    input_object_properties = find_lables(input_object_properties)
    input_object_properties = replace_apostrophe(input_object_properties)
    input_object_properties_df = ols4_mapping(input_ontologies, idspace="MOLSIM", searchobject=input_object_properties, label_weight=input_label_weight, description_weight=input_description_weight, threshold=input_threshold)
    create_sssom_mapping_file(input_object_properties_df, input_ns_dict, object_property_suggestion_list, save_output=True)
    
    # mapping data properties
    print("mapping data properties.")
    input_data_properties = find_lables(input_data_properties)
    input_data_properties = replace_apostrophe(input_data_properties)
    input_data_properties_df = ols4_mapping(input_ontologies, idspace="MOLSIM", searchobject=input_data_properties, label_weight=input_label_weight, description_weight=input_description_weight, threshold=input_threshold, number_of_inputs=3)
    create_sssom_mapping_file(input_data_properties_df, input_ns_dict, data_property_suggestion_list, save_output=True)

    





