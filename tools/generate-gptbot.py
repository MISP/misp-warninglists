#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, consolidate_networks


def process(file, dst):
    l = []
    with open(get_abspath_source_file(file), 'r') as freetext_file:
        for line in freetext_file:
            cidr = line.rstrip()
            l.append(cidr)

    warninglist = {
        'name': 'List of known IP address ranges for OpenAI GPT crawler bot',
        'version': get_version(),
        'description': 'OpenAI gptbot crawler (https://openai.com/gptbot-ranges.txt)',
        'type': 'cidr',
        'list': consolidate_networks(l),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    gptbot_url = "https://openai.com/gptbot-ranges.txt"
    gptbot_file = "openai-gptbot-ranges.json"
    gptbot_dst = "openai-gptbot"

    download_to_file(gptbot_url, gptbot_file)
    process(gptbot_file, gptbot_dst)
