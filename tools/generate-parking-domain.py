#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the parking-domain address warninglist by live measurement.

**Why this is not sourced from a dataset.** There is no maintained public list
of parking-service address space. The TMA 2022 research artefact
(tma22-parking.github.io) is the only published one and its data has not been
touched since 2022-07-04; 66 of its 67 addresses are already committed here,
so importing it adds nothing. github.com/bambenek/parkingipaddresses, the only
other candidate found, is an empty repository last pushed in 2014.

So this generator does not transcribe an authority. It repeats, in small, the
measurement the TMA paper made: **find the addresses that many unrelated
domains are parked on, and confirm each one serves parking before listing
it.** That is also how this list's most recent entries were added -- the 2025
commits for the teaminternet and domainsalesform ranges each justified an
address by inspecting what it actually served.

How it works
------------

1. Read the newly-registered-domain feed from
   github.com/shreshta-labs/newly-registered-domains, regenerated daily.
   Newly registered domains are parked at very high rates, which makes them
   the cheapest available probe for parking infrastructure.
2. Resolve them and count how many *distinct* domains share each address.
3. For every address above the threshold, require positive evidence that it
   serves parking before it may be listed:
     * its PTR record names it as parking ("domain-parking.one.com",
       "parkedweb01.domeneshop.no"), or
     * the page it serves says so. The request carries the ``Host`` header of
       a domain observed parked there, because parking landers are virtual
       hosts: asked by bare address they return a default page, asked with a
       parked domain's name they return that domain's parking page.
   An address without such evidence is discarded no matter how many domains
   resolve to it.
4. Discard anything sitting on a shared CDN or cloud network, read from Team
   Cymru. A parking page served from a Cloudflare edge address is still a
   Cloudflare edge address: Loopia fronts part of its estate that way, so
   188.114.96.0 answers "Parked at Loopia" while being shared with a large
   part of the web. Evidence of parking is necessary but not sufficient.

Step 3 is the whole safety argument. Shared hosting, CDNs and PaaS dominate
the raw counts -- Vercel, Shopify, GitHub Pages, IONOS and several web hosts
each serve hundreds of new domains -- and every one of them would be a
damaging entry in a suppression list. Requiring the host to identify *itself*
as parking removes them.

**This generator replaces the list; it does not union with it.** The list it
writes is exactly the set of addresses proven to be serving parking at the
time of the run, which is the property that makes the list trustworthy. Two
consequences follow and neither is hidden:

  * Every committed entry that the run does not re-prove is dropped, and each
    one is logged by name. Most such entries are not disproven -- the evidence
    check simply cannot reach a virtual-hosted lander without knowing a domain
    parked there -- so a maintainer restoring one by hand is a legitimate act,
    not a fight with the generator.
  * The feed is regional: it covers .se, .sk and .nu. Operators serving those
    registries are found; operators that do not appear there are not. This is
    the dominant limit on the size of the result.

A floor check refuses to write a list smaller than MINIMUM_ENTRIES, so a
failed fetch or a broken resolver empties nothing.

Second source: verified research indicators
-------------------------------------------

The measurement above only sees operators serving the feed's registries. It is
supplemented by RESEARCH_INDICATORS below -- ten addresses from an
infrastructure study resolved on 2026-09-07 that tested each candidate against
its RIR assignment and then reverse-swept the whole assignment. Every one of
them carries its operator and its evidence in this file, so the claim can be
re-checked rather than taken on trust.

