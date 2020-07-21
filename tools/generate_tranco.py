#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile

from generator import download_to_file, get_version, write_to_file


def process(file):
    top10k, all_sites = get_lists(file)

    # Top 1M
    tranco_dst = "tranco"
    tranco_warninglist = {
        'description': "Event contains one or more entries from the top 1,000,000 most-used sites (https://tranco-list.eu/).",
        'name': "Top 1,000,000 most-used sites from Tranco"
    }
    generate(all_sites, tranco_warninglist, tranco_dst)

    # Top 10K
    tranco_10k_dst = "tranco10k"
    tranco_10k_warninglist = {
        'description': "Event contains one or more entries from the top 10K most-used sites (https://tranco-list.eu/).",
        'name': "Top 10K most-used sites from Tranco"
    }
    generate(top10k, tranco_10k_warninglist, tranco_10k_dst)


def generate(sites, warninglist, dst):

    warninglist['type'] = 'hostname'
    warninglist['version'] = get_version()
    warninglist['matching_attributes'] = [
        'hostname', 'domain', 'url', 'domain|ip']
    warninglist['list'] = []

    for site in sites:
        v = site.decode('UTF-8').split(',')[1]
        warninglist['list'].append(v.rstrip())

    write_to_file(warninglist, dst)


def get_lists(file):
    with zipfile.ZipFile(file, 'r') as tranco_lists:
        for name in tranco_lists.namelist():
            if name == 'top-1m.csv':
                with tranco_lists.open(name) as tranco:
                    all_sites = tranco.readlines()
                    top10k = all_sites[:10000]
            else:
                continue

    return top10k, all_sites


if __name__ == '__main__':
    tranco_url = 'https://tranco-list.eu/top-1m.csv.zip'
    tranco_file = 'tranco_top-1m.csv.zip'

    download_to_file(tranco_url, tranco_file)

    process(tranco_file)
