
def extract_between(text: str, start: str, end: str) -> str:
    s = text.lower(); lo = s.find(start); hi = s.find(end)
    if lo == -1 or hi == -1 or hi <= lo: return ""
    return text[lo+len(start):hi].strip()
def format_ok(q: str) -> bool:
    s = q.lower()
    return all(tag in s for tag in ("<question>", "</question>", "<answer>", "</answer>"))
