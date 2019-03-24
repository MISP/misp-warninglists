#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://raw.githubusercontent.com/martenson/disposable-email-domains/master/disposable_email_blocklist.conf'
r = requests.get(url, stream=True)
domain = []
for ip in r.iter_lines():
    v = ip.decode('utf-8')
    if not v.startswith("#"):
        if v: domain.append(v)

warninglist = {}
warninglist['name'] = 'List of disposable email domains'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'List of disposable email domains'
warninglist['list'] = sorted(set(domain))
warninglist['type'] = 'substring'
warninglist['matching_attributes'] = ["email-src", "email-dst", "whois-registrant-email", "domain|ip", "dns-soa-email"] 

with open('../lists/disposable-email/lists.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)


