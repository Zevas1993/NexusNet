
from __future__ import annotations
import time, json, os
LOG="runtime/logs/audit.log"
os.makedirs("runtime/logs", exist_ok=True)

def log(action: str, detail: dict):
    with open(LOG,"a",encoding="utf-8") as f:
        f.write(json.dumps({"ts": int(time.time()), "action": action, "detail": detail})+"\n")
