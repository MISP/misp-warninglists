#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'
r = requests.get(url)
tlds = []
for tld in r.text.splitlines():
    if tld.startswith('#'):
        continue
    tlds.append(tld)

warninglist = {
    'name': 'TLDs as known by IANA',
    'version': int(datetime.date.today().strftime('%Y%m%d')),
    'description': 'Event contains one or more TLDs as attribute with an IDS flag set',
    'list': sorted(set(tlds)),
    'matching_attributes': ["hostname", "domain", "domain|ip"],
    'type': 'string',
}

with open('../lists/tlds/list.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=2, sort_keys=True)
    data_file.write("\n")
