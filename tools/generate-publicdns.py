#!/usr/bin/env python3

import csv
import datetime
import logging
import ipaddress
import json
import os
import requests

servers_url = 'http://public-dns.info/nameservers.csv'
csv_path = 'nameservers.csv'
dns4_path = 'list4.json'
dns6_path = 'list6.json'

if os.path.isfile(csv_path):
    logging.warning('Not erasing local csv file')
else:
    req = requests.get(servers_url)
    with open(csv_path, 'wb') as fd:
        for chunk in req.iter_content(4096):
            fd.write(chunk)

ip4_list = []
ip6_list = []
with open(csv_path) as csv_file:
    servers_list = csv.reader(csv_file, delimiter=',', quotechar='"')

    for row in servers_list:
        if row[5] == '':
            try: 
                ip = ipaddress.ip_address(row[0])

                if ip.version == 4:
                    list = ip4_list
                else:
                    list = ip6_list

                list.append(ip.compressed)
                if len(row[1]) > 0 and row[1] != '.':
                    list.append(row[1])

            except ValueError as exc:
                logging.warning(str(exc))

version = datetime.datetime.now().strftime('%Y%m%d')

out4_list = {}
out4_list['name'] = 'List of known IPv4 public DNS resolvers'
out4_list['version'] = version
out4_list['description'] = 'Event contains one or more public IPv4 DNS resolvers as attribute with an IDS flag set'
out4_list['matching_attribute'] = [ 'ip-src', 'ip-dst', 'domain|ip' ]
out4_list['list'] = sorted(ip4_list)


out6_list = {}
out6_list['name'] = 'List of known IPv6 public DNS resolvers'
out6_list['version'] = version
out6_list['description'] = 'Event contains one or more public IPv6 DNS resolvers as attribute with an IDS flag set'
out6_list['matching_attribute'] = [ 'ip-src', 'ip-dst', 'domain|ip' ]
out6_list['list'] = sorted(ip6_list)


#print(json.dumps(out4_list, indent=True))
with open(dns4_path, 'w') as dns4_file:
    dns4_file.write(json.dumps(out4_list, indent=4, sort_keys=True))

with open(dns6_path, 'w') as dns6_file:
    dns6_file.write(json.dumps(out6_list, indent=4, sort_keys=True))
