#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the parking-domain address warninglist.

Source: https://github.com/tma22-parking/tma22-parking.github.io
(parking_services.json) -- the indicator set published with "Domain Parking:
Largely Present, Rarely Considered!" (Zirngibl, Deusch, Sattler, Aulbach,
Carle and Jonker, TMA 2022). The same artefact backs generate-parking-domain-ns.py;
that script reads the NS indicators, this one reads the A and AAAA indicators,
which is what this list holds.

**That this is the right source is measured, not assumed: 66 of the 67
addresses the paper publishes are already committed here.** The list was built
from this artefact by hand; this generator makes that import reproducible.

**Consequently it adds nothing today, and that is the honest result.** No
public feed of parking-service address space exists. The alternative
considered -- resolving the parking CNAME targets live -- was rejected on
inspection: twenty of the paper's thirty-six CNAME targets are AWS ELB, ALB or
NLB names, whose addresses rotate between tenants. Unioning resolved addresses
from those would, over repeated runs, accumulate /32s that had since been
reassigned to unrelated AWS customers, and a warninglist entry does not merely
add noise -- it suppresses. That failure is structural, not something a filter
fixes, so it is not done here.

**Its limitation, same as its sibling: a 2022 research artefact is not a live
feed.** It does not grow when a new parking service appears. A successful run
means "the list matches the published evidence", not "the list is complete".

**This generator unions, it never replaces.** 42 committed addresses are not
in the paper and are kept untouched.

Individual IPv6 interface addresses are skipped. The artefact contains one
(a /128 inside an AWS eu-central-1 allocation): that is the address a host
happened to hold during the 2022 measurement, not an address range a parking
service was assigned, and it will have belonged to someone else since.
"""

import ipaddress
import json
import logging

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = (
    "https://raw.githubusercontent.com/tma22-parking/"
    "tma22-parking.github.io/main/parking_services.json"
)

DST = "parking-domain"

RECORD_TYPES = ("a", "aaaa")


def collect_networks(services):
    networks = set()
    for key, service in services.items():
        records = (service or {}).get("record_types") or {}
        for record_type in RECORD_TYPES:
            for indicator in records.get(record_type) or []:
                if isinstance(indicator, dict):
                    logging.warning(
                        "%s: skipping %s pattern indicator, not a fixed network: %s",
                        key, record_type.upper(), json.dumps(indicator),
                    )
                    continue
                value = str(indicator).strip()
                try:
                    network = ipaddress.ip_network(value, strict=True)
                except ValueError as exc:
                    logging.warning(
                        "%s: skipping unreadable %s indicator %s: %s",
                        key, record_type.upper(), value, exc,
                    )
                    continue
                if network.version == 6 and network.prefixlen == 128:
                    logging.info(
                        "%s: skipping single IPv6 interface address %s -- an "
                        "address a host held during the measurement, not an "
                        "allocation held by the parking service", key, network,
                    )
                    continue
                networks.add(str(network))
    return networks


def existing_warninglist():
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def main():
    response = download(URL)
    response.raise_for_status()

    services = response.json()
    if not isinstance(services, dict) or not services:
        raise Exception("Unexpected upstream shape: expected a JSON object of services")

    fetched = collect_networks(services)
    if not fetched:
        raise Exception(
            "No parking addresses found upstream, refusing to write an empty list"
        )

    warninglist = existing_warninglist()
    if warninglist is None:
        raise Exception(
            "lists/{}/list.json is missing; this generator maintains an "
            "existing curated list and will not create one from scratch".format(DST)
        )

    committed = set(warninglist.get("list", []))
    merged = committed.union(fetched)
    logging.info(
        "parking-domain: %d services, %d committed + %d published -> %d after "
        "union (%d new)",
        len(services), len(committed), len(fetched), len(merged),
        len(merged) - len(committed),
    )
    for network in sorted(fetched - committed):
        logging.info("parking-domain: new address range from the artefact: %s", network)

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
