#!/usr/bin/env python3

import json

from generator import download_to_file, get_abspath_list_file, get_version


def process(files, dst):
    warninglist = {}
    warninglist['name'] = "List of known Cloudflare IP ranges"
    warninglist['version'] = get_version()
    warninglist['description'] = "List of known Cloudflare IP ranges (https://www.cloudflare.com/ips/)"
    warninglist['type'] = "cidr"
    warninglist['list'] = []
    warninglist['matching_attributes'] = ["ip-dst", "ip-src", "domain|ip"]

    for file in files:
        with open(file, 'r') as f:
            ips = f.readlines()
        for ip in ips:
            warninglist['list'].append(ip.strip())
        warninglist['list'] = sorted(set(warninglist['list']))

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


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
