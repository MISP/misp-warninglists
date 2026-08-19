#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download_to_file, get_version, write_to_file, get_abspath_source_file
import itertools

def process(file, dst):
    warninglist = {
        'name': "List of known Fastly IP address ranges",
        'version': get_version(),
        'description': "Fastly IP address ranges (https://api.fastly.com/public-ip-list)",
        'type': "cidr",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    with open(get_abspath_source_file(file), 'r') as f:
        warninglist['list'] = list(itertools.chain.from_iterable(json.load(f).values()))

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    url = "https://api.fastly.com/public-ip-list"
    file = "fastly"
    dst = "fastly"

    download_to_file(url, file)
    process(file, dst)
