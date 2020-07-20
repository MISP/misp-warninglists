#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download, get_version, write_to_file


def process(url, dst):

    university_list = download(url).json()

    warninglist = {
        'type': "hostname",
        'name': "University domains",
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip'],
        'version': get_version(),
        'description': "List of University domains from https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json",
        'list': []
    }

    for university in university_list:
        for domain in university.get('domains'):
            if domain not in warninglist['list']:
                warninglist['list'].append(domain)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    university_url = 'https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json'
    university_dst = 'university_domains'

    process(university_url, university_dst)
