#!/usr/bin/env python3

import csv
import ipaddress
import logging
from typing import List, Tuple

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file

golden_servers_ipv4 = ['9.9.9.9', '8.8.8.8', '1.0.0.1', '1.1.1.3', '8.8.4.4', '1.1.1.1']


def process(ipv4: List, ipv6: List, hostname: List):
    # Public DNS Domains
    publicdns_hostname_dst = 'public-dns-hostname'
    publicdns_hostname_warninglist = {
        'description': 'Event contains one or more public DNS resolvers (expressed as hostname) as attribute with an IDS flag set',
        'name': 'List of known public DNS resolvers expressed as hostname',
        'type': 'hostname',
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip']
    }
    generate(hostname, publicdns_hostname_warninglist, publicdns_hostname_dst)

    # Public DNS IPv4
    publicdns_ipv4_dst = 'public-dns-v4'
    publicdns_ipv4_warninglist = {
        'description': 'Event contains one or more public IPv4 DNS resolvers as attribute with an IDS flag set',
        'name': 'List of known IPv4 public DNS resolvers',
        'type': 'cidr',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip', 'ip-src|port', 'ip-dst|port']
    }
    generate(ipv4, publicdns_ipv4_warninglist, publicdns_ipv4_dst)

    # Public DNS IPv4
    publicdns_ipv6_dst = 'public-dns-v6'
    publicdns_ipv6_warninglist = {
        'description': 'Event contains one or more public IPv6 DNS resolvers as attribute with an IDS flag set',
        'name': 'List of known IPv6 public DNS resolvers',
        'type': 'cidr',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip', 'ip-src|port', 'ip-dst|port']
    }
    generate(ipv6, publicdns_ipv6_warninglist, publicdns_ipv6_dst)


def generate(data_list, warninglist, dst):
    warninglist['version'] = get_version()
    warninglist['list'] = data_list

    write_to_file(warninglist, dst)


def get_lists_publidns(file) -> Tuple[List, List, List]:
    with open(get_abspath_source_file(file)) as csv_file:
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

                    if row[1] not in (None, '', '.', '-.'):
                        row[1] = row[1].rstrip('.')
                        lhostname.append(row[1])
                except ValueError as exc:
                    logging.warning(str(exc))

        for golden in golden_servers_ipv4:
            if golden not in lipv4:
                lipv4.append(golden)

    return lipv4, lipv6, lhostname


def get_lists_dnscrypt(file) -> Tuple[List, List]:
    with open(get_abspath_source_file(file)) as csv_file:
        servers_list = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(servers_list)  # skip header
        lipv4 = []
        lipv6 = []
        for row in servers_list:
            address = row[10]
            if address[0] == "[":
                address = address[1:address.index("]")]
            else:
                address = address.split(":")[0]
            ip = ipaddress.ip_address(address)
            if ip.version == 4:
                lipv4.append(ip.compressed)
            elif ip.version == 6:
                lipv6.append(ip.compressed)

    return lipv4, lipv6


def main():
    publicdns_url = 'https://public-dns.info/nameservers.csv'
    publicdns_file = 'public-dns-nameservers.csv'
    download_to_file(publicdns_url, publicdns_file)

    dnscrypt_url = "https://raw.githubusercontent.com/DNSCrypt/dnscrypt-resolvers/master/v1/dnscrypt-resolvers.csv"
    dnscrypt_file = "dnscrypt-resolvers.csv"
    download_to_file(dnscrypt_url, dnscrypt_file)

    ipv4, ipv6, hostname = get_lists_publidns(publicdns_file)
    ipv4_c, ipv6_c = get_lists_dnscrypt(dnscrypt_file)

    ipv4 += ipv4_c
    ipv6 += ipv6_c

    process(ipv4, ipv6, hostname)


if __name__ == '__main__':
    main()
