from __future__ import annotations
import time, random

def eval_candidate(candidate: dict, sample_prompts: list[str]) -> dict:
    seed = sum(ord(c) for c in str(candidate)) % 9973
    random.seed(seed)
    quality = 0.80 + 0.15 * random.random()
    b = candidate.get("bits", 8)
    kv = candidate.get("kv_cache_bits", 8)
    latency = max(5.0, 50.0/(b+kv/8.0))
    stability = 1.0
    return {"quality": quality, "latency_ms": latency, "stability": stability}

def score(fit: dict, w=(0.6,0.3,0.1)) -> float:
    q,l,s = fit["quality"], fit["latency_ms"], fit["stability"]
    l_norm = 1.0 / (1.0 + l/50.0)
    return w[0]*q + w[1]*l_norm + w[2]*s
