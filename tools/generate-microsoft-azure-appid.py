#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from bs4 import BeautifulSoup
from generator import download, get_version, write_to_file


def process(url, dst):

    warninglist = {
        'name': 'List of Azure Applicaiton IDs',
        'version': get_version(),
        'description': 'List of Azure Application IDs (https://learn.microsoft.com/en-us/troubleshoot/azure/active-directory/verify-first-party-apps-sign-in)',
        'type': 'string',
        'list': [],
        'matching_attributes': ["azure-application-id"]
    }

    soup = BeautifulSoup(download(url).text, 'html.parser')
    for uuid in soup.find_all(text=re.compile(r'^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$')):
        try:
            if not uuid == 'f8cdef31-a31e-4b4a-93e4-5f571e91255a':
                warninglist['list'].append(uuid)
        except ValueError:
            pass

    write_to_file(warninglist, dst)

if __name__ == '__main__':
    Azure_App_ID_url = 'https://learn.microsoft.com/en-us/troubleshoot/azure/active-directory/verify-first-party-apps-sign-in'
    Azure_App_ID_dst = 'microsoft-azure-appid'

    process(Azure_App_ID_url, Azure_App_ID_dst)
