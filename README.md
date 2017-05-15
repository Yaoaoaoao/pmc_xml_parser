Mac 
http://stackoverflow.com/questions/30410030/python-install-lxml-on-mac-os-10-10-1
xcode-select -p
xcode-select --install

sudo easy_install lxml


Output format: 
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