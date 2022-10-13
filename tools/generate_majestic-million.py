#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file
import argparse


def process(file, dst, numbers):

    with open(get_abspath_source_file(file), newline='\n', encoding='utf-8', errors='replace') as csv_file:
        sites = csv_file.readlines()[1:numbers]

    warninglist = {
        'name': f'Top {numbers} websites from Majestic Million',
        'version': get_version(),
        'description': 'Event contains one or more entries from the top 10K of the most used websites (Majestic Million).',
        'matching_attributes': ['hostname', 'domain'],
        'type': 'string',
        'list': []
    }

    for site in sites:
        v = site.split(',')[2]
        warninglist['list'].append(v.rstrip())

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
