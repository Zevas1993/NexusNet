
import os, json, time, random
PREF="runtime/qes"
def record(sample:dict)->str:
    os.makedirs(PREF, exist_ok=True)
    p=os.path.join(PREF, f"telemetry_{int(time.time())}.json")
    with open(p,"w",encoding="utf-8") as f: json.dump(sample, f)
    return p

def synthesize_proxy_quality()->float:
    # Proxy quality: 0.0..1.0
    # Replace later with real eval harness
    return round(0.55 + random.random()*0.4, 3)
