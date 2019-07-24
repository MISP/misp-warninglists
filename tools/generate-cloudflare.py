#!/usr/bin/env python3

import json
import os
import requests
import datetime
import io

base_url="https://www.cloudflare.com/"
uri_list=['ips-v4','ips-v6']
dict=dict()
dict['list']=list()
def source_read_and_add(input_file):
	output_list=list()

	for line in input_file.splitlines():
		output_list.append(line)
	return output_list


for uri in uri_list:
	url = base_url + uri
	r=requests.get(url)
	dict['list'] += source_read_and_add(r.text)

dict['type'] = "cidr"
dict['matching_attributes']=["ip-dst","ip-src","domain|ip"]
dict['name']="List of known Cloudflare IP ranges"
dict['version']= int(datetime.date.today().strftime('%Y%m%d'))
dict['description']="List of known Cloudflare IP ranges (https://www.cloudflare.com/ips/)"
dict['list']=list(set(dict['list']))

print(json.dumps(dict))
