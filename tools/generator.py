#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
from inspect import currentframe, getframeinfo
from os import path

import requests


def download_to_file(url, file):
    user_agent = {
        "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    r = requests.get(url, headers=user_agent)
    with open(file, 'wb') as fd:
        for chunk in r.iter_content(4096):
            fd.write(chunk)


def download(url):
    user_agent = {
        "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    return requests.get(url, headers=user_agent)


def get_abspath_list_file(dst):
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    real_path = path.join(
        current_folder, '../lists/{dst}/list.json'.format(dst=dst))
    return path.abspath(path.realpath(real_path))


def get_version():
    return int(datetime.date.today().strftime('%Y%m%d'))
