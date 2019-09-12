#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import datetime
import urllib.request
import re
import ipaddress 

res = urllib.request.urlopen('http://noc.wikimedia.org/conf/reverse-proxy.php.txt')

res_body = res.read()
decoded = res_body.decode("unicode_escape", "utf-8")

l = []
for line in decoded.split('\n'):
    if re.search("public", line):
        matched = re.findall(r'\'(.*?)\'', line)
        if matched:
            try:
                ipaddress.ip_network(matched[0])
                l.append(matched[0])
            except ValueError:
                pass
   
warninglist = {}
warninglist['name'] = 'List of known Wikimedia address ranges'
warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
warninglist['description'] = 'Wikimedia address ranges (http://noc.wikimedia.org/conf/reverse-proxy.php.txt)'
warninglist['type'] = 'cidr'
warninglist['list'] = sorted(set(l))
warninglist['matching_attributes'] = ["ip-src", "ip-dst", "domain|ip"]

print(json.dumps(warninglist))
