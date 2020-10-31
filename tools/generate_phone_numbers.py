#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import get_version, write_to_file


def generate_american_warninglist():

    # Warning list for fictitious telephone numbers in the US
    warninglist = [
        '/((?:\+|00)1)?55501([0-9]{2})/g',
        '/((?:\+|00)1)?([0-9]{3})55501([0-9]{2})/g'
    ]

    return warninglist


def generate_australian_warninglist():
    prefix = '((?:\+|00)61)?'

    # Australian Fictitious numbers
    warninglist = [f'/{prefix}1900654321/g', f'/{prefix}1800160401/g']
    location = ('02', '03', '07', '08')
    numbers = ('5550', '7010')
    rate_numbers = ('07', '08', '09', '10', '11')
    warninglist = [
        f'/{prefix}1900654321/g',
        f'/{prefix}1800160401/g',
        f"/{prefix}1(3|8)009757{'|'.join(rate_numbers)}/g",
        '/%s(%s)(%s)([0-9]{4})/g' % (prefix, '|'.join(location), '|'.join(numbers))
    ]

    mobile_numbers = {
        '570': ('006', '156', '157', '158', '159', '110', '313', '737'),
        '571': ('266', '491', '804'),
        '572': ('549', '665', '983'),
        '573': ('770', '087'),
        '574': ('118', '632'),
        '575': ('254', '789'),
        '576': ('398', '801'),
        '577': ('426', '644'),
        '578': ('957', '148', '888'),
        '579': ('212', '760', '455')
    }
    warninglist.extend([f"/{prefix}0491{key}({'|'.join(values)})/g" for key, values in mobile_numbers.items()])

    return warninglist


def generate_french_warninglist():
    regex = '/((?:\+|00)33?|0?)(%s)([0-9]{%s})/g'

    # Warning list for numbers dedicated to communications companies internal use: numbers starting with 09 99
    warninglist = [regex % ('999', '6')]

    # Warning list for numbers dedicated to audiovisual works: starting with any of the following list
    prefixes = ('19900', '26191', '35301', '46571', '53649', '63998')
    warninglist.append(regex % ('|'.join(prefixes), '4'))

    return warninglist


def generate_irish_warninglist():
    return ['/((?:\+|00)353)?02091([0-9]{5})/g']


def generate_swedish_warninglist():
    prefix = '((?:\+|00)46)?'
    numbers = (
        '3139006',
        '4062804',
        '8465004',
        '9803192'
    )
    warninglist = ['/%s07017406(0[5-9]|[1-9][0-9])/g' % prefix]
    warninglist.extend('/%s%s([0-9]{2})/g' % (prefix, number) for number in numbers)
    return warninglist


def generate_uk_warninglist():
    prefix = '((?:\+|00)44)?'
    end = '([0-9]{3})'
    codes = ('13', '14', '15', '16', '17', '18', '21', '31', '41', '51', '61')

    warninglist = [
        f"/{prefix}01({'|'.join(codes)})4960{end}/g",
        f'/{prefix}01914980{end}/g',
        f'/{prefix}02079460{end}/g',
        f'/{prefix}02(89|92)0180{end}/g',
        f'/{prefix}01632960{end}/g',
        f'/{prefix}07700900{end}/g',
        f'/{prefix}03069990{end}/g',
        f'/{prefix}08081570{end}/g',
        f'/{prefix}09098790{end}/g'
    ]
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

    warninglist = generate_australian_warninglist()
    warninglist.extend(generate_american_warninglist())
    warninglist.extend(generate_french_warninglist())
    warninglist.extend(generate_irish_warninglist())
    warninglist.extend(generate_swedish_warninglist())
    warninglist.extend(generate_uk_warninglist())
    # The list can be extended by adding other entries: `warninglist.extend(generate_some_warninglist())`

    description['list'] = warninglist
    write_to_file(description, warninglist_name)


if __name__ == '__main__':
    warninglist_name = 'phone_numbers'
    process(warninglist_name)
