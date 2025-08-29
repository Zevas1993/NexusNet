
# Local-only telemetry hooks (append to log files). Intentionally minimal.
import os, time, json
from .config import CONFIG_ROOT

LOG_DIR = os.path.join(CONFIG_ROOT, "..", "..", "data", "telemetry")
os.makedirs(LOG_DIR, exist_ok=True)

def log_event(name: str, payload: dict):
    with open(os.path.join(LOG_DIR, f"{name}.log"), "a") as f:
        f.write(json.dumps({"ts": time.time(), "name": name, "payload": payload}) + "\n")
