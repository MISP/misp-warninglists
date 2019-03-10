#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7'
r = requests.get(url)
service_list = r.json()
l = []
for service in service_list:
    for url in service.get('urls', []):
        l.append(url.replace('*', ''))
    for ip in service.get('ips', []):
        l.append(ip)

warninglist = {}
warninglist['name'] = 'List of known Office 365 URLs and IP address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Office 365 URLs and IP address ranges'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip", "hostname"]

with open('../lists/microsoft-office365/list.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)
