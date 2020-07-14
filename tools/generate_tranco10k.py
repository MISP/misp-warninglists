#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import zipfile
import datetime
import json

tranco_url = 'https://tranco-list.eu/top-1m.csv.zip'
tranco_file = 'top-1m.csv.zip'
user_agent = {'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0'}
r = requests.get(tranco_url, headers=user_agent)
with open(tranco_file, 'wb') as fd:
    for chunk in r.iter_content(4096):
        fd.write(chunk)
with zipfile.ZipFile(tranco_file, 'r') as tranco_lists:
    for name in tranco_lists.namelist():
        if name == 'top-1m.csv':
            with tranco_lists.open(name) as tranco:
                sites = tranco.readlines()[:10000]
        else:
            continue

tranco_warninglist = {}
version = int(datetime.date.today().strftime('%Y%m%d'))

tranco_warninglist['description'] = "Event contains one or more entries from the top 10K most-used sites (Tranco)."
d = datetime.datetime.now()
tranco_warninglist['version'] = version
tranco_warninglist['name'] = "Top 10K most-used sites from Tranco"
tranco_warninglist['type'] = 'hostname'
tranco_warninglist['list'] = []
tranco_warninglist['matching_attributes'] = ['hostname', 'domain', 'url', 'domain|ip']

for site in sites:
    v = site.decode('UTF-8').split(',')[1]
    tranco_warninglist['list'].append(v.rstrip())
tranco_warninglist['list'] = sorted(set(tranco_warninglist['list']))
print(json.dumps(tranco_warninglist))
