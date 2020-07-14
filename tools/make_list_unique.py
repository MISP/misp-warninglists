#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json


for p in Path('../lists/').glob('*/*.json'):
    with p.open() as _f:
        warninglist = json.load(_f, encoding="utf-8")
    warninglist['list'] = sorted(list(set(warninglist['list'])))

    with p.open('w') as _f:
        warninglist = json.dump(warninglist, _f, indent=2, sort_keys=True, ensure_ascii=False)
        _f.write('\n')
