# coding=utf-8
import sys, os, traceback
import csv
import pywikibot
from pywikibot import config2
from datetime import datetime
import requests
import json
from IdSparql import IdSparql
from SPARQLWrapper import SPARQLWrapper, JSON
import time
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

    def getClaim(self, item_id):
        entity = pywikibot.ItemPage(self.wikibase_repo, item_id)
        claims = entity.get(u'claims')  # Get all the existing claims
        return claims

    def getClaimFromWikidataRepo(self, item_id):
        entity = pywikibot.ItemPage(self.wikidata_repo, item_id)
        claims = entity.get(u'claims')  # Get all the existing claims
        return claims

    wikidata_code_property_id = None
    def getWikiDataItemtifier(self):
        query = """
            select ?wikicode
            {
              ?wikicode rdfs:label ?plabel .
              FILTER(?plabel = 'Wikidata QID'@en) .
              FILTER(lang(?plabel)='fr' || lang(?plabel)='en')
            }
            limit 1


            """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # for result in results['results']['bindings']:
        #     print(result)
        if (len(results['results']['bindings']) > 0):
            self.wikidata_code_property_id = results['results']['bindings'][0]['wikicode']['value'].split("/")[-1]
        return results

    wikidata_pid_property_id = None
    def getWikiDataPropertyItemtifier(self):
        query = """
                select ?s
                {
                  ?s rdfs:label ?plabel .
                  FILTER(?plabel = 'Wikidata PID'@en) .
                  FILTER(lang(?plabel)='fr' || lang(?plabel)='en')
                }
                limit 1
                """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # for result in results['results']['bindings']:
        #     print(result)
        if (len(results['results']['bindings']) > 0):
            self.wikidata_pid_property_id = results['results']['bindings'][0]['s']['value'].split("/")[-1]
        return results

    def getWikibasePIDbyWikidataPID(self,pid) :
        query="""
            select ?s  where
            {
                ?s  ?p ?o; 
                rdfs:label ?label ;
                wdt:"""+self.wikidata_pid_property_id+""" '"""+pid+"""'.
            }
            LIMIT 1
        """
        self.sparql.setQuery(query)
        self.sparql.setReturnFormat(JSON)
        results = self.sparql.query().convert()
        # for result in results['results']['bindings']:
        #     print(result)
        if (len(results['results']['bindings']) > 0):
            wikibase_pid= results['results']['bindings'][0]['s']['value'].split("/")[-1]
        return wikibase_pid

    def importWikiDataConcept(self,qid):
        arg = qid
        wikidata_item = pywikibot.ItemPage(self.wikidata_repo, arg)
        wikidata_item.get()
        wikibase_item=self.changeItem(wikidata_item, self.wikibase_repo, True)
        return wikibase_item;

    def checkDifferences(self, item_id, change):
        if (item_id and item_id[0] == 'Q'):
            print(f' changed item {item_id} : edit type {change.get("type")}')
            item = pywikibot.ItemPage(self.wikibase_repo, item_id)
            item.get();
            existing_claims = self.getClaim(item.id)
            if u'' + self.wikidata_code_property_id + '' in existing_claims[u'claims']:
                "It has a wikidata qid"
                wikidata_qid = \
                existing_claims[u'claims'][self.wikidata_code_property_id][0].toJSON()['mainsnak']['datavalue']['value']
                wikidata_item = pywikibot.ItemPage(self.wikidata_repo, wikidata_qid)
                wikidata_existing_claims = self.getClaimFromWikidataRepo(wikidata_qid)
                wikidata_property_ids = list(wikidata_existing_claims[u'claims'].toJSON().keys())
                if (len(wikidata_property_ids) < 1):
                    return
                for prop in wikidata_property_ids:
                    wikibase_pid = self.getWikibasePIDbyWikidataPID(prop)
                    if (wikibase_pid is None):  # if one of the property from wikidata is not exist in wikibase, then perform import process
                        try:
                            self.importWikiDataConcept(wikidata_qid)
                        except Exception as e:
                            print(
                                f'ERROR IMPORTING ITEM FROM WIKIDATA : QID : {wikidata_qid}, ERROR_MESSAGE >> {e}')
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            tb = traceback.extract_tb(exc_tb)[-1]
                            print(exc_type, tb[2], tb[1])
                        break
                    if existing_claims[u'claims'].get(wikibase_pid) is not None:
                        print('property exist')
                        # if (existing_claims[u'claims'][wikibase_pid][0].toJSON().get('mainsnak').get(
                        #         'datavalue').get('value') is not None and
                        #         wikidata_existing_claims[u'claims'][prop][0].toJSON().get('mainsnak').get(
                        #             'datavalue').get('value') is not None):
                        #     if existing_claims[u'claims'][wikibase_pid][0].toJSON().get('mainsnak').get(
                        #             'datavalue').get('value') != \
                        #             wikidata_existing_claims[u'claims'][prop][0].toJSON().get('mainsnak').get(
                        #                 'datavalue').get('value'):
                        #         self.importWikiDataConcept(wikidata_qid)
                        #         break
                        # else:
                        #     self.importWikiDataConcept(wikidata_qid)
                    else:
                        try:
                            self.importWikiDataConcept(wikidata_qid)
                        except Exception as e:
                            print(
                                f'ERROR IMPORTING ITEM FROM WIKIDATA : QID : {wikidata_qid}, ERROR_MESSAGE >> {e}')
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            tb = traceback.extract_tb(exc_tb)[-1]
                            print(exc_type, tb[2], tb[1])
            else:
                "ITEM DOES NOT CONTAINS CORRESPONDING WIKIDATA QID"
        elif (item_id and item_id[0] == 'P'):
            print(f' changed property {item_id} : edit type {change.get("type")}')


    from util.util import changeItem, changeProperty, importProperty
    from pywikibot.diff import PatchManager
    # get changes
    def getChanges(self):
        current_time = self.wikibase.server_time()
        # requests=self.wikibase.recentchanges(start=current_time, end=current_time - timedelta(hours=1))
        requests=self.wikibase.recentchanges(start=current_time, end=current_time - timedelta(minutes=240))
        response=requests.request.submit();
        changes=response.get('query')['recentchanges']
        for change in changes:
            try:
                if(change.get('type') == 'new'):
                    item_id=change.get('title').split(':')[-1]
                    self.checkDifferences(item_id,change)
                elif(change.get('type') == 'edit'):
                    item_id = change.get('title').split(':')[-1]
                    self.checkDifferences(item_id, change)
            except Exception as e:
                print(
                    f'ERROR CHECKING DIFFERENCES : ERROR_MESSAGE >> {e}')
                exc_type, exc_obj, exc_tb = sys.exc_info()
                tb = traceback.extract_tb(exc_tb)[-1]
                print(exc_type, tb[2], tb[1])
        return response

def start():
    changes=MonitorChanges()
    try:
        # changes.importWikiDataConcept('Q3031')
        changes.getWikiDataItemtifier()
        changes.getWikiDataPropertyItemtifier()
        while True:
            try:
                res = changes.getChanges()
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                tb = traceback.extract_tb(exc_tb)[-1]
                print(f'ERROR >> {e}')
                print(exc_type, tb[2], tb[1])
            time.sleep(2)
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        tb = traceback.extract_tb(exc_tb)[-1]
        print(f'ERROR >> {e}')
        print(exc_type, tb[2], tb[1])



start()
exit()



