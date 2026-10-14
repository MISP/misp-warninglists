#!/usr/bin/env python3
"""
Generate lists/google/list.json by merging three independent sources of
Google-operated domains:

  1. https://www.google.com/supported_domains
     Google's own list of ccTLD variants of google.com, one leading-dot
     domain per line (e.g. ".google.co.uk"). Authoritative and live.

  2. https://raw.githubusercontent.com/nickspaargaren/no-google/master/google-domains
     A community-maintained hosts-file style blocklist of Google service
     domains (analytics, ads, API endpoints, ...). Format is
     "0.0.0.0 <domain>", with '#' comment lines (including a
     "Last updated:" banner) to be skipped. Verified: the "master" branch
     is the live branch (raw fetch returns HTTP 200 and ~6.8k lines);
     "main" returns HTTP 404.

  3. https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/google
     A structured domain list used by v2ray/Xray-style routing rules.
     Lines can be:
       - a bare domain            -> suffix match (the default rule kind)
       - "full:<domain>"          -> exact match
       - "keyword:<substring>"    -> substring match (DROPPED, see below)
       - "regexp:<pattern>"       -> regex match     (DROPPED, see below)
       - "include:<name>"         -> pull in sibling file data/<name>
       - trailing " @tag" attributes (e.g. " @cn", " @ads") which are
         stripped
       - '#' comments and blank lines, skipped

DECISION: following `include:` directives
------------------------------------------
The v2fly "google" file starts with a block of `include:` lines
(android, blogspot, dart, fastlane, firebase, flutter, golang,
google-deepmind, google-play, google-registry, google-scholar,
google-trust-services, googlefcm, kaggle, opensourceinsights, polymer,
v8, youtube). These are genuinely Google-operated properties (Android,
YouTube, Firebase, Google Play, Google Trust Services, ...), so this
generator DOES follow them and merges their domains in. To stay safe
against cycles or unexpectedly deep chains, the fetch is recursive with
an explicit `visited` set (skips a file already fetched) and a hard
MAX_INCLUDE_DEPTH cap; if the cap is hit a WARNING is logged and that
branch is abandoned rather than raising. Verified in practice (2026-08)
none of the 18 first-level include files themselves contain further
`include:` lines, so real-world recursion depth is 1, but the guard is
kept in the code because the upstream file is not under our control.

DECISION: `keyword:` / `regexp:` entries
------------------------------------------
Both signify a matching semantics (substring anywhere / regex) that this
warninglist's `type` cannot express (see the `type` decision below), so
they are dropped. Every dropped entry is counted and logged.

DECISION: warninglist `type` and entry shape (TYPE CHANGE -- see PR body)
------------------------------------------
This generator switches the list from `type: "string"` with leading-dot
entries (".google.ad") to `type: "hostname"` with bare, dot-free
entries ("google.ad"). This is a user-visible change from the frozen
2025-08-21 list and is called out explicitly in the PR body so a
maintainer can accept or reject it deliberately. It is NOT a
stylistic choice -- it was checked against MISP core's actual matching
code (MISP/MISP app/Model/Warninglist.php, `checkValue()` and its
`__evalString()` / `__evalHostname()` helpers, fetched and read during
this change):

  - `__evalString()` (used for `type: "string"`) does
    `isset($listValues[$value])` -- a byte-for-byte EXACT match of the
    whole attribute value against a list entry. There is no dot
    special-casing anywhere in it. A stored entry of ".google.ad" can
    therefore only ever match an attribute whose value is literally
    the 11-character string ".google.ad" -- which no real hostname
    attribute value is. Per README.md, `string` is documented as
    "perfect match", consistent with the code: it is not a suffix/
    domain match, regardless of a leading dot.
  - `__evalHostname()` (used for `type: "hostname"`) is the mechanism
    that actually does the intended matching: it splits the attribute
    value into labels and walks the suffixes ("www.google.ad" tries
    "ad", "google.ad", "www.google.ad" in turn) doing an exact lookup
    of each bare (non-dot-prefixed) suffix against the list. This is
    the documented "hostname matching (e.g. domain matching from URL)"
    behaviour in README.md, and it is what every one of the three
    sources here actually needs (source 1's ccTLD variants, and
    sources 2/3's service subdomains like "googlevideo.com" or
    "play.googleapis.com", are all meant to also cover their own
    subdomains).
  - The in-repo `tranco` list (`lists/tranco/list.json`) is the
    working precedent for this: `type: "hostname"` with bare entries,
    the same `matching_attributes` family used here.
  - `getFilteredEntries()` in the same file confirms this from the
    loading side: for `type: "hostname"` every entry is loaded via
    `strtolower(trim($v, '.'))` (dots trimmed, case folded) before use,
    while `type: "string"` entries are loaded completely as-is with no
    trimming at all -- i.e. bare, lowercase entries are the canonical
    form MISP core itself normalizes "hostname" lists to.
  - The old leading-dot/`type: "string"` shape shared by `google`,
    `microsoft`, and `microsoft-win10-connection-endpoints` therefore
    appears to already be non-functional against current MISP core --
    but fixing those other two frozen lists is out of scope here
    (scope is `google` only); this generator does not perpetuate the
    same defect for `google` going forward.
  - Practically: dot-stripping/adding was a uniform bijection over the
    merged set, so switching to bare entries does not change *which*
    domains are in the list or its final count (verified: 7469 before
    and after the switch) -- only the stored shape and, importantly,
    whether the list actually matches anything in MISP.
"""

