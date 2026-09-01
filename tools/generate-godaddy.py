#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the GoDaddy warninglist from the RIPEstat Data API.

Tier 2 (RIPEstat by ASN). GoDaddy publishes no machine-readable address-space
endpoint: geofeed.godaddy.com and ip-ranges.godaddy.com do not resolve,
https://www.godaddy.com/geofeed answers 403 with an HTML bot page, and the
ARIN registrations of their space (for example NET-97-74-0-0-1 and
132.148.0.0/16) carry no RFC 9092 "geofeed" remark. So the address space is
collected from what their autonomous systems announce:

    https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS<n>

The ASNs are pinned below rather than discovered at run time. RIPEstat's
"searchcomplete" data call truncates its answer at ~41 suggestions, and for
GoDaddy it omitted AS26496 -- their single largest hosting ASN -- under both
"GODADDY" and "GO-DADDY". A search-driven generator would therefore silently
lose most of the coverage. Instead every pinned ASN is verified at run time
against the registries, and the generator fails loudly if a holder no longer
matches, so the pin can never end up listing somebody else's space.

Scope: the announced space of the GoDaddy.com, LLC ASNs (ARIN) and of the
GoDaddy Host Europe GmbH ASNs (RIPE), which is GoDaddy's EMEA hosting arm.
That is hosting/network space; GoDaddy's registrar and corporate systems live
inside the same autonomous systems and cannot be separated out by ASN. Domain
registration data itself is not address space and is out of scope.

Semantics caveat: this is general-purpose rented compute: the tenant behind
any given address changes constantly and an attacker can simply rent one. The
list recognises that an address belongs to the provider; it is NOT grounds for
treating traffic as benign.
"""

import ipaddress
import logging
from time import sleep

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

RIPESTAT = "https://stat.ripe.net/data/{call}/data.json?resource={resource}"

# An AS is accepted only if its registry holder name contains this substring
# (case-insensitively) AND one of its abuse contacts sits in one of the
# domains below. GoDaddy's EMEA hosting entity still publishes Host Europe
# abuse addresses; AS21501 is the mirror-image anomaly (a Host Europe holder
# name with an @godaddy.com abuse contact), which the "or" covers.
EXPECTED_HOLDER_SUBSTRING = "GODADDY"
EXPECTED_ABUSE_DOMAINS = ("@godaddy.com", "@hosteurope.de")

# Pinned autonomous systems, enumerated on 2026-08-31 from
#   - ARIN RDAP https://rdap.arin.net/registry/entity/GODAD  ("autnums")
#   - RIPEstat searchcomplete for "GODADDY" (the RIPE/Host Europe entity)
# Every one of them is re-verified against as-names and abuse-contact-finder
# on each run; an AS that announces nothing today is normal and is kept in the
# pin so that space reappearing later is picked up.
ASNS = (
    # ARIN, GoDaddy.com, LLC
    16892, 26496,
    31815,  # MEDIATEMPLE, the Media Temple hosting brand, held by GoDaddy
    397513, 397514, 397515, 397516, 397517, 397518, 397519, 397520, 397521,
    397522,
    398101, 398102, 398103, 398104, 398105, 398106, 398107, 398108, 398109,
    398110,
    398785, 398786, 398787, 398788, 398789, 398790, 398791, 398792, 398793,
    398794,
    400746, 400747, 400748, 400749, 400750, 400751, 400752, 400753, 400754,
    400755,
    # RIPE, GoDaddy Host Europe GmbH
    15891, 20773, 21499, 21501, 31100, 34289, 34440, 35329, 39779, 43788,
    44273, 44497, 50932, 60253,
    # APNIC
    133882,
)


def ripestat(call, resource):
    sleep(0.5)  # be gentle with the API between requests
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def get_as_name(asn):
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    name = names.get(str(asn))
    if not name:
        raise Exception(
            "RIPEstat returned no holder name for AS{}; refusing to use its "
            "prefixes".format(asn)
        )
    return name


def get_abuse_contacts(asn):
    contacts = ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]
    if not contacts:
        raise Exception(
            "RIPEstat returned no abuse contact for AS{}; refusing to use its "
            "prefixes".format(asn)
        )
    return contacts


def verify_holder(asn):
    """Fail loudly unless AS<asn> is still held by GoDaddy.

    Returns the evidence (holder name and abuse contacts) so it can be logged.
    """
    name = get_as_name(asn)
    if EXPECTED_HOLDER_SUBSTRING not in name.upper():
        raise Exception(
            "AS{} is held by '{}', which does not contain '{}'; the pinned ASN "
            "list is stale and would list somebody else's address "
            "space".format(asn, name, EXPECTED_HOLDER_SUBSTRING)
        )

    contacts = get_abuse_contacts(asn)
    corroborated = False
    for email in contacts:
        for domain in EXPECTED_ABUSE_DOMAINS:
            if email.lower().endswith(domain):
                corroborated = True
    if not corroborated:
        raise Exception(
            "AS{} ('{}') publishes abuse contacts {}, none of them in {}; "
            "refusing to list its address space".format(
                asn, name, contacts, list(EXPECTED_ABUSE_DOMAINS)
            )
        )

    return name, contacts


def get_prefixes_for_asn(asn):
    data = ripestat("announced-prefixes", "AS{}".format(asn))["data"]
    return [entry["prefix"] for entry in data["prefixes"]]


def main():
    networks = set()

    for asn in ASNS:
        name, contacts = verify_holder(asn)
        logging.info(
            "AS%d verified: holder '%s', abuse contacts %s", asn, name, contacts
        )

        prefixes = get_prefixes_for_asn(asn)
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            logging.info("AS%d announces no prefixes", asn)
            continue

        for prefix in prefixes:
            try:
                # strict=True: a prefix with host bits set is ambiguous, and
                # the only way to accept one is to widen it to its enclosing
                # network, which would suppress alerts for addresses nobody
                # claimed.
                ipaddress.ip_network(prefix)
            except ValueError as exc:
                logging.warning(
                    "Skipping malformed prefix %s from AS%d: %s", prefix, asn, exc
                )
                continue
            networks.add(prefix)

    if not networks:
        raise Exception("No GoDaddy prefixes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known GoDaddy IP address ranges",
        "version": get_version(),
        "description": (
            "GoDaddy IP address ranges, collected from the prefixes announced "
            "by the autonomous systems of GoDaddy.com, LLC and GoDaddy Host "
            "Europe GmbH, via the RIPEstat Data API "
            "(https://stat.ripe.net/data/announced-prefixes/data.json). Note "
            "this is general-purpose rented compute: the tenant behind any "
            "given address changes constantly and an attacker can simply rent "
            "one. The list recognises that an address belongs to the provider; "
            "it is NOT grounds for treating traffic as benign."
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
    write_to_file(warninglist, "godaddy")


if __name__ == "__main__":
    main()
