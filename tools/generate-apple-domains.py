#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate lists/apple-domains/list.json by merging two independent sources of
Apple-operated hosts:

  1. https://support.apple.com/en-us/101555
     Apple's own support article "Use Apple products on enterprise
     networks". The article is fully server-rendered (no JS execution
     needed): the host tables are present directly in the HTML returned by
     a plain GET request, one <table> per service/section, each with a
     "Hosts" column as the first column.

  2. https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/apple
     A structured domain list used by v2ray/Xray-style routing rules.
     Lines can be:
       - a bare domain            -> suffix match (the default rule kind)
       - "full:<domain>"          -> exact match
       - "keyword:<substring>"    -> substring match (DROPPED, see below)
       - "regexp:<pattern>"       -> regex match     (DROPPED, see below)
       - "include:<name>"         -> pull in sibling file data/<name>
       - trailing " @tag" attributes (e.g. " @cn", " @ads") which are
         stripped, along with any trailing " # comment" on the same line
       - '#' comments and blank lines, skipped

DECISION: following `include:` directives
------------------------------------------
The v2fly "apple" file lists 9 first-level includes: apple-dev,
apple-music, apple-pki, apple-podcasts, apple-tvplus, apple-update, beats,
icloud, itunes. All are genuinely Apple-operated properties, so this
generator DOES follow them and merges their domains in. Two of those
nest one level further (apple-dev -> swift, icloud -> icloudprivaterelay);
verified in practice (2026-08) neither `swift` nor `icloudprivaterelay`
contains further `include:` lines, so real-world recursion depth is 2.
The fetch is recursive with an explicit `visited` set (skips a file
already fetched, guarding against cycles) and a hard MAX_INCLUDE_DEPTH
cap; if the cap is hit a WARNING is logged and that branch is abandoned
rather than raising. This mirrors generate-google.py exactly.

TRAP handled: line 2 of the "apple" file is
`# Not include:apple-intelligence` -- a commented-out include. It must
NOT be followed. process_stream() (generator.py) already discards any
line whose first character is "#" before this generator ever sees it,
so the commented-out directive is dropped before directive-matching
happens and apple-intelligence is never fetched. Verified explicitly
below (see `assert "apple-intelligence" not in visited`).

DECISION: `keyword:` / `regexp:` entries
------------------------------------------
Both signify a matching semantics (substring anywhere / regex) that this
warninglist's `type` cannot express, so they are dropped. Every dropped
entry is counted and logged. (None currently occur anywhere in the
"apple" file or any of its transitive includes, verified 2026-08, but
the handling is kept for when upstream adds one.)

DECISION: single-label hostnames (e.g. bare "apple")
------------------------------------------
The v2fly "apple" file's line 13 is the bare entry `apple` (a ".apple"
gTLD Apple itself operates), preceded by the comment "# All .apple
domains". The ORIGINAL support-page-only HOSTNAME_RE in this file
required at least one dot, which would have silently dropped this entry
now that a second source can produce one. To stay consistent with the
sibling `generate-google.py` -- which is deliberately permissive about
single-label entries for the identical reason (it keeps bare "google",
itself a gTLD pulled in via v2fly includes; verified present in
lists/google/list.json) -- HOSTNAME_RE below is relaxed to also accept
a single label with no dot. This does not change the support-page
source's behaviour in practice: support.apple.com has no single-label
Hosts-column values (verified 2026-08), so the relaxation is only ever
exercised by the new v2fly source, and matters for exactly one entry
("apple"). Semantically it is also correct: `hostname`-type suffix
matching on entry "apple" matches any "*.apple" attribute value, which
is what a ".apple" TLD entry is meant to convey.

