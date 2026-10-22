#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download, filter_hostname_entries, get_version, write_to_file

# The list is of type "hostname", so an entry also matches all its subdomains.
# Public suffixes and their parents (e.g. "ruhr-uni-bochum.de", or
# "kuleuven.be" whose ezproxy.kuleuven.be serves third-party sites as
# subdomains) are dropped by filter_hostname_entries() itself.
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

    warninglist['list'] = filter_hostname_entries(warninglist['list'], too_wide=TOO_WIDE, junk=JUNK)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    university_url = 'https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json'
    university_dst = 'university_domains'

    process(university_url, university_dst)
