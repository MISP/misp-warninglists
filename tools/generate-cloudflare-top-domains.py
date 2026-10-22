#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from generator import (
    MULTI_TENANT_DOMAINS, download_to_file, filter_hostname_entries, get_version, write_to_file, get_abspath_source_file
)
import os

# The list is of type "hostname", so an entry also matches all its subdomains.
# Entries whose subdomains belong to third parties are dropped; public
# suffixes and their parents are dropped by filter_hostname_entries() itself.
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
        
        warninglist['list'] = filter_hostname_entries(ips, too_wide=TOO_WIDE, junk=JUNK)

        write_to_file(warninglist, base_dst + dataset_pretty_name)


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
