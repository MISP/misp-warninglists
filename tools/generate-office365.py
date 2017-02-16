#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import json
import datetime

url = 'https://support.content.office.net/en-us/static/O365IPAddresses.xml'
r = requests.get(url)
office365 = ET.fromstring(r.text)
l = []
for address in office365.iter('address'):
    l.append(address.text.replace('*', ''))

warninglist = {}
warninglist['name'] = 'List of known Office 365 URLs and IP address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Office 365 URLs and IP address ranges'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip", "hostname"]


print(json.dumps(warninglist))
