#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate a warninglist from University of Michigan CSE connection-attempts page."""

import ipaddress
import re

from generator import consolidate_networks, download, get_version, write_to_file


def process(content: str, dst: str):
    """Parse IPv4 CIDR ranges and generate warninglist JSON."""
    candidates = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}/\d{1,2}\b", content)

    networks = []
    for candidate in candidates:
        try:
            network = ipaddress.ip_network(candidate, strict=True)
        except ValueError:
            continue

        if network.version != 4:
            continue

        networks.append(str(network))

    warninglist = {
        "name": "University of Michigan CSE connection-attempt network ranges",
        "version": get_version(),
        "description": "University of Michigan Computer Science and Engineering connection attempts page (https://cse.engin.umich.edu/about/resources/connection-attempts/)",
        "type": "cidr",
        "list": consolidate_networks(networks),
        "matching_attributes": [
            "ip-src",
            "ip-dst",
            "domain|ip",
            "ip-src|port",
            "ip-dst|port",
        ],
    }

    write_to_file(warninglist, dst)


if __name__ == "__main__":
    URL = "https://cse.engin.umich.edu/about/resources/connection-attempts/"
    DST = "umich-cse-connection-attempts"

    response = download(URL)
    response.raise_for_status()
    process(response.text, DST)
