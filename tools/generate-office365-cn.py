#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import json
import datetime

url = 'https://download.microsoft.com/download/3/5/3/353F871C-5CF8-4CF8-8A76-6A88D9CA1ABE/PublicIPs_MC_20171211.xml'
r = requests.get(url)
office365 = ET.fromstring(r.text)
l = []
for region in office365.iter('Region'):
    for subnet in region.iter('IpRange'):
        l.append(subnet.get('Subnet'))

warninglist = {}
warninglist['name'] = 'List of known Office 365 IP address ranges in China'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Office 365 IP address ranges in China'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]
warninglist['type'] = 'cidr'

print(json.dumps(warninglist))
