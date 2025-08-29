
from __future__ import annotations
import re

ALIASES = {
    "openai": {"oai","open ai"},
    "google": {"alphabet", "google llc"},
    "microsoft": {"msft","microsoft corp","microsoft corporation"},
}

def normalize(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r'[^a-z0-9\s\-\._]', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s

def canonicalize(entity: str) -> str:
    n = normalize(entity)
    for k,vs in ALIASES.items():
        if n == k or n in vs:
            return k
    return n
