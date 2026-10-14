#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate the known-Microsoft-domains warninglist.

Source: the Microsoft 365 IP Address and URL Web Service --
https://endpoints.office.com/endpoints/<instance> -- queried for every
published instance (Worldwide, China, USGOVDoD, USGOVGCCHigh, Germany). It is
Microsoft's own machine-readable statement of the host names its services
use, and it is already trusted elsewhere in this project by
generate-office365.py.

**Scope, stated honestly: this covers Microsoft 365 service endpoints, not
"every domain Microsoft owns".** No authoritative machine-readable enumeration
of the latter exists, and this list contains entries that no such feed would
ever produce -- ".akadns.net" (an Akamai domain used by Microsoft),
".azuredns-prd.info", ".windowsupdate.com". So this generator does not make
the list complete; it keeps the M365-derived majority of it current and
reproducible instead of hand-edited. The remainder stays curated by hand, and
the union below is what protects it.

**This generator unions, it never replaces.** Every committed entry survives
untouched.

Three deliberate restraints:

  * URLs are added as published, with only a leading "*" wildcard removed --
    they are NOT reduced to a registrable domain. Reducing "account.live.com"
    to "live.com" would be a broader claim than Microsoft made, and where an
    endpoint sits on a third-party CDN, reducing it would suppress alerts
    across that whole provider rather than across Microsoft.
  * A candidate already covered by a committed suffix entry is not added
    again. ".azure.com" is committed, so "management.azure.com" adds nothing
    and would only make the list longer to read.
  * Third-party infrastructure the feed publishes -- certificate authorities,
    rented CDNs, customer-operated .mil domains -- is excluded, because the
    feed says "M365 talks to this", not "Microsoft owns this". See
    EXCLUDED_DOMAINS below.

Entries carry a leading dot, this list's established matching convention.
"""

import json
import logging

from generator import download, get_abspath_list_file, get_version, write_to_file

# A fixed request id, as the web service requires; the same convention as
# generate-office365.py. See
# https://learn.microsoft.com/microsoft-365/enterprise/microsoft-365-ip-web-service
CLIENT_REQUEST_ID = "b10c5ed1-bad1-445f-b386-b919946339a7"

INSTANCES = ("Worldwide", "China", "USGOVDoD", "USGOVGCCHigh", "Germany")

# The web service answers "which host names does Microsoft 365 talk to", which
# is not the same question as "which domains does Microsoft own" -- and this
# list's title asks the second one. The difference is third-party
# infrastructure that M365 depends on: the certificate authorities it fetches
# CRL and OCSP responses from, content delivery networks it rents, and the
# customer-operated government domains its sovereign clouds are reached
# through. Listing those here would assert that a CA's revocation endpoint is
# a Microsoft domain, and would suppress it as an indicator everywhere -- for
# every other vendor using that same CA too.
#
# They are therefore excluded by registrable domain, and every exclusion is
# logged so the decision stays auditable. This filter only ever *removes*
# published candidates; it can never invent one.
EXCLUDED_DOMAINS = {
    # Certificate authorities: CRL / OCSP / AIA endpoints
    "digicert.com": "certificate authority",
    "globalsign.com": "certificate authority",
    "globalsign.net": "certificate authority",
    "entrust.net": "certificate authority",
    "geotrust.com": "certificate authority",
    "identrust.com": "certificate authority",
    "letsencrypt.org": "certificate authority",
    "omniroot.com": "certificate authority (Baltimore/DigiCert root)",
    "public-trust.com": "certificate authority",
    "symcb.com": "certificate authority (Symantec)",
    "symcd.com": "certificate authority (Symantec)",
    "verisign.com": "certificate authority",
    "verisign.net": "certificate authority",
    # Third-party content delivery networks
    "akamaihd.net": "Akamai CDN, not a Microsoft domain",
    "cdnsvc.com": "third-party CDN fronting the China instance",
    # Customer-operated government domains, not Microsoft's
    "apps.mil": "US Department of Defense domain",
    "dps.mil": "US Department of Defense domain",
}

URL = "https://endpoints.office.com/endpoints/{instance}?clientrequestid=" + CLIENT_REQUEST_ID

DST = "microsoft"


def fetch_urls():
    """Collect the published host names across every M365 instance.

    A single instance failing is not fatal -- the sovereign clouds are smaller
    and less reliable than Worldwide -- but Worldwide failing is, since
    without it the run would look successful while contributing almost
    nothing.
    """
    hosts = set()
    for instance in INSTANCES:
        try:
            response = download(URL.format(instance=instance))
            response.raise_for_status()
            rows = response.json()
        except Exception as exc:
            if instance == "Worldwide":
                raise Exception(
                    "Could not read the Worldwide M365 endpoint service: {}".format(exc)
                )
            logging.warning("Skipping M365 instance %s: %s", instance, exc)
            continue

        if not isinstance(rows, list):
            logging.warning("Skipping M365 instance %s: unexpected shape", instance)
            continue

        count = 0
        for row in rows:
            for url in row.get("urls") or []:
                host = str(url).strip().lower().lstrip("*").lstrip(".")
                if not host or "." not in host or "/" in host:
                    continue
                hosts.add(host)
                count += 1
        logging.info("M365 instance %s contributed %d url entries", instance, count)
    return hosts


def registrable_domain(host):
    labels = host.strip(".").split(".")
    if len(labels) < 2:
        return host
    return ".".join(labels[-2:])


def covered_by(host, suffixes):
    """True if a committed suffix entry already matches this host."""
    for suffix in suffixes:
        if host == suffix or host.endswith("." + suffix):
            return True
    return False


def existing_warninglist():
    try:
        with open(get_abspath_list_file(DST)) as data_file:
            return json.load(data_file)
    except (IOError, OSError, ValueError):
        return None


def main():
    fetched = fetch_urls()
    if not fetched:
        raise Exception(
            "No Microsoft endpoints found upstream, refusing to write an empty list"
        )

    warninglist = existing_warninglist()
    if warninglist is None:
        raise Exception(
            "lists/{}/list.json is missing; this generator maintains an "
            "existing curated list and will not create one from scratch".format(DST)
        )

    committed = set(warninglist.get("list", []))
    suffixes = {entry.lstrip(".").lower() for entry in committed}

    additions = set()
    excluded = 0
    for host in fetched:
        if covered_by(host, suffixes):
            continue
        reason = EXCLUDED_DOMAINS.get(registrable_domain(host))
        if reason:
            logging.info(
                "microsoft: excluding %s -- %s", host, reason
            )
            excluded += 1
            continue
        additions.add("." + host)

    merged = committed.union(additions)
    logging.info(
        "microsoft: %d committed + %d published endpoints -> %d after union "
        "(%d new, %d already covered by a committed suffix, %d third-party)",
        len(committed), len(fetched), len(merged), len(additions),
        len(fetched) - len(additions) - excluded, excluded,
    )

    warninglist["list"] = sorted(merged)
    warninglist["version"] = get_version()
    write_to_file(warninglist, DST)


if __name__ == "__main__":
    main()
