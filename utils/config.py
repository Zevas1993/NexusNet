
from __future__ import annotations
import os, json, yaml
from pathlib import Path

def load_yaml(path: str, default: dict | None = None) -> dict:
    p = Path(path)
    if not p.exists():
        return default or {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def get_rag_cfg() -> dict:
    env = {"enabled": os.environ.get("RAG_LITE","0") == "1"}
    yml = load_yaml("runtime/config/rag.yaml", {})
    env.update(yml if isinstance(yml, dict) else {})
    env.setdefault("enabled", False)
    env.setdefault("top_k", 3)
    env.setdefault("corpus_dir", "data/corpus/sample")
    return env
