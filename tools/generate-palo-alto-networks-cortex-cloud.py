#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from generator import download_to_file, get_version, write_to_file, get_abspath_source_file

# Rough IPv4 and IPv6 extraction regex taken from `generate-ovh.py`
ip_regex = re.compile(r'[" ](\d{1,3}(?:\.\d{1,3}){3})[\\:]')

def process(file, dst):
    warninglist = {
        'name': "List of known Palo Alto Cortex Cloud IP ranges",
        'version': get_version(),
        'description': "Palo Alto Cortex Cloud IP address ranges (https://docs.ovhcloud.com/en/guides/web-cloud/web-hosting/clusters-and-shared-hosting-ip)",
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
        file_contents = f.read()
        warninglist['list'].extend(list(map(lambda x: ''.join(x), ip_regex.findall(file_contents))))

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    source = "https://cortex-docs.paloaltonetworks.com/cortex-cloud-runtime-security/onboard-and-configure/deployment-steps-and-checklist/activate-cortex-cloud/enable-access-to-required-panw-resources"
    file = "palo-alto-networks-cortex-cloud.html"
    download_to_file(source, file)
    process(file, "palo-alto-networks-cortex-cloud")
