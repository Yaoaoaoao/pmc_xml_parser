#!/usr/bin/env python
from __future__ import print_function
import sys, os, lucene
from pmc_mongo import *

from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.analysis.standard import ClassicAnalyzer
from org.apache.lucene.analysis import CharArraySet

"""
This script is loosely based on the Lucene (java implementation) demo class
org.apache.lucene.demo.SearchFiles.  It will prompt for a search query, then it
will search the Lucene index in the current directory called 'index' for the
search query entered against the 'contents' field.  It will then display the
'path' and 'name' fields for each of the hits it finds in the index.  Note that
search.close() is currently commented out because it causes a stack overflow in
some cases.
"""


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print('lucene', lucene.VERSION)

    index_dir = '/data/Applications/pmc/pmc_xml_parser/index'
    directory = SimpleFSDirectory(Paths.get(index_dir))
    index = DirectoryReader.open(directory)
    print('index has {} documents'.format(index.numDocs()))

    searcher = IndexSearcher(index)
    stop_words = CharArraySet(50, True)
    c_analyzer = ClassicAnalyzer(stop_words)
    analyzer = LimitTokenCountAnalyzer(c_analyzer, 1048576)

    # RLIMS-P phosphorylation.
    #command = 'phosphorylat* OR autophosphorylat* OR auto-phosphorylat* OR transphosphorylat* OR trans-phosphorylat* OR cis-phosphorylat* OR phosphoserine OR phosphoserines OR phospho-serine OR phospho-serines OR phosphotyrosine OR phosphotyrosines OR phospho-tyrosine OR phospho-tyrosines OR phosphothreonine OR phosphothreonines OR phospho-threonine OR phospho-threonines OR phosphopeptide OR phosphopeptides OR phospho-peptide OR phospho-peptides'
    # miRTex
    command = 'miRNA OR miR OR microRNA'
    query = QueryParser("text", analyzer).parse(command)
    print(query)
    total_hits = searcher.search(query, 1).totalHits
    print("{} total matching documents.".format(total_hits))
    scoreDocs = searcher.search(query, total_hits).scoreDocs
    
    for scoreDoc in scoreDocs:
        doc = searcher.doc(scoreDoc.doc)
        pmid = doc.get('pmid')
        pmcid = doc.get('pmcid')
        id_ = doc.get('id')
        print(pmid, id_)
        print(fetch_text(pmid, pmcid, id_))
        break

    del searcher
