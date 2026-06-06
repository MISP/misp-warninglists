#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import (
    download,
    get_version,
    write_to_file,
    consolidate_networks,
)
from bs4 import BeautifulSoup


def process(url, dst):
    cidr_ranges = []
    soup = BeautifulSoup(download(url).text, "html.parser")
    lines = soup.find(id="ips").get_text().splitlines()
    for line in lines:
        if line != "":
            cidr_ranges.append(line)

    warninglist = {
        "name": "List of known Driftnet / Internet-Measurement IP ranges (https://internet-measurement.com/)",
        "version": get_version(),
        "description": "Driftnet / Internet-Measurement IP address ranges (https://internet-measurement.com/)",
        "matching_attributes": [
            "ip-src",
            "ip-dst",
            "domain|ip",
            "ip-src|port",
            "ip-dst|port",
        ],
        "type": "cidr",
        "list": consolidate_networks(cidr_ranges),
    }

    write_to_file(warninglist, dst)


if __name__ == "__main__":
    DRIFTNET_URL = "https://internet-measurement.com/"
    DRIFTNET_DST = "driftnet"

    process(DRIFTNET_URL, DRIFTNET_DST)
