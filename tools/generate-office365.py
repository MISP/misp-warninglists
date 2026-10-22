#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import CERTIFICATE_AUTHORITY_DOMAINS, download, get_public_suffixes, get_version, write_to_file, consolidate_networks


def process(url):
    lurls, lips = get_lists(url)
    # A public suffix (e.g. "azurewebsites.net") would match names registered
    # by any customer of that platform, not by Microsoft. Certificate
    # authorities' CRL / OCSP endpoints are not Office 365 endpoints of their
    # own, and would be suppressed for every other vendor using the same CA.
    public_suffixes = get_public_suffixes()
    lurls = [u for u in lurls
             if u not in public_suffixes
             and '.'.join(u.split('.')[-2:]) not in CERTIFICATE_AUTHORITY_DOMAINS]

    # URLs of services
    office365_urls_dst = 'microsoft-office365'
    office365_urls_warninglist = {
        'name': 'List of known Office 365 URLs',
        'description': 'Office 365 URLs and IP address ranges',
        'type': 'hostname',
        'matching_attributes': ["domain", "domain|ip", "hostname"]
    }
    generate(lurls, office365_urls_dst, office365_urls_warninglist)

    # IPs of services
    office365_ips_dst = 'microsoft-office365-ip'
    office365_ips_warninglist = {
        'name': 'List of known Office 365 IP address ranges',
        'description': 'Office 365 IP address ranges',
        'category': 'known',
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }
    generate(consolidate_networks(lips), office365_ips_dst, office365_ips_warninglist)


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
            # The list is of type "hostname", which also matches subdomains,
            # so a wildcard is expressed by dropping every label up to and
            # including the one holding the "*": "*.foo.com" -> "foo.com",
            # "a.*.foo.com" -> "foo.com", "*-admin.foo.com" -> "foo.com".
            labels = url.split('.')
            wildcard = [i for i, label in enumerate(labels) if '*' in label]
            if wildcard:
                labels = labels[wildcard[-1] + 1:]
            lurls.append('.'.join(labels))
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
        'category': 'known',
        'type': 'cidr',
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip", "ip-src|port", "ip-dst|port"]
    }
    generate(consolidate_networks(lips), "microsoft-office365-cn", warninglist)
