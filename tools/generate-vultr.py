#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Vultr warninglist.

Tier 1, vendor-published endpoint. Vultr (operated by Constant Company, LLC)
self-publishes the address space it assigns to its cloud compute instances as
an RFC 8805 geofeed:

    <prefix>,<alpha2code>,<region>,<city>,<postal_code>

The feed's own header comment reads "Constant.com / Vultr.com GeoFeed
(AS20473)" with support@vultr.com as the contact, which is what identifies it
as Vultr's. Only the prefix matters here; the geolocation columns are ignored.

The feed carries a handful of IANA special-use prefixes -- the IPv4 TEST-NET
blocks and several IPv6 documentation/benchmarking/6to4 ranges -- geolocated
to Vultr sites. Whatever their purpose in the feed, they are not Vultr tenant
space and listing them would suppress alerts far outside the provider, so
anything that is not globally routable address space is dropped with a logged
warning naming the prefix. The filter only ever removes what the source
published; it never adds anything.

Note this is general-purpose rented compute: the tenant behind any given
address changes constantly and an attacker can simply rent one. The list
recognises that an address belongs to the provider; it is NOT grounds for
treating traffic as benign.
"""

import ipaddress
import logging

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = "https://geofeed.constant.com/"


# ipaddress.is_global consults a stdlib table of special-use ranges that has
# changed across Python versions: CPython 3.8 has no 6to4 entry, so is_global
# reports 2002::/16 as globally routable there and this list would have claimed
# the whole 6to4 range. Upstream CI runs 3.8, so the check cannot rely on the
# stdlib table alone. These are IANA registry constants, not provider data --
# nothing here describes Vultr's address space.
EXTRA_SPECIAL_USE = (
    "2002::/16",  # 6to4 (RFC 3056), absent from the 3.8 special-use table
)


def is_globally_routable(network):
    if not network.is_global:
        return False
    for special in EXTRA_SPECIAL_USE:
        block = ipaddress.ip_network(special)
        if block.version == network.version and network.subnet_of(block):
            return False
    return True


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
            network = ipaddress.ip_network(prefix)
        except ValueError as exc:
            logging.warning("Skipping malformed prefix %s: %s", prefix, exc)
            continue
        if not is_globally_routable(network):
            logging.warning(
                "Skipping non-globally-routable prefix %s: IANA special-use "
                "space is not Vultr tenant space",
                prefix,
            )
            continue
        networks.append(prefix)
    return networks


def main():
    response = download(URL)
    response.raise_for_status()

    networks = parse_geofeed(response.text)
    if not networks:
        raise Exception("No Vultr prefixes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known Vultr IP address ranges",
        "version": get_version(),
        "description": (
            "Vultr (Constant Company, LLC) IP address ranges, from their "
            "published RFC 8805 geofeed ({}). This is general-purpose rented "
            "compute: the tenant behind any given address changes constantly "
            "and an attacker can simply rent one. The list recognises that an "
            "address belongs to the provider; it is NOT grounds for treating "
            "traffic as benign.".format(URL)
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
    write_to_file(warninglist, "vultr")


if __name__ == "__main__":
    main()
