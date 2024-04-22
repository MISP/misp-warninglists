#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    bots = download("https://developers.google.com/search/apis/ipranges/googlebot.json")
    parsed = json.loads(bots.text)

    ranges = [p["ipv4Prefix"] if "ipv4Prefix" in p else p["ipv6Prefix"] for p in parsed["prefixes"]]

    warninglist = {
        'name': 'List of known Googlebot IP ranges (https://developers.google.com/search/apis/ipranges/googlebot.json)',
        'version': get_version(),
        'description': "Google Bot IP address ranges (https://developers.google.com/search/apis/ipranges/googlebot.json)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "googlebot")
