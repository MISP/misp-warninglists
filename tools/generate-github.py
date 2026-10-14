#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    github = download("https://api.github.com/meta")
    parsed = json.loads(github.text)

    # List of keys in the meta data that might contain IP networks
    ip_keys = ['hooks', 'web', 'api', 'git', 'pages', 'importer', 'actions']

    ranges = []

    for key in ip_keys:
      ranges += [p for p in parsed[key]]

    warninglist = {
        'name': 'List of known GitHub IP ranges (https://api.github.com/meta)',
        'version': get_version(),
        'description': "GitHub IP address ranges (https://api.github.com/meta)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr',
        'list': consolidate_networks(ranges),
    }

    write_to_file(warninglist, "github")
