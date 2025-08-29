
from __future__ import annotations
import time
from typing import Dict

STATS = {"tokens":0, "latency_ms":0, "errors":0, "rag_hits":0, "qar_trials":0}

def incr(name: str, val: int = 1):
    STATS[name] = STATS.get(name,0) + val

def observe_latency(ms: float):
    STATS["latency_ms"] = int(ms)

def render_prom() -> str:
    out=[]
    for k,v in STATS.items():
        out.append(f"nexusnet_{k} {v}")
    return "\n".join(out)+"\n"


def record_generation(tokens: int, ms: float):
    STATS["tokens"] += tokens
    STATS["latency_ms"] = int(ms)
    try:
        import json, os
        os.makedirs("runtime/state", exist_ok=True)
        with open("runtime/state/metrics.json","w",encoding="utf-8") as f:
            json.dump({"tokens": STATS["tokens"], "latency_ms": STATS["latency_ms"], "ts": int(time.time())}, f)
    except Exception:
        pass


def sample_system():
    data={"cpu":0.0,"ram_gb":0.0,"vram_gb":0.0}
    try:
        import psutil
        data["cpu"]=psutil.cpu_percent(interval=0.05)
        data["ram_gb"]=psutil.virtual_memory().used/1024/1024/1024
    except Exception:
        pass
    try:
        import torch
        if torch.cuda.is_available():
            data["vram_gb"]=torch.cuda.memory_reserved(0)/1024/1024/1024
    except Exception:
        pass
    try:
        import json, os, time
        os.makedirs("runtime/state", exist_ok=True)
        snap={"sys": data, "ts": int(time.time())}
        with open("runtime/state/sysmetrics.json","w",encoding="utf-8") as f:
            json.dump(snap, f)
    except Exception:
        pass
    return data


def count_tokens(text: str, model: str = "gpt2") -> int:
    "Try tokenizer if present; fall back to whitespace."
    try:
        from transformers import AutoTokenizer  # type: ignore
        tok = AutoTokenizer.from_pretrained(model)
        return len(tok.encode(text))
    except Exception:
        return max(1, len((text or "").split()))


_stream = {"tokens":0, "on":False}

def begin_stream():
    _stream["tokens"]=0; _stream["on"]=True

def tick_stream(n:int):
    try:
        if _stream["on"]:
            _stream["tokens"] += int(n)
    except Exception:
        pass

def end_stream(ms:int=0):
    try:
        if _stream["on"]:
            record_generation(tokens=_stream["tokens"], ms=ms)
    finally:
        _stream["on"]=False
