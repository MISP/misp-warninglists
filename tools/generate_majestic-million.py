#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(file, dst):

    with open(get_abspath_source_file(file), newline='\n', encoding='utf-8', errors='replace') as csv_file:
        sites = csv_file.readlines()[:10000]

    warninglist = {
        'name': 'Top 10K websites from Majestic Million',
        'version': get_version(),
        'description': 'Event contains one or more entries from the top 10K of the most used websites (Majestic Million).',
        'matching_attributes': ['hostname', 'domain'],
        'type': 'hostname',
        'list': []
    }

    for site in sites:
        v = site.split(',')[2]
        warninglist['list'].append(v.rstrip())

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    majestic_url = 'http://downloads.majestic.com/majestic_million.csv'
    majestic_file = 'majestic_million.csv'
    majestic_dst = 'majestic_million'

    download_to_file(majestic_url, majestic_file)
    process(majestic_file, majestic_dst)
