#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the CacheFly warninglist.

Source: https://cachefly.cachefly.net/ips/cdn.txt (plain text, one CIDR per line)
"""

from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    response = download("https://cachefly.cachefly.net/ips/cdn.txt")
    response.raise_for_status()

    ranges = [line.strip() for line in response.text.splitlines() if line.strip()]

    if not ranges:
        raise Exception("No CacheFly IP ranges found, refusing to write an empty list")

    warninglist = {
        'name': "List of known CacheFly IP address ranges",
        'version': get_version(),
        'description': "CacheFly IP address ranges (https://cachefly.cachefly.net/ips/cdn.txt)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "cachefly")
