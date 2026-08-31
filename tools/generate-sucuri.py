#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Sucuri (Website Firewall / WAF) warninglist.

Sucuri does not publish an API or a dedicated machine-readable file for its
WAF IP ranges. The URL suggested in the initial brief 404s, and no such
endpoint could be found after research.

The ranges are, however, published in a stable, parseable structure on
Sucuri's own documentation page: a single <pre><code> block that immediately
follows the sentence "Check our IP ranges:" on the troubleshooting guide.
This is scraped directly (not hand-transcribed) at generation time, one CIDR
per line inside that code block. If Sucuri ever restructures that page this
generator will simply fail to find any ranges and refuse to write, rather
than silently going stale.

Source: https://docs.sucuri.net/website-firewall/sucuri-firewall-troubleshooting-guide/
"""

import re

from generator import download, get_version, write_to_file, consolidate_networks

URL = "https://docs.sucuri.net/website-firewall/sucuri-firewall-troubleshooting-guide/"
ANCHOR = "Check our IP ranges:"


def extract_ranges(html):
    anchor_pos = html.find(ANCHOR)
    if anchor_pos == -1:
        return []

    remainder = html[anchor_pos:]
    match = re.search(r"<pre><code>(.*?)</code></pre>", remainder, re.DOTALL)
    if not match:
        return []

    block = match.group(1)
    # Strip any stray HTML entities/tags defensively, then split on whitespace.
    block = re.sub(r"<[^>]+>", "", block)
    block = block.replace("&amp;", "&")

    ranges = []
    for token in block.split():
        token = token.strip()
        if "/" in token:
            ranges.append(token)
    return ranges


if __name__ == '__main__':
    response = download(URL)
    response.raise_for_status()

    ranges = extract_ranges(response.text)

    if not ranges:
        raise Exception(
            "No Sucuri IP ranges found on the docs page, refusing to write an empty list"
        )

    warninglist = {
        'name': "List of known Sucuri (Website Firewall) IP address ranges",
        'version': get_version(),
        'description': "Sucuri Website Firewall IP address ranges, scraped from "
                        "https://docs.sucuri.net/website-firewall/sucuri-firewall-troubleshooting-guide/ "
                        "(no machine-readable API is published)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "sucuri")
