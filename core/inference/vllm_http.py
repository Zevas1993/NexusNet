
import requests
def available(url:str)->bool:
    try:
        r=requests.get(url, timeout=2); return r.status_code<500
    except Exception:
        return False

def generate(url:str, prompt:str)->str:
    try:
        r=requests.post(url.rstrip('/')+'/generate', json={"prompt":prompt}, timeout=15)
        if r.ok: return (r.json().get("text") or "")[:512]
    except Exception: pass
    return "[vLLM offline] " + prompt[:80]
