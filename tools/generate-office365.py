#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7'
r = requests.get(url)
service_list = r.json()
lurls= []
lips = []

for service in service_list:
    for url in service.get('urls', []):
        lurls.append(url.replace('*', ''))
    for ip in service.get('ips', []):
        lips.append(ip)

warninglist = {}
warninglist['name'] = 'List of known Office 365 URLs address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Office 365 URLs and IP address ranges'
warninglist['type'] = 'string'
warninglist['list'] = sorted(set(lurls))
warninglist['matching_attributes'] = ["domain", "domain|ip", "hostname"]


with open('../lists/microsoft-office365/list.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)

warninglist = {}
warninglist['name'] = 'List of known Office 365 IP address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Office 365 URLs and IP address ranges'
warninglist['list'] = sorted(set(lips))
warninglist['type'] = 'cidr'
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]


with open('../lists/microsoft-office365-ip/lists.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)
