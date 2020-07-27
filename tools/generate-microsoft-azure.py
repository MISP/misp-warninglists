#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from bs4 import BeautifulSoup

from generator import download, download_to_file, get_version, write_to_file, get_abspath_source_file


def get_json_url(page):
    soup = BeautifulSoup(page.text, 'html.parser')
    retry_link_text = soup.find(class_='link-align')
    retry_links = retry_link_text.find_all('a')
    return retry_links[0].get('href')


def process(file, dst):

    warninglist = {
        'name': 'List of known Microsoft Azure Datacenter IP Ranges',
        'version': get_version(),
        'description': 'Microsoft Azure Datacenter IP Ranges',
        'list': [],
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"],
        'type': 'cidr'
    }

    with open(get_abspath_source_file(file), 'r') as json_file:
        ms_azure_ip_list = json.load(json_file)

    for value in ms_azure_ip_list['values']:
        warninglist['list'] += value['properties']['addressPrefixes']

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    ms_azure_url = 'https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519'
    ms_azure_file = 'ms-azure.json'
    ms_azure_dst = 'microsoft-azure'

    ms_azure_json_url = get_json_url(download(ms_azure_url))
    download_to_file(ms_azure_json_url, ms_azure_file)
    process(ms_azure_file, ms_azure_dst)
