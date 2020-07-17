#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile
import json

from generator import download, download_to_file, get_abspath_list_file, get_version


def process(file, dst):
    with zipfile.ZipFile(file, 'r') as cisco_lists:
        for name in cisco_lists.namelist():
            if name == "top-1m.csv":
                with cisco_lists.open(name) as top:
                    top1000 = top.readlines()[:1000]
            else:
                continue
    
    warninglist = {
        'description': 'Event contains one or more entries from the top 1000 of the most used website (Cisco Umbrella).',
        'version': get_version(),
        'name': 'Top 1000 website from Cisco Umbrella',
        'type': 'hostname',
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip'],
        'list': []
    }

    for site in top1000:
        v = site.decode('UTF-8').split(',')[1]
        warninglist['list'].append(v.strip().replace('\\r\\n',''))
    warninglist['list'] = sorted(set(warninglist['list']))
    
    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


if __name__ == '__main__':
    cisco_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    cisco_file = "cisco_top-1m.csv.zip"
    cisco_dst = 'cisco_top1000'
    
    download_to_file(cisco_url, cisco_file)
    process(cisco_file, cisco_dst)