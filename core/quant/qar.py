
from __future__ import annotations
import os, json, time, random, yaml

CANDIDATES = [
    {"name":"bnb_int8", "type":"transformers", "kwargs":{"load_in_8bit": True}},
    {"name":"bnb_int4", "type":"transformers", "kwargs":{"load_in_4bit": True}},
    {"name":"gguf_q4_k_m", "type":"gguf", "kwargs":{"quant":"Q4_K_M"}},
    {"name":"gguf_q5_k_m", "type":"gguf", "kwargs":{"quant":"Q5_K_M"}},
]

def _load_profile():
    path = os.path.join("runtime","config","quant_profile.yaml")
    try:
        import yaml
        return yaml.safe_load(open(path,"r",encoding="utf-8"))
    except Exception:
        return {"current": {}, "trials": []}

def _save_profile(p):
    path = os.path.join("runtime","config","quant_profile.yaml")
    with open(path,"w",encoding="utf-8") as f:
        f.write(yaml.safe_dump(p, sort_keys=False))

def _metric_stub():
    """Return a cheap metric; prefer real snapshot if exists."""
    try:
        import json
        with open('runtime/state/metrics.json','r',encoding='utf-8') as f:
            j=json.load(f)
        tps = max(1.0, j.get('tokens',0)/max(1,j.get('latency_ms',1))*1000.0)
        quality = 0.6
        return {'tps': tps, 'quality': quality, 'score': _score(tps, quality), 'vram': 0.0}
    except Exception:
        # fallback synthetic
        import random
        toks = random.uniform(20, 60)
        quality = random.uniform(0.3, 0.9)
        return {'tps': toks, 'quality': quality, 'score': 0.7*(toks/60.0)+0.3*quality}


def run_bandit(rounds: int = 8, epsilon: float = 0.2):
    prof = _load_profile()
    trials = prof.get("trials", [])
    best = prof.get("current", {})

    for i in range(rounds):
        explore = random.random() < epsilon or not best
        cand = random.choice(CANDIDATES) if explore else best
        m = _metric_stub()
        entry = {"time": int(time.time()), "cand": cand, "metric": m}
        trials.append(entry)
        if m["score"] > (best.get("metric", {}) or {}).get("score", 0.0):
            best = {"name": cand["name"], "cand": cand, "metric": m}
    prof["trials"] = trials[-200:]
    try:
        export_csv(prof['trials'])
    except Exception:
        pass
    prof["current"] = best
    _save_profile(prof)
    return best, trials


def _score(tps: float, quality: float) -> float:
    # Incorporate VRAM penalty if sysmetrics exists
    try:
        import json
        j=json.loads(open('runtime/state/sysmetrics.json','r',encoding='utf-8').read())
        vram = float((j.get('sys') or {}).get('vram_gb') or 0.0)
        # normalize vram to 0..1 using 16GB cap reference
        vpen = min(1.0, vram/16.0)
        return 0.6*(tps/60.0) + 0.3*quality + 0.1*(1.0 - vpen)
    except Exception:
        return 0.7*(tps/60.0)+0.3*quality


def pareto_front(trials):
    "Return indices on the Pareto frontier for (higher tps, higher quality, lower vram)."
    pts=[(t["metric"].get("tps",0), t["metric"].get("quality",0), -abs((t["metric"].get("vram",0))) ) for t in trials]
    front=set()
    for i,a in enumerate(pts):
        dominated=False
        for j,b in enumerate(pts):
            if j==i: continue
            if (b[0]>=a[0] and b[1]>=a[1] and b[2]>=a[2]) and (b[0]>a[0] or b[1]>a[1] or b[2]>a[2]):
                dominated=True; break
        if not dominated: front.add(i)
    return sorted(list(front))

def export_csv(trials, path='runtime/config/quant_trials.csv'):
    import csv, os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.writer(f); w.writerow(['time','name','tps','quality','score'])
        for t in trials:
            w.writerow([t.get('time'), (t.get('cand') or {}).get('name',''), (t.get('metric') or {}).get('tps',''), (t.get('metric') or {}).get('quality',''), (t.get('metric') or {}).get('score','')])
