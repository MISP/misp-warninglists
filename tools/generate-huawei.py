#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Huawei Cloud warninglist.

Source (tier 1, vendor-published endpoint): Huawei Cloud publishes the address
space it assigns to its cloud regions as an RFC 8805 geofeed, served from its
own static-resource CDN:

    https://res-static.hc-cdn.cn/cloudbu-site/china/zh-cn/IP-location/google-geo-feed.csv

This is not a URL guessed at or taken from a blog post. It is the value of the
``geofeed:`` attribute published in the APNIC whois records of Huawei Cloud's
own inetnum objects -- the blocks registered with netnames such as
``Huawei-Cloud-CO`` and ``Huawei-Cloud-HK`` all point at exactly this file.
The registry data therefore vouches for the feed: Huawei is the party that
told the RIR where to find it.

Format is plain RFC 8805:

    <prefix>,<alpha2code>,<region>,<city>,<postal_code>

Only the prefix column is used; the geolocation columns are ignored. The feed
carries both IPv4 and IPv6 prefixes and they go into the one list.

The feed was preferred over the tier-2 fallback (RIPEstat announced-prefixes
for AS55990 "HWCSNET / Huawei Cloud Service data center" and AS136907
"HWCLOUDS-AS-AP / HUAWEI CLOUDS"). It was checked against both: of the 410
prefixes AS55990 announced and the 652 AS136907 announced at the time of
writing, 400 and 612 respectively overlap an entry in this feed. The vendor's
own statement of its address space is the better authority, and unlike a BGP
snapshot it does not drift with transient announcement changes.

Semantics caveat -- this matters more here than the coverage does:

    This is general-purpose rented compute: the tenant behind any given
    address changes constantly and an attacker can simply rent one. The list
    recognises that an address belongs to the provider; it is NOT grounds for
    treating traffic as benign.

A hit tells you who owns the wire, not who is on it.
"""

import ipaddress
import logging

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = (
    "https://res-static.hc-cdn.cn/cloudbu-site/china/zh-cn/"
    "IP-location/google-geo-feed.csv"
)

SEMANTICS_CAVEAT = (
    "This is general-purpose rented compute: the tenant behind any given "
    "address changes constantly and an attacker can simply rent one. The list "
    "recognises that an address belongs to the provider; it is NOT grounds "
    "for treating traffic as benign."
)


def parse_geofeed(text):
    """Prefixes from an RFC 8805 geofeed, one per line, first column."""
    networks = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        prefix = line.split(",")[0].strip()
        if not prefix:
            continue
        try:
            # strict=True (the default): a prefix with host bits set is
            # ambiguous, and the only way to accept one is to widen it to its
            # enclosing network -- which would suppress alerts for addresses
            # nobody has claimed. Skip it instead.
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
            "No Huawei Cloud prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known Huawei Cloud IP address ranges",
        "version": get_version(),
        "description": (
            "Huawei Cloud IP address ranges, from the RFC 8805 geofeed Huawei "
            "publishes for its cloud regions ({}), the file referenced by the "
            "geofeed: attribute of Huawei Cloud's own inetnum objects in "
            "APNIC whois. {}".format(URL, SEMANTICS_CAVEAT)
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
    write_to_file(warninglist, "huawei-cloud")


if __name__ == "__main__":
    main()
