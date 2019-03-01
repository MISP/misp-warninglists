#!/usr/bin/env python3

import json
import os
import requests
import datetime

base_url="https://raw.githubusercontent.com/threatstop/crl-ocsp-whitelist/master/"
uri_list=['crl-hostnames.txt','crl-ipv4.txt','crl-ipv6.txt','ocsp-hostnames.txt','ocsp-ipv4.txt','ocsp-ipv6.txt']
dict=dict()
dict['list']=list()
def source_read_and_add(input_file):
	output_list=list()
	for item in input_file:
		item=item.rstrip()
		output_list.append(item)
	return output_list


for uri in uri_list:
	url = base_url + uri
	r=requests.get(url)
	dict['list'] += source_read_and_add(r.text)

dict['type'] = "string"
dict['matching_attributes']=["hostname","domain","ip-dst","ip-src","url", "domain|ip"]
dict['name']="CRL Warninglist"
dict['version']= int(datetime.date.today().strftime('%Y%m%d'))
dict['description']="CRL Warninglist from threatstop (https://github.com/threatstop/crl-ocsp-whitelist/)"
dict['list']=list(set(dict['list']))

with open('../lists/crl-ip-hostname/list.json', 'w') as dict_output:
	dict_output.write(json.dumps(dict))
