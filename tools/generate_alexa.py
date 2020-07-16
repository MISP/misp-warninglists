#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
from os import path
import zipfile
from inspect import currentframe, getframeinfo

import requests


def download(url, file):
    user_agent = {
        "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    r = requests.get(url, headers=user_agent)
    with open(file, 'wb') as fd:
        for chunk in r.iter_content(4096):
            fd.write(chunk)


def get_abspath_list_file(dst):
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    real_path = path.join(
        current_folder, '../lists/{dst}/list.json'.format(dst=dst))
    return path.abspath(path.realpath(real_path))


def process(file, dst):
    with zipfile.ZipFile(file, 'r') as alexa_lists:
        for name in alexa_lists.namelist():
            if name == "top-1m.csv":
                with alexa_lists.open(name) as top:
                    top1000 = top.readlines()[:1000]
            else:
                continue

    alexa_warninglist = {}
    alexa_warninglist[
        'description'] = "Event contains one or more entries from the top 1000 of the most used website (Alexa)."
    alexa_warninglist['version'] = int(
        datetime.date.today().strftime('%Y%m%d'))
    alexa_warninglist['name'] = "Top 1000 website from Alexa"
    alexa_warninglist['type'] = 'hostname'
    alexa_warninglist['list'] = []
    alexa_warninglist['matching_attributes'] = ['hostname', 'domain', 'url', 'domain|ip']

    for site in top1000:
        v = site.decode('UTF-8').split(',')[1]
        alexa_warninglist['list'].append(v.rstrip())
    alexa_warninglist['list'] = sorted(set(alexa_warninglist['list']))

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(alexa_warninglist, data_file, indent=2, sort_keys=True)
        data_file.write("\n")


if __name__ == "__main__":
    alexa_url = "http://s3.amazonaws.com/alexa-static/top-1m.csv.zip"
    alexa_file = "top-1m.csv.zip"
    alexa_dst = "alexa"

    download(alexa_url, alexa_file)
    process(alexa_file, alexa_dst)
