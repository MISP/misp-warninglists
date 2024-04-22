#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download, download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks

def process(file, dst, name: str, description: str, prefixlist: str, prefixitem: str):
    warninglist = {
        'name': name,
        'version': get_version(),
        'description': description,
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr'
    }

    with open(get_abspath_source_file(file), 'r') as json_file:
        tenable_ip_list = json.load(json_file)

    values = []
    for value in tenable_ip_list[prefixlist]:
        values.append(value[prefixitem])

    warninglist['list'] = consolidate_networks(values)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    TYPES = [
        {
            "name": "List of known Tenable Cloud Sensors IPv4",
            "description": "Tenable IPv4 Cloud Sensor addresses used for scanning Internet-facing infrastructure",
            "url": "https://docs.tenable.com/ip-ranges/data.json",
            "file": "tenable-cloud.json",
            "destination_folder": "tenable-cloud-ipv4",
            "prefixlist": "prefixes",
            "prefixitem": "ip_prefix",
        },
        {
            "name": "List of known Tenable Cloud Sensors IPv6",
            "description": "Tenable IPv6 Cloud Sensor addresses used for scanning Internet-facing infrastructure",
            "url": "https://docs.tenable.com/ip-ranges/data.json",
            "file": "tenable-cloud.json",
            "destination_folder": "tenable-cloud-ipv6",
            "prefixlist": "ipv6_prefixes",
            "prefixitem": "ipv6_prefix",
        }
    ]

    for type in TYPES:
        tenable_json_url = type["url"]
        download_to_file(tenable_json_url, type["file"])
        process(type["file"], type["destination_folder"], type["name"], type["description"], type["prefixlist"], type["prefixitem"])
