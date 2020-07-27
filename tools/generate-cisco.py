#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(file):
    top1k, top5k, top10k, top20k = get_lists(file)

    cisco_dst_1k = 'cisco_top1000'
    cisco_1k_warninglist = {
        'name': 'Top 1000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 1000 of the most used websites (Cisco Umbrella).'
    }
    generate(top1k, cisco_1k_warninglist, cisco_dst_1k)

    cisco_dst_5k = 'cisco_top5k'
    cisco_5k_warninglist = {
        'name': 'Top 5000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 5000 of the most used websites (Cisco Umbrella).'
    }
    generate(top5k, cisco_5k_warninglist, cisco_dst_5k)

    cisco_dst_10k = 'cisco_top10k'
    cisco_10k_warninglist = {
        'name': 'Top 10 000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 10 000 of the most used websites (Cisco Umbrella).'
    }
    generate(top10k, cisco_10k_warninglist, cisco_dst_10k)

    cisco_dst_20k = 'cisco_top20k'
    cisco_20k_warninglist = {
        'name': 'Top 20 000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 20 000 of the most used websites (Cisco Umbrella).'
    }
    generate(top20k, cisco_20k_warninglist, cisco_dst_20k)


def generate(sites, warninglist, dst):
    warninglist['version'] = get_version()
    warninglist['type'] = 'hostname'
    warninglist['matching_attributes'] = [
        'hostname', 'domain', 'url', 'domain|ip']
    warninglist['list'] = []

    for site in sites:
        v = site.decode('UTF-8').split(',')[1]
        warninglist['list'].append(v.strip().replace('\\r\\n', ''))

    write_to_file(warninglist, dst)


def get_lists(file):
    with zipfile.ZipFile(get_abspath_source_file(file), 'r') as cisco_lists:
        for name in cisco_lists.namelist():
            if name == "top-1m.csv":
                with cisco_lists.open(name) as cisco_list:
                    all = cisco_list.readlines()
                    top1k = all[:1000]
                    top5k = all[:5000]
                    top10k = all[:10000]
                    top20k = all[:20000]
            else:
                continue

    return top1k, top5k, top10k, top20k


if __name__ == '__main__':
    cisco_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    cisco_file = "cisco_top-1m.csv.zip"

    download_to_file(cisco_url, cisco_file)

    process(cisco_file)
