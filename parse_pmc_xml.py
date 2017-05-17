import os
import sys
import json
from parser import parse_file, parse_string
import traceback
import tarfile


def texify(pmid, pmcid, article_type, ele):
    """
    Merge all element title/text/caption into "text" field. So the entity offset
    is based on the "text" field. For title, keep an extra title_offset 
    attribute of the start and end (inclusive) position.
    """
    ele['pmid'] = pmid
    ele['pmcid'] = pmcid
    ele['article_type'] = article_type

    text = []
    if 'title' in ele:
        # title ends with either .?!
        title = ele['title']
        if not title.endswith(('.', '!', '?')):
            title += '.'
        text.append(title)
        del ele['title']
        ele['title_offset'] = [0, len(title) - 1]
    if 'text' in ele:
        text.append(ele['text'])
        del ele['text']
    if 'caption' in ele:
        text.append(ele['caption'])
        del ele['caption']

    ele['text'] = ' '.join(text)


def extract_from_tar(path, json_file):
    with tarfile.open(path, 'r:gz') as tar:
        for member in tar:
            if not member.isreg():
                continue

            f = tar.extractfile(member)
            content = f.read()
            try:
                result = parse_string(content)
                for ele in result['elements']:
                    texify(result['pmid'], result['pmcid'],
                           result['article_type'], ele)
                    json_file.write(json.dumps(ele) + '\n')

            except:
                traceback.print_exc()


if __name__ == '__main__':
    xml_folder = sys.argv[1]
    json_file = open('result.json', 'w')

    for root, _, files in os.walk(xml_folder):
        for f in files:
            if not f.endswith('.xml.tar.gz'):
                continue

            print(f)
            path = os.path.join(root, f)
            extract_from_tar(path, json_file)

    json_file.close()
