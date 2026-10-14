#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the dynamic DNS warninglist.

Source: https://github.com/alexandrosmagos/dyn-dns-list -- a maintained,
automatically refreshed collection of domains offered by dynamic DNS
providers (afraid.org, no-ip.com, dyn.com, changeip.com, duckdns.org and
others). The plain one-domain-per-line rendering is used.

That repository is where this list's contents originally came from: 29,200 of
the 35,467 entries committed here are present in it verbatim, and the oldest
entries match its ordering exactly. This generator simply reconnects the list
to the upstream it was hand-copied from in 2021 and 2023.

**This generator unions, it never replaces.** 6,267 committed entries are NOT
in the upstream feed today -- providers that shut down, domains the upstream
dropped, and entries MISP maintainers added by hand. A dynamic DNS domain that
stopped being offered last year still explains an indicator seen last year, so
nothing is ever removed automatically. Removal stays a human decision.

Entries carry a leading dot (".duckdns.org"), which is this list's established
matching convention -- it is what makes a subdomain such as
"evil.duckdns.org" match. The convention is preserved exactly; changing it
would silently alter matching behaviour on every deployed MISP instance.
"""

import json
import logging

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = "https://raw.githubusercontent.com/alexandrosmagos/dyn-dns-list/master/links.txt"

DST = "dynamic-dns"


def existing_warninglist():
    """Return the committed warninglist, or None if it is not there yet.

    The committed name/description/type/matching_attributes are authoritative:
    MISP keys warninglists on `name`, so regenerating with a different one
    registers server-side as a competing list rather than an update.
    """
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def parse_domains(text):
    domains = []
    for line in text.splitlines():
        line = line.strip().lower()
        if not line or line.startswith("#"):
            continue
        # Defensive: the feed is one bare domain per line, but reject anything
        # carrying a scheme, path or whitespace rather than storing a value
        # that could never match.
        if any(c in line for c in ("/", " ", "\t", ":")):
            logging.warning("Skipping malformed feed line: %s", line)
            continue
        if "." not in line:
            logging.warning("Skipping entry without a dot: %s", line)
            continue
        domains.append("." + line.lstrip("."))
    return domains


def main():
    response = download(URL)
    response.raise_for_status()

    fetched = parse_domains(response.text)
    if not fetched:
        raise Exception(
            "No dynamic DNS domains found upstream, refusing to write an empty list"
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
        "dynamic-dns: %d committed + %d fetched -> %d after union (%d new)",
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
