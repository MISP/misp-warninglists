#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Gcore CDN warninglist.

Source: https://api.gcore.com/cdn/public-net-list ({"addresses": [...]})
There is also a "public-ip-list" endpoint of individual /32s; the
"public-net-list" endpoint (CIDR networks) is preferred here.
"""

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    response = download("https://api.gcore.com/cdn/public-net-list")
    response.raise_for_status()
    parsed = json.loads(response.text)

    ranges = list(parsed.get("addresses", []))

    if not ranges:
        raise Exception("No Gcore IP ranges found, refusing to write an empty list")

    warninglist = {
        'name': "List of known Gcore CDN IP address ranges",
        'version': get_version(),
        'description': "Gcore CDN IP address ranges (https://api.gcore.com/cdn/public-net-list)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "gcore")
