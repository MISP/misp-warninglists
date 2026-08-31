#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Akamai warninglist from the RIPEstat Data API.

This generator previously used api.bgpview.io, which stopped resolving
(NXDOMAIN), freezing lists/akamai/list.json at version 20240422. RIPEstat
provides the same three primitives, so the original logic is preserved:

  1. search for autonomous systems whose handle starts with AKAMAI
     -> data call "searchcomplete"
  2. keep only those whose abuse contact is an @akamai.com address
     -> data call "abuse-contact-finder"
  3. collect the prefixes each surviving AS announces
     -> data call "announced-prefixes"

One capability does not carry over. bgpview's search also returned prefixes
matching the search term directly, and the generator added those whose own
abuse contact was @akamai.com even when no Akamai AS announced them.
RIPEstat's searchcomplete has no prefix category, so prefixes registered to
Akamai but announced by somebody else are no longer picked up. In practice the
announced prefixes of the Akamai ASNs are the substantive coverage.
"""

import json
from time import sleep
from typing import List

from generator import (
    consolidate_networks,
    download,
    get_abspath_list_file,
    get_abspath_source_file,
    get_version,
    write_to_file,
)

RIPESTAT = "https://stat.ripe.net/data/{call}/data.json?resource={resource}"

# Autonomous systems that pass both checks below but should still be left out.
# Empty by default: this mirrors the behaviour the generator has always had.
#
# The obvious candidate for this dict is AS63949 (AKAMAI-LINODE-AP, "Akamai
# Connected Cloud"). It is genuinely Akamai -- they acquired Linode -- and it
# passes both tests, but it is general-purpose VPS space that anyone can rent by
# the hour, not CDN edge capacity. It contributes roughly 1.36 million IPv4
# addresses, and the list this generator replaces contained none of them.
# Suppressing alerts across rentable VPS space is a different risk from
# suppressing them across a CDN, so the choice is left to the maintainers rather
# than made here.
EXCLUDED_ASNS = {}

# If the search stops returning these, something changed upstream and the list
# would silently lose most of its coverage. Fail instead.
EXPECTED_ASNS = {16625, 20940, 21342}


def ripestat(call: str, resource) -> dict:
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def search_asns(term: str) -> List[dict]:
    """Autonomous systems suggested for a search term, as {asn, name} dicts."""
    data = ripestat("searchcomplete", term)["data"]

    asns = []
    for category in data["categories"]:
        if category["category"] != "ASNs":
            continue
        for suggestion in category["suggestions"]:
            # "AS20940" -> 20940; description is "<HANDLE> <holder>".
            asns.append(
                {
                    "asn": int(suggestion["value"].lstrip("ASas")),
                    "name": suggestion["description"],
                }
            )
    return asns


def has_akamai_abuse_contact(asn: int) -> bool:
    """Whether the AS publishes an @akamai.com abuse contact."""
    contacts = ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]
    for email in contacts:
        if "@akamai.com" in email:
            return True
    return False


def is_akamai(candidate: dict) -> bool:
    if not candidate["name"].startswith("AKAMAI"):
        return False
    return has_akamai_abuse_contact(candidate["asn"])


def get_networks_for_asn(asn: int) -> List[str]:
    temp_file = get_abspath_source_file("ripestat-asn-{}".format(asn))

    try:
        prefixes = json.load(open(temp_file, "r"))
    except Exception:
        sleep(0.5)  # be gentle with the API between requests
        prefixes = ripestat("announced-prefixes", asn)
        json.dump(prefixes, open(temp_file, "w"))

    return [entry["prefix"] for entry in prefixes["data"]["prefixes"]]


def existing_entries() -> List[str]:
    try:
        with open(get_abspath_list_file("akamai")) as data_file:
            return json.load(data_file)["list"]
    except (IOError, OSError, ValueError, KeyError):
        return []


def main():
    candidates = search_asns("AKAMAI")
    found = {candidate["asn"] for candidate in candidates}
    missing = EXPECTED_ASNS - found
    if missing:
        raise Exception(
            "RIPEstat searchcomplete did not return the core Akamai ASNs {}; "
            "refusing to regenerate the list from an incomplete search".format(
                sorted(missing)
            )
        )

    networks = set()
    for candidate in candidates:
        asn = candidate["asn"]
        if asn in EXCLUDED_ASNS:
            print("Skipping AS{}: {}".format(asn, EXCLUDED_ASNS[asn]))
            continue
        if not is_akamai(candidate):
            continue

        prefixes = get_networks_for_asn(asn)
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            print("AS{} announces no prefixes".format(asn))
            continue
        networks.update(prefixes)

    if not networks:
        raise Exception("No Akamai prefixes found, refusing to write an empty list")

    # Keep whatever the list already held. The address space an AS announces
    # today is a snapshot, and a prefix that has merely stopped being announced
    # for a while is still worth recognising. Note the tension: a range Akamai
    # has genuinely given up stays here too, and a stale CDN entry suppresses
    # real alerts once the space is reassigned. The PR reports how much of the
    # previous list the fresh data no longer covers so that can be judged.
    networks.update(existing_entries())

    warninglist = {
        "name": "List of known Akamai IP ranges",
        "version": get_version(),
        "description": "Akamai IP ranges from BGP search",
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
    write_to_file(warninglist, "akamai")


if __name__ == "__main__":
    main()
