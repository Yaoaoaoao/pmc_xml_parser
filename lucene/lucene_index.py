from __future__ import unicode_literals, print_function
import sys
import json
import codecs
import glog
from tqdm import tqdm

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.standard import ClassicAnalyzer
from org.apache.lucene.document import Document, Field, FieldType, IntPoint, \
    StoredField, StringField, SortedDocValuesField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions
from org.apache.lucene.index import Term
from org.apache.lucene.search import TermQuery, BooleanQuery, BooleanClause
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version, BytesRef
from org.apache.lucene.analysis import CharArraySet

if __name__ == '__main__':
    # http://svn.apache.org/viewvc/lucene/pylucene/trunk/samples/IndexFiles
    # .py?view=markup
    json_file = sys.argv[1]
    index_folder = sys.argv[2]

    glog.setLevel(glog.INFO)
    lucene.initVM()
    store = SimpleFSDirectory(Paths.get(index_folder))
    stop_words = CharArraySet(50, True)
    c_analyzer = ClassicAnalyzer(stop_words)
    analyzer = LimitTokenCountAnalyzer(c_analyzer, 1048576)
    config = IndexWriterConfig(analyzer)
    config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
    writer = IndexWriter(store, config)

    print('%d docs in index' % writer.numDocs())
    print('Indexing json files...')

    # For text field.
    t1 = FieldType()
    t1.setStored(False)
    t1.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)

    with codecs.open(json_file, encoding='utf8') as f:
        for line in tqdm(f):
            line = line.strip()
            try:
                json_doc = json.loads(line)
            except:
                glog.warning('Error json parsing: {}'.format(line))
                continue

            # Delete existing abstracts. This is useful when adding
            # update files from Medline.
            try:
                assert 'pmid' in json_doc
                pmid_query = TermQuery(Term('pmid', json_doc['pmid']))
                id_query = IntPoint.newRangeQuery("id", json_doc['id'],
                                                  json_doc['id'])
                bq = BooleanQuery.Builder()
                bq.add(pmid_query, BooleanClause.Occur.MUST)
                bq.add(id_query, BooleanClause.Occur.MUST)
                q = bq.build()
                writer.deleteDocuments(q)

                # Add whole abstract.
                doc = Document()
                # Store field.
                doc.add(IntPoint('id', json_doc['id']))  # index
                doc.add(StoredField('id', json_doc['id']))  # store
                doc.add(StringField('pmid', json_doc['pmid'], Field.Store.YES))
                doc.add(StringField('pmcid', json_doc['pmcid'], Field.Store.YES))
                # Index only.
                doc.add(StringField('article_type', json_doc['article_type'],
                                    Field.Store.NO))
                doc.add(StringField('type', json_doc['type'], Field.Store.NO))
                doc.add(StringField('sec_type', json_doc['sec_type'],
                                    Field.Store.NO))
                doc.add(Field('text', json_doc['text'], t1))

                writer.addDocument(doc)
            except:
                print(json_doc)

                # for sentence in json_doc['sentence']:
                #     char_start, char_end = -1, -1
                #     if 'charStart' not in sentence:
                #         char_start = 0
                #     else:
                #         char_start = sentence['charStart']
                # 
                #     if 'charEnd' not in sentence:
                #         glog.info('No char end: {}'.format(line))
                #         continue
                # 
                #     char_end = sentence['charEnd']
                # 
                #     assert char_start >=0
                #     assert char_end >=0
                #     assert char_end >= char_start
                # 
                #     sent_text = json_doc['text'][char_start:char_end+1]
                #     sent_id = sentence['index'] if 'index' in sentence else 0
                #     is_title = 'T' if sent_id == 0 else 'F'
                # 
                #     doc = Document()
                # 
                #     # See lucene_web.py for detailed usage of following 
                # fields.
                #     # pmid is used for searching and grouping.
                #     doc.add(StringField('pmid', json_doc['docId'], 
                # Field.Store.YES))
                #     doc.add(SortedDocValuesField('pmid', BytesRef(json_doc[
                # 'docId'])))
                # 
                #     # sent id is not used for searching.
                #     doc.add(StoredField('sent_id', sent_id))
                # 
                #     # title is used for grouping/filtering.
                #     doc.add(StoredField('is_title', is_title))
                #     if is_title == 'T':
                #         doc.add(SortedDocValuesField('is_title', BytesRef(
                # is_title)))
                #     # Add text
                #     doc.add(Field('sent_text', sent_text, t1))
                #     writer.addDocument(doc)

    print('Closing index of %d docs...' % writer.numDocs())
    writer.close()
