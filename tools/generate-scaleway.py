#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Scaleway warninglist.

Tier 1, vendor-published endpoint. Scaleway (formerly Online SAS, part of the
Iliad group) documents the address space it uses on its own documentation site,
and serves that page as plain Markdown through the ``text/markdown`` alternate
the HTML page advertises:

    https://www.scaleway.com/en/docs/account/reference-content/scaleway-network-information.md

Only the "IP ranges used by Scaleway" section is read. The rest of the page
lists individual DNS cache and NTP server addresses, which are bare host IPs --
``ipaddress.ip_network()`` accepts those as valid /32s, so an unscoped sweep of
the document would silently add single resolvers as list entries. Everything is
fetched at runtime; no address is hardcoded here.

No RFC 8805 geofeed is published: the peering geofeed URL returns 404 and
geofeed.scaleway.com does not resolve. RIPEstat by ASN (tier 2) is therefore not
needed -- every prefix AS12876 announces falls inside the documented ranges, so
the vendor list is the broader and more stable of the two.

Semantics caveat: this is general-purpose rented compute. The tenant behind any
given address changes constantly and an attacker can simply rent one. The list
recognises that an address belongs to the provider; it is NOT grounds for
treating traffic as benign.
"""

import ipaddress
import logging
import re

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

URL = (
    "https://www.scaleway.com/en/docs/account/reference-content/"
    "scaleway-network-information.md"
)

# The Markdown heading that opens the address-space section. Parsing stops at
# the next level-2 heading.
SECTION_HEADING = "## IP ranges used by Scaleway"

# Bullet items in that section look like:  * `62.210.0.0/16`
BULLET = re.compile(r"^[-*]\s+`([^`]+)`\s*$")


def extract_section(text):
    """Lines of the IP-ranges section, exclusive of the following section."""
    lines = text.splitlines()

    start = None
    for index, line in enumerate(lines):
        if line.strip() == SECTION_HEADING:
            start = index + 1
            break
    if start is None:
        raise Exception(
            "Section {!r} not found at {}; the documentation page has been "
            "restructured and the generator must be updated rather than "
            "guessing at the layout".format(SECTION_HEADING, URL)
        )

    section = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        section.append(line)
    return section


def parse_prefixes(section):
    networks = []
    for line in section:
        match = BULLET.match(line.strip())
        if not match:
            continue
        prefix = match.group(1).strip()
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
    response = download(URL)
    response.raise_for_status()

    networks = parse_prefixes(extract_section(response.text))
    if not networks:
        raise Exception(
            "No Scaleway prefixes found at {}, refusing to write an empty "
            "list".format(URL)
        )

    warninglist = {
        "name": "List of known Scaleway IP address ranges",
        "version": get_version(),
        "description": (
            "Scaleway (formerly Online SAS) IP address ranges, from the ranges "
            "Scaleway documents itself ({}). This is general-purpose rented "
            "compute: the tenant behind any given address changes constantly "
            "and an attacker can simply rent one. The list recognises that an "
            "address belongs to the provider; it is NOT grounds for treating "
            "traffic as benign.".format(URL)
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
    write_to_file(warninglist, "scaleway")


if __name__ == "__main__":
    main()
