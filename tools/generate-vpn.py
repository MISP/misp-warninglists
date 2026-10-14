#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from ipaddress import ip_network

from generator import download, get_version, write_to_file, consolidate_networks


SOURCE = 'https://raw.githubusercontent.com/X4BNet/lists_vpn/main/output'
CATEGORIES = {
    'vpn': 'common VPN providers',
    'datacenter': 'datacenters and VPN providers',
}


def process(category, ip_version):
    dst = '{}-ipv{}'.format(category, ip_version)
    url = '{}/{}/ipv{}.txt'.format(SOURCE, category, ip_version)
    response = download(url)
    response.raise_for_status()

    networks = []
    for line in response.text.splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        network = ip_network(line)
        if network.version != ip_version:
            raise ValueError('Unexpected IP version in {}: {}'.format(url, line))
        networks.append(network)
    if not networks:
        raise ValueError('No networks found in {}, refusing to write an empty list'.format(url))

    warninglist = {
        'name': 'List of known IPv{} networks belonging to {}'.format(ip_version, CATEGORIES[category]),
        'version': get_version(),
        'category': 'known',
        'description': 'IPv{} networks belonging to {}, from {}'.format(ip_version, CATEGORIES[category], url),
        'list': consolidate_networks(networks),
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


def main():
    for category in CATEGORIES:
        for ip_version in (4, 6):
            process(category, ip_version)


if __name__ == '__main__':
    main()
