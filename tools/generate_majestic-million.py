#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import (
    MULTI_TENANT_DOMAINS, download_to_file, filter_hostname_entries, get_version, write_to_file, get_abspath_source_file
)
import argparse

# The list is of type "hostname", so an entry also matches all its subdomains.
# Entries whose subdomains belong to third parties are dropped; public
# suffixes and their parents are dropped by filter_hostname_entries() itself.
TOO_WIDE = MULTI_TENANT_DOMAINS

# Values seen in the dataset that are not domains. None so far: malformed
# values are caught by the syntax check in filter_hostname_entries().
JUNK = set()


def process(file, dst, numbers):

    with open(get_abspath_source_file(file), newline='\n', encoding='utf-8', errors='replace') as csv_file:
        sites = csv_file.readlines()[1:numbers + 1]

    warninglist = {
        'name': f'Top {numbers} websites from Majestic Million',
        'version': get_version(),
        'description': f'Event contains one or more entries from the top {numbers} of the most used websites (Majestic Million).',
        'matching_attributes': ['hostname', 'domain'],
        'type': 'hostname',
        'list': []
    }

    domains = [site.split(',')[2] for site in sites]
    warninglist['list'] = filter_hostname_entries(domains, too_wide=TOO_WIDE, junk=JUNK)

    write_to_file(warninglist, dst)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-n", help="number of website to process", required=True)
    args = parser.parse_args()

    majestic_url = 'http://downloads.majestic.com/majestic_million.csv'
    majestic_file = 'majestic_million.csv'
    majestic_dst = 'majestic_million'

    download_to_file(majestic_url, majestic_file)
    process(majestic_file, majestic_dst, int(args.n))
