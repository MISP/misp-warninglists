#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks


def process(file, dst):
    with open(get_abspath_source_file(file), 'r') as json_file:
        zscaler_ip_list = json.load(json_file)
    l = []

    for prefix in zscaler_ip_list['hubPrefixes']:
        l.append(prefix)

    warninglist = {
        'name': 'List of known Zscaler IP address ranges',
        'version': get_version(),
        'description': 'Zscaler IP address ranges (https://config.zscaler.com/api/zscaler.net/hubs/cidr/json/required)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    zscaler_url = "https://config.zscaler.com/api/zscaler.net/hubs/cidr/json/required"
    zscaler_file = "zscaler_ip-ranges.json"
    zscaler_dst = "zscaler"

    download_to_file(zscaler_url, zscaler_file)
    process(zscaler_file, zscaler_dst)
