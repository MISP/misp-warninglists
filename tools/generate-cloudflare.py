#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(files, dst):
    warninglist = {
        'name': "List of known Cloudflare IP ranges",
        'version': get_version(),
        'description': "List of known Cloudflare IP ranges (https://www.cloudflare.com/ips/)",
        'type': "cidr",
        'list': [],
        'matching_attributes': ["ip-dst", "ip-src", "domain|ip"]
    }

    for file in files:
        with open(get_abspath_source_file(file), 'r') as f:
            ips = f.readlines()
        for ip in ips:
            warninglist['list'].append(ip.strip())

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    cf_base_url = "https://www.cloudflare.com/"
    uri_list = ['ips-v4', 'ips-v6']
    cf_dst = 'cloudflare'

    to_process = list()

    for uri in uri_list:
        url = cf_base_url+uri
        file = 'cloudflare_{}.txt'.format(uri)
        download_to_file(url, file)
        to_process.append(file)

    process(to_process, cf_dst)
