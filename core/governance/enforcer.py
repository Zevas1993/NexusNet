
import os, yaml, json
STATE="runtime/state/tou.json"

def accepted()->bool:
    try:
        with open(STATE,"r",encoding="utf-8") as f: 
            j=json.load(f); return j.get("accepted") is True
    except Exception: 
        return False

def require_acceptance(cfg_path="runtime/config/terms_of_use.yaml")->bool:
    with open(cfg_path,"r",encoding="utf-8") as f: cfg=yaml.safe_load(f) or {}
    if not cfg.get("must_accept", True): return True
    if accepted(): return True
    # auto-create a placeholder the UI/CLI can flip to true
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE,"w",encoding="utf-8") as f: json.dump({"accepted": False, "version": cfg.get("version",1)}, f, indent=2)
    return False
