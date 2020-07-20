#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import ipaddress
import json
import logging

from generator import download_to_file, get_version, write_to_file


def process(file):
    lipv4, lipv6, lhostname = get_lists(file)

    # Public DNS Domains
    publicdns_hostname_dst = 'public-dns-hostname'
    publicdns_hostname_warninglist = {
        'description': 'Event contains one or more public DNS resolvers (expressed as hostname) as attribute with an IDS flag set',
        'name': 'List of known public DNS resolvers expressed as hostname',
        'type': 'hostname',
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip']
    }
    generate(lhostname, publicdns_hostname_warninglist, publicdns_hostname_dst)

    # Public DNS IPv4
    publicdns_ipv4_dst = 'public-dns-v4'
    publicdns_ipv4_warninglist = {
        'description': 'Event contains one or more public IPv4 DNS resolvers as attribute with an IDS flag set',
        'name': 'List of known IPv4 public DNS resolvers',
        'type': 'string',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip']
    }
    generate(lipv4, publicdns_ipv4_warninglist, publicdns_ipv4_dst)

    # Public DNS IPv4
    publicdns_ipv6_dst = 'public-dns-v6'
    publicdns_ipv6_warninglist = {
        'description': 'Event contains one or more public IPv6 DNS resolvers as attribute with an IDS flag set',
        'name': 'List of known IPv6 public DNS resolvers',
        'type': 'string',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip']
    }
    generate(lipv6, publicdns_ipv6_warninglist, publicdns_ipv6_dst)


def generate(data_list, warninglist, dst):

    warninglist['version'] = get_version()
    warninglist['list'] = sorted(set(data_list))

    write_to_file(warninglist, dst)


def get_lists(file):

    with open(file) as csv_file:
        servers_list = csv.reader(csv_file, delimiter=',', quotechar='"')

        lipv4 = []
        lipv6 = []
        lhostname = []
        for row in servers_list:
            if row[7] in (None, ""):
                try:
                    ip = ipaddress.ip_address(row[0])

                    if ip.version == 4:
                        lipv4.append(ip.compressed)
                    elif ip.version == 6:
                        lipv6.append(ip.compressed)

                    if row[1] not in (None, "", '.'):
                        lhostname.append(row[1])
                except ValueError as exc:
                    logging.warning(str(exc))

    return lipv4, lipv6, lhostname


if __name__ == '__main__':
    publicdns_url = 'https://public-dns.info/nameservers.csv'
    publicdns_file = 'public-dns-nameservers.csv'

    download_to_file(publicdns_url, publicdns_file)

    process(publicdns_file)
