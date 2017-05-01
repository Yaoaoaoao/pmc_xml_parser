import os
import sys
import json
from parser import parse_file

xml_folder = sys.argv[1]

json_file = open('result.json', 'w')
for root, _, files in os.walk(xml_folder):
    for f in files:
        if not f.endswith('.nxml'):
            continue
        path = os.path.join(root, f)
        result = parse_file(path)
        json_file.write(json.dumps(result)+'\n')
json_file.close()