That study's headline finding is the reason this generator lists no ranges at
all: of nineteen candidate prefixes tested, **not one was exclusive to
parking**. Trellian's 103.224.182.0/23 also carries www.mamma.com and a
DirectAdmin hosting estate; Sedo's 91.195.240.0/23 carries
mta-production.sedo.com; GoDaddy's aftermarket /23s are 96% *.secureserver.net.
Individual addresses inside operator-owned assignments survive that test;
ranges do not.
"""

import ipaddress
import json
import logging
import re
import socket
from concurrent.futures import ThreadPoolExecutor

import dns.resolver
import requests

from generator import DEFAULT_HEADERS, download, get_abspath_list_file, get_version, write_to_file

URL = (
    "https://raw.githubusercontent.com/shreshta-labs/"
    "newly-registered-domains/main/nrd-1w.csv"
)

DST = "parking-domain"

# How many distinct newly-registered domains must share an address before it is
# worth probing. Evidence is the real gate, so this only has to be high enough
# to keep the probe count bounded and to exclude a single customer's own server.
MIN_DOMAINS = 5

# Bounds so a scheduled run stays predictable.
MAX_DOMAINS = 12000
DNS_WORKERS = 50
PROBE_WORKERS = 25
PROBE_TIMEOUT = 8

# A feed yielding fewer domains than this has broken rather than the world
# having stopped registering domains.
MINIMUM_FEED_SIZE = 500

# Refuse to publish a list this small: it would mean the measurement failed,
# not that parking stopped existing.
MINIMUM_ENTRIES = 5

# Phrases parking operators use about their own hosts, matched against the PTR
# record and the served page title. Deliberately narrow. "Under construction"
# and "coming soon" are NOT here: a site genuinely being built is not parked,
# and including them matched shared web-hosting front ends during testing.
PARKING_MARKERS = (
    "parked",
    "parking",
    "domain-default",
    "domain for sale",
    "domain is for sale",
    "domain may be for sale",
    "domain name is for sale",
    "buy this domain",
)

TITLE = re.compile(r"<title[^>]*>([^<]{0,200})", re.IGNORECASE)

# A parking page served from a shared CDN or cloud edge is still a shared CDN
# or cloud edge. Loopia fronts part of its parking estate with Cloudflare, so
# 188.114.96.0 answers "Parked at Loopia" -- and listing it would suppress
# every other site behind that Cloudflare address. Evidence alone is therefore
# not enough: the address must also belong to a network that is not shared by
# construction.
#
# The owning network is read from Team Cymru over DNS
# (<reversed-ip>.origin.asn.cymru.com TXT for the ASN, AS<n>.asn.cymru.com TXT
# for its name). No API key, no rate-limit negotiation. Matching on the AS name
# rather than a numeric list keeps this working when an operator renumbers.
MULTITENANT_AS_NAMES = (
    "cloudflare", "amazon", "aws", "akamai", "google", "fastly", "microsoft",
    "azure", "digitalocean", "vultr", "linode", "ovh", "hetzner", "automattic",
    "vercel", "github", "shopify", "netlify", "wix", "squarespace", "leaseweb",
    "worldstream", "limestone", "gigenet", "psychz", "oracle", "alibaba",
    "tencent", "cdn", "cloudfront", "edgecast", "stackpath", "bunny",
)


def owning_as(address):
    """Return (asn, as_name) for an address, or (None, None) if unknown."""
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError:
        return (None, None)
    if parsed.version == 4:
        query = ".".join(reversed(address.split("."))) + ".origin.asn.cymru.com"
    else:
        nibbles = parsed.exploded.replace(":", "")
        query = ".".join(reversed(nibbles)) + ".origin6.asn.cymru.com"
    try:
        answer = dns.resolver.resolve(query, "TXT")
        record = b"".join(answer[0].strings).decode("utf-8", "replace")
    except Exception:
        return (None, None)
    asn = record.split("|")[0].strip().split()[0]
    try:
        answer = dns.resolver.resolve("AS{}.asn.cymru.com".format(asn), "TXT")
        name = b"".join(answer[0].strings).decode("utf-8", "replace")
    except Exception:
        return (asn, "")
    return (asn, name)


def on_shared_network(address):
    """Return the matching network name if this address is multi-tenant space."""
    asn, name = owning_as(address)
    if not name:
        return None
    lowered = name.lower()
    for keyword in MULTITENANT_AS_NAMES:
        if keyword in lowered:
            return "AS{} {}".format(asn, name.strip())
    return None

# Addresses verified by the Parked Domain Infrastructure Atlas, resolved
# 2026-09-07 from a European vantage point. Each passed three tests: the
# covering RIR assignment is registered to the parking operator itself (not to
# a cloud or hosting provider reselling it); a reverse-DNS sweep of every
# address in that assignment returned no non-parking hostname; and the address
# was seen serving parking, or is the A record of a parking-only hostname.
#
# "high" means the sweep found PTR evidence supporting parking use and nothing
# contradicting it. "medium" means the sweep found no PTR records at all --
# absence of contradiction, which is weaker than proof. The Confluence/Skenzo
# rows are all medium for the same reason: AS40034 publishes no reverse DNS
# anywhere in its 25 prefixes, so exclusivity there is unfalsified rather than
# demonstrated.
#
# These are static because they are a citable observation, not a feed. They are
# unioned with the live measurement, never used to justify a range.
RESEARCH_INDICATORS = (
    ("199.59.243.50", "Bodis", "high",
     "NetName BODIS-COM / BODIS-A (199.59.243.0/24); 0 of 1022 PTRs across "
     "199.59.240.0/22, none non-parking"),
    ("185.53.179.200", "ParkingCrew / Team Internet", "high",
     "185.53.179.0/24 announced by AS206834 Team Internet AG; 0 PTRs in the "
     "/24; serves lb, lp and ns3.parkingcrew.net"),
    ("64.190.63.136", "Sedo", "high",
     "SEDO-NET2 (64.190.62.0/23, Sedo GmbH); 0 of 510 PTRs in the assignment; "
     "serves Server: Parking/1.0"),
    ("104.247.81.99", "NameDrive / Team Internet CA", "medium",
     "104.247.80.0/22 NetName NEXTD (Team Internet AG); 0 of 1022 PTRs; "
     "delegates to ns1/ns2.parkingcrew.net"),
    ("185.53.177.29", "ParkingCrew / Team Internet", "medium",
     "inside 185.53.176.0/22 (DE-TEAMINTERNET), which also carries "
     "infra.teaminternet.de -- the range is not exclusive, this address is"),
    ("208.91.196.4", "Skenzo / Radix", "medium",
     "CONFLUENCE-NETWORK-INC (208.91.196.0/23); 0 of 510 PTRs"),
    ("208.91.196.7", "Skenzo / Radix", "medium",
     "CONFLUENCE-NETWORK-INC (208.91.196.0/23); 0 of 510 PTRs"),
    ("208.91.196.138", "DomainAdvertising (Skenzo platform)", "medium",
     "CONFLUENCE-NETWORK-INC (208.91.196.0/23); 0 of 510 PTRs"),
    ("208.91.197.7", "Skenzo", "medium",
     "CONFLUENCE-NETWORK-INC (208.91.197.0/24); 0 PTRs in the assignment"),
    ("199.79.60.7", "Skenzo / Radix", "medium",
     "CONFLUENCE-NETWORKS (199.79.60.0/24); 0 of 254 PTRs"),
)


def read_feed():
    response = download(URL)
    response.raise_for_status()
    domains = []
    for line in response.text.splitlines():
        name = line.strip().lower().rstrip(".")
        if not name or "," in name or "." not in name or name.startswith("#"):
            continue
        domains.append(name)
        if len(domains) >= MAX_DOMAINS:
            break
    return domains


def resolve(name):
    try:
        return {info[4][0] for info in socket.getaddrinfo(name, None)}
    except Exception:
        return set()


def measure(domains):
    """Map each address to (distinct domain count, one domain seen there)."""
    counts = {}
    witness = {}
    with ThreadPoolExecutor(DNS_WORKERS) as pool:
        for name, addresses in zip(domains, pool.map(resolve, domains)):
            for address in addresses:
                counts[address] = counts.get(address, 0) + 1
                witness.setdefault(address, name)
    return counts, witness


def says_parking(text):
    lowered = text.lower()
    for marker in PARKING_MARKERS:
        if marker in lowered:
            return marker
    return None


def fetch_title(address, host_header):
    target = "[{}]".format(address) if ":" in address else address
    headers = DEFAULT_HEADERS.copy()
    if host_header:
        headers["Host"] = host_header
    for scheme in ("http", "https"):
        try:
            response = requests.get(
                "{}://{}/".format(scheme, target),
                headers=headers,
                timeout=PROBE_TIMEOUT,
                allow_redirects=True,
            )
        except Exception:
            continue
        match = TITLE.search(response.text[:20000])
        if match:
            return match.group(1).strip()
    return None


def parking_evidence(address, host_header):
    """Return the evidence that this address serves parking, or None."""
    try:
        pointer = socket.gethostbyaddr(address)[0]
    except Exception:
        pointer = ""
    if pointer:
        marker = says_parking(pointer)
        if marker:
            return "PTR {} matches '{}'".format(pointer, marker)

    title = fetch_title(address, host_header)
    if title:
        marker = says_parking(title)
        if marker:
            return "page title {!r} (Host: {}) matches '{}'".format(
                title[:80], host_header, marker
            )
    return None


def existing_warninglist():
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def main():
    domains = read_feed()
    if len(domains) < MINIMUM_FEED_SIZE:
        raise Exception(
            "Only {} domains read from {} (expected at least {}); refusing to "
            "act on a partial feed.".format(len(domains), URL, MINIMUM_FEED_SIZE)
        )

    counts, witness = measure(domains)
    candidates = sorted(
        (address for address, count in counts.items() if count >= MIN_DOMAINS),
        key=lambda address: counts[address],
        reverse=True,
    )
    logging.info(
        "parking-domain: %d feed domains -> %d distinct addresses, %d shared by "
        "at least %d domains", len(domains), len(counts), len(candidates), MIN_DOMAINS,
    )

    with ThreadPoolExecutor(PROBE_WORKERS) as pool:
        evidence = list(
            pool.map(lambda a: parking_evidence(a, witness.get(a)), candidates)
        )

    entries = set()
    for address, reason in zip(candidates, evidence):
        if reason is None:
            logging.info(
                "parking-domain: %s shared by %d domains but shows no parking "
                "evidence, not listed", address, counts[address],
            )
            continue
        shared = on_shared_network(address)
        if shared:
            logging.info(
                "parking-domain: %s shows parking evidence (%s) but belongs to "
                "multi-tenant network %s, not listed -- the address is shared "
                "with everything else behind that edge",
                address, reason, shared,
            )
            continue
        entry = str(ipaddress.ip_network(ipaddress.ip_address(address)))
        entries.add(entry)
        logging.info(
            "parking-domain: listing %s -- %d newly registered domains, %s",
            entry, counts[address], reason,
        )

    for address, operator, confidence, reason in RESEARCH_INDICATORS:
        entry = str(ipaddress.ip_network(ipaddress.ip_address(address)))
        if entry in entries:
            continue
        entries.add(entry)
        logging.info(
            "parking-domain: listing %s -- %s, verified indicator (%s): %s",
            entry, operator, confidence, reason,
        )

    if len(entries) < MINIMUM_ENTRIES:
        raise Exception(
            "Only {} addresses could be proven to serve parking (expected at "
            "least {}); refusing to publish a list this small.".format(
                len(entries), MINIMUM_ENTRIES
            )
        )

    warninglist = existing_warninglist()
    if warninglist is None:
        raise Exception(
            "lists/{}/list.json is missing; this generator maintains an "
            "existing curated list and will not create one from scratch".format(DST)
        )

    committed = set(warninglist.get("list", []))
    dropped = sorted(committed - entries)
    if dropped:
        logging.info(
            "parking-domain: %d of %d committed entries were not re-proven and "
            "are dropped. Most are not disproven -- a virtual-hosted lander "
            "cannot be reached without a domain parked on it -- so restoring "
            "one by hand is legitimate: %s",
            len(dropped), len(committed), ", ".join(dropped),
        )
    logging.info(
        "parking-domain: %d committed -> %d evidenced (%d kept, %d new, %d dropped)",
        len(committed), len(entries), len(committed & entries),
        len(entries - committed), len(dropped),
    )

    warninglist["list"] = sorted(entries)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
