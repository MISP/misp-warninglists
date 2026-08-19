#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from generator import download_to_file, get_version, write_to_file, get_abspath_source_file

ip_regex = re.compile(r"(\d{1,3}(?:\.\d{1,3}){3})|((?:[\da-f]{1,4}:){7}(?:[\da-f]{1,4}))|((?:[\da-f]{1,4}:){1,6}:(?:[\da-f]{1,4}){1,6})")

def process(file, dst):
    warninglist = {
        'name': "List of known OVH Cluster IPs",
        'version': get_version(),
        'description': "OVH Cluster IP address (https://docs.ovhcloud.com/en/guides/web-cloud/web-hosting/clusters-and-shared-hosting-ip)",
        'type': "cidr",
        'list': [],
        'matching_attributes': [
            "ip-src",
            "ip-dst",
            "domain|ip",
            "ip-src|port",
            "ip-dst|port"
        ]
    }

    with open(get_abspath_source_file(file), 'r') as f:
        file_contents = f.readlines()
        for line in file_contents:
            warninglist['list'].extend(list(map(lambda x: ''.join(x), ip_regex.findall(line))))

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    source = "https://raw.githubusercontent.com/ovh/ovhcloud-docs/refs/heads/develop/docs/en/guides/web-cloud/web-hosting/clusters-and-shared-hosting-ip.mdx"
    file = "ovh_cluster.txt"
    download_to_file(source, file)
    process(file, "ovh-cluster")
