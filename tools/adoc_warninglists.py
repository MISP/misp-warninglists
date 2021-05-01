#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#
#    A simple converter of MISP warning lists to asciidoctor format
#    Copyright (C) 2018 Alexandre Dulaunoy
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import json
import argparse

thisDir = os.path.dirname(__file__)

lists = []

pathLists = os.path.join(thisDir, '../lists')

for f in os.listdir(pathLists):
	filename = "{}/{}".format(f,"list.json")
	lists.append(filename)

lists.sort()

argParser = argparse.ArgumentParser(description='Generate documentation from MISP warning lists', epilog='Available warning lists are {0}'.format(lists))
argParser.add_argument('-v', action='store_true', help='Verbose mode')
args = argParser.parse_args()

def header(adoc=False):
    if adoc is False:
        return False

    dedication = "\n[dedication]\n== Funding and Support\nThe MISP project is financially and resource supported by https://www.circl.lu/[CIRCL Computer Incident Response Center Luxembourg ].\n\nimage:{images-misp}logo.png[CIRCL logo]\n\nA CEF (Connecting Europe Facility) funding under CEF-TC-2016-3 - Cyber Security has been granted from 1st September 2017 until 31th August 2019 as ***Improving MISP as building blocks for next-generation information sharing***.\n\nimage:{images-misp}en_cef.png[CEF funding]\n\nIf you are interested to co-fund projects around MISP, feel free to get in touch with us.\n\n"
    doc = adoc
    doc = doc + ":toc: right\n"
    doc = doc + ":toclevels: 1\n"
    doc = doc + ":toc-title: MISP warning lists\n"
    doc = doc + ":icons: font\n"
    doc = doc + ":sectanchors:\n"
    doc = doc + ":sectlinks:\n"
    doc = doc + ":images-cdn: https://raw.githubusercontent.com/MISP/MISP/2.4/INSTALL/logos/\n"
    doc = doc + ":images-misp: https://www.misp-project.org/assets/images/\n"
    doc = doc + "\n= MISP warning lists\n\n"
    doc = doc + "= Introduction\n"
    doc = doc + "\nimage::{images-cdn}misp-logo.png[MISP logo]\n\n"
    doc = doc + "The MISP threat sharing platform is a free and open source software helping information sharing of threat intelligence including cyber security indicators, financial fraud or counter-terrorism information. The MISP project includes multiple sub-projects to support the operational requirements of analysts and improve the overall quality of information shared.\n\n"
    doc = doc + ""
    doc = "{}{}".format(doc, "\nMISP warning lists are lists of well-known indicators that can be associated to potential false positives, errors or mistakes. The warning lists are integrated in MISP to display an info/warning box at the event and attribute level if such indicators are available in one of the list. The list can be globally enabled or disabled in MISP following the practices of the organization.\n")
    doc = doc + "The following document is generated from the machine-readable JSON describing the https://github.com/MISP/misp-warninglists[MISP warning lists]."
    doc = doc + "\n\n"
    doc = doc + "<<<\n"
    doc = doc + dedication
    doc = doc + "<<<\n"
    doc = doc + "= MISP warning lists\n"
    return doc

def asciidoc(content=False, adoc=None, t='title', title=''):
    adoc = adoc + "\n"
    output = ""
    if t == 'title':
        output = '== ' + content
    elif t == 'info':
        output = "\n{}.\n\n{} {} {} {}.".format(content, 'NOTE:' ,title, 'are warning lists available in JSON format at https://github.com/MISP/misp-warninglists/tree/main/lists.' ,'The JSON format can be freely reused in your application or automatically enabled in https://www.github.com/MISP/MISP[MISP]')
    elif t == 'description':
        output = "\n{} \n".format(content)
    elif t == 'list':
        output = "The warning list contains {} elements.\n".format(content)
    adoc = adoc + output
    return adoc
adoc = ""
print (header(adoc=adoc))

for warninglist in lists:
    fullPathLists = os.path.join(pathLists, warninglist)
    with open(fullPathLists) as fp:
        c = json.load(fp)
    title = c['name']
    adoc = asciidoc(content=title, adoc=adoc, t='title')
    adoc = asciidoc(content=c['description'], adoc=adoc, t='info', title=title)
    if 'matching_attributes' in c:
        adoc = asciidoc(content=c['matching_attributes'], adoc=adoc, t='matching_attributes')
    if 'list' in c:
        cards = len(c['list'])
    adoc = asciidoc(content=cards, adoc=adoc, t='list')

print(adoc)
