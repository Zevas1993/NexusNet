
import requests
def available(url:str)->bool:
    try:
        r=requests.get(url.rstrip('/')+'/api/tags', timeout=2); return r.ok
    except Exception: return False

def generate(url:str, prompt:str)->str:
    try:
        r=requests.post(url.rstrip('/')+'/api/generate', json={"model":"qwen2.5:7b", "prompt":prompt}, timeout=30, stream=False)
        if r.ok: 
            j=r.json()
            return (j.get("response") or "")[:512]
    except Exception: pass
    return "[ollama offline] " + prompt[:80]
