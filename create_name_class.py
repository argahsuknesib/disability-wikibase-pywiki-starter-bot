# coding=utf-8

import configparser
import csv
import sys
import traceback
import time
import pywikibot
from SPARQLWrapper import SPARQLWrapper, JSON

config = configparser.ConfigParser()
config.read('config/application.config.ini')

wikibase = pywikibot.Site("my", "my")


class Create_item:
    def __init__(self, wikibase):
        self.wikibase = wikibase
        self.wikibase_repo = wikibase.data_repository()
        self.sparql = SPARQLWrapper(config.get('wikibase', 'sparqlEndPoint'))

    def create_class_entity(self):
        dis_wiki_class = pywikibot.ItemPage(self.wikibase_repo)
        dis_wiki_data = {'labels': {'en': 'Disability rights wiki', 'fr': 'Disability rights wiki'},
                         'descriptions': {'en': 'Free knowledge graph project by York university , University Jean Monnet and QA Company',
                                          'fr': "Projet gratuit de graphe de connaissances par l'université de York, l'université Jean Monnet et QA Company"},
                         'aliases': {
            'en': ['Diswiki', 'disability wiki', 'wiki disability', 'wiki rights', 'disability wiki rights', 'diswikidata'],
            'fr': ['Diswiki', 'disability wiki', 'wiki disability', 'wiki rights', 'disability wiki rights', 'diswikidata']}}
        dis_wiki_class.editEntity(dis_wiki_data, summary='Edit document')
        
        # UNCOMMENT REQUIRED ENTITY CREATION IF NOT ALREADY CREATED##############
        
        document_class = pywikibot.ItemPage(self.wikibase_repo)
        doc_data = {'labels': {'en': 'Document', 'fr': 'Document'},
                    'descriptions': {'en': 'preserved information', 'fr': "porteur d'information qui contient l'écriture"},
                    'aliases': {'en': ['doc', 'record', 'documents', 'docs', 'records'], 'fr': ["pièce d'archives", "documents", "pièces d'archives"]}}
        document_class.editEntity(doc_data, summary='Edit document')

        crpd_class = pywikibot.ItemPage(self.wikibase_repo)
        crpd_data = {'labels': {'en': 'Crpd', 'fr': 'Crpd'},
                     'descriptions': {'en': 'Convention on the Rights of Persons with Disabilities', 'fr': "Convention sur les droits des personnes handicapées"},
                     'aliases': {'en': ['doc', 'crpd', 'crpd document'], 'fr': ["crpd"]}}
        crpd_class.editEntity(crpd_data, summary='Edit crpd')

        web_content_class = pywikibot.ItemPage(self.wikibase_repo)
        web_content_data = {'labels': {'en': 'Web content', 'fr': 'Contenu du web'},
                            'descriptions': {'en': 'Content from web resource', 'fr': "Contenu d'une ressource web"},
                            'aliases': {'en': ['blog', 'website', 'blog post', 'online resource'], 'fr': ["blog", "site web"]}}
        web_content_class.editEntity(
            web_content_data, summary='Edit web content')

        topic_class = pywikibot.ItemPage(self.wikibase_repo)
        topic_data = {'labels': {'en': 'Topic', 'fr': 'Thème'},
                      'descriptions': {'en': 'in linguistics, the known information in a phrase', 'fr': "l'information connue dans une phrase"},
                      'aliases': {'en': ['Subject', 'Topics', 'topic', 'tags', 'tag', 'theeme', 'sub topic', 'sub topics'],
                                  'fr': ["tags", "tag", "sub topic"]}}
        topic_class.editEntity(topic_data, summary='Edit topic')

        paragraph_class = pywikibot.ItemPage(self.wikibase_repo)
        paragraph_data = {'labels': {'en': 'Paragraph', 'fr': 'Paragraphe'},
                          'descriptions': {'en': 'portion of text composed of one or more sentences', 'fr': "partie dans le texte est composé d'un ou plusieurs jeux"},
                          'aliases': {'en': ['subsection', 'part of document', 'text of document', 'document text']}}
        paragraph_class.editEntity(paragraph_data, summary='Edit paragraph')

        wikidata_class = pywikibot.ItemPage(self.wikibase_repo)
        wikidata_data = {'labels': {'en': 'Wikidata', 'fr': 'Wikidata'},
                         'descriptions': {'en': 'free knowledge database project hosted by the Wikimedia Foundation and edited by volunteers',
                                          'fr': "projet de base de données éditée de manière collaborative"},
                         'aliases': {
            'en': ['WD', 'wikidata.org', 'www.wikidata.org', 'wikidatawiki', 'd:'],
            'fr': ['WD', 'wikidata.org', 'www.wikidata.org', 'wikidatawiki', 'd:']}}
        wikidata_class.editEntity(wikidata_data, summary='Edit document')

        instance_of_property_data = {'labels': {'en': 'instance of', 'fr': "nature de l'élément"},
                                     'descriptions': {
            'en': 'relation of type constraints',
            'fr': "relation de contrainte de type"},
            'aliases': {
            'en': ['is a', 'is an', 'is a particular', 'has type',
                                    'is an individual', 'is a unique', 'member of', 'has class'],
            'fr': ['instance de', 'is a']}}
        instance_of_property = pywikibot.PropertyPage(
            self.wikibase_repo, datatype='wikibase-item')
        instance_of_property.editEntity(instance_of_property_data)

        document_reference_uri_data = {'labels': {'en': 'document reference link', 'fr': "document link"},
                                       'descriptions': {
            'en': 'uri of the full document',
            'fr': "uri du document complet"},
            'aliases': {
            'en': ['document link', 'web content link', 'blog url']}}
        document_reference_uri_propert = pywikibot.PropertyPage(
            self.wikibase_repo, datatype='url')
        document_reference_uri_propert.editEntity(document_reference_uri_data)

        has_paragraph_property_data = {'labels': {'en': 'has paragraph', 'fr': "a un paragraphe"},
                                       'descriptions': {'en': 'paragraph of the document', 'fr': "paragraphe du document"},
                                       'aliases': {'en': ['document content', 'part of document'],
                                                   'fr': ['contenu du document', 'partie du document']}}
        has_paragraph_property = pywikibot.PropertyPage(
            self.wikibase_repo, datatype='wikibase-item')
        has_paragraph_property.editEntity(has_paragraph_property_data)

        part_of_document_property_data = {'labels': {'en': 'part of', 'fr': "partie de"},
                                          'descriptions': {
            'en': 'source document of the paragraph',
            'fr': "document source du paragraphe"},
            'aliases': {
            'en': ['paragraph from'],
            'fr': ['paragraphe de']}}
        part_of_document_property = pywikibot.PropertyPage(
            self.wikibase_repo, datatype='wikibase-item')
        part_of_document_property.editEntity(part_of_document_property_data)


def start():
    create_item = Create_item(wikibase)
    create_item.create_class_entity()


start()
exit()
