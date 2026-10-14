#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the CDN77 warninglist.

Source: https://prefixlists.tools.cdn77.com/public_lmax_prefixes.json
JSON shape: {"updated_at": "...", "prefixes": [{"prefix": "<cidr>"}, ...]}

The URL suggested in the initial brief, https://prefixes.cdn77.com/, does not
resolve. This is CDN77's own IP-Radar tooling host (radar.tools.cdn77.com /
prefixlists.tools.cdn77.com) and returns a live, machine-readable prefix list.
"""

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    response = download("https://prefixlists.tools.cdn77.com/public_lmax_prefixes.json")
    response.raise_for_status()
    parsed = json.loads(response.text)

    ranges = [entry["prefix"] for entry in parsed.get("prefixes", [])]

    if not ranges:
        raise Exception("No CDN77 IP ranges found, refusing to write an empty list")

    warninglist = {
        'name': "List of known CDN77 IP address ranges",
        'version': get_version(),
        'description': "CDN77 IP address ranges (https://prefixlists.tools.cdn77.com/public_lmax_prefixes.json)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "cdn77")
