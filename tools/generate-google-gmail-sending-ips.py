#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ipaddress import ip_network, IPv4Network, IPv6Network
from dns.resolver import Resolver
from typing import List, Union
from generator import get_version, write_to_file


class Spf:
    def _parse_spf(self, spf: str) -> dict:
        output = {"include": [], "ranges": []}
        for part in spf.split(" "):
            if part.startswith("include:"):
                output["include"].append(part.split(":", 1)[1])
            elif part.startswith("ip4:") or part.startswith("ip6:"):
                output["ranges"].append(ip_network(part.split(":", 1)[1]))
        return output

    def _query_spf(self, resolver: Resolver, domain: str) -> List[Union[IPv4Network, IPv6Network]]:
        ranges = []
        for rdata in resolver.query(domain, "TXT"):
            parsed = self._parse_spf(rdata.to_text())
            ranges += parsed["ranges"]

            for include in parsed["include"]:
                ranges += self._query_spf(resolver, include)

        return ranges

    def get_list(self, domain: str) -> List[Union[IPv4Network, IPv6Network]]:
        resolver = Resolver()
        return self._query_spf(resolver, domain)


if __name__ == '__main__':
    spf = Spf()
    print()

    warninglist = {
        'name': "List of known Gmail sending IP ranges",
        'version': get_version(),
        'description': "List of known Gmail sending IP ranges (https://support.google.com/a/answer/27642?hl=en)",
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"],
        'type': 'cidr',
        'list': [str(range) for range in spf.get_list("_spf.google.com")],
    }

    write_to_file(warninglist, "google-gmail-sending-ips")
