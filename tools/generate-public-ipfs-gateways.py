#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from urllib.parse import urlparse

from generator import download, get_abspath_list_file, get_version, write_to_file

# Source: https://ipfs.github.io/public-gateway-checker/ is a JavaScript
# single-page app that renders its gateway list client-side from these two
# JSON data files in the same GitHub repository.
GATEWAYS_URL = "https://raw.githubusercontent.com/ipfs/public-gateway-checker/main/gateways.json"
ONION_GATEWAYS_URL = "https://raw.githubusercontent.com/ipfs/public-gateway-checker/main/onion-gateways.json"


def to_hostname(entry):
    # Entries are URL templates, historically like "https://ipfs.io/ipfs/:hash"
    # and currently bare origins like "https://ipfs.filebase.io". Parsing with
    # urlparse and taking .hostname handles scheme, port, path/placeholder,
    # and mixed case uniformly, whichever shape upstream currently uses.
    entry = entry.strip()
    if not entry:
        return None
    if "://" not in entry:
        entry = "https://" + entry
    hostname = urlparse(entry).hostname
    if not hostname:
        return None
    return hostname.rstrip('.').lower()


if __name__ == '__main__':
    gateways = json.loads(download(GATEWAYS_URL).text)
    onion_gateways = json.loads(download(ONION_GATEWAYS_URL).text)

    hostnames = set()
    for entry in gateways + onion_gateways:
        hostname = to_hostname(entry)
        if hostname:
            hostnames.add(hostname)

    # Union with the entries already committed, never replace them. Upstream
    # tracks gateways that are *currently reachable*, so it drops hosts that
    # are merely down or retired -- including long-lived ones such as ipfs.io
    # and dweb.link. For a warninglist that exists to suppress false positives,
    # a gateway that operated in the past is still worth recognising, so the
    # generator only ever adds.
    try:
        with open(get_abspath_list_file("public-ipfs-gateways")) as existing_file:
            hostnames.update(json.load(existing_file)["list"])
    except (IOError, OSError, ValueError, KeyError):
        pass

    warninglist = {
        'name': "List of known public IPFS gateways",
        'version': get_version(),
        'description': "Event contains one or more entries of known public IPFS gateways",
        'type': "string",
        'list': sorted(hostnames),
        'matching_attributes': ["domain", "hostname", "domain|ip", "url", "uri"]
    }

    write_to_file(warninglist, "public-ipfs-gateways")
