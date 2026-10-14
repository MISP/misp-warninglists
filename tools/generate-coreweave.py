#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the CoreWeave warninglist from the RIPEstat Data API.

CoreWeave publishes no machine-readable list of its address space. There is no
ip-ranges JSON, no RFC 8805 geofeed (the ARIN RDAP record for their allocations
carries no geofeed remark either), and ipranges.coreweave.com does not resolve;
docs.coreweave.com/docs/ip-ranges exists but is behind a login wall and is a
prose page, not a feed. So this is a tier 2 generator: the address space is
derived from the prefixes CoreWeave's autonomous systems announce, via

    https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS<n>

The ASNs are pinned in ASNS below, but they are never trusted blindly. Every
run re-verifies each one against two independent RIPEstat data calls before a
single prefix is read from it:

  1. "as-names"            -> the holder string must still contain COREWEAVE
  2. "abuse-contact-finder" -> the abuse contact must still be @coreweave.com

If either check fails the generator raises rather than continuing, because a
reassigned ASN would otherwise quietly publish somebody else's address space
under CoreWeave's name.

Semantics caveat: this is general-purpose rented compute. The tenant behind any
given address changes constantly and an attacker can simply rent one. The list
recognises that an address belongs to the provider; it is NOT grounds for
treating traffic as benign.
"""

import ipaddress
import logging
from time import sleep
from typing import List

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

RIPESTAT = "https://stat.ripe.net/data/{call}/data.json?resource={resource}"

# Autonomous systems held by CoreWeave, Inc. Both are verified at runtime
# against the two expectations below before any of their prefixes are used.
ASNS = [33425, 46992]

# Expected holder evidence. EXPECTED_HOLDER is matched case-insensitively
# against the RIPEstat as-names string ("COREWEAVE - CoreWeave, Inc" and
# "COREWEAVE-CUSTOMER - CoreWeave, Inc" at the time of writing).
EXPECTED_HOLDER = "COREWEAVE"
EXPECTED_ABUSE_DOMAIN = "@coreweave.com"


def ripestat(call, resource):
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def verify_asn(asn):
    """Fail loudly unless the AS is still held by CoreWeave.

    Two independent signals have to agree: the registry holder name and the
    published abuse contact. Either one drifting means the pinned ASN is no
    longer the company's, and listing its announcements would mislabel a
    third party's address space as CoreWeave's.
    """
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    holder = names.get(str(asn), "")
    if EXPECTED_HOLDER.lower() not in holder.lower():
        raise Exception(
            "AS{} is held by {!r}, which does not contain {!r}; refusing to "
            "list its prefixes as CoreWeave's".format(asn, holder, EXPECTED_HOLDER)
        )

    contacts = ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]
    corroborated = False
    for email in contacts:
        if EXPECTED_ABUSE_DOMAIN in email.lower():
            corroborated = True
            break
    if not corroborated:
        raise Exception(
            "AS{} ({}) publishes abuse contacts {}, none of them {}; refusing "
            "to list its prefixes as CoreWeave's".format(
                asn, holder, contacts, EXPECTED_ABUSE_DOMAIN
            )
        )

    logging.info(
        "AS%d verified as CoreWeave: holder %r, abuse contacts %s",
        asn,
        holder,
        contacts,
    )
    return holder


def get_networks_for_asn(asn):
    # type: (int) -> List[str]
    prefixes = ripestat("announced-prefixes", "AS{}".format(asn))
    return [entry["prefix"] for entry in prefixes["data"]["prefixes"]]


def valid_networks(prefixes):
    # type: (List[str]) -> List[str]
    networks = []
    for prefix in prefixes:
        prefix = prefix.strip()
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
    networks = set()
    for asn in ASNS:
        verify_asn(asn)
        sleep(0.5)  # be gentle with the API between requests

        prefixes = valid_networks(get_networks_for_asn(asn))
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            # AS46992 (COREWEAVE-CUSTOMER) announces nothing today.
            logging.info("AS%d announces no prefixes", asn)
            continue
        networks.update(prefixes)
        sleep(0.5)

    if not networks:
        raise Exception("No CoreWeave prefixes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known CoreWeave IP address ranges",
        "version": get_version(),
        "description": (
            "CoreWeave IP address ranges, from the prefixes announced by the "
            "autonomous systems held by CoreWeave, Inc (AS33425, AS46992) as "
            "reported by the RIPEstat Data API. This is general-purpose rented "
            "compute: the tenant behind any given address changes constantly "
            "and an attacker can simply rent one. The list recognises that an "
            "address belongs to the provider; it is NOT grounds for treating "
            "traffic as benign."
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
    write_to_file(warninglist, "coreweave")


if __name__ == "__main__":
    main()