import json
import logging
import re
from urllib.parse import urlsplit

from generator import process_stream, get_abspath_list_file, get_version, write_to_file

SOURCE_1_URL = "https://www.google.com/supported_domains"
SOURCE_2_URL = "https://raw.githubusercontent.com/nickspaargaren/no-google/master/google-domains"
SOURCE_3_BASE = "https://raw.githubusercontent.com/v2fly/domain-list-community/master/data/"
SOURCE_3_ROOT = "google"

MAX_INCLUDE_DEPTH = 8

# Plausible-hostname check: labels of letters/digits/hyphens (no leading/
# trailing hyphen), joined by dots, 1-253 chars overall. Deliberately
# permissive about single-label entries (e.g. "google" itself is a
# Google-operated gTLD pulled in via v2fly's includes).
HOSTNAME_RE = re.compile(
    r"^(?!-)[a-z0-9-]{1,63}(?<!-)(\.(?!-)[a-z0-9-]{1,63}(?<!-))*$"
)

dropped_keyword_regexp_count = 0


def normalise_hostname(raw):
    """
    Lowercase; strip surrounding whitespace, a scheme (if any), any
    path/query/fragment, a port, and a trailing dot. Return None if the
    result is empty or not a plausible hostname.
    """
    value = raw.strip()
    if not value:
        return None

    value = value.lower()

    # Strip a scheme like "https://" if present.
    if "://" in value:
        value = value.split("://", 1)[1]

    # If it still looks URL-ish (has a path/query/fragment), let urlsplit
    # pull just the host (and drop any port) out; otherwise treat the
    # whole string as a bare host[:port].
    if "/" in value or "?" in value or "#" in value:
        parsed = urlsplit("//" + value)
        value = parsed.hostname or ""
    else:
        # Strip a trailing port, e.g. "example.com:8080".
        value = value.split(":", 1)[0]

    value = value.strip().rstrip(".")

    if not value:
        return None

    if not HOSTNAME_RE.match(value):
        return None

    return value


def parse_source1(lines):
    """
    Source 1 lines come as leading-dot domains (e.g. ".google.ad").
    process_stream() has already dropped '#' comments and blank lines.
    The leading dot is stripped: entries are stored bare (see the
    `type: "hostname"` decision above).
    """
    result = set()
    for line in lines:
        host = normalise_hostname(line.lstrip("."))
        if host is None:
            continue
        result.add(host)
    return result


def parse_source2(lines):
    """
    Source 2 is a hosts file: "0.0.0.0 <domain>". process_stream() has
    already dropped '#' comments (including the "Last updated:" banner)
    and blank lines.
    """
    result = set()
    for line in lines:
        fields = line.split()
        if len(fields) < 2:
            continue
        domain = fields[1]
        host = normalise_hostname(domain)
        if host is None:
            continue
        result.add(host)
    return result


