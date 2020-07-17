#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

from generator import download, download_to_file, get_abspath_list_file, get_version


def process(url, warninglist, dst):
    whitelist = download(url).text
    whitelist = list(set(whitelist.split()))

    warninglist['type'] = 'hostname'
    warninglist['matching_attributes'] = ['domain', 'hostname', 'url']
    warninglist['version'] = get_version()
    warninglist['list'] = sorted(whitelist)

    with open(get_abspath_list_file(dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=2, sort_keys=True)
        data_file.write('\n')


if __name__ == '__main__':
    covid_krassi_url = 'https://raw.githubusercontent.com/krassi/covid19-related/master/whitelist-domains.txt'
    covid_krassi_dst = 'covid-19-krassi-whitelist'
    covid_krassi_warninglist = {
        'name': 'Covid-19 Krassi\'s Whitelist',
        'description': 'Krassimir\'s Covid-19 whitelist of known good Covid-19 related websites.'
    }
    covid_cyber_threat_coalition_url = 'https://raw.githubusercontent.com/Cyber-Threat-Coalition/goodlist/master/hostnames.txt'
    covid_cyber_threat_coalition_dst = 'covid-19-cyber-threat-coalition-whitelist'
    covid_cyber_threat_coalition_warninglist = {
        'name': 'Covid-19 Cyber Threat Coalition\'s Whitelist',
        'description': 'The Cyber Threat Coalition\'s whitelist of COVID-19 related websites.'
    }
    
    process(covid_krassi_url, covid_krassi_warninglist, covid_krassi_dst)
    process(covid_cyber_threat_coalition_url, covid_cyber_threat_coalition_warninglist, covid_cyber_threat_coalition_dst)
