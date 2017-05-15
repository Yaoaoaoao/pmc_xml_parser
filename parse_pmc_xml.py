import os
import sys
import json
from parser import parse_file, parse_string
import traceback
import tarfile

xml_folder = sys.argv[1]

json_file = open('result.json', 'w')


def pmc(pmid, pmcid, article_type):
    def write_ele(ele):
        ele['pmid'] = pmid
        ele['pmcid'] = pmcid
        ele['article_type'] = article_type
        json_file.write(json.dumps(ele) + '\n')

    return write_ele


for root, _, files in os.walk(xml_folder):
    for f in files:
        if not f.endswith('.xml.tar.gz'):
            continue

        print(f)

        path = os.path.join(root, f)
        with tarfile.open(path, 'r:gz') as tar:
            for member in tar:

                if member.isreg():
                    f = tar.extractfile(member)
                    content = f.read()
                    try:
                        result = parse_string(content)
                        write_ele = pmc(result['pmid'], result['pmcid'],
                                        result['article_type'])

                        if result['abstract'] != '':
                            write_ele({
                                'title': result['title'],
                                'text': result['abstract']
                            })

                        for ele in result['elements']:
                            if ele['type'] == 'SEC' and ele['title'] != '':
                                write_ele(ele)
                            elif ele['type'] == 'P' and ele['text'] != '':
                                write_ele(ele)
                            elif ele['type'] == 'FIG' and ele['caption'] != '':
                                write_ele(ele)
                            elif ele['type'] == 'TBL' and ele['caption'] != '':
                                write_ele(ele)

                    except:
                        traceback.print_exc()

json_file.close()
