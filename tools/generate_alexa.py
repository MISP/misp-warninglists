#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BROKEN: the sole upstream source, http://s3.amazonaws.com/alexa-static/top-1m.csv.zip,
# still answers HTTP 200 but no longer serves the real top-1m.csv dataset. As of 2026-08-29
# it returns a 193-byte zip (Last-Modified: Sat, 06 Sep 2025) whose sole entry, top-1m.csv,
# contains only the text "poc by @gopal_ethical" instead of ranked domains. This is worse
# than the generate_all.sh comment ("not updated since February 1, 2023 and offline after
# July 31, 2023") suggests: the endpoint has since been repurposed/squatted, not merely
# stopped updating. lists/alexa/list.json has therefore been frozen at version 20230511
# since 2023-05-11. Amazon retired the Alexa Rank product entirely in 2022, so there is no
# equivalent replacement feed at the same source. Options: port this generator to another
# top-sites ranking source (e.g. Tranco, https://tranco-list.eu/), or deprecate the list.
# Note: this repo already ships lists/tranco/list.json and lists/tranco10k/list.json
# (see tools/generate_tranco.py, itself currently commented out in generate_all.sh) which cover the same "well-known popular domain" use case
# from a maintained source, so those are a plausible successor rather than a fresh port.

import zipfile

from generator import (download_to_file, get_abspath_source_file, get_version,
                       write_to_file)


def process(file, dst):
    with zipfile.ZipFile(get_abspath_source_file(file), 'r') as alexa_lists:
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
