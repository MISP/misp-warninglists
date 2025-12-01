#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json


for p in Path('../lists/').glob('*/*.json'):
    with p.open() as _f:
        warninglist = json.load(_f)
    lst = warninglist.get("list")
    if isinstance(lst, list):
        warninglist["list"] = sorted(set(lst))
    elif isinstance(lst, dict):
        warninglist["list"] = {k: lst[k] for k in sorted(lst)}
    else:
        raise TypeError("warninglist[‘list’] must be list or dict")

    with p.open('w') as _f:
        warninglist = json.dump(warninglist, _f, indent=2, sort_keys=True, ensure_ascii=False)
        _f.write('\n')
