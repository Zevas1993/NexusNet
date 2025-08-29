
import requests
def available(url:str)->bool:
    try:
        r=requests.get(url.rstrip('/')+'/models', timeout=2); return r.ok
    except Exception: return False

def generate(url:str, prompt:str)->str:
    try:
        r=requests.post(url.rstrip('/')+'/chat/completions', json={"model":"local", "messages":[{"role":"user","content":prompt}]}, timeout=30)
        if r.ok: 
            j=r.json(); c=j.get("choices") or []
            if c: return (c[0].get("message",{}).get("content") or "")[:512]
    except Exception: pass
    return "[lmstudio offline] " + prompt[:80]
