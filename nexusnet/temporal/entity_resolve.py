
from __future__ import annotations
from rapidfuzz import process, fuzz

def canonicalize(name: str, aliases: dict[str, list[str]], threshold: int = 85) -> tuple[str, float]:
    candidates = list(aliases.keys())
    for k, al in aliases.items():
        candidates.extend(al)
    match = process.extractOne(name, candidates, scorer=fuzz.ratio)
    if not match:
        return name, 1.0
    best, score, _ = match
    for k, al in aliases.items():
        if best == k or best in al:
            return k, float(score)/100.0
    return name, float(score)/100.0
