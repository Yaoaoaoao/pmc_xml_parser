Mac 
http://stackoverflow.com/questions/30410030/python-install-lxml-on-mac-os-10-10-1
xcode-select -p
xcode-select --install

sudo easy_install lxml


### parser.py output format: 
```
{'pmid':'', 
 'pmcid': '', 
 'article_type', '',
 'elements': []
}
```

Every element in 'elements' contains the following fields: 
```
{
    'id': id,
    'type': '...',
    'sec_type': '...',
    'parent': []
}
```
For each element type, it contains additional field: 
```
type == 'ABS'
{
    'id': 0,
    'sec_type': 'abstract'
    'title': '...',
    'text': '...'
}
type == 'SEC' 
{
    'title': title,
    'xml_sec_type': '...'  # optional   
}
type == 'P' 
{
    'text': text,
}
type == 'FIG'
{
    'fig_id': fig_id,
    'fig_lable': label,
    'caption': caption,
}
type == 'TBL'
{
    'table_id': table_id,
    'table_lable': label,
    'caption': caption,
}
``` 

### parse_pmc_xml.py
Parse every "xml.tar.gz" file under one folder. 
Output format: 
```
{
    'id': id,
    'type': '...',
    'sec_type': '...',
    'parent': [],
    'pmid':'', 
    'pmcid': '', 
    'article_type', '',
    'text': '...'   # title + text + caption: add '.' if title is not end with '.!?'
    'title_offset': [0, #]   # optional: if text contains a title
    ... 
}
```

### lucene
