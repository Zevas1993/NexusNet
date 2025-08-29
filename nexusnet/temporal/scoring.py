
from __future__ import annotations
def blend(semantic: float, freshness: float, provenance: float, consistency: float, w=(0.50,0.25,0.15,0.10)) -> float:
    a,b,c,d = w
    return a*semantic + b*freshness + c*provenance + d*consistency
