#!/usr/bin/env python3
"""
Generate a warninglist of known Windows 11 connection endpoints.

Sources (both are merged, then deduplicated):
  - https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints
    (Windows 11 Enterprise, Education, and Pro editions)
  - https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions
    (Windows 11 non-Enterprise editions)

Source choice: both Learn pages were probed with plain `requests` (no JS
execution) and returned fully server-rendered HTML containing clean
`<table>` markup with the endpoint data already present (verified with
curl/BeautifulSoup: 1 table / 3 tables respectively, rows readable
directly). Since the rendered HTML is reliable and directly parseable,
it is used as the source instead of the raw markdown mirror on GitHub
(MicrosoftDocs/windows-itpro-docs) -- fetching HTML avoids an extra
GitHub dependency/rate limit and matches what a human reading the page
actually sees.

Normalisation rules applied to each "Destination" table cell:
  - Row is skipped if it has fewer than 4 cells (Area/Description/
    Protocol/Destination) -- this drops header rows and any malformed
    rows.
  - A cell can contain multiple endpoints separated by an HTML <br>;
    these are split into separate entries.
  - Any inline link text (e.g. "Learn how to turn off traffic to ...")
    used in place of a real destination is dropped -- detected by the
    absence of a dot and presence of whitespace/uppercase prose.
  - Leading/trailing whitespace is stripped.
  - A URL scheme (http:// or https://) is stripped, then everything
    from the first "/" onward (path) is stripped.
  - A trailing ":port" is stripped.
  - A leading "*" (with or without a following ".") is normalised to a
    single leading "." to match this repository's existing wildcard
    convention (see lists/microsoft-win10-connection-endpoints), e.g.
    "*.smartscreen-prod.microsoft.com" -> ".smartscreen-prod.microsoft.com"
    and "*displaycatalog.mp.microsoft.com" -> ".displaycatalog.mp.microsoft.com".
  - A trailing "*" (used inconsistently on the source page, with no
    accompanying footnote) is stripped as a rendering artifact rather
    than kept as a wildcard, e.g. "arc.msn.com*" -> "arc.msn.com".
  - Empty strings, and any value that still contains whitespace, a
    backtick, a pipe character, or has no "." after the above cleanup,
    are dropped as not being a plausible hostname.
"""

import re

from bs4 import BeautifulSoup

from generator import download, get_version, write_to_file

lists = [
    "https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints",
    "https://learn.microsoft.com/en-us/windows/privacy/windows-11-endpoints-non-enterprise-editions",
]


def normalise(raw):
    value = raw.strip()
    if not value:
        return None

    # Strip URL scheme
    value = re.sub(r'^[a-zA-Z][a-zA-Z0-9+.-]*://', '', value)
    # Strip path/query (everything from the first "/")
    value = value.split('/', 1)[0]
    # Strip trailing port
    value = re.sub(r':\d+$', '', value)

    value = value.strip()
    if not value:
        return None

    # Leading wildcard: "*.foo.com" or "*foo.com" -> ".foo.com"
    if value.startswith('*'):
        value = '.' + value.lstrip('*').lstrip('.')
    # Trailing wildcard artifact: "foo.com*" -> "foo.com"
    value = value.rstrip('*')

    value = value.strip()
    if not value:
        return None

    # Reject anything that still isn't a plausible bare hostname
    if any(ch in value for ch in (' ', '`', '|', '<', '>')):
        return None
    if '.' not in value:
        return None

    return value.lower()


def get_destinations(url):
    destinations = []
    req = download(url)
    soup = BeautifulSoup(req.text, "html.parser")
    tables = soup.find_all("table")
    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all(["td", "th"])
            if len(cells) < 4:
                continue
            dest_cell = cells[3]
            # Split on <br> tags first, preserving each fragment.
            raw_values = dest_cell.get_text(separator="\n", strip=True).split("\n")
            for raw_value in raw_values:
                value = normalise(raw_value)
                if value:
                    destinations.append(value)
    return destinations


if __name__ == '__main__':
    misp_warninglist = {
        'name': 'List of known Windows 11 connection endpoints',
        'version': get_version(),
        'description': 'Event contains one or more entries of known Windows 11 connection endpoints (https://learn.microsoft.com/en-us/windows/privacy/manage-windows-11-endpoints)',
        'type': 'string',
        'matching_attributes': ['domain', 'hostname', 'domain|ip'],
    }

    endpoints = []
    for list_url in lists:
        endpoints.extend(get_destinations(list_url))

    misp_warninglist['list'] = endpoints

    write_to_file(misp_warninglist, 'microsoft-win11-connection-endpoints')
