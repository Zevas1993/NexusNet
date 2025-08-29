
from __future__ import annotations
import json, os, platform

POLICY_PATH = "runtime/quantlab/policy.json"

def learn_from_bench(bench_path: str = "runtime/quantlab/bench.json") -> dict:
    if not os.path.exists(bench_path):
        return {}
    data = json.load(open(bench_path,"r",encoding="utf-8"))
    # very simple: choose lowest p50 latency among candidates with non-empty outputs
    best = None
    for r in data.get("results", []):
        if r.get("ok"):
            if best is None or (r.get("p50_ms", 9e9) < best.get("p50_ms", 9e9)):
                best = r
    pol = {"engine": best.get("engine","transformers"), "quant": best.get("quant","int8")} if best else {}
    if pol:
        os.makedirs(os.path.dirname(POLICY_PATH), exist_ok=True)
        json.dump(pol, open(POLICY_PATH,"w",encoding="utf-8"))
    return pol

def current_policy() -> dict:
    if os.path.exists(POLICY_PATH):
        try: return json.load(open(POLICY_PATH,"r",encoding="utf-8"))
        except Exception: return {}
    return {}
