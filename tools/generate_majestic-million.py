#!/usr/bin/env python3

import datetime
import logging
import json
import os
import requests

servers_url = 'http://downloads.majestic.com/majestic_million.csv'
csv_path = 'majestic_million.csv'
hostname_path = 'list.json'

if os.path.isfile(csv_path):
    logging.warning('Not erasing local csv file')
else:
    req = requests.get(servers_url)
    with open(csv_path, 'wb') as fd:
        for chunk in req.iter_content(4096):
            fd.write(chunk)

host_list = []
with open(csv_path, newline='\n', encoding='utf-8', errors='replace') as csv_file:
    top10k = csv_file.readlines()[:10000]

version = int(datetime.date.today().strftime('%Y%m%d'))
out_list = {}

out_list['name'] = 'Top 10K websites from Majestic Million'
out_list['version'] = version
out_list['description'] = 'Event contains one or more entries from the top 10K of the most used websites (Majestic Million).'
out_list['matching_attributes'] = ['hostname', 'domain']
out_list['type'] = 'hostname'
out_list['list'] = sorted(set(host_list))

for hostname in top10k:
    v = hostname.split(',')[2]
    out_list['list'].append(v.rstrip())
out_list['list'] = sorted(set(out_list['list']))
with open(hostname_path, 'w', newline='\n') as hostname_file:
    hostname_file.write(json.dumps(out_list, indent=2, sort_keys=False))
