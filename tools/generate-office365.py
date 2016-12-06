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
d = datetime.datetime.now()
warninglist['version'] = "{0}{1:02d}{2:02d}".format(d.year, d.month, d.day)
warninglist['description'] = 'Office 365 URLs and IP address ranges'
warninglist['list'] = l


print (json.dumps(warninglist))
