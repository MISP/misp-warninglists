#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, get_version, write_to_file


if __name__ == '__main__':
    cloud = download("https://www.gstatic.com/ipranges/cloud.json")
    parsed = json.loads(cloud.text)

    ranges = [p["ipv4Prefix"] if "ipv4Prefix" in p else p["ipv6Prefix"] for p in parsed["prefixes"]]

    warninglist = {
        'name': "List of known GCP (Google Cloud Platform) IP address ranges",
        'version': get_version(),
        'description': "GCP (Google Cloud Platform) IP address ranges (https://www.gstatic.com/ipranges/cloud.json)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"],
        'type': 'cidr',
        'list': ranges,
    }

    write_to_file(warninglist, "google-gcp")
