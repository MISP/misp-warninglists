#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import json
import logging
from inspect import currentframe, getframeinfo, getmodulename, stack
from os import mkdir, path

import requests
from dateutil.parser import parse as parsedate


def init_logging():
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    LOG_DIR = path.join(current_folder, '../generators.log')

    logFormatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s::%(funcName)s()::%(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    # Log to file
    fileHandler = logging.FileHandler(LOG_DIR)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    # Log to console too
    ''' consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler) '''
    return rootLogger


init_logging()


def download_to_file(url, file):
    frame_records = stack()[1]
    caller = getmodulename(frame_records[1]).upper()

    user_agent = {
        "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    try:
        r = requests.head(url, headers=user_agent)
        url_datetime = parsedate(r.headers['Last-Modified']).astimezone()
        file_datetime = datetime.datetime.fromtimestamp(
            path.getmtime(get_abspath_source_file(file))).astimezone()

        if(url_datetime > file_datetime):
            logging.info('{} File on server is newer, so downloading update to {}'.format(
                caller, get_abspath_source_file(file)))
            actual_download_to_file(url, file, user_agent)
        else:
            logging.info(
                '{} File on server is older, nothing to do'.format(caller))
    except KeyError as exc:
        logging.warning('{} KeyError in the headers. the {} header was not sent by server {}. Downloading file'.format(
            caller, str(exc), url))
        actual_download_to_file(url, file, user_agent)
    except FileNotFoundError as exc:
        logging.info(
            "{} File didn't exist, so downloading {} from {}".format(caller, file, url))
        actual_download_to_file(url, file, user_agent)
    except Exception as exc:
        logging.warning(
            '{} General exception occured: {}.'.format(caller, str(exc)))
        actual_download_to_file(url, file, user_agent)


def actual_download_to_file(url, file, user_agent):
    r = requests.get(url, headers=user_agent)
    with open(get_abspath_source_file(file), 'wb') as fd:
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


def get_abspath_source_file(dst):
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    tmp_path = path.join(current_folder, '../tmp/')
    if not path.exists(tmp_path):
        mkdir(tmp_path)
    return path.abspath(path.realpath(path.join(tmp_path, '{dst}'.format(dst=dst))))


def get_version():
    return int(datetime.date.today().strftime('%Y%m%d'))


def unique_sorted_warninglist(warninglist):
    warninglist['list'] = sorted(set(warninglist['list']))
    return warninglist


def write_to_file(warninglist, dst):
    frame_records = stack()[1]
    caller = getmodulename(frame_records[1]).upper()

    try:
        with open(get_abspath_list_file(dst), 'w') as data_file:
            json.dump(unique_sorted_warninglist(warninglist),
                      data_file, indent=2, sort_keys=True)
            data_file.write("\n")
        logging.info('New warninglist written to {}.'.format(
            get_abspath_list_file(dst)))
    except Exception as exc:
        logging.error(
            '{} General exception occurred: {}.'.format(caller, str(exc)))


def main():
    init_logging()


if __name__ == '__main__':
    main()
