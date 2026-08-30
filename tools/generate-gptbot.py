#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, get_version, write_to_file, consolidate_networks


if __name__ == '__main__':
    bots = download("https://openai.com/gptbot.json")
    parsed = json.loads(bots.text)

    ranges = [p["ipv4Prefix"] if "ipv4Prefix" in p else p["ipv6Prefix"] for p in parsed["prefixes"]]

    warninglist = {
        'name': 'List of known IP address ranges for OpenAI GPT crawler bot',
        'version': get_version(),
        'description': 'OpenAI gptbot crawler (https://openai.com/gptbot.json)',
        'type': 'cidr',
        'list': consolidate_networks(ranges),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }

    write_to_file(warninglist, "openai-gptbot")
