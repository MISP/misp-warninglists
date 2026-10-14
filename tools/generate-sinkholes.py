#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the known-sinkholes warninglist.

Source: https://github.com/brakmic/Sinkholes -- a community-curated list of
malware and research sinkhole address ranges together with the organisation
operating each one, published as JSON. It descends from Lesley Carhart's
Consolidated Malware Sinkhole List and covers the operators this list was
already being populated from by hand (SecurityScorecard, Bitsight, RiskRecon,
Anubis, Microsoft and others named in this list's commit history).

**This generator unions, it never replaces.** 36 of the 107 committed entries
are not in the upstream feed. A sinkhole address that an operator has since
retired still explains an indicator recorded while it was live, so entries are
never dropped automatically; removal stays a human decision.

Two shapes appear in the feed's "IP Range" column that ipaddress cannot read
directly and that are handled explicitly below: last-octet shorthand
("131.253.18.11-12") and full dotted ranges ("1.2.3.4 - 1.2.3.9"). Anything
else that will not parse is skipped with a warning rather than guessed at --
a wrong network in a suppression list silences alerts for somebody else's
addresses.

Single addresses are emitted in the bare form this list already uses
("104.155.11.149", not "104.155.11.149/32") so the generator does not rewrite
71 existing entries into an equivalent-but-different spelling on first run.
"""

import ipaddress
import json
import logging
import re

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = "https://raw.githubusercontent.com/brakmic/Sinkholes/master/Sinkholes_List.json"

DST = "sinkholes"

# "131.253.18.11-12" -- a dotted quad whose final octet carries a range.
SHORT_RANGE = re.compile(r"^(\d+\.\d+\.\d+)\.(\d+)\s*-\s*(\d+)$")
# "1.2.3.4 - 1.2.3.9"
FULL_RANGE = re.compile(r"^(\d+\.\d+\.\d+\.\d+)\s*-\s*(\d+\.\d+\.\d+\.\d+)$")


def normalise(network):
    """Render a network the way this list already spells it.

    A single address is written bare; anything wider keeps its prefix length.
    """
    if network.prefixlen == network.max_prefixlen:
        return str(network.network_address)
    return str(network)


def summarize(first, last):
    return list(
        ipaddress.summarize_address_range(
            ipaddress.IPv4Address(first), ipaddress.IPv4Address(last)
        )
    )


def parse_entry(value):
    """Turn one "IP Range" cell into a list of networks. Never guesses."""
    value = value.strip()
    if not value:
        return []
    try:
        return [ipaddress.ip_network(value, strict=True)]
    except ValueError:
        pass

    match = FULL_RANGE.match(value)
    if match:
        try:
            return summarize(match.group(1), match.group(2))
        except (ValueError, ipaddress.AddressValueError) as exc:
            logging.warning("Skipping unreadable range %s: %s", value, exc)
            return []

    match = SHORT_RANGE.match(value)
    if match:
        prefix, start, end = match.group(1), match.group(2), match.group(3)
        try:
            return summarize(
                "{}.{}".format(prefix, start), "{}.{}".format(prefix, end)
            )
        except (ValueError, ipaddress.AddressValueError) as exc:
            logging.warning("Skipping unreadable shorthand range %s: %s", value, exc)
            return []

    logging.warning("Skipping unrecognised IP Range value: %s", value)
    return []


def existing_warninglist():
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def main():
    response = download(URL)
    response.raise_for_status()

    rows = response.json()
    if not isinstance(rows, list):
        raise Exception("Unexpected upstream shape: expected a JSON array of rows")

    fetched = set()
    for row in rows:
        for network in parse_entry(str(row.get("IP Range", ""))):
            fetched.add(normalise(network))

    if not fetched:
        raise Exception("No sinkholes found upstream, refusing to write an empty list")

    warninglist = existing_warninglist()
    if warninglist is None:
        raise Exception(
            "lists/{}/list.json is missing; this generator maintains an "
            "existing curated list and will not create one from scratch".format(DST)
        )

    committed = set(warninglist.get("list", []))
    merged = committed.union(fetched)
    logging.info(
        "sinkholes: %d committed + %d fetched -> %d after union (%d new)",
        len(committed),
        len(fetched),
        len(merged),
        len(merged) - len(committed),
    )

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
