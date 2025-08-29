
from __future__ import annotations
import time
from typing import Callable, Dict

def measure(fn: Callable[[], str], trials: int = 3) -> Dict[str,float]:
    lat = []
    start = time.perf_counter()
    for _ in range(trials):
        t0 = time.perf_counter()
        _ = fn()
        lat.append(time.perf_counter()-t0)
    total = time.perf_counter()-start
    return {"p50": sorted(lat)[len(lat)//2], "p95": sorted(lat)[int(0.95*len(lat))-1], "total": total}
