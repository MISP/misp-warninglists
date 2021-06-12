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
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"],
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
            "url": "https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519",
            "file": "ms-azure.json",
            "destination_folder": "microsoft-azure",
        },
        {
            "name": "List of known Microsoft Azure US Government Cloud Datacenter IP Ranges",
            "description": "Microsoft Azure US Government Cloud Datacenter IP Ranges",
            "url": "https://www.microsoft.com/en-us/download/confirmation.aspx?id=57063",
            "file": "ms-azure-us-gov.json",
            "destination_folder": "microsoft-azure-us-gov",
        },
        {
            "name": "List of known Microsoft Azure Germany Datacenter IP Ranges",
            "description": "Microsoft Azure Germany Datacenter IP Ranges",
            "url": "https://www.microsoft.com/en-us/download/confirmation.aspx?id=57064",
            "file": "ms-azure-germany.json",
            "destination_folder": "microsoft-azure-germany",
        },
        {
            "name": "List of known Microsoft Azure China Datacenter IP Ranges",
            "description": "Microsoft Azure China Datacenter IP Ranges",
            "url": "https://www.microsoft.com/en-us/download/confirmation.aspx?id=57062",
            "file": "ms-azure-china.json",
            "destination_folder": "microsoft-azure-china",
        }
    ]

    for type in TYPES:
        ms_azure_json_url = get_json_url(download(type["url"]))
        download_to_file(ms_azure_json_url, type["file"])
        process(type["file"], type["destination_folder"], type["name"], type["description"])
