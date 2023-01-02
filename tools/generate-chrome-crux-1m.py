#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import gzip
from urllib.parse import urlparse

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(files, dst):

    warninglist = {
        'description': "Cached Chrome Top Million Websites - top 1 million",
        'version': get_version(),
        'name': "google-chrome-crux-1million",
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
                    print(True)
                    continue
                v = row[0]
                p = urlparse(v)
                host = p.hostname
                warninglist['list'].append(host)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    crux_domains_url = "https://github.com/zakird/crux-top-lists/raw/main/data/global/current.csv.gz"

    crux_domains_file = "crux-top-1m.csv.gz"

    dst = 'google-chrome-crux-1million'

    download_to_file(crux_domains_url, crux_domains_file, gzip_enable=True)

    process([crux_domains_file], dst)
