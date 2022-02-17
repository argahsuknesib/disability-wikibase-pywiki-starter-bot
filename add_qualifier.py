# -*- coding: utf-8  -*-
"""
Adding a qualifier to existing claims/statements
"""
# coding=utf-8
import sys, os, traceback
import pywikibot
from pywikibot import config2
import json
from SPARQLWrapper import SPARQLWrapper, JSON
from Enum.PropertyDatatypeEnum import PropertyDataType
from pywikibot.data import api
# application config
import configparser
from datetime import timedelta
import time
"""
THIS CLASS RUNS FREQUENTLY TO MONITOR THE CHANGES AND IMPORT WIKIDATA CHANGES IF ANY
"""

class MonitorChanges:
    config = configparser.ConfigParser()
    config.read('config/application.config.ini')

    family = 'my'
    mylang = 'my'
    familyfile = os.path.relpath("./config/my_family.py")
    if not os.path.isfile(familyfile):
        print("family file %s is missing" % (familyfile))
    config2.register_family_file(family, familyfile)
    config2.password_file = "user-password.py"
    # config2.usernames['my']['my'] = 'DG Regio'
    # config2.usernames['my']['my'] = 'WikibaseAdmin'
    config2.usernames['my']['my'] = config.get('wikibase', 'user')

    # connect to the wikibase
    wikibase = pywikibot.Site("my", "my")
    wikibase_repo = wikibase.data_repository()

    wikidata = pywikibot.Site("wikidata", "wikidata")
    wikidata_repo = wikidata.data_repository()

    sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))
    site = pywikibot.Site()

    item = pywikibot.ItemPage(wikibase_repo, "Q2")
    item.get() #Fetch all page data, and cache it.

    #QUALIFIER FOR EXISTENCE STATEMENTS/CLAIMS
    qualifier = pywikibot.Claim(wikibase_repo, u'P286')
    target = pywikibot.ItemPage(wikibase_repo, "Q1")
    qualifier.setTarget(target)
    for claim in item.claims['P4']: #Finds all statements (P131)
        if 'P286' not in claim.qualifiers: #If not already exist
            claim.addQualifier(qualifier, summary=u'Adding a qualifier.') #Adding qualifier to all statements (P131)