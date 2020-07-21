#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

from generator import process_stream, get_version, write_to_file


def process(url, dst):

    warninglist = {
        'name': 'List of disposable email domains',
        'version': get_version(),
        'description': 'List of disposable email domains',
        'list': process_stream(url),
        'type': 'substring',
        'matching_attributes': ["email-src", "email-dst", "whois-registrant-email", "domain|ip", "dns-soa-email"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    disposal_url = 'https://raw.githubusercontent.com/martenson/disposable-email-domains/master/disposable_email_blocklist.conf'
    disposal_dst = 'disposable-email'

    process(disposal_url, disposal_dst)
