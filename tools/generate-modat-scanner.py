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
        'name': 'List of published IP address ranges for Modat Scanner',
        'version': get_version(),
        'description': 'Modat Scanner (https://www.modat.io/)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    modat_url = "https://scanner.modat.io/ipv4.txt"
    modat_file = "modat-scanner.json"
    modat_dst = "modat-scanner"

    download_to_file(modat_url, modat_file) # Download in TMP
    process(modat_file, modat_dst)
