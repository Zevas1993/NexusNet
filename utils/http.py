
from __future__ import annotations
import json, time, urllib.request

def post_json(url: str, body: dict, timeout: float = 2.0, retries: int = 1, headers: dict | None = None):
    data = json.dumps(body).encode("utf-8")
    hdrs = {"Content-Type":"application/json"}
    if headers: hdrs.update(headers)
    last = None
    for i in range(max(1, retries)):
        try:
            req = urllib.request.Request(url, method="POST", data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8") or "{}"
                return json.loads(raw)
        except Exception as e:
            last = e
            if i < retries - 1:
                time.sleep(0.2 * (i+1))
    return {"_error": str(last) if last else "unknown"}
