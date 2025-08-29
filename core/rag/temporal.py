
from __future__ import annotations
import time, math

def recency_boost(ts: int, halflife_days: int = 30) -> float:
    if ts <= 0: return 1.0
    age_days = (time.time() - ts)/86400.0
    lam = math.log(2)/max(1e-6, halflife_days)
    return math.exp(-lam*age_days)
