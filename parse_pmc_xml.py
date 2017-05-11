import os
import sys
import json
from parser import parse_file, parse_string
import traceback
import tarfile

xml_folder = sys.argv[1]

json_file = open('result.json', 'w')

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
                        json_file.write(json.dumps(result)+'\n')
                    except:
                        traceback.print_exc()

json_file.close()
