#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from generator import download, download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks


def get_json_url(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    retry_link_text = soup.find(class_='link-align')
    retry_links = retry_link_text.find_all('a')
    return retry_links[0].get('href')


def process(file, dst, name: str, description: str):
    warninglist = {
        'name': name,
        'version': get_version(),
        'description': description,
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"],
        'type': 'cidr'
    }

    with open(get_abspath_source_file(file), 'r') as json_file:
        ms_azure_ip_list = json.load(json_file)

    values = []
    for value in ms_azure_ip_list['values']:
        values += value['properties']['addressPrefixes']

    warninglist['list'] = consolidate_networks(values)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    TYPES = [
        {
            "name": "List of known Microsoft Azure Datacenter IP Ranges",
            "description": "Microsoft Azure Datacenter IP Ranges",
            "url": "https://download.microsoft.com/download/7/1/D/71D86715-5596-4529-9B13-DA13A5DE5B63/ServiceTags_Public_20241216.json",
            "file": "ms-azure.json",
            "destination_folder": "microsoft-azure",
        }
   ]

    for type in TYPES:
        ms_azure_json_url = get_json_url(download(type["url"]))
        download_to_file(ms_azure_json_url, type["file"])
        process(type["file"], type["destination_folder"], type["name"], type["description"])
