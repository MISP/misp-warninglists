import datetime
import ipaddress
import json
import logging
from inspect import currentframe, getframeinfo, getmodulename, stack
from os import mkdir, path
from typing import List, Union

import requests
import dns.exception
import dns.resolver
from dateutil.parser import parse as parsedate


def init_logging():
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    LOG_DIR = path.join(current_folder, '../generators.log')

    logFormatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s::%(funcName)s()::%(message)s")
    rootLogger = logging.getLogger()
    rootLogger.setLevel(logging.INFO)
    # Log to file
    fileHandler = logging.FileHandler(LOG_DIR)
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    # Log to console too
    ''' consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler) '''
    return rootLogger


init_logging()


def download_to_file(url, file):
    frame_records = stack()[1]
    caller = getmodulename(frame_records[1]).upper()

    user_agent = {
        "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    try:
        r = requests.head(url, headers=user_agent)
        url_datetime = parsedate(r.headers['Last-Modified']).astimezone()
        file_datetime = datetime.datetime.fromtimestamp(
            path.getmtime(get_abspath_source_file(file))).astimezone()

        if(url_datetime > file_datetime):
            logging.info('{} File on server is newer, so downloading update to {}'.format(
                caller, get_abspath_source_file(file)))
            actual_download_to_file(url, file, user_agent)
        else:
            logging.info(
                '{} File on server is older, nothing to do'.format(caller))
    except KeyError as exc:
        logging.warning('{} KeyError in the headers. the {} header was not sent by server {}. Downloading file'.format(
            caller, str(exc), url))
        actual_download_to_file(url, file, user_agent)
    except FileNotFoundError as exc:
        logging.info(
            "{} File didn't exist, so downloading {} from {}".format(caller, file, url))
        actual_download_to_file(url, file, user_agent)
    except Exception as exc:
        logging.warning(
            '{} General exception occured: {}.'.format(caller, str(exc)))
        actual_download_to_file(url, file, user_agent)


def actual_download_to_file(url, file, user_agent):
    r = requests.get(url, headers=user_agent)
    with open(get_abspath_source_file(file), 'wb') as fd:
        for chunk in r.iter_content(4096):
            fd.write(chunk)


def process_stream(url):
    r = requests.get(url, stream=True)

    data_list = []
    for line in r.iter_lines():
        v = line.decode('utf-8')
        if not v.startswith("#"):
            if v:
                data_list.append(v)

    return data_list


def download(url):
    user_agent = {
        "User-agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0"}
    return requests.get(url, headers=user_agent)


def get_abspath_list_file(dst):
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    real_path = path.join(
        current_folder, '../lists/{dst}/list.json'.format(dst=dst))
    return path.abspath(path.realpath(real_path))


def get_abspath_source_file(dst):
    rel_path = getframeinfo(currentframe()).filename
    current_folder = path.dirname(path.abspath(rel_path))
    tmp_path = path.join(current_folder, '../tmp/')
    if not path.exists(tmp_path):
        mkdir(tmp_path)
    return path.abspath(path.realpath(path.join(tmp_path, '{dst}'.format(dst=dst))))


def get_version():
    return int(datetime.date.today().strftime('%Y%m%d'))


def unique_sorted_warninglist(warninglist):
    warninglist['list'] = sorted(set(warninglist['list']))
    return warninglist


def write_to_file(warninglist, dst):
    frame_records = stack()[1]
    caller = getmodulename(frame_records[1]).upper()

    try:
        warninglist = unique_sorted_warninglist(warninglist)
        with open(get_abspath_list_file(dst), 'w') as data_file:
            json.dump(warninglist, data_file, indent=2, sort_keys=True)
            data_file.write("\n")
        logging.info('New warninglist written to {}.'.format(
            get_abspath_list_file(dst)))
    except Exception as exc:
        logging.error(
            '{} General exception occurred: {}.'.format(caller, str(exc)))


def consolidate_networks(networks):
    # Split to IPv4 and IPv6 ranges
    ipv4_networks = []
    ipv6_networks = []
    for network in networks:
        if isinstance(network, str):
            # Convert string to IpNetwork
            network = ipaddress.ip_network(network)

        if network.version == 4:
            ipv4_networks.append(network)
        else:
            ipv6_networks.append(network)

    # Collapse ranges
    networks_to_keep = list(map(str, ipaddress.collapse_addresses(ipv4_networks)))
    networks_to_keep.extend(map(str, ipaddress.collapse_addresses(ipv6_networks)))

    return networks_to_keep


def create_resolver() -> dns.resolver.Resolver:
    resolver = dns.resolver.Resolver(configure=False)
    resolver.timeout = 30
    resolver.lifetime = 30
    resolver.cache = dns.resolver.LRUCache()
    resolver.nameservers = ["193.17.47.1", "185.43.135.1"]  # CZ.NIC nameservers
    return resolver


class Spf:
    def __init__(self, resolver: dns.resolver.Resolver):
        self.__resolver = resolver

    def _parse_spf(self, domain: str, spf: str) -> dict:
        output = {"include": [], "ranges": [], "a": [], "mx": []}
        for part in spf.split(" "):
            if part.startswith("include:"):
                output["include"].append(part.split(":", 1)[1])
            elif part.startswith("redirect="):
                output["include"].append(part.split("=", 1)[1])
            elif part == "a":
                output["a"].append(domain)
            elif part.startswith("a:"):
                output["a"].append(part.split(":", 1)[1])
            elif part == "mx":
                output["mx"].append(domain)
            elif part.startswith("mx:"):
                output["mx"].append(part.split(":", 1)[1])
            elif part.startswith("ip4:") or part.startswith("ip6:"):
                output["ranges"].append(ipaddress.ip_network(part.split(":", 1)[1], strict=False))
        return output

    def _get_ip_for_domain(self, domain: str) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        ranges = []
        try:
            for ip in self.__resolver.query(domain, "a"):
                ranges.append(ipaddress.ip_network(str(ip)))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            pass

        try:
            for ip in self.__resolver.query(domain, "aaaa"):
                ranges.append(ipaddress.ip_network(str(ip)))
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            pass

        return ranges

    def _get_mx_ips_for_domain(self, domain: str) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        ranges = []
        try:
            for rdata in self.__resolver.query(domain, "mx"):
                ranges += self._get_ip_for_domain(rdata.exchange)
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout):
            pass
        return ranges

    def get_ip_ranges(self, domain: str) -> List[Union[ipaddress.IPv4Network, ipaddress.IPv6Network]]:
        try:
            txt_records = self.__resolver.query(domain, "TXT")
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.exception.Timeout) as e:
            logging.info("Could not fetch TXT record for domain {}: {}".format(domain, str(e)))
            return []

        ranges = []
        for rdata in txt_records:
            record = "".join([s.decode("utf-8") for s in rdata.strings])
            if not record.startswith("v=spf1"):
                continue

            parsed = self._parse_spf(domain, record)
            ranges += parsed["ranges"]

            for include in parsed["include"]:
                ranges += self.get_ip_ranges(include)

            for domain in parsed["a"]:
                ranges += self._get_ip_for_domain(domain)

            for mx in parsed["mx"]:
                ranges += self._get_mx_ips_for_domain(mx)

        return ranges


def main():
    init_logging()


if __name__ == '__main__':
    main()
