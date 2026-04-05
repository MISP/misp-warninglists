#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from generator import download, get_version, write_to_file


def process(url, dst):
    """Process winbindex data and generate warninglist."""
    response = download(url)
    data = response.json()
    
    # Extract all SHA256 hashes from the winbindex data
    # Structure: {filename: {sha256_hash: source_type, ...}, ...}
    hashes = []
    if data:
        for file_name, hash_dict in data.items():
            if isinstance(hash_dict, dict):
                # Each key in hash_dict is a SHA256 hash
                for sha256_hash in hash_dict.keys():
                    # Validate it looks like a SHA256 (64 hex characters)
                    if isinstance(sha256_hash, str) and len(sha256_hash) == 64:
                        hashes.append(sha256_hash)
    
    warninglist = {
        'name': 'List of known hashes for Windows binaries',
        'version': get_version(),
        'description': 'List of known Windows binaries based on hashes from winbindex (https://github.com/m417z/winbindex)',
        'type': 'string',
        'list': hashes,
        'matching_attributes': [
            'sha256'
        ]
    }
    
    write_to_file(warninglist, dst)


if __name__ == '__main__':
    winbindex_url = 'https://raw.githubusercontent.com/m417z/winbindex/gh-pages/data/info_sources.json'
    winbindex_dst = 'windows-binary-hashes'
    
    process(winbindex_url, winbindex_dst)
