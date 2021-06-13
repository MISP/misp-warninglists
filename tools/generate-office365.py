#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import download, get_version, write_to_file


def process(url):
    lurls, lips = get_lists(url)

    # URLs of services
    office365_urls_dst = 'microsoft-office365'
    office365_urls_warninglist = {
        'name': 'List of known Office 365 URLs',
        'description': 'Office 365 URLs and IP address ranges',
        'type': 'string',
        'matching_attributes': ["domain", "domain|ip", "hostname"]
    }
    generate(lurls, office365_urls_dst, office365_urls_warninglist)

    # IPs of services
    office365_ips_dst = 'microsoft-office365-ip'
    office365_ips_warninglist = {
        'name': 'List of known Office 365 IP address ranges',
        'description': 'Office 365 IP address ranges',
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }
    generate(lips, office365_ips_dst, office365_ips_warninglist)


def generate(data_list, dst, warninglist):

    warninglist['version'] = get_version()
    warninglist['list'] = data_list

    write_to_file(warninglist, dst)


def get_lists(url):
    service_list = download(url).json()

    lurls = []
    lips = []

    for service in service_list:
        for url in service.get('urls', []):
            if url.find(".*.") == -1:
                lurls.append(url.replace('*.', '').replace('*-', '').replace('*', ''))
            else:
                lurls.append(url.rsplit('.*.',1)[1])
        for ip in service.get('ips', []):
            lips.append(ip)

    return lurls, lips


if __name__ == '__main__':
    # For more info see https://docs.microsoft.com/en-us/microsoft-365/enterprise/microsoft-365-ip-web-service?view=o365-worldwide
    office365_url = 'https://endpoints.office.com/endpoints/worldwide?clientrequestid=b10c5ed1-bad1-445f-b386-b919946339a7'
    process(office365_url)

    office365_url_china = 'https://endpoints.office.com/endpoints/China?ClientRequestId=b10c5ed1-bad1-445f-b386-b919946339a7'
    _, lips = get_lists(office365_url_china)
    warninglist = {
        'name': 'List of known Office 365 IP address ranges in China',
        'description': 'Office 365 IP address ranges in China',
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }
    generate(lips, "microsoft-office365-cn", warninglist)
