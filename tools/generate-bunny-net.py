#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def process(files, dst):
    warninglist = {
        'name': "List of known Bunny.net CDN ranges",
        'version': get_version(),
        'description': "List of known Bunny.net CDN IP ranges (https://support.bunny.net/hc/en-us/articles/115003578911-How-to-detect-when-BunnyCDN-PoP-servers-are-accessing-your-backend)",
        'type': "cidr",
        'list': [],
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    for file in files:
        with open(get_abspath_source_file(file), 'r') as f:
            ips = f.readlines()
        for ip in ips:
            warninglist['list'].append(ip.strip())

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    bunny_net_base_uri = "https://bunnycdn.com/api/system/edgeserverlist/"
    uri_list = ['', 'IPv6']
    bunny_net_dst = 'bunny-net'

    to_process = list()

    for uri in uri_list:
        url = bunny_net_base_uri + uri + "/plain"
        file = 'bunny_net_{}.txt'.format(uri)
        download_to_file(url, file)
        to_process.append(file)

    process(to_process, bunny_net_dst)
