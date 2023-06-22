#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download, get_version, write_to_file


def process(url, dst):
    DSList = download(url).text.strip().split("\n")
    
    warninglist = {
        'name': 'OSINT.DigitalSide.IT Warning List',
        'version': get_version(),
        'description': '"OSINT DigitalSide Threat-Intel Repository - MISP Warninglist - List of domains should be marked as false positive in the related MISP event with IDS attribute not flagged',
        'type': 'hostname',
        'list': DSList,
        'matching_attributes': ["hostname", "domain"]
    }
    
    write_to_file(warninglist, dst)


if __name__ == '__main__':
    digitalside_url = 'https://raw.githubusercontent.com/davidonzo/Threat-Intel-Domain-WL/main/OSINT.DigitalSide-Threat-Intel-Domain-WL.txt'
    digitalside_dst = 'digitalside'

    process(digitalside_url, digitalside_dst)
