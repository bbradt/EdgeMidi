# -*- coding: utf-8 -*-
"""
Created on Sat May 26 23:02:12 2018

@author: Brad
"""
import re
import numpy as np

def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.
    """
    import unicodedata
    value = str(unicodedata.normalize('NFKD', value).encode('ascii', 'ignore'))
    value = str(re.sub('[^\w\s-]', '', value).strip().lower())
    value = str(re.sub('[-\s]+', '_', value))
    return value[1:]

def chunks(l, n):
    """Yield n chunks from l."""
    out = [[] for i in range(n)]
    for i, e in enumerate(l):
        if e is None:
            continue
        out[i % n].append(e) 
    return out