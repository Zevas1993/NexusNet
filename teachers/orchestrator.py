from __future__ import annotations
import yaml
from .generate import generate_items
from .critique import filter_by_consistency

def run_curriculum(capsule: str, out_path: str, n: int = 50) -> int:
    cfg = yaml.safe_load(open("runtime/config/teachers.yaml","r",encoding="utf-8"))
    if not cfg.get("enabled", False):
        return 0
    items = generate_items(capsule, n)
    good = filter_by_consistency(items, min_agree=2)
    import json, os
    os.makedirs("data/lake/curricula", exist_ok=True)
    with open(out_path,"w",encoding="utf-8") as f:
        for it in good:
            f.write(json.dumps(it)+"\n")
    return len(good)
