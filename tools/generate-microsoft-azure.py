#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import json
import datetime

url = 'https://download.microsoft.com/download/0/1/8/018E208D-54F8-44CD-AA26-CD7BC9524A8C/PublicIPs_20171226.xml'
r = requests.get(url)
office365 = ET.fromstring(r.text)
l = []
for region in office365.iter('Region'):
    for subnet in region.iter('IpRange'):
        l.append(subnet.get('Subnet'))

warninglist = {}
warninglist['name'] = 'List of known Microsoft Azure Datacenter IP Ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Microsoft Azure Datacenter IP Ranges'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]
warninglist['type'] = 'cidr'

print(json.dumps(warninglist))
