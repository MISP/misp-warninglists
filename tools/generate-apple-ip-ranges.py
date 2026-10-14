#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import ipaddress
import json

from generator import download, get_version, write_to_file, consolidate_networks

ASNS = ["AS714", "AS6185"]


def fetch_prefixes(asn):
    url = "https://stat.ripe.net/data/announced-prefixes/data.json?resource={}".format(asn)
    r = download(url)
    data = json.loads(r.text)
    return [entry["prefix"] for entry in data["data"]["prefixes"]]


def process(dst, name, description, prefixes):
    warninglist = {
        'name': name,
        'version': get_version(),
        'description': description,
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr'
    }

    warninglist['list'] = consolidate_networks(prefixes)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    all_prefixes = []
    for asn in ASNS:
        all_prefixes.extend(fetch_prefixes(asn))

    ipv4_prefixes = [p for p in all_prefixes if ipaddress.ip_network(p).version == 4]
    ipv6_prefixes = [p for p in all_prefixes if ipaddress.ip_network(p).version == 6]

    process(
        "apple-ipv4",
        "List of known Apple IPv4 ranges",
        "Apple IPv4 ranges announced by AS714 and AS6185",
        ipv4_prefixes,
    )
    process(
        "apple-ipv6",
        "List of known Apple IPv6 ranges",
        "Apple IPv6 ranges announced by AS714 and AS6185",
        ipv6_prefixes,
    )
