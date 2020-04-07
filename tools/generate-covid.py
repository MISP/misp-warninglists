#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import datetime

url = 'https://raw.githubusercontent.com/krassi/covid19-related/master/whitelist-domains.txt'
r = requests.get(url)
whitelist = r.text
whitelist = list(set(whitelist.split()))

warninglist = {
    'name': 'Covid-19 Krassi\'s Whitelist',
    'description': 'Krassimir\'s Covid-19 whitelist of known good Covid-19 related websites.',
    'type': 'hostname',
    'matching_attributes': ['domain', 'hostname', 'url'],
    'version': int(datetime.date.today().strftime('%Y%m%d')),
    'list': sorted(whitelist)
}

with open('../lists/covid-19-krassi-whitelist/list.json', 'w+') as data_file:
    json.dump(warninglist, data_file, indent=2, sort_keys=True)

url = 'https://raw.githubusercontent.com/Cyber-Threat-Coalition/goodlist/master/hostnames.txt'
r = requests.get(url)
whitelist = r.text
whitelist = list(set(whitelist.split()))

warninglist = {
    'name': 'Covid-19 Cyber Threat Coalition\'s Whitelist',
    'description': 'The Cyber Threat Coalition\'s whitelist of COVID-19 related websites.',
    'type': 'hostname',
    'matching_attributes': ['domain', 'hostname', 'url'],
    'version': int(datetime.date.today().strftime('%Y%m%d')),
    'list': sorted(whitelist)
}

with open('../lists/covid-19-cyber-threat-coalition-whitelist/list.json', 'w+') as data_file:
    json.dump(warninglist, data_file, indent=2, sort_keys=True)



