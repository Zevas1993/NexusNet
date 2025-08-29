
from __future__ import annotations
import json, os
from typing import Iterable

def iter_logs(paths: Iterable[str]):
    for p in paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except Exception:
                        continue

def build_examples(paths: Iterable[str]) -> list[tuple[str, str]]:
    out = []
    for item in iter_logs(paths):
        prompt = item.get("prompt")
        capsule = item.get("capsule")
        if prompt and capsule:
            out.append((prompt, capsule))
    return out
