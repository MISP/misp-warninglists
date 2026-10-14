#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import process_stream, get_version, write_to_file, consolidate_networks


def process(url, dst):
    # RFC 8805 geofeed: ip_prefix,country,region,city,postal_code
    ranges = [line.split(',')[0].strip() for line in process_stream(url)]

    warninglist = {
        'name': 'List of known VPN by Google egress IP address ranges',
        'version': get_version(),
        'description': 'VPN by Google (formerly Google One VPN) egress IP address ranges, from the self-published RFC 8805 geofeed ({})'.format(url),
        'type': 'cidr',
        'list': consolidate_networks(ranges),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    # Previously published at https://www.gstatic.com/g1vpn/geofeed, which now redirects here
    google_vpn_url = 'https://www.gstatic.com/vpn/geofeed'
    google_vpn_dst = 'google-vpn'

    process(google_vpn_url, google_vpn_dst)
