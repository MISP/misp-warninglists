#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the captive-portal detection warninglist.

Source: https://captivebehavior.wballiance.com/ -- the Wireless Broadband
Alliance's captive-portal behaviour reference, which is the source this list
was created from (see the list's original commit) and which documents the
host names each operating system contacts to decide whether it is behind a
captive portal.

**This is an HTML scrape, and that is a real weakness.** The WBA publishes no
JSON or CSV rendering; there is no API. A redesign of that page can silently
reduce what this generator extracts, so the code is written to fail loudly
rather than quietly shrink the list:

  * it refuses to write if the page yields fewer host names than a floor, and
  * it unions with the committed list, so a bad scrape can never delete an
    entry -- the worst case is that a run adds nothing.

The page text also contains file names ("hotspot-detect.html",
"success.txt"), schema URLs and JavaScript identifiers ("window.alert") that
look superficially like host names. Candidates are therefore accepted only if
their last label is a real TLD, checked against the IANA registry at runtime
rather than against a hand-written allowlist.

Entries are bare host names ("captive.apple.com"), matching this list's
existing convention -- no leading dot, unlike the suffix-matching lists.
"""

import json
import logging
import re

from generator import download, get_abspath_list_file, get_version, write_to_file

URL = "https://captivebehavior.wballiance.com/"

# The authoritative list of current TLDs, used to tell a host name apart from
# a file name or a JavaScript identifier.
TLD_URL = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"

DST = "captive-portals"

# A scrape that returns fewer than this many host names has almost certainly
# broken rather than genuinely shrunk; the WBA page has carried around twenty
# for years. Refuse to act on such a run.
MINIMUM_EXPECTED = 12

# Deliberately NOT a nested-quantifier hostname regex. A pattern such as
# (?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+ backtracks polynomially, and this runs
# over HTML fetched from the network -- i.e. input this code does not control.
# A flat character-class scan is linear, and the structural validation is done
# in is_hostname() below with plain string operations that cannot backtrack.
TOKEN = re.compile(r"[a-z0-9.-]+")

LABEL_CHARS = frozenset("abcdefghijklmnopqrstuvwxyz0123456789-")


def is_hostname(token, tlds):
    """Structural hostname check using only linear string operations."""
    if len(token) > 253 or token.count(".") < 1:
        return False
    labels = token.split(".")
    if len(labels) < 2:
        return False
    for label in labels:
        if not label or len(label) > 63:
            return False
        if label[0] == "-" or label[-1] == "-":
            return False
        if not set(label) <= LABEL_CHARS:
            return False
    return labels[-1] in tlds


# Hosts belonging to the publishing site and its page furniture rather than to
# captive-portal detection.
IGNORED_SUFFIXES = (
    "wballiance.com", "googleapis.com", "gstatic.net", "github.com",
    "githubusercontent.com", "w3.org", "schema.org", "jquery.com",
    "bootstrapcdn.com", "cloudflare.com", "fontawesome.com",
)


def fetch_tlds():
    response = download(TLD_URL)
    response.raise_for_status()
    tlds = set()
    for line in response.text.splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            tlds.add(line)
    if not tlds:
        raise Exception("Could not load the IANA TLD list; refusing to guess")
    return tlds


def extract_hostnames(html, tlds):
    # Strip tags so that attribute values (href, src) do not contribute hosts
    # that belong to the page's own assets rather than to its subject matter.
    text = re.sub(r"<script[^>]*>.*?</script>", " ", html, flags=re.S | re.I)
    text = re.sub(r"<style[^>]*>.*?</style>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", text)

    hosts = set()
    for match in TOKEN.finditer(text.lower()):
        host = match.group(0).strip(".")
        # is_hostname() rejects "hotspot-detect.html", "success.txt" and
        # "window.alert": their last label is not a registered TLD.
        if not is_hostname(host, tlds):
            continue
        if host.endswith(IGNORED_SUFFIXES) or host in IGNORED_SUFFIXES:
            continue
        hosts.add(host)
    return hosts


def existing_warninglist():
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def main():
    tlds = fetch_tlds()

    response = download(URL)
    response.raise_for_status()

    fetched = extract_hostnames(response.text, tlds)
    if len(fetched) < MINIMUM_EXPECTED:
        raise Exception(
            "Only {} host names scraped from {} (expected at least {}); the page "
            "layout has probably changed. Refusing to act on a partial scrape.".format(
                len(fetched), URL, MINIMUM_EXPECTED
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
        "captive-portals: %d committed + %d scraped -> %d after union (%d new)",
        len(committed), len(fetched), len(merged), len(merged) - len(committed),
    )
    for host in sorted(fetched - committed):
        logging.info("captive-portals: new candidate from WBA page: %s", host)

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
