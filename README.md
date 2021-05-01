# misp-warninglist

misp-warninglists are lists of well-known indicators that can be associated to potential false positives, errors or mistakes.

![Python application](https://github.com/MISP/misp-warninglists/workflows/Python%20application/badge.svg)

The warning lists are integrated in MISP to display an info/warning box at the event and attribute level if such indicators
are available in one of the list. The list can be globally enabled or disabled in MISP following the practices of the organization.

# lists

- [akamai/list.json](./akamai/list.json) - List of known Akamai IP ranges - _Akamai IP ranges from BGP search_
- [alexa/list.json](./alexa/list.json) - Top 1000 website from Alexa - _Event contains one or more entries from the top 1000 of the most used website (Alexa)._
- [amazon-aws/list.json](./amazon-aws/list.json) - List of known Amazon AWS IP address ranges - _Amazon AWS IP address ranges (https://ip-ranges.amazonaws.com/ip-ranges.json)_
- [automated-malware-analysis/list.json](./automated-malware-analysis/list.json) - List of known domains used by automated malware analysis services & security vendors - _Domains used by automated malware analysis services & security vendors_
- [bank-website/list.json](./bank-website/list.json) - List of known bank domains - _Event contains one or more entries of known banking website_
- [cisco_top1000/list.json](./cisco_top1000/list.json) - Top 1000 websites from Cisco Umbrella - _Event contains one or more entries from the top 1000 of the most used websites (Cisco Umbrella)._
- [cisco_top10k/list.json](./cisco_top10k/list.json) - Top 10 000 websites from Cisco Umbrella - _Event contains one or more entries from the top 10 000 of the most used websites (Cisco Umbrella)._
- [cisco_top20k/list.json](./cisco_top20k/list.json) - Top 20 000 websites from Cisco Umbrella - _Event contains one or more entries from the top 20 000 of the most used websites (Cisco Umbrella)._
- [cisco_top5k/list.json](./cisco_top5k/list.json) - Top 5000 websites from Cisco Umbrella - _Event contains one or more entries from the top 5000 of the most used websites (Cisco Umbrella)._
- [cloudflare/list.json](./cloudflare/list.json) - List of known Cloudflare IP ranges - _List of known Cloudflare IP ranges (https://www.cloudflare.com/ips/)_
- [common-contact-emails/list.json](./common-contact-emails/list.json) - Common contact e-mail addresses - _A list of commonly used abuse and contact e-mail addresses, including the ones denoted in RFC2142._
- [common-ioc-false-positive/list.json](./common-ioc-false-positive/list.json) - List of known hashes with common false-positives (based on Florian Roth input list) - _Event contains one or more entries with common false-positives_
- [covid-19-cyber-threat-coalition-whitelist/list.json](./covid-19-cyber-threat-coalition-whitelist/list.json) - Covid-19 Cyber Threat Coalition's Whitelist - _The Cyber Threat Coalition's whitelist of COVID-19 related websites._
- [covid-19-krassi-whitelist/list.json](./covid-19-krassi-whitelist/list.json) - Covid-19 Krassi's Whitelist - _Krassimir's Covid-19 whitelist of known good Covid-19 related websites._
- [covid/list.json](./covid/list.json) - Valid covid-19 related domains - _Maintained using different lists (such as Jaime Blasco's and Krassimir's lists)._
- [crl-ip-hostname/list.json](./crl-ip-hostname/list.json) - CRL Warninglist - _CRL Warninglist from threatstop (https://github.com/threatstop/crl-ocsp-whitelist/)_
- [dax30/list.json](./dax30/list.json) - List of known dax30 webpages - _Event contains one or more entries of known dax30 webpages_
- [disposable-email/list.json](./disposable-email/list.json) - List of disposable email domains - _List of disposable email domains_
- [eicar.com/list.json](./eicar.com/list.json) - List of hashes for EICAR test virus - _Event contains one or more entries based on hashes for EICAR test virus_
- [empty-hashes/list.json](./empty-hashes/list.json) - List of known hashes for empty files - _Event contains one or more entries of empty files based on known hashed_
- [fastly/list.json](./fastly/list.json) - List of known Fastly IP address ranges - _Fastly IP address ranges (https://api.fastly.com/public-ip-list)_
- [google-gcp/list.json](./google-gcp/list.json) - List of known GCP (Google Cloud Platform) IP address ranges - _GCP (Google Cloud Platform) IP address ranges (https://www.gstatic.com/ipranges/cloud.json)_
- [google-gmail-sending-ips/list.json](./google-gmail-sending-ips/list.json) - List of known gmail sending IP ranges - _List of known gmail sending IP ranges (https://support.google.com/a/answer/27642?hl=en )_
- [google/list.json](./google/list.json) - List of known google domains - _Event contains one or more entries of known google domains_
- [googlebot/list.json](./googlebot/list.json) - List of known Googlebot IP ranges - _List of known Googlebot IP ranges (https://www.lifewire.com/what-is-the-ip-address-of-google-818153 )_
- [ipv6-linklocal/list.json](./ipv6-linklocal/list.json) - List of IPv6 link local blocks - _Event contains one or more entries part of the IPv6 link local prefix (RFC 4291)_
- [majestic_million/list.json](./majestic_million/list.json) - Top 10K websites from Majestic Million - _Event contains one or more entries from the top 10K of the most used websites (Majestic Million)._
- [microsoft-attack-simulator/list.json](./microsoft-attack-simulator/list.json) - List of known Office 365 Attack Simulator used for phishing awareness campaigns - _Office 365 URLs and IP address ranges used for their attack simulator in Office 365 Threat Intelligence_
- [microsoft-azure/list.json](./microsoft-azure/list.json) - List of known Microsoft Azure Datacenter IP Ranges - _Microsoft Azure Datacenter IP Ranges_
- [microsoft-office365-cn/list.json](./microsoft-office365-cn/list.json) - List of known Office 365 IP address ranges in China - _Office 365 IP address ranges in China_
- [microsoft-office365-ip/list.json](./microsoft-office365-ip/list.json) - List of known Office 365 IP address ranges - _Office 365 IP address ranges_
- [microsoft-office365/list.json](./microsoft-office365/list.json) - List of known Office 365 URLs - _Office 365 URLs and IP address ranges_
- [microsoft-win10-connection-endpoints/list.json](./microsoft-win10-connection-endpoints/list.json) - List of known Windows 10 connection endpoints - _Event contains one or more entries of known Windows 10 connection endpoints (https://docs.microsoft.com/en-us/windows/privacy/manage-windows-endpoints)_
- [microsoft/list.json](./microsoft/list.json) - List of known microsoft domains - _Event contains one or more entries of known microsoft domains_
- [moz-top500/list.json](./moz-top500/list.json) - Top 500 domains and pages from https://moz.com/top500 - _Event contains one or more entries from the top 500 of the most used domains (Mozilla)._
- [mozilla-CA/list.json](./mozilla-CA/list.json) - Fingerprint of trusted CA certificates - _Fingerprint of trusted CA certificates taken from Mozilla's lists at https://wiki.mozilla.org/CA_
- [mozilla-IntermediateCA/list.json](./mozilla-IntermediateCA/list.json) - Fingerprint of known intermedicate of trusted certificates - _Fingerprint of known intermedicate of trusted certificates taken from Mozilla's lists at https://wiki.mozilla.org/CA_
- [multicast/list.json](./multicast/list.json) - List of RFC 5771 multicast CIDR blocks - _Event contains one or more entries part of the RFC 5771 multicast CIDR blocks_
- [nioc-filehash/list.json](./nioc-filehash/list.json) - List of known hashes for benign files - _Event contains one or more benign files based on known hashes, see https://github.com/RichieB2B/nioc_
- [ovh-cluster/list.json](./ovh-cluster/list.json) - List of known Ovh Cluster IP - _OVH Cluster IP address (https://docs.ovh.com/fr/hosting/liste-des-adresses-ip-des-clusters-et-hebergements-web/)_
- [phone_numbers/list.json](./phone_numbers/list.json) - Unattributed phone number. - _Numbers that cannot be attributed because they reserved for different purposes._
- [public-dns-hostname/list.json](./public-dns-hostname/list.json) - List of known public DNS resolvers expressed as hostname - _Event contains one or more public DNS resolvers (expressed as hostname) as attribute with an IDS flag set_
- [public-dns-v4/list.json](./public-dns-v4/list.json) - List of known IPv4 public DNS resolvers - _Event contains one or more public IPv4 DNS resolvers as attribute with an IDS flag set_
- [public-dns-v6/list.json](./public-dns-v6/list.json) - List of known IPv6 public DNS resolvers - _Event contains one or more public IPv6 DNS resolvers as attribute with an IDS flag set_
- [rfc1918/list.json](./rfc1918/list.json) - List of RFC 1918 CIDR blocks - _Event contains one or more entries part of the RFC 1918 CIDR blocks_
- [rfc3849/list.json](./rfc3849/list.json) - List of RFC 3849 CIDR blocks - _Event contains one or more entries part of the IPv6 documentation prefix (RFC 3849)_
- [rfc5735/list.json](./rfc5735/list.json) - List of RFC 5735 CIDR blocks - _Event contains one or more entries part of the RFC 5735 CIDR blocks - Special Use IPv4 Addresses_
- [rfc6598/list.json](./rfc6598/list.json) - List of RFC 6598 CIDR blocks - _Event contains one or more entries part of the RFC 6598 CIDR blocks - Special Use IPv4 Addresses_
- [rfc6761/list.json](./rfc6761/list.json) - List of RFC 6761 Special-Use Domain Names - _Event contains one or more entries part of the RFC 6761 Special-Use Domain Names_
- [second-level-tlds/list.json](./second-level-tlds/list.json) - Second level TLDs as known by Mozilla Foundation - _Event contains one or more second level TLDs as attribute with an IDS flag set_
- [security-provider-blogpost/list.json](./security-provider-blogpost/list.json) - List of known security providers/vendors blog domain - _Event contains one or more entries of known security providers/vendors blog domain with an IDS flag set_
- [sinkholes/list.json](./sinkholes/list.json) - List of known sinkholes - _List of known sinkholes_
- [stackpath/list.json](./stackpath/list.json) - List of known Stackpath CDN IP ranges - _List of known Stackpath (Highwinds) CDN IP ranges (https://support.stackpath.com/hc/en-us/articles/360001091666-Whitelist-CDN-WAF-IP-Blocks)_
- [ti-falsepositives/list.json](./ti-falsepositives/list.json) - Hashes that are often included in IOC lists but are false positives. - _Hashes that are often included in IOC lists but are false positives._
- [tlds/list.json](./tlds/list.json) - TLDs as known by IANA - _Event contains one or more TLDs as attribute with an IDS flag set_
- [tranco/list.json](./tranco/list.json) - Top 1,000,000 most-used sites from Tranco - _Event contains one or more entries from the top 1,000,000 most-used sites (https://tranco-list.eu/)._
- [tranco10k/list.json](./tranco10k/list.json) - Top 10K most-used sites from Tranco - _Event contains one or more entries from the top 10K most-used sites (https://tranco-list.eu/)._
- [university_domains/list.json](./university_domains/list.json) - University domains - _List of University domains from https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json_
- [url-shortener/list.json](./url-shortener/list.json) - List of known URL Shorteners domains - _Event contains one or more entries of known Shorteners domains_
- [vpn-ipv4/list.json](./vpn-ipv4/list.json) - Specialized list of IPv4 addresses belonging to common VPN providers and datacenters - _Specialized list of IPv4 addresses belonging to common VPN providers and datacenters_
- [vpn-ipv6/list.json](./vpn-ipv6/list.json) - Specialized list of IPv6 addresses belonging to common VPN providers and datacenters - _Specialized list of IPv6 addresses belonging to common VPN providers and datacenters_
- [whats-my-ip/list.json](./whats-my-ip/list.json) - List of known domains to know external IP - _Event contains one or more entries of known 'what's my ip' domains_
- [wikimedia/list.json](./wikimedia/list.json) - List of known Wikimedia address ranges - _Wikimedia address ranges (http://noc.wikimedia.org/conf/reverse-proxy.php.txt)_

# Format of a warning list

~~~~json
{
  "name": "List of known public DNS resolvers",
  "version": 1,
  "description": "Event contains one or more public DNS resolvers as attribute with an IDS flag set",
  "matching_attributes": [
    "ip-src",
    "ip-dst"
  ],
  "list": [
    "8.8.8.8",
    "8.8.4.4",
    "208.67.222.222",
    "208.67.220.220",
    "195.46.39.39",
    "195.46.39.40"
  ]
}
~~~~

If matching_attributes are not set, the list is matched against any type of attributes.

## type of warning list

- ```string``` (default) - perfect match of a string in the warning list against matching attributes
- ```substring``` - substring matching of a string in the warning list against matching attributes
- ```hostname``` - hostname matching (e.g. domain matching from URL) of a string in the warning list against matching attributes
- ```cidr``` - IP or CDIR block matching in the warning list against matching attributes
- ```regex``` - regex matching of a string matching attributes

# Processing warning lists in python

See [PyMISPWarningLists](https://github.com/MISP/PyMISPWarningLists) for a
python interface to warning lists.

# License

MISP warning-lists are licensed under [CC0 1.0 Universal (CC0 1.0)](https://creativecommons.org/publicdomain/zero/1.0/) -  Public Domain Dedication. If a specific author of a taxonomy wants to license it under a different license, a pull request can be requested.
