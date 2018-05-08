#!/usr/bin/env python3

# warninglists.py - make use of misp-warninglists in python code
# Copyright (C) 2018, Daniel Roethlisberger <daniel@roe.ch>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions, and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
# IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT
# NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
# THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# NOTES
# -   Warninglists of type regex are untested due to lack of lists using it.
# -   Exact matching behaviour may or may not be different from MISP itself.
# -   For use on larger data sets, consider precomputing which warninglists
#     handle which attributes and combining the CIDR ranges into a prefix
#     tree instead of treating them as a flat list of ranges.

import ipaddress
import json
import os
import re
import urllib.parse


class WarningList:
    """
    Represents a single warninglist and provides a match function.
    """
    def __init__(self, path):
        """
        Load a warninglist in JSON format from the file pointed to by *path*.
        """
        with open(path, 'r') as f:
            data = json.load(f)
        self._matching_attributes = self._get_matching_attributes(data, path)
        listtype = self._get_type(data, path)
        listdata = self._get_list(data, path)
        if listtype in ('string', 'substring', 'hostname'):
            self._list = set([x.lower().rstrip('.') for x in listdata])
        elif listtype == 'cidr':
            self._list = [ipaddress.ip_network(x) for x in listdata]
        elif listtype == 'regex':
            self._list = [re.compile(x) for x in listdata]
        else:
            raise ValueError("unknown type '%s' in '%s'" % (listtype, path))
        setattr(self, '_matchfunc', getattr(self, '_matchfunc_' + listtype))

    def _matchfunc_string(self, key, value):
        return value in self._list

    def _matchfunc_substring(self, key, value):
        for entry in self._list:
            if entry in value:
                return True
        return False

    def _matchfunc_hostname(self, key, value):
        if key == 'url':
            value = urllib.parse.urlparse(value).netloc
        for entry in self._list:
            if value == entry or value.endswith('.' + entry):
                return True
        return False

    def _matchfunc_cidr(self, key, value):
        value = ipaddress.ip_address(value)
        for entry in self._list:
            if value in entry:
                return True
        return False

    def _matchfunc_regex(self, key, value):
        for entry in self._list:
            if entry.match(value):
                return True
        return False

    def match(self, key, value):
        """
        Returns True iff the attribute of type *key* and value *value* matches
        this warninglist, False otherwise.
        """
        if '|' in key:
            # for multi-value fields, use the first part that the list wants
            for i, subkey in enumerate(key.split('|')):
                if subkey == 'ip':
                    subkey = 'ip-dst'
                if subkey not in self._matching_attributes:
                    continue
                if '|' not in value:
                    raise ValueError("key contains pipe, but value does not")
                key = subkey
                value = value.split('|')[i]
                break
        if key not in self._matching_attributes:
            return False
        value = value.lower()
        return self._matchfunc(key, value)

    @staticmethod
    def _get_type(data, path):
        if 'type' not in data:
            raise ValueError("no 'type' in '%s'" % path)
        return data['type']

    @staticmethod
    def _get_list(data, path):
        if 'list' not in data:
            raise ValueError("no 'list' in '%s'" % path)
        l = data['list']
        if not isinstance(l, (tuple, list)):
            raise ValueError("'list' is not a list in '%s'" % path)
        return l

    @staticmethod
    def _get_matching_attributes(data, path):
        if 'matching_attributes' not in data:
            raise ValueError("no 'matching_attributes' in '%s'" % path)
        l = data['matching_attributes']
        if not isinstance(l, (tuple, list)):
            raise ValueError(
                    "'matching-attributes' is not a list in '%s'" % path)
        return l


class WarningLists:
    """
    Loads multiple lists into memory and provides a method for checking if an
    indicator is in any of the warning lists.
    """

    def __init__(self, paths):
        """
        Load warning lists from the files or directories pointed to by *paths*
        as string or iterable of strings.  JSON files are loaded directly,
        directories are recursively searched for JSON files.
        Normally, you would point *paths* to the 'lists' subdirectory of the
        misp-warninglists repository to load all warninglists but not the
        schema.
        """
        self._lists = []
        for path in self._find_lists(paths):
            self._lists.append(WarningList(path))

    def _find_lists(self, paths):
        if isinstance(paths, str):
            paths = [paths]
        for path in paths:
            if path.endswith('.json'):
                yield path
                continue
            for root, dirs, files in os.walk(path):
                for f in files:
                    if f.endswith('.json'):
                        yield os.path.join(root, f)

    def match(self, key, value):
        """
        Returns True iff attribute of type *key* and value *value* matches any
        of the loaded warninglists; False otherwise.
        """
        for l in self._lists:
            if l.match(key, value):
                return True
        return False


if __name__ == '__main__':
    import sys
    lists = WarningLists(sys.argv[1:])
    assert(lists.match('domain', 'google.com'))
    assert(lists.match('domain|ip', 'asdhfzehljadhkdsfke.ch|8.8.8.8'))
    assert(lists.match('url', 'http://www.google.com/wiwawo?q=foobar'))
    assert(not lists.match('url', 'https://www.roe.ch/'))
    assert(lists.match('ip-dst', '127.0.0.1'))
    assert(lists.match('ip-dst', '8.8.8.8'))
    assert(not lists.match('ip-dst', '212.251.23.2'))

