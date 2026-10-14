#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import ipaddress
from generator import download_to_file, get_abspath_source_file, get_version, write_to_file

ip_regex = re.compile(r"((?:(?:\d{1,3}(?:\.\d{1,3}){3})|(?:[\da-f]{0,4}(?::[\da-f]{0,4}){3,7}))\/\d+)")

def process(file, dst):
    warninglist = {
        'name': 'List of known Wikimedia address ranges',
        'version': get_version(),
        'description': 'Wikimedia address ranges (https://wikitech.wikimedia.org/w/api.php?action=parse&page=IP_and_AS_allocations&format=json&prop=wikitext)',
        'type': 'cidr',
        'list': [],
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    with open(get_abspath_source_file(file), "r") as f:
        matched = ip_regex.findall(json.load(f)['parse']['wikitext']['*'])
        for ip in matched:
            ipaddress.ip_network(ip)
            warninglist['list'].append(ip)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    wikimedia_url = 'https://wikitech.wikimedia.org/w/api.php?action=parse&page=IP_and_AS_allocations&format=json&prop=wikitext'
    wikimedia_file = "wikimedia.json"
    wikimedia_dst = 'wikimedia'

    download_to_file(wikimedia_url, wikimedia_file)
    process(wikimedia_file, wikimedia_dst)
