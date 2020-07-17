#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import zipfile

from generator import download_to_file, get_abspath_list_file, get_version


def process(file, warninglist, dst, limit='1k'):

    with zipfile.ZipFile(file, 'r') as cisco_lists:
        for name in cisco_lists.namelist():
            if name == "top-1m.csv":
                with cisco_lists.open(name) as cisco_list:
                    if limit == '1k':
                        top = cisco_list.readlines()[:1000]
                    elif limit == '5k':
                        top = cisco_list.readlines()[:5000]
                    elif limit == '10k':
                        top = cisco_list.readlines()[:10000]
                    elif limit == '20k':
                        top = cisco_list.readlines()[:20000]
            else:
                continue

    warninglist['version'] = get_version()
    warninglist['type'] = 'hostname'
    warninglist['matching_attributes'] = [
        'hostname', 'domain', 'url', 'domain|ip']
    warninglist['list'] = []

    for site in top:
        v = site.decode('UTF-8').split(',')[1]
        warninglist['list'].append(v.strip().replace('\\r\\n', ''))
    warninglist['list'] = sorted(set(warninglist['list']))

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


if __name__ == '__main__':
    cisco_url = "http://s3-us-west-1.amazonaws.com/umbrella-static/top-1m.csv.zip"
    cisco_file = "cisco_top-1m.csv.zip"

    download_to_file(cisco_url, cisco_file)

    cisco_dst_1k = 'cisco_top1000'
    cisco_1k_warninglist = {
        'name': 'Top 1000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 1000 of the most used websites (Cisco Umbrella).'
    }
    process(cisco_file, cisco_1k_warninglist, cisco_dst_1k, limit='1k')

    cisco_dst_5k = 'cisco_top5k'
    cisco_5k_warninglist = {
        'name': 'Top 5000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 5000 of the most used websites (Cisco Umbrella).'
    }
    process(cisco_file, cisco_5k_warninglist, cisco_dst_5k, limit='5k')

    cisco_dst_10k = 'cisco_top10k'
    cisco_10k_warninglist = {
        'name': 'Top 10 000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 10 000 of the most used websites (Cisco Umbrella).'
    }
    process(cisco_file, cisco_10k_warninglist, cisco_dst_10k, limit='10k')

    cisco_dst_20k = 'cisco_top20k'
    cisco_20k_warninglist = {
        'name': 'Top 20 000 websites from Cisco Umbrella',
        'description': 'Event contains one or more entries from the top 20 000 of the most used websites (Cisco Umbrella).'
    }
    process(cisco_file, cisco_20k_warninglist, cisco_dst_20k, limit='20k')
