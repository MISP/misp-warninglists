from generator import get_abspath_source_file, download, get_version, write_to_file, consolidate_networks
from typing import List
import json
from time import sleep


def get_networks_for_asn(asn: int) -> List[str]:
    temp_file = get_abspath_source_file("bgp-asn-{}".format(asn))

    try:
        prefixes = json.load(open(temp_file, "r"))
    except:
        sleep(0.5)  # API has limitation, we have to wait between requests
        response = download("https://api.bgpview.io/asn/{}/prefixes".format(asn))
        response.raise_for_status()
        prefixes = response.json()
        json.dump(prefixes, open(temp_file, "w"))

    output = []
    for ipv4_prefix in prefixes["data"]["ipv4_prefixes"]:
        output.append(ipv4_prefix["prefix"])

    for ipv6_prefix in prefixes["data"]["ipv6_prefixes"]:
        output.append(ipv6_prefix["prefix"])
    return output


def search(term: str):
    response = download("https://api.bgpview.io/search?query_term={}".format(term))
    response.raise_for_status()
    return response.json()


def is_akamai(data: dict) -> bool:
    if not data["name"].startswith("AKAMAI"):
        return False

    for email in data["abuse_contacts"]:
        if "@akamai.com" in email:
            return True

    return False


if __name__ == '__main__':
    # Fetch all AS that belongs to AKAMAI
    search_result = search("AKAMAI")

    networks = set()
    asn_to_fetch = []
    for asn in search_result["data"]["asns"]:
        if is_akamai(asn):
            asn_to_fetch.append(asn["asn"])

    for prefix in search_result["data"]["ipv4_prefixes"]:
        if is_akamai(prefix):
            networks.add(prefix["prefix"])

    for prefix in search_result["data"]["ipv6_prefixes"]:
        if is_akamai(prefix):
            networks.add(prefix["prefix"])

    for asn in asn_to_fetch:
        try:
            networks.update(get_networks_for_asn(asn))
        except Exception as e:
            print(str(e))

    warninglist = {
        'name': 'List of known Akamai IP ranges',
        'version': get_version(),
        'description': 'Akamai IP ranges from BGP search',
        'type': 'cidr',
        'list': consolidate_networks(networks),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"]
    }
    write_to_file(warninglist, "akamai")

