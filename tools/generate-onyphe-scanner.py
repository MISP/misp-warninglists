#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module will download the IP of scanners from Onyphe
It will then generate the warning list
"""

from generator import (
    download_to_file,
    get_version,
    write_to_file,
    get_abspath_source_file,
    consolidate_networks,
)


def process(file: str, dst: str):
    """
    This function
    It will parse the downloaded IP list
    and generate the Json

    """
    l = []
    with open(get_abspath_source_file(file), "r", encoding="utf-8") as freetext_file:
        for line in freetext_file:
            if not line.startswith("#"):
                cidr = line.rstrip()
                l.append(cidr)

    warninglist = {
        "name": "List of published IP address ranges for Onyphe Scanner",
        "version": get_version(),
        "description": "Onyphe Scanner (https://www.onyphe.io/)",
        "type": "cidr",
        "list": consolidate_networks(l),
        "matching_attributes": [
            "ip-src",
            "ip-dst",
            "domain|ip",
            "ip-src|port",
            "ip-dst|port",
        ],
    }

    write_to_file(warninglist, dst)


if __name__ == "__main__":
    ONYPHE_URL = "https://www.onyphe.io/ip-ranges.txt"
    ONYPHE_FILE = "onyphe-scanner.txt"
    ONYPHE_DST = "onyphe-scanner"

    download_to_file(ONYPHE_URL, ONYPHE_FILE)  # Download in TMP
    process(ONYPHE_FILE, ONYPHE_DST)
