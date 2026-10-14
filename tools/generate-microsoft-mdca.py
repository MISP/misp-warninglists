#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from generator import download_to_file, get_version, write_to_file, get_abspath_source_file

ip_regex = re.compile(r"> - `\*([.a-z-]+)`")

def process(file, dst):
    warninglist = {
        'name': "List of known Microsoft Defender for Cloud Apps (MDCA/MCAS) proxy hostnames",
        'version': get_version(),
        'description': "Microsoft Defender for Cloud Apps (MDCA/MCAS) hostnames (https://learn.microsoft.com/en-us/defender-cloud-apps/troubleshooting-proxy-url)",
        'type': "hostname",
        'list': [],
        'matching_attributes': [
            "hostname",
            "domain",
            "url",
            "domain|ip"
        ]
    }

    with open(get_abspath_source_file(file), 'r') as f:
        file_contents = f.readlines()
        for line in file_contents:
            warninglist['list'].extend(list(map(lambda x: ''.join(x), ip_regex.findall(line))))

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    source = "https://raw.githubusercontent.com/MicrosoftDocs/defender-docs/refs/heads/public/defender-for-cloud-apps/troubleshooting-proxy-url.md"
    file = "microsoft-mdca-proxy.md"
    download_to_file(source, file)
    process(file, "microsoft-mdca-proxy")
