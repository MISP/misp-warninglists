#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv4.txt'
r = requests.get(url, stream=True)
ipsv4 = []
for ip in r.iter_lines():
    v = ip.decode('utf-8')
    if not v.startswith("#"):
        if v: ipsv4.append(v)

warninglist = {}
warninglist['name'] = 'Specialized list of IPv4 addresses belonging to common VPN providers and datacenters'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Specialized list of IPv4 addresses belonging to common VPN providers and datacenters'
warninglist['list'] = sorted(set(ipsv4))
warninglist['type'] = 'cidr'
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]


with open('../lists/vpn-ipv4/list.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)


url = 'https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv6.txt'
r = requests.get(url, stream=True)
ipsv6 = []
for ip in r.iter_lines():
    v = ip.decode('utf-8')
    if not v.startswith("#"):
        if v: ipsv6.append(v)

warninglist = {}
warninglist['name'] = 'Specialized list of IPv6 addresses belonging to common VPN providers and datacenters'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Specialized list of IPv6 addresses belonging to common VPN providers and datacenters'
warninglist['list'] = sorted(set(ipsv6))
warninglist['type'] = 'cidr'
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]


with open('../lists/vpn-ipv6/list.json', 'w') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)


