
def math_verify(prompt: str, answer: str) -> float:
    # toy verifier: expects "2+2=4" style or "Answer: 4"
    import re
    m = re.search(r'(\d+)\s*\+\s*(\d+)', prompt)
    if not m: return 0.0
    a = int(m.group(1)) + int(m.group(2))
    return 1.0 if str(a) in answer else 0.0
