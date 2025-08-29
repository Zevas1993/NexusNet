
#!/usr/bin/env python3
from __future__ import annotations
import threading, time, requests, os, subprocess

def run():
    import uvicorn
    from apps.api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8133, log_level="error")

def main():
    # import demo docs
    subprocess.run(["python","scripts/demo/import_pack.py"], check=False)
    t=threading.Thread(target=run, daemon=True); t.start()
    time.sleep(1.2)
    # create session + set as_of (now)
    sid=requests.post("http://127.0.0.1:8133/sessions", json={}).json().get("sid")
    requests.post(f"http://127.0.0.1:8133/sessions/{sid}/settings", json={"as_of": int(time.time()) })
    # ask a question
    j=requests.post(f"http://127.0.0.1:8133/chat2?sid={sid}", json={"prompt":"What did OpenAI do in the demo data?"}).json()
    ctx=j.get("ctx") or []
    ok = any("OpenAI" in (c.get("text","")+c.get("source","")) for c in ctx)
    print({"sid":sid, "ctx_items":len(ctx), "ctx_ok": ok})
if __name__ == "__main__":
    main()
