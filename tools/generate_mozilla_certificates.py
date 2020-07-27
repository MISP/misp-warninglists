#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv

from OpenSSL.crypto import FILETYPE_PEM, load_certificate

from generator import download_to_file, get_version, write_to_file


def gethash(cert, digest):
    return cert.digest(digest).decode('ASCII').replace(':', '').lower()


def process(file, dst, type):
    hashes = set()
    with open(file, 'r') as f_in:
        for obj in csv.DictReader(f_in):
            pem = obj['PEM Info'].strip("'").replace(
                '\r', '').replace('\n\n', '\n')
            try:
                obj['Certificate Name']
            except:
                obj['Common Name or Certificate Name']
            cert = load_certificate(FILETYPE_PEM, pem)
            hashes.add(gethash(cert, 'md5'))
            hashes.add(gethash(cert, 'sha1'))
            hashes.add(obj['SHA-256 Fingerprint'].lower())

    warninglist = {
        'name': 'Fingerprint of {type}'.format(type=type),
        'version': get_version(),
        'description': "Fingerprint of {type} taken from Mozilla's lists at https://wiki.mozilla.org/CA".format(
            type=type),
        'list': hashes,
        'type': 'string',
        'matching_attributes': ["md5", "sha1", "sha256", "filename|md5", "filename|sha1",
                                "filename|sha256", "x509-fingerprint-md5", "x509-fingerprint-sha1", "x509-fingerprint-sha256"]
    }

    write_to_file(warninglist, dst)


if __name__ == '__main__':
    Included_CA_url = 'https://ccadb-public.secure.force.com/mozilla/IncludedCACertificateReportPEMCSV'
    Included_CA_file = 'IncludedCACertificateReportPEMCSV.csv'
    Included_CA_dst = 'mozilla-CA'
    CA_known_intermediate_url = 'https://ccadb-public.secure.force.com/mozilla/PublicAllIntermediateCertsWithPEMCSV'
    CA_known_intermediate_file = 'PublicAllIntermediateCertsWithPEMCSV.csv'
    CA_known_intermediate_dst = 'mozilla-IntermediateCA'

    download_to_file(Included_CA_url, Included_CA_file)
    process(Included_CA_file, Included_CA_dst, 'trusted CA certificates')
    download_to_file(CA_known_intermediate_url, CA_known_intermediate_file)
    process(CA_known_intermediate_file, CA_known_intermediate_dst,
            'known intermedicate of trusted certificates')
