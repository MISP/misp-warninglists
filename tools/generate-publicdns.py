#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import ipaddress
import json
import logging

from generator import download_to_file, get_abspath_list_file, get_version


def process(file, warninglist, dst, type='v4'):

    with open(file) as csv_file:
        servers_list = csv.reader(csv_file, delimiter=',', quotechar='"')

        data_list = []
        for row in servers_list:
            if row[7] in (None, ""):
                try:
                    ip = ipaddress.ip_address(row[0])

                    if type == 'v4' and ip.version == 4:
                        data_list.append(ip.compressed)
                    elif type == 'v6' and ip.version == 6:
                        data_list.append(ip.compressed)
                    elif type == 'hostname' and row[1] not in (None, "", '.'):
                        data_list.append(row[1])
                except ValueError as exc:
                    logging.warning(str(exc))

    warninglist['version'] = get_version()
    warninglist['list'] = sorted(set(data_list))

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


if __name__ == '__main__':
    publicdns_url = 'https://public-dns.info/nameservers.csv'
    publicdns_file = 'public-dns-nameservers.csv'

    download_to_file(publicdns_url, publicdns_file)

    # Public DNS Domains
    publicdns_hostname_dst = 'public-dns-hostname'
    publicdns_hostname_warninglist = {
        'description': 'Event contains one or more public DNS resolvers (expressed as hostname) as attribute with an IDS flag set',
        'name': 'List of known public DNS resolvers expressed as hostname',
        'type': 'hostname',
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip']
    }
    process(publicdns_file, publicdns_hostname_warninglist,
            publicdns_hostname_dst, type='hostname')

    # Public DNS IPv4
    publicdns_ipv4_dst = 'public-dns-v4'
    publicdns_ipv4_warninglist = {
        'description': 'Event contains one or more public IPv4 DNS resolvers as attribute with an IDS flag set',
        'name': 'List of known IPv4 public DNS resolvers',
        'type': 'string',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip']
    }
    process(publicdns_file, publicdns_ipv4_warninglist,
            publicdns_ipv4_dst, type='v4')

    # Public DNS IPv4
    publicdns_ipv6_dst = 'public-dns-v6'
    publicdns_ipv6_warninglist = {
        'description': 'Event contains one or more public IPv6 DNS resolvers as attribute with an IDS flag set',
        'name': 'List of known IPv6 public DNS resolvers',
        'type': 'string',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip']
    }
    process(publicdns_file, publicdns_ipv6_warninglist,
            publicdns_ipv6_dst, type='v6')
