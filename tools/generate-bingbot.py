#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    bots = download("https://www.bing.com/toolbox/bingbot.json")
    parsed = json.loads(bots.text)

    ranges = [p["ipv4Prefix"] if "ipv4Prefix" in p else p["ipv6Prefix"] for p in parsed["prefixes"]]

    warninglist = {
        'name': 'List of known Bingbot IP ranges (https://www.bing.com/toolbox/bingbot.json)',
        'version': get_version(),
        'description': "Microsoft Bingbot crawler IP address ranges (https://www.bing.com/toolbox/bingbot.json)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "bingbot")
