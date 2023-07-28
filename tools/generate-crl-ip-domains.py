#!/usr/bin/env python3
import csv
import logging
import multiprocessing.dummy
import urllib.parse
import sys
from OpenSSL.crypto import FILETYPE_PEM, load_certificate, X509
from pyasn1.codec.der.decoder import decode as asn1_decoder
from pyasn1_modules.rfc2459 import CRLDistPointsSyntax, AuthorityInfoAccessSyntax
from typing import List, Set
from dns.resolver import NoAnswer, NXDOMAIN, NoNameservers
from dns.exception import Timeout
import dns
from generator import download_to_file, get_version, write_to_file, get_abspath_source_file, create_resolver


def get_domain(url: str) -> str:
    return urllib.parse.urlparse(url).hostname


def get_crl_ocsp_domains(cert: X509) -> List[str]:
    crl_ocsp_domains = []
    for i in range(0, cert.get_extension_count()):
        extension = cert.get_extension(i)
        short_name = extension.get_short_name()
        if short_name == b'crlDistributionPoints':
            decoded, _ = asn1_decoder(extension.get_data(), asn1Spec=CRLDistPointsSyntax())
            for crl in decoded:
                for generalName in crl.getComponentByName('distributionPoint').getComponentByName('fullName'):
                    crl_url = generalName.getComponentByName('uniformResourceIdentifier')
                    domain = get_domain(str(crl_url))
                    if domain:
                        crl_ocsp_domains.append(domain)

        elif short_name == b'authorityInfoAccess':
            decoded, _ = asn1_decoder(extension.get_data(), asn1Spec=AuthorityInfoAccessSyntax())
            for section in decoded:
                if str(section.getComponentByName('accessMethod')) == '1.3.6.1.5.5.7.48.1':  # ocsp
                    ocsp_url = section.getComponentByName('accessLocation').getComponentByName(
                        'uniformResourceIdentifier')
                    domain = get_domain(str(ocsp_url))
                    if domain:
                        crl_ocsp_domains.append(domain)

    return crl_ocsp_domains


def get_ips_from_domain(domain: str) -> Set[str]:
    resolver = create_resolver()
    ips = set()

    try:
        answers = dns.resolver.resolve(domain, 'A')
        for rdata in answers:
            ips.add(str(rdata))
    except (NoAnswer, NXDOMAIN, NoNameservers, Timeout):
        pass
    try:
        answers = dns.resolver.resolve(domain, 'AAAA')
        for rdata in answers:
            ips.add(str(rdata))
    except (NoAnswer, NXDOMAIN, NoNameservers, Timeout):
        pass

    return ips


def get_ips_from_domains(domains) -> Set[str]:
    p = multiprocessing.dummy.Pool(10)
    ips = set()
    for ips_for_domain in p.map(get_ips_from_domain, domains):
        ips.update(ips_for_domain)
    return ips


def process(file):
    crl_ocsp_domains = set()
    with open(get_abspath_source_file(file), 'r') as f_in:
        for obj in csv.DictReader(f_in):
            try:
                pem = obj['PEM Info'].strip("'").replace('\r', '').replace('\n\n', '\n')
                cert = load_certificate(FILETYPE_PEM, pem)
                crl_ocsp_domains.update(get_crl_ocsp_domains(cert))
            except Exception:
                logging.exception("Could not process certificate")

    warninglist = {
        'name': 'CRL and OCSP domains',
        'version': get_version(),
        'description': 'Domains that belongs to CRL or OCSP',
        'list': crl_ocsp_domains,
        'matching_attributes': ["hostname", "domain", "domain|ip"],
        'type': 'string',
    }
    write_to_file(warninglist, "crl-hostname")

    warninglist = {
        'name': 'CRL and OCSP IP addresses',
        'version': get_version(),
        'description': 'IP addresses that belongs to CRL or OCSP',
        'list': get_ips_from_domains(crl_ocsp_domains),
        'matching_attributes': ["ip-src", "ip-dst", "domain|ip"],
        'type': 'cidr',
    }
    write_to_file(warninglist, "crl-ip")


if __name__ == '__main__':
    CA_known_intermediate_url = 'https://ccadb-public.secure.force.com/mozilla/PublicAllIntermediateCertsWithPEMCSV'
    CA_known_intermediate_file = 'PublicAllIntermediateCertsWithPEMCSV.csv'

    download_to_file(CA_known_intermediate_url, CA_known_intermediate_file)
    process(CA_known_intermediate_file)
