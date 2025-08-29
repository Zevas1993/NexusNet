
from sympy import sympify
def normalize(s: str):
    try: return str(sympify(s))
    except Exception: return s.strip()
def is_correct(pred: str, gold: str) -> bool:
    return normalize(pred) == normalize(gold)
