#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
from generator import download, get_version, write_to_file


if __name__ == '__main__':
    req = download("https://lots-project.com")
    soup = BeautifulSoup(req.text, 'html.parser')
    links = soup.find_all('a', class_='link', href=True, target=None)

    lots_list = []

    for link in links:
        if link.contents[0].startswith('*'):
            lots_list.append(link.contents[0].lstrip('*'))
        elif link.contents[0].startswith('www'):
            lots_list.append(link.contents[0].lstrip('www'))
        else:
            lots_list.append(link.contents[0])

    warninglist = {
        'name': 'List of LOTS (Living Off Trusted Sites) Project Domains',
        'version': get_version(),
        'description': 'List of popular legitimate domains from LOTS (Living Off Trusted Sites) Project used to conduct phishing, C&C, exfiltration or downloading tools to evade detection',
        'matching_attributes': ['domain', 'domain|ip', 'hostname', 'hostname|port', 'url'],
        'type': 'hostname',
        'list': lots_list
    }

    write_to_file(warninglist, "lots-project")
