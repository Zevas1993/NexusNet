
"""
IO helpers for writing curated datasets from RND-R0.
"""
import os, json, time
from typing import List, Dict

def write_curated_jsonl(curated: List[Dict], out_dir: str, experiment: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    fname = f"curated-{experiment}-{int(time.time())}.jsonl"
    path = os.path.join(out_dir, fname)
    with open(path, "w", encoding="utf-8") as f:
        for ex in curated:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")
    return path
