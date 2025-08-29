
from __future__ import annotations
import re

DISCLAIMER = {
  "medical": "This is not medical advice. Consult a qualified professional.",
  "legal": "This is not legal advice. Consult a licensed attorney.",
  "finance": "This is not financial advice. Do your own research."
}

BLOCK_PATTERNS = {
  "medical": [r"diagnose", r"prescribe"],
  "legal": [r"draft.*contract"],
  "finance": [r"guarantee.*profit"]
}

def guard(domain: str, text: str) -> str:
    pats = BLOCK_PATTERNS.get(domain, [])
    if any(re.search(p, text, re.I) for p in pats):
        return DISCLAIMER.get(domain,"")
    return ""


SOFT_BLOCK = {"enabled": False}

def set_soft_block(enabled: bool):
    SOFT_BLOCK["enabled"] = bool(enabled)
