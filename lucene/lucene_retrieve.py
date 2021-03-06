#!/usr/bin/env python

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


def run(searcher, analyzer):
    while True:
        print
        print "Hit enter with no input to quit."
        command = raw_input("Query:")
        if command == '':
            return

        print
        print "Searching for:", command
        query = QueryParser("text", analyzer).parse(command)
        print query
        scoreDocs = searcher.search(query, 5).scoreDocs
        print "%s total matching documents." % len(scoreDocs)

        for scoreDoc in scoreDocs:
            doc = searcher.doc(scoreDoc.doc)
            pmid = doc.get('pmid')
            pmcid = doc.get('pmcid')
            id_ = doc.get('id')
            print(pmid, id_)
            print(fetch_text(pmid, pmcid, id_))

            # sent_id = int(doc.get('sent_id'))
            # json_doc = db.medline.find_one({'docId': pmid}, {'_id': 0})
            # sentence = json_doc['sentence'][sent_id]
            # char_start = sentence['charStart'] if 'charStart' in sentence 
            # else 0
            # char_end = sentence['charEnd'] if 'charEnd' in sentence else 0
            # sent_text = json_doc['text'][char_start:char_end+1]
            # 
            # print doc.get("pmid"), doc.get("sent_id"), doc.get("is_title"),
            #  sent_text


if __name__ == '__main__':
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    print 'lucene', lucene.VERSION
    # base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    index_dir = sys.argv[1]
    directory = SimpleFSDirectory(Paths.get(index_dir))
    index = DirectoryReader.open(directory)
    print 'index has {} documents'.format(index.numDocs())
    searcher = IndexSearcher(index)

    stop_words = CharArraySet(50, True)
    c_analyzer = ClassicAnalyzer(stop_words)
    analyzer = LimitTokenCountAnalyzer(c_analyzer, 1048576)

    run(searcher, analyzer)
    del searcher
