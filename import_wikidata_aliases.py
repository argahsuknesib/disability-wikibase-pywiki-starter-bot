# coding=utf-8
import sys, os, traceback
import csv
import pywikibot
from pywikibot import config2
from datetime import datetime
import requests
import json
import csv
from SPARQLWrapper import SPARQLWrapper, JSON
import time
from Enum.PropertyDatatypeEnum import PropertyDataType
from pywikibot.data import api
# application config
import configparser
import re
from logger import DebugLogger
"""
THIS CLASS HELPS TO CREATE CLAIMS WITH EXISTING ITEMS AND PROPERTIES
"""

config = configparser.ConfigParser()
config.read('config/application.config.ini')

family = 'my'
mylang = 'my'
familyfile = os.path.relpath("./config/my_family.py")
if not os.path.isfile(familyfile):
    print("family file %s is missing" % (familyfile))
config2.register_family_file(family, familyfile)
config2.password_file = "user-password.py"
config2.usernames['my']['my'] = config.get('wikibase', 'user')

from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier
from util.util import WikibaseImporter


# connect to the wikibase
wikibase = pywikibot.Site("my", "my")
sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
site = pywikibot.Site()

# connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")


class Import_wikidata_aliases:
    def __init__(self, wikidata, wikibase, sparql):
        self.wikidata=wikidata
        self.sparql=sparql
        self.wikibase=wikibase
        self.wikidata_repo=wikidata.data_repository()
        self.wikibase_repo=wikibase.data_repository()

        identifier = PropertyWikidataIdentifier()
        identifier.get(self.wikibase_repo)
        self.wikidata_code_property_id = identifier.itemIdentifier
        self.wikidata_pid_property_id = identifier.propertyIdentifier
        self.wikibase_importer = WikibaseImporter(self.wikibase_repo,self.wikidata_repo)

    def get_all_wikidata_corresponding_item(self):
        query="""
            select DISTINCT ?s ?qid where{
            ?s ?p ?o;
                  wdt:P1 ?qid
            }
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # for result in results['results']['bindings']:
        #     print(result)
        if (len(results['results']['bindings']) > 0):
            map_wdqid_wbqid={}
            for result in results['results']['bindings']:
                map_wdqid_wbqid[result.get('s',{}).get('value',{}).split("/")[-1]]=result.get('qid',{}).get('value',{})
        return map_wdqid_wbqid

    def start(self):
        map_entity=self.get_all_wikidata_corresponding_item()
        for wb_qid in map_entity:
            wd_qid=map_entity[wb_qid]
            if(wb_qid.startswith("Q")):
                wikibase_item= pywikibot.ItemPage(self.wikibase_repo, wb_qid)
                wikidata_item= pywikibot.ItemPage(self.wikidata_repo, wd_qid)
                self.wikibase_importer.changeAliases(wikidata_item, wikibase_item)

def test():
    iwa=Import_wikidata_aliases(wikidata, wikibase,sparql)
    iwa.start()

test()