#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks


def process(file, dst):
    with open(get_abspath_source_file(file), 'r') as json_file:
        checkhost_ip_list = json.load(json_file)
    l = []

    for prefix in checkhost_ip_list['nodes']:
        l.append(prefix)

    warninglist = {
        'name': 'List of known check-host.net IP address ranges',
        'version': get_version(),
        'description': 'check-host IP addresses (https://check-host.net/nodes/ips)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    checkhost_url = "https://check-host.net/nodes/ips"
    checkhost_file = "check-host-net.json"
    checkhost_dst = "check-host-net"

    download_to_file(checkhost_url, checkhost_file)
    process(checkhost_file, checkhost_dst)
