#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the DigitalOcean warninglist.

DigitalOcean self-publishes the address space it assigns to droplets and
managed services as an RFC 8805 geofeed:

    <prefix>,<alpha2code>,<region>,<city>,<postal_code>

Only the prefix matters here; the geolocation columns are ignored.

Note this is general-purpose cloud hosting rather than a CDN or a fixed set of
service endpoints: the address space is rented out and the tenant behind any
given address changes over time. The list is useful for recognising that an
address belongs to DigitalOcean, not for concluding that traffic from it is
benign.
"""

import ipaddress
import logging

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = "https://digitalocean.com/geo/google.csv"


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
            "No DigitalOcean prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known DigitalOcean IP address ranges",
        "version": get_version(),
        "description": (
            "DigitalOcean IP address ranges, from their published RFC 8805 "
            "geofeed ({})".format(URL)
        ),
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
    write_to_file(warninglist, "digitalocean")


if __name__ == "__main__":
    main()
