#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file
import ipaddress

def process(files, dst):
    warninglist = {
        'name': "List of known Stackpath CDN IP ranges",
        'version': get_version(),
        'description': "List of known Stackpath (Highwinds) CDN IP ranges (https://support.stackpath.com/hc/en-us/articles/360001091666-Whitelist-CDN-WAF-IP-Blocks)",
        'type': "cidr",
        'list': [],
        'matching_attributes': ["ip-dst", "ip-src", "domain|ip"]
    }

    for file in files:
        with open(get_abspath_source_file(file), 'r') as f:
            ips = f.readlines()
        for ip in ips:
            iptoadd = ip.strip()
            try:
                ipaddress.ip_network(ip.strip())
            except ValueError as err:# if it's host given strip to the subnet
                iptoadd = str(ipaddress.IPv6Interface(ip.strip()).ip)
            warninglist['list'].append(iptoadd)

    write_to_file(warninglist, dst)

if __name__ == '__main__':
    sp_base_url = "https://support.stackpath.com/hc/en-us/article_attachments/360083735711/"
    uri_list = ['ipblocks.txt']
    sp_dst = 'stackpath'

    to_process = list()

    for uri in uri_list:
        url = sp_base_url+uri
        file = 'stackpath_{}'.format(uri)
        download_to_file(url, file)
        to_process.append(file)

    process(to_process, sp_dst)
