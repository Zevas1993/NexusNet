
from __future__ import annotations
import os, json

GLOBAL = "runtime/quantlab/policy.json"
PER_DIR = "runtime/quantlab/policies"

def get_active_policy(capsule: str | None = None) -> dict:
    if capsule:
        p = os.path.join(PER_DIR, f"{capsule}.json")
        if os.path.exists(p):
            try: return json.load(open(p,"r",encoding="utf-8"))
            except Exception: pass
    if os.path.exists(GLOBAL):
        try: return json.load(open(GLOBAL,"r",encoding="utf-8"))
        except Exception: pass
    return {}
