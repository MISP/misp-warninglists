#!/usr/bin/env python3

from generator import download, get_version, write_to_file

if __name__ == '__main__':
    source_url = 'https://publicsuffix.org/list/public_suffix_list.dat'
    destination_folder = 'second-level-tlds'

    data = download(source_url).text
    lines = data.split("\n")
    # Filter out comments
    domains = [line.strip() for line in lines if len(line) != 0 and not line.startswith('//')]
    # Convert IDN domain to xn-- format
    domains = [domain.encode('idna').decode('utf-8') for domain in domains]
    # Filter out invalid domains
    domains = [domain.lstrip('*.') for domain in domains if not domain.startswith('!')]

    warninglist = {
        'name': 'Second level TLDs as known by Mozilla Foundation',
        'description': 'Event contains one or more second level TLDs as attribute with an IDS flag set.',
        'matching_attributes': ['hostname', 'domain', 'domain|ip'],
        'type': 'string',
        'version': get_version(),
        'list': domains,
    }

    write_to_file(warninglist, destination_folder)
