from __future__ import annotations
import json, os, time, uuid

def run_trial(candidate: dict, fit: dict) -> str:
    tid = str(uuid.uuid4())[:8]
    os.makedirs("runtime/qes/trials", exist_ok=True)
    path = f"runtime/qes/trials/{tid}.json"
    json.dump({"candidate": candidate, "fitness": fit, "ts": time.time()}, open(path,"w",encoding="utf-8"))
    return path