DECISION: warninglist `type` and entry shape
------------------------------------------
Unlike the frozen `google` list this generator's sibling deals with,
`apple-domains` was already shipped as `type: "hostname"` with bare,
dot-free entries (suffix/subdomain matching) -- see the docstring this
file replaces, and the in-repo `tranco` list for the same precedent.
That shape already suits both sources: Apple's own "*.example.com"
wildcard convention and v2fly's bare-domain suffix-match default both
collapse onto the same bare-hostname-with-suffix-matching semantics, and
v2fly's `full:` entries (exact match) are still valid, if slightly
narrower-than-necessary, members of a suffix-matching list. No `type`
change is needed or made here.
"""
import json
import logging
import re

from bs4 import BeautifulSoup

from generator import download, get_abspath_list_file, get_version, process_stream, write_to_file

# Apple republishes the same article content, verbatim, under every locale
# path. en-us is the canonical/most stable one.
SOURCE_1_URL = "https://support.apple.com/en-us/101555"

SOURCE_2_BASE = "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/"
SOURCE_2_ROOT = "apple"

MAX_INCLUDE_DEPTH = 8

# Permissive about single-label entries (e.g. bare "apple" itself, a
# gTLD Apple operates, pulled in via the v2fly source) -- see the
# single-label DECISION note above. Matches the sibling
# generate-google.py's HOSTNAME_RE shape/rationale for the same case.
HOSTNAME_RE = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?(\.[A-Za-z0-9]([A-Za-z0-9-]*[A-Za-z0-9])?)*$')

dropped_keyword_regexp_count = 0


def normalise_host(raw):
    value = raw.strip()
    if not value:
        return None

    # Defensive: strip a scheme if one ever shows up.
    value = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', value)
    # Defensive: strip a path or query if one ever shows up.
    value = value.split('/', 1)[0]
    # Defensive: strip a port if one ever shows up.
    value = value.split(':', 1)[0]

    value = value.strip()

    # Apple's wildcard convention: "*.example.com" -> "example.com".
    # The "hostname" warninglist type already matches a value and all of its
    # subdomains, so dropping the "*." keeps the same matching semantics.
    if value.startswith('*.'):
        value = value[2:]

    # Strip a trailing FQDN dot.
    value = value.rstrip('.')

    if not value:
        return None

    if not HOSTNAME_RE.match(value):
        return None

    return value.lower()


def fetch_hosts(url):
    response = download(url)
    if response.status_code != 200:
        raise Exception("Request to {} returned HTTP code {}".format(url, response.status_code))

    soup = BeautifulSoup(response.content, 'html.parser')
    hosts = set()

    for table in soup.find_all('table'):
        header_cells = table.find_all('th')
        headers = [th.get_text(strip=True) for th in header_cells]
        if not headers or headers[0] != 'Hosts':
            continue

        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if not cells:
                continue
            host_cell = cells[0]
            # A cell can (in theory) contain more than one host, e.g.
            # separated by <br> or commas; split defensively on both.
            cell_text = host_cell.get_text(separator='\n', strip=True)
            for line in cell_text.split('\n'):
                for part in line.split(','):
                    host = normalise_host(part)
                    if host:
                        hosts.add(host)

    return hosts


def fetch_v2fly_file(name, visited, depth):
    """
    Fetch one v2fly domain-list-community data file (recursing into any
    `include:` directives it contains) and return the set of bare,
    normalised hostnames it yields.

    `visited` guards against cycles/re-fetching a file already pulled in
    by another include chain. `depth` is checked against
    MAX_INCLUDE_DEPTH to bound recursion regardless of `visited`.
    """
    global dropped_keyword_regexp_count

    result = set()

    if name in visited:
        return result
    visited.add(name)

    if depth > MAX_INCLUDE_DEPTH:
        logging.warning(
            "generate-apple-domains: MAX_INCLUDE_DEPTH exceeded while "
            "following v2fly include chain at '{}', abandoning this "
            "branch".format(name)
        )
        return result

    url = SOURCE_2_BASE + name
    # process_stream() drops any line whose first character is "#" (and
    # blank lines) before we ever see it -- this is what keeps the
    # commented-out "# Not include:apple-intelligence" line on line 2 of
    # the root "apple" file from ever being treated as a directive.
    lines = process_stream(url)

    for line in lines:
        entry = line.strip()
        if not entry:
            continue

        # Strip trailing " @tag" attributes (e.g. " @cn", " @ads") and any
        # trailing " # comment" on the same line -- both fall after the
        # first whitespace, so one split handles them together.
        entry = entry.split(" ", 1)[0].split("\t", 1)[0]
        if not entry:
            continue

        if entry.startswith("include:"):
            included_name = entry.split(":", 1)[1].strip()
            if included_name:
                result |= fetch_v2fly_file(included_name, visited, depth + 1)
            continue

        if entry.startswith("keyword:") or entry.startswith("regexp:"):
            dropped_keyword_regexp_count += 1
            continue

        if entry.startswith("full:"):
            domain = entry.split(":", 1)[1]
        else:
            # Bare entry: default v2fly rule kind is domain-suffix match,
            # which is exactly what MISP's `hostname` type expresses.
            domain = entry

        host = normalise_host(domain)
        if host is None:
            continue
        result.add(host)

    return result


def parse_source2():
    visited = set()
    result = fetch_v2fly_file(SOURCE_2_ROOT, visited, 0)
    # Verify the commented-out include was never followed.
    assert "apple-intelligence" not in visited, (
        "generate-apple-domains: commented-out 'apple-intelligence' "
        "include was wrongly followed"
    )
    return result, visited


def process(url, dst):
    # --- Source 1: Apple's own support article ---
    source1 = fetch_hosts(url)
    logging.info(
        "generate-apple-domains: source1 (support.apple.com) kept={}".format(len(source1))
    )

    # --- Source 2 (recursive, follows include:) ---
    source2, visited = parse_source2()
    included_files = sorted(visited - {SOURCE_2_ROOT})
    logging.info(
        "generate-apple-domains: source2 (v2fly domain-list-community) "
        "kept={} dropped_keyword_or_regexp={} include_files_fetched={}".format(
            len(source2), dropped_keyword_regexp_count, included_files
        )
    )

    merged = source1 | source2
    logging.info(
        "generate-apple-domains: overlap source1&source2={}".format(len(source1 & source2))
    )

    # Union with the entries already committed, never replace them. The two
    # upstream sources between them do not necessarily cover every domain
    # the existing list carried, and a domain Apple operated in the past is
    # still worth recognising in a false-positive warninglist, so this
    # generator only ever adds. Existing entries are normalised through the
    # same path as the sources (mirrors generate-google.py's pattern).
    try:
        with open(get_abspath_list_file(dst)) as existing_file:
            for entry in json.load(existing_file)["list"]:
                normalised = normalise_host(entry)
                if normalised:
                    merged.add(normalised)
    except (IOError, OSError, ValueError, KeyError):
        pass

    logging.info(
        "generate-apple-domains: merged unique count={}".format(len(merged))
    )

    warninglist = {
        'name': "List of known Apple hosts for enterprise networks",
        'version': get_version(),
        'description': "Hosts that Apple products need to access on enterprise networks, merged from Apple's support article ({}) and the v2fly domain-list-community 'apple' data set (and its includes).".format(url),
        'type': "hostname",
        'list': [],
        'matching_attributes': ["hostname", "domain", "domain|ip", "url"]
    }

    warninglist['list'] = sorted(merged)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    process(SOURCE_1_URL, 'apple-domains')
