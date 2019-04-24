#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import zipfile
import datetime
import json

cisco_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
cisco_file = "top-1m.csv.zip"
user_agent = {"User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
r = requests.get(cisco_url, headers=user_agent)
with open(cisco_file, 'wb') as fd:
    for chunk in r.iter_content(4096):
        fd.write(chunk)
with zipfile.ZipFile(cisco_file, 'r') as cisco_lists:
    for name in cisco_lists.namelist():
        if name == "top-1m.csv":
            with cisco_lists.open(name) as top:
                top1000 = top.readlines()[:1000]
        else:
            continue

cisco_warninglist = {}
version = int(datetime.date.today().strftime('%Y%m%d'))

cisco_warninglist['description'] = 'Event contains one or more entries from the top 1000 of the most used website (Cisco Umbrella).'
d = datetime.datetime.now()
cisco_warninglist['version'] = version
cisco_warninglist['name'] = 'Top 1000 website from Cisco Umbrella'
cisco_warninglist['type'] = 'hostname'
cisco_warninglist['matching_attributes'] = ['hostname', 'domain']
cisco_warninglist['list'] = []


for site in top1000:
    v = str(site).split(',')[1]
    cisco_warninglist['list'].append(v.rstrip())
cisco_warninglist['list'] = sorted(set(cisco_warninglist['list']))
print(json.dumps(cisco_warninglist))
