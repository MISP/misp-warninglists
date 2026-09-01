#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Rackspace warninglist from the RIPEstat Data API.

Tier 2 (RIPEstat by ASN). Rackspace publishes no machine-readable feed of its
own address space: there is no ip-ranges JSON, no RFC 8805 geofeed at
rackspace.com (/geofeed, /geo/google.csv, ip-ranges.rackspace.com and friends
all 404), and no geofeed: attribute on its registry objects. The only
documented address lists on docs.rackspace.com are narrow service subsets
(cloud load balancer source addresses, ServiceNet RFC 1918 space), not the
provider's public ranges. So the address space is derived from BGP instead:

  1. search for autonomous systems matching "RACKSPACE"
     -> data call "searchcomplete"
  2. verify each candidate really is Rackspace, at runtime
     -> data call "as-names"             (holder must contain RACKSPACE)
     -> data call "abuse-contact-finder" (must publish an @rackspace.com address)
  3. collect the prefixes each surviving AS announces
     -> data call "announced-prefixes"

Rackspace is a multi-entity operator -- the US parent plus RACKSPACE-LON
(Rackspace Ltd.), RACKSPACE-AUS, RACKSPACE-AP (Rackspace Hosting (Hong Kong))
and RACKSPACE-AS (Rackspace.com Sydney) -- so several distinct ASNs are in
scope and all of them are covered by the same two checks. Both checks are
required: the name test alone would admit unrelated holders that merely borrow
the word, and the abuse-contact test alone would admit anything Rackspace
happens to handle abuse for. Nothing whose holder name lacks RACKSPACE can
enter the list, which structurally excludes look-alike neighbours such as
"A100 ROW Inc" (an Amazon entity, not Rackspace).

If one of the ASNs pinned in EXPECTED_ASNS stops matching, the generator fails
loudly rather than quietly listing whoever holds the number now.

Semantics caveat -- this is general-purpose rented compute: the tenant behind
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

SEARCH_TERM = "RACKSPACE"

# What a genuine Rackspace autonomous system must look like. Both are required.
EXPECTED_HOLDER_SUBSTRING = "RACKSPACE"
EXPECTED_ABUSE_DOMAIN = "@rackspace.com"

# The autonomous systems that carry the substantive coverage. Each was
# confirmed against as-names and abuse-contact-finder when this generator was
# written; none is taken from memory or from documentation. If the search stops
# returning one, or one stops passing verification, the list would silently
# lose a whole region -- so that is an error, not a warning.
EXPECTED_ASNS = {
    10532,  # RACKSPACE - Rackspace Hosting
    12200,  # RACKSPACE - Rackspace Hosting
    15395,  # RACKSPACE-LON Rackspace Ltd.
    19994,  # RACKSPACE - Rackspace Hosting
    22720,  # RACKSPACE-AUS - Rackspace Hosting
    27357,  # RACKSPACE - Rackspace Hosting
    36248,  # RACKSPACE - Rackspace Hosting
    45187,  # RACKSPACE-AP - Rackspace IT Hosting, Hong Kong
    58683,  # RACKSPACE-AS - Rackspace.com Sydney
}


def ripestat(call, resource):
    sleep(0.5)  # be gentle with the API between requests
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def search_asns(term):
    """Autonomous systems suggested for a search term, as a sorted list of int."""
    data = ripestat("searchcomplete", term)["data"]

    asns = []
    for category in data["categories"]:
        if category["category"] != "ASNs":
            continue
        for suggestion in category["suggestions"]:
            # "AS27357" -> 27357
            asns.append(int(suggestion["value"].lstrip("ASas")))
    return sorted(set(asns))


def holder_name(asn):
    """The registered holder of an AS, as RIPEstat reports it."""
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    return names.get(str(asn), "")


def abuse_contacts(asn):
    return ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]


def verify(asn):
    """Whether AS<asn> is held by Rackspace, with the reason when it is not."""
    name = holder_name(asn)
    if EXPECTED_HOLDER_SUBSTRING not in name.upper():
        return False, "holder is {!r}, expected a name containing {!r}".format(
            name, EXPECTED_HOLDER_SUBSTRING
        )

    contacts = abuse_contacts(asn)
    for email in contacts:
        if EXPECTED_ABUSE_DOMAIN in email.lower():
            return True, "{} / {}".format(name, email)
    return False, "holder {!r} publishes no {} abuse contact (got {})".format(
        name, EXPECTED_ABUSE_DOMAIN, contacts
    )


def get_networks_for_asn(asn):
    prefixes = ripestat("announced-prefixes", asn)
    return [entry["prefix"] for entry in prefixes["data"]["prefixes"]]


def validate(prefixes):
    """Keep only prefixes that parse as a strict CIDR."""
    valid = []
    for prefix in prefixes:
        try:
            # strict=True: a prefix with host bits set is ambiguous, and the
            # only way to accept one is to widen it to its enclosing network,
            # which would suppress alerts for addresses nobody claimed.
            ipaddress.ip_network(prefix)
        except ValueError as exc:
            logging.warning("Skipping malformed prefix %s: %s", prefix, exc)
            continue
        valid.append(prefix)
    return valid


def main():
    candidates = search_asns(SEARCH_TERM)
    missing = EXPECTED_ASNS - set(candidates)
    if missing:
        raise Exception(
            "RIPEstat searchcomplete did not return the pinned Rackspace ASNs "
            "{}; refusing to regenerate the list from an incomplete "
            "search".format(sorted(missing))
        )

    networks = set()
    for asn in candidates:
        ok, reason = verify(asn)
        if not ok:
            if asn in EXPECTED_ASNS:
                raise Exception(
                    "AS{} is pinned as Rackspace but no longer verifies: {}. "
                    "Refusing to write a list that would either lose Rackspace "
                    "space or claim somebody else's".format(asn, reason)
                )
            logging.warning("Skipping AS%s: %s", asn, reason)
            continue

        print("AS{} verified: {}".format(asn, reason))
        prefixes = get_networks_for_asn(asn)
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            print("AS{} announces no prefixes".format(asn))
            continue
        networks.update(validate(prefixes))

    if not networks:
        raise Exception("No Rackspace prefixes found, refusing to write an empty list")

    warninglist = {
        "name": "List of known Rackspace IP address ranges",
        "version": get_version(),
        "description": (
            "Rackspace IP address ranges, from the prefixes announced by the "
            "Rackspace autonomous systems (RIPEstat announced-prefixes). Note "
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
    write_to_file(warninglist, "rackspace")


if __name__ == "__main__":
    main()
