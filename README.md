Mac 
http://stackoverflow.com/questions/30410030/python-install-lxml-on-mac-os-10-10-1
xcode-select -p
xcode-select --install

sudo easy_install lxml

pip install shortuuid

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
    'parent': []
}
P 
{
    'id': id,
    'type': 'P',
    'text': text,
    'parent': []
}
FIG
{
    'id': self.uuid(),
    'fig_id': fig_id,
    'fig_lable': label,
    'type': 'FIG',
    'caption': caption,
    'parent': []
}
TABLE
{
    'id': self.uuid(),
    'table_id': table_id,
    'table_lable': label,
    'type': 'TBL',
    'caption': caption,
    'parent': []
}
``` 