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
from util.PropertyWikidataIdentifier import PropertyWikidataIdentifier
import import_one_v2
from util import get_wikibase_changes
from pywikibot.diff import PatchManager
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


    wikidata_code_property_id = None
    wikidata_pid_property_id = None

    def getWikiDataItemtifier(self):
        identifier = PropertyWikidataIdentifier()
        identifier.get(self.wikibase_repo)
        self.wikidata_code_property_id=identifier.itemIdentifier
        self.wikidata_pid_property_id = identifier.propertyIdentifier


    def checkDifferences(self, item_id, change):
        if (item_id and item_id[0] == 'Q'):
            print(f' changed item {item_id} : edit type {change.get("type")}')
            item = pywikibot.ItemPage(self.wikibase_repo, item_id)
            item.get();

            existing_claims = self.getClaim(item.id)
            if (u'' + self.wikidata_code_property_id + '' in existing_claims[u'claims'] and len(
                    list(existing_claims.get('claims'))) > 1):
                rev_text = []
                for x in item.revisions(total=3, content=True):
                    rev_text.append(x.text)
                self.PatchManager(rev_text[0], rev_text[1]).print_hunks() # print the diff

                # RECENT REVISION CONTAINS WIKIDATAQID PROPERTY AND PREVIOUS REVISION DOES NOT CONTAINS THAT PROPERTY
                if (json.loads(rev_text[0]).get('claims').get(self.wikidata_code_property_id, None) is not None and json.loads(rev_text[1]).get(
                        'claims').get(self.wikidata_code_property_id, None) is None):
                    wikidata_qid = existing_claims[u'claims'][self.wikidata_code_property_id][0].toJSON()['mainsnak']['datavalue']['value']
                    "CALL IMPORT_ONE: I HAVE CREATED A METHOD 'run' INSIDE IMPORT_ONE"
                    import_one_v2.run(wikidata_qid)
                else:
                    return


    # get changes
    def getChanges(self):
        current_time = self.wikibase.server_time()
        requests=self.wikibase.recentchanges(start=current_time, end=current_time - timedelta(minutes=20))
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
        return changes

def start():
    changes=MonitorChanges()
    changes.getWikiDataItemtifier();
    while True:
        try:
            res = changes.getChanges()
            print(res)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            tb = traceback.extract_tb(exc_tb)[-1]
            print(f'ERROR >> {e}')
            print(exc_type, tb[2], tb[1])
        print('Wikiwata QID Change Monitor sleeps for 180s')
        time.sleep(180)

# start()

exit()



