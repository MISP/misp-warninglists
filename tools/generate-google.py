#!/usr/bin/env python3

from lxml import etree
from bs4 import BeautifulSoup
import datetime
import urllib.request, urllib.parse, urllib.error
import json

#webpage = urllib.request.urlopen("https://en.wikipedia.org/w/index.php?title=List_of_Google_domains&printable=yes")
webpage = urllib.request.urlopen("https://en.wikipedia.org/w/index.php?title=List_of_Google_domains")
soup = BeautifulSoup(webpage,'html.parser')

tables = soup.find_all("table", { "class" : "wikitable sortable" })
#print(tables)

gdomains = []
for tabl in tables :

    for row in tabl.findAll("tr"):
        cells = row.findAll('td')
        if len(cells) == 4:
            domain = cells[2].find_all(text=True)

            if len(domain) is 1 :
                domain = "{}".format(domain[0])
            elif len(domain) is 2 :
                domain = "{}{}".format(domain[0], domain[1])
            elif len(domain) is 3  and not "[" in domain[2]:
                domain = "{}{}".format(domain[0], domain[2])
            else:
                domain = "{}{}".format(domain[0], domain[1])

            print(domain)

            gdomains.append(domain)
#print(gdomains)
gdomains = sorted(set(gdomains))

google_warninglist = {}
version = int(datetime.date.today().strftime('%Y%m%d'))

google_warninglist['description'] = "Event contains one or more entries from the google owned domains."
d = datetime.datetime.now()
google_warninglist['version'] = version
google_warninglist['name'] = "Known Google domains"
google_warninglist['list'] = []
google_warninglist['matching_attributes'] = ['hostname', 'domain']

for site in gdomains:
    #v = str(site).split(',')[1]
    google_warninglist['list'].append(site)
google_warninglist['list'] = sorted(set(google_warninglist['list']))
#print(json.dumps(google_warninglist))                                                                       
