from __future__ import unicode_literals, print_function
from lxml import etree
import os
import sys
import re
import json
from itertools import chain
from io import BytesIO

SPACE_PATTERN = re.compile(r'[\s][\s]+')


class PMCXMLParser(object):
    def __init__(self, article_tag):
        self.article_tag = article_tag
        self.element_id = 0
        self.result = {'elements': []}

    def run(self, context):
        for event, element in context:
            for child in element:
                if child.tag == self.article_tag('front'):
                    self.parse_front(child)

                if child.tag == self.article_tag('body'):
                    self.parse_body(child)

                if child.tag == self.article_tag('floats-group'):
                    self.parse_floats_group(child)

            # Clear element. See http://stackoverflow.com/questions/12160418.
            element.clear()

        return self.result

    def parse_front(self, root):
        # pmid, pmcid
        for article_id in root.iterfind('.//' + self.article_tag('article-id')):
            attr = article_id.attrib.get('pub-id-type')
            if attr == 'pmid':
                self.result['pmid'] = article_id.text
            if attr == 'pmcid':
                self.result['pmcid'] = article_id.text

        # Article title
        self.result['title'] = root.find(
            './/' + self.article_tag('article-title')).text

        # Abstract format: title + ': " + all p joined by " "
        abstract_list = []
        abstract_root = root.find('.//' + self.article_tag('abstract'))
        for sec in abstract_root.iterfind('.//' + self.article_tag('sec')):
            abstract_list.extend(self.get_title_p_text(sec))

        self.result['abstract'] = ' '.join(abstract_list)

    def parse_body(self, root):
        def dfs(node, path):
            for element in node:
                if element.tag == self.article_tag('p'):
                    self.new_p(self.result['elements'], self.uuid(),
                               self.stringfy_node(element), path)

                if element.tag == self.article_tag('sec'):
                    sec_id = self.uuid()
                    title = element.find('.//' + self.article_tag('title')).text
                    self.new_sec(self.result['elements'], sec_id, title, path)
                    dfs(element, path + [sec_id])

                self.parse_fig(element, path)
                self.parse_table(element, path)

        dfs(root, [])

    def parse_floats_group(self, root):
        self.parse_fig(root, [])
        self.parse_table(root, [])

    def parse_fig(self, root, path):
        # Only parse current level fig
        for fig in root.iterfind('./' + self.article_tag('fig')):
            fig_id = fig.attrib.get('id')

            label_node = fig.find(self.article_tag('label'))
            label = label_node.text if label_node is not None else ''

            caption_node = fig.find(self.article_tag('caption'))
            caption = ' '.join(self.get_title_p_text(caption_node))

            self.result['elements'].append({
                'id': self.uuid(),
                'fig_id': fig_id,
                'fig_lable': label,
                'type': 'FIG',
                'caption': caption,
                'parent': path[:]
            })

    def parse_table(self, root, path):
        # Only parse current level table
        for table in root.iterfind('./' + self.article_tag('table-wrap')):
            table_id = table.attrib.get('id')

            label_node = table.find(self.article_tag('label'))
            label = label_node.text if label_node is not None else ''

            caption_node = table.find(self.article_tag('caption'))
            caption = ' '.join(self.get_title_p_text(caption_node))

            self.result['elements'].append({
                'id': self.uuid(),
                'table_id': table_id,
                'table_lable': label,
                'type': 'TBL',
                'caption': caption,
                'parent': path[:]
            })

    def new_sec(self, rst, id, title, path):
        rst.append({
            'id': id,
            'type': 'SEC',
            'title': title,
            'parent': path[:]
        })

    def new_p(self, rst, id, text, path):
        rst.append({
            'id': id,
            'type': 'P',
            'text': text,
            'parent': path[:]
        })

    def get_title_p_text(self, root):
        """ Return a list of text. """
        text = []
        title_node = root.find(self.article_tag('title'))
        if title_node is not None:
            title_text = title_node.text
            # if not title_text.endswith(':'):
            #     title_text += ':'
            text.append(title_text)

        for p in root.findall('.//' + self.article_tag('p')):
            text.append(self.stringfy_node(p))

        return text

    def stringfy_node(self, node):
        parts = [node.text] + list(
            chain(*([c.text, c.tail] for c in
                    node.getchildren())))  # + [node.tail]
        # filter removes possible Nones in texts and tails
        return ''.join(filter(None, parts))

    def uuid(self):
        self.element_id += 1
        return self.element_id


def make_tag_ns(ns):
    def get_tag(tag):
        return '{' + ns + '}' + tag

    return get_tag


def parse_file(xml_file):
    article_ns = None
    with open(xml_file) as f:
        context = etree.iterparse(f, events=('start',))
        for event, element in context:
            if etree.QName((element.tag)).localname == 'article':
                article_ns = element.nsmap.get(None)
                break

    assert article_ns is not None
    article_tag = make_tag_ns(article_ns)

    with open(xml_file) as f:
        context = etree.iterparse(f, events=('end',),
                                  tag=(article_tag('article'),))
        parser = PMCXMLParser(article_tag)
        result = parser.run(context)
        return result


def parse_string(xml_string):
    # Must be of type str.
    assert type(xml_string) is str, type(xml_string)

    article_ns = None
    context = etree.iterparse(BytesIO(xml_string), events=('start',))
    for event, element in context:
        if etree.QName((element.tag)).localname == 'article':
            article_ns = element.nsmap.get(None)
            break

    assert article_ns is not None
    article_tag = make_tag_ns(article_ns)
    context = etree.iterparse(BytesIO(xml_string), events=('end',),
                              tag=(article_tag('article'),))
    parser = PMCXMLParser(article_tag)
    result = parser.run(context)
    return result


if __name__ == '__main__':
    xml_file = sys.argv[1]
    result = parse_file(xml_file)
    # print(result)
    for i in result['elements']:
        print(i)
        # print(json.dumps(result, indent=2, separators=(',', ': ')))
