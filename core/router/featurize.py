
from __future__ import annotations
from collections import Counter
import re

def features(text: str, max_ngrams: int = 2) -> dict[str,float]:
    toks = re.findall(r"[A-Za-z0-9_]+", text.lower())
    feats = Counter()
    for t in toks:
        feats[f"unigram:{t}"] += 1.0
    if max_ngrams >= 2:
        for i in range(len(toks)-1):
            feats[f"bigram:{toks[i]}_{toks[i+1]}"] += 1.0
    s = sum(feats.values()) or 1.0
    return {k: v/s for k, v in feats.items()}
