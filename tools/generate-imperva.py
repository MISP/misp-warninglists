#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Imperva (Incapsula) warninglist.

Source: https://my.imperva.com/api/integration/v1/ips
Imperva's own documentation specifies POST for this endpoint, but a plain
GET returns the same HTTP 200 with the same JSON body in testing, so GET is
used here (no request body / credentials required either way).
"""

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    response = download("https://my.imperva.com/api/integration/v1/ips")
    response.raise_for_status()
    parsed = json.loads(response.text)

    ranges = list(parsed.get("ipRanges", []))
    ranges.extend(parsed.get("ipv6Ranges", []))

    if not ranges:
        raise Exception("No Imperva IP ranges found, refusing to write an empty list")

    warninglist = {
        'name': "List of known Imperva (Incapsula) IP address ranges",
        'version': get_version(),
        'description': "Imperva (Incapsula) IP address ranges (https://my.imperva.com/api/integration/v1/ips)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "imperva")
