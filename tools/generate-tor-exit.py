#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Tor exit node warninglist from X4BNet/lists_torexit.

Built the same way as generate-vpn.py, which consumes the sibling repository
lists_vpn from the same author.

Upstream publishes ipv4.txt only, so this list is IPv4-only; there is no
lists_torexit equivalent of the vpn-ipv6 list.

Unlike most generators here, this one replaces the list rather than adding to
it. Tor exit nodes come and go within hours, so carrying forward every address
that was ever an exit node would steadily turn the list into a history of the
Tor network rather than a description of it.
"""

from generator import (
    consolidate_networks,
    get_version,
    process_stream,
    write_to_file,
)


def process(url, dst):
    networks = consolidate_networks(process_stream(url))
    if not networks:
        raise Exception("No Tor exit nodes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known Tor exit nodes",
        "version": get_version(),
        "description": (
            "Specialized list of IPv4 addresses belonging to Tor exit nodes, "
            "from https://github.com/X4BNet/lists_torexit"
        ),
        "list": networks,
        "type": "cidr",
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
    url = "https://raw.githubusercontent.com/X4BNet/lists_torexit/main/ipv4.txt"
    dst = "tor-exit-nodes"
    process(url, dst)
