#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import zipfile
import datetime
import json

alexa_url = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
alexa_file = "top-1m.csv.zip"
user_agent = {"User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
r = requests.get(alexa_url, headers=user_agent)
with open(alexa_file, 'wb') as fd:
    for chunk in r.iter_content(4096):
        fd.write(chunk)
with zipfile.ZipFile(alexa_file, 'r') as alexa_lists:
    for name in alexa_lists.namelist():
        if name == "top-1m.csv":
            with alexa_lists.open(name) as top:
                top1000 = top.readlines()[:1000]
        else:
            continue

alexa_warninglist = {}
version = int(datetime.date.today().strftime('%Y%m%d'))

alexa_warninglist['description'] = "Event contains one or more entries from the top 1000 of the most used website (Alexa)."
d = datetime.datetime.now()
alexa_warninglist['version'] = version
alexa_warninglist['name'] = "Top 1000 website from Alexa"
alexa_warninglist['type'] = 'hostname'
alexa_warninglist['list'] = []
alexa_warninglist['matching_attributes'] = ['hostname', 'domain']

for site in top1000:
    v = str(site).split(',')[1]
    alexa_warninglist['list'].append(v.rstrip())
alexa_warninglist['list'] = sorted(set(alexa_warninglist['list']))
print(json.dumps(alexa_warninglist))
