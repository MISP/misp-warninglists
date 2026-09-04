#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Propose candidates for the security-provider-blogpost warninglist.

**This is a review aid, not a generator. It never writes list.json, and it is
deliberately not wired into generate_all.sh.**

Why this list is not auto-generated
-----------------------------------
lists/security-provider-blogpost is a curated judgement call about which
domains are security-vendor *blog* space, and its commit history is a record
of that judgement being exercised: pastebin.com removed because malware
fetches payloads from it, imgur.com removed, Google services removed after
issue #214. The list's purpose is to stop an analyst's own reading material
from being treated as an indicator -- so a wrong entry here does not merely
add noise, it suppresses a real domain.

The available sources are curated "awesome" README files, and measuring them
against the committed list shows why they cannot be unioned in blind. Of 190
domains linked from the largest one, only 48 are already present, and the 142
"new" ones include aws.amazon.com and the list maintainer's own commercial
product. Auto-importing that set would put a major cloud provider's domain
into a suppression list -- exactly the class of mistake the removals above
were correcting.

So the automation offered here is the part that is safe to automate: finding
and presenting candidates, with the accept/reject decision left to a human.

Usage
-----
    python3 review-security-provider-blogpost.py            # candidates
    python3 review-security-provider-blogpost.py --check    # dead entries

--check resolves every committed entry and reports the ones that no longer
exist. It reports only; it never prunes. A vendor blog that has moved still
explains an indicator recorded while it was live, and deciding otherwise is a
maintainer's call.
"""

from __future__ import print_function

import argparse
import json
import logging
import os
import re
import sys

from generator import download, get_abspath_list_file

DST = "security-provider-blogpost"

SOURCES = (
    (
        "muchdogesec/awesome_threat_intel_blogs",
        "https://raw.githubusercontent.com/muchdogesec/"
        "awesome_threat_intel_blogs/main/README.md",
    ),
    (
        "thehappydinoa/awesome-threat-intel-rss",
        "https://raw.githubusercontent.com/thehappydinoa/"
        "awesome-threat-intel-rss/main/README.md",
    ),
)

# Domains that appear in these READMEs as infrastructure, badges or the
# publisher's own product rather than as a security vendor's blog. Filtering
# them out here keeps the candidate list short enough to actually be read.
NOT_CANDIDATES = (
    "github.com", "githubusercontent.com", "shields.io", "twitter.com",
    "x.com", "opensource.org", "creativecommons.org", "w3.org",
    "obstracts.com", "feedburner.com", "youtube.com", "linkedin.com",
    "mastodon.social", "infosec.exchange", "archive.org", "web.archive.org",
    "aws.amazon.com", "amazon.com", "google.com", "medium.com",
)

LINK = re.compile(r"https?://([a-z0-9.-]+\.[a-z]{2,})", re.I)


def committed_entries():
    with open(get_abspath_list_file(DST)) as data_file:
        return {entry.lower() for entry in json.load(data_file)["list"]}


def gather_candidates(existing):
    found = {}
    for name, url in SOURCES:
        try:
            response = download(url)
            response.raise_for_status()
        except Exception as exc:
            print("  ! could not read {}: {}".format(name, exc), file=sys.stderr)
            continue
        for match in LINK.finditer(response.text):
            host = match.group(1).lower().strip(".")
            if host in existing:
                continue
            if host.endswith(NOT_CANDIDATES) or host in NOT_CANDIDATES:
                continue
            found.setdefault(host, set()).add(name)
    return found


def check_dead(existing):
    try:
        import dns.resolver
    except ImportError:
        print("dnspython is required for --check", file=sys.stderr)
        return 1
    from generator import create_resolver

    resolver = create_resolver()
    dead = []
    for host in sorted(existing):
        try:
            resolver.resolve(host, "A")
        except dns.resolver.NXDOMAIN:
            dead.append(host)
        except Exception:
            # Timeouts, SERVFAIL and rate limiting are not evidence of
            # anything; only NXDOMAIN is reported.
            continue
    print("\n== Entries returning NXDOMAIN ({}) ==".format(len(dead)))
    print("Reported for review only -- nothing is removed automatically.\n")
    for host in dead:
        print("  {}".format(host))
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true",
        help="resolve committed entries and report ones that are NXDOMAIN",
    )
    args = parser.parse_args()

    existing = committed_entries()
    print("Committed entries: {}".format(len(existing)))

    if args.check:
        return check_dead(existing)

    found = gather_candidates(existing)
    print("\n== Candidate domains not already listed ({}) ==".format(len(found)))
    print("Each needs a human decision: is this a security vendor's blog?")
    print("Adding a non-vendor domain here SUPPRESSES it as an indicator.\n")
    for host in sorted(found):
        print("  {:45s} seen in: {}".format(host, ", ".join(sorted(found[host]))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
