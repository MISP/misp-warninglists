#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Salesforce warninglist.

Tier 1, vendor-published endpoint. Salesforce publishes the address space its
services are reachable from as an AWS-shaped JSON document:

    https://ip-ranges.salesforce.com/ip-ranges.json

The document carries a syncToken and a createDate, an "prefixes" array of
{region, provider, ip_prefix[]} objects and an "ipv6_prefixes" array of
{region, provider, ipv6_prefix[]} objects. Both families are collected into
this single list.

Semantics caveat: this is the inverse of the rented-compute case. The ranges
are fixed SaaS service endpoints -- the addresses Salesforce's own platform
serves from and calls out from -- not address space rented out to arbitrary
tenants whose identity changes over time. That makes it cleaner warninglist
material than a general-purpose hosting range: an address staying in this list
keeps meaning "Salesforce's service", rather than "somebody who rented a
machine from Salesforce today".
"""

import ipaddress
import logging

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = "https://ip-ranges.salesforce.com/ip-ranges.json"

# (top-level key, per-entry key) pairs holding the prefixes in the document.
PREFIX_KEYS = [
    ("prefixes", "ip_prefix"),
    ("ipv6_prefixes", "ipv6_prefix"),
]


def parse_ip_ranges(document):
    networks = []
    for group_key, prefix_key in PREFIX_KEYS:
        for entry in document.get(group_key, []):
            prefixes = entry.get(prefix_key, [])
            if isinstance(prefixes, str):
                prefixes = [prefixes]
            for prefix in prefixes:
                prefix = prefix.strip()
                if not prefix:
                    continue
                try:
                    # strict=True: a prefix with host bits set is ambiguous,
                    # and the only way to accept one is to widen it to its
                    # enclosing network, which would suppress alerts for
                    # addresses nobody claimed.
                    ipaddress.ip_network(prefix)
                except ValueError as exc:
                    logging.warning(
                        "Skipping malformed prefix %s: %s", prefix, exc
                    )
                    continue
                networks.append(prefix)
    return networks


def main():
    response = download(URL)
    response.raise_for_status()
    document = response.json()

    logging.info(
        "Salesforce ip-ranges.json syncToken=%s createDate=%s",
        document.get("syncToken"),
        document.get("createDate"),
    )

    networks = parse_ip_ranges(document)
    if not networks:
        raise Exception(
            "No Salesforce prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known Salesforce IP address ranges",
        "version": get_version(),
        "description": (
            "Salesforce IP address ranges, from their published ip-ranges "
            "endpoint ({}). These are fixed SaaS service endpoints rather "
            "than rentable compute, which makes them cleaner warninglist "
            "material: the addresses stay tied to Salesforce's own platform "
            "instead of to whichever tenant rented them today.".format(URL)
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
    write_to_file(warninglist, "salesforce")


if __name__ == "__main__":
    main()
