
from __future__ import annotations
import hashlib
import math
from typing import Dict

def _hash_vec(text: str, dim: int) -> list[float]:
    # Fast, deterministic pseudo-embedding from SHA256 digest
    h = hashlib.sha256(text.encode("utf-8")).digest()
    vals = [b/255.0 for b in h]
    # tile to dim
    out = []
    while len(out) < dim:
        out.extend(vals)
    return out[:dim]

class PlaneEncoders:
    def __init__(self, planes_cfg: dict):
        self.cfg = planes_cfg
        self.dims = {p["name"]: int(p.get("dim", 64)) for p in planes_cfg.get("planes", [])}

    def encode(self, plane: str, text: str) -> list[float]:
        dim = self.dims.get(plane, 32)
        if plane == "temporal":
            # emphasize numbers/year-like content
            score = sum(ch.isdigit() for ch in text)
            base = _hash_vec(text, dim)
            return [min(1.0, v + 0.01*score) for v in base]
        return _hash_vec(text, dim)
