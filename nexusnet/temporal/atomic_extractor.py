
from __future__ import annotations
import re
from typing import List
from .schemas import AtomicFact, Provenance, ValidityWindow
from .normalize_time import normalize

_SIMPLE_PATTERNS = [
    re.compile(r"(?P<subj>[A-Z][\w\- ]+)\s+(?P<pred>is|was|became)\s+(?P<obj>[^.]+?)(?:\.|$)", re.I),
    re.compile(r"(?P<subj>[A-Z][\w\- ]+)\s+(?P<pred>announced|launched|released)\s+(?P<obj>[^.]+?)(?:\.|$)", re.I),
]

def extract_atomic(text: str, source: str = "ingest", url: str | None = None) -> List[AtomicFact]:
    facts: List[AtomicFact] = []
    # naive sentence split
    sentences = re.split(r"[\.!?]\s+", text)
    for s in sentences:
        s = s.strip()
        if not s: continue
        # try temporal window hints
        win = ValidityWindow()
        m = re.search(r"(?:since|from)\s+([0-9]{4}(?:-[0-9]{2}(?:-[0-9]{2})?)?)", s, re.I)
        if m:
            win.start = normalize(m.group(1)) or m.group(1)
        m2 = re.search(r"(?:until|through|till|to)\s+([0-9]{4}(?:-[0-9]{2}(?:-[0-9]{2})?)?)", s, re.I)
        if m2:
            win.end = normalize(m2.group(1)) or m2.group(1)
        for pat in _SIMPLE_PATTERNS:
            m3 = pat.search(s)
            if m3:
                prov = Provenance(source=source, url=url, confidence=0.55)
                facts.append(AtomicFact(m3.group("subj").strip(), m3.group("pred").lower().strip(), m3.group("obj").strip(), prov, win, {}))
                break
    return facts
