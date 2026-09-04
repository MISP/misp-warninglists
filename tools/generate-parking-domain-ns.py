#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the parking-domain name server warninglist.

Source: https://github.com/tma22-parking/tma22-parking.github.io
(parking_services.json) -- the indicator set published alongside "Domain
Parking: Largely Present, Rarely Considered!" (Zirngibl, Deusch, Sattler,
Aulbach, Carle and Jonker, TMA 2022). It enumerates 82 parking services and,
for each, the NS, A, AAAA and CNAME records that identify a domain parked with
it. Only the NS indicators are used here, which is exactly what this list
holds.

Why this source: it is the only *published, structured, peer-reviewed*
enumeration of parking-service name servers found. The alternatives are
personal gists covering roughly ten services -- far less than the 129 entries
already committed here.

**Its limitation, stated plainly: it is a 2022 research artefact, not a live
feed.** It does not grow when a new parking service appears. Running this
generator therefore reconciles the list against a fixed, citable body of
evidence and adds what is missing; it does not keep the list current on its
own. That is still worth automating -- it replaces hand-transcription with a
reproducible import -- but a maintainer should not read a successful run as
"the list is now complete".

**This generator unions, it never replaces.** Entries committed here that the
paper does not cover are kept untouched.

The NS indicators come in two shapes: literal host names ("ns1.dan.com") and
SQL LIKE patterns ("ns%.parkingcrew.net."). Both are reduced to the
registrable domain this list stores ("dan.com", "parkingcrew.net"), because
that is the convention of the committed entries -- "bodis.com", not
"ns1.bodis.com". A pattern whose wildcard falls inside the *domain* rather
than the host label (e.g. "%.parking%.com") is skipped rather than guessed at:
expanding it would claim domains nobody has shown to be parking services.
"""

import json
import logging
import re

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = (
    "https://raw.githubusercontent.com/tma22-parking/"
    "tma22-parking.github.io/main/parking_services.json"
)

DST = "parking-domain-ns"

# A host name made only of ordinary labels: no SQL wildcard anywhere.
CLEAN_HOST = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]([a-z0-9-]*[a-z0-9])?)+$")


def registrable_domain(host):
    """Reduce a name-server host name to the domain this list stores.

    "ns1.bodis.com" -> "bodis.com". Deliberately the last two labels rather
    than a public-suffix lookup: every entry in the committed list is a plain
    two-label domain, the source's name servers are all under ordinary gTLDs,
    and adding a Public Suffix List fetch for this would be a dependency the
    result does not need. A name under a multi-part suffix (".co.uk") would be
    over-reduced, so those are rejected below instead of being guessed at.
    """
    labels = host.strip(".").split(".")
    if len(labels) < 2:
        return None
    return ".".join(labels[-2:])


# Suffixes where the last two labels are not a registrable domain. The source
# uses none of these today; the guard exists so that if one is ever added it
# is skipped loudly rather than reduced to a public suffix such as "co.uk",
# which as a warninglist entry would match a large part of a national TLD.
MULTIPART_SUFFIXES = (
    ".co.uk", ".org.uk", ".ac.uk", ".gov.uk", ".co.jp", ".com.au", ".co.nz",
    ".com.br", ".co.za", ".com.cn", ".net.cn", ".org.cn", ".co.in", ".com.mx",
)


def extract_ns_domains(services):
    domains = set()
    for key, service in services.items():
        records = (service or {}).get("record_types") or {}
        for indicator in records.get("ns") or []:
            if isinstance(indicator, dict):
                pattern = indicator.get("ilike")
                if not pattern:
                    continue
                value = pattern.strip().lower().rstrip(".")
                # Accept a wildcard only in the leading host label
                # ("ns%.bodis.com"): the rest must be a literal domain.
                head, _, tail = value.partition(".")
                if "%" in tail or "_" in tail or not tail:
                    logging.warning(
                        "%s: skipping NS pattern with a wildcard in the domain: %s",
                        key, pattern,
                    )
                    continue
                candidate = tail
            else:
                value = str(indicator).strip().lower().rstrip(".")
                if not value or "%" in value or "_" in value:
                    logging.warning("%s: skipping NS indicator: %s", key, indicator)
                    continue
                candidate = value

            if not CLEAN_HOST.match(candidate):
                logging.warning("%s: skipping unparseable NS host: %s", key, indicator)
                continue
            if candidate.endswith(MULTIPART_SUFFIXES):
                logging.warning(
                    "%s: skipping %s -- under a multi-part public suffix, "
                    "reducing it would produce an over-broad entry", key, candidate,
                )
                continue

            domain = registrable_domain(candidate)
            if domain:
                domains.add(domain)
    return domains


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

    fetched = extract_ns_domains(services)
    if not fetched:
        raise Exception(
            "No parking name servers found upstream, refusing to write an empty list"
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
        "parking-domain-ns: %d services, %d committed + %d fetched -> %d "
        "after union (%d new)",
        len(services), len(committed), len(fetched), len(merged),
        len(merged) - len(committed),
    )

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
