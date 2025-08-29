
from __future__ import annotations
import math
from typing import List, Optional

def energy_score(prompt: str, draft: str, evidences: Optional[List[str]] = None) -> float:
    # Heuristic "energy": penalize long answers w/o evidence, reward overlap with evidence and brevity
    if not draft: return 1e9  # high energy = bad
    L = max(1, len(draft.split()))
    ev_bonus = 0.0
    if evidences:
        shared = 0
        toks = set(draft.lower().split())
        for e in evidences:
            shared += len(toks & set(e.lower().split()))
        ev_bonus = shared / (L + 1e-6)
    # shorter is better if no evidence; longer ok if evidence supports
    base = L**0.5 - 2.0*ev_bonus
    # small penalty if answer repeats prompt too much
    rep = len(set(draft.lower().split()) & set(prompt.lower().split())) / (L+1e-6)
    return max(0.0, base + 0.5*rep)
