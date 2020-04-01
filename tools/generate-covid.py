#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://raw.githubusercontent.com/krassi/covid19-related/master/whitelist-domains.txt'
r = requests.get(url)
whitelist = r.text
whitelist = whitelist.split()

warninglist = {
    'name': 'Covid-19 Krassi\'s Whitelist',
    'uuid': 'b600900c-aacc-4860-acf4-7e24a1b08202',
    'description': 'Krassimir\'s Covid-19 whitelist of known good Covid-19 related websites.',
    'type': 'hostname',
    'matching_attributes': ['domain', 'hostname', 'url'],
    'version': int(datetime.date.today().strftime('%Y%m%d')),
    'list': whitelist
}

with open('../lists/covid-19-krassi-whitelist/list.json', 'w+') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)

url = 'https://raw.githubusercontent.com/Cyber-Threat-Coalition/goodlist/master/hostnames.txt'
r = requests.get(url)
whitelist = r.text
whitelist = whitelist.split()

warninglist = {
    'name': 'Covid-19 Cyber Threat Coalition\'s Whitelist',
    'uuid': '535002a9-0dec-4363-b29b-1b365cff060d',
    'description': 'The Cyber Threat Coalition\'s whitelist of COVID-19 related websites.',
    'type': 'hostname',
    'matching_attributes': ['domain', 'hostname', 'url'],
    'version': int(datetime.date.today().strftime('%Y%m%d')),
    'list': whitelist
}

with open('../lists/covid-19-cyber-threat-coalition-whitelist/list.json', 'w+') as data_file:
    json.dump(warninglist, data_file, indent=4, sort_keys=True)



