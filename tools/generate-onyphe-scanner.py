#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks

def process(file, dst):
    l = []
    with open(get_abspath_source_file(file), 'r') as freetext_file:
        for line in freetext_file:
            if not line.startswith("#"):
                cidr = line.rstrip()
                l.append(cidr)

    warninglist = {
        'name': 'List of published IP address ranges for Onyphe Scanner',
        'version': get_version(),
        'description': 'Onyphe Scanner (https://www.onyphe.io/)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    onyphe_url = "https://www.onyphe.io/ip-ranges.txt"
    onyphe_file = "onyphe-scanner.json"
    onyphe_dst = "onyphe-scanner"

    download_to_file(onyphe_url, onyphe_file) # Download in TMP
    process(onyphe_file, onyphe_dst)
