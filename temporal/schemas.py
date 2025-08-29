
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class AtomicFact:
    subject: str
    predicate: str
    object: str
    source: str
    valid_from: int
    valid_to: int
    provenance: Optional[str] = None
