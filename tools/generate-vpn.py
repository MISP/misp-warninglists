#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import process_stream, get_version, write_to_file, consolidate_networks


def process(url, dst):
    warninglist = {
        'name': 'Specialized list of {} addresses belonging to common VPN providers and datacenters'.format(dst.split('-')[1].replace('ip', 'IP')),
        'version': get_version(),
        'description': 'Specialized list of {} addresses belonging to common VPN providers and datacenters'.format(dst.split('-')[1].replace('ip', 'IP')),
        'list': consolidate_networks(process_stream(url)),
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    vpn_base_url_v4 = 'https://raw.githubusercontent.com/X4BNet/lists_vpn/main/vpn-ipv4.txt'
    vpn_base_url_v6 = 'https://raw.githubusercontent.com/ejrv/VPNs/master/vpn-ipv6.txt'

    for url in [vpn_base_url_v4, vpn_base_url_v6]:
        uri = url.split('/')[-1]
        uri.split('-')[1].replace('ip', 'IP')
        process(url, uri)
