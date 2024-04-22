#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import codecs
import ipaddress
import re

from generator import download, get_version, write_to_file


def process(url, dst):
    warninglist = {
        'name': 'List of known Wikimedia address ranges',
        'version': get_version(),
        'description': 'Wikimedia address ranges (http://noc.wikimedia.org/conf/reverse-proxy.php.txt)',
        'type': 'cidr',
        'list': [],
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    matched = re.findall(
        r'\'(.*?)\'', codecs.decode(download(url).content, 'UTF-8'))
    for ip in matched:
        try:
            ipaddress.ip_network(ip)
            warninglist['list'].append(ip)
        except ValueError:
            pass

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    wikimedia_url = 'http://noc.wikimedia.org/conf/reverse-proxy.php.txt'
    wikimedia_dst = 'wikimedia'

    process(wikimedia_url, wikimedia_dst)
