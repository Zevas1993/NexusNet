
#!/usr/bin/env python3
from __future__ import annotations
import threading, time, requests, os

def run():
    import uvicorn
    from apps.api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8123, log_level="error")

def main():
    t=threading.Thread(target=run, daemon=True); t.start()
    time.sleep(1.0)
    # Basic probes
    r1=requests.get("http://127.0.0.1:8123/metrics"); print("metrics", r1.status_code)
    r2=requests.get("http://127.0.0.1:8123/temporal/namespaces"); print("namespaces", r2.json())
    # session create
    r3=requests.post("http://127.0.0.1:8123/sessions", json={}); sid=r3.json().get("sid"); print("sid",sid)
    # chat2 minimal
    r4=requests.post(f"http://127.0.0.1:8123/chat2?sid={sid}", json={"prompt":"hello world"}); print("chat2", r4.status_code)
    print("SMOKE DONE")
if __name__ == "__main__":
    main()
