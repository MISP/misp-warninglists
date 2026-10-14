#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Linode (Akamai Connected Cloud) warninglist.

Linode self-publishes the address space it assigns to its instances as an
RFC 8805 geofeed:

    <prefix>,<alpha2code>,<region>,<city>,<postal_code>

Only the prefix matters here; the geolocation columns are ignored.

Two things worth knowing about this list:

Linode is now Akamai Connected Cloud, and AS63949 (AKAMAI-LINODE-AP) is picked
up by generate-akamai.py, so part of this space also appears in lists/akamai.
The two are kept separate deliberately: the Akamai list exists to recognise CDN
edge traffic, whereas this is rentable compute, and a maintainer who decides
the Akamai list should not carry VPS space can set EXCLUDED_ASNS there without
losing the ability to recognise Linode addresses here.

Like any general-purpose cloud, this address space is rented by the hour and
the tenant behind any given address changes constantly. The list is useful for
recognising that an address belongs to Linode, not for concluding that traffic
from it is benign.
"""

import ipaddress
import logging

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = "https://geoip.linode.com/"


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
        raise Exception("No Linode prefixes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known Linode (Akamai Connected Cloud) IP address ranges",
        "version": get_version(),
        "description": (
            "Linode (Akamai Connected Cloud) IP address ranges, from their "
            "published RFC 8805 geofeed ({})".format(URL)
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
    write_to_file(warninglist, "linode")


if __name__ == "__main__":
    main()
