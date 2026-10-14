#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module downloads scanner IPs published by Internet Cleanup Foundation
and updates the corresponding warninglist.
"""

import ipaddress
import re

from generator import download, get_version, write_to_file, consolidate_networks


def process(content: str, dst: str):
    """Parse scanner IPs from the Scaninfo page and generate warninglist JSON."""
    candidates = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}(?:/\d{1,2})?\b", content)

    networks = []
    for candidate in candidates:
        try:
            network = ipaddress.ip_network(candidate, strict=False)
        except ValueError:
            continue

        if network.version != 4:
            continue

        if network.network_address == ipaddress.IPv4Address("0.0.0.0"):
            continue

        networks.append(str(network))

    warninglist = {
        "name": "List of published IP address ranges for Internet Cleanup Foundation scanners",
        "version": get_version(),
        "description": "Internet Cleanup Foundation scaninfo (https://internetcleanup.foundation/scaninfo/)",
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
    URL = "https://internetcleanup.foundation/scaninfo/"
    DST = "internetcleanup-scanner"

    response = download(URL)
    response.raise_for_status()
    process(response.text, DST)
