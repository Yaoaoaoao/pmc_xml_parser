from __future__ import unicode_literals, print_function
from lxml import etree
import sys
from itertools import chain
from io import BytesIO


class PMCXMLParser(object):
    def __init__(self, article_tag, article_type):
        self.article_tag = article_tag
        self.element_id = 0
        self.result = {'pmid': '', 'pmcid': '', 'article_type': article_type,
                       'elements': []}

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
            if attr == 'pmc' or attr == 'pmc-uid':
                self.result['pmcid'] = 'PMC' + article_id.text

        # Article title
        title_ele = root.find('.//' + self.article_tag('article-title'))
        title = self.get_title_text(title_ele)

        # Abstract format: title + ': " + all p joined by " "
        abstract_list = []
        abstract_root = root.find('.//' + self.article_tag('abstract'))
        abstract = ''
        if abstract_root is not None:
            for sec in abstract_root.iterfind('.//' + self.article_tag('sec')):
                abstract_list.extend(self.get_title_p_text(sec, abstract=True))
            abstract = ' '.join(abstract_list)

        addition = {
            'title': title,
            'text': abstract
        }
        self.new_element(0, 'ABS', 'abstract', [], addition)

    def parse_body(self, root):
        def dfs(node, path, parent_sec_type):
            for element in node:
                if element.tag == self.article_tag('p'):
                    self.parse_p(element, parent_sec_type, path)

                if element.tag == self.article_tag('sec'):
                    sec_id = self.uuid()
                    title_ele = element.find('.//' + self.article_tag('title'))
                    title = self.get_title_text(title_ele)

                    # Decide sec type
                    xml_sec_type = element.attrib.get('sec-type')
                    sec_type = self.assign_sec_type(parent_sec_type,
                                                    xml_sec_type, title)

                    self.new_sec(sec_id, title, path, xml_sec_type, sec_type)
                    dfs(element, path + [sec_id], sec_type)

                self.parse_fig(element, path, parent_sec_type)
                self.parse_table(element, path, parent_sec_type)

        dfs(root, [], 'other')

    def parse_floats_group(self, root):
        self.parse_fig(root, [], 'other')
        self.parse_table(root, [], 'other')

    def new_element(self, id, ele_type, sec_type, path, addition):
        element = {
            'id': id,
            'type': ele_type,
            'sec_type': sec_type,
            'parent': path[:]
        }
        element.update(addition)
        self.result['elements'].append(element)
        
    def new_sec(self, id, title, path, xml_sec_type, sec_type):
        addition = {'title': title}
        if xml_sec_type is not None:
            addition['xml_sec_type'] = xml_sec_type
        self.new_element(id, 'SEC', sec_type, path, addition)

    def parse_p(self, p_ele, sec_type, path):
        text = self.stringfy_node(p_ele)
        self.new_element(self.uuid(), 'P', sec_type, path, {'text': text})

    def parse_fig(self, root, path, sec_type):
        # Only parse current level fig
        for fig in root.iterfind('./' + self.article_tag('fig')):
            fig_id = fig.attrib.get('id')

            label_node = fig.find(self.article_tag('label'))
            label = label_node.text if label_node is not None else ''

            caption_node = fig.find(self.article_tag('caption'))
            caption = ''
            if caption_node is not None:
                caption = ' '.join(self.get_title_p_text(caption_node))

            addition = {
                'fig_id': fig_id,
                'fig_lable': label,
                'caption': caption
            }
            self.new_element(self.uuid(), 'FIG', sec_type, path, addition)

    def parse_table(self, root, path, sec_type):
        # Only parse current level table
        for table in root.iterfind('./' + self.article_tag('table-wrap')):
            table_id = table.attrib.get('id')

            label_node = table.find(self.article_tag('label'))
            label = label_node.text if label_node is not None else ''

            caption_node = table.find(self.article_tag('caption'))
            caption = ''
            if caption_node is not None:
                caption = ' '.join(self.get_title_p_text(caption_node))

            addition = {
                'table_id': table_id,
                'table_lable': label,
                'caption': caption
            }
            self.new_element(self.uuid(), 'TBL', sec_type, path, addition)

    def get_title_text(self, ele):
         return self.stringfy_node(ele) if ele is not None else ''

    def get_title_p_text(self, root, abstract=False):
        """ 
            If abstract = True, check and add a colon after title. 
            Return a list of text. 
        """
        text = []
        title_ele = root.find(self.article_tag('title'))
        title = self.get_title_text(title_ele)
        if title != '':
            if abstract and not title.endswith(':'):
                title += ':'
            text.append(title)

        for p in root.findall('.//' + self.article_tag('p')):
            text.append(self.stringfy_node(p))

        return text

    def assign_sec_type(self, parent_sec_type, xml_sec_type, title_text):
        if xml_sec_type is None:
            xml_sec_type = ''

        if 'supplementary-material' in xml_sec_type:
            sec_type = 'other'
        elif 'material' in xml_sec_type:
            sec_type = 'methods'
        elif 'method' in xml_sec_type:
            sec_type = 'methods'
        elif 'display-objects' in xml_sec_type:
            sec_type = 'other'
        elif 'result' in xml_sec_type:
            sec_type = 'results'
        elif 'discussion' in xml_sec_type:
            sec_type = 'discussion'
        elif 'intro' in xml_sec_type:
            sec_type = 'introduction'
        else:
            if parent_sec_type is not None and \
                    parent_sec_type != '' and parent_sec_type != 'other':
                sec_type = parent_sec_type
            else:
                title_text = title_text.lower() if title_text else ''
                if 'background' in title_text:
                    sec_type = 'background'
                elif 'introduction' in title_text:
                    sec_type = 'introduction'
                elif 'method' in title_text:
                    sec_type = 'methods'
                elif 'material' in title_text:
                    sec_type = 'materials'
                elif 'result' in title_text:
                    sec_type = 'results'
                elif 'discussion' in title_text:
                    sec_type = 'discussion'
                elif 'conclusion' in title_text:
                    sec_type = 'conclusion'
                elif 'appendix' in title_text:
                    sec_type = 'appendix'
                else:
                    sec_type = 'other'

        return sec_type

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
        if len(ns) > 0:
            return '{' + ns + '}' + tag
        return tag

    return get_tag


def parse_article(handle):
    article = {'type': None, 'ns': None}
    context = etree.iterparse(handle, events=('start',))
    for event, element in context:
        if 'article-type' in element.attrib:
            article['type'] = element.attrib.get('article-type')
        if etree.QName((element.tag)).localname == 'article':
            article['ns'] = element.nsmap.get(None, '')
            break
    return article


def parse_xml(article, handle):
    article_tag = make_tag_ns(article['ns'])
    context = etree.iterparse(handle, events=('end',),
                              tag=(article_tag('article'),))
    parser = PMCXMLParser(article_tag, article['type'])
    result = parser.run(context)
    return result


def parse_file(xml_file):
    with open(xml_file) as f:
        article = parse_article(f)

    assert article['ns'] is not None, xml_file

    with open(xml_file) as f:
        return parse_xml(article, f)


def parse_string(xml_string):
    # Must be of type str.
    assert type(xml_string) is str, type(xml_string)

    article = parse_article(BytesIO(xml_string))

    assert article['ns'] is not None
    return parse_xml(article, BytesIO(xml_string))


if __name__ == '__main__':
    xml_file = sys.argv[1]
    result = parse_file(xml_file)
    print(result)
    # for i in result['elements']:
    #     print(i)
