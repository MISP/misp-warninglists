#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from generator import get_version, write_to_file, Dns, consolidate_networks, create_resolver


if __name__ == '__main__':
    spf = Dns(create_resolver())
    warninglist = {
        'name': "List of known Gmail sending IP ranges",
        'version': get_version(),
        'description': "List of known Gmail sending IP ranges (https://support.google.com/a/answer/27642?hl=en)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"],
        'type': 'cidr',
        'list': consolidate_networks(spf.get_ip_ranges_from_spf("gmail.com")),
    }

    write_to_file(warninglist, "google-gmail-sending-ips")
