#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the RFC 6761 Special-Use Domain Names warninglist.

Source: the IANA "Special-Use Domain Names" registry -- the registry RFC 6761
itself created (RFC 6761 section 5) and the only authoritative record of what
belongs in it. The XML rendering is used rather than the HTML page so the
reference for each name can be read from a parsed attribute instead of being
recovered from markup.

**Why this generator exists, stated plainly: it closes a gap.** The committed
list holds the twenty-one reverse-mapping and example.* names, but not the
four names RFC 6761 section 6 defines in plain text -- "test.", "localhost.",
"invalid." and the "example." TLD. A list whose name promises RFC 6761 should
contain all of them, and "localhost" in particular is the special-use name an
analyst is most likely to meet in a real event.

RFC 6761 is a frozen document, so this is a reconciliation rather than a live
feed: it will not find anything next month that it does not find today. What
it does buy is that the reconciliation is reproducible, and that if IANA ever
records a further name against RFC 6761 the next scheduled run picks it up.

**Scope is deliberately narrow: only names whose registry reference is
RFC 6761.** The registry also carries "local." and the mDNS reverse zones
(RFC 6762), ".onion" (RFC 7686), "home.arpa" (RFC 8375), "ipv4only.arpa"
(RFC 8880) and others. Those are real special-use names, but they are not
RFC 6761 names, and this list is titled after that RFC. Adding them would make
the list's name a lie; if MISP wants full registry coverage that is a
different, separately named list.

**This generator unions, it never replaces.** Entries are stored without the
registry's trailing dot, matching the committed convention.
"""

import json
import logging
import xml.etree.ElementTree as ElementTree

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = "https://www.iana.org/assignments/special-use-domain-names/special-use-domain-names.xml"

DST = "rfc6761"

NAMESPACE = {"iana": "http://www.iana.org/assignments"}

# The reference RFC 6761 names carry in the registry, lowercased.
REFERENCE = "rfc6761"

# RFC 6761 defines twenty-five names (test, localhost, invalid, example plus
# example.com/net/org, and the eighteen private-address reverse zones). Fewer
# than this means the registry was read wrongly, not that IANA removed names.
MINIMUM_EXPECTED = 20


def parse_registry(payload):
    """Return the registry names whose reference is RFC 6761.

    Parsed with ElementTree rather than matched with a pattern: this is
    network-fetched input, and an XML parser is both correct and free of the
    backtracking a markup regex invites.
    """
    root = ElementTree.fromstring(payload)
    names = set()
    for record in root.findall(".//iana:record", NAMESPACE):
        name = (record.findtext("iana:name", default="", namespaces=NAMESPACE) or "").strip()
        if not name:
            continue
        # Withdrawn entries are annotated in the name field, e.g.
        # "eap-noob.arpa. (DEPRECATED)". Never guess at those.
        if " " in name or "(" in name:
            logging.info("rfc6761: skipping annotated registry entry: %s", name)
            continue
        references = set()
        for xref in record.findall("iana:xref", NAMESPACE):
            data = xref.get("data")
            if xref.get("type") == "rfc" and data:
                references.add(data.strip().lower())
        if REFERENCE not in references:
            continue
        names.add(name.strip(".").lower())
    return names


def existing_warninglist():
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def main():
    response = download(URL)
    response.raise_for_status()

    fetched = parse_registry(response.content)
    if len(fetched) < MINIMUM_EXPECTED:
        raise Exception(
            "Only {} RFC 6761 names found in the IANA registry (expected at "
            "least {}); refusing to act on a partial read.".format(
                len(fetched), MINIMUM_EXPECTED
            )
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
        "rfc6761: %d committed + %d registry names -> %d after union (%d new)",
        len(committed), len(fetched), len(merged), len(merged) - len(committed),
    )
    for name in sorted(fetched - committed):
        logging.info("rfc6761: adding RFC 6761 name absent from the list: %s", name)

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
