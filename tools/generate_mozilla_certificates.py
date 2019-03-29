#!/usr/bin/env python3

import csv
import datetime
import io
import json
import requests

from OpenSSL.crypto import load_certificate, FILETYPE_PEM

Included_CA_url = 'https://ccadb-public.secure.force.com/mozilla/IncludedCACertificateReportPEMCSV'
Included_CA_file = 'IncludedCACertificateReportPEMCSV.csv'
Included_CA_dst = 'mozilla-CA'
CA_known_intermediate_url = 'https://ccadb-public.secure.force.com/mozilla/PublicAllIntermediateCertsWithPEMCSV'
CA_known_intermediate_file = 'PublicAllIntermediateCertsWithPEMCSV.csv'
CA_known_intermediate_dst = 'mozilla-IntermediateCA'

def download(url, file):
    r = requests.get(url)
    with open(file, 'wb') as fd:
        for chunk in r.iter_content(4096):
            fd.write(chunk)

def gethash(cert, digest):
    return cert.digest(digest).decode('ASCII').replace(':', '').lower()

def process(file, dst, type):
    hashes = set()
    with open(file, 'r') as f_in:
        for obj in csv.DictReader(f_in):
            pem = obj['PEM Info'].strip("'").replace('\r','').replace('\n\n','\n')
            try:
                name = obj['Certificate Name']
            except:
                name = obj['Common Name or Certificate Name']
            cert = load_certificate(FILETYPE_PEM, pem)
            hashes.add(gethash(cert, 'md5'))
            hashes.add(gethash(cert, 'sha1'))
            hashes.add(obj['SHA-256 Fingerprint'].lower())
    warninglist = {}
    warninglist['name'] = 'Fingerprint of {type}'.format(type=type)
    warninglist['version'] = int(datetime.date.today().strftime('%Y%m%d'))
    warninglist['description'] = "Fingerprint of {type} taken from Mozilla's lists at https://wiki.mozilla.org/CA".format(type=type)
    warninglist['list'] = sorted(hashes)
    warninglist['type'] = 'string'
    warninglist['matching_attributes'] = ["md5", "sha1", "sha256", "filename|md5", "filename|sha1", "filename|sha256", "x509-fingerprint-md5", "x509-fingerprint-sha1", "x509-fingerprint-sha256"]
    with open('../lists/{dst}/list.json'.format(dst=dst), 'w') as data_file:
        json.dump(warninglist, data_file, indent=4, sort_keys=True)

if __name__ == '__main__':
    download(Included_CA_url, Included_CA_file)
    process(Included_CA_file, Included_CA_dst, 'trusted CA certificates')
    download(CA_known_intermediate_url, CA_known_intermediate_file)
    process(CA_known_intermediate_file, CA_known_intermediate_dst, 'known intermedicate of trusted certificates')
