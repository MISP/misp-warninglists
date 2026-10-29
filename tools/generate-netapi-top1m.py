#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

from generator import download_to_file, get_abspath_source_file, get_version, write_to_file


def process(file):
    all_sites = get_list(file)

    # Top 1M
    generate(all_sites, {
        'name': "Top 1,000,000 most popular websites from NetAPI",
        'description': "Event contains one or more entries from the NetAPI Top 1M (https://netapi.com/top-1-mln-websites/), a daily ranking of the 1,000,000 most popular websites as registrable domains, published under CC BY 4.0."
    }, "netapi-top1m")

    # Top 10K
    generate(all_sites[:10000], {
        'name': "Top 10K most popular websites from NetAPI",
        'description': "Event contains one or more entries from the top 10K of the NetAPI Top 1M (https://netapi.com/top-1-mln-websites/), a daily ranking of the most popular websites as registrable domains, published under CC BY 4.0."
    }, "netapi-top10k")

    # Top 1K
    generate(all_sites[:1000], {
        'name': "Top 1K most popular websites from NetAPI",
        'description': "Event contains one or more entries from the top 1K of the NetAPI Top 1M (https://netapi.com/top-1-mln-websites/), a daily ranking of the most popular websites as registrable domains, published under CC BY 4.0."
    }, "netapi-top1k")


def generate(sites, warninglist, dst):
    warninglist['type'] = 'hostname'
    warninglist['version'] = get_version()
    warninglist['matching_attributes'] = ['hostname', 'domain', 'url', 'domain|ip']
    warninglist['list'] = list(sites)

    write_to_file(warninglist, dst)


def get_list(file):
    # CSV with a header line: NetAPI_Rank,Domain - rows are already in rank order
    sites = []
    with open(get_abspath_source_file(file), newline='') as csv_file:
        reader = csv.reader(csv_file)
        next(reader)
        for row in reader:
            domain = row[1].strip().lower()
            if domain:
                sites.append(domain)

    return sites


if __name__ == '__main__':
    netapi_url = 'https://netapi.com/netapi_top1mln.csv'
    netapi_file = 'netapi_top1mln.csv'

    download_to_file(netapi_url, netapi_file)
    process(netapi_file)
