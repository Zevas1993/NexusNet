
from __future__ import annotations
from typing import Optional
from fastapi import FastAPI
try:
    from prometheus_client import make_asgi_app, Counter, Histogram
except Exception:  # optional dep
    make_asgi_app = None
    Counter = Histogram = None

app = FastAPI(title="NexusNet Metrics")

REQUESTS = Counter("nexusnet_requests_total","NexusNet requests") if Counter else None
LATENCY = Histogram("nexusnet_latency_seconds","Latency") if Histogram else None

ROUTER_PAIR = Counter("nexusnet_router_pair_total","Router predicted vs used", ["pred","used"]) if Counter else None

def record_router_pair(pred: str, used: str):
    if ROUTER_PAIR:
        try:
            ROUTER_PAIR.labels(pred=pred, used=used).inc()
        except Exception:
            pass

if make_asgi_app:
    app.mount("/metrics", make_asgi_app())
