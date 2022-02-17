# coding=utf-8
# application config
import configparser
import csv
import json
import os
import sys
import traceback

import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON
from pywikibot import config2

from logger import DebugLogger

appConfig = configparser.ConfigParser()
appConfig.read('config/application.config.ini')

family = 'my'
mylang = 'my'
familyfile = os.path.relpath("./config/my_family.py")
if not os.path.isfile(familyfile):
    print("family file %s is missing" % (familyfile))
config2.register_family_file(family, familyfile)
config2.password_file = "user-password.py"
config2.usernames['my']['my'] = appConfig.get('wikibase', 'user')

# connect to the wikibase
wikibase = pywikibot.Site("my", "my")
wikibase_repo = wikibase.data_repository()


sparql = SPARQLWrapper(appConfig.get('wikibase', 'sparqlEndPoint'))
site = pywikibot.Site()


def capitaliseFirstLetter(word):
    return word.capitalize().rstrip()

# get items with sparql


def getWikiItemSparql(label):
    query = """
         select ?label ?s where
                {
                  ?s ?p ?o.
                  ?s rdfs:label ?label .
                  FILTER(lang(?label)='fr' || lang(?label)='en')
                  FILTER(?label = '""" + label + """'@en)

                }
         """
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    print(results)
    return results

# Searches a concept based on its label with a API call


def searchWikiItem(label):
    if label is None:
        return True
    params = {'action': 'wbsearchentities', 'format': 'json',
              'language': 'en', 'type': 'item', 'limit': 1,
              'search': label}
    request = wikibase._simple_request(**params)
    result = request.submit()
    print(result)
    return True if len(result['search']) > 0 else False


def createProperty(label, description, datatype, property_map):
    if (capitaliseFirstLetter(label.rstrip()) in property_map):
        return property_map
    property_result = getWikiItemSparql(capitaliseFirstLetter(label.rstrip()))
    if (len(property_result['results']['bindings']) == 0):
        data = {
            'datatype': datatype,  # mandatory
            'descriptions': {
                'en': {
                    'language': 'en',
                    'value': capitaliseFirstLetter(description).rstrip() + " en"
                }
            },
            'labels': {
                'en': {
                    'language': 'en',
                    'value': capitaliseFirstLetter(label).rstrip()
                }
            }
        }
        params = {
            'action': 'wbeditentity',
            'new': 'property',
            'data': json.dumps(data),
            'summary': 'creating properties from scripts',
            'token': wikibase.tokens['edit']
        }
        req = wikibase._simple_request(**params)
        response = req.submit()
        property_map[capitaliseFirstLetter(
            label).rstrip()] = response['entity']['id']
        print(response)
        return property_map
    else:
        property_map[capitaliseFirstLetter(label).rstrip(
        )] = property_result['results']['bindings'][0]['s']['value'].split("/")[-1]
        return property_map


def createPropertyV2(labelStr, label, description, datatype, aliases, property_map):
    if (capitaliseFirstLetter(labelStr.rstrip()) in property_map):
        return property_map
    property_result = getWikiItemSparql(
        capitaliseFirstLetter(labelStr.rstrip()))
    if (len(property_result['results']['bindings']) == 0):
        data = {}
        print(f"creating property {labelStr} ")
        data['labels'] = label
        data['descriptions'] = description
        if(len(aliases) > 0):
            data['aliases'] = aliases
        new_property = pywikibot.PropertyPage(wikibase_repo, datatype=datatype)
        new_property.editEntity(data)
        # new_property.get();
        print(new_property.type, new_property.id)
        property_map[capitaliseFirstLetter(
            labelStr).rstrip()] = new_property.id
        return property_map
    else:
        data = {}
        print(f"creating property {labelStr} ")
        data['labels'] = label
        data['descriptions'] = description
        if (len(aliases) > 0):
            data['aliases'] = aliases
        exist_property = pywikibot.PropertyPage(
            wikibase_repo, property_result['results']['bindings'][0]['s']['value'].split("/")[-1])
        exist_property.get()
        exist_property.editEntity(data)

        print(exist_property.type, exist_property.id)
        property_map[capitaliseFirstLetter(
            labelStr).rstrip()] = exist_property.id
        return property_map


# Reading CSV
def readFileAndProcess():
    with open('data/PredicatesWithAliases.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        property_map = {}
        for row in csv_reader:
            print(f'Processing line number of {line_count} ')
            if line_count == 0:
                print(f'Column Headings are {", ".join(row)}')
                line_count += 1
            else:
                try:
                    description = ""
                    aliases = ""
                    if not row[2]:
                        description = {"en": capitaliseFirstLetter(
                            row[0]).rstrip()+" : property"}
                    else:
                        description = {
                            "en": capitaliseFirstLetter(row[2]).rstrip()}
                    if len(row[3]) > 0:
                        aliases = {"en": capitaliseFirstLetter(
                            row[3]).rstrip().split(",")}

                    label = {"en": row[0].rstrip().lstrip().lower()}
                    labelStr = row[0].rstrip().lstrip().lower()
                    datatype = row[1]
                    property_map = createPropertyV2(
                        labelStr, label, description, datatype, aliases, property_map)
                except Exception as e:
                    err_msg = f"ERROR : Entity:  {row[1].rstrip()} , Property {row[2].rstrip()}  Line count: {line_count}"
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    tb = traceback.extract_tb(exc_tb)[-1]
                    err_trace = f"ERROR_TRACE >>>: + {exc_type} , method: {tb[2]} , line-no: {tb[1]}"
                    logger = DebugLogger()
                    logger.logError('CREATE_ITEM', e, exc_type,
                                    exc_obj, exc_tb, tb, err_msg)
                line_count += 1
        print(f'Completed Creating Properties total of {line_count} ')


def test():
    property_map = {}
    property_map = createProperty(
        'Has wikidata identifier', 'Corresponding wikidata code for the entity', 'external-id', property_map)
    print(property_map)


# test()
readFileAndProcess()
exit()
