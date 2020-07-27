#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(file, dst):
    with open(get_abspath_source_file(file), 'r') as json_file:
        amazon_aws_ip_list = json.load(json_file)
    l = []

    for prefix in amazon_aws_ip_list['prefixes']:
        l.append(prefix['ip_prefix'])

    for prefix in amazon_aws_ip_list['ipv6_prefixes']:
        l.append(prefix['ipv6_prefix'])

    warninglist = {
        'name': 'List of known Amazon AWS IP address ranges',
        'version': get_version(),
        'description': 'Amazon AWS IP address ranges (https://ip-ranges.amazonaws.com/ip-ranges.json)',
        'type': 'cidr',
        'list': l,
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    amazon_url = "https://ip-ranges.amazonaws.com/ip-ranges.json"
    amazon_file = "amazon_ip-ranges.json"
    amazon_dst = "amazon-aws"

    download_to_file(amazon_url, amazon_file)
    process(amazon_file, amazon_dst)