def fetch_v2fly_file(name, visited, depth):
    """
    Fetch one v2fly domain-list-community data file (recursing into any
    `include:` directives it contains) and return the set of bare,
    normalised hostnames it yields.

    `visited` guards against cycles/re-fetching a file already pulled
    in by another include chain. `depth` is checked against
    MAX_INCLUDE_DEPTH to bound recursion regardless of `visited`.
    """
    global dropped_keyword_regexp_count

    result = set()

    if name in visited:
        return result
    visited.add(name)

    if depth > MAX_INCLUDE_DEPTH:
        logging.warning(
            "generate-google: MAX_INCLUDE_DEPTH exceeded while following "
            "v2fly include chain at '{}', abandoning this branch".format(name)
        )
        return result

    url = SOURCE_3_BASE + name
    lines = process_stream(url)

    for line in lines:
        entry = line.strip()
        if not entry:
            continue

        # Strip trailing " @tag" attributes (e.g. " @cn", " @ads").
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

        host = normalise_hostname(domain)
        if host is None:
            continue
        result.add(host)

    return result


def parse_source3():
    visited = set()
    return fetch_v2fly_file(SOURCE_3_ROOT, visited, 0)


def main():
    # --- Source 1 ---
    source1_raw = process_stream(SOURCE_1_URL)
    source1 = parse_source1(source1_raw)
    logging.info(
        "generate-google: source1 (supported_domains) raw={} kept={}".format(
            len(source1_raw), len(source1)
        )
    )

    # --- Source 2 ---
    source2_raw = process_stream(SOURCE_2_URL)
    source2 = parse_source2(source2_raw)
    logging.info(
        "generate-google: source2 (no-google) raw={} kept={}".format(
            len(source2_raw), len(source2)
        )
    )

    # --- Source 3 (recursive, follows include:) ---
    source3 = parse_source3()
    logging.info(
        "generate-google: source3 (v2fly domain-list-community) kept={} "
        "dropped_keyword_or_regexp={}".format(
            len(source3), dropped_keyword_regexp_count
        )
    )

    merged = source1 | source2 | source3
    pre_dedup_total = len(source1_raw) + len(source2_raw)  # source3 counted post-parse (recursive files)
    logging.info(
        "generate-google: overlap source1&source2={} source1&source3={} "
        "source2&source3={} all-three={}".format(
            len(source1 & source2),
            len(source1 & source3),
            len(source2 & source3),
            len(source1 & source2 & source3),
        )
    )
    logging.info(
        "generate-google: merged unique count={} (source1={}, source2={}, "
        "source3={}, pre-merge raw lines seen source1+source2={})".format(
            len(merged), len(source1), len(source2), len(source3), pre_dedup_total
        )
    )

    # Union with the entries already committed, never replace them. The three
    # upstream sources between them do not cover every domain the frozen list
    # carried, and a domain Google operated in the past is still worth
    # recognising in a false-positive warninglist, so the generator only ever
    # adds. Existing entries are normalised through the same path as the
    # sources, which also strips the old leading-dot convention.
    try:
        with open(get_abspath_list_file("google")) as existing_file:
            for entry in json.load(existing_file)["list"]:
                normalised = normalise_hostname(entry)
                if normalised:
                    merged.add(normalised)
    except (IOError, OSError, ValueError, KeyError):
        pass

    google_warninglist = {
        "description": (
            "Event contains one or more entries of known google domains, "
            "merged from Google's own supported_domains list, the "
            "nickspaargaren/no-google community blocklist, and the v2fly "
            "domain-list-community 'google' data set."
        ),
        "version": get_version(),
        "name": "List of known google domains",
        # type: "hostname" (changed from the frozen list's "string"), with
        # bare, dot-free entries -- see the DECISION block at the top of
        # this file for why: type "string" is a byte-for-byte exact match
        # in MISP core with no dot special-casing, so leading-dot "string"
        # entries never actually match a real hostname attribute value.
        "type": "hostname",
        "list": sorted(merged),
        "matching_attributes": ["domain", "hostname", "domain|ip", "url"],
    }

    write_to_file(google_warninglist, "google")


if __name__ == "__main__":
    main()
