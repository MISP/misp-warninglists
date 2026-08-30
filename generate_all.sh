#!/bin/bash

set -e
set -x

pushd tools
# python3 generate_alexa.py  # not updated since February 1, 2023 and offline after July 31, 2023
python3 generate-amazon-aws.py
python3 generate-oracle-oci.py
python3 generate-apple-ip-ranges.py
python3 generate-cisco.py
python3 generate-cloudflare.py
python3 generate-fastly.py
#python3 generate-cloudflare-top-domains.py  # requires a CLOUDFLARE_API_TOKEN env var (Cloudflare Radar API); raises KeyError: 'CLOUDFLARE_API_TOKEN' when unset
python3 generate-covid.py
python3 generate-crl-ip-domains.py
python3 generate-disposal.py
python3 generate-google.py
python3 generate_majestic-million.py -n 10000
python3 generate-microsoft-azure.py
# See https://github.com/MISP/misp-warninglists/issues/319
python3 generate_mozilla_certificates.py
python3 generate_moz-top500.py
python3 generate-office365.py
python3 generate_phone_numbers.py
#python3 generate-stackpath.py  # source https://k3t9x2h3.map2.ssl.hwcdn.net/ipblocks.txt is dead (NXDOMAIN); StackPath wound down its CDN and hwcdn.net is now a parked domain-for-sale page
python3 generate-tlds.py
python3 generate-github.py
python3 generate-public-ipfs-gateways.py
python3 generate_tranco.py
python3 generate-university-domain-list.py
# python3 generate-windows-binary-hashes.py  # ON HOLD DUE TO https://github.com/m417z/winbindex/commit/24dd6995fd1c8eacbf59b5ce658d34ccf00bae00
python3 generate-microsoft-win11-endpoints.py
python3 generate-vpn.py
python3 generate-wikimedia.py
python3 generate-second-level-tlds.py
python3 generate-google-gcp.py
python3 generate-google-bot.py
python3 generate-google-gmail-sending-ips.py
python3 generate-smtp.py
python3 generate-tenable.py
python3 generate-microsoft-azure-appid.py
python3 generate-chrome-crux-1m.py
python3 generate-digitalside.py
python3 generate-gptbot.py
python3 generate-cisco-umbrella-blockpage.py
python3 generate-zscaler.py
python3 generate-onyphe-scanner.py
python3 generate-modat-scanner.py
python3 generate-internetcleanup-scanner.py
python3 generate-apple-domains.py
python3 generate-icloud-private-relay.py
python3 generate-driftnet.py
#python3 generate-umich-cse-connection-attempts.py # ON HOLD: source protected by Cloudflare managed JS challenge (HTTP 403, Cf-Mitigated: challenge header) as of 2026-08-29; not a User-Agent issue, requests-based fetch cannot pass itpython3 generate-icloud-private-relay.py
python3 generate-bunny-net.py
python3 generate-ovh.py
python3 generate-microsoft-mdca.py
python3 generate-palo-alto-networks-cortex-cloud.py
python3 generate-openfilters-scanners.py
python3 generate-lots-project.py
python3 generate-check-host-net.py
python3 generate-akamai.py
popd

./jq_all_the_things.sh
