#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks


def process(file, dst):
    l = []
    with open(get_abspath_source_file(file), 'r') as csv_file:
        icloud_private_relay_ip_list = csv.reader(csv_file)
        for row in icloud_private_relay_ip_list:
            l.append(row[0])

    warninglist = {
        'name': 'List of known iCloud Private Relay egress IP address ranges',
        'version': get_version(),
        'description': 'iCloud Private Relay egress IP address ranges (https://developer.apple.com/support/prepare-your-network-for-icloud-private-relay/)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    icloud_private_relay_url = "https://mask-api.icloud.com/egress-ip-ranges.csv"
    icloud_private_relay_file = "icloud_private_relay_ip-ranges.json"
    icloud_private_relay_dst = "icloud-private-relay"

    download_to_file(icloud_private_relay_url, icloud_private_relay_file)
    process(icloud_private_relay_file, icloud_private_relay_dst)
