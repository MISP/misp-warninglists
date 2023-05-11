#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


# TODO: Include MozRank
def process(files, dst):

    warninglist = {
        'description': "Event contains one or more entries from the top 500 of the most used domains from Moz.",
        'version': get_version(),
        'name': "Top 500 domains and pages from https://moz.com/top500",
        'type': 'string',
        'list': [],
        'matching_attributes': ['hostname', 'domain', 'uri', 'url']
    }

    flag = True

    for file in files:
        with open(get_abspath_source_file(file)) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if flag:
                    flag = False
                    continue
                v = row[1]
                warninglist['list'].append(v.rstrip().rstrip('/'))

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    moz_domains_url = "https://moz.com/top-500/download/?table=top500Domains"
    #moz_pages_url = "https://moz.com/top500/pages/csv"

    moz_domains_file = "moz-top500.domains.csv"
    #moz_pages_file = "moz-top500.pages.csv"

    moz_dst = 'moz-top500'

    download_to_file(moz_domains_url, moz_domains_file)
    #download_to_file(moz_pages_url, moz_pages_file)

    #process([moz_domains_file, moz_pages_file], moz_dst)
    process([moz_domains_file], moz_dst)
