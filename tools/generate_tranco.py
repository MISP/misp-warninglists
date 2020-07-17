#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import zipfile

from generator import download, download_to_file, get_abspath_list_file, get_version


def process(file, warninglist, dst, first_10k=False):

    with zipfile.ZipFile(file, 'r') as tranco_lists:
        for name in tranco_lists.namelist():
            if name == 'top-1m.csv':
                with tranco_lists.open(name) as tranco:
                    if first_10k:
                        sites = tranco.readlines()[:10000]
                    else:
                        sites = tranco.readlines()
            else:
                continue
    
    warninglist['type'] = 'hostname'
    warninglist['version'] = get_version()
    warninglist['matching_attributes'] = ['hostname', 'domain', 'url', 'domain|ip']

    for site in sites:
        v = site.decode('UTF-8').split(',')[1]
        warninglist['list'].append(v.rstrip())
    warninglist['list'] = sorted(set(warninglist['list']))

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


if __name__ == '__main__':
    tranco_url = 'https://tranco-list.eu/top-1m.csv.zip'
    tranco_file = 'tranco_top-1m.csv.zip'

    download_to_file(tranco_url, tranco_file)

    # Top 1M
    tranco_dst = "tranco"
    tranco_warninglist = {
        'description': "Event contains one or more entries from the top 1,000,000 most-used sites (https://tranco-list.eu/).",
        'name': "Top 1,000,000 most-used sites from Tranco"
    }
    process(tranco_file, tranco_warninglist, tranco_dst)

    # Top 10K
    tranco_10k_dst = "tranco10k"
    tranco_10k_warninglist = {
        'description': "Event contains one or more entries from the top 10K most-used sites (https://tranco-list.eu/).",
        'name': "Top 10K most-used sites from Tranco"
    }
    process(tranco_file, tranco_10k_warninglist, tranco_10k_dst, first_10k=True)
