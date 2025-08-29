
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple, Dict

@dataclass
class Provenance:
    source: str
    url: Optional[str] = None
    author: Optional[str] = None
    confidence: float = 0.5

@dataclass
class ValidityWindow:
    start: Optional[str] = None  # ISO date
    end: Optional[str] = None    # ISO date

@dataclass
class AtomicFact:
    subject: str
    predicate: str
    obj: str
    prov: Provenance
    window: ValidityWindow
    meta: Dict[str,str] | None = None
