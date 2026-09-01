#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the IBM Cloud warninglist from the RIPEstat Data API.

Tier: RIPEstat by ASN (tier 2). IBM Cloud publishes no machine-readable
address-space endpoint that can be fetched without authentication. The
documented ip-ranges JSON under cloud.ibm.com redirects to a login page
(https://cloud.ibm.com/docs-content/v1/content/ip-ranges.json -> /login), no
RFC 8805 geofeed is served at ibm.com, www.softlayer.com or cloud.ibm.com, and
there is no public IBM-Cloud/ip-ranges repository. The prefixes are therefore
taken from what IBM Cloud's own autonomous systems announce in BGP:

    https://stat.ripe.net/data/announced-prefixes/data.json?resource=AS<n>

Scope: the SOFTLAYER-handle ASN family only. IBM Cloud runs on the network it
acquired with SoftLayer, and those are the autonomous systems that carry the
rented cloud fleet. IBM also holds a great deal of *corporate* address space
under separate autonomous systems (AS163 IBM-RESEARCH-AS, AS1747 IBMWATSON-AS,
AS3059 IBMCANAS, AS19604 IBM-RALEIGH-CL and many more). None of that is cloud
capacity and none of it is included here; a warninglist entry for an IBM office
network would say something quite different from "this is rented compute".

Holder verification happens at runtime, for every ASN, before its prefixes are
used. Each AS must still be named "IBM Cloud" by RIPE's as-names data call and
must still publish an @softlayer.com abuse contact -- softlayer.com, not
ibm.com, is the domain IBM Cloud's network objects actually carry. If either
check fails the generator raises rather than quietly listing address space that
now belongs to somebody else.

A minority of the prefixes AS36351 announces are registered to third parties
rather than to IBM Cloud -- 89.38.54.0/24, for instance, sits inside a RIPE
block registered to PC Hardware SRL. These are customer / bring-your-own-IP
ranges routed out of IBM Cloud's autonomous system, and they are deliberately
kept: operationally the traffic leaves IBM Cloud infrastructure, which is
exactly what this list is meant to recognise. Note also that announced-prefixes
reports what was visible over a rolling window of roughly two weeks, so an
entry can lag current routing slightly.

Semantics caveat: this is general-purpose rented compute. The tenant behind any
given address changes constantly and an attacker can simply rent one. The list
recognises that an address belongs to the provider; it is NOT grounds for
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

# The autonomous systems making up the IBM Cloud (ex-SoftLayer) fleet, as
# returned by RIPEstat's searchcomplete data call for the terms "SOFTLAYER"
# and "SOFTLAYER-". Every one of these is re-verified at runtime against the
# strings below; nothing here is taken on trust.
IBM_CLOUD_ASNS = [36351, 46702, 46703, 46704]

# The as-names holder string every one of the above must still contain, and the
# abuse-contact domain that must corroborate it.
EXPECTED_HOLDER = "IBM Cloud"
EXPECTED_HANDLE_PREFIX = "SOFTLAYER"
EXPECTED_ABUSE_DOMAIN = "@softlayer.com"


def ripestat(call, resource):
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def as_name(asn):
    """The '<HANDLE> - <holder>' string RIPE records for an AS."""
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    return names.get(str(asn), "")


def abuse_contacts(asn):
    return ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]


def verify_holder(asn):
    """Raise unless AS<asn> is still held by IBM Cloud.

    Both halves have to hold: the RIPE name has to carry the SOFTLAYER handle
    and the IBM Cloud holder, and the abuse contact has to corroborate it with
    an @softlayer.com address. Failing loudly is the point -- an AS that has
    changed hands would otherwise silently drag a stranger's address space into
    a list that says "IBM Cloud".
    """
    name = as_name(asn)
    if EXPECTED_HOLDER not in name or not name.startswith(EXPECTED_HANDLE_PREFIX):
        raise Exception(
            "AS{} is named {!r}, which no longer looks like {} {}; refusing to "
            "list its prefixes as IBM Cloud".format(
                asn, name, EXPECTED_HANDLE_PREFIX, EXPECTED_HOLDER
            )
        )

    contacts = abuse_contacts(asn)
    corroborated = False
    for email in contacts:
        if EXPECTED_ABUSE_DOMAIN in email:
            corroborated = True
            break
    if not corroborated:
        raise Exception(
            "AS{} ({}) publishes abuse contacts {} -- none on {}; refusing to "
            "list its prefixes as IBM Cloud".format(
                asn, name, contacts, EXPECTED_ABUSE_DOMAIN
            )
        )

    logging.info("AS%d verified: %s, abuse %s", asn, name, contacts)
    print("AS{} verified: {} (abuse: {})".format(asn, name, ", ".join(contacts)))


def get_networks_for_asn(asn):
    prefixes = ripestat("announced-prefixes", "AS{}".format(asn))
    return [entry["prefix"] for entry in prefixes["data"]["prefixes"]]


def valid_networks(prefixes):
    networks = []
    for prefix in prefixes:
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
    for asn in IBM_CLOUD_ASNS:
        verify_holder(asn)

        sleep(0.5)  # be gentle with the API between requests
        prefixes = get_networks_for_asn(asn)
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            # The per-datacentre SOFTLAYER ASNs are dormant in this way.
            print("AS{} announces no prefixes".format(asn))
            continue
        networks.update(valid_networks(prefixes))
        sleep(0.5)

    if not networks:
        raise Exception("No IBM Cloud prefixes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known IBM Cloud IP address ranges",
        "version": get_version(),
        "description": (
            "IBM Cloud (ex-SoftLayer) IP address ranges, from the prefixes "
            "announced by its autonomous systems {} as reported by the RIPEstat "
            "Data API (https://stat.ripe.net/data/announced-prefixes/data.json). "
            "IBM publishes no unauthenticated machine-readable endpoint for "
            "these. Scoped to the SOFTLAYER-handle cloud fleet; IBM corporate "
            "address space is deliberately excluded. A minority of the "
            "announced prefixes are registered to third parties: those are "
            "customer / bring-your-own-IP ranges routed out of IBM Cloud's "
            "autonomous system and are kept on purpose. This is general-purpose "
            "rented compute: the tenant behind any given address changes "
            "constantly and an attacker can simply rent one. The list "
            "recognises that an address belongs to the provider; it is NOT "
            "grounds for treating traffic as benign.".format(
                ", ".join("AS{}".format(asn) for asn in IBM_CLOUD_ASNS)
            )
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
    write_to_file(warninglist, "ibm-cloud")


if __name__ == "__main__":
    main()
