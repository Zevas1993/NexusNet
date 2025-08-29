
from __future__ import annotations
from typing import Dict, Any, List, Callable
from .profiler import measure

def bakeoff(candidates: List[Dict[str,Any]], prompt: str, call: Callable[[Dict[str,Any], str], str]) -> List[Dict[str,Any]]:
    results = []
    for c in candidates:
        stats = measure(lambda: call(c, prompt), trials=2)
        c2 = dict(c); c2.update(stats)
        results.append(c2)
    results.sort(key=lambda x: (x["p50"], x["p95"]))
    return results
