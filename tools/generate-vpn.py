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
    vpn_base_url = 'https://raw.githubusercontent.com/ejrv/VPNs/master/'
    uri_list = ['vpn-ipv4', 'vpn-ipv6']

    for uri in uri_list:
        url = vpn_base_url + uri + '.txt'
        uri.split('-')[1].replace('ip', 'IP')
        process(url, uri)
