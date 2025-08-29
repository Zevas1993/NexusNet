
from __future__ import annotations
import re

DOMAINS = {
  "medical": ["diagnose","symptom","dosage","prescribe","side effect"],
  "legal": ["contract","binding","liability","lawsuit","statute"],
  "finance": ["investment","guarantee","profit","stock tip","insider"]
}

def classify(text: str) -> str:
  s=text.lower()
  for k,keys in DOMAINS.items():
    if any(re.search(r'\b'+re.escape(w)+r'\b', s) for w in keys):
      return k
  return "general"
