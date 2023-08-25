#!/usr/bin/env python3

import ipaddress
import logging
from typing import List

from generator import get_version, write_to_file, Dns, create_resolver

# Static Umbrella blockpage addresses: https://docs.umbrella.com/deployment-umbrella/docs/block-page-ip-addresses
blockpage_ip_list = [
    '146.112.61.104',
    '::ffff:146.112.61.104',
    '146.112.61.105',
    '::ffff:146.112.61.105',
    '146.112.61.106',
    '::ffff:146.112.61.106',
    '146.112.61.107',
    '::ffff:146.112.61.107',
    '146.112.61.108',
    '::ffff:146.112.61.108',
    '146.112.61.110',
    '::ffff:146.112.61.110',
]


def process(ipv4: List, ipv6: List, hostname: List):
    # Cisco Umbrella blockpage Domains
    umbrella_blockpage_hostname_dst = 'umbrella-blockpage-hostname'
    umbrella_blockpage_warninglist = {
        'description': 'Umbrella blockpage hostnames',
        'name': 'cisco-umbrella-blockpage-hostname',
        'type': 'hostname',
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip'],
    }
    generate(hostname, umbrella_blockpage_warninglist, umbrella_blockpage_hostname_dst)

    # Cisco Umbrella blockpage IPv4
    umbrella_blockpage_ipv4_dst = 'umbrella-blockpage-v4'
    umbrella_blockpage_ipv4_warninglist = {
        'description': 'Cisco Umbrella blockpage in IPv4',
        'name': 'cisco-umbrella-blockpage-ipv4',
        'type': 'cidr',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip'],
    }
    generate(ipv4, umbrella_blockpage_ipv4_warninglist, umbrella_blockpage_ipv4_dst)

    # Cisco Umbrella blockpage IPv6
    umbrella_blockpage_ipv6_dst = 'umbrella-blockpage-v6'
    umbrella_blockpage_ipv6_warninglist = {
        'description': 'Cisco Umbrella blockpage in IPv6',
        'name': 'cisco-umbrella-blockpage-ipv6',
        'type': 'cidr',
        'matching_attributes': ['ip-src', 'ip-dst', 'domain|ip'],
    }
    generate(ipv6, umbrella_blockpage_ipv6_warninglist, umbrella_blockpage_ipv6_dst)


def generate(data_list, warninglist, dst):
    warninglist['version'] = get_version()
    warninglist['list'] = data_list
    write_to_file(warninglist, dst)


def main():
    dns = Dns(create_resolver())

    ipv4_addresses = []
    ipv6_addresses = []
    host_names = []

    for ip in blockpage_ip_list:
        host_names.append(dns.get_domain_from_ip(ip))

        try:
            ip = ipaddress.ip_address(ip)

            if ip.version == 4:
                ipv4_addresses.append(ip.compressed)
            elif ip.version == 6:
                ipv6_addresses.append(ip.compressed)

        except ValueError as exc:
            logging.warning(str(exc))

    process(ipv4_addresses, ipv6_addresses, host_names)


if __name__ == '__main__':
    main()
