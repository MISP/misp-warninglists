#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Leaseweb warninglist from the RIPEstat Data API.

Tier: RIPEstat by ASN (tier 2). Leaseweb publishes no machine-readable
address-space feed of its own. Checked at build time, all negative:

  * geofeed.leaseweb.com does not resolve (NXDOMAIN);
  * https://leaseweb.com/.well-known/geofeed returns the website's HTML
    single-page-app shell, not an RFC 8805 feed;
  * www.leaseweb.com/geofeed.csv, /geo/google.csv, /ip-ranges.json and
    api.leaseweb.com/ip-ranges all return 404;
  * none of the 138 inetnum objects maintained by LEASEWEB-NL-MNT in the
    RIPE database carries a "geofeed:" attribute, so RFC 9632 discovery
    finds nothing either.

So the address space is derived from BGP instead, following the same three
steps as the Akamai generator:

  1. ask RIPEstat "searchcomplete" which autonomous systems match LEASEWEB
     -- the ASNs are discovered at runtime, never hardcoded from memory;
  2. verify each candidate really is Leaseweb, via "as-names" (the holder
     string must contain LEASEWEB) and "abuse-contact-finder" (the abuse
     mailbox must sit under leaseweb.com);
  3. collect the prefixes each surviving AS announces, via
     "announced-prefixes".

Leaseweb is a multi-entity group -- Leaseweb Netherlands, USA, Deutschland,
UK, Singapore, Hong Kong, Japan, Australia -- each with its own ASNs and its
own regional abuse mailbox (abuse@nl.leaseweb.com, abuse@us.leaseweb.com,
...), which is why the abuse check accepts any subdomain of leaseweb.com.

Five ASNs held by "LeaseWeb Network B.V." (AS16265, AS60626, AS202134,
AS203774, AS203928) publish abuse@fiberring.com -- Fiberring being the
company Leaseweb's network entity grew out of -- so they fail the abuse
gate and are logged as skipped. That costs no coverage: every one of them
announces zero prefixes today.

SEMANTICS CAVEAT. This is general-purpose rented compute: the tenant behind
any given address changes constantly and an attacker can simply rent one.
The list recognises that an address belongs to the provider; it is NOT
grounds for treating traffic as benign.
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

SEARCH_TERM = "LEASEWEB"

# An AS holder string must contain this (case-insensitive) to be accepted.
EXPECTED_HOLDER = "LEASEWEB"

# An AS abuse mailbox must sit under this domain to be accepted. Matched on
# the parsed domain part, as exactly the domain or a subdomain of it, so that
# a lookalike such as abuse@notleaseweb.com cannot pass.
EXPECTED_ABUSE_DOMAIN = "leaseweb.com"

# Multi-region anchors that carry the bulk of the address space. If the search
# stops returning one of these, or one of them stops verifying as Leaseweb,
# something changed upstream and the list would silently lose most of its
# coverage or gain somebody else's space. Fail instead of writing that.
# Smaller ASNs are discovered and gated at runtime without being pinned, so a
# single regional AS being retired does not break the generator.
EXPECTED_ASNS = frozenset([7203, 28753, 30633, 59253, 60781])


def ripestat(call, resource):
    sleep(0.5)  # be gentle with the API between requests
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def search_asns(term):
    """Autonomous systems suggested for a search term, as {asn, name} dicts."""
    data = ripestat("searchcomplete", term)["data"]

    asns = []
    for category in data["categories"]:
        if category["category"] != "ASNs":
            continue
        for suggestion in category["suggestions"]:
            # "AS60781" -> 60781; description is "<HANDLE> <holder>".
            asns.append(
                {
                    "asn": int(suggestion["value"].lstrip("ASas")),
                    "name": suggestion["description"],
                }
            )
    return asns


def get_holder(asn):
    """The registry holder string for an AS, or an empty string."""
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    for value in names.values():
        return value
    return ""


def has_leaseweb_abuse_contact(asn):
    """Whether the AS publishes an abuse mailbox under leaseweb.com."""
    contacts = ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]
    for email in contacts:
        if "@" not in email:
            continue
        domain = email.rsplit("@", 1)[1].strip().lower()
        if domain == EXPECTED_ABUSE_DOMAIN:
            return True
        if domain.endswith("." + EXPECTED_ABUSE_DOMAIN):
            return True
    return False


def is_leaseweb(asn):
    """Both holder gates. Logs why a candidate was rejected."""
    holder = get_holder(asn)
    if EXPECTED_HOLDER not in holder.upper():
        logging.warning(
            "Skipping AS%d: holder %r does not contain %r",
            asn,
            holder,
            EXPECTED_HOLDER,
        )
        return False
    if not has_leaseweb_abuse_contact(asn):
        logging.warning(
            "Skipping AS%d (%s): abuse contact is not under %s",
            asn,
            holder,
            EXPECTED_ABUSE_DOMAIN,
        )
        return False
    return True


def get_networks_for_asn(asn):
    prefixes = ripestat("announced-prefixes", "AS{}".format(asn))
    return [entry["prefix"] for entry in prefixes["data"]["prefixes"]]


def valid_networks(prefixes):
    """Keep only prefixes that parse as a strict CIDR."""
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
    candidates = search_asns(SEARCH_TERM)
    found = set()
    for candidate in candidates:
        found.add(candidate["asn"])

    missing = EXPECTED_ASNS - found
    if missing:
        raise Exception(
            "RIPEstat searchcomplete did not return the core Leaseweb ASNs "
            "{}; refusing to regenerate the list from an incomplete "
            "search".format(sorted(missing))
        )

    prefixes = set()
    verified = set()
    for candidate in candidates:
        asn = candidate["asn"]
        if not is_leaseweb(asn):
            if asn in EXPECTED_ASNS:
                raise Exception(
                    "AS{} is pinned as a core Leaseweb AS but no longer "
                    "verifies as Leaseweb; refusing to list address space "
                    "that may belong to somebody else".format(asn)
                )
            continue
        verified.add(asn)

        announced = get_networks_for_asn(asn)
        if not announced:
            # Perfectly normal: an allocated AS need not announce anything.
            logging.info("AS%d announces no prefixes", asn)
            continue
        prefixes.update(announced)

    logging.info(
        "Verified %d Leaseweb ASNs: %s", len(verified), sorted(verified)
    )

    networks = valid_networks(prefixes)
    if not networks:
        raise Exception(
            "No Leaseweb prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known Leaseweb IP address ranges",
        "version": get_version(),
        "description": (
            "Leaseweb IP address ranges, from the prefixes announced by the "
            "autonomous systems held by the Leaseweb group, as reported by "
            "the RIPEstat Data API (https://stat.ripe.net). Leaseweb "
            "publishes no address-space feed of its own. This is "
            "general-purpose rented compute: the tenant behind any given "
            "address changes constantly and an attacker can simply rent one. "
            "The list recognises that an address belongs to the provider; it "
            "is NOT grounds for treating traffic as benign."
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
    write_to_file(warninglist, "leaseweb")


if __name__ == "__main__":
    main()
