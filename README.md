# misp-warninglist

misp-warninglists are lists of well-known indicators that can be associated to potential false positives, errors or mistakes.

![Python application](https://github.com/MISP/misp-warninglists/workflows/Python%20application/badge.svg)

The warning lists are integrated in MISP to display an info/warning box at the event and attribute level if such indicators
are available in one of the list. The lists are also used to filter potential false-positive at API level. The list can be globally enabled or disabled in MISP following the practices of the organization. The warning lists
are reused in many other open source projects.

# lists

- [akamai/list.json](./lists/akamai/list.json) - **List of known Akamai IP ranges** - _Akamai IP ranges from BGP search_
- [alexa/list.json](./lists/alexa/list.json) - **Top 1000 website from Alexa** - _Event contains one or more entries from the top 1000 of the most used website (Alexa)._
- [alphastrike-research-nt-scanning/list.json](./lists/alphastrike-research-nt-scanning/list.json) - **Alphastrike research IP Ranges Used for Scanning** - _List containing IP's associated with the Alphastrike research scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [alphastrike-scanning/list.json](./lists/alphastrike-scanning/list.json) - **Alpha Strike Labs IP Ranges Used for Scanning** - _List containing IP ranges associated with Alpha Strike Labs scanning infrastructure. Alpha Strike Labs GmbH (AS208843) operates legitimate security research and internet-wide scanning services [https://ipinfo.io/AS208843]_
- [amazon-aws/list.json](./lists/amazon-aws/list.json) - **List of known Amazon AWS IP address ranges** - _Amazon AWS IP address ranges (https://ip-ranges.amazonaws.com/ip-ranges.json)_
- [apple/list.json](./lists/apple/list.json) - **List of known Apple IP ranges** - _IP ranges assigned to Apple_
- [automated-malware-analysis/list.json](./lists/automated-malware-analysis/list.json) - **List of known domains used by automated malware analysis services & security vendors** - _Domains used by automated malware analysis services & security vendors_
- [bank-website/list.json](./lists/bank-website/list.json) - **List of known bank domains** - _Event contains one or more entries of known banking website_
- [bufferover-nt-scanning/list.json](./lists/bufferover-nt-scanning/list.json) - **Bufferover IP Ranges Used for Scanning** - _List containing IP's associated with the Bufferover scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [captive-portals/list.json](./lists/captive-portals/list.json) - **Captive Portal Detection Hostnames** - _Hostnames used by different desktop and mobile device operating systems for captive portal detection as documented by the Wireless Broadband Alliance._
- [censys-scanning/list.json](./lists/censys-scanning/list.json) - **Censys IP Ranges Used for Scanning** - _List containing IP's associated with Censys scanning [https://support.censys.io/hc/en-us/articles/360043177092-Opt-Out-of-Data-Collection#Can_I_opt_out_of_Censys_data_collection?]_
- [check-host-net/list.json](./lists/check-host-net/list.json) - **List of known check-host.net IP address ranges** - _check-host IP addresses (https://check-host.net/nodes/ips)_
- [cisco_top1000/list.json](./lists/cisco_top1000/list.json) - **Top 1000 websites from Cisco Umbrella** - _Event contains one or more entries from the top 1000 of the most used websites (Cisco Umbrella)._
- [cisco_top10k/list.json](./lists/cisco_top10k/list.json) - **Top 10 000 websites from Cisco Umbrella** - _Event contains one or more entries from the top 10 000 of the most used websites (Cisco Umbrella)._
- [cisco_top20k/list.json](./lists/cisco_top20k/list.json) - **Top 20 000 websites from Cisco Umbrella** - _Event contains one or more entries from the top 20 000 of the most used websites (Cisco Umbrella)._
- [cisco_top5k/list.json](./lists/cisco_top5k/list.json) - **Top 5000 websites from Cisco Umbrella** - _Event contains one or more entries from the top 5000 of the most used websites (Cisco Umbrella)._
- [cloudflare/list.json](./lists/cloudflare/list.json) - **List of known Cloudflare IP ranges** - _List of known Cloudflare IP ranges (https://www.cloudflare.com/ips/)_
- [coalition-signals-intelligence-nt-scanning/list.json](./lists/coalition-signals-intelligence-nt-scanning/list.json) - **Coalition signals intelligence IP Ranges Used for Scanning** - _List containing IP's associated with the Coalition signals intelligence scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [common-contact-emails/list.json](./lists/common-contact-emails/list.json) - **Common contact e-mail addresses** - _A list of commonly used abuse and contact e-mail addresses, including the ones denoted in RFC2142._
- [common-ioc-false-positive/list.json](./lists/common-ioc-false-positive/list.json) - **List of known hashes with common false-positives (based on Florian Roth input list)** - _Event contains one or more entries with common false-positives_
- [covid-19-cyber-threat-coalition-whitelist/list.json](./lists/covid-19-cyber-threat-coalition-whitelist/list.json) - **Covid-19 Cyber Threat Coalition's Whitelist** - _The Cyber Threat Coalition's whitelist of COVID-19 related websites._
- [covid-19-krassi-whitelist/list.json](./lists/covid-19-krassi-whitelist/list.json) - **Covid-19 Krassi's Whitelist** - _Krassimir's Covid-19 whitelist of known good Covid-19 related websites._
- [covid/list.json](./lists/covid/list.json) - **Valid covid-19 related domains** - _Maintained using different lists (such as Jaime Blasco's and Krassimir's lists)._
- [crl-hostname/list.json](./lists/crl-hostname/list.json) - **CRL and OCSP domains** - _Domains that belongs to CRL or OCSP_
- [crl-ip/list.json](./lists/crl-ip/list.json) - **CRL and OCSP IP addresses** - _IP addresses that belongs to CRL or OCSP_
- [cybergreen-nt-scanning/list.json](./lists/cybergreen-nt-scanning/list.json) - **Cybergreen IP Ranges Used for Scanning** - _List containing IP's associated with the Cybergreen scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [cyberresilience-nt-scanning/list.json](./lists/cyberresilience-nt-scanning/list.json) - **Cyberresilience IP Ranges Used for Scanning** - _List containing IP's associated with the Cyberresilience scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [cypex-nt-scanning/list.json](./lists/cypex-nt-scanning/list.json) - **Cypex IP Ranges Used for Scanning** - _List containing IP's associated with the Cypex scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [dax30/list.json](./lists/dax30/list.json) - **List of known dax30 webpages** - _Event contains one or more entries of known dax30 webpages_
- [digitalside/list.json](./lists/digitalside/list.json) - **OSINT.DigitalSide.IT Warning List** - _OSINT DigitalSide Threat-Intel Repository - MISP Warninglist - List of domains should be marked as false positive in the related MISP event with IDS attribute not flagged_
- [disposable-email/list.json](./lists/disposable-email/list.json) - **List of disposable email domains** - _List of disposable email domains_
- [dynamic-dns/list.json](./lists/dynamic-dns/list.json) - **List of known dynamic DNS domains** - _Event contains one or more entries of known dynamic DNS domains._
- [eicar.com/list.json](./lists/eicar.com/list.json) - **List of hashes for EICAR test virus** - _Event contains one or more entries based on hashes for EICAR test virus_
- [empty-hashes/list.json](./lists/empty-hashes/list.json) - **List of known hashes for empty files** - _Event contains one or more entries of empty files based on known hashed_
- [f6-nt-scanning/list.json](./lists/f6-nt-scanning/list.json) - **F6 IP Ranges Used for Scanning** - _List containing IP's associated with the F6 scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [fastly/list.json](./lists/fastly/list.json) - **List of known Fastly IP address ranges** - _Fastly IP address ranges (https://api.fastly.com/public-ip-list)_
- [findip-host/list.json](./lists/findip-host/list.json) - **List of known hostname used for querying your source IP. This can be used as exclusion for your Passive DNS lookup.** - _Event contains one or more entries of known hostname querying your source IP._
- [github/list.json](./lists/github/list.json) - **List of known GitHub IP ranges (https://api.github.com/meta)** - _GitHub IP address ranges (https://api.github.com/meta)_
- [google-chrome-crux-1million/list.json](./lists/google-chrome-crux-1million/list.json) - **google-chrome-crux-1million** - _Cached Chrome Top Million Websites - top 1 million_
- [google-gcp/list.json](./lists/google-gcp/list.json) - **List of known GCP (Google Cloud Platform) IP address ranges** - _GCP (Google Cloud Platform) IP address ranges (https://www.gstatic.com/ipranges/cloud.json)_
- [google-gmail-sending-ips/list.json](./lists/google-gmail-sending-ips/list.json) - **List of known Gmail sending IP ranges** - _List of known Gmail sending IP ranges (https://support.google.com/a/answer/27642?hl=en)_
- [google/list.json](./lists/google/list.json) - **List of known google domains** - _Event contains one or more entries of known google domains_
- [googlebot/list.json](./lists/googlebot/list.json) - **List of known Googlebot IP ranges (https://developers.google.com/search/apis/ipranges/googlebot.json)** - _Google Bot IP address ranges (https://developers.google.com/search/apis/ipranges/googlebot.json)_
- [internet-census-nt-scanning/list.json](./lists/internet-census-nt-scanning/list.json) - **Internet census IP Ranges Used for Scanning** - _List containing IP's associated with the Internet census scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [intrinsec-nt-scanning/list.json](./lists/intrinsec-nt-scanning/list.json) - **Intrinsec IP Ranges Used for Scanning** - _List containing IP's associated with the Intrinsec scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [ipinfo-nt-scanning/list.json](./lists/ipinfo-nt-scanning/list.json) - **Ipinfo IP Ranges Used for Scanning** - _List containing IP's associated with the Ipinfo scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [ipip-nt-scanning/list.json](./lists/ipip-nt-scanning/list.json) - **Ipip IP Ranges Used for Scanning** - _List containing IP's associated with the Ipip scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [ipv6-linklocal/list.json](./lists/ipv6-linklocal/list.json) - **List of IPv6 link local blocks** - _Event contains one or more entries part of the IPv6 link local prefix (RFC 4291)_
- [link-in-bio/list.json](./lists/link-in-bio/list.json) - **List of known link in Bio domains** - _Event contains one or more entries of known Link in bio domains. Those shorten links are a reference to a list of links._
- [lots-project/list.json](./lists/lots-project/list.json) - **List of LOTS (Living Off Trusted Sites) Project Domains** - _List of popular legitimate domains from LOTS (Living Off Trusted Sites) Project used to conduct phishing, C&C, exfiltration or downloading tools to evade detection_
- [majestic_million/list.json](./lists/majestic_million/list.json) - **Top 10000 websites from Majestic Million** - _Event contains one or more entries from the top 10K of the most used websites (Majestic Million)._
- [microsoft-attack-simulator/list.json](./lists/microsoft-attack-simulator/list.json) - **List of known Office 365 Attack Simulator used for phishing awareness campaigns** - _Office 365 URLs and IP address ranges used for their attack simulator in Office 365 Threat Intelligence_
- [microsoft-azure-appid/list.json](./lists/microsoft-azure-appid/list.json) - **List of Azure Applicaiton IDs** - _List of Azure Application IDs (https://learn.microsoft.com/en-us/troubleshoot/azure/active-directory/verify-first-party-apps-sign-in)_
- [microsoft-azure-china/list.json](./lists/microsoft-azure-china/list.json) - **List of known Microsoft Azure China Datacenter IP Ranges** - _Microsoft Azure China Datacenter IP Ranges_
- [microsoft-azure-germany/list.json](./lists/microsoft-azure-germany/list.json) - **List of known Microsoft Azure Germany Datacenter IP Ranges** - _Microsoft Azure Germany Datacenter IP Ranges_
- [microsoft-azure-us-gov/list.json](./lists/microsoft-azure-us-gov/list.json) - **List of known Microsoft Azure US Government Cloud Datacenter IP Ranges** - _Microsoft Azure US Government Cloud Datacenter IP Ranges_
- [microsoft-azure/list.json](./lists/microsoft-azure/list.json) - **List of known Microsoft Azure Datacenter IP Ranges** - _Microsoft Azure Datacenter IP Ranges_
- [microsoft-office365-cn/list.json](./lists/microsoft-office365-cn/list.json) - **List of known Office 365 IP address ranges in China** - _Office 365 IP address ranges in China_
- [microsoft-office365-ip/list.json](./lists/microsoft-office365-ip/list.json) - **List of known Office 365 IP address ranges** - _Office 365 IP address ranges_
- [microsoft-office365/list.json](./lists/microsoft-office365/list.json) - **List of known Office 365 URLs** - _Office 365 URLs and IP address ranges_
- [microsoft-win10-connection-endpoints/list.json](./lists/microsoft-win10-connection-endpoints/list.json) - **List of known Windows 10 connection endpoints** - _Event contains one or more entries of known Windows 10 connection endpoints (https://docs.microsoft.com/en-us/windows/privacy/manage-windows-endpoints)_
- [microsoft/list.json](./lists/microsoft/list.json) - **List of known microsoft domains** - _Event contains one or more entries of known microsoft domains_
- [modat-nt-scanning/list.json](./lists/modat-nt-scanning/list.json) - **Modat IP Ranges Used for Scanning** - _List containing IP's associated with the Modat scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [modat-scanner/list.json](./lists/modat-scanner/list.json) - **List of published IP address ranges for Modat Scanner** - _Modat Scanner (https://www.modat.io/)_
- [moz-top500/list.json](./lists/moz-top500/list.json) - **Top 500 domains and pages from https://moz.com/top500** - _Event contains one or more entries from the top 500 of the most used domains from Moz._
- [mozilla-CA/list.json](./lists/mozilla-CA/list.json) - **Fingerprint of trusted CA certificates** - _Fingerprint of trusted CA certificates taken from Mozilla's lists at https://wiki.mozilla.org/CA_
- [mozilla-IntermediateCA/list.json](./lists/mozilla-IntermediateCA/list.json) - **Fingerprint of known intermediate of trusted certificates** - _Fingerprint of known intermediate of trusted certificates taken from Mozilla's lists at https://wiki.mozilla.org/CA_
- [multicast/list.json](./lists/multicast/list.json) - **List of RFC 5771 multicast CIDR blocks** - _Event contains one or more entries part of the RFC 5771 multicast CIDR blocks_
- [netsecscan-nt-scanning/list.json](./lists/netsecscan-nt-scanning/list.json) - **Netsecscan IP Ranges Used for Scanning** - _List containing IP's associated with the Netsecscan scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [netsecscan-scanning/list.json](./lists/netsecscan-scanning/list.json) - **NetSecScan IP-Ranges, pot. used for Scanning** - _List of NetSecScan.net scanners _
- [nioc-filehash/list.json](./lists/nioc-filehash/list.json) - **List of known hashes for benign files** - _Event contains one or more benign files based on known hashes, see https://github.com/RichieB2B/nioc_
- [onyphe-nt-scanning/list.json](./lists/onyphe-nt-scanning/list.json) - **Onyphe IP Ranges Used for Scanning** - _List containing IP's associated with the Onyphe scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [onyphe-scanner/list.json](./lists/onyphe-scanner/list.json) - **List of published IP address ranges for Onyphe Scanner** - _Onyphe Scanner (https://www.onyphe.io/)_
- [openai-gptbot/list.json](./lists/openai-gptbot/list.json) - **List of known IP address ranges for OpenAI GPT crawler bot** - _OpenAI gptbot crawler (https://openai.com/gptbot-ranges.txt)_
- [ovh-cluster/list.json](./lists/ovh-cluster/list.json) - **List of known Ovh Cluster IP** - _OVH Cluster IP address (https://docs.ovh.com/fr/hosting/liste-des-adresses-ip-des-clusters-et-hebergements-web/)_
- [parking-domain-ns/list.json](./lists/parking-domain-ns/list.json) - **Parking domains name server** - _List of parking domain's name server_
- [parking-domain/list.json](./lists/parking-domain/list.json) - **Parking domains** - _List of parking domain's ip adresses_
- [phone_numbers/list.json](./lists/phone_numbers/list.json) - **Unattributed phone number.** - _Numbers that cannot be attributed because they reserved for different purposes._
- [probethenet-nt-scanning/list.json](./lists/probethenet-nt-scanning/list.json) - **Probethenet IP Ranges Used for Scanning** - _List containing IP's associated with the Probethenet scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [public-dns-hostname/list.json](./lists/public-dns-hostname/list.json) - **List of known public DNS resolvers expressed as hostname** - _Event contains one or more public DNS resolvers (expressed as hostname) as attribute with an IDS flag set_
- [public-dns-v4/list.json](./lists/public-dns-v4/list.json) - **List of known IPv4 public DNS resolvers** - _Event contains one or more public IPv4 DNS resolvers as attribute with an IDS flag set_
- [public-dns-v6/list.json](./lists/public-dns-v6/list.json) - **List of known IPv6 public DNS resolvers** - _Event contains one or more public IPv6 DNS resolvers as attribute with an IDS flag set_
- [public-ipfs-gateways/list.json](./lists/public-ipfs-gateways/list.json) - **List of known public IPFS gateways** - _Event contains one or more entries of known public IPFS gateways_
- [rapid7-nt-scanning/list.json](./lists/rapid7-nt-scanning/list.json) - **Rapid7 IP Ranges Used for Scanning** - _List containing IP's associated with the Rapid7 scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [research-scanner-nt-scanning/list.json](./lists/research-scanner-nt-scanning/list.json) - **Research scanner IP Ranges Used for Scanning** - _List containing IP's associated with the Research scanner scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [rfc1918/list.json](./lists/rfc1918/list.json) - **List of RFC 1918 CIDR blocks** - _Event contains one or more entries part of the private network CIDR blocks (RFC 1918)_
- [rfc3849/list.json](./lists/rfc3849/list.json) - **List of RFC 3849 CIDR blocks** - _Event contains one or more entries part of the IPv6 documentation prefix (RFC 3849)_
- [rfc5735/list.json](./lists/rfc5735/list.json) - **List of RFC 5735 CIDR blocks** - _Event contains one or more entries part of the Special Use IPv4 Addresses CIDR blocks (RFC 5735)_
- [rfc6598/list.json](./lists/rfc6598/list.json) - **List of RFC 6598 CIDR blocks** - _Event contains one or more entries part of the Shared Address Space CIDR blocks (RFC 6598)_
- [rfc6761/list.json](./lists/rfc6761/list.json) - **List of RFC 6761 Special-Use Domain Names** - _Event contains one or more entries part of the Special-Use Domain Names (RFC 6761)_
- [second-level-tlds/list.json](./lists/second-level-tlds/list.json) - **Second level TLDs as known by Mozilla Foundation** - _Event contains one or more second level TLDs as attribute with an IDS flag set._
- [security-provider-blogpost/list.json](./lists/security-provider-blogpost/list.json) - **List of known security providers/vendors blog domain** - _Event contains one or more entries of known security providers/vendors blog domain with an IDS flag set_
- [shadowforce-nt-scanning/list.json](./lists/shadowforce-nt-scanning/list.json) - **Shadowforce IP Ranges Used for Scanning** - _List containing IP's associated with the Shadowforce scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [shadowforce-scanning/list.json](./lists/shadowforce-scanning/list.json) - **Shadowforce IP-Ranges, pot. used for Scanning** - _List of shadowforce.io scanners _
- [shadowserver-nt-scanning/list.json](./lists/shadowserver-nt-scanning/list.json) - **Shadowserver IP Ranges Used for Scanning** - _List containing IP's associated with the Shadowserver scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [shadowserver/list.json](./lists/shadowserver/list.json) - **Shadowserver IP-Ranges, pot. used for Scanning** - _List of Shadowserver IP-Ranges. Potentially associated with Shadowserver scans. based on [https://bgp.he.net/search?search%5Bsearch%5D=shadowserver&commit=Search]_
- [shodan-nt-scanning/list.json](./lists/shodan-nt-scanning/list.json) - **Shodan IP Ranges Used for Scanning** - _List containing IP's associated with the Shodan scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [shodan-scanning/list.json](./lists/shodan-scanning/list.json) - **Shodan IP-Ranges, pot. used for Scanning** - _List of Shodan.io scanners _
- [sinkholes/list.json](./lists/sinkholes/list.json) - **List of known sinkholes** - _List of known sinkholes_
- [skipa-nt-scanning/list.json](./lists/skipa-nt-scanning/list.json) - **Skipa IP Ranges Used for Scanning** - _List containing IP's associated with the Skipa scanners. This scanner CIDR range is extracted from CIRCL Network Telescope analysis on 2025/12/10_
- [smtp-receiving-ips/list.json](./lists/smtp-receiving-ips/list.json) - **List of known SMTP receiving IP addresses** - _List of IP addresses for known SMTP servers._
- [smtp-sending-ips/list.json](./lists/smtp-sending-ips/list.json) - **List of known SMTP sending IP ranges** - _List of IP ranges for known SMTP servers._
- [stackpath/list.json](./lists/stackpath/list.json) - **List of known Stackpath CDN IP ranges** - _List of known Stackpath (Highwinds) CDN IP ranges (https://support.stackpath.com/hc/en-us/articles/360001091666-Whitelist-CDN-WAF-IP-Blocks)_
- [tenable-cloud-ipv4/list.json](./lists/tenable-cloud-ipv4/list.json) - **List of known Tenable Cloud Sensors IPv4** - _Tenable IPv4 Cloud Sensor addresses used for scanning Internet-facing infrastructure_
- [tenable-cloud-ipv6/list.json](./lists/tenable-cloud-ipv6/list.json) - **List of known Tenable Cloud Sensors IPv6** - _Tenable IPv6 Cloud Sensor addresses used for scanning Internet-facing infrastructure_
- [ti-falsepositives/list.json](./lists/ti-falsepositives/list.json) - **Hashes that are often included in IOC lists but are false positives.** - _Hashes that are often included in IOC lists but are false positives._
- [tlds/list.json](./lists/tlds/list.json) - **TLDs as known by IANA** - _Event contains one or more TLDs as attribute with an IDS flag set_
- [tranco/list.json](./lists/tranco/list.json) - **Top 1,000,000 most-used sites from Tranco** - _Event contains one or more entries from the top 1,000,000 most-used sites (https://tranco-list.eu/)._
- [tranco10k/list.json](./lists/tranco10k/list.json) - **Top 10K most-used sites from Tranco** - _Event contains one or more entries from the top 10K most-used sites (https://tranco-list.eu/)._
- [umbrella-blockpage-hostname/list.json](./lists/umbrella-blockpage-hostname/list.json) - **cisco-umbrella-blockpage-hostname** - _Umbrella blockpage hostnames_
- [umbrella-blockpage-v4/list.json](./lists/umbrella-blockpage-v4/list.json) - **cisco-umbrella-blockpage-ipv4** - _Cisco Umbrella blockpage in IPv4_
- [umbrella-blockpage-v6/list.json](./lists/umbrella-blockpage-v6/list.json) - **cisco-umbrella-blockpage-ipv6** - _Cisco Umbrella blockpage in IPv6_
- [university_domains/list.json](./lists/university_domains/list.json) - **University domains** - _List of University domains from https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json_
- [url-shortener/list.json](./lists/url-shortener/list.json) - **List of known URL Shorteners domains** - _Event contains one or more entries of known Shorteners domains_
- [vpn-ipv4/list.json](./lists/vpn-ipv4/list.json) - **Specialized list of vpn-ipv4 addresses belonging to common VPN providers and datacenters** - _Specialized list of vpn-ipv4 addresses belonging to common VPN providers and datacenters_
- [vpn-ipv6/list.json](./lists/vpn-ipv6/list.json) - **Specialized list of IPv6 addresses belonging to common VPN providers and datacenters** - _Specialized list of IPv6 addresses belonging to common VPN providers and datacenters_
- [whats-my-ip/list.json](./lists/whats-my-ip/list.json) - **List of known domains to know external IP** - _Event contains one or more entries of known 'what's my ip' domains_
- [wikimedia/list.json](./lists/wikimedia/list.json) - **List of known Wikimedia address ranges** - _Wikimedia address ranges (http://noc.wikimedia.org/conf/reverse-proxy.php.txt)_
- [zscaler/list.json](./lists/zscaler/list.json) - **List of known Zscaler IP address ranges** - _Zscaler IP address ranges (https://config.zscaler.com/api/zscaler.net/hubs/cidr/json/recommended)_

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

# Using warning lists in Earthly builds

Lists are exposed to [Earthly](https://github.com/earthly/earthly) builds through the target `export-lists`. Earthfiles can directly reference them in their copy statements as follows:
```earthly
COPY github.com/MISP/misp-warninglists[:commit]+export-lists/lists/<list-name>/list.json ./
```

# License

MISP warning-lists are licensed under [CC0 1.0 Universal (CC0 1.0)](https://creativecommons.org/publicdomain/zero/1.0/) -  Public Domain Dedication. If a specific author of a warning-list (or associated source) wants to license it under a different license, a pull request can be requested.
