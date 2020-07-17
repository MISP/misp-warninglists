#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, download_to_file, get_abspath_list_file, get_version


def process(file, dst):

    with open(file, newline='\n', encoding='utf-8', errors='replace') as csv_file:
        sites = csv_file.readlines()[:10000]
    
    warninglist = {
        'name': 'Top 10K websites from Majestic Million',
        'version': get_version(),
        'description': 'Event contains one or more entries from the top 10K of the most used websites (Majestic Million).',
        'matching_attributes': ['hostname', 'domain'],
        'type': 'hostname',
        'list': []
    }

    for site in sites:
        v = site.split(',')[2]
        warninglist['list'].append(v.rstrip())
    warninglist['list'] = sorted(set(warninglist['list']))

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


if __name__ == '__main__':
    majestic_url = 'http://downloads.majestic.com/majestic_million.csv'
    majestic_file = 'majestic_million.csv'
    majestic_dst = 'majestic_million'

    download_to_file(majestic_url, majestic_file)
    process(majestic_file, majestic_dst)    