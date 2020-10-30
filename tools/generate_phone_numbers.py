#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import get_version, write_to_file


def generate_american_warninglist():
    # Warning list for fictitious telephone numbers in the US
    warninglist = [
        '/((?:\+|00)1?)55501([0-9]{2})/g',
        '/((?:\+|00)1?)([0-9]{3})55501([0-9]{2})/g'
    ]
    return warninglist


def generate_french_warninglist():
    regex = '/((?:\+|00)33?|0?)(%s)([0-9]{%s})/g'

    # Warning list for numbers dedicated to communications companies internal use: numbers starting with 09 99
    warninglist = [regex % ('999', '6')]

    # Warning list for numbers dedicated to audiovisual works: starting with any of the following list
    prefixes = ('19900', '26191', '35301', '46571', '53649', '63998')
    warninglist.append(regex % ('|'.join(prefixes), '4'))

    return warninglist


def process(warninglist_name):
    description = {
        'description': 'Numbers that cannot be attributed because they reserved for different purposes.',
        'name': 'Unattributed phone number.',
        'matching_attributes': [
            'phone-number',
            'whois-registrant-phone'
        ],
        'type': 'regex',
        'version': get_version()
    }

    warninglist = generate_french_warninglist()
    warninglist.extend(generate_american_warninglist())
    # The list can be extended by adding other entries: `warninglist.extend(generate_some_warninglist())`

    description['list'] = warninglist
    write_to_file(description, warninglist_name)


if __name__ == '__main__':
    warninglist_name = 'phone_numbers'
    process(warninglist_name)
