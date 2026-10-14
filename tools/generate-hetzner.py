#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Hetzner warninglist.

Tier 1, vendor-published endpoint. Hetzner Online GmbH self-publishes the
address space it assigns to its dedicated servers, cloud servers and other
services as an RFC 8805 geofeed on its own web site:

    https://www.hetzner.com/geofeed.csv

    <prefix>,<alpha2code>,<region>,<city>,<postal_code>

Only the prefix column matters here; the geolocation columns are ignored.
The feed carries both IPv4 and IPv6 prefixes and both go into this one list.
Because it is an assignment-level feed, the IPv6 side is very granular --
tens of thousands of per-assignment /64s and /63s -- and consolidation can
only merge the adjacent ones. That granularity is deliberate: it describes
exactly the space Hetzner published, and nothing more.

Semantics caveat: this is general-purpose rented compute. The tenant behind
any given address changes constantly and an attacker can simply rent one.
The list recognises that an address belongs to the provider; it is NOT
grounds for treating traffic as benign.
"""

import ipaddress
import logging

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = "https://www.hetzner.com/geofeed.csv"

DESCRIPTION = (
    "Hetzner Online GmbH IP address ranges, from their published RFC 8805 "
    "geofeed ({}). This is general-purpose rented compute: the tenant behind "
    "any given address changes constantly and an attacker can simply rent "
    "one. The list recognises that an address belongs to the provider; it is "
    "NOT grounds for treating traffic as benign.".format(URL)
)


def parse_geofeed(text):
    networks = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        prefix = line.split(",")[0].strip()
        if not prefix:
            continue
        try:
            # strict=True: a prefix with host bits set is ambiguous, and the
            # only way to accept one is to widen it to its enclosing network,
            # which would suppress alerts for addresses nobody claimed.
            ipaddress.ip_network(prefix)
        except ValueError as exc:
            logging.warning("Skipping malformed prefix %s: %s", prefix, exc)
            continue
        networks.append(prefix)
    return networks


def main():
    response = download(URL)
    response.raise_for_status()

    networks = parse_geofeed(response.text)
    if not networks:
        raise Exception(
            "No Hetzner prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known Hetzner IP address ranges",
        "version": get_version(),
        "description": DESCRIPTION,
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
    write_to_file(warninglist, "hetzner")


if __name__ == "__main__":
    main()
