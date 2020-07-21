#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download, get_version, write_to_file


def process(url, dst):
    warninglist = {
        'name': 'TLDs as known by IANA',
        'version': get_version(),
        'description': 'Event contains one or more TLDs as attribute with an IDS flag set',
        'list': [],
        'matching_attributes': ["hostname", "domain", "domain|ip"],
        'type': 'string'
    }

    r = download(url)
    for tld in r.text.splitlines():
        if tld.startswith('#'):
            continue
        warninglist['list'].append(tld)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    tlds_url = 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'
    tlds_dst = 'tlds'

    process(tlds_url, tlds_dst)
