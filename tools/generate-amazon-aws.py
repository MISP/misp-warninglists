#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import urllib.request
import json

res = urllib.request.urlopen('https://ip-ranges.amazonaws.com/ip-ranges.json')

res_body = res.read()
j = json.loads(res_body.decode("utf-8"))
l = []

for prefix in j['prefixes']:
   l.append(prefix['ip_prefix'])


for prefix in j['ipv6_prefixes']:
   prefix['ipv6_prefix']
   
warninglist = {}
warninglist['name'] = 'List of known Amazon AWS IP address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Amazon AWS IP address ranges (https://ip-ranges.amazonaws.com/ip-ranges.json)'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]


print(json.dumps(warninglist))
