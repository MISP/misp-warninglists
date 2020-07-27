#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download_to_file, get_version, write_to_file


def process(files, dst):

    warninglist = {
        'type': "string",
        'matching_attributes': ["hostname", "domain", "ip-dst", "ip-src", "url", "domain|ip"],
        'name': "CRL Warninglist",
        'version': get_version(),
        'description': "CRL Warninglist from threatstop (https://github.com/threatstop/crl-ocsp-whitelist/)",
        'list': []
    }

    for file in files:
        with open(file, 'r') as f:
            ips = f.readlines()
        for ip in ips:
            warninglist['list'].append(ip.strip())

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    crl_ip_base_url = 'https://raw.githubusercontent.com/threatstop/crl-ocsp-whitelist/master/'
    uri_list = ['crl-hostnames.txt', 'crl-ipv4.txt', 'crl-ipv6.txt',
                'ocsp-hostnames.txt', 'ocsp-ipv4.txt', 'ocsp-ipv6.txt']
    crl_ip_dst = 'crl-ip-hostname'

    to_process = list()

    for uri in uri_list:
        url = crl_ip_base_url + uri
        file = 'ocsp_{}'.format(uri)
        download_to_file(url, file)
        to_process.append(file)

    process(to_process, crl_ip_dst)
