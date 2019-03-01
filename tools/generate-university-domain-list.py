#!/usr/bin/env python3


import requests
import datetime
import json

json_output=dict()
json_output['type']="hostname"
json_output['name']="University domains"
json_output['matching_attributes']=['hostname','domain','url','domain|ip']
json_output['version']= int(datetime.date.today().strftime('%Y%m%d'))
json_output['description']="List of University domains from https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json"
json_output['list']=list()



url="https://raw.githubusercontent.com/Hipo/university-domains-list/master/world_universities_and_domains.json"
university_list_file=requests.get(url)
university_list_json=university_list_file.json()

for university in university_list_json:
	for domain in university.get('domains'):
		json_output['list'].append(domain)

with open('../lists/university_domains/list.json','w') as university_domains_output:
	university_domains_output.write(json.dumps(json_output, indent=1))
