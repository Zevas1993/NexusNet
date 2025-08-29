
from __future__ import annotations
import os, time, yaml, threading
from typing import Tuple, Dict

_latency = { "transformers": 0.6, "ollama": 0.7, "vllm": 0.5, "tgi": 0.55 }
_last = 0.0
_lock = threading.Lock()

def _load_policy():
    path = os.path.join("runtime","config","engines.yaml")
    try:
        with open(path,"r",encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return {"weights":{"latency":0.4,"cost":0.3,"capability":0.25,"gpu":0.05},
                "capabilities":{"transformers":0.7,"ollama":0.6,"vllm":0.9,"tgi":0.85},
                "cost":{"transformers":1.0,"ollama":1.0,"vllm":0.9,"tgi":0.8}}

def _gpu_available():
    try:
        import torch
        return 1.0 if torch.cuda.is_available() else 0.0
    except Exception:
        return 0.0

def record_latency(engine: str, seconds: float):
    with _lock:
        cur = _latency.get(engine, 0.8)
        # EMA smoothing
        _latency[engine] = 0.8*cur + 0.2*seconds

def score_engines() -> Dict[str,float]:
    pol = _load_policy()
    w = pol["weights"]; cap = pol["capabilities"]; cost = pol["cost"]
    gpu = _gpu_available()
    scores = {}
    for eng in ["transformers","ollama","vllm","tgi"]:
        L = _latency.get(eng, 0.8)
        # normalize latency to 0..1 where lower is better
        lat_score = max(0.0, min(1.0, 1.0 - L))
        s = w["latency"]*lat_score + w["cost"]*cost.get(eng,0.5) + w["capability"]*cap.get(eng,0.5) + w["gpu"]*gpu
        scores[eng]=s
    return scores

def select_engine(capsule: str) -> Tuple[object, dict]:
    # honor DEMO/OFFLINE defaults unless LIVE_ENGINES=1
    live = os.environ.get("LIVE_ENGINES","0") == "1"
    prefer = os.environ.get("DEFAULT_ENGINE","transformers")
    if not live:
        prefer = "transformers"
    scores = score_engines()
    eng = max(scores.items(), key=lambda kv: kv[1])[0] if live else prefer

    if eng == "ollama":
        from core.engines.ollama_backend import Engine as E
    elif eng == "vllm":
        from core.engines.vllm_backend import Engine as E
    elif eng == "tgi":
        from core.engines.tgi_backend import Engine as E
    else:
        from core.engines.local_backend import Engine as E
        eng = "transformers"
    return E(), {"engine": eng, "scores": scores}


import threading, time, random
_PROBE = {"data":{}}
_STICKY = {}   # sid -> engine
_CANARY = {"ratio": 0.1, "candidate": None, "win": {"engine":None, "delta":0.0}}

class ProbeThread(threading.Thread):
    daemon = True
    def run(self):
        while True:
            try:
                for eng in ["transformers","ollama","vllm","tgi"]:
                    # micro-probe; in $0 mode this is a synthetic sleep
                    start=time.time(); time.sleep(random.uniform(0.01,0.03))
                    dur=time.time()-start
                    _PROBE["data"][eng] = {"lat": dur}
            except Exception:
                pass
            time.sleep(2.0)

_probe_once = False
def ensure_probe():
    global _probe_once
    if not _probe_once:
        ProbeThread().start()
        _probe_once = True

def sticky_for_session(sid: str, eng: str | None = None) -> str | None:
    if eng is not None:
        _STICKY[sid]=eng
    return _STICKY.get(sid)

def select_canary(base_engine: str) -> str:
    cand = _CANARY.get("candidate")
    if not cand: return base_engine
    import random
    return cand if random.random() < _CANARY.get("ratio", 0.1) else base_engine
