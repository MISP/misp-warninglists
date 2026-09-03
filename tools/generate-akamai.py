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

import ipaddress
import json
import logging
from time import sleep
from typing import List

import requests

from generator import (
    consolidate_networks,
    download,
    get_abspath_list_file,
    get_abspath_source_file,
    get_version,
    write_to_file,
)

RIPESTAT = "https://stat.ripe.net/data/{call}/data.json?resource={resource}"
REQUEST_DELAY = 1.0
MAX_REQUEST_ATTEMPTS = 5
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

# Autonomous systems that pass both checks below but are still left out.
#
# AS63949 (AKAMAI-LINODE-AP, "Akamai Connected Cloud") is genuinely Akamai --
# they acquired Linode -- and it passes both the name and the abuse-contact
# test. But it is general-purpose VPS space that anyone can rent by the hour,
# not CDN edge capacity, and suppressing alerts across rentable hosting is a
# different risk from suppressing them across a CDN: the tenant behind any
# given address changes constantly, and an attacker can simply buy one.
#
# Linode's address space is still recognisable through lists/linode, which is
# generated from Linode's own published geofeed and carries the semantics of
# "this is rented compute" rather than "this is CDN edge".
EXCLUDED_ASNS = {
    63949: "AKAMAI-LINODE-AP / Akamai Connected Cloud is rentable VPS hosting, "
           "not CDN edge capacity",
}

# If the search stops returning these, something changed upstream and the list
# would silently lose most of its coverage. Fail instead.
EXPECTED_ASNS = {16625, 20940, 21342}


def ripestat(call: str, resource) -> dict:
    """Fetch a RIPEstat response, pacing and retrying transient failures."""
    url = RIPESTAT.format(call=call, resource=resource)

    for attempt in range(MAX_REQUEST_ATTEMPTS):
        # searchcomplete and abuse-contact-finder used to be sent back-to-back.
        # Pace *all* RIPEstat calls, rather than only prefix lookups, so a fresh
        # run does not trip the service's traffic limits.
        sleep(REQUEST_DELAY)
        try:
            response = download(url)
            if response.status_code not in RETRYABLE_STATUS_CODES:
                response.raise_for_status()
                return response.json()

            error = "HTTP {}".format(response.status_code)
            retry_after = response.headers.get("Retry-After")
        except requests.exceptions.RequestException as exc:
            error = str(exc)
            retry_after = None

        if attempt == MAX_REQUEST_ATTEMPTS - 1:
            raise RuntimeError(
                "RIPEstat request failed after {} attempts: {} ({})".format(
                    MAX_REQUEST_ATTEMPTS, url, error
                )
            )

        try:
            delay = float(retry_after) if retry_after is not None else 2 ** attempt
        except ValueError:
            delay = 2 ** attempt
        logging.warning(
            "RIPEstat request failed (%s); retrying in %.1f seconds",
            error,
            delay,
        )
        sleep(delay)

    raise AssertionError("unreachable")


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
        prefixes = ripestat("announced-prefixes", asn)
        json.dump(prefixes, open(temp_file, "w"))

    return [entry["prefix"] for entry in prefixes["data"]["prefixes"]]


def existing_entries() -> List[str]:
    try:
        with open(get_abspath_list_file("akamai")) as data_file:
            return json.load(data_file)["list"]
    except (IOError, OSError, ValueError, KeyError):
        return []


def drop_excluded(networks):
    """Remove entries that lie wholly inside an excluded AS's address space.

    Only wholly-contained entries go. A large aggregate that merely *contains*
    some excluded space is kept intact -- 104.64.0.0/10 is Akamai's own block
    and stays Akamai's even though AS63949 announces a few prefixes inside it.
    Subtracting those out would shatter one meaningful entry into dozens of
    fragments to no benefit.
    """
    if not EXCLUDED_ASNS:
        return networks

    announced = []
    for asn in EXCLUDED_ASNS:
        for prefix in get_networks_for_asn(asn):
            try:
                announced.append(ipaddress.ip_network(prefix))
            except ValueError:
                continue
    if not announced:
        return networks

    # Collapse before testing. An AS commonly announces one block as several
    # adjacent prefixes, while the committed list carries the aggregate --
    # 139.162.0.0/16 is a subnet of no single AS63949 announcement, but it is
    # exactly the union of them, and it is plainly Linode space.
    excluded = list(
        ipaddress.collapse_addresses([n for n in announced if n.version == 4])
    )
    excluded += list(
        ipaddress.collapse_addresses([n for n in announced if n.version == 6])
    )

    kept = set()
    for entry in networks:
        try:
            network = ipaddress.ip_network(entry)
        except ValueError:
            continue
        inside = False
        for block in excluded:
            if block.version == network.version and network.subnet_of(block):
                inside = True
                break
        if not inside:
            kept.add(entry)

    dropped = len(networks) - len(kept)
    if dropped:
        logging.info(
            "Dropped %d entries falling inside excluded ASNs %s",
            dropped,
            sorted(EXCLUDED_ASNS),
        )
    return kept


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
    # real alerts once the space is reassigned.
    networks.update(existing_entries())

    # Excluding an AS has to subtract, not merely skip. Entries carried over
    # from the committed list were added before the exclusion existed, so
    # without this the exclusion would be a no-op on every run after the first.
    networks = drop_excluded(networks)

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
