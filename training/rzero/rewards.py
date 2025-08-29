
from typing import List, Dict
def jaccard(a: str, b: str) -> float:
    sa, sb = set(a.lower().split()), set(b.lower().split())
    if not sa and not sb: return 1.0
    inter = len(sa & sb); union = len(sa | sb) or 1
    return inter / union
def repetition_penalty(questions: List[str], threshold: float = 0.85, strength: float = 0.2) -> List[float]:
    n = len(questions); penalties = [0.0] * n
    for i in range(n):
        sim_count = 0
        for j in range(n):
            if i == j: continue
            if jaccard(questions[i], questions[j]) >= threshold:
                sim_count += 1
        if sim_count: penalties[i] = min(1.0, strength * sim_count)
    return penalties
def uncertainty_reward(correct_rate: float) -> float:
    return 1.0 - 2.0 * abs(correct_rate - 0.5)
def composite_reward(evals: List[Dict], questions: List[str], rep_threshold: float, rep_strength: float) -> List[float]:
    base = [uncertainty_reward(e['correct_rate']) * (1.0 if e.get('format_ok', True) else 0.0) for e in evals]
    reps = repetition_penalty(questions, rep_threshold, rep_strength)
    return [max(0.0, b - r) for b, r in zip(base, reps)]
