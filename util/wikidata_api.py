# coding=utf-8
import sys, os, traceback
import csv
import pywikibot
from pywikibot import config2
from datetime import datetime
import requests
import json
import csv
from IdSparql import IdSparql
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

# connect to the wikibase
wikibase = pywikibot.Site("my", "my")
sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
site = pywikibot.Site()

# connect to wikidata
wikidata = pywikibot.Site("wikidata", "wikidata")


class Wikidata_Api:
    def __init__(self, wikidata, wikibase, sparql):
        self.wikidata=wikidata
        self.sparql=sparql
        self.wikibase=wikibase
        self.wikidata_repo=wikidata.data_repository()
        self.wikibase_repo=wikibase.data_repository()

    if __name__ == '__main__':
        "only called when instantiated"

    
