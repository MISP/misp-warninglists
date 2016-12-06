#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import json

url = 'https://support.content.office.net/en-us/static/O365IPAddresses.xml'
r = requests.get(url)
office365 = ET.fromstring(r.text)
l = []
for address in office365.iter('address'):
    l.append(address.text.replace('*', ''))

warninglist = {}
warninglist['description'] = 'Office 365 URLs and IP address ranges'
warninglist['list'] = l

print (json.dumps(warninglist))
