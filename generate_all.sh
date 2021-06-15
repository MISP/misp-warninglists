#!/bin/bash

set -e
set -x

pushd tools
python3 generate_alexa.py
python3 generate-amazon-aws.py
python3 generate-cisco.py
python3 generate-cloudflare.py
python3 generate-covid.py
python3 generate-crl-ip-domains.py
python3 generate-disposal.py
# TODO: Google page on Wikipedia does not exist anymore
# Suggestion came to use a passivetotal whois search for org:Google LLC
#python3 generate-google.py > lists/google/list.json
python3 generate_majestic-million.py
python3 generate-microsoft-azure.py
python3 generate_mozilla_certificates.py
python3 generate_moz-top500.py
python3 generate-office365.py
python3 generate_phone_numbers.py
python3 generate-publicdns.py
python3 generate-stackpath.py
python3 generate-tlds.py
python3 generate_tranco.py
python3 generate-university-domain-list.py
python3 generate-vpn.py
python3 generate-wikimedia.py
python3 generate-second-level-tlds.py
python3 generate-google-gcp.py
python3 generate-google-gmail-sending-ips.py
python3 generate-smtp.py
popd

./jq_all_the_things.sh
