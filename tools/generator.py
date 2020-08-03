#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
from inspect import currentframe, getframeinfo
from os import path
import logging

import requests
from dateutil.parser import parse as parsedate


def download_to_file(url, file):
    user_agent = {"User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    try:
        r = requests.head(url, headers=user_agent)
        url_datetime = parsedate(r.headers['Last-Modified']).astimezone()
        file_datetime = datetime.datetime.fromtimestamp(
            path.getmtime(file)).astimezone()

        if(url_datetime > file_datetime):
            actual_download_to_file(url, file, user_agent)
    except (KeyError, FileNotFoundError) as ex:
        logging.warning(str(ex))
        actual_download_to_file(url, file, user_agent)
        

def actual_download_to_file(url, file, user_agent):
    r = requests.get(url, headers=user_agent)
    with open(file, 'wb') as fd:
        for chunk in r.iter_content(4096):
            fd.write(chunk)


def process_stream(url):
    r = requests.get(url, stream=True)
    
    data_list = []
    for line in r.iter_lines():
        v = line.decode('utf-8')
        if not v.startswith("#"):
            if v:
                data_list.append(v)
    
    return data_list

   
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


def unique_sorted_warninglist(warninglist):
    warninglist['list'] = sorted(set(warninglist['list']))
    return warninglist


def write_to_file(warninglist, dst):
    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(unique_sorted_warninglist(warninglist),
                  data_file, indent=2, sort_keys=True)
        data_file.write("\n")
