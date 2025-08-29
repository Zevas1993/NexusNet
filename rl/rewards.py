
from __future__ import annotations
def simple_reward(prompt: str, answer: str) -> float:
    # Toy reward: brevity + presence of key terms from the prompt
    toks = set(prompt.lower().split())
    a = set(answer.lower().split())
    overlap = len(toks & a) / max(1, len(toks))
    brev = 1.0 / (1.0 + 0.01*len(answer.split()))
    return 0.5*overlap + 0.5*brev
