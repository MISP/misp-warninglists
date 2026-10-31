#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import (
    MULTI_TENANT_DOMAINS, download_to_file, split_hostname_entries, get_version, write_to_file,
    write_exact_match_warninglist, get_abspath_source_file
)
import os

# The list is of type "hostname", so an entry also matches all its subdomains.
# Entries whose subdomains belong to third parties are dropped; public
# suffixes and their parents are dropped by split_hostname_entries() itself.
# The dropped entries go to the exact-match list cloudflare-top-exact.
TOO_WIDE = MULTI_TENANT_DOMAINS

# Values seen in the datasets that are not domains: the CSV header, and a
# broken line. Other malformed values are caught by the syntax check.
JUNK = {
    "domain",
    '"com,thefatherofsalmon.com.host"',
}

def process(dataset_files, base_dst):
    warninglist = {
        'version': get_version(),
        'type': "hostname",
        'matching_attributes': ["hostname", "domain", "url", "domain|ip"]
    }
    too_wide_entries = set()

    for dataset, file in dataset_files.items():
        with open(get_abspath_source_file(file), 'r') as f:
            ips = f.readlines()

        if dataset >= 1000000:
            dataset_pretty_name = "{}m".format(int(dataset / 1000000))
        elif dataset >= 1000:
            dataset_pretty_name = "{}k".format(int(dataset / 1000))
        else:
            dataset_pretty_name = str(dataset)
            
        warninglist.update({
            'name': "Top {:,} domains from Cloudflare Radar".format(dataset),
            'description': "List of top {:,} domains from Cloudflare Radar (https://developers.cloudflare.com/radar/investigate/domain-ranking-datasets/)".format(dataset),
            'list': [],
        })
        
        warninglist['list'], too_wide = split_hostname_entries(ips, too_wide=TOO_WIDE, junk=JUNK)
        too_wide_entries.update(too_wide)

        write_to_file(warninglist, base_dst + dataset_pretty_name)

    write_exact_match_warninglist(
        too_wide_entries,
        base_dst + '-exact',
        "Top domains from Cloudflare Radar too wide for hostname matching (exact match)",
        "Domains from the Cloudflare Radar top domains lists (https://developers.cloudflare.com/radar/investigate/"
        "domain-ranking-datasets/) that the cloudflare-top* lists leave out because they match hostnames: a "
        "public suffix, a domain a public suffix sits under, or a domain whose subdomains belong to customers or "
        "users. Matched exactly, so the domain itself is flagged but names registered under it are not.",
    )


if __name__ == '__main__':
    cloudflare_base_uri = "https://api.cloudflare.com/client/v4/radar/datasets/ranking_top_"
    dataset_list = [200, 1000, 2000, 5000, 10000, 20000, 50000, 100000, 200000, 500000, 1000000]
    cloudflare_base_dst = 'cloudflare-top'

    to_process = {}

    for dataset in dataset_list:
        url = cloudflare_base_uri + str(dataset)
        file = 'cloudflare_top_{}.txt'.format(dataset)
        download_to_file(url,
                         file,
                         additional_headers={
                             'Authorization': "Bearer {}".format(os.environ["CLOUDFLARE_API_TOKEN"])
                         })
        to_process[dataset] = file

    process(to_process, cloudflare_base_dst)
