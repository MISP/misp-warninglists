#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Telegram IP address range warninglist.

Source: https://core.telegram.org/resources/cidr.txt -- Telegram's own
published statement of the address space its infrastructure uses. This is not
a source discovered here: it is the URL already named in this list's own
description field, which means the list was built from it by hand and simply
never wired up.

Because the source is first-party and authoritative, the only thing this
generator changes is who transcribes it. At the time of writing the feed and
the committed list agree exactly, entry for entry -- so the value of this
script is not what it adds today but that the next time Telegram publishes a
new prefix, a scheduled run picks it up instead of somebody noticing.

**This generator unions, it never replaces.** Telegram does publish removals,
and a prefix Telegram has released is still worth recognising in an event
recorded while Telegram held it. Dropping an entry stays a human decision.

Every line is parsed with ipaddress and re-rendered before comparison, so a
difference in spelling (an uppercase or uncompressed IPv6 prefix, say) cannot
appear as a spurious new entry alongside the one already committed.
"""

import ipaddress
import json
import logging

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = "https://core.telegram.org/resources/cidr.txt"

DST = "telegram-ips"

# Telegram has published more than a dozen prefixes for years. A feed that
# suddenly yields a handful has more likely broken or been truncated than
# Telegram has shrunk, and this refuses to act on such a run.
MINIMUM_EXPECTED = 8


def parse_feed(text):
    networks = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        try:
            networks.add(str(ipaddress.ip_network(line, strict=True)))
        except ValueError as exc:
            logging.warning("telegram-ips: skipping unreadable prefix %s: %s", line, exc)
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

    fetched = parse_feed(response.text)
    if len(fetched) < MINIMUM_EXPECTED:
        raise Exception(
            "Only {} prefixes read from {} (expected at least {}); refusing to "
            "act on a partial feed.".format(len(fetched), URL, MINIMUM_EXPECTED)
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
        "telegram-ips: %d committed + %d published -> %d after union (%d new)",
        len(committed), len(fetched), len(merged), len(merged) - len(committed),
    )
    for prefix in sorted(fetched - committed):
        logging.info("telegram-ips: new prefix published by Telegram: %s", prefix)
    for prefix in sorted(committed - fetched):
        logging.info(
            "telegram-ips: committed prefix no longer published upstream "
            "(kept, removal is a human decision): %s", prefix,
        )

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
