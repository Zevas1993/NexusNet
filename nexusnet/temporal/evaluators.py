
from __future__ import annotations
from typing import List, Tuple

def timeslice_qa_correctness(atoms: List[Tuple[str,str,str]], answers: List[str]) -> float:
    # Toy metric: fraction of answers matching any subject/object token
    if not answers: return 0.0
    tokens = set()
    for s,p,o in atoms:
        tokens.update(s.lower().split())
        tokens.update(o.lower().split())
    hits = sum(1 for a in answers if any(t in a.lower() for t in tokens))
    return hits/len(answers)
