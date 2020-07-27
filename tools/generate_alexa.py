#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import zipfile

from generator import download_to_file, get_version, write_to_file


def process(file, dst):
    with zipfile.ZipFile(file, 'r') as alexa_lists:
        for name in alexa_lists.namelist():
            if name == "top-1m.csv":
                with alexa_lists.open(name) as top:
                    top1000 = top.readlines()[:1000]
            else:
                continue

    warninglist = {
        'description': "Event contains one or more entries from the top 1000 of the most used website (Alexa).",
        'version': get_version(),
        'name': "Top 1000 website from Alexa",
        'type': 'hostname',
        'list': [],
        'matching_attributes': ['hostname', 'domain', 'url', 'domain|ip']
    }

    for site in top1000:
        v = site.decode('UTF-8').split(',')[1]
        warninglist['list'].append(v.rstrip())

    write_to_file(warninglist, dst)


if __name__ == "__main__":
    alexa_url = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
    alexa_file = "alexa_top-1m.csv.zip"
    alexa_dst = "alexa"

    download_to_file(alexa_url, alexa_file)
    process(alexa_file, alexa_dst)
