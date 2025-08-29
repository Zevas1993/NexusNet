
from __future__ import annotations
import re
from typing import List, Dict

REL_TEMPLATES = [
    (r'([A-Z][A-Za-z0-9_ ]+) (released|announced) (.+?)\.', 'event'),
    (r'([A-Z][A-Za-z0-9_ ]+) (acquired) ([A-Z][A-Za-z0-9_ ]+)', 'mna'),
]

def extract_facts(text: str) -> List[Dict]:
    out=[]
    for pat,kind in REL_TEMPLATES:
        for m in re.finditer(pat, text):
            s, p, o = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            out.append({"s":s,"p":p,"o":o,"kind":kind})
    return out
