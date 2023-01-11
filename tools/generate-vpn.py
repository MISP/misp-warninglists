#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import process_stream, get_version, write_to_file, consolidate_networks


def process(url, dst):
    warninglist = {
        'name': 'Specialized list of {} addresses belonging to common VPN providers and datacenters'.format(dst),
        'version': get_version(),
        'description': 'Specialized list of {} addresses belonging to common VPN providers and datacenters'.format(dst),
        'list': consolidate_networks(process_stream(url)),
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    url = 'https://raw.githubusercontent.com/X4BNet/lists_vpn/main/ipv4.txt'
    dst = 'vpn-ipv4'
    process(url, dst)
