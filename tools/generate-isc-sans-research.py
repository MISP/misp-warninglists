#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import ipaddress
import xml.etree.ElementTree as ET
from generator import get_version, write_to_file


if __name__ == '__main__':
    # need explicit header with 
    headers = {
    "User-Agent": "MISP-WarninglistBot/1.0 (contact: misp-warninglist@github.com)"
    }  
    r = requests.get("https://isc.sans.edu/api/threatcategory/research/", headers=headers)
    r.raise_for_status()
    xml_data = r.text
    
    root = ET.fromstring(xml_data)
    values = []
    for item in root.findall("research"):
        ip = item.findtext("ipv4")
        if not ip:
            continue
        try:
            ipaddress.ip_address(ip)
            values.append(f"{ip}")
        except ValueError:
            continue

    warninglist = {
        "name": "SANS ISC Research IPs",
        "version": get_version(),
        "description": "List of IPs from SANS ISC Research feed (https://isc.sans.edu/api/threatcategory/research/)",
        "matching_attributes": ["ip-src", "ip-dst", "ip-dst|port", "ip-src|port"],
        "type": "cidr",
        "list": values,
    }

    write_to_file(warninglist, "isc-sans-research")