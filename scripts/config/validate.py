
#!/usr/bin/env python3
from __future__ import annotations
import json, yaml
from pathlib import Path
from jsonschema import Draft202012Validator

SCHEMA_DIR = Path("runtime/config/schema")

def _read_yaml(p: Path):
    if not p.exists(): return {}
    with p.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def run():
    results = {}
    for sp in SCHEMA_DIR.glob("*.schema.json"):
        base = sp.stem.replace(".schema","") if sp.name.endswith(".schema.json") else sp.stem
        cfg = Path("runtime/config") / f"{base}.yaml"
        schema = json.loads(sp.read_text("utf-8"))
        data = _read_yaml(cfg)
        try:
            Draft202012Validator(schema).validate(data)
            results[base] = {"ok": True}
        except Exception as e:
            results[base] = {"ok": False, "error": str(e)}
    return results

if __name__ == "__main__":
    import pprint
    pprint.pprint(run())
