
#!/usr/bin/env python3
from __future__ import annotations
import threading, time, requests, os, subprocess, json

def run():
    import uvicorn
    from apps.api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8144, log_level="error")

def main():
    # Create two versions of a fact
    os.makedirs("data/corpus/demo", exist_ok=True)
    with open("data/corpus/demo/company_v1.txt","w",encoding="utf-8") as f:
        f.write("OpenAI released GPT-4 in 2023.")
    with open("data/corpus/demo/company_v2.txt","w",encoding="utf-8") as f:
        f.write("OpenAI released GPT-4.1 in 2024.")
    # Ingest
    subprocess.run(["python","scripts/rag/watch_ingest.py"], check=False)
    t=threading.Thread(target=run, daemon=True); t.start()
    time.sleep(1.3)
    sid=requests.post("http://127.0.0.1:8144/sessions", json={}).json().get("sid")
    # Ask with as_of = 2023-12-31
    cutoff=int(time.mktime(time.strptime("2023-12-31","%Y-%m-%d")))
    requests.post(f"http://127.0.0.1:8144/sessions/{sid}/settings", json={"as_of": cutoff})
    j=requests.post(f"http://127.0.0.1:8144/chat2?sid={sid}", json={"prompt":"What did OpenAI release?"}).json()
    print(json.dumps({"sid":sid,"as_of":cutoff,"ctx":[c.get("text","") for c in (j.get("ctx") or [])]}, indent=2))
if __name__ == "__main__":
    main()
