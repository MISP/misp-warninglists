#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks


def process(file, dst):
    with open(get_abspath_source_file(file), 'r') as json_file:
        oci_ip_list = json.load(json_file)
    l = []

    for region in oci_ip_list['regions']:
        for cidr in region['cidrs']:
            l.append(cidr['cidr'])

    warninglist = {
        'name': 'List of known Oracle Cloud Infrastructure (OCI) IP address ranges',
        'version': get_version(),
        'description': 'Oracle Cloud Infrastructure (OCI) IP address ranges (https://docs.oracle.com/en-us/iaas/Content/General/Concepts/addressranges.htm)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    oci_url = "https://docs.oracle.com/en-us/iaas/tools/public_ip_ranges.json"
    oci_file = "oracle_oci_ip-ranges.json"
    oci_dst = "oracle-oci"

    download_to_file(oci_url, oci_file)
    process(oci_file, oci_dst)
