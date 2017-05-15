Mac 
http://stackoverflow.com/questions/30410030/python-install-lxml-on-mac-os-10-10-1
xcode-select -p
xcode-select --install

sudo easy_install lxml


```
Output format: 
{'pmid':'', 
 'pmcid': '', 
 'title': '', 
 'abstract': '', 
 'elements': []
}

Elements can be:
SEC 
{
    'id': id,
    'type': 'SEC',
    'title': title,
    'parent': [],
    'sec_type': '...',
    'xml_sec_type': '...'  # optional
    
}
P 
{
    'id': id,
    'type': 'P',
    'text': text,
    'parent': [],
    'sec_type': '...'
}
FIG
{
    'id': id,
    'fig_id': fig_id,
    'fig_lable': label,
    'type': 'FIG',
    'caption': caption,
    'parent': []
}
TABLE
{
    'id': id,
    'table_id': table_id,
    'table_lable': label,
    'type': 'TBL',
    'caption': caption,
    'parent': []
}
``` 