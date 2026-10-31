#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import (
    download, split_hostname_entries, get_version, write_to_file, write_exact_match_warninglist
)

# The list is of type "hostname", so an entry also matches all its subdomains.
# Public suffixes and their parents (e.g. "ruhr-uni-bochum.de", or
# "kuleuven.be" whose ezproxy.kuleuven.be serves third-party sites as
# subdomains) are dropped by split_hostname_entries() itself. The dropped
# entries go to the exact-match list university_domains-exact.
TOO_WIDE = {
    # National Defence Academy of Latvia: would match all of the Latvian
    # military's mil.lv
    "mil.lv",
}

# Values seen in the dataset that are not domains. None so far: malformed
# values are caught by the syntax check in filter_hostname_entries().
JUNK = set()


def process(url, dst):

    university_list = download(url).json()

    warninglist = {
        'type': "hostname",
        'name': "University domains",
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip'],
        'version': get_version(),
        'description': "List of University domains from https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json",
        'list': []
    }

    for university in university_list:
        for domain in university.get('domains'):
            if domain not in warninglist['list']:
                warninglist['list'].append(domain)

    warninglist['list'], too_wide = split_hostname_entries(warninglist['list'], too_wide=TOO_WIDE, junk=JUNK)

    write_to_file(warninglist, dst)

    write_exact_match_warninglist(
        too_wide,
        dst + '-exact',
        "University domains too wide for hostname matching (exact match)",
        "University domains from https://raw.githubusercontent.com/Hipo/university-domains-list/master/"
        "world_universities_and_domains.json that the university_domains list leaves out because it matches "
        "hostnames: a public suffix, a domain a public suffix sits under, or a domain shared with other "
        "organisations. Matched exactly, so the domain itself is flagged but names registered under it are not.",
        matching_attributes=('hostname', 'domain', 'domain|ip'),
    )


if __name__ == '__main__':
    university_url = 'https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json'
    university_dst = 'university_domains'

    process(university_url, university_dst)
