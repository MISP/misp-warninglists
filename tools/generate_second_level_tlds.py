#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

def get_mozilla_list():
    return requests.get("https://publicsuffix.org/list/public_suffix_list.dat", stream=True)

def load_existing_list():
    with open('../lists/second-level-tlds/list.json', 'r') as f:
        return json.load(f)

def dump_to_list(content):
    with open('../lists/second-level-tlds/list.json', 'w') as f:
        return json.dump(content, f)


if __name__ == '__main__':
    current_file = load_existing_list()
    current_file.pop('list')
    current_file['version'] += 1
    tlds_list = []
    for l in get_mozilla_list().iter_lines():
        l = l.decode().strip()
        if not l or l.startswith('//'):
            continue
        tlds_list.append(l)
    current_file['list'] = tlds_list
    dump_to_list(current_file)
