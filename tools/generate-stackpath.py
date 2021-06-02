#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ipaddress
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

from generator import download_to_file, get_version, write_to_file, get_abspath_source_file


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def get_all_website_links(url):
    internal_urls = set()
    external_urls = set()

    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)

        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                external_urls.add(href)
            continue
        urls.add(href)
        internal_urls.add(href)

    return urls, internal_urls, external_urls


def get_file_link(base_url, filename):
    urls, internal_urls, external_urls = get_all_website_links(base_url)
    for url in internal_urls:
        if filename in url:
            return url


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
            except ValueError as err:  # if it's host given strip to the subnet
                iptoadd = str(ipaddress.IPv6Interface(ip.strip()).ip)
            warninglist['list'].append(iptoadd)

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    sp_base_url = "https://support.stackpath.com/hc/en-us/articles/360001091666-Whitelist-CDN-WAF-IP-Blocks"
    filename = 'ipblocks.txt'
    sp_dst = 'stackpath'

    to_process = list()

    url = get_file_link(sp_base_url, filename)
    file = 'stackpath_{}'.format(filename)
    download_to_file(url, file)
    to_process.append(file)

    process(to_process, sp_dst)
