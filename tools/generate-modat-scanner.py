#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This module will download from MODAT the IP of scanners
and update the Warning list for the MODAT scanner
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
        "name": "List of published IP address ranges for Modat Scanner",
        "version": get_version(),
        "description": "Modat Scanner (https://www.modat.io/)",
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
    MODAT_URL = "https://scanner.modat.io/ipv4.txt"
    MODAT_FILE = "modat-scanner.json"
    MODAT_DST = "modat-scanner"

    download_to_file(MODAT_URL, MODAT_FILE)  # Download in TMP
    process(MODAT_FILE, MODAT_DST)
