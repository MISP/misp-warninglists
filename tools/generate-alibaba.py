#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the Alibaba Cloud (Aliyun) warninglist from the RIPEstat Data API.

Tier 2 source: BGP-announced prefixes per ASN.

Alibaba Cloud publishes no machine-readable address-space feed of its own.
There is no ip-ranges.json, no documented text file and no RFC 8805 geofeed:
every candidate URL under alibabacloud.com / aliyun.com answers with the
marketing site's soft-404 HTML rather than data. So the address space is
derived from what Alibaba's own autonomous systems announce, read live from

    https://stat.ripe.net/data/announced-prefixes/data.json?resource=<asn>

The ASNs are pinned in ALIBABA_ASNS below, and every one of them is verified
against the registry at runtime before a single prefix of its is used:

  1. https://stat.ripe.net/data/as-names/data.json?resource=AS<n>
     must contain that ASN's expected holder substring, and
  2. https://stat.ripe.net/data/abuse-contact-finder/data.json?resource=<n>
     must publish an abuse address in Alibaba's own domain.

A mismatch raises rather than being skipped: an ASN that changed hands would
otherwise put somebody else's address space into a list labelled Alibaba.
The holder substrings are deliberately specific per ASN, not a generic
"Alibaba". AS34947 is "Alibaba-Travels-Company / Alibaba Travel Company (LTD)"
with abuse@alibaba.ir -- an unrelated Iranian travel firm that a loose match
would happily have swept in. It is not in the list. Neither is AS24429
(Taobao / Zhejiang Taobao Network Co.,Ltd), which is Alibaba Group retail
rather than Alibaba Cloud and publishes no abuse contact at all.

"Hangzhou Alibaba Advertising Co.,Ltd." is not a verification bug: it is the
registry holder name behind the ALIBABA-CN-NET handle, i.e. Aliyun's Chinese
network. Alibaba Cloud's space is spread over several legal entities --
Hangzhou Alibaba Advertising (CN), Alibaba (US) Technology, Alibaba Cloud LLC
(US) and Alibaba Cloud (Singapore) Private Limited -- which is why the list
below spans four expected holder strings.

Several of the pinned ASNs currently announce nothing. That is normal for an
allocated-but-idle AS; they are kept (and still holder-verified) so that space
is picked up as soon as it is announced.

Semantics caveat: this is general-purpose rented compute. The tenant behind
any given address changes constantly and an attacker can simply rent one. The
list recognises that an address belongs to the provider; it is NOT grounds for
treating traffic as benign.
"""

import ipaddress
import logging
from time import sleep

from generator import (
    consolidate_networks,
    download,
    get_version,
    write_to_file,
)

RIPESTAT = "https://stat.ripe.net/data/{call}/data.json?resource={resource}"

# ASN -> substring that must appear in the registry holder name. Specific on
# purpose; see the module docstring for what a generic "Alibaba" would let in.
ALIBABA_ASNS = {
    37963: "Hangzhou Alibaba Advertising",
    45102: "Alibaba (US) Technology",
    45103: "Hangzhou Alibaba Advertising",
    45104: "Hangzhou Alibaba Advertising",
    59028: "Hangzhou Alibaba Advertising",
    59051: "Hangzhou Alibaba Advertising",
    59052: "Hangzhou Alibaba Advertising",
    59053: "Hangzhou Alibaba Advertising",
    59054: "Hangzhou Alibaba Advertising",
    59055: "Hangzhou Alibaba Advertising",
    134963: "Alibaba Cloud (Singapore) Private Limited",
    203513: "Alibaba Cloud (Singapore) Private Limited",
    402205: "Alibaba Cloud LLC",
    402206: "Alibaba Cloud LLC",
    402207: "Alibaba Cloud LLC",
}

# The abuse contact has to corroborate the name. Alibaba routes abuse for both
# the group and the cloud through alibaba-inc.com mailboxes.
EXPECTED_ABUSE_DOMAINS = ("alibaba-inc.com", "alibabacloud.com")


def ripestat(call, resource):
    response = download(RIPESTAT.format(call=call, resource=resource))
    response.raise_for_status()
    return response.json()


def holder_name(asn):
    names = ripestat("as-names", "AS{}".format(asn))["data"]["names"]
    return names.get(str(asn), "")


def abuse_contacts(asn):
    return ripestat("abuse-contact-finder", asn)["data"]["abuse_contacts"]


def verify_holder(asn, expected):
    """Raise unless the registry still says this ASN is Alibaba's.

    Failing loudly is the point. Skipping a mismatch would silently shrink the
    list; accepting one would list address space Alibaba no longer holds.
    """
    name = holder_name(asn)
    if expected not in name:
        raise Exception(
            "AS{} holder is {!r}, expected it to contain {!r}; refusing to "
            "list address space that may no longer be Alibaba Cloud's".format(
                asn, name, expected
            )
        )

    contacts = abuse_contacts(asn)
    corroborated = False
    for email in contacts:
        for domain in EXPECTED_ABUSE_DOMAINS:
            if email.endswith(domain):
                corroborated = True
    if not corroborated:
        raise Exception(
            "AS{} ({}) publishes abuse contacts {}, none in {}; holder name "
            "alone is not enough to keep it".format(
                asn, name, contacts, list(EXPECTED_ABUSE_DOMAINS)
            )
        )

    print("AS{} verified: {} / {}".format(asn, name, ", ".join(contacts)))
    return name


def get_networks_for_asn(asn):
    prefixes = ripestat("announced-prefixes", asn)["data"]["prefixes"]
    return [entry["prefix"] for entry in prefixes]


def main():
    networks = set()

    for asn in sorted(ALIBABA_ASNS):
        verify_holder(asn, ALIBABA_ASNS[asn])
        sleep(0.5)  # be gentle with the API between requests

        prefixes = get_networks_for_asn(asn)
        if not prefixes:
            # Perfectly normal: an allocated AS need not announce anything.
            print("AS{} announces no prefixes".format(asn))
            continue

        for prefix in prefixes:
            try:
                # strict=True: a prefix with host bits set is ambiguous, and
                # the only way to accept one is to widen it to its enclosing
                # network, which would suppress alerts for addresses nobody
                # claimed.
                ipaddress.ip_network(prefix)
            except ValueError as exc:
                logging.warning("Skipping malformed prefix %s: %s", prefix, exc)
                continue
            networks.add(prefix)

        sleep(0.5)

    if not networks:
        raise Exception(
            "No Alibaba Cloud prefixes found, refusing to write an empty list"
        )

    warninglist = {
        "name": "List of known Alibaba Cloud IP address ranges",
        "version": get_version(),
        "description": (
            "Alibaba Cloud (Aliyun) IPv4 and IPv6 ranges, from the prefixes "
            "its verified autonomous systems announce, read live from the "
            "RIPEstat Data API (https://stat.ripe.net/). Alibaba Cloud "
            "publishes no address-space feed of its own. This is "
            "general-purpose rented compute: the tenant behind any given "
            "address changes constantly and an attacker can simply rent one. "
            "The list recognises that an address belongs to the provider; it "
            "is NOT grounds for treating traffic as benign."
        ),
        "type": "cidr",
        "list": consolidate_networks(networks),
        "matching_attributes": [
            "ip-src",
            "ip-dst",
            "domain|ip",
            "ip-src|port",
            "ip-dst|port",
        ],
    }
    write_to_file(warninglist, "alibaba-cloud")


if __name__ == "__main__":
    main()
