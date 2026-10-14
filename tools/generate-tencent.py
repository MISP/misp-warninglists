#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Tencent Cloud warninglist from the RIPEstat Data API.

Tier 2 source: BGP data, because there is no tier 1 vendor endpoint.
Tencent publishes no machine-readable address-space file. www.tencentcloud.com
answers /ip-ranges.json (and every other path) with a JavaScript anti-bot page
rather than JSON, intl.cloud.tencent.com/ip-ranges.json is a 404, the "IP and
IP Ranges" documentation page (product 215, doc 35529) only discusses private
VPC CIDR blocks in prose, and no geofeed remark (RFC 9092) is registered for
their address space. So the address space is derived from what Tencent's
autonomous systems announce:

  1. search for autonomous systems matching TENCENT
     -> data call "searchcomplete"
  2. keep only those whose holder name still matches and whose abuse contact
     is still a Tencent address
     -> data calls "as-names" and "abuse-contact-finder"
  3. collect the prefixes each surviving AS announces
     -> data call "announced-prefixes"

Both verification steps run at generation time and the run FAILS LOUDLY if a
core ASN no longer checks out, rather than quietly listing whatever address
space the number has been reassigned to.

Semantics caveat: this is general-purpose rented compute. The tenant behind
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

SEARCH_TERM = "TENCENT"

# Expected holder evidence. An AS has to satisfy both to be listed: RIPEstat's
# holder name has to contain EXPECTED_HOLDER_NAME, and at least one published
# abuse contact has to sit under EXPECTED_ABUSE_DOMAIN.
#
# The abuse domain is deliberately "@tencent." and not "@tencent.com", so the
# regional Tencent entities are included too -- AS137876 (Tencent Thailand)
# publishes ITNetworkSecurityGroup@tencent.co.th. That is still Tencent's own
# rented compute, and the list's semantics is "this address belongs to the
# provider", not an endorsement of the traffic.
#
# The pair also rejects near misses: AS9390 carries the TENCENT-NET-AP holder
# name but its abuse contact is ipas@cnnic.cn (the registry, not Tencent), so
# the contact test drops it.
EXPECTED_HOLDER_NAME = "TENCENT"
EXPECTED_ABUSE_DOMAIN = "@tencent."

# The autonomous systems carrying the substantive coverage. If the search or
# the verification stops returning any of these, something changed upstream
# and the list would silently lose most of its address space. Fail instead.
EXPECTED_ASNS = {45090, 132203, 132591, 133478}


def ripestat(call, resource):
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    sleep(0.5)  # be gentle with the API between requests
    return response.json()


def search_asns(term):
    """Autonomous systems suggested for a search term, as a list of ints."""
    data = ripestat("searchcomplete", term)["data"]

    asns = []
    for category in data["categories"]:
        if category["category"] != "ASNs":
            continue
        for suggestion in category["suggestions"]:
            # "AS132203" -> 132203
            asns.append(int(suggestion["value"].lstrip("ASas")))
    return sorted(set(asns))


def get_holder_name(asn):
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    return names.get(str(asn), "")


def get_abuse_contacts(asn):
    return ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]


def is_tencent(asn):
    """Whether AS<asn> still verifies as Tencent, on both name and contact."""
    name = get_holder_name(asn)
    if EXPECTED_HOLDER_NAME not in name.upper():
        logging.info(
            "AS%d holder %r does not match %r, skipping",
            asn,
            name,
            EXPECTED_HOLDER_NAME,
        )
        return False

    contacts = get_abuse_contacts(asn)
    for email in contacts:
        if EXPECTED_ABUSE_DOMAIN in email.lower():
            print("AS{} verified: {} / {}".format(asn, name, ", ".join(contacts)))
            return True

    logging.info(
        "AS%d holder %r matches but abuse contacts %s are not under %r, skipping",
        asn,
        name,
        contacts,
        EXPECTED_ABUSE_DOMAIN,
    )
    return False


def get_networks_for_asn(asn):
    prefixes = ripestat("announced-prefixes", asn)["data"]["prefixes"]
    return [entry["prefix"] for entry in prefixes]


def validated(prefixes):
    """Keep only well-formed CIDR prefixes, warning about the rest.

    strict=True is the default and stays that way: a prefix with host bits set
    is ambiguous, and the only way to accept one is to widen it to its
    enclosing network, which would suppress alerts for addresses nobody
    claimed. consolidate_networks() would also raise on such a string, so the
    filtering has to happen here.
    """
    networks = []
    for prefix in prefixes:
        try:
            ipaddress.ip_network(prefix)
        except ValueError as exc:
            logging.warning("Skipping malformed prefix %s: %s", prefix, exc)
            continue
        networks.append(prefix)
    return networks


def main():
    candidates = search_asns(SEARCH_TERM)
    if not candidates:
        raise Exception(
            "RIPEstat searchcomplete returned no ASNs for {}; refusing to "
            "regenerate the list from an empty search".format(SEARCH_TERM)
        )

    verified = set()
    networks = set()
    for asn in candidates:
        if not is_tencent(asn):
            continue
        verified.add(asn)

        prefixes = get_networks_for_asn(asn)
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            print("AS{} announces no prefixes".format(asn))
            continue
        networks.update(validated(prefixes))

    missing = EXPECTED_ASNS - verified
    if missing:
        raise Exception(
            "Expected Tencent ASNs {} did not verify as Tencent (holder name "
            "containing {!r} and an abuse contact under {!r}); refusing to "
            "regenerate the list".format(
                sorted(missing), EXPECTED_HOLDER_NAME, EXPECTED_ABUSE_DOMAIN
            )
        )

    if not networks:
        raise Exception(
            "No Tencent Cloud prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known Tencent Cloud IP address ranges",
        "version": get_version(),
        "description": (
            "Tencent Cloud IP address ranges, from the prefixes announced by "
            "Tencent's autonomous systems as reported by the RIPEstat Data "
            "API (https://stat.ripe.net/). Tencent publishes no machine-"
            "readable address-space file, so the address space is derived from "
            "BGP. This is general-purpose rented compute: the tenant behind "
            "any given address changes constantly and an attacker can simply "
            "rent one. The list recognises that an address belongs to the "
            "provider; it is NOT grounds for treating traffic as benign."
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
    write_to_file(warninglist, "tencent-cloud")


if __name__ == "__main__":
    main()
